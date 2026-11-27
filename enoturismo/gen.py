# -*- coding: utf-8 -*-
"""Genera la sección de Enoturismo de WorldWinePedia dentro de una copia de la rama main.

Uso:  python3 enoturismo/gen.py /ruta/a/main  [--nav]

- Toma como plantilla la página de Herramientas ya publicada en cada idioma (cabecera, pie,
  SEO y scripts idénticos a los de la web en vivo) y le cambia el contenido.
- Escribe <l>/<seg>/index.html, <l>/<seg>/<slug>/index.html y
  <l>/<seg>/bodegas-visitables/index.html, y sitemaps/<l>-enoturismo.xml.
- Con --nav añade «Enoturismo» al menú y al pie de todas las páginas HTML de la web.
"""
import json, glob, os, re, sys, html, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
OUT = sys.argv[1]
DOMAIN = 'https://worldwinepedia.com'
LANGS = ['es', 'en', 'fr', 'it']
e = html.escape

sys.path.insert(0, os.path.join(SRC, 'tools'))
from i18n import SEG as SEG0

SEG = dict(SEG0)
SEG['eno'] = {'es': 'enoturismo', 'en': 'wine-tourism', 'fr': 'oenotourisme', 'it': 'enoturismo'}
SEG['tools'] = {'es': 'herramientas', 'en': 'tools', 'fr': 'outils', 'it': 'strumenti'}

def load(kind):
    out = {}
    for f in glob.glob(os.path.join(SRC, 'data', kind, '*.json')):
        d = json.load(open(f, encoding='utf-8')); out[d['slug']] = d
    return out
R = load('regions'); C = load('countries')
def T(x, l):
    if x is None: return ''
    if isinstance(x, dict): return x.get(l) or x.get('es') or ''
    return x
def strip(h): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h or '')).strip()

TX = json.load(open(os.path.join(HERE, 'textos.json'), encoding='utf-8'))
def tx(k, l): return TX[k][l]

ITEMS = {}
for f in sorted(glob.glob(os.path.join(HERE, 'rutas', '*.json'))):
    d = json.load(open(f, encoding='utf-8')); ITEMS[d['slug']] = d
GROUPS = ['catalunya', 'espana', 'mundo', 'guias']
ORDER = json.load(open(os.path.join(HERE, 'orden.json'), encoding='utf-8'))

# ---- bodegas publicadas en main (nombre, región, país, si tienen visitas) ----
WIN = {}
for f in glob.glob(os.path.join(OUT, 'es', 'bodegas', '*', 'index.html')):
    slug = f.split(os.sep)[-2]
    h = open(f, encoding='utf-8').read()
    cr = re.search(r'<div class="crumbs">(.*?)</div>', h).group(1)
    reg = re.search(r'regiones/([a-z0-9-]+)/', cr); co = re.search(r'paises/([a-z0-9-]+)/', cr)
    town = re.search(r'<dt>Localidad</dt><dd>(.*?)</dd>', h)
    WIN[slug] = {'name': html.unescape(re.search(r'<h1>(.*?)</h1>', h).group(1)),
                 'region': reg and reg.group(1), 'country': co and co.group(1),
                 'town': town and html.unescape(town.group(1)),
                 'visits': '<h3>Visitas y enoturismo</h3>' in h}

def path(l, slug=None, kind='eno'):
    u = '/%s/%s/' % (l, SEG[kind][l])
    return u + slug + '/' if slug else u

# ---- plantilla ----
SHELL = {l: open(os.path.join(OUT, l, SEG['tools'][l], 'index.html'), encoding='utf-8').read() for l in LANGS}

