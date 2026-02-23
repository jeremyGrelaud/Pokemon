# Credits

- https://play.pokemonshowdown.com/sprites/trainers/?filter=credited (for trainer sprites)
- https://bulbapedia.bulbagarden.net (for pokeball sprites and refrences to exp, catch, dmg formulas)
- https://github.com/msikma/pokesprite/tree/master/items (for items HM, battle iitems ... sprites)
- https://www.pokepedia.fr (for map sprites)

# Pokemon
For education purpose only


Recreating pokemon game in python

TODO Roadmap :

- Improve battle 'GUI'
- ajouter un système de restriction sur le changement de map, certaines quêtes ou objets nécessaires, devoir forcément affronter certains dresseurs ou avoir une chance de trigger une wild battle ... ainsi que placer les combats contre le rival au moment de l'aventure de Kanto comme dans le jeu original
- système de quêtes avec les key items sur la save comme avec la fonction grant pokedex ?
- After everything, implement different game mods ?

TODO BugFixes :

- continuer la refactorisation en utilisant/implémentant le plus possibles des helpers de GameUtils.py ou via des méthodes dans les models

# Setup

pip install -r requirements.txt 

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

To init database in one command :
```
python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase()"
```