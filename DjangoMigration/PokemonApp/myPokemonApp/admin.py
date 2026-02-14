#!/usr/bin/python3
"""
Configuration de l'interface d'administration Django
pour l'application Pokémon
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import *


# ============================================================================
# CONFIGURATION GLOBALE DE L'ADMIN
# ============================================================================

# Personnalisation du titre de l'admin
admin.site.site_header = "Administration Pokémon Gen 1"
admin.site.site_title = "Admin Pokémon"
admin.site.index_title = "Gestion de l'application Pokémon"


# ============================================================================
# INLINE ADMIN CLASSES
# ============================================================================

class PokemonEvolutionInline(admin.TabularInline):
    """Évolutions dans l'admin Pokémon"""
    model = PokemonEvolution
    fk_name = 'pokemon'
    extra = 0
    fields = ('evolves_to', 'method', 'level', 'required_item')


class PokemonLearnableMoveInline(admin.TabularInline):
    """Capacités apprises dans l'admin Pokémon"""
    model = PokemonLearnableMove
    extra = 0
    fields = ('move', 'level_learned')
    ordering = ('level_learned',)


class PokemonMoveInstanceInline(admin.TabularInline):
    """Capacités d'un Pokémon jouable"""
    model = PokemonMoveInstance
    extra = 0
    max_num = 4
    fields = ('move', 'current_pp', 'max_pp_display')
    readonly_fields = ('max_pp_display',)
    
    def max_pp_display(self, obj):
        return obj.move.pp if obj.move else '-'
    max_pp_display.short_description = 'PP Max'


class TrainerInventoryInline(admin.TabularInline):
    """Inventaire dans l'admin Trainer"""
    model = TrainerInventory
    extra = 0
    fields = ('item', 'quantity')


class PlayablePokemonInline(admin.TabularInline):
    """Pokémon dans l'admin Trainer"""
    model = PlayablePokemon
    extra = 0
    fields = ('species', 'nickname', 'level', 'current_hp', 'max_hp', 'is_in_party')
    readonly_fields = ('max_hp',)
    show_change_link = True


# ============================================================================
# ADMIN CLASSES - TYPES ET POKÉMON DE BASE
# ============================================================================

@admin.register(PokemonType)
class PokemonTypeAdmin(admin.ModelAdmin):
    """Administration des types Pokémon"""
    list_display = ('name', 'strong_against_list')
    search_fields = ('name',)
    filter_horizontal = ('strong_against',)
    
    def strong_against_list(self, obj):
        """Affiche les types contre lesquels ce type est fort"""
        types = obj.strong_against.all()[:5]
        if types:
            return ', '.join([t.name for t in types])
        return '-'
    strong_against_list.short_description = 'Fort contre'


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    """Administration des Pokémon (templates)"""
    list_display = (
        'pokedex_number', 
        'name', 
        'primary_type', 
        'secondary_type',
        'total_stats',
        'catch_rate',
        'base_experience'
    )
    list_filter = ('primary_type', 'secondary_type')
    search_fields = ('name', 'pokedex_number')
    ordering = ('pokedex_number',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'pokedex_number', 'primary_type', 'secondary_type', 'sprite_url')
        }),
        ('Stats de base', {
            'fields': (
                ('base_hp', 'base_attack', 'base_defense'),
                ('base_special_attack', 'base_special_defense', 'base_speed')
            )
        }),
        ('Méta-données', {
            'fields': ('catch_rate', 'base_experience', 'growth_rate')
        })
    )
    
    inlines = [PokemonEvolutionInline, PokemonLearnableMoveInline]
    
    def total_stats(self, obj):
        """Calcule le total des stats de base"""
        total = (obj.base_hp + obj.base_attack + obj.base_defense + 
                obj.base_special_attack + obj.base_special_defense + obj.base_speed)
        return total
    total_stats.short_description = 'Total Stats'


