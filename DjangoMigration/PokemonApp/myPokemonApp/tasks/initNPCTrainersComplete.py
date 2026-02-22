#!/usr/bin/python3
"""
Script d'initialisation complet des dresseurs NPC de Kanto.
Couvre TOUTES les zones de Kanto avec des équipes fidèles aux jeux originaux.
Basé sur FireRed/LeafGreen (Gen 3).

Remplace/complète la section initialize_npc_trainers() de initializeItemsAndNpcs.py.
À appeler depuis initAllDatabase.py ou le shell Django.
"""

from myPokemonApp.models import Pokemon, PokemonMove, Trainer
from myPokemonApp.gameUtils import create_npc_trainer
import logging

logging.basicConfig(level=logging.INFO)


def get_pokemon(name):
    return Pokemon.objects.get(name=name)


def get_moves(move_names):
    moves = []
    for name in move_names:
        try:
            moves.append(PokemonMove.objects.get(name=name))
        except PokemonMove.DoesNotExist:
            logging.warning(f"[!] Move introuvable: {name}")
    return moves


def init_route_2():
    """Route 2 - Entre Jadielle et la Forêt de Jade"""
    logging.info("[*] Route 2...")

    create_npc_trainer(
        username='Bug Catcher Colton',
        trainer_type='trainer',
        location='Route 2',
        team_data=[
            {'species': get_pokemon('Weedle'), 'level': 4, 'moves': get_moves(['Poison Sting', 'String Shot'])},
            {'species': get_pokemon('Caterpie'), 'level': 4, 'moves': get_moves(['Tackle', 'String Shot'])},
        ],
        intro_text="Les insectes de la route 2 sont redoutables!"
    )

    create_npc_trainer(
        username='Youngster Joey',
        trainer_type='trainer',
        location='Route 2',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 5, 'moves': get_moves(['Tackle', 'Tail Whip'])},
        ],
        intro_text="Mon Rattata est dans le top percentage!"
    )


def init_route_5():
    """Route 5 - Entre Azuria et le souterrain de Safrania"""
    logging.info("[*] Route 5...")

    create_npc_trainer(
        username='Lass Dawn',
        trainer_type='trainer',
        location='Route 5',
        team_data=[
            {'species': get_pokemon('Oddish'), 'level': 16, 'moves': get_moves(['Absorb', 'Poison Powder'])},
            {'species': get_pokemon('Pidgey'), 'level': 16, 'moves': get_moves(['Gust', 'Sand Attack'])},
        ],
        intro_text="Je me promène sur cette route tous les jours!"
    )

    create_npc_trainer(
        username='Youngster Allen',
        trainer_type='trainer',
        location='Route 5',
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 17, 'moves': get_moves(['Wrap', 'Poison Sting', 'Leer'])},
            {'species': get_pokemon('Mankey'), 'level': 17, 'moves': get_moves(['Scratch', 'Low Kick', 'Leer'])},
        ],
        intro_text="Prépare-toi à te battre!"
    )

    create_npc_trainer(
        username='Camper Todd',
        trainer_type='trainer',
        location='Route 5',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 15, 'moves': get_moves(['Tackle', 'Quick Attack'])},
            {'species': get_pokemon('Sandshrew'), 'level': 15, 'moves': get_moves(['Scratch', 'Defense Curl'])},
        ],
        intro_text="Je campe ici depuis des jours!"
    )

    create_npc_trainer(
        username='Lass Haley',
        trainer_type='trainer',
        location='Route 5',
        team_data=[
            {'species': get_pokemon('Jigglypuff'), 'level': 17, 'moves': get_moves(['Sing', 'Pound'])},
            {'species': get_pokemon('Meowth'), 'level': 17, 'moves': get_moves(['Scratch', 'Growl', 'Bite'])},
        ],
        intro_text="Mes Pokémon chantent magnifiquement!"
    )


def init_route_7():
    """Route 7 - Entre Safrania et Céladopole"""
    logging.info("[*] Route 7...")

    create_npc_trainer(
        username='Lass Paige',
        trainer_type='trainer',
        location='Route 7',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 23, 'moves': get_moves(['Hyper Fang', 'Quick Attack'])},
            {'species': get_pokemon('Oddish'), 'level': 23, 'moves': get_moves(['Absorb', 'Acid'])},
        ],
        intro_text="Cette route est à moi!"
    )

    create_npc_trainer(
        username='Youngster Robby',
        trainer_type='trainer',
        location='Route 7',
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 24, 'moves': get_moves(['Wrap', 'Bite', 'Poison Sting'])},
        ],
        intro_text="Mon Ekans va t'enrouler!"
    )

    create_npc_trainer(
        username='Pokemaniac Cooper',
        trainer_type='trainer',
        location='Route 7',
        team_data=[
            {'species': get_pokemon('Slowpoke'), 'level': 25, 'moves': get_moves(['Tackle', 'Water Gun', 'Confusion'])},
            {'species': get_pokemon('Lickitung'), 'level': 25, 'moves': get_moves(['Lick', 'Supersonic'])},
        ],
        intro_text="Les Pokémon étranges sont ma spécialité!"
    )


def init_route_8():
    """Route 8 - Entre Safrania et Lavanville"""
    logging.info("[*] Route 8...")

    create_npc_trainer(
        username='Gambler Giselle',
        trainer_type='trainer',
        location='Route 8',
        team_data=[
            {'species': get_pokemon('Poliwag'), 'level': 23, 'moves': get_moves(['Bubble', 'Hypnosis'])},
            {'species': get_pokemon('Poliwag'), 'level': 23, 'moves': get_moves(['Bubble', 'Hypnosis'])},
        ],
        intro_text="Je parie sur mes Pokémon!"
    )

    create_npc_trainer(
        username='Lass Crissy',
        trainer_type='trainer',
        location='Route 8',
        team_data=[
            {'species': get_pokemon('Cubone'), 'level': 24, 'moves': get_moves(['Bone Club', 'Headbutt'])},
            {'species': get_pokemon('Drowzee'), 'level': 24, 'moves': get_moves(['Pound', 'Hypnosis', 'Confusion'])},
        ],
        intro_text="Attention à mon équipe!"
    )

    create_npc_trainer(
        username='Pokemaniac Mark',
        trainer_type='trainer',
        location='Route 8',
        team_data=[
            {'species': get_pokemon('Cubone'), 'level': 25, 'moves': get_moves(['Bone Club', 'Headbutt', 'Leer'])},
            {'species': get_pokemon('Slowpoke'), 'level': 25, 'moves': get_moves(['Confusion', 'Water Gun'])},
        ],
        intro_text="J'adore les Pokémon rares!"
    )

    create_npc_trainer(
        username='Biker Danny',
        trainer_type='trainer',
        location='Route 8',
        team_data=[
            {'species': get_pokemon('Koffing'), 'level': 26, 'moves': get_moves(['Smog', 'Tackle', 'Poison Gas'])},
        ],
        intro_text="Sors de ma route!"
    )


