#!/usr/bin/python3
"""
Fonctions utilitaires pour le jeu Pokémon
Helpers pour la création de Pokémon, combats, NPCs, etc.
"""

import random
import math
from django.db.models import Q
from .models import PokeballItem


# ============================================================================
# CRÉATION DE POKÉMON
# ============================================================================

def create_wild_pokemon(species, level, location=None):
    """
    Crée un Pokémon sauvage à un niveau donné
    """
    from .models import PlayablePokemon, Trainer
    
    # Créer un "dresseur" sauvage temporaire
    wild_trainer, _ = Trainer.objects.get_or_create(
        username="Wild",
        defaults={'trainer_type': 'wild'}
    )
    
    # IVs aléatoires (0-31)
    ivs = {
        'iv_hp': random.randint(0, 31),
        'iv_attack': random.randint(0, 31),
        'iv_defense': random.randint(0, 31),
        'iv_special_attack': random.randint(0, 31),
        'iv_special_defense': random.randint(0, 31),
        'iv_speed': random.randint(0, 31),
    }
    
    # Créer le Pokémon
    pokemon = PlayablePokemon(
        species=species,
        trainer=wild_trainer,
        level=level,
        current_exp=0,
        original_trainer="Wild",
        caught_location=location,
        **ivs
    )
    
    # Calculer les stats
    pokemon.calculate_stats()
    pokemon.current_hp = pokemon.max_hp
    pokemon.save()
    
    # Apprendre les capacités appropriées au niveau
    learn_moves_up_to_level(pokemon, level)
    
    return pokemon


def create_starter_pokemon(species, trainer, nickname=None):
    """
    Crée un Pokémon de départ pour un joueur
    """
    from .models import PlayablePokemon
    
    # IVs légèrement meilleurs pour les starters
    ivs = {
        'iv_hp': random.randint(10, 31),
        'iv_attack': random.randint(10, 31),
        'iv_defense': random.randint(10, 31),
        'iv_special_attack': random.randint(10, 31),
        'iv_special_defense': random.randint(10, 31),
        'iv_speed': random.randint(10, 31),
    }
    
    pokemon = PlayablePokemon(
        species=species,
        trainer=trainer,
        nickname=nickname,
        level=5,
        current_exp=0,
        original_trainer=trainer.username,
        caught_location="Pallet Town",
        party_position=1,
        **ivs
    )
    
    pokemon.calculate_stats()
    pokemon.current_hp = pokemon.max_hp
    pokemon.save()
    
    # Apprendre les capacités de niveau 1-5
    learn_moves_up_to_level(pokemon, 5)
    
    return pokemon


def learn_moves_up_to_level(pokemon, level):
    """
    Fait apprendre au Pokémon toutes les capacités jusqu'au niveau donné
    Garde seulement les 4 dernières
    pokemon : PlayablePokemon
    """
    from .models.PlayablePokemon import PokemonMoveInstance
    
    learnable = pokemon.species.learnable_moves.filter(
        level_learned__lte=level
    ).order_by('level_learned')
    
    moves_to_learn = []
    for lm in learnable:
        if lm.move not in [m.move for m in moves_to_learn]:
            moves_to_learn.append(lm)
    
    # Garder les 4 dernières capacités
    final_moves = moves_to_learn[-4:] if len(moves_to_learn) > 4 else moves_to_learn


    # Copier les moves
    for move_instance in pokemon.pokemonmoveinstance_set.all():
        # Check if the move already exists for the captured Pokémon
        exists = PokemonMoveInstance.objects.filter(
            pokemon=pokemon,
            move=move_instance.move
        ).exists()

        if not exists:
            PokemonMoveInstance.objects.get_or_create(
                pokemon=pokemon,
                move=move_instance.move,
                current_pp=move_instance.current_pp,
            )


