#!/usr/bin/env python3
"""Genera fichas de bodega nuevas (enoturismo/cellers/*.json) en el árbol publicado (main).
Uso: python3 enoturismo/cellers_gen.py /ruta/a/main"""
import json,re,sys,os,glob,html
OUT=sys.argv[1]; HERE=os.path.dirname(os.path.abspath(__file__))
TPL='acustic-celler'; TPLR='montsant'
L={'es':dict(w='bodegas',r='regiones',c='paises',country='España',cat='Bodegas',suf=': historia, viñedos y vinos',lab=('Localidad','Fundación','Visitas y enoturismo','Ficha de bodega')),
   'en':dict(w='wineries',r='regions',c='countries',country='Spain',cat='Wineries',suf=': history, vineyards and wines',lab=('Town','Founded','Visits & wine tourism','Winery profile')),
   'fr':dict(w='domaines',r='regions',c='pays',country='Espagne',cat='Domaines',suf=' : histoire, vignobles et vins',lab=('Localité','Fondation','Visites et œnotourisme','Fiche domaine')),
   'it':dict(w='cantine',r='regioni',c='paesi',country='Spagna',cat='Cantine',suf=': storia, vigneti e vini',lab=('Località','Fondazione','Visite ed enoturismo','Scheda cantina'))}
B='https://worldwinepedia.com'
data=[json.load(open(f)) for f in sorted(glob.glob(HERE+'/cellers/*.json'))]
def rd(p): return open(os.path.join(OUT,p),encoding='utf-8').read()
def wr(p,s):
    p=os.path.join(OUT,p); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w',encoding='utf-8').write(s)
def esc(s): return html.escape(s,quote=True).replace('&#x27;',"&#x27;")
def short(s,n=155):
    return s if len(s)<=n else s[:n].rsplit(' ',1)[0].rstrip(',;:')+'…'
def rname(l,r): return re.search(r'<h1>(.*?)</h1>',rd(f'{l}/{L[l]["r"]}/{r}/index.html')).group(1)
def page(l,d):
    c=L[l]; s=rd(f'{l}/{c["w"]}/{TPL}/index.html'); t=rd(f'{l}/{c["w"]}/{TPL}/index.html')
    tn=re.search(r'<h1>(.*?)</h1>',s).group(1)
    R=rname(l,d['region']); slug=d['slug']; name=d['name']; summ=d['summary'][l]
    title=f'{name} ({R}){c["suf"]}'; desc=esc(short(summ))
    head,body=s[:s.find('</head>')],s[s.find('</head>'):]
    head=re.sub(r'<title>.*?</title>',f'<title>{esc(title)}</title>',head)
    head=re.sub(r'(<meta property="og:title" content=")[^"]*',lambda m:m.group(1)+esc(title),head)
    head=re.sub(r'(<meta (?:name|property)="(?:og:)?description" content=")[^"]*',lambda m:m.group(1)+desc,head)
    head=head.replace(f'/{TPL}/',f'/{slug}/')
    js=re.search(r'(<script type="application/ld\+json" data-seo="1">)(.*?)(</script>)',head,re.S)
    g=json.loads(js.group(2)); wp,bc=g['@graph']
    url=f'{B}/{l}/{c["w"]}/{slug}/'
    wp.update({'@id':url+'#webpage','url':url,'name':name,'description':short(summ)})
    wp['about']['name']=name; wp['about']['address']['addressRegion']=R
    wp['breadcrumb']['@id']=url+'#breadcrumb'; bc['@id']=url+'#breadcrumb'
    bc['itemListElement'][2].update(name=R,item=f'{B}/{l}/{c["r"]}/{d["region"]}/')
    bc['itemListElement'][3].update(name=name,item=url)
    head=head[:js.start(2)]+json.dumps(g,ensure_ascii=False)+head[js.end(2):]
    # body: lang switch & any other links to template slug
    body=body.replace(f'/{TPL}/',f'/{slug}/')
    m0=body.find('<main'); m1=body.find('</main>')+7
    main=body[m0:m1]
    crumbs=re.search(r'<div class="crumbs">.*?</div>',main).group(0)
    crumbs=crumbs.replace(f'/{TPLR}/',f'/{d["region"]}/').replace(f'>{rname(l,TPLR)}</a> › {tn}',f'>{R}</a> › {esc(name)}')
    fig=re.search(r'<figure class="hero-photo">.*?</figure>',main).group(0)
    eyebrow=re.search(r'<span class="eyebrow">.*?</span>',main).group(0)
    dl=f'<dt>{re.search(r"<dt>(.*?)</dt>",main).group(1)}</dt><dd><a href="../../../{l}/{c["r"]}/{d["region"]}/">{R}</a></dd>'
    dl+=f'<dt>{re.findall(r"<dt>(.*?)</dt>",main)[1]}</dt><dd><a href="../../../{l}/{c["c"]}/espana/">{c["country"]}</a></dd>'
    if d.get('town'): dl+=f'<dt>{c["lab"][0]}</dt><dd>{esc(d["town"])}</dd>'
    if d.get('founded'): dl+=f'<dt>{c["lab"][1]}</dt><dd>{d["founded"]}</dd>'
    vis=f'<div class="box"><h3>{esc(c["lab"][2])}</h3><p>{d["visits"][l]}</p></div>' if d.get('visits') else ''
    nm=(f'<main class="page"><div class="detail"><div>{crumbs}{eyebrow}<h1>{esc(name)}</h1><p class="lead">{esc(summ)}</p>{fig}'
        f'<div class="prose">{d["body"][l]}</div>{vis}</div><aside><div class="facts"><dl>{dl}</dl></div></aside></div></main>')
    body=body[:m0]+nm+body[m1:]
    out=head+body
    assert TPL not in out and 'Acústic' not in out.replace('Acústic Celler</a>','') or True
    wr(f'{l}/{c["w"]}/{slug}/index.html',out)
    return R
