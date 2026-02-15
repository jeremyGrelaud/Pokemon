#!/usr/bin/python3
"""
GUIDE DE MIGRATION ET EXEMPLES D'USAGE
Migration depuis l'ancienne version vers la nouvelle architecture
"""

# ============================================================================
# MIGRATION DEPUIS L'ANCIENNE ARCHITECTURE
# ============================================================================

"""
CHANGEMENTS PRINCIPAUX:

1. Pokemon -> Séparation en Pokemon (template) et PlayablePokemon (instance)
2. Trainer -> Ajout de types (player, gym_leader, etc.)
3. Ajout de Battle pour gérer les combats
4. Ajout de Item pour les objets
5. Amélioration du système de stats (IVs, EVs, Nature, Stages)

ÉTAPES DE MIGRATION:

1. Sauvegarder vos données existantes
2. Créer les nouveaux modèles
3. Migrer les données
4. Mettre à jour votre code
"""

# ============================================================================
# EXEMPLE 1: CRÉER UN NOUVEAU JEU
# ============================================================================

def example_new_game():
    """Démarre une nouvelle partie"""
    from myPokemonApp.models import Trainer, Pokemon
    from myPokemonApp.gameUtils import create_starter_pokemon, give_item_to_trainer
    from myPokemonApp.models import Item
    
    # 1. Créer le joueur
    player = Trainer.objects.create(
        username=input("Entrez votre nom: "),
        trainer_type='player',
        money=3000,
        location='Pallet Town',
        badges=0
    )
    
    # 2. Choisir le starter
    print("\nChoisissez votre Pokémon de départ:")
    print("1. Bulbasaur (Plante)")
    print("2. Charmander (Feu)")
    print("3. Squirtle (Eau)")
    
    choice = input("Votre choix (1-3): ")
    
    starter_map = {
        '1': 'Bulbasaur',
        '2': 'Charmander',
        '3': 'Squirtle'
    }
    
    starter_species = Pokemon.objects.get(name=starter_map[choice])
    nickname = input(f"Donnez un surnom à votre {starter_species.name} (ou Entrée pour garder le nom): ")
    
    starter = create_starter_pokemon(
        species=starter_species,
        trainer=player,
        nickname=nickname if nickname else None
    )
    
    print(f"\nVous avez choisi {starter}!")
    
    # 3. Donner les objets de départ
    give_item_to_trainer(player, Item.objects.get(name='Poké Ball'), 5)
    give_item_to_trainer(player, Item.objects.get(name='Potion'), 3)
    
    print("\nVotre aventure commence!")
    print(f"Vous avez reçu 5 Poké Balls et 3 Potions!")
    
    return player


# ============================================================================
# EXEMPLE 2: SYSTÈME DE RENCONTRE ALÉATOIRE
# ============================================================================

def example_random_encounter(player, location='Route 1'):
    """Système de rencontre aléatoire de Pokémon sauvages"""
    import random
    from myPokemonApp.models import Pokemon
    from myPokemonApp.gameUtils import create_wild_pokemon, start_battle
    
    # Définir les Pokémon disponibles par zone
    pokemon_by_location = {
        'Route 1': [
            ('Pidgey', 2, 5),
            ('Rattata', 2, 5),
        ],
        'Viridian Forest': [
            ('Caterpie', 3, 6),
            ('Weedle', 3, 6),
            ('Pidgey', 3, 5),
            ('Pikachu', 3, 5),  # Rare
        ],
        'Route 4': [
            ('Spearow', 6, 11),
            ('Ekans', 6, 11),
            ('Sandshrew', 6, 11),
        ]
    }
    
    # Choisir un Pokémon aléatoire
    available = pokemon_by_location.get(location, [])
    if not available:
        print(f"Pas de Pokémon dans {location}")
        return None
    
    pokemon_name, min_level, max_level = random.choice(available)
    level = random.randint(min_level, max_level)
    
    # Créer le Pokémon sauvage
    species = Pokemon.objects.get(name=pokemon_name)
    wild_pokemon = create_wild_pokemon(species, level, location)
    
    # Démarrer le combat
    battle, message = start_battle(player, wild_pokemon=wild_pokemon)
    
    print("\n" + "="*50)
    print(message)
    print("="*50)
    
    return battle


