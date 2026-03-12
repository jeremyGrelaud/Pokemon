#!/usr/bin/python3
"""
initTMsAndCSs.py — Initialisation des CT (TM) et CS (HM) Gen 9 (Scarlet/Violet)

Ce script :
  1. Crée les items TM et CS dans la base.
  2. Enregistre dans PokemonLearnableMove les compatibilités par espèce
     (learn_method='tm') pour les 151 Pokémon de Kanto.

Source : pokemondb.net — learnsets Scarlet/Violet (Gen 9)

ORDRE D'EXÉCUTION :
    initMovesGen9.py  →  initLearnableMovesGen9.py  →  InitTMsandCS.py
"""

import logging
from myPokemonApp.models import Item, PokemonMove, Pokemon, PokemonLearnableMove

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================================================
# 1. DÉFINITION DES CT (TM) — Gen 9 Scarlet/Violet
#    Format : (numéro, nom_item, nom_move_db, prix)
#    Seules les CT pertinentes pour les 151 Pokémon de Kanto sont listées.
# ==============================================================================

TM_DATA = [
    # num   nom CT               move en base              prix
    (1,   "CT001 Poing-Feu",     "Fire Punch",              3000),
    (2,   "CT002 Poing-Éclair",  "Thunder Punch",           3000),
    (3,   "CT003 Poing-Glace",   "Ice Punch",               3000),
    (4,   "CT004 Torgnoles",     "Mega Punch",              3000),
    (5,   "CT005 Jackpot",       "Pay Day",                 2000),
    (6,   "CT006 Tranche",       "Cut",                     1000),
    (7,   "CT007 Crocs Éclair",  "Thunder Fang",            2500),
    (8,   "CT008 Crocs de Feu",  "Fire Fang",               2500),
    (9,   "CT009 Crocs Givre",   "Ice Fang",                2500),
    (10,  "CT010 Méga-Sabot",    "Mega Kick",               3000),
    (11,  "CT011 Vibrobscur",    "Bulldoze",                2000),
    (12,  "CT012 Choc Mental",   "Psychic Fangs",           3000),
    (13,  "CT013 Jackpot",       "Thief",                   2000),
    (14,  "CT014 Jackpot",       "Thunder Wave",            1500),
    (15,  "CT015 Jackpot",       "Dig",                     2000),
    (16,  "CT016 Jackpot",       "Psybeam",                 2000),
    (17,  "CT017 Jackpot",       "Air Cutter",              2000),
    (18,  "CT018 Jackpot",       "Roost",                   2500),
    (19,  "CT019 Jackpot",       "Telekinesis",             2000),
    (20,  "CT020 Jackpot",       "Tri Attack",              3000),
    (21,  "CT021 Jackpot",       "Bounce",                  2500),
    (22,  "CT022 Jackpot",       "Rock Slide",              2500),
    (23,  "CT023 Jackpot",       "Charge Beam",             2500),
    (24,  "CT024 Jackpot",       "Snore",                   1500),
    (25,  "CT025 Jackpot",       "Protect",                 2000),
    (26,  "CT026 Jackpot",       "Scary Face",              1000),
    (27,  "CT027 Jackpot",       "Icy Wind",                2000),
    (28,  "CT028 Jackpot",       "Brick Break",             3000),
    (29,  "CT029 Jackpot",       "Hex",                     2000),
    (30,  "CT030 Jackpot",       "Snarl",                   2000),
    (31,  "CT031 Jackpot",       "Metal Sound",             1500),
    (32,  "CT032 Jackpot",       "Swift",                   2000),
    (33,  "CT033 Jackpot",       "Magical Leaf",            2000),
    (34,  "CT034 Jackpot",       "Icy Wind",                2000),
    (35,  "CT035 Jackpot",       "Mud Shot",                2000),
    (36,  "CT036 Jackpot",       "Rock Tomb",               2000),
    (37,  "CT037 Jackpot",       "Draining Kiss",           2000),
    (38,  "CT038 Jackpot",       "Flame Charge",            2000),
    (39,  "CT039 Jackpot",       "Facade",                  2500),
    (40,  "CT040 Jackpot",       "Air Slash",               3000),
    (41,  "CT041 Jackpot",       "Amnesia",                 2000),
    (42,  "CT042 Jackpot",       "Night Shade",             2000),
    (43,  "CT043 Jackpot",       "Fling",                   2000),
    (44,  "CT044 Jackpot",       "Imprison",                2000),
    (45,  "CT045 Jackpot",       "Solar Beam",              5000),
    (46,  "CT046 Jackpot",       "Avalanche",               2500),
    (47,  "CT047 Jackpot",       "Endure",                  2000),
    (48,  "CT048 Jackpot",       "Hyper Voice",             4000),
    (49,  "CT049 Jackpot",       "Sunny Day",               3000),
    (50,  "CT050 Jackpot",       "Rain Dance",              3000),
    (51,  "CT051 Jackpot",       "Sandstorm",               3000),
    (52,  "CT052 Jackpot",       "Gyro Ball",               3000),
    (53,  "CT053 Jackpot",       "Mud Slap",                1000),
    (54,  "CT054 Jackpot",       "Rock Blast",              2500),
    (55,  "CT055 Jackpot",       "Brine",                   2500),
    (56,  "CT056 Jackpot",       "Bullet Seed",             2500),
    (57,  "CT057 Jackpot",       "Swords Dance",            3000),
    (58,  "CT058 Jackpot",       "Brick Break",             3000),
    (59,  "CT059 Jackpot",       "Zen Headbutt",            3000),
    (60,  "CT060 Jackpot",       "U-turn",                  3000),
    (61,  "CT061 Jackpot",       "Shadow Claw",             3000),
    (62,  "CT062 Jackpot",       "Foul Play",               3000),
    (63,  "CT063 Jackpot",       "Psychic",                 5000),
    (64,  "CT064 Jackpot",       "Bulk Up",                 3000),
    (65,  "CT065 Jackpot",       "Ice Spinner",             3000),
    (66,  "CT066 Jackpot",       "Body Slam",               3000),
    (67,  "CT067 Jackpot",       "Fire Blast",              5000),
    (68,  "CT068 Jackpot",       "Thunder",                 5000),
    (69,  "CT069 Jackpot",       "Ice Beam",                5000),
    (70,  "CT070 Jackpot",       "Flash",                   1000),
    (71,  "CT071 Jackpot",       "Seed Bomb",               3000),
    (72,  "CT072 Jackpot",       "Electro Ball",            3000),
    (73,  "CT073 Jackpot",       "Drain Punch",             3000),
    (74,  "CT074 Jackpot",       "Reflect",                 2000),
    (75,  "CT075 Jackpot",       "Light Screen",            2000),
    (76,  "CT076 Jackpot",       "Rock Polish",             2000),
    (77,  "CT077 Jackpot",       "Waterfall",               3000),
    (78,  "CT078 Jackpot",       "Surf",                    5000),
    (79,  "CT079 Jackpot",       "Earthquake",              5000),
    (80,  "CT080 Jackpot",       "Volt Switch",             3000),
    (81,  "CT081 Jackpot",       "Bulldoze",                2500),
    (82,  "CT082 Jackpot",       "Flamethrower",            5000),
    (83,  "CT083 Jackpot",       "Poison Jab",              3000),
    (84,  "CT084 Jackpot",       "Stomping Tantrum",        3000),
    (85,  "CT085 Jackpot",       "Rest",                    2000),
    (86,  "CT086 Jackpot",       "Rock Tomb",               2000),
    (87,  "CT087 Jackpot",       "Taunt",                   2000),
    (88,  "CT088 Jackpot",       "Sludge Bomb",             4000),
    (89,  "CT089 Jackpot",       "Body Press",              3000),
    (90,  "CT090 Jackpot",       "Sleep Talk",              2000),
    (91,  "CT091 Jackpot",       "Swift",                   2000),
    (92,  "CT092 Jackpot",       "Imprison",                2000),
    (93,  "CT093 Jackpot",       "Flash Cannon",            4000),
    (94,  "CT094 Jackpot",       "Dark Pulse",              4000),
    (95,  "CT095 Jackpot",       "Leech Life",              3000),
    (96,  "CT096 Jackpot",       "Eerie Impulse",           2500),
    (97,  "CT097 Jackpot",       "Fly",                     3000),
    (98,  "CT098 Jackpot",       "Aerial Ace",              2500),
    (99,  "CT099 Jackpot",       "Hyper Beam",              7500),
    (100, "CT100 Jackpot",       "Dragon Claw",             4000),
    (101, "CT101 Jackpot",       "Pounce",                  2000),
    (102, "CT102 Jackpot",       "Gunk Shot",               4000),
    (103, "CT103 Jackpot",       "Substitute",              3000),
    (104, "CT104 Jackpot",       "Iron Head",               4000),
    (105, "CT105 Jackpot",       "X-Scissor",               3000),
    (106, "CT106 Jackpot",       "Trailblaze",              2000),
    (107, "CT107 Jackpot",       "Will-O-Wisp",             2500),
    (108, "CT108 Jackpot",       "Crunch",                  3000),
    (109, "CT109 Jackpot",       "Trick",                   3000),
    (110, "CT110 Jackpot",       "Liquidation",             4000),
    (111, "CT111 Jackpot",       "Giga Impact",             7500),
    (112, "CT112 Jackpot",       "Aura Sphere",             4000),
    (113, "CT113 Jackpot",       "Tailwind",                2500),
    (114, "CT114 Jackpot",       "Shadow Ball",             4000),
    (115, "CT115 Jackpot",       "Dragon Pulse",            4000),
    (116, "CT116 Jackpot",       "Stealth Rock",            2500),
    (117, "CT117 Jackpot",       "Gravity",                 2500),
    (118, "CT118 Jackpot",       "Heat Wave",               4000),
    (119, "CT119 Jackpot",       "Energy Ball",             4000),
    (120, "CT120 Jackpot",       "Scald",                   4000),
    (121, "CT121 Jackpot",       "Hurricane",               5000),
    (122, "CT122 Jackpot",       "Encore",                  2000),
    (123, "CT123 Jackpot",       "Surf",                    5000),
    (124, "CT124 Jackpot",       "Ice Spinner",             3000),
    (125, "CT125 Jackpot",       "Stone Edge",              5000),
    (126, "CT126 Jackpot",       "Thunderbolt",             5000),
    (127, "CT127 Jackpot",       "Glare",                   2000),
    (128, "CT128 Jackpot",       "Amnesia",                 2000),
    (129, "CT129 Jackpot",       "Work Up",                 2000),
    (130, "CT130 Jackpot",       "Helping Hand",            2000),
    (131, "CT131 Jackpot",       "Stored Power",            3000),
    (132, "CT132 Jackpot",       "Baton Pass",              3000),
    (133, "CT133 Jackpot",       "Slash",                   2500),
    (134, "CT134 Jackpot",       "Reversal",                3000),
    (135, "CT135 Jackpot",       "Ice Punch",               3000),
    (136, "CT136 Jackpot",       "Fire Punch",              3000),
    (137, "CT137 Jackpot",       "Hyper Drill",             4000),
    (138, "CT138 Jackpot",       "Confide",                 1500),
    (139, "CT139 Jackpot",       "Misty Terrain",           3000),
    (140, "CT140 Jackpot",       "Nasty Plot",              3000),
    (141, "CT141 Jackpot",       "Fire Spin",               2500),
    (142, "CT142 Jackpot",       "Mega Drain",              2000),
    (143, "CT143 Jackpot",       "Blizzard",                5000),
    (144, "CT144 Jackpot",       "Dragon Breath",           3000),
    (145, "CT145 Jackpot",       "Fly",                     3000),
    (146, "CT146 Jackpot",       "Dig",                     2000),
    (147, "CT147 Jackpot",       "Sludge Wave",             4000),
    (148, "CT148 Jackpot",       "Confuse Ray",             1500),
    (149, "CT149 Jackpot",       "Tri Attack",              3000),
    (150, "CT150 Jackpot",       "Stone Edge",              5000),
    (151, "CT151 Jackpot",       "Hydro Pump",              5000),
    (152, "CT152 Jackpot",       "Giga Drain",              3000),
    (153, "CT153 Jackpot",       "Overheat",                5000),
    (154, "CT154 Jackpot",       "Volt Tackle",             5000),
    (155, "CT155 Jackpot",       "Leech Seed",              2000),
    (156, "CT156 Jackpot",       "Outrage",                 5000),
    (157, "CT157 Jackpot",       "Thunderclap",             4000),
    (158, "CT158 Jackpot",       "Bind",                    1500),
    (159, "CT159 Jackpot",       "Grass Knot",              3000),
    (160, "CT160 Jackpot",       "Acid Spray",              2000),
    (161, "CT161 Jackpot",       "Bug Bite",                2000),
    (162, "CT162 Jackpot",       "Hyper Voice",             4000),
    (163, "CT163 Jackpot",       "Disarming Voice",         2000),
    (164, "CT164 Jackpot",       "Knock Off",               2500),
    (165, "CT165 Jackpot",       "Dazzling Gleam",          4000),
    (166, "CT166 Jackpot",       "Steamroller",             2500),
    (167, "CT167 Jackpot",       "Low Sweep",               2500),
    (168, "CT168 Jackpot",       "Flatter",                 1500),
    (169, "CT169 Jackpot",       "Spite",                   1500),
    (170, "CT170 Jackpot",       "Sky Attack",              5000),
    (171, "CT171 Jackpot",       "Power Gem",               4000),
    (172, "CT172 Jackpot",       "Headbutt",                2500),
    (173, "CT173 Jackpot",       "Aerial Ace",              2500),
    (174, "CT174 Jackpot",       "Haze",                    2000),
    (175, "CT175 Jackpot",       "Agility",                 3000),
    (176, "CT176 Jackpot",       "Dragon Dance",            3000),
    (177, "CT177 Jackpot",       "Fake Out",                3000),
    (178, "CT178 Jackpot",       "Focus Blast",             5000),
    (179, "CT179 Jackpot",       "Smack Down",              2500),
    (180, "CT180 Jackpot",       "Lunge",                   3000),
    (181, "CT181 Jackpot",       "Petal Blizzard",          4000),
    (182, "CT182 Jackpot",       "Bug Buzz",                4000),
    (183, "CT183 Jackpot",       "Mud Bomb",                2000),
    (184, "CT184 Jackpot",       "Dragon Rush",             4000),
    (185, "CT185 Jackpot",       "Chilling Water",          2000),
    (186, "CT186 Jackpot",       "Spit Up",                 2000),
    (187, "CT187 Jackpot",       "Stockpile",               2000),
    (188, "CT188 Jackpot",       "Swallow",                 2000),
    (189, "CT189 Jackpot",       "Recycle",                 2500),
    (190, "CT190 Jackpot",       "Lash Out",                3000),
    (191, "CT191 Jackpot",       "Uproar",                  3000),
    (192, "CT192 Jackpot",       "Focus Energy",            1500),
    (193, "CT193 Jackpot",       "Foul Play",               3000),
    (194, "CT194 Jackpot",       "Icicle Spear",            3000),
    (195, "CT195 Jackpot",       "Mystical Fire",           4000),
    (196, "CT196 Jackpot",       "Hyper Drill",             4000),
    (197, "CT197 Jackpot",       "Power Whip",              4000),
    (198, "CT198 Jackpot",       "Nuzzle",                  2000),
    (199, "CT199 Jackpot",       "Meteor Mash",             5000),
    (200, "CT200 Jackpot",       "Flash Cannon",            4000),
]

