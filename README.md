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

- après qu'un pokemon levelUp suite à un combat regarder si de nouveaux moves sont disponibles à l'apprentissage et si on dépasse les 4 move créer un modal de sélection de move à garder
- Dans les combat contre des dresseurs je ne gagne de l'xp que après avoir tué le dernier pokemon et le gain d'xp sur le dernier pokémon est en double -> cela est dû au fait que l'xp est calculée dans check_battle_end() et end_batlle()
- Ne donner accès à la 'BattleListView' qu'aux super_user et pour les créations de combats des gymLeader se baser sur les urls depuis la map
- continuer la refactorisation en utilisant le plus possibles les helpers de GameUtils.py ou en en implémentant de nouveaux
- Les achievements après avoir vaincu un champion d'arène ne s'update pas comme il faut
- Il faudrait afficher les sprites d'objets etc là où c'est possible à la place des icônes font awesome
- La fonctionalité de sauvegarde sauvegarde tout le temps dans le slot n°1 et pas forcément celui active
- système de wild combat depuis les maps buggé, on gagne des pokedollar alors qu'il ne faudrait pas et on affronte parfois plusieurs pokemon à la suite

# Setup

pip install -r requirements.txt 

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

To init database in one command :
```
python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase()"
```