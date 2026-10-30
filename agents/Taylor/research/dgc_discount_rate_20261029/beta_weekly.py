"""β tuần 5Y của DGC và trung vị peer hoá chất vs VNINDEX (job Taylor_20261030_031028). READ-ONLY.
Quy ước (khai rõ): giá = Close ĐIỀU CHỈNH (tav2_bq.ticker.Close); điểm tuần = phiên GIAO DỊCH CUỐI CÙNG của tuần ISO (Thứ Sáu,
hoặc phiên cuối nếu Thứ Sáu nghỉ); lợi suất = đơn giản tuần-sau/tuần-trước − 1; cửa sổ = các điểm tuần có ngày ∈ (2021-10-28, 2026-10-28]
(tuần 2026-10-26..30 chưa đủ ⇒ điểm cuối = phiên 28/10, như báo cáo gốc); β = cov(r_i, r_m)/var(r_m) (OLS, ddof=1).
Peer = tav2_mike.universe_pit in_universe tại 2026-10-28 ∩ ICB_Code 13xx (tại 2026-10-28), ≥150 tuần, loại DGC.
Chạy: $DNA_PYEXE beta_weekly.py  -> out_beta.csv. Biến thể quy ước in ra để biết độ nhạy."""
import os, io, subprocess
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
END, START = "2026-10-28", "2021-10-28"

def bq(sql):
    cmd = f'source {WC}/wc_env.sh && bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=1000000 "$SQL"'
    return pd.read_csv(io.StringIO(subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, check=True, env={**os.environ, "SQL": sql}).stdout))

peers = bq(f"SELECT DISTINCT t.ticker FROM tav2_bq.ticker AS t JOIN tav2_mike.universe_pit AS u ON u.ticker=t.ticker AND u.time=t.time "
           f"WHERE t.time='{END}' AND u.in_universe AND CAST(t.ICB_Code AS INT64) BETWEEN 1300 AND 1399 AND t.ticker!='DGC'").ticker.tolist()
tk = ",".join(f"'{x}'" for x in peers + ["DGC", "VNINDEX"])
px = bq(f"SELECT t.time, t.ticker, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker IN ({tk}) AND t.time>'2021-09-01' AND t.time<='{END}'")
px["time"] = pd.to_datetime(px.time)
wide = px.pivot_table(index="time", columns="ticker", values="Close").sort_index()

def weekly(wide, mode):
    w = wide.copy()
    if mode == "friday_last_trading":
        key = w.index.to_period("W-SUN")                 # tuần ISO Mon-Sun
        w = w.groupby(key).apply(lambda g: g.ffill().iloc[-1]); w.index = wide.groupby(key).apply(lambda g: g.index[-1])
    elif mode == "strict_friday":                         # chỉ lấy đúng Thứ Sáu; tuần không có ⇒ bỏ
        w = w[w.index.dayofweek == 4]
    return w

def beta(w, col, start=START, log=False):
    r = (np.log(w) .diff() if log else w.pct_change())
    r = r[(r.index > pd.Timestamp(start))][[col, "VNINDEX"]].dropna()
    return float(np.cov(r[col], r.VNINDEX, ddof=1)[0, 1] / np.var(r.VNINDEX, ddof=1)), len(r), float(r.corr().iloc[0, 1])

w = weekly(wide, "friday_last_trading")
b, n, rho = beta(w, "DGC")
rows = []
for p in peers:
    r = w[[p, "VNINDEX"]].pct_change(); r = r[r.index > pd.Timestamp(START)].dropna()
    if len(r) >= 150: rows.append((p, float(np.cov(r[p], r.VNINDEX, ddof=1)[0, 1] / np.var(r.VNINDEX, ddof=1)), len(r)))
pe = pd.DataFrame(rows, columns=["ticker", "beta", "n_weeks"])
print(f"DGC: β thô {b:.3f}  n={n}  ρ={rho:.3f}  Blume {2/3*b+1/3:.3f}")
print(f"PEER: N={len(pe)}  trung vị β thô {pe.beta.median():.3f}  Blume {2/3*pe.beta.median()+1/3:.3f}")
print("-- độ nhạy quy ước (DGC) --")
for lab, ww, st, lg in (("Friday-last-trading, simple (CHÍNH)", w, START, False), ("log-return", w, START, True),
                        ("strict Friday only", weekly(wide, "strict_friday"), START, False),
                        ("cửa sổ từ 2021-10-29", w, "2021-10-29", False), ("cửa sổ từ 2021-11-05", w, "2021-11-05", False)):
    bb, nn, rr = beta(ww, "DGC", st, lg); print(f"  {lab}: β {bb:.3f} n={nn} ρ={rr:.3f}")
pe.assign(dgc_beta=b, dgc_n=n).to_csv(os.path.join(HERE, "out_beta.csv"), index=False)
