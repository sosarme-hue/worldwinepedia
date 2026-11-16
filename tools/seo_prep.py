#!/usr/bin/env python3
"""Preparación SEO de WorldWinePedia (idempotente).
Uso: python3 -I seo_prep.py <carpeta_de_la_web> [AAAA-MM-DD]
Trabaja sobre la web ya generada (rama main), porque main tiene fichas que no están en la rama source.
- Títulos descriptivos por tipo de página e idioma (sin repetir el mismo título en 4 idiomas).
- Metadescripciones de 70-160 caracteres, cortadas por frase o palabra.
- og:title, og:description, og:type y og:image con la foto de cada ficha.
- JSON-LD: WebSite en portadas, WebPage + BreadcrumbList en todas, y la entidad (bodega, país,
  región, uva, vino) sin el Product incompleto que Search Console marca como error.
- width/height en las imágenes locales y sin lazy en la foto principal (mejor LCP y CLS).
- Buscador interno con noindex y fuera del sitemap.
- sitemap.xml pasa a índice de sitemaps por idioma y sección, con lastmod.
- robots.txt cierra /dist/, /tools/ y /_blog/.
"""
import os, re, sys, json, html, posixpath, datetime
from PIL import Image

ROOT = sys.argv[1].rstrip('/')
HOY = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
D = 'https://worldwinepedia.com'
BRAND = 'WorldWinePedia'
SUF = ' · ' + BRAND
MAXT = 65
LANGS = ['es', 'en', 'fr', 'it']
OGL = {'es': 'es_ES', 'en': 'en_GB', 'fr': 'fr_FR', 'it': 'it_IT'}

SEG = {  # carpeta -> tipo
 'es': {'vinos': 'wine', 'uvas': 'grape', 'bodegas': 'winery', 'paises': 'country', 'regiones': 'region', 'aprender': 'article', 'herramientas': 'tool', 'glosario': 'glossary', 'buscar': 'search'},
 'en': {'wines': 'wine', 'grapes': 'grape', 'wineries': 'winery', 'countries': 'country', 'regions': 'region', 'learn': 'article', 'tools': 'tool', 'glossary': 'glossary', 'search': 'search'},
 'fr': {'vins': 'wine', 'cepages': 'grape', 'domaines': 'winery', 'pays': 'country', 'regions': 'region', 'apprendre': 'article', 'outils': 'tool', 'glossaire': 'glossary', 'recherche': 'search'},
 'it': {'vini': 'wine', 'vitigni': 'grape', 'cantine': 'winery', 'paesi': 'country', 'regioni': 'region', 'imparare': 'article', 'strumenti': 'tool', 'glossario': 'glossary', 'cerca': 'search'},
}