def catch_pokemon(wild_pokemon, trainer, pokeball_item):
    """
    Tente de capturer un Pokémon sauvage
    Retourne (success: bool, message: str)
    """
    # Formule de capture Gen 1
    catch_rate = wild_pokemon.species.catch_rate
    ball_modifier = pokeball_item.catch_rate_modifier
    
    # Modificateur de HP
    hp_modifier = (3 * wild_pokemon.max_hp - 2 * wild_pokemon.current_hp) / (3 * wild_pokemon.max_hp)
    
    # Modificateur de statut
    status_modifier = 1.0
    if wild_pokemon.status_condition in ['sleep', 'freeze']:
        status_modifier = 2.0
    elif wild_pokemon.status_condition in ['paralysis', 'poison', 'burn']:
        status_modifier = 1.5
    
    # Calcul final
    capture_value = (catch_rate * ball_modifier * hp_modifier * status_modifier) / 255
    
    # Jet aléatoire
    if random.random() < capture_value:
        # Capture réussie!
        wild_pokemon.trainer = trainer
        wild_pokemon.original_trainer = trainer.username
        wild_pokemon.pokeball_used = pokeball_item.name
        wild_pokemon.friendship = 70
        
        # Position dans l'équipe
        party_count = trainer.pokemon_team.filter(is_in_party=True).count()
        if party_count < 6:
            wild_pokemon.is_in_party = True
            wild_pokemon.party_position = party_count + 1
        else:
            wild_pokemon.is_in_party = False
        
        wild_pokemon.save()
        
        return True, f"{wild_pokemon.species.name} a été capturé!"
    else:
        # Capture ratée
        return False, f"{wild_pokemon.species.name} s'est libéré de la ball!"


# ============================================================================
# GESTION DES COMBATS
# ============================================================================

def start_battle(player_trainer, opponent_trainer=None, wild_pokemon=None, battle_type='trainer'):
    """
    Démarre un nouveau combat
    """
    from .models import Battle
    
    # Pokémon actif du joueur
    player_pokemon = player_trainer.pokemon_team.filter(
        is_in_party=True,
        current_hp__gt=0
    ).order_by('party_position').first()
    
    if not player_pokemon:
        return None, "Aucun Pokémon disponible pour combattre!"
    
    # Pokémon adverse
    if wild_pokemon:
        opponent_pokemon = wild_pokemon
        battle_type = 'wild'
    elif opponent_trainer:
        opponent_pokemon = opponent_trainer.pokemon_team.filter(
            is_in_party=True,
            current_hp__gt=0
        ).order_by('party_position').first()
        
        if not opponent_pokemon:
            return None, "L'adversaire n'a pas de Pokémon disponible!"
    else:
        return None, "Pas d'adversaire défini!"
    
    # Créer le combat
    battle = Battle.objects.create(
        battle_type=battle_type,
        player_trainer=player_trainer,
        opponent_trainer=opponent_trainer,
        player_pokemon=player_pokemon,
        opponent_pokemon=opponent_pokemon,
        is_active=True
    )
    
    # Message d'intro
    if battle_type == 'wild':
        msg = f"Un {opponent_pokemon.species.name} sauvage apparaît!"
    else:
        msg = opponent_trainer.intro_text or f"{opponent_trainer.username} veut combattre!"
    
    battle.add_to_log(msg)
    battle.add_to_log(f"{player_trainer.username} envoie {player_pokemon}!")
    battle.add_to_log(f"{opponent_trainer.username if opponent_trainer else 'Wild'} envoie {opponent_pokemon}!")
    
    return battle, msg


def ai_choose_action(pokemon, opponent, battle):
    """
    IA simple pour choisir l'action d'un Pokémon adverse
    Retourne un dictionnaire d'action
    """
    from .models.PlayablePokemon import PokemonMoveInstance
    
    # Si HP < 20%, 30% de chance d'utiliser une potion si disponible
    if pokemon.current_hp < pokemon.max_hp * 0.2:
        trainer = pokemon.trainer
        potions = trainer.inventory.filter(
            item__item_type='potion',
            quantity__gt=0
        )
        if potions.exists() and random.random() < 0.3:
            potion = potions.first().item
            return {
                'type': 'item',
                'item': potion,
                'target': pokemon
            }
    
    # Si le Pokémon est KO ou presque, changer si possible
    if pokemon.current_hp < pokemon.max_hp * 0.1:
        available_pokemon = pokemon.trainer.pokemon_team.filter(
            is_in_party=True,
            current_hp__gt=0
        ).exclude(id=pokemon.id)
        
        if available_pokemon.exists() and random.random() < 0.5:
            return {
                'type': 'switch',
                'pokemon': random.choice(list(available_pokemon))
            }
    
    # Choisir une attaque
    moves = PokemonMoveInstance.objects.filter(
        pokemon=pokemon,
        current_pp__gt=0
    )
    
    if not moves.exists():
        # Pas de PP, utiliser Struggle (à implémenter)
        return {'type': 'struggle'}
    
    # IA simple: choisir la meilleure attaque en fonction de l'efficacité
    best_move = None
    best_score = -1
    
    for move_instance in moves:
        move = move_instance.move
        score = move.power
        
        # Bonus pour les attaques super efficaces
        effectiveness = battle.get_type_effectiveness(move.type, opponent)
        score *= effectiveness
        
        # Bonus STAB
        if move.type == pokemon.species.primary_type or move.type == pokemon.species.secondary_type:
            score *= 1.5
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return {
        'type': 'attack',
        'move': best_move
    }


