#!/usr/bin/python3
"""
Configuration de l'interface d'administration Django
pour l'application Pokémon — tous les modèles enregistrés.
"""

from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import *


# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

admin.site.site_header = "Administration Pokémon Gen 1"
admin.site.site_title  = "Admin Pokémon"
admin.site.index_title = "Gestion de l'application Pokémon"


# ============================================================================
# BASE — Suppression des messages INFO parasites
# ============================================================================

class QuietModelAdmin(admin.ModelAdmin):
    """
    Supprime les messages de succès Django par défaut (ajout/modif/suppression).
    Conserve les erreurs et les messages explicites des actions personnalisées.
    """
    def message_user(self, request, message, level=messages.INFO,
                     extra_tags='', fail_silently=False):
        if level == messages.INFO:
            return
        super().message_user(request, message, level, extra_tags, fail_silently)

    def notify(self, request, msg):
        """Afficher un message de succès depuis une action custom."""
        super().message_user(request, msg, messages.SUCCESS)


# ============================================================================
# INLINES
# ============================================================================

class PokemonEvolutionInline(admin.TabularInline):
    model   = PokemonEvolution
    fk_name = 'pokemon'
    extra   = 0
    fields  = ('evolves_to', 'method', 'level', 'required_item')


class PokemonLearnableMoveInline(admin.TabularInline):
    model    = PokemonLearnableMove
    extra    = 0
    fields   = ('move', 'level_learned')
    ordering = ('level_learned',)


class PokemonMoveInstanceInline(admin.TabularInline):
    model           = PokemonMoveInstance
    extra           = 0
    max_num         = 4
    fields          = ('move', 'current_pp', 'max_pp_display')
    readonly_fields = ('max_pp_display',)

    def max_pp_display(self, obj):
        return obj.move.pp if obj.move else '-'
    max_pp_display.short_description = 'PP Max'


class TrainerInventoryInline(admin.TabularInline):
    model  = TrainerInventory
    extra  = 0
    fields = ('item', 'quantity')


class PlayablePokemonInline(admin.TabularInline):
    model            = PlayablePokemon
    extra            = 0
    fields           = ('species', 'nickname', 'level', 'current_hp', 'max_hp', 'is_in_party', 'party_position')
    readonly_fields  = ('max_hp',)
    show_change_link = True


class ShopInventoryInline(admin.TabularInline):
    model  = ShopInventory
    extra  = 0
    fields = ('item', 'price_override', 'stock', 'is_available')


class WildPokemonSpawnInline(admin.TabularInline):
    model   = WildPokemonSpawn
    extra   = 0
    fields  = ('pokemon', 'level_min', 'level_max', 'spawn_rate', 'encounter_type')
    ordering = ('-spawn_rate',)


# ============================================================================
# TYPES ET POKÉMON DE BASE
# ============================================================================

@admin.register(PokemonType)
class PokemonTypeAdmin(QuietModelAdmin):
    list_display      = ('name', 'strong_against_list')
    search_fields     = ('name',)
    filter_horizontal = ('strong_against',)

    def strong_against_list(self, obj):
        types = obj.strong_against.all()[:5]
        return ', '.join(t.name for t in types) if types else '-'
    strong_against_list.short_description = 'Fort contre'


@admin.register(Pokemon)
class PokemonAdmin(QuietModelAdmin):
    list_display = ('pokedex_number', 'name', 'primary_type', 'secondary_type', 'total_stats', 'catch_rate', 'base_experience')
    list_filter  = ('primary_type', 'secondary_type')
    search_fields = ('name', 'pokedex_number')
    ordering     = ('pokedex_number',)
    inlines      = [PokemonEvolutionInline, PokemonLearnableMoveInline]

    fieldsets = (
        ('Informations', {'fields': ('name', 'pokedex_number', 'primary_type', 'secondary_type', 'sprite_url')}),
        ('Stats de base', {'fields': (('base_hp', 'base_attack', 'base_defense'), ('base_special_attack', 'base_special_defense', 'base_speed'))}),
        ('Méta', {'fields': ('catch_rate', 'base_experience', 'growth_rate')}),
    )

    def total_stats(self, obj):
        return (obj.base_hp + obj.base_attack + obj.base_defense +
                obj.base_special_attack + obj.base_special_defense + obj.base_speed)
    total_stats.short_description = 'Total'


