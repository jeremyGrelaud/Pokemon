"""
scripts/initFieldItemsAndNpcs.py
=================================
Script d'initialisation des NPCs non-combattants et des items au sol.
Couvre : Bourg Palette, Route 1.

⚠️  Les tiled_obj_id sont des PLACEHOLDERS (100, 101, 102...).
    Remplacez-les par les vrais obj.id une fois les objets placés dans Tiled
    (visible dans les propriétés de l'objet dans Tiled).

python manage.py init_db --step 21
"""

import logging
from myPokemonApp.models.Zone import Zone
from myPokemonApp.models.Item import Item
from myPokemonApp.models.FieldItem import FieldItem
from myPokemonApp.models.Trainer import Trainer
from myPokemonApp.services.pokemon_factory import create_npc_trainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def get_zone(name: str) -> Zone:
    try:
        return Zone.objects.get(name=name)
    except Zone.DoesNotExist:
        raise RuntimeError(f"Zone '{name}' introuvable — vérifiez votre base de données.")


def get_item(name: str) -> Item:
    try:
        return Item.objects.get(name=name)
    except Item.DoesNotExist:
        raise RuntimeError(f"Item '{name}' introuvable — vérifiez initializeItemsAndNpcs.py.")


def create_field_item(zone: Zone, item_name: str, quantity: int, tiled_obj_id: int):
    """Crée ou met à jour un FieldItem. Idempotent sur (zone, tiled_obj_id)."""
    item = get_item(item_name)
    obj, created = FieldItem.objects.update_or_create(
        zone=zone,
        tiled_obj_id=tiled_obj_id,
        defaults={'item': item, 'quantity': quantity},
    )
    action = "créé" if created else "mis à jour"
    logger.info(f"  [item] {action} : {item_name} ×{quantity} @ {zone.name} (tiled#{tiled_obj_id})")
    return obj


def create_dialog_npc(zone_name: str, username: str, npc_class: str,
                      dialog: str, sprite_name: str = '', npc_code: str = None):
    """
    Crée un NPC sans équipe Pokémon (dialogue uniquement).
    Utilise create_npc_trainer avec team_data=[] et trainer_type='trainer'.
    """
    trainer = create_npc_trainer(
        username=username,
        trainer_type='trainer',
        location=zone_name,
        team_data=[],             # pas de Pokémon — NPC dialogue uniquement
        intro_text=dialog,
        npc_class=npc_class,
        sprite_name=sprite_name,
        npc_code=npc_code,
    )
    logger.info(f"  [npc]  {username} ({npc_class}) @ {zone_name} → {trainer.npc_code}")
    return trainer


# ─────────────────────────────────────────────────────────────
# BOURG PALETTE (Pallet Town)
# ─────────────────────────────────────────────────────────────

def init_bourg_palette():
    logger.info("[*] Bourg Palette — NPCs & items...")
    zone = get_zone('Bourg Palette')

    # ── NPCs dialogue ──────────────────────────────────────────

    # Maman du joueur — dans la maison du joueur
    create_dialog_npc(
        zone_name='Bourg Palette',
        username='Maman',
        npc_class='Famille',
        dialog="Prends bien soin de toi ! Et n'oublie pas de rentrer à la maison si tu es blessé.",
        sprite_name='npc_mom',
        npc_code='bourg_palette_maman',
    )

    # Daisy (sœur du rival) — dans la maison du rival
    create_dialog_npc(
        zone_name='Bourg Palette',
        username='Daisy',
        npc_class='Rival Sister',
        dialog="Tiens, prends cette Carte de Kanto. Mon frère ne voulait pas te la donner !",
        sprite_name='npc_daisy',
        npc_code='bourg_palette_daisy',
    )

    # Aide du Professeur Chen — dans le labo
    create_dialog_npc(
        zone_name='Bourg Palette',
        username='Aide du Professeur',
        npc_class='Chercheur',
        dialog="Le Professeur Chen étudie les Pokémon depuis de nombreuses années. "
               "Sa passion est de comprendre les liens entre les humains et les Pokémon.",
        sprite_name='npc_researcher',
        npc_code='bourg_palette_aide_prof_1',
    )

    create_dialog_npc(
        zone_name='Bourg Palette',
        username='Aide Senior',
        npc_class='Chercheur',
        dialog="Les Pokémon sont de bien mystérieuses créatures ! "
               "Nous n'en savons encore que très peu sur leurs origines.",
        sprite_name='npc_researcher',
        npc_code='bourg_palette_aide_prof_2',
    )

    # Habitant de Bourg Palette
    create_dialog_npc(
        zone_name='Bourg Palette',
        username='Habitant',
        npc_class='Habitant',
        dialog="Bourg Palette est un endroit paisible. "
               "Beaucoup de grands dresseurs viennent d'ici !",
        sprite_name='npc_townfolk',
        npc_code='bourg_palette_habitant',
    )

    # ── Items au sol ───────────────────────────────────────────
    # Note : Bourg Palette n'a pas d'items au sol dans FireRed/LeafGreen.
    # Remplacez les tiled_obj_id dès que vous placez des objets dans Tiled.
    # Exemple (désactivé) :
    # create_field_item(zone, 'Potion', 1, tiled_obj_id=101)

    logger.info("  [ok] Bourg Palette terminé.")