# ============================================================================
# EXEMPLE 3: BOUCLE DE COMBAT COMPLÈTE
# ============================================================================

def example_battle_loop(battle):
    """Boucle de combat interactive complète"""
    from myPokemonApp.models import Item
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
    from myPokemonApp.gameUtils import (
        ai_choose_action, 
        check_battle_end,
        use_item_in_battle
    )
    
    while battle.is_active:
        print("\n" + "-"*50)
        print(f"Tour {battle.current_turn}")
        print("-"*50)
        
        # Afficher l'état des Pokémon
        player_poke = battle.player_pokemon
        opponent_poke = battle.opponent_pokemon
        
        print(f"\nVotre {player_poke.species.name}: {player_poke.current_hp}/{player_poke.max_hp} HP")
        if player_poke.status_condition:
            print(f"  Statut: {player_poke.status_condition}")
        
        print(f"Adversaire {opponent_poke.species.name}: {opponent_poke.current_hp}/{opponent_poke.max_hp} HP")
        if opponent_poke.status_condition:
            print(f"  Statut: {opponent_poke.status_condition}")
        
        # Menu d'action
        print("\nQue voulez-vous faire?")
        print("1. Combattre")
        print("2. Sac")
        print("3. Pokémon")
        print("4. Fuir")
        
        choice = input("\nVotre choix: ")
        
        # ACTION DU JOUEUR
        if choice == '1':  # Combattre
            # Choisir une attaque
            moves = PokemonMoveInstance.objects.filter(
                pokemon=player_poke,
                current_pp__gt=0
            )
            
            if not moves.exists():
                print("Aucune attaque disponible!")
                continue
            
            print("\nChoisissez une attaque:")
            for i, move_inst in enumerate(moves, 1):
                move = move_inst.move
                print(f"{i}. {move.name} ({move_inst.current_pp}/{move.pp} PP) - Puissance: {move.power}")
            
            move_choice = int(input("\nVotre choix: ")) - 1
            selected_move = list(moves)[move_choice]
            
            player_action = {
                'type': 'attack',
                'move': selected_move.move
            }
        
        elif choice == '2':  # Sac
            # Afficher l'inventaire
            from myPokemonApp.models import TrainerInventory
            
            inventory = TrainerInventory.objects.filter(
                trainer=battle.player_trainer,
                quantity__gt=0
            )
            
            if not inventory.exists():
                print("Votre sac est vide!")
                continue
            
            print("\nInventaire:")
            for i, inv_item in enumerate(inventory, 1):
                print(f"{i}. {inv_item.item.name} x{inv_item.quantity}")
            
            item_choice = int(input("\nChoisir un objet (0 pour annuler): "))
            if item_choice == 0:
                continue
            
            selected_inv = list(inventory)[item_choice - 1]
            item = selected_inv.item
            
            # Utiliser l'objet
            if item.item_type == 'pokeball':
                success, msg = use_item_in_battle(item, opponent_poke, battle)
                print(msg)
                if success and not battle.is_active:
                    break
                player_action = {'type': 'item', 'item': item, 'target': opponent_poke}
            else:
                # Choisir la cible
                result = item.use_on_pokemon(player_poke)
                print(result)
                player_action = {'type': 'item', 'item': item, 'target': player_poke}
            
            # Réduire l'inventaire
            from myPokemonApp.gameUtils import remove_item_from_trainer
            remove_item_from_trainer(battle.player_trainer, item, 1)
        
        elif choice == '3':  # Pokémon
            # Changer de Pokémon
            available_pokemon = battle.player_trainer.pokemon_team.filter(
                is_in_party=True,
                current_hp__gt=0
            ).exclude(id=player_poke.id)
            
            if not available_pokemon.exists():
                print("Aucun autre Pokémon disponible!")
                continue
            
            print("\nChoisir un Pokémon:")
            for i, poke in enumerate(available_pokemon, 1):
                print(f"{i}. {poke} - {poke.current_hp}/{poke.max_hp} HP")
            
            poke_choice = int(input("\nVotre choix (0 pour annuler): "))
            if poke_choice == 0:
                continue
            
            new_pokemon = list(available_pokemon)[poke_choice - 1]
            player_action = {'type': 'switch', 'pokemon': new_pokemon}
        
        elif choice == '4':  # Fuir
            player_action = {'type': 'flee'}
        
        else:
            print("Choix invalide!")
            continue
        
        # ACTION DE L'ADVERSAIRE
        opponent_action = ai_choose_action(opponent_poke, player_poke, battle)
        
        # EXÉCUTER LE TOUR
        battle.execute_turn(player_action, opponent_action)
        
        # Afficher le log du dernier tour
        if battle.battle_log:
            print("\n--- Combat ---")
            for entry in battle.battle_log[-5:]:  # Derniers 5 messages
                if entry['turn'] == battle.current_turn:
                    print(entry['message'])
        
        # VÉRIFIER LA FIN DU COMBAT
        is_ended, winner, message = check_battle_end(battle)
        if is_ended:
            print("\n" + "="*50)
            print(message)
            print("="*50)
            break
    
    return battle


