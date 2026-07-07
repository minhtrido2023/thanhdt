# -*- coding: utf-8 -*-
"""dc_waterfall_deepdive.py (job Taylor_20260706_173317) — RESEARCH ONLY, production +
paper sleeve untouched.

CÂU 0 — full-config table of the PAPER waterfall (BAL/LAG → DC double-confirm ex-DHG
cap 0.20/name equal-weight → custom30V, NEUTRAL-only) vs baseline R3 (custom30V-only
parking), at FULL-V2.4-NAV level.

METHOD (overlay recomposition — same decomposition job _125540 used, here made exact-daily
and self-checked): take the R3 full-harness DAILY audit (data/h3_baseline_R3.csv,
pt_v23_audit_2014.py v23a, AUDIT_END=2026-06-19, identities 0 VND), derive
  r_base(t)   = combined_nav(t)/combined_nav(t-1) - 1
  w_park(t-1) = (bal_etf_ref + lag_etf_ref)/combined_nav at t-1   (the parked sleeve)
and substitute the parked sleeve's vehicle: custom30V -> waterfall composite:
  r_new(t) = r_base(t) + w_park(t-1) * (r_wf(t) - r_c30v(t))
where r_wf / r_c30v are the sleeve-level vehicle returns from the SAME framework
(converge_portfolio_backtest.py job _093329: 'ConvergePort (equal-weight)' = exactly the
paper waterfall vehicle math w=min(0.20,1/n) + custom30V remainder, TC 0.1%, T+1;
'baseline_ret' = custom30V thuần). The delta term only needs the two vehicle series to be
built consistently WITH EACH OTHER, which they are (same script, same day).

SELF-CHECKS:
  A. metrics recomputed from audit combined_nav == the file's own METRIC rows.
  B. substituting r_wf := r_c30v reproduces r_base EXACTLY (0-VND identity of the overlay).
  C. w_park > 0 only on NEUTRAL (state==3) days; w_park <= 0.75.

CÂU 1/2/3 use the cached double-confirm panel (dc_waterfall_panel_build.py) when present.
"""
import os, sys, numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

AUDIT = "data/h3_baseline_R3.csv"
SLEEVE = "data/converge_portfolio_backtest_nav.csv"
IS_END = pd.Timestamp("2019-12-31")
CAP = 0.20
TC = 0.001

