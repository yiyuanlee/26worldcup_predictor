from datetime import datetime, timezone


def _parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def compute_advanced_form(
    matches: list[dict],
    team: str,
    window: int = 5,
    reference_date: str | None = None,
    team_matches: list[dict] | None = None,
) -> dict[str, float]:
    """进阶状态：零封率、双方进球率、休息天数。"""
    if team_matches is None:
        team_matches = [
            m for m in matches if m["home_team"] == team or m["away_team"] == team
        ]
    recent = team_matches[-window:]

    if not recent:
        return {
            "clean_sheet_rate": 0.0,
            "btts_rate": 0.0,
            "avg_goal_diff": 0.0,
            "unbeaten_rate": 0.0,
            "days_since_last": 7.0,
        }

    clean_sheets = btts = unbeaten = 0
    goal_diff_sum = 0

    for m in recent:
        is_home = m["home_team"] == team
        scored = m["home_goals"] if is_home else m["away_goals"]
        conceded = m["away_goals"] if is_home else m["home_goals"]
        goal_diff_sum += scored - conceded
        if conceded == 0:
            clean_sheets += 1
        if scored > 0 and conceded > 0:
            btts += 1
        if scored >= conceded:
            unbeaten += 1

    n = len(recent)
    days_since = 7.0
    last = recent[-1]
    if reference_date and last.get("date"):
        ref = _parse_date(reference_date)
        last_dt = _parse_date(last["date"])
        if ref and last_dt:
            days_since = max(0.0, (ref - last_dt).total_seconds() / 86400)

    return {
        "clean_sheet_rate": clean_sheets / n,
        "btts_rate": btts / n,
        "avg_goal_diff": goal_diff_sum / n,
        "unbeaten_rate": unbeaten / n,
        "days_since_last": days_since,
    }


def advanced_form_features(
    matches: list[dict],
    home_team: str,
    away_team: str,
    window: int = 5,
    reference_date: str | None = None,
    home_matches: list[dict] | None = None,
    away_matches: list[dict] | None = None,
) -> dict[str, float]:
    home_adv = compute_advanced_form(
        matches, home_team, window, reference_date, team_matches=home_matches
    )
    away_adv = compute_advanced_form(
        matches, away_team, window, reference_date, team_matches=away_matches
    )

    features = {}
    for k, v in home_adv.items():
        features[f"home_{k}"] = v
    for k, v in away_adv.items():
        features[f"away_{k}"] = v

    features["rest_diff"] = away_adv["days_since_last"] - home_adv["days_since_last"]
    features["clean_sheet_diff"] = home_adv["clean_sheet_rate"] - away_adv["clean_sheet_rate"]
    return features
