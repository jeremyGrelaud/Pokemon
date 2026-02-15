#!/usr/bin/python3
"""
Views Django pour l'application Pokémon Gen 1
Adapté aux nouveaux modèles
"""

import bleach
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
import django_tables2 as tables
from .Views import GenericOverview
from django.views import generic
from ..models import *


# ============================================================================
# CAPACITÉS POKÉMON
# ============================================================================

class PokemonMoveOverView(GenericOverview):
    """Vue liste de toutes les capacités"""
    model = PokemonMove
    template_name = "pokemon/moves_list.html"
    
    class MovesTable(tables.Table):
        name = tables.TemplateColumn(
            '<a href="{% url \'PokemonMoveDetailView\' record.id %}">{{ record.name }}</a>'
        )
        type = tables.TemplateColumn(
            '<span class="badge badge-type-{{record.type.name}}">{{record.type.name}}</span>'
        )
        category = tables.Column()
        power = tables.Column()
        accuracy = tables.Column()
        pp = tables.Column()
        
        class Meta:
            model = PokemonMove
            fields = ('name', 'type', 'category', 'power', 'accuracy', 'pp')
            attrs = {'class': 'table table-striped table-hover'}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtres
        move_filter = Q()
        search_query = bleach.clean(self.request.GET.get('searchQuery', ''), tags=[], attributes={})
        type_filter = self.request.GET.get('typeFilter', '')
        category_filter = self.request.GET.get('categoryFilter', '')
        
        if search_query:
            move_filter.add(Q(name__icontains=search_query), Q.AND)
        
        if type_filter:
            move_filter.add(Q(type__name=type_filter), Q.AND)
        
        if category_filter:
            move_filter.add(Q(category=category_filter), Q.AND)
        
        # Pagination
        queryset = PokemonMove.objects.filter(move_filter).distinct().order_by('name')
        paginator = Paginator(queryset, 25)
        page_number = self.request.GET.get('page', 1)
        page_objects = paginator.get_page(page_number)
        
        table = self.MovesTable(page_objects)
        
        types = PokemonType.objects.all().order_by('name')
        
        context.update({
            'table': table,
            'page_objects': page_objects,
            'searchQuery': search_query,
            'typeFilter': type_filter,
            'categoryFilter': category_filter,
            'types': types
        })
        
        return context


class PokemonMoveDetailView(generic.DetailView):
    """Vue détails d'une capacité"""
    model = PokemonMove
    template_name = "pokemon/move_detail.html"
    context_object_name = 'move'

