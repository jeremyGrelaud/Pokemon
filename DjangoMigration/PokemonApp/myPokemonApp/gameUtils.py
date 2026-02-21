#!/usr/bin/python3
"""
Fonctions utilitaires pour le jeu Pokemon Gen 1.

Organisation :
  1. Helpers trainer / pokemon
  2. Gestion des moves
  3. Creation de Pokemon  (sauvage, starter, NPC)
  4. Creation de NPCs et dresseurs
  5. Combats  (demarrage, IA, XP, fin de combat)
  6. Serialisation JSON  (pour les API views)
  7. Capture
  8. Rencontres sauvages
  9. Gestion inventaire
 10. Utilitaires divers (PC, natures, stats)
"""

import random
import logging
from myPokemonApp.models import *


# =============================================================================
# 1. HELPERS TRAINER / POKEMON
# =============================================================================

def get_first_alive_pokemon(trainer):
    """
    Retourne le premier Pokemon vivant de l'equipe active d'un dresseur.
    Pattern recurrent centralise ici pour eviter de le reecrire partout.
    """
    return trainer.pokemon_team.filter(
        is_in_party=True,
        current_hp__gt=0
    ).order_by('party_position').first()


def get_or_create_wild_trainer():
    """Recupere ou cree le Trainer 'Wild' utilise pour les Pokemon sauvages."""
    trainer, _ = Trainer.objects.get_or_create(
        username='Wild',
        defaults={'trainer_type': 'wild'}
    )
    return trainer


# =============================================================================
# 2. GESTION DES MOVES
# =============================================================================

def learn_moves_up_to_level(pokemon, level):
    """
    Synchronise les PokemonMoveInstance avec les 4 dernieres capacites
    apprises jusqu'au niveau donne.

    - Deduplique (si un move apparait a plusieurs niveaux, garde le plus recent).
    - Supprime les moves hors du set final (utile apres level-up ou relance).
    - Ajoute les moves manquants via get_or_create (idempotent).
    - Hard cap a 4 moves (regle Gen 1).
    """
    from .models.PlayablePokemon import PokemonMoveInstance

    learnable = pokemon.species.learnable_moves.filter(
        level_learned__lte=level
    ).order_by('level_learned')

    seen_moves = {}
    for lm in learnable:
        seen_moves[lm.move_id] = lm  # garde la derniere occurrence par move_id

    all_moves   = list(seen_moves.values())
    final_moves = all_moves[-4:] if len(all_moves) > 4 else all_moves
    final_ids   = {lm.move_id for lm in final_moves}

    PokemonMoveInstance.objects.filter(pokemon=pokemon).exclude(move_id__in=final_ids).delete()

    for lm in final_moves:
        PokemonMoveInstance.objects.get_or_create(
            pokemon=pokemon,
            move=lm.move,
            defaults={'current_pp': lm.move.pp}
        )


def copy_moves_to_pokemon(source_pokemon, target_pokemon):
    """
    Copie les PokemonMoveInstance du source vers la cible.
    Utilise lors de la capture. Hard cap a 4 moves.
    """
    from myPokemonApp.models import PokemonMoveInstance

    for mi in source_pokemon.pokemonmoveinstance_set.all()[:4]:
        if target_pokemon.pokemonmoveinstance_set.count() >= 4:
            break
        PokemonMoveInstance.objects.get_or_create(
            pokemon=target_pokemon,
            move=mi.move,
            defaults={'current_pp': mi.current_pp}
        )


def ensure_has_moves(pokemon):
    """
    Garantit qu'un Pokemon a au moins un move.
    Fallback sur Charge (Tackle) pour les Pokemon sans learnset configure.
    """
    from myPokemonApp.models import PokemonMoveInstance

    if not pokemon.pokemonmoveinstance_set.exists():
        tackle = (
            PokemonMove.objects.filter(name__icontains='Charge').first()
            or PokemonMove.objects.first()
        )
        if tackle:
            PokemonMoveInstance.objects.get_or_create(
                pokemon=pokemon,
                move=tackle,
                defaults={'current_pp': tackle.pp}
            )


# =============================================================================
# 3. CREATION DE POKEMON
# =============================================================================

def _build_ivs(iv_min=0, iv_max=31):
    """Genere un dict d'IVs aleatoires entre iv_min et iv_max."""
    iv_stats = ('iv_hp', 'iv_attack', 'iv_defense',
                'iv_special_attack', 'iv_special_defense', 'iv_speed')
    return {stat: random.randint(iv_min, iv_max) for stat in iv_stats}


def _finalize_pokemon(pokemon, level):
    """
    Calcule les stats, fixe les HP a leur maximum, apprend les moves.
    Factorise le pattern commun a toutes les creations de Pokemon.
    """
    pokemon.calculate_stats()
    pokemon.current_hp = pokemon.max_hp
    pokemon.save()
    learn_moves_up_to_level(pokemon, level)
    return pokemon


