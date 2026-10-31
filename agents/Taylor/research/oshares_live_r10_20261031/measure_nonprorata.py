"""R10/việc 2: lớp ISS KHÔNG theo tỷ lệ (riêng lẻ / ESOP / chuyển đổi TP / sáp nhập / đấu giá) —
oshares_live có thấy CP mới trước khi BCTC quý thấy không? Mỗi sự kiện executed từ 2023 trong
nonprorata_iss.csv: asof ∈ {ex−1, ex+30, ex+180} (≤ 2026-10-30): live (oshares_dcf.oshares_for) vs
số quý (ticker_financial dòng mới nhất time ≤ asof). Chạy: python measure_nonprorata.py <cay_WC>"""
import sys, os, contextlib, io
import pandas as pd
tree = sys.argv[1]
HERE_R = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tree); os.chdir(tree)
import dcf_valuation as dv, oshares_dcf as osd
ev = pd.read_csv(os.path.join(HERE_R, "nonprorata_iss.csv"))
fin = dv._load_financials()
tks = sorted(set(ev.ticker) & set(fin.ticker))
with contextlib.redirect_stdout(io.StringIO()):
    osd.prime(tks, "2026-10-30")
out = []
for _, e in ev[ev.ticker.isin(tks)].iterrows():
    ex = pd.Timestamp(e.exright_date)
    for lag in (-1, 30, 180):
        a = ex + pd.Timedelta(days=lag)
        if a > pd.Timestamp("2026-10-30"):
            continue
        rows = fin[(fin.ticker == e.ticker) & (fin.time <= a)]
        if rows.empty or not rows.iloc[-1].OShares > 0:
            continue
        f_os = float(rows.iloc[-1].OShares)
        with contextlib.redirect_stdout(io.StringIO()):
            r = osd.oshares_for(e.ticker, a.date().isoformat(), f_os)
        lv = r.get("value")
        out.append(dict(ticker=e.ticker, method_iss=e.issue_method_name_vi, ex=e.exright_date, listing=e.listing_date,
                        vol=e.issue_volumn, lag=lag, asof=a.date().isoformat(), fin_q=rows.iloc[-1].quarter,
                        fin_rel=rows.iloc[-1].time.date().isoformat(), fin_os=f_os, live=lv, src=r.get("source"),
                        meth=r.get("method"), div=(lv / f_os - 1) if lv else None))
d = pd.DataFrame(out)
d.to_csv(os.path.join(HERE_R, "nonprorata_live_vs_fin.csv"), index=False)
d["below"] = d["div"] < -0.005
d["above"] = d["div"] > 0.005
print("n đo", len(d), "| sự kiện", d.groupby(["ticker", "ex"]).ngroups)
print(d.groupby(["method_iss", "lag"]).agg(n=("div", "size"), live_below_fin=("below", "sum"),
                                           live_above_fin=("above", "sum")).to_string())
b = d[d.below].sort_values("div")
print("\nlive < quý > 0,5% (đầu 25):"); print(b.head(25)[["ticker", "method_iss", "ex", "lag", "fin_q", "fin_os", "live", "meth", "div"]].to_string())
print("\n|div| phân bố khi live<quý:", b["div"].describe().to_string())
