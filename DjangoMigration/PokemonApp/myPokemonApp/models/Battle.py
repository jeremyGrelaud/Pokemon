#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
import random

from .PlayablePokemon import PokemonMoveInstance
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
        """Calcule les dégâts d'une attaque"""
        # Formule Gen 1
        level = attacker.level
        
        if move.category == 'physical':
            attack_stat = attacker.get_effective_attack()
            defense_stat = defender.get_effective_defense()
        else:
            attack_stat = attacker.get_effective_special_attack()
            defense_stat = defender.get_effective_special_defense()
        
        # Dégâts de base
        damage = ((2 * level / 5 + 2) * move.power * attack_stat / defense_stat) / 50 + 2
        
        # STAB (Same Type Attack Bonus)
        if move.type == attacker.species.primary_type or move.type == attacker.species.secondary_type:
            damage *= 1.5
        
        # Efficacité des types
        effectiveness = self.get_type_effectiveness(move.type, defender)
        damage *= effectiveness
        
        # Coup critique (6.25% de chance)
        if random.random() < 0.0625:
            damage *= 2
            self.add_to_log("Coup critique!")
        
        # Variation aléatoire (85% à 100%)
        damage *= random.uniform(0.85, 1.0)
        
        # Brûlure réduit l'attaque physique de moitié
        if attacker.status_condition == 'burn' and move.category == 'physical':
            damage *= 0.5
        
        return int(damage)
    
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
        """Calcule l'XP gagnée après avoir vaincu un Pokémon Formule Gen 1
        """
        # a = 1 si Pokémon sauvage, 1.5 si Pokémon de dresseur
        a = 1.5 if self.battle_type in ['trainer', 'gym', 'elite_four'] else 1.0
        
        # b = base experience du Pokémon vaincu
        b = defeated_pokemon.species.base_experience
        
        # L = niveau du Pokémon vaincu
        L = defeated_pokemon.level
        
        # s = nombre de Pokémon ayant participé (simplifié à 1 pour l'instant)
        s = 1
        
        # Formule: exp = (a * b * L) / (7 * s)
        exp = int((a * b * L) / (7 * s))
        
        return exp
    
    def end_battle(self, winner):
        """Termine le combat.
        XP distribution is generated in BattleViews.py.
        """
        self.winner = winner
        self.is_active = False
        from django.utils import timezone
        self.ended_at = timezone.now()
        self.save()