KNOCKOUT_STAGES = frozenset({
    "round32", "round16", "quarter", "semi", "final", "third", "knockout",
})


def is_knockout_stage(stage: str | None) -> bool:
    return bool(stage and stage in KNOCKOUT_STAGES)


def tournament_experience_features(
    matches: list[dict],
    home_team: str,
    away_team: str,
    window: int = 10,
) -> dict[str, float]:
    """世界杯淘汰赛经验：近 N 场中淘汰赛占比。"""
    return {
        "home_knockout_rate": _knockout_rate(matches, home_team, window),
        "away_knockout_rate": _knockout_rate(matches, away_team, window),
    }


def _knockout_rate(matches: list[dict], team: str, window: int) -> float:
    team_matches = [
        m for m in matches
        if m["home_team"] == team or m["away_team"] == team
    ][-window:]
    if not team_matches:
        return 0.0
    knockout = sum(
        1 for m in team_matches
        if m.get("stage", "group") in KNOCKOUT_STAGES
    )
    return knockout / len(team_matches)
