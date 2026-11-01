"""Đánh giá nhanh ngưỡng −15% so tâm DD: tần suất lịch sử 2 năm (30/10/2024–30/10/2026, BQ tav2_bq.ticker Close
điều chỉnh, khớp DNSE 30/10 17/17 mã). ƯỚC LƯỢNG NHANH: áp tâm HIỆN TẠI lên giá quá khứ (giá trị hợp lý
khi đó khác) ⇒ chỉ đo 'giá hay dao động xa tâm hôm nay tới mức nào', không phải backtest tín hiệu.
Hysteresis giống công cụ (classify của bin/dd_price_zone_watch.py): vào ≤ −thr, ra > −10%."""
import csv, json, sys, importlib.util, collections
WT = "/home/trido/thanhdt/WorkingClaude/wt-dd-price-zone-20261101"
spec = importlib.util.spec_from_file_location("ddz", f"{WT}/bin/dd_price_zone_watch.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ents = m.latest_entries(json.load(open(f"{WT}/kb/dd_price_zones.json")))
H = collections.defaultdict(list)
for r in csv.DictReader(open("hist_2y.csv")):
    H[r["ticker"]].append((r["d"], float(r["c"])))
YEARS = 2.0
print("| Mã | Tâm | Đáy vùng | Mức −15% tâm | −15% so đáy | Giá 30/10 | Phiên | Ngày/năm ≤−15% | Lần vào (trễ −10%) | Ngày/năm ≤−20% | Ngày/năm < đáy vùng | Lần vào < đáy | Min 2 năm (% tâm) |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
out = []
for t, e in sorted(ents.items()):
    c, lo = e.get("center"), e.get("zone_low")
    px = H.get(t, [])
    n = len(px)
    def run(thr, base):
        alert, days, entries = False, 0, 0
        ee = dict(e, center=base)
        for _, p in px:
            k = m.classify(p, ee, alert, thr=thr, rel=10)
            if k["alert"] and not alert: entries += 1
            alert = k["alert"]; days += alert
        return days, entries
    if c:
        d15, n15 = run(15, c); d20, _ = run(20, c)
        mn = min(p for _, p in px) / c * 100 - 100
    else:
        d15 = n15 = d20 = mn = None
    if lo:
        dlo = sum(p < lo for _, p in px)
        ent_lo = sum(1 for i, (_, p) in enumerate(px) if p < lo and (i == 0 or px[i-1][1] >= lo))
    else:
        dlo = ent_lo = None
    lvl = int(c * 85 / 100) if c else None
    vs_lo = (lvl / lo - 1) * 100 if (lvl and lo) else None
    f = lambda x, fmt="{:,.0f}": "—" if x is None else fmt.format(x).replace(",", ".")
    print(f"| {t} | {f(c)} | {f(lo)} | {f(lvl)} | {f(vs_lo, '{:+.1f}%')} | {f(px[-1][1] if px else None)} | {n} | "
          f"{f(None if d15 is None else d15/YEARS, '{:.0f}')} | {f(n15)} | {f(None if d20 is None else d20/YEARS, '{:.0f}')} | "
          f"{f(None if dlo is None else dlo/YEARS, '{:.0f}')} | {f(ent_lo)} | {f(mn, '{:+.1f}%')} |")
    out.append({"ticker": t, "center": c, "zone_low": lo, "level_15": lvl, "level15_vs_low_pct": vs_lo, "n_sessions": n,
                "days_per_yr_le15": None if d15 is None else d15/YEARS, "entries_15": n15,
                "days_per_yr_le20": None if d20 is None else d20/YEARS,
                "days_per_yr_below_low": None if dlo is None else dlo/YEARS, "entries_below_low": ent_lo, "min_pct_center": mn})
json.dump(out, open("threshold_eval.json", "w"), ensure_ascii=False, indent=1)
