"""Fichas nuevas a partir del catálogo de Decantalo (feed de Daisycon).

Uso: python3 tools/decantalo_fichas.py catalogo.json descripciones.json [--max-precio 40] [--min-precio 0]
- catalogo.json: exportación compacta del feed (t, b, pr, l, i, cat...)
- descripciones.json: misma exportación con la descripción de cada vino (ds, alc, g)
Crea data/wines/<slug>.json con "brief": true (ficha breve con datos del catálogo y textos
de plantilla en 4 idiomas) y añade el enlace y la foto a data/decantalo.json.
Solo usa hechos del catálogo: bodega, denominación, tipo, elaboración, uva y grado.
"""
import json, os, re, sys, glob, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decantalo import norm, strip_title
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
L4 = ('es', 'en', 'fr', 'it')
STOPW = {'bodegas', 'bodega', 'celler', 'cellers', 'domaine', 'chateau', 'weingut', 'cantina', 'azienda', 'agricola', 'tenuta', 'quinta', 'herdade', 'vinos', 'vins', 'vinedos', 'y', 'e', 'et', 'de', 'del', 'la', 'le', 'les', 'el', 'family', 'familia', 'wines', 'estate', 'maison', 'champagne', 'casa'}

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

COUNTRY = {'España': 'espana', 'Francia': 'francia', 'Italia': 'italia', 'Portugal': 'portugal', 'Alemania': 'alemania',
           'Sudáfrica': 'sudafrica', 'Austria': 'austria', 'Estados Unidos': 'estados-unidos', 'Argentina': 'argentina',
           'Grecia': 'grecia', 'Australia': 'australia', 'Nueva Zelanda': 'nueva-zelanda', 'Chile': 'chile', 'Hungría': 'hungria',
           'Líbano': 'libano', 'Uruguay': 'uruguay', 'Eslovenia': 'eslovenia', 'Georgia': 'georgia', 'Israel': 'israel',
           'Suiza': 'suiza', 'Croacia': 'croacia', 'Inglaterra': 'inglaterra', 'Reino Unido': 'inglaterra', 'Canadá': 'canada',
           'México': 'mexico', 'Rumanía': 'rumania', 'Bulgaria': 'bulgaria', 'Moldavia': 'moldavia', 'Turquía': 'turquia', 'Brasil': 'brasil', 'China': 'china'}
TYPE = {'tinto': 'tinto', 'blanco': 'blanco', 'rosado': 'rosado', 'generoso': 'generoso', 'dulce': 'dulce', 'espumoso': 'espumoso'}
SPARK_DO = ('cava', 'champagne', 'corpinnat', 'franciacorta', 'cremant', 'prosecco', 'trento', 'clasic penedes', 'asti', 'cap classique', 'sekt', 'conca del riu anoia', 'espumoso')
GRAPE = {'garnacha tinta': 'garnacha', 'garnacha': 'garnacha', 'tinto fino': 'tempranillo', 'tinta de toro': 'tempranillo', 'tinta del pais': 'tempranillo',
         'tempranillo': 'tempranillo', 'cencibel': 'tempranillo', 'mencia': 'mencia', 'xarel lo': 'xarel-lo', 'garnacha blanca': 'garnacha-blanca',
         'carinena': 'carinena', 'samso': 'carinena', 'mazuelo': 'carinena', 'monastrell': 'monastrell', 'bobal': 'bobal', 'albarino': 'albarino',
         'godello': 'godello', 'verdejo': 'verdejo', 'palomino': 'palomino', 'palomino fino': 'palomino', 'pedro ximenez': 'pedro-ximenez',
         'moscatel': 'moscatel', 'moscatel de alejandria': 'moscatel', 'treixadura': 'treixadura', 'macabeo': 'macabeo', 'viura': 'macabeo',
         'parellada': 'parellada', 'graciano': 'graciano', 'listan negro': 'listan-negro', 'listan blanco': 'listan-blanco', 'prieto picudo': 'prieto-picudo',
         'hondarrabi zuri': 'hondarrabi-zuri', 'caino': 'caino', 'loureira': 'loureira', 'brancellao': 'brancellao', 'souson': 'souson', 'merenzao': 'trousseau',
         'trousseau': 'trousseau', 'juan garcia': 'juan-garcia', 'maturana tinta': 'maturana-tinta', 'moristel': 'moristel', 'airen': 'airen', 'malvasia': 'malvasia'}

