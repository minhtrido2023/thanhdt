#!/usr/bin/env python3
"""
lag_common.py — shared LAG-only universe builder + NAV ledger engine.
Job Taylor_20260723_131958. Run with $DNA_PYEXE (pandas 3).

Builds the canonical LAG event schedule (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5,
entry T+5, hold 25d) and attaches, PER EVENT (all point-in-time at entry):
  - surprise_B_MA (NP surprise vs trailing-4Q mean)
  - rating (8L, asof eff_time <= entry_dt)
  - regime proxies at entry: dt5g_state, dt4_state, vni_dd (drawdown from 1y peak),
    vni_6m (6M return %), vni_vs_ma200 (Close/MA200-1 %), vni_rsi

simulate_nav(events, admit_fn, mult_fn, ...) runs the single-path NAV ledger, returns
(nav_series, trades_df). admit_fn(row)->bool gates entry; mult_fn(row)->float scales size.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
import pandas as pd, numpy as np

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
INIT_NAV = 50e9

# ---- canonical LAG params ----
POST_MIN, N_MIN, NPR_MIN = 5.0, 4, 0.15
ENTRY, HOLD, MAX_POS, POS_PCT = 5, 25, 12, 0.08
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
DEPOSIT, LIQ_CAP, MAX_FILL, LIQ_MIN = 0.01, 0.20, 5, 2e9
SIM_START, SIM_END = pd.Timestamp("2014-01-02"), pd.Timestamp("2026-05-15")


def _load_prices():
    with open("data/earnings_px.pkl", "rb") as f: px_data = pickle.load(f)
    px_data["time"] = pd.to_datetime(px_data["time"])
    px_close = px_data.pivot_table(index="time", columns="ticker", values="Close",
                                   aggfunc="first").sort_index().ffill(limit=5)
    master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
    px_close.index = master_idx
    with open("data/lagged_pos_ov.pkl", "rb") as f: ov = pickle.load(f)
    ov["time"] = pd.to_datetime(ov["time"])
    px_open = ov.pivot_table(index="time", columns="ticker", values="Open",
                             aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
    liq = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50",
                         aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
    return px_close, px_open, liq, master_idx


def _regime_frame():
    """Daily regime table indexed by date: dt5g_state, dt4_state, vni_dd, vni_6m, vni_vs_ma200, vni_rsi."""
    ref = pd.read_csv("deploy_golive_dt5g_v4/dt5g_daily_reference.csv", parse_dates=["time"])
    ref = ref[["time", "dt4_state", "dt5g_state"]].set_index("time").sort_index()
    vni = pickle.load(open("data/_cache_vnindex_2000_now.pkl", "rb"))
    vni["time"] = pd.to_datetime(vni["time"])
    vni = vni.set_index("time").sort_index()
    c = vni["Close"]
    vni_dd = (c / c.rolling(252, min_periods=60).max() - 1.0) * 100.0     # drawdown from 1y peak, <=0
    vni_6m = c.pct_change(126) * 100.0
    vni_vs_ma200 = (c / vni["MA200"] - 1.0) * 100.0
    vni_rsi = vni["D_RSI"]                                                # 0-1 daily RSI
    reg = pd.DataFrame({"vni_dd": vni_dd, "vni_6m": vni_6m,
                        "vni_vs_ma200": vni_vs_ma200, "vni_rsi": vni_rsi})
    reg = reg.join(ref, how="outer").sort_index()
    reg[["dt4_state", "dt5g_state"]] = reg[["dt4_state", "dt5g_state"]].ffill()
    reg = reg.ffill()
    return reg


def _asof_on(idx, target):
    pos = idx.searchsorted(target, side="right") - 1
    return pos if pos >= 0 else None


def build_events():
    """Return events DataFrame (one row per admitted LAG signal) with entry/exit dates + attrs."""
    px_close, px_open, liq, master_idx = _load_prices()
    all_dates = np.array(master_idx)

    # base event table + persistence-adjusted post history (pa_HL3)
    ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
    ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
    LN2, HL = np.log(2), 3.0
    ev["pa_HL3"] = np.nan; ev["prior_n_good"] = 0
    for tk, g in ev.groupby("ticker"):
        good = []
        for ri in g.index.tolist():
            row = ev.loc[ri]; cur = row["Release_Date"]; n = len(good)
            ev.at[ri, "prior_n_good"] = n
            if n >= 1:
                da = pd.to_datetime([d for d, _ in good]); pa = np.array([p for _, p in good])
                w = np.exp(-LN2 * (cur - da).days.values / 365.25 / HL)
                ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
            if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
                good.append((cur, row["post_ret"]))

    # surprise
    fin = pickle.load(open("data/earnings_surprise_data.pkl", "rb"))
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
    FLOOR = 1e9
    exp = fin[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].mean(axis=1)
    fin["surprise_B_MA"] = ((fin["NP_P0"] - exp) / np.maximum(np.abs(exp), FLOOR)).clip(-5, 5)
    ev = ev.merge(fin[["ticker", "quarter", "Release_Date", "surprise_B_MA"]],
                  on=["ticker", "quarter", "Release_Date"], how="left")

    # LAG admission filter
    e = ev[(ev["NP_R"] >= NPR_MIN * 100) & (ev["prior_n_good"] >= N_MIN) &
           (ev["pa_HL3"] >= POST_MIN)].copy()

    # entry/exit trading-day offsets
    def offset(ref_dt, off):
        p = np.searchsorted(all_dates, np.datetime64(ref_dt), side="right") - 1
        if p < 0: return None
        t = p + off
        return pd.Timestamp(all_dates[t]) if 0 <= t < len(all_dates) else None

    rows = []
    for _, r in e.iterrows():
        tk = r["ticker"]
        if tk not in px_open.columns: continue
        ent = offset(r["Release_Date"], ENTRY); ex = offset(r["Release_Date"], ENTRY + HOLD)
        if ent is None or ex is None: continue
        rows.append({"ticker": tk, "quarter": r["quarter"], "release_dt": r["Release_Date"],
                     "entry_dt": ent, "exit_dt": ex, "NP_R": r["NP_R"],
                     "surprise": r["surprise_B_MA"], "post_ret": r["post_ret"]})
    E = pd.DataFrame(rows).sort_values("entry_dt").reset_index(drop=True)

    # rating asof entry_dt (PIT)
    rt = pickle.load(open("data/rating_8l_history.pkl", "rb"))
    rt["eff_time"] = pd.to_datetime(rt["eff_time"]).astype("datetime64[ns]")
    E["entry_dt"] = E["entry_dt"].astype("datetime64[ns]")
    rt["ticker"] = rt["ticker"].astype(str)
    E["ticker"] = E["ticker"].astype(str)
    rt = rt.sort_values("eff_time")
    E = E.sort_values("entry_dt")
    E = pd.merge_asof(E, rt[["ticker", "eff_time", "rating", "route"]].sort_values("eff_time"),
                      left_on="entry_dt", right_on="eff_time", by="ticker", direction="backward")
    E = E.drop(columns=["eff_time"])

    # regime at entry_dt (PIT)
    reg = _regime_frame()
    ridx = reg.index
    for col in ["dt5g_state", "dt4_state", "vni_dd", "vni_6m", "vni_vs_ma200", "vni_rsi"]:
        E[col] = np.nan
    for i, ent in enumerate(E["entry_dt"].values):
        p = _asof_on(ridx, ent)
        if p is None: continue
        rr = reg.iloc[p]
        for col in ["dt5g_state", "dt4_state", "vni_dd", "vni_6m", "vni_vs_ma200", "vni_rsi"]:
            E.iat[i, E.columns.get_loc(col)] = rr[col]
    E["year"] = E["entry_dt"].dt.year
    return E, (px_close, px_open, liq, master_idx)


def simulate_nav(E, prices, admit_fn=None, mult_fn=None, start=SIM_START, end=SIM_END):
    """Single-path NAV ledger. admit_fn(row)->bool, mult_fn(row)->float in (0,1]."""
    px_close, px_open, liq, master_idx = prices
    all_dates = np.array(master_idx)
    sched = E.copy()
    if admit_fn is not None:
        keep = sched.apply(admit_fn, axis=1)
        sched = sched[keep].reset_index(drop=True)
    entries_by_day = sched.groupby("entry_dt")
    exits_by_day = sched.groupby("exit_dt")
    sim_days = [d for d in master_idx if start <= d <= end]
    cash = INIT_NAV; positions = {}; trades = []; nav_hist = []
    drate = (1 + DEPOSIT) ** (1 / 365.25) - 1
    for dt in sim_days:
        cash *= (1 + drate)
        if dt in exits_by_day.groups:
            for _, ex in exits_by_day.get_group(dt).iterrows():
                tk = ex["ticker"]
                if tk not in positions or positions[tk]["exit_dt"] != dt: continue
                pos = positions[tk]
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0:
                    fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx <= 0: continue
                cash += pos["shares"] * fpx * (1 - SLIP_OUT) * (1 - TAX)
                trades.append({"dt": dt, "ticker": tk, "entry_dt": pos["entry_dt"],
                               "ret_pct": (fpx / pos["entry_px"] - 1) * 100})
                del positions[tk]
        if dt in entries_by_day.groups:
            mtm = sum(p["shares"] * px_close.at[dt, tk] for tk, p in positions.items()
                      if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            for _, en in entries_by_day.get_group(dt).iterrows():
                tk = en["ticker"]
                if tk in positions or len(positions) >= MAX_POS: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq.at[dt, tk] if tk in liq.columns else 0
                if pd.isna(adv) or adv * fpx < LIQ_MIN: continue
                m = mult_fn(en) if mult_fn is not None else 1.0
                if m <= 0: continue
                target = POS_PCT * nav_now * m
                cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff = fpx * (1 + SLIP_IN); sh = alloc / eff
                cash -= sh * eff
                positions[tk] = {"entry_dt": dt, "exit_dt": en["exit_dt"],
                                 "shares": sh, "entry_px": fpx}
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk, p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_hist.append((dt, cash + mtm))
    nav = pd.Series({d: v for d, v in nav_hist}).sort_index()
    return nav, pd.DataFrame(trades)


def metrics(nav):
    """CAGR/Sharpe/MaxDD/Calmar on calendar time."""
    nav = nav.dropna()
    if len(nav) < 20: return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    n_per_yr = len(r) / yrs
    sharpe = r.mean() / r.std() * np.sqrt(n_per_yr) if r.std() > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    return dict(CAGR=cagr * 100, Sharpe=sharpe, MaxDD=dd * 100, Calmar=calmar)


if __name__ == "__main__":
    E, prices = build_events()
    E.to_pickle("research/lag_regime_gate/lag_events_attributed.pkl")
    print("Built events:", E.shape)
    print("cols:", list(E.columns))
    print("year range:", E["year"].min(), E["year"].max())
    print("rating coverage:", E["rating"].notna().mean())
    print("surprise coverage:", E["surprise"].notna().mean())
    print("dt5g coverage:", E["dt5g_state"].notna().mean())
    print(E[["entry_dt", "ticker", "NP_R", "surprise", "rating", "dt5g_state",
             "vni_dd", "post_ret"]].head(8).to_string())
    nav, tr = simulate_nav(E, prices)
    print("\nBASELINE:", metrics(nav), "| trades:", len(tr))