def check_battle_end(battle):
    """
    Vérifie si le combat est terminé
    Retourne (is_ended: bool, winner: Trainer, message: str)
    """
    player_has_pokemon = battle.player_trainer.pokemon_team.filter(
        is_in_party=True,
        current_hp__gt=0
    ).exists()
    
    opponent_has_pokemon = True
    if battle.opponent_trainer:
        opponent_has_pokemon = battle.opponent_trainer.pokemon_team.filter(
            is_in_party=True,
            current_hp__gt=0
        ).exists()
    else:
        # Combat sauvage
        opponent_has_pokemon = battle.opponent_pokemon.current_hp > 0
    
    if not player_has_pokemon:
        battle.end_battle(battle.opponent_trainer)
        return True, battle.opponent_trainer, "Vous avez perdu le combat..."
    
    if not opponent_has_pokemon:
        battle.end_battle(battle.player_trainer)
        
        # Distribuer l'expérience
        if battle.opponent_pokemon.is_fainted():
            exp = calculate_exp_gain(
                battle.opponent_pokemon,
                battle.player_pokemon
            )
            battle.player_pokemon.gain_exp(exp)
            battle.add_to_log(f"{battle.player_pokemon} gagne {exp} points d'expérience!")
        
        msg = "Vous avez gagné le combat!"
        if battle.opponent_trainer:
            msg = battle.opponent_trainer.defeat_text or msg
        
        return True, battle.player_trainer, msg
    
    return False, None, ""


def calculate_exp_gain(defeated_pokemon, winner_pokemon):
    """
    Calcule l'expérience gagnée après avoir vaincu un Pokémon
    Formule Gen 1
    """
    # a = 1.5 si dresseur, 1 si sauvage
    a = 1.5 if defeated_pokemon.trainer.trainer_type != 'wild' else 1.0
    
    # b = expérience de base de l'espèce
    b = defeated_pokemon.species.base_experience
    
    # L = niveau du Pokémon vaincu
    L = defeated_pokemon.level
    
    # s = nombre de Pokémon ayant participé (simplifié à 1 pour l'instant)
    s = 1
    
    # e = 1.5 si Lucky Egg, 1 sinon
    e = 1.0
    if winner_pokemon.held_item and winner_pokemon.held_item.name == "Lucky Egg":
        e = 1.5
    
    # t = 1.5 si échangé, 1 sinon
    t = 1.0
    if winner_pokemon.original_trainer != winner_pokemon.trainer.username:
        t = 1.5
    
    exp = int((a * b * L * e * t) / (7 * s))
    
    return exp


# ============================================================================
# CRÉATION DE NPCs ET DRESSEURS
# ============================================================================

