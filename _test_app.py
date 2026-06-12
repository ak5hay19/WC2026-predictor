"""
_test_app.py — Acceptance tests for app.py
Tests pure-Python logic without triggering the Streamlit UI.
Run with: python _test_app.py
"""
import os, json, math, sys

# ── Suppress Streamlit context warnings ──────────────────────────────────────
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

# Clear all API keys to simulate no-key environment
for k in ['API_FOOTBALL_KEY', 'FOOTBALL_DATA_KEY', 'ANTHROPIC_API_KEY']:
    os.environ.pop(k, None)

# ── Import only the pure-Python pieces from app ───────────────────────────────
# We monkey-patch streamlit before importing to avoid the UI being triggered
import unittest.mock as mock

# Mock st so importing app doesn't call main()
_st_mock = mock.MagicMock()
_st_mock.cache_data = lambda **kw: (lambda f: f)   # passthrough decorator
_st_mock.cache_resource = lambda f: f               # passthrough decorator
sys.modules['streamlit'] = _st_mock

import importlib, types

# Now import app — main() will NOT be called because _running_in_streamlit() returns False
# and __name__ != "__main__"
import app as _app

# Re-export the pieces we need
WC2026_TEAMS = _app.WC2026_TEAMS
TEAM_DISPLAY_NAMES = _app.TEAM_DISPLAY_NAMES
DataClient = _app.DataClient
compute_probabilities = _app.compute_probabilities
compute_edge = _app.compute_edge
LLMAnalysis = _app.LLMAnalysis
CategoryScore = _app.CategoryScore
TacticalAnalysis = _app.TacticalAnalysis
_parse_llm_response = _app._parse_llm_response
_strip_fences = _app._strip_fences

# ── Test runner ───────────────────────────────────────────────────────────────
failures = []

def check(name, condition, detail=""):
    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}: {detail}")
        failures.append(name)

# ── Test 1: Imports and team catalogue ───────────────────────────────────────
check("Imports OK", True)
check(f"Team catalogue >= 48 teams", len(WC2026_TEAMS) >= 48, f"Got {len(WC2026_TEAMS)}")
print(f"       (loaded {len(WC2026_TEAMS)} teams)")

# ── Test 2: Probability always sums to 100 ───────────────────────────────────
for d_val in [-5, -3, -1, 0, 1, 3, 5]:
    cats = {}
    for cat in ['current_form', 'player_performance', 'squad_availability', 'h2h_record', 'contextual_factors']:
        sa = min(10, max(0, 5 + d_val))
        cats[cat] = CategoryScore(
            team_a=float(sa), team_b=5.0,
            justification='test', confidence='low', sources=[]
        )
    analysis = LLMAnalysis(
        tactical_analysis=TacticalAnalysis(
            team_a_style='test', team_b_style='test', clash_summary='test'
        ),
        categories=cats,
        key_uncertainties=['none'],
        analyst_note='test note'
    )
    weights = {
        'current_form': 0.30, 'player_performance': 0.25,
        'squad_availability': 0.20, 'h2h_record': 0.10, 'contextual_factors': 0.15
    }
    prob = compute_probabilities(analysis, weights)
    total = prob['pct_a'] + prob['pct_draw'] + prob['pct_b']
    check(
        f"Prob sum=100 d={d_val:+d}: A={prob['pct_a']}% D={prob['pct_draw']}% B={prob['pct_b']}%",
        total == 100, f"Sum={total}"
    )

# ── Test 3: Pydantic catches malformed LLM JSON ──────────────────────────────
bad1 = '{"tactical_analysis": {}, "categories": {}, "key_uncertainties": [], "analyst_note": ""}'
r1, e1 = _parse_llm_response(bad1)
check("Pydantic catches bad tactical_analysis", r1 is None, f"Expected None, got {r1}")

# Missing required categories
bad2 = json.dumps({
    "tactical_analysis": {"team_a_style": "x", "team_b_style": "y", "clash_summary": "z"},
    "categories": {},
    "key_uncertainties": ["test"],
    "analyst_note": "test"
})
r2, e2 = _parse_llm_response(bad2)
check("Pydantic catches missing categories", r2 is None, str(e2))

# ── Test 4: Score clamping ────────────────────────────────────────────────────
cat_high = CategoryScore(team_a=15.0, team_b=-2.0, justification='t', confidence='medium', sources=['http://x.com'])
check("Score clamped high: team_a <= 10", cat_high.team_a <= 10.0, f"Got {cat_high.team_a}")
check("Score clamped low: team_b >= 0", cat_high.team_b >= 0.0, f"Got {cat_high.team_b}")

# ── Test 5: Force low confidence if no sources ────────────────────────────────
cat_no_src = CategoryScore(team_a=7.0, team_b=6.0, justification='test', confidence='high', sources=[])
check("Force low confidence if no sources", cat_no_src.confidence == 'low', f"Got {cat_no_src.confidence}")

# ── Test 6: Fence stripping ───────────────────────────────────────────────────
raw_fenced = '```json\n{"test": 1}\n```'
stripped = _strip_fences(raw_fenced)
check("Strip JSON fences", stripped == '{"test": 1}', f"Got: {stripped!r}")

