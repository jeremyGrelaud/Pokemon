import random
from pokemon import All_Pokemons, create_copy_pokemon, create_pokemon, find_pokemon_by_name, level_up
from trainer import Trainer

def calculate_damage(current_pokemon, other_pokemon, current_move):
    #we select the highest between atk spe and atk
    if(current_pokemon.attack > current_pokemon.special_attack):
        check = ( ( (((2*current_pokemon.level)//5)+2)*(current_pokemon.attack //other_pokemon.defense) * current_move.attack_power + 2 )//50)
    else:
        check = ( ( (((2*current_pokemon.level)//5)+2)*(current_pokemon.special_attack //other_pokemon.special_defense) * current_move.attack_power + 2 )//50)
    
    if(check >= 0):
        return check
    else:
        return 0

    #il faudrait rajouter la faiblesse des types (*0.5 *1 ou *2) ainsi que les crit *1 ou *2, ainsi que le STAB *1.5


class Combat:
  def __init__(self, trainer1, trainer2):
    self.trainer1 = trainer1
    self.trainer2 = trainer2
    self.current_trainer = self.trainer1
    self.other_trainer = self.trainer2
    self.current_pokemon = self.trainer1.pokemon_list[0]
    self.other_pokemon = self.trainer2.pokemon_list[0]
  
  def swicth_to_player(self):
        old_curr_trainer = self.current_trainer
        old_other_trainer = self.other_trainer
        old_curr_pokemon = self.current_pokemon
        old_other_pokemon = self.other_pokemon
        #we switch
        self.current_trainer = old_other_trainer
        self.other_trainer = old_curr_trainer
        self.current_pokemon = old_other_pokemon
        self.other_pokemon = old_curr_pokemon
 


  def start_battle(self):
    print(f"{self.trainer1.name} is challenging {self.trainer2.name} to a pokemon battle!")
    print(f"{self.trainer1.name} sends out {self.current_pokemon.name}!")
    print(f"{self.trainer2.name} sends out {self.other_pokemon.name}!")

  def choose_move(self):
    print(f"{self.current_trainer.name}, choose a move for {self.current_pokemon.name}:")
    for i, move in enumerate(self.current_pokemon.moves):
      print(f"{i+1}. {move.name} (Power: {move.attack_power}, Accuracy: {move.accuracy}%)")
    choice = int(input()) - 1
    return self.current_pokemon.moves[choice]
 

  def switch_pokemon(self):
    if len(self.current_trainer.pokemon_list) > 0:
      print(f"{self.current_trainer.name}, do you want to switch pokemon?")
      choice = input("Enter y for Yes or n for No: ")
      if choice == "y" or choice == "Y":
        print(f"{self.current_trainer.name}, choose a new pokemon:")
        for i, pokemon in enumerate(self.current_trainer.pokemon_list):
          print(f"{i+1}. {pokemon.name} (Level {pokemon.level})")
        choice = int(input()) - 1
        self.current_pokemon = self.current_trainer.pokemon_list[choice]
        print(f"{self.current_trainer.name} has switched to {self.current_pokemon.name}!")
      else:
        print(f"{self.current_trainer.name} has chosen to keep {self.current_pokemon.name} in battle.")
    else:
      print(f"{self.current_trainer.name} has no other pokemon to switch to.")


  def attack(self):
    move = self.choose_move()
    if random.uniform(0, 1) <= move.accuracy/100:
      # Calculate the damage dealt by the attacker
      damage = calculate_damage(self.current_pokemon,self.other_pokemon, move)
      self.other_pokemon.hp -= damage
      print(f"{self.current_pokemon.name} used {move.name} and dealt {damage} damage to {self.other_pokemon.name}!")
    else:
      print(f"{self.current_pokemon.name}'s attack missed!")

  
  def check_if_fainted(self, pokemon):
    if pokemon.hp <= 0:
        print(f"{pokemon.name} has fainted!")
        return True
    return False

  def show_hp_pokemons(self):
    print(f"{self.current_trainer.name}'s {self.current_pokemon.name} has {self.current_pokemon.hp} hp left ")
    print(f"{self.other_trainer.name}'s {self.other_pokemon.name} has {self.other_pokemon.hp} hp left ")

def battle(self):
    # Start the battle
    self.start_battle()
    trainer1 = self.trainer1 
    trainer2 = self.trainer2

    # Continue the battle until one trainer's pokemon have all fainted
    while True:
        # Trainer 1 attacks
        self.attack()
        self.show_hp_pokemons()
        fainted = self.check_if_fainted(self.other_pokemon)
        
        self.swicth_to_player() #we switch to player2
        if fainted:
            self.current_trainer.remove_pokemon(self.current_pokemon)
            if len(self.current_trainer.pokemon_list) > 0:
                self.switch_pokemon()
            else:
                print(f"{self.current_trainer.name} has no more pokemon left!")
                print(f"{self.other_trainer.name} wins!")
                break

        # Trainer 2 attacks
        self.attack()
        self.show_hp_pokemons()
        fainted = self.check_if_fainted(self.other_pokemon)

        self.swicth_to_player() #we switch back to player1
        if fainted:
            self.current_trainer.remove_pokemon(self.current_pokemon)
            if len(self.current_trainer.pokemon_list) > 0:
                self.switch_pokemon()
            else:
                print(f"{self.current_trainer.name} has no more pokemon left!")
                print(f"{self.other_trainer.name} wins!")
                break   



###################TESTS#######################"
# Initialize a trainer with some pokemon
pokemon_list = All_Pokemons().pokemon_list

pikachu = find_pokemon_by_name("Pikachu", pokemon_list)
pikachu1 = create_copy_pokemon(pikachu)
pikachu2 = create_copy_pokemon(pikachu)
squirtle = find_pokemon_by_name("Squirtle", pokemon_list)
bulbasaur = find_pokemon_by_name("Bulbasaur", pokemon_list)

for i in range (0,90):
    level_up(pikachu1)

ash = Trainer("Ash", [pikachu1, squirtle])
red = Trainer("Red", [pikachu2, bulbasaur])

combat1 = Combat(ash, red)
#print(f"You've chosen : {combat1.choose_move().name}")

#combat1.start_battle()
#combat1.attack()

battle(combat1)