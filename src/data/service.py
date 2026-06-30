from src.data.cache_store import count_csv_rows, get_or_load, invalidate, load_csv_rows, load_json
from src.config import CACHE_DIR, COMPETITION_MAP, DATA_DIR, DEFAULT_COMPETITION, FOOTBALL_DATA_API_KEY, INTERNATIONAL_COMPETITIONS
from src.data.odds_api import OddsAPIClient
from src.data.wc2026_loader import (
    get_wc2026_full_history,
    get_wc2026_group_tables,
    get_wc2026_standings,
    get_wc2026_teams,
    get_wc2026_upcoming_matches,
    load_wc2026_schedule,
    refresh_wc2026_cache,
)
from src.features.builder import MatchContext
from src.features.history_index import (
    index_away_matches,
    index_history_by_team,
    index_home_matches,
)
from src.features.odds_features import OddsFeatures
from src.model.predict import get_predictor


def _football_data():
    from src.data import football_data
    return football_data


class DataService:
    """统一数据服务：缓存读取 + 实时 API + 2026 世界杯赛程。"""

    def __init__(self, competition: str = DEFAULT_COMPETITION):
        self.competition = competition
        info = COMPETITION_MAP.get(competition, {})
        self.odds_sport = info.get("odds_sport", "soccer_epl")
        self.total_teams = info.get("teams", 32 if competition == "WC" else 20)
        self.is_international = competition in INTERNATIONAL_COMPETITIONS

    def get_competitions(self) -> list[dict]:
        return [
            {
                "code": code,
                "name": info["name"],
                "odds_sport": info["odds_sport"],
                "type": info.get("type", "club"),
                "icon": info.get("icon", "⚽"),
            }
            for code, info in COMPETITION_MAP.items()
        ]

    def sync(self) -> dict:
        if self.competition == "WC":
            from src.config import FOOTBALL_DATA_API_KEY
            if FOOTBALL_DATA_API_KEY:
                try:
                    fd = _football_data()
                    api_meta = fd.sync_competition_data(self.competition)
                    refresh_wc2026_cache()
                    return {**api_meta, "source": "api+wc2026"}
                except Exception:
                    pass
            return refresh_wc2026_cache()
        return _football_data().sync_competition_data(self.competition)

    def refresh_schedule(self) -> dict:
        """更新本地赛程（世界杯专用）。"""
        if self.competition == "WC":
            invalidate("wc")
            invalidate("history")
            return refresh_wc2026_cache()
        raise ValueError("refresh_schedule 目前仅支持世界杯 (WC)")

    def get_bootstrap(self) -> dict:
        """一次返回页面所需全部数据，减少 HTTP 往返。"""
        status = self.get_sync_status()
        info = COMPETITION_MAP.get(self.competition, {})
        payload = {
            "status": {
                **status,
                "competition": self.competition,
                "competition_type": info.get("type", "club"),
                "history_matches": status.get("history_matches")
                or status.get("finished_matches")
                or 0,
                "has_api_key": bool(FOOTBALL_DATA_API_KEY),
            },
            "teams": self.get_teams(),
            "upcoming": self.get_upcoming(),
            "competition": self.competition,
            "type": info.get("type", "club"),
        }
        if self.competition == "WC":
            payload["groups"] = self.get_groups()
        return payload

    def get_teams(self) -> list[dict]:
        if self.competition == "WC":
            cache_path = CACHE_DIR / "WC_teams.json"
            if cache_path.exists():
                return get_or_load("wc:teams", lambda: load_json(cache_path), cache_path)
            return get_wc2026_teams()
        fd = _football_data()
        teams = fd.load_cached_teams(self.competition)
        if teams:
            return teams
        try:
            client = fd.FootballDataClient()
            return client.get_teams(self.competition)
        except ValueError:
            return []

    def get_upcoming(self) -> list[dict]:
        if self.competition == "WC":
            cache_path = CACHE_DIR / "WC_upcoming.json"
            if cache_path.exists():
                return get_or_load("wc:upcoming", lambda: load_json(cache_path), cache_path)
            return get_wc2026_upcoming_matches()
        fd = _football_data()
        upcoming = fd.load_cached_upcoming(self.competition)
        if upcoming:
            return upcoming
        try:
            client = fd.FootballDataClient()
            return client.get_upcoming_matches(self.competition)
        except ValueError:
            return []

    def get_groups(self) -> dict[str, list[dict]]:
        if self.competition == "WC":
            return get_wc2026_group_tables()
        fd = _football_data()
        groups = fd.load_group_standings(self.competition)
        return {k: v for k, v in groups.items() if k != "TOTAL"}

    def get_sync_status(self) -> dict:
        meta_path = CACHE_DIR / f"{self.competition}_meta.json"
        if meta_path.exists():
            meta = get_or_load(
                f"meta:{self.competition}",
                lambda: load_json(meta_path),
                meta_path,
            )
            csv_path = CACHE_DIR / f"{self.competition}_matches.csv"
            if csv_path.exists():
                meta = {**meta, "history_matches": count_csv_rows(csv_path)}
            return meta
        if self.competition == "WC":
            schedule = get_or_load(
                "wc2026:schedule",
                load_wc2026_schedule,
                DATA_DIR / "wc2026_schedule.json",
            )
            if schedule:
                return {
                    "synced": False,
                    "message": "2026 世界杯 · 32强阶段",
                    "competition_name": "世界杯 2026",
                    "updated_at": schedule.get("updated_at"),
                    "finished_matches": count_csv_rows(DATA_DIR / "wc2026_results.csv"),
                    "upcoming_matches": len(get_wc2026_upcoming_matches()),
                    "history_matches": 201,
                    "stage": schedule.get("note", ""),
                }
        return {"synced": False, "message": "尚未同步数据，请点击「更新赛程」", "history_matches": 0}

    def get_history(self) -> list[dict]:
        if self.competition == "WC":
            csv_path = CACHE_DIR / "WC_matches.csv"
            if csv_path.exists():
                return get_or_load(
                    "history:WC",
                    lambda: load_csv_rows(csv_path),
                    csv_path,
                )
            return get_or_load(
                "history:WC:full",
                get_wc2026_full_history,
            )

        cached_path = CACHE_DIR / f"{self.competition}_matches.json"
        if cached_path.exists():
            return get_or_load(
                f"history:{self.competition}:json",
                lambda: load_json(cached_path),
                cached_path,
            )

        csv_path = CACHE_DIR / f"{self.competition}_matches.csv"
        if csv_path.exists():
            return get_or_load(
                f"history:{self.competition}",
                lambda: load_csv_rows(csv_path),
                csv_path,
            )

        sample = DATA_DIR / "sample_matches.csv"
        if sample.exists() and self.competition != "WC":
            return get_or_load(
                f"history:sample",
                lambda: load_csv_rows(sample),
                sample,
            )
        return []

    def __init__(self, competition: str = DEFAULT_COMPETITION):
        self.competition = competition
        info = COMPETITION_MAP.get(competition, {})
        self.odds_sport = info.get("odds_sport", "soccer_epl")
        self.total_teams = info.get("teams", 32 if competition == "WC" else 20)
        self.is_international = competition in INTERNATIONAL_COMPETITIONS
        self._odds_client: OddsAPIClient | None = None

    def _get_odds_client(self) -> OddsAPIClient | None:
        try:
            if self._odds_client is None:
                self._odds_client = OddsAPIClient()
            return self._odds_client
        except ValueError:
            return None

    def prefetch_odds_events(self) -> list[dict] | None:
        """一次性拉取当前联赛全部待赛赔率（带缓存）。"""
        client = self._get_odds_client()
        if not client:
            return None
        try:
            return client.get_upcoming_odds(self.odds_sport)
        except Exception:
            return None

    def fetch_odds(
        self,
        home_team: str,
        away_team: str,
        events: list[dict] | None = None,
        client: OddsAPIClient | None = None,
    ) -> OddsFeatures | None:
        try:
            c = client or self._get_odds_client()
            if not c:
                return None
            return c.find_match_odds(
                home_team, away_team, self.odds_sport, events=events
            )
        except Exception:
            return None

    def _standings_map(self) -> dict:
        if self.competition == "WC":
            return get_wc2026_standings()
        return _football_data().load_cached_standings(self.competition)

    def predict(
        self,
        home_team: str,
        away_team: str,
        fetch_odds: bool = True,
        match_date: str | None = None,
        stage: str | None = None,
        odds_events: list[dict] | None = None,
        *,
        history: list[dict] | None = None,
        standings: dict | None = None,
        predictor=None,
        team_index: dict | None = None,
        home_index: dict | None = None,
        away_index: dict | None = None,
        odds_client: OddsAPIClient | None = None,
    ) -> dict:
        history = history if history is not None else self.get_history()
        standings = standings if standings is not None else self._standings_map()

        context = MatchContext(
            standings=standings,
            total_teams=self.total_teams,
            match_date=match_date,
            stage=stage,
            is_international=self.is_international,
            group_size=4,
            team_index=team_index,
            home_index=home_index,
            away_index=away_index,
        )

        odds = None
        if fetch_odds:
            odds = self.fetch_odds(
                home_team, away_team, odds_events, client=odds_client
            )

        if predictor is None:
            predictor = get_predictor()
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
            result["raw_odds"] = {
                "home": round(odds.home_odds, 2),
                "draw": round(odds.draw_odds, 2),
                "away": round(odds.away_odds, 2),
            }
        else:
            result["odds_source"] = "default"

        home_st = standings.get(home_team)
        away_st = standings.get(away_team)
        if home_st and away_st:
            result["standings"] = {
                "home": {
                    "position": home_st.position,
                    "points": home_st.points,
                    "group": home_st.group,
                },
                "away": {
                    "position": away_st.position,
                    "points": away_st.points,
                    "group": away_st.group,
                },
            }

        comp_info = COMPETITION_MAP.get(self.competition, {})
        result["competition"] = self.competition
        result["competition_name"] = comp_info.get("name", self.competition)
        result["is_international"] = self.is_international
        result["model"] = "World Cup Predictor"
        return result

    def get_analysis(
        self,
        home_team: str,
        away_team: str,
        fetch_odds: bool = False,
        match_date: str | None = None,
        stage: str | None = None,
        lang: str = "zh",
    ) -> dict:
        """专业分析页：预测 + 交手 + 状态对比。"""
        from src.features.form import compute_form
        from src.features.h2h import compute_h2h

        result = self.predict(home_team, away_team, fetch_odds, match_date, stage)
        history = self.get_history()
        h2h = compute_h2h(history, home_team, away_team, window=10)
        home_form = compute_form(history, home_team, 5)
        away_form = compute_form(history, away_team, 5)

        meetings = [
            m for m in history
            if {m["home_team"], m["away_team"]} == {home_team, away_team}
        ][-5:]

        recent_meetings = []
        for m in reversed(meetings):
            is_home = m["home_team"] == home_team
            hg = m["home_goals"]
            ag = m["away_goals"]
            if not is_home:
                hg, ag = ag, hg
            if hg > ag:
                outcome_key = "home_win"
            elif hg == ag:
                outcome_key = "draw"
            else:
                outcome_key = "away_win"
            recent_meetings.append({
                "date": m.get("date", "")[:10],
                "score": f"{m['home_goals']}-{m['away_goals']}",
                "outcome_key": outcome_key,
                "stage": m.get("stage", ""),
            })

        model_p = result["probabilities"]
        market_p = result.get("market_implied")
        edge = None
        if market_p:
            edge = {
                "home_win": round(model_p["home_win"] - market_p["home_win"], 4),
                "draw": round(model_p["draw"] - market_p["draw"], 4),
                "away_win": round(model_p["away_win"] - market_p["away_win"], 4),
            }

        standings = get_wc2026_standings()
        home_st = standings.get(home_team)
        away_st = standings.get(away_team)

        return {
            **result,
            "stage": stage,
            "h2h": {
                "total": h2h.total_matches,
                "home_wins": int(h2h.home_wins),
                "draws": int(h2h.draws),
                "away_wins": int(h2h.away_wins),
                "home_goals_avg": round(h2h.home_goals_avg, 2),
                "away_goals_avg": round(h2h.away_goals_avg, 2),
            },
            "form": {
                "home": {
                    "ppg": round(home_form.points_per_game, 2),
                    "scored": round(home_form.goals_scored_avg, 2),
                    "conceded": round(home_form.goals_conceded_avg, 2),
                    "win_rate": round(home_form.win_rate, 2),
                },
                "away": {
                    "ppg": round(away_form.points_per_game, 2),
                    "scored": round(away_form.goals_scored_avg, 2),
                    "conceded": round(away_form.goals_conceded_avg, 2),
                    "win_rate": round(away_form.win_rate, 2),
                },
            },
            "team_profiles": {
                "home": _team_profile(home_team, home_st),
                "away": _team_profile(away_team, away_st),
            },
            "recent_meetings": recent_meetings,
            "model_vs_market": edge,
            "insights": _build_insights(result, h2h, home_form, away_form, edge, lang),
        }

    def get_bankroll_plan(
        self,
        bankroll: float,
        risk: str = "moderate",
        fetch_odds: bool = False,
        lang: str = "zh",
    ) -> dict:
        """待赛场次预算分配方案（Kelly + 模型边际）。"""
        from src.model.bankroll import RISK_PROFILES, build_bankroll_plan

        upcoming = [
            m for m in self.get_upcoming()
            if m.get("home_team") and m["home_team"] != "TBD"
            and m.get("away_team") and m["away_team"] != "TBD"
        ]
        odds_events = self.prefetch_odds_events() if fetch_odds else None
        odds_client = self._get_odds_client() if fetch_odds else None
        history = self.get_history()
        standings = self._standings_map()
        predictor = get_predictor()
        team_index = index_history_by_team(history)
        home_index = index_home_matches(history)
        away_index = index_away_matches(history)

        analyses = []
        for m in upcoming:
            analyses.append(
                self.predict(
                    m["home_team"],
                    m["away_team"],
                    fetch_odds=fetch_odds,
                    match_date=m.get("date"),
                    stage=m.get("stage"),
                    odds_events=odds_events,
                    history=history,
                    standings=standings,
                    predictor=predictor,
                    team_index=team_index,
                    home_index=home_index,
                    away_index=away_index,
                    odds_client=odds_client,
                )
            )

        plan = build_bankroll_plan(upcoming, analyses, bankroll, risk)
        labels = _OUTCOME_LABELS.get(lang, _OUTCOME_LABELS["zh"])
        for rec in plan["recommendations"]:
            rec["pick_label"] = labels.get(rec["pick"], rec["pick"])

        matched = sum(1 for r in plan["recommendations"] if r.get("has_market_odds"))
        total_rec = len(plan["recommendations"])

        plan["disclaimer"] = (
            "仅供学习研究，不构成投资建议。请理性管理资金，切勿超出承受能力。"
            if lang == "zh"
            else "For research only. Not financial advice. Never risk more than you can afford to lose."
        )
        plan["risk_profiles"] = {
            k: {"name": k, **v} for k, v in RISK_PROFILES.items()
        }
        if fetch_odds and odds_events is None:
            plan["odds_mode"] = "unavailable"
            plan["odds_hint"] = (
                "无法连接赔率 API，请检查 ODDS_API_KEY 配置"
                if lang == "zh"
                else "Odds API unavailable — check ODDS_API_KEY"
            )
        elif fetch_odds and matched > 0:
            plan["odds_mode"] = "market"
            plan["odds_matched"] = matched
            plan["odds_hint"] = (
                f"已匹配 {matched}/{total_rec} 场实时市场赔率"
                if lang == "zh"
                else f"Live odds matched for {matched}/{total_rec} fixtures"
            )
        elif fetch_odds:
            plan["odds_mode"] = "estimate"
            plan["odds_hint"] = (
                "已请求赔率但未匹配到对阵，使用估算赔率"
                if lang == "zh"
                else "Odds requested but no fixture match — using estimates"
            )
        else:
            plan["odds_mode"] = "model_estimate"
            plan["odds_hint"] = (
                "未拉取市场赔率，使用基准估算"
                if lang == "zh"
                else "Market odds not fetched — using baseline estimates"
            )
        return plan


