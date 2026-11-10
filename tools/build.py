# -*- coding: utf-8 -*-
"""Genera la web estática de WorldWinePedia en dist/ a partir de data/."""
import json, glob, os, shutil, html, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from i18n import LANGS, LANG_NAMES, SEG, S, SHIP, ATLAS
from pages import STATIC_PAGES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
DIST = os.path.join(ROOT, 'dist')
DOMAIN = 'https://worldwinepedia.com'
OG = {'es': 'es_ES', 'en': 'en_GB', 'fr': 'fr_FR', 'it': 'it_IT'}

def load(kind):
    out = {}
    for f in sorted(glob.glob(os.path.join(DATA, kind, '*.json'))):
        try:
            d = json.load(open(f, encoding='utf-8'))
            out[d['slug']] = d
        except Exception as e:
            print('ERROR', f, e)
    return out

C, R, G, B, V, A = (load(k) for k in ('countries', 'regions', 'grapes', 'wineries', 'wines', 'articles'))
GL = []
for f in sorted(glob.glob(os.path.join(DATA, 'glossary-*.json'))):
    try: GL += json.load(open(f, encoding='utf-8'))
    except Exception as e: print('ERROR', f, e)
IMG = {}
try: IMG = json.load(open(os.path.join(DATA, 'images.json'), encoding='utf-8'))
except Exception: pass
WM = {}
try: WM = json.load(open(os.path.join(DATA, 'images_wm.json'), encoding='utf-8'))
except Exception: pass
import zlib
def pick(pool, slug):
    return pool[zlib.crc32(slug.encode()) % len(pool)] if pool else None
ILL = {'es': 'imagen ilustrativa', 'en': 'illustrative image', 'fr': 'image d\'illustration', 'it': 'immagine illustrativa'}
PH = {'es': 'Foto', 'en': 'Photo', 'fr': 'Photo', 'it': 'Foto'}
def photo(f, l, w=1400, cls='hero-photo'):
    if not f: return ''
    if 'src' in f:
        lic = html.escape(f.get('license', ''))
        if f.get('license_url'): lic = f'<a href="{html.escape(f["license_url"])}" rel="nofollow noopener" target="_blank">{lic}</a>'
        return (f'<figure class="{cls}"><img src="{f["src"]}" alt="{html.escape(f.get("alt", ""))}" loading="lazy">'
                f'<figcaption>{PH[l]}: {html.escape(f.get("author", ""))[:80]} · {lic} · <a href="{html.escape(f["page"])}" rel="nofollow noopener" target="_blank">Wikimedia Commons</a></figcaption></figure>')
    sep = '&' if '?' in f['url'] else '?'
    src = f"{f['url']}{sep}w={w}&q=75&fm=jpg&fit=crop&crop=entropy"
    ref = '?utm_source=worldwinepedia&utm_medium=referral'
    ill = '' if f.get('specific') else ' · ' + ILL[l]
    return (f'<figure class="{cls}"><img src="{html.escape(src)}" alt="{html.escape(f.get("alt", ""))}" loading="lazy" width="{w}" height="{int(w*0.5)}">'
            f'<figcaption>{PH[l]}: <a href="{html.escape(f["author_url"] + ref)}" rel="nofollow noopener" target="_blank">{html.escape(f["author"])}</a> / '
            f'<a href="https://unsplash.com/{ref}" rel="nofollow noopener" target="_blank">Unsplash</a>{ill}</figcaption></figure>')
STORES = json.load(open(os.path.join(ROOT, 'stores.json'), encoding='utf-8'))

try: CUL = json.load(open(os.path.join(ROOT, 'data', 'culinapedia_links.json'), encoding='utf-8'))
except Exception: CUL = {}
CUL_T = {"es": ("Más historia en Culinapedia", "Historia y cultura de {n} en Culinapedia, la enciclopedia de la gastronomía."),
         "en": ("More history on Culinapedia", "History and culture of {n} on Culinapedia, the encyclopedia of food and culinary culture."),
         "fr": ("Plus d'histoire sur Culinapedia", "Histoire et culture de {n} sur Culinapedia (en anglais)."),
         "it": ("Più storia su Culinapedia", "Storia e cultura di {n} su Culinapedia (in inglese).")}
def cul_box(l, kind, slug, name):
    p = CUL.get(kind, {}).get(slug)
    if not p: return ''
    href = 'https://culinapedia.com/' + ('' if l == 'es' else 'en/') + p
    t, d = CUL_T[l]
    return f'<div class="box"><h3>{t}</h3><p><a href="{e(href)}" rel="noopener" target="_blank">{e(d.format(n=name))} ↗</a></p></div>'

def T(x, l):
    if x is None: return ''
    if isinstance(x, dict): return x.get(l) or x.get('es') or x.get('en') or ''
    return x
def s(key, l): return T(S[key], l)
e = html.escape
def strip(h): return re.sub(r'<[^>]+>', ' ', h or '')
def ws(l, s_):  # words
    return re.sub(r'\s+', ' ', s_).strip()

def url(l, kind=None, slug=None):
    if kind is None: return '/%s/' % l
    u = '/%s/%s/' % (l, SEG[kind][l])
    if slug: u += slug + '/'
    return u

PREVIEW = False
def relativize(content, path):
    depth = len([x for x in path.strip('/').split('/') if x]) if not path.endswith(('.json', '.xml', '.txt')) else 0
    pre = '../' * depth
    def fix(m):
        attr, u = m.group(1), m.group(2)
        if u.startswith('//'): return m.group(0)
        frag = ''
        if '#' in u: u, frag = u.split('#', 1); frag = '#' + frag
        rel = pre + u[1:]
        if PREVIEW and (rel == '' or rel.endswith('/')): rel += 'index.html'
        if rel == '': rel = './'
        return '%s="%s%s"' % (attr, rel, frag)
    content = re.sub(r'(href|src|action)="(/[^"]*)"', fix, content)
    content = content.replace('window.WWP={lang:', 'window.WWP={root:"%s",preview:%s,lang:' % (pre, 'true' if PREVIEW else 'false'))
    content = content.replace('window.PV', 'true' if PREVIEW else 'false')
    return content

