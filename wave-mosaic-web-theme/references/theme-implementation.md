# Wave Mosaic Theme Implementation

这个 reference 保存可复制的完整实现。替换页面内容即可复刻同一套动态背景和 4 种背景颜色。

## HTML Head

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" onload="this.onload=null;this.rel='stylesheet'">
<noscript>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap">
</noscript>
<link rel="icon" type="image/svg+xml" href="assets/rocket.svg">
<meta name="theme-color" content="#ffffff">
```

## CSS

```css
:root {
  --bg:              #ffffff;
  --masthead-bg:     #f5f5f5;
  --masthead-border: #e8e8e8;
  --paper-border:    #efefef;
  --paper-hover:     #f7f7f7;
  --h1-border:       #e8e8e8;
  --c-bg-start:      #ffffff;
  --c-bg-end:        #f5f5f5;
  --c-border:        rgba(0, 0, 0, 0.12);
  --c-text:          #1a1a1a;
  --c-hover-start:   #f0f0f0;
  --c-hover-end:     #e8e8e8;
  --c-hover-border:  rgba(0, 0, 0, 0.28);
  --c-hover-text:    #000000;
  --seg-start:       #1a1a1a;
  --seg-end:         #333333;
  --seg-shadow:      rgba(0, 0, 0, 0.22);
  --seg-inactive:    #888888;
  --seg-active-text: #ffffff;
  --glow-rgb:        0, 0, 0;
}

[data-theme="yellow"] {
  --bg:              #faf8f4;
  --masthead-bg:     #f0ebe1;
  --masthead-border: #e5ddd0;
  --paper-border:    #e8e0d5;
  --paper-hover:     #f0ece4;
  --h1-border:       #ddd6c8;
  --c-bg-start:      #ffffff;
  --c-bg-end:        #faf4ea;
  --c-border:        rgba(140, 95, 35, 0.22);
  --c-text:          #3d2810;
  --c-hover-start:   #f5ede0;
  --c-hover-end:     #ede0cc;
  --c-hover-border:  rgba(140, 95, 35, 0.5);
  --c-hover-text:    #1c1208;
  --seg-start:       #1c1208;
  --seg-end:         #3a2410;
  --seg-shadow:      rgba(28, 18, 8, 0.28);
  --seg-inactive:    #8a7055;
  --seg-active-text: #ffffff;
  --glow-rgb:        180, 128, 40;
}

[data-theme="blue"] {
  --bg:              #f3f5f8;
  --masthead-bg:     #e3e8ef;
  --masthead-border: #d3dae3;
  --paper-border:    #dde4ed;
  --paper-hover:     #e8eef5;
  --h1-border:       #ccd4de;
  --c-bg-start:      #ffffff;
  --c-bg-end:        #edf2fa;
  --c-border:        rgba(38, 88, 155, 0.22);
  --c-text:          #1a3654;
  --c-hover-start:   #e8f0fb;
  --c-hover-end:     #d8e8f8;
  --c-hover-border:  rgba(38, 88, 155, 0.5);
  --c-hover-text:    #102847;
  --seg-start:       #1a3654;
  --seg-end:         #1e4a7a;
  --seg-shadow:      rgba(26, 54, 84, 0.3);
  --seg-inactive:    #6a8aaa;
  --seg-active-text: #ffffff;
  --glow-rgb:        38, 88, 155;
}

[data-theme="dark"] {
  --bg:              #111110;
  --masthead-bg:     #1c1c1a;
  --masthead-border: #2e2e2b;
  --paper-border:    #252522;
  --paper-hover:     #1a1a18;
  --h1-border:       #2e2e2b;
  --c-bg-start:      #1e1e1c;
  --c-bg-end:        #252520;
  --c-border:        rgba(255, 255, 255, 0.1);
  --c-text:          #e8e6df;
  --c-hover-start:   #2a2a26;
  --c-hover-end:     #303028;
  --c-hover-border:  rgba(255, 255, 255, 0.22);
  --c-hover-text:    #ffffff;
  --seg-start:       #e8e6df;
  --seg-end:         #d0cec7;
  --seg-shadow:      rgba(232, 230, 223, 0.12);
  --seg-inactive:    #666660;
  --seg-active-text: #111110;
  --glow-rgb:        220, 210, 180;
}

html {
  min-height: 100%;
  background-color: var(--bg);
  color: var(--c-text);
  font-family: "Space Grotesk", "Noto Sans SC", Inter, ui-sans-serif, system-ui, sans-serif;
}

body {
  min-height: 100vh;
  margin: 0;
  background: transparent;
}

.wm-page {
  position: relative;
  z-index: 1;
}

.wm-panel {
  border: 1px solid var(--c-border);
  border-radius: 16px;
  background: linear-gradient(135deg, var(--c-bg-start) 0%, var(--c-bg-end) 100%);
  box-shadow: 0 18px 55px rgba(0, 0, 0, 0.08);
}

