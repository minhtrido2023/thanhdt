# -*- coding: utf-8 -*-
"""custom30.py — single-call SERVICE for the 8L custom30 parking basket.
Reads the published BQ table tav2_bq.custom30_8l (built by custom30_history.py) so consumers
(bot/report/screener) get ONE consistent basket without re-running build_pit at runtime.

  from custom30 import current
  df = current(bq)              # today's basket: ticker, weight, rating_8l, liq_rank (weight-desc)
  df = current(bq, "2025-02-05")# basket effective on a past date

CLI:  python custom30.py [YYYY-MM-DD]
"""
import os
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
TABLE = "tav2_bq.custom30_8l"        # blend (liquidity-led) basket — pre-2026-06-30 live spec
TABLE_V = "tav2_bq.custom30v_8l"     # custom30V (yieldcombo) — the V2.4 production parking basket


def current(bq, asof=None, table=TABLE):
    """Members of the basket effective on `asof` (default today), weight-descending.
    `bq` = a query helper returning a DataFrame (e.g. simulate_holistic_nav.bq).
    `table` — pass TABLE_V for the V2.4 production parking basket (custom30V/yieldcombo);
    default TABLE keeps the legacy blend basket for the audit scripts built on it."""
    cond = f"DATE '{asof}'" if asof else "CURRENT_DATE()"
    return bq(f"""SELECT t.ticker, t.weight, t.rating_8l, t.liq_rank, t.rebal_date
FROM {table} AS t
WHERE t.rebal_date = (SELECT MAX(s.rebal_date) FROM {table} AS s WHERE s.rebal_date <= {cond})
ORDER BY t.weight DESC""")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
    from simulate_holistic_nav import bq
    asof = sys.argv[1] if len(sys.argv) > 1 else None
    df = current(bq, asof)
    rd = df["rebal_date"].iloc[0] if len(df) else "?"
    print(f"8L custom30 — rebal {rd} ({len(df)} mã), namecap≤10%:\n")
    for r in df.itertuples():
        print(f"  {r.ticker:<5} {r.weight*100:5.2f}%   8L={int(r.rating_8l) if r.rating_8l==r.rating_8l else '-'}  liq#{int(r.liq_rank)}")
