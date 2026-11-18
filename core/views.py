from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse, Http404
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from players.models import PlayerProfile, Team, TeamMember
from tournaments.models import Tournament, Registration, Match, MatchDispute, MatchResult
from .forms import SignUpForm, ProfileForm, TeamCreateForm, JoinTeamForm, DisputeForm, MatchResultForm

def home(request):
    tournaments=Tournament.objects.filter(status='PUBLISHED').order_by('start_at')[:6]
    return render(request,'core/home.html',{'tournaments':tournaments,'now':timezone.now()})

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
    memberships=TeamMember.objects.filter(player=request.user,is_active=True).select_related('team','team__captain').prefetch_related(Prefetch('team__members',queryset=TeamMember.objects.filter(is_active=True).select_related('player','player__player_profile')))
    registrations=Registration.objects.filter(team__members__player=request.user,team__members__is_active=True).select_related('team','tournament').distinct().order_by('-created_at')[:10]
    return render(request,'core/dashboard.html',{'profile':profile,'memberships':memberships,'registrations':registrations,'create_form':TeamCreateForm(),'join_form':JoinTeamForm(),'profile_form':ProfileForm(instance=profile)})

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
            else:
                try:
                    with transaction.atomic():
                        locked=Team.objects.select_for_update().get(pk=team.pk)
                        if locked.members.filter(is_active=True).count()>=4:
                            messages.error(request,'This team already has four active players.')
                        else:
                            TeamMember.objects.update_or_create(team=locked,player=request.user,defaults={'is_active':True})
                            messages.success(request,f'You joined {locked.name}.')
                except IntegrityError:
                    messages.error(request,'You could not be added to this team. Refresh and try again.')
    return redirect('dashboard')


@login_required
def update_profile(request):
    profile=get_object_or_404(PlayerProfile,user=request.user)
    form=ProfileForm(request.POST or None,instance=profile)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Your player profile has been updated.')
        return redirect('dashboard')
    return render(request,'core/form_page.html',{'form':form,'heading':'Edit player profile','intro':'Keep your in-game name and Game UID accurate.','button':'Save profile'})

@login_required
def leave_team(request,team_id):
    if request.method!='POST': return redirect('dashboard')
    with transaction.atomic():
        team=get_object_or_404(Team.objects.select_for_update(),pk=team_id)
        membership=TeamMember.objects.filter(team=team,player=request.user,is_active=True).first()
        if not membership: raise Http404
        if team.captain_id==request.user.id:
            messages.error(request,'Captain must transfer captaincy to another active member before leaving.')
        elif Registration.objects.filter(team=team,status__in=['PENDING','APPROVED']).exists():
            messages.error(request,'This team has an active tournament registration. Ask the admin to reject or complete it before changing the roster.')
        else:
            membership.is_active=False
            membership.save(update_fields=['is_active'])
            messages.success(request,f'You left {team.name}.')
    return redirect('dashboard')

@login_required
def manage_team_member(request,team_id,member_id):
    if request.method!='POST': return redirect('dashboard')
    action=request.POST.get('action','remove')
    with transaction.atomic():
        team=get_object_or_404(Team.objects.select_for_update(),pk=team_id,captain=request.user)
        member=get_object_or_404(TeamMember.objects.select_for_update(),pk=member_id,team=team,is_active=True)
        if Registration.objects.filter(team=team,status__in=['PENDING','APPROVED']).exists():
            messages.error(request,'Roster is locked while this team has a pending or approved tournament registration.')
        elif member.player_id==team.captain_id:
            messages.error(request,'Captain cannot remove themselves. Transfer captaincy first.')
        elif action=='transfer':
            team.captain=member.player
            team.save(update_fields=['captain'])
            messages.success(request,f'{member.player.username} is now the team captain.')
        else:
            member.is_active=False
            member.save(update_fields=['is_active'])
            messages.success(request,f'{member.player.username} was removed from the team.')
    return redirect('dashboard')

@login_required
def regenerate_team_code(request,team_id):
    if request.method!='POST': return redirect('dashboard')
    with transaction.atomic():
        team=get_object_or_404(Team.objects.select_for_update(),pk=team_id,captain=request.user)
        if Registration.objects.filter(team=team,status__in=['PENDING','APPROVED']).exists():
            messages.error(request,'Invite code cannot be changed while a tournament registration is pending or approved.')
        else:
            from players.models import make_team_code
            team.join_code=make_team_code()
            team.save(update_fields=['join_code'])
            messages.success(request,f'New invite code for {team.name}: {team.join_code}')
    return redirect('dashboard')

@login_required
def tournament_detail(request,slug):
    tournament=get_object_or_404(Tournament,slug=slug)
    my_teams=Team.objects.filter(members__player=request.user,members__is_active=True).distinct() if request.user.is_authenticated else Team.objects.none()
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
        try:
            with transaction.atomic():
                locked_tournament=Tournament.objects.select_for_update().get(pk=tournament.pk)
                if locked_tournament.registrations.exclude(status='REJECTED').count()>=locked_tournament.max_teams:
                    messages.error(request,'All team slots are currently full.')
                else:
                    Registration.objects.create(tournament=locked_tournament,team=team)
                    messages.success(request,'Registration request sent. It will appear as pending until an admin approves it.')
        except IntegrityError:
            messages.info(request,'This team is already registered for this tournament.')
    return redirect('tournament-detail',slug=slug)

