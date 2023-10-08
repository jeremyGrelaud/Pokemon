#main big file where all pokemons are initialized with their stats, types ... and also which moves they can learn and when do they evolve...


from moves import All_Moves, display_pokemon_moves, find_move, get_move_info_in_line
import random

###########################Pokemons#################################
class Pokemon:
  def __init__(self, name, level, type, hp, attack, defense, special_attack, special_defense, speed, moves, base_experience, catch_rate, experience=0):
    self.name = name
    self.level = level
    self.type = type
    self.hp = hp
    self.attack = attack
    self.defense = defense
    self.special_attack = special_attack
    self.special_defense = special_defense
    self.speed = speed
    self.moves = moves
    self.catch_rate = catch_rate  #to complete
    self.base_experience = base_experience
    self.experience = experience 
    self.max_hp = hp
    self.status = "none"

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
          self.level += 1
          self.experience = 0
          #stats_increase = stats_increase_by_pokemon_type(self.type)
          base_pokemon = All_Pokemons().better_find_pokemon_by_name(self.name)

          stats_increase = self.stats_increase_for_each_pokemon(base_pokemon)
          increase_stats(self, stats_increase, base_pokemon)
          print(f"\033[1;32m  {self.name} has leveled up to level {self.level}!  \033[0;0m\n")

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
     """Return True if the pokemon's current HP is 0 or lower."""
     return self.hp <= 0
  
  """
  def get_max_hp(self):
    #it will be x time a part of the base hp
    poke = find_pokemon_by_name(self.name, initialize_all_pokemons())
    base_hp = poke.hp
    for i in range (self.level-poke.level):
        poke.hp += (round((base_hp)/50))
    return poke.hp
  """

    #cette fonction sera un raccourci pour aller direct à un lvl donc on ne va pas demander de choisir un moove à chaque fois que le pokemon
    #peut en apprendre un on supprimera juste le plus ancien moove (c comme ça qu'on génèrera les pkemon sauvage à un niveua supérieur)
  def go_to_lvl(self, level):
    diff_between_curr_level_and_new = level - self.level
    for i in range (diff_between_curr_level_and_new):
        self.level += 1
        #stats_increase = stats_increase_by_pokemon_type(self.type)
        base_pokemon = All_Pokemons().better_find_pokemon_by_name(self.name)

        stats_increase = self.stats_increase_for_each_pokemon(base_pokemon)
        increase_stats(self, stats_increase, base_pokemon)
      
        #ajout forcément des nouveaux move
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
 
           

    #comme go_to_lvl mais on ne veut pas qu'ils évoluent : ah bah c'est pas le cas dans aucune des 2 fonctions donc elles sont identiques :/
  def skip_to_lvl(self, level):
    diff_between_curr_level_and_new = level - self.level
    #pas besoin de refaire à chaque fois les 2 calcul sur le poke de base non ?
    base_pokemon = All_Pokemons().better_find_pokemon_by_name(self.name)
    stats_increase = self.stats_increase_for_each_pokemon(base_pokemon)
    
    for i in range (diff_between_curr_level_and_new):
      self.level += 1
      increase_stats(self, stats_increase, base_pokemon)
    
      #ajout forcément des nouveaux move
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

  def check_evolution(self):
    evolution_dict = All_Evolutions().evolutions
    try:
        pokemon_data = evolution_dict[self.name]
        level_of_evolution = pokemon_data[0]
        #print("Debuging",level_of_evolution, "and", self.level)
        pokemon_name_to_evolve_to = pokemon_data[1]

        #if level_of_evolution == 0 it means it evolves with an object (not implemented yet)
        if self.level >= level_of_evolution and level_of_evolution!=0:
            print(f"\033[1;31m{self.name} is evolving into {pokemon_name_to_evolve_to}\033[0;0m\n")
            evolved_pokemon = find_pokemon_by_name(pokemon_name_to_evolve_to, All_Pokemons().pokemon_list)
            evolved_pokemon.skip_to_lvl(level_of_evolution)

            self.name = evolved_pokemon.name
            self.level = self.level  #stay the same
            self.type = evolved_pokemon.type
            self.hp = evolved_pokemon.hp
            self.attack = evolved_pokemon.attack
            self.defense = evolved_pokemon.defense
            self.special_attack = evolved_pokemon.special_attack
            self.special_defense = evolved_pokemon.special_defense
            self.speed = evolved_pokemon.speed
            self.moves = self.moves  #we keep the old moves
            self.catch_rate = 1
            self.base_experience = evolved_pokemon.base_experience
            self.experience = 0
            self.max_hp = evolved_pokemon.hp    
    except KeyError:
        #it means it has no evolutions left
      return 0
    

  def is_moved_already_learned(self, name_other_move):
    for move in self.moves:
      if move.name.lower() == name_other_move.lower():
        return True
    return False

  def choose_move(self):
    print(f"Choose a move for {self.name}:")
    for i, move in enumerate(self.moves):
      print(f"{i+1}. {move.name} (Power: {move.attack_power}, Accuracy: {move.accuracy}%), Type : {move.type}")
    choice = int(input()) - 1
    return self.moves[choice]
  
  def is_move_type_same_as_pokemon(self, move):
    return self.type == move.type



  def stats_increase_for_each_pokemon(self, base_pokemon):
    #we need to compare to base stats
    
    #without Nature or EV or IV for the moment
    #normaly + 1/100 of IV+EV
    #and + 1/50 of the base stat
    stats_increase = [round((base_pokemon.hp)/50), round((base_pokemon.attack)/50), round((base_pokemon.defense)/50), round((base_pokemon.special_attack)/50), round((base_pokemon.special_defense)/50), round((base_pokemon.speed)/50)]
    return stats_increase
    
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

  #In gen 1 it's a falt formula that doesn't take into account the winner's level

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
def increase_stats(self, stats_increase):
    # Increase the stats of the pokemon by the given amount
    #print(f"Your stats have increased by : {stats_increase}")
    self.hp += (stats_increase[0])
    self.attack += stats_increase[1]
    self.defense += stats_increase[2]
    self.special_attack += stats_increase[3]
    self.special_defense += stats_increase[4]
    self.speed += stats_increase[5]