@admin.register(PokemonMove)
class PokemonMoveAdmin(admin.ModelAdmin):
    """Administration des capacités"""
    list_display = (
        'name', 
        'type', 
        'category', 
        'power', 
        'accuracy', 
        'pp',
        'priority',
        'status_effect'
    )
    list_filter = ('type', 'category', 'inflicts_status')
    search_fields = ('name',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'type', 'category')
        }),
        ('Caractéristiques', {
            'fields': (
                ('power', 'accuracy'),
                ('pp', 'max_pp', 'priority')
            )
        }),
        ('Effets', {
            'fields': ('effect', 'effect_chance', 'inflicts_status', 'stat_changes')
        })
    )
    
    def status_effect(self, obj):
        """Affiche l'effet de statut si présent"""
        if obj.inflicts_status:
            return f"{obj.inflicts_status} ({obj.effect_chance}%)"
        return '-'
    status_effect.short_description = 'Effet de statut'


@admin.register(PokemonEvolution)
class PokemonEvolutionAdmin(admin.ModelAdmin):
    """Administration des évolutions"""
    list_display = ('pokemon', 'evolves_to', 'method', 'level', 'required_item')
    list_filter = ('method',)
    search_fields = ('pokemon__name', 'evolves_to__name')


@admin.register(PokemonLearnableMove)
class PokemonLearnableMoveAdmin(admin.ModelAdmin):
    """Administration des capacités apprises"""
    list_display = ('pokemon', 'move', 'level_learned')
    list_filter = ('level_learned',)
    search_fields = ('pokemon__name', 'move__name')
    ordering = ('pokemon__pokedex_number', 'level_learned')


# ============================================================================
# ADMIN CLASSES - POKÉMON JOUABLES
# ============================================================================

@admin.register(PlayablePokemon)
class PlayablePokemonAdmin(admin.ModelAdmin):
    """Administration des Pokémon jouables"""
    list_display = (
        'display_name',
        'species',
        'trainer',
        'level',
        'hp_display',
        'status_condition',
        'is_in_party'
    )
    list_filter = (
        'trainer__trainer_type',
        'species__primary_type',
        'is_in_party',
        'status_condition'
    )
    search_fields = ('nickname', 'species__name', 'trainer__username')
    
    fieldsets = (
        ('Informations de base', {
            'fields': (
                'species',
                'trainer',
                'nickname',
                'original_trainer',
                'caught_location',
                'pokeball_used'
            )
        }),
        ('Niveau et Expérience', {
            'fields': (
                ('level', 'current_exp'),
                'friendship'
            )
        }),
        ('Stats actuelles', {
            'fields': (
                ('current_hp', 'max_hp'),
                ('attack', 'defense'),
                ('special_attack', 'special_defense'),
                'speed'
            )
        }),
        ('IVs (Individual Values)', {
            'fields': (
                ('iv_hp', 'iv_attack', 'iv_defense'),
                ('iv_special_attack', 'iv_special_defense', 'iv_speed')
            ),
            'classes': ('collapse',)
        }),
        ('EVs (Effort Values)', {
            'fields': (
                ('ev_hp', 'ev_attack', 'ev_defense'),
                ('ev_special_attack', 'ev_special_defense', 'ev_speed')
            ),
            'classes': ('collapse',)
        }),
        ('Combat', {
            'fields': (
                'nature',
                'status_condition',
                'sleep_turns',
                ('attack_stage', 'defense_stage'),
                ('special_attack_stage', 'special_defense_stage'),
                ('speed_stage', 'accuracy_stage', 'evasion_stage')
            ),
            'classes': ('collapse',)
        }),
        ('Équipe', {
            'fields': (
                'is_in_party',
                'party_position',
                'held_item'
            )
        })
    )
    
    inlines = [PokemonMoveInstanceInline]
    
    readonly_fields = ('max_hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed')
    
    def display_name(self, obj):
        """Affiche le surnom ou le nom de l'espèce"""
        return obj.nickname or obj.species.name
    display_name.short_description = 'Nom'
    
    def hp_display(self, obj):
        """Affiche les HP avec une barre de couleur"""
        percentage = (obj.current_hp / obj.max_hp * 100) if obj.max_hp > 0 else 0
        
        if percentage > 50:
            color = 'green'
        elif percentage > 20:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{}/{} HP ({}%)</span>',
            color,
            obj.current_hp,
            obj.max_hp,
            int(percentage)
        )
    hp_display.short_description = 'HP'
    
    actions = ['heal_pokemon', 'reset_stages', 'level_up_action']
    
    def heal_pokemon(self, request, queryset):
        """Action pour soigner les Pokémon sélectionnés"""
        for pokemon in queryset:
            pokemon.heal()
            # Restaurer aussi les PP
            for move_instance in PokemonMoveInstance.objects.filter(pokemon=pokemon):
                move_instance.restore_pp()
        self.message_user(request, f"{queryset.count()} Pokémon soignés.")
    heal_pokemon.short_description = "Soigner les Pokémon sélectionnés"
    
    def reset_stages(self, request, queryset):
        """Réinitialise les stages de combat"""
        for pokemon in queryset:
            pokemon.reset_stat_stages()
        self.message_user(request, f"Stages réinitialisés pour {queryset.count()} Pokémon.")
    reset_stages.short_description = "Réinitialiser les stages de combat"
    
    def level_up_action(self, request, queryset):
        """Fait monter les Pokémon d'un niveau"""
        for pokemon in queryset:
            pokemon.level_up()
        self.message_user(request, f"{queryset.count()} Pokémon ont gagné un niveau.")
    level_up_action.short_description = "Faire monter d'un niveau"


