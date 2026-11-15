"""P0 ai_momentum: cooldown greedy 90 ngay lich (<=1/ma/quy) tren qual_days.csv -> events.csv + bang N/thang.
Hai bien the: ALL (khong loc rating) va R4 (rating_8l as-of <= 4, nguon PIT tav2_bq.fa_ratings_8l).
Cooldown tinh tu SU KIEN da phat (greedy), khong phai tu ngay du dk lien truoc (khac SQL phu luc ke hoach)."""
import sys, pandas as pd
D = sys.argv[1]
QIN = sys.argv[2] if len(sys.argv) > 2 else "qual_days.csv"      # v3: qual_days_loose.csv events_v3.csv
EOUT = sys.argv[3] if len(sys.argv) > 3 else "events.csv"
q = pd.read_csv(f"{D}/{QIN}", parse_dates=["time"])

def greedy(df):
    out = []
    for tk, g in df.sort_values("time").groupby("ticker"):
        last = None; lastq = None
        for _, r in g.iterrows():
            qq = (r.time.year, (r.time.month - 1) // 3)
            if last is None or ((r.time - last).days > 90 and qq != lastq):
                out.append(r); last = r.time; lastq = qq
    return pd.DataFrame(out)

allv = greedy(q); allv["variant"] = "ALL"
r4 = greedy(q[q.rating.notna() & (q.rating <= 4)]); r4["variant"] = "R4"
ev = pd.concat([allv, r4]); ev.to_csv(f"{D}/{EOUT}", index=False)
for name, e in [("ALL", allv), ("R4", r4)]:
    e = e.copy(); e["ym"] = e.time.dt.strftime("%Y-%m")
    m = e.groupby("ym").size()
    print(f"== {name}: N={len(e)} ma={e.ticker.nunique()} thang={len(m)} TB/thang={len(e)/len(m):.1f} median/thang={m.median():.0f}")
    print(" ".join(f"{k}:{v}" for k, v in m.items()))
    print("  rating NULL:", int(e.rating.isna().sum()), "| route:", e.route.value_counts(dropna=False).to_dict())
    print("  rating dist:", e.rating.value_counts(dropna=False).sort_index().to_dict())
    print("  ex20 notna", int(e.ex20.notna().sum()), "ex60 notna", int(e.ex60.notna().sum()))
    print("  ex20 mean/med/sd", round(e.ex20.mean(),4), round(e.ex20.median(),4), round(e.ex20.std(),4),
          "| ex60", round(e.ex60.mean(),4), round(e.ex60.median(),4), round(e.ex60.std(),4))
    print("  P(ex20>0)", round((e.ex20.dropna()>0).mean(),3), "P(ex60>0)", round((e.ex60.dropna()>0).mean(),3))
q["ym"] = q.time.dt.strftime("%Y-%m")
print("qual_days rating NULL:", int(q.rating.isna().sum()), "of", len(q))