@admin.register(PokemonMove)
class PokemonMoveAdmin(QuietModelAdmin):
    list_display  = ('name', 'type', 'category', 'power', 'accuracy', 'pp', 'priority', 'status_effect')
    list_filter   = ('type', 'category', 'inflicts_status')
    search_fields = ('name',)

    fieldsets = (
        ('Base',   {'fields': ('name', 'type', 'category')}),
        ('Stats',  {'fields': (('power', 'accuracy'), ('pp', 'max_pp', 'priority'))}),
        ('Effets', {'fields': ('effect', 'effect_chance', 'inflicts_status', 'stat_changes')}),
    )

    def status_effect(self, obj):
        return f"{obj.inflicts_status} ({obj.effect_chance}%)" if obj.inflicts_status else '-'
    status_effect.short_description = 'Effet'


@admin.register(PokemonEvolution)
class PokemonEvolutionAdmin(QuietModelAdmin):
    list_display  = ('pokemon', 'evolves_to', 'method', 'level', 'required_item')
    list_filter   = ('method',)
    search_fields = ('pokemon__name', 'evolves_to__name')


@admin.register(PokemonLearnableMove)
class PokemonLearnableMoveAdmin(QuietModelAdmin):
    list_display  = ('pokemon', 'move', 'level_learned')
    list_filter   = ('level_learned',)
    search_fields = ('pokemon__name', 'move__name')
    ordering      = ('pokemon__pokedex_number', 'level_learned')


# ============================================================================
# POKÉMON JOUABLES
# ============================================================================

@admin.register(PlayablePokemon)
class PlayablePokemonAdmin(QuietModelAdmin):
    list_display    = ('display_name', 'species', 'trainer', 'level', 'hp_display', 'status_condition', 'is_in_party', 'party_position')
    list_filter     = ('is_in_party', 'status_condition', 'species__primary_type', 'trainer__trainer_type')
    search_fields   = ('nickname', 'species__name', 'trainer__username')
    readonly_fields = ('max_hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed')
    inlines         = [PokemonMoveInstanceInline]

    fieldsets = (
        ('Identité', {'fields': ('species', 'trainer', 'nickname', 'original_trainer', 'caught_location', 'pokeball_used')}),
        ('Niveau',   {'fields': (('level', 'current_exp'), 'friendship')}),
        ('Stats',    {'fields': (('current_hp', 'max_hp'), ('attack', 'defense'), ('special_attack', 'special_defense'), 'speed')}),
        ('IVs',      {'fields': (('iv_hp', 'iv_attack', 'iv_defense'), ('iv_special_attack', 'iv_special_defense', 'iv_speed')), 'classes': ('collapse',)}),
        ('EVs',      {'fields': (('ev_hp', 'ev_attack', 'ev_defense'), ('ev_special_attack', 'ev_special_defense', 'ev_speed')), 'classes': ('collapse',)}),
        ('Combat',   {'fields': ('nature', 'status_condition', 'sleep_turns', ('attack_stage', 'defense_stage'), ('special_attack_stage', 'special_defense_stage'), ('speed_stage', 'accuracy_stage', 'evasion_stage')), 'classes': ('collapse',)}),
        ('Équipe',   {'fields': ('is_in_party', 'party_position', 'held_item')}),
    )

    actions = ['heal_pokemon', 'reset_stages', 'level_up_action']

    def display_name(self, obj):
        return obj.nickname or obj.species.name
    display_name.short_description = 'Nom'

    def hp_display(self, obj):
        pct   = (obj.current_hp / obj.max_hp * 100) if obj.max_hp > 0 else 0
        color = '#28a745' if pct > 50 else ('#ffc107' if pct > 20 else '#dc3545')
        return format_html('<span style="color:{};">{}/{} ({}%)</span>', color, obj.current_hp, obj.max_hp, int(pct))
    hp_display.short_description = 'HP'

    def heal_pokemon(self, request, queryset):
        for p in queryset:
            p.heal()
            for mi in PokemonMoveInstance.objects.filter(pokemon=p):
                mi.restore_pp()
        self.notify(request, f"{queryset.count()} Pokémon soignés.")
    heal_pokemon.short_description = "Soigner les Pokémon sélectionnés"

    def reset_stages(self, request, queryset):
        for p in queryset:
            p.reset_stat_stages()
        self.notify(request, f"Stages réinitialisés pour {queryset.count()} Pokémon.")
    reset_stages.short_description = "Réinitialiser les stages"

    def level_up_action(self, request, queryset):
        for p in queryset:
            p.level_up()
        self.notify(request, f"{queryset.count()} Pokémon ont gagné un niveau.")
    level_up_action.short_description = "Faire monter d'un niveau"


