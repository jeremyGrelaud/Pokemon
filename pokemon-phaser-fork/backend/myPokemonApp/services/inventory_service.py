"""
services/inventory_service.py
==============================
Gestion de l'inventaire des dresseurs.

Exports publics :
    give_item_to_trainer(trainer, item, quantity)    → TrainerInventory
    remove_item_from_trainer(trainer, item, quantity) → bool
    use_item_in_battle(item, pokemon, battle)        → (bool, str)
"""

import logging

logger = logging.getLogger(__name__)


def give_item_to_trainer(trainer, item, quantity=1):
    """
    Donne un objet à un dresseur (crée ou incrémente l'entrée inventaire).
    Déclenche automatiquement les quêtes de type 'have_item' pour cet objet.
    """
    from myPokemonApp.models.Trainer import TrainerInventory

    inv, _ = TrainerInventory.objects.get_or_create(
        trainer=trainer, item=item, defaults={'quantity': 0}
    )
    inv.quantity += quantity
    inv.save()

    try:
        from myPokemonApp.questEngine import trigger_quest_event
        trigger_quest_event(trainer, 'have_item', item=item)
    except Exception as exc:
        logger.warning("Erreur déclenchement quête have_item pour %s : %s", item, exc)

    return inv


def remove_item_from_trainer(trainer, item, quantity=1):
    """
    Retire un objet de l'inventaire.
    Retourne True si OK, False si stock insuffisant ou objet absent.
    """
    from myPokemonApp.models.Trainer import TrainerInventory

    try:
        inv = TrainerInventory.objects.get(trainer=trainer, item=item)
        if inv.quantity < quantity:
            return False
        inv.quantity -= quantity
        if inv.quantity == 0:
            inv.delete()
        else:
            inv.save()
        return True
    except TrainerInventory.DoesNotExist:
        return False


def use_item_in_battle(item, pokemon, battle):
    """
    Applique l'effet d'un objet pendant un combat.
    Retourne (success: bool, message: str).
    """
    if item.item_type == 'pokeball':
        if battle.battle_type != 'wild':
            return False, "On ne peut pas capturer le Pokémon d'un dresseur !"
        success, msg = _catch_pokemon_simple(
            battle.opponent_pokemon, battle.player_trainer, item
        )
        battle.add_to_log(msg)
        if success:
            battle.end_battle(battle.player_trainer)
        return success, msg
    elif item.item_type in ('potion', 'status'):
        result = item.use_on_pokemon(pokemon)
        battle.add_to_log(result)
        return True, result
    else:
        return False, "Cet objet ne peut pas être utilisé en combat !"


def _catch_pokemon_simple(wild_pokemon, trainer, pokeball_item):
    """
    Tentative de capture simplifiée (sans système de shakes).
    Retourne (success: bool, message: str).
    Utilisé uniquement en interne par use_item_in_battle().
    """
    import random

    catch_rate = wild_pokemon.species.catch_rate
    hp_mod     = (3 * wild_pokemon.max_hp - 2 * wild_pokemon.current_hp) / (3 * wild_pokemon.max_hp)
    status_mod = (2.0 if wild_pokemon.status_condition in ('sleep', 'freeze')
                  else 1.5 if wild_pokemon.status_condition in ('paralysis', 'poison', 'burn')
                  else 1.0)

    if random.random() < (catch_rate * pokeball_item.catch_rate_modifier * hp_mod * status_mod) / 255:
        party_count = trainer.pokemon_team.filter(is_in_party=True).count()
        wild_pokemon.trainer          = trainer
        wild_pokemon.original_trainer = trainer.username
        wild_pokemon.pokeball_used    = pokeball_item.name
        wild_pokemon.friendship       = 70
        wild_pokemon.is_in_party      = party_count < 6
        wild_pokemon.party_position   = party_count + 1 if party_count < 6 else None
        wild_pokemon.save()
        return True, f"{wild_pokemon.species.name} a été capturé !"

    return False, f"{wild_pokemon.species.name} s'est libéré de la ball !"