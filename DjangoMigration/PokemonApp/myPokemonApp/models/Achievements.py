"""
Système de succès/achievements
"""

from django.db import models
from .Trainer import Trainer, TrainerInventory
from .Item import Item
from django.utils import timezone

class Achievement(models.Model):
    """
    Succès à débloquer
    """
    
    CATEGORIES = [
        ('combat', 'Combat'),
        ('capture', 'Capture'),
        ('collection', 'Collection'),
        ('exploration', 'Exploration'),
        ('progression', 'Progression'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    # Conditions
    required_value = models.IntegerField(default=1)
    
    # Récompense
    reward_item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    reward_money = models.IntegerField(default=0)
    
    # Visuel
    icon = models.CharField(max_length=100, blank=True)
    
    # Ordre
    is_hidden = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class TrainerAchievement(models.Model):
    """
    Succès débloqués par un joueur
    """
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    
    current_progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['trainer', 'achievement']
    
    def __str__(self):
        status = "✅" if self.is_completed else f"{self.current_progress}/{self.achievement.required_value}"
        return f"{self.trainer.username} - {self.achievement.name} [{status}]"
    
    def check_completion(self):
        """Vérifie si le succès est complété"""
        if self.current_progress >= self.achievement.required_value and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()
            
            # Donner récompense
            if self.achievement.reward_money > 0:
                self.trainer.money += self.achievement.reward_money
                self.trainer.save()
            
            if self.achievement.reward_item:
                inv, _ = TrainerInventory.objects.get_or_create(
                    trainer=self.trainer,
                    item=self.achievement.reward_item
                )
                inv.quantity += 1
                inv.save()
            
            return True
        return False