def init_route_12():
    """Route 12 - Longue route côtière au sud de Lavanville"""
    logging.info("[*] Route 12...")

    create_npc_trainer(
        username='Fisherman Wade',
        trainer_type='trainer',
        location='Route 12',
        team_data=[
            {'species': get_pokemon('Poliwag'), 'level': 25, 'moves': get_moves(['Bubble', 'Hypnosis'])},
            {'species': get_pokemon('Poliwag'), 'level': 25, 'moves': get_moves(['Bubble', 'Hypnosis'])},
            {'species': get_pokemon('Poliwag'), 'level': 25, 'moves': get_moves(['Bubble', 'Hypnosis'])},
        ],
        intro_text="La pêche, c'est ma passion!"
    )

    create_npc_trainer(
        username='Fisherman Raymond',
        trainer_type='trainer',
        location='Route 12',
        team_data=[
            {'species': get_pokemon('Horsea'), 'level': 26, 'moves': get_moves(['Bubble', 'Smokescreen'])},
            {'species': get_pokemon('Goldeen'), 'level': 26, 'moves': get_moves(['Peck', 'Tail Whip', 'Water Gun'])},
        ],
        intro_text="Mes Pokémon aquatiques sont excellents!"
    )

    create_npc_trainer(
        username='Picnicker Blossom',
        trainer_type='trainer',
        location='Route 12',
        team_data=[
            {'species': get_pokemon('Oddish'), 'level': 25, 'moves': get_moves(['Absorb', 'Acid', 'Sleep Powder'])},
            {'species': get_pokemon('Bellsprout'), 'level': 25, 'moves': get_moves(['Vine Whip', 'Poison Powder'])},
        ],
        intro_text="Cette route est magnifique au printemps!"
    )

    create_npc_trainer(
        username='Youngster Timmy',
        trainer_type='trainer',
        location='Route 12',
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 27, 'moves': get_moves(['Wrap', 'Bite', 'Screech'])},
            {'species': get_pokemon('Spearow'), 'level': 27, 'moves': get_moves(['Peck', 'Growl', 'Fury Attack'])},
        ],
        intro_text="Je suis le roi de cette route!"
    )


def init_route_13():
    """Route 13 - Route venteuse"""
    logging.info("[*] Route 13...")

    create_npc_trainer(
        username='Birdkeeper Chester',
        trainer_type='trainer',
        location='Route 13',
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 28, 'moves': get_moves(['Gust', 'Sand Attack', 'Quick Attack'])},
            {'species': get_pokemon('Spearow'), 'level': 28, 'moves': get_moves(['Peck', 'Growl', 'Fury Attack'])},
        ],
        intro_text="Mes oiseaux dominent le ciel!"
    )

    create_npc_trainer(
        username='Birdkeeper Perry',
        trainer_type='trainer',
        location='Route 13',
        team_data=[
            {'species': get_pokemon('Pidgeotto'), 'level': 30, 'moves': get_moves(['Gust', 'Sand Attack', 'Quick Attack'])},
            {'species': get_pokemon('Fearow'), 'level': 30, 'moves': get_moves(['Peck', 'Fury Attack', 'Mirror Move'])},
        ],
        intro_text="Volons ensemble vers la victoire!"
    )

    create_npc_trainer(
        username='Picnicker Sofia',
        trainer_type='trainer',
        location='Route 13',
        team_data=[
            {'species': get_pokemon('Weepinbell'), 'level': 29, 'moves': get_moves(['Vine Whip', 'Poison Powder', 'Sleep Powder'])},
            {'species': get_pokemon('Gloom'), 'level': 29, 'moves': get_moves(['Absorb', 'Acid', 'Sleep Powder'])},
        ],
        intro_text="La nature est magnifique ici!"
    )

    create_npc_trainer(
        username='Fisherman Ned',
        trainer_type='trainer',
        location='Route 13',
        team_data=[
            {'species': get_pokemon('Shellder'), 'level': 28, 'moves': get_moves(['Tackle', 'Withdraw', 'Supersonic'])},
            {'species': get_pokemon('Krabby'), 'level': 28, 'moves': get_moves(['Tackle', 'Stomp'])},
        ],
        intro_text="Les crustacés sont mes alliés!"
    )


def init_route_14():
    """Route 14 - Route au sud menant vers Parmanie"""
    logging.info("[*] Route 14...")

    create_npc_trainer(
        username='Birdkeeper Donald',
        trainer_type='trainer',
        location='Route 14',
        team_data=[
            {'species': get_pokemon('Pidgeotto'), 'level': 32, 'moves': get_moves(['Gust', 'Quick Attack', 'Wing Attack'])},
            {'species': get_pokemon('Fearow'), 'level': 32, 'moves': get_moves(['Fury Attack', 'Mirror Move', 'Drill Peck'])},
        ],
        intro_text="Défi de hauteur!"
    )

    create_npc_trainer(
        username='Youngster Mikey',
        trainer_type='trainer',
        location='Route 14',
        team_data=[
            {'species': get_pokemon('Nidorino'), 'level': 31, 'moves': get_moves(['Horn Attack', 'Double Kick', 'Poison Sting'])},
        ],
        intro_text="Mon Nidorino va t'empoisonner!"
    )

    create_npc_trainer(
        username='Picnicker Becky',
        trainer_type='trainer',
        location='Route 14',
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 28, 'moves': get_moves(['Gust', 'Sand Attack'])},
            {'species': get_pokemon('Rattata'), 'level': 28, 'moves': get_moves(['Hyper Fang', 'Quick Attack'])},
            {'species': get_pokemon('Meowth'), 'level': 28, 'moves': get_moves(['Scratch', 'Growl', 'Bite'])},
        ],
        intro_text="Un pique-nique interrompu par un combat... parfait!"
    )