def write(path, content):
    if path.endswith('/') or path == '/': content = relativize(content, path)
    full = os.path.join(DIST, path.strip('/'), 'index.html') if not path.endswith('.json') and not path.endswith('.xml') and not path.endswith('.txt') else os.path.join(DIST, path.strip('/'))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)

SITEMAP = []

SISTERS = ['classicapedia.com', 'pinacopedia.com', 'filopedia.com', 'cinematopedia.com', 'medicapedia.org', 'tenispedia.com', 'newtonpedia.com', 'culinapedia.com', 'mythicapedia.com', 'zodiacopedia.com', 'ludicopedia.com', 'catdogpedia.com']
SISTERS_EN = set(SISTERS) - {'ludicopedia.com'}
def sister_sites(l):
    tit = {'es': 'Webs hermanas', 'en': 'Sister sites', 'fr': 'Sites frères', 'it': 'Siti fratelli'}[l]
    links = ' · '.join('<a href="https://%s/%s">%s</a>' % (d, 'en/' if l == 'en' and d in SISTERS_EN else '', d) for d in SISTERS)
    return tit + ': ' + links

import hashlib as _h
ASSET_V = {k: _h.md5(open(os.path.join(ROOT, 'static', f), 'rb').read()).hexdigest()[:8] for k, f in (('css', 'css/style.css'), ('js', 'js/site.js'))}

def layout(l, title, desc, body, alt, active=''):
    """alt: dict lang->path for hreflang"""
    SITEMAP.append(alt)
    links = ''.join('<link rel="alternate" hreflang="%s" href="%s%s">' % (x, DOMAIN, alt[x]) for x in LANGS)
    links += '<link rel="alternate" hreflang="x-default" href="%s%s">' % (DOMAIN, alt['en'])
    navs = [('wines', 'nav_wines'), ('countries', 'nav_atlas'), ('grapes', 'nav_grapes'), ('wineries', 'nav_wineries'), ('articles', 'nav_learn'), ('glossary', 'nav_glossary'), ('tools', 'nav_tools')]
    nav = ''.join('<a href="%s"%s>%s</a>' % (url(l, k), ' aria-current="page"' if active == k else '', s(n, l)) for k, n in navs)
    langs = ''.join('<a href="%s" hreflang="%s" lang="%s"%s>%s</a>' % (alt[x], x, x, ' class="on"' if x == l else '', x.upper()) for x in LANGS)
    ship_opts = ''.join('<option value="%s">%s</option>' % (c, T(n, l)) for c, n in SHIP)
    t_js = json.dumps({k: s(k, l) for k in ('see_price', 'compare_world', 'us_note', 'fr_note', 'age_bye', 'results', 'no_results')}, ensure_ascii=False)
    stores_js = json.dumps({k: STORES[k] for k in ('amazon', 'shops', 'comparator')}, ensure_ascii=False)
    agelinks = ''.join('<a href="%s">%s</a>' % (alt[x], LANG_NAMES[x]) for x in LANGS)
    foot_explore = ''.join('<a href="%s">%s</a>' % (url(l, k), s(n, l)) for k, n in navs[:4])
    foot_learn = ''.join('<a href="%s">%s</a>' % (url(l, 'articles') + '#' + sec, T(S['sections'][sec], l)) for sec in ('ciencia', 'viticultura', 'cata', 'maridaje', 'historia')) + '<a href="%s">%s</a>' % (url(l, 'glossary'), s('nav_glossary', l))
    foot_proj = ''.join('<a href="%s">%s</a>' % (url(l, k), s(k + '_t', l)) for k in ('about', 'affiliates', 'privacy', 'legal'))
    return f'''<!doctype html>
<html lang="{l}" translate="no">
<head>
<meta charset="utf-8">
<meta name="google" content="notranslate">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc[:300])}">
<link rel="canonical" href="{DOMAIN}{alt[l]}">
{links}
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc[:300])}"><meta property="og:type" content="website"><meta property="og:locale" content="{OG[l]}"><meta property="og:image" content="{DOMAIN}/img/og-{l}.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:url" content="{DOMAIN}{alt[l]}"><meta property="og:site_name" content="WorldWinePedia"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/css/style.css?v={ASSET_V['css']}">
</head>
<body>
<div class="top"><span>{s('topbar', l)}</span><span>{s('topbar2', l)}</span></div>
<header>
<div class="brand">
<a href="{url(l)}" class="logo" aria-label="WorldWinePedia"><img class="mark" src="/img/logo.svg" alt="" width="48" height="48">World<b>Wine</b>pedia</a>
<div class="util"><span class="langs">{langs}</span></div>
</div>
<div class="tag">{s('tagline', l)}</div>
<nav aria-label="Menu">{nav}</nav>
<form class="hsearch" role="search" action="{url(l, 'search')}"><input type="search" name="q" aria-label="{s('search_btn', l)}" placeholder="{s('search_ph', l)}"><button>{s('search_btn', l)}</button></form>
</header>
{body}
<footer>
<div class="footergrid">
<div><div class="logo" style="color:white">World<b style="color:#d9a5b8">Wine</b>pedia</div><p style="font-size:13px">{s('footer_about', l)}</p><p class="langs" style="font-size:12px">{langs}</p></div>
<div><h4>{s('f_explore', l)}</h4>{foot_explore}</div>
<div><h4>{s('f_learn', l)}</h4>{foot_learn}</div>
<div><h4>{s('f_project', l)}</h4>{foot_proj}</div>
</div>
<p class="webs-hermanas">{sister_sites(l)}</p>
<div class="disclaimer">{s('moderation', l)} · {s('aff_short', l)} {s('amazon_note', l)} · © WorldWinePedia</div>
</footer>
<div id="agegate" role="dialog" aria-modal="true" aria-labelledby="ageq"><div class="in">
<div class="logo">World<b>Wine</b>pedia</div>
<h2 id="ageq">{s('age_q', l)}</h2><p>{s('age_p', l)}</p>
<button type="button" class="yes">{s('age_yes', l)}</button><button type="button" class="no">{s('age_no', l)}</button>
<div class="ln">{agelinks}</div></div></div>
<script>window.WWP={{lang:"{l}",base:"{l}/",t:{t_js},stores:{stores_js}}};</script>
<script src="/js/site.js?v={ASSET_V['js']}" defer></script>
</body>
</html>'''

