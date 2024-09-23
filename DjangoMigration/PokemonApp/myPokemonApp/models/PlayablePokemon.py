#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models
from .Pokemon import Pokemon
from .Trainer import Trainer



class PlayablePokemon(Pokemon):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='pokemons')

    def __str__(self):
        return f"{self.name} (Trainer: {self.trainer.username})"
    


    #comme go_to_lvl mais on ne veut pas qu'ils évoluent : ah bah c'est pas le cas dans aucune des 2 fonctions donc elles sont identiques :/
    def skip_to_lvl(self, newLevel):
        levelsGained = newLevel - self.level
        basePokemonObj = Pokemon.objects.get(name=self.name)
        statsIncrease = self.stats_increase_for_each_pokemon(basePokemonObj)

        for _ in range(levelsGained):
            self.level += 1
            self.increaseStats(statsIncrease, self.level-1)

        
        """ Si utilisé pour la copie useless sinon pour les pokemon sauvages il faudra leur mettre des moves
        moves_by_pokemon = All_Learnable_Moves().moves_by_pokemon
        learnable_moves = [move for move in moves_by_pokemon[self.name] if move[1] == self.level]
        new_moves = [move for move in learnable_moves if move not in self.moves]
        if new_moves:
            name_learnable_move = new_moves[0][0]
            if(not (self.is_moved_already_learned(name_learnable_move))):
                learnable_move = find_move(name_learnable_move)
                if len(self.moves) >= 4:
                    del self.moves[0]                
                self.moves.append(learnable_move)
        """
            #cette fonction sera un raccourci pour aller direct à un lvl donc on ne va pas demander de choisir un moove à chaque fois que le pokemon
    #peut en apprendre un on supprimera juste le plus ancien moove (c comme ça qu'on génèrera les pkemon sauvage à un niveua supérieur)



    def gain_experience(self, experience):
        self.experience += experience
        self.check_level_up()
        self.check_evolution()

    def display_experience_bar(self):
        # Calculate the experience needed for the next level
        exp_for_next_level = self.level * self.base_experience
        # Calculate the percentage of current experience relative to the experience needed for the next level
        exp_percentage = (self.experience / exp_for_next_level) * 100
        # Display the experience bar
        print(f"Experience: {self.experience}/{exp_for_next_level} ({exp_percentage:.2f}%)")

    def check_level_up(self):
        # Determine the amount of experience needed to reach the next level
        experience_needed = self.level * self.base_experience
        
        # If the Pokemon has enough experience, level it up and reset its experience points
        if self.experience >= experience_needed:
            self.experience = 0
            self.levelUp()
    


    def check_evolution(self):
        evolutionList = self.evolutions.all()
        #exception eeve and stones evoltuions TODO
        for evolutionData in evolutionList:
            if self.level >= evolutionData.evolutionLevel and evolutionData.evolutionLevel!=0:
                #if level_of_evolution == 0 it means it evolves with an object (not implemented yet)
                EvolvedPokemonObj = evolutionData.evolvesTo
                print(f"\033[1;31m{self.name} is evolving into {EvolvedPokemonObj.name}\033[0;0m\n")
                
                EvolvedPokemonObjCopy = copyNewPokemonObj(EvolvedPokemonObj)  

                EvolvedPokemonObjCopy.skip_to_lvl(evolutionData.evolutionLevel) #TODO

                self.name = EvolvedPokemonObjCopy.name
                self.level = self.level  #stay the same
                self.type = EvolvedPokemonObjCopy.type
                self.hp = EvolvedPokemonObjCopy.hp
                self.attack = EvolvedPokemonObjCopy.attack
                self.defense = EvolvedPokemonObjCopy.defense
                self.special_attack = EvolvedPokemonObjCopy.special_attack
                self.special_defense = EvolvedPokemonObjCopy.special_defense
                self.speed = EvolvedPokemonObjCopy.speed
                self.moves = self.moves  #we keep the old moves
                self.catch_rate = 1
                self.base_experience = EvolvedPokemonObjCopy.base_experience
                self.experience = 0
                self.max_hp = EvolvedPokemonObjCopy.hp    
      
    

    def is_moved_already_learned(self, OtherMoveObj):
        for move in self.moves:
            if move.name.lower() == OtherMoveObj.name.lower():
                return True
        return False

    #checks if the pokemon can learn a new move and if he already has 4 moves
    def checkLearnableMoves(self):
        pokemon =  self
        learnableMovesList = pokemon.learnable_moves.all()
        actualLevel = pokemon.level

        # Check if the level of the Pokemon is high enough to learn a new move
        for learnableMove in learnableMovesList:
            if learnableMove.LearnableAtLevel == actualLevel:
                NewMoveObj = learnableMove.move
                if(not (pokemon.is_moved_already_learned(NewMoveObj))):
                    
                    # If the Pokemon has less than 4 moves, add the new move(s) directly
                    if pokemon.moves.count() < 4:
                        pokemon.moves.add(NewMoveObj)
                        return (f"New moves added: {NewMoveObj.name}")
                    
                    # If the Pokemon has 4 moves already, ask the user if they want to replace an existing move
                    else:
                        while True:
                            print("Choose a move to replace:")
                            for i, move in enumerate(pokemon.moves):
                                print(f"{i+1}. {move}")
                            choice = input("Enter the number of the move to replace or 'cancel' to cancel: ")
                            if choice.lower() == 'cancel':
                                return "Move learning canceled."
                            try:
                                choiceIndex = int(choice)
                                if 1 <= choiceIndex <= 4:
                                    movesList = list(pokemon.moves.all())
                                    moveToRemove = movesList[choiceIndex - 1]
                                    pokemon.moves.remove(moveToRemove)

                                    pokemon.moves.add(NewMoveObj)

                                    return (f"Move replaced with {NewMoveObj.name}")
                            except ValueError:
                                pass
                            print("Invalid input. Try again.")

                else:
                    return (f"Move {NewMoveObj.name} already known")

        #if no move was detected as learnable return 0
        return 0


    def stats_increase_for_each_pokemon(self, basePokemonObj):
        #we need to compare to base stats
        
        #without Nature or EV or IV for the moment
        #normaly + 1/100 of IV+EV
        #and + 1/50 of the base stat
        stats_increase = [round((basePokemonObj.hp)/50), round((basePokemonObj.attack)/50), round((basePokemonObj.defense)/50), round((basePokemonObj.special_attack)/50), round((basePokemonObj.special_defense)/50), round((basePokemonObj.speed)/50)]
        return stats_increase

    #Updated ver taking into account the evolution 
    def increaseStats(self, statsIncrease, oldLvl):
        levelsGained = self.level - oldLvl

        for _ in range(levelsGained):
            self.hp += statsIncrease[0]
            self.attack += statsIncrease[1]
            self.defense += statsIncrease[2]
            self.special_attack += statsIncrease[3]
            self.special_defense += statsIncrease[4]
            self.speed += statsIncrease[5]
            self.max_hp += statsIncrease[0]


    def levelUp(self):
        oldLvl = self.level
        self.level += 1
        basePokemonObj = Pokemon.objects.get(name=self.name)

        statsIncrease = self.stats_increase_for_each_pokemon(basePokemonObj)

        self.increaseStats(statsIncrease, oldLvl)

        print(f"\033[1;32m  {self.name} has leveled up to level {self.level}!  \033[0;0m\n")

        #checking if he can now learn a new move
        retour = self.checkLearnableMoves()
        if(retour != 0):
            print(retour)