@login_required
def matches(request):
    team_ids=list(TeamMember.objects.filter(player=request.user,is_active=True).values_list('team_id',flat=True))
    regs=Registration.objects.filter(team_id__in=team_ids,status='APPROVED').values_list('tournament_id',flat=True)
    match_list=Match.objects.filter(tournament_id__in=regs).filter(Q(team_a_id__in=team_ids)|Q(team_b_id__in=team_ids)).select_related('tournament','team_a','team_b').order_by('scheduled_at')
    visible=[]
    now=timezone.now()
    for match in match_list:
        item={'match':match,'room':None,'result':getattr(match,'result',None)}
        if hasattr(match,'room_credentials') and match.room_credentials.release_at<=now and match.room_credentials and (match.team_a_id in team_ids or match.team_b_id in team_ids):
            item['room']=match.room_credentials
        visible.append(item)
    return render(request,'core/matches.html',{'items':visible})


@login_required
def submit_result(request,match_id):
    match=get_object_or_404(Match.objects.select_related('tournament','team_a','team_b'),pk=match_id)
    captain_team=Team.objects.filter(captain=request.user,id__in=[match.team_a_id,match.team_b_id]).first()
    approved=Registration.objects.filter(tournament=match.tournament,team_id=captain_team.id,status='APPROVED').exists() if captain_team else False
    if not captain_team or not approved: raise Http404
    existing=MatchResult.objects.filter(match=match).first()
    if existing and existing.status in ('CONFIRMED','DISPUTED'):
        messages.info(request,'This result is locked for admin review. Contact the tournament admin if it needs correction.')
        return redirect('matches')
    form=MatchResultForm(request.POST or None,initial={'score_a':existing.score_a,'score_b':existing.score_b} if existing else None)
    if request.method=='POST' and form.is_valid():
        a=form.cleaned_data['score_a']; b=form.cleaned_data['score_b']
        winner=match.team_a if a>b else match.team_b if b>a else None
        result,created=MatchResult.objects.get_or_create(match=match)
        result.score_a=a; result.score_b=b; result.winner=winner; result.status='SUBMITTED'; result.save()
        messages.success(request,'Match result submitted for admin review.')
        return redirect('matches')
    return render(request,'core/form_page.html',{'form':form,'heading':'Submit match result','intro':f'{match.tournament.title} · Match {match.match_number}. Scores are provisional until admin confirmation.','button':'Submit result'})

@login_required
def file_dispute(request,match_id):
    match=get_object_or_404(Match,pk=match_id)
    team_ids=TeamMember.objects.filter(player=request.user,is_active=True).values_list('team_id',flat=True)
    approved_team_ids=Registration.objects.filter(tournament=match.tournament,team_id__in=team_ids,status='APPROVED').values_list('team_id',flat=True)
    is_participant=match.team_a_id in approved_team_ids or match.team_b_id in approved_team_ids
    if not is_participant: raise Http404
    form=DisputeForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        MatchDispute.objects.create(match=match,filed_by=request.user,message=form.cleaned_data['message'])
        result=MatchResult.objects.filter(match=match).first()
        if result and result.status!='CONFIRMED':
            result.status='DISPUTED'; result.save(update_fields=['status','updated_at'])
        messages.success(request,'Your dispute was sent to the tournament admin.')
        return redirect('matches')
    return render(request,'core/form_page.html',{'form':form,'heading':'Report a match issue','intro':f'Match {match.match_number} · {match.tournament.title}','button':'Submit dispute'})

def health(request):
    from django.db import connection
    from django.db.utils import DatabaseError
    try:
        connection.ensure_connection()
        return JsonResponse({'status':'ok','database':'connected'})
    except DatabaseError:
        return JsonResponse({'status':'error','database':'unavailable'},status=503)

def manifest(request):
    data={'name':'ROOM ARENA','short_name':'ROOM ARENA','start_url':'/','display':'standalone','background_color':'#090d14','theme_color':'#ff5a36','description':'Community Clash Squad tournament hub','icons':[{'src':'/static/pwa/icon-192.svg','sizes':'192x192','type':'image/svg+xml','purpose':'any maskable'},{'src':'/static/pwa/icon-512.svg','sizes':'512x512','type':'image/svg+xml','purpose':'any maskable'}]}
    return JsonResponse(data)

def service_worker(request):
    js="const CACHE='room-arena-v2';const ASSETS=['/','/static/css/site.css','/static/js/app.js'];self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(fetch(e.request).catch(()=>caches.match(e.request).then(hit=>hit||caches.match('/'))))});"
    return HttpResponse(js,content_type='application/javascript')
