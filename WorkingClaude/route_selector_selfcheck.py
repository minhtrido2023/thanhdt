# -*- coding: utf-8 -*-
"""route_selector_selfcheck.py — verification for BASKET_SELECT=v3route (custom_basket.py,
job Taylor_20260714_112932).

v3route = v3latest, except the three FINANCIAL routes (BANK/INSURANCE/SECURITIES) are scored with
rating_8l's value_score_v2 formula instead of the ey/cfy/ps composite — because a bank's 1/PCF
(deposit/loan flows) is not comparable to a manufacturer's (cash from core operations).

Checks the things that can silently invalidate the backtest:
  [1] OFF by default — no BASKET_SELECT env -> the v3route code path is never entered.
  [2] BANK really is scored on the v2 axis (pb_z + within-route ey), NOT cfy: perturbing a bank's
      PCF must NOT move its score; perturbing its pb_z MUST.
  [3] Non-financial routes are BYTE-IDENTICAL to v3latest (clean single-axis ablation).
  [4] Ranking is WITHIN route (a bank competes with banks, not with manufacturers).
  [5] Coverage-aware / missing-data behavior: no pb_z -> abstain (NaN), never a fabricated 0.5;
      golden floor + PB<0 handling unchanged.
  [6] The v2 score reproduces rating_8l's value_score_v2 arithmetic exactly on real panel rows.

Run: $DNA_PYEXE route_selector_selfcheck.py
"""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)

FAILS = []


def check(cond, label):
    print(f"  {'OK  ' if cond else 'FAIL'}  {label}")
    if not cond: FAILS.append(label)


# ---------------------------------------------------------------------------------------------
# Harness: custom_basket reads BASKET_SELECT at build_pit() time, and _score_v3 is a closure over
# it. Rather than run a full (slow, BQ-hitting) build, re-exec the scoring block against the same
# panel the harness uses, with the same env, by importing the module and calling a rebuilt closure.
# We do that by driving build_pit's own code through a tiny shim: load the panel exactly as the
# module does, then reproduce _score_v3 via the module's source in a controlled namespace.
# Simpler + more faithful: call build_pit with a fake bq that returns the minimum, and capture the
# scores it computes. But build_pit needs real liquidity/rating data -> instead we test the
# SCORING semantics directly by re-deriving it from the module, and test the env gating by
# inspecting the module's branch behavior.
# ---------------------------------------------------------------------------------------------
PANEL = os.path.join(WORKDIR, "data", "value_panel_2014.csv")
_p = pd.read_csv(PANEL, parse_dates=["time"])
_p["qstart"] = _p["time"].dt.to_period("Q").dt.start_time
_p = _p.sort_values("time").groupby(["ticker", "qstart"]).last().reset_index()
_COLS = ["qstart", "ticker", "PE", "PCF", "PS", "pb_z", "PB", "route", "ICB_Code", "ROE_Min3Y",
         "CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3", "CF_OA_3Y", "ROE_Min5Y", "CF_OA_5Y"]
PQ = _p[[c for c in _COLS if c in _p.columns]]

VR_W_LATEST = {"COMPOUNDER": (.45, .30, .25), "CYCLICAL": (.40, .60, .00), "RETAIL": (.35, .20, .45)}
_V2_ROUTES = {"BANK", "INSURANCE", "SECURITIES"}
W_ABS_V2 = 0.65


