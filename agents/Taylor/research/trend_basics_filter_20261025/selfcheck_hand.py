"""Tính tay Python thuần (không numpy/pandas cho phép tính; pandas chỉ để ĐỌC parquet ra list) 5 chỉ báo cho 4 vị thế, so với trend.csv."""
import csv, glob, math
import pandas as pd
PX = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker"
HIDS = ["HPG_20140509_1", "AAM_20160722_504", "DPM_20150825_6", "SD4_20140428_26"]
rows = {r["holding_id"]: r for r in csv.DictReader(open("trend.csv"))}
HIDS = [h for h in HIDS if h in rows] + [h for h in list(rows)[::200] if h not in HIDS][: max(0, 4 - len([h for h in HIDS if h in rows]))]
tks = {rows[h]["ticker"] for h in HIDS} | {"VNINDEX"}
d = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "High", "Low", "Close"], filters=[("ticker", "in", list(tks))]) for f in sorted(glob.glob(f"{PX}/*.parquet"))])
data = {}
for tk, t, h, l, c in zip(d.ticker, d.time.astype(str).str[:10], d.High, d.Low, d.Close):
    data.setdefault(tk, {})[t] = (float(h), float(l), float(c))
mx = 0.0
for hid in HIDS:
    r = rows[hid]; tk = r["ticker"]; sd = r["ind_date"][:10]
    dates = sorted(data[tk]); i = dates.index(sd)
    H = [data[tk][x][0] for x in dates]; L = [data[tk][x][1] for x in dates]; C = [data[tk][x][2] for x in dates]
    vn = lambda k: data["VNINDEX"][dates[k]][2]
    rs60 = math.log(C[i] / C[i - 60]) - math.log(vn(i) / vn(i - 60))
    ma200 = sum(C[i - 199:i + 1]) / 200
    d_ma200 = C[i] / ma200 - 1
    pos52 = (C[i] - min(L[i - 251:i + 1])) / (max(H[i - 251:i + 1]) - min(L[i - 251:i + 1]))
    TR = [None] + [max(H[k] - L[k], abs(H[k] - C[k - 1]), abs(L[k] - C[k - 1])) for k in range(1, len(C))]
    atr = (sum(TR[i - 19:i + 1]) / 20) / (sum(TR[i - 99:i + 1]) / 100)
    up60 = sum(1 for k in range(i - 59, i + 1) if C[k] > C[k - 1]) / 60
    for nm, v in [("rs60", rs60), ("d_ma200", d_ma200), ("pos52", pos52), ("atr_ratio", atr), ("up60", up60)]:
        e = float(r[nm]); rel = abs(v - e) / max(abs(e), 1e-12); mx = max(mx, rel)
        print(f"{hid} {nm}: hand={v:.10g} engine={e:.10g} rel={rel:.2e}")
print(f"MAX rel err = {mx:.2e} -> {'PASS' if mx < 1e-9 else 'FAIL'}")
