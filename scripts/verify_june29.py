#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.service import DataService
from src.model import predict as pred_mod

pred_mod._predictor_instance = None

svc = DataService("WC")
cases = [
    ("Germany", "Paraguay", "draw"),
    ("Netherlands", "Morocco", "draw"),
    ("Brazil", "Japan", "home_win"),
]
for home, away, actual in cases:
    r = svc.predict(home, away, False, "2026-06-29T16:00:00Z", "round32")
    p = r["probabilities"]
    ok = "OK" if r["predicted_key"] == actual else "MISS"
    print(
        f"{home} vs {away}: {r['predicted_key']} "
        f"({p['home_win']*100:.0f}/{p['draw']*100:.0f}/{p['away_win']*100:.0f}) "
        f"actual={actual} {ok}"
    )
