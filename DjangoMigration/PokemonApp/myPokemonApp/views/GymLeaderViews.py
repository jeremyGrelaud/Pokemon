#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

from django.views import generic
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

