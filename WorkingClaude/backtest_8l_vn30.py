#!/usr/bin/env python3
"""backtest_8l_vn30.py — does a liquidity-screened 8L-quality 30-stock basket beat VN30?

Point-in-time PROXY of the 8L thesis (route-aware quality + cheap-vs-own-history + dislocation),
since the live 8L composite is a current snapshot only. Built from PIT columns in tav2_bq.ticker
(panel pulled to data/panel_8l_quarterly.csv): ROE_Min5Y, ROIC5Y, FSCORE, PB/PB_MA5Y/PB_SD5Y (->pb_z),
PE/PE_MA5Y/PE_SD5Y (->pe_z), Close/HI_3M_T1 (->dd), Volume_3M_P50*Price (->liquidity).

Construction (quarterly rebalance, 2014Q1 -> 2026Q1):
  • Eligible universe = liquidity >= LIQ_FLOOR (10B VND/day) AND has 5Y quality history (ROE_Min5Y not null).
  • Score = weighted sum of CROSS-SECTIONAL PERCENTILE RANKS within that quarter's eligible set
    (rank-based => immune to the fundamental-column outliers in early years):
        quality:     1.0*pr(ROE_Min5Y) + 0.7*pr(ROIC5Y) + 0.5*pr(FSCORE)
        cheap-vs-hist: 1.0*pr(-pb_z)    + 0.6*pr(-pe_z)
        dislocation: 0.5*pr(-dd3m)        (deeper drawdown ranks higher; only pays off for quality names
                                           because the quality terms dominate junk)
  • Pick top 30 -> "8L-VN30". Two weightings: EW and liquidity-weight.
Benchmark VN30-proxy = top-30 by liquidity (no quality screen), EW and liq-weight (liq-weight ~ the real
cap/liquidity-weighted VN30). VNINDEX buy&hold added separately.

Returns: adjusted Close (= total-return proxy) quarter-end to quarter-end. TC charged on turnover.
Metrics: CAGR, vol, Sharpe, MaxDD (quarterly freq), Calmar, annual table, win-rate vs benchmark.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PANEL = os.path.join(WORKDIR, "data", "panel_8l_quarterly.csv")
LIQ_FLOOR = 10e9          # 10B VND/day
N8L = int(sys.argv[1]) if len(sys.argv) > 1 else 30   # 8L basket size (benchmark VN30 fixed at 30)
TOPN = 30                 # VN30-proxy size (definition of VN30)
TC = 0.0020               # 0.20% on traded portion (turnover) per rebalance, one-way
W = dict(roe=1.0, roic=0.7, fscore=0.5, pb=1.0, pe=0.6, dd=0.5)

def pr(s):
    """cross-sectional percentile rank 0..1; NaN -> 0.5 (neutral)."""
    r = s.rank(pct=True)
    return r.fillna(0.5)

def load():
    df = pd.read_csv(PANEL)
    df["time"] = pd.to_datetime(df["time"])
    df["qtr"] = pd.to_datetime(df["qtr"])
    df["liq"] = df["Volume_3M_P50"] * df["Price"].fillna(df["Close"])
    df["pb_z"] = (df["PB"] - df["PB_MA5Y"]) / df["PB_SD5Y"].replace(0, np.nan)
    df["pe_z"] = (df["PE"] - df["PE_MA5Y"]) / df["PE_SD5Y"].replace(0, np.nan)
    df["dd3m"] = df["Close"] / df["HI_3M_T1"].replace(0, np.nan) - 1
    df = df[(df["Close"] > 0)].copy()
    # ── attach PIT bank fundamentals (NPL/cov/ROE) by release date (eff_time<=rebalance) ──
    bp = os.path.join(WORKDIR, "data", "bank_rating_history.csv")
    if os.path.exists(bp):
        br = pd.read_csv(bp)
        br["eff_time"] = pd.to_datetime(br["eff_time"])
        br = br.sort_values("eff_time")[["ticker", "eff_time", "ROE", "NPL", "cov"]]
        br = br.rename(columns={"ROE": "bROE", "NPL": "bNPL", "cov": "bcov"})
        df = df.sort_values("time")
        df = pd.merge_asof(df, br, by="ticker", left_on="time", right_on="eff_time",
                           direction="backward")
    else:
        df["bROE"] = df["bNPL"] = df["bcov"] = np.nan
    return df

BANK_ICB = {8355}   # ICB 8355 = Banks (VCB/CTG/ACB/MBB/... verified PIT)
NB_SCALE = 95.0     # map the non-bank 0..sum(W) composite onto a 0..95 absolute scale (≈ rank_8l range)

def bank_score(g):
    """Faithful rank_8l BANK lens on PIT data: gate(NPL) + npl + coverage + ROE + PB/ROE.
    Uses released bank fundamentals (bNPL/bcov/bROE, 2018+); pre-2018 falls back to ROE_Min5Y+PB."""
    npl = g["bNPL"] * 100.0          # fraction -> %
    cov = g["bcov"]                  # ratio (1.35 = 135%)
    roe = g["bROE"]
    pb = g["PB"].replace(0, np.nan)
    rpb = roe * 100.0 / pb
    gate = np.select([npl < 1.5, npl < 2.5], [40, 20], default=-10)
    nplb = np.select([npl < 1, npl < 1.5, npl < 2, npl < 2.5, npl < 3], [15, 12, 8, 4, 2], default=-5)
    covb = np.select([cov >= 1.5, cov >= 1.0, cov >= 0.8, cov >= 0.5], [10, 8, 5, 2], default=0)
    roeb = np.select([roe >= 0.20, roe >= 0.17, roe >= 0.14, roe >= 0.10], [10, 8, 5, 2], default=0)
    rpbb = np.select([rpb >= 15, rpb >= 12, rpb >= 10], [10, 7, 4], default=1)
    sc = gate + nplb + covb + roeb + rpbb
    # pre-2018 fallback (no released NPL): assume CLEAN-ish liquid bank, score on ROE_Min5Y + PB/ROE
    rpb_fb = g["ROE_Min5Y"] * 100.0 / pb
    fb = 30 + np.select([g["ROE_Min5Y"] >= 0.18, g["ROE_Min5Y"] >= 0.12], [15, 8], default=0) \
            + np.select([rpb_fb >= 12, rpb_fb >= 9], [10, 6], default=2)
    return pd.Series(np.where(g["bNPL"].notna(), sc, fb), index=g.index)

def quality_screen_nb(g):
    """Non-bank quality gate (drop deep-value junk & cyclical-trough the proxy can't time PIT)."""
    return ((g["ROE_Min5Y"] >= 0.12) & (g["FSCORE"] >= 4)) | (g["ROIC5Y"] >= 0.12)

def score_quarter(g):
    """Route-aware score on a common ~0-95 scale: banks via faithful bank lens; non-banks via
    percentile composite (quality+cheap-vs-history+dislocation) rescaled to match."""
    g = g.copy()
    is_bank = g["ICB_Code"].isin(BANK_ICB)
    s_nb = (W["roe"]*pr(g["ROE_Min5Y"]) + W["roic"]*pr(g["ROIC5Y"].clip(-1, 1)) +
            W["fscore"]*pr(g["FSCORE"]) + W["pb"]*pr(-g["pb_z"]) +
            W["pe"]*pr(-g["pe_z"]) + W["dd"]*pr(-g["dd3m"]))
    nb_abs = (s_nb / sum(W.values())) * NB_SCALE
    g["s"] = np.where(is_bank, bank_score(g), nb_abs)
    g["is_bank"] = is_bank
    return g

def build_baskets(df):
    """Return dict qtr -> {basket_name: DataFrame[ticker, weight]}."""
    qs = sorted(df["qtr"].unique())
    out = {}
    for q in qs:
        g = df[df["qtr"] == q]
        liq_elig = g[g["liq"] >= LIQ_FLOOR].copy()
        if len(liq_elig) < TOPN:
            continue
        # --- 8L-VN30: banks (own lens) + quality-screened non-banks, ranked on common scale ---
        cand = liq_elig[liq_elig["ROE_Min5Y"].notna()].copy()
        is_bank = cand["ICB_Code"].isin(BANK_ICB)
        cand = cand[is_bank | quality_screen_nb(cand)]
        if len(cand) < 10:
            continue
        q8 = score_quarter(cand).sort_values("s", ascending=False).head(N8L)
        # --- VN30-proxy: top-30 by liquidity, no quality screen ---
        vp = liq_elig.sort_values("liq", ascending=False).head(TOPN).copy()
        def mk(sub, lw):
            w = (sub["liq"] / sub["liq"].sum()) if lw else pd.Series(1/len(sub), index=sub.index)
            return pd.DataFrame({"ticker": sub["ticker"].values, "weight": w.values,
                                 "Close": sub["Close"].values})
        out[q] = {
            "8L_EW":   mk(q8, False), "8L_LIQ":  mk(q8, True),
            "VN30_EW": mk(vp, False), "VN30_LIQ": mk(vp, True),
            "_nbank": int(q8["ICB_Code"].isin(BANK_ICB).sum()),
        }
    return out, qs

def load_state():
    p = os.path.join(WORKDIR, "data", "state_qtr.csv")
    if not os.path.exists(p): return {}
    s = pd.read_csv(p); s["qtr"] = pd.to_datetime(s["qtr"])
    return dict(zip(s["qtr"], s["state"]))

def run_strategy(baskets, qs, name, df, timing=None):
    """Chain quarterly returns for one basket variant. timing: dict qtr->state; if provided, hold
    CASH (0% return) for any quarter whose START state is BEAR(2)/CRISIS(1)."""
    closes = {q: df[df["qtr"] == q].set_index("ticker")["Close"] for q in qs}
    rebal_qs = [q for q in qs if q in baskets]
    navs = [1.0]; idx = [rebal_qs[0]]
    prev_w = pd.Series(dtype=float); miss = 0; turn_tot = 0.0
    for i, q in enumerate(rebal_qs[:-1]):
        nxt = rebal_qs[i+1]
        in_cash = timing is not None and int(timing.get(pd.Timestamp(q), 3)) in (1, 2)
        if in_cash:
            cur_w = pd.Series(dtype=float)          # flat
            port_ret = 0.0
            turn = prev_w.abs().sum()               # exit cost
        else:
            bk = baskets[q][name].set_index("ticker")
            ret = closes[nxt].reindex(bk.index) / bk["Close"] - 1
            miss += int(ret.isna().sum()); ret = ret.fillna(0.0)
            port_ret = float((bk["weight"] * ret).sum())
            cur_w = bk["weight"]
            turn = cur_w.subtract(prev_w, fill_value=0).abs().sum() if len(prev_w) else 1.0
        turn_tot += turn; port_ret -= TC * turn; prev_w = cur_w
        navs.append(navs[-1] * (1 + port_ret)); idx.append(nxt)
    return pd.Series(navs, index=pd.to_datetime(idx), name=name), miss, turn_tot

def vnindex_nav(qs):
    """VNINDEX buy&hold quarter-end NAV from the panel's implied index (pull separately)."""
    p = os.path.join(WORKDIR, "data", "vnindex_qtr.csv")
    if not os.path.exists(p): return None
    v = pd.read_csv(p); v["qtr"] = pd.to_datetime(v["qtr"])
    v = v.set_index("qtr")["vnindex"].reindex(pd.to_datetime(qs)).dropna()
    return (v / v.iloc[0]).rename("VNINDEX")

def metrics(nav):
    nav = nav.dropna()
    rq = nav.pct_change().dropna()
    n_years = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1/n_years) - 1
    vol = rq.std() * np.sqrt(4)
    sharpe = (rq.mean()*4) / vol if vol > 0 else np.nan
    roll_max = nav.cummax(); dd = nav/roll_max - 1; maxdd = dd.min()
    calmar = cagr / abs(maxdd) if maxdd < 0 else np.nan
    return dict(CAGR=cagr, Vol=vol, Sharpe=sharpe, MaxDD=maxdd, Calmar=calmar,
                Finalx=nav.iloc[-1], years=n_years)

