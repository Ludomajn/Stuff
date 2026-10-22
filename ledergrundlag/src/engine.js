// Fælles tidslinje-motor: deterministisk renderAt(t) til video + live-præsentation med tastaturstyring.
(function () {
  const E = window.E = {};
  E.W = 1920; E.H = 1080; E.TAU = Math.PI * 2;
  E.G = { alpha: 1 };
  E.clock = 0;

  E.clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  E.prog = (t, s, d) => E.clamp((t - s) / d);
  E.lerp = (a, b, p) => a + (b - a) * p;
  E.eo = x => 1 - Math.pow(1 - x, 3);
  E.eio = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  E.eback = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  E.rng = function (seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  };
  const hex = h => { const n = parseInt(h.slice(1), 16); return [n >> 16, (n >> 8) & 255, n & 255]; };
  E.rgba = (h, a) => { const [r, g, b] = hex(h); return `rgba(${r},${g},${b},${a})`; };
  E.mix = (h1, h2, p) => {
    const a = hex(h1), b = hex(h2);
    return '#' + a.map((v, i) => Math.round(E.lerp(v, b[i], E.clamp(p))).toString(16).padStart(2, '0')).join('');
  };
  E.mk = function (p, cls = '', css = '', html = '') {
    const d = document.createElement('div');
    if (cls) d.className = cls; if (css) d.style.cssText = css; if (html) d.innerHTML = html;
    p.appendChild(d); return d;
  };
  const NS = 'http://www.w3.org/2000/svg';
  E.svg = function (p, tag, attrs) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    p.appendChild(e); return e;
  };

  E.run = function (o) {
    const { scenes, stage } = o, layer = o.layer || stage, ctx = o.ctx || null;
    const W = E.W, H = E.H, clamp = E.clamp;
    scenes.forEach(s => { if (s.fadeIn == null) s.fadeIn = .5; if (s.fadeOut == null) s.fadeOut = .5; });
    const starts = []; let total = 0;
    scenes.forEach(s => { starts.push(total); total += s.dur; });
    window.TOTAL = total;
    const capture = E.capture = new URLSearchParams(location.search).has('capture');

    function fit() {
      const k = Math.min(innerWidth / W, innerHeight / H);
      stage.style.transform = capture ? 'none' : `scale(${k})`;
    }
    addEventListener('resize', fit); fit();

    let shown = -1;
    function draw(i, lt, out) {
      const sc = scenes[i];
      if (shown !== i) { scenes.forEach((s, k) => s.el.style.display = k === i ? 'block' : 'none'); shown = i; }
      let a = sc.fadeIn ? clamp(lt / sc.fadeIn) : 1;
      if (!sc.customOut && sc.fadeOut) a *= 1 - out;
      if (ctx) { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.clearRect(0, 0, W, H); }
      E.G.alpha = a;
      if (o.before) o.before(i, lt, out, a);
      E.G.alpha = a; sc.el.style.opacity = a;
      sc.render(lt, sc.s, out);
    }

    window.renderAt = function (t) {
      let i = scenes.length - 1;
      while (i > 0 && starts[i] > t) i--;
      const sc = scenes[i], lt = t - starts[i];
      E.clock = t;
      draw(i, lt, sc.fadeOut ? clamp((lt - (sc.dur - sc.fadeOut)) / sc.fadeOut) : 0);
    };

    Promise.all([...document.fonts].map(f => f.load().catch(() => {}))).then(() => document.fonts.ready).then(() => {
      scenes.forEach(sc => { sc.el = E.mk(layer, 'scene'); sc.s = sc.build(sc.el); });
      if (o.onBuilt) o.onBuilt();
      window.__ready = true;
      if (!capture) (o.audio ? player : live)();
    });

    // Afspiller: tidslinjen følger lydsporet (stemme + musik)
    function player() {
      const a = new Audio(o.audio);
      const ov = E.mk(document.body, '', 'position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.55);color:#fff;font:600 30px -apple-system,"Helvetica Neue",sans-serif;cursor:pointer;z-index:10', '▶&nbsp; Klik for at afspille');
      const toggle = () => { if (a.paused) { a.play(); ov.style.display = 'none'; } else { a.pause(); ov.innerHTML = '❚❚&nbsp; Pause – klik for at fortsætte'; ov.style.display = 'flex'; } };
      ov.addEventListener('click', toggle);
      a.addEventListener('ended', () => { ov.innerHTML = '↺&nbsp; Afspil igen'; ov.style.display = 'flex'; });
      addEventListener('keydown', e => {
        if (e.key === ' ') { e.preventDefault(); toggle(); }
        else if (e.key === 'ArrowRight') a.currentTime = Math.min(a.duration || total, a.currentTime + 5);
        else if (e.key === 'ArrowLeft') a.currentTime = Math.max(0, a.currentTime - 5);
        else if (e.key === 'f' || e.key === 'F') document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
      });
      (function frame() { window.renderAt(a.currentTime); requestAnimationFrame(frame); })();
    }

    // Live: hver scene spiller og holder sit slutbillede, til du går videre
    function live() {
      const hint = E.mk(document.body, '', 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);font:500 14px/1.4 -apple-system,"Helvetica Neue",sans-serif;color:#fff;background:rgba(0,0,0,.5);padding:8px 14px;border-radius:999px;transition:opacity .8s;pointer-events:none;white-space:nowrap;z-index:10',
        '→ / mellemrum / klik: næste · ← forrige · A: autoplay · F: fuldskærm');
      setTimeout(() => hint.style.opacity = 0, 5000);
      let idx = 0, t0 = performance.now(), leaving = null, auto = false;
      const go = k => { idx = clamp(k, 0, scenes.length - 1); t0 = performance.now(); leaving = null; };
      const next = () => {
        if (leaving !== null) return go(idx + 1);
        if (idx >= scenes.length - 1) return;
        if (scenes[idx].fadeOut) leaving = performance.now(); else go(idx + 1);
      };
      addEventListener('keydown', e => {
        if (['ArrowRight', ' ', 'PageDown', 'Enter'].includes(e.key)) { e.preventDefault(); next(); }
        else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); go(idx - 1); }
        else if (e.key === 'Home') go(0);
        else if (e.key === 'a' || e.key === 'A') {
          auto = !auto; hint.textContent = auto ? 'Autoplay: til' : 'Autoplay: fra';
          hint.style.opacity = 1; setTimeout(() => hint.style.opacity = 0, 1500);
        }
        else if (e.key === 'f' || e.key === 'F') document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
      });
      addEventListener('click', next);
      (function frame(now) {
        const sc = scenes[idx], lt = (now - t0) / 1000;
        E.clock = now / 1000;
        if (auto && leaving === null && lt >= sc.dur - sc.fadeOut) next();
        let out = 0;
        if (leaving !== null) {
          out = (now - leaving) / 1000 / scenes[idx].fadeOut;
          if (out >= 1) { go(idx + 1); return requestAnimationFrame(frame); }
        }
        draw(idx, (now - t0) / 1000, out);
        requestAnimationFrame(frame);
      })(performance.now());
    }
  };
})();
