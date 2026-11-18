from django.contrib import admin
from .models import PlayerProfile, Team, TeamMember

class TeamMemberInline(admin.TabularInline):
    model=TeamMember
    extra=0
@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display=('in_game_name','game_uid','user','created_at')
    search_fields=('in_game_name','game_uid','user__username')
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display=('name','captain','created_at')
    search_fields=('name','captain__username')
    inlines=[TeamMemberInline]
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display=('team','player','is_active','joined_at')
    list_filter=('is_active',)
