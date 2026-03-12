"""
0014_defeatedtrainer_data

Étape 2/3 de la migration defeated_trainers JSON → table relationnelle.

Lit GameSave.defeated_trainers (list[int]) sur chaque save existante
et crée les rows DefeatedTrainer correspondantes.

Idempotente : ignore_conflicts=True évite les erreurs si la migration
est rejouée (ex. après un rollback partiel).
"""

from django.db import migrations


def populate_defeated_trainers(apps, schema_editor):
    GameSave        = apps.get_model('myPokemonApp', 'GameSave')
    DefeatedTrainer = apps.get_model('myPokemonApp', 'DefeatedTrainer')
    Trainer         = apps.get_model('myPokemonApp', 'Trainer')

    # Index des IDs de Trainer existants pour éviter des FK invalides
    valid_trainer_ids = set(Trainer.objects.values_list('id', flat=True))

    rows = []
    for save in GameSave.objects.exclude(defeated_trainers=[]):
        for trainer_id in save.defeated_trainers:
            if trainer_id in valid_trainer_ids:
                rows.append(DefeatedTrainer(save_id=save.id, trainer_id=trainer_id))

    if rows:
        # ignore_conflicts garantit l'idempotence (contrainte unique)
        DefeatedTrainer.objects.bulk_create(rows, ignore_conflicts=True)


def reverse_populate(apps, schema_editor):
    """
    Reverse : recopie les rows DefeatedTrainer dans le JSONField
    pour pouvoir revenir à la migration 0013 sans perte de données.
    """
    GameSave        = apps.get_model('myPokemonApp', 'GameSave')
    DefeatedTrainer = apps.get_model('myPokemonApp', 'DefeatedTrainer')

    for save in GameSave.objects.all():
        ids = list(
            DefeatedTrainer.objects
            .filter(save=save)
            .values_list('trainer_id', flat=True)
        )
        save.defeated_trainers = ids
        save.save(update_fields=['defeated_trainers'])


class Migration(migrations.Migration):

    dependencies = [
        ('myPokemonApp', '0013_defeatedtrainer_schema'),
    ]

    operations = [
        migrations.RunPython(populate_defeated_trainers, reverse_code=reverse_populate),
    ]
