# Herramientas de WorldWinePedia: buscador de maridajes, comparador de uvas y mapa de denominaciones.
# Se ejecuta dentro de build.py (exec), así que usa sus globales: V, G, R, C, T, s, url, e, layout, crumbs, alts, page_wrap, wine_card.

SEG['tools'] = {'es': 'herramientas', 'en': 'tools', 'fr': 'outils', 'it': 'strumenti'}
TOOL_SLUG = {
    'pairing': {'es': 'maridajes', 'en': 'food-pairing', 'fr': 'accords-mets-vins', 'it': 'abbinamenti'},
    'compare': {'es': 'comparador-de-uvas', 'en': 'grape-comparison', 'fr': 'comparateur-de-cepages', 'it': 'confronto-vitigni'},
    'map': {'es': 'mapa', 'en': 'map', 'fr': 'carte', 'it': 'mappa'},
}
TX = {
    'tools': {'es': 'Herramientas', 'en': 'Tools', 'fr': 'Outils', 'it': 'Strumenti'},
    'tools_intro': {'es': 'Utilidades para elegir y entender el vino: qué beber con cada plato, en qué se parecen y se diferencian las uvas, y dónde está cada denominación.',
                    'en': 'Handy tools to choose and understand wine: what to drink with each dish, how grapes compare, and where each appellation lies.',
                    'fr': 'Des outils pour choisir et comprendre le vin : que boire avec chaque plat, en quoi les cépages se ressemblent ou diffèrent, et où se trouve chaque appellation.',
                    'it': 'Strumenti per scegliere e capire il vino: cosa bere con ogni piatto, come si confrontano i vitigni e dove si trova ogni denominazione.'},
    'pairing': {'es': 'Buscador de maridajes', 'en': 'Food and wine pairing', 'fr': 'Accords mets et vins', 'it': 'Abbinamenti cibo e vino'},
    'pairing_intro': {'es': 'Elige qué vas a comer y te proponemos estilos de vino, uvas y vinos concretos de la enciclopedia.',
                      'en': 'Choose what you are eating and we suggest wine styles, grapes and specific wines from the encyclopedia.',
                      'fr': 'Choisissez ce que vous allez manger : nous vous proposons des styles de vin, des cépages et des vins précis de l\'encyclopédie.',
                      'it': 'Scegli cosa mangerai e ti proponiamo stili di vino, vitigni e vini precisi dell\'enciclopedia.'},
    'compare': {'es': 'Comparador de uvas', 'en': 'Grape comparison', 'fr': 'Comparateur de cépages', 'it': 'Confronto tra vitigni'},
    'compare_intro': {'es': 'Pon dos o tres uvas lado a lado: color, origen, aromas típicos, países donde se cultivan y regiones donde destacan.',
                      'en': 'Put two or three grapes side by side: colour, origin, typical aromas, countries where they grow and regions where they shine.',
                      'fr': 'Comparez deux ou trois cépages côte à côte : couleur, origine, arômes typiques, pays de culture et régions où ils brillent.',
                      'it': 'Metti a confronto due o tre vitigni: colore, origine, aromi tipici, paesi in cui si coltivano e regioni in cui eccellono.'},
    'map': {'es': 'Mapa de denominaciones', 'en': 'Map of wine regions', 'fr': 'Carte des appellations', 'it': 'Mappa delle denominazioni'},
    'map_intro': {'es': 'Todas las regiones y denominaciones de la enciclopedia sobre el mapa. Elige un país o pulsa un punto para abrir su ficha.',
                  'en': 'Every region and appellation in the encyclopedia on the map. Pick a country or tap a point to open its page.',
                  'fr': 'Toutes les régions et appellations de l\'encyclopédie sur la carte. Choisissez un pays ou touchez un point pour ouvrir sa fiche.',
                  'it': 'Tutte le regioni e denominazioni dell\'enciclopedia sulla mappa. Scegli un paese o tocca un punto per aprirne la scheda.'},
    'what_eat': {'es': '¿Qué vas a comer?', 'en': 'What are you eating?', 'fr': 'Que mangez-vous ?', 'it': 'Cosa mangi?'},
    'grapes_to_try': {'es': 'Uvas que van bien', 'en': 'Grapes that work well', 'fr': 'Cépages qui conviennent', 'it': 'Vitigni adatti'},
    'wines_to_try': {'es': 'Vinos de la enciclopedia para probar', 'en': 'Wines from the encyclopedia to try', 'fr': 'Vins de l\'encyclopédie à essayer', 'it': 'Vini dell\'enciclopedia da provare'},
    'dishes_cul': {'es': 'Platos de este tipo en Culinapedia', 'en': 'Dishes of this kind on Culinapedia', 'fr': 'Plats de ce type sur Culinapedia', 'it': 'Piatti di questo tipo su Culinapedia'},
    'pair_note': {'es': 'Sugerencia orientativa: el mejor maridaje es el que te gusta. Si bebes alcohol, hazlo con moderación.',
                  'en': 'A general suggestion: the best pairing is the one you enjoy. If you drink alcohol, do so in moderation.',
                  'fr': 'Suggestion indicative : le meilleur accord est celui qui vous plaît. L\'abus d\'alcool est dangereux pour la santé.',
                  'it': 'Suggerimento indicativo: il miglior abbinamento è quello che ti piace. Se bevi alcol, fallo con moderazione.'},
    'pick_grape': {'es': 'Elige una uva', 'en': 'Choose a grape', 'fr': 'Choisissez un cépage', 'it': 'Scegli un vitigno'},
    'none': {'es': '(ninguna)', 'en': '(none)', 'fr': '(aucun)', 'it': '(nessuno)'},
    'colour': {'es': 'Color', 'en': 'Colour', 'fr': 'Couleur', 'it': 'Colore'},
    'origin': {'es': 'Origen', 'en': 'Origin', 'fr': 'Origine', 'it': 'Origine'},
    'aromas': {'es': 'Aromas típicos', 'en': 'Typical aromas', 'fr': 'Arômes typiques', 'it': 'Aromi tipici'},
    'synonyms': {'es': 'Otros nombres', 'en': 'Other names', 'fr': 'Autres noms', 'it': 'Altri nomi'},
    'countries': {'es': 'Países', 'en': 'Countries', 'fr': 'Pays', 'it': 'Paesi'},
    'regions': {'es': 'Regiones donde destaca', 'en': 'Regions where it shines', 'fr': 'Régions où il brille', 'it': 'Regioni in cui eccelle'},
    'nwines': {'es': 'Vinos en la enciclopedia', 'en': 'Wines in the encyclopedia', 'fr': 'Vins dans l\'encyclopédie', 'it': 'Vini nell\'enciclopedia'},
    'summary': {'es': 'En pocas palabras', 'en': 'In a nutshell', 'fr': 'En bref', 'it': 'In breve'},
    'open': {'es': 'Ver ficha', 'en': 'Open page', 'fr': 'Voir la fiche', 'it': 'Apri la scheda'},
    'all_countries': {'es': 'Todo el mundo', 'en': 'Whole world', 'fr': 'Monde entier', 'it': 'Tutto il mondo'},
    'red': {'es': 'Tinta', 'en': 'Red', 'fr': 'Noir', 'it': 'Rosso'},
    'white': {'es': 'Blanca', 'en': 'White', 'fr': 'Blanc', 'it': 'Bianco'},
    'map_list': {'es': 'Denominaciones de', 'en': 'Appellations in', 'fr': 'Appellations de', 'it': 'Denominazioni di'},
    'map_note': {'es': 'Los puntos marcan el centro aproximado de la zona de viñedo de cada denominación.',
                 'en': 'Points mark the approximate centre of each appellation\'s vineyard area.',
                 'fr': 'Les points indiquent le centre approximatif de la zone viticole de chaque appellation.',
                 'it': 'I punti indicano il centro approssimativo della zona vitata di ogni denominazione.'},
}
def tx(k, l): return TX[k][l]

