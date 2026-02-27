"""
services/serializers.py
=======================
Sérialisation JSON des objets de combat pour les réponses API.

Fonctions publiques :
    serialize_pokemon(pokemon, include_moves=False) → dict
    serialize_pokemon_moves(pokemon)                → list[dict]
    build_battle_response(battle)                   → dict
"""


def serialize_pokemon(pokemon, include_moves=False):
    """
    Sérialise un PlayablePokemon en dict JSON prêt à être envoyé au client.

    Args:
        pokemon:       PlayablePokemon
        include_moves: bool — inclure la liste des moves avec PP courants

    Utilisé dans build_battle_response() et GetTrainerTeam().
    """
    data = {
        'id':           pokemon.id,
        'name':         pokemon.nickname or pokemon.species.name,
        'species_name': pokemon.species.name,
        'level':        pokemon.level,
        'current_hp':   pokemon.current_hp,
        'max_hp':       pokemon.max_hp,
        'status':       pokemon.status_condition,
        'is_shiny':     pokemon.is_shiny,
    }

    if include_moves:
        data['moves'] = [
            {
                'id':         mi.move.id,
                'name':       mi.move.name,
                'type':       mi.move.type.name if mi.move.type else '',
                'category':   mi.move.category,
                'power':      mi.move.power,
                'current_pp': mi.current_pp,
                'max_pp':     mi.move.pp,
            }
            for mi in pokemon.pokemonmoveinstance_set.select_related('move', 'move__type').all()
        ]

    return data


def serialize_pokemon_moves(pokemon):
    """
    Sérialise les moves actifs d'un Pokémon pour les réponses JSON
    (gestion d'équipe, modal de capacités).

    Distinct de serialize_pokemon(include_moves=True) qui est orienté combat :
    on ajoute ici category, accuracy et pp (max) pour la gestion d'équipe.
    """
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance

    return [
        {
            'id':         mi.move.id,
            'name':       mi.move.name,
            'type':       mi.move.type.name if mi.move.type else '',
            'category':   mi.move.category,
            'power':      mi.move.power,
            'accuracy':   mi.move.accuracy,
            'pp':         mi.move.pp,
            'current_pp': mi.current_pp,
        }
        for mi in PokemonMoveInstance.objects.filter(
            pokemon=pokemon
        ).select_related('move', 'move__type')
    ]


def build_battle_response(battle):
    """
    Construit le dict JSON complet renvoyé au client après chaque action.

    Contient :
      - player_pokemon   (avec moves + champs EXP)
      - opponent_pokemon (sans moves)
      - champs de rétrocompatibilité (player_hp, opponent_hp, …)
      - battle_ended: False  (le caller le passe à True si besoin)
      - battle_state: états volatils + stat stages pour le frontend
    """
    pp = battle.player_pokemon

    # XP cumulée requise pour le niveau actuel et le suivant
    exp_at_current = pp.exp_at_level(pp.level)
    exp_at_next    = pp.exp_for_next_level()   # = exp_at_level(level + 1)
    current_exp    = pp.current_exp or 0

    # XP relative dans le niveau courant (0 → exp_needed_this_level)
    exp_in_level = max(0, current_exp - exp_at_current)
    exp_needed   = max(1, exp_at_next - exp_at_current)
    exp_percent  = int(min(100, (exp_in_level / exp_needed) * 100))

    player_data = serialize_pokemon(pp, include_moves=True)
    player_data['current_exp']        = exp_in_level   # XP dans le niveau actuel
    player_data['exp_for_next_level'] = exp_needed     # XP requise pour passer au suivant
    player_data['exp_percent']        = exp_percent

    opp = battle.opponent_pokemon
    bs  = battle.battle_state if isinstance(battle.battle_state, dict) else {}

    def pst(pokemon):
        return bs.get(str(pokemon.pk), {})

    p_pst = pst(pp)
    o_pst = pst(opp)

    battle_state = {
        # ── Météo ──────────────────────────────────────────────────────────
        'weather':       bs.get('weather'),
        'weather_turns': bs.get('weather_turns', 0),

        # ── États volatils joueur ──────────────────────────────────────────
        'player_confused':       bool(p_pst.get('confusion_turns', 0)),
        'player_leech_seed':     bool(p_pst.get('leech_seed')),
        'player_trapped':        bool(p_pst.get('trap_turns', 0)),
        'player_badly_poisoned': bool(p_pst.get('toxic')),
        'player_charging':       p_pst.get('charging_move'),
        'player_recharge':       bool(p_pst.get('recharge')),
        'player_protected':      bool(p_pst.get('protect')),
        'player_focus_energy':   bool(p_pst.get('focus_energy')),
        'player_ingrain':        bool(p_pst.get('ingrain')),
        'player_rampaging':      bool(p_pst.get('rampage_turns', 0)),
        'player_screens': {
            'light_screen': bs.get('player_light_screen', 0),
            'reflect':      bs.get('player_reflect', 0),
        },

        # ── Stat stages joueur ─────────────────────────────────────────────
        'player_atk_stage':   pp.attack_stage,
        'player_def_stage':   pp.defense_stage,
        'player_spatk_stage': pp.special_attack_stage,
        'player_spdef_stage': pp.special_defense_stage,
        'player_speed_stage': pp.speed_stage,
        'player_acc_stage':   pp.accuracy_stage,
        'player_eva_stage':   pp.evasion_stage,

        # ── États volatils adversaire ──────────────────────────────────────
        'opponent_confused':       bool(o_pst.get('confusion_turns', 0)),
        'opponent_leech_seed':     bool(o_pst.get('leech_seed')),
        'opponent_trapped':        bool(o_pst.get('trap_turns', 0)),
        'opponent_badly_poisoned': bool(o_pst.get('toxic')),
        'opponent_charging':       o_pst.get('charging_move'),
        'opponent_recharge':       bool(o_pst.get('recharge')),
        'opponent_protected':      bool(o_pst.get('protect')),
        'opponent_focus_energy':   bool(o_pst.get('focus_energy')),
        'opponent_ingrain':        bool(o_pst.get('ingrain')),
        'opponent_rampaging':      bool(o_pst.get('rampage_turns', 0)),
        'opponent_screens': {
            'light_screen': bs.get('opponent_light_screen', 0),
            'reflect':      bs.get('opponent_reflect', 0),
        },

        # ── Stat stages adversaire ─────────────────────────────────────────
        'opponent_atk_stage':   opp.attack_stage,
        'opponent_def_stage':   opp.defense_stage,
        'opponent_spatk_stage': opp.special_attack_stage,
        'opponent_spdef_stage': opp.special_defense_stage,
        'opponent_speed_stage': opp.speed_stage,
        'opponent_acc_stage':   opp.accuracy_stage,
        'opponent_eva_stage':   opp.evasion_stage,
    }

    return {
        'success':          True,
        'log':              [],
        'player_pokemon':   player_data,
        'opponent_pokemon': serialize_pokemon(battle.opponent_pokemon),
        # Champs de rétrocompatibilité pour le JS existant
        'player_hp':        pp.current_hp,
        'player_max_hp':    pp.max_hp,
        'opponent_hp':      opp.current_hp,
        'opponent_max_hp':  opp.max_hp,
        'battle_ended':     False,
        # États volatils + stat stages pour le frontend
        'battle_state':     battle_state,
        # Ordre du tour : le frontend l'utilise pour savoir si le second attaquant
        # a réellement agi (skip si K.O. avant son tour)
        'turn_info':        bs.get('last_turn_info', {
            'player_first':   True,
            'second_skipped': False,
        }),
    }