from django import template
from django.utils import timezone
from datetime import timedelta
import re, bleach
from django.template.defaultfilters import date as lazy_date
from django.template.loader import render_to_string

from django_tables2.templatetags.django_tables2 import Node
from django.template.loader import get_template, select_template
import django_tables2 as tables

register = template.Library()


@register.filter(name="removeFromURL")
def removeFromURL(fullUrlPath, argToRemove):
    """Reads full URL Path and remove 'argToRemove' from path
    ex: toto.com/?vendor=tata -> toto.com/?"""
    # Chunk : /cve/?vendor=microsoft&product=windows&searchQuery=
    
    # 1. Clean url 
    fullUrlPath = bleach.clean(fullUrlPath, tags=[], attributes={})

    # 2. Retrieve args
    urlPath, *urlArgs = fullUrlPath.split("?")

    # 3. If multiple '?', it is unusual access -> return current page
    if len(urlArgs)!=1:
        return fullUrlPath
    
    # 4. Iterate througt args
    # Chunk vendor=microsoft
    newUrlArgs = []
    for arg in urlArgs[0].split("&amp;"):
        key, *value = arg.split("=")

        # 5. If multiple '=', it is unusual access -> return current page
        if len(value) != 1: 
            return fullUrlPath
        
        # 6. If not to remove, then add to arg paths
        if key!=argToRemove:
            if key=="page":
                newUrlArgs.append("page=1") 
            else:
                newUrlArgs.append(arg) 
    
    return f"{urlPath}?{'&'.join(newUrlArgs)}"


@register.tag
def optimized_render_table(parser, token):
    bits = token.split_contents()
    bits.pop(0)

    table = parser.compile_filter(bits.pop(0))
    template = parser.compile_filter(bits.pop(0)) if bits else None
    pageObjects = parser.compile_filter(bits.pop(0)) if bits else None

    return OptimizedRenderTableNode(table, template, pageObjects)

class OptimizedRenderTableNode(Node):
    """
    parameters:
        table (~.Table): the table to render
        template (str or list): Name[s] of template to render
    """

    def __init__(self, table, template_name=None, pageObjects=None):
        super().__init__()
        self.table = table
        self.template_name = template_name
        self.pageObjects = pageObjects

    def render(self, context):
        table = self.table.resolve(context)
        pageObjects = self.pageObjects.resolve(context)

        request = context.get("request")

        if isinstance(table, tables.Table):
            pass
        elif hasattr(table, "model"):
            queryset = table

            table = tables.table_factory(model=queryset.model)(queryset, request=request)
        else:
            raise ValueError(f"Expected table or queryset, not {type(table).__name__}")

        if self.template_name:
            template_name = self.template_name.resolve(context)
        else:
            template_name = table.template_name

        if isinstance(template_name, str):
            template = get_template(template_name)
        else:
            # assume some iterable was given
            template = select_template(template_name)

        try:
            table.context = context
            table.before_render(request)

            return template.render(context={"table": table, "pageObjects" : pageObjects}, request=request)
        finally:
            del table.context


@register.filter(name='same_as')
def same_as(value, arg):
    """Compare deux chaînes de caractères et retourne 'True' si elles sont identiques, sinon 'False'."""
    return str(value) == str(arg)

@register.filter
def mul(value, arg):
    """Multiplie value par arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def lower(value):
    """Convertit une chaîne de caractères en minuscules."""
    try:
        return value.lower()
    except AttributeError:
        return value
    
@register.filter(name="gymleaderescape")
def gymleaderescape(value):
    """Supprime les espaces et les points d'une chaîne de caractères."""
    if not isinstance(value, str):
        return value
    return value.replace(" ", "").replace(".", "")


@register.filter(name='floatformat')
def floatformat(value, decimal_places=0):
    """Formate la valeur en float avec le nombre de décimales spécifié."""
    try:
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return value
    
@register.filter(name='is_available_for_trainer')
def is_available_for_trainer(item, trainer):
    return item.is_available_for_trainer(trainer)

