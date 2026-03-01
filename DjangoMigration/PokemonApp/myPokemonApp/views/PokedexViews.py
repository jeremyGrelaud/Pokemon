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
        sprite = tables.Column(
            verbose_name="",
            orderable=False,
            empty_values=(),
        )
        name = tables.TemplateColumn(
            '<a href="{% url \'PokemonDetailView\' record.id %}">{{ record.name }}</a>',
            verbose_name="Nom"
        )

        def render_sprite(self, record):
            import re
            from django.utils.html import format_html
            name = record.name.replace('\u2642', 'm').replace('\u2640', 'f').lower()
            name = re.sub(r'[^a-z0-9]', '', name)
            url = f"/static/img/sprites_gen5/normal/{name}.png"
            fallback = "/static/img/pokeball.png"
            return format_html(
                '<img src="{}" alt="{}" '
                'style="width:40px;height:40px;object-fit:contain;" '
                'onerror="this.src=\'{}\'">',
                url, record.name, fallback
            )
        primary_type = tables.TemplateColumn(
            '<span class="badge badge-type-{{record.primary_type.name}}">{{record.primary_type.name}}</span>',
            verbose_name="Type 1"
        )
        secondary_type = tables.TemplateColumn(
            '{% if record.secondary_type %}<span class="badge badge-type-{{record.secondary_type.name}}">{{record.secondary_type.name}}</span>{% endif %}',
            verbose_name="Type 2"
        )
        caught = tables.TemplateColumn(
            '{% if record.id in caught_ids %}<span class="badge-captured"><i class="fas fa-check"></i> Capturé</span>{% else %}<span class="badge-not-captured">—</span>{% endif %}',
            verbose_name="Capturé",
            orderable=False,
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
            fields = ('pokedex_number', 'sprite', 'name', 'caught', 'primary_type', 'secondary_type',
                      'base_hp', 'base_attack', 'base_defense', 'base_special_attack',
                      'base_special_defense', 'base_speed', 'total_stats')
            attrs = {'class': 'table table-striped table-hover'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtres
        pokemon_filter = Q()
        search_query  = bleach.clean(self.request.GET.get('searchQuery', ''), tags=[], attributes={})
        type_filter   = self.request.GET.get('typeFilter', '')
        gen_filter    = self.request.GET.get('genFilter', 'all')
        caught_filter = self.request.GET.get('caughtFilter', 'all')  # all | caught | missing

        if search_query:
            pokemon_filter.add(
                Q(name__icontains=search_query) | Q(pokedex_number__icontains=search_query),
                Q.AND
            )

        if type_filter:
            pokemon_filter.add(
                Q(primary_type__name=type_filter) | Q(secondary_type__name=type_filter),
                Q.AND
            )

        if gen_filter == 'gen1':
            pokemon_filter.add(Q(pokedex_number__lte=151), Q.AND)

        # Caught IDs for the current trainer
        caught_ids = set()
        try:
            from myPokemonApp.gameUtils import get_or_create_player_trainer
            trainer   = get_or_create_player_trainer(self.request.user)
            caught_ids = set(
                trainer.pokemon_team.values_list('species_id', flat=True)
            )
        except Exception:
            pass

        # Filter by caught status
        if caught_filter == 'caught' and caught_ids:
            pokemon_filter.add(Q(id__in=caught_ids), Q.AND)
        elif caught_filter == 'missing':
            pokemon_filter.add(~Q(id__in=caught_ids), Q.AND)

        # Pagination
        queryset    = Pokemon.objects.filter(pokemon_filter).distinct().order_by('pokedex_number')
        paginator   = Paginator(queryset, 20)
        page_number = self.request.GET.get('page', 1)
        page_objects = paginator.get_page(page_number)

        # Table — pass caught_ids into template context used by TemplateColumn
        table = self.PokedexTable(page_objects)
        # Make caught_ids available to the table's TemplateColumn via extra context
        # django_tables2 TemplateColumns have access to the table's context
        table.context = {'caught_ids': caught_ids}

        # Types pour le filtre
        types = PokemonType.objects.all().order_by('name')

        context.update({
            'table':        table,
            'pageObjects':  page_objects,
            'searchQuery':  search_query,
            'typeFilter':   type_filter,
            'genFilter':    gen_filter,
            'caughtFilter': caught_filter,
            'types':        types,
            'total_count':  Pokemon.objects.count(),
            'total_caught': len(caught_ids),
            'caught_ids':   caught_ids,
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

        evolutions_from = pokemon.evolutions_from.all()
        evolutions_to   = pokemon.evolutions_to.all()
        learnable_moves = pokemon.learnable_moves.all().order_by('level_learned')

        total_stats = (pokemon.base_hp + pokemon.base_attack + pokemon.base_defense +
                       pokemon.base_special_attack + pokemon.base_special_defense +
                       pokemon.base_speed)

        context.update({
            'evolutions_from': evolutions_from,
            'evolutions_to':   evolutions_to,
            'learnable_moves': learnable_moves,
            'total_stats':     total_stats,
        })

        return context