def init_route_15():
    """Route 15 - Relie Route 14 à Parmanie"""
    logging.info("[*] Route 15...")

    create_npc_trainer(
        username='Birdkeeper Hank',
        trainer_type='trainer',
        location='Route 15',
        team_data=[
            {'species': get_pokemon('Spearow'), 'level': 34, 'moves': get_moves(['Fury Attack', 'Mirror Move'])},
            {'species': get_pokemon('Fearow'), 'level': 34, 'moves': get_moves(['Fury Attack', 'Mirror Move', 'Drill Peck'])},
        ],
        intro_text="Traverser cette route sans se battre? Impossible!"
    )

    create_npc_trainer(
        username='Lass Vivian',
        trainer_type='trainer',
        location='Route 15',
        team_data=[
            {'species': get_pokemon('Nidorina'), 'level': 33, 'moves': get_moves(['Scratch', 'Poison Sting', 'Body Slam'])},
            {'species': get_pokemon('Oddish'), 'level': 33, 'moves': get_moves(['Absorb', 'Acid', 'Sleep Powder'])},
        ],
        intro_text="Ma Nidorina est féroce!"
    )

    create_npc_trainer(
        username='Biker Ernest',
        trainer_type='trainer',
        location='Route 15',
        team_data=[
            {'species': get_pokemon('Koffing'), 'level': 34, 'moves': get_moves(['Smog', 'Sludge', 'Smokescreen'])},
            {'species': get_pokemon('Koffing'), 'level': 34, 'moves': get_moves(['Smog', 'Sludge', 'Smokescreen'])},
        ],
        intro_text="Mes Smogo vont vous enfumer!"
    )


def init_route_16():
    """Route 16 - À l'ouest de Céladopole"""
    logging.info("[*] Route 16...")

    create_npc_trainer(
        username='Biker Hideo',
        trainer_type='trainer',
        location='Route 16',
        team_data=[
            {'species': get_pokemon('Koffing'), 'level': 30, 'moves': get_moves(['Smog', 'Tackle', 'Sludge'])},
            {'species': get_pokemon('Grimer'), 'level': 30, 'moves': get_moves(['Pound', 'Disable', 'Sludge'])},
        ],
        intro_text="On se bat ici!"
    )

    create_npc_trainer(
        username='Biker Lucius',
        trainer_type='trainer',
        location='Route 16',
        team_data=[
            {'species': get_pokemon('Grimer'), 'level': 31, 'moves': get_moves(['Pound', 'Poison Gas', 'Sludge'])},
            {'species': get_pokemon('Grimer'), 'level': 31, 'moves': get_moves(['Pound', 'Poison Gas', 'Sludge'])},
            {'species': get_pokemon('Grimer'), 'level': 31, 'moves': get_moves(['Pound', 'Poison Gas', 'Sludge'])},
        ],
        intro_text="Ma bande de Grotadmorv est invincible!"
    )


def init_route_17():
    """Route 17 - Route du Vélo"""
    logging.info("[*] Route 17 (Route du Vélo)...")

    create_npc_trainer(
        username='Biker Jared',
        trainer_type='trainer',
        location='Route 17',
        team_data=[
            {'species': get_pokemon('Doduo'), 'level': 33, 'moves': get_moves(['Peck', 'Growl', 'Fury Attack'])},
        ],
        intro_text="À fond les gaz sur la Route du Vélo!"
    )

    create_npc_trainer(
        username='Biker Russel',
        trainer_type='trainer',
        location='Route 17',
        team_data=[
            {'species': get_pokemon('Koffing'), 'level': 34, 'moves': get_moves(['Smog', 'Sludge', 'Self-Destruct'])},
            {'species': get_pokemon('Koffing'), 'level': 34, 'moves': get_moves(['Smog', 'Sludge', 'Self-Destruct'])},
        ],
        intro_text="Gare à mes Smogo!"
    )

    create_npc_trainer(
        username='Biker Alex',
        trainer_type='trainer',
        location='Route 17',
        team_data=[
            {'species': get_pokemon('Primeape'), 'level': 35, 'moves': get_moves(['Karate Chop', 'Screech', 'Fury Swipes'])},
        ],
        intro_text="Mon Mackogneur est inarrêtable!"
    )

    create_npc_trainer(
        username='Cue Ball Isaac',
        trainer_type='trainer',
        location='Route 17',
        team_data=[
            {'species': get_pokemon('Voltorb'), 'level': 34, 'moves': get_moves(['Tackle', 'Screech', 'Sonic Boom'])},
            {'species': get_pokemon('Electrode'), 'level': 36, 'moves': get_moves(['Tackle', 'Screech', 'Self-Destruct'])},
        ],
        intro_text="L'électricité me donne des ailes!"
    )

    create_npc_trainer(
        username='Cue Ball Jamar',
        trainer_type='trainer',
        location='Route 17',
        team_data=[
            {'species': get_pokemon('Grimer'), 'level': 36, 'moves': get_moves(['Pound', 'Disable', 'Sludge'])},
            {'species': get_pokemon('Koffing'), 'level': 36, 'moves': get_moves(['Smog', 'Poison Gas', 'Sludge'])},
        ],
        intro_text="Sur cette route, je suis le plus rapide!"
    )


def init_route_18():
    """Route 18 - Prolongement est de la Route du Vélo"""
    logging.info("[*] Route 18...")

    create_npc_trainer(
        username='Birdkeeper Jacob',
        trainer_type='trainer',
        location='Route 18',
        team_data=[
            {'species': get_pokemon('Spearow'), 'level': 36, 'moves': get_moves(['Fury Attack', 'Mirror Move'])},
            {'species': get_pokemon('Fearow'), 'level': 36, 'moves': get_moves(['Fury Attack', 'Mirror Move', 'Drill Peck'])},
            {'species': get_pokemon('Fearow'), 'level': 36, 'moves': get_moves(['Fury Attack', 'Mirror Move', 'Drill Peck'])},
        ],
        intro_text="Mes oiseaux sont les maîtres du ciel!"
    )

    create_npc_trainer(
        username='Cue Ball Nick',
        trainer_type='trainer',
        location='Route 18',
        team_data=[
            {'species': get_pokemon('Primeape'), 'level': 37, 'moves': get_moves(['Karate Chop', 'Cross Chop', 'Screech'])},
        ],
        intro_text="Personne ne passe sans se battre!"
    )


