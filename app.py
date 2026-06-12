"""
app.py — FIFA World Cup 2026 Predictive Analytics Dashboard
Single-file Streamlit application.
"""

from __future__ import annotations

import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Literal, Optional

import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator

load_dotenv()


def _running_in_streamlit() -> bool:
    """Return True when this file is executed by the Streamlit runner."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# 0. CONSTANTS & TEAM CATALOGUE
# ═══════════════════════════════════════════════════════════════════════════════

APP_TITLE = "🏆 WC 2026 Predictive Analytics Engine"
MODEL_ID = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
LOG_FILE = "analysis_log.jsonl"

# All 48 FIFA World Cup 2026 teams — verified from official draw
WC2026_TEAMS: list[dict] = [
    # Group A — Mexico, South Africa, South Korea, Czech Republic
    {"name": "Mexico",                 "flag": "🇲🇽", "group": "A", "aliases": ["mex", "el tri"],
     "api_football_id": 16,   "fd_id": "MEX"},
    {"name": "South Africa",           "flag": "🇿🇦", "group": "A", "aliases": ["rsa", "bafana bafana"],
     "api_football_id": 66,   "fd_id": "RSA"},
    {"name": "South Korea",            "flag": "🇰🇷", "group": "A", "aliases": ["kor", "korea republic", "korea"],
     "api_football_id": 23,   "fd_id": "KOR"},
    {"name": "Czech Republic",         "flag": "🇨🇿", "group": "A", "aliases": ["cze", "czechia"],
     "api_football_id": 798,  "fd_id": "CZE"},
    # Group B — Canada, Bosnia and Herzegovina, Qatar, Switzerland
    {"name": "Canada",                 "flag": "🇨🇦", "group": "B", "aliases": ["can"],
     "api_football_id": 3,    "fd_id": "CAN"},
    {"name": "Bosnia and Herzegovina", "flag": "🇧🇦", "group": "B",
     "aliases": ["bih", "bosnia", "bos", "bosnia & herzegovina", "bosnia herzegovina"],
     "api_football_id": 7947, "fd_id": "BIH"},
    {"name": "Qatar",                  "flag": "🇶🇦", "group": "B", "aliases": ["qat"],
     "api_football_id": 33,   "fd_id": "QAT"},
    {"name": "Switzerland",            "flag": "🇨🇭", "group": "B", "aliases": ["sui", "swi"],
     "api_football_id": 777,  "fd_id": "SUI"},
    # Group C — Brazil, Morocco, Haiti, Scotland
    {"name": "Brazil",                 "flag": "🇧🇷", "group": "C", "aliases": ["bra", "brasil"],
     "api_football_id": 9,    "fd_id": "BRA"},
    {"name": "Morocco",                "flag": "🇲🇦", "group": "C", "aliases": ["mar"],
     "api_football_id": 32,   "fd_id": "MAR"},
    {"name": "Haiti",                  "flag": "🇭🇹", "group": "C", "aliases": ["hai", "hti"],
     "api_football_id": 468,  "fd_id": "HAI"},
    {"name": "Scotland",               "flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "group": "C", "aliases": ["sco"],
     "api_football_id": 1108, "fd_id": "SCO"},
    # Group D — United States, Paraguay, Australia, Turkey
    {"name": "United States",          "flag": "🇺🇸", "group": "D",
     "aliases": ["usa", "usmnt", "us", "united states of america"],
     "api_football_id": 2,    "fd_id": "USA"},
    {"name": "Paraguay",               "flag": "🇵🇾", "group": "D", "aliases": ["par"],
     "api_football_id": 37,   "fd_id": "PAR"},
    {"name": "Australia",              "flag": "🇦🇺", "group": "D", "aliases": ["aus", "socceroos"],
     "api_football_id": 24,   "fd_id": "AUS"},
    {"name": "Turkey",                 "flag": "🇹🇷", "group": "D", "aliases": ["tur", "turkiye"],
     "api_football_id": 778,  "fd_id": "TUR"},
    # Group E — Germany, Curacao, Cote d'Ivoire, Ecuador
    {"name": "Germany",                "flag": "🇩🇪", "group": "E", "aliases": ["ger", "die mannschaft"],
     "api_football_id": 25,   "fd_id": "GER"},
    {"name": "Curacao",                "flag": "🇨🇼", "group": "E", "aliases": ["cur", "cuw", "curacao"],
     "api_football_id": 1569, "fd_id": "CUW"},
    {"name": "Cote d'Ivoire",          "flag": "🇨🇮", "group": "E",
     "aliases": ["civ", "ivory coast", "cote d ivoire", "ivory"],
     "api_football_id": 88,   "fd_id": "CIV"},
    {"name": "Ecuador",                "flag": "🇪🇨", "group": "E", "aliases": ["ecu"],
     "api_football_id": 131,  "fd_id": "ECU"},
    # Group F — Netherlands, Japan, Sweden, Tunisia
    {"name": "Netherlands",            "flag": "🇳🇱", "group": "F", "aliases": ["ned", "holland", "dutch"],
     "api_football_id": 1118, "fd_id": "NED"},
    {"name": "Japan",                  "flag": "🇯🇵", "group": "F", "aliases": ["jpn"],
     "api_football_id": 29,   "fd_id": "JPN"},
    {"name": "Sweden",                 "flag": "🇸🇪", "group": "F", "aliases": ["swe"],
     "api_football_id": 768,  "fd_id": "SWE"},
    {"name": "Tunisia",                "flag": "🇹🇳", "group": "F", "aliases": ["tun"],
     "api_football_id": 1359, "fd_id": "TUN"},
    # Group G — Belgium, Egypt, Iran, New Zealand
    {"name": "Belgium",                "flag": "🇧🇪", "group": "G", "aliases": ["bel", "red devils"],
     "api_football_id": 1326, "fd_id": "BEL"},
    {"name": "Egypt",                  "flag": "🇪🇬", "group": "G", "aliases": ["egy"],
     "api_football_id": 21,   "fd_id": "EGY"},
    {"name": "Iran",                   "flag": "🇮🇷", "group": "G", "aliases": ["irn", "iir"],
     "api_football_id": 20,   "fd_id": "IRN"},
    {"name": "New Zealand",            "flag": "🇳🇿", "group": "G", "aliases": ["nzl", "all whites"],
     "api_football_id": 95,   "fd_id": "NZL"},
    # Group H — Spain, Cape Verde, Saudi Arabia, Uruguay
    {"name": "Spain",                  "flag": "🇪🇸", "group": "H", "aliases": ["esp", "la roja"],
     "api_football_id": 9,    "fd_id": "ESP"},
    {"name": "Cape Verde",             "flag": "🇨🇻", "group": "H", "aliases": ["cpv", "cabo verde"],
     "api_football_id": 1591, "fd_id": "CPV"},
    {"name": "Saudi Arabia",           "flag": "🇸🇦", "group": "H", "aliases": ["ksa"],
     "api_football_id": 28,   "fd_id": "KSA"},
    {"name": "Uruguay",                "flag": "🇺🇾", "group": "H", "aliases": ["uru"],
     "api_football_id": 7,    "fd_id": "URU"},
    # Group I — France, Senegal, Iraq, Norway
    {"name": "France",                 "flag": "🇫🇷", "group": "I", "aliases": ["fra", "les bleus"],
     "api_football_id": 2,    "fd_id": "FRA"},
    {"name": "Senegal",                "flag": "🇸🇳", "group": "I", "aliases": ["sen"],
     "api_football_id": 34,   "fd_id": "SEN"},
    {"name": "Iraq",                   "flag": "🇮🇶", "group": "I", "aliases": ["irq"],
     "api_football_id": 1504, "fd_id": "IRQ"},
    {"name": "Norway",                 "flag": "🇳🇴", "group": "I", "aliases": ["nor"],
     "api_football_id": 1529, "fd_id": "NOR"},
    # Group J — Argentina, Algeria, Austria, Jordan
    {"name": "Argentina",              "flag": "🇦🇷", "group": "J", "aliases": ["arg", "albiceleste"],
     "api_football_id": 6,    "fd_id": "ARG"},
    {"name": "Algeria",                "flag": "🇩🇿", "group": "J", "aliases": ["alg", "dza"],
     "api_football_id": 91,   "fd_id": "ALG"},
    {"name": "Austria",                "flag": "🇦🇹", "group": "J", "aliases": ["aut"],
     "api_football_id": 775,  "fd_id": "AUT"},
    {"name": "Jordan",                 "flag": "🇯🇴", "group": "J", "aliases": ["jor"],
     "api_football_id": 1499, "fd_id": "JOR"},
    # Group K — Portugal, DR Congo, Uzbekistan, Colombia
    {"name": "Portugal",               "flag": "🇵🇹", "group": "K", "aliases": ["por"],
     "api_football_id": 27,   "fd_id": "POR"},
    {"name": "DR Congo",               "flag": "🇨🇩", "group": "K", "aliases": ["cod", "congo dr", "drc"],
     "api_football_id": 89,   "fd_id": "COD"},
    {"name": "Uzbekistan",             "flag": "🇺🇿", "group": "K", "aliases": ["uzb"],
     "api_football_id": 1493, "fd_id": "UZB"},
    {"name": "Colombia",               "flag": "🇨🇴", "group": "K", "aliases": ["col"],
     "api_football_id": 8,    "fd_id": "COL"},
    # Group L — England, Croatia, Ghana, Panama
    {"name": "England",                "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "group": "L", "aliases": ["eng", "three lions"],
     "api_football_id": 10,   "fd_id": "ENG"},
    {"name": "Croatia",                "flag": "🇭🇷", "group": "L", "aliases": ["cro"],
     "api_football_id": 799,  "fd_id": "CRO"},
    {"name": "Ghana",                  "flag": "🇬🇭", "group": "L", "aliases": ["gha"],
     "api_football_id": 22,   "fd_id": "GHA"},
    {"name": "Panama",                 "flag": "🇵🇦", "group": "L", "aliases": ["pan"],
     "api_football_id": 26,   "fd_id": "PAN"},
]

# Deduplicate by name
_seen_n: set = set()
_deduped_n: list = []
for _t in WC2026_TEAMS:
    if _t["name"] not in _seen_n:
        _seen_n.add(_t["name"])
        _deduped_n.append(_t)
WC2026_TEAMS = _deduped_n

# Display names include the group: flag + name + "(Grp X)"
TEAM_DISPLAY_NAMES = [f"{t['flag']} {t['name']} (Grp {t['group']})" for t in WC2026_TEAMS]
TEAM_BY_DISPLAY    = {f"{t['flag']} {t['name']} (Grp {t['group']})": t for t in WC2026_TEAMS}
TEAM_BY_NAME       = {t["name"]: t for t in WC2026_TEAMS}

# World Cup fixture lookup constants
AF_WC_LEAGUE_ID = 1      # API-Football: FIFA World Cup league ID
AF_WC_SEASON    = 2026
FD_WC_COMP      = "WC"   # football-data.org competition code


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class TeamRef(BaseModel):
    name: str
    flag: str
    api_football_id: int
    fd_id: str

class ResultRow(BaseModel):
    date: str
    competition: str
    opponent: str
    score: str
    outcome: Literal["W", "D", "L"]

class H2HSummary(BaseModel):
    wins_a: int
    draws: int
    wins_b: int
    goals_a: int
    goals_b: int
    matches: list[dict]

class Fixture(BaseModel):
    fixture_id: Optional[int] = None
    kickoff_utc: Optional[str] = None
    kickoff_local: Optional[str] = None
    stadium: Optional[str] = None
    city: Optional[str] = None
    round: Optional[str] = None
    status: Optional[str] = None
    is_knockout: bool = False
    source: str = "unknown"
    fetched_at: str = ""

class CategoryScore(BaseModel):
    team_a: float = Field(ge=0, le=10)
    team_b: float = Field(ge=0, le=10)
    justification: str
    confidence: Literal["high", "medium", "low"]
    sources: list[str] = []

    @field_validator("team_a", "team_b", mode="before")
    @classmethod
    def clamp_score(cls, v):
        try:
            return max(0.0, min(10.0, float(v)))
        except (TypeError, ValueError):
            return 5.0

    @model_validator(mode="after")
    def force_low_confidence_if_no_sources(self):
        if not self.sources:
            self.confidence = "low"
        return self

class TacticalAnalysis(BaseModel):
    team_a_style: str
    team_b_style: str
    clash_summary: str

class LLMAnalysis(BaseModel):
    tactical_analysis: TacticalAnalysis
    categories: dict[str, CategoryScore]
    key_uncertainties: list[str]
    analyst_note: str

    @model_validator(mode="after")
    def validate_categories(self):
        required = {"current_form", "player_performance", "squad_availability",
                    "h2h_record", "contextual_factors"}
        missing = required - set(self.categories.keys())
        if missing:
            raise ValueError(f"Missing required categories: {missing}")
        return self

# ═══════════════════════════════════════════════════════════════════════════════
# 2. DATA CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

class DataClient:
    """Handles all structured football data fetching with fallback chain."""

    AF_BASE = "https://v3.football.api-sports.io"
    FD_BASE = "https://api.football-data.org/v4"
    TIMEOUT = 8

    def __init__(self):
        self.af_key = os.getenv("API_FOOTBALL_KEY", "")
        self.fd_key = os.getenv("FOOTBALL_DATA_KEY", "")
        self._af_ok: Optional[bool] = None
        self._fd_ok: Optional[bool] = None

    # ── Internal HTTP helpers ─────────────────────────────────────────────────

    def _af_get(self, path: str, params: dict = None) -> dict:
        if not self.af_key:
            raise ValueError("API_FOOTBALL_KEY not set")
        r = requests.get(
            f"{self.AF_BASE}{path}",
            headers={"x-rapidapi-key": self.af_key, "x-rapidapi-host": "v3.football.api-sports.io"},
            params=params or {},
            timeout=self.TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def _fd_get(self, path: str, params: dict = None) -> dict:
        if not self.fd_key:
            raise ValueError("FOOTBALL_DATA_KEY not set")
        r = requests.get(
            f"{self.FD_BASE}{path}",
            headers={"X-Auth-Token": self.fd_key},
            params=params or {},
            timeout=self.TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    # ── API status ping ───────────────────────────────────────────────────────

    def ping_af(self) -> bool:
        try:
            data = self._af_get("/status")
            self._af_ok = True
            return True
        except Exception:
            self._af_ok = False
            return False

    def ping_fd(self) -> bool:
        try:
            data = self._fd_get("/competitions/WC")
            self._fd_ok = True
            return True
        except Exception:
            self._fd_ok = False
            return False

    # ── Team resolution ───────────────────────────────────────────────────────

    def resolve_team(self, display_name: str) -> TeamRef:
        """Map display name (flag + name [+ optional group suffix]) to TeamRef."""
        import re as _re
        # Strip '(Grp X)' suffix and extra whitespace
        clean = _re.sub(r'\s*\(Grp [A-L]\)\s*$', '', display_name.strip()).strip()

        # 1. Exact match in TEAM_BY_DISPLAY (includes group suffix)
        team = TEAM_BY_DISPLAY.get(display_name)
        if not team:
            # 2. Partial prefix match (flag + name without suffix)
            for key, t in TEAM_BY_DISPLAY.items():
                if clean in key:
                    team = t
                    break
        if not team:
            # 3. TEAM_BY_NAME: strip flag emojis and look up bare name
            bare = _re.sub(r'^[\U0001F1E0-\U0001F1FF\U0001F3F4\U000E0000-\U000EFFFF\s]+', '', clean).strip()
            team = TEAM_BY_NAME.get(bare)
        if not team:
            # 4. Alias scan
            for t in WC2026_TEAMS:
                candidates = [t["name"].lower()] + [a.lower() for a in t["aliases"]]
                if bare.lower() in candidates:
                    team = t
                    break
        if not team:
            raise ValueError(f"Team '{display_name}' not found in WC 2026 catalogue")
        return TeamRef(
            name=team["name"],
            flag=team["flag"],
            api_football_id=team["api_football_id"],
            fd_id=team["fd_id"],
        )

    # ── Fixture ───────────────────────────────────────────────────────────────

    @st.cache_data(ttl=900, show_spinner=False)
    def get_fixture(_self, team_a_name: str, team_b_name: str) -> tuple[Optional[Fixture], str]:
        """Returns (Fixture|None, warning_message)."""
        team_a = _self.resolve_team(team_a_name)
        team_b = _self.resolve_team(team_b_name)
        warning = ""

        # Try API-Football first
        try:
            data = _self._af_get("/fixtures", params={
                "league": AF_WC_LEAGUE_ID,
                "season": AF_WC_SEASON,
                "team": team_a.api_football_id,
            })
            fixtures = data.get("response", [])
            matched = None
            for fx in fixtures:
                home_id = fx["teams"]["home"]["id"]
                away_id = fx["teams"]["away"]["id"]
                if team_b.api_football_id in (home_id, away_id):
                    matched = fx
                    break

            if matched:
                f = matched["fixture"]
                venue = matched.get("fixture", {}).get("venue", {})
                now = datetime.now(timezone.utc).isoformat()
                round_val = matched.get("league", {}).get("round", "")
                is_ko = any(kw in round_val.lower() for kw in ["round of", "quarter", "semi", "final"])
                return Fixture(
                    fixture_id=f.get("id"),
                    kickoff_utc=f.get("date", ""),
                    stadium=venue.get("name", ""),
                    city=venue.get("city", ""),
                    round=round_val,
                    status=matched["fixture"]["status"]["long"],
                    is_knockout=is_ko,
                    source="api-football",
                    fetched_at=now,
                ), ""
        except Exception as e:
            warning = f"⚠️ API-Football error: {e}. Trying football-data.org…"

        # Fallback: football-data.org
        try:
            data = _self._fd_get(f"/competitions/{FD_WC_COMP}/matches", params={
                "season": AF_WC_SEASON,
                "status": "SCHEDULED,LIVE,IN_PLAY,PAUSED,FINISHED",
            })
            matches = data.get("matches", [])
            now = datetime.now(timezone.utc).isoformat()
            for m in matches:
                home_tla = m["homeTeam"].get("tla", "")
                away_tla = m["awayTeam"].get("tla", "")
                if {home_tla, away_tla} == {team_a.fd_id, team_b.fd_id}:
                    ko = m.get("utcDate", "")
                    stage = m.get("stage", "")
                    is_ko = any(kw in stage.upper() for kw in ["ROUND_OF", "QUARTER", "SEMI", "FINAL"])
                    return Fixture(
                        kickoff_utc=ko,
                        stadium=m.get("venue", ""),
                        city="",
                        round=stage,
                        status=m.get("status", ""),
                        is_knockout=is_ko,
                        source="football-data.org",
                        fetched_at=now,
                    ), warning
        except Exception as e2:
            warning += f"\n⚠️ football-data.org error: {e2}."

        return None, warning

    # ── Last N results ────────────────────────────────────────────────────────

    @st.cache_data(ttl=900, show_spinner=False)
    def get_last_results(_self, team_name: str, n: int = 5) -> tuple[list[ResultRow], str, str, str]:
        """Returns (results, source, fetched_at, warning)."""
        team = _self.resolve_team(team_name)
        warning = ""
        now = datetime.now(timezone.utc).isoformat()

        # API-Football
        try:
            data = _self._af_get("/fixtures", params={
                "team": team.api_football_id,
                "last": n,
                "status": "FT-AET-PEN",  # Full Time, After Extra Time, Penalties
            })
            rows = []
            for fx in data.get("response", [])[:n]:
                league = fx["league"]["name"]
                home = fx["teams"]["home"]
                away = fx["teams"]["away"]
                goals = fx["goals"]
                is_home = home["id"] == team.api_football_id
                opp = away["name"] if is_home else home["name"]
                score_a = goals["home"] if is_home else goals["away"]
                score_b = goals["away"] if is_home else goals["home"]
                if score_a is None or score_b is None:
                    continue
                if score_a > score_b:
                    outcome = "W"
                elif score_a == score_b:
                    outcome = "D"
                else:
                    outcome = "L"
                rows.append(ResultRow(
                    date=fx["fixture"]["date"][:10],
                    competition=league,
                    opponent=opp,
                    score=f"{score_a}–{score_b}",
                    outcome=outcome,
                ))
            if rows:
                return rows, "api-football", now, warning
        except Exception as e:
            warning = f"⚠️ API-Football: {e}. Trying football-data.org…"

        # Fallback: football-data.org
        try:
            data = _self._fd_get(f"/teams/{_self._fd_team_id(team.fd_id)}/matches", params={
                "status": "FINISHED",
                "limit": n,
            })
            rows = []
            for m in data.get("matches", [])[:n]:
                comp = m.get("competition", {}).get("name", "Unknown")
                home_tla = m["homeTeam"].get("tla", "")
                away_tla = m["awayTeam"].get("tla", "")
                is_home = home_tla == team.fd_id
                opp = m["awayTeam"]["name"] if is_home else m["homeTeam"]["name"]
                score = m.get("score", {}).get("fullTime", {})
                sa = score.get("home", 0) if is_home else score.get("away", 0)
                sb = score.get("away", 0) if is_home else score.get("home", 0)
                if sa is None or sb is None:
                    continue
                if sa > sb:
                    oc = "W"
                elif sa == sb:
                    oc = "D"
                else:
                    oc = "L"
                rows.append(ResultRow(
                    date=m.get("utcDate", "")[:10],
                    competition=comp,
                    opponent=opp,
                    score=f"{sa}–{sb}",
                    outcome=oc,
                ))
            if rows:
                return rows, "football-data.org", now, warning
        except Exception as e2:
            warning += f"\n⚠️ football-data.org: {e2}."

        return [], "none", now, warning + "\n⚠️ Structured API unavailable — no recent-result facts are available."

    def _fd_team_id(self, tla: str) -> int:
        """Lookup football-data.org numeric ID by TLA (simplified mapping)."""
        # Football-data.org uses numeric IDs; for WC teams we embed a basic mapping
        fd_ids = {
            "ARG": 762, "BRA": 764, "FRA": 773, "ENG": 770, "GER": 759,
            "ESP": 760, "POR": 765, "NED": 779, "BEL": 763, "ITA": 784,
            "CRO": 799, "DEN": 782, "AUT": 775, "SUI": 788, "SRB": 808,
            "POL": 794, "UKR": 805, "CZE": 798, "ROU": 811, "SCO": 769,
            "SVK": 800, "HUN": 827, "TUR": 803, "GRE": 806,
            "USA": 768, "CAN": 772, "MEX": 758, "PAN": 815, "CRC": 780,
            "HON": 804, "JAM": 7773, "SLV": 1871, "TRI": 1899,
            "ARG": 762, "URU": 788, "COL": 801, "ECU": 1835, "VEN": 868,
            "CHI": 813, "BOL": 828, "PAR": 807, "PER": 810,
            "JPN": 825, "KOR": 766, "IRN": 781, "KSA": 843, "AUS": 817, "QAT": 8601,
            "MAR": 1031, "SEN": 866, "NGA": 815, "EGY": 782, "CMR": 789,
            "GHA": 1047, "CIV": 1046, "COD": 1048, "MLI": 6654, "ALG": 1049,
            "TUN": 1050, "TAN": 6655, "UGA": 6656, "NZL": 1047,
        }
        return fd_ids.get(tla, 999)

    # ── Head to head ─────────────────────────────────────────────────────────

    @st.cache_data(ttl=900, show_spinner=False)
    def get_h2h(_self, team_a_name: str, team_b_name: str, n: int = 10) -> tuple[Optional[H2HSummary], str, str, str]:
        """Returns (H2HSummary|None, source, fetched_at, warning)."""
        team_a = _self.resolve_team(team_a_name)
        team_b = _self.resolve_team(team_b_name)
        warning = ""
        now = datetime.now(timezone.utc).isoformat()

        # API-Football
        try:
            data = _self._af_get("/fixtures/headtohead", params={
                "h2h": f"{team_a.api_football_id}-{team_b.api_football_id}",
                "last": n,
            })
            matches = data.get("response", [])[:n]
            if matches:
                wa = wd = wb = 0
                ga = gb = 0
                rows = []
                for fx in matches:
                    home = fx["teams"]["home"]
                    away = fx["teams"]["away"]
                    goals = fx["goals"]
                    if home["winner"] is True:
                        winner_id = home["id"]
                    elif away["winner"] is True:
                        winner_id = away["id"]
                    else:
                        winner_id = None
                    is_a_home = home["id"] == team_a.api_football_id
                    ga += goals["home"] if is_a_home else goals["away"]
                    gb += goals["away"] if is_a_home else goals["home"]
                    if winner_id == team_a.api_football_id:
                        wa += 1
                    elif winner_id == team_b.api_football_id:
                        wb += 1
                    else:
                        wd += 1
                    rows.append({
                        "date": fx["fixture"]["date"][:10],
                        "home": home["name"],
                        "away": away["name"],
                        "score": f"{goals['home']}–{goals['away']}",
                    })
                return H2HSummary(
                    wins_a=wa, draws=wd, wins_b=wb,
                    goals_a=ga, goals_b=gb, matches=rows
                ), "api-football", now, warning
        except Exception as e:
            warning = f"⚠️ API-Football H2H: {e}."

        # Fallback: football-data.org doesn't have direct H2H; skip and return empty
        return None, "none", now, warning + " H2H data unavailable from APIs."


# Global DataClient instance
@st.cache_resource
def get_data_client() -> DataClient:
    return DataClient()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. LLM ANALYSIS LAYER
# ═══════════════════════════════════════════════════════════════════════════════

JSON_SCHEMA_STR = """
{
  "tactical_analysis": {
    "team_a_style": "str",
    "team_b_style": "str",
    "clash_summary": "str"
  },
  "categories": {
    "current_form":       {"team_a": 0, "team_b": 0, "justification": "str", "confidence": "high|medium|low", "sources": ["url"]},
    "player_performance": {"team_a": 0, "team_b": 0, "justification": "str", "confidence": "high|medium|low", "sources": ["url"]},
    "squad_availability": {"team_a": 0, "team_b": 0, "justification": "str", "confidence": "high|medium|low", "sources": ["url"]},
    "h2h_record":         {"team_a": 0, "team_b": 0, "justification": "str", "confidence": "high|medium|low", "sources": ["url"]},
    "contextual_factors": {"team_a": 0, "team_b": 0, "justification": "str", "confidence": "high|medium|low", "sources": ["url"]}
  },
  "key_uncertainties": ["str"],
  "analyst_note": "str  // 2-3 sentence synthesis, no percentages"
}
"""


def _build_system_prompt(
    team_a: str, team_b: str,
    fixture: Optional[Fixture],
    results_a: list[ResultRow], results_b: list[ResultRow],
    h2h: Optional[H2HSummary],
) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if fixture:
        fx_summary = (
            f"{team_a} vs {team_b} | {fixture.round} | {fixture.stadium}, {fixture.city} | "
            f"Kickoff UTC: {fixture.kickoff_utc} | Status: {fixture.status}"
        )
    else:
        fx_summary = "No official fixture; treat as hypothetical matchup"

    def fmt_results(results: list[ResultRow]) -> str:
        if not results:
            return "No results available"
        return "; ".join(
            f"{r.date} {r.competition} vs {r.opponent} {r.score} ({r.outcome})"
            for r in results
        )

    if h2h:
        h2h_summary = (
            f"{team_a} {h2h.wins_a}W – {h2h.draws}D – {h2h.wins_b}W {team_b}, "
            f"goals: {team_a} {h2h.goals_a} – {h2h.goals_b} {team_b} "
            f"(last {len(h2h.matches)} meetings)"
        )
    else:
        h2h_summary = "H2H data unavailable"

    return f"""You are a football performance analyst producing structured pre-match analysis for