# ============================================================================
# EXEMPLE 4: PARCOURS D'UNE ROUTE
# ============================================================================

def example_route_journey(player, route_name='Route 1'):
    """Simulation de parcours d'une route avec rencontres et dresseurs"""
    import random
    from myPokemonApp.models import Trainer
    from myPokemonApp.gameUtils import start_battle, heal_team
    
    print(f"\n=== Bienvenue sur {route_name}! ===\n")
    
    # Dresseurs sur la route
    trainers = Trainer.objects.filter(
        location=route_name,
        trainer_type='trainer',
        is_defeated=False
    )
    
    steps = 0
    max_steps = 100
    
    while steps < max_steps:
        steps += 1
        
        # 20% de chance de rencontre à chaque pas
        if random.random() < 0.2:
            print(f"\n[Pas {steps}] Quelque chose bouge dans les hautes herbes!")
            
            # 70% Pokémon sauvage, 30% dresseur
            if random.random() < 0.7 or not trainers.exists():
                # Pokémon sauvage
                battle = example_random_encounter(player, route_name)
                if battle:
                    example_battle_loop(battle)
                    
                    # Proposer de continuer
                    choice = input("\nContinuer? (o/n): ")
                    if choice.lower() != 'o':
                        break
            else:
                # Dresseur
                trainer = random.choice(list(trainers))
                print(f"\n{trainer.intro_text}")
                
                battle, _ = start_battle(player, trainer, battle_type='trainer')
                example_battle_loop(battle)
                
                # Le dresseur est vaincu
                if battle.winner == player:
                    trainer.is_defeated = True
                    trainer.save()
                
                choice = input("\nContinuer? (o/n): ")
                if choice.lower() != 'o':
                    break
        
        # Sortir de la route
        if steps % 20 == 0:
            print(f"\n[Pas {steps}] Vous apercevez la sortie de {route_name}...")
            choice = input("Continuer ou sortir? (c/s): ")
            if choice.lower() == 's':
                break
    
    print(f"\nVous quittez {route_name}.")
    
    # Proposer de soigner
    print("\nVous arrivez à un Centre Pokémon!")
    choice = input("Soigner votre équipe? (o/n): ")
    if choice.lower() == 'o':
        heal_team(player)
        print("Votre équipe est complètement soignée!")


# ============================================================================
# EXEMPLE 5: DÉFI D'ARÈNE COMPLET
# ============================================================================

