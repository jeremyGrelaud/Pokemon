#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
import random

from .PlayablePokemon import PokemonMoveInstance
from .PokemonMove import PokemonMove
from .Trainer import Trainer
from .PlayablePokemon import PlayablePokemon
from .Trainer import TrainerInventory

class Battle(models.Model):
    """Représente un combat"""
    
    BATTLE_TYPES = [
        ('wild', 'Pokémon sauvage'),
        ('trainer', 'Dresseur'),
        ('gym', 'Arène'),
        ('elite_four', 'Conseil des 4'),
    ]
    
    battle_type = models.CharField(max_length=20, choices=BATTLE_TYPES)
    
    # Participants
    player_trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='battles_as_player'
    )
    opponent_trainer = models.ForeignKey(
        Trainer,
        on_delete=models.CASCADE,
        related_name='battles_as_opponent',
        null=True,
        blank=True
    )
    
    # Pokémon actuels
    player_pokemon = models.ForeignKey(
        PlayablePokemon,
        on_delete=models.SET_NULL,
        null=True,
        related_name='battles_as_player_pokemon'
    )
    opponent_pokemon = models.ForeignKey(
        PlayablePokemon,
        on_delete=models.SET_NULL,
        null=True,
        related_name='battles_as_opponent_pokemon'
    )
    
    # État du combat
    is_active = models.BooleanField(default=True)
    current_turn = models.IntegerField(default=1)
    winner = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_battles'
    )
    
    # Météo et terrain
    weather = models.CharField(max_length=20, blank=True, null=True)
    terrain = models.CharField(max_length=20, blank=True, null=True)
    
    # Historique
    battle_log = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Combat"
        verbose_name_plural = "Combats"
    
    def __str__(self):
        return f"Combat: {self.player_trainer.username} vs {self.opponent_trainer.username if self.opponent_trainer else 'Sauvage'}"
    
    def add_to_log(self, message):
        """Ajoute un message au log du combat"""
        if not isinstance(self.battle_log, list):
            self.battle_log = []
        self.battle_log.append({
            'turn': self.current_turn,
            'message': message
        })
        self.save()
    

    def execute_turn(self, player_action, opponent_action):
        """Exécute un tour de combat"""
        
        # Vérifier si le joueur tente de fuir
        if player_action.get('type') == 'flee':
            self.execute_action(self.player_pokemon, self.opponent_pokemon, player_action)
            return  # Si fuite réussie, le tour s'arrête ici

        # Vérifier si l'adversaire tente de fuir
        if opponent_action.get('type') == 'flee':
            self.execute_action(self.opponent_pokemon, self.player_pokemon, opponent_action)
            return

        # ============================================================
        # SWITCH a toujours la priorité (avant attaques)
        # ============================================================
        player_is_switching = player_action.get('type') == 'switch'
        opponent_is_switching = opponent_action.get('type') == 'switch'
        
        if player_is_switching:
            new_pokemon = player_action.get('pokemon')
            self.switch_pokemon(self.player_pokemon, new_pokemon)
        
        if opponent_is_switching:
            new_pokemon = opponent_action.get('pokemon')
            self.switch_pokemon(self.opponent_pokemon, new_pokemon)
        
        # Si les deux ont switch, le tour se termine
        if player_is_switching and opponent_is_switching:
            self.current_turn += 1
            self.save()
            return
        
        # Si seulement le joueur a switch, l'adversaire attaque
        if player_is_switching and not opponent_is_switching:
            self.execute_action(self.opponent_pokemon, self.player_pokemon, opponent_action)
            self.current_turn += 1
            self.save()
            return
        
        # Si seulement l'adversaire a switch, le joueur attaque
        if opponent_is_switching and not player_is_switching:
            self.execute_action(self.player_pokemon, self.opponent_pokemon, player_action)
            self.current_turn += 1
            self.save()
            return

        # ============================================================
        # ITEMS (objets, pokeballs) - priorité sur attaques
        # ============================================================
        player_using_item = player_action.get('type') == 'item'
        opponent_using_item = opponent_action.get('type') == 'item'
        
        if player_action.get('type') == 'PokeBall':
            pass # we implemented logic before this call 
        
        if player_using_item:
            item = player_action.get('item')
            target = player_action.get('target')
            # Potion, antidote, etc.
            result = item.use_on_pokemon(target)
            self.add_to_log(result)
        
        if opponent_using_item:
            item = opponent_action.get('item')
            target = opponent_action.get('target')
            result = item.use_on_pokemon(target)
            self.add_to_log(result)
        
        # Si les deux ont utilisé un objet, le tour se termine
        if player_using_item and opponent_using_item:
            self.current_turn += 1
            self.save()
            return
        
        # Si seulement le joueur a utilisé un objet, l'adversaire attaque
        if player_using_item and not opponent_using_item:
            self.execute_action(self.opponent_pokemon, self.player_pokemon, opponent_action)
            self.current_turn += 1
            self.save()
            return
        
        # Si seulement l'adversaire a utilisé un objet, le joueur attaque
        if opponent_using_item and not player_using_item:
            self.execute_action(self.player_pokemon, self.opponent_pokemon, player_action)
            self.current_turn += 1
            self.save()
            return

        # ============================================================
        # ATTAQUES - Déterminer qui attaque en premier par vitesse
        # ============================================================
        player_speed = self.player_pokemon.get_effective_speed()
        opponent_speed = self.opponent_pokemon.get_effective_speed()

        # Prendre en compte la priorité des capacités
        player_priority = player_action.get('move').priority if player_action.get('type') == 'attack' and player_action.get('move') else 0
        opponent_priority = opponent_action.get('move').priority if opponent_action.get('type') == 'attack' and opponent_action.get('move') else 0

        # Déterminer l'ordre des actions
        if player_priority > opponent_priority:
            first, second = (self.player_pokemon, player_action, self.opponent_pokemon), (self.opponent_pokemon, opponent_action, self.player_pokemon)
        elif opponent_priority > player_priority:
            first, second = (self.opponent_pokemon, opponent_action, self.player_pokemon), (self.player_pokemon, player_action, self.opponent_pokemon)
        elif player_speed > opponent_speed:
            first, second = (self.player_pokemon, player_action, self.opponent_pokemon), (self.opponent_pokemon, opponent_action, self.player_pokemon)
        elif opponent_speed > player_speed:
            first, second = (self.opponent_pokemon, opponent_action, self.player_pokemon), (self.player_pokemon, player_action, self.opponent_pokemon)
        else:
            # Même vitesse, aléatoire
            if random.choice([True, False]):
                first, second = (self.player_pokemon, player_action, self.opponent_pokemon), (self.opponent_pokemon, opponent_action, self.player_pokemon)
            else:
                first, second = (self.opponent_pokemon, opponent_action, self.player_pokemon), (self.player_pokemon, player_action, self.opponent_pokemon)

        # Exécuter la première action
        attacker, action, defender = first
        self.execute_action(attacker, defender, action)

        # Vérifier si le défenseur est KO
        if defender.is_fainted():
            self.add_to_log(f"{defender} est K.O.!")
            self.current_turn += 1
            self.save()
            return

        # Exécuter la seconde action
        attacker, action, defender = second
        self.execute_action(attacker, defender, action)

        # Vérifier si le défenseur est KO
        if defender.is_fainted():
            self.add_to_log(f"{defender} est K.O.!")

        self.current_turn += 1
        self.save()


    def execute_action(self, attacker, defender, action):
        """Exécute une action (attaque, changement, objet, fuite)"""

        action_type = action.get('type')
        
        if action_type == 'attack':
            move = action.get('move')
            self.use_move(attacker, defender, move)
        
        elif action_type == 'switch':
            new_pokemon = action.get('pokemon')
            self.switch_pokemon(attacker, new_pokemon)
        
        elif action_type == 'flee':
            self.attempt_flee()
    
    def use_move(self, attacker, defender, move):
        """Utilise une capacité"""
        # Vérifier les PP

        if move.name == "Struggle":
            move_instance, _ = PokemonMoveInstance.objects.get_or_create(
                pokemon=attacker,
                move=move,
                defaults={
                    'current_pp': 99999
                }
            )

        else:
            move_instance = PokemonMoveInstance.objects.get(
                pokemon=attacker,
                move=move
            )
        
        if not move_instance.can_use():
            self.add_to_log(f"{attacker} ne peut pas utiliser {move.name} (plus de PP)!")
            return
        
        # Vérifier le statut
        if attacker.status_condition == 'paralysis' and random.random() < 0.25:
            self.add_to_log(f"{attacker} est paralysé et ne peut pas attaquer!")
            return
        
        if attacker.status_condition == 'freeze' and random.random() < 0.8:
            self.add_to_log(f"{attacker} est gelé et ne peut pas attaquer!")
            return
        
        if attacker.status_condition == 'sleep':
            if attacker.sleep_turns > 0:
                attacker.sleep_turns -= 1
                attacker.save()
                self.add_to_log(f"{attacker} dort profondément...")
                return
            else:
                attacker.status_condition = None
                attacker.save()
                self.add_to_log(f"{attacker} se réveille!")
        
        # Utiliser la capacité
        move_instance.use()
        self.add_to_log(f"{attacker} utilise {move.name}!")
        
        # Vérifier la précision
        if move.accuracy < 100:
            accuracy_modifier = attacker.get_stat_multiplier(attacker.accuracy_stage)
            evasion_modifier = defender.get_stat_multiplier(-defender.evasion_stage)
            hit_chance = move.accuracy * accuracy_modifier * evasion_modifier
            
            if random.randint(1, 100) > hit_chance:
                self.add_to_log(f"L'attaque a raté!")
                return
        
        # Calculer les dégâts
        if move.power > 0:
            damage = self.calculate_damage(attacker, defender, move)
            defender.current_hp = max(0, defender.current_hp - damage)
            defender.save()
            
            self.add_to_log(f"{defender} subit {damage} points de dégâts!")
            
            # Efficacité
            effectiveness = self.get_type_effectiveness(move.type, defender)
            if effectiveness > 1:
                self.add_to_log("C'est super efficace!")
            elif effectiveness < 1 and effectiveness > 0:
                self.add_to_log("Ce n'est pas très efficace...")
            elif effectiveness == 0:
                self.add_to_log("Ça n'a aucun effet...")
        
        # Appliquer les effets
        if move.inflicts_status and random.randint(1, 100) <= move.effect_chance:
            if defender.apply_status(move.inflicts_status):
                self.add_to_log(f"{defender} est {move.inflicts_status}!")
        
        # Modifications de stats
        if move.stat_changes:
            for stat, change in move.stat_changes.items():
                self.modify_stat(attacker, stat, change)
    
    def calculate_damage(self, attacker, defender, move):
        """
        Calcule les dégâts d'une attaque.

        Formule Gen 3+ (base identique Gen 3-9) :
            damage = floor( floor( floor(2*L/5 + 2) * Power * A/D ) / 50 + 2 )
                     × STAB × type_eff × crit × random × burn × ...

        Différences Gen 1 → Gen 6+ appliquées ici :
          - Coup critique : ×1.5 (Gen 6+) au lieu de ×2 (Gen 1-5)
          - Taux crit de base : 1/16 ≈ 6.25% (Gen 3-5) — inchangé
          - Brûlure : ×0.5 sur physique (Gen 1+) — inchangé
          - Aléatoire : 85–100% (Gen 1+) — inchangé
        """
        level = attacker.level

        if move.category == 'physical':
            attack_stat  = attacker.get_effective_attack()
            defense_stat = defender.get_effective_defense()
        else:
            attack_stat  = attacker.get_effective_special_attack()
            defense_stat = defender.get_effective_special_defense()

        # ── Dégâts de base ────────────────────────────────────────────────────
        damage = (((2 * level / 5 + 2) * move.power * attack_stat / defense_stat) / 50) + 2

        # ── STAB ──────────────────────────────────────────────────────────────
        if (move.type == attacker.species.primary_type or
                move.type == attacker.species.secondary_type):
            damage *= 1.5

        # ── Efficacité des types ───────────────────────────────────────────────
        effectiveness = self.get_type_effectiveness(move.type, defender)
        damage *= effectiveness

        # ── Coup critique (Gen 6+ : ×1.5) ─────────────────────────────────────
        # Taux de base : 1/16 ≈ 6.25 %
        is_critical = random.random() < (1 / 16)
        if is_critical:
            damage *= 1.5
            self.add_to_log("Coup critique !")

        # ── Variation aléatoire 85–100 % ──────────────────────────────────────
        damage *= random.uniform(0.85, 1.0)

        # ── Brûlure : ×0.5 sur les coups physiques ────────────────────────────
        if attacker.status_condition == 'burn' and move.category == 'physical':
            damage *= 0.5

        # ── Garantir au moins 1 dégât si le move a de la puissance ────────────
        result = int(damage)
        if move.power > 0 and result < 1:
            result = 1

        return result
    
    def get_type_effectiveness(self, attack_type, defender):
        """Calcule l'efficacité du type d'attaque"""
        effectiveness = 1.0
        
        # Type primaire
        effectiveness *= attack_type.get_effectiveness(defender.species.primary_type)
        
        # Type secondaire
        if defender.species.secondary_type:
            effectiveness *= attack_type.get_effectiveness(defender.species.secondary_type)
        
        return effectiveness
    
    def modify_stat(self, pokemon, stat_name, stages):
        """Modifie une stat de combat"""
        current_stage = getattr(pokemon, f"{stat_name}_stage")
        new_stage = max(-6, min(6, current_stage + stages))
        setattr(pokemon, f"{stat_name}_stage", new_stage)
        pokemon.save()
        
        if stages > 0:
            self.add_to_log(f"L'{stat_name} de {pokemon} augmente!")
        else:
            self.add_to_log(f"L'{stat_name} de {pokemon} diminue!")
    
    def switch_pokemon(self, trainer_pokemon, new_pokemon):
        """Change de Pokémon"""
        if trainer_pokemon == self.player_pokemon:
            self.player_pokemon = new_pokemon
        else:
            self.opponent_pokemon = new_pokemon
        
        self.save()
        self.add_to_log(f"{new_pokemon} entre en combat!")
    
    def use_item(self, item, target_pokemon):
        """Utilise un objet"""
        result = item.use_on_pokemon(target_pokemon)
        self.add_to_log(result)
    
    def attempt_flee(self):
        """Tente de fuir le combat"""
        if self.battle_type == 'wild':
            # Formule de fuite Gen 1
            player_speed = self.player_pokemon.get_effective_speed()
            opponent_speed = self.opponent_pokemon.get_effective_speed()
            
            odds = (player_speed * 32) / (opponent_speed % 256) + 30 * self.current_turn
            
            if random.randint(0, 255) < odds:
                self.add_to_log("Fuite réussie!")
                self.is_active = False
                self.save()
                #self.end_battle(winner=self.opponent_trainer)
                return True
            else:
                self.add_to_log("Echec dans la fuite !")
                return False
        else:
            self.add_to_log("On ne peut pas fuir un combat de dresseur!")
            return False
    

    def calculate_exp_reward(self, defeated_pokemon):
        """
        Calcule l'XP gagnée après avoir vaincu un Pokémon.

        Formule Gen 5+ (Noire/Blanche → présent) :
            exp = round( (b × Lf / 5) × √((2×Lf + 10)³ / (Lf + Lp + 10)³) + 1 ) × t

        Où :
          b  = base_experience du Pokémon vaincu
          Lf = niveau du Pokémon vaincu
          Lp = niveau du Pokémon vainqueur
          t  = 1.5 si combat de dresseur, 1.0 si Pokémon sauvage

        L'écart de niveau est intégré : battre un Pokémon plus fort rapporte
        plus d'XP, battre un Pokémon bien plus faible rapporte très peu.
        """
        b  = defeated_pokemon.species.base_experience or 64
        Lf = defeated_pokemon.level
        Lp = self.player_pokemon.level
        t  = 1.5 if self.battle_type in ('trainer', 'gym', 'elite_four') else 1.0

        numerator   = (2 * Lf + 10) ** 3
        denominator = (Lf + Lp + 10) ** 3
        level_factor = (numerator / denominator) ** 0.5   # racine cubique = **0.5 non — c'est **0.5 sur le rapport de cubes = (**1.5) sur le ratio

        # Formule exacte : √( ratio³ ) = ratio^1.5, mais on applique:
        # level_factor = ((2*Lf+10)/(Lf+Lp+10))^2.5 (approximation de Bulbapedia)
        ratio = (2 * Lf + 10) / (Lf + Lp + 10)
        level_factor = ratio ** 2.5

        exp = round((b * Lf / 5) * level_factor + 1) * t
        return max(1, int(exp))

    def grant_ev_gains(self, defeated_pokemon):
        """
        Accorde les EV (Effort Values) au Pokémon vainqueur après le combat.

        Chaque Pokémon vaincue accorde des EVs dans certaines stats selon
        son espèce. Limites Gen 3+ : 252 EVs par stat, 510 EVs au total.
        """
        # Table EV simplifiée Gen 3 (stat → EV accordés)
        EV_YIELDS = {
            # (stat_name, valeur)
            'Bulbasaur':   [('ev_special_attack', 1)],
            'Ivysaur':     [('ev_special_attack', 1), ('ev_special_defense', 1)],
            'Venusaur':    [('ev_special_attack', 2), ('ev_special_defense', 1)],
            'Charmander':  [('ev_speed', 1)],
            'Charmeleon':  [('ev_speed', 1), ('ev_attack', 1)],
            'Charizard':   [('ev_speed', 3)],
            'Squirtle':    [('ev_defense', 1)],
            'Wartortle':   [('ev_defense', 1), ('ev_special_defense', 1)],
            'Blastoise':   [('ev_defense', 1), ('ev_special_defense', 2)],
            'Caterpie':    [('ev_hp', 1)],
            'Metapod':     [('ev_defense', 1)],
            'Butterfree':  [('ev_special_attack', 2), ('ev_special_defense', 1)],
            'Weedle':      [('ev_speed', 1)],
            'Kakuna':      [('ev_defense', 1)],
            'Beedrill':    [('ev_attack', 2), ('ev_speed', 1)],
            'Pidgey':      [('ev_speed', 1)],
            'Pidgeotto':   [('ev_speed', 1), ('ev_attack', 1)],
            'Pidgeot':     [('ev_speed', 3)],
            'Rattata':     [('ev_speed', 1)],
            'Raticate':    [('ev_speed', 2)],
            'Spearow':     [('ev_speed', 1)],
            'Fearow':      [('ev_speed', 2)],
            'Ekans':       [('ev_attack', 1)],
            'Arbok':       [('ev_attack', 2)],
            'Pikachu':     [('ev_speed', 2)],
            'Raichu':      [('ev_speed', 3)],
            'Sandshrew':   [('ev_defense', 1)],
            'Sandslash':   [('ev_defense', 2)],
            'Nidoran♀':   [('ev_hp', 1)],
            'Nidorina':    [('ev_hp', 2)],
            'Nidoqueen':   [('ev_hp', 3)],
            'Nidoran♂':   [('ev_attack', 1)],
            'Nidorino':    [('ev_attack', 2)],
            'Nidoking':    [('ev_attack', 3)],
            'Clefairy':    [('ev_hp', 2)],
            'Clefable':    [('ev_hp', 3)],
            'Vulpix':      [('ev_special_attack', 1)],
            'Ninetales':   [('ev_special_attack', 2), ('ev_speed', 1)],
            'Jigglypuff':  [('ev_hp', 2)],
            'Wigglytuff':  [('ev_hp', 3)],
            'Zubat':       [('ev_speed', 1)],
            'Golbat':      [('ev_speed', 2)],
            'Oddish':      [('ev_special_attack', 1)],
            'Gloom':       [('ev_special_attack', 1), ('ev_special_defense', 1)],
            'Vileplume':   [('ev_special_attack', 2), ('ev_special_defense', 1)],
            'Paras':       [('ev_attack', 1)],
            'Parasect':    [('ev_attack', 2), ('ev_defense', 1)],
            'Venonat':     [('ev_special_defense', 1)],
            'Venomoth':    [('ev_special_attack', 2), ('ev_special_defense', 1)],
            'Diglett':     [('ev_speed', 1)],
            'Dugtrio':     [('ev_speed', 2)],
            'Meowth':      [('ev_speed', 1)],
            'Persian':     [('ev_speed', 2)],
            'Psyduck':     [('ev_special_attack', 1)],
            'Golduck':     [('ev_special_attack', 2)],
            'Mankey':      [('ev_attack', 1)],
            'Primeape':    [('ev_attack', 2)],
            'Growlithe':   [('ev_attack', 1)],
            'Arcanine':    [('ev_attack', 2), ('ev_speed', 1)],
            'Poliwag':     [('ev_speed', 1)],
            'Poliwhirl':   [('ev_speed', 2)],
            'Poliwrath':   [('ev_defense', 1), ('ev_special_defense', 1)],
            'Abra':        [('ev_special_attack', 1)],
            'Kadabra':     [('ev_special_attack', 2)],
            'Alakazam':    [('ev_special_attack', 3)],
            'Machop':      [('ev_attack', 1)],
            'Machoke':     [('ev_attack', 2)],
            'Machamp':     [('ev_attack', 3)],
            'Bellsprout':  [('ev_attack', 1)],
            'Weepinbell':  [('ev_attack', 2)],
            'Victreebel':  [('ev_attack', 3)],
            'Tentacool':   [('ev_special_defense', 1)],
            'Tentacruel':  [('ev_special_defense', 2)],
            'Geodude':     [('ev_defense', 1)],
            'Graveler':    [('ev_defense', 2)],
            'Golem':       [('ev_defense', 3)],
            'Ponyta':      [('ev_speed', 1)],
            'Rapidash':    [('ev_speed', 2)],
            'Slowpoke':    [('ev_hp', 1)],
            'Slowbro':     [('ev_defense', 1), ('ev_special_attack', 1)],
            'Magnemite':   [('ev_special_attack', 1)],
            'Magneton':    [('ev_special_attack', 2)],
            'Doduo':       [('ev_attack', 1)],
            'Dodrio':      [('ev_attack', 2)],
            'Seel':        [('ev_special_defense', 1)],
            'Dewgong':     [('ev_special_defense', 2)],
            'Grimer':      [('ev_hp', 1)],
            'Muk':         [('ev_hp', 2)],
            'Shellder':    [('ev_defense', 1)],
            'Cloyster':    [('ev_defense', 2)],
            'Gastly':      [('ev_special_attack', 1)],
            'Haunter':     [('ev_special_attack', 2)],
            'Gengar':      [('ev_special_attack', 3)],
            'Onix':        [('ev_defense', 1)],
            'Drowzee':     [('ev_special_defense', 1)],
            'Hypno':       [('ev_special_defense', 2)],
            'Krabby':      [('ev_attack', 1)],
            'Kingler':     [('ev_attack', 2)],
            'Voltorb':     [('ev_speed', 1)],
            'Electrode':   [('ev_speed', 2)],
            'Exeggcute':   [('ev_special_attack', 1)],
            'Exeggutor':   [('ev_special_attack', 2)],
            'Cubone':      [('ev_defense', 1)],
            'Marowak':     [('ev_defense', 2)],
            'Hitmonlee':   [('ev_attack', 2)],
            'Hitmonchan':  [('ev_special_defense', 2)],
            'Lickitung':   [('ev_hp', 1)],
            'Koffing':     [('ev_defense', 1)],
            'Weezing':     [('ev_defense', 2)],
            'Rhyhorn':     [('ev_defense', 1)],
            'Rhydon':      [('ev_attack', 2)],
            'Chansey':     [('ev_hp', 2)],
            'Tangela':     [('ev_defense', 1)],
            'Kangaskhan':  [('ev_hp', 2)],
            'Horsea':      [('ev_special_attack', 1)],
            'Seadra':      [('ev_special_attack', 2)],
            'Goldeen':     [('ev_attack', 1)],
            'Seaking':     [('ev_attack', 2)],
            'Staryu':      [('ev_speed', 1)],
            'Starmie':     [('ev_speed', 2)],
            'Mr. Mime':    [('ev_special_defense', 2)],
            'Scyther':     [('ev_attack', 1), ('ev_speed', 1)],
            'Jynx':        [('ev_special_attack', 2)],
            'Electabuzz':  [('ev_special_attack', 2)],
            'Magmar':      [('ev_special_attack', 2)],
            'Pinsir':      [('ev_attack', 2)],
            'Tauros':      [('ev_attack', 1), ('ev_speed', 1)],
            'Magikarp':    [('ev_speed', 1)],
            'Gyarados':    [('ev_attack', 2)],
            'Lapras':      [('ev_hp', 2)],
            'Ditto':       [('ev_hp', 1)],
            'Eevee':       [('ev_hp', 1)],
            'Vaporeon':    [('ev_hp', 2)],
            'Jolteon':     [('ev_speed', 2)],
            'Flareon':     [('ev_attack', 2)],
            'Porygon':     [('ev_special_attack', 1)],
            'Omanyte':     [('ev_defense', 1)],
            'Omastar':     [('ev_defense', 1), ('ev_special_attack', 1)],
            'Kabuto':      [('ev_defense', 1)],
            'Kabutops':    [('ev_attack', 2)],
            'Aerodactyl':  [('ev_speed', 2)],
            'Snorlax':     [('ev_hp', 2)],
            'Articuno':    [('ev_special_defense', 3)],
            'Zapdos':      [('ev_special_attack', 3)],
            'Moltres':     [('ev_special_attack', 3)],
            'Dratini':     [('ev_attack', 1)],
            'Dragonair':   [('ev_attack', 2)],
            'Dragonite':   [('ev_attack', 3)],
            'Mewtwo':      [('ev_special_attack', 3)],
            'Mew':         [('ev_hp', 3)],
        }

        EV_CAP_PER_STAT = 252
        EV_TOTAL_CAP    = 510

        winner = self.player_pokemon
        species_name = defeated_pokemon.species.name
        yields = EV_YIELDS.get(species_name, [('ev_hp', 1)])

        # Total EVs actuels du vainqueur
        current_total = (
            winner.ev_hp + winner.ev_attack + winner.ev_defense +
            winner.ev_special_attack + winner.ev_special_defense + winner.ev_speed
        )

        for stat_field, amount in yields:
            if current_total >= EV_TOTAL_CAP:
                break
            current_val = getattr(winner, stat_field)
            gain = min(amount, EV_CAP_PER_STAT - current_val, EV_TOTAL_CAP - current_total)
            if gain > 0:
                setattr(winner, stat_field, current_val + gain)
                current_total += gain

        winner.save()
    
    # =========================================================================
    # IA ADVERSAIRE
    # =========================================================================

    def choose_enemy_move(self, attacker, defender):
        """
        Sélectionne intelligemment le move de l'ennemi via un système de scoring.
        Tient compte de : l'efficacité des types, le STAB, la puissance, les KO
        potentiels, les soins si en danger, les statuts, et une légère dose
        d'aléatoire pour ne pas être trop prévisible.

        Retourne un dict d'action {'type': 'attack', 'move': <PokemonMove>}.
        """
        from .PlayablePokemon import PokemonMoveInstance

        # Récupérer les moves avec PP restants
        move_instances = PokemonMoveInstance.objects.filter(
            pokemon=attacker, current_pp__gt=0
        ).select_related('move', 'move__type')

        available_moves = [mi.move for mi in move_instances]

        # Fallback sur Struggle si aucun move dispo
        if not available_moves:
            struggle = PokemonMove.objects.filter(name__iexact='Struggle').first()
            if struggle:
                return {'type': 'attack', 'move': struggle}
            return None

        best_move  = None
        best_score = -9999

        for move in available_moves:
            score = self._score_enemy_move(move, attacker, defender)
            if score > best_score:
                best_score = score
                best_move  = move

        return {'type': 'attack', 'move': best_move}

    def _score_enemy_move(self, move, attacker, defender):
        """
        Calcule un score de pertinence pour un move donné.
        Retourne un float : plus il est élevé, plus le move est intéressant.
        """
        score = 0.0

        # ── 1. Efficacité de type ──────────────────────────────────────────
        type_mult = self.get_type_effectiveness(move.type, defender)
        if type_mult >= 2.0:
            score += 80    # Super efficace
        elif type_mult > 1.0:
            score += 40
        elif type_mult == 0:
            score -= 200   # Immunité → à éviter absolument
        elif type_mult < 1.0:
            score -= 30    # Pas très efficace

        # ── 2. STAB ───────────────────────────────────────────────────────
        attacker_types = [attacker.species.primary_type, attacker.species.secondary_type]
        if move.type in attacker_types:
            score += 20

        # ── 3. Puissance de base ──────────────────────────────────────────
        if move.power and move.power > 0:
            score += move.power * 0.25

        # ── 4. Précision ──────────────────────────────────────────────────
        accuracy = move.accuracy if move.accuracy else 100
        score *= (accuracy / 100.0)

        # ── 5. KO potentiel (priorité absolue) ───────────────────────────
        if move.power and move.power > 0:
            estimated = self._estimate_enemy_damage(move, attacker, defender)
            if estimated >= defender.current_hp:
                score += 200   # KO garanti → on le fait toujours
            elif estimated >= defender.current_hp * 0.75:
                score += 50    # Presque KO

        # ── 6. Moves de statut ────────────────────────────────────────────
        if not move.power or move.power == 0:
            if move.inflicts_status:
                if not defender.status_condition:
                    score += 30   # Infliger un statut a de la valeur
                else:
                    score -= 40   # Inutile si déjà statué
            elif move.stat_changes:
                # Boost de stats utile en début de combat
                hp_ratio_enemy = attacker.current_hp / max(attacker.max_hp, 1)
                if hp_ratio_enemy > 0.6:
                    score += 20
                else:
                    score -= 10   # Trop tard pour booster
            else:
                score -= 20   # Move de statut sans effet clair

        # ── 7. Moves de soin ──────────────────────────────────────────────
        if hasattr(move, 'healing') and move.healing and move.healing > 0:
            hp_ratio = attacker.current_hp / max(attacker.max_hp, 1)
            if hp_ratio < 0.3:
                score += 120   # Critique → se soigner d'urgence
            elif hp_ratio < 0.5:
                score += 50
            elif hp_ratio < 0.7:
                score += 10
            else:
                score -= 30    # HP OK, inutile de se soigner

        # ── 8. Moves prioritaires (Quick Attack etc.) ─────────────────────
        if hasattr(move, 'priority') and move.priority and move.priority > 0:
            if defender.current_hp <= attacker.current_hp * 0.4:
                score += 25   # Finir un ennemi affaibli

        # ── 9. Légère dose d'aléatoire (anti-prévisibilité) ──────────────
        score += random.uniform(0, 8)

        return score

    def _estimate_enemy_damage(self, move, attacker, defender):
        """
        Estimation rapide des dégâts sans les effets aléatoires de calculate_damage.
        Sert uniquement à détecter les KO potentiels pour le scoring IA.
        """
        if not move.power or move.power == 0:
            return 0

        if move.category == 'physical':
            atk_stat = attacker.get_effective_attack()
            def_stat = defender.get_effective_defense()
        else:
            atk_stat = attacker.get_effective_special_attack()
            def_stat = defender.get_effective_special_defense()

        if def_stat == 0:
            def_stat = 1

        base   = ((2 * attacker.level / 5 + 2) * move.power * atk_stat / def_stat) / 50 + 2
        mult   = self.get_type_effectiveness(move.type, defender)

        # STAB
        attacker_types = [attacker.species.primary_type, attacker.species.secondary_type]
        if move.type in attacker_types:
            base *= 1.5

        return int(base * mult * 0.925)   # 0.925 ≈ moyenne de la variation aléatoire

    def end_battle(self, winner):
        """Termine le combat.
        XP distribution is generated in BattleViews.py.
        """
        self.winner = winner
        self.is_active = False
        from django.utils import timezone
        self.ended_at = timezone.now()
        self.save()