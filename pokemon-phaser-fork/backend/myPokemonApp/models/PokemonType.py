#!/usr/bin/python3
"""! @brief Pokemon type model
"""

from django.db import models

class PokemonType(models.Model):
    """Type d'un Pokémon (Feu, Eau, Plante, etc.)"""
    name = models.CharField(max_length=20, unique=True)
    
    # Table des efficacités de type (pour optimisation)
    strong_against = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='weak_against',
        blank=True
    )
    
    class Meta:
        verbose_name = "Type de Pokémon"
        verbose_name_plural = "Types de Pokémon"
    
    def __str__(self):
        return self.name
    
    def get_effectiveness(self, defending_type):
        """Retourne l'efficacité de ce type contre un type défenseur"""
        if defending_type in self.strong_against.all():
            return 2.0
        elif self in defending_type.strong_against.all():
            return 0.5
        return 1.0
        