def render(l, alt, title, desc, main, crumbs_ld, ptype='WebPage', image=None, extra_css=''):
    """alt: lang->ruta absoluta. Devuelve el HTML con rutas relativas a la profundidad de alt[l]."""
    h = SHELL[l]
    depth = len([x for x in alt[l].strip('/').split('/') if x])
    pre = '../' * depth
    canon = DOMAIN + alt[l]
    img = image or (DOMAIN + '/img/og-%s.jpg' % l)
    # cabecera
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(title), h, 1)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % e(desc[:300]), h, 1)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % canon, h, 1)
    alts = ''.join('<link rel="alternate" hreflang="%s" href="%s%s">' % (x, DOMAIN, alt[x]) for x in LANGS) + '<link rel="alternate" hreflang="x-default" href="%s%s">' % (DOMAIN, alt['en'])
    h = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href="[^"]*">)+', alts, h, 1)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % e(title), h, 1)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % e(desc[:300]), h, 1)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % canon, h, 1)
    h = re.sub(r'<meta property="og:image" content="[^"]*"><meta property="og:image:width" content="\d+"><meta property="og:image:height" content="\d+">',
               '<meta property="og:image" content="%s">' % img + ('' if image else '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'), h, 1)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": ptype, "@id": canon + "#webpage", "url": canon, "name": title.split(' · ')[0], "description": desc[:300], "inLanguage": l,
         "isPartOf": {"@id": DOMAIN + "/#website"}, "primaryImageOfPage": {"@type": "ImageObject", "url": img}, "breadcrumb": {"@id": canon + "#breadcrumb"}},
        {"@type": "BreadcrumbList", "@id": canon + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u} for i, (n, u) in enumerate(crumbs_ld)]}]}
    h = re.sub(r'<script type="application/ld\+json" data-seo="1">.*?</script>', lambda m: '<script type="application/ld+json" data-seo="1">%s</script>' % json.dumps(ld, ensure_ascii=False), h, 1, flags=re.S)
    # selector de idioma (cabecera y pie) y enlaces de la ventana de edad
    def langlinks(m):
        return ''.join('<a href="%s" hreflang="%s" lang="%s"%s>%s</a>' % (alt[x], x, x, ' class="on"' if x == l else '', x.upper()) for x in LANGS)
    h = re.sub(r'(?:<a href="[^"]*" hreflang="[a-z]{2}" lang="[a-z]{2}"(?: class="on")?>[A-Z]{2}</a>){4}', langlinks, h)
    names = {'es': 'Español', 'en': 'English', 'fr': 'Français', 'it': 'Italiano'}
    h = re.sub(r'<div class="ln">.*?</div>', '<div class="ln">%s</div>' % ''.join('<a href="%s">%s</a>' % (alt[x], names[x]) for x in LANGS), h, 1, flags=re.S)
    # menú: sin «actual» en Herramientas; Enoturismo activo
    h = h.replace(' aria-current="page"', '')
    h = add_nav(h, l, current=True)
    # cuerpo
    h = re.sub(r'<style>.*?</main>', lambda m: '<style>%s</style>%s' % (CSS + extra_css, main), h, count=1, flags=re.S)
    # rutas absolutas -> relativas (la plantilla está a profundidad 2)
    h = re.sub(r'(href|src|action)="\.\./\.\./', r'\1="/', h)
    h = h.replace('window.WWP={root:"../../"', 'window.WWP={root:"/"')
    def rel(m):
        attr, u = m.group(1), m.group(2)
        if u.startswith('//'): return m.group(0)
        return '%s="%s%s"' % (attr, pre, u[1:])
    h = re.sub(r'(href|src|action)="(/[^"]*)"', rel, h)
    h = h.replace('window.WWP={root:"/"', 'window.WWP={root:"%s"' % pre)
    return h

