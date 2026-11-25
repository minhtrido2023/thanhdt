"""Đo lại GPM peer (Q4 = cả năm, 2016Q4–2025Q4) từ BQ tav2_bq.ticker_financial, truy vấn 25/11/2026 -> bq_gpm_q4_20261125.csv.
Đối chiếu số ADDENDUM_5F_r1 §2 (TB 14 CĐT 37,7% / trung vị 37,9% / TCH 29,9%); peer_stats_out.txt gốc không còn trong kho."""
import csv, statistics as st, sys
rows = list(csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else 'bq_gpm_q4_20261125.csv')))
per = {}
for r in rows:
    try: per.setdefault(r['ticker'], []).append(float(r['gpm']) * 100)
    except ValueError: pass
dev = {k: (st.mean(v), min(v), max(v), len(v)) for k, v in per.items() if k != 'TCH' and len(v) >= 5}
for k, (m, lo, hi, n) in sorted(dev.items()):
    print(f"{k}: TB {m:.1f}% (min {lo:.1f}, max {hi:.1f}, n={n})")
means = [m for m, *_ in dev.values()]
print(f"DEV n={len(dev)} TB-của-TB {st.mean(means):.1f}% trung vị {st.median(means):.1f}% | IQR {st.quantiles(means, n=4)[0]:.1f}–{st.quantiles(means, n=4)[2]:.1f}%")
t = per['TCH']; print(f"TCH TB {st.mean(t):.1f}% min {min(t):.1f} max {max(t):.1f} n={len(t)}")
