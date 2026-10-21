#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2b/B3 phụ — một record `event_type: RIGHTS` (dù chỉ PROPOSED) trong sổ corp_actions (bản SANDBOX)
lan tới park_holdings / book_lot_snapshot / compute_trim thế nào. Không đụng data/corp_actions.json thật."""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b3_common as C  # noqa: E402
import corp_actions as ca  # noqa: E402
import park_holdings as ph  # noqa: E402
import portfolio_status as ps  # noqa: E402

td, EX, PL = C.sandbox()
C.write_journal(EX, "2026-10-26", [(C.LAG_TK, "buy", C.QTY_OLD, C.PX_CUM, "LAG")])
C.write_raw(EX, "2026-11-20", 14_000, 14_000, C.PX_EX, 100e6, 100e6)
reg = os.path.join(td, "corp_actions.json")
json.dump({"actions": [{"id": "SCL-R", "ticker": "SCL", "event_type": "RIGHTS",
                        "qty_multiplier": 19 / 14, "ex_date": "2026-11-09",
                        "broker_effective_ts": "2026-12-03T19:00:00", "_status": "PROPOSED"}]},
          open(reg, "w"))
ph.load_corp_actions = lambda *a, **k: ca.load_corp_actions(reg)
ph.account_profile = lambda label: {"account_id": C.ACCOUNT_NO, "excluded_tickers": []}
try:
    ph.park_holdings(C.ACCOUNT, asof="2026-11-20", plan_dir=PL, exec_dir=EX,
                     price_fn=C.price_fn_for(C.PX_EX))
    print("park_holdings: OK")
except SystemExit as e:
    print(f"park_holdings: SystemExit {e}")
except Exception as e:
    print(f"park_holdings: {type(e).__name__} (KHÔNG phải SystemExit ⇒ compute_park_trim/"
          f"compute_jit_unpark không bắt): {str(e)[:120]}")
r = ps.book_lot_snapshot(C.ACCOUNT, "LAG", asof="2026-11-20", plan_dir=PL, exec_dir=EX)
print(f"book_lot_snapshot LAG: lots={r[0]} ok={r[1]} reason={str(r[2])[:140]}")
r = ps.book_lot_snapshot(C.ACCOUNT, "BAL", asof="2026-11-20", plan_dir=PL, exec_dir=EX)
print(f"book_lot_snapshot BAL: ok={r[1]}  (⇒ auto_exit chặn CẢ book LAG lẫn BAL của account)")