FIFA World Cup 2026. Today's date is {today}. The tournament is in progress.

VERIFIED FACTS (from official data APIs — treat as ground truth, do not contradict):
- Fixture: {fx_summary}
- {team_a} last 5 results: {fmt_results(results_a)}
- {team_b} last 5 results: {fmt_results(results_b)}
- Head-to-head (last 10): {h2h_summary}

You have no web access. Base current claims only on the verified facts above. You may use
general football knowledge for broad tactical context, but do not invent current managers,
injuries, suspensions, player form, xG, or dated reports. When current evidence is absent,
say so explicitly, score conservatively toward 5, set confidence to "low", and use an empty
sources list.

YOUR TASK:
1. Describe current form from the supplied results only
2. Explain broad tactical tendencies and how the styles may interact, clearly marking
   uncertain or potentially outdated details
3. Treat squad availability as unknown unless supplied in VERIFIED FACTS
4. Assess player performance only when supported by the supplied results
5. Contextual factors: venue conditions/altitude/climate, rest days, travel, stakes

SCORING: Rate each category for each team on 0–10. Justify scores with the supplied
facts. If evidence is thin, score conservatively toward 5 and set confidence to "low".
Do not fabricate source URLs; use [] when no URL was provided.

OUTPUT: Respond with ONLY a raw JSON object matching the schema below. No markdown
fences, no preamble, no trailing text. Do NOT output win/draw/loss percentages —
probabilities are computed downstream from your category scores.

