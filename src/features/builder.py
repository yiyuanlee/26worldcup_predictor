from dataclasses import dataclass, field

from src.features.advanced import advanced_form_features
from src.features.world_cup import tournament_experience_features
from src.features.form import compute_form
from src.features.h2h import compute_h2h
from src.features.home_away import home_away_features
from src.features.odds_features import OddsFeatures, odds_to_implied
from src.features.standings import TeamStanding, compute_standings_features

FEATURE_COLUMNS = [
    # H2H
    "h2h_home_win_rate",
    "h2h_draw_rate",
    "h2h_away_win_rate",
    "h2h_home_goals_avg",
    "h2h_away_goals_avg",
    # 近期状态
    "home_ppg",
    "home_goals_scored_avg",
    "home_goals_conceded_avg",
    "home_win_rate",
    "away_ppg",
    "away_goals_scored_avg",
    "away_goals_conceded_avg",
    "away_win_rate",
    # 主客场分化
    "home_home_ppg",
    "home_home_win_rate",
    "away_away_ppg",
    "away_away_win_rate",
    "home_away_ppg_diff",
    # 排名
    "home_position_norm",
    "away_position_norm",
    "standings_points_diff",
    "standings_gd_diff",
    "standings_ppg_diff",
    # 进阶状态
    "home_clean_sheet_rate",
    "away_clean_sheet_rate",
    "home_unbeaten_rate",
    "away_unbeaten_rate",
    "rest_diff",
    # 世界杯淘汰赛经验
    "home_knockout_rate",
    "away_knockout_rate",
    # 赔率
    "odds_home_implied",
    "odds_draw_implied",
    "odds_away_implied",
    # 差值
    "form_diff_ppg",
    "form_diff_goals_scored",
    "form_diff_goals_conceded",
]


@dataclass
class MatchContext:
    standings: dict[str, TeamStanding] = field(default_factory=dict)
    total_teams: int = 20
    match_date: str | None = None
    is_international: bool = False
    group_size: int = 4


def build_feature_vector(
    history: list[dict],
    home_team: str,
    away_team: str,
    odds: OddsFeatures | None = None,
    context: MatchContext | None = None,
    h2h_window: int = 10,
    form_window: int = 5,
) -> dict[str, float]:
    """合并所有特征为单一特征字典。"""
    context = context or MatchContext()

    h2h = compute_h2h(history, home_team, away_team, h2h_window)
    home_form = compute_form(history, home_team, form_window)
    away_form = compute_form(history, away_team, form_window)

    if odds is None:
        odds = odds_to_implied(2.5, 3.3, 2.8)

    features: dict[str, float] = {}
    features.update(h2h.to_dict())
    features.update(home_form.to_dict("home"))
    features.update(away_form.to_dict("away"))
    features.update(home_away_features(history, home_team, away_team, form_window))
    features.update(
        compute_standings_features(
            home_team,
            away_team,
            context.standings,
            context.total_teams,
            context.group_size,
        )
    )
    features.update(
        advanced_form_features(
            history, home_team, away_team, form_window, context.match_date
        )
    )
    if context.is_international:
        features.update(
            tournament_experience_features(history, home_team, away_team, form_window)
        )
    else:
        features["home_knockout_rate"] = 0.0
        features["away_knockout_rate"] = 0.0
    features.update(odds.to_dict())

    features["form_diff_ppg"] = home_form.points_per_game - away_form.points_per_game
    features["form_diff_goals_scored"] = (
        home_form.goals_scored_avg - away_form.goals_scored_avg
    )
    features["form_diff_goals_conceded"] = (
        home_form.goals_conceded_avg - away_form.goals_conceded_avg
    )

    return features


def features_to_row(features: dict[str, float], columns: list[str] | None = None) -> list[float]:
    cols = columns or FEATURE_COLUMNS
    return [features.get(col, 0.0) for col in cols]
