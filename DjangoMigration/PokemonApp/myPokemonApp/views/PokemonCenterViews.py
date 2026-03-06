"""
Vues pour le Centre Pokémon
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum
import json

from myPokemonApp.models import PokemonCenter, CenterVisit, Trainer, NurseDialogue, PlayerLocation, Zone
from myPokemonApp.gameUtils import get_player_trainer, trainer_is_at_zone_with


@method_decorator(login_required, name='dispatch')
class PokemonCenterListView(generic.ListView):
    """Liste de tous les Centres Pokémon"""
    model = PokemonCenter
    template_name = 'pokemon_center/center_list.html'
    context_object_name = 'centers'

    def dispatch(self, request, *args, **kwargs):
        trainer = get_player_trainer(request.user)
        if not trainer_is_at_zone_with(trainer, 'has_pokemon_center'):
            messages.warning(
                request,
                "Vous devez être dans une ville possédant un Centre Pokémon pour y accéder."
            )
            return redirect('map_view')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return PokemonCenter.objects.filter(is_available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_player_trainer(self.request.user)
        visits  = CenterVisit.objects.filter(trainer=trainer)
        agg = visits.aggregate(total_pokemon_healed=Sum('pokemon_healed'))

        # Zone actuelle pour griser les centres hors de la ville du joueur
        from myPokemonApp.gameUtils import get_player_location
        location        = get_player_location(trainer)
        current_zone    = location.current_zone if location else None
        zone_name_lower = current_zone.name.lower() if current_zone else ''

        # Enrichir chaque centre avec un flag is_local
        centers_with_local = []
        for center in context['centers']:
            loc_lower = center.location.lower() if center.location else ''
            is_local  = (zone_name_lower in loc_lower or loc_lower in zone_name_lower) if zone_name_lower else True
            centers_with_local.append({'center': center, 'is_local': is_local})

        context['centers']              = centers_with_local
        context['trainer']              = trainer
        context['total_visits']         = visits.count()
        context['total_pokemon_healed'] = agg['total_pokemon_healed'] or 0
        context['current_zone']         = current_zone
        return context


@method_decorator(login_required, name='dispatch')
class PokemonCenterDetailView(generic.DetailView):
    """Vue détaillée d'un Centre Pokémon"""
    model = PokemonCenter
    template_name = 'pokemon_center/center_detail.html'
    context_object_name = 'center'

    def dispatch(self, request, *args, **kwargs):
        trainer = get_player_trainer(request.user)
        # 1. La zone actuelle doit avoir un centre
        if not trainer_is_at_zone_with(trainer, 'has_pokemon_center'):
            messages.warning(request, "Vous devez être dans une ville possédant un Centre Pokémon pour y accéder.")
            return redirect('map_view')
        # 2. Le centre demandé doit être celui de la zone actuelle
        center = get_object_or_404(PokemonCenter, pk=kwargs.get('pk'))
        from myPokemonApp.gameUtils import get_player_location
        location = get_player_location(trainer, create_if_missing=False)
        if location is not None:
            zone_name = location.current_zone.name.lower()
            bldg_loc  = (center.location or '').lower()
            if zone_name not in bldg_loc and bldg_loc not in zone_name:
                messages.warning(request, "Ce Centre Pokémon ne se trouve pas dans votre ville actuelle.")
                return redirect('PokemonCenterListView')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_player_trainer(self.request.user)

        team = trainer.party   # utilise la property Trainer.party

        # PlayablePokemon.needs_healing remplace le any() inline
        team_needs_healing = any(p.needs_healing for p in team)

        greeting = NurseDialogue.get_random_dialogue(
            'greeting', trainer.badges, self.object
        )

        context.update({
            'trainer':            trainer,
            'team':               team,
            'team_needs_healing': team_needs_healing,
            'greeting':           greeting.text if greeting else self.object.nurse_greeting,
            'recent_visits':      CenterVisit.objects.filter(
                trainer=trainer, center=self.object
            )[:5],
        })
        return context


