#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .Pokemon import Pokemon


class PokemonEvolution(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name='evolutions')
    evolutionLevel = models.IntegerField()
    evolvesTo = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name='evolved_from')