def create_gym_leader(username, gym_name, city, badge_name, specialty_type, badge_order, team_data):
    """
    Crée un Champion d'Arène avec son équipe
    
    team_data = [
        {'species': Pokemon object, 'level': 14, 'moves': [move1, move2]},
        ...
    ]
    """
    from .models import Trainer, PlayablePokemon
    from .models.PlayablePokemon import PokemonMoveInstance
    from .models.Trainer import GymLeader
    
    # Créer le dresseur
    trainer = Trainer.objects.create(
        username=username,
        trainer_type='gym_leader',
        location=city,
        intro_text=f"Bienvenue à l'arène de {city}! Je suis {username}, champion de type {specialty_type.name}!",
        defeat_text=f"Tu m'as battu... Tu mérites le badge {badge_name}!",
        victory_text=f"Tu n'es pas encore prêt pour mon badge!",
        can_rebattle=True,
        is_npc=True,  # Default value 
        npc_class="GymLeader",
    )
    
    # Créer les infos de l'arène
    gym = GymLeader.objects.create(
        trainer=trainer,
        gym_name=gym_name,
        gym_city=city,
        badge_name=badge_name,
        specialty_type=specialty_type,
        badge_order=badge_order
    )
    
    # Créer l'équipe
    for i, poke_data in enumerate(team_data, 1):
        pokemon = PlayablePokemon(
            species=poke_data['species'],
            trainer=trainer,
            level=poke_data['level'],
            original_trainer=username,
            is_in_party=True,
            party_position=i,
            # IVs élevés pour les champions
            iv_hp=random.randint(20, 31),
            iv_attack=random.randint(20, 31),
            iv_defense=random.randint(20, 31),
            iv_special_attack=random.randint(20, 31),
            iv_special_defense=random.randint(20, 31),
            iv_speed=random.randint(20, 31),
        )
        pokemon.calculate_stats()
        pokemon.current_hp = pokemon.max_hp
        pokemon.save()
        
        # Apprendre les capacités
        for move in poke_data.get('moves', []):
            PokemonMoveInstance.objects.create(
                pokemon=pokemon,
                move=move,
                current_pp=move.pp
            )
    
    return trainer, gym


def create_npc_trainer(username, trainer_type, location, team_data, intro_text=None):
    """
    Crée un dresseur NPC générique avec son équipe
    """
    from .models import Trainer, PlayablePokemon
    from .models.PlayablePokemon import PokemonMoveInstance
    
    trainer = Trainer.objects.create(
        username=username,
        trainer_type=trainer_type,
        location=location,
        intro_text=intro_text or f"{username} veut combattre!",
        defeat_text="J'ai perdu...",
        victory_text="J'ai gagné!",
        can_rebattle=False,
        is_npc=True,  # Default value 
        npc_class="Gamin", #Default
    )
    
    for i, poke_data in enumerate(team_data, 1):
        pokemon = PlayablePokemon(
            species=poke_data['species'],
            trainer=trainer,
            level=poke_data['level'],
            original_trainer=username,
            is_in_party=True,
            party_position=i,
            # IVs moyens pour les dresseurs normaux
            iv_hp=random.randint(0, 20),
            iv_attack=random.randint(0, 20),
            iv_defense=random.randint(0, 20),
            iv_special_attack=random.randint(0, 20),
            iv_special_defense=random.randint(0, 20),
            iv_speed=random.randint(0, 20),
        )
        pokemon.calculate_stats()
        pokemon.current_hp = pokemon.max_hp
        pokemon.save()
        
        # Apprendre les capacités
        for move in poke_data.get('moves', []):
            PokemonMoveInstance.objects.create(
                pokemon=pokemon,
                move=move,
                current_pp=move.pp
            )
    
    return trainer


def create_rival(username, player_trainer):
    """
    Crée un rival qui évolue avec le joueur
    """
    from .models import Trainer
    
    rival = Trainer.objects.create(
        username=username,
        trainer_type='rival',
        intro_text=f"Salut {player_trainer.username}! On fait un combat?",
        defeat_text="Tu t'améliores... Mais je serai toujours meilleur!",
        victory_text="Haha! J'ai gagné comme toujours!",
        can_rebattle=True,
        money=0,  # Le rival ne donne pas d'argent
        is_npc=True,  # Default value 
        npc_class="Rival",
    )
    
    return rival


# ============================================================================
# GESTION DES OBJETS
# ============================================================================

def use_item_in_battle(item, pokemon, battle):
    """
    Utilise un objet pendant un combat
    """
    if item.item_type == 'pokeball':
        # Tenter une capture
        if battle.battle_type == 'wild':
            success, message = catch_pokemon(
                battle.opponent_pokemon,
                battle.player_trainer,
                item
            )
            battle.add_to_log(message)
            
            if success:
                battle.end_battle(battle.player_trainer)
                return True, message
            return False, message
        else:
            return False, "On ne peut pas capturer le Pokémon d'un dresseur!"
    
    elif item.item_type in ['potion', 'status']:
        result = item.use_on_pokemon(pokemon)
        battle.add_to_log(result)
        return True, result
    
    else:
        return False, "Cet objet ne peut pas être utilisé en combat!"


