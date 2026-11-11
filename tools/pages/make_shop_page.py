# builds the parts and budget page from spec/bom.yaml into build/argus-parts.html
import json
import pathlib, sys, time
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from argus import bom as S

FREE = S.FREE_SHIPPING
data = dict(rows=S.rows(), hw=S.HARDWARE, redesign=S.REDESIGN, budget=S.BUDGET_TL, free=FREE, status=S.STATUS_TXT,
            updated=time.strftime('%d %b %Y'))

page = r'''<title>ARGUS Parts and Budget</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Saira+Condensed:wght@600;700&display=swap">
<style>
/* layout: purchase ledger, budget strip on top, then one block per store, then what is still missing */
:root {
  --bg: #eef0f4; --surface: #ffffff; --ink: #1a1c25; --muted: #5b6070; --line: #d9dce5; --accent: #5a3ea6; --accent-soft: #ece7f8;
  --ok: #23744a; --ok-bg: #dcefe4; --warn: #915c10; --warn-bg: #f5e8cf; --info: #4a5170; --info-bg: #e3e6ef; --bar: #e4e6ee;
  --f-display: "Saira Condensed", "Arial Narrow", sans-serif; --f-body: "IBM Plex Sans", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0f1117; --surface: #171a23; --ink: #e6e7ee; --muted: #9a9fb1; --line: #2a2f3c; --accent: #a48cff; --accent-soft: #2a2347;
  --ok: #62c891; --ok-bg: #15301f; --warn: #e9b45a; --warn-bg: #36290f; --info: #aab2d0; --info-bg: #232838; --bar: #232736; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0f1117; --surface: #171a23; --ink: #e6e7ee; --muted: #9a9fb1; --line: #2a2f3c; --accent: #a48cff; --accent-soft: #2a2347;
  --ok: #62c891; --ok-bg: #15301f; --warn: #e9b45a; --warn-bg: #36290f; --info: #aab2d0; --info-bg: #232838; --bar: #232736; color-scheme: dark; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: var(--f-body); font-size: 14px; line-height: 1.45; margin: 0;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 20px 40px; }
.wrap { max-width: 1080px; margin: 0 auto; display: grid; gap: 22px; }
h1 { font-family: var(--f-display); font-weight: 700; font-size: 34px; letter-spacing: 0.04em; margin: 0; line-height: 1; }
h1 span { color: var(--accent); }
h2 { font-family: var(--f-display); font-weight: 600; font-size: 15px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin: 0 0 8px; }
.sub { color: var(--muted); margin: 6px 0 0; }
a { color: var(--accent); }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 16px; min-width: 0; }
.kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.kpi b { display: block; font-family: var(--f-mono); font-size: 20px; font-weight: 500; font-variant-numeric: tabular-nums; }
.kpi span { color: var(--muted); font-size: 12px; }
.bar { height: 14px; background: var(--bar); border-radius: 7px; overflow: hidden; display: flex; margin-top: 14px; position: relative; }
.bar i { display: block; height: 100%; }
.bar .lim { position: absolute; top: -4px; bottom: -4px; width: 2px; background: var(--ink); }
.legend { display: flex; flex-wrap: wrap; gap: 6px 16px; margin-top: 8px; font-size: 12px; color: var(--muted); }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 5px; vertical-align: -1px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { border: 1px solid var(--line); background: var(--surface); border-radius: 999px; padding: 5px 12px; font-size: 13px; cursor: pointer; color: var(--ink); }
.chip[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: var(--surface); }
.chip:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.store { display: grid; gap: 6px; }
.store-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 12px; }
.store-head h3 { margin: 0; font-family: var(--f-display); font-weight: 700; font-size: 22px; letter-spacing: 0.03em; }
.store-head .t { font-family: var(--f-mono); font-variant-numeric: tabular-nums; }
.ship { font-size: 12px; color: var(--muted); }
.ship.ok { color: var(--ok); } .ship.gap { color: var(--warn); }
.tbl { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
th { text-align: left; font-weight: 500; color: var(--muted); font-size: 12px; padding: 6px 8px 6px 0; border-bottom: 1px solid var(--line); white-space: nowrap; }
td { padding: 8px 8px 8px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
td.n, th.n { text-align: right; font-family: var(--f-mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
td.q { font-family: var(--f-mono); color: var(--muted); white-space: nowrap; }
td .note { color: var(--muted); font-size: 12px; }
.st { font-family: var(--f-mono); font-size: 11px; padding: 2px 7px; border-radius: 4px; white-space: nowrap; }
.st-chosen { background: var(--ok-bg); color: var(--ok); } .st-check, .st-quote { background: var(--warn-bg); color: var(--warn); }
.st-borrow { background: var(--accent-soft); color: var(--accent); } .st-later { background: var(--info-bg); color: var(--info); }
.two { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 16px; }
ol, ul { margin: 0; padding-left: 20px; display: grid; gap: 6px; }
.hw { columns: 2; column-gap: 24px; list-style: none; padding: 0; }
.hw li { break-inside: avoid; padding: 3px 0; border-bottom: 1px solid var(--line); display: flex; gap: 8px; }
.hw b { font-family: var(--f-mono); font-weight: 500; min-width: 34px; color: var(--muted); }
@media (max-width: 760px) { .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } .two { grid-template-columns: minmax(0, 1fr); } .hw { columns: 1; } }
</style>

<div class="wrap">
  <header>
    <h1>ARGUS <span>T18</span> parts and budget</h1>
    <p class="sub">Every part we picked, where to buy it, what it costs and what is still open. Updated <span id="upd"></span>. Prices include VAT as seen on the store pages.</p>
  </header>

  <section class="panel">
    <div class="kpis" id="kpis"></div>
    <div class="bar" id="bar"></div>
    <div class="legend" id="legend"></div>
  </section>

  <section>
    <h2>Show</h2>
    <div class="chips" id="filters"></div>
  </section>

  <section id="stores" style="display:grid;gap:16px"></section>

  <section class="two">
    <div class="panel">
      <h2>Hardware store list</h2>
      <ul class="hw" id="hw"></ul>
    </div>
    <div class="panel">
      <h2>Model changes waiting on real parts</h2>
      <ol id="redesign"></ol>
    </div>
  </section>
</div>

<script>
const D = /*__DATA__*/null;
const $ = (s) => document.querySelector(s);
const tl = (v) => Math.round(v).toLocaleString('en-US') + ' TL';
const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
$('#upd').textContent = D.updated;
const COL = { chosen: 'var(--ok)', check: 'var(--warn)', quote: 'var(--warn)', borrow: 'var(--accent)', later: 'var(--info)' };
const sum = (f) => D.rows.filter(f).reduce((s, r) => s + r.total, 0);
const chosen = sum((r) => r.status === 'chosen'), check = sum((r) => r.status === 'check' || r.status === 'quote');
const borrow = sum((r) => r.status === 'borrow'), later = sum((r) => r.status === 'later');
const all = chosen + check + borrow + later, noBorrow = all - borrow;
$('#kpis').innerHTML = [
  [tl(D.budget), 'budget ($350)'], [tl(chosen), 'chosen, ready to order'],
  [tl(check + later), 'still to check or pick'], [tl(all), all <= D.budget ? `total, ${tl(D.budget - all)} under budget` : `total, ${tl(all - D.budget)} over budget`],
].map(([a, b]) => `<div class="kpi"><b>${a}</b><span>${b}</span></div>`).join('');
const max = Math.max(all, D.budget) * 1.02;
$('#bar').innerHTML = [['chosen', chosen], ['check', check], ['later', later], ['borrow', borrow]]
  .map(([k, v]) => `<i style="width:${v / max * 100}%;background:${COL[k]}"></i>`).join('') + `<span class="lim" style="left:${D.budget / max * 100}%"></span>`;
$('#legend').innerHTML = [['chosen', 'Chosen', chosen], ['check', 'Check or quote', check], ['later', 'Still to pick (estimates)', later], ['borrow', 'Borrow first', borrow]]
  .map(([k, t, v]) => `<span><i style="background:${COL[k]}"></i>${t} ${tl(v)}</span>`).join('') + '<span>black line = budget</span>';

const counts = {}; D.rows.forEach((r) => (counts[r.status] = (counts[r.status] || 0) + 1));
let filt = '';
$('#filters').innerHTML = [['', `All (${D.rows.length})`], ...Object.keys(D.status).map((k) => [k, `${D.status[k]} (${counts[k] || 0})`])]
  .map(([k, t]) => `<button class="chip" data-k="${k}" aria-pressed="${k === ''}">${t}</button>`).join('');
document.querySelectorAll('#filters .chip').forEach((b) => b.addEventListener('click', () => {
  filt = b.dataset.k; document.querySelectorAll('#filters .chip').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); render();
}));

function render() {
  const stores = [...new Set(D.rows.map((r) => r.store))];
  $('#stores').innerHTML = stores.map((st) => {
    const all_ = D.rows.filter((r) => r.store === st), rows = all_.filter((r) => !filt || r.status === filt);
    if (!rows.length) return '';
    const sub = all_.reduce((s, r) => s + r.total, 0), cho = all_.filter((r) => r.status === 'chosen').reduce((s, r) => s + r.total, 0);
    let ship = '';
    if (D.free[st]) ship = cho >= D.free[st] ? `<span class="ship ok">free shipping reached (over ${tl(D.free[st])})</span>`
      : `<span class="ship gap">${tl(D.free[st] - cho)} short of free shipping (${tl(D.free[st])})</span>`;
    return `<div class="panel store"><div class="store-head"><h3>${esc(st)}</h3><div>${ship} <span class="t">${tl(sub)}</span></div></div>
      <div class="tbl"><table><thead><tr><th>Qty</th><th>Item</th><th>Step</th><th>Status</th><th class="n">Unit</th><th class="n">Total</th></tr></thead><tbody>
      ${rows.map((r) => `<tr><td class="q">${r.qty} x</td><td>${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.item)}</a>` : esc(r.item)}${r.note ? `<div class="note">${esc(r.note)}</div>` : ''}</td>
        <td class="q">${esc(r.step)}</td><td><span class="st st-${r.status}">${D.status[r.status]}</span></td>
        <td class="n">${r.unit ? tl(r.unit) : '?'}</td><td class="n">${r.total ? tl(r.total) : '?'}</td></tr>`).join('')}
      </tbody></table></div></div>`;
  }).join('');
}
render();
$('#hw').innerHTML = D.hw.map(([n, q]) => `<li><b>${q}x</b><span>${esc(n)}</span></li>`).join('');
$('#redesign').innerHTML = D.redesign.map((t) => `<li>${esc(t)}</li>`).join('');
</script>
'''
(ROOT / 'build').mkdir(exist_ok=True)
open(ROOT / 'build' / 'argus-parts.html', 'w', encoding='utf-8').write(page.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False)))
print('ok')