@login_required
@require_POST
def heal_team_api(request):
    """API pour soigner l'équipe"""
    try:
        data      = json.loads(request.body)
        center_id = data.get('center_id')

        trainer = get_player_trainer(request.user)
        center  = get_object_or_404(PokemonCenter, pk=center_id)

        result = center.heal_trainer_team(trainer)

        if result['success']:
            complete_dialogue = NurseDialogue.get_random_dialogue(
                'complete', trainer.badges, center
            )
            if complete_dialogue:
                result['message'] = complete_dialogue.text

            return JsonResponse({
                'success':      True,
                'healed_count': result['healed_count'],
                'cost':         result['cost'],
                'new_balance':  trainer.money,
                'message':      result['message'],
            })
        else:
            return JsonResponse({'success': False, 'error': result['message']})

    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def center_history_view(request):
    """Historique des visites aux Centres Pokémon"""
    import json as _json
    from datetime import date, timedelta
    from django.db.models import Count
    from django.db.models.functions import TruncMonth

    trainer = get_player_trainer(request.user)
    visits  = CenterVisit.objects.filter(trainer=trainer).select_related('center')

    # Statistiques globales — tout en DB
    agg = visits.aggregate(
        total_healed=Sum('pokemon_healed'),
        total_spent=Sum('cost'),
    )
    total_visits  = visits.count()
    total_healed  = agg['total_healed'] or 0
    total_spent   = agg['total_spent']  or 0

    favorite_center = (
        visits.values('center__name')
        .annotate(visit_count=Count('id'))
        .order_by('-visit_count')
        .first()
    )

    today      = date.today()
    six_months = today - timedelta(days=180)

    monthly_qs = (
        visits.filter(visited_at__date__gte=six_months)
        .annotate(month=TruncMonth('visited_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months_map          = {row['month'].strftime('%Y-%m'): row['count'] for row in monthly_qs}
    chart_months_labels = []
    chart_months_data   = []
    MONTH_FR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']

    for i in range(5, -1, -1):
        d         = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        month_key = d.strftime('%Y-%m')
        chart_months_labels.append(f"{MONTH_FR[d.month - 1]} {d.year}")
        chart_months_data.append(months_map.get(month_key, 0))

    centers_qs = (
        visits.values('center__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:6]
    )
    chart_centers_labels = [row['center__name'] for row in centers_qs]
    chart_centers_data   = [row['count']         for row in centers_qs]
    CHART_COLORS = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c']

    context = {
        'trainer':        trainer,
        'visits':         visits.order_by('-visited_at')[:50],
        'total_visits':   total_visits,
        'total_healed':   total_healed,
        'total_spent':    total_spent,
        'favorite_center': favorite_center,
        'chart_months_labels':  _json.dumps(chart_months_labels),
        'chart_months_data':    _json.dumps(chart_months_data),
        'chart_centers_labels': _json.dumps(chart_centers_labels),
        'chart_centers_data':   _json.dumps(chart_centers_data),
        'chart_colors':         _json.dumps(CHART_COLORS[:len(chart_centers_labels)]),
    }
    return render(request, 'pokemon_center/history.html', context)


@login_required
@require_POST
def access_pc_from_center_api(request):
    """Accéder au PC depuis le Centre Pokémon"""
    trainer   = get_player_trainer(request.user)
    pc_pokemon = trainer.pc   # utilise la property Trainer.pc

    from myPokemonApp.gameUtils import serialize_pokemon
    pokemon_data = [
        {
            'id':       p.id,
            'nickname': p.nickname,
            'species':  p.species.name,
            'level':    p.level,
            'current_hp': p.current_hp,
            'max_hp':   p.max_hp,
            'types': [
                p.species.primary_type.name,
                p.species.secondary_type.name if p.species.secondary_type else None,
            ],
        }
        for p in pc_pokemon
    ]

    return JsonResponse({
        'success':    True,
        'pc_pokemon': pokemon_data,
        'count':      len(pokemon_data),
    })