def annual_table(navs):
    """Year-end NAV -> calendar-year returns per strategy."""
    out = {}
    for name, nav in navs.items():
        ye = nav.groupby(nav.index.year).last()
        out[name] = ye.pct_change()
    return pd.DataFrame(out)

def main():
    df = load()
    baskets, qs = build_baskets(df)
    state = load_state()
    variants = ["8L_EW", "8L_LIQ", "VN30_EW", "VN30_LIQ"]
    navs = {}; info = {}
    for v in variants:
        nav, miss, turn = run_strategy(baskets, qs, v, df)
        navs[v] = nav; info[v] = (miss, turn)
    # timed overlay (cash in BEAR/CRISIS) on the two headline baskets
    if state:
        for v in ["8L_EW", "8L_LIQ", "VN30_LIQ"]:
            nav, miss, turn = run_strategy(baskets, qs, v, df, timing=state)
            navs[v + "_TIMED"] = nav; info[v + "_TIMED"] = (miss, turn)
    vni = vnindex_nav(qs)
    if vni is not None: navs["VNINDEX"] = vni

    print("="*92)
    print(f"8L-VN30 backtest — quarterly rebalance, liq>={LIQ_FLOOR/1e9:.0f}B/day, 8L basket={N8L} / VN30=30, TC {TC*100:.2f}%/turnover")
    print(f"Period: {navs['8L_EW'].index[0].date()} -> {navs['8L_EW'].index[-1].date()}  "
          f"({metrics(navs['8L_EW'])['years']:.1f}y, {len(baskets)} rebalances)")
    print("="*92)
    hdr = f"{'Strategy':<10} {'CAGR':>7} {'Vol':>6} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'Final×':>7}"
    print(hdr); print("-"*len(hdr))
    rows = {}
    for name, nav in navs.items():
        m = metrics(nav); rows[name] = m
        print(f"{name:<10} {m['CAGR']*100:>6.2f}% {m['Vol']*100:>5.1f}% {m['Sharpe']:>7.2f} "
              f"{m['MaxDD']*100:>6.1f}% {m['Calmar']:>7.2f} {m['Finalx']:>6.2f}x")
    print()
    for v in variants:
        print(f"  {v}: missing next-qtr closes={info[v][0]}, avg turnover/rebal={info[v][1]/len(baskets):.2f}")

    print("\n" + "="*92); print("ANNUAL RETURNS (%) — calendar year"); print("="*92)
    at = (annual_table(navs)*100).round(1)
    print(at.to_string())

    # win-rate: 8L_EW vs VN30_LIQ (the real-VN30 analogue)
    print("\n" + "="*92)
    a = annual_table(navs)
    for chal in ["8L_EW", "8L_LIQ"]:
        for bench in ["VN30_LIQ", "VN30_EW"]:
            comp = (a[chal] - a[bench]).dropna()
            wr = (comp > 0).mean()
            print(f"{chal} vs {bench}: win-rate {wr*100:.0f}% ({(comp>0).sum()}/{len(comp)} yrs), "
                  f"avg excess {comp.mean()*100:+.2f}pp/yr")

    # save
    navdf = pd.DataFrame(navs)
    navdf.to_csv(os.path.join(WORKDIR, "data", "bt_8l_vn30_nav.csv"))
    print(f"\nSaved data/bt_8l_vn30_nav.csv")

    # show a sample recent basket
    lastq = sorted(baskets.keys())[-1]
    nb = [baskets[q]["_nbank"] for q in sorted(baskets.keys())]
    print(f"\nBanks per 8L-VN30 basket: mean {np.mean(nb):.1f} (min {min(nb)}, max {max(nb)}), "
          f"latest {baskets[lastq]['_nbank']}  [real 8L top-30 ≈ 6 banks]")
    print(f"Most-recent 8L-VN30 basket ({pd.to_datetime(lastq).date()} quarter):")
    print("  "+", ".join(baskets[lastq]["8L_EW"]["ticker"].tolist()))

if __name__ == "__main__":
    main()
