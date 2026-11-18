# Generated for ROOM ARENA Phase 1
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('players','0001_initial')]
    operations = [
        migrations.CreateModel(name='Tournament', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=120)),
            ('slug', models.SlugField(unique=True)),
            ('game', models.CharField(default='Free Fire MAX', editable=False, max_length=40)),
            ('mode', models.CharField(default='Clash Squad 4v4', editable=False, max_length=40)),
            ('description', models.TextField(blank=True)),
            ('start_at', models.DateTimeField()),
            ('registration_deadline', models.DateTimeField()),
            ('max_teams', models.PositiveIntegerField(default=8)),
            ('prize_note', models.CharField(blank=True, help_text='Sponsor-funded prize description only; do not promise unconfirmed prizes.', max_length=180)),
            ('status', models.CharField(choices=[('DRAFT','Draft'),('PUBLISHED','Published'),('CLOSED','Registration closed'),('LIVE','Live'),('COMPLETED','Completed'),('CANCELLED','Cancelled'),('UNDER_REVIEW','Under review')], default='DRAFT', max_length=20)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ], options={'ordering':['start_at']}),
        migrations.CreateModel(name='Registration', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('status', models.CharField(choices=[('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected')], default='PENDING', max_length=16)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to='players.team')),
            ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='tournaments.tournament')),
        ], options={'constraints':[models.UniqueConstraint(fields=('tournament','team'), name='one_team_per_tournament')]}),
        migrations.CreateModel(name='Match', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('match_number', models.PositiveIntegerField()),
            ('scheduled_at', models.DateTimeField(blank=True, null=True)),
            ('status', models.CharField(choices=[('SCHEDULED','Scheduled'),('LIVE','Live'),('REVIEW','Review'),('COMPLETED','Completed')], default='SCHEDULED', max_length=16)),
            ('team_a', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='matches_as_a', to='players.team')),
            ('team_b', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='matches_as_b', to='players.team')),
            ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='tournaments.tournament')),
        ], options={'constraints':[models.UniqueConstraint(fields=('tournament','match_number'), name='unique_tournament_match'),models.CheckConstraint(condition=~Q(team_a=models.F('team_b')), name='match_teams_different')]}),
        migrations.CreateModel(name='RoomCredential', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('room_id', models.CharField(max_length=40)),
            ('room_password', models.CharField(max_length=40)),
            ('release_at', models.DateTimeField()),
            ('match', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='room_credentials', to='tournaments.match')),
        ]),
        migrations.CreateModel(name='MatchResult', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('score_a', models.PositiveIntegerField(default=0)),
            ('score_b', models.PositiveIntegerField(default=0)),
            ('status', models.CharField(choices=[('SUBMITTED','Submitted'),('CONFIRMED','Confirmed'),('DISPUTED','Disputed')], default='SUBMITTED', max_length=16)),
            ('admin_note', models.TextField(blank=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('match', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='tournaments.match')),
            ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='wins', to='players.team')),
        ]),
        migrations.CreateModel(name='MatchDispute', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('message', models.TextField(max_length=2000)),
            ('status', models.CharField(choices=[('OPEN','Open'),('REVIEWING','Reviewing'),('RESOLVED','Resolved'),('REJECTED','Rejected')], default='OPEN', max_length=16)),
            ('admin_response', models.TextField(blank=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('filed_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='match_disputes', to=settings.AUTH_USER_MODEL)),
            ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disputes', to='tournaments.match')),
        ], options={'ordering':['-created_at']}),
    ]
