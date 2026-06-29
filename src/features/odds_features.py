from dataclasses import dataclass


@dataclass
class OddsFeatures:
    """赔率衍生特征（隐含概率）。"""

    home_implied: float
    draw_implied: float
    away_implied: float
    home_odds: float
    draw_odds: float
    away_odds: float

    def to_dict(self) -> dict[str, float]:
        return {
            "odds_home_implied": self.home_implied,
            "odds_draw_implied": self.draw_implied,
            "odds_away_implied": self.away_implied,
            "odds_home": self.home_odds,
            "odds_draw": self.draw_odds,
            "odds_away": self.away_odds,
        }


def odds_to_implied(home: float, draw: float, away: float) -> OddsFeatures:
    """
    将十进制赔率转换为去水后的隐含概率。

    隐含概率 = (1/赔率) / sum(1/各赔率)
    """
    if home <= 1 or draw <= 1 or away <= 1:
        return OddsFeatures(0.33, 0.34, 0.33, home, draw, away)

    raw_home = 1.0 / home
    raw_draw = 1.0 / draw
    raw_away = 1.0 / away
    total = raw_home + raw_draw + raw_away

    return OddsFeatures(
        home_implied=raw_home / total,
        draw_implied=raw_draw / total,
        away_implied=raw_away / total,
        home_odds=home,
        draw_odds=draw,
        away_odds=away,
    )


def average_odds_from_bookmakers(
    bookmakers: list[dict],
) -> OddsFeatures | None:
    """
    从 The Odds API 返回的 bookmakers 列表中提取 h2h 市场平均赔率。
    """
    home_odds_list: list[float] = []
    draw_odds_list: list[float] = []
    away_odds_list: list[float] = []

    for bm in bookmakers:
        for market in bm.get("markets", []):
            if market.get("key") != "h2h":
                continue
            outcomes = {o["name"]: o["price"] for o in market.get("outcomes", [])}
            names = list(outcomes.keys())
            if len(names) < 2:
                continue
            prices = list(outcomes.values())
            if len(prices) == 2:
                home_odds_list.append(prices[0])
                away_odds_list.append(prices[1])
            elif len(prices) >= 3:
                home_odds_list.append(prices[0])
                draw_odds_list.append(prices[1])
                away_odds_list.append(prices[2])

    if not home_odds_list or not away_odds_list:
        return None

    home_avg = sum(home_odds_list) / len(home_odds_list)
    away_avg = sum(away_odds_list) / len(away_odds_list)
    draw_avg = (
        sum(draw_odds_list) / len(draw_odds_list) if draw_odds_list else 3.3
    )

    return odds_to_implied(home_avg, draw_avg, away_avg)