{JSON_SCHEMA_STR}"""


def _strip_fences(text: str) -> str:
    """Remove accidental markdown code fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence line
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def _parse_llm_response(raw: str) -> tuple[Optional[LLMAnalysis], Optional[str]]:
    """Returns (analysis, error_message). One of them is always None."""
    cleaned = _strip_fences(raw)
    try:
        data = json.loads(cleaned)
        analysis = LLMAnalysis.model_validate(data)
        return analysis, None
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=1800, show_spinner=False)
def run_llm_analysis(
    team_a_name: str,
    team_b_name: str,
    date_key: str,  # for cache keying
    fixture_json: str,
    results_a_json: str,
    results_b_json: str,
    h2h_json: str,
) -> tuple[Optional[LLMAnalysis], Optional[str], str]:
    """
    Returns (LLMAnalysis|None, raw_text_fallback|None, error_message).
    """
    # Deserialize inputs
    fixture = Fixture.model_validate_json(fixture_json) if fixture_json != "null" else None
    results_a = [ResultRow.model_validate(r) for r in json.loads(results_a_json)]
    results_b = [ResultRow.model_validate(r) for r in json.loads(results_b_json)]
    h2h = H2HSummary.model_validate_json(h2h_json) if h2h_json != "null" else None

    system_prompt = _build_system_prompt(team_a_name, team_b_name, fixture, results_a, results_b, h2h)

    def _call(messages: list) -> str:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": MODEL_ID,
                "stream": False,
                "format": "json",
                "messages": [{"role": "system", "content": system_prompt}, *messages],
                "options": {"temperature": 0.2},
            },
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content")
        if not content:
            raise ValueError("Ollama returned no message content")
        return content

    try:
        raw = _call([{"role": "user", "content": f"Analyze the {team_a_name} vs {team_b_name} matchup."}])
        analysis, err = _parse_llm_response(raw)
        if analysis:
            return analysis, None, ""

        # Repair retry
        repair_messages = [
            {"role": "user", "content": f"Analyze the {team_a_name} vs {team_b_name} matchup."},
            {"role": "assistant", "content": raw},
            {"role": "user", "content": f"Your previous output failed validation: {err}. Return ONLY corrected raw JSON."},
        ]
        raw2 = _call(repair_messages)
        analysis2, err2 = _parse_llm_response(raw2)
        if analysis2:
            return analysis2, None, ""

        # Raw text fallback
        return None, raw2 or raw, f"JSON parse failed after retry: {err2}"

    except requests.Timeout:
        return None, None, "LLM API timeout (90s exceeded)"
    except requests.ConnectionError:
        return None, None, (
            f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            "Start Ollama and pull the configured model."
        )
    except requests.HTTPError as e:
        detail = e.response.text if e.response is not None else str(e)
        return None, None, f"Ollama API error: {detail}"
    except Exception as e:
        return None, None, f"Unexpected error: {traceback.format_exc()}"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. PROBABILITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_WEIGHTS = {
    "current_form": 0.30,
    "player_performance": 0.25,
    "squad_availability": 0.20,
    "h2h_record": 0.10,
    "contextual_factors": 0.15,
}