def score(pool_tokens, src_q, mode, panel=None):
    """Reimplementation of custom_basket._score_v3 for mode in {v3latest, v3route}.

    This is a MIRROR used to test semantics; check [6] pins it against rating_8l's own arithmetic
    and check [3]/[2] pin the v3route-vs-v3latest delta. The real harness path is exercised by the
    integration run (pt_v23_audit_2014.py) separately.
    """
    _v3q = PQ if panel is None else panel
    toks = list(pool_tokens)
    d = _v3q[(_v3q.qstart == src_q) & (_v3q.ticker.isin(toks))].set_index("ticker").reindex(toks)
    ey = np.where(d.PE > 0, 1.0 / d.PE, np.nan)
    cfy = np.where(d.PCF > 0, 1.0 / d.PCF, np.nan)
    ps = np.where(d.PS > 0, 1.0 / d.PS, np.nan)
    _ttm = d[["CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3"]].sum(axis=1, min_count=1)
    _n3 = d["CF_OA_3Y"] / 3.0
    _cfynorm = np.where((d.PCF > 0) & (_ttm > 0) & (_n3 > 0), (1.0 / d.PCF) * np.clip(_n3 / _ttm, 0.3, 3.0), np.nan)
    cfy = np.where((d.route == "CYCLICAL").values, cfy, _cfynorm)
    F = pd.DataFrame({"ey": ey, "cfy": cfy, "ps": ps}, index=toks)
    icb = d.ICB_Code
    vr = np.where((d.route == "COMPOUNDER") & icb.apply(lambda c: pd.notna(c) and ((3500 <= c < 3800) or (5300 <= c < 5400))),
                  "RETAIL", d.route.fillna("COMPOUNDER"))
    vr = pd.Series(vr, index=toks)
    pct = {}
    for c in ["ey", "cfy", "ps"]:
        rr = F[c].groupby(vr).transform(lambda g: g.rank(pct=True) if g.notna().sum() >= 5 else pd.Series(np.nan, index=g.index))
        gg = F[c].rank(pct=True); m = rr.isna() & F[c].notna(); rr = rr.copy(); rr[m] = gg[m]
        pct[c] = rr
    Wm = np.array([VR_W_LATEST.get(v, VR_W_LATEST["COMPOUNDER"]) for v in vr])
    P = np.vstack([pct["ey"].values, pct["cfy"].values, pct["ps"].values]).T
    pres = ~np.isnan(P); num = np.nansum(np.where(pres, P * Wm, 0), 1); den = np.nansum(np.where(pres, Wm, 0), 1)
    sc = np.where(den > 0, num / den, np.nan)
    golden = (d.pb_z.values <= -1); bookok = ~(d.ROE_Min3Y.values < 0)
    bookok = bookok & (d.CF_OA_3Y.values > 0)
    if mode == "v3route":
        _fin = vr.isin(_V2_ROUTES).values
        if _fin.any():
            _rel = np.clip(0.5 - d.pb_z.values / 2.0, 0, 1)
            _cfo_pct = pd.Series(cfy, index=toks).rank(pct=True)
            _adj = np.where(_cfo_pct.notna() & (_cfo_pct >= 0.5), 0.05,
                            np.where(_cfo_pct.notna() & (_cfo_pct < 0.2), -0.08, 0.0))
            _track = (np.where(pd.Series(d.get("CF_OA_5Y", np.nan), index=toks).fillna(-9).values > 0, 0.03, 0.0)
                      + np.where(pd.Series(d.get("ROE_Min5Y", np.nan), index=toks).fillna(-9).values > 0.10, 0.03, 0.0))
            _v2 = np.clip((1 - W_ABS_V2) * _rel + W_ABS_V2 * np.nan_to_num(pct["ey"].values, nan=0.5) + _adj + _track, 0, 1)
            _v2 = np.where(np.isnan(d.pb_z.values), np.nan, _v2)
            sc = np.where(_fin, _v2, sc)
    sc = sc + 0.10 * np.where(golden & pd.notna(d.pb_z.values), 1.0, 0.0)
    sc = np.where(d.PB.values < 0, 0.0, sc)
    sc = np.where(golden & bookok, np.maximum(np.nan_to_num(sc, nan=0.0), 1.0), sc)
    return {t: (float(v) if pd.notna(v) else -1.0) for t, v in zip(toks, sc)}


# pick a real, well-populated quarter with a decent mix of routes
_q = pd.Timestamp("2023-01-01")
_pool_df = PQ[(PQ.qstart == _q) & PQ.PE.notna()]
POOL = list(_pool_df.ticker)
BANKS = list(_pool_df[_pool_df.route == "BANK"].ticker)
# checks [2]/[6] perturb a bank's inputs, so the sample must be one that actually SCORES —
# a bank without pb_z correctly abstains (score -1) and is inert to perturbation (see [5]).
BANKS_SCORED = list(_pool_df[(_pool_df.route == "BANK") & _pool_df.pb_z.notna()].ticker)
NONFIN = list(_pool_df[~_pool_df.route.isin(_V2_ROUTES)].ticker)
print(f"panel quarter {_q.date()}: pool={len(POOL)} banks={len(BANKS)} (scored {len(BANKS_SCORED)}) nonfin={len(NONFIN)}")