def init_route_19_20():
    """Routes 19 et 20 - Routes maritimes"""
    logging.info("[*] Routes 19 et 20...")

    create_npc_trainer(
        username='Swimmer Barry',
        trainer_type='trainer',
        location='Route 19',
        team_data=[
            {'species': get_pokemon('Tentacool'), 'level': 30, 'moves': get_moves(['Acid', 'Constrict', 'Supersonic'])},
            {'species': get_pokemon('Tentacool'), 'level': 30, 'moves': get_moves(['Acid', 'Constrict', 'Supersonic'])},
        ],
        intro_text="La mer est mon terrain de jeu!"
    )

    create_npc_trainer(
        username='Swimmer Diana',
        trainer_type='trainer',
        location='Route 19',
        team_data=[
            {'species': get_pokemon('Staryu'), 'level': 30, 'moves': get_moves(['Tackle', 'Water Gun', 'Rapid Spin'])},
            {'species': get_pokemon('Shellder'), 'level': 30, 'moves': get_moves(['Tackle', 'Withdraw', 'Supersonic'])},
        ],
        intro_text="L'eau me rend plus forte!"
    )

    create_npc_trainer(
        username='Swimmer Matthew',
        trainer_type='trainer',
        location='Route 20',
        team_data=[
            {'species': get_pokemon('Poliwhirl'), 'level': 32, 'moves': get_moves(['Bubble', 'Hypnosis', 'Body Slam'])},
            {'species': get_pokemon('Horsea'), 'level': 32, 'moves': get_moves(['Bubble', 'Smokescreen', 'Water Gun'])},
        ],
        intro_text="Je nage plus vite que tu ne cours!"
    )

    create_npc_trainer(
        username='Swimmer Beth',
        trainer_type='trainer',
        location='Route 20',
        team_data=[
            {'species': get_pokemon('Dewgong'), 'level': 34, 'moves': get_moves(['Headbutt', 'Aurora Beam', 'Ice Beam'])},
        ],
        intro_text="Les eaux glacées ne me font pas peur!"
    )

    create_npc_trainer(
        username='Juggler Kurt',
        trainer_type='trainer',
        location='Route 20',
        team_data=[
            {'species': get_pokemon('Gengar'), 'level': 35, 'moves': get_moves(['Lick', 'Night Shade', 'Hypnosis', 'Confuse Ray'])},
        ],
        intro_text="Mon Ectoplasma surgit des flots!"
    )


def init_route_21():
    """Route 21 - Route maritime entre Cramois'Île et Bourg Palette"""
    logging.info("[*] Route 21...")

    create_npc_trainer(
        username='Swimmer Charlie',
        trainer_type='trainer',
        location='Route 21',
        team_data=[
            {'species': get_pokemon('Tentacool'), 'level': 38, 'moves': get_moves(['Acid', 'Constrict', 'Wrap'])},
            {'species': get_pokemon('Tentacruel'), 'level': 38, 'moves': get_moves(['Acid', 'Hydro Pump', 'Barrier'])},
        ],
        intro_text="Nage jusqu'à Bourg Palette si tu peux!"
    )

    create_npc_trainer(
        username='Swimmer Linda',
        trainer_type='trainer',
        location='Route 21',
        team_data=[
            {'species': get_pokemon('Staryu'), 'level': 37, 'moves': get_moves(['Water Gun', 'Rapid Spin', 'Swift'])},
            {'species': get_pokemon('Starmie'), 'level': 37, 'moves': get_moves(['Water Gun', 'Psychic', 'Ice Beam'])},
        ],
        intro_text="Mes Staross brillent dans les vagues!"
    )

    create_npc_trainer(
        username='Fisherman Scott',
        trainer_type='trainer',
        location='Route 21',
        team_data=[
            {'species': get_pokemon('Magikarp'), 'level': 15, 'moves': get_moves(['Splash'])},
            {'species': get_pokemon('Magikarp'), 'level': 15, 'moves': get_moves(['Splash'])},
            {'species': get_pokemon('Gyarados'), 'level': 38, 'moves': get_moves(['Bite', 'Dragon Rage', 'Hydro Pump'])},
        ],
        intro_text="Ne te moque pas de mes Magicarpe... l'un d'eux a évolué!"
    )


def init_route_22():
    """Route 22 - Entre Jadielle et les Gardes de la Ligue"""
    logging.info("[*] Route 22...")

    create_npc_trainer(
        username='Youngster Wayne',
        trainer_type='trainer',
        location='Route 22',
        team_data=[
            {'species': get_pokemon('Nidoran♂'), 'level': 5, 'moves': get_moves(['Leer', 'Tackle'])},
            {'species': get_pokemon('Nidoran♀'), 'level': 5, 'moves': get_moves(['Scratch', 'Tail Whip'])},
        ],
        intro_text="Tu veux te battre avant la Ligue?"
    )


def init_route_23():
    """Route 23 - Chemin vers le Plateau Indigo"""
    logging.info("[*] Route 23...")

    create_npc_trainer(
        username='Swimmer Taylor',
        trainer_type='trainer',
        location='Route 23',
        team_data=[
            {'species': get_pokemon('Wartortle'), 'level': 44, 'moves': get_moves(['Bite', 'Water Gun', 'Withdraw'])},
            {'species': get_pokemon('Tentacruel'), 'level': 44, 'moves': get_moves(['Acid', 'Hydro Pump', 'Barrier'])},
        ],
        intro_text="Cette route est la dernière épreuve aquatique!"
    )

    create_npc_trainer(
        username='Swimmer Marina',
        trainer_type='trainer',
        location='Route 23',
        team_data=[
            {'species': get_pokemon('Golduck'), 'level': 45, 'moves': get_moves(['Confusion', 'Disable', 'Hydro Pump'])},
            {'species': get_pokemon('Seadra'), 'level': 45, 'moves': get_moves(['Water Gun', 'Smokescreen', 'Agility'])},
        ],
        intro_text="Mes Pokémon aquatiques sont au sommet!"
    )


def init_power_plant():
    """Centrale électrique / Power Plant"""
    logging.info("[*] Centrale électrique...")

    create_npc_trainer(
        username='Raichu Guard',
        trainer_type='trainer',
        location='Centrale',
        team_data=[
            {'species': get_pokemon('Raichu'), 'level': 35, 'moves': get_moves(['Thunder Shock', 'Thunder Wave', 'Thunder'])},
        ],
        intro_text="Cette centrale est sous haute tension!"
    )

    # En réalité la Power Plant n'a pas de dresseurs (que des Pokémon sauvages)
    # mais on peut y ajouter quelques Team Rocket
    create_npc_trainer(
        username='Team Rocket Grunt',
        trainer_type='trainer',
        location='Centrale',
        team_data=[
            {'species': get_pokemon('Electrode'), 'level': 33, 'moves': get_moves(['Tackle', 'Self-Destruct', 'Screech'])},
            {'species': get_pokemon('Magneton'), 'level': 33, 'moves': get_moves(['Thunder Shock', 'Sonic Boom', 'Thunder Wave'])},
        ],
        intro_text="Cette centrale va alimenter nos plans!"
    )