CATEGORY_LABELS = {
    "current_form": "Current Form",
    "player_performance": "Player Performance",
    "squad_availability": "Squad Availability",
    "h2h_record": "H2H Record",
    "contextual_factors": "Contextual Factors",
}


def compute_probabilities(
    analysis: LLMAnalysis,
    weights: dict[str, float],
    k: float = 0.45,
    D_max: float = 0.30,
    tau: float = 6.0,
) -> dict[str, Any]:
    """Deterministic probability engine from weighted category scores."""
    # Normalize weights to sum to 1
    total_w = sum(weights.values())
    w = {cat: v / total_w for cat, v in weights.items()}

    # Compute weighted scores
    S_a = S_b = 0.0
    score_details = {}
    for cat, cat_data in analysis.categories.items():
        wi = w.get(cat, 0.0)
        S_a += wi * cat_data.team_a
        S_b += wi * cat_data.team_b
        score_details[cat] = {
            "team_a": cat_data.team_a,
            "team_b": cat_data.team_b,
            "weight": wi,
        }

    d = S_a - S_b

    # Logistic + draw model
    p_a_raw = 1.0 / (1.0 + math.exp(-k * d))
    p_draw = D_max * math.exp(-(d ** 2) / tau)
    p_a = p_a_raw * (1.0 - p_draw)
    p_b = (1.0 - p_a_raw) * (1.0 - p_draw)

    # Convert to whole percentages
    pct_a = round(p_a * 100)
    pct_draw = round(p_draw * 100)
    pct_b = round(p_b * 100)

    # Force sum = 100
    total = pct_a + pct_draw + pct_b
    diff = 100 - total
    if diff != 0:
        # Adjust the largest
        largest = max((pct_a, "a"), (pct_draw, "draw"), (pct_b, "b"), key=lambda x: x[0])
        if largest[1] == "a":
            pct_a += diff
        elif largest[1] == "draw":
            pct_draw += diff
        else:
            pct_b += diff

    # Clamp to [0, 100] (shouldn't be needed, but safety)
    pct_a = max(0, min(100, pct_a))
    pct_draw = max(0, min(100, pct_draw))
    pct_b = max(0, min(100, pct_b))

    # Fair decimal odds
    fair_odds_a = round(100 / pct_a, 2) if pct_a > 0 else 999.0
    fair_odds_draw = round(100 / pct_draw, 2) if pct_draw > 0 else 999.0
    fair_odds_b = round(100 / pct_b, 2) if pct_b > 0 else 999.0

    return {
        "S_a": round(S_a, 3),
        "S_b": round(S_b, 3),
        "d": round(d, 3),
        "pct_a": pct_a,
        "pct_draw": pct_draw,
        "pct_b": pct_b,
        "fair_odds_a": fair_odds_a,
        "fair_odds_draw": fair_odds_draw,
        "fair_odds_b": fair_odds_b,
        "score_details": score_details,
    }