@register.filter(name='lowerPokemonFileNames')
def lowerPokemonFileNames(value):
    # Remplacer les symboles ♂ et ♀ par "m" et "f"
    value = value.replace('♂', 'm').replace('♀', 'f')
    value = value.lower()
    # Supprimer tout ce qui n'est pas alphanumérique
    value = re.sub(r'[^a-z0-9]', '', value)
    return value

# ============================================================
#  SPRITE FILTERS — Items
# ============================================================

# ---------------------------------------------------------------------------
# item_sprite_path : retourne le chemin relatif dans img/items_sprites/
# Usage : {{ inventory_item.item|item_sprite_path }}
# ---------------------------------------------------------------------------

# Mapping nom français → (sous-dossier, fichier)
_ITEM_SPRITE_MAP = {
    # ── Pokéballs ──────────────────────────────────────────────────────────
    'poké ball':      ('ball', 'poke.png'),
    'super ball':     ('ball', 'great.png'),
    'great ball':     ('ball', 'great.png'),
    'ultra ball':     ('ball', 'ultra.png'),
    'master ball':    ('ball', 'master.png'),
    'safari ball':    ('ball', 'safari.png'),
    'filet ball':     ('ball', 'net.png'),
    'scuba ball':     ('ball', 'dive.png'),
    'faiblo ball':    ('ball', 'heal.png'),
    'chrono ball':    ('ball', 'timer.png'),
    'sombre ball':    ('ball', 'dusk.png'),
    'rapide ball':    ('ball', 'quick.png'),
    'bis ball':       ('ball', 'repeat.png'),
    'luxe ball':      ('ball', 'luxury.png'),
    'honor ball':     ('ball', 'premier.png'),
    'amour ball':     ('ball', 'love.png'),
    'appât ball':     ('ball', 'lure.png'),
    'appat ball':     ('ball', 'lure.png'),
    'niveau ball':    ('ball', 'level.png'),
    'copain ball':    ('ball', 'friend.png'),
    'masse ball':     ('ball', 'heavy.png'),
    'lune ball':      ('ball', 'moon.png'),
    'nid ball':       ('ball', 'nest.png'),
    'sport ball':     ('ball', 'sport.png'),
    'park ball':      ('ball', 'park.png'),
    'dream ball':     ('ball', 'dream.png'),
    'beast ball':     ('ball', 'beast.png'),
    'premier ball':   ('ball', 'premier.png'),
    'heal ball':      ('ball', 'heal.png'),
    'net ball':       ('ball', 'net.png'),
    'dive ball':      ('ball', 'dive.png'),
    'nest ball':      ('ball', 'nest.png'),
    'repeat ball':    ('ball', 'repeat.png'),
    'timer ball':     ('ball', 'timer.png'),
    'dusk ball':      ('ball', 'dusk.png'),
    'quick ball':     ('ball', 'quick.png'),
    'cherry ball':    ('ball', 'cherish.png'),
    'fast ball':      ('ball', 'fast.png'),
    'level ball':     ('ball', 'level.png'),
    'lure ball':      ('ball', 'lure.png'),
    'heavy ball':     ('ball', 'heavy.png'),
    'love ball':      ('ball', 'love.png'),
    'moon ball':      ('ball', 'moon.png'),
    'friend ball':    ('ball', 'friend.png'),
    # ── Médecines / Soins ──────────────────────────────────────────────────
    'potion':              ('medicine', 'potion.png'),
    'super potion':        ('medicine', 'super-potion.png'),
    'hyper potion':        ('medicine', 'hyper-potion.png'),
    'max potion':          ('medicine', 'max-potion.png'),
    'plein air':           ('medicine', 'full-restore.png'),
    'full restore':        ('medicine', 'full-restore.png'),
    'soin total':          ('medicine', 'full-heal.png'),
    'full heal':          ('medicine', 'full-heal.png'),
    'antidote':            ('medicine', 'antidote.png'),
    'burn heal':           ('medicine', 'burn-heal.png'),
    'awakening':           ('medicine', 'awakening.png'),
    'paralyze heal':       ('medicine', 'paralyze-heal.png'),
    'ice heal':            ('medicine', 'ice-heal.png'),
    'brûle-froid':         ('medicine', 'burn-heal.png'),
    'brule-froid':         ('medicine', 'burn-heal.png'),
    'réveil':              ('medicine', 'awakening.png'),
    'reveil':              ('medicine', 'awakening.png'),
    'para-guérison':       ('medicine', 'paralyze-heal.png'),
    'para-guerison':       ('medicine', 'paralyze-heal.png'),
    'guérison glace':      ('medicine', 'ice-heal.png'),
    'guerison glace':      ('medicine', 'ice-heal.png'),
    'rappel':              ('medicine', 'revive.png'),
    'revive':              ('medicine', 'revive.png'),
    'max revive':          ('medicine', 'max-revive.png'),
    'max rappel':          ('medicine', 'max-revive.png'),
    'pp plus':             ('medicine', 'pp-up.png'),
    'pp up':               ('medicine', 'pp-up.png'),
    'pp max':              ('medicine', 'pp-max.png'),
    'protéine':            ('medicine', 'protein.png'),
    'proteine':            ('medicine', 'protein.png'),
    'fer':                 ('medicine', 'iron.png'),
    'calcium':             ('medicine', 'calcium.png'),
    'zinc':                ('medicine', 'zinc.png'),
    'glucides':            ('medicine', 'carbos.png'),
    'pv plus':             ('medicine', 'hp-up.png'),
    'bonbon rare':         ('medicine', 'rare-candy.png'),
    'élixir':              ('medicine', 'elixir.png'),
    'elixir':              ('medicine', 'elixir.png'),
    'max élixir':          ('medicine', 'max-elixir.png'),
    'max elixir':          ('medicine', 'max-elixir.png'),
    'éther':               ('medicine', 'ether.png'),
    'ether':               ('medicine', 'ether.png'),
    'max éther':           ('medicine', 'max-ether.png'),
    'max ether':           ('medicine', 'max-ether.png'),
    'eau fraîche':         ('medicine', 'fresh-water.png'),
    'eau fraiche':         ('medicine', 'fresh-water.png'),
    'limonade':            ('medicine', 'lemonade.png'),
    'soda':                ('medicine', 'soda-pop.png'),
    'lait meumeu':         ('medicine', 'moomoo-milk.png'),
    'capacité capsule':    ('medicine', 'ability-capsule.png'),
    'capsule capacité':    ('medicine', 'ability-capsule.png'),
    # ── Pierres d'évolution ────────────────────────────────────────────────
    'pierre feu':          ('evo-item', 'fire-stone.png'),
    'pierre eau':          ('evo-item', 'water-stone.png'),
    'pierre tonnerre':     ('evo-item', 'thunder-stone.png'),
    'pierre plante':       ('evo-item', 'leaf-stone.png'),
    'pierre lune':         ('evo-item', 'moon-stone.png'),
    'pierre soleil':       ('evo-item', 'sun-stone.png'),
    'pierre aube':         ('evo-item', 'dawn-stone.png'),
    'pierre nuit':         ('evo-item', 'dusk-stone.png'),
    'pierre brillante':    ('evo-item', 'shiny-stone.png'),
    'pierre glace':        ('evo-item', 'ice-stone.png'),
    'fire stone':          ('evo-item', 'fire-stone.png'),
    'water stone':         ('evo-item', 'water-stone.png'),
    'thunder stone':       ('evo-item', 'thunder-stone.png'),
    'leaf stone':          ('evo-item', 'leaf-stone.png'),
    'moon stone':          ('evo-item', 'moon-stone.png'),
    'sun stone':           ('evo-item', 'sun-stone.png'),
    'dawn stone':          ('evo-item', 'dawn-stone.png'),
    'dusk stone':          ('evo-item', 'dusk-stone.png'),
    'shiny stone':         ('evo-item', 'shiny-stone.png'),
    'ice stone':           ('evo-item', 'ice-stone.png'),
    'fire_stone':          ('evo-item', 'fire-stone.png'),
    'water_stone':         ('evo-item', 'water-stone.png'),
    'thunder_stone':       ('evo-item', 'thunder-stone.png'),
    'leaf_stone':          ('evo-item', 'leaf-stone.png'),
    'moon_stone':          ('evo-item', 'moon-stone.png'),
    'sun_stone':           ('evo-item', 'sun-stone.png'),
    'dawn_stone':          ('evo-item', 'dawn-stone.png'),
    'dusk_stone':          ('evo-item', 'dusk-stone.png'),
    'shiny_stone':         ('evo-item', 'shiny-stone.png'),
    'ice_stone':           ('evo-item', 'ice-stone.png'),
    'rocco roi':           ('evo-item', 'kings-rock.png'),
    'écaille dragonie':    ('evo-item', 'dragon-scale.png'),
    'ecaille dragonie':    ('evo-item', 'dragon-scale.png'),
    'manteau métal':       ('evo-item', 'metal-coat.png'),
    'manteau metal':       ('evo-item', 'metal-coat.png'),
    'écaille prismatique': ('evo-item', 'prism-scale.png'),
    'ecaille prismatique': ('evo-item', 'prism-scale.png'),
    'protecteur':          ('evo-item', 'protector.png'),
    'linceul':             ('evo-item', 'reaper-cloth.png'),
    'sachet':              ('evo-item', 'sachet.png'),
    'griffe rasoir':       ('evo-item', 'razor-claw.png'),
    'crochet rasoir':      ('evo-item', 'razor-fang.png'),
    # ── Objets tenus ──────────────────────────────────────────────────────
    'restes':              ('hold-item', 'leftovers.png'),
    'leftovers':              ('hold-item', 'leftovers.png'),
    'orbe vie':            ('hold-item', 'life-orb.png'),
    'bandeau choix':       ('hold-item', 'choice-band.png'),
    'lunettes choix':      ('hold-item', 'choice-specs.png'),
    'foulard choix':       ('hold-item', 'choice-scarf.png'),
    'œuf chance':          ('hold-item', 'lucky-egg.png'),
    'oeuf chance':         ('hold-item', 'lucky-egg.png'),
    'lucky egg':           ('hold-item', 'lucky-egg.png'),
    'bandeau concentration': ('hold-item', 'focus-band.png'),
    'ceinture concentration': ('hold-item', 'focus-sash.png'),
    'charbon':             ('hold-item', 'charcoal.png'),
    'eau mystique':        ('hold-item', 'mystic-water.png'),
    'aimant':              ('hold-item', 'magnet.png'),
    'pierre dure':         ('hold-item', 'hard-stone.png'),
    'écharpe soie':        ('hold-item', 'silk-scarf.png'),
    'echarpe soie':        ('hold-item', 'silk-scarf.png'),
    'croc dragon':         ('hold-item', 'dragon-fang.png'),
    'lentille zoom':       ('hold-item', 'zoom-lens.png'),
    'lentille large':      ('hold-item', 'wide-lens.png'),
    'veste assaut':        ('hold-item', 'assault-vest.png'),
    'orbe flamme':         ('hold-item', 'flame-orb.png'),
    'orbe toxique':        ('hold-item', 'toxic-orb.png'),
    'grosse racine':       ('hold-item', 'big-root.png'),
    'ballon air':          ('hold-item', 'air-balloon.png'),
    'casque rocheux':      ('hold-item', 'rocky-helmet.png'),
    'fumigène':            ('hold-item', 'smoke-ball.png'),
    'fumigene':            ('hold-item', 'smoke-ball.png'),
    'griffe rapide':       ('hold-item', 'quick-claw.png'),
    'bandeau muscle':      ('hold-item', 'muscle-band.png'),
    'ceinture expert':     ('hold-item', 'expert-belt.png'),
    'roc lissé':           ('hold-item', 'smooth-rock.png'),
    'roc lisse':           ('hold-item', 'smooth-rock.png'),
    'roc givré':           ('hold-item', 'icy-rock.png'),
    'roc givre':           ('hold-item', 'icy-rock.png'),
    'roc chaleur':         ('hold-item', 'heat-rock.png'),
    'roc humide':          ('hold-item', 'damp-rock.png'),
    'lunettes sages':      ('hold-item', 'wise-glasses.png'),
    'lentille portée':     ('hold-item', 'scope-lens.png'),
    'clochette coque':     ('hold-item', 'shell-bell.png'),
    'orbe adamantin':      ('hold-item', 'adamant-orb.png'),
    'orbe lustré':         ('hold-item', 'lustrous-orb.png'),
    'orbe griseous':       ('hold-item', 'griseous-orb.png'),
    # ── Objets de combat ──────────────────────────────────────────────────
    'x-attaque':           ('battle-item', 'x-attack.png'),
    'x attaque':           ('battle-item', 'x-attack.png'),
    'x-attack':            ('battle-item', 'x-attack.png'),
    'x attack':            ('battle-item', 'x-attack.png'),
    'x-défense':           ('battle-item', 'x-defense.png'),
    'x defense':           ('battle-item', 'x-defense.png'),
    'x-vitesse':           ('battle-item', 'x-speed.png'),
    'x vitesse':           ('battle-item', 'x-speed.png'),
    'x-speed':             ('battle-item', 'x-speed.png'),
    'x speed':             ('battle-item', 'x-speed.png'),
    'x-précision':         ('battle-item', 'x-accuracy.png'),
    'x precision':         ('battle-item', 'x-accuracy.png'),
    'x-special':           ('battle-item', 'x-sp-atk.png'),
    'x special':           ('battle-item', 'x-sp-atk.png'),
    'guard spec':          ('battle-item', 'guard-spec.png'),
    'x-sp.atq':            ('battle-item', 'x-sp-atk.png'),
    'x-sp.déf':            ('battle-item', 'x-sp-def.png'),
    'miroir obscur':       ('battle-item', 'guard-spec.png'),
    'danse leurre':        ('battle-item', 'dire-hit.png'),
    'dire hit':            ('battle-item', 'dire-hit.png'),
    # ── Objets divers ─────────────────────────────────────────────────────
    'corde caverne':       ('other-item', 'escape-rope.png'),
    'repel':               ('other-item', 'repel.png'),
    'super repel':         ('other-item', 'super-repel.png'),
    'max repel':           ('other-item', 'max-repel.png'),
    'anti-repousse':       ('other-item', 'repel.png'),
    'repousse':            ('other-item', 'repel.png'),
    'super repousse':      ('other-item', 'super-repel.png'),
    'maxi repousse':       ('other-item', 'max-repel.png'),
    'super anti-repousse': ('other-item', 'super-repel.png'),
    'maxi anti-repousse':  ('other-item', 'max-repel.png'),
    'escape rope':         ('other-item', 'escape-rope.png'),
    'poupon poké':         ('other-item', 'poke-doll.png'),
    'grelot bonheur':      ('hold-item', 'soothe-bell.png'),
    'clochette bonheur':   ('hold-item', 'soothe-bell.png'),
    # ── Objets clefs ─────────────────────────────────────────────────────
    'old rod':   ('key-item', 'old-rod.png'),
    'bicycle':   ('key-item', 'bicycle.png'),
    'good rod':   ('key-item', 'good-rod.png'),
    'super rod':   ('key-item', 'super-rod.png'),
    'silph scope':   ('key-item', 'silph-scope-gen3.png'),
    'poke flute':   ('key-item', 'poke-flute.png'),
    'card key':   ('key-item', 'card-key-gen3.png'),
    'town map':   ('key-item', 'town-map-gen3.png'),
    'ss ticket':   ('key-item', 'ss-ticket.png'),
    's.s. ticket':   ('key-item', 'ss-ticket.png'),
    'coin case':   ('key-item', 'coin-case.png'),
    'itemfinder':   ('key-item', 'dowsing-machine-gen3.png'),

    'dome fossil':   ('fossil', 'dome.png'),
    'old amber':   ('fossil', 'old-amber.png'),
    'helix fossil':   ('fossil', 'helix.png'),

    

    

}

