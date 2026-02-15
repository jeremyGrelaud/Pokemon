#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models


class Item(models.Model):
    """Objet utilisable (potions, balls, objets d'évolution, etc.)"""
    
    ITEM_TYPES = [
        ('potion', 'Potion'),
        ('pokeball', 'Poké Ball'),
        ('evolution', 'Pierre d\'évolution'),
        ('status', 'Soin de statut'),
        ('battle', 'Objet de combat'),
        ('held', 'Objet tenu'),
        ('key', 'Objet clé'),
    ]
    
    name = models.CharField(max_length=50)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    price = models.IntegerField(default=0)
    
    # Effets
    heal_amount = models.IntegerField(default=0)  # HP restaurés
    heal_percentage = models.IntegerField(default=0)  # % HP restaurés
    cures_status = models.BooleanField(default=False)
    specific_status = models.CharField(max_length=20, blank=True, null=True)
    
    # Poké Balls
    catch_rate_modifier = models.FloatField(default=1.0)
    
    # Évolutions
    evolves_pokemon = models.CharField(max_length=50, blank=True, null=True)
    
    # Objet tenu
    held_effect = models.CharField(max_length=100, blank=True, null=True)
    
    is_consumable = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Objet"
        verbose_name_plural = "Objets"
    
    def __str__(self):
        return self.name
    
    def use_on_pokemon(self, pokemon):
        """Utilise l'objet sur un Pokémon"""
        if pokemon.nickname:
            name = pokemon.nickname
        else:
            name = pokemon.species.name
        
        if self.item_type == 'potion':
            healed = min(self.heal_amount, pokemon.max_hp - pokemon.current_hp)
            pokemon.current_hp += healed
            pokemon.save()
            return f"{name} a récupéré {healed} HP!"
        
        elif self.item_type == 'status' and self.cures_status:
            if self.specific_status:
                if pokemon.status == self.specific_status:
                    pokemon.status = None
                    pokemon.save()
                    return f"{name} est guéri de {self.specific_status}!"
            else:
                old_status = pokemon.status
                pokemon.status = None
                pokemon.save()
                return f"{name} est guéri de {old_status}!"
        
        elif self.item_type == 'evolution':
            # Logique d'évolution par pierre
            return pokemon.check_stone_evolution(self)
        
        return "Aucun effet."

