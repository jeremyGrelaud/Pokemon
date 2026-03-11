#!/usr/bin/python3
"""
Script d'initialisation des capacités apprises par niveau — Gen 3 (FireRed/LeafGreen).

POURQUOI GEN 3 ?
- En Gen 1, les Pokémon apprennent leurs moves très tardivement (Bulbasaur apprend
  Vine Whip au niveau 21, au lieu de 9 en Gen 3).
- FireRed/LeafGreen a rebalancé les niveaux pour un meilleur rythme de jeu.
- Les Pokémon apprennent leurs moves signature bien plus tôt → combats plus variés.

SOURCE: pokemondb.net (learnsets FRLG)
"""

from myPokemonApp.models import Pokemon, PokemonMove, PokemonLearnableMove
import logging

logging.basicConfig(level=logging.INFO)


# ==============================================================================
# DONNÉES GEN 3 (FireRed/LeafGreen) — niveaux d'apprentissage
# Format: 'NomPokemon': [('NomMove', niveau), ...]
# Les moves au niveau 1 sont disponibles dès le départ (ou via rappel).
# ==============================================================================

LEARNABLE_MOVES_GEN3 = {

    # ─── STARTERS ─────────────────────────────────────────────────────────────

    'Bulbasaur': [
        ('Tackle', 1), ('Growl', 1),
        ('Leech Seed', 7), ('Vine Whip', 9),
        ('Poison Powder', 15), ('Razor Leaf', 20),
        ('Growth', 27), ('Sleep Powder', 29),
        ('Solar Beam', 41), ('Sweet Scent', 33),
    ],
    'Ivysaur': [
        ('Tackle', 1), ('Growl', 1), ('Leech Seed', 1), ('Vine Whip', 1),
        ('Poison Powder', 15), ('Razor Leaf', 22),
        ('Growth', 29), ('Sleep Powder', 32),
        ('Solar Beam', 45), ('Sweet Scent', 36),
    ],
    'Venusaur': [
        ('Tackle', 1), ('Growl', 1), ('Leech Seed', 1), ('Vine Whip', 1),
        ('Poison Powder', 15), ('Razor Leaf', 22),
        ('Growth', 29), ('Sleep Powder', 32),
        ('Petal Dance', 54), ('Solar Beam', 45), ('Sweet Scent', 36),
    ],

    'Charmander': [
        ('Scratch', 1), ('Growl', 1),
        ('Ember', 7), ('Smokescreen', 13),
        ('Dragon Rage', 20), ('Slash', 26),
        ('Flamethrower', 31), ('Fire Spin', 38),
    ],
    'Charmeleon': [
        ('Scratch', 1), ('Growl', 1), ('Ember', 1), ('Smokescreen', 1),
        ('Dragon Rage', 20), ('Slash', 27),
        ('Flamethrower', 32), ('Fire Spin', 40),
    ],
    'Charizard': [
        ('Scratch', 1), ('Growl', 1), ('Ember', 1), ('Smokescreen', 1),
        ('Dragon Rage', 20), ('Slash', 27),
        ('Flamethrower', 32), ('Fire Spin', 40),
        ('Wing Attack', 1),
    ],

    'Squirtle': [
        ('Tackle', 1), ('Tail Whip', 1),
        ('Bubble', 7), ('Withdraw', 13),
        ('Water Gun', 16), ('Bite', 20),
        ('Rapid Spin', 23), ('Protect', 28),
        ('Rain Dance', 31), ('Skull Bash', 35),
        ('Hydro Pump', 42),
    ],
    'Wartortle': [
        ('Tackle', 1), ('Tail Whip', 1), ('Bubble', 1), ('Withdraw', 1),
        ('Water Gun', 16), ('Bite', 21),
        ('Rapid Spin', 24), ('Protect', 29),
        ('Rain Dance', 33), ('Skull Bash', 38),
        ('Hydro Pump', 47),
    ],
    'Blastoise': [
        ('Tackle', 1), ('Tail Whip', 1), ('Bubble', 1), ('Withdraw', 1),
        ('Water Gun', 16), ('Bite', 21),
        ('Rapid Spin', 24), ('Protect', 29),
        ('Rain Dance', 33), ('Skull Bash', 38),
        ('Hydro Pump', 47),
    ],

    # ─── CHENILLES / INSECTES ────────────────────────────────────────────────

    'Caterpie': [
        ('Tackle', 1), ('String Shot', 1),
    ],
    'Metapod': [
        ('Harden', 1),
    ],
    'Butterfree': [
        ('Confusion', 1), ('Sleep Powder', 12), ('Stun Spore', 15),
        ('Poison Powder', 18), ('Supersonic', 23), ('Whirlwind', 28),
        ('Psybeam', 34), ('Silver Wind', 40), ('Safeguard', 47),
    ],

    'Weedle': [
        ('Poison Sting', 1), ('String Shot', 1),
    ],
    'Kakuna': [
        ('Harden', 1),
    ],
    'Beedrill': [
        ('Fury Attack', 1), ('Twineedle', 1), ('Rage', 13),
        ('Focus Energy', 20), ('Pursuit', 27), ('Pin Missile', 34),
        ('Agility', 41), ('Endeavor', 48),
    ],

    # ─── PIGEONS ─────────────────────────────────────────────────────────────

    'Pidgey': [
        ('Tackle', 1), ('Sand Attack', 1),
        ('Gust', 9), ('Quick Attack', 13), ('Whirlwind', 19),
        ('Wing Attack', 24), ('Mirror Move', 30), ('Agility', 36),
    ],
    'Pidgeotto': [
        ('Tackle', 1), ('Sand Attack', 1), ('Gust', 1), ('Quick Attack', 1),
        ('Whirlwind', 21), ('Wing Attack', 26), ('Mirror Move', 32), ('Agility', 38),
    ],
    'Pidgeot': [
        ('Tackle', 1), ('Sand Attack', 1), ('Gust', 1), ('Quick Attack', 1),
        ('Whirlwind', 21), ('Wing Attack', 26), ('Mirror Move', 32), ('Agility', 38),
        ('Hurricane', 44),
    ],

    # ─── RATTATA / RATICATE ──────────────────────────────────────────────────

    'Rattata': [
        ('Tackle', 1), ('Tail Whip', 1),
        ('Quick Attack', 7), ('Focus Energy', 13),
        ('Bite', 16), ('Super Fang', 20),
        ('Hyper Fang', 24), ('Screech', 28),
        ('Endeavor', 33),
    ],
    'Raticate': [
        ('Tackle', 1), ('Tail Whip', 1), ('Quick Attack', 1), ('Focus Energy', 1),
        ('Bite', 1), ('Super Fang', 1),
        ('Hyper Fang', 24), ('Screech', 29),
        ('Endeavor', 35),
    ],

    # ─── SPEAROW / FEAROW ─────────────────────────────────────────────────────

    'Spearow': [
        ('Peck', 1), ('Growl', 1),
        ('Leer', 9), ('Fury Attack', 13),
        ('Pursuit', 19), ('Aerial Ace', 25),
        ('Mirror Move', 28), ('Drill Peck', 34),
        ('Agility', 40),
    ],
    'Fearow': [
        ('Peck', 1), ('Growl', 1), ('Leer', 1), ('Fury Attack', 1),
        ('Pursuit', 19), ('Aerial Ace', 25),
        ('Mirror Move', 28), ('Drill Peck', 34),
        ('Agility', 40),
    ],

    # ─── EKANS / ARBOK ───────────────────────────────────────────────────────

    'Ekans': [
        ('Wrap', 1), ('Leer', 1),
        ('Poison Sting', 9), ('Bite', 12),
        ('Glare', 17), ('Screech', 22),
        ('Acid', 27), ('Sludge Bomb', 32),
        ('Haze', 38),
    ],
    'Arbok': [
        ('Wrap', 1), ('Leer', 1), ('Poison Sting', 1), ('Bite', 1),
        ('Glare', 17), ('Screech', 22),
        ('Acid', 27), ('Sludge Bomb', 32),
        ('Haze', 38),
    ],

    # ─── PIKACHU / RAICHU ─────────────────────────────────────────────────────

    'Pikachu': [
        ('Thunder Shock', 1), ('Growl', 1),
        ('Tail Whip', 9), ('Thunder Wave', 13),
        ('Quick Attack', 18), ('Double Team', 22),
        ('Slam', 26), ('Thunderbolt', 29),
        ('Agility', 34), ('Thunder', 38),
        ('Light Screen', 43),
    ],
    'Raichu': [
        ('Thunder Shock', 1), ('Tail Whip', 1), ('Quick Attack', 1),
        ('Thunder Wave', 1), ('Slam', 1), ('Thunderbolt', 1),
        ('Agility', 1), ('Thunder', 1),
    ],

    # ─── SANDSHREW / SANDSLASH ───────────────────────────────────────────────

    'Sandshrew': [
        ('Scratch', 1), ('Defense Curl', 1),
        ('Sand Attack', 6), ('Poison Sting', 11),
        ('Rollout', 17), ('Slash', 22),
        ('Swift', 28), ('Fury Swipes', 34),
        ('Sand Tomb', 40),
    ],
    'Sandslash': [
        ('Scratch', 1), ('Defense Curl', 1), ('Sand Attack', 1), ('Poison Sting', 1),
        ('Rollout', 17), ('Slash', 22),
        ('Swift', 30), ('Fury Swipes', 36),
        ('Sand Tomb', 42),
    ],

    # ─── NIDORAN ─────────────────────────────────────────────────────────────

    'Nidoran♀': [
        ('Growl', 1), ('Scratch', 1),
        ('Tail Whip', 8), ('Bite', 12),
        ('Poison Sting', 17), ('Fury Swipes', 20),
        ('Growl', 23), ('Double Kick', 27),
        ('Poison Fang', 30),
    ],
    'Nidorina': [
        ('Growl', 1), ('Scratch', 1), ('Tail Whip', 1), ('Bite', 1),
        ('Poison Sting', 17), ('Fury Swipes', 20),
        ('Double Kick', 28), ('Poison Fang', 32),
        ('Crunch', 38),
    ],
    'Nidoqueen': [
        ('Scratch', 1), ('Tail Whip', 1), ('Bite', 1), ('Double Kick', 1),
        ('Poison Fang', 1), ('Body Slam', 23),
        ('Crunch', 38), ('Earth Power', 43),
        ('Superpower', 50),
    ],
    'Nidoran♂': [
        ('Leer', 1), ('Tackle', 1),
        ('Horn Attack', 8), ('Poison Sting', 13),
        ('Focus Energy', 18), ('Double Kick', 21),
        ('Fury Attack', 23), ('Horn Drill', 28),
        ('Poison Jab', 32),
    ],
    'Nidorino': [
        ('Leer', 1), ('Tackle', 1), ('Horn Attack', 1), ('Poison Sting', 1),
        ('Focus Energy', 18), ('Double Kick', 21),
        ('Fury Attack', 23), ('Horn Drill', 29),
        ('Poison Jab', 34),
    ],
    'Nidoking': [
        ('Tackle', 1), ('Horn Attack', 1), ('Poison Sting', 1), ('Double Kick', 1),
        ('Focus Energy', 1), ('Thrash', 23),
        ('Megahorn', 38), ('Earth Power', 43),
        ('Hyper Beam', 50),
    ],

    # ─── CLEFAIRY / CLEFABLE ─────────────────────────────────────────────────

    'Clefairy': [
        ('Pound', 1), ('Growl', 1),
        ('Encore', 5), ('Sing', 9),
        ('Double Slap', 13), ('Minimize', 17),
        ('Metronome', 21), ('Defense Curl', 25),
        ('Follow Me', 29), ('Wish', 33),
        ('Softboiled', 37), ('Body Slam', 41),
        ('Moonblast', 45),
    ],
    'Clefable': [
        ('Pound', 1), ('Growl', 1), ('Sing', 1), ('Metronome', 1),
        ('Minimize', 1), ('Defense Curl', 1),
        ('Moonblast', 1),
    ],

    # ─── VULPIX / NINETALES ──────────────────────────────────────────────────

    'Vulpix': [
        ('Ember', 1), ('Tail Whip', 1),
        ('Roar', 7), ('Quick Attack', 13),
        ('Fire Spin', 17), ('Confuse Ray', 21),
        ('Imprison', 27), ('Flamethrower', 33),
        ('Will-O-Wisp', 39), ('Grudge', 45),
        ('Fire Blast', 51),
    ],
    'Ninetales': [
        ('Ember', 1), ('Tail Whip', 1), ('Quick Attack', 1), ('Confuse Ray', 1),
        ('Flamethrower', 1), ('Will-O-Wisp', 1), ('Fire Blast', 1),
    ],

    # ─── JIGGLYPUFF / WIGGLYTUFF ─────────────────────────────────────────────

    'Jigglypuff': [
        ('Sing', 1), ('Defense Curl', 1),
        ('Pound', 5), ('Disable', 9),
        ('Rollout', 13), ('Doubleslap', 17),
        ('Rest', 21), ('Body Slam', 25),
        ('Gyro Ball', 29), ('Wake-Up Slap', 33),
        ('Mimic', 37), ('Hyper Voice', 41),
        ('Moonblast', 45),
    ],
    'Wigglytuff': [
        ('Sing', 1), ('Defense Curl', 1), ('Pound', 1), ('Disable', 1),
        ('Doubleslap', 1), ('Body Slam', 1), ('Hyper Voice', 1),
    ],

    # ─── ZUBAT / GOLBAT ──────────────────────────────────────────────────────

    'Zubat': [
        ('Leech Life', 1),
        ('Supersonic', 5), ('Astonish', 9),
        ('Bite', 13), ('Wing Attack', 17),
        ('Confuse Ray', 21), ('Air Cutter', 25),
        ('Mean Look', 29), ('Poison Fang', 33),
        ('Haze', 37),
    ],
    'Golbat': [
        ('Leech Life', 1), ('Supersonic', 1), ('Bite', 1), ('Wing Attack', 1),
        ('Confuse Ray', 21), ('Air Cutter', 25),
        ('Mean Look', 29), ('Poison Fang', 33),
        ('Haze', 37),
    ],

    # ─── ODDISH / GLOOM / VILEPLUME ──────────────────────────────────────────

    'Oddish': [
        ('Absorb', 1), ('Growl', 1),
        ('Acid', 9), ('Sleep Powder', 13),
        ('Poison Powder', 15), ('Stun Spore', 17),
        ('Mega Drain', 21), ('Moonlight', 25),
        ('Giga Drain', 33),
    ],
    'Gloom': [
        ('Absorb', 1), ('Growl', 1), ('Acid', 1), ('Sleep Powder', 1),
        ('Poison Powder', 15), ('Stun Spore', 17),
        ('Mega Drain', 21), ('Moonlight', 27),
        ('Giga Drain', 36),
    ],
    'Vileplume': [
        ('Absorb', 1), ('Acid', 1), ('Sleep Powder', 1), ('Petal Dance', 1),
        ('Mega Drain', 1), ('Giga Drain', 1),
    ],

    # ─── PARAS / PARASECT ────────────────────────────────────────────────────

    'Paras': [
        ('Scratch', 1), ('Stun Spore', 1),
        ('Leech Life', 7), ('Poison Powder', 13),
        ('Slash', 20), ('Growth', 27),
        ('Spore', 32), ('Giga Drain', 38),
        ('Aromatherapy', 45),
    ],
    'Parasect': [
        ('Scratch', 1), ('Stun Spore', 1), ('Leech Life', 1), ('Poison Powder', 1),
        ('Slash', 20), ('Growth', 27),
        ('Spore', 32), ('Giga Drain', 38),
        ('Aromatherapy', 45),
    ],

    # ─── VENONAT / VENOMOTH ──────────────────────────────────────────────────

    'Venonat': [
        ('Tackle', 1), ('Disable', 1),
        ('Foresight', 9), ('Supersonic', 13),
        ('Confusion', 17), ('Poison Powder', 21),
        ('Psybeam', 25), ('Sleep Powder', 29),
        ('Leech Life', 33), ('Stun Spore', 37),
        ('Psychic', 41), ('Signal Beam', 45),
    ],
    'Venomoth': [
        ('Tackle', 1), ('Disable', 1), ('Foresight', 1), ('Supersonic', 1),
        ('Confusion', 17), ('Poison Powder', 21),
        ('Psybeam', 25), ('Sleep Powder', 29),
        ('Leech Life', 33), ('Psychic', 41),
        ('Signal Beam', 45),
    ],

    # ─── DIGLETT / DUGTRIO ───────────────────────────────────────────────────

    'Diglett': [
        ('Scratch', 1), ('Sand Attack', 1),
        ('Growl', 9), ('Astonish', 13),
        ('Mud Slap', 17), ('Magnitude', 21),
        ('Dig', 25), ('Slash', 29),
        ('Earthquake', 33), ('Sand Tomb', 37),
        ('Fissure', 41),
    ],
    'Dugtrio': [
        ('Scratch', 1), ('Sand Attack', 1), ('Growl', 1), ('Astonish', 1),
        ('Mud Slap', 17), ('Magnitude', 21),
        ('Dig', 25), ('Slash', 29),
        ('Earthquake', 33), ('Sand Tomb', 37),
        ('Fissure', 41),
    ],

    # ─── MEOWTH / PERSIAN ────────────────────────────────────────────────────

    'Meowth': [
        ('Scratch', 1), ('Growl', 1),
        ('Bite', 9), ('Pay Day', 13),
        ('Faint Attack', 17), ('Screech', 21),
        ('Slash', 25), ('Fake Out', 29),
        ('Night Slash', 33),
    ],
    'Persian': [
        ('Scratch', 1), ('Growl', 1), ('Bite', 1), ('Pay Day', 1),
        ('Faint Attack', 17), ('Screech', 21),
        ('Slash', 25), ('Fake Out', 29),
        ('Night Slash', 33),
    ],

    # ─── PSYDUCK / GOLDUCK ───────────────────────────────────────────────────

    'Psyduck': [
        ('Scratch', 1), ('Tail Whip', 1),
        ('Water Sport', 6), ('Disable', 11),
        ('Confusion', 16), ('Water Pulse', 21),
        ('Fury Swipes', 26), ('Screech', 31),
        ('Psych Up', 36), ('Amnesia', 41),
        ('Hydro Pump', 46),
    ],
    'Golduck': [
        ('Scratch', 1), ('Tail Whip', 1), ('Disable', 1), ('Confusion', 1),
        ('Water Pulse', 21), ('Fury Swipes', 26),
        ('Screech', 31), ('Psych Up', 36),
        ('Amnesia', 41), ('Hydro Pump', 46),
    ],

    # ─── MANKEY / PRIMEAPE ───────────────────────────────────────────────────

    'Mankey': [
        ('Scratch', 1), ('Leer', 1),
        ('Low Kick', 7), ('Karate Chop', 13),
        ('Fury Swipes', 18), ('Focus Energy', 22),
        ('Seismic Toss', 26), ('Screech', 30),
        ('Cross Chop', 34), ('Thrash', 38),
        ('Close Combat', 44),
    ],
    'Primeape': [
        ('Scratch', 1), ('Leer', 1), ('Low Kick', 1), ('Karate Chop', 1),
        ('Fury Swipes', 18), ('Focus Energy', 22),
        ('Seismic Toss', 26), ('Screech', 30),
        ('Cross Chop', 34), ('Thrash', 38),
        ('Close Combat', 44),
    ],

    # ─── GROWLITHE / ARCANINE ────────────────────────────────────────────────

    'Growlithe': [
        ('Bite', 1), ('Roar', 1),
        ('Ember', 7), ('Leer', 9),
        ('Odor Sleuth', 13), ('Take Down', 19),
        ('Flame Wheel', 25), ('Agility', 31),
        ('Flamethrower', 37), ('Reversal', 43),
        ('Fire Blast', 49),
    ],
    'Arcanine': [
        ('Bite', 1), ('Roar', 1), ('Ember', 1), ('Flamethrower', 1),
        ('Extreme Speed', 49), ('Fire Blast', 1),
        ('Flare Blitz', 1),
    ],

    # ─── POLIWAG / POLIWHIRL / POLIWRATH ─────────────────────────────────────

    'Poliwag': [
        ('Bubble', 1), ('Water Sport', 1),
        ('Hypnosis', 5), ('Water Gun', 11),
        ('Doubleslap', 15), ('Rain Dance', 19),
        ('Body Slam', 24), ('Belly Drum', 29),
        ('Wake-Up Slap', 34),
    ],
    'Poliwhirl': [
        ('Bubble', 1), ('Hypnosis', 1), ('Water Gun', 1), ('Doubleslap', 1),
        ('Rain Dance', 19), ('Body Slam', 25),
        ('Belly Drum', 31), ('Submission', 38),
        ('Wake-Up Slap', 45),
    ],
    'Poliwrath': [
        ('Bubble', 1), ('Hypnosis', 1), ('Water Gun', 1), ('Doubleslap', 1),
        ('Body Slam', 1), ('Submission', 38),
        ('Mind Reader', 1), ('Dynamic Punch', 50),
    ],

    # ─── ABRA / KADABRA / ALAKAZAM ───────────────────────────────────────────

    'Abra': [
        ('Teleport', 1),
    ],
    'Kadabra': [
        ('Teleport', 1), ('Kinesis', 1), ('Confusion', 16),
        ('Disable', 18), ('Psybeam', 21),
        ('Reflect', 23), ('Recover', 27),
        ('Future Sight', 30), ('Psychic', 33),
        ('Calm Mind', 37), ('Trick', 42),
    ],
    'Alakazam': [
        ('Teleport', 1), ('Kinesis', 1), ('Confusion', 16),
        ('Disable', 18), ('Psybeam', 21),
        ('Reflect', 23), ('Recover', 27),
        ('Future Sight', 30), ('Psychic', 33),
        ('Calm Mind', 37), ('Trick', 42),
    ],

    # ─── MACHOP / MACHOKE / MACHAMP ──────────────────────────────────────────

    'Machop': [
        ('Low Kick', 1), ('Leer', 1),
        ('Focus Energy', 7), ('Karate Chop', 13),
        ('Foresight', 19), ('Seismic Toss', 22),
        ('Vital Throw', 27), ('Submission', 31),
        ('Wake-Up Slap', 36), ('Cross Chop', 41),
        ('Scary Face', 45), ('Dynamic Punch', 51),
    ],
    'Machoke': [
        ('Low Kick', 1), ('Leer', 1), ('Focus Energy', 1), ('Karate Chop', 1),
        ('Foresight', 19), ('Seismic Toss', 22),
        ('Vital Throw', 27), ('Submission', 31),
        ('Cross Chop', 41), ('Dynamic Punch', 51),
    ],
    'Machamp': [
        ('Low Kick', 1), ('Leer', 1), ('Focus Energy', 1), ('Karate Chop', 1),
        ('Seismic Toss', 22), ('Submission', 31),
        ('Cross Chop', 41), ('Dynamic Punch', 51),
        ('Close Combat', 1),
    ],

    # ─── BELLSPROUT / WEEPINBELL / VICTREEBEL ────────────────────────────────

    'Bellsprout': [
        ('Vine Whip', 1), ('Growth', 1),
        ('Wrap', 7), ('Sleep Powder', 13),
        ('Poison Powder', 15), ('Stun Spore', 17),
        ('Acid', 21), ('Knock Off', 26),
        ('Sweet Scent', 33), ('Gastro Acid', 41),
    ],
    'Weepinbell': [
        ('Vine Whip', 1), ('Growth', 1), ('Wrap', 1), ('Sleep Powder', 1),
        ('Poison Powder', 15), ('Stun Spore', 17),
        ('Acid', 21), ('Knock Off', 26),
        ('Sweet Scent', 34), ('Gastro Acid', 43),
    ],
    'Victreebel': [
        ('Vine Whip', 1), ('Sleep Powder', 1), ('Acid', 1), ('Razor Leaf', 1),
        ('Sweet Scent', 1), ('Leaf Blade', 1),
    ],

    # ─── TENTACOOL / TENTACRUEL ──────────────────────────────────────────────

    'Tentacool': [
        ('Poison Sting', 1), ('Constrict', 1),
        ('Supersonic', 7), ('Acid', 13),
        ('Toxic Spikes', 18), ('Water Pulse', 22),
        ('Wrap', 27), ('Barrier', 33),
        ('Bubblebeam', 38), ('Hydro Pump', 46),
    ],
    'Tentacruel': [
        ('Poison Sting', 1), ('Constrict', 1), ('Supersonic', 1), ('Acid', 1),
        ('Toxic Spikes', 18), ('Water Pulse', 22),
        ('Wrap', 27), ('Barrier', 33),
        ('Bubblebeam', 38), ('Hydro Pump', 46),
    ],

    # ─── GEODUDE / GRAVELER / GOLEM ──────────────────────────────────────────

    'Geodude': [
        ('Tackle', 1), ('Defense Curl', 1),
        ('Mud Sport', 7), ('Rock Throw', 11),
        ('Magnitude', 15), ('Rollout', 19),
        ('Rock Blast', 23), ('Rock Polish', 29),
        ('Self-Destruct', 33), ('Earthquake', 37),
        ('Explosion', 43),
    ],
    'Graveler': [
        ('Tackle', 1), ('Defense Curl', 1), ('Rock Throw', 1), ('Magnitude', 1),
        ('Rollout', 19), ('Rock Blast', 23),
        ('Rock Polish', 29), ('Self-Destruct', 33),
        ('Earthquake', 37), ('Explosion', 43),
    ],
    'Golem': [
        ('Tackle', 1), ('Defense Curl', 1), ('Rock Throw', 1), ('Magnitude', 1),
        ('Rollout', 19), ('Rock Blast', 23),
        ('Self-Destruct', 33), ('Earthquake', 37),
        ('Explosion', 43),
    ],

    # ─── PONYTA / RAPIDASH ───────────────────────────────────────────────────

    'Ponyta': [
        ('Tackle', 1), ('Growl', 1),
        ('Tail Whip', 7), ('Ember', 9),
        ('Flame Wheel', 16), ('Stomp', 22),
        ('Fire Spin', 28), ('Agility', 32),
        ('Take Down', 36), ('Fire Blast', 44),
        ('Bounce', 50),
    ],
    'Rapidash': [
        ('Tackle', 1), ('Growl', 1), ('Tail Whip', 1), ('Ember', 1),
        ('Flame Wheel', 16), ('Stomp', 22),
        ('Fire Spin', 28), ('Agility', 32),
        ('Take Down', 36), ('Fire Blast', 44),
        ('Bounce', 50),
    ],

    # ─── SLOWPOKE / SLOWBRO ──────────────────────────────────────────────────

    'Slowpoke': [
        ('Curse', 1), ('Yawn', 1),
        ('Tackle', 1), ('Growl', 6),
        ('Water Gun', 15), ('Confusion', 21),
        ('Disable', 27), ('Headbutt', 33),
        ('Amnesia', 37), ('Psychic', 40),
        ('Rain Dance', 45), ('Psych Up', 51),
    ],
    'Slowbro': [
        ('Curse', 1), ('Yawn', 1), ('Tackle', 1), ('Growl', 1),
        ('Water Gun', 15), ('Confusion', 21),
        ('Disable', 27), ('Headbutt', 33),
        ('Amnesia', 37), ('Psychic', 40),
        ('Rain Dance', 45),
    ],

    # ─── MAGNEMITE / MAGNETON ────────────────────────────────────────────────

    'Magnemite': [
        ('Metal Sound', 1), ('Tackle', 1),
        ('Thunder Wave', 6), ('Sonic Boom', 11),
        ('Spark', 16), ('Lock-On', 21),
        ('Swift', 26), ('Screech', 31),
        ('Discharge', 36), ('Magnet Rise', 41),
        ('Gyro Ball', 46), ('Zap Cannon', 51),
    ],
    'Magneton': [
        ('Metal Sound', 1), ('Tackle', 1), ('Thunder Wave', 1), ('Sonic Boom', 1),
        ('Spark', 16), ('Lock-On', 21),
        ('Swift', 26), ('Screech', 31),
        ('Discharge', 36), ('Magnet Rise', 41),
        ('Gyro Ball', 46), ('Zap Cannon', 51),
    ],

    # ─── DODUO / DODRIO ──────────────────────────────────────────────────────

    'Doduo': [
        ('Peck', 1), ('Growl', 1),
        ('Quick Attack', 13), ('Fury Attack', 20),
        ('Pursuit', 25), ('Drill Peck', 30),
        ('Agility', 37), ('Tri Attack', 44),
    ],
    'Dodrio': [
        ('Peck', 1), ('Growl', 1), ('Quick Attack', 1), ('Fury Attack', 1),
        ('Pursuit', 25), ('Drill Peck', 30),
        ('Agility', 37), ('Tri Attack', 44),
    ],

    # ─── SEEL / DEWGONG ──────────────────────────────────────────────────────

    'Seel': [
        ('Headbutt', 1), ('Growl', 1),
        ('Water Sport', 8), ('Icy Wind', 13),
        ('Encore', 18), ('Ice Shard', 23),
        ('Rest', 28), ('Safeguard', 33),
        ('Hail', 38), ('Blizzard', 43),
        ('Sheer Cold', 48),
    ],
    'Dewgong': [
        ('Headbutt', 1), ('Growl', 1), ('Water Sport', 1), ('Icy Wind', 1),
        ('Encore', 18), ('Ice Shard', 23),
        ('Rest', 28), ('Safeguard', 33),
        ('Hail', 38), ('Blizzard', 43),
        ('Sheer Cold', 48),
    ],

    # ─── GRIMER / MUK ────────────────────────────────────────────────────────

    'Grimer': [
        ('Pound', 1), ('Poison Gas', 1),
        ('Harden', 6), ('Mud Slap', 11),
        ('Disable', 16), ('Minimize', 21),
        ('Sludge', 26), ('Screech', 31),
        ('Sludge Bomb', 36), ('Acid Armor', 41),
        ('Gunk Shot', 46),
    ],
    'Muk': [
        ('Pound', 1), ('Poison Gas', 1), ('Harden', 1), ('Sludge', 1),
        ('Disable', 16), ('Minimize', 21),
        ('Screech', 31), ('Sludge Bomb', 36),
        ('Acid Armor', 41), ('Gunk Shot', 46),
    ],

    # ─── SHELLDER / CLOYSTER ─────────────────────────────────────────────────

    'Shellder': [
        ('Tackle', 1), ('Withdraw', 1),
        ('Supersonic', 8), ('Icicle Spear', 13),
        ('Protect', 18), ('Leer', 23),
        ('Clamp', 28), ('Ice Shard', 33),
        ('Razor Shell', 38), ('Hydro Pump', 43),
    ],
    'Cloyster': [
        ('Tackle', 1), ('Withdraw', 1), ('Supersonic', 1), ('Icicle Spear', 1),
        ('Protect', 18), ('Clamp', 28),
        ('Ice Shard', 33), ('Spike Cannon', 1),
        ('Blizzard', 50),
    ],

    # ─── GASTLY / HAUNTER / GENGAR ───────────────────────────────────────────

    'Gastly': [
        ('Hypnosis', 1), ('Lick', 1),
        ('Spite', 8), ('Mean Look', 13),
        ('Curse', 18), ('Night Shade', 23),
        ('Confuse Ray', 26), ('Sucker Punch', 29),
        ('Shadow Ball', 33), ('Destiny Bond', 38),
        ('Shadow Punch', 41), ('Nightmare', 46),
    ],
    'Haunter': [
        ('Hypnosis', 1), ('Lick', 1), ('Spite', 1), ('Mean Look', 1),
        ('Curse', 18), ('Night Shade', 23),
        ('Confuse Ray', 26), ('Sucker Punch', 29),
        ('Shadow Ball', 33), ('Destiny Bond', 38),
        ('Shadow Punch', 41), ('Nightmare', 46),
    ],
    'Gengar': [
        ('Hypnosis', 1), ('Lick', 1), ('Spite', 1), ('Mean Look', 1),
        ('Curse', 18), ('Night Shade', 23),
        ('Confuse Ray', 26), ('Sucker Punch', 29),
        ('Shadow Ball', 33), ('Destiny Bond', 38),
        ('Shadow Punch', 41), ('Nightmare', 46),
    ],

    # ─── ONIX ────────────────────────────────────────────────────────────────

    'Onix': [
        ('Tackle', 1), ('Screech', 1),
        ('Bind', 9), ('Rock Throw', 13),
        ('Rage', 20), ('Rock Polish', 26),
        ('Sandstorm', 33), ('Slam', 37),
        ('Rock Slide', 42), ('Stealth Rock', 48),
        ('Double-Edge', 54),
    ],

    # ─── DROWZEE / HYPNO ─────────────────────────────────────────────────────

    'Drowzee': [
        ('Pound', 1), ('Hypnosis', 1),
        ('Disable', 9), ('Confusion', 13),
        ('Headbutt', 17), ('Poison Gas', 21),
        ('Meditate', 25), ('Psybeam', 29),
        ('Psych Up', 33), ('Psychic', 37),
        ('Future Sight', 41), ('Dream Eater', 45),
    ],
    'Hypno': [
        ('Pound', 1), ('Hypnosis', 1), ('Disable', 1), ('Confusion', 1),
        ('Headbutt', 17), ('Meditate', 25),
        ('Psybeam', 29), ('Psych Up', 33),
        ('Psychic', 37), ('Future Sight', 41),
        ('Dream Eater', 45),
    ],

    # ─── KRABBY / KINGLER ────────────────────────────────────────────────────

    'Krabby': [
        ('Bubble', 1), ('Leer', 1),
        ('Vicegrip', 1), ('Mud Sport', 7),
        ('Stomp', 13), ('Protect', 20),
        ('Guillotine', 25), ('Slam', 30),
        ('Harden', 35), ('Crabhammer', 40),
        ('Flail', 47),
    ],
    'Kingler': [
        ('Bubble', 1), ('Leer', 1), ('Vicegrip', 1), ('Stomp', 1),
        ('Protect', 20), ('Guillotine', 25),
        ('Slam', 30), ('Crabhammer', 40),
        ('Flail', 47),
    ],

    # ─── VOLTORB / ELECTRODE ─────────────────────────────────────────────────

    'Voltorb': [
        ('Charge', 1), ('Tackle', 1),
        ('Screech', 9), ('Sonic Boom', 13),
        ('Spark', 17), ('Rollout', 21),
        ('Self-Destruct', 26), ('Light Screen', 29),
        ('Swift', 33), ('Explosion', 39),
        ('Mirror Coat', 43),
    ],
    'Electrode': [
        ('Charge', 1), ('Tackle', 1), ('Screech', 1), ('Sonic Boom', 1),
        ('Spark', 17), ('Rollout', 21),
        ('Self-Destruct', 26), ('Light Screen', 29),
        ('Swift', 33), ('Explosion', 39),
        ('Mirror Coat', 43),
    ],

    # ─── EXEGGCUTE / EXEGGUTOR ───────────────────────────────────────────────

    'Exeggcute': [
        ('Uproar', 1), ('Hypnosis', 1),
        ('Reflect', 7), ('Leech Seed', 11),
        ('Bullet Seed', 15), ('Stun Spore', 19),
        ('Poison Powder', 23), ('Sleep Powder', 27),
        ('Egg Bomb', 33),
    ],
    'Exeggutor': [
        ('Uproar', 1), ('Hypnosis', 1), ('Reflect', 1), ('Leech Seed', 1),
        ('Egg Bomb', 33), ('Wood Hammer', 1),
        ('Leaf Storm', 47),
    ],

    # ─── CUBONE / MAROWAK ────────────────────────────────────────────────────

    'Cubone': [
        ('Growl', 1), ('Tail Whip', 1),
        ('Bone Club', 5), ('Headbutt', 9),
        ('Leer', 13), ('Focus Energy', 17),
        ('Bonemerang', 21), ('Rage', 25),
        ('False Swipe', 33), ('Thrash', 37),
        ('Bone Rush', 41), ('Double-Edge', 45),
    ],
    'Marowak': [
        ('Growl', 1), ('Tail Whip', 1), ('Bone Club', 1), ('Headbutt', 1),
        ('Focus Energy', 17), ('Bonemerang', 21),
        ('Rage', 25), ('False Swipe', 33),
        ('Thrash', 37), ('Bone Rush', 41),
        ('Double-Edge', 45),
    ],

    # ─── HITMONLEE / HITMONCHAN ──────────────────────────────────────────────

    'Hitmonlee': [
        ('Reversal', 1), ('Double Kick', 1),
        ('Meditate', 1), ('Rolling Kick', 6),
        ('Jump Kick', 11), ('Brick Break', 16),
        ('Focus Energy', 21), ('Hi Jump Kick', 26),
        ('Mind Reader', 31), ('Foresight', 36),
        ('Blaze Kick', 41), ('Endure', 46),
        ('Mega Kick', 51), ('Close Combat', 56),
    ],
    'Hitmonchan': [
        ('Comet Punch', 1), ('Agility', 1),
        ('Pursuit', 6), ('Mach Punch', 11),
        ('Bullet Punch', 16), ('Thunder Punch', 21),
        ('Ice Punch', 26), ('Fire Punch', 31),
        ('Sky Uppercut', 36), ('Mega Punch', 41),
        ('Detect', 46), ('Focus Punch', 51),
        ('Counter', 56),
    ],

    # ─── LICKITUNG ───────────────────────────────────────────────────────────

    'Lickitung': [
        ('Lick', 1), ('Supersonic', 1),
        ('Defense Curl', 7), ('Knock Off', 13),
        ('Wrap', 18), ('Stomp', 23),
        ('Disable', 28), ('Slam', 33),
        ('Rollout', 38), ('Me First', 43),
        ('Screech', 48), ('Refresh', 53),
    ],

    # ─── KOFFING / WEEZING ───────────────────────────────────────────────────

    'Koffing': [
        ('Poison Gas', 1), ('Tackle', 1),
        ('Smog', 9), ('Smokescreen', 13),
        ('Self-Destruct', 17), ('Sludge', 22),
        ('Haze', 30), ('Explosion', 36),
        ('Destiny Bond', 43),
    ],
    'Weezing': [
        ('Poison Gas', 1), ('Tackle', 1), ('Smog', 1), ('Smokescreen', 1),
        ('Self-Destruct', 17), ('Sludge', 22),
        ('Haze', 30), ('Explosion', 36),
        ('Destiny Bond', 43),
    ],

    # ─── RHYHORN / RHYDON ────────────────────────────────────────────────────

    'Rhyhorn': [
        ('Horn Attack', 1), ('Tail Whip', 1),
        ('Stomp', 10), ('Fury Attack', 15),
        ('Scary Face', 22), ('Rock Blast', 29),
        ('Horn Drill', 36), ('Earthquake', 41),
        ('Stone Edge', 48), ('Megahorn', 55),
    ],
    'Rhydon': [
        ('Horn Attack', 1), ('Tail Whip', 1), ('Stomp', 1), ('Fury Attack', 1),
        ('Scary Face', 22), ('Rock Blast', 29),
        ('Horn Drill', 36), ('Earthquake', 41),
        ('Stone Edge', 48), ('Megahorn', 55),
    ],

    # ─── CHANSEY ─────────────────────────────────────────────────────────────

    'Chansey': [
        ('Pound', 1), ('Growl', 1),
        ('Tail Whip', 5), ('Refresh', 9),
        ('Softboiled', 13), ('Doubleslap', 17),
        ('Minimize', 23), ('Sing', 29),
        ('Egg Bomb', 33), ('Defense Curl', 39),
        ('Light Screen', 45), ('Double-Edge', 51),
    ],

    # ─── TANGELA ─────────────────────────────────────────────────────────────

    'Tangela': [
        ('Ingrain', 1), ('Constrict', 1),
        ('Sleep Powder', 4), ('Vine Whip', 9),
        ('Bind', 14), ('Growth', 19),
        ('Mega Drain', 24), ('Knock Off', 29),
        ('Stun Spore', 34), ('Ancient Power', 39),
        ('Slam', 43), ('Tickle', 47),
        ('Wring Out', 51), ('Power Whip', 55),
    ],

    # ─── KANGASKHAN ──────────────────────────────────────────────────────────

    'Kangaskhan': [
        ('Comet Punch', 1), ('Leer', 1),
        ('Fake Out', 1), ('Tail Whip', 6),
        ('Bite', 11), ('Double Hit', 16),
        ('Headbutt', 21), ('Rage', 26),
        ('Dizzy Punch', 31), ('Crunch', 36),
        ('Endure', 41), ('Outrage', 46),
        ('Sucker Punch', 51),
    ],

    # ─── HORSEA / SEADRA ─────────────────────────────────────────────────────

    'Horsea': [
        ('Bubble', 1), ('Smokescreen', 1),
        ('Leer', 8), ('Water Gun', 14),
        ('Twister', 21), ('Agility', 28),
        ('Hydro Pump', 35), ('Dragon Dance', 44),
        ('Dragon Pulse', 51),
    ],
    'Seadra': [
        ('Bubble', 1), ('Smokescreen', 1), ('Leer', 1), ('Water Gun', 1),
        ('Twister', 21), ('Agility', 28),
        ('Hydro Pump', 35), ('Dragon Dance', 44),
        ('Dragon Pulse', 51),
    ],

    # ─── GOLDEEN / SEAKING ───────────────────────────────────────────────────

    'Goldeen': [
        ('Peck', 1), ('Tail Whip', 1),
        ('Water Sport', 7), ('Supersonic', 11),
        ('Horn Attack', 17), ('Flail', 24),
        ('Water Pulse', 31), ('Fury Attack', 38),
        ('Horn Drill', 44), ('Agility', 50),
        ('Megahorn', 57),
    ],
    'Seaking': [
        ('Peck', 1), ('Tail Whip', 1), ('Supersonic', 1), ('Horn Attack', 1),
        ('Flail', 24), ('Water Pulse', 31),
        ('Fury Attack', 38), ('Horn Drill', 44),
        ('Agility', 50), ('Megahorn', 57),
    ],

    # ─── STARYU / STARMIE ────────────────────────────────────────────────────

    'Staryu': [
        ('Tackle', 1), ('Harden', 1),
        ('Water Gun', 6), ('Rapid Spin', 10),
        ('Recover', 14), ('Swift', 19),
        ('Minimize', 24), ('Light Screen', 29),
        ('Cosmic Power', 34), ('Hydro Pump', 39),
        ('Power Gem', 44),
    ],
    'Starmie': [
        ('Tackle', 1), ('Harden', 1), ('Water Gun', 1), ('Rapid Spin', 1),
        ('Recover', 14), ('Swift', 19),
        ('Minimize', 24), ('Light Screen', 29),
        ('Cosmic Power', 34), ('Hydro Pump', 39),
        ('Power Gem', 44), ('Psychic', 1),
    ],

    # ─── MR. MIME ────────────────────────────────────────────────────────────

    'Mr. Mime': [
        ('Magical Leaf', 1), ('Copy Cat', 1),
        ('Meditate', 1), ('Confusion', 9),
        ('Encore', 13), ('Doubleslap', 17),
        ('Mimic', 21), ('Psybeam', 25),
        ('Barrier', 29), ('Reflect', 33),
        ('Psychic', 37), ('Trick', 41),
        ('Role Play', 45), ('Baton Pass', 49),
        ('Nasty Plot', 53),
    ],

    # ─── SCYTHER ─────────────────────────────────────────────────────────────

    'Scyther': [
        ('Vacuum Wave', 1), ('Quick Attack', 1),
        ('Leer', 1), ('Focus Energy', 6),
        ('Pursuit', 9), ('False Swipe', 12),
        ('Agility', 17), ('Wing Attack', 20),
        ('Fury Cutter', 25), ('Slash', 28),
        ('Razor Wind', 33), ('Air Slash', 36),
        ('X-Scissor', 41), ('Night Slash', 44),
        ('Double Hit', 49),
    ],

    # ─── JYNX ────────────────────────────────────────────────────────────────

    'Jynx': [
        ('Pound', 1), ('Lick', 1),
        ('Lovely Kiss', 9), ('Powder Snow', 13),
        ('DoubleSlap', 17), ('Ice Punch', 23),
        ('Mean Look', 33), ('Fake Tears', 39),
        ('Blizzard', 43), ('Perish Song', 48),
        ('Psychic', 51),
    ],

    # ─── ELECTABUZZ ──────────────────────────────────────────────────────────

    'Electabuzz': [
        ('Quick Attack', 1), ('Leer', 1),
        ('Thunder Shock', 1), ('Low Kick', 9),
        ('Swift', 13), ('Shock Wave', 17),
        ('Thunder Punch', 23), ('Light Screen', 33),
        ('Discharge', 39), ('Thunder', 46),
        ('Giga Impact', 53),
    ],

    # ─── MAGMAR ──────────────────────────────────────────────────────────────

    'Magmar': [
        ('Ember', 1), ('Leer', 1),
        ('Smog', 9), ('Smokescreen', 13),
        ('Faint Attack', 17), ('Fire Punch', 23),
        ('Sunny Day', 33), ('Flamethrower', 39),
        ('Fire Blast', 46), ('Giga Impact', 53),
    ],

    # ─── PINSIR ──────────────────────────────────────────────────────────────

    'Pinsir': [
        ('Vice Grip', 1), ('Focus Energy', 1),
        ('Bind', 9), ('Seismic Toss', 13),
        ('Guillotine', 17), ('Harden', 22),
        ('Slash', 27), ('X-Scissor', 31),
        ('Swords Dance', 36), ('Thrash', 41),
        ('Close Combat', 46),
    ],

    # ─── TAUROS ──────────────────────────────────────────────────────────────

    'Tauros': [
        ('Tackle', 1), ('Tail Whip', 1),
        ('Rage', 4), ('Horn Attack', 9),
        ('Scary Face', 14), ('Pursuit', 19),
        ('Rest', 26), ('Payback', 31),
        ('Work Up', 36), ('Zen Headbutt', 41),
        ('Take Down', 46), ('Giga Impact', 51),
    ],

    # ─── MAGIKARP / GYARADOS ─────────────────────────────────────────────────

    'Magikarp': [
        ('Splash', 1), ('Tackle', 15), ('Flail', 30),
    ],
    'Gyarados': [
        ('Thrash', 1), ('Bite', 1), ('Dragon Rage', 1),
        ('Leer', 20), ('Twister', 25),
        ('Ice Fang', 30), ('Aqua Tail', 35),
        ('Dragon Dance', 40), ('Hyper Beam', 45),
        ('Hurricane', 50),
    ],

    # ─── LAPRAS ──────────────────────────────────────────────────────────────

    'Lapras': [
        ('Water Gun', 1), ('Growl', 1),
        ('Sing', 7), ('Mist', 13),
        ('Body Slam', 18), ('Confuse Ray', 23),
        ('Ice Shard', 28), ('Rain Dance', 33),
        ('Perish Song', 38), ('Safeguard', 43),
        ('Ice Beam', 48), ('Blizzard', 53),
        ('Sheer Cold', 58),
    ],

    # ─── DITTO ───────────────────────────────────────────────────────────────

    'Ditto': [
        ('Transform', 1),
    ],

    # ─── EEVEE / EEVEELUTIONS ────────────────────────────────────────────────

    'Eevee': [
        ('Tackle', 1), ('Tail Whip', 1),
        ('Helping Hand', 1), ('Sand Attack', 8),
        ('Growl', 15), ('Quick Attack', 22),
        ('Bite', 29), ('Baton Pass', 36),
        ('Take Down', 42),
    ],
    'Vaporeon': [
        ('Water Gun', 1), ('Tail Whip', 1), ('Sand Attack', 1), ('Quick Attack', 1),
        ('Bite', 29), ('Acid Armor', 36),
        ('Haze', 42), ('Hydro Pump', 48),
    ],
    'Jolteon': [
        ('Thunder Shock', 1), ('Tail Whip', 1), ('Sand Attack', 1), ('Quick Attack', 1),
        ('Bite', 29), ('Double Kick', 36),
        ('Pin Missile', 42), ('Thunder', 48),
    ],
    'Flareon': [
        ('Ember', 1), ('Tail Whip', 1), ('Sand Attack', 1), ('Quick Attack', 1),
        ('Bite', 29), ('Fire Spin', 36),
        ('Smog', 42), ('Flamethrower', 48),
    ],

    # ─── PORYGON ─────────────────────────────────────────────────────────────

    'Porygon': [
        ('Conversion', 1), ('Tackle', 1),
        ('Sharpen', 4), ('Psybeam', 9),
        ('Conversion 2', 12), ('Agility', 17),
        ('Recover', 22), ('Magnet Rise', 27),
        ('Signal Beam', 31), ('Ice Beam', 34),
        ('Zap Cannon', 38), ('Tri Attack', 42),
        ('Lock-On', 47), ('Hyper Beam', 52),
    ],

    # ─── OMANYTE / OMASTAR ───────────────────────────────────────────────────

    'Omanyte': [
        ('Withdraw', 1), ('Bind', 1),
        ('Water Gun', 7), ('Constrict', 13),
        ('Leer', 20), ('Mud Shot', 27),
        ('Protect', 33), ('Ancient Power', 40),
        ('Tickle', 47), ('Rock Blast', 54),
        ('Hydro Pump', 60),
    ],
    'Omastar': [
        ('Withdraw', 1), ('Bind', 1), ('Water Gun', 1), ('Constrict', 1),
        ('Leer', 20), ('Mud Shot', 27),
        ('Ancient Power', 40), ('Tickle', 47),
        ('Rock Blast', 54), ('Hydro Pump', 60),
    ],

    # ─── KABUTO / KABUTOPS ───────────────────────────────────────────────────

    'Kabuto': [
        ('Scratch', 1), ('Harden', 1),
        ('Absorb', 7), ('Leer', 13),
        ('Mud Shot', 20), ('Sand Attack', 27),
        ('Endure', 33), ('Ancient Power', 40),
        ('Aqua Jet', 47), ('Slash', 54),
        ('Night Slash', 60),
    ],
    'Kabutops': [
        ('Scratch', 1), ('Harden', 1), ('Absorb', 1), ('Leer', 1),
        ('Mud Shot', 20), ('Sand Attack', 27),
        ('Endure', 33), ('Ancient Power', 40),
        ('Aqua Jet', 47), ('Slash', 54),
        ('Night Slash', 60),
    ],

    # ─── AERODACTYL ──────────────────────────────────────────────────────────

    'Aerodactyl': [
        ('Wing Attack', 1), ('Agility', 1),
        ('Bite', 9), ('Supersonic', 14),
        ('Scary Face', 19), ('Roar', 24),
        ('Ancient Power', 29), ('Take Down', 34),
        ('Crunch', 39), ('Iron Head', 44),
        ('Hyper Beam', 49), ('Rock Slide', 54),
        ('Giga Impact', 59),
    ],

    # ─── LEGENDAIRES ─────────────────────────────────────────────────────────

    'Articuno': [
        ('Powder Snow', 1), ('Mist', 1),
        ('Gust', 8), ('Mind Reader', 15),
        ('Ancient Power', 22), ('Agility', 29),
        ('Ice Shard', 36), ('Reflect', 43),
        ('Blizzard', 50), ('Hail', 57),
        ('Sheer Cold', 64),
    ],
    'Zapdos': [
        ('Peck', 1), ('Thunder Shock', 1),
        ('Thunder Wave', 8), ('Detect', 15),
        ('Ancient Power', 22), ('Charge', 29),
        ('Agility', 36), ('Discharge', 43),
        ('Rain Dance', 50), ('Thunder', 57),
        ('Zap Cannon', 64),
    ],
    'Moltres': [
        ('Wing Attack', 1), ('Ember', 1),
        ('Fire Spin', 8), ('Agility', 15),
        ('Ancient Power', 22), ('Safeguard', 29),
        ('Air Slash', 36), ('Endure', 43),
        ('Flamethrower', 50), ('Sunny Day', 57),
        ('Sky Attack', 64),
    ],
    'Dratini': [
        ('Wrap', 1), ('Leer', 1),
        ('Thunder Wave', 5), ('Dragon Rage', 11),
        ('Slam', 15), ('Agility', 21),
        ('Safeguard', 27), ('Dragon Tail', 31),
        ('Aqua Tail', 37), ('Dragon Rush', 41),
        ('Hyper Beam', 47), ('Outrage', 51),
    ],
    'Dragonair': [
        ('Wrap', 1), ('Leer', 1), ('Thunder Wave', 1), ('Dragon Rage', 1),
        ('Slam', 15), ('Agility', 21),
        ('Safeguard', 27), ('Dragon Tail', 32),
        ('Aqua Tail', 38), ('Dragon Rush', 44),
        ('Hyper Beam', 51), ('Outrage', 55),
    ],
    'Dragonite': [
        ('Wrap', 1), ('Leer', 1), ('Thunder Wave', 1), ('Dragon Rage', 1),
        ('Slam', 15), ('Agility', 21),
        ('Safeguard', 27), ('Wing Attack', 1),
        ('Aqua Tail', 38), ('Dragon Rush', 44),
        ('Hyper Beam', 51), ('Outrage', 55),
        ('Hurricane', 61),
    ],
    'Mewtwo': [
        ('Confusion', 1), ('Disable', 1),
        ('Barrier', 11), ('Swift', 15),
        ('Future Sight', 19), ('Psych Up', 23),
        ('Me First', 27), ('Amnesia', 31),
        ('Power Swap', 35), ('Guard Swap', 39),
        ('Psychic', 43), ('Recover', 49),
        ('Psystrike', 57),
    ],
    'Mew': [
        ('Pound', 1), ('Transform', 10),
        ('Mega Punch', 20), ('Metronome', 30),
        ('Psychic', 40), ('Ancient Power', 50),
    ],

    # ─── POKÉMON ÉVOLUÉS TARDIFS (stubs si manquants) ────────────────────────
    'Slowbro': [
        ('Curse', 1), ('Yawn', 1), ('Tackle', 1), ('Growl', 1),
        ('Water Gun', 15), ('Confusion', 21),
        ('Disable', 27), ('Headbutt', 33),
        ('Amnesia', 37), ('Psychic', 40),
        ('Rain Dance', 45), ('Withdraw', 1),
    ],
    'Scyther': [  # doublon évité par get_or_create
        ('Vacuum Wave', 1), ('Quick Attack', 1), ('Leer', 1),
        ('Focus Energy', 6), ('Pursuit', 9),
        ('False Swipe', 12), ('Agility', 17),
        ('Wing Attack', 20), ('Fury Cutter', 25),
        ('Slash', 28), ('X-Scissor', 41),
    ],
}


