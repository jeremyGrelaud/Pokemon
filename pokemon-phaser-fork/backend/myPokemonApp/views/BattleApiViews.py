#!/usr/bin/python3
"""
Vues Django — APIs JSON utilitaires pour le combat.

  GET /get_trainer_team/   → GetTrainerTeam   : équipe active du dresseur
  GET /get_trainer_items/  → GetTrainerItems  : inventaire utilisable en combat
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from myPokemonApp.models.Trainer import Trainer, TrainerInventory
from myPokemonApp.gameUtils import serialize_pokemon


@login_required
@require_http_methods(['GET'])
def GetTrainerTeam(request):
    """
    Retourne l'équipe active du dresseur (is_in_party=True, max 6 Pokémon).
    Utilise serialize_pokemon() de gameUtils pour éviter la duplication de structure.
    """
    trainer_id         = request.GET.get('trainer_id')
    exclude_pokemon_id = request.GET.get('exclude_pokemon_id')

    trainer = get_object_or_404(Trainer, pk=trainer_id)
    team    = trainer.pokemon_team.filter(is_in_party=True)

    if exclude_pokemon_id:
        team = team.exclude(pk=exclude_pokemon_id)

    team_data = []
    for pokemon in team:
        data = serialize_pokemon(pokemon)
        data['nickname']         = pokemon.nickname
        data['species']          = {'name': pokemon.species.name, 'id': pokemon.species.id}
        data['status_condition'] = pokemon.status_condition
        team_data.append(data)

    return JsonResponse({'success': True, 'team': team_data})


@login_required
@require_http_methods(['GET'])
def GetTrainerItems(request):
    """Retourne les objets du dresseur utilisables en combat, avec leurs quantités."""
    trainer = get_object_or_404(Trainer, pk=request.GET.get('trainer_id'))

    BATTLE_USABLE_TYPES = ('potion', 'pokeball', 'status', 'battle')
    inventory = TrainerInventory.objects.filter(
        trainer=trainer,
        quantity__gt=0,
        item__item_type__in=BATTLE_USABLE_TYPES,
    ).select_related('item')

    items_data = [
        {
            'id':          inv.id,
            'name':        inv.item.name,
            'quantity':    inv.quantity,
            'item_type':   inv.item.item_type,
            'description': inv.item.description,
        }
        for inv in inventory
    ]

    return JsonResponse({'success': True, 'items': items_data})