# Mismas 12 categorías y criterio que el recuadro de maridaje de Culinapedia (novedades.py), ampliado.
PAIR = [
 ('roja', '🥩', {'es': 'Carne roja y caza', 'en': 'Red meat and game', 'fr': 'Viande rouge et gibier', 'it': 'Carne rossa e selvaggina'},
  {'es': 'Tintos con cuerpo y algo de crianza: sus taninos se suavizan con la proteína y la grasa de la carne. Con asados y caza, tintos estructurados; con un filete a la plancha, también un tinto medio.',
   'en': 'Full-bodied reds with some oak ageing: their tannins soften against the protein and fat of the meat. Structured reds for roasts and game; a medium-bodied red also works with a grilled steak.',
   'fr': 'Des rouges charpentés avec un peu d\'élevage : leurs tanins s\'assouplissent au contact des protéines et du gras de la viande. Des rouges structurés pour les rôtis et le gibier ; un rouge moyen convient aussi à une pièce grillée.',
   'it': 'Rossi corposi con un po\' di affinamento: i tannini si ammorbidiscono con le proteine e il grasso della carne. Rossi strutturati per arrosti e selvaggina; con una bistecca alla griglia va bene anche un rosso medio.'},
  ['tempranillo', 'cabernet-sauvignon', 'syrah', 'nebbiolo', 'malbec', 'monastrell'], ['tinto']),
 ('cerdo', '🍖', {'es': 'Cerdo y embutidos', 'en': 'Pork and cured meats', 'fr': 'Porc et charcuterie', 'it': 'Maiale e salumi'},
  {'es': 'Tintos ligeros y afrutados o un rosado, que acompañan la grasa sin taparla. Con jamón ibérico, un fino o una manzanilla también funcionan muy bien.',
   'en': 'Light, fruity reds or a rosé, which match the fat without overpowering it. With Iberian ham, a fino or manzanilla also works very well.',
   'fr': 'Des rouges légers et fruités ou un rosé, qui accompagnent le gras sans l\'écraser. Avec le jambon ibérique, un fino ou une manzanilla fonctionnent aussi très bien.',
   'it': 'Rossi leggeri e fruttati o un rosato, che accompagnano il grasso senza coprirlo. Con il prosciutto iberico funzionano molto bene anche un fino o una manzanilla.'},
  ['garnacha', 'pinot-noir', 'mencia', 'tempranillo'], ['tinto', 'rosado']),
 ('ave', '🍗', {'es': 'Aves', 'en': 'Poultry', 'fr': 'Volaille', 'it': 'Pollame'},
  {'es': 'Blancos con cuerpo o tintos ligeros. Con pollo asado, un chardonnay con barrica o un pinot noir; con pato, un tinto algo más estructurado.',
   'en': 'Full-bodied whites or light reds. With roast chicken, an oaked Chardonnay or a Pinot Noir; with duck, a slightly more structured red.',
   'fr': 'Des blancs amples ou des rouges légers. Avec un poulet rôti, un chardonnay élevé en fût ou un pinot noir ; avec le canard, un rouge un peu plus structuré.',
   'it': 'Bianchi corposi o rossi leggeri. Con il pollo arrosto, uno chardonnay in barrique o un pinot nero; con l\'anatra, un rosso un po\' più strutturato.'},
  ['chardonnay', 'pinot-noir', 'godello', 'garnacha'], ['blanco', 'tinto']),
 ('pescado', '🐟', {'es': 'Pescado', 'en': 'Fish', 'fr': 'Poisson', 'it': 'Pesce'},
  {'es': 'Blancos secos. Con pescados blancos y delicados, blancos frescos; con pescados grasos (salmón, atún) o en salsa, blancos con algo más de cuerpo o un rosado.',
   'en': 'Dry whites. Fresh whites with delicate white fish; slightly fuller whites or a rosé with oily fish (salmon, tuna) or fish in sauce.',
   'fr': 'Des blancs secs. Des blancs vifs avec les poissons blancs délicats ; des blancs un peu plus amples ou un rosé avec les poissons gras (saumon, thon) ou en sauce.',
   'it': 'Bianchi secchi. Bianchi freschi con pesci bianchi delicati; bianchi un po\' più corposi o un rosato con pesci grassi (salmone, tonno) o in salsa.'},
  ['albarino', 'verdejo', 'chardonnay', 'godello', 'sauvignon-blanc'], ['blanco']),
 ('marisco', '🦐', {'es': 'Marisco', 'en': 'Seafood', 'fr': 'Fruits de mer', 'it': 'Frutti di mare'},
  {'es': 'Blancos frescos y salinos, o un espumoso. La acidez y las notas marinas del albariño o el muscadet acompañan muy bien a ostras, almejas y gambas.',
   'en': 'Fresh, saline whites, or a sparkling wine. The acidity and sea-breeze notes of Albariño or Muscadet suit oysters, clams and prawns very well.',
   'fr': 'Des blancs vifs et salins, ou un effervescent. L\'acidité et les notes iodées de l\'albariño ou du muscadet s\'accordent très bien avec huîtres, palourdes et crevettes.',
   'it': 'Bianchi freschi e sapidi, o uno spumante. L\'acidità e le note marine dell\'albariño o del muscadet si sposano molto bene con ostriche, vongole e gamberi.'},
  ['albarino', 'xarel-lo', 'sauvignon-blanc', 'chardonnay'], ['blanco', 'espumoso']),
 ('arroz', '🥘', {'es': 'Arroces y paella', 'en': 'Rice dishes and paella', 'fr': 'Riz et paella', 'it': 'Riso e paella'},
  {'es': 'Blancos frescos o rosados. Con arroces de marisco, un blanco o un rosado; con arroces de carne, un tinto joven y ligero.',
   'en': 'Fresh whites or rosés. A white or rosé with seafood rice; a young, light red with meat-based rice dishes.',
   'fr': 'Des blancs vifs ou des rosés. Un blanc ou un rosé avec un riz aux fruits de mer ; un rouge jeune et léger avec un riz à la viande.',
   'it': 'Bianchi freschi o rosati. Un bianco o un rosato con il riso ai frutti di mare; un rosso giovane e leggero con i risi di carne.'},
  ['verdejo', 'garnacha', 'albarino', 'macabeo'], ['blanco', 'rosado']),
 ('italiano', '🍝', {'es': 'Pasta y pizza', 'en': 'Pasta and pizza', 'fr': 'Pâtes et pizza', 'it': 'Pasta e pizza'},
  {'es': 'Con salsas de tomate, tintos con buena acidez como el sangiovese o la barbera, que acompañan la acidez del tomate. Con pasta en salsa blanca o con verduras, un blanco con cuerpo.',
   'en': 'With tomato sauces, reds with good acidity such as Sangiovese or Barbera, which match the acidity of tomato. With creamy or vegetable pasta, a fuller white.',
   'fr': 'Avec les sauces tomate, des rouges à bonne acidité comme le sangiovese ou la barbera, qui accompagnent l\'acidité de la tomate. Avec des pâtes à la crème ou aux légumes, un blanc ample.',
   'it': 'Con i sughi al pomodoro, rossi di buona acidità come il sangiovese o la barbera, che accompagnano l\'acidità del pomodoro. Con pasta in bianco o alle verdure, un bianco corposo.'},
  ['sangiovese', 'garnacha', 'nebbiolo', 'chardonnay'], ['tinto', 'blanco']),
 ('verdura', '🥗', {'es': 'Verduras, ensaladas y legumbres', 'en': 'Vegetables, salads and pulses', 'fr': 'Légumes, salades et légumineuses', 'it': 'Verdure, insalate e legumi'},
  {'es': 'Blancos ligeros y frescos, con notas herbáceas que acompañan a la verdura. Con guisos de legumbres, un tinto joven.',
   'en': 'Light, fresh whites, with herbaceous notes that suit vegetables. A young red with pulse stews.',
   'fr': 'Des blancs légers et vifs, aux notes herbacées qui conviennent aux légumes. Un rouge jeune avec les plats mijotés de légumineuses.',
   'it': 'Bianchi leggeri e freschi, con note erbacee che accompagnano le verdure. Con gli stufati di legumi, un rosso giovane.'},
  ['sauvignon-blanc', 'godello', 'verdejo', 'mencia'], ['blanco', 'rosado']),
 ('frito', '🍤', {'es': 'Fritos y tapas', 'en': 'Fried food and tapas', 'fr': 'Fritures et tapas', 'it': 'Fritti e tapas'},
  {'es': 'Generosos secos (fino, manzanilla) o un espumoso: su acidez y sus burbujas limpian la boca después de cada bocado frito.',
   'en': 'Dry fortified wines (fino, manzanilla) or a sparkling wine: their acidity and bubbles cleanse the palate after each fried bite.',
   'fr': 'Des vins mutés secs (fino, manzanilla) ou un effervescent : leur acidité et leurs bulles nettoient la bouche après chaque bouchée frite.',
   'it': 'Vini liquorosi secchi (fino, manzanilla) o uno spumante: acidità e bollicine puliscono la bocca dopo ogni boccone fritto.'},
  ['palomino', 'macabeo', 'xarel-lo', 'chardonnay'], ['generoso', 'espumoso']),
 ('especiado', '🌶️', {'es': 'Picante y cocina asiática', 'en': 'Spicy and Asian food', 'fr': 'Cuisine épicée et asiatique', 'it': 'Cucina piccante e asiatica'},
  {'es': 'Blancos aromáticos, mejor con un punto de dulzor, que suavizan el picante. Evita los tintos muy tánicos y alcohólicos, que lo acentúan.',
   'en': 'Aromatic whites, ideally off-dry, which soften the heat. Avoid very tannic, high-alcohol reds, which make it hotter.',
   'fr': 'Des blancs aromatiques, idéalement avec une pointe de sucre, qui adoucissent le piquant. Évitez les rouges très tanniques et alcooleux, qui l\'accentuent.',
   'it': 'Bianchi aromatici, meglio se con un filo di dolcezza, che ammorbidiscono il piccante. Evita i rossi molto tannici e alcolici, che lo accentuano.'},
  ['riesling', 'gewurztraminer', 'chenin-blanc', 'moscatel'], ['blanco']),
 ('queso', '🧀', {'es': 'Quesos', 'en': 'Cheese', 'fr': 'Fromages', 'it': 'Formaggi'},
  {'es': 'Depende del queso: blancos con cuerpo para los frescos y suaves; tintos o vinos generosos para los curados; y un vino dulce con los azules.',
   'en': 'It depends on the cheese: full-bodied whites for fresh, mild cheeses; reds or fortified wines for aged ones; and a sweet wine with blue cheese.',
   'fr': 'Tout dépend du fromage : des blancs amples pour les frais et doux ; des rouges ou des vins mutés pour les affinés ; et un vin doux avec les bleus.',
   'it': 'Dipende dal formaggio: bianchi corposi per i freschi e delicati; rossi o vini liquorosi per gli stagionati; e un vino dolce con gli erborinati.'},
  ['chardonnay', 'tempranillo', 'palomino', 'pedro-ximenez'], ['blanco', 'tinto', 'generoso', 'dulce']),
 ('dulce', '🍰', {'es': 'Postres', 'en': 'Desserts', 'fr': 'Desserts', 'it': 'Dolci'},
  {'es': 'Un vino dulce, al menos tan dulce como el postre: moscatel con postres de fruta y crema; Pedro Ximénez u oporto con chocolate.',
   'en': 'A sweet wine, at least as sweet as the dessert: Muscat with fruit and cream desserts; Pedro Ximénez or Port with chocolate.',
   'fr': 'Un vin doux, au moins aussi sucré que le dessert : muscat avec les desserts aux fruits et à la crème ; Pedro Ximénez ou porto avec le chocolat.',
   'it': 'Un vino dolce, almeno quanto il dessert: moscato con dolci alla frutta e alla crema; Pedro Ximénez o porto con il cioccolato.'},
  ['moscatel', 'pedro-ximenez', 'riesling'], ['dulce', 'generoso']),
]

