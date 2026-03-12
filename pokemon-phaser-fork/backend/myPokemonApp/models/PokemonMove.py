#!/usr/bin/python3
"""! @brief Pokemon moves model
"""

from django.db import models
from .PokemonType import PokemonType
from django.core.validators import MinValueValidator, MaxValueValidator

class PokemonMove(models.Model):
    #https://pokemondb.net/move/generation/1
    #A move can raise user's stats
    #or lower oponent's stats or precision
    #it can cause status, flinching, high critical hit or inflict a fixed amount of dm
    #self destruction too
    """Attaque Pokémon"""
    
    MOVE_CATEGORIES = [
        ('physical', 'Physique'),
        ('special', 'Spécial'),
        ('status', 'Statut'),
    ]
    
    name = models.CharField(max_length=50)
    type = models.ForeignKey(PokemonType, on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=MOVE_CATEGORIES)
    power = models.IntegerField(default=0)
    accuracy = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=100
    )
    pp = models.IntegerField(default=5)
    max_pp = models.IntegerField(default=5)
    priority = models.IntegerField(default=0)  # Pour attaques prioritaires
    
    # Effets spéciaux
    effect = models.CharField(max_length=50, blank=True, null=True)
    effect_chance = models.IntegerField(default=0)  # % de chance
    
    # Effets de statut
    inflicts_status = models.CharField(max_length=20, blank=True, null=True)
    
    # Modificateurs de stats
    stat_changes = models.JSONField(default=dict, blank=True)  # Ex: {"attack": 1, "defense": -1}
    
    class Meta:
        verbose_name = "Capacité"
        verbose_name_plural = "Capacités"
    
    def __str__(self):
        return f"{self.name} ({self.type})"