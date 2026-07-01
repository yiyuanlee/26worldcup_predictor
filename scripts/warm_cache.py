"""部署前预热 WC 历史缓存，写入 data/cache/ 随函数包部署。"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 构建阶段强制写入持久目录（勿用 /tmp/wc_cache）
os.environ.pop("VERCEL", None)

from src.config import CACHE_DIR
from src.data.wc2026_loader import refresh_wc2026_cache

if __name__ == "__main__":
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    meta = refresh_wc2026_cache()
    print("cache ready:", meta.get("upcoming_matches"), "upcoming at", CACHE_DIR)
