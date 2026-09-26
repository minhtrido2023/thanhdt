"""H4 -- foreign MATCHED-ORDER net-sell indicator. Thresholds/rules per PREREG.md §1.2-1.6.
No parameter is chosen here that is not already written in PREREG.md."""
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
MIKE = f"{WC}/mike"

# ---------- load ----------
E = pd.read_csv(f"{MIKE}/data/fiinprox_vnindex_investor_flow_daily_20260914.csv",
                parse_dates=["date"])
E["flags"] = E["flags"].fillna("")
# PREREG 1.3: provisional window is display-only, excluded from every count
prov = E["flags"].str.contains("provisional")
E.loc[prov, ["foreign_matched_net_bn", "local_individual_net_bn",
             "local_institutional_net_bn"]] = np.nan

G = pd.read_csv("gtgd_daily.csv", parse_dates=["date"])
V = pd.read_csv(f"{WC}/data/VNINDEX.csv", usecols=["time", "Close"], parse_dates=["time"]) \
      .rename(columns={"time": "date", "Close": "vni"}).dropna().sort_values("date")

d = E[["date", "foreign_matched_net_bn", "foreign_deal_net_bn", "flags"]].merge(
        G[["date", "gtgd_bn"]], on="date", how="left").sort_values("date").reset_index(drop=True)
d = d.merge(V, on="date", how="left")
m = d["foreign_matched_net_bn"]

# ---------- IND-A: normalised by GTGD (median-60 denominator) ----------
def roll_sum_minobs(s, w, minobs):
    return s.rolling(w, min_periods=minobs).sum()

d["S20"] = roll_sum_minobs(m, 20, 15)          # PREREG: min 15/20 real cells
d["S60"] = roll_sum_minobs(m, 60, 45)
d["D60"] = d["gtgd_bn"].rolling(60, min_periods=45).median()
d["A20"] = d["S20"] / (20 * d["D60"])
d["A60"] = d["S60"] / (60 * d["D60"])

# ---------- IND-B: self z-score ----------
sd250 = m.rolling(250, min_periods=180).std()
d["z20"] = d["S20"] / (np.sqrt(20) * sd250)

CONFIGS = {                     # exactly the 5 declared in PREREG 1.2
    "A20@0.02":  ("A20", -0.02),
    "A20@0.03":  ("A20", -0.03),
    "A60@0.015": ("A60", -0.015),
    "B@2.0":     ("z20", -2.0),
    "B@2.5":     ("z20", -2.5),
}

def episodes(dates_fired, gap_days=60):
    """PREREG 1.4: fires <60 calendar days apart = ONE event."""
    out = []
    for dt in dates_fired:
        if out and (dt - out[-1][-1]).days < gap_days:
            out[-1].append(dt)
        else:
            out.append([dt])
    return out

vni = d.set_index("date")["vni"].dropna()

def is_false_alarm(fire_date):
    """PREREG 1.5: false alarm if VNINDEX does NOT fall >=10% from the fire-day close
    to any low within the next 126 sessions."""
    if fire_date not in vni.index:
        nxt = vni.index[vni.index >= fire_date]
        if len(nxt) == 0:
            return None
        fire_date = nxt[0]
    i = vni.index.get_loc(fire_date)
    fwd = vni.iloc[i: i + 127]
    if len(fwd) < 20:
        return None                      # not enough forward data to judge
    return bool((fwd.min() / fwd.iloc[0] - 1) > -0.10)

rows = []
detail = {}
for name, (col, thr) in CONFIGS.items():
    fired = d.loc[d[col] <= thr, "date"].tolist()
    eps = episodes(fired)
    recs = []
    for ep in eps:
        f0 = ep[0]
        fa = is_false_alarm(f0)
        i = vni.index.get_indexer([f0], method="bfill")[0]
        fwd = vni.iloc[i: i + 127]
        dd = (fwd.min() / fwd.iloc[0] - 1) * 100 if len(fwd) > 1 else np.nan
        recs.append(dict(first=f0.date(), last=ep[-1].date(), ndays=len(ep),
                         fwd_dd_pct=round(dd, 1), false_alarm=fa))
    detail[name] = recs
    ep2018 = [r for r in recs if r["first"].year == 2018]
    other = [r for r in recs if r["first"].year != 2018]
    fa_other = sum(1 for r in other if r["false_alarm"] is True)
    rows.append(dict(config=name, n_fire_days=len(fired), n_events=len(recs),
                     ev_2018=(ep2018[0]["first"] if ep2018 else None),
                     n_events_non2018=len(other), n_false_alarm_non2018=fa_other))

summary = pd.DataFrame(rows)
print("=== H4 SUMMARY (2014-01 -> 2026-08, provisional excluded) ===")
print(summary.to_string(index=False))
print()
for name, recs in detail.items():
    print(f"--- {name}  ({len(recs)} events) ---")
    print(pd.DataFrame(recs).to_string(index=False) if recs else "  (no fire)")
    print()

d.to_csv("h4_series.csv", index=False)
summary.to_csv("h4_summary.csv", index=False)
import json
json.dump({k: [{kk: str(vv) for kk, vv in r.items()} for r in v] for k, v in detail.items()},
          open("h4_events.json", "w"), indent=1)