def gmap(g):
    g = norm(g)
    if g in GRAPE: return GRAPE[g]
    s = g.replace(' ', '-')
    return s if os.path.exists(os.path.join(DATA, 'grapes', s + '.json')) else None

# --- textos de plantilla ---
TYPE_T = {
 'tinto': {'es': 'vino tinto', 'en': 'red wine', 'fr': 'vin rouge', 'it': 'vino rosso'},
 'blanco': {'es': 'vino blanco', 'en': 'white wine', 'fr': 'vin blanc', 'it': 'vino bianco'},
 'rosado': {'es': 'vino rosado', 'en': 'rosé wine', 'fr': 'vin rosé', 'it': 'vino rosato'},
 'espumoso': {'es': 'vino espumoso', 'en': 'sparkling wine', 'fr': 'vin effervescent', 'it': 'vino spumante'},
 'dulce': {'es': 'vino dulce', 'en': 'sweet wine', 'fr': 'vin doux', 'it': 'vino dolce'},
 'generoso': {'es': 'vino generoso', 'en': 'fortified wine', 'fr': 'vin fortifié', 'it': 'vino liquoroso'}}
CAT = {'crianza': {'es': 'Crianza', 'en': 'Crianza', 'fr': 'Crianza', 'it': 'Crianza'},
       'reserva': {'es': 'Reserva', 'en': 'Reserva', 'fr': 'Reserva', 'it': 'Reserva'},
       'gran reserva': {'es': 'Gran Reserva', 'en': 'Gran Reserva', 'fr': 'Gran Reserva', 'it': 'Gran Reserva'},
       'roble': {'es': 'Roble', 'en': 'Roble', 'fr': 'Roble', 'it': 'Roble'},
       'joven': {'es': 'Joven', 'en': 'Joven', 'fr': 'Joven', 'it': 'Joven'}}
MAKE = {
 'envejecido en madera': {'es': 'Tiene crianza en madera.', 'en': 'It is aged in wood.', 'fr': 'Il est élevé en bois.', 'it': 'È affinato in legno.'},
 'sobre lias': {'es': 'Se cría sobre sus lías.', 'en': 'It is aged on its lees.', 'fr': 'Il est élevé sur lies.', 'it': 'Affina sulle fecce fini.'},
 'fermentado en barrica': {'es': 'Fermenta en barrica.', 'en': 'It is fermented in barrel.', 'fr': 'Il est fermenté en barrique.', 'it': 'Fermenta in barrique.'},
 'envejecido en hormigon': {'es': 'Se cría en depósitos de hormigón.', 'en': 'It is aged in concrete vats.', 'fr': 'Il est élevé en cuves béton.', 'it': 'Affina in vasche di cemento.'},
 'envejecido en acero': {'es': 'Se cría en depósitos de acero inoxidable.', 'en': 'It is aged in stainless steel tanks.', 'fr': 'Il est élevé en cuves inox.', 'it': 'Affina in acciaio inox.'},
 'envejecido en arcilla': {'es': 'Se cría en recipientes de barro, como ánforas o tinajas.', 'en': 'It is aged in clay vessels such as amphorae.', 'fr': 'Il est élevé en jarres de terre cuite, comme des amphores.', 'it': 'Affina in contenitori di terracotta, come anfore.'},
 'envejecido bajo velo': {'es': 'Se cría bajo velo de flor.', 'en': 'It is aged under a veil of flor yeast.', 'fr': 'Il est élevé sous voile de levures.', 'it': 'Affina sotto velo di flor.'},
 'maceracion carbonica': {'es': 'Se elabora por maceración carbónica.', 'en': 'It is made by carbonic maceration.', 'fr': 'Il est élaboré par macération carbonique.', 'it': 'È prodotto con macerazione carbonica.'},
 'joven': {'es': 'Es un vino joven, pensado para beber en sus primeros años.', 'en': 'It is a young wine, meant to be drunk in its first years.', 'fr': 'C’est un vin jeune, à boire dans ses premières années.', 'it': 'È un vino giovane, da bere nei primi anni.'}}