def create_wild_pokemon(species, level, location=None):
    """
    Cree un Pokemon sauvage avec des IVs aleatoires (0-31) et garantit
    au moins un move via ensure_has_moves().

    Args:
        species:  Pokemon (espece)
        level:    int
        location: str optionnel (nom de la zone de capture)

    Returns:
        PlayablePokemon sauvegarde avec stats et moves
    """
    from .models import PlayablePokemon

    pokemon = PlayablePokemon(
        species=species,
        trainer=get_or_create_wild_trainer(),
        level=level,
        current_exp=0,
        original_trainer='Wild',
        caught_location=location,
        is_in_party=True,
        **_build_ivs(0, 31)
    )
    _finalize_pokemon(pokemon, level)
    ensure_has_moves(pokemon)
    return pokemon


def create_starter_pokemon(species, trainer, nickname=None):
    """
    Cree un Pokemon de depart pour un joueur (niveau 5, IVs favorables 10-31).
    """
    from .models import PlayablePokemon

    pokemon = PlayablePokemon(
        species=species,
        trainer=trainer,
        nickname=nickname,
        level=5,
        current_exp=0,
        original_trainer=trainer.username,
        caught_location='Pallet Town',
        party_position=1,
        **_build_ivs(10, 31)
    )
    return _finalize_pokemon(pokemon, 5)


# =============================================================================
# 4. CREATION DE NPCs ET DRESSEURS
# =============================================================================

def _create_npc_pokemon(species, trainer, level, username, party_position,
                        iv_min=0, iv_max=20):
    """
    Cree et sauvegarde un PlayablePokemon pour un NPC avec ses stats calculees.
    Helper interne partage entre create_gym_leader et create_npc_trainer.
    """
    from .models import PlayablePokemon

    pokemon = PlayablePokemon(
        species=species,
        trainer=trainer,
        level=level,
        original_trainer=username,
        is_in_party=True,
        party_position=party_position,
        **_build_ivs(iv_min, iv_max)
    )
    pokemon.calculate_stats()
    pokemon.current_hp = pokemon.max_hp
    pokemon.save()
    return pokemon


def _assign_npc_moves(pokemon, moves):
    """
    Assigne une liste de moves a un Pokemon NPC.
    get_or_create + deduplication pour eviter les violations UNIQUE constraint.
    """
    from .models.PlayablePokemon import PokemonMoveInstance

    seen = set()
    for move in moves:
        if move.id in seen:
            continue
        seen.add(move.id)
        PokemonMoveInstance.objects.get_or_create(
            pokemon=pokemon,
            move=move,
            defaults={'current_pp': move.pp}
        )


def create_gym_leader(username, gym_name, city, badge_name,
                      specialty_type, badge_order, team_data):
    """
    Cree un Champion d'Arene avec son equipe. Idempotent (get_or_create).

    team_data = [
        {'species': Pokemon, 'level': 14, 'moves': [move1, move2]},
        ...
    ]
    """
    from .models import Trainer
    from .models.Trainer import GymLeader

    # IMPORTANT : le lookup se fait UNIQUEMENT sur username.
    # Tous les autres champs vont dans 'defaults' pour eviter que get_or_create
    # echoue si l'un d'eux differe lors d'une relance.
    trainer, created = Trainer.objects.get_or_create(
        username=username,
        defaults={
            'trainer_type': 'gym_leader',
            'location': city,
            'intro_text': f"Bienvenue a l'arene de {city} ! Je suis {username} !",
            'defeat_text': f"Tu m'as battu... Tu merites le badge {badge_name} !",
            'victory_text': "Tu n'es pas encore pret pour mon badge !",
            'can_rebattle': True,
            'is_npc': True,
            'npc_class': 'GymLeader',
        }
    )

    if not created:
        logging.info(f"  [skip] Gym Leader '{username}' existe deja")
        gym, _ = GymLeader.objects.get_or_create(trainer=trainer)
        return trainer, gym

    gym, _ = GymLeader.objects.get_or_create(
        trainer=trainer,
        defaults={
            'gym_name': gym_name,
            'gym_city': city,
            'badge_name': badge_name,
            'specialty_type': specialty_type,
            'badge_order': badge_order,
        }
    )

    for i, poke_data in enumerate(team_data, 1):
        # IVs eleves pour les champions (20-31)
        pokemon = _create_npc_pokemon(
            poke_data['species'], trainer, poke_data['level'],
            username, i, iv_min=20, iv_max=31
        )
        _assign_npc_moves(pokemon, poke_data.get('moves', []))

    return trainer, gym