def give_item_to_trainer(trainer, item, quantity=1):
    """
    Donne un objet à un dresseur
    """
    from .models import TrainerInventory
    
    inventory_item, created = TrainerInventory.objects.get_or_create(
        trainer=trainer,
        item=item,
        defaults={'quantity': 0}
    )
    
    inventory_item.quantity += quantity
    inventory_item.save()
    
    return inventory_item


def remove_item_from_trainer(trainer, item, quantity=1):
    """
    Retire un objet de l'inventaire d'un dresseur
    """
    from .models import TrainerInventory
    
    try:
        inventory_item = TrainerInventory.objects.get(
            trainer=trainer,
            item=item
        )
        
        if inventory_item.quantity >= quantity:
            inventory_item.quantity -= quantity
            if inventory_item.quantity == 0:
                inventory_item.delete()
            else:
                inventory_item.save()
            return True
        return False
    except TrainerInventory.DoesNotExist:
        return False


# ============================================================================
# UTILITAIRES DIVERS
# ============================================================================

def heal_team(trainer):
    """
    Soigne complètement tous les Pokémon d'un dresseur
    """
    for pokemon in trainer.pokemon_team.all():
        pokemon.heal()
        
        # Restaurer les PP
        from .models.PlayablePokemon import PokemonMoveInstance
        for move_instance in PokemonMoveInstance.objects.filter(pokemon=pokemon):
            move_instance.restore_pp()


def organize_party(trainer, pokemon_order):
    """
    Réorganise l'équipe d'un dresseur
    pokemon_order = [pokemon_id1, pokemon_id2, ...]
    """
    for position, pokemon_id in enumerate(pokemon_order, 1):
        pokemon = trainer.pokemon_team.get(id=pokemon_id)
        pokemon.party_position = position
        pokemon.save()


def deposit_pokemon(pokemon):
    """
    Dépose un Pokémon dans le PC
    """
    pokemon.is_in_party = False
    pokemon.party_position = None
    pokemon.save()


def withdraw_pokemon(pokemon, position):
    """
    Retire un Pokémon du PC
    """
    # Vérifier qu'il y a de la place
    party_count = pokemon.trainer.pokemon_team.filter(is_in_party=True).count()
    if party_count >= 6:
        return False, "L'équipe est complète!"
    
    pokemon.is_in_party = True
    pokemon.party_position = position
    pokemon.save()
    
    return True, f"{pokemon} a été ajouté à l'équipe!"


def generate_random_nature():
    """
    Génère une nature aléatoire
    """
    natures = [
        'Hardy', 'Lonely', 'Brave', 'Adamant', 'Naughty',
        'Bold', 'Docile', 'Relaxed', 'Impish', 'Lax',
        'Timid', 'Hasty', 'Serious', 'Jolly', 'Naive',
        'Modest', 'Mild', 'Quiet', 'Bashful', 'Rash',
        'Calm', 'Gentle', 'Sassy', 'Careful', 'Quirky'
    ]
    return random.choice(natures)


def get_nature_modifiers(nature):
    """
    Retourne les modificateurs de stats pour une nature
    Retourne (stat_increased, stat_decreased)
    """
    nature_effects = {
        'Lonely': ('attack', 'defense'),
        'Brave': ('attack', 'speed'),
        'Adamant': ('attack', 'special_attack'),
        'Naughty': ('attack', 'special_defense'),
        'Bold': ('defense', 'attack'),
        'Relaxed': ('defense', 'speed'),
        'Impish': ('defense', 'special_attack'),
        'Lax': ('defense', 'special_defense'),
        'Timid': ('speed', 'attack'),
        'Hasty': ('speed', 'defense'),
        'Jolly': ('speed', 'special_attack'),
        'Naive': ('speed', 'special_defense'),
        'Modest': ('special_attack', 'attack'),
        'Mild': ('special_attack', 'defense'),
        'Quiet': ('special_attack', 'speed'),
        'Rash': ('special_attack', 'special_defense'),
        'Calm': ('special_defense', 'attack'),
        'Gentle': ('special_defense', 'defense'),
        'Sassy': ('special_defense', 'speed'),
        'Careful': ('special_defense', 'special_attack'),
    }
    
    return nature_effects.get(nature, (None, None))