def copyNewPokemonObj(PokemonToCopy):
    newPokemonObj = PlayablePokemon()
    newPokemonObj.name = PokemonToCopy.name
    newPokemonObj.level = PokemonToCopy.level 
    newPokemonObj.type = PokemonToCopy.type
    newPokemonObj.hp = PokemonToCopy.hp
    newPokemonObj.attack = PokemonToCopy.attack
    newPokemonObj.defense = PokemonToCopy.defense
    newPokemonObj.special_attack = PokemonToCopy.special_attack
    newPokemonObj.special_defense = PokemonToCopy.special_defense
    newPokemonObj.speed = PokemonToCopy.speed
    newPokemonObj.moves = PokemonToCopy.moves
    newPokemonObj.catch_rate = 1
    newPokemonObj.base_experience = PokemonToCopy.base_experience
    newPokemonObj.experience = 0
    newPokemonObj.max_hp = PokemonToCopy.hp    
    
    return newPokemonObj




#TODO
"""

  def display_stats(self):
    print(f"Name: {self.name}")
    print(f"Level: {self.level}")
    print(f"Type: {self.type}")
    print(f"HP: {self.hp}")
    print(f"Attack: {self.attack}")
    print(f"Defense: {self.defense}")
    print(f"Special Attack: {self.special_attack}")
    print(f"Special Defense: {self.special_defense}")
    print(f"Speed: {self.speed}")
    
  def is_fainted(self):
     #Return True if the pokemon's current HP is 0 or lower.
     return self.hp <= 0
  

  def get_random_move(self):
    #print("Longueur", len(self.moves))
    if(len(self.moves)<=1):
      choice = 0
    else:
      choice = random.randint(0, len(self.moves)-1)
    #print("choix :", choice)
    #print(f"moves of {self.name}:")
    for i, move in enumerate(self.moves):
      #print(f"{i+1}. {move.name} (Power: {move.attack_power}, Accuracy: {move.accuracy}%)")
      if i == choice:
        #print(f"Move chosen by {move.name} (Power: {move.attack_power}, Accuracy: {move.accuracy}%)")
        return move


  def choose_move(self):
    print(f"Choose a move for {self.name}:")
    for i, move in enumerate(self.moves):
      print(f"{i+1}. {move.name} (Power: {move.attack_power}, Accuracy: {move.accuracy}%), Type : {move.type}")
    choice = int(input()) - 1
    return self.moves[choice]
  
  def is_move_type_same_as_pokemon(self, move):
    return self.type == move.type


def attack(attacking_pokemon, other_pokemon, move):
  #print(move.name)
  damage = calculate_damage(attacking_pokemon, other_pokemon, move)
  other_pokemon.hp -= damage
  print(f"\033[1;32m {attacking_pokemon.name} used {move.name} and dealt {damage} damage to {other_pokemon.name}.\033[0;0m\n")
  if other_pokemon.hp <= 0:
    other_pokemon.hp = 0
    print(f"{other_pokemon.name} fainted.")
    return True
  return False

def calculate_damage(current_pokemon, other_pokemon, current_move):

  if(current_move.attack_power == 0):
    return 0
  else:
    #critical is 1 or 2 with 5% of chance
    r = random.random()
    if r <= 0.05:
      critical = 2
    else:
      critical = 1

    if(current_pokemon.is_move_type_same_as_pokemon(current_move)):
      STAB = 1.5
    else:
      STAB =1

    #0 for innefective O.5 for not good  1 for normal and 2 for super effective
    TYPE = determine_effectiveness(current_move.type, other_pokemon.type)
       

    #we select the highest between atk spe and atk
    if(current_pokemon.attack > current_pokemon.special_attack):
        check = (( ( (((2*current_pokemon.level*critical)//5)+2)*(current_pokemon.attack//other_pokemon.defense) *current_move.attack_power )//50) +2) * STAB * TYPE
    else:
        check = (( ( (((2*current_pokemon.level*critical)//5)+2)*(current_pokemon.special_attack//other_pokemon.special_defense) * current_move.attack_power)//50)+2) * STAB * TYPE
    
    if(check >= 0):
        return check
    else:
        return 0

    #il faudrait rajouter la faiblesse des types (*0.5 *1 ou *2) ainsi que les crit *1 ou *2, ainsi que le STAB *1.5

def determine_effectiveness(attack_type, pokemon_type):
    # Map type advantages and disadvantages
    types_advantages = {
      'normal': {'rock': 0.5,  'steel' : 0.5, 'ghost': 0},
      'fire': {'fire': 0.5, 'water': 0.5, 'rock': 0.5, 'dragon': 0.5, 'grass': 2, 'ice' : 2, 'bug' : 2, 'steel' : 2},
      'water': {'water': 0.5, 'grass': 0.5, 'dragon': 0.5, 'fire' : 2, 'ground' : 2, 'rock' : 2},
      'electric': {'electric': 0.5, 'grass': 0.5, 'dragon': 0.5, 'ground': 0, 'flying' : 2, 'water' : 2},
      'grass': {'fire': 0.5, 'grass': 0.5, 'poison': 0.5, 'flying': 0.5, 'dragon': 0.5, 'bug' : 0.5, 'steel' : 0.5, 'water' : 2, 'rock' : 2, 'ground' : 2},
      'ice': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 0.5, 'dragon': 2, 'steel' : 0.5, 'ground' : 2, 'flying' : 2}, 
      'fighting': {'normal': 2, 'ice': 2, 'poison': 0.5, 'flying': 0.5, 'psychic': 0.5, 'bug': 0.5, 'rock' : 2, 'ghost': 0, 'dark' : 2, 'steel' : 2, 'fairy' : 0.5},
      'poison': {'grass': 2, 'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 'ghost': 0.5, 'steel' : 0, 'fairy' : 2},
      'ground': {'fire': 2, 'electric': 2, 'grass': 0.5, 'poison': 2, 'flying': 0, 'bug': 0.5, 'rock' : 2, 'steel' : 2},
      'flying': {'electric': 0.5, 'grass': 2, 'fighting': 2, 'bug': 2, 'rock' : 0.5, 'steel' : 0.5},
      'psychic': {'psychic': 0.5, 'fighting': 2, 'poison': 2, 'dark' : 0, 'steel' : 0.5},
      'bug': {'fire': 0.5, 'grass': 2, 'fighting': 0.5, 'poison': 0.5, 'flying': 0.5, 'psychic': 2, 'ghost': 0.5, 'dark' : 2, 'steel' : 0.5, 'fairy' : 0.5},
      'rock': {'fire': 2, 'ice': 2, 'flying': 2, 'bug': 2, 'poison' : 0.5, 'ground' : 0.5, 'steel' : 0.5},
      'ghost': {'normal': 0, 'psychic': 2, 'ghost': 2, 'dark' : 0.5},
      'dragon': {'dragon': 2, 'steel': 0.5, 'fairy' : 0},
      'dark': {'fighting': 0.5, 'ghost': 2, 'psychic': 2, 'dark' : 0.5, 'fairy' : 0.5},
      'steel' : {'fire': 0.5, 'water': 0.5, 'electric': 0.5, 'ice': 2, 'rock': 2, 'steel': 0.5, 'fairy': 2},
      'fairy' : {'fire' : 0.5, 'fighting': 2, 'poison': 0.5, 'dragon': 2, 'dark': 2,'steel': 0.5,}
    }
    try:
      effectiveness = types_advantages[attack_type][pokemon_type]
      if effectiveness == 2:
        print("super effective")
        return 2
      elif effectiveness == 0.5:
        print("not very effective")
        return 0.5
      elif effectiveness == 0:
        print("no effect")
        return 0
      else:
        print("normal effectiveness")
        return 1
    except KeyError:
      print("normal effectiveness")
      return 1


def defeated_pokemon_experience(defeated_pokemon, winner_pokemon):

  #In gen 1 it's a flat formula that doesn't take into account the winner's level

  #a=1 if pokemon is wild a=1.5 if pokemon is owned by a Trainer
  a=1
  #b is the base experience uield of the fainted Pokemon's speicies, values here https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_effort_value_yield
  b = defeated_pokemon.base_experience
  #e=1.5 if the winner holds a lucky egg e=1 otherwise
  e=1
  #s
  #In Gen I 
  #If Exp. All is not in the player's Bag...
  #      Number of Pokémon that participated in the battle and have not fainted
  #  If Exp. All is in the player's Bag...
  #      Twice the number of Pokémon that participated and have not fainted, when calculating the experience of a Pokémon that participated in battle
  #      Twice the number of Pokémon that participated and have not fainted times the number of Pokémon in the player's party, when calculating the experience given by Exp. All
  s=1
  #t=1 1 if the winning Pokémon's current owner is its Original Trainer t=1.5 if the Pokémon was gained in a domestic trade
  t=1
  #L is the level of the fainted pokemon
  L = defeated_pokemon.level
  exp = int(((b*L)/7) * (1/s) * e * a * t)
  return exp



"""