"""Which changed (ticker, quarter) rows actually reach a DECISION path?

Two consumers checked:
  A. data/custom30v_8l_publish.csv — the published custom30V basket (rebal_date, ticker, rating_8l, weight).
  B. the rating<=3 gate applied as-of a date (LAG P1 / golive sizing / custom30 selection all gate this way).
As-of semantics = the reader's own: latest row with eff_date <= as-of date (backward), per ticker.
"""
import pandas as pd, os, json

WC = "/home/trido/thanhdt/WorkingClaude"
c = pd.read_csv(os.path.join(WC, "data/rating_8l_history.csv"))
n = pd.read_csv("r8l_hist_EXP_icbpit_v2.csv")
for d in (c, n):
    d["eff_date"] = pd.to_datetime(d["eff_date"])

def asof(df, tk, when):
    s = df[(df.ticker == tk) & (df.eff_date <= when)].sort_values(["eff_date", "q_time"])
    return None if s.empty else s.iloc[-1]

pub = pd.read_csv(os.path.join(WC, "data/custom30v_8l_publish.csv"))
pub["rebal_date"] = pd.to_datetime(pub["rebal_date"])
CHANGED = ["HDG", "DIH"]

print("=== A. custom30v_8l_publish.csv rows for changed tickers ===")
rows = []
for _, r in pub[pub.ticker.isin(CHANGED)].sort_values("rebal_date").iterrows():
    a, b = asof(c, r.ticker, r.rebal_date), asof(n, r.ticker, r.rebal_date)
    rows.append({"rebal_date": str(r.rebal_date.date()), "ticker": r.ticker,
                 "published_rating": int(r.rating_8l), "weight": float(r.weight),
                 "ctl_rating": None if a is None else int(a.rating),
                 "new_rating": None if b is None else int(b.rating),
                 "ctl_route": None if a is None else a.route,
                 "new_route": None if b is None else b.route,
                 "ctl_gate_le3": None if a is None else bool(a.rating <= 3),
                 "new_gate_le3": None if b is None else bool(b.rating <= 3),
                 "ctl_le2": None if a is None else bool(a.rating <= 2),
                 "new_le2": None if b is None else bool(b.rating <= 2)})
p = pd.DataFrame(rows)
print(p.to_string(index=False))
p.to_csv("publish_asof_ab.csv", index=False)
print(f"\npublished rows for changed tickers: {len(p)}")
print(f"  published_rating == ctl_rating on {int((p.published_rating==p.ctl_rating).sum())}/{len(p)} rows"
      "  (sanity: the publish CSV was built on the control route)")
print(f"  rating DIFFERS under PIT on {int((p.ctl_rating!=p.new_rating).sum())}/{len(p)} rows")
print(f"  <=3 GATE flips on {int((p.ctl_gate_le3!=p.new_gate_le3).sum())}/{len(p)} rows")
print(f"  <=2 flag flips on {int((p.ctl_le2!=p.new_le2).sum())}/{len(p)} rows  "
      "(custom30v_hybrid swap rule gates at <=2)")

print("\n=== B. gate <=3 / <=2 as-of EVERY publish rebal date (all 49 rebals) ===")
gate = []
for rb in sorted(pub.rebal_date.unique()):
    for tk in CHANGED:
        a, b = asof(c, tk, rb), asof(n, tk, rb)
        if a is None and b is None:
            continue
        ga = None if a is None else a.rating <= 3
        gb = None if b is None else b.rating <= 3
        la = None if a is None else a.rating <= 2
        lb = None if b is None else b.rating <= 2
        gate.append({"rebal_date": str(pd.Timestamp(rb).date()), "ticker": tk,
                     "ctl_rating": None if a is None else int(a.rating),
                     "new_rating": None if b is None else int(b.rating),
                     "gate3_ctl": ga, "gate3_new": gb, "gate3_FLIP": ga != gb,
                     "le2_ctl": la, "le2_new": lb, "le2_FLIP": la != lb,
                     "in_published_basket": bool(((pub.rebal_date == rb) & (pub.ticker == tk)).any())})
g = pd.DataFrame(gate)
g.to_csv("gate_asof_ab.csv", index=False)
print(f"rebal x ticker pairs examined: {len(g)}")
print(f"  <=3 gate FLIPS: {int(g.gate3_FLIP.sum())}   <=2 flag FLIPS: {int(g.le2_FLIP.sum())}")
print("\n--- rows where the <=3 gate flips:")
print(g[g.gate3_FLIP].to_string(index=False) if g.gate3_FLIP.any() else "  (none)")
print("\n--- rows where the <=2 flag flips:")
print(g[g.le2_FLIP].to_string(index=False) if g.le2_FLIP.any() else "  (none)")

print("\n=== C. LIVE state (as of today 2026-09-27) — the money path ===")
today = pd.Timestamp("2026-09-27")
for tk in CHANGED:
    a, b = asof(c, tk, today), asof(n, tk, today)
    print(f"  {tk}: ctl eff={a.eff_date.date()} route={a.route} rating={a.rating} tier={a.tier}"
          f"  ||  new eff={b.eff_date.date()} route={b.route} rating={b.rating} tier={b.tier}"
          f"  | gate<=3 {a.rating<=3}->{b.rating<=3} | <=2 {a.rating<=2}->{b.rating<=2}")

# rebal currently in force
cur = pub[(pd.to_datetime(pub.effective_from) <= today) & (pd.to_datetime(pub.effective_to) >= today)]
print(f"\nrebal currently in force: {sorted(cur.rebal_date.dt.date.unique().tolist())} "
      f"({len(cur)} names)  changed tickers in it: {sorted(set(cur.ticker) & set(CHANGED))}")
json.dump({"publish_rows_changed_tickers": int(len(p)),
           "publish_rating_differs": int((p.ctl_rating != p.new_rating).sum()),
           "publish_gate3_flips": int((p.ctl_gate_le3 != p.new_gate_le3).sum()),
           "publish_le2_flips": int((p.ctl_le2 != p.new_le2).sum()),
           "gate3_flips_all_rebals": int(g.gate3_FLIP.sum()),
           "le2_flips_all_rebals": int(g.le2_FLIP.sum()),
           "rebal_in_force": sorted(cur.rebal_date.dt.date.astype(str).unique().tolist()),
           "changed_tickers_in_force": sorted(set(cur.ticker) & set(CHANGED))},
          open("consumers_summary.json", "w"), indent=1)
