/* familia de webs: todas las webs pedia en el pie de todas las páginas (2026-11-01; v4 2026-11-07: 12 webs, + ludicopedia y catdogpedia) */
(function () {
  function poner() {
    try {
      var f = document.querySelector('footer.pie');
      if (!f) { var fs = document.querySelectorAll('body > footer'); f = fs[fs.length - 1]; }
      if (!f) return;
      var webs = ['classicapedia.com', 'pinacopedia.com', 'filopedia.com', 'cinematopedia.com', 'medicapedia.org', 'tenispedia.com', 'newtonpedia.com', 'culinapedia.com', 'mythicapedia.com', 'zodiacopedia.com', 'ludicopedia.com', 'catdogpedia.com'];
      /* webs que tienen versión en inglés en /en/ */
      var conEn = ['classicapedia.com', 'pinacopedia.com', 'filopedia.com', 'cinematopedia.com', 'medicapedia.org', 'tenispedia.com', 'newtonpedia.com', 'culinapedia.com', 'mythicapedia.com', 'zodiacopedia.com', 'catdogpedia.com'];
      /* parejas que no se enlazan entre sí (vacío: todas enlazan con todas) */
      var aparte = {};
      var host = location.hostname.replace(/^www\./, '');
      function separadas(a, b) { return (aparte[a] || []).indexOf(b) >= 0 || (aparte[b] || []).indexOf(a) >= 0; }
      webs = webs.filter(function (d) { return d === host || !separadas(host, d); });
      var l = (document.documentElement.lang || 'es').slice(0, 2).toLowerCase();
      var tit = {es: 'Webs hermanas', en: 'Sister sites', ca: 'Webs germanes', fr: 'Sites frères', it: 'Siti fratelli'}[l] || 'Webs hermanas';
      /* quita las menciones parciales que ya hubiera en el pie */
      Array.prototype.forEach.call(f.querySelectorAll('p:not(.familia):not(.webs-hermanas) a[href]'), function (a) {
        var d = (a.hostname || '').replace(/^www\./, '');
        if (webs.indexOf(d) < 0 || d === host) return;
        var p = a.previousSibling;
        if (p && p.nodeType === 3) p.nodeValue = p.nodeValue.replace(/\s*·\s*$/, ' ').replace(/(Webs hermanas|Sister sites|Webs germanes|Webs germans):\s*$/, '');
        a.parentNode.removeChild(a);
      });
      Array.prototype.forEach.call(f.querySelectorAll('p:not(.familia):not(.webs-hermanas)'), function (p) {
        if (!/hermanas|Sister sites|germanes|germans|·\s*·|·\s*$/.test(p.innerHTML)) return;
        p.innerHTML = p.innerHTML.replace(/(Webs hermanas|Sister sites|Webs germanes|Webs germans):\s*(·\s*)?/, '').replace(/(\s*·\s*)+$/, '').replace(/·(\s*·)+/g, '·');
      });
      var html = webs.map(function (d) {
        if (d === host) return '<strong>' + d + '</strong>';
        var s = l === 'en' && conEn.indexOf(d) >= 0 ? 'en/' : (l === 'ca' && d === 'medicapedia.org' ? 'ca/' : '');
        return '<a href="https://' + d + '/' + s + '">' + d + '</a>';
      }).join(' · ');
      /* si la página ya trae la línea (newtonpedia la lleva fija en el HTML), se actualiza */
      /* clase propia «webs-hermanas»: «familia» choca con otros estilos (familias de instrumentos en classicapedia) */
      var p = f.querySelector('.webs-hermanas, p.familia');
      if (p) p.className = 'webs-hermanas';
      else {
        p = document.createElement('p'); p.className = 'webs-hermanas';
        var dentro = f.querySelector('.contenedor') || f;
        if (!dentro.querySelector('p')) p.style.margin = '.8em 0 0';
        dentro.appendChild(p);
      }
      p.innerHTML = tit + ': ' + html;
    } catch (e) {}
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', poner); else poner();
})();

/* WorldWinePedia (2026-11-08): enlace a la ficha de vino equivalente y línea en el pie. Bloque propio de culinapedia, independiente del bloque de webs hermanas. */
(function () {
  function wwp() {
    try {
      var M = {"v/cabernet-sauvignon.html":"g:cabernet-sauvignon","v/pinot-noir.html":"g:pinot-noir","v/chardonnay.html":"g:chardonnay","v/sauvignon-blanc.html":"g:sauvignon-blanc","v/riesling.html":"g:riesling","v/merlot.html":"g:merlot","v/syrah.html":"g:syrah","v/gewurztraminer.html":"g:gewurztraminer","v/pinot-gris.html":"g:pinot-gris","v/cabernet-franc.html":"g:cabernet-franc","v/garnacha.html":"g:garnacha","v/zinfandel.html":"g:primitivo","v/tempranillo.html":"g:tempranillo","v/chenin-blanc.html":"g:chenin-blanc","v/nebbiolo.html":"g:nebbiolo","v/silvaner.html":"g:silvaner","v/gruner-veltliner.html":"g:gruner-veltliner","v/muller-thurgau.html":"g:muller-thurgau","v/gamay.html":"g:gamay","v/malbec.html":"g:malbec","v/semillon.html":"g:semillon","v/sangiovese.html":"g:sangiovese","v/carinena.html":"g:carinena","v/carmenere.html":"g:carmenere","v/trebbiano.html":"g:trebbiano","v/barbera.html":"g:barbera","v/albarino.html":"g:albarino","v/petit-verdot.html":"g:petit-verdot","v/viognier.html":"g:viognier","v/corvina.html":"g:corvina","v/monastrell.html":"g:monastrell","v/nero-d-avola.html":"g:nero-davola","v/aligote.html":"g:aligote","v/cinsault.html":"g:cinsault","v/aglianico.html":"g:aglianico","v/pinotage.html":"g:pinotage","v/moscatel-de-alejandria.html":"g:moscatel","v/zweigelt.html":"g:zweigelt","v/macabeo.html":"g:macabeo","v/garnacha-tintorera.html":"g:alicante-bouschet","v/blaufrankisch.html":"g:blaufrankisch","v/palomino.html":"g:palomino","v/vermentino.html":"g:vermentino","v/dolcetto.html":"g:dolcetto","v/garganega.html":"g:garganega","v/pedro-ximenez.html":"g:pedro-ximenez","v/torrontes.html":"g:torrontes","v/xarello.html":"g:xarel-lo","v/airen.html":"g:airen","v/bobal.html":"g:bobal","v/mencia.html":"g:mencia","v/graciano.html":"g:graciano","v/garnacha-blanca.html":"g:garnacha-blanca","v/verdejo.html":"g:verdejo","v/sercial.html":"g:sercial","v/durif.html":"g:petite-sirah","v/melon-de-borgona.html":"g:melon-de-bourgogne","v/parellada.html":"g:parellada","v/touriga-nacional.html":"g:touriga-nacional","v/glera.html":"g:glera","v/montepulciano.html":"g:montepulciano","v/loureira.html":"g:loureira","v/fiano.html":"g:fiano","v/treixadura.html":"g:treixadura","v/arinto.html":"g:arinto","v/prieto-picudo.html":"g:prieto-picudo","v/touriga-franca.html":"g:touriga-franca","v/verdelho.html":"g:verdelho","v/listan-negro.html":"g:listan-negro","v/hondarrabi-zuri-courbu-blanc.html":"g:hondarrabi-zuri","v/bonarda-douce-noir.html":"g:bonarda","v/godello.html":"g:godello","v/pais.html":"g:pais","v/baga.html":"g:baga","v/castelao.html":"g:castelao","v/nerello-mascalese.html":"g:nerello-mascalese","v/vino-de-oporto.html":"r:porto","v/jerez.html":"r:jerez-xeres-sherry","v/madeira.html":"r:madeira","v/vinedo-de-burdeos.html":"r:bordeaux","v/vinos-de-borgona.html":"r:bourgogne","v/alto-duero.html":"r:douro","v/valle-de-napa.html":"r:napa-valley","v/rioja.html":"r:rioja","v/vinho-verde.html":"r:vinho-verde","v/champana.html":"r:champagne","v/valpolicella.html":"r:valpolicella","v/vinedo-de-alsacia.html":"r:alsace","v/mosel.html":"r:mosel","v/franciacorta.html":"r:franciacorta","v/valle-del-loira.html":"r:loire","v/rheingau.html":"r:rheingau","v/ribera-del-duero.html":"r:ribera-del-duero","v/vinos-del-languedoc-rosellon.html":"r:languedoc-roussillon","v/baden.html":"r:baden","v/priorato.html":"r:priorat","v/d-o-somontano.html":"r:somontano","v/cote-de-nuits.html":"r:cote-de-nuits","v/rheinhessen-renania-hesse.html":"r:rheinhessen","v/cote-de-beaune.html":"r:cote-de-beaune","v/dao.html":"r:dao","v/franconia-franconia.html":"r:franken","v/region-vinicola-del-nahe.html":"r:nahe","v/bierzo.html":"r:bierzo","v/carinena-q2832748.html":"r:carinena","v/palatinado.html":"r:pfalz","v/alentejo-doc.html":"r:alentejo","v/bairrada.html":"r:bairrada","v/d-o-calatayud.html":"r:calatayud","v/campo-de-borja.html":"r:campo-de-borja","v/valle-de-sonoma.html":"r:sonoma","v/valle-de-clare.html":"r:clare-valley","v/region-viticola-de-aconcagua.html":"r:aconcagua","v/barossa-valley.html":"r:barossa-valley","v/columbia-valley.html":"r:columbia-valley","v/central-otago.html":"r:central-otago","v/alto-adigio-sudtirol.html":"r:trentino-alto-adige","v/region-vinicola-de-marlborough.html":"r:marlborough","v/margaret-river.html":"r:margaret-river","v/valle-de-willamette.html":"r:willamette-valley","v/lisboa.html":"r:lisboa","v/peninsula-de-setubal.html":"r:setubal","v/paso-robles.html":"r:paso-robles","v/veuve-clicquot.html":"w:veuve-clicquot","v/chateau-d-yquem.html":"w:chateau-d-yquem","v/concha-y-toro.html":"w:concha-y-toro","v/vega-sicilia.html":"w:vega-sicilia","v/louis-roederer.html":"w:louis-roederer","v/maison-louis-jadot.html":"w:louis-jadot","v/chateau-margaux.html":"w:chateau-margaux","v/gramona.html":"w:gramona","v/chapoutier.html":"w:m-chapoutier","v/domaine-faiveley.html":"w:domaine-faiveley","v/chateau-haut-brion.html":"w:chateau-haut-brion","v/jose-maria-da-fonseca.html":"w:jose-maria-da-fonseca","v/maison-trimbach.html":"w:trimbach","v/chateau-cheval-blanc.html":"w:chateau-cheval-blanc","v/sogrape.html":"w:sogrape","v/cavas-codorniu.html":"w:codorniu","v/chateau-lynch-bages.html":"w:chateau-lynch-bages","v/cloudy-bay-vineyards.html":"w:cloudy-bay","v/opus-one.html":"w:opus-one","v/maison-joseph-drouhin.html":"w:joseph-drouhin","v/guigal.html":"w:e-guigal","v/marchesi-antinori.html":"w:antinori","v/ornellaia-e-masseto.html":"w:ornellaia","v/stag-s-leap-wine-cellars.html":"w:stags-leap-wine-cellars","v/moscatel-de-grano-menudo.html":"g:moscatel","v/pigato.html":"g:vermentino","v/douro-doc-douro.html":"r:douro","v/vinos-del-mosela.html":"r:mosel"};
      var SEG = {"es":{"g":"uvas","r":"regiones","w":"bodegas"},"en":{"g":"grapes","r":"regions","w":"wineries"}};
      var l = (document.documentElement.lang || 'es').slice(0, 2).toLowerCase() === 'en' ? 'en' : 'es';
      var base = 'https://worldwinepedia.com/' + l + '/';
      var path = location.pathname.replace(/^\/+/, '').replace(/^en\//, '');
      var t = l === 'en'
        ? {h: 'Buy it and taste it', p: 'Tasting notes, food pairing and where to buy on WorldWinePedia', f: 'World wines', v: 'Wine profiles, tasting notes and where to buy them: '}
        : {h: 'Dónde comprar y catar', p: 'Fichas de cata, maridaje y dónde comprar en WorldWinePedia', f: 'Vinos del mundo', v: 'Fichas de vinos, notas de cata y dónde comprarlos: '};
      var c = M[path];
      if (c) {
        var k = c.split(':');
        var aside = document.querySelector('.ficha aside') || document.querySelector('aside');
        if (aside && !document.getElementById('wwp-caja')) {
          var d = document.createElement('div'); d.className = 'caja'; d.id = 'wwp-caja';
          d.innerHTML = '<h3>' + t.h + '</h3><a href="' + base + SEG[l][k[0]] + '/' + k[1] + '/" style="display:block;padding:3px 0">' + t.p + ' \u2197</a>';
          aside.appendChild(d);
        }
      }
      if (/^(vinos|uvas|regiones-vino|bodegas)(-\d+)?\.html$/.test(path)) {
        var h1 = document.querySelector('main h1');
        if (h1 && !document.getElementById('wwp-intro')) {
          var q = document.createElement('p'); q.id = 'wwp-intro';
          q.innerHTML = t.v + '<a href="' + base + '">WorldWinePedia</a>.';
          h1.parentNode.insertBefore(q, h1.nextSibling);
        }
      }
      var f = document.querySelector('footer.pie');
      if (f && !document.getElementById('wwp-pie')) {
        var p = document.createElement('p'); p.id = 'wwp-pie';
        p.innerHTML = t.f + ': <a href="' + base + '">worldwinepedia.com</a>';
        f.appendChild(p);
      }
    } catch (e) {}
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wwp); else wwp();
})();
