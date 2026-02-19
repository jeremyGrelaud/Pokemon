#!/usr/bin/python3
"""
Système de Boutique PokéMart
Nouveau modèle pour gérer les magasins et achats
"""

from django.db import models
from .Item import Item
from .Trainer import Trainer


class Shop(models.Model):
    """Boutique Pokémon (PokéMart)"""
    
    SHOP_TYPES = [
        ('pokemart', 'PokéMart'),
        ('department', 'Grand Magasin'),
        ('special', 'Boutique Spéciale'),
    ]
    
    name = models.CharField(max_length=100)
    shop_type = models.CharField(max_length=20, choices=SHOP_TYPES, default='pokemart')
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Sprite du vendeur
    shopkeeper_sprite = models.CharField(max_length=100, blank=True, null=True)
    shopkeeper_greeting = models.TextField(default="Bienvenue au PokéMart!")
    
    class Meta:
        verbose_name = "Boutique"
        verbose_name_plural = "Boutiques"
    
    def __str__(self):
        return f"{self.name} ({self.location})"


class ShopInventory(models.Model):
    """Inventaire d'une boutique - quels items sont vendus où"""
    
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    
    # Stock (-1 = illimité)
    stock = models.IntegerField(default=-1)
    
    # Conditions de déverrouillage
    unlock_badge_required = models.IntegerField(default=0)
    
    # Prix (si différent du prix de base)
    custom_price = models.IntegerField(null=True, blank=True)
    discount_percentage = models.IntegerField(default=0)  # 0-100
    
    # Mise en avant
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['shop', 'item']
        verbose_name = "Inventaire Boutique"
        ordering = ['-is_featured', '-is_new', 'item__item_type', 'item__name']
    
    def __str__(self):
        return f"{self.shop.name} - {self.item.name}"
    
    def get_final_price(self):
        """Retourne le prix final après réduction"""
        base_price = self.custom_price if self.custom_price else self.item.price
        
        if self.discount_percentage > 0:
            return int(base_price * (1 - self.discount_percentage / 100))
        
        return base_price
    
    def get_sell_price(self):
        """Prix de revente (50% du prix d'achat)"""
        return self.get_final_price() // 2
    
    def is_available_for_trainer(self, trainer):
        """Vérifie si l'item est disponible pour ce dresseur"""
        return trainer.badges >= self.unlock_badge_required
    
    def can_afford(self, trainer, quantity=1):
        """Vérifie si le dresseur peut acheter"""
        total_cost = self.get_final_price() * quantity
        return trainer.money >= total_cost
    
    def has_stock(self, quantity=1):
        """Vérifie le stock"""
        if self.stock == -1:  # Stock illimité
            return True
        return self.stock >= quantity


class Transaction(models.Model):
    """Historique des transactions"""
    
    TRANSACTION_TYPES = [
        ('buy', 'Achat'),
        ('sell', 'Vente'),
    ]
    
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='transactions')
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    unit_price = models.IntegerField()
    total_price = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Transaction"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.trainer.username} - {self.get_transaction_type_display()} {self.item.name} x{self.quantity}"