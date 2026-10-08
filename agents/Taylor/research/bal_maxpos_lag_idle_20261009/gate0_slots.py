"""Gate-0 part B: from SLOT_AUDIT_LOG of the control leg (engine-exact), count BAL candidates rejected ONLY by the
max_positions slot cap, split by DT5G state x LAG-idle; how much BAL cash existed at block time (= what a 13th+ slot
could actually be funded with, since BAL/LAG are independent ledgers); and forward-return quality of blocked-never-
filled candidates vs started entries (Open at would-be fill date -> Close +45 sessions = BAL hold_days), IS/OOS."""
import sys, pandas as pd, numpy as np, duckdb
AUD, LEDGER = sys.argv[1], sys.argv[2]
HOLD = 45
a = pd.read_csv(AUD, parse_dates=["ymd", "exec_start"]); a = a[a.book == "v23audit_BAL"]
L = pd.read_csv(LEDGER, low_memory=False)
d = L[L.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d.ymd)
for c in ["state", "nav_bal_ref", "bal_cash_ref", "nav_lag_ref", "lag_cash_ref", "cap_bal", "cap_lag"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
tx = L[L.record_type == "TX"]; lagbuy = set(pd.to_datetime(tx[(tx.book == "LAG") & (tx.action == "buy")].ymd))
d["lag_idle"] = ~d.ymd.isin(lagbuy)
d["lag_cash_comb"] = (d.lag_cash_ref / d.nav_lag_ref) * d.cap_lag / (d.cap_bal + d.cap_lag)
d = d.set_index("ymd")
NM = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
a["st"] = a.ymd.map(d.state).map(NM); a["lag_idle"] = a.ymd.map(d.lag_idle)
a["cash_pct_bal"] = a.cash / a.ymd.map(d.nav_bal_ref)
print("outcomes:", a.outcome.value_counts().to_dict())
# per entry
ent = a.groupby("seq_id").agg(ticker=("ticker", "first"), play=("play_type", "first"),
    first_block=("ymd", lambda s: s[a.loc[s.index, "outcome"].eq("SLOT_BLOCK")].min()),
    fill=("ymd", lambda s: s[a.loc[s.index, "outcome"].eq("FILL_START")].min()),
    first_seen=("ymd", "min"))
ent["blocked"] = ent.first_block.notna(); ent["filled"] = ent.fill.notna()
ent["lost_to_slot"] = ent.blocked & ~ent.filled
print("entries:", len(ent), "| ever slot-blocked:", int(ent.blocked.sum()), "| blocked then filled later:",
      int((ent.blocked & ent.filled).sum()), "| blocked & never filled (lost to slot):", int(ent.lost_to_slot.sum()))
# session level
blk = a[a.outcome == "SLOT_BLOCK"]
ses = blk.groupby("ymd").agg(n_blocked=("seq_id", "nunique"), cash_pct_bal=("cash_pct_bal", "first"))
ses["st"] = ses.index.map(d.state).map(NM); ses["lag_idle"] = ses.index.map(d.lag_idle)
tot = d.groupby(d.state.map(NM)).size()
tot_idle = d[d.lag_idle].groupby(d[d.lag_idle].state.map(NM)).size()
rows = []
for st in ["CRISIS", "BEAR", "NEUTRAL", "BULL", "EXBULL"]:
    s_all = ses[ses.st == st]; s_i = s_all[s_all.lag_idle == True]
    lost = ent[ent.lost_to_slot & ent.first_block.map(d.state).map(NM).eq(st)]
    lost_i = lost[lost.first_block.map(d.lag_idle) == True]
    rows.append(dict(state=st, N_sess=int(tot.get(st, 0)), N_idle=int(tot_idle.get(st, 0)),
        sess_block_idle=len(s_i), pct_idle_sess_blocked=round(len(s_i) / max(tot_idle.get(st, 1), 1), 3),
        cand_blocked_per_blk_sess=round(s_i.n_blocked.mean(), 2) if len(s_i) else 0,
        lost_cands_idle=len(lost_i),
        bal_cash_at_block_med=round(s_i.cash_pct_bal.median(), 4) if len(s_i) else np.nan,
        bal_cash_at_block_p90=round(s_i.cash_pct_bal.quantile(.9), 4) if len(s_i) else np.nan,
        lag_cash_comb_idle=round(d[(d.state.map(NM) == st) & d.lag_idle].lag_cash_comb.mean(), 3)))
G = pd.DataFrame(rows); print("\nGATE-0 by state (LAG-idle sessions):\n" + G.to_string(index=False)); G.to_csv("gate0_by_state.csv", index=False)
# quality: forward return Open(fill-or-would-be-fill date) -> Close(+HOLD sessions)
tick = sorted(set(ent.ticker) | {"VNINDEX"})
con = duckdb.connect()
px = con.sql(f"""SELECT ticker, CAST(time AS DATE) AS time, Open, Close FROM read_parquet('/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker/*.parquet')
  WHERE ticker IN ({",".join("'" + t + "'" for t in tick)}) AND time >= '2013-12-01'""").df()
px["time"] = pd.to_datetime(px.time); cal = pd.DatetimeIndex(sorted(d.index))
P = {t: g.set_index("time").sort_index() for t, g in px.groupby("ticker")}
vni = P.get("VNINDEX")
def fwd(t, t0):
    g = P.get(t)
    if g is None or t0 not in cal: return np.nan, np.nan
    i = cal.get_loc(t0); 
    if i + HOLD >= len(cal): return np.nan, np.nan
    t1 = cal[i + HOLD]
    try:
        o = g.Open.get(t0, np.nan); c = g.Close.asof(t1)
        r = c / o - 1 if o and o > 0 else np.nan
        rv = vni.Close.asof(t1) / vni.Close.asof(cal[i - 1]) - 1 if vni is not None else np.nan
    except Exception: return np.nan, np.nan
    return r, rv
ent["t0"] = ent.fill.where(ent.filled, ent.first_block)
ent[["r", "rv"]] = [fwd(t, t0) for t, t0 in zip(ent.ticker, ent.t0)]
ent["ex"] = ent.r - ent.rv
ent["st"] = ent.t0.map(d.state).map(NM); ent["idle"] = ent.t0.map(d.lag_idle)
ent["grp"] = np.where(ent.lost_to_slot, "LOST_TO_SLOT", np.where(ent.filled, "STARTED", "OTHER"))
ent["era"] = np.where(ent.t0.dt.year <= 2019, "IS", "OOS")
q = ent[ent.grp != "OTHER"].dropna(subset=["r"])
out = q.groupby(["grp", "era"]).agg(n=("r", "size"), n_dates=("t0", "nunique"), r_mean=("r", "mean"), r_med=("r", "median"),
                                     ex_mean=("ex", "mean"), hit=("ex", lambda s: (s > 0).mean()))
print("\nQUALITY (fwd %dd from Open at would-be fill):\n" % HOLD + out.round(4).to_string())
qb = q[q.st.isin(["BULL", "EXBULL"])]
print("\nQUALITY BULL+EXBULL only:\n" + qb.groupby(["grp", "era"]).agg(n=("r", "size"), n_dates=("t0", "nunique"),
      r_mean=("r", "mean"), ex_mean=("ex", "mean"), hit=("ex", lambda s: (s > 0).mean())).round(4).to_string())
# date-clustered contrast (collapse to one obs per date per group) — honest N
m = q.groupby(["t0", "grp"]).ex.mean().unstack()
print("\nper-date mean excess: STARTED %.4f (N=%d dates) | LOST %.4f (N=%d dates)" % (
    m.STARTED.mean(), m.STARTED.notna().sum(), m.get("LOST_TO_SLOT", pd.Series(dtype=float)).mean(),
    m.get("LOST_TO_SLOT", pd.Series(dtype=float)).notna().sum()))
ent.to_csv("gate0_entries.csv")
# --- addendum: de-duplicate daily re-signals into ticker EPISODES (same ticker blocked on sessions <=5 apart = 1 episode)
b = blk.sort_values(["ticker", "ymd"]).copy(); b["ci"] = b.ymd.map({t: i for i, t in enumerate(cal)})
b["new"] = b.groupby("ticker").ci.diff().fillna(99) > 5; b["ep"] = b.groupby("ticker").new.cumsum()
ep = b.groupby(["ticker", "ep"]).agg(t0=("ymd", "min"), t1=("ymd", "max"), ndays=("ymd", "nunique")).reset_index()
fs = a[a.outcome == "FILL_START"].groupby("ticker").ymd.apply(list).to_dict()
ep["started_within_20"] = [any(0 <= cal.get_loc(f) - cal.get_loc(t1) <= 20 for f in fs.get(tk, []) if f in cal)
                           for tk, t1 in zip(ep.ticker, ep.t1)]
ep["st"] = ep.t0.map(d.state).map(NM); ep["idle"] = ep.t0.map(d.lag_idle)
ep[["r", "rv"]] = [fwd(t, t0) for t, t0 in zip(ep.ticker, ep.t0)]; ep["ex"] = ep.r - ep.rv
ep["era"] = np.where(ep.t0.dt.year <= 2019, "IS", "OOS")
print("\nBLOCKED EPISODES (ticker, <=5-session gaps merged):", len(ep), "| later started within 20 sessions:", int(ep.started_within_20.sum()))
print(ep.groupby("st").agg(n_ep=("ticker", "size"), n_idle=("idle", "sum"), med_days=("ndays", "median")).to_string())
print("\nEPISODE quality (fwd 45d from Open at first block), never-started episodes:")
e2 = ep[~ep.started_within_20].dropna(subset=["r"])
print(e2.groupby("era").agg(n=("r", "size"), r_mean=("r", "mean"), r_med=("r", "median"), ex_mean=("ex", "mean"), ex_med=("ex", "median"), hit=("ex", lambda s: (s > 0).mean())).round(4).to_string())
st_ = q[q.grp == "STARTED"]
print("STARTED entries:"); print(st_.groupby("era").agg(n=("r", "size"), r_mean=("r", "mean"), r_med=("r", "median"), ex_mean=("ex", "mean"), ex_med=("ex", "median"), hit=("ex", lambda s: (s > 0).mean())).round(4).to_string())
# per-calendar-year mean excess of blocked episodes (LOO view)
print("\nblocked-episode mean excess by year:", e2.groupby(e2.t0.dt.year).ex.agg(["size", "mean"]).round(4).to_dict("index"))
bb = blk[blk.ymd.map(d.state).isin([4, 5])]
print("\nBAL cash/BAL NAV at block time, BULL+EXBULL: mean %.4f med %.4f | share of block-sessions with cash<1%%: %.3f" % (
    bb.groupby("ymd").cash_pct_bal.first().mean(), bb.groupby("ymd").cash_pct_bal.first().median(),
    (bb.groupby("ymd").cash_pct_bal.first() < 0.01).mean()))
ep.to_csv("gate0_episodes.csv", index=False)