def create_npc_trainer(username, trainer_type, location, team_data,
                       intro_text=None):
    """
    Cree un dresseur NPC generique avec son equipe. Idempotent (get_or_create).
    """
    from .models import Trainer

    trainer, created = Trainer.objects.get_or_create(
        username=username,
        defaults={
            'trainer_type': trainer_type,
            'location': location,
            'intro_text': intro_text or f"{username} veut combattre !",
            'defeat_text': "J'ai perdu...",
            'victory_text': "J'ai gagne !",
            'can_rebattle': False,
            'is_npc': True,
            'npc_class': 'Gamin',
        }
    )

    if not created:
        logging.info(f"  [skip] NPC '{username}' existe deja")
        return trainer

    for i, poke_data in enumerate(team_data, 1):
        # IVs moyens pour les dresseurs normaux (0-20)
        pokemon = _create_npc_pokemon(
            poke_data['species'], trainer, poke_data['level'],
            username, i, iv_min=0, iv_max=20
        )
        _assign_npc_moves(pokemon, poke_data.get('moves', []))

    return trainer


def create_rival(username, player_trainer):
    """Cree un rival lie au joueur."""
    from .models import Trainer

    return Trainer.objects.create(
        username=username,
        trainer_type='rival',
        intro_text=f"Salut {player_trainer.username} ! On fait un combat ?",
        defeat_text="Tu t'ameliores... Mais je serai toujours meilleur !",
        victory_text="Haha ! J'ai gagne comme toujours !",
        can_rebattle=True,
        money=0,
        is_npc=True,
        npc_class='Rival',
    )


# =============================================================================
# 5. COMBATS
# =============================================================================

# --- Demarrage ---

def start_battle(player_trainer, opponent_trainer=None, wild_pokemon=None,
                 battle_type='trainer'):
    """
    Demarre un nouveau combat et retourne (Battle, message_intro).

    Cas d'usage :
        battle, msg = start_battle(trainer, opponent_trainer=npc)
        battle, msg = start_battle(trainer, wild_pokemon=wild)
    """
    from .models import Battle

    player_pokemon = get_first_alive_pokemon(player_trainer)
    if not player_pokemon:
        return None, "Aucun Pokemon disponible pour combattre !"

    if wild_pokemon:
        opponent_pokemon = wild_pokemon
        battle_type = 'wild'
    elif opponent_trainer:
        opponent_pokemon = get_first_alive_pokemon(opponent_trainer)
        if not opponent_pokemon:
            return None, "L'adversaire n'a pas de Pokemon disponible !"
    else:
        return None, "Pas d'adversaire defini !"

    battle = Battle.objects.create(
        battle_type=battle_type,
        player_trainer=player_trainer,
        opponent_trainer=opponent_trainer,
        player_pokemon=player_pokemon,
        opponent_pokemon=opponent_pokemon,
        is_active=True,
    )

    msg = (
        f"Un {opponent_pokemon.species.name} sauvage apparait !"
        if battle_type == 'wild'
        else (opponent_trainer.intro_text or f"{opponent_trainer.username} veut combattre !")
    )
    battle.add_to_log(msg)
    battle.add_to_log(f"{player_trainer.username} envoie {player_pokemon} !")
    opponent_label = opponent_trainer.username if opponent_trainer else 'Wild'
    battle.add_to_log(f"{opponent_label} envoie {opponent_pokemon} !")

    return battle, msg


# --- IA adversaire ---

def get_opponent_ai_action(battle):
    """
    Determine l'action de l'adversaire pour ce tour.

    Priorites (dans l'ordre) :
      1. HP < 20% et potion disponible  -> utiliser potion  (30 % de chance)
      2. HP < 10% et remplacant dispo   -> changer          (50 % de chance)
      3. Choisir le move le plus efficace (puissance x type x STAB)
      4. Struggle si plus aucun PP

    Retourne un dict action compatible avec battle.execute_turn().
    """
    from .models.PlayablePokemon import PokemonMoveInstance

    pokemon  = battle.opponent_pokemon
    opponent = battle.player_pokemon

    # 1. Utiliser une potion si HP critique
    if pokemon.current_hp < pokemon.max_hp * 0.2:
        potions = pokemon.trainer.inventory.filter(
            item__item_type='potion', quantity__gt=0
        )
        if potions.exists() and random.random() < 0.3:
            return {'type': 'item', 'item': potions.first().item, 'target': pokemon}

    # 2. Changer si presque KO
    if pokemon.current_hp < pokemon.max_hp * 0.1:
        bench = pokemon.trainer.pokemon_team.filter(
            is_in_party=True, current_hp__gt=0
        ).exclude(id=pokemon.id)
        if bench.exists() and random.random() < 0.5:
            return {'type': 'switch', 'pokemon': random.choice(list(bench))}

    # 3. Meilleur move selon efficacite
    moves = PokemonMoveInstance.objects.filter(pokemon=pokemon, current_pp__gt=0)
    if not moves.exists():
        return {'type': 'struggle'}

    best_move, best_score = None, -1
    for mi in moves:
        score = (mi.move.power or 0) * battle.get_type_effectiveness(mi.move.type, opponent)
        if mi.move.type in (pokemon.species.primary_type, pokemon.species.secondary_type):
            score *= 1.5
        if score > best_score:
            best_score, best_move = score, mi.move

    return {'type': 'attack', 'move': best_move}


