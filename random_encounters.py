import random
from items import All_Items, get_item_by_name

from pokemon import All_Pokemons, attack, create_copy_pokemon, defeated_pokemon_experience, find_pokemon_by_name, find_pokemon_by_position, level_up
from trainer import Trainer

class WildCombat:
  def __init__(self, trainer, wild_pokemon):
    self.trainer = trainer
    self.wild_pokemon = wild_pokemon
    self.current_trainer_pokemon = self.trainer.pokemon_list[0]
    self.current_wild_pokemon = self.wild_pokemon

  def start_battle(self):
    print(f"A wild {self.current_wild_pokemon.name} has appeared!")
    # The battle continues as long as both the trainer and wild pokemon have at least one non-fainted pokemon
    while self.trainer.has_non_fainted_pokemon() and not self.wild_pokemon.is_fainted():
      # Display the current status of the trainer's and wild pokemon's teams
      self.trainer.print_team_status()
      print(f"{self.wild_pokemon.name}'s health: {self.wild_pokemon.hp}/{self.wild_pokemon.max_hp}")

      #if trainer's pokemon si fainted force the switch 
      if(self.current_trainer_pokemon.is_fainted()):
        self.forced_switch_pokemon()

      combat = False
      # Display the options for the trainer
      print("What do you want to do?")
      print("1. Attack")
      print("2. Switch Pokemon")
      print("3. Catch Pokemon")
      print("4. Run Away")

      # Get the trainer's choice
      choice = input("Enter the number of your choice: ")

      if choice == "1":
        # Attack the wild pokemon
        combat = True
        #but determine which ones attack first dependin of their speed
        if(self.current_trainer_pokemon.speed > self.current_wild_pokemon.speed):
          attack(self.current_trainer_pokemon, self.current_wild_pokemon, self.current_trainer_pokemon.choose_move())
          if not self.current_wild_pokemon.is_fainted(): 
            attack(self.current_wild_pokemon, self.current_trainer_pokemon, self.current_wild_pokemon.get_random_move())
        else:
          attack(self.current_wild_pokemon, self.current_trainer_pokemon, self.current_wild_pokemon.get_random_move())
          if not self.current_trainer_pokemon.is_fainted(): 
            attack(self.current_trainer_pokemon, self.current_wild_pokemon, self.current_trainer_pokemon.choose_move())
      
      elif choice == "2":
        # Switch to a different pokemon
        self.switch_pokemon()
      elif choice == "3":
        #choose pokeball to use between thoose present in the trainer bag
        all_items = All_Items()
        pokeball_chosen = get_item_by_name(all_items.items, "Pokeball")
        #for the test for now we use pokeballs

      
        # Attempt to catch the wild pokemon
        result = self.attempt_catch(pokeball_chosen)
        if(result):
          #we need to stop the fight with this pokemon
          return 
          #encounter_wild_pokemon(self.trainer)

          #je dissocie pas bien le pokemon capturé on tente une copie mais le dernier que j'ai capturé continue de m'attaquer :)
          #les max hp sont pas bon aussi x)

      elif choice == "4":
        # Run away from the battle
        print("You ran away from the battle!")
        break
      else:
        print("Invalid choice. Please try again.")

      # The wild pokemon attacks if it has not fainted
      if not self.wild_pokemon.is_fainted():
        if not combat == True :
          #######################################################définir une attaque random
          #print(self.current_wild_pokemon.get_random_move().name)
          attack(self.current_wild_pokemon, self.current_trainer_pokemon, self.current_wild_pokemon.get_random_move())
      else :
        experience = defeated_pokemon_experience(self.current_wild_pokemon, self.current_trainer_pokemon)
        self.current_trainer_pokemon.gain_experience(experience)
        # The battle ends
        print(f"{self.current_wild_pokemon.name} has fainted, {self.current_trainer_pokemon.name}'s gained {experience} exp")

        #We display the exp needed for next level
        self.current_trainer_pokemon.display_experience_bar()


    
  def attempt_catch(self, pokeball_used):
    print(f"{self.trainer.name} is attempting to catch {self.wild_pokemon.name}...")
      
    #if it's a Masterball you caught the pokemon
    if(pokeball_used.name == "Master Ball"):
      print(f"{self.wild_pokemon.name} was caught!")
      self.trainer.pokemon_list.append(create_copy_pokemon(self.wild_pokemon))
      return True
    else:
      #Generating a random number N : 0 to 255 for pokeball 0 to 200 for superball and 0 to 150 for ultra ball
      N = random.randint(0, pokeball_used.catch_rate)
      s=0
      #caught if pokemon asleep or frozen and N < 25
      if(self.wild_pokemon.status == "asleep" or "frozen"):
        temp_status = 25
        s=10
        if(N<25):
          print(f"{self.wild_pokemon.name} was caught!")
          self.trainer.pokemon_list.append(create_copy_pokemon(self.wild_pokemon))
          return True
      #caught if paralyzed, burned or poisoned and N < 12
      elif(self.wild_pokemon.status == "paralyzed" or "burned" or "poisoned"):
        temp_status = 12
        s=5
        if(N<12):
          print(f"{self.wild_pokemon.name} was caught!")
          self.trainer.pokemon_list.append(create_copy_pokemon(self.wild_pokemon))
          return True
      

      #otherwise if N - status threshold above is greater than pokemon's catch rate --> break free
      if(N-temp_status > self.wild_pokemon.catch_rate):
        print(f"{self.wild_pokemon.name} broke free  immediately!") 
      else:
        M = random.randint(0, 255)
        if(pokeball_used.name == "Geat Ball"):
          Ball = 8
        elif(pokeball_used.name == "Ultra Ball"):
          Ball = 6
        else:
          Ball = 12
        f = (self.wild_pokemon.max_hp * 255 * 4) / (self.wild_pokemon.hp * Ball)
        #f between 1 and 255

        if(f >= M):
          print(f"{self.wild_pokemon.name} was caught!")
          self.trainer.pokemon_list.append(create_copy_pokemon(self.wild_pokemon))
          return True
        else:
          #not caught but we now determine how many times the pokeball will shake
          d = (self.wild_pokemon.catch_rate * 100) / pokeball_used.catch_rate
          if(d>=256):
            print(f"Pokeball shook 3 times then {self.wild_pokemon.name} broke free!")
          else:
            x = ((d*f)/255) + s
            if(x<10):
              print(f"Complete miss {self.wild_pokemon.name} broke free!")
            elif(x<30):
              print(f"Pokeball shook once then  {self.wild_pokemon.name} broke free!")
            elif(x<70):
              print(f"Pokeball shook 2 times then  {self.wild_pokemon.name} broke free!")
            else:
              print(f"Pokeball shook 3 times then  {self.wild_pokemon.name} broke free!")

      return False
      """
      # Calculate the catch rate using the formula: (Catch rate * Ball modifier) / (3 * HP max - 2 * HP current)
      catch_rate = self.wild_pokemon.catch_rate * pokeball_used.catch_rate / (3 * self.wild_pokemon.max_hp - 2 * self.wild_pokemon.hp)
      catch_modifier = random.uniform(0, 1)
        
      if catch_modifier < catch_rate:
        print(f"{self.wild_pokemon.name} was caught!")
        self.trainer.add_pokemon_to_team(self.wild_pokemon)
      else:
        print(f"{self.wild_pokemon.name} broke free!")
      """

      

  def forced_switch_pokemon(self):
    done = False
    if len(self.trainer.pokemon_list) > 0:
      while(not done):
        print(f"{self.trainer.name}, choose a new pokemon:")
        for i, pokemon in enumerate(self.trainer.pokemon_list):
          print(f"{i+1}. {pokemon.name} (Level {pokemon.level})")
        choice = int(input()) - 1
        if(self.trainer.pokemon_list[choice].is_fainted()):
          print(f"{self.trainer.pokemon_list[choice].name} is fainted you can't choose him")
        else:
          self.current_trainer_pokemon = self.trainer.pokemon_list[choice]
          print(f"{self.trainer.name} has switched to {self.current_trainer_pokemon.name}!")
          done = True
    else:
      print(f"{self.trainer.name} has no other pokemon to switch to.")

  def switch_pokemon(self):
    done =  False
    if len(self.trainer.pokemon_list) > 0:
      while(not done):
        print(f"{self.trainer.name}, do you want to switch pokemon?")
        choice = input("Enter y for Yes or n for No: ")
        if choice == "y" or choice == "Y":
          print(f"{self.trainer.name}, choose a new pokemon:")
          for i, pokemon in enumerate(self.trainer.pokemon_list):
            print(f"{i+1}. {pokemon.name} (Level {pokemon.level})")
          choice = int(input()) - 1
          if(self.trainer.pokemon_list[choice].is_fainted()):
            print(f"{self.trainer.pokemon_list[choice].name} is fainted you can't choose him")
          else:
            self.current_trainer_pokemon = self.trainer.pokemon_list[choice]
            print(f"{self.trainer.name} has switched to {self.current_trainer_pokemon.name}!")
            done = True
        else:
          print(f"{self.trainer.name} has chosen to keep {self.current_trainer_pokemon.name} in battle.")
          done = True
    else:
      print(f"{self.trainer.name} has no other pokemon to switch to.")

