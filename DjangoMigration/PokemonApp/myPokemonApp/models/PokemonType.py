#!/usr/bin/python3
"""! @brief Pokemon type model
"""

from django.db import models

class PokemonType(models.Model):
  TypeName = models.TextField()

  def __str__(self) -> str:
    return str(self.TypeName)

        