# Títulos de los listados y la portada (sin marca: se añade si cabe)
LIST_T = {
 'es': {'': 'WorldWinePedia: enciclopedia del vino, uvas, regiones y bodegas', 'wine': 'Todos los vinos: fichas de cata, maridaje y dónde comprar', 'grape': 'Uvas del vino: variedades tintas y blancas de la A a la Z',
        'winery': 'Bodegas del mundo: historia, viñedos y vinos', 'country': 'Países del vino: regiones, uvas e historia', 'region': 'Regiones y denominaciones de origen del vino',
        'article': 'Aprender sobre vino: cata, maridaje, viticultura y ciencia', 'glossary': 'Glosario del vino: términos de cata y elaboración', 'tool': 'Herramientas del vino: maridajes, mapa y comparador de uvas'},
 'en': {'': 'WorldWinePedia: the wine encyclopedia of grapes, regions and wineries', 'wine': 'All wines: tasting notes, food pairing and where to buy', 'grape': 'Wine grapes: red and white varieties from A to Z',
        'winery': 'Wineries of the world: history, vineyards and wines', 'country': 'Wine countries: regions, grapes and history', 'region': 'Wine regions and appellations of the world',
        'article': 'Learn about wine: tasting, food pairing, viticulture and science', 'glossary': 'Wine glossary: tasting and winemaking terms', 'tool': 'Wine tools: food pairing, appellation map and grape comparison'},
 'fr': {'': "WorldWinePedia : l'encyclopédie du vin, cépages, régions et domaines", 'wine': 'Tous les vins : dégustation, accords et où les acheter', 'grape': 'Cépages : variétés rouges et blanches de A à Z',
        'winery': 'Domaines du monde : histoire, vignobles et vins', 'country': 'Pays du vin : régions, cépages et histoire', 'region': 'Régions viticoles et appellations du monde',
        'article': 'Apprendre le vin : dégustation, accords, viticulture et science', 'glossary': 'Glossaire du vin : termes de dégustation et de vinification', 'tool': 'Outils du vin : accords mets-vins, carte et comparateur de cépages'},
 'it': {'': "WorldWinePedia: l'enciclopedia del vino, vitigni, regioni e cantine", 'wine': 'Tutti i vini: degustazione, abbinamenti e dove comprarli', 'grape': 'Vitigni: varietà rosse e bianche dalla A alla Z',
        'winery': 'Cantine del mondo: storia, vigneti e vini', 'country': 'Paesi del vino: regioni, vitigni e storia', 'region': 'Regioni vinicole e denominazioni del mondo',
        'article': 'Imparare il vino: degustazione, abbinamenti, viticoltura e scienza', 'glossary': 'Glossario del vino: termini di degustazione e vinificazione', 'tool': 'Strumenti del vino: abbinamenti, mappa e confronto tra vitigni'},
}
COLOR = {
 'es': {'Tinto': 'vino tinto', 'Blanco': 'vino blanco', 'Rosado': 'vino rosado', 'Espumoso': 'espumoso', 'Dulce': 'vino dulce', 'Generoso': 'vino generoso'},
 'en': {'Red': 'red wine', 'White': 'white wine', 'Rosé': 'rosé wine', 'Sparkling': 'sparkling wine', 'Sweet': 'sweet wine', 'Fortified': 'fortified wine'},
 'fr': {'Rouge': 'vin rouge', 'Blanc': 'vin blanc', 'Rosé': 'vin rosé', 'Effervescent': 'vin effervescent', 'Doux': 'vin doux', 'Vin muté': 'vin muté'},
 'it': {'Rosso': 'vino rosso', 'Bianco': 'vino bianco', 'Rosato': 'vino rosato', 'Spumante': 'spumante', 'Dolce': 'vino dolce', 'Liquoroso': 'vino liquoroso'},
}
def prep(l, place):
    if l == 'es': return 'de ' + place
    if l == 'en': return 'from ' + place
    if l == 'fr': return ("d'" if re.match(r'[AEIOUYÉÈÂÎaeiouy]', place) else 'de ') + place
    return '– ' + place
TPL = {
 'grape': {'es': 'Uva {n}: origen, aromas y dónde se cultiva', 'en': '{n} grape: origin, aromas and where it grows', 'fr': 'Cépage {n} : origine, arômes et terroirs', 'it': 'Vitigno {n}: origine, aromi e zone di coltivazione'},
 'grape2': {'es': 'Uva {n}: origen y aromas', 'en': '{n} grape: origin and aromas', 'fr': 'Cépage {n} : origine et arômes', 'it': 'Vitigno {n}: origine e aromi'},
 'country': {'es': '{n}: regiones vinícolas, uvas e historia del vino', 'en': '{n}: wine regions, grapes and history', 'fr': '{n} : régions viticoles, cépages et histoire', 'it': '{n}: regioni vinicole, vitigni e storia'},
 'region': {'es': '{n}: clima, suelos, uvas y vinos', 'en': '{n}: climate, soils, grapes and wines', 'fr': '{n} : climat, sols, cépages et vins', 'it': '{n}: clima, suoli, vitigni e vini'},
 'region2': {'es': '{n}: uvas y vinos', 'en': '{n}: grapes and wines', 'fr': '{n} : cépages et vins', 'it': '{n}: vitigni e vini'},
 'winery': {'es': '{n} ({r}): historia, viñedos y vinos', 'en': '{n} ({r}): history, vineyards and wines', 'fr': '{n} ({r}) : histoire, vignobles et vins', 'it': '{n} ({r}): storia, vigneti e vini'},
 'winery2': {'es': '{n}: historia, viñedos y vinos', 'en': '{n}: history, vineyards and wines', 'fr': '{n} : histoire, vignobles et vins', 'it': '{n}: storia, vigneti e vini'},
 'winery3': {'es': '{n}: bodega y vinos', 'en': '{n}: winery and wines', 'fr': '{n} : domaine et vins', 'it': '{n}: cantina e vini'},
}
WINE_TAIL = {'es': ' Perfil de cata, maridaje y dónde comprarlo.', 'en': ' Tasting notes, food pairing and where to buy it.', 'fr': " Dégustation, accords et où l'acheter.", 'it': ' Degustazione, abbinamenti e dove comprarlo.'}