def alts(kind=None, slug=None): return {x: url(x, kind, slug) for x in LANGS}

def crumbs(l, items):
    parts = ['<a href="%s">%s</a>' % (url(l), s('home', l))]
    for name, u in items:
        parts.append('<a href="%s">%s</a>' % (u, e(name)) if u else e(name))
    return '<div class="crumbs">' + ' › '.join(parts) + '</div>'

BOTTLE = {'tinto': 'redb', 'blanco': 'whiteb', 'rosado': 'roseb', 'espumoso': 'sparkb', 'dulce': 'sweetb', 'generoso': 'sweetb'}

def wine_card(l, w, photo=True):
    reg = R.get(w.get('region'), {})
    win = B.get(w.get('winery'), {})
    label = re.split(r'[ \-/]', T(reg.get('name'), l) or '')[0][:11]
    txt = (w['name'] + ' ' + win.get('name', '') + ' ' + T(reg.get('name'), l) + ' ' + ' '.join(T(G[g]['name'], l) for g in w.get('grapes', []) if g in G)).lower()
    grapes = ', '.join(T(G[g]['name'], l) for g in w.get('grapes', []) if g in G)
    wm = WM.get('wines', {}).get(w['slug']) if photo else None
    bottle_img = f'<img class="realbottle" src="{wm["src"]}" alt="{e(wm.get("alt", ""))}" loading="lazy">' if wm else f'<div class="bottle {BOTTLE.get(w.get("type"), "")}" data-label="{e(label)}"></div>'
    return f'''<article class="wine" data-item data-type="{w.get('type','')}" data-region="{w.get('region','')}" data-text="{e(txt)}">
<div class="bottlearea"><span class="label">{e(T(S['type1'].get(w.get('type'), {}), l)).upper()}</span>{bottle_img}</div>
<p class="meta">{e(win.get('name',''))} · {e(T(reg.get('name'), l))}</p>
<h3>{e(w['name'])}</h3>
<p class="meta">{e(grapes)}</p>
<a class="btn" href="{url(l, 'wines', w['slug'])}">{s('see_buy', l)} ↗</a>
</article>'''

def type_pills(l, types):
    p = '<button type="button" class="pill active" data-type="all" aria-pressed="true">%s</button>' % s('all', l)
    for t in ('tinto', 'blanco', 'rosado', 'espumoso', 'dulce', 'generoso'):
        if t in types: p += '<button type="button" class="pill" data-type="%s" aria-pressed="false">%s</button>' % (t, T(S['types'][t], l))
    return '<div class="pills">' + p + '</div>'

def linklist(items):
    return '<div class="linklist">' + ''.join('<a href="%s">%s</a>' % (u, e(n)) for n, u in items) + '</div>'

# ---------------- HOME ----------------

CONT_ORDER = ['europa', 'america', 'oceania', 'africa', 'asia']
HOME_COUNTRIES = ['espana', 'francia', 'italia', 'portugal', 'alemania', 'austria', 'estados-unidos', 'argentina', 'chile', 'australia', 'nueva-zelanda', 'sudafrica']
SOON = [("japon", "asia", "JP", {"es": "Japón", "en": "Japan", "fr": "Japon", "it": "Giappone"}, "Yamanashi · Koshu"),
        ("india", "asia", "IN", {"es": "India", "en": "India", "fr": "Inde", "it": "India"}, "Nashik · Karnataka")]
def country_card(l, c):
    regs = ' · '.join(T(R[r]['name'], l) for r in c.get('regions', [])[:5] if r in R)
    return f'<a class="country" data-code="{e(c.get("code", ""))}" href="{url(l, "countries", c["slug"])}"><small>{T(S["continents"][c["continent"]], l).upper()}</small><h3>{e(T(c["name"], l))}</h3><p>{regs}</p></a>'
def all_country_cards(l):
    cs = sorted(C.values(), key=lambda c: (CONT_ORDER.index(c.get('continent', 'asia')) if c.get('continent') in CONT_ORDER else 9, -len(c.get('regions', [])), T(c['name'], l)))
    out = ''.join(country_card(l, c) for c in cs)
    for slug, cont, code, name, regs in SOON:
        if slug not in C:
            out += f'<a class="country" data-code="{code}" href="#"><small>{T(S["continents"][cont], l).upper()} · <em>{s("soon", l)}</em></small><h3>{T(name, l)}</h3><p>{regs}</p></a>'
    return out

