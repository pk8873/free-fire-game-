# Generated for ROOM ARENA Phase 1
import players.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='PlayerProfile', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('game_uid', models.CharField(max_length=32, unique=True)),
            ('in_game_name', models.CharField(max_length=40)),
            ('phone', models.CharField(blank=True, max_length=20)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='player_profile', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Team', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=60, unique=True)),
            ('join_code', models.CharField(default=players.models.make_team_code, editable=False, max_length=8, unique=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('captain', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='captained_teams', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='TeamMember', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('is_active', models.BooleanField(default=True)),
            ('joined_at', models.DateTimeField(auto_now_add=True)),
            ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_memberships', to=settings.AUTH_USER_MODEL)),
            ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='players.team')),
        ], options={'constraints':[models.UniqueConstraint(fields=('team','player'), name='unique_team_player')]}),
    ]
