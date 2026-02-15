#!/usr/bin/python3
"""
Modèle Centre Pokémon
Gère les centres de soin et l'historique des visites
"""

from django.db import models
from .Trainer import Trainer


class PokemonCenter(models.Model):
    """Centre Pokémon - Lieu de soin"""
    
    name = models.CharField(max_length=100, default="Centre Pokémon")
    location = models.CharField(max_length=100)
    
    # Infirmière Joy
    nurse_name = models.CharField(max_length=50, default="Infirmière Joy")
    nurse_greeting = models.TextField(
        default="Bienvenue au Centre Pokémon ! Puis-je soigner vos Pokémon ?"
    )
    nurse_healing_message = models.TextField(
        default="Vos Pokémon ont été complètement soignés ! Revenez quand vous voulez !"
    )
    nurse_farewell = models.TextField(
        default="Nous espérons vous revoir bientôt !"
    )
    
    # Sprite de l'infirmière (optionnel)
    nurse_sprite = models.CharField(max_length=100, blank=True, null=True)
    
    # Paramètres
    is_available = models.BooleanField(default=True)
    healing_cost = models.IntegerField(default=0)  # 0 = gratuit
    
    # Statistiques
    total_healings = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Centre Pokémon"
        verbose_name_plural = "Centres Pokémon"
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    def heal_trainer_team(self, trainer):
        """
        Soigne toute l'équipe d'un dresseur
        Retourne un dictionnaire avec les résultats
        """
        if not self.is_available:
            return {
                'success': False,
                'message': 'Ce Centre Pokémon est actuellement fermé.'
            }
        
        # Vérifier le coût
        if self.healing_cost > 0:
            if trainer.money < self.healing_cost:
                return {
                    'success': False,
                    'message': f'Soin coûte {self.healing_cost}₽. Vous n\'avez pas assez d\'argent.'
                }
            
            trainer.money -= self.healing_cost
            trainer.save()
        
        # Soigner tous les Pokémon de l'équipe
        team_pokemon = trainer.pokemon_team.filter(is_in_party=True)
        healed_count = 0
        
        for pokemon in team_pokemon:
            pokemon.heal()  # Restaure HP
            pokemon.cure_status()  # Retire statuts
            pokemon.restore_all_pp()  # Restaure PP
            pokemon.reset_combat_stats()  # Reset modificateurs
            healed_count += 1
        
        # Incrémenter les stats du centre
        self.total_healings += 1
        self.save()
        
        # Enregistrer la visite
        CenterVisit.objects.create(
            trainer=trainer,
            center=self,
            pokemon_healed=healed_count,
            cost=self.healing_cost
        )
        
        return {
            'success': True,
            'healed_count': healed_count,
            'cost': self.healing_cost,
            'message': self.nurse_healing_message
        }


class CenterVisit(models.Model):
    """Historique des visites au Centre Pokémon"""
    
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='center_visits'
    )
    center = models.ForeignKey(
        PokemonCenter,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    
    visited_at = models.DateTimeField(auto_now_add=True)
    pokemon_healed = models.IntegerField()
    cost = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Visite Centre"
        verbose_name_plural = "Visites Centres"
        ordering = ['-visited_at']
    
    def __str__(self):
        return f"{self.trainer.username} - {self.center.name} ({self.visited_at.strftime('%d/%m/%Y %H:%M')})"


class NurseDialogue(models.Model):
    """Dialogues variés pour Infirmière Joy"""
    
    DIALOGUE_TYPES = [
        ('greeting', 'Salutation'),
        ('healing', 'Pendant le soin'),
        ('complete', 'Soin terminé'),
        ('farewell', 'Au revoir'),
        ('special', 'Spécial'),
    ]
    
    center = models.ForeignKey(
        PokemonCenter,
        on_delete=models.CASCADE,
        related_name='dialogues',
        null=True,
        blank=True  # null = dialogue universel
    )
    
    dialogue_type = models.CharField(max_length=20, choices=DIALOGUE_TYPES)
    text = models.TextField()
    
    # Conditions d'affichage (optionnel)
    min_badges = models.IntegerField(default=0)
    max_badges = models.IntegerField(default=8)
    
    # Fréquence d'apparition (1-10, 10 = très rare)
    rarity = models.IntegerField(default=5)
    
    class Meta:
        verbose_name = "Dialogue Infirmière"
        verbose_name_plural = "Dialogues Infirmière"
    
    def __str__(self):
        return f"{self.get_dialogue_type_display()} - {self.text[:50]}"
    
    @classmethod
    def get_random_dialogue(cls, dialogue_type, trainer_badges=0, center=None):
        """Récupère un dialogue aléatoire selon le type et les conditions"""
        import random
        
        dialogues = cls.objects.filter(
            dialogue_type=dialogue_type,
            min_badges__lte=trainer_badges,
            max_badges__gte=trainer_badges
        )
        
        if center:
            # Prioriser les dialogues spécifiques au centre
            center_dialogues = dialogues.filter(center=center)
            if center_dialogues.exists():
                dialogues = center_dialogues
        
        if not dialogues.exists():
            return None
        
        # Sélection pondérée par rareté (inverse)
        weights = [11 - d.rarity for d in dialogues]
        return random.choices(list(dialogues), weights=weights)[0]