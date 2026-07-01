import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from src.config import (
    CACHE_DIR,
    COMPETITION_MAP,
    DEFAULT_COMPETITION,
    INTERNATIONAL_COMPETITIONS,
    FOOTBALL_DATA_API_KEY,
    FOOTBALL_DATA_BASE,
)
from src.features.standings import TeamStanding


def resolve_football_data_api_key(api_key: str | None = None) -> str:
    return api_key or os.getenv("FOOTBALL_DATA_API_KEY", "") or FOOTBALL_DATA_API_KEY


def map_fd_stage(fd_stage: str | None) -> str:
    """football-data.org stage → 站内 stage 代码。"""
    mapping = {
        "GROUP_STAGE": "group",
        "LAST_32": "round32",
        "LAST_16": "round16",
        "QUARTER_FINALS": "quarter",
        "SEMI_FINALS": "semi",
        "FINAL": "final",
        "THIRD_PLACE": "third",
        "PLAYOFFS": "knockout",
    }
    if not fd_stage:
        return ""
    return mapping.get(fd_stage, fd_stage.lower())


class FootballDataClient:
    """football-data.org API 客户端 — https://www.football-data.org/"""

    def __init__(self, api_key: str | None = None):
        self.api_key = resolve_football_data_api_key(api_key)
        if not self.api_key:
            raise ValueError(
                "未设置 FOOTBALL_DATA_API_KEY。请在 .env 中配置，"
                "或在 https://www.football-data.org/client/register 免费注册"
            )
        self.session = requests.Session()
        self.session.headers["X-Auth-Token"] = self.api_key

    def _get(self, path: str, params: dict | None = None) -> dict:
        resp = self.session.get(
            f"{FOOTBALL_DATA_BASE}{path}", params=params, timeout=30
        )
        if resp.status_code == 429:
            raise RuntimeError("API 请求频率超限，请稍后再试（免费版 10 次/分钟）")
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _normalize_match(m: dict) -> dict:
        score = m.get("score", {}).get("fullTime", {}) or {}
        home = m.get("homeTeam") or {}
        away = m.get("awayTeam") or {}
        return {
            "id": m.get("id"),
            "home_team": home.get("name", "TBD"),
            "away_team": away.get("name", "TBD"),
            "home_team_id": home.get("id"),
            "away_team_id": away.get("id"),
            "home_goals": score.get("home") if score.get("home") is not None else 0,
            "away_goals": score.get("away") if score.get("away") is not None else 0,
            "date": m.get("utcDate", ""),
            "status": m.get("status", ""),
            "stage": map_fd_stage(m.get("stage")),
            "competition": m.get("competition", {}).get("code", ""),
        }

    def get_competition_matches(
        self,
        competition: str = DEFAULT_COMPETITION,
        status: str = "FINISHED",
        limit: int = 100,
    ) -> list[dict]:
        if competition in INTERNATIONAL_COMPETITIONS:
            limit = max(limit, 200)
        data = self._get(
            f"/competitions/{competition}/matches",
            {"status": status, "limit": limit},
        )
        return [self._normalize_match(m) for m in data.get("matches", [])]

    def get_upcoming_matches(
        self,
        competition: str = DEFAULT_COMPETITION,
        limit: int = 20,
    ) -> list[dict]:
        if competition in INTERNATIONAL_COMPETITIONS:
            limit = max(limit, 64)
        data = self._get(
            f"/competitions/{competition}/matches",
            {"status": "SCHEDULED,TIMED", "limit": limit},
        )
        return [self._normalize_match(m) for m in data.get("matches", [])]

    def get_standings(
        self, competition: str = DEFAULT_COMPETITION
    ) -> dict[str, TeamStanding]:
        data = self._get(f"/competitions/{competition}/standings")
        result: dict[str, TeamStanding] = {}
        is_wc = competition in INTERNATIONAL_COMPETITIONS

        for table in data.get("standings", []):
            table_type = table.get("type")
            if not is_wc and table_type != "TOTAL":
                continue
            if is_wc and table_type not in ("TOTAL", "GROUP"):
                continue

            group = table.get("group", "").replace("GROUP_", "") or None
            for row in table.get("table", []):
                team = row["team"]["name"]
                result[team] = TeamStanding(
                    position=row["position"],
                    points=row["points"],
                    goal_difference=row["goalDifference"],
                    played=row["playedGames"],
                    won=row["won"],
                    draw=row["draw"],
                    lost=row["lost"],
                    goals_for=row["goalsFor"],
                    goals_against=row["goalsAgainst"],
                    group=group,
                )
        return result

    def get_teams(self, competition: str = DEFAULT_COMPETITION) -> list[dict]:
        data = self._get(f"/competitions/{competition}/teams")
        return [
            {"id": t["id"], "name": t["name"], "short_name": t.get("shortName", "")}
            for t in data.get("teams", [])
        ]

    def get_team_matches(
        self,
        team_id: int,
        limit: int = 30,
        status: str = "FINISHED",
    ) -> list[dict]:
        data = self._get(
            f"/teams/{team_id}/matches",
            {"limit": limit, "status": status},
        )
        return [self._normalize_match(m) for m in data.get("matches", [])]


