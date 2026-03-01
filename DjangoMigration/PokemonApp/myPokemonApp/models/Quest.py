"""
Système de quêtes et étages pour Pokemon Kanto.

Modèles :
  - Quest            : définition d'une quête (trigger, récompenses, prérequis)
  - QuestProgress    : progression par joueur
  - ZoneFloor        : étage d'un bâtiment multi-niveaux
  - ZoneFloorSpawn   : spawns propres à un étage
  - RivalEncounter   : point de rencontre obligatoire avec le rival
"""

from django.db import models
from django.utils import timezone


# ─────────────────────────────────────────────────────────────────────────────
# QUEST
# ─────────────────────────────────────────────────────────────────────────────

class Quest(models.Model):
    """Définition d'une quête."""

    QUEST_TYPES = [
        ('main',  'Quête principale'),
        ('side',  'Quête secondaire'),
        ('rival', 'Rencontre Rival'),
        ('hm',    'Obtention CS'),
    ]

    TRIGGER_TYPES = [
        ('visit_zone',       'Visiter une zone'),
        ('defeat_trainer',   'Battre un dresseur'),
        ('defeat_gym',       'Battre un Champion d\'Arène'),
        ('have_item',        'Posséder un objet'),
        ('give_item',        'Remettre un objet à quelqu\'un'),
        ('collect_badge',    'Obtenir un badge'),
        ('story_flag',       'Flag scénaristique'),
        ('auto',             'Automatique'),
    ]

    # Identifiant stable utilisé dans le code
    quest_id    = models.CharField(max_length=60, unique=True)
    title       = models.CharField(max_length=100)
    description = models.TextField()
    quest_type  = models.CharField(max_length=10, choices=QUEST_TYPES, default='main')

    # Ordre narratif (affiché, utilisé pour tri)
    order = models.IntegerField(default=0)

    # Prérequis : quêtes à avoir complétées avant
    prerequisite_quests = models.ManyToManyField(
        'self', symmetrical=False, blank=True,
        related_name='unlocks_quests'
    )

    # Déclencheur
    trigger_type    = models.CharField(max_length=20, choices=TRIGGER_TYPES, default='auto')
    trigger_zone    = models.ForeignKey(
        'Zone', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='quest_triggers'
    )
    trigger_trainer = models.ForeignKey(
        'Trainer', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='quest_triggers'
    )
    trigger_item    = models.ForeignKey(
        'Item', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='quest_triggers'
    )
    # Pour trigger_type='story_flag' : flag dans GameSave.story_flags
    trigger_flag    = models.CharField(max_length=60, blank=True)

    # Récompenses
    reward_item    = models.ForeignKey(
        'Item', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='quest_rewards'
    )
    reward_money   = models.IntegerField(default=0)
    # Flag posé dans GameSave.story_flags quand la quête est complétée
    reward_flag    = models.CharField(max_length=60, blank=True)

    # Objectif lisible (affiché dans le journal)
    objective_text = models.CharField(max_length=200, blank=True)

    # Icône FontAwesome (ex: "fa-scroll")
    icon = models.CharField(max_length=50, default='fa-scroll')

    class Meta:
        ordering = ['order']
        verbose_name = 'Quête'
        verbose_name_plural = 'Quêtes'

    def __str__(self):
        return f"[{self.quest_id}] {self.title}"


# ─────────────────────────────────────────────────────────────────────────────
# QUEST PROGRESS
# ─────────────────────────────────────────────────────────────────────────────

