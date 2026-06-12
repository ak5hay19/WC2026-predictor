"""patch_teams.py — surgically replaces the team catalogue in app.py"""
import sys

NEW_TEAM_BLOCK = '''# ── Verified 48-team WC 2026 roster (Groups A-L, confirmed from official draw) ──
WC2026_TEAMS: list[dict] = [
    # Group A
    {"name": "Mexico",                 "flag": "\\U0001f1f2\\U0001f1fd", "group": "A", "aliases": ["mex", "el tri"],
     "api_football_id": 16,   "fd_id": "MEX"},
    {"name": "South Africa",           "flag": "\\U0001f1ff\\U0001f1e6", "group": "A", "aliases": ["rsa", "bafana bafana"],
     "api_football_id": 66,   "fd_id": "RSA"},
    {"name": "South Korea",            "flag": "\\U0001f1f0\\U0001f1f7", "group": "A", "aliases": ["kor", "korea republic", "korea"],
     "api_football_id": 23,   "fd_id": "KOR"},
    {"name": "Czech Republic",         "flag": "\\U0001f1e8\\U0001f1ff", "group": "A", "aliases": ["cze", "czechia"],
     "api_football_id": 798,  "fd_id": "CZE"},
    # Group B
    {"name": "Canada",                 "flag": "\\U0001f1e8\\U0001f1e6", "group": "B", "aliases": ["can"],
     "api_football_id": 3,    "fd_id": "CAN"},
    {"name": "Bosnia and Herzegovina", "flag": "\\U0001f1e7\\U0001f1e6", "group": "B",
     "aliases": ["bih", "bosnia", "bos", "bosnia & herzegovina", "bosnia herzegovina"],
     "api_football_id": 7947, "fd_id": "BIH"},
    {"name": "Qatar",                  "flag": "\\U0001f1f6\\U0001f1e6", "group": "B", "aliases": ["qat"],
     "api_football_id": 33,   "fd_id": "QAT"},
    {"name": "Switzerland",            "flag": "\\U0001f1e8\\U0001f1ed", "group": "B", "aliases": ["sui", "swi"],
     "api_football_id": 777,  "fd_id": "SUI"},
    # Group C
    {"name": "Brazil",                 "flag": "\\U0001f1e7\\U0001f1f7", "group": "C", "aliases": ["bra", "brasil"],
     "api_football_id": 9,    "fd_id": "BRA"},
    {"name": "Morocco",                "flag": "\\U0001f1f2\\U0001f1e6", "group": "C", "aliases": ["mar"],
     "api_football_id": 32,   "fd_id": "MAR"},
    {"name": "Haiti",                  "flag": "\\U0001f1ed\\U0001f1f9", "group": "C", "aliases": ["hai", "hti"],
     "api_football_id": 468,  "fd_id": "HAI"},
    {"name": "Scotland",               "flag": "\\U0001f3f4\\U000e0067\\U000e0062\\U000e0073\\U000e0063\\U000e0074\\U000e007f", "group": "C", "aliases": ["sco"],
     "api_football_id": 1108, "fd_id": "SCO"},
    # Group D
    {"name": "United States",          "flag": "\\U0001f1fa\\U0001f1f8", "group": "D",
     "aliases": ["usa", "usmnt", "us", "united states of america"],
     "api_football_id": 2,    "fd_id": "USA"},
    {"name": "Paraguay",               "flag": "\\U0001f1f5\\U0001f1fe", "group": "D", "aliases": ["par"],
     "api_football_id": 37,   "fd_id": "PAR"},
    {"name": "Australia",              "flag": "\\U0001f1e6\\U0001f1fa", "group": "D", "aliases": ["aus", "socceroos"],
     "api_football_id": 24,   "fd_id": "AUS"},
    {"name": "Turkey",                 "flag": "\\U0001f1f9\\U0001f1f7", "group": "D", "aliases": ["tur", "turkiye"],
     "api_football_id": 778,  "fd_id": "TUR"},
    # Group E
    {"name": "Germany",                "flag": "\\U0001f1e9\\U0001f1ea", "group": "E", "aliases": ["ger", "die mannschaft"],
     "api_football_id": 25,   "fd_id": "GER"},
    {"name": "Curacao",                "flag": "\\U0001f1e8\\U0001f1fc", "group": "E", "aliases": ["cur", "cuw", "curacao"],
     "api_football_id": 1569, "fd_id": "CUW"},
    {"name": "Cote d\'Ivoire",          "flag": "\\U0001f1e8\\U0001f1ee", "group": "E",
     "aliases": ["civ", "ivory coast", "cote d ivoire", "ivory"],
     "api_football_id": 88,   "fd_id": "CIV"},
    {"name": "Ecuador",                "flag": "\\U0001f1ea\\U0001f1e8", "group": "E", "aliases": ["ecu"],
     "api_football_id": 131,  "fd_id": "ECU"},
    # Group F
    {"name": "Netherlands",            "flag": "\\U0001f1f3\\U0001f1f1", "group": "F", "aliases": ["ned", "holland", "dutch"],
     "api_football_id": 1118, "fd_id": "NED"},
    {"name": "Japan",                  "flag": "\\U0001f1ef\\U0001f1f5", "group": "F", "aliases": ["jpn"],
     "api_football_id": 29,   "fd_id": "JPN"},
    {"name": "Sweden",                 "flag": "\\U0001f1f8\\U0001f1ea", "group": "F", "aliases": ["swe"],
     "api_football_id": 768,  "fd_id": "SWE"},
    {"name": "Tunisia",                "flag": "\\U0001f1f9\\U0001f1f3", "group": "F", "aliases": ["tun"],
     "api_football_id": 1359, "fd_id": "TUN"},
    # Group G
    {"name": "Belgium",                "flag": "\\U0001f1e7\\U0001f1ea", "group": "G", "aliases": ["bel", "red devils"],
     "api_football_id": 1326, "fd_id": "BEL"},
    {"name": "Egypt",                  "flag": "\\U0001f1ea\\U0001f1ec", "group": "G", "aliases": ["egy"],
     "api_football_id": 21,   "fd_id": "EGY"},
    {"name": "Iran",                   "flag": "\\U0001f1ee\\U0001f1f7", "group": "G", "aliases": ["irn", "iir"],
     "api_football_id": 20,   "fd_id": "IRN"},
    {"name": "New Zealand",            "flag": "\\U0001f1f3\\U0001f1ff", "group": "G", "aliases": ["nzl", "all whites"],
     "api_football_id": 95,   "fd_id": "NZL"},
    # Group H
    {"name": "Spain",                  "flag": "\\U0001f1ea\\U0001f1f8", "group": "H", "aliases": ["esp", "la roja"],
     "api_football_id": 9,    "fd_id": "ESP"},
    {"name": "Cape Verde",             "flag": "\\U0001f1e8\\U0001f1fb", "group": "H", "aliases": ["cpv", "cabo verde"],
     "api_football_id": 1591, "fd_id": "CPV"},
    {"name": "Saudi Arabia",           "flag": "\\U0001f1f8\\U0001f1e6", "group": "H", "aliases": ["ksa"],
     "api_football_id": 28,   "fd_id": "KSA"},
    {"name": "Uruguay",                "flag": "\\U0001f1fa\\U0001f1fe", "group": "H", "aliases": ["uru"],
     "api_football_id": 7,    "fd_id": "URU"},
    # Group I
    {"name": "France",                 "flag": "\\U0001f1eb\\U0001f1f7", "group": "I", "aliases": ["fra", "les bleus"],
     "api_football_id": 2,    "fd_id": "FRA"},
    {"name": "Senegal",                "flag": "\\U0001f1f8\\U0001f1f3", "group": "I", "aliases": ["sen"],
     "api_football_id": 34,   "fd_id": "SEN"},
    {"name": "Iraq",                   "flag": "\\U0001f1ee\\U0001f1f6", "group": "I", "aliases": ["irq"],
     "api_football_id": 1504, "fd_id": "IRQ"},
    {"name": "Norway",                 "flag": "\\U0001f1f3\\U0001f1f4", "group": "I", "aliases": ["nor"],
     "api_football_id": 1529, "fd_id": "NOR"},
    # Group J
    {"name": "Argentina",              "flag": "\\U0001f1e6\\U0001f1f7", "group": "J", "aliases": ["arg", "albiceleste"],
     "api_football_id": 6,    "fd_id": "ARG"},
    {"name": "Algeria",                "flag": "\\U0001f1e9\\U0001f1ff", "group": "J", "aliases": ["alg", "dza"],
     "api_football_id": 91,   "fd_id": "ALG"},
    {"name": "Austria",                "flag": "\\U0001f1e6\\U0001f1f9", "group": "J", "aliases": ["aut"],
     "api_football_id": 775,  "fd_id": "AUT"},
    {"name": "Jordan",                 "flag": "\\U0001f1ef\\U0001f1f4", "group": "J", "aliases": ["jor"],
     "api_football_id": 1499, "fd_id": "JOR"},
    # Group K
    {"name": "Portugal",               "flag": "\\U0001f1f5\\U0001f1f9", "group": "K", "aliases": ["por"],
     "api_football_id": 27,   "fd_id": "POR"},
    {"name": "DR Congo",               "flag": "\\U0001f1e8\\U0001f1e9", "group": "K", "aliases": ["cod", "congo dr", "drc"],
     "api_football_id": 89,   "fd_id": "COD"},
    {"name": "Uzbekistan",             "flag": "\\U0001f1fa\\U0001f1ff", "group": "K", "aliases": ["uzb"],
     "api_football_id": 1493, "fd_id": "UZB"},
    {"name": "Colombia",               "flag": "\\U0001f1e8\\U0001f1f4", "group": "K", "aliases": ["col"],
     "api_football_id": 8,    "fd_id": "COL"},
    # Group L
    {"name": "England",                "flag": "\\U0001f3f4\\U000e0067\\U000e0062\\U000e0065\\U000e006e\\U000e0067\\U000e007f", "group": "L", "aliases": ["eng", "three lions"],
     "api_football_id": 10,   "fd_id": "ENG"},
    {"name": "Croatia",                "flag": "\\U0001f1ed\\U0001f1f7", "group": "L", "aliases": ["cro"],
     "api_football_id": 799,  "fd_id": "CRO"},
    {"name": "Ghana",                  "flag": "\\U0001f1ec\\U0001f1ed", "group": "L", "aliases": ["gha"],
     "api_football_id": 22,   "fd_id": "GHA"},
    {"name": "Panama",                 "flag": "\\U0001f1f5\\U0001f1e6", "group": "L", "aliases": ["pan"],
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

# Display names include the group: "\\U0001f1e7\\U0001f1e6 Bosnia and Herzegovina (Grp B)"
TEAM_DISPLAY_NAMES = [f"{t[\'flag\']} {t[\'name\']} (Grp {t[\'group\']})" for t in WC2026_TEAMS]
TEAM_BY_DISPLAY    = {f"{t[\'flag\']} {t[\'name\']} (Grp {t[\'group\']})": t for t in WC2026_TEAMS}
TEAM_BY_NAME       = {t["name"]: t for t in WC2026_TEAMS}

# World Cup fixture lookup constants
AF_WC_LEAGUE_ID = 1      # API-Football: FIFA World Cup league ID
AF_WC_SEASON    = 2026
FD_WC_COMP      = "WC"   # football-data.org competition code
'''

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start marker
START_MARKER = '# All 48 FIFA World Cup 2026 qualified teams with flag emoji'
END_MARKER = 'FD_WC_COMP = "WC"  # football-data.org competition code'

start_idx = content.find(START_MARKER)
if start_idx == -1:
    print("ERROR: Could not find start marker")
    sys.exit(1)

end_idx = content.find(END_MARKER)
if end_idx == -1:
    print("ERROR: Could not find end marker")
    sys.exit(1)

# Include everything after END_MARKER on the same line
end_idx = content.find('\n', end_idx) + 1

new_content = content[:start_idx] + NEW_TEAM_BLOCK + content[end_idx:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Done! Replaced team section. File is now {len(new_content)} bytes.")

# Verify
import ast
try:
    ast.parse(new_content)
    print("Syntax OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
