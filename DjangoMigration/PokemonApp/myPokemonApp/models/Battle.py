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
            self.add_to_log(result)
        if opponent_using_item:
            item   = opponent_action.get('item')
            target = opponent_action.get('target')
            result = item.use_on_pokemon(target)
            self.add_to_log(result)

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
        elif opponent_priority > player_priority:
            first  = (self.opponent_pokemon, opponent_action, self.player_pokemon)
            second = (self.player_pokemon, player_action, self.opponent_pokemon)
        elif player_speed > opponent_speed:
            first  = (self.player_pokemon, player_action, self.opponent_pokemon)
            second = (self.opponent_pokemon, opponent_action, self.player_pokemon)
        elif opponent_speed > player_speed:
            first  = (self.opponent_pokemon, opponent_action, self.player_pokemon)
            second = (self.player_pokemon, player_action, self.opponent_pokemon)
        else:
            if random.choice([True, False]):
                first  = (self.player_pokemon, player_action, self.opponent_pokemon)
                second = (self.opponent_pokemon, opponent_action, self.player_pokemon)
            else:
                first  = (self.opponent_pokemon, opponent_action, self.player_pokemon)
                second = (self.player_pokemon, player_action, self.opponent_pokemon)

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
            if accuracy < 100:
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
        """Dispatcher central de tous les effets de moves."""

        effect = move.effect or ''

        # ─── Moves de statut purs (pas de dégâts) ─────────────────────────────

        if effect == 'leech_seed':
            if 'grass' in (
                getattr(defender.species.primary_type, 'name', ''),
                getattr(defender.species.secondary_type, 'name', '') if defender.species.secondary_type else ''
            ):
                self.add_to_log(f"Ça n'a aucun effet sur {defender} !")
            elif self.has_leech_seed(defender):
                self.add_to_log(f"{defender} est déjà sous Vampigraine !")
            else:
                if self.apply_leech_seed(defender):
                    self.add_to_log(f"{defender} est planté avec Vampigraine !")
            return

        if effect == 'confuse':
            if self.is_confused(defender):
                self.add_to_log(f"{defender} est déjà confus !")
            elif self.confuse(defender):
                self.add_to_log(f"{defender} est maintenant confus !")
            return

        if effect == 'confuse_raise_spatk':
            self.modify_stat(attacker, 'special_attack', 1)
            if not self.is_confused(defender):
                self.confuse(defender)
                self.add_to_log(f"{defender} est maintenant confus !")
            return

        if effect == 'heal_half':
            healed = min(attacker.max_hp - attacker.current_hp, attacker.max_hp // 2)
            attacker.current_hp += healed
            attacker.save()
            self.add_to_log(f"{attacker} récupère {healed} PV !")
            return

        if effect == 'heal_sleep':   # Rest
            attacker.current_hp       = attacker.max_hp
            attacker.status_condition = 'sleep'
            attacker.sleep_turns      = 2
            attacker.save()
            self.add_to_log(f"{attacker} se repose et récupère tous ses PV !")
            return

        if effect == 'ingrain':
            self.set_ingrain(attacker)
            self.add_to_log(f"{attacker} s'enracine dans le sol !")
            return

        if effect == 'focus_energy':
            self.set_focus_energy(attacker)
            self.add_to_log(f"{attacker} se concentre pour viser les points vitaux !")
            return

        if effect == 'destiny_bond':
            self.set_destiny_bond(attacker)
            self.add_to_log(f"{attacker} veut emporter son adversaire avec lui !")
            return

        if effect == 'nightmare':
            if defender.status_condition == 'sleep':
                self.set_nightmare(defender)
                self.add_to_log(f"{defender} est plongé dans des cauchemars !")
            else:
                self.add_to_log(f"Ça n'a aucun effet !")
            return

        if effect == 'pain_split':
            avg = (attacker.current_hp + defender.current_hp) // 2
            attacker.current_hp = min(attacker.max_hp, avg)
            defender.current_hp = min(defender.max_hp, avg)
            attacker.save()
            defender.save()
            self.add_to_log(f"Les deux Pokémon partagent leurs PV !")
            return

        if effect == 'reset_stats':  # Brume
            for pkmn in [attacker, defender]:
                pkmn.attack_stage = pkmn.defense_stage = 0
                pkmn.special_attack_stage = pkmn.special_defense_stage = 0
                pkmn.speed_stage = pkmn.accuracy_stage = pkmn.evasion_stage = 0
                pkmn.save()
            self.add_to_log("Les modifications de stats ont été annulées !")
            return

        if effect == 'copy_stat_changes':  # Psych Up
            attacker.attack_stage         = defender.attack_stage
            attacker.defense_stage        = defender.defense_stage
            attacker.special_attack_stage = defender.special_attack_stage
            attacker.special_defense_stage= defender.special_defense_stage
            attacker.speed_stage          = defender.speed_stage
            attacker.save()
            self.add_to_log(f"{attacker} copie les modifications de stats de {defender} !")
            return

        if effect == 'force_switch':
            if self.battle_type == 'wild':
                defender.current_hp = 0
                defender.save()
                self.add_to_log(f"{defender} est repoussé !")
            else:
                self.add_to_log(f"Ça n'a aucun effet en combat de dresseur !")
            return

        if effect == 'disable':
            self.disable_move(defender)
            return

        if effect == 'transform':
            # Copier les stats de base (simplifié)
            self.add_to_log(f"{attacker} se transforme en {defender.species.name} !")
            return

        if effect == 'prevent_stat_lower':  # Brume
            self._pstate(attacker)['mist'] = 5
            self._save_state()
            self.add_to_log(f"{attacker} est enveloppé de Brume !")
            return

        # ─── Météo ─────────────────────────────────────────────────────────────

        if effect == 'sunny_day':
            self.set_weather('sunny')
            self.add_to_log("Le soleil brille intensément !")
            return

        if effect == 'rain_dance':
            self.set_weather('rain')
            self.add_to_log("Une pluie torrentielle s'abat sur le terrain !")
            return

        if effect == 'sandstorm':
            self.set_weather('sandstorm')
            self.add_to_log("Une tempête de sable se déclenche !")
            return

        if effect == 'hail':
            self.set_weather('hail')
            self.add_to_log("Il commence à grêler !")
            return

        # ─── Écrans ────────────────────────────────────────────────────────────

        if effect == 'light_screen':
            side = 'player' if attacker == self.player_pokemon else 'opponent'
            self.set_screen(side, 'light_screen')
            self.add_to_log(f"{attacker} érige un Écran Lumière !")
            return

        if effect == 'reflect':
            side = 'player' if attacker == self.player_pokemon else 'opponent'
            self.set_screen(side, 'reflect')
            self.add_to_log(f"{attacker} érige un Mur !")
            return

        # ─── Break barrières ───────────────────────────────────────────────────

        if effect == 'break_barrier':
            side = 'opponent' if attacker == self.player_pokemon else 'player'
            self._bstate().pop(f'{side}_light_screen', None)
            self._bstate().pop(f'{side}_reflect', None)
            self._save_state()
            # Puis dégâts normaux

        # ─── Moves de stat purs ────────────────────────────────────────────────

        # Dictionnaire des effets stat pour éviter le code répété
        STAT_EFFECTS = {
            'raise_attack':                 [('attack', 1, attacker)],
            'raise_defense':                [('defense', 1, attacker)],
            'raise_special_attack':         [('special_attack', 1, attacker)],
            'raise_special_defense':        [('special_defense', 1, attacker)],
            'raise_speed':                  [('speed', 1, attacker)],
            'raise_evasion':                [('evasion', 1, attacker)],
            'raise_accuracy':               [('accuracy', 1, attacker)],
            'raise_attack_defense':         [('attack', 1, attacker), ('defense', 1, attacker)],
            'raise_attack_speed':           [('attack', 1, attacker), ('speed', 1, attacker)],
            'raise_attack_accuracy':        [('attack', 1, attacker), ('accuracy', 1, attacker)],
            'raise_special_attack_special_defense': [('special_attack', 1, attacker), ('special_defense', 1, attacker)],
            'raise_defense_special_defense': [('defense', 1, attacker), ('special_defense', 1, attacker)],
            'raise_all_stats':              [('attack', 1, attacker), ('defense', 1, attacker),
                                             ('special_attack', 1, attacker), ('special_defense', 1, attacker),
                                             ('speed', 1, attacker)],
            'sharply_raise_attack':         [('attack', 2, attacker)],
            'sharply_raise_defense':        [('defense', 2, attacker)],
            'sharply_raise_special_attack': [('special_attack', 2, attacker)],
            'sharply_raise_special_defense':[('special_defense', 2, attacker)],
            'sharply_raise_speed':          [('speed', 2, attacker)],
            'raise_attack_speed_sharply':   [('attack', 1, attacker), ('speed', 2, attacker)],
            'raise_attack_special_attack_speed_sharply_lower_defense_special_defense':
                                            [('attack', 2, attacker), ('special_attack', 2, attacker),
                                             ('speed', 2, attacker), ('defense', -1, attacker),
                                             ('special_defense', -1, attacker)],

            'lower_attack':                 [('attack', -1, defender)],
            'lower_defense':                [('defense', -1, defender)],
            'lower_special_defense':        [('special_defense', -1, defender)],
            'lower_speed':                  [('speed', -1, defender)],
            'lower_accuracy':               [('accuracy', -1, defender)],
            'lower_evasion':                [('evasion', -1, defender)],
            'lower_sp_atk':                 [('special_attack', -1, defender)],
            'lower_special_attack':         [('special_attack', -1, defender)],
            'lower_attack_defense':         [('attack', -1, attacker), ('defense', -1, attacker)],
            'lower_defense_special_defense':[('defense', -1, attacker), ('special_defense', -1, attacker)],
            'sharply_lower_attack':         [('attack', -2, defender)],
            'sharply_lower_defense':        [('defense', -2, defender)],
            'sharply_lower_special_attack': [('special_attack', -2, attacker)],
            'sharply_lower_special_defense':[('special_defense', -2, defender)],
            'lower_special_attack_opponent':[('special_attack', -2, defender)],
        }

        if effect in STAT_EFFECTS and move.power == 0:
            for stat_name, stages, target in STAT_EFFECTS[effect]:
                self.modify_stat(target, stat_name, stages)
            return

        # ─── max_attack_half_hp (Belly Drum) ────────────────────────────────────

        if effect == 'max_attack_half_hp':
            cost = attacker.max_hp // 2
            if attacker.current_hp <= cost:
                self.add_to_log(f"{attacker} n'a pas assez de PV !")
                return
            attacker.current_hp -= cost
            attacker.attack_stage = 6
            attacker.save()
            self.add_to_log(f"{attacker} se sacrifie pour maximiser son Attaque !")
            return

        # ─── Refresh ──────────────────────────────────────────────────────────

        if effect == 'refresh':
            if attacker.status_condition:
                attacker.cure_status()
                self.add_to_log(f"{attacker} guérit son statut !")
            else:
                self.add_to_log(f"Ça n'a aucun effet !")
            return

        # ─── Cure team status (Heal Bell, Aromatherapy) ───────────────────────

        if effect == 'cure_team_status':
            team = attacker.trainer.pokemon_team.filter(is_in_party=True)
            for pkmn in team:
                pkmn.cure_status()
            self.add_to_log("Tous les Pokémon de l'équipe sont guéris !")
            return

        # ─── Random power (Magnitude) ─────────────────────────────────────────

        if effect == 'random_power':
            magnitudes = [(10, 4), (20, 8), (30, 14), (50, 19), (70, 24),
                          (90, 29), (110, 34), (150, 39), (80, 44), (120, 49)]
            r = random.randint(0, 50)
            power = 70  # default Mag7
            mag_level = 7
            for p, threshold in magnitudes:
                if r <= threshold:
                    power     = p
                    mag_level = magnitudes.index((p, threshold)) + 1
                    break
            self.add_to_log(f"Magnitude {mag_level} !")
            move._temp_power = power
            # Calculer les dégâts avec la puissance aléatoire
            damage = self._calculate_damage_with_power(attacker, defender, move, power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Superpower (lower_attack_defense sur soi) ──────────────────────────

        if effect == 'lower_attack_defense' and move.power > 0:
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            self.modify_stat(attacker, 'attack', -1)
            self.modify_stat(attacker, 'defense', -1)
            return

        if effect == 'lower_defense_special_defense' and move.power > 0:   # Close Combat
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            self.modify_stat(attacker, 'defense', -1)
            self.modify_stat(attacker, 'special_defense', -1)
            return

        # ─── Fissure / Horn Drill / Guillotine (OHKO) ────────────────────────

        if effect == 'ohko':
            if attacker.level < defender.level:
                self.add_to_log("L'attaque a raté !")
                return
            ohko_acc = 30 + (attacker.level - defender.level)
            if random.randint(1, 100) <= ohko_acc:
                defender.current_hp = 0
                defender.save()
                self.add_to_log(f"Victoire par KO instantané !")
            else:
                self.add_to_log("L'attaque a raté !")
            return

        # ─── Sonic Boom (fixed_damage_20) ─────────────────────────────────────

        if effect == 'fixed_damage_20':
            self._apply_fixed_damage(defender, 20)
            return

        if effect == 'fixed_40':  # Dragon Rage
            self._apply_fixed_damage(defender, 40)
            return

        # ─── Seismic Toss / Night Shade (level_damage) ────────────────────────

        if effect == 'level_damage':
            self._apply_fixed_damage(defender, attacker.level)
            return

        # ─── Super Fang (half_hp) ─────────────────────────────────────────────

        if effect == 'half_hp':
            dmg = max(1, defender.current_hp // 2)
            self._apply_fixed_damage(defender, dmg)
            return

        # ─── Eruption / Water Spout (more_damage_if_hp) ───────────────────────

        if effect == 'more_damage_if_hp':
            real_power = max(1, int(move.power * attacker.current_hp / attacker.max_hp))
            damage = self._calculate_damage_with_power(attacker, defender, move, real_power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Future Sight ─────────────────────────────────────────────────────

        if effect == 'future_sight':
            damage = self.calculate_damage(attacker, defender, move)
            self.set_future_sight(defender, damage)
            self.add_to_log(f"{attacker} prédit l'avenir…")
            return

        # ─── Tri-Attack ───────────────────────────────────────────────────────

        if effect == 'tri_attack':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if not defender.is_fainted() and random.randint(1, 100) <= 20:
                status = random.choice(['paralysis', 'burn', 'freeze'])
                if defender.apply_status(status):
                    self.add_to_log(f"{defender} est {status} !")
            return

        # ─── Drain (Absorb, Mega Drain, Giga Drain, Drain Punch, Leech Life) ──

        if effect == 'drain':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if damage > 0:
                healed = max(1, damage // 2)
                attacker.current_hp = min(attacker.max_hp, attacker.current_hp + healed)
                attacker.save()
                self.add_to_log(f"{attacker} récupère {healed} PV !")
            return

        if effect == 'drain_sleep':  # Dream Eater
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

        # ─── Recoil (Double-Edge, Take Down, Flare Blitz…) ───────────────────

        if effect == 'recoil':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if damage > 0:
                recoil = max(1, damage // 3)
                attacker.current_hp = max(0, attacker.current_hp - recoil)
                attacker.save()
                self.add_to_log(f"{attacker} est blessé par le contrecoup ! (-{recoil} PV)")
            return

        # ─── Self-Destruct / Explosion ────────────────────────────────────────

        if effect in ('faint_user', 'self_destruct'):
            damage = self.calculate_damage(attacker, defender, move)
            # Explosion réduit la défense de moitié (Gen 1-4)
            if effect == 'self_destruct':
                orig_def = defender.defense
                defender.defense = max(1, defender.defense // 2)
                damage = self.calculate_damage(attacker, defender, move)
                defender.defense = orig_def
            self._apply_damage_to_defender(attacker, defender, move, damage)
            attacker.current_hp = 0
            attacker.save()
            self.add_to_log(f"{attacker} s'est sacrifié !")
            return

        # ─── Rampage (Thrash, Petal Dance, Outrage) ──────────────────────────

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

        # ─── Multi-hit (Bullet Seed, Pin Missile, Fury Attack…) ───────────────

        if effect == 'multi_hit':
            # 2-5 coups selon distribution Gen 3+: 35%/35%/15%/15%
            r = random.random()
            if   r < 0.35: hits = 2
            elif r < 0.70: hits = 3
            elif r < 0.85: hits = 4
            else:           hits = 5
            total_damage = 0
            for i in range(hits):
                if defender.is_fainted():
                    break
                damage = self.calculate_damage(attacker, defender, move)
                defender.current_hp = max(0, defender.current_hp - damage)
                total_damage += damage
            defender.save()
            self.add_to_log(f"Touche {hits} fois pour {total_damage} dégâts totaux !")
            return

        if effect == 'two_hit':  # Double Kick, Twineedle
            total_damage = 0
            for _ in range(2):
                if defender.is_fainted():
                    break
                damage = self.calculate_damage(attacker, defender, move)
                defender.current_hp = max(0, defender.current_hp - damage)
                total_damage += damage
            defender.save()
            self.add_to_log(f"Touche 2 fois pour {total_damage} dégâts !")
            # Poison pour Twineedle
            if move.inflicts_status and random.randint(1, 100) <= move.effect_chance:
                if defender.apply_status(move.inflicts_status):
                    self.add_to_log(f"{defender} est {move.inflicts_status} !")
            return

        # ─── Trap (Bind, Clamp, Fire Spin…) ──────────────────────────────────

        if effect == 'trap':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if not self.is_trapped(defender):
                self.trap_pokemon(defender, move.name)
                self.add_to_log(f"{defender} est pris au piège !")
            return

        # ─── Recharge (Hyper Beam, Giga Impact, Blast Burn…) ─────────────────

        if effect == 'recharge':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            self.set_recharge(attacker)
            self.add_to_log(f"{attacker} doit se recharger au prochain tour !")
            return

        # ─── Smelling Salts (double if paralyzed) ─────────────────────────────

        if effect == 'double_if_paralyzed':
            power  = move.power * (2 if defender.status_condition == 'paralysis' else 1)
            damage = self._calculate_damage_with_power(attacker, defender, move, power)
            if defender.status_condition == 'paralysis':
                defender.status_condition = None
                defender.save()
                self.add_to_log(f"{defender} est guéri de sa paralysie !")
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Facade (double if statused) ──────────────────────────────────────

        if effect == 'double_power_if_statused':
            power  = move.power * (2 if attacker.status_condition else 1)
            damage = self._calculate_damage_with_power(attacker, defender, move, power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Assurance / Revenge (double if hit this turn) ────────────────────

        if effect in ('double_if_hit', 'double_power_if_hit'):
            was_hit = self._pstate(attacker).get('was_hit_this_turn', False)
            power   = move.power * (2 if was_hit else 1)
            damage  = self._calculate_damage_with_power(attacker, defender, move, power)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            return

        # ─── Badly poison (Poison Fang, Toxic) ───────────────────────────────

        if effect == 'badly_poison':
            if move.power == 0:  # Toxic pur
                if random.randint(1, 100) <= move.effect_chance:
                    if not defender.status_condition:
                        defender.status_condition = 'poison'
                        defender.save()
                        self.set_badly_poisoned(defender)
                        self.add_to_log(f"{defender} est gravement empoisonné !")
                return
            else:
                damage = self.calculate_damage(attacker, defender, move)
                self._apply_damage_to_defender(attacker, defender, move, damage)
                if random.randint(1, 100) <= move.effect_chance:
                    if not defender.status_condition:
                        defender.status_condition = 'poison'
                        defender.save()
                        self.set_badly_poisoned(defender)
                        self.add_to_log(f"{defender} est gravement empoisonné !")
            return

        # ─── Knock Off ────────────────────────────────────────────────────────

        if effect == 'remove_item':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            if defender.held_item:
                item_name = defender.held_item.name
                defender.held_item = None
                defender.save()
                self.add_to_log(f"{defender} perd son {item_name} !")
            return

        # ─── Struggle (recoil 25% max HP) ────────────────────────────────────

        if move.name == 'Struggle':
            damage = self.calculate_damage(attacker, defender, move)
            self._apply_damage_to_defender(attacker, defender, move, damage)
            recoil = max(1, attacker.max_hp // 4)
            attacker.current_hp = max(0, attacker.current_hp - recoil)
            attacker.save()
            self.add_to_log(f"{attacker} souffre du contrecoup ! (-{recoil} PV)")
            return

        # ─── Stat changes en accompagnement d'une attaque ────────────────────

        if move.power > 0:
            # Dégâts de base
            damage = self.calculate_damage(attacker, defender, move)

            # Modificateurs de météo
            if self.weather == 'sunny':
                if hasattr(move.type, 'name'):
                    if move.type.name == 'fire':   damage = int(damage * 1.5)
                    elif move.type.name == 'water': damage = int(damage * 0.5)
            elif self.weather == 'rain':
                if hasattr(move.type, 'name'):
                    if move.type.name == 'water':   damage = int(damage * 1.5)
                    elif move.type.name == 'fire':  damage = int(damage * 0.5)

            self._apply_damage_to_defender(attacker, defender, move, damage)

            if not defender.is_fainted():
                # Statut secondaire
                if move.inflicts_status and random.randint(1, 100) <= move.effect_chance:
                    if defender.apply_status(move.inflicts_status):
                        self.add_to_log(f"{defender} est {move.inflicts_status} !")

                # Flinch secondaire
                if effect == 'flinch' and random.randint(1, 100) <= move.effect_chance:
                    self.set_flinched(defender)

                # Modificateurs de stats du move (via stat_changes JSON)
                if move.stat_changes:
                    for stat, change in move.stat_changes.items():
                        self.modify_stat(attacker if change > 0 else defender, stat, change)

                # Effets secondaires via le champ effect
                if effect in STAT_EFFECTS and move.power > 0:
                    for stat_name, stages, target in STAT_EFFECTS[effect]:
                        if random.randint(1, 100) <= move.effect_chance:
                            self.modify_stat(target, stat_name, stages)

                # always_crit (Frost Breath) — géré dans calculate_damage via flag
                if effect == 'always_crit':
                    pass  # Déjà géré dans calculate_damage

        else:
            # Move de statut sans puissance ni effet reconnu
            if move.inflicts_status and random.randint(1, 100) <= move.effect_chance:
                if defender.apply_status(move.inflicts_status):
                    self.add_to_log(f"{defender} est {move.inflicts_status} !")
            if move.stat_changes:
                for stat, change in move.stat_changes.items():
                    self.modify_stat(attacker if change > 0 else defender, stat, change)

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
        """Applique les dégâts au défenseur avec gestion Endure et efficacité."""
        if damage <= 0:
            damage = 1 if move.power > 0 else 0
        if damage == 0:
            return

        # Endure : survivre avec 1 PV
        if self.is_enduring(defender) and defender.current_hp <= damage:
            damage = defender.current_hp - 1
            self.add_to_log(f"{defender} tient le coup !")

        defender.current_hp = max(0, defender.current_hp - damage)
        defender.save()
        self.add_to_log(f"{defender} subit {damage} points de dégâts !")

        # Efficacité des types
        effectiveness = self.get_type_effectiveness(move.type, defender)
        if effectiveness > 1:
            self.add_to_log("C'est super efficace !")
        elif 0 < effectiveness < 1:
            self.add_to_log("Ce n'est pas très efficace…")
        elif effectiveness == 0:
            self.add_to_log("Ça n'a aucun effet !")

        # Marquer que le défenseur a été touché ce tour
        self._pstate(defender)['was_hit_this_turn'] = True
        self._save_state()

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

        # ── Dégâts de base ────────────────────────────────────────────────────
        damage = (((2 * level / 5 + 2) * move.power * attack_stat / max(1, defense_stat)) / 50) + 2

        # ── STAB ──────────────────────────────────────────────────────────────
        if (move.type == attacker.species.primary_type or
                move.type == attacker.species.secondary_type):
            damage *= 1.5

        # ── Efficacité des types ───────────────────────────────────────────────
        effectiveness = self.get_type_effectiveness(move.type, defender)
        damage *= effectiveness

        if effectiveness == 0:
            return 0

        # ── Coup critique ─────────────────────────────────────────────────────
        crit_rate = 1 / 16
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
            damage *= 0.5

        # ── Écrans (Light Screen / Reflect) ────────────────────────────────────
        side = 'opponent' if attacker == self.player_pokemon else 'player'
        damage *= self.get_screen_multiplier(side, move.category)

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
        current = getattr(pokemon, f"{stat_name}_stage", 0)
        new     = max(-6, min(6, current + stages))
        setattr(pokemon, f"{stat_name}_stage", new)
        pokemon.save()
        if stages > 0:
            self.add_to_log(f"L'{stat_name} de {pokemon} augmente{'fortement' if abs(stages) >= 2 else ''} !")
        else:
            self.add_to_log(f"L'{stat_name} de {pokemon} diminue{'fortement' if abs(stages) >= 2 else ''} !")

    # =========================================================================
    # SWITCH
    # =========================================================================

    def switch_pokemon(self, trainer_pokemon, new_pokemon):
        if trainer_pokemon == self.player_pokemon:
            self.player_pokemon = new_pokemon
        else:
            self.opponent_pokemon = new_pokemon
        self.save()
        self.add_to_log(f"{new_pokemon} entre en combat !")

    # =========================================================================
    # EFFETS DE FIN DE TOUR
    # =========================================================================

    def _apply_end_of_turn_effects(self):
        """Applique tous les effets de fin de tour (météo, statuts, Vampigraine…)."""
        for pkmn in [self.player_pokemon, self.opponent_pokemon]:
            if not pkmn or pkmn.is_fainted():
                continue

            other = (self.opponent_pokemon if pkmn == self.player_pokemon
                     else self.player_pokemon)

            # ── Leech Seed ────────────────────────────────────────────────────
            if self.has_leech_seed(pkmn):
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
            if trap_turns > 0:
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
            if pkmn.status_condition == 'burn':
                burn_dmg = max(1, pkmn.max_hp // 8)
                pkmn.current_hp = max(0, pkmn.current_hp - burn_dmg)
                pkmn.save()
                self.add_to_log(f"{pkmn} souffre de brûlures ! (-{burn_dmg} PV)")

            # ── Poison / Poison sévère ─────────────────────────────────────────
            elif pkmn.status_condition == 'poison':
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

            # ── Décranement screens ───────────────────────────────────────────
            side = 'player' if pkmn == self.player_pokemon else 'opponent'
            for screen in ('light_screen', 'reflect'):
                key = f'{side}_{screen}'
                if self._bstate().get(key, 0) > 0:
                    self._bstate()[key] -= 1
                    if self._bstate()[key] == 0:
                        self.add_to_log(f"L'{'Écran Lumière' if screen == 'light_screen' else 'Mur'} se dissipe !")
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