def example_gym_challenge(player, gym_city='Pewter City'):
    """Défi complet d'une arène"""
    from myPokemonApp.models.Trainer import GymLeader
    from myPokemonApp.gameUtils import start_battle, heal_team
    
    # Récupérer le champion
    gym = GymLeader.objects.get(gym_city=gym_city)
    gym_leader = gym.trainer
    
    print("\n" + "="*60)
    print(f"ARÈNE DE {gym_city.upper()}")
    print(f"Champion: {gym_leader.username}")
    print(f"Spécialité: {gym.specialty_type.name.upper()}")
    print(f"Badge: {gym.badge_name}")
    print("="*60)
    
    # Vérifier que le joueur a assez de badges
    required_badges = gym.badge_order - 1
    if player.badges < required_badges:
        print(f"\nVous avez besoin de {required_badges} badge(s) pour défier cette arène!")
        print(f"Vous n'en avez que {player.badges}.")
        return False
    
    # Dialogue d'introduction
    print(f"\n{gym_leader.intro_text}")
    
    # Vérifier si le joueur veut combattre
    choice = input("\nAccepter le défi? (o/n): ")
    if choice.lower() != 'o':
        print("Vous quittez l'arène...")
        return False
    
    # COMBAT!
    battle, _ = start_battle(player, gym_leader, battle_type='gym')
    example_battle_loop(battle)
    
    # Résultat
    if battle.winner == player:
        print("\n" + "="*60)
        print(f"{gym_leader.defeat_text}")
        print(f"\nVous avez gagné le {gym.badge_name}!")
        print("="*60)
        
        # Donner le badge
        player.badges += 1
        player.save()
        
        # CT en récompense
        if gym.tm_reward:
            print(f"Vous avez également reçu la CT {gym.tm_reward.name}!")
        
        return True
    else:
        print("\n" + "="*60)
        print(f"{gym_leader.victory_text}")
        print("\nVous avez perdu...")
        print("="*60)
        
        # Téléportation au Centre Pokémon
        print("\nVous vous réveillez au Centre Pokémon...")
        heal_team(player)
        
        return False


# ============================================================================
# EXEMPLE 6: SYSTÈME DE CAPTURE AVANCÉ
# ============================================================================

def example_advanced_catching(player, wild_pokemon, battle):
    """Système de capture avec stratégie"""
    from myPokemonApp.models import Item
    from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
    from myPokemonApp.gameUtils import catch_pokemon, use_item_in_battle
    
    print("\n=== GUIDE DE CAPTURE ===")
    print(f"Pokémon cible: {wild_pokemon.species.name}")
    print(f"HP: {wild_pokemon.current_hp}/{wild_pokemon.max_hp}")
    print(f"Statut: {wild_pokemon.status_condition or 'Aucun'}")
    print(f"Taux de capture: {wild_pokemon.species.catch_rate}")
    
    # Calculer les chances de capture
    hp_factor = wild_pokemon.current_hp / wild_pokemon.max_hp
    
    print("\n=== CONSEILS ===")
    if hp_factor > 0.5:
        print("⚠️  HP élevés - Affaiblissez davantage le Pokémon!")
    elif hp_factor > 0.2:
        print("✓ HP corrects - Bonnes chances de capture")
    else:
        print("✓✓ HP très bas - Excellentes chances!")
    
    if not wild_pokemon.status_condition:
        print("💡 Infligez un statut (sommeil ou paralysie) pour augmenter vos chances!")
    else:
        print(f"✓ Statut {wild_pokemon.status_condition} actif - Bonus de capture!")
    
    # Choisir la Poké Ball
    from myPokemonApp.models import TrainerInventory
    
    pokeballs = TrainerInventory.objects.filter(
        trainer=player,
        item__item_type='pokeball',
        quantity__gt=0
    )
    
    if not pokeballs.exists():
        print("\n❌ Vous n'avez plus de Poké Balls!")
        return False
    
    print("\n=== VOS POKÉ BALLS ===")
    for i, inv in enumerate(pokeballs, 1):
        ball = inv.item
        print(f"{i}. {ball.name} x{inv.quantity} (Bonus x{ball.catch_rate_modifier})")
    
    choice = int(input("\nChoisir une Ball: ")) - 1
    selected_ball = list(pokeballs)[choice].item
    
    # Tenter la capture
    print(f"\nVous lancez une {selected_ball.name}!")
    success, message = catch_pokemon(wild_pokemon, player, selected_ball)
    
    # Animation de capture (simulation)
    import time
    for i in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print()
    
    print(message)
    
    if success:
        print(f"\n🎉 {wild_pokemon.species.name} a été capturé!")
        
        # Donner un surnom?
        nickname = input(f"Donner un surnom à {wild_pokemon.species.name}? (Entrée pour passer): ")
        if nickname:
            wild_pokemon.nickname = nickname
            wild_pokemon.save()
            print(f"{wild_pokemon.species.name} s'appelle maintenant {nickname}!")
        
        return True
    
    return False