# --- XP et level-up ---

def calculate_exp_gain(defeated_pokemon, battle_type='wild'):
    """Calcule l'XP gagne selon la formule Gen 1."""
    base_exp = defeated_pokemon.species.base_experience or 100
    exp = int((base_exp * defeated_pokemon.level) / 7)
    if battle_type == 'trainer':
        exp = int(exp * 1.5)
    return exp


def apply_exp_gain(pokemon, exp_amount):
    """
    Applique l'XP a un Pokemon et gere les level-ups avec apprentissage de moves.

    Retourne :
        {
            'exp_gained':      int,
            'level_up':        bool,
            'new_level':       int,
            'learned_moves':   [str],  # noms des capacites auto-apprises (< 4 moves)
            'pending_moves':   [       # capacites en attente si le pokemon a deja 4 moves
                {
                    'move_id':   int,
                    'move_name': str,
                    'move_type': str,
                    'move_power': int|None,
                    'move_pp':   int,
                    'current_moves': [
                        {'id': int, 'name': str, 'type': str, 'power': int|None, 'pp': int}
                    ]
                }
            ]
        }
    """
    from .models.PlayablePokemon import PokemonMoveInstance

    result = {
        'exp_gained':    exp_amount,
        'level_up':      False,
        'new_level':     pokemon.level,
        'learned_moves': [],
        'pending_moves': [],
    }

    pokemon.current_exp = (pokemon.current_exp or 0) + exp_amount

    while pokemon.current_exp >= pokemon.exp_for_next_level():
        pokemon.current_exp -= pokemon.exp_for_next_level()
        pokemon.level += 1
        result['level_up'] = True
        result['new_level'] = pokemon.level

        # Recalculer stats et augmenter HP proportionnellement au gain de max_hp
        old_max_hp = pokemon.max_hp
        pokemon.calculate_stats()
        pokemon.current_hp = min(
            pokemon.current_hp + (pokemon.max_hp - old_max_hp),
            pokemon.max_hp
        )

        # Trouver les moves apprenables exactement a ce niveau
        new_learnable = pokemon.species.learnable_moves.filter(
            level_learned=pokemon.level
        ).select_related('move', 'move__type')

        for lm in new_learnable:
            move = lm.move
            # Verifier que le pokemon n'a pas deja ce move
            already_has = PokemonMoveInstance.objects.filter(
                pokemon=pokemon, move=move
            ).exists()
            if already_has:
                continue

            current_count = PokemonMoveInstance.objects.filter(pokemon=pokemon).count()

            if current_count < 4:
                # Apprendre automatiquement
                PokemonMoveInstance.objects.get_or_create(
                    pokemon=pokemon,
                    move=move,
                    defaults={'current_pp': move.pp}
                )
                result['learned_moves'].append(move.name)
            else:
                # Pokemon a deja 4 moves → proposer au joueur de choisir
                current_moves = [
                    {
                        'id':    mi.move.id,
                        'name':  mi.move.name,
                        'type':  mi.move.type.name if mi.move.type else '',
                        'power': mi.move.power,
                        'pp':    mi.move.pp,
                    }
                    for mi in PokemonMoveInstance.objects.filter(
                        pokemon=pokemon
                    ).select_related('move', 'move__type')
                ]
                result['pending_moves'].append({
                    'move_id':       move.id,
                    'move_name':     move.name,
                    'move_type':     move.type.name if move.type else '',
                    'move_power':    move.power,
                    'move_pp':       move.pp,
                    'current_moves': current_moves,
                })

    # Vérifier l'évolution après tous les level-ups
    # On ne l'applique pas ici : le joueur voit l'animation côté client,
    # puis envoie confirm_evolution pour effectuer le changement.
    if result['level_up'] and 'pending_evolution' not in result:
        evo = pokemon.check_evolution()
        if evo:
            result['pending_evolution'] = {
                'evolution_id':    evo.id,
                'pokemon_id':      pokemon.id,
                'from_name':       pokemon.species.name,
                'from_species_id': pokemon.species.id,
                'to_name':         evo.evolves_to.name,
                'to_species_id':   evo.evolves_to.id,
                # Stats actuelles (avant évolution)
                'stats_before': {
                    'hp':              pokemon.max_hp,
                    'attack':          pokemon.attack,
                    'defense':         pokemon.defense,
                    'special_attack':  pokemon.special_attack,
                    'special_defense': pokemon.special_defense,
                    'speed':           pokemon.speed,
                },
            }

    pokemon.save()
    return result


