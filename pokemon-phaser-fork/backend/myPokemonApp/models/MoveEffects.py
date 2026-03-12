#!/usr/bin/python3
"""
MoveEffects.py — Architecture orientée objet pour les effets de moves.

Chaque effet hérite de MoveEffect et implémente apply().
Le registre EFFECT_REGISTRY mappe les chaînes d'effet à leur handler.

Retour de apply():
    True  → effet entièrement traité, _apply_move_effect doit return.
    False → effet de pré-traitement uniquement (ex: break_barrier avant dégâts).
"""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Evite les imports circulaires ; utilisé uniquement pour les type hints.
    from .Battle import Battle
    from .PlayablePokemon import PlayablePokemon
    from .PokemonMove import PokemonMove


# =============================================================================
# CLASSE DE BASE
# =============================================================================

class MoveEffect:
    """
    Classe de base pour tous les effets de moves.

    Sous-classer et implémenter apply().  Retourner True si l'effet est
    entièrement géré (Battle._apply_move_effect fera return).
    Retourner False pour laisser la suite du dispatcher s'exécuter.
    """

    def apply(self, battle: "Battle",
              attacker: "PlayablePokemon",
              defender: "PlayablePokemon",
              move: "PokemonMove") -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}.apply() non implémenté")


# =============================================================================
# STATUT PURS (sans dégâts)
# =============================================================================

class LeechSeedEffect(MoveEffect):
    """Vampigraine : drène 1/8 HP chaque fin de tour vers l'attaquant."""

    def apply(self, battle, attacker, defender, move):
        grass_types = {
            getattr(defender.species.primary_type, 'name', ''),
            getattr(defender.species.secondary_type, 'name', '')
            if defender.species.secondary_type else '',
        }
        if 'grass' in grass_types:
            battle.add_to_log(f"Ça n'a aucun effet sur {defender} !")
        elif battle.has_leech_seed(defender):
            battle.add_to_log(f"{defender} est déjà sous Vampigraine !")
        elif battle.apply_leech_seed(defender):
            battle.add_to_log(f"{defender} est planté avec Vampigraine !")
        return True


class ConfuseEffect(MoveEffect):
    """Inflige la confusion au défenseur."""

    def apply(self, battle, attacker, defender, move):
        if battle.is_confused(defender):
            battle.add_to_log(f"{defender} est déjà confus !")
        elif battle.confuse(defender):
            battle.add_to_log(f"{defender} est maintenant confus !")
        return True


class ConfuseRaiseSpAtkEffect(MoveEffect):
    """Augmente l'Atq Spé de l'attaquant et confond le défenseur."""

    def apply(self, battle, attacker, defender, move):
        battle.modify_stat(attacker, 'special_attack', 1)
        if not battle.is_confused(defender):
            battle.confuse(defender)
            battle.add_to_log(f"{defender} est maintenant confus !")
        return True


