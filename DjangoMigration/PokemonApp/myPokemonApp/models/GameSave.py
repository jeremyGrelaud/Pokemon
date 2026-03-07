"""
Système de sauvegarde simplifié - utilise Trainer existant
"""

from django.db import models
from django.utils import timezone
from .Trainer import Trainer
from .Battle import Battle

# ============================================================================
# SYSTÈME DE SAUVEGARDE
# ============================================================================

class GameSave(models.Model):
    """
    Sauvegarde de la progression du joueur.
    Les dresseurs vaincus sont stockés dans la table DefeatedTrainer
    """

    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='game_saves')

    # Slot de sauvegarde
    slot      = models.IntegerField(default=1, help_text="Numéro du slot (1-3)")
    save_name = models.CharField(max_length=100, blank=True, help_text="Nom personnalisé")

    # Progression
    play_time = models.IntegerField(default=0, help_text="Temps de jeu en secondes")

    # Position du joueur
    current_location    = models.CharField(max_length=100, default="Bourg Palette")
    last_pokemon_center = models.CharField(max_length=100, default="Bourg Palette")

    # Flags d'événements (JSON) — écritures rares, jamais concurrentes → JSONField OK
    story_flags = models.JSONField(default=dict, help_text="Événements complétés")

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    last_saved = models.DateTimeField(auto_now=True)
    is_active  = models.BooleanField(default=True)

    game_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['trainer', 'slot']
        ordering        = ['slot']
        verbose_name    = "Sauvegarde"
        indexes = [
            # Requête fréquente : sauvegarde active d'un joueur
            # → filter(trainer=X, is_active=True)
            models.Index(fields=['trainer', 'is_active'], name='idx_gamesave_trainer_active'),
        ]

    def __str__(self):
        name    = self.save_name or f"Sauvegarde {self.slot}"
        hours   = self.play_time // 3600
        minutes = (self.play_time % 3600) // 60
        return f"{self.trainer.username} - {name} ({hours}h{minutes:02d}m)"

    def get_play_time_display(self):
        hours   = self.play_time // 3600
        minutes = (self.play_time % 3600) // 60
        return f"{hours}h{minutes:02d}m"

    # ── Dresseurs vaincus ────────────────────────────────────────────────────

    def add_defeated_trainer(self, trainer_id):
        """
        Marque un dresseur comme battu.
        Atomique : get_or_create s'appuie sur la contrainte UNIQUE (save, trainer)
        → pas de race condition ni de double-comptage en cas de requêtes simultanées.
        """
        from .DefeatedTrainer import DefeatedTrainer
        DefeatedTrainer.objects.get_or_create(game_save_id=self.pk, trainer_id=trainer_id)


    def is_trainer_defeated(self, trainer_id):
        """
        Vérifie si un dresseur a été battu.
        """
        return self.defeated_trainer_set.filter(trainer_id=trainer_id).exists()

    # ── Story flags ──────────────────────────────────────────────────────────

    def set_story_flag(self, flag_name, value=True):
        """Définit un flag d'événement."""
        self.story_flags[flag_name] = value
        self.save()

    def has_story_flag(self, flag_name):
        """Vérifie un flag d'événement."""
        return self.story_flags.get(flag_name, False)

    # ── Propriétés calculées depuis la snapshot ──────────────────────────────

    @property
    def badges_count(self):
        if self.game_snapshot and 'trainer' in self.game_snapshot:
            return self.game_snapshot['trainer'].get('badges', 0)
        return self.trainer.badges

    @property
    def money(self):
        if self.game_snapshot and 'trainer' in self.game_snapshot:
            return self.game_snapshot['trainer'].get('money', 0)
        return self.trainer.money

    @property
    def pokedex_caught(self):
        if self.game_snapshot and 'pokemon_team' in self.game_snapshot:
            return len(self.game_snapshot['pokemon_team'])
        return self.trainer.pokemon_team.count()

    @property
    def pokedex_seen(self):
        if self.game_snapshot and 'pokemon_team' in self.game_snapshot:
            return len({p.get('species_id') for p in self.game_snapshot['pokemon_team']})
        return self.trainer.pokemon_team.values('species').distinct().count()



# ============================================================================
# HISTORIQUE DES COMBATS
# ============================================================================

class TrainerBattleHistory(models.Model):
    """
    Historique des combats entre dresseurs.
    Simplifié - utilise directement Trainer existant.
    """

    player   = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='battle_history_as_player')
    opponent = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='battle_history_as_opponent')

    player_won = models.BooleanField()
    battle     = models.ForeignKey(Battle, on_delete=models.SET_NULL, null=True, blank=True)

    money_earned = models.IntegerField(default=0)
    fought_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering     = ['-fought_at']
        verbose_name = "Historique Combat"

    def __str__(self):
        result = "Victoire" if self.player_won else "Défaite"
        return f"{self.player.username} vs {self.opponent.username} - {result}"