def encounter_wild_pokemon(trainer):
  wild_pokemon = generate_random_wild_pokemon()
  # Start a battle with the wild Pokemon
  start_wild_battle(trainer, wild_pokemon)

def generate_random_wild_pokemon():
  number = random.randint(1, 151)
  pokemon_list = All_Pokemons().pokemon_list
  wild_pokemon = find_pokemon_by_position(number-1, pokemon_list)
  return create_copy_pokemon(wild_pokemon)


def start_wild_battle(player, wild_pokemon):
  # Initialize the wild combat
  wild_combat = WildCombat(player, wild_pokemon)

  # Start the battle
  wild_combat.start_battle()


def game_progression(trainer):

  while trainer.has_non_fainted_pokemon():
    encounter_wild_pokemon(trainer)
  print(f"Game Over {trainer.name} has no more pokemon left")



###############################TESTS###########################################
pokemon_list = All_Pokemons().pokemon_list

pikachu = find_pokemon_by_name("Pikachu", pokemon_list)
pikachu1 = create_copy_pokemon(pikachu)
squirtle = find_pokemon_by_name("Squirtle", pokemon_list)
squirtle1 = create_copy_pokemon(squirtle)

squirtle1.go_to_lvl(38)
squirtle1.check_evolution()
squirtle1.check_evolution()
pikachu1.go_to_lvl(10)

player = Trainer("Ash", [squirtle1, pikachu1])

#combat = encounter_wild_pokemon(player)

game_progression(player)