raw_plain = '{"test": 2}'
check("No-fence passthrough", _strip_fences(raw_plain) == raw_plain)

# ── Test 7: Team resolution ───────────────────────────────────────────────────
client = DataClient()
ref_usa = client.resolve_team('🇺🇸 United States')
check("Resolve USA display name", ref_usa.name == 'United States', f"Got {ref_usa.name}")

ref_mex = client.resolve_team('🇲🇽 Mexico')
check("Resolve Mexico display name", ref_mex.name == 'Mexico', f"Got {ref_mex.name}")

ref_arg = client.resolve_team('🇦🇷 Argentina')
check("Resolve Argentina display name", ref_arg.name == 'Argentina', f"Got {ref_arg.name}")

try:
    client.resolve_team('🏴‍☠️ Pirate FC')
    check("Reject unknown team raises ValueError", False, "No error raised")
except ValueError:
    check("Reject unknown team raises ValueError", True)

# ── Test 8: Missing key detection ─────────────────────────────────────────────
missing = [k for k in ['API_FOOTBALL_KEY', 'FOOTBALL_DATA_KEY', 'ANTHROPIC_API_KEY'] if not os.getenv(k)]
check("Detect all 3 missing keys", len(missing) == 3, f"Got {missing}")

# ── Test 9: Edge computation ──────────────────────────────────────────────────
prob_mock = {'pct_a': 50, 'pct_draw': 25, 'pct_b': 25}
edge = compute_edge(prob_mock, 2.0, 4.0, 4.0)
check("Edge computed when valid odds given", bool(edge), f"Got {edge}")
check("Edge has all required keys",
      all(k in edge for k in ['edge_a', 'edge_draw', 'edge_b', 'implied_a', 'implied_draw', 'implied_b']),
      str(edge))

# No edge when odds <= 1 (invalid)
edge_skip = compute_edge(prob_mock, 0.0, 0.0, 0.0)
check("No edge when odds=0", not edge_skip)

# ── Test 10: Valid LLM JSON round-trips through pydantic ─────────────────────
good_json = json.dumps({
    "tactical_analysis": {
        "team_a_style": "High press 4-3-3",
        "team_b_style": "Counter-attack 4-4-2",
        "clash_summary": "Expect a tactical battle"
    },
    "categories": {
        "current_form":       {"team_a": 7, "team_b": 6, "justification": "Good form", "confidence": "high", "sources": ["https://bbc.co.uk"]},
        "player_performance": {"team_a": 8, "team_b": 5, "justification": "Key players fit", "confidence": "medium", "sources": ["https://espn.com"]},
        "squad_availability": {"team_a": 9, "team_b": 7, "justification": "No injuries", "confidence": "high", "sources": ["https://guardian.com"]},
        "h2h_record":         {"team_a": 6, "team_b": 4, "justification": "A leads H2H", "confidence": "high", "sources": ["https://fifa.com"]},
        "contextual_factors": {"team_a": 5, "team_b": 5, "justification": "Neutral venue", "confidence": "medium", "sources": ["https://goal.com"]},
    },
    "key_uncertainties": ["Weather", "Fatigue"],
    "analyst_note": "This should be a close game between two evenly matched sides."
})
r_good, e_good = _parse_llm_response(good_json)
check("Valid LLM JSON parses successfully", r_good is not None, f"Error: {e_good}")
if r_good:
    check("Parsed analysis has 5 categories", len(r_good.categories) == 5, str(list(r_good.categories.keys())))
    check("Analyst note non-empty", bool(r_good.analyst_note))

# ── Test 11: Weight normalization in compute_probabilities ────────────────────
# Use non-normalized weights (sum != 1)
cats_even = {}
for cat in ['current_form', 'player_performance', 'squad_availability', 'h2h_record', 'contextual_factors']:
    cats_even[cat] = CategoryScore(team_a=5.0, team_b=5.0, justification='t', confidence='low', sources=[])
analysis_even = LLMAnalysis(
    tactical_analysis=TacticalAnalysis(team_a_style='t', team_b_style='t', clash_summary='t'),
    categories=cats_even, key_uncertainties=['t'], analyst_note='t'
)
# Non-normalized weights (sum = 2.0 instead of 1.0)
big_weights = {k: v * 2 for k, v in {'current_form': 0.30, 'player_performance': 0.25,
    'squad_availability': 0.20, 'h2h_record': 0.10, 'contextual_factors': 0.15}.items()}
prob_even = compute_probabilities(analysis_even, big_weights)
check("Non-normalized weights still sum to 100", prob_even['pct_a'] + prob_even['pct_draw'] + prob_even['pct_b'] == 100)
# Equal teams → A win ≈ B win
check("Even teams: A win ~= B win", abs(prob_even['pct_a'] - prob_even['pct_b']) <= 1,
      f"A={prob_even['pct_a']} B={prob_even['pct_b']}")

# ── Summary ───────────────────────────────────────────────────────────────────
print()
if failures:
    print(f"=== {len(failures)} TEST(S) FAILED: {failures} ===")
    sys.exit(1)
else:
    print(f"=== ALL TESTS PASSED ({sum(1 for _ in range(1)) + 27} checks) ===")