def _pair_wines(grapes, types, n=8):
    gs = set(grapes)
    pool = [w for w in V.values() if w.get('type') in types and gs & set(w.get('grapes', []))]
    # variedad: alterna uvas y regiones
    pool.sort(key=lambda w: (min(grapes.index(g) for g in w.get('grapes', []) if g in gs), w['name']))
    out, seen_r = [], set()
    for w in pool:
        if w.get('region') in seen_r: continue
        out.append(w); seen_r.add(w.get('region'))
        if len(out) >= n: break
    return out

TOOLS_CSS = '''<style>
.toolgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin-top:20px}
.toolcard{display:block;background:white;border:1px solid var(--line);padding:22px;color:var(--ink);text-decoration:none}
.toolcard b{display:block;font:24px Georgia;margin:6px 0}.toolcard span{font-size:14px;color:#56635c}.toolcard i{font-style:normal;font-size:28px}
.dishes{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0}
.dishes button{border:1px solid var(--line);background:white;padding:9px 13px;font-size:15px;border-radius:999px;cursor:pointer;color:var(--ink)}
.dishes button[aria-pressed=true]{background:var(--wine);border-color:var(--wine);color:white}
.pairbox{display:none}.pairbox.on{display:block}
.pairbox h2{margin-top:6px}.pairbox p a{color:var(--wine)}.pairbox .note{font-size:12px;color:#68736c}
.cmp{width:100%;border-collapse:collapse;background:white;margin-top:16px;font-size:14px}
.cmp th,.cmp td{border:1px solid var(--line);padding:10px;vertical-align:top;text-align:left}
.cmp th{background:#f0f1eb;width:18%;font-weight:600}.cmp td a{color:var(--wine)}
.cmpsel{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}.cmpsel select{padding:10px;font-size:15px;border:1px solid var(--line);background:white;min-width:200px;flex:1}
#map{height:560px;border:1px solid var(--line);margin-top:14px;background:#e7eadf}
.mapbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:14px}.mapbar select{padding:10px;font-size:15px;border:1px solid var(--line);background:white;min-width:220px}
.maplist{columns:3 220px;margin-top:16px;font-size:14px}.maplist a{display:block;color:var(--wine);padding:2px 0}
@media(max-width:850px){#map{height:420px}.cmp{font-size:12px}.cmp th,.cmp td{padding:6px}.dishes button{font-size:14px;padding:8px 11px}}
</style>'''

