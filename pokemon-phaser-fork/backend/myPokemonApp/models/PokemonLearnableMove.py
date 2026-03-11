#!/usr/bin/python3
"""! @brief PokemonLearnableMove.py — Capacités apprises par un Pokémon (niveau OU TM/CS)
"""

from django.db import models
from .Pokemon import Pokemon
from .PokemonMove import PokemonMove

class PokemonLearnableMove(models.Model):
    """
    Relie un Pokémon (espèce) à une capacité qu'il peut apprendre,
    avec la méthode d'apprentissage et le niveau éventuel.

    learn_method:
      - 'level' : appris en montant de niveau (level_learned > 0)
      - 'tm'    : appris via CT ou CS (TM/HM). level_learned = 0.
                  Respecte les restrictions de compatibilité Gen 9.
    """

    LEARN_METHODS = [
        ('level', 'Montée de niveau'),
        ('tm',    'CT / CS (TM/HM)'),
    ]

    pokemon = models.ForeignKey(
        Pokemon,
        on_delete=models.CASCADE,
        related_name='learnable_moves',
    )
    move = models.ForeignKey(
        PokemonMove,
        on_delete=models.CASCADE,
    )
    # Pour 'level' : niveau auquel le move est appris.
    # Pour 'tm'    : 0 (pas de niveau requis).
    level_learned = models.IntegerField(default=0)

    learn_method = models.CharField(
        max_length=10,
        choices=LEARN_METHODS,
        default='level',
        verbose_name='Méthode d\'apprentissage',
    )

    class Meta:
        # Un Pokémon peut avoir le même move via niveau ET via TM
        # (ex: Tackle appris au niveau 1 ET disponible via CT)
        unique_together = ['pokemon', 'move', 'learn_method']
        ordering = ['learn_method', 'level_learned']
        verbose_name        = "Capacité apprennable"
        verbose_name_plural = "Capacités apprenables"

    def __str__(self):
        if self.learn_method == 'tm':
            return f"{self.pokemon.name} — {self.move.name} (CT/CS)"
        return f"{self.pokemon.name} apprend {self.move.name} (Niv. {self.level_learned})"