# --- Fin de combat ---

def check_battle_end(battle):
    """
    Verifie si le combat est termine.
    Retourne (is_ended: bool, winner: Trainer | None, message: str).

    Note : cette fonction ne distribue PAS l'XP ni n'appelle end_battle().
    La gestion de l'XP est centralisee dans BattleViews.py (action 'attack').
    """
    # Si le combat est deja marque termine, ne rien faire
    if not battle.is_active:
        return False, None, ""

    player_alive = battle.player_trainer.pokemon_team.filter(
        is_in_party=True, current_hp__gt=0
    ).exists()

    if battle.opponent_trainer:
        opponent_alive = battle.opponent_trainer.pokemon_team.filter(
            is_in_party=True, current_hp__gt=0
        ).exists()
    else:
        opponent_alive = battle.opponent_pokemon.current_hp > 0

    if not player_alive:
        battle.is_active = False
        battle.winner    = battle.opponent_trainer
        from django.utils import timezone
        battle.ended_at  = timezone.now()
        battle.save()
        return True, battle.opponent_trainer, "Vous avez perdu le combat..."

    if not opponent_alive:
        # La victoire du joueur est deja geree dans BattleViews.py (action attack).
        # On ne devrait jamais arriver ici pour une victoire normale.
        # Mais en cas de cas tordu, on marque quand meme la fin.
        battle.is_active = False
        battle.winner    = battle.player_trainer
        from django.utils import timezone
        battle.ended_at  = timezone.now()
        battle.save()
        msg = "Vous avez gagne le combat !"
        if battle.opponent_trainer:
            msg = battle.opponent_trainer.defeat_text or msg
        return True, battle.player_trainer, msg

    return False, None, ""


def opponent_switch_pokemon(battle):
    """Fait switcher l'adversaire vers son prochain Pokemon vivant."""
    if not battle.opponent_trainer:
        return None

    bench = battle.opponent_trainer.pokemon_team.filter(
        is_in_party=True, current_hp__gt=0
    ).exclude(id=battle.opponent_pokemon.id)

    if not bench.exists():
        return None

    new_pokemon = bench.first()
    battle.opponent_pokemon = new_pokemon
    battle.save()
    return new_pokemon


# =============================================================================
# 6. SERIALISATION JSON (pour les API views)
# =============================================================================

def serialize_pokemon(pokemon, include_moves=False):
    """
    Serialise un PlayablePokemon en dict JSON pret a etre envoye au client.

    Args:
        pokemon:       PlayablePokemon
        include_moves: bool — inclure la liste des moves avec PP courants

    Utilise dans build_battle_response() et GetTrainerTeam().
    """
    data = {
        'id':           pokemon.id,
        'name':         pokemon.nickname or pokemon.species.name,
        'species_name': pokemon.species.name,
        'level':        pokemon.level,
        'current_hp':   pokemon.current_hp,
        'max_hp':       pokemon.max_hp,
        'status':       pokemon.status_condition,
    }

    if include_moves:
        data['moves'] = [
            {
                'id':         mi.move.id,
                'name':       mi.move.name,
                'type':       mi.move.type.name,
                'power':      mi.move.power,
                'current_pp': mi.current_pp,
                'max_pp':     mi.move.max_pp,
            }
            for mi in pokemon.pokemonmoveinstance_set.all()
        ]

    return data


def build_battle_response(battle):
    """
    Construit le dict JSON complet renvoye au client apres chaque action.
    Remplace le build_response_data() qui etait defini inline dans battle_action_view.

    Contient :
      - player_pokemon   (avec moves + champs EXP)
      - opponent_pokemon (sans moves)
      - champs de retrocompatibilite (player_hp, opponent_hp, ...)
      - battle_ended: False  (le caller le passe a True si besoin)
    """
    exp_for_next = battle.player_pokemon.exp_for_next_level() or 100
    current_exp  = battle.player_pokemon.current_exp or 0

    player_data = serialize_pokemon(battle.player_pokemon, include_moves=True)
    player_data['current_exp']        = current_exp
    player_data['exp_for_next_level'] = exp_for_next
    player_data['exp_percent']        = int((current_exp / exp_for_next) * 100)

    return {
        'success':          True,
        'log':              [],
        'player_pokemon':   player_data,
        'opponent_pokemon': serialize_pokemon(battle.opponent_pokemon),
        # Champs de retrocompatibilite pour le JS existant
        'player_hp':        battle.player_pokemon.current_hp,
        'player_max_hp':    battle.player_pokemon.max_hp,
        'opponent_hp':      battle.opponent_pokemon.current_hp,
        'opponent_max_hp':  battle.opponent_pokemon.max_hp,
        'battle_ended':     False,
    }


