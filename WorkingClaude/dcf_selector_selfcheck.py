# -*- coding: utf-8 -*-
"""dcf_selector_selfcheck.py — verification for the Pha-3 DCF overlay on the custom30V selector
(custom_basket.py, job Taylor_20260714_070221).

Checks the three things that can silently invalidate the backtest:
  [1] the cache-based status/robust EXACTLY reproduces production's
      trading_bot/strategies.py::_dcf_check_for_order on real (ticker, date, price) samples;
  [2] NOT_COMPUTED is a NEUTRAL pass-through in BOTH variants (never dropped in A, mid-rank 0.5
      in B) — the bug class that has already bitten the golden-floor gate twice;
  [3] the overlay is OFF by default (no env -> selection code path unchanged / byte-identical).

Run: $DNA_PYEXE dcf_selector_selfcheck.py
"""
import os, sys, bisect, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)

CACHE = f"{WORKDIR}/mike/agents/Taylor/dcf_exp/fv_sens_releases.parquet"
FAILS = []


def check(cond, label):
    print(f"  {'OK  ' if cond else 'FAIL'}  {label}")
    if not cond: FAILS.append(label)


# ---- shared: live status/robust (same code as custom_basket's dcf_at) --------------------------
# Mirrors the harness verbatim: fair_value(asof=d) resolves BOTH the release-as-of-d AND the
# discount rate / terminal g at d. An earlier version of this overlay read a per-release FV cache
# instead, which prices r/g at rel_time, not d -> 14/40 samples disagreed with production incl. a
# CHEAP/RICH flip at MoS~=0. Kept live on purpose; the cache parquet is no longer a dependency.
import dcf_valuation as _dcfv
_FIN = _dcfv._load_financials()


def status_live(tk, d, px):
    if not px or px <= 0:
        return ("NOT_COMPUTED", np.nan, False)
    try:
        res = _dcfv.fair_value(tk, pd.Timestamp(d), price=float(px), fin=_FIN)
    except Exception:
        return ("NOT_COMPUTED", np.nan, False)
    if not res.get("ok"):
        return ("NOT_COMPUTED", np.nan, False)
    mos = res.get("margin_of_safety")
    if mos is None or pd.isna(mos):
        return ("NOT_COMPUTED", np.nan, False)
    # the 4 box keys ONLY — `sensitivity` also carries a bare `base_fv_ps` float, and folding that
    # in would add a 5th point production never counts (and crash on .get). Same list production uses.
    _sens = res.get("sensitivity") or {}
    signs = [((f - px) / f) > 0 for f in
             ((_sens.get(k) or {}).get("fv") for k in ("r-1%", "r+1%", "g-2%", "g+2%"))
             if f and f > 0]
    robust = bool(signs) and all(s == (mos > 0) for s in signs)
    return (("CHEAP" if mos > 0 else "RICH"), float(mos), robust)


# ---- [1] parity with the production dcf_check producer ----------------------------------------
print("\n[1] live status/robust == production _dcf_check_for_order (real samples)")
from trading_bot.strategies import _dcf_check_for_order

import duckdb
c = duckdb.connect(":memory:")
samp = c.execute(f"""
    SELECT ticker, CAST(time AS DATE) AS d, Price FROM read_parquet('{WORKDIR}/data/bq_cache/ticker/202*.parquet')
    WHERE Price IS NOT NULL AND ticker IN (SELECT DISTINCT ticker FROM read_parquet('{CACHE}') WHERE ok)
      AND time IN (DATE '2021-05-05', DATE '2024-05-06', DATE '2025-11-05')
    ORDER BY hash(ticker || CAST(time AS VARCHAR)) LIMIT 40""").df()   # deterministic pseudo-sample
n_match = n_rich = n_cheap = n_nc = 0
for r in samp.itertuples():
    mine = status_live(r.ticker, r.d, float(r.Price))
    prod = _dcf_check_for_order(r.ticker, float(r.Price), r.d)
    same_status = mine[0] == prod["status"]
    same_robust = bool(mine[2]) == bool(prod["robust"])
    same_mos = (pd.isna(mine[1]) and prod["margin_of_safety"] is None) or (
        prod["margin_of_safety"] is not None and abs(mine[1] - prod["margin_of_safety"]) < 5e-4)
    if same_status and same_robust and same_mos: n_match += 1
    else: print(f"    MISMATCH {r.ticker} {r.d}: mine={mine} prod={prod}")
    n_rich += mine[0] == "RICH"; n_cheap += mine[0] == "CHEAP"; n_nc += mine[0] == "NOT_COMPUTED"
check(len(samp) >= 20 and n_match == len(samp),   # len guard: 0/0 must never pass vacuously
      f"{n_match}/{len(samp)} samples match production exactly "
                            f"(RICH={n_rich} CHEAP={n_cheap} NOT_COMPUTED={n_nc})")
check(n_rich > 0 and n_cheap > 0 and n_nc > 0, "sample covers all three statuses (test is meaningful)")

# ---- [2] NOT_COMPUTED neutrality in both variants ---------------------------------------------
print("\n[2] NOT_COMPUTED = neutral pass-through (not auto-cheap, not auto-rich)")
# synthetic pool replicating the exact overlay code paths in custom_basket.py
POOL = [("RICHROB", ("RICH", -0.50, True)), ("RICHSOFT", ("RICH", -0.02, False)),
        ("CHEAPROB", ("CHEAP", 0.40, True)), ("NC1", ("NOT_COMPUTED", np.nan, False)),
        ("NC2", ("NOT_COMPUTED", np.nan, False))]