def _team_profile(name: str, standing) -> dict:
    if not standing:
        return {"name": name}
    return {
        "name": name,
        "group": standing.group,
        "position": standing.position,
        "points": standing.points,
        "goal_difference": standing.goal_difference,
    }


_OUTCOME_LABELS = {
    "zh": {"home_win": "主胜", "draw": "平局", "away_win": "客胜"},
    "en": {"home_win": "home win", "draw": "draw", "away_win": "away win"},
}


def _build_insights(result, h2h, home_form, away_form, edge, lang: str = "zh") -> list[str]:
    insights = []
    p = result["probabilities"]
    fav = max(p, key=p.get)
    fav_name = {
        "home_win": result["home_team"],
        "draw": _OUTCOME_LABELS.get(lang, _OUTCOME_LABELS["zh"])["draw"],
        "away_win": result["away_team"],
    }[fav]

    if lang == "en":
        insights.append(f"Model favors {fav_name} ({p[fav]*100:.1f}%)")
        if h2h.total_matches >= 3:
            if h2h.home_win_rate > 0.5:
                insights.append(f"{result['home_team']} leads H2H ({h2h.total_matches} matches)")
            elif h2h.away_win_rate > 0.5:
                insights.append(f"{result['away_team']} leads H2H ({h2h.total_matches} matches)")
        diff = home_form.points_per_game - away_form.points_per_game
        if abs(diff) >= 0.8:
            better = result["home_team"] if diff > 0 else result["away_team"]
            insights.append(f"{better} in better form (PPG diff {abs(diff):.1f})")
        if edge:
            max_edge_key = max(edge, key=lambda k: abs(edge[k]))
            if abs(edge[max_edge_key]) >= 0.05:
                oc = _OUTCOME_LABELS["en"][max_edge_key]
                direction = "above" if edge[max_edge_key] > 0 else "below"
                insights.append(
                    f"Model {oc} prob. {abs(edge[max_edge_key])*100:.1f}pp {direction} market"
                )
    else:
        insights.append(f"模型最看好：{fav_name}（{p[fav]*100:.1f}%）")
        if h2h.total_matches >= 3:
            if h2h.home_win_rate > 0.5:
                insights.append(f"历史交手中 {result['home_team']} 占优（{h2h.total_matches} 场）")
            elif h2h.away_win_rate > 0.5:
                insights.append(f"历史交手中 {result['away_team']} 占优（{h2h.total_matches} 场）")
        diff = home_form.points_per_game - away_form.points_per_game
        if abs(diff) >= 0.8:
            better = result["home_team"] if diff > 0 else result["away_team"]
            insights.append(f"近期状态 {better} 更出色（PPG 差 {abs(diff):.1f}）")
        if edge:
            max_edge_key = max(edge, key=lambda k: abs(edge[k]))
            if abs(edge[max_edge_key]) >= 0.05:
                labels = _OUTCOME_LABELS["zh"]
                direction = "高于" if edge[max_edge_key] > 0 else "低于"
                insights.append(
                    f"模型认为{labels[max_edge_key]}概率{direction}市场 "
                    f"{abs(edge[max_edge_key])*100:.1f} 个百分点"
                )

    return insights[:4]