# =============================================================================
# 7. CAPTURE
# =============================================================================

def calculate_capture_rate(pokemon, ball, pokemon_hp_percent, pokemon_status=None):
    """
    Calcule le taux de capture selon la formule Gen 1.

    Args:
        pokemon:            PlayablePokemon adversaire
        ball:               Item (pokeball)
        pokemon_hp_percent: float 0.0-1.0 (HP actuels / HP max)
        pokemon_status:     str ou None ('sleep', 'freeze', ...)

    Returns:
        float 0.0-1.0
    """
    # Master Ball -> capture garantie
    try:
        pokeball_stats = PokeballItem.objects.get(item=ball)
        if pokeball_stats.guaranteed_capture:
            return 1.0
    except PokeballItem.DoesNotExist:
        pokeball_stats = None

    base_rate = (
        pokemon.species.catch_rate if hasattr(pokemon, 'species') else pokemon.catch_rate
    ) or 45

    ball_mult = ball.catch_rate_modifier or 1.0

    # Bonus specifiques a certaines balls (type / statut)
    if pokeball_stats:
        if pokeball_stats.bonus_on_type:
            poke_types = (
                pokemon.species.types.all() if hasattr(pokemon, 'species')
                else pokemon.types.all()
            )
            if pokeball_stats.bonus_on_type in poke_types:
                ball_mult *= 1.5
        if (pokeball_stats.bonus_on_status
                and pokemon_status == pokeball_stats.bonus_on_status):
            ball_mult *= 1.5

    hp_mod     = max(0.1, min(1.0, (3 - 2 * pokemon_hp_percent) / 3))
    status_mod = (2.0 if pokemon_status in ('sleep', 'freeze')
                  else 1.5 if pokemon_status in ('burn', 'poison', 'paralysis')
                  else 1.0)

    return min(1.0, ((hp_mod * base_rate * ball_mult) / 255) * status_mod)


def attempt_pokemon_capture(battle, ball_item, trainer):
    """
    Tente de capturer le Pokemon adverse dans un combat avec le systeme de shakes.

    Returns:
        dict: {
            'success', 'capture_rate', 'shakes', 'message',
            'captured_pokemon', 'is_first_catch', 'achievement_notifications'
        }
    """
    from myPokemonApp.models import CaptureAttempt

    opponent     = battle.opponent_pokemon
    hp_percent   = opponent.current_hp / opponent.max_hp
    capture_rate = calculate_capture_rate(
        opponent, ball_item, hp_percent, opponent.status_condition
    )

    attempt = CaptureAttempt.objects.create(
        trainer=trainer,
        pokemon_species=opponent.species,
        ball_used=ball_item,
        pokemon_level=opponent.level,
        pokemon_hp_percent=hp_percent,
        pokemon_status=opponent.status_condition,
        capture_rate=capture_rate,
        battle=battle,
        success=False,
        shakes=0,
    )

    # Master Ball -> succes garanti sans shakes
    try:
        if PokeballItem.objects.get(item=ball_item).guaranteed_capture:
            return _capture_success(battle, opponent, ball_item, trainer, attempt, shakes=0)
    except PokeballItem.DoesNotExist:
        pass

    # Systeme de 3 shakes
    shakes = 0
    for _ in range(3):
        if random.random() < capture_rate:
            shakes += 1
        else:
            attempt.shakes = shakes
            attempt.save()
            return {
                'success':          False,
                'capture_rate':     capture_rate,
                'shakes':           shakes,
                'message':          f"{opponent.species.name} s'est echappe apres {shakes} shake(s) !",
                'captured_pokemon': None,
            }

    return _capture_success(battle, opponent, ball_item, trainer, attempt, shakes=3)


