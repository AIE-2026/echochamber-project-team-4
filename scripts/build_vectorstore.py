<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vlad Alexe — Tutorials</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;1,9..144,300&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:       #1a1a1a;
  --surface:  #222222;
  --border:   #333333;
  --border-hi:#444444;
  --text:     #e2e2e2;
  --dim:      #666666;
  --sub:      #999999;
  --accent:   #c8956c;
  --blue:     #7ab0d4;
  --green:    #89b99a;
}

:root.light {
  --bg:       #ffffff;
  --surface:  #f5f5f5;
  --border:   #e5e5e5;
  --border-hi:#cccccc;
  --text:     #111111;
  --dim:      #888888;
  --sub:      #444444;
  --accent:   #b5784a;
  --blue:     #2f6fa8;
  --green:    #3d7a52;
}

/* Nav name style */
.nav-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 300;
  font-size: 10px;
  color: var(--dim);
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

html { scroll-behavior: smooth; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.7;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  transition: background 0.2s, color 0.2s;
}

/* ── Nav ── */
nav {
  height: 50px;
  border-bottom: 1px solid var(--border);
  padding: 0 3rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  background: var(--bg);
  z-index: 10;
  transition: background 0.2s;
}

.nav-left { display: flex; align-items: center; gap: 1.8rem; }

.nav-logo {
  display: flex; align-items: center; gap: 0.55rem;
  font-size: 12.5px; font-weight: 500; color: var(--text);
}

.nav-logo img { width: 22px; height: 22px; border-radius: 50%; }

.nav-sep { width: 1px; height: 14px; background: var(--border); }

.breadcrumb {
  display: flex; align-items: center; gap: 0.35rem;
  font-size: 12px; color: var(--dim);
}
.breadcrumb a { color: var(--sub); }
.breadcrumb a:hover { color: var(--text); }
.breadcrumb .cur { color: var(--text); }
.breadcrumb .sl { color: var(--border-hi); }

.theme-btn {
  background: none; border: 1px solid var(--border);
  color: var(--dim); font-family: 'JetBrains Mono', monospace;
  font-size: 11px; padding: 0.22rem 0.65rem;
  border-radius: 3px; cursor: pointer;
  transition: color 0.12s, border-color 0.12s;
}
.theme-btn:hover { color: var(--text); border-color: var(--border-hi); }

/* ── Hero ── */
.hero {
  padding: 3.5rem 3rem 2.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: flex-start;
  gap: 2rem;
}

.hero-logo {
  width: 64px; height: 64px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
  /* invert logo in dark mode so black logo shows on dark bg */
  filter: invert(1);
}
:root.light .hero-logo { filter: none; }

.hero-body {}

.hero-tag {
  font-size: 10px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--accent);
  margin-bottom: 0.6rem;
}

.hero h1 {
  font-family: 'Fraunces', serif;
  font-size: 2.2rem; font-weight: 700; color: var(--text);
  letter-spacing: -0.025em; line-height: 1.1;
  margin-bottom: 0.65rem;
}

.hero p {
  font-size: 12.5px; color: var(--sub);
  max-width: 500px; line-height: 1.8;
}

.hero-meta {
  margin-top: 1rem; display: flex; gap: 1.4rem;
  font-size: 11px; color: var(--dim);
}
.hero-meta strong { color: var(--sub); font-weight: 400; }

/* ── Main ── */
main {
  flex: 1;
  padding: 2.8rem 3rem 5rem;
  max-width: 880px;
  width: 100%;
}

.label {
  font-size: 10px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--dim);
  margin-bottom: 1rem;
}

/* ── Card grid ── */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  border: 1px solid var(--border);
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 2.8rem;
}

.card {
  background: var(--surface);
  padding: 1.3rem 1.4rem;
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  position: relative;
  transition: background 0.12s;
}

.card:hover { background: var(--bg); }

/* Remove extra borders on grid edges */
.card:nth-child(3n) { border-right: none; }
.grid > .card:last-child { border-bottom: none; }

.card a.card-link { position: absolute; inset: 0; }

