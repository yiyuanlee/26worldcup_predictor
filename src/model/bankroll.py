"""基于模型概率与市场赔率的预算分配（Kelly / 分数 Kelly）。"""

from dataclasses import dataclass

MIN_STAKE_PCT = 0.01  # 单场最低 1%


def _distribute_integer_percents(
    weights: list[float],
    bankroll: float,
    max_slate_pct: float,
    max_single_pct: float,
) -> list[tuple[float, int]]:
    """按权重分配整百分比（1% 步进），返回 (stake_pct, stake_int)。"""
    n = len(weights)
    if n == 0:
        return []

    total_w = sum(weights)
    if total_w <= 0:
        weights = [1.0] * n
        total_w = float(n)

    target_units = int(round(max_slate_pct * 100))
    max_single_units = max(1, int(max_single_pct * 100))
    min_units = 1

    if target_units < n * min_units:
        n = min(n, max(1, target_units // min_units))
        weights = weights[:n]
        total_w = sum(weights) or float(n)

    raw_units = [min(w / total_w * target_units, max_single_units) for w in weights]
    units = [max(min_units, int(u)) for u in raw_units]
    remainders = [ru - int(ru) for ru in raw_units]

    # 不足目标：按余数补 1%
    while sum(units) < target_units:
        idx = max(range(n), key=lambda i: (remainders[i], weights[i]))
        if units[idx] >= max_single_units:
            remainders[idx] = -1.0
            if all(units[i] >= max_single_units for i in range(n)):
                break
            continue
        units[idx] += 1
        remainders[idx] = -1.0

    # 超出目标：从权重最低且 > min 的场次减 1%
    while sum(units) > target_units:
        idx = min(
            (i for i in range(n) if units[i] > min_units),
            key=lambda i: (weights[i], units[i]),
            default=None,
        )
        if idx is None:
            break
        units[idx] -= 1

    out: list[tuple[float, int]] = []
    for u in units:
        pct = round(u / 100.0, 4)
        stake = int(round(bankroll * pct))
        if stake < 1 and bankroll >= 1:
            stake = 1
            pct = round(stake / bankroll, 4)
        out.append((pct, stake))
    return out

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
    stake: int
    expected_value: int
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
                stake_pct=0.0,
                stake=0,
                expected_value=0,
                has_market_odds=has_market,
            )
        )

    opportunities.sort(key=lambda x: x.edge, reverse=True)

    weights = [max(o.edge, 0.001) for o in opportunities]
    allocations = _distribute_integer_percents(
        weights,
        bankroll,
        profile["max_slate_pct"],
        profile["max_single_pct"],
    )
    for o, (stake_pct, stake) in zip(opportunities, allocations):
        o.stake_pct = stake_pct
        o.stake = stake
        o.expected_value = int(round(stake * (o.model_prob * o.decimal_odds - 1.0)))

    allocated = sum(o.stake for o in opportunities)

    return {
        "risk_profile": risk,
        "rules": profile,
        "summary": {
            "bankroll": int(round(bankroll)),
            "allocated": allocated,
            "remaining": int(round(bankroll)) - allocated,
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
