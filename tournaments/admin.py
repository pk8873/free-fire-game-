from django.contrib import admin, messages
from .models import Tournament, Registration, Match, RoomCredential, MatchResult, MatchDispute

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display=('title','mode','start_at','registration_deadline','status','max_teams')
    list_filter=('status','start_at')
    list_editable=('status',)
    search_fields=('title','slug')
    prepopulated_fields={'slug':('title',)}
    date_hierarchy='start_at'

@admin.action(description='Approve selected pending team registrations')
def approve_registrations(modeladmin, request, queryset):
    updated=queryset.filter(status='PENDING').update(status='APPROVED')
    modeladmin.message_user(request,f'{updated} registration(s) approved.',messages.SUCCESS)

@admin.action(description='Reject selected pending team registrations')
def reject_registrations(modeladmin, request, queryset):
    updated=queryset.filter(status='PENDING').update(status='REJECTED')
    modeladmin.message_user(request,f'{updated} registration(s) rejected.',messages.WARNING)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display=('tournament','team','status','created_at')
    list_filter=('status','tournament')
    search_fields=('team__name','tournament__title')
    actions=(approve_registrations,reject_registrations)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display=('tournament','match_number','team_a','team_b','scheduled_at','status')
    list_filter=('status','tournament')
    search_fields=('team_a__name','team_b__name','tournament__title')
    ordering=('tournament','match_number')

@admin.register(RoomCredential)
class RoomCredentialAdmin(admin.ModelAdmin):
    list_display=('match','room_id','release_at')
    search_fields=('room_id','match__tournament__title')
    def has_view_permission(self,request,obj=None): return request.user.is_superuser
    def has_add_permission(self,request): return request.user.is_superuser
    def has_change_permission(self,request,obj=None): return request.user.is_superuser
    def has_delete_permission(self,request,obj=None): return request.user.is_superuser

@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display=('match','score_a','score_b','winner','status','updated_at')
    list_filter=('status',)
    search_fields=('match__tournament__title','match__team_a__name','match__team_b__name')
    readonly_fields=('updated_at',)

@admin.register(MatchDispute)
class MatchDisputeAdmin(admin.ModelAdmin):
    list_display=('match','filed_by','status','created_at')
    list_filter=('status',)
    search_fields=('match__tournament__title','filed_by__username','message')
    readonly_fields=('match','filed_by','message','created_at')
