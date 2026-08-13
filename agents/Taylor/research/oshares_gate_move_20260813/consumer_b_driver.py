#!/usr/bin/env python3
"""consumer_b_driver.py — chạy ĐÚNG điểm nối Việc B (`rating_8l._reconcile_oshares`) và chụp
`OShares` ra file, để so TRƯỚC/SAU khi dời cổng chứng nhận.

Không tái tạo lại logic của `rating_8l` — gọi thẳng hàm thật trên `df` thật của phiên chấm rating,
vì thứ cần chứng minh là "consumer nhận được số y hệt", không phải "mô hình của tôi về consumer".
"""
import json
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")        # §5b: không ghi vào sổ burn-in thật

import rating_8l as R                                                       # noqa: E402

df = R.bq(R.MAIN_SQL)
before = dict(zip(df["ticker"], df["OShares"]))
out = R._reconcile_oshares(df)
after = dict(zip(out["ticker"], out["OShares"]))

path = sys.argv[1]
with open(path, "w", encoding="utf-8") as fh:
    json.dump({"n": len(after),
               "oshares": {t: (None if v is None or v != v else float(v))
                           for t, v in after.items()},
               "n_changed_vs_bq_admin": sum(
                   1 for t in after
                   if (after[t] is None) != (before[t] is None)
                   or (after[t] is not None and before[t] is not None
                       and float(after[t]) != float(before[t])))},
              fh, ensure_ascii=False, indent=1, sort_keys=True)
print(f"đã ghi {len(after)} mã -> {path}")
