#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .Pokemon import Pokemon
from .PokemonMove import PokemonMove



class PokemonLearnableMove(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name='learnable_moves')
    move = models.ForeignKey(PokemonMove, on_delete=models.CASCADE)
    LearnableAtLevel = models.IntegerField()

    def __str__(self):
        return f"[{self.pokemon.name}] learns {self.move.name} at level {self.LearnableAtLevel}"