@admin.register(PokemonMoveInstance)
class PokemonMoveInstanceAdmin(QuietModelAdmin):
    list_display  = ('pokemon', 'move', 'current_pp', 'max_pp_display')
    search_fields = ('pokemon__species__name', 'move__name')

    def max_pp_display(self, obj):
        return obj.move.pp
    max_pp_display.short_description = 'PP Max'


# ============================================================================
# DRESSEURS
# ============================================================================

@admin.register(Trainer)
class TrainerAdmin(QuietModelAdmin):
    list_display  = ('username', 'trainer_type', 'npc_class', 'money', 'badges', 'pokemon_count', 'location', 'is_npc')
    list_filter   = ('trainer_type', 'is_npc', 'is_defeated', 'can_rebattle')
    search_fields = ('username', 'location', 'npc_class')
    inlines       = [PlayablePokemonInline, TrainerInventoryInline]

    fieldsets = (
        ('Identité',    {'fields': ('username', 'trainer_type', 'location', 'sprite_name')}),
        ('Progression', {'fields': ('money', 'badges')}),
        ('NPC', {'fields': ('is_npc', 'npc_class', 'is_defeated', 'can_rebattle', 'intro_text', 'defeat_text', 'victory_text'), 'classes': ('collapse',)}),
    )

    actions = ['heal_team_action', 'give_starter_money']

    def pokemon_count(self, obj):
        return obj.pokemon_team.count()
    pokemon_count.short_description = 'Pokémon'

    def heal_team_action(self, request, queryset):
        count = 0
        for trainer in queryset:
            for p in trainer.pokemon_team.all():
                p.heal()
                for mi in PokemonMoveInstance.objects.filter(pokemon=p):
                    mi.restore_pp()
                count += 1
        self.notify(request, f"{count} Pokémon soignés pour {queryset.count()} dresseurs.")
    heal_team_action.short_description = "Soigner toutes les équipes"

    def give_starter_money(self, request, queryset):
        queryset.update(money=3000)
        self.notify(request, f"{queryset.count()} dresseurs ont reçu 3 000₽.")
    give_starter_money.short_description = "Donner 3 000₽"


@admin.register(GymLeader)
class GymLeaderAdmin(QuietModelAdmin):
    list_display  = ('badge_order', 'trainer_name', 'gym_name', 'gym_city', 'specialty_type', 'badge_name')
    list_filter   = ('specialty_type',)
    search_fields = ('trainer__username', 'gym_name', 'gym_city')
    ordering      = ('badge_order',)

    fieldsets = (
        ('Dresseur',   {'fields': ('trainer',)}),
        ('Arène',      {'fields': ('gym_name', 'gym_city', 'badge_name', 'badge_order', 'specialty_type')}),
        ('Récompense', {'fields': ('tm_reward',)}),
    )

    def trainer_name(self, obj):
        return obj.trainer.username
    trainer_name.short_description = 'Champion'


@admin.register(TrainerInventory)
class TrainerInventoryAdmin(QuietModelAdmin):
    list_display  = ('trainer', 'item', 'quantity')
    list_filter   = ('item__item_type',)
    search_fields = ('trainer__username', 'item__name')


# ============================================================================
# OBJETS
# ============================================================================

