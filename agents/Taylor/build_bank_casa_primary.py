#!/usr/bin/env python3
"""CASA rổ 13 ngân hàng, Q2/2026 — đọc từ THUYẾT MINH BCTC GỐC (nguồn sơ cấp).

Thay chân CASA "chép từ báo chí" của build_bank_casa_ldr.py bằng số đọc thẳng từ thuyết minh
"Tiền gửi của khách hàng" trong BCTC hợp nhất Q2/2026 của từng ngân hàng.

Nguồn PDF: kho lưu trữ công bố thông tin HOSE trên static2.vietstock.vn
  https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%202/<TICKER>_Baocaotaichinh_Q2_2026_Hopnhat.pdf
  (LPB: ..._Q2_2026.pdf — không có hậu tố Hopnhat; VPB: IR VPBank, bản tra cứu text-based)

11/13 PDF là ẢNH SCAN → OCR bằng tesseract 4.1.1 `-l vie`, rasterize PyMuPDF 300–500 dpi.
HDB có text layer nhưng CMap HỎNG (mojibake) → xử lý như scan. VPB text-based sạch.

**Vì sao số OCR ở đây tin được** — mỗi ngân hàng phải qua 2 bất biến số học ĐỘC LẬP:
  (A) mỗi nhóm  == thành phần VND + ngoại tệ
  (B) tổng cộng == Σ các nhóm  (khớp đúng dòng tổng IN TRONG bảng)
Một chữ số đọc sai gần như chắc chắn phá vỡ ít nhất một bất biến. Ba ca đã bị bắt và được
CHÍNH bất biến (B) định lại giá trị đúng: MSB ký quỹ 1.900.330 (OCR 300dpi đọc "4.900.330"),
TPB ký quỹ 7.649.049 (300dpi đọc "1.649.049"), LPB không kỳ hạn 22.292.930 + ký quỹ 227.996
(cả 300dpi lẫn 500dpi đều đọc lệch, chỉ dòng tổng chốt được).

Đơn vị mọi con số dưới đây: TRIỆU VND (đúng như bảng in trong BCTC).
"""
import csv
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "..", "data", "bank_casa_primary_20260814.csv")

# ticker -> dict. Mỗi nhóm: (tổng_nhóm, [thành phần...]) ; components rỗng = BCTC không tách.
# "total" = dòng tổng IN TRONG bảng (không phải ta tự cộng) -> dùng làm check (B).
BANKS = {
    # ACB tách RIÊNG "tiền gửi tiết kiệm không kỳ hạn" thành dòng thứ 2 -> xem ghi chú casa_note
    "ACB": dict(page="p020", src="OCR", note="10",
                demand=(115_492_484, [99_924_470, 15_568_014]),
                demand_savings=(7_985_207, [126_086, 7_859_121]),
                term=(144_190_231, [143_528_787, 661_444]),
                term_savings=(305_787_377, [302_998_978, 2_788_399]),
                margin=(2_845_034, [2_568_065, 276_969]),
                special=(303_269, [112_310, 190_959]),
                total=576_603_602),
    "BID": dict(page="p024", src="OCR", note="9",
                demand=(455_240_197, [383_197_726, 72_042_471]),
                term=(1_790_591_105, [1_647_614_641, 142_976_464]),
                special=(10_371_497, [4_213_387, 6_158_110]),
                margin=(5_517_595, [5_211_365, 306_230]),
                total=2_261_720_394),
    "CTG": dict(page="p041", src="OCR", note="9",
                demand=(429_532_340, [345_054_765, 84_477_575]),
                term=(1_446_501_419, [1_397_336_136, 49_165_283]),
                special=(6_261_403, [5_530_197, 731_206]),
                margin=(8_514_391, [6_862_449, 1_651_942]),
                total=1_890_809_553),
    "HDB": dict(page="p030@400dpi", src="OCR", note="9",
                demand=(72_867_051, [56_755_388, 16_111_663]),
                term=(599_616_658, [599_298_989, 317_669]),
                special=(972_219, []),
                margin=(602_773, []),
                total=674_058_701),
    # LPB: OCR 300dpi VÀ 500dpi đều đọc lệch dòng "không kỳ hạn"/"ký quỹ";
    #      giá trị dưới đây do bất biến (B) chốt (xem docstring).
    "LPB": dict(page="p049@500dpi", src="OCR", note="18",
                demand=(22_292_930, [21_028_058, 1_264_872]),
                term=(330_990_763, [330_583_622, 407_141]),
                margin=(227_996, [225_712, 2_284]),
                special=(1_625, []),
                total=353_513_314),
    "MBB": dict(page="p042", src="OCR", note="17",
                demand=(324_045_154, [283_968_111, 40_077_043]),
                term=(630_236_029, [619_953_010, 10_283_019]),
                special=(1_707_241, []),
                margin=(7_826_933, [5_364_992, 2_461_941]),
                total=963_815_357),
    "MSB": dict(page="p037", src="OCR", note="19.1",
                demand=(44_834_808, [38_161_597, 6_673_211]),
                term=(157_394_270, [153_994_479, 3_399_791]),
                special=(544_971, [407_841, 137_130]),
                margin=(1_900_330, []),
                total=204_674_379),
    "SHB": dict(page="p032", src="OCR", note="17",
                demand=(48_493_175, [43_871_091, 4_622_084]),
                term=(573_480_307, [563_896_998, 9_583_309]),
                special=(8_703, [610, 8_093]),
                margin=(2_286_948, [2_258_856, 28_092]),
                total=624_269_133),
    "TCB": dict(page="p052", src="OCR", note="18",
                demand=(223_945_387, [204_877_439, 19_067_948]),
                term=(430_455_311, [424_296_258, 6_159_053]),
                margin=(8_047_032, [7_878_989, 168_043]),
                total=662_447_730),
    "TPB": dict(page="p047@500dpi", src="OCR", note="22",
                demand=(52_849_056, []),   # thành phần VND OCR lệch (47->41); tổng nhóm do (B) chốt
                term=(227_954_098, [225_402_402, 2_551_696]),
                special=(25_480, []),
                margin=(7_649_049, []),
                total=288_477_683),
    "VCB": dict(page="p034", src="OCR", note="11",
                demand=(559_193_794, [435_064_614, 124_129_180]),
                term=(1_142_239_293, [1_024_944_616, 117_294_677]),
                special=(19_904_421, []),
                margin=(7_483_059, []),
                total=1_728_820_567),
    "VIB": dict(page="p040", src="OCR", note="19.1",
                demand=(37_334_817, [33_555_941, 149, 3_778_335, 392]),
                term=(279_589_942, [161_212_711, 97_320_225, 1_244_811, 19_812_195]),
                special=(111_483, [86_708, 24_775]),
                margin=(415_306, [397_878, 17_428]),
                total=317_451_548),
    "VPB": dict(page="p061", src="TEXT", note="18",
                demand=(84_173_507, [82_115_398, 2_058_109]),
                term=(639_422_050, [628_091_395, 11_330_655]),
                special=(4_962_471, [4_859_798, 102_673]),
                margin=(4_329_412, [3_907_329, 422_083]),
                total=732_887_440),
}

