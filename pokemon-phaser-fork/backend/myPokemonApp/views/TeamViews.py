#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

import json
import logging

from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import re

logger = logging.getLogger(__name__)
from myPokemonApp.gameUtils import (
    deposit_pokemon,
    withdraw_pokemon,
    get_or_create_player_trainer,
    get_player_trainer,
    serialize_pokemon_moves,
    auto_reorganize_party,
)

from myPokemonApp.models.PlayablePokemon import PlayablePokemon, PokemonMoveInstance
from myPokemonApp.models.PokemonMove import PokemonMove
from myPokemonApp.models.Trainer import Trainer
from myPokemonApp.models.GameSave import GameSave



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
        return trainer.party   # Trainer.party property

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_or_create_player_trainer(self.request.user)

        # Inventaire complet, pré-chargé
        full_inventory = (
            trainer.inventory
            .all()
            .select_related('item', 'item__tm_move', 'item__tm_move__type')
            .order_by('item__item_type', 'item__tm_number', 'item__name')
        )

        # Séparer objets normaux et CT/CS
        regular_inventory = full_inventory.exclude(item__item_type__in=('tm', 'cs'))
        tm_inventory      = full_inventory.filter(item__item_type__in=('tm', 'cs'))

        context.update({
            'trainer':    trainer,
            'pc_pokemon': trainer.pc.order_by('species__pokedex_number'),
            'inventory':  regular_inventory,
            'tm_inventory': tm_inventory,
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
        logger.exception("Erreur inattendue dans TeamViews")
        return JsonResponse({'success': False, 'error': "Une erreur est survenue. Veuillez réessayer."}, status=400)


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
        logger.exception("Erreur inattendue dans TeamViews")
        return JsonResponse({'success': False, 'error': "Une erreur est survenue. Veuillez réessayer."}, status=400)


@login_required
@require_POST
def add_to_party_api(request):
    """
    API pour ajouter un Pokémon du PC à l'équipe
    """
    try:
        data       = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')

        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        trainer = get_or_create_player_trainer(request.user)
        if pokemon.trainer != trainer:
            return JsonResponse({'success': False, 'error': 'Ce Pokémon ne vous appartient pas'})

        if trainer.party_count >= 6:
            return JsonResponse({'success': False, 'error': 'Votre équipe est complète (6/6)'})

        # withdraw_pokemon gère is_in_party + party_position + save()
        next_position = trainer.party_count + 1
        success, message = withdraw_pokemon(pokemon, next_position)
        if not success:
            return JsonResponse({'success': False, 'error': message})

        auto_reorganize_party(trainer)
        return JsonResponse({'success': True, 'message': message})

    except Exception as e:
        logger.exception("Erreur inattendue dans TeamViews")
        return JsonResponse({'success': False, 'error': "Une erreur est survenue. Veuillez réessayer."}, status=400)


@login_required
@require_POST
def swap_move_api(request):
    """
    API pour remplacer un move actif par un move apprenable, ou ajouter directement
    si le deck a moins de 4 capacités.
    Body JSON :
      { "pokemon_id": int, "remove_move_id": int|null, "add_move_id": int }
    Si remove_move_id est null/absent et que le deck a < 4 moves, le move est simplement ajouté.
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance

    try:
        data       = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')
        remove_id  = data.get('remove_move_id')   # peut être None
        add_id     = data.get('add_move_id')

        trainer = get_or_create_player_trainer(request.user)
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id, trainer=trainer)

        # Vérifier que le move est apprenable PAR NIVEAU (pas via TM)
        learnable = pokemon.species.learnable_moves.filter(
            move_id=add_id,
            learn_method='level',
            level_learned__lte=pokemon.level
        ).first()
        if not learnable:
            return JsonResponse({'success': False, 'error': 'Ce move ne peut pas être appris à ce niveau.'})

        if PokemonMoveInstance.objects.filter(pokemon=pokemon, move_id=add_id).exists():
            return JsonResponse({'success': False, 'error': 'Ce move est déjà dans le deck.'})

        new_move = learnable.move
        current_count = PokemonMoveInstance.objects.filter(pokemon=pokemon).count()

        if remove_id is None:
            # Ajout direct (deck non plein)
            if current_count >= 4:
                return JsonResponse({'success': False, 'error': 'Le deck est plein (4/4). Choisissez un move à remplacer.'})
            PokemonMoveInstance.objects.create(pokemon=pokemon, move=new_move, current_pp=new_move.pp)
        else:
            # Remplacement
            to_remove = PokemonMoveInstance.objects.filter(pokemon=pokemon, move_id=remove_id).first()
            if not to_remove:
                return JsonResponse({'success': False, 'error': 'Ce move ne fait pas partie du deck actif.'})
            to_remove.delete()
            PokemonMoveInstance.objects.create(pokemon=pokemon, move=new_move, current_pp=new_move.pp)

        return JsonResponse({'success': True, 'moves': serialize_pokemon_moves(pokemon)})

    except Exception as e:
        logger.exception("Erreur inattendue dans TeamViews")
        return JsonResponse({'success': False, 'error': "Une erreur est survenue. Veuillez réessayer."}, status=400)


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
        learn_method='level',
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
        logger.exception("Erreur inattendue dans TeamViews")
        return JsonResponse({'success': False, 'error': "Une erreur est survenue. Veuillez réessayer."}, status=400)

@login_required
@require_POST
def reorder_moves_api(request):
    """
    API pour réordonner les capacités d'un Pokémon.
    Stratégie : supprime toutes les instances et les recrée dans le nouvel ordre,
    en préservant les PP actuels. Aucune migration nécessaire.
    Body JSON : { "pokemon_id": int, "order": [move_id1, move_id2, ...] }
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
    from django.db import transaction

    try:
        data       = json.loads(request.body)
        pokemon_id = data.get('pokemon_id')
        order      = data.get('order', [])

        trainer = get_or_create_player_trainer(request.user)
        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id, trainer=trainer)

        # Récupérer les instances actuelles et indexer par move_id
        instances = PokemonMoveInstance.objects.filter(pokemon=pokemon).select_related('move')
        pp_map = {inst.move_id: inst.current_pp for inst in instances}

        # Vérifier que les IDs envoyés correspondent exactement au deck actuel
        current_ids = set(pp_map.keys())
        if set(order) != current_ids or len(order) != len(current_ids):
            return JsonResponse({'success': False, 'error': 'IDs de capacités invalides.'}, status=400)

        # Supprimer et recréer dans l'ordre en une transaction atomique.
        # Les moves sont pré-chargés en une seule requête pour éviter un
        # PokemonMove.objects.get() par entrée dans la boucle.
        with transaction.atomic():
            from myPokemonApp.models.PokemonMove import PokemonMove
            moves_map = {m.id: m for m in PokemonMove.objects.filter(pk__in=order)}
            instances.delete()
            PokemonMoveInstance.objects.bulk_create([
                PokemonMoveInstance(
                    pokemon=pokemon,
                    move=moves_map[move_id],
                    current_pp=pp_map[move_id],
                )
                for move_id in order
            ])

        from myPokemonApp.gameUtils import serialize_pokemon_moves
        return JsonResponse({'success': True, 'moves': serialize_pokemon_moves(pokemon)})

    except Exception as e:
        logger.exception("Erreur inattendue dans TeamViews")
        return JsonResponse({'success': False, 'error': "Une erreur est survenue. Veuillez réessayer."}, status=400)

@require_POST
@login_required
def rename_pokemon_api(request):
    """Endpoint pour renommer (donner un surnom à) un Pokémon."""
    try:
        data = json.loads(request.body)
        pokemon_id = int(data.get('pokemon_id', 0))
        nickname = data.get('nickname', '').strip()

        if len(nickname) > 12:
            return JsonResponse({'success': False, 'error': 'Le surnom ne peut pas dépasser 12 caractères.'}, status=400)

        trainer = get_player_trainer(request.user)
        save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
        if not save:
            return JsonResponse({'success': False, 'error': 'Aucune sauvegarde active.'}, status=400)

        pokemon = get_object_or_404(PlayablePokemon, pk=pokemon_id)
        if GameSave.objects.filter(trainer=pokemon.trainer, is_active=True).first()  != save:
            return JsonResponse({'success': False, 'error': 'Ce Pokémon ne vous appartient pas.'}, status=403)

        # Nickname vide = suppression du surnom
        pokemon.nickname = nickname if nickname else None
        pokemon.save(update_fields=['nickname'])

        return JsonResponse({'success': True, 'nickname': pokemon.nickname or ''})

    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Données invalides.'}, status=400)
    except Exception:
        logger.exception("Erreur dans rename_pokemon_api")
        return JsonResponse({'success': False, 'error': 'Une erreur est survenue.'}, status=500)
# ============================================================================
# PC DÉDIÉ
# ============================================================================

@method_decorator(login_required, name='dispatch')
class PCView(generic.TemplateView):
    """Interface dédiée au PC — Pokémon en réserve avec pagination + filtres backend."""
    template_name = "trainer/pc.html"
    PAGE_SIZE = 24

    def get_context_data(self, **kwargs):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        context = super().get_context_data(**kwargs)
        trainer  = get_or_create_player_trainer(self.request.user)
        request  = self.request

        # ── Paramètres GET ─────────────────────────────────────────────────
        search     = request.GET.get('q', '').strip()
        type_filter = request.GET.get('type', '').strip().lower()
        sort        = request.GET.get('sort', 'dex')
        page_num    = request.GET.get('page', 1)

        # ── Queryset de base ───────────────────────────────────────────────
        pc_qs = (
            trainer.pokemon_team
            .filter(is_in_party=False)
            .select_related(
                'species',
                'species__primary_type',
                'species__secondary_type',
                'held_item',
            )
            .prefetch_related('pokemonmoveinstance_set__move__type')
        )

        # ── Filtres ────────────────────────────────────────────────────────
        if search:
            
            pc_qs = pc_qs.filter(
                Q(nickname__icontains=search) | Q(species__name__icontains=search)
            )
        if type_filter:
            pc_qs = pc_qs.filter(
                Q(species__primary_type__name__iexact=type_filter) |
                Q(species__secondary_type__name__iexact=type_filter)
            )

        # ── Tri ────────────────────────────────────────────────────────────
        sort_map = {
            'dex':        ('species__pokedex_number', 'id'),
            'level-desc': ('-level', 'id'),
            'level-asc':  ('level', 'id'),
            'name':       ('species__name', 'id'),
        }
        pc_qs = pc_qs.order_by(*sort_map.get(sort, ('species__pokedex_number', 'id')))

        # ── Types pour les filtres (toujours calculé sur le PC complet) ───
        all_pc = trainer.pokemon_team.filter(is_in_party=False).select_related('species__primary_type')
        types_present = sorted({
            p.species.primary_type.name
            for p in all_pc
            if p.species.primary_type
        })

        # ── Pagination ─────────────────────────────────────────────────────
        paginator = Paginator(pc_qs, self.PAGE_SIZE)
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context.update({
            'trainer':       trainer,
            'pc_pokemon':    page_obj.object_list,  # seulement la page courante
            'page_obj':      page_obj,
            'paginator':     paginator,
            'party':         trainer.party,
            'party_count':   trainer.party_count,
            'types_present': types_present,
            # Paramètres courants pour les liens de pagination
            'q':             search,
            'type_filter':   type_filter,
            'sort':          sort,
            'pc_total':      paginator.count,
        })
        return context

# ============================================================================
# CENTRE D'ÉCHANGE NPC — Évolutions par trade
# ============================================================================

# Zones possédant un NPC échangeur (Centres Pokémon des grandes villes)
_TRADE_ZONES = {
    'Carmin sur Mer', 'Céladopole', 'Safrania', 'Parmanie',
    "Cramois'Île", 'Jadielle', 'Argenta',
}


@login_required
def trade_center_view(request):
    """
    GET  /team/trade-center/     → liste les Pokémon échangeables (évolution par trade possible)
    POST /team/trade-center/     → effectue le trade NPC et déclenche l'évolution
    Body POST : pokemon_id=<int>

    Règle narrative : le joueur doit se trouver dans une ville avec un Centre Pokémon.
    Le NPC échange le Pokémon contre lui-même (simule le câble d'échange),
    ce qui déclenche l'évolution immédiatement.
    """
    from myPokemonApp.gameUtils import get_player_location
    from myPokemonApp.models.PlayablePokemon import PlayablePokemon

    trainer         = get_player_trainer(request.user)
    player_location = get_player_location(trainer)
    current_zone    = player_location.current_zone if player_location else None

    # Vérifier que le joueur est dans une ville avec Centre d'échange
    in_trade_zone = current_zone and current_zone.name in _TRADE_ZONES

    if request.method == 'POST':
        if not in_trade_zone:
            return JsonResponse({
                'success': False,
                'message': "Vous devez être dans une ville proposant un Centre d'échange."
            }, status=403)

        pokemon_id = request.POST.get('pokemon_id')
        if not pokemon_id:
            return JsonResponse({'error': 'pokemon_id manquant'}, status=400)

        poke = get_object_or_404(
            PlayablePokemon, pk=pokemon_id, trainer=trainer
        )

        can_evolve, evo = poke.check_trade_evolution()
        if not can_evolve:
            return JsonResponse({
                'success': False,
                'message': f"{poke.nickname or poke.species.name} ne peut pas évoluer par échange."
                           + (" (objet tenu requis ?)" if poke.species.evolutions_from.filter(method='trade').exists() else ""),
            })

        old_name  = poke.species.name
        new_name  = evo.evolves_to.name
        msg       = poke.evolve_to(evo.evolves_to)

        # Si l'évolution nécessitait un objet tenu, le consommer
        if evo.required_item and poke.held_item:
            poke.held_item = None
            poke.save(update_fields=['held_item'])

        logger.info("Trade evolution: %s → %s (trainer=%s)", old_name, new_name, trainer.username)

        cleanedName = poke.species.name.replace('♂', 'm').replace('♀', 'f').lower()
        cleanedName = re.sub(r'[^a-z0-9]', '', cleanedName)
        return JsonResponse({
            'success':   True,
            'message':   f"🔗 {old_name} a été échangé… et revient transformé en {new_name} !",
            'old_name':  old_name,
            'new_name':  new_name,
            'sprite_url': f"/static/img/sprites_gen5/normal/{cleanedName}.png",
        })


    # GET — liste les membres de l'équipe capables d'évoluer par échange
    tradeable = []
    for poke in trainer.party:
        can_evolve, evo = poke.check_trade_evolution()
        if can_evolve:
            needs_item = evo.required_item is not None
            tradeable.append({
                'pokemon':    poke,
                'evolves_to': evo.evolves_to,
                'needs_item': needs_item,
                'item_name':  evo.required_item.name if needs_item else None,
                'has_item':   bool(needs_item and poke.held_item and poke.held_item == evo.required_item),
            })

    return render(request, 'trainer/trade_center.html', {
        'tradeable':    tradeable,
        'in_trade_zone': in_trade_zone,
        'current_zone': current_zone,
        'trade_zones':  sorted(_TRADE_ZONES),
        'trainer':      trainer,
    })