"""Biểu đồ bổ sung DD POW 25/11/2026. Chạy: /home/trido/thanhdt/wc_venv/bin/python -I tools/build_figs_20261125.py
Số: BCTN 2025 (src/BCTN_2025.ocr_garbled.txt: danh mục nhà máy tr.24-31; TM chi phí tài chính + lãi vay vốn hoá), BCTC Q3/2026 (TM 'chi phí tài chính').
Mỗi hình kèm CSV cùng tên."""
import os, textwrap, pandas as pd
import matplotlib; matplotlib.use("Agg")
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = [os.path.join(H, "png"), os.path.join(H, "investor_report", "figs")]
F = "/home/trido/.claude/skills/dd-investor-report/fonts/"
for f in ("BeVietnamPro-Regular.ttf", "BeVietnamPro-Bold.ttf"): fm.fontManager.addfont(F + f)
plt.rcParams.update({"font.family": "Be Vietnam Pro", "font.size": 9, "axes.titlesize": 9.8, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#ECEFF2", "axes.axisbelow": True, "figure.facecolor": "white", "savefig.facecolor": "white"})
NAVY, ACC, GREY, LIGHT, GREEN = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B"

def save(fig, name, src, df, dirs=OUT):
    fig.subplots_adjust(bottom=0.21)
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(src, 150)), fontsize=6.6, color="#666", va="bottom")
    for d in dirs:
        fig.savefig(os.path.join(d, name + ".png"), dpi=200); df.to_csv(os.path.join(d, name + ".csv"), index=False)
    plt.close(fig)

# --- 1. Công suất lắp đặt theo nhà máy (BCTN 2025)
plants = [("Cà Mau 1&2", 2008, 1500, NAVY), ("Nhơn Trạch 1", 2009, 450, "#2A7F9E"), ("Nhơn Trạch 2", 2011, 750, "#6FAFCB"),
          ("Hủa Na", 2013, 180, GREEN), ("Đakđrinh", 2014, 125, "#8CC9A5"), ("Vũng Áng 1", 2015, 1200, GREY),
          ("Nậm Nơn", 2024, 20, "#E0A030"), ("Nhơn Trạch 3&4", 2025, 1624, ACC)]
years = [2008, 2009, 2011, 2013, 2014, 2015, 2024, 2025]
rows = []; fig, ax = plt.subplots(figsize=(7.2, 3.3)); bottom = [0] * len(years)
for n, y, mw, c in plants:
    vals = [mw if yy >= y else 0 for yy in years]
    ax.bar([str(v) for v in years], vals, bottom=bottom, color=c, label=f"{n} ({mw:,} MW)".replace(",", "."), width=0.62)
    bottom = [b + v for b, v in zip(bottom, vals)]
for i, t in enumerate(bottom): ax.text(i, t + 80, f"{t:,}".replace(",", "."), ha="center", fontsize=8, fontweight="bold")
for i, yy in enumerate(years): rows.append({"nam_cuoi": yy, "tong_MW": bottom[i]})
ax.set_ylabel("MW"); ax.set_ylim(0, 6900); ax.set_title("Công suất lắp đặt tích luỹ theo năm vận hành: Nhơn Trạch 3&4 thêm 1.624 MW (+38%)")
ax.legend(fontsize=6.8, ncol=2, frameon=False, loc="upper left")
save(fig, "fig_10_capacity", "Nguồn: BCTN 2025 (danh mục nhà máy, năm vận hành thương mại), tự tổng hợp; Nậm Nơn tiếp nhận 12/2024; NT3&4 vận hành 21/11 và 17/12/2025.", pd.DataFrame(rows))