CAT_S = {'es': 'Lleva la mención {c}.', 'en': 'It carries the {c} designation.', 'fr': 'Il porte la mention {c}.', 'it': 'Riporta la menzione {c}.'}
PAIR = {
 'tinto': {'es': 'Carnes rojas, asados, guisos, quesos curados', 'en': 'Red meat, roasts, stews, aged cheeses', 'fr': 'Viandes rouges, rôtis, plats mijotés, fromages affinés', 'it': 'Carni rosse, arrosti, stufati, formaggi stagionati'},
 'blanco': {'es': 'Pescados, mariscos, arroces, quesos frescos', 'en': 'Fish, shellfish, rice dishes, fresh cheeses', 'fr': 'Poissons, fruits de mer, plats de riz, fromages frais', 'it': 'Pesce, frutti di mare, risotti, formaggi freschi'},
 'rosado': {'es': 'Aperitivo, ensaladas, arroces, pescados', 'en': 'Aperitif, salads, rice dishes, fish', 'fr': 'Apéritif, salades, plats de riz, poissons', 'it': 'Aperitivo, insalate, risotti, pesce'},
 'espumoso': {'es': 'Aperitivo, mariscos, fritos, pescados', 'en': 'Aperitif, shellfish, fried food, fish', 'fr': 'Apéritif, fruits de mer, fritures, poissons', 'it': 'Aperitivo, frutti di mare, fritture, pesce'},
 'dulce': {'es': 'Postres, foie gras, quesos azules', 'en': 'Desserts, foie gras, blue cheeses', 'fr': 'Desserts, foie gras, fromages à pâte persillée', 'it': 'Dolci, foie gras, formaggi erborinati'},
 'generoso': {'es': 'Aperitivo, jamón, frutos secos, quesos curados', 'en': 'Aperitif, cured ham, nuts, aged cheeses', 'fr': 'Apéritif, jambon sec, fruits secs, fromages affinés', 'it': 'Aperitivo, prosciutto crudo, frutta secca, formaggi stagionati'}}
SERVE = {
 'tinto': {'es': '15-18 °C, copa amplia', 'en': '15-18 °C, large glass', 'fr': '15-18 °C, verre ample', 'it': '15-18 °C, calice ampio'},
 'blanco': {'es': '8-11 °C, copa de vino blanco', 'en': '8-11 °C, white wine glass', 'fr': '8-11 °C, verre à vin blanc', 'it': '8-11 °C, calice da vino bianco'},
 'rosado': {'es': '8-10 °C, copa de vino blanco', 'en': '8-10 °C, white wine glass', 'fr': '8-10 °C, verre à vin blanc', 'it': '8-10 °C, calice da vino bianco'},
 'espumoso': {'es': '6-8 °C, copa de espumoso', 'en': '6-8 °C, sparkling wine glass', 'fr': '6-8 °C, verre à vin effervescent', 'it': '6-8 °C, calice da spumante'},
 'dulce': {'es': '8-12 °C, copa pequeña', 'en': '8-12 °C, small glass', 'fr': '8-12 °C, petit verre', 'it': '8-12 °C, calice piccolo'},
 'generoso': {'es': '7-14 °C según el tipo, catavino', 'en': '7-14 °C depending on style, copita glass', 'fr': '7-14 °C selon le style, verre à xérès', 'it': '7-14 °C secondo lo stile, bicchiere da sherry'}}