NAVLABEL = {'es': 'Enoturismo', 'en': 'Wine tourism', 'fr': 'Œnotourisme', 'it': 'Enoturismo'}
def add_nav(h, l, current=False):
    """Añade Enoturismo al menú (después de Bodegas) y al pie (columna Explorar). Idempotente."""
    seg = SEG['eno'][l]
    if '/%s/%s/"' % (l, seg) in h.split('<nav', 1)[-1].split('</nav>', 1)[0]:
        return h
    wseg = SEG['wineries'][l]
    cur = ' aria-current="page"' if current else ''
    def navrep(m):
        a = m.group(0)
        return a + '<a href="%s%s/%s/"%s>%s</a>' % (m.group(1), l, seg, cur, NAVLABEL[l])
    nav_start = h.find('<nav aria-label="Menu">'); nav_end = h.find('</nav>', nav_start)
    if nav_start < 0: return h
    nav = h[nav_start:nav_end]
    nav2 = re.sub(r'<a href="([^"]*?)%s/%s/"(?: aria-current="page")?>[^<]*</a>' % (l, wseg), navrep, nav, count=1)
    h = h[:nav_start] + nav2 + h[nav_end:]
    # pie
    fs = h.find('<div class="footergrid">')
    if fs > 0:
        foot = h[fs:]
        foot = re.sub(r'(<a href="([^"]*?)%s/%s/">[^<]*</a>)(</div>)' % (l, wseg),
                      lambda m: m.group(1) + '<a href="%s%s/%s/">%s</a>' % (m.group(2), l, seg, NAVLABEL[l]) + m.group(3), foot, count=1)
        h = h[:fs] + foot
    return h

CSS = '''
.eno-hero{background:linear-gradient(90deg,rgba(32,58,49,.95),rgba(32,58,49,.55)),url(/img/hero.jpg) center 60%/cover;color:white;padding:46px 5%;margin:0 0 26px}
.eno-hero h1{font:clamp(34px,4.4vw,56px)/1.06 Georgia,serif;margin:8px 0 12px;letter-spacing:-1px}.eno-hero p{max-width:760px;color:#e0e7df;font-size:17px}
.eno-hero .quick a{color:white}
.eno-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;margin:16px 0 34px}
.eno-card{display:block;background:white;border:1px solid var(--line);padding:20px;color:var(--ink)}.eno-card:hover{border-color:#a2ad9b}
.eno-card small{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--wine)}.eno-card b{display:block;font:23px/1.15 Georgia,serif;margin:6px 0}.eno-card span{font-size:13px;color:#56635c}
.eno-sec{display:flex;justify-content:space-between;align-items:end;gap:20px;border-top:2px solid var(--ink);padding-top:14px;margin-top:10px}.eno-sec h2{margin:4px 0}.eno-sec p{color:#68736c;max-width:700px;margin:4px 0}
.eno-band{background:#f0f1e9;padding:22px;margin:0 0 30px;display:grid;grid-template-columns:1.4fr 1fr;gap:24px;align-items:center}.eno-band h2{margin:4px 0}
.eno-facts{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:24px 0}.eno-facts .box{margin:0}
.box ul{padding-left:18px;margin:6px 0}.box li{margin:4px 0}
.eno-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.eno-list a{display:block;background:white;border:1px solid var(--line);padding:14px}.eno-list a b{display:block;font:19px Georgia,serif}.eno-list a span{font-size:12px;color:#637168}
.eno-note{font-size:12px;color:#68736c;margin-top:18px}
@media(max-width:850px){.eno-band{grid-template-columns:1fr}.eno-facts{grid-template-columns:1fr}.eno-hero{padding:28px 5%}.eno-hero h1{font-size:34px}.eno-grid{grid-template-columns:1fr 1fr;gap:10px}.eno-card{padding:14px}.eno-card b{font-size:19px}}
@media(max-width:480px){.eno-grid{grid-template-columns:1fr}}
'''

def crumbs_html(l, items):
    parts = ['<a href="/%s/">%s</a>' % (l, tx('home', l))]
    for n, u in items:
        parts.append('<a href="%s">%s</a>' % (u, e(n)) if u else e(n))
    return '<div class="crumbs">' + ' › '.join(parts) + '</div>'

def card(l, it):
    return '<a class="eno-card" href="%s"><small>%s</small><b>%s</b><span>%s</span></a>' % (
        path(l, it['slug']), e(T(it.get('kicker'), l)), e(T(it['name'], l)), e(T(it.get('summary'), l)))

def region_photo(slug):
    if not slug: return ''
    f = os.path.join(OUT, 'es', 'regiones', slug, 'index.html')
    if not os.path.exists(f): return ''
    m = re.search(r'<figure class="hero-photo">.*?</figure>', open(f, encoding='utf-8').read(), re.S)
    return m.group(0) if m else ''

