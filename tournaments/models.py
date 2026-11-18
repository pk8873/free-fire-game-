from django.conf import settings
from django.db import models
from django.db.models import Q

class Tournament(models.Model):
    STATUS=[('DRAFT','Draft'),('PUBLISHED','Published'),('CLOSED','Registration closed'),('LIVE','Live'),('COMPLETED','Completed'),('CANCELLED','Cancelled'),('UNDER_REVIEW','Under review')]
    title=models.CharField(max_length=120)
    slug=models.SlugField(unique=True)
    game=models.CharField(max_length=40, default='Free Fire MAX', editable=False)
    mode=models.CharField(max_length=40, default='Clash Squad 4v4', editable=False)
    description=models.TextField(blank=True)
    start_at=models.DateTimeField()
    registration_deadline=models.DateTimeField()
    max_teams=models.PositiveIntegerField(default=8)
    prize_note=models.CharField(max_length=180, blank=True, help_text='Sponsor-funded prize description only; do not promise unconfirmed prizes.')
    status=models.CharField(max_length=20, choices=STATUS, default='DRAFT')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['start_at']
    def __str__(self): return self.title
    @property
    def registered_teams(self): return self.registrations.filter(status='APPROVED').count()

class Registration(models.Model):
    tournament=models.ForeignKey(Tournament,on_delete=models.CASCADE,related_name='registrations')
    team=models.ForeignKey('players.Team',on_delete=models.PROTECT,related_name='registrations')
    status=models.CharField(max_length=16,choices=[('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected')],default='PENDING')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['tournament','team'],name='one_team_per_tournament')]
    def __str__(self): return f'{self.team} / {self.tournament}'

class Match(models.Model):
    tournament=models.ForeignKey(Tournament,on_delete=models.CASCADE,related_name='matches')
    match_number=models.PositiveIntegerField()
    team_a=models.ForeignKey('players.Team',on_delete=models.PROTECT,related_name='matches_as_a')
    team_b=models.ForeignKey('players.Team',on_delete=models.PROTECT,related_name='matches_as_b')
    scheduled_at=models.DateTimeField(null=True,blank=True)
    status=models.CharField(max_length=16,choices=[('SCHEDULED','Scheduled'),('LIVE','Live'),('REVIEW','Review'),('COMPLETED','Completed')],default='SCHEDULED')
    class Meta:
        constraints=[models.UniqueConstraint(fields=['tournament','match_number'],name='unique_tournament_match'),models.CheckConstraint(condition=~Q(team_a=models.F('team_b')),name='match_teams_different')]
    def __str__(self): return f'{self.tournament} — Match {self.match_number}'

class RoomCredential(models.Model):
    match=models.OneToOneField(Match,on_delete=models.CASCADE,related_name='room_credentials')
    room_id=models.CharField(max_length=40)
    room_password=models.CharField(max_length=40)
    release_at=models.DateTimeField()
    def __str__(self): return f'Room details for {self.match}'

class MatchResult(models.Model):
    match=models.OneToOneField(Match,on_delete=models.CASCADE,related_name='result')
    score_a=models.PositiveIntegerField(default=0)
    score_b=models.PositiveIntegerField(default=0)
    winner=models.ForeignKey('players.Team',on_delete=models.PROTECT,related_name='wins',null=True,blank=True)
    status=models.CharField(max_length=16,choices=[('SUBMITTED','Submitted'),('CONFIRMED','Confirmed'),('DISPUTED','Disputed')],default='SUBMITTED')
    admin_note=models.TextField(blank=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self): return f'Result: {self.match}'

class MatchDispute(models.Model):
    match=models.ForeignKey(Match,on_delete=models.CASCADE,related_name='disputes')
    filed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='match_disputes')
    message=models.TextField(max_length=2000)
    status=models.CharField(max_length=16,choices=[('OPEN','Open'),('REVIEWING','Reviewing'),('RESOLVED','Resolved'),('REJECTED','Rejected')],default='OPEN')
    admin_response=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']
    def __str__(self): return f'Dispute: {self.match} by {self.filed_by}'
