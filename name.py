"""
Name Nationality Predictor — FastAPI + User-Friendly Web Interface
-------------------------------------------------------------------
• Serves a polished HTML frontend at http://127.0.0.1:8000
• Accepts a name as input via the web form
• Calls nationalize.io to predict nationalities
• Resolves ISO country codes → full country names via pycountry
• Displays flag emojis and probability bars in the browser
• Prints all country names to the terminal on each request

Run:
    pip install fastapi uvicorn requests pycountry
    python nationalize_app.py

Then open:  http://127.0.0.1:8000
"""

import requests
import pycountry
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

# ─────────────────────────────────────────────
#  App setup
# ─────────────────────────────────────────────

app = FastAPI(
    title="Name Nationality Predictor",
    description="Predicts nationalities for any name using the nationalize.io API.",
    version="2.0.0",
)

# ─────────────────────────────────────────────
#  HTML frontend (served at /)
# ─────────────────────────────────────────────

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Name Nationality Predictor</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --brand:   #4f6ef7;
      --brand-h: #3a57e8;
      --bg:      #f1f5fb;
      --card:    #ffffff;
      --border:  #e2e8f0;
      --text:    #1e293b;
      --sub:     #64748b;
      --muted:   #94a3b8;
      --row-bg:  #f8fafc;
      --error-bg:#fff1f2;
      --error-bd:#fecdd3;
      --error-tx:#be123c;
      --radius:  14px;
    }

    body {
      font-family: 'DM Sans', sans-serif;
      background: var(--bg);
      min-height: 100vh;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      padding: 3rem 1rem 4rem;
    }

    .card {
      background: var(--card);
      border-radius: 22px;
      box-shadow: 0 2px 8px rgba(0,0,0,.06), 0 12px 40px rgba(0,0,0,.08);
      padding: 2.5rem 2rem 2rem;
      width: 100%;
      max-width: 540px;
    }

    /* ── Header ── */
    .header { text-align: center; margin-bottom: 2rem; }
    .globe  { font-size: 3rem; line-height: 1; margin-bottom: .6rem; }
    .header h1 {
      font-size: 1.55rem;
      font-weight: 700;
      color: var(--text);
      letter-spacing: -.02em;
    }
    .header p  { font-size: .92rem; color: var(--sub); margin-top: .35rem; }

    /* ── Search row ── */
    .search-row {
      display: flex;
      gap: 10px;
      margin-bottom: 1.75rem;
    }

    .search-row input {
      flex: 1;
      padding: .78rem 1.1rem;
      border: 1.8px solid var(--border);
      border-radius: var(--radius);
      font-size: 1rem;
      font-family: inherit;
      color: var(--text);
      background: #fafbfc;
      outline: none;
      transition: border-color .18s, box-shadow .18s;
    }
    .search-row input::placeholder { color: var(--muted); }
    .search-row input:focus {
      border-color: var(--brand);
      box-shadow: 0 0 0 3px rgba(79,110,247,.12);
      background: #fff;
    }

    .search-row button {
      padding: .78rem 1.4rem;
      background: var(--brand);
      color: #fff;
      border: none;
      border-radius: var(--radius);
      font-size: .97rem;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      transition: background .18s, transform .1s, box-shadow .18s;
      white-space: nowrap;
    }
    .search-row button:hover  { background: var(--brand-h); box-shadow: 0 4px 14px rgba(79,110,247,.35); }
    .search-row button:active { transform: scale(.97); }
    .search-row button:disabled { background: var(--muted); cursor: not-allowed; box-shadow: none; }

    /* ── Results ── */
    #results-section { display: none; }

    .results-label {
      font-size: .78rem;
      font-weight: 700;
      letter-spacing: .07em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: .85rem;
    }

    .result-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: .85rem 1rem;
      border-radius: 12px;
      background: var(--row-bg);
      border: 1px solid var(--border);
      margin-bottom: .55rem;
      transition: box-shadow .15s;
    }
    .result-item:hover { box-shadow: 0 2px 10px rgba(0,0,0,.07); }

    .country-left  { display: flex; align-items: center; gap: 12px; min-width: 0; }
    .flag          { font-size: 1.65rem; line-height: 1; flex-shrink: 0; }
    .country-name  { font-size: .97rem; font-weight: 600; color: var(--text); }
    .country-code  { font-size: .77rem; color: var(--muted); margin-top: 2px; }

    .bar-group     { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
    .bar-bg        { width: 100px; height: 7px; background: var(--border); border-radius: 99px; overflow: hidden; }
    .bar-fill      { height: 100%; background: var(--brand); border-radius: 99px; }
    .pct           { font-size: .85rem; font-weight: 700; color: var(--brand); min-width: 42px; text-align: right; }

    .meta {
      text-align: center;
      font-size: .8rem;
      color: var(--muted);
      margin-top: 1.1rem;
    }

    /* ── States ── */
    .spinner { text-align: center; padding: 1.2rem 0; color: var(--muted); font-size: .9rem; }
    .spinner span { display: inline-block; animation: pulse 1.2s ease-in-out infinite; }
    @keyframes pulse { 0%,100%{opacity:.3} 50%{opacity:1} }

    .error-box {
      background: var(--error-bg);
      border: 1px solid var(--error-bd);
      color: var(--error-tx);
      border-radius: 10px;
      padding: .8rem 1rem;
      font-size: .88rem;
      text-align: center;
    }
  </style>
</head>
<body>
<div class="card">
  <div class="header">
    <div class="globe">🌍</div>
    <h1>Name Nationality Predictor</h1>
    <p>Enter any first name to discover its most likely nationalities</p>
  </div>

  <div class="search-row">
    <input
      id="nameInput"
      type="text"
      placeholder="e.g. Nathaniel, Ali, Sofia, Yuki…"
      autocomplete="off"
    />
    <button id="predictBtn" onclick="predict()">Predict</button>
  </div>

  <div id="results-section">
    <div class="results-label" id="resultsLabel"></div>
    <div id="resultsList"></div>
    <div class="meta" id="resultsMeta"></div>
  </div>
</div>

<script>
  document.getElementById('nameInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') predict();
  });

  /* Convert ISO alpha-2 code to flag emoji */
  function toFlag(code) {
    if (!code || code.length !== 2) return '🏳️';
    return [...code.toUpperCase()].map(c =>
      String.fromCodePoint(0x1F1E6 - 65 + c.charCodeAt(0))
    ).join('');
  }

  async function predict() {
    const input  = document.getElementById('nameInput');
    const btn    = document.getElementById('predictBtn');
    const sec    = document.getElementById('results-section');
    const list   = document.getElementById('resultsList');
    const label  = document.getElementById('resultsLabel');
    const meta   = document.getElementById('resultsMeta');

    const name = input.value.trim();
    if (!name) { input.focus(); return; }

    /* Loading state */
    btn.disabled   = true;
    btn.textContent = 'Loading…';
    sec.style.display = 'block';
    list.innerHTML = '<div class="spinner"><span>Fetching predictions…</span></div>';
    label.textContent = '';
    meta.textContent  = '';

    try {
      const res  = await fetch('http://192.168.100.90:8000/predict?name=' + encodeURIComponent(name));
      const data = await res.json();

      if (!res.ok) {
        list.innerHTML = `<div class="error-box">${data.detail || 'Something went wrong. Please try again.'}</div>`;
        return;
      }

      label.textContent = `Results for "${data.name}"`;
      meta.textContent  = `Based on ${data.count.toLocaleString()} records`;

      list.innerHTML = data.predictions.map(p => `
        <div class="result-item">
          <div class="country-left">
            <span class="flag">${toFlag(p.country_code)}</span>
            <div>
              <div class="country-name">${p.country_name}</div>
              <div class="country-code">${p.country_code}</div>
            </div>
          </div>
          <div class="bar-group">
            <div class="bar-bg">
              <div class="bar-fill" style="width:${Math.min(p.probability, 100)}%"></div>
            </div>
            <div class="pct">${p.probability.toFixed(1)}%</div>
          </div>
        </div>
      `).join('');

    } catch {
      list.innerHTML = '<div class="error-box">Network error — make sure the server is running.</div>';
    } finally {
      btn.disabled    = false;
      btn.textContent = 'Predict';
    }
  }
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def get_country_name(code: str) -> str:
    """Resolve an ISO 3166-1 alpha-2 code to a full country name."""
    country = pycountry.countries.get(alpha_2=code.upper())
    return country.name if country else f"Unknown ({code})"


