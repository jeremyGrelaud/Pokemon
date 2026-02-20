# Credits

For trainer sprites credit to pokemon showdown : https://play.pokemonshowdown.com/sprites/trainers/?filter=credited
To https://bulbapedia.bulbagarden.net for pokeball sprites and refrences to formulas (dmg, exp, catch, ...)
Possibly https://github.com/msikma/pokesprite/tree/master/items for items  & HM sprites
https://www.pokepedia.fr

# Pokemon
For education purpose only


Recreating pokemon game in python

TODO Roadmap :

- Fix battle 'GUI'
- Implement different game mods ?
- Sur les combats de trainer à multiples pokemon on obtient de l'exp que sur le dernier kill et en plus c'est en double le gain d'exp
- ajouter un système de restriction sur le changement de map, certaines quêtes ou objets nécessaires, devoir forcément affronter certains dresseurs ou avoir une chance de trigger une wild battle ... ainsi que placer les combats contre le rival au moment de l'aventure de Kanto comme dans le jeu original
- système de quêtes ?

TODO BugFixes :

- après qu'un pokemon levelUp suite à un combat regarder si de nouveaux moves sont disponibles à l'apprentissage et si on dépasse les 4 move créer un modal de sélection de move à garder
- Dans les combat contre des dresseurs je ne gagne de l'xp que après avoir tué le dernier pokemon et le gain d'xp sur le dernier pokémon est en double -> cela est dû au fait que l'xp est calculée dans check_battle_end() et end_batlle()
- Ne donner accès à la 'BattleListView' qu'aux super_user et pour les créations de combats des gymLeader se baser sur les urls depuis la map
- continuer la refactorisation en utilisant le plus possibles les helpers de GameUtils.py ou en en implémentant de nouveaux
- Après une victoire contre un gym leader il est bien marqué en vaincu mais le trainer n'obtient pas de badge
- Les achievements après avoir vaincu des dresseurs ne s'update pas comme il faut (à vérifier)
- Il faudrait afficher les sprites d'objets etc là où c'est possible à la place des icônes font awesome
- La fonctionalité de sauvegarde sauvegarde tout le temps dans le slot n°1 et pas forcément celui active

# Setup

pip install -r requirements.txt 

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

To init database in one command :
```
python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase()"
```