def init_fuchsia_safari_zone():
    """Zone Safari - Quelques gardes en entrée"""
    logging.info("[*] Zone Safari (gardes)...")

    create_npc_trainer(
        username='Safari Zone Warden',
        trainer_type='trainer',
        location='Zone Safari',
        team_data=[
            {'species': get_pokemon('Kangaskhan'), 'level': 40, 'moves': get_moves(['Headbutt', 'Dizzy Punch', 'Tail Whip'])},
            {'species': get_pokemon('Tauros'), 'level': 40, 'moves': get_moves(['Horn Attack', 'Tackle', 'Tail Whip'])},
        ],
        intro_text="Bienvenue dans ma Zone Safari!"
    )


def init_lavender_town():
    """Tour Pokémon - Lavanville (ajouts)"""
    logging.info("[*] Tour Pokémon (ajouts)...")

    create_npc_trainer(
        username='Channeler Margaret',
        trainer_type='trainer',
        location='Tour Pokémon',
        team_data=[
            {'species': get_pokemon('Gastly'), 'level': 22, 'moves': get_moves(['Lick', 'Spite'])},
        ],
        intro_text="Les défunts parlent à travers moi..."
    )

    create_npc_trainer(
        username='Channeler Tammy',
        trainer_type='trainer',
        location='Tour Pokémon',
        team_data=[
            {'species': get_pokemon('Gastly'), 'level': 23, 'moves': get_moves(['Lick', 'Spite', 'Confuse Ray'])},
            {'species': get_pokemon('Haunter'), 'level': 25, 'moves': get_moves(['Lick', 'Hypnosis', 'Night Shade'])},
        ],
        intro_text="Je vois l'au-delà..."
    )

    create_npc_trainer(
        username='Channeler Karina',
        trainer_type='trainer',
        location='Tour Pokémon',
        team_data=[
            {'species': get_pokemon('Haunter'), 'level': 24, 'moves': get_moves(['Lick', 'Night Shade', 'Hypnosis'])},
        ],
        intro_text="Les esprits m'ont accordé leur pouvoir!"
    )

    create_npc_trainer(
        username='Team Rocket Jesse',
        trainer_type='trainer',
        location='Tour Pokémon',
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 23, 'moves': get_moves(['Wrap', 'Bite', 'Poison Sting'])},
            {'species': get_pokemon('Drowzee'), 'level': 23, 'moves': get_moves(['Pound', 'Hypnosis', 'Confusion'])},
        ],
        intro_text="Nous sommes de la Team Rocket! La Tour nous appartient!"
    )

    create_npc_trainer(
        username='Team Rocket James',
        trainer_type='trainer',
        location='Tour Pokémon',
        team_data=[
            {'species': get_pokemon('Koffing'), 'level': 23, 'moves': get_moves(['Tackle', 'Smog', 'Poison Gas'])},
            {'species': get_pokemon('Zubat'), 'level': 23, 'moves': get_moves(['Leech Life', 'Bite', 'Supersonic'])},
        ],
        intro_text="Prepare for trouble... et maintenant du combat!"
    )


def init_celadon_city():
    """Céladopole - Bâtiment Team Rocket supplémentaires"""
    logging.info("[*] Céladopole...")

    create_npc_trainer(
        username='Team Rocket Grunt',
        trainer_type='trainer',
        location='Céladopole',
        team_data=[
            {'species': get_pokemon('Grimer'), 'level': 26, 'moves': get_moves(['Pound', 'Disable', 'Sludge'])},
            {'species': get_pokemon('Koffing'), 'level': 26, 'moves': get_moves(['Smog', 'Tackle', 'Poison Gas'])},
        ],
        intro_text="Tu fouines dans nos affaires?!"
    )

    create_npc_trainer(
        username='Team Rocket Executive Archer',
        trainer_type='trainer',
        location='Céladopole',
        team_data=[
            {'species': get_pokemon('Arbok'), 'level': 28, 'moves': get_moves(['Wrap', 'Bite', 'Screech'])},
            {'species': get_pokemon('Weezing'), 'level': 28, 'moves': get_moves(['Smog', 'Tackle', 'Sludge'])},
            {'species': get_pokemon('Hypno'), 'level': 28, 'moves': get_moves(['Pound', 'Hypnosis', 'Confusion', 'Disable'])},
        ],
        intro_text="Tu ne peux pas arrêter la Team Rocket!"
    )


def init_saffron_city():
    """Safrania - Silph Co. étendu"""
    logging.info("[*] Safrania (Silph Co. étendu)...")

    create_npc_trainer(
        username='Team Rocket Grunt',
        trainer_type='trainer',
        location='Safrania',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 27, 'moves': get_moves(['Hyper Fang', 'Quick Attack'])},
            {'species': get_pokemon('Zubat'), 'level': 27, 'moves': get_moves(['Bite', 'Leech Life', 'Supersonic'])},
        ],
        intro_text="La Sylphe Co. va alimenter notre empire!"
    )

    create_npc_trainer(
        username='Scientist Franklin',
        trainer_type='trainer',
        location='Safrania',
        team_data=[
            {'species': get_pokemon('Magnemite'), 'level': 29, 'moves': get_moves(['Thunder Shock', 'Sonic Boom', 'Thunder Wave'])},
            {'species': get_pokemon('Electrode'), 'level': 29, 'moves': get_moves(['Tackle', 'Screech', 'Self-Destruct'])},
        ],
        intro_text="La science au service du mal... pourquoi pas?"
    )

    create_npc_trainer(
        username='Team Rocket Giovanni Shadow',
        trainer_type='trainer',
        location='Safrania',
        team_data=[
            {'species': get_pokemon('Nidorino'), 'level': 35, 'moves': get_moves(['Horn Attack', 'Double Kick', 'Poison Sting'])},
            {'species': get_pokemon('Kangaskhan'), 'level': 35, 'moves': get_moves(['Headbutt', 'Dizzy Punch', 'Tail Whip'])},
            {'species': get_pokemon('Rhyhorn'), 'level': 37, 'moves': get_moves(['Horn Attack', 'Stomp', 'Tail Whip'])},
        ],
        intro_text="Giovanni - intermédiaire: Silph Co. sera à moi... enfin à la Team Rocket!"
    )


