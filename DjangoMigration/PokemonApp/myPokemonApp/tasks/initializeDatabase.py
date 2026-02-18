#!/usr/bin/python3
"""
Script d'initialisation de la base de données Pokémon Gen 1
Corrigé pour la nouvelle architecture de modèles
"""


from myPokemonApp.models import (
    Pokemon, 
    PokemonType, 
    PokemonMove, 
    PokemonLearnableMove, 
    PokemonEvolution,
    Item
)
import logging

logging.basicConfig(level=logging.INFO)


def scriptToInitializeDatabase():
    """
    Initialise la base de données avec tous les Pokémon de la Gen 1,
    leurs types, capacités, évolutions et capacités apprises
    """
    
    logging.info("="*60)
    logging.info("INITIALISATION DE LA BASE DE DONNÉES POKÉMON")
    logging.info("="*60)
    
    # ============================================================================
    # ÉTAPE 1: CRÉER LES TYPES
    # ============================================================================
    
    logging.info("\n[*] Création des types Pokémon...")
    
    types_list = [
        'normal', 'fire', 'water', 'electric', 'grass', 'ice',
        'fighting', 'poison', 'ground', 'flying', 'psychic',
        'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy'
    ]
    
    types_dict = {}
    for type_name in types_list:
        type_obj, created = PokemonType.objects.get_or_create(name=type_name)
        types_dict[type_name] = type_obj
        if created:
            logging.info(f"  [+] Type créé: {type_name}")
    
    logging.info(f"[+] {len(types_dict)} types créés/vérifiés")
    
    
    # ============================================================================
    # ÉTAPE 2: DÉFINIR LES EFFICACITÉS DE TYPES
    # ============================================================================
    
    logging.info("\n[*] Configuration des efficacités de types...")
    
    # Format: {type_attaquant: [types_faibles_contre_lui]}
    type_effectiveness = {
        'normal': [],
        'fire': ['grass', 'ice', 'bug', 'steel'],
        'water': ['fire', 'ground', 'rock'],
        'electric': ['water', 'flying'],
        'grass': ['water', 'ground', 'rock'],
        'ice': ['grass', 'ground', 'flying', 'dragon'],
        'fighting': ['normal', 'ice', 'rock', 'dark', 'steel'],
        'poison': ['grass', 'fairy'],
        'ground': ['fire', 'electric', 'poison', 'rock', 'steel'],
        'flying': ['grass', 'fighting', 'bug'],
        'psychic': ['fighting', 'poison'],
        'bug': ['grass', 'psychic', 'dark'],
        'rock': ['fire', 'ice', 'flying', 'bug'],
        'ghost': ['psychic', 'ghost'],
        'dragon': ['dragon'],
        'dark': ['psychic', 'ghost'],
        'steel': ['ice', 'rock', 'fairy'],
        'fairy': ['fighting', 'dragon', 'dark']
    }
    
    for attacking_type_name, effective_against_names in type_effectiveness.items():
        attacking_type = types_dict[attacking_type_name]
        for defending_type_name in effective_against_names:
            defending_type = types_dict[defending_type_name]
            attacking_type.strong_against.add(defending_type)
    
    logging.info("[+] Efficacités de types configurées")
    
    
    # ============================================================================
    # ÉTAPE 3: CRÉER LES CAPACITÉS
    # ============================================================================
    
    logging.info("\n[*] Création des capacités...")
    
    # Liste des capacités avec leurs caractéristiques
    # Format: (nom, type, catégorie, puissance, précision, pp, priorité, effet, chance_effet, statut_infligé)
    # moves_data = [
    #     # ============================================================================
    #     # CAPACITÉS NORMALES
    #     # ============================================================================
    #     ('Pound', 'normal', 'physical', 40, 100, 35, 0, None, 0, None),
    #     ('Karate Chop', 'fighting', 'physical', 50, 100, 25, 0, 'high_crit', 100, None),
    #     ('Double Slap', 'normal', 'physical', 15, 85, 10, 0, 'multi_hit', 100, None),
    #     ('Comet Punch', 'normal', 'physical', 18, 85, 15, 0, 'multi_hit', 100, None),
    #     ('Mega Punch', 'normal', 'physical', 80, 85, 20, 0, None, 0, None),
    #     ('Pay Day', 'normal', 'physical', 40, 100, 20, 0, 'scatter_coins', 100, None),
    #     ('Fire Punch', 'fire', 'physical', 75, 100, 15, 0, None, 10, 'burn'),
    #     ('Ice Punch', 'ice', 'physical', 75, 100, 15, 0, None, 10, 'freeze'),
    #     ('Thunder Punch', 'electric', 'physical', 75, 100, 15, 0, None, 10, 'paralysis'),
    #     ('Scratch', 'normal', 'physical', 40, 100, 35, 0, None, 0, None),
    #     ('Vice Grip', 'normal', 'physical', 55, 100, 30, 0, None, 0, None),
    #     ('Guillotine', 'normal', 'physical', 1, 30, 5, 0, 'ohko', 100, None),
    #     ('Razor Wind', 'normal', 'special', 80, 100, 10, 0, 'charge_turn', 100, None),
    #     ('Swords Dance', 'normal', 'status', 0, 100, 20, 0, 'sharply_raise_attack', 100, None),
    #     ('Cut', 'normal', 'physical', 50, 95, 30, 0, None, 0, None),
    #     ('Gust', 'flying', 'special', 40, 100, 35, 0, None, 0, None),
    #     ('Wing Attack', 'flying', 'physical', 60, 100, 35, 0, None, 0, None),
    #     ('Whirlwind', 'normal', 'status', 0, 100, 20, -6, 'force_switch', 100, None),
    #     ('Fly', 'flying', 'physical', 90, 95, 15, 0, 'fly', 100, None),
    #     ('Bind', 'normal', 'physical', 15, 85, 20, 0, 'trap', 100, None),
    #     ('Slam', 'normal', 'physical', 80, 75, 20, 0, None, 0, None),
    #     ('Vine Whip', 'grass', 'physical', 45, 100, 25, 0, None, 0, None),
    #     ('Stomp', 'normal', 'physical', 65, 100, 20, 0, 'flinch', 30, None),
    #     ('Double Kick', 'fighting', 'physical', 30, 100, 30, 0, 'two_hit', 100, None),
    #     ('Mega Kick', 'normal', 'physical', 120, 75, 5, 0, None, 0, None),
    #     ('Jump Kick', 'fighting', 'physical', 100, 95, 10, 0, 'crash', 100, None),
    #     ('Rolling Kick', 'fighting', 'physical', 60, 85, 15, 0, 'flinch', 30, None),
    #     ('Sand Attack', 'ground', 'status', 0, 100, 15, 0, 'lower_accuracy', 100, None),
    #     ('Headbutt', 'normal', 'physical', 70, 100, 15, 0, 'flinch', 30, None),
    #     ('Horn Attack', 'normal', 'physical', 65, 100, 25, 0, None, 0, None),
    #     ('Fury Attack', 'normal', 'physical', 15, 85, 20, 0, 'multi_hit', 100, None),
    #     ('Horn Drill', 'normal', 'physical', 1, 30, 5, 0, 'ohko', 100, None),
    #     ('Tackle', 'normal', 'physical', 40, 100, 35, 0, None, 0, None),
    #     ('Body Slam', 'normal', 'physical', 85, 100, 15, 0, None, 30, 'paralysis'),
    #     ('Wrap', 'normal', 'physical', 15, 90, 20, 0, 'trap', 100, None),
    #     ('Take Down', 'normal', 'physical', 90, 85, 20, 0, 'recoil', 100, None),
    #     ('Thrash', 'normal', 'physical', 120, 100, 10, 0, 'rampage', 100, None),
    #     ('Double-Edge', 'normal', 'physical', 120, 100, 15, 0, 'recoil', 100, None),
    #     ('Tail Whip', 'normal', 'status', 0, 100, 30, 0, 'lower_defense', 100, None),
    #     ('Poison Sting', 'poison', 'physical', 15, 100, 35, 0, None, 30, 'poison'),
    #     ('Twineedle', 'bug', 'physical', 25, 100, 20, 0, None, 20, 'poison'),
    #     ('Pin Missile', 'bug', 'physical', 25, 95, 20, 0, 'multi_hit', 100, None),
    #     ('Leer', 'normal', 'status', 0, 100, 30, 0, 'lower_defense', 100, None),
    #     ('Bite', 'normal', 'physical', 60, 100, 25, 0, 'flinch', 30, None),
    #     ('Growl', 'normal', 'status', 0, 100, 40, 0, 'lower_attack', 100, None),
    #     ('Roar', 'normal', 'status', 0, 100, 20, -6, 'force_switch', 100, None),
    #     ('Sing', 'normal', 'status', 0, 55, 15, 0, None, 0, 'sleep'),
    #     ('Supersonic', 'normal', 'status', 0, 55, 20, 0, 'confuse', 100, None),
    #     ('Sonic Boom', 'normal', 'special', 1, 90, 20, 0, 'fixed_20', 100, None),
    #     ('Disable', 'normal', 'status', 0, 100, 20, 0, 'disable', 100, None),
    #     ('Acid', 'poison', 'special', 40, 100, 30, 0, 'lower_defense', 10, None),
    #     ('Ember', 'fire', 'special', 40, 100, 25, 0, None, 10, 'burn'),
    #     ('Flamethrower', 'fire', 'special', 90, 100, 15, 0, None, 10, 'burn'),
    #     ('Mist', 'ice', 'status', 0, 100, 30, 0, 'prevent_stat_lower', 100, None),
    #     ('Water Gun', 'water', 'special', 40, 100, 25, 0, None, 0, None),
    #     ('Hydro Pump', 'water', 'special', 110, 80, 5, 0, None, 0, None),
    #     ('Surf', 'water', 'special', 90, 100, 15, 0, None, 0, None),
    #     ('Ice Beam', 'ice', 'special', 90, 100, 10, 0, None, 10, 'freeze'),
    #     ('Blizzard', 'ice', 'special', 110, 70, 5, 0, None, 10, 'freeze'),
    #     ('Psybeam', 'psychic', 'special', 65, 100, 20, 0, 'confuse', 10, None),
    #     ('Bubble Beam', 'water', 'special', 65, 100, 20, 0, 'lower_speed', 10, None),
    #     ('Aurora Beam', 'ice', 'special', 65, 100, 20, 0, 'lower_attack', 10, None),
    #     ('Hyper Beam', 'normal', 'special', 150, 90, 5, 0, 'recharge', 100, None),
    #     ('Peck', 'flying', 'physical', 35, 100, 35, 0, None, 0, None),
    #     ('Drill Peck', 'flying', 'physical', 80, 100, 20, 0, None, 0, None),
    #     ('Submission', 'fighting', 'physical', 80, 80, 20, 0, 'recoil', 100, None),
    #     ('Low Kick', 'fighting', 'physical', 50, 100, 20, 0, None, 30, None),
    #     ('Counter', 'fighting', 'physical', 1, 100, 20, -5, 'counter', 100, None),
    #     ('Seismic Toss', 'fighting', 'physical', 1, 100, 20, 0, 'level_damage', 100, None),
    #     ('Strength', 'normal', 'physical', 80, 100, 15, 0, None, 0, None),
    #     ('Absorb', 'grass', 'special', 20, 100, 25, 0, 'drain', 100, None),
    #     ('Mega Drain', 'grass', 'special', 40, 100, 15, 0, 'drain', 100, None),
    #     ('Leech Seed', 'grass', 'status', 0, 90, 10, 0, 'leech_seed', 100, None),
    #     ('Growth', 'grass', 'status', 0, 100, 20, 0, 'raise_special', 100, None),
    #     ('Razor Leaf', 'grass', 'physical', 55, 95, 25, 0, 'high_crit', 100, None),
    #     ('Solar Beam', 'grass', 'special', 120, 100, 10, 0, 'charge_turn', 100, None),
    #     ('Poison Powder', 'poison', 'status', 0, 75, 35, 0, None, 0, 'poison'),
    #     ('Stun Spore', 'grass', 'status', 0, 75, 30, 0, None, 0, 'paralysis'),
    #     ('Sleep Powder', 'grass', 'status', 0, 75, 15, 0, None, 0, 'sleep'),
    #     ('Petal Dance', 'grass', 'special', 120, 100, 10, 0, 'confusion_after', 100, None),
    #     ('String Shot', 'bug', 'status', 0, 95, 40, 0, 'lower_speed', 100, None),
    #     ('Dragon Rage', 'dragon', 'special', 1, 100, 10, 0, 'fixed_40', 100, None),
    #     ('Fire Spin', 'fire', 'special', 35, 85, 15, 0, 'trap', 100, None),
    #     ('Thunder Shock', 'electric', 'special', 40, 100, 30, 0, None, 10, 'paralysis'),
    #     ('Thunderbolt', 'electric', 'special', 90, 100, 15, 0, None, 10, 'paralysis'),
    #     ('Thunder Wave', 'electric', 'status', 0, 90, 20, 0, None, 0, 'paralysis'),
    #     ('Thunder', 'electric', 'special', 110, 70, 10, 0, None, 30, 'paralysis'),
    #     ('Rock Throw', 'rock', 'physical', 50, 90, 15, 0, None, 0, None),
    #     ('Earthquake', 'ground', 'physical', 100, 100, 10, 0, None, 0, None),
    #     ('Fissure', 'ground', 'physical', 1, 30, 5, 0, 'ohko', 100, None),
    #     ('Dig', 'ground', 'physical', 80, 100, 10, 0, 'dig', 100, None),
    #     ('Toxic', 'poison', 'status', 0, 90, 10, 0, 'badly_poison', 100, None),
    #     ('Confusion', 'psychic', 'special', 50, 100, 25, 0, 'confuse', 10, None),
    #     ('Psychic', 'psychic', 'special', 90, 100, 10, 0, 'lower_special_defense', 10, None),
    #     ('Hypnosis', 'psychic', 'status', 0, 60, 20, 0, None, 0, 'sleep'),
    #     ('Meditate', 'psychic', 'status', 0, 100, 40, 0, 'raise_attack', 100, None),
    #     ('Agility', 'psychic', 'status', 0, 100, 30, 0, 'sharply_raise_speed', 100, None),
    #     ('Quick Attack', 'normal', 'physical', 40, 100, 30, 1, None, 0, None),
    #     ('Rage', 'normal', 'physical', 20, 100, 20, 0, 'raise_attack_on_hit', 100, None),
    #     ('Teleport', 'psychic', 'status', 0, 100, 20, -6, 'flee', 100, None),
    #     ('Night Shade', 'ghost', 'special', 1, 100, 15, 0, 'level_damage', 100, None),
    #     ('Mimic', 'normal', 'status', 0, 100, 10, 0, 'mimic', 100, None),
    #     ('Screech', 'normal', 'status', 0, 85, 40, 0, 'sharply_lower_defense', 100, None),
    #     ('Double Team', 'normal', 'status', 0, 100, 15, 0, 'raise_evasion', 100, None),
    #     ('Recover', 'normal', 'status', 0, 100, 10, 0, 'heal_half', 100, None),
    #     ('Harden', 'normal', 'status', 0, 100, 30, 0, 'raise_defense', 100, None),
    #     ('Minimize', 'normal', 'status', 0, 100, 10, 0, 'raise_evasion', 100, None),
    #     ('Smokescreen', 'normal', 'status', 0, 100, 20, 0, 'lower_accuracy', 100, None),
    #     ('Confuse Ray', 'ghost', 'status', 0, 100, 10, 0, 'confuse', 100, None),
    #     ('Withdraw', 'water', 'status', 0, 100, 40, 0, 'raise_defense', 100, None),
    #     ('Defense Curl', 'normal', 'status', 0, 100, 40, 0, 'raise_defense', 100, None),
    #     ('Barrier', 'psychic', 'status', 0, 100, 20, 0, 'sharply_raise_defense', 100, None),
    #     ('Light Screen', 'psychic', 'status', 0, 100, 30, 0, 'light_screen', 100, None),
    #     ('Haze', 'ice', 'status', 0, 100, 30, 0, 'reset_stats', 100, None),
    #     ('Reflect', 'psychic', 'status', 0, 100, 20, 0, 'reflect', 100, None),
    #     ('Focus Energy', 'normal', 'status', 0, 100, 30, 0, 'focus_energy', 100, None),
    #     ('Bide', 'normal', 'physical', 1, 100, 10, 1, 'bide', 100, None),
    #     ('Metronome', 'normal', 'status', 0, 100, 10, 0, 'metronome', 100, None),
    #     ('Mirror Move', 'flying', 'status', 0, 100, 20, 0, 'mirror_move', 100, None),
    #     ('Self-Destruct', 'normal', 'physical', 200, 100, 5, 0, 'self_destruct', 100, None),
    #     ('Egg Bomb', 'normal', 'physical', 100, 75, 10, 0, None, 0, None),
    #     ('Lick', 'ghost', 'physical', 30, 100, 30, 0, None, 30, 'paralysis'),
    #     ('Smog', 'poison', 'special', 30, 70, 20, 0, None, 40, 'poison'),
    #     ('Sludge', 'poison', 'special', 65, 100, 20, 0, None, 30, 'poison'),
    #     ('Bone Club', 'ground', 'physical', 65, 85, 20, 0, 'flinch', 10, None),
    #     ('Fire Blast', 'fire', 'special', 110, 85, 5, 0, None, 10, 'burn'),
    #     ('Waterfall', 'water', 'physical', 80, 100, 15, 0, 'flinch', 20, None),
    #     ('Clamp', 'water', 'physical', 35, 85, 15, 0, 'trap', 100, None),
    #     ('Swift', 'normal', 'special', 60, 100, 20, 0, 'never_miss', 100, None),
    #     ('Skull Bash', 'normal', 'physical', 130, 100, 10, 0, 'charge_turn', 100, None),
    #     ('Spike Cannon', 'normal', 'physical', 20, 100, 15, 0, 'multi_hit', 100, None),
    #     ('Constrict', 'normal', 'physical', 10, 100, 35, 0, 'lower_speed', 10, None),
    #     ('Amnesia', 'psychic', 'status', 0, 100, 20, 0, 'sharply_raise_special', 100, None),
    #     ('Kinesis', 'psychic', 'status', 0, 80, 15, 0, 'lower_accuracy', 100, None),
    #     ('Soft-Boiled', 'normal', 'status', 0, 100, 10, 0, 'heal_half', 100, None),
    #     ('High Jump Kick', 'fighting', 'physical', 130, 90, 10, 0, 'crash', 100, None),
    #     ('Glare', 'normal', 'status', 0, 100, 30, 0, None, 0, 'paralysis'),
    #     ('Dream Eater', 'psychic', 'special', 100, 100, 15, 0, 'drain_sleep', 100, None),
    #     ('Poison Gas', 'poison', 'status', 0, 90, 40, 0, None, 0, 'poison'),
    #     ('Barrage', 'normal', 'physical', 15, 85, 20, 0, 'multi_hit', 100, None),
    #     ('Leech Life', 'bug', 'physical', 80, 100, 10, 0, 'drain', 100, None),
    #     ('Lovely Kiss', 'normal', 'status', 0, 75, 10, 0, None, 0, 'sleep'),
    #     ('Sky Attack', 'flying', 'physical', 140, 90, 5, 0, 'charge_turn', 30, None),
    #     ('Transform', 'normal', 'status', 0, 100, 10, 0, 'transform', 100, None),
    #     ('Bubble', 'water', 'special', 40, 100, 30, 0, 'lower_speed', 10, None),
    #     ('Dizzy Punch', 'normal', 'physical', 70, 100, 10, 0, 'confuse', 20, None),
    #     ('Spore', 'grass', 'status', 0, 100, 15, 0, None, 0, 'sleep'),
    #     ('Flash', 'normal', 'status', 0, 100, 20, 0, 'lower_accuracy', 100, None),
    #     ('Psywave', 'psychic', 'special', 1, 100, 15, 0, 'psywave', 100, None),
    #     ('Splash', 'normal', 'status', 0, 100, 40, 0, 'no_effect', 100, None),
    #     ('Acid Armor', 'poison', 'status', 0, 100, 20, 0, 'sharply_raise_defense', 100, None),
    #     ('Crabhammer', 'water', 'physical', 100, 90, 10, 0, 'high_crit', 100, None),
    #     ('Explosion', 'normal', 'physical', 250, 100, 5, 0, 'self_destruct', 100, None),
    #     ('Fury Swipes', 'normal', 'physical', 18, 80, 15, 0, 'multi_hit', 100, None),
    #     ('Bonemerang', 'ground', 'physical', 50, 90, 10, 0, 'two_hit', 100, None),
    #     ('Rest', 'psychic', 'status', 0, 100, 10, 0, 'heal_sleep', 100, None),
    #     ('Rock Slide', 'rock', 'physical', 75, 90, 10, 0, 'flinch', 30, None),
    #     ('Hyper Fang', 'normal', 'physical', 80, 90, 15, 0, 'flinch', 10, None),
    #     ('Sharpen', 'normal', 'status', 0, 100, 30, 0, 'raise_attack', 100, None),
    #     ('Conversion', 'normal', 'status', 0, 100, 30, 0, 'conversion', 100, None),
    #     ('Tri Attack', 'normal', 'special', 80, 100, 10, 0, 'tri_attack', 20, None),
    #     ('Super Fang', 'normal', 'physical', 1, 90, 10, 0, 'half_hp', 100, None),
    #     ('Slash', 'normal', 'physical', 70, 100, 20, 0, 'high_crit', 100, None),
    #     ('Substitute', 'normal', 'status', 0, 100, 10, 0, 'substitute', 100, None),
    #     ('Struggle', 'normal', 'physical', 50, 100, 1, 0, 'recoil', 100, None),
        
    #     # ============================================================================
    #     # CAPACITÉS AJOUTÉES PLUS TARD (si besoin)
    #     # ============================================================================
    #     ('Psycho Cut', 'psychic', 'physical', 70, 100, 20, 0, 'high_crit', 100, None),
    #     ('Psystrike', 'psychic', 'special', 100, 100, 10, 0, None, 0, None),
    #     ('Charm', 'fairy', 'status', 0, 100, 20, 0, 'lower_attack', 100, None),
    #     ('Belly Drum', 'normal', 'status', 0, 100, 10, 0, 'max_attack_half_hp', 100, None),
    #     ('Scary Face', 'normal', 'status', 0, 100, 10, 0, 'lower_speed', 100, None),
    #     ('Dragon Claw', 'dragon', 'physical', 80, 100, 15, 0, None, 0, None),
    #     ('Mud Shot', 'ground', 'special', 55, 95, 15, 0, 'lower_speed', 100, None),
    #     ('Bug Bite', 'bug', 'physical', 60, 100, 20, 0, 'consume_berry', 100, None),
    #     ('Assurance', 'dark', 'physical', 60, 100, 10, 0, 'double_power_if_hit', 100, None),
    #     ('Crush Claw', 'normal', 'physical', 75, 95, 10, 0, 'lower_defense', 50, None),
    #     ('Superpower', 'fighting', 'physical', 120, 100, 5, 0, 'lower_attack_defense', 100, None),
    #     ('Cross Chop', 'fighting', 'physical', 100, 80, 5, 0, 'high_crit', 100, None),
    #     ('Megahorn', 'bug', 'physical', 120, 85, 10, 0, None, 0, None),
    #     ('Moonblast', 'fairy', 'special', 95, 100, 15, 0, 'lower_sp_atk', 30, None),
    #     ('Disarming Voice', 'fairy', 'special', 40, 100, 15, 0, None, 0, None),
    #     ('Sweet Scent', 'normal', 'status', 0, 100, 20, 0, 'lower_evasion', 100, None),
    #     ('Aqua Tail', 'water', 'physical', 90, 90, 10, 0, None, 0, None),
    #     ('Icy Wind', 'ice', 'special', 55, 95, 15, 0, 'lower_speed', 100, None),
    #     ('Inferno', 'fire', 'special', 100, 50, 5, 0, None, 100, 'burn'),
    #     ('Flare Blitz', 'fire', 'physical', 120, 100, 15, 0, 'recoil', 10, 'burn'),
    #     ('Leaf Storm', 'grass', 'special', 130, 90, 5, 0, 'sharply_lower_special_attack', 100, None),
    #     ('Water Pulse', 'water', 'special', 60, 100, 20, 0, 'confuse', 20, None),
    #     ('Sludge Wave', 'poison', 'special', 95, 100, 10, 0, None, 10, 'poison'),
    #     ('Magnet Bomb', 'steel', 'physical', 60, 100, 20, 0, 'never_miss', 100, None),
    #     ('Power Gem', 'rock', 'special', 80, 100, 20, 0, None, 0, None),
    #     ('Play Rough', 'fairy', 'physical', 90, 90, 10, 0, 'lower_attack', 10, None),
    #     ('Astonish', 'ghost', 'physical', 30, 100, 15, 0, 'flinch', 30, None),
    #     ('Air Cutter', 'flying', 'special', 60, 95, 25, 0, 'high_crit', 100, None),
    #     ('Gunk Shot', 'poison', 'physical', 120, 80, 5, 0, None, 30, 'poison'),
    #     ('Bone Rush', 'ground', 'physical', 25, 90, 10, 0, 'multi_hit', 100, None),
    #     ('Shadow Punch', 'ghost', 'physical', 60, 100, 20, 0, 'never_miss', 100, None),
    #     ('Powder Snow', 'ice', 'special', 40, 100, 25, 0, None, 10, 'freeze'),
    #     ('Sunny Day', 'fire', 'status', 0, 100, 5, 0, 'sunny_day', 100, None),
    #     ('Psych Up', 'normal', 'status', 0, 100, 10, 0, 'psych_up', 100, None),
    #     ('Ingrain', 'grass', 'status', 0, 100, 20, 0, 'ingrain', 100, None),
    #     ('Giga Drain', 'grass', 'special', 75, 100, 10, 0, 'drain', 100, None),
    #     ('Twister', 'dragon', 'special', 40, 100, 20, 0, 'flinch', 20, None),
    #     ('Future Sight', 'psychic', 'special', 120, 100, 10, 0, 'future_sight', 100, None),
    #     ('Rapid Spin', 'normal', 'physical', 20, 100, 40, 0, 'raise_speed', 100, None),
    #     ('Rollout', 'rock', 'physical', 30, 90, 20, 0, 'rollout', 100, None),
    #     ('Dynamic Punch', 'fighting', 'physical', 100, 50, 5, 0, 'confuse', 100, None),
    #     ('Foresight', 'normal', 'status', 0, 100, 40, 0, 'foresight', 100, None),
    #     ('Mud-Slap', 'ground', 'special', 20, 100, 10, 0, 'lower_accuracy', 100, None),
    #     ('Low Sweep', 'fighting', 'physical', 65, 100, 20, 0, 'lower_speed', 100, None),
    #     ('Magnitude', 'ground', 'physical', 1, 100, 30, 0, 'random_power', 100, None),
    #     ('Flame Charge', 'fire', 'physical', 50, 100, 20, 0, 'raise_speed', 100, None),
    #     ('Sludge Bomb', 'poison', 'special', 90, 100, 10, 0, None, 30, 'poison'),
    # ]

    #Second version more complete 
    moves_data = [
        ('Brick Break', 'fighting', 'physical', 75, 100, 15, 0, 'break_barrier', 100, None),
        ('Bulk Up', 'fighting', 'status', 0, 100, 20, 0, 'raise_attack_defense', 100, None),
        ('Bullet Punch', 'steel', 'physical', 40, 100, 30, 1, None, 0, None),
        ('Close Combat', 'fighting', 'physical', 120, 100, 5, 0, 'lower_defense_special_defense', 100, None),
        ('Drain Punch', 'fighting', 'physical', 75, 100, 10, 0, 'drain', 100, None),
        ('Earth Power', 'ground', 'special', 90, 100, 10, 0, 'lower_special_defense', 10, None),
        ('Energy Ball', 'grass', 'special', 90, 100, 10, 0, 'lower_special_defense', 10, None),
        ('Facade', 'normal', 'physical', 70, 100, 20, 0, 'double_power_if_statused', 100, None),
        ('Fake Out', 'normal', 'physical', 40, 100, 10, 3, 'flinch', 100, None),
        ('Flame Charge', 'fire', 'physical', 50, 100, 20, 0, 'raise_speed', 100, None),
        ('Flare Blitz', 'fire', 'physical', 120, 100, 15, 0, 'recoil', 10, 'burn'),
        ('Giga Impact', 'normal', 'physical', 150, 90, 5, 0, 'recharge', 100, None),
        ('Ice Punch', 'ice', 'physical', 75, 100, 15, 0, None, 10, 'freeze'),
        ('Iron Head', 'steel', 'physical', 80, 100, 15, 0, 'flinch', 30, None),
        ('Knock Off', 'dark', 'physical', 65, 100, 20, 0, 'remove_item', 100, None),
        ('Leaf Blade', 'grass', 'physical', 90, 100, 15, 0, 'high_crit', 100, None),
        ('Mach Punch', 'fighting', 'physical', 40, 100, 30, 1, None, 0, None),
        ('Play Rough', 'fairy', 'physical', 90, 90, 10, 0, 'lower_attack', 10, None),
        ('Power Whip', 'grass', 'physical', 120, 85, 10, 0, None, 0, None),
        ('Rock Slide', 'rock', 'physical', 75, 90, 10, 0, 'flinch', 30, None),
        ('Shadow Claw', 'ghost', 'physical', 70, 100, 15, 0, 'high_crit', 100, None),
        ('Stone Edge', 'rock', 'physical', 100, 80, 5, 0, 'high_crit', 100, None),
        ('Thunder Punch', 'electric', 'physical', 75, 100, 15, 0, None, 10, 'paralysis'),
        ('U-turn', 'bug', 'physical', 70, 100, 20, 0, 'switch_out', 100, None),
        ('Waterfall', 'water', 'physical', 80, 100, 15, 0, 'flinch', 20, None),
        ('Wild Charge', 'electric', 'physical', 90, 100, 15, 0, 'recoil', 100, None),
        ('X-Scissor', 'bug', 'physical', 80, 100, 15, 0, None, 0, None),
        ('Zen Headbutt', 'psychic', 'physical', 80, 90, 15, 0, 'flinch', 20, None),
        ('Air Slash', 'flying', 'special', 75, 95, 15, 0, 'flinch', 30, None),
        ('Aura Sphere', 'fighting', 'special', 80, 100, 20, 0, 'never_miss', 100, None),
        ('Blast Burn', 'fire', 'special', 150, 90, 5, 0, 'recharge', 100, None),
        ('Dark Pulse', 'dark', 'special', 80, 100, 15, 0, 'flinch', 20, None),
        ('Dragon Pulse', 'dragon', 'special', 85, 100, 10, 0, None, 0, None),
        ('Draco Meteor', 'dragon', 'special', 130, 90, 5, 0, 'sharply_lower_special_attack', 100, None),
        ('Focus Blast', 'fighting', 'special', 120, 70, 5, 0, 'lower_special_defense', 10, None),
        ('Frost Breath', 'ice', 'special', 60, 90, 20, 0, 'always_crit', 100, 'freeze'),
        ('Hydro Cannon', 'water', 'special', 150, 90, 5, 0, 'recharge', 100, None),
        ('Hyper Voice', 'normal', 'special', 90, 100, 10, 0, 'sound_based', 100, None),
        ('Ice Shard', 'ice', 'physical', 40, 100, 30, 1, None, 0, None),
        ('Moonblast', 'fairy', 'special', 95, 100, 15, 0, 'lower_sp_atk', 30, None),
        ('Overheat', 'fire', 'special', 130, 90, 5, 0, 'sharply_lower_special_attack', 100, None),
        ('Shadow Ball', 'ghost', 'special', 80, 100, 15, 0, 'lower_special_defense', 20, None),
        ('Sludge Wave', 'poison', 'special', 95, 100, 10, 0, None, 10, 'poison'),
        ('Thunder', 'electric', 'special', 110, 70, 10, 0, None, 30, 'paralysis'),
        ('Tri Attack', 'normal', 'special', 80, 100, 10, 0, 'tri_attack', 20, None),
        ('Calm Mind', 'psychic', 'status', 0, 100, 20, 0, 'raise_special_attack_special_defense', 100, None),
        ('Cosmic Power', 'psychic', 'status', 0, 100, 20, 0, 'raise_defense_special_defense', 100, None),
        ('Dragon Dance', 'dragon', 'status', 0, 100, 20, 0, 'raise_attack_speed', 100, None),
        ('Hone Claws', 'dark', 'status', 0, 100, 15, 0, 'raise_attack_accuracy', 100, None),
        ('Iron Defense', 'steel', 'status', 0, 100, 15, 0, 'sharply_raise_defense', 100, None),
        ('Nasty Plot', 'dark', 'status', 0, 100, 20, 0, 'sharply_raise_special_attack', 100, None),
        ('Protect', 'normal', 'status', 0, 100, 10, 4, 'protect', 100, None),
        ('Rain Dance', 'water', 'status', 0, 100, 5, 0, 'rain_dance', 100, None),
        ('Reflect', 'psychic', 'status', 0, 100, 20, 0, 'reflect', 100, None),
        ('Rest', 'psychic', 'status', 0, 100, 10, 0, 'heal_sleep', 100, None),
        ('Roost', 'flying', 'status', 0, 100, 10, 0, 'heal_half', 100, None),
        ('Sandstorm', 'rock', 'status', 0, 100, 10, 0, 'sandstorm', 100, None),
        ('Swords Dance', 'normal', 'status', 0, 100, 20, 0, 'sharply_raise_attack', 100, None),
        ('Tailwind', 'flying', 'status', 0, 100, 15, 0, 'tailwind', 100, None),
        ('Toxic Spikes', 'poison', 'status', 0, 100, 20, 0, 'toxic_spikes', 100, None),
        ('Trick Room', 'psychic', 'status', 0, 100, 5, -7, 'trick_room', 100, None),
        ('Will-O-Wisp', 'fire', 'status', 0, 85, 15, 0, None, 0, 'burn'),
        ('Acupressure', 'normal', 'status', 0, 100, 30, 0, 'raise_random_stat_sharply', 100, None),
        ('Baton Pass', 'normal', 'status', 0, 100, 40, 0, 'baton_pass', 100, None),
        ('Bestow', 'normal', 'status', 0, 100, 15, 0, 'give_item', 100, None),
        ('Block', 'normal', 'status', 0, 100, 5, 0, 'block', 100, None),
        ('Camouflage', 'normal', 'status', 0, 100, 20, 0, 'camouflage', 100, None),
        ('Captivate', 'normal', 'status', 0, 100, 20, 0, 'lower_special_attack_opponent', 100, None),
        ('Confide', 'normal', 'status', 0, 100, 20, 0, 'lower_special_attack', 100, None),
        ('Copycat', 'normal', 'status', 0, 100, 20, 0, 'copy_last_move', 100, None),
        ('Defog', 'flying', 'status', 0, 100, 15, 0, 'clear_weather_hazards', 100, None),
        ('Destiny Bond', 'ghost', 'status', 0, 100, 5, -5, 'destiny_bond', 100, None),
        ('Detect', 'fighting', 'status', 0, 100, 5, 4, 'protect', 100, None),
        ('Double Team', 'normal', 'status', 0, 100, 15, 0, 'raise_evasion', 100, None),
        ('Echoed Voice', 'normal', 'special', 40, 100, 15, 0, 'increase_power_repeated', 100, None),
        ('Electroweb', 'electric', 'special', 55, 95, 15, 0, 'lower_speed', 100, None),
        ('Embargo', 'dark', 'status', 0, 100, 15, 0, 'embargo', 100, None),
        ('Encore', 'normal', 'status', 0, 100, 5, 0, 'encore', 100, None),
        ('Endure', 'normal', 'status', 0, 100, 10, 4, 'endure', 100, None),
        ('Fairy Lock', 'fairy', 'status', 0, 100, 10, 0, 'fairy_lock', 100, None),
        ('Feather Dance', 'flying', 'status', 0, 100, 15, 0, 'sharply_lower_attack', 100, None),
        ('Feint', 'normal', 'physical', 30, 100, 10, 2, 'break_protect', 100, None),
        ('Follow Me', 'normal', 'status', 0, 100, 20, 3, 'redirect_attacks', 100, None),
        ('Foul Play', 'dark', 'physical', 95, 100, 15, 0, 'use_opponent_attack', 100, None),
        ('Freeze-Dry', 'ice', 'special', 70, 100, 20, 0, 'super_effective_water', 10, 'freeze'),
        ('Grassy Terrain', 'grass', 'status', 0, 100, 10, 0, 'grassy_terrain', 100, None),
        ('Gravity', 'psychic', 'status', 0, 100, 5, 0, 'gravity', 100, None),
        ('Heal Bell', 'normal', 'status', 0, 100, 5, 0, 'cure_team_status', 100, None),
        ('Heal Pulse', 'psychic', 'status', 0, 100, 10, 0, 'heal_target_50', 100, None),
        ('Helping Hand', 'normal', 'status', 0, 100, 20, 5, 'boost_ally_power', 100, None),
        ('Hold Hands', 'normal', 'status', 0, 100, 40, 0, 'double_evasion', 100, None),
        ('Howl', 'normal', 'status', 0, 100, 40, 0, 'raise_attack', 100, None),
        ('Hyperspace Hole', 'psychic', 'special', 80, 100, 5, 0, 'bypass_protect', 100, None),
        ('Icy Wind', 'ice', 'special', 55, 95, 15, 0, 'lower_speed', 100, None),
        ('Imprison', 'psychic', 'status', 0, 100, 10, 0, 'imprison', 100, None),
        ('Incinerate', 'fire', 'special', 60, 100, 15, 0, 'destroy_berry', 100, None),
        ('Instruct', 'psychic', 'status', 0, 100, 15, 0, 'instruct', 100, None),
        ('Ion Deluge', 'electric', 'status', 0, 100, 5, 0, 'ion_deluge', 100, None),
        ('King\'s Shield', 'steel', 'status', 0, 100, 10, 4, 'protect_lower_attack', 100, None),
        ('Laser Focus', 'normal', 'status', 0, 100, 30, 0, 'guarantee_crit_next', 100, None),
        ('Lucky Chant', 'normal', 'status', 0, 100, 30, 0, 'lucky_chant', 100, None),
        ('Magic Room', 'psychic', 'status', 0, 100, 10, 0, 'magic_room', 100, None),
        ('Mat Block', 'fighting', 'status', 0, 100, 10, 4, 'protect_ally', 100, None),
        ('Me First', 'normal', 'status', 0, 100, 20, 0, 'use_move_first', 100, None),
        ('Misty Terrain', 'fairy', 'status', 0, 100, 10, 0, 'misty_terrain', 100, None),
        ('Nature Power', 'normal', 'status', 0, 100, 20, 0, 'nature_power', 100, None),
        ('Nightmare', 'ghost', 'status', 0, 100, 15, 0, 'nightmare', 100, None),
        ('Pain Split', 'normal', 'status', 0, 100, 20, 0, 'pain_split', 100, None),
        ('Photon Geyser', 'psychic', 'special', 100, 100, 5, 0, 'use_higher_stat', 100, None),
        ('Pluck', 'flying', 'physical', 60, 100, 20, 0, 'steal_berry', 100, None),
        ('Power Split', 'psychic', 'status', 0, 100, 10, 0, 'power_split', 100, None),
        ('Power Trick', 'psychic', 'status', 0, 100, 10, 0, 'swap_attack_defense', 100, None),
        ('Psychic Terrain', 'psychic', 'status', 0, 100, 10, 0, 'psychic_terrain', 100, None),
        ('Quash', 'dark', 'status', 0, 100, 15, 0, 'delay_opponent_move', 100, None),
        ('Quick Guard', 'fighting', 'status', 0, 100, 15, 3, 'protect_priority', 100, None),
        ('Rage Powder', 'bug', 'status', 0, 100, 20, 2, 'redirect_attacks', 100, None),
        ('Recycle', 'normal', 'status', 0, 100, 10, 0, 'recycle_item', 100, None),
        ('Reflect Type', 'normal', 'status', 0, 100, 15, 0, 'reflect_type', 100, None),
        ('Relic Song', 'normal', 'special', 75, 100, 10, 0, 'maybe_sleep', 10, None),
        ('Retaliate', 'normal', 'physical', 70, 100, 5, 0, 'double_power_if_ally_fainted', 100, None),
        ('Revelation Dance', 'normal', 'special', 90, 100, 15, 0, 'use_user_type', 100, None),
        ('Rototiller', 'ground', 'status', 0, 100, 10, 0, 'raise_special_attack_special_defense', 100, None),
        ('Sacred Fire', 'fire', 'physical', 100, 95, 5, 0, None, 50, 'burn'),
        ('Scald', 'water', 'special', 80, 100, 15, 0, None, 30, 'burn'),
        ('Shell Smash', 'normal', 'status', 0, 100, 15, 0, 'raise_attack_special_attack_speed_sharply_lower_defense_special_defense', 100, None),
        ('Shift Gear', 'steel', 'status', 0, 100, 10, 0, 'raise_attack_speed_sharply', 100, None),
        ('Signal Beam', 'bug', 'special', 75, 100, 15, 0, 'confuse', 10, None),
        ('Simple Beam', 'normal', 'status', 0, 100, 15, 0, 'simple_beam', 100, None),
        ('Skill Swap', 'psychic', 'status', 0, 100, 10, 0, 'skill_swap', 100, None),
        ('Slack Off', 'normal', 'status', 0, 100, 10, 0, 'heal_half', 100, None),
        ('Smack Down', 'rock', 'physical', 50, 100, 15, 0, 'remove_flying_type', 100, None),
        ('Snarl', 'dark', 'special', 55, 95, 15, 0, 'lower_special_attack', 100, None),
        ('Snatch', 'dark', 'status', 0, 100, 10, 4, 'snatch', 100, None),
        ('Spite', 'ghost', 'status', 0, 100, 10, 0, 'lower_move_pp', 100, None),
        ('Spotlight', 'normal', 'status', 0, 100, 15, 3, 'redirect_attacks', 100, None),
        ('Stealth Rock', 'rock', 'status', 0, 100, 20, 0, 'stealth_rock', 100, None),
        ('Sticky Web', 'bug', 'status', 0, 100, 20, 0, 'sticky_web', 100, None),
        ('Storm Throw', 'fighting', 'physical', 60, 100, 10, 0, 'always_crit', 100, None),
        ('Struggle Bug', 'bug', 'special', 50, 100, 20, 0, 'lower_special_attack', 100, None),
        ('Synchronoise', 'psychic', 'special', 120, 100, 10, 0, 'sync_type_damage', 100, None),
        ('Tail Slap', 'normal', 'physical', 25, 85, 10, 0, 'multi_hit', 100, None),
        ('Tar Shot', 'rock', 'status', 0, 100, 15, 0, 'lower_speed', 100, None),
        ('Taunt', 'dark', 'status', 0, 100, 20, 0, 'taunt', 100, None),
        ('Tearful Look', 'normal', 'status', 0, 100, 20, 0, 'lower_attack_special_attack', 100, None),
        ('Telekinesis', 'psychic', 'status', 0, 100, 15, 0, 'telekinesis', 100, None),
        ('Throat Chop', 'dark', 'physical', 80, 100, 15, 0, 'prevent_sound_moves', 100, None),
        ('Torment', 'dark', 'status', 0, 100, 15, 0, 'torment', 100, None),
        ('Toxic Thread', 'poison', 'status', 0, 100, 20, 0, 'lower_speed', 100, 'poison'),
        ('Trick', 'psychic', 'status', 0, 100, 10, 0, 'swap_items', 100, None),
        ('Uproar', 'normal', 'special', 90, 100, 10, 0, 'uproar', 100, None),
        ('Venom Drench', 'poison', 'status', 0, 100, 20, 0, 'venom_drench', 100, None),
        ('Wide Guard', 'rock', 'status', 0, 100, 10, 3, 'protect_ally_multi', 100, None),
        ('Wonder Room', 'psychic', 'status', 0, 100, 10, 0, 'wonder_room', 100, None),
        ('Work Up', 'normal', 'status', 0, 100, 30, 0, 'raise_attack_special_attack', 100, None),
        ('Worry Seed', 'grass', 'status', 0, 100, 10, 0, 'worry_seed', 100, None),
        ('Wrap', 'normal', 'physical', 15, 90, 20, 0, 'trap', 100, None),
        ('Wring Out', 'normal', 'special', 1, 100, 5, 0, 'more_damage_if_hp', 100, None),
        ('Zen Headbutt', 'psychic', 'physical', 80, 90, 15, 0, 'flinch', 20, None),
        ('Sludge Bomb', 'poison', 'special', 90, 100, 10, 0, None, 30, 'poison'),
        ('Icicle Spear', 'ice', 'physical', 25, 100, 30, 0, 'multi_hit', 100, None),
        ('Mean Look', 'normal', 'status', 0, 100, 5, 0, 'block', 100, None),
        ('Curse', 'ghost', 'status', 0, 100, 10, 0, 'curse', 100, None),
        ('Spark', 'electric', 'physical', 65, 100, 20, 0, None, 30, 'paralysis'),
        ('SmokeScreen', 'normal', 'status', 0, 100, 20, 0, 'lower_accuracy', 100, None),
        ('Rock Throw', 'rock', 'physical', 50, 90, 15, 0, None, 0, None),
        ('Rock Blast', 'rock', 'physical', 50, 90, 15, 0, None, 0, None),
        ('Struggle', 'normal', 'physical', 50, None, 1, 0, 'recoil_25', 100, None),
    ]

    moves_dict = {}
    for move_data in moves_data:
        name, type_name, category, power, accuracy, pp, priority, effect, effect_chance, inflicts_status = move_data
        
        move, created = PokemonMove.objects.get_or_create(
            name=name,
            defaults={
                'type': types_dict[type_name],
                'category': category,
                'power': power,
                'accuracy': accuracy,
                'pp': pp,
                'max_pp': pp,
                'priority': priority,
                'effect': effect,
                'effect_chance': effect_chance,
                'inflicts_status': inflicts_status
            }
        )
        moves_dict[name] = move
        if created:
            logging.info(f"  [+] Capacité créée: {name}")
    
    logging.info(f"[+] {len(moves_dict)} capacités créées/vérifiées")
    
    
    # ============================================================================
    # ÉTAPE 4: CRÉER LES POKÉMON
    # ============================================================================
    
    logging.info("\n[*] Création des Pokémon...")
    
    # Données des Pokémon
    # Format: (nom, numéro_pokedex, type_primaire, type_secondaire, hp, atk, def, sp_atk, sp_def, speed, taux_capture, exp_base)
    pokemon_data = [
        ("Abra", 63, "psychic", None, 25, 20, 15, 105, 55, 90, 200, 62),
        ("Aerodactyl", 142, "rock", "flying", 80, 105, 65, 60, 75, 130, 45, 180),
        ("Alakazam", 65, "psychic", None, 55, 50, 45, 135, 95, 120, 50, 250),
        ("Arbok", 24, "poison", None, 60, 95, 69, 65, 79, 80, 90, 157),
        ("Arcanine", 59, "fire", None, 90, 110, 80, 100, 80, 95, 75, 194),
        ("Articuno", 144, "ice", "flying", 90, 85, 100, 95, 125, 85, 3, 290),
        ("Beedrill", 15, "bug", "poison", 65, 90, 40, 45, 80, 75, 45, 198),
        ("Bellsprout", 69, "grass", "poison", 50, 75, 35, 70, 30, 40, 255, 60),
        ("Blastoise", 9, "water", None, 79, 83, 100, 85, 105, 78, 45, 265),
        ("Bulbasaur", 1, "grass", "poison", 45, 49, 49, 65, 65, 45, 45, 64),
        ("Butterfree", 12, "bug", "flying", 60, 45, 50, 90, 80, 70, 45, 198),
        ("Caterpie", 10, "bug", None, 45, 30, 35, 20, 20, 45, 255, 39),
        ("Chansey", 113, "normal", None, 250, 5, 5, 35, 105, 50, 30, 395),
        ("Charizard", 6, "fire", "flying", 78, 84, 78, 109, 85, 100, 45, 267),
        ("Charmander", 4, "fire", None, 39, 52, 43, 60, 50, 65, 45, 62),
        ("Charmeleon", 5, "fire", None, 58, 64, 58, 80, 65, 80, 45, 142),
        ("Clefable", 36, "fairy", None, 95, 70, 73, 95, 90, 60, 25, 242),
        ("Clefairy", 35, "fairy", None, 70, 45, 48, 60, 65, 35, 150, 113),
        ("Cloyster", 91, "water", "ice", 50, 95, 180, 85, 45, 70, 60, 184),
        ("Cubone", 104, "ground", None, 50, 50, 95, 40, 50, 35, 190, 64),
        ("Dewgong", 87, "water", "ice", 90, 70, 80, 70, 95, 70, 75, 166),
        ("Diglett", 50, "ground", None, 10, 55, 25, 35, 45, 95, 255, 53),
        ("Ditto", 132, "normal", None, 48, 48, 48, 48, 48, 48, 35, 101),
        ("Dodrio", 85, "normal", "flying", 60, 110, 70, 60, 60, 100, 45, 165),
        ("Doduo", 84, "normal", "flying", 35, 85, 45, 35, 35, 75, 190, 62),
        ("Dragonair", 148, "dragon", None, 61, 84, 65, 70, 70, 70, 45, 147),
        ("Dragonite", 149, "dragon", "flying", 91, 134, 95, 100, 100, 80, 45, 300),
        ("Dratini", 147, "dragon", None, 41, 64, 45, 50, 50, 50, 45, 60),
        ("Drowzee", 96, "psychic", None, 60, 48, 45, 43, 90, 42, 190, 66),
        ("Dugtrio", 51, "ground", None, 35, 100, 50, 50, 70, 120, 50, 149),
        ("Eevee", 133, "normal", None, 55, 55, 50, 45, 65, 55, 45, 65),
        ("Ekans", 23, "poison", None, 35, 60, 44, 40, 54, 55, 255, 58),
        ("Electabuzz", 125, "electric", None, 65, 83, 57, 95, 85, 105, 45, 172),
        ("Electrode", 101, "electric", None, 60, 50, 70, 80, 80, 150, 60, 172),
        ("Exeggcute", 102, "grass", "psychic", 60, 40, 80, 60, 45, 40, 90, 65),
        ("Exeggutor", 103, "grass", "psychic", 95, 95, 85, 125, 75, 55, 45, 186),
        ("Farfetch'd", 83, "normal", "flying", 52, 90, 55, 58, 62, 60, 45, 132),
        ("Fearow", 22, "normal", "flying", 65, 90, 65, 61, 61, 100, 90, 155),
        ("Flareon", 136, "fire", None, 65, 130, 60, 95, 110, 65, 45, 184),
        ("Gastly", 92, "ghost", "poison", 30, 35, 30, 100, 35, 80, 190, 62),
        ("Gengar", 94, "ghost", "poison", 60, 65, 60, 130, 75, 110, 45, 250),
        ("Geodude", 74, "rock", "ground", 40, 80, 100, 30, 30, 20, 255, 60),
        ("Gloom", 44, "grass", "poison", 60, 65, 70, 85, 75, 40, 120, 138),
        ("Golbat", 42, "poison", "flying", 75, 80, 70, 65, 75, 90, 90, 159),
        ("Goldeen", 118, "water", None, 45, 67, 60, 35, 50, 63, 225, 64),
        ("Golduck", 55, "water", None, 80, 82, 78, 95, 80, 85, 75, 175),
        ("Golem", 76, "rock", "ground", 80, 120, 130, 55, 65, 45, 45, 248),
        ("Graveler", 75, "rock", "ground", 55, 95, 115, 45, 45, 35, 120, 137),
        ("Grimer", 88, "poison", None, 80, 80, 50, 40, 50, 25, 190, 65),
        ("Growlithe", 58, "fire", None, 55, 70, 45, 70, 50, 60, 190, 70),
        ("Gyarados", 130, "water", "flying", 95, 125, 79, 60, 100, 81, 45, 189),
        ("Haunter", 93, "ghost", "poison", 45, 50, 45, 115, 55, 95, 90, 142),
        ("Hitmonchan", 107, "fighting", None, 50, 105, 79, 35, 110, 76, 45, 159),
        ("Hitmonlee", 106, "fighting", None, 50, 120, 53, 35, 110, 87, 45, 159),
        ("Horsea", 116, "water", None, 30, 40, 70, 70, 25, 60, 225, 59),
        ("Hypno", 97, "psychic", None, 85, 73, 70, 73, 115, 67, 75, 169),
        ("Ivysaur", 2, "grass", "poison", 60, 62, 63, 80, 80, 60, 45, 142),
        ("Jigglypuff", 39, "normal", "fairy", 115, 45, 20, 45, 25, 20, 170, 95),
        ("Jolteon", 135, "electric", None, 65, 65, 60, 110, 95, 130, 45, 184),
        ("Jynx", 124, "ice", "psychic", 65, 50, 35, 115, 95, 95, 45, 159),
        ("Kabutops", 141, "rock", "water", 60, 115, 105, 65, 70, 80, 45, 173),
        ("Kabuto", 140, "rock", "water", 30, 80, 90, 55, 45, 55, 45, 71),
        ("Kadabra", 64, "psychic", None, 40, 35, 30, 120, 70, 105, 100, 140),
        ("Kakuna", 14, "bug", "poison", 45, 25, 50, 25, 25, 35, 120, 72),
        ("Kangaskhan", 115, "normal", None, 105, 95, 80, 40, 80, 90, 45, 172),
        ("Kingler", 99, "water", None, 55, 130, 115, 50, 50, 75, 60, 166),
        ("Koffing", 109, "poison", None, 40, 65, 95, 60, 45, 35, 190, 68),
        ("Krabby", 98, "water", None, 30, 105, 90, 25, 25, 50, 225, 65),
        ("Lapras", 131, "water", "ice", 130, 85, 80, 85, 95, 60, 45, 187),
        ("Lickitung", 108, "normal", None, 90, 55, 75, 60, 75, 30, 45, 77),
        ("Machamp", 68, "fighting", None, 90, 130, 80, 65, 85, 55, 45, 253),
        ("Machoke", 67, "fighting", None, 80, 100, 70, 50, 60, 45, 90, 142),
        ("Machop", 66, "fighting", None, 70, 80, 50, 35, 35, 35, 180, 61),
        ("Magikarp", 129, "water", None, 20, 10, 55, 15, 20, 80, 255, 40),
        ("Magmar", 126, "fire", None, 65, 95, 57, 100, 85, 93, 45, 173),
        ("Magnemite", 81, "electric", "steel", 25, 35, 70, 95, 55, 45, 190, 65),
        ("Magneton", 82, "electric", "steel", 50, 60, 95, 120, 70, 70, 60, 163),
        ("Mankey", 56, "fighting", None, 40, 80, 35, 35, 45, 70, 190, 61),
        ("Marowak", 105, "ground", None, 60, 80, 110, 50, 80, 45, 75, 149),
        ("Meowth", 52, "normal", None, 40, 45, 35, 40, 40, 90, 255, 58),
        ("Metapod", 11, "bug", None, 50, 20, 55, 25, 25, 30, 120, 72),
        ("Mew", 151, "psychic", None, 100, 100, 100, 100, 100, 100, 45, 300),
        ("Mewtwo", 150, "psychic", None, 106, 110, 90, 154, 90, 130, 3, 340),
        ("Moltres", 146, "fire", "flying", 90, 100, 90, 125, 85, 90, 3, 290),
        ("Mr. Mime", 122, "psychic", "fairy", 40, 45, 65, 100, 120, 90, 45, 161),
        ("Muk", 89, "poison", None, 105, 105, 75, 65, 100, 50, 75, 175),
        ("Nidoking", 34, "poison", "ground", 81, 102, 77, 85, 75, 85, 45, 253),
        ("Nidoqueen", 31, "poison", "ground", 90, 92, 87, 75, 85, 76, 45, 253),
        ("Nidoran♀", 29, "poison", None, 55, 47, 52, 40, 40, 41, 235, 55),
        ("Nidoran♂", 32, "poison", None, 46, 57, 40, 40, 40, 50, 235, 55),
        ("Nidorina", 30, "poison", None, 70, 62, 67, 55, 55, 56, 120, 128),
        ("Nidorino", 33, "poison", None, 61, 72, 57, 55, 55, 65, 120, 128),
        ("Ninetales", 38, "fire", None, 73, 76, 75, 81, 100, 100, 75, 177),
        ("Oddish", 43, "grass", "poison", 45, 50, 55, 75, 65, 30, 255, 64),
        ("Omanyte", 138, "rock", "water", 35, 40, 100, 90, 55, 35, 45, 71),
        ("Omastar", 139, "rock", "water", 70, 60, 125, 115, 70, 55, 45, 173),
        ("Onix", 95, "rock", "ground", 35, 45, 160, 30, 45, 70, 45, 77),
        ("Paras", 46, "bug", "grass", 35, 70, 55, 45, 55, 25, 190, 57),
        ("Parasect", 47, "bug", "grass", 60, 95, 80, 60, 80, 30, 75, 142),
        ("Persian", 53, "normal", None, 65, 70, 60, 65, 65, 115, 90, 154),
        ("Pidgeot", 18, "normal", "flying", 83, 80, 75, 70, 70, 101, 45, 240),
        ("Pidgeotto", 17, "normal", "flying", 63, 60, 55, 50, 50, 71, 120, 122),
        ("Pidgey", 16, "normal", "flying", 40, 45, 40, 35, 35, 56, 255, 50),
        ("Pikachu", 25, "electric", None, 35, 55, 40, 50, 50, 90, 190, 112),
        ("Pinsir", 127, "bug", None, 65, 125, 100, 55, 70, 85, 45, 175),
        ("Poliwag", 60, "water", None, 40, 50, 40, 40, 40, 90, 255, 60),
        ("Poliwhirl", 61, "water", None, 65, 65, 65, 50, 50, 90, 120, 135),
        ("Poliwrath", 62, "water", "fighting", 90, 95, 95, 70, 90, 70, 45, 255),
        ("Ponyta", 77, "fire", None, 50, 85, 55, 65, 65, 90, 190, 82),
        ("Porygon", 137, "normal", None, 65, 60, 70, 85, 75, 40, 45, 79),
        ("Primeape", 57, "fighting", None, 65, 105, 60, 60, 70, 95, 75, 159),
        ("Psyduck", 54, "water", None, 50, 52, 48, 65, 50, 55, 190, 64),
        ("Raichu", 26, "electric", None, 60, 90, 55, 90, 80, 110, 75, 243),
        ("Rapidash", 78, "fire", None, 65, 100, 70, 80, 80, 105, 60, 175),
        ("Raticate", 20, "normal", None, 55, 81, 60, 50, 70, 97, 127, 145),
        ("Rattata", 19, "normal", None, 30, 56, 35, 25, 35, 72, 255, 51),
        ("Rhydon", 112, "ground", "rock", 105, 130, 120, 45, 45, 40, 60, 170),
        ("Rhyhorn", 111, "ground", "rock", 80, 85, 95, 30, 30, 25, 120, 69),
        ("Sandshrew", 27, "ground", None, 50, 75, 85, 20, 30, 40, 255, 60),
        ("Sandslash", 28, "ground", None, 75, 100, 110, 45, 55, 65, 90, 158),
        ("Scyther", 123, "bug", "flying", 70, 110, 80, 55, 80, 105, 45, 100),
        ("Seadra", 117, "water", None, 55, 65, 95, 95, 45, 85, 75, 154),
        ("Seaking", 119, "water", None, 80, 92, 65, 65, 80, 68, 60, 158),
        ("Seel", 86, "water", None, 65, 45, 55, 45, 70, 45, 190, 65),
        ("Shellder", 90, "water", None, 30, 65, 100, 45, 25, 40, 190, 61),
        ("Slowbro", 80, "water", "psychic", 95, 75, 110, 100, 80, 30, 75, 172),
        ("Slowpoke", 79, "water", "psychic", 90, 65, 65, 40, 40, 15, 190, 63),
        ("Snorlax", 143, "normal", None, 160, 110, 65, 65, 110, 30, 25, 189),
        ("Spearow", 21, "normal", "flying", 40, 60, 30, 31, 31, 70, 255, 52),
        ("Squirtle", 7, "water", None, 44, 48, 65, 50, 64, 43, 45, 63),
        ("Starmie", 121, "water", "psychic", 60, 75, 85, 100, 85, 115, 60, 182),
        ("Staryu", 120, "water", None, 30, 45, 55, 70, 55, 85, 225, 68),
        ("Tangela", 114, "grass", None, 65, 55, 115, 100, 40, 60, 45, 87),
        ("Tauros", 128, "normal", None, 75, 100, 95, 40, 70, 110, 45, 172),
        ("Tentacool", 72, "water", "poison", 40, 40, 35, 50, 100, 70, 190, 67),
        ("Tentacruel", 73, "water", "poison", 80, 70, 65, 80, 120, 100, 60, 180),
        ("Vaporeon", 134, "water", None, 130, 65, 60, 110, 95, 65, 45, 184),
        ("Venomoth", 49, "bug", "poison", 70, 65, 60, 90, 75, 90, 75, 158),
        ("Venonat", 48, "bug", "poison", 60, 55, 50, 40, 55, 45, 190, 61),
        ("Venusaur", 3, "grass", "poison", 80, 82, 83, 100, 100, 80, 45, 263),
        ("Victreebel", 71, "grass", "poison", 80, 105, 65, 100, 70, 70, 45, 245),
        ("Vileplume", 45, "grass", "poison", 75, 80, 85, 110, 90, 50, 45, 245),
        ("Voltorb", 100, "electric", None, 40, 30, 50, 55, 55, 100, 190, 66),
        ("Vulpix", 37, "fire", None, 38, 41, 40, 50, 65, 65, 190, 60),
        ("Wartortle", 8, "water", None, 59, 63, 80, 65, 80, 58, 45, 142),
        ("Weedle", 13, "bug", "poison", 40, 35, 30, 20, 20, 50, 255, 39),
        ("Weepinbell", 70, "grass", "poison", 65, 90, 50, 85, 45, 55, 120, 137),
        ("Weezing", 110, "poison", None, 65, 90, 120, 85, 70, 60, 60, 173),
        ("Wigglytuff", 40, "normal", "fairy", 140, 70, 45, 85, 50, 45, 50, 196),
        ("Zapdos", 145, "electric", "flying", 90, 90, 85, 125, 90, 100, 3, 290),
        ("Zubat", 41, "poison", "flying", 40, 45, 35, 30, 40, 55, 255, 49),
    ]
    
    pokemon_dict = {}
    for poke_data in pokemon_data:
        name, dex_num, primary, secondary, hp, atk, defense, sp_atk, sp_def, speed, catch, exp = poke_data
        
        pokemon, created = Pokemon.objects.get_or_create(
            pokedex_number=dex_num,
            defaults={
                'name': name,
                'primary_type': types_dict[primary],
                'secondary_type': types_dict[secondary] if secondary else None,
                'base_hp': hp,
                'base_attack': atk,
                'base_defense': defense,
                'base_special_attack': sp_atk,
                'base_special_defense': sp_def,
                'base_speed': speed,
                'catch_rate': catch,
                'base_experience': exp,
                'growth_rate': 'medium_fast'
            }
        )
        pokemon_dict[name] = pokemon
        if created:
            logging.info(f"  [+] Pokémon créé: #{dex_num:03d} {name}")
    
    logging.info(f"[+] {len(pokemon_dict)} Pokémon créés/vérifiés")

    # ============================================================================
    # ÉTAPE X: CRÉER LES ÉVOLUTIONS DES POKÉMON
    # ============================================================================

    logging.info("\n[*] Création des évolutions Pokémon...")

    # Common evolution items in Gen 1
    common_evolution_items = {
        "Fire Stone": "fire_stone",
        "Water Stone": "water_stone",
        "Thunder Stone": "thunder_stone",
        "Leaf Stone": "leaf_stone",
        "Moon Stone": "moon_stone",
    }

    # Evolution data for Gen 1 Pokémon
    # Format: (method, level, required_item, evolved_name)
    pokemon_evolution_data = {
        "Bulbasaur": [("level", 16, None, "Ivysaur")],
        "Ivysaur": [("level", 32, None, "Venusaur")],
        "Charmander": [("level", 16, None, "Charmeleon")],
        "Charmeleon": [("level", 36, None, "Charizard")],
        "Squirtle": [("level", 16, None, "Wartortle")],
        "Wartortle": [("level", 36, None, "Blastoise")],
        "Caterpie": [("level", 7, None, "Metapod")],
        "Metapod": [("level", 10, None, "Butterfree")],
        "Weedle": [("level", 7, None, "Kakuna")],
        "Kakuna": [("level", 10, None, "Beedrill")],
        "Pidgey": [("level", 18, None, "Pidgeotto")],
        "Pidgeotto": [("level", 36, None, "Pidgeot")],
        "Rattata": [("level", 20, None, "Raticate")],
        "Spearow": [("level", 20, None, "Fearow")],
        "Ekans": [("level", 22, None, "Arbok")],
        "Pikachu": [("stone", None, "Thunder Stone", "Raichu")],
        "Sandshrew": [("level", 22, None, "Sandslash")],
        "Nidoran♀": [("level", 16, None, "Nidorina")],
        "Nidorina": [("stone", None, "Moon Stone", "Nidoqueen")],
        "Nidoran♂": [("level", 16, None, "Nidorino")],
        "Nidorino": [("stone", None, "Moon Stone", "Nidoking")],
        "Clefairy": [("stone", None, "Moon Stone", "Clefable")],
        "Vulpix": [("stone", None, "Fire Stone", "Ninetales")],
        "Jigglypuff": [("stone", None, "Moon Stone", "Wigglytuff")],
        "Zubat": [("level", 22, None, "Golbat")],
        "Oddish": [("level", 21, None, "Gloom")],
        "Gloom": [("stone", None, "Leaf Stone", "Vileplume")],
        "Paras": [("level", 24, None, "Parasect")],
        "Venonat": [("level", 31, None, "Venomoth")],
        "Diglett": [("level", 26, None, "Dugtrio")],
        "Meowth": [("level", 28, None, "Persian")],
        "Psyduck": [("level", 33, None, "Golduck")],
        "Mankey": [("level", 28, None, "Primeape")],
        "Poliwag": [("level", 25, None, "Poliwhirl")],
        "Poliwhirl": [("stone", None, "Water Stone", "Poliwrath")],
        "Abra": [("level", 16, None, "Kadabra")],
        "Machop": [("level", 28, None, "Machoke")],
        "Bellsprout": [("level", 21, None, "Weepinbell")],
        "Weepinbell": [("stone", None, "Leaf Stone", "Victreebel")],
        "Tentacool": [("level", 30, None, "Tentacruel")],
        "Geodude": [("level", 25, None, "Graveler")],
        "Ponyta": [("level", 40, None, "Rapidash")],
        "Slowpoke": [("level", 37, None, "Slowbro")],
        "Magnemite": [("level", 30, None, "Magneton")],
        "Doduo": [("level", 31, None, "Dodrio")],
        "Seel": [("level", 34, None, "Dewgong")],
        "Grimer": [("level", 38, None, "Muk")],
        "Shellder": [("level", 36, None, "Cloyster")],
        "Gastly": [("level", 25, None, "Haunter")],
        "Drowzee": [("level", 26, None, "Hypno")],
        "Krabby": [("level", 28, None, "Kingler")],
        "Voltorb": [("level", 30, None, "Electrode")],
        "Exeggcute": [("stone", None, "Leaf Stone", "Exeggutor")],
        "Cubone": [("level", 28, None, "Marowak")],
        "Koffing": [("level", 35, None, "Weezing")],
        "Rhyhorn": [("level", 42, None, "Rhydon")],
        "Horsea": [("level", 32, None, "Seadra")],
        "Goldeen": [("level", 33, None, "Seaking")],
        "Staryu": [("stone", None, "Water Stone", "Starmie")],
        "Magikarp": [("level", 20, None, "Gyarados")],
        "Omanyte": [("level", 40, None, "Omastar")],
        "Kabuto": [("level", 40, None, "Kabutops")],
        "Dratini": [("level", 30, None, "Dragonair")],
        "Dragonair": [("level", 55, None, "Dragonite")],
        "Eevee": [
            ("stone", None, "Water Stone", "Vaporeon"),
            ("stone", None, "Thunder Stone", "Jolteon"),
            ("stone", None, "Fire Stone", "Flareon"),
        ],
    }

    # Dictionnaire pour mapper les noms d'objets à leurs instances
    item_dict = {}
    for item_name in common_evolution_items.values():
        item_obj, created = Item.objects.get_or_create(name=item_name)
        item_dict[item_name] = item_obj
        if created:
            logging.info(f"  [+] Objet créé: {item_name}")

    for pokemon_name, evolutions in pokemon_evolution_data.items():
        try:
            pokemon = Pokemon.objects.get(name=pokemon_name)
            for method, level, required_item_name, evolved_name in evolutions:
                evolved_pokemon = Pokemon.objects.get(name=evolved_name)
                required_item = item_dict.get(common_evolution_items.get(required_item_name)) if required_item_name else None

                PokemonEvolution.objects.get_or_create(
                    pokemon=pokemon,
                    evolves_to=evolved_pokemon,
                    method=method,
                    level=level,
                    required_item=required_item
                )
                logging.info(f"  [+] Évolution créée: {pokemon_name} -> {evolved_name} (Méthode: {method}, Niveau: {level}, Objet: {required_item_name})")
        except Pokemon.DoesNotExist as e:
            logging.warning(f"  [!] Pokémon non trouvé: {e}")


    logging.info(f"[+] Évolution des Pokémon configurée")


    # ============================================================================
    # ÉTAPE Y: CRÉER LES CAPACITÉS APPRISES PAR LES POKÉMON
    # ============================================================================

    logging.info("\n[*] Création des capacités apprises par les Pokémon...")

    learnable_moves_data = {
        'Bulbasaur': [
            ('Tackle', 1),
            ('Growl', 7),
            ('Leech Seed', 13),
            ('Vine Whip', 21),
            ('Poison Powder', 28),
            ('Razor Leaf', 35),
            ('Sleep Powder', 42),
            ('Solar Beam', 49)
        ],
        'Ivysaur': [
            ('Tackle', 1),
            ('Growl', 1),
            ('Leech Seed', 1),
            ('Vine Whip', 21),
            ('Poison Powder', 28),
            ('Razor Leaf', 36),
            ('Sleep Powder', 43),
            ('Solar Beam', 50)
        ],
        'Venusaur': [
            ('Tackle', 1),
            ('Growl', 1),
            ('Leech Seed', 1),
            ('Vine Whip', 21),
            ('Poison Powder', 28),
            ('Razor Leaf', 36),
            ('Sleep Powder', 43),
            ('Solar Beam', 50),
            ('Sludge', 1),
            ('Charm', 1),
            ('Mega Drain', 1),
            ('Belly Drum', 1)
        ],
        'Charmander': [
            ('Scratch', 1),
            ('Growl', 1),
            ('Ember', 9),
            ('Smokescreen', 15),
            ('Dragon Rage', 22),
            ('Scary Face', 29),
            ('Fire Spin', 36),
            ('Flamethrower', 43)
        ],
        'Charmeleon': [
            ('Scratch', 1),
            ('Growl', 1),
            ('Ember', 1),
            ('Smokescreen', 16),
            ('Dragon Rage', 23),
            ('Scary Face', 30),
            ('Fire Spin', 37),
            ('Flamethrower', 44)
        ],
        'Charizard': [
            ('Scratch', 1),
            ('Growl', 1),
            ('Ember', 1),
            ('Smokescreen', 16),
            ('Dragon Rage', 23),
            ('Scary Face', 30),
            ('Fire Spin', 37),
            ('Flamethrower', 44),
            ('Wing Attack', 1),
            ('Slash', 1),
            ('Dragon Claw', 1)
        ],
        'Squirtle': [
            ('Tackle', 1),
            ('Tail Whip', 5),
            ('Bubble', 11),
            ('Water Gun', 17),
            ('Bite', 23),
            ('Withdraw', 30),
            ('Skull Bash', 37),
            ('Hydro Pump', 44)
        ],
        'Wartortle': [
            ('Tackle', 1),
            ('Tail Whip', 1),
            ('Bubble', 11),
            ('Water Gun', 18),
            ('Bite', 25),
            ('Withdraw', 33),
            ('Skull Bash', 41),
            ('Hydro Pump', 49)
        ],
        'Blastoise': [
            ('Tackle', 1),
            ('Tail Whip', 1),
            ('Bubble', 11),
            ('Water Gun', 18),
            ('Bite', 25),
            ('Withdraw', 33),
            ('Skull Bash', 41),
            ('Hydro Pump', 49),
            ('Mud Shot', 1),
            ('Ice Beam', 1),
            ('Blizzard', 1)
        ],
        'Caterpie': [
            ('String Shot', 1),
            ('Bug Bite', 1)
        ],
        'Metapod': [
            ('Harden', 1)
        ],
        'Butterfree': [
            ('Confusion', 1),
            ('Poison Powder', 1),
            ('Stun Spore', 1),
            ('Sleep Powder', 1),
            ('Supersonic', 28),
            ('Psybeam', 36),
            ('Whirlwind', 43)
        ],
        'Weedle': [
            ('Poison Sting', 1),
            ('Bug Bite', 1)
        ],
        'Kakuna': [
            ('Harden', 1)
        ],
        'Beedrill': [
            ('Fury Attack', 1),
            ('Twineedle', 1),
            ('Rage', 21),
            ('Pin Missile', 28),
            ('Agility', 36),
            ('Assurance', 43)
        ],
        'Pidgey': [
            ('Gust', 1),
            ('Sand Attack', 9),
            ('Quick Attack', 15),
            ('Whirlwind', 22),
            ('Wing Attack', 29),
            ('Double-Edge', 36)
        ],
        'Pidgeotto': [
            ('Gust', 1),
            ('Sand Attack', 1),
            ('Quick Attack', 16),
            ('Whirlwind', 23),
            ('Wing Attack', 30),
            ('Double-Edge', 37)
        ],
        'Pidgeot': [
            ('Gust', 1),
            ('Sand Attack', 1),
            ('Quick Attack', 16),
            ('Whirlwind', 23),
            ('Wing Attack', 30),
            ('Double-Edge', 37),
            ('Sky Attack', 1)
        ],
        'Rattata': [
            ('Tackle', 1),
            ('Tail Whip', 5),
            ('Quick Attack', 10),
            ('Hyper Fang', 15),
            ('Focus Energy', 20),
            ('Super Fang', 25)
        ],
        'Raticate': [
            ('Tackle', 1),
            ('Tail Whip', 1),
            ('Quick Attack', 1),
            ('Hyper Fang', 16),
            ('Focus Energy', 21),
            ('Super Fang', 26)
        ],
        'Spearow': [
            ('Peck', 1),
            ('Growl', 6),
            ('Leer', 11),
            ('Fury Attack', 16),
            ('Mirror Move', 21),
            ('Drill Peck', 26)
        ],
        'Fearow': [
            ('Peck', 1),
            ('Growl', 1),
            ('Leer', 1),
            ('Fury Attack', 16),
            ('Mirror Move', 21),
            ('Drill Peck', 26),
            ('Tri Attack', 1),
            ('Agility', 1),
            ('Whirlwind', 1)
        ],
        'Ekans': [
            ('Wrap', 1),
            ('Leer', 8),
            ('Poison Sting', 15),
            ('Bite', 22),
            ('Glare', 29),
            ('Screech', 36),
            ('Acid', 43)
        ],
        'Arbok': [
            ('Wrap', 1),
            ('Leer', 1),
            ('Poison Sting', 1),
            ('Bite', 22),
            ('Glare', 29),
            ('Screech', 38),
            ('Acid', 47)
        ],
        'Pikachu': [
            ('Thunder Shock', 1),
            ('Growl', 1),
            ('Tail Whip', 9),
            ('Thunder Wave', 17),
            ('Quick Attack', 25),
            ('Swift', 33),
            ('Agility', 41)
        ],
        'Raichu': [
            ('Thunder Shock', 1),
            ('Growl', 1),
            ('Tail Whip', 1),
            ('Thunder Wave', 17),
            ('Quick Attack', 25),
            ('Swift', 33),
            ('Agility', 41),
            ('Thunderbolt', 49)
        ],
        'Sandshrew': [
            ('Scratch', 1),
            ('Sand Attack', 8),
            ('Slash', 15),
            ('Poison Sting', 22),
            ('Swift', 29),
            ('Fury Swipes', 36),
            ('Crush Claw', 43)
        ],
        'Sandslash': [
            ('Scratch', 1),
            ('Sand Attack', 1),
            ('Slash', 15),
            ('Poison Sting', 22),
            ('Swift', 29),
            ('Fury Swipes', 36),
            ('Crush Claw', 45)
        ],
        'Nidoran♀': [
            ('Scratch', 1),
            ('Tail Whip', 7),
            ('Double Kick', 13),
            ('Poison Sting', 19),
            ('Body Slam', 25),
            ('Take Down', 31)
        ],
        'Nidorina': [
            ('Scratch', 1),
            ('Tail Whip', 1),
            ('Double Kick', 13),
            ('Poison Sting', 20),
            ('Body Slam', 27),
            ('Take Down', 34)
        ],
        'Nidoqueen': [
            ('Scratch', 1),
            ('Tail Whip', 1),
            ('Double Kick', 13),
            ('Poison Sting', 20),
            ('Body Slam', 27),
            ('Take Down', 34),
            ('Superpower', 1),
            ('Earthquake', 1),
            ('Cross Chop', 1)
        ],
        'Nidoran♂': [
            ('Peck', 1),
            ('Tail Whip', 7),
            ('Double Kick', 13),
            ('Poison Sting', 19),
            ('Horn Attack', 25),
            ('Fury Attack', 31)
        ],
        'Nidorino': [
            ('Peck', 1),
            ('Tail Whip', 1),
            ('Double Kick', 13),
            ('Poison Sting', 20),
            ('Horn Attack', 27),
            ('Fury Attack', 34)
        ],
        'Nidoking': [
            ('Peck', 1),
            ('Tail Whip', 1),
            ('Double Kick', 13),
            ('Poison Sting', 20),
            ('Horn Attack', 27),
            ('Fury Attack', 34),
            ('Megahorn', 1),
            ('Thunderbolt', 1),
            ('Ice Beam', 1)
        ],
        'Clefairy': [
            ('Pound', 1),
            ('Growl', 5),
            ('Sing', 9),
            ('Double Slap', 13),
            ('Minimize', 17),
            ('Defense Curl', 21),
            ('Metronome', 25)
        ],
        'Clefable': [
            ('Pound', 1),
            ('Growl', 1),
            ('Sing', 1),
            ('Double Slap', 13),
            ('Minimize', 17),
            ('Defense Curl', 21),
            ('Metronome', 25),
            ('Moonblast', 29)
        ],
        'Vulpix': [
            ('Ember', 1),
            ('Tail Whip', 7),
            ('Quick Attack', 13),
            ('Roar', 19),
            ('Confuse Ray', 25),
            ('Flamethrower', 31)
        ],
        'Ninetales': [
            ('Ember', 1),
            ('Tail Whip', 1),
            ('Quick Attack', 13),
            ('Roar', 19),
            ('Confuse Ray', 25),
            ('Flamethrower', 31),
            ('Fire Blast', 37)
        ],
        'Jigglypuff': [
            ('Sing', 1),
            ('Pound', 5),
            ('Disarming Voice', 9),
            ('Double Slap', 13),
            ('Defense Curl', 17),
            ('Rest', 21)
        ],
        'Wigglytuff': [
            ('Sing', 1),
            ('Pound', 1),
            ('Disarming Voice', 1),
            ('Double Slap', 13),
            ('Defense Curl', 17),
            ('Rest', 21),
            ('Play Rough', 25)
        ],
        'Zubat': [
            ('Leech Life', 1),
            ('Supersonic', 7),
            ('Astonish', 13),
            ('Bite', 19),
            ('Wing Attack', 25),
            ('Swift', 31)
        ],
        'Golbat': [
            ('Leech Life', 1),
            ('Supersonic', 1),
            ('Astonish', 13),
            ('Bite', 19),
            ('Wing Attack', 25),
            ('Swift', 31),
            ('Air Cutter', 37)
        ],
        'Oddish': [
            ('Absorb', 1),
            ('Acid', 15),
            ('Sweet Scent', 19),
            ('Poison Powder', 23),
            ('Stun Spore', 27),
            ('Sleep Powder', 31)
        ],
        'Gloom': [
            ('Absorb', 1),
            ('Acid', 1),
            ('Sweet Scent', 19),
            ('Poison Powder', 25),
            ('Stun Spore', 31),
            ('Sleep Powder', 37)
        ],
        'Vileplume': [
            ('Absorb', 1),
            ('Acid', 1),
            ('Sweet Scent', 19),
            ('Poison Powder', 25),
            ('Stun Spore', 31),
            ('Sleep Powder', 37),
            ('Solar Beam', 43)
        ],
        'Paras': [
            ('Scratch', 1),
            ('Stun Spore', 7),
            ('Poison Powder', 13),
            ('Leech Life', 19),
            ('Spore', 25),
            ('Slash', 31)
        ],
        'Parasect': [
            ('Scratch', 1),
            ('Stun Spore', 1),
            ('Poison Powder', 13),
            ('Leech Life', 19),
            ('Spore', 25),
            ('Slash', 31),
            ('Solar Beam', 37)
        ],
        'Venonat': [
            ('Tackle', 1),
            ('Disable', 8),
            ('Foresight', 15),
            ('Leech Life', 22),
            ('Poison Powder', 29),
            ('Psybeam', 36)
        ],
        'Venomoth': [
            ('Tackle', 1),
            ('Disable', 1),
            ('Foresight', 15),
            ('Leech Life', 22),
            ('Poison Powder', 29),
            ('Psybeam', 36),
            ('Psychic', 43)
        ],
        'Diglett': [
            ('Scratch', 1),
            ('Sand Attack', 7),
            ('Slash', 13),
            ('Earthquake', 19),
            ('Mud-Slap', 25)
        ],
        'Dugtrio': [
            ('Scratch', 1),
            ('Sand Attack', 1),
            ('Slash', 13),
            ('Earthquake', 19),
            ('Mud-Slap', 25),
            ('Fissure', 31)
        ],
        'Meowth': [
            ('Scratch', 1),
            ('Growl', 6),
            ('Bite', 11),
            ('Screech', 16),
            ('Fury Swipes', 21),
            ('Slash', 26)
        ],
        'Persian': [
            ('Scratch', 1),
            ('Growl', 1),
            ('Bite', 11),
            ('Screech', 16),
            ('Fury Swipes', 21),
            ('Slash', 26),
            ('Power Gem', 31)
        ],
        'Psyduck': [
            ('Scratch', 1),
            ('Water Gun', 8),
            ('Confusion', 15),
            ('Disable', 22),
            ('Psycho Cut', 29),
            ('Screech', 36)
        ],
        'Golduck': [
            ('Scratch', 1),
            ('Water Gun', 1),
            ('Confusion', 15),
            ('Disable', 22),
            ('Psycho Cut', 29),
            ('Screech', 36),
            ('Hydro Pump', 43)
        ],
        'Mankey': [
            ('Scratch', 1),
            ('Leer', 7),
            ('Low Kick', 13),
            ('Karate Chop', 19),
            ('Fury Swipes', 25),
            ('Seismic Toss', 31)
        ],
        'Primeape': [
            ('Scratch', 1),
            ('Leer', 1),
            ('Low Kick', 13),
            ('Karate Chop', 19),
            ('Fury Swipes', 25),
            ('Seismic Toss', 31),
            ('Cross Chop', 37)
        ],
        'Growlithe': [
            ('Bite', 1),
            ('Roar', 8),
            ('Ember', 15),
            ('Leer', 22),
            ('Take Down', 29),
            ('Agility', 36)
        ],
        'Arcanine': [
            ('Bite', 1),
            ('Roar', 1),
            ('Ember', 15),
            ('Leer', 22),
            ('Take Down', 29),
            ('Agility', 36),
            ('Flare Blitz', 43)
        ],
        'Poliwag': [
            ('Bubble', 1),
            ('Hypnosis', 15),
            ('Water Gun', 23),
            ('Double Slap', 31),
            ('Body Slam', 39)
        ],
        'Poliwhirl': [
            ('Bubble', 1),
            ('Hypnosis', 1),
            ('Water Gun', 23),
            ('Double Slap', 31),
            ('Body Slam', 39),
            ('Mud Shot', 47)
        ],
        'Poliwrath': [
            ('Bubble', 1),
            ('Hypnosis', 1),
            ('Water Gun', 23),
            ('Double Slap', 31),
            ('Body Slam', 39),
            ('Mud Shot', 47),
            ('Dynamic Punch', 55)
        ],
        'Abra': [
            ('Teleport', 1)
        ],
        'Kadabra': [
            ('Teleport', 1),
            ('Kinesis', 1),
            ('Confusion', 16),
            ('Disable', 20),
            ('Psycho Cut', 24),
            ('Recover', 28),
            ('Psychic', 32)
        ],
        'Alakazam': [
            ('Teleport', 1),
            ('Kinesis', 1),
            ('Confusion', 16),
            ('Disable', 20),
            ('Psycho Cut', 24),
            ('Recover', 28),
            ('Psychic', 32)
        ],
        'Machop': [
            ('Low Kick', 1),
            ('Leer', 7),
            ('Focus Energy', 13),
            ('Karate Chop', 19),
            ('Low Sweep', 25),
            ('Seismic Toss', 31)
        ],
        'Machoke': [
            ('Low Kick', 1),
            ('Leer', 1),
            ('Focus Energy', 13),
            ('Karate Chop', 19),
            ('Low Sweep', 25),
            ('Seismic Toss', 31),
            ('Submission', 37)
        ],
        'Machamp': [
            ('Low Kick', 1),
            ('Leer', 1),
            ('Focus Energy', 13),
            ('Karate Chop', 19),
            ('Low Sweep', 25),
            ('Seismic Toss', 31),
            ('Submission', 37),
            ('Cross Chop', 43)
        ],
        'Bellsprout': [
            ('Vine Whip', 1),
            ('Growth', 7),
            ('Wrap', 13),
            ('Sleep Powder', 19),
            ('Poison Powder', 25),
            ('Sludge', 31)
        ],
        'Weepinbell': [
            ('Vine Whip', 1),
            ('Growth', 1),
            ('Wrap', 13),
            ('Sleep Powder', 19),
            ('Poison Powder', 25),
            ('Sludge', 31),
            ('Acid', 37)
        ],
        'Victreebel': [
            ('Vine Whip', 1),
            ('Growth', 1),
            ('Wrap', 13),
            ('Sleep Powder', 19),
            ('Poison Powder', 25),
            ('Sludge', 31),
            ('Acid', 37),
            ('Leaf Storm', 43)
        ],
        'Tentacool': [
            ('Acid', 1),
            ('Poison Sting', 10),
            ('Supersonic', 15),
            ('Wrap', 20),
            ('Water Pulse', 25),
            ('Hydro Pump', 30)
        ],
        'Tentacruel': [
            ('Acid', 1),
            ('Poison Sting', 1),
            ('Supersonic', 15),
            ('Wrap', 20),
            ('Water Pulse', 25),
            ('Hydro Pump', 30),
            ('Sludge Wave', 35)
        ],
        'Geodude': [
            ('Tackle', 1),
            ('Defense Curl', 1),
            ('Rock Throw', 9),
            ('Magnitude', 17),
            ('Self-Destruct', 25),
            ('Rock Slide', 33)
        ],
        'Graveler': [
            ('Tackle', 1),
            ('Defense Curl', 1),
            ('Rock Throw', 9),
            ('Magnitude', 17),
            ('Self-Destruct', 25),
            ('Rock Slide', 33),
            ('Earthquake', 41)
        ],
        'Golem': [
            ('Tackle', 1),
            ('Defense Curl', 1),
            ('Rock Throw', 9),
            ('Magnitude', 17),
            ('Self-Destruct', 25),
            ('Rock Slide', 33),
            ('Earthquake', 41),
            ('Explosion', 49)
        ],
        'Ponyta': [
            ('Tackle', 1),
            ('Growl', 5),
            ('Tail Whip', 10),
            ('Ember', 15),
            ('Stomp', 20),
            ('Flame Charge', 25),
            ('Take Down', 30)
        ],
        'Rapidash': [
            ('Tackle', 1),
            ('Growl', 1),
            ('Tail Whip', 10),
            ('Ember', 15),
            ('Stomp', 20),
            ('Flame Charge', 25),
            ('Take Down', 30),
            ('Inferno', 35)
        ],
        'Slowpoke': [
            ('Tackle', 1),
            ('Growl', 1),
            ('Water Gun', 9),
            ('Confusion', 17),
            ('Disable', 25),
            ('Psychic', 33)
        ],
        'Slowbro': [
            ('Tackle', 1),
            ('Growl', 1),
            ('Water Gun', 1),
            ('Confusion', 17),
            ('Disable', 25),
            ('Psychic', 33),
            ('Amnesia', 41)
        ],
        'Magnemite': [
            ('Tackle', 1),
            ('Thunder Shock', 1),
            ('Thunder Wave', 15),
            ('Thunderbolt', 30)
        ],
        'Magneton': [
            ('Tackle', 1),
            ('Thunder Shock', 1),
            ('Thunder Wave', 15),
            ('Thunderbolt', 30),
            ('Magnet Bomb', 45)
        ],
        "Farfetch'd": [
            ('Peck', 1),
            ('Sand Attack', 1),
            ('Leer', 15),
            ('Fury Attack', 30),
            ('Swords Dance', 45)
        ],
        'Doduo': [
            ('Peck', 1),
            ('Growl', 1),
            ('Quick Attack', 15),
            ('Rage', 30),
            ('Double Kick', 45)
        ],
        'Dodrio': [
            ('Peck', 1),
            ('Growl', 1),
            ('Quick Attack', 15),
            ('Rage', 30),
            ('Double Kick', 45),
            ('Drill Peck', 60)
        ],
        'Seel': [
            ('Headbutt', 1),
            ('Growl', 15),
            ('Aqua Tail', 30),
            ('Icy Wind', 45)
        ],
        'Dewgong': [
            ('Headbutt', 1),
            ('Growl', 1),
            ('Aqua Tail', 30),
            ('Icy Wind', 45),
            ('Aurora Beam', 60)
        ],
        'Grimer': [
            ('Pound', 1),
            ('Poison Gas', 15),
            ('Mud-Slap', 20),
            ('Sludge', 25),
            ('Sludge Bomb', 30)
        ],
        'Muk': [
            ('Pound', 1),
            ('Poison Gas', 1),
            ('Mud-Slap', 20),
            ('Sludge', 25),
            ('Sludge Bomb', 30),
            ('Gunk Shot', 35)
        ],
        'Shellder': [
            ('Tackle', 1),
            ('Withdraw', 15),
            ('Icicle Spear', 30),
            ('Clamp', 45)
        ],
        'Cloyster': [
            ('Tackle', 1),
            ('Withdraw', 15),
            ('Icicle Spear', 30),
            ('Clamp', 45),
            ('Aurora Beam', 60)
        ],
        'Gastly': [
            ('Lick', 1),
            ('Spite', 7),
            ('Mean Look', 13),
            ('Curse', 19),
            ('Night Shade', 25)
        ],
        'Haunter': [
            ('Lick', 1),
            ('Spite', 1),
            ('Mean Look', 13),
            ('Curse', 19),
            ('Night Shade', 25),
            ('Shadow Punch', 31)
        ],
        'Gengar': [
            ('Lick', 1),
            ('Spite', 1),
            ('Mean Look', 13),
            ('Curse', 19),
            ('Night Shade', 25),
            ('Shadow Punch', 31),
            ('Dream Eater', 37)
        ],
        'Onix': [
            ('Tackle', 1),
            ('Screech', 15),
            ('Rock Throw', 30),
            ('Rock Slide', 45)
        ],
        'Drowzee': [
            ('Pound', 1),
            ('Hypnosis', 15),
            ('Poison Gas', 20),
            ('Psychic', 25),
            ('Meditate', 30)
        ],
        'Hypno': [
            ('Pound', 1),
            ('Hypnosis', 1),
            ('Poison Gas', 20),
            ('Psychic', 25),
            ('Meditate', 30),
            ('Psycho Cut', 35)
        ],
        'Krabby': [
            ('Bubble', 1),
            ('Leer', 7),
            ('Mud Shot', 15),
            ('Stomp', 23),
            ('Crabhammer', 31)
        ],
        'Kingler': [
            ('Bubble', 1),
            ('Leer', 1),
            ('Mud Shot', 15),
            ('Stomp', 23),
            ('Crabhammer', 31),
            ('Hyper Beam', 39)
        ],
        'Voltorb': [
            ('Tackle', 1),
            ('Screech', 15),
            ('Sonic Boom', 20),
            ('Spark', 25),
            ('Self-Destruct', 30)
        ],
        'Electrode': [
            ('Tackle', 1),
            ('Screech', 15),
            ('Sonic Boom', 20),
            ('Spark', 25),
            ('Self-Destruct', 30),
            ('Light Screen', 35)
        ],
        'Exeggcute': [
            ('Barrage', 1),
            ('Hypnosis', 1),
            ('Reflect', 16),
            ('Leech Seed', 21),
            ('Psychic', 26),
            ('Solar Beam', 31)
        ],
        'Exeggutor': [
            ('Barrage', 1),
            ('Hypnosis', 1),
            ('Reflect', 16),
            ('Leech Seed', 21),
            ('Psychic', 26),
            ('Solar Beam', 31),
            ('Psych Up', 36)
        ],
        'Cubone': [
            ('Growl', 1),
            ('Tail Whip', 4),
            ('Bone Club', 8),
            ('Headbutt', 13),
            ('Leer', 19),
            ('Focus Energy', 26)
        ],
        'Marowak': [
            ('Growl', 1),
            ('Tail Whip', 1),
            ('Bone Club', 1),
            ('Headbutt', 13),
            ('Leer', 19),
            ('Focus Energy', 26),
            ('Bone Rush', 34)
        ],
        'Hitmonlee': [
            ('Double Kick', 1),
            ('Meditate', 1),
            ('Rolling Kick', 20),
            ('Jump Kick', 35),
            ('High Jump Kick', 50)
        ],
        'Hitmonchan': [
            ('Comet Punch', 1),
            ('Agility', 1),
            ('Thunder Punch', 20),
            ('Fire Punch', 35),
            ('Ice Punch', 50)
        ],
        'Lickitung': [
            ('Lick', 1),
            ('Supersonic', 1),
            ('Defense Curl', 15),
            ('Stomp', 20),
            ('Wrap', 25),
            ('Slam', 30)
        ],
        'Koffing': [
            ('Tackle', 1),
            ('Smog', 1),
            ('SmokeScreen', 17),
            ('Sludge', 21),
            ('Self-Destruct', 25),
            ('Haze', 29)
        ],
        'Weezing': [
            ('Tackle', 1),
            ('Smog', 1),
            ('SmokeScreen', 17),
            ('Sludge', 21),
            ('Self-Destruct', 25),
            ('Haze', 29),
            ('Explosion', 33)
        ],
        'Rhyhorn': [
            ('Horn Attack', 1),
            ('Tail Whip', 1),
            ('Fury Attack', 15),
            ('Scary Face', 20),
            ('Rock Blast', 25)
        ],
        'Rhydon': [
            ('Horn Attack', 1),
            ('Tail Whip', 1),
            ('Fury Attack', 15),
            ('Scary Face', 20),
            ('Rock Blast', 25),
            ('Horn Drill', 30)
        ],
        'Chansey': [
            ('Pound', 1),
            ('Growl', 1),
            ('Tail Whip', 5),
            ('Soft-Boiled', 10),
            ('Double Slap', 15),
            ('Minimize', 20)
        ],
        'Tangela': [
            ('Ingrain', 1),
            ('Sleep Powder', 1),
            ('Absorb', 16),
            ('Giga Drain', 21),
            ('Sludge Bomb', 26)
        ],
        'Kangaskhan': [
            ('Comet Punch', 1),
            ('Leer', 1),
            ('Bite', 10),
            ('Tail Whip', 15),
            ('Mega Punch', 20),
            ('Dizzy Punch', 25)
        ],
        'Horsea': [
            ('Bubble', 1),
            ('SmokeScreen', 15),
            ('Leer', 20),
            ('Bubble Beam', 25),
            ('Agility', 30)
        ],
        'Seadra': [
            ('Bubble', 1),
            ('SmokeScreen', 15),
            ('Leer', 20),
            ('Bubble Beam', 25),
            ('Agility', 30),
            ('Hydro Pump', 35)
        ],
        'Goldeen': [
            ('Peck', 1),
            ('Tail Whip', 1),
            ('Water Gun', 15),
            ('Horn Attack', 20),
            ('Fury Attack', 25),
            ('Waterfall', 30)
        ],
        'Seaking': [
            ('Peck', 1),
            ('Tail Whip', 1),
            ('Water Gun', 15),
            ('Horn Attack', 20),
            ('Fury Attack', 25),
            ('Waterfall', 30),
            ('Megahorn', 35)
        ],
        'Staryu': [
            ('Tackle', 1),
            ('Harden', 1),
            ('Water Gun', 15),
            ('Rapid Spin', 20),
            ('Recover', 25),
            ('Bubble Beam', 30)
        ],
        'Starmie': [
            ('Tackle', 1),
            ('Harden', 1),
            ('Water Gun', 15),
            ('Rapid Spin', 20),
            ('Recover', 25),
            ('Bubble Beam', 30),
            ('Light Screen', 35)
        ],
        'Mr. Mime': [
            ('Barrier', 1),
            ('Confusion', 1),
            ('Meditate', 20),
            ('Double Slap', 25),
            ('Light Screen', 30)
        ],
        'Scyther': [
            ('Quick Attack', 1),
            ('Leer', 1),
            ('Focus Energy', 20),
            ('Double Team', 25),
            ('Slash', 30),
            ('Swords Dance', 35)
        ],
        'Jynx': [
            ('Pound', 1),
            ('Lick', 1),
            ('Lovely Kiss', 20),
            ('Powder Snow', 25),
            ('Double Slap', 30)
        ],
        'Electabuzz': [
            ('Quick Attack', 1),
            ('Leer', 1),
            ('Thunder Shock', 20),
            ('Thunder Punch', 25),
            ('Screech', 30)
        ],
        'Magmar': [
            ('Ember', 1),
            ('Leer', 1),
            ('SmokeScreen', 20),
            ('Fire Punch', 25),
            ('Sunny Day', 30)
        ],
        'Pinsir': [
            ('Vice Grip', 1),
            ('Focus Energy', 1),
            ('Seismic Toss', 20),
            ('Guillotine', 25),
            ('Harden', 30)
        ],
        'Tauros': [
            ('Tackle', 1),
            ('Tail Whip', 1),
            ('Stomp', 20),
            ('Leer', 25),
            ('Horn Attack', 30)
        ],
        'Magikarp': [
            ('Splash', 1)
        ],
        'Gyarados': [
            ('Bite', 1),
            ('Dragon Rage', 1),
            ('Twister', 20),
            ('Hydro Pump', 30)
        ],
        'Lapras': [
            ('Water Gun', 1),
            ('Growl', 1),
            ('Sing', 15),
            ('Mist', 20),
            ('Ice Beam', 25),
            ('Body Slam', 30)
        ],
        'Ditto': [
            ('Transform', 1)
        ],
        'Eevee': [
            ('Tackle', 1),
            ('Tail Whip', 1),
            ('Sand Attack', 20),
            ('Quick Attack', 25),
            ('Bite', 30)
        ],
        'Vaporeon': [
            ('Tackle', 1),
            ('Tail Whip', 1),
            ('Sand Attack', 20),
            ('Quick Attack', 25),
            ('Bite', 30),
            ('Water Gun', 35)
        ],
        'Jolteon': [
            ('Tackle', 1),
            ('Tail Whip', 1),
            ('Sand Attack', 20),
            ('Quick Attack', 25),
            ('Double Kick', 30),
            ('Thunderbolt', 35)
        ],
        'Flareon': [
            ('Tackle', 1),
            ('Tail Whip', 1),
            ('Sand Attack', 20),
            ('Quick Attack', 25),
            ('Ember', 30),
            ('Fire Blast', 35)
        ],
        'Porygon': [
            ('Tackle', 1),
            ('Conversion', 1),
            ('Agility', 15),
            ('Psychic', 20),
            ('Recover', 25),
            ('Tri Attack', 30)
        ],
        'Omanyte': [
            ('Water Gun', 1),
            ('Withdraw', 1),
            ('Bite', 15),
            ('Rollout', 20),
            ('Leer', 25),
            ('Rock Blast', 30)
        ],
        'Omastar': [
            ('Water Gun', 1),
            ('Withdraw', 1),
            ('Bite', 15),
            ('Rollout', 20),
            ('Leer', 25),
            ('Rock Blast', 30),
            ('Hydro Pump', 35)
        ],
        'Kabuto': [
            ('Scratch', 1),
            ('Harden', 1),
            ('Absorb', 15),
            ('Slash', 20),
            ('Leer', 25),
            ('Rock Blast', 30)
        ],
        'Kabutops': [
            ('Scratch', 1),
            ('Harden', 1),
            ('Absorb', 15),
            ('Slash', 20),
            ('Leer', 25),
            ('Rock Blast', 30),
            ('Megahorn', 35)
        ],
        'Aerodactyl': [
            ('Bite', 1),
            ('Wing Attack', 1),
            ('Agility', 20),
            ('Take Down', 25),
            ('Hyper Beam', 30)
        ],
        'Snorlax': [
            ('Tackle', 1),
            ('Amnesia', 1),
            ('Headbutt', 15),
            ('Body Slam', 20),
            ('Harden', 25),
            ('Double-Edge', 30)
        ],
        'Articuno': [
            ('Peck', 1),
            ('Growl', 1),
            ('Mist', 20),
            ('Ice Beam', 25),
            ('Agility', 30),
            ('Blizzard', 35)
        ],
        'Zapdos': [
            ('Peck', 1),
            ('Growl', 1),
            ('Thunder Shock', 20),
            ('Thunder Wave', 25),
            ('Agility', 30),
            ('Thunderbolt', 35)
        ],
        'Moltres': [
            ('Peck', 1),
            ('Growl', 1),
            ('Ember', 20),
            ('Fire Spin', 25),
            ('Agility', 30),
            ('Flamethrower', 35)
        ],
        'Dratini': [
            ('Wrap', 1),
            ('Leer', 1),
            ('Thunder Wave', 20),
            ('Agility', 25),
            ('Slam', 30)
        ],
        'Dragonair': [
            ('Wrap', 1),
            ('Leer', 1),
            ('Thunder Wave', 20),
            ('Agility', 25),
            ('Slam', 30),
            ('Hyper Beam', 35)
        ],
        'Dragonite': [
            ('Wrap', 1),
            ('Leer', 1),
            ('Thunder Wave', 20),
            ('Agility', 25),
            ('Slam', 30),
            ('Hyper Beam', 35),
            ('Dragon Rage', 40)
        ],
        'Mewtwo': [
            ('Confusion', 1),
            ('Disable', 1),
            ('Psychic', 20),
            ('Swift', 25),
            ('Future Sight', 30)
        ],
        'Mew': [
            ('Pound', 1),
            ('Transform', 1)
        ]
    }

    # Dictionnaire pour mapper les noms des capacités à leurs instances
    moves_dict = {}
    for move_name in set(move for moves in learnable_moves_data.values() for move, _ in moves):
        
        move_obj = PokemonMove.objects.filter(name=move_name).first()
        moves_dict[move_name] = move_obj

    for pokemon_name, moves in learnable_moves_data.items():
        try:
            pokemon = Pokemon.objects.get(name=pokemon_name)
            for move_name, level_learned in moves:
                move = moves_dict[move_name]
                PokemonLearnableMove.objects.get_or_create(
                    pokemon=pokemon,
                    move=move,
                    level_learned=level_learned
                )
                logging.info(f"  [+] Capacité apprise: {pokemon_name} apprend {move_name} (Niveau {level_learned})")
        except Pokemon.DoesNotExist as e:
            logging.warning(f"  [!] Pokémon non trouvé: {e}")

    logging.info(f"[+] Capacités apprises configurées")

    
    
    logging.info("\n" + "="*60)
    logging.info("[✓] INITIALISATION DE LA BASE TERMINÉE AVEC SUCCÈS")
    logging.info("="*60)
    
    return pokemon_dict, moves_dict, types_dict


# Point d'entrée pour Django shell
if __name__ == '__main__':
    scriptToInitializeDatabase()