U = html.unescape
def E(s): return html.escape(s, quote=True)
def clean(s): return re.sub(r'\s+', ' ', U(re.sub(r'<[^>]+>', ' ', s or ''))).strip()
def short(n):
    m = re.match(r'^(.*?)\s*\(.*\)\s*$', n)
    return m.group(1) if m and m.group(1) else n
def brand(t):
    return t + SUF if len(t + SUF) <= MAXT else t
def fit(*opts):
    for o in opts:
        if o and len(o) <= MAXT: return o
    return [o for o in opts if o][-1]
def cut(d, n=160):
    d = re.sub(r'\s+', ' ', d).strip()
    if len(d) <= n: return d
    s = d[:n]
    m = list(re.finditer(r'[.!?…](\s|$)', s))
    if m and m[-1].end() >= 90: return s[:m[-1].end()].strip()
    s = s[:n - 1].rsplit(' ', 1)[0].rstrip(',;:–- ')
    return s + '…'

def crumbs(h, page):
    m = re.search(r'<div class="crumbs">(.*?)</div>', h)
    if not m: return []
    out = []
    for part in m.group(1).split(' › '):
        a = re.match(r'<a href="([^"]*)">(.*?)</a>', part)
        if a:
            href = a.group(1)
            u = posixpath.normpath(posixpath.join(page, href)) + '/'
            if u.startswith('//'): u = u[1:]
            out.append((clean(a.group(2)), D + u.replace('/index.html/', '/')))
        else:
            out.append((clean(part), None))
    return out

IMGSIZE = {}
def size(rel):
    p = os.path.join(ROOT, rel.lstrip('/'))
    if rel not in IMGSIZE:
        try:
            with Image.open(p) as im: IMGSIZE[rel] = im.size
        except Exception: IMGSIZE[rel] = None
    return IMGSIZE[rel]

