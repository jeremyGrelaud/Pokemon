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
- Stats & Achievements
- Map System ?
- Implement different game mods ?
- Take into account spawn rates for in the wild encounters
- possibily use showdown battle background gen 3> instead of pure css https://play.pokemonshowdown.com/fx/
- Rework html views of battle histories and take into account multiple pokemon opponents in recap for trainer battle
- Give reward money at the end of a trainer fight
- Display correct Victory or Defeat modal at the end of a fight and redirect to pokemon center or combat creation page/combat recap page
- Sur les combats de trainer à multiples pokemon on obtient de l'exp que sur le dernier kill et en plus c'est en double le gain d'exp


TODO BugFixes :

- continuer la refactorisation
- lorsqu'un nouveau joueur se connecte pour la première fois il n'a pas de choix de starter et on ne lui donne pas de pokeball de départ
- La redirection sur l'url de /login ne fonction pas correctement
- On n'est pas correctement redirigé et n'a pas d'écran de victoire après avoir gagné un combat dans battle_gamev2
- On ne gagne pas l'argent des combats contre dresseurs
- Les achievements après avoir vaincu des dresseurs ne s'update pas comme il faut
- Après avoir battu un champion d'arène je n'obtiens pas son badge
- Il faudrait améliorer le modal de sélection de pokemon lors des switch forcé en affichant le sprite du pokemon et potentiellement plus d'informations
- Il faudrait afficher les sprites d'objets etc là où c'est possible à la place des icônes font awesome
- Il faut afficher la précision et la puissance des attaques dans l'interface de sélection des moves en combat
- Les interfaces de récap de résultat des combat dans la liste et le dashboard affichent 'Défaite' au lieu de 'Victoire' lorsqu'on termine un comba via capture ou fuite ou même lors d'un combat wild depuis une map
- Dans les maps, exemple sur Route 1 on ne donne pas la possibilité de retourner au Bourg Palette alors qu'il faudrait (mais à chaque fois il faudrait donnerla possibilité de retourner dans l'autre sens d'où on vient sur la vue html)
- Sur le système de maps il faudrait bloquer l'accès aux centre pokemon lorsque la player localisation n'est pas sur une map avec un centre pokemon et si on perds un combat rediriger le player vers le centre pokemon le plus porche en changeant sa localisation


# Setup

pip install -r requirements.txt 

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

To init database in one command :
```
python manage.py shell -c "from myPokemonApp.tasks.initAllDatabase import initAllDatabase; initAllDatabase()"
```