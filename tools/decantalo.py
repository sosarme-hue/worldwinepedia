"""Cruza el catálogo de Decantalo (feed de Daisycon) con las fichas de vinos.

Uso: python3 tools/decantalo.py ruta/decantalo-catalogo.json
Escribe data/decantalo.json: {slug: {name, url, img}}.
El catálogo se descarga en my.daisycon.com > Material > Feeds de productos > Decantalo (INT).
"""
import json, os, re, sys, glob, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    s = s.replace('&', ' and ')
    s = re.sub(r"[’'`]", ' ', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return ' '.join(s.split())

STOP = {'vino', 'tinto', 'blanco', 'rosado', 'magnum', 'cl', 'l', 'estuche', 'caja', 'de', 'del', 'la', 'el', 'les', 'le', 'di', 'do', 'da', 'the', 'bodegas', 'bodega', 'domaine', 'chateau', 'celler', 'cellers', 'cantina', 'weingut', 'quinta', 'and', 'y', 'e', 'et'}

def strip_title(t):
    t = norm(t)
    t = re.sub(r'\b(19|20)\d\d\b', ' ', t)          # añada
    t = re.sub(r'\b\d+([ ,.]\d+)? ?(cl|l|ml)\b', ' ', t)  # formato
    t = re.sub(r'\b(magnum|jeroboam|estuche|caja|pack|botella|botellas|x ?\d+)\b', ' ', t)
    return ' '.join(t.split())

# Coincidencias aproximadas revisadas a mano y descartadas (otro vino de la misma bodega)
EXCLUDE = {
    'chateau-de-fieuzal-blanc',
    'chateau-de-fieuzal-rouge',
    'chateau-olivier-blanc',
    'chateau-saint-pierre',
    'clos-des-fees-clos-des-fees',
    'foradori-teroldego',
    'kripta',
    'muga-reserva',
    'ornellaia',
    'quinta-do-vallado-douro-tinto',
    'roda-i',
    'segla',
    'valduero-reserva',
    'y-d-yquem',
    'chateau-olivier-rouge',
    'm-de-minuty-rouge',
}
CONFLICT = {'rosado', 'rose', 'rosat', 'blanco', 'blanc', 'branco', 'bianco', 'tinto', 'rouge', 'negre', 'rosso', 'crozes', 'ice', 'touriga', 'masseto', 'abeille', 'jeune', 'kiedricher', 'tonschiefer', 'vinas', 'viejas', 'miranda', 'rauzan', 'perle'}

def main(feed):
    P = [p for p in json.load(open(feed, encoding='utf-8')) if p.get('cat') == 'Vino' and p.get('l')]
    W = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(os.path.join(DATA, 'wines', '*.json')))]
    B = {}
    for f in glob.glob(os.path.join(DATA, 'wineries', '*.json')):
        b = json.load(open(f, encoding='utf-8')); B[b['slug']] = b
    prods = []
    for p in P:
        st = strip_title(p['t']); br = norm(p['b'])
        prods.append((p, st, br, set(st.split()) - STOP, set(br.split()) - STOP))
    by_title = {}
    for x in prods: by_title.setdefault(x[1], []).append(x)
    out = {}; global FB; FB = {}
    for w in W:
        wname = strip_title(w['name']); win = norm(B.get(w.get('winery'), {}).get('name', ''))
        wint = set(win.split()) - STOP
        cands = []
        # 1) mismo nombre exacto (con o sin la bodega delante)
        keys = {wname, (win + ' ' + wname).strip()}
        if win and wname.startswith(win + ' '): keys.add(wname[len(win) + 1:])
        for k in keys:
            for x in by_title.get(k, []):
                p, st, br, tt, bt = x
                # nombres cortos o genéricos: exigir que coincida la bodega
                if len(set(k.split()) - STOP) < 2 and not (wint & (bt | tt)) and not (tt and tt <= bt): continue
                cands.append((0, x))
        # 2) todas las palabras del nombre están en el título y la bodega coincide
        if not cands:
            wt = set(wname.split()) - STOP - {'rouge', 'red', 'tinto', 'rosso', 'negre'}
            if len(wt) >= 1 and wint:
                for x in prods:
                    p, st, br, tt, bt = x
                    extra = tt - wt - wint
                    if wt <= tt and wint <= (bt | tt) and len(extra) <= 2 and not (extra & CONFLICT):
                        cands.append((len(tt - wt - wint), x))
        if not cands or w['slug'] in EXCLUDE: continue
        cands.sort(key=lambda c: (c[0], c[1][0].get('st') != 'true', len(c[1][1]), float(c[1][0].get('pr') or 0)))
        p = cands[0][1][0]
        out[w['slug']] = {'name': p['t'], 'url': p['l'], 'img': p.get('i', '')}; FB[w['slug']] = cands[0][0] if not any(c[0]==0 and c[1][1] in keys for c in cands[:1]) else None
    json.dump(out, open(os.path.join(DATA, 'decantalo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print(len(P), 'vinos en el catálogo;', len(W), 'fichas;', len(out), 'fichas enlazadas')

if __name__ == '__main__':
    main(sys.argv[1])
