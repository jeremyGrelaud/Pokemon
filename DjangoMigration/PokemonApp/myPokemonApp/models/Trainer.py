#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .Item import Item
from .PokemonMove import PokemonMove
from .PokemonType import PokemonType
class Trainer(models.Model):
    """Dresseur de base"""
    
    TRAINER_TYPES = [
        ('player', 'Joueur'),
        ('rival', 'Rival'),
        ('gym_leader', 'Champion d\'Arène'),
        ('elite_four', 'Conseil des 4'),
        ('champion', 'Maître'),
        ('trainer', 'Dresseur'),
        ('wild', 'Sauvage'),
    ]
    
    username = models.CharField(max_length=50)
    trainer_type = models.CharField(max_length=20, choices=TRAINER_TYPES)
    
    # Inventaire
    money = models.IntegerField(default=3000)
    
    # Badges
    badges = models.IntegerField(default=0)
    
    # Position dans le jeu (pour les NPCs)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    # Pour les NPCs
    is_defeated = models.BooleanField(default=False)
    can_rebattle = models.BooleanField(default=False)
    
    # Dialogue
    intro_text = models.TextField(blank=True, null=True)
    defeat_text = models.TextField(blank=True, null=True)
    victory_text = models.TextField(blank=True, null=True)

    is_npc = models.BooleanField(default=False)
    is_battle_required = models.BooleanField(
        default=False,
        help_text="Ce dresseur bloque le passage et doit être battu avant de quitter la zone."
    )
    npc_class = models.CharField(max_length=50, blank=True)  # "Gamin", "Scout", etc.
    sprite_name = models.CharField(max_length=100, blank=True)

    
    class Meta:
        verbose_name = "Dresseur"
        verbose_name_plural = "Dresseurs"
    
    def __str__(self):
        return f"{self.username} ({self.get_trainer_type_display()})"
    
    def has_available_pokemon(self):
        """Vérifie si le dresseur a des Pokémon non KO"""
        return self.pokemon_team.filter(current_hp__gt=0).exists()
    
    def get_reward(self):
        """Calcule la récompense à donner en cas de défaite"""
        if self.trainer_type == 'gym_leader':
            return 1000 + (self.badges * 500)
        elif self.trainer_type == 'elite_four':
            return 5000
        elif self.trainer_type == 'champion':
            return 10000
        else:
            highest_level = self.pokemon_team.aggregate(
                models.Max('level')
            )['level__max'] or 1
            return highest_level * 100

    def get_full_title(self):
        if self.npc_class:
            return f"{self.npc_class} {self.username}"
        return self.username

    # ------------------------------------------------------------------
    # Statut de defaite per-joueur
    # ------------------------------------------------------------------

    def is_defeated_by_player(self, player_trainer) -> bool:
        """
        Retourne True si CE joueur a deja vaincu ce Trainer NPC.

        La source de verite est GameSave.defeated_trainers (liste d IDs JSON),
        qui est strictement per-joueur. On ne se base PAS sur Trainer.is_defeated
        qui est un booleen global inutilisable en contexte multi-joueur.

        Performance : dans les vues qui iterent sur N trainers, preferer
        get_defeated_trainer_ids(player_trainer) pour recuperer le set
        d IDs en une seule requete, puis tester npc.id in defeated_ids.
        """
        from .GameSave import GameSave
        save = GameSave.objects.filter(trainer=player_trainer, is_active=True).first()
        if save is None:
            return False
        return self.id in save.defeated_trainers

    # ------------------------------------------------------------------
    # Helpers badges
    # ------------------------------------------------------------------

    def has_badge(self, badge_order: int) -> bool:
        """Retourne True si le trainer a obtenu le badge d'ordre badge_order."""
        return self.badges >= badge_order

    # ------------------------------------------------------------------
    # Helpers équipe / PC — évitent de réécrire le filtre partout
    # ------------------------------------------------------------------

    @property
    def party(self):
        """QuerySet des Pokémon actifs, triés par position."""
        return self.pokemon_team.filter(is_in_party=True).order_by('party_position')

    @property
    def pc(self):
        """QuerySet des Pokémon en réserve (PC)."""
        return self.pokemon_team.filter(is_in_party=False)

    @property
    def party_count(self) -> int:
        """Nombre de Pokémon dans l'équipe active."""
        return self.pokemon_team.filter(is_in_party=True).count()

    @property
    def pc_count(self) -> int:
        """Nombre de Pokémon dans le PC."""
        return self.pokemon_team.filter(is_in_party=False).count()

    # ------------------------------------------------------------------
    # Helpers argent — garantissent un .save() systématique
    # ------------------------------------------------------------------

    def spend_money(self, amount: int) -> bool:
        """Dépense amount₽. Retourne False si fonds insuffisants."""
        if self.money < amount:
            return False
        self.money -= amount
        self.save(update_fields=['money'])
        return True

    def earn_money(self, amount: int) -> None:
        """Crédite amount₽ sur le solde du trainer."""
        self.money += amount
        self.save(update_fields=['money'])

class GymLeader(models.Model):
    """Champion d'Arène avec informations spécifiques"""
    
    trainer = models.OneToOneField(
        Trainer,
        on_delete=models.CASCADE,
        related_name='gym_info'
    )
    
    gym_name = models.CharField(max_length=50)
    gym_city = models.CharField(max_length=50)
    badge_name = models.CharField(max_length=50)
    specialty_type = models.ForeignKey(
        PokemonType,
        on_delete=models.CASCADE,
        related_name='gym_leaders'
    )
    
    badge_order = models.IntegerField(unique=True)  # 1-8
    
    # TM donné en récompense
    tm_reward = models.ForeignKey(
        PokemonMove,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Champion d'Arène"
        verbose_name_plural = "Champions d'Arène"
        ordering = ['badge_order']
    
    def __str__(self):
        return f"{self.trainer.username} - {self.gym_name} ({self.gym_city})"
    
    def isChallengableByPlayer(self, player_trainer) -> bool:
        """
        Retourne True si le joueur peut defier cet Arena Leader.
        - Utilise is_defeated_by_player() (per-joueur) au lieu de trainer.is_defeated (global).
        - Verifie que le joueur possede les badges requis (badge_order - 1).
        """
        if self.trainer.is_defeated_by_player(player_trainer):
            return False
        required_badges = self.badge_order - 1
        return player_trainer.badges >= required_badges



class TrainerInventory(models.Model):
    """Inventaire d'un dresseur"""
    
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ['trainer', 'item']
        verbose_name = "Inventaire"
    
    def __str__(self):
        return f"{self.trainer.username} - {self.item.name} x{self.quantity}"