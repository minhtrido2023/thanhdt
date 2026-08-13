#!/usr/bin/env python3
"""consumer_c_driver.py — consumer THỨ BA của `oshares_at`, không nằm trong đề bài dispatch:
`mike/bin/corp_action_daily.py` (cron LIVE từ 2026-08-13) import THẲNG `oshares_at`, không qua
`oshares_pit`. Đó chính là hình dạng rủi ro mà vòng 4 đang đóng — nên phải ĐO nó, không suy luận.

Dựng lại đúng `track set` của lượt chạy thật (mã đang giữ ∪ ex-right hôm nay ∪ AIS hiệu lực hôm
nay) rồi chụp `oshares_at` trên đúng tập đó.
"""
import json
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

import corp_action_daily as C                                               # noqa: E402
from oshares_live import _fetch, oshares_at                                 # noqa: E402

asof = sys.argv[2] if len(sys.argv) > 2 else C.today_ict()
pos = C.read_positions(asof=asof)
held = sorted({tk for a in pos.values() for tk in a["positions"]})
ex_today, ais_today, _ev = C.triggered_today(asof)
track = sorted(set(held) | ex_today | ais_today)
cache = _fetch(track, asof) if track else ([], [])
cur = oshares_at(track, asof, _cache=cache) if track else {}

with open(sys.argv[1], "w", encoding="utf-8") as fh:
    json.dump({"asof": asof, "n_track": len(track), "held": held,
               "rows": {t: {"value": r["value"], "method": r["method"],
                            "anchor_date": r.get("anchor_date"),
                            "anchor_source": r.get("anchor_source")}
                        for t, r in sorted(cur.items())}},
              fh, ensure_ascii=False, indent=1, sort_keys=True)
print(f"asof={asof} track={len(track)} -> {sys.argv[1]}")
