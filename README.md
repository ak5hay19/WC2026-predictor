# 🏆 WC 2026 Predictive Analytics Engine

A single-file Streamlit dashboard for analyzing FIFA World Cup 2026 matchups.
Select two national teams and the app will:

1. **Pull verified structured data** (fixture, venue, kickoff, recent results, H2H) from
   football data APIs — with automatic fallback between providers.
2. **Augment with LLM + web search** via Claude for qualitative analysis (form narrative,
   tactics, injuries, key players).
3. **Compute win/draw/loss probabilities deterministically in Python** from weighted
   category scores — the LLM never emits probabilities.

> **Anti-hallucination design:** The LLM is *never* the source of truth for facts.
> Facts come from the data API. The LLM only scores and explains.

---

## Prerequisites

- Python 3.11 or higher
- pip

---

## Setup

### 1. Clone / navigate to the project directory

```bash
cd c:\garrison\Prediction
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

Copy the example env file and fill in your keys:

```bash
copy .env.example .env
```

Then edit `.env`:

```
API_FOOTBALL_KEY=your_key_here
FOOTBALL_DATA_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Where to get each free API key

| Key | Service | URL | Free Tier |
|-----|---------|-----|-----------|
| `API_FOOTBALL_KEY` | API-Football (api-sports.io) — **primary data source** | https://www.api-football.com/ | 100 requests/day |
| `FOOTBALL_DATA_KEY` | football-data.org — **fallback data source** | https://www.football-data.org/client/register | 10 requests/minute |
| `ANTHROPIC_API_KEY` | Anthropic Claude — **LLM + web search** | https://console.anthropic.com/ | Pay-per-use (~$3 per 1M tokens) |

> **Note:** The app boots and displays the team selector without any keys set.
> At least `ANTHROPIC_API_KEY` and one football data key are required to run an analysis.

---

## Run

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Architecture Overview

```
app.py
├── WC2026_TEAMS          — 48 qualified teams with aliases, flag emoji, API IDs
├── DataClient            — Structured data layer
│   ├── resolve_team()    — Alias resolution
│   ├── get_fixture()     — API-Football → football-data.org fallback
│   ├── get_last_results()— API-Football → football-data.org fallback
│   └── get_h2h()         — API-Football primary
├── run_llm_analysis()    — Claude claude-sonnet-4-6 + web_search_20250305 tool
│   └── parse → repair-retry → raw-text-fallback loop
├── compute_probabilities()— Deterministic logistic + draw model
│   └── P always sums to exactly 100%
└── main()                — Streamlit UI: 5 result cards + sidebar
```

### Probability Engine

Given LLM category scores (0–10) for each team:

1. Weighted sum `S_a`, `S_b` using sidebar-tunable weights (renormalized to sum to 1)
2. Strength gap `d = S_a − S_b`
3. Logistic model: `p_a_raw = 1 / (1 + exp(−k·d))` with sidebar-tunable sharpness `k`
4. Draw model: `p_draw = D_max · exp(−d²/τ)` (≈ 30% for even sides, shrinks with gap)
5. Final: `p_a = p_a_raw(1−p_draw)`, `p_b = (1−p_a_raw)(1−p_draw)`
6. Round to whole %, force sum = 100 (adjust largest bucket)

---

## Sidebar Controls

| Control | Description |
|---------|-------------|
| **Category Weights** | Five sliders (form, players, availability, H2H, context) — live renormalized |
| **Sharpness k** | How strongly score gap translates to probability gap (default 0.45) |
| **Bookmaker Odds** | Optional: paste decimal odds to see model edge table |
| **Clear Cache** | Clears all `st.cache_data` and `st.cache_resource` |
| **Ping APIs** | Tests connectivity to each data provider |

---

## Data Caching

- Football data API calls: **15-minute TTL** (`st.cache_data(ttl=900)`)
- LLM analysis: **30-minute TTL** (`st.cache_data(ttl=1800)`), keyed by (team_a, team_b, date)

---

## Logging

Every analysis is appended to `analysis_log.jsonl` in the project directory.
Each line is a JSON record with: timestamp, teams, scores per category, final probabilities,
weights used, and source URLs. Use this to back-test predictions against actual results.

---

## Error Handling

| Failure | Behavior |
|---------|----------|
| Missing API keys | Setup screen listing which vars to set; app still boots |
| API timeout (8s) | Falls through fallback chain with visible warning banner |
| Rate limit / HTTP error | Falls through to next provider; warning shown |
| LLM JSON parse failure | One repair retry; if still fails, shows raw text in expander |
| LLM timeout (90s) | `st.error` with message; other cards still render |
| Any external call | Wrapped in try/except; failure degrades one card only |

---

## Acceptance Criteria

- [x] `streamlit run app.py` boots with no env vars set → shows setup screen
- [x] Probabilities always sum to exactly 100
- [x] Pydantic v2 validates all LLM output; catches malformed JSON
- [x] Every external call wrapped in try/except; failures are isolated to one card
- [x] Hypothetical matchups show `HYPOTHETICAL MATCHUP` banner
- [x] Source + `fetched_at` shown on every data card
- [x] Sidebar weights live-renormalize and update probability display
- [x] `analysis_log.jsonl` written after every successful analysis
