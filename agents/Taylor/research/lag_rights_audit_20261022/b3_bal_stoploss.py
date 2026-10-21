#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B3 phụ — `_bal_stop_loss_candidates` (hàm thuần) khi mã BAL có quyền mua: GDKHQ hạ marketPrice
theo TERP nhưng (GIẢ ĐỊNH) DNSE KHÔNG hạ costPrice vì KL chưa đổi ⇒ pnl broker gộp cả phần
'pha loãng' vào lỗ. Không I/O."""
import datetime as dt
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b3_common as C  # noqa: E402,F401  (test-mode env)
import auto_exit_inject as aei  # noqa: E402

lots = {"SCL": {"qty": 14_000, "entry_date": "2026-10-26"}}
asof = dt.date(2026, 11, 20)
for mp in (25_400, 23_800):
    pos = {"SCL": {"qty": 14_000, "avg_cost": 30_000.0, "marketPrice": mp, "sellable": 14_000}}
    out, blk = aei._bal_stop_loss_candidates(asof, pos, lots)
    print(f"marketPrice={mp}: pnl broker={mp/30_000-1:+.1%} | so với TERP 25.395: "
          f"{mp/25_395-1:+.1%} | stop-loss hit={bool(out)} {out}")