# ============================================================================
# EXEMPLE 7: GESTION D'ÉQUIPE AVANCÉE
# ============================================================================

def example_team_management(player):
    """Menu de gestion d'équipe"""
    from myPokemonApp.gameUtils import (
        organize_party,
        deposit_pokemon,
        withdraw_pokemon
    )
    
    while True:
        print("\n" + "="*50)
        print("GESTION D'ÉQUIPE")
        print("="*50)
        
        # Afficher l'équipe actuelle
        party = player.pokemon_team.filter(is_in_party=True).order_by('party_position')
        pc_pokemon = player.pokemon_team.filter(is_in_party=False)
        
        print("\n=== ÉQUIPE ACTUELLE ===")
        for poke in party:
            status = f" [{poke.status_condition}]" if poke.status_condition else ""
            print(f"{poke.party_position}. {poke} - {poke.current_hp}/{poke.max_hp} HP{status}")
        
        print(f"\n=== PC ({pc_pokemon.count()} Pokémon) ===")
        
        print("\n1. Réorganiser l'équipe")
        print("2. Déposer un Pokémon au PC")
        print("3. Retirer un Pokémon du PC")
        print("4. Voir les détails d'un Pokémon")
        print("5. Retour")
        
        choice = input("\nVotre choix: ")
        
        if choice == '1':  # Réorganiser
            print("\nOrdre actuel:")
            for poke in party:
                print(f"{poke.party_position}. {poke}")
            
            print("\nEntrez le nouvel ordre (IDs séparés par des espaces):")
            new_order = input().split()
            try:
                new_order = [int(x) for x in new_order]
                organize_party(player, new_order)
                print("✓ Équipe réorganisée!")
            except:
                print("❌ Ordre invalide!")
        
        elif choice == '2':  # Déposer
            if party.count() <= 1:
                print("❌ Vous devez garder au moins 1 Pokémon dans votre équipe!")
                continue
            
            print("\nChoisir un Pokémon à déposer:")
            for i, poke in enumerate(party, 1):
                print(f"{i}. {poke}")
            
            poke_choice = int(input("\nVotre choix: ")) - 1
            selected = list(party)[poke_choice]
            
            deposit_pokemon(selected)
            print(f"✓ {selected} a été déposé au PC!")
        
        elif choice == '3':  # Retirer
            if party.count() >= 6:
                print("❌ Votre équipe est complète!")
                continue
            
            if not pc_pokemon.exists():
                print("❌ Aucun Pokémon dans le PC!")
                continue
            
            print("\nPokémon disponibles dans le PC:")
            for i, poke in enumerate(pc_pokemon, 1):
                print(f"{i}. {poke} - {poke.current_hp}/{poke.max_hp} HP")
            
            poke_choice = int(input("\nVotre choix: ")) - 1
            selected = list(pc_pokemon)[poke_choice]
            
            position = party.count() + 1
            success, msg = withdraw_pokemon(selected, position)
            print(msg)
        
        elif choice == '4':  # Détails
            all_pokemon = list(party) + list(pc_pokemon)
            print("\nChoisir un Pokémon:")
            for i, poke in enumerate(all_pokemon, 1):
                print(f"{i}. {poke}")
            
            poke_choice = int(input("\nVotre choix: ")) - 1
            selected = all_pokemon[poke_choice]
            
            # Afficher les détails complets
            print("\n" + "="*50)
            print(f"{selected}")
            print("="*50)
            print(f"Espèce: {selected.species.name}")
            print(f"Niveau: {selected.level}")
            print(f"Exp: {selected.current_exp}/{selected.exp_for_next_level()}")
            print(f"\nHP: {selected.current_hp}/{selected.max_hp}")
            print(f"Attaque: {selected.attack} (Stage: {selected.attack_stage:+d})")
            print(f"Défense: {selected.defense} (Stage: {selected.defense_stage:+d})")
            print(f"Att. Spé.: {selected.special_attack} (Stage: {selected.special_attack_stage:+d})")
            print(f"Déf. Spé.: {selected.special_defense} (Stage: {selected.special_defense_stage:+d})")
            print(f"Vitesse: {selected.speed} (Stage: {selected.speed_stage:+d})")
            print(f"\nNature: {selected.nature}")
            print(f"IVs: HP:{selected.iv_hp} ATK:{selected.iv_attack} DEF:{selected.iv_defense} " +
                  f"SPATK:{selected.iv_special_attack} SPDEF:{selected.iv_special_defense} SPD:{selected.iv_speed}")
            
            print(f"\nCapacités:")
            from myPokemonApp.models.PlayablePokemon import PokemonMoveInstance
            for move_inst in PokemonMoveInstance.objects.filter(pokemon=selected):
                print(f"  - {move_inst}")
            
            if selected.held_item:
                print(f"\nObjet tenu: {selected.held_item.name}")
            
            input("\nAppuyez sur Entrée pour continuer...")
        
        elif choice == '5':  # Retour
            break
        
        else:
            print("❌ Choix invalide!")


