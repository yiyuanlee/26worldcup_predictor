"""2026 世界杯赛程加载与缓存更新。"""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import CACHE_DIR, DATA_DIR
from src.data.cache_store import invalidate, read_csv_rows, write_csv_rows
from src.features.standings import TeamStanding

WC2026_SCHEDULE = DATA_DIR / "wc2026_schedule.json"
WC2026_RESULTS = DATA_DIR / "wc2026_results.csv"
WC2026_HISTORICAL = DATA_DIR / "world_cup_matches.csv"


def load_wc2026_schedule() -> dict:
    if not WC2026_SCHEDULE.exists():
        return {}
    return json.loads(WC2026_SCHEDULE.read_text(encoding="utf-8"))


def get_wc2026_finished_matches() -> list[dict]:
    """2026 世界杯已结束比赛。"""
    if not WC2026_RESULTS.exists():
        return []
    rows = read_csv_rows(WC2026_RESULTS)
    for row in rows:
        row["status"] = "FINISHED"
    return rows


def get_wc2026_upcoming_matches() -> list[dict]:
    """2026 世界杯待赛（含今日）。"""
    data = load_wc2026_schedule()
    upcoming = []
    for m in data.get("matches", []):
        if m.get("status") in ("SCHEDULED", "TIMED"):
            if m.get("home_team") == "TBD":
                continue
            upcoming.append({
                "home_team": m["home_team"],
                "away_team": m["away_team"],
                "date": m["date"],
                "status": m["status"],
                "stage": m.get("stage", ""),
                "match_no": m.get("match_no"),
            })
    upcoming.sort(key=lambda x: x["date"])
    return upcoming


def get_wc2026_standings() -> dict[str, TeamStanding]:
    """从赛程文件读取小组排名。"""
    data = load_wc2026_schedule()
    result: dict[str, TeamStanding] = {}
    for group, teams in data.get("groups", {}).items():
        for t in teams:
            result[t["team"]] = TeamStanding(
                position=t["position"],
                points=t["points"],
                goal_difference=t["goal_difference"],
                played=t["played"],
                won=t["won"],
                draw=t["draw"],
                lost=t["lost"],
                goals_for=t["goals_for"],
                goals_against=t["goals_against"],
                group=group,
            )
    return result


def get_wc2026_teams() -> list[dict]:
    data = load_wc2026_schedule()
    teams = []
    for group, rows in data.get("groups", {}).items():
        for t in rows:
            teams.append({
                "id": 0,
                "name": t["team"],
                "short_name": group,
                "group": group,
            })
    return teams


def get_wc2026_group_tables() -> dict[str, list[dict]]:
    data = load_wc2026_schedule()
    groups: dict[str, list[dict]] = {}
    for group, teams in data.get("groups", {}).items():
        groups[group] = [
            {
                "team": t["team"],
                "position": t["position"],
                "points": t["points"],
                "played": t["played"],
                "won": t["won"],
                "draw": t["draw"],
                "lost": t["lost"],
                "goal_difference": t["goal_difference"],
            }
            for t in teams
        ]
    return groups


def get_wc2026_full_history() -> list[dict]:
    """2018+2022 历史 + 2026 已赛，用于模型预测。"""
    history: list[dict] = []

    if WC2026_HISTORICAL.exists():
        history.extend(read_csv_rows(WC2026_HISTORICAL))

    history.extend(get_wc2026_finished_matches())
    history.sort(key=lambda x: x.get("date", ""))
    return history


def refresh_wc2026_cache() -> dict:
    """将 2026 世界杯数据写入 data/cache/WC_* 缓存。"""
    invalidate("")
    CACHE_DIR.mkdir(exist_ok=True)
    competition = "WC"

    finished = get_wc2026_finished_matches()
    upcoming = get_wc2026_upcoming_matches()
    teams = get_wc2026_teams()
    standings = get_wc2026_standings()

    (CACHE_DIR / f"{competition}_matches.json").write_text(
        json.dumps(finished, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CACHE_DIR / f"{competition}_upcoming.json").write_text(
        json.dumps(upcoming, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (CACHE_DIR / f"{competition}_teams.json").write_text(
        json.dumps(teams, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    standings_raw = {
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
    (CACHE_DIR / f"{competition}_standings.json").write_text(
        json.dumps(standings_raw, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    full_history = get_wc2026_full_history()
    write_csv_rows(
        CACHE_DIR / f"{competition}_matches.csv",
        [
            {
                "date": m.get("date", ""),
                "home_team": m["home_team"],
                "away_team": m["away_team"],
                "home_goals": m["home_goals"],
                "away_goals": m["away_goals"],
                "stage": m.get("stage", ""),
            }
            for m in full_history
        ],
        ["date", "home_team", "away_team", "home_goals", "away_goals", "stage"],
    )

    schedule = load_wc2026_schedule()
    meta = {
        "competition": "WC",
        "competition_name": "世界杯 2026",
        "synced_at": schedule.get("updated_at", datetime.now(timezone.utc).isoformat()),
        "finished_matches": len(finished),
        "upcoming_matches": len(upcoming),
        "teams": len(teams),
        "source": "wc2026_schedule",
        "stage": "Round of 32",
    }
    (CACHE_DIR / f"{competition}_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta
