"""
Modèles pour le système de capture
"""

from django.db import models
from django.utils import timezone
from .Pokemon import Pokemon
from .Trainer import Trainer
from .Item import Item
from .PokemonType import PokemonType
from .PlayablePokemon import PlayablePokemon

class CaptureAttempt(models.Model):
    """Enregistre chaque tentative de capture"""
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='capture_attempts')
    pokemon_species = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    
    # Détails de la tentative
    ball_used = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    pokemon_level = models.IntegerField()
    pokemon_hp_percent = models.FloatField(help_text="% HP au moment de la capture")
    pokemon_status = models.CharField(max_length=20, blank=True, null=True)
    
    # Résultat
    success = models.BooleanField()
    capture_rate = models.FloatField(help_text="Probabilité calculée (0-1)")
    shakes = models.IntegerField(default=0, help_text="Nombre de shakes avant capture/échec")
    
    # Métadonnées
    attempted_at = models.DateTimeField(default=timezone.now)
    battle = models.ForeignKey('Battle', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-attempted_at']
        verbose_name = "Tentative de Capture"
        verbose_name_plural = "Tentatives de Capture"
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.pokemon_species.name} - {self.trainer.username} ({self.attempted_at.strftime('%Y-%m-%d')})"


class CaptureJournal(models.Model):
    """Journal des captures réussies (pour stats et achievements)"""
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='capture_journal')
    pokemon = models.ForeignKey(PlayablePokemon, on_delete=models.CASCADE, related_name='capture_entry')
    
    # Circonstances de la capture
    captured_at = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=100, blank=True)
    ball_used = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    attempts_before_success = models.IntegerField(default=1)
    
    # Stats au moment de la capture
    level_at_capture = models.IntegerField()
    hp_at_capture = models.IntegerField()
    
    # Achievements
    is_first_catch = models.BooleanField(default=False, help_text="Premier de cette espèce")
    is_shiny = models.BooleanField(default=False)
    is_critical_catch = models.BooleanField(default=False, help_text="Capture critique (1 shake)")
    
    class Meta:
        ordering = ['-captured_at']
        verbose_name = "Entrée Journal de Capture"
        verbose_name_plural = "Journal de Captures"
    
    def __str__(self):
        return f"{self.pokemon.species.name} capturé par {self.trainer.username} le {self.captured_at.strftime('%d/%m/%Y')}"


class PokeballItem(models.Model):
    """Extension du modèle Item pour les Poké Balls avec bonus"""
    
    item = models.OneToOneField(Item, on_delete=models.CASCADE, primary_key=True)

    # Bonus de capture in item.catch_rate_modifier
    
    # Conditions spéciales
    bonus_on_type = models.ForeignKey(
        PokemonType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Bonus sur un type spécifique"
    )
    bonus_on_status = models.CharField(
        max_length=20,
        blank=True,
        help_text="Bonus si Pokémon a ce status (burn, sleep, etc.)"
    )
    
    # Effets spéciaux
    guaranteed_capture = models.BooleanField(default=False, help_text="Master Ball")
    critical_catch_bonus = models.FloatField(default=0.0, help_text="Chance de capture critique")
    
    class Meta:
        verbose_name = "Poké Ball (Stats)"
        verbose_name_plural = "Poké Balls (Stats)"
    
    def __str__(self):
        return f"{self.item.name} (x{self.item.catch_rate_modifier})"