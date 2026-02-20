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
import json

from myPokemonApp.models import PokemonCenter, CenterVisit, Trainer, NurseDialogue, PlayerLocation, Zone


def _trainer_is_at_pokemon_center(trainer):
    """Renvoie True si le trainer se trouve actuellement dans une zone avec un Centre Pokémon"""
    try:
        loc = PlayerLocation.objects.get(trainer=trainer)
        return loc.current_zone.has_pokemon_center
    except PlayerLocation.DoesNotExist:
        return True  # Pas de localisation → on ne bloque pas


@method_decorator(login_required, name='dispatch')
class PokemonCenterListView(generic.ListView):
    """Liste de tous les Centres Pokémon"""
    model = PokemonCenter
    template_name = 'pokemon_center/center_list.html'
    context_object_name = 'centers'
    
    def dispatch(self, request, *args, **kwargs):
        trainer = get_object_or_404(Trainer, username=request.user.username)
        if not _trainer_is_at_pokemon_center(trainer):
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
        trainer = get_object_or_404(Trainer, username=self.request.user.username)
        context['trainer'] = trainer
        
        # Statistiques
        context['total_visits'] = CenterVisit.objects.filter(trainer=trainer).count()
        context['total_pokemon_healed'] = sum(
            visit.pokemon_healed 
            for visit in CenterVisit.objects.filter(trainer=trainer)
        )
        
        return context


@method_decorator(login_required, name='dispatch')
class PokemonCenterDetailView(generic.DetailView):
    """Vue détaillée d'un Centre Pokémon"""
    model = PokemonCenter
    template_name = 'pokemon_center/center_detail.html'
    context_object_name = 'center'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_object_or_404(Trainer, username=self.request.user.username)
        
        # Équipe du joueur
        team = trainer.pokemon_team.filter(is_in_party=True)
        team_needs_healing = any(
            p.current_hp < p.max_hp or p.status_condition 
            for p in team
        )
        
        # Dialogues
        greeting = NurseDialogue.get_random_dialogue(
            'greeting',
            trainer.badges,
            self.object
        )
        
        context.update({
            'trainer': trainer,
            'team': team,
            'team_needs_healing': team_needs_healing,
            'greeting': greeting.text if greeting else self.object.nurse_greeting,
            
            # Historique des visites dans ce centre
            'recent_visits': CenterVisit.objects.filter(
                trainer=trainer,
                center=self.object
            )[:5]
        })
        
        return context


@login_required
@require_POST
def heal_team_api(request):
    """API pour soigner l'équipe"""
    try:
        data = json.loads(request.body)
        center_id = data.get('center_id')
        
        trainer = get_object_or_404(Trainer, username=request.user.username)
        center = get_object_or_404(PokemonCenter, pk=center_id)
        
        # Soigner l'équipe
        result = center.heal_trainer_team(trainer)
        
        if result['success']:
            # Dialogue de fin
            complete_dialogue = NurseDialogue.get_random_dialogue(
                'complete',
                trainer.badges,
                center
            )
            
            if complete_dialogue:
                result['message'] = complete_dialogue.text
            
            return JsonResponse({
                'success': True,
                'healed_count': result['healed_count'],
                'cost': result['cost'],
                'new_balance': trainer.money,
                'message': result['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['message']
            })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def center_history_view(request):
    """Historique des visites aux Centres Pokémon"""
    trainer = get_object_or_404(Trainer, username=request.user.username)
    
    visits = CenterVisit.objects.filter(trainer=trainer).select_related('center')
    
    # Statistiques
    total_visits = visits.count()
    total_healed = sum(visit.pokemon_healed for visit in visits)
    total_spent = sum(visit.cost for visit in visits)
    
    # Centre le plus visité
    from django.db.models import Count
    favorite_center = visits.values('center__name').annotate(
        visit_count=Count('id')
    ).order_by('-visit_count').first()
    
    context = {
        'trainer': trainer,
        'visits': visits[:50],  # 50 dernières visites
        'total_visits': total_visits,
        'total_healed': total_healed,
        'total_spent': total_spent,
        'favorite_center': favorite_center,
    }
    
    return render(request, 'pokemon_center/history.html', context)


@login_required
@require_POST
def access_pc_from_center_api(request):
    """Accéder au PC depuis le Centre Pokémon"""
    # Cette vue redirige simplement vers la gestion du PC
    # ou retourne les données du PC si c'est une API
    
    trainer = get_object_or_404(Trainer, username=request.user.username)
    
    # Pokémon dans le PC
    pc_pokemon = trainer.pokemon_team.filter(is_in_party=False)
    
    pokemon_data = [
        {
            'id': p.id,
            'nickname': p.nickname,
            'species': p.species.name,
            'level': p.level,
            'current_hp': p.current_hp,
            'max_hp': p.max_hp,
            'types': [
                p.species.primary_type.name,
                p.species.secondary_type.name if p.species.secondary_type else None
            ]
        }
        for p in pc_pokemon
    ]
    
    return JsonResponse({
        'success': True,
        'pc_pokemon': pokemon_data,
        'count': len(pokemon_data)
    })