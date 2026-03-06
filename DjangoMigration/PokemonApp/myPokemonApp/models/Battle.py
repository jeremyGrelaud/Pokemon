#!/usr/bin/python3
"""! @brief Battle.py model — Logique de combat complète avec effets de moves spéciaux.

Système d'effets implémentés :
  - Dégâts spéciaux : drain, recoil, crash, faint_user/self_destruct, multi_hit,
    two_hit, high_crit, always_crit, fixed_damage_20, fixed_40, level_damage,
    half_hp, ohko, more_damage_if_hp, double_if_paralyzed, double_power_if_statused,
    never_miss (ignoré ici : déjà géré par l'absence de check précision)
  - Statut/Volatil : confuse, confusion_after, leech_seed, trap, flinch, disable,
    badly_poison (toxic counter), nightmare, destiny_bond, ingrain, focus_energy
  - Boost de stats : raise_*/lower_* (single + double stage), reset_stats,
    copy_stat_changes, raise_all_stats, lower_attack_defense, etc.
  - Charge/recharge : charge_turn (SolarBeam/Fly/Dig/Skull Bash), recharge (Hyper Beam)
  - Météo : sunny_day, rain_dance, sandstorm, hail (5 tours, effets fin de tour)
  - Soins : heal_half, heal_sleep (Rest), belly_drum, max_attack_half_hp
  - Divers : rampage, rollout, metronome, force_switch, tri_attack, protect, endure,
    drain_sleep (Dream Eater), remove_item, pain_split, future_sight, charge_turn variants
  - Fin de tour : Leech Seed, brûlure, poison, poison sévère, Ingrain, météo
"""

from django.db import models
import random

from .PlayablePokemon import PokemonMoveInstance
from .PokemonMove import PokemonMove
from .Trainer import Trainer
from .PlayablePokemon import PlayablePokemon
from .Trainer import TrainerInventory
from .MoveEffects import EFFECT_REGISTRY, SECONDARY_STAT_EFFECTS


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
WEATHER_DURATIONS = 5           # Tours de météo standard
CHARGE_MOVES = {
    'Solar Beam',
    'Dig',
    'Fly',
    'Skull Bash',
    'Sky Attack',
    'Dive',
    'Bounce',
    'Shadow Force',
    'Freeze Shock',
    'Ice Burn',
}


