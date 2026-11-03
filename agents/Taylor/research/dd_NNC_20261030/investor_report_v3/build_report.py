"""Báo cáo DD nhà đầu tư NNC — dữ liệu đến 03/11/2026. Số định giá đọc từ ../r3/calc/model_r3_out.json (khoá ../r3/calc/LOCK_md5_r3.txt
20:04:30 ICT, TRƯỚC khi so giá); so giá: ../r3/calc/compare_r3_out.txt. Hình không phụ thuộc định giá (01–10, 18–22) chép nguyên từ bộ hình
31/10/2026 (cùng số BCTC Q3/2026; CSV đi kèm). Khuôn PDF/CSS/md_to_html: _base_v2.py (không sửa).
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I build_report.py [figs|pdf|all]
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import _base_v2 as B
B.HERE = HERE; B.FIGS = os.path.join(HERE, "figs"); B.BREAK_BEFORE = ("5.",)
FIGS = B.FIGS; NAVY, ACCENT, GREY, GREEN = B.NAVY, B.ACCENT, B.GREY, B.GREEN
O = json.load(open(os.path.join(HERE, "..", "r3", "calc", "model_r3_out.json")))
PX = 46_100                                   # đóng cửa 03/11/2026 (DNSE; khớp tav2_bq.ticker) — đọc SAU khoá md5
TAM = round(O["tam"]); BASEV = round(O["base_co_so"]); G = {k: round(v) for k, v in O["grid_pct"].items()}
C = O["cells"]; TOR = O["tornado"]
SC = {"Tích cực (25%)": (C["tot|g2031"], C["tot|real"]), "Cơ sở (50%)": (C["co_so|g2031"], C["co_so|real"]),
      "Tiêu cực (25%)": tuple((0.2 * C[f"xau|{p}"] + 0.05 * C[f"rat_xau|{p}"]) / 0.25 for p in ("g2031", "real"))}
GPM = {"NNC": [.35, .21, .36, .35, .37, .43, .34, .30, .37, .40, .21, .28, .32, .49, .53],
       "KSB": [.31, .34, .35, .34, .39, .36, .49, .49, .46, .45, .37, .45, .44, .41, .33],
       "DHA": [.05, .13, .23, .32, .28, .27, .31, .31, .32, .22, .27, .28, .29, .36, .37],
       "VLB": [None] * 4 + [.27, .26, .22, .19, .26, .26, .24, .21, .27, .29, .34]}
YRS = [str(y) for y in range(2012, 2026)] + ["Q3/26"]
vn, k = B.vn, B.k


def figs():
    import numpy as np, pandas as pd
    import matplotlib.patches as mp
    plt = B.setup_mpl()
    st1 = TAM + TOR["stress bien cum 1,0 (GPM ve TB 2012-25) tu 2028"]
    st36 = [v for kk, v in TOR.items() if kk.startswith("STRESS bien da ve GPM 36%")][0] + TAM
    # 00 HERO
    fig = plt.figure(figsize=(7.2, 3.15))
    band = fig.add_axes([0, 0.86, 1, 0.14]); band.axis("off")
    band.add_patch(mp.Rectangle((0, 0), 1, 1, fc=NAVY, transform=band.transAxes))
    band.text(0.015, 0.5, "NNC · Đá xây dựng cụm Đồng Phú (Đông Nam Bộ)", color="white", fontsize=10.5, fontweight="bold", va="center")
    band.text(0.985, 0.5, "Giá 46,1k: dưới P10 giá trị — rẻ có điều kiện biên", color="white", fontsize=9, fontweight="bold", va="center", ha="right",
              bbox=dict(boxstyle="round,pad=0.3", fc=ACCENT, ec="none"))
    a = fig.add_axes([0.0, 0.15, 0.28, 0.66]); a.axis("off"); a.set_xlim(0, 3); a.set_ylim(0, 3.2)
    a.add_patch(mp.Polygon([[0.2, 0.9], [1.0, 2.4], [1.5, 1.7], [2.1, 2.6], [2.85, 0.9]], fc="#8A98A8", ec=NAVY, lw=0.8))
    for x, y, s in ((0.5, 0.75, 0.16), (0.85, 0.72, 0.12), (1.1, 0.76, 0.14)):
        a.add_patch(mp.Circle((x, y), s, fc=ACCENT, alpha=0.75, ec="none"))
    a.plot([0.05, 2.95], [0.6, 0.6], color="#B9C3CE", lw=1.2)
    a.text(1.5, 0.4, "Mỏ Mũi Tàu · 1,0 tr m³/năm", ha="center", fontsize=8.6, fontweight="bold", color=NAVY)
    a.text(1.5, 0.2, "nguyên khối, giấy phép tới 2043\n≈1,42 tr m³ đá thành phẩm/năm", ha="center", va="top", fontsize=6.6, color="#333")
    a.text(0.05, 3.1, "1 · NGÀNH NGHỀ", fontsize=7.6, fontweight="bold", color=ACCENT)
    b = fig.add_axes([0.35, 0.2, 0.30, 0.5])
    b.plot(YRS, [x * 100 for x in GPM["NNC"]], color=NAVY, lw=1.6, marker="o", ms=2.5)
    b.axhline(34.1, color=GREY, ls="--", lw=1); b.text(9.2, 26.5, "TB 2012–25: 34%", fontsize=6.2, color="#555")
    b.set_xticks(range(0, 15, 3)); b.set_xticklabels([YRS[i] for i in range(0, 15, 3)], fontsize=6.2); b.tick_params(labelsize=6.2)
    b.set_ylim(0, 60); b.set_ylabel("Biên gộp 4 quý, %", fontsize=6.6)
    fig.text(0.35, 0.83, "2 · CHU KỲ", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.35, 0.81, "Biên gộp 53% — đỉnh 15 năm; lợi nhuận\n4 quý 214 tỷ nhờ giá đá, sản lượng đã chạm trần", fontsize=6.3, color="#333", va="top")
    c = fig.add_axes([0.71, 0.13, 0.23, 0.56]); c.set_xlim(0, 1); c.set_ylim(30_000, 110_000); c.grid(False)
    for sp in ("left", "bottom"): c.spines[sp].set_visible(False)
    c.set_xticks([]); c.yaxis.tick_right(); c.tick_params(labelsize=6.4); c.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k")
    c.add_patch(mp.Rectangle((0.08, G["10"]), 0.42, G["90"] - G["10"], fc=GREEN, alpha=0.18, ec="none"))
    c.add_patch(mp.Rectangle((0.08, G["25"]), 0.42, G["75"] - G["25"], fc=GREEN, alpha=0.85, ec="none"))
    c.text(0.29, (G["25"] + G["75"]) / 2, "vùng\nhợp lý\n68–89k", ha="center", va="center", fontsize=6.3, color="white", fontweight="bold")
    c.plot([0.6, 0.88], [st36, st36], color=ACCENT, lw=1.2, ls="--"); c.text(0.74, st36 + 1500, f"biên đá về\n36%: {st36/1e3:.0f}k", ha="center", va="bottom", fontsize=5.6, color=ACCENT)
    c.axhline(PX, xmin=0.02, xmax=0.98, color=NAVY, lw=1.6); c.text(0.02, PX - 5200, "Giá 46,1k (03/11)", fontsize=6.6, color=NAVY, fontweight="bold")
    fig.text(0.70, 0.83, "3 · ĐỊNH GIÁ", fontsize=7.6, fontweight="bold", color=ACCENT)
    fig.text(0.70, 0.81, "dưới P10 của 729 bộ tham số;\nđiều kiện: biên đá không về đáy", fontsize=6.3, color="#333", va="top")
    fig.text(0.01, 0.005, "Nguồn: BCTN 2025 (giấy phép, công suất); biên gộp 4 quý từ cơ sở dữ liệu tài chính (Q4 mỗi năm); mô hình DCF hữu hạn 2027–2043 + tài sản theo sổ sách "
             "(ước lượng; vùng đậm = P25–P75, nhạt = P10–P90 của 729 bộ tham số); giá đóng cửa 03/11/2026.", fontsize=5.8, color="#666", va="bottom", wrap=True)
    fig.savefig(os.path.join(FIGS, "fig_00_hero.png"), dpi=200); plt.close(fig)
    pd.DataFrame([("grid_p10", G["10"]), ("grid_p25", G["25"]), ("grid_p75", G["75"]), ("grid_p90", G["90"]), ("stress_gpm36", round(st36)), ("gia_0311", PX)],
                 columns=["chi_tieu", "gia_tri"]).to_csv(os.path.join(FIGS, "fig_00_hero.csv"), index=False)

    # 11 BIEN GOP CHU KY — NNC & ngành
    fig, ax = plt.subplots(figsize=(7.2, 3.2)); fig.subplots_adjust(bottom=0.2, left=0.08, right=0.98, top=0.9)
    cols = {"NNC": ACCENT, "KSB": NAVY, "DHA": GREEN, "VLB": GREY}
    for t, ys in GPM.items():
        xs = [i for i, y in enumerate(ys) if y is not None]
        ax.plot(xs, [ys[i] * 100 for i in xs], color=cols[t], lw=2.0 if t == "NNC" else 1.2, marker="o", ms=2.5, label=t)
    ax.axhline(34.1, color=ACCENT, ls=":", lw=1); ax.text(1.6, 45, "đường chấm: NNC bình quân 2012–2025 = 34%", fontsize=7, color=ACCENT)
    ax.set_xticks(range(15)); ax.set_xticklabels(YRS, fontsize=6.6, rotation=45); ax.set_ylabel("Biên gộp 4 quý, %"); ax.set_ylim(0, 60)
    ax.legend(fontsize=7, ncol=4, loc="upper left", frameon=False)
    ax.set_title("Biên gộp các mã đá niêm yết phía Nam 2012–Q3/2026: NNC ở đỉnh, ngành không đồng loạt ở đỉnh")
    B.save(fig, "fig_11_margin_cycle", "Nguồn: cơ sở dữ liệu tài chính (biên gộp lũy kế 4 quý tại quý 4 mỗi năm và Q3/2026); NNC 2012–2019 gồm cả mỏ Núi Nhỏ đã đóng.",
           pd.DataFrame({"nam": YRS, **{t: ys for t, ys in GPM.items()}})); plt.close(fig)

    # 12 BA KICH BAN
    fig, ax = plt.subplots(figsize=(7.2, 2.8)); fig.subplots_adjust(bottom=0.2, left=0.2, right=0.97, top=0.88)
    for i, (lab, (lo, hi)) in enumerate(SC.items()):
        ax.barh(i, hi - lo, left=lo, color=[GREEN, NAVY, ACCENT][i], alpha=0.85, height=0.5)
        ax.text(hi + 1500 if i < 2 else lo - 1500, i, f"{vn(lo/1e3,0)}–{vn(hi/1e3,0)}k", va="center", ha="left" if i < 2 else "right", fontsize=7.5)
    ax.axvline(PX, color="black", lw=1.4); ax.text(PX + 800, 1.45, "giá 46,1k", fontsize=7)
    ax.axvline(TAM, color=GREY, lw=1, ls="--"); ax.text(TAM + 800, 1.45, f"kỳ vọng {vn(TAM/1e3,1)}k", fontsize=7, color="#555")
    ax.set_yticks(range(3)); ax.set_yticklabels(list(SC)); ax.invert_yaxis(); ax.set_xlim(0, 160_000)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_title("Ba kịch bản (đ/cp): mỗi thanh từ 'giá tăng theo lạm phát từ 2031' tới 'giữ giá trị thực'")
    B.save(fig, "fig_12_scenarios", "Nguồn: mô hình nhóm nghiên cứu (ước lượng). Tiêu cực = gộp 'cung mới ép giá, 0,8 tr m³ × 250k từ 2028' (20%) và 'giá về mặt bằng 2023–24' (5%).",
           pd.DataFrame([(a, round(b[0]), round(b[1])) for a, b in SC.items()], columns=["kich_ban", "g2031", "gia_thuc"])); plt.close(fig)

    # 13 FOOTBALL FIELD
    rows = [("Lưới 729 bộ tham số (P10–P90)", G["10"], G["90"]), ("  vùng hợp lý (P25–P75)", G["25"], G["75"]),
            ("Kịch bản cơ sở (hai đường giá)", C["co_so|g2031"], C["co_so|real"]),
            ("Biên cụm về bình quân chu kỳ từ 2028", st1, st1), ("Biên đá về 36% từ 2028", st36, st36),
            ("Gordon P/B, ROE 12–20%", O["gordon"]["ROE 12%"]["ps"], O["gordon"]["ROE 20%"]["ps"])]
    fig, ax = plt.subplots(figsize=(7.2, 3.0)); fig.subplots_adjust(bottom=0.18, left=0.36, right=0.97, top=0.9)
    for i, (lab, lo, hi) in enumerate(rows):
        if hi - lo < 500: ax.plot(lo, i, "D", color=ACCENT, ms=6); ax.text(lo + 1500, i, k(lo), va="center", fontsize=7)
        else: ax.barh(i, hi - lo, left=lo, color=NAVY if i != 5 else GREY, alpha=0.8 if i else 0.35, height=0.5); ax.text(hi + 1500, i, f"{k(lo)}–{k(hi)}", va="center", fontsize=7)
    ax.axvline(PX, color="black", lw=1.4); ax.text(PX + 800, 2.5, "giá 46,1k", fontsize=7)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=7.4); ax.invert_yaxis(); ax.set_xlim(20_000, 125_000)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_title("Các thước đo giá trị (đ/cp) so với giá 03/11/2026")
    B.save(fig, "fig_13_football_field", "Nguồn: mô hình nhóm nghiên cứu (ước lượng). Gordon P/B = (ROE − 3%)/(13% − 3%) × vốn chủ/cp 29.915 — đối chiếu thô vì mỏ có hạn 2043 và 1/3 vốn chủ là tiền.",
           pd.DataFrame(rows, columns=["thuoc_do", "thap", "cao"])); plt.close(fig)

    # 14 DO NHAY
    keep = [("r 11%", "r 15%", "Lãi suất chiết khấu 11% / 15%"), ("K chi phi 0,87", "K chi phi 1,07", "Chi phí ±10%"),
            ("W 35/50/10/5", "W 15/60/20/5", "Xác suất tích cực 35% / 15%"), ("SL co_so 1,20 ca ky 2028+", None, "Sản lượng 1,2 tr m³ từ 2028"),
            ("[cu] vach gia co_so 300 (2028-30) thay truot 360/340/320", None, "Giá cơ sở 300k (2028–30)"),
            ("bo LN cho thue Nui Nho", None, "Không có thu nhập cho thuê Núi Nhỏ"),
            ("(+) tra truoc dai han CNBP 59,2: PV khau tru phi tien mat 12,8/nam x 4,6 nam (CHUA XAC MINH ban chat)", None, "Chi phí trả trước dài hạn là phi tiền mặt"),
            ("MVC: han GP Tan Lap 2045", "MVC: han GP Tan Lap 2035", "Giá trị cổ phần MVC (giấy phép mỏ MVC 2045 / 2035)")]
    data = [(lab, TOR[a], TOR[b] if b else 0.0) for a, b, lab in keep]
    fig, ax = plt.subplots(figsize=(7.2, 3.3)); fig.subplots_adjust(bottom=0.16, left=0.42, right=0.97, top=0.9)
    for i, (lab, u, d) in enumerate(data):
        for v in (u, d):
            if v: ax.barh(i, v, color=GREEN if v > 0 else ACCENT, height=0.55); ax.text(v + (600 if v > 0 else -600), i, f"{v/1e3:+.1f}k".replace(".", ","), va="center", ha="left" if v > 0 else "right", fontsize=6.8)
    ax.axvline(0, color="black", lw=0.8); ax.set_yticks(range(len(data))); ax.set_yticklabels([d[0] for d in data], fontsize=7.2); ax.invert_yaxis()
    ax.set_xlim(-14_000, 14_000); ax.xaxis.set_major_formatter(lambda v, p: f"{v/1e3:+.0f}k")
    ax.set_title(f"Độ nhạy quanh giá trị kỳ vọng {vn(TAM/1e3,1)}k đ/cp")
    B.save(fig, "fig_14_sensitivity", "Nguồn: mô hình nhóm nghiên cứu (ước lượng); mỗi thanh đổi một giả định, giữ nguyên phần còn lại.",
           pd.DataFrame(data, columns=["gia_dinh", "len", "xuong"])); plt.close(fig)

    # 23 CAU NOI co_so (d/cp, TB hai duong gia)
    br = {kk: (O["bridge"]["g2031"][kk] + O["bridge"]["real"][kk]) / 2 * 1e9 / 21.92e6 for kk in O["bridge"]["g2031"] if kk not in ("TONG", "TONG_dcp")}
    lab = {"DCF_Mui_Tau_2027_43_gom_cho_thue": "Mỏ Mũi Tàu\n2027–43 (+thuê)", "Q4_2026": "LN\nQ4/2026", "tien_rong_sau_nghia_vu": "Tiền ròng\nsau nghĩa vụ",
           "ky_quy_PHMT": "Ký quỹ +\nthuế hoãn lại", "thue_hoan_lai": None, "NHC_so_sach": "NHC\n(sổ sách)", "CIP_TamLap_so_sach": "Tam Lập 1 khu II\n(vốn đã chi)",
           "tre_GP_ky_vong": "Rủi ro trễ\ngiấy phép", "co_phan_MVC_10_3pct": "10,3% MVC\n(giá trị nội tại)"}
    br["ky_quy_PHMT"] += br.pop("thue_hoan_lai")
    fig, ax = plt.subplots(figsize=(7.2, 3.1)); fig.subplots_adjust(bottom=0.25, left=0.08, right=0.98, top=0.9)
    cum = 0
    for i, (kk, v) in enumerate(br.items()):
        ax.bar(i, v, bottom=cum if v >= 0 else cum + v, color=NAVY if v >= 0 else ACCENT, width=0.6); ax.text(i, cum + max(v, 0) + 800, k(v), ha="center", fontsize=6.6); cum += v
    ax.bar(len(br), cum, color=GREEN, width=0.6); ax.text(len(br), cum + 800, k(cum), ha="center", fontsize=7, fontweight="bold")
    ax.axhline(PX, color="black", lw=1, ls="--"); ax.text(len(br) - 0.4, PX + 1200, "giá 46,1k", fontsize=6.8, ha="right")
    ax.set_xticks(range(len(br) + 1)); ax.set_xticklabels([lab[kk] for kk in br] + ["Kịch bản\ncơ sở"], fontsize=6.3)
    ax.yaxis.set_major_formatter(lambda v, p: f"{v/1e3:.0f}k"); ax.set_title("Kịch bản cơ sở cộng từ các phần (đ/cp, trung bình hai đường giá)")
    B.save(fig, "fig_23_bridge", "Nguồn: mô hình nhóm nghiên cứu (ước lượng); số dư BCTC riêng 30/9/2026. Cổ phần MVC định giá bằng mô hình nội tại MVC, giải sở hữu chéo đồng thời, không dùng thị giá.",
           pd.DataFrame([(kk, round(v)) for kk, v in br.items()], columns=["thanh_phan", "dcp"])); plt.close(fig)
    print("figs ok")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("figs", "all"): figs()
    if mode in ("pdf", "all"):
        md = os.path.join(HERE, "NNC_DD_investor_report_20261103.md")
        B.pdf(md, md.replace(".md", ".pdf")); print("pdf ok")