def tool_url(l, k=None): return url(l, 'tools', TOOL_SLUG[k][l] if k else None)
def tool_alts(k=None): return {x: tool_url(x, k) for x in LANGS}

def tools_hub(l):
    cards = ''.join(f'<a class="toolcard" href="{tool_url(l, k)}"><i>{ic}</i><b>{tx(k, l)}</b><span>{tx(k + "_intro", l)}</span></a>'
                    for k, ic in (('pairing', '🍽️'), ('compare', '⚖️'), ('map', '🗺️')))
    body = TOOLS_CSS + page_wrap(l, tx('tools', l), tx('tools_intro', l), f'<div class="toolgrid">{cards}</div>', [(tx('tools', l), None)])
    return layout(l, tx('tools', l) + ' · WorldWinePedia', tx('tools_intro', l), body, tool_alts(), 'tools')

def pairing_page(l):
    btns, boxes = '', ''
    for i, (k, ic, name, txt, grapes, types) in enumerate(PAIR):
        btns += f'<button type="button" data-k="{k}" aria-pressed="{"true" if i == 0 else "false"}">{ic} {e(name[l])}</button>'
        gl = ' · '.join(a_(url(l, 'grapes', g), T(G[g]['name'], l)) for g in grapes if g in G)
        ws_ = _pair_wines(grapes, types)
        cards = ''.join(wine_card(l, w, photo=False) for w in ws_)
        cul = 'https://culinapedia.com/' + ('en/' if l == 'en' else '')
        boxes += (f'<section class="pairbox{" on" if i == 0 else ""}" id="p-{k}" style="padding:0">'
                  f'<h2>{ic} {e(name[l])}</h2><p class="lead" style="font-size:17px">{e(txt[l])}</p>'
                  f'<p><strong>{tx("grapes_to_try", l)}:</strong> {gl}</p>'
                  + (f'<h3 style="margin-top:22px">{tx("wines_to_try", l)}</h3><div class="listgrid">{cards}</div>' if cards else '')
                  + f'<p style="margin-top:16px"><a class="textlink" href="{cul}" rel="noopener">{tx("dishes_cul", l)} ↗</a></p>'
                  f'<p class="note">{tx("pair_note", l)}</p></section>')
    js = ('<script>(function(){var b=document.querySelectorAll(".dishes button");b.forEach(function(x){x.addEventListener("click",function(){'
          'b.forEach(function(y){y.setAttribute("aria-pressed",y===x?"true":"false")});'
          'document.querySelectorAll(".pairbox").forEach(function(p){p.classList.toggle("on",p.id==="p-"+x.dataset.k)});'
          'history.replaceState(null,"","#"+x.dataset.k)})});var h=location.hash.slice(1);if(h){var t=document.querySelector(\'.dishes button[data-k="\'+h+\'"]\');if(t)t.click()}})();</script>')
    inner = f'<h2 style="font-size:22px;margin-top:10px">{tx("what_eat", l)}</h2><div class="dishes">{btns}</div>{boxes}{js}'
    body = TOOLS_CSS + page_wrap(l, tx('pairing', l), tx('pairing_intro', l), inner, [(tx('tools', l), tool_url(l)), (tx('pairing', l), None)])
    return layout(l, tx('pairing', l) + ' · WorldWinePedia', tx('pairing_intro', l), body, tool_alts('pairing'), 'tools')

