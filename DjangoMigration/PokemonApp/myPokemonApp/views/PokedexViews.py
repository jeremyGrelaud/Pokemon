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

from ..models import *


# ============================================================================
# POKÉDEX - POKÉMON TEMPLATES
# ============================================================================

class PokemonOverView(GenericOverview):
    """Vue liste de tous les Pokémon (templates)"""
    model = Pokemon
    template_name = "pokemon/pokedex.html"
    
    class PokedexTable(tables.Table):
        pokedex_number = tables.Column(verbose_name="#")
        name = tables.TemplateColumn(
            '<a href="{% url \'PokemonDetailView\' record.id %}">{{ record.name }}</a>',
            verbose_name="Nom"
        )
        primary_type = tables.TemplateColumn(
            '<span class="badge badge-type-{{record.primary_type.name}}">{{record.primary_type.name}}</span>',
            verbose_name="Type 1"
        )
        secondary_type = tables.TemplateColumn(
            '{% if record.secondary_type %}<span class="badge badge-type-{{record.secondary_type.name}}">{{record.secondary_type.name}}</span>{% endif %}',
            verbose_name="Type 2"
        )
        base_hp = tables.Column(verbose_name="HP")
        base_attack = tables.Column(verbose_name="ATK")
        base_defense = tables.Column(verbose_name="DEF")
        base_special_attack = tables.Column(verbose_name="SP.ATK")
        base_special_defense = tables.Column(verbose_name="SP.DEF")
        base_speed = tables.Column(verbose_name="SPD")
        total_stats = tables.Column(empty_values=(), verbose_name="Total")
        
        def render_total_stats(self, record):
            return (record.base_hp + record.base_attack + record.base_defense + 
                   record.base_special_attack + record.base_special_defense + record.base_speed)
        
        class Meta:
            model = Pokemon
            fields = ('pokedex_number', 'name', 'primary_type', 'secondary_type', 
                     'base_hp', 'base_attack', 'base_defense', 'base_special_attack',
                     'base_special_defense', 'base_speed', 'total_stats')
            attrs = {'class': 'table table-striped table-hover'}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtres
        pokemon_filter = Q()
        search_query = bleach.clean(self.request.GET.get('searchQuery', ''), tags=[], attributes={})
        type_filter = self.request.GET.get('typeFilter', '')
        gen_filter = self.request.GET.get('genFilter', 'all')
        
        if search_query:
            pokemon_filter.add(Q(name__icontains=search_query) | 
                             Q(pokedex_number__icontains=search_query), Q.AND)
        
        if type_filter:
            pokemon_filter.add(
                Q(primary_type__name=type_filter) | Q(secondary_type__name=type_filter), 
                Q.AND
            )
        
        # Génération (Gen 1 = 1-151)
        if gen_filter == 'gen1':
            pokemon_filter.add(Q(pokedex_number__lte=151), Q.AND)
        
        # Pagination
        queryset = Pokemon.objects.filter(pokemon_filter).distinct().order_by('pokedex_number')
        paginator = Paginator(queryset, 20)
        page_number = self.request.GET.get('page', 1)
        page_objects = paginator.get_page(page_number)
        
        # Table
        table = self.PokedexTable(page_objects)
        
        # Types pour le filtre
        types = PokemonType.objects.all().order_by('name')
        
        context.update({
            'table': table,
            'pageObjects': page_objects,
            'searchQuery': search_query,
            'typeFilter': type_filter,
            'genFilter': gen_filter,
            'types': types,
            'total_count': Pokemon.objects.count()
        })
        
        return context


class PokemonDetailView(generic.DetailView):
    """Vue détails d'un Pokémon (template)"""
    model = Pokemon
    template_name = "pokemon/pokemon_detail.html"
    context_object_name = 'pokemon'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pokemon = self.object
        
        # Évolutions
        evolutions_from = pokemon.evolutions_from.all()
        evolutions_to = pokemon.evolutions_to.all()
        
        # Capacités apprises par niveau
        learnable_moves = pokemon.learnable_moves.all().order_by('level_learned')
        
        # Stats totales
        total_stats = (pokemon.base_hp + pokemon.base_attack + pokemon.base_defense +
                      pokemon.base_special_attack + pokemon.base_special_defense + 
                      pokemon.base_speed)
        
        context.update({
            'evolutions_from': evolutions_from,
            'evolutions_to': evolutions_to,
            'learnable_moves': learnable_moves,
            'total_stats': total_stats
        })
        
        return context