.wm-card {
  border: 1.5px solid var(--c-border);
  border-radius: 12px;
  background: linear-gradient(135deg, var(--c-bg-start) 0%, var(--c-bg-end) 100%);
  color: var(--c-text);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.wm-card:hover {
  transform: translateY(-2px);
  border-color: var(--c-hover-border);
  background: linear-gradient(135deg, var(--c-hover-start) 0%, var(--c-hover-end) 100%);
  box-shadow: 0 8px 26px rgba(var(--glow-rgb), 0.12);
}

#theme-switcher {
  position: fixed;
  bottom: 1.5em;
  right: 1.5em;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--masthead-bg);
  border: 1px solid var(--masthead-border);
  border-radius: 9999px;
  padding: 9px 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transition: background 0.3s ease, border-color 0.3s ease;
}

.theme-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  padding: 0;
  flex-shrink: 0;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.theme-dot[data-theme="white"]  { background: #ffffff; border-color: #c8c8c8; }
.theme-dot[data-theme="yellow"] { background: #e8d5a0; border-color: #c4a060; }
.theme-dot[data-theme="blue"]   { background: #a8c4e8; border-color: #5e8ec8; }
.theme-dot[data-theme="dark"]   { background: #2a2a26; border-color: #585852; }

.theme-dot.active {
  transform: scale(1.35);
  box-shadow: 0 0 0 2px var(--bg), 0 0 0 3.5px var(--masthead-border);
}

.theme-dot:hover:not(.active) {
  transform: scale(1.18);
}

[data-theme="dark"] {
  color-scheme: dark;
}
```

## JavaScript

```html
<script>
(function () {
  var canvas, ctx, t = 0;
  var TILE = 26, GAP = 1;
  var rafId = null;
  var cachedRgb = '10,10,10';
  var lastDraw = 0;
  var FRAME_MS = 1000 / 24;

  function rgb() {
    var th = document.documentElement.getAttribute('data-theme') || 'white';
    if (th === 'dark')   return '220,210,175';
    if (th === 'yellow') return '120,85,20';
    if (th === 'blue')   return '38,88,155';
    return '10,10,10';
  }

  function frame(ts) {
    rafId = requestAnimationFrame(frame);
    if (ts - lastDraw < FRAME_MS) return;
    lastDraw = ts;

    var w = canvas.width, h = canvas.height;
    var cols = Math.ceil(w / TILE) + 1;
    var rows = Math.ceil(h / TILE) + 1;
    var pre  = 'rgba(' + cachedRgb + ',';

    ctx.clearRect(0, 0, w, h);

    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        var wave = 0.6 * Math.sin(c * 0.21 + t * 0.36) * Math.sin(r * 0.17 + t * 0.28)
                 + 0.4 * Math.sin(c * 0.11 - r * 0.13 + t * 0.19);
        var norm = (wave + 1) * 0.5;
        var v = norm * norm * norm;
        var a = Math.round((0.004 + v * 0.186) * 100) / 100;
        if (a < 0.02) continue;
        ctx.fillStyle = pre + a + ')';
        ctx.fillRect(c * TILE + GAP, r * TILE + GAP, TILE - GAP, TILE - GAP);
      }
    }

    t += 0.007;
  }

  var resizeTimer;
  function resize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      var newW = window.innerWidth;
      var newH = window.innerHeight;
      if (newW === canvas.width && Math.abs(newH - canvas.height) <= 90) return;
      canvas.width = newW;
      canvas.height = newH;
    }, 120);
  }

  function onVisibilityChange() {
    if (document.hidden) {
      if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    } else {
      if (!rafId) rafId = requestAnimationFrame(frame);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;' +
      'z-index:0;pointer-events:none;will-change:transform;' +
      '-webkit-backface-visibility:hidden;backface-visibility:hidden;';
    document.body.insertBefore(canvas, document.body.firstChild);
    ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    cachedRgb = rgb();
    window.addEventListener('resize', resize);
    document.addEventListener('visibilitychange', onVisibilityChange);
    rafId = requestAnimationFrame(frame);
  });

  new MutationObserver(function () { cachedRgb = rgb(); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
})();

(function () {
  var THEMES = ['white', 'yellow', 'blue', 'dark'];
  var LABELS = { white: 'Pure White', yellow: 'Warm Yellow', blue: 'Cool Blue', dark: 'Dark' };
  var STORAGE_KEY = 'site-theme';

  function applyTheme(theme) {
    if (theme === 'white') {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', theme);
    }
    try { localStorage.setItem(STORAGE_KEY, theme); } catch(e) {}
    document.querySelectorAll('.theme-dot').forEach(function (dot) {
      dot.classList.toggle('active', dot.dataset.theme === theme);
    });
  }

  var saved = 'white';
  try { saved = localStorage.getItem(STORAGE_KEY) || 'white'; } catch(e) {}
  applyTheme(saved);

  document.addEventListener('DOMContentLoaded', function () {
    var switcher = document.createElement('div');
    switcher.id = 'theme-switcher';
    switcher.setAttribute('aria-label', 'Choose colour theme');
    THEMES.forEach(function (theme) {
      var btn = document.createElement('button');
      btn.className = 'theme-dot';
      btn.dataset.theme = theme;
      btn.title = LABELS[theme];
      btn.setAttribute('aria-label', LABELS[theme]);
      btn.addEventListener('click', function () { applyTheme(theme); });
      switcher.appendChild(btn);
    });
    document.body.appendChild(switcher);
    applyTheme(saved);
  });
})();
</script>
```