def _cache_path(competition: str, kind: str) -> Path:
    return CACHE_DIR / f"{competition}_{kind}.json"


def sync_competition_data(
    competition: str = DEFAULT_COMPETITION,
    client: FootballDataClient | None = None,
) -> dict:
    """
    从 football-data.org 同步比赛、排名、球队到本地缓存。
    返回同步摘要。
    """
    client = client or FootballDataClient()

    matches = client.get_competition_matches(competition, status="FINISHED", limit=100)
    upcoming = client.get_upcoming_matches(competition)
    standings = client.get_standings(competition)
    teams = client.get_teams(competition)

    _cache_path(competition, "matches").write_text(
        json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _cache_path(competition, "upcoming").write_text(
        json.dumps(upcoming, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _cache_path(competition, "teams").write_text(
        json.dumps(teams, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    standings_serializable = {
        name: {
            "position": s.position,
            "points": s.points,
            "goal_difference": s.goal_difference,
            "played": s.played,
            "won": s.won,
            "draw": s.draw,
            "lost": s.lost,
            "goals_for": s.goals_for,
            "goals_against": s.goals_against,
            "group": s.group,
        }
        for name, s in standings.items()
    }
    _cache_path(competition, "standings").write_text(
        json.dumps(standings_serializable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    csv_rows = []
    for m in matches:
        csv_rows.append({
            "date": m["date"],
            "home_team": m["home_team"],
            "away_team": m["away_team"],
            "home_goals": m["home_goals"],
            "away_goals": m["away_goals"],
        })
    if csv_rows:
        df = pd.DataFrame(csv_rows)
        df = df.sort_values("date")
        df.to_csv(CACHE_DIR / f"{competition}_matches.csv", index=False)

    meta = {
        "competition": competition,
        "competition_name": COMPETITION_MAP.get(competition, {}).get("name", competition),
        "synced_at": datetime.utcnow().isoformat() + "Z",
        "finished_matches": len(matches),
        "upcoming_matches": len(upcoming),
        "teams": len(teams),
    }
    _cache_path(competition, "meta").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta


def load_cached_matches(competition: str = DEFAULT_COMPETITION) -> list[dict]:
    path = _cache_path(competition, "matches")
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_cached_standings(competition: str = DEFAULT_COMPETITION) -> dict[str, TeamStanding]:
    path = _cache_path(competition, "standings")
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        name: TeamStanding(**data)
        for name, data in raw.items()
    }


def load_group_standings(competition: str = DEFAULT_COMPETITION) -> dict[str, list[dict]]:
    """按小组整理排名，供前端展示。"""
    standings = load_cached_standings(competition)
    groups: dict[str, list[dict]] = {}
    for name, st in standings.items():
        key = st.group or "TOTAL"
        groups.setdefault(key, []).append({
            "team": name,
            "position": st.position,
            "points": st.points,
            "played": st.played,
            "won": st.won,
            "draw": st.draw,
            "lost": st.lost,
            "goal_difference": st.goal_difference,
        })
    for g in groups.values():
        g.sort(key=lambda x: x["position"])
    return groups


def load_cached_teams(competition: str = DEFAULT_COMPETITION) -> list[dict]:
    path = _cache_path(competition, "teams")
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_cached_upcoming(competition: str = DEFAULT_COMPETITION) -> list[dict]:
    path = _cache_path(competition, "upcoming")
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