# Fallback par item_type
_ITEM_TYPE_FALLBACK = {
    'pokeball':  ('ball', 'poke.png'),
    'potion':    ('medicine', 'potion.png'),
    'evolution': ('evo-item', 'fire-stone.png'),
    'status':    ('medicine', 'full-heal.png'),
    'held':      ('hold-item', 'leftovers.png'),
    'battle':    ('battle-item', 'x-attack.png'),
    'other':     ('other-item', 'escape-rope.png'),
}

@register.filter(name='item_sprite_path')
def item_sprite_path(item):
    """
    Retourne le chemin relatif de l'icône d'un item dans img/items_sprites/.
    Usage dans le template :
        <img src="{% static 'img/items_sprites/' %}{{ item|item_sprite_path }}">
    """
    if item is None:
        return None

    name_lower = item.name.lower().strip()

    # 1. Correspondance exacte
    if name_lower in _ITEM_SPRITE_MAP:
        folder, filename = _ITEM_SPRITE_MAP[name_lower]
        return f"{folder}/{filename}"

    # 2. Correspondance partielle (le nom de l'item contient une clé connue)
    for key, (folder, filename) in _ITEM_SPRITE_MAP.items():
        if key in name_lower or name_lower in key:
            return f"{folder}/{filename}"

    # 3. Fallback sur item_type
    item_type = getattr(item, 'item_type', '')
    if item_type in _ITEM_TYPE_FALLBACK:
        folder, filename = _ITEM_TYPE_FALLBACK[item_type]
        return f"{folder}/{filename}"

    return None


