#!/usr/bin/env python3
"""从 football-data.org 同步比赛数据到本地缓存。"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import COMPETITION_MAP, DEFAULT_COMPETITION
from src.data.football_data import sync_competition_data


def main():
    parser = argparse.ArgumentParser(description="同步足球比赛数据")
    parser.add_argument(
        "--competition",
        default=DEFAULT_COMPETITION,
        choices=list(COMPETITION_MAP.keys()),
        help="赛事代码（WC=世界杯, PL=英超 ...）",
    )
    args = parser.parse_args()

    print(f"正在同步 {COMPETITION_MAP[args.competition]['name']} ({args.competition})...")
    try:
        meta = sync_competition_data(args.competition)
        print(f"\n同步完成!")
        print(f"  已完成比赛: {meta['finished_matches']}")
        print(f"  即将开赛:   {meta['upcoming_matches']}")
        print(f"  球队数量:   {meta['teams']}")
        print(f"  缓存目录:   data/cache/")
    except ValueError as e:
        print(f"\n错误: {e}")
        print("\n请按以下步骤配置 API Key:")
        print("  1. 访问 https://www.football-data.org/client/register 注册")
        print("  2. 复制 API Token 到 .env 文件的 FOOTBALL_DATA_API_KEY")
        sys.exit(1)
    except Exception as e:
        print(f"\n同步失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