def init_victory_road_extra():
    """Chemin de la Victoire - Dresseurs supplémentaires"""
    logging.info("[*] Chemin de la Victoire (ajouts)...")

    create_npc_trainer(
        username='Cool Trainer Caroline',
        trainer_type='trainer',
        location='Chemin de la Victoire',
        team_data=[
            {'species': get_pokemon('Haunter'), 'level': 43, 'moves': get_moves(['Night Shade', 'Hypnosis', 'Confuse Ray'])},
            {'species': get_pokemon('Kadabra'), 'level': 43, 'moves': get_moves(['Psybeam', 'Recover', 'Psychic'])},
        ],
        intro_text="Seuls les meilleurs atteignent le Plateau Indigo!"
    )

    create_npc_trainer(
        username='Pokemaniac Bernard',
        trainer_type='trainer',
        location='Chemin de la Victoire',
        team_data=[
            {'species': get_pokemon('Slowbro'), 'level': 44, 'moves': get_moves(['Confusion', 'Psychic', 'Amnesia'])},
            {'species': get_pokemon('Kangaskhan'), 'level': 44, 'moves': get_moves(['Headbutt', 'Dizzy Punch', 'Body Slam'])},
        ],
        intro_text="J'accumule les Pokémon rares depuis des années!"
    )

    create_npc_trainer(
        username='Black Belt Takashi',
        trainer_type='trainer',
        location='Chemin de la Victoire',
        team_data=[
            {'species': get_pokemon('Primeape'), 'level': 43, 'moves': get_moves(['Karate Chop', 'Cross Chop', 'Fury Swipes'])},
            {'species': get_pokemon('Machamp'), 'level': 45, 'moves': get_moves(['Karate Chop', 'Cross Chop', 'Submission'])},
        ],
        intro_text="Le combat forge l'âme!"
    )


def init_mt_moon_extra():
    """Mont Sélénite - Dresseurs supplémentaires"""
    logging.info("[*] Mont Sélénite (ajouts)...")

    create_npc_trainer(
        username='Hiker Eric',
        trainer_type='trainer',
        location='Mont Sélénite',
        team_data=[
            {'species': get_pokemon('Geodude'), 'level': 11, 'moves': get_moves(['Tackle', 'Defense Curl'])},
            {'species': get_pokemon('Graveler'), 'level': 11, 'moves': get_moves(['Tackle', 'Defense Curl', 'Rock Throw'])},
        ],
        intro_text="La montagne teste ta force!"
    )

    create_npc_trainer(
        username='Team Rocket Cassidy',
        trainer_type='trainer',
        location='Mont Sélénite',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 12, 'moves': get_moves(['Tackle', 'Hyper Fang'])},
            {'species': get_pokemon('Ekans'), 'level': 12, 'moves': get_moves(['Wrap', 'Leer', 'Bite'])},
        ],
        intro_text="Les fossiles rares appartiennent à la Team Rocket!"
    )

    create_npc_trainer(
        username='Super Nerd Clifford',
        trainer_type='trainer',
        location='Mont Sélénite',
        team_data=[
            {'species': get_pokemon('Clefairy'), 'level': 13, 'moves': get_moves(['Pound', 'Growl', 'Sing'])},
            {'species': get_pokemon('Clefairy'), 'level': 13, 'moves': get_moves(['Pound', 'Growl', 'Sing'])},
        ],
        intro_text="Les Mélofée du Mont Lune m'ont choisi!"
    )

    create_npc_trainer(
        username='Team Rocket Butch',
        trainer_type='trainer',
        location='Mont Sélénite',
        team_data=[
            {'species': get_pokemon('Zubat'), 'level': 13, 'moves': get_moves(['Leech Life', 'Supersonic', 'Bite'])},
            {'species': get_pokemon('Sandshrew'), 'level': 13, 'moves': get_moves(['Scratch', 'Defense Curl', 'Sand Attack'])},
        ],
        intro_text="Rendez-nous ces fossiles!"
    )


def init_rock_tunnel_extra():
    """Tunnel Roche - Dresseurs supplémentaires"""
    logging.info("[*] Tunnel Roche (ajouts)...")

    create_npc_trainer(
        username='Hiker Allen',
        trainer_type='trainer',
        location='Tunnel Roche',
        team_data=[
            {'species': get_pokemon('Geodude'), 'level': 20, 'moves': get_moves(['Defense Curl', 'Rock Throw', 'Magnitude'])},
            {'species': get_pokemon('Machop'), 'level': 20, 'moves': get_moves(['Low Kick', 'Karate Chop', 'Leer'])},
        ],
        intro_text="Dans l'obscurité, mes Pokémon sont à leur avantage!"
    )

    create_npc_trainer(
        username='Picnicker Leah',
        trainer_type='trainer',
        location='Tunnel Roche',
        team_data=[
            {'species': get_pokemon('Clefairy'), 'level': 20, 'moves': get_moves(['Pound', 'Sing', 'Defense Curl'])},
        ],
        intro_text="Je me suis perdue... et j'ai envie de me battre!"
    )

    create_npc_trainer(
        username='Hiker Lucas',
        trainer_type='trainer',
        location='Tunnel Roche',
        team_data=[
            {'species': get_pokemon('Onix'), 'level': 22, 'moves': get_moves(['Tackle', 'Screech', 'Bind', 'Rock Throw'])},
            {'species': get_pokemon('Graveler'), 'level': 22, 'moves': get_moves(['Defense Curl', 'Rock Throw', 'Earthquake'])},
        ],
        intro_text="Le Tunnel Roche est mon habitat naturel!"
    )


def init_ss_anne_extra():
    """S.S. Anne - Dresseurs supplémentaires"""
    logging.info("[*] S.S. Anne (ajouts)...")

    create_npc_trainer(
        username='Sailor Eddy',
        trainer_type='trainer',
        location='Carmin sur Mer',
        team_data=[
            {'species': get_pokemon('Tentacool'), 'level': 19, 'moves': get_moves(['Acid', 'Constrict'])},
            {'species': get_pokemon('Machop'), 'level': 19, 'moves': get_moves(['Low Kick', 'Karate Chop', 'Leer'])},
        ],
        intro_text="Les marins sont les meilleurs combattants!"
    )

    create_npc_trainer(
        username='Gentleman Brooks',
        trainer_type='trainer',
        location='Carmin sur Mer',
        team_data=[
            {'species': get_pokemon('Nidoran♂'), 'level': 18, 'moves': get_moves(['Leer', 'Tackle', 'Poison Sting'])},
            {'species': get_pokemon('Nidoran♀'), 'level': 18, 'moves': get_moves(['Scratch', 'Tail Whip', 'Poison Sting'])},
        ],
        intro_text="Les gentlemen partagent leur savoir en duel!"
    )

    create_npc_trainer(
        username='Super Nerd Felix',
        trainer_type='trainer',
        location='Carmin sur Mer',
        team_data=[
            {'species': get_pokemon('Magnemite'), 'level': 20, 'moves': get_moves(['Thunder Shock', 'Sonic Boom'])},
            {'species': get_pokemon('Magnemite'), 'level': 20, 'moves': get_moves(['Thunder Shock', 'Sonic Boom'])},
            {'species': get_pokemon('Magnemite'), 'level': 20, 'moves': get_moves(['Thunder Shock', 'Sonic Boom'])},
        ],
        intro_text="Mes Magnéti sont chargés à fond!"
    )


