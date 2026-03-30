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
  .tz-toggle { display: flex; gap: 0; border-radius: 5px; overflow: hidden; border: 1px solid #2a2a3e; margin-left: auto; }
  .tz-btn {
    font-family: 'JetBrains Mono', monospace; font-size: 0.78em;
    background: #12121c; color: #555; border: none; padding: 6px 12px;
    cursor: pointer; transition: all 0.2s; white-space: nowrap;
  }
  .tz-btn:hover { color: #888; }
  .tz-btn.active { background: rgba(0,255,136,0.1); color: #00ff88; }
  .time-range { font-family: 'JetBrains Mono', monospace; font-size: 0.85em; color: #888; white-space: nowrap; }

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

  /* Code block with header */
  .code-block { border-radius: 8px; border: 1px solid #1a1a2e; overflow: hidden; margin-top: 8px; }
  .code-header {
    background: #12121c; padding: 10px 16px;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #1a1a2e;
  }
  .code-title { font-family: 'JetBrains Mono', monospace; font-size: 0.82em; color: #9d4edd; }
  .copy-btn {
    font-family: 'JetBrains Mono', monospace; font-size: 0.75em;
    background: rgba(0,255,136,0.08); color: #00ff88; border: 1px solid rgba(0,255,136,0.2);
    padding: 4px 12px; border-radius: 4px; cursor: pointer; transition: all 0.2s;
  }
  .copy-btn:hover { background: rgba(0,255,136,0.15); border-color: #00ff88; }
  .code-block pre { margin: 0; border: none; border-radius: 0; max-height: 400px; overflow-y: auto; }
  .code-dim { color: #333; }
  .code-loading { color: #9d4edd; }

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
    <div class="tz-toggle">
      <button class="tz-btn active" id="tz-utc" onclick="setTZ('UTC')">UTC</button>
      <button class="tz-btn" id="tz-local" onclick="setTZ('local')"></button>
    </div>
  </div>
  <div class="results" id="results">
    <table>
      <thead>
        <tr><th>Period</th><th>Block Start</th><th>Block End</th><th>Time Range</th><th>Blocks</th></tr>
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
<div class="code-block">
  <div class="code-header">
    <span class="code-title" id="code-title">GET /api/block/1752521</span>
    <button class="copy-btn" id="copy-btn" onclick="copyCode()">Copy</button>
  </div>
  <pre id="example-code"><span class="code-dim">click an endpoint card above...</span></pre>
</div>

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
var dp = document.getElementById('datepicker');
var resultsDiv = document.getElementById('results');
var resultsBody = document.getElementById('results-body');
var loading = document.getElementById('loading');
var currentTZ = 'UTC';
var localTZName = Intl.DateTimeFormat().resolvedOptions().timeZone;
var lastLookupData = null;

// Set local TZ button label
document.getElementById('tz-local').textContent = localTZName.split('/').pop().replace(/_/g, ' ');

function fmt(n) { return n.toLocaleString(); }

function fmtTime(ts_ms, tz) {
  var d = new Date(ts_ms);
  var opts = { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: tz === 'UTC' ? 'UTC' : localTZName };
  return d.toLocaleTimeString('en-GB', opts);
}

function fmtDateTime(ts_ms, tz) {
  var d = new Date(ts_ms);
  var tzName = tz === 'UTC' ? 'UTC' : localTZName;
  var opts = { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: tzName };
  return d.toLocaleDateString('en-GB', opts);
}

function setTZ(tz) {
  currentTZ = tz;
  document.getElementById('tz-utc').classList.toggle('active', tz === 'UTC');
  document.getElementById('tz-local').classList.toggle('active', tz === 'local');
  if (lastLookupData) renderResults(lastLookupData);
}

function getISOWeek(d) {
  var date = new Date(d.getTime());
  date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7));
  var yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  var weekNo = Math.ceil(((date - yearStart) / 86400000 + 1) / 7);
  return { year: date.getUTCFullYear(), week: weekNo };
}

function timeCell(startTs, endTs) {
  if (!startTs || !endTs) return '<td class="time-range" style="color:#333">-</td>';
  return '<td class="time-range">' + fmtDateTime(startTs, currentTZ) + ' &rarr; ' + fmtTime(endTs, currentTZ) + '</td>';
}

function renderResults(data) {
  var rows = '';
  for (var i = 0; i < data.length; i++) {
    var r = data[i];
    if (r.empty) {
      rows += '<tr><td class="period">' + r.label + '</td><td colspan="4" style="color:#333">no blocks mined</td></tr>';
    } else {
      rows += '<tr><td class="period">' + r.label + '</td>' +
              '<td class="blocks">' + fmt(r.block_start) + '</td>' +
              '<td class="blocks">' + fmt(r.block_end) + '</td>' +
              timeCell(r.ts_start, r.ts_end) +
              '<td class="count-cell">' + fmt(r.count) + '</td></tr>';
    }
  }
  resultsBody.innerHTML = rows;
  resultsDiv.style.display = 'block';
}

async function lookup() {
  var dateStr = dp.value;
  if (!dateStr) return;

  loading.style.display = 'block';
  resultsDiv.style.display = 'none';

  var parts = dateStr.split('-');
  var year = parseInt(parts[0]);
  var month = parseInt(parts[1]);
  var d = new Date(dateStr + 'T00:00:00Z');
  var iso = getISOWeek(d);

  try {
    var results = await Promise.all([
      fetch('/api/days?date=' + dateStr).then(function(r) { return r.json(); }),
      fetch('/api/weeks?year=' + iso.year + '&week=' + iso.week).then(function(r) { return r.json(); }),
      fetch('/api/months?year=' + year + '&month=' + month).then(function(r) { return r.json(); }),
      fetch('/api/years?year=' + year).then(function(r) { return r.json(); }),
    ]);

    var dayData = results[0], weekData = results[1], monthData = results[2], yearData = results[3];
    var data = [];

    // Collect block IDs we need timestamps for
    var blockIds = [];

    if (dayData.days && dayData.days.length > 0) {
      var dy = dayData.days[0];
      blockIds.push(dy.block_start, dy.block_end);
      data.push({ label: dateStr, block_start: dy.block_start, block_end: dy.block_end, count: dy.count, ts_start: null, ts_end: null });
    } else {
      data.push({ label: dateStr, empty: true });
    }

    if (weekData.weeks && weekData.weeks.length > 0) {
      var wk = weekData.weeks[0];
      blockIds.push(wk.block_start, wk.block_end);
      data.push({ label: 'Week ' + wk.label + ' / ' + iso.year, block_start: wk.block_start, block_end: wk.block_end, count: wk.block_end - wk.block_start + 1, ts_start: null, ts_end: null });
    }

    if (monthData.months && monthData.months.length > 0) {
      var mo = monthData.months[0];
      blockIds.push(mo.block_start, mo.block_end);
      data.push({ label: mo.name + ' ' + year, block_start: mo.block_start, block_end: mo.block_end, count: mo.block_end - mo.block_start + 1, ts_start: null, ts_end: null });
    }

    if (yearData.years && yearData.years.length > 0) {
      var yr = yearData.years[0];
      blockIds.push(yr.block_start, yr.block_end);
      data.push({ label: 'Year ' + year, block_start: yr.block_start, block_end: yr.block_end, count: yr.count, ts_start: null, ts_end: null });
    }

    // Fetch timestamps for boundary blocks (deduplicated)
    var unique = Array.from(new Set(blockIds));
    var tsMap = {};
    var tsResults = await Promise.all(unique.map(function(h) {
      return fetch('/api/block/' + h).then(function(r) { return r.json(); });
    }));
    for (var i = 0; i < unique.length; i++) {
      tsMap[unique[i]] = tsResults[i].timestamp_ms;
    }

    // Fill in timestamps
    for (var j = 0; j < data.length; j++) {
      if (!data[j].empty) {
        data[j].ts_start = tsMap[data[j].block_start];
        data[j].ts_end = tsMap[data[j].block_end];
      }
    }

    lastLookupData = data;
    renderResults(data);
  } catch (e) {
    resultsBody.innerHTML = '<tr><td colspan="5" style="color:#ff4444">rekt. try again.</td></tr>';
    resultsDiv.style.display = 'block';
  }
  loading.style.display = 'none';
}

dp.addEventListener('change', lookup);
lookup();

// Interactive endpoint examples — live fetch
var endpoints = {
  block:  '/api/block/1752521',
  blocks: '/api/blocks?from=1752500&to=1752505',
  days:   '/api/days?date=2026-03-29',
  weeks:  '/api/weeks?year=2026&week=13',
  months: '/api/months?year=2026&month=3',
  years:  '/api/years?year=2026',
  info:   '/api/info'
};

var exPre = document.getElementById('example-code');
var codeTitle = document.getElementById('code-title');
var cards = document.querySelectorAll('.ep-card[data-ep]');
var lastResponse = '';

function copyCode() {
  navigator.clipboard.writeText(lastResponse).then(function() {
    var btn = document.getElementById('copy-btn');
    btn.textContent = 'Copied!';
    setTimeout(function() { btn.textContent = 'Copy'; }, 1500);
  });
}

function showExample(key) {
  cards.forEach(function(c) { c.classList.remove('active'); });
  var card = document.querySelector('[data-ep="' + key + '"]');
  if (card) card.classList.add('active');
  var path = endpoints[key];
  codeTitle.textContent = 'GET ' + path;
  exPre.innerHTML = '<span class="code-loading">fetching...</span>';

  fetch(path)
    .then(function(r) { return r.json(); })
    .then(function(data) {
      lastResponse = JSON.stringify(data, null, 2);
      exPre.textContent = lastResponse;
    })
    .catch(function() {
      exPre.innerHTML = '<span class="code-dim">request failed</span>';
    });
}

cards.forEach(function(card) {
  card.addEventListener('click', function() { showExample(card.dataset.ep); });
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