def fix_imgs(h, page):
    main_s = h.find('<main'); first = [True]
    def f(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src or src.group(1).startswith(('http', '//', 'data:')): return tag
        rel = posixpath.normpath(posixpath.join(page, src.group(1)))
        if 'width=' not in tag:
            wh = size(rel)
            if wh: tag = tag.replace('<img ', '<img width="%d" height="%d" ' % wh, 1)
        if first[0] and m.start() > main_s >= 0 and '/img/wm/' in rel:
            first[0] = False
            tag = tag.replace(' loading="lazy"', ' fetchpriority="high"')
        return tag
    return re.sub(r'<img [^>]*>', f, h)

def first_photo(h, page):
    m = re.search(r'<main.*?<img [^>]*src="([^"]*img/wm/[^"]+)"', h, re.S)
    if not m: return None
    rel = posixpath.normpath(posixpath.join(page, m.group(1)))
    return rel, size(rel)

def set_meta(h, attr, key, val):
    pat = r'<meta %s="%s" content="[^"]*">' % (attr, re.escape(key))
    new = '<meta %s="%s" content="%s">' % (attr, key, E(val))
    if re.search(pat, h): return re.sub(pat, lambda m: new, h, count=1)
    return h.replace('</head>', new + '\n</head>', 1)

ST = {'pages': 0, 'title': 0, 'desc': 0, 'noindex': 0, 'product_ld_removed': 0}
CSV = []
SITEMAP = {}  # nombre -> [(url, alts)]

def process(path):
    rel = '/' + os.path.relpath(path, ROOT).replace(os.sep, '/')
    page = rel[:-len('index.html')]  # /es/vinos/x/
    h = open(path, encoding='utf-8').read()
    orig = h
    parts = [p for p in page.split('/') if p]
    if not parts: return  # raíz: redirección por idioma, se deja igual
    l = parts[0]
    if l not in LANGS: return
    kind = SEG[l].get(parts[1]) if len(parts) > 1 else 'home'
    if len(parts) > 1 and kind is None: kind = 'static'
    is_list = len(parts) == 2 and kind not in ('static',)
    ST['pages'] += 1

    t0 = clean(re.search(r'<title>(.*?)</title>', h, re.S).group(1))
    dm = re.search(r'<meta name="description" content="([^"]*)"', h)
    d0 = U(dm.group(1)) if dm else ''
    h1 = clean((re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S) or [None, ''])[1])
    eb = clean((re.search(r'<span class="eyebrow">(.*?)</span>', h, re.S) or [None, ''])[1])
    cr = crumbs(h, page)
    canon = D + page

    # ---------- títulos ----------
    t = t0; ent = None
    if kind == 'home': t = LIST_T[l]['']
    elif is_list and kind in LIST_T[l]: t = brand(LIST_T[l][kind])
    elif kind == 'wine' and h1:
        col = clean((re.search(r'<span class="tag2 t">(.*?)</span>', h) or [None, ''])[1])
        cp = COLOR[l].get(col, '')
        reg = cr[-2][0] if len(cr) >= 3 else ''
        win = short(eb) if eb else ''
        tail = (cp + ' ' + prep(l, reg)).strip() if cp and reg else cp
        sep = ': ' if l != 'fr' else ' : '
        if l == 'it' and cp and reg: tail = cp + ' – ' + reg
        has_w = win and (win.split()[0].lower() in h1.lower() or len(win) > 28)
        nm = h1 if has_w or not win else '%s (%s)' % (h1, win)
        t = fit(brand(nm + sep + tail) if tail else brand(nm), nm + sep + tail if tail else nm,
                (nm + sep + cp) if cp else nm)
        ent = {'@type': 'Thing', 'name': h1}
        if win: ent['description'] = d0
    elif kind == 'grape' and h1:
        t = fit(brand(TPL['grape'][l].format(n=h1)), TPL['grape'][l].format(n=h1), TPL['grape2'][l].format(n=h1), h1)
        ent = {'@type': 'Thing', 'name': h1}
    elif kind == 'country' and h1:
        t = fit(brand(TPL['country'][l].format(n=h1)), TPL['country'][l].format(n=h1))
        ent = {'@type': 'Country', 'name': h1}
    elif kind == 'region' and h1:
        ab = re.search(r'\(([^()]+)\)\s*$', eb)
        if ab and not re.match(r'^(?=(?:[^A-Z]*[A-Z]){2})[A-Z][A-Za-z.]{1,7}$', ab.group(1)): ab = None
        n = h1 if not ab or ab.group(1) in h1 else '%s (%s)' % (h1, ab.group(1))
        t = fit(brand(TPL['region'][l].format(n=n)), TPL['region'][l].format(n=n), TPL['region2'][l].format(n=n), TPL['region2'][l].format(n=h1), h1)
        ent = {'@type': 'Place', 'name': h1}
        if len(cr) >= 3: ent['containedInPlace'] = {'@type': 'Country', 'name': cr[1][0]}
    elif kind == 'winery' and h1:
        n = short(h1); reg = cr[-2][0] if len(cr) >= 3 else ''
        t = fit(brand(TPL['winery'][l].format(n=n, r=reg)) if reg else None, TPL['winery'][l].format(n=n, r=reg) if reg else None,
                brand(TPL['winery2'][l].format(n=n)), TPL['winery2'][l].format(n=n), TPL['winery3'][l].format(n=n), n)
        ent = {'@type': 'Organization', 'name': h1}
        if len(cr) >= 3:
            ent['address'] = {'@type': 'PostalAddress', 'addressRegion': reg, 'addressCountry': cr[1][0]}
    elif kind == 'article' and h1 and not is_list:
        t = fit(brand(h1), h1)
    if t != t0:
        ST['title'] += 1
        h = re.sub(r'<title>.*?</title>', lambda m: '<title>%s</title>' % E(t), h, count=1, flags=re.S)

    # ---------- descripción ----------
    d = d0
    if kind == 'wine' and len(d) + len(WINE_TAIL[l]) <= 160: d = d.rstrip() + WINE_TAIL[l]
    d = cut(d)
    if len(d) < 50 and is_list and kind in LIST_T[l]: d = cut(LIST_T[l][kind] + '. ' + d)
    if d != d0:
        ST['desc'] += 1
        h = set_meta(h, 'name', 'description', d)
    h = set_meta(h, 'property', 'og:title', t)
    h = set_meta(h, 'property', 'og:description', d)
    content = kind in ('wine', 'grape', 'country', 'region', 'winery', 'article') and not is_list
    h = set_meta(h, 'property', 'og:type', 'article' if content else 'website')

    # ---------- foto ----------
    h = fix_imgs(h, page)
    ph = first_photo(h, page)
    if ph and ph[1]:
        h = set_meta(h, 'property', 'og:image', D + ph[0])
        h = set_meta(h, 'property', 'og:image:width', str(ph[1][0]))
        h = set_meta(h, 'property', 'og:image:height', str(ph[1][1]))
    img_url = D + ph[0] if ph and ph[1] else D + '/img/og-%s.jpg' % l

    # ---------- noindex del buscador ----------
    if kind == 'search':
        if 'name="robots"' not in h:
            h = h.replace('<meta name="viewport"', '<meta name="robots" content="noindex,follow">\n<meta name="viewport"', 1)
        ST['noindex'] += 1

    # ---------- JSON-LD ----------
    h = re.sub(r'<script type="application/ld\+json" data-seo="1">.*?</script>', '', h, flags=re.S)
    def drop_product(m):
        try: j = json.loads(m.group(1))
        except Exception: return m.group(0)
        if j.get('@type') == 'Product':
            ST['product_ld_removed'] += 1
            return ''
        return m.group(0)
    h = re.sub(r'<script type="application/ld\+json">(.*?)</script>', drop_product, h, flags=re.S)
    g = []
    site = {'@type': 'WebSite', '@id': D + '/#website', 'url': D + '/', 'name': BRAND,
            'inLanguage': LANGS, 'publisher': {'@id': D + '/#org'}}
    org = {'@type': 'Organization', '@id': D + '/#org', 'name': BRAND, 'url': D + '/', 'logo': D + '/img/logo.png'}
    if kind == 'home': g += [site, org]
    wp = {'@type': 'CollectionPage' if (is_list or kind == 'home') else 'WebPage', '@id': canon + '#webpage', 'url': canon,
          'name': h1 or t, 'description': d, 'inLanguage': l, 'isPartOf': {'@id': D + '/#website'},
          'primaryImageOfPage': {'@type': 'ImageObject', 'url': img_url}}
    if ent:
        ent = {k: v for k, v in ent.items() if v}
        wp['about'] = ent
    if cr:
        wp['breadcrumb'] = {'@id': canon + '#breadcrumb'}
        items = []
        for i, (n, u) in enumerate(cr, 1):
            it = {'@type': 'ListItem', 'position': i, 'name': n}
            it['item'] = u if u else canon
            items.append(it)
        g.append({'@type': 'BreadcrumbList', '@id': canon + '#breadcrumb', 'itemListElement': items})
    g.insert(0 if kind != 'home' else 2, wp)
    ld = '<script type="application/ld+json" data-seo="1">%s</script>' % json.dumps({'@context': 'https://schema.org', '@graph': g}, ensure_ascii=False).replace('</', '<\\/')
    h = h.replace('</head>', ld + '\n</head>', 1)

    if h != orig: open(path, 'w', encoding='utf-8').write(h)
    CSV.append((page, t0, t, len(t), d0, d))

    # ---------- sitemap ----------
    if kind == 'search': return
    alts = dict(re.findall(r'<link rel="alternate" hreflang="([a-z-]+)" href="([^"]+)">', h))
    grp = l + '-' + ({'home': 'portada', 'static': 'paginas', 'glossary': 'paginas', 'tool': 'paginas'}.get(kind, kind) if not is_list or kind == 'home' else 'portadas')
    SITEMAP.setdefault(grp, []).append((canon, alts))

