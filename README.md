# Credits

- https://play.pokemonshowdown.com/sprites/trainers/?filter=credited (for trainer sprites)
- https://bulbapedia.bulbagarden.net (for pokeball sprites and refrences to exp, catch, dmg formulas)
- https://github.com/msikma/pokesprite/tree/master/items (for items HM, battle iitems ... sprites)
- https://www.pokepedia.fr (for map sprites)

- Johto reference for future integration ? https://gamefaqs.gamespot.com/gbc/375087-pokemon-crystal-version/faqs/75486/full-trainer-info-list

# Pokemon
For education purpose only


Recreating pokemon game in python

#TODO lorsqu'on commence de zéro un objet GameSave n'estpas automatiquement créé  on pourrait le faire dans le choose starter

TODO Roadmap :

- Improve battle 'GUI'
- Améliorer les zones avec étages en répartissant correctement les dresseurs de la zone dans les étages
- empêcher de pouvoir changer de map sans déclencher aucun combat de dresseur s'il en reste des invaincus et potentiellement rajouter une chance de déclencher une wild battle en changeant de zone comme si on marchait dans les herbes (ou proposer un nouveau système de maps)
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
python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase(); from myPokemonApp.tasks import *; init_all();"
```