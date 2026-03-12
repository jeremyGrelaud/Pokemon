#!/usr/bin/python3
"""! @brief Ability.py — Modèle Talent Pokémon.

Chaque Ability est une entrée en base avec :
  - name          : identifiant unique ("Blaze", "Intimidate", …)
  - description   : texte affiché dans l'UI
  - effect_tag    : clé machine utilisée par Battle.py pour résoudre les effets
  - trigger       : moment où le talent s'active

Triggers disponibles :
  - on_switch_in      : à l'entrée en combat (Intimidate, Drizzle, …)
  - on_switch_out     : au retrait du combat (Regenerator, Natural Cure, …)
  - on_damage_taken   : quand le Pokémon reçoit des dégâts (Sturdy, Marvel Scale, …)
  - on_attack         : quand le Pokémon attaque (Technician, Sheer Force, …)
  - on_status         : quand un statut est infligé/subi (Immunity, Insomnia, …)
  - modify_stat       : modifie passivement une stat (Guts, Hustle, Swift Swim, …)
  - end_of_turn       : fin de tour (Speed Boost, Rain Dish, …)
  - passive           : effet permanent sans trigger précis
  - on_capture        : modifie la mécanique de capture (Illuminate, …)

Retours standardisés :
  Chaque hook retourne None (pas d'effet) ou un dict avec les clés :
    - 'block'                    : bool  — annule les dégâts / le statut
    - 'message'                  : str   — texte affiché dans le log de combat
    - 'heal'                     : int   — HP récupérés
    - 'damage'                   : int   — dégâts subis (fin de tour)
    - 'extra_damage'             : int   — dégâts supplémentaires appliqués
    - 'damage_cap'               : int   — plafond de dégâts (Sturdy)
    - 'damage_to_attacker'       : int   — dégâts infligés à l'attaquant (Rough Skin)
    - 'power_multiplier'         : float — multiplie la puissance de l'attaque
    - 'accuracy_multiplier'      : float — multiplie la précision de l'attaque
    - 'defense_multiplier'       : float — multiplie la Défense effective
    - 'stab_override'            : float — remplace le multiplicateur STAB (Adaptability)
    - 'raise_*'                  : int   — booste un palier de stat du porteur
    - 'lower_opponent_*'         : int   — baisse un palier de stat de l'adversaire
    - 'set_weather'              : str   — déclenche une météo
    - 'weather_turns'            : int   — durée de la météo
    - 'boost_fire'               : bool  — active le bonus interne Flash Fire
    - 'block_poison_damage'      : bool  — empêche les dégâts de poison (Poison Heal)
    - 'prevent_status'           : bool  — bloque l'infliction d'un statut
    - 'clear_status'             : bool  — guérit le statut du porteur
    - 'transmit_status_to_opponent': str — status transmis à l'adversaire (Synchronize)
    - 'inflict_status_on_attacker' : str — status infligé à l'attaquant (Static…)
    - 'confuse_attacker'         : bool  — confusionne l'attaquant (Cute Charm)
    - 'invert_drain'             : bool  — drain → dégâts (Liquid Ooze)
    - 'recoil_block'             : bool  — annule les dégâts de recul (Rock Head)
    - 'crit_block'               : bool  — immunité aux coups critiques (Shell Armor)
    - 'stat_drop_block'          : bool  — bloque toute baisse de stats (Clear Body)
    - 'ignore_opponent_ability'  : bool  — ignore le talent adverse (Mold Breaker)
    - 'copy_ability_from_opponent': bool — Trace
    - 'suppress_secondary_effect': bool  — Sheer Force (supprime effets secondaires)
    - 'double_effect_chance'     : bool  — Serene Grace
    - 'rate_multiplier'          : float — modificateur taux de capture
"""

from django.db import models
import random


TRIGGER_CHOICES = [
    ('on_switch_in',    "À l'entrée en combat"),
    ('on_switch_out',   'Au retrait du combat'),
    ('on_damage_taken', 'À la réception de dégâts'),
    ('on_attack',       "Lors d'une attaque"),
    ('on_status',       "Lors d'un changement de statut"),
    ('modify_stat',     'Modificateur de stats'),
    ('end_of_turn',     'Fin de tour'),
    ('passive',         'Passif permanent'),
    ('on_capture',      "Lors d'une capture"),
]

