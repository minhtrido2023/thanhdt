#!/usr/bin/env python3
"""Chart cho báo cáo tuần SpaceX+ZaloPay 2026-08-10 -> 2026-08-14.
NAV indexed (=100 tại ngày go-live riêng từng account) vs VNINDEX indexed, cùng trục thời gian.
Dữ liệu: nav_history_{account}.csv (đã vá 2 dòng 08-10/08-14 bị thiếu, xem report Mục provenance)
+ BQ tav2_bq.ticker.VNINDEX (mirror, ticker='VNM' để tránh trùng ngày do JOIN nhiều mã).
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

WC = "/home/trido/thanhdt/WorkingClaude"

spx = pd.read_csv(f"{WC}/data/execution_logs/nav_history_SpaceX.csv")[["date", "nav"]]
zlp = pd.read_csv(f"{WC}/data/execution_logs/nav_history_ZaloPay.csv")[["date", "nav"]]

# vá 2 ngày thiếu (08-10, 08-14) — số đã đối soát trong report (mtm_stock BQ close + cash broker thật)
spx = pd.concat([spx, pd.DataFrame([
    {"date": "2026-08-10", "nav": 965822008},
    {"date": "2026-08-14", "nav": 958940908},
])], ignore_index=True).drop_duplicates("date").sort_values("date")
zlp = pd.concat([zlp, pd.DataFrame([
    {"date": "2026-08-10", "nav": 949074832},
    {"date": "2026-08-14", "nav": 939887091},
])], ignore_index=True).drop_duplicates("date").sort_values("date")

vnindex = pd.read_csv("/tmp/vnindex_1y.csv")  # time,VNINDEX — đã kéo từ BQ trong phiên này

spx["date"] = pd.to_datetime(spx["date"])
zlp["date"] = pd.to_datetime(zlp["date"])
vnindex["time"] = pd.to_datetime(vnindex["time"])

spx = spx[spx["date"] >= "2026-07-01"]
zlp = zlp[zlp["date"] >= "2026-07-01"]
vni_spx = vnindex[(vnindex["time"] >= spx["date"].min()) & (vnindex["time"] <= spx["date"].max())]
vni_zlp = vnindex[(vnindex["time"] >= zlp["date"].min()) & (vnindex["time"] <= zlp["date"].max())]

spx_idx = spx["nav"] / spx["nav"].iloc[0] * 100
zlp_idx = zlp["nav"] / zlp["nav"].iloc[0] * 100
vni_spx_idx = vni_spx["VNINDEX"] / vni_spx["VNINDEX"].iloc[0] * 100
vni_zlp_idx = vni_zlp["VNINDEX"] / vni_zlp["VNINDEX"].iloc[0] * 100

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
ax.plot(spx["date"], spx_idx, label="SpaceX NAV (go-live 01/07)", color="#1f6feb", linewidth=2)
ax.plot(zlp["date"], zlp_idx, label="ZaloPay NAV (go-live 06/07)", color="#e8590c", linewidth=2)
ax.plot(vni_spx["date"] if "date" in vni_spx else vni_spx["time"], vni_spx_idx,
        label="VNINDEX (mốc SpaceX 01/07)", color="#6c757d", linewidth=1.4, linestyle="--")
ax.plot(vni_zlp["time"], vni_zlp_idx,
        label="VNINDEX (mốc ZaloPay 06/07)", color="#adb5bd", linewidth=1.0, linestyle=":")

ax.axvspan(pd.Timestamp("2026-08-10"), pd.Timestamp("2026-08-14"), color="#ffd43b", alpha=0.15,
           label="Kỳ báo cáo (10-14/08)")

ax.set_title("SpaceX & ZaloPay — NAV so với VNINDEX (index=100 tại go-live)\n"
              "01/07/2026 → 14/08/2026 · nguồn: nav_history_{account}.csv (verify_account_snapshot.py) "
              "+ BigQuery tav2_bq.ticker.VNINDEX", fontsize=10)
ax.set_xlabel("Ngày")
ax.set_ylabel("Index (=100 tại ngày go-live)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
ax.legend(fontsize=8, loc="lower left")
ax.grid(alpha=0.25)
fig.tight_layout()
out = f"{WC}/mike/reports/SpaceX_ZaloPay_weekly_2026-08-10_to_2026-08-14_nav_chart.png"
fig.savefig(out)
print("saved", out)
