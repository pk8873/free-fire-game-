from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse, Http404
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from players.models import PlayerProfile, Team, TeamMember
from tournaments.models import Tournament, Registration, Match, MatchDispute
from .forms import SignUpForm, TeamCreateForm, JoinTeamForm, DisputeForm

def home(request):
    tournaments=Tournament.objects.filter(status='PUBLISHED').order_by('start_at')[:6]
    return render(request,'core/home.html',{'tournaments':tournaments})

def signup_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form=SignUpForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save()
        login(request,user)
        messages.success(request,'Your player account is ready.')
        return redirect('dashboard')
    return render(request,'core/form_page.html',{'form':form,'heading':'Create player account','intro':'Register once, then build your squad.','button':'Create account'})

def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    error=''
    if request.method=='POST':
        username=request.POST.get('username','').strip()
        user=authenticate(request,username=username,password=request.POST.get('password',''))
        if user is not None:
            login(request,user)
            next_url=request.POST.get('next') or request.GET.get('next')
            from django.utils.http import url_has_allowed_host_and_scheme
            if next_url and url_has_allowed_host_and_scheme(next_url,allowed_hosts={request.get_host()},require_https=request.is_secure()): return redirect(next_url)
            return redirect('dashboard')
        error='Username or password is incorrect.'
    return render(request,'core/login.html',{'error':error})

@login_required
def logout_view(request):
    if request.method!='POST': return redirect('dashboard')
    logout(request); return redirect('home')

@login_required
def dashboard(request):
    profile=PlayerProfile.objects.filter(user=request.user).first()
    memberships=TeamMember.objects.filter(player=request.user,is_active=True).select_related('team')
    registrations=Registration.objects.filter(team__members__player=request.user,team__members__is_active=True).select_related('team','tournament').distinct().order_by('-created_at')[:10]
    return render(request,'core/dashboard.html',{'profile':profile,'memberships':memberships,'registrations':registrations,'create_form':TeamCreateForm(),'join_form':JoinTeamForm()})

@login_required
def create_team(request):
    if request.method!='POST': return redirect('dashboard')
    form=TeamCreateForm(request.POST)
    if form.is_valid():
        if TeamMember.objects.filter(player=request.user,is_active=True).exists():
            messages.error(request,'Leave your current active team before creating another.')
            return redirect('dashboard')
        try:
            with transaction.atomic():
                team=form.save(commit=False); team.captain=request.user; team.save()
                TeamMember.objects.create(team=team,player=request.user)
            messages.success(request,f'Team created. Invite code: {team.join_code}')
        except IntegrityError:
            messages.error(request,'That team name is already in use.')
    else:
        messages.error(request,'Please enter a valid team name.')
    return redirect('dashboard')

@login_required
def join_team(request):
    if request.method!='POST': return redirect('dashboard')
    form=JoinTeamForm(request.POST)
    if form.is_valid():
        if TeamMember.objects.filter(player=request.user,is_active=True).exists():
            messages.error(request,'You are already in an active team.')
        else:
            team=Team.objects.filter(join_code=form.cleaned_data['join_code'].strip().upper()).first()
            if not team: messages.error(request,'Invite code not found.')
            elif team.members.filter(is_active=True).count()>=4: messages.error(request,'This team already has four active players.')
            else:
                TeamMember.objects.update_or_create(team=team,player=request.user,defaults={'is_active':True})
                messages.success(request,f'You joined {team.name}.')
    return redirect('dashboard')

@login_required
def tournament_detail(request,slug):
    tournament=get_object_or_404(Tournament,slug=slug)
    my_teams=Team.objects.filter(members__player=request.user,members__is_active=True).distinct()
    registrations=Registration.objects.filter(tournament=tournament,team__in=my_teams)
    return render(request,'core/tournament_detail.html',{'tournament':tournament,'my_teams':my_teams,'registrations':registrations})

@login_required
def register_team(request,slug):
    if request.method!='POST': return redirect('tournament-detail',slug=slug)
    tournament=get_object_or_404(Tournament,slug=slug)
    team=get_object_or_404(Team,pk=request.POST.get('team_id'),captain=request.user)
    active_count=team.members.filter(is_active=True).count()
    if tournament.status!='PUBLISHED' or tournament.registration_deadline<=timezone.now():
        messages.error(request,'Registration is closed.')
    elif active_count!=4:
        messages.error(request,'A Clash Squad team must have exactly four active players.')
    elif Registration.objects.filter(tournament=tournament,team=team).exists():
        messages.info(request,'This team is already registered.')
    elif tournament.registrations.exclude(status='REJECTED').count()>=tournament.max_teams:
        messages.error(request,'All team slots are currently full.')
    else:
        Registration.objects.create(tournament=tournament,team=team)
        messages.success(request,'Registration request sent. It will appear as pending until an admin approves it.')
    return redirect('tournament-detail',slug=slug)

@login_required
def matches(request):
    team_ids=TeamMember.objects.filter(player=request.user,is_active=True).values_list('team_id',flat=True)
    regs=Registration.objects.filter(team_id__in=team_ids,status='APPROVED').values_list('tournament_id',flat=True)
    match_list=Match.objects.filter(tournament_id__in=regs).filter(Q(team_a_id__in=team_ids)|Q(team_b_id__in=team_ids)).select_related('tournament','team_a','team_b').order_by('scheduled_at')
    visible=[]
    now=timezone.now()
    for match in match_list:
        item={'match':match,'room':None}
        if hasattr(match,'room_credentials') and match.room_credentials.release_at<=now and match.room_credentials and (match.team_a_id in team_ids or match.team_b_id in team_ids):
            item['room']=match.room_credentials
        visible.append(item)
    return render(request,'core/matches.html',{'items':visible})

@login_required
def file_dispute(request,match_id):
    match=get_object_or_404(Match,pk=match_id)
    team_ids=TeamMember.objects.filter(player=request.user,is_active=True).values_list('team_id',flat=True)
    is_participant=match.team_a_id in team_ids or match.team_b_id in team_ids
    approved=Registration.objects.filter(tournament=match.tournament,team_id__in=team_ids,status='APPROVED').exists()
    if not is_participant or not approved: raise Http404
    form=DisputeForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        MatchDispute.objects.create(match=match,filed_by=request.user,message=form.cleaned_data['message'])
        messages.success(request,'Your dispute was sent to the tournament admin.')
        return redirect('matches')
    return render(request,'core/form_page.html',{'form':form,'heading':'Report a match issue','intro':f'Match {match.match_number} · {match.tournament.title}','button':'Submit dispute'})

def manifest(request):
    data={'name':'ROOM ARENA','short_name':'ROOM ARENA','start_url':'/','display':'standalone','background_color':'#090d14','theme_color':'#ff5a36','description':'Community Clash Squad tournament hub','icons':[{'src':'/static/pwa/icon-192.svg','sizes':'192x192','type':'image/svg+xml','purpose':'any maskable'},{'src':'/static/pwa/icon-512.svg','sizes':'512x512','type':'image/svg+xml','purpose':'any maskable'}]}
    return JsonResponse(data)

def service_worker(request):
    js="const CACHE='room-arena-v2';const ASSETS=['/','/static/css/site.css','/static/js/app.js'];self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(fetch(e.request).catch(()=>caches.match(e.request).then(hit=>hit||caches.match('/'))))});"
    return HttpResponse(js,content_type='application/javascript')
