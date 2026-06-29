"""合并世界杯训练数据（2018+2022+2026）。"""

from pathlib import Path

import pandas as pd

from src.config import DATA_DIR


def build_wc_training_csv(output: Path | None = None) -> pd.DataFrame:
    paths = [
        DATA_DIR / "world_cup_matches.csv",
        DATA_DIR / "wc2026_results.csv",
    ]
    frames = []
    for p in paths:
        if p.exists():
            frames.append(pd.read_csv(p))
    if not frames:
        raise FileNotFoundError("未找到世界杯训练数据")
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates(
        subset=["date", "home_team", "away_team"], keep="last"
    ).sort_values("date")
    if output:
        df.to_csv(output, index=False)
    return df
