"""Biểu đồ báo cáo DD nhà đầu tư MBB (31/10/2026). Import bởi build_report.py.
Số: ../REPORT.md v2 (đã áp 9 đính chính phản biện) + ../calc/mbb_calc_out.txt + ../calc/notes_read.md (đọc ảnh BCTC gốc).
Mỗi hình kèm CSV trong figs/. Ảnh: BCTN 2025 của MB (trích bằng pymupdf, src/bctn_img/).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
DD = os.path.join(HERE, "..")
IMG = os.path.join(DD, "src", "bctn_img")
NAVY, ACCENT, GREY, LIGHT, GREEN, GOLD = "#1F3A5F", "#C8553D", "#9AA5B1", "#D9DEE4", "#2E7D5B", "#E0A526"
FONT = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Regular.ttf"
FONT_B = "/home/trido/.claude/skills/dd-investor-report/fonts/BeVietnamPro-Bold.ttf"

PX = 19_300                      # đóng cửa 30/10/2026 [BQ]
BVPS = 15_594
FV_LO, FV_C, FV_HI = 18_000, 22_000, 26_000
Q = ["Q3/25", "Q4/25", "Q1/26", "Q2/26", "Q3/26"]
NIM = [4.02, 4.03, 3.85, 4.16, 4.07]
NIMX = [4.08, 4.15, 3.96, 4.21, 4.12]
YLD = [6.90, 7.23, 7.49, 8.37, 8.61]
COF = [2.87, 3.20, 3.63, 4.21, 4.55]
LNTT = [7249.9, 11129.1, 9628.4, 10559.9, 10330.1]
LNST = [5800.4, 8903.0, 7702.7, 8445.5, 8251.9]
PPOP = [11051.4, 13298.5, 13083.2, 14807.0, 15571.4]
DP = [3801.5, 2169.4, 3454.8, 4247.1, 5241.3]


def vn(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager as fm
    import matplotlib.pyplot as plt
    for f in (FONT, FONT_B):
        fm.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": "Be Vietnam Pro", "font.size": 9, "axes.titlesize": 9.8,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#555", "axes.labelcolor": "#333", "xtick.color": "#333",
        "ytick.color": "#333", "figure.facecolor": "white", "savefig.facecolor": "white",
        "axes.grid": True, "grid.color": "#ECEFF2", "grid.linewidth": 0.8, "axes.axisbelow": True})
    return plt


def save(fig, name, source, df=None):
    import textwrap
    fig.text(0.01, 0.01, "\n".join(textwrap.wrap(source, 150)), fontsize=6.6, color="#666", ha="left", va="bottom")
    fig.savefig(os.path.join(FIGS, name + ".png"), dpi=200)
    if df is not None:
        df.to_csv(os.path.join(FIGS, name + ".csv"), index=False)


def crop_h(im, ratio):
    """cắt giữa ảnh về tỉ lệ rộng/cao = ratio"""
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio); x0 = (w - nw) // 2
        return im.crop((x0, 0, x0 + nw, h))
    nh = int(w / ratio); y0 = (h - nh) // 2
    return im.crop((0, y0, w, y0 + nh))


def figs():
    import numpy as np
    import pandas as pd
    from PIL import Image
    plt = setup_mpl()
    x = np.arange(5)

    # 00 HERO -------------------------------------------------------------
    fig = plt.figure(figsize=(7.2, 3.3))
    axp = fig.add_axes([0.0, 0.08, 0.40, 0.92]); axp.axis("off")
    im = crop_h(Image.open(os.path.join(IMG, "p10_hq.jpeg")).convert("RGB"), 0.80)
    axp.imshow(im, aspect="auto")
    axp.text(0.04, 0.05, "Hội sở MB, Hà Nội — ảnh: BCTN 2025", transform=axp.transAxes, color="white", fontsize=6.5,
             bbox=dict(fc="#0d1b2a", ec="none", alpha=0.75, pad=2))
    axk = fig.add_axes([0.43, 0.50, 0.56, 0.48]); axk.axis("off")
    kpis = [("Giá 30/10/2026", "19.300 đ"), ("Vùng hợp lý", "18–26k"), ("P/B · P/E TTM", "1,24x · 6,0x"),
            ("ROE 9T/26", "21,7%"), ("Nhóm 2 Q3 vs Q2", "+42%"), ("NIM Q3 (bỏ TG NHNN)", "4,12%")]
    for i, (k, v) in enumerate(kpis):
        xx, yy = (i % 3) * 0.34, 0.55 if i < 3 else 0.02
        axk.add_patch(plt.Rectangle((xx, yy), 0.31, 0.42, color="#F3F5F7", transform=axk.transAxes))
        axk.text(xx + 0.02, yy + 0.27, v, fontsize=12, weight="bold", color=ACCENT if "Nhóm 2" in k else NAVY, transform=axk.transAxes)
        axk.text(xx + 0.02, yy + 0.07, k, fontsize=7, color="#444", transform=axk.transAxes)
    axv = fig.add_axes([0.45, 0.17, 0.52, 0.22])
    axv.barh(0, FV_HI - FV_LO, left=FV_LO, color=LIGHT, height=0.5)
    for lab, v in (("Xấu", 17323), ("Cơ sở", 24489), ("Tốt", 34144)):
        axv.plot(v, 0, "o", color=GREY, ms=5)
        axv.text(v, -0.55, f"{lab} {vn(v/1000,1)}k", ha="center", fontsize=6.5, color="#444")
    axv.axvline(FV_C, color=NAVY, lw=2); axv.text(FV_C + 250, 0.42, "tâm 22,0k", ha="left", fontsize=7, color=NAVY, weight="bold")
    axv.axvline(PX, color=ACCENT, lw=2, ls="--"); axv.text(PX - 250, 0.42, "giá 19,3k", ha="right", fontsize=7, color=ACCENT, weight="bold")
    axv.set_xlim(12000, 37000); axv.set_ylim(-1.1, 0.8); axv.set_yticks([]); axv.grid(False)
    axv.spines["left"].set_visible(False); axv.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    axv.tick_params(labelsize=7)
    fig.text(0.45, 0.43, "Giá trong vùng hợp lý, nửa dưới (−12% so với tâm)", fontsize=8.5, weight="bold", color=NAVY)
    save(fig, "fig_00_hero", "Nguồn: BCTC hợp nhất Q3/2026; tav2_bq (giá 30/10/2026); định giá của nhóm nghiên cứu (ước lượng; điểm kịch bản = RI @Ke 13,4%). Ảnh: BCTN 2025 của MB.",
         pd.DataFrame(kpis, columns=["kpi", "gia_tri"]))
    plt.close(fig)

    # 01 Chuỗi giá trị ngân hàng + cơ cấu thu nhập -----------------------
    fig = plt.figure(figsize=(7.2, 3.4))
    ax = fig.add_axes([0.01, 0.12, 0.60, 0.80]); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    boxes = [(0.2, 6.4, "HUY ĐỘNG\nTiền gửi KH 994k\nGiấy tờ có giá 302k\nVay TCTD 102k", NAVY),
             (3.6, 6.4, "NGÂN HÀNG\n(chênh lệch lãi\n= NIM ~4,1%)", GREEN),
             (7.0, 6.4, "CHO VAY\nDư nợ 1.288k\nTCKT 59%\ncá nhân 39% · BĐS 14%", NAVY),
             (0.2, 1.4, "THANH TOÁN &\nNGÂN HÀNG SỐ\n~99% giao dịch số", GREY),
             (3.6, 1.4, "BẢO HIỂM\nMB Life · MIC", GREY),
             (7.0, 1.4, "CHỨNG KHOÁN · TCTD\nMBS · MCredit\nMB Capital", GREY)]
    for bx, by, t, c in boxes:
        ax.add_patch(plt.Rectangle((bx, by), 2.8, 3.0, color=c, alpha=0.92 if c != GREY else 0.55))
        ax.text(bx + 1.4, by + 1.5, t, ha="center", va="center", color="white", fontsize=6.6, weight="bold")
    for a0, a1 in ((3.0, 3.6), (6.4, 7.0)):
        ax.annotate("", (a1, 7.9), (a0, 7.9), arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.2))
    ax.text(5.0, 5.4, "phí dịch vụ, bán chéo trong hệ sinh thái", ha="center", fontsize=7, color="#444")
    ax.set_title("Mô hình kinh doanh: 84% thu nhập là chênh lệch lãi", fontsize=9.8)
    ax2 = fig.add_axes([0.70, 0.42, 0.26, 0.50])
    comp = [("Thu nhập lãi thuần", 49642.7), ("Dịch vụ thuần", 5192.2), ("Ngoại hối thuần", 467.0),
            ("Chứng khoán KD+ĐT", 541.2), ("Khác (gồm thu nợ đã xử lý 2.080)", 3112.8)]
    cols = [NAVY, GREEN, GOLD, GREY, ACCENT]
    tot = sum(v for _, v in comp)
    ax2.pie([v for _, v in comp], colors=cols, startangle=90, counterclock=False, wedgeprops=dict(width=0.38, edgecolor="white"))
    ax2.text(0, 0, f"9T/26\n{vn(tot/1000,1)}k tỷ", ha="center", va="center", fontsize=8, weight="bold", color=NAVY)
    ax2.legend([f"{k} {v/tot*100:.0f}%".replace(".", ",") for k, v in comp], loc="upper center", bbox_to_anchor=(0.45, 0.0), fontsize=6.2, frameon=False, handlelength=1)
    save(fig, "fig_01_value_chain", "Nguồn: BCTC hợp nhất Q3/2026 (BCĐKT 30/09/2026, KQKD 9T/2026, thuyết minh tr.24–25, 35–40), nghìn tỷ đồng; BCTN 2025 (tỷ lệ giao dịch số). Sơ đồ minh họa của nhóm nghiên cứu.",
         pd.DataFrame(comp, columns=["khoan", "ty_dong_9T26"]))
    plt.close(fig)

    # 02 Sản phẩm / hệ sinh thái (ảnh BCTN) -------------------------------
    import sys
    sys.path.insert(0, "/tmp/pdflib")
    import pymupdf
    d = pymupdf.open(os.path.join(DD, "src", "bctn_2025.pdf"))
    logos = {"MBS": (43, (1030, 466, 1153, 490)), "MB Life": (44, (1072, 92, 1153, 121)),
             "MIC": (44, (500, 446, 557, 473)), "Mcredit": (44, (484, 89, 557, 121))}
    for k, (p, r) in logos.items():
        d[p - 1].get_pixmap(matrix=pymupdf.Matrix(5, 5), clip=pymupdf.Rect(*r)).save(os.path.join(IMG, f"logo_{k.replace(' ', '')}.png"))
    fig = plt.figure(figsize=(7.2, 3.35))
    tiles = [("p35_branch.jpeg", "Mạng lưới", "327 CN/PGD trong nước, 33/34 tỉnh;\n1 CN Lào, ngân hàng con Campuchia"),
             ("p15_a.jpeg", "Bán lẻ & ngân hàng số", "~35 triệu khách hàng; App MBBank\n~10 triệu giao dịch/ngày; ~99% GD số"),
             (None, "Hệ sinh thái tài chính", "MB Life top 1 bancassurance; MIC top 4\nphi nhân thọ; MBS LNTT 2025 1.415 tỷ;\nMcredit (50%) dư nợ 29,8 nghìn tỷ"),
             ("p09_team.jpeg", "Khách hàng doanh nghiệp", "TCKT 59% dư nợ; cổ đông lớn gồm\nViettel, SCIC… (theo báo chí)")]
    for i, (f, t, cap) in enumerate(tiles):
        ax = fig.add_axes([0.005 + i * 0.249, 0.27, 0.24, 0.66]); ax.axis("off")
        if f:
            ax.imshow(crop_h(Image.open(os.path.join(IMG, f)).convert("RGB"), 1.05), aspect="auto")
        else:
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
            ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="#F3F5F7"))
            for j, k in enumerate(("MB Life", "MIC", "MBS", "Mcredit")):
                lg = Image.open(os.path.join(IMG, f"logo_{k.replace(' ', '')}.png"))
                ext_w = 0.80 * min(1.0, (lg.width / lg.height) / 4.5)
                ax.imshow(lg, extent=(0.1, 0.1 + ext_w, 0.78 - j * 0.23, 0.95 - j * 0.23), aspect="auto", zorder=3)
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.text(0.0, 1.03, t, transform=ax.transAxes, fontsize=8.6, weight="bold", color=NAVY)
        fig.text(0.008 + i * 0.249, 0.245, cap, fontsize=6.1, color="#333", va="top")
    save(fig, "fig_02_products", "Ảnh và logo: Báo cáo thường niên 2025 của MB (trích nguyên bản). Số: BCTN 2025 (mạng lưới, khách hàng, giao dịch số, công ty con); BCTC hợp nhất Q3/2026 (cơ cấu dư nợ).",
         pd.DataFrame([(t, c.replace("\n", " ")) for _, t, c in tiles], columns=["mang", "chu_thich"]))
    plt.close(fig)

    # 03 NIM 5 quý ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(x, NIM, marker="o", color=GREY, lw=1.6, label="NIM (mẫu số gồm TG NHNN)")
    ax.plot(x, NIMX, marker="o", color=NAVY, lw=2.2, label="NIM bỏ TG NHNN (chuẩn mốc theo dõi)")
    for i in range(5):
        ax.text(i, NIMX[i] + 0.04, vn(NIMX[i], 2), ha="center", fontsize=7.5, color=NAVY, weight="bold")
        ax.text(i, NIM[i] - 0.09, vn(NIM[i], 2), ha="center", fontsize=7, color="#666")
    a2 = ax.twinx(); a2.grid(False); a2.spines["right"].set_visible(True)
    a2.bar(x - 0.15, YLD, width=0.28, color=LIGHT, label="Lợi suất TS sinh lãi")
    a2.bar(x + 0.15, COF, width=0.28, color="#F2C9BF", label="Chi phí lãi / TS sinh lãi")
    a2.set_ylim(0, 22); a2.set_ylabel("%/năm (cột)"); ax.set_zorder(a2.get_zorder() + 1); ax.patch.set_visible(False)
    ax.set_xticks(x, Q); ax.set_ylim(3.4, 4.65); ax.set_ylabel("NIM, %")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=6.8, frameon=False, ncol=2, loc="upper left")
    ax.set_title("NIM giữ ~4,1% dù chi phí lãi +115%; Q3 giảm 9 bp so với Q2")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_03_nim", "Nguồn: BCTC hợp nhất 5 quý; tự tính = thu nhập lãi thuần năm hoá / TS sinh lãi bình quân đầu–cuối quý (định nghĩa khác số MB công bố).",
         pd.DataFrame({"quy": Q, "nim": NIM, "nim_bo_tg_nhnn": NIMX, "loi_suat": YLD, "chi_phi_lai": COF}))
    plt.close(fig)

    # 04 PPOP, dự phòng, LNTT quý -------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.bar(x, np.array(LNTT) / 1e3, color=[LIGHT, LIGHT, NAVY, NAVY, NAVY], width=0.6, label="LNTT")
    ax.bar(x, np.array(DP) / 1e3, bottom=np.array(LNTT) / 1e3, color=ACCENT, alpha=0.75, width=0.6, label="Chi phí dự phòng")
    for i in range(5):
        ax.text(i, LNTT[i] / 1e3 / 2, vn(LNTT[i] / 1e3, 1), ha="center", fontsize=7.8, color="white" if i >= 2 else "#333", weight="bold")
        ax.text(i, PPOP[i] / 1e3 + 0.25, f"PPOP {vn(PPOP[i]/1e3,1)}", ha="center", fontsize=7)
        ax.text(i, -1.3, f"LNST {vn(LNST[i]/1e3,1)}", ha="center", fontsize=6.8, color="#555")
    ax.set_xticks(x, Q); ax.set_ylim(-1.8, 18.5); ax.set_ylabel("nghìn tỷ đồng")
    ax.legend(fontsize=7.2, frameon=False, loc="upper left")
    ax.set_title("Lợi nhuận trước dự phòng +41% cùng kỳ; dự phòng Q3 cao nhất 5 quý")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_04_profit", "Nguồn: BCTC hợp nhất (Q1/26 = 6T − Q2; Q4/25 từ BCTC Q4/2025). PPOP = LNTT + chi phí dự phòng. Q4 theo mùa: dự phòng Q4/25 chỉ 2.169 tỷ.",
         pd.DataFrame({"quy": Q, "lntt": LNTT, "lnst": LNST, "ppop": PPOP, "du_phong": DP}))
    plt.close(fig)

    # 05 Nguồn tài trợ tăng trưởng ------------------------------------------
    src_ = [("Giấy tờ có giá\n(CCTG, trái phiếu)", 115163), ("Tiền gửi\nkhách hàng", 72620), ("Rút tiền gửi\ntại NHNN", 52672), ("Vốn chủ sở hữu", 22119)]
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    yy = np.arange(len(src_))[::-1]
    ax.barh(yy, [v / 1e3 for _, v in src_], color=[ACCENT, NAVY, GREY, GREEN], height=0.6)
    for y_, (k, v) in zip(yy, src_):
        ax.text(v / 1e3 + 2, y_, f"{vn(v/1e3,1)}k · {v/204109*100:.0f}%".replace(".", ","), va="center", fontsize=8, weight="bold")
    ax.set_yticks(yy, [k for k, _ in src_], fontsize=7.6); ax.set_xlim(0, 150); ax.set_xlabel("nghìn tỷ đồng, 31/12/2025 – 30/09/2026")
    ax.set_title("Dư nợ +204 nghìn tỷ (+18,8%): 56% tài trợ bằng giấy tờ có giá, 36% bằng tiền gửi")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_05_funding", "Nguồn: BCTC hợp nhất Q3/2026 (BCĐKT, thuyết minh tr.35–36). % = phần trăm của mức tăng dư nợ 204.109 tỷ; tổng >100% vì tài sản khác cũng tăng. Không kỳ hạn 339.353 – 326.389 tỷ.",
         pd.DataFrame(src_, columns=["nguon", "tang_ty_dong"]))
    plt.close(fig)

    # 06 Chất lượng tài sản -------------------------------------------------
    dates = ["31/12/25", "30/06/26", "30/09/26"]
    g2 = [10210, 11990, 17014]; npl = [14027, 17797, 21474]; cov = [93.7, 93.6, 84.7]
    g2m = [5556, 7720, 12899]
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    xx = np.arange(3)
    ax.bar(xx - 0.2, np.array(g2) / 1e3, width=0.38, color=GOLD, label="Nợ nhóm 2 (hợp nhất)")
    ax.bar(xx + 0.2, np.array(npl) / 1e3, width=0.38, color=ACCENT, label="Nợ xấu nhóm 3–5")
    ax.plot(xx - 0.2, np.array(g2m) / 1e3, "D", color=NAVY, ms=5, label="Nhóm 2 ngân hàng mẹ")
    for i in range(3):
        ax.text(i - 0.2, g2[i] / 1e3 + 0.4, vn(g2[i] / 1e3, 1), ha="center", fontsize=7.5)
        ax.text(i + 0.2, npl[i] / 1e3 + 0.4, vn(npl[i] / 1e3, 1), ha="center", fontsize=7.5)
    ax.set_xticks(xx, dates); ax.set_ylim(0, 42); ax.set_ylabel("nghìn tỷ đồng")
    a2 = ax.twinx(); a2.grid(False); a2.spines["right"].set_visible(True)
    a2.plot(xx, cov, color=NAVY, marker="o", lw=1.8)
    for i in range(3):
        a2.text(i, cov[i] + 1.5, f"bao phủ {vn(cov[i],1)}%", ha="center", fontsize=7.3, color=NAVY, weight="bold")
    a2.set_ylim(30, 102); a2.set_ylabel("Bao phủ nợ xấu, %")
    ax.legend(fontsize=7, frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.6), ncol=3)
    ax.set_title("Q3 là điểm gãy: nhóm 2 +42% trong một quý, bao phủ 93,6% – 84,7%")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_06_asset_quality", "Nguồn: BCTC hợp nhất và riêng lẻ Q2, Q3/2026 (thuyết minh chất lượng nợ tr.19, 23, 26). NPL hợp nhất 1,29% – 1,45% – 1,67%; xoá nợ 9T 7.877 tỷ.",
         pd.DataFrame({"ngay": dates, "nhom2_hn": g2, "npl_hn": npl, "bao_phu_pct": cov, "nhom2_me": g2m}))
    plt.close(fig)

    # 07 BĐS + kỳ hạn -------------------------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.7))
    ax = axs[0]
    labs = ["Dư nợ chung", "KD bất động sản", "Hộ gia đình\n(gồm mua nhà)", "Xây dựng"]
    gr = [18.8, 48.3, 23.0, 13.0]
    ax.barh(range(4)[::-1], gr, color=[GREY, ACCENT, NAVY, NAVY])
    for i, v in zip(range(4)[::-1], gr):
        ax.text(v + 1, i, f"+{vn(v,1)}%", va="center", fontsize=8, weight="bold")
    ax.set_yticks(range(4)[::-1], labs, fontsize=7.4); ax.set_xlim(0, 60); ax.set_xlabel("% tăng 9T/2026")
    ax.set_title("BĐS tăng 2,6 lần dư nợ chung", fontsize=8.8)
    ax = axs[1]
    ax.bar([0, 1], [11.18, 13.95], color=[LIGHT, ACCENT], width=0.5)
    ax.bar([3, 4], [45.1, 51.1], color=[LIGHT, NAVY], width=0.5)
    for xx_, v in ((0, 11.18), (1, 13.95), (3, 45.1), (4, 51.1)):
        ax.text(xx_, v + 1.2, vn(v, 1) + "%", ha="center", fontsize=7.8, weight="bold")
    ax.set_xticks([0, 1, 3, 4], ["BĐS\n31/12", "BĐS\n30/09", "Trung–dài\nhạn 31/12", "Trung–dài\nhạn 30/09"], fontsize=7)
    ax.set_ylim(0, 60); ax.set_title("Tỷ trọng BĐS dưới 15%; kỳ hạn dài hơn", fontsize=8.8)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "fig_07_real_estate", "Nguồn: BCTC hợp nhất Q3/2026 thuyết minh tr.23, 25 (theo ngành, không gồm margin MBS). Hộ gia đình không tách vay mua nhà. Trung–dài hạn chia dư nợ không gồm margin MBS.",
         pd.DataFrame({"chi_tieu": labs, "tang_9T_pct": gr}))
    plt.close(fig)

    # 08 DuPont ------------------------------------------------------------
    steps = [("Thu nhập lãi thuần", 3.84), ("Ngoài lãi", 0.72), ("Chi phí hoạt động", -1.20), ("Dự phòng", -1.00), ("Thuế & khác", -0.47)]
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    cum = 0
    for i, (k, v) in enumerate(steps):
        ax.bar(i, v, bottom=cum if v > 0 else cum + v, color=NAVY if v > 0 else ACCENT, width=0.6)
        ax.text(i, max(cum, cum + v) + 0.08, ("+" if v > 0 else "−") + vn(abs(v), 2), ha="center", fontsize=8)
        cum += v
    ax.bar(5, 1.89, color=GREEN, width=0.6); ax.text(5, 1.97, "ROA 1,89%", ha="center", fontsize=8, weight="bold")
    ax.set_xticks(range(6), [k for k, _ in steps] + ["= ROA"], fontsize=7.4); ax.set_ylim(0, 5.2); ax.set_ylabel("% tổng tài sản BQ, năm hoá")
    ax.text(5.45, 4.5, "× đòn bẩy 11,2x\n= ROE 21,7%", ha="right", fontsize=9, weight="bold", color=NAVY)
    ax.set_title("DuPont 9T/2026: ROE 21,7% nhờ NIM cao và chi phí thấp, dự phòng ăn ~1/3 lợi nhuận")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "fig_08_dupont", "Nguồn: BCTC hợp nhất Q3/2026; tự tính trên TTS bình quân 31/12/25–30/09/26, năm hoá 365/273. ROE = LNST ngân hàng / VCSH mẹ bình quân.",
         pd.DataFrame(steps + [("ROA", 1.89), ("ROE", 21.7)], columns=["buoc", "pct"]))
    plt.close(fig)

    # 09 P/B lịch sử ---------------------------------------------------------
    pb = pd.read_csv(os.path.join(DD, "calc", "bq_mbb_pb_hist.csv"))
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    ax.vlines(pb["y"], pb["pb_min"], pb["pb_max"], color=LIGHT, lw=6)
    ax.plot(pb["y"], pb["pb_avg"], "o-", color=NAVY, lw=1.6, ms=4)
    ax.axhline(1.24, color=ACCENT, ls="--", lw=1.2); ax.text(2012, 1.27, "hiện tại 1,24x", color=ACCENT, fontsize=7.5, weight="bold")
    ax.axhline(1.17, color=GREY, ls=":", lw=1.2); ax.text(2012, 1.12, "trung vị 11 ngân hàng 1,17x", color="#555", fontsize=7)
    ax.set_ylabel("P/B (x)"); ax.set_xticks(pb["y"][::2])
    ax.set_title("P/B 1,24x: dưới trung bình 2025–26 (1,38–1,39x), trên đáy 2023 (1,06x)")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_09_pb_history", "Nguồn: tav2_bq.ticker (P/B ngày; thanh = min–max năm, chấm = trung bình). 2026 tính tới 30/10. Trung vị ngành: 11 ngân hàng niêm yết, không gồm MBB và STB, TCB đã điều chỉnh ngày GDKHQ.", pb)
    plt.close(fig)

    # 10 Football field ------------------------------------------------------
    bars = [("RI có trọng số, Ke 12,3–13,4%", 23912, 29419), ("RI kịch bản xấu – tốt (Ke 13,4%)", 17323, 34144),
            ("RI có trọng số, Ke ~15% (thị trường ngụ ý)", 18163, 18691), ("Hồi quy P/B–ROE 12 NH (R² 0,13)", 22580, 22580),
            ("Trung vị P/B 11 NH (1,17x)", 18275, 18275), ("P/B lịch sử 2023–26 (1,06–1,39x)", 16530, 21680),
            ("Gordon P/B, ROE 16%, g 7–8%", 22758, 30157)]
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    for i, (k, lo, hi) in enumerate(bars[::-1]):
        if hi - lo < 300:
            ax.plot((lo + hi) / 2, i, "D", color=NAVY, ms=6)
        else:
            ax.barh(i, hi - lo, left=lo, color=NAVY if "RI" in k else GREY, height=0.55, alpha=0.85)
        ax.text(hi + 400, i, f"{vn(lo/1e3,1)}–{vn(hi/1e3,1)}k" if hi - lo >= 300 else f"{vn(hi/1e3,1)}k", va="center", fontsize=7)
    ax.axvspan(FV_LO, FV_HI, color=GREEN, alpha=0.08)
    ax.axvline(FV_C, color=GREEN, lw=1.6); ax.text(FV_C + 250, len(bars) - 0.45, "tâm 22,0k", color=GREEN, fontsize=7.5, ha="left", weight="bold")
    ax.axvline(PX, color=ACCENT, lw=1.6, ls="--"); ax.text(PX - 250, len(bars) - 0.45, "giá 19,3k", color=ACCENT, fontsize=7.5, ha="right", weight="bold")
    ax.set_yticks(range(len(bars)), [b[0] for b in bars[::-1]], fontsize=7.2); ax.set_xlim(14000, 38000); ax.set_ylim(-1.1, len(bars) - 0.1)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    ax.set_title("Football field: vùng 18–26k (nền xanh); giá nằm nửa dưới")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_10_football_field", "Nguồn: tính toán của nhóm nghiên cứu (ước lượng), đ/cổ phiếu; BVPS 30/09/2026 15.594 đ. RI = thu nhập thặng dư 3 giai đoạn. Chưa trừ rủi ro ngoài bảng MBV (−350…−1.560 đ/CP tuỳ kịch bản).",
         pd.DataFrame(bars, columns=["phuong_phap", "thap", "cao"]))
    plt.close(fig)

    # 11 Độ nhạy Ke --------------------------------------------------------
    ke = [12.3, 12.8, 13.4, 15.0]; w = [29419, 26645, 23912, 18691]; w45 = [28487, 25823, 23196, 18163]
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.plot(ke, np.array(w) / 1e3, "o-", color=NAVY, lw=2, label="Trọng số kịch bản 0,35 / 0,45 / 0,20")
    ax.plot(ke, np.array(w45) / 1e3, "s--", color=GREY, lw=1.4, label="Xấu nâng lên 0,45")
    for k_, v in zip(ke, w):
        ax.text(k_, v / 1e3 + 0.7, vn(v / 1e3, 1), ha="center", fontsize=7.5, color=NAVY, weight="bold")
    ax.axhline(PX / 1e3, color=ACCENT, ls="--", lw=1.2); ax.text(13.7, PX / 1e3 + 0.4, "giá 19,3k", color=ACCENT, fontsize=7.5, weight="bold")
    ax.axvspan(12.3, 13.4, color=GREEN, alpha=0.08); ax.text(12.35, 16.6, "Ke nội địa 12,3–13,4%", fontsize=7, color=GREEN)
    ax.text(15.0, 16.6, "thị trường ngụ ý", fontsize=7, color="#555", ha="right")
    ax.set_xlabel("Chi phí vốn chủ Ke, %"); ax.set_ylabel("nghìn đ/CP"); ax.set_ylim(15, 32)
    ax.legend(fontsize=7, frameon=False, loc="upper right")
    ax.set_title("Kết luận nhạy với Ke: giá rẻ ở Ke nội địa, xấp xỉ hợp lý ở Ke ~15%")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "fig_11_ke_sensitivity", "Nguồn: RI 3 giai đoạn của nhóm nghiên cứu (ước lượng): rf chuẩn hoá ~6,75%, ERP nội địa, beta ~1,1. Tỷ trọng terminal ở kịch bản cơ sở 26–38%.",
         pd.DataFrame({"ke_pct": ke, "ri_trong_so": w, "ri_w_xau_045": w45}))
    plt.close(fig)

    # 12 Giá 12 tháng -------------------------------------------------------
    px = pd.read_csv(os.path.join(DD, "calc", "bq_mbb_px_1y.csv"), parse_dates=["time"])
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.plot(px["time"], px["Close"] / 1e3, color=NAVY, lw=1.4)
    for dt, lab in (("2026-02-11", "đỉnh 23,2k"), ("2026-07-27", "đáy 18,0k"), ("2026-10-20", "BCTC Q3 ký 20/10")):
        r = px[px["time"] == dt]
        if len(r):
            ax.annotate(lab, (r["time"].iloc[0], r["Close"].iloc[0] / 1e3), xytext=(0, 12 if "đáy" not in lab else -16), textcoords="offset points", fontsize=7, ha="center",
                        arrowprops=dict(arrowstyle="-", color="#888", lw=0.6))
    ax.set_ylim(17.5, 24.8); ax.set_ylabel("nghìn đ (điều chỉnh)"); ax.set_title("Giá 12 tháng: −17% từ đỉnh, YTD −4,7%; không phản ứng mạnh với BCTC Q3 (quan sát)")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_12_price", "Nguồn: tav2_bq.ticker (giá đóng cửa điều chỉnh, 01/10/2025–30/10/2026). Thanh khoản 20 phiên ~221 tỷ đ/phiên. Không gán nhân quả cho biến động giá.",
         px[["time", "Close", "val_bn"]])
    plt.close(fig)

    # 13 Ma trận rủi ro -----------------------------------------------------
    risks = [("Nhóm 2 chuyển thành nợ xấu", 0.45, 4.5), ("Bao phủ phải xây lại (DP tăng)", 0.45, 3.5), ("NIM nén do CV 9608 + vốn đắt", 0.55, 3.0),
             ("Hỗ trợ MBV ngoài bảng", 0.30, 3.0), ("BĐS tăng nóng, chủ đầu tư", 0.30, 4.0), ("Vốn: pha loãng/CAR", 0.35, 2.5),
             ("Room ngoại kín (cầu thụ động)", 0.60, 1.5)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.axvspan(0.4, 0.7, ymin=0.5, color=ACCENT, alpha=0.06)
    for k, p, imp in risks:
        ax.scatter(p, imp, s=110, color=ACCENT if p * imp >= 1.3 else GOLD, edgecolor="white", zorder=3)
        ax.text(p + 0.012, imp + 0.12, k, fontsize=7.2)
    ax.set_xlim(0.2, 0.85); ax.set_ylim(1, 5.2); ax.set_xlabel("Xác suất 12 tháng (ước lượng)"); ax.set_ylabel("Tác động (1–5)")
    ax.set_title("Ma trận rủi ro: chất lượng tài sản là cụm rủi ro chính")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_13_risk_matrix", "Nguồn: đánh giá của nhóm nghiên cứu (ước lượng, chủ quan); dấu hiệu sớm và ngày kiểm ở bảng mục 8.",
         pd.DataFrame(risks, columns=["rui_ro", "xac_suat", "tac_dong"]))
    plt.close(fig)

    # 14 Mạng lưới & lợi nhuận theo vùng (minh họa) -------------------------
    reg = [("Miền Bắc", 158, 22998), ("Miền Nam", 122, 9110), ("Miền Trung", 47, 2120), ("Nước ngoài\n(Lào, Campuchia)", 2, 40)]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.5))
    yy = np.arange(4)[::-1]
    axs[0].barh(yy, [r[1] for r in reg], color=NAVY); axs[0].set_yticks(yy, [r[0] for r in reg], fontsize=7.4)
    for y_, r in zip(yy, reg):
        axs[0].text(r[1] + 3, y_, str(r[1]), va="center", fontsize=8, weight="bold")
    axs[0].set_title("Điểm giao dịch 12/2025", fontsize=8.8); axs[0].set_xlim(0, 190)
    axs[1].barh(yy, [r[2] / 34268 * 100 for r in reg], color=GREEN); axs[1].set_yticks(yy, [""] * 4)
    for y_, r in zip(yy, reg):
        axs[1].text(r[2] / 34268 * 100 + 1.5, y_, f"{r[2]/34268*100:.0f}%", va="center", fontsize=8, weight="bold")
    axs[1].set_title("% LNTT bộ phận 2025 (trước loại trừ)", fontsize=8.8); axs[1].set_xlim(0, 80)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, "fig_14_network", "Nguồn: BCTN 2025 (mạng lưới theo vùng; báo cáo bộ phận theo địa lý, BCTC hợp nhất kiểm toán 2025 TM 46.2). Phân bổ theo tỉnh: không công bố.",
         pd.DataFrame(reg, columns=["vung", "diem_gd", "lntt_bo_phan_ty"]))
    plt.close(fig)
