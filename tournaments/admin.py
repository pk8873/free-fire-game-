from django.contrib import admin
from .models import Tournament, Registration, Match, RoomCredential, MatchResult

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display=('title','mode','start_at','status','max_teams')
    list_filter=('status','start_at')
    prepopulated_fields={'slug':('title',)}
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display=('tournament','team','status','created_at')
    list_filter=('status','tournament')
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display=('tournament','match_number','team_a','team_b','scheduled_at','status')
    list_filter=('status','tournament')
@admin.register(RoomCredential)
class RoomCredentialAdmin(admin.ModelAdmin):
    list_display=('match','room_id','release_at')
    readonly_fields=('room_password',)
    def has_view_permission(self, request, obj=None): return request.user.is_superuser
    def has_change_permission(self, request, obj=None): return request.user.is_superuser
@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display=('match','score_a','score_b','winner','status','updated_at')
    list_filter=('status',)
