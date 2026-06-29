#!/usr/bin/env python3
"""更新 2026 世界杯赛程到本地缓存。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.wc2026_loader import refresh_wc2026_cache


def main():
    print("正在更新 2026 世界杯赛程...")
    meta = refresh_wc2026_cache()
    print(f"\n更新完成 ({meta.get('source', 'wc2026_schedule')})")
    print(f"  赛事阶段:   {meta.get('stage', 'Round of 32')}")
    print(f"  2026 已赛:  {meta['finished_matches']} 场")
    print(f"  待赛:       {meta['upcoming_matches']} 场")
    print(f"  参赛队:     {meta['teams']} 支")
    print(f"  更新时间:   {meta['synced_at']}")
    print(f"  缓存目录:   data/cache/")


if __name__ == "__main__":
    main()