def photo_for(l, slug):
    """Foto de la ficha de región en el idioma l (las rutas tienen la misma profundidad que las fichas)."""
    if not slug: return '', None
    f = os.path.join(OUT, l, SEG['regions'][l], slug, 'index.html')
    if not os.path.exists(f): return '', None
    m = re.search(r'<figure class="hero-photo">.*?</figure>', open(f, encoding='utf-8').read(), re.S)
    if not m: return '', None
    fig = m.group(0).replace(' fetchpriority="high"', '')
    src = re.search(r'src="(?:\.\./)+(img/[^"]+)"', fig)
    # a rutas absolutas para que render() las relativice
    fig = re.sub(r'(src|href)="(?:\.\./)+', r'\1="/', fig)
    return fig, (DOMAIN + '/' + src.group(1)) if src else None

def winery_links(l, slugs):
    out = []
    for s_ in slugs:
        w = WIN.get(s_)
        if not w: continue
        rn = T(R.get(w['region'], {}).get('name'), l) if w['region'] else ''
        sub = ' · '.join(x for x in (w.get('town'), rn) if x)
        out.append('<a href="%s"><b>%s</b><span>%s%s</span></a>' % (path(l, s_, 'wineries'), e(w['name']), e(sub), (' · ' + tx('has_visits', l)) if w['visits'] else ''))
    return '<div class="eno-list">' + ''.join(out) + '</div>' if out else ''

def item_page(l, it):
    alt = {x: path(x, it['slug']) for x in LANGS}
    g = it['group']
    name = T(it['name'], l)
    fig, img = photo_for(l, it.get('photo_region') or it.get('region'))
    facts = ''
    for k in ('towns', 'see', 'season', 'food', 'tip'):
        v = T(it.get(k), l)
        if v:
            if not v.lstrip().startswith('<'): v = '<p>%s</p>' % e(v)
            facts += '<div class="box"><h3>%s</h3>%s</div>' % (tx('f_' + k, l), v)
    facts = '<div class="eno-facts">%s</div>' % facts if facts else ''
    # bodegas de la enciclopedia
    ws = list(it.get('wineries', []))
    if it.get('region') and it.get('auto_wineries', True):
        regs = [it['region']] + it.get('more_regions', [])
        ws += sorted([k for k, w in WIN.items() if w['region'] in regs and k not in ws], key=lambda k: (not WIN[k]['visits'], WIN[k]['name']))
    wl = winery_links(l, ws)
    wl = '<h2 style="margin-top:30px">%s</h2><p class="sub">%s</p>%s' % (tx('wineries_h', l), tx('wineries_p', l), wl) if wl else ''
    # aside
    side = '<aside>'
    rlinks = []
    for r in ([it['region']] if it.get('region') else []) + it.get('more_regions', []):
        if r in R: rlinks.append('<a href="%s">%s</a>' % (path(l, r, 'regions'), e(T(R[r]['name'], l) + ' · ' + T(R[r].get('kind'), l))))
    co = C.get(it.get('country'))
    if co: rlinks.append('<a href="%s">%s</a>' % (path(l, co['slug'], 'countries'), e(T(co['name'], l))))
    if rlinks: side += '<div class="box" style="margin-top:0"><h3>%s</h3><div class="linklist">%s</div></div>' % (tx('in_encyclopedia', l), ''.join(rlinks))
    same = [ITEMS[x] for x in ORDER[g] if x in ITEMS and x != it['slug']]
    side += '<div class="box"><h3>%s</h3><div class="linklist">%s</div></div>' % (tx('g_' + g, l), ''.join('<a href="%s">%s</a>' % (path(l, x['slug']), e(T(x['name'], l))) for x in same))
    side += '<div class="box"><h3>%s</h3><div class="linklist"><a href="%s">%s</a><a href="%s">%s</a></div></div>' % (tx('nav', l), path(l), tx('hub_h1', l), path(l, 'bodegas-visitables'), tx('dir_h1', l))
    side += '</aside>'
    cr = [(tx('nav', l), path(l)), (tx('g_' + g, l), path(l) + '#' + g), (name, None)]
    main = ('<main class="page"><div class="detail"><div>%s<span class="eyebrow">%s</span><h1>%s</h1><p class="lead">%s</p>%s<div class="prose">%s</div>%s</div>%s</div>%s<p class="eno-note">%s</p></main>'
            % (crumbs_html(l, cr), e(T(it.get('kicker'), l)), e(name), e(T(it.get('summary'), l)), fig, T(it['body'], l), facts, side, wl, tx('note', l)))
    title = T(it.get('title'), l) or (tx('title_route', l).format(n=name) if g != 'guias' else name)
    crumbs_ld = [(tx('home', l), '/%s/' % l), (tx('nav', l), path(l)), (name, path(l, it['slug']))]
    return alt, render(l, alt, title + ' · WorldWinePedia', strip(T(it.get('summary'), l)), main, crumbs_ld, 'Article' if g == 'guias' else 'WebPage', img)

