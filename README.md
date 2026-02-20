# Credits

For trainer sprites credit to pokemon showdown : https://play.pokemonshowdown.com/sprites/trainers/?filter=credited
To https://bulbapedia.bulbagarden.net for pokeball sprites and refrences to formulas (dmg, exp, catch, ...)
Possibly https://github.com/msikma/pokesprite/tree/master/items for items  & HM sprites
https://www.pokepedia.fr

# Pokemon
For education purpose only


Recreating pokemon game in python

TODO :

- Better Pokemon Center
- Save Game data options
- Fix battle 'GUI'
- Battle Animations
- Better Capture System with ball throw animation ...
- Implement different game mods ?
- possibily use showdown battle background gen 3> instead of pure css https://play.pokemonshowdown.com/fx/
- Display correct Victory or Defeat modal at the end of a fight and redirect to pokemon center or combat creation page/combat recap page
- Sur les combats de trainer à multiples pokemon on obtient de l'exp que sur le dernier kill et en plus c'est en double le gain d'exp


TODO BugFixes :

- continuer la refactorisation en utilisant le plus possibles les helpers de GameUtils.py ou en en implémentant de nouveaux
- Dans battle_gamev2 on a seulement le modal de victoire en cas de capture qui s'affiche pas quand on bat un pokémon sauvage ou un dresseur
- Après une victoire contre un gym leader il est bien marqué en vaincu mais le trainer n'obtient pas de badge de plus pas de modal d'obtention de badge affiché
- Les achievements après avoir vaincu des dresseurs ne s'update pas comme il faut
- Il faudrait afficher les sprites d'objets etc là où c'est possible à la place des icônes font awesome
- Les interfaces de récap de résultat des combat dans la liste et le dashboard affichent 'Défaite' au lieu de 'Victoire' lorsqu'on termine un comba via capture ou fuite ou même lors d'un combat wild depuis une map
- permettre de gérer le team order
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