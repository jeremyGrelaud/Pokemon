#!/usr/bin/python3
"""! @brief Pokemon moves model
"""

from django.db import models

class PokemonMove(models.Model):
  #it could be sleep, paralysis, ...
  #https://pokemondb.net/move/generation/1
  #A move can raise user's stats
  #or lower oponent's stats or precision
  #it can cause status, flinching, high critical hit or inflict a fixed amount of dm
  #self destruction too

  name = models.TextField()
  pp = models.IntegerField()
  attackPower =  models.IntegerField()
  accuracy =  models.IntegerField()
  type = models.TextField() #TYPE OF THE MOVE
  effect = models.TextField() #TODO


  def __str__(self) -> str:
    strMove = f"Name: {self.name}\n"+\
              f"Type: {self.type}\n"+\
              f"PP: {self.pp}\n"+\
              f"Attack Power: {self.attackPower}\n"+\
              f"Accuracy: {self.accuracy}\n"
    return str(strMove)

        




  def use(self, user, opponent):
      """Use the move and apply its effects to the user and opponent."""
      print(f'{user.name} used {self.name}!')
      ##########################CALCULATE AND APPLY DAMAGE VIA ANOTHER FUNCTION££££££££££££££££££££££££££££££££££
      # Apply the special effect
      if self.effect == "paralysis":
          opponent.status = "paralyzed"
      elif self.effect == "raise_atk":
          user.attack += 1