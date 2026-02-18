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


def initialize_npc_trainers():
    """Initialise les NPCs non majeurs de Kanto"""
    
    logging.info("[*] Initialisation des dresseurs NPCs...")
    
    # Fonctions helper
    def get_pokemon(name):
        return Pokemon.objects.get(name=name)
    
    def get_moves(move_names):
        return [PokemonMove.objects.get(name=name) for name in move_names]
    
    # ============================================================================
    # ROUTE 1 - Dresseurs débutants
    # ============================================================================
    
    create_npc_trainer(
        username='Youngster Ben',
        trainer_type='trainer',
        location='Route 1',
        team_data=[
            {
                'species': get_pokemon('Rattata'),
                'level': 6,
                'moves': get_moves(['Tackle', 'Tail Whip'])
            }
        ],
        intro_text="Hé! Tu veux te battre?"
    )
    
    create_npc_trainer(
        username='Youngster Calvin',
        trainer_type='trainer',
        location='Route 1',
        team_data=[
            {
                'species': get_pokemon('Spearow'),
                'level': 7,
                'moves': get_moves(['Peck'])
            }
        ],
        intro_text="Je suis nouveau dans le dressage!"
    )
    
    # ============================================================================
    # VIRIDIAN FOREST
    # ============================================================================
    
    create_npc_trainer(
        username='Bug Catcher Rick',
        trainer_type='trainer',
        location='Viridian Forest',
        team_data=[
            {
                'species': get_pokemon('Weedle'),
                'level': 6,
                'moves': get_moves(['Poison Sting'])
            },
            {
                'species': get_pokemon('Caterpie'),
                'level': 6,
                'moves': get_moves(['Tackle'])
            }
        ],
        intro_text="Les insectes sont les meilleurs!"
    )
    
    create_npc_trainer(
        username='Bug Catcher Doug',
        trainer_type='trainer',
        location='Viridian Forest',
        team_data=[
            {
                'species': get_pokemon('Weedle'),
                'level': 7,
                'moves': get_moves(['Poison Sting'])
            },
            {
                'species': get_pokemon('Kakuna'),
                'level': 7,
                'moves': get_moves(['Harden'])
            },
            {
                'species': get_pokemon('Weedle'),
                'level': 7,
                'moves': get_moves(['Poison Sting'])
            }
        ],
        intro_text="Ma collection d'insectes est la meilleure!"
    )
    
    create_npc_trainer(
        username='Bug Catcher Sammy',
        trainer_type='trainer',
        location='Viridian Forest',
        team_data=[
            {
                'species': get_pokemon('Weedle'),
                'level': 9,
                'moves': get_moves(['Poison Sting'])
            }
        ],
        intro_text="Les insectes sont cool!"
    )
    
    # ============================================================================
    # ROUTE 3
    # ============================================================================
    
    create_npc_trainer(
        username='Lass Janice',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {
                'species': get_pokemon('Pidgey'),
                'level': 9,
                'moves': get_moves(['Tackle', 'Gust'])
            },
            {
                'species': get_pokemon('Pidgey'),
                'level': 9,
                'moves': get_moves(['Tackle', 'Gust'])
            }
        ],
        intro_text="Mes oiseaux vont gagner!"
    )
    
    create_npc_trainer(
        username='Youngster Ben',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {
                'species': get_pokemon('Rattata'),
                'level': 8,
                'moves': get_moves(['Tackle', 'Tail Whip'])
            },
            {
                'species': get_pokemon('Ekans'),
                'level': 9,
                'moves': get_moves(['Wrap', 'Poison Sting'])
            }
        ],
        intro_text="Prêt à perdre?"
    )
    
    create_npc_trainer(
        username='Bug Catcher James',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {
                'species': get_pokemon('Caterpie'),
                'level': 11,
                'moves': get_moves(['Tackle'])
            },
            {
                'species': get_pokemon('Metapod'),
                'level': 11,
                'moves': get_moves(['Harden'])
            }
        ],
        intro_text="Les chenilles deviendront des papillons!"
    )
    
    create_npc_trainer(
        username='Lass Sally',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {
                'species': get_pokemon('Rattata'),
                'level': 10,
                'moves': get_moves(['Tackle', 'Tail Whip'])
            },
            {
                'species': get_pokemon('Nidoran♀'),
                'level': 10,
                'moves': get_moves(['Scratch', 'Tail Whip'])
            }
        ],
        intro_text="Tu aimes les Pokémon mignons?"
    )
    
    # ============================================================================
    # MT. MOON
    # ============================================================================
    
    create_npc_trainer(
        username='Lass Iris',
        trainer_type='trainer',
        location='Mt. Moon',
        team_data=[
            {
                'species': get_pokemon('Clefairy'),
                'level': 14,
                'moves': get_moves(['Pound', 'Growl'])
            }
        ],
        intro_text="Les Pokémon fée sont magnifiques!"
    )
    
    create_npc_trainer(
        username='Super Nerd Jovan',
        trainer_type='trainer',
        location='Mt. Moon',
        team_data=[
            {
                'species': get_pokemon('Magnemite'),
                'level': 11,
                'moves': get_moves(['Tackle', 'Sonic Boom'])
            },
            {
                'species': get_pokemon('Voltorb'),
                'level': 11,
                'moves': get_moves(['Tackle', 'Screech'])
            }
        ],
        intro_text="La science est la clé!"
    )
    
    create_npc_trainer(
        username='Hiker Marcos',
        trainer_type='trainer',
        location='Mt. Moon',
        team_data=[
            {
                'species': get_pokemon('Geodude'),
                'level': 10,
                'moves': get_moves(['Tackle', 'Defense Curl'])
            },
            {
                'species': get_pokemon('Geodude'),
                'level': 10,
                'moves': get_moves(['Tackle', 'Defense Curl'])
            },
            {
                'species': get_pokemon('Onix'),
                'level': 10,
                'moves': get_moves(['Tackle', 'Screech'])
            }
        ],
        intro_text="Les rochers sont solides!"
    )
    
    create_npc_trainer(
        username='Team Rocket Grunt',
        trainer_type='trainer',
        location='Mt. Moon',
        team_data=[
            {
                'species': get_pokemon('Rattata'),
                'level': 11,
                'moves': get_moves(['Tackle', 'Tail Whip'])
            },
            {
                'species': get_pokemon('Zubat'),
                'level': 11,
                'moves': get_moves(['Leech Life', 'Supersonic'])
            }
        ],
        intro_text="Prépare-toi, gamin!"
    )
    
    # ============================================================================
    # ROUTE 4
    # ============================================================================
    
    create_npc_trainer(
        username='Lass Crissy',
        trainer_type='trainer',
        location='Route 4',
        team_data=[
            {
                'species': get_pokemon('Pidgey'),
                'level': 31,
                'moves': get_moves(['Gust', 'Quick Attack'])
            },
            {
                'species': get_pokemon('Rattata'),
                'level': 31,
                'moves': get_moves(['Hyper Fang', 'Quick Attack'])
            }
        ],
        intro_text="C'est mon jour de chance!"
    )
    
    # ============================================================================
    # ROUTE 24 (NUGGET BRIDGE)
    # ============================================================================
    
    create_npc_trainer(
        username='Camper Liam',
        trainer_type='trainer',
        location='Route 24',
        team_data=[
            {
                'species': get_pokemon('Sandshrew'),
                'level': 14,
                'moves': get_moves(['Scratch', 'Defense Curl'])
            }
        ],
        intro_text="Le Nugget Bridge est célèbre!"
    )
    
    create_npc_trainer(
        username='Lass Ali',
        trainer_type='trainer',
        location='Route 24',
        team_data=[
            {
                'species': get_pokemon('Pidgey'),
                'level': 12,
                'moves': get_moves(['Gust', 'Sand Attack'])
            },
            {
                'species': get_pokemon('Nidoran♀'),
                'level': 14,
                'moves': get_moves(['Scratch', 'Poison Sting'])
            }
        ],
        intro_text="Bienvenue sur le pont!"
    )
    
    create_npc_trainer(
        username='Youngster Timmy',
        trainer_type='trainer',
        location='Route 24',
        team_data=[
            {
                'species': get_pokemon('Rattata'),
                'level': 14,
                'moves': get_moves(['Tackle', 'Hyper Fang'])
            },
            {
                'species': get_pokemon('Ekans'),
                'level': 14,
                'moves': get_moves(['Wrap', 'Poison Sting'])
            }
        ],
        intro_text="On va se battre!"
    )
    
    create_npc_trainer(
        username='Team Rocket Grunt',
        trainer_type='trainer',
        location='Route 24',
        team_data=[
            {
                'species': get_pokemon('Ekans'),
                'level': 15,
                'moves': get_moves(['Wrap', 'Poison Sting', 'Bite'])
            },
            {
                'species': get_pokemon('Zubat'),
                'level': 15,
                'moves': get_moves(['Leech Life', 'Supersonic', 'Bite'])
            }
        ],
        intro_text="Rejoins la Team Rocket!"
    )
    
    # ============================================================================
    # ROUTE 25
    # ============================================================================
    
    create_npc_trainer(
        username='Hiker Franklin',
        trainer_type='trainer',
        location='Route 25',
        team_data=[
            {
                'species': get_pokemon('Machop'),
                'level': 15,
                'moves': get_moves(['Low Kick', 'Leer'])
            },
            {
                'species': get_pokemon('Geodude'),
                'level': 15,
                'moves': get_moves(['Tackle', 'Defense Curl'])
            }
        ],
        intro_text="L'entraînement rend fort!"
    )
    
    create_npc_trainer(
        username='Youngster Dan',
        trainer_type='trainer',
        location='Route 25',
        team_data=[
            {
                'species': get_pokemon('Slowpoke'),
                'level': 17,
                'moves': get_moves(['Tackle', 'Growl'])
            }
        ],
        intro_text="Mon Slowpoke est spécial!"
    )
    
    # ============================================================================
    # S.S. ANNE
    # ============================================================================
    
    create_npc_trainer(
        username='Sailor Edmond',
        trainer_type='trainer',
        location='S.S. Anne',
        team_data=[
            {
                'species': get_pokemon('Machop'),
                'level': 18,
                'moves': get_moves(['Low Kick', 'Leer', 'Karate Chop'])
            },
            {
                'species': get_pokemon('Shellder'),
                'level': 18,
                'moves': get_moves(['Tackle', 'Withdraw'])
            }
        ],
        intro_text="Ahoy, marin d'eau douce!"
    )
    
    create_npc_trainer(
        username='Gentleman Thomas',
        trainer_type='trainer',
        location='S.S. Anne',
        team_data=[
            {
                'species': get_pokemon('Growlithe'),
                'level': 18,
                'moves': get_moves(['Bite', 'Roar', 'Ember'])
            },
            {
                'species': get_pokemon('Ponyta'),
                'level': 18,
                'moves': get_moves(['Tackle', 'Growl', 'Ember'])
            }
        ],
        intro_text="Un combat de gentlemen?"
    )
    
    create_npc_trainer(
        username='Lass Ann',
        trainer_type='trainer',
        location='S.S. Anne',
        team_data=[
            {
                'species': get_pokemon('Pidgey'),
                'level': 18,
                'moves': get_moves(['Gust', 'Sand Attack'])
            },
            {
                'species': get_pokemon('Nidoran♀'),
                'level': 18,
                'moves': get_moves(['Scratch', 'Poison Sting'])
            }
        ],
        intro_text="Cette croisière est géniale!"
    )
    
    # ============================================================================
    # ROUTE 6
    # ============================================================================
    
    create_npc_trainer(
        username='Bug Catcher Kent',
        trainer_type='trainer',
        location='Route 6',
        team_data=[
            {
                'species': get_pokemon('Weedle'),
                'level': 11,
                'moves': get_moves(['Poison Sting'])
            },
            {
                'species': get_pokemon('Kakuna'),
                'level': 11,
                'moves': get_moves(['Harden'])
            }
        ],
        intro_text="Les insectes règnent!"
    )
    
    create_npc_trainer(
        username='Camper Ricky',
        trainer_type='trainer',
        location='Route 6',
        team_data=[
            {
                'species': get_pokemon('Squirtle'),
                'level': 20,
                'moves': get_moves(['Tackle', 'Tail Whip', 'Bubble'])
            }
        ],
        intro_text="Le camping c'est la vie!"
    )
    
    # ============================================================================
    # ROUTE 11
    # ============================================================================
    
    create_npc_trainer(
        username='Gambler Hugo',
        trainer_type='trainer',
        location='Route 11',
        team_data=[
            {
                'species': get_pokemon('Poliwag'),
                'level': 18,
                'moves': get_moves(['Bubble', 'Hypnosis'])
            },
            {
                'species': get_pokemon('Horsea'),
                'level': 18,
                'moves': get_moves(['Bubble', 'Smokescreen'])
            }
        ],
        intro_text="Faisons un pari!"
    )
    
    create_npc_trainer(
        username='Engineer Baily',
        trainer_type='trainer',
        location='Route 11',
        team_data=[
            {
                'species': get_pokemon('Voltorb'),
                'level': 21,
                'moves': get_moves(['Tackle', 'Screech', 'Sonic Boom'])
            },
            {
                'species': get_pokemon('Magnemite'),
                'level': 21,
                'moves': get_moves(['Tackle', 'Sonic Boom', 'Thunder Shock'])
            }
        ],
        intro_text="L'électricité, c'est fantastique!"
    )
    
    # ============================================================================
    # ROCK TUNNEL
    # ============================================================================
    
    create_npc_trainer(
        username='Hiker Lenny',
        trainer_type='trainer',
        location='Rock Tunnel',
        team_data=[
            {
                'species': get_pokemon('Geodude'),
                'level': 19,
                'moves': get_moves(['Tackle', 'Defense Curl'])
            },
            {
                'species': get_pokemon('Machop'),
                'level': 19,
                'moves': get_moves(['Low Kick', 'Leer'])
            },
            {
                'species': get_pokemon('Geodude'),
                'level': 19,
                'moves': get_moves(['Tackle', 'Defense Curl'])
            }
        ],
        intro_text="Ces tunnels sont mon terrain!"
    )
    
    create_npc_trainer(
        username='Picnicker Dana',
        trainer_type='trainer',
        location='Rock Tunnel',
        team_data=[
            {
                'species': get_pokemon('Meowth'),
                'level': 19,
                'moves': get_moves(['Scratch', 'Growl', 'Bite'])
            },
            {
                'species': get_pokemon('Oddish'),
                'level': 19,
                'moves': get_moves(['Absorb', 'Poison Powder'])
            },
            {
                'species': get_pokemon('Pidgey'),
                'level': 19,
                'moves': get_moves(['Gust', 'Quick Attack'])
            }
        ],
        intro_text="Perdue dans le tunnel!"
    )
    
    create_npc_trainer(
        username='Pokemaniac Mark',
        trainer_type='trainer',
        location='Rock Tunnel',
        team_data=[
            {
                'species': get_pokemon('Rhyhorn'),
                'level': 29,
                'moves': get_moves(['Horn Attack', 'Stomp'])
            },
            {
                'species': get_pokemon('Lickitung'),
                'level': 29,
                'moves': get_moves(['Lick', 'Supersonic'])
            }
        ],
        intro_text="Les Pokémon rares sont ma passion!"
    )
    
    # ============================================================================
    # ROUTE 9
    # ============================================================================
    
    create_npc_trainer(
        username='Hiker Jeremy',
        trainer_type='trainer',
        location='Route 9',
        team_data=[
            {
                'species': get_pokemon('Machop'),
                'level': 20,
                'moves': get_moves(['Low Kick', 'Leer', 'Karate Chop'])
            },
            {
                'species': get_pokemon('Onix'),
                'level': 20,
                'moves': get_moves(['Tackle', 'Screech', 'Bind'])
            }
        ],
        intro_text="La montagne m'a rendu fort!"
    )
    
    create_npc_trainer(
        username='Bug Catcher Brent',
        trainer_type='trainer',
        location='Route 9',
        team_data=[
            {
                'species': get_pokemon('Beedrill'),
                'level': 19,
                'moves': get_moves(['Fury Attack', 'Twineedle'])
            },
            {
                'species': get_pokemon('Beedrill'),
                'level': 19,
                'moves': get_moves(['Fury Attack', 'Twineedle'])
            }
        ],
        intro_text="Mes Dardargnan sont redoutables!"
    )
    
    # ============================================================================
    # ROUTE 10
    # ============================================================================
    
    create_npc_trainer(
        username='Pokemaniac Steve',
        trainer_type='trainer',
        location='Route 10',
        team_data=[
            {
                'species': get_pokemon('Cubone'),
                'level': 22,
                'moves': get_moves(['Bone Club', 'Growl', 'Headbutt'])
            },
            {
                'species': get_pokemon('Slowpoke'),
                'level': 22,
                'moves': get_moves(['Tackle', 'Growl', 'Water Gun'])
            }
        ],
        intro_text="J'aime les Pokémon étranges!"
    )
    
    # ============================================================================
    # POKEMON TOWER (LAVENDER TOWN)
    # ============================================================================
    
    create_npc_trainer(
        username='Channeler Hope',
        trainer_type='trainer',
        location='Pokemon Tower',
        team_data=[
            {
                'species': get_pokemon('Gastly'),
                'level': 23,
                'moves': get_moves(['Lick', 'Spite', 'Confuse Ray'])
            }
        ],
        intro_text="Les esprits m'appellent..."
    )
    
    create_npc_trainer(
        username='Channeler Patricia',
        trainer_type='trainer',
        location='Pokemon Tower',
        team_data=[
            {
                'species': get_pokemon('Gastly'),
                'level': 22,
                'moves': get_moves(['Lick', 'Spite'])
            },
            {
                'species': get_pokemon('Haunter'),
                'level': 24,
                'moves': get_moves(['Lick', 'Spite', 'Hypnosis'])
            }
        ],
        intro_text="Je vois les âmes des Pokémon..."
    )
    
    # ============================================================================
    # CELADON GAME CORNER (TEAM ROCKET)
    # ============================================================================
    
    create_npc_trainer(
        username='Team Rocket Grunt',
        trainer_type='trainer',
        location='Rocket Game Corner',
        team_data=[
            {
                'species': get_pokemon('Raticate'),
                'level': 25,
                'moves': get_moves(['Hyper Fang', 'Quick Attack'])
            },
            {
                'species': get_pokemon('Zubat'),
                'level': 25,
                'moves': get_moves(['Bite', 'Leech Life', 'Supersonic'])
            }
        ],
        intro_text="Que fais-tu ici?!"
    )
    
    # ============================================================================
    # SILPH CO.
    # ============================================================================
    
    create_npc_trainer(
        username='Team Rocket Grunt',
        trainer_type='trainer',
        location='Silph Co.',
        team_data=[
            {
                'species': get_pokemon('Cubone'),
                'level': 29,
                'moves': get_moves(['Bone Club', 'Headbutt', 'Leer'])
            },
            {
                'species': get_pokemon('Drowzee'),
                'level': 29,
                'moves': get_moves(['Pound', 'Hypnosis', 'Confusion'])
            }
        ],
        intro_text="Silph sera à nous!"
    )
    
    create_npc_trainer(
        username='Scientist Jose',
        trainer_type='trainer',
        location='Silph Co.',
        team_data=[
            {
                'species': get_pokemon('Electrode'),
                'level': 29,
                'moves': get_moves(['Sonic Boom', 'Self-Destruct'])
            },
            {
                'species': get_pokemon('Weezing'),
                'level': 29,
                'moves': get_moves(['Tackle', 'Smog', 'Sludge'])
            }
        ],
        intro_text="La science au service de Silph!"
    )
    
    # ============================================================================
    # CYCLING ROAD
    # ============================================================================
    
    create_npc_trainer(
        username='Biker Jaren',
        trainer_type='trainer',
        location='Cycling Road',
        team_data=[
            {
                'species': get_pokemon('Grimer'),
                'level': 28,
                'moves': get_moves(['Pound', 'Poison Gas', 'Sludge'])
            },
            {
                'species': get_pokemon('Grimer'),
                'level': 28,
                'moves': get_moves(['Pound', 'Poison Gas', 'Sludge'])
            }
        ],
        intro_text="À fond la vitesse!"
    )
    
    create_npc_trainer(
        username='Cue Ball Corey',
        trainer_type='trainer',
        location='Cycling Road',
        team_data=[
            {
                'species': get_pokemon('Primeape'),
                'level': 29,
                'moves': get_moves(['Scratch', 'Leer', 'Karate Chop'])
            },
            {
                'species': get_pokemon('Machop'),
                'level': 29,
                'moves': get_moves(['Low Kick', 'Leer', 'Karate Chop'])
            }
        ],
        intro_text="Dégage de mon chemin!"
    )
    
    # ============================================================================
    # SAFARI ZONE
    # ============================================================================
    
    # Pas de dresseurs dans la Safari Zone
    
    # ============================================================================
    # SEAFOAM ISLANDS
    # ============================================================================
    
    create_npc_trainer(
        username='Swimmer Bryce',
        trainer_type='trainer',
        location='Seafoam Islands',
        team_data=[
            {
                'species': get_pokemon('Shellder'),
                'level': 38,
                'moves': get_moves(['Tackle', 'Withdraw', 'Ice Beam'])
            },
            {
                'species': get_pokemon('Cloyster'),
                'level': 38,
                'moves': get_moves(['Aurora Beam', 'Ice Beam'])
            }
        ],
        intro_text="L'eau glacée renforce!"
    )
    
    # ============================================================================
    # VICTORY ROAD
    # ============================================================================
    
    create_npc_trainer(
        username='Black Belt Atsushi',
        trainer_type='trainer',
        location='Victory Road',
        team_data=[
            {
                'species': get_pokemon('Machop'),
                'level': 40,
                'moves': get_moves(['Low Kick', 'Karate Chop', 'Submission'])
            },
            {
                'species': get_pokemon('Machoke'),
                'level': 40,
                'moves': get_moves(['Low Kick', 'Karate Chop', 'Submission'])
            }
        ],
        intro_text="Seuls les forts passent!"
    )
    
    create_npc_trainer(
        username='Cool Trainer Samuel',
        trainer_type='trainer',
        location='Victory Road',
        team_data=[
            {
                'species': get_pokemon('Sandslash'),
                'level': 37,
                'moves': get_moves(['Scratch', 'Slash', 'Sand Attack'])
            },
            {
                'species': get_pokemon('Sandslash'),
                'level': 37,
                'moves': get_moves(['Scratch', 'Slash', 'Sand Attack'])
            },
            {
                'species': get_pokemon('Rhyhorn'),
                'level': 38,
                'moves': get_moves(['Horn Attack', 'Stomp'])
            }
        ],
        intro_text="Je m'entraîne ici depuis des mois!"
    )
    
    create_npc_trainer(
        username='Juggler Nelson',
        trainer_type='trainer',
        location='Victory Road',
        team_data=[
            {
                'species': get_pokemon('Drowzee'),
                'level': 41,
                'moves': get_moves(['Pound', 'Hypnosis', 'Psychic'])
            },
            {
                'species': get_pokemon('Hypno'),
                'level': 41,
                'moves': get_moves(['Pound', 'Hypnosis', 'Psychic'])
            },
            {
                'species': get_pokemon('Kadabra'),
                'level': 41,
                'moves': get_moves(['Teleport', 'Kinesis', 'Psybeam'])
            }
        ],
        intro_text="La psychologie est tout!"
    )
    
    create_npc_trainer(
        username='Tamer Vincent',
        trainer_type='trainer',
        location='Victory Road',
        team_data=[
            {
                'species': get_pokemon('Persian'),
                'level': 44,
                'moves': get_moves(['Scratch', 'Growl', 'Bite', 'Slash'])
            },
            {
                'species': get_pokemon('Golduck'),
                'level': 44,
                'moves': get_moves(['Scratch', 'Confusion', 'Hydro Pump'])
            }
        ],
        intro_text="J'ai dompté les plus féroces!"
    )
    
    logging.info(f"[+] {Trainer.objects.filter(trainer_type='trainer').count()} Dresseurs NPCs créés")

