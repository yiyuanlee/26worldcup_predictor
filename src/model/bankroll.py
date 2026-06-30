"""基于模型概率与市场赔率的预算分配（Kelly / 分数 Kelly）。"""

from dataclasses import dataclass

MIN_STAKE_PCT = 0.005  # 低于 0.5% 视为无效仓位（含浮点噪声）

RISK_PROFILES = {
    "conservative": {
        "kelly_fraction": 0.15,
        "min_edge": 0.05,
        "min_model_prob": 0.38,
        "max_single_pct": 0.03,
        "max_slate_pct": 0.12,
    },
    "moderate": {
        "kelly_fraction": 0.25,
        "min_edge": 0.03,
        "min_model_prob": 0.35,
        "max_single_pct": 0.05,
        "max_slate_pct": 0.20,
    },
    "aggressive": {
        "kelly_fraction": 0.40,
        "min_edge": 0.02,
        "min_model_prob": 0.33,
        "max_single_pct": 0.08,
        "max_slate_pct": 0.35,
    },
}


@dataclass
class BetOpportunity:
    home_team: str
    away_team: str
    date: str
    stage: str
    pick: str
    model_prob: float
    market_prob: float | None
    edge: float
    decimal_odds: float
    kelly_raw: float
    stake_pct: float
    stake: float
    expected_value: float
    has_market_odds: bool


def kelly_fraction(prob: float, decimal_odds: float) -> float:
    """Full Kelly: f* = (bp - q) / b, b = odds - 1."""
    if decimal_odds <= 1.0 or prob <= 0 or prob >= 1:
        return 0.0
    b = decimal_odds - 1.0
    q = 1.0 - prob
    f = (b * prob - q) / b
    return max(0.0, f)


def _best_pick(
    model_probs: dict[str, float],
    market_probs: dict[str, float] | None,
    raw_odds: dict[str, float] | None,
) -> tuple[str, float, float | None, float, float, bool]:
    """返回 (pick_key, model_p, market_p, edge, decimal_odds, has_market)。"""
    best_key = max(model_probs, key=model_probs.get)
    model_p = model_probs[best_key]

    if market_probs and raw_odds:
        market_p = market_probs.get(best_key, 0.0)
        edge = model_p - market_p
        odds_map = {"home_win": "home", "draw": "draw", "away_win": "away"}
        decimal = float(raw_odds.get(odds_map[best_key], 0.0))
        return best_key, model_p, market_p, edge, decimal, True

    # 无市场赔率：边际相对均衡市场(1/3)，Kelly 用基准赔率 3.0（勿用 1/模型概率，否则 EV≈0）
    baseline = 1.0 / 3.0
    edge = model_p - baseline
    decimal = 1.0 / baseline
    return best_key, model_p, None, edge, decimal, False


def build_bankroll_plan(
    matches: list[dict],
    analyses: list[dict],
    bankroll: float,
    risk: str = "moderate",
) -> dict:
    """
    matches: upcoming 赛程
    analyses: 与 matches 同序的 predict/analysis 结果
    """
    profile = RISK_PROFILES.get(risk, RISK_PROFILES["moderate"])
    k_frac = profile["kelly_fraction"]
    opportunities: list[BetOpportunity] = []

    for match, analysis in zip(matches, analyses):
        probs = analysis["probabilities"]
        market = analysis.get("market_implied")
        raw = analysis.get("raw_odds")

        pick, model_p, market_p, edge, decimal, has_market = _best_pick(
            probs, market, raw
        )

        if model_p < profile["min_model_prob"]:
            continue
        if edge < profile["min_edge"]:
            continue

        k_raw = kelly_fraction(model_p, decimal) * k_frac
        stake_pct = min(k_raw, profile["max_single_pct"])
        if stake_pct < MIN_STAKE_PCT:
            continue

        stake = round(bankroll * stake_pct, 2)
        ev = round(stake * (model_p * decimal - 1.0), 2)

        opportunities.append(
            BetOpportunity(
                home_team=match["home_team"],
                away_team=match["away_team"],
                date=match.get("date", "")[:10],
                stage=match.get("stage", ""),
                pick=pick,
                model_prob=round(model_p, 4),
                market_prob=round(market_p, 4) if market_p is not None else None,
                edge=round(edge, 4),
                decimal_odds=round(decimal, 2),
                kelly_raw=round(k_raw, 4),
                stake_pct=round(stake_pct, 4),
                stake=stake,
                expected_value=ev,
                has_market_odds=has_market,
            )
        )

    # 按 edge 降序，总投入不超过 max_slate_pct
    opportunities.sort(key=lambda x: x.edge, reverse=True)
    max_slate = bankroll * profile["max_slate_pct"]
    total = sum(o.stake for o in opportunities)
    if total > max_slate and total > 0:
        scale = max_slate / total
        for o in opportunities:
            o.stake = round(o.stake * scale, 2)
            o.stake_pct = round(o.stake / bankroll, 4)
            o.expected_value = round(o.stake * (o.model_prob * o.decimal_odds - 1.0), 2)

    allocated = round(sum(o.stake for o in opportunities), 2)

    return {
        "risk_profile": risk,
        "rules": profile,
        "summary": {
            "bankroll": bankroll,
            "allocated": allocated,
            "remaining": round(bankroll - allocated, 2),
            "allocation_pct": round(allocated / bankroll, 4) if bankroll else 0,
            "slate_matches": len(matches),
            "recommended_bets": len(opportunities),
        },
        "recommendations": [
            {
                "home_team": o.home_team,
                "away_team": o.away_team,
                "date": o.date,
                "stage": o.stage,
                "pick": o.pick,
                "model_prob": o.model_prob,
                "market_prob": o.market_prob,
                "edge": o.edge,
                "decimal_odds": o.decimal_odds,
                "kelly_pct": o.kelly_raw,
                "stake_pct": o.stake_pct,
                "stake": o.stake,
                "expected_value": o.expected_value,
                "has_market_odds": o.has_market_odds,
            }
            for o in opportunities
        ],
    }
