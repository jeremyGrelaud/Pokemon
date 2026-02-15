# Credits

For trainer sprites credit to pokemon showdown : https://play.pokemonshowdown.com/sprites/trainers/?filter=credited



# Pokemon
For education purpose only


Recreating pokemon game in python

TODO :

- Better Pokemon Center
- Save Game data options
- Fix battle 'GUI'
- Battle Animations
- Better Capture System with ball throw animation ...
- Stats & Achievements
- Map System ?
- Implement different game mods ?
- Take into account spawn rates for in the wild encounters
- possibily use showdown battle background gen 3> instead of pure css https://play.pokemonshowdown.com/fx/



# Setup

pip install -r requirements.txt 

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

To init database in one command :
```
python manage.py shell -c "from myPokemonApp.tasks.initializeDatabase import scriptToInitializeDatabase; from myPokemonApp.tasks.initializeItemsAndNpcs import run_full_initialization; scriptToInitializeDatabase(); run_full_initialization(); from myPokemonApp.tasks.initShops import initShops; initShops(); from myPokemonApp.tasks.initPokeCenters import scrip
tToInitializePokeCenters; scriptToInitializePokeCenters();from myPokemonApp.tasks.initPokeballItem import scriptToInitNewPokeBalls; scriptToInitNewPokeBalls();"
```