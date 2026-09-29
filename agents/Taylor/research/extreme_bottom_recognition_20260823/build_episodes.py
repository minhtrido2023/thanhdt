"""Q2 — enumerate every VNINDEX dd52<=-20% episode 2007-2026, compare dd52-arm date vs TRUE trough.
All indicators are point-in-time: expanding-window percentiles only, no full-sample ranking."""
import pandas as pd, numpy as np, sys
D = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/extreme_bottom_recognition_20260823"

vni = pd.read_csv(f"{D}/_vni_daily.csv", parse_dates=["time"]).sort_values("time").reset_index(drop=True)
br  = pd.read_csv(f"{D}/_daily_breadth.csv", parse_dates=["time"]).sort_values("time").reset_index(drop=True)

# --- VNINDEX rolling 252-session high -> dd52 (identical definition to capit_margin_lever gate)
vni["hi252"] = vni["Close"].rolling(252, min_periods=120).max()
vni["dd52"]  = vni["Close"]/vni["hi252"] - 1.0
vni["tv20_vni"] = (vni["Close"]*vni["Volume"]).rolling(20).mean()
vni["tv250_vni"] = (vni["Close"]*vni["Volume"]).rolling(250).mean()
vni["dryup"] = vni["tv20_vni"]/vni["tv250_vni"]          # <1 = thanh khoan can kiet so voi 1 nam
for h,lab in [(250,"fwd12"),(500,"fwd24")]:
    vni[lab] = vni["Close"].shift(-h)/vni["Close"] - 1.0

# --- breadth, point-in-time
br["pct_ma200"]  = br["n_above_ma200"]/br["n_has_ma200"]
br["pct_52wlow"] = br["n_at_52wlow"]/br["n_has_52w"]
br["pct_dd50"]   = br["n_dd52_lt50"]/br["n_has_52w"]
br["pct_dd35"]   = br["n_dd52_lt35"]/br["n_has_52w"]
br["tv_ratio"]   = br["tv20_bn_vnd"]/br["tv20_bn_vnd"].rolling(250).mean()

df = vni.merge(br, on="time", how="inner").sort_values("time").reset_index(drop=True)

# --- PIT expanding percentile (min 750 sessions ~3y history; strictly <= t)
def pit_pctile(s, minobs=750):
    out = np.full(len(s), np.nan)
    v = s.values
    for i in range(len(v)):
        if i+1 < minobs or not np.isfinite(v[i]): continue
        h = v[:i+1]; h = h[np.isfinite(h)]
        if len(h) < minobs: continue
        out[i] = (h <= v[i]).mean()
    return out
for c in ["pe_med","pb_med","pct_ma200","pct_dd50"]:
    df[c+"_pit"] = pit_pctile(df[c])

df.to_csv(f"{D}/daily_panel.csv", index=False)

# --- episodes: contiguous dd52 <= -20 ; merge if gap < 90 calendar days (declared up front)
m = (df["dd52"] <= -0.20).values
segs, i = [], 0
while i < len(m):
    if m[i]:
        j = i
        while j+1 < len(m) and m[j+1]: j += 1
        segs.append((i,j)); i = j+1
    else: i += 1
merged = []
for s in segs:
    if merged and (df["time"][s[0]] - df["time"][merged[-1][1]]).days < 90:
        merged[-1] = (merged[-1][0], s[1])
    else: merged.append(list(s))
merged = [tuple(x) for x in merged]

rows = []
for a,b in merged:
    sub = df.iloc[a:b+1]
    ti = sub["Close"].idxmin()
    arm, tr = df.loc[a], df.loc[ti]
    peak_i = df["Close"][:a+1].idxmax()
    rows.append(dict(
        episode=f"{df['time'][a]:%Y-%m}", arm_date=f"{df['time'][a]:%Y-%m-%d}",
        trough_date=f"{df['time'][ti]:%Y-%m-%d}", end_date=f"{df['time'][b]:%Y-%m-%d}",
        lag_days=(df["time"][ti]-df["time"][a]).days,
        n_sessions=b-a+1,
        vni_arm=round(arm["Close"],1), vni_trough=round(tr["Close"],1),
        drop_arm_to_trough=round(tr["Close"]/arm["Close"]-1,4),
        dd52_arm=round(arm["dd52"],4), dd52_trough=round(tr["dd52"],4),
        maxdd_from_peak=round(tr["Close"]/df["Close"][peak_i]-1,4),
        # breadth / valuation AT ARM vs AT TROUGH
        ma200_arm=round(arm["pct_ma200"],3), ma200_trough=round(tr["pct_ma200"],3),
        low52_arm=round(arm["pct_52wlow"],3), low52_trough=round(tr["pct_52wlow"],3),
        dd50_arm=round(arm["pct_dd50"],3), dd50_trough=round(tr["pct_dd50"],3),
        pe_arm=round(arm["pe_med"],2) if np.isfinite(arm["pe_med"]) else None,
        pe_trough=round(tr["pe_med"],2) if np.isfinite(tr["pe_med"]) else None,
        pe_pit_arm=round(arm["pe_med_pit"],3) if np.isfinite(arm["pe_med_pit"]) else None,
        pe_pit_trough=round(tr["pe_med_pit"],3) if np.isfinite(tr["pe_med_pit"]) else None,
        pb_arm=round(arm["pb_med"],2), pb_trough=round(tr["pb_med"],2),
        dryup_arm=round(arm["dryup"],3) if np.isfinite(arm["dryup"]) else None,
        dryup_trough=round(tr["dryup"],3) if np.isfinite(tr["dryup"]) else None,
        tvratio_arm=round(arm["tv_ratio"],3) if np.isfinite(arm["tv_ratio"]) else None,
        tvratio_trough=round(tr["tv_ratio"],3) if np.isfinite(tr["tv_ratio"]) else None,
        rsi_arm=round(arm["D_RSI"],3), rsi_trough=round(tr["D_RSI"],3),
        fwd12_arm=round(arm["fwd12"],4) if np.isfinite(arm["fwd12"]) else None,
        fwd12_trough=round(tr["fwd12"],4) if np.isfinite(tr["fwd12"]) else None,
        fwd24_arm=round(arm["fwd24"],4) if np.isfinite(arm["fwd24"]) else None,
        fwd24_trough=round(tr["fwd24"],4) if np.isfinite(tr["fwd24"]) else None,
    ))
ep = pd.DataFrame(rows)
ep.to_csv(f"{D}/episodes_dd52.csv", index=False)
pd.set_option("display.width", 250, "display.max_columns", 60)
print(f"So episode dd52<=-20% (merge gap<90d): {len(ep)}\n")
print(ep[["episode","arm_date","trough_date","lag_days","drop_arm_to_trough","maxdd_from_peak",
          "fwd12_arm","fwd12_trough","fwd24_arm","fwd24_trough"]].to_string(index=False))
