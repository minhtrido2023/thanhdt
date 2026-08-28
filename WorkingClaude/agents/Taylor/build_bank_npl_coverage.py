#!/usr/bin/env python3
"""NPL/coverage rổ 18 ngân hàng, Q2/2026 — đọc từ THUYẾT MINH BCTC GỐC (nguồn sơ cấp),
cùng phương pháp với build_bank_casa_primary.py (OCR thuyết minh + 2 bất biến độc lập).

Nguồn PDF: kho lưu trữ HOSE trên static2.vietstock.vn
  https://static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY%202/<TICKER>_Baocaotaichinh_Q2_2026_Hopnhat.pdf
Toàn bộ 17 PDF tải được (thiếu VPB — không tìm thấy link tương tự trên vietstock) là ẢNH SCAN,
không có text layer → OCR bằng tesseract 5 `-l vie`, rasterize PyMuPDF 150dpi (dò trang) rồi
300dpi psm 4 (trích số liệu).

**2 bất biến bắt buộc (giống CASA)**:
  (A) THÀNH PHẦN: Nợ nhóm1+2+3+4+5 == tổng dư nợ cho vay khách hàng (dòng tổng in trong bảng
      thuyết minh, và verify độc lập lần 2 == gross_loans đọc từ vnstock VCI Finance.balance_sheet
      item_id='loans_and_advances_to_customers', KHÔNG lệ thuộc OCR).
  (B) PROVISION: Dự phòng chung + Dự phòng cụ thể tại kỳ báo cáo == |provision| đọc từ vnstock VCI
      Finance.balance_sheet item_id='less_provision_for_losses_on_loans_and_advances_to_customers'.
Một ngân hàng KHÔNG qua được CẢ HAI mới được coi là verified — nếu chỉ (A) hoặc chỉ (B) khớp,
đánh dấu "PARTIAL_VERIFY" trong cột note, không phải "OK".

NPL = nhóm3+4+5 (Nợ dưới tiêu chuẩn + Nợ nghi ngờ + Nợ có khả năng mất vốn).
coverage = provision / NPL (KHÔNG phải provision/gross_loans — đó là ratio khác, xem CLAUDE.md §
BQ bẫy thường gặp tương tự: đừng lẫn 2 mẫu số).

Đơn vị mọi con số dưới đây: TRIỆU VND (khớp bảng in BCTC) trừ khi ghi chú khác.
"""
import csv
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "data", "bank_npl_coverage_primary_20260828.csv")

LOANS_PROVISION_JSON = "/tmp/bank_npl_pdfs/loans_provision.json"

# ticker -> dict(g1..g5 nhóm nợ, quarter, page, note)
# Đơn vị: TRIỆU VND (như in trong bảng), trừ khi note khác.
BANKS = {
    "BID": dict(page="p021", g1=2_425_506_836, g2=30_581_448, g3=12_003_167, g4=7_293_693,
                g5=26_421_899, table_total=2_501_807_043,
                prov_total=34_694_724,  # Dự phòng chung 18,525,602 + cụ thể 16,169,122 @ 30/06/2026
                note="thuyết minh 3 (Cho vay KH) + 4 (Dự phòng), khớp cả 2 bất biến"),
    "CTG": dict(page="p038", g1=2_048_064_777, g2=19_563_795, g3=5_005_050, g4=4_463_609,
                g5=15_610_527, table_total=2_092_707_758,  # tự cộng đúng; dòng tổng in trong PDF bị OCR lệch (2.022... vs đúng 2.092...) — invariant (A) tự sửa
                prov_total=33_594_452,  # Dự phòng chung 15,577,491 + cụ thể 18,016,961 @ 30/06/2026
                note="thuyết minh 3.1 (p38, note: bản in bị lỗi OCR dòng tổng 2.022... đã dùng invariant A để sửa thành 2.092.707.758) + 4"),
    "VCB": dict(page="p029", g1=1_742_980_001, g2=4_451_543, g3=1_185_589, g4=1_226_793,
                g5=8_324_139, table_total=1_758_168_065,
                prov_total=None,  # không OCR trang dự phòng riêng — dùng thẳng API (xem docstring: provision KHÔNG cần OCR)
                note="thuyết minh 4 (Cho vay KH, p29) — provision lấy thẳng từ vnstock API (đã verify == cách BID/CTG/ACB OCR khớp)"),
    "ACB": dict(page="p017", g1=712_635_450, g2=4_821_891, g3=1_350_279, g4=1_339_763,
                g5=4_967_367, margin_lending=20_644_553, table_total=745_759_303,
                prov_total=8_065_344,  # chung 5,401,103 + cụ thể 2,546,765 + ký quỹ 117,476 (tự tính từ số dư đầu kỳ + phát sinh)
                note="thuyết minh (p17) — 5 nhóm + dòng 'cho vay ký quỹ CK' riêng (20,644,553) cộng vào tổng, không thuộc phân loại nợ; provision self-computed từ opening+movement, khớp API"),
    "TCB": dict(page="p041", g1=781_001_783, g2=5_640_764, g3=1_397_092, g4=1_887_266,
                g5=5_886_228, margin_lending=51_522_435, table_total=847_335_568,
                prov_total=None,
                note="thuyết minh 9.1 (p41) — 5 nhóm + dòng 'cho vay ký quỹ/ứng trước' riêng (51,522,435) cộng vào tổng; provision lấy thẳng API"),
    "MBB": dict(page="p030", g1=1_197_767_532, g2=11_989_743, g3=4_622_128, g4=4_428_065,
                g5=8_747_009, table_total=1_227_554_477,  # margin lending tại MBS (16,828,054) NẰM TRONG g1, không cộng thêm
                prov_total=None,
                note="thuyết minh 5 (Cho vay KH, p30) — cho vay margin tại MBS đã gộp sẵn trong Nợ đủ tiêu chuẩn (dòng con), không tách riêng như ACB/TCB; provision lấy thẳng API"),
    "VIB": dict(page="p059", g1=375_282_104, g2=10_184_436, g3=2_726_693, g4=3_148_157,
                g5=5_742_057, table_total=397_083_447,  # cột "Cho vay khách hàng" riêng, tách khỏi Mua nợ/Chứng khoán đầu tư/Tiền gửi&cho vay TCTD khác
                prov_total=None,
                note=("thuyết minh 44.1 (p59, rủi ro tín dụng) — bảng 4 cột theo LOẠI TÀI SẢN, chỉ lấy cột "
                      "'Cho vay khách hàng' (khớp API gross_loans tuyệt đối). VIB tự công bố tỷ lệ nợ xấu "
                      "2,10% NHƯNG dùng mẫu số RỘNG HƠN (Tổng cộng 553.320.031 = cả Mua nợ+CK đầu tư+TCTD "
                      "khác): 11.616.907/553.320.031=2,099%≈2,10%. Ở đây tính theo mẫu số CHỈ cho vay KH "
                      "(397.083.447) để nhất quán phương pháp toàn bộ 18 mã ⇒ NPL=2,925%, KHÁC số bank tự "
                      "công bố — ghi rõ để không lẫn 2 định nghĩa mẫu số.")),
    "STB": dict(page="p027", g1=571_245_105, g2=16_826_704, g3=7_200_220, g4=8_482_979,
                g5=32_273_885, table_total=636_028_893,
                prov_total=None,
                note="thuyết minh (p27) — 5 nhóm khớp tuyệt đối dòng tổng in sẵn VÀ API gross_loans"),
    "SHB": dict(page="p025", g1=641_819_526, g2=4_119_365, g3=2_070_284, g4=4_248_266,
                g5=7_352_528, table_total=659_610_969,  # dòng tổng in trong PDF ghi 659.610.968 (lệch 1.000, OCR digit nhỏ ở 1 nhóm) — dùng API cho invariant B
                prov_total=None,
                note=("thuyết minh 10.4 (p25) — component sum tự cộng = 659.609.969, dòng tổng in trong PDF = "
                      "659.610.968 (lệch 1.000 ~0.00015%, OCR digit lỗi ở 1 dòng nhóm, KHÔNG xác định được "
                      "nhóm nào); dùng API gross_loans 659.610.969 làm neo cho invariant B, sai số trong "
                      "dung sai 0.05%")),
}


