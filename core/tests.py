from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from players.models import PlayerProfile, Team, TeamMember
from tournaments.models import Tournament, Registration, Match, RoomCredential, MatchResult

class RoomArenaWorkflowTests(TestCase):
    def make_player(self, username):
        user=User.objects.create_user(username=username,password='Strong-Test-Pass-2026!')
        PlayerProfile.objects.create(user=user,game_uid=f'UID-{username}',in_game_name=username)
        return user

    def make_full_team(self,name):
        captain=self.make_player(name.lower()+'captain')
        team=Team.objects.create(name=name,captain=captain)
        TeamMember.objects.create(team=team,player=captain)
        for i in range(3):
            player=self.make_player(f'{name.lower()}p{i}')
            TeamMember.objects.create(team=team,player=player)
        return team

    def make_tournament(self):
        now=timezone.now()
        return Tournament.objects.create(title='Test Clash Cup',slug='test-clash-cup',description='Test event',start_at=now+timedelta(days=1),registration_deadline=now+timedelta(hours=12),max_teams=8,status='PUBLISHED')

    def test_signup_creates_player_profile(self):
        response=self.client.post(reverse('signup'),{
            'username':'newplayer','email':'new@example.com','in_game_name':'New Player',
            'game_uid':'UID-NEW-PLAYER','phone':'','password1':'Strong-Test-Pass-2026!',
            'password2':'Strong-Test-Pass-2026!'
        })
        self.assertRedirects(response,reverse('dashboard'))
        self.assertTrue(PlayerProfile.objects.filter(user__username='newplayer',game_uid='UID-NEW-PLAYER').exists())

    def test_captain_registration_requires_four_active_players(self):
        captain=self.make_player('solo_captain')
        team=Team.objects.create(name='Short Squad',captain=captain)
        TeamMember.objects.create(team=team,player=captain)
        tournament=self.make_tournament()
        self.client.force_login(captain)
        response=self.client.post(reverse('register-team',args=[tournament.slug]),{'team_id':team.id})
        self.assertRedirects(response,reverse('tournament-detail',args=[tournament.slug]))
        self.assertFalse(Registration.objects.filter(tournament=tournament,team=team).exists())

    def test_room_credentials_are_hidden_until_release_time(self):
        team_a=self.make_full_team('Alpha')
        team_b=self.make_full_team('Bravo')
        tournament=self.make_tournament()
        Registration.objects.create(tournament=tournament,team=team_a,status='APPROVED')
        match=Match.objects.create(tournament=tournament,match_number=1,team_a=team_a,team_b=team_b)
        RoomCredential.objects.create(match=match,room_id='ROOM-SECRET-123',room_password='SECRET-PASS',release_at=timezone.now()+timedelta(hours=1))
        self.client.force_login(team_a.captain)
        response=self.client.get(reverse('matches'))
        self.assertNotContains(response,'ROOM-SECRET-123')
        credential=match.room_credentials
        credential.release_at=timezone.now()-timedelta(minutes=1)
        credential.save()
        response=self.client.get(reverse('matches'))
        self.assertContains(response,'ROOM-SECRET-123')
        self.assertContains(response,'SECRET-PASS')

    def test_captain_can_submit_provisional_result(self):
        team_a=self.make_full_team('Gamma')
        team_b=self.make_full_team('Delta')
        tournament=self.make_tournament()
        Registration.objects.create(tournament=tournament,team=team_a,status='APPROVED')
        match=Match.objects.create(tournament=tournament,match_number=1,team_a=team_a,team_b=team_b)
        self.client.force_login(team_a.captain)
        response=self.client.post(reverse('submit-result',args=[match.id]),{'score_a':4,'score_b':2})
        self.assertRedirects(response,reverse('matches'))
        result=MatchResult.objects.get(match=match)
        self.assertEqual(result.status,'SUBMITTED')
        self.assertEqual(result.winner,team_a)

    def test_tournament_detail_is_public(self):
        tournament=self.make_tournament()
        response=self.client.get(reverse('tournament-detail',args=[tournament.slug]))
        self.assertEqual(response.status_code,200)

    def test_non_captain_cannot_remove_team_member(self):
        team=self.make_full_team('Echo')
        other=self.make_player('outsider')
        target=team.members.filter(is_active=True).exclude(player=team.captain).first()
        self.client.force_login(other)
        response=self.client.post(reverse('manage-team-member',args=[team.id,target.id]),{'action':'remove'})
        self.assertEqual(response.status_code,404)
        target.refresh_from_db()
        self.assertTrue(target.is_active)

    def test_captain_can_transfer_captaincy(self):
        team=self.make_full_team('Foxtrot')
        target=team.members.filter(is_active=True).exclude(player=team.captain).first()
        self.client.force_login(team.captain)
        response=self.client.post(reverse('manage-team-member',args=[team.id,target.id]),{'action':'transfer'})
        self.assertRedirects(response,reverse('dashboard'))
        team.refresh_from_db()
        self.assertEqual(team.captain_id,target.player_id)

    def test_captain_cannot_register_without_four_members(self):
        captain=self.make_player('incomplete_captain')
        team=Team.objects.create(name='Incomplete Squad',captain=captain)
        TeamMember.objects.create(team=team,player=captain)
        tournament=self.make_tournament()
        self.client.force_login(captain)
        response=self.client.post(reverse('register-team',args=[tournament.slug]),{'team_id':team.id})
        self.assertRedirects(response,reverse('tournament-detail',args=[tournament.slug]))
        self.assertFalse(Registration.objects.filter(tournament=tournament,team=team).exists())

    def test_health_endpoint_reports_database(self):
        response=self.client.get(reverse('health'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['status'],'ok')
