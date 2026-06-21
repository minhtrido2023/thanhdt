# -*- coding: utf-8 -*-
"""
macro_state_live.py
===================
Reusable LIVE consolidated-macro-state module (production + paper-trade).

CANONICAL NAME: **DT5G** = DT 4-gate (4 state gates) + Macro gate (SBV money + US panic,
  bull-bypass, cap-commit K=7, confirmed easing) + a breadth-decoupling guard on the US
  pillar (suppress the US cap when VN breadth is broadly healthy while the US panics —
  fail-safe, free insurance; added 2026-05-29, shipped to production). DT5G == DT4G in
  benign windows; diverges only on persistent macro stress/easing or a US-VN decoupling.
  (Identifiers: BQ table vnindex_5state_dt5g_live, package deploy_golive_dt5g_v4.)

Computes the macro-adjusted 5-state series for any [start, end] window by fusing,
into ONE causal signal, the three existing rule families (no rule-sprawl):
  Pillar A  DOMESTIC MONEY  — SBV refi 6m-momentum (sbv_macro_overlay.SBV_REFI_EVENTS)
  Pillar B  US PANIC        — VIX + SPX 1y drawdown (us_market_history.csv, aligned T-1)
  + v3.4b BULL-AWARE BYPASS — in a confirmed VN bull, ignore Pillar B, keep Pillar A
Asymmetric action on the DT-4gate base state:
  DEFENSIVE  stress  -> CAP state ceiling (CRISIS/BEAR/NEUTRAL)
  RECOVERY   SBV cut from peak + US calm, CONFIRMED (>=10 sessions persist AND price
             turn-up Close>Close[t-10]) -> FLOOR at NEUTRAL
Validated (2026-05-29): pure-index sensitivity plateau (+0.39..+0.76pp, bull-bypass
essential). INTEGRATED prod-spec ablation (run_5systems_prodspec STATE_OVERRIDE=dt4/dt5g,
50B): V5 +0.43pp / V4 +0.27pp FULL; **IS 2014-19 = +0.00pp EXACTLY** (overlay dormant
in-sample — walk-forward IS/OOS is uninformative here); OOS 2020-now V5 +0.88pp / V4
+0.54pp. Edge rests on n=4 de-risk episodes (all post-2020, all EpRet<=0, 0 in-bull,
easing arm never fired); per-year LOO shows the ENTIRE edge = the single 2023 tightening
(+5pp/yr V5); 2025 bull COSTS -0.89pp. ⇒ DT5G = FAIL-SAFE GATE, not a return-enhancer.
Causal: US T-1, refi +5d. See validate_macro_report.md + audit_dt5g_events.md.

API:  get_macro_state(start, end, bq=None) -> DataFrame[time, state, state_dt4, cap, easing]
      The DT-4gate base is computed on-the-fly from tav2_bq.vnindex_5state_tam_quan_v34b_clean
      (always in sync with the daily-refreshed live table), warmed up from 2014.
"""
import os, sys
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
from sbv_macro_overlay import SBV_REFI_EVENTS

NEUTRAL, CRISIS, BEAR = 3, 1, 2
# fused-signal params (validated robust plateau; do NOT tune to history)
P = dict(vix_crisis=35, vix_bear=25, vix_mild=20,
         spx_crisis=-0.25, spx_bear=-0.15, spx_mild=-0.10,
         dom_extreme=3.0, dom_strong=1.5, dom_mild=0.5,
         refi_lag=5, refi_chg_win=126, refi_cut_drop=0.5,
         ez_confirm=10, ez_price_lb=10,
         cap_commit=7,          # cap must persist 7 sessions to commit (debounce whipsaw, 2026-05-29)
         bull_r6m=0.15,
         breadth_th=0.50,       # US cap suppressed if VN breadth_MA200 >= this (decoupling guard)
         breadth_min_univ=100)  # ...and only if the breadth universe is this large (else feed/nascent -> no suppress)


def _commit(arr, K):
    """Causal dwell: a new cap level must persist K sessions before it commits
       (debounces both tighten & release -> kills 1-3 day VIX-flicker transitions)."""
    if K <= 1:
        return arr.copy()
    out = arr.copy(); c = arr[0]; ps, pr = arr[0], 1
    for t in range(1, len(arr)):
        if arr[t] == ps: pr += 1
        else: ps, pr = arr[t], 1
        if pr >= K: c = ps
        out[t] = c
    return out