SM = dict(POOL)
pool = [(t, 2) for t, _ in POOL]

# variant A path (verbatim logic from custom_basket.py)
keep = [(t, rt) for t, rt in pool if not (lambda s: s[0] == "RICH" and s[2])(SM[t])]
kept = {t for t, _ in keep}
check("NC1" in kept and "NC2" in kept, "A: NOT_COMPUTED kept in pool (not dropped)")
check("RICHROB" not in kept, "A: RICH+robust dropped")
check("RICHSOFT" in kept, "A: RICH but non-robust kept (sensitivity box flipped sign)")
check("CHEAPROB" in kept, "A: CHEAP kept")

# variant B path (verbatim logic)
mos_r = pd.Series({t: SM[t][1] for t, _ in pool}).rank(pct=True).fillna(0.5)
check(abs(mos_r["NC1"] - 0.5) < 1e-9 and abs(mos_r["NC2"] - 0.5) < 1e-9,
      "B: NOT_COMPUTED gets neutral 0.5 mid-rank (same convention as a missing 1/PE)")
check(mos_r["CHEAPROB"] > 0.5 > mos_r["RICHROB"],
      "B: CHEAP ranks above the neutral mid-rank, RICH below")
check(mos_r["RICHROB"] < mos_r["RICHSOFT"] < mos_r["CHEAPROB"], "B: MoS ordering monotone")
# a NOT_COMPUTED name must not be able to out/under-rank purely from the DCF term
W = 0.25
check(abs(W * mos_r["NC1"] - W * 0.5) < 1e-9, f"B: DCF term for NOT_COMPUTED = W*0.5 = {W*0.5} (constant, cancels in ordering)")

# ---- [2b] regression: a ticker whose CURRENT release is NOT_COMPUTED must not inherit a stale
#      older computable FV (the ok-only-filter bug caught by check [1] on 2026-07-14).
print("\n[2b] regression: stale ok-release must not mask a current NOT_COMPUTED")
_all = pd.read_parquet(CACHE); _all["rel_time"] = pd.to_datetime(_all["rel_time"])
_flip = _all.sort_values(["ticker", "rel_time"]).groupby("ticker").filter(
    lambda g: len(g) > 2 and g.ok.iloc[:-1].any() and not g.ok.iloc[-1])
check(len(_flip) > 0, f"found {_flip.ticker.nunique()} tickers that go ok -> NOT_COMPUTED (case exists)")
if len(_flip):
    tk = _flip.ticker.iloc[-1]
    g = _all[_all.ticker == tk].sort_values("rel_time")
    d_after = g.rel_time.iloc[-1] + pd.Timedelta(days=1)
    check(status_live(tk, d_after, 10000.0)[0] == "NOT_COMPUTED",
          f"{tk} after its NOT_COMPUTED release -> NOT_COMPUTED (no stale-FV fallback)")

# ---- [3] default OFF ---------------------------------------------------------------------------
print("\n[3] overlay OFF by default")
for k in ("BASKET_DCF_MODE", "BASKET_DCF_W"): os.environ.pop(k, None)
import custom_basket as CB
src = open(f"{WORKDIR}/custom_basket.py").read()
check('os.environ.get("BASKET_DCF_MODE", "")' in src, "BASKET_DCF_MODE defaults to '' (OFF)")
check("if DCF_MODE:" in src and "dcf_at = None" in src,
      "cache/price load and dcf_at are gated behind DCF_MODE (OFF -> no work, no behaviour change)")
# The invariant is "every use of dcf_at is dominated by an `dcf_at is not None` guard", NOT a
# literal-string count: an earlier version asserted `src.count("if dcf_at is not None and DCF_MODE
# ==") == 2` and went red on 2026-08-08 purely because the placebo modes turned one `== "..."` into
# `in ("...", "...")` — three correctly-guarded call-sites, zero behaviour change. Check the
# structure with `ast` so a refactor that keeps the guard keeps the test green.
import ast as _ast

_tree = _ast.parse(src)
_guarded = []      # line ranges of `if dcf_at is not None ...:` bodies
_uses = []         # linenos of every `dcf_at(...)` call
for _n in _ast.walk(_tree):
    if isinstance(_n, _ast.If):
        for _t in _ast.walk(_n.test):
            if (isinstance(_t, _ast.Compare) and isinstance(_t.left, _ast.Name)
                    and _t.left.id == "dcf_at"
                    and any(isinstance(o, _ast.IsNot) for o in _t.ops)
                    and any(isinstance(c, _ast.Constant) and c.value is None for c in _t.comparators)):
                _guarded.append((_n.body[0].lineno, max(_ast.walk(_n.body[-1]),
                                                       key=lambda x: getattr(x, "lineno", 0)).lineno))
                break
    if isinstance(_n, _ast.Call) and isinstance(_n.func, _ast.Name) and _n.func.id == "dcf_at":
        _uses.append(_n.lineno)
_unguarded = [ln for ln in _uses if not any(a <= ln <= b for a, b in _guarded)]
check(len(_uses) >= 2 and not _unguarded,
      f"all {len(_uses)} dcf_at(...) call-sites sit inside an `dcf_at is not None` guard "
      f"({len(_guarded)} guards; unguarded lines={_unguarded}) -> OFF leaves yieldcombo untouched")

print("\n" + ("SELFCHECK PASS" if not FAILS else f"SELFCHECK FAIL ({len(FAILS)}): {FAILS}"))
sys.exit(1 if FAILS else 0)