"""
#Updated ver taking into account the evolution 

def increase_stats(self, stats_increase, base_pokemon):


    copy = create_copy_pokemon(base_pokemon)
    # Increase the stats of the pokemon by the given amount
    #print(f"Your stats have increased by : {stats_increase}")
    self.hp = copy.hp
    self.attack = copy.attack
    self.defense = copy.defense
    self.special_attack = copy.special_attack
    self.special_defense = copy.special_defense
    self.speed = copy.speed
    self.max_hp = copy.hp

    for i in range (self.level-1):
        self.hp += (stats_increase[0])
        self.attack += stats_increase[1]
        self.defense += stats_increase[2]
        self.special_attack += stats_increase[3]
        self.special_defense += stats_increase[4]
        self.speed += stats_increase[5]
        self.max_hp += (stats_increase[0])



def level_up(self):
    self.level += 1
    #stats_increase = stats_increase_by_pokemon_type(self.type)
    base_pokemon = All_Pokemons().better_find_pokemon_by_name(self.name)

    stats_increase = self.stats_increase_for_each_pokemon(base_pokemon)
    increase_stats(self, stats_increase, base_pokemon)
    print(f"{self.name} has leveled up to level {self.level}!")
    retour = check_learnable_moves(self)
    if(retour != 0):
        print(retour)




# Create a new pokemon with stats and moves
def create_pokemon(name, level, type, hp, attack, defense, special_attack, special_defense, speed, move_names, base_exp, catch_rate):
  
  # Find the moves with the given names
  moves_list = [move for move in All_Moves().move_list if move.name in move_names]

  return Pokemon(name, level, type, hp, attack, defense, special_attack, special_defense, speed, moves_list, base_exp, catch_rate)

def create_copy_pokemon(pokemon: Pokemon):
  return Pokemon(pokemon.name, pokemon.level, pokemon.type, pokemon.max_hp, pokemon.attack, pokemon.defense, pokemon.special_attack, pokemon.special_defense, pokemon.speed, pokemon.moves, pokemon.base_experience, pokemon.catch_rate)


def find_pokemon_by_name(name, pokemon_list):
    for pokemon in pokemon_list:
        if pokemon.name == name:
            return pokemon
    return None
    
def find_pokemon_by_position(position, pokemon_list):
  # Check if the position is a valid index for the list
  if position < 0 or position >= len(pokemon_list):
    return None

  # Return the Pokemon object at the specified position in the list
  return pokemon_list[position]


#Initialize all pokemons in the game
"""
def initialize_all_pokemons():
  # List of tuples containing the pokemon's name, level, type, stats, and moves
  pokemon_data = [
    ("Bulbasaur", 1, "grass", 45, 49, 49, 65, 65, 45, ["Tackle", "Growl"], 64),
    ("Ivysaur", 2, "grass", 60, 62, 63, 80, 80, 60, ["Tackle", "Growl", "Leech Seed"], 142),
    ("Venusaur", 3, "grass", 80, 82, 83, 100, 100, 80, ["Tackle", "Growl", "Leech Seed", "Vine Whip"], 263),
    ("Charmander", 1, "fire", 39, 52, 43, 60, 50, 65, ["Scratch", "Growl"], 62),
    ("Charmeleon", 2, "fire", 58, 64, 58, 80, 65, 80, ["Scratch", "Growl", "Ember"], 142),
    ("Charizard", 3, "fire", 78, 84, 78, 109, 85, 100, ["Scratch", "Growl", "Ember", "Flamethrower"], 267),
    ("Squirtle", 1, "water", 44, 48, 65, 50, 64, 43, ["Tackle", "Tail Whip"], 63),
    ("Wartortle", 2, "water", 59, 63, 80, 65, 80, 58, ["Tackle", "Tail Whip", "Bubble"], 142),
    ("Blastoise", 3, "water", 79, 83, 100, 85, 105, 78, ["Tackle", "Tail Whip", "Bubble", "Hydro Pump"], 265),
    ("Caterpie", 1, "bug", 45, 30, 35, 20, 20, 45, ["Tackle"], 39),
    ("Metapod", 2, "bug", 50, 20, 55, 25, 25, 30, ["Harden"], 72),
    ("Butterfree", 3, "bug", 60, 45, 50, 90, 80, 70, ["Confusion", "Poison Powder", "Stun Spore"], 198),
    ("Weedle", 1, "bug", 40, 35, 30, 20, 20, 50, ["Poison Sting"], 39),
    ("Kakuna", 2, "bug", 45, 25, 50, 25, 25, 35, ["Harden"], 72),
    ("Beedrill", 3, "bug", 65, 90, 40, 45, 80, 75, ["Fury Attack", "Twineedle"], 198),
    ("Pidgey", 1, "normal", 40, 45, 40, 35, 35, 56, ["Tackle", "Gust"], 50),
    ("Pidgeotto", 2, "normal", 63, 60, 55, 50, 50, 71, ["Tackle", "Gust", "Sand Attack"], 122),
    ("Pidgeot", 3, "normal", 83, 80, 75, 70, 70, 101, ["Tackle", "Gust", "Sand Attack", "Wing Attack"], 240),
    ("Rattata", 1, "normal", 30, 56, 35, 25, 35, 72, ["Tackle", "Tail Whip"], 51),
    ("Raticate", 2, "normal", 55, 81, 60, 50, 70, 97, ["Tackle", "Tail Whip", "Hyper Fang"], 145),
    ("Spearow", 1, "normal", 40, 60, 30, 31, 31, 70, ["Peck"], 52),
    ("Fearow", 2, "normal", 65, 90, 65, 61, 61, 100, ["Peck", "Drill Peck"], 155),
    ("Ekans", 1, "poison", 35, 60, 44, 40, 54, 55, ["Wrap", "Poison Sting"], 58),
    ("Arbok", 2, "poison", 60, 95, 69, 65, 79, 80, ["Wrap", "Poison Sting", "Bite"], 157),
    ("Pikachu", 1, "electric", 35, 55, 40, 50, 50, 90, ["Thunder Shock", "Growl"], 112),
    ("Raichu", 2, "electric", 60, 90, 55, 90, 80, 110, ["Thunder Shock", "Growl", "Thunderbolt"], 243),
    ("Sandshrew", 1, "ground", 50, 75, 85, 20, 30, 40, ["Scratch", "Defense Curl"], 60),
    ("Sandslash", 2, "ground", 75, 100, 110, 45, 55, 65, ["Scratch", "Defense Curl", "Sand Attack"], 158),
    ("Nidoran♀", 1, "poison", 55, 47, 52, 40, 40, 41, ["Scratch", "Tail Whip"], 55),
    ("Nidorina", 2, "poison", 70, 62, 67, 55, 55, 56, ["Scratch", "Tail Whip", "Double Kick"], 128),
    ("Nidoqueen", 3, "poison", 90, 92, 87, 75, 85, 76, ["Scratch", "Tail Whip", "Double Kick", "Body Slam"], 253),
    ("Nidoran♂", 1, "poison", 46, 57, 40, 40, 40, 50, ["Peck", "Tail Whip"], 55),
    ("Nidorino", 2, "poison", 61, 72, 57, 55, 55, 65, ["Peck", "Tail Whip", "Horn Attack"], 128),
    ("Nidoking", 3, "poison", 81, 102, 77, 85, 75, 85, ["Peck", "Tail Whip", "Horn Attack", "Thrash"], 253),
    ("Clefairy", 1, "fairy", 70, 45, 48, 60, 65, 35, ["Pound", "Growl"], 113),
    ("Clefable", 2, "fairy", 95, 70, 73, 95, 90, 60, ["Pound", "Growl", "Double Slap"], 242),
    ("Vulpix", 1, "fire", 38, 41, 40, 50, 65, 65, ["Ember", "Tail Whip"], 60),
    ("Ninetales", 2, "fire", 73, 76, 75, 81, 100, 100, ["Ember", "Tail Whip", "Fire Spin"], 177),
    ("Jigglypuff", 1, "normal", 115, 45, 20, 45, 25, 20, ["Sing", "Pound"], 95),
    ("Wigglytuff", 2, "normal", 140, 70, 45, 85, 50, 45, ["Sing", "Pound", "Double Slap"], 218),
    ("Zubat", 1, "poison", 40, 45, 35, 30, 40, 55, ["Leech Life", "Supersonic"], 49),
    ("Golbat", 2, "poison", 75, 80, 70, 65, 75, 90, ["Leech Life", "Supersonic", "Bite"], 159),
    ("Oddish", 1, "grass", 45, 50, 55, 75, 65, 30, ["Absorb"], 64),
    ("Gloom", 2, "grass", 60, 65, 70, 85, 75, 40, ["Absorb", "Acid"], 138),
    ("Vileplume", 3, "grass", 75, 80, 85, 100, 90, 50, ["Absorb", "Acid", "Petal Dance"], 245),
    ("Paras", 1, "bug", 35, 70, 55, 45, 55, 25, ["Scratch", "Stun Spore"], 57),
    ("Parasect", 2, "bug", 60, 95, 80, 60, 80, 30, ["Scratch", "Stun Spore", "Slash"], 142),
    ("Venonat", 1, "bug", 60, 55, 50, 40, 55, 45, ["Tackle", "Poison Powder"], 61),
    ("Venomoth", 2, "bug", 70, 65, 60, 90, 75, 90, ["Tackle", "Poison Powder", "Confusion"], 158),
    ("Diglett", 1, "ground", 10, 55, 25, 35, 45, 95, ["Scratch", "Growl"], 53),
    ("Dugtrio", 2, "ground", 35, 100, 50, 50, 70, 120, ["Scratch", "Growl", "Slash"], 149),
    ("Meowth", 1, "normal", 40, 45, 35, 40, 40, 90, ["Scratch", "Growl"], 58),
    ("Persian", 2, "normal", 65, 70, 60, 65, 65, 115, ["Scratch", "Growl", "Bite"], 154),
    ("Psyduck", 1, "water", 50, 52, 48, 65, 50, 55, ["Scratch", "Tail Whip"], 64),
    ("Golduck", 2, "water", 80, 82, 78, 95, 80, 85, ["Scratch", "Tail Whip", "Hydro Pump"], 175),
    ("Mankey", 1, "fighting", 40, 80, 35, 35, 45, 70, ["Scratch", "Leer"], 61),
    ("Primeape", 2, "fighting", 65, 105, 60, 60, 70, 95, ["Scratch", "Leer", "Low Kick"], 159),
    ("Growlithe", 1, "fire", 55, 70, 45, 70, 50, 60, ["Bite", "Roar"], 70),
    ("Arcanine", 2, "fire", 90, 110, 80, 100, 80, 95, ["Bite", "Roar", "Flamethrower"], 194),
    ("Poliwag", 1, "water", 40, 50, 40, 40, 40, 90, ["Bubble", "Hypnosis"], 60),
    ("Poliwhirl", 2, "water", 65, 65, 65, 50, 50, 90, ["Bubble", "Hypnosis", "Double Slap"], 135),
    ("Poliwrath", 3, "water", 90, 85, 95, 70, 90, 70, ["Bubble", "Hypnosis", "Double Slap", "Submission"], 255),
    ("Abra", 1, "psychic", 25, 20, 15, 105, 55, 90, ["Teleport"], 62),
    ("Kadabra", 2, "psychic", 40, 35, 30, 120, 70, 105, ["Teleport", "Kinesis"], 140),
    ("Alakazam", 3, "psychic", 55, 50, 45, 135, 95, 120, ["Teleport", "Kinesis", "Psychic"], 250),
    ("Machop", 1, "fighting", 70, 80, 50, 35, 35, 35, ["Low Kick", "Leer"], 61),
    ("Machoke", 2, "fighting", 80, 100, 70, 50, 60, 45, ["Low Kick", "Leer", "Karate Chop"], 142),
    ("Machamp", 3, "fighting", 90, 130, 80, 65, 85, 55, ["Low Kick", "Leer", "Karate Chop", "Submission"], 253),
    ("Bellsprout", 1, "grass", 50, 75, 35, 70, 30, 40, ["Vine Whip", "Growth"], 60),
    ("Weepinbell", 2, "grass", 65, 90, 50, 85, 45, 55, ["Vine Whip", "Growth", "Razor Leaf"], 137),
    ("Victreebel", 3, "grass", 80, 105, 65, 100, 70, 70, ["Vine Whip", "Growth", "Razor Leaf", "Sleep Powder"], 245),
    ("Tentacool", 1, "water", 40, 40, 35, 50, 100, 70, ["Acid", "Poison Sting"], 67),
    ("Tentacruel", 2, "water", 80, 70, 65, 80, 120, 100, ["Acid", "Poison Sting", "Wrap"], 180),
    ("Geodude", 1, "rock", 40, 80, 100, 30, 30, 20, ["Tackle", "Defense Curl"], 60),
    ("Graveler", 2, "rock", 55, 95, 115, 45, 45, 35, ["Tackle", "Defense Curl", "Rock Throw"], 137),
    ("Golem", 3, "rock", 80, 110, 130, 55, 65, 45, ["Tackle", "Defense Curl", "Rock Throw", "Earthquake"], 248),
    ("Ponyta", 1, "fire", 50, 85, 55, 65, 65, 90, ["Tackle", "Growl"], 82),
    ("Rapidash", 2, "fire", 65, 100, 70, 80, 80, 105, ["Tackle", "Growl", "Stomp"], 175),
    ("Slowpoke", 1, "water", 90, 65, 65, 40, 40, 15, ["Tackle", "Growl"], 63),
    ("Slowbro", 2, "water", 95, 75, 110, 100, 80, 30, ["Tackle", "Growl", "Confusion"], 172),
    ("Magnemite", 1, "electric", 25, 35, 70, 95, 55, 45, ["Tackle", "Sonic Boom"], 65),
    ("Magneton", 2, "electric", 50, 60, 95, 120, 70, 70, ["Tackle", "Sonic Boom", "Thunder Shock"], 163),
    ("Farfetch'd", 1, "normal", 52, 65, 55, 60, 58, 62, ["Peck", "Sand Attack"], 132),
    ("Doduo", 1, "normal", 35, 85, 45, 35, 35, 75, ["Peck", "Growl"], 62),
    ("Dodrio", 2, "normal", 60, 110, 70, 60, 60, 100, ["Peck", "Growl", "Drill Peck"], 165),
    ("Seel", 1, "water", 65, 45, 55, 45, 70, 45, ["Headbutt", "Growl"], 65),
    ("Dewgong", 2, "water", 90, 70, 80, 70, 95, 70, ["Headbutt", "Growl", "Aurora Beam"], 166),
    ("Grimer", 1, "poison", 80, 80, 50, 25, 40, 50, ["Pound", "Poison Gas"], 65),
    ("Muk", 2, "poison", 105, 105, 75, 50, 65, 100, ["Pound", "Poison Gas", "Sludge"], 175),
    ("Shellder", 1, "water", 30, 65, 100, 45, 25, 40, ["Tackle", "Withdraw"], 61),
    ("Cloyster", 2, "water", 50, 95, 180, 85, 45, 70, ["Tackle", "Withdraw", "Ice Beam"], 184),
    ("Gastly", 1, "ghost", 30, 35, 30, 100, 35, 80, ["Lick", "Spite"], 62),
    ("Haunter", 2, "ghost", 45, 50, 45, 115, 55, 95, ["Lick", "Spite", "Hypnosis"], 142),
    ("Gengar", 3, "ghost", 60, 65, 60, 130, 75, 110, ["Lick", "Spite", "Hypnosis", "Dream Eater"], 250),
    ("Onix", 1, "rock", 35, 45, 160, 30, 45, 70, ["Tackle", "Screech"], 77),
    ("Drowzee", 1, "psychic", 60, 48, 45, 43, 90, 42, ["Pound", "Hypnosis"], 66),
    ("Hypno", 2, "psychic", 85, 73, 70, 73, 115, 67, ["Pound", "Hypnosis", "Psychic"], 169),
    ("Krabby", 1, "water", 30, 105, 90, 25, 25, 50, ["Bubble", "Leer"], 65),
    ("Kingler", 2, "water", 55, 130, 115, 50, 50, 75, ["Bubble", "Leer", "Vice Grip"], 166),
    ("Voltorb", 1, "electric", 40, 30, 50, 55, 55, 100, ["Tackle", "Screech"], 66),
    ("Electrode", 2, "electric", 60, 50, 70, 80, 80, 150, ["Tackle", "Screech", "Thunder Shock"], 172),
    ("Exeggcute", 1, "grass", 60, 40, 80, 60, 45, 40, ["Barrage", "Hypnosis"], 65),
    ("Exeggutor", 2, "grass", 95, 95, 85, 125, 65, 55, ["Barrage", "Hypnosis", "Egg Bomb"], 186),
    ("Cubone", 1, "ground", 50, 50, 95, 40, 50, 35, ["Bone Club", "Growl"], 64),
    ("Marowak", 2, "ground", 60, 80, 110, 50, 80, 45, ["Bone Club", "Growl", "Headbutt"], 149),
    ("Hitmonlee", 1, "fighting", 50, 120, 53, 35, 110, 87, ["Mega Kick", "Jump Kick"], 159),
    ("Hitmonchan", 1, "fighting", 50, 105, 79, 35, 110, 76, ["Mega Punch", "Fire Punch"], 159),
    ("Lickitung", 1, "normal", 90, 55, 75, 60, 75, 30, ["Lick", "Supersonic"], 77),
    ("Koffing", 1, "poison", 40, 65, 95, 60, 45, 35, ["Tackle", "Smog"], 68),
    ("Weezing", 2, "poison", 65, 90, 120, 85, 70, 60, ["Tackle", "Smog", "Sludge"], 172),
    ("Rhyhorn", 1, "rock", 80, 85, 95, 30, 30, 25, ["Horn Attack", "Stomp"], 69),
    ("Rhydon", 2, "rock", 105, 130, 120, 45, 45, 40, ["Horn Attack", "Stomp", "Earthquake"], 170),
    ("Chansey", 1, "normal", 250, 5, 5, 35, 105, 50, ["Pound", "Growl"], 395),
    ("Tangela", 1, "grass", 65, 55, 115, 100, 40, 60, ["Bind", "Absorb"], 87),
    ("Kangaskhan", 2, "normal", 105, 95, 80, 90, 40, 80, ["Bite", "Tail Whip", "Rage"], 172),
    ("Horsea", 1, "water", 30, 40, 70, 70, 25, 60, ["Bubble", "Smokescreen"], 59),
    ("Seadra", 2, "water", 55, 65, 95, 95, 45, 85, ["Bubble", "Smokescreen", "Water Gun"], 154),
    ("Goldeen", 1, "water", 45, 67, 60, 63, 35, 50, ["Peck", "Tail Whip"], 64),
    ("Seaking", 2, "water", 80, 92, 65, 68, 65, 80, ["Peck", "Tail Whip", "Horn Attack"], 158),
    ("Staryu", 1, "water", 30, 45, 55, 85, 70, 55, ["Tackle", "Harden"], 68),
    ("Starmie", 2, "water", 60, 75, 85, 115, 100, 85, ["Tackle", "Harden", "Water Gun"], 182),
    ("Mr. Mime", 1, "psychic", 40, 45, 65, 90, 100, 120, ["Confusion", "Barrier"], 161),
    ("Scyther", 1, "bug", 70, 110, 80, 105, 55, 80, ["Quick Attack", "Leer"], 100),
    ("Jynx", 1, "ice", 65, 50, 35, 95, 115, 95, ["Pound", "Lick"], 159),
    ("Electabuzz", 1, "electric", 65, 83, 57, 105, 95, 85, ["Quick Attack", "Thunder Punch"], 172),
    ("Magmar", 1, "fire", 65, 95, 57, 93, 100, 85, ["Ember", "Smokescreen"], 173),
    ("Pinsir", 1, "bug", 65, 125, 100, 85, 55, 70, ["Vice Grip", "Seismic Toss"], 175),
    ("Tauros", 1, "normal", 75, 100, 95, 110, 40, 70, ["Tackle", "Stomp"], 172),
    ("Magikarp", 1, "water", 20, 10, 55, 80, 15, 20, ["Splash"], 40),
    ("Gyarados", 2, "water", 95, 125, 79, 81, 60, 100, ["Bite", "Hydro Pump"], 189),
    ("Lapras", 2, "water", 130, 85, 80, 85, 95, 60, ["Growl", "Water Gun"], 187),
    ("Ditto", 1, "normal", 48, 48, 48, 48, 48, 48, ["Transform"], 101),
    ("Eevee", 1, "normal", 55, 55, 50, 65, 65, 55, ["Quick Attack", "Tail Whip"], 65),
    ("Vaporeon", 2, "water", 130, 65, 60, 110, 95, 65, ["Quick Attack", "Tail Whip", "Water Gun"], 184),
    ("Jolteon", 2, "electric", 65, 65, 60, 110, 95, 130, ["Quick Attack", "Tail Whip", "Thunder Shock"], 184),
    ("Flareon", 2, "fire", 65, 130, 60, 95, 110, 65, ["Quick Attack", "Tail Whip", "Ember"], 184),
    ("Porygon", 1, "normal", 65, 60, 70, 85, 75, 40, ["Tackle", "Sharpen"], 79),
    ("Omanyte", 1, "rock", 35, 40, 100, 90, 55, 35, ["Bite", "Withdraw"], 71),
    ("Omastar", 2, "rock", 70, 60, 125, 115, 70, 55, ["Bite", "Withdraw", "Rock Slide"], 173),
    ("Kabuto", 1, "rock", 30, 80, 90, 55, 45, 55, ["Scratch", "Harden"], 71),
    ("Kabutops", 2, "rock", 60, 115, 105, 80, 70, 80, ["Scratch", "Harden", "Slash"], 173),
    ("Aerodactyl", 2, "rock", 80, 105, 65, 130, 60, 75, ["Bite", "Wing Attack"], 180),
    ("Snorlax", 2, "normal", 160, 110, 65, 30, 65, 110, ["Tackle", "Rest"], 189),
    ("Articuno", 3, "ice", 90, 85, 100, 95, 125, 85, ["Peck", "Ice Beam", "Blizzard"], 290),
    ("Zapdos", 3, "electric", 90, 90, 85, 125, 90, 100, ["Peck", "Thunder Shock", "Thunderbolt"], 290),
    ("Moltres", 3, "fire", 90, 100, 90, 125, 85, 90, ["Peck", "Ember", "Fire Blast"], 290),
    ("Dratini", 1, "dragon", 41, 64, 45, 50, 50, 50, ["Wrap", "Leer"], 60),
    ("Dragonair", 2, "dragon", 61, 84, 65, 70, 70, 70, ["Wrap", "Leer", "Thunder Wave"], 147),
    ("Dragonite", 3, "dragon", 91, 134, 95, 80, 100, 100, ["Wrap", "Leer", "Thunder Wave", "Dragon Rage"], 300),
    ("Mewtwo", 3, "psychic", 106, 110, 90, 130, 154, 90, ["Psycho Cut", "Swift", "Psystrike"], 340),
    ("Mew", 3, "psychic", 100, 100, 100, 100, 100, 100, ["Pound", "Mega Punch", "Psychic"], 300)
  ]


  # Create a list to store the pokemon
  pokemon_list = []

  # Iterate over the pokemon data and create each pokemon
  for data in pokemon_data:
    #name, level, type, hp, attack, defense, special_attack, special_defense, speed, moves = data
    #pokemon = create_pokemon(name, level, type, hp, attack, defense, special_attack, special_defense, speed, moves)
    pokemon = create_pokemon(*data)
    pokemon_list.append(pokemon)
  
  return pokemon_list
