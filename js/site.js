(function () {
  var W = window.WWP || {};
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  document.querySelectorAll('a[hreflang]').forEach(function (a) { a.addEventListener('click', function () { set('wwp-lang', a.getAttribute('hreflang')); }); });
  // ---- Age gate ----
  var gate = document.getElementById('agegate');
  if (gate && get('wwp-age') !== 'ok') {
    gate.style.display = 'flex';
    gate.querySelector('.yes').addEventListener('click', function () { set('wwp-age', 'ok'); gate.style.display = 'none'; });
    gate.querySelector('.no').addEventListener('click', function () { gate.querySelector('.in').innerHTML = '<h2>' + W.t.age_bye + '</h2>'; });
  }

  // ---- Ship-to country ----
  function guessShip() {
    var l = (navigator.language || '').toUpperCase();
    var m = l.split('-')[1] || '';
    if (m === 'GB') m = 'UK';
    var known = ['ES', 'FR', 'IT', 'DE', 'UK', 'US'];
    if (known.indexOf(m) >= 0) return m;
    var byLang = { ES: 'ES', FR: 'FR', IT: 'IT', DE: 'DE' };
    return byLang[l.split('-')[0]] || 'XX';
  }
  var ship = get('wwp-ship') || guessShip();
  var selects = document.querySelectorAll('select.ship');
  function setShip(v) {
    ship = v; set('wwp-ship', v);
    selects.forEach(function (s) { s.value = v; });
    renderBuy();
  }
  selects.forEach(function (s) { s.value = ship; s.addEventListener('change', function () { setShip(s.value); }); });

  // ---- Buy box ----
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function renderBuy() {
    document.querySelectorAll('.shops').forEach(function (box) {
      var q = box.getAttribute('data-q');
      var st = W.stores, html = '', notes = '';
      var a = st.amazon[ship];
      if (a) {
        var url = 'https://' + a.domain + '/s?k=' + encodeURIComponent(q) + (a.tag ? '&tag=' + a.tag : '');
        html += '<div class="shop"><strong>' + esc(a.name) + '</strong><a rel="sponsored nofollow noopener" target="_blank" href="' + esc(url) + '">' + W.t.see_price + ' ↗</a></div>';
      }
      (st.shops || []).forEach(function (s) {
        if (s.countries.indexOf(ship) >= 0) {
          html += '<div class="shop"><strong>' + esc(s.name) + '</strong><a rel="sponsored nofollow noopener" target="_blank" href="' + esc(s.url.replace('{q}', encodeURIComponent(q))) + '">' + W.t.see_price + ' ↗</a></div>';
        }
      });
      var c = st.comparator;
      html += '<div class="shop"><strong>' + esc(c.name) + '</strong><a rel="nofollow noopener" target="_blank" href="' + esc(c.url.replace('{q}', encodeURIComponent(q).replace(/%20/g, '+'))) + '">' + W.t.compare_world + ' ↗</a></div>';
      if (ship === 'US') notes += '<p class="note">' + W.t.us_note + '</p>';
      if (ship === 'FR') notes += '<p class="note">' + W.t.fr_note + '</p>';
      box.innerHTML = notes + html;
    });
  }
  renderBuy();

  // ---- List filters (type pills, text, region select) ----
  document.querySelectorAll('[data-filter-scope]').forEach(function (scope) {
    var items = scope.querySelectorAll('[data-item]');
    var pills = scope.querySelectorAll('.pill[data-type]');
    var txt = scope.querySelector('input.ftext');
    var reg = scope.querySelector('select.freg');
    var count = scope.querySelector('.fcount');
    var cur = 'all';
    function apply() {
      var q = txt ? txt.value.trim().toLowerCase() : '';
      var r = reg ? reg.value : '';
      var n = 0;
      items.forEach(function (it) {
        var ok = (cur === 'all' || it.getAttribute('data-type') === cur) &&
          (!q || it.getAttribute('data-text').indexOf(q) >= 0) &&
          (!r || it.getAttribute('data-region') === r);
        it.style.display = ok ? '' : 'none'; if (ok) n++;
      });
      if (count) count.textContent = n;
    }
    pills.forEach(function (p) {
      p.addEventListener('click', function () {
        pills.forEach(function (x) { x.classList.remove('active'); x.setAttribute('aria-pressed', 'false'); });
        p.classList.add('active'); p.setAttribute('aria-pressed', 'true'); cur = p.getAttribute('data-type'); apply();
      });
    });
    if (txt) txt.addEventListener('input', apply);
    if (reg) reg.addEventListener('change', apply);
    apply();
  });

  // ---- Site search ----
  var sr = document.getElementById('searchres');
  if (sr) {
    var params = new URLSearchParams(location.search);
    var q0 = (params.get('q') || '').trim();
    var input = document.getElementById('sq');
    if (input) input.value = q0;
    fetch(W.root + W.base + 'search.json').then(function (r) { return r.json(); }).then(function (idx) {
      function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
      function run(q) {
        q = norm(q);
        if (!q) { sr.innerHTML = ''; return; }
        var words = q.split(/\s+/);
        var res = idx.filter(function (e) { var t = norm(e.t + ' ' + e.k); return words.every(function (w) { return t.indexOf(w) >= 0; }); });
        sr.innerHTML = '<p>' + res.length + ' ' + W.t.results + '</p>' + (res.length ? res.slice(0, 200).map(function (e) {
          var u = W.root + e.u.slice(1); if (W.preview) u = u.replace(/\/(#|$)/, '/index.html$1'); return '<a href="' + u + '">' + esc(e.t) + '<small>' + esc(e.c) + '</small></a>';
        }).join('') : '<p>' + W.t.no_results + '</p>');
      }
      run(q0);
      if (input) input.addEventListener('input', function () { run(input.value); });
    });
  }
})();