for dp, dn, fn in os.walk(ROOT):
    dn[:] = [x for x in dn if not (dp == ROOT and x in ('.git', 'dist', 'tools', '_blog', 'img', 'css', 'js'))]
    if 'index.html' in fn: process(os.path.join(dp, 'index.html'))

# ---------- sitemaps ----------
os.makedirs(os.path.join(ROOT, 'sitemaps'), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, 'sitemaps')):
    if f.endswith('.xml'): os.remove(os.path.join(ROOT, 'sitemaps', f))
idx = []
for grp in sorted(SITEMAP):
    rows = sorted(SITEMAP[grp])
    x = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u, alts in rows:
        al = ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (k, E(v)) for k, v in alts.items())
        x.append('<url><loc>%s</loc><lastmod>%s</lastmod>%s</url>' % (E(u), HOY, al))
    x.append('</urlset>')
    open(os.path.join(ROOT, 'sitemaps', grp + '.xml'), 'w', encoding='utf-8').write('\n'.join(x) + '\n')
    idx.append('<sitemap><loc>%s/sitemaps/%s.xml</loc><lastmod>%s</lastmod></sitemap>' % (D, grp, HOY))
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(idx) + '\n</sitemapindex>\n')

open(os.path.join(ROOT, 'robots.txt'), 'w').write(
    'User-agent: *\nAllow: /\nDisallow: /dist/\nDisallow: /tools/\nDisallow: /_blog/\n\n'
    'Sitemap: %s/sitemap.xml\nSitemap: %s/sitemap-blog.xml\n' % (D, D))

out = os.environ.get('SEO_CSV')
if out:
    import csv
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['pagina', 'titulo_antes', 'titulo_despues', 'largo', 'descripcion_antes', 'descripcion_despues'])
        w.writerows(CSV)
print(json.dumps(ST), 'sitemaps:', {k: len(v) for k, v in sorted(SITEMAP.items())})
