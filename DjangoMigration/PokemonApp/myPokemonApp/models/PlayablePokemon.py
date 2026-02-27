#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .Pokemon import Pokemon
from .Trainer import Trainer
from .Item import Item
from .PokemonMove import PokemonMove
import random


# Constante module-level
NATURE_MODIFIERS = {
    'Lonely':  ('attack',         'defense'),
    'Brave':   ('attack',         'speed'),
    'Adamant': ('attack',         'special_attack'),
    'Naughty': ('attack',         'special_defense'),
    'Bold':    ('defense',        'attack'),
    'Relaxed': ('defense',        'speed'),
    'Impish':  ('defense',        'special_attack'),
    'Lax':     ('defense',        'special_defense'),
    'Timid':   ('speed',          'attack'),
    'Hasty':   ('speed',          'defense'),
    'Jolly':   ('speed',          'special_attack'),
    'Naive':   ('speed',          'special_defense'),
    'Modest':  ('special_attack', 'attack'),
    'Mild':    ('special_attack', 'defense'),
    'Quiet':   ('special_attack', 'speed'),
    'Rash':    ('special_attack', 'special_defense'),
    'Calm':    ('special_defense', 'attack'),
    'Gentle':  ('special_defense', 'defense'),
    'Sassy':   ('special_defense', 'speed'),
    'Careful': ('special_defense', 'special_attack'),
}

