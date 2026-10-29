"""Độ trễ & độ dẫn trước của sự kiện tăng vốn 2025–2026 (q_lag2.csv). Thuần pandas, in ra stdout."""
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "q_lag2.csv")
for c in ["pub_now", "pub0", "fd", "objid_d", "first_seen", "ex", "rec", "ing"]:
    df[c] = pd.to_datetime(df[c], errors="coerce")
WARN = {"Rights", "PP", "EMPL", "PUBL", "TRANS", "MERGER", "ICRE", "BBOD"}
df["cls"] = df.m.map(lambda m: "WARN" if m in WARN else "INFO")
df = df[df.event_status != "not_executed"]
df["pub"] = df.pub0.fillna(df.pub_now)
bulk = df.objid_d.isin(pd.to_datetime(["2024-10-11"]))         # đợt migrate hàng loạt của vendor
ok = df[~bulk].copy()


def q(s):
    s = s.dropna()
    return f"n={len(s):4d} p10={s.quantile(.1):6.0f} med={s.median():5.0f} p90={s.quantile(.9):6.0f}" if len(s) else "n=0"


print(f"ISS public_date≥2025 (bỏ not_executed): {len(df)}; bỏ objid bulk 2024-10-11: {len(ok)}")
print(df.groupby(["cls", "m"]).size().to_string())
ok["obj_minus_pub"] = (ok.objid_d - ok.pub).dt.days
ok["ex_minus_obj"] = (ok.ex - ok.objid_d).dt.days
ok["ex_minus_pub"] = (ok.ex - ok.pub).dt.days
ok["obj_minus_fd"] = (ok.objid_d - ok.fd).dt.days
print("\n(1) vendor tạo record − public_date  [âm = vendor có record TRƯỚC ngày công bố ghi trên dòng]")
for c, g in ok.groupby("cls"):
    print(f"  {c} {q(g.obj_minus_pub)}")
print("(2) vendor tạo record − first_disclosure")
for c, g in ok.groupby("cls"):
    print(f"  {c} {q(g.obj_minus_fd)}")
print("(3) GDKHQ − vendor tạo record  [= số ngày cảnh báo tối đa nếu BQ thấy ngay]")
for (c, m), g in ok.groupby(["cls", "m"]):
    print(f"  {c} {m:7s} {q(g.ex_minus_obj)}  ex NULL {g.ex.isna().sum()}")
print("(4) GDKHQ − public_date")
for c, g in ok.groupby("cls"):
    print(f"  {c} {q(g.ex_minus_pub)}")
late = ok[(ok.ex_minus_obj <= 0)]
print(f"(5) record vendor tạo ĐÚNG/SAU GDKHQ: {len(late)}/{ok.ex.notna().sum()} có ex "
      f"({len(late)/max(ok.ex.notna().sum(),1):.0%}); theo cls: {late.groupby('cls').size().to_dict()}")
new = ok[ok.objid_d > "2026-08-17"].copy()
new["fs_minus_obj"] = (new.first_seen - new.objid_d).dt.days
print("(6) BQ của ta thấy (snapshot) − vendor tạo, chỉ record tạo sau 2026-08-17 (không censor):")
for c, g in new.groupby("cls"):
    print(f"  {c} {q(g.fs_minus_obj)}")
print(f"  ALL {q(new.fs_minus_obj)}")
print("(7) WARN 2025-26 có ex NULL (dòng P chưa ngày) theo phương thức:",
      ok[(ok.cls == 'WARN') & ok.ex.isna()].groupby('m').size().to_dict())
