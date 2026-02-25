#!/usr/bin/python3
"""! @brief Django models

This is where you import your models files in order to use them in your Django app.\n
*Then they will be imported when the models module is called.*\n
"""

#from ._Example import _Example
from .Pokemon import Pokemon
from .PokemonMove import PokemonMove
from .PokemonType import PokemonType
from .Trainer import Trainer, GymLeader, TrainerInventory
from .PlayablePokemon import PlayablePokemon, PokemonMoveInstance
from .PokemonLearnableMove import PokemonLearnableMove
from .PokemonEvolution import PokemonEvolution
from .Item import Item
from .Battle import Battle
from .ShopModel import Shop, ShopInventory, Transaction
from .PokemonCenter import PokemonCenter, CenterVisit, NurseDialogue
from .CaptureSystem import *
from .GameSave import *
from .Zone import *
from .Achievements import *
from .Quest import *