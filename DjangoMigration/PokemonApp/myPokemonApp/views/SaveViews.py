"""
Système de sauvegarde COMPLET avec snapshot v1.1
=================================================

Changements v1.0 → v1.1 :
  - create_game_snapshot() inclut désormais 'achievements' et 'quests'
    (pour référence / export — la source de vérité reste la DB)
  - restore_game_snapshot() restaure achievements et quests depuis le snapshot
  - Pas de régression sur le reste
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
import logging
import json

from myPokemonApp.models import *
from myPokemonApp.models.Achievements import Achievement, TrainerAchievement
from myPokemonApp.models.Quest import Quest, QuestProgress
from myPokemonApp.gameUtils import get_player_trainer


# ============================================================================
# SNAPSHOT — Sauvegarder l'état complet
# ============================================================================

def create_game_snapshot(trainer, save):
    """
    Crée un snapshot complet de l'état du jeu (version 1.1).

    Inclut : trainer, pokémon, inventaire, defeated_trainers,
             story_flags, achievements, quêtes.

    Returns:
        dict JSON-serializable
    """
    snapshot = {
        'version':    '1.1',
        'created_at': timezone.now().isoformat(),

        'trainer': {
            'money':    trainer.money,
            'badges':   trainer.badges,
            'location': save.current_location,
        },

        'pokemon_team':      [],
        'inventory':         [],
        'defeated_trainers': list(save.defeated_trainers),
        'story_flags':       dict(save.story_flags),
        'achievements':      [],   # NOUVEAU v1.1
        'quests':            [],   # NOUVEAU v1.1
    }

    # ── Pokémon ───────────────────────────────────────────────────────────
    for pokemon in trainer.pokemon_team.all():
        pdata = {
            'species_id':        pokemon.species.id,
            'species_name':      pokemon.species.name,
            'nickname':          pokemon.nickname,
            'level':             pokemon.level,
            'current_hp':        pokemon.current_hp,
            'max_hp':            pokemon.max_hp,
            'attack':            pokemon.attack,
            'defense':           pokemon.defense,
            'special_attack':    pokemon.special_attack,
            'special_defense':   pokemon.special_defense,
            'speed':             pokemon.speed,
            'status_condition':  pokemon.status_condition,
            'is_in_party':       pokemon.is_in_party,
            'current_exp':       pokemon.current_exp,
            'exp_for_next_level': pokemon.exp_for_next_level(),
            # ── IVs ──────────────────────────────────────────────────────
            'iv_hp':             pokemon.iv_hp,
            'iv_attack':         pokemon.iv_attack,
            'iv_defense':        pokemon.iv_defense,
            'iv_special_attack': pokemon.iv_special_attack,
            'iv_special_defense':pokemon.iv_special_defense,
            'iv_speed':          pokemon.iv_speed,
            # ── EVs ──────────────────────────────────────────────────────
            'ev_hp':             pokemon.ev_hp,
            'ev_attack':         pokemon.ev_attack,
            'ev_defense':        pokemon.ev_defense,
            'ev_special_attack': pokemon.ev_special_attack,
            'ev_special_defense':pokemon.ev_special_defense,
            'ev_speed':          pokemon.ev_speed,
            # ── Misc ─────────────────────────────────────────────────────
            'nature':            pokemon.nature,
            'is_shiny':          pokemon.is_shiny,
            'party_position':    pokemon.party_position,
            'original_trainer':  pokemon.original_trainer,
            'pokeball_used':     pokemon.pokeball_used,
            'friendship':        pokemon.friendship,
            'moves':             [],
        }
        for mi in pokemon.pokemonmoveinstance_set.all():
            pdata['moves'].append({
                'move_id':    mi.move.id,
                'move_name':  mi.move.name,
                'current_pp': mi.current_pp,
            })
        snapshot['pokemon_team'].append(pdata)

    # ── Inventaire ────────────────────────────────────────────────────────
    for inv in trainer.inventory.all():
        snapshot['inventory'].append({
            'item_id':   inv.item.id,
            'item_name': inv.item.name,
            'quantity':  inv.quantity,
        })

    # ── Achievements ──────────────────────────────────────────────────────
    for ta in (
        TrainerAchievement.objects
        .filter(trainer=trainer)
        .select_related('achievement')
    ):
        snapshot['achievements'].append({
            'achievement_name': ta.achievement.name,
            'current_progress': ta.current_progress,
            'is_completed':     ta.is_completed,
            'completed_at':     ta.completed_at.isoformat() if ta.completed_at else None,
        })

    # ── Quêtes ────────────────────────────────────────────────────────────
    for qp in (
        QuestProgress.objects
        .filter(trainer=trainer)
        .select_related('quest')
    ):
        snapshot['quests'].append({
            'quest_id':     qp.quest.quest_id,
            'state':        qp.state,
            'data':         dict(qp.data),
            'started_at':   qp.started_at.isoformat()   if qp.started_at   else None,
            'completed_at': qp.completed_at.isoformat() if qp.completed_at else None,
        })

    return snapshot


# ============================================================================
# RESTORE — Restaurer l'état complet
# ============================================================================

def restore_game_snapshot(trainer, snapshot):
    """
    Restaure l'état complet du jeu depuis un snapshot.
    Gère v1.0 (sans achievements/quests) et v1.1.
    """
    # ── Trainer ───────────────────────────────────────────────────────────
    trainer.money  = snapshot['trainer']['money']
    trainer.badges = snapshot['trainer']['badges']
    trainer.save()

    # ── GameSave : story_flags + defeated_trainers ────────────────────────
    # Ces deux champs vivent sur GameSave, pas sur Trainer.
    # On met à jour l'objet actif en DB.
    save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
    if save:
        save.story_flags      = dict(snapshot.get('story_flags', {}))
        save.defeated_trainers = list(snapshot.get('defeated_trainers', []))
        save.save(update_fields=['story_flags', 'defeated_trainers'])

    # ── Pokémon ───────────────────────────────────────────────────────────
    trainer.pokemon_team.all().delete()

    for pd in snapshot['pokemon_team']:
        try:
            species = Pokemon.objects.get(id=pd['species_id'])
        except Pokemon.DoesNotExist:
            continue

        restored = PlayablePokemon(
            species=species,
            nickname=pd.get('nickname'),
            level=pd['level'],
            trainer=trainer,
            current_hp=pd['current_hp'],
            max_hp=pd['max_hp'],
            attack=pd['attack'],
            defense=pd['defense'],
            special_attack=pd['special_attack'],
            special_defense=pd['special_defense'],
            speed=pd['speed'],
            status_condition=pd.get('status_condition'),
            is_in_party=pd['is_in_party'],
            current_exp=pd.get('current_exp', 0),
            # ── IVs ──────────────────────────────────────────────────────
            iv_hp=pd.get('iv_hp', 0),
            iv_attack=pd.get('iv_attack', 0),
            iv_defense=pd.get('iv_defense', 0),
            iv_special_attack=pd.get('iv_special_attack', 0),
            iv_special_defense=pd.get('iv_special_defense', 0),
            iv_speed=pd.get('iv_speed', 0),
            # ── EVs ──────────────────────────────────────────────────────
            ev_hp=pd.get('ev_hp', 0),
            ev_attack=pd.get('ev_attack', 0),
            ev_defense=pd.get('ev_defense', 0),
            ev_special_attack=pd.get('ev_special_attack', 0),
            ev_special_defense=pd.get('ev_special_defense', 0),
            ev_speed=pd.get('ev_speed', 0),
            # ── Misc ─────────────────────────────────────────────────────
            nature=pd.get('nature', 'Hardy'),
            is_shiny=pd.get('is_shiny', False),
            party_position=pd.get('party_position'),
            original_trainer=pd.get('original_trainer'),
            pokeball_used=pd.get('pokeball_used'),
            friendship=pd.get('friendship', 70),
        )
        # Poser le flag AVANT save() pour bloquer learn_initial_moves().
        # Les moves seront restaurés manuellement depuis le snapshot juste après.
        restored._skip_learn_moves = True
        restored.save()

        for md in pd.get('moves', []):
            try:
                move = PokemonMove.objects.get(id=md['move_id'])
                PokemonMoveInstance.objects.get_or_create(
                    pokemon=restored,
                    move=move,
                    defaults={'current_pp': md['current_pp']},
                )
            except PokemonMove.DoesNotExist:
                continue

    # ── Inventaire ────────────────────────────────────────────────────────
    trainer.inventory.all().delete()

    for id_ in snapshot.get('inventory', []):
        try:
            item = Item.objects.get(id=id_['item_id'])
            TrainerInventory.objects.create(
                trainer=trainer,
                item=item,
                quantity=id_['quantity'],
            )
        except Item.DoesNotExist:
            continue

    # ── Achievements (v1.1) ───────────────────────────────────────────────
    for adata in snapshot.get('achievements', []):
        try:
            ach = Achievement.objects.get(name=adata['achievement_name'])
        except Achievement.DoesNotExist:
            continue

        ta, _ = TrainerAchievement.objects.get_or_create(
            trainer=trainer,
            achievement=ach,
            defaults={'current_progress': 0},
        )
        # Ne restaurer que si snapshot est plus avancé
        if adata['current_progress'] > ta.current_progress:
            ta.current_progress = adata['current_progress']
        if adata['is_completed'] and not ta.is_completed:
            ta.is_completed = True
            ta.completed_at = (
                timezone.datetime.fromisoformat(adata['completed_at'])
                if adata.get('completed_at') else timezone.now()
            )
        ta.save()

    # ── Quêtes (v1.1) ─────────────────────────────────────────────────────
    for qdata in snapshot.get('quests', []):
        try:
            quest = Quest.objects.get(quest_id=qdata['quest_id'])
        except Quest.DoesNotExist:
            continue

        qp, _ = QuestProgress.objects.get_or_create(
            trainer=trainer,
            quest=quest,
            defaults={'state': qdata['state']},
        )
        # On ne recule jamais un état (completed > active > available > locked)
        STATE_ORDER = {'locked': 0, 'available': 1, 'active': 2, 'completed': 3}
        if STATE_ORDER.get(qdata['state'], 0) > STATE_ORDER.get(qp.state, 0):
            qp.state = qdata['state']
        if qdata.get('data'):
            qp.data.update(qdata['data'])
        if qdata.get('completed_at') and not qp.completed_at:
            qp.completed_at = timezone.datetime.fromisoformat(qdata['completed_at'])
        qp.save()


# ============================================================================
# VUES DE SAUVEGARDE
# ============================================================================

@login_required
def save_select_view(request):
    """Écran de sélection de sauvegarde (3 slots)."""
    trainer = get_player_trainer(request.user)

    saves = []
    for slot in range(1, 4):
        save = GameSave.objects.filter(trainer=trainer, slot=slot).first()
        saves.append({'slot': slot, 'save': save, 'exists': save is not None})

    return render(request, 'saves/save_select.html', {'saves': saves, 'trainer': trainer})


@login_required
def save_create_view(request, slot):
    """Créer une nouvelle sauvegarde dans un slot."""
    trainer  = get_player_trainer(request.user)
    existing = GameSave.objects.filter(trainer=trainer, slot=slot).first()

    if request.method == 'POST':
        save_name = request.POST.get('save_name', f'Aventure {slot}')

        if existing:
            existing.delete()

        save = GameSave.objects.create(
            trainer=trainer,
            slot=slot,
            save_name=save_name,
            current_location='Bourg Palette',
            last_pokemon_center='Bourg Palette',
            play_time=0,
            story_flags={},
            defeated_trainers=[],
        )

        snapshot = create_game_snapshot(trainer, save)
        save.game_snapshot = snapshot
        save.is_active = True
        GameSave.objects.filter(trainer=trainer).exclude(pk=save.pk).update(is_active=False)
        save.save()

        logging.info(request, f"Nouvelle partie '{save_name}' créée !")
        return redirect('home')

    return render(request, 'saves/save_create.html', {'slot': slot, 'existing': existing})


@login_required
def save_load_view(request, save_id):
    """Charger une sauvegarde (restaure tout l'état du jeu)."""
    trainer = get_player_trainer(request.user)
    save    = get_object_or_404(GameSave, pk=save_id, trainer=trainer)

    if save.game_snapshot:
        try:
            restore_game_snapshot(trainer, save.game_snapshot)
            logging.info(request, f"Sauvegarde '{save.save_name}' chargée !")
        except Exception as e:
            logging.error(request, f"Erreur lors du chargement : {e}")
            return redirect('save_select')
    else:
        logging.warning(request, "Sauvegarde sans snapshot — chargement sans restauration.")

    GameSave.objects.filter(trainer=trainer).update(is_active=False)
    save.refresh_from_db()   # récupérer les story_flags/defeated_trainers restaurés
    save.is_active        = True
    save.current_location = save.game_snapshot.get('trainer', {}).get('location', 'Bourg Palette')
    save.save()

    return redirect('home')


@login_required
def save_game_view(request, save_id):
    """Sauvegarde manuelle — crée un snapshot complet."""
    trainer = get_player_trainer(request.user)
    save    = get_object_or_404(GameSave, pk=save_id, trainer=trainer)

    # Relire depuis la DB (story_flags/defeated_trainers écrits par d'autres vues)
    save.refresh_from_db()

    # Mettre à jour current_location depuis PlayerLocation (vraie source de vérité)
    try:
        save.current_location = trainer.player_location.current_zone.name
    except Exception:
        pass

    snapshot = create_game_snapshot(trainer, save)
    save.game_snapshot = snapshot

    time_since_last = (timezone.now() - save.last_saved).seconds
    save.play_time += time_since_last

    GameSave.objects.filter(trainer=trainer).update(is_active=False)
    save.is_active = True
    save.save()

    return JsonResponse({
        'success':                  True,
        'message':                  'Partie sauvegardée !',
        'save_id':                  save.id,
        'slot':                     save.slot,
        'play_time':                save.get_play_time_display(),
        'story_flags_count':        len(snapshot.get('story_flags', {})),
        'defeated_trainers_count':  len(snapshot.get('defeated_trainers', [])),
        'location':                 snapshot['trainer']['location'],
    })


@login_required
def auto_save_view(request, save_id):
    """Auto-save AJAX périodique."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    trainer = get_player_trainer(request.user)
    save    = get_object_or_404(GameSave, pk=save_id, trainer=trainer)

    if request.POST.get('location'):
        save.current_location = request.POST.get('location')

    # Rafraîchir depuis la DB avant le snapshot
    save.refresh_from_db()

    # Re-appliquer la location si elle a été fournie (refresh l'aurait écrasée)
    if request.POST.get('location'):
        save.current_location = request.POST.get('location')

    snapshot = create_game_snapshot(trainer, save)
    save.game_snapshot = snapshot

    time_since_last = (timezone.now() - save.last_saved).seconds
    save.play_time += time_since_last
    save.save()

    return JsonResponse({'success': True, 'snapshot_created': True})


@login_required
def save_slots_list_view(request):
    """API JSON pour le modal de sauvegarde."""
    trainer     = get_player_trainer(request.user)
    active_save = GameSave.objects.filter(trainer=trainer, is_active=True).first()

    slots = []
    for slot_num in range(1, 4):
        save      = GameSave.objects.filter(trainer=trainer, slot=slot_num).first()
        slot_data = {
            'slot':       slot_num,
            'exists':     save is not None,
            'is_current': save == active_save if save else False,
            'save_id':    save.id if save else None,
            'name':       save.save_name if save else f'Slot {slot_num}',
        }
        if save:
            slot_data.update({
                'play_time': save.get_play_time_display(),
                'badges':    save.badges_count,
                'money':     save.money,
                'location':  save.current_location,
            })
        slots.append(slot_data)

    return JsonResponse({'success': True, 'slots': slots})


@login_required
def save_create_quick_view(request, slot):
    """Créer rapidement une sauvegarde (pour modal)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})

    trainer   = get_player_trainer(request.user)
    save_name = request.POST.get('save_name', f'Aventure {slot}')

    # ── Récupérer l'état ACTUEL avant toute suppression ───────────────────
    # story_flags et defeated_trainers vivent sur le GameSave actif.
    # Il faut les lire MAINTENANT, avant de supprimer quoi que ce soit.
    active_save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
    current_story_flags      = dict(active_save.story_flags)      if active_save else {}
    current_defeated_trainers = list(active_save.defeated_trainers) if active_save else []

    # ── Récupérer la vraie position courante ──────────────────────────────
    try:
        current_location = trainer.player_location.current_zone.name
    except Exception:
        from myPokemonApp.gameUtils import get_player_location
        current_location = get_player_location(trainer)

    # ── Supprimer l'ancien save de CE slot (pas l'actif si différent) ─────
    existing = GameSave.objects.filter(trainer=trainer, slot=slot).first()
    if existing:
        existing.delete()

    # ── Créer le nouveau save avec les vraies données ─────────────────────
    save = GameSave.objects.create(
        trainer=trainer,
        slot=slot,
        save_name=save_name,
        current_location=current_location,
        play_time=active_save.play_time if active_save else 0,
        story_flags=current_story_flags,
        defeated_trainers=current_defeated_trainers,
    )

    snapshot = create_game_snapshot(trainer, save)
    save.game_snapshot = snapshot
    GameSave.objects.filter(trainer=trainer).update(is_active=False)
    save.is_active = True
    save.save()

    return JsonResponse({
        'success': True,
        'save_id': save.id,
        'slot':    slot,
        'message': f"Sauvegarde '{save_name}' créée !",
        # Debug
        'story_flags_count':        len(current_story_flags),
        'defeated_trainers_count':  len(current_defeated_trainers),
        'location':                 current_location,
    })