class Battle(models.Model):
    """Représente un combat Pokémon avec effets spéciaux complets."""

    BATTLE_TYPES = [
        ('wild',       'Pokémon sauvage'),
        ('trainer',    'Dresseur'),
        ('gym',        'Arène'),
        ('elite_four', 'Conseil des 4'),
    ]

    battle_type = models.CharField(max_length=20, choices=BATTLE_TYPES)

    # Participants
    player_trainer = models.ForeignKey(
        Trainer, on_delete=models.CASCADE, related_name='battles_as_player'
    )
    opponent_trainer = models.ForeignKey(
        Trainer, on_delete=models.CASCADE, related_name='battles_as_opponent',
        null=True, blank=True
    )

    # Pokémon actuels
    player_pokemon = models.ForeignKey(
        PlayablePokemon, on_delete=models.SET_NULL, null=True,
        related_name='battles_as_player_pokemon'
    )
    opponent_pokemon = models.ForeignKey(
        PlayablePokemon, on_delete=models.SET_NULL, null=True,
        related_name='battles_as_opponent_pokemon'
    )

    # État du combat
    is_active       = models.BooleanField(default=True)
    current_turn    = models.IntegerField(default=1)
    winner          = models.ForeignKey(
        Trainer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='won_battles'
    )

    # Météo et terrain
    weather = models.CharField(max_length=20, blank=True, null=True)
    terrain = models.CharField(max_length=20, blank=True, null=True)

    # Historique et état de combat volatile (JSONField)
    battle_log   = models.JSONField(default=list)
    battle_state = models.JSONField(default=dict)   # ← état volatile du combat

    # Snapshot permanent des équipes (début) + HP finaux (fin).
    battle_snapshot = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    ended_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name          = "Combat"
        verbose_name_plural   = "Combats"

    def __str__(self):
        opp = self.opponent_trainer.username if self.opponent_trainer else 'Sauvage'
        return f"Combat: {self.player_trainer.username} vs {opp}"

    # =========================================================================
    # HELPERS ÉTAT VOLATIL (battle_state)
    # =========================================================================

    def _bstate(self):
        """Retourne battle_state initialisé."""
        if not isinstance(self.battle_state, dict):
            self.battle_state = {}
        return self.battle_state

    def _pstate(self, pokemon):
        """Retourne le sous-dict d'état pour un Pokémon donné."""
        key = str(pokemon.pk)
        s   = self._bstate()
        if key not in s:
            s[key] = {}
        return s[key]

    def _save_state(self):
        self.save(update_fields=['battle_state'])

    # ─── Confuse ──────────────────────────────────────────────────────────────

    def is_confused(self, pokemon):
        return bool(self._pstate(pokemon).get('confusion_turns', 0) > 0)

    def confuse(self, pokemon):
        pst = self._pstate(pokemon)
        if not pst.get('confusion_turns', 0):
            pst['confusion_turns'] = random.randint(2, 5)
            self._save_state()
            return True
        return False

    def tick_confusion(self, pokemon):
        """Décrémente le compteur et retourne True si le Pokémon se blesse."""
        pst = self._pstate(pokemon)
        turns = pst.get('confusion_turns', 0)
        if turns <= 0:
            return False
        if turns == 1:
            pst['confusion_turns'] = 0
            self._save_state()
            self.add_to_log(f"{pokemon} n'est plus confus !")
            return False
        pst['confusion_turns'] = turns - 1
        self._save_state()
        if random.random() < 0.33:
            # Se blesse lui-même
            damage = max(1, int(((2 * pokemon.level / 5 + 2) * 40 * pokemon.attack / pokemon.defense) / 50 + 2))
            pokemon.current_hp = max(0, pokemon.current_hp - damage)
            pokemon.save()
            self.add_to_log(f"{pokemon} est confus et se blesse ! (-{damage} PV)")
            return True
        return False

    # ─── Leech Seed ──────────────────────────────────────────────────────────

    def has_leech_seed(self, pokemon):
        return bool(self._pstate(pokemon).get('leech_seed'))

    def apply_leech_seed(self, pokemon):
        pst = self._pstate(pokemon)
        if not pst.get('leech_seed'):
            pst['leech_seed'] = True
            self._save_state()
            return True
        return False

    # ─── Trap (Bind, Clamp, Fire Spin…) ─────────────────────────────────────

    def is_trapped(self, pokemon):
        return bool(self._pstate(pokemon).get('trap_turns', 0) > 0)

    def trap_pokemon(self, pokemon, move_name):
        pst = self._pstate(pokemon)
        if not pst.get('trap_turns', 0):
            pst['trap_turns']  = random.randint(2, 5)
            pst['trap_move']   = move_name
            self._save_state()

    # ─── Disable ─────────────────────────────────────────────────────────────

    def disable_move(self, pokemon):
        """Désactive aléatoirement un move du Pokémon pour 4 tours."""
        pst   = self._pstate(pokemon)
        moves = PokemonMoveInstance.objects.filter(pokemon=pokemon, current_pp__gt=0)
        if not moves.exists():
            return False
        chosen = random.choice(list(moves))
        pst['disabled_move_id'] = chosen.move.pk
        pst['disable_turns']    = 4
        self._save_state()
        self.add_to_log(f"{chosen.move.name} de {pokemon} est neutralisé !")
        return True

    def is_move_disabled(self, pokemon, move):
        pst = self._pstate(pokemon)
        return (pst.get('disabled_move_id') == move.pk and
                pst.get('disable_turns', 0) > 0)

    # ─── Recharge (Hyper Beam, Giga Impact…) ─────────────────────────────────

    def set_recharge(self, pokemon):
        self._pstate(pokemon)['recharge'] = True
        self._save_state()

    def needs_recharge(self, pokemon):
        return bool(self._pstate(pokemon).get('recharge'))

    def clear_recharge(self, pokemon):
        self._pstate(pokemon).pop('recharge', None)
        self._save_state()

    # ─── Charge (SolarBeam, Fly, Dig…) ───────────────────────────────────────

    def set_charging(self, pokemon, move_name):
        self._pstate(pokemon)['charging'] = move_name
        self._save_state()

    def get_charging_move(self, pokemon):
        return self._pstate(pokemon).get('charging')

    def clear_charging(self, pokemon):
        self._pstate(pokemon).pop('charging', None)
        self._save_state()

    # ─── Protect / Endure ─────────────────────────────────────────────────────

    def set_protected(self, pokemon):
        self._pstate(pokemon)['protected'] = True
        self._save_state()

    def is_protected(self, pokemon):
        return bool(self._pstate(pokemon).get('protected'))

    def clear_protected(self, pokemon):
        self._pstate(pokemon).pop('protected', None)
        self._save_state()

    def set_enduring(self, pokemon):
        self._pstate(pokemon)['enduring'] = True
        self._save_state()

    def is_enduring(self, pokemon):
        return bool(self._pstate(pokemon).get('enduring'))

    def clear_enduring(self, pokemon):
        self._pstate(pokemon).pop('enduring', None)
        self._save_state()

    # ─── Flinch ──────────────────────────────────────────────────────────────

    def set_flinched(self, pokemon):
        self._pstate(pokemon)['flinched'] = True
        self._save_state()

    def check_and_clear_flinch(self, pokemon):
        pst = self._pstate(pokemon)
        if pst.pop('flinched', False):
            self._save_state()
            return True
        return False

    # ─── Focus Energy (taux de critique élevé) ───────────────────────────────

    def set_focus_energy(self, pokemon):
        self._pstate(pokemon)['focus_energy'] = True
        self._save_state()

    def has_focus_energy(self, pokemon):
        return bool(self._pstate(pokemon).get('focus_energy'))

    # ─── Destiny Bond ────────────────────────────────────────────────────────

    def set_destiny_bond(self, pokemon):
        self._pstate(pokemon)['destiny_bond'] = True
        self._save_state()

    def check_destiny_bond(self, pokemon):
        return bool(self._pstate(pokemon).get('destiny_bond'))

    # ─── Ingrain ─────────────────────────────────────────────────────────────

    def set_ingrain(self, pokemon):
        self._pstate(pokemon)['ingrain'] = True
        self._save_state()

    def has_ingrain(self, pokemon):
        return bool(self._pstate(pokemon).get('ingrain'))

    # ─── Toxic counter ────────────────────────────────────────────────────────

    def get_toxic_counter(self, pokemon):
        return self._pstate(pokemon).get('toxic_counter', 0)

    def increment_toxic_counter(self, pokemon):
        pst = self._pstate(pokemon)
        pst['toxic_counter'] = pst.get('toxic_counter', 0) + 1
        self._save_state()

    def set_badly_poisoned(self, pokemon):
        pst = self._pstate(pokemon)
        pst['badly_poisoned'] = True
        pst['toxic_counter']  = 1
        self._save_state()

    def is_badly_poisoned(self, pokemon):
        return bool(self._pstate(pokemon).get('badly_poisoned'))

    # ─── Weather ─────────────────────────────────────────────────────────────

    def set_weather(self, weather_name):
        self.weather = weather_name
        self._bstate()['weather_turns'] = WEATHER_DURATIONS
        self.save(update_fields=['weather', 'battle_state'])

    def get_weather_turns(self):
        return self._bstate().get('weather_turns', 0)

    # ─── Future Sight ────────────────────────────────────────────────────────

    def set_future_sight(self, target_pokemon, damage):
        self._pstate(target_pokemon)['future_sight_damage'] = damage
        self._pstate(target_pokemon)['future_sight_turns']  = 2
        self._save_state()

    # ─── Nightmare ────────────────────────────────────────────────────────────

    def set_nightmare(self, pokemon):
        self._pstate(pokemon)['nightmare'] = True
        self._save_state()

    def has_nightmare(self, pokemon):
        return bool(self._pstate(pokemon).get('nightmare'))

    # ─── Light Screen / Reflect ──────────────────────────────────────────────

    def set_screen(self, side, screen_type):
        """side = 'player' | 'opponent'"""
        key = f"{side}_{screen_type}"
        self._bstate()[key] = 5  # 5 tours
        self._save_state()

    def get_screen_multiplier(self, side, category):
        key = f"{side}_{'light_screen' if category == 'special' else 'reflect'}"
        return 0.5 if self._bstate().get(key, 0) > 0 else 1.0

    # ─── Rampage / Rollout ────────────────────────────────────────────────────

    def set_rampage(self, pokemon, move_name, turns=None):
        pst = self._pstate(pokemon)
        pst['rampage_move']  = move_name
        pst['rampage_turns'] = turns if turns is not None else random.randint(2, 3)
        self._save_state()

    def is_rampaging(self, pokemon):
        pst = self._pstate(pokemon)
        return pst.get('rampage_turns', 0) > 0

    def tick_rampage(self, pokemon):
        pst = self._pstate(pokemon)
        turns = pst.get('rampage_turns', 0)
        if turns > 0:
            pst['rampage_turns'] = turns - 1
            self._save_state()
            if pst['rampage_turns'] == 0:
                pst.pop('rampage_move', None)
                self._save_state()
                self.confuse(pokemon)
                self.add_to_log(f"{pokemon} est confus après son emballement !")

    def get_rollout_count(self, pokemon):
        return self._pstate(pokemon).get('rollout_count', 0)

    def increment_rollout(self, pokemon):
        pst = self._pstate(pokemon)
        pst['rollout_count'] = pst.get('rollout_count', 0) + 1
        self._save_state()

    def reset_rollout(self, pokemon):
        self._pstate(pokemon).pop('rollout_count', None)
        self._save_state()

    # =========================================================================
    # LOG
    # =========================================================================

    def add_to_log(self, message):
        if not isinstance(self.battle_log, list):
            self.battle_log = []
        self.battle_log.append({'turn': self.current_turn, 'message': message})
        self.save(update_fields=['battle_log'])

    # =========================================================================
    # HELPERS — ABILITY SYSTEM
    # =========================================================================

    def _get_ability(self, pokemon):
        """Retourne l'ability du Pokémon si elle est implémentée (effect_tag présent)."""
        ability = getattr(pokemon, 'ability', None)
        if ability and ability.effect_tag:
            return ability
        return None

    def _get_opponent(self, pokemon):
        """Retourne le Pokémon adverse."""
        if pokemon == self.player_pokemon:
            return self.opponent_pokemon
        return self.player_pokemon
    
    # ── Held Item helpers ─────────────────────────────────────────────────
    def _get_held_effect(self, pokemon) -> str | None:
        """Retourne le held_effect de l'objet tenu du Pokémon, ou None."""
        item = getattr(pokemon, 'held_item', None)
        if item and item.held_effect:
            return item.held_effect
        return None

    def _consume_held_item(self, pokemon) -> None:
        """Retire l'objet tenu si is_consumable=True (sauvegarde FK uniquement)."""
        item = getattr(pokemon, 'held_item', None)
        if item and item.is_consumable:
            pokemon.held_item = None
            pokemon.save(update_fields=['held_item'])


    def _try_apply_status(self, target, status, attacker=None):
        """
        Tente d'appliquer un statut en vérifiant d'abord le talent du Pokémon cible.
        Retourne True si le statut a bien été appliqué.
        """
        ability = self._get_ability(target)
        if ability:
            result = ability.on_status(self, target, status)
            if result:
                if result.get('message'):
                    self.add_to_log(result['message'])
                if result.get('prevent_status'):
                    return False
                if result.get('transmit_status_to_opponent') and attacker:
                    transmitted = result['transmit_status_to_opponent']
                    if attacker.apply_status(transmitted):
                        self.add_to_log(f"{attacker} est aussi touché ({transmitted}) !")
        return target.apply_status(status)

    def _fire_switch_in_ability(self, pokemon):
        """Active le talent on_switch_in du Pokémon entrant en combat."""
        ability = self._get_ability(pokemon)
        if not ability:
            return
        result = ability.on_switch_in(self, pokemon)
        if not result:
            return
        if result.get('message'):
            self.add_to_log(result['message'])
        if result.get('set_weather'):
            self.set_weather(result['set_weather'])
        if result.get('lower_opponent_attack'):
            opp = self._get_opponent(pokemon)
            if opp:
                self.modify_stat(opp, 'attack', -result['lower_opponent_attack'])
        if result.get('raise_attack'):
            self.modify_stat(pokemon, 'attack', result['raise_attack'])
        if result.get('raise_special_attack'):
            self.modify_stat(pokemon, 'special_attack', result['raise_special_attack'])
        if result.get('copy_ability_from_opponent'):
            opp = self._get_opponent(pokemon)
            if opp and opp.ability:
                pokemon.ability = opp.ability
                pokemon.save(update_fields=['ability'])
                self.add_to_log(f"{pokemon} a maintenant le talent {opp.ability.name} !")

    def _fire_switch_out_ability(self, pokemon):
        """Active le talent on_switch_out du Pokémon qui sort du combat."""
        ability = self._get_ability(pokemon)
        if not ability:
            return
        result = ability.on_switch_out(self, pokemon)
        if not result:
            return
        if result.get('message'):
            self.add_to_log(result['message'])
        if result.get('clear_status'):
            pokemon.cure_status()
            pokemon.save()
        if result.get('heal'):
            healed = min(pokemon.max_hp - pokemon.current_hp, result['heal'])
            if healed > 0:
                pokemon.current_hp += healed
                pokemon.save()
                self.add_to_log(f"{pokemon} récupère {healed} PV !")

    # =========================================================================
    # TOUR DE COMBAT PRINCIPAL
    # =========================================================================

    def execute_turn(self, player_action, opponent_action):
        """Exécute un tour complet de combat."""

        # ── Réinitialiser Protect/Endure (valable 1 seul tour) ───────────────
        self.clear_protected(self.player_pokemon)
        self.clear_enduring(self.player_pokemon)
        self.clear_protected(self.opponent_pokemon)
        self.clear_enduring(self.opponent_pokemon)

        # ── Fuite ────────────────────────────────────────────────────────────
        if player_action.get('type') == 'flee':
            self.execute_action(self.player_pokemon, self.opponent_pokemon, player_action)
            return
        if opponent_action.get('type') == 'flee':
            self.execute_action(self.opponent_pokemon, self.player_pokemon, opponent_action)
            return

        # ── Switch (priorité maximale) ────────────────────────────────────────
        player_is_switching   = player_action.get('type') == 'switch'
        opponent_is_switching = opponent_action.get('type') == 'switch'

        if player_is_switching:
            self.switch_pokemon(self.player_pokemon, player_action.get('pokemon'))
        if opponent_is_switching:
            self.switch_pokemon(self.opponent_pokemon, opponent_action.get('pokemon'))

        if player_is_switching and opponent_is_switching:
            self.current_turn += 1
            self.save()
            return
        if player_is_switching:
            self.execute_action(self.opponent_pokemon, self.player_pokemon, opponent_action)
            self._apply_end_of_turn_effects()
            self.current_turn += 1
            self.save()
            return
        if opponent_is_switching:
            self.execute_action(self.player_pokemon, self.opponent_pokemon, player_action)
            self._apply_end_of_turn_effects()
            self.current_turn += 1
            self.save()
            return

        # ── Items ─────────────────────────────────────────────────────────────
        player_using_item   = player_action.get('type') == 'item'
        opponent_using_item = opponent_action.get('type') == 'item'

        if player_action.get('type') == 'PokeBall':
            pass

        if player_using_item:
            item   = player_action.get('item')
            target = player_action.get('target')
            result = item.use_on_pokemon(target)
            msg = result.get('message', str(result)) if isinstance(result, dict) else result
            self.add_to_log(msg)
        if opponent_using_item:
            item   = opponent_action.get('item')
            target = opponent_action.get('target')
            result = item.use_on_pokemon(target)
            msg = result.get('message', str(result)) if isinstance(result, dict) else result
            self.add_to_log(msg)

        if player_using_item and opponent_using_item:
            self.current_turn += 1
            self.save()
            return
        if player_using_item:
            self.execute_action(self.opponent_pokemon, self.player_pokemon, opponent_action)
            self._apply_end_of_turn_effects()
            self.current_turn += 1
            self.save()
            return
        if opponent_using_item:
            self.execute_action(self.player_pokemon, self.opponent_pokemon, player_action)
            self._apply_end_of_turn_effects()
            self.current_turn += 1
            self.save()
            return

        # ── Ordre d'attaque ───────────────────────────────────────────────────
        player_speed   = self.player_pokemon.get_effective_speed()
        opponent_speed = self.opponent_pokemon.get_effective_speed()

        player_priority   = (player_action.get('move').priority
                             if player_action.get('type') == 'attack' and player_action.get('move')
                             else 0)
        opponent_priority = (opponent_action.get('move').priority
                             if opponent_action.get('type') == 'attack' and opponent_action.get('move')
                             else 0)

        if player_priority > opponent_priority:
            first  = (self.player_pokemon, player_action, self.opponent_pokemon)
            second = (self.opponent_pokemon, opponent_action, self.player_pokemon)
            player_first = True
        elif opponent_priority > player_priority:
            first  = (self.opponent_pokemon, opponent_action, self.player_pokemon)
            second = (self.player_pokemon, player_action, self.opponent_pokemon)
            player_first = False
        else:
            # ── Salle Bizarre : inverser la comparaison de vitesse ──────────
            trick_room = self._bstate().get('trick_room_turns', 0) > 0
            p_speed    = self.player_pokemon.get_effective_speed()
            o_speed    = self.opponent_pokemon.get_effective_speed()
            # Tailwind : ×2 sur la vitesse effective du côté concerné
            if self._bstate().get('player_tailwind', 0) > 0:
                p_speed *= 2
            if self._bstate().get('opponent_tailwind', 0) > 0:
                o_speed *= 2

            player_faster = (p_speed < o_speed) if trick_room else (p_speed > o_speed)
            opponent_faster = (o_speed < p_speed) if trick_room else (o_speed > p_speed)

            if player_faster:
                first  = (self.player_pokemon, player_action, self.opponent_pokemon)
                second = (self.opponent_pokemon, opponent_action, self.player_pokemon)
                player_first = True
            elif opponent_faster:
                first  = (self.opponent_pokemon, opponent_action, self.player_pokemon)
                second = (self.player_pokemon, player_action, self.opponent_pokemon)
                player_first = False
            else:
                player_first = random.choice([True, False])
                if player_first:
                    first  = (self.player_pokemon, player_action, self.opponent_pokemon)
                    second = (self.opponent_pokemon, opponent_action, self.player_pokemon)
                else:
                    first  = (self.opponent_pokemon, opponent_action, self.player_pokemon)
                    second = (self.player_pokemon, player_action, self.opponent_pokemon)

        # Helper pour extraire infos du move depuis une action
        def _move_info(action):
            move = action.get('move')
            if move:
                return {
                    'name':     move.name,
                    'type':     move.type.name if move.type else '',
                    'category': move.category or '',
                }
            return {'name': '', 'type': '', 'category': ''}

        player_move_info   = _move_info(player_action)
        opponent_move_info = _move_info(opponent_action)

        # Premier attaquant
        attacker, action, defender = first
        self.execute_action(attacker, defender, action)
        if defender.is_fainted():
            # Vérifier Destiny Bond
            if self.check_destiny_bond(defender):
                attacker.current_hp = 0
                attacker.save()
                self.add_to_log(f"{defender} emporte {attacker} avec lui !")
            self.add_to_log(f"{defender} est K.O.!")
            # Store turn info: second attacker was skipped (defender KO'd first)
            bs = self._bstate()
            bs['last_turn_info'] = {
                'player_first':    player_first,
                'second_skipped':  True,
                'player_move':     player_move_info,
                'opponent_move':   opponent_move_info,
            }
            self._save_state()
            self.current_turn += 1
            self.save()
            return

        # Second attaquant
        attacker, action, defender = second
        self.execute_action(attacker, defender, action)
        if defender.is_fainted():
            if self.check_destiny_bond(defender):
                attacker.current_hp = 0
                attacker.save()
                self.add_to_log(f"{defender} emporte {attacker} avec lui !")
            self.add_to_log(f"{defender} est K.O.!")

        # Store turn info: both attackers acted
        bs = self._bstate()
        bs['last_turn_info'] = {
            'player_first':   player_first,
            'second_skipped': False,
            'player_move':    player_move_info,
            'opponent_move':  opponent_move_info,
        }
        self._save_state()

        # ── Effets de fin de tour ─────────────────────────────────────────────
        self._apply_end_of_turn_effects()
        self.current_turn += 1
        self.save()

    # =========================================================================
    # EXÉCUTION D'UNE ACTION
    # =========================================================================

    def execute_action(self, attacker, defender, action):
        action_type = action.get('type')
        if action_type == 'attack':
            move = action.get('move')
            self.use_move(attacker, defender, move)
        elif action_type == 'switch':
            self.switch_pokemon(attacker, action.get('pokemon'))
        elif action_type == 'flee':
            self.attempt_flee()

    # =========================================================================
    # UTILISATION D'UN MOVE
    # =========================================================================

    def use_move(self, attacker, defender, move):
        """Utilise une capacité avec tous ses effets spéciaux."""

        # ── Struggle ─────────────────────────────────────────────────────────
        if move.name == "Struggle":
            move_instance, _ = PokemonMoveInstance.objects.get_or_create(
                pokemon=attacker, move=move, defaults={'current_pp': 99999}
            )
        else:
            try:
                move_instance = PokemonMoveInstance.objects.get(pokemon=attacker, move=move)
            except PokemonMoveInstance.DoesNotExist:
                self.add_to_log(f"{attacker} ne connaît pas {move.name} !")
                return

        if not move_instance.can_use():
            self.add_to_log(f"{attacker} n'a plus de PP pour {move.name} !")
            # Utiliser Struggle
            struggle = PokemonMove.objects.filter(name__iexact='Struggle').first()
            if struggle:
                self.use_move(attacker, defender, struggle)
            return

        # ── Vérifier si un move est désactivé ────────────────────────────────
        if self.is_move_disabled(attacker, move):
            self.add_to_log(f"{move.name} de {attacker} est neutralisé !")
            return

        # ── Encore : forcer le move encored ──────────────────────────────────
        pst_attacker = self._pstate(attacker)
        encore_turns = pst_attacker.get('encore_turns', 0)
        if encore_turns > 0:
            encored_name = pst_attacker.get('encore_move')
            if encored_name and move.name != encored_name:
                try:
                    move = PokemonMove.objects.get(name=encored_name)
                    move_instance = PokemonMoveInstance.objects.get(
                        pokemon=attacker, move=move
                    )
                    self.add_to_log(f"{attacker} est forcé d'utiliser {move.name} (Encore) !")
                except (PokemonMove.DoesNotExist, PokemonMoveInstance.DoesNotExist):
                    pass

        # ── Raillerie (Taunt) : interdit les moves de statut ─────────────────
        if pst_attacker.get('taunt_turns', 0) > 0:
            if not move.power or move.power == 0:
                self.add_to_log(
                    f"{attacker} est raillé et ne peut pas utiliser {move.name} !"
                )
                return

        # ── Tourment (Torment) : interdit de répéter le même move ────────────
        if pst_attacker.get('torment'):
            last = pst_attacker.get('last_move_used')
            if last and last == move.name:
                self.add_to_log(
                    f"{attacker} est sous Tourment et ne peut pas répéter {move.name} !"
                )
                return

        # ── Vérifier le rechargement (Hyper Beam…) ────────────────────────────
        if self.needs_recharge(attacker):
            self.clear_recharge(attacker)
            self.add_to_log(f"{attacker} doit recharger !")
            return

        # ── Vérifier la phase de charge (SolarBeam, Fly…) ────────────────────
        charging = self.get_charging_move(attacker)
        if charging:
            # Phase 2 : lancer l'attaque
            if charging == move.name:
                self.clear_charging(attacker)
                # Passer directement aux dégâts
            else:
                self.add_to_log(f"{attacker} est en train de charger !")
                return

        elif move.effect == 'charge_turn':
            # Phase 1 : charger (sauf si Sunny Day pour SolarBeam)
            if move.name == 'Solar Beam' and self.weather == 'sunny':
                pass  # Pas de charge sous le soleil
            else:
                self.set_charging(attacker, move.name)
                if move.name == 'Skull Bash':
                    self.modify_stat(attacker, 'defense', 1)
                elif move.name == 'Sky Attack':
                    pass
                self.add_to_log(f"{attacker} se concentre !")
                move_instance.use()
                return

        # ── Effets Protect avant d'utiliser ──────────────────────────────────
        if move.effect == 'protect':
            self.set_protected(attacker)
            self.add_to_log(f"{attacker} se protège !")
            move_instance.use()
            return

        if move.effect == 'endure':
            self.set_enduring(attacker)
            self.add_to_log(f"{attacker} se prépare à tenir le coup !")
            move_instance.use()
            return

        # ── Vérifier si le défenseur est protégé ─────────────────────────────
        if self.is_protected(defender) and move.priority >= 0:
            self.add_to_log(f"{attacker} attaque mais {defender} est protégé !")
            move_instance.use()
            return

        # ── Effets de statut qui bloquent l'action ────────────────────────────
        if attacker.status_condition == 'paralysis' and random.random() < 0.25:
            self.add_to_log(f"{attacker} est paralysé et ne peut pas attaquer !")
            return

        if attacker.status_condition == 'freeze':
            if random.random() < 0.8:
                self.add_to_log(f"{attacker} est gelé et ne peut pas attaquer !")
                return
            else:
                attacker.status_condition = None
                attacker.save()
                self.add_to_log(f"{attacker} dégèle !")

        if attacker.status_condition == 'sleep':
            if attacker.sleep_turns > 0:
                attacker.sleep_turns -= 1
                attacker.save()
                self.add_to_log(f"{attacker} dort profondément…")
                return
            else:
                attacker.status_condition = None
                attacker.save()
                self.add_to_log(f"{attacker} se réveille !")

        # ── Confusion ────────────────────────────────────────────────────────
        if self.is_confused(attacker):
            self.add_to_log(f"{attacker} est confus !")
            hurt = self.tick_confusion(attacker)
            if hurt:
                if attacker.is_fainted():
                    return
                return  # Frappe lui-même, skip l'attaque

        # ── Rampage forcé ─────────────────────────────────────────────────────
        if self.is_rampaging(attacker):
            rampage_move_name = self._pstate(attacker).get('rampage_move')
            if rampage_move_name and move.name != rampage_move_name:
                # Forcer le move du rampage
                try:
                    forced = PokemonMove.objects.get(name=rampage_move_name)
                    move   = forced
                except PokemonMove.DoesNotExist:
                    pass

        # ── Flinch ────────────────────────────────────────────────────────────
        if self.check_and_clear_flinch(attacker):
            self.add_to_log(f"{attacker} a le sursaut et ne peut pas attaquer !")
            return

        # ── Nightmare ─────────────────────────────────────────────────────────
        if (self.has_nightmare(attacker) and
                attacker.status_condition == 'sleep'):
            dmg = max(1, attacker.max_hp // 4)
            attacker.current_hp = max(0, attacker.current_hp - dmg)
            attacker.save()
            self.add_to_log(f"{attacker} souffre d'un Cauchemar ! (-{dmg} PV)")
            if attacker.is_fainted():
                return

        # ── Consommation des PP ───────────────────────────────────────────────
        move_instance.use()
        self.add_to_log(f"{attacker} utilise {move.name} !")

        # ── Tracker le dernier move utilisé (pour Encore / Tourment) ─────────
        self._pstate(attacker)['last_move_used'] = move.name
        if encore_turns > 0:
            self._pstate(attacker)['encore_turns'] = encore_turns - 1
            if self._pstate(attacker)['encore_turns'] == 0:
                self._pstate(attacker).pop('encore_move', None)
                self.add_to_log(f"{attacker} n'est plus sous l'effet d'Encore !")
        self._save_state()

        # ── Métronome ─────────────────────────────────────────────────────────
        if move.effect == 'metronome' or move.effect == 'random_move':
            all_moves = list(PokemonMove.objects.exclude(name__in=['Metronome', 'Struggle']))
            if all_moves:
                move = random.choice(all_moves)
                self.add_to_log(f"Métronome choisit {move.name} !")
                self._apply_move_effect(attacker, defender, move, move_instance)
            return

        # ── Splash / no_effect ────────────────────────────────────────────────
        if move.effect in ('no_effect', 'splash'):
            self.add_to_log("Rien ne s'est passé !")
            return

        # ── Vérifier la précision (sauf never_miss) ───────────────────────────
        if move.effect != 'never_miss' and move.name != 'Struggle':
            accuracy = move.accuracy if move.accuracy else 100
            # Toujours appliquer les stages de précision/esquive, même si accuracy=100
            acc_mod  = attacker.get_stat_multiplier(attacker.accuracy_stage)
            eva_mod  = attacker.get_stat_multiplier(-defender.evasion_stage)
            hit_pct  = accuracy * acc_mod * eva_mod
            if random.randint(1, 100) > hit_pct:
                self.add_to_log(f"L'attaque a raté !")
                # Crash (High Jump Kick…)
                if move.effect in ('crash', 'high_jump_kick'):
                    dmg = max(1, attacker.max_hp // 2)
                    attacker.current_hp = max(0, attacker.current_hp - dmg)
                    attacker.save()
                    self.add_to_log(f"{attacker} s'est blessé en tombant ! (-{dmg} PV)")
                return

        # ── Appliquer l'effet du move ─────────────────────────────────────────
        self._apply_move_effect(attacker, defender, move, move_instance)

    # =========================================================================
    # DISPATCH DES EFFETS
    # =========================================================================

    def _apply_move_effect(self, attacker, defender, move, move_instance=None):
        """Dispatcher central : délègue à EFFECT_REGISTRY, puis gère les effets de dégâts."""

        effect = move.effect or ''

        # ═════════════════════════════════════════════════════════════════════
        # 1. REGISTRE — effets purs et pré-traitements (protect, météo, etc.)
        # ═════════════════════════════════════════════════════════════════════
        handler = EFFECT_REGISTRY.get(effect)
        if handler is not None:
            # Pour les StatBoostEffect : ne s'applique qu'en move pur (power==0)
            from .MoveEffects import StatBoostEffect
            if isinstance(handler, StatBoostEffect) and (move.power or 0) > 0:
                pass   # Effet secondaire → géré plus bas avec effect_chance
            else:
                handled = handler.apply(self, attacker, defender, move)
                if handled:
                    return
                # handled=False → pré-traitement fait (break_barrier…), on continue

        # ═════════════════════════════════════════════════════════════════════
        # 2. EFFETS DE DÉGÂTS SPÉCIAUX
        # ═════════════════════════════════════════════════════════════════════

        # ─── Superpower (lower_attack_defense sur soi + dégâts) ─────────────
        if effect == 'lower_attack_defense' and (move.power or 0) > 0:
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            self.modify_stat(attacker, 'attack', -1)
            self.modify_stat(attacker, 'defense', -1)
            return

        # ─── Close Combat (lower_defense_special_defense + dégâts) ──────────
        if effect == 'lower_defense_special_defense' and (move.power or 0) > 0:
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            self.modify_stat(attacker, 'defense', -1)
            self.modify_stat(attacker, 'special_defense', -1)
            return

        # ─── OHKO (Fissure, Guillotine, Horn Drill) ──────────────────────────
        if effect == 'ohko':
            if attacker.level < defender.level:
                self.add_to_log("L'attaque a raté !")
                return
            ohko_acc = 30 + (attacker.level - defender.level)
            if random.randint(1, 100) <= ohko_acc:
                defender.current_hp = 0
                defender.save()
                self.add_to_log("Victoire par KO instantané !")
            else:
                self.add_to_log("L'attaque a raté !")
            return

        # ─── Dégâts fixes ────────────────────────────────────────────────────
        if effect == 'fixed_damage_20':
            self._apply_fixed_damage(defender, 20)
            return

        if effect == 'fixed_40':
            self._apply_fixed_damage(defender, 40)
            return

        if effect == 'level_damage':
            self._apply_fixed_damage(defender, attacker.level)
            return

        if effect == 'half_hp':
            self._apply_fixed_damage(defender, max(1, defender.current_hp // 2))
            return

        # ─── Puissance variable (Eruption, Magnitude) ────────────────────────
        if effect == 'more_damage_if_hp':
            power  = max(1, int(move.power * attacker.current_hp / attacker.max_hp))
            damage = self._calculate_damage_with_power(attacker, defender, move, power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        if effect == 'random_power':
            magnitudes = [
                (10, 4), (20, 8), (30, 14), (50, 19), (70, 24),
                (90, 29), (110, 34), (150, 39), (80, 44), (120, 49),
            ]
            r = random.randint(0, 50)
            power, mag_level = 70, 7
            for idx, (p, threshold) in enumerate(magnitudes, 1):
                if r <= threshold:
                    power, mag_level = p, idx
                    break
            self.add_to_log(f"Magnitude {mag_level} !")
            damage = self._calculate_damage_with_power(attacker, defender, move, power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Prescience (Future Sight) ───────────────────────────────────────
        if effect == 'future_sight':
            damage = self.calculate_damage(attacker, defender, move)
            self.set_future_sight(defender, damage)
            self.add_to_log(f"{attacker} prédit l'avenir…")
            return

        # ─── Tri-Attaque ──────────────────────────────────────────────────────
        if effect == 'tri_attack':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if not defender.is_fainted() and random.randint(1, 100) <= 20:
                status = random.choice(['paralysis', 'burn', 'freeze'])
                if self._try_apply_status(defender, status, attacker):
                    self.add_to_log(f"{defender} est {status} !")
            return

        # ─── Drain (Absorb, Giga Drain, Drain Punch…) ───────────────────────
        if effect == 'drain':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if damage > 0:
                healed = max(1, damage // 2)
                attacker.current_hp = min(attacker.max_hp, attacker.current_hp + healed)
                attacker.save()
                self.add_to_log(f"{attacker} récupère {healed} PV !")
            return

        if effect == 'drain_sleep':   # Dream Eater
            if defender.status_condition != 'sleep':
                self.add_to_log(f"{defender} ne dort pas !")
                return
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if damage > 0:
                healed = max(1, damage // 2)
                attacker.current_hp = min(attacker.max_hp, attacker.current_hp + healed)
                attacker.save()
                self.add_to_log(f"{attacker} récupère {healed} PV !")
            return

        # ─── Recoil (Double-Edge, Flare Blitz…) ─────────────────────────────
        if effect == 'recoil':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if damage > 0:
                attk_ability = self._get_ability(attacker)
                rock_head = (
                    attk_ability and
                    attk_ability.effect_tag in ('rock_head', 'magic_guard')
                )
                if not rock_head:
                    recoil = max(1, damage // 3)
                    attacker.current_hp = max(0, attacker.current_hp - recoil)
                    attacker.save()
                    self.add_to_log(
                        f"{attacker} est blessé par le contrecoup ! (-{recoil} PV)"
                    )
            return

        # ─── Self-Destruct / Explosion ────────────────────────────────────────
        if effect in ('faint_user', 'self_destruct'):
            if effect == 'self_destruct':
                orig_def = defender.defense
                defender.defense = max(1, defender.defense // 2)
                damage = self.calculate_damage(attacker, defender, move)
                defender.defense = orig_def
            else:
                damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            attacker.current_hp = 0
            attacker.save()
            self.add_to_log(f"{attacker} s'est sacrifié !")
            return

        # ─── Rampage (Outrage, Thrash, Petal Dance) ──────────────────────────
        if effect in ('rampage', 'confusion_after'):
            if not self.is_rampaging(attacker):
                self.set_rampage(attacker, move.name)
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            self.tick_rampage(attacker)
            return

        # ─── Rollout ──────────────────────────────────────────────────────────
        if effect == 'rollout':
            count  = self.get_rollout_count(attacker)
            power  = move.power * (2 ** count)
            damage = self._calculate_damage_with_power(attacker, defender, move, power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if not defender.is_fainted():
                self.increment_rollout(attacker)
                if count >= 4:
                    self.reset_rollout(attacker)
            else:
                self.reset_rollout(attacker)
            return

        # ─── Multi-hit ────────────────────────────────────────────────────────
        if effect == 'multi_hit':
            r = random.random()
            if   r < 0.35: hits = 2
            elif r < 0.70: hits = 3
            elif r < 0.85: hits = 4
            else:           hits = 5
            total = 0
            for _ in range(hits):
                if defender.is_fainted():
                    break
                dmg = self.calculate_damage(attacker, defender, move)
                defender.current_hp = max(0, defender.current_hp - dmg)
                total += dmg
            defender.save()
            self.add_to_log(f"Touche {hits} fois pour {total} dégâts totaux !")
            return

        if effect == 'two_hit':    # Double Kick, Twineedle
            total = 0
            for _ in range(2):
                if defender.is_fainted():
                    break
                dmg = self.calculate_damage(attacker, defender, move)
                defender.current_hp = max(0, defender.current_hp - dmg)
                total += dmg
            defender.save()
            self.add_to_log(f"Touche 2 fois pour {total} dégâts !")
            if (move.inflicts_status and
                    random.randint(1, 100) <= move.effect_chance):
                if self._try_apply_status(defender, move.inflicts_status, attacker):
                    self.add_to_log(f"{defender} est {move.inflicts_status} !")
            return

        # ─── Trap ────────────────────────────────────────────────────────────
        if effect == 'trap':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if not self.is_trapped(defender):
                self.trap_pokemon(defender, move.name)
                self.add_to_log(f"{defender} est pris au piège !")
            return

        # ─── Recharge (Hyper Beam, Giga Impact…) ────────────────────────────
        if effect == 'recharge':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            self.set_recharge(attacker)
            self.add_to_log(f"{attacker} doit se recharger au prochain tour !")
            return

        # ─── Smelling Salts (double si paralysé) ────────────────────────────
        if effect == 'double_if_paralyzed':
            power  = move.power * (2 if defender.status_condition == 'paralysis' else 1)
            damage = self._calculate_damage_with_power(attacker, defender, move, power)
            if defender.status_condition == 'paralysis':
                defender.status_condition = None
                defender.save()
                self.add_to_log(f"{defender} est guéri de sa paralysie !")
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Façade (double si statut) ───────────────────────────────────────
        if effect == 'double_power_if_statused':
            power  = move.power * (2 if attacker.status_condition else 1)
            damage = self._calculate_damage_with_power(attacker, defender, move, power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Assurance / Revanche ────────────────────────────────────────────
        if effect in ('double_if_hit', 'double_power_if_hit'):
            was_hit = self._pstate(attacker).get('was_hit_this_turn', False)
            power   = move.power * (2 if was_hit else 1)
            damage  = self._calculate_damage_with_power(attacker, defender, move, power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Poison sévère (Toxic pur ou secondaire comme Poison Fang) ───────
        if effect == 'badly_poison':
            if (move.power or 0) == 0:
                if random.randint(1, 100) <= (move.effect_chance or 100):
                    if not defender.status_condition:
                        defender.status_condition = 'poison'
                        defender.save()
                        self.set_badly_poisoned(defender)
                        self.add_to_log(f"{defender} est gravement empoisonné !")
            else:
                damage = self.calculate_damage(attacker, defender, move)
                self._apply_damage_to_defender(attacker, defender, move, damage)
                if (not defender.is_fainted() and
                        random.randint(1, 100) <= (move.effect_chance or 100) and
                        not defender.status_condition):
                    defender.status_condition = 'poison'
                    defender.save()
                    self.set_badly_poisoned(defender)
                    self.add_to_log(f"{defender} est gravement empoisonné !")
            return

        # ─── Knock Off ────────────────────────────────────────────────────────
        if effect == 'remove_item':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if getattr(defender, 'held_item', None):
                item_name = defender.held_item.name
                defender.held_item = None
                defender.save()
                self.add_to_log(f"{defender} perd son {item_name} !")
            return

        # ─── Struggle ─────────────────────────────────────────────────────────
        if move.name == 'Struggle':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            recoil = max(1, attacker.max_hp // 4)
            attacker.current_hp = max(0, attacker.current_hp - recoil)
            attacker.save()
            self.add_to_log(f"{attacker} souffre du contrecoup ! (-{recoil} PV)")
            return

        # ═════════════════════════════════════════════════════════════════════
        # 3. ATTAQUE GÉNÉRIQUE (power > 0) + effets secondaires
        # ═════════════════════════════════════════════════════════════════════
        if (move.power or 0) > 0:
            damage = self.calculate_damage(attacker, defender, move)

            # Modificateurs météo
            if self.weather == 'sunny':
                if hasattr(move.type, 'name'):
                    if move.type.name == 'fire':    damage = int(damage * 1.5)
                    elif move.type.name == 'water': damage = int(damage * 0.5)
            elif self.weather == 'rain':
                if hasattr(move.type, 'name'):
                    if move.type.name == 'water':   damage = int(damage * 1.5)
                    elif move.type.name == 'fire':  damage = int(damage * 0.5)

            self._apply_damage_to_defender(attacker, defender, move, damage)

            if not defender.is_fainted():
                sheer_force  = self._pstate(attacker).get('sheer_force_active', False)
                serene_grace = self._pstate(attacker).get('serene_grace_active', False)

                if not sheer_force:
                    # Statut secondaire
                    if move.inflicts_status:
                        eff_chance = (move.effect_chance or 0) * (2 if serene_grace else 1)
                        if random.randint(1, 100) <= eff_chance:
                            if self._try_apply_status(
                                defender, move.inflicts_status, attacker
                            ):
                                self.add_to_log(f"{defender} est {move.inflicts_status} !")

                    # Flinch secondaire
                    if effect == 'flinch':
                        flinch_chance = (move.effect_chance or 0) * (2 if serene_grace else 1)
                        if random.randint(1, 100) <= flinch_chance:
                            def_ability = self._get_ability(defender)
                            if not (def_ability and
                                    def_ability.effect_tag == 'inner_focus'):
                                self.set_flinched(defender)

                    # Effets de stat secondaires (via move.stat_changes JSON)
                    if move.stat_changes:
                        for stat, change in move.stat_changes.items():
                            self.modify_stat(
                                attacker if change > 0 else defender, stat, change
                            )

                    # Effets de stat secondaires via le champ effect
                    if effect in SECONDARY_STAT_EFFECTS:
                        for stat_name, stages, who in SECONDARY_STAT_EFFECTS[effect]:
                            chance = (move.effect_chance or 0) * (2 if serene_grace else 1)
                            if random.randint(1, 100) <= chance:
                                target = attacker if who == 'self' else defender
                                self.modify_stat(target, stat_name, stages)

        else:
            # ── Move de statut sans handler reconnu (fallback) ────────────────
            if move.inflicts_status:
                if random.randint(1, 100) <= (move.effect_chance or 100):
                    if self._try_apply_status(defender, move.inflicts_status, attacker):
                        self.add_to_log(f"{defender} est {move.inflicts_status} !")
            if move.stat_changes:
                for stat, change in move.stat_changes.items():
                    self.modify_stat(
                        attacker if change > 0 else defender, stat, change
                    )

    # =========================================================================
    # HELPERS DÉGÂTS
    # =========================================================================

    def _apply_fixed_damage(self, target, amount):
        """Applique des dégâts fixes (type-immunité ignorée)."""
        amount = max(1, int(amount))
        target.current_hp = max(0, target.current_hp - amount)
        target.save()
        self.add_to_log(f"{target} subit {amount} points de dégâts !")

    def _apply_damage_to_defender(self, attacker, defender, move, damage):
        """Applique les dégâts au défenseur avec gestion Substitut, Endure, talent et efficacité."""
        if damage <= 0:
            damage = 1 if (move.power or 0) > 0 else 0
        if damage == 0:
            return

        # ── Substitut : encaisse les dégâts à la place du Pokémon ───────────
        sub_hp = self._pstate(defender).get('substitute_hp', 0)
        if sub_hp > 0:
            remaining = sub_hp - damage
            if remaining <= 0:
                self._pstate(defender)['substitute_hp'] = 0
                self._save_state()
                self.add_to_log(
                    f"Le Substitut de {defender} est détruit ! "
                    f"({damage} dégâts absorbés)"
                )
            else:
                self._pstate(defender)['substitute_hp'] = remaining
                self._save_state()
                self.add_to_log(
                    f"Le Substitut de {defender} absorbe {damage} dégâts ! "
                    f"(PV restants : {remaining})"
                )
            # Les dégâts ne touchent pas le Pokémon lui-même
            return

        # ── Ability: on_damage_taken (pré-dégâts) ────────────────────────────
        ignore_ability = self._pstate(attacker).get('ignore_opponent_ability', False)
        def_ability    = self._get_ability(defender) if not ignore_ability else None
        ab_result      = None

        if def_ability:
            ab_result = def_ability.on_damage_taken(self, defender, damage, move)
            if ab_result:
                # --- Blocage total (Levitate, Flash Fire, Volt/Water Absorb…) ---
                if ab_result.get('block'):
                    if ab_result.get('message'):
                        self.add_to_log(ab_result['message'])
                    heal = ab_result.get('heal', 0)
                    if heal:
                        healed = min(defender.max_hp - defender.current_hp, heal)
                        if healed > 0:
                            defender.current_hp += healed
                            defender.save()
                            self.add_to_log(f"{defender} récupère {healed} PV !")
                    if ab_result.get('boost_fire'):
                        self._pstate(defender)['flash_fire_active'] = True
                        self._save_state()
                    return  # dégâts bloqués

                # --- Réduction de dégâts (Thick Fat, Filter, Solid Rock…) ---
                if ab_result.get('power_multiplier'):
                    damage = max(1, int(damage * ab_result['power_multiplier']))
                    if ab_result.get('message'):
                        self.add_to_log(ab_result['message'])

        # ── Endure : survivre avec 1 PV ─────────────────────────────────────
        if self.is_enduring(defender) and defender.current_hp <= damage:
            damage = defender.current_hp - 1
            self.add_to_log(f"{defender} tient le coup !")

        # ── Focus Sash : survivre à 1 PV (PV pleins requis) ─────────────────
        _hp_before = defender.current_hp
        if (self._get_held_effect(defender) == 'focus_sash'
                and _hp_before == defender.max_hp
                and _hp_before <= damage):
            damage = _hp_before - 1
        
        defender.current_hp = max(0, defender.current_hp - damage)
        defender.save()
        self.add_to_log(f"{defender} subit {damage} points de dégâts !")

        # ── Focus Sash : log + consommation après dégâts ─────────────────────
        if (self._get_held_effect(defender) == 'focus_sash'
                and _hp_before == defender.max_hp
                and defender.current_hp == 1):
            self.add_to_log(
                f"La Ceinture Concentration de {defender} lui permet de tenir !"
            )
            self._consume_held_item(defender)

        # ── Life Orb : recul 1/10 PV max sur l'attaquant ────────────────────
        if self._get_held_effect(attacker) == 'life_orb' and damage > 0:
            _mg = self._get_ability(attacker)
            if not (_mg and _mg.effect_tag == 'magic_guard'):
                _recoil = max(1, attacker.max_hp // 10)
                attacker.current_hp = max(0, attacker.current_hp - _recoil)
                attacker.save(update_fields=['current_hp'])
                self.add_to_log(
                    f"L'Orbe Vie blesse {attacker} en retour ! (-{_recoil} PV)"
                )

        # ── Efficacité des types ─────────────────────────────────────────────
        effectiveness = self.get_type_effectiveness(move.type, defender)
        if effectiveness > 1:
            self.add_to_log("C'est super efficace !")
        elif 0 < effectiveness < 1:
            self.add_to_log("Ce n'est pas très efficace…")
        elif effectiveness == 0:
            self.add_to_log("Ça n'a aucun effet !")

        # ── Marquer que le défenseur a été touché ce tour ───────────────────
        self._pstate(defender)['was_hit_this_turn'] = True
        self._save_state()

        # ── Ability: effets de contact post-dégâts ───────────────────────────
        if ab_result and move is not None and not defender.is_fainted():
            if ab_result.get('inflict_status_on_attacker') and not attacker.is_fainted():
                status = ab_result['inflict_status_on_attacker']
                if self._try_apply_status(attacker, status):
                    self.add_to_log(f"{attacker} est affecté ({status}) par le contact !")
            if ab_result.get('confuse_attacker') and not attacker.is_fainted():
                if self.confuse(attacker):
                    self.add_to_log(f"{attacker} est troublé par le charme de {defender} !")
            if ab_result.get('damage_to_attacker') and not attacker.is_fainted():
                rebound = ab_result['damage_to_attacker']
                magic_guard_attacker = self._get_ability(attacker)
                if not (magic_guard_attacker and magic_guard_attacker.effect_tag == 'magic_guard'):
                    attacker.current_hp = max(0, attacker.current_hp - rebound)
                    attacker.save()
                    self.add_to_log(f"{attacker} est blessé par le contact ! (-{rebound} PV)")

    def _calculate_damage_with_power(self, attacker, defender, move, power):
        """Calcule les dégâts en surchargeant la puissance du move."""
        class _FakeMove:
            pass
        fake = _FakeMove()
        fake.power    = power
        fake.category = move.category
        fake.type     = move.type
        fake.effect   = move.effect
        return self.calculate_damage(attacker, defender, fake)

    # =========================================================================
    # CALCUL DE DÉGÂTS
    # =========================================================================

    def calculate_damage(self, attacker, defender, move):
        """
        Calcule les dégâts d'une attaque.

        Formule Gen 3+ :
            damage = floor( floor( floor(2*L/5 + 2) * Power * A/D ) / 50 + 2 )
                     × STAB × type_eff × crit × random × burn × screen
        """
        level = attacker.level

        if move.category == 'physical':
            attack_stat  = attacker.get_effective_attack()
            defense_stat = defender.get_effective_defense()
        else:
            attack_stat  = attacker.get_effective_special_attack()
            defense_stat = defender.get_effective_special_defense()

        # ── Ability: modify_stat (Guts, Huge Power, Swift Swim, Marvel Scale…) ──
        attk_ability = self._get_ability(attacker)
        if attk_ability:
            stat_name = 'attack' if move.category == 'physical' else 'special_attack'
            atk_mult  = attk_ability.modify_stat(stat_name, attacker, self)
            if atk_mult != 1.0:
                attack_stat = int(attack_stat * atk_mult)

        def_ability = self._get_ability(defender)
        if def_ability:
            stat_name = 'defense' if move.category == 'physical' else 'special_defense'
            def_mult  = def_ability.modify_stat(stat_name, defender, self)
            if def_mult != 1.0:
                defense_stat = int(defense_stat * def_mult)
            # Marvel Scale: boost défense si statut
            if def_ability.effect_tag == 'marvel_scale' and defender.status_condition:
                defense_stat = int(defense_stat * 1.5)

        # ── Dégâts de base ────────────────────────────────────────────────────
        damage = (((2 * level / 5 + 2) * move.power * attack_stat / max(1, defense_stat)) / 50) + 2

        # ── Ability: on_attack (Blaze, Torrent, Technician, Sheer Force…) ──────
        power_mult      = 1.0
        stab_override   = None
        ignore_opp_ab   = False
        suppress_second = False
        double_eff_ch   = False

        if attk_ability:
            atk_result = attk_ability.on_attack(self, attacker, move, move.power)
            if atk_result:
                if atk_result.get('message'):
                    self.add_to_log(atk_result['message'])
                power_mult      = atk_result.get('power_multiplier', 1.0)
                stab_override   = atk_result.get('stab_override')
                ignore_opp_ab   = atk_result.get('ignore_opponent_ability', False)
                suppress_second = atk_result.get('suppress_secondary_effect', False)
                double_eff_ch   = atk_result.get('double_effect_chance', False)
                # Store flags for _apply_move_effect
                pst = self._pstate(attacker)
                pst['sheer_force_active']     = suppress_second
                pst['serene_grace_active']    = double_eff_ch
                pst['ignore_opponent_ability'] = ignore_opp_ab
                self._save_state()

        if power_mult != 1.0:
            damage *= power_mult

        # ── Flash Fire: boost attaque Feu si actif ────────────────────────────
        if (attk_ability and attk_ability.effect_tag == 'flash_fire' and
                hasattr(move.type, 'name') and move.type.name == 'fire' and
                self._pstate(attacker).get('flash_fire_active')):
            damage *= 1.5
            self.add_to_log(f"Le talent Feu Intérieur de {attacker} enflamme l'attaque !")

        # ── Solar Power: boost Atq Spé au soleil ──────────────────────────────
        if (attk_ability and attk_ability.effect_tag == 'solar_power' and
                move.category == 'special' and self.weather == 'sunny'):
            damage *= 1.5

        # ── STAB ──────────────────────────────────────────────────────────────
        if stab_override is not None:
            if (move.type == attacker.species.primary_type or
                    move.type == attacker.species.secondary_type):
                damage *= stab_override
        else:
            if (move.type == attacker.species.primary_type or
                    move.type == attacker.species.secondary_type):
                damage *= 1.5

        # ── Efficacité des types ───────────────────────────────────────────────
        effectiveness = self.get_type_effectiveness(move.type, defender)
        damage       *= effectiveness
        self.last_effectiveness = effectiveness  # pour Tinted Lens / Filter

        if effectiveness == 0:
            return 0

        # ── Coup critique ─────────────────────────────────────────────────────
        crit_blocked = (def_ability and def_ability.effect_tag in ('shell_armor', 'battle_armor'))
        crit_rate    = 0.0 if crit_blocked else 1 / 16
        if not crit_blocked:
            if self.has_focus_energy(attacker):
                crit_rate = 1 / 4
            if getattr(move, 'effect', '') in ('high_crit',):
                crit_rate = min(1.0, crit_rate * 4)
            if getattr(move, 'effect', '') == 'always_crit':
                crit_rate = 1.0

        is_critical = random.random() < crit_rate
        if is_critical:
            damage *= 1.5
            self.add_to_log("Coup critique !")

        # ── Variation aléatoire 85–100% ────────────────────────────────────────
        damage *= random.uniform(0.85, 1.0)

        # ── Brûlure : ×0.5 sur physique ───────────────────────────────────────
        if attacker.status_condition == 'burn' and move.category == 'physical':
            # Guts annule le malus de brûlure sur l'Attaque
            if not (attk_ability and attk_ability.effect_tag == 'guts'):
                damage *= 0.5

        # ── Écrans (Light Screen / Reflect) ────────────────────────────────────
        side = 'opponent' if attacker == self.player_pokemon else 'player'
        damage *= self.get_screen_multiplier(side, move.category)


        # ── Held items — bonus offensifs (attaquant) ────────────────────────
        _attk_held = self._get_held_effect(attacker)
        if _attk_held and move.power:
            _mtype = getattr(move.type, 'name', '').lower() if move.type else ''

            if _attk_held == 'life_orb':
                damage *= 1.3

            elif _attk_held == 'choice_band' and move.category == 'physical':
                damage *= 1.5

            elif _attk_held == 'choice_specs' and move.category == 'special':
                damage *= 1.5

            else:
                _TYPE_BOOST = {
                    'type_boost_fire':     'fire',
                    'type_boost_electric': 'electric',
                    'type_boost_water':    'water',
                    'type_boost_psychic':  'psychic',
                    'type_boost_grass':    'grass',
                    'type_boost_normal':   'normal',
                }
                if _attk_held in _TYPE_BOOST and _mtype == _TYPE_BOOST[_attk_held]:
                    damage *= 1.2

        # ── Held items — baies de résistance (défenseur) ─────────────────────
        _def_held = self._get_held_effect(defender)
        if _def_held and move.power:
            _mtype = getattr(move.type, 'name', '').lower() if move.type else ''
            _eff   = getattr(self, 'last_effectiveness', 1.0)
            _RESIST = {
                'resist_berry_ice':   'ice',
                'resist_berry_fight': 'fighting',
            }
            if _def_held in _RESIST and _mtype == _RESIST[_def_held] and _eff >= 2.0:
                damage *= 0.5
                self.add_to_log(
                    f"La {defender.held_item.name} de {defender} atténue le coup !"
                )
                self._consume_held_item(defender)

        # ── Plancher à 1 ─────────────────────────────────────────────────────
        result = int(damage)
        return max(1, result) if move.power > 0 else 0

    # =========================================================================
    # EFFICACITÉ DES TYPES
    # =========================================================================

    def get_type_effectiveness(self, attack_type, defender):
        effectiveness = 1.0
        effectiveness *= attack_type.get_effectiveness(defender.species.primary_type)
        if defender.species.secondary_type:
            effectiveness *= attack_type.get_effectiveness(defender.species.secondary_type)
        return effectiveness

    # =========================================================================
    # MODIFICATION DE STATS
    # =========================================================================

    def modify_stat(self, pokemon, stat_name, stages):
        # ── Brume : bloque les baisses de stats ──────────────────────────────
        if stages < 0:
            side = 'player' if pokemon == self.player_pokemon else 'opponent'
            if self._bstate().get(f'{side}_mist', 0) > 0:
                self.add_to_log(
                    f"La Brume protège {pokemon} contre la baisse de {stat_name} !"
                )
                return

        current = getattr(pokemon, f"{stat_name}_stage", 0)
        new     = max(-6, min(6, current + stages))
        if new == current:
            msg = "ne peut plus monter" if stages > 0 else "ne peut plus descendre"
            self.add_to_log(f"L'{stat_name} de {pokemon} {msg} !")
            return
        setattr(pokemon, f"{stat_name}_stage", new)
        pokemon.save()
        intensite = " fortement" if abs(stages) >= 2 else ""
        if stages > 0:
            self.add_to_log(f"L'{stat_name} de {pokemon} augmente{intensite} !")
        else:
            self.add_to_log(f"L'{stat_name} de {pokemon} diminue{intensite} !")

    # =========================================================================
    # SWITCH
    # =========================================================================

    def switch_pokemon(self, trainer_pokemon, new_pokemon):
        # ── Talent on_switch_out pour le Pokémon sortant ────────────────────────
        self._fire_switch_out_ability(trainer_pokemon)

        # ── Effectuer le changement ─────────────────────────────────────────────
        if trainer_pokemon == self.player_pokemon:
            self.player_pokemon = new_pokemon
        else:
            self.opponent_pokemon = new_pokemon
        self.save()
        self.add_to_log(f"{new_pokemon} entre en combat !")

        # ── Dégâts d'entrée (Picots, Toxipics, Roc Furtif) ─────────────────────
        entering_side = 'player' if new_pokemon == self.player_pokemon else 'opponent'

        # Roc Furtif (Stealth Rock)
        if self._bstate().get(f'{entering_side}_stealth_rock'):
            rock_type_name = 'rock'
            from .PokemonType import PokemonType
            rock_type = PokemonType.objects.filter(name__iexact=rock_type_name).first()
            if rock_type:
                eff = rock_type.get_effectiveness(new_pokemon.species.primary_type)
                if new_pokemon.species.secondary_type:
                    eff *= rock_type.get_effectiveness(new_pokemon.species.secondary_type)
            else:
                eff = 1.0
            sr_dmg = max(1, int(new_pokemon.max_hp * eff / 8))
            new_pokemon.current_hp = max(0, new_pokemon.current_hp - sr_dmg)
            new_pokemon.save()
            self.add_to_log(
                f"Le Roc Furtif blesse {new_pokemon} à l'entrée ! (-{sr_dmg} PV)"
            )

        # Picots (Spikes) — pas d'effet sur les types Vol ou Lévitation
        spikes = self._bstate().get(f'{entering_side}_spikes', 0)
        if spikes > 0:
            ptype = getattr(new_pokemon.species.primary_type, 'name', '')
            stype = getattr(new_pokemon.species.secondary_type, 'name', '') \
                if new_pokemon.species.secondary_type else ''
            if 'flying' not in (ptype, stype):
                ratios = {1: 8, 2: 6, 3: 4}
                denom  = ratios.get(spikes, 8)
                sp_dmg = max(1, new_pokemon.max_hp // denom)
                new_pokemon.current_hp = max(0, new_pokemon.current_hp - sp_dmg)
                new_pokemon.save()
                self.add_to_log(
                    f"Les Picots blessent {new_pokemon} à l'entrée ! (-{sp_dmg} PV)"
                )

        # Toxipics (Toxic Spikes)
        tspikes = self._bstate().get(f'{entering_side}_toxic_spikes', 0)
        if tspikes > 0:
            ptype = getattr(new_pokemon.species.primary_type, 'name', '')
            stype = getattr(new_pokemon.species.secondary_type, 'name', '') \
                if new_pokemon.species.secondary_type else ''
            if 'flying' not in (ptype, stype) and not new_pokemon.status_condition:
                if tspikes == 1:
                    new_pokemon.status_condition = 'poison'
                    new_pokemon.save()
                    self.add_to_log(f"Les Toxipics empoisonnent {new_pokemon} !")
                else:
                    new_pokemon.status_condition = 'poison'
                    new_pokemon.save()
                    self.set_badly_poisoned(new_pokemon)
                    self.add_to_log(
                        f"Les Toxipics empoisonnent gravement {new_pokemon} !"
                    )

        # ── Talent on_switch_in pour le Pokémon entrant ─────────────────────────
        self._fire_switch_in_ability(new_pokemon)

    # =========================================================================
    # EFFETS DE FIN DE TOUR
    # =========================================================================

    def _apply_end_of_turn_effects(self):
        """Applique tous les effets de fin de tour (météo, statuts, Vampigraine, talents…)."""
        for pkmn in [self.player_pokemon, self.opponent_pokemon]:
            if not pkmn or pkmn.is_fainted():
                continue

            other = (self.opponent_pokemon if pkmn == self.player_pokemon
                     else self.player_pokemon)

            # ── Ability: end_of_turn (Speed Boost, Rain Dish, Poison Heal…) ───
            pkmn_ability   = self._get_ability(pkmn)
            has_magic_guard = (pkmn_ability and pkmn_ability.effect_tag == 'magic_guard')
            has_poison_heal = (pkmn_ability and pkmn_ability.effect_tag == 'poison_heal')
            block_poison    = False

            if pkmn_ability:
                eot_result = pkmn_ability.end_of_turn(self, pkmn)
                if eot_result:
                    if eot_result.get('message'):
                        self.add_to_log(eot_result['message'])
                    if eot_result.get('heal'):
                        healed = min(pkmn.max_hp - pkmn.current_hp, eot_result['heal'])
                        if healed > 0:
                            pkmn.current_hp += healed
                            pkmn.save()
                    if eot_result.get('damage') and not has_magic_guard:
                        pkmn.current_hp = max(0, pkmn.current_hp - eot_result['damage'])
                        pkmn.save()
                    if eot_result.get('raise_speed'):
                        self.modify_stat(pkmn, 'speed', eot_result['raise_speed'])
                    if eot_result.get('clear_status'):
                        pkmn.cure_status()
                        pkmn.save()
                    block_poison = eot_result.get('block_poison_damage', False)

            # ── Leech Seed ────────────────────────────────────────────────────
            if self.has_leech_seed(pkmn) and not has_magic_guard:
                drain_hp = max(1, pkmn.max_hp // 8)
                pkmn.current_hp = max(0, pkmn.current_hp - drain_hp)
                pkmn.save()
                self.add_to_log(f"Vampigraine suce {drain_hp} PV à {pkmn} !")
                if other and not other.is_fainted():
                    other.current_hp = min(other.max_hp, other.current_hp + drain_hp)
                    other.save()

            # ── Trap ──────────────────────────────────────────────────────────
            pst = self._pstate(pkmn)
            trap_turns = pst.get('trap_turns', 0)
            if trap_turns > 0 and not has_magic_guard:
                trap_dmg = max(1, pkmn.max_hp // 8)
                pkmn.current_hp = max(0, pkmn.current_hp - trap_dmg)
                pkmn.save()
                self.add_to_log(f"{pkmn} souffre de {pst.get('trap_move', 'Piège')} ! (-{trap_dmg} PV)")
                pst['trap_turns'] -= 1
                if pst['trap_turns'] == 0:
                    pst.pop('trap_move', None)
                    self.add_to_log(f"{pkmn} est libéré du piège !")
                self._save_state()

            # ── Brûlure ───────────────────────────────────────────────────────
            if pkmn.status_condition == 'burn' and not has_magic_guard:
                burn_dmg = max(1, pkmn.max_hp // 8)
                pkmn.current_hp = max(0, pkmn.current_hp - burn_dmg)
                pkmn.save()
                self.add_to_log(f"{pkmn} souffre de brûlures ! (-{burn_dmg} PV)")

            # ── Poison / Poison sévère ─────────────────────────────────────────
            elif pkmn.status_condition == 'poison' and not has_magic_guard and not block_poison:
                if self.is_badly_poisoned(pkmn):
                    counter = self.get_toxic_counter(pkmn)
                    poison_dmg = max(1, pkmn.max_hp * counter // 16)
                    self.increment_toxic_counter(pkmn)
                else:
                    poison_dmg = max(1, pkmn.max_hp // 8)
                pkmn.current_hp = max(0, pkmn.current_hp - poison_dmg)
                pkmn.save()
                self.add_to_log(f"{pkmn} souffre du poison ! (-{poison_dmg} PV)")

            # ── Ingrain ───────────────────────────────────────────────────────
            if self.has_ingrain(pkmn):
                heal_ingrain = max(1, pkmn.max_hp // 16)
                pkmn.current_hp = min(pkmn.max_hp, pkmn.current_hp + heal_ingrain)
                pkmn.save()
                self.add_to_log(f"{pkmn} récupère {heal_ingrain} PV grâce à ses racines !")

            # ── Disable countdown ─────────────────────────────────────────────
            dis_turns = pst.get('disable_turns', 0)
            if dis_turns > 0:
                pst['disable_turns'] -= 1
                if pst['disable_turns'] == 0:
                    pst.pop('disabled_move_id', None)
                    self.add_to_log(f"{pkmn} peut à nouveau utiliser tous ses moves !")
                self._save_state()

            # ── Encore countdown ──────────────────────────────────────────────
            enc_turns = pst.get('encore_turns', 0)
            if enc_turns > 0:
                pst['encore_turns'] = enc_turns - 1
                if pst['encore_turns'] == 0:
                    pst.pop('encore_move', None)
                    self.add_to_log(f"{pkmn} n'est plus sous l'effet d'Encore !")
                self._save_state()

            # ── Taunt countdown ───────────────────────────────────────────────
            tnt_turns = pst.get('taunt_turns', 0)
            if tnt_turns > 0:
                pst['taunt_turns'] = tnt_turns - 1
                if pst['taunt_turns'] == 0:
                    self.add_to_log(f"{pkmn} n'est plus sous l'effet de Raillerie !")
                self._save_state()

            # ── Vœu (Wish) ────────────────────────────────────────────────────
            wish_turns = pst.get('wish_turns', 0)
            if wish_turns > 0:
                pst['wish_turns'] = wish_turns - 1
                if pst['wish_turns'] == 0:
                    wish_hp = pst.pop('wish_amount', 0)
                    if wish_hp > 0 and not pkmn.is_fainted():
                        healed = min(pkmn.max_hp - pkmn.current_hp, wish_hp)
                        if healed > 0:
                            pkmn.current_hp += healed
                            pkmn.save()
                            self.add_to_log(
                                f"Le Vœu se réalise ! {pkmn} récupère {healed} PV !"
                            )
                self._save_state()

            # ── Chant du Destin (Perish Song) ─────────────────────────────────
            perish = pst.get('perish_turns', 0)
            if perish > 0:
                pst['perish_turns'] = perish - 1
                self.add_to_log(
                    f"Chant du Destin : {pkmn} a encore {pst['perish_turns']} tour(s) !"
                )
                if pst['perish_turns'] == 0:
                    pkmn.current_hp = 0
                    pkmn.save()
                    self.add_to_log(f"{pkmn} tombe sous l'effet du Chant du Destin !")
                self._save_state()

            # ── Décranement screens ───────────────────────────────────────────
            side = 'player' if pkmn == self.player_pokemon else 'opponent'
            for screen in ('light_screen', 'reflect'):
                key = f'{side}_{screen}'
                if self._bstate().get(key, 0) > 0:
                    self._bstate()[key] -= 1
                    if self._bstate()[key] == 0:
                        self.add_to_log(
                            f"L'{'Écran Lumière' if screen == 'light_screen' else 'Mur'} "
                            f"se dissipe !"
                        )
            # ── Brume countdown ───────────────────────────────────────────────
            mist_key = f'{side}_mist'
            if self._bstate().get(mist_key, 0) > 0:
                self._bstate()[mist_key] -= 1
                if self._bstate()[mist_key] == 0:
                    self.add_to_log(f"La Brume se dissipe du côté de {pkmn} !")
            # ── Vent Arrière countdown ────────────────────────────────────────
            tw_key = f'{side}_tailwind'
            if self._bstate().get(tw_key, 0) > 0:
                self._bstate()[tw_key] -= 1
                if self._bstate()[tw_key] == 0:
                    self.add_to_log(f"Le Vent Arrière retombe du côté de {pkmn} !")
            self._save_state()

            # ── Future Sight ──────────────────────────────────────────────────
            fs_turns = pst.get('future_sight_turns', 0)
            if fs_turns > 0:
                pst['future_sight_turns'] -= 1
                if pst['future_sight_turns'] == 0:
                    fs_dmg = pst.pop('future_sight_damage', 0)
                    if fs_dmg > 0:
                        pkmn.current_hp = max(0, pkmn.current_hp - fs_dmg)
                        pkmn.save()
                        self.add_to_log(f"Prescience frappe {pkmn} pour {fs_dmg} dégâts !")
                self._save_state()

            # ── Réinitialiser was_hit_this_turn ───────────────────────────────
            pst.pop('was_hit_this_turn', None)
            self._save_state()

        # ── Held items — effets de fin de tour ───────────────────────────────
        for _pk in [self.player_pokemon, self.opponent_pokemon]:
            if not _pk or _pk.is_fainted():
                continue
            _opp  = self._get_opponent(_pk)
            _held = self._get_held_effect(_pk)
            if not _held:
                continue

            # Restes : +1/16 PV max chaque tour
            if _held == 'leftovers' and _pk.current_hp < _pk.max_hp:
                _h = min(max(1, _pk.max_hp // 16), _pk.max_hp - _pk.current_hp)
                _pk.current_hp += _h
                _pk.save(update_fields=['current_hp'])
                self.add_to_log(f"Les Restes de {_pk} lui restaurent {_h} PV !")

            # Baie Sitrus : +1/8 PV si ≤ 50 %
            elif _held == 'sitrus_berry' and _pk.current_hp <= _pk.max_hp // 2:
                _h = min(max(1, _pk.max_hp // 8), _pk.max_hp - _pk.current_hp)
                if _h > 0:
                    _pk.current_hp += _h
                    _pk.save(update_fields=['current_hp'])
                    self.add_to_log(f"La Baie Sitrus de {_pk} lui restaure {_h} PV !")
                    self._consume_held_item(_pk)

            # Baie Oran : +10 PV si ≤ 50 %
            elif _held == 'oran_berry' and _pk.current_hp <= _pk.max_hp // 2:
                _h = min(10, _pk.max_hp - _pk.current_hp)
                if _h > 0:
                    _pk.current_hp += _h
                    _pk.save(update_fields=['current_hp'])
                    self.add_to_log(f"La Baie Oran de {_pk} lui restaure {_h} PV !")
                    self._consume_held_item(_pk)

            # Baie Lum : soigne tout statut
            elif _held == 'lum_berry' and _pk.status_condition:
                _pk.cure_status()
                self.add_to_log(f"La Baie Lum de {_pk} guérit son altération de statut !")
                self._consume_held_item(_pk)

            # Baies mono-statut
            elif _held == 'cure_paralysis_berry' and _pk.status_condition == 'paralysis':
                _pk.cure_status()
                self.add_to_log(f"La Baie Pêche de {_pk} soigne sa paralysie !")
                self._consume_held_item(_pk)

            elif _held == 'cure_sleep_berry' and _pk.status_condition == 'sleep':
                _pk.cure_status()
                self.add_to_log(f"La Baie Mepo réveille {_pk} !")
                self._consume_held_item(_pk)

            elif _held == 'cure_poison_berry' and _pk.status_condition == 'poison':
                _pk.cure_status()
                self.add_to_log(f"La Baie Gribi soigne le poison de {_pk} !")
                self._consume_held_item(_pk)

            elif _held == 'cure_burn_berry' and _pk.status_condition == 'burn':
                _pk.cure_status()
                self.add_to_log(f"La Baie Rago soigne la brûlure de {_pk} !")
                self._consume_held_item(_pk)

            elif _held == 'cure_freeze_berry' and _pk.status_condition == 'freeze':
                _pk.cure_status()
                self.add_to_log(f"La Baie Glace dégèle {_pk} !")
                self._consume_held_item(_pk)

            # Casque Rocheux : 1/6 PV max en retour si touché ce tour
            elif _held == 'rocky_helmet':
                if self._pstate(_pk).get('was_hit_this_turn') and _opp and not _opp.is_fainted():
                    _d = max(1, _opp.max_hp // 6)
                    _opp.current_hp = max(0, _opp.current_hp - _d)
                    _opp.save(update_fields=['current_hp'])
                    self.add_to_log(
                        f"Le Casque Rocheux de {_pk} blesse {_opp} ! (-{_d} PV)"
                    )

        # ── Météo ─────────────────────────────────────────────────────────────
        weather_turns = self.get_weather_turns()
        if self.weather and weather_turns > 0:
            self._bstate()['weather_turns'] = weather_turns - 1
            remaining = self._bstate()['weather_turns']

            if self.weather == 'sandstorm':
                for pkmn in [self.player_pokemon, self.opponent_pokemon]:
                    if not pkmn or pkmn.is_fainted():
                        continue
                    types = {
                        getattr(pkmn.species.primary_type, 'name', ''),
                        getattr(pkmn.species.secondary_type, 'name', '') if pkmn.species.secondary_type else '',
                    }
                    if not types & {'rock', 'ground', 'steel'}:
                        sd_dmg = max(1, pkmn.max_hp // 16)
                        pkmn.current_hp = max(0, pkmn.current_hp - sd_dmg)
                        pkmn.save()
                        self.add_to_log(f"La tempête de sable blesse {pkmn} ! (-{sd_dmg} PV)")

            elif self.weather == 'hail':
                for pkmn in [self.player_pokemon, self.opponent_pokemon]:
                    if not pkmn or pkmn.is_fainted():
                        continue
                    typ = getattr(pkmn.species.primary_type, 'name', '')
                    typ2 = getattr(pkmn.species.secondary_type, 'name', '') if pkmn.species.secondary_type else ''
                    if 'ice' not in (typ, typ2):
                        hail_dmg = max(1, pkmn.max_hp // 16)
                        pkmn.current_hp = max(0, pkmn.current_hp - hail_dmg)
                        pkmn.save()
                        self.add_to_log(f"La grêle blesse {pkmn} ! (-{hail_dmg} PV)")

            if remaining == 0:
                weather_labels = {
                    'sunny': "Le soleil se couche.",
                    'rain': "La pluie s'arrête.",
                    'sandstorm': "La tempête de sable se dissipe.",
                    'hail': "La grêle cesse.",
                }
                self.add_to_log(weather_labels.get(self.weather, "La météo reprend son cours normal."))
                self.weather = None
            self._save_state()
            self.save()

        # ── Salle Bizarre countdown ────────────────────────────────────────────
        tr = self._bstate().get('trick_room_turns', 0)
        if tr > 0:
            self._bstate()['trick_room_turns'] = tr - 1
            if self._bstate()['trick_room_turns'] == 0:
                self.add_to_log("La Salle Bizarre retrouve son état normal !")
            self._save_state()

    # =========================================================================
    # ITEM
    # =========================================================================

    def use_item(self, item, target_pokemon):
        result = item.use_on_pokemon(target_pokemon)
        self.add_to_log(result)

    # =========================================================================
    # FUITE
    # =========================================================================

    def attempt_flee(self):
        if self.battle_type == 'wild':
            player_speed   = self.player_pokemon.get_effective_speed()
            opponent_speed = self.opponent_pokemon.get_effective_speed()
            odds = (player_speed * 32) / max(1, opponent_speed % 256) + 30 * self.current_turn
            if random.randint(0, 255) < odds:
                self.add_to_log("Fuite réussie !")
                self.is_active = False
                self.save()
                return True
            else:
                self.add_to_log("Échec dans la fuite !")
                return False
        else:
            self.add_to_log("On ne peut pas fuir un combat de dresseur !")
            return False

    # =========================================================================
    # XP / EV
    # =========================================================================

    def calculate_exp_reward(self, defeated_pokemon):
        """Calcule l'XP gagnée (formule Gen 5+)."""
        b    = defeated_pokemon.species.base_experience or 64
        Lf   = defeated_pokemon.level
        Lp   = self.player_pokemon.level
        t    = 1.5 if self.battle_type in ('trainer', 'gym', 'elite_four') else 1.0
        ratio        = (2 * Lf + 10) / (Lf + Lp + 10)
        level_factor = ratio ** 2.5
        exp = round((b * Lf / 5) * level_factor + 1) * t
        return max(1, int(exp))

    def grant_ev_gains(self, defeated_pokemon):
        """Accorde les EVs (Effort Values) au Pokémon vainqueur."""
        EV_YIELDS = {
            'Bulbasaur': [('ev_special_attack', 1)], 'Ivysaur': [('ev_special_attack', 1), ('ev_special_defense', 1)],
            'Venusaur': [('ev_special_attack', 2), ('ev_special_defense', 1)], 'Charmander': [('ev_speed', 1)],
            'Charmeleon': [('ev_speed', 1), ('ev_attack', 1)], 'Charizard': [('ev_speed', 3)],
            'Squirtle': [('ev_defense', 1)], 'Wartortle': [('ev_defense', 1), ('ev_special_defense', 1)],
            'Blastoise': [('ev_defense', 1), ('ev_special_defense', 2)], 'Caterpie': [('ev_hp', 1)],
            'Metapod': [('ev_defense', 1)], 'Butterfree': [('ev_special_attack', 2), ('ev_special_defense', 1)],
            'Weedle': [('ev_speed', 1)], 'Kakuna': [('ev_defense', 1)],
            'Beedrill': [('ev_attack', 2), ('ev_speed', 1)], 'Pidgey': [('ev_speed', 1)],
            'Pidgeotto': [('ev_speed', 1), ('ev_attack', 1)], 'Pidgeot': [('ev_speed', 3)],
            'Rattata': [('ev_speed', 1)], 'Raticate': [('ev_speed', 2)],
            'Spearow': [('ev_speed', 1)], 'Fearow': [('ev_speed', 2)],
            'Ekans': [('ev_attack', 1)], 'Arbok': [('ev_attack', 2)],
            'Pikachu': [('ev_speed', 2)], 'Raichu': [('ev_speed', 3)],
            'Sandshrew': [('ev_defense', 1)], 'Sandslash': [('ev_defense', 2)],
            'Nidoran♀': [('ev_hp', 1)], 'Nidorina': [('ev_hp', 2)], 'Nidoqueen': [('ev_hp', 3)],
            'Nidoran♂': [('ev_attack', 1)], 'Nidorino': [('ev_attack', 2)], 'Nidoking': [('ev_attack', 3)],
            'Clefairy': [('ev_hp', 2)], 'Clefable': [('ev_hp', 3)],
            'Vulpix': [('ev_special_attack', 1)], 'Ninetales': [('ev_special_attack', 2), ('ev_speed', 1)],
            'Jigglypuff': [('ev_hp', 2)], 'Wigglytuff': [('ev_hp', 3)],
            'Zubat': [('ev_speed', 1)], 'Golbat': [('ev_speed', 2)],
            'Oddish': [('ev_special_attack', 1)], 'Gloom': [('ev_special_attack', 1), ('ev_special_defense', 1)],
            'Vileplume': [('ev_special_attack', 2), ('ev_special_defense', 1)],
            'Paras': [('ev_attack', 1)], 'Parasect': [('ev_attack', 2), ('ev_defense', 1)],
            'Venonat': [('ev_special_defense', 1)], 'Venomoth': [('ev_special_attack', 2), ('ev_special_defense', 1)],
            'Diglett': [('ev_speed', 1)], 'Dugtrio': [('ev_speed', 2)],
            'Meowth': [('ev_speed', 1)], 'Persian': [('ev_speed', 2)],
            'Psyduck': [('ev_special_attack', 1)], 'Golduck': [('ev_special_attack', 2)],
            'Mankey': [('ev_attack', 1)], 'Primeape': [('ev_attack', 2)],
            'Growlithe': [('ev_attack', 1)], 'Arcanine': [('ev_attack', 2), ('ev_speed', 1)],
            'Poliwag': [('ev_speed', 1)], 'Poliwhirl': [('ev_speed', 2)],
            'Poliwrath': [('ev_defense', 1), ('ev_special_defense', 1)],
            'Abra': [('ev_special_attack', 1)], 'Kadabra': [('ev_special_attack', 2)],
            'Alakazam': [('ev_special_attack', 3)], 'Machop': [('ev_attack', 1)],
            'Machoke': [('ev_attack', 2)], 'Machamp': [('ev_attack', 3)],
            'Bellsprout': [('ev_attack', 1)], 'Weepinbell': [('ev_attack', 2)],
            'Victreebel': [('ev_attack', 3)], 'Tentacool': [('ev_special_defense', 1)],
            'Tentacruel': [('ev_special_defense', 2)], 'Geodude': [('ev_defense', 1)],
            'Graveler': [('ev_defense', 2)], 'Golem': [('ev_defense', 3)],
            'Ponyta': [('ev_speed', 1)], 'Rapidash': [('ev_speed', 2)],
            'Slowpoke': [('ev_hp', 1)], 'Slowbro': [('ev_defense', 1), ('ev_special_attack', 1)],
            'Magnemite': [('ev_special_attack', 1)], 'Magneton': [('ev_special_attack', 2)],
            'Doduo': [('ev_attack', 1)], 'Dodrio': [('ev_attack', 2)],
            'Seel': [('ev_special_defense', 1)], 'Dewgong': [('ev_special_defense', 2)],
            'Grimer': [('ev_hp', 1)], 'Muk': [('ev_hp', 2)],
            'Shellder': [('ev_defense', 1)], 'Cloyster': [('ev_defense', 2)],
            'Gastly': [('ev_special_attack', 1)], 'Haunter': [('ev_special_attack', 2)],
            'Gengar': [('ev_special_attack', 3)], 'Onix': [('ev_defense', 1)],
            'Drowzee': [('ev_special_defense', 1)], 'Hypno': [('ev_special_defense', 2)],
            'Krabby': [('ev_attack', 1)], 'Kingler': [('ev_attack', 2)],
            'Voltorb': [('ev_speed', 1)], 'Electrode': [('ev_speed', 2)],
            'Exeggcute': [('ev_special_attack', 1)], 'Exeggutor': [('ev_special_attack', 2)],
            'Cubone': [('ev_defense', 1)], 'Marowak': [('ev_defense', 2)],
            'Hitmonlee': [('ev_attack', 2)], 'Hitmonchan': [('ev_special_defense', 2)],
            'Lickitung': [('ev_hp', 1)], 'Koffing': [('ev_defense', 1)], 'Weezing': [('ev_defense', 2)],
            'Rhyhorn': [('ev_defense', 1)], 'Rhydon': [('ev_attack', 2)],
            'Chansey': [('ev_hp', 2)], 'Tangela': [('ev_defense', 1)], 'Kangaskhan': [('ev_hp', 2)],
            'Horsea': [('ev_special_attack', 1)], 'Seadra': [('ev_special_attack', 2)],
            'Goldeen': [('ev_attack', 1)], 'Seaking': [('ev_attack', 2)],
            'Staryu': [('ev_speed', 1)], 'Starmie': [('ev_speed', 2)],
            'Mr. Mime': [('ev_special_defense', 2)], 'Scyther': [('ev_attack', 1), ('ev_speed', 1)],
            'Jynx': [('ev_special_attack', 2)], 'Electabuzz': [('ev_special_attack', 2)],
            'Magmar': [('ev_special_attack', 2)], 'Pinsir': [('ev_attack', 2)],
            'Tauros': [('ev_attack', 1), ('ev_speed', 1)], 'Magikarp': [('ev_speed', 1)],
            'Gyarados': [('ev_attack', 2)], 'Lapras': [('ev_hp', 2)],
            'Ditto': [('ev_hp', 1)], 'Eevee': [('ev_hp', 1)], 'Vaporeon': [('ev_hp', 2)],
            'Jolteon': [('ev_speed', 2)], 'Flareon': [('ev_attack', 2)],
            'Porygon': [('ev_special_attack', 1)], 'Omanyte': [('ev_defense', 1)],
            'Omastar': [('ev_defense', 1), ('ev_special_attack', 1)], 'Kabuto': [('ev_defense', 1)],
            'Kabutops': [('ev_attack', 2)], 'Aerodactyl': [('ev_speed', 2)],
            'Snorlax': [('ev_hp', 2)], 'Articuno': [('ev_special_defense', 3)],
            'Zapdos': [('ev_special_attack', 3)], 'Moltres': [('ev_special_attack', 3)],
            'Dratini': [('ev_attack', 1)], 'Dragonair': [('ev_attack', 2)],
            'Dragonite': [('ev_attack', 3)], 'Mewtwo': [('ev_special_attack', 3)],
            'Mew': [('ev_hp', 3)],
        }

        EV_CAP_PER_STAT = 252
        EV_TOTAL_CAP    = 510

        winner       = self.player_pokemon
        species_name = defeated_pokemon.species.name
        yields       = EV_YIELDS.get(species_name, [('ev_hp', 1)])

        current_total = (
            winner.ev_hp + winner.ev_attack + winner.ev_defense +
            winner.ev_special_attack + winner.ev_special_defense + winner.ev_speed
        )

        for stat_field, amount in yields:
            if current_total >= EV_TOTAL_CAP:
                break
            current_val = getattr(winner, stat_field)
            gain = min(amount, EV_CAP_PER_STAT - current_val, EV_TOTAL_CAP - current_total)
            if gain > 0:
                setattr(winner, stat_field, current_val + gain)
                current_total += gain

        winner.save()

    # =========================================================================
    # IA ADVERSAIRE
    # =========================================================================

    def choose_enemy_move(self, attacker, defender):
        """Sélectionne intelligemment le move de l'ennemi via un système de scoring."""
        from .PlayablePokemon import PokemonMoveInstance

        move_instances = PokemonMoveInstance.objects.filter(
            pokemon=attacker, current_pp__gt=0
        ).select_related('move', 'move__type')

        # Filtrer les moves désactivés
        available_moves = [
            mi.move for mi in move_instances
            if not self.is_move_disabled(attacker, mi.move)
        ]

        if not available_moves:
            struggle = PokemonMove.objects.filter(name__iexact='Struggle').first()
            if struggle:
                return {'type': 'attack', 'move': struggle}
            return None

        best_move  = None
        best_score = -9999

        for move in available_moves:
            score = self._score_enemy_move(move, attacker, defender)
            if score > best_score:
                best_score = score
                best_move  = move

        return {'type': 'attack', 'move': best_move}

    def _score_enemy_move(self, move, attacker, defender):
        """Calcule un score de pertinence pour un move donné."""
        score = 0.0

        type_mult = self.get_type_effectiveness(move.type, defender)
        if type_mult >= 2.0:    score += 80
        elif type_mult > 1.0:   score += 40
        elif type_mult == 0:    score -= 200
        elif type_mult < 1.0:   score -= 30

        attacker_types = [attacker.species.primary_type, attacker.species.secondary_type]
        if move.type in attacker_types:
            score += 20

        if move.power and move.power > 0:
            score += move.power * 0.25

        accuracy = move.accuracy if move.accuracy else 100
        score *= (accuracy / 100.0)

        if move.power and move.power > 0:
            estimated = self._estimate_enemy_damage(move, attacker, defender)
            if estimated >= defender.current_hp:
                score += 200
            elif estimated >= defender.current_hp * 0.75:
                score += 50

        if not move.power or move.power == 0:
            if move.inflicts_status:
                score += 30 if not defender.status_condition else -40
            elif move.stat_changes:
                hp_ratio = attacker.current_hp / max(attacker.max_hp, 1)
                score += 20 if hp_ratio > 0.6 else -10
            elif move.effect in ('leech_seed',) and not self.has_leech_seed(defender):
                score += 40
            elif move.effect in ('heal_half', 'heal_sleep'):
                hp_ratio = attacker.current_hp / max(attacker.max_hp, 1)
                if hp_ratio < 0.3:   score += 120
                elif hp_ratio < 0.5: score += 50
                else:                score -= 30
            else:
                score -= 20

        if hasattr(move, 'priority') and move.priority and move.priority > 0:
            if defender.current_hp <= attacker.current_hp * 0.4:
                score += 25

        score += random.uniform(0, 8)
        return score

    def _estimate_enemy_damage(self, move, attacker, defender):
        if not move.power or move.power == 0:
            return 0
        if move.category == 'physical':
            atk_stat = attacker.get_effective_attack()
            def_stat = defender.get_effective_defense()
        else:
            atk_stat = attacker.get_effective_special_attack()
            def_stat = defender.get_effective_special_defense()
        if def_stat == 0:
            def_stat = 1
        base = ((2 * attacker.level / 5 + 2) * move.power * atk_stat / def_stat) / 50 + 2
        mult = self.get_type_effectiveness(move.type, defender)
        attacker_types = [attacker.species.primary_type, attacker.species.secondary_type]
        if move.type in attacker_types:
            base *= 1.5
        return int(base * mult * 0.925)

    # =========================================================================
    # FIN DE COMBAT
    # =========================================================================

    def end_battle(self, winner):
        self.winner     = winner
        self.is_active  = False
        from django.utils import timezone
        self.ended_at   = timezone.now()
        self.save()