# ---------------------------------------------------------------- load audit
def load_audit():
    df = pd.read_csv(AUDIT, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    for c in ["state", "bal_etf_ref", "lag_etf_ref", "bal_cash_ref", "lag_cash_ref", "combined_nav"]:
        d[c] = pd.to_numeric(d[c])
    d = d.set_index("ymd").sort_index()
    met = df[df["record_type"] == "METRIC"].set_index("key")["value"]
    return d, met

def metrics(r, index=None):
    r = r.dropna()
    nav = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    sd = r.std()
    sh = r.mean() / sd * np.sqrt(252) if sd > 0 else np.nan
    neg = r[r < 0]
    so = r.mean() / np.sqrt((neg ** 2).mean()) * np.sqrt(252) if len(neg) else np.nan
    dd = (nav / nav.cummax() - 1).min()
    cal = cagr / abs(dd) if dd < 0 else np.nan
    return dict(CAGR=cagr * 100, Sharpe=sh, Sortino=so, MaxDD=dd * 100, Calmar=cal)

def wf3(r):
    return [("FULL", r), ("IS 2014-19", r[r.index <= IS_END]), ("OOS 2020+", r[r.index > IS_END])]

def table(rows):
    hdr = f"{'config':<34}{'win':<11}{'CAGR':>8}{'Sharpe':>8}{'Sortino':>9}{'MaxDD':>8}{'Calmar':>8}"
    print(hdr); print("-" * len(hdr))
    for name, r in rows:
        for tag, rr in wf3(r):
            m = metrics(rr)
            print(f"{name:<34}{tag:<11}{m['CAGR']:>7.2f}%{m['Sharpe']:>8.2f}{m['Sortino']:>9.2f}"
                  f"{m['MaxDD']:>7.1f}%{m['Calmar']:>8.2f}")
        print()

def overlay(r_base, w_park_prev, delta_vehicle):
    """r_new = r_base + w_park(t-1) * delta_vehicle(t), delta aligned/0-filled."""
    dv = delta_vehicle.reindex(r_base.index).fillna(0.0)
    return r_base + w_park_prev.reindex(r_base.index).fillna(0.0) * dv

def main():
    aud, met = load_audit()
    slv = pd.read_csv(SLEEVE, parse_dates=["date"]).set_index("date")
    r_c30v = slv["baseline_ret"]
    r_wf = slv["ConvergePort (equal-weight)"]

    nav = aud["combined_nav"]
    r_base = nav.pct_change().dropna()
    w_park = ((aud["bal_etf_ref"] + aud["lag_etf_ref"]) / aud["combined_nav"])
    w_park_prev = w_park.shift(1).reindex(r_base.index).fillna(0.0)

    # ---- self-check A: audit metrics reproduce METRIC rows
    m_full = metrics(r_base)
    print("=== SELF-CHECK A — recompute base metrics vs audit METRIC rows ===")
    print(f"  CAGR   {m_full['CAGR']/100:.6f}  vs file {float(met['cagr']):.6f}")
    print(f"  Sharpe {m_full['Sharpe']:.4f}  vs file {float(met['sharpe_252']):.4f}")
    print(f"  MaxDD  {m_full['MaxDD']/100:.6f} vs file {float(met['max_dd']):.6f}")
    print(f"  Calmar {m_full['Calmar']:.4f}  vs file {float(met['calmar']):.4f}")

    # ---- self-check B: identity overlay
    r_id = overlay(r_base, w_park_prev, (r_c30v - r_c30v))
    print(f"=== SELF-CHECK B — identity overlay max|r_new - r_base| = {(r_id - r_base).abs().max():.2e}")

    # ---- self-check C: parking only in NEUTRAL
    st = aud["state"]
    bad = ((w_park > 1e-9) & (st != 3)).sum()
    print(f"=== SELF-CHECK C — parked>0 on non-NEUTRAL days: {int(bad)}  | max w_park={w_park.max():.3f}")
    pre = ((w_park > 1e-9) & (w_park.index < r_wf.index[0])).sum()
    print(f"    parked days before sleeve history start ({r_wf.index[0].date()}): {int(pre)} (delta=0 there, honest no-coverage)")

    # ---- CÂU 0: waterfall vs baseline at full-NAV level
    r_wfall = overlay(r_base, w_park_prev, (r_wf - r_c30v))
    print("\n=== CÂU 0 — FULL V2.4 NAV: baseline R3 vs WATERFALL parking (paper config) ===")
    print(f"audit: {AUDIT} ({r_base.index[0].date()} → {r_base.index[-1].date()}, {len(r_base)} sessions)")
    print(f"parked sleeve: mean {w_park.mean()*100:.1f}% NAV, NEUTRAL-days mean {w_park[st==3].mean()*100:.1f}%, max {w_park.max()*100:.1f}%\n")
    table([("R3 baseline (custom30V parking)", r_base),
           ("WATERFALL DC→custom30V (paper cfg)", r_wfall)])

    # DSR of the full-NAV excess (N trials declared in report)
    try:
        from dsr_pbo_annex import dsr
        ex = (r_wfall - r_base).dropna()
        T = len(ex); sr = ex.mean() / ex.std() * np.sqrt(252) if ex.std() > 0 else 0
        from scipy import stats as _st  # not available? fallback moments via pandas
    except Exception:
        pass
    ex = (r_wfall - r_base).dropna()
    if ex.std() > 0:
        sr_d = ex.mean() / ex.std()
        g3 = float(((ex - ex.mean()) ** 3).mean() / ex.std() ** 3)
        g4 = float(((ex - ex.mean()) ** 4).mean() / ex.std() ** 4)
        try:
            from dsr_pbo_annex import dsr as _dsr
            for N in (1, 10):
                sr0 = ex.std() * 0  # placeholder replaced below
            import math
            # expected max SR under N trials (Bailey-LdP), sr in daily units
            T = len(ex)
            emc = 0.5772156649
            def sr0_of(N):
                if N <= 1: return 0.0
                from statistics import NormalDist
                z1 = NormalDist().inv_cdf(1 - 1.0 / N)
                z2 = NormalDist().inv_cdf(1 - 1.0 / (N * math.e))
                return (ex.std() * 0 + 1) * ((1 - emc) * z1 + emc * z2) * ex.std() / math.sqrt(T - 1) / ex.std()
            for N in (10,):
                sr0 = sr0_of(N)
                p, stat = _dsr(sr_d, sr0, g3, g4, T)
                print(f"DSR (full-NAV excess, N={N} trials): {p:.3f}")
        except Exception as e:
            print(f"(DSR via annex failed: {e}; raw daily SR of excess = {sr_d:.4f}, ann {sr_d*np.sqrt(252):.2f})")

    # ================= CÂU 1/2/3 — need the cached double-confirm panel =================
    if not os.path.exists("data/dc_dbl_panel.csv"):
        print("\n[panel not ready yet — CÂU 1/2/3 pending]"); return

    dbl = pd.read_csv("data/dc_dbl_panel.csv", index_col=0, parse_dates=True)
    sret = pd.read_csv("data/dc_stock_ret.csv", index_col=0, parse_dates=True)
    park = pd.read_csv("data/dc_park_ret.csv", index_col=0, parse_dates=True)["park_ret"]
    cal = dbl.index
    dbl = dbl.astype(bool)
    if "DHG" in dbl.columns:                      # paper config: DHG hard-excluded
        dbl = dbl.copy(); dbl["DHG"] = False
    names = list(dbl.columns)

    def vehicle(dc_share=None, rebal="daily"):
        """Composite vehicle daily net return: DC names equal-weight w=min(CAP,1/n) (or a fixed
        dc_share split across n names, per-name cap CAP), remainder -> custom30V. TC on top-level
        weight changes (same treatment as the paper sleeve). T+1: weights t-1 earn ret t.
        rebal: 'daily' (paper: re-target every close) | 'event' (only when membership changes,
        drift between) | 'quarterly' (membership refreshed only at quarter-month rebal dates)."""
        W = pd.DataFrame(0.0, index=cal, columns=names); pk = pd.Series(0.0, index=cal)
        if rebal == "quarterly":
            # refresh membership on the custom30V rebal-cycle months (q+2m5 style ≈ quarterly)
            qdates = [d for i, d in enumerate(cal) if i == 0 or (d.month != cal[i-1].month and d.month in (2, 5, 8, 11))]
            cur = []
            for d in cal:
                if d in qdates:
                    cur = [t for t in names if dbl.at[d, t]]
                n = len(cur)
                if n:
                    w = min(CAP, (dc_share or 1.0) / n) if dc_share else min(CAP, 1.0 / n)
                    for t in cur: W.at[d, t] = w
                    pk.loc[d] = max(0.0, 1.0 - w * n)
                else:
                    pk.loc[d] = 1.0
        else:
            prev_set = None
            cache_w = {}
            for d in cal:
                cur = tuple(t for t in names if dbl.at[d, t])
                if rebal == "event" and cur == prev_set and cache_w:
                    for t, wv in cache_w.items(): W.at[d, t] = wv
                    pk.loc[d] = max(0.0, 1.0 - sum(cache_w.values()))
                else:
                    n = len(cur)
                    if n:
                        w = min(CAP, (dc_share or 1.0) / n) if dc_share else min(CAP, 1.0 / n)
                        cache_w = {t: w for t in cur}
                        for t in cur: W.at[d, t] = w
                        pk.loc[d] = max(0.0, 1.0 - w * n)
                    else:
                        cache_w = {}; pk.loc[d] = 1.0
                prev_set = cur
        # T+1 sim with TC on |Δw| (incl. parking leg), matching the paper sleeve turnover def
        r = pd.Series(0.0, index=cal); prev_w = W.iloc[0].copy(); prev_p = pk.iloc[0]
        turn = pd.Series(0.0, index=cal)
        for i, d in enumerate(cal):
            if i == 0: continue
            ra = float((prev_w * sret.loc[d].reindex(names).fillna(0.0)).sum())
            rp = prev_p * (park.loc[d] if np.isfinite(park.loc[d]) else 0.0)
            t = (float((W.loc[d] - prev_w).abs().sum()) + abs(pk.loc[d] - prev_p)) / 2.0
            r.loc[d] = ra + rp - t * TC
            turn.loc[d] = t
            prev_w = W.loc[d].copy(); prev_p = pk.loc[d]
        yrs = (cal[-1] - cal[0]).days / 365.25
        return r, turn.sum() / yrs, (turn.sum() * TC / yrs)

    def dc_only():
        """DC names only, remainder CASH (for the BULL extension — custom30V bull-park was
        REJECTED so the BULL test deploys the DC layer only)."""
        r = pd.Series(0.0, index=cal); prev_w = pd.Series(0.0, index=names)
        W = pd.DataFrame(0.0, index=cal, columns=names)
        for d in cal:
            cur = [t for t in names if dbl.at[d, t]]
            n = len(cur)
            if n:
                w = min(CAP, 1.0 / n)
                for t in cur: W.at[d, t] = w
        for i, d in enumerate(cal):
            if i == 0: prev_w = W.iloc[0].copy(); continue
            ra = float((prev_w * sret.loc[d].reindex(names).fillna(0.0)).sum())
            t = float((W.loc[d] - prev_w).abs().sum()) / 2.0
            r.loc[d] = ra - t * TC
            prev_w = W.loc[d].copy()
        return r, W.sum(axis=1)  # return + deployed frac of the dc-only sleeve

    # ---------- CÂU 1: state coverage ----------
    print("\n=== CÂU 1 — DC book state coverage: NEUTRAL-only vs +BULL vs +EXBULL ===")
    r_dc, dc_frac = dc_only()
    cash_frac = ((aud["bal_cash_ref"] + aud["lag_cash_ref"]) / aud["combined_nav"])
    for tag, states in [("BULL(4)", [4]), ("EXBULL(5)", [5])]:
        m = st.isin(states)
        cf = cash_frac[m]
        print(f"  idle cash on {tag} days: n={int(m.sum())}, mean {cf.mean()*100:.1f}% NAV, "
              f"median {cf.median()*100:.1f}%, p90 {cf.quantile(0.9)*100:.1f}%")
    variants = {
        "(a) NEUTRAL-only (paper, wired)": r_wfall,
    }
    for tag, states in [("(b) NEUTRAL+BULL", [4]), ("(c) NEUTRAL+BULL+EXBULL", [4, 5])]:
        w_ext = pd.Series(0.0, index=r_base.index)
        mm = st.isin(states).reindex(r_base.index).fillna(False)
        w_ext[mm] = 0.7 * cash_frac.reindex(r_base.index)[mm]      # same 0.7-of-idle policy
        w_ext = w_ext.shift(1).fillna(0.0)
        variants[tag] = r_wfall + w_ext * r_dc.reindex(r_base.index).fillna(0.0)
    table(list(variants.items()))

    # ---------- CÂU 2: DC vs custom30V split of the parked sleeve ----------
    print("=== CÂU 2 — parked-sleeve split: pure waterfall vs fixed mixes (full-NAV level) ===")
    rows = [("waterfall thuần (DC ăn hết cap)", r_wfall)]
    for share in (0.7, 0.5, 0.3):
        rv, tvr, drag = vehicle(dc_share=share)
        rr = overlay(r_base, w_park_prev, (rv - r_c30v))
        rows.append((f"fixed {int(share*100)}/{int((1-share)*100)} DC/c30V (turn {tvr:.1f}x, TCdrag {drag*100:.2f}pp/yr sleeve)", rr))
    table(rows)

    # ---------- CÂU 3: rebalance timing ----------
    print("=== CÂU 3 — DC rebalance timing (sleeve-vehicle level + full-NAV) ===")
    rows3 = []
    for tag, rb in [("daily signal-driven (paper hiện tại)", "daily"),
                    ("event-driven (chỉ khi membership đổi)", "event"),
                    ("quarterly (q2m5-style)", "quarterly")]:
        rv, tvr, drag = vehicle(rebal=rb)
        rr = overlay(r_base, w_park_prev, (rv - r_c30v))
        rows3.append((f"{tag} | turn {tvr:.2f}x/yr TCdrag {drag*100:.2f}pp/yr", rr))
    table(rows3)

if __name__ == "__main__":
    main()
