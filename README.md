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
- système de quêtes ?
- système de shiny (sprites présents)
- After everything, implement different game mods ?

TODO BugFixes :

- améliorer le menu de sélection de pokemon sur le switch normal pour se rapprocher du modal de switch forcé
- Les achievements après avoir vaincu un champion d'arène ne s'update pas comme il faut
- Il faudrait afficher les sprites d'objets etc là où c'est possible à la place des icônes font awesome
- continuer la refactorisation en utilisant le plus possibles les helpers de GameUtils.py ou en en implémentant de nouveaux


# Setup

pip install -r requirements.txt 

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

To init database in one command :
```
python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase()"
```