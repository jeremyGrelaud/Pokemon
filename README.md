# Propriété intellectuelle et sources

Les assets graphiques utilisés dans ce projet sont la propriété exclusive de **Nintendo Co., Ltd.** et sont utilisés ici à des fins de démonstration ou d'archivage personnel uniquement. Toute utilisation commerciale ou redistribution de ces assets est strictement interdite sans l'autorisation expresse de Nintendo.

Pour les autres ressources utilisées (sprites, musiques, etc.) non produites par Nintendo, référez vous au paragraphe Credits ci-dessous.



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

Roadmap :
- After everything, implement different game mods ?
- implement missing Abilites effects/logic
- implement moves Abilites effects/logic


# Setup

pip install -r requirements.txt 

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

To init database in one command :
```
python manage.py init_db
```

To launch unitTests : 
```
python manage.py test myPokemonApp.tests
```


## Stack technique

- **Backend** : Django (Python)
- **Frontend** : HTML/CSS/JS vanilla + Bootstrap 5 (free sb admin theme)
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **Auth** : Django Auth natif

---

## Fonctionnalités principales

- **Combat au tour par tour** — formules Gen 3 (FireRed/LeafGreen), effets de capacités, états de statut
- **Système de capture** — formule Gen 3, shake count, Master Ball
- **Pokédex** — consultation des espèces, types, capacités apprenables
- **Mon équipe** — gestion de l'équipe (6 max), PC, IVs/EVs, natures, talents, capacités
- **Carte Kanto** — zones avec accès conditionnels (badges, CS, objets clés, quêtes)
- **Quêtes** — journal de quêtes, quêtes principales / secondaires / rival
- **Succès** — 5 catégories (combat, capture, collection, exploration, progression)
- **Shops & Pokémon Centers** — achat d'objets, soins d'équipe
- **Objets tenus** — équipement sur les Pokémon
- **Sauvegarde** — système de slots avec snapshot 
- **Champions d'Arène** — badges, progression de ligue
- **Rencontres sauvages** — spawn par zone, herbe / eau / pêche / grotte
- **Rival** — rencontres scénaristiques liées aux quêtes
- **BGM** — musiques par zone
