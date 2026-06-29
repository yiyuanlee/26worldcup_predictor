from dataclasses import dataclass


@dataclass
class TeamStanding:
    position: int
    points: int
    goal_difference: int
    played: int
    won: int
    draw: int
    lost: int
    goals_for: int
    goals_against: int
    group: str | None = None

    @property
    def ppg(self) -> float:
        if self.played == 0:
            return 0.0
        return self.points / self.played


def normalize_position(position: int, total_teams: int) -> float:
    """排名归一化：第 1 名 → 1.0，最后一名 → 0.0。"""
    if total_teams <= 1:
        return 0.5
    return 1.0 - (position - 1) / (total_teams - 1)


def compute_standings_features(
    home_team: str,
    away_team: str,
    standings: dict[str, TeamStanding],
    total_teams: int = 20,
    group_size: int = 4,
) -> dict[str, float]:
    home = standings.get(home_team)
    away = standings.get(away_team)

    if not home or not away:
        return {
            "home_position_norm": 0.5,
            "away_position_norm": 0.5,
            "standings_points_diff": 0.0,
            "standings_gd_diff": 0.0,
            "standings_ppg_diff": 0.0,
            "home_position": 10.0,
            "away_position": 10.0,
        }

    # 世界杯小组赛：按小组内 4 队归一化排名
    norm_teams = group_size if (home.group or away.group) else total_teams

    return {
        "home_position_norm": normalize_position(home.position, norm_teams),
        "away_position_norm": normalize_position(away.position, norm_teams),
        "standings_points_diff": float(home.points - away.points),
        "standings_gd_diff": float(home.goal_difference - away.goal_difference),
        "standings_ppg_diff": home.ppg - away.ppg,
        "home_position": float(home.position),
        "away_position": float(away.position),
    }
