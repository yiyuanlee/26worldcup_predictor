from dataclasses import dataclass


@dataclass
class FormStats:
    """球队近期状态统计。"""

    points_per_game: float
    goals_scored_avg: float
    goals_conceded_avg: float
    wins: int
    draws: int
    losses: int
    matches_played: int

    @property
    def win_rate(self) -> float:
        if self.matches_played == 0:
            return 0.33
        return self.wins / self.matches_played

    def to_dict(self, prefix: str) -> dict[str, float]:
        return {
            f"{prefix}_ppg": self.points_per_game,
            f"{prefix}_goals_scored_avg": self.goals_scored_avg,
            f"{prefix}_goals_conceded_avg": self.goals_conceded_avg,
            f"{prefix}_win_rate": self.win_rate,
            f"{prefix}_matches": float(self.matches_played),
        }


def _result_points(is_win: bool, is_draw: bool) -> int:
    if is_win:
        return 3
    if is_draw:
        return 1
    return 0


def compute_form(
    matches: list[dict],
    team: str,
    window: int = 5,
    team_matches: list[dict] | None = None,
) -> FormStats:
    """
    计算球队近期状态。

    每条 match 需包含: home_team, away_team, home_goals, away_goals
    按时间顺序排列，取该队最近 window 场。
    """
    if team_matches is None:
        team_matches = [
            m
            for m in matches
            if m["home_team"] == team or m["away_team"] == team
        ]
    team_matches = team_matches[-window:]

    if not team_matches:
        return FormStats(0.0, 0.0, 0.0, 0, 0, 0, 0)

    points = goals_scored = goals_conceded = 0
    wins = draws = losses = 0

    for m in team_matches:
        is_home = m["home_team"] == team
        scored = m["home_goals"] if is_home else m["away_goals"]
        conceded = m["away_goals"] if is_home else m["home_goals"]
        goals_scored += scored
        goals_conceded += conceded

        if scored > conceded:
            wins += 1
            points += 3
        elif scored == conceded:
            draws += 1
            points += 1
        else:
            losses += 1

    n = len(team_matches)
    return FormStats(
        points_per_game=points / n,
        goals_scored_avg=goals_scored / n,
        goals_conceded_avg=goals_conceded / n,
        wins=wins,
        draws=draws,
        losses=losses,
        matches_played=n,
    )