def _capture_success(battle, opponent, ball_item, trainer, attempt, shakes):
    """Gere la capture reussie d'un Pokemon (helper prive)."""
    from myPokemonApp.models import PlayablePokemon, CaptureJournal
    from myPokemonApp.views.AchievementViews import trigger_achievements_after_capture

    captured = PlayablePokemon.objects.create(
        species=opponent.species,
        level=opponent.level,
        trainer=trainer,
        current_hp=opponent.current_hp,
        max_hp=opponent.max_hp,
        attack=opponent.attack,
        defense=opponent.defense,
        special_attack=opponent.special_attack,
        special_defense=opponent.special_defense,
        speed=opponent.speed,
        status_condition=opponent.status_condition,
        is_in_party=False,
        current_exp=0,
    )
    copy_moves_to_pokemon(opponent, captured)

    is_first = not trainer.pokemon_team.filter(
        species=opponent.species
    ).exclude(id=captured.id).exists()

    CaptureJournal.objects.create(
        trainer=trainer,
        pokemon=captured,
        ball_used=ball_item,
        level_at_capture=opponent.level,
        hp_at_capture=opponent.current_hp,
        is_first_catch=is_first,
        is_critical_catch=(shakes == 0),
        attempts_before_success=1,
    )

    attempt.success = True
    attempt.shakes  = shakes
    attempt.save()

    battle.is_active = False
    battle.winner    = trainer
    battle.save()

    message = f"Vous avez capture {opponent.species.name} !"
    if is_first:
        message += " (Premier capture !)"

    return {
        'success':                   True,
        'capture_rate':              attempt.capture_rate,
        'shakes':                    shakes,
        'message':                   message,
        'captured_pokemon':          {'name': captured.species.name, 'level': captured.level},
        'is_first_catch':            is_first,
        'achievement_notifications': trigger_achievements_after_capture(trainer),
    }


# =============================================================================
# 8. RENCONTRES SAUVAGES
# =============================================================================

def get_random_wild_pokemon(zone, encounter_type='grass'):
    """
    Genere un Pokemon sauvage aleatoire selon les spawn rates d'une zone.

    Returns:
        (Pokemon species, level) ou (None, None) si aucun spawn configure.
    """
    spawns = WildPokemonSpawn.objects.filter(zone=zone, encounter_type=encounter_type)
    if not spawns.exists():
        return None, None

    total = sum(s.spawn_rate for s in spawns)
    if total == 0:
        return None, None

    roll, cumulative = random.uniform(0, total), 0
    for spawn in spawns:
        cumulative += spawn.spawn_rate
        if roll <= cumulative:
            return spawn.pokemon, random.randint(spawn.level_min, spawn.level_max)

    # Fallback (ne devrait jamais arriver si total > 0)
    first = spawns.first()
    return first.pokemon, random.randint(first.level_min, first.level_max)


def get_encounter_chance(encounter_type='grass'):
    """
    Determine s'il y a une rencontre aleatoire lors d'un deplacement.
    Returns: bool
    """
    base_rates = {'grass': 10.0, 'water': 20.0, 'fishing': 40.0, 'cave': 15.0}
    return random.random() * 100 < base_rates.get(encounter_type, 10.0)


# =============================================================================
# 9. GESTION INVENTAIRE
# =============================================================================

def give_item_to_trainer(trainer, item, quantity=1):
    """Donne un objet a un dresseur (cree ou incremente l'entree inventaire)."""
    from .models import TrainerInventory

    inv, _ = TrainerInventory.objects.get_or_create(
        trainer=trainer, item=item, defaults={'quantity': 0}
    )
    inv.quantity += quantity
    inv.save()
    return inv


def remove_item_from_trainer(trainer, item, quantity=1):
    """
    Retire un objet de l'inventaire.
    Retourne True si OK, False si stock insuffisant ou objet absent.
    """
    from .models import TrainerInventory

    try:
        inv = TrainerInventory.objects.get(trainer=trainer, item=item)
        if inv.quantity < quantity:
            return False
        inv.quantity -= quantity
        if inv.quantity == 0:
            inv.delete()
        else:
            inv.save()
        return True
    except TrainerInventory.DoesNotExist:
        return False


def use_item_in_battle(item, pokemon, battle):
    """
    Applique l'effet d'un objet pendant un combat.
    Retourne (success: bool, message: str).
    """
    if item.item_type == 'pokeball':
        if battle.battle_type != 'wild':
            return False, "On ne peut pas capturer le Pokemon d'un dresseur !"
        success, msg = _catch_pokemon_simple(
            battle.opponent_pokemon, battle.player_trainer, item
        )
        battle.add_to_log(msg)
        if success:
            battle.end_battle(battle.player_trainer)
        return success, msg
    elif item.item_type in ('potion', 'status'):
        result = item.use_on_pokemon(pokemon)
        battle.add_to_log(result)
        return True, result
    else:
        return False, "Cet objet ne peut pas etre utilise en combat !"