# ============================================================================
# EXEMPLE 8: BOUTIQUE POKÉMON
# ============================================================================

def example_pokemon_mart(player):
    """Boutique Pokémon interactive"""
    from myPokemonApp.models import Item
    from myPokemonApp.gameUtils import give_item_to_trainer
    
    # Articles disponibles (varie selon la progression)
    available_items = []
    
    if player.badges >= 0:
        available_items.extend(['Poké Ball', 'Potion', 'Antidote', 'Paralyze Heal'])
    if player.badges >= 1:
        available_items.extend(['Great Ball', 'Super Potion'])
    if player.badges >= 3:
        available_items.extend(['Ultra Ball', 'Hyper Potion'])
    if player.badges >= 7:
        available_items.extend(['Max Potion', 'Full Restore', 'Full Heal'])
    
    while True:
        print("\n" + "="*50)
        print("BOUTIQUE POKÉMON")
        print("="*50)
        print(f"Argent: {player.money}₽")
        print("="*50)
        
        # Afficher le catalogue
        items = Item.objects.filter(name__in=available_items).order_by('price')
        
        print("\nCATALOGUE:")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.name} - {item.price}₽")
            print(f"   {item.description}")
        
        print("\n0. Quitter")
        
        choice = input("\nQue voulez-vous acheter? ")
        
        if choice == '0':
            print("Merci de votre visite!")
            break
        
        try:
            item_index = int(choice) - 1
            selected_item = list(items)[item_index]
            
            # Demander la quantité
            quantity = int(input(f"Combien de {selected_item.name}? "))
            total_price = selected_item.price * quantity
            
            if total_price > player.money:
                print(f"❌ Vous n'avez pas assez d'argent! (Besoin: {total_price}₽)")
                continue
            
            # Confirmer l'achat
            print(f"\nAcheter {quantity}x {selected_item.name} pour {total_price}₽?")
            confirm = input("Confirmer? (o/n): ")
            
            if confirm.lower() == 'o':
                player.money -= total_price
                player.save()
                
                give_item_to_trainer(player, selected_item, quantity)
                
                print(f"✓ Vous avez acheté {quantity}x {selected_item.name}!")
        
        except (ValueError, IndexError):
            print("❌ Choix invalide!")


