# -*- coding: utf-8 -*-
"""regen_c30v.py — regenerate the PUBLISHED `tav2_bq.custom30v_8l` artifact OFFLINE, from the
frozen pinned snapshot, on either price basis, WITHOUT touching the live BQ table.

Why this exists (job Taylor_20260802_154231, Việc 1): pt_v23_audit_2014.py:124 `_c30v_asof` reads
MEMBERSHIP from the already-published table, so an A/B that only flips BASKET_PRICE_BASIS inside
the simulator leaves that branch on the OLD basis — the CAPIT-membership gap quant-skeptic raised.
To close it we need the table itself rebuilt on the new basis.

The live table is read every session by golive_recommend_v23.py, so we do NOT republish it. We
exec the committed publisher's own build block (source-truncated immediately before its
`bq load --replace`) so the logic is byte-identical to production, and write the result to a local
parquet that overlays the frozen BQ cache instead.

  regen_c30v.py <legacy|split> <out.parquet>

Validation anchor: the `legacy` leg MUST reproduce the pinned cached custom30v_8l.parquet exactly.
If it does not, this regeneration path is not faithful and nothing may be concluded from `split`.
"""
import os, sys, subprocess

BASIS = sys.argv[1]
OUT = sys.argv[2]
assert BASIS in ("legacy", "split"), "basis must be legacy|split"

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
SRC = os.path.join(WORKDIR, "custom30_history.py")

# The V2.4 PRODUCTION parking basket = papertrade_daily.sh [6b]: BASKET_SELECT=yieldcombo +
# CUSTOM30_TABLE=custom30v_8l. Same frozen vintage the pinned R3 was measured on.
os.environ["BASKET_SELECT"] = "yieldcombo"
os.environ["BASKET_PRICE_BASIS"] = BASIS
os.environ["BQ_LOCAL_CACHE"] = os.path.join(WORKDIR, "data/bq_cache_asof20260729_postrestate")
os.environ["BQ_CACHE_THREADS"] = "1"
os.environ["CUSTOM30_CSV"] = f"c30v_regen_{BASIS}.csv"

src = open(SRC, encoding="utf-8").read()
# Cut the publisher at its BQ write. Everything above builds `df`; everything below is
# `bq load --replace` against the live production table, which must never run here.
marker = "schema = ("
assert src.count(marker) == 1, "publisher shape changed — re-check the truncation point"
build_only = src[: src.index(marker)]
assert "bq load" not in build_only and "--replace" not in build_only, "BQ write leaked into build"

ns = {"__name__": "__main__", "__file__": SRC}
exec(compile(build_only, SRC, "exec"), ns)

import pandas as pd
df = ns["df"].copy()

# Match the cached-parquet schema exactly (dates as date objects; the open-ended last rebal's
# effective_to is None, not the empty string the CSV path writes).
for c in ("rebal_date", "effective_from", "effective_to"):
    df[c] = pd.to_datetime(df[c], errors="coerce").dt.date
    df[c] = df[c].where(pd.notna(df[c]), None)
df["ticker"] = df["ticker"].astype(str)
df["quarter"] = df["quarter"].astype(str)
df["liq_rank"] = df["liq_rank"].astype("int64")
df["rating_8l"] = pd.to_numeric(df["rating_8l"], errors="coerce").astype("int64")
df["weight"] = df["weight"].astype("float64")

df.to_parquet(OUT, index=False)
print(f"OK basis={BASIS} rows={len(df)} rebals={df.rebal_date.nunique()} -> {OUT}")
