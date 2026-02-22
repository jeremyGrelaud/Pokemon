#!/usr/bin/python3
"""
Script d'ajout des moves Gen 3 manquants dans la base.
À exécuter AVANT initLearnableMovesGen3.py pour que les learnsets
puissent référencer ces moves.

Moves ajoutés: ceux présents dans les learnsets FRLG mais absents
de initializeDatabase.py (Aerial Ace, Drill Peck, Blaze Kick, etc.)
"""

from myPokemonApp.models import PokemonMove, PokemonType
import logging

logging.basicConfig(level=logging.INFO)


def add_missing_gen3_moves():
    """Ajoute les moves Gen 3 manquants pour supporter les learnsets FRLG."""

    logging.info("[*] Ajout des moves manquants Gen 3...")

    def get_type(name):
        return PokemonType.objects.get(name=name)

    # Format: (nom, type, catégorie, puissance, précision, pp, priorité, effet, chance_effet, statut)
    missing_moves = [
        # GEN 3 NOUVEAUX MOVES (non présents dans initializeDatabase.py)
        ('Aerial Ace',      'flying',    'physical', 60,   100, 20, 0, 'never_miss',         100, None),
        ('Air Cutter',      'flying',    'special',  60,   95,  25, 0, 'high_crit',          100, None),
        ('Blaze Kick',      'fire',      'physical', 85,   90,  10, 0, 'high_crit',          10,  'burn'),
        ('Bullet Seed',     'grass',     'physical', 25,   100, 30, 0, 'multi_hit',          100, None),
        ('Dive',            'water',     'physical', 80,   100, 10, 0, 'charge_turn',        100, None),
        ('Eruption',        'fire',      'special',  150,  100, 5,  0, 'more_damage_if_hp',  100, None),
        ('Extrasensory',    'psychic',   'special',  80,   100, 20, 0, 'flinch',             10,  None),
        ('Fake Tears',      'dark',      'status',   0,    100, 20, 0, 'sharply_lower_special_defense', 100, None),
        ('Feather Dance',   'flying',    'status',   0,    100, 15, 0, 'sharply_lower_attack', 100, None),
        ('Flatter',         'dark',      'status',   0,    100, 15, 0, 'confuse_raise_spatk', 100, None),
        ('Focus Punch',     'fighting',  'physical', 150,  100, 20, 0, 'focus_punch',        100, None),
        ('Grass Whistle',   'grass',     'status',   0,    55,  15, 0, None,                 0,   'sleep'),
        ('Hail',            'ice',       'status',   0,    100, 10, 0, 'hail',               100, None),
        ('Heat Wave',       'fire',      'special',  95,   90,  10, 0, None,                 10,  'burn'),
        ('Howl',            'normal',    'status',   0,    100, 40, 0, 'raise_attack',       100, None),
        ('Hyper Voice',     'normal',    'special',  90,   100, 10, 0, 'sound_based',        100, None),
        ('Icicle Spear',    'ice',       'physical', 25,   100, 30, 0, 'multi_hit',          100, None),
        ('Ingrain',         'grass',     'status',   0,    100, 20, 0, 'ingrain',            100, None),
        ('Knock Off',       'dark',      'physical', 65,   100, 20, 0, 'remove_item',        100, None),
        ('Leaf Blade',      'grass',     'physical', 90,   100, 15, 0, 'high_crit',          100, None),
        ('Luster Purge',    'psychic',   'special',  95,   100, 5,  0, 'lower_special_defense', 50, None),
        ('Magic Coat',      'psychic',   'status',   0,    100, 15, 0, 'magic_coat',         100, None),
        ('Magical Leaf',    'grass',     'special',  60,   100, 20, 0, 'never_miss',         100, None),
        ('Memento',         'dark',      'status',   0,    100, 10, 0, 'memento',            100, None),
        ('Metal Sound',     'steel',     'status',   0,    85,  40, 0, 'sharply_lower_special_defense', 100, None),
        ('Mist Ball',       'psychic',   'special',  95,   100, 5,  0, 'lower_spatk',        50,  None),
        ('Nature Power',    'normal',    'status',   0,    100, 20, 0, 'nature_power',       100, None),
        ('Needle Arm',      'grass',     'physical', 60,   100, 15, 0, 'flinch',             30,  None),
        ('Odor Sleuth',     'normal',    'status',   0,    100, 40, 0, 'odor_sleuth',        100, None),
        ('Overheat',        'fire',      'special',  130,  90,  5,  0, 'sharply_lower_special_attack', 100, None),
        ('Poison Fang',     'poison',    'physical', 50,   100, 15, 0, 'badly_poison',       30,  None),
        ('Psycho Boost',    'psychic',   'special',  140,  90,  5,  0, 'sharply_lower_special_attack', 100, None),
        ('Refresh',         'normal',    'status',   0,    100, 20, 0, 'refresh',            100, None),
        ('Revenge',         'fighting',  'physical', 60,   100, 10, -4, 'double_if_hit',     100, None),
        ('Role Play',       'psychic',   'status',   0,    100, 10, 0, 'role_play',          100, None),
        ('Sand Tomb',       'ground',    'physical', 35,   85,  15, 0, 'trap',               100, None),
        ('Secret Power',    'normal',    'physical', 70,   100, 20, 0, 'secret_power',       30,  None),
        ('Shock Wave',      'electric',  'special',  60,   100, 20, 0, 'never_miss',         100, None),
        ('Signal Beam',     'bug',       'special',  75,   100, 15, 0, 'confuse',            10,  None),
        ('Silver Wind',     'bug',       'special',  60,   100, 5,  0, 'raise_all_stats',    10,  None),
        ('Skill Swap',      'psychic',   'status',   0,    100, 10, 0, 'skill_swap',         100, None),
        ('Sky Uppercut',    'fighting',  'physical', 85,   90,  15, 0, 'hit_flying',         100, None),
        ('Smelling Salts',  'normal',    'physical', 70,   100, 10, 0, 'double_if_paralyzed', 100, None),
        ('Snatch',          'dark',      'status',   0,    100, 10, 4, 'snatch',             100, None),
        ('Spit Up',         'normal',    'special',  1,    100, 10, 0, 'spit_up',            100, None),
        ('Stockpile',       'normal',    'status',   0,    100, 20, 0, 'stockpile',          100, None),
        ('Superpower',      'fighting',  'physical', 120,  100, 5,  0, 'lower_attack_defense', 100, None),
        ('Swallow',         'normal',    'status',   0,    100, 10, 0, 'swallow',            100, None),
        ('Taunt',           'dark',      'status',   0,    100, 20, 0, 'taunt',              100, None),
        ('Tickle',          'normal',    'status',   0,    100, 20, 0, 'lower_attack_defense', 100, None),
        ('Torment',         'dark',      'status',   0,    100, 15, 0, 'torment',            100, None),
        ('Trick',           'psychic',   'status',   0,    100, 10, 0, 'swap_items',         100, None),
        ('Uproar',          'normal',    'special',  90,   100, 10, 0, 'uproar',             100, None),
        ('Volt Tackle',     'electric',  'physical', 120,  100, 15, 0, 'recoil',             10,  'paralysis'),
        ('Water Pulse',     'water',     'special',  60,   100, 20, 0, 'confuse',            20,  None),
        ('Water Sport',     'water',     'status',   0,    100, 15, 0, 'water_sport',        100, None),
        ('Weather Ball',    'normal',    'special',  50,   100, 10, 0, 'weather_ball',       100, None),
        ('Will-O-Wisp',     'fire',      'status',   0,    85,  15, 0, None,                 0,   'burn'),
        ('Yawn',            'normal',    'status',   0,    100, 10, 0, 'yawn',               100, None),
        ('Wish',            'normal',    'status',   0,    100, 10, 0, 'wish',               100, None),

        # MOVES GEN 1 MANQUANTS
        ('Drill Peck',      'flying',    'physical', 80,   100, 20, 0, None,                 0,   None),
        ('Double Kick',     'fighting',  'physical', 30,   100, 30, 0, 'hits_twice',         100, None),
        ('Spikes',          'ground',    'status',   0,    100, 20, 0, 'spikes',             100, None),
        ('Pay Day',         'normal',    'physical', 40,   100, 20, 0, 'pay_day',            100, None),
        ('Faint Attack',    'dark',      'physical', 60,   100, 20, 0, 'never_miss',         100, None),
        ('Mega Punch',      'normal',    'physical', 80,   85,  20, 0, None,                 0,   None),
        ('Mega Kick',       'normal',    'physical', 120,  75,  5,  0, None,                 0,   None),
        ('Counter',         'fighting',  'physical', 1,    100, 20, -5, 'counter',           100, None),
        ('Rage',            'normal',    'physical', 20,   100, 20, 0, 'rage',               100, None),
        ('Glare',           'normal',    'status',   0,    90,  30, 0, None,                 0,   'paralysis'),
        ('Bonemerang',      'ground',    'physical', 50,   90,  10, 0, 'hits_twice',         100, None),
        ('Sharpen',         'normal',    'status',   0,    100, 30, 0, 'raise_attack',       100, None),
        ('Conversion 2',    'normal',    'status',   0,    100, 30, 0, 'conversion2',        100, None),
        ('Substitute',      'normal',    'status',   0,    100, 10, 0, 'substitute',         100, None),
        ('Encore',          'normal',    'status',   0,    100, 5,  0, 'encore',             100, None),
        ('Pursuit',         'dark',      'physical', 40,   100, 20, 0, 'double_fleeing',     100, None),
        ('False Swipe',     'normal',    'physical', 40,   100, 40, 0, 'false_swipe',        100, None),
        ('Flail',           'normal',    'physical', 1,    100, 15, 0, 'low_hp_power',       100, None),
        ('Reversal',        'fighting',  'physical', 1,    100, 15, 0, 'low_hp_power',       100, None),
        ('Spider Web',      'bug',       'status',   0,    100, 10, 0, 'block',              100, None),
        ('Foresight',       'normal',    'status',   0,    100, 40, 0, 'foresight',          100, None),
        ('Destiny Bond',    'ghost',     'status',   0,    100, 5,  -5, 'destiny_bond',      100, None),
        ('Perish Song',     'normal',    'status',   0,    100, 5,  0, 'perish_song',        100, None),
        ('Safeguard',       'normal',    'status',   0,    100, 25, 0, 'safeguard',          100, None),
        ('Attract',         'normal',    'status',   0,    100, 15, 0, 'attract',            100, None),
        ('Mud Slap',        'ground',    'special',  20,   100, 10, 0, 'lower_accuracy',     100, None),
        ('Rollout',         'rock',      'physical', 30,   90,  20, 0, 'rollout',            100, None),
        ('Sweet Kiss',      'fairy',     'status',   0,    75,  10, 0, 'confuse',            100, None),
        ('Belly Drum',      'normal',    'status',   0,    100, 10, 0, 'belly_drum',         100, None),
        ('Fury Cutter',     'bug',       'physical', 40,   95,  20, 0, 'fury_cutter',        100, None),
        ('Attract',         'normal',    'status',   0,    100, 15, 0, 'attract',            100, None),
        ('Magnitude',       'ground',    'physical', 1,    100, 30, 0, 'magnitude',          100, None),
        ('Dynamic Punch',   'fighting',  'physical', 100,  50,  5,  0, 'confuse',            100, None),
        ('Megahorn',        'bug',       'physical', 120,  85,  10, 0, None,                 0,   None),
        ('Night Slash',     'dark',      'physical', 70,   100, 15, 0, 'high_crit',          100, None),
        ('Icy Wind',        'ice',       'special',  55,   95,  15, 0, 'lower_speed',        100, None),
        ('Endure',          'normal',    'status',   0,    100, 10, 0, 'endure',             100, None),
        ('Charm',           'fairy',     'status',   0,    100, 20, 0, 'sharply_lower_attack', 100, None),
        ('Present',         'normal',    'physical', 1,    90,  15, 0, 'present',            100, None),
        ('Frustration',     'normal',    'physical', 1,    100, 20, 0, 'frustration',        100, None),
        ('Return',          'normal',    'physical', 1,    100, 20, 0, 'return',             100, None),
        ('Lock-On',         'normal',    'status',   0,    100, 5,  0, 'lock_on',            100, None),
        ('Zap Cannon',      'electric',  'special',  120,  50,  5,  0, None,                 100, 'paralysis'),
        ('Foresight',       'normal',    'status',   0,    100, 40, 0, 'foresight',          100, None),
        ('Vital Throw',     'fighting',  'physical', 70,   100, 10, -1, 'never_miss',        100, None),
        ('Wake-Up Slap',    'fighting',  'physical', 70,   100, 10, 0, 'double_if_sleep_cure', 100, None),
        ('Discharge',       'electric',  'special',  80,   100, 15, 0, None,                 30,  'paralysis'),
        ('Magnet Rise',     'electric',  'status',   0,    100, 10, 0, 'magnet_rise',        100, None),
        ('Charge',          'electric',  'status',   0,    100, 20, 0, 'charge',             100, None),
        ('Aqua Tail',       'water',     'physical', 90,   90,  10, 0, None,                 0,   None),
        ('Dragon Rush',     'dragon',    'physical', 100,  75,  10, 0, 'flinch',             20,  None),
        ('Dragon Tail',     'dragon',    'physical', 60,   90,  10, -6, 'force_switch',      100, None),
        ('Hurricane',       'flying',    'special',  110,  70,  10, 0, 'confuse',            30,  None),
        ('Psystrike',       'psychic',   'special',  100,  100, 10, 0, 'physical_defense',   100, None),
        ('Ancient Power',   'rock',      'special',  60,   100, 5,  0, 'raise_all_stats',    10,  None),
        ('Twister',         'dragon',    'special',  40,   100, 20, 0, 'flinch',             20,  None),
        ('Double Hit',      'normal',    'physical', 35,   90,  10, 0, 'hits_twice',         100, None),
        ('Mud Shot',        'ground',    'special',  55,   95,  15, 0, 'lower_speed',        100, None),
        ('Rock Polish',     'rock',      'status',   0,    100, 20, 0, 'sharply_raise_speed', 100, None),
        ('Aqua Jet',        'water',     'physical', 40,   100, 20, 1, None,                 0,   None),
        ('Gunk Shot',       'poison',    'physical', 120,  80,  5,  0, None,                 30,  'poison'),
        ('Acid Armor',      'poison',    'status',   0,    100, 20, 0, 'sharply_raise_defense', 100, None),
        ('Wood Hammer',     'grass',     'physical', 120,  100, 15, 0, 'recoil',             100, None),
        ('Leaf Storm',      'grass',     'special',  130,  90,  5,  0, 'sharply_lower_special_attack', 100, None),
        ('Gastro Acid',     'poison',    'status',   0,    100, 10, 0, 'suppress_ability',   100, None),
        ('Sucker Punch',    'dark',      'physical', 70,   100, 5,  1, 'fail_if_not_attacking', 100, None),
        ('Sheer Cold',      'ice',       'special',  1,    30,  5,  0, 'ohko',               100, None),
        ('Mind Reader',     'normal',    'status',   0,    100, 5,  0, 'lock_on',            100, None),
        ('Ice Fang',        'ice',       'physical', 65,   95,  15, 0, 'flinch',             10,  'freeze'),
        ('Rock Blast',      'rock',      'physical', 25,   90,  10, 0, 'multi_hit',          100, None),
        ('Crabhammer',      'water',     'physical', 100,  90,  10, 0, 'high_crit',          100, None),
        ('Spike Cannon',    'normal',    'physical', 20,   100, 15, 0, 'multi_hit',          100, None),
        ('Earth Power',     'ground',    'special',  90,   100, 10, 0, 'lower_special_defense', 10, None),
        ('Outrage',         'dragon',    'physical', 120,  100, 10, 0, 'rampage',            100, None),
        ('Extreme Speed',   'normal',    'physical', 80,   100, 5,  2, None,                 0,   None),
        ('Comet Punch',     'normal',    'physical', 18,   85,  15, 0, 'multi_hit',          100, None),
        ('Sky Attack',      'flying',    'physical', 140,  90,  5,  0, 'charge_turn',        30,  'flinch'),
        ('Mist',            'ice',       'status',   0,    100, 30, 0, 'mist',               100, None),
        ('Focus Energy',    'normal',    'status',   0,    100, 30, 0, 'focus_energy',       100, None),
        ('Mirror Move',     'flying',    'status',   0,    100, 20, 0, 'mirror_move',        100, None),
        ('Powder Snow',     'ice',       'special',  40,   100, 25, 0, None,                 10,  'freeze'),
        ('Ice Shard',       'ice',       'physical', 40,   100, 30, 1, None,                 0,   None),
        ('Razor Shell',     'water',     'physical', 75,   95,  10, 0, 'lower_defense',      50,  None),
        ('Constrict',       'normal',    'physical', 10,   100, 35, 0, 'lower_speed',        10,  None),
        ('Bubblebeam',      'water',     'special',  65,   100, 20, 0, 'lower_speed',        10,  None),
        ('Wing Attack',     'flying',    'physical', 60,   100, 35, 0, None,                 0,   None),
        ('Smokescreen',     'normal',    'status',   0,    100, 20, 0, 'lower_accuracy',     100, None),
        ('Scary Face',      'normal',    'status',   0,    100, 10, 0, 'sharply_lower_speed', 100, None),
        ('Pay Day',         'normal',    'physical', 40,   100, 20, 0, 'pay_day',            100, None),
        ('Arm Thrust',      'fighting',  'physical', 15,   100, 20, 0, 'multi_hit',          100, None),
        ('Aromatherapy',    'grass',     'status',   0,    100, 5,  0, 'heal_team_status',   100, None),
        ('Bounce',          'flying',    'physical', 85,   85,  5,  0, 'charge_turn',        30,  'paralysis'),
        ('Night Slash',     'dark',      'physical', 70,   100, 15, 0, 'high_crit',          100, None),
        ('Power Whip',      'grass',     'physical', 120,  85,  10, 0, None,                 0,   None),
        ('Endeavor',        'normal',    'physical', 0,    100, 5,  0, 'endeavor',           100, None),
        ('Crunch',          'dark',      'physical', 80,   100, 15, 0, 'lower_defense',       20,  None),
        ('Poison Jab',      'poison',    'physical', 80,   100, 20, 0, 'poison',             30,  'poison'),
        ('Softboiled',      'normal',    'status',   0,    100, 10, 0, 'heal',               100, None),
        ('Grudge',          'ghost',     'status',   0,    100, 5,  0, 'grudge',             100, None),
        ('Doubleslap',      'normal',    'physical', 15,   85,  10, 0, 'multi_hit',          100, None),
        ('Gyro Ball',       'steel',     'physical', 0,    100, 5,  0, 'gyro_ball',          100, None),
        ('Mimic',           'normal',    'status',   0,    100, 10, 0, 'mimic',              100, None),
        ('Moonlight',       'fairy',     'status',   0,    100, 5,  0, 'heal',               100, None),
        ('Flame Wheel',     'fire',      'physical', 60,   100, 25, 0, 'burn',               10,  'burn'),
        ('Mud Sport',       'ground',    'status',   0,    100, 15, 0, 'mud_sport',           100, None),
        ('Vicegrip',        'normal',    'physical', 55,   100, 30, 0, 'none',               100, None),
        ('Mirror Coat',     'psychic',   'special',  0,    100, 20, -5, 'mirror_coat',        100, None),
        ('Hi Jump Kick',    'fighting',  'physical', 130,  90,  10, 0, 'high_jump_kick',     100, None),
        ('Copy Cat',        'normal',    'status',   0,    100, 20, 0, 'copycat',             100, None),
        ('Vacuum Wave',     'fighting',  'special',  40,   100, 30, 1, 'none',               100, None),
        ('DoubleSlap',      'normal',    'physical', 15,   85,  10, 0, 'multi_hit',          100, None),
        ('Payback',         'dark',      'physical', 50,   100, 10, 0, 'payback',            100, None),
        ('Power Swap',      'psychic',   'status',   0,    100, 10, 0, 'power_swap',         100, None),
        ('Guard Swap',      'psychic',   'status',   0,    100, 10, 0, 'guard_swap',         100, None),
    ]

    types_cache = {}

    def get_type_cached(name):
        if name not in types_cache:
            types_cache[name] = PokemonType.objects.get(name=name)
        return types_cache[name]

    created_count = 0
    skipped_count = 0

    for move_data in missing_moves:
        name, type_name, category, power, accuracy, pp, priority, effect, effect_chance, inflicts_status = move_data
        try:
            move_type = get_type_cached(type_name)
            _, created = PokemonMove.objects.get_or_create(
                name=name,
                defaults={
                    'type': move_type,
                    'category': category,
                    'power': power,
                    'accuracy': accuracy,
                    'pp': pp,
                    'max_pp': pp,
                    'priority': priority,
                    'effect': effect,
                    'effect_chance': effect_chance,
                    'inflicts_status': inflicts_status,
                }
            )
            if created:
                created_count += 1
                logging.info(f"  [+] Move créé: {name}")
            else:
                skipped_count += 1
        except Exception as e:
            logging.warning(f"  [!] Erreur pour move {name}: {e}")

    logging.info(f"[✓] {created_count} moves créés, {skipped_count} déjà présents")


if __name__ == '__main__':
    add_missing_gen3_moves()