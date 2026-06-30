"""历史赛果索引，避免批量预测时重复扫描全量列表。"""

from collections import defaultdict


def index_history_by_team(history: list[dict]) -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = defaultdict(list)
    for m in history:
        idx[m["home_team"]].append(m)
        idx[m["away_team"]].append(m)
    return dict(idx)


def index_home_matches(history: list[dict]) -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = defaultdict(list)
    for m in history:
        idx[m["home_team"]].append(m)
    return dict(idx)


def index_away_matches(history: list[dict]) -> dict[str, list[dict]]:
    idx: dict[str, list[dict]] = defaultdict(list)
    for m in history:
        idx[m["away_team"]].append(m)
    return dict(idx)