def home(l):
    cards = ''
    for i, (k, key) in enumerate([('wines', 'card_wines'), ('countries', 'card_atlas'), ('grapes', 'card_grapes'), ('wineries', 'card_wineries')]):
        h, p = S[key][l]
        cards += f'<div class="card"><span class="num">0{i+1}</span><h3>{h}</h3><p>{p}</p><a class="textlink" href="{url(l, k)}">{s("explore", l)} →</a></div>'
    atlas = ''.join(country_card(l, C[x]) for x in HOME_COUNTRIES if x in C)
    sci = ''.join(f'<a class="topic" href="{url(l, "articles", a["slug"])}"><i>↗</i><strong>{e(T(a["title"], l))}</strong><span>{e(T(a["summary"], l))[:140]}</span></a>' for a in A.values() if a.get('section') == 'ciencia')
    viti = ''.join(f'<li><a href="{url(l, "articles", a["slug"])}">{e(T(a["title"], l))}</a></li>' for a in A.values() if a.get('section') == 'viticultura')
    gp = ''.join(f'<a class="pill" href="{url(l, "grapes", g)}">{e(T(G[g]["name"], l))} ↗</a>' for g in ['tempranillo', 'garnacha', 'albarino', 'verdejo', 'mencia', 'monastrell', 'cabernet-sauvignon', 'pinot-noir', 'chardonnay', 'riesling', 'sangiovese', 'nebbiolo'] if g in G)
    # wines: diverse selection
    pick, seen = [], set()
    for w in V.values():
        if w.get('type') not in seen: pick.append(w); seen.add(w.get('type'))
    for w in V.values():
        if len(pick) >= 8: break
        if w not in pick: pick.append(w)
    wines = ''.join(wine_card(l, w, photo=False) for w in pick[:8])
    winer = ''.join(f'<a class="card" href="{url(l, "wineries", b["slug"])}"><h3>{e(b["name"])}</h3><p>{e(T(R.get(b.get("region"), {}).get("name"), l))}</p></a>' for b in list(B.values())[:4])
    cult = ''
    for sec in ('cata', 'maridaje', 'historia'):
        arts = [a for a in A.values() if a.get('section') == sec][:3]
        cult += f'<div class="article"><span class="eyebrow">{T(S["sections"][sec], l)}</span>' + ''.join(f'<h3><a href="{url(l, "articles", a["slug"])}">{e(T(a["title"], l))}</a></h3><p>{e(T(a["summary"], l))}</p>' for a in arts[:2]) + '</div>'
    r = [S[k][l] for k in ('rib1', 'rib2', 'rib3', 'rib4')]
    body = f'''<main>
<div class="hero"><div><span class="eyebrow">{s('hero_eyebrow', l)}</span><h1>{s('hero_h1', l)}</h1><p>{s('hero_p', l)}</p>
<form class="search" role="search" action="{url(l, 'search')}"><input name="q" aria-label="{s('search_btn', l)}" placeholder="{s('search_ph', l)}"><button>{s('search_btn', l)} ↗</button></form>
<div class="quick"><a href="{url(l, 'regions', 'rioja')}">Rioja</a><a href="{url(l, 'regions', 'ribera-del-duero')}">Ribera del Duero</a><a href="{url(l, 'grapes', 'albarino')}">Albariño</a><a href="{url(l, 'regions', 'jerez-xeres-sherry')}">Jerez</a><a href="{url(l, 'articles')}">{T(S['sections']['guias'], l)}</a></div></div></div>
<div class="ribbon">{''.join(f'<div><strong>{a}</strong><span>{b}</span></div>' for a, b in r)}</div>
<section><div class="sectionhead"><div><span class="eyebrow">{s('s1_eyebrow', l)}</span><h2>{s('s1_h2', l)}</h2><p class="sub">{s('s1_sub', l)}</p></div></div><div class="grid four">{cards}</div></section>
<section style="background:#f0f1e9"><div class="sectionhead"><div><span class="eyebrow">{s('s2_eyebrow', l)}</span><h2>{s('s2_h2', l)}</h2><p class="sub">{s('s2_sub', l)}</p></div><a class="textlink" href="{url(l, 'countries')}">{s('explore', l)} ↗</a></div><div class="grid three">{atlas}</div></section>
<section class="dark"><div class="science"><div><span class="eyebrow">{s('s3_eyebrow', l)}</span><h2>{s('s3_h2', l)}</h2><p class="sub">{s('s3_sub', l)}</p><a class="textlink" href="{url(l, 'articles')}#ciencia">{s('explore', l)} →</a></div><div>{sci}</div></div></section>
<section><span class="eyebrow">{s('s4_eyebrow', l)}</span><h2>{s('s4_h2', l)}</h2><div class="grid two" style="margin-top:24px"><div class="feature"><h3>{T(S['sections']['viticultura'], l)}</h3><ul>{viti}</ul></div><div><span class="eyebrow">{s('nav_grapes', l)}</span><h3>{s('s4_grapes_h', l)}</h3><p class="sub">{s('grapes_intro', l)}</p><div class="pills">{gp}</div><a class="textlink" href="{url(l, 'grapes')}">{s('explore', l)} →</a></div></div></section>
<section style="border-top:1px solid var(--line)"><div class="grid two"><div><span class="eyebrow">{s('s5_eyebrow', l)}</span><h2>{s('s5_h2', l)}</h2><p class="sub">{s('wineries_intro', l)}</p><a class="btn" href="{url(l, 'wineries')}">{s('explore', l)} ↗</a></div><div class="grid two">{winer}</div></div></section>
<section class="burgundy" data-filter-scope><div class="sectionhead"><div><span class="eyebrow">{s('s6_eyebrow', l)}</span><h2>{s('s6_h2', l)}</h2><p class="sub">{s('s6_sub', l)}</p></div><a class="textlink" href="{url(l, 'wines')}">{s('all_wines', l)} ↗</a></div>{type_pills(l, set(w.get('type') for w in pick))}<div class="grid four">{wines}</div><p class="sub" style="font-size:12px;margin-top:20px">{s('aff_short', l)} {s('amazon_note', l)}</p></section>
<section><span class="eyebrow">{s('s7_eyebrow', l)}</span><h2>{s('s7_h2', l)}</h2><div class="grid three" style="margin-top:24px">{cult}</div></section>
</main>'''
    return layout(l, 'WorldWinePedia · ' + s('tagline', l), strip(s('hero_p', l)), body, alts())

# ---------------- LISTS ----------------
def page_wrap(l, h1, intro, inner, cr):
    return f'<main class="page">{crumbs(l, cr)}<h1 style="font:clamp(34px,4vw,50px)/1.1 Georgia,serif;margin:6px 0">{h1}</h1><p class="lead">{intro}</p>{inner}</main>'

def wines_list(l):
    regs = sorted({w.get('region') for w in V.values() if w.get('region') in R}, key=lambda r: T(R[r]['name'], l))
    opts = '<option value="">%s</option>' % s('filter_region', l) + ''.join('<option value="%s">%s</option>' % (r, e(T(R[r]['name'], l))) for r in regs)
    cards = ''.join(wine_card(l, w) for w in sorted(V.values(), key=lambda w: w['name']))
    inner = f'<div data-filter-scope><div class="filters"><input class="ftext" type="search" placeholder="{s("search_ph", l)}" aria-label="{s("search_btn", l)}"><select class="freg" aria-label="{s("region", l)}">{opts}</select><span><b class="fcount"></b> {s("results", l)}</span></div>{type_pills(l, set(w.get("type") for w in V.values()))}<div class="listgrid">{cards}</div></div>'
    return layout(l, s('all_wines', l) + ' · WorldWinePedia', s('wines_intro', l), page_wrap(l, s('all_wines', l), s('wines_intro', l), inner, [(s('nav_wines', l), None)]), alts('wines'), 'wines')

