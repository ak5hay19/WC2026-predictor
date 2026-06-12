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