def _dt_4gate(states, default=10, enC=25, exC=10, enX=25, exX=10):
    """v3.4b 4-gate causal commitment (= DT_10_25_25). No look-ahead."""
    out = states.copy(); committed = states[0]; ps, pr = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps == committed:
            out[t] = committed; continue
        need = (enC if ps == 1 else enX if ps == 5
                else exC if committed == 1 else exX if committed == 5 else default)
        if pr >= need: committed = ps
        out[t] = committed
    return out


def get_macro_state(start, end, bq=None):
    if bq is None:
        from simulate_holistic_nav import bq as _bq; bq = _bq

    # Respect `start` but never warm up LESS than the default 2014 floor: read from the
    # EARLIER of (requested start, 2014-01-01). start>=2014 -> qstart=2014 (production
    # unchanged, byte-identical); start<2014 -> qstart=start (pre-2014 research, data
    # exists back to 2000). The DT-4gate needs lookback to commit states, so we never
    # truncate the warmup, only ever extend it.
    qstart = min(pd.Timestamp(start), pd.Timestamp("2014-01-01")).strftime("%Y-%m-%d")

    # ── DT-4gate base state (warmup from qstart, slice to window) ──
    # SOURCE OF TRUTH = BigQuery `vnindex_5state_tam_quan_v34b_clean` (the v3.4b base, deployed
    # daily from the ew_v1->dual_v3->v3.1->v3.4b chain). We read from BQ — NOT a local CSV — so the
    # state is always reconcilable against what the dev / downstream consumers pull from BQ.
    # (Changed 2026-06-02 per user: never silently prefer local data, else there is no reconciliation
    #  basis. If BQ lags, that is a deploy/ops gap to FIX by running the refresh+deploy chain — we
    #  WARN rather than paper over it with local. Local CSV is an EMERGENCY fallback only, used
    #  solely when the BQ read itself fails, and announced loudly.)
    try:
        sf = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s
