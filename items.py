#work in progress it's only a beginning. Haven't figured out all the classes I should use yet ...

class Item:
  def __init__(self, name, description):
    self.name = name
    self.description = description

def get_item_by_name(list, name):
  for item in list:
      if item.name == name:
          return item
  return None


class CombatItem(Item):
  def __init__(self, name, description, stats_increase, stat_name):
    super().__init__(name, description)
    self.stats_increase = stats_increase
    self.stat_name = stat_name
    


class Potion(Item):
  def __init__(self, name, description, healing_amount):
    super().__init__(name, description)
    self.healing_amount = healing_amount


class Pokeball(Item):
  def __init__(self, name, description, catch_rate):
    super().__init__(name, description)
    self.catch_rate = catch_rate


class EquipableItem(Item):
    def __init__(self, name, description, boost_stats, stat_name):
        super().__init__(name, description)
        self.boost_stats = boost_stats
        self.stat_name = stat_name

class ExpShare(EquipableItem):
    def __init__(self, name, description):
        super().__init__(name, description, 0.5, "experience_share")

class ChoiceBand(EquipableItem):
    def __init__(self, name, description):
        super().__init__(name, description, 1.5, "attack")

class LifeOrb(EquipableItem):
    def __init__(self, name, description):
        super().__init__(name, description, 1.3, "damage")


#####################All learnable Moves#########################
class All_Items:
    instance = None
    def __init__(self):
      self.items = [
        Potion("Potion", "A red potion that restores a Pokemon's health.", 20),
        Potion("Super Potion", "A blue potion that restores a Pokemon's health more effectively than a regular potion.", 50),
        Potion("Hyper Potion", "A yellow potion that restores a Pokemon's health even more effectively than a super potion.", 200),
        Potion("Max Potion", "Fully restores the HP of a Pokémon", 9999),
        Potion("Elixir", "Fully restores the PP of all moves of a Pokémon", 0,),
        Potion("Full Restore", "Fully restores the HP and PP of a Pokémon", 9999),
        Pokeball("Pokeball", "A red and white ball used to catch Pokemon.", 255),
        Pokeball("Great Ball", "A better version of the Pokeball with a higher catch rate.", 200),
        Pokeball("Ultra Ball", "An ultra-high-performance Poké Ball that provides the best catch rate", 150),
        Pokeball("Master Ball", "The most powerful Poké Ball with the ultimate level of performance. With it, you will catch any wild Pokémon without fail", 255),
        CombatItem("X Attack", "Raises the Attack stat of a Pokémon by one stage", 0, "attack"),
        CombatItem("X Defense", "Raises the Defense stat of a Pokémon by one stage", 0, "defense"),
        CombatItem("X Special", "Raises the Special stat of a Pokémon by one stage", 0, "special"),
        CombatItem("X Speed", "Raises the Speed stat of a Pokémon by one stage", 0, "speed"),
        ExpShare("Exp. Share", "An item to be held by a Pokémon. The holder earns Exp. Points in battle, but at a slower rate"),
        ChoiceBand("Choice Band", "An item to be held by a Pokémon. The holder's Attack stat is raised"),
        LifeOrb("Life Orb", "An item to be held by a Pokémon. The holder's moves deal 30% more damage")
      ] 
          
    def __new__(cls):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.__init__()
        return cls.instance
###########################END All learnable Moves################

def initialize_all_items():
    items = [
        Potion("Potion", "A red potion that restores a Pokemon's health.", 20),
        Potion("Super Potion", "A blue potion that restores a Pokemon's health more effectively than a regular potion.", 50),
        Potion("Hyper Potion", "A yellow potion that restores a Pokemon's health even more effectively than a super potion.", 200),
        Potion("Max Potion", "Fully restores the HP of a Pokémon", 9999),
        Potion("Elixir", "Fully restores the PP of all moves of a Pokémon", 0, "restore_pp"),
        Potion("Full Restore", "Fully restores the HP and PP of a Pokémon", 9999, "full_restore"),
        Pokeball("Pokeball", "A red and white ball used to catch Pokemon.", 1),
        Pokeball("Great Ball", "A better version of the Pokeball with a higher catch rate.", 1.5),
        Pokeball("Ultra Ball", "An ultra-high-performance Poké Ball that provides the best catch rate", 2),
        Pokeball("Master Ball", "The most powerful Poké Ball with the ultimate level of performance. With it, you will catch any wild Pokémon without fail", 255),
        CombatItem("X Attack", "Raises the Attack stat of a Pokémon by one stage", 0, "attack"),
        CombatItem("X Defense", "Raises the Defense stat of a Pokémon by one stage", 0, "defense"),
        CombatItem("X Special", "Raises the Special stat of a Pokémon by one stage", 0, "special"),
        CombatItem("X Speed", "Raises the Speed stat of a Pokémon by one stage", 0, "speed"),
        ExpShare("Exp. Share", "An item to be held by a Pokémon. The holder earns Exp. Points in battle, but at a slower rate"),
        ChoiceBand("Choice Band", "An item to be held by a Pokémon. The holder's Attack stat is raised"),
        LifeOrb("Life Orb", "An item to be held by a Pokémon. The holder's moves deal 30% more damage")
    ]
    return items
"""
potions = [
    Potion("Potion", "A red potion that restores a Pokemon's health.", 20),
    Potion("Super Potion", "A blue potion that restores a Pokemon's health more effectively than a regular potion.", 50),
    Potion("Hyper Potion", "A yellow potion that restores a Pokemon's health even more effectively than a super potion.", 200),
    Potion("Max Potion", "Fully restores the HP of a Pokémon", 9999),
    Potion("Elixir", "Fully restores the PP of all moves of a Pokémon", 0, "restore_pp"),
    Potion("Full Restore", "Fully restores the HP and PP of a Pokémon", 9999, "full_restore")

]

pokeballs = [
  Pokeball("Pokeball", "A red and white ball used to catch Pokemon.", 1),
  Pokeball("Great Ball", "A better version of the Pokeball with a higher catch rate.", 1.5),
  Pokeball("Ultra Ball", "An ultra-high-performance Poké Ball that provides the best catch rate", 2),
  Pokeball("Master Ball", "The most powerful Poké Ball with the ultimate level of performance. With it, you will catch any wild Pokémon without fail", 255)
]

combat_items = [
    CombatItem("X Attack", "Raises the Attack stat of a Pokémon by one stage", 0, "attack"),
    CombatItem("X Defense", "Raises the Defense stat of a Pokémon by one stage", 0, "defense"),
    CombatItem("X Special", "Raises the Special stat of a Pokémon by one stage", 0, "special"),
    CombatItem("X Speed", "Raises the Speed stat of a Pokémon by one stage", 0, "speed")
]
"""




"""
    Full Heal: Cures all status conditions of a Pokémon.
    Revive: Revives a fainted Pokémon with 50% of its maximum HP.
    Antidote: Cures a Pokémon of poison.
    Paralysis Heal: Cures a Pokémon of paralysis.
    Awakening: Cures a Pokémon of sleep.
    Burn Heal: Cures a Pokémon of burn.
    Ice Heal: Cures a Pokémon of freeze.
    Repel: Prevents wild Pokémon from appearing for a certain number of steps.
    Escape Rope: Allows the player to escape a cave or a dungeon.
    Old Rod: Can be used to catch a level 5 or lower Water-type Pokémon.
    Good Rod: Can be used to catch a level 10 or lower Water-type Pokémon.
    Super Rod: Can be used to catch any Water-type Pokémon.
"""