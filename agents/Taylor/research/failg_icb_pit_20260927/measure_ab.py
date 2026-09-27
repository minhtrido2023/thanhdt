"""FAIL-G A/B measurement: canonical (non-PIT ANY_VALUE route) vs ICB-PIT patch.

Control = data/rating_8l_history.csv (registry-pinned, md5 68ae047b, mtime 2026-09-27 10:36)
New     = r8l_hist_EXP_icbpit_v2.csv (branch fix/rating8l-icb-pit @7cdc08cc, md5 ea66aa95)
Key     = (ticker, eff_date, q_time) — the row identity used downstream by as-of readers.
"""
import pandas as pd, json, hashlib, os

WC = "/home/trido/thanhdt/WorkingClaude"
CTL = os.path.join(WC, "data/rating_8l_history.csv")
NEW = "r8l_hist_EXP_icbpit_v2.csv"

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

c = pd.read_csv(CTL); n = pd.read_csv(NEW)
K = ["ticker", "eff_date", "q_time"]
print(f"control {len(c)} rows md5={md5(CTL)[:8]} | new {len(n)} rows md5={md5(NEW)[:8]}")
assert len(c) == len(n), "row count changed -> not a pure route relabel"

m = c.merge(n, on=K, how="outer", suffixes=("_c", "_n"), indicator=True)
assert (m["_merge"] == "both").all(), f"key mismatch: {m['_merge'].value_counts().to_dict()}"

route_d  = m[m.route_c  != m.route_n]
rating_d = m[m.rating_c != m.rating_n]
tier_d   = m[m.tier_c   != m.tier_n]
# 8L gate is binary at <=3 (KB: "Rating = binary gate <=3"); crossing it is the only
# rating change that can flip a real decision.
cross = rating_d[((rating_d.rating_c <= 3) & (rating_d.rating_n >= 4)) |
                 ((rating_d.rating_c >= 4) & (rating_d.rating_n <= 3))]

print(f"\nrows: route changed {len(route_d)} | rating changed {len(rating_d)} | tier changed {len(tier_d)}")
print(f"rows CROSSING the <=3 gate: {len(cross)}")
for nm, d in (("route", route_d), ("rating", rating_d), ("cross34", cross)):
    print(f"\n--- {nm}: tickers = {sorted(d.ticker.unique())}")
    if len(d):
        print(d.groupby("ticker").size().to_string())

route_d.sort_values(K).to_csv("route_changes.csv", index=False)
rating_d.sort_values(K).to_csv("rating_changes.csv", index=False)
cross.sort_values(K).to_csv("cross_34.csv", index=False)

print("\n=== route transition detail (per ticker: which eff_date the route flips) ===")
for tk in sorted(route_d.ticker.unique()):
    d = m[m.ticker == tk].sort_values("eff_date")
    ch = d[d.route_c != d.route_n]
    print(f"{tk}: {len(d)} rows total, {len(ch)} changed | "
          f"ctl={sorted(d.route_c.unique())} new={sorted(d.route_n.unique())} | "
          f"eff_date {ch.eff_date.min()} -> {ch.eff_date.max()}")

print("\n=== rating change detail (ticker, eff_date, rating ctl->new, gate side) ===")
for _, r in rating_d.sort_values(K).iterrows():
    g = "CROSS" if ((r.rating_c <= 3) != (r.rating_n <= 3)) else "same-side"
    print(f"  {r.ticker} {r.eff_date} q={r.q_time} route {r.route_c}->{r.route_n} "
          f"rating {r.rating_c}->{r.rating_n} tier {r.tier_c}->{r.tier_n}  [{g}]")

json.dump({"control_md5": md5(CTL), "new_md5": md5(NEW), "rows": int(len(c)),
           "route_changed": int(len(route_d)), "rating_changed": int(len(rating_d)),
           "tier_changed": int(len(tier_d)), "cross_gate_3_4": int(len(cross)),
           "tickers_route": sorted(route_d.ticker.unique().tolist()),
           "tickers_rating": sorted(rating_d.ticker.unique().tolist()),
           "tickers_cross": sorted(cross.ticker.unique().tolist()),
           "unchanged_tickers": int(len(set(c.ticker.unique()) - set(route_d.ticker.unique())))},
          open("ab_summary.json", "w"), indent=1)
print("\nwrote ab_summary.json")
