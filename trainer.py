from pokemon import All_Pokemons, find_pokemon_by_name


class Trainer:
  def __init__(self, name, pokemon_list, max_pokemon=6, bag=[]):
    self.name = name
    self.pokemon_list = pokemon_list
    self.max_pokemon = max_pokemon
    self.bag = bag
  
  def catch_pokemon(self, pokemon):
    if len(self.pokemon_list) < self.max_pokemon:
      self.pokemon_list.append(pokemon)
    else:
      print(f"{self.name} can't catch any more pokemon, the team is full!")
  
  def release_pokemon(self, pokemon):
    self.pokemon_list.remove(pokemon)

  def print_team(self):
    print(f"{self.name}'s pokemon:")
    for pokemon in self.pokemon_list:
      print(f"  - {pokemon.name} (level {pokemon.level})")    

  def remove_pokemon(self, pokemon_to_remove):
    self.pokemon_list.remove(pokemon_to_remove)

  def has_non_fainted_pokemon(self):
    for pokemon in self.pokemon_list:
      if not pokemon.is_fainted():
        return True
    return False
  
  def print_team_status(self):
    print(f"{self.name}'s team:")
    for pokemon in self.pokemon_list:
      print(f"  - {pokemon.name}: {pokemon.hp}/{pokemon.max_hp} hp")
  
  def add_item_to_bag(self, item):
      self.bag.append(item)

  def display_items(self):
      for item in self.bag:
          print(item.name)

#######################TESTS############################################
"""
# Initialize a trainer with some pokemon
pokemon_list = All_Pokemons().pokemon_list

pikachu = find_pokemon_by_name("Pikachu", pokemon_list)
squirtle = find_pokemon_by_name("Squirtle", pokemon_list)

ash = Trainer("Ash", [pikachu, squirtle])

# Print the names and levels of the trainer's pokemon
ash.print_team()

ash.catch_pokemon(pikachu)
ash.catch_pokemon(pikachu)
ash.catch_pokemon(pikachu)
ash.catch_pokemon(pikachu)
ash.catch_pokemon(pikachu)

ash.print_team()
"""