# ---------------------------------------------------------------------------
# zone_image_path : retourne le chemin relatif dans img/mapSprites/Kanto/
# Usage : {{ zone.name|zone_image_path }}
# ---------------------------------------------------------------------------

def _normalize(s):
    """Minuscules + suppression accents pour comparaison souple."""
    import unicodedata
    s = s.lower().strip()
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

# Mapping nom de zone (normalisé) → chemin relatif depuis mapSprites/Kanto/
_ZONE_IMAGE_MAP = {
    # ── Villes / Towns ────────────────────────────────────────────────────
    'bourg palette':    'towns/Bourg_Palette_FullView.png',
    'jadielle':         'towns/Jadielle_FullView.png',
    'argenta':          'towns/Argenta_FullView.png',
    'azuria':           'towns/Azuria_FullView.png',
    'carmin sur mer':   'towns/Carmin_sur_Mer_FullView.png',
    'lavanville':       'towns/Lavanville_FullView.png',
    'safrania':         'towns/Safrania_FullView.png',
    'celadopole':       'towns/Céladopole_FullView.png',
    'parmanie':         'towns/Parmanie_FullView.png',
    "cramois'ile":      "towns/Cramois_ile_FullView.png",
    'cramois ile':      'towns/Cramois_ile_FullView.png',
    'fuchsia':          'towns/Fuchsia_City_Illustration.png',
    # Noms anglais alternatifs
    'pallet town':      'towns/Pallet_Town_Illustration.png',
    'viridian city':    'towns/Viridian_City_Illustration.png',
    'pewter city':      'towns/Pewter_City_Illustration.png',
    'cerulean city':    'towns/Cerulean_City_Illustration.png',
    'vermilion city':   'towns/Vermilion_City_Illustration.png',
    'lavender town':    'towns/Lavender_Town_Illustration.png',
    'celadon city':     'towns/Celadon_City_Illustration.png',
    'fuchsia city':     'towns/Fuchsia_City_Illustration.png',
    'saffron city':     'towns/Saffron_City_Illustration.png',
    'cinnabar island':  'towns/Cinnabar_Island_Illustration.png',
    # ── Landmarks ─────────────────────────────────────────────────────────
    'foret de jade':         'landmarks/Forêt_de_Jade.png',
    'viridian forest':       'landmarks/Viridian_Forest.png',
    'mont selenitee':        'landmarks/Mt_Moon.png',
    'mt moon':               'landmarks/Mt_Moon.png',
    'tunnel roche':          'landmarks/Rock_Tunnel.png',
    'rock tunnel':           'landmarks/Rock_Tunnel.png',
    'tour pokemon':          'landmarks/Tour_Pokémon_rdc.png',
    'pokemon tower':         'landmarks/Pokemon_Tower.png',
    'zone safari':           'landmarks/Safari_Zone.png',
    'safari zone':           'landmarks/Safari_Zone.png',
    'iles ecume':            'landmarks/Seafoam_Islands.png',
    'seafoam islands':       'landmarks/Seafoam_Islands.png',
    'centrale':              'landmarks/Centrale.png',
    'power plant':           'landmarks/Power_Plant.png',
    'grottes inconnues':     'landmarks/Cerulean_Cave.png',
    'cerulean cave':         'landmarks/Cerulean_Cave.png',
    'chemin de la victoire': 'landmarks/Victory_Road.png',
    'victory road':          'landmarks/Victory_Road.png',
    'plateau indigo':        'landmarks/Plateau_Indigo_extérieur.png',
    'indigo plateau':        'landmarks/Indigo_Plateau.png',
    'manoir pokemon':        'landmarks/Manoir_Pokémon_rdc.png',
    'pokemon mansion':       'landmarks/Pokemon_Mansion.png',
    'sylphe sarl':           'landmarks/Sylphe_SARL_Extérieur.png',
    'silph company':         'landmarks/Silph_Company.png',
    'dojo de safrania':      'landmarks/Dojo_de_Safrania.png',
    'grotte taupiqueur':     'landmarks/Digletts_Cave.png',
    "diglett's cave":        'landmarks/Digletts_Cave.png',
    'laboratoire pokemon':   'landmarks/Laboratoire_Pokémon.png',
    'musee des sciences':    "landmarks/Musée_des_Sciences_d'Argenta.png",
    "l'oceane":              "landmarks/Aquaria_jour.png",
    'aquaria':               'landmarks/Aquaria_jour.png',
    # ── Routes ────────────────────────────────────────────────────────────
    **{f'route {i}': f'routes/Route_{i}.png' for i in range(1, 18)},
    **{f'route {i}': f'routes/Route_{i}.png' for i in range(22, 29)},
    'route 19': 'routes/Chenal_19.png',
    'route 20': 'routes/Chenal_20.png',
    'route 21': 'routes/Chenal_21.png',
    'chenal 19': 'routes/Chenal_19.png',
    'chenal 20': 'routes/Chenal_20.png',
    'chenal 21': 'routes/Chenal_21.png',
    'souterrain routes 5 6': 'routes/Souterrain_(Routes_5-6).png',
    'souterrain routes 7 8': 'routes/Souterrain_(routes_7-8).png',
}

