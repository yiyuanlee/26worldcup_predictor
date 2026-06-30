"""淘汰赛阶段概率校准：90 分钟内平局率显著高于小组赛。"""

from src.features.world_cup import is_knockout_stage

__all__ = ["is_knockout_stage", "calibrate_knockout_probs"]


def _parity_score(features: dict[str, float]) -> float:
    """双方实力越接近，值越高 (0~1)。"""
    gap = (
        abs(features.get("form_diff_ppg", 0)) * 0.45
        + abs(features.get("standings_points_diff", 0)) * 0.08
        + abs(features.get("standings_gd_diff", 0)) * 0.04
        + abs(features.get("home_away_ppg_diff", 0)) * 0.25
    )
    return 1.0 / (1.0 + gap)


def calibrate_knockout_probs(
    probabilities: dict[str, float],
    features: dict[str, float],
    stage: str | None,
) -> dict[str, float]:
    """淘汰赛：向平局概率倾斜，修正小组赛模型在淘汰赛的偏差。"""
    if not is_knockout_stage(stage):
        return probabilities

    import numpy as np

    p = np.array([
        probabilities["home_win"],
        probabilities["draw"],
        probabilities["away_win"],
    ], dtype=float)

    parity = _parity_score(features)
    # 淘汰赛 90 分钟平局率约 30–40%，势均力敌时更高
    draw_target = 0.26 + 0.22 * parity
    boost = (draw_target - p[1]) * 0.9
    if boost > 0:
        p[1] += boost
        ha = p[0] + p[2]
        if ha > 1e-6:
            p[0] -= boost * (p[0] / ha)
            p[2] -= boost * (p[2] / ha)

    p = np.clip(p, 0.02, None)
    p /= p.sum()

    return {
        "home_win": round(float(p[0]), 4),
        "draw": round(float(p[1]), 4),
        "away_win": round(float(p[2]), 4),
    }