class PlayablePokemon(models.Model):
    """Pokémon possédé par un dresseur"""
    
    # Référence au template
    species = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    
    # Propriétaire
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='pokemon_team'
    )
    
    # Surnom optionnel
    nickname = models.CharField(max_length=12, blank=True, null=True)
    
    # Niveau et expérience
    level = models.IntegerField(default=5)
    current_exp = models.IntegerField(default=0)
    
    # Stats actuelles (calculées à partir des stats de base)
    max_hp = models.IntegerField()
    current_hp = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    special_attack = models.IntegerField()
    special_defense = models.IntegerField()
    speed = models.IntegerField()
    
    # IVs (Individual Values) - 0 à 31
    iv_hp = models.IntegerField(default=0)
    iv_attack = models.IntegerField(default=0)
    iv_defense = models.IntegerField(default=0)
    iv_special_attack = models.IntegerField(default=0)
    iv_special_defense = models.IntegerField(default=0)
    iv_speed = models.IntegerField(default=0)
    
    # EVs (Effort Values) - max 252 par stat, 510 total
    ev_hp = models.IntegerField(default=0)
    ev_attack = models.IntegerField(default=0)
    ev_defense = models.IntegerField(default=0)
    ev_special_attack = models.IntegerField(default=0)
    ev_special_defense = models.IntegerField(default=0)
    ev_speed = models.IntegerField(default=0)
    
    # Nature (affecte les stats)
    nature = models.CharField(max_length=20, default='Hardy')
    
    # Statut
    status_condition = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('paralysis', 'Paralysie'),
            ('poison', 'Poison'),
            ('burn', 'Brûlure'),
            ('freeze', 'Gel'),
            ('sleep', 'Sommeil'),
        ]
    )
    sleep_turns = models.IntegerField(default=0)
    
    # Modificateurs temporaires de combat
    attack_stage = models.IntegerField(default=0)  # -6 à +6
    defense_stage = models.IntegerField(default=0)
    special_attack_stage = models.IntegerField(default=0)
    special_defense_stage = models.IntegerField(default=0)
    speed_stage = models.IntegerField(default=0)
    accuracy_stage = models.IntegerField(default=0)
    evasion_stage = models.IntegerField(default=0)
    
    # Capacités connues (max 4)
    moves = models.ManyToManyField(
        PokemonMove,
        through='PokemonMoveInstance',
        related_name='known_by'
    )
    
    # Objet tenu
    held_item = models.ForeignKey(
        Item,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='held_by'
    )
    
    # Bonheur
    friendship = models.IntegerField(default=70)
    
    # Informations de capture
    original_trainer = models.CharField(max_length=50)
    caught_location = models.CharField(max_length=100, blank=True, null=True)
    pokeball_used = models.CharField(max_length=20, default='pokeball')
    
    # Position dans l'équipe
    party_position = models.IntegerField(blank=True, null=True)
    is_in_party = models.BooleanField(default=True)

    is_shiny = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Pokémon (Jouable)"
        verbose_name_plural = "Pokémon (Jouables)"
        ordering = ['party_position']
    
    def __str__(self):
        name = self.nickname or self.species.name
        return f"{name} (Niv. {self.level})"
    
    def save(self, *args, **kwargs):
        """Recalcule les stats avant de sauvegarder"""
        is_new = not self.pk  # Détecter si c'est un nouveau Pokémon
        
        if is_new:  # Nouveau Pokémon
            self.calculate_stats()
            if not self.current_hp:
                self.current_hp = self.max_hp
        
        super().save(*args, **kwargs)
        
        # Auto-apprentissage des moves initiaux après sauvegarde
        if is_new:
            self.learn_initial_moves()
    
    def learn_initial_moves(self):
        """
        Apprend automatiquement les moves disponibles pour ce niveau
        """
        from .PokemonLearnableMove import PokemonLearnableMove
        
        # Récupérer toutes les capacités apprises jusqu'à ce niveau
        learnable_moves = PokemonLearnableMove.objects.filter(
            pokemon=self.species,
            level_learned__lte=self.level
        ).order_by('-level_learned')[:4]  # Les 4 plus récentes
        
        for learnable in learnable_moves:
            if self.moves.count() >= 4:
                break
            
            # Créer l'instance de move pour ce Pokémon
            PokemonMoveInstance.objects.get_or_create(
                pokemon=self,
                move=learnable.move,
                defaults={'current_pp': learnable.move.pp}
            )
    
    def calculate_stats(self):
        """
        Calcule les stats basées sur le niveau, IVs, EVs et nature.

        Formule Gen 3+ :
          HP    = floor( (2*base + IV + floor(EV/4)) * L / 100 ) + L + 10
          Autre = floor( floor( (2*base + IV + floor(EV/4)) * L / 100 ) + 5 ) × nature
        """
        L = self.level

        self.max_hp = int(
            ((2 * self.species.base_hp + self.iv_hp + self.ev_hp // 4) * L) // 100
            + L + 10
        )

        boosted_stat, reduced_stat = NATURE_MODIFIERS.get(self.nature, (None, None))

        stats = {
            'attack':          (self.species.base_attack,         self.iv_attack,         self.ev_attack),
            'defense':         (self.species.base_defense,        self.iv_defense,        self.ev_defense),
            'special_attack':  (self.species.base_special_attack, self.iv_special_attack, self.ev_special_attack),
            'special_defense': (self.species.base_special_defense,self.iv_special_defense,self.ev_special_defense),
            'speed':           (self.species.base_speed,          self.iv_speed,          self.ev_speed),
        }

        for stat_name, (base, iv, ev) in stats.items():
            value = int(((2 * base + iv + ev // 4) * L) // 100 + 5)

            # Application de la nature (±10 %)
            if stat_name == boosted_stat:
                value = int(value * 1.1)
            elif stat_name == reduced_stat:
                value = int(value * 0.9)

            # Plancher à 1
            setattr(self, stat_name, max(1, value))

    def exp_at_level(self, n):
        """
        Retourne l'XP totale cumulée requise pour ATTEINDRE le niveau n.
        Même formules que exp_for_next_level mais paramétrées sur n.
        """
        if n <= 1:
            return 0
        if n > 100:
            n = 100

        rate = getattr(self.species, 'growth_rate', 'medium_fast')

        if rate == 'fast':
            return int(4 * n ** 3 / 5)
        elif rate == 'medium_slow':
            val = int(6 * n ** 3 / 5) - 15 * n ** 2 + 100 * n - 140
            return max(0, val)
        elif rate == 'slow':
            return int(5 * n ** 3 / 4)
        elif rate == 'erratic':
            if n <= 50:
                return int(n ** 3 * (100 - n) / 50)
            elif n <= 68:
                return int(n ** 3 * (150 - n) / 100)
            elif n <= 98:
                return int(n ** 3 * ((1911 - 10 * n) // 3) / 500)
            else:
                return int(n ** 3 * (160 - n) / 100)
        elif rate == 'fluctuating':
            if n <= 15:
                return int(n ** 3 * ((n + 1) // 3 + 24) / 50)
            elif n <= 36:
                return int(n ** 3 * (n + 14) / 50)
            else:
                return int(n ** 3 * ((n // 2) + 32) / 50)
        else:  # medium_fast
            return n ** 3

    def exp_for_next_level(self):
        """
        Retourne l'XP totale cumulée nécessaire pour atteindre le niveau suivant.

        Système cumulatif (comme dans les jeux) : current_exp est l'XP
        totale depuis le niveau 1. On compare directement au seuil,
        sans soustraction.

        Groupes de croissance (XP requise au niveau 100) :
          - Erratic      : 600 000  (formule complexe, non-monotone)
          - Fast         : 800 000  (4n³/5)
          - Medium Fast  : 1 000 000 (n³)             ← défaut
          - Medium Slow  : 1 059 860 (6n³/5 − 15n² + 100n − 140)
          - Slow         : 1 250 000 (5n³/4)
          - Fluctuating  : 1 640 000 (formule complexe)
        """
        n = self.level + 1  # seuil pour atteindre le prochain niveau
        if n > 100:
            return 10_000_000  # niveau max déjà atteint

        rate = getattr(self.species, 'growth_rate', 'medium_fast')

        if rate == 'fast':
            return int(4 * n ** 3 / 5)

        elif rate == 'medium_slow':
            val = int(6 * n ** 3 / 5) - 15 * n ** 2 + 100 * n - 140
            return max(0, val)

        elif rate == 'slow':
            return int(5 * n ** 3 / 4)

        elif rate == 'erratic':
            if n <= 50:
                return int(n ** 3 * (100 - n) / 50)
            elif n <= 68:
                return int(n ** 3 * (150 - n) / 100)
            elif n <= 98:
                return int(n ** 3 * ((1911 - 10 * n) // 3) / 500)
            else:
                return int(n ** 3 * (160 - n) / 100)

        elif rate == 'fluctuating':
            if n <= 15:
                return int(n ** 3 * ((n + 1) // 3 + 24) / 50)
            elif n <= 36:
                return int(n ** 3 * (n + 14) / 50)
            else:
                return int(n ** 3 * ((n // 2) + 32) / 50)

        else:  # medium_fast (défaut)
            return n ** 3
    
    def level_up(self):
        """Monte d'un niveau"""
        old_level = self.level
        self.level += 1
        
        # Recalculer les stats
        old_max_hp = self.max_hp
        self.calculate_stats()
        hp_gain = self.max_hp - old_max_hp
        self.current_hp += hp_gain
        
        # Vérifier les nouvelles capacités
        new_moves = self.check_new_moves()
        
        # Auto-apprentissage des nouvelles capacités
        for move in new_moves:
            if self.moves.count() < 4:
                self.learn_move(move)
        
        # Vérifier l'évolution
        self.check_evolution()
        
        return f"{self} est monté niveau {self.level}!"
    
    def check_new_moves(self):
        """Vérifie si le Pokémon peut apprendre de nouvelles capacités"""
        learnable = self.species.learnable_moves.filter(
            level_learned=self.level
        )
        
        new_moves = []
        for learnable_move in learnable:
            if not self.moves.filter(id=learnable_move.move.id).exists():
                new_moves.append(learnable_move.move)
        
        return new_moves
    
    def learn_move(self, move, replace_move=None):
        """Apprend une nouvelle capacité"""
        if self.moves.count() < 4:
            PokemonMoveInstance.objects.create(
                pokemon=self,
                move=move,
                current_pp=move.pp
            )
            return True
        elif replace_move:
            PokemonMoveInstance.objects.filter(
                pokemon=self,
                move=replace_move
            ).delete()
            PokemonMoveInstance.objects.create(
                pokemon=self,
                move=move,
                current_pp=move.pp
            )
            return True
        return False
    
    def check_evolution(self):
        """Vérifie si le Pokémon peut évoluer"""
        from .PokemonEvolution import PokemonEvolution
        
        evolutions = PokemonEvolution.objects.filter(
            pokemon=self.species,
            method='level',
            level__lte=self.level
        )
        
        return evolutions.first() if evolutions.exists() else None
    
    def check_stone_evolution(self, stone_item):
        """Vérifie si le Pokémon peut évoluer avec une pierre"""
        from .PokemonEvolution import PokemonEvolution
        
        evolution = PokemonEvolution.objects.filter(
            pokemon=self.species,
            method='stone',
            required_item=stone_item
        ).first()
        
        if evolution:
            return self.evolve_to(evolution.evolves_to)
        
        return "Aucun effet."
    
    def evolve_to(self, new_species):
        """Fait évoluer le Pokémon"""
        old_name = self.species.name
        self.species = new_species
        
        # Recalculer les stats
        old_hp = self.current_hp
        hp_percentage = old_hp / self.max_hp if self.max_hp > 0 else 1
        
        self.calculate_stats()
        self.current_hp = int(self.max_hp * hp_percentage)
        
        self.save()
        
        return f"{old_name} évolue en {new_species.name}!"
    
    def is_fainted(self):
        """Vérifie si le Pokémon est KO"""
        return self.current_hp <= 0

    @property
    def needs_healing(self) -> bool:
        """True si le Pokémon n'est pas à pleine forme (HP ou statut)."""
        return self.current_hp < self.max_hp or bool(self.status_condition)

    @property
    def hp_percent(self) -> float:
        """Pourcentage de HP restants (0.0 – 100.0)."""
        if not self.max_hp:
            return 0.0
        return round(self.current_hp / self.max_hp * 100, 1)

    @property
    def display_name(self) -> str:
        """Nom affiché : surnom si présent, sinon nom de l'espèce."""
        return self.nickname or self.species.name
    
    def heal(self, hp_amount=None):
        """Soigne le Pokémon"""
        if hp_amount is None:
            # Soigne complètement
            self.current_hp = self.max_hp
        else:
            self.current_hp = min(self.max_hp, self.current_hp + hp_amount)
        
        self.save()
    
    def cure_status(self):
        """Guérit le statut"""
        self.status_condition = None
        self.sleep_turns = 0
        self.save()
    
    def restore_all_pp(self):
        """Restaure tous les PP des capacités"""
        for move_instance in self.pokemonmoveinstance_set.all():
            move_instance.restore_pp()
    
    def apply_status(self, status):
        """Applique un statut"""
        if not self.status_condition:
            self.status_condition = status
            
            if status == 'sleep':
                self.sleep_turns = random.randint(1, 3)
            
            self.save()
            return True
        return False
    
    def reset_combat_stats(self):
        """Réinitialise les modificateurs de combat"""
        self.attack_stage = 0
        self.defense_stage = 0
        self.special_attack_stage = 0
        self.special_defense_stage = 0
        self.speed_stage = 0
        self.accuracy_stage = 0
        self.evasion_stage = 0
        self.save()
    
    def get_stat_multiplier(self, stage):
        """Retourne le multiplicateur de stat basé sur le stage"""
        multipliers = {
            -6: 2/8, -5: 2/7, -4: 2/6, -3: 2/5, -2: 2/4, -1: 2/3,
            0: 1,
            1: 3/2, 2: 4/2, 3: 5/2, 4: 6/2, 5: 7/2, 6: 8/2
        }
        return multipliers.get(stage, 1)
    
    def get_effective_attack(self):
        """Retourne l'attaque avec le multiplicateur de stage"""
        return int(self.attack * self.get_stat_multiplier(self.attack_stage))
    
    def get_effective_defense(self):
        """Retourne la défense avec le multiplicateur de stage"""
        return int(self.defense * self.get_stat_multiplier(self.defense_stage))
    
    def get_effective_special_attack(self):
        """Retourne l'attaque spéciale avec le multiplicateur de stage"""
        return int(self.special_attack * self.get_stat_multiplier(self.special_attack_stage))
    
    def get_effective_special_defense(self):
        """Retourne la défense spéciale avec le multiplicateur de stage"""
        return int(self.special_defense * self.get_stat_multiplier(self.special_defense_stage))
    
    def get_effective_speed(self):
        """Retourne la vitesse avec le multiplicateur de stage et de statut"""
        speed = int(self.speed * self.get_stat_multiplier(self.speed_stage))
        
        # Paralysie divise la vitesse par 4
        if self.status_condition == 'paralysis':
            speed = speed // 4
        
        return speed


class PokemonMoveInstance(models.Model):
    """Instance d'une capacité pour un Pokémon spécifique (avec PP)"""
    
    pokemon = models.ForeignKey(PlayablePokemon, on_delete=models.CASCADE)
    move = models.ForeignKey(PokemonMove, on_delete=models.CASCADE)
    current_pp = models.IntegerField()
    
    class Meta:
        unique_together = ['pokemon', 'move']
    
    def __str__(self):
        return f"{self.move.name} ({self.current_pp}/{self.move.pp} PP)"
    
    def can_use(self):
        """Vérifie si la capacité peut être utilisée"""
        return self.current_pp > 0
    
    def use(self):
        """Utilise la capacité (réduit les PP)"""
        if self.can_use():
            self.current_pp -= 1
            self.save()
            return True
        return False
    
    def restore_pp(self, amount=None):
        """Restaure les PP"""
        if amount is None:
            self.current_pp = self.move.pp
        else:
            self.current_pp = min(self.move.pp, self.current_pp + amount)
        self.save()