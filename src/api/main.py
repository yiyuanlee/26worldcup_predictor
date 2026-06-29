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
    return {
        "status": svc.get_sync_status(),
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


@app.post("/api/refresh-schedule")
async def refresh_schedule():
    try:
        svc = DataService(WC)
        result = svc.refresh_schedule()
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 本地开发：FastAPI 直接提供静态页面；Vercel 使用 public/ 目录
if not os.getenv("VERCEL"):
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