# ==============================================================================
# 2. CS (HM) — Gen 9
#    Les CS sont réutilisables et souvent nécessaires pour la progression.
# ==============================================================================

CS_DATA = [
    # num   nom CS         move en base    prix
    (1,  "CS01 Coupe",    "Cut",           0),
    (2,  "CS02 Vol",      "Fly",           0),
    (3,  "CS03 Surf",     "Surf",          0),
    (4,  "CS04 Force",    "Strength",      0),
    (5,  "CS05 Flash",    "Flash",         0),
    (6,  "CS06 Cascade",  "Waterfall",     0),
]

# ==============================================================================
# 3. COMPATIBILITÉ TM/CS PAR POKÉMON (Gen 9 — Scarlet/Violet)
#
#    Format : { 'NomPokemon': ['NomMove', ...] }
#
#    Source : pokemondb.net/pokedex/<pokemon>/moves/9
#    Seuls les 151 Pokémon de Kanto + leurs moves accessibles via TM en Gen 9.
# ==============================================================================

TM_LEARNSETS_GEN9 = {
    "Bulbasaur": [
        "Swords Dance","Toxic","Protect","Sunny Day","Solar Beam","Rest","Endure",
        "Facade","Giga Drain","Leech Seed","Magical Leaf","Seed Bomb","Energy Ball",
        "Sludge Bomb","Venoshock","Work Up","Grass Knot","Substitute","Power Whip",
        "Petal Blizzard","Hyper Beam","Giga Impact","Trailblaze",
    ],
    "Ivysaur": [
        "Swords Dance","Toxic","Protect","Sunny Day","Solar Beam","Rest","Endure",
        "Facade","Giga Drain","Leech Seed","Magical Leaf","Seed Bomb","Energy Ball",
        "Sludge Bomb","Venoshock","Work Up","Grass Knot","Substitute","Power Whip",
        "Petal Blizzard","Hyper Beam","Giga Impact","Trailblaze",
    ],
    "Venusaur": [
        "Swords Dance","Toxic","Protect","Sunny Day","Solar Beam","Rest","Endure",
        "Facade","Giga Drain","Leech Seed","Magical Leaf","Seed Bomb","Energy Ball",
        "Sludge Bomb","Venoshock","Work Up","Grass Knot","Substitute","Power Whip",
        "Petal Blizzard","Hyper Beam","Giga Impact","Trailblaze","Earthquake",
    ],
    "Charmander": [
        "Swords Dance","Toxic","Protect","Sunny Day","Solar Beam","Rest","Endure",
        "Facade","Fire Spin","Flamethrower","Fire Blast","Slash","Dragon Claw",
        "Shadow Claw","Aerial Ace","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Flame Charge","Dragon Breath","Scary Face","Dragon Dance","Dragon Rush",
    ],
    "Charmeleon": [
        "Swords Dance","Toxic","Protect","Sunny Day","Solar Beam","Rest","Endure",
        "Facade","Fire Spin","Flamethrower","Fire Blast","Slash","Dragon Claw",
        "Shadow Claw","Aerial Ace","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Flame Charge","Dragon Breath","Scary Face","Dragon Dance","Dragon Rush",
    ],
    "Charizard": [
        "Swords Dance","Toxic","Protect","Sunny Day","Solar Beam","Rest","Endure",
        "Facade","Fire Spin","Flamethrower","Fire Blast","Slash","Dragon Claw",
        "Shadow Claw","Aerial Ace","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Flame Charge","Dragon Breath","Scary Face","Dragon Dance","Dragon Rush",
        "Earthquake","Air Slash","Hurricane","Fly","Heat Wave","Focus Blast",
    ],
    "Squirtle": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Waterfall",
        "Brine","Scald","Ice Beam","Blizzard","Flash Cannon","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Aqua Tail","Chilling Water","Icy Wind",
    ],
    "Wartortle": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Waterfall",
        "Brine","Scald","Ice Beam","Blizzard","Flash Cannon","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Aqua Tail","Chilling Water","Icy Wind",
    ],
    "Blastoise": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Waterfall",
        "Brine","Scald","Ice Beam","Blizzard","Flash Cannon","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Aqua Tail","Chilling Water","Icy Wind",
        "Earthquake","Hydro Pump","Focus Blast","Aura Sphere",
    ],
    "Caterpie":  [],
    "Metapod":   [],
    "Butterfree": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Aerial Ace","Air Slash",
        "Bug Buzz","Energy Ball","Psychic","Shadow Ball","Hurricane","Work Up",
        "Substitute","Hyper Beam","Giga Impact","Tailwind","Sleep Powder","Quiver Dance",
    ],
    "Weedle":    [],
    "Kakuna":    [],
    "Beedrill": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Poison Jab","Swords Dance",
        "X-Scissor","Brick Break","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Bug Bite","Knock Off","Drill Run",
    ],
    "Pidgey": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","Fly",
        "Work Up","Substitute","Hyper Beam","Giga Impact","Tailwind","Brave Bird",
    ],
    "Pidgeotto": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","Fly",
        "Work Up","Substitute","Hyper Beam","Giga Impact","Tailwind","Brave Bird","Hurricane",
    ],
    "Pidgeot": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","Fly",
        "Work Up","Substitute","Hyper Beam","Giga Impact","Tailwind","Brave Bird",
        "Hurricane","Heat Wave","Sky Attack",
    ],
    "Rattata": [
        "Toxic","Protect","Rest","Endure","Facade","Crunch","Thunder Wave","Thunderbolt",
        "Shadow Claw","Work Up","Substitute","Hyper Beam","Giga Impact","Sucker Punch",
    ],
    "Raticate": [
        "Toxic","Protect","Rest","Endure","Facade","Crunch","Thunder Wave","Thunderbolt",
        "Shadow Claw","Work Up","Substitute","Hyper Beam","Giga Impact","Sucker Punch",
        "Blizzard","Earthquake","Fire Blast","Hyper Fang",
    ],
    "Spearow": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","Fly",
        "Work Up","Substitute","Hyper Beam","Giga Impact","Tailwind","Brave Bird",
        "Drill Run",
    ],
    "Fearow": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","Fly",
        "Work Up","Substitute","Hyper Beam","Giga Impact","Tailwind","Brave Bird",
        "Drill Run","Sky Attack",
    ],
    "Ekans": [
        "Toxic","Protect","Rest","Endure","Facade","Crunch","Earthquake","Glare",
        "Sludge Bomb","Poison Jab","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Gastro Acid","Coil",
    ],
    "Arbok": [
        "Toxic","Protect","Rest","Endure","Facade","Crunch","Earthquake","Glare",
        "Sludge Bomb","Poison Jab","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Gastro Acid","Coil","Gunk Shot",
    ],
    "Pikachu": [
        "Toxic","Thunder Wave","Protect","Rest","Endure","Facade","Thunderbolt","Thunder",
        "Volt Switch","Electro Ball","Nuzzle","Iron Tail","Slam","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Flash","Charge Beam","Wild Charge","Brick Break",
        "Surf","Body Slam",
    ],
    "Raichu": [
        "Toxic","Thunder Wave","Protect","Rest","Endure","Facade","Thunderbolt","Thunder",
        "Volt Switch","Electro Ball","Nuzzle","Iron Tail","Slam","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Flash","Charge Beam","Wild Charge","Brick Break",
        "Surf","Body Slam","Earthquake","Focus Blast","Thunder Punch",
    ],
    "Sandshrew": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Swords Dance","Rock Slide",
        "Rock Tomb","Slash","Dig","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Iron Head","Rollout","Knock Off","Sand Tomb",
    ],
    "Sandslash": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Swords Dance","Rock Slide",
        "Rock Tomb","Slash","Dig","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Iron Head","Rollout","Knock Off","Sand Tomb","Stone Edge","Night Slash",
    ],
    "Nidoran-F": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Swords Dance","Poison Jab",
        "Sludge Bomb","Work Up","Substitute","Hyper Beam","Giga Impact","Ice Beam",
        "Blizzard","Thunderbolt","Thunder","Surf","Flamethrower","Fire Blast",
    ],
    "Nidorina": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Swords Dance","Poison Jab",
        "Sludge Bomb","Work Up","Substitute","Hyper Beam","Giga Impact","Ice Beam",
        "Blizzard","Thunderbolt","Thunder","Surf","Flamethrower","Fire Blast",
    ],
    "Nidoqueen": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Swords Dance","Poison Jab",
        "Sludge Bomb","Work Up","Substitute","Hyper Beam","Giga Impact","Ice Beam",
        "Blizzard","Thunderbolt","Thunder","Surf","Flamethrower","Fire Blast",
        "Shadow Ball","Psychic","Focus Blast","Body Slam","Brick Break","Gunk Shot",
    ],
    "Nidoran-M": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Swords Dance","Poison Jab",
        "Sludge Bomb","Work Up","Substitute","Hyper Beam","Giga Impact","Ice Beam",
        "Blizzard","Thunderbolt","Thunder","Surf","Flamethrower","Fire Blast",
    ],
    "Nidorino": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Swords Dance","Poison Jab",
        "Sludge Bomb","Work Up","Substitute","Hyper Beam","Giga Impact","Ice Beam",
        "Blizzard","Thunderbolt","Thunder","Surf","Flamethrower","Fire Blast",
    ],
    "Nidoking": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Swords Dance","Poison Jab",
        "Sludge Bomb","Work Up","Substitute","Hyper Beam","Giga Impact","Ice Beam",
        "Blizzard","Thunderbolt","Thunder","Surf","Flamethrower","Fire Blast",
        "Shadow Ball","Psychic","Focus Blast","Body Slam","Brick Break","Gunk Shot",
        "Dragon Pulse","Outrage","Stone Edge","Rock Slide",
    ],
    "Clefairy": [
        "Toxic","Protect","Sunny Day","Rain Dance","Rest","Endure","Facade","Psychic",
        "Shadow Ball","Energy Ball","Ice Beam","Blizzard","Thunderbolt","Thunder",
        "Flamethrower","Fire Blast","Dazzling Gleam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Gravity","Stored Power","Amnesia","Body Slam",
    ],
    "Clefable": [
        "Toxic","Protect","Sunny Day","Rain Dance","Rest","Endure","Facade","Psychic",
        "Shadow Ball","Energy Ball","Ice Beam","Blizzard","Thunderbolt","Thunder",
        "Flamethrower","Fire Blast","Dazzling Gleam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Gravity","Stored Power","Amnesia","Body Slam","Focus Blast",
        "Hyper Voice","Moonblast",
    ],
    "Vulpix": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Flamethrower","Fire Blast",
        "Flame Charge","Will-O-Wisp","Hex","Dark Pulse","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Overheat","Mystical Fire","Energy Ball","Dazzling Gleam",
    ],
    "Ninetales": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Flamethrower","Fire Blast",
        "Flame Charge","Will-O-Wisp","Hex","Dark Pulse","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Overheat","Mystical Fire","Energy Ball","Dazzling Gleam",
        "Solar Beam","Shadow Ball","Extrasensory","Heat Wave","Nasty Plot",
    ],
    "Jigglypuff": [
        "Toxic","Protect","Rest","Endure","Facade","Body Slam","Psychic","Shadow Ball",
        "Flamethrower","Ice Beam","Thunderbolt","Dazzling Gleam","Disarming Voice","Work Up",
        "Substitute","Hyper Beam","Giga Impact","Gravity","Stored Power","Amnesia",
        "Hyper Voice","Play Rough",
    ],
    "Wigglytuff": [
        "Toxic","Protect","Rest","Endure","Facade","Body Slam","Psychic","Shadow Ball",
        "Flamethrower","Ice Beam","Thunderbolt","Dazzling Gleam","Disarming Voice","Work Up",
        "Substitute","Hyper Beam","Giga Impact","Gravity","Stored Power","Amnesia",
        "Hyper Voice","Play Rough","Focus Blast","Ice Beam","Blizzard",
    ],
    "Zubat": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","Fly",
        "Leech Life","Crunch","Shadow Ball","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Poison Jab","Brave Bird","Tailwind","Confuse Ray",
    ],
    "Golbat": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","Fly",
        "Leech Life","Crunch","Shadow Ball","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Poison Jab","Brave Bird","Tailwind","Confuse Ray","Heat Wave","Roost",
    ],
    "Oddish": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Energy Ball","Giga Drain",
        "Sludge Bomb","Moonblast","Dazzling Gleam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Leech Seed","Acid Spray","Grass Knot","Magical Leaf",
    ],
    "Gloom": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Energy Ball","Giga Drain",
        "Sludge Bomb","Moonblast","Dazzling Gleam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Leech Seed","Acid Spray","Grass Knot","Magical Leaf",
    ],
    "Vileplume": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Energy Ball","Giga Drain",
        "Sludge Bomb","Moonblast","Dazzling Gleam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Leech Seed","Acid Spray","Grass Knot","Magical Leaf",
        "Solar Beam","Petal Blizzard","Strength","Synthesis",
    ],
    "Paras": [
        "Toxic","Protect","Rest","Endure","Facade","X-Scissor","Bug Bite","Seed Bomb",
        "Energy Ball","Giga Drain","Sludge Bomb","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Slash","Leech Life","Knock Off",
    ],
    "Parasect": [
        "Toxic","Protect","Rest","Endure","Facade","X-Scissor","Bug Bite","Seed Bomb",
        "Energy Ball","Giga Drain","Sludge Bomb","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Slash","Leech Life","Knock Off","Brick Break","Aerial Ace",
    ],
    "Venonat": [
        "Toxic","Protect","Rest","Endure","Facade","Psychic","Signal Beam","Bug Buzz",
        "Sludge Bomb","Work Up","Substitute","Hyper Beam","Giga Impact","Energy Ball",
        "Hex","Poison Jab",
    ],
    "Venomoth": [
        "Toxic","Protect","Rest","Endure","Facade","Psychic","Signal Beam","Bug Buzz",
        "Sludge Bomb","Work Up","Substitute","Hyper Beam","Giga Impact","Energy Ball",
        "Hex","Poison Jab","Shadow Ball","Quiver Dance","Sleep Powder","Tailwind",
    ],
    "Diglett": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Dig","Rock Slide",
        "Rock Tomb","Slash","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Sucker Punch","Aerial Ace","Mud Shot","Sand Tomb",
    ],
    "Dugtrio": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Dig","Rock Slide",
        "Rock Tomb","Slash","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Sucker Punch","Aerial Ace","Mud Shot","Sand Tomb","Stone Edge","Night Slash",
    ],
    "Meowth": [
        "Toxic","Protect","Rest","Endure","Facade","Slash","Shadow Claw","Crunch",
        "Thunder Wave","Thunderbolt","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Knock Off","Thief","Pay Day","Dark Pulse","Nasty Plot",
    ],
    "Persian": [
        "Toxic","Protect","Rest","Endure","Facade","Slash","Shadow Claw","Crunch",
        "Thunder Wave","Thunderbolt","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Knock Off","Thief","Pay Day","Dark Pulse","Nasty Plot","Night Slash",
        "Foul Play","Aerial Ace","Hyper Voice",
    ],
    "Psyduck": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Ice Beam",
        "Blizzard","Psychic","Shadow Ball","Focus Blast","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Calm Mind","Amnesia","Scald","Aqua Tail","Dig",
    ],
    "Golduck": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Ice Beam",
        "Blizzard","Psychic","Shadow Ball","Focus Blast","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Calm Mind","Amnesia","Scald","Aqua Tail","Dig",
        "Hydro Pump","Brick Break","Encore",
    ],
    "Mankey": [
        "Toxic","Protect","Rest","Endure","Facade","Brick Break","Focus Blast","Bulk Up",
        "Rock Slide","Earthquake","Aerial Ace","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Close Combat","Knock Off","Thunder Punch","Ice Punch","Fire Punch",
    ],
    "Primeape": [
        "Toxic","Protect","Rest","Endure","Facade","Brick Break","Focus Blast","Bulk Up",
        "Rock Slide","Earthquake","Aerial Ace","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Close Combat","Knock Off","Thunder Punch","Ice Punch","Fire Punch",
        "U-turn","Stone Edge","Final Gambit","Thrash",
    ],
    "Growlithe": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Flamethrower","Fire Blast",
        "Flame Charge","Wild Charge","Crunch","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Will-O-Wisp","Overheat","Reversal","Morning Sun","Body Slam",
        "Thunder Fang","Fire Fang","Heat Wave",
    ],
    "Arcanine": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Flamethrower","Fire Blast",
        "Flame Charge","Wild Charge","Crunch","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Will-O-Wisp","Overheat","Reversal","Morning Sun","Body Slam",
        "Thunder Fang","Fire Fang","Heat Wave","Earthquake","Dragon Pulse","Extreme Speed",
        "Outrage","Close Combat","Solar Beam",
    ],
    "Poliwag": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Ice Beam",
        "Blizzard","Focus Blast","Bulk Up","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Scald","Mud Shot","Chilling Water","Body Slam",
    ],
    "Poliwhirl": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Ice Beam",
        "Blizzard","Focus Blast","Bulk Up","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Scald","Mud Shot","Chilling Water","Body Slam","Earthquake","Brick Break",
    ],
    "Poliwrath": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Ice Beam",
        "Blizzard","Focus Blast","Bulk Up","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Scald","Mud Shot","Chilling Water","Body Slam","Earthquake","Brick Break",
        "Close Combat","Submission","Rock Slide","Mind Reader",
    ],
    "Abra": [
        "Toxic","Protect","Rest","Endure","Facade","Psychic","Shadow Ball","Focus Blast",
        "Dazzling Gleam","Energy Ball","Thunderbolt","Thunder Wave","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Calm Mind","Stored Power","Psybeam","Flash",
    ],
    "Kadabra": [
        "Toxic","Protect","Rest","Endure","Facade","Psychic","Shadow Ball","Focus Blast",
        "Dazzling Gleam","Energy Ball","Thunderbolt","Thunder Wave","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Calm Mind","Stored Power","Psybeam","Flash","Trick",
        "Psyshock","Future Sight","Skill Swap",
    ],
    "Alakazam": [
        "Toxic","Protect","Rest","Endure","Facade","Psychic","Shadow Ball","Focus Blast",
        "Dazzling Gleam","Energy Ball","Thunderbolt","Thunder Wave","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Calm Mind","Stored Power","Psybeam","Flash","Trick",
        "Psyshock","Future Sight","Skill Swap","Recover","Teleport","Thunder Punch",
        "Fire Punch","Ice Punch","Encore","Nasty Plot",
    ],
    "Machop": [
        "Toxic","Protect","Rest","Endure","Facade","Brick Break","Bulk Up","Rock Slide",
        "Earthquake","Focus Blast","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Close Combat","Thunder Punch","Ice Punch","Fire Punch","Knock Off","Body Slam",
    ],
    "Machoke": [
        "Toxic","Protect","Rest","Endure","Facade","Brick Break","Bulk Up","Rock Slide",
        "Earthquake","Focus Blast","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Close Combat","Thunder Punch","Ice Punch","Fire Punch","Knock Off","Body Slam",
    ],
    "Machamp": [
        "Toxic","Protect","Rest","Endure","Facade","Brick Break","Bulk Up","Rock Slide",
        "Earthquake","Focus Blast","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Close Combat","Thunder Punch","Ice Punch","Fire Punch","Knock Off","Body Slam",
        "Stone Edge","Submission","Bullet Punch","Heavy Slam","Payback",
    ],
    "Bellsprout": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Energy Ball","Giga Drain",
        "Sludge Bomb","Leech Seed","Grass Knot","Magical Leaf","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Acid Spray","Solar Beam","Power Whip",
    ],
    "Weepinbell": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Energy Ball","Giga Drain",
        "Sludge Bomb","Leech Seed","Grass Knot","Magical Leaf","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Acid Spray","Solar Beam","Power Whip",
    ],
    "Victreebel": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Energy Ball","Giga Drain",
        "Sludge Bomb","Leech Seed","Grass Knot","Magical Leaf","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Acid Spray","Solar Beam","Power Whip","Swords Dance",
        "Leaf Storm","Knock Off","Gastro Acid",
    ],
    "Tentacool": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Sludge Bomb","Poison Jab","Scald","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Acid Spray","Liquidation","Venoshock","Muddy Water",
    ],
    "Tentacruel": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Sludge Bomb","Poison Jab","Scald","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Acid Spray","Liquidation","Venoshock","Muddy Water","Gunk Shot","Hydro Pump",
    ],
    "Geodude": [
        "Toxic","Protect","Rest","Endure","Facade","Rock Slide","Rock Blast","Stone Edge",
        "Rock Polish","Earthquake","Dig","Iron Head","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Rock Tomb","Smack Down","Heavy Slam","Bulldoze",
    ],
    "Graveler": [
        "Toxic","Protect","Rest","Endure","Facade","Rock Slide","Rock Blast","Stone Edge",
        "Rock Polish","Earthquake","Dig","Iron Head","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Rock Tomb","Smack Down","Heavy Slam","Bulldoze","Brick Break",
    ],
    "Golem": [
        "Toxic","Protect","Rest","Endure","Facade","Rock Slide","Rock Blast","Stone Edge",
        "Rock Polish","Earthquake","Dig","Iron Head","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Rock Tomb","Smack Down","Heavy Slam","Bulldoze","Brick Break",
        "Fire Punch","Thunder Punch","Stealth Rock","Explosion",
    ],
    "Ponyta": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Flamethrower","Fire Blast",
        "Flame Charge","Wild Charge","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Will-O-Wisp","Solar Beam","Overheat","Agility","Morning Sun","Body Slam",
    ],
    "Rapidash": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Flamethrower","Fire Blast",
        "Flame Charge","Wild Charge","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Will-O-Wisp","Solar Beam","Overheat","Agility","Morning Sun","Body Slam",
        "Heat Wave","Drill Run","Smart Strike",
    ],
    "Slowpoke": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Psychic","Ice Beam",
        "Blizzard","Fire Blast","Flamethrower","Calm Mind","Shadow Ball","Work Up",
        "Substitute","Hyper Beam","Giga Impact","Amnesia","Scald","Trick Room","Slack Off",
    ],
    "Slowbro": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Psychic","Ice Beam",
        "Blizzard","Fire Blast","Flamethrower","Calm Mind","Shadow Ball","Work Up",
        "Substitute","Hyper Beam","Giga Impact","Amnesia","Scald","Trick Room","Slack Off",
        "Future Site","Stored Power","Focus Blast","Hydro Pump","Psyshock",
    ],
    "Magnemite": [
        "Toxic","Protect","Rest","Endure","Facade","Thunderbolt","Thunder","Volt Switch",
        "Flash Cannon","Thunder Wave","Electro Ball","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Charge Beam","Gyro Ball","Mirror Shot","Magnet Rise",
    ],
    "Magneton": [
        "Toxic","Protect","Rest","Endure","Facade","Thunderbolt","Thunder","Volt Switch",
        "Flash Cannon","Thunder Wave","Electro Ball","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Charge Beam","Gyro Ball","Mirror Shot","Magnet Rise","Tri Attack",
    ],
    "Farfetch'd": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","Fly","Leaf Blade",
        "Swords Dance","Night Slash","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Shadow Claw","Knock Off","Slash",
    ],
    "Doduo": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Fly","Brave Bird",
        "Work Up","Substitute","Hyper Beam","Giga Impact","Drill Peck","Quick Attack",
    ],
    "Dodrio": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Fly","Brave Bird",
        "Work Up","Substitute","Hyper Beam","Giga Impact","Drill Peck","Quick Attack",
        "Sky Attack","Tailwind","Agility",
    ],
    "Seel": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Ice Beam","Blizzard","Aqua Tail",
        "Waterfall","Work Up","Substitute","Hyper Beam","Giga Impact","Icy Wind","Body Slam",
    ],
    "Dewgong": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Ice Beam","Blizzard","Aqua Tail",
        "Waterfall","Work Up","Substitute","Hyper Beam","Giga Impact","Icy Wind","Body Slam",
        "Sheer Cold","Liquidation","Aqua Jet",
    ],
    "Grimer": [
        "Toxic","Protect","Rest","Endure","Facade","Sludge Bomb","Gunk Shot","Poison Jab",
        "Crunch","Minimize","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Shadow Punch","Fire Punch","Thunder Punch","Ice Punch","Sludge Wave",
    ],
    "Muk": [
        "Toxic","Protect","Rest","Endure","Facade","Sludge Bomb","Gunk Shot","Poison Jab",
        "Crunch","Minimize","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Shadow Punch","Fire Punch","Thunder Punch","Ice Punch","Sludge Wave",
        "Brick Break","Body Slam","Explosion",
    ],
    "Shellder": [
        "Toxic","Protect","Rest","Endure","Facade","Ice Beam","Blizzard","Rock Slide",
        "Rock Blast","Work Up","Substitute","Hyper Beam","Giga Impact","Icicle Spear",
        "Liquidation","Surf",
    ],
    "Cloyster": [
        "Toxic","Protect","Rest","Endure","Facade","Ice Beam","Blizzard","Rock Slide",
        "Rock Blast","Work Up","Substitute","Hyper Beam","Giga Impact","Icicle Spear",
        "Liquidation","Surf","Icicle Crash","Hydro Pump","Shell Smash","Razor Shell",
    ],
    "Gastly": [
        "Toxic","Protect","Rest","Endure","Facade","Shadow Ball","Psychic","Hex","Dark Pulse",
        "Sludge Bomb","Energy Ball","Dazzling Gleam","Will-O-Wisp","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Confuse Ray","Nasty Plot","Thunderbolt",
    ],
    "Haunter": [
        "Toxic","Protect","Rest","Endure","Facade","Shadow Ball","Psychic","Hex","Dark Pulse",
        "Sludge Bomb","Energy Ball","Dazzling Gleam","Will-O-Wisp","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Confuse Ray","Nasty Plot","Thunderbolt","Trick","Encore",
    ],
    "Gengar": [
        "Toxic","Protect","Rest","Endure","Facade","Shadow Ball","Psychic","Hex","Dark Pulse",
        "Sludge Bomb","Energy Ball","Dazzling Gleam","Will-O-Wisp","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Confuse Ray","Nasty Plot","Thunderbolt","Trick","Encore",
        "Focus Blast","Icy Wind","Thunder Punch","Fire Punch","Ice Punch","Calm Mind",
    ],
    "Onix": [
        "Toxic","Protect","Rest","Endure","Facade","Rock Slide","Rock Blast","Stone Edge",
        "Rock Polish","Earthquake","Iron Head","Stealth Rock","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Rock Tomb","Smack Down","Bulldoze","Dragon Breath",
    ],
    "Drowzee": [
        "Toxic","Protect","Rest","Endure","Facade","Psychic","Shadow Ball","Focus Blast",
        "Dazzling Gleam","Thunderbolt","Thunder Wave","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Calm Mind","Stored Power","Psybeam","Trick","Zen Headbutt",
    ],
    "Hypno": [
        "Toxic","Protect","Rest","Endure","Facade","Psychic","Shadow Ball","Focus Blast",
        "Dazzling Gleam","Thunderbolt","Thunder Wave","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Calm Mind","Stored Power","Psybeam","Trick","Zen Headbutt",
        "Psyshock","Future Sight","Skill Swap","Nasty Plot","Amnesia",
    ],
    "Krabby": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Brick Break",
        "Rock Slide","Swords Dance","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Knock Off","Slash","Liquidation","Crabhammer","X-Scissor",
    ],
    "Kingler": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Brick Break",
        "Rock Slide","Swords Dance","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Knock Off","Slash","Liquidation","Crabhammer","X-Scissor","Agility",
    ],
    "Voltorb": [
        "Toxic","Protect","Rest","Endure","Facade","Thunderbolt","Thunder","Volt Switch",
        "Thunder Wave","Electro Ball","Charge Beam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Gyro Ball","Eerie Impulse","Explosion","Spark",
    ],
    "Electrode": [
        "Toxic","Protect","Rest","Endure","Facade","Thunderbolt","Thunder","Volt Switch",
        "Thunder Wave","Electro Ball","Charge Beam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Gyro Ball","Eerie Impulse","Explosion","Spark","Foul Play",
    ],
    "Exeggcute": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Psychic","Energy Ball",
        "Giga Drain","Solar Beam","Leech Seed","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Magical Leaf","Grass Knot","Seed Bomb","Bullet Seed",
    ],
    "Exeggutor": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Psychic","Energy Ball",
        "Giga Drain","Solar Beam","Leech Seed","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Magical Leaf","Grass Knot","Seed Bomb","Bullet Seed",
        "Stomping Tantrum","Earthquake","Amnesia","Leaf Storm",
    ],
    "Cubone": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Rock Slide","Rock Tomb",
        "Swords Dance","Iron Head","Stealth Rock","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Bonemerang","False Swipe","Knock Off",
    ],
    "Marowak": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Rock Slide","Rock Tomb",
        "Swords Dance","Iron Head","Stealth Rock","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Bonemerang","False Swipe","Knock Off","Stone Edge","Shadow Bone",
        "Heavy Slam","Fire Punch","Thunder Punch","Ice Punch",
    ],
    "Hitmonlee": [
        "Toxic","Protect","Rest","Endure","Facade","Brick Break","Bulk Up","Focus Blast",
        "Rock Slide","Earthquake","Swords Dance","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Close Combat","High Jump Kick","Blaze Kick","Knock Off",
        "Stone Edge","Stomping Tantrum","Thunder Punch","Ice Punch","Fire Punch",
    ],
    "Hitmonchan": [
        "Toxic","Protect","Rest","Endure","Facade","Brick Break","Bulk Up","Focus Blast",
        "Rock Slide","Earthquake","Swords Dance","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Close Combat","Sky Uppercut","Knock Off","Stone Edge",
        "Thunder Punch","Ice Punch","Fire Punch","Mach Punch","Bullet Punch",
    ],
    "Lickitung": [
        "Toxic","Protect","Rest","Endure","Facade","Body Slam","Slam","Hyper Voice",
        "Work Up","Substitute","Hyper Beam","Giga Impact","Earthquake","Rock Slide",
        "Blizzard","Ice Beam","Thunderbolt","Flamethrower","Amnesia","Stomping Tantrum",
    ],
    "Koffing": [
        "Toxic","Protect","Rest","Endure","Facade","Sludge Bomb","Gunk Shot","Poison Jab",
        "Dark Pulse","Shadow Ball","Will-O-Wisp","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Explosion","Acid Spray","Venoshock",
    ],
    "Weezing": [
        "Toxic","Protect","Rest","Endure","Facade","Sludge Bomb","Gunk Shot","Poison Jab",
        "Dark Pulse","Shadow Ball","Will-O-Wisp","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Explosion","Acid Spray","Venoshock","Thunderbolt","Flamethrower",
        "Fire Blast","Sludge Wave","Burning Jealousy",
    ],
    "Rhyhorn": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Rock Slide","Rock Blast",
        "Stone Edge","Rock Polish","Iron Head","Stealth Rock","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Rock Tomb","Bulldoze","Smack Down","Horn Drill",
    ],
    "Rhydon": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Rock Slide","Rock Blast",
        "Stone Edge","Rock Polish","Iron Head","Stealth Rock","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Rock Tomb","Bulldoze","Smack Down","Horn Drill",
        "Drill Run","Megahorn","Hammer Arm","Brick Break","Thunder Punch","Fire Punch",
        "Ice Punch","Aqua Tail","Surf",
    ],
    "Chansey": [
        "Toxic","Protect","Rest","Endure","Facade","Body Slam","Hyper Voice","Dazzling Gleam",
        "Thunderbolt","Ice Beam","Flamethrower","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Psychic","Shadow Ball","Soft-Boiled","Gravity","Amnesia",
        "Heal Pulse","Seismic Toss",
    ],
    "Tangela": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Energy Ball","Giga Drain",
        "Solar Beam","Leech Seed","Grass Knot","Magical Leaf","Sleep Powder","Work Up",
        "Substitute","Hyper Beam","Giga Impact","Seed Bomb","Power Whip","Knock Off",
    ],
    "Kangaskhan": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Rock Slide","Swords Dance",
        "Brick Break","Focus Blast","Body Slam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Ice Punch","Thunder Punch","Fire Punch","Knock Off","Crunch",
        "Mega Punch","Mega Kick","Outrage","Aqua Tail","Drain Punch","Stomping Tantrum",
    ],
    "Horsea": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Dragon Pulse","Work Up","Substitute","Hyper Beam","Giga Impact","Scald","Waterfall",
        "Flash Cannon","Muddy Water","Dragon Breath",
    ],
    "Seadra": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Dragon Pulse","Work Up","Substitute","Hyper Beam","Giga Impact","Scald","Waterfall",
        "Flash Cannon","Muddy Water","Dragon Breath","Hydro Pump","Outrage",
    ],
    "Goldeen": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Waterfall","Ice Beam",
        "Blizzard","Work Up","Substitute","Hyper Beam","Giga Impact","Aqua Tail","Scald",
    ],
    "Seaking": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Waterfall","Ice Beam",
        "Blizzard","Work Up","Substitute","Hyper Beam","Giga Impact","Aqua Tail","Scald",
        "Liquidation","Megahorn","Drill Run",
    ],
    "Staryu": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Psychic","Thunderbolt","Thunder","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Swift","Flash","Scald","Power Gem","Cosmic Power","Gravity",
    ],
    "Starmie": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Psychic","Thunderbolt","Thunder","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Swift","Flash","Scald","Power Gem","Cosmic Power","Gravity","Hydro Pump",
        "Psyshock","Shadow Ball","Dazzling Gleam","Calm Mind","Trick","Rapid Spin",
    ],
    "Mr. Mime": [
        "Toxic","Protect","Rest","Endure","Facade","Psychic","Shadow Ball","Focus Blast",
        "Dazzling Gleam","Thunderbolt","Thunder Wave","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Calm Mind","Stored Power","Trick","Skill Swap","Nasty Plot",
        "Misty Terrain","Psyshock","Future Sight","Encore","Baton Pass","Barrier",
    ],
    "Scyther": [
        "Toxic","Protect","Rest","Endure","Facade","Aerial Ace","Air Slash","X-Scissor",
        "Swords Dance","Night Slash","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Slash","Wing Attack","Agility","Knock Off","U-turn","Brick Break",
    ],
    "Jynx": [
        "Toxic","Protect","Rest","Endure","Facade","Ice Beam","Blizzard","Psychic",
        "Shadow Ball","Dazzling Gleam","Energy Ball","Calm Mind","Nasty Plot","Work Up",
        "Substitute","Hyper Beam","Giga Impact","Focus Blast","Icy Wind","Trick",
        "Psyshock","Future Sight","Skill Swap","Lovely Kiss",
    ],
    "Electabuzz": [
        "Toxic","Protect","Rest","Endure","Facade","Thunderbolt","Thunder","Volt Switch",
        "Thunder Wave","Electro Ball","Thunder Punch","Focus Blast","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Charge Beam","Ice Punch","Fire Punch","Brick Break",
        "Wild Charge","Low Kick","Flamethrower","Psychic",
    ],
    "Magmar": [
        "Toxic","Protect","Rest","Endure","Facade","Flamethrower","Fire Blast","Flame Charge",
        "Overheat","Will-O-Wisp","Focus Blast","Fire Punch","Thunder Punch","Work Up",
        "Substitute","Hyper Beam","Giga Impact","Heat Wave","Confuse Ray","Ice Punch",
        "Brick Break","Psychic","Power Gem",
    ],
    "Pinsir": [
        "Toxic","Protect","Rest","Endure","Facade","X-Scissor","Bug Bite","Swords Dance",
        "Rock Slide","Earthquake","Brick Break","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Close Combat","Knock Off","Slash","Stone Edge","Aerial Ace",
        "Bulk Up","Return",
    ],
    "Tauros": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Rock Slide","Body Slam",
        "Swords Dance","Iron Head","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Zen Headbutt","Brick Break","Bulldoze","Stomping Tantrum","Close Combat","Thrash",
    ],
    "Magikarp": [],
    "Gyarados": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Waterfall","Ice Beam",
        "Blizzard","Crunch","Dark Pulse","Swords Dance","Dragon Dance","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Aqua Tail","Bite","Earthquake","Stone Edge",
        "Power Whip","Liquidation","Hurricane","Bounce","Outrage","Dragon Pulse",
    ],
    "Lapras": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Thunderbolt","Thunder","Psychic","Body Slam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Dragon Pulse","Icy Wind","Freeze-Dry","Chilling Water","Brine",
        "Waterfall","Focus Blast","Shadow Ball","Aqua Tail","Sheer Cold",
    ],
    "Ditto":    [],
    "Eevee": [
        "Toxic","Protect","Rest","Endure","Facade","Shadow Ball","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Body Slam","Quick Attack","Hyper Voice","Bite",
        "Baby-Doll Eyes","Charm","Swift",
    ],
    "Vaporeon": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Shadow Ball","Scald","Work Up","Substitute","Hyper Beam","Giga Impact","Aqua Ring",
        "Muddy Water","Chilling Water","Brine","Hydro Pump","Body Slam","Aurora Veil",
    ],
    "Jolteon": [
        "Toxic","Protect","Rest","Endure","Facade","Thunderbolt","Thunder","Volt Switch",
        "Thunder Wave","Shadow Ball","Charge Beam","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Electro Ball","Wild Charge","Pin Missile","Body Slam",
    ],
    "Flareon": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Flamethrower","Fire Blast",
        "Flame Charge","Shadow Ball","Will-O-Wisp","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Overheat","Heat Wave","Body Slam","Superpower","Burning Jealousy",
    ],
    "Porygon": [
        "Toxic","Protect","Rest","Endure","Facade","Thunderbolt","Thunder","Psybeam",
        "Psychic","Ice Beam","Blizzard","Shadow Ball","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Tri Attack","Discharge","Flash Cannon","Charge Beam","Recover",
        "Recycle","Trick","Agility",
    ],
    "Omanyte": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Rock Slide","Rock Blast","Stone Edge","Earth Power","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Scald","Mud Shot","Ancient Power","Shell Smash",
    ],
    "Omastar": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Surf","Ice Beam","Blizzard",
        "Rock Slide","Rock Blast","Stone Edge","Earth Power","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Scald","Mud Shot","Ancient Power","Shell Smash",
        "Hydro Pump","Toxic Spikes","Spikes",
    ],
    "Kabuto": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Rock Slide",
        "Rock Blast","Stone Edge","Swords Dance","Aqua Jet","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Slash","Knock Off","X-Scissor","Ancient Power",
    ],
    "Kabutops": [
        "Toxic","Protect","Rest","Endure","Facade","Surf","Waterfall","Rock Slide",
        "Rock Blast","Stone Edge","Swords Dance","Aqua Jet","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Slash","Knock Off","X-Scissor","Ancient Power",
        "Liquidation","Brick Break","Earthquake","Night Slash","Leech Life",
    ],
    "Aerodactyl": [
        "Toxic","Protect","Rest","Endure","Facade","Rock Slide","Rock Blast","Stone Edge",
        "Aerial Ace","Fly","Earthquake","Iron Head","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Rock Tomb","Ancient Power","Crunch","Sky Attack","Agility",
        "Dragon Claw","Dragon Breath","Tailwind","Bulldoze","Fire Fang","Thunder Fang",
        "Ice Fang",
    ],
    "Snorlax": [
        "Toxic","Protect","Rest","Endure","Facade","Earthquake","Rock Slide","Body Slam",
        "Swords Dance","Crunch","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Ice Beam","Blizzard","Thunderbolt","Thunder","Flamethrower","Fire Blast",
        "Surf","Shadow Ball","Psychic","Focus Blast","Heavy Slam","Brick Break",
        "Bulk Up","Belly Drum","Sleep Talk","Recycle","Zen Headbutt",
    ],
    "Articuno": [
        "Toxic","Protect","Rest","Endure","Facade","Ice Beam","Blizzard","Aerial Ace",
        "Air Slash","Fly","Psychic","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Hurricane","Tailwind","Icy Wind","Mind Reader","Sheer Cold","Sky Attack",
        "Ancient Power","Roost","Freeze-Dry",
    ],
    "Zapdos": [
        "Toxic","Protect","Rest","Endure","Facade","Thunderbolt","Thunder","Volt Switch",
        "Thunder Wave","Aerial Ace","Air Slash","Fly","Charge Beam","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Hurricane","Tailwind","Agility","Roost","Heat Wave",
        "Ancient Power","Sky Attack",
    ],
    "Moltres": [
        "Toxic","Protect","Sunny Day","Rest","Endure","Facade","Flamethrower","Fire Blast",
        "Aerial Ace","Air Slash","Fly","Hurricane","Solar Beam","Work Up","Substitute",
        "Hyper Beam","Giga Impact","Tailwind","Overheat","Heat Wave","Sky Attack","Roost",
        "Ancient Power","Will-O-Wisp","Burn Up",
    ],
    "Dratini": [
        "Toxic","Protect","Rest","Endure","Facade","Dragon Pulse","Dragon Claw","Outrage",
        "Thunder Wave","Thunderbolt","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Slam","Agility","Wrap","Dragon Dance","Dragon Breath","Body Slam",
    ],
    "Dragonair": [
        "Toxic","Protect","Rest","Endure","Facade","Dragon Pulse","Dragon Claw","Outrage",
        "Thunder Wave","Thunderbolt","Work Up","Substitute","Hyper Beam","Giga Impact",
        "Slam","Agility","Wrap","Dragon Dance","Dragon Breath","Body Slam",
        "Aqua Tail","Iron Tail",
    ],
    "Dragonite": [
        "Toxic","Protect","Rain Dance","Rest","Endure","Facade","Dragon Pulse","Dragon Claw",
        "Outrage","Thunder Wave","Thunderbolt","Thunder","Surf","Waterfall","Ice Beam",
        "Blizzard","Fire Blast","Flamethrower","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Slam","Agility","Dragon Dance","Dragon Breath","Body Slam",
        "Aqua Tail","Iron Tail","Earthquake","Stone Edge","Fly","Hurricane","Aerial Ace",
        "Extreme Speed","Dragon Rush","Focus Blast","Steel Wing","Heat Wave",
    ],
    "Mewtwo": [
        "Toxic","Protect","Sunny Day","Rain Dance","Rest","Endure","Facade","Psychic",
        "Shadow Ball","Focus Blast","Dazzling Gleam","Ice Beam","Blizzard","Thunderbolt",
        "Thunder","Flamethrower","Fire Blast","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Calm Mind","Stored Power","Trick","Psyshock","Future Sight",
        "Skill Swap","Amnesia","Aura Sphere","Bulk Up","Swords Dance","Earthquake",
        "Stone Edge","Aerial Ace","Fly","Surf","Brick Break","Drain Punch","Body Slam",
        "Recover","Teleport","Agility","Nasty Plot","Dragon Pulse","Mystical Fire",
        "Flash Cannon","Signal Beam","Electro Ball","Volt Switch","Power Gem","Swift",
        "Energy Ball","Shadow Claw","Night Slash","Laser Focus","Low Kick",
    ],
    "Mew": [
        # Mew peut apprendre toutes les CT/CS
        "Swords Dance","Toxic","Protect","Sunny Day","Rain Dance","Sandstorm","Rest",
        "Endure","Facade","Thunderbolt","Thunder","Ice Beam","Blizzard","Psychic",
        "Shadow Ball","Flamethrower","Fire Blast","Energy Ball","Giga Drain","Solar Beam",
        "Surf","Waterfall","Earthquake","Rock Slide","Stone Edge","Iron Head",
        "Brick Break","Focus Blast","Bulk Up","Work Up","Substitute","Hyper Beam",
        "Giga Impact","Calm Mind","Stored Power","Trick","Aerial Ace","Air Slash","Fly",
        "Sludge Bomb","Poison Jab","Dragon Pulse","Dragon Claw","Outrage","Body Slam",
        "Volt Switch","Flash Cannon","Dark Pulse","Shadow Claw","Dazzling Gleam",
        "Nasty Plot","Agility","Dragon Dance","Amnesia","Tailwind","Hyper Voice",
        "Ice Punch","Thunder Punch","Fire Punch","Knock Off","Foul Play","U-turn",
    ],
}

