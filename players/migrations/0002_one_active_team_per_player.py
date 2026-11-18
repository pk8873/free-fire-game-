from django.db import migrations, models
from django.db.models import Q

class Migration(migrations.Migration):
    dependencies = [('players','0001_initial')]
    operations = [
        migrations.AddConstraint(
            model_name='teammember',
            constraint=models.UniqueConstraint(fields=('player',),condition=Q(is_active=True),name='one_active_team_per_player'),
        ),
    ]
