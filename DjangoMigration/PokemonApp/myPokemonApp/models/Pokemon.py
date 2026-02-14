#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .PokemonType import PokemonType
class Pokemon(models.Model):
    """Modèle de base pour un Pokémon (template)"""
    
    name = models.CharField(max_length=50, unique=True)
    pokedex_number = models.IntegerField(unique=True)
    
    # Types
    primary_type = models.ForeignKey(
        PokemonType, 
        on_delete=models.CASCADE,
        related_name='primary_pokemon'
    )
    secondary_type = models.ForeignKey(
        PokemonType,
        on_delete=models.CASCADE,
        related_name='secondary_pokemon',
        blank=True,
        null=True
    )
    
    # Stats de base
    base_hp = models.IntegerField()
    base_attack = models.IntegerField()
    base_defense = models.IntegerField()
    base_special_attack = models.IntegerField()
    base_special_defense = models.IntegerField()
    base_speed = models.IntegerField()
    
    # Métadonnées
    catch_rate = models.IntegerField(default=45)
    base_experience = models.IntegerField()
    growth_rate = models.CharField(max_length=20, default='medium_fast')
    
    # Sprite/Image
    sprite_url = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Pokémon (Base)"
        verbose_name_plural = "Pokémon (Bases)"
        ordering = ['pokedex_number']
    
    def __str__(self):
        return f"#{self.pokedex_number:03d} {self.name}"