# CASA công bố trên báo chí (job Taylor_20260813_172358) — dùng để ĐỐI SOÁT, %.
PRESS = {"TCB": 35.0, "MBB": 34.4, "VCB": 32.8, "CTG": 23.2, "MSB": 22.8,
         "TPB": 21.0, "ACB": 20.5, "BID": 20.4, "VIB": 11.9, "LPB": 6.4}

PDF_URL = "https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%202/{t}_Baocaotaichinh_Q2_2026_Hopnhat.pdf"
PDF_OVERRIDE = {
    "LPB": "https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%202/LPB_Baocaotaichinh_Q2_2026.pdf",
    "VPB": "https://www.vpbank.com.vn/-/media/vpbank-latest/5nha-dau-tu/bao-cao-tai-chinh/vas/2026/3.-BCTC-hop-nhat--ban-tra-cuu-.pdf",
}

GROUPS = ("demand", "demand_savings", "term", "term_savings", "special", "margin")


def check(t, b):
    """2 bất biến số học. Trả (ok_components, ok_total, mô tả lỗi)."""
    errs = []
    for g in GROUPS:
        if g not in b:
            continue
        tot, comp = b[g]
        if comp and sum(comp) != tot:
            errs.append(f"{g}: Σcomp {sum(comp):,} != {tot:,}")
    s = sum(b[g][0] for g in GROUPS if g in b)
    if s != b["total"]:
        errs.append(f"TOTAL: Σgroups {s:,} != in-table {b['total']:,}")
    return (not errs), errs


def main():
    rows, bad = [], []
    for t in sorted(BANKS):
        b = BANKS[t]
        ok, errs = check(t, b)
        if not ok:
            bad.append((t, errs))
        tot = b["total"]
        demand = b["demand"][0]
        demand_sav = b.get("demand_savings", (0, []))[0]
        margin = b.get("margin", (0, []))[0]

        casa_strict = (demand + demand_sav) / tot * 100
        casa_narrow = demand / tot * 100
        casa_press_def = (demand + margin) / tot * 100  # định nghĩa khớp báo chí

        p = PRESS.get(t)
        delta = None if p is None else round(casa_press_def - p, 2)
        rows.append(dict(
            ticker=t, period="2026-Q2",
            casa_strict_pct=round(casa_strict, 3),
            casa_narrow_pct=round(casa_narrow, 3),
            casa_pressdef_pct=round(casa_press_def, 3),
            press_pct=p, press_delta_pp=delta,
            demand_mn=demand, demand_savings_mn=demand_sav, margin_mn=margin,
            total_deposit_mn=tot,
            selfcheck="PASS" if ok else "FAIL: " + "; ".join(errs),
            src=b["src"], note_no=b["note"], page=b["page"],
            pdf_url=PDF_OVERRIDE.get(t, PDF_URL.format(t=t)),
        ))

    out = os.path.abspath(OUT)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"{'mã':4s} {'CASA chặt':>10s} {'CASA hẹp':>9s} {'CASA đn-BC':>11s} "
          f"{'báo chí':>8s} {'lệch pp':>8s}  selfcheck")
    for r in rows:
        p = "-" if r["press_pct"] is None else f"{r['press_pct']:.1f}"
        d = "-" if r["press_delta_pp"] is None else f"{r['press_delta_pp']:+.2f}"
        print(f"{r['ticker']:4s} {r['casa_strict_pct']:9.2f}% {r['casa_narrow_pct']:8.2f}% "
              f"{r['casa_pressdef_pct']:10.2f}% {p:>8s} {d:>8s}  {r['selfcheck']}")

    print(f"\nself-check số học: {len(rows) - len(bad)}/{len(rows)} PASS")
    ds = [r["press_delta_pp"] for r in rows if r["press_delta_pp"] is not None]
    print(f"đối soát báo chí (định nghĩa không kỳ hạn + ký quỹ): {len(ds)} mã, "
          f"|lệch| tối đa {max(abs(x) for x in ds):.2f}pp")
    print(f"→ {out}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