"""


def check_learnable_moves(pokemon):
    moves_by_pokemon = All_Learnable_Moves().moves_by_pokemon
    # Check if the level of the Pokemon is high enough to learn a new move
    learnable_moves = [move for move in moves_by_pokemon[pokemon.name] if move[1] == pokemon.level]
    new_moves = [move for move in learnable_moves if move not in pokemon.moves]
    if not new_moves:
        return 0  # No new moves can be learned at this level.
    
    

    name_learnable_move = new_moves[0][0]
    if(not (pokemon.is_moved_already_learned(name_learnable_move))):
        
        #print(name_learnable_move)
        learnable_move = find_move(name_learnable_move)
        print(get_move_info_in_line(learnable_move))
        # If the Pokemon has less than 4 moves, add the new move(s) directly
        if len(pokemon.moves) < 4:
            pokemon.moves.append(learnable_move)
            return "New moves added: {}".format(learnable_move.name)
        # If the Pokemon has 4 moves already, ask the user if they want to replace an existing move
        else:
            while True:
                print("Choose a move to replace:")
                for i, move in enumerate(pokemon.moves):
                    print("{}. {}".format(i + 1, get_move_info_in_line(move)))
                choice = input("Enter the number of the move to replace or 'cancel' to cancel: ")
                if choice.lower() == 'cancel':
                    return "Move learning canceled."
                try:
                    choice = int(choice)
                    if 1 <= choice <= 4:
                        del pokemon.moves[choice - 1]
                        pokemon.moves.append(learnable_move)
                        return "Move replaced with {}".format(learnable_move.name)
                except ValueError:
                    pass
                print("Invalid input. Try again.")
    else:
        return(f"Move {name_learnable_move} already known")








##########################"End_Pokemons##############################


########################Start All Pokemons###############################
class All_Pokemons:
    instance = None
    def __init__(self):
        self.pokemon_list = []
        pokemon_data = [
            ("Abra", 1, "psychic", 25, 20, 15, 105, 55, 90, ["Teleport"], 62, 25),
            ("Aerodactyl", 2, "rock", 80, 105, 65, 130, 60, 75, ["Bite", "Wing Attack"], 180, 45),
            ("Alakazam", 3, "psychic", 55, 50, 45, 135, 95, 120, ["Teleport", "Kinesis", "Psychic"], 250, 50),
            ("Arbok", 2, "poison", 60, 95, 69, 65, 79, 80, ["Wrap", "Poison Sting", "Bite"], 157, 90),
            ("Arcanine", 2, "fire", 90, 110, 80, 100, 80, 95, ["Bite", "Roar", "Flamethrower"], 194, 75),
            ("Articuno", 3, "ice", 90, 85, 100, 95, 125, 85, ["Peck", "Ice Beam", "Blizzard"], 290, 3),
            ("Beedrill", 3, "bug", 65, 90, 40, 45, 80, 75, ["Fury Attack", "Twineedle"], 198, 45),
            ("Bellsprout", 1, "grass", 50, 75, 35, 70, 30, 40, ["Vine Whip", "Growth"], 60, 255),
            ("Blastoise", 3, "water", 79, 83, 100, 85, 105, 78, ["Tackle", "Tail Whip", "Bubble", "Hydro Pump"], 265, 45),
            ("Bulbasaur", 1, "grass", 45, 49, 49, 65, 65, 45, ["Tackle", "Growl"], 64, 45),
            ("Butterfree", 3, "bug", 60, 45, 50, 90, 80, 70, ["Confusion", "Poison Powder", "Stun Spore"], 198, 45),
            ("Caterpie", 1, "bug", 45, 30, 35, 20, 20, 45, ["Tackle"], 39, 255),
            ("Chansey", 1, "normal", 250, 5, 5, 35, 105, 50, ["Pound", "Growl"], 395, 30),
            ("Charizard", 3, "fire", 78, 84, 78, 109, 85, 100, ["Scratch", "Growl", "Ember", "Flamethrower"], 267, 45),
            ("Charmander", 1, "fire", 39, 52, 43, 60, 50, 65, ["Scratch", "Growl"], 62, 45),
            ("Charmeleon", 2, "fire", 58, 64, 58, 80, 65, 80, ["Scratch", "Growl", "Ember"], 142, 45),
            ("Clefable", 2, "fairy", 95, 70, 73, 95, 90, 60, ["Pound", "Growl", "Double Slap"], 242, 25),
            ("Clefairy", 1, "fairy", 70, 45, 48, 60, 65, 35, ["Pound", "Growl"], 113, 150),
            ("Cloyster", 2, "water", 50, 95, 180, 85, 45, 70, ["Tackle", "Withdraw", "Ice Beam"], 184, 60),
            ("Cubone", 1, "ground", 50, 50, 95, 40, 50, 35, ["Bone Club", "Growl"], 64, 190),
            ("Dewgong", 2, "water", 90, 70, 80, 70, 95, 70, ["Headbutt", "Growl", "Aurora Beam"], 166, 75),
            ("Diglett", 1, "ground", 10, 55, 25, 35, 45, 95, ["Scratch", "Growl"], 53, 255),
            ("Ditto", 1, "normal", 48, 48, 48, 48, 48, 48, ["Transform"], 101, 35),
            ("Dodrio", 2, "normal", 60, 110, 70, 60, 60, 100, ["Peck", "Growl", "Drill Peck"], 165, 45),
            ("Doduo", 1, "normal", 35, 85, 45, 35, 35, 75, ["Peck", "Growl"], 62, 190),
            ("Dragonair", 2, "dragon", 61, 84, 65, 70, 70, 70, ["Wrap", "Leer", "Thunder Wave"], 147, 45),
            ("Dragonite", 3, "dragon", 91, 134, 95, 80, 100, 100, ["Wrap", "Leer", "Thunder Wave", "Dragon Rage"], 300, 45),
            ("Dratini", 1, "dragon", 41, 64, 45, 50, 50, 50, ["Wrap", "Leer"], 60, 45),
            ("Drowzee", 1, "psychic", 60, 48, 45, 43, 90, 42, ["Pound", "Hypnosis"], 66, 190),
            ("Dugtrio", 2, "ground", 35, 100, 50, 50, 70, 120, ["Scratch", "Growl", "Slash"], 149, 50),
            ("Eevee", 1, "normal", 55, 55, 50, 65, 65, 55, ["Quick Attack", "Tail Whip"], 65, 45),
            ("Ekans", 1, "poison", 35, 60, 44, 40, 54, 55, ["Wrap", "Poison Sting"], 58, 255),
            ("Electabuzz", 1, "electric", 65, 83, 57, 105, 95, 85, ["Quick Attack", "Thunder Punch"], 172, 45),
            ("Electrode", 2, "electric", 60, 50, 70, 80, 80, 150, ["Tackle", "Screech", "Thunder Shock"], 172, 60),
            ("Exeggcute", 1, "grass", 60, 40, 80, 60, 45, 40, ["Barrage", "Hypnosis"], 65, 90),
            ("Exeggutor", 2, "grass", 95, 95, 85, 125, 65, 55, ["Barrage", "Hypnosis", "Egg Bomb"], 186, 45),
            ("Farfetch'd", 1, "normal", 52, 65, 55, 60, 58, 62, ["Peck", "Sand Attack"], 132, 45),
            ("Fearow", 2, "normal", 65, 90, 65, 61, 61, 100, ["Peck", "Drill Peck"], 155, 90),
            ("Flareon", 2, "fire", 65, 130, 60, 95, 110, 65, ["Quick Attack", "Tail Whip", "Ember"], 184, 45),
            ("Gastly", 1, "ghost", 30, 35, 30, 100, 35, 80, ["Lick", "Spite"], 62, 190),
            ("Gengar", 3, "ghost", 60, 65, 60, 130, 75, 110, ["Lick", "Spite", "Hypnosis", "Dream Eater"], 250, 45),
            ("Geodude", 1, "rock", 40, 80, 100, 30, 30, 20, ["Tackle", "Defense Curl"], 60, 255),
            ("Gloom", 2, "grass", 60, 65, 70, 85, 75, 40, ["Absorb", "Acid"], 138, 120),
            ("Golbat", 2, "poison", 75, 80, 70, 65, 75, 90, ["Leech Life", "Supersonic", "Bite"], 159, 90),
            ("Goldeen", 1, "water", 45, 67, 60, 63, 35, 50, ["Peck", "Tail Whip"], 64, 255),
            ("Golduck", 2, "water", 80, 82, 78, 95, 80, 85, ["Scratch", "Tail Whip", "Hydro Pump"], 175, 75),
            ("Golem", 3, "rock", 80, 110, 130, 55, 65, 45, ["Tackle", "Defense Curl", "Rock Throw", "Earthquake"], 248, 45),
            ("Graveler", 2, "rock", 55, 95, 115, 45, 45, 35, ["Tackle", "Defense Curl", "Rock Throw"], 137, 120),
            ("Grimer", 1, "poison", 80, 80, 50, 25, 40, 50, ["Pound", "Poison Gas"], 65, 190),
            ("Growlithe", 1, "fire", 55, 70, 45, 70, 50, 60, ["Bite", "Roar"], 70, 190),
            ("Gyarados", 2, "water", 95, 125, 79, 81, 60, 100, ["Bite", "Hydro Pump"], 189, 45),
            ("Haunter", 2, "ghost", 45, 50, 45, 115, 55, 95, ["Lick", "Spite", "Hypnosis"], 142, 90),
            ("Hitmonchan", 1, "fighting", 50, 105, 79, 35, 110, 76, ["Mega Punch", "Fire Punch"], 159, 45),
            ("Hitmonlee", 1, "fighting", 50, 120, 53, 35, 110, 87, ["Mega Kick", "Jump Kick"], 159, 45),
            ("Horsea", 1, "water", 30, 40, 70, 70, 25, 60, ["Bubble", "Smokescreen"], 59, 225),
            ("Hypno", 2, "psychic", 85, 73, 70, 73, 115, 67, ["Pound", "Hypnosis", "Psychic"], 169, 75),
            ("Ivysaur", 2, "grass", 60, 62, 63, 80, 80, 60, ["Tackle", "Growl", "Leech Seed"], 142, 45),
            ("Jigglypuff", 1, "normal", 115, 45, 20, 45, 25, 20, ["Sing", "Pound"], 95, 170),
            ("Jolteon", 2, "electric", 65, 65, 60, 110, 95, 130, ["Quick Attack", "Tail Whip", "Thunder Shock"], 184, 45),
            ("Jynx", 1, "ice", 65, 50, 35, 95, 115, 95, ["Pound", "Lick"], 159, 45),
            ("Kabutops", 2, "rock", 60, 115, 105, 80, 70, 80, ["Scratch", "Harden", "Slash"], 173, 45),
            ("Kabuto", 1, "rock", 30, 80, 90, 55, 45, 55, ["Scratch", "Harden"], 71, 45),
            ("Kadabra", 2, "psychic", 40, 35, 30, 120, 70, 105, ["Teleport", "Kinesis"], 140, 100),
            ("Kakuna", 2, "bug", 45, 25, 50, 25, 25, 35, ["Harden"], 72, 120),
            ("Kangaskhan", 2, "normal", 105, 95, 80, 90, 40, 80, ["Bite", "Tail Whip", "Rage"], 172, 45),
            ("Kingler", 2, "water", 55, 130, 115, 50, 50, 75, ["Bubble", "Leer", "Vice Grip"], 166, 60),
            ("Koffing", 1, "poison", 40, 65, 95, 60, 45, 35, ["Tackle", "Smog"], 68, 190),
            ("Krabby", 1, "water", 30, 105, 90, 25, 25, 50, ["Bubble", "Leer"], 65, 225),
            ("Lapras", 2, "water", 130, 85, 80, 85, 95, 60, ["Growl", "Water Gun"], 187, 45),
            ("Lickitung", 1, "normal", 90, 55, 75, 60, 75, 30, ["Lick", "Supersonic"], 77, 45),
            ("Machamp", 3, "fighting", 90, 130, 80, 65, 85, 55, ["Low Kick", "Leer", "Karate Chop", "Submission"], 253, 45),
            ("Machoke", 2, "fighting", 80, 100, 70, 50, 60, 45, ["Low Kick", "Leer", "Karate Chop"], 142, 90),
            ("Machop", 1, "fighting", 70, 80, 50, 35, 35, 35, ["Low Kick", "Leer"], 61, 180),
            ("Magikarp", 1, "water", 20, 10, 55, 80, 15, 20, ["Splash"], 40, 255),
            ("Magmar", 1, "fire", 65, 95, 57, 93, 100, 85, ["Ember", "Smokescreen"], 173, 45),
            ("Magnemite", 1, "electric", 25, 35, 70, 95, 55, 45, ["Tackle", "Sonic Boom"], 65, 190),
            ("Magneton", 2, "electric", 50, 60, 95, 120, 70, 70, ["Tackle", "Sonic Boom", "Thunder Shock"], 163, 60),
            ("Mankey", 1, "fighting", 40, 80, 35, 35, 45, 70, ["Scratch", "Leer"], 61, 190),
            ("Marowak", 2, "ground", 60, 80, 110, 50, 80, 45, ["Bone Club", "Growl", "Headbutt"], 149, 75),
            ("Meowth", 1, "normal", 40, 45, 35, 40, 40, 90, ["Scratch", "Growl"], 58, 255),
            ("Metapod", 2, "bug", 50, 20, 55, 25, 25, 30, ["Harden"], 72, 120),
            ("Mew", 3, "psychic", 100, 100, 100, 100, 100, 100, ["Pound", "Mega Punch", "Psychic"], 300, 45),
            ("Mewtwo", 3, "psychic", 106, 110, 90, 130, 154, 90, ["Psycho Cut", "Swift", "Psystrike"], 340, 3),
            ("Moltres", 3, "fire", 90, 100, 90, 125, 85, 90, ["Peck", "Ember", "Fire Blast"], 290, 3),
            ("Mr. Mime", 1, "psychic", 40, 45, 65, 90, 100, 120, ["Confusion", "Barrier"], 161, 45),
            ("Muk", 2, "poison", 105, 105, 75, 50, 65, 100, ["Pound", "Poison Gas", "Sludge"], 175, 75),
            ("Nidoking", 3, "poison", 81, 102, 77, 85, 75, 85, ["Peck", "Tail Whip", "Horn Attack", "Thrash"], 253, 45),
            ("Nidoqueen", 3, "poison", 90, 92, 87, 75, 85, 76, ["Scratch", "Tail Whip", "Double Kick", "Body Slam"], 253, 45),
            ("Nidoran♀", 1, "poison", 55, 47, 52, 40, 40, 41, ["Scratch", "Tail Whip"], 55, 235),
            ("Nidoran♂", 1, "poison", 46, 57, 40, 40, 40, 50, ["Peck", "Tail Whip"], 55, 235),
            ("Nidorina", 2, "poison", 70, 62, 67, 55, 55, 56, ["Scratch", "Tail Whip", "Double Kick"], 128, 120),
            ("Nidorino", 2, "poison", 61, 72, 57, 55, 55, 65, ["Peck", "Tail Whip", "Horn Attack"], 128, 120),
            ("Ninetales", 2, "fire", 73, 76, 75, 81, 100, 100, ["Ember", "Tail Whip", "Fire Spin"], 177, 75),
            ("Oddish", 1, "grass", 45, 50, 55, 75, 65, 30, ["Absorb"], 64, 255),
            ("Omanyte", 1, "rock", 35, 40, 100, 90, 55, 35, ["Bite", "Withdraw"], 71, 45),
            ("Omastar", 2, "rock", 70, 60, 125, 115, 70, 55, ["Bite", "Withdraw", "Rock Slide"], 173, 45),
            ("Onix", 1, "rock", 35, 45, 160, 30, 45, 70, ["Tackle", "Screech"], 77, 45),
            ("Paras", 1, "bug", 35, 70, 55, 45, 55, 25, ["Scratch", "Stun Spore"], 57, 190),
            ("Parasect", 2, "bug", 60, 95, 80, 60, 80, 30, ["Scratch", "Stun Spore", "Slash"], 142, 75),
            ("Persian", 2, "normal", 65, 70, 60, 65, 65, 115, ["Scratch", "Growl", "Bite"], 154, 90),
            ("Pidgeot", 3, "normal", 83, 80, 75, 70, 70, 101, ["Tackle", "Gust", "Sand Attack", "Wing Attack"], 240, 45),
            ("Pidgeotto", 2, "normal", 63, 60, 55, 50, 50, 71, ["Tackle", "Gust", "Sand Attack"], 122, 120),
            ("Pidgey", 1, "normal", 40, 45, 40, 35, 35, 56, ["Tackle", "Gust"], 50, 255),
            ("Pikachu", 1, "electric", 35, 55, 40, 50, 50, 90, ["Thunder Shock", "Growl"], 112, 190),
            ("Pinsir", 1, "bug", 65, 125, 100, 85, 55, 70, ["Vice Grip", "Seismic Toss"], 175, 45),
            ("Poliwag", 1, "water", 40, 50, 40, 40, 40, 90, ["Bubble", "Hypnosis"], 60, 255),
            ("Poliwhirl", 2, "water", 65, 65, 65, 50, 50, 90, ["Bubble", "Hypnosis", "Double Slap"], 135, 120),
            ("Poliwrath", 3, "water", 90, 85, 95, 70, 90, 70, ["Bubble", "Hypnosis", "Double Slap", "Submission"], 255, 45),
            ("Ponyta", 1, "fire", 50, 85, 55, 65, 65, 90, ["Tackle", "Growl"], 82, 190),
            ("Porygon", 1, "normal", 65, 60, 70, 85, 75, 40, ["Tackle", "Sharpen"], 79, 45),
            ("Primeape", 2, "fighting", 65, 105, 60, 60, 70, 95, ["Scratch", "Leer", "Low Kick"], 159, 75),
            ("Psyduck", 1, "water", 50, 52, 48, 65, 50, 55, ["Scratch", "Tail Whip"], 64, 190),
            ("Raichu", 2, "electric", 60, 90, 55, 90, 80, 110, ["Thunder Shock", "Growl", "Thunderbolt"], 243, 75),
            ("Rapidash", 2, "fire", 65, 100, 70, 80, 80, 105, ["Tackle", "Growl", "Stomp"], 175, 60),
            ("Raticate", 2, "normal", 55, 81, 60, 50, 70, 97, ["Tackle", "Tail Whip", "Hyper Fang"], 145, 127),
            ("Rattata", 1, "normal", 30, 56, 35, 25, 35, 72, ["Tackle", "Tail Whip"], 51, 255),
            ("Rhydon", 2, "rock", 105, 130, 120, 45, 45, 40, ["Horn Attack", "Stomp", "Earthquake"], 170, 60),
            ("Rhyhorn", 1, "rock", 80, 85, 95, 30, 30, 25, ["Horn Attack", "Stomp"], 69, 120),
            ("Sandshrew", 1, "ground", 50, 75, 85, 20, 30, 40, ["Scratch", "Defense Curl"], 60, 255),
            ("Sandslash", 2, "ground", 75, 100, 110, 45, 55, 65, ["Scratch", "Defense Curl", "Sand Attack"], 158, 90),
            ("Scyther", 1, "bug", 70, 110, 80, 105, 55, 80, ["Quick Attack", "Leer"], 100, 45),
            ("Seadra", 2, "water", 55, 65, 95, 95, 45, 85, ["Bubble", "Smokescreen", "Water Gun"], 154, 45),
            ("Seaking", 2, "water", 80, 92, 65, 68, 65, 80, ["Peck", "Tail Whip", "Horn Attack"], 158, 60),
            ("Seel", 1, "water", 65, 45, 55, 45, 70, 45, ["Headbutt", "Growl"], 65, 190),
            ("Shellder", 1, "water", 30, 65, 100, 45, 25, 40, ["Tackle", "Withdraw"], 61, 190),
            ("Slowbro", 2, "water", 95, 75, 110, 100, 80, 30, ["Tackle", "Growl", "Confusion"], 172, 75),
            ("Slowpoke", 1, "water", 90, 65, 65, 40, 40, 15, ["Tackle", "Growl"], 63, 190),
            ("Snorlax", 2, "normal", 160, 110, 65, 30, 65, 110, ["Tackle", "Rest"], 189, 25),
            ("Spearow", 1, "normal", 40, 60, 30, 31, 31, 70, ["Peck"], 52, 255),
            ("Squirtle", 1, "water", 44, 48, 65, 50, 64, 43, ["Tackle", "Tail Whip"], 63, 45),
            ("Starmie", 2, "water", 60, 75, 85, 115, 100, 85, ["Tackle", "Harden", "Water Gun"], 182, 60),
            ("Staryu", 1, "water", 30, 45, 55, 85, 70, 55, ["Tackle", "Harden"], 68, 225),
            ("Tangela", 1, "grass", 65, 55, 115, 100, 40, 60, ["Bind", "Absorb"], 87, 45),
            ("Tauros", 1, "normal", 75, 100, 95, 110, 40, 70, ["Tackle", "Stomp"], 172, 45),
            ("Tentacool", 1, "water", 40, 40, 35, 50, 100, 70, ["Acid", "Poison Sting"], 67, 190),
            ("Tentacruel", 2, "water", 80, 70, 65, 80, 120, 100, ["Acid", "Poison Sting", "Wrap"], 180, 60),
            ("Vaporeon", 2, "water", 130, 65, 60, 110, 95, 65, ["Quick Attack", "Tail Whip", "Water Gun"], 184, 45),
            ("Venomoth", 2, "bug", 70, 65, 60, 90, 75, 90, ["Tackle", "Poison Powder", "Confusion"], 158, 75),
            ("Venonat", 1, "bug", 60, 55, 50, 40, 55, 45, ["Tackle", "Poison Powder"], 61, 190),
            ("Venusaur", 3, "grass", 80, 82, 83, 100, 100, 80, ["Tackle", "Growl", "Leech Seed", "Vine Whip"], 263, 45),
            ("Victreebel", 3, "grass", 80, 105, 65, 100, 70, 70, ["Vine Whip", "Growth", "Razor Leaf", "Sleep Powder"], 245, 45),
            ("Vileplume", 3, "grass", 75, 80, 85, 100, 90, 50, ["Absorb", "Acid", "Petal Dance"], 245, 45),
            ("Voltorb", 1, "electric", 40, 30, 50, 55, 55, 100, ["Tackle", "Screech"], 66, 190),
            ("Vulpix", 1, "fire", 38, 41, 40, 50, 65, 65, ["Ember", "Tail Whip"], 60, 190),
            ("Wartortle", 2, "water", 59, 63, 80, 65, 80, 58, ["Tackle", "Tail Whip", "Bubble"], 142, 45),
            ("Weedle", 1, "bug", 40, 35, 30, 20, 20, 50, ["Poison Sting"], 39, 255),
            ("Weepinbell", 2, "grass", 65, 90, 50, 85, 45, 55, ["Vine Whip", "Growth", "Razor Leaf"], 137, 120),
            ("Weezing", 2, "poison", 65, 90, 120, 85, 70, 60, ["Tackle", "Smog", "Sludge"], 172, 60),
            ("Wigglytuff", 2, "normal", 140, 70, 45, 85, 50, 45, ["Sing", "Pound", "Double Slap"], 218, 50),
            ("Zapdos", 3, "electric", 90, 90, 85, 125, 90, 100, ["Peck", "Thunder Shock", "Thunderbolt"], 290, 3),
            ("Zubat", 1, "poison", 40, 45, 35, 30, 40, 55, ["Leech Life", "Supersonic"], 49, 255)
        ]

        
        # Iterate over the pokemon data and create each pokemon
        for data in pokemon_data:
            pokemon = create_pokemon(*data)
            self.pokemon_list.append(pokemon)
        

    def __new__(cls):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.__init__()
        return cls.instance


    #binary search for a list in alphabetical order
    def better_find_pokemon_by_name(self, name):
        low = 0
        high = len(self.pokemon_list) - 1
        while low <= high:
            mid = (low + high) // 2
            guess = self.pokemon_list[mid]
            if guess.name == name:
                return guess #we return the poke
            if guess.name > name:
                high = mid - 1
            else:
                low = mid + 1
        return None
#############################End All Pokemons#################################
#####################All learnable Moves#########################
class All_Learnable_Moves:
    instance = None
    def __init__(self):
        self.moves_by_pokemon = {
            'Bulbasaur': [
                ('Tackle', 1),
                ('Growl', 7),
                ('Leech Seed', 13),
                ('Vine Whip', 21),
                ('Poison Powder', 28),
                ('Razor Leaf', 35),
                ('Sleep Powder', 42),
                ('Solar Beam', 49)
            ],
            'Ivysaur': [
                ('Tackle', 1),
                ('Growl', 1),
                ('Leech Seed', 1),
                ('Vine Whip', 21),
                ('Poison Powder', 28),
                ('Razor Leaf', 36),
                ('Sleep Powder', 43),
                ('Solar Beam', 50)
            ],
            'Venusaur': [
                ('Tackle', 1),
                ('Growl', 1),
                ('Leech Seed', 1),
                ('Vine Whip', 21),
                ('Poison Powder', 28),
                ('Razor Leaf', 36),
                ('Sleep Powder', 43),
                ('Solar Beam', 50),
                ('Sludge', 1),
                ('Charm', 1),
                ('Mega Drain', 1),
                ('Belly Drum', 1)
            ],
            'Charmander': [
                ('Scratch', 1),
                ('Growl', 1),
                ('Ember', 9),
                ('Smokescreen', 15),
                ('Dragon Rage', 22),
                ('Scary Face', 29),
                ('Fire Spin', 36),
                ('Flamethrower', 43)
            ],
            'Charmeleon': [
                ('Scratch', 1),
                ('Growl', 1),
                ('Ember', 1),
                ('Smokescreen', 16),
                ('Dragon Rage', 23),
                ('Scary Face', 30),
                ('Fire Spin', 37),
                ('Flamethrower', 44)
            ],
            'Charizard': [
                ('Scratch', 1),
                ('Growl', 1),
                ('Ember', 1),
                ('Smokescreen', 16),
                ('Dragon Rage', 23),
                ('Scary Face', 30),
                ('Fire Spin', 37),
                ('Flamethrower', 44),
                ('Wing Attack', 1),
                ('Slash', 1),
                ('Dragon Claw', 1)
            ],
            'Squirtle': [
                ('Tackle', 1),
                ('Tail Whip', 5),
                ('Bubble', 11),
                ('Water Gun', 17),
                ('Bite', 23),
                ('Withdraw', 30),
                ('Skull Bash', 37),
                ('Hydro Pump', 44)
            ],
            'Wartortle': [
                ('Tackle', 1),
                ('Tail Whip', 1),
                ('Bubble', 11),
                ('Water Gun', 18),
                ('Bite', 25),
                ('Withdraw', 33),
                ('Skull Bash', 41),
                ('Hydro Pump', 49)
            ],
        'Blastoise': [
                ('Tackle', 1),
                ('Tail Whip', 1),
                ('Bubble', 11),
                ('Water Gun', 18),
                ('Bite', 25),
                ('Withdraw', 33),
                ('Skull Bash', 41),
                ('Hydro Pump', 49),
                ('Mud Shot', 1),
                ('Ice Beam', 1),
                ('Blizzard', 1)
            ],
            'Caterpie': [
                ('String Shot', 1),
                ('Bug Bite', 1)
            ],
            'Metapod': [
                ('Harden', 1)
            ],
            'Butterfree': [
                ('Confusion', 1),
                ('Poison Powder', 1),
                ('Stun Spore', 1),
                ('Sleep Powder', 1),
                ('Supersonic', 28),
                ('Psybeam', 36),
                ('Whirlwind', 43)
            ],
            'Weedle': [
                ('Poison Sting', 1),
                ('Bug Bite', 1)
            ],
            'Kakuna': [
                ('Harden', 1)
            ],
            'Beedrill': [
                ('Fury Attack', 1),
                ('Twineedle', 1),
                ('Rage', 21),
                ('Pin Missile', 28),
                ('Agility', 36),
                ('Assurance', 43)
            ],
            'Pidgey': [
                ('Gust', 1),
                ('Sand Attack', 9),
                ('Quick Attack', 15),
                ('Whirlwind', 22),
                ('Wing Attack', 29),
                ('Double-Edge', 36)
            ],
            'Pidgeotto': [
                ('Gust', 1),
                ('Sand Attack', 1),
                ('Quick Attack', 16),
                ('Whirlwind', 23),
                ('Wing Attack', 30),
                ('Double-Edge', 37)
            ],
            'Pidgeot': [
                ('Gust', 1),
                ('Sand Attack', 1),
                ('Quick Attack', 16),
                ('Whirlwind', 23),
                ('Wing Attack', 30),
                ('Double-Edge', 37),
                ('Sky Attack', 1)
            ],
            'Rattata': [
                ('Tackle', 1),
                ('Tail Whip', 5),
                ('Quick Attack', 10),
                ('Hyper Fang', 15),
                ('Focus Energy', 20),
                ('Super Fang', 25)
            ],
            'Raticate': [
                ('Tackle', 1),
                ('Tail Whip', 1),
                ('Quick Attack', 1),
                ('Hyper Fang', 16),
                ('Focus Energy', 21),
                ('Super Fang', 26)
            ],
            'Spearow': [
                ('Peck', 1),
                ('Growl', 6),
                ('Leer', 11),
                ('Fury Attack', 16),
                ('Mirror Move', 21),
                ('Drill Peck', 26)
            ],
            'Fearow': [
                ('Peck', 1),
                ('Growl', 1),
                ('Leer', 1),
                ('Fury Attack', 16),
                ('Mirror Move', 21),
                ('Drill Peck', 26),
                ('Tri Attack', 1),
                ('Agility', 1),
                ('Whirlwind', 1)
            ],
            'Ekans': [
                ('Wrap', 1),
                ('Leer', 8),
                ('Poison Sting', 15),
                ('Bite', 22),
                ('Glare', 29),
                ('Screech', 36),
                ('Acid', 43)
            ],
            'Arbok': [
                ('Wrap', 1),
                ('Leer', 1),
                ('Poison Sting', 1),
                ('Bite', 22),
                ('Glare', 29),
                ('Screech', 38),
                ('Acid', 47)
            ],
            'Pikachu': [
                ('Thunder Shock', 1),
                ('Growl', 1),
                ('Tail Whip', 9),
                ('Thunder Wave', 17),
                ('Quick Attack', 25),
                ('Swift', 33),
                ('Agility', 41)
            ],
            'Raichu': [
                ('Thunder Shock', 1),
                ('Growl', 1),
                ('Tail Whip', 1),
                ('Thunder Wave', 17),
                ('Quick Attack', 25),
                ('Swift', 33),
                ('Agility', 41),
                ('Thunderbolt', 49)
            ],
            'Sandshrew': [
                ('Scratch', 1),
                ('Sand Attack', 8),
                ('Slash', 15),
                ('Poison Sting', 22),
                ('Swift', 29),
                ('Fury Swipes', 36),
                ('Crush Claw', 43)
            ],
            'Sandslash': [
                ('Scratch', 1),
                ('Sand Attack', 1),
                ('Slash', 15),
                ('Poison Sting', 22),
                ('Swift', 29),
                ('Fury Swipes', 36),
                ('Crush Claw', 45)
            ],
            'Nidoran♀': [
                ('Scratch', 1),
                ('Tail Whip', 7),
                ('Double Kick', 13),
                ('Poison Sting', 19),
                ('Body Slam', 25),
                ('Take Down', 31)
            ],
            'Nidorina': [
                ('Scratch', 1),
                ('Tail Whip', 1),
                ('Double Kick', 13),
                ('Poison Sting', 20),
                ('Body Slam', 27),
                ('Take Down', 34)
            ],
            'Nidoqueen': [
                ('Scratch', 1),
                ('Tail Whip', 1),
                ('Double Kick', 13),
                ('Poison Sting', 20),
                ('Body Slam', 27),
                ('Take Down', 34),
                ('Superpower', 1),
                ('Earthquake', 1),
                ('Cross Chop', 1)
            ],
            'Nidoran♂': [
                ('Peck', 1),
                ('Tail Whip', 7),
                ('Double Kick', 13),
                ('Poison Sting', 19),
                ('Horn Attack', 25),
                ('Fury Attack', 31)
            ],
            'Nidorino': [
                ('Peck', 1),
                ('Tail Whip', 1),
                ('Double Kick', 13),
                ('Poison Sting', 20),
                ('Horn Attack', 27),
                ('Fury Attack', 34)
            ],
            'Nidoking': [
                ('Peck', 1),
                ('Tail Whip', 1),
                ('Double Kick', 13),
                ('Poison Sting', 20),
                ('Horn Attack', 27),
                ('Fury Attack', 34),
                ('Megahorn', 1),
                ('Thunderbolt', 1),
                ('Ice Beam', 1)
            ],
            'Clefairy': [
                ('Pound', 1),
                ('Growl', 5),
                ('Sing', 9),
                ('Double Slap', 13),
                ('Minimize', 17),
                ('Defense Curl', 21),
                ('Metronome', 25)
            ],
            'Clefable': [
                ('Pound', 1),
                ('Growl', 1),
                ('Sing', 1),
                ('Double Slap', 13),
                ('Minimize', 17),
                ('Defense Curl', 21),
                ('Metronome', 25),
                ('Moonblast', 29)
            ],
            'Vulpix': [
                ('Ember', 1),
                ('Tail Whip', 7),
                ('Quick Attack', 13),
                ('Roar', 19),
                ('Confuse Ray', 25),
                ('Flamethrower', 31)
            ],
            'Ninetales': [
                ('Ember', 1),
                ('Tail Whip', 1),
                ('Quick Attack', 13),
                ('Roar', 19),
                ('Confuse Ray', 25),
                ('Flamethrower', 31),
                ('Fire Blast', 37)
            ],
            'Jigglypuff': [
                ('Sing', 1),
                ('Pound', 5),
                ('Disarming Voice', 9),
                ('Double Slap', 13),
                ('Defense Curl', 17),
                ('Rest', 21)
            ],
            'Wigglytuff': [
                ('Sing', 1),
                ('Pound', 1),
                ('Disarming Voice', 1),
                ('Double Slap', 13),
                ('Defense Curl', 17),
                ('Rest', 21),
                ('Play Rough', 25)
            ],
            'Zubat': [
                ('Leech Life', 1),
                ('Supersonic', 7),
                ('Astonish', 13),
                ('Bite', 19),
                ('Wing Attack', 25),
                ('Swift', 31)
            ],
            'Golbat': [
                ('Leech Life', 1),
                ('Supersonic', 1),
                ('Astonish', 13),
                ('Bite', 19),
                ('Wing Attack', 25),
                ('Swift', 31),
                ('Air Cutter', 37)
            ],
            'Oddish': [
                ('Absorb', 1),
                ('Acid', 15),
                ('Sweet Scent', 19),
                ('Poison Powder', 23),
                ('Stun Spore', 27),
                ('Sleep Powder', 31)
            ],
            'Gloom': [
                ('Absorb', 1),
                ('Acid', 1),
                ('Sweet Scent', 19),
                ('Poison Powder', 25),
                ('Stun Spore', 31),
                ('Sleep Powder', 37)
            ],
            'Vileplume': [
                ('Absorb', 1),
                ('Acid', 1),
                ('Sweet Scent', 19),
                ('Poison Powder', 25),
                ('Stun Spore', 31),
                ('Sleep Powder', 37),
                ('Solar Beam', 43)
            ],
            'Paras': [
                ('Scratch', 1),
                ('Stun Spore', 7),
                ('Poison Powder', 13),
                ('Leech Life', 19),
                ('Spore', 25),
                ('Slash', 31)
            ],
            'Parasect': [
                ('Scratch', 1),
                ('Stun Spore', 1),
                ('Poison Powder', 13),
                ('Leech Life', 19),
                ('Spore', 25),
                ('Slash', 31),
                ('Solar Beam', 37)
            ],
            'Venonat': [
                ('Tackle', 1),
                ('Disable', 8),
                ('Foresight', 15),
                ('Leech Life', 22),
                ('Poison Powder', 29),
                ('Psybeam', 36)
            ],
            'Venomoth': [
                ('Tackle', 1),
                ('Disable', 1),
                ('Foresight', 15),
                ('Leech Life', 22),
                ('Poison Powder', 29),
                ('Psybeam', 36),
                ('Psychic', 43)
            ],
            'Diglett': [
                ('Scratch', 1),
                ('Sand Attack', 7),
                ('Slash', 13),
                ('Earthquake', 19),
                ('Mud-Slap', 25)
            ],
            'Dugtrio': [
                ('Scratch', 1),
                ('Sand Attack', 1),
                ('Slash', 13),
                ('Earthquake', 19),
                ('Mud-Slap', 25),
                ('Fissure', 31)
            ],
            'Meowth': [
                ('Scratch', 1),
                ('Growl', 6),
                ('Bite', 11),
                ('Screech', 16),
                ('Fury Swipes', 21),
                ('Slash', 26)
            ],
            'Persian': [
                ('Scratch', 1),
                ('Growl', 1),
                ('Bite', 11),
                ('Screech', 16),
                ('Fury Swipes', 21),
                ('Slash', 26),
                ('Power Gem', 31)
            ],
            'Psyduck': [
                ('Scratch', 1),
                ('Water Gun', 8),
                ('Confusion', 15),
                ('Disable', 22),
                ('Psycho Cut', 29),
                ('Screech', 36)
            ],
            'Golduck': [
                ('Scratch', 1),
                ('Water Gun', 1),
                ('Confusion', 15),
                ('Disable', 22),
                ('Psycho Cut', 29),
                ('Screech', 36),
                ('Hydro Pump', 43)
            ],
            'Mankey': [
                ('Scratch', 1),
                ('Leer', 7),
                ('Low Kick', 13),
                ('Karate Chop', 19),
                ('Fury Swipes', 25),
                ('Seismic Toss', 31)
            ],
            'Primeape': [
                ('Scratch', 1),
                ('Leer', 1),
                ('Low Kick', 13),
                ('Karate Chop', 19),
                ('Fury Swipes', 25),
                ('Seismic Toss', 31),
                ('Cross Chop', 37)
            ],
            'Growlithe': [
                ('Bite', 1),
                ('Roar', 8),
                ('Ember', 15),
                ('Leer', 22),
                ('Take Down', 29),
                ('Agility', 36)
            ],
            'Arcanine': [
                ('Bite', 1),
                ('Roar', 1),
                ('Ember', 15),
                ('Leer', 22),
                ('Take Down', 29),
                ('Agility', 36),
                ('Flare Blitz', 43)
            ],
            'Poliwag': [
                ('Bubble', 1),
                ('Hypnosis', 15),
                ('Water Gun', 23),
                ('Double Slap', 31),
                ('Body Slam', 39)
            ],
            'Poliwhirl': [
                ('Bubble', 1),
                ('Hypnosis', 1),
                ('Water Gun', 23),
                ('Double Slap', 31),
                ('Body Slam', 39),
                ('Mud Shot', 47)
            ],
            'Poliwrath': [
                ('Bubble', 1),
                ('Hypnosis', 1),
                ('Water Gun', 23),
                ('Double Slap', 31),
                ('Body Slam', 39),
                ('Mud Shot', 47),
                ('Dynamic Punch', 55)
            ],
            'Abra': [
                ('Teleport', 1)
            ],
            'Kadabra': [
                ('Teleport', 1),
                ('Kinesis', 1),
                ('Confusion', 16),
                ('Disable', 20),
                ('Psycho Cut', 24),
                ('Recover', 28),
                ('Psychic', 32)
            ],
            'Alakazam': [
                ('Teleport', 1),
                ('Kinesis', 1),
                ('Confusion', 16),
                ('Disable', 20),
                ('Psycho Cut', 24),
                ('Recover', 28),
                ('Psychic', 32)
            ],
            'Machop': [
                ('Low Kick', 1),
                ('Leer', 7),
                ('Focus Energy', 13),
                ('Karate Chop', 19),
                ('Low Sweep', 25),
                ('Seismic Toss', 31)
            ],
            'Machoke': [
                ('Low Kick', 1),
                ('Leer', 1),
                ('Focus Energy', 13),
                ('Karate Chop', 19),
                ('Low Sweep', 25),
                ('Seismic Toss', 31),
                ('Submission', 37)
            ],
            'Machamp': [
                ('Low Kick', 1),
                ('Leer', 1),
                ('Focus Energy', 13),
                ('Karate Chop', 19),
                ('Low Sweep', 25),
                ('Seismic Toss', 31),
                ('Submission', 37),
                ('Cross Chop', 43)
            ],
            'Bellsprout': [
                ('Vine Whip', 1),
                ('Growth', 7),
                ('Wrap', 13),
                ('Sleep Powder', 19),
                ('Poison Powder', 25),
                ('Sludge', 31)
            ],
            'Weepinbell': [
                ('Vine Whip', 1),
                ('Growth', 1),
                ('Wrap', 13),
                ('Sleep Powder', 19),
                ('Poison Powder', 25),
                ('Sludge', 31),
                ('Acid', 37)
            ],
            'Victreebel': [
                ('Vine Whip', 1),
                ('Growth', 1),
                ('Wrap', 13),
                ('Sleep Powder', 19),
                ('Poison Powder', 25),
                ('Sludge', 31),
                ('Acid', 37),
                ('Leaf Storm', 43)
            ],
            'Tentacool': [
                ('Acid', 1),
                ('Poison Sting', 10),
                ('Supersonic', 15),
                ('Wrap', 20),
                ('Water Pulse', 25),
                ('Hydro Pump', 30)
            ],
            'Tentacruel': [
                ('Acid', 1),
                ('Poison Sting', 1),
                ('Supersonic', 15),
                ('Wrap', 20),
                ('Water Pulse', 25),
                ('Hydro Pump', 30),
                ('Sludge Wave', 35)
            ],
            'Geodude': [
                ('Tackle', 1),
                ('Defense Curl', 1),
                ('Rock Throw', 9),
                ('Magnitude', 17),
                ('Self-Destruct', 25),
                ('Rock Slide', 33)
            ],
            'Graveler': [
                ('Tackle', 1),
                ('Defense Curl', 1),
                ('Rock Throw', 9),
                ('Magnitude', 17),
                ('Self-Destruct', 25),
                ('Rock Slide', 33),
                ('Earthquake', 41)
            ],
            'Golem': [
                ('Tackle', 1),
                ('Defense Curl', 1),
                ('Rock Throw', 9),
                ('Magnitude', 17),
                ('Self-Destruct', 25),
                ('Rock Slide', 33),
                ('Earthquake', 41),
                ('Explosion', 49)
            ],
            'Ponyta': [
                ('Tackle', 1),
                ('Growl', 5),
                ('Tail Whip', 10),
                ('Ember', 15),
                ('Stomp', 20),
                ('Flame Charge', 25),
                ('Take Down', 30)
            ],
            'Rapidash': [
                ('Tackle', 1),
                ('Growl', 1),
                ('Tail Whip', 10),
                ('Ember', 15),
                ('Stomp', 20),
                ('Flame Charge', 25),
                ('Take Down', 30),
                ('Inferno', 35)
            ],
            'Slowpoke': [
                ('Tackle', 1),
                ('Growl', 1),
                ('Water Gun', 9),
                ('Confusion', 17),
                ('Disable', 25),
                ('Psychic', 33)
            ],
            'Slowbro': [
                ('Tackle', 1),
                ('Growl', 1),
                ('Water Gun', 1),
                ('Confusion', 17),
                ('Disable', 25),
                ('Psychic', 33),
                ('Amnesia', 41)
            ],
            'Magnemite': [
                ('Tackle', 1),
                ('Thunder Shock', 1),
                ('Thunder Wave', 15),
                ('Thunderbolt', 30)
            ],
            'Magneton': [
                ('Tackle', 1),
                ('Thunder Shock', 1),
                ('Thunder Wave', 15),
                ('Thunderbolt', 30),
                ('Magnet Bomb', 45)
            ],
            "Farfetch'd": [
                ('Peck', 1),
                ('Sand Attack', 1),
                ('Leer', 15),
                ('Fury Attack', 30),
                ('Swords Dance', 45)
            ],
            'Doduo': [
                ('Peck', 1),
                ('Growl', 1),
                ('Quick Attack', 15),
                ('Rage', 30),
                ('Double Kick', 45)
            ],
            'Dodrio': [
                ('Peck', 1),
                ('Growl', 1),
                ('Quick Attack', 15),
                ('Rage', 30),
                ('Double Kick', 45),
                ('Drill Peck', 60)
            ],
                'Seel': [
                ('Headbutt', 1),
                ('Growl', 15),
                ('Aqua Tail', 30),
                ('Icy Wind', 45)
            ],
            'Dewgong': [
                ('Headbutt', 1),
                ('Growl', 1),
                ('Aqua Tail', 30),
                ('Icy Wind', 45),
                ('Aurora Beam', 60)
            ],
            'Grimer': [
                ('Pound', 1),
                ('Poison Gas', 15),
                ('Mud-Slap', 20),
                ('Sludge', 25),
                ('Sludge Bomb', 30)
            ],
            'Muk': [
                ('Pound', 1),
                ('Poison Gas', 1),
                ('Mud-Slap', 20),
                ('Sludge', 25),
                ('Sludge Bomb', 30),
                ('Gunk Shot', 35)
            ],
            'Shellder': [
                ('Tackle', 1),
                ('Withdraw', 15),
                ('Icicle Spear', 30),
                ('Clamp', 45)
            ],
            'Cloyster': [
                ('Tackle', 1),
                ('Withdraw', 15),
                ('Icicle Spear', 30),
                ('Clamp', 45),
                ('Aurora Beam', 60)
            ],
            'Gastly': [
                ('Lick', 1),
                ('Spite', 7),
                ('Mean Look', 13),
                ('Curse', 19),
                ('Night Shade', 25)
            ],
            'Haunter': [
                ('Lick', 1),
                ('Spite', 1),
                ('Mean Look', 13),
                ('Curse', 19),
                ('Night Shade', 25),
                ('Shadow Punch', 31)
            ],
            'Gengar': [
                ('Lick', 1),
                ('Spite', 1),
                ('Mean Look', 13),
                ('Curse', 19),
                ('Night Shade', 25),
                ('Shadow Punch', 31),
                ('Dream Eater', 37)
            ],
            'Onix': [
                ('Tackle', 1),
                ('Screech', 15),
                ('Rock Throw', 30),
                ('Rock Slide', 45)
            ],
            'Drowzee': [
                ('Pound', 1),
                ('Hypnosis', 15),
                ('Poison Gas', 20),
                ('Psychic', 25),
                ('Meditate', 30)
            ],
            'Hypno': [
                ('Pound', 1),
                ('Hypnosis', 1),
                ('Poison Gas', 20),
                ('Psychic', 25),
                ('Meditate', 30),
                ('Psycho Cut', 35)
            ],
            'Krabby': [
                ('Bubble', 1),
                ('Leer', 7),
                ('Mud Shot', 15),
                ('Stomp', 23),
                ('Crabhammer', 31)
            ],
            'Kingler': [
                ('Bubble', 1),
                ('Leer', 1),
                ('Mud Shot', 15),
                ('Stomp', 23),
                ('Crabhammer', 31),
                ('Hyper Beam', 39)
            ],
            'Voltorb': [
                ('Tackle', 1),
                ('Screech', 15),
                ('Sonic Boom', 20),
                ('Spark', 25),
                ('Self-Destruct', 30)
            ],
            'Electrode': [
                ('Tackle', 1),
                ('Screech', 15),
                ('Sonic Boom', 20),
                ('Spark', 25),
                ('Self-Destruct', 30),
                ('Light Screen', 35)
            ],
            'Exeggcute': [
                ('Barrage', 1),
                ('Hypnosis', 1),
                ('Reflect', 16),
                ('Leech Seed', 21),
                ('Psychic', 26),
                ('Solar Beam', 31)
            ],
            'Exeggutor': [
                ('Barrage', 1),
                ('Hypnosis', 1),
                ('Reflect', 16),
                ('Leech Seed', 21),
                ('Psychic', 26),
                ('Solar Beam', 31),
                ('Psych Up', 36)
            ],
            'Cubone': [
                ('Growl', 1),
                ('Tail Whip', 4),
                ('Bone Club', 8),
                ('Headbutt', 13),
                ('Leer', 19),
                ('Focus Energy', 26)
            ],
            'Marowak': [
                ('Growl', 1),
                ('Tail Whip', 1),
                ('Bone Club', 1),
                ('Headbutt', 13),
                ('Leer', 19),
                ('Focus Energy', 26),
                ('Bone Rush', 34)
            ],
            'Hitmonlee': [
                ('Double Kick', 1),
                ('Meditate', 1),
                ('Rolling Kick', 20),
                ('Jump Kick', 35),
                ('High Jump Kick', 50)
            ],
            'Hitmonchan': [
                ('Comet Punch', 1),
                ('Agility', 1),
                ('Thunder Punch', 20),
                ('Fire Punch', 35),
                ('Ice Punch', 50)
            ],
            'Lickitung': [
                ('Lick', 1),
                ('Supersonic', 1),
                ('Defense Curl', 15),
                ('Stomp', 20),
                ('Wrap', 25),
                ('Slam', 30)
            ],
            'Koffing': [
                ('Tackle', 1),
                ('Smog', 1),
                ('SmokeScreen', 17),
                ('Sludge', 21),
                ('Self-Destruct', 25),
                ('Haze', 29)
            ],
            'Weezing': [
                ('Tackle', 1),
                ('Smog', 1),
                ('SmokeScreen', 17),
                ('Sludge', 21),
                ('Self-Destruct', 25),
                ('Haze', 29),
                ('Explosion', 33)
            ],
            'Rhyhorn': [
                ('Horn Attack', 1),
                ('Tail Whip', 1),
                ('Fury Attack', 15),
                ('Scary Face', 20),
                ('Rock Blast', 25)
            ],
            'Rhydon': [
                ('Horn Attack', 1),
                ('Tail Whip', 1),
                ('Fury Attack', 15),
                ('Scary Face', 20),
                ('Rock Blast', 25),
                ('Horn Drill', 30)
            ],
            'Chansey': [
                ('Pound', 1),
                ('Growl', 1),
                ('Tail Whip', 5),
                ('Soft-Boiled', 10),
                ('Double Slap', 15),
                ('Minimize', 20)
            ],
            'Tangela': [
                ('Ingrain', 1),
                ('Sleep Powder', 1),
                ('Absorb', 16),
                ('Giga Drain', 21),
                ('Sludge Bomb', 26)
            ],
            'Kangaskhan': [
                ('Comet Punch', 1),
                ('Leer', 1),
                ('Bite', 10),
                ('Tail Whip', 15),
                ('Mega Punch', 20),
                ('Dizzy Punch', 25)
            ],
            'Horsea': [
                ('Bubble', 1),
                ('SmokeScreen', 15),
                ('Leer', 20),
                ('Bubble Beam', 25),
                ('Agility', 30)
            ],
            'Seadra': [
                ('Bubble', 1),
                ('SmokeScreen', 15),
                ('Leer', 20),
                ('Bubble Beam', 25),
                ('Agility', 30),
                ('Hydro Pump', 35)
            ],
            'Goldeen': [
                ('Peck', 1),
                ('Tail Whip', 1),
                ('Water Gun', 15),
                ('Horn Attack', 20),
                ('Fury Attack', 25),
                ('Waterfall', 30)
            ],
            'Seaking': [
                ('Peck', 1),
                ('Tail Whip', 1),
                ('Water Gun', 15),
                ('Horn Attack', 20),
                ('Fury Attack', 25),
                ('Waterfall', 30),
                ('Megahorn', 35)
            ],
            'Staryu': [
                ('Tackle', 1),
                ('Harden', 1),
                ('Water Gun', 15),
                ('Rapid Spin', 20),
                ('Recover', 25),
                ('Bubble Beam', 30)
            ],        
            'Starmie': [
                ('Tackle', 1),
                ('Harden', 1),
                ('Water Gun', 15),
                ('Rapid Spin', 20),
                ('Recover', 25),
                ('Bubble Beam', 30),
                ('Light Screen', 35)
            ],
            'Mr. Mime': [
                ('Barrier', 1),
                ('Confusion', 1),
                ('Meditate', 20),
                ('Double Slap', 25),
                ('Light Screen', 30)
            ],
            'Scyther': [
                ('Quick Attack', 1),
                ('Leer', 1),
                ('Focus Energy', 20),
                ('Double Team', 25),
                ('Slash', 30),
                ('Swords Dance', 35)
            ],
            'Jynx': [
                ('Pound', 1),
                ('Lick', 1),
                ('Lovely Kiss', 20),
                ('Powder Snow', 25),
                ('Double Slap', 30)
            ],
            'Electabuzz': [
                ('Quick Attack', 1),
                ('Leer', 1),
                ('Thunder Shock', 20),
                ('Thunder Punch', 25),
                ('Screech', 30)
            ],
            'Magmar': [
                ('Ember', 1),
                ('Leer', 1),
                ('SmokeScreen', 20),
                ('Fire Punch', 25),
                ('Sunny Day', 30)
            ],
            'Pinsir': [
                ('Vice Grip', 1),
                ('Focus Energy', 1),
                ('Seismic Toss', 20),
                ('Guillotine', 25),
                ('Harden', 30)
            ],
            'Tauros': [
                ('Tackle', 1),
                ('Tail Whip', 1),
                ('Stomp', 20),
                ('Leer', 25),
                ('Horn Attack', 30)
            ],
            'Magikarp': [
                ('Splash', 1)
            ],
            'Gyarados': [
                ('Bite', 1),
                ('Dragon Rage', 1),
                ('Twister', 20),
                ('Hydro Pump', 30)
            ],
            'Lapras': [
                ('Water Gun', 1),
                ('Growl', 1),
                ('Sing', 15),
                ('Mist', 20),
                ('Ice Beam', 25),
                ('Body Slam', 30)
            ],
            'Ditto': [
                ('Transform', 1)
            ],
            'Eevee': [
                ('Tackle', 1),
                ('Tail Whip', 1),
                ('Sand Attack', 20),
                ('Quick Attack', 25),
                ('Bite', 30)
            ],
            'Vaporeon': [
                ('Tackle', 1),
                ('Tail Whip', 1),
                ('Sand Attack', 20),
                ('Quick Attack', 25),
                ('Bite', 30),
                ('Water Gun', 35)
            ],
            'Jolteon': [
                ('Tackle', 1),
                ('Tail Whip', 1),
                ('Sand Attack', 20),
                ('Quick Attack', 25),
                ('Double Kick', 30),
                ('Thunderbolt', 35)
            ],
            'Flareon': [
                ('Tackle', 1),
                ('Tail Whip', 1),
                ('Sand Attack', 20),
                ('Quick Attack', 25),
                ('Ember', 30),
                ('Fire Blast', 35)
            ],
            'Porygon': [
                ('Tackle', 1),
                ('Conversion', 1),
                ('Agility', 15),
                ('Psychic', 20),
                ('Recover', 25),
                ('Tri Attack', 30)
            ],
            'Omanyte': [
                ('Water Gun', 1),
                ('Withdraw', 1),
                ('Bite', 15),
                ('Rollout', 20),
                ('Leer', 25),
                ('Rock Blast', 30)
            ],
            'Omastar': [
                ('Water Gun', 1),
                ('Withdraw', 1),
                ('Bite', 15),
                ('Rollout', 20),
                ('Leer', 25),
                ('Rock Blast', 30),
                ('Hydro Pump', 35)
            ],
            'Kabuto': [
                ('Scratch', 1),
                ('Harden', 1),
                ('Absorb', 15),
                ('Slash', 20),
                ('Leer', 25),
                ('Rock Blast', 30)
            ],
            'Kabutops': [
                ('Scratch', 1),
                ('Harden', 1),
                ('Absorb', 15),
                ('Slash', 20),
                ('Leer', 25),
                ('Rock Blast', 30),
                ('Megahorn', 35)
            ],
            'Aerodactyl': [
                ('Bite', 1),
                ('Wing Attack', 1),
                ('Agility', 20),
                ('Take Down', 25),
                ('Hyper Beam', 30)
            ],
            'Snorlax': [
                ('Tackle', 1),
                ('Amnesia', 1),
                ('Headbutt', 15),
                ('Body Slam', 20),
                ('Harden', 25),
                ('Double-Edge', 30)
            ],
            'Articuno': [
                ('Peck', 1),
                ('Growl', 1),
                ('Mist', 20),
                ('Ice Beam', 25),
                ('Agility', 30),
                ('Blizzard', 35)
            ],        
        'Zapdos': [
                ('Peck', 1),
                ('Growl', 1),
                ('Thunder Shock', 20),
                ('Thunder Wave', 25),
                ('Agility', 30),
                ('Thunderbolt', 35)
            ],
            'Moltres': [
                ('Peck', 1),
                ('Growl', 1),
                ('Ember', 20),
                ('Fire Spin', 25),
                ('Agility', 30),
                ('Flamethrower', 35)
            ],
            'Dratini': [
                ('Wrap', 1),
                ('Leer', 1),
                ('Thunder Wave', 20),
                ('Agility', 25),
                ('Slam', 30)
            ],
            'Dragonair': [
                ('Wrap', 1),
                ('Leer', 1),
                ('Thunder Wave', 20),
                ('Agility', 25),
                ('Slam', 30),
                ('Hyper Beam', 35)
            ],
            'Dragonite': [
                ('Wrap', 1),
                ('Leer', 1),
                ('Thunder Wave', 20),
                ('Agility', 25),
                ('Slam', 30),
                ('Hyper Beam', 35),
                ('Dragon Rage', 40)
            ],
            'Mewtwo': [
                ('Confusion', 1),
                ('Disable', 1),
                ('Psychic', 20),
                ('Swift', 25),
                ('Future Sight', 30)
            ],
            'Mew': [
                ('Pound', 1),
                ('Transform', 1)
            ]
        }

    def __new__(cls):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.__init__()
        return cls.instance
###########################END All learnable Moves################
############################"All Evolutions##############################
class All_Evolutions:
    instance = None
    def __init__(self):
        ################Evolution database##################
        #if it's 0 it means it evolves with an item or in another way
        #if you get a KeyError it means the pokemon doesn't have any evolutions left
        self.  evolutions = {
            "Bulbasaur": (16, "Ivysaur"),
            "Ivysaur": (32, "Venusaur"),
            "Charmander": (16, "Charmeleon"),
            "Charmeleon": (36, "Charizard"),
            "Squirtle": (16, "Wartortle"),
            "Wartortle": (36, "Blastoise"),
            "Caterpie": (7, "Metapod"),
            "Metapod": (10, "Butterfree"),
            "Weedle": (7, "Kakuna"),
            "Kakuna": (10, "Beedrill"),
            "Pidgey": (18, "Pidgeotto"),
            "Pidgeotto": (36, "Pidgeot"),
            "Rattata": (20, "Raticate"),
            "Spearow": (20, "Fearow"),
            "Ekans": (22, "Arbok"),
            "Sandshrew": (22, "Sandslash"),
            "Nidoran♀": (16, "Nidorina"),
            "Nidorina": (32, "Nidoqueen"),
            "Nidoran♂": (16, "Nidorino"),
            "Nidorino": (32, "Nidoking"),
            "Zubat": (22, "Golbat"),
            "Oddish": (21, "Gloom"),
            "Paras": (24, "Parasect"),
            "Venonat": (31, "Venomoth"),
            "Diglett": (26, "Dugtrio"),
            "Meowth": (28, "Persian"),
            "Psyduck": (33, "Golduck"),
            "Mankey": (28, "Primeape"),
            "Poliwag": (25, "Poliwhirl"),
            "Abra": (16, "Kadabra"),
            "Machop": (28, "Machoke"),
            "Bellsprout": (21, "Weepinbell"),
            "Tentacool": (30, "Tentacruel"),
            "Geodude": (25, "Graveler"),
            "Ponyta": (40, "Rapidash"),
            "Slowpoke": (37, "Slowbro"),
            "Magnemite": (30, "Magneton"),
            "Doduo": (31, "Dodrio"),
            "Seel": (34, "Dewgong"),
            "Grimer": (38, "Muk"),
            "Shellder": (36, "Cloyster"),
            "Gastly": (25, "Haunter"),
            "Drowzee": (26, "Hypno"),
            "Krabby": (28, "Kingler"),
            "Voltorb": (30, "Electrode"),
            "Exeggcute": (42, "Exeggutor"),
            "Cubone": (28, "Marowak"),
            "Lickitung": (33, "Lickilicky"),
            "Koffing": (35, "Weezing"),
            "Rhyhorn": (42, "Rhydon"),
            "Horsea": (32, "Seadra"),
            "Goldeen": (33, "Seaking"),
            "Staryu": (34, "Starmie"),
            "Scyther": (50, "Scizor"),
            "Jynx": (32, "Jynx"),
            "Electabuzz": (50, "Electivire"),
            "Magmar": (50, "Magmortar"),
            "Pinsir": (50, "Pinsir"),
            "Tauros": (50, "Tauros"),
            "Magikarp": (20, "Gyarados"),
            "Jynx": (30, "Smoochum"),
            "Goldeen": (33, "Seaking"),
            "Omanyte": (40, "Omastar"),
            "Kabuto": (40, "Kabutops"),
            "Dratini": (30, "Dragonair"),
            "Dragonair": (55, "Dragonite"),

            "Gloom": (0, "Vileplume"),
            "Pikachu": (0, "Raichu"),
            "Machoke": (0, "Machamp"),
            "Weepinbell": (0, "Victreebel"),
            "Kadabra": (0, "Alakazam"),
            "Poliwhirl": (0, "Poliwrath"),
            "Growlithe": (0, "Arcanine"),
            "Clefairy": (0, "Clefable"),
            "Vulpix": (0, "Ninetales"),
            "Jigglypuff": (0, "Wigglytuff"),
            "Graveler": (0, "Golem"),
            "Staryu": (0, "Starmie"),
            "Scyther": (0, "Scizor"),
            "Electabuzz": (0, "Electivire"),
            "Magmar": (0, "Magmortar"),
            "Eevee": (0, "Vaporeon"),
            "Eevee": (0, "Jolteon"),
            "Eevee": (0, "Flareon")
        }

    def __new__(cls):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.__init__()
        return cls.instance

#############################END All Evolutions###########################

#######################Tests#################################""
"""
pokemon_list = initialize_all_pokemons()

