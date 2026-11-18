from django.contrib import admin
from .models import PlayerProfile, Team, TeamMember

class TeamMemberInline(admin.TabularInline):
    model=TeamMember
    extra=0
    autocomplete_fields=('player',)

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display=('in_game_name','game_uid','user','created_at')
    search_fields=('in_game_name','game_uid','user__username','user__email')
    readonly_fields=('created_at',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display=('name','captain','active_count','join_code','created_at')
    search_fields=('name','captain__username','join_code')
    inlines=[TeamMemberInline]
    readonly_fields=('join_code','created_at')
    @admin.display(description='Active players')
    def active_count(self,obj): return obj.active_member_count

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display=('team','player','is_active','joined_at')
    list_filter=('is_active','team')
    search_fields=('team__name','player__username','player__player_profile__in_game_name')
    autocomplete_fields=('team','player')
