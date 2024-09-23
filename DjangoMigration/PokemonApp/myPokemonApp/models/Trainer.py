#!/usr/bin/python3
"""! @brief Pokemon.py model
"""

from django.db import models

class Trainer(models.Model):
    username = models.TextField()
    isNPC = models.BooleanField(default=False)