def simple_cards(items):
    return '<div class="listgrid">' + ''.join(f'<a class="card" href="{u}" data-item data-type="" data-region="" data-text="{e(t.lower())}"><h3>{e(t)}</h3><p>{e(p)}</p></a>' for t, p, u in items) + '</div>'

def grapes_list(l):
    out = ''
    for col, key in (('tinta', 'color_tinta'), ('blanca', 'color_blanca')):
        items = sorted([(T(g['name'], l), T(g.get('summary'), l), url(l, 'grapes', g['slug'])) for g in G.values() if g.get('color') == col])
        out += f'<h2>{s(key, l)}</h2>' + simple_cards(items)
    return layout(l, s('nav_grapes', l) + ' · WorldWinePedia', s('grapes_intro', l), page_wrap(l, s('nav_grapes', l), s('grapes_intro', l), out, [(s('nav_grapes', l), None)]), alts('grapes'), 'grapes')

def wineries_list(l):
    items = sorted([(b['name'], T(R.get(b.get('region'), {}).get('name'), l) + ' · ' + T(b.get('summary'), l), url(l, 'wineries', b['slug'])) for b in B.values()])
    inner = f'<div data-filter-scope><div class="filters"><input class="ftext" type="search" placeholder="{s("search_ph", l)}" aria-label="{s("search_btn", l)}"></div>{simple_cards(items)}</div>'
    return layout(l, s('nav_wineries', l) + ' · WorldWinePedia', s('wineries_intro', l), page_wrap(l, s('nav_wineries', l), s('wineries_intro', l), inner, [(s('nav_wineries', l), None)]), alts('wineries'), 'wineries')

def countries_list(l):
    atlas = all_country_cards(l)
    inner = f'<div class="grid three" style="margin-top:24px">{atlas}</div>'
    return layout(l, s('nav_atlas', l) + ' · WorldWinePedia', s('atlas_intro', l), page_wrap(l, s('nav_atlas', l), s('atlas_intro', l), inner, [(s('nav_atlas', l), None)]), alts('countries'), 'countries')

def regions_list(l):
    items = sorted([(T(r['name'], l), T(r.get('kind'), l) + ' · ' + T(r.get('summary'), l), url(l, 'regions', r['slug'])) for r in R.values()])
    return layout(l, s('regions_of', l) + ' · WorldWinePedia', s('atlas_intro', l), page_wrap(l, s('regions_of', l), s('atlas_intro', l), simple_cards(items), [(s('nav_atlas', l), url(l, 'countries')), (s('regions_of', l), None)]), alts('regions'), 'countries')

def articles_list(l):
    out = ''
    for sec in ('ciencia', 'viticultura', 'cata', 'maridaje', 'historia', 'guias'):
        arts = [a for a in A.values() if a.get('section') == sec]
        if not arts: continue
        out += f'<h2 id="{sec}">{T(S["sections"][sec], l)}</h2>' + simple_cards([(T(a['title'], l), T(a.get('summary'), l), url(l, 'articles', a['slug'])) for a in arts])
    return layout(l, s('nav_learn', l) + ' · WorldWinePedia', s('learn_intro', l), page_wrap(l, s('nav_learn', l), s('learn_intro', l), out, [(s('nav_learn', l), None)]), alts('articles'), 'articles')

def glossary(l):
    items = sorted(GL, key=lambda g: strip(T(g['term'], l)).lower().lstrip('¿"\''))
    import unicodedata
    def first(t):
        c = unicodedata.normalize('NFD', t.strip()[:1].upper())[:1]
        return c if c.isalpha() else '#'
    letters, out, cur = [], '', None
    for g in items:
        f = first(T(g['term'], l))
        if f != cur:
            cur = f; letters.append(f); out += f'<h2 id="l-{f}">{f}</h2>'
        out += f'<div class="gl" id="{e(g["slug"])}" data-item data-type="" data-region="" data-text="{e((T(g["term"], l) + " " + T(g["definition"], l)).lower())}"><strong>{e(T(g["term"], l))}</strong><p>{e(T(g["definition"], l))}</p></div>'
    nav = '<div class="letters">' + ''.join(f'<a href="#l-{x}">{x}</a>' for x in letters) + '</div>'
    inner = f'<div data-filter-scope><div class="filters"><input class="ftext" type="search" placeholder="{s("search_btn", l)}…" aria-label="{s("search_btn", l)}"><span><b class="fcount"></b> {s("results", l)}</span></div>{nav}{out}</div>'
    return layout(l, s('nav_glossary', l) + ' · WorldWinePedia', s('glossary_intro', l), page_wrap(l, s('nav_glossary', l), s('glossary_intro', l), inner, [(s('nav_glossary', l), None)]), alts('glossary'), 'glossary')

def search_page(l):
    inner = f'<form class="filters" onsubmit="return false"><input id="sq" type="search" autofocus placeholder="{s("search_ph", l)}" aria-label="{s("search_btn", l)}"></form><div id="searchres" class="searchres"></div>'
    return layout(l, s('search_btn', l) + ' · WorldWinePedia', s('search_ph', l), page_wrap(l, s('search_btn', l), '', inner, [(s('search_btn', l), None)]), alts('search'))

# ---------------- DETAIL ----------------
def facts(rows):
    return '<div class="facts"><dl>' + ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows if v) + '</dl></div>'

def a_(u, t): return f'<a href="{u}">{e(t)}</a>'

def grape_links(l, gs): return ', '.join(a_(url(l, 'grapes', g), T(G[g]['name'], l)) for g in gs if g in G)