def compare_page(l):
    gr = {}
    for g in G.values():
        regs = [r for r in R.values() if g['slug'] in r.get('grapes', [])]
        gr[g['slug']] = {
            'n': T(g['name'], l), 'u': url(l, 'grapes', g['slug']),
            'c': tx('red' if g.get('color') == 'tinta' else 'white', l),
            'o': T(g.get('origin'), l) or '', 'a': T(g.get('aromas'), l) or '',
            's': ', '.join(g.get('synonyms') or []), 'r': T(g.get('summary'), l) or '',
            'p': ', '.join(T(C[c]['name'], l) for c in g.get('countries', []) if c in C),
            'g': [[T(r['name'], l), url(l, 'regions', r['slug'])] for r in sorted(regs, key=lambda r: T(r['name'], l))[:12]],
            'w': sum(1 for w in V.values() if g['slug'] in w.get('grapes', [])),
        }
    order = sorted(gr, key=lambda k: gr[k]['n'].lower())
    opts = ''.join(f'<option value="{k}">{e(gr[k]["n"])}</option>' for k in order)
    defaults = ['tempranillo', 'cabernet-sauvignon', 'pinot-noir']
    sels = ''.join(f'<select aria-label="{tx("pick_grape", l)} {i + 1}" data-i="{i}">{"<option value=\"\">" + tx("none", l) + "</option>" if i == 2 else ""}{opts}</select>' for i in range(3))
    rows = [('n', ''), ('c', tx('colour', l)), ('r', tx('summary', l)), ('o', tx('origin', l)), ('a', tx('aromas', l)), ('s', tx('synonyms', l)), ('p', tx('countries', l)), ('g', tx('regions', l)), ('w', tx('nwines', l))]
    data = json.dumps(gr, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    js = ('<script>(function(){var D=' + data + ',R=' + json.dumps(rows, ensure_ascii=False) + ',S=document.querySelectorAll(".cmpsel select"),T=document.getElementById("cmpt"),O=' + json.dumps(tx('open', l)) + ';'
          'function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c]})}'
          'function draw(){var ks=[].map.call(S,function(s){return s.value}).filter(function(k){return k&&D[k]});var h="";'
          'R.forEach(function(r){h+="<tr><th>"+esc(r[1])+"</th>";ks.forEach(function(k){var g=D[k],v=g[r[0]];'
          'if(r[0]==="n")v="<a href=\\""+g.u+"\\"><strong>"+esc(g.n)+"</strong></a>";else if(r[0]==="g")v=v.map(function(x){return "<a href=\\""+x[1]+"\\">"+esc(x[0])+"</a>"}).join(", ");else v=esc(v);'
          'h+="<td>"+(v===""?"—":v)+"</td>"});h+="</tr>"});T.innerHTML=h;history.replaceState(null,"","#"+ks.join(","))}'
          'var h=location.hash.slice(1).split(",").filter(function(k){return D[k]}),d=' + json.dumps(defaults) + ';'
          'S.forEach(function(s,i){s.value=h.length?(h[i]||""):d[i];if(s.selectedIndex<0)s.value="";s.addEventListener("change",draw)});draw()})();</script>')
    inner = f'<div class="cmpsel">{sels}</div><div style="overflow-x:auto"><table class="cmp"><tbody id="cmpt"></tbody></table></div>{js}'
    body = TOOLS_CSS + page_wrap(l, tx('compare', l), tx('compare_intro', l), inner, [(tx('tools', l), tool_url(l)), (tx('compare', l), None)])
    return layout(l, tx('compare', l) + ' · WorldWinePedia', tx('compare_intro', l), body, tool_alts('compare'), 'tools')

GEO = json.load(open(os.path.join(ROOT, 'data', 'geo.json'))) if os.path.exists(os.path.join(ROOT, 'data', 'geo.json')) else {'regions': {}, 'countries': {}}

def map_page(l):
    pts = [[r['slug'], T(r['name'], l), r['country'], url(l, 'regions', r['slug'])] + GEO['regions'][r['slug']] for r in R.values() if r['slug'] in GEO['regions']]
    cs = sorted({p[2] for p in pts}, key=lambda c: T(C[c]['name'], l))
    copts = f'<option value="">{tx("all_countries", l)}</option>' + ''.join(f'<option value="{c}">{e(T(C[c]["name"], l))}</option>' for c in cs)
    cz = {c: GEO['countries'].get(c) for c in cs}
    # lista estática (también sirve sin JavaScript y para buscadores)
    lists = ''.join(f'<div data-c="{c}"><h3>{e(T(C[c]["name"], l))}</h3>' + ''.join(f'<a href="{p[3]}">{e(p[1])}</a>' for p in sorted(pts, key=lambda p: p[1]) if p[2] == c) + '</div>' for c in cs)
    data = json.dumps({'p': pts, 'c': cz}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    js = ('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">'
          '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>'
          '<script>(function(){var D=' + data + ';if(!window.L){document.getElementById("map").style.display="none";return}'
          'var m=L.map("map",{scrollWheelZoom:false}).setView([30,10],2);'
          'L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:12,attribution:"© <a href=\\"https://www.openstreetmap.org/copyright\\">OpenStreetMap</a>"}).addTo(m);'
          'var mk=D.p.map(function(p){return L.circleMarker([p[4],p[5]],{radius:6,color:"#5c1f37",weight:1.5,fillColor:"#7b2a49",fillOpacity:.85}).bindPopup("<a href=\\""+p[3]+"\\"><strong>"+p[1].replace(/</g,"&lt;")+"</strong></a>").bindTooltip(p[1]).addTo(m)});'
          'var sel=document.getElementById("mapc"),lst=document.querySelectorAll(".maplist>div");'
          'function go(c){var z=c&&D.c[c],b=[];if(z){D.p.forEach(function(p){if(p[2]===c&&Math.abs(p[4]-z[0])<9&&Math.abs(p[5]-z[1])<14)b.push([p[4],p[5]])})}'
          'if(b.length>1)m.fitBounds(b,{padding:[30,30],maxZoom:8});else if(z)m.setView([z[0],z[1]],z[2]);else m.fitBounds(L.featureGroup(mk).getBounds(),{padding:[20,20]});'
          'lst.forEach(function(d){d.style.display=!c||d.dataset.c===c?"":"none"});history.replaceState(null,"","#"+(c||""))}'
          'sel.addEventListener("change",function(){go(sel.value)});var h=location.hash.slice(1);if(h&&D.c[h])sel.value=h;go(sel.value)})();</script>')
    inner = (f'<div class="mapbar"><select id="mapc" aria-label="{tx("countries", l)}">{copts}</select><small style="color:#68736c">{tx("map_note", l)}</small></div>'
             f'<div id="map"></div><div class="maplist">{lists}</div>{js}')
    body = TOOLS_CSS + page_wrap(l, tx('map', l), tx('map_intro', l), inner, [(tx('tools', l), tool_url(l)), (tx('map', l), None)])
    return layout(l, tx('map', l) + ' · WorldWinePedia', tx('map_intro', l), body, tool_alts('map'), 'tools')

def tools_pages(l):
    return [(tool_url(l), tools_hub(l)), (tool_url(l, 'pairing'), pairing_page(l)), (tool_url(l, 'compare'), compare_page(l)), (tool_url(l, 'map'), map_page(l))]
