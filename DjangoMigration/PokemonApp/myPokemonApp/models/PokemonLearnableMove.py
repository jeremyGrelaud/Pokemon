#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .Pokemon import Pokemon
from .PokemonMove import PokemonMove

class PokemonLearnableMove(models.Model):
    """Capacités qu'un Pokémon peut apprendre"""
    
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='learnable_moves'
    )
    move = models.ForeignKey(PokemonMove, on_delete=models.CASCADE)
    level_learned = models.IntegerField()
    
    class Meta:
        unique_together = ['pokemon', 'move']
        ordering = ['level_learned']
    
    def __str__(self):
        return f"{self.pokemon.name} apprend {self.move.name} (Niv. {self.level_learned})"