@register.filter(name='zone_image_path')
def zone_image_path(zone_name):
    """
    Retourne le chemin relatif de l'image d'une zone dans img/mapSprites/Kanto/.
    Usage dans le template :
        <img src="{% static 'img/mapSprites/Kanto/' %}{{ zone.name|zone_image_path }}">
    """
    if not zone_name:
        return 'Full_Kanto_Map.png'

    key = _normalize(str(zone_name))

    # 1. Correspondance exacte (normalisée)
    if key in _ZONE_IMAGE_MAP:
        return _ZONE_IMAGE_MAP[key]

    # 2. Correspondance partielle
    for map_key, path in _ZONE_IMAGE_MAP.items():
        if map_key in key or key in map_key:
            return path

    # 3. Détection de numéro de route
    route_match = re.search(r'route\s*(\d+)', key)
    if route_match:
        n = route_match.group(1)
        return f'routes/Route_{n}.png'

    chenal_match = re.search(r'chenal\s*(\d+)', key)
    if chenal_match:
        n = chenal_match.group(1)
        return f'routes/Chenal_{n}.png'

    # 4. Fallback : carte générale
    return 'Full_Kanto_Map.png'



# ---------------------------------------------------------------------------
# trainer_sprite_path : retourne le chemin de fichier dans img/trainer_sprites/
# Usage : {{ trainer|trainer_sprite_path }}
# ---------------------------------------------------------------------------