def calculate_pokemon_stats_with_nature(pokemon):
    """
    Recalcule les stats d'un Pokémon en prenant en compte la nature
    """
    # Calculer les stats de base
    pokemon.calculate_stats()
    
    # Appliquer les modificateurs de nature (+10% / -10%)
    increased, decreased = get_nature_modifiers(pokemon.nature)
    
    if increased:
        current_value = getattr(pokemon, increased)
        setattr(pokemon, increased, int(current_value * 1.1))
    
    if decreased:
        current_value = getattr(pokemon, decreased)
        setattr(pokemon, decreased, int(current_value * 0.9))
    
    pokemon.save()


def opponent_switch_pokemon(battle):
    """Switch adversaire vers prochain Pokémon vivant"""
    if not battle.opponent_trainer:
        return None
    
    alive_pokemon = battle.opponent_trainer.pokemon_team.filter(
        is_in_party=True,
        current_hp__gt=0
    ).exclude(id=battle.opponent_pokemon.id)
    
    if not alive_pokemon.exists():
        return None
    
    new_pokemon = alive_pokemon.first()
    battle.opponent_pokemon = new_pokemon
    battle.save()
    
    return new_pokemon


def calculate_exp_gain(defeated_pokemon, battle_type='wild'):
    """Calcule XP selon formule Gen 1"""
    base_exp = defeated_pokemon.species.base_experience or 100
    level = defeated_pokemon.level
    exp = int((base_exp * level) / 7)
    
    if battle_type == 'trainer':
        exp = int(exp * 1.5)
    
    return exp


def apply_exp_gain(pokemon, exp_amount):
    """Applique XP et gère level-ups"""
    result = {
        'exp_gained': exp_amount,
        'level_up': False,
        'new_level': pokemon.level,
        'learned_moves': []
    }
    
    pokemon.current_exp = (pokemon.current_exp or 0) + exp_amount
    
    while pokemon.current_exp >= pokemon.exp_for_next_level():
        pokemon.current_exp -= pokemon.exp_for_next_level()
        pokemon.level += 1
        result['level_up'] = True
        result['new_level'] = pokemon.level
        
        pokemon.calculate_stats()
        pokemon.current_hp = pokemon.max_hp
        
        # Apprendre nouvelles attaques (TODO: gérer 4 max)
    
    pokemon.save()
    return result



"""
Logique de capture Gen 1
"""
def calculate_capture_rate(pokemon, ball, pokemon_hp_percent, pokemon_status=None):
    """
    Calcule le taux de capture selon la formule Gen 1
    
    Args:
        pokemon: PlayablePokemon ou Pokemon (opponent)
        ball: Item
        pokemon_hp_percent: % HP restants (0.0-1.0)
        pokemon_status: 'sleep', 'freeze', 'burn', etc.
    
    Returns:
        float: Taux de capture (0.0-1.0)
    """
    
    # Vérifier Master Ball
    try:
        pokeball_stats = PokeballItem.objects.get(item=ball)
        if pokeball_stats.guaranteed_capture:
            return 1.0
    except PokeballItem.DoesNotExist:
        pokeball_stats = None
    
    # Base catch rate
    if hasattr(pokemon, 'species'):
        base_catch_rate = pokemon.species.catch_rate or 45
    else:
        base_catch_rate = pokemon.catch_rate or 45
    
    # Ball multiplier
    ball_multiplier = ball.catch_rate_modifier or 1.0
    
    # Bonus type et status
    if pokeball_stats:
        if pokeball_stats.bonus_on_type:
            pokemon_types = pokemon.species.types.all() if hasattr(pokemon, 'species') else pokemon.types.all()
            if pokeball_stats.bonus_on_type in pokemon_types:
                ball_multiplier *= 1.5
        
        if pokeball_stats.bonus_on_status and pokemon_status == pokeball_stats.bonus_on_status:
            ball_multiplier *= 1.5
    
    # HP modifier
    hp_modifier = (3 - 2 * pokemon_hp_percent) / 3
    hp_modifier = max(0.1, min(1.0, hp_modifier))
    
    # Status modifier
    status_modifier = 1.0
    if pokemon_status in ['sleep', 'freeze']:
        status_modifier = 2.0
    elif pokemon_status in ['burn', 'poison', 'paralysis']:
        status_modifier = 1.5
    
    # Formule finale
    a = ((hp_modifier * base_catch_rate * ball_multiplier) / 255) * status_modifier
    
    return min(1.0, a)