# ==============================================================================
# FONCTIONS PRINCIPALES
# ==============================================================================

def create_tm_items():
    """Crée ou met à jour les items CT dans la base."""
    logger.info("=" * 70)
    logger.info("CRÉATION DES CT (TM) — Gen 9")
    logger.info("=" * 70)

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for num, name, move_name, price in TM_DATA:
        try:
            move = PokemonMove.objects.get(name=move_name)
        except PokemonMove.DoesNotExist:
            logger.warning(f"  [!] Move introuvable en base : '{move_name}' → CT{num:03d} ignorée")
            skipped_count += 1
            continue

        obj, created = Item.objects.update_or_create(
            item_type='tm',
            tm_number=num,
            defaults={
                'name': f"CT{num:03d} {move.name}",
                'description': f"CT qui enseigne {move.name}.",
                'price': price,
                'tm_move': move,
                'is_consumable': False,
            }
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    logger.info(f"  CT — {created_count} créées, {updated_count} mises à jour, {skipped_count} ignorées")


def create_cs_items():
    """Crée ou met à jour les items CS dans la base."""
    logger.info("=" * 70)
    logger.info("CRÉATION DES CS (HM) — Gen 9")
    logger.info("=" * 70)

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for num, name, move_name, price in CS_DATA:
        try:
            move = PokemonMove.objects.get(name=move_name)
        except PokemonMove.DoesNotExist:
            logger.warning(f"  [!] Move introuvable en base : '{move_name}' → CS{num:02d} ignorée")
            skipped_count += 1
            continue

        obj, created = Item.objects.update_or_create(
            item_type='cs',
            tm_number=num,
            defaults={
                'name': f"{name}",
                'price': price,
                'tm_move': move,
                'is_consumable': False,
            }
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    logger.info(f"  CS — {created_count} créées, {updated_count} mises à jour, {skipped_count} ignorées")


def create_tm_learnsets():
    """
    Enregistre dans PokemonLearnableMove les compatibilités TM/CS par espèce.
    learn_method='tm', level_learned=0.
    """
    logger.info("=" * 70)
    logger.info("CRÉATION DES COMPATIBILITÉS TM/CS PAR ESPÈCE — Gen 9")
    logger.info("=" * 70)

    total_created  = 0
    total_skipped  = 0
    pokemon_errors = []
    move_errors    = []

    # Rassembler tous les moves TM/CS dans un dict pour accélerer les lookups
    all_tm_moves = {item.tm_move.name: item.tm_move
                    for item in Item.objects.filter(item_type__in=('tm', 'cs'))
                    .select_related('tm_move') if item.tm_move}

    # Normalisation des noms Pokémon (noms du script → noms en base)
    POKEMON_NAME_MAP = {
        'Nidoran-F': 'Nidoran♀',
        'Nidoran-M': 'Nidoran♂',
    }

    for pokemon_name, move_names in TM_LEARNSETS_GEN9.items():
        db_name = POKEMON_NAME_MAP.get(pokemon_name, pokemon_name)
        try:
            pokemon = Pokemon.objects.get(name=db_name)
        except Pokemon.DoesNotExist:
            logger.warning(f"  [!] Pokémon introuvable : '{pokemon_name}'")
            pokemon_errors.append(pokemon_name)
            continue

        for move_name in move_names:
            move = all_tm_moves.get(move_name)
            if move is None:
                # Essai direct en base
                try:
                    move = PokemonMove.objects.get(name=move_name)
                except PokemonMove.DoesNotExist:
                    if move_name not in move_errors:
                        logger.warning(f"    [!] Move TM introuvable en base : '{move_name}'")
                        move_errors.append(move_name)
                    total_skipped += 1
                    continue

            _, created = PokemonLearnableMove.objects.get_or_create(
                pokemon=pokemon,
                move=move,
                learn_method='tm',
                defaults={'level_learned': 0},
            )
            if created:
                total_created += 1

    logger.info(f"  Compatibilités — {total_created} créées, {total_skipped} moves ignorés")
    if pokemon_errors:
        logger.warning(f"  Pokémon introuvables : {pokemon_errors}")
    if move_errors:
        logger.warning(f"  Moves introuvables   : {move_errors}")
    logger.info("=" * 70)


def runCSAndTM(clear_tm_learnsets: bool = False):
    """
    Point d'entrée principal.

    Args:
        clear_tm_learnsets: Si True, supprime toutes les entrées TM existantes
                            avant de les recréer (utile pour une réinitialisation).
    """
    logger.info("=" * 70)
    logger.info("INIT TM/CS — DÉMARRAGE")
    logger.info("=" * 70)

    if clear_tm_learnsets:
        deleted, _ = PokemonLearnableMove.objects.filter(learn_method='tm').delete()
        logger.info(f"  [!] {deleted} entrées TM supprimées (clear demandé)")

    create_tm_items()
    create_cs_items()
    create_tm_learnsets()

    logger.info("=" * 70)
    logger.info("[✓] Initialisation TM/CS terminée !")
    logger.info("=" * 70)