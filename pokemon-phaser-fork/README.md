# Pokémon Kanto — Fork Phaser 3

Fork du projet Django original. Ce fork remplace la navigation HTML par une carte
interactive en **Phaser 3 + TypeScript**, tout en réutilisant intégralement le backend Django.

---

## Architecture

```
pokemon-phaser-fork/
├── backend/                  ← Ton Django existant (peu modifié)
│   └── myPokemonApp/
│       └── views/api/
│           ├── phaser_api.py     ← NOUVEAU : 4 endpoints JSON purs
│           └── phaser_urls.py    ← NOUVEAU : routage de ces endpoints
│
└── frontend/                 ← NOUVEAU : Vite + Phaser 3 + TypeScript
    ├── index.html
    ├── vite.config.ts        ← Proxy vers Django :8000
    ├── tsconfig.json
    └── src/
        ├── main.ts           ← Point d'entrée Phaser
        ├── config/
        │   └── gameConfig.ts ← Config Phaser + liste des scènes
        ├── scenes/
        │   ├── BootScene.ts      ← Vérifie la session Django
        │   ├── PreloadScene.ts   ← Charge assets + crée les animations
        │   ├── GameScene.ts      ← Carte + déplacement + transitions de zone
        │   ├── BattleScene.ts    ← Combat au tour par tour
        │   ├── UIScene.ts        ← HUD (tourne en parallèle de GameScene)
        │   └── DialogScene.ts    ← Boîtes de dialogue
        ├── api/
        │   └── djangoClient.ts   ← Client HTTP (CSRF, session, mapApi, battleApi)
        ├── types/
        │   └── index.ts          ← Types TS miroirs des serializers Django
        └── utils/
            └── EventBus.ts       ← Bus d'événements inter-scènes
```

---

## Démarrage rapide

### 1. Backend Django

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver   # → http://localhost:8000
```

Ajouter dans `urls.py` :
```python
from myPokemonApp.views.api.phaser_api import phaser_battle_state

urlpatterns += [
    path('api/phaser/', include('myPokemonApp.views.api.phaser_urls')),
    path('api/battle/state/<int:battle_id>/', phaser_battle_state, name='phaser_battle_state'),
]
```

### 2. Frontend Phaser

```bash
cd frontend
npm install
npm run dev   # → http://localhost:5173
```

Le proxy Vite redirige automatiquement `/api/*`, `/map/*`, `/battle/*` vers Django.

---

## Feuille de route

### Étape 1 — Tilemap Kanto ✦ PRIORITAIRE
Créer la tilemap avec **[Tiled](https://www.mapeditor.org/)** :
- Télécharger les tilesets FireRed (libre pour fan games)
- Créer les couches : `Ground`, `Objects`, `Collision`, `Portals`, `Grass`
- Chaque portail Tiled doit avoir une propriété `zone_id` = l'ID Django de la zone de destination
- Exporter en JSON → `frontend/src/assets/tilemaps/kanto.json`

### Étape 2 — Sprites joueur
Format : spritesheet 48×48px, 4 rangées (bas/gauche/droite/haut), 3 frames chacune.
Placer dans `frontend/src/assets/sprites/player.png`.

### Étape 3 — Sprites Pokémon dans BattleScene
Remplacer les rectangles placeholder par les vraies images.
Charger dynamiquement : `this.load.image(`pokemon-${id}`, `assets/sprites/pokemon/front/${id}.png`)`

### Étape 4 — Audio
Les fichiers `.wav` de ton projet Django sont réutilisables directement.
Les copier dans `frontend/src/assets/audio/` ou les servir via Django static.

### Étape 5 — Menu / Inventaire en Phaser
Créer une `MenuScene` qui s'ouvre sur ESC/ENTRÉE.

---

## Ce qui est réutilisé du projet original

| Composant Django | Statut |
|---|---|
| Tous les models (`Zone`, `Pokemon`, `Battle`…) | ✅ Inchangé |
| `battle_service.py`, `capture_service.py` | ✅ Inchangé |
| `serializers.py` (`build_battle_response`) | ✅ Inchangé |
| Endpoints battle (`/battle/<id>/action/`) | ✅ Inchangé |
| Auth Django + session cookie | ✅ Inchangé |
| Assets audio (`.wav`) | ✅ Réutilisés |
| Templates HTML de navigation | ⚠️ Remplacés par Phaser |
| `MapViews.py` (render HTML) | ⚠️ Nouveaux endpoints JSON en parallèle |