def hub(l):
    alt = {x: path(x) for x in LANGS}
    secs = ''
    for g in GROUPS:
        its = [ITEMS[x] for x in ORDER[g] if x in ITEMS]
        if not its: continue
        secs += '<div class="eno-sec" id="%s"><div><span class="eyebrow">%s</span><h2>%s</h2><p>%s</p></div></div><div class="eno-grid">%s</div>' % (
            g, tx('g_' + g + '_eb', l), tx('g_' + g, l), tx('g_' + g + '_p', l), ''.join(card(l, it) for it in its))
        if g == 'catalunya':
            nv = sum(1 for w in WIN.values() if w['visits'])
            secs += '<div class="eno-band"><div><span class="eyebrow">%s</span><h2>%s</h2><p>%s</p></div><div><a class="btn" href="%s">%s ↗</a></div></div>' % (
                tx('dir_eb', l), tx('dir_h1', l), tx('dir_band', l).format(n=nv), path(l, 'bodegas-visitables'), tx('dir_btn', l))
    quick = ''.join('<a href="%s">%s</a>' % (path(l, s_), e(T(ITEMS[s_]['name'], l))) for s_ in ORDER['destacados'] if s_ in ITEMS)
    main = ('<main class="page" style="padding-top:0"><div class="eno-hero"><span class="eyebrow">%s</span><h1>%s</h1><p>%s</p><div class="quick">%s</div></div>%s<div class="prose" style="max-width:900px">%s</div>%s<p class="eno-note">%s</p></main>'
            % (tx('hub_eb', l), tx('hub_h1', l), tx('hub_p', l), quick, crumbs_html(l, [(tx('nav', l), None)]), tx('hub_body', l), secs, tx('note', l)))
    return alt, render(l, alt, tx('hub_title', l), strip(tx('hub_p', l)), main, [(tx('home', l), '/%s/' % l), (tx('nav', l), path(l))], 'CollectionPage')

def directory(l):
    alt = {x: path(x, 'bodegas-visitables') for x in LANGS}
    vis = [(k, w) for k, w in WIN.items() if w['visits']]
    def cname(c): return T(C.get(c, {}).get('name'), l) if c else ''
    countries = sorted({w['country'] for k, w in vis if w['country']}, key=lambda c: cname(c))
    opts = '<option value="">%s</option>' % tx('all_countries', l) + ''.join('<option value="%s">%s</option>' % (c, e(cname(c))) for c in countries)
    cards = ''
    for k, w in sorted(vis, key=lambda kw: (cname(kw[1]['country']), kw[1]['name'])):
        rn = T(R.get(w['region'], {}).get('name'), l) if w['region'] else ''
        sub = ' · '.join(x for x in (w.get('town'), rn, cname(w['country'])) if x)
        txt = (w['name'] + ' ' + sub).lower()
        cards += '<a class="card" href="%s" data-item data-type="" data-region="%s" data-text="%s"><h3>%s</h3><p>%s</p></a>' % (path(l, k, 'wineries'), w['country'] or '', e(txt), e(w['name']), e(sub))
    inner = ('<div data-filter-scope><div class="filters"><input class="ftext" type="search" placeholder="%s" aria-label="%s"><select class="freg" aria-label="%s">%s</select><span><b class="fcount"></b> %s</span></div><div class="listgrid">%s</div></div>'
             % (tx('dir_ph', l), tx('dir_ph', l), tx('country', l), opts, tx('results', l), cards))
    main = ('<main class="page">%s<h1 style="font:clamp(34px,4vw,50px)/1.1 Georgia,serif;margin:6px 0">%s</h1><p class="lead">%s</p>%s<p class="eno-note">%s</p></main>'
            % (crumbs_html(l, [(tx('nav', l), path(l)), (tx('dir_h1', l), None)]), tx('dir_h1', l), tx('dir_p', l).format(n=len(vis)), inner, tx('dir_note', l)))
    return alt, render(l, alt, tx('dir_title', l), strip(tx('dir_p', l).format(n=len(vis))), main,
                       [(tx('home', l), '/%s/' % l), (tx('nav', l), path(l)), (tx('dir_h1', l), path(l, 'bodegas-visitables'))], 'CollectionPage')