class HealHalfEffect(MoveEffect):
    """Soin / Surfin' : récupère 50 % des PV max."""

    def apply(self, battle, attacker, defender, move):
        healed = min(attacker.max_hp - attacker.current_hp, attacker.max_hp // 2)
        attacker.current_hp += healed
        attacker.save()
        battle.add_to_log(f"{attacker} récupère {healed} PV !")
        return True


class HealSleepEffect(MoveEffect):
    """Repos : restaure tous les PV mais endort pendant 2 tours."""

    def apply(self, battle, attacker, defender, move):
        attacker.current_hp       = attacker.max_hp
        attacker.status_condition = 'sleep'
        attacker.sleep_turns      = 2
        attacker.save()
        battle.add_to_log(f"{attacker} se repose et récupère tous ses PV !")
        return True


class IngrainEffect(MoveEffect):
    """Enracinement : récupère 1/16 HP par tour, empêche de fuir."""

    def apply(self, battle, attacker, defender, move):
        battle.set_ingrain(attacker)
        battle.add_to_log(f"{attacker} s'enracine dans le sol !")
        return True


class FocusEnergyEffect(MoveEffect):
    """Jackpot : augmente le taux de coups critiques."""

    def apply(self, battle, attacker, defender, move):
        battle.set_focus_energy(attacker)
        battle.add_to_log(f"{attacker} se concentre pour viser les points vitaux !")
        return True


class DestinyBondEffect(MoveEffect):
    """Lien Mortel : si le porteur est mis KO, son adversaire l'est aussi."""

    def apply(self, battle, attacker, defender, move):
        battle.set_destiny_bond(attacker)
        battle.add_to_log(f"{attacker} veut emporter son adversaire avec lui !")
        return True


class NightmareEffect(MoveEffect):
    """Cauchemar : inflige 1/4 HP par tour à un Pokémon endormi."""

    def apply(self, battle, attacker, defender, move):
        if defender.status_condition == 'sleep':
            battle.set_nightmare(defender)
            battle.add_to_log(f"{defender} est plongé dans des cauchemars !")
        else:
            battle.add_to_log("Ça n'a aucun effet !")
        return True


class PainSplitEffect(MoveEffect):
    """Rancœur : moyenne les PV des deux Pokémon."""

    def apply(self, battle, attacker, defender, move):
        avg = (attacker.current_hp + defender.current_hp) // 2
        attacker.current_hp = min(attacker.max_hp, avg)
        defender.current_hp = min(defender.max_hp, avg)
        attacker.save()
        defender.save()
        battle.add_to_log("Les deux Pokémon partagent leurs PV !")
        return True


class ResetStatsEffect(MoveEffect):
    """Brume / Haze : réinitialise toutes les modifications de stats."""

    def apply(self, battle, attacker, defender, move):
        for pkmn in [attacker, defender]:
            pkmn.attack_stage          = 0
            pkmn.defense_stage         = 0
            pkmn.special_attack_stage  = 0
            pkmn.special_defense_stage = 0
            pkmn.speed_stage           = 0
            pkmn.accuracy_stage        = 0
            pkmn.evasion_stage         = 0
            pkmn.save()
        battle.add_to_log("Les modifications de stats ont été annulées !")
        return True


class CopyStatChangesEffect(MoveEffect):
    """Psych Up : copie les stages de stats de l'adversaire."""

    def apply(self, battle, attacker, defender, move):
        attacker.attack_stage          = defender.attack_stage
        attacker.defense_stage         = defender.defense_stage
        attacker.special_attack_stage  = defender.special_attack_stage
        attacker.special_defense_stage = defender.special_defense_stage
        attacker.speed_stage           = defender.speed_stage
        attacker.save()
        battle.add_to_log(
            f"{attacker} copie les modifications de stats de {defender} !"
        )
        return True


class ForceSwitchEffect(MoveEffect):
    """Rugissement / Cyclone : force le switch en combat sauvage."""

    def apply(self, battle, attacker, defender, move):
        if battle.battle_type == 'wild':
            defender.current_hp = 0
            defender.save()
            battle.add_to_log(f"{defender} est repoussé !")
        else:
            battle.add_to_log("Ça n'a aucun effet en combat de dresseur !")
        return True


class DisableEffect(MoveEffect):
    """Neutralisation : désactive un move aléatoire pour 4 tours."""

    def apply(self, battle, attacker, defender, move):
        battle.disable_move(defender)
        return True


class TransformEffect(MoveEffect):
    """
    Transformation : copie les stages de stats et mémorise l'espèce cible.

    (Copie complète des moves non implémentée — nécessiterait un clonage
    des PokemonMoveInstance, hors du scope du dispatcher.)
    """

    def apply(self, battle, attacker, defender, move):
        attacker.attack_stage          = defender.attack_stage
        attacker.defense_stage         = defender.defense_stage
        attacker.special_attack_stage  = defender.special_attack_stage
        attacker.special_defense_stage = defender.special_defense_stage
        attacker.speed_stage           = defender.speed_stage
        attacker.save()
        battle._pstate(attacker)['transformed_into'] = defender.species.name
        battle._save_state()
        battle.add_to_log(f"{attacker} se transforme en {defender.species.name} !")
        return True


class PreventStatLowerEffect(MoveEffect):
    """
    Brume : protège le côté de l'attaquant contre les baisses de stats
    pendant 5 tours.  modify_stat() vérifie ce flag avant d'appliquer.
    """

    def apply(self, battle, attacker, defender, move):
        side = 'player' if attacker == battle.player_pokemon else 'opponent'
        battle._bstate()[f'{side}_mist'] = 5
        battle._save_state()
        battle.add_to_log(f"{attacker} est enveloppé de Brume !")
        return True


class RefreshEffect(MoveEffect):
    """Rafraîchissement : guérit le statut de l'attaquant."""

    def apply(self, battle, attacker, defender, move):
        if attacker.status_condition:
            attacker.cure_status()
            battle.add_to_log(f"{attacker} guérit son statut !")
        else:
            battle.add_to_log("Ça n'a aucun effet !")
        return True


class CureTeamStatusEffect(MoveEffect):
    """Glas Soin / Aromathérapie : guérit tous les Pokémon de l'équipe."""

    def apply(self, battle, attacker, defender, move):
        team = attacker.trainer.pokemon_team.filter(is_in_party=True)
        for pkmn in team:
            pkmn.cure_status()
        battle.add_to_log("Tous les Pokémon de l'équipe sont guéris !")
        return True


class BellyDrumEffect(MoveEffect):
    """Abdominaux : sacrifie 50 % des PV pour maximiser l'Attaque."""

    def apply(self, battle, attacker, defender, move):
        cost = attacker.max_hp // 2
        if attacker.current_hp <= cost:
            battle.add_to_log(f"{attacker} n'a pas assez de PV !")
            return True
        attacker.current_hp  -= cost
        attacker.attack_stage = 6
        attacker.save()
        battle.add_to_log(
            f"{attacker} se sacrifie pour maximiser son Attaque !"
        )
        return True


# =============================================================================
# MÉTÉO
# =============================================================================

class SunnyDayEffect(MoveEffect):
    def apply(self, battle, attacker, defender, move):
        battle.set_weather('sunny')
        battle.add_to_log("Le soleil brille intensément !")
        return True


class RainDanceEffect(MoveEffect):
    def apply(self, battle, attacker, defender, move):
        battle.set_weather('rain')
        battle.add_to_log("Une pluie torrentielle s'abat sur le terrain !")
        return True


class SandstormEffect(MoveEffect):
    def apply(self, battle, attacker, defender, move):
        battle.set_weather('sandstorm')
        battle.add_to_log("Une tempête de sable se déclenche !")
        return True


class HailEffect(MoveEffect):
    def apply(self, battle, attacker, defender, move):
        battle.set_weather('hail')
        battle.add_to_log("Il commence à grêler !")
        return True


# =============================================================================
# ÉCRANS
# =============================================================================

class LightScreenEffect(MoveEffect):
    def apply(self, battle, attacker, defender, move):
        side = 'player' if attacker == battle.player_pokemon else 'opponent'
        battle.set_screen(side, 'light_screen')
        battle.add_to_log(f"{attacker} érige un Écran Lumière !")
        return True


class ReflectEffect(MoveEffect):
    def apply(self, battle, attacker, defender, move):
        side = 'player' if attacker == battle.player_pokemon else 'opponent'
        battle.set_screen(side, 'reflect')
        battle.add_to_log(f"{attacker} érige un Mur !")
        return True


class BreakBarrierEffect(MoveEffect):
    """Brise les écrans adverses PUIS laisse la suite appliquer les dégâts."""

    def apply(self, battle, attacker, defender, move):
        side = 'opponent' if attacker == battle.player_pokemon else 'player'
        battle._bstate().pop(f'{side}_light_screen', None)
        battle._bstate().pop(f'{side}_reflect', None)
        battle._save_state()
        battle.add_to_log("Les écrans adverses sont brisés !")
        return False   # ← continuer pour les dégâts normaux


# =============================================================================
# PROTECTION
# =============================================================================

class ProtectEffect(MoveEffect):
    def apply(self, battle, attacker, defender, move):
        battle.set_protected(attacker)
        battle.add_to_log(f"{attacker} se protège !")
        return True


class EndureEffect(MoveEffect):
    def apply(self, battle, attacker, defender, move):
        battle.set_enduring(attacker)
        battle.add_to_log(f"{attacker} se prépare à tenir le coup !")
        return True


# =============================================================================
# BOOSTS DE STATS (StatBoostEffect)
# =============================================================================

class StatBoostEffect(MoveEffect):
    """
    Moves de stat purs (power == 0).

    changes : liste de tuples (stat_name, stages, who)
        who = 'self'     → attacker
        who = 'opponent' → defender
    """

    def __init__(self, changes: list):
        self.changes = changes

    def apply(self, battle, attacker, defender, move):
        for stat_name, stages, who in self.changes:
            target = attacker if who == 'self' else defender
            battle.modify_stat(target, stat_name, stages)
        return True


# =============================================================================
# NOUVEAUX EFFETS STATUS
# =============================================================================

class SubstituteEffect(MoveEffect):
    """
    Substitut : crée un clone (25 % HP max) qui encaisse les dégâts à la place.
    Le HP du substitut est stocké dans _pstate(pokemon)['substitute_hp'].
    _apply_damage_to_defender() le consulte en priorité.
    """

    def apply(self, battle, attacker, defender, move):
        cost = attacker.max_hp // 4
        if attacker.current_hp <= cost:
            battle.add_to_log(
                f"{attacker} n'a pas assez de PV pour créer un Substitut !"
            )
            return True
        if battle._pstate(attacker).get('substitute_hp', 0) > 0:
            battle.add_to_log(f"{attacker} a déjà un Substitut !")
            return True
        attacker.current_hp -= cost
        attacker.save()
        battle._pstate(attacker)['substitute_hp'] = cost
        battle._save_state()
        battle.add_to_log(f"{attacker} crée un Substitut ({cost} PV) !")
        return True


class EncoreEffect(MoveEffect):
    """
    Encore : force l'adversaire à répéter son dernier move pendant 3 tours.
    Le dernier move utilisé est tracké dans _pstate(pokemon)['last_move_used'].
    """

    def apply(self, battle, attacker, defender, move):
        pst       = battle._pstate(defender)
        last_move = pst.get('last_move_used')
        if not last_move:
            battle.add_to_log(f"Ça n'a aucun effet sur {defender} !")
            return True
        if pst.get('encore_turns', 0) > 0:
            battle.add_to_log(f"{defender} est déjà sous l'effet d'Encore !")
            return True
        pst['encore_move']  = last_move
        pst['encore_turns'] = 3
        battle._save_state()
        battle.add_to_log(f"{defender} doit répéter {last_move} !")
        return True


class TauntEffect(MoveEffect):
    """
    Raillerie : interdit les moves de statut (power == 0) pendant 3 tours.
    use_move() vérifie taunt_turns avant d'autoriser le move.
    """

    def apply(self, battle, attacker, defender, move):
        pst = battle._pstate(defender)
        if pst.get('taunt_turns', 0) > 0:
            battle.add_to_log(f"{defender} est déjà sous l'effet de Raillerie !")
            return True
        pst['taunt_turns'] = 3
        battle._save_state()
        battle.add_to_log(
            f"{defender} est provoqué ! Il ne peut plus utiliser de moves de statut !"
        )
        return True


class TormentEffect(MoveEffect):
    """
    Tourment : interdit de répéter deux fois de suite le même move.
    use_move() vérifie torment + last_move_used avant d'autoriser.
    """

    def apply(self, battle, attacker, defender, move):
        pst = battle._pstate(defender)
        if pst.get('torment'):
            battle.add_to_log(f"{defender} est déjà sous l'effet de Tourment !")
            return True
        pst['torment'] = True
        battle._save_state()
        battle.add_to_log(
            f"{defender} est sous Tourment ! Il ne peut pas répéter le même move !"
        )
        return True


class TrickEffect(MoveEffect):
    """Échange / Switcharoo : swap des objets tenus."""

    def apply(self, battle, attacker, defender, move):
        a_item = getattr(attacker, 'held_item', None)
        d_item = getattr(defender, 'held_item', None)
        attacker.held_item = d_item
        defender.held_item = a_item
        attacker.save()
        defender.save()
        if a_item or d_item:
            a_name = a_item.name if a_item else 'rien'
            d_name = d_item.name if d_item else 'rien'
            battle.add_to_log(
                f"{attacker} et {defender} échangent leurs objets ({a_name} ↔ {d_name}) !"
            )
        else:
            battle.add_to_log("L'échange n'a aucun effet !")
        return True


class WishEffect(MoveEffect):
    """
    Vœu : soigne 50 % des PV max du Pokémon actif au tour suivant.
    _apply_end_of_turn_effects() décrémente wish_turns et soigne à 0.
    """

    def apply(self, battle, attacker, defender, move):
        pst = battle._pstate(attacker)
        if pst.get('wish_turns', 0) > 0:
            battle.add_to_log("Un Vœu est déjà en cours !")
            return True
        pst['wish_turns']  = 2
        pst['wish_amount'] = attacker.max_hp // 2
        battle._save_state()
        battle.add_to_log(f"{attacker} fait un Vœu !")
        return True


class MeanLookEffect(MoveEffect):
    """
    Œil Fatal / Toile / Blocage : empêche l'adversaire de fuir ou de changer.
    attempt_flee() et switch_pokemon() vérifient trapped_by_mean_look.
    """

    def apply(self, battle, attacker, defender, move):
        pst = battle._pstate(defender)
        if pst.get('trapped_by_mean_look'):
            battle.add_to_log(f"{defender} ne peut déjà pas s'échapper !")
            return True
        pst['trapped_by_mean_look'] = True
        battle._save_state()
        battle.add_to_log(f"{defender} ne peut plus s'échapper !")
        return True


class TrickRoomEffect(MoveEffect):
    """
    Salle Bizarre : inverse l'ordre de vitesse pendant 5 tours (toggle).
    execute_turn() lit trick_room_turns pour inverser first/second.
    """

    def apply(self, battle, attacker, defender, move):
        bs = battle._bstate()
        if bs.get('trick_room_turns', 0) > 0:
            bs['trick_room_turns'] = 0
            battle._save_state()
            battle.add_to_log("La Salle Bizarre retrouve son état normal !")
        else:
            bs['trick_room_turns'] = 5
            battle._save_state()
            battle.add_to_log(
                "La Salle Bizarre est instaurée ! Les Pokémon lents passent en premier !"
            )
        return True


class TailwindEffect(MoveEffect):
    """
    Vent Arrière : double la vitesse effective du côté de l'attaquant
    pendant 4 tours.  get_effective_speed() doit tenir compte de ce flag.
    """

    def apply(self, battle, attacker, defender, move):
        side = 'player' if attacker == battle.player_pokemon else 'opponent'
        battle._bstate()[f'{side}_tailwind'] = 4
        battle._save_state()
        battle.add_to_log(
            f"Le Vent Arrière souffle pour le côté de {attacker} !"
        )
        return True


class PerishSongEffect(MoveEffect):
    """
    Chant du Destin : les deux Pokémon tombent KO dans 3 tours.
    _apply_end_of_turn_effects() décrémente perish_turns.
    """

    def apply(self, battle, attacker, defender, move):
        for pkmn in [attacker, defender]:
            pst = battle._pstate(pkmn)
            if not pst.get('perish_turns'):
                pst['perish_turns'] = 3
        battle._save_state()
        battle.add_to_log(
            "Tous ceux qui ont entendu le Chant du Destin tomberont dans 3 tours !"
        )
        return True


class SpikesEffect(MoveEffect):
    """
    Picots : pose 1 à 3 couches de pièges côté adverse.
    Les dégâts sont appliqués lors du switch dans switch_pokemon().
    """

    def apply(self, battle, attacker, defender, move):
        side  = 'opponent' if attacker == battle.player_pokemon else 'player'
        key   = f'{side}_spikes'
        count = battle._bstate().get(key, 0)
        if count >= 3:
            battle.add_to_log("Les Picots sont déjà au maximum (3 couches) !")
            return True
        battle._bstate()[key] = count + 1
        battle._save_state()
        who = "l'adversaire" if side == 'opponent' else "votre équipe"
        battle.add_to_log(
            f"Une couche de Picots est posée du côté de {who} ! ({count + 1}/3)"
        )
        return True


class ToxicSpikesEffect(MoveEffect):
    """
    Toxipics : 1 couche → poison, 2 couches → poison sévère au switch.
    """

    def apply(self, battle, attacker, defender, move):
        side  = 'opponent' if attacker == battle.player_pokemon else 'player'
        key   = f'{side}_toxic_spikes'
        count = battle._bstate().get(key, 0)
        if count >= 2:
            battle.add_to_log("Les Toxipics sont déjà au maximum (2 couches) !")
            return True
        battle._bstate()[key] = count + 1
        battle._save_state()
        who = "l'adversaire" if side == 'opponent' else "votre équipe"
        battle.add_to_log(
            f"Une couche de Toxipics est posée du côté de {who} ! ({count + 1}/2)"
        )
        return True


class StealthRockEffect(MoveEffect):
    """
    Roc Furtif : inflige des dégâts type Roche lors du switch selon les faiblesses.
    """

    def apply(self, battle, attacker, defender, move):
        side = 'opponent' if attacker == battle.player_pokemon else 'player'
        key  = f'{side}_stealth_rock'
        if battle._bstate().get(key):
            battle.add_to_log("Le Roc Furtif est déjà en place !")
            return True
        battle._bstate()[key] = True
        battle._save_state()
        who = "l'adversaire" if side == 'opponent' else "votre équipe"
        battle.add_to_log(f"Des pierres acérées sont posées du côté de {who} !")
        return True


class ConversionEffect(MoveEffect):
    """
    Conversion : change le type de l'attaquant en celui de son premier move.
    Mémorise le changement dans _pstate pour l'affichage.
    """

    def apply(self, battle, attacker, defender, move):
        from .PlayablePokemon import PokemonMoveInstance
        first_mi = (
            PokemonMoveInstance.objects
            .filter(pokemon=attacker)
            .select_related('move__type')
            .first()
        )
        if first_mi and first_mi.move.type:
            new_type = first_mi.move.type
            battle._pstate(attacker)['converted_type'] = new_type.name
            battle._save_state()
            battle.add_to_log(f"{attacker} devient de type {new_type.name} !")
        else:
            battle.add_to_log("Ça n'a aucun effet !")
        return True


# =============================================================================
# EFFETS DE STAT SECONDAIRES (utilisés par Battle._apply_move_effect
#   lorsque move.power > 0, avec vérification effect_chance)
# =============================================================================

#: Format : effect_tag → [(stat_name, stages, 'self' | 'opponent')]
SECONDARY_STAT_EFFECTS: dict[str, list] = {
    'raise_attack':                  [('attack',           1,  'self')],
    'raise_defense':                 [('defense',          1,  'self')],
    'raise_special_attack':          [('special_attack',   1,  'self')],
    'raise_special_defense':         [('special_defense',  1,  'self')],
    'raise_speed':                   [('speed',            1,  'self')],
    'raise_evasion':                 [('evasion',          1,  'self')],
    'raise_accuracy':                [('accuracy',         1,  'self')],
    'raise_attack_defense':          [('attack',           1,  'self'), ('defense',          1, 'self')],
    'raise_attack_speed':            [('attack',           1,  'self'), ('speed',             1, 'self')],
    'raise_attack_accuracy':         [('attack',           1,  'self'), ('accuracy',          1, 'self')],
    'raise_special_attack_special_defense':
                                     [('special_attack',   1,  'self'), ('special_defense',   1, 'self')],
    'raise_defense_special_defense': [('defense',          1,  'self'), ('special_defense',   1, 'self')],
    'raise_all_stats':               [('attack',           1,  'self'), ('defense',           1, 'self'),
                                      ('special_attack',   1,  'self'), ('special_defense',   1, 'self'),
                                      ('speed',            1,  'self')],
    'sharply_raise_attack':          [('attack',           2,  'self')],
    'sharply_raise_defense':         [('defense',          2,  'self')],
    'sharply_raise_special_attack':  [('special_attack',   2,  'self')],
    'sharply_raise_special_defense': [('special_defense',  2,  'self')],
    'sharply_raise_speed':           [('speed',            2,  'self')],
    'raise_attack_speed_sharply':    [('attack',           1,  'self'), ('speed',             2, 'self')],
    'raise_attack_special_attack_speed_sharply_lower_defense_special_defense':
                                     [('attack',           2,  'self'), ('special_attack',    2, 'self'),
                                      ('speed',            2,  'self'), ('defense',          -1, 'self'),
                                      ('special_defense',  -1, 'self')],
    'lower_attack':                  [('attack',           -1, 'opponent')],
    'lower_defense':                 [('defense',          -1, 'opponent')],
    'lower_special_defense':         [('special_defense',  -1, 'opponent')],
    'lower_speed':                   [('speed',            -1, 'opponent')],
    'lower_accuracy':                [('accuracy',         -1, 'opponent')],
    'lower_evasion':                 [('evasion',          -1, 'opponent')],
    'lower_sp_atk':                  [('special_attack',   -1, 'opponent')],
    'lower_special_attack':          [('special_attack',   -1, 'opponent')],
    'lower_attack_defense':          [('attack',           -1, 'self'),  ('defense',          -1, 'self')],
    'lower_defense_special_defense': [('defense',          -1, 'self'),  ('special_defense',  -1, 'self')],
    'sharply_lower_attack':          [('attack',           -2, 'opponent')],
    'sharply_lower_defense':         [('defense',          -2, 'opponent')],
    'sharply_lower_special_attack':  [('special_attack',   -2, 'self')],
    'sharply_lower_special_defense': [('special_defense',  -2, 'opponent')],
    'lower_special_attack_opponent': [('special_attack',   -2, 'opponent')],
}


# =============================================================================
# REGISTRE CENTRAL
# =============================================================================

#: Toutes les instances partagées (stateless — ne stockent pas d'état).
EFFECT_REGISTRY: dict[str, MoveEffect] = {

    # ── Statut purs ────────────────────────────────────────────────────────────
    'leech_seed':           LeechSeedEffect(),
    'confuse':              ConfuseEffect(),
    'confuse_raise_spatk':  ConfuseRaiseSpAtkEffect(),
    'heal_half':            HealHalfEffect(),
    'heal_sleep':           HealSleepEffect(),
    'ingrain':              IngrainEffect(),
    'focus_energy':         FocusEnergyEffect(),
    'destiny_bond':         DestinyBondEffect(),
    'nightmare':            NightmareEffect(),
    'pain_split':           PainSplitEffect(),
    'reset_stats':          ResetStatsEffect(),
    'copy_stat_changes':    CopyStatChangesEffect(),
    'force_switch':         ForceSwitchEffect(),
    'disable':              DisableEffect(),
    'transform':            TransformEffect(),
    'prevent_stat_lower':   PreventStatLowerEffect(),
    'refresh':              RefreshEffect(),
    'cure_team_status':     CureTeamStatusEffect(),
    'max_attack_half_hp':   BellyDrumEffect(),

    # ── Protection ─────────────────────────────────────────────────────────────
    'protect': ProtectEffect(),
    'endure':  EndureEffect(),

    # ── Météo ──────────────────────────────────────────────────────────────────
    'sunny_day':  SunnyDayEffect(),
    'rain_dance': RainDanceEffect(),
    'sandstorm':  SandstormEffect(),
    'hail':       HailEffect(),

    # ── Écrans ─────────────────────────────────────────────────────────────────
    'light_screen':  LightScreenEffect(),
    'reflect':       ReflectEffect(),
    'break_barrier': BreakBarrierEffect(),

    # ── Boosts de stats purs (power == 0) ──────────────────────────────────────
    'raise_attack':         StatBoostEffect([('attack',          1,  'self')]),
    'raise_defense':        StatBoostEffect([('defense',         1,  'self')]),
    'raise_special_attack': StatBoostEffect([('special_attack',  1,  'self')]),
    'raise_special_defense':StatBoostEffect([('special_defense', 1,  'self')]),
    'raise_speed':          StatBoostEffect([('speed',           1,  'self')]),
    'raise_evasion':        StatBoostEffect([('evasion',         1,  'self')]),
    'raise_accuracy':       StatBoostEffect([('accuracy',        1,  'self')]),
    'raise_attack_defense': StatBoostEffect([('attack', 1, 'self'), ('defense', 1, 'self')]),
    'raise_attack_speed':   StatBoostEffect([('attack', 1, 'self'), ('speed',   1, 'self')]),
    'raise_attack_accuracy':StatBoostEffect([('attack', 1, 'self'), ('accuracy',1, 'self')]),
    'raise_special_attack_special_defense':
        StatBoostEffect([('special_attack', 1, 'self'), ('special_defense', 1, 'self')]),
    'raise_defense_special_defense':
        StatBoostEffect([('defense', 1, 'self'), ('special_defense', 1, 'self')]),
    'raise_all_stats':
        StatBoostEffect([('attack', 1, 'self'), ('defense', 1, 'self'),
                         ('special_attack', 1, 'self'), ('special_defense', 1, 'self'),
                         ('speed', 1, 'self')]),
    'sharply_raise_attack':          StatBoostEffect([('attack',          2, 'self')]),
    'sharply_raise_defense':         StatBoostEffect([('defense',         2, 'self')]),
    'sharply_raise_special_attack':  StatBoostEffect([('special_attack',  2, 'self')]),
    'sharply_raise_special_defense': StatBoostEffect([('special_defense', 2, 'self')]),
    'sharply_raise_speed':           StatBoostEffect([('speed',           2, 'self')]),
    'raise_attack_speed_sharply':
        StatBoostEffect([('attack', 1, 'self'), ('speed', 2, 'self')]),
    'raise_attack_special_attack_speed_sharply_lower_defense_special_defense':
        StatBoostEffect([('attack', 2, 'self'), ('special_attack', 2, 'self'),
                         ('speed', 2, 'self'), ('defense', -1, 'self'),
                         ('special_defense', -1, 'self')]),

    'lower_attack':          StatBoostEffect([('attack',          -1, 'opponent')]),
    'lower_defense':         StatBoostEffect([('defense',         -1, 'opponent')]),
    'lower_special_defense': StatBoostEffect([('special_defense', -1, 'opponent')]),
    'lower_speed':           StatBoostEffect([('speed',           -1, 'opponent')]),
    'lower_accuracy':        StatBoostEffect([('accuracy',        -1, 'opponent')]),
    'lower_evasion':         StatBoostEffect([('evasion',         -1, 'opponent')]),
    'lower_sp_atk':          StatBoostEffect([('special_attack',  -1, 'opponent')]),
    'lower_special_attack':  StatBoostEffect([('special_attack',  -1, 'opponent')]),
    'lower_attack_defense':
        StatBoostEffect([('attack', -1, 'self'), ('defense', -1, 'self')]),
    'lower_defense_special_defense':
        StatBoostEffect([('defense', -1, 'self'), ('special_defense', -1, 'self')]),
    'sharply_lower_attack':
        StatBoostEffect([('attack',          -2, 'opponent')]),
    'sharply_lower_defense':
        StatBoostEffect([('defense',         -2, 'opponent')]),
    'sharply_lower_special_attack':
        StatBoostEffect([('special_attack',  -2, 'self')]),
    'sharply_lower_special_defense':
        StatBoostEffect([('special_defense', -2, 'opponent')]),
    'lower_special_attack_opponent':
        StatBoostEffect([('special_attack',  -2, 'opponent')]),

    # ── Nouveaux effets status ─────────────────────────────────────────────────
    'substitute':    SubstituteEffect(),
    'encore':        EncoreEffect(),
    'taunt':         TauntEffect(),
    'torment':       TormentEffect(),
    'trick':         TrickEffect(),
    'switcharoo':    TrickEffect(),
    'wish':          WishEffect(),
    'mean_look':     MeanLookEffect(),
    'spider_web':    MeanLookEffect(),
    'block':         MeanLookEffect(),
    'trick_room':    TrickRoomEffect(),
    'tailwind':      TailwindEffect(),
    'perish_song':   PerishSongEffect(),
    'spikes':        SpikesEffect(),
    'toxic_spikes':  ToxicSpikesEffect(),
    'stealth_rock':  StealthRockEffect(),
    'conversion':    ConversionEffect(),
}