# Moves de poing pour Iron Fist
PUNCHING_MOVES = frozenset({
    'Comet Punch', 'Dizzy Punch', 'Fire Punch', 'Ice Punch',
    'Thunder Punch', 'Mega Punch', 'Mach Punch', 'Bullet Punch',
    'Shadow Punch', 'Drain Punch', 'Sky Uppercut', 'Hammer Arm',
    'Focus Punch', 'Sucker Punch',
})

# Moves sonores (bloqués par Soundproof)
SOUND_MOVES = frozenset({
    'Growl', 'Roar', 'Sing', 'Supersonic', 'Screech', 'Snore',
    'Uproar', 'Metal Sound', 'Grass Whistle', 'Hyper Voice',
    'Bug Buzz', 'Chatter', 'Snarl', 'Boomburst', 'Disarming Voice',
    'Noble Roar', 'Echoed Voice', 'Round',
})

# Moves avec recul pour Reckless
RECOIL_EFFECTS = frozenset({'recoil', 'recoil_25', 'recoil_33', 'recoil_half'})


class Ability(models.Model):
    """Talent Pokémon — template partagé entre toutes les espèces qui le possèdent."""

    name        = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, default='')
    effect_tag  = models.CharField(max_length=50, blank=True, null=True)
    trigger     = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='passive')

    class Meta:
        verbose_name        = "Talent"
        verbose_name_plural = "Talents"
        ordering            = ['name']

    def __str__(self):
        return self.name

    @property
    def is_implemented(self):
        return bool(self.effect_tag)

    def get_trigger_label(self):
        return dict(TRIGGER_CHOICES).get(self.trigger, self.trigger)

    # =========================================================================
    # HOOKS PUBLICS — appelés par Battle.py
    # =========================================================================

    def on_switch_in(self, battle, pokemon):
        handlers = {
            'intimidate':   self._resolve_intimidate,
            'drought':      self._resolve_drought,
            'drizzle':      self._resolve_drizzle,
            'sand_stream':  self._resolve_sand_stream,
            'snow_warning': self._resolve_snow_warning,
            'trace':        self._resolve_trace,
            'download':     self._resolve_download,
            'forewarn':     self._resolve_forewarn,
            'anticipation': self._resolve_anticipation,
            'frisk':        self._resolve_frisk,
        }
        handler = handlers.get(self.effect_tag)
        return handler(battle, pokemon) if handler else None

    def on_switch_out(self, battle, pokemon):
        handlers = {
            'natural_cure': self._resolve_natural_cure,
            'regenerator':  self._resolve_regenerator,
        }
        handler = handlers.get(self.effect_tag)
        return handler(battle, pokemon) if handler else None

    def on_damage_taken(self, battle, pokemon, damage, move):
        """move peut être None pour les dégâts indirects (météo, poison…)."""
        handlers = {
            'sturdy':       self._resolve_sturdy,
            'levitate':     self._resolve_levitate,
            'flash_fire':   self._resolve_flash_fire,
            'volt_absorb':  self._resolve_volt_absorb,
            'water_absorb': self._resolve_water_absorb,
            'dry_skin':     self._resolve_dry_skin,
            'marvel_scale': self._resolve_marvel_scale,
            'thick_fat':    self._resolve_thick_fat,
            'static':       self._resolve_static,
            'flame_body':   self._resolve_flame_body,
            'poison_point': self._resolve_poison_point,
            'effect_spore': self._resolve_effect_spore,
            'cute_charm':   self._resolve_cute_charm,
            'rough_skin':   self._resolve_rough_skin,
            'iron_barbs':   self._resolve_rough_skin,   # même effet
            'liquid_ooze':  self._resolve_liquid_ooze,
            'shell_armor':  self._resolve_shell_armor,
            'battle_armor': self._resolve_shell_armor,
            'soundproof':   self._resolve_soundproof,
            'filter':       self._resolve_filter,
            'solid_rock':   self._resolve_filter,
            'damp':         self._resolve_damp,
            'rock_head':    self._resolve_rock_head,
            'magic_guard':  self._resolve_magic_guard,
            'sand_veil':    None,    # evasion boost, géré dans calcul précision
            'snow_cloak':   None,
            'clear_body':   self._resolve_clear_body,
            'white_smoke':  self._resolve_clear_body,
            'hyper_cutter': self._resolve_hyper_cutter,
            'keen_eye':     self._resolve_keen_eye,
        }
        handler = handlers.get(self.effect_tag)
        return handler(battle, pokemon, damage, move) if handler else None

    def on_attack(self, battle, pokemon, move, base_power):
        handlers = {
            'blaze':        self._resolve_blaze,
            'torrent':      self._resolve_torrent,
            'overgrow':     self._resolve_overgrow,
            'swarm':        self._resolve_swarm,
            'technician':   self._resolve_technician,
            'hustle':       self._resolve_hustle,
            'iron_fist':    self._resolve_iron_fist,
            'reckless':     self._resolve_reckless,
            'sheer_force':  self._resolve_sheer_force,
            'serene_grace': self._resolve_serene_grace,
            'solar_power':  self._resolve_solar_power,
            'tinted_lens':  self._resolve_tinted_lens,
            'adaptability': self._resolve_adaptability,
            'mold_breaker': self._resolve_mold_breaker,
            'analytic':     self._resolve_analytic,
            'stench':       self._resolve_stench,
        }
        handler = handlers.get(self.effect_tag)
        return handler(battle, pokemon, move, base_power) if handler else None

    def on_status(self, battle, pokemon, status):
        handlers = {
            'immunity':     self._resolve_immunity,
            'insomnia':     self._resolve_insomnia,
            'vital_spirit': self._resolve_insomnia,
            'limber':       self._resolve_limber,
            'own_tempo':    self._resolve_own_tempo,
            'oblivious':    self._resolve_oblivious,
            'inner_focus':  self._resolve_inner_focus,
            'synchronize':  self._resolve_synchronize,
            'water_veil':   self._resolve_water_veil,
            'magma_armor':  self._resolve_magma_armor,
        }
        handler = handlers.get(self.effect_tag)
        return handler(battle, pokemon, status) if handler else None

    def modify_stat(self, stat_name, pokemon, battle=None):
        handlers = {
            'guts':        self._modify_guts,
            'huge_power':  self._modify_huge_power,
            'pure_power':  self._modify_huge_power,
            'swift_swim':  self._modify_swift_swim,
            'chlorophyll': self._modify_chlorophyll,
            'sand_rush':   self._modify_sand_rush,
            'slush_rush':  self._modify_slush_rush,
            'hustle':      self._modify_hustle_stat,
            'defiant':     self._modify_defiant,
            'competitive': self._modify_competitive,
        }
        handler = handlers.get(self.effect_tag)
        return handler(stat_name, pokemon, battle) if handler else 1.0

    def end_of_turn(self, battle, pokemon):
        handlers = {
            'speed_boost': self._resolve_speed_boost,
            'rain_dish':   self._resolve_rain_dish,
            'poison_heal': self._resolve_poison_heal,
            'shed_skin':   self._resolve_shed_skin,
            'dry_skin':    self._resolve_dry_skin_eot,
            'solar_power': self._resolve_solar_power_eot,
            'ice_body':    self._resolve_ice_body,
            'hydration':   self._resolve_hydration,
        }
        handler = handlers.get(self.effect_tag)
        return handler(battle, pokemon) if handler else None

    def on_capture(self, wild_pokemon):
        handlers = {
            'illuminate': self._resolve_illuminate,
        }
        handler = handlers.get(self.effect_tag)
        return handler(wild_pokemon) if handler else None

    # =========================================================================
    # RÉSOLUTIONS — on_switch_in
    # =========================================================================

    def _resolve_intimidate(self, battle, pokemon):
        return {
            'lower_opponent_attack': 1,
            'message': f"Le talent Intimidation de {pokemon} baisse l'Attaque adverse !",
        }

    def _resolve_drought(self, battle, pokemon):
        return {
            'set_weather': 'sunny', 'weather_turns': 5,
            'message': f"Le talent Sécheresse de {pokemon} déclenche un soleil intense !",
        }

    def _resolve_drizzle(self, battle, pokemon):
        return {
            'set_weather': 'rain', 'weather_turns': 5,
            'message': f"Le talent Bruine de {pokemon} fait tomber la pluie !",
        }

    def _resolve_sand_stream(self, battle, pokemon):
        return {
            'set_weather': 'sandstorm', 'weather_turns': 5,
            'message': f"Le talent Sable Volant de {pokemon} déclenche une tempête !",
        }

    def _resolve_snow_warning(self, battle, pokemon):
        return {
            'set_weather': 'hail', 'weather_turns': 5,
            'message': f"Le talent Alerte Neige de {pokemon} déclenche la grêle !",
        }

    def _resolve_trace(self, battle, pokemon):
        opp = self._get_opponent(battle, pokemon)
        if opp and opp.ability:
            return {
                'copy_ability_from_opponent': True,
                'message': f"{pokemon} copie le talent {opp.ability.name} grâce à Calque !",
            }
        return None

    def _resolve_download(self, battle, pokemon):
        opp = self._get_opponent(battle, pokemon)
        if opp:
            if opp.defense <= opp.special_defense:
                return {
                    'raise_attack': 1,
                    'message': f"Le talent Téléchargement de {pokemon} booste son Attaque !",
                }
            else:
                return {
                    'raise_special_attack': 1,
                    'message': f"Le talent Téléchargement de {pokemon} booste son Attaque Spéciale !",
                }
        return None

    def _resolve_forewarn(self, battle, pokemon):
        opp = self._get_opponent(battle, pokemon)
        if opp:
            strongest = max(
                opp.pokemonmoveinstance_set.select_related('move').all(),
                key=lambda mi: mi.move.power or 0,
                default=None,
            )
            if strongest:
                return {
                    'message': (
                        f"Pressentiment détecte {strongest.move.name} "
                        f"({strongest.move.power or 0} puissance) chez {opp} !"
                    ),
                }
        return None

    def _resolve_anticipation(self, battle, pokemon):
        opp = self._get_opponent(battle, pokemon)
        if opp:
            p_types = {pokemon.species.primary_type.name}
            if pokemon.species.secondary_type:
                p_types.add(pokemon.species.secondary_type.name)
            for mi in opp.pokemonmoveinstance_set.select_related('move__type').all():
                # Simplification : on vérifie les types super efficaces connus
                SE_MAP = {
                    'fire': {'grass', 'ice', 'bug', 'steel'},
                    'water': {'fire', 'ground', 'rock'},
                    'electric': {'water', 'flying'},
                    'grass': {'water', 'ground', 'rock'},
                    'ice': {'grass', 'ground', 'flying', 'dragon'},
                    'fighting': {'normal', 'ice', 'rock', 'dark', 'steel'},
                    'poison': {'grass', 'fairy'},
                    'ground': {'fire', 'electric', 'poison', 'rock', 'steel'},
                    'flying': {'grass', 'fighting', 'bug'},
                    'psychic': {'fighting', 'poison'},
                    'bug': {'grass', 'psychic', 'dark'},
                    'rock': {'fire', 'ice', 'flying', 'bug'},
                    'ghost': {'psychic', 'ghost'},
                    'dragon': {'dragon'},
                    'dark': {'psychic', 'ghost'},
                    'steel': {'ice', 'rock', 'fairy'},
                    'fairy': {'fighting', 'dragon', 'dark'},
                }
                move_type = mi.move.type.name if mi.move.type else ''
                if p_types & SE_MAP.get(move_type, set()):
                    return {
                        'message': f"{pokemon} frémit grâce à son talent Appréhension !",
                    }
        return None

    def _resolve_frisk(self, battle, pokemon):
        opp = self._get_opponent(battle, pokemon)
        if opp and opp.held_item:
            return {
                'message': (
                    f"Grâce à Inspection de {pokemon}, "
                    f"{opp} porte {opp.held_item.name} !"
                ),
            }
        return None

    # =========================================================================
    # RÉSOLUTIONS — on_switch_out
    # =========================================================================

    def _resolve_natural_cure(self, battle, pokemon):
        if pokemon.status_condition:
            return {
                'clear_status': True,
                'message': f"Guérison Naturelle libère {pokemon} de son statut !",
            }
        return None

    def _resolve_regenerator(self, battle, pokemon):
        heal = max(1, pokemon.max_hp // 3)
        return {
            'heal': heal,
            'message': f"Régénérateur restaure {heal} HP à {pokemon} au retrait !",
        }

    # =========================================================================
    # RÉSOLUTIONS — on_damage_taken
    # =========================================================================

    def _resolve_sturdy(self, battle, pokemon, damage, move):
        if pokemon.current_hp == pokemon.max_hp and damage >= pokemon.current_hp:
            return {
                'damage_cap': pokemon.current_hp - 1,
                'message': f"{pokemon} résiste grâce à Fermeté !",
            }
        return None

    def _resolve_levitate(self, battle, pokemon, damage, move):
        if move and move.type and move.type.name == 'ground':
            return {
                'block': True,
                'message': f"Lévitation immunise {pokemon} contre les attaques Sol !",
            }
        return None

    def _resolve_flash_fire(self, battle, pokemon, damage, move):
        if move and move.type and move.type.name == 'fire':
            return {
                'block': True, 'boost_fire': True,
                'message': f"Magma Carapace absorbe l'attaque Feu et booste {pokemon} !",
            }
        return None

    def _resolve_volt_absorb(self, battle, pokemon, damage, move):
        if move and move.type and move.type.name == 'electric':
            heal = max(1, pokemon.max_hp // 4)
            return {
                'block': True, 'heal': heal,
                'message': f"Absorption absorbe l'électricité ! {pokemon} récupère {heal} HP !",
            }
        return None

    def _resolve_water_absorb(self, battle, pokemon, damage, move):
        if move and move.type and move.type.name == 'water':
            heal = max(1, pokemon.max_hp // 4)
            return {
                'block': True, 'heal': heal,
                'message': f"Absorption Eau soigne {pokemon} de {heal} HP !",
            }
        return None

    def _resolve_dry_skin(self, battle, pokemon, damage, move):
        if not move or not move.type:
            return None
        if move.type.name == 'water':
            heal = max(1, pokemon.max_hp // 4)
            return {
                'block': True, 'heal': heal,
                'message': f"Peau Sèche absorbe l'eau ! {pokemon} récupère {heal} HP !",
            }
        if move.type.name == 'fire':
            extra = max(1, pokemon.max_hp // 4)
            return {
                'extra_damage': extra,
                'message': f"La Peau Sèche de {pokemon} aggrave les dégâts du feu !",
            }
        return None

    def _resolve_marvel_scale(self, battle, pokemon, damage, move):
        if pokemon.status_condition:
            return {'defense_multiplier': 1.5}
        return None

    def _resolve_thick_fat(self, battle, pokemon, damage, move):
        if move and move.type and move.type.name in ('fire', 'ice'):
            return {
                'power_multiplier': 0.5,
                'message': f"L'Engraissement de {pokemon} réduit les dégâts !",
            }
        return None

    def _resolve_static(self, battle, pokemon, damage, move):
        if move and move.category == 'physical' and random.random() < 0.30:
            return {
                'inflict_status_on_attacker': 'paralysis',
                'message': f"Le talent Statik de {pokemon} paralyse l'attaquant !",
            }
        return None

    def _resolve_flame_body(self, battle, pokemon, damage, move):
        if move and move.category == 'physical' and random.random() < 0.30:
            return {
                'inflict_status_on_attacker': 'burn',
                'message': f"Corps Ardent de {pokemon} brûle l'attaquant !",
            }
        return None

    def _resolve_poison_point(self, battle, pokemon, damage, move):
        if move and move.category == 'physical' and random.random() < 0.30:
            return {
                'inflict_status_on_attacker': 'poison',
                'message': f"Point Poison de {pokemon} empoisonne l'attaquant !",
            }
        return None

    def _resolve_effect_spore(self, battle, pokemon, damage, move):
        if move and move.category == 'physical' and random.random() < 0.30:
            status = random.choice(['paralysis', 'poison', 'sleep'])
            labels = {'paralysis': 'paralysé', 'poison': 'empoisonné', 'sleep': 'endormi'}
            return {
                'inflict_status_on_attacker': status,
                'message': f"Paraspora de {pokemon} laisse l'attaquant {labels[status]} !",
            }
        return None

    def _resolve_cute_charm(self, battle, pokemon, damage, move):
        if move and move.category == 'physical' and random.random() < 0.30:
            return {
                'confuse_attacker': True,
                'message': f"Joli Sourire de {pokemon} fascine l'attaquant !",
            }
        return None

    def _resolve_rough_skin(self, battle, pokemon, damage, move):
        if move and move.category == 'physical':
            dmg = max(1, pokemon.max_hp // 8)
            return {
                'damage_to_attacker': dmg,
                'message': f"La Peau Dure de {pokemon} blesse l'attaquant ({dmg} HP) !",
            }
        return None

    def _resolve_liquid_ooze(self, battle, pokemon, damage, move):
        if move and getattr(move, 'effect', None) in ('drain', 'drain_sleep'):
            return {
                'invert_drain': True,
                'message': f"La Sève Toxique de {pokemon} blesse l'attaquant !",
            }
        return None

    def _resolve_shell_armor(self, battle, pokemon, damage, move):
        return {'crit_block': True}

    def _resolve_soundproof(self, battle, pokemon, damage, move):
        if move and move.name in SOUND_MOVES:
            return {
                'block': True,
                'message': f"Anti-Son de {pokemon} bloque l'attaque sonore !",
            }
        return None

    def _resolve_filter(self, battle, pokemon, damage, move):
        if getattr(battle, 'last_effectiveness', 1.0) >= 2.0:
            return {
                'power_multiplier': 0.75,
                'message': f"Le Filtre de {pokemon} réduit les dégâts super efficaces !",
            }
        return None

    def _resolve_damp(self, battle, pokemon, damage, move):
        if move and getattr(move, 'effect', None) in ('faint_user', 'self_destruct'):
            return {
                'block': True,
                'message': f"La Moiteur de {pokemon} empêche l'explosion !",
            }
        return None

    def _resolve_rock_head(self, battle, pokemon, damage, move):
        """Annule les dégâts de recul pour le porteur."""
        # Ce hook est appelé lors des dégâts de recul (battle doit passer move=None, damage=recul)
        if move is None:   # recul = dégât sans move attaquant
            return {'recoil_block': True}
        return None

    def _resolve_magic_guard(self, battle, pokemon, damage, move):
        """Immunité à tous les dégâts indirects (météo, recul, empoisonnement…)."""
        if move is None:
            return {
                'block': True,
            }
        return None

    def _resolve_clear_body(self, battle, pokemon, damage, move):
        """Bloque toute baisse de stat infligée par l'adversaire."""
        return {'stat_drop_block': True}

    def _resolve_hyper_cutter(self, battle, pokemon, damage, move):
        """L'Attaque ne peut pas être baissée."""
        return {'stat_drop_block_attack': True}

    def _resolve_keen_eye(self, battle, pokemon, damage, move):
        """La précision ne peut pas être baissée."""
        return {'stat_drop_block_accuracy': True}

    # =========================================================================
    # RÉSOLUTIONS — on_attack
    # =========================================================================

    def _resolve_blaze(self, battle, pokemon, move, base_power):
        if move.type.name == 'fire' and pokemon.current_hp <= pokemon.max_hp // 3:
            return {
                'power_multiplier': 1.5,
                'message': f"Le talent Brasier de {pokemon} s'enflamme !",
            }
        return None

    def _resolve_torrent(self, battle, pokemon, move, base_power):
        if move.type.name == 'water' and pokemon.current_hp <= pokemon.max_hp // 3:
            return {
                'power_multiplier': 1.5,
                'message': f"Le talent Torrent de {pokemon} déchaîne les flots !",
            }
        return None

    def _resolve_overgrow(self, battle, pokemon, move, base_power):
        if move.type.name == 'grass' and pokemon.current_hp <= pokemon.max_hp // 3:
            return {
                'power_multiplier': 1.5,
                'message': f"Le talent Engrais de {pokemon} renforce les plantes !",
            }
        return None

    def _resolve_swarm(self, battle, pokemon, move, base_power):
        if move.type.name == 'bug' and pokemon.current_hp <= pokemon.max_hp // 3:
            return {
                'power_multiplier': 1.5,
                'message': f"Le talent Essaim de {pokemon} décuple sa puissance !",
            }
        return None

    def _resolve_technician(self, battle, pokemon, move, base_power):
        if base_power <= 60:
            return {
                'power_multiplier': 1.5,
                'message': f"Technicien de {pokemon} booste l'attaque !",
            }
        return None

    def _resolve_hustle(self, battle, pokemon, move, base_power):
        if move.category == 'physical':
            return {'power_multiplier': 1.5, 'accuracy_multiplier': 0.8}
        return None

    def _resolve_iron_fist(self, battle, pokemon, move, base_power):
        if move.name in PUNCHING_MOVES:
            return {
                'power_multiplier': 1.2,
                'message': f"Poing de Fer de {pokemon} amplifie le coup !",
            }
        return None

    def _resolve_reckless(self, battle, pokemon, move, base_power):
        if getattr(move, 'effect', None) in RECOIL_EFFECTS:
            return {
                'power_multiplier': 1.2,
                'message': f"Témérité de {pokemon} booste l'attaque !",
            }
        return None

    def _resolve_sheer_force(self, battle, pokemon, move, base_power):
        if getattr(move, 'effect_chance', 0) and move.effect_chance > 0 and move.effect:
            return {
                'power_multiplier': 1.3,
                'suppress_secondary_effect': True,
                'message': f"Grande Forme de {pokemon} concentre sa puissance !",
            }
        return None

    def _resolve_serene_grace(self, battle, pokemon, move, base_power):
        if getattr(move, 'effect_chance', 0) and move.effect_chance > 0:
            return {'double_effect_chance': True}
        return None

    def _resolve_solar_power(self, battle, pokemon, move, base_power):
        if move.category == 'special' and getattr(battle, 'weather', None) == 'sunny':
            return {'power_multiplier': 1.5}
        return None

    def _resolve_tinted_lens(self, battle, pokemon, move, base_power):
        if getattr(battle, 'last_effectiveness', 1.0) < 1.0:
            return {
                'power_multiplier': 2.0,
                'message': f"Xérolens de {pokemon} perce les défenses !",
            }
        return None

    def _resolve_adaptability(self, battle, pokemon, move, base_power):
        p_types = {pokemon.species.primary_type.name}
        if pokemon.species.secondary_type:
            p_types.add(pokemon.species.secondary_type.name)
        if move.type.name in p_types:
            return {'stab_override': 2.0}
        return None

    def _resolve_mold_breaker(self, battle, pokemon, move, base_power):
        return {'ignore_opponent_ability': True}

    def _resolve_analytic(self, battle, pokemon, move, base_power):
        if getattr(battle, 'player_moved_last', False):
            return {
                'power_multiplier': 1.3,
                'message': f"Analytique de {pokemon} profite de l'avantage !",
            }
        return None

    def _resolve_stench(self, battle, pokemon, move, base_power):
        """10 % de chance de faire reculer l'adversaire."""
        if random.random() < 0.10:
            return {'flinch_opponent': True}
        return None

    # =========================================================================
    # RÉSOLUTIONS — on_status
    # =========================================================================

    def _resolve_immunity(self, battle, pokemon, status):
        if status == 'poison':
            return {
                'prevent_status': True,
                'message': f"Immunité bloque l'empoisonnement de {pokemon} !",
            }
        return None

    def _resolve_insomnia(self, battle, pokemon, status):
        if status == 'sleep':
            return {
                'prevent_status': True,
                'message': f"Insomnie empêche {pokemon} de s'endormir !",
            }
        return None

    def _resolve_limber(self, battle, pokemon, status):
        if status == 'paralysis':
            return {
                'prevent_status': True,
                'message': f"Souplesse immunise {pokemon} contre la paralysie !",
            }
        return None

    def _resolve_own_tempo(self, battle, pokemon, status):
        if status == 'confusion':
            return {
                'prevent_status': True,
                'message': f"Tempo Perso immunise {pokemon} contre la confusion !",
            }
        return None

    def _resolve_oblivious(self, battle, pokemon, status):
        if status in ('infatuation', 'taunt'):
            return {
                'prevent_status': True,
                'message': f"Indolence rend {pokemon} insensible !",
            }
        return None

    def _resolve_inner_focus(self, battle, pokemon, status):
        if status == 'flinch':
            return {'prevent_status': True}
        return None

    def _resolve_synchronize(self, battle, pokemon, status):
        if status in ('paralysis', 'poison', 'burn'):
            return {
                'transmit_status_to_opponent': status,
                'message': f"Synchronisme de {pokemon} transmet le statut à l'adversaire !",
            }
        return None

    def _resolve_water_veil(self, battle, pokemon, status):
        if status == 'burn':
            return {
                'prevent_status': True,
                'message': f"Voile Aquatique immunise {pokemon} contre la brûlure !",
            }
        return None

    def _resolve_magma_armor(self, battle, pokemon, status):
        if status == 'freeze':
            return {
                'prevent_status': True,
                'message': f"Armure de Feu empêche {pokemon} d'être gelé !",
            }
        return None

    # =========================================================================
    # RÉSOLUTIONS — modify_stat
    # =========================================================================

    def _get_weather(self, battle):
        return getattr(battle, 'weather', None) if battle else None

    def _modify_guts(self, stat_name, pokemon, battle):
        if stat_name == 'attack' and pokemon.status_condition:
            return 1.5
        return 1.0

    def _modify_hustle_stat(self, stat_name, pokemon, battle):
        return 1.0   # le malus précision est appliqué dans on_attack

    def _modify_huge_power(self, stat_name, pokemon, battle):
        return 2.0 if stat_name == 'attack' else 1.0

    def _modify_swift_swim(self, stat_name, pokemon, battle):
        return 2.0 if stat_name == 'speed' and self._get_weather(battle) == 'rain' else 1.0

    def _modify_chlorophyll(self, stat_name, pokemon, battle):
        return 2.0 if stat_name == 'speed' and self._get_weather(battle) == 'sunny' else 1.0

    def _modify_sand_rush(self, stat_name, pokemon, battle):
        return 2.0 if stat_name == 'speed' and self._get_weather(battle) == 'sandstorm' else 1.0

    def _modify_slush_rush(self, stat_name, pokemon, battle):
        return 2.0 if stat_name == 'speed' and self._get_weather(battle) == 'hail' else 1.0

    def _modify_defiant(self, stat_name, pokemon, battle):
        """Boost géré dans Battle.py lors d'une baisse de stat imposée."""
        return 1.0

    def _modify_competitive(self, stat_name, pokemon, battle):
        """Idem Defiant mais pour Atq Spé."""
        return 1.0

    # =========================================================================
    # RÉSOLUTIONS — end_of_turn
    # =========================================================================

    def _resolve_speed_boost(self, battle, pokemon):
        return {
            'raise_speed': 1,
            'message': f"Le talent Turbo de {pokemon} augmente sa Vitesse !",
        }

    def _resolve_rain_dish(self, battle, pokemon):
        if getattr(battle, 'weather', None) == 'rain':
            heal = max(1, pokemon.max_hp // 16)
            return {'heal': heal, 'message': f"Cuvette restaure {heal} HP à {pokemon} !"}
        return None

    def _resolve_poison_heal(self, battle, pokemon):
        if pokemon.status_condition in ('poison', 'badly_poison'):
            heal = max(1, pokemon.max_hp // 8)
            return {
                'heal': heal, 'block_poison_damage': True,
                'message': f"Soin Toxique restaure {heal} HP à {pokemon} !",
            }
        return None

    def _resolve_shed_skin(self, battle, pokemon):
        if pokemon.status_condition and random.random() < 0.30:
            return {
                'clear_status': True,
                'message': f"Mue libère {pokemon} de son statut !",
            }
        return None

    def _resolve_dry_skin_eot(self, battle, pokemon):
        weather = getattr(battle, 'weather', None)
        if weather == 'rain':
            heal = max(1, pokemon.max_hp // 8)
            return {'heal': heal, 'message': f"Peau Sèche soigne {pokemon} sous la pluie (+{heal} HP) !"}
        if weather == 'sunny':
            dmg = max(1, pokemon.max_hp // 8)
            return {'damage': dmg, 'message': f"Peau Sèche brûle {pokemon} sous le soleil (-{dmg} HP) !"}
        return None

    def _resolve_solar_power_eot(self, battle, pokemon):
        if getattr(battle, 'weather', None) == 'sunny':
            dmg = max(1, pokemon.max_hp // 8)
            return {
                'damage': dmg,
                'message': f"Puissance Solaire consume {pokemon} (-{dmg} HP) !",
            }
        return None

    def _resolve_ice_body(self, battle, pokemon):
        if getattr(battle, 'weather', None) == 'hail':
            heal = max(1, pokemon.max_hp // 16)
            return {'heal': heal, 'message': f"Corps Glace soigne {pokemon} (+{heal} HP) !"}
        return None

    def _resolve_hydration(self, battle, pokemon):
        if pokemon.status_condition and getattr(battle, 'weather', None) == 'rain':
            return {
                'clear_status': True,
                'message': f"Hydratation guérit le statut de {pokemon} !",
            }
        return None

    # =========================================================================
    # RÉSOLUTIONS — on_capture
    # =========================================================================

    def _resolve_illuminate(self, wild_pokemon):
        return {'rate_multiplier': 1.0}

    # =========================================================================
    # HELPER
    # =========================================================================

    @staticmethod
    def _get_opponent(battle, pokemon):
        """Retourne le Pokémon adverse selon le camp du porteur."""
        if not battle:
            return None
        if getattr(battle, 'player_pokemon', None) == pokemon:
            return getattr(battle, 'opponent_pokemon', None)
        return getattr(battle, 'player_pokemon', None)