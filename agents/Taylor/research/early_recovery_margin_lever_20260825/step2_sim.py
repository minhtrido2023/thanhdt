"""Step 2 — overlay lever f trong cua so early-recovery. Causal, 1 phien tre thuc thi."""
import pandas as pd, numpy as np, sys, json
W = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
OUT = W + "/mike/agents/Taylor/research/early_recovery_margin_lever_20260825"

CSV = W + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv"
df = pd.read_csv(CSV, low_memory=False)
d = df[df["record_type"] == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
d = d.sort_values("ymd").drop_duplicates("ymd", keep="last").set_index("ymd")
for c in ["combined_nav","bal_stocks_ref","bal_etf_ref","lag_stocks_ref","lag_etf_ref","state","vni_close"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
nav = d["combined_nav"]
gross = (d["bal_stocks_ref"]+d["bal_etf_ref"]+d["lag_stocks_ref"]+d["lag_etf_ref"]) / nav
r = nav.pct_change()
idx = nav.index

print("=== gross exposure theo DT5G state (base R3) ===")
g_by = pd.DataFrame({"gross": gross, "state": d["state"]}).groupby("state")["gross"].agg(["count","mean","median","max"])
print(g_by.round(3).to_string())

dt = pd.read_csv(W + "/data/vnindex_5state_dt5g_live.csv", parse_dates=["time"]).sort_values("time")
state_s = dt.set_index("time")["state"].reindex(idx).ffill()
import value_radar
vr = value_radar.load_series(update=False).set_index("time")
radar = vr["score"].astype(float).reindex(idx).ffill()

EXITS = pd.read_csv(OUT + "/exits.csv", parse_dates=["exit"])

def build_window(exit_dates, months=18, radar_cap=67.0, lag=1):
    """Tra ve boolean Series: lever ACTIVE ngay t (da tinh tre thuc thi `lag` phien).
    Tin hieu tinh tren du lieu <= t-1-lag."""
    active = pd.Series(False, index=idx)
    spans = []
    for E in exit_dates:
        E = pd.Timestamp(E)
        if E not in idx:
            cand = idx[idx >= E]
            if not len(cand): continue
            E = cand[0]
        cap = E + pd.DateOffset(months=months)
        fut = idx[idx > E]
        C = None
        for t in fut:
            if t > cap: C = t; reason = "18m cap"; break
            if state_s.loc[t] in (1.0, 2.0): C = t; reason = "DT5G->BEAR/CRISIS"; break
            if radar.loc[t] > radar_cap: C = t; reason = "radar DAT"; break
        if C is None: C = idx[-1]; reason = "het mau"
        spans.append((E, C, reason))
        # signal at day s -> active from s+lag+1 ... apply through C+lag
        i0 = idx.get_loc(E) + 1 + lag
        i1 = idx.get_loc(C) + lag
        if i0 <= min(i1, len(idx)-1):
            active.iloc[i0:min(i1, len(idx)-1)+1] = True
    return active, spans

def sim(f, active, interest="actual", i_ann=0.10, tc=0.001):
    """interest: 'actual' = vay max(0, f*g-1); 'flat' = vay (f-1) moi ngay trong cua so."""
    lev = np.where(active.values, f, 1.0)
    g_prev = gross.shift(1).values
    daily_i = i_ann / 252.0
    if interest == "actual":
        borrow = np.maximum(0.0, lev * g_prev - 1.0)
    else:
        borrow = np.where(active.values, f - 1.0, 0.0)
    cost = np.nan_to_num(borrow) * daily_i
    # TC khi bat/tat don bay: notional = |dlev| * g
    dlev = np.abs(np.diff(np.concatenate([[1.0], lev])))
    tc_cost = dlev * np.nan_to_num(g_prev, nan=0.0) * tc
    rr = lev * r.values - cost - tc_cost
    rr[0] = 0.0
    nv = pd.Series(nav.iloc[0] * np.cumprod(1 + np.nan_to_num(rr)), index=idx)
    return nv, pd.Series(borrow, index=idx)

def metrics(nv):
    rr = nv.pct_change().dropna()
    yrs = (nv.index[-1]-nv.index[0]).days/365.25
    cagr = ((nv.iloc[-1]/nv.iloc[0])**(1/yrs)-1)*100
    dd = (nv/nv.cummax()-1).min()*100
    return dict(CAGR=round(cagr,2), Sharpe=round(rr.mean()/rr.std()*np.sqrt(252),2),
                MaxDD=round(dd,1), Calmar=round(cagr/abs(dd),2), finalB=round(nv.iloc[-1]/1e9,1))

# ---- bo episode ----
SETS = {
  "A_bobby_loai2+radar<=67": ["2020-05-27","2020-07-17","2022-08-17","2023-04-12"],
  "B_mech_dd<=-20+radar<=67": ["2020-05-27","2022-08-17","2023-04-12"],
  "C_mech_dd<=-15+radar<=67": ["2014-06-09","2020-05-27","2020-07-17","2022-08-17","2023-04-12","2023-11-30"],
}
base_m = metrics(nav)
print("\n=== BASE (control leg) ===", base_m)

results = {}
for sname, dates in SETS.items():
    active, spans = build_window(dates)
    print(f"\n=== SET {sname} — {active.sum()} phien active ({active.sum()/len(idx)*100:.1f}% mau) ===")
    for E,C,why in spans:
        print(f"   window {E.date()} -> {C.date()}  ({(C-E).days} ngay lich, dong vi: {why})")
    for interest in ["actual","flat"]:
        line = []
        for f in [1.0,1.1,1.2,1.3]:
            nv,b = sim(f, active, interest=interest)
            m = metrics(nv); m["f"]=f; m["interest"]=interest
            m["max_borrow_pct_nav"] = round(float(b.max())*100,1)
            m["days_borrowing"] = int((b>1e-9).sum())
            results[(sname,interest,f)] = (m, nv)
            line.append(m)
        print(f"  -- interest={interest} --")
        print(pd.DataFrame(line)[["f","CAGR","Sharpe","MaxDD","Calmar","finalB","max_borrow_pct_nav","days_borrowing"]].to_string(index=False))

import pickle
with open(OUT+"/results.pkl","wb") as fh:
    pickle.dump({k:(v[0],v[1]) for k,v in results.items()}, fh)
pd.DataFrame({"nav":nav,"gross":gross,"state":d["state"],"radar":radar,"r":r}).to_csv(OUT+"/base_daily.csv")
print("\nsaved.")
