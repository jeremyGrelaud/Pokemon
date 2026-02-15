#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .Pokemon import Pokemon
from .Item import Item


class PokemonEvolution(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name='evolutions')
    evolutionLevel = models.IntegerField()
    evolvesTo = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name='evolved_from')



class PokemonEvolution(models.Model):
    """Définit les évolutions possibles"""
    
    EVOLUTION_METHODS = [
        ('level', 'Niveau'),
        ('stone', 'Pierre'),
        ('trade', 'Échange'),
        ('friendship', 'Bonheur'),
        ('item', 'Objet'),
    ]
    
    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='evolutions_from'
    )
    evolves_to = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='evolutions_to'
    )
    
    method = models.CharField(max_length=20, choices=EVOLUTION_METHODS)
    level = models.IntegerField(blank=True, null=True)
    required_item = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = "Évolution"
        unique_together = ['pokemon', 'evolves_to']
    
    def __str__(self):
        return f"{self.pokemon.name} → {self.evolves_to.name}"
