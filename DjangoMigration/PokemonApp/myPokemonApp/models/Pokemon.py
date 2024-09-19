#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .PokemonMove import PokemonMove
from .PokemonType import PokemonType

#main big file where all pokemons are initialized with their stats, types ... and also which moves they can learn and when do they evolve...
#from moves import All_Moves, display_pokemon_moves, find_move, get_move_info_in_line
#import random


class Pokemon(models.Model):

    name = models.TextField()
    level = models.IntegerField()
    type = models.ForeignKey(PokemonType, on_delete=models.CASCADE, verbose_name="PokemonType")
    hp =  models.IntegerField()
    attack =  models.IntegerField()
    defense =  models.IntegerField()
    specialAttack = models.IntegerField()
    specialDefense = models.IntegerField()
    speed = models.IntegerField()
    moves  = models.ManyToManyField(PokemonMove, verbose_name="Pokemon's List of moves")
    catchRate = models.IntegerField()
    baseExperience = models.IntegerField()
    experience = models.IntegerField() 
    maxHp = models.IntegerField()
    status = models.TextField() #TODO

    
    def __str__(self) -> str:
        strPokemon = f"Name: {self.name}\n"+\
                        f"Level: {self.level}\n"+\
                        f"Type: {self.type}\n"+\
                        f"HP: {self.hp}\n"+\
                        f"Attack: {self.attack}\n"+\
                        f"Defense: {self.defense}\n"+\
                        f"Special Attack: {self.specialAttack}\n"+\
                        f"Special Defense: {self.specialDefense}\n"+\
                        f"Speed: {self.speed}"
        return str(strPokemon)