WHERE s.time BETWEEN DATE '{qstart}' AND DATE '{end}' ORDER BY s.time""")
        sf["time"] = pd.to_datetime(sf["time"])
        if len(sf) == 0:
            raise RuntimeError("BQ base state `vnindex_5state_tam_quan_v34b_clean` returned 0 rows")
        _bmax = sf["time"].max()
        if _bmax < pd.Timestamp(end):
            print(f"[get_macro_state] WARNING: BQ base state max={_bmax.date()} < requested end={end} "
                  f"→ base is STALE. Run the v3.4b refresh+deploy chain. (NOT falling back to local.)")
    except Exception as e:
        _base_csv = os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
        print(f"[get_macro_state] WARNING: BQ base read failed ({e}) → EMERGENCY local-CSV fallback "
              f"{_base_csv} (results may NOT reconcile with BQ — fix BQ access).")
        sf = pd.read_csv(_base_csv)
        sf["time"] = pd.to_datetime(sf["time"])
        sf = sf[(sf["time"] >= pd.Timestamp(qstart)) & (sf["time"] <= pd.Timestamp(end))]
    sf = sf.sort_values("time").reset_index(drop=True)
    sf["state_dt"] = _dt_4gate(sf["state"].values.astype(int))

    # ── VNINDEX price + MA200/RSI (for bull-flag + base) ──
    px = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{qstart}' AND DATE '{end}' ORDER BY t.time""")
    px["time"] = pd.to_datetime(px["time"])
    df = px.merge(sf[["time", "state_dt"]], on="time", how="left")
    df["state_dt"] = df["state_dt"].ffill()
    df = df.dropna(subset=["state_dt"]).reset_index(drop=True); df["state_dt"] = df["state_dt"].astype(int)

    # ── Pillar B: US VIX/SPX, aligned to VN T-1 ──
    us = pd.read_csv(os.path.join(WORKDIR, "data/us_market_history.csv"), parse_dates=["time"]).sort_values("time")
    key = df[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
    um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                       left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
    df = df.merge(um[["time", "vix", "spx_dd_1y", "vix_ma252"]], on="time", how="left")

    # ── Pillar A: SBV refi 6m-momentum (+ lag) ──
    ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
    dr = pd.DataFrame({"time": pd.date_range(df["time"].min(), df["time"].max(), freq="D")}).merge(ev, on="time", how="left")
    dr["refi"] = dr["refi"].ffill().bfill()
    df = df.merge(dr, on="time", how="left"); df["refi"] = df["refi"].ffill().bfill()
    df["refi_chg6m"] = (df["refi"] - df["refi"].shift(P["refi_chg_win"])).shift(P["refi_lag"])
    peak = df["refi"].rolling(P["refi_chg_win"], min_periods=20).max()
    df["refi_cut"] = ((peak - df["refi"]) >= P["refi_cut_drop"]).shift(P["refi_lag"]).fillna(False)
    df["bull"] = ((df["Close"] / df["Close"].shift(P["refi_chg_win"]) - 1 > P["bull_r6m"]) & (df["Close"] > df["MA200"])).shift(1).fillna(False)

    # ── VN-BREADTH DECOUPLING GUARD on Pillar B (free insurance, 2026-05-29) ──
    # Suppress the US-panic cap ONLY when VN breadth is broadly HEALTHY while the US panics
    # (genuine US-VN decoupling, e.g. 2025 VIC-led). FAIL-SAFE: weak / missing / small-universe
    # breadth => NO suppression => US cap fires as usual (never skip crisis protection on a data
    # gap). Breadth = % of ticker_prune above MA200 (the production breadth universe). Causal (T-1).
    df["us_decoupled"] = False
    try:
        bd = bq(f"""SELECT t.time, AVG(IF(t.Close>t.MA200,1.0,0.0)) AS b200, COUNT(*) AS univ
FROM tav2_bq.ticker AS t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.MA200 IS NOT NULL AND t.time BETWEEN DATE '{qstart}' AND DATE '{end}'
GROUP BY t.time ORDER BY t.time""")
        bd["time"] = pd.to_datetime(bd["time"])
        df = df.merge(bd, on="time", how="left")
        decoup = ((df["univ"].fillna(0) >= P["breadth_min_univ"]) & (df["b200"] >= P["breadth_th"])).shift(1).fillna(False)
        df["us_decoupled"] = decoup.values
    except Exception as e:
        print(f"[get_macro_state] breadth guard inactive ({e}) -> US pillar ungated (fail-safe)")

    # ── fuse to cap level + easing (causal) ──
    n = len(df); vix = df["vix"].values; sdd = df["spx_dd_1y"].values; vma = df["vix_ma252"].values
    rc6 = df["refi_chg6m"].values; cut = df["refi_cut"].values.astype(bool); bull = df["bull"].values.astype(bool)
    decoup = df["us_decoupled"].values.astype(bool)
    close = df["Close"].values
    cap = np.full(n, 9); easing = np.zeros(n, bool)
    for t in range(n):
        v, dd, vm, rr = vix[t], sdd[t], vma[t], rc6[t]
        if bull[t] or decoup[t]:          # Pillar B bypassed in VN bull OR US-VN decoupling (breadth guard)
            uc = ub = umild = False
        else:
            uc = (not np.isnan(dd) and dd < P["spx_crisis"]) or (not np.isnan(v) and v > P["vix_crisis"])
            ub = (not np.isnan(dd) and dd < P["spx_bear"]) and (not np.isnan(v) and v > P["vix_bear"])
            umild = (not np.isnan(dd) and dd < P["spx_mild"]) and (not np.isnan(v) and v > P["vix_mild"])
        de = (not np.isnan(rr) and rr >= P["dom_extreme"]); ds = (not np.isnan(rr) and rr >= P["dom_strong"])
        dm = (not np.isnan(rr) and rr >= P["dom_mild"])
        if uc or de: cap[t] = CRISIS
        elif ub or ds: cap[t] = BEAR
        elif umild or dm: cap[t] = NEUTRAL
        calm = (not np.isnan(v) and not np.isnan(vm) and v < vm) and (not np.isnan(dd) and dd > -0.05)
        if cap[t] == 9 and cut[t] and calm: easing[t] = True
    persist = np.zeros(n, int)
    for t in range(n):
        persist[t] = persist[t-1] + 1 if (t > 0 and easing[t]) else (1 if easing[t] else 0)
    lb = P["ez_price_lb"]; pup = np.zeros(n, bool); pup[lb:] = close[lb:] > close[:-lb]
    ez = easing & (persist >= P["ez_confirm"]) & pup

    cap = _commit(cap, P["cap_commit"])   # debounce defensive cap (anti-whipsaw)
    st = df["state_dt"].values
    sm = np.where(cap != 9, np.minimum(st, cap), st).astype(int)
    # ── EASING FLOOR — DISABLED 2026-06-03 (ASYMMETRY principle) ──────────────────────────────
    # The macro overlay is now PURELY DEFENSIVE: it CAPS the state ceiling on stress (de-risk) but
    # NO LONGER FLOORS it back up on a monetary-easing signal. Re-risk happens ONLY via the
    # price-based DT base (slow, price-confirmed) — never on rate cuts alone.
    # WHY: SBV cutting from a peak happens DURING a bear (2012: 15%->9%), so a "recovery floor" on
    # that signal catches falling knives. Event audit (gen_noeasing_transitions_html.py): of the 13
    # historical easing-lift windows, 11 had NEGATIVE fwd-60d (2012-05 -13%, Aug-2012 -12%); only the
    # 2014-05 V-recovery was correctly caught. The floor is also DORMANT in the discrete production
    # state since 2014-06 (0 change-windows) => disabling it is a zero-behavior-change cleanup for the
    # live era that removes a fragile, historically net-negative leg. Full-history backtest: disabling
    # improves Full CAGR 19.93->20.05%, Sharpe 1.36->1.37, same MaxDD; 2012 +6.95pp.
    # `easing` (ez) is still COMPUTED and returned for transparency/ablation; it is NOT applied.
    EASING_FLOOR_ENABLED = False
    if EASING_FLOOR_ENABLED:
        sm = np.where((cap == 9) & ez & (sm < NEUTRAL), NEUTRAL, sm).astype(int)

    out = pd.DataFrame({"time": df["time"], "state": sm, "state_dt4": st,
                        "cap": cap, "easing": ez})
    out = out[out["time"] >= pd.Timestamp(start)].reset_index(drop=True)
    return out


def get_gated_state(start, end, bq=None, health_path=None, max_health_age_min=1440):
    """FAIL-SAFE production state source. Returns the macro (DT5G) state ONLY when the
    latest macro_healthcheck.py report says the feeds are trustworthy; otherwise reverts
    to DT4-only (the base state). Fail-CLOSED: a missing / stale / FAILED health report
    => DT4_only (never trust a stale or broken macro cap).

    Returns DataFrame[time, state, base_state, macro_state, source]; production code should
    consume the `state` column. `source` ∈ {DT5G_macro, DT4_only}. Reason is printed.
    """
    import json, os
    from datetime import datetime
    if health_path is None:
        health_path = os.path.join(WORKDIR, "data", "macro_health.json")
    m = get_macro_state(start, end, bq=bq)          # has BOTH 'state' (macro) and 'state_dt4' (base)
    use_macro, reason = False, "no health report -> DT4_only (fail-closed)"
    try:
        h = json.load(open(health_path, encoding="utf-8"))
        age_min = (datetime.now() - datetime.fromisoformat(h["ts"])).total_seconds() / 60.0
        if age_min > max_health_age_min:
            reason = f"health report {age_min:.0f}min old (> {max_health_age_min}) -> DT4_only"
        elif h.get("status") != "FAILED" and h.get("recommended_state_source") == "DT5G_macro":
            use_macro, reason = True, f"health={h.get('status')} -> DT5G_macro"
        else:
            reason = f"health={h.get('status')} rec={h.get('recommended_state_source')} -> DT4_only"
    except Exception as e:
        reason = f"health report unreadable ({e}) -> DT4_only"
    src = "DT5G_macro" if use_macro else "DT4_only"
    chosen = (m["state"] if use_macro else m["state_dt4"]).astype(int)
    out = pd.DataFrame({"time": m["time"], "state": chosen,
                        "base_state": m["state_dt4"].astype(int),
                        "macro_state": m["state"].astype(int), "source": src})
    print(f"[get_gated_state] {src}: {reason}")
    return out


if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    start = os.environ.get("START_DATE", "2026-01-01"); end = os.environ.get("END_DATE", "2026-05-26")
    m = get_macro_state(start, end)
    diff = int((m["state"] != m["state_dt4"]).sum())
    print(f"macro_state_live {start}->{end}: {len(m)} rows, {diff} days macro differs from DT4 "
          f"({int((m['state']<m['state_dt4']).sum())} de-risk, {int((m['state']>m['state_dt4']).sum())} re-risk)")
    print(f"  latest: {m['time'].iloc[-1].date()} state={int(m['state'].iloc[-1])} "
          f"(DT4={int(m['state_dt4'].iloc[-1])}, cap={int(m['cap'].iloc[-1])}, easing={bool(m['easing'].iloc[-1])})")
    print(m.tail(8).to_string(index=False))
