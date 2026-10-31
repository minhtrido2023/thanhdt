"""Hình đổi cho bản v3 (hiệu đính 31/10/2026). Ghi file *_v3 để KHÔNG đè hình của bản v2 đã gửi.
Đổi: fig_06 (thêm QĐ 1917 chống lẩn tránh), fig_12 (dòng tiền TLSH/liên danh theo GAPS2 §2–4), fig_13 (R5 TLSH/liên danh BT nâng xác suất).
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I build_report.py figs3
"""
import os
from figs_part import FIGS, NAVY, ACCENT, GREY, LIGHT, setup_mpl, save


def figs_v3():
    import pandas as pd
    plt = setup_mpl()

    # 06 Chuỗi giá trị ---------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3)
    boxes = [(0.1, 1.1, "Quặng sắt, than cốc\n(nhập khẩu + nội địa)", LIGHT, NAVY), (2.3, 1.1, "Lò cao – lò thổi (BOF)\nthép thô 16 tr t/năm", NAVY, "white"),
             (4.6, 2.0, "Thép XD, cuộn CLC\n(Hải Dương, Dung Quất)", "#E8EEF5", NAVY), (4.6, 0.2, "HRC 9 tr t/năm\n(Dung Quất)", ACCENT, "white"),
             (7.3, 0.2, "Ống thép, tôn mạ\n(hạ nguồn, nội địa + XK)", "#E8EEF5", NAVY), (7.3, 2.0, "Nhà ở, hạ tầng\n(nội địa ≈74–79% DT)", "#F3F5F7", NAVY)]
    for x0, y0, t, fc, tc in boxes:
        ax.add_patch(plt.Rectangle((x0, y0), 2.15, 0.8, fc=fc, ec=NAVY, lw=0.8))
        ax.text(x0 + 1.075, y0 + 0.4, t, ha="center", va="center", fontsize=6.6, color=tc, weight="bold")
    arr = dict(arrowstyle="->", color=GREY, lw=1.2)
    for (a0, a1) in (((2.25, 1.5), (2.3, 1.5)), ((4.45, 1.6), (4.6, 2.3)), ((4.45, 1.4), (4.6, 0.6)), ((6.75, 0.6), (7.3, 0.6)), ((6.75, 2.4), (7.3, 2.4))):
        ax.annotate("", a1, a0, arrowprops=arr)
    ax.text(0.1, 0.25, "Bảo hộ HRC Trung Quốc: AD 23,1–27,83% (QĐ 1959);\nchống lẩn tránh 27,83% khổ rộng (QĐ 1917, từ 28/07/2026);\nrà soát QĐ 1902", ha="left", fontsize=6.3, color=ACCENT)
    ax.set_title("Mô hình tích hợp: từ quặng tới HRC và hạ nguồn — biên phụ thuộc spread và bảo hộ")
    save(fig, "fig_06_value_chain_v3", "Minh họa của nhóm nghiên cứu. Công suất: thông cáo công ty 06/2026; AD: QĐ 1959/QĐ-BCT (04/07/2025); chống lẩn tránh chính thức QĐ 1917/QĐ-BCT (hiệu lực 28/07/2026, theo báo chí; thay QĐ 612 tạm thời); rà soát QĐ 1902/QĐ-BCT (27/07/2026); tỷ trọng nội địa: BCTC soát xét 6T/2026.")
    plt.close(fig)

    # 12 Sơ đồ TLSH --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4.1)
    def box(x0, y0, w, h, t, fc, tc=NAVY):
        ax.add_patch(plt.Rectangle((x0, y0), w, h, fc=fc, ec=NAVY, lw=0.8)); ax.text(x0 + w / 2, y0 + h / 2, t, ha="center", va="center", fontsize=6.4, color=tc, weight="bold")
    box(0.1, 1.5, 2.0, 1.0, "HPG\n(công ty mẹ)", NAVY, "white")
    box(3.8, 2.9, 3.1, 0.9, "(1) TLSH — 25,13%\n9.915 tỷ (giá gốc)", "#FBF1EC")
    box(3.8, 1.5, 3.1, 0.9, "(2) BĐS Hòa Phát — còn 26,55%\n2.814 tỷ (giá gốc)", "#F3F5F7")
    box(3.8, 0.05, 3.1, 1.05, "(3) Thành viên liên danh\nĐại lộ sông Hồng (BT)\nchuyển 1.600; dư HN 100 (30/9)", "#FBF1EC")
    box(7.5, 2.9, 2.4, 0.9, "Dự án KĐT 696 ha\n(Thư Lâm–Đông Anh)", "#FBF1EC")
    box(7.5, 0.4, 2.4, 1.3, "Chưa rõ đích ≈1,4–1,9\nnghìn tỷ (ước lượng)\nký quỹ DH +251;\nmẹ: cọc 361 + BCC 135", "#FFF6E0")
    ax.annotate("", (3.8, 3.35), (2.1, 2.3), arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.1))
    ax.text(0.1, 3.05, "1.920 tiền (H1) + 7.995 bằng\n778,4 tr CP BĐS HP (Q3):\n10.271 đ/cp ≈ mệnh giá\n(NQ 10 trước đó: 32.000 đ/cp)", fontsize=6.3, color=ACCENT)
    ax.annotate("", (3.8, 1.95), (2.1, 1.95), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0))
    ax.annotate("", (3.8, 0.55), (2.1, 1.6), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0))
    ax.annotate("", (7.5, 3.35), (6.9, 3.35), arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0))
    ax.set_title("Ba lớp phơi nhiễm: ≈8,5% vốn chủ ở TLSH + BĐS HP, cộng liên danh BT")
    save(fig, "fig_12_tlsh_v3", "Nguồn: BCTC riêng công ty mẹ Q3/2026 (liên kết 12.728,9; thu nhập khác 210,95 tỷ; VI.4); BCTC soát xét 6T/2026 TM6b, TM9; BCTC hợp nhất Q3 VI.4, LCTT 9T; NQ HĐQT 10 & 13/NQHP-2026; báo chí (dự án, thành viên liên danh). Đích chưa rõ là ước lượng của nhóm nghiên cứu.",
         pd.DataFrame({"khoan": ["TLSH", "BĐS HP 26,55%", "Phai thu lien danh HN 30/9", "Chua ro dich (thap)", "Chua ro dich (cao)", "Ky quy DH HN tang", "Coc/ky quy cty me", "BCC cty me", "Gia hoan doi d/cp"],
                       "ty": [9915, 2813.9, 100, 1370, 1870, 251, 361.2, 134.6, 10271]}))
    plt.close(fig)

    # 13 Ma trận rủi ro ----------------------------------------------------
    rk = pd.DataFrame([("R1", "Rà soát AD HRC hạ mức", 2, 5), ("R2", "Nhà ở gãy – thép XD H2/27", 3, 3),
                       ("R3", "Spread HRC về 150–200 USD/t", 2, 4), ("R4", "Hết ưu đãi thuế / DQ2 'mở rộng'", 3, 3),
                       ("R5", "TLSH / liên danh BT: góp thêm", 3, 2), ("R6", "VinMetal cạnh tranh HRC", 3, 2),
                       ("R7", "Cầm cố CP cá nhân / công bố TT", 2, 2)], columns=["ma", "rui_ro", "xac_suat_1_5", "tac_dong_1_5"])
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for i in range(1, 6):
        for j in range(1, 6):
            s = i * j
            ax.add_patch(plt.Rectangle((i - 0.5, j - 0.5), 1, 1, color="#F6E3DE" if s >= 10 else ("#F3F5F7" if s < 6 else "#FBF1EC"), lw=0))
    offs = {"R2": (-0.22, 0.2), "R4": (0.15, -0.2), "R5": (-0.22, 0.2), "R6": (0.15, -0.2), "R7": (0, 0)}
    for _, r in rk.iterrows():
        dx, dy = offs.get(r["ma"], (0, 0))
        ax.plot(r["xac_suat_1_5"] + dx, r["tac_dong_1_5"] + dy, "o", color=ACCENT if r["xac_suat_1_5"] * r["tac_dong_1_5"] >= 9 else NAVY, ms=9)
        ax.text(r["xac_suat_1_5"] + dx + 0.12, r["tac_dong_1_5"] + dy, r["ma"], fontsize=8, va="center", fontweight="bold")
    ax.text(5.75, 5.4, "\n".join(f"{a}  {b}" for a, b in zip(rk["ma"], rk["rui_ro"])), fontsize=7.3, va="top", ha="left", linespacing=1.6)
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5); ax.grid(False)
    ax.set_xticks(range(1, 6), ["Rất thấp", "Thấp", "TB", "Cao", "Rất cao"], fontsize=7.5)
    ax.set_yticks(range(1, 6), ["Rất nhỏ", "Nhỏ", "TB", "Lớn", "Rất lớn"], fontsize=7.5)
    ax.set_xlabel("Xác suất trong 12–18 tháng (nhận định)"); ax.set_ylabel("Tác động lên giá trị")
    ax.set_title("AD và spread: tác động lớn nhất; nhà ở, thuế và TLSH/liên danh: dễ xảy ra hơn")
    fig.tight_layout(rect=(0, 0.07, 0.68, 1))
    save(fig, "fig_13_risk_matrix_v3", "Nguồn: nhận định của nhóm nghiên cứu (thang 1–5, chủ quan); tham chiếu đọc ngành độc lập 31/10/2026; hiệu đính 31/10/2026 (R5 nâng xác suất).", rk)
    plt.close(fig)
    print("figs v3 ok", FIGS)
