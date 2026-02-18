# Credits

For trainer sprites credit to pokemon showdown : https://play.pokemonshowdown.com/sprites/trainers/?filter=credited
To https://bulbapedia.bulbagarden.net for pokeball sprites and refrences to formulas (dmg, exp, catch, ...)


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
- Rework html views of battle histories and take into account multiple pokemon opponents in recap for trainer battle
- Give reward money at the end of a trainer fight
- Display correct Victory or Defeat modal at the end of a fight and redirect to pokemon center or combat creation page/combat recap page
- Sur les combats de trainer à multiples pokemon on obtient de l'exp que sur le dernier kill et en plus c'est en double le gain d'exp


# Setup

pip install -r requirements.txt 

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

To init database in one command :
```
python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase()"
```