"""
HeldItemViews.py
================
Vues API pour les Objets Tenus (Held Items).

Endpoints :
  POST  /api/pokemon/equip-held-item/
  GET   /api/pokemon/held-items/
"""

from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
import json

from myPokemonApp.gameUtils import get_or_create_player_trainer
from ..models import PlayablePokemon, Item
from ..models.Trainer import TrainerInventory


# ─────────────────────────────────────────────────────────────────────────────
# Sérialisation d'un item (pour les réponses JSON)
# ─────────────────────────────────────────────────────────────────────────────

def _serialize_held_item(item: Item) -> dict:
    return {
        "id":            item.id,
        "name":          item.name,
        "description":   item.description,
        "held_effect":   item.held_effect or "",
        "is_consumable": item.is_consumable,
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/pokemon/equip-held-item/
# ─────────────────────────────────────────────────────────────────────────────

class EquipHeldItemView(LoginRequiredMixin, View):
    """
    Équipe ou déséquipe un objet tenu sur un PlayablePokemon du joueur.

    Body JSON :
      { "pokemon_id": <int>, "item_id": <int|null> }

    - item_id fourni  → équipe cet objet (doit être de type 'held' et dans l'inventaire)
    - item_id null/absent → déséquipe sans remplacer

    Règles :
      1. L'objet actuellement tenu (s'il existe) est rendu à l'inventaire avant
         d'équiper le nouveau.
      2. Si item_id est fourni, l'item est retiré de l'inventaire (qty -= 1,
         supprimé si qty == 0).
    """

    def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({"error": "JSON invalide."}, status=400)

        pokemon_id = body.get("pokemon_id")
        item_id    = body.get("item_id")   # None = simple déséquipement

        if not pokemon_id:
            return JsonResponse({"error": "pokemon_id requis."}, status=400)

        trainer = get_or_create_player_trainer(request.user)
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id, trainer=trainer)

        # ── 1. Restituer l'item déjà tenu ────────────────────────────────────
        if pokemon.held_item_id:
            inv, _ = TrainerInventory.objects.get_or_create(
                trainer=trainer,
                item=pokemon.held_item,
                defaults={"quantity": 0},
            )
            inv.quantity += 1
            inv.save()
            pokemon.held_item = None

        # ── 2. Équiper le nouvel item ────────────────────────────────────────
        new_held_data = None

        if item_id:
            new_item = get_object_or_404(Item, pk=item_id, item_type="held")

            try:
                inv = TrainerInventory.objects.get(trainer=trainer, item=new_item)
            except TrainerInventory.DoesNotExist:
                return JsonResponse(
                    {"error": f"Vous ne possédez pas {new_item.name}."},
                    status=403,
                )

            if inv.quantity <= 0:
                return JsonResponse(
                    {"error": f"Vous n'avez plus de {new_item.name} en stock."},
                    status=403,
                )

            inv.quantity -= 1
            if inv.quantity == 0:
                inv.delete()
            else:
                inv.save()

            pokemon.held_item = new_item
            new_held_data = _serialize_held_item(new_item)
            message = f"{pokemon.display_name} tient maintenant {new_item.name} !"
        else:
            message = f"{pokemon.display_name} ne tient plus aucun objet."

        pokemon.save(update_fields=["held_item"])

        return JsonResponse({
            "success":   True,
            "message":   message,
            "held_item": new_held_data,  # null si déséquipement
        })


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/pokemon/held-items/?pokemon_id=<int>
# ─────────────────────────────────────────────────────────────────────────────

class PokemonHeldItemsView(LoginRequiredMixin, View):
    """
    Retourne :
      - current_held  : objet tenu actuellement par le Pokémon (ou null)
      - available     : held items présents dans l'inventaire du dresseur
    """

    def get(self, request):
        pokemon_id = request.GET.get("pokemon_id")
        if not pokemon_id:
            return JsonResponse({"error": "pokemon_id requis."}, status=400)

        trainer = get_or_create_player_trainer(request.user)
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id, trainer=trainer)

        current = (
            _serialize_held_item(pokemon.held_item)
            if pokemon.held_item_id else None
        )

        inv_qs = (
            TrainerInventory.objects
            .filter(trainer=trainer, item__item_type="held", quantity__gt=0)
            .select_related("item")
            .order_by("item__name")
        )

        available = [
            {**_serialize_held_item(inv.item), "quantity": inv.quantity}
            for inv in inv_qs
        ]

        return JsonResponse({
            "success":      True,
            "current_held": current,
            "available":    available,
        })