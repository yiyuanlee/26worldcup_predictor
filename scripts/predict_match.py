#!/usr/bin/env python3
"""预测指定对阵的胜率。"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline import predict_match


def load_history(csv_path: str) -> list[dict]:
    df = pd.read_csv(csv_path)
    return [
        {
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "home_goals": int(row["home_goals"]),
            "away_goals": int(row["away_goals"]),
        }
        for _, row in df.iterrows()
    ]


def main():
    parser = argparse.ArgumentParser(description="预测足球比赛胜率")
    parser.add_argument("home_team", help="主队名称")
    parser.add_argument("away_team", help="客队名称")
    parser.add_argument(
        "--data",
        default=str(PROJECT_ROOT / "data" / "sample_matches.csv"),
        help="历史比赛数据 CSV",
    )
    parser.add_argument(
        "--fetch-odds",
        action="store_true",
        help="从 The Odds API 拉取实时赔率",
    )
    parser.add_argument(
        "--sport",
        default=None,
        help="The Odds API sport key，如 soccer_epl",
    )
    args = parser.parse_args()

    history = load_history(args.data)
    result = predict_match(
        history,
        args.home_team,
        args.away_team,
        fetch_odds=args.fetch_odds,
        sport=args.sport,
    )

    print("\n=== 比赛预测 ===")
    print(f"{result['home_team']} vs {result['away_team']}")
    print(f"\n预测结果: {result['predicted_outcome']}")
    print("\n模型胜率:")
    for label, key in [("主胜", "home_win"), ("平局", "draw"), ("客胜", "away_win")]:
        pct = result["probabilities"][key] * 100
        print(f"  {label}: {pct:.1f}%")

    if "market_implied" in result:
        print("\n市场隐含概率 (赔率):")
        for label, key in [("主胜", "home_win"), ("平局", "draw"), ("客胜", "away_win")]:
            pct = result["market_implied"][key] * 100
            print(f"  {label}: {pct:.1f}%")

    print(f"\n赔率来源: {result['odds_source']}")


if __name__ == "__main__":
    main()