def wine_page(l, w):
    reg = R.get(w.get('region'), {}); win = B.get(w.get('winery'), {}); co = C.get(w.get('country') or reg.get('country'), {})
    ship_opts = ''.join('<option value="%s">%s</option>' % (c, T(n, l)) for c, n in SHIP)
    side = f'''<aside><div class="buybox"><h2>{s('where_buy', l)}</h2><label style="font-size:13px">{s('shops_to', l)}:<select class="ship">{ship_opts}</select></label><div class="shops" data-q="{e(w.get('search') or w['name'])}"></div><small>{s('price_note', l)}<br>{s('aff_short', l)} {s('amazon_note', l)}</small></div>
{facts([(s('winery', l), a_(url(l, 'wineries', win['slug']), win['name']) if win else ''), (s('region', l), a_(url(l, 'regions', reg['slug']), T(reg['name'], l)) if reg else ''), (s('country', l), a_(url(l, 'countries', co['slug']), T(co['name'], l)) if co else ''), (s('type', l), T(S['type1'].get(w.get('type'), {}), l)), (s('category', l), e(T(w.get('category'), l))), (s('grapes', l), grape_links(l, w.get('grapes', []))), (s('serve', l), e(T(w.get('serve'), l)))])}</aside>'''
    more = [x for x in V.values() if x['slug'] != w['slug'] and (x.get('winery') == w.get('winery') or x.get('region') == w.get('region'))][:8]
    morehtml = f'<div class="box"><h3>{s("related", l)}</h3>{linklist([(x["name"], url(l, "wines", x["slug"])) for x in more])}</div>' if more else ''
    main = f'''<div>{crumbs(l, [(T(co.get('name'), l), url(l, 'countries', co['slug']) if co else None), (T(reg.get('name'), l), url(l, 'regions', reg['slug']) if reg else None), (w['name'], None)])}
<span class="eyebrow">{e(win.get('name', ''))}</span><h1>{e(w['name'])}</h1>
<div class="tags"><span class="tag2 t">{T(S['type1'].get(w.get('type'), {}), l)}</span>{'<span class="tag2">%s</span>' % e(T(w.get('category'), l)) if w.get('category') else ''}<span class="tag2">{e(T(reg.get('kind'), l))} {e(T(reg.get('name'), l))}</span></div>
<p class="lead">{e(T(w.get('summary'), l))}</p>
{photo(WM.get('wines', {}).get(w['slug']), l, cls='bottle-photo')}
<div class="prose">{T(w.get('body'), l)}</div>
<div class="grid three" style="margin-top:24px"><div class="box"><h3>{s('tasting', l)}</h3><p>{e(T(w.get('tasting'), l))}</p></div><div class="box"><h3>{s('pairing', l)}</h3><p>{e(T(w.get('pairing'), l))}</p></div><div class="box"><h3>{s('serve', l)}</h3><p>{e(T(w.get('serve'), l))}</p></div></div>
{morehtml}</div>'''
    ld = {"@context": "https://schema.org", "@type": "Product", "name": w['name'], "brand": win.get('name'), "category": "Wine", "description": strip(T(w.get('summary'), l))}
    body = f'<main class="page"><div class="detail">{main}{side}</div><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></main>'
    return layout(l, f"{w['name']} · {win.get('name', '')} · WorldWinePedia", strip(T(w.get('summary'), l)), body, alts('wines', w['slug']), 'wines')

def winery_page(l, b):
    reg = R.get(b.get('region'), {}); co = C.get(b.get('country') or reg.get('country'), {})
    wines = [w for w in V.values() if w.get('winery') == b['slug']]
    site = f'<a href="{e(b["website"])}" rel="nofollow noopener" target="_blank">{e(re.sub("^https?://(www.)?", "", b["website"]).strip("/"))}</a>' if b.get('website') else ''
    side = '<aside>' + facts([(s('region', l), a_(url(l, 'regions', reg['slug']), T(reg['name'], l)) if reg else ''), (s('country', l), a_(url(l, 'countries', co['slug']), T(co['name'], l)) if co else ''), (s('town', l), e(b.get('town') or '')), (s('founded', l), str(b['founded']) if b.get('founded') else ''), (s('website', l), site)]) + cul_box(l, 'wineries', b['slug'], b["name"]) + '</aside>'
    visits = f'<div class="box"><h3>{s("visits", l)}</h3><p>{e(T(b.get("visits"), l))}</p></div>' if b.get('visits') else ''
    wl = f'<h2 style="margin-top:36px">{s("wines_of", l)}</h2><div class="listgrid" data-filter-scope>' + ''.join(wine_card(l, w) for w in wines) + '</div>' if wines else ''
    main = f'<div>{crumbs(l, [(T(co.get("name"), l), url(l, "countries", co["slug"]) if co else None), (T(reg.get("name"), l), url(l, "regions", reg["slug"]) if reg else None), (b["name"], None)])}<span class="eyebrow">{s("winery", l)}</span><h1>{e(b["name"])}</h1><p class="lead">{e(T(b.get("summary"), l))}</p>{photo(WM.get("wineries", {}).get(b["slug"]) or pick(IMG.get("wineries_pool", []), b["slug"]), l)}<div class="prose">{T(b.get("body"), l)}</div>{visits}</div>'
    body = f'<main class="page"><div class="detail">{main}{side}</div>{wl}</main>'
    return layout(l, f"{b['name']} · WorldWinePedia", strip(T(b.get('summary'), l)), body, alts('wineries', b['slug']), 'wineries')