.card-icon { font-size: 1rem; margin-bottom: 0.55rem; }

.card-title {
  font-size: 12.5px; font-weight: 500; color: var(--text);
  margin-bottom: 0.3rem; line-height: 1.3;
}

.card-desc { font-size: 11px; color: var(--dim); line-height: 1.65; }

.card-badge {
  display: inline-block; margin-top: 0.65rem;
  font-size: 10px; letter-spacing: 0.05em;
  color: var(--accent); border: 1px solid var(--accent);
  padding: 0.06em 0.45em; border-radius: 2px; opacity: 0.75;
}

/* ── Week table ── */
.week-table {
  border: 1px solid var(--border);
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 2.8rem;
  width: 100%;
}

.week-row {
  display: grid;
  grid-template-columns: 72px 1fr;
  border-bottom: 1px solid var(--border);
  transition: background 0.1s;
}
.week-row:last-child { border-bottom: none; }
.week-row:hover { background: var(--surface); }

.wk {
  padding: 0.9rem 0.8rem 0.9rem 1.1rem;
  font-size: 11px; color: var(--dim);
  border-right: 1px solid var(--border);
  display: flex; align-items: flex-start;
  padding-top: 1rem;
}

.wb { padding: 0.9rem 1.2rem; }

.wb-title { font-size: 12.5px; color: var(--text); margin-bottom: 0.18rem; }
.wb-topics { font-size: 11px; color: var(--dim); line-height: 1.6; }
.wb-topics a { color: var(--blue); border-bottom: 1px solid transparent; }
.wb-topics a:hover { border-bottom-color: var(--blue); }

/* ── Footer ── */
footer {
  border-top: 1px solid var(--border);
  padding: 1.1rem 3rem;
  font-size: 11px; color: var(--dim);
  display: flex; justify-content: space-between;
  align-items: center;
}
footer a { color: var(--dim); }
footer a:hover { color: var(--text); }
</style>
</head>
<body>

<nav>
  <div class="nav-left">
    <a href="/" class="nav-name">Vlad Alexe</a>
  </div>
  <button class="theme-btn" id="themeBtn" onclick="toggleTheme()">◑ light</button>
</nav>

<div class="hero">
  <img class="hero-logo" src="logo.png" alt="">
  <div class="hero-body">
    <div class="hero-tag">tutorials</div>
    <h1>Course Materials</h1>
    <p>Open teaching materials, guides, and notebooks. Free to use under CC&nbsp;BY-NC-SA&nbsp;4.0.</p>
</div>
</div>

<main>
  <p class="label">Courses</p>
  <div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(300px,1fr))">

    <div class="card">
      <a href="ai-engineering/" class="card-link"></a>
      <div class="card-icon">🔊</div>
      <div class="card-title">AI Engineering</div>
      <div class="card-desc">Discursive agents, filter bubbles, RAG, and LLM simulation on Romanian political data.</div>
      <span class="card-badge">ADC 2026</span>
    </div>

  </div>
</main>

<footer>
  <span>© 2026 Vlad Alexe</span>
  <span>
    <a href="LICENSE">CC BY-NC-SA 4.0</a>&nbsp;·&nbsp;
    <a href="https://github.com/VladAlexe/tutorials" target="_blank">GitHub ↗</a>
  </span>
</footer>

<script>
  function toggleTheme() {
    const r = document.documentElement;
    const b = document.getElementById('themeBtn');
    if (r.classList.contains('light')) {
      r.classList.remove('light');
      b.textContent = '◑ light';
      localStorage.setItem('va-theme','dark');
    } else {
      r.classList.add('light');
      b.textContent = '◑ dark';
      localStorage.setItem('va-theme','light');
    }
  }
  (function() {
    if (localStorage.getItem('va-theme') === 'light') {
      document.documentElement.classList.add('light');
      document.addEventListener('DOMContentLoaded', () => {
        const b = document.getElementById('themeBtn');
        if (b) b.textContent = '◑ dark';
      });
    }
  })();
</script>
</body>
</html>