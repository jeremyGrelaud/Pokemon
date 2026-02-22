#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from myPokemonApp.gameUtils import get_or_create_player_trainer
from ..models import *


# ============================================================================
# CHAMPIONS D'ARÈNE
# ============================================================================

class GymLeaderListView(generic.ListView):
    """Liste des Champions d'Arène"""
    model = GymLeader
    template_name = "gym/gym_leaders.html"
    context_object_name = 'gym_leaders'
    
    def get_queryset(self):
        return GymLeader.objects.all().order_by('badge_order').select_related('trainer', 'specialty_type')


class GymLeaderDetailView(generic.DetailView):
    """Détails d'un Champion d'Arène"""
    model = GymLeader
    template_name = "gym/gym_leader_detail.html"
    context_object_name = 'gym_leader'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Équipe du champion
        team = self.object.trainer.pokemon_team.all()
        
        context['team'] = team
        return context


@method_decorator(login_required, name='dispatch')
class BadgeBoxView(generic.TemplateView):
    """Boîte à badges — affiche les 8 badges de Kanto avec leur statut obtenu/non-obtenu."""
    template_name = "gym/badge_box.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainer = get_or_create_player_trainer(self.request.user)

        gym_leaders = GymLeader.objects.select_related(
            'trainer', 'specialty_type'
        ).order_by('badge_order')

        badge_data = []
        for gl in gym_leaders:
            badge_data.append({
                'gym_leader': gl,
                'obtained': trainer.badges >= gl.badge_order,
            })

        context.update({
            'trainer': trainer,
            'badge_data': badge_data,
            'badges_count': trainer.badges,
        })
        return context