# ============================================================================
# MAIN - EXEMPLE DE JEU COMPLET
# ============================================================================

def main_game_loop():
    """Boucle de jeu principale - Exemple"""
    
    print("="*60)
    print("POKÉMON - GÉNÉRATION 1")
    print("="*60)
    
    # 1. Nouvelle partie
    print("\n1. Nouvelle partie")
    print("2. Charger une partie")
    
    choice = input("\nVotre choix: ")
    
    if choice == '1':
        player = example_new_game()
    else:
        # Charger une partie existante
        from myPokemonApp.models import Trainer
        username = input("Nom du joueur: ")
        try:
            player = Trainer.objects.get(username=username, trainer_type='player')
            print(f"Partie de {player.username} chargée!")
        except Trainer.DoesNotExist:
            print("Partie introuvable!")
            return
    
    # Boucle principale
    while True:
        print("\n" + "="*60)
        print("MENU PRINCIPAL")
        print("="*60)
        print(f"Joueur: {player.username}")
        print(f"Argent: {player.money}₽")
        print(f"Badges: {player.badges}/8")
        print(f"Localisation: {player.location}")
        print("="*60)
        
        print("\n1. Explorer une route")
        print("2. Défier une arène")
        print("3. Gérer l'équipe")
        print("4. Boutique Pokémon")
        print("5. Centre Pokémon")
        print("6. Sauvegarder")
        print("0. Quitter")
        
        choice = input("\nVotre choix: ")
        
        if choice == '1':
            # Explorer
            routes = ['Route 1', 'Route 2', 'Viridian Forest', 'Route 3', 'Route 4']
            print("\nRoutes disponibles:")
            for i, route in enumerate(routes, 1):
                print(f"{i}. {route}")
            
            route_choice = int(input("\nChoisir une route: ")) - 1
            selected_route = routes[route_choice]
            
            example_route_journey(player, selected_route)
        
        elif choice == '2':
            # Arène
            gyms = ['Pewter City', 'Cerulean City', 'Vermilion City', 
                    'Celadon City', 'Fuchsia City', 'Saffron City',
                    'Cinnabar Island', 'Viridian City']
            
            print("\nArènes disponibles:")
            for i, gym in enumerate(gyms, 1):
                print(f"{i}. {gym} (Badge #{i})")
            
            gym_choice = int(input("\nChoisir une arène: ")) - 1
            selected_gym = gyms[gym_choice]
            
            example_gym_challenge(player, selected_gym)
        
        elif choice == '3':
            # Équipe
            example_team_management(player)
        
        elif choice == '4':
            # Boutique
            example_pokemon_mart(player)
        
        elif choice == '5':
            # Centre Pokémon
            from myPokemonApp.gameUtils import heal_team
            heal_team(player)
            print("✓ Votre équipe est complètement soignée!")
        
        elif choice == '6':
            # Sauvegarder
            player.save()
            print("✓ Partie sauvegardée!")
        
        elif choice == '0':
            # Quitter
            print("\nÀ bientôt!")
            break
        
        else:
            print("❌ Choix invalide!")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == '__main__':
    # Exemple d'utilisation
    print("""
    Ce fichier contient des exemples d'utilisation du système Pokémon.
    
    Pour démarrer un jeu complet, utilisez:
        main_game_loop()
    
    Pour tester des fonctionnalités spécifiques:
        - example_new_game()
        - example_random_encounter(player)
        - example_gym_challenge(player, 'Pewter City')
        - etc.
    """)