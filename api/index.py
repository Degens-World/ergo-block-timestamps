from http.server import BaseHTTPRequestHandler
import sys
import os
from string import Template

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api._utils import load_index

HTML = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ergo Block Timestamps | degens.world</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Space Grotesk', sans-serif;
    max-width: 860px; margin: 0 auto; padding: 40px 20px;
    color: #c4c9d4;
    background: #0a0a0f;
    line-height: 1.6;
    min-height: 100vh;
  }

  /* Glow bg accent */
  body::before {
    content: '';
    position: fixed; top: -200px; left: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(157,78,221,0.08) 0%, transparent 70%);
    pointer-events: none; z-index: -1;
  }
  body::after {
    content: '';
    position: fixed; bottom: -200px; right: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(0,255,136,0.06) 0%, transparent 70%);
    pointer-events: none; z-index: -1;
  }

  h1 {
    font-size: 2.4em; font-weight: 700; margin-bottom: 0;
    background: linear-gradient(135deg, #00ff88, #00d4ff, #9d4edd);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .tagline {
    color: #666; font-size: 1.05em; margin-top: 4px; margin-bottom: 24px;
  }
  .tagline span { color: #00ff88; }

  h2 {
    font-size: 1.3em; font-weight: 700; margin-top: 2.2em; margin-bottom: 0.6em;
    color: #fff;
    letter-spacing: -0.02em;
  }
  h2::before { content: '// '; color: #9d4edd; font-family: 'JetBrains Mono', monospace; font-size: 0.85em; }

  h3 { color: #888; font-size: 1em; margin-top: 1.5em; margin-bottom: 0.5em; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }

  a { color: #00d4ff; text-decoration: none; }
  a:hover { text-decoration: underline; color: #00ff88; }

  code {
    font-family: 'JetBrains Mono', monospace;
    background: rgba(157,78,221,0.12); padding: 2px 7px; border-radius: 4px;
    font-size: 0.88em; color: #e0b0ff;
    border: 1px solid rgba(157,78,221,0.2);
  }
  pre {
    font-family: 'JetBrains Mono', monospace;
    background: #0d0d14; padding: 18px; border-radius: 8px;
    overflow-x: auto; font-size: 0.85em;
    border: 1px solid #1a1a2e;
    color: #a0a8b8;
  }
  pre .k { color: #00ff88; }

  /* Stats banner */
  .stats {
    background: linear-gradient(135deg, rgba(0,255,136,0.06), rgba(157,78,221,0.06));
    padding: 18px 22px; border-radius: 10px;
    border: 1px solid rgba(0,255,136,0.15);
    display: flex; gap: 32px; flex-wrap: wrap; align-items: center;
  }
  .stat-item { }
  .stat-label { font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.1em; color: #555; }
  .stat-value { font-family: 'JetBrains Mono', monospace; font-size: 1.3em; font-weight: 700; color: #00ff88; }

  /* Date picker section */
  .picker {
    background: #0d0d14; padding: 28px; border-radius: 12px;
    border: 1px solid #1a1a2e; margin: 1.2em 0;
    position: relative;
  }
  .picker::before {
    content: ''; position: absolute; top: -1px; left: 20%; right: 20%; height: 1px;
    background: linear-gradient(90deg, transparent, #9d4edd, transparent);
  }
  .picker-row { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
  .picker label {
    font-weight: 600; color: #888; font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.05em;
  }
  .picker input[type="date"] {
    font-family: 'JetBrains Mono', monospace;
    background: #12121c; color: #fff; border: 1px solid #2a2a3e;
    padding: 10px 16px; border-radius: 6px; font-size: 1em; cursor: pointer;
    transition: border-color 0.2s;
  }
  .picker input[type="date"]:hover { border-color: #9d4edd; }
  .picker input[type="date"]:focus { outline: none; border-color: #00ff88; box-shadow: 0 0 12px rgba(0,255,136,0.15); }
  .picker input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(1); cursor: pointer; }

  /* Results table */
  .results { margin-top: 20px; display: none; }
  .results table { width: 100%; border-collapse: collapse; }
  .results th {
    text-align: left; padding: 10px 14px;
    font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.1em; color: #555;
    border-bottom: 1px solid #1a1a2e;
  }
  .results td { padding: 12px 14px; border-bottom: 1px solid #111118; }
  .results tr:hover td { background: rgba(157,78,221,0.04); }
  .period { color: #9d4edd; font-weight: 700; }
  .blocks { font-family: 'JetBrains Mono', monospace; color: #00ff88; }
  .count-cell { font-family: 'JetBrains Mono', monospace; color: #666; }
  .loading { color: #333; font-style: italic; margin-top: 12px; }

  /* Endpoint cards */
  .endpoint-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .ep-card {
    background: #0d0d14; padding: 14px 16px; border-radius: 8px;
    border: 1px solid #1a1a2e; transition: border-color 0.2s, background 0.2s;
    cursor: pointer; user-select: none;
  }
  .ep-card:hover { border-color: #9d4edd; }
  .ep-card.active { border-color: #00ff88; background: rgba(0,255,136,0.04); }
  .ep-card p { margin: 0; }
  .ep-card .desc { color: #444; font-size: 0.85em; margin-top: 4px; }
  .method {
    font-family: 'JetBrains Mono', monospace;
    color: #00ff88; font-weight: 700; font-size: 0.85em;
    background: rgba(0,255,136,0.08); padding: 2px 6px; border-radius: 3px;
    margin-right: 6px;
  }

  hr { border: none; border-top: 1px solid #1a1a2e; margin: 2.5em 0; }

  footer {
    margin-top: 3em; padding-top: 1.5em;
    border-top: 1px solid #1a1a2e;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 12px;
  }
  footer a { color: #9d4edd; }
  .footer-left { color: #333; font-size: 0.85em; }
  .footer-right { color: #222; font-size: 0.8em; font-family: 'JetBrains Mono', monospace; }

  /* Glow pulse on the title */
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.7; } }
  .live-dot {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    background: #00ff88; margin-right: 6px;
    animation: pulse 2s ease-in-out infinite;
    box-shadow: 0 0 8px rgba(0,255,136,0.5);
  }

  @media (max-width: 600px) {
    h1 { font-size: 1.7em; }
    .endpoint-grid { grid-template-columns: 1fr; }
    .stats { flex-direction: column; gap: 14px; }
  }
</style>
</head>
<body>

<h1>ergo block timestamps</h1>
<p class="tagline"><span class="live-dot"></span>live block data for <span>degens</span> who build</p>

<div class="stats">
  <div class="stat-item">
    <div class="stat-label">Total Blocks</div>
    <div class="stat-value">$total_blocks</div>
  </div>
  <div class="stat-item">
    <div class="stat-label">Latest Height</div>
    <div class="stat-value">$latest_height</div>
  </div>
  <div class="stat-item">
    <div class="stat-label">Since</div>
    <div class="stat-value">Genesis</div>
  </div>
  <div class="stat-item">
    <div class="stat-label">Updates</div>
    <div class="stat-value">Hourly</div>
  </div>
</div>

<!-- Interactive Date Picker -->
<h2>Block Height Lookup</h2>
<div class="picker">
  <div class="picker-row">
    <label for="datepicker">pick a date</label>
    <input type="date" id="datepicker" min="2019-07-01" value="$today">
  </div>
  <div class="results" id="results">
    <table>
      <thead>
        <tr><th>Period</th><th>Block Start</th><th>Block End</th><th>Blocks</th></tr>
      </thead>
      <tbody id="results-body"></tbody>
    </table>
  </div>
  <div class="loading" id="loading" style="display:none">fetching blocks...</div>
</div>

<hr>

<!-- API Docs -->
<h2>Endpoints</h2>

<h3>Block Lookups</h3>
<div class="endpoint-grid">
  <div class="ep-card active" data-ep="block">
    <p><span class="method">GET</span> <code>/api/block/:height</code></p>
    <p class="desc">single block timestamp</p>
  </div>
  <div class="ep-card" data-ep="blocks">
    <p><span class="method">GET</span> <code>/api/blocks?from=X&amp;to=Y</code></p>
    <p class="desc">range query, max 1,000</p>
  </div>
</div>

<h3>Period Boundaries</h3>
<div class="endpoint-grid">
  <div class="ep-card" data-ep="days">
    <p><span class="method">GET</span> <code>/api/days?date=YYYY-MM-DD</code></p>
    <p class="desc">filter: <code>?year=</code> <code>?month=</code></p>
  </div>
  <div class="ep-card" data-ep="weeks">
    <p><span class="method">GET</span> <code>/api/weeks?year=Y&amp;week=W</code></p>
    <p class="desc">ISO week boundaries</p>
  </div>
  <div class="ep-card" data-ep="months">
    <p><span class="method">GET</span> <code>/api/months?year=Y&amp;month=M</code></p>
    <p class="desc">calendar month boundaries</p>
  </div>
  <div class="ep-card" data-ep="years">
    <p><span class="method">GET</span> <code>/api/years?year=Y</code></p>
    <p class="desc">full year boundaries</p>
  </div>
</div>

<h3>Metadata</h3>
<div class="endpoint-grid">
  <div class="ep-card" data-ep="info">
    <p><span class="method">GET</span> <code>/api/info</code></p>
    <p class="desc">latest height, totals, year index</p>
  </div>
</div>

<h3>Example <span style="color:#333; font-size:0.7em; font-weight:400">click an endpoint above</span></h3>
<pre id="example-code"></pre>

<hr>

<p style="color:#444; font-size:0.9em">
  CORS enabled on all endpoints. Call from any frontend. No API key needed. No rate limits. Just vibes.
</p>

<footer>
  <div class="footer-left">
    built by <a href="https://degens.world">degens.world</a> for the ergo ecosystem
  </div>
  <div class="footer-right">
    <a href="https://github.com/Degens-World/ergo-block-timestamps" style="color:#333">source</a>
  </div>
</footer>

<script>
const dp = document.getElementById('datepicker');
const resultsDiv = document.getElementById('results');
const resultsBody = document.getElementById('results-body');
const loading = document.getElementById('loading');

function fmt(n) { return n.toLocaleString(); }

function getISOWeek(d) {
  const date = new Date(d.getTime());
  date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil(((date - yearStart) / 86400000 + 1) / 7);
  return { year: date.getUTCFullYear(), week: weekNo };
}

async function lookup() {
  const dateStr = dp.value;
  if (!dateStr) return;

  loading.style.display = 'block';
  resultsDiv.style.display = 'none';

  const parts = dateStr.split('-');
  const year = parseInt(parts[0]);
  const month = parseInt(parts[1]);
  const d = new Date(dateStr + 'T00:00:00Z');
  const iso = getISOWeek(d);

  try {
    const [dayData, weekData, monthData, yearData] = await Promise.all([
      fetch('/api/days?date=' + dateStr).then(r => r.json()),
      fetch('/api/weeks?year=' + iso.year + '&week=' + iso.week).then(r => r.json()),
      fetch('/api/months?year=' + year + '&month=' + month).then(r => r.json()),
      fetch('/api/years?year=' + year).then(r => r.json()),
    ]);

    let rows = '';

    if (dayData.days && dayData.days.length > 0) {
      const dy = dayData.days[0];
      rows += '<tr><td class="period">' + dateStr + '</td><td class="blocks">' + fmt(dy.block_start) +
              '</td><td class="blocks">' + fmt(dy.block_end) +
              '</td><td class="count-cell">' + fmt(dy.count) + '</td></tr>';
    } else {
      rows += '<tr><td class="period">' + dateStr + '</td><td colspan="3" style="color:#333">no blocks mined</td></tr>';
    }

    if (weekData.weeks && weekData.weeks.length > 0) {
      const wk = weekData.weeks[0];
      const cnt = wk.block_end - wk.block_start + 1;
      rows += '<tr><td class="period">Week ' + wk.label + ' / ' + iso.year +
              '</td><td class="blocks">' + fmt(wk.block_start) +
              '</td><td class="blocks">' + fmt(wk.block_end) +
              '</td><td class="count-cell">' + fmt(cnt) + '</td></tr>';
    }

    if (monthData.months && monthData.months.length > 0) {
      const mo = monthData.months[0];
      const cnt = mo.block_end - mo.block_start + 1;
      rows += '<tr><td class="period">' + mo.name + ' ' + year +
              '</td><td class="blocks">' + fmt(mo.block_start) +
              '</td><td class="blocks">' + fmt(mo.block_end) +
              '</td><td class="count-cell">' + fmt(cnt) + '</td></tr>';
    }

    if (yearData.years && yearData.years.length > 0) {
      const yr = yearData.years[0];
      rows += '<tr><td class="period">Year ' + year +
              '</td><td class="blocks">' + fmt(yr.block_start) +
              '</td><td class="blocks">' + fmt(yr.block_end) +
              '</td><td class="count-cell">' + fmt(yr.count) + '</td></tr>';
    }

    resultsBody.innerHTML = rows;
    resultsDiv.style.display = 'block';
  } catch (e) {
    resultsBody.innerHTML = '<tr><td colspan="4" style="color:#ff4444">rekt. try again.</td></tr>';
    resultsDiv.style.display = 'block';
  }
  loading.style.display = 'none';
}

dp.addEventListener('change', lookup);
lookup();

// Interactive endpoint examples
const examples = {
  block: {
    curl: '/api/block/1752521',
    resp: JSON.stringify({"height":1752521,"timestamp_ms":1774800957664,"datetime":"2026-03-29T16:15:57.664000"}, null, 2)
  },
  blocks: {
    curl: '/api/blocks?from=1752000&to=1752005',
    resp: JSON.stringify({"blocks":[{"height":1752000,"timestamp_ms":1774738527691,"datetime":"2026-03-28T22:55:27.691000"},{"height":1752001,"timestamp_ms":1774738620113,"datetime":"2026-03-28T22:57:00.113000"}],"count":2}, null, 2).replace('}]',"},\n    ...\n  ]")
  },
  days: {
    curl: '/api/days?date=2026-03-29',
    resp: JSON.stringify({"days":[{"date":"2026-03-29","year":2026,"month":3,"day":29,"block_start":1752068,"block_end":1752671,"count":604}],"count":1}, null, 2)
  },
  weeks: {
    curl: '/api/weeks?year=2026&week=14',
    resp: JSON.stringify({"weeks":[{"year":2026,"week":14,"label":"W14","block_start":1747799,"block_end":1752671,"date_start":"2026-03-23","date_end":"2026-03-29"}],"count":1}, null, 2)
  },
  months: {
    curl: '/api/months?year=2026&month=3',
    resp: JSON.stringify({"months":[{"year":2026,"month":3,"name":"March","label":"M03","block_start":1732084,"block_end":1752671,"date_start":"2026-03-01","date_end":"2026-03-29"}],"count":1}, null, 2)
  },
  years: {
    curl: '/api/years?year=2026',
    resp: JSON.stringify({"years":[{"year":2026,"block_start":1689941,"block_end":1752671,"count":62731,"date_start":"2026-01-01","date_end":"2026-03-29"}],"count":1}, null, 2)
  },
  info: {
    curl: '/api/info',
    resp: JSON.stringify({"latest_height":1752671,"first_height":2,"total_blocks":1752670,"years":{"2019":{"min_height":2,"max_height":132121,"count":132120},"...":"..."}}, null, 2)
  }
};

const exPre = document.getElementById('example-code');
const cards = document.querySelectorAll('.ep-card[data-ep]');

function showExample(key) {
  cards.forEach(c => c.classList.remove('active'));
  document.querySelector('[data-ep="' + key + '"]').classList.add('active');
  const ex = examples[key];
  const host = window.location.origin;
  exPre.innerHTML = '<span class="k">$$</span> curl "' + host + ex.curl + '"\n\n' + ex.resp;
}

cards.forEach(card => {
  card.addEventListener('click', () => showExample(card.dataset.ep));
});

showExample('block');
</script>

</body>
</html>""")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        index = load_index()
        host = self.headers.get('host', 'ergo-block-timestamps.vercel.app')
        from datetime import datetime, timezone
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        page = HTML.substitute(
            total_blocks=f"{index['total_blocks']:,}",
            first_height=f"{index['first_height']:,}",
            latest_height=f"{index['latest_height']:,}",
            base_url=f"https://{host}",
            today=today,
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(page.encode())