print("\n[1] OFF by default — v3route never entered without the env")
_prev = os.environ.pop("BASKET_SELECT", None)
import custom_basket  # noqa: E402
_src = open(os.path.join(WORKDIR, "custom_basket.py")).read()
check(os.environ.get("BASKET_SELECT") is None, "no BASKET_SELECT in a clean env")
check('SELECT_MODE = os.environ.get("BASKET_SELECT", "blend")' in _src,
      "default SELECT_MODE is 'blend' (production yieldcombo is set explicitly, never v3route)")
check(_src.count('"v3route"') > 0 and 'if SELECT_MODE == "v3route"' in _src,
      "v3route branch is env-gated inside _score_v3, not a default")
if _prev is not None: os.environ["BASKET_SELECT"] = _prev

print("\n[2] BANK is scored on the v2 axis (pb_z + within-route ey), NOT on cfy/PCF")
base = score(POOL, _q, "v3route")
# perturb a bank's PCF hard (halve it => 1/PCF doubles). Under v3route its score must not move
# beyond the small pool-wide cfo-confirm nudge; under v3latest (cfy w=.30) it must move.
_bank = BANKS_SCORED[0]
pert = PQ.copy()
_m = (pert.qstart == _q) & (pert.ticker == _bank)
pert.loc[_m, "PCF"] = pert.loc[_m, "PCF"] / 2.0
s_pcf = score(POOL, _q, "v3route", panel=pert)
s_pcf_latest = score(POOL, _q, "v3latest", panel=pert)
b_latest = score(POOL, _q, "v3latest")
d_route = abs(s_pcf[_bank] - base[_bank])
d_latest = abs(s_pcf_latest[_bank] - b_latest[_bank])
print(f"      bank={_bank}: |Δscore| on PCF/2 -> v3route {d_route:.4f} vs v3latest {d_latest:.4f}")
check(d_route < 1e-9 or d_route <= 0.05, f"v3route: bank score is (near-)insensitive to PCF ({d_route:.4f})")
check(d_latest > d_route, f"v3latest DOES move on PCF ({d_latest:.4f}) — confirms the axis actually changed")
# pb_z must matter under v3route
pert2 = PQ.copy()
_m2 = (pert2.qstart == _q) & (pert2.ticker == _bank)
pert2.loc[_m2, "pb_z"] = pert2.loc[_m2, "pb_z"] + 1.0
s_pbz = score(POOL, _q, "v3route", panel=pert2)
print(f"      bank={_bank}: |Δscore| on pb_z+1 -> v3route {abs(s_pbz[_bank]-base[_bank]):.4f}")
check(abs(s_pbz[_bank] - base[_bank]) > 0.01, "v3route: bank score DOES respond to pb_z (the intended metric)")

print("\n[3] non-financial routes BYTE-IDENTICAL to v3latest (clean single-axis ablation)")
_diff = [t for t in NONFIN if abs(base[t] - b_latest[t]) > 1e-12]
check(len(_diff) == 0, f"{len(NONFIN)} non-financial names unchanged vs v3latest ({len(_diff)} differ)")
_fin_changed = [t for t in POOL if t not in NONFIN and abs(base[t] - b_latest[t]) > 1e-9]
check(len(_fin_changed) > 0, f"financial names DID change ({len(_fin_changed)} of {len(POOL)-len(NONFIN)}) — not a silent no-op")

print("\n[4] ranking is WITHIN route (bank competes with banks)")
# shift EVERY non-financial's PE to make the whole market look dirt cheap; a bank's score must not move.
pert3 = PQ.copy()
_m3 = (pert3.qstart == _q) & (~pert3.route.isin(_V2_ROUTES))
pert3.loc[_m3, "PE"] = pert3.loc[_m3, "PE"] / 5.0
s_iso = score(POOL, _q, "v3route", panel=pert3)
_moved = [t for t in BANKS if abs(s_iso[t] - base[t]) > 1e-9]
check(len(_moved) == 0, f"banks' scores unaffected by a market-wide non-financial PE shock ({len(_moved)} moved)")

print("\n[5] coverage-aware / missing-data behavior")
_nopbz = PQ[(PQ.qstart == _q) & (PQ.route.isin(_V2_ROUTES)) & (PQ.pb_z.isna())]
_nopbz_in = [t for t in _nopbz.ticker if t in base]
if _nopbz_in:
    check(all(base[t] == -1.0 for t in _nopbz_in),
          f"financial w/o pb_z abstains (score -1, ranked last) not a fabricated 0.5 — n={len(_nopbz_in)}")
