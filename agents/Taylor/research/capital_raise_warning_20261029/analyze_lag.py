"""Độ trễ nguồn sự kiện tăng vốn: đọc q_lag.csv (vintage snapshot) → in median/p90 theo nhóm. Thuần pandas."""
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "q_lag.csv")
for c in ["first_seen", "pub0", "fd0", "objid_d", "ex0", "ex_now", "pub_now", "fd_now", "ing_now"]:
    df[c] = pd.to_datetime(df[c], errors="coerce")
WARN = {"Rights", "PP", "EMPL", "PUBL", "TRANS", "MERGER", "ICRE", "BBOD"}
df["cls"] = df["m"].map(lambda m: "WARN" if m in WARN else ("INFO" if m in ("DIV", "Bonus") else "?"))
new = df[df.first_seen > "2026-08-17"].copy()          # bỏ censoring trái (vintage đầu 08-17)
new["lag_pub"] = (new.first_seen - new.pub0).dt.days     # trễ so với ngày công bố ghi ở vintage ĐẦU
new["lag_fd"] = (new.first_seen - new.fd_now).dt.days    # so với first_disclosure (giá trị hiện tại)
new["lag_obj"] = (new.first_seen - new.objid_d).dt.days  # pipeline BQ so với lúc vendor tạo record
new["lead_ex"] = (new.ex_now - new.first_seen).dt.days   # còn bao nhiêu ngày cảnh báo trước GDKHQ
new["naive"] = (new.ing_now - new.pub_now).dt.days       # cách đo SAI (ingested_at = lần upsert cuối)


def q(s):
    s = s.dropna()
    return f"n={len(s)} med={s.median():.0f} p90={s.quantile(.9):.0f} max={s.max():.0f}" if len(s) else "n=0"


print(f"tổng dòng ISS {len(df)}; mới (first_seen>2026-08-17) {len(new)}; theo phương thức:")
print(new.groupby(["cls", "m"]).size().to_string())
for col, lab in [("lag_pub", "first_seen − public_date(vintage đầu)"), ("lag_fd", "first_seen − first_disclosure"),
                 ("lag_obj", "first_seen − objectid(vendor tạo)"), ("lead_ex", "GDKHQ − first_seen"),
                 ("naive", "SAI: ingested_at − public_date (hiện tại)")]:
    print(f"\n{lab}:\n  ALL  {q(new[col])}")
    for c, g in new.groupby("cls"):
        print(f"  {c:4s} {q(g[col])}")
neg = new[new.lead_ex <= 0]
print(f"\nsự kiện có GDKHQ ≤ ngày BQ thấy lần đầu (cảnh báo đến SAU/ĐÚNG ngày GDKHQ): {len(neg)}/{new.ex_now.notna().sum()}")
print(neg[["ticker", "m", "pub0", "first_seen", "ex_now"]].to_string(index=False))
print("\nca nêu tên (SCL/MBB/VIB/DSC) — public_date ≥ 2025:")
nm = df[df.ticker.isin(["SCL", "MBB", "VIB", "DSC"]) & (df.pub_now >= "2025-01-01")]
print(nm[["ticker", "m", "st_now", "pub0", "pub_now", "fd_now", "objid_d", "first_seen", "ex_now", "ing_now",
          "ratio0", "ratio_now"]].sort_values(["ticker", "pub_now"]).to_string(index=False))
