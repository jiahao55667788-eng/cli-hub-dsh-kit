#!/usr/bin/env python3
"""Build the CLI-Hub DSH Kit static playground.

Reads the upstream registry snapshots plus the local install manifest and emits
a single self-contained docs/index.html (no external assets, GitHub Pages ready).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"


def load(name: str, fallback: dict) -> dict:
    path = DATA / name
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def installed_snapshot() -> dict:
    for cand in (Path.home() / ".cli-hub" / "installed.json",):
        if cand.exists():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
    return {}


def main() -> None:
    harness = load("registry.snapshot.json", {"clis": []})
    public = load("public_registry.snapshot.json", {"clis": []})
    matrices = load("matrix_registry.snapshot.json", {"matrices": []})
    installed = installed_snapshot()

    payload = {
        "harness": harness.get("clis", []),
        "public": public.get("clis", []),
        "matrices": matrices.get("matrices", []),
        "installed": sorted(installed.keys()),
        "meta": {
            "harness_updated": harness.get("meta", {}).get("updated"),
            "public_updated": public.get("meta", {}).get("updated"),
            "matrix_updated": matrices.get("meta", {}).get("updated"),
            "built": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "upstream": "https://github.com/HKUDS/CLI-Anything",
            "hub": "https://clianything.cc/",
        },
    }

    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    DOCS.mkdir(parents=True, exist_ok=True)
    html = TEMPLATE.replace("__DATA__", blob)
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    n = len(payload["harness"]) + len(payload["public"])
    print(f"built {DOCS / 'index.html'} · {n} CLIs · {len(payload['matrices'])} matrices · installed {len(payload['installed'])}")


TEMPLATE = r"""<!doctype html>
<html lang="zh-CN" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CLI-Hub DSH Kit · Agent-native CLI Playground</title>
<meta name="description" content="CLI-Anything / CLI-Hub 全量目录的离线可搜索试玩页：79 harness CLI + 24 public CLI + 5 能力矩阵。">
<style>
:root{--bg:#0b0e14;--panel:#141922;--panel2:#1b2230;--line:#26303f;--fg:#e6edf6;--muted:#8b98ab;--accent:#4ea1ff;--accent2:#22d3a6;--warn:#f0b429;--radius:14px}
[data-theme="light"]{--bg:#f5f7fb;--panel:#fff;--panel2:#f0f3f9;--line:#dde3ee;--fg:#131722;--muted:#5d6b80;--accent:#0b66d6;--accent2:#0f9d76;--warn:#a86b00}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,"Segoe UI",Roboto,"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 80px}
header.top{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start;justify-content:space-between;margin-bottom:22px}
.brand h1{margin:0;font-size:26px;letter-spacing:-.4px}
.brand h1 span{color:var(--accent)}
.brand p{margin:6px 0 0;color:var(--muted);font-size:13.5px;max-width:62ch}
.stats{display:flex;gap:10px;flex-wrap:wrap}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:10px 14px;min-width:96px}
.stat b{display:block;font-size:22px;line-height:1.1;font-variant-numeric:tabular-nums}
.stat span{color:var(--muted);font-size:11.5px;text-transform:uppercase;letter-spacing:.7px}
.toolbar{position:sticky;top:0;z-index:20;background:linear-gradient(var(--bg) 78%,transparent);padding:10px 0 14px;margin-bottom:6px}
.searchrow{display:flex;gap:10px;flex-wrap:wrap}
input#q{flex:1 1 320px;background:var(--panel);border:1px solid var(--line);color:var(--fg);border-radius:12px;padding:12px 14px;font-size:15px;outline:none}
input#q:focus{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 18%,transparent)}
button,.chip{cursor:pointer;font:inherit}
.btn{background:var(--panel);border:1px solid var(--line);color:var(--fg);border-radius:12px;padding:11px 14px}
.btn:hover{border-color:var(--accent)}
.tabs{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
.tab{background:transparent;border:1px solid var(--line);color:var(--muted);border-radius:999px;padding:7px 14px;font-size:13.5px}
.tab[aria-selected="true"]{color:var(--fg);border-color:var(--accent);background:color-mix(in srgb,var(--accent) 12%,transparent)}
.chips{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}
.chip{background:var(--panel2);border:1px solid transparent;color:var(--muted);border-radius:999px;padding:5px 11px;font-size:12.5px}
.chip[aria-pressed="true"]{color:var(--fg);border-color:var(--accent);background:color-mix(in srgb,var(--accent) 14%,transparent)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px;margin-top:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px;display:flex;flex-direction:column;gap:9px}
.card.in{box-shadow:inset 3px 0 0 var(--accent2)}
.card h3{margin:0;font-size:16px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.card .mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:11.5px;color:var(--muted)}
.desc{margin:0;color:var(--fg);opacity:.88;font-size:13.5px}
.badges{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.badge{font-size:11px;padding:2.5px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.badge.src{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,var(--line))}
.badge.ok{color:var(--accent2);border-color:color-mix(in srgb,var(--accent2) 45%,var(--line))}
.cmd{display:flex;gap:8px;align-items:center;background:#05070b;border:1px solid var(--line);border-radius:10px;padding:8px 10px;overflow:auto}
[data-theme="light"] .cmd{background:#f7f9fc}
.cmd code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;white-space:nowrap;color:#9fd0ff}
[data-theme="light"] .cmd code{color:#0b66d6}
.copy{margin-left:auto;background:transparent;border:1px solid var(--line);color:var(--muted);border-radius:8px;padding:4px 9px;font-size:11.5px;flex:none}
.copy:hover{border-color:var(--accent);color:var(--fg)}
.matrix{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:18px;margin-bottom:14px}
.matrix h3{margin:0 0 4px;font-size:18px}
.matrix .lead{color:var(--muted);font-size:13.5px;margin:0 0 12px}
.memberlist{display:flex;flex-wrap:wrap;gap:7px;margin:8px 0 12px}
.member{font-size:12.5px;border:1px solid var(--line);border-radius:999px;padding:4px 10px;color:var(--muted);background:var(--panel2)}
.member.inst{color:var(--accent2);border-color:color-mix(in srgb,var(--accent2) 40%,var(--line))}
.caps{margin:0;padding-left:18px;color:var(--muted);font-size:13px}
.caps li{margin:3px 0}
.caps b{color:var(--fg);font-weight:600}
.hero{background:linear-gradient(135deg,color-mix(in srgb,var(--accent) 16%,var(--panel)),var(--panel));border:1px solid var(--line);border-radius:18px;padding:24px;margin-bottom:20px}
.hero h2{margin:0 0 8px;font-size:21px}
.hero ol{margin:10px 0 0;padding-left:20px;color:var(--muted);font-size:13.5px}
.hero li{margin:4px 0}
.hero code{font-family:ui-monospace,Consolas,monospace;color:var(--accent2);font-size:12.5px}
.empty{color:var(--muted);padding:36px 4px;text-align:center}
footer{margin-top:40px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);padding-top:16px;display:flex;gap:14px;flex-wrap:wrap;justify-content:space-between}
.toast{position:fixed;left:50%;bottom:26px;transform:translate(-50%,20px);background:var(--accent2);color:#04120c;font-weight:600;padding:9px 16px;border-radius:999px;opacity:0;transition:.22s;pointer-events:none;font-size:13px}
.toast.show{opacity:1;transform:translate(-50%,0)}
@media(max-width:620px){.stats{width:100%}.stat{flex:1 1 88px}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand">
      <h1>CLI-Hub <span>DSH Kit</span> · 试玩台</h1>
      <p>CLI-Anything 全量目录的离线可搜索版本。任何软件 → agent 原生 CLI，装一条命令即可被 agent 调用。</p>
    </div>
    <div class="stats">
      <div class="stat"><b id="s-all">0</b><span>CLI 总数</span></div>
      <div class="stat"><b id="s-cat">0</b><span>分类</span></div>
      <div class="stat"><b id="s-mx">0</b><span>能力矩阵</span></div>
      <div class="stat"><b id="s-in">0</b><span>本机已装</span></div>
    </div>
  </header>

  <section class="hero">
    <h2>三步上手</h2>
    <ol>
      <li>装包管理器：<code>pip install cli-anything-hub</code>（本机已装在隔离 venv，`cli-hub` 已在 PATH）</li>
      <li>找工具：<code>cli-hub search video</code> / <code>cli-hub can "edit a video"</code></li>
      <li>装上即用：<code>cli-hub install kdenlive</code> → <code>cli-anything-kdenlive --help</code></li>
    </ol>
  </section>

  <div class="toolbar">
    <div class="searchrow">
      <input id="q" type="search" placeholder="搜索 CLI / 能力 / 分类…（按 / 聚焦）" autocomplete="off" spellcheck="false">
      <button class="btn" id="theme" title="切换主题">◐ 主题</button>
    </div>
    <div class="tabs" role="tablist">
      <button class="tab" role="tab" data-view="all" aria-selected="true">全部 CLI</button>
      <button class="tab" role="tab" data-view="installed" aria-selected="false">本机已装</button>
      <button class="tab" role="tab" data-view="matrix" aria-selected="false">能力矩阵</button>
      <button class="tab" role="tab" data-view="about" aria-selected="false">说明</button>
    </div>
    <div class="chips" id="cats"></div>
  </div>

  <main id="view"></main>

  <footer>
    <span>数据快照：harness <b id="f-h"></b> · public <b id="f-p"></b> · matrix <b id="f-m"></b> · 页面构建 <b id="f-b"></b></span>
    <span>来源 <a href="https://github.com/HKUDS/CLI-Anything" target="_blank" rel="noreferrer">HKUDS/CLI-Anything</a> · <a href="https://clianything.cc/" target="_blank" rel="noreferrer">clianything.cc</a></span>
  </footer>
</div>
<div class="toast" id="toast">已复制</div>

<script id="payload" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('payload').textContent);
const ALL = [...D.harness.map(c => ({...c, src:'harness'})), ...D.public.map(c => ({...c, src:'public'}))];
const INST = new Set(D.installed || []);
const byName = new Map(ALL.map(c => [c.name, c]));
const cats = [...new Set(ALL.map(c => c.category).filter(Boolean))].sort();

let state = { view:'all', q:'', cat:null };

const el = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));

el('s-all').textContent = ALL.length;
el('s-cat').textContent = cats.length;
el('s-mx').textContent = D.matrices.length;
el('s-in').textContent = INST.size;
el('f-h').textContent = D.meta.harness_updated || '—';
el('f-p').textContent = D.meta.public_updated || '—';
el('f-m').textContent = D.meta.matrix_updated || '—';
el('f-b').textContent = (D.meta.built || '').slice(0, 19).replace('T', ' ');

const catsBox = el('cats');
function renderChips(){
  const list = state.view === 'matrix' || state.view === 'about' ? [] : ['__all', ...cats];
  catsBox.innerHTML = list.map(c => {
    const label = c === '__all' ? '全部分类' : c;
    const on = c === '__all' ? state.cat === null : state.cat === c;
    return `<button class="chip" data-cat="${esc(c)}" aria-pressed="${on}">${esc(label)}</button>`;
  }).join('');
}
catsBox.addEventListener('click', e => {
  const b = e.target.closest('[data-cat]'); if (!b) return;
  const v = b.dataset.cat;
  state.cat = v === '__all' ? null : v;
  renderChips(); render();
});

function match(c, q){
  if (!q) return true;
  const hay = [c.name, c.display_name, c.description, c.category, c.entry_point, c.requires, c.version, c.package_manager].filter(Boolean).join(' ').toLowerCase();
  return q.toLowerCase().split(/\s+/).filter(Boolean).every(t => hay.includes(t));
}

function card(c){
  const inst = INST.has(c.name);
  const cmd = c.install_cmd || (c.src === 'harness' ? `cli-hub install ${c.name}` : '');
  return `<article class="card ${inst ? 'in' : ''}">
    <h3>${esc(c.display_name || c.name)} <span class="mono">${esc(c.name)}</span>${inst ? '<span class="badge ok">已装</span>' : ''}</h3>
    <div class="badges">
      <span class="badge src">${esc(c.src)}</span>
      ${c.category ? `<span class="badge">${esc(c.category)}</span>` : ''}
      ${c.version ? `<span class="badge">v${esc(c.version)}</span>` : ''}
      ${c.package_manager ? `<span class="badge">${esc(c.package_manager)}</span>` : ''}
    </div>
    <p class="desc">${esc(c.description || '')}</p>
    ${c.requires ? `<div class="mono">需要：${esc(c.requires)}</div>` : ''}
    ${c.entry_point ? `<div class="mono">入口：${esc(c.entry_point)}</div>` : ''}
    ${cmd ? `<div class="cmd"><code>${esc(cmd)}</code><button class="copy" data-cmd="${esc(cmd)}">复制</button></div>` : ''}
  </article>`;
}

function renderList(){
  const q = state.q.trim();
  let list = ALL.filter(c => match(c, q) && (!state.cat || c.category === state.cat));
  if (state.view === 'installed') list = list.filter(c => INST.has(c.name));
  list.sort((a, b) => a.name.localeCompare(b.name));
  if (!list.length) return `<div class="empty">没有匹配的 CLI。清空搜索或换关键词试试。</div>`;
  return `<div class="grid">${list.map(card).join('')}</div>`;
}

function renderMatrix(){
  const q = state.q.trim();
  const cards = D.matrices.map(m => {
    const members = (m.clis || []).map(n => ({ n, cli: byName.get(n) }));
    if (q){
      const hit = [m.name, m.display_name, m.description, ...(m.capabilities || []).map(c => c.intent)].join(' ').toLowerCase().includes(q.toLowerCase());
      if (!hit) return '';
    }
    const mem = members.map(({n, cli}) => {
      const inst = INST.has(n);
      return `<span class="member ${inst ? 'inst' : ''}" title="${esc(cli ? (cli.description || '') : 'public CLI')}">${esc(n)}${inst ? ' ✓' : ''}</span>`;
    }).join('');
    const caps = (m.capabilities || []).slice(0, 8).map(c => `<li><b>${esc(c.id)}</b> — ${esc((c.intent || '').slice(0, 150))}</li>`).join('');
    return `<section class="matrix">
      <h3>${esc(m.display_name || m.name)} <span class="badge">${esc(m.matrix_id || '')}</span> <span class="badge">${members.filter(x => INST.has(x.n)).length}/${members.length} 已装</span></h3>
      <p class="lead">${esc(m.description || '')}</p>
      <div class="memberlist">${mem}</div>
      <div class="cmd"><code>cli-hub matrix install ${esc(m.name)}</code><button class="copy" data-cmd="cli-hub matrix install ${esc(m.name)}">复制</button></div>
      ${caps ? `<ul class="caps">${caps}</ul>` : ''}
    </section>`;
  }).filter(Boolean);
  return cards.length ? cards.join('') : `<div class="empty">没有匹配的矩阵。</div>`;
}

function renderAbout(){
  return `<section class="matrix">
    <h3>这个页面是什么</h3>
    <p class="lead">CLI-Anything（HKUDS）把 GUI 软件、代码库、Web API 变成 agent 原生 CLI。这页是它的目录快照 + 本机安装台账，静态托管、离线可查。</p>
    <ul class="caps">
      <li><b>cli-hub list / search / info</b> — 浏览与检索注册表</li>
      <li><b>cli-hub install &lt;name&gt;</b> — harness 类走 pip（装进隔离 venv），public 类走 uv/npm</li>
      <li><b>cli-hub launch &lt;name&gt;</b> — 装完直接拉起，参数透传</li>
      <li><b>cli-hub can "&lt;任务&gt;"</b> — 按能力反查矩阵，不知道装什么时用它</li>
      <li><b>cli-hub matrix install &lt;name&gt;</b> — 一次性装齐一条工作流的全部 CLI</li>
      <li><b>cli-hub update / uninstall &lt;name&gt;</b> — 升级与卸载，台账在 <code>~/.cli-hub/installed.json</code></li>
    </ul>
  </section>
  <section class="matrix">
    <h3>数据与来源</h3>
    <p class="lead">harness 注册表 ${ALL.filter(c => c.src === 'harness').length} 条 · public 注册表 ${ALL.filter(c => c.src === 'public').length} 条 · 矩阵 ${D.matrices.length} 条。上游 ${esc(D.meta.upstream)}，站点 ${esc(D.meta.hub)}。本页不联网、不含追踪脚本。</p>
  </section>`;
}

function render(){
  const v = el('view');
  v.innerHTML = state.view === 'matrix' ? renderMatrix() : state.view === 'about' ? renderAbout() : renderList();
  window.scrollTo({ top: 0, behavior: 'instant' });
}

document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(x => x.setAttribute('aria-selected', String(x === t)));
  state.view = t.dataset.view;
  renderChips(); render();
}));

el('q').addEventListener('input', e => { state.q = e.target.value; render(); });

el('theme').addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try { localStorage.setItem('clihub-theme', next); } catch {}
});

document.addEventListener('click', async e => {
  const b = e.target.closest('.copy'); if (!b) return;
  const text = b.dataset.cmd;
  try { await navigator.clipboard.writeText(text); }
  catch { const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove(); }
  const t = el('toast'); t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 1400);
});

document.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== el('q')) { e.preventDefault(); el('q').focus(); }
  if (e.key === 'Escape' && document.activeElement === el('q')) { el('q').value = ''; state.q = ''; el('q').blur(); render(); }
});

try { const th = localStorage.getItem('clihub-theme'); if (th) document.documentElement.setAttribute('data-theme', th); } catch {}
renderChips();
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