@admin.register(PokemonMoveInstance)
class PokemonMoveInstanceAdmin(admin.ModelAdmin):
    """Administration des instances de capacités"""
    list_display = ('pokemon', 'move', 'current_pp', 'max_pp_display')
    search_fields = ('pokemon__species__name', 'move__name')
    
    def max_pp_display(self, obj):
        return obj.move.pp
    max_pp_display.short_description = 'PP Max'


# ============================================================================
# ADMIN CLASSES - DRESSEURS
# ============================================================================

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    """Administration des dresseurs"""
    list_display = (
        'username',
        'trainer_type',
        'money',
        'badges',
        'pokemon_count',
        'location',
        'is_defeated'
    )
    list_filter = ('trainer_type', 'is_defeated', 'can_rebattle')
    search_fields = ('username', 'location')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('username', 'trainer_type', 'location')
        }),
        ('Progression', {
            'fields': ('money', 'badges')
        }),
        ('NPC', {
            'fields': (
                'is_defeated',
                'can_rebattle',
                'intro_text',
                'defeat_text',
                'victory_text'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [PlayablePokemonInline, TrainerInventoryInline]
    
    def pokemon_count(self, obj):
        """Compte le nombre de Pokémon"""
        return obj.pokemon_team.count()
    pokemon_count.short_description = 'Nb. Pokémon'
    
    actions = ['heal_team_action', 'give_starter_money']
    
    def heal_team_action(self, request, queryset):
        """Soigne tous les Pokémon des dresseurs sélectionnés"""
        count = 0
        for trainer in queryset:
            for pokemon in trainer.pokemon_team.all():
                pokemon.heal()
                for move_inst in PokemonMoveInstance.objects.filter(pokemon=pokemon):
                    move_inst.restore_pp()
                count += 1
        self.message_user(request, f"{count} Pokémon soignés pour {queryset.count()} dresseurs.")
    heal_team_action.short_description = "Soigner toutes les équipes"
    
    def give_starter_money(self, request, queryset):
        """Donne 3000₽ aux dresseurs sélectionnés"""
        queryset.update(money=3000)
        self.message_user(request, f"{queryset.count()} dresseurs ont reçu 3000₽.")
    give_starter_money.short_description = "Donner 3000₽"


@admin.register(GymLeader)
class GymLeaderAdmin(admin.ModelAdmin):
    """Administration des Champions d'Arène"""
    list_display = (
        'badge_order',
        'trainer_name',
        'gym_name',
        'gym_city',
        'specialty_type',
        'badge_name'
    )
    list_filter = ('specialty_type',)
    search_fields = ('trainer__username', 'gym_name', 'gym_city')
    ordering = ('badge_order',)
    
    fieldsets = (
        ('Dresseur', {
            'fields': ('trainer',)
        }),
        ('Arène', {
            'fields': (
                'gym_name',
                'gym_city',
                'badge_name',
                'badge_order',
                'specialty_type'
            )
        }),
        ('Récompense', {
            'fields': ('tm_reward',)
        })
    )
    
    def trainer_name(self, obj):
        return obj.trainer.username
    trainer_name.short_description = 'Champion'


@admin.register(TrainerInventory)
class TrainerInventoryAdmin(admin.ModelAdmin):
    """Administration des inventaires"""
    list_display = ('trainer', 'item', 'quantity')
    list_filter = ('item__item_type',)
    search_fields = ('trainer__username', 'item__name')


# ============================================================================
# ADMIN CLASSES - OBJETS
# ============================================================================

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Administration des objets"""
    list_display = (
        'name',
        'item_type',
        'price',
        'effect_display',
        'is_consumable'
    )
    list_filter = ('item_type', 'is_consumable')
    search_fields = ('name',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'item_type', 'price', 'is_consumable')
        }),
        ('Effets de soin', {
            'fields': ('heal_amount', 'heal_percentage', 'cures_status', 'specific_status')
        }),
        ('Capture', {
            'fields': ('catch_rate_modifier',)
        }),
        ('Évolution', {
            'fields': ('evolves_pokemon',)
        }),
        ('Objet tenu', {
            'fields': ('held_effect',)
        })
    )
    
    def effect_display(self, obj):
        """Affiche les effets principaux de l'objet"""
        effects = []
        
        if obj.heal_amount > 0:
            effects.append(f"+{obj.heal_amount} HP")
        if obj.heal_percentage > 0:
            effects.append(f"+{obj.heal_percentage}% HP")
        if obj.cures_status:
            if obj.specific_status:
                effects.append(f"Soigne {obj.specific_status}")
            else:
                effects.append("Soigne tous statuts")
        if obj.catch_rate_modifier != 1.0:
            effects.append(f"Capture x{obj.catch_rate_modifier}")
        
        return ', '.join(effects) if effects else '-'
    effect_display.short_description = 'Effets'


# ============================================================================
# ADMIN CLASSES - COMBATS
# ============================================================================

@admin.register(Battle)
class BattleAdmin(admin.ModelAdmin):
    """Administration des combats"""
    list_display = (
        'id',
        'battle_type',
        'player_trainer',
        'opponent_trainer',
        'is_active',
        'current_turn',
        'winner',
        'created_at'
    )
    list_filter = ('battle_type', 'is_active', 'created_at')
    search_fields = ('player_trainer__username', 'opponent_trainer__username')
    readonly_fields = ('created_at', 'ended_at', 'battle_log')
    
    fieldsets = (
        ('Participants', {
            'fields': (
                'battle_type',
                'player_trainer',
                'opponent_trainer',
                'player_pokemon',
                'opponent_pokemon'
            )
        }),
        ('État du combat', {
            'fields': (
                'is_active',
                'current_turn',
                'winner',
                'weather',
                'terrain'
            )
        }),
        ('Historique', {
            'fields': ('battle_log', 'created_at', 'ended_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['end_battle_action']
    
    def end_battle_action(self, request, queryset):
        """Termine les combats sélectionnés"""
        for battle in queryset:
            if battle.is_active:
                battle.end_battle(battle.player_trainer)
        self.message_user(request, f"{queryset.count()} combats terminés.")
    end_battle_action.short_description = "Terminer les combats"