def initialize_rival_battles(player_starter_choice='Bulbasaur'):
    """
    Initialise les différentes versions du Rival au cours de l'aventure
    
    Args:
        player_starter_choice: 'Bulbasaur', 'Charmander', ou 'Squirtle'
    """
    
    logging.info("[*] Initialisation des combats contre le Rival...")
    
    # Fonctions helper
    def get_pokemon(name):
        return Pokemon.objects.get(name=name)
    
    def get_moves(move_names):
        return [PokemonMove.objects.get(name=name) for name in move_names]
    
    # Déterminer le starter du rival
    rival_starter_map = {
        'Bulbasaur': 'Charmander',    # Si joueur a Bulbasaur, rival a Charmander
        'Charmander': 'Squirtle',      # Si joueur a Charmander, rival a Squirtle
        'Squirtle': 'Bulbasaur'        # Si joueur a Squirtle, rival a Bulbasaur
    }
    rival_starter = rival_starter_map.get(player_starter_choice, 'Squirtle')
    
    # Évolutions du starter du rival
    starter_evolutions = {
        'Charmander': ['Charmander', 'Charmeleon', 'Charizard'],
        'Squirtle': ['Squirtle', 'Wartortle', 'Blastoise'],
        'Bulbasaur': ['Bulbasaur', 'Ivysaur', 'Venusaur']
    }
    rival_line = starter_evolutions[rival_starter]
    
    # ============================================================================
    # COMBAT 1: PALLET TOWN (Niveau 5)
    # ============================================================================
    
    create_npc_trainer(
        username='Rival - Pallet Town',
        trainer_type='rival',
        location='Oak Laboratory',
        team_data=[
            {
                'species': get_pokemon(rival_line[0]),
                'level': 5,
                'moves': get_moves(['Scratch', 'Growl'] if rival_starter == 'Charmander' else 
                                 ['Tackle', 'Tail Whip'] if rival_starter == 'Squirtle' else
                                 ['Tackle', 'Growl'])
            }
        ],
        intro_text=f"Allez {rival_line[0]}! On va leur montrer!"
    )
    
    # ============================================================================
    # COMBAT 2: ROUTE 22 (Niveau 9)
    # ============================================================================
    
    pidgey_team = {
        'species': get_pokemon('Pidgey'),
        'level': 9,
        'moves': get_moves(['Tackle', 'Gust'])
    }
    
    create_npc_trainer(
        username='Rival - Route 22 (1)',
        trainer_type='rival',
        location='Route 22',
        team_data=[
            pidgey_team,
            {
                'species': get_pokemon(rival_line[0]),
                'level': 9,
                'moves': get_moves(['Scratch', 'Growl', 'Ember'] if rival_starter == 'Charmander' else 
                                 ['Tackle', 'Tail Whip', 'Bubble'] if rival_starter == 'Squirtle' else
                                 ['Tackle', 'Growl', 'Leech Seed'])
            }
        ],
        intro_text="Tu crois être fort? Voyons voir!"
    )
    
    # ============================================================================
    # COMBAT 3: CERULEAN CITY (Niveau 18)
    # ============================================================================
    
    create_npc_trainer(
        username='Rival - Cerulean City',
        trainer_type='rival',
        location='Route 24',
        team_data=[
            {
                'species': get_pokemon('Pidgeotto'),
                'level': 17,
                'moves': get_moves(['Tackle', 'Gust', 'Sand Attack'])
            },
            {
                'species': get_pokemon('Abra'),
                'level': 16,
                'moves': get_moves(['Teleport'])
            },
            {
                'species': get_pokemon('Rattata'),
                'level': 15,
                'moves': get_moves(['Tackle', 'Tail Whip', 'Quick Attack'])
            },
            {
                'species': get_pokemon(rival_line[1]),  # Évolution 1
                'level': 18,
                'moves': get_moves(['Scratch', 'Growl', 'Ember', 'Leer'] if rival_starter == 'Charmander' else 
                                 ['Tackle', 'Tail Whip', 'Bubble', 'Water Gun'] if rival_starter == 'Squirtle' else
                                 ['Tackle', 'Growl', 'Leech Seed', 'Vine Whip'])
            }
        ],
        intro_text="Je t'attendais! Prépare-toi!"
    )
    
    # ============================================================================
    # COMBAT 4: S.S. ANNE (Niveau 20)
    # ============================================================================
    
    create_npc_trainer(
        username='Rival - S.S. Anne',
        trainer_type='rival',
        location='S.S. Anne',
        team_data=[
            {
                'species': get_pokemon('Pidgeotto'),
                'level': 19,
                'moves': get_moves(['Gust', 'Sand Attack', 'Quick Attack'])
            },
            {
                'species': get_pokemon('Raticate'),
                'level': 16,
                'moves': get_moves(['Tackle', 'Tail Whip', 'Hyper Fang'])
            },
            {
                'species': get_pokemon('Kadabra'),
                'level': 18,
                'moves': get_moves(['Teleport', 'Kinesis', 'Confusion'])
            },
            {
                'species': get_pokemon(rival_line[1]),
                'level': 20,
                'moves': get_moves(['Scratch', 'Ember', 'Leer', 'Rage'] if rival_starter == 'Charmander' else 
                                 ['Tackle', 'Bubble', 'Water Gun', 'Bite'] if rival_starter == 'Squirtle' else
                                 ['Tackle', 'Leech Seed', 'Vine Whip', 'Poison Powder'])
            }
        ],
        intro_text="Toi ici?! On va régler ça maintenant!"
    )
    
    # ============================================================================
    # COMBAT 5: POKEMON TOWER (Niveau 25)
    # ============================================================================
    
    create_npc_trainer(
        username='Rival - Pokemon Tower',
        trainer_type='rival',
        location='Pokemon Tower',
        team_data=[
            {
                'species': get_pokemon('Pidgeotto'),
                'level': 25,
                'moves': get_moves(['Gust', 'Sand Attack', 'Quick Attack', 'Wing Attack'])
            },
            {
                'species': get_pokemon('Growlithe') if rival_starter != 'Charmander' else get_pokemon('Gyarados'),
                'level': 23,
                'moves': get_moves(['Bite', 'Roar', 'Ember'] if rival_starter != 'Charmander' else
                                 ['Bite', 'Dragon Rage', 'Leer'])
            },
            {
                'species': get_pokemon('Exeggcute') if rival_starter != 'Bulbasaur' else get_pokemon('Meowth'),
                'level': 22,
                'moves': get_moves(['Barrage', 'Hypnosis'] if rival_starter != 'Bulbasaur' else
                                 ['Scratch', 'Growl', 'Bite'])
            },
            {
                'species': get_pokemon('Kadabra'),
                'level': 20,
                'moves': get_moves(['Teleport', 'Kinesis', 'Confusion', 'Psybeam'])
            },
            {
                'species': get_pokemon(rival_line[1]),
                'level': 25,
                'moves': get_moves(['Ember', 'Leer', 'Rage', 'Slash'] if rival_starter == 'Charmander' else 
                                 ['Water Gun', 'Bite', 'Withdraw', 'Skull Bash'] if rival_starter == 'Squirtle' else
                                 ['Vine Whip', 'Poison Powder', 'Sleep Powder', 'Razor Leaf'])
            }
        ],
        intro_text="Qu'est-ce que tu fais ici? Ton Pokémon est-il mort?"
    )
    
    # ============================================================================
    # COMBAT 6: SILPH CO. (Niveau 37)
    # ============================================================================
    
    create_npc_trainer(
        username='Rival - Silph Co.',
        trainer_type='rival',
        location='Silph Co.',
        team_data=[
            {
                'species': get_pokemon('Pidgeot'),
                'level': 37,
                'moves': get_moves(['Wing Attack', 'Sand Attack', 'Quick Attack', 'Mirror Move'])
            },
            {
                'species': get_pokemon('Growlithe') if rival_starter == 'Bulbasaur' else 
                          get_pokemon('Exeggcute') if rival_starter == 'Squirtle' else
                          get_pokemon('Gyarados'),
                'level': 35,
                'moves': get_moves(['Bite', 'Roar', 'Ember', 'Take Down'] if rival_starter == 'Bulbasaur' else
                                 ['Barrage', 'Hypnosis', 'Reflect'] if rival_starter == 'Squirtle' else
                                 ['Bite', 'Dragon Rage', 'Leer', 'Hydro Pump'])
            },
            {
                'species': get_pokemon('Alakazam'),
                'level': 35,
                'moves': get_moves(['Teleport', 'Kinesis', 'Psybeam', 'Recover'])
            },
            {
                'species': get_pokemon('Exeggcute') if rival_starter == 'Charmander' else
                          get_pokemon('Gyarados') if rival_starter == 'Bulbasaur' else
                          get_pokemon('Growlithe'),
                'level': 35,
                'moves': get_moves(['Barrage', 'Hypnosis', 'Reflect'] if rival_starter == 'Charmander' else
                                 ['Bite', 'Dragon Rage', 'Leer', 'Hydro Pump'] if rival_starter == 'Bulbasaur' else
                                 ['Bite', 'Roar', 'Ember', 'Take Down'])
            },
            {
                'species': get_pokemon(rival_line[2]),  # Évolution finale
                'level': 40,
                'moves': get_moves(['Ember', 'Leer', 'Rage', 'Slash'] if rival_starter == 'Charmander' else 
                                 ['Water Gun', 'Bite', 'Withdraw', 'Hydro Pump'] if rival_starter == 'Squirtle' else
                                 ['Vine Whip', 'Poison Powder', 'Razor Leaf', 'Solar Beam'])
            }
        ],
        intro_text="Je vais te montrer qui est le meilleur!"
    )
    
    # ============================================================================
    # COMBAT 7: ROUTE 22 AVANT LA LIGUE (Niveau 47)
    # ============================================================================
    
    create_npc_trainer(
        username='Rival - Route 22 (2)',
        trainer_type='rival',
        location='Route 22',
        team_data=[
            {
                'species': get_pokemon('Pidgeot'),
                'level': 47,
                'moves': get_moves(['Wing Attack', 'Mirror Move', 'Sky Attack', 'Quick Attack'])
            },
            {
                'species': get_pokemon('Rhyhorn'),
                'level': 45,
                'moves': get_moves(['Horn Attack', 'Stomp', 'Tail Whip', 'Fury Attack'])
            },
            {
                'species': get_pokemon('Growlithe') if rival_starter == 'Bulbasaur' else 
                          get_pokemon('Exeggcute') if rival_starter == 'Squirtle' else
                          get_pokemon('Gyarados'),
                'level': 45,
                'moves': get_moves(['Bite', 'Roar', 'Flamethrower', 'Take Down'] if rival_starter == 'Bulbasaur' else
                                 ['Barrage', 'Hypnosis', 'Solar Beam', 'Reflect'] if rival_starter == 'Squirtle' else
                                 ['Bite', 'Dragon Rage', 'Leer', 'Hydro Pump'])
            },
            {
                'species': get_pokemon('Alakazam'),
                'level': 47,
                'moves': get_moves(['Psychic', 'Recover', 'Psybeam', 'Reflect'])
            },
            {
                'species': get_pokemon('Exeggutor') if rival_starter == 'Charmander' else
                          get_pokemon('Gyarados') if rival_starter == 'Bulbasaur' else
                          get_pokemon('Arcanine'),
                'level': 45,
                'moves': get_moves(['Barrage', 'Hypnosis', 'Solar Beam', 'Stomp'] if rival_starter == 'Charmander' else
                                 ['Bite', 'Dragon Rage', 'Leer', 'Hydro Pump'] if rival_starter == 'Bulbasaur' else
                                 ['Bite', 'Roar', 'Flamethrower', 'Take Down'])
            },
            {
                'species': get_pokemon(rival_line[2]),
                'level': 53,
                'moves': get_moves(['Flamethrower', 'Fire Spin', 'Slash', 'Fire Blast'] if rival_starter == 'Charmander' else 
                                 ['Hydro Pump', 'Bite', 'Ice Beam', 'Skull Bash'] if rival_starter == 'Squirtle' else
                                 ['Razor Leaf', 'Poison Powder', 'Solar Beam', 'Sleep Powder'])
            }
        ],
        intro_text="Tu n'iras pas plus loin! Je vais te prouver ma supériorité!"
    )
    
    # ============================================================================
    # COMBAT 8: CHAMPION (Niveau 61-65)
    # ============================================================================
    
    create_npc_trainer(
        username='Champion Blue',
        trainer_type='champion',
        location='Pokemon League',
        team_data=[
            {
                'species': get_pokemon('Pidgeot'),
                'level': 61,
                'moves': get_moves(['Wing Attack', 'Mirror Move', 'Sky Attack', 'Whirlwind'])
            },
            {
                'species': get_pokemon('Alakazam'),
                'level': 59,
                'moves': get_moves(['Psychic', 'Recover', 'Psybeam', 'Reflect'])
            },
            {
                'species': get_pokemon('Rhydon'),
                'level': 61,
                'moves': get_moves(['Horn Attack', 'Stomp', 'Earthquake', 'Horn Drill'])
            },
            {
                'species': get_pokemon('Arcanine') if rival_starter == 'Bulbasaur' else 
                          get_pokemon('Exeggutor') if rival_starter == 'Squirtle' else
                          get_pokemon('Gyarados'),
                'level': 61,
                'moves': get_moves(['Bite', 'Roar', 'Flamethrower', 'Take Down'] if rival_starter == 'Bulbasaur' else
                                 ['Barrage', 'Hypnosis', 'Solar Beam', 'Stomp'] if rival_starter == 'Squirtle' else
                                 ['Bite', 'Dragon Rage', 'Hydro Pump', 'Hyper Beam'])
            },
            {
                'species': get_pokemon('Exeggutor') if rival_starter == 'Charmander' else
                          get_pokemon('Gyarados') if rival_starter == 'Bulbasaur' else
                          get_pokemon('Arcanine'),
                'level': 61,
                'moves': get_moves(['Barrage', 'Hypnosis', 'Solar Beam', 'Stomp'] if rival_starter == 'Charmander' else
                                 ['Bite', 'Dragon Rage', 'Hydro Pump', 'Hyper Beam'] if rival_starter == 'Bulbasaur' else
                                 ['Bite', 'Roar', 'Flamethrower', 'Take Down'])
            },
            {
                'species': get_pokemon(rival_line[2]),
                'level': 65,
                'moves': get_moves(['Flamethrower', 'Fire Spin', 'Slash', 'Fire Blast'] if rival_starter == 'Charmander' else 
                                 ['Hydro Pump', 'Bite', 'Ice Beam', 'Blizzard'] if rival_starter == 'Squirtle' else
                                 ['Razor Leaf', 'Poison Powder', 'Solar Beam', 'Sleep Powder'])
            }
        ],
        intro_text="J'ai battu la Ligue et je t'attendais! Je suis devenu le Champion grâce au Prof. Chen! Voyons si tu es à la hauteur!"
    )
    
    rival_count = Trainer.objects.filter(trainer_type__in=['rival', 'champion']).count()
    logging.info(f"[+] {rival_count} versions du Rival créées (starter adverse: {rival_starter})")


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
        location='Pokemon League',
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
        location='Pokemon League',
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
        location='Pokemon League',
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
        location='Pokemon League',
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
        location='Pokemon League',
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
        initialize_npc_trainers()
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