def init_seafoam_extra():
    """Îles Écume - Dresseurs supplémentaires"""
    logging.info("[*] Îles Écume (ajouts)...")

    create_npc_trainer(
        username='Swimmer Anya',
        trainer_type='trainer',
        location='Îles Écume',
        team_data=[
            {'species': get_pokemon('Dewgong'), 'level': 39, 'moves': get_moves(['Headbutt', 'Aurora Beam', 'Ice Beam'])},
            {'species': get_pokemon('Cloyster'), 'level': 39, 'moves': get_moves(['Aurora Beam', 'Ice Beam', 'Spikes'])},
        ],
        intro_text="Les eaux glacées des Îles Écume me galvanisent!"
    )

    create_npc_trainer(
        username='Juggler Nate',
        trainer_type='trainer',
        location='Îles Écume',
        team_data=[
            {'species': get_pokemon('Jynx'), 'level': 40, 'moves': get_moves(['Pound', 'Lovely Kiss', 'Ice Beam', 'Psychic'])},
        ],
        intro_text="La glace et le mystère... c'est mon style!"
    )


# ==============================================================================
# ZONES MANQUANTES — Forêt de Jade, Routes 1/3/4/6/9/10/11/24/25
# Ces zones existent dans initializeItemsAndNpcs.py mais avec des noms
# anglais incorrects. Ici on ajoute des trainers supplémentaires avec
# les vrais noms de zones (français).
# ==============================================================================

def init_foret_de_jade():
    """Forêt de Jade — dresseurs insectes supplémentaires"""
    logging.info("[*] Forêt de Jade — trainers")
    create_npc_trainer(
        username='Lasseur Sacha',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Caterpie'), 'level': 6, 'moves': get_moves(['Tackle', 'String Shot'])},
            {'species': get_pokemon('Weedle'),   'level': 6, 'moves': get_moves(['Poison Sting', 'String Shot'])},
        ],
        intro_text="Tu veux traverser ma forêt ? Il faut d'abord me battre !"
    )
    create_npc_trainer(
        username='Lasseur Éric',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Metapod'),  'level': 7, 'moves': get_moves(['Harden'])},
            {'species': get_pokemon('Caterpie'), 'level': 7, 'moves': get_moves(['Tackle', 'String Shot'])},
        ],
        intro_text="Mon Chrysacier va vous bloquer la route !"
    )
    create_npc_trainer(
        username='Lasseur Damien',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Weedle'),  'level': 7, 'moves': get_moves(['Poison Sting', 'String Shot'])},
            {'species': get_pokemon('Kakuna'),  'level': 7, 'moves': get_moves(['Harden'])},
            {'species': get_pokemon('Weedle'),  'level': 7, 'moves': get_moves(['Poison Sting', 'String Shot'])},
        ],
        intro_text="Les chenilles de la forêt m'obéissent !"
    )


def init_route_1_extra():
    """Route 1 — dresseurs supplémentaires (nom FR correct)"""
    logging.info("[*] Route 1 extra — trainers")
    create_npc_trainer(
        username='Gamin Luc',
        trainer_type='trainer',
        location='Route 1',
        team_data=[
            {'species': get_pokemon('Pidgey'),  'level': 3, 'moves': get_moves(['Tackle', 'Sand Attack'])},
        ],
        intro_text="Hé toi ! Viens te battre avec moi !"
    )
    create_npc_trainer(
        username='Gamine Lucie',
        trainer_type='trainer',
        location='Route 1',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 4, 'moves': get_moves(['Tackle', 'Tail Whip'])},
        ],
        intro_text="Mon Rattata est adorable ET puissant !"
    )


def init_route_3_extra():
    """Route 3 — trainers additionnels (nom FR)"""
    logging.info("[*] Route 3 extra — trainers")
    create_npc_trainer(
        username='Gamin Martin',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {'species': get_pokemon('Pidgey'),   'level': 10, 'moves': get_moves(['Gust', 'Sand Attack'])},
            {'species': get_pokemon('Rattata'),  'level': 10, 'moves': get_moves(['Tackle', 'Quick Attack'])},
        ],
        intro_text="J'aime les Pokémon communs mais je me bats bien !"
    )
    create_npc_trainer(
        username='Infirmière Joy',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {'species': get_pokemon('Jigglypuff'), 'level': 11, 'moves': get_moves(['Pound', 'Sing'])},
        ],
        intro_text="Mes soins Pokémon sont les meilleurs !"
    )


def init_route_4_extra():
    """Route 4 — trainers additionnels (nom FR)"""
    logging.info("[*] Route 4 extra — trainers")
    create_npc_trainer(
        username='Gamine Sandra',
        trainer_type='trainer',
        location='Route 4',
        team_data=[
            {'species': get_pokemon('Nidoran♀'), 'level': 13, 'moves': get_moves(['Scratch', 'Tail Whip', 'Bite'])},
        ],
        intro_text="Je chasse les mauvais dresseurs de cette route !"
    )
    create_npc_trainer(
        username='Rocker Jim',
        trainer_type='trainer',
        location='Route 4',
        team_data=[
            {'species': get_pokemon('Geodude'), 'level': 12, 'moves': get_moves(['Tackle', 'Defense Curl'])},
            {'species': get_pokemon('Geodude'), 'level': 12, 'moves': get_moves(['Tackle', 'Defense Curl'])},
        ],
        intro_text="Rock n' roll Pokémon forever !"
    )