def compute_edge(prob_result: dict, bm_a: float, bm_draw: float, bm_b: float) -> dict:
    """Compute edge against bookmaker odds after removing overround."""
    if not (bm_a > 1 and bm_draw > 1 and bm_b > 1):
        return {}
    # Raw implied probabilities
    imp_a_raw = 1 / bm_a
    imp_draw_raw = 1 / bm_draw
    imp_b_raw = 1 / bm_b
    overround = imp_a_raw + imp_draw_raw + imp_b_raw
    # Remove overround proportionally
    imp_a = imp_a_raw / overround
    imp_draw = imp_draw_raw / overround
    imp_b = imp_b_raw / overround
    return {
        "edge_a": round((prob_result["pct_a"] / 100 - imp_a) * 100, 1),
        "edge_draw": round((prob_result["pct_draw"] / 100 - imp_draw) * 100, 1),
        "edge_b": round((prob_result["pct_b"] / 100 - imp_b) * 100, 1),
        "implied_a": round(imp_a * 100, 1),
        "implied_draw": round(imp_draw * 100, 1),
        "implied_b": round(imp_b * 100, 1),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

def log_analysis(data: dict):
    """Append analysis to analysis_log.jsonl."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        st.warning(f"Could not write to analysis_log.jsonl: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# 6. UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def confidence_badge(level: str) -> str:
    return {"high": "🟢 High", "medium": "🟡 Medium", "low": "🔴 Low"}.get(level, "⚪ Unknown")


def outcome_chip(outcome: str) -> str:
    return {"W": "🟩 W", "D": "🟨 D", "L": "🟥 L"}.get(outcome, outcome)


def render_setup_screen(missing_keys: list[str]):
    st.error("### ⚙️ Setup Required — Missing API Keys")
    st.markdown(
        "The following environment variables are not set. "
        "Copy `.env.example` to `.env` and fill in your keys, then restart the app."
    )
    key_info = {
        "API_FOOTBALL_KEY": ("API-Football (primary data)", "https://www.api-football.com/"),
        "FOOTBALL_DATA_KEY": ("football-data.org (fallback data)", "https://www.football-data.org/client/register"),
    }
    for key in missing_keys:
        name, url = key_info.get(key, (key, "#"))
        st.markdown(f"- **`{key}`** — {name} → [Get free key]({url})")
    st.info("Add at least one football data key. Ollama runs locally and does not require an API key.")


def render_result_table(results: list[ResultRow], highlight_recent: int = 2):
    if not results:
        st.caption("No results available.")
        return
    for i, r in enumerate(results):
        chip = outcome_chip(r.outcome)
        highlight = "**" if i < highlight_recent else ""
        st.markdown(
            f"{highlight}{r.date} | {r.competition} | vs {r.opponent} | "
            f"{r.score} | {chip}{highlight}"
        )


def render_probability_donut(team_a: str, team_b: str, prob: dict):
    fig = go.Figure(go.Pie(
        labels=[f"🏆 {team_a} Win", "🤝 Draw", f"🏆 {team_b} Win"],
        values=[prob["pct_a"], prob["pct_draw"], prob["pct_b"]],
        hole=0.55,
        marker=dict(colors=["#00d4aa", "#f0a500", "#e05252"]),
        textinfo="label+percent",
        textfont=dict(size=14),
        hovertemplate="%{label}: %{value}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(t=20, b=20, l=10, r=10),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_score_bar_chart(analysis: LLMAnalysis, team_a: str, team_b: str, weights: dict):
    cats = list(CATEGORY_LABELS.values())
    scores_a = [analysis.categories[k].team_a for k in CATEGORY_LABELS]
    scores_b = [analysis.categories[k].team_b for k in CATEGORY_LABELS]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=team_a, y=cats, x=scores_a,
        orientation="h",
        marker_color="#00d4aa",
        text=[f"{v:.1f}" for v in scores_a],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name=team_b, y=cats, x=scores_b,
        orientation="h",
        marker_color="#e05252",
        text=[f"{v:.1f}" for v in scores_b],
        textposition="outside",
    ))
    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 11], gridcolor="#333"),
        yaxis=dict(gridcolor="#333"),
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=30, b=20, l=10, r=40),
        height=320,
        font=dict(color="#e6edf3"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="WC 2026 Predictive Analytics Engine",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Custom CSS ────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; }
    .badge-tournament { background: #00d4aa22; color: #00d4aa;
        padding: 2px 10px; border-radius: 12px; font-size: 0.8rem;
        border: 1px solid #00d4aa55; }
    .card-box { background: #161b22; border-radius: 12px; padding: 16px 20px;
        margin-bottom: 12px; border: 1px solid #30363d; }
    .source-footer { font-size: 0.72rem; color: #8b949e; margin-top: 8px; }
    .hypothetical-banner { background: #f0a50022; border: 1px solid #f0a500;
        border-radius: 8px; padding: 10px 16px; color: #f0a500; margin: 8px 0; }
    .api-warning { background: #e0525222; border: 1px solid #e05252;
        border-radius: 8px; padding: 8px 14px; color: #e05252; margin: 4px 0; }
    .disclaimer { font-size: 0.78rem; color: #8b949e; font-style: italic; margin-top: 8px; }
    </style>
    """, unsafe_allow_html=True)

    # ── Check env vars ────────────────────────────────────────────────────────
    missing_keys = [k for k in ["API_FOOTBALL_KEY", "FOOTBALL_DATA_KEY"]
                    if not os.getenv(k)]

    # ── Header ────────────────────────────────────────────────────────────────
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f'<div class="main-header">{APP_TITLE}</div>', unsafe_allow_html=True)
        today_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
        st.markdown(
            f'📅 {today_str} &nbsp;&nbsp; <span class="badge-tournament">🟢 Tournament in progress</span>',
            unsafe_allow_html=True,
        )

    if missing_keys:
        with st.expander("⚙️ Setup: Missing API keys detected", expanded=True):
            render_setup_screen(missing_keys)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Model Configuration")

        st.subheader("Category Weights")
        raw_weights = {}
        for cat, label in CATEGORY_LABELS.items():
            raw_weights[cat] = st.slider(
                label, min_value=0.0, max_value=1.0,
                value=DEFAULT_WEIGHTS[cat], step=0.05,
                key=f"weight_{cat}",
            )
        # Live-renormalized display
        total_w = sum(raw_weights.values()) or 1e-9
        norm_w = {k: round(v / total_w, 4) for k, v in raw_weights.items()}
        st.caption(f"Normalized: {', '.join(f'{CATEGORY_LABELS[k]}: {v:.0%}' for k, v in norm_w.items())}")

        st.divider()
        k_sharp = st.slider("Sharpness (k)", 0.1, 1.0, 0.45, 0.05,
                             help="Controls how strongly score gap translates to probability gap")

        st.divider()
        st.subheader("📊 Bookmaker Odds (optional)")
        st.caption("Enter decimal odds to see edge table (leave at 0 to skip)")
        bm_a = st.number_input("Odds: Team A Win", min_value=0.0, max_value=100.0,
                                value=0.0, step=0.01, key="bm_a",
                                help="e.g. 2.50 — enter 0 to skip")
        bm_draw = st.number_input("Odds: Draw", min_value=0.0, max_value=100.0,
                                   value=0.0, step=0.01, key="bm_draw",
                                   help="e.g. 3.20 — enter 0 to skip")
        bm_b = st.number_input("Odds: Team B Win", min_value=0.0, max_value=100.0,
                                value=0.0, step=0.01, key="bm_b",
                                help="e.g. 4.50 — enter 0 to skip")

        st.divider()
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")

        st.divider()
        st.subheader("🌐 API Status")
        client = get_data_client()
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Ping APIs", key="ping_btn", use_container_width=True):
                af_ok = client.ping_af()
                fd_ok = client.ping_fd()
                st.session_state["af_ok"] = af_ok
                st.session_state["fd_ok"] = fd_ok
        af_ok = st.session_state.get("af_ok", None)
        fd_ok = st.session_state.get("fd_ok", None)
        dot = lambda ok: "🟢" if ok is True else ("🔴" if ok is False else "⚪")
        st.markdown(
            f"{dot(af_ok)} API-Football  \n"
            f"{dot(fd_ok)} football-data.org  \n"
            f"⚪ Ollama `{MODEL_ID}`"
        )

    # ── Main Controls ─────────────────────────────────────────────────────────
    st.divider()
    col1, col_swap, col2 = st.columns([5, 1, 5])
    with col1:
        team_a_display = st.selectbox(
            "🏠 Team A", TEAM_DISPLAY_NAMES,
            index=next((i for i, n in enumerate(TEAM_DISPLAY_NAMES) if "United States" in n), 0),
            key="team_a",
        )
    with col_swap:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⇄", key="swap_btn", use_container_width=True, help="Swap teams"):
            a_val = st.session_state["team_a"]
            b_val = st.session_state["team_b"]
            st.session_state["team_a"] = b_val
            st.session_state["team_b"] = a_val
            st.rerun()
    with col2:
        team_b_display = st.selectbox(
            "✈️ Team B", TEAM_DISPLAY_NAMES,
            index=next((i for i, n in enumerate(TEAM_DISPLAY_NAMES) if "Mexico" in n), 1),
            key="team_b",
        )

    same_team = team_a_display == team_b_display
    if same_team:
        st.warning("⚠️ Please select two different teams.")

    analyze_disabled = same_team
    analyze_clicked = st.button(
        "🔍 Analyze Matchup",
        type="primary",
        use_container_width=True,
        disabled=analyze_disabled,
        key="analyze_btn",
    )

    # ── Analysis Flow ─────────────────────────────────────────────────────────
    if analyze_clicked and not same_team:
        t_start = time.time()
        client = get_data_client()

        fixture_obj: Optional[Fixture] = None
        fixture_warning = ""
        results_a: list[ResultRow] = []
        results_b: list[ResultRow] = []
        results_a_source = results_b_source = "unknown"
        results_a_fetched = results_b_fetched = ""
        results_a_warn = results_b_warn = ""
        h2h_obj: Optional[H2HSummary] = None
        h2h_source = ""
        h2h_fetched = ""
        h2h_warn = ""

        analysis: Optional[LLMAnalysis] = None
        raw_text_fallback: Optional[str] = None
        llm_error = ""

        with st.status("🔄 Running analysis…", expanded=True) as status:

            # Step 1: Resolve teams
            status.update(label="Resolving teams…")
            try:
                team_a_ref = client.resolve_team(team_a_display)
                team_b_ref = client.resolve_team(team_b_display)
                st.write(f"✅ Teams resolved: {team_a_ref.name} vs {team_b_ref.name}")
            except Exception as e:
                st.error(f"Team resolution failed: {e}")
                st.stop()

            # Step 2: Fetch data
            status.update(label="Fetching fixture & results from data API…")

            try:
                fixture_obj, fixture_warning = client.get_fixture(team_a_display, team_b_display)
                if fixture_obj:
                    st.write(f"✅ Fixture found: {fixture_obj.round} | {fixture_obj.stadium}")
                else:
                    st.write("ℹ️ No scheduled fixture found — hypothetical matchup")
            except Exception as e:
                fixture_warning = f"⚠️ Fixture fetch error: {e}"
                st.write(f"⚠️ {e}")

            try:
                results_a, results_a_source, results_a_fetched, results_a_warn = \
                    client.get_last_results(team_a_display)
                st.write(f"✅ {team_a_ref.name} results: {len(results_a)} matches (source: {results_a_source})")
            except Exception as e:
                results_a_warn = str(e)
                st.write(f"⚠️ {team_a_ref.name} results error: {e}")

            try:
                results_b, results_b_source, results_b_fetched, results_b_warn = \
                    client.get_last_results(team_b_display)
                st.write(f"✅ {team_b_ref.name} results: {len(results_b)} matches (source: {results_b_source})")
            except Exception as e:
                results_b_warn = str(e)
                st.write(f"⚠️ {team_b_ref.name} results error: {e}")

            try:
                h2h_obj, h2h_source, h2h_fetched, h2h_warn = \
                    client.get_h2h(team_a_display, team_b_display)
                if h2h_obj:
                    st.write(f"✅ H2H: {h2h_obj.wins_a}W {h2h_obj.draws}D {h2h_obj.wins_b}L")
                else:
                    st.write("ℹ️ H2H data not available")
            except Exception as e:
                h2h_warn = str(e)
                st.write(f"⚠️ H2H error: {e}")

            # Step 3: LLM analysis
            status.update(label=f"Running local analysis with Ollama ({MODEL_ID})…")
            try:
                date_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                fixture_json = fixture_obj.model_dump_json() if fixture_obj else "null"
                results_a_json = json.dumps([r.model_dump() for r in results_a])
                results_b_json = json.dumps([r.model_dump() for r in results_b])
                h2h_json = h2h_obj.model_dump_json() if h2h_obj else "null"

                analysis, raw_text_fallback, llm_error = run_llm_analysis(
                    team_a_ref.name, team_b_ref.name,
                    date_key, fixture_json, results_a_json, results_b_json, h2h_json,
                )
                if analysis:
                    st.write("✅ LLM analysis complete")
                elif raw_text_fallback:
                    st.write("⚠️ LLM returned unstructured text (JSON parse failed)")
                else:
                    st.write(f"❌ LLM failed: {llm_error}")
            except Exception as e:
                llm_error = str(e)
                st.write(f"❌ LLM error: {e}")

            # Step 4: Probabilities
            status.update(label="Computing probability matrix…")
            elapsed = round(time.time() - t_start, 1)
            status.update(label=f"✅ Analysis complete in {elapsed}s", state="complete")

        # ── Results ──────────────────────────────────────────────────────────

        # ── CARD 1: Match Info & Verification ───────────────────────────────
        st.markdown("---")
        st.subheader("📋 Match Info & Verification")

        # Determine same group or cross-group
        try:
            grp_a = TEAM_BY_NAME.get(team_a_ref.name, {}).get("group", "?")
            grp_b = TEAM_BY_NAME.get(team_b_ref.name, {}).get("group", "?")
            same_group = (grp_a == grp_b)
        except Exception:
            grp_a = grp_b = "?"; same_group = False

        if not fixture_obj:
            if same_group:
                st.markdown(
                    f'<div style="background:#1a0a0a;border:2px solid #ff4444;border-radius:8px;padding:14px 18px;margin-bottom:10px">'
                    f'<span style="font-size:1.3em">❌</span> '
                    f'<b style="color:#ff6666">Not yet scheduled in WC 2026</b> '
                    f'<span style="color:#aaa">&mdash; {team_a_ref.name} and {team_b_ref.name} are both in '
                    f'<b>Group {grp_a}</b>. Their match exists but kickoff details are <b>TBD</b> '
                    f'in the live feed. Analysis below uses historical data.</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="background:#1a0a0a;border:2px solid #ff4444;border-radius:8px;padding:14px 18px;margin-bottom:10px">'
                    f'<span style="font-size:1.3em">❌</span> '
                    f'<b style="color:#ff6666">Not scheduled in this WC</b> '
                    f'<span style="color:#aaa">&mdash; {team_a_ref.name} (Group {grp_a}) and '
                    f'{team_b_ref.name} (Group {grp_b}) are in different groups and cannot meet '
                    f'until the knockout stage. This is a <b>hypothetical matchup</b> analysis.</span></div>',
                    unsafe_allow_html=True,
                )
        if fixture_warning:
            for line in fixture_warning.strip().split("\n"):
                if line.strip():
                    st.markdown(f'<div class="api-warning">{line}</div>', unsafe_allow_html=True)

        if fixture_obj:
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.metric("Stadium", fixture_obj.stadium or "—")
                st.metric("City", fixture_obj.city or "—")
            with fc2:
                st.metric("Round / Group", fixture_obj.round or "—")
                st.metric("Status", fixture_obj.status or "—")
            with fc3:
                st.metric("Kickoff (UTC)", fixture_obj.kickoff_utc or "—")
                if fixture_obj.is_knockout:
                    st.info("🏆 Knockout stage — *draw = level at 90 min (ET/pens follow)*")
            st.markdown(
                f'<div class="source-footer">Source: {fixture_obj.source} | Fetched: {fixture_obj.fetched_at}</div>',
                unsafe_allow_html=True,
            )

        # Last 5 results side by side
        res_col_a, res_col_b = st.columns(2)
        with res_col_a:
            st.markdown(f"**{team_a_ref.flag} {team_a_ref.name} — Last {len(results_a)} Results**")
            render_result_table(results_a)
            if results_a_warn:
                st.caption(f"⚠️ {results_a_warn}")
            st.markdown(
                f'<div class="source-footer">Source: {results_a_source} | Fetched: {results_a_fetched}</div>',
                unsafe_allow_html=True,
            )
        with res_col_b:
            st.markdown(f"**{team_b_ref.flag} {team_b_ref.name} — Last {len(results_b)} Results**")
            render_result_table(results_b)
            if results_b_warn:
                st.caption(f"⚠️ {results_b_warn}")
            st.markdown(
                f'<div class="source-footer">Source: {results_b_source} | Fetched: {results_b_fetched}</div>',
                unsafe_allow_html=True,
            )

        # H2H strip
        if h2h_obj:
            st.markdown(
                f"**H2H Strip (last {len(h2h_obj.matches)}):** "
                f"{team_a_ref.name} **{h2h_obj.wins_a}W** – **{h2h_obj.draws}D** – **{h2h_obj.wins_b}W** {team_b_ref.name} | "
                f"Goals: {h2h_obj.goals_a} – {h2h_obj.goals_b}"
            )
            with st.expander("View H2H match list"):
                for m in h2h_obj.matches:
                    st.markdown(f"- {m['date']} | {m['home']} vs {m['away']} | {m['score']}")
            st.markdown(
                f'<div class="source-footer">Source: {h2h_source} | Fetched: {h2h_fetched}</div>',
                unsafe_allow_html=True,
            )
        if h2h_warn:
            st.caption(f"⚠️ {h2h_warn}")

        # ── CARD 2: Tactical Styles ──────────────────────────────────────────
        st.markdown("---")
        st.subheader("⚽ Tactical Styles")

        if analysis:
            tac_a, tac_b = st.columns(2)
            with tac_a:
                st.markdown(f"**{team_a_ref.flag} {team_a_ref.name}**")
                st.write(analysis.tactical_analysis.team_a_style)
            with tac_b:
                st.markdown(f"**{team_b_ref.flag} {team_b_ref.name}**")
                st.write(analysis.tactical_analysis.team_b_style)
            st.markdown("**Clash Summary**")
            st.write(analysis.tactical_analysis.clash_summary)
        elif raw_text_fallback:
            with st.expander("Unstructured analysis (JSON parse failed)"):
                st.text(raw_text_fallback)
        elif llm_error:
            st.error(f"LLM error: {llm_error}")
        else:
            st.info("No LLM analysis available.")

        # ── CARD 3: Probability Matrix ────────────────────────────────────────
        st.markdown("---")
        st.subheader("🎯 Probability Matrix")

        if analysis:
            prob = compute_probabilities(analysis, norm_w, k=k_sharp)

            render_probability_donut(team_a_ref.name, team_b_ref.name, prob)

            p1, p2, p3 = st.columns(3)
            p1.metric(f"🏆 {team_a_ref.name} Win", f"{prob['pct_a']}%",
                      delta=f"Fair odds: {prob['fair_odds_a']}")
            p2.metric("🤝 Draw", f"{prob['pct_draw']}%",
                      delta=f"Fair odds: {prob['fair_odds_draw']}")
            p3.metric(f"🏆 {team_b_ref.name} Win", f"{prob['pct_b']}%",
                      delta=f"Fair odds: {prob['fair_odds_b']}")

            assert prob["pct_a"] + prob["pct_draw"] + prob["pct_b"] == 100, "Prob sum bug!"

            # Bookmaker edge table
            edge = compute_edge(prob, bm_a, bm_draw, bm_b)
            if edge:
                st.markdown("**Edge vs Bookmaker**")
                import pandas as pd
                edge_df = pd.DataFrame({
                    "Outcome": [f"{team_a_ref.name} Win", "Draw", f"{team_b_ref.name} Win"],
                    "Model %": [prob["pct_a"], prob["pct_draw"], prob["pct_b"]],
                    "Implied %": [edge["implied_a"], edge["implied_draw"], edge["implied_b"]],
                    "Edge (pp)": [edge["edge_a"], edge["edge_draw"], edge["edge_b"]],
                })
                st.dataframe(
                    edge_df.style.map(
                        lambda v: "color: #00d4aa" if isinstance(v, float) and v > 0
                        else ("color: #e05252" if isinstance(v, float) and v < 0 else ""),
                        subset=["Edge (pp)"],
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            st.markdown(
                '<div class="disclaimer">⚠️ Model output for research — not betting advice. '
                "Past results don't predict outcomes; bet responsibly.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("Probability matrix requires successful LLM analysis.")

        # ── CARD 4: Weighted Scores ───────────────────────────────────────────
        st.markdown("---")
        st.subheader("📊 Weighted Category Scores")

        if analysis:
            render_score_bar_chart(analysis, team_a_ref.name, team_b_ref.name, norm_w)

            import pandas as pd
            rows = []
            for cat_key, label in CATEGORY_LABELS.items():
                cat = analysis.categories[cat_key]
                srcs = " ".join(f"[{i+1}]({s})" for i, s in enumerate(cat.sources)) if cat.sources else "—"
                rows.append({
                    "Category": label,
                    f"{team_a_ref.name}": cat.team_a,
                    f"{team_b_ref.name}": cat.team_b,
                    "Confidence": confidence_badge(cat.confidence),
                    "Justification": cat.justification[:120] + ("…" if len(cat.justification) > 120 else ""),
                    "Sources": srcs,
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption("Justification truncated — see full detail in Row expander or raw JSON audit below.")
        else:
            st.info("Score breakdown requires successful LLM analysis.")

        # ── CARD 5: Uncertainties & Notes ─────────────────────────────────────
        st.markdown("---")
        st.subheader("🔎 Uncertainties & Analyst Notes")

        if analysis:
            st.markdown("**Key Uncertainties**")
            for u in analysis.key_uncertainties:
                st.markdown(f"- {u}")
            st.markdown("**Analyst Note**")
            st.info(analysis.analyst_note)

            with st.expander("🔬 Show raw model output (audit)"):
                st.json(analysis.model_dump())

            # Log analysis
            log_analysis({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "team_a": team_a_ref.name,
                "team_b": team_b_ref.name,
                "fixture": fixture_obj.model_dump() if fixture_obj else None,
                "scores": {
                    cat: {"team_a": v.team_a, "team_b": v.team_b}
                    for cat, v in analysis.categories.items()
                },
                "probabilities": {
                    "pct_a": prob["pct_a"],
                    "pct_draw": prob["pct_draw"],
                    "pct_b": prob["pct_b"],
                },
                "weights": norm_w,
                "k": k_sharp,
                "sources": {
                    cat: v.sources for cat, v in analysis.categories.items()
                },
            })
        elif raw_text_fallback:
            with st.expander("Unstructured analysis (JSON parse failed)", expanded=True):
                st.text(raw_text_fallback)
        elif llm_error:
            st.error(f"LLM error: {llm_error}")

        st.markdown("---")
        st.caption(
            f"Analysis generated at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC | "
            f"Model: {MODEL_ID} | Elapsed: {elapsed}s | "
            "This dashboard is for research purposes only."
        )


# Streamlit runs the whole module as a script — call main() at top level.
# The guard lets unit tests import without triggering the UI.
if __name__ == "__main__" or _running_in_streamlit():
    main()