@admin.register(Item)
class ItemAdmin(QuietModelAdmin):
    list_display  = ('name', 'item_type', 'price', 'effect_display', 'is_consumable')
    list_filter   = ('item_type', 'is_consumable')
    search_fields = ('name',)

    fieldsets = (
        ('Base',      {'fields': ('name', 'description', 'item_type', 'price', 'is_consumable')}),
        ('Soin',      {'fields': ('heal_amount', 'heal_percentage', 'cures_status', 'specific_status')}),
        ('Capture',   {'fields': ('catch_rate_modifier',)}),
        ('Évolution', {'fields': ('evolves_pokemon',)}),
        ('Objet tenu',{'fields': ('held_effect',)}),
    )

    def effect_display(self, obj):
        effects = []
        if obj.heal_amount > 0:     effects.append(f"+{obj.heal_amount} HP")
        if obj.heal_percentage > 0: effects.append(f"+{obj.heal_percentage}% HP")
        if obj.cures_status:        effects.append(f"Soigne {obj.specific_status or 'tous statuts'}")
        if obj.catch_rate_modifier != 1.0: effects.append(f"Capture x{obj.catch_rate_modifier}")
        return ', '.join(effects) or '-'
    effect_display.short_description = 'Effets'


@admin.register(PokeballItem)
class PokeballItemAdmin(QuietModelAdmin):
    list_display  = ('item', 'guaranteed_capture', 'bonus_on_type', 'bonus_on_status')
    search_fields = ('item__name',)


# ============================================================================
# COMBATS
# ============================================================================

@admin.register(Battle)
class BattleAdmin(QuietModelAdmin):
    list_display    = ('id', 'battle_type', 'player_trainer', 'opponent_trainer', 'is_active', 'current_turn', 'winner', 'created_at')
    list_filter     = ('battle_type', 'is_active', 'created_at')
    search_fields   = ('player_trainer__username', 'opponent_trainer__username')
    readonly_fields = ('created_at', 'ended_at', 'battle_log')

    fieldsets = (
        ('Participants', {'fields': ('battle_type', 'player_trainer', 'opponent_trainer', 'player_pokemon', 'opponent_pokemon')}),
        ('État',         {'fields': ('is_active', 'current_turn', 'winner', 'weather', 'terrain')}),
        ('Journal',      {'fields': ('battle_log', 'created_at', 'ended_at'), 'classes': ('collapse',)}),
    )

    actions = ['end_battles']

    def end_battles(self, request, queryset):
        count = sum(
            1 for battle in queryset.filter(is_active=True)
            if not battle.end_battle(battle.player_trainer) or True
        )
        self.notify(request, f"{count} combat(s) terminé(s).")
    end_battles.short_description = "Terminer les combats actifs"


# ============================================================================
# CAPTURE
# ============================================================================

@admin.register(CaptureAttempt)
class CaptureAttemptAdmin(QuietModelAdmin):
    list_display    = ('trainer', 'pokemon_species', 'ball_used', 'pokemon_level', 'success', 'capture_rate', 'shakes')
    list_filter     = ('success',)
    search_fields   = ('trainer__username', 'pokemon_species__name')
    readonly_fields = ('trainer', 'pokemon_species', 'ball_used', 'pokemon_level',
                       'pokemon_hp_percent', 'pokemon_status', 'success', 'capture_rate', 'shakes')


@admin.register(CaptureJournal)
class CaptureJournalAdmin(QuietModelAdmin):
    list_display    = ('trainer', 'pokemon', 'ball_used', 'level_at_capture', 'location', 'is_first_catch', 'captured_at')
    list_filter     = ('is_first_catch', 'is_shiny', 'is_critical_catch')
    search_fields   = ('trainer__username', 'pokemon__species__name')
    readonly_fields = ('captured_at',)


# ============================================================================
# SAUVEGARDE & HISTORIQUE
# ============================================================================

@admin.register(GameSave)
class GameSaveAdmin(QuietModelAdmin):
    list_display    = ('trainer', 'save_name', 'slot', 'current_location', 'play_time_display', 'is_active', 'last_saved')
    list_filter     = ('is_active', 'slot')
    search_fields   = ('trainer__username', 'save_name', 'current_location')
    readonly_fields = ('created_at', 'last_saved')

    def play_time_display(self, obj):
        return obj.get_play_time_display()
    play_time_display.short_description = 'Temps de jeu'


@admin.register(TrainerBattleHistory)
class TrainerBattleHistoryAdmin(QuietModelAdmin):
    list_display    = ('player', 'opponent', 'player_won', 'money_earned', 'battle')
    list_filter     = ('player_won',)
    search_fields   = ('player__username', 'opponent__username')
    readonly_fields = ('player', 'opponent', 'player_won', 'battle', 'money_earned')


