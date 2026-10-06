"""Lane C (earnings-growth "cheap by growth") — PIT monthly cross-sectional backtest.

Job Taylor_20261005_180155. Research only, reads local BQ cache, writes only to this folder.
Interpreter: /home/trido/thanhdt/wc_venv/bin/python (pandas 3).

Universe E(d) at each month-end session d (all point-in-time):
  universe_pit in_universe & !banned & pass_golden_floor & rating_8l<=3  (tav2_mike cache)
Signal inputs: latest ticker_financial row with known_date (Release_Date, fallback `time`) < d,
  PE_now = tav2_bq.ticker.PE on d (raw-Price basis, PIT by construction — registry valuation_pe_pb_pcf_ps (4)).
Trade: signal at close d, enter close d+1 session, exit close of next rebalance's d+1 (T+1 both legs).
Returns from adjusted Close. TC 0.1%/side on one-way turnover.

Pre-declared trials (N_TRIALS=4) — thresholds fixed before the first run, not tuned:
  C1 GARP      : g_yoy>=30% & g_qoq>0 & 0<PE<=12                     (EW, all passing)
  C2 PEG       : g_ttm>=15% & 0<PEG<=0.5, PEG=PE/(100*g_ttm)          (EW, all passing)
  C3 RUNRATE3  : top-3/route by 1/PE_run, PE_run=PE*TTM/(4*NP_P0), need g_yoy>0 & PE>0
  C4 PEG3      : top-3/route by g_ttm/PE (=1/PEG), need g_ttm>0 & PE>0
Comparators (NOT trials): BASE = EW all E(d);  LANE_B = top-3/route by 1/PE (existing lane B).
"""
import os, glob, json
import numpy as np, pandas as pd

os.environ.setdefault("OMP_NUM_THREADS", "1")
WC = "/home/trido/thanhdt/WorkingClaude"
KNOWN_MODE = os.environ.get("KNOWN_MODE", "release")  # release | deadline (stress: max(release, regulatory deadline))
OUT = os.path.dirname(os.path.abspath(__file__)) + ("" if KNOWN_MODE == "release" else f"/known_{KNOWN_MODE}")
os.makedirs(OUT, exist_ok=True)
C = f"{WC}/data/bq_cache"
START, END = pd.Timestamp("2014-01-01"), pd.Timestamp("2026-10-05")
TC = 0.001
TRIALS = ["C1_GARP", "C2_PEG", "C3_RUNRATE3", "C4_PEG3"]
COMPS = ["BASE", "LANE_B"]

# ---------------- load ----------------
px = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "Close", "PE"])
                for f in sorted(glob.glob(f"{C}/ticker/*.parquet")) if int(os.path.basename(f)[:4]) >= 2013])
px["time"] = pd.to_datetime(px["time"])
px = px[(px.time >= "2013-10-01") & (px.time <= END)].drop_duplicates(["time", "ticker"])
close = px.pivot(index="time", columns="ticker", values="Close").sort_index()
pe = px.pivot(index="time", columns="ticker", values="PE").sort_index()
cal = close.index[close.index >= START]

up = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "in_universe", "banned", "pass_golden_floor", "rating_8l"])
                for f in sorted(glob.glob(f"{C}/universe_pit_q/*.parquet"))])
up["time"] = pd.to_datetime(up["time"])

fin = pd.read_parquet(f"{C}/ticker_financial.parquet",
                      columns=["ticker", "time", "quarter", "Release_Date"] + [f"NP_P{i}" for i in range(8)])
fin["known"] = pd.to_datetime(fin["Release_Date"]).fillna(pd.to_datetime(fin["time"]))
if KNOWN_MODE == "deadline":  # Circular 96/2020: quarterly consolidated <=45d, annual audited <=90d after quarter end
    qe = pd.PeriodIndex(fin["quarter"], freq="Q").end_time.normalize()
    dl = qe + pd.to_timedelta(np.where(fin["quarter"].str.endswith("Q4"), 90, 45), unit="D")
    fin["known"] = np.maximum(fin["known"].values, dl.values)