def region_page(l, r):
    co = C.get(r.get('country'), {})
    wines = [w for w in V.values() if w.get('region') == r['slug']]
    wins = [b for b in B.values() if b.get('region') == r['slug']]
    side = '<aside>' + facts([(s('country', l), a_(url(l, 'countries', co['slug']), T(co['name'], l)) if co else ''), ('', ''), (s('climate', l), e(T(r.get('climate'), l))), (s('soils', l), e(T(r.get('soils'), l))), (s('styles', l), e(T(r.get('styles'), l))), (s('grapes', l), grape_links(l, r.get('grapes', [])))]) + (f'<div class="box"><h3>{s("wineries_of", l)}</h3>{linklist([(b["name"], url(l, "wineries", b["slug"])) for b in wins])}</div>' if wins else '') + cul_box(l, 'regions', r['slug'], T(r["name"], l)) + '</aside>'
    main = f'<div>{crumbs(l, [(T(co.get("name"), l), url(l, "countries", co["slug"]) if co else None), (T(r["name"], l), None)])}<span class="eyebrow">{e(T(r.get("kind"), l))}</span><h1>{e(T(r["name"], l))}</h1><p class="lead">{e(T(r.get("summary"), l))}</p>{photo(WM.get("regions", {}).get(r["slug"]) or IMG.get("regions", {}).get(r["slug"]), l)}<div class="prose">{T(r.get("body"), l)}</div></div>'
    wl = f'<section data-filter-scope style="margin-top:40px"><h2>{s("wines_of", l)} · {e(T(r["name"], l))}</h2>{type_pills(l, set(w.get("type") for w in wines))}<div class="listgrid">' + ''.join(wine_card(l, w) for w in wines) + '</div></section>' if wines else ''
    body = f'<main class="page"><div class="detail">{main}{side}</div>{wl}</main>'
    return layout(l, f"{T(r['name'], l)} · {T(r.get('kind'), l)} · WorldWinePedia", strip(T(r.get('summary'), l)), body, alts('regions', r['slug']), 'countries')

def country_page(l, c):
    regs = [R[x] for x in c.get('regions', []) if x in R]
    regcards = simple_cards([(T(r['name'], l), T(r.get('kind'), l) + ' · ' + T(r.get('summary'), l), url(l, 'regions', r['slug'])) for r in regs])
    wins = [b for b in B.values() if (b.get('country') or R.get(b.get('region'), {}).get('country')) == c['slug']]
    side = '<aside>' + facts([(s('key_grapes', l), grape_links(l, c.get('key_grapes', [])))]) + (f'<div class="box"><h3>{s("wineries_of", l)}</h3>{linklist([(b["name"], url(l, "wineries", b["slug"])) for b in sorted(wins, key=lambda b: b["name"])])}</div>' if wins else '') + '</aside>'
    main = f'<div>{crumbs(l, [(s("nav_atlas", l), url(l, "countries")), (T(c["name"], l), None)])}<span class="eyebrow">{T(S["continents"].get(c.get("continent"), {}), l)}</span><h1>{e(T(c["name"], l))}</h1><p class="lead">{e(T(c.get("summary"), l))}</p>{photo(WM.get("countries", {}).get(c["slug"]) or IMG.get("countries", {}).get(c["slug"]), l)}<div class="prose">{T(c.get("body"), l)}</div></div>'
    body = f'<main class="page"><div class="detail">{main}{side}</div><h2 style="margin-top:40px">{s("regions_of", l)}</h2>{regcards}</main>'
    return layout(l, f"{T(c['name'], l)} · WorldWinePedia", strip(T(c.get('summary'), l)), body, alts('countries', c['slug']), 'countries')

def grape_page(l, g):
    regs = [r for r in R.values() if g['slug'] in r.get('grapes', [])]
    wines = [w for w in V.values() if g['slug'] in w.get('grapes', [])]
    side = '<aside>' + facts([(s('origin', l), e(T(g.get('origin'), l))), (s('synonyms', l), e(', '.join(g.get('synonyms') or []))), (s('aromas', l), e(T(g.get('aromas'), l))), (s('type', l), s('color_' + g.get('color', 'tinta'), l))]) + (f'<div class="box"><h3>{s("where_grown", l)}</h3>{linklist([(T(r["name"], l), url(l, "regions", r["slug"])) for r in regs])}</div>' if regs else '') + cul_box(l, 'grapes', g['slug'], T(g["name"], l)) + '</aside>'
    main = f'<div>{crumbs(l, [(s("nav_grapes", l), url(l, "grapes")), (T(g["name"], l), None)])}<span class="eyebrow">{s("color_" + g.get("color", "tinta"), l)}</span><h1>{e(T(g["name"], l))}</h1><p class="lead">{e(T(g.get("summary"), l))}</p>{photo(pick(IMG.get("grapes_" + g.get("color", "tinta"), []), g["slug"]), l)}<div class="prose">{T(g.get("body"), l)}</div></div>'
    wl = f'<section data-filter-scope style="margin-top:40px"><h2>{s("wines_with", l)}</h2><div class="listgrid">' + ''.join(wine_card(l, w) for w in wines) + '</div></section>' if wines else ''
    body = f'<main class="page"><div class="detail">{main}{side}</div>{wl}</main>'
    return layout(l, f"{T(g['name'], l)} · WorldWinePedia", strip(T(g.get('summary'), l)), body, alts('grapes', g['slug']), 'grapes')

def article_page(l, a):
    sec = a.get('section', 'guias')
    rel = [x for x in A.values() if x.get('section') == sec and x['slug'] != a['slug']]
    side = '<aside>' + f'<div class="box" style="margin-top:0"><h3>{T(S["sections"][sec], l)}</h3>{linklist([(T(x["title"], l), url(l, "articles", x["slug"])) for x in rel])}</div>'
    rg = [g for g in a.get('related_grapes', []) if g in G]; rr = [r for r in a.get('related_regions', []) if r in R]
    if rg or rr: side += f'<div class="box"><h3>{s("related", l)}</h3>{linklist([(T(G[g]["name"], l), url(l, "grapes", g)) for g in rg] + [(T(R[r]["name"], l), url(l, "regions", r)) for r in rr])}</div>'
    side += '</aside>'
    main = f'<div>{crumbs(l, [(s("nav_learn", l), url(l, "articles")), (T(S["sections"][sec], l), url(l, "articles") + "#" + sec), (T(a["title"], l), None)])}<span class="eyebrow">{T(S["sections"][sec], l)}</span><h1>{e(T(a["title"], l))}</h1><p class="lead">{e(T(a.get("summary"), l))}</p><div class="prose">{T(a.get("body"), l)}</div></div>'
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": strip(T(a['title'], l)), "inLanguage": l, "publisher": {"@type": "Organization", "name": "WorldWinePedia"}}
    body = f'<main class="page"><div class="detail">{main}{side}</div><script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></main>'
    return layout(l, f"{T(a['title'], l)} · WorldWinePedia", strip(T(a.get('summary'), l)), body, alts('articles', a['slug']), 'articles')