# ============================================================================
# BOUTIQUES & TRANSACTIONS
# ============================================================================

@admin.register(Shop)
class ShopAdmin(QuietModelAdmin):
    list_display  = ('name', 'shop_type', 'location')
    list_filter   = ('shop_type',)
    search_fields = ('name', 'location')
    inlines       = [ShopInventoryInline]


@admin.register(ShopInventory)
class ShopInventoryAdmin(QuietModelAdmin):
    list_display  = ('shop', 'item', 'get_final_price', 'stock', 'unlock_badge_required')
    list_filter   = ('shop', 'unlock_badge_required')
    search_fields = ('shop__name', 'item__name')


@admin.register(Transaction)
class TransactionAdmin(QuietModelAdmin):
    list_display    = ('trainer', 'item', 'quantity', 'total_price', 'transaction_type', 'created_at')
    list_filter     = ('transaction_type', 'created_at')
    search_fields   = ('trainer__username', 'item__name')
    readonly_fields = ('created_at',)


# ============================================================================
# ZONES & CARTE
# ============================================================================

@admin.register(Zone)
class ZoneAdmin(QuietModelAdmin):
    list_display  = ('name', 'zone_type', 'recommended_level_min', 'recommended_level_max', 'has_pokemon_center', 'has_shop', 'is_safe_zone')
    list_filter   = ('zone_type', 'has_pokemon_center', 'has_shop', 'is_safe_zone')
    search_fields = ('name',)
    inlines       = [WildPokemonSpawnInline]


@admin.register(ZoneConnection)
class ZoneConnectionAdmin(QuietModelAdmin):
    list_display  = ('from_zone', 'to_zone', 'is_bidirectional')
    list_filter   = ('is_bidirectional',)
    search_fields = ('from_zone__name', 'to_zone__name')


@admin.register(WildPokemonSpawn)
class WildPokemonSpawnAdmin(QuietModelAdmin):
    list_display  = ('zone', 'pokemon', 'level_min', 'level_max', 'spawn_rate', 'encounter_type')
    list_filter   = ('zone', 'encounter_type')
    search_fields = ('zone__name', 'pokemon__name')
    ordering      = ('zone', '-spawn_rate')


@admin.register(PlayerLocation)
class PlayerLocationAdmin(QuietModelAdmin):
    list_display      = ('trainer', 'current_zone', 'last_pokemon_center', 'updated_at')
    search_fields     = ('trainer__username', 'current_zone__name')
    readonly_fields   = ('updated_at',)
    filter_horizontal = ('visited_zones',)


# ============================================================================
# CENTRES POKÉMON
# ============================================================================

@admin.register(PokemonCenter)
class PokemonCenterAdmin(QuietModelAdmin):
    list_display  = ('name', 'location', 'nurse_name', 'heals_count')
    search_fields = ('name', 'location', 'nurse_name')

    def heals_count(self, obj):
        return obj.visits.count()
    heals_count.short_description = 'Visites'


@admin.register(CenterVisit)
class CenterVisitAdmin(QuietModelAdmin):
    list_display    = ('trainer', 'center', 'visited_at')
    list_filter     = ('center',)
    search_fields   = ('trainer__username',)
    readonly_fields = ('visited_at',)


@admin.register(NurseDialogue)
class NurseDialogueAdmin(QuietModelAdmin):
    list_display  = ('center', 'dialogue_type', 'dialogue_short')
    list_filter   = ('center', 'dialogue_type')
    search_fields = ('center__name',)

    def dialogue_short(self, obj):
        t = obj.text
        return (t[:60] + '…') if len(t) > 60 else t
    dialogue_short.short_description = 'Dialogue'


# ============================================================================
# ACHIEVEMENTS
# ============================================================================

@admin.register(Achievement)
class AchievementAdmin(QuietModelAdmin):
    list_display  = ('name', 'category', 'required_value', 'reward_money')
    list_filter   = ('category',)
    search_fields = ('name',)


@admin.register(TrainerAchievement)
class TrainerAchievementAdmin(QuietModelAdmin):
    list_display    = ('trainer', 'achievement', 'completed_at', 'current_progress')
    list_filter     = ('achievement__category',)
    search_fields   = ('trainer__username', 'achievement__name')
    readonly_fields = ('completed_at',)