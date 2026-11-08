# WorldWinePedia — formato de datos

Web enciclopédica del vino en 4 idiomas: es, en, fr, it. Cada texto traducible es un objeto
`{"es": "...", "en": "...", "fr": "...", "it": "..."}` (llamado **T** abajo). Las 4 versiones
deben ser traducciones naturales y completas (no resúmenes), escritas por un nativo culto.
Nombres propios (bodegas, vinos, DO) no se traducen; los nombres de países y de uvas con nombre
local sí cuando es costumbre (Garnacha / Grenache / Grenache / Grenache; Cariñena = Carignan…).

Todos los archivos: JSON UTF-8 válido, uno por entidad, en `data/<tipo>/<slug>.json`.
`slug`: minúsculas ASCII con guiones, sin acentos (ej. `ribera-del-duero`). Mismo slug en todos los idiomas.

## Reglas de contenido (MUY IMPORTANTES)
- Sólo hechos que conozcas con seguridad. Nada inventado: ni precios, ni puntuaciones, ni premios,
  ni cifras de producción, ni fechas o nombres de enólogos de los que no estés seguro.
  Si un dato concreto no lo sabes con seguridad, omite el campo (déjalo en null) en vez de inventar.
- Tono: enciclopedia divulgativa, claro y riguroso, sin tono publicitario ni superlativos vacíos.
- Texto en HTML simple permitido dentro de los campos largos (`body`, `history`…): sólo `<p>`, `<h2>`,
  `<h3>`, `<ul>`, `<li>`, `<strong>`, `<em>`. Nada de enlaces ni imágenes.
- Nada dirigido a menores ni que incite a beber en exceso.

## countries/<slug>.json
{"slug","continent": "europa|america|oceania|africa|asia",
 "code": "ES" (ISO-2), "name": T, "summary": T (1-2 frases),
 "body": T (HTML, 500-900 palabras: historia, clima, suelos, estilos, normativa/clasificaciones),
 "key_grapes": [grape slugs], "regions": [region slugs]}

## regions/<slug>.json  (región o denominación)
{"slug","country": country slug, "name": T (normalmente igual en los 4), "kind": T (p.ej. "D.O.Ca.", "D.O.", "Vino de Pago"),
 "summary": T (1-2 frases), "body": T (HTML, 350-600 palabras: historia, clima, suelos, subzonas, estilos, normas de crianza),
 "climate": T (una frase), "soils": T (una frase), "grapes": [grape slugs], "styles": T (una frase)}

## grapes/<slug>.json
{"slug","name": T, "color": "tinta|blanca", "origin": T (frase corta), "synonyms": ["..."],
 "summary": T, "body": T (HTML, 300-500 palabras: origen, viticultura, perfil en copa, dónde se cultiva),
 "aromas": T (lista corta separada por comas), "countries": [country slugs]}

## wineries/<slug>.json
{"slug","name": "nombre oficial", "country", "region": region slug, "town": "localidad" o null,
 "founded": año (número) o null si no seguro, "website": "https://..." sólo si estás seguro, si no null,
 "summary": T, "body": T (HTML, 200-400 palabras: historia, viñedos, estilo),
 "visits": T o null (enoturismo, sólo si sabes que ofrece visitas; genérico, sin horarios ni precios)}

## wines/<slug>.json
{"slug","name": "nombre comercial (sin añada)", "winery": winery slug, "region": region slug, "country",
 "type": "tinto|blanco|rosado|espumoso|dulce|generoso", "category": T o null (Crianza, Reserva, Brut Nature…),
 "grapes": [grape slugs],
 "summary": T (1-2 frases), "body": T (HTML, 120-250 palabras: elaboración y estilo, de forma general y prudente),
 "tasting": T (perfil sensorial típico del vino, prudente, 2-3 frases), "pairing": T (lista corta),
 "serve": T (temperatura de servicio y copa, p.ej. "16-18 °C, copa amplia"),
 "search": "texto para buscarlo en tiendas, p.ej. 'Viña Tondonia Reserva López de Heredia'"}

## articles/<slug>.json
{"slug","section": "ciencia|viticultura|cata|maridaje|historia|guias", "title": T, "summary": T,
 "body": T (HTML, 700-1200 palabras, con <h2>), "related_grapes": [], "related_regions": []}

## glossary.json  (un solo archivo, lista)
[{"slug","term": T, "definition": T (1-3 frases)}, ...]
