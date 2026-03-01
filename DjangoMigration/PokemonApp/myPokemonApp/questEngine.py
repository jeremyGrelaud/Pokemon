"""
QuestEngine — cerveau du système de quêtes.

API publique :
    get_quest_progress(trainer, quest_id)   → QuestProgress (crée si absent)
    complete_quest(trainer, quest_id)       → dict résultat
    trigger_quest_event(trainer, event, **ctx) → list[dict] notifications
    can_access_zone(trainer, zone)          → (bool, str)
    can_access_floor(trainer, floor)        → (bool, str)
    get_active_quests(trainer)              → QuerySet[QuestProgress]
    get_quest_log(trainer)                  → dict groupé par état
    trainer_has_hm(trainer, hm_name)       → bool  (Pokemon dans l'équipe qui connaît la CS)
    check_rival_encounter(trainer, zone, floor=None) → RivalEncounter | None
"""

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Mapping nom CS → nom de la capacité dans la BDD
HM_MOVE_NAMES = {
    'cut':      'Coupe',
    'surf':     'Surf',
    'strength': 'Force',
    'fly':      'Vol',
    'flash':    'Flash',
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE BAS NIVEAU
# ─────────────────────────────────────────────────────────────────────────────

def _get_save(trainer):
    """Retourne la GameSave active du trainer, ou None."""
    from myPokemonApp.models import GameSave
    return GameSave.objects.filter(trainer=trainer, is_active=True).first()


def _give_item(trainer, item, quantity=1):
    """Ajoute un item à l'inventaire du trainer."""
    from myPokemonApp.models import TrainerInventory
    inv, _ = TrainerInventory.objects.get_or_create(
        trainer=trainer, item=item,
        defaults={'quantity': 0}
    )
    inv.quantity += quantity
    inv.save(update_fields=['quantity'])


def set_story_flag_and_trigger(trainer, flag: str, value=True):
    """
    Pose un story_flag sur la GameSave active du trainer ET déclenche
    immédiatement les quêtes de type trigger_type='story_flag' qui attendent
    ce flag.

    À utiliser partout où l'on veut poser un flag scénaristique depuis une vue
    ou un système externe (ex: sommet Tour Pokémon nettoyé, Sylphe libéré…).

    Usage :
        set_story_flag_and_trigger(trainer, 'pokemon_tower_cleared')
    """
    save = _get_save(trainer)
    if save:
        save.story_flags[flag] = value
        save.save(update_fields=['story_flags'])

    # Propager aux quêtes en attente de ce flag
    try:
        trigger_quest_event(trainer, 'story_flag', flag=flag)
    except Exception as e:
        logger.warning("set_story_flag_and_trigger error: %s", e)


def _has_item(trainer, item):
    """Vérifie si le trainer possède au moins 1 exemplaire de l'item."""
    return trainer.inventory.filter(item=item, quantity__gte=1).exists()


# ─────────────────────────────────────────────────────────────────────────────
# CS / HM
# ─────────────────────────────────────────────────────────────────────────────

def trainer_has_hm(trainer, hm_name: str) -> bool:
    """
    Retourne True si au moins un Pokémon vivant de l'équipe active
    connaît la CS demandée.
    hm_name : 'cut' | 'surf' | 'strength' | 'fly' | 'flash'
    """
    move_name = HM_MOVE_NAMES.get(hm_name.lower())
    if not move_name:
        return False

    from myPokemonApp.models import PokemonMoveInstance
    return PokemonMoveInstance.objects.filter(
        pokemon__trainer=trainer,
        pokemon__is_in_party=True,
        pokemon__current_hp__gt=0,
        move__name__iexact=move_name,
    ).exists()


# ─────────────────────────────────────────────────────────────────────────────
# QUEST PROGRESS
# ─────────────────────────────────────────────────────────────────────────────

def get_quest_progress(trainer, quest_id: str):
    """
    Retourne (ou crée) le QuestProgress du trainer pour la quête quest_id.
    Gère automatiquement l'état initial (locked vs available).
    """
    from myPokemonApp.models import Quest, QuestProgress

    try:
        quest = Quest.objects.prefetch_related('prerequisite_quests').get(quest_id=quest_id)
    except Quest.DoesNotExist:
        return None

    progress, created = QuestProgress.objects.get_or_create(
        trainer=trainer,
        quest=quest,
        defaults={'state': 'locked'}
    )

    if created or progress.state == 'locked':
        # Recalculer si la quête peut être disponible
        if _prerequisites_met(trainer, quest):
            progress.state = 'available'
            progress.save(update_fields=['state'])

    return progress


def _prerequisites_met(trainer, quest) -> bool:
    """Tous les prérequis de la quête sont-ils complétés ?"""
    from myPokemonApp.models import QuestProgress
    prereqs = quest.prerequisite_quests.all()
    if not prereqs:
        return True
    completed_ids = set(
        QuestProgress.objects.filter(
            trainer=trainer, state='completed'
        ).values_list('quest__quest_id', flat=True)
    )
    return all(p.quest_id in completed_ids for p in prereqs)


# ─────────────────────────────────────────────────────────────────────────────
# COMPLÉTION DE QUÊTE
# ─────────────────────────────────────────────────────────────────────────────

def complete_quest(trainer, quest_id: str) -> dict:
    """
    Marque une quête comme complétée et applique les récompenses.
    Retourne un dict de notification (titre, récompenses, nouvelles quêtes).
    """
    from myPokemonApp.models import Quest, QuestProgress

    progress = get_quest_progress(trainer, quest_id)
    if not progress or progress.state == 'completed':
        return {'already_done': True}

    quest = progress.quest
    newly_done = progress.complete()
    if not newly_done:
        return {'error': 'impossible de compléter'}

    result = {
        'quest_id':    quest_id,
        'title':       quest.title,
        'reward_money': 0,
        'reward_item':  None,
        'new_flag':     quest.reward_flag or None,
        'newly_completed': True,
    }

    # Argent
    if quest.reward_money:
        trainer.earn_money(quest.reward_money)
        result['reward_money'] = quest.reward_money

    # Item
    if quest.reward_item:
        _give_item(trainer, quest.reward_item)
        result['reward_item'] = quest.reward_item.name

    # Story flag
    save = _get_save(trainer)
    if save and quest.reward_flag:
        save.story_flags[quest.reward_flag] = True
        save.save(update_fields=['story_flags'])

    # Débloquer les quêtes suivantes
    _unlock_dependent_quests(trainer, quest)

    # ── Hooks post-complétion spécifiques ─────────────────────────────────────
    _post_complete_hooks(trainer, quest_id, result)

    logger.info("Quest completed: %s for trainer %s", quest_id, trainer.username)
    return result


def _post_complete_hooks(trainer, quest_id: str, result: dict):
    """
    Effets de bord déclenchés après la complétion d'une quête spécifique.
    Centralise la logique narrative qui va au-delà des récompenses génériques
    (item, argent, flag) déjà gérées par complete_quest().
    """
    if quest_id == 'give_parcel_to_oak':
        # Le joueur a remis le colis au Professeur Chen.
        # On lui accorde le Pokédex et on retire le Colis de son inventaire.
        try:
            from myPokemonApp.gameUtils import grant_pokedex, remove_item_from_trainer
            from myPokemonApp.models import Item
            grant_pokedex(trainer)
            parcel = Item.objects.filter(name='Colis de Chen').first()
            if parcel:
                remove_item_from_trainer(trainer, parcel, quantity=1)
        except Exception as e:
            logger.warning("Hook give_parcel_to_oak error: %s", e)

    if quest_id == 'defeat_giovanni':
        # Giovanni battu = 8e badge obtenu → débloquer la Route 23
        try:
            set_story_flag_and_trigger(trainer, 'all_badges_obtained')
            logger.info("Hook defeat_giovanni: flag all_badges_obtained posé pour %s", trainer.username)
        except Exception as e:
            logger.warning("Hook defeat_giovanni error: %s", e)



def _unlock_dependent_quests(trainer, completed_quest):
    """Passe en 'available' les quêtes qui attendaient cette quête."""
    from myPokemonApp.models import Quest, QuestProgress
    dependents = Quest.objects.filter(prerequisite_quests=completed_quest)
    for dep in dependents:
        if _prerequisites_met(trainer, dep):
            QuestProgress.objects.update_or_create(
                trainer=trainer,
                quest=dep,
                defaults={'state': 'available'},
            )


# ─────────────────────────────────────────────────────────────────────────────
# DÉCLENCHEURS D'ÉVÉNEMENTS
# ─────────────────────────────────────────────────────────────────────────────

def trigger_quest_event(trainer, event: str, **ctx) -> list:
    """
    Déclenche les quêtes liées à un événement.

    event : 'visit_zone' | 'defeat_trainer' | 'defeat_gym' | 'have_item' | 'give_item'
    ctx   : données contextuelles (zone=, trainer_id=, gym_leader=, item=, …)

    Retourne une liste de dicts de notifications pour les quêtes complétées.
    """
    from myPokemonApp.models import Quest, QuestProgress

    notifications = []

    quests = Quest.objects.filter(trigger_type=event).prefetch_related('prerequisite_quests')

    for quest in quests:
        # Vérifier si cette quête est pertinente pour l'événement
        if not _event_matches_quest(quest, event, ctx):
            continue

        progress = get_quest_progress(trainer, quest.quest_id)
        if not progress or progress.state == 'completed':
            continue

        # S'assurer que les prérequis sont OK
        if not _prerequisites_met(trainer, quest):
            continue

        # Démarrer si pas encore active
        if progress.state == 'available':
            progress.start()

        # Compléter
        result = complete_quest(trainer, quest.quest_id)
        if result.get('newly_completed'):
            notifications.append(result)

    return notifications


def _event_matches_quest(quest, event: str, ctx: dict) -> bool:
    """Vérifie si l'événement correspond aux critères de la quête."""

    if event == 'visit_zone':
        zone = ctx.get('zone')
        return quest.trigger_zone_id and zone and quest.trigger_zone_id == zone.id

    if event == 'defeat_trainer':
        trainer_id = ctx.get('trainer_id')
        # Cas normal : quête avec trigger_trainer explicite (NPC, Elite 4…)
        if quest.trigger_trainer_id:
            return trainer_id and quest.trigger_trainer_id == trainer_id
        # Cas rival : quête de type 'rival' sans trigger_trainer (résolu per-player).
        # On vérifie si le Trainer NPC battu est bien le PlayerRival de ce joueur
        # pour cette quête.
        if quest.quest_type == 'rival' and trainer_id:
            player_trainer = ctx.get('player_trainer')
            if player_trainer is None:
                return False
            try:
                from myPokemonApp.models import PlayerRival
                pr = PlayerRival.objects.filter(
                    player=player_trainer,
                    template__quest_id=quest.quest_id,
                    trainer__id=trainer_id,
                ).exists()
                return pr
            except Exception:
                return False
        return False

    if event == 'defeat_gym':
        gym_leader = ctx.get('gym_leader')   # objet GymLeader
        if not gym_leader:
            return False
        # Si la quête cible un trainer précis, vérifier l'ID
        if quest.trigger_trainer_id:
            return quest.trigger_trainer_id == gym_leader.trainer_id
        # Si la quête n'a pas de trainer spécifique mais a un flag arène,
        # on la déclenche pour tout gym win (cas quêtes génériques "defeat_gym")
        if quest.trigger_type == 'defeat_gym' and not quest.trigger_trainer_id:
            return True
        return False

    if event == 'have_item':
        item = ctx.get('item')
        return quest.trigger_item_id and item and quest.trigger_item_id == item.id

    if event == 'give_item':
        # give_item = le joueur remet un objet à quelqu'un (NPC, lab, etc.)
        # Le trigger_item de la quête doit correspondre à l'item remis.
        item = ctx.get('item')
        return quest.trigger_item_id and item and quest.trigger_item_id == item.id

    if event == 'story_flag':
        flag = ctx.get('flag')
        return quest.trigger_flag and flag and quest.trigger_flag == flag

    return False


# ─────────────────────────────────────────────────────────────────────────────
# CONTRÔLE D'ACCÈS AUX ZONES
# ─────────────────────────────────────────────────────────────────────────────

def can_access_zone(trainer, zone) -> tuple:
    """
    Vérifie si le trainer peut accéder à une zone.
    Chaîne de contrôle :
      1. Badge requis
      2. Item requis
      3. CS requise (HM) — un Pokémon doit la connaître
      4. Flags scénaristiques requis
      5. Quête requise complétée
    Retourne (bool, str_raison).
    """
    # 1. Badge
    if zone.required_badge:
        if trainer.badges < zone.required_badge.badge_order:
            return False, f"Badge « {zone.required_badge.badge_name} » requis"

    # 2. Item clé
    if zone.required_item:
        if not _has_item(trainer, zone.required_item):
            return False, f"Objet requis : {zone.required_item.name}"

    # 3. CS
    if hasattr(zone, 'required_hm') and zone.required_hm:
        hm = zone.required_hm
        move_label = HM_MOVE_NAMES.get(hm, hm.capitalize())
        if not trainer_has_hm(trainer, hm):
            return False, f"CS {move_label} requise (un Pokémon doit la connaître)"

    # 4. Story flags
    if hasattr(zone, 'required_flags') and zone.required_flags:
        save = _get_save(trainer)
        for flag in zone.required_flags:
            if not (save and save.story_flags.get(flag)):
                label = flag.replace('_', ' ').capitalize()
                return False, f"Condition manquante : {label}"

    # 5. Quête requise
    if hasattr(zone, 'required_quest') and zone.required_quest:
        from myPokemonApp.models import QuestProgress
        done = QuestProgress.objects.filter(
            trainer=trainer,
            quest=zone.required_quest,
            state='completed',
        ).exists()
        if not done:
            return False, f"Quête requise : « {zone.required_quest.title} »"

    return True, 'OK'


def can_access_floor(trainer, floor) -> tuple:
    """Délègue à ZoneFloor.is_accessible_by + vérif HM si pertinent."""
    return floor.is_accessible_by(trainer)


# ─────────────────────────────────────────────────────────────────────────────
# JOURNAL DE QUÊTES
# ─────────────────────────────────────────────────────────────────────────────

def get_quest_log(trainer) -> dict:
    """
    Retourne le journal de quêtes complet, groupé par état.
    Crée les QuestProgress manquants pour les quêtes disponibles.
    """
    from myPokemonApp.models import Quest, QuestProgress

    # S'assurer que toutes les quêtes sans prérequis sont 'available'
    all_quests = Quest.objects.prefetch_related('prerequisite_quests').all()
    for quest in all_quests:
        get_quest_progress(trainer, quest.quest_id)

    qs = QuestProgress.objects.filter(trainer=trainer).select_related(
        'quest', 'quest__reward_item', 'quest__trigger_zone'
    ).order_by('quest__order')

    log = {
        'active':    [p for p in qs if p.state in ('available', 'active')],
        'completed': [p for p in qs if p.state == 'completed'],
        'locked':    [p for p in qs if p.state == 'locked'],
    }
    return log


def get_active_quests(trainer):
    """Shortcut : quêtes en cours ou disponibles."""
    from myPokemonApp.models import QuestProgress
    return QuestProgress.objects.filter(
        trainer=trainer, state__in=('available', 'active')
    ).select_related('quest').order_by('quest__order')


# ─────────────────────────────────────────────────────────────────────────────
# RIVAL
# ─────────────────────────────────────────────────────────────────────────────

def check_rival_encounter(trainer, zone, floor=None):
    """
    Retourne le RivalEncounter actif dans cette zone/étage pour CE joueur.

    Résolution per-player :
      1. On cherche les RivalEncounter actifs dans la zone.
      2. Pour chaque encounter, on résout le Trainer NPC via PlayerRival
         (instance spécifique à ce joueur) plutôt que via enc.rival directement.
      3. Si le PlayerRival n'existe pas encore (rare), on retourne None silencieusement.

    Retourne un objet "encounter proxy" avec l'attribut .rival pointant vers
    le Trainer NPC spécifique au joueur, ou None si rien de disponible.
    """
    from myPokemonApp.models import RivalEncounter, PlayerRival, RivalTemplate

    encounters = RivalEncounter.objects.filter(zone=zone).select_related(
        'quest', 'rival', 'floor'
    )
    if floor:
        encounters = encounters.filter(floor=floor)

    for enc in encounters:
        # La quête associée doit être active (non complétée)
        progress = get_quest_progress(trainer, enc.quest.quest_id)
        if not progress or progress.state not in ('available', 'active'):
            continue

        # Résolution per-player via PlayerRival.
        # On cherche directement le PlayerRival de ce joueur pour ce quest_id
        # (sans passer par le template : PlayerRival.template.quest_id suffit).
        try:
            pr = PlayerRival.objects.filter(
                player=trainer,
                template__quest_id=enc.quest.quest_id,
            ).select_related('trainer', 'template').first()
        except Exception:
            pr = None

        if pr is not None:
            rival_trainer = pr.trainer
            if rival_trainer is None:
                # Spawn tardif si manquant (sécurité)
                rival_trainer = pr.spawn_for_player()
        else:
            # Aucun PlayerRival → fallback enc.rival (retro-compat)
            rival_trainer = enc.rival

        if rival_trainer and not rival_trainer.is_defeated_by_player(trainer):
            # Retourner un proxy léger avec .rival résolu pour ce joueur
            enc._resolved_rival = rival_trainer
            return _RivalEncounterProxy(enc, rival_trainer)

    return None


class _RivalEncounterProxy:
    """
    Proxy léger autour de RivalEncounter qui expose .rival résolu per-player.
    Compatible avec les templates existants (rival_encounter.rival.username,
    rival_encounter.pre_battle_text, rival_encounter.rival.id, etc.).
    """
    def __init__(self, encounter, rival_trainer):
        self._enc    = encounter
        self.rival   = rival_trainer
        # Délégation des attributs de RivalEncounter
        self.id               = encounter.id
        self.quest            = encounter.quest
        self.zone             = encounter.zone
        self.floor            = encounter.floor
        self.pre_battle_text  = encounter.pre_battle_text
        self.post_battle_text = encounter.post_battle_text

    def __repr__(self):
        return f"<RivalEncounterProxy quest={self.quest.quest_id} rival={self.rival.username}>"