def fetch_nationalize(name: str) -> dict:
    """Fetch nationality predictions from nationalize.io."""
    response = requests.get(
        "https://api.nationalize.io",
        params={"name": name},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    """Serve the web interface."""
    return HTML_PAGE


@app.get("/predict", summary="Predict nationalities for a given name")
def predict_nationality(
    name: str = Query(..., min_length=1, description="First name to analyse")
):
    """
    Calls nationalize.io, maps country codes to full names,
    prints results to the terminal, and returns JSON to the browser.
    """
    data = fetch_nationalize(name)
    countries = data.get("country", [])

    if not countries:
        raise HTTPException(
            status_code=404,
            detail=f"No nationality predictions found for '{name}'. Try a different name."
        )

    results = []
    print(f"\n  Predictions for: '{name}'")
    print("  " + "─" * 43)

    for entry in countries:
        code        = entry.get("country_id", "")
        probability = entry.get("probability", 0)
        full_name   = get_country_name(code)

        results.append({
            "country_code": code,
            "country_name": full_name,
            "probability":  round(probability * 100, 2),
        })

        print(f"  {full_name:<35} ({code})  {probability * 100:.2f}%")

    print("  " + "─" * 43 + "\n")

    return {
        "name":        data.get("name"),
        "count":       data.get("count"),
        "predictions": results,
    }


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  ┌─────────────────────────────────────────┐")
    print("  │   Name Nationality Predictor  v2.0      │")
    print("  ├─────────────────────────────────────────┤")
    print("  │  Web UI  →  http://192.168.100.90:8000       │")
    print("  │  API docs→  http://192.168.100.90:8000/docs  │")
    print("  └─────────────────────────────────────────┘\n")

    uvicorn.run(app, host="192.168.100.90", port=8000)