"""
myPokemonApp/migrations/XXXX_populate_npc_codes.py
===================================================
Migration de données : peuple npc_code sur tous les Trainer NPC existants.
À renommer avec le bon numéro de séquence (ex: 0042_populate_npc_codes.py).

Le numéro exact s'obtient avec :
    python manage.py makemigrations --empty myPokemonApp --name populate_npc_codes
puis remplacer le corps par ce fichier.
"""

import unicodedata
import re

from django.db import migrations


def slugify(s: str) -> str:
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = s.encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')


def populate_npc_codes(apps, schema_editor):
    """Génère npc_code = slugify(location)_slugify(username) pour chaque NPC."""
    Trainer = apps.get_model('myPokemonApp', 'Trainer')

    npcs = Trainer.objects.filter(is_npc=True, npc_code__isnull=True)

    for trainer in npcs:
        base_code = f"{slugify(trainer.location or 'unknown')}_{slugify(trainer.username)}"
        code      = base_code
        suffix    = 1

        # Résoudre les collisions
        while Trainer.objects.filter(npc_code=code).exclude(pk=trainer.pk).exists():
            suffix += 1
            code = f"{base_code}_{suffix}"

        trainer.npc_code = code
        trainer.save(update_fields=['npc_code'])


def reverse_npc_codes(apps, schema_editor):
    """Annule la migration — remet npc_code à NULL."""
    Trainer = apps.get_model('myPokemonApp', 'Trainer')
    Trainer.objects.filter(is_npc=True).update(npc_code=None)


class Migration(migrations.Migration):

    dependencies = [
        ('myPokemonApp', '0021_fielditem_pickedupitem_and_more'),
    ]

    operations = [
        migrations.RunPython(
            populate_npc_codes,
            reverse_code=reverse_npc_codes,
        ),
    ]
