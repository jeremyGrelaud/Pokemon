# Credits

- https://play.pokemonshowdown.com/sprites/trainers/?filter=credited (for trainer sprites)
- https://bulbapedia.bulbagarden.net (for pokeball sprites and refrences to exp, catch, dmg formulas)
- https://github.com/msikma/pokesprite/tree/master/items (for items HM, battle iitems ... sprites)
- https://www.pokepedia.fr (for map sprites)
- https://downloads.khinsider.com/game-soundtracks/album/pokemon-firered-leafgreen-enhanced-soundtrack (for soundtracks)  --> ajout des OST des différentes zones du jeux sur zone detail
- https://play.pokemonshowdown.com/fx/ (for battle scenes backgrounds)

- Johto reference for future integration ? https://gamefaqs.gamespot.com/gbc/375087-pokemon-crystal-version/faqs/75486/full-trainer-info-list



# Pokemon
For education purpose only


TODO Roadmap :

- Improve Moves effects during battle (use real pokemon game move animations)
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
python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase(); from myPokemonApp.tasks import *; init_all(); init_zone_music();"
```