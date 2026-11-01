# TV2 DD v3 (01/11/2026) — trung vi P/E/P/B thang theo PHA chu ky LN (dinh chinh CAO-1 cua nguoi phan bien).
# Nguon: calc/bq_pe_pb_monthly.csv (BQ tav2_bq.ticker, PE/PB ngay cuoi thang, TTM BQ). Bo loc: pe>0 (khong loc tran tru khi ghi).
# Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc/pe_by_phase.py > calc/pe_by_phase_out.txt
import sys, pandas as pd
df = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "calc/bq_pe_pb_monthly.csv", parse_dates=["m", "d"])
df["y"] = df["m"].dt.year
def q(s):
    s = s.dropna()
    return f"p25/p50/p75 {s.quantile(.25):.2f}/{s.median():.2f}/{s.quantile(.75):.2f} n={len(s)}"
t = df[(df.tk == "TV2") & (df.pe > 0)]
phases = {
    "2014-16 (LN 36-100 ty, truoc chu ky)": (2014, 2016),
    "2017-21 LN DINH (214-272 ty)": (2017, 2021),
    "2019-21 LN DINH muon": (2019, 2021),
    "2018-21 (TTM da phan anh LN dinh)": (2018, 2021),
    "2022-25 LN DAY (53-95 ty) — KHONG DUNG": (2022, 2025),
    "2026 (LN hoi phuc)": (2026, 2026),
    "2014+ toan bo": (2014, 2026),
    "2019+ (so v2 da dung — lan pha)": (2019, 2026),
}
print("TV2 P/E thang theo pha (pe>0):")
for k, (a, b) in phases.items():
    s = t[(t.y >= a) & (t.y <= b)]
    print(f"  {k:42s} PE {q(s.pe)} | PB {q(s.pb)}")
print("Theo nam (trung vi PE):", t.groupby("y").pe.median().round(1).to_dict())
for tk in ("TV1", "TV3", "TV4"):
    u = df[(df.tk == tk) & (df.pe > 0)]
    print(f"{tk} 2014+ pe>0: {q(u.pe)} | pe<100: {q(u[u.pe < 100].pe)}")