def init_route_6_extra():
    """Route 6 — trainers additionnels (nom FR)"""
    logging.info("[*] Route 6 extra — trainers")
    create_npc_trainer(
        username='Gamin Cyril',
        trainer_type='trainer',
        location='Route 6',
        team_data=[
            {'species': get_pokemon('Ekans'),  'level': 15, 'moves': get_moves(['Wrap', 'Leer', 'Poison Sting'])},
        ],
        intro_text="Je veux devenir le meilleur dresseur de Carmin !"
    )
    create_npc_trainer(
        username='Gamine Petra',
        trainer_type='trainer',
        location='Route 6',
        team_data=[
            {'species': get_pokemon('Oddish'), 'level': 14, 'moves': get_moves(['Absorb', 'Growl', 'Acid'])},
            {'species': get_pokemon('Bellsprout'), 'level': 14, 'moves': get_moves(['Vine Whip', 'Growth'])},
        ],
        intro_text="Les Pokémon Plante sont les plus beaux !"
    )


def init_route_9_extra():
    """Route 9 — trainers additionnels (nom FR)"""
    logging.info("[*] Route 9 extra — trainers")
    create_npc_trainer(
        username='Gamin Tom',
        trainer_type='trainer',
        location='Route 9',
        team_data=[
            {'species': get_pokemon('Ekans'),     'level': 20, 'moves': get_moves(['Bite', 'Glare', 'Poison Sting'])},
            {'species': get_pokemon('Spearow'),   'level': 20, 'moves': get_moves(['Peck', 'Leer', 'Fury Attack'])},
        ],
        intro_text="Cette route est dangereuse. Comme moi !"
    )


def init_route_10_extra():
    """Route 10 — trainers additionnels (nom FR)"""
    logging.info("[*] Route 10 extra — trainers")
    create_npc_trainer(
        username='Rocker Max',
        trainer_type='trainer',
        location='Route 10',
        team_data=[
            {'species': get_pokemon('Voltorb'),  'level': 21, 'moves': get_moves(['Screech', 'Spark', 'Tackle'])},
            {'species': get_pokemon('Magneton'), 'level': 21, 'moves': get_moves(['Thunder Wave', 'Spark', 'Sonic Boom'])},
        ],
        intro_text="La Centrale est tout près... méfie-toi des Voltorb !"
    )
    create_npc_trainer(
        username='Gamine Nadia',
        trainer_type='trainer',
        location='Route 10',
        team_data=[
            {'species': get_pokemon('Voltorb'), 'level': 20, 'moves': get_moves(['Tackle', 'Screech', 'Spark'])},
        ],
        intro_text="Allez, Voltorb, montre-leur ce que tu vaux !"
    )


def init_route_11_extra():
    """Route 11 — trainers additionnels (nom FR)"""
    logging.info("[*] Route 11 extra — trainers")
    create_npc_trainer(
        username='Gamin Alexis',
        trainer_type='trainer',
        location='Route 11',
        team_data=[
            {'species': get_pokemon('Ekans'),  'level': 17, 'moves': get_moves(['Bite', 'Poison Sting'])},
            {'species': get_pokemon('Ekans'),  'level': 17, 'moves': get_moves(['Bite', 'Glare'])},
        ],
        intro_text="Les serpents Pokémon sont mes alliés !"
    )


def init_route_24_extra():
    """Route 24 — trainers additionnels (nom FR)"""
    logging.info("[*] Route 24 extra — trainers")
    create_npc_trainer(
        username='Nageur Louis',
        trainer_type='trainer',
        location='Route 24',
        team_data=[
            {'species': get_pokemon('Goldeen'),   'level': 17, 'moves': get_moves(['Water Gun', 'Horn Attack'])},
        ],
        intro_text="Le Pont Cerclef est mon terrain de jeu !"
    )


def init_route_25_extra():
    """Route 25 — trainers additionnels (nom FR)"""
    logging.info("[*] Route 25 extra — trainers")
    create_npc_trainer(
        username='Lasseur Théo',
        trainer_type='trainer',
        location='Route 25',
        team_data=[
            {'species': get_pokemon('Caterpie'), 'level': 14, 'moves': get_moves(['Tackle', 'String Shot'])},
            {'species': get_pokemon('Weedle'),   'level': 14, 'moves': get_moves(['Poison Sting', 'String Shot'])},
            {'species': get_pokemon('Kakuna'),   'level': 14, 'moves': get_moves(['Harden'])},
        ],
        intro_text="Cette route mène au labo du Prof. Boulmich !"
    )
    create_npc_trainer(
        username='Naïade Emma',
        trainer_type='trainer',
        location='Route 25',
        team_data=[
            {'species': get_pokemon('Staryu'),   'level': 15, 'moves': get_moves(['Tackle', 'Water Gun', 'Harden'])},
        ],
        intro_text="La mer est magnifique ici. Mais gare à moi !"
    )


def run_complete_npc_initialization():
    """Lance l'initialisation complète de tous les NPCs manquants"""

    logging.info("="*70)
    logging.info("INITIALISATION COMPLÈTE DES NPCS DE KANTO")
    logging.info("="*70)

    # Supprimer les NPCs existants pour les zones concernées si besoin
    # (optionnel - commenter si on veut juste ajouter sans supprimer)
    # Trainer.objects.filter(trainer_type='trainer').delete()

    try:
        # ── Zones manquantes ou sans trainers ────────────────────────────────
        init_foret_de_jade()
        init_route_1_extra()
        init_route_3_extra()
        init_route_4_extra()
        init_route_6_extra()
        init_route_9_extra()
        init_route_10_extra()
        init_route_11_extra()
        init_route_24_extra()
        init_route_25_extra()
        # ── Zones du fichier original (locations FR corrigées) ────────────────
        init_route_2()
        init_route_5()
        init_route_7()
        init_route_8()
        init_route_12()
        init_route_13()
        init_route_14()
        init_route_15()
        init_route_16()
        init_route_17()
        init_route_18()
        init_route_19_20()
        init_route_21()
        init_route_22()
        init_route_23()
        init_power_plant()
        init_fuchsia_safari_zone()
        init_lavender_town()
        init_celadon_city()
        init_saffron_city()
        init_victory_road_extra()
        init_mt_moon_extra()
        init_rock_tunnel_extra()
        init_ss_anne_extra()
        init_seafoam_extra()

        total = Trainer.objects.filter(trainer_type='trainer').count()
        logging.info("="*70)
        logging.info(f"[✓] INITIALISATION TERMINÉE — {total} dresseurs NPCs au total")
        logging.info("="*70)

    except Exception as e:
        logging.error(f"[✗] ERREUR: {e}")
        raise


if __name__ == '__main__':
    run_complete_npc_initialization()