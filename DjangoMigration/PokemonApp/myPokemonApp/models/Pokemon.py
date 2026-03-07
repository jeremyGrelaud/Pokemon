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

    # -------------------------------------------------------------------------
    # EV Yields / Source : FRLG / Bulbapedia — Gen 3+
    # -------------------------------------------------------------------------
    ev_yield_hp              = models.PositiveSmallIntegerField(default=0, verbose_name='EV HP')
    ev_yield_attack          = models.PositiveSmallIntegerField(default=0, verbose_name='EV Attaque')
    ev_yield_defense         = models.PositiveSmallIntegerField(default=0, verbose_name='EV Défense')
    ev_yield_special_attack  = models.PositiveSmallIntegerField(default=0, verbose_name='EV Att. Spé.')
    ev_yield_special_defense = models.PositiveSmallIntegerField(default=0, verbose_name='EV Déf. Spé.')
    ev_yield_speed           = models.PositiveSmallIntegerField(default=0, verbose_name='EV Vitesse')

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

    def get_ev_yields(self) -> list[tuple[str, int]]:
        """
        Retourne la liste des EVs accordés par ce Pokémon sous la forme :
            [('ev_hp', 2), ('ev_speed', 1), ...]

        Seules les stats avec un yield > 0 sont incluses.
        """
        mapping = [
            ('ev_hp',              self.ev_yield_hp),
            ('ev_attack',          self.ev_yield_attack),
            ('ev_defense',         self.ev_yield_defense),
            ('ev_special_attack',  self.ev_yield_special_attack),
            ('ev_special_defense', self.ev_yield_special_defense),
            ('ev_speed',           self.ev_yield_speed),
        ]
        return [(field, amount) for field, amount in mapping if amount > 0]