# --- 2. Chi phí lãi vay (đã tính vào KQKD + vốn hoá)
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [1.5, 1]})
ex = [381.6, 655.4]; cap = [622.0, 791.0]; lab = ["2024", "2025"]
a.bar(lab, ex, color=NAVY, width=0.55, label="Tính vào KQKD"); a.bar(lab, cap, bottom=ex, color=LIGHT, width=0.55, label="Vốn hoá vào XDCB (chủ yếu NT3&4)")
a.bar(["2026E"], [2048], color=ACC, alpha=0.55, hatch="//", width=0.55, label="2026E = 9T × 4/3 (ước lượng)")
for x, e, c in zip(lab, ex, cap): a.text(x, e + c + 50, f"{e + c:,.0f}".replace(",", "."), ha="center", fontsize=8, fontweight="bold"); a.text(x, e / 2, f"{e:,.0f}".replace(",", "."), ha="center", color="white", fontsize=8)
a.text("2026E", 2048 + 50, "2.048", ha="center", fontsize=8, fontweight="bold")
a.set_title("Lãi vay cả năm (tỷ đồng)"); a.set_ylim(0, 2500); a.legend(fontsize=6.5, frameon=False, loc="upper left")
b.bar(["9T/2025", "9T/2026"], [409.7, 1535.7], color=[NAVY, ACC], width=0.55)
for x, v in zip(["9T/2025", "9T/2026"], [409.7, 1535.7]): b.text(x, v + 40, f"{v:,.0f}".replace(",", "."), ha="center", fontsize=8, fontweight="bold")
b.set_title("Lãi vay 9 tháng (KQKD)"); b.set_ylim(0, 1900)
fig.suptitle("Lãi vay vào KQKD gấp ~3 lần vì hết vốn hoá; tổng lãi vay (cả vốn hoá) chỉ tăng ~1,4 lần", x=0.01, ha="left", fontsize=9.3, fontweight="bold")
fig.subplots_adjust(top=0.82, bottom=0.2)
save(fig, "fig_11_interest", "Nguồn: BCTN 2025 (TM chi phí tài chính; lãi vay vốn hoá 791,0 tỷ năm 2025, 622,0 tỷ năm 2024), BCTC HN Q3/2026 (TM 21 chi phí tài chính: 1.509,1 + 26,6 PVcomBank; 9T/25: 374,3 + 35,5). 2026E là ước lượng của nhóm nghiên cứu, chưa tính trả nợ gốc/vay mới.",
     pd.DataFrame({"ky": ["2024", "2025", "2026E", "9T/25", "9T/26"], "kqkd": [381.6, 655.4, 2048, 409.7, 1535.7], "von_hoa": [622.0, 791.0, None, None, None]}))

# --- 3. (NỘI BỘ) cơ cấu sản lượng điện — ước lượng đọc từ biểu đồ nhà môi giới, KHÔNG nguồn gốc
yrs = list(range(2019, 2026)); hydro = [29, 31, 32, 36, 29, 29, 33]; coal = [48, 48, 44, 39, 46, 50, 45]
fig, ax = plt.subplots(figsize=(7.2, 3.0))
for i, y in enumerate(yrs):
    if y in (2019, 2023, 2024): ax.axvspan(i - .5, i + .5, color="#F4D9D2", zorder=0)
    if y in (2021, 2022): ax.axvspan(i - .5, i + .5, color="#D6E4F0", zorder=0)
ax.plot(yrs, coal, "-o", color=NAVY, label="Nhiệt điện than (%)"); ax.plot(yrs, hydro, "-o", color=GREEN, label="Thuỷ điện (%)")
ax.set_ylim(20, 58); ax.legend(frameon=False, fontsize=8); ax.set_title("NỘI BỘ — tỷ trọng sản lượng điện: than đỉnh 50%, thuỷ điện đáy 29% ở El Niño (2023-24)")
save(fig, "fig_int_genmix_broker_est", "ƯỚC LƯỢNG đọc từ biểu đồ của nhà môi giới (email 25/11/2026), KHÔNG có nguồn gốc EVN/BCT đối chiếu; tô nền hồng = El Niño, xanh = La Niña theo biểu đồ đó. Không đưa vào bản nhà đầu tư.",
     pd.DataFrame({"nam": yrs, "thuy_dien_pct": hydro, "nhiet_dien_than_pct": coal}), dirs=[OUT[0]])
print("ok")
