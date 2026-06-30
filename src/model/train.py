from src.features.builder import FEATURE_COLUMNS, build_feature_vector, features_to_row
from src.features.odds_features import odds_to_implied


def prepare_training_data(df):
    """
    从历史比赛 DataFrame 构建训练集。

    必需列: home_team, away_team, home_goals, away_goals
    可选列: odds_home, odds_draw, odds_away, date,
            home_position, away_position, home_points, away_points
    """
    import numpy as np
    import pandas as pd
    from src.features.builder import MatchContext
    from src.features.standings import TeamStanding

    history: list[dict] = []
    rows: list[list[float]] = []
    labels: list[int] = []

    has_standings = all(
        c in df.columns for c in ("home_position", "away_position", "home_points", "away_points")
    )
    is_wc_data = "stage" in df.columns

    for _, row in df.iterrows():
        match = {
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "home_goals": int(row["home_goals"]),
            "away_goals": int(row["away_goals"]),
            "date": row.get("date", ""),
        }
        if is_wc_data and pd.notna(row.get("stage")):
            match["stage"] = row["stage"]

        odds = None
        if all(col in row and pd.notna(row[col]) for col in ("odds_home", "odds_draw", "odds_away")):
            odds = odds_to_implied(row["odds_home"], row["odds_draw"], row["odds_away"])

        context = MatchContext(
            match_date=str(row.get("date", "")) if pd.notna(row.get("date")) else None,
            stage=str(row.get("stage", "")) if is_wc_data and pd.notna(row.get("stage")) else None,
            is_international=is_wc_data,
            group_size=4,
        )
        if has_standings and pd.notna(row.get("home_position")):
            context.standings = {
                row["home_team"]: TeamStanding(
                    position=int(row["home_position"]),
                    points=int(row["home_points"]),
                    goal_difference=int(row.get("home_gd", 0) or 0),
                    played=int(row.get("home_played", 1) or 1),
                    won=0, draw=0, lost=0,
                    goals_for=0, goals_against=0,
                ),
                row["away_team"]: TeamStanding(
                    position=int(row["away_position"]),
                    points=int(row["away_points"]),
                    goal_difference=int(row.get("away_gd", 0) or 0),
                    played=int(row.get("away_played", 1) or 1),
                    won=0, draw=0, lost=0,
                    goals_for=0, goals_against=0,
                ),
            }

        features = build_feature_vector(
            history, row["home_team"], row["away_team"], odds=odds, context=context
        )
        rows.append(features_to_row(features))
        labels.append(_encode_outcome(match["home_goals"], match["away_goals"]))
        history.append(match)

    return np.array(rows), np.array(labels)


def _encode_outcome(home_goals: int, away_goals: int) -> int:
    if home_goals > away_goals:
        return 0
    if home_goals == away_goals:
        return 1
    return 2


def train_model(df, model_path=None, test_size=0.2, random_state=42):
    """训练三分类模型并保存。"""
    from pathlib import Path

    import joblib
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import accuracy_score, classification_report, log_loss
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    from src.config import MODEL_DIR

    if model_path is None:
        from src.config import WC_MODEL_FILENAME
        model_path = MODEL_DIR / WC_MODEL_FILENAME

    X, y = prepare_training_data(df)
    sample_weights = _build_sample_weights(df)

    X_train, X_test, y_train, y_test, w_train, _ = train_test_split(
        X, y, sample_weights, test_size=test_size, random_state=random_state, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            random_state=random_state,
        )),
    ])

    calibrated = CalibratedClassifierCV(pipeline, cv=3, method="isotonic")
    calibrated.fit(X_train, y_train, sample_weight=w_train)

    y_pred = calibrated.predict(X_test)
    y_proba = calibrated.predict_proba(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "log_loss": log_loss(y_test, y_proba),
        "report": classification_report(
            y_test, y_pred, target_names=["主胜", "平局", "客胜"]
        ),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_count": len(FEATURE_COLUMNS),
    }

    joblib.dump({"model": calibrated, "features": FEATURE_COLUMNS}, model_path)
    return metrics


def _build_sample_weights(df) -> "np.ndarray":
    """近期赛果与淘汰赛样本加权，提升对当前阶段的拟合。"""
    import numpy as np

    from src.features.world_cup import is_knockout_stage

    weights = np.ones(len(df), dtype=float)
    if "date" in df.columns:
        dates = df["date"].astype(str)
        weights[dates.str.startswith("2026")] *= 2.5
    if "stage" in df.columns:
        ko = df["stage"].apply(lambda s: is_knockout_stage(str(s) if s == s else None))
        weights[ko] *= 1.8
        # 淘汰赛平局样本额外加权
        is_draw = df["home_goals"] == df["away_goals"]
        weights[ko & is_draw] *= 1.5
    return weights
