from src.config import MODEL_DIR, WC_MODEL_FILENAME
from src.features.builder import FEATURE_COLUMNS, build_feature_vector, features_to_row
from src.features.odds_features import OddsFeatures
from src.features.world_cup import is_knockout_stage
from src.model.knockout_calibrate import calibrate_knockout_probs

DEFAULT_MODEL_PATH = MODEL_DIR / WC_MODEL_FILENAME
OUTCOME_LABELS = {0: "主胜", 1: "平局", 2: "客胜"}
OUTCOME_KEYS = {0: "home_win", 1: "draw", 2: "away_win"}

_predictor_instance: "MatchPredictor | None" = None
_predictor_path: str | None = None


def get_predictor(model_path=DEFAULT_MODEL_PATH) -> "MatchPredictor":
    """单例加载模型，避免每次预测重复读盘。"""
    global _predictor_instance, _predictor_path
    path_str = str(model_path)
    if _predictor_instance is None or _predictor_path != path_str:
        _predictor_instance = MatchPredictor(model_path)
        _predictor_path = path_str
    return _predictor_instance


class MatchPredictor:
    """加载训练好的模型，预测比赛胜率。"""

    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        import joblib
        from pathlib import Path

        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"模型文件不存在: {path}\n请先运行: python scripts/train_model.py"
            )
        saved = joblib.load(path)
        self.model = saved["model"]
        self.feature_columns = saved.get("features", FEATURE_COLUMNS)

    def predict(
        self,
        history: list[dict],
        home_team: str,
        away_team: str,
        odds: OddsFeatures | None = None,
        context=None,
    ) -> dict:
        import numpy as np
        from src.features.builder import MatchContext

        if context is None:
            context = MatchContext()

        features = build_feature_vector(
            history, home_team, away_team, odds=odds, context=context
        )
        X = np.array([features_to_row(features, self.feature_columns)])

        proba = self.model.predict_proba(X)[0]
        probs = calibrate_knockout_probs(
            {
                "home_win": float(proba[0]),
                "draw": float(proba[1]),
                "away_win": float(proba[2]),
            },
            features,
            context.stage,
        )
        predicted_key = max(probs, key=probs.get)
        # 淘汰赛：平局概率接近胜负时，90 分钟更倾向判平
        if is_knockout_stage(context.stage):
            h, d, a = probs["home_win"], probs["draw"], probs["away_win"]
            if d >= max(h, a) - 0.06 and d >= 0.30:
                predicted_key = "draw"
        key_to_idx = {"home_win": 0, "draw": 1, "away_win": 2}
        predicted = key_to_idx[predicted_key]

        return {
            "home_team": home_team,
            "away_team": away_team,
            "probabilities": probs,
            "predicted_outcome": OUTCOME_LABELS[predicted],
            "predicted_key": predicted_key,
            "features": {k: round(v, 4) for k, v in features.items()},
        }
