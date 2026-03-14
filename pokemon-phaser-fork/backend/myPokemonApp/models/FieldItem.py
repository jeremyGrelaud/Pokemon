"""
models/FieldItem.py
===================
Objets ramassables sur la carte (Pokéballs au sol).

FieldItem   : définition statique — un objet dans une zone à une position Tiled précise.
PickedUpItem: par joueur — enregistre qu'un FieldItem a déjà été ramassé.
"""

from django.db import models


class FieldItem(models.Model):
    """
    Objet au sol sur la carte.
    Peuplé via le script d'init ou l'admin Django.

    tiled_obj_id : ID de l'objet dans le JSON Tiled (obj.id) — stable tant que
                   la map n'est pas recrée depuis zéro.
    zone         : zone Django correspondante.
    item         : objet Django à donner au joueur.
    quantity     : quantité donnée (défaut 1).
    """
    zone         = models.ForeignKey(
        'myPokemonApp.Zone',
        on_delete=models.CASCADE,
        related_name='field_items',
    )
    item         = models.ForeignKey(
        'myPokemonApp.Item',
        on_delete=models.CASCADE,
    )
    quantity     = models.IntegerField(default=1)
    tiled_obj_id = models.IntegerField(
        help_text="ID de l'objet dans le JSON Tiled (obj.id)"
    )

    class Meta:
        unique_together = ['zone', 'tiled_obj_id']
        verbose_name        = "Objet de terrain"
        verbose_name_plural = "Objets de terrain"
        indexes = [
            models.Index(fields=['zone', 'tiled_obj_id'], name='idx_fielditem_zone_tiled'),
        ]

    def __str__(self):
        return f"{self.item.name} ×{self.quantity} — {self.zone.name} (tiled#{self.tiled_obj_id})"


class PickedUpItem(models.Model):
    """
    Enregistre qu'un joueur a déjà ramassé un FieldItem.
    Garantit l'idempotence : on ne peut pas ramasser deux fois le même objet.
    """
    trainer    = models.ForeignKey(
        'myPokemonApp.Trainer',
        on_delete=models.CASCADE,
        related_name='picked_up_items',
    )
    field_item = models.ForeignKey(
        FieldItem,
        on_delete=models.CASCADE,
        related_name='picked_up_by',
    )
    picked_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['trainer', 'field_item']
        verbose_name        = "Objet ramassé"
        verbose_name_plural = "Objets ramassés"
        indexes = [
            models.Index(fields=['trainer', 'field_item'], name='idx_pickedup_trainer_item'),
        ]

    def __str__(self):
        return f"{self.trainer.username} → {self.field_item}"