# Gym leaders Gen 1 (username exact)
_GYM_LEADER_SPRITES = {
    'brock':    'brock-gen3.png',
    'misty':    'misty-gen3.png',
    'lt. surge': 'ltsurge-gen3.png',
    'lt surge': 'ltsurge-gen3.png',
    'ltsurge':  'ltsurge-gen3.png',
    'erika':    'erika-gen3.png',
    'koga':     'koga-gen3.png',
    'sabrina':  'sabrina-gen3.png',
    'blaine':   'blaine-gen3.png',
    'giovanni': 'giovanni-gen3.png',
    # Elite Four / Champion
    'lorelei':  'lorelei-gen3.png',
    'bruno':    'bruno-gen3.png',
    'agatha':   'agatha-gen3.png',
    'lance':    'lance-gen3.png',
    'blue':     'blue-gen3champion.png',
    'red':      'red-gen3.png',
    'green':    'green.png',
    'leaf':     'leaf-gen3.png',
}

# Classes NPC → sprite (préfixe du username → fichier)
_NPC_CLASS_SPRITES = {
    'youngster':     'youngster-gen3.png',
    'lass':          'lass-gen3.png',
    'bug catcher':   'bugcatcher-gen3.png',
    'bug maniac':    'bugmaniac-gen3.png',
    'hiker':         'hiker-gen3.png',
    'camper':        'camper-gen3.png',
    'picnicker':     'picnicker-gen3.png',
    'super nerd':    'supernerd-gen3.png',
    'sailor':        'sailor-gen3.png',
    'gentleman':     'gentleman-gen3.png',
    'gambler':       'gambler-gen3.png',
    'engineer':      'engineer-gen3.png',
    'pokemaniac':    'pokemaniac-gen3.png',
    'channeler':     'channeler-gen3.png',
    'scientist':     'scientist-gen3.png',
    'biker':         'biker-gen3.png',
    'cue ball':      'cueball-gen3.png',
    'swimmer':       'swimmer-gen3.png',
    'black belt':    'blackbelt-gen3.png',
    'beauty':        'beauty-gen3.png',
    'bird keeper':   'birdkeeper-gen3.png',
    'tamer':         'tamer-gen3.png',
    'rocker':        'rocker-gen3.png',
    'psychic':       'psychic-gen3.png',
    'juggler':       'juggler-gen3.png',
    'burglar':       'burglar-gen3.png',
    'ace trainer':   'acetrainer-gen3.png',
    'fisherman':     'fisherman-gen3.png',
    'team rocket':   'rocketgrunt.png',
    'rocket':        'rocketgrunt.png',
    'jessie':        'teamrocket.png',
    'james':         'teamrocket.png',
    'rival':         'blue-gen3.png',
    'gary':          'blue-gen3.png',
    'gamin':         'youngster-gen3.png',
    'dresseur':      'acetrainer-gen3.png',
}

