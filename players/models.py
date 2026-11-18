from django.conf import settings
from django.db import models

class PlayerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='player_profile')
    game_uid = models.CharField(max_length=32, unique=True)
    in_game_name = models.CharField(max_length=40)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.in_game_name} ({self.game_uid})'

class Team(models.Model):
    name = models.CharField(max_length=60, unique=True)
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='captained_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team_memberships')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['team','player'], name='unique_team_player')]
    def __str__(self): return f'{self.player} — {self.team}'