# ─────────────────────────────────────────────────────────────
# ROUTE 1
# ─────────────────────────────────────────────────────────────

def init_route_1():
    logger.info("[*] Route 1 — NPCs & items...")
    zone = get_zone('Route 1')

    # ── NPCs dialogue ──────────────────────────────────────────

    # La femme qui donne une Potion gratuite au début du jeu
    # (scripted dans FRLG — ici on la traite comme NPC dialogue après le premier passage)
    create_dialog_npc(
        zone_name='Route 1',
        username='Femme aux Potions',
        npc_class='Habitante',
        dialog="Tu commences ton aventure ? Tiens, prends cette Potion ! "
               "Elle restaurera 20 PV à l'un de tes Pokémon.",
        sprite_name='npc_woman',
        npc_code='route_1_femme_potions',
    )

    # Gamin passant sur la route
    create_dialog_npc(
        zone_name='Route 1',
        username='Gamin Curieux',
        npc_class='Gamin',
        dialog="Hé ! Tu vas à Jadielle Ville ? "
               "Il paraît qu'il y a un Centre Pokémon là-bas !",
        sprite_name='npc_youngster',
        npc_code='route_1_gamin_curieux',
    )

    # Randonneuse
    create_dialog_npc(
        zone_name='Route 1',
        username='Randonneuse Anne',
        npc_class='Randonneuse',
        dialog="Les Roucool et les Rattata sont très communs sur cette route. "
               "Parfait pour commencer à remplir ton Pokédex !",
        sprite_name='npc_lass',
        npc_code='route_1_randonneuse_anne',
    )

    # ── Items au sol ───────────────────────────────────────────
    # Dans FireRed/LeafGreen, Route 1 ne contient pas d'items au sol visibles.
    # Les items cachés (Itemfinder) ne sont pas dans notre système FieldItem.
    #
    # ⚠️  Placeholders — remplacez tiled_obj_id par les vrais IDs Tiled
    #     après avoir placé les Pokéballs dans votre map route_1.json

    # Exemple de Potion visible (à activer une fois la map Tiled configurée) :
    create_field_item(zone, 'Potion', 1, tiled_obj_id=10)

    logger.info("  [ok] Route 1 terminé.")


# ─────────────────────────────────────────────────────────────
# JADIELLE VILLE (Viridian City) — NPCs de base
# ─────────────────────────────────────────────────────────────

def init_jadielle():
    logger.info("[*] Jadielle Ville — NPCs...")

    # Le vieil homme qui apprend à capturer les Pokémon
    create_dialog_npc(
        zone_name='Jadielle',
        username='Vieil Homme',
        npc_class='Habitant',
        dialog="Tu veux savoir comment capturer des Pokémon ? "
               "Affaiblis-les d'abord, puis lance une Poké Ball !",
        sprite_name='npc_oldman',
        npc_code='jadielle_vieil_homme',
    )

    # Aide du Professeur Chen dans le labo de Jadielle (si présent)
    create_dialog_npc(
        zone_name='Jadielle',
        username='Aide Pokédex',
        npc_class='Chercheur',
        dialog="Si tu attrapes au moins 10 Pokémon différents, "
               "le Professeur Chen a un cadeau pour toi !",
        sprite_name='npc_researcher',
        npc_code='jadielle_aide_pokedex',
    )

    logger.info("  [ok] Jadielle terminé.")


# ─────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────

def run():
    logger.info("=== Initialisation NPCs dialogues & items au sol ===\n")

    try:
        init_bourg_palette()
    except Exception as e:
        logger.error(f"[!] Bourg Palette : {e}")

    try:
        init_route_1()
    except Exception as e:
        logger.error(f"[!] Route 1 : {e}")

    try:
        init_jadielle()
    except Exception as e:
        logger.error(f"[!] Jadielle : {e}")

    logger.info("\n=== Terminé ===")


run()