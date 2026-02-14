#!/usr/bin/python3
"""! @brief ___Django tasks___

This is where you import your tasks files in order to use them in your Django app.\n
*Then they will be imported when the models tasks is called.*\n
"""

from .initializeDatabase import scriptToInitializeDatabase
from .initializeItemsAndNpcs import run_full_initialization
from .initShops import initShops
from .initPokeCenters import scriptToInitializePokeCenters