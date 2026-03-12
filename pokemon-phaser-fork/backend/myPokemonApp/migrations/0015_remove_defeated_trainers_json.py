"""
0015_remove_defeated_trainers_json

Étape 3/3 de la migration defeated_trainers JSON → table relationnelle.

Supprime le champ GameSave.defeated_trainers (JSONField) devenu obsolète.
À n'appliquer qu'une fois que le code applicatif ne référence plus ce champ
(GameSave.py, SaveViews.py, player_service.py, Trainer.py déjà patchés).
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myPokemonApp', '0014_defeatedtrainer_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamesave',
            name='defeated_trainers',
        ),
    ]
