from dataclasses import dataclass


@dataclass
class H2HStats:
    """双方历史交手统计。"""

    home_wins: float
    draws: float
    away_wins: float
    home_goals_avg: float
    away_goals_avg: float
    total_matches: int

    @property
    def home_win_rate(self) -> float:
        if self.total_matches == 0:
            return 0.33
        return self.home_wins / self.total_matches

    @property
    def draw_rate(self) -> float:
        if self.total_matches == 0:
            return 0.34
        return self.draws / self.total_matches

    @property
    def away_win_rate(self) -> float:
        if self.total_matches == 0:
            return 0.33
        return self.away_wins / self.total_matches

    def to_dict(self) -> dict[str, float]:
        return {
            "h2h_home_win_rate": self.home_win_rate,
            "h2h_draw_rate": self.draw_rate,
            "h2h_away_win_rate": self.away_win_rate,
            "h2h_home_goals_avg": self.home_goals_avg,
            "h2h_away_goals_avg": self.away_goals_avg,
            "h2h_total_matches": float(self.total_matches),
        }


def compute_h2h(
    matches: list[dict],
    home_team: str,
    away_team: str,
    window: int = 10,
) -> H2HStats:
    """
    从历史比赛记录计算双方交手战绩。

    每条 match 需包含: home_team, away_team, home_goals, away_goals
    """
    relevant = [
        m
        for m in matches
        if {m["home_team"], m["away_team"]} == {home_team, away_team}
    ]
    relevant = relevant[-window:]

    if not relevant:
        return H2HStats(0, 0, 0, 0.0, 0.0, 0)

    home_wins = draws = away_wins = 0
    home_goals_sum = away_goals_sum = 0.0

    for m in relevant:
        h_goals = m["home_goals"]
        a_goals = m["away_goals"]

        if m["home_team"] == home_team:
            home_goals_sum += h_goals
            away_goals_sum += a_goals
            if h_goals > a_goals:
                home_wins += 1
            elif h_goals == a_goals:
                draws += 1
            else:
                away_wins += 1
        else:
            home_goals_sum += a_goals
            away_goals_sum += h_goals
            if a_goals > h_goals:
                home_wins += 1
            elif a_goals == h_goals:
                draws += 1
            else:
                away_wins += 1

    n = len(relevant)
    return H2HStats(
        home_wins=home_wins,
        draws=draws,
        away_wins=away_wins,
        home_goals_avg=home_goals_sum / n,
        away_goals_avg=away_goals_sum / n,
        total_matches=n,
    )