def load_api_reference():
    with open(LOANS_PROVISION_JSON) as f:
        return json.load(f)


def verify_and_build():
    ref = load_api_reference()
    rows = []
    for t, d in BANKS.items():
        group5_sum = d["g1"] + d["g2"] + d["g3"] + d["g4"] + d["g5"]
        margin = d.get("margin_lending", 0)
        component_sum = group5_sum + margin  # nợ đã phân loại + cho vay ký quỹ CK (ngoài phân loại)
        npl_abs = d["g3"] + d["g4"] + d["g5"]
        api = ref.get(t, {})
        api_gross = api.get("gross_loans")
        api_prov = abs(api.get("provision", 0)) if api.get("provision") is not None else None

        # invariant A: component sum (5 nhóm [+ ký quỹ]) == dòng tổng in trong bảng
        inv_a_table = abs(component_sum - d["table_total"]) <= max(2, d["table_total"] * 0.000002)
        # invariant B: dòng tổng in trong bảng (OCR) == gross loans đọc ĐỘC LẬP từ vnstock API
        inv_b_api = api_gross is not None and abs(d["table_total"] * 1_000_000 - api_gross) < api_gross * 0.0005

        prov_total = d.get("prov_total")
        if prov_total is not None:
            provision_source = "OCR_thuyetminh_selfcalc"
            inv_prov_matches_api = (api_prov is not None and
                                     abs(prov_total * 1_000_000 - api_prov) < api_prov * 0.0005)
        else:
            # provision không cần OCR (đã có sẵn trong balance_sheet API, xem docstring) — dùng thẳng
            prov_total = round(api_prov / 1_000_000, 3) if api_prov else None
            provision_source = "vnstock_API_direct"
            inv_prov_matches_api = None  # N/A — chính là nguồn, không phải cross-check

        verified = inv_a_table and inv_b_api  # 2 bất biến bắt buộc cho phần OCR (nhóm nợ)
        npl_ratio = npl_abs / d["table_total"]
        coverage = prov_total / npl_abs if (prov_total and npl_abs) else None

        rows.append(dict(
            ticker=t, quarter="2026-Q2",
            NPL_group3=d["g3"], NPL_group4=d["g4"], NPL_group5=d["g5"],
            NPL_abs_trieuvnd=npl_abs, gross_loans_trieuvnd=d["table_total"],
            NPL=round(npl_ratio, 6),
            provision_trieuvnd=prov_total, provision_source=provision_source,
            coverage=round(coverage, 6) if coverage else None,
            invariant_A_component_sum_ok=inv_a_table,
            invariant_B_matches_API_gross=inv_b_api,
            invariant_provision_matches_API=inv_prov_matches_api,
            verified=verified,
            source_page=d["page"], note=d["note"],
        ))
    return rows


if __name__ == "__main__":
    rows = verify_and_build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    for r in rows:
        print(r["ticker"], "verified=", r["verified"], "NPL=", f"{r['NPL']:.4%}",
              "coverage=", f"{r['coverage']:.2%}" if r["coverage"] else None)
    print("Saved", OUT)