elif KNOWN_MODE != "release":
    raise SystemExit(f"KNOWN_MODE={KNOWN_MODE!r} (release|deadline)")
fin = fin.dropna(subset=["NP_P0"]).sort_values(["known", "ticker"])

rh = pd.read_csv(f"{WC}/data/rating_8l_history.csv", usecols=["ticker", "eff_date", "route"], parse_dates=["eff_date"])
rh = rh.sort_values("eff_date")

# LAG candidate events — exact production gate (pt_v23_audit_2014.py §4: NP_R>=15 & prior_n_good>=4 & pa_HL3>=5,
# forensic exclude date-aware), entry Release+5 sessions, hold 25 sessions.
ev = pd.read_csv(f"{WC}/data/earnings_events_classified.csv", parse_dates=["Release_Date"]).sort_values(["ticker", "Release_Date"])
LN2, HL = np.log(2), 3.0
png, pah = [], []
for tk, g in ev.groupby("ticker", sort=False):
    hist = []
    for _, row in g.iterrows():
        cur = row["Release_Date"]; png.append(len(hist))
        if hist:
            da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
            w = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL); pah.append((pa * w).sum() / w.sum())
        else:
            pah.append(np.nan)
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            hist.append((cur, row["post_ret"]))
ev["prior_n_good"], ev["pa_HL3"] = png, pah
ff = pd.read_csv(f"{WC}/data/forensic_flags.csv")
forx = {r.ticker: pd.Timestamp(r.date) for r in ff.itertuples() if str(r.severity).strip() == "exclude"}
ev["_forbid"] = [(t in forx) and (d >= forx[t]) for t, d in zip(ev.ticker, ev.Release_Date)]
lag = ev[(ev.NP_R >= 15) & (ev.prior_n_good >= 4) & (ev.pa_HL3 >= 5) & ~ev._forbid].copy()
allcal = close.index
def off(d, k):
    p = np.searchsorted(allcal.values, np.datetime64(d), side="right") - 1 + k
    return allcal[p] if 0 <= p < len(allcal) else pd.NaT
lag["entry"] = [off(d, 5) for d in lag.Release_Date]
lag["exit"] = [off(d, 30) for d in lag.Release_Date]
lag_q = set(zip(lag.ticker, lag.quarter))
lag.to_csv(f"{OUT}/lag_events_prodgate.csv", index=False)

# ---------------- signal panel per rebalance ----------------
me = pd.Series(cal).groupby(cal.to_period("M")).max().values
reb = [pd.Timestamp(d) for d in me if pd.Timestamp(d) < cal[-2]]
def nxt(d):
    p = allcal.get_loc(d) + 1
    return allcal[p] if p < len(allcal) else pd.NaT

rows = []
for d in reb:
    u = up[up.time == d]
    if u.empty:  # universe_pit missing that exact session -> last available before d
        dd = up.time[up.time <= d].max(); u = up[up.time == dd]
    e = u[(u.in_universe == True) & (u.banned != True) & (u.pass_golden_floor == True) & (u.rating_8l <= 3)]
    if e.empty: continue
    f = fin[fin.known < d].groupby("ticker").tail(1).set_index("ticker")  # latest KNOWN quarter (strict <)
    r = rh[rh.eff_date <= d].groupby("ticker").tail(1).set_index("ticker")["route"]
    x = e[["ticker", "rating_8l"]].set_index("ticker").join(f, how="inner")
    x["route"] = r.reindex(x.index).fillna("UNK")
    x["PE"] = pe.loc[d].reindex(x.index)
    x["d"], x["entry"] = d, nxt(d)
    rows.append(x.reset_index())
