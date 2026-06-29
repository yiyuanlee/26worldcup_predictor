from src.data.odds_api import OddsAPIClient
from src.features.builder import MatchContext
from src.features.odds_features import OddsFeatures
from src.model.predict import MatchPredictor


def predict_match(
    history: list[dict],
    home_team: str,
    away_team: str,
    odds: OddsFeatures | None = None,
    fetch_odds: bool = False,
    sport: str | None = None,
    context: MatchContext | None = None,
) -> dict:
    """完整预测流水线。"""
    if fetch_odds and odds is None:
        try:
            from src.config import DEFAULT_SPORT
            client = OddsAPIClient()
            odds = client.find_match_odds(
                home_team, away_team, sport or DEFAULT_SPORT
            )
        except (ValueError, Exception):
            odds = None

    predictor = MatchPredictor()
    result = predictor.predict(
        history, home_team, away_team, odds=odds, context=context
    )

    if odds:
        result["odds_source"] = "api"
        result["market_implied"] = {
            "home_win": round(odds.home_implied, 4),
            "draw": round(odds.draw_implied, 4),
            "away_win": round(odds.away_implied, 4),
        }
    else:
        result["odds_source"] = "default"

    return result