def static_page(l, key):
    p = STATIC_PAGES[key]
    body = page_wrap(l, s(key + '_t', l), '', f'<div class="prose">{T(p, l)}</div>', [(s(key + '_t', l), None)])
    return layout(l, s(key + '_t', l) + ' · WorldWinePedia', strip(T(p, l))[:200], body, alts(key))

def search_index(l):
    idx = []
    for w in V.values(): idx.append({'t': w['name'], 'c': s('nav_wines', l) + ' · ' + B.get(w.get('winery'), {}).get('name', ''), 'u': url(l, 'wines', w['slug']), 'k': T(R.get(w.get('region'), {}).get('name'), l) + ' ' + ' '.join(T(G[g]['name'], l) for g in w.get('grapes', []) if g in G)})
    for b in B.values(): idx.append({'t': b['name'], 'c': s('nav_wineries', l), 'u': url(l, 'wineries', b['slug']), 'k': T(R.get(b.get('region'), {}).get('name'), l)})
    for r in R.values(): idx.append({'t': T(r['name'], l), 'c': T(r.get('kind'), l), 'u': url(l, 'regions', r['slug']), 'k': ''})
    for c in C.values(): idx.append({'t': T(c['name'], l), 'c': s('country', l), 'u': url(l, 'countries', c['slug']), 'k': ''})
    for g in G.values(): idx.append({'t': T(g['name'], l), 'c': s('nav_grapes', l), 'u': url(l, 'grapes', g['slug']), 'k': ' '.join(g.get('synonyms') or [])})
    for a in A.values(): idx.append({'t': T(a['title'], l), 'c': T(S['sections'].get(a.get('section'), {}), l), 'u': url(l, 'articles', a['slug']), 'k': ''})
    for g in GL: idx.append({'t': T(g['term'], l), 'c': s('nav_glossary', l), 'u': url(l, 'glossary') + '#' + g['slug'], 'k': ''})
    return json.dumps(idx, ensure_ascii=False, separators=(',', ':'))

def root_index():
    links = ''.join(f'<a href="/{x}/" hreflang="{x}" lang="{x}">{LANG_NAMES[x]}</a>' for x in LANGS)
    return f'''<!doctype html><html lang="en" translate="no"><head><meta charset="utf-8"><meta name="google" content="notranslate"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WorldWinePedia · The world wine encyclopedia</title>
{''.join(f'<link rel="alternate" hreflang="{x}" href="{DOMAIN}/{x}/">' for x in LANGS)}<link rel="alternate" hreflang="x-default" href="{DOMAIN}/">
<meta name="description" content="The world wine encyclopedia: wines, grapes, regions and wineries in four languages."><meta property="og:title" content="WorldWinePedia · The world wine encyclopedia"><meta property="og:description" content="The world wine encyclopedia: wines, grapes, regions and wineries in four languages."><meta property="og:type" content="website"><meta property="og:image" content="{DOMAIN}/img/og-en.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:url" content="{DOMAIN}/"><meta property="og:site_name" content="WorldWinePedia"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/css/style.css?v={ASSET_V['css']}"><script>(function(){{var l=(navigator.language||'en').slice(0,2);if(['es','en','fr','it'].indexOf(l)<0)l='en';var s=null;try{{s=localStorage.getItem('wwp-lang')}}catch(e){{}};location.replace((s||l)+'/'+(window.PV?'index.html':''));}})();</script></head>
<body style="display:flex;align-items:center;justify-content:center;min-height:100vh"><div style="text-align:center"><div class="logo">World<b>Wine</b>pedia</div><p class="langs" style="display:flex;gap:16px;justify-content:center">{links}</p></div></body></html>'''

exec(open(os.path.join(ROOT, 'tools', 'herramientas.py'), encoding='utf-8').read())
S['nav_tools'] = TX['tools']

def build():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    shutil.copytree(os.path.join(ROOT, 'static'), DIST)
    n = 0
    for l in LANGS:
        pages = [(url(l), home(l)), (url(l, 'wines'), wines_list(l)), (url(l, 'grapes'), grapes_list(l)), (url(l, 'wineries'), wineries_list(l)), (url(l, 'countries'), countries_list(l)), (url(l, 'regions'), regions_list(l)), (url(l, 'articles'), articles_list(l)), (url(l, 'glossary'), glossary(l)), (url(l, 'search'), search_page(l))]
        pages += [(url(l, k), static_page(l, k)) for k in STATIC_PAGES]
        pages += tools_pages(l)
        pages += [(url(l, 'wines', x['slug']), wine_page(l, x)) for x in V.values()]
        pages += [(url(l, 'wineries', x['slug']), winery_page(l, x)) for x in B.values()]
        pages += [(url(l, 'regions', x['slug']), region_page(l, x)) for x in R.values()]
        pages += [(url(l, 'countries', x['slug']), country_page(l, x)) for x in C.values()]
        pages += [(url(l, 'grapes', x['slug']), grape_page(l, x)) for x in G.values()]
        pages += [(url(l, 'articles', x['slug']), article_page(l, x)) for x in A.values()]
        for p, h in pages: write(p, h); n += 1
        write('/%s/search.json' % l, search_index(l))
    write('/', root_index())
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    seen = set()
    for alt in SITEMAP:
        for l in LANGS:
            if alt[l] in seen: continue
            seen.add(alt[l])
            sm += '<url><loc>%s%s</loc>%s</url>\n' % (DOMAIN, alt[l], ''.join('<xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (x, DOMAIN, alt[x]) for x in LANGS))
    sm += '</urlset>\n'
    write('/sitemap.xml', sm)
    write('/robots.txt', 'User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n' % DOMAIN)
    print('pages:', n, '| wines', len(V), 'wineries', len(B), 'regions', len(R), 'countries', len(C), 'grapes', len(G), 'articles', len(A), 'glossary', len(GL))

if __name__ == '__main__':
    if 'preview' in sys.argv:
        PREVIEW = True
        DIST = os.path.join(ROOT, 'preview')
    build()