def _catch_pokemon_simple(wild_pokemon, trainer, pokeball_item):
    """
    Tentative de capture simplifiee (sans systeme de shakes).
    Retourne (success: bool, message: str).
    Utilise uniquement en interne par use_item_in_battle().
    """
    catch_rate = wild_pokemon.species.catch_rate
    hp_mod     = (3 * wild_pokemon.max_hp - 2 * wild_pokemon.current_hp) / (3 * wild_pokemon.max_hp)
    status_mod = (2.0 if wild_pokemon.status_condition in ('sleep', 'freeze')
                  else 1.5 if wild_pokemon.status_condition in ('paralysis', 'poison', 'burn')
                  else 1.0)

    if random.random() < (catch_rate * pokeball_item.catch_rate_modifier * hp_mod * status_mod) / 255:
        wild_pokemon.trainer          = trainer
        wild_pokemon.original_trainer = trainer.username
        wild_pokemon.pokeball_used    = pokeball_item.name
        wild_pokemon.friendship       = 70
        party_count = trainer.pokemon_team.filter(is_in_party=True).count()
        wild_pokemon.is_in_party    = party_count < 6
        wild_pokemon.party_position = party_count + 1 if party_count < 6 else None
        wild_pokemon.save()
        return True, f"{wild_pokemon.species.name} a ete capture !"

    return False, f"{wild_pokemon.species.name} s'est libere de la ball !"


# =============================================================================
# 10. UTILITAIRES DIVERS
# =============================================================================

def heal_team(trainer):
    """Soigne completement tous les Pokemon d'un dresseur (HP max + PP max)."""
    from .models.PlayablePokemon import PokemonMoveInstance

    for pokemon in trainer.pokemon_team.all():
        pokemon.heal()
        for mi in PokemonMoveInstance.objects.filter(pokemon=pokemon):
            mi.restore_pp()


def organize_party(trainer, pokemon_order):
    """
    Reordonne l'equipe du dresseur.
    pokemon_order = [pokemon_id_1, pokemon_id_2, ...]
    """
    for position, pokemon_id in enumerate(pokemon_order, 1):
        pokemon = trainer.pokemon_team.get(id=pokemon_id)
        pokemon.party_position = position
        pokemon.save()


def deposit_pokemon(pokemon):
    """Depose un Pokemon dans le PC (retire de l'equipe active)."""
    pokemon.is_in_party    = False
    pokemon.party_position = None
    pokemon.save()


def withdraw_pokemon(pokemon, position):
    """
    Retire un Pokemon du PC et l'ajoute a l'equipe.
    Retourne (success: bool, message: str).
    """
    if pokemon.trainer.pokemon_team.filter(is_in_party=True).count() >= 6:
        return False, "L'equipe est complete !"
    pokemon.is_in_party    = True
    pokemon.party_position = position
    pokemon.save()
    return True, f"{pokemon} a ete ajoute a l'equipe !"


def generate_random_nature():
    """Genere une nature aleatoire parmi les 25 natures."""
    return random.choice([
        'Hardy', 'Lonely', 'Brave', 'Adamant', 'Naughty',
        'Bold',  'Docile', 'Relaxed', 'Impish', 'Lax',
        'Timid', 'Hasty',  'Serious', 'Jolly',  'Naive',
        'Modest','Mild',   'Quiet',   'Bashful','Rash',
        'Calm',  'Gentle', 'Sassy',   'Careful','Quirky',
    ])


def get_nature_modifiers(nature):
    """
    Retourne (stat_augmentee, stat_diminuee) pour une nature.
    Retourne (None, None) pour les natures neutres.
    """
    effects = {
        'Lonely':  ('attack',         'defense'),
        'Brave':   ('attack',         'speed'),
        'Adamant': ('attack',         'special_attack'),
        'Naughty': ('attack',         'special_defense'),
        'Bold':    ('defense',        'attack'),
        'Relaxed': ('defense',        'speed'),
        'Impish':  ('defense',        'special_attack'),
        'Lax':     ('defense',        'special_defense'),
        'Timid':   ('speed',          'attack'),
        'Hasty':   ('speed',          'defense'),
        'Jolly':   ('speed',          'special_attack'),
        'Naive':   ('speed',          'special_defense'),
        'Modest':  ('special_attack', 'attack'),
        'Mild':    ('special_attack', 'defense'),
        'Quiet':   ('special_attack', 'speed'),
        'Rash':    ('special_attack', 'special_defense'),
        'Calm':    ('special_defense','attack'),
        'Gentle':  ('special_defense','defense'),
        'Sassy':   ('special_defense','speed'),
        'Careful': ('special_defense','special_attack'),
    }
    return effects.get(nature, (None, None))


def calculate_pokemon_stats_with_nature(pokemon):
    """Recalcule les stats d'un Pokemon en appliquant les modificateurs de nature (+10%/-10%)."""
    pokemon.calculate_stats()
    increased, decreased = get_nature_modifiers(pokemon.nature)
    if increased:
        setattr(pokemon, increased, int(getattr(pokemon, increased) * 1.1))
    if decreased:
        setattr(pokemon, decreased, int(getattr(pokemon, decreased) * 0.9))
    pokemon.save()