P = pd.concat(rows, ignore_index=True)
assert (P.known < P.d).all(), "look-ahead: financial known_date >= rebalance date"
np0, np1, np4 = P.NP_P0, P.NP_P1, P.NP_P4
ttm, ttm_prev = P[[f"NP_P{i}" for i in range(4)]].sum(axis=1, min_count=4), P[[f"NP_P{i}" for i in range(4, 8)]].sum(axis=1, min_count=4)
P["g_yoy"] = np.where((np4 > 0) & (np0 > 0), np0 / np4 - 1, np.nan)
P["g_qoq"] = np.where((np1 > 0) & (np0 > 0), np0 / np1 - 1, np.nan)
P["g_ttm"] = np.where((ttm_prev > 0) & (ttm > 0), ttm / ttm_prev - 1, np.nan)
P["PE_run"] = np.where((P.PE > 0) & (np0 > 0) & (ttm > 0), P.PE * ttm / (4 * np0), np.nan)
P["PEG"] = np.where((P.PE > 0) & (P.g_ttm > 0), P.PE / (100 * P.g_ttm), np.nan)
P["lag_same_q"] = [(t, q) in lag_q for t, q in zip(P.ticker, P.quarter)]
# held by LAG at entry date (LAG entry <= entry < LAG exit)
lg = lag.groupby("ticker")[["entry", "exit"]].apply(lambda g: list(zip(g.entry, g.exit))).to_dict()
P["lag_held"] = [any(a <= en < b for a, b in lg.get(t, [])) for t, en in zip(P.ticker, P.entry)]

def top3(df, key):
    df = df.dropna(subset=[key])
    return df.sort_values(["d", "route", key, "ticker"], ascending=[True, True, False, True]).groupby(["d", "route"]).head(3)
sel = {
    "BASE": P,
    "LANE_B": top3(P[P.PE > 0].assign(k=1 / P.PE), "k"),
    "C1_GARP": P[(P.g_yoy >= 0.30) & (P.g_qoq > 0) & (P.PE > 0) & (P.PE <= 12)],
    "C2_PEG": P[(P.g_ttm >= 0.15) & (P.PEG > 0) & (P.PEG <= 0.5)],
    "C3_RUNRATE3": top3(P[(P.g_yoy > 0) & (P.PE_run > 0)].assign(k=1 / P.PE_run), "k"),
    "C4_PEG3": top3(P[(P.g_ttm > 0) & (P.PE > 0)].assign(k=P.g_ttm / P.PE), "k"),
}

# ---------------- returns ----------------
ent = [nxt(d) for d in reb]
per = pd.DataFrame({"d": reb, "entry": ent, "exit": ent[1:] + [close.index[-1]]})
per = per[per.entry < per.exit]
def fwd(t, a, b):
    try: pa, pb = close.at[a, t], close.at[b, t]
    except KeyError: return np.nan
    if not (pa > 0): return np.nan
    if not (pb > 0):  # delisted / no price at exit: last valid price in window (no survivorship drop)
        s = close.loc[a:b, t].dropna(); pb = s.iloc[-1] if len(s) else np.nan
    return pb / pa - 1
P = P.merge(per, on=["d", "entry"], how="inner")
P["ret"] = [fwd(t, a, b) for t, a, b in zip(P.ticker, P.entry, P.exit)]
_key = P.set_index(["d", "ticker"]).index
for k in sel: sel[k] = P[_key.isin(sel[k].set_index(["d", "ticker"]).index)]
P.to_csv(f"{OUT}/panel.csv", index=False)

base_route = P.groupby(["d", "route"]).ret.mean().rename("route_mean")
def series(df, name):
    df = df.dropna(subset=["ret"])
    g = df.groupby("d")
    s = g.ret.mean()
    hold = g.ticker.apply(set)
    to, prev = [], set()
    for d, h in hold.items():
        to.append(1.0 if not prev else len(h - prev) / max(len(h), 1)); prev = h
    net = s - 2 * TC * pd.Series(to, index=hold.index)
    rx = df.join(base_route, on=["d", "route"]); rx = (rx.ret - rx.route_mean).groupby(rx.d).mean()
    return pd.DataFrame({f"{name}": net, f"{name}_n": g.size(), f"{name}_xroute": rx, f"{name}_lagheld": g.lag_held.mean(), f"{name}_lagq": g.lag_same_q.mean()})
M = pd.concat([series(sel[k], k) for k in COMPS + TRIALS], axis=1)
M = M.reindex(per.d).fillna({c: 0.0 for c in M.columns if c.endswith("_n")})
M.index.name = "d"
for k in COMPS + TRIALS:  # empty month = cash (0)
    M[k] = M[k].fillna(0.0)

