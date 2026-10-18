# -*- coding: utf-8 -*-
"""dcf_selector_selfcheck.py — verification for the Pha-3 DCF overlay on the custom30V selector
(custom_basket.py, job Taylor_20260714_070221).

Checks the three things that can silently invalidate the backtest:
  [1] custom_basket.py's REAL `dcf_at` (extracted from source and exec'd, not re-typed here)
      EXACTLY reproduces production's trading_bot/strategies.py::_dcf_check_for_order on real
      (ticker, date, price) samples;
  [2] NOT_COMPUTED is a NEUTRAL pass-through in BOTH variants (never dropped in A, mid-rank 0.5
      in B) — the bug class that has already bitten the golden-floor gate twice. Runs the REAL
      variant-A `_keep` and variant-B `mos_r` statements extracted from custom_basket.py;
  [3] the overlay is OFF by default (no env -> selection code path unchanged / byte-identical).

Run: $DNA_PYEXE dcf_selector_selfcheck.py
"""
import os, sys, bisect, warnings, importlib.util
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"            # DỮ LIỆU production (bq_cache, parquet — không track)
HERE = os.path.dirname(os.path.abspath(__file__))   # code under test: cạnh file này (worktree-aware)


def _load(name):
    """Nạp module GỐC từ HERE theo đường dẫn file — module production tự chèn WORKDIR canonical vào
    sys.path[0], nên `import <name>` từ worktree sẽ lặng lẽ lấy bản canonical (cùng mẫu
    tz_asof_ict_dd_dcf_selfcheck.py)."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    assert os.path.abspath(mod.__file__).startswith(HERE + os.sep), mod.__file__
    return mod


sys.path.insert(0, HERE); os.chdir(WORKDIR)

CACHE = f"{WORKDIR}/mike/agents/Taylor/dcf_exp/fv_sens_releases.parquet"
FAILS = []


def check(cond, label):
    print(f"  {'OK  ' if cond else 'FAIL'}  {label}")
    if not cond: FAILS.append(label)


# ---- shared: the REAL dcf_at, extracted from custom_basket.py ---------------------------------
# dcf_at is a closure inside build_pit, so it cannot be imported. Re-typing it here (an earlier
# version of this file did) lets the selfcheck stay green while the real function drifts from
# production. Instead pull its source out with `ast` and exec it against the same free names it
# closes over (_px_map, _dcfv, _fin, _dcf_memo, _dcf_stat). fair_value(asof=d) resolves BOTH the
# release-as-of-d AND the discount rate / terminal g at d — kept live on purpose (a per-release FV
# cache prices r/g at rel_time, not d -> 14/40 samples disagreed with production).
import ast as _ast, textwrap

_CB_SRC = open(os.path.join(HERE, "custom_basket.py"), encoding="utf-8").read()
_CB_TREE = _ast.parse(_CB_SRC)


def _one(nodes, what):
    nodes = list(nodes)
    assert len(nodes) == 1, f"expected exactly 1 {what} in custom_basket.py, found {len(nodes)}"
    return textwrap.dedent(_ast.get_source_segment(_CB_SRC, nodes[0]))


def _extract_func(name):
    return _one((n for n in _ast.walk(_CB_TREE) if isinstance(n, _ast.FunctionDef) and n.name == name),
                f"def {name}")


def _extract_assign(target):
    return _one((n for n in _ast.walk(_CB_TREE) if isinstance(n, _ast.Assign) and len(n.targets) == 1
                 and isinstance(n.targets[0], _ast.Name) and n.targets[0].id == target),
                f"assignment to {target}")


_dcfv = _load("dcf_valuation")
_FIN = _dcfv._load_financials()
_PX_MAP = {}                                         # (ticker, Timestamp) -> Price, filled per sample
_DCF_NS = {"pd": pd, "np": np, "_dcfv": _dcfv, "_fin": _FIN, "_px_map": _PX_MAP,
           "_dcf_memo": {}, "_dcf_stat": {"CHEAP": 0, "RICH": 0, "NOT_COMPUTED": 0}}
exec(_extract_func("dcf_at"), _DCF_NS)
dcf_at = _DCF_NS["dcf_at"]


def status_live(tk, d, px):
    """The REAL custom_basket.dcf_at at (tk, d) with price `px` injected into its price map."""
    _PX_MAP[(tk, pd.Timestamp(d))] = float(px)
    _DCF_NS["_dcf_memo"].pop((tk, pd.Timestamp(d)), None)
    return dcf_at(tk, d)


# ---- [1] parity with the production dcf_check producer ----------------------------------------
print("\n[1] custom_basket.dcf_at (real code) == production _dcf_check_for_order (real samples)")
sys.path.insert(0, HERE)                                # dcf_valuation vừa chèn WORKDIR canonical lên đầu
import trading_bot.strategies as _strat
assert os.path.abspath(_strat.__file__).startswith(HERE + os.sep), _strat.__file__
_dcf_check_for_order = _strat._dcf_check_for_order

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
# synthetic pool fed through the REAL overlay statements extracted from custom_basket.py
POOL = [("RICHROB", ("RICH", -0.50, True)), ("RICHSOFT", ("RICH", -0.02, False)),
        ("CHEAPROB", ("CHEAP", 0.40, True)), ("NC1", ("NOT_COMPUTED", np.nan, False)),
        ("NC2", ("NOT_COMPUTED", np.nan, False))]
SM = dict(POOL)
pool = [(t, 2) for t, _ in POOL]
_stub = lambda t, d: SM[t]

# variant A: the real `_keep = [...]` statement
_ns_a = {"pool": pool, "dcf_at": _stub, "d": None}
exec(_extract_assign("_keep"), _ns_a)
keep = _ns_a["_keep"]
kept = {t for t, _ in keep}
check("NC1" in kept and "NC2" in kept, "A: NOT_COMPUTED kept in pool (not dropped)")
check("RICHROB" not in kept, "A: RICH+robust dropped")
check("RICHSOFT" in kept, "A: RICH but non-robust kept (sensitivity box flipped sign)")
check("CHEAPROB" in kept, "A: CHEAP kept")

# variant B: the real `mos_r = ...` statement
_ns_b = {"pool": pool, "dcf_at": _stub, "d": None, "pd": pd}
exec(_extract_assign("mos_r"), _ns_b)
mos_r = _ns_b["mos_r"]
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
CB = _load("custom_basket")
src = open(f"{HERE}/custom_basket.py").read()
check('os.environ.get("BASKET_DCF_MODE", "")' in src, "BASKET_DCF_MODE defaults to '' (OFF)")
check("if DCF_MODE:" in src and "dcf_at = None" in src,
      "cache/price load and dcf_at are gated behind DCF_MODE (OFF -> no work, no behaviour change)")
# The invariant is "every use of dcf_at is dominated by an `dcf_at is not None` guard", NOT a
# literal-string count: an earlier version asserted `src.count("if dcf_at is not None and DCF_MODE
# ==") == 2` and went red on 2026-08-08 purely because the placebo modes turned one `== "..."` into
# `in ("...", "...")` — three correctly-guarded call-sites, zero behaviour change. Check the
# structure with `ast` so a refactor that keeps the guard keeps the test green.
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
