import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.data.service import DataService
from src.model.predict import get_predictor

app = FastAPI(title="World Cup Predictor", version="2.0.0")
WC = "WC"


@app.on_event("startup")
def warmup():
    try:
        get_predictor()
        svc = DataService(WC)
        svc.get_history()
    except Exception:
        pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    home_team: str
    away_team: str
    fetch_odds: bool = False
    match_date: str | None = None
    stage: str | None = None


@app.get("/api/home")
async def home_data():
    """首页数据：赛程 + 小组排名 + 状态。"""
    svc = DataService(WC)
    status = svc.get_sync_status()
    return {
        "status": status,
        "upcoming": svc.get_upcoming(),
        "groups": svc.get_groups(),
        "teams": svc.get_teams(),
        "model": "World Cup Predictor",
    }


ERR_SAME_TEAM = {"zh": "主客队不能相同", "en": "Home and away teams must differ"}


@app.get("/api/analysis")
async def analysis(
    home: str = Query(...),
    away: str = Query(...),
    fetch_odds: bool = False,
    stage: str | None = None,
    date: str | None = None,
    lang: str = Query("zh", pattern="^(zh|en)$"),
):
    if home == away:
        raise HTTPException(status_code=400, detail=ERR_SAME_TEAM.get(lang, ERR_SAME_TEAM["zh"]))
    try:
        svc = DataService(WC)
        return svc.get_analysis(home, away, fetch_odds, date, stage, lang)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/odds/status")
async def odds_status():
    """诊断 The Odds API 是否可用。"""
    svc = DataService(WC)
    return svc.get_odds_status()


@app.get("/api/bankroll/plan")
async def bankroll_plan(
    bankroll: float = Query(1000, ge=10, le=10_000_000),
    risk: str = Query("moderate", pattern="^(conservative|moderate|aggressive)$"),
    fetch_odds: bool = False,
    lang: str = Query("zh", pattern="^(zh|en)$"),
):
    try:
        svc = DataService(WC)
        return svc.get_bankroll_plan(bankroll, risk, fetch_odds, lang)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh-schedule")
async def refresh_schedule():
    try:
        svc = DataService(WC)
        result = svc.refresh_schedule()
        ok = result.get("synced", True) or result.get("source") != "wc2026_schedule"
        return {"success": ok, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 本地开发：static/；Vercel：public/ 静态资源
if os.getenv("VERCEL"):
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles

    from src.config import STATIC_DIR

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def home():
        return (STATIC_DIR / "index.html").read_text(encoding="utf-8")

    @app.get("/analysis", response_class=HTMLResponse)
    async def analysis_page():
        return (STATIC_DIR / "analysis.html").read_text(encoding="utf-8")

    @app.get("/bankroll", response_class=HTMLResponse)
    async def bankroll_page():
        return (STATIC_DIR / "bankroll.html").read_text(encoding="utf-8")
else:
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles

    from src.config import STATIC_DIR

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    async def home():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/analysis")
    async def analysis_page():
        return FileResponse(STATIC_DIR / "analysis.html")

    @app.get("/bankroll")
    async def bankroll_page():
        return FileResponse(STATIC_DIR / "bankroll.html")
