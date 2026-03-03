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

    # -------------------------------------------------------------------------
    # Talents (Abilities)
    # ability_1     : talent normal principal  (toujours présent)
    # ability_2     : second talent normal     (nullable — certaines espèces n'en ont qu'un)
    # hidden_ability: talent caché             (nullable — accessible via breed ou events)
    # -------------------------------------------------------------------------
    ability_1 = models.ForeignKey(
        'Ability',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='species_slot_1',
        verbose_name='Talent 1',
    )
    ability_2 = models.ForeignKey(
        'Ability',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='species_slot_2',
        verbose_name='Talent 2',
    )
    hidden_ability = models.ForeignKey(
        'Ability',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='species_hidden',
        verbose_name='Talent Caché',
    )

    class Meta:
        verbose_name = "Pokémon (Base)"
        verbose_name_plural = "Pokémon (Bases)"
        ordering = ['pokedex_number']
    
    def __str__(self):
        return f"#{self.pokedex_number:03d} {self.name}"

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def get_ability_pool(self, allow_hidden=True):
        """
        Retourne la liste des talents disponibles avec leur poids de tirage.
        Format : [(Ability, weight), ...]

        Poids par défaut (inspirés de la série principale) :
          - ability_1 seul         → 100 %
          - ability_1 + ability_2  → 50 % / 50 % (normal), 10 % caché
          - hidden_ability         → 10 % si allow_hidden=True
        """
        pool = []

        has_two_normal = self.ability_1_id and self.ability_2_id
        weight_normal = 45 if (has_two_normal and allow_hidden and self.hidden_ability_id) else \
                        50 if has_two_normal else 100

        if self.ability_1_id:
            pool.append((self.ability_1, weight_normal))
        if self.ability_2_id:
            pool.append((self.ability_2, weight_normal))
        if allow_hidden and self.hidden_ability_id:
            pool.append((self.hidden_ability, 10))

        return pool