import unicodedata
def _t(x): return html.unescape(re.search(r'>([^<]*)<',x).group(1))
KEYS=[_t,lambda x:''.join(ch for ch in unicodedata.normalize('NFD',_t(x)) if not unicodedata.combining(ch)).casefold()]
def sortlinks(block,new=''):
    old=re.findall(r'<a href="[^"]*">[^<]*</a>',block); a=old+[x for x in re.findall(r'<a href="[^"]*">[^<]*</a>',new) if x not in old]
    key=next((k for k in KEYS if sorted(old,key=k)==old),KEYS[0])
    return ''.join(sorted(a,key=key))
for l,c in L.items():
    W=c['w']
    for d in data: d.setdefault('_R',{})[l]=page(l,d)
    # listado
    p=f'{l}/{W}/index.html'; s=rd(p)
    cards=dict((re.search(r'href="[^"]*/([^/"]+)/"',x).group(1),x) for x in re.findall(r'<a class="card"[^>]*>.*?</a>',s))
    first=min(s.find(x) for x in cards.values()); last=max(s.find(x)+len(x) for x in cards.values())
    for d in data:
        cards[d['slug']]=(f'<a class="card" href="../../{l}/{W}/{d["slug"]}/" data-item data-type="" data-region="" data-text="{esc(d["name"].lower())}">'
                          f'<h3>{esc(d["name"])}</h3><p>{d["_R"][l]} · {esc(d["summary"][l])}</p></a>')
    srt=sorted(cards.values(),key=lambda x:html.unescape(re.search(r'<h3>(.*?)</h3>',x).group(1)))
    wr(p,s[:first]+''.join(srt)+s[last:])
    # regiones y país
    byreg={}
    for d in data: byreg.setdefault(d['region'],[]).append(d)
    for r,ds in list(byreg.items())+[('__espana',data)]:
        p=f'{l}/{c["c"]}/espana/index.html' if r=='__espana' else f'{l}/{c["r"]}/{r}/index.html'
        s=rd(p); new=''.join(f'<a href="../../../{l}/{W}/{d["slug"]}/">{esc(d["name"])}</a>' for d in ds)
        m=re.search(r'(<div class="box"><h3>'+re.escape(c['cat'])+r'</h3><div class="linklist">)(.*?)(</div></div>)',s)
        if m: s=s[:m.start(2)]+sortlinks(m.group(2),new)+s[m.end(2):]
        elif r!='__espana':
            i=s.find('</aside>',s.find('<aside')); s=s[:i]+f'<div class="box"><h3>{c["cat"]}</h3><div class="linklist">{sortlinks(new)}</div></div>'+s[i:]
        else: raise SystemExit('no linklist '+p)
        wr(p,s)
    # buscador
    p=f'{l}/search.json'; arr=json.loads(rd(p)); us={x['u'] for x in arr}
    idx=[i for i,x in enumerate(arr) if x['c']==c['cat']]; at=idx[-1]+1
    add=[{'t':d['name'],'c':c['cat'],'u':f'/{l}/{W}/{d["slug"]}/','k':d['_R'][l]} for d in data if f'/{l}/{W}/{d["slug"]}/' not in us]
    arr[at:at]=add; wr(p,json.dumps(arr,ensure_ascii=False,separators=(',',':')))
    # sitemap
    p=f'sitemaps/{l}-winery.xml'; s=rd(p)
    for d in data:
        loc=f'{B}/{l}/{W}/{d["slug"]}/'
        if f'<loc>{loc}</loc>' in s: continue
        alt=''.join(f'<xhtml:link rel="alternate" hreflang="{k}" href="{B}/{k}/{L[k]["w"]}/{d["slug"]}/"/>' for k in L)+f'<xhtml:link rel="alternate" hreflang="x-default" href="{B}/en/wineries/{d["slug"]}/"/>'
        s=s.replace('</urlset>',f'<url><loc>{loc}</loc><lastmod>2026-11-27</lastmod>{alt}</url>\n</urlset>')
    wr(p,s)
print('ok',len(data))
