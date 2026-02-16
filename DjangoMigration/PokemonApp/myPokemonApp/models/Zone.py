"""
Zones de la carte Kanto
"""

from django.db import models
from .Trainer import GymLeader
from .Item import Item
from .Pokemon import Pokemon

class Zone(models.Model):
    """
    Zone géographique (Route, Ville, Grotte, etc.)
    """
    
    ZONE_TYPES = [
        ('route', 'Route'),
        ('city', 'Ville'),
        ('cave', 'Grotte'),
        ('forest', 'Forêt'),
        ('water', 'Mer'),
        ('building', 'Bâtiment'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPES)
    description = models.TextField(blank=True)
    
    # Progression
    recommended_level_min = models.IntegerField(default=1)
    recommended_level_max = models.IntegerField(default=10)
    order = models.IntegerField(default=0, help_text="Ordre dans la progression")
    
    # Accès
    required_badge = models.ForeignKey(
        GymLeader,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Badge requis pour accéder"
    )
    required_item = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Item requis (ex: Bicyclette)"
    )
    
    # Visuel
    image = models.CharField(max_length=200, blank=True)
    music = models.CharField(max_length=200, blank=True)
    
    # Flags
    is_safe_zone = models.BooleanField(default=False, help_text="Pas de wild battles")
    has_pokemon_center = models.BooleanField(default=False)
    has_shop = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Zone"
    
    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"
    
    def is_accessible_by(self, trainer):
        """Vérifie si le trainer peut accéder à cette zone"""
        
        # Badge requis
        if self.required_badge:
            if not trainer.badges >= self.required_badge.badge_order:
                return False, f"Badge {self.required_badge.badge_name} requis"
        
        # Item requis
        if self.required_item:
            has_item = trainer.inventory.filter(item=self.required_item).exists()
            if not has_item:
                return False, f"{self.required_item.name} requis"
        
        return True, "OK"


class ZoneConnection(models.Model):
    """
    Connexions entre zones (pour la navigation)
    """
    
    from_zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='connections_from'
    )
    to_zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name='connections_to'
    )
    
    is_bidirectional = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['from_zone', 'to_zone']
    
    def __str__(self):
        arrow = "↔" if self.is_bidirectional else "→"
        return f"{self.from_zone.name} {arrow} {self.to_zone.name}"


class WildPokemonSpawn(models.Model):
    """
    Spawn de Pokémon sauvages dans une zone
    """
    
    ENCOUNTER_TYPES = [
        ('grass', 'Hautes herbes'),
        ('water', 'Surf'),
        ('fishing', 'Pêche'),
        ('cave', 'Grotte'),
    ]
    
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='wild_spawns')
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    
    # Taux de spawn (0-100%)
    spawn_rate = models.FloatField(
        default=10.0,
        help_text="% de chance d'apparition (total zone = 100%)"
    )
    
    # Niveaux
    level_min = models.IntegerField(default=2)
    level_max = models.IntegerField(default=5)
    
    # Type de rencontre
    encounter_type = models.CharField(
        max_length=20,
        choices=ENCOUNTER_TYPES,
        default='grass'
    )
    
    # Conditions
    time_of_day = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('', 'Toujours'),
            ('morning', 'Matin'),
            ('day', 'Jour'),
            ('night', 'Nuit')
        ],
        default=''
    )
    
    class Meta:
        ordering = ['-spawn_rate']
        verbose_name = "Spawn Pokémon"
    
    def __str__(self):
        return f"{self.pokemon.name} dans {self.zone.name} ({self.spawn_rate}%)"


class PlayerLocation(models.Model):
    """
    Position actuelle du joueur
    """
    
    trainer = models.OneToOneField('Trainer', on_delete=models.CASCADE, related_name='player_location')
    current_zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    
    # Historique
    visited_zones = models.ManyToManyField(Zone, related_name='visitors', blank=True)
    
    last_pokemon_center = models.ForeignKey(
        Zone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.trainer.username} @ {self.current_zone.name}"
    
    def can_travel_to(self, zone):
        """Vérifie si le joueur peut voyager vers une zone"""
        
        # Vérifier connexion
        is_connected = ZoneConnection.objects.filter(
            from_zone=self.current_zone,
            to_zone=zone
        ).exists()
        
        if not is_connected:
            # Vérifier bidirectional
            reverse = ZoneConnection.objects.filter(
                from_zone=zone,
                to_zone=self.current_zone,
                is_bidirectional=True
            ).exists()
            
            if not reverse:
                return False, "Zone non connectée"
        
        # Vérifier accès
        return zone.is_accessible_by(self.trainer)
    
    def travel_to(self, zone):
        """Déplace le joueur vers une zone"""
        can_travel, reason = self.can_travel_to(zone)
        
        if not can_travel:
            return False, reason
        
        self.current_zone = zone
        self.visited_zones.add(zone)
        self.save()
        
        return True, f"Arrivé à {zone.name}"