# ==============================================================================
# FONCTION DE MISE À JOUR
# ==============================================================================

def update_learnable_moves_gen3(clear_existing=True):
    """
    Met à jour les PokemonLearnableMove avec les niveaux Gen 3 (FRLG).

    Args:
        clear_existing (bool): Si True, supprime les ancien learnsets avant de recréer.
                               Si False, ajoute/met à jour seulement.
    """
    logging.info("="*70)
    logging.info("MISE À JOUR DES LEARNSETS — GEN 3 (FireRed/LeafGreen)")
    logging.info("="*70)

    total_created = 0
    total_skipped = 0
    pokemon_not_found = []
    move_not_found = []

    for pokemon_name, moves_list in LEARNABLE_MOVES_GEN3.items():
        try:
            pokemon = Pokemon.objects.get(name=pokemon_name)
        except Pokemon.DoesNotExist:
            logging.warning(f"[!] Pokémon introuvable: {pokemon_name}")
            pokemon_not_found.append(pokemon_name)
            continue

        if clear_existing:
            deleted_count, _ = PokemonLearnableMove.objects.filter(pokemon=pokemon).delete()
            if deleted_count:
                logging.debug(f"  [-] {deleted_count} ancien(s) learnset(s) supprimé(s) pour {pokemon_name}")

        for move_name, level in moves_list:
            try:
                move = PokemonMove.objects.get(name=move_name)
            except PokemonMove.DoesNotExist:
                logging.warning(f"  [!] Move introuvable: {move_name} pour {pokemon_name}")
                if move_name not in move_not_found:
                    move_not_found.append(move_name)
                total_skipped += 1
                continue

            _, created = PokemonLearnableMove.objects.get_or_create(
                pokemon=pokemon,
                move=move,
                defaults={'level_learned': level}
            )
            if not created:
                # Mettre à jour le niveau si différent
                PokemonLearnableMove.objects.filter(
                    pokemon=pokemon, move=move
                ).update(level_learned=level)

            if created:
                total_created += 1

    logging.info("="*70)
    logging.info(f"[✓] Learnsets Gen 3 mis à jour!")
    logging.info(f"    — {total_created} entrées créées")
    logging.info(f"    — {total_skipped} moves ignorés (introuvables)")
    if pokemon_not_found:
        logging.warning(f"    — Pokémon introuvables: {pokemon_not_found}")
    if move_not_found:
        logging.warning(f"    — Moves introuvables: {move_not_found}")
    logging.info("="*70)


if __name__ == '__main__':
    update_learnable_moves_gen3()