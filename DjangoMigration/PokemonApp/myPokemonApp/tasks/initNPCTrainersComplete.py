#!/usr/bin/python3
"""
Script d'initialisation COMPLET des dresseurs NPC de Kanto.
Remplace initialize_npc_trainers() (initializeItemsAndNpcs.py) ET
toutes les fonctions init_* du fichier initNPCTrainersComplete.py.

Source de référence : Bulbapedia — Walkthrough FireRed / LeafGreen
https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pokémon_FireRed_and_LeafGreen

Règle is_battle_required=True — STRICTEMENT inévitables dans FireRed/LeafGreen :
  ■ Route 24 (Pont Cerclef) : 5 dresseurs du pont + 1 Grunt Rocket final
      → couloir linéaire, impossible de passer sans se battre (Bulbapedia Part 5)
  ■ Mont Sélénite B2F (étage 3) : Team Rocket Grunt (Mont Sélénite)
      → couloir B2F unique (Bulbapedia Part 4)
  ■ Mont Sélénite B2F (étage 3) : Super Nerd Miguel
      → les fossiles BLOQUENT physiquement le chemin (Bulbapedia Part 4)
  ■ Tour Pokémon 4F : Jesse & James
      → script déclenché, bloquent l'escalier vers le sommet
  ■ QG Rocket Céladopole B3F (étage 3) : Executive Archer
      → boss de zone, script obligatoire
  ■ Sylphe SARL 11F (étage 11) : Giovanni Shadow
      → script scénaristique, impossible de contourner

Tout autre dresseur (routes ouvertes, grottes à plusieurs chemins,
bâtiments à layout libre) est OPTIONNEL.

Zones à étages couvertes :
  Mont Sélénite       : 1F (étage 1), B1F (étage 2), B2F (étage 3)
  SS Anne             : Pont (étage 1), 1F (étage 2), 2F (étage 3)
  Tour Pokémon        : 2F → 6F (étages 2 à 6) — 7F sans dresseur combattant
  QG Rocket           : B1F → B4F (étages 1 à 4)
  Sylphe SARL         : 1F, 2F, 3F, 5F, 7F, 11F
  Manoir Pokémon      : 1F, 2F, 3F, B1F (étages 1 à 4)
  Cave Taupiqueur     : Tunnel (étage 1)
  Îles Écume          : B1F → B4F (étages 1 à 4)
  Chemin de la Victoire: 1F → 3F (étages 1 à 3)
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


# ==============================================================================
# ROUTE 1
# ==============================================================================

def init_route_1():
    logging.info("[*] Route 1...")

    create_npc_trainer(
        username='Youngster Ben',
        trainer_type='trainer',
        location='Route 1',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 6, 'moves': get_moves(['Tackle', 'Tail Whip'])},
        ],
        intro_text="Hé! Tu veux te battre?"
    )
    create_npc_trainer(
        username='Youngster Calvin',
        trainer_type='trainer',
        location='Route 1',
        team_data=[
            {'species': get_pokemon('Spearow'), 'level': 7, 'moves': get_moves(['Peck'])},
        ],
        intro_text="Je suis nouveau dans le dressage!"
    )
    create_npc_trainer(
        username='Gamin Luc',
        trainer_type='trainer',
        location='Route 1',
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 3, 'moves': get_moves(['Tackle', 'Sand Attack'])},
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


# ==============================================================================
# FORÊT DE JADE
# ==============================================================================

def init_foret_de_jade():
    logging.info("[*] Forêt de Jade...")

    create_npc_trainer(
        username='Bug Catcher Rick',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Weedle'), 'level': 6, 'moves': get_moves(['Poison Sting'])},
            {'species': get_pokemon('Caterpie'), 'level': 6, 'moves': get_moves(['Tackle'])},
        ],
        intro_text="Les insectes sont les meilleurs!"
    )
    create_npc_trainer(
        username='Bug Catcher Doug',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Weedle'), 'level': 7, 'moves': get_moves(['Poison Sting'])},
            {'species': get_pokemon('Kakuna'), 'level': 7, 'moves': get_moves(['Harden'])},
            {'species': get_pokemon('Weedle'), 'level': 7, 'moves': get_moves(['Poison Sting'])},
        ],
        intro_text="Ma collection d'insectes est la meilleure!"
    )
    create_npc_trainer(
        username='Bug Catcher Sammy',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Weedle'), 'level': 9, 'moves': get_moves(['Poison Sting'])},
        ],
        intro_text="Les insectes sont cool!"
    )
    create_npc_trainer(
        username='Lasseur Sacha',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Caterpie'), 'level': 6, 'moves': get_moves(['Tackle', 'String Shot'])},
            {'species': get_pokemon('Weedle'), 'level': 6, 'moves': get_moves(['Poison Sting', 'String Shot'])},
        ],
        intro_text="Tu veux traverser ma forêt ? Il faut d'abord me battre !"
    )
    create_npc_trainer(
        username='Lasseur Éric',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Metapod'), 'level': 7, 'moves': get_moves(['Harden'])},
            {'species': get_pokemon('Caterpie'), 'level': 7, 'moves': get_moves(['Tackle', 'String Shot'])},
        ],
        intro_text="Mon Chrysacier va vous bloquer la route !"
    )
    create_npc_trainer(
        username='Lasseur Damien',
        trainer_type='trainer',
        location='Forêt de Jade',
        team_data=[
            {'species': get_pokemon('Weedle'), 'level': 7, 'moves': get_moves(['Poison Sting', 'String Shot'])},
            {'species': get_pokemon('Kakuna'), 'level': 7, 'moves': get_moves(['Harden'])},
            {'species': get_pokemon('Weedle'), 'level': 7, 'moves': get_moves(['Poison Sting', 'String Shot'])},
        ],
        intro_text="Les chenilles de la forêt m'obéissent !"
    )


# ==============================================================================
# ROUTE 2
# ==============================================================================

def init_route_2():
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


# ==============================================================================
# ROUTE 3
# ==============================================================================

def init_route_3():
    logging.info("[*] Route 3...")

    create_npc_trainer(
        username='Lass Janice',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 9, 'moves': get_moves(['Tackle', 'Gust'])},
            {'species': get_pokemon('Pidgey'), 'level': 9, 'moves': get_moves(['Tackle', 'Gust'])},
        ],
        intro_text="Mes oiseaux vont gagner!"
    )
    create_npc_trainer(
        username='Youngster Ben',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 8, 'moves': get_moves(['Tackle', 'Tail Whip'])},
            {'species': get_pokemon('Ekans'), 'level': 9, 'moves': get_moves(['Wrap', 'Poison Sting'])},
        ],
        intro_text="Prêt à perdre?"
    )
    create_npc_trainer(
        username='Bug Catcher James',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {'species': get_pokemon('Caterpie'), 'level': 11, 'moves': get_moves(['Tackle'])},
            {'species': get_pokemon('Metapod'), 'level': 11, 'moves': get_moves(['Harden'])},
        ],
        intro_text="Les chenilles deviendront des papillons!"
    )
    create_npc_trainer(
        username='Lass Sally',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 10, 'moves': get_moves(['Tackle', 'Tail Whip'])},
            {'species': get_pokemon('Nidoran♀'), 'level': 10, 'moves': get_moves(['Scratch', 'Tail Whip'])},
        ],
        intro_text="Tu aimes les Pokémon mignons?"
    )
    create_npc_trainer(
        username='Gamin Martin',
        trainer_type='trainer',
        location='Route 3',
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 10, 'moves': get_moves(['Gust', 'Sand Attack'])},
            {'species': get_pokemon('Rattata'), 'level': 10, 'moves': get_moves(['Tackle', 'Quick Attack'])},
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


# ==============================================================================
# MONT SÉLÉNITE
# is_battle_required :
#   - Team Rocket Grunt (B2F, couloir unique selon Bulbapedia Part 4)
#   - Super Nerd Miguel (B2F, fossiles bloquent le chemin — Bulbapedia Part 4 + Fandom)
# ==============================================================================

def init_mont_selenite():
    logging.info("[*] Mont Sélénite (1F / B1F / B2F)...")

    # ── 1F — Entrée ──────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Lass Iris',
        trainer_type='trainer',
        location='Mont Sélénite-1',
        team_data=[
            {'species': get_pokemon('Clefairy'), 'level': 14, 'moves': get_moves(['Pound', 'Growl'])},
        ],
        intro_text="Les Pokémon fée sont magnifiques!"
    )
    create_npc_trainer(
        username='Hiker Marcos',
        trainer_type='trainer',
        location='Mont Sélénite-1',
        team_data=[
            {'species': get_pokemon('Geodude'), 'level': 10, 'moves': get_moves(['Tackle', 'Defense Curl'])},
            {'species': get_pokemon('Geodude'), 'level': 10, 'moves': get_moves(['Tackle', 'Defense Curl'])},
            {'species': get_pokemon('Onix'), 'level': 10, 'moves': get_moves(['Tackle', 'Screech'])},
        ],
        intro_text="Les rochers sont solides!"
    )
    create_npc_trainer(
        username='Super Nerd Jovan',
        trainer_type='trainer',
        location='Mont Sélénite-1',
        team_data=[
            {'species': get_pokemon('Magnemite'), 'level': 11, 'moves': get_moves(['Tackle', 'Sonic Boom'])},
            {'species': get_pokemon('Voltorb'), 'level': 11, 'moves': get_moves(['Tackle', 'Screech'])},
        ],
        intro_text="La science est la clé!"
    )

    # ── B1F — Premier sous-sol (fossiles, premiers Rockets) ──────────────────
    create_npc_trainer(
        username='Hiker Eric',
        trainer_type='trainer',
        location='Mont Sélénite-2',
        team_data=[
            {'species': get_pokemon('Geodude'), 'level': 11, 'moves': get_moves(['Tackle', 'Defense Curl'])},
            {'species': get_pokemon('Graveler'), 'level': 11, 'moves': get_moves(['Tackle', 'Defense Curl', 'Rock Throw'])},
        ],
        intro_text="La montagne teste ta force!"
    )
    create_npc_trainer(
        username='Team Rocket Cassidy',
        trainer_type='trainer',
        location='Mont Sélénite-2',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 12, 'moves': get_moves(['Tackle', 'Hyper Fang'])},
            {'species': get_pokemon('Ekans'), 'level': 12, 'moves': get_moves(['Wrap', 'Leer', 'Bite'])},
        ],
        intro_text="Les fossiles rares appartiennent à la Team Rocket!"
    )
    create_npc_trainer(
        username='Super Nerd Clifford',
        trainer_type='trainer',
        location='Mont Sélénite-2',
        team_data=[
            {'species': get_pokemon('Clefairy'), 'level': 13, 'moves': get_moves(['Pound', 'Growl', 'Sing'])},
            {'species': get_pokemon('Clefairy'), 'level': 13, 'moves': get_moves(['Pound', 'Growl', 'Sing'])},
        ],
        intro_text="Les Mélofée du Mont Lune m'ont choisi!"
    )

    # ── B2F — Galeries profondes (sortie Route 4) — Grunt + Miguel OBLIGATOIRES
    # Grunt dans le couloir unique (Bulbapedia Part 4)
    create_npc_trainer(
        username='Team Rocket Grunt (Mont Sélénite)',
        trainer_type='trainer',
        location='Mont Sélénite-3',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 11, 'moves': get_moves(['Tackle', 'Tail Whip'])},
            {'species': get_pokemon('Zubat'), 'level': 11, 'moves': get_moves(['Leech Life', 'Supersonic'])},
        ],
        intro_text="Prépare-toi, gamin!"
    )
    # Super Nerd Miguel — les fossiles bloquent physiquement le chemin (OBLIGATOIRE)
    create_npc_trainer(
        username='Super Nerd Miguel',
        trainer_type='trainer',
        location='Mont Sélénite-3',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Grimer'), 'level': 12, 'moves': get_moves(['Pound', 'Disable'])},
            {'species': get_pokemon('Voltorb'), 'level': 12, 'moves': get_moves(['Tackle', 'Screech'])},
            {'species': get_pokemon('Koffing'), 'level': 12, 'moves': get_moves(['Tackle', 'Smog'])},
        ],
        intro_text="Ces fossiles sont à moi ! Tu ne les auras pas !"
    )
    create_npc_trainer(
        username='Team Rocket Butch',
        trainer_type='trainer',
        location='Mont Sélénite-3',
        team_data=[
            {'species': get_pokemon('Zubat'), 'level': 13, 'moves': get_moves(['Leech Life', 'Supersonic', 'Bite'])},
            {'species': get_pokemon('Sandshrew'), 'level': 13, 'moves': get_moves(['Scratch', 'Defense Curl', 'Sand Attack'])},
        ],
        intro_text="Rendez-nous ces fossiles!"
    )


# ==============================================================================
# ROUTE 4
# ==============================================================================

def init_route_4():
    logging.info("[*] Route 4...")

    create_npc_trainer(
        username='Lass Crissy',
        trainer_type='trainer',
        location='Route 4',
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 13, 'moves': get_moves(['Gust', 'Quick Attack'])},
            {'species': get_pokemon('Rattata'), 'level': 13, 'moves': get_moves(['Hyper Fang', 'Quick Attack'])},
        ],
        intro_text="C'est mon jour de chance!"
    )
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


# ==============================================================================
# ROUTE 24 — PONT CERCLEF (NUGGET BRIDGE)
# TOUS les 6 combats sont obligatoires (couloir linéaire, Bulbapedia Part 5)
# "There are five Trainers to be fought on the famous Nugget Bridge."
# + le Grunt Rocket final déclenché par script quand on refuse de rejoindre
# ==============================================================================

def init_route_24():
    logging.info("[*] Route 24 (Pont Cerclef — combats obligatoires)...")

    create_npc_trainer(
        username='Bug Catcher Cale',
        trainer_type='trainer',
        location='Route 24',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Caterpie'), 'level': 10, 'moves': get_moves(['Tackle', 'String Shot'])},
            {'species': get_pokemon('Weedle'), 'level': 10, 'moves': get_moves(['Poison Sting', 'String Shot'])},
            {'species': get_pokemon('Metapod'), 'level': 10, 'moves': get_moves(['Harden'])},
            {'species': get_pokemon('Kakuna'), 'level': 10, 'moves': get_moves(['Harden'])},
        ],
        intro_text="Le Pont Cerclef, terrain de chasse des insectes !"
    )
    create_npc_trainer(
        username='Lass Mirelle',
        trainer_type='trainer',
        location='Route 24',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 12, 'moves': get_moves(['Gust', 'Sand Attack'])},
            {'species': get_pokemon('Oddish'), 'level': 12, 'moves': get_moves(['Absorb', 'Poison Powder'])},
            {'species': get_pokemon('Bellsprout'), 'level': 12, 'moves': get_moves(['Vine Whip', 'Growth'])},
        ],
        intro_text="Bienvenue sur le pont !"
    )
    create_npc_trainer(
        username='Camper Liam',
        trainer_type='trainer',
        location='Route 24',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Sandshrew'), 'level': 14, 'moves': get_moves(['Scratch', 'Defense Curl'])},
        ],
        intro_text="Le Nugget Bridge est célèbre!"
    )
    create_npc_trainer(
        username='Lass Ali',
        trainer_type='trainer',
        location='Route 24',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 12, 'moves': get_moves(['Gust', 'Sand Attack'])},
            {'species': get_pokemon('Nidoran♀'), 'level': 14, 'moves': get_moves(['Scratch', 'Poison Sting'])},
        ],
        intro_text="Bienvenue sur le pont!"
    )
    create_npc_trainer(
        username='Youngster Timmy',
        trainer_type='trainer',
        location='Route 24',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 14, 'moves': get_moves(['Tackle', 'Hyper Fang'])},
            {'species': get_pokemon('Ekans'), 'level': 14, 'moves': get_moves(['Wrap', 'Poison Sting'])},
        ],
        intro_text="On va se battre!"
    )
    # Grunt final — script déclenché (refuse de rejoindre la Team Rocket)
    create_npc_trainer(
        username='Team Rocket Grunt',
        trainer_type='trainer',
        location='Route 24',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 15, 'moves': get_moves(['Wrap', 'Poison Sting', 'Bite'])},
            {'species': get_pokemon('Zubat'), 'level': 15, 'moves': get_moves(['Leech Life', 'Supersonic', 'Bite'])},
        ],
        intro_text="Rejoins la Team Rocket!"
    )
    # Dresseur optionnel sur la route (hors pont)
    create_npc_trainer(
        username='Nageur Louis',
        trainer_type='trainer',
        location='Route 24',
        team_data=[
            {'species': get_pokemon('Goldeen'), 'level': 17, 'moves': get_moves(['Water Gun', 'Horn Attack'])},
        ],
        intro_text="Le Pont Cerclef est mon terrain de jeu !"
    )


# ==============================================================================
# ROUTE 25
# ==============================================================================

def init_route_25():
    logging.info("[*] Route 25...")

    create_npc_trainer(
        username='Hiker Franklin',
        trainer_type='trainer',
        location='Route 25',
        team_data=[
            {'species': get_pokemon('Machop'), 'level': 15, 'moves': get_moves(['Low Kick', 'Leer'])},
            {'species': get_pokemon('Geodude'), 'level': 15, 'moves': get_moves(['Tackle', 'Defense Curl'])},
        ],
        intro_text="L'entraînement rend fort!"
    )
    create_npc_trainer(
        username='Youngster Dan',
        trainer_type='trainer',
        location='Route 25',
        team_data=[
            {'species': get_pokemon('Slowpoke'), 'level': 17, 'moves': get_moves(['Tackle', 'Growl'])},
        ],
        intro_text="Mon Slowpoke est spécial!"
    )
    create_npc_trainer(
        username='Lasseur Théo',
        trainer_type='trainer',
        location='Route 25',
        team_data=[
            {'species': get_pokemon('Caterpie'), 'level': 14, 'moves': get_moves(['Tackle', 'String Shot'])},
            {'species': get_pokemon('Weedle'), 'level': 14, 'moves': get_moves(['Poison Sting', 'String Shot'])},
            {'species': get_pokemon('Kakuna'), 'level': 14, 'moves': get_moves(['Harden'])},
        ],
        intro_text="Cette route mène au labo du Prof. Boulmich !"
    )
    create_npc_trainer(
        username='Naïade Emma',
        trainer_type='trainer',
        location='Route 25',
        team_data=[
            {'species': get_pokemon('Staryu'), 'level': 15, 'moves': get_moves(['Tackle', 'Water Gun', 'Harden'])},
        ],
        intro_text="La mer est magnifique ici. Mais gare à moi !"
    )


# ==============================================================================
# S.S. ANNE / CARMIN SUR MER
# ==============================================================================

def init_ss_anne():
    logging.info("[*] S.S. Anne...")

    # ── Pont extérieur (étage 1) ──────────────────────────────────────────────
    create_npc_trainer(
        username='Sailor Edmond',
        trainer_type='trainer',
        location='SS Anne-1',
        team_data=[
            {'species': get_pokemon('Machop'), 'level': 18, 'moves': get_moves(['Low Kick', 'Leer', 'Karate Chop'])},
            {'species': get_pokemon('Shellder'), 'level': 18, 'moves': get_moves(['Tackle', 'Withdraw'])},
        ],
        intro_text="Ahoy, marin d'eau douce!"
    )
    create_npc_trainer(
        username='Gentleman Thomas',
        trainer_type='trainer',
        location='SS Anne-1',
        team_data=[
            {'species': get_pokemon('Growlithe'), 'level': 18, 'moves': get_moves(['Bite', 'Roar', 'Ember'])},
            {'species': get_pokemon('Ponyta'), 'level': 18, 'moves': get_moves(['Tackle', 'Growl', 'Ember'])},
        ],
        intro_text="Un combat de gentlemen?"
    )

    # ── 1F — Salon principal (étage 2) ────────────────────────────────────────
    create_npc_trainer(
        username='Lass Ann',
        trainer_type='trainer',
        location='SS Anne-2',
        team_data=[
            {'species': get_pokemon('Pidgey'), 'level': 18, 'moves': get_moves(['Gust', 'Sand Attack'])},
            {'species': get_pokemon('Nidoran♀'), 'level': 18, 'moves': get_moves(['Scratch', 'Poison Sting'])},
        ],
        intro_text="Cette croisière est géniale!"
    )
    create_npc_trainer(
        username='Sailor Eddy',
        trainer_type='trainer',
        location='SS Anne-2',
        team_data=[
            {'species': get_pokemon('Tentacool'), 'level': 19, 'moves': get_moves(['Acid', 'Constrict'])},
            {'species': get_pokemon('Machop'), 'level': 19, 'moves': get_moves(['Low Kick', 'Karate Chop', 'Leer'])},
        ],
        intro_text="Les marins sont les meilleurs combattants!"
    )

    # ── 2F — Cabines de luxe (étage 3) ───────────────────────────────────────
    create_npc_trainer(
        username='Gentleman Brooks',
        trainer_type='trainer',
        location='SS Anne-3',
        team_data=[
            {'species': get_pokemon('Nidoran♂'), 'level': 18, 'moves': get_moves(['Leer', 'Tackle', 'Poison Sting'])},
            {'species': get_pokemon('Nidoran♀'), 'level': 18, 'moves': get_moves(['Scratch', 'Tail Whip', 'Poison Sting'])},
        ],
        intro_text="Les gentlemen partagent leur savoir en duel!"
    )
    create_npc_trainer(
        username='Super Nerd Felix',
        trainer_type='trainer',
        location='SS Anne-3',
        team_data=[
            {'species': get_pokemon('Magnemite'), 'level': 20, 'moves': get_moves(['Thunder Shock', 'Sonic Boom'])},
            {'species': get_pokemon('Magnemite'), 'level': 20, 'moves': get_moves(['Thunder Shock', 'Sonic Boom'])},
            {'species': get_pokemon('Magnemite'), 'level': 20, 'moves': get_moves(['Thunder Shock', 'Sonic Boom'])},
        ],
        intro_text="Mes Magnéti sont chargés à fond!"
    )


# ==============================================================================
# ROUTE 5
# ==============================================================================

def init_route_5():
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


# ==============================================================================
# ROUTE 6
# ==============================================================================

def init_route_6():
    logging.info("[*] Route 6...")

    create_npc_trainer(
        username='Bug Catcher Kent',
        trainer_type='trainer',
        location='Route 6',
        team_data=[
            {'species': get_pokemon('Weedle'), 'level': 11, 'moves': get_moves(['Poison Sting'])},
            {'species': get_pokemon('Kakuna'), 'level': 11, 'moves': get_moves(['Harden'])},
        ],
        intro_text="Les insectes règnent!"
    )
    create_npc_trainer(
        username='Camper Ricky',
        trainer_type='trainer',
        location='Route 6',
        team_data=[
            {'species': get_pokemon('Squirtle'), 'level': 20, 'moves': get_moves(['Tackle', 'Tail Whip', 'Bubble'])},
        ],
        intro_text="Le camping c'est la vie!"
    )
    create_npc_trainer(
        username='Gamin Cyril',
        trainer_type='trainer',
        location='Route 6',
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 15, 'moves': get_moves(['Wrap', 'Leer', 'Poison Sting'])},
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


# ==============================================================================
# TUNNEL ROCHE
# ==============================================================================

def init_tunnel_roche():
    logging.info("[*] Tunnel Roche...")

    create_npc_trainer(
        username='Hiker Lenny',
        trainer_type='trainer',
        location='Tunnel Roche',
        team_data=[
            {'species': get_pokemon('Geodude'), 'level': 19, 'moves': get_moves(['Tackle', 'Defense Curl'])},
            {'species': get_pokemon('Machop'), 'level': 19, 'moves': get_moves(['Low Kick', 'Leer'])},
            {'species': get_pokemon('Geodude'), 'level': 19, 'moves': get_moves(['Tackle', 'Defense Curl'])},
        ],
        intro_text="Ces tunnels sont mon terrain!"
    )
    create_npc_trainer(
        username='Picnicker Dana',
        trainer_type='trainer',
        location='Tunnel Roche',
        team_data=[
            {'species': get_pokemon('Meowth'), 'level': 19, 'moves': get_moves(['Scratch', 'Growl', 'Bite'])},
            {'species': get_pokemon('Oddish'), 'level': 19, 'moves': get_moves(['Absorb', 'Poison Powder'])},
            {'species': get_pokemon('Pidgey'), 'level': 19, 'moves': get_moves(['Gust', 'Quick Attack'])},
        ],
        intro_text="Perdue dans le tunnel!"
    )
    create_npc_trainer(
        username='Pokemaniac Mark',
        trainer_type='trainer',
        location='Tunnel Roche',
        team_data=[
            {'species': get_pokemon('Rhyhorn'), 'level': 29, 'moves': get_moves(['Horn Attack', 'Stomp'])},
            {'species': get_pokemon('Lickitung'), 'level': 29, 'moves': get_moves(['Lick', 'Supersonic'])},
        ],
        intro_text="Les Pokémon rares sont ma passion!"
    )
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


# ==============================================================================
# ROUTE 9
# ==============================================================================

def init_route_9():
    logging.info("[*] Route 9...")

    create_npc_trainer(
        username='Hiker Jeremy',
        trainer_type='trainer',
        location='Route 9',
        team_data=[
            {'species': get_pokemon('Machop'), 'level': 20, 'moves': get_moves(['Low Kick', 'Leer', 'Karate Chop'])},
            {'species': get_pokemon('Onix'), 'level': 20, 'moves': get_moves(['Tackle', 'Screech', 'Bind'])},
        ],
        intro_text="La montagne m'a rendu fort!"
    )
    create_npc_trainer(
        username='Bug Catcher Brent',
        trainer_type='trainer',
        location='Route 9',
        team_data=[
            {'species': get_pokemon('Beedrill'), 'level': 19, 'moves': get_moves(['Fury Attack', 'Twineedle'])},
            {'species': get_pokemon('Beedrill'), 'level': 19, 'moves': get_moves(['Fury Attack', 'Twineedle'])},
        ],
        intro_text="Mes Dardargnan sont redoutables!"
    )
    create_npc_trainer(
        username='Gamin Tom',
        trainer_type='trainer',
        location='Route 9',
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 20, 'moves': get_moves(['Bite', 'Glare', 'Poison Sting'])},
            {'species': get_pokemon('Spearow'), 'level': 20, 'moves': get_moves(['Peck', 'Leer', 'Fury Attack'])},
        ],
        intro_text="Cette route est dangereuse. Comme moi !"
    )


# ==============================================================================
# ROUTE 10
# ==============================================================================

def init_route_10():
    logging.info("[*] Route 10...")

    create_npc_trainer(
        username='Pokemaniac Steve',
        trainer_type='trainer',
        location='Route 10',
        team_data=[
            {'species': get_pokemon('Cubone'), 'level': 22, 'moves': get_moves(['Bone Club', 'Growl', 'Headbutt'])},
            {'species': get_pokemon('Slowpoke'), 'level': 22, 'moves': get_moves(['Tackle', 'Growl', 'Water Gun'])},
        ],
        intro_text="J'aime les Pokémon étranges!"
    )
    create_npc_trainer(
        username='Rocker Max',
        trainer_type='trainer',
        location='Route 10',
        team_data=[
            {'species': get_pokemon('Voltorb'), 'level': 21, 'moves': get_moves(['Screech', 'Spark', 'Tackle'])},
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


# ==============================================================================
# ROUTE 11
# ==============================================================================

def init_route_11():
    logging.info("[*] Route 11...")

    create_npc_trainer(
        username='Gambler Hugo',
        trainer_type='trainer',
        location='Route 11',
        team_data=[
            {'species': get_pokemon('Poliwag'), 'level': 18, 'moves': get_moves(['Bubble', 'Hypnosis'])},
            {'species': get_pokemon('Horsea'), 'level': 18, 'moves': get_moves(['Bubble', 'Smokescreen'])},
        ],
        intro_text="Faisons un pari!"
    )
    create_npc_trainer(
        username='Engineer Baily',
        trainer_type='trainer',
        location='Route 11',
        team_data=[
            {'species': get_pokemon('Voltorb'), 'level': 21, 'moves': get_moves(['Tackle', 'Screech', 'Sonic Boom'])},
            {'species': get_pokemon('Magnemite'), 'level': 21, 'moves': get_moves(['Tackle', 'Sonic Boom', 'Thunder Shock'])},
        ],
        intro_text="L'électricité, c'est fantastique!"
    )
    create_npc_trainer(
        username='Gamin Alexis',
        trainer_type='trainer',
        location='Route 11',
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 17, 'moves': get_moves(['Bite', 'Poison Sting'])},
            {'species': get_pokemon('Ekans'), 'level': 17, 'moves': get_moves(['Bite', 'Glare'])},
        ],
        intro_text="Les serpents Pokémon sont mes alliés !"
    )


# ==============================================================================
# ROUTE 7
# ==============================================================================

def init_route_7():
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


# ==============================================================================
# ROUTE 8
# ==============================================================================

def init_route_8():
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


# ==============================================================================
# CÉLADOPOLE — QG TEAM ROCKET
# Executive Archer = boss obligatoire (script) — Bulbapedia
# ==============================================================================

def init_celadon_city():
    logging.info("[*] QG Team Rocket (Céladopole)...")

    # ── B1F ──────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Team Rocket Grunt A',
        trainer_type='trainer',
        location='Quartier Général Rocket-1',
        team_data=[
            {'species': get_pokemon('Raticate'), 'level': 25, 'moves': get_moves(['Hyper Fang', 'Quick Attack'])},
            {'species': get_pokemon('Zubat'), 'level': 25, 'moves': get_moves(['Bite', 'Leech Life', 'Supersonic'])},
        ],
        intro_text="Que fais-tu ici?!"
    )
    create_npc_trainer(
        username='Team Rocket Grunt B',
        trainer_type='trainer',
        location='Quartier Général Rocket-1',
        team_data=[
            {'species': get_pokemon('Grimer'), 'level': 26, 'moves': get_moves(['Pound', 'Disable', 'Sludge'])},
            {'species': get_pokemon('Koffing'), 'level': 26, 'moves': get_moves(['Smog', 'Tackle', 'Poison Gas'])},
        ],
        intro_text="Tu fouines dans nos affaires?!"
    )

    # ── B2F ──────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Team Rocket Grunt C',
        trainer_type='trainer',
        location='Quartier Général Rocket-2',
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 26, 'moves': get_moves(['Wrap', 'Bite', 'Screech'])},
            {'species': get_pokemon('Sandshrew'), 'level': 26, 'moves': get_moves(['Scratch', 'Sand Attack', 'Slash'])},
        ],
        intro_text="Ces couloirs sont à nous!"
    )
    create_npc_trainer(
        username='Team Rocket Grunt D',
        trainer_type='trainer',
        location='Quartier Général Rocket-2',
        team_data=[
            {'species': get_pokemon('Drowzee'), 'level': 27, 'moves': get_moves(['Pound', 'Hypnosis', 'Confusion'])},
            {'species': get_pokemon('Machop'), 'level': 27, 'moves': get_moves(['Low Kick', 'Leer', 'Karate Chop'])},
        ],
        intro_text="Tu ne passeras pas plus loin!"
    )

    # ── B3F — Boss obligatoire (Archer) ──────────────────────────────────────
    create_npc_trainer(
        username='Team Rocket Grunt E',
        trainer_type='trainer',
        location='Quartier Général Rocket-3',
        team_data=[
            {'species': get_pokemon('Arbok'), 'level': 27, 'moves': get_moves(['Wrap', 'Bite', 'Glare'])},
            {'species': get_pokemon('Weezing'), 'level': 27, 'moves': get_moves(['Smog', 'Sludge', 'Smokescreen'])},
        ],
        intro_text="C'est notre quartier général, intrus!"
    )
    # Archer — boss scénaristique OBLIGATOIRE
    create_npc_trainer(
        username='Team Rocket Executive Archer',
        trainer_type='trainer',
        location='Quartier Général Rocket-3',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Arbok'), 'level': 28, 'moves': get_moves(['Wrap', 'Bite', 'Screech'])},
            {'species': get_pokemon('Weezing'), 'level': 28, 'moves': get_moves(['Smog', 'Tackle', 'Sludge'])},
            {'species': get_pokemon('Hypno'), 'level': 28, 'moves': get_moves(['Pound', 'Hypnosis', 'Confusion', 'Disable'])},
        ],
        intro_text="Tu ne peux pas arrêter la Team Rocket!"
    )

    # ── B4F — Salle au trésor (Lunette Silph) ────────────────────────────────
    create_npc_trainer(
        username='Team Rocket Grunt F',
        trainer_type='trainer',
        location='Quartier Général Rocket-4',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 28, 'moves': get_moves(['Hyper Fang', 'Quick Attack', 'Bite'])},
            {'species': get_pokemon('Raticate'), 'level': 28, 'moves': get_moves(['Hyper Fang', 'Quick Attack', 'Super Fang'])},
        ],
        intro_text="La Lunette Silph est notre trésor — tu ne l'auras pas!"
    )


# ==============================================================================
# TOUR POKÉMON — LAVANVILLE
# Jesse & James (4F) = OBLIGATOIRES — bloquent l'escalier par script
# ==============================================================================

def init_lavender_town():
    logging.info("[*] Tour Pokémon (2F → 7F)...")

    # ── 2F ───────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Channeler Margaret',
        trainer_type='trainer',
        location='Tour Pokémon-2',
        team_data=[
            {'species': get_pokemon('Gastly'), 'level': 22, 'moves': get_moves(['Lick', 'Spite'])},
        ],
        intro_text="Les défunts parlent à travers moi..."
    )

    # ── 3F ───────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Channeler Tammy',
        trainer_type='trainer',
        location='Tour Pokémon-3',
        team_data=[
            {'species': get_pokemon('Gastly'), 'level': 23, 'moves': get_moves(['Lick', 'Spite', 'Confuse Ray'])},
            {'species': get_pokemon('Haunter'), 'level': 25, 'moves': get_moves(['Lick', 'Hypnosis', 'Night Shade'])},
        ],
        intro_text="Je vois l'au-delà..."
    )
    create_npc_trainer(
        username='Channeler Karina',
        trainer_type='trainer',
        location='Tour Pokémon-3',
        team_data=[
            {'species': get_pokemon('Haunter'), 'level': 24, 'moves': get_moves(['Lick', 'Night Shade', 'Hypnosis'])},
        ],
        intro_text="Les esprits m'ont accordé leur pouvoir!"
    )
    create_npc_trainer(
        username='Channeler Hope',
        trainer_type='trainer',
        location='Tour Pokémon-3',
        team_data=[
            {'species': get_pokemon('Gastly'), 'level': 23, 'moves': get_moves(['Lick', 'Spite', 'Confuse Ray'])},
        ],
        intro_text="Les esprits m'appellent..."
    )
    create_npc_trainer(
        username='Channeler Patricia',
        trainer_type='trainer',
        location='Tour Pokémon-3',
        team_data=[
            {'species': get_pokemon('Gastly'), 'level': 22, 'moves': get_moves(['Lick', 'Spite'])},
            {'species': get_pokemon('Haunter'), 'level': 24, 'moves': get_moves(['Lick', 'Spite', 'Hypnosis'])},
        ],
        intro_text="Je vois les âmes des Pokémon..."
    )

    # ── 4F — Jesse & James bloquent l'escalier (OBLIGATOIRES) ────────────────
    create_npc_trainer(
        username='Team Rocket Jesse',
        trainer_type='trainer',
        location='Tour Pokémon-4',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Ekans'), 'level': 23, 'moves': get_moves(['Wrap', 'Bite', 'Poison Sting'])},
            {'species': get_pokemon('Drowzee'), 'level': 23, 'moves': get_moves(['Pound', 'Hypnosis', 'Confusion'])},
        ],
        intro_text="Nous sommes de la Team Rocket! La Tour nous appartient!"
    )
    create_npc_trainer(
        username='Team Rocket James',
        trainer_type='trainer',
        location='Tour Pokémon-4',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Koffing'), 'level': 23, 'moves': get_moves(['Tackle', 'Smog', 'Poison Gas'])},
            {'species': get_pokemon('Zubat'), 'level': 23, 'moves': get_moves(['Leech Life', 'Bite', 'Supersonic'])},
        ],
        intro_text="Prepare for trouble... et maintenant du combat!"
    )

    # ── 5F ───────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Channeler Laurel',
        trainer_type='trainer',
        location='Tour Pokémon-5',
        team_data=[
            {'species': get_pokemon('Haunter'), 'level': 26, 'moves': get_moves(['Night Shade', 'Hypnosis', 'Confuse Ray'])},
        ],
        intro_text="Les esprits ici sont plus anciens et plus sombres..."
    )
    create_npc_trainer(
        username='Channeler Jody',
        trainer_type='trainer',
        location='Tour Pokémon-5',
        team_data=[
            {'species': get_pokemon('Gastly'), 'level': 24, 'moves': get_moves(['Lick', 'Spite', 'Mean Look'])},
            {'species': get_pokemon('Gastly'), 'level': 24, 'moves': get_moves(['Lick', 'Confuse Ray', 'Mean Look'])},
        ],
        intro_text="Mes Fantominus garderont ces couloirs éternellement!"
    )
    create_npc_trainer(
        username='Team Rocket Grunt (Tour)',
        trainer_type='trainer',
        location='Tour Pokémon-5',
        team_data=[
            {'species': get_pokemon('Zubat'), 'level': 25, 'moves': get_moves(['Bite', 'Leech Life', 'Supersonic'])},
            {'species': get_pokemon('Cubone'), 'level': 25, 'moves': get_moves(['Bone Club', 'Headbutt', 'Leer'])},
        ],
        intro_text="Les ossements ici valent de l'or pour la Team Rocket!"
    )

    # ── 6F ───────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Channeler Astrid',
        trainer_type='trainer',
        location='Tour Pokémon-6',
        team_data=[
            {'species': get_pokemon('Haunter'), 'level': 27, 'moves': get_moves(['Night Shade', 'Hypnosis', 'Lick'])},
            {'species': get_pokemon('Haunter'), 'level': 27, 'moves': get_moves(['Confuse Ray', 'Night Shade', 'Spite'])},
        ],
        intro_text="Deux Ectoplasma pour punir les vivants!"
    )
    create_npc_trainer(
        username='Team Rocket Grunt (Tour 6F)',
        trainer_type='trainer',
        location='Tour Pokémon-6',
        team_data=[
            {'species': get_pokemon('Raticate'), 'level': 26, 'moves': get_moves(['Hyper Fang', 'Quick Attack', 'Bite'])},
            {'species': get_pokemon('Arbok'), 'level': 26, 'moves': get_moves(['Wrap', 'Bite', 'Screech'])},
        ],
        intro_text="Tu ne monteras pas plus haut!"
    )

    # ── 7F — Sommet (spectre de Marowak + M. Fuji) ───────────────────────────
    # Aucun dresseur combattant au 7F : Marowak est un Pokémon sauvage
    # spécial (impossible à capturer), M. Fuji est un PNJ non-combattant.


# ==============================================================================
# SAFRANIA — SYLPHE SARL
# Giovanni Shadow = OBLIGATOIRE (script scénaristique — Bulbapedia)
# ==============================================================================

def init_saffron_city():
    logging.info("[*] Sylphe SARL (Safrania)...")

    # ── 1F — Hall d'accueil ───────────────────────────────────────────────────
    create_npc_trainer(
        username='Team Rocket Grunt A',
        trainer_type='trainer',
        location='Sylphe SARL-1',
        team_data=[
            {'species': get_pokemon('Cubone'), 'level': 29, 'moves': get_moves(['Bone Club', 'Headbutt', 'Leer'])},
            {'species': get_pokemon('Drowzee'), 'level': 29, 'moves': get_moves(['Pound', 'Hypnosis', 'Confusion'])},
        ],
        intro_text="Silph sera à nous!"
    )
    create_npc_trainer(
        username='Team Rocket Grunt B',
        trainer_type='trainer',
        location='Sylphe SARL-1',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 27, 'moves': get_moves(['Hyper Fang', 'Quick Attack'])},
            {'species': get_pokemon('Zubat'), 'level': 27, 'moves': get_moves(['Bite', 'Leech Life', 'Supersonic'])},
        ],
        intro_text="La Sylphe Co. va alimenter notre empire!"
    )

    # ── 2F / 3F — Labos et couloirs ───────────────────────────────────────────
    create_npc_trainer(
        username='Scientist Jose',
        trainer_type='trainer',
        location='Sylphe SARL-2',
        team_data=[
            {'species': get_pokemon('Electrode'), 'level': 29, 'moves': get_moves(['Sonic Boom', 'Self-Destruct'])},
            {'species': get_pokemon('Weezing'), 'level': 29, 'moves': get_moves(['Tackle', 'Smog', 'Sludge'])},
        ],
        intro_text="La science au service de Silph!"
    )
    create_npc_trainer(
        username='Team Rocket Grunt C',
        trainer_type='trainer',
        location='Sylphe SARL-2',
        team_data=[
            {'species': get_pokemon('Grimer'), 'level': 28, 'moves': get_moves(['Pound', 'Disable', 'Sludge'])},
            {'species': get_pokemon('Koffing'), 'level': 28, 'moves': get_moves(['Smog', 'Poison Gas', 'Sludge'])},
        ],
        intro_text="Ce couloir est sous notre contrôle!"
    )
    create_npc_trainer(
        username='Scientist Franklin',
        trainer_type='trainer',
        location='Sylphe SARL-3',
        team_data=[
            {'species': get_pokemon('Magnemite'), 'level': 29, 'moves': get_moves(['Thunder Shock', 'Sonic Boom', 'Thunder Wave'])},
            {'species': get_pokemon('Electrode'), 'level': 29, 'moves': get_moves(['Tackle', 'Screech', 'Self-Destruct'])},
        ],
        intro_text="La science au service du mal... pourquoi pas?"
    )
    create_npc_trainer(
        username='Team Rocket Grunt D',
        trainer_type='trainer',
        location='Sylphe SARL-3',
        team_data=[
            {'species': get_pokemon('Arbok'), 'level': 30, 'moves': get_moves(['Wrap', 'Bite', 'Glare'])},
            {'species': get_pokemon('Hypno'), 'level': 30, 'moves': get_moves(['Pound', 'Hypnosis', 'Confusion'])},
        ],
        intro_text="Le Laissez-Passer ne vous donnera pas accès à tout!"
    )

    # ── 5F — Scientifique prisonnier (donne le Laissez-Passer) ───────────────
    create_npc_trainer(
        username='Team Rocket Grunt E',
        trainer_type='trainer',
        location='Sylphe SARL-5',
        team_data=[
            {'species': get_pokemon('Rattata'), 'level': 30, 'moves': get_moves(['Hyper Fang', 'Quick Attack', 'Bite'])},
            {'species': get_pokemon('Ekans'), 'level': 30, 'moves': get_moves(['Wrap', 'Glare', 'Bite'])},
        ],
        intro_text="Ce scientifique est notre otage, dégages!"
    )

    # ── 7F — Blue (rival) + accès bureau du Président ────────────────────────
    create_npc_trainer(
        username='Rival - Silph Co.',
        trainer_type='trainer',
        location='Sylphe SARL-7',
        team_data=[
            {'species': get_pokemon('Pidgeot'),   'level': 37, 'moves': get_moves(['Wing Attack', 'Quick Attack', 'Sand Attack'])},
            {'species': get_pokemon('Gyarados'),  'level': 38, 'moves': get_moves(['Bite', 'Dragon Rage', 'Hydro Pump'])},
            {'species': get_pokemon('Growlithe'), 'level': 35, 'moves': get_moves(['Bite', 'Ember', 'Roar'])},
            {'species': get_pokemon('Alakazam'),  'level': 38, 'moves': get_moves(['Psybeam', 'Recover', 'Psychic'])},
        ],
        intro_text="Je t'attendais ici! Tu es vraiment tenace..."
    )

    # ── 11F — Giovanni (OBLIGATOIRE — script de libération de Sylphe SARL) ───
    # Giovanni Shadow — script scénaristique OBLIGATOIRE
    create_npc_trainer(
        username='Team Rocket Giovanni Shadow',
        trainer_type='trainer',
        location='Sylphe SARL-11',
        is_battle_required=True,
        team_data=[
            {'species': get_pokemon('Nidorino'),  'level': 35, 'moves': get_moves(['Horn Attack', 'Double Kick', 'Poison Sting'])},
            {'species': get_pokemon('Kangaskhan'), 'level': 35, 'moves': get_moves(['Headbutt', 'Dizzy Punch', 'Tail Whip'])},
            {'species': get_pokemon('Rhyhorn'),   'level': 37, 'moves': get_moves(['Horn Attack', 'Stomp', 'Tail Whip'])},
        ],
        intro_text="Giovanni - Sylphe SARL: Cette entreprise sera à nous... enfin à la Team Rocket!"
    )


# ==============================================================================
# ROUTES 12-15
# ==============================================================================

def init_route_12():
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


# ==============================================================================
# ROUTES 16-18 (ROUTE DU VÉLO)
# ==============================================================================

def init_route_16():
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
    logging.info("[*] Route 17 (Route du Vélo)...")

    create_npc_trainer(
        username='Biker Jaren',
        trainer_type='trainer',
        location='Route 17',
        team_data=[
            {'species': get_pokemon('Grimer'), 'level': 28, 'moves': get_moves(['Pound', 'Poison Gas', 'Sludge'])},
            {'species': get_pokemon('Grimer'), 'level': 28, 'moves': get_moves(['Pound', 'Poison Gas', 'Sludge'])},
        ],
        intro_text="À fond la vitesse!"
    )
    create_npc_trainer(
        username='Cue Ball Corey',
        trainer_type='trainer',
        location='Route 17',
        team_data=[
            {'species': get_pokemon('Primeape'), 'level': 29, 'moves': get_moves(['Scratch', 'Leer', 'Karate Chop'])},
            {'species': get_pokemon('Machop'), 'level': 29, 'moves': get_moves(['Low Kick', 'Leer', 'Karate Chop'])},
        ],
        intro_text="Dégage de mon chemin!"
    )
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


# ==============================================================================
# ROUTES 19-21
# ==============================================================================

def init_route_19_20():
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


# ==============================================================================
# ROUTES 22 ET 23
# ==============================================================================

def init_route_22():
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


# ==============================================================================
# CENTRALE ÉLECTRIQUE
# ==============================================================================

def init_power_plant():
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


# ==============================================================================
# ZONE SAFARI
# ==============================================================================

def init_safari_zone():
    logging.info("[*] Zone Safari...")

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



# ==============================================================================
# MANOIR POKÉMON — CRAMOIS'ÎLE
# Dresseurs répartis sur 1F, 2F, 3F, B1F (Clé Secrète)
# ==============================================================================

def init_manoir_pokemon():
    logging.info("[*] Manoir Pokémon (1F / 2F / 3F / B1F)...")

    # ── 1F — Hall en ruines ───────────────────────────────────────────────────
    create_npc_trainer(
        username='Burglar Simon',
        trainer_type='trainer',
        location='Manoir Pokémon-1',
        team_data=[
            {'species': get_pokemon('Growlithe'), 'level': 40, 'moves': get_moves(['Bite', 'Ember', 'Flamethrower'])},
            {'species': get_pokemon('Ponyta'),    'level': 40, 'moves': get_moves(['Ember', 'Fire Spin', 'Stomp'])},
        ],
        intro_text="Ce manoir recèle des trésors... et je les veux!"
    )
    create_npc_trainer(
        username='Juggler Horton',
        trainer_type='trainer',
        location='Manoir Pokémon-1',
        team_data=[
            {'species': get_pokemon('Koffing'), 'level': 39, 'moves': get_moves(['Smog', 'Sludge', 'Explosion'])},
            {'species': get_pokemon('Koffing'), 'level': 39, 'moves': get_moves(['Smog', 'Sludge', 'Explosion'])},
            {'species': get_pokemon('Weezing'), 'level': 41, 'moves': get_moves(['Smog', 'Sludge', 'Explosion'])},
        ],
        intro_text="Les ruines du manoir sont mon terrain de jeu!"
    )

    # ── 2F — Bibliothèque (journaux sur Mew) ─────────────────────────────────
    create_npc_trainer(
        username='Scientist Beau',
        trainer_type='trainer',
        location='Manoir Pokémon-2',
        team_data=[
            {'species': get_pokemon('Magmar'),   'level': 42, 'moves': get_moves(['Ember', 'Fire Punch', 'Smog'])},
            {'species': get_pokemon('Electrode'), 'level': 40, 'moves': get_moves(['Tackle', 'Screech', 'Self-Destruct'])},
        ],
        intro_text="Les journaux de recherche sur Mew sont fascinants!"
    )
    create_npc_trainer(
        username='Burglar Lewis',
        trainer_type='trainer',
        location='Manoir Pokémon-2',
        team_data=[
            {'species': get_pokemon('Growlithe'), 'level': 41, 'moves': get_moves(['Bite', 'Ember', 'Flamethrower'])},
            {'species': get_pokemon('Magmar'),    'level': 43, 'moves': get_moves(['Fire Punch', 'Confuse Ray', 'Flamethrower'])},
        ],
        intro_text="Les vieux grimoires ici valent une fortune!"
    )

    # ── 3F — Couloirs sombres ─────────────────────────────────────────────────
    create_npc_trainer(
        username='Scientist Foster',
        trainer_type='trainer',
        location='Manoir Pokémon-3',
        team_data=[
            {'species': get_pokemon('Grimer'), 'level': 41, 'moves': get_moves(['Pound', 'Sludge', 'Minimize'])},
            {'species': get_pokemon('Muk'),    'level': 43, 'moves': get_moves(['Pound', 'Sludge', 'Disable'])},
        ],
        intro_text="Mes Pokémon Poison s'épanouissent dans ces couloirs putrides!"
    )
    create_npc_trainer(
        username='Burglar Ramon',
        trainer_type='trainer',
        location='Manoir Pokémon-3',
        team_data=[
            {'species': get_pokemon('Koffing'), 'level': 40, 'moves': get_moves(['Smog', 'Sludge', 'Smokescreen'])},
            {'species': get_pokemon('Ponyta'),  'level': 40, 'moves': get_moves(['Ember', 'Fire Spin', 'Stomp'])},
            {'species': get_pokemon('Magmar'),  'level': 42, 'moves': get_moves(['Ember', 'Fire Punch', 'Confuse Ray'])},
        ],
        intro_text="Personne ne ressort de ce couloir!"
    )

    # ── B1F — Sous-sol (Clé Secrète) ─────────────────────────────────────────
    create_npc_trainer(
        username='Scientist Jordan',
        trainer_type='trainer',
        location='Manoir Pokémon-4',
        team_data=[
            {'species': get_pokemon('Ditto'),  'level': 43, 'moves': get_moves(['Transform'])},
            {'species': get_pokemon('Ditto'),  'level': 43, 'moves': get_moves(['Transform'])},
        ],
        intro_text="Mes Metamorphe peuvent imiter n'importe quel Pokémon... y compris les tiens!"
    )
    create_npc_trainer(
        username='Burglar Arnie',
        trainer_type='trainer',
        location='Manoir Pokémon-4',
        team_data=[
            {'species': get_pokemon('Magmar'), 'level': 44, 'moves': get_moves(['Fire Punch', 'Flamethrower', 'Confuse Ray', 'Smokescreen'])},
            {'species': get_pokemon('Muk'),    'level': 42, 'moves': get_moves(['Sludge', 'Pound', 'Disable'])},
        ],
        intro_text="La Clé Secrète est quelque part ici — et tu ne la trouveras pas!"
    )


# ==============================================================================
# CAVE TAUPIQUEUR
# Tunnel unique entre Carmin sur Mer et Route 2 (CS01 Coupe requise)
# Aucun combat obligatoire (galerie ouverte à sens unique)
# ==============================================================================

def init_cave_taupiqueur():
    logging.info("[*] Cave Taupiqueur...")

    create_npc_trainer(
        username='Hiker Alan',
        trainer_type='trainer',
        location='Cave Taupiqueur-1',
        team_data=[
            {'species': get_pokemon('Diglett'), 'level': 19, 'moves': get_moves(['Scratch', 'Growl', 'Dig'])},
            {'species': get_pokemon('Diglett'), 'level': 19, 'moves': get_moves(['Scratch', 'Growl', 'Dig'])},
            {'species': get_pokemon('Dugtrio'), 'level': 22, 'moves': get_moves(['Scratch', 'Growl', 'Dig', 'Slash'])},
        ],
        intro_text="Ce tunnel appartient aux Taupiqueur et à moi!"
    )
    create_npc_trainer(
        username='Rocker Lenny',
        trainer_type='trainer',
        location='Cave Taupiqueur-1',
        team_data=[
            {'species': get_pokemon('Diglett'), 'level': 18, 'moves': get_moves(['Scratch', 'Sand Attack', 'Dig'])},
            {'species': get_pokemon('Geodude'), 'level': 18, 'moves': get_moves(['Tackle', 'Defense Curl', 'Rock Throw'])},
        ],
        intro_text="Rock and roll sous la terre!"
    )


# ==============================================================================
# ÎLES ÉCUME
# ==============================================================================

def init_seafoam():
    logging.info("[*] Îles Écume (B1F → B4F)...")

    # ── B1F ──────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Swimmer Bryce',
        trainer_type='trainer',
        location='Îles Écume-1',
        team_data=[
            {'species': get_pokemon('Shellder'), 'level': 38, 'moves': get_moves(['Tackle', 'Withdraw', 'Ice Beam'])},
            {'species': get_pokemon('Cloyster'), 'level': 38, 'moves': get_moves(['Aurora Beam', 'Ice Beam'])},
        ],
        intro_text="L'eau glacée renforce!"
    )
    create_npc_trainer(
        username='Swimmer Anya',
        trainer_type='trainer',
        location='Îles Écume-1',
        team_data=[
            {'species': get_pokemon('Dewgong'), 'level': 39, 'moves': get_moves(['Headbutt', 'Aurora Beam', 'Ice Beam'])},
            {'species': get_pokemon('Cloyster'), 'level': 39, 'moves': get_moves(['Aurora Beam', 'Ice Beam', 'Spikes'])},
        ],
        intro_text="Les eaux glacées des Îles Écume me galvanisent!"
    )

    # ── B2F ──────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Juggler Nate',
        trainer_type='trainer',
        location='Îles Écume-2',
        team_data=[
            {'species': get_pokemon('Jynx'), 'level': 40, 'moves': get_moves(['Pound', 'Lovely Kiss', 'Ice Beam', 'Psychic'])},
        ],
        intro_text="La glace et le mystère... c'est mon style!"
    )
    create_npc_trainer(
        username='Swimmer Darrin',
        trainer_type='trainer',
        location='Îles Écume-2',
        team_data=[
            {'species': get_pokemon('Staryu'),  'level': 39, 'moves': get_moves(['Water Gun', 'Rapid Spin', 'Ice Beam'])},
            {'species': get_pokemon('Golduck'), 'level': 39, 'moves': get_moves(['Scratch', 'Confusion', 'Hydro Pump'])},
        ],
        intro_text="Les courants souterrains sont dévastateurs!"
    )

    # ── B3F ──────────────────────────────────────────────────────────────────
    create_npc_trainer(
        username='Swimmer Melissa',
        trainer_type='trainer',
        location='Îles Écume-3',
        team_data=[
            {'species': get_pokemon('Dewgong'),  'level': 41, 'moves': get_moves(['Headbutt', 'Aurora Beam', 'Ice Beam', 'Rest'])},
            {'species': get_pokemon('Lapras'),   'level': 40, 'moves': get_moves(['Body Slam', 'Ice Beam', 'Confuse Ray'])},
        ],
        intro_text="Artikodin rôde quelque part dans ces grottes!"
    )
    create_npc_trainer(
        username='Juggler Linn',
        trainer_type='trainer',
        location='Îles Écume-3',
        team_data=[
            {'species': get_pokemon('Jynx'),  'level': 41, 'moves': get_moves(['Ice Punch', 'Lovely Kiss', 'Psychic'])},
            {'species': get_pokemon('Jynx'),  'level': 41, 'moves': get_moves(['Ice Punch', 'Lovely Kiss', 'Psychic'])},
        ],
        intro_text="Mes Lippoutou dansent sur la glace... puis attaquent!"
    )

    # ── B4F — Chambre d'Artikodin ─────────────────────────────────────────────
    create_npc_trainer(
        username='Swimmer Gerald',
        trainer_type='trainer',
        location='Îles Écume-4',
        team_data=[
            {'species': get_pokemon('Cloyster'),  'level': 43, 'moves': get_moves(['Ice Beam', 'Aurora Beam', 'Spikes'])},
            {'species': get_pokemon('Tentacruel'),'level': 43, 'moves': get_moves(['Acid', 'Hydro Pump', 'Barrier'])},
        ],
        intro_text="Seuls les plus endurcis atteignent ces profondeurs!"
    )


# ==============================================================================
# CHEMIN DE LA VICTOIRE
# ==============================================================================

def init_victory_road():
    logging.info("[*] Chemin de la Victoire...")

    create_npc_trainer(
        username='Black Belt Atsushi',
        trainer_type='trainer',
        location='Chemin de la Victoire-1',
        team_data=[
            {'species': get_pokemon('Machop'), 'level': 40, 'moves': get_moves(['Low Kick', 'Karate Chop', 'Submission'])},
            {'species': get_pokemon('Machoke'), 'level': 40, 'moves': get_moves(['Low Kick', 'Karate Chop', 'Submission'])},
        ],
        intro_text="Seuls les forts passent!"
    )
    create_npc_trainer(
        username='Cool Trainer Samuel',
        trainer_type='trainer',
        location='Chemin de la Victoire-1',
        team_data=[
            {'species': get_pokemon('Sandslash'), 'level': 37, 'moves': get_moves(['Scratch', 'Slash', 'Sand Attack'])},
            {'species': get_pokemon('Sandslash'), 'level': 37, 'moves': get_moves(['Scratch', 'Slash', 'Sand Attack'])},
            {'species': get_pokemon('Rhyhorn'), 'level': 38, 'moves': get_moves(['Horn Attack', 'Stomp'])},
        ],
        intro_text="Je m'entraîne ici depuis des mois!"
    )
    create_npc_trainer(
        username='Cool Trainer Caroline',
        trainer_type='trainer',
        location='Chemin de la Victoire-1',
        team_data=[
            {'species': get_pokemon('Haunter'), 'level': 43, 'moves': get_moves(['Night Shade', 'Hypnosis', 'Confuse Ray'])},
            {'species': get_pokemon('Kadabra'), 'level': 43, 'moves': get_moves(['Psybeam', 'Recover', 'Psychic'])},
        ],
        intro_text="Seuls les meilleurs atteignent le Plateau Indigo!"
    )
    create_npc_trainer(
        username='Juggler Nelson',
        trainer_type='trainer',
        location='Chemin de la Victoire-2',
        team_data=[
            {'species': get_pokemon('Drowzee'), 'level': 41, 'moves': get_moves(['Pound', 'Hypnosis', 'Psychic'])},
            {'species': get_pokemon('Hypno'), 'level': 41, 'moves': get_moves(['Pound', 'Hypnosis', 'Psychic'])},
            {'species': get_pokemon('Kadabra'), 'level': 41, 'moves': get_moves(['Teleport', 'Kinesis', 'Psybeam'])},
        ],
        intro_text="La psychologie est tout!"
    )
    create_npc_trainer(
        username='Pokemaniac Bernard',
        trainer_type='trainer',
        location='Chemin de la Victoire-2',
        team_data=[
            {'species': get_pokemon('Slowbro'), 'level': 44, 'moves': get_moves(['Confusion', 'Psychic', 'Amnesia'])},
            {'species': get_pokemon('Kangaskhan'), 'level': 44, 'moves': get_moves(['Headbutt', 'Dizzy Punch', 'Body Slam'])},
        ],
        intro_text="J'accumule les Pokémon rares depuis des années!"
    )
    create_npc_trainer(
        username='Tamer Vincent',
        trainer_type='trainer',
        location='Chemin de la Victoire-2',
        team_data=[
            {'species': get_pokemon('Persian'), 'level': 44, 'moves': get_moves(['Scratch', 'Growl', 'Bite', 'Slash'])},
            {'species': get_pokemon('Golduck'), 'level': 44, 'moves': get_moves(['Scratch', 'Confusion', 'Hydro Pump'])},
        ],
        intro_text="J'ai dompté les plus féroces!"
    )
    create_npc_trainer(
        username='Black Belt Takashi',
        trainer_type='trainer',
        location='Chemin de la Victoire-3',
        team_data=[
            {'species': get_pokemon('Primeape'), 'level': 43, 'moves': get_moves(['Karate Chop', 'Cross Chop', 'Fury Swipes'])},
            {'species': get_pokemon('Machamp'), 'level': 45, 'moves': get_moves(['Karate Chop', 'Cross Chop', 'Submission'])},
        ],
        intro_text="Le combat forge l'âme!"
    )


# ==============================================================================
# FONCTION PRINCIPALE
# ==============================================================================

def run_complete_npc_initialization():
    """Lance l'initialisation complète de tous les NPCs de Kanto."""

    logging.info("=" * 70)
    logging.info("INITIALISATION COMPLÈTE DES NPCS DE KANTO")
    logging.info("Source : Bulbapedia — FireRed / LeafGreen")
    logging.info("=" * 70)

    try:
        init_route_1()
        init_foret_de_jade()
        init_route_2()
        init_route_3()
        init_mont_selenite()       # Miguel & Grunt obligatoires
        init_route_4()
        init_route_24()            # Pont Cerclef — 6 combats obligatoires
        init_route_25()
        init_ss_anne()
        init_route_5()
        init_route_6()
        init_tunnel_roche()
        init_route_9()
        init_route_10()
        init_route_11()
        init_route_7()
        init_route_8()
        init_celadon_city()        # Archer obligatoire
        init_lavender_town()       # Jesse & James obligatoires
        init_saffron_city()        # Giovanni Shadow obligatoire
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
        init_safari_zone()
        init_manoir_pokemon()
        init_cave_taupiqueur()
        init_seafoam()
        init_victory_road()

        required_count = Trainer.objects.filter(
            trainer_type='trainer', is_battle_required=True
        ).count()
        total = Trainer.objects.filter(trainer_type='trainer').count()

        logging.info("=" * 70)
        logging.info(f"[✓] {total} dresseurs NPCs créés/vérifiés")
        logging.info(f"[✓] dont {required_count} combats OBLIGATOIRES (is_battle_required=True)")
        logging.info("=" * 70)

    except Exception as e:
        logging.error(f"[✗] ERREUR: {e}")
        raise


if __name__ == '__main__':
    run_complete_npc_initialization()