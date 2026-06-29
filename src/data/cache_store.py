"""进程内缓存，避免重复读盘与解析。"""

import csv
import json
import time
from pathlib import Path

_CACHE: dict[str, tuple[float, object]] = {}
_DEFAULT_TTL = 300  # 5 分钟


def count_csv_rows(path: Path) -> int:
    try:
        return max(0, sum(1 for _ in open(path, encoding="utf-8")) - 1)
    except OSError:
        return 0


def _cell(row: dict, key: str, default: str = "") -> str:
    val = row.get(key, default)
    return default if val in (None, "") else str(val)


def read_csv_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            item = {
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "home_goals": int(row["home_goals"]),
                "away_goals": int(row["away_goals"]),
                "date": _cell(row, "date"),
            }
            if row.get("stage"):
                item["stage"] = row["stage"]
            if row.get("group"):
                item["group"] = row["group"]
            rows.append(item)
    return rows


def write_csv_rows(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


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
    return read_csv_rows(path)


def invalidate(prefix: str = "") -> None:
    if not prefix:
        _CACHE.clear()
        return
    for k in list(_CACHE):
        if k.startswith(prefix):
            del _CACHE[k]
