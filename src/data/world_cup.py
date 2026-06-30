"""世界杯国家队名称映射（football-data.org ↔ The Odds API）。"""

TEAM_ALIASES: dict[str, list[str]] = {
    "Argentina": ["argentina"],
    "Brazil": ["brazil"],
    "France": ["france"],
    "Germany": ["germany"],
    "Spain": ["spain"],
    "England": ["england"],
    "Portugal": ["portugal"],
    "Netherlands": ["netherlands", "holland"],
    "Belgium": ["belgium"],
    "Croatia": ["croatia"],
    "Morocco": ["morocco"],
    "Japan": ["japan"],
    "Korea Republic": ["korea republic", "south korea", "korea"],
    "USA": ["usa", "united states", "us"],
    "Mexico": ["mexico"],
    "Canada": ["canada"],
    "Uruguay": ["uruguay"],
    "Colombia": ["colombia"],
    "Ecuador": ["ecuador"],
    "Senegal": ["senegal"],
    "Ghana": ["ghana"],
    "Cameroon": ["cameroon"],
    "Tunisia": ["tunisia"],
    "Australia": ["australia"],
    "Saudi Arabia": ["saudi arabia"],
    "Iran": ["iran"],
    "Qatar": ["qatar"],
    "Poland": ["poland"],
    "Serbia": ["serbia"],
    "Switzerland": ["switzerland"],
    "Denmark": ["denmark"],
    "Wales": ["wales"],
    "Costa Rica": ["costa rica"],
    "Peru": ["peru"],
    "Chile": ["chile"],
    "Paraguay": ["paraguay"],
    "Venezuela": ["venezuela"],
    "Bolivia": ["bolivia"],
    "Italy": ["italy"],
    "Ukraine": ["ukraine"],
    "Turkey": ["turkey", "türkiye"],
    "Scotland": ["scotland"],
    "Austria": ["austria"],
    "Sweden": ["sweden"],
    "Norway": ["norway"],
    "Egypt": ["egypt"],
    "Nigeria": ["nigeria"],
    "Algeria": ["algeria"],
    "RD Congo": ["rd congo", "dr congo", "congo dr"],
    "Czech Republic": ["czech republic", "czechia"],
    "Bosnia and Herzegovina": ["bosnia and herzegovina", "bosnia & herzegovina", "bosnia"],
    "Ivory Coast": ["ivory coast", "cote d'ivoire", "côte d'ivoire"],
    "Curacao": ["curacao", "curaçao"],
    "Cape Verde": ["cape verde"],
    "Panama": ["panama"],
    "Honduras": ["honduras"],
    "Jamaica": ["jamaica"],
    "New Zealand": ["new zealand"],
    "China PR": ["china", "china pr"],
}


def _normalize_token(name: str) -> str:
    """统一队名格式便于匹配（& → and、去多余空格）。"""
    n = name.lower().strip()
    n = n.replace("&", " and ")
    return " ".join(n.split())


def normalize_for_match(name: str) -> set[str]:
    """返回用于模糊匹配的名称集合。"""
    lower = _normalize_token(name)
    tokens = {lower, lower.replace(" fc", "")}
    for canonical, aliases in TEAM_ALIASES.items():
        canon_norm = _normalize_token(canonical)
        alias_norms = {_normalize_token(a) for a in aliases}
        if lower == canon_norm or lower in alias_norms:
            tokens.add(canon_norm)
            tokens.update(alias_norms)
    return tokens


def teams_match(name_a: str, name_b: str) -> bool:
    a = normalize_for_match(name_a)
    b = normalize_for_match(name_b)
    if a & b:
        return True
    na, nb = _normalize_token(name_a), _normalize_token(name_b)
    return na in nb or nb in na


# 2026 世界杯常见参赛国（含扩军后示例名单，同步 API 后会覆盖）
DEFAULT_WC_TEAMS = [
    {"id": 0, "name": "Argentina", "short_name": "ARG"},
    {"id": 0, "name": "Brazil", "short_name": "BRA"},
    {"id": 0, "name": "France", "short_name": "FRA"},
    {"id": 0, "name": "Germany", "short_name": "GER"},
    {"id": 0, "name": "Spain", "short_name": "ESP"},
    {"id": 0, "name": "England", "short_name": "ENG"},
    {"id": 0, "name": "Portugal", "short_name": "POR"},
    {"id": 0, "name": "Netherlands", "short_name": "NED"},
    {"id": 0, "name": "Belgium", "short_name": "BEL"},
    {"id": 0, "name": "Croatia", "short_name": "CRO"},
    {"id": 0, "name": "Morocco", "short_name": "MAR"},
    {"id": 0, "name": "Japan", "short_name": "JPN"},
    {"id": 0, "name": "Korea Republic", "short_name": "KOR"},
    {"id": 0, "name": "USA", "short_name": "USA"},
    {"id": 0, "name": "Mexico", "short_name": "MEX"},
    {"id": 0, "name": "Canada", "short_name": "CAN"},
    {"id": 0, "name": "Uruguay", "short_name": "URU"},
    {"id": 0, "name": "Colombia", "short_name": "COL"},
    {"id": 0, "name": "Ecuador", "short_name": "ECU"},
    {"id": 0, "name": "Senegal", "short_name": "SEN"},
    {"id": 0, "name": "Australia", "short_name": "AUS"},
    {"id": 0, "name": "Saudi Arabia", "short_name": "KSA"},
    {"id": 0, "name": "Iran", "short_name": "IRN"},
    {"id": 0, "name": "Qatar", "short_name": "QAT"},
    {"id": 0, "name": "Switzerland", "short_name": "SUI"},
    {"id": 0, "name": "Denmark", "short_name": "DEN"},
    {"id": 0, "name": "Poland", "short_name": "POL"},
    {"id": 0, "name": "Serbia", "short_name": "SRB"},
    {"id": 0, "name": "Wales", "short_name": "WAL"},
    {"id": 0, "name": "Costa Rica", "short_name": "CRC"},
    {"id": 0, "name": "Cameroon", "short_name": "CMR"},
    {"id": 0, "name": "Ghana", "short_name": "GHA"},
]
