from src.features.form import FormStats, compute_form


def compute_home_form(
    matches: list[dict],
    team: str,
    window: int = 5,
    home_only: list[dict] | None = None,
) -> FormStats:
    """球队主场近期状态（仅统计主场作战）。"""
    if home_only is None:
        home_only = [m for m in matches if m["home_team"] == team]
    return compute_form(home_only, team, window, team_matches=home_only)


def compute_away_form(
    matches: list[dict],
    team: str,
    window: int = 5,
    away_only: list[dict] | None = None,
) -> FormStats:
    """球队客场近期状态（仅统计客场作战）。"""
    if away_only is None:
        away_only = [m for m in matches if m["away_team"] == team]
    return compute_form(away_only, team, window, team_matches=away_only)


def home_away_features(
    matches: list[dict],
    home_team: str,
    away_team: str,
    window: int = 5,
    home_index: dict[str, list[dict]] | None = None,
    away_index: dict[str, list[dict]] | None = None,
) -> dict[str, float]:
    home_only = home_index.get(home_team, []) if home_index is not None else None
    away_only = away_index.get(away_team, []) if away_index is not None else None

    home_at_home = compute_home_form(matches, home_team, window, home_only)
    away_on_road = compute_away_form(matches, away_team, window, away_only)

    return {
        "home_home_ppg": home_at_home.points_per_game,
        "home_home_win_rate": home_at_home.win_rate,
        "home_home_goals_scored": home_at_home.goals_scored_avg,
        "home_home_goals_conceded": home_at_home.goals_conceded_avg,
        "away_away_ppg": away_on_road.points_per_game,
        "away_away_win_rate": away_on_road.win_rate,
        "away_away_goals_scored": away_on_road.goals_scored_avg,
        "away_away_goals_conceded": away_on_road.goals_conceded_avg,
        "home_away_ppg_diff": home_at_home.points_per_game - away_on_road.points_per_game,
    }