def text(n, wname, do, ctry, typ, cat, make, grape, alc, reg, win):
    c = {l: (ctry or {}).get(l, '') for l in L4}
    ty = TYPE_T[typ]
    s1 = {
      'es': f'{n} es un {ty["es"]} de {wname}' + (f', con la denominación {do}' if do else '') + (f', en {c["es"]}' if c['es'] else '') + '.',
      'en': f'{n} is a {ty["en"]} from {wname}' + (f', made under the {do} appellation' if do else '') + (f' in {c["en"]}' if c['en'] else '') + '.',
      'fr': f'{n} est un {ty["fr"]} de {wname}' + (f', élaboré sous l’appellation {do}' if do else '') + (f' ({c["fr"]})' if c['fr'] else '') + '.',
      'it': f'{n} è un {ty["it"]} di {wname}' + (f', prodotto nella denominazione {do}' if do else '') + (f' ({c["it"]})' if c['it'] else '') + '.'}
    gr = {'es': 'Se elabora con {g}.', 'en': 'It is made from {g}.', 'fr': 'Il est élaboré à partir de {g}.', 'it': 'È prodotto con {g}.'}
    al = {'es': 'Su graduación es de {a} % vol.', 'en': 'It has {a}% ABV.', 'fr': 'Il titre {a} % vol.', 'it': 'Ha {a}% vol.'}
    summary, body = {}, {}
    for l in L4:
        parts = []
        if grape: parts.append(gr[l].format(g=grape[l]))
        if cat: parts.append(CAT_S[l].format(c=cat[l]))
        if make: parts.append(make[l])
        if alc: parts.append(al[l].format(a=alc.replace('.', ',') if l != 'en' else alc))
        summary[l] = s1[l]
        b = ('<p>' + ' '.join(parts) + '</p>') if parts else ''
        if win and win.get('summary', {}).get(l): b += '<p>' + win['summary'][l] + '</p>'
        if reg and reg.get('summary', {}).get(l): b += '<p>' + reg['summary'][l] + '</p>'
        body[l] = b
    return summary, body

