#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from myPokemonApp.gameUtils import (
    deposit_pokemon,
    withdraw_pokemon,
    get_or_create_player_trainer,
    serialize_pokemon_moves,
    auto_reorganize_party,
)

from ..models import *



# ============================================================================
# ÉQUIPE DU JOUEUR
# ============================================================================

@method_decorator(login_required, name='dispatch')
class MyTeamView(generic.ListView):
    """Vue de l'équipe du joueur"""
    model = PlayablePokemon
    template_name = "trainer/my_team.html"
    context_object_name = 'team'
    
    def get_queryset(self):
        trainer = get_or_create_player_trainer(self.request.user)
        return trainer.pokemon_team.filter(is_in_party=True).order_by('party_position')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_or_create_player_trainer(self.request.user)
        
        # PC (Pokémon en réserve)
        pc_pokemon = trainer.pokemon_team.filter(is_in_party=False).order_by('species__pokedex_number')
        
        # Inventaire
        inventory = trainer.inventory.all().select_related('item')
        
        context.update({
            'trainer': trainer,
            'pc_pokemon': pc_pokemon,
            'inventory': inventory
        })
        
        return context





@login_required
@require_POST
def heal_pokemon_api(request):
    """
    API pour soigner un Pokémon (restaure HP et PP)
    """
    try:
        data = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')

        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        trainer = get_or_create_player_trainer(request.user)
        if pokemon.trainer != trainer:
            return JsonResponse({'success': False, 'error': 'Ce Pokémon ne vous appartient pas'})

        pokemon.heal()
        pokemon.cure_status()
        pokemon.restore_all_pp()
        pokemon.reset_combat_stats()

        return JsonResponse({'success': True, 'message': f'{pokemon} a été soigné!'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def send_to_pc_api(request):
    """
    API pour envoyer un Pokémon au PC
    """
    try:
        data = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')

        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        trainer = get_or_create_player_trainer(request.user)
        if pokemon.trainer != trainer:
            return JsonResponse({'success': False, 'error': 'Ce Pokémon ne vous appartient pas'})

        team_count = trainer.pokemon_team.filter(is_in_party=True).count()
        if team_count <= 1:
            return JsonResponse({'success': False, 'error': 'Vous devez garder au moins 1 Pokémon dans votre équipe'})

        deposit_pokemon(pokemon)
        auto_reorganize_party(trainer)

        return JsonResponse({'success': True, 'message': f'{pokemon} a été envoyé au PC'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def add_to_party_api(request):
    """
    API pour ajouter un Pokémon du PC à l'équipe
    """
    try:
        data = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')

        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        trainer = get_or_create_player_trainer(request.user)
        if pokemon.trainer != trainer:
            return JsonResponse({'success': False, 'error': 'Ce Pokémon ne vous appartient pas'})

        team_count = trainer.pokemon_team.filter(is_in_party=True).count()
        if team_count >= 6:
            return JsonResponse({'success': False, 'error': 'Votre équipe est complète (6/6)'})

        pokemon.is_in_party = True
        pokemon.save()
        auto_reorganize_party(trainer)

        return JsonResponse({'success': True, 'message': f'{pokemon} a été ajouté à l\'équipe'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def swap_move_api(request):
    """
    API pour remplacer un move actif par un move apprenable.
    Body JSON :
      { "pokemon_id": int, "remove_move_id": int, "add_move_id": int }
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance

    try:
        data       = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')
        remove_id  = data.get('remove_move_id')
        add_id     = data.get('add_move_id')

        trainer = get_or_create_player_trainer(request.user)
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id, trainer=trainer)

        to_remove = PokemonMoveInstance.objects.filter(pokemon=pokemon, move_id=remove_id).first()
        if not to_remove:
            return JsonResponse({'success': False, 'error': 'Ce move ne fait pas partie du deck actif.'})

        learnable = pokemon.species.learnable_moves.filter(
            move_id=add_id,
            level_learned__lte=pokemon.level
        ).first()
        if not learnable:
            return JsonResponse({'success': False, 'error': 'Ce move ne peut pas être appris à ce niveau.'})

        if PokemonMoveInstance.objects.filter(pokemon=pokemon, move_id=add_id).exists():
            return JsonResponse({'success': False, 'error': 'Ce move est déjà dans le deck.'})

        new_move = learnable.move
        to_remove.delete()
        PokemonMoveInstance.objects.create(pokemon=pokemon, move=new_move, current_pp=new_move.pp)

        return JsonResponse({'success': True, 'moves': serialize_pokemon_moves(pokemon)})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_pokemon_moves_api(request):
    """
    GET — Retourne le deck actif + tous les moves apprenables jusqu'au niveau actuel.
    Query param : ?pokemon_id=<int>
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance

    trainer    = get_or_create_player_trainer(request.user)
    pokemon_id = request.GET.get('pokemon_id')
    pokemon    = get_object_or_404(PlayablePokemon, pk=pokemon_id, trainer=trainer)

    active_ids = set(
        PokemonMoveInstance.objects.filter(pokemon=pokemon).values_list('move_id', flat=True)
    )
    moves = serialize_pokemon_moves(pokemon)

    learnable_qs = pokemon.species.learnable_moves.filter(
        level_learned__lte=pokemon.level
    ).select_related('move', 'move__type').order_by('level_learned')

    learnable = [
        {
            'id':            lm.move.id,
            'name':          lm.move.name,
            'type':          lm.move.type.name if lm.move.type else '',
            'category':      lm.move.category,
            'power':         lm.move.power,
            'accuracy':      lm.move.accuracy,
            'pp':            lm.move.pp,
            'level_learned': lm.level_learned,
        }
        for lm in learnable_qs
        if lm.move_id not in active_ids
    ]

    return JsonResponse({
        'success':      True,
        'pokemon_id':   pokemon.id,
        'pokemon_name': pokemon.nickname or pokemon.species.name,
        'moves':        moves,
        'learnable':    learnable,
    })


@login_required
@require_POST
def reorder_party_api(request):
    """
    API pour réordonner l'équipe via drag & drop.
    Attend un JSON : { "order": [id1, id2, id3, ...] }
    """
    try:
        data    = json.loads(request.body)
        order   = data.get('order', [])
        trainer = get_or_create_player_trainer(request.user)

        team_ids = set(
            trainer.pokemon_team.filter(is_in_party=True).values_list('id', flat=True)
        )
        if set(order) != team_ids:
            return JsonResponse({'success': False, 'error': 'IDs invalides'}, status=400)

        for position, pk in enumerate(order, start=1):
            trainer.pokemon_team.filter(pk=pk).update(party_position=position)

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)