import time

import requests

from src.config import ODDS_API_BASE, ODDS_API_KEY, DEFAULT_SPORT
from src.data.world_cup import teams_match
from src.features.odds_features import OddsFeatures, average_odds_from_bookmakers

_EVENTS_CACHE: dict[str, tuple[float, list]] = {}
_CACHE_TTL_SEC = 120


class OddsAPIClient:
    """The Odds API 客户端 — https://the-odds-api.com/"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ODDS_API_KEY
        if not self.api_key:
            raise ValueError(
                "未设置 ODDS_API_KEY，请在 .env 中配置或在 https://the-odds-api.com/ 注册"
            )

    def _get(self, path: str, params: dict | None = None) -> list | dict:
        params = params or {}
        params["apiKey"] = self.api_key
        resp = requests.get(f"{ODDS_API_BASE}{path}", params=params, timeout=(3, 6))
        resp.raise_for_status()
        return resp.json()

    def list_sports(self) -> list[dict]:
        return self._get("/sports")

    def get_upcoming_odds(
        self,
        sport: str = DEFAULT_SPORT,
        regions: str = "eu",
        markets: str = "h2h",
        *,
        use_cache: bool = True,
    ) -> list[dict]:
        now = time.time()
        if use_cache and sport in _EVENTS_CACHE:
            ts, events = _EVENTS_CACHE[sport]
            if now - ts < _CACHE_TTL_SEC:
                return events

        events = self._get(
            f"/sports/{sport}/odds",
            {"regions": regions, "markets": markets, "oddsFormat": "decimal"},
        )
        if use_cache:
            _EVENTS_CACHE[sport] = (now, events)
        return events

    def find_match_odds(
        self,
        home_team: str,
        away_team: str,
        sport: str = DEFAULT_SPORT,
        events: list[dict] | None = None,
    ) -> OddsFeatures | None:
        """查找指定对阵的赔率特征（支持国家队名称别名）。"""
        try:
            if events is None:
                events = self.get_upcoming_odds(sport)
        except requests.HTTPError:
            return None

        for event in events:
            event_home = event.get("home_team", "")
            event_away = event.get("away_team", "")
            if teams_match(home_team, event_home) and teams_match(away_team, event_away):
                return average_odds_from_bookmakers(event.get("bookmakers", []))
        return None

    @staticmethod
    def clear_cache() -> None:
        _EVENTS_CACHE.clear()
