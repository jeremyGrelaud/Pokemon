#!/usr/bin/python3
"""
Script d'initialisation des capacités apprises par niveau — Gen 9 (Scarlet/Violet).

POURQUOI GEN 9 ?
- Scarlet/Violet a rebalancé les learnsets pour un meilleur gameplay.
- Nouveaux moves comme Tera Blast, Trailblaze, Pounce sont disponibles.
- Certains anciens moves ont été retirés, d'autres ajoutés pour plus d'options.
- Les Pokémon de la Gen 1 restent jouables avec des outils modernes.

SOURCE: pokemondb.net (learnsets SV — Scarlet/Violet)
NOTES:
- Niveau 0 = move disponible dès le départ / forme initiale.
- Les moves de niveau 1 sont appris dès que le Pokémon est obtenu.
- Les moves appris par évolution (evo moves) sont indiqués au niveau 1.
"""

from myPokemonApp.models import Pokemon, PokemonMove, PokemonLearnableMove
import logging

logging.basicConfig(level=logging.INFO)


# ==============================================================================
# DONNÉES GEN 9 (Scarlet/Violet) — niveaux d'apprentissage
# Format: 'NomPokemon': [('NomMove', niveau), ...]
# ==============================================================================

LEARNABLE_MOVES_GEN9 = {

    # ── STARTERS ──────────────────────────────────────────────────────────────

    "Bulbasaur": [
        ("Tackle", 1), ("Growl", 1),
        ("Vine Whip", 3), ("Growth", 6),
        ("Leech Seed", 9), ("Razor Leaf", 12),
        ("Poison Powder", 15), ("Sleep Powder", 15),
        ("Sweet Scent", 18), ("Synthesis", 21),
        ("Worry Seed", 24), ("Ingrain", 27),
        ("Knock Off", 30), ("Giga Drain", 33),
        ("Petal Dance", 36), ("Solar Beam", 45),
    ],
    "Ivysaur": [
        ("Tackle", 1), ("Growl", 1), ("Vine Whip", 1),
        ("Growth", 6), ("Leech Seed", 9), ("Razor Leaf", 12),
        ("Poison Powder", 15), ("Sleep Powder", 15),
        ("Sweet Scent", 20), ("Synthesis", 23),
        ("Worry Seed", 26), ("Ingrain", 29),
        ("Knock Off", 32), ("Giga Drain", 35),
        ("Petal Dance", 38), ("Solar Beam", 47),
    ],
    "Venusaur": [
        ("Tackle", 1), ("Growl", 1), ("Vine Whip", 1), ("Growth", 1),
        ("Leech Seed", 9), ("Razor Leaf", 12),
        ("Poison Powder", 15), ("Sleep Powder", 15),
        ("Sweet Scent", 20), ("Synthesis", 23),
        ("Worry Seed", 26), ("Ingrain", 29),
        ("Knock Off", 32), ("Giga Drain", 36),
        ("Petal Dance", 42), ("Solar Beam", 52),
        ("Petal Blizzard", 58),
    ],

    "Charmander": [
        ("Scratch", 1), ("Growl", 1),
        ("Ember", 4), ("Smokescreen", 8),
        ("Dragon Breath", 12), ("Slash", 17),
        ("Flamethrower", 21), ("Scary Face", 25),
        ("Fire Spin", 28), ("Inferno", 32),
        ("Dragon Rage", 36), ("Flare Blitz", 40),
    ],
    "Charmeleon": [
        ("Scratch", 1), ("Growl", 1), ("Ember", 1), ("Smokescreen", 1),
        ("Dragon Breath", 12), ("Slash", 18),
        ("Flamethrower", 23), ("Scary Face", 28),
        ("Fire Spin", 32), ("Inferno", 37),
        ("Dragon Rage", 42), ("Flare Blitz", 46),
    ],
    "Charizard": [
        ("Scratch", 1), ("Growl", 1), ("Ember", 1), ("Smokescreen", 1),
        ("Dragon Breath", 12), ("Slash", 18),
        ("Flamethrower", 23), ("Scary Face", 28),
        ("Wing Attack", 36), ("Fire Spin", 36),
        ("Inferno", 42), ("Dragon Rage", 47),
        ("Flare Blitz", 52), ("Fire Blast", 58),
        ("Hurricane", 62),
    ],

    "Squirtle": [
        ("Tackle", 1), ("Tail Whip", 1),
        ("Water Gun", 3), ("Withdraw", 6),
        ("Bubble", 9), ("Bite", 12),
        ("Rapid Spin", 16), ("Water Pulse", 20),
        ("Protect", 24), ("Rain Dance", 28),
        ("Aqua Tail", 32), ("Skull Bash", 36),
        ("Iron Defense", 40), ("Hydro Pump", 44),
    ],
    "Wartortle": [
        ("Tackle", 1), ("Tail Whip", 1), ("Water Gun", 1), ("Withdraw", 1),
        ("Bubble", 9), ("Bite", 12),
        ("Rapid Spin", 16), ("Water Pulse", 21),
        ("Protect", 26), ("Rain Dance", 31),
        ("Aqua Tail", 36), ("Skull Bash", 41),
        ("Iron Defense", 46), ("Hydro Pump", 51),
    ],
    "Blastoise": [
        ("Tackle", 1), ("Tail Whip", 1), ("Water Gun", 1), ("Withdraw", 1),
        ("Bubble", 9), ("Bite", 12),
        ("Rapid Spin", 16), ("Water Pulse", 21),
        ("Protect", 26), ("Rain Dance", 31),
        ("Aqua Tail", 36), ("Skull Bash", 42),
        ("Iron Defense", 48), ("Hydro Pump", 54),
        ("Hydro Cannon", 62),
    ],

    # ── CHENILLES / INSECTES ─────────────────────────────────────────────────

    "Caterpie": [
        ("Tackle", 1), ("String Shot", 1), ("Bug Bite", 9),
    ],
    "Metapod": [
        ("Harden", 1),
    ],
    "Butterfree": [
        ("Gust", 1), ("Confusion", 1),
        ("Poison Powder", 12), ("Sleep Powder", 12), ("Stun Spore", 12),
        ("Psybeam", 16), ("Whirlwind", 20),
        ("Silver Wind", 24), ("Air Slash", 28),
        ("Safeguard", 32), ("Bug Buzz", 36),
        ("Quiver Dance", 40),
    ],

    "Weedle": [
        ("Poison Sting", 1), ("String Shot", 1), ("Bug Bite", 9),
    ],
    "Kakuna": [
        ("Harden", 1),
    ],
    "Beedrill": [
        ("Fury Attack", 1), ("Twineedle", 1),
        ("Rage", 10), ("Pursuit", 15),
        ("Focus Energy", 20), ("Assurance", 25),
        ("Pin Missile", 30), ("Agility", 35),
        ("X-Scissor", 40), ("Fell Stinger", 45),
        ("Endeavor", 50),
    ],

    # ── PIGEONS ───────────────────────────────────────────────────────────────

    "Pidgey": [
        ("Tackle", 1), ("Sand Attack", 1),
        ("Gust", 5), ("Quick Attack", 9),
        ("Whirlwind", 13), ("Twister", 17),
        ("Wing Attack", 21), ("Feather Dance", 25),
        ("Agility", 29), ("Mirror Move", 33),
        ("Air Slash", 37), ("Roost", 41),
        ("Hurricane", 45),
    ],
    "Pidgeotto": [
        ("Tackle", 1), ("Sand Attack", 1), ("Gust", 1), ("Quick Attack", 1),
        ("Whirlwind", 13), ("Twister", 17),
        ("Wing Attack", 21), ("Feather Dance", 26),
        ("Agility", 31), ("Mirror Move", 36),
        ("Air Slash", 41), ("Roost", 46),
        ("Hurricane", 51),
    ],
    "Pidgeot": [
        ("Tackle", 1), ("Sand Attack", 1), ("Gust", 1), ("Quick Attack", 1),
        ("Wing Attack", 1), ("Whirlwind", 13),
        ("Feather Dance", 26), ("Agility", 31),
        ("Mirror Move", 36), ("Air Slash", 42),
        ("Roost", 48), ("Hurricane", 54),
    ],

    # ── RONGEURS ──────────────────────────────────────────────────────────────

    "Rattata": [
        ("Tackle", 1), ("Tail Whip", 1),
        ("Quick Attack", 4), ("Focus Energy", 7),
        ("Bite", 10), ("Pursuit", 13),
        ("Hyper Fang", 16), ("Assurance", 19),
        ("Super Fang", 22), ("Double-Edge", 25),
        ("Endeavor", 28), ("Screech", 31),
        ("Crunch", 34),
    ],
    "Raticate": [
        ("Tackle", 1), ("Tail Whip", 1), ("Quick Attack", 1), ("Focus Energy", 1),
        ("Bite", 1), ("Pursuit", 1),
        ("Hyper Fang", 16), ("Assurance", 19),
        ("Super Fang", 22), ("Double-Edge", 26),
        ("Endeavor", 30), ("Screech", 34),
        ("Crunch", 38),
    ],

    # ── SPEAROW / FEAROW ──────────────────────────────────────────────────────

    "Spearow": [
        ("Peck", 1), ("Growl", 1),
        ("Leer", 5), ("Fury Attack", 9),
        ("Aerial Ace", 13), ("Pursuit", 17),
        ("Assurance", 21), ("Mirror Move", 25),
        ("Agility", 29), ("Drill Peck", 33),
        ("Roost", 37),
    ],
    "Fearow": [
        ("Peck", 1), ("Growl", 1), ("Leer", 1), ("Fury Attack", 1),
        ("Aerial Ace", 13), ("Pursuit", 17),
        ("Assurance", 21), ("Mirror Move", 25),
        ("Agility", 29), ("Drill Peck", 33),
        ("Roost", 37),
    ],

    # ── SERPENTS ──────────────────────────────────────────────────────────────

    "Ekans": [
        ("Wrap", 1), ("Leer", 1),
        ("Poison Sting", 5), ("Bite", 9),
        ("Glare", 13), ("Screech", 17),
        ("Acid", 21), ("Crunch", 25),
        ("Stockpile", 29), ("Swallow", 29), ("Spit Up", 29),
        ("Sludge Bomb", 33), ("Coil", 37),
        ("Haze", 41), ("Gunk Shot", 45),
    ],
    "Arbok": [
        ("Wrap", 1), ("Leer", 1), ("Poison Sting", 1), ("Bite", 1),
        ("Glare", 13), ("Screech", 17),
        ("Acid", 21), ("Crunch", 25),
        ("Stockpile", 29), ("Swallow", 29), ("Spit Up", 29),
        ("Sludge Bomb", 33), ("Coil", 38),
        ("Haze", 43), ("Gunk Shot", 48),
    ],

    # ── PIKACHU / RAICHU ──────────────────────────────────────────────────────

    "Pikachu": [
        ("Thunder Shock", 1), ("Tail Whip", 1),
        ("Growl", 4), ("Play Nice", 6),
        ("Quick Attack", 8), ("Electro Ball", 11),
        ("Thunder Wave", 14), ("Feint", 17),
        ("Spark", 20), ("Nuzzle", 23),
        ("Double Team", 26), ("Slam", 29),
        ("Thunderbolt", 33), ("Discharge", 37),
        ("Light Screen", 41), ("Thunder", 45),
        ("Wild Charge", 49), ("Volt Tackle", 53),
    ],
    "Raichu": [
        ("Thunderbolt", 1), ("Quick Attack", 1), ("Nuzzle", 1),
        ("Thunder Wave", 1), ("Tail Whip", 1),
        ("Slam", 1), ("Thunder", 1),
        ("Wild Charge", 1), ("Volt Tackle", 1),
        ("Agility", 1), ("Discharge", 1),
    ],

    # ── SANDSHREW / SANDSLASH ─────────────────────────────────────────────────

    "Sandshrew": [
        ("Scratch", 1), ("Defense Curl", 1),
        ("Sand Attack", 4), ("Rapid Spin", 8),
        ("Poison Sting", 12), ("Rollout", 16),
        ("Swift", 20), ("Fury Swipes", 24),
        ("Slash", 28), ("Crush Claw", 32),
        ("Sand Tomb", 36), ("Earthquake", 40),
        ("Swords Dance", 44),
    ],
    "Sandslash": [
        ("Scratch", 1), ("Defense Curl", 1), ("Sand Attack", 1), ("Rapid Spin", 1),
        ("Poison Sting", 12), ("Rollout", 16),
        ("Swift", 20), ("Fury Swipes", 24),
        ("Slash", 29), ("Crush Claw", 34),
        ("Sand Tomb", 39), ("Earthquake", 44),
        ("Swords Dance", 49), ("Stone Edge", 54),
    ],

    # ── NIDORAN ───────────────────────────────────────────────────────────────

    "Nidoran♀": [
        ("Growl", 1), ("Scratch", 1),
        ("Tail Whip", 5), ("Double Kick", 9),
        ("Poison Sting", 13), ("Bite", 17),
        ("Helping Hand", 20), ("Fury Swipes", 23),
        ("Flatter", 27), ("Crunch", 31),
        ("Captivate", 35), ("Poison Fang", 38),
        ("Superpower", 43),
    ],
    "Nidorina": [
        ("Growl", 1), ("Scratch", 1), ("Tail Whip", 1), ("Double Kick", 1),
        ("Poison Sting", 13), ("Bite", 17),
        ("Helping Hand", 20), ("Fury Swipes", 23),
        ("Flatter", 27), ("Crunch", 31),
        ("Captivate", 35), ("Poison Fang", 38),
        ("Superpower", 43),
    ],
    "Nidoqueen": [
        ("Scratch", 1), ("Tail Whip", 1), ("Double Kick", 1), ("Poison Sting", 1),
        ("Bite", 1), ("Superpower", 1),
        ("Crunch", 23), ("Poison Fang", 28),
        ("Earth Power", 32), ("Flatter", 36),
        ("Captivate", 41), ("Earthquake", 46),
        ("Scary Face", 51),
    ],
    "Nidoran♂": [
        ("Leer", 1), ("Peck", 1),
        ("Focus Energy", 5), ("Double Kick", 9),
        ("Poison Sting", 13), ("Headbutt", 17),
        ("Helping Hand", 20), ("Fury Attack", 23),
        ("Flatter", 27), ("Horn Drill", 31),
        ("Captivate", 35), ("Poison Jab", 38),
        ("Superpower", 43),
    ],
    "Nidorino": [
        ("Leer", 1), ("Peck", 1), ("Focus Energy", 1), ("Double Kick", 1),
        ("Poison Sting", 13), ("Headbutt", 17),
        ("Helping Hand", 20), ("Fury Attack", 23),
        ("Flatter", 27), ("Horn Drill", 31),
        ("Captivate", 35), ("Poison Jab", 38),
        ("Superpower", 43),
    ],
    "Nidoking": [
        ("Peck", 1), ("Leer", 1), ("Focus Energy", 1), ("Double Kick", 1),
        ("Poison Sting", 1), ("Superpower", 1),
        ("Poison Jab", 23), ("Thrash", 28),
        ("Earth Power", 32), ("Flatter", 36),
        ("Captivate", 41), ("Earthquake", 46),
        ("Megahorn", 51),
    ],

    # ── FÉES LUNAIRES ─────────────────────────────────────────────────────────

    "Clefairy": [
        ("Pound", 1), ("Growl", 1),
        ("Encore", 5), ("Sing", 9),
        ("Double Slap", 13), ("Defense Curl", 17),
        ("Follow Me", 21), ("Bestow", 25),
        ("Body Slam", 29), ("Metronome", 33),
        ("Moonblast", 37), ("Cosmic Power", 41),
        ("Stored Power", 45), ("Moonlight", 49),
        ("Healing Wish", 53),
    ],
    "Clefable": [
        ("Pound", 1), ("Growl", 1), ("Sing", 1), ("Encore", 1),
        ("Metronome", 1), ("Body Slam", 1),
        ("Moonblast", 37), ("Cosmic Power", 41),
        ("Stored Power", 45), ("Moonlight", 49),
        ("Healing Wish", 53), ("Dazzling Gleam", 55),
    ],

    # ── RENARDS FEU ───────────────────────────────────────────────────────────

    "Vulpix": [
        ("Ember", 1), ("Tail Whip", 1),
        ("Roar", 5), ("Quick Attack", 9),
        ("Hex", 13), ("Will-O-Wisp", 17),
        ("Confuse Ray", 21), ("Payback", 25),
        ("Flamethrower", 29), ("Imprison", 33),
        ("Fire Spin", 37), ("Safeguard", 41),
        ("Inferno", 45), ("Grudge", 49),
        ("Fire Blast", 53),
    ],
    "Ninetales": [
        ("Ember", 1), ("Tail Whip", 1), ("Quick Attack", 1), ("Hex", 1),
        ("Will-O-Wisp", 17), ("Confuse Ray", 21),
        ("Payback", 25), ("Flamethrower", 29),
        ("Imprison", 33), ("Safeguard", 38),
        ("Extrasensory", 43), ("Fire Blast", 48),
        ("Nasty Plot", 53),
    ],

    # ── GONFLABLES ────────────────────────────────────────────────────────────

    "Jigglypuff": [
        ("Sing", 1), ("Defense Curl", 1),
        ("Pound", 5), ("Play Nice", 9),
        ("Disarming Voice", 13), ("Round", 17),
        ("Rollout", 21), ("Double Slap", 25),
        ("Rest", 29), ("Body Slam", 33),
        ("Gyro Ball", 37), ("Wake-Up Slap", 41),
        ("Hyper Voice", 45), ("Moonblast", 49),
        ("Last Resort", 53),
    ],
    "Wigglytuff": [
        ("Sing", 1), ("Defense Curl", 1), ("Pound", 1), ("Disarming Voice", 1),
        ("Double Slap", 1), ("Body Slam", 1),
        ("Hyper Voice", 45), ("Moonblast", 49),
        ("Dazzling Gleam", 55), ("Stored Power", 60),
    ],

    # ── CHAUVES-SOURIS ────────────────────────────────────────────────────────

    "Zubat": [
        ("Leech Life", 1), ("Supersonic", 1),
        ("Astonish", 5), ("Bite", 9),
        ("Wing Attack", 13), ("Confuse Ray", 17),
        ("Swift", 21), ("Air Cutter", 25),
        ("Poison Fang", 29), ("Mean Look", 33),
        ("Acrobatics", 37), ("Haze", 41),
        ("Air Slash", 45),
    ],
    "Golbat": [
        ("Leech Life", 1), ("Supersonic", 1), ("Astonish", 1), ("Bite", 1),
        ("Wing Attack", 13), ("Confuse Ray", 17),
        ("Swift", 21), ("Air Cutter", 25),
        ("Poison Fang", 29), ("Mean Look", 33),
        ("Acrobatics", 38), ("Haze", 43),
        ("Air Slash", 48), ("Cross Poison", 53),
    ],

    # ── PLANTES ───────────────────────────────────────────────────────────────

    "Oddish": [
        ("Absorb", 1), ("Sweet Scent", 1),
        ("Poison Powder", 5), ("Sleep Powder", 9),
        ("Acid", 13), ("Lucky Chant", 17),
        ("Mega Drain", 21), ("Moonblast", 25),
        ("Giga Drain", 29), ("Petal Blizzard", 33),
    ],
    "Gloom": [
        ("Absorb", 1), ("Sweet Scent", 1), ("Poison Powder", 1), ("Sleep Powder", 1),
        ("Acid", 13), ("Lucky Chant", 17),
        ("Mega Drain", 21), ("Moonblast", 25),
        ("Giga Drain", 29), ("Petal Blizzard", 33),
        ("Petal Dance", 40),
    ],
    "Vileplume": [
        ("Absorb", 1), ("Sweet Scent", 1), ("Poison Powder", 1), ("Sleep Powder", 1),
        ("Petal Dance", 1),
        ("Petal Blizzard", 33), ("Moonblast", 36),
        ("Giga Drain", 40), ("Aromatherapy", 44),
        ("Solar Beam", 48),
    ],

    # ── PARASITES ─────────────────────────────────────────────────────────────

    "Paras": [
        ("Scratch", 1), ("Stun Spore", 1),
        ("Absorb", 5), ("Poison Powder", 9),
        ("Leech Life", 13), ("Slash", 17),
        ("Growth", 21), ("Giga Drain", 25),
        ("Aromatherapy", 29), ("X-Scissor", 33),
        ("Spore", 37), ("Rage Powder", 41),
    ],
    "Parasect": [
        ("Scratch", 1), ("Stun Spore", 1), ("Absorb", 1), ("Leech Life", 1),
        ("Slash", 17), ("Growth", 21),
        ("Giga Drain", 25), ("Aromatherapy", 29),
        ("X-Scissor", 33), ("Spore", 38),
        ("Rage Powder", 43),
    ],

    # ── INSECTES ──────────────────────────────────────────────────────────────

    "Venonat": [
        ("Tackle", 1), ("Foresight", 1),
        ("Supersonic", 5), ("Confusion", 9),
        ("Poison Powder", 13), ("Leech Life", 17),
        ("Stun Spore", 21), ("Psybeam", 25),
        ("Sleep Powder", 29), ("Signal Beam", 33),
        ("Zen Headbutt", 37), ("Bug Buzz", 41),
    ],
    "Venomoth": [
        ("Tackle", 1), ("Foresight", 1), ("Supersonic", 1), ("Confusion", 1),
        ("Poison Powder", 13), ("Leech Life", 17),
        ("Stun Spore", 21), ("Psybeam", 25),
        ("Sleep Powder", 29), ("Signal Beam", 34),
        ("Quiver Dance", 38), ("Bug Buzz", 43),
    ],

    # ── TAUPES ────────────────────────────────────────────────────────────────

    "Diglett": [
        ("Scratch", 1), ("Sand Attack", 1),
        ("Growl", 4), ("Astonish", 7),
        ("Mud-Slap", 10), ("Magnitude", 13),
        ("Bulldoze", 16), ("Sucker Punch", 19),
        ("Mud Shot", 22), ("Slash", 25),
        ("Dig", 28), ("Fissure", 31),
        ("Earthquake", 34),
    ],
    "Dugtrio": [
        ("Scratch", 1), ("Sand Attack", 1), ("Growl", 1), ("Astonish", 1),
        ("Mud-Slap", 10), ("Magnitude", 13),
        ("Bulldoze", 16), ("Sucker Punch", 19),
        ("Mud Shot", 22), ("Slash", 26),
        ("Dig", 30), ("Fissure", 35),
        ("Earthquake", 40), ("Earth Power", 45),
        ("Stone Edge", 50),
    ],

    # ── CHATS ─────────────────────────────────────────────────────────────────

    "Meowth": [
        ("Scratch", 1), ("Growl", 1),
        ("Bite", 5), ("Pay Day", 9),
        ("Screech", 13), ("Fury Swipes", 17),
        ("Fake Out", 21), ("Assurance", 25),
        ("Swift", 29), ("Night Slash", 33),
        ("Snatch", 37), ("Slash", 41),
        ("Nasty Plot", 45),
    ],
    "Persian": [
        ("Scratch", 1), ("Growl", 1), ("Bite", 1), ("Pay Day", 1),
        ("Screech", 13), ("Fury Swipes", 17),
        ("Fake Out", 21), ("Assurance", 26),
        ("Swift", 31), ("Night Slash", 36),
        ("Snatch", 41), ("Slash", 46),
        ("Nasty Plot", 51), ("Power Gem", 56),
    ],

    # ── CANARDS ───────────────────────────────────────────────────────────────

    "Psyduck": [
        ("Scratch", 1), ("Tail Whip", 1),
        ("Water Sport", 5), ("Confusion", 9),
        ("Disable", 13), ("Water Pulse", 17),
        ("Screech", 21), ("Psych Up", 25),
        ("Zen Headbutt", 29), ("Aqua Tail", 33),
        ("Amnesia", 37), ("Hydro Pump", 41),
        ("Psychic", 45),
    ],
    "Golduck": [
        ("Scratch", 1), ("Tail Whip", 1), ("Confusion", 1), ("Disable", 1),
        ("Water Pulse", 17), ("Screech", 21),
        ("Psych Up", 25), ("Zen Headbutt", 29),
        ("Aqua Tail", 33), ("Amnesia", 38),
        ("Hydro Pump", 43), ("Psychic", 48),
        ("Calm Mind", 53),
    ],

    # ── SINGES ────────────────────────────────────────────────────────────────

    "Mankey": [
        ("Scratch", 1), ("Leer", 1),
        ("Low Kick", 5), ("Fury Swipes", 9),
        ("Karate Chop", 13), ("Screech", 17),
        ("Seismic Toss", 21), ("Assurance", 25),
        ("Thrash", 29), ("Cross Chop", 33),
        ("Punishment", 37), ("Close Combat", 41),
        ("Swagger", 45),
    ],
    "Primeape": [
        ("Scratch", 1), ("Leer", 1), ("Low Kick", 1), ("Fury Swipes", 1),
        ("Karate Chop", 13), ("Screech", 17),
        ("Seismic Toss", 21), ("Assurance", 25),
        ("Thrash", 29), ("Cross Chop", 34),
        ("Punishment", 39), ("Close Combat", 44),
        ("Swagger", 49), ("Rage Fist", 55),
    ],

    # ── CANINS FEU ────────────────────────────────────────────────────────────

    "Growlithe": [
        ("Bite", 1), ("Roar", 1),
        ("Ember", 5), ("Leer", 9),
        ("Odor Sleuth", 13), ("Fire Fang", 17),
        ("Flame Wheel", 21), ("Helping Hand", 25),
        ("Reversal", 29), ("Flamethrower", 33),
        ("Agility", 37), ("Crunch", 41),
        ("Flare Blitz", 45),
    ],
    "Arcanine": [
        ("Bite", 1), ("Roar", 1), ("Ember", 1), ("Leer", 1),
        ("Fire Fang", 17), ("Flame Wheel", 21),
        ("Helping Hand", 25), ("Extremespeed", 34),
        ("Flamethrower", 39), ("Agility", 44),
        ("Crunch", 49), ("Flare Blitz", 54),
    ],

    # ── POLIWAG ───────────────────────────────────────────────────────────────

    "Poliwag": [
        ("Water Sport", 1), ("Water Gun", 1),
        ("Hypnosis", 5), ("Bubble", 9),
        ("Double Slap", 13), ("Body Slam", 17),
        ("Bubble Beam", 21), ("Rain Dance", 25),
        ("Mud Shot", 29), ("Belly Drum", 33),
        ("Wake-Up Slap", 37), ("Hydro Pump", 41),
    ],
    "Poliwhirl": [
        ("Water Sport", 1), ("Water Gun", 1), ("Hypnosis", 1), ("Bubble", 1),
        ("Double Slap", 13), ("Body Slam", 17),
        ("Bubble Beam", 21), ("Rain Dance", 25),
        ("Mud Shot", 29), ("Belly Drum", 33),
        ("Wake-Up Slap", 38), ("Hydro Pump", 43),
        ("Amnesia", 48),
    ],
    "Poliwrath": [
        ("Water Sport", 1), ("Water Gun", 1), ("Hypnosis", 1), ("Bubble", 1),
        ("Body Slam", 1), ("Rain Dance", 1),
        ("Circle Throw", 36), ("Belly Drum", 40),
        ("Close Combat", 46), ("Dynamic Punch", 52),
        ("Hydro Pump", 58),
    ],

    # ── ABRA ──────────────────────────────────────────────────────────────────

    "Abra": [
        ("Teleport", 1),
    ],
    "Kadabra": [
        ("Teleport", 1), ("Kinesis", 1), ("Confusion", 1),
        ("Disable", 16), ("Psybeam", 18),
        ("Reflect", 22), ("Recover", 26),
        ("Psycho Cut", 30), ("Psychic", 34),
        ("Role Play", 38), ("Ally Switch", 42),
        ("Future Sight", 46), ("Trick", 50),
        ("Calm Mind", 54),
    ],
    "Alakazam": [
        ("Teleport", 1), ("Kinesis", 1), ("Confusion", 1), ("Disable", 1),
        ("Psybeam", 18), ("Reflect", 22),
        ("Recover", 26), ("Psycho Cut", 30),
        ("Psychic", 34), ("Role Play", 38),
        ("Ally Switch", 42), ("Future Sight", 47),
        ("Trick", 52), ("Calm Mind", 57),
        ("Dazzling Gleam", 62),
    ],

    # ── MACHOP ────────────────────────────────────────────────────────────────

    "Machop": [
        ("Low Kick", 1), ("Leer", 1),
        ("Focus Energy", 4), ("Karate Chop", 8),
        ("Foresight", 12), ("Seismic Toss", 16),
        ("Vital Throw", 20), ("Revenge", 24),
        ("Knock Off", 28), ("Submission", 32),
        ("Bulk Up", 36), ("Cross Chop", 40),
        ("Scary Face", 44), ("Dynamic Punch", 48),
        ("Close Combat", 52),
    ],
    "Machoke": [
        ("Low Kick", 1), ("Leer", 1), ("Focus Energy", 1), ("Karate Chop", 1),
        ("Foresight", 12), ("Seismic Toss", 16),
        ("Vital Throw", 20), ("Revenge", 24),
        ("Knock Off", 28), ("Submission", 32),
        ("Bulk Up", 36), ("Cross Chop", 41),
        ("Scary Face", 46), ("Dynamic Punch", 51),
        ("Close Combat", 56),
    ],
    "Machamp": [
        ("Low Kick", 1), ("Leer", 1), ("Focus Energy", 1), ("Karate Chop", 1),
        ("Seismic Toss", 1), ("Submission", 1),
        ("Bulk Up", 36), ("Cross Chop", 41),
        ("Scary Face", 46), ("Dynamic Punch", 51),
        ("Close Combat", 56), ("Superpower", 62),
    ],

    # ── BELLSPROUT ────────────────────────────────────────────────────────────

    "Bellsprout": [
        ("Vine Whip", 1), ("Growth", 1),
        ("Wrap", 5), ("Sleep Powder", 9),
        ("Poison Powder", 13), ("Razor Leaf", 17),
        ("Acid", 21), ("Sweet Scent", 25),
        ("Stockpile", 29), ("Swallow", 29), ("Spit Up", 29),
        ("Knock Off", 33), ("Gastro Acid", 37),
        ("Weather Ball", 41), ("Solar Beam", 45),
        ("Leaf Storm", 49),
    ],
    "Weepinbell": [
        ("Vine Whip", 1), ("Growth", 1), ("Wrap", 1), ("Sleep Powder", 1),
        ("Poison Powder", 13), ("Razor Leaf", 17),
        ("Acid", 21), ("Sweet Scent", 25),
        ("Stockpile", 29), ("Swallow", 29), ("Spit Up", 29),
        ("Knock Off", 33), ("Gastro Acid", 38),
        ("Weather Ball", 43), ("Solar Beam", 48),
        ("Leaf Storm", 53),
    ],
    "Victreebel": [
        ("Vine Whip", 1), ("Growth", 1), ("Wrap", 1), ("Sleep Powder", 1),
        ("Razor Leaf", 1), ("Acid", 1),
        ("Leaf Storm", 1), ("Weather Ball", 1),
        ("Giga Drain", 44), ("Belch", 48),
        ("Solar Beam", 53), ("Leaf Blade", 58),
    ],

    # ── TENTACOOL ─────────────────────────────────────────────────────────────

    "Tentacool": [
        ("Poison Sting", 1), ("Water Sport", 1),
        ("Water Gun", 5), ("Wrap", 9),
        ("Acid", 13), ("Toxic Spikes", 17),
        ("Bubble Beam", 21), ("Poison Jab", 25),
        ("Screech", 29), ("Hex", 33),
        ("Sludge Bomb", 37), ("Barrier", 41),
        ("Hydro Pump", 45),
    ],
    "Tentacruel": [
        ("Poison Sting", 1), ("Water Sport", 1), ("Water Gun", 1), ("Wrap", 1),
        ("Acid", 13), ("Toxic Spikes", 17),
        ("Bubble Beam", 21), ("Poison Jab", 25),
        ("Screech", 29), ("Hex", 33),
        ("Sludge Bomb", 38), ("Barrier", 43),
        ("Hydro Pump", 48), ("Acid Spray", 53),
        ("Clear Smog", 58),
    ],

    # ── ROCHERS ───────────────────────────────────────────────────────────────

    "Geodude": [
        ("Tackle", 1), ("Defense Curl", 1),
        ("Mud Sport", 5), ("Rock Polish", 9),
        ("Rock Throw", 13), ("Magnitude", 17),
        ("Smack Down", 21), ("Bulldoze", 25),
        ("Stealth Rock", 29), ("Rock Slide", 33),
        ("Self-Destruct", 37), ("Earthquake", 41),
        ("Stone Edge", 45), ("Double-Edge", 49),
        ("Explosion", 53),
    ],
    "Graveler": [
        ("Tackle", 1), ("Defense Curl", 1), ("Mud Sport", 1), ("Rock Polish", 1),
        ("Rock Throw", 13), ("Magnitude", 17),
        ("Smack Down", 21), ("Bulldoze", 25),
        ("Stealth Rock", 29), ("Rock Slide", 33),
        ("Self-Destruct", 38), ("Earthquake", 43),
        ("Stone Edge", 48), ("Double-Edge", 53),
        ("Explosion", 58),
    ],
    "Golem": [
        ("Tackle", 1), ("Defense Curl", 1), ("Rock Throw", 1), ("Magnitude", 1),
        ("Bulldoze", 1), ("Stealth Rock", 1),
        ("Rock Slide", 33), ("Self-Destruct", 38),
        ("Earthquake", 43), ("Stone Edge", 49),
        ("Heavy Slam", 55), ("Explosion", 62),
    ],

    # ── PONYTA ────────────────────────────────────────────────────────────────

    "Ponyta": [
        ("Tackle", 1), ("Growl", 1),
        ("Flame Wheel", 4), ("Tail Whip", 7),
        ("Ember", 10), ("Stomp", 14),
        ("Flame Charge", 18), ("Fire Fang", 22),
        ("Take Down", 26), ("Agility", 30),
        ("Flamethrower", 34), ("Bounce", 38),
        ("Flare Blitz", 42),
    ],
    "Rapidash": [
        ("Tackle", 1), ("Growl", 1), ("Flame Wheel", 1), ("Tail Whip", 1),
        ("Ember", 10), ("Stomp", 14),
        ("Flame Charge", 18), ("Fire Fang", 22),
        ("Take Down", 26), ("Agility", 30),
        ("Flamethrower", 35), ("Bounce", 40),
        ("Flare Blitz", 46), ("Megahorn", 52),
    ],

    # ── SLOWPOKE ──────────────────────────────────────────────────────────────

    "Slowpoke": [
        ("Curse", 1), ("Tackle", 1),
        ("Yawn", 4), ("Growl", 7),
        ("Water Gun", 10), ("Confusion", 14),
        ("Disable", 18), ("Headbutt", 22),
        ("Water Pulse", 26), ("Zen Headbutt", 30),
        ("Amnesia", 34), ("Psychic", 38),
        ("Rain Dance", 42), ("Psych Up", 46),
        ("Slack Off", 50),
    ],
    "Slowbro": [
        ("Curse", 1), ("Tackle", 1), ("Yawn", 1), ("Growl", 1),
        ("Water Gun", 10), ("Confusion", 14),
        ("Disable", 18), ("Headbutt", 22),
        ("Water Pulse", 26), ("Zen Headbutt", 30),
        ("Amnesia", 35), ("Psychic", 40),
        ("Rain Dance", 45), ("Psych Up", 50),
        ("Slack Off", 55), ("Scald", 60),
    ],

    # ── MAGNÉTIQUES ───────────────────────────────────────────────────────────

    "Magnemite": [
        ("Metal Sound", 1), ("Tackle", 1),
        ("Supersonic", 5), ("Thunder Shock", 9),
        ("Charge Beam", 13), ("Thunder Wave", 17),
        ("Magnet Bomb", 21), ("Volt Switch", 25),
        ("Electroweb", 29), ("Discharge", 33),
        ("Flash Cannon", 37), ("Mirror Coat", 41),
        ("Zap Cannon", 45), ("Magnet Rise", 49),
    ],
    "Magneton": [
        ("Metal Sound", 1), ("Tackle", 1), ("Supersonic", 1), ("Thunder Shock", 1),
        ("Charge Beam", 13), ("Thunder Wave", 17),
        ("Magnet Bomb", 21), ("Volt Switch", 25),
        ("Electroweb", 29), ("Discharge", 33),
        ("Flash Cannon", 38), ("Mirror Coat", 43),
        ("Zap Cannon", 48), ("Magnet Rise", 53),
    ],

    # ── OISEAUX ───────────────────────────────────────────────────────────────

    "Farfetch'd": [
        ("Peck", 1), ("Sand Attack", 1),
        ("Leer", 5), ("Fury Cutter", 9),
        ("Fury Attack", 13), ("Aerial Ace", 17),
        ("Knock Off", 21), ("Swords Dance", 25),
        ("Air Cutter", 29), ("Slash", 33),
        ("Leaf Blade", 37), ("Air Slash", 41),
        ("Night Slash", 45), ("Brave Bird", 49),
    ],
    "Doduo": [
        ("Peck", 1), ("Growl", 1),
        ("Quick Attack", 5), ("Fury Attack", 9),
        ("Pursuit", 13), ("Pluck", 17),
        ("Double Hit", 21), ("Agility", 25),
        ("Acupressure", 29), ("Drill Peck", 33),
        ("Uproar", 37),
    ],
    "Dodrio": [
        ("Peck", 1), ("Growl", 1), ("Quick Attack", 1), ("Fury Attack", 1),
        ("Pursuit", 13), ("Pluck", 17),
        ("Double Hit", 21), ("Agility", 25),
        ("Acupressure", 29), ("Drill Peck", 33),
        ("Brave Bird", 38), ("Thrash", 43),
        ("Uproar", 48),
    ],

    # ── PHOQUES / COQUILLAGES ─────────────────────────────────────────────────

    "Seel": [
        ("Headbutt", 1), ("Growl", 1),
        ("Water Sport", 5), ("Icy Wind", 9),
        ("Encore", 13), ("Ice Shard", 17),
        ("Rest", 21), ("Aurora Beam", 25),
        ("Aqua Jet", 29), ("Safeguard", 33),
        ("Aqua Tail", 37), ("Sheer Cold", 41),
        ("Blizzard", 45), ("Hail", 49),
    ],
    "Dewgong": [
        ("Headbutt", 1), ("Growl", 1), ("Water Sport", 1), ("Icy Wind", 1),
        ("Encore", 13), ("Ice Shard", 17),
        ("Rest", 21), ("Aurora Beam", 25),
        ("Aqua Jet", 29), ("Safeguard", 33),
        ("Aqua Tail", 38), ("Sheer Cold", 43),
        ("Blizzard", 48), ("Hail", 53),
        ("Ice Beam", 58),
    ],

    "Shellder": [
        ("Tackle", 1), ("Water Gun", 1),
        ("Withdraw", 5), ("Icicle Spear", 9),
        ("Leer", 13), ("Razor Shell", 17),
        ("Ice Shard", 21), ("Aurora Beam", 25),
        ("Whirlpool", 29), ("Brine", 33),
        ("Iron Defense", 37), ("Clamp", 41),
        ("Ice Beam", 45), ("Shell Smash", 49),
        ("Blizzard", 53),
    ],
    "Cloyster": [
        ("Tackle", 1), ("Water Gun", 1), ("Withdraw", 1), ("Icicle Spear", 1),
        ("Toxic Spikes", 1), ("Spikes", 1),
        ("Razor Shell", 17), ("Ice Shard", 21),
        ("Aurora Beam", 25), ("Iron Defense", 38),
        ("Clamp", 43), ("Ice Beam", 48),
        ("Shell Smash", 53), ("Icicle Crash", 58),
        ("Blizzard", 63),
    ],

    # ── FANTÔMES ──────────────────────────────────────────────────────────────

    "Gastly": [
        ("Hypnosis", 1), ("Lick", 1),
        ("Spite", 5), ("Mean Look", 9),
        ("Curse", 13), ("Night Shade", 17),
        ("Confuse Ray", 21), ("Sucker Punch", 25),
        ("Payback", 29), ("Shadow Ball", 33),
        ("Dream Eater", 37), ("Destiny Bond", 41),
        ("Hex", 45), ("Nightmare", 49),
    ],
    "Haunter": [
        ("Hypnosis", 1), ("Lick", 1), ("Spite", 1), ("Mean Look", 1),
        ("Curse", 13), ("Night Shade", 17),
        ("Confuse Ray", 21), ("Sucker Punch", 25),
        ("Payback", 29), ("Shadow Ball", 33),
        ("Dream Eater", 38), ("Destiny Bond", 43),
        ("Hex", 48), ("Nightmare", 53),
        ("Shadow Punch", 58),
    ],
    "Gengar": [
        ("Hypnosis", 1), ("Lick", 1), ("Spite", 1), ("Mean Look", 1),
        ("Night Shade", 1), ("Shadow Ball", 1),
        ("Confuse Ray", 21), ("Sucker Punch", 25),
        ("Payback", 29), ("Dream Eater", 38),
        ("Destiny Bond", 43), ("Hex", 49),
        ("Dark Pulse", 55), ("Nightmare", 60),
        ("Shadow Ball", 65),
    ],

    # ── ONIX ──────────────────────────────────────────────────────────────────

    "Onix": [
        ("Tackle", 1), ("Bind", 1),
        ("Screech", 4), ("Rock Throw", 8),
        ("Rock Tomb", 12), ("Rage", 16),
        ("Stealth Rock", 20), ("Rock Slide", 24),
        ("Slam", 28), ("Iron Tail", 32),
        ("Sand Tomb", 36), ("Stone Edge", 40),
        ("Double-Edge", 44), ("Sandstorm", 48),
    ],

    # ── DROWZEE ───────────────────────────────────────────────────────────────

    "Drowzee": [
        ("Pound", 1), ("Hypnosis", 1),
        ("Disable", 5), ("Confusion", 9),
        ("Headbutt", 13), ("Poison Gas", 17),
        ("Meditate", 21), ("Psybeam", 25),
        ("Wake-Up Slap", 29), ("Psychic", 33),
        ("Zen Headbutt", 37), ("Psych Up", 41),
        ("Dream Eater", 45), ("Nasty Plot", 49),
    ],
    "Hypno": [
        ("Pound", 1), ("Hypnosis", 1), ("Disable", 1), ("Confusion", 1),
        ("Headbutt", 13), ("Poison Gas", 17),
        ("Meditate", 21), ("Psybeam", 25),
        ("Wake-Up Slap", 29), ("Psychic", 33),
        ("Zen Headbutt", 38), ("Psych Up", 43),
        ("Dream Eater", 48), ("Nasty Plot", 53),
        ("Future Sight", 58),
    ],

    # ── CRABES ────────────────────────────────────────────────────────────────

    "Krabby": [
        ("Mud Sport", 1), ("Bubble", 1),
        ("Vice Grip", 5), ("Leer", 9),
        ("Harden", 13), ("Bubble Beam", 17),
        ("Stomp", 21), ("Protect", 25),
        ("Knock Off", 29), ("Crabhammer", 33),
        ("Flail", 37), ("Slam", 41),
        ("Guillotine", 45),
    ],
    "Kingler": [
        ("Mud Sport", 1), ("Bubble", 1), ("Vice Grip", 1), ("Leer", 1),
        ("Harden", 13), ("Bubble Beam", 17),
        ("Stomp", 21), ("Protect", 25),
        ("Knock Off", 29), ("Crabhammer", 33),
        ("Flail", 38), ("Slam", 43),
        ("X-Scissor", 48), ("Guillotine", 53),
    ],

    # ── VOLTORB ───────────────────────────────────────────────────────────────

    "Voltorb": [
        ("Tackle", 1), ("Charge",  1),
        ("Thunder Shock", 4), ("Sonic Boom", 7),
        ("Electroweb", 10), ("Spark", 14),
        ("Rollout", 18), ("Screech", 22),
        ("Charge Beam", 26), ("Discharge", 30),
        ("Self-Destruct", 34), ("Thunder Wave", 38),
        ("Mirror Coat", 42), ("Thunderbolt", 46),
        ("Thunder", 50), ("Explosion", 54),
    ],
    "Electrode": [
        ("Tackle", 1), ("Charge", 1), ("Thunder Shock", 1), ("Sonic Boom", 1),
        ("Electroweb", 10), ("Spark", 14),
        ("Rollout", 18), ("Screech", 22),
        ("Charge Beam", 26), ("Discharge", 30),
        ("Self-Destruct", 35), ("Thunder Wave", 40),
        ("Mirror Coat", 45), ("Thunderbolt", 50),
        ("Thunder", 55), ("Explosion", 60),
    ],

    # ── EXEGGCUTE ─────────────────────────────────────────────────────────────

    "Exeggcute": [
        ("Barrage", 1), ("Uproar", 1),
        ("Hypnosis", 5), ("Reflect", 9),
        ("Leech Seed", 13), ("Bullet Seed", 17),
        ("Stun Spore", 21), ("Poison Powder", 21),
        ("Sleep Powder", 21), ("Confusion", 25),
        ("Worry Seed", 29), ("Natural Gift", 33),
        ("Solar Beam", 37), ("Bestow", 41),
    ],
    "Exeggutor": [
        ("Barrage", 1), ("Hypnosis", 1), ("Confusion", 1), ("Reflect", 1),
        ("Stomp", 33), ("Egg Bomb", 38),
        ("Wood Hammer", 43), ("Psychic", 48),
        ("Energy Ball", 53), ("Solar Beam", 58),
        ("Leaf Storm", 63),
    ],

    # ── CUBONE ────────────────────────────────────────────────────────────────

    "Cubone": [
        ("Growl", 1), ("Tackle", 1),
        ("Bone Club", 4), ("Headbutt", 7),
        ("Leer", 10), ("Bone Rush", 14),
        ("Focus Energy", 18), ("Bulldoze", 22),
        ("Thrash", 26), ("Stomping Tantrum", 30),
        ("Retaliate", 34), ("Earthquake", 38),
        ("Swords Dance", 42), ("Bonemerang", 46),
        ("Double-Edge", 50),
    ],
    "Marowak": [
        ("Growl", 1), ("Tackle", 1), ("Bone Club", 1), ("Headbutt", 1),
        ("Leer", 10), ("Bone Rush", 14),
        ("Focus Energy", 18), ("Bulldoze", 22),
        ("Thrash", 26), ("Stomping Tantrum", 30),
        ("Retaliate", 35), ("Earthquake", 40),
        ("Swords Dance", 45), ("Bonemerang", 50),
        ("Double-Edge", 55), ("Stone Edge", 60),
    ],

    # ── LUCHEURS ──────────────────────────────────────────────────────────────

    "Hitmonlee": [
        ("Double Kick", 1), ("Meditate", 1),
        ("Rolling Kick", 6), ("Jump Kick", 10),
        ("Brick Break", 15), ("Focus Energy", 21),
        ("Feint", 26), ("Hi Jump Kick", 31),
        ("Mind Reader", 36), ("Wide Guard", 41),
        ("Blaze Kick", 46), ("Endure", 51),
        ("Mega Kick", 56), ("Close Combat", 61),
    ],
    "Hitmonchan": [
        ("Jab", 1), ("Meditate", 1),
        ("Comet Punch", 6), ("Agility", 10),
        ("Pursuit", 15), ("Mach Punch", 21),
        ("Bullet Punch", 26), ("Feint", 31),
        ("Sky Uppercut", 36), ("Counter", 41),
        ("Focus Punch", 46), ("Thunder Punch", 51),
        ("Ice Punch", 56), ("Fire Punch", 61),
        ("Close Combat", 66),
    ],

    # ── LIPOUTOU ──────────────────────────────────────────────────────────────

    "Lickitung": [
        ("Lick", 1), ("Growl", 1),
        ("Supersonic", 5), ("Defense Curl", 9),
        ("Knock Off", 13), ("Wrap", 17),
        ("Stomp", 21), ("Disable", 25),
        ("Slam", 29), ("Rollout", 33),
        ("Body Slam", 37), ("Me First", 41),
        ("Screech", 45), ("Power Whip", 49),
        ("Hyper Beam", 53),
    ],

    # ── GAZ TOXIQUES ──────────────────────────────────────────────────────────

    "Koffing": [
        ("Poison Gas", 1), ("Tackle", 1),
        ("Smog", 4), ("Smokescreen", 7),
        ("Assurance", 10), ("Gyro Ball", 14),
        ("Sludge", 18), ("Explosion", 22),
        ("Haze", 26), ("Destiny Bond", 30),
        ("Belch", 34), ("Pain Split", 38),
        ("Sludge Bomb", 42), ("Self-Destruct", 46),
        ("Memento", 50),
    ],
    "Weezing": [
        ("Poison Gas", 1), ("Tackle", 1), ("Smog", 1), ("Smokescreen", 1),
        ("Assurance", 10), ("Gyro Ball", 14),
        ("Sludge", 18), ("Explosion", 22),
        ("Haze", 26), ("Destiny Bond", 30),
        ("Belch", 35), ("Pain Split", 40),
        ("Sludge Bomb", 45), ("Self-Destruct", 50),
        ("Memento", 55), ("Strange Steam", 60),
    ],

    # ── RHINOCÉROS ────────────────────────────────────────────────────────────

    "Rhyhorn": [
        ("Horn Attack", 1), ("Tail Whip", 1),
        ("Fury Attack", 5), ("Scary Face", 9),
        ("Bulldoze", 13), ("Stomp", 17),
        ("Rock Blast", 21), ("Chip Away", 25),
        ("Take Down", 29), ("Stealth Rock", 33),
        ("Rock Slide", 37), ("Drill Run", 41),
        ("Stone Edge", 45), ("Earthquake", 49),
        ("Horn Drill", 53),
    ],
    "Rhydon": [
        ("Horn Attack", 1), ("Tail Whip", 1), ("Fury Attack", 1), ("Scary Face", 1),
        ("Bulldoze", 13), ("Stomp", 17),
        ("Rock Blast", 21), ("Chip Away", 25),
        ("Take Down", 29), ("Stealth Rock", 33),
        ("Rock Slide", 38), ("Drill Run", 43),
        ("Stone Edge", 48), ("Earthquake", 53),
        ("Megahorn", 58), ("Horn Drill", 63),
    ],

    # ── KANGASKHAN ────────────────────────────────────────────────────────────

    "Kangaskhan": [
        ("Comet Punch", 1), ("Leer", 1),
        ("Fake Out", 4), ("Tail Whip", 7),
        ("Bite", 10), ("Double Slap", 13),
        ("Headbutt", 17), ("Dizzy Punch", 21),
        ("Mega Punch", 25), ("Whirlwind", 29),
        ("Sucker Punch", 33), ("Crunch", 37),
        ("Outrage", 41), ("Reversal", 45),
        ("Stomp", 49), ("Hyper Voice", 53),
    ],

    # ── HIPPOCAMPES ───────────────────────────────────────────────────────────

    "Horsea": [
        ("Water Gun", 1), ("Leer", 1),
        ("Bubble", 5), ("Smokescreen", 9),
        ("Focus Energy", 13), ("Bubble Beam", 17),
        ("Agility", 21), ("Dragon Breath", 25),
        ("Brine", 29), ("Twister", 33),
        ("Hydro Pump", 37), ("Dragon Dance", 41),
    ],
    "Seadra": [
        ("Water Gun", 1), ("Leer", 1), ("Bubble", 1), ("Smokescreen", 1),
        ("Focus Energy", 13), ("Bubble Beam", 17),
        ("Agility", 21), ("Dragon Breath", 25),
        ("Brine", 29), ("Twister", 33),
        ("Hydro Pump", 38), ("Dragon Dance", 43),
        ("Dragon Pulse", 48),
    ],

    # ── POISSONS ──────────────────────────────────────────────────────────────

    "Goldeen": [
        ("Peck", 1), ("Tail Whip", 1),
        ("Water Sport", 5), ("Supersonic", 9),
        ("Horn Attack", 13), ("Water Pulse", 17),
        ("Flail", 21), ("Fury Attack", 25),
        ("Aqua Tail", 29), ("Agility", 33),
        ("Soak", 37), ("Megahorn", 41),
        ("Liquidation", 45),
    ],
    "Seaking": [
        ("Peck", 1), ("Tail Whip", 1), ("Water Sport", 1), ("Supersonic", 1),
        ("Horn Attack", 13), ("Water Pulse", 17),
        ("Flail", 21), ("Fury Attack", 25),
        ("Aqua Tail", 29), ("Agility", 33),
        ("Soak", 38), ("Megahorn", 43),
        ("Liquidation", 48),
    ],

    "Staryu": [
        ("Tackle", 1), ("Water Gun", 1),
        ("Harden", 5), ("Rapid Spin", 9),
        ("Recover", 13), ("Psywave", 17),
        ("Minimize", 21), ("Confuse Ray", 25),
        ("Gyro Ball", 29), ("Cosmic Power", 33),
        ("Power Gem", 37), ("Hydro Pump", 41),
        ("Camouflage", 45), ("Swift", 49),
    ],
    "Starmie": [
        ("Tackle", 1), ("Water Gun", 1), ("Harden", 1), ("Rapid Spin", 1),
        ("Recover", 13), ("Confuse Ray", 25),
        ("Cosmic Power", 33), ("Power Gem", 38),
        ("Hydro Pump", 43), ("Psychic", 48),
        ("Thunder", 53),
    ],

    # ── MIME ──────────────────────────────────────────────────────────────────

    "Mr. Mime": [
        ("Confusion", 1), ("Copy Cat", 1),
        ("Tickle", 4), ("Encore", 7),
        ("Magical Leaf", 10), ("Meditate", 13),
        ("Light Screen", 17), ("Reflect", 21),
        ("Psybeam", 25), ("Mimic", 29),
        ("Substitute", 33), ("Baton Pass", 37),
        ("Recycle", 41), ("Dazzling Gleam", 45),
        ("Psychic", 49), ("Nasty Plot", 53),
        ("Psyshock", 57),
    ],

    # ── SCYTHER ───────────────────────────────────────────────────────────────

    "Scyther": [
        ("Vacuum Wave", 1), ("Quick Attack", 1),
        ("Leer", 5), ("Focus Energy", 9),
        ("Fury Cutter", 13), ("Wing Attack", 17),
        ("Slash", 21), ("Swords Dance", 25),
        ("Agility", 29), ("X-Scissor", 33),
        ("Night Slash", 37), ("Air Slash", 41),
        ("False Swipe", 45),
    ],

    # ── ÉLECTRIQUES ───────────────────────────────────────────────────────────

    "Jynx": [
        ("Pound", 1), ("Lick", 1),
        ("Sweet Kiss", 4), ("Powder Snow", 8),
        ("Confusion", 12), ("Fake Tears", 17),
        ("Ice Punch", 22), ("Mean Look", 27),
        ("Draining Kiss", 32), ("Psychic", 37),
        ("Lovely Kiss", 42), ("Blizzard", 47),
        ("Perish Song", 52),
    ],
    "Electabuzz": [
        ("Quick Attack", 1), ("Leer", 1),
        ("Thunder Shock", 4), ("Low Kick", 8),
        ("Swift", 12), ("Shock Wave", 17),
        ("Electroweb", 22), ("Thunder Punch", 27),
        ("Discharge", 32), ("Thunderbolt", 37),
        ("Light Screen", 42), ("Thunder Wave", 46),
        ("Thunder", 50),
    ],
    "Magmar": [
        ("Ember", 1), ("Leer", 1),
        ("Smog", 4), ("Faint Attack", 8),
        ("Fire Spin", 12), ("Smokescreen", 17),
        ("Flame Burst", 22), ("Fire Punch", 27),
        ("Lava Plume", 32), ("Flamethrower", 37),
        ("Sunny Day", 42), ("Fire Blast", 46),
        ("Flare Blitz", 50),
    ],

    # ── INSECTES ÉPINEUX ──────────────────────────────────────────────────────

    "Pinsir": [
        ("Vice Grip", 1), ("Focus Energy", 1),
        ("Bind", 5), ("Seismic Toss", 9),
        ("Harden", 13), ("Revenge", 17),
        ("X-Scissor", 21), ("Bug Bite", 25),
        ("Thrash", 29), ("Vital Throw", 33),
        ("Slash", 37), ("Submission", 41),
        ("Swords Dance", 45), ("Close Combat", 49),
        ("Guillotine", 53),
    ],

    # ── TAUROS ────────────────────────────────────────────────────────────────

    "Tauros": [
        ("Tackle", 1), ("Tail Whip", 1),
        ("Rage", 5), ("Horn Attack", 9),
        ("Scary Face", 13), ("Pursuit", 17),
        ("Payback", 21), ("Rest", 25),
        ("Work Up", 29), ("Take Down", 33),
        ("Zen Headbutt", 37), ("Swagger", 41),
        ("Thrash", 45), ("Double-Edge", 49),
        ("Giga Impact", 53),
    ],

    # ── MAGIKARP ──────────────────────────────────────────────────────────────

    "Magikarp": [
        ("Splash", 1), ("Tackle", 15),
        ("Flail", 25),
    ],
    "Gyarados": [
        ("Bite", 1), ("Dragon Rage", 1),
        ("Leer", 20), ("Twister", 25),
        ("Ice Fang", 29), ("Aqua Tail", 32),
        ("Dragon Dance", 35), ("Crunch", 38),
        ("Hyper Beam", 41), ("Rain Dance", 44),
        ("Hurricane", 47), ("Hydro Pump", 50),
        ("Outrage", 53),
    ],

    # ── LAPINS ────────────────────────────────────────────────────────────────

    "Lapras": [
        ("Water Gun", 1), ("Growl", 1),
        ("Sing", 5), ("Mist", 9),
        ("Confuse Ray", 13), ("Ice Shard", 17),
        ("Water Pulse", 21), ("Body Slam", 25),
        ("Rain Dance", 29), ("Perish Song", 33),
        ("Ice Beam", 37), ("Brine", 41),
        ("Safeguard", 45), ("Hydro Pump", 49),
        ("Sheer Cold", 53), ("Blizzard", 57),
    ],

    # ── MÉTAMORPH ─────────────────────────────────────────────────────────────

    "Ditto": [
        ("Transform", 1),
    ],

    # ── ÉVOLI ET ÉVOLUTIONS ───────────────────────────────────────────────────

    "Eevee": [
        ("Tackle", 1), ("Tail Whip", 1),
        ("Sand Attack", 5), ("Growl", 9),
        ("Quick Attack", 13), ("Bite", 17),
        ("Covet", 21), ("Take Down", 25),
        ("Charm", 29), ("Baton Pass", 33),
        ("Double-Edge", 37), ("Last Resort", 41),
        ("Trump Card", 45),
    ],
    "Vaporeon": [
        ("Tackle", 1), ("Tail Whip", 1), ("Sand Attack", 1), ("Water Gun", 1),
        ("Quick Attack", 13), ("Bite", 17),
        ("Aqua Ring", 23), ("Aurora Beam", 29),
        ("Aqua Tail", 36), ("Acid Armor", 42),
        ("Muddy Water", 48), ("Hydro Pump", 54),
        ("Last Resort", 60),
    ],
    "Jolteon": [
        ("Tackle", 1), ("Tail Whip", 1), ("Sand Attack", 1), ("Thunder Shock", 1),
        ("Quick Attack", 13), ("Bite", 17),
        ("Pin Missile", 23), ("Discharge", 29),
        ("Thunder Wave", 36), ("Agility", 42),
        ("Wild Charge", 48), ("Thunder", 54),
        ("Last Resort", 60),
    ],
    "Flareon": [
        ("Tackle", 1), ("Tail Whip", 1), ("Sand Attack", 1), ("Ember", 1),
        ("Quick Attack", 13), ("Bite", 17),
        ("Baby-Doll Eyes", 23), ("Flame Charge", 29),
        ("Flare Blitz", 36), ("Fire Spin", 42),
        ("Smog", 48), ("Flamethrower", 54),
        ("Last Resort", 60),
    ],

    # ── PORYGON ───────────────────────────────────────────────────────────────

    "Porygon": [
        ("Conversion", 1), ("Tackle", 1),
        ("Sharpen", 4), ("Psybeam", 8),
        ("Agility", 12), ("Conversion 2", 16),
        ("Recover", 20), ("Discharge", 24),
        ("Signal Beam", 28), ("Lock-On", 32),
        ("Tri Attack", 36), ("Ice Beam", 40),
        ("Zap Cannon", 44), ("Magic Coat", 48),
        ("Hyper Beam", 52),
    ],

    # ── FOSSILES ──────────────────────────────────────────────────────────────

    "Omanyte": [
        ("Withdraw", 1), ("Bind", 1),
        ("Water Gun", 7), ("Rollout", 13),
        ("Leer", 20), ("Mud Shot", 27),
        ("Protect", 33), ("Rock Blast", 40),
        ("Ancient Power", 47), ("Tickle", 54),
        ("Hydro Pump", 60), ("Stealth Rock", 66),
    ],
    "Omastar": [
        ("Withdraw", 1), ("Bind", 1), ("Water Gun", 1), ("Rollout", 1),
        ("Leer", 20), ("Mud Shot", 27),
        ("Protect", 33), ("Rock Blast", 40),
        ("Ancient Power", 47), ("Tickle", 54),
        ("Hydro Pump", 60), ("Stealth Rock", 66),
        ("Shell Smash", 72),
    ],
    "Kabuto": [
        ("Scratch", 1), ("Harden", 1),
        ("Absorb", 7), ("Leer", 13),
        ("Mud Shot", 20), ("Sand Attack", 27),
        ("Endure", 33), ("Ancient Power", 40),
        ("Aqua Jet", 47), ("X-Scissor", 54),
        ("Night Slash", 60),
    ],
    "Kabutops": [
        ("Scratch", 1), ("Harden", 1), ("Absorb", 1), ("Leer", 1),
        ("Mud Shot", 20), ("Sand Attack", 27),
        ("Endure", 33), ("Ancient Power", 40),
        ("Aqua Jet", 47), ("X-Scissor", 54),
        ("Night Slash", 60), ("Stone Edge", 66),
        ("Close Combat", 72),
    ],

    # ── AÉRODACTYLE ───────────────────────────────────────────────────────────

    "Aerodactyl": [
        ("Wing Attack", 1), ("Agility", 1),
        ("Bite", 9), ("Scary Face", 14),
        ("Supersonic", 19), ("Ancient Power", 24),
        ("Crunch", 29), ("Take Down", 34),
        ("Roost", 38), ("Iron Head", 42),
        ("Hyper Beam", 46), ("Rock Slide", 50),
        ("Giga Impact", 54), ("Stone Edge", 58),
    ],

    # ── RONFLEX ───────────────────────────────────────────────────────────────

    "Snorlax": [
        ("Tackle", 1), ("Defense Curl", 1),
        ("Amnesia", 4), ("Lick", 9),
        ("Chip Away", 14), ("Headbutt", 19),
        ("Rest", 24), ("Yawn", 29),
        ("Snore", 34), ("Belly Drum", 39),
        ("Block", 44), ("Rollout", 49),
        ("Heavy Slam", 54), ("Crunch", 59),
        ("Giga Impact", 64), ("Last Resort", 69),
    ],

    # ── OISEAUX LÉGENDAIRES ───────────────────────────────────────────────────

    "Articuno": [
        ("Powder Snow", 1), ("Mist", 1),
        ("Ice Shard", 7), ("Mind Reader", 13),
        ("Sheer Cold", 19), ("Reflect", 25),
        ("Ice Beam", 31), ("Hail", 37),
        ("Freeze-Dry", 43), ("Tailwind", 49),
        ("Ancient Power", 55), ("Blizzard", 61),
        ("Agility", 67), ("Hurricane", 73),
    ],
    "Zapdos": [
        ("Peck", 1), ("Thunder Shock", 1),
        ("Charge", 7), ("Thunder Wave", 13),
        ("Detect", 19), ("Agility", 25),
        ("Discharge", 31), ("Drill Peck", 37),
        ("Rain Dance", 43), ("Roost", 49),
        ("Ancient Power", 55), ("Thunder", 61),
        ("Volt Switch", 67), ("Zap Cannon", 73),
    ],
    "Moltres": [
        ("Ember", 1), ("Wing Attack", 1),
        ("Agility", 7), ("Endure", 13),
        ("Fire Spin", 19), ("Safeguard", 25),
        ("Air Slash", 31), ("Flamethrower", 37),
        ("Sunny Day", 43), ("Roost", 49),
        ("Ancient Power", 55), ("Heat Wave", 61),
        ("Solar Beam", 67), ("Sky Attack", 73),
    ],

    # ── DRAGONS ───────────────────────────────────────────────────────────────

    "Dratini": [
        ("Wrap", 1), ("Leer", 1),
        ("Thunder Wave", 5), ("Twister", 11),
        ("Dragon Rage", 15), ("Slam", 21),
        ("Agility", 27), ("Dragon Tail", 33),
        ("Aqua Tail", 39), ("Dragon Rush", 45),
        ("Safeguard", 51), ("Outrage", 57),
        ("Hyper Beam", 63),
    ],
    "Dragonair": [
        ("Wrap", 1), ("Leer", 1), ("Thunder Wave", 1), ("Twister", 1),
        ("Dragon Rage", 15), ("Slam", 21),
        ("Agility", 27), ("Dragon Tail", 35),
        ("Aqua Tail", 42), ("Dragon Rush", 49),
        ("Safeguard", 56), ("Outrage", 63),
        ("Hyper Beam", 70),
    ],
    "Dragonite": [
        ("Wrap", 1), ("Leer", 1), ("Thunder Wave", 1), ("Twister", 1),
        ("Dragon Rage", 1), ("Wing Attack", 1),
        ("Slam", 21), ("Agility", 27),
        ("Dragon Dance", 35), ("Aqua Tail", 44),
        ("Dragon Rush", 51), ("Outrage", 60),
        ("Hyper Beam", 68), ("Hurricane", 76),
    ],

    # ── LÉGENDAIRES PSYCHIQUES ────────────────────────────────────────────────

    "Mewtwo": [
        ("Confusion", 1), ("Disable", 1),
        ("Barrier", 8), ("Swift", 15),
        ("Psych Up", 22), ("Future Sight", 29),
        ("Amnesia", 36), ("Recover", 43),
        ("Guard Swap", 50), ("Power Swap", 50),
        ("Psychic", 57), ("Calm Mind", 64),
        ("Aura Sphere", 71), ("Psystrike", 78),
    ],
    "Mew": [
        ("Pound", 1), ("Transform", 10),
        ("Mega Punch", 20), ("Metronome", 30),
        ("Psychic", 40), ("Ancient Power", 50),
        ("Amnesia", 60), ("Baton Pass", 70),
        ("Nasty Plot", 80), ("Aura Sphere", 90),
        ("Geomancy", 100),
    ],
}


