"""进程内缓存，避免重复读盘与解析。"""

import json
import time
from pathlib import Path

import pandas as pd

_CACHE: dict[str, tuple[float, object]] = {}
_DEFAULT_TTL = 300  # 5 分钟


def count_csv_rows(path: Path) -> int:
    try:
        return max(0, sum(1 for _ in open(path, encoding="utf-8")) - 1)
    except OSError:
        return 0


def _key(name: str, path: Path | None = None) -> str:
    if path is None:
        return name
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0
    return f"{name}:{path}:{mtime}"


def get_or_load(name: str, loader, path: Path | None = None, ttl: float = _DEFAULT_TTL):
    key = _key(name, path)
    now = time.monotonic()
    if key in _CACHE:
        ts, val = _CACHE[key]
        if now - ts < ttl:
            return val
    val = loader()
    _CACHE[key] = (now, val)
    return val


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict]:
    df = pd.read_csv(path)
    rows = []
    for _, r in df.iterrows():
        row = {
            "home_team": r["home_team"],
            "away_team": r["away_team"],
            "home_goals": int(r["home_goals"]),
            "away_goals": int(r["away_goals"]),
            "date": str(r.get("date", "")) if pd.notna(r.get("date")) else "",
        }
        if "stage" in r and pd.notna(r.get("stage")):
            row["stage"] = r["stage"]
        rows.append(row)
    return rows


def invalidate(prefix: str = "") -> None:
    if not prefix:
        _CACHE.clear()
        return
    for k in list(_CACHE):
        if k.startswith(prefix):
            del _CACHE[k]
