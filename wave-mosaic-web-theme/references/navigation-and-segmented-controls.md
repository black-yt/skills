# Navigation And Segmented Controls

这个 reference 记录从 [black-yt/black-yt.github.io](https://github.com/black-yt/black-yt.github.io) 当前设计中抽取出的两个高复用组件。源站后续可能更新，下面的代码应视为可复刻的稳定模式，而不是对源站未来文件结构的固定声明：

- 顶部圆角导航栏：居中、横向滚动、当前章节高亮、点击锚点跳转、active link 自动滚入视野。
- 论文筛选滑块：用于在 `Core Papers` 和 `Collaboration Papers` 之间切换，也可扩展成任意 segmented filter。

这两个组件都依赖 `SKILL.md` 中的主题变量：`--masthead-bg`、`--masthead-border`、`--c-border`、`--c-text`、`--seg-start`、`--seg-end`、`--seg-shadow`、`--seg-inactive`、`--seg-active-text`、`--glow-rgb`。

## 源码追溯入口

下面是当前版本的源码追溯入口。若源站后续重构文件结构，优先搜索表中的 class、函数名和关键词，而不是假设路径永久不变。

| 组件 | 当前源站入口 | 复刻时关注点 |
| --- | --- | --- |
| 顶部导航 HTML | `_includes/masthead.html`、`_data/navigation.yml` | `<nav class="site-nav">`、`ul.site-nav__links`、锚点链接列表 |
| 顶部导航样式 | `assets/css/main.scss`、`_sass/_config.scss` | `.masthead`、`.site-nav`、`.site-nav__link`、`$nav-font-size: 21px`、`$nav-link-padding: 0.1em 0.6em` |
| 顶部导航行为 | `assets/js/custom-scripts.js` | scroll-spy、点击后立即 active、横向导航自动滚入 active link |
| 论文滑块 HTML | `_pages/includes/pub.md` | `.seg-control`、`.seg-indicator`、`.seg-btn`、论文卡片 `data-*` 标记 |
| 论文滑块样式 | `assets/css/main.scss` | segmented control 背景、边框、indicator 动画、active/inactive 文字颜色 |
| 论文滑块行为 | `assets/js/custom-scripts.js` | `moveSegIndicator(...)`、初始化 indicator、点击筛选论文卡片 |

## 顶部导航栏

设计要点：

- 顶部栏使用 `var(--masthead-bg)` 和 `var(--masthead-border)`，跟随 4 种背景颜色切换。
- 导航链接是轻量圆角 tab，不使用重按钮质感。
- 桌面端居中；窄屏时只让 `.wm-site-nav` 横向滚动，不让整个页面横向溢出。
- hover 和 focus 只用低透明主题色背景，不使用强色块。
- active 状态使用 `.nav-active`，背景为 `rgba(var(--glow-rgb), 0.13)`。
- 点击锚点后立即高亮，并短暂抑制 scroll-spy，避免点击动画过程中 active 状态来回跳。
- 滚动页面时用 `requestAnimationFrame` 节流，按 `offset = 80` 判断当前章节。

### HTML

```html
<header class="wm-masthead">
  <div class="wm-masthead__inner">
    <nav class="wm-site-nav" aria-label="Primary navigation">
      <ul class="wm-site-nav__links">
        <li><a class="wm-site-nav__link" href="#about">About</a></li>
        <li><a class="wm-site-nav__link" href="#news">News</a></li>
        <li><a class="wm-site-nav__link" href="#publications">Publications</a></li>
        <li><a class="wm-site-nav__link" href="#honors">Honors</a></li>
        <li><a class="wm-site-nav__link" href="#talks">Talks</a></li>
        <li><a class="wm-site-nav__link" href="#services">Services</a></li>
      </ul>
    </nav>
  </div>
</header>

<main class="wm-page">
  <section id="about">...</section>
  <section id="news">...</section>
  <section id="publications">...</section>
  <section id="honors">...</section>
  <section id="talks">...</section>
  <section id="services">...</section>
</main>
```

### CSS

```css
.wm-masthead {
  position: sticky;
  top: 0;
  z-index: 900;
  width: 100%;
  background-color: var(--masthead-bg);
  border-bottom: 1px solid var(--masthead-border);
  transition: background-color 0.25s ease, border-color 0.25s ease;
}

.wm-masthead__inner {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.wm-site-nav {
  width: 100%;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.wm-site-nav::-webkit-scrollbar {
  display: none;
}

.wm-site-nav__links {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  width: max-content;
  min-width: 100%;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 6px 8px;
  gap: 4px;
  list-style: none;
}

.wm-site-nav__link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.1em 0.6em;
  border-radius: 7px;
  color: inherit;
  font-family: "Space Grotesk", "Noto Sans SC", Inter, ui-sans-serif, system-ui, sans-serif;
  font-size: 21px;
  font-weight: 400;
  line-height: 1.45;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.wm-site-nav__link.nav-active {
  background: rgba(var(--glow-rgb), 0.13);
}

.wm-site-nav__link:focus {
  outline: none;
  background: rgba(var(--glow-rgb), 0.07);
  box-shadow: 0 0 0 4px rgba(var(--glow-rgb), 0.08);
  text-decoration: none;
}

@media (hover: hover) and (pointer: fine) {
  .wm-site-nav__link:hover {
    background: rgba(var(--glow-rgb), 0.07);
    text-decoration: none;
  }

  [data-theme="dark"] .wm-site-nav__link:hover {
    color: #ffffff;
  }
}

[data-theme="dark"] .wm-site-nav__link {
  color: #e8e6df;
}

[data-theme="dark"] .wm-site-nav__link:focus {
  color: #ffffff;
}

@media (max-width: 720px) {
  .wm-site-nav__links {
    justify-content: flex-start;
  }

  .wm-site-nav__link {
    font-size: 17px;
    padding: 0.18em 0.62em;
  }
}
```

### JavaScript

```html
<script>
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var links = document.querySelectorAll('.wm-site-nav__link[href*="#"]');
    if (!links.length) return;

    var anchors = [];
    links.forEach(function (link) {
      var hash = (link.getAttribute('href') || '').split('#')[1];
      if (!hash) return;
      var el = document.getElementById(hash);
      if (el) anchors.push({ el: el, link: link });
    });
    if (!anchors.length) return;

    var current = null;
    var suppressUntil = 0;
    var nav = document.querySelector('.wm-site-nav');

    function scrollNavToLink(link) {
      if (!nav) return;
      var navRect = nav.getBoundingClientRect();
      var linkRect = link.getBoundingClientRect();
      var pad = 12;
      var visLeft = linkRect.left - navRect.left;
      var visRight = linkRect.right - navRect.left;
      if (visLeft < pad) {
        nav.scrollLeft += visLeft - pad;
      } else if (visRight > navRect.width - pad) {
        nav.scrollLeft += visRight - navRect.width + pad;
      }
    }

    function setActive(link) {
      if (current === link) return;
      links.forEach(function (l) { l.classList.remove('nav-active'); });
      current = link;
      if (current) {
        current.classList.add('nav-active');
        scrollNavToLink(current);
      }
    }

    links.forEach(function (link) {
      link.addEventListener('click', function (event) {
        setActive(link);
        suppressUntil = Date.now() + 1000;

        var href = link.getAttribute('href') || '';
        var hash = href.split('#')[1];
        var target = hash ? document.getElementById(hash) : null;
        if (!target) return;

        event.preventDefault();
        var offset = 72;
        var top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
      }, { capture: true });
    });

    var scrollPending = false;
    function onScroll() {
      if (Date.now() < suppressUntil) return;
      if (scrollPending) return;
      scrollPending = true;
      requestAnimationFrame(function () {
        scrollPending = false;
        if (Date.now() < suppressUntil) return;

        var offset = 80;
        var scrollY = window.scrollY + offset;
        var active = anchors[0].link;
        for (var i = anchors.length - 1; i >= 0; i--) {
          var anchorTop = anchors[i].el.getBoundingClientRect().top + window.scrollY;
          if (anchorTop <= scrollY) {
            active = anchors[i].link;
            break;
          }
        }
        setActive(active);
      });
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  });
})();
</script>
```

## 论文筛选滑块

设计要点：

- 外层 `.wm-seg-control` 是带边框的圆角容器，背景跟随主题变量。
- `.wm-seg-indicator` 是真正移动的滑块，覆盖在 active 按钮下方。
- 按钮本身透明，active 只改文字颜色；滑块移动由 JS 写入 `left` 和 `width`。
- 动画使用 `0.25s cubic-bezier(0.4, 0, 0.2, 1)`，观感接近原站。
- 用 `data-paper-type="core"` / `data-paper-type="collab"` 标记卡片；不要用内容文本判断类型。
- 切换时用 `hidden` 隐藏不匹配卡片，便于无障碍和 CSS 管理。

### HTML

```html
<section id="publications" class="wm-section">
  <h2>Publications</h2>

  <div class="wm-seg-control" id="paperFilter" role="group" aria-label="Publication filter">
    <div class="wm-seg-indicator" aria-hidden="true"></div>
    <button class="wm-seg-btn active" type="button" data-filter="core">Core Papers</button>
    <button class="wm-seg-btn" type="button" data-filter="collab">Collaboration Papers</button>
  </div>

  <div class="wm-paper-list">
    <article class="wm-paper-card" data-paper-type="core">
      <span class="wm-paper-badge wm-paper-badge--core">Core</span>
      <h3>Core Paper Title</h3>
      <p>Short venue, author, and link line.</p>
    </article>

    <article class="wm-paper-card" data-paper-type="collab">
      <span class="wm-paper-badge wm-paper-badge--collab">Collaboration</span>
      <h3>Collaboration Paper Title</h3>
      <p>Short venue, author, and link line.</p>
    </article>
  </div>
</section>
```

### CSS

```css
.wm-seg-control {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin: 0.5rem 0 1.25rem;
  padding: 3px;
  user-select: none;
  border: 1.5px solid var(--c-border);
  border-radius: 10px;
  background: linear-gradient(135deg, var(--c-bg-start) 0%, var(--c-bg-end) 100%);
}

.wm-seg-indicator {
  position: absolute;
  top: 3px;
  bottom: 3px;
  z-index: 0;
  pointer-events: none;
  border-radius: 7px;
  background: linear-gradient(135deg, var(--seg-start) 0%, var(--seg-end) 100%);
  box-shadow: 0 4px 14px var(--seg-shadow);
  transition:
    left 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.wm-seg-btn {
  position: relative;
  z-index: 1;
  appearance: none;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--seg-inactive);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 7px 20px;
  white-space: nowrap;
  transition: color 0.2s ease;
}

.wm-seg-btn.active {
  color: var(--seg-active-text);
}

.wm-paper-list {
  display: grid;
  gap: 14px;
}

.wm-paper-card {
  position: relative;
  border: 1.5px solid var(--c-border);
  border-radius: 12px;
  padding: 16px 18px;
  background: linear-gradient(135deg, var(--c-bg-start) 0%, var(--c-bg-end) 100%);
  color: var(--c-text);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.wm-paper-card:hover {
  transform: translateY(-2px);
  border-color: var(--c-hover-border);
  box-shadow: 0 8px 26px rgba(var(--glow-rgb), 0.12);
}

.wm-paper-card[hidden] {
  display: none !important;
}

.wm-paper-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 0.4rem;
  padding: 0.2rem 0.6rem;
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.wm-paper-badge--core {
  background-color: #1a8917;
  box-shadow: 0 4px 6px rgba(26, 137, 23, 0.3);
}

.wm-paper-badge--collab {
  background-color: #6c757d;
}

@media (max-width: 560px) {
  .wm-seg-control {
    width: 100%;
    box-sizing: border-box;
  }

  .wm-seg-btn {
    flex: 1;
    padding: 7px 10px;
  }
}
```

### JavaScript

```html
<script>
function moveWmSegIndicator(control, activeBtn) {
  var indicator = control.querySelector('.wm-seg-indicator');
  if (!indicator || !activeBtn) return;
  indicator.style.left = activeBtn.offsetLeft + 'px';
  indicator.style.width = activeBtn.offsetWidth + 'px';
}

function applyWmPaperFilter(filter, cards) {
  cards.forEach(function (card) {
    var type = card.dataset.paperType;
    card.hidden = !(filter === 'all' || type === filter);
  });
}

function initWmSegmentedFilters() {
  document.querySelectorAll('.wm-seg-control').forEach(function (control) {
    var activeBtn = control.querySelector('.wm-seg-btn.active') || control.querySelector('.wm-seg-btn');
    if (activeBtn) {
      activeBtn.classList.add('active');
      requestAnimationFrame(function () { moveWmSegIndicator(control, activeBtn); });
    }
  });

  var paperFilter = document.getElementById('paperFilter');
  if (!paperFilter) return;

  var cards = document.querySelectorAll('.wm-paper-card[data-paper-type]');
  var activeBtn = paperFilter.querySelector('.wm-seg-btn.active') || paperFilter.querySelector('.wm-seg-btn');
  if (activeBtn) {
    activeBtn.classList.add('active');
    applyWmPaperFilter(activeBtn.dataset.filter, cards);
  }

  paperFilter.querySelectorAll('.wm-seg-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      paperFilter.querySelectorAll('.wm-seg-btn').forEach(function (other) {
        other.classList.remove('active');
      });
      btn.classList.add('active');
      moveWmSegIndicator(paperFilter, btn);

      var filter = btn.dataset.filter;
      applyWmPaperFilter(filter, cards);
    });
  });

  window.addEventListener('resize', function () {
    var activeBtn = paperFilter.querySelector('.wm-seg-btn.active');
    moveWmSegIndicator(paperFilter, activeBtn);
  });
}

document.addEventListener('DOMContentLoaded', initWmSegmentedFilters);
</script>
```

## 复刻检查

- 顶部导航栏在桌面端居中，在窄屏只让导航条横向滚动。
- `.wm-site-nav__links` 保持 `width: max-content` 和 `min-width: 100%`，不要改成 `width: 100%`，否则窄屏溢出行为会变差。
- `.wm-site-nav__link` 的字号基准为 `21px`，圆角为 `7px`，内边距为 `0.1em 0.6em`。
- hover 只在 `@media (hover: hover) and (pointer: fine)` 中启用，避免移动端 sticky hover。
- 点击导航链接后，目标 section 平滑滚动，active 状态立即更新。
- 滚动页面时，当前 section 的导航项自动高亮，并在横向导航中自动入视。
- 论文筛选滑块初始化时 indicator 已对齐 active button。
- 点击 `Core Papers` / `Collaboration Papers` 后，indicator 平滑移动并隐藏不匹配论文。
- resize 后重新计算 indicator 的 `left` 和 `width`，避免移动端旋转或字体加载后错位。