# ---- self-check: independent recompute of gross monthly mean via pivot path ----
R = P.pivot_table(index="d", columns="ticker", values="ret")
for k in ["BASE", "C1_GARP"]:
    msk = sel[k].dropna(subset=["ret"]).assign(v=1).pivot_table(index="d", columns="ticker", values="v").reindex_like(R)
    alt = (R * msk).sum(axis=1) / msk.notna().sum(axis=1).replace(0, np.nan)
    ref = sel[k].dropna(subset=["ret"]).groupby("d").ret.mean()
    diff = (alt.reindex(ref.index) - ref).abs().max()
    assert diff < 1e-12, (k, diff)
    print(f"[selfcheck] {k}: pivot vs groupby max|diff|={diff:.2e}  OK")

M.to_csv(f"{OUT}/monthly.csv")
# also LAG-free variants: incremental part of each trial
for k in TRIALS:
    s2 = series(sel[k][~sel[k].lag_held & ~sel[k].lag_same_q], k + "_noLAG")
    M = M.join(s2[[k + "_noLAG", k + "_noLAG_n", k + "_noLAG_xroute"]])
    M[k + "_noLAG"] = M[k + "_noLAG"].fillna(0.0)
M.to_csv(f"{OUT}/monthly.csv")

def stats(r):
    r = r.dropna(); n = len(r)
    if n < 6: return dict(n=n)
    yrs = n / 12; cum = (1 + r).prod()
    nav = (1 + r).cumprod(); dd = (nav / nav.cummax() - 1).min()
    return dict(n=n, cagr=cum ** (1 / yrs) - 1, sharpe=r.mean() / r.std() * np.sqrt(12), maxdd=dd)
def ex(a, b):
    x = (a - b).dropna(); n = len(x)
    return dict(ex_mean_m=x.mean(), ex_t=x.mean() / x.std() * np.sqrt(n) if n > 2 else np.nan, ex_hit=(x > 0).mean(), ex_ir=x.mean() / x.std() * np.sqrt(12))
out = []
W = {"FULL": (START, END), "IS": (START, pd.Timestamp("2019-12-31")), "OOS": (pd.Timestamp("2020-01-01"), END),
     "OOS_ex2021": (pd.Timestamp("2022-01-01"), END)}
for w, (a, b) in W.items():
    m = M[(M.index >= a) & (M.index <= b)]
    for k in COMPS + TRIALS + [t + "_noLAG" for t in TRIALS]:
        row = dict(window=w, leg=k, **stats(m[k]))
        if k != "BASE":
            row.update(ex(m[k], m["BASE"]))
            if k + "_xroute" in m: row["xroute_mean_m"] = m[k + "_xroute"].mean(); row["xroute_t"] = m[k + "_xroute"].mean() / m[k + "_xroute"].std() * np.sqrt(m[k + "_xroute"].notna().sum())
            if k != "LANE_B": row.update({f"vsB_{kk}": vv for kk, vv in ex(m[k], m["LANE_B"]).items()})
        if k + "_n" in m: row["avg_n"] = m[k + "_n"].mean()
        if k + "_lagheld" in m: row["lag_held"] = m[k + "_lagheld"].mean(); row["lag_sameq"] = m[k + "_lagq"].mean()
        out.append(row)
S = pd.DataFrame(out)
S.to_csv(f"{OUT}/summary.csv", index=False)
pd.set_option("display.width", 250, "display.max_columns", 30)
print(S.round(4).to_string())
# per-year excess vs BASE (concentration check)
Y = (M[TRIALS + ["LANE_B"]].sub(M["BASE"], axis=0)).groupby(M.index.year).sum()
Y.to_csv(f"{OUT}/excess_by_year.csv"); print(Y.round(3).to_string())
json.dump({"n_trials": len(TRIALS), "trials": TRIALS, "months": int(len(M)), "rebal_first": str(M.index[0].date()), "rebal_last": str(M.index[-1].date())},
          open(f"{OUT}/meta.json", "w"), indent=1)
