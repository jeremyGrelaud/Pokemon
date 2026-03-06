#!/usr/bin/python3
"""
Views Django — Objets (Items), incluant CT/CS
"""

from django.views import generic
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
import json

from ..models import Item, PlayablePokemon, PokemonLearnableMove


# ============================================================================
# LISTE DES OBJETS
# ============================================================================

class ItemListView(generic.ListView):
    """Liste des objets — filtre par type possible via ?itemType=tm"""
    model = Item
    template_name = "items/item_list.html"
    context_object_name = 'items'
    paginate_by = 30 

    def get_queryset(self):
        item_type = self.request.GET.get('itemType', '')
        queryset = Item.objects.all().order_by('item_type', 'tm_number', 'name')
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_types']    = Item.ITEM_TYPES
        context['selected_type'] = self.request.GET.get('itemType', '')
        return context


# ============================================================================
# UTILISATION D'UNE CT / CS SUR UN POKÉMON
# ============================================================================

class UseTMView(LoginRequiredMixin, View):
    """
    API JSON pour utiliser une CT ou CS sur un PlayablePokemon.

    POST /items/tm/<item_id>/use/
    Body JSON :
        {
            "pokemon_id": 42,
            "replace_move_id": 7   // optionnel — ID PokemonMove à remplacer
        }

    Réponses :
        200  { success: true,  message: "...", move: { id, name } }
        200  { success: false, message: "...", needs_replace: true,
               move: { id, name }, current_moves: [...] }
        400  { error: "..." }
        404  item / pokémon non trouvé
    """

    def post(self, request, item_id):
        # ── Parsing du body ─────────────────────────────────────────────────
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'error': 'JSON invalide.'}, status=400)

        pokemon_id      = body.get('pokemon_id')
        replace_move_id = body.get('replace_move_id')   # peut être None

        if not pokemon_id:
            return JsonResponse({'error': 'pokemon_id requis.'}, status=400)

        # ── Récupération des objets ──────────────────────────────────────────
        item    = get_object_or_404(Item, pk=item_id, item_type__in=('tm', 'cs'))
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)

        # Vérifier que le Pokémon appartient bien au dresseur connecté
        if hasattr(request, 'game_save') and request.game_save:
            trainer = request.game_save.trainer
        else:
            # Fallback : cherche via le trainer lié à l'user
            trainer = getattr(request.user, 'trainer', None)

        if trainer and pokemon.trainer != trainer:
            return JsonResponse(
                {'error': 'Ce Pokémon ne vous appartient pas.'},
                status=403,
            )

        # ── Move à remplacer (optionnel) ─────────────────────────────────────
        replace_move = None
        if replace_move_id:
            from ..models import PokemonMove
            replace_move = get_object_or_404(PokemonMove, pk=replace_move_id)

        # ── Application de la CT/CS ──────────────────────────────────────────
        result = item.teach_move_to_pokemon(pokemon, replace_move=replace_move)

        # ── Formatage de la réponse ──────────────────────────────────────────
        response_data = {
            'success': result['success'],
            'message': result['message'],
        }

        if 'move' in result and result['move']:
            response_data['move'] = {
                'id':   result['move'].id,
                'name': result['move'].name,
            }

        if result.get('needs_replace'):
            response_data['needs_replace'] = True
            # Envoyer les 4 moves actuels pour que le front puisse proposer
            # le choix de l'oubli
            from ..models import PokemonMoveInstance
            current_moves = PokemonMoveInstance.objects.filter(
                pokemon=pokemon
            ).select_related('move')
            response_data['current_moves'] = [
                {'id': mi.move.id, 'name': mi.move.name, 'pp': mi.current_pp}
                for mi in current_moves
            ]

        return JsonResponse(response_data)


class TMCompatibilityView(LoginRequiredMixin, View):
    """
    Retourne la liste des CT/CS qu'un Pokémon peut apprendre.

    GET /items/tm/compatible/<pokemon_id>/

    Réponse :
        200 { compatible_tms: [ { item_id, name, move_name, already_known }, ... ] }
    """

    def get(self, request, pokemon_id):
        from myPokemonApp.gameUtils import get_or_create_player_trainer
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        trainer = get_or_create_player_trainer(request.user)

        # Moves que le Pokémon (espèce) peut apprendre via TM
        learnable_tm_move_ids = PokemonLearnableMove.objects.filter(
            pokemon=pokemon.species,
            learn_method='tm',
        ).values_list('move_id', flat=True)

        # Moves que le Pokémon connaît déjà
        known_move_ids = set(pokemon.moves.values_list('id', flat=True))

        # CT/CS que le DRESSEUR possède ET que le Pokémon peut apprendre
        owned_tm_item_ids = trainer.inventory.filter(
            item__item_type__in=('tm', 'cs'),
        ).values_list('item_id', flat=True)

        tm_items = Item.objects.filter(
            id__in=owned_tm_item_ids,
            tm_move_id__in=learnable_tm_move_ids,
        ).select_related('tm_move', 'tm_move__type').order_by('item_type', 'tm_number')

        data = [
            {
                'item_id':       item.id,
                'name':          str(item),
                'move_id':       item.tm_move.id,
                'move_name':     item.tm_move.name,
                'move_type':     item.tm_move.type.name if item.tm_move.type else '',
                'already_known': item.tm_move_id in known_move_ids,
                'item_type':     item.item_type,
            }
            for item in tm_items
        ]

        return JsonResponse({'compatible_tms': data})