#!/usr/bin/python3
"""
Script d'initialisation pour les objets, NPCs et Champions d'Arène
À exécuter après l'initialisation des Pokémon de base
"""

from myPokemonApp.models import (
    Item, PokemonType, Pokemon, PokemonMove,
    Trainer
)
from myPokemonApp.gameUtils import (
    create_gym_leader, create_npc_trainer
)

import logging

logging.basicConfig(level=logging.INFO)


def initialize_items():
    """Initialise tous les objets Gen 1 (complet)"""

    logging.info("[*] Initialisation des objets...")

    items_data = [

        # POTIONS
        {'name': 'Potion', 'description': 'Restaure 20 HP.', 'item_type': 'potion', 'price': 300, 'heal_amount': 20, 'is_consumable': True},
        {'name': 'Super Potion', 'description': 'Restaure 50 HP.', 'item_type': 'potion', 'price': 700, 'heal_amount': 50, 'is_consumable': True},
        {'name': 'Hyper Potion', 'description': 'Restaure 200 HP.', 'item_type': 'potion', 'price': 1200, 'heal_amount': 200, 'is_consumable': True},
        {'name': 'Max Potion', 'description': 'Restaure tous les HP.', 'item_type': 'potion', 'price': 2500, 'heal_percentage': 100, 'is_consumable': True},
        {'name': 'Full Restore', 'description': 'Restaure tous les HP et soigne le statut.', 'item_type': 'potion', 'price': 3000, 'heal_percentage': 100, 'cures_status': True, 'is_consumable': True},
        {'name': 'Revive', 'description': 'Ranime un Pokemon evanoui (moitie HP).', 'item_type': 'potion', 'price': 1500, 'heal_percentage': 50, 'is_consumable': True},
        {'name': 'Max Revive', 'description': 'Ranime un Pokemon evanoui (HP max).', 'item_type': 'potion', 'price': 4000, 'heal_percentage': 100, 'is_consumable': True},

        # SOINS DE STATUT
        {'name': 'Antidote', 'description': 'Soigne l empoisonnement.', 'item_type': 'status', 'price': 100, 'cures_status': True, 'specific_status': 'poison', 'is_consumable': True},
        {'name': 'Awakening', 'description': 'Reveille un Pokemon endormi.', 'item_type': 'status', 'price': 250, 'cures_status': True, 'specific_status': 'sleep', 'is_consumable': True},
        {'name': 'Burn Heal', 'description': 'Soigne une brulure.', 'item_type': 'status', 'price': 250, 'cures_status': True, 'specific_status': 'burn', 'is_consumable': True},
        {'name': 'Ice Heal', 'description': 'Degele un Pokemon gele.', 'item_type': 'status', 'price': 250, 'cures_status': True, 'specific_status': 'freeze', 'is_consumable': True},
        {'name': 'Paralyze Heal', 'description': 'Soigne la paralysie.', 'item_type': 'status', 'price': 200, 'cures_status': True, 'specific_status': 'paralysis', 'is_consumable': True},
        {'name': 'Full Heal', 'description': 'Soigne tous les problemes de statut.', 'item_type': 'status', 'price': 600, 'cures_status': True, 'is_consumable': True},

        # PP
        {'name': 'Ether', 'description': 'Restaure 10 PP d une capacite.', 'item_type': 'status', 'price': 1200, 'is_consumable': True},
        {'name': 'Max Ether', 'description': 'Restaure tous les PP d une capacite.', 'item_type': 'status', 'price': 2000, 'is_consumable': True},
        {'name': 'Elixir', 'description': 'Restaure 10 PP de toutes les capacites.', 'item_type': 'status', 'price': 3000, 'is_consumable': True},
        {'name': 'Max Elixir', 'description': 'Restaure tous les PP de toutes les capacites.', 'item_type': 'status', 'price': 4500, 'is_consumable': True},
        {'name': 'PP Up', 'description': 'Augmente definitivement le max PP d une capacite.', 'item_type': 'battle', 'price': 9800, 'is_consumable': True},
        {'name': 'PP Max', 'description': 'Augmente au maximum les PP d une capacite.', 'item_type': 'battle', 'price': 0, 'is_consumable': True},

        # REPULSIFS
        {'name': 'Repel', 'description': 'Empeche les Pokemon sauvages faibles pendant 100 pas.', 'item_type': 'battle', 'price': 350, 'is_consumable': True},
        {'name': 'Super Repel', 'description': 'Empeche les Pokemon sauvages faibles pendant 200 pas.', 'item_type': 'battle', 'price': 500, 'is_consumable': True},
        {'name': 'Max Repel', 'description': 'Empeche les Pokemon sauvages faibles pendant 250 pas.', 'item_type': 'battle', 'price': 700, 'is_consumable': True},

        # POKEBALLS
        {'name': 'Poke Ball', 'description': 'Capture les Pokemon sauvages.', 'item_type': 'pokeball', 'price': 200, 'catch_rate_modifier': 1.0, 'is_consumable': True},
        {'name': 'Great Ball', 'description': 'Ball avec un meilleur taux de capture.', 'item_type': 'pokeball', 'price': 600, 'catch_rate_modifier': 1.5, 'is_consumable': True},
        {'name': 'Ultra Ball', 'description': 'Ball ultra-performante.', 'item_type': 'pokeball', 'price': 1200, 'catch_rate_modifier': 2.0, 'is_consumable': True},
        {'name': 'Master Ball', 'description': 'La meilleure Ball. Capture a coup sur.', 'item_type': 'pokeball', 'price': 0, 'catch_rate_modifier': 255.0, 'is_consumable': True},
        {'name': 'Safari Ball', 'description': 'Ball speciale de la Zone Safari.', 'item_type': 'pokeball', 'price': 0, 'catch_rate_modifier': 1.5, 'is_consumable': True},
        # POKEBALLS spéciales
        {'name': 'Net Ball', 'description': "Efficace contre les Pokémon de type Eau ou Insecte.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 3.0, 'is_consumable': True},
        {'name': 'Dive Ball', 'description': "Efficace sous l'eau ou contre les Pokémon aquatiques.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 3.5, 'is_consumable': True},
        {'name': 'Nest Ball', 'description': "Plus efficace contre les Pokémon de bas niveau.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 1.0, 'is_consumable': True}, # To implement in pokeballItem class catch_rate_modifier = pokemon_level: (40 - pokemon_level) / 10 if pokemon_level < 30 else 1.0
        {'name': 'Repeat Ball', 'description': "Efficace contre les Pokémon déjà capturés.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 3.0, 'is_consumable': True},
        {'name': 'Timer Ball', 'description': "Plus efficace après plusieurs tours.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 1.0, 'is_consumable': True}, # To implement in pokeballItem class catch_rate_modifier = turn: 1 + (turn / 10)
        {'name': 'Dusk Ball', 'description': "Efficace la nuit ou dans les grottes.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 3.5, 'is_consumable': True},
        {'name': 'Quick Ball', 'description': "Efficace si utilisée en premier tour.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 4.0, 'is_consumable': True},
        {'name': 'Heal Ball', 'description': "Soigne les problèmes de statut du Pokémon capturé.", 'item_type': 'pokeball', 'price': 300, 'catch_rate_modifier': 1.0, 'is_consumable': True},
        {'name': 'Luxury Ball', 'description': "Améliore l'amitié du Pokémon capturé.", 'item_type': 'pokeball', 'price': 1200, 'catch_rate_modifier': 1.0, 'is_consumable': True},
        {'name': 'Premier Ball', 'description': "Une Poke Ball commémorative.", 'item_type': 'pokeball', 'price': 200, 'catch_rate_modifier': 1.0, 'is_consumable': True},
        {'name': 'Cherry Ball', 'description': "Efficace contre les Pokémon avec une évolution unique.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 3.0, 'is_consumable': True},
        {'name': 'Fast Ball', 'description': "Efficace contre les Pokémon rapides.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 3.0, 'is_consumable': True},
        {'name': 'Level Ball', 'description': "Plus efficace contre les Pokémon de niveau inférieur.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 1.0, 'is_consumable': True},# To implement in pokeballItem class catch_rate_modifier = user_level, pokemon_level: (4 * user_level / pokemon_level) if user_level > pokemon_level else 1.0
        {'name': 'Lure Ball', 'description': "Efficace contre les Pokémon pêchés.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 3.0, 'is_consumable': True},
        {'name': 'Heavy Ball', 'description': "Plus efficace contre les Pokémon lourds.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 1.0, 'is_consumable': True}, # To implement in pokeballItem class catch_rate_modifier = weight: (weight / 10) if weight > 200 else 1.0
        {'name': 'Love Ball', 'description': "Efficace contre les Pokémon du sexe opposé.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 8.0, 'is_consumable': True},
        {'name': 'Moon Ball', 'description': "Efficace contre les Pokémon qui évoluent avec une Pierre Lune.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 4.0, 'is_consumable': True},
        {'name': 'Friend Ball', 'description': "Le Pokémon capturé a une amitié instantanée maximale.", 'item_type': 'pokeball', 'price': 1000, 'catch_rate_modifier': 1.0, 'is_consumable': True},
        {'name': 'Sport Ball', 'description': "Une Poke Ball spéciale pour les concours.", 'item_type': 'pokeball', 'price': 0, 'catch_rate_modifier': 1.5, 'is_consumable': True},
        {'name': 'Park Ball', 'description': "Utilisée dans le Parc des Amis.", 'item_type': 'pokeball', 'price': 0, 'catch_rate_modifier': 1.0, 'is_consumable': True},
        {'name': 'Dream Ball', 'description': "Utilisée dans le Monde des Rêves.", 'item_type': 'pokeball', 'price': 0, 'catch_rate_modifier': 3.0, 'is_consumable': True},
        {'name': 'Beast Ball', 'description': "Spéciale pour les Ultra-Chimères.", 'item_type': 'pokeball', 'price': 0, 'catch_rate_modifier': 0.1, 'is_consumable': True},

        # PIERRES D EVOLUTION
        {'name': 'Fire Stone', 'description': 'Fait evoluer Goupix, Caninos, Evoli (Pyroli).', 'item_type': 'evolution', 'price': 2100, 'is_consumable': True},
        {'name': 'Water Stone', 'description': 'Fait evoluer Ptitard, Stari, Evoli (Aquali).', 'item_type': 'evolution', 'price': 2100, 'is_consumable': True},
        {'name': 'Thunder Stone', 'description': 'Fait evoluer Pikachu, Evoli (Voltali).', 'item_type': 'evolution', 'price': 2100, 'is_consumable': True},
        {'name': 'Leaf Stone', 'description': 'Fait evoluer Phytofali, Ortide, Exekul.', 'item_type': 'evolution', 'price': 2100, 'is_consumable': True},
        {'name': 'Moon Stone', 'description': 'Fait evoluer Melo, Nidorina, Nidorino, Melodelfe, Mystherbe.', 'item_type': 'evolution', 'price': 2100, 'is_consumable': True},

        # OBJETS TENUS
        {'name': 'Lucky Egg', 'description': 'Augmente l experience gagnee.', 'item_type': 'held', 'price': 0, 'held_effect': 'exp_boost', 'is_consumable': False},
        {'name': 'Leftovers', 'description': 'Restaure un peu de HP a chaque tour.', 'item_type': 'held', 'price': 0, 'held_effect': 'hp_regen', 'is_consumable': False},

        # OBJETS DE COMBAT
        {'name': 'X Attack', 'description': 'Augmente l Attaque en combat.', 'item_type': 'battle', 'price': 500, 'is_consumable': True},
        {'name': 'X Defense', 'description': 'Augmente la Defense en combat.', 'item_type': 'battle', 'price': 550, 'is_consumable': True},
        {'name': 'X Speed', 'description': 'Augmente la Vitesse en combat.', 'item_type': 'battle', 'price': 350, 'is_consumable': True},
        {'name': 'X Special', 'description': 'Augmente l Attaque Speciale en combat.', 'item_type': 'battle', 'price': 350, 'is_consumable': True},
        {'name': 'Guard Spec.', 'description': 'Empeche la baisse de stats pendant 5 tours.', 'item_type': 'battle', 'price': 700, 'is_consumable': True},
        {'name': 'Dire Hit', 'description': 'Augmente le taux de coup critique.', 'item_type': 'battle', 'price': 650, 'is_consumable': True},

        # OBJETS CLES
        {'name': 'Escape Rope', 'description': 'Permet de s echapper d une grotte.', 'item_type': 'key', 'price': 550, 'is_consumable': True},
        {'name': 'Bicycle', 'description': 'Velo ultra-leger pour se deplacer rapidement.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Old Rod', 'description': 'Vieille canne a peche (Pokemon Eau basiques).', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Good Rod', 'description': 'Canne a peche correcte (Pokemon Eau moyens).', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Super Rod', 'description': 'Meilleure canne a peche (Pokemon Eau rares).', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Silph Scope', 'description': 'Identifie les Pokemon fantomes dans la Tour Pokemon.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Poke Flute', 'description': 'Reveille les Pokemon endormis, notamment Ronflex.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Card Key', 'description': 'Carte magnetique pour la Tour Sylphe.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Town Map', 'description': 'Carte de Kanto offerte par le rival.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'S.S. Ticket', 'description': 'Ticket pour le SS Anne.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Dome Fossil', 'description': 'Ressuscite Kabuto.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Helix Fossil', 'description': 'Ressuscite Amonita.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Old Amber', 'description': 'Ressuscite Aerodactyl.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Coin Case', 'description': 'Porte-monnaie pour les Pokeocoins du Casino.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
        {'name': 'Itemfinder', 'description': 'Detecte les objets caches sur le sol.', 'item_type': 'key', 'price': 0, 'is_consumable': False},
    ]

    for item_data in items_data:
        Item.objects.get_or_create(
            name=item_data['name'],
            defaults=item_data
        )

    logging.info(f"[+] {len(items_data)} objets crees/verifies")


def initialize_gym_leaders():
    """Initialise les 8 Champions d'Arène de Kanto"""
    
    logging.info("[*] Initialisation des Champions d'Arène...")
    
    # Récupérer les types
    types = {t.name: t for t in PokemonType.objects.all()}
    
    # Récupérer les Pokémon
    def get_pokemon(name):
        return Pokemon.objects.get(name=name)
    
    # Récupérer les moves
    def get_moves(move_names):
        return [PokemonMove.objects.get(name=name) for name in move_names]
    
    # ============================================================================
    # BROCK - Pewter City (Roche)
    # ============================================================================
    brock_team = [
        {
            'species': get_pokemon('Geodude'),
            'level': 12,
            'moves': get_moves(['Tackle', 'Defense Curl'])
        },
        {
            'species': get_pokemon('Onix'),
            'level': 14,
            'moves': get_moves(['Tackle', 'Screech', 'Bind', 'Rock Throw'])
        }
    ]
    
    create_gym_leader(
        username='Brock',
        gym_name='Pewter Gym',
        city='Pewter City',
        badge_name='Boulder Badge',
        specialty_type=types['rock'],
        badge_order=1,
        team_data=brock_team
    )
    
    # ============================================================================
    # MISTY - Cerulean City (Eau)
    # ============================================================================
    misty_team = [
        {
            'species': get_pokemon('Staryu'),
            'level': 18,
            'moves': get_moves(['Tackle', 'Water Gun'])
        },
        {
            'species': get_pokemon('Starmie'),
            'level': 21,
            'moves': get_moves(['Tackle', 'Water Gun', 'Bubble Beam'])
        }
    ]
    
    create_gym_leader(
        username='Misty',
        gym_name='Cerulean Gym',
        city='Cerulean City',
        badge_name='Cascade Badge',
        specialty_type=types['water'],
        badge_order=2,
        team_data=misty_team
    )
    
    # ============================================================================
    # LT. SURGE - Vermilion City (Électrique)
    # ============================================================================
    surge_team = [
        {
            'species': get_pokemon('Voltorb'),
            'level': 21,
            'moves': get_moves(['Tackle', 'Screech'])
        },
        {
            'species': get_pokemon('Pikachu'),
            'level': 18,
            'moves': get_moves(['Thunder Shock', 'Growl'])
        },
        {
            'species': get_pokemon('Raichu'),
            'level': 24,
            'moves': get_moves(['Thunder Shock', 'Growl', 'Thunder Wave'])
        }
    ]
    
    create_gym_leader(
        username='Lt. Surge',
        gym_name='Vermilion Gym',
        city='Vermilion City',
        badge_name='Thunder Badge',
        specialty_type=types['electric'],
        badge_order=3,
        team_data=surge_team
    )
    
    # ============================================================================
    # ERIKA - Celadon City (Plante)
    # ============================================================================
    erika_team = [
        {
            'species': get_pokemon('Victreebel'),
            'level': 29,
            'moves': get_moves(['Vine Whip', 'Poison Powder'])
        },
        {
            'species': get_pokemon('Tangela'),
            'level': 24,
            'moves': get_moves(['Vine Whip', 'Bind'])
        },
        {
            'species': get_pokemon('Vileplume'),
            'level': 29,
            'moves': get_moves(['Petal Dance'])
        }
    ]
    
    create_gym_leader(
        username='Erika',
        gym_name='Celadon Gym',
        city='Celadon City',
        badge_name='Rainbow Badge',
        specialty_type=types['grass'],
        badge_order=4,
        team_data=erika_team
    )
    
    # ============================================================================
    # KOGA - Fuchsia City (Poison)
    # ============================================================================
    koga_team = [
        {
            'species': get_pokemon('Koffing'),
            'level': 37,
            'moves': get_moves(['Tackle', 'Smog'])
        },
        {
            'species': get_pokemon('Muk'),
            'level': 39,
            'moves': get_moves(['Pound', 'Poison Gas'])
        },
        {
            'species': get_pokemon('Koffing'),
            'level': 37,
            'moves': get_moves(['Tackle', 'Smog'])
        },
        {
            'species': get_pokemon('Weezing'),
            'level': 43,
            'moves': get_moves(['Tackle', 'Smog', 'Self-Destruct'])
        }
    ]
    
    create_gym_leader(
        username='Koga',
        gym_name='Fuchsia Gym',
        city='Fuchsia City',
        badge_name='Soul Badge',
        specialty_type=types['poison'],
        badge_order=5,
        team_data=koga_team
    )
    
    # ============================================================================
    # SABRINA - Saffron City (Psy)
    # ============================================================================
    sabrina_team = [
        {
            'species': get_pokemon('Kadabra'),
            'level': 38,
            'moves': get_moves(['Psybeam', 'Confusion'])
        },
        {
            'species': get_pokemon('Mr. Mime'),
            'level': 37,
            'moves': get_moves(['Confusion', 'Barrier'])
        },
        {
            'species': get_pokemon('Venomoth'),
            'level': 38,
            'moves': get_moves(['Psybeam', 'Leech Life'])
        },
        {
            'species': get_pokemon('Alakazam'),
            'level': 43,
            'moves': get_moves(['Psybeam', 'Recover', 'Psychic'])
        }
    ]
    
    create_gym_leader(
        username='Sabrina',
        gym_name='Saffron Gym',
        city='Saffron City',
        badge_name='Marsh Badge',
        specialty_type=types['psychic'],
        badge_order=6,
        team_data=sabrina_team
    )
    
    # ============================================================================
    # BLAINE - Cinnabar Island (Feu)
    # ============================================================================
    blaine_team = [
        {
            'species': get_pokemon('Growlithe'),
            'level': 42,
            'moves': get_moves(['Bite', 'Roar', 'Ember'])
        },
        {
            'species': get_pokemon('Ponyta'),
            'level': 40,
            'moves': get_moves(['Tackle', 'Growl', 'Ember'])
        },
        {
            'species': get_pokemon('Rapidash'),
            'level': 42,
            'moves': get_moves(['Tackle', 'Growl', 'Ember'])
        },
        {
            'species': get_pokemon('Arcanine'),
            'level': 47,
            'moves': get_moves(['Bite', 'Roar', 'Flamethrower'])
        }
    ]
    
    create_gym_leader(
        username='Blaine',
        gym_name='Cinnabar Gym',
        city='Cinnabar Island',
        badge_name='Volcano Badge',
        specialty_type=types['fire'],
        badge_order=7,
        team_data=blaine_team
    )
    
    # ============================================================================
    # GIOVANNI - Viridian City (Sol)
    # ============================================================================
    giovanni_team = [
        {
            'species': get_pokemon('Rhyhorn'),
            'level': 45,
            'moves': get_moves(['Horn Attack', 'Stomp'])
        },
        {
            'species': get_pokemon('Dugtrio'),
            'level': 42,
            'moves': get_moves(['Slash', 'Dig'])
        },
        {
            'species': get_pokemon('Nidoqueen'),
            'level': 44,
            'moves': get_moves(['Scratch', 'Body Slam'])
        },
        {
            'species': get_pokemon('Nidoking'),
            'level': 45,
            'moves': get_moves(['Thrash', 'Earthquake'])
        },
        {
            'species': get_pokemon('Rhydon'),
            'level': 50,
            'moves': get_moves(['Horn Attack', 'Earthquake'])
        }
    ]
    
    create_gym_leader(
        username='Giovanni',
        gym_name='Viridian Gym',
        city='Viridian City',
        badge_name='Earth Badge',
        specialty_type=types['ground'],
        badge_order=8,
        team_data=giovanni_team
    )
    
    logging.info("[+] 8 Champions d'Arène créés")

def initialize_rival_battles():
    """
    Peuple les RivalTemplate — templates statiques des combats de rival.

    NE crée PLUS de Trainer directement.  Les Trainer NPC sont générés
    à la demande par PlayerRival.spawn_for_player() lors du choix du starter
    (choose_starter_view), ce qui garantit :
      - Un Trainer unique par joueur (pas de collision de username).
      - Des équipes adaptées au starter choisi par chaque joueur.
      - Compatibilité multi-joueurs complète.

    Un RivalTemplate par (quest_id × player_starter_match) est créé,
    soit 3 templates pour le combat 1 (un par starter joueur) et un seul
    template "any" pour les combats 2-8 (le starter est inclus dans team_data
    via le champ "species" résolu dynamiquement au spawn).

    La colonne team_data est un JSON pur (noms de Pokémon et de moves en string)
    — les objets Django sont résolus dans spawn_for_player().
    """
    from myPokemonApp.models import RivalTemplate

    logging.info("[*] Initialisation des RivalTemplate (combats Rival)...")

    FIXED_IVS_LV5  = {"iv_hp":10,"iv_attack":10,"iv_defense":10,
                       "iv_special_attack":10,"iv_special_defense":10,"iv_speed":10}
    FIXED_IVS_MID  = {"iv_hp":15,"iv_attack":15,"iv_defense":15,
                       "iv_special_attack":15,"iv_special_defense":15,"iv_speed":15}

    # Mapping : starter joueur → starter rival → ligne d'évolution
    RIVAL_STARTER_MAP = {
        'Bulbasaur':  'Charmander',
        'Charmander': 'Squirtle',
        'Squirtle':   'Bulbasaur',
    }
    EVOLUTIONS = {
        'Charmander': ['Charmander', 'Charmeleon', 'Charizard'],
        'Squirtle':   ['Squirtle',   'Wartortle',  'Blastoise'],
        'Bulbasaur':  ['Bulbasaur',  'Ivysaur',    'Venusaur'],
    }
    # Moves de base par starter rival au lv5
    STARTER_MOVES_LV5 = {
        'Charmander': ['Scratch', 'Growl'],
        'Squirtle':   ['Tackle',  'Tail Whip'],
        'Bulbasaur':  ['Tackle',  'Growl'],
    }
    # Moves évol. 1 par combat
    STARTER_MOVES_LV9 = {
        'Charmander': ['Scratch', 'Growl', 'Ember'],
        'Squirtle':   ['Tackle',  'Tail Whip', 'Bubble'],
        'Bulbasaur':  ['Tackle',  'Growl', 'Leech Seed'],
    }
    STARTER_MOVES_LV18 = {
        'Charmander': ['Scratch', 'Growl', 'Ember', 'Leer'],
        'Squirtle':   ['Tackle',  'Tail Whip', 'Bubble', 'Water Gun'],
        'Bulbasaur':  ['Tackle',  'Growl', 'Leech Seed', 'Vine Whip'],
    }

    templates_data = []

    # =========================================================================
    # COMBAT 1 : BOURG PALETTE (lv5) — 3 versions per-starter joueur
    # IVs fixes 10 + nature Hardy → stats prévisibles, combat équilibré.
    # =========================================================================
    COMBAT1_DIALOGUES = {
        # player_starter → (intro, defeat, victory, pre_battle, post_battle)
        'Bulbasaur': (
            "Hé ! Le Prof. Chen m'a donné Salamèche ! Il bat le type Plante — vas-y !",
            "Quoi ?! J'ai perdu ?! Salamèche, on va s'entraîner encore plus fort !",
            "Haha ! Salamèche est trop fort pour ton Bulbizarre !",
            "Attends ! Vérifions nos Pokémon ! Allez, je te défie !",
            "Hein ?! Incroyable... Je dois m'entraîner plus dur.",
        ),
        'Charmander': (
            "Ha ! Le Prof. Chen m'a confié Carapuce ! L'Eau contre le Feu, bonne chance !",
            "Incroyable... Carapuce a perdu. L'entraînement va tout changer !",
            "Trop facile ! L'Eau écrase le Feu, c'est la loi de la nature !",
            "Attends ! Vérifions nos Pokémon ! Allez, je te défie !",
            "Carapuce... on a perdu. Mais je reviendrai plus fort !",
        ),
        'Squirtle': (
            "J'ai pris Bulbizarre — la Plante bat l'Eau ! Prouve-moi que Carapuce vaut quelque chose !",
            "Bulbizarre... on a perdu. C'est promis, la prochaine fois sera différente !",
            "Oui ! La Plante domine l'Eau ! Bulbizarre est imbattable !",
            "Attends ! Vérifions nos Pokémon ! Allez, je te défie !",
            "Bulbizarre... on a vraiment perdu. Je dois travailler plus dur !",
        ),
    }
    for player_starter, rival_starter in RIVAL_STARTER_MAP.items():
        intro, defeat, victory, pre, post = COMBAT1_DIALOGUES[player_starter]
        templates_data.append({
            'quest_id':            'rival_pallet_town',
            'combat_order':        1,
            'rival_starter':       rival_starter,
            'player_starter_match': player_starter,
            'intro_text':          intro,
            'defeat_text':         defeat,
            'victory_text':        victory,
            'pre_battle_text':     pre,
            'post_battle_text':    post,
            'money_reward':        175,
            'team_data': [{
                'species':       rival_starter,
                'level':         5,
                'moves':         STARTER_MOVES_LV5[rival_starter],
                'fixed_ivs':     FIXED_IVS_LV5,
                'fixed_nature':  'Hardy',
            }],
        })

    # =========================================================================
    # COMBATS 2–8 : 3 versions par starter joueur
    # =========================================================================

    for player_starter, rival_starter in RIVAL_STARTER_MAP.items():
        evo = EVOLUTIONS[rival_starter]   # [base, evo1, evo2]

        # Pokémon variable selon starter rival
        third_pokemon = {
            'Charmander': {'Bulbasaur': 'Growlithe', 'Squirtle': 'Exeggcute'},
            'Squirtle':   {'Bulbasaur': 'Gyarados',  'Charmander': 'Exeggcute'},
            'Bulbasaur':  {'Charmander': 'Gyarados', 'Squirtle': 'Growlithe'},
        }

        # ─── COMBAT 2 : ROUTE 22 (lv9) ────────────────────────────────────
        templates_data.append({
            'quest_id':            'rival_route_22',
            'combat_order':        2,
            'rival_starter':       rival_starter,
            'player_starter_match': player_starter,
            'intro_text':          "Tu crois être fort? Voyons voir!",
            'defeat_text':         "Grrr... Tu t'améliores. Mais ça ne durera pas !",
            'victory_text':        "Comme d'habitude, je suis le meilleur !",
            'pre_battle_text':     "Hé ! Attends un peu ! Je savais que tu viendrais ici. Allez !",
            'post_battle_text':    "Quoi ?! Tu as gagné ?! Peu importe. La prochaine fois ce sera différent.",
            'money_reward':        280,
            'team_data': [
                {'species': 'Pidgey', 'level': 9, 'moves': ['Tackle', 'Gust']},
                {'species': evo[0],   'level': 9, 'moves': STARTER_MOVES_LV9[rival_starter]},
            ],
        })

        # ─── COMBAT 3 : CERULEAN CITY (lv18) ──────────────────────────────
        templates_data.append({
            'quest_id':            'rival_cerulean',
            'combat_order':        3,
            'rival_starter':       rival_starter,
            'player_starter_match': player_starter,
            'intro_text':          "Je t'attendais! Prépare-toi!",
            'defeat_text':         "Encore ?! Bah... La prochaine fois je te battrai facilement.",
            'victory_text':        "Mes Pokémon s'améliorent de jour en jour !",
            'pre_battle_text':     "Encore toi ! Mes Pokémon ont grandi depuis la dernière fois. Prépare-toi !",
            'post_battle_text':    "Encore ?! Bah... La prochaine fois je te battrai facilement.",
            'money_reward':        640,
            'team_data': [
                {'species': 'Pidgeotto', 'level': 17, 'moves': ['Tackle', 'Gust', 'Sand Attack']},
                {'species': 'Abra',      'level': 16, 'moves': ['Teleport']},
                {'species': 'Rattata',   'level': 15, 'moves': ['Tackle', 'Tail Whip', 'Quick Attack']},
                {'species': evo[1],      'level': 18, 'moves': STARTER_MOVES_LV18[rival_starter]},
            ],
        })

        # ─── COMBAT 4 : S.S. ANNE (lv20) ──────────────────────────────────
        starter_moves_lv20 = {
            'Charmander': ['Scratch', 'Ember', 'Leer', 'Rage'],
            'Squirtle':   ['Tackle',  'Bubble', 'Water Gun', 'Bite'],
            'Bulbasaur':  ['Tackle',  'Leech Seed', 'Vine Whip', 'Poison Powder'],
        }
        templates_data.append({
            'quest_id':            'rival_ss_anne',
            'combat_order':        4,
            'rival_starter':       rival_starter,
            'player_starter_match': player_starter,
            'intro_text':          "Toi ici?! On va régler ça maintenant!",
            'defeat_text':         "Comment... Tu me bats encore !",
            'victory_text':        "Haha ! Je savais que j'étais plus fort !",
            'pre_battle_text':     "Encore toi ! Sur ce bateau, c'est moi le maître !",
            'post_battle_text':    "Pfff... La chance était de ton côté. C'est tout.",
            'money_reward':        720,
            'team_data': [
                {'species': 'Pidgeotto', 'level': 19, 'moves': ['Gust', 'Sand Attack', 'Quick Attack']},
                {'species': 'Raticate',  'level': 16, 'moves': ['Tackle', 'Tail Whip', 'Hyper Fang']},
                {'species': 'Kadabra',   'level': 18, 'moves': ['Teleport', 'Kinesis', 'Confusion']},
                {'species': evo[1],      'level': 20, 'moves': starter_moves_lv20[rival_starter]},
            ],
        })

        # ─── COMBAT 5 : TOUR POKÉMON (lv25) ───────────────────────────────
        companion3 = 'Gyarados' if rival_starter == 'Charmander' else 'Growlithe'
        companion4 = 'Exeggcute' if rival_starter != 'Bulbasaur' else 'Meowth'
        companion3_moves = (
            ['Bite', 'Dragon Rage', 'Leer'] if rival_starter == 'Charmander'
            else ['Bite', 'Roar', 'Ember']
        )
        companion4_moves = (
            ['Barrage', 'Hypnosis'] if rival_starter != 'Bulbasaur'
            else ['Scratch', 'Growl', 'Bite']
        )
        starter_moves_lv25 = {
            'Charmander': ['Ember', 'Leer', 'Rage', 'Slash'],
            'Squirtle':   ['Water Gun', 'Bite', 'Withdraw', 'Skull Bash'],
            'Bulbasaur':  ['Vine Whip', 'Poison Powder', 'Sleep Powder', 'Razor Leaf'],
        }
        templates_data.append({
            'quest_id':            'rival_pokemon_tower',
            'combat_order':        5,
            'rival_starter':       rival_starter,
            'player_starter_match': player_starter,
            'intro_text':          "Qu'est-ce que tu fais ici? Ton Pokémon est-il mort?",
            'defeat_text':         "Tu m'as encore battu... Je dois revoir ma stratégie.",
            'victory_text':        "Cette tour est à moi ! Retourne d'où tu viens !",
            'pre_battle_text':     "Tu es venu chercher la même chose que moi ? Montre-moi si tu le mérites !",
            'post_battle_text':    "J'aurais dû mieux m'entraîner avant de venir ici.",
            'money_reward':        1000,
            'team_data': [
                {'species': 'Pidgeotto',  'level': 25, 'moves': ['Gust', 'Sand Attack', 'Quick Attack', 'Wing Attack']},
                {'species': companion3,   'level': 23, 'moves': companion3_moves},
                {'species': companion4,   'level': 22, 'moves': companion4_moves},
                {'species': 'Kadabra',    'level': 20, 'moves': ['Teleport', 'Kinesis', 'Confusion', 'Psybeam']},
                {'species': evo[1],       'level': 25, 'moves': starter_moves_lv25[rival_starter]},
            ],
        })

        # ─── COMBAT 6 : SILPH CO. (lv37) ──────────────────────────────────
        if rival_starter == 'Bulbasaur':
            spe3, spe3m = 'Growlithe',  ['Bite', 'Roar', 'Ember', 'Take Down']
            spe4, spe4m = 'Gyarados',   ['Bite', 'Dragon Rage', 'Leer', 'Hydro Pump']
        elif rival_starter == 'Squirtle':
            spe3, spe3m = 'Exeggcute',  ['Barrage', 'Hypnosis', 'Reflect']
            spe4, spe4m = 'Growlithe',  ['Bite', 'Roar', 'Ember', 'Take Down']
        else:  # Charmander
            spe3, spe3m = 'Gyarados',   ['Bite', 'Dragon Rage', 'Leer', 'Hydro Pump']
            spe4, spe4m = 'Exeggcute',  ['Barrage', 'Hypnosis', 'Reflect']
        starter_moves_lv40 = {
            'Charmander': ['Ember', 'Leer', 'Rage', 'Slash'],
            'Squirtle':   ['Water Gun', 'Bite', 'Withdraw', 'Hydro Pump'],
            'Bulbasaur':  ['Vine Whip', 'Poison Powder', 'Razor Leaf', 'Solar Beam'],
        }
        templates_data.append({
            'quest_id':            'rival_silph_co',
            'combat_order':        6,
            'rival_starter':       rival_starter,
            'player_starter_match': player_starter,
            'intro_text':          "Je vais te montrer qui est le meilleur!",
            'defeat_text':         "Encore toi... C'est agaçant !",
            'victory_text':        "Bien sûr que j'ai gagné ! Je suis le futur Champion !",
            'pre_battle_text':     "Tu as du culot de venir jusqu'ici. Mais tu ne passeras pas !",
            'post_battle_text':    "Tch... tu as encore gagné. Va, monte voir le Président.",
            'money_reward':        2800,
            'team_data': [
                {'species': 'Pidgeot',   'level': 37, 'moves': ['Wing Attack', 'Sand Attack', 'Quick Attack', 'Mirror Move']},
                {'species': spe3,        'level': 35, 'moves': spe3m},
                {'species': 'Alakazam',  'level': 35, 'moves': ['Teleport', 'Kinesis', 'Psybeam', 'Recover']},
                {'species': spe4,        'level': 35, 'moves': spe4m},
                {'species': evo[2],      'level': 40, 'moves': starter_moves_lv40[rival_starter]},
            ],
        })

        # ─── COMBAT 7 : ROUTE 22 AVANT LA LIGUE (lv47) ────────────────────
        if rival_starter == 'Bulbasaur':
            spe5, spe5m = 'Growlithe',  ['Bite', 'Roar', 'Flamethrower', 'Take Down']
            spe6, spe6m = 'Gyarados',   ['Bite', 'Dragon Rage', 'Leer', 'Hydro Pump']
        elif rival_starter == 'Squirtle':
            spe5, spe5m = 'Exeggcute',  ['Barrage', 'Hypnosis', 'Solar Beam', 'Reflect']
            spe6, spe6m = 'Arcanine',   ['Bite', 'Roar', 'Flamethrower', 'Take Down']
        else:  # Charmander
            spe5, spe5m = 'Gyarados',   ['Bite', 'Dragon Rage', 'Leer', 'Hydro Pump']
            spe6, spe6m = 'Exeggutor',  ['Barrage', 'Hypnosis', 'Solar Beam', 'Stomp']
        starter_moves_lv53 = {
            'Charmander': ['Flamethrower', 'Fire Spin', 'Slash', 'Fire Blast'],
            'Squirtle':   ['Hydro Pump', 'Bite', 'Ice Beam', 'Skull Bash'],
            'Bulbasaur':  ['Razor Leaf', 'Poison Powder', 'Solar Beam', 'Sleep Powder'],
        }
        templates_data.append({
            'quest_id':            'rival_route_22_final',
            'combat_order':        7,
            'rival_starter':       rival_starter,
            'player_starter_match': player_starter,
            'intro_text':          "Tu n'iras pas plus loin! Je vais te prouver ma supériorité!",
            'defeat_text':         "Pfff... Vas-y alors. Mais ne crois pas que tu vas gagner facilement là-haut.",
            'victory_text':        "Je savais que tu n'étais pas prêt pour la Ligue !",
            'pre_battle_text':     "Tu veux affronter la Ligue ? Tu devras d'abord passer par moi.",
            'post_battle_text':    "Pfff... Vas-y alors. Mais ne crois pas que tu vas gagner facilement là-haut.",
            'money_reward':        4700,
            'team_data': [
                {'species': 'Pidgeot',   'level': 47, 'moves': ['Wing Attack', 'Mirror Move', 'Sky Attack', 'Quick Attack']},
                {'species': 'Rhyhorn',   'level': 45, 'moves': ['Horn Attack', 'Stomp', 'Tail Whip', 'Fury Attack']},
                {'species': spe5,        'level': 45, 'moves': spe5m},
                {'species': 'Alakazam',  'level': 47, 'moves': ['Psychic', 'Recover', 'Psybeam', 'Reflect']},
                {'species': spe6,        'level': 45, 'moves': spe6m},
                {'species': evo[2],      'level': 53, 'moves': starter_moves_lv53[rival_starter]},
            ],
        })

        # ─── COMBAT 8 : CHAMPION (lv61-65) ────────────────────────────────
        if rival_starter == 'Bulbasaur':
            champ5, champ5m = 'Arcanine',  ['Bite', 'Roar', 'Flamethrower', 'Take Down']
            champ6, champ6m = 'Gyarados',  ['Bite', 'Dragon Rage', 'Hydro Pump', 'Hyper Beam']
        elif rival_starter == 'Squirtle':
            champ5, champ5m = 'Exeggutor', ['Barrage', 'Hypnosis', 'Solar Beam', 'Stomp']
            champ6, champ6m = 'Arcanine',  ['Bite', 'Roar', 'Flamethrower', 'Take Down']
        else:  # Charmander
            champ5, champ5m = 'Gyarados',  ['Bite', 'Dragon Rage', 'Hydro Pump', 'Hyper Beam']
            champ6, champ6m = 'Exeggutor', ['Barrage', 'Hypnosis', 'Solar Beam', 'Stomp']
        starter_moves_lv65 = {
            'Charmander': ['Flamethrower', 'Fire Spin', 'Slash', 'Fire Blast'],
            'Squirtle':   ['Hydro Pump', 'Bite', 'Ice Beam', 'Blizzard'],
            'Bulbasaur':  ['Razor Leaf', 'Poison Powder', 'Solar Beam', 'Sleep Powder'],
        }
        templates_data.append({
            'quest_id':            'rival_champion',
            'combat_order':        8,
            'rival_starter':       rival_starter,
            'player_starter_match': player_starter,
            'intro_text':          "J'ai battu la Ligue et je t'attendais! Voyons si tu es à la hauteur!",
            'defeat_text':         "Perdu... contre toi... Je dois revoir toute ma façon de dresser.",
            'victory_text':        "Je suis et resterai le meilleur Dresseur du monde !",
            'pre_battle_text':     "J'ai battu les 4 As en premier. Je suis le Champion ! Tu n'as aucune chance.",
            'post_battle_text':    "Perdu... contre toi... Je dois revoir toute ma façon de dresser. Tu mérites vraiment ce titre.",
            'money_reward':        10000,
            'team_data': [
                {'species': 'Pidgeot',   'level': 61, 'moves': ['Wing Attack', 'Mirror Move', 'Sky Attack', 'Whirlwind']},
                {'species': 'Alakazam',  'level': 59, 'moves': ['Psychic', 'Recover', 'Psybeam', 'Reflect']},
                {'species': 'Rhydon',    'level': 61, 'moves': ['Horn Attack', 'Stomp', 'Earthquake', 'Horn Drill']},
                {'species': champ5,      'level': 61, 'moves': champ5m},
                {'species': champ6,      'level': 61, 'moves': champ6m},
                {'species': evo[2],      'level': 65, 'moves': starter_moves_lv65[rival_starter]},
            ],
        })

    # ── Persistance idempotente (get_or_create sur quest_id + player_starter) ─
    created_count = 0
    for tdata in templates_data:
        quest_id_val            = tdata['quest_id']
        player_starter_match_val = tdata['player_starter_match']
        defaults = {k: v for k, v in tdata.items()
                    if k not in ('quest_id', 'player_starter_match')}
        _, created = RivalTemplate.objects.update_or_create(
            quest_id=quest_id_val,
            player_starter_match=player_starter_match_val,
            defaults=defaults,
        )
        if created:
            created_count += 1

    total = RivalTemplate.objects.count()
    logging.info(f"[+] RivalTemplate : {created_count} créés, {total} au total")



def initialize_elite_four():
    """Initialise le Conseil des 4"""
    
    logging.info("[*] Initialisation du Conseil des 4...")
    
    def get_pokemon(name):
        return Pokemon.objects.get(name=name)
    
    def get_moves(move_names):
        return [PokemonMove.objects.get(name=name) for name in move_names]
    
    # ============================================================================
    # LORELEI (Glace)
    # ============================================================================
    lorelei_team = [
        {
            'species': get_pokemon('Dewgong'),
            'level': 54,
            'moves': get_moves(['Aurora Beam', 'Ice Beam'])
        },
        {
            'species': get_pokemon('Cloyster'),
            'level': 53,
            'moves': get_moves(['Ice Beam', 'Withdraw'])
        },
        {
            'species': get_pokemon('Slowbro'),
            'level': 54,
            'moves': get_moves(['Surf', 'Psychic'])
        },
        {
            'species': get_pokemon('Jynx'),
            'level': 56,
            'moves': get_moves(['Ice Beam', 'Psychic'])
        },
        {
            'species': get_pokemon('Lapras'),
            'level': 56,
            'moves': get_moves(['Ice Beam', 'Surf', 'Body Slam'])
        }
    ]
    
    create_npc_trainer(
        username='Lorelei',
        trainer_type='elite_four',
        location='Plateau Indigo',
        team_data=lorelei_team,
        intro_text="Bienvenue dans le Conseil des 4. Je suis Lorelei, maître du type Glace!"
    )
    
    # ============================================================================
    # BRUNO (Combat)
    # ============================================================================
    bruno_team = [
        {
            'species': get_pokemon('Onix'),
            'level': 53,
            'moves': get_moves(['Rock Throw', 'Earthquake'])
        },
        {
            'species': get_pokemon('Hitmonchan'),
            'level': 55,
            'moves': get_moves(['Fire Punch', 'Ice Punch', 'Thunder Punch'])
        },
        {
            'species': get_pokemon('Hitmonlee'),
            'level': 55,
            'moves': get_moves(['Jump Kick', 'High Jump Kick'])
        },
        {
            'species': get_pokemon('Onix'),
            'level': 56,
            'moves': get_moves(['Rock Throw', 'Earthquake'])
        },
        {
            'species': get_pokemon('Machamp'),
            'level': 58,
            'moves': get_moves(['Karate Chop', 'Submission', 'Seismic Toss'])
        }
    ]
    
    create_npc_trainer(
        username='Bruno',
        trainer_type='elite_four',
        location='Plateau Indigo',
        team_data=bruno_team,
        intro_text="Je suis Bruno, maître du Combat!"
    )
    
    # ============================================================================
    # AGATHA (Spectre/Poison)
    # ============================================================================
    agatha_team = [
        {
            'species': get_pokemon('Gengar'),
            'level': 56,
            'moves': get_moves(['Hypnosis', 'Dream Eater', 'Confuse Ray'])
        },
        {
            'species': get_pokemon('Golbat'),
            'level': 56,
            'moves': get_moves(['Bite', 'Supersonic', 'Wing Attack'])
        },
        {
            'species': get_pokemon('Haunter'),
            'level': 55,
            'moves': get_moves(['Hypnosis', 'Lick', 'Night Shade'])
        },
        {
            'species': get_pokemon('Arbok'),
            'level': 58,
            'moves': get_moves(['Bite', 'Glare', 'Acid'])
        },
        {
            'species': get_pokemon('Gengar'),
            'level': 60,
            'moves': get_moves(['Hypnosis', 'Dream Eater', 'Psychic'])
        }
    ]
    
    create_npc_trainer(
        username='Agatha',
        trainer_type='elite_four',
        location='Plateau Indigo',
        team_data=agatha_team,
        intro_text="Je suis Agatha, maître des Spectres!"
    )
    
    # ============================================================================
    # LANCE (Dragon)
    # ============================================================================
    lance_team = [
        {
            'species': get_pokemon('Gyarados'),
            'level': 58,
            'moves': get_moves(['Hydro Pump', 'Dragon Rage', 'Hyper Beam'])
        },
        {
            'species': get_pokemon('Dragonair'),
            'level': 56,
            'moves': get_moves(['Dragon Rage', 'Hyper Beam', 'Thunder Wave'])
        },
        {
            'species': get_pokemon('Dragonair'),
            'level': 56,
            'moves': get_moves(['Dragon Rage', 'Hyper Beam', 'Thunder Wave'])
        },
        {
            'species': get_pokemon('Aerodactyl'),
            'level': 60,
            'moves': get_moves(['Wing Attack', 'Hyper Beam'])
        },
        {
            'species': get_pokemon('Dragonite'),
            'level': 62,
            'moves': get_moves(['Dragon Rage', 'Hyper Beam', 'Blizzard'])
        }
    ]
    
    create_npc_trainer(
        username='Lance',
        trainer_type='elite_four',
        location='Plateau Indigo',
        team_data=lance_team,
        intro_text="Je suis Lance, maître des Dragons et dernier membre du Conseil des 4!"
    )
    
    logging.info("[+] Conseil des 4 créé")


def create_champion():
    """Crée le Champion de la Ligue"""
    
    logging.info("[*] Création du Champion...")
    
    def get_pokemon(name):
        return Pokemon.objects.get(name=name)
    
    def get_moves(move_names):
        return [PokemonMove.objects.get(name=name) for name in move_names]
    
    # Blue/Gary - équipe variable selon le starter du joueur
    # Version avec Blastoise (si le joueur a choisi Bulbasaur)
    champion_team = [
        {
            'species': get_pokemon('Pidgeot'),
            'level': 61,
            'moves': get_moves(['Wing Attack', 'Mirror Move'])
        },
        {
            'species': get_pokemon('Alakazam'),
            'level': 59,
            'moves': get_moves(['Psychic', 'Recover'])
        },
        {
            'species': get_pokemon('Rhydon'),
            'level': 61,
            'moves': get_moves(['Earthquake', 'Horn Drill'])
        },
        {
            'species': get_pokemon('Arcanine'),
            'level': 61,
            'moves': get_moves(['Flamethrower', 'Take Down'])
        },
        {
            'species': get_pokemon('Exeggutor'),
            'level': 61,
            'moves': get_moves(['Psychic', 'Egg Bomb'])
        },
        {
            'species': get_pokemon('Blastoise'),
            'level': 63,
            'moves': get_moves(['Hydro Pump', 'Ice Beam', 'Earthquake'])
        }
    ]
    
    create_npc_trainer(
        username='Blue',
        trainer_type='champion',
        location='Plateau Indigo',
        team_data=champion_team,
        intro_text="Je t'attendais! Je suis maintenant le Champion de la Ligue Pokémon!",
    )
    
    logging.info("[+] Champion créé")


def run_full_initialization():
    """Lance l'initialisation complète"""
    
    logging.info("="*60)
    logging.info("INITIALISATION DES OBJETS ET NPCS")
    logging.info("="*60)
    
    try:
        initialize_items()
        initialize_gym_leaders()
        initialize_rival_battles()
        initialize_elite_four()
        create_champion()
        
        logging.info("="*60)
        logging.info("[✓] INITIALISATION TERMINÉE AVEC SUCCÈS")
        logging.info("="*60)
        
    except Exception as e:
        logging.error(f"[✗] ERREUR LORS DE L'INITIALISATION: {e}")
        raise


# Point d'entrée pour Django shell
if __name__ == '__main__':
    run_full_initialization()