class QuestProgress(models.Model):
    """Progression d'un joueur sur une quête donnée."""

    STATES = [
        ('locked',     'Verrouillée'),
        ('available',  'Disponible'),
        ('active',     'En cours'),
        ('completed',  'Terminée'),
    ]

    trainer      = models.ForeignKey(
        'Trainer', on_delete=models.CASCADE, related_name='quest_progress'
    )
    quest        = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='progress')
    state        = models.CharField(max_length=12, choices=STATES, default='locked')

    started_at   = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Données flexibles (ex: {"items_delivered": 1})
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['trainer', 'quest']
        ordering = ['quest__order']
        verbose_name = 'Progression de quête'

    def __str__(self):
        return f"{self.trainer.username} — {self.quest.title} [{self.state}]"

    def start(self):
        if self.state == 'available':
            self.state = 'active'
            self.started_at = timezone.now()
            self.save(update_fields=['state', 'started_at'])

    def complete(self):
        if self.state in ('available', 'active'):
            self.state = 'completed'
            self.completed_at = timezone.now()
            self.save(update_fields=['state', 'completed_at'])
            return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
# ZONE FLOOR  (multi-étages)
# ─────────────────────────────────────────────────────────────────────────────

class ZoneFloor(models.Model):
    """
    Étage d'un bâtiment multi-niveaux (Tour Pokémon, Sylphe SARL…).
    Les dresseurs NPC ont leur champ Trainer.location formaté :
        "<nom de zone>-<floor_number>"   ex: "Tour Pokemon-3"
    Les WildPokemonSpawn peuvent pointer sur cette zone + floor via le champ
    encounter_floor (ajouté ci-dessous).
    """

    zone         = models.ForeignKey(
        'Zone', on_delete=models.CASCADE, related_name='floors'
    )
    # Entier : -1 = SS, 0 = RDC, 1 = 1F, 2 = 2F …
    floor_number = models.IntegerField()
    floor_name   = models.CharField(max_length=20)   # "1F", "B1F", "Sommet"…
    description  = models.TextField(blank=True)

    # Drapeau scénaristique requis pour accéder à cet étage
    # Ex: "has_silph_scope" pour le 7F de la Tour Pokémon
    required_flag = models.CharField(max_length=60, blank=True)
    required_flag_label = models.CharField(
        max_length=100, blank=True,
        help_text="Message affiché si le flag est absent"
    )

    is_safe      = models.BooleanField(default=False)

    # Ordre d'affichage (du bas vers le haut)
    order        = models.IntegerField(default=0)

    class Meta:
        unique_together = ['zone', 'floor_number']
        ordering = ['zone', 'floor_number']
        verbose_name = 'Étage'
        verbose_name_plural = 'Étages'

    def __str__(self):
        return f"{self.zone.name} — {self.floor_name}"

    def is_accessible_by(self, trainer):
        """Retourne (bool, raison)."""
        if not self.required_flag:
            return True, 'OK'
        from .GameSave import GameSave
        save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
        if save and save.story_flags.get(self.required_flag):
            return True, 'OK'
        label = self.required_flag_label or f"Accès bloqué (flag: {self.required_flag})"
        return False, label


# ─────────────────────────────────────────────────────────────────────────────
# RIVAL ENCOUNTER
# ─────────────────────────────────────────────────────────────────────────────

class RivalEncounter(models.Model):
    """
    Point de rencontre obligatoire avec le rival.
    Lié à une quête : le combat est requis pour progresser.
    """

    quest        = models.OneToOneField(
        Quest, on_delete=models.CASCADE, related_name='rival_encounter'
    )
    rival        = models.ForeignKey(
        'Trainer', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='rival_encounters',
        help_text="NULL avec la nouvelle archi RivalTemplate/PlayerRival — résolu per-player."
    )
    zone         = models.ForeignKey(
        'Zone', on_delete=models.SET_NULL, null=True, related_name='rival_encounters'
    )
    floor        = models.ForeignKey(
        ZoneFloor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='rival_encounters'
    )

    # Dialogue avant le combat
    pre_battle_text  = models.TextField(blank=True)
    # Dialogue après victoire
    post_battle_text = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Rencontre Rival'
        verbose_name_plural = 'Rencontres Rival'

    def __str__(self):
        return f"Rival @ {self.zone} ({self.quest.quest_id})"