"""
Système de sauvegarde COMPLET avec snapshot v1.3
=================================================

Changements v1.0 → v1.1 :
  - create_game_snapshot() inclut désormais 'achievements' et 'quests'
    (pour référence / export — la source de vérité reste la DB)
  - restore_game_snapshot() restaure achievements et quests depuis le snapshot
  - Pas de régression sur le reste

v1.2 (DefeatedTrainer) :
  - defeated_trainers n'est plus un JSONField sur GameSave mais une table
    relationnelle (DefeatedTrainer). Les snapshots conservent le format
    list[int] pour la portabilité (export/import), mais la source de
    vérité live est la table.

v1.3 (Held Items) :
  - create_game_snapshot() inclut désormais 'held_item_id' pour chaque Pokémon.
  - restore_game_snapshot() restaure le held_item de chaque Pokémon.
  - Les snapshots anciens (sans held_item_id) sont tolérés : pd.get('held_item_id')
    retourne None, ce qui équivaut à aucun objet tenu.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import logging
import json

logger = logging.getLogger(__name__)

from myPokemonApp.models.Achievements import Achievement, TrainerAchievement
from myPokemonApp.models.GameSave import GameSave
from myPokemonApp.models.DefeatedTrainer import DefeatedTrainer
from myPokemonApp.models.Item import Item
from myPokemonApp.models.PlayablePokemon import PlayablePokemon, PokemonMoveInstance
from myPokemonApp.models.Pokemon import Pokemon
from myPokemonApp.models.PokemonMove import PokemonMove
from myPokemonApp.models.Quest import Quest, QuestProgress
from myPokemonApp.models.Trainer import Trainer, TrainerInventory
from myPokemonApp.models.Zone import PlayerLocation
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
        # defeated_trainers : list[int] dans le snapshot pour portabilité (export/restore)
        # La source de vérité live est la table DefeatedTrainer.
        'defeated_trainers': list(
            save.defeated_trainer_set.values_list('trainer_id', flat=True)
        ),
        'story_flags':  dict(save.story_flags),
        'achievements': [],
        'quests':       [],
    }

    # ── Pokémon ───────────────────────────────────────────────────────────
    for pokemon in trainer.pokemon_team.all():
        pdata = {
            'species_id':         pokemon.species.id,
            'species_name':       pokemon.species.name,
            'nickname':           pokemon.nickname,
            'level':              pokemon.level,
            'current_hp':         pokemon.current_hp,
            'max_hp':             pokemon.max_hp,
            'attack':             pokemon.attack,
            'defense':            pokemon.defense,
            'special_attack':     pokemon.special_attack,
            'special_defense':    pokemon.special_defense,
            'speed':              pokemon.speed,
            'status_condition':   pokemon.status_condition,
            'is_in_party':        pokemon.is_in_party,
            'current_exp':        pokemon.current_exp,
            'exp_for_next_level': pokemon.exp_for_next_level(),
            # ── IVs ──────────────────────────────────────────────────────
            'iv_hp':              pokemon.iv_hp,
            'iv_attack':          pokemon.iv_attack,
            'iv_defense':         pokemon.iv_defense,
            'iv_special_attack':  pokemon.iv_special_attack,
            'iv_special_defense': pokemon.iv_special_defense,
            'iv_speed':           pokemon.iv_speed,
            # ── EVs ──────────────────────────────────────────────────────
            'ev_hp':              pokemon.ev_hp,
            'ev_attack':          pokemon.ev_attack,
            'ev_defense':         pokemon.ev_defense,
            'ev_special_attack':  pokemon.ev_special_attack,
            'ev_special_defense': pokemon.ev_special_defense,
            'ev_speed':           pokemon.ev_speed,
            # ── Misc ─────────────────────────────────────────────────────
            'nature':             pokemon.nature,
            'is_shiny':           pokemon.is_shiny,
            'party_position':     pokemon.party_position,
            'original_trainer':   pokemon.original_trainer,
            'pokeball_used':      pokemon.pokeball_used,
            'friendship':         pokemon.friendship,
            # ── Held item ────────────────────────────────────────────────
            'held_item_id':       pokemon.held_item_id,
            'moves':              [],
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

def restore_game_snapshot(trainer, snapshot, save=None):
    """
    Restaure l'état complet du jeu depuis un snapshot.
    Gère v1.0 (sans achievements/quests), v1.1, v1.2, v1.3.

    Args:
        trainer  : le Trainer dont on restaure la progression.
        snapshot : le dict JSON du snapshot.
        save     : la GameSave cible (optionnel). Si None, on cherche
                   is_active=True — comportement rétrocompatible pour
                   les appels sans save explicite (ex. quicksave).
                   Toujours passer save explicitement depuis save_load_view
                   pour éviter d'écrire les DefeatedTrainer sur la mauvaise save.
    """
    # ── Trainer ───────────────────────────────────────────────────────────
    trainer.money  = snapshot['trainer']['money']
    trainer.badges = snapshot['trainer']['badges']
    trainer.save()

    # ── GameSave : story_flags + dresseurs vaincus ────────────────────────
    if save is None:
        save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
    if save:
        save.story_flags = dict(snapshot.get('story_flags', {}))
        save.save(update_fields=['story_flags'])

        # Restaure les dresseurs vaincus depuis le snapshot :
        save.defeated_trainer_set.all().delete()
        valid_ids = set(Trainer.objects.filter(
            id__in=snapshot.get('defeated_trainers', [])
        ).values_list('id', flat=True))
        DefeatedTrainer.objects.bulk_create(
            [DefeatedTrainer(game_save=save, trainer_id=tid)
             for tid in snapshot.get('defeated_trainers', [])
             if tid in valid_ids],
            ignore_conflicts=True,
        )

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
            # ── Held item ────────────────────────────────────────────────
            held_item_id=pd.get('held_item_id'),
        )
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
            # defeated_trainers : table vide par défaut (aucun DefeatedTrainer à créer)
        )

        snapshot = create_game_snapshot(trainer, save)
        save.game_snapshot = snapshot
        save.is_active = True
        GameSave.objects.filter(trainer=trainer).exclude(pk=save.pk).update(is_active=False)
        save.save()

        logger.info("Nouvelle partie '%s' créée pour %s", save_name, trainer.username)
        messages.success(request, f"Nouvelle partie '{save_name}' créée !")
        return redirect('home')

    return render(request, 'saves/save_create.html', {'slot': slot, 'existing': existing})


@login_required
def save_load_view(request, save_id):
    """Charger une sauvegarde (restaure tout l'état du jeu)."""
    trainer = get_player_trainer(request.user)
    save    = get_object_or_404(GameSave, pk=save_id, trainer=trainer)

    if save.game_snapshot:
        try:
            restore_game_snapshot(trainer, save.game_snapshot, save=save)
            logger.info("Sauvegarde '%s' (slot %s) chargée pour %s", save.save_name, save.slot, trainer.username)
            messages.success(request, f"Sauvegarde « {save.save_name} » chargée !")
        except Exception as e:
            logger.error("Erreur lors du chargement de la sauvegarde %s pour %s : %s", save.pk, trainer.username, e, exc_info=True)
            messages.error(request, f"Erreur lors du chargement : {e}")
            return redirect('save_select')
    else:
        logger.warning("Sauvegarde %s sans snapshot pour %s — chargement sans restauration.", save.pk, trainer.username)
        messages.warning(request, "Cette sauvegarde ne contient pas de snapshot — chargement partiel.")

    GameSave.objects.filter(trainer=trainer).update(is_active=False)
    save.refresh_from_db()   # récupérer les story_flags/defeated_trainers restaurés
    save.is_active        = True
    save.current_location = save.game_snapshot.get('trainer', {}).get('location', 'Bourg Palette')
    save.save()

    return redirect('home')


@login_required
def save_game_view(request, save_id):
    """Sauvegarde manuelle — crée un snapshot complet. Requiert POST."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    trainer = get_player_trainer(request.user)
    save    = get_object_or_404(GameSave, pk=save_id, trainer=trainer)

    # Relire depuis la DB (story_flags/defeated_trainers écrits par d'autres vues)
    save.refresh_from_db()

    active_save           = GameSave.objects.filter(trainer=trainer, is_active=True).first()
    saving_to_active_slot = active_save and active_save.id == save.id

    # ── Si on sauvegarde dans un slot DIFFÉRENT du slot actif ─────────────
    # → Copier l'état courant (defeated_trainers + story_flags) vers le slot cible.
    # → NE PAS changer is_active : sauvegarder ailleurs = backup, pas un switch de session.
    if not saving_to_active_slot and active_save:
        live_ids     = set(active_save.defeated_trainer_set.values_list('trainer_id', flat=True))
        snapshot_ids = set(active_save.game_snapshot.get('defeated_trainers', [])) if active_save.game_snapshot else set()
        source_ids   = list(live_ids | snapshot_ids)

        save.defeated_trainer_set.all().delete()
        if source_ids:
            valid_ids = set(Trainer.objects.filter(id__in=source_ids).values_list('id', flat=True))
            DefeatedTrainer.objects.bulk_create(
                [DefeatedTrainer(game_save=save, trainer_id=tid) for tid in source_ids if tid in valid_ids],
                ignore_conflicts=True,
            )
        save.story_flags = dict(active_save.story_flags)
        logger.info("save_game_view: backup vers slot %s — %d defeated trainers", save.slot, len(source_ids))

    # Mettre à jour current_location depuis PlayerLocation (vraie source de vérité)
    try:
        save.current_location = trainer.player_location.current_zone.name
    except Exception:
        pass

    snapshot = create_game_snapshot(trainer, save)
    save.game_snapshot = snapshot

    time_since_last = int((timezone.now() - save.last_saved).total_seconds())
    save.play_time += max(0, min(time_since_last, 7200))  # cap à 2h pour éviter les dérives

    if saving_to_active_slot:
        GameSave.objects.filter(trainer=trainer).update(is_active=False)
        save.is_active = True

    save.save()

    return JsonResponse({
        'success':                 True,
        'message':                 'Partie sauvegardée !',
        'save_id':                 save.id,
        'slot':                    save.slot,
        'play_time':               save.get_play_time_display(),
        'story_flags_count':       len(snapshot.get('story_flags', {})),
        'defeated_trainers_count': len(snapshot.get('defeated_trainers', [])),
        'location':                snapshot['trainer']['location'],
    })


@login_required
def auto_save_view(request, save_id):
    """Auto-save AJAX périodique."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    trainer = get_player_trainer(request.user)
    save    = get_object_or_404(GameSave, pk=save_id, trainer=trainer)

    # Relire depuis la DB en premier pour avoir les données fraîches
    save.refresh_from_db()

    # Appliquer la localisation APRÈS le refresh pour ne pas l'écraser
    if request.POST.get('location'):
        save.current_location = request.POST.get('location')

    snapshot = create_game_snapshot(trainer, save)
    save.game_snapshot = snapshot

    time_since_last = int((timezone.now() - save.last_saved).total_seconds())
    save.play_time += max(0, min(time_since_last, 7200))  # cap à 2h
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

    # ── Lire l'état ACTUEL avant toute suppression ────────────────────────
    active_save = GameSave.objects.filter(trainer=trainer, is_active=True).first()
    saving_to_active_slot = active_save and active_save.slot == slot

    current_story_flags = dict(active_save.story_flags) if active_save else {}

    # Lire les IDs de dresseurs vaincus : fusion table live + snapshot
    # pour couvrir les éventuels écarts entre les deux sources.
    live_defeated_ids = set(
        active_save.defeated_trainer_set.values_list('trainer_id', flat=True)
    ) if active_save else set()
    snapshot_defeated_ids = set(
        active_save.game_snapshot.get('defeated_trainers', [])
    ) if active_save and active_save.game_snapshot else set()
    current_defeated_ids = list(live_defeated_ids | snapshot_defeated_ids)

    try:
        current_location = trainer.player_location.current_zone.name
    except Exception:
        from myPokemonApp.gameUtils import get_player_location
        current_location = get_player_location(trainer)

    # ── Supprimer l'ancien save de CE slot ────────────────────────────────
    existing = GameSave.objects.filter(trainer=trainer, slot=slot).first()
    if existing:
        existing.delete()  # CASCADE supprime ses DefeatedTrainer

    # ── Créer le nouveau save ─────────────────────────────────────────────
    save = GameSave.objects.create(
        trainer=trainer,
        slot=slot,
        save_name=save_name,
        current_location=current_location,
        play_time=active_save.play_time if active_save else 0,
        story_flags=current_story_flags,
    )

    # Copier les dresseurs vaincus sur le nouveau slot
    if current_defeated_ids:
        valid_ids = set(Trainer.objects.filter(
            id__in=current_defeated_ids
        ).values_list('id', flat=True))
        DefeatedTrainer.objects.bulk_create(
            [DefeatedTrainer(game_save=save, trainer_id=tid)
             for tid in current_defeated_ids if tid in valid_ids],
            ignore_conflicts=True,
        )

    snapshot = create_game_snapshot(trainer, save)
    save.game_snapshot = snapshot

    # ── Gestion de is_active ──────────────────────────────────────────────
    # Sauvegarder dans un slot différent = copie de l'état (backup) :
    # l'active_save reste inchangée pour ne pas perturber add_defeated_trainer.
    # On ne bascule is_active que si on écrase le slot déjà actif.
    if saving_to_active_slot:
        GameSave.objects.filter(trainer=trainer).update(is_active=False)
        save.is_active = True

    save.save()

    return JsonResponse({
        'success': True,
        'save_id': save.id,
        'slot':    slot,
        'message': f"Sauvegarde '{save_name}' créée !",
        'story_flags_count':       len(current_story_flags),
        'defeated_trainers_count': len(current_defeated_ids),
        'location':                current_location,
    })