def main(cat_path, desc_path, pmin, pmax, limit=None):
    P = [p for p in json.load(open(cat_path, encoding='utf-8')) if p.get('cat') == 'Vino' and p.get('i') and p.get('l')]
    DS = {x['t']: x for x in json.load(open(desc_path, encoding='utf-8'))}
    dec = json.load(open(os.path.join(DATA, 'decantalo.json'), encoding='utf-8'))
    W = {os.path.basename(f)[:-5]: json.load(open(f, encoding='utf-8')) for f in glob.glob(os.path.join(DATA, 'wines', '*.json'))}
    have = {strip_title(v['name']) for v in dec.values()} | {strip_title(w['name']) for w in W.values()}
    B = {}
    for f in glob.glob(os.path.join(DATA, 'wineries', '*.json')):
        b = json.load(open(f, encoding='utf-8'))
        for v in (b['name'], b['slug'].replace('-', ' ')):
            B[norm(v)] = b; B[' '.join(t for t in norm(v).split() if t not in STOPW)] = b
    R, RN = {}, {}
    for f in glob.glob(os.path.join(DATA, 'regions', '*.json')):
        r = json.load(open(f, encoding='utf-8')); R[r['slug']] = r
        for v in ([r['slug']] + list(r['name'].values() if isinstance(r['name'], dict) else [r['name']])):
            RN[norm(v).replace(' ', '')] = r['slug']
    C = {}
    for f in glob.glob(os.path.join(DATA, 'countries', '*.json')):
        c = json.load(open(f, encoding='utf-8')); C[c['slug']] = c
    groups = {}
    for p in P:
        if re.search(r'botellas|\+|estuche|pack|caja|regalo|copas', p['t'], re.I): continue
        k = strip_title(p['t'])
        if not k or k in have: continue
        groups.setdefault(k, []).append(p)
    made = 0
    for k, ps in sorted(groups.items()):
        ps.sort(key=lambda p: (bool(re.search(r'magnum|1[,.]5 ?l|150 ?cl|37[,.]5|50 ?cl', p['t'], re.I)), p['st'] != 'true', p['t']))
        p = ps[0]
        price = float(p.get('pr') or 0)
        if not (pmin <= price < pmax): continue
        d = DS.get(p['t'], {})
        m = re.search(r' en (.+?)\. Vino ?(\w*) ?(.*?)\.?$', d.get('ds', ''))
        do = m.group(1).strip() if m else ''
        typ = (m.group(2).lower() if m else '') or ''
        extra = norm(m.group(3)) if m else ''
        if any(x in norm(do) for x in SPARK_DO) or re.search(r'\bbrut\b|nature|cava|champagne|cr[eé]mant', p['t'], re.I): typ = 'espumoso'
        if typ not in TYPE: continue
        name = re.sub(r'\s+((19|20)\d\d|N/?V)\s*$', '', p['t']).strip()
        name = re.sub(r'\s+((19|20)\d\d)\b', '', name).strip()
        slug = slugify(name)
        if not slug or slug in W: slug = slugify(name + ' ' + p['b'])
        if slug in W: continue
        win = B.get(norm(p['b'])) or B.get(' '.join(t for t in norm(p['b']).split() if t not in STOPW))
        dokey = norm(re.sub(r'^(DOCa|DOQ|DOCG|DOC|DOP|DO|AOC|AOP|IGP|IGT|IG|VT|VdlT|Vino de la Tierra de|Vino de la Tierra|Vino de Pago|VP|Vin de|Vinho Regional|DAC|AVA|WO|GI)\s+', '', do, flags=re.I)).replace(' ', '')
        reg = RN.get(dokey)
        country = COUNTRY.get(p.get('c', ''))
        g = d.get('g') or ''
        gs = gmap(g) if g and g != 'Various' else None
        grape_t = None
        if gs and os.path.exists(os.path.join(DATA, 'grapes', gs + '.json')):
            gname = json.load(open(os.path.join(DATA, 'grapes', gs + '.json'), encoding='utf-8'))['name']
            grape_t = gname if isinstance(gname, dict) else {l: gname for l in L4}
        cat = next((CAT[c] for c in ('gran reserva', 'reserva', 'crianza', 'roble') if extra.startswith(c)), None)
        make = next((MAKE[x] for x in MAKE if extra.startswith(x)), None)
        alc = (d.get('alc') or '').strip()
        try: alc = ('%g' % float(alc)) if alc and 5 <= float(alc) <= 25 else ''
        except ValueError: alc = ''
        summary, body = text(name, win['name'] if win else p['b'], do, C.get(country, {}).get('name') if country else None, typ, cat, make, grape_t, alc, R.get(reg), win)
        w = {'slug': slug, 'name': name, 'winery': win['slug'] if win else None, 'winery_name': None if win else p['b'],
             'region': reg, 'country': country or (R[reg]['country'] if reg else None), 'appellation': do or None,
             'type': typ, 'category': cat, 'grapes': [gs] if gs else [], 'summary': summary, 'body': body,
             'tasting': None, 'pairing': PAIR[typ], 'serve': SERVE[typ], 'search': f'{name} {p["b"]}', 'brief': True, 'source': 'decantalo'}
        json.dump(w, open(os.path.join(DATA, 'wines', slug + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        dec[slug] = {'name': p['t'], 'url': p['l'], 'img': p['i']}
        W[slug] = w; made += 1
        if limit and made >= limit: break
    json.dump(dec, open(os.path.join(DATA, 'decantalo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print('fichas nuevas:', made)

if __name__ == '__main__':
    a = sys.argv[1:]
    pmax = float(a[a.index('--max-precio') + 1]) if '--max-precio' in a else 1e9
    pmin = float(a[a.index('--min-precio') + 1]) if '--min-precio' in a else 0
    main(a[0], a[1], pmin, pmax)
