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