def write(p, content):
    full = os.path.join(OUT, p.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)

def main():
    pages = []
    for l in LANGS:
        a, h = hub(l); write(a[l], h); pages.append(a)
        a, h = directory(l); write(a[l], h); pages.append(a)
        for it in ITEMS.values():
            a, h = item_page(l, it); write(a[l], h); pages.append(a)
    # sitemaps por idioma
    os.makedirs(os.path.join(OUT, 'sitemaps'), exist_ok=True)
    for l in LANGS:
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        for a in pages:
            if a is None: continue
            sm += '<url><loc>%s%s</loc>%s</url>\n' % (DOMAIN, a[l], ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (x, DOMAIN, a[x]) for x in LANGS))
        sm += '</urlset>\n'
        open(os.path.join(OUT, 'sitemaps', '%s-enoturismo.xml' % l), 'w', encoding='utf-8').write(sm)
    # índice de sitemaps
    idx = os.path.join(OUT, 'sitemap.xml')
    s_ = open(idx, encoding='utf-8').read()
    if 'sitemapindex' in s_:
        for l in LANGS:
            loc = '%s/sitemaps/%s-enoturismo.xml' % (DOMAIN, l)
            if loc not in s_:
                s_ = s_.replace('</sitemapindex>', '<sitemap><loc>%s</loc></sitemap>\n</sitemapindex>' % loc)
        open(idx, 'w', encoding='utf-8').write(s_)
    print('páginas:', len(pages) // 1, 'rutas/guías:', len(ITEMS), 'bodegas visitables:', sum(1 for w in WIN.values() if w['visits']))
    if '--nav' in sys.argv:
        import hashlib
        css = os.path.join(OUT, 'css', 'style.css')
        c = open(css, encoding='utf-8').read()
        rule = '\n@media(max-width:850px){nav{grid-template-columns:repeat(3,1fr)}} /* 9 entradas: Enoturismo */\n'
        if 'Enoturismo */' not in c:
            open(css, 'w', encoding='utf-8').write(c.rstrip('\n') + rule)
        newv = hashlib.md5(open(css, 'rb').read()).hexdigest()[:8]
        n = 0
        for l in LANGS:
            for f in glob.glob(os.path.join(OUT, l, '**', 'index.html'), recursive=True):
                h = open(f, encoding='utf-8').read()
                h2 = re.sub(r'css/style\.css\?v=[0-9a-z]+', 'css/style.css?v=' + newv, add_nav(h, l))
                if h2 != h:
                    open(f, 'w', encoding='utf-8').write(h2); n += 1
        for f in glob.glob(os.path.join(OUT, '_blog', '**', '*.html'), recursive=True):
            h = open(f, encoding='utf-8').read()
            m = re.search(r'<html lang="([a-z]{2})"', h)
            if m and m.group(1) in LANGS:
                h2 = re.sub(r'css/style\.css\?v=[0-9a-z]+', 'css/style.css?v=' + newv, add_nav(h, m.group(1)))
                if h2 != h: open(f, 'w', encoding='utf-8').write(h2); n += 1
        print('menú actualizado en', n, 'páginas')

if __name__ == '__main__':
    main()