@register.filter(name='trainer_sprite_path')
def trainer_sprite_path(trainer):
    """
    Retourne le nom de fichier du sprite d'un dresseur dans img/trainer_sprites/.
    Accepte un objet Trainer ou une chaîne (username).

    Usage :
        <img src="{% static 'img/trainer_sprites/' %}{{ trainer|trainer_sprite_path }}">
    """
    if trainer is None:
        return 'unknown.png'

    # Si on reçoit un objet Trainer
    if hasattr(trainer, 'sprite_name') and trainer.sprite_name:
        return trainer.sprite_name

    username = getattr(trainer, 'username', str(trainer))
    trainer_type = getattr(trainer, 'trainer_type', '')
    username_lower = username.lower().strip()

    # 1. Gym leaders / personnages nommés
    if username_lower in _GYM_LEADER_SPRITES:
        return _GYM_LEADER_SPRITES[username_lower]

    # 2. Recherche partielle dans les noms connus
    for key, sprite in _GYM_LEADER_SPRITES.items():
        if key in username_lower:
            return sprite

    # 3. Correspondance par classe NPC (préfixe du username)
    for class_key, sprite in _NPC_CLASS_SPRITES.items():
        if username_lower.startswith(class_key):
            return sprite

    # 4. Recherche partielle de classe dans le username
    for class_key, sprite in _NPC_CLASS_SPRITES.items():
        if class_key in username_lower:
            return sprite

    # 5. Fallback par trainer_type
    type_fallback = {
        'gym_leader':  'acetrainer-gen1.png',
        'elite_four':  'acetrainerf-gen1.png',
        'champion':    'blue-gen1champion.png',
        'rival':       'blue-gen1.png',
        'trainer':     'youngster-gen1.png',
    }
    if trainer_type in type_fallback:
        return type_fallback[trainer_type]

    return 'unknown.png'