pikachu_object = find_pokemon_by_name("Pikachu", pokemon_list)
print(f"{pikachu_object.name} is at level {pikachu_object.level}.")


pikachu_object.display_stats()
level_up(pikachu_object)
pikachu_object.display_stats()
#Print his attacks
for move in pikachu_object.moves :
    print(move.name)

"""   



###############################TESTS###########################################
# Assume that the dictionary is stored in a variable called 'moves_by_level'

"""
moves_by_pokemon = All_Learnable_Moves().moves_by_pokemon
# Get the moves that a Bulbasaur can learn
bulbasaur_moves = moves_by_pokemon['Bulbasaur']

#print(bulbasaur_moves[0][0])
#print(bulbasaur_moves[0][1])

# Loop through all levels and moves that a Bulbasaur can learn
for moves, level in bulbasaur_moves:
  print(f"Bulbasaur can learn the following moves at level {level} : {moves}")


pokemon_list = initialize_all_pokemons()
bulbasaur = find_pokemon_by_name("Bulbasaur", pokemon_list)
bulbasaur1 = create_copy_pokemon(bulbasaur)

#display_pokemon_moves(bulbasaur1)
bulbasaur1.go_to_lvl(13)
bulbasaur1.go_to_lvl(28)
bulbasaur1.go_to_lvl(35)

display_pokemon_moves(bulbasaur1)
bulbasaur1.display_stats()
"""
##############################################################################