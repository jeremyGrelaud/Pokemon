"""
Système de sauvegarde simplifié - utilise Trainer existant
"""

from django.db import models

# ============================================================================
# DRESSEURS VAINCUS
# ============================================================================

class DefeatedTrainer(models.Model):
    """
    Enregistre qu'un joueur a vaincu un Trainer NPC dans une GameSave donnée.

    La contrainte unique_together garantit l'idempotence des insertions :
    on peut appeler add_defeated_trainer() plusieurs fois sans créer de doublons,
    et sans avoir besoin de lire la liste avant d'écrire (pas de race condition).
    """
    game_save   = models.ForeignKey(
        'myPokemonApp.GameSave', on_delete=models.CASCADE, related_name='defeated_trainer_set'
    )
    trainer = models.ForeignKey(
        'myPokemonApp.Trainer', on_delete=models.CASCADE, related_name='defeated_in_saves'
    )

    class Meta:
        unique_together = ['game_save', 'trainer']
        verbose_name    = "Dresseur vaincu"
        indexes = [
            models.Index(fields=['game_save', 'trainer'], name='idx_defeated_save_trainer'),
        ]

    def __str__(self):
        return f"{self.save} → {self.trainer.username} vaincu"