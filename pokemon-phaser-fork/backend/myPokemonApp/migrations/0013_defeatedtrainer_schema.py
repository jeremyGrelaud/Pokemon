"""
0013_defeatedtrainer_schema

Étape 1/3 de la migration defeated_trainers JSON → table relationnelle.

Crée la table DefeatedTrainer. Le champ GameSave.defeated_trainers (JSONField)
est intentionnellement conservé pour permettre la migration des données
en étape 2 (0014_defeatedtrainer_data).
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myPokemonApp', '0012_pokemon_ev_yields_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefeatedTrainer',
            fields=[
                ('id',      models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('save',    models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='defeated_trainer_set',
                    to='myPokemonApp.gamesave',
                )),
                ('trainer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='defeated_in_saves',
                    to='myPokemonApp.trainer',
                )),
            ],
            options={
                'verbose_name': 'Dresseur vaincu',
            },
        ),
        migrations.AddConstraint(
            model_name='defeatedtrainer',
            constraint=models.UniqueConstraint(
                fields=['save', 'trainer'],
                name='unique_defeated_trainer_per_save',
            ),
        ),
        migrations.AddIndex(
            model_name='defeatedtrainer',
            index=models.Index(
                fields=['save', 'trainer'],
                name='idx_defeated_save_trainer',
            ),
        ),
    ]