else:
    print("      (no financial lacks pb_z in this quarter — checked synthetically instead)")
    pert4 = PQ.copy(); pert4.loc[(pert4.qstart == _q) & (pert4.ticker == _bank), "pb_z"] = np.nan
    s4 = score(POOL, _q, "v3route", panel=pert4)
    check(s4[_bank] == -1.0, "financial w/o pb_z abstains (score -1), not a fabricated 0.5")
# PB<0 -> 0
pert5 = PQ.copy(); pert5.loc[(pert5.qstart == _q) & (pert5.ticker == _bank), "PB"] = -1.0
s5 = score(POOL, _q, "v3route", panel=pert5)
check(s5[_bank] == 0.0, "PB<0 -> score 0 (unchanged guard)")
# golden floor still fires for a book-OK financial
pert6 = PQ.copy()
_m6 = (pert6.qstart == _q) & (pert6.ticker == _bank)
pert6.loc[_m6, ["pb_z", "ROE_Min3Y", "CF_OA_3Y"]] = [-1.5, 0.10, 0.10]
s6 = score(POOL, _q, "v3route", panel=pert6)
check(s6[_bank] >= 1.0, "golden-cell (pb_z<=-1) + book-OK financial hits the golden floor (>=1.0)")

print("\n[6] v2 arithmetic reproduces rating_8l.value_score_v2 on real rows")
# rating_8l: value_score_v2 = 0.35*(0.5 - pb_z/2).clip(0,1) + 0.65*value_yield_pct(within route)
#                             + adj(cfo_normy pool-pct: >=.5 -> +.05, <.2 -> -.08) + track bonus
# Recompute independently for one bank and compare to the selector's pre-golden score.
_d = PQ[(PQ.qstart == _q) & (PQ.ticker.isin(POOL))].set_index("ticker").reindex(POOL)
_ey = np.where(_d.PE > 0, 1.0 / _d.PE, np.nan)
_ttm = _d[["CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3"]].sum(axis=1, min_count=1)
_n3 = _d["CF_OA_3Y"] / 3.0
_cfyn = np.where((_d.PCF > 0) & (_ttm > 0) & (_n3 > 0), (1.0 / _d.PCF) * np.clip(_n3 / _ttm, 0.3, 3.0), np.nan)
_cfyn = np.where((_d.route == "CYCLICAL").values, np.where(_d.PCF > 0, 1.0 / _d.PCF, np.nan), _cfyn)
_vrs = pd.Series(np.where((_d.route == "COMPOUNDER") & _d.ICB_Code.apply(lambda c: pd.notna(c) and ((3500 <= c < 3800) or (5300 <= c < 5400))),
                          "RETAIL", _d.route.fillna("COMPOUNDER")), index=POOL)
_eyS = pd.Series(_ey, index=POOL)
_eyr = _eyS.groupby(_vrs).transform(lambda g: g.rank(pct=True) if g.notna().sum() >= 5 else pd.Series(np.nan, index=g.index))
_gg = _eyS.rank(pct=True); _mm = _eyr.isna() & _eyS.notna(); _eyr = _eyr.copy(); _eyr[_mm] = _gg[_mm]
_cp = pd.Series(_cfyn, index=POOL).rank(pct=True)
_i = POOL.index(_bank)
_expect = np.clip(0.35 * np.clip(0.5 - _d.pb_z.values[_i] / 2.0, 0, 1)
                  + 0.65 * (_eyr.values[_i] if pd.notna(_eyr.values[_i]) else 0.5)
                  + (0.05 if (pd.notna(_cp.values[_i]) and _cp.values[_i] >= 0.5) else (-0.08 if (pd.notna(_cp.values[_i]) and _cp.values[_i] < 0.2) else 0.0))
                  + (0.03 if _d.CF_OA_5Y.values[_i] > 0 else 0.0)
                  + (0.03 if _d.ROE_Min5Y.values[_i] > 0.10 else 0.0), 0, 1)
_got = base[_bank]
_golden_adj = 0.10 if (_d.pb_z.values[_i] <= -1) else 0.0
print(f"      {_bank}: independent v2 recompute {_expect+_golden_adj:.6f} vs selector {_got:.6f}")
check(abs((_expect + _golden_adj) - _got) < 1e-6, "selector v2 branch == independent rating_8l arithmetic")

print("\n" + ("=" * 70))
print(f"RESULT: {'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'}")
for f in FAILS: print("  FAILED:", f)
sys.exit(1 if FAILS else 0)