########################Start All Pokemons###############################
class All_Pokemons:
    instance = None
    def __init__(self):
        self.pokemon_list = []
        pokemon_data = [
            ("Abra", 1, "psychic", 25, 20, 15, 105, 55, 90, ["Teleport"], 62, 25),
            ("Aerodactyl", 2, "rock", 80, 105, 65, 130, 60, 75, ["Bite", "Wing Attack"], 180, 45),
            ("Alakazam", 3, "psychic", 55, 50, 45, 135, 95, 120, ["Teleport", "Kinesis", "Psychic"], 250, 50),
            ("Arbok", 2, "poison", 60, 95, 69, 65, 79, 80, ["Wrap", "Poison Sting", "Bite"], 157, 90),
            ("Arcanine", 2, "fire", 90, 110, 80, 100, 80, 95, ["Bite", "Roar", "Flamethrower"], 194, 75),
            ("Articuno", 3, "ice", 90, 85, 100, 95, 125, 85, ["Peck", "Ice Beam", "Blizzard"], 290, 3),
            ("Beedrill", 3, "bug", 65, 90, 40, 45, 80, 75, ["Fury Attack", "Twineedle"], 198, 45),
            ("Bellsprout", 1, "grass", 50, 75, 35, 70, 30, 40, ["Vine Whip", "Growth"], 60, 255),
            ("Blastoise", 3, "water", 79, 83, 100, 85, 105, 78, ["Tackle", "Tail Whip", "Bubble", "Hydro Pump"], 265, 45),
            ("Bulbasaur", 1, "grass", 45, 49, 49, 65, 65, 45, ["Tackle", "Growl"], 64, 45),
            ("Butterfree", 3, "bug", 60, 45, 50, 90, 80, 70, ["Confusion", "Poison Powder", "Stun Spore"], 198, 45),
            ("Caterpie", 1, "bug", 45, 30, 35, 20, 20, 45, ["Tackle"], 39, 255),
            ("Chansey", 1, "normal", 250, 5, 5, 35, 105, 50, ["Pound", "Growl"], 395, 30),
            ("Charizard", 3, "fire", 78, 84, 78, 109, 85, 100, ["Scratch", "Growl", "Ember", "Flamethrower"], 267, 45),
            ("Charmander", 1, "fire", 39, 52, 43, 60, 50, 65, ["Scratch", "Growl"], 62, 45),
            ("Charmeleon", 2, "fire", 58, 64, 58, 80, 65, 80, ["Scratch", "Growl", "Ember"], 142, 45),
            ("Clefable", 2, "fairy", 95, 70, 73, 95, 90, 60, ["Pound", "Growl", "Double Slap"], 242, 25),
            ("Clefairy", 1, "fairy", 70, 45, 48, 60, 65, 35, ["Pound", "Growl"], 113, 150),
            ("Cloyster", 2, "water", 50, 95, 180, 85, 45, 70, ["Tackle", "Withdraw", "Ice Beam"], 184, 60),
            ("Cubone", 1, "ground", 50, 50, 95, 40, 50, 35, ["Bone Club", "Growl"], 64, 190),
            ("Dewgong", 2, "water", 90, 70, 80, 70, 95, 70, ["Headbutt", "Growl", "Aurora Beam"], 166, 75),
            ("Diglett", 1, "ground", 10, 55, 25, 35, 45, 95, ["Scratch", "Growl"], 53, 255),
            ("Ditto", 1, "normal", 48, 48, 48, 48, 48, 48, ["Transform"], 101, 35),
            ("Dodrio", 2, "normal", 60, 110, 70, 60, 60, 100, ["Peck", "Growl", "Drill Peck"], 165, 45),
            ("Doduo", 1, "normal", 35, 85, 45, 35, 35, 75, ["Peck", "Growl"], 62, 190),
            ("Dragonair", 2, "dragon", 61, 84, 65, 70, 70, 70, ["Wrap", "Leer", "Thunder Wave"], 147, 45),
            ("Dragonite", 3, "dragon", 91, 134, 95, 80, 100, 100, ["Wrap", "Leer", "Thunder Wave", "Dragon Rage"], 300, 45),
            ("Dratini", 1, "dragon", 41, 64, 45, 50, 50, 50, ["Wrap", "Leer"], 60, 45),
            ("Drowzee", 1, "psychic", 60, 48, 45, 43, 90, 42, ["Pound", "Hypnosis"], 66, 190),
            ("Dugtrio", 2, "ground", 35, 100, 50, 50, 70, 120, ["Scratch", "Growl", "Slash"], 149, 50),
            ("Eevee", 1, "normal", 55, 55, 50, 65, 65, 55, ["Quick Attack", "Tail Whip"], 65, 45),
            ("Ekans", 1, "poison", 35, 60, 44, 40, 54, 55, ["Wrap", "Poison Sting"], 58, 255),
            ("Electabuzz", 1, "electric", 65, 83, 57, 105, 95, 85, ["Quick Attack", "Thunder Punch"], 172, 45),
            ("Electrode", 2, "electric", 60, 50, 70, 80, 80, 150, ["Tackle", "Screech", "Thunder Shock"], 172, 60),
            ("Exeggcute", 1, "grass", 60, 40, 80, 60, 45, 40, ["Barrage", "Hypnosis"], 65, 90),
            ("Exeggutor", 2, "grass", 95, 95, 85, 125, 65, 55, ["Barrage", "Hypnosis", "Egg Bomb"], 186, 45),
            ("Farfetch'd", 1, "normal", 52, 65, 55, 60, 58, 62, ["Peck", "Sand Attack"], 132, 45),
            ("Fearow", 2, "normal", 65, 90, 65, 61, 61, 100, ["Peck", "Drill Peck"], 155, 90),
            ("Flareon", 2, "fire", 65, 130, 60, 95, 110, 65, ["Quick Attack", "Tail Whip", "Ember"], 184, 45),
            ("Gastly", 1, "ghost", 30, 35, 30, 100, 35, 80, ["Lick", "Spite"], 62, 190),
            ("Gengar", 3, "ghost", 60, 65, 60, 130, 75, 110, ["Lick", "Spite", "Hypnosis", "Dream Eater"], 250, 45),
            ("Geodude", 1, "rock", 40, 80, 100, 30, 30, 20, ["Tackle", "Defense Curl"], 60, 255),
            ("Gloom", 2, "grass", 60, 65, 70, 85, 75, 40, ["Absorb", "Acid"], 138, 120),
            ("Golbat", 2, "poison", 75, 80, 70, 65, 75, 90, ["Leech Life", "Supersonic", "Bite"], 159, 90),
            ("Goldeen", 1, "water", 45, 67, 60, 63, 35, 50, ["Peck", "Tail Whip"], 64, 255),
            ("Golduck", 2, "water", 80, 82, 78, 95, 80, 85, ["Scratch", "Tail Whip", "Hydro Pump"], 175, 75),
            ("Golem", 3, "rock", 80, 110, 130, 55, 65, 45, ["Tackle", "Defense Curl", "Rock Throw", "Earthquake"], 248, 45),
            ("Graveler", 2, "rock", 55, 95, 115, 45, 45, 35, ["Tackle", "Defense Curl", "Rock Throw"], 137, 120),
            ("Grimer", 1, "poison", 80, 80, 50, 25, 40, 50, ["Pound", "Poison Gas"], 65, 190),
            ("Growlithe", 1, "fire", 55, 70, 45, 70, 50, 60, ["Bite", "Roar"], 70, 190),
            ("Gyarados", 2, "water", 95, 125, 79, 81, 60, 100, ["Bite", "Hydro Pump"], 189, 45),
            ("Haunter", 2, "ghost", 45, 50, 45, 115, 55, 95, ["Lick", "Spite", "Hypnosis"], 142, 90),
            ("Hitmonchan", 1, "fighting", 50, 105, 79, 35, 110, 76, ["Mega Punch", "Fire Punch"], 159, 45),
            ("Hitmonlee", 1, "fighting", 50, 120, 53, 35, 110, 87, ["Mega Kick", "Jump Kick"], 159, 45),
            ("Horsea", 1, "water", 30, 40, 70, 70, 25, 60, ["Bubble", "Smokescreen"], 59, 225),
            ("Hypno", 2, "psychic", 85, 73, 70, 73, 115, 67, ["Pound", "Hypnosis", "Psychic"], 169, 75),
            ("Ivysaur", 2, "grass", 60, 62, 63, 80, 80, 60, ["Tackle", "Growl", "Leech Seed"], 142, 45),
            ("Jigglypuff", 1, "normal", 115, 45, 20, 45, 25, 20, ["Sing", "Pound"], 95, 170),
            ("Jolteon", 2, "electric", 65, 65, 60, 110, 95, 130, ["Quick Attack", "Tail Whip", "Thunder Shock"], 184, 45),
            ("Jynx", 1, "ice", 65, 50, 35, 95, 115, 95, ["Pound", "Lick"], 159, 45),
            ("Kabutops", 2, "rock", 60, 115, 105, 80, 70, 80, ["Scratch", "Harden", "Slash"], 173, 45),
            ("Kabuto", 1, "rock", 30, 80, 90, 55, 45, 55, ["Scratch", "Harden"], 71, 45),
            ("Kadabra", 2, "psychic", 40, 35, 30, 120, 70, 105, ["Teleport", "Kinesis"], 140, 100),
            ("Kakuna", 2, "bug", 45, 25, 50, 25, 25, 35, ["Harden"], 72, 120),
            ("Kangaskhan", 2, "normal", 105, 95, 80, 90, 40, 80, ["Bite", "Tail Whip", "Rage"], 172, 45),
            ("Kingler", 2, "water", 55, 130, 115, 50, 50, 75, ["Bubble", "Leer", "Vice Grip"], 166, 60),
            ("Koffing", 1, "poison", 40, 65, 95, 60, 45, 35, ["Tackle", "Smog"], 68, 190),
            ("Krabby", 1, "water", 30, 105, 90, 25, 25, 50, ["Bubble", "Leer"], 65, 225),
            ("Lapras", 2, "water", 130, 85, 80, 85, 95, 60, ["Growl", "Water Gun"], 187, 45),
            ("Lickitung", 1, "normal", 90, 55, 75, 60, 75, 30, ["Lick", "Supersonic"], 77, 45),
            ("Machamp", 3, "fighting", 90, 130, 80, 65, 85, 55, ["Low Kick", "Leer", "Karate Chop", "Submission"], 253, 45),
            ("Machoke", 2, "fighting", 80, 100, 70, 50, 60, 45, ["Low Kick", "Leer", "Karate Chop"], 142, 90),
            ("Machop", 1, "fighting", 70, 80, 50, 35, 35, 35, ["Low Kick", "Leer"], 61, 180),
            ("Magikarp", 1, "water", 20, 10, 55, 80, 15, 20, ["Splash"], 40, 255),
            ("Magmar", 1, "fire", 65, 95, 57, 93, 100, 85, ["Ember", "Smokescreen"], 173, 45),
            ("Magnemite", 1, "electric", 25, 35, 70, 95, 55, 45, ["Tackle", "Sonic Boom"], 65, 190),
            ("Magneton", 2, "electric", 50, 60, 95, 120, 70, 70, ["Tackle", "Sonic Boom", "Thunder Shock"], 163, 60),
            ("Mankey", 1, "fighting", 40, 80, 35, 35, 45, 70, ["Scratch", "Leer"], 61, 190),
            ("Marowak", 2, "ground", 60, 80, 110, 50, 80, 45, ["Bone Club", "Growl", "Headbutt"], 149, 75),
            ("Meowth", 1, "normal", 40, 45, 35, 40, 40, 90, ["Scratch", "Growl"], 58, 255),
            ("Metapod", 2, "bug", 50, 20, 55, 25, 25, 30, ["Harden"], 72, 120),
            ("Mew", 3, "psychic", 100, 100, 100, 100, 100, 100, ["Pound", "Mega Punch", "Psychic"], 300, 45),
            ("Mewtwo", 3, "psychic", 106, 110, 90, 130, 154, 90, ["Psycho Cut", "Swift", "Psystrike"], 340, 3),
            ("Moltres", 3, "fire", 90, 100, 90, 125, 85, 90, ["Peck", "Ember", "Fire Blast"], 290, 3),
            ("Mr. Mime", 1, "psychic", 40, 45, 65, 90, 100, 120, ["Confusion", "Barrier"], 161, 45),
            ("Muk", 2, "poison", 105, 105, 75, 50, 65, 100, ["Pound", "Poison Gas", "Sludge"], 175, 75),
            ("Nidoking", 3, "poison", 81, 102, 77, 85, 75, 85, ["Peck", "Tail Whip", "Horn Attack", "Thrash"], 253, 45),
            ("Nidoqueen", 3, "poison", 90, 92, 87, 75, 85, 76, ["Scratch", "Tail Whip", "Double Kick", "Body Slam"], 253, 45),
            ("Nidoran♀", 1, "poison", 55, 47, 52, 40, 40, 41, ["Scratch", "Tail Whip"], 55, 235),
            ("Nidoran♂", 1, "poison", 46, 57, 40, 40, 40, 50, ["Peck", "Tail Whip"], 55, 235),
            ("Nidorina", 2, "poison", 70, 62, 67, 55, 55, 56, ["Scratch", "Tail Whip", "Double Kick"], 128, 120),
            ("Nidorino", 2, "poison", 61, 72, 57, 55, 55, 65, ["Peck", "Tail Whip", "Horn Attack"], 128, 120),
            ("Ninetales", 2, "fire", 73, 76, 75, 81, 100, 100, ["Ember", "Tail Whip", "Fire Spin"], 177, 75),
            ("Oddish", 1, "grass", 45, 50, 55, 75, 65, 30, ["Absorb"], 64, 255),
            ("Omanyte", 1, "rock", 35, 40, 100, 90, 55, 35, ["Bite", "Withdraw"], 71, 45),
            ("Omastar", 2, "rock", 70, 60, 125, 115, 70, 55, ["Bite", "Withdraw", "Rock Slide"], 173, 45),
            ("Onix", 1, "rock", 35, 45, 160, 30, 45, 70, ["Tackle", "Screech"], 77, 45),
            ("Paras", 1, "bug", 35, 70, 55, 45, 55, 25, ["Scratch", "Stun Spore"], 57, 190),
            ("Parasect", 2, "bug", 60, 95, 80, 60, 80, 30, ["Scratch", "Stun Spore", "Slash"], 142, 75),
            ("Persian", 2, "normal", 65, 70, 60, 65, 65, 115, ["Scratch", "Growl", "Bite"], 154, 90),
            ("Pidgeot", 3, "normal", 83, 80, 75, 70, 70, 101, ["Tackle", "Gust", "Sand Attack", "Wing Attack"], 240, 45),
            ("Pidgeotto", 2, "normal", 63, 60, 55, 50, 50, 71, ["Tackle", "Gust", "Sand Attack"], 122, 120),
            ("Pidgey", 1, "normal", 40, 45, 40, 35, 35, 56, ["Tackle", "Gust"], 50, 255),
            ("Pikachu", 1, "electric", 35, 55, 40, 50, 50, 90, ["Thunder Shock", "Growl"], 112, 190),
            ("Pinsir", 1, "bug", 65, 125, 100, 85, 55, 70, ["Vice Grip", "Seismic Toss"], 175, 45),
            ("Poliwag", 1, "water", 40, 50, 40, 40, 40, 90, ["Bubble", "Hypnosis"], 60, 255),
            ("Poliwhirl", 2, "water", 65, 65, 65, 50, 50, 90, ["Bubble", "Hypnosis", "Double Slap"], 135, 120),
            ("Poliwrath", 3, "water", 90, 85, 95, 70, 90, 70, ["Bubble", "Hypnosis", "Double Slap", "Submission"], 255, 45),
            ("Ponyta", 1, "fire", 50, 85, 55, 65, 65, 90, ["Tackle", "Growl"], 82, 190),
            ("Porygon", 1, "normal", 65, 60, 70, 85, 75, 40, ["Tackle", "Sharpen"], 79, 45),
            ("Primeape", 2, "fighting", 65, 105, 60, 60, 70, 95, ["Scratch", "Leer", "Low Kick"], 159, 75),
            ("Psyduck", 1, "water", 50, 52, 48, 65, 50, 55, ["Scratch", "Tail Whip"], 64, 190),
            ("Raichu", 2, "electric", 60, 90, 55, 90, 80, 110, ["Thunder Shock", "Growl", "Thunderbolt"], 243, 75),
            ("Rapidash", 2, "fire", 65, 100, 70, 80, 80, 105, ["Tackle", "Growl", "Stomp"], 175, 60),
            ("Raticate", 2, "normal", 55, 81, 60, 50, 70, 97, ["Tackle", "Tail Whip", "Hyper Fang"], 145, 127),
            ("Rattata", 1, "normal", 30, 56, 35, 25, 35, 72, ["Tackle", "Tail Whip"], 51, 255),
            ("Rhydon", 2, "rock", 105, 130, 120, 45, 45, 40, ["Horn Attack", "Stomp", "Earthquake"], 170, 60),
            ("Rhyhorn", 1, "rock", 80, 85, 95, 30, 30, 25, ["Horn Attack", "Stomp"], 69, 120),
            ("Sandshrew", 1, "ground", 50, 75, 85, 20, 30, 40, ["Scratch", "Defense Curl"], 60, 255),
            ("Sandslash", 2, "ground", 75, 100, 110, 45, 55, 65, ["Scratch", "Defense Curl", "Sand Attack"], 158, 90),
            ("Scyther", 1, "bug", 70, 110, 80, 105, 55, 80, ["Quick Attack", "Leer"], 100, 45),
            ("Seadra", 2, "water", 55, 65, 95, 95, 45, 85, ["Bubble", "Smokescreen", "Water Gun"], 154, 45),
            ("Seaking", 2, "water", 80, 92, 65, 68, 65, 80, ["Peck", "Tail Whip", "Horn Attack"], 158, 60),
            ("Seel", 1, "water", 65, 45, 55, 45, 70, 45, ["Headbutt", "Growl"], 65, 190),
            ("Shellder", 1, "water", 30, 65, 100, 45, 25, 40, ["Tackle", "Withdraw"], 61, 190),
            ("Slowbro", 2, "water", 95, 75, 110, 100, 80, 30, ["Tackle", "Growl", "Confusion"], 172, 75),
            ("Slowpoke", 1, "water", 90, 65, 65, 40, 40, 15, ["Tackle", "Growl"], 63, 190),
            ("Snorlax", 2, "normal", 160, 110, 65, 30, 65, 110, ["Tackle", "Rest"], 189, 25),
            ("Spearow", 1, "normal", 40, 60, 30, 31, 31, 70, ["Peck"], 52, 255),
            ("Squirtle", 1, "water", 44, 48, 65, 50, 64, 43, ["Tackle", "Tail Whip"], 63, 45),
            ("Starmie", 2, "water", 60, 75, 85, 115, 100, 85, ["Tackle", "Harden", "Water Gun"], 182, 60),
            ("Staryu", 1, "water", 30, 45, 55, 85, 70, 55, ["Tackle", "Harden"], 68, 225),
            ("Tangela", 1, "grass", 65, 55, 115, 100, 40, 60, ["Bind", "Absorb"], 87, 45),
            ("Tauros", 1, "normal", 75, 100, 95, 110, 40, 70, ["Tackle", "Stomp"], 172, 45),
            ("Tentacool", 1, "water", 40, 40, 35, 50, 100, 70, ["Acid", "Poison Sting"], 67, 190),
            ("Tentacruel", 2, "water", 80, 70, 65, 80, 120, 100, ["Acid", "Poison Sting", "Wrap"], 180, 60),
            ("Vaporeon", 2, "water", 130, 65, 60, 110, 95, 65, ["Quick Attack", "Tail Whip", "Water Gun"], 184, 45),
            ("Venomoth", 2, "bug", 70, 65, 60, 90, 75, 90, ["Tackle", "Poison Powder", "Confusion"], 158, 75),
            ("Venonat", 1, "bug", 60, 55, 50, 40, 55, 45, ["Tackle", "Poison Powder"], 61, 190),
            ("Venusaur", 3, "grass", 80, 82, 83, 100, 100, 80, ["Tackle", "Growl", "Leech Seed", "Vine Whip"], 263, 45),
            ("Victreebel", 3, "grass", 80, 105, 65, 100, 70, 70, ["Vine Whip", "Growth", "Razor Leaf", "Sleep Powder"], 245, 45),
            ("Vileplume", 3, "grass", 75, 80, 85, 100, 90, 50, ["Absorb", "Acid", "Petal Dance"], 245, 45),
            ("Voltorb", 1, "electric", 40, 30, 50, 55, 55, 100, ["Tackle", "Screech"], 66, 190),
            ("Vulpix", 1, "fire", 38, 41, 40, 50, 65, 65, ["Ember", "Tail Whip"], 60, 190),
            ("Wartortle", 2, "water", 59, 63, 80, 65, 80, 58, ["Tackle", "Tail Whip", "Bubble"], 142, 45),
            ("Weedle", 1, "bug", 40, 35, 30, 20, 20, 50, ["Poison Sting"], 39, 255),
            ("Weepinbell", 2, "grass", 65, 90, 50, 85, 45, 55, ["Vine Whip", "Growth", "Razor Leaf"], 137, 120),
            ("Weezing", 2, "poison", 65, 90, 120, 85, 70, 60, ["Tackle", "Smog", "Sludge"], 172, 60),
            ("Wigglytuff", 2, "normal", 140, 70, 45, 85, 50, 45, ["Sing", "Pound", "Double Slap"], 218, 50),
            ("Zapdos", 3, "electric", 90, 90, 85, 125, 90, 100, ["Peck", "Thunder Shock", "Thunderbolt"], 290, 3),
            ("Zubat", 1, "poison", 40, 45, 35, 30, 40, 55, ["Leech Life", "Supersonic"], 49, 255)
        ]

        
        # Iterate over the pokemon data and create each pokemon
        for data in pokemon_data:
            #pokemon = create_pokemon(*data)
            #self.pokemon_list.append(pokemon)
            pass
        

    #binary search for a list in alphabetical order
    def better_find_pokemon_by_name(self, name):
        low = 0
        high = len(self.pokemon_list) - 1
        while low <= high:
            mid = (low + high) // 2
            guess = self.pokemon_list[mid]
            if guess.name == name:
                return guess #we return the poke
            if guess.name > name:
                high = mid - 1
            else:
                low = mid + 1
        return None
#############################End All Pokemons#################################