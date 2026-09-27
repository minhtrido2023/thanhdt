#!/usr/bin/env python3
"""FAIL-D: DY hieu dung theo trong so tung ky rebal custom30V + haircut thue 5% + phi tai dau tu.
Paper-only. Doc: data/custom30v_8l_publish.csv, part2/div_events.csv, part2/px_at_rebal.csv."""
import csv, collections, datetime as dt, json, sys, os

ROOT = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(ROOT, "mike/agents/Taylor/research/measurement_integrity_audit_20260927/part2")
D = lambda s: dt.date.fromisoformat(s)

TAX = 0.05          # thue TNCN co tuc tien mat VN
FEE = 0.001         # phi 0,1%/chieu (CLAUDE.md §Backtest) tren phan tai dau tu
LAST_END = D("2026-06-15")   # bien du lieu ticker

memb = collections.defaultdict(list)
win = {}
for r in csv.DictReader(open(f"{ROOT}/data/custom30v_8l_publish.csv")):
    rb = r["rebal_date"]
    memb[rb].append((r["ticker"], float(r["weight"])))
    et = r["effective_to"].strip()
    win[rb] = (D(r["effective_from"]), D(et) if et else LAST_END)

div = collections.defaultdict(list)   # ticker -> [(exdate, vps, status)]
for r in csv.DictReader(open(f"{OUT}/div_events.csv")):
    div[r["ticker"]].append((D(r["exright_date"]), float(r["value_per_share"]), r["event_status"]))

px = {}
for r in csv.DictReader(open(f"{OUT}/px_at_rebal.csv")):
    px[(r["rebal_date"], r["ticker"])] = (float(r["price_raw"]), r["px_time"])

rows, missing_px, n_ann = [], [], 0
for rb in sorted(memb):
    f, t = win[rb]
    dy = 0.0; wcov = 0.0; nev = 0
    for tk, w in memb[rb]:
        p = px.get((rb, tk))
        if p is None:
            missing_px.append((rb, tk, w)); continue
        wcov += w
        d = 0.0
        for ex, vps, st in div.get(tk, []):
            if f <= ex < t:
                if st != "executed":
                    n_ann += 1
                d += vps; nev += 1
        dy += w * d / p[0]
    days = (t - f).days
    rows.append(dict(rebal=rb, start=str(f), end=str(t), days=days,
                     dy_period=dy, dy_ann=dy * 365.25 / days if days else 0.0,
                     w_cov=wcov, n_div_events=nev))

# tong hop
tot_days = (win[max(memb)][1] - win[min(memb)][0]).days
yrs = tot_days / 365.25
k = TAX + (1 - TAX) * FEE          # haircut tren moi dong co tuc
prod = 1.0
for r in rows:
    prod *= (1 - k * r["dy_period"])
dy_tot = sum(r["dy_period"] for r in rows)
dy_ann_agg = dy_tot / yrs

def cagr_drag(cagr_gross):
    return (1 + cagr_gross) * (1 - prod ** (1 / yrs))

byyear = collections.defaultdict(float)
for r in rows:
    byyear[r["start"][:4]] += r["dy_period"]

print(f"ky rebal: {len(rows)} | {rows[0]['start']} -> {rows[-1]['end']} | {tot_days} ngay lich = {yrs:.3f} nam")
print(f"thieu gia raw: {len(missing_px)} (ticker,ky) {missing_px[:5]}")
print(f"su kien DIV 'announced' (chua thuc hien) roi trong cua so: {n_ann}")
print()
print("DY hieu dung theo TRONG SO, quy nam (dy_ann):")
vals = sorted(r["dy_ann"] for r in rows)
med = vals[len(vals)//2]
print(f"  trung binh {sum(vals)/len(vals)*100:.3f}%  median {med*100:.3f}%  min {vals[0]*100:.3f}%  max {vals[-1]*100:.3f}%")
print(f"  DY tich luy toan giai doan {dy_tot*100:.3f}% / {yrs:.2f} nam = {dy_ann_agg*100:.3f}%/nam (gop)")
print()
print("Theo nam (tong dy_period cua cac ky BAT DAU trong nam):")
for y in sorted(byyear):
    print(f"  {y}: {byyear[y]*100:6.3f}%")
print()
print(f"he so haircut k = thue {TAX:.0%} + phi {FEE:.1%}x(1-thue) = {k:.5f}")
print(f"tich luy (1-k*DY) = {prod:.6f}  => drag hinh hoc {(1-prod**(1/yrs))*100:.4f} pp/nam tren muc TANG TRUONG")
for g in (0.1690, 0.2438):
    print(f"  neu CAGR gop chan park = {g*100:.2f}% => CAGR rong {(1+g)*prod**(1/yrs)-1:.4%}, drag {cagr_drag(g)*100:.4f} pp/nam")

with open(f"{OUT}/dy_by_rebal.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(dict(n_rebal=len(rows), yrs=yrs, dy_ann_agg=dy_ann_agg, k=k, prod=prod,
               drag_pp_per_year_on_growth=(1-prod**(1/yrs))*100,
               drag_pp_park_1690=cagr_drag(0.1690)*100, drag_pp_park_2438=cagr_drag(0.2438)*100,
               missing_px=len(missing_px), announced_in_window=n_ann),
          open(f"{OUT}/dy_summary.json","w"), indent=1)