# ==============================================================================
# FONCTION DE MISE À JOUR
# ==============================================================================

def update_learnable_moves_gen9(clear_existing=True):
    """
    Met à jour les PokemonLearnableMove avec les niveaux Gen 9 (Scarlet/Violet).

    Args:
        clear_existing (bool): Si True, supprime les anciens learnsets avant de recréer.
                               Si False, ajoute/met à jour seulement.
    """
    logging.info("=" * 70)
    logging.info("MISE À JOUR DES LEARNSETS — GEN 9 (Scarlet/Violet)")
    logging.info("=" * 70)

    total_created = 0
    total_updated = 0
    total_skipped = 0
    pokemon_not_found = []
    move_not_found = []

    for pokemon_name, moves_list in LEARNABLE_MOVES_GEN9.items():
        try:
            pokemon = Pokemon.objects.get(name=pokemon_name)
        except Pokemon.DoesNotExist:
            logging.warning(f"[!] Pokémon introuvable: {pokemon_name}")
            pokemon_not_found.append(pokemon_name)
            continue

        if clear_existing:
            deleted_count, _ = PokemonLearnableMove.objects.filter(pokemon=pokemon).delete()
            if deleted_count:
                logging.debug(
                    f"  [-] {deleted_count} ancien(s) learnset(s) supprimé(s) pour {pokemon_name}"
                )

        for move_name, level in moves_list:
            try:
                move = PokemonMove.objects.get(name=move_name)
            except PokemonMove.DoesNotExist:
                logging.warning(f"  [!] Move introuvable: '{move_name}' pour {pokemon_name}")
                if move_name not in move_not_found:
                    move_not_found.append(move_name)
                total_skipped += 1
                continue

            obj, created = PokemonLearnableMove.objects.get_or_create(
                pokemon=pokemon,
                move=move,
                defaults={"level_learned": level},
            )
            if created:
                total_created += 1
            else:
                # Mise à jour du niveau si différent
                if obj.level_learned != level:
                    obj.level_learned = level
                    obj.save(update_fields=["level_learned"])
                    total_updated += 1

    logging.info("=" * 70)
    logging.info("[✓] Learnsets Gen 9 mis à jour!")
    logging.info(f"    — {total_created} entrées créées")
    logging.info(f"    — {total_updated} niveaux mis à jour")
    logging.info(f"    — {total_skipped} moves ignorés (introuvables)")
    if pokemon_not_found:
        logging.warning(f"    — Pokémon introuvables : {pokemon_not_found}")
    if move_not_found:
        logging.warning(f"    — Moves introuvables  : {move_not_found}")
    logging.info("=" * 70)


if __name__ == "__main__":
    update_learnable_moves_gen9()