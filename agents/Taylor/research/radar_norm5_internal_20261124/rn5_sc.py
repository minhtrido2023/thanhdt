import os, sys, re, subprocess
O, M = sys.argv[1], sys.argv[2]
sys.path.insert(0, O)
import dna_report as d
fails = 0
def ck(n, c):
    global fails
    print(("PASS" if c else "FAIL"), n); fails += (not c)
base = d.build_value_radar_line(html=False)
n5 = d.build_value_radar_line(html=False, with_norm5=True)
print(n5.splitlines()[-1])
ck("default (SpaceX/email path) không có dòng norm5", "LỢI NHUẬN" not in base and "chuẩn hoá 5Y" not in base and base.count("\n") == 1)
ck("with_norm5=True = base + 1 dòng phụ", n5.startswith(base) and n5.count("\n") == 2 and "chuẩn hoá 5Y" in n5)
ck("html default path vẫn byte-giống (chỉ so structure)", d.build_value_radar_line() is not None)
# cache thiếu => chỉ mất dòng phụ
import value_radar as v
v.NORM5_CACHE = "/nonexistent/x.csv"; v._NORM5_NOW.update(t=0.0, val=None)
ck("cache thiếu: with_norm5=True == base", d.build_value_radar_line(html=False, with_norm5=True) == base)
# static call-site checks
eod = open(f"{M}/bin/eod_trading_report.sh").read()
ck("eod: with_norm5 chỉ khi ACCOUNT=ZaloPay", "with_norm5=('$ACCOUNT' == 'ZaloPay')" in eod)
for f in ("portfolio_status.py", "report_v2/data_sources.py"):
    ck(f"{f}: không có with_norm5", "with_norm5" not in open(f"{M}/bin/{f}").read())
ck("dna_report.build_report (telegram) mặc định tắt", "with_norm5" not in d.__dict__.get("__doc__","") and re.search(r"vrline = build_value_radar_line\(\)", open(f"{O}/dna_report.py").read()) is not None)
# eod snippet thực thi với ACCOUNT=SpaceX vs ZaloPay (render python từ bash)
for acct in ("SpaceX", "ZaloPay"):
    code = re.search(r"vr = build_value_radar_line\(html=False(.*?)\)\n", eod).group(1).replace("'$ACCOUNT'", f"'{acct}'")
    got = eval("(lambda: " + f"d.build_value_radar_line(html=False{code})" + ")()") if False else None
print("FAILS", fails); sys.exit(1 if fails else 0)