def attempt_pokemon_capture(battle, ball_item, trainer):
    """
    Tente de capturer le Pokémon adverse
    
    Returns:
        dict: {
            'success': bool,
            'capture_rate': float,
            'shakes': int,
            'message': str,
            'captured_pokemon': PlayablePokemon or None
        }
    """
    
    opponent = battle.opponent_pokemon
    
    # Calculer HP%
    hp_percent = opponent.current_hp / opponent.max_hp
    
    # Calculer taux de capture
    capture_rate = calculate_capture_rate(
        opponent,
        ball_item,
        hp_percent,
        opponent.status_condition
    )
    
    # Enregistrer la tentative
    from myPokemonApp.models import CaptureAttempt
    attempt = CaptureAttempt.objects.create(
        trainer=trainer,
        pokemon_species=opponent.species,
        ball_used=ball_item,
        pokemon_level=opponent.level,
        pokemon_hp_percent=hp_percent,
        pokemon_status=opponent.status_condition,
        capture_rate=capture_rate,
        battle=battle,
        success=False,  # Sera mis à jour
        shakes=0
    )
    
    # Master Ball = succès garanti
    try:
        pokeball_stats = PokeballItem.objects.get(item=ball_item)
        if pokeball_stats.guaranteed_capture:
            return capture_pokemon_success(battle, opponent, ball_item, trainer, attempt, shakes=0)
    except PokeballItem.DoesNotExist:
        pass
    
    # Système de shakes (3 max)
    shakes = 0
    for shake in range(3):
        if random.random() < capture_rate:
            shakes += 1
        else:
            # Échappement
            attempt.shakes = shakes
            attempt.save()
            
            return {
                'success': False,
                'capture_rate': capture_rate,
                'shakes': shakes,
                'message': f"{opponent.species.name} s'est échappé après {shakes} shake(s) !",
                'captured_pokemon': None
            }
    
    # Les 3 shakes ont réussi = CAPTURE !
    return capture_pokemon_success(battle, opponent, ball_item, trainer, attempt, shakes=3)


def capture_pokemon_success(battle, opponent, ball_item, trainer, attempt, shakes):
    """Gère la capture réussie d'un Pokémon"""
    
    from myPokemonApp.models import PlayablePokemon, CaptureJournal
    
    # Créer le nouveau PlayablePokemon pour le trainer
    captured = PlayablePokemon.objects.create(
        species=opponent.species,
        nickname=None,  # Pas de surnom par défaut
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
        is_in_party=False,  # Pas dans l'équipe par défaut (PC)
        current_exp=0,
    )
    
    # Copier les moves
    for move_instance in opponent.pokemonmoveinstance_set.all():
        from myPokemonApp.models import PokemonMoveInstance
        # Check if the move already exists for the captured Pokémon
        exists = PokemonMoveInstance.objects.filter(
            pokemon=captured,
            move=move_instance.move
        ).exists()

        if not exists:
            PokemonMoveInstance.objects.get_or_create(
                pokemon=captured,
                move=move_instance.move,
                current_pp=move_instance.current_pp,
            )
    
    # Vérifier si c'est le premier de cette espèce
    is_first = not trainer.pokemon_team.filter(species=opponent.species).exclude(id=captured.id).exists()
    
    # Créer l'entrée de journal
    journal_entry = CaptureJournal.objects.create(
        trainer=trainer,
        pokemon=captured,
        ball_used=ball_item,
        level_at_capture=opponent.level,
        hp_at_capture=opponent.current_hp,
        is_first_catch=is_first,
        is_critical_catch=(shakes == 0),  # Capture critique si 0 shake
        attempts_before_success=1  # TODO: Compter les vraies tentatives
    )
    
    # Mettre à jour l'attempt
    attempt.success = True
    attempt.shakes = shakes
    attempt.save()
    
    # Terminer le combat
    battle.is_active = False
    battle.winner = trainer
    battle.save()
    
    message = f"Vous avez capturé {opponent.species.name} !"
    if is_first:
        message += " (Premier capturé !)"
    
    return {
        'success': True,
        'capture_rate': attempt.capture_rate,
        'shakes': shakes,
        'message': message,
        'captured_pokemon': {'name':captured.species.name, 'level' : captured.level } ,
        'is_first_catch': is_first,
        # 'journal_entry': journal_entry
    }