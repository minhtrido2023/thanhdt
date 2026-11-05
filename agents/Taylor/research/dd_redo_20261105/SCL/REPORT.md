# SCL — DD làm lại theo khung skill 03/11 · giá 04/11/2026 · job `Taylor_20261105_014130`

> Chỉ nghiên cứu, trung dung. Pháp lý/quản trị = WARNING. Số: `calc/model_scl_out.txt|json` (`$DNA_PYEXE -I calc/model_scl.py`). Lõi định giá = r3 03/11 (`dd_SCL_20261029/r3/calc/model_r3.py`, vốn đã dựng theo luật 03/11), chép nguyên văn sang `calc/scl_r3_core.py` và **tái lập**: `model_r3_out.txt` md5 `f9e7346c…` trùng bản gốc. BCTC HN/riêng Q3/2026 đã có ở `dd_SCL_20261029/src/` (không tải lại). Sector read: `sector_read_vlxd_nhe_aac_20261029.md` (Bobby, blind).

## 0. Kết luận (số chuẩn hoá liên mã — cơ sở CUM-quyền vì giá 04/11 còn quyền, ĐKCC 10/11)

| 38,84tr cp (cum) | Trước CK thanh khoản | Sau CK (4,50% @5 tỷ) |
|---|---|---|
| **Tâm** (kỳ vọng trọng số 3 nhánh 50/30/20) | 23.933 | **22.855** |
| P10 / P50 / P90 (lưới n=108) | 18.445 / 24.488 / 28.397 | **17.615 / 23.386 / 27.119** |

- Giá **30.000** (đóng cửa 04/11, cum): **+31,3% so tâm**, +10,6% so P90 ⇒ **TRÊN vùng (>P90)**.
- Sau quyền (44,84tr cp): tâm sau CK **21.394**, P10–P90 16.855–25.087; TERP @30.000 = 27.659 ⇒ +29,3% so tâm, cũng TRÊN vùng.
- Nhánh (cum, trước CK): CYCLICAL 21.880 · ADMIN_GATED 24.813 · STRUCTURAL 27.745 — kể cả nhánh biên đỉnh bền vẫn dưới giá.
- So r3 03/11 (tâm sau quyền 21.400): **0,0%**. Không lệch >10%.

## 1. Kiểm chứng giả thuyết
"Lợi nhuận lõi tăng thật" — **đúng**: biên gộp 9T/2026 40,1% (9T/25 36,1%), LNST mẹ 9T 94,4 vs 40,9; thu nhập tài chính/khác không đáng kể; kiểm toán 2025 chấp nhận toàn phần. "Giá rẻ vì tăng trưởng" — **không**: biên ròng TTM 12,7% là đỉnh 7 năm (BQ năm 2020–2025: 4,7–10,4%; `scl_r3_core.HIST`).

## 2. Chất lượng lợi nhuận
- DT thuần 9T 665,5 (+81%), LN gộp 267,2; tăng nhờ nhà máy Vĩnh Tân (Green SCL 85,8%) và cầu xây dựng 2026.
- Không vốn hoá lãi vay (lãi trả 14,3 < lãi ghi nhận 15,5). Không công bố cơ cấu mảng ⇒ không tách được bền/một lần theo mảng.
- Thuế suất thực ≈20,0% (Q3: 9,55/47,66).

## 3. Bảng cân đối — net cash thật (30/09/2026)
- Tiền 95,1; vay + thuê TC 416,5 ⇒ **nợ ròng 321,4** (1,4× EBITDA). XDCB dở dang 205,5 (Phả Lại 190,7; Vĩnh Tân GĐ2 14,8) tài trợ bằng vay (capex 9T 198,1 vs CFO 9,9).
- Phải thu KH 116,0 (~37 ngày); trả trước người bán 86,6. CFO 9T 9,9 vs LNST 94,4 — vốn lưu động hút tiền.
- Quyền mua 6,0tr cp @12.500 = 75 tỷ trả nợ ⇒ nợ ròng sau quyền ≈ 246 (ước lượng nếu phát hành đủ).

## 4. Ghi nhận doanh thu
Bán hàng (tro bay, gạch nhẹ, vữa) ghi nhận khi giao; không POC. Q4 dự phóng = Q3 (ước lượng) cho chân 2026E.

## 5. Cổ đông, thanh khoản
- Thanh khoản (BQ, 120 phiên tới 04/11): ADV trung vị **2,28 tỷ**; σ ngày 2,71%; spread CS 0,97%. 5 tỷ = 21,9 / 10,9 phiên ở 10% / 20% ADV ⇒ CK **4,50%** (1 tỷ 2,28%; 10 tỷ 6,17%).
- Free float/room: không có số mới trong job này (xem DD gốc) — ghi ở open_issues.

## 6. Pháp lý / quản trị — ⚠️ WARNING
Pha loãng 2,6 lần từ 2023 (thưởng, quyền, ESOP 0,92tr @10.000); vay 26 tỷ từ cổ đông lớn lãi 10%; khách hàng một tập đoàn BĐS = 58,5% phải thu. Tin công khai tới 29/10 không thấy khởi tố/xử phạt. Không vào tâm.

## 7. Định giá
- Giá trị = LN chuẩn hoá chu kỳ × P/E nội tại (1 − g/ROE)/(r − g) (7,7–8,8x) + dự án dở dang theo giá vốn − nợ tài trợ (ròng 0) + lãi vay của nợ dự án cộng lại (lãi P&L thực 4,96%) + 75 tỷ tiền quyền (cơ sở sau quyền).
- **Dự án mới (luật NPV=0):** Phả Lại đã chi 190,7 + còn ~72 (ước lượng) và Vĩnh Tân GĐ2 14,8 = giá vốn; không cộng lợi nhuận tương lai (thiếu giá/sản lượng/hợp đồng), không trừ rủi ro thừa cung (thiếu số vùng). Cơ sở dữ liệu: BCTC Q3/2026 XDCB, LCTT.
- **Kịch bản = 3 nhánh chế độ ngành** (Bobby 29/10: CYCLICAL 0,50 / ADMIN_GATED 0,30 / STRUCTURAL 0,20); mức quay về TB biên 100/50/0% là thiết kế nhóm nghiên cứu (ước lượng).
- **Lưới:** 3 nhánh × DT {TTM, 2026E} × biên chuẩn hoá {TB 2020–TTM, TB 2023–TTM, lệch biên gộp} × g {3,4,5%} × ROE {15,20%} ⇒ n=108.
- Cận dưới "toàn bộ nợ theo mệnh giá" (sau CK): cum 21.671, sau quyền 20.368.

## 8. Độ nhạy r (tâm cum SAU CK)
r = 13,5% @ lãi huy động 12T hiệu dụng 7,40% (CCTG 12M 02/11; điểm neo 03/11 = 7,40%; Big-4 12M 6,8%).
| Lãi huy động | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β=1,0 | 25.576 (+11,9%) | 24.138 (+5,6%) | 22.855 | 21.703 (−5,0%) | 20.661 (−9,6%) |
| β=0,5 | 24.138 (+5,6%) | 23.479 (+2,7%) | 22.855 | 22.264 (−2,6%) | 21.703 (−5,0%) |
Kể cả −100bp (25.576) giá 30.000 vẫn cao hơn 17%.

## 9. Mốc khoá trước & điều kiện đổi nhận định (hai chiều)
| Mốc | LÊN nếu | XUỐNG nếu |
|---|---|---|
| Quyền mua 10/11–08/12/2026 | Phát hành đủ, nợ ròng −75 tỷ | Không hết |
| BCTC Q4/2026 (~20/01/2027) | LNST ≥ 38 tỷ, CFO ≥ LNST, phải thu giảm | Biên gộp < 36%, phải thu tăng tiếp |
| Phả Lại vận hành (2027) | Công bố hợp đồng/sản lượng/giá ⇒ IRR (15% ⇒ +650 đ/cp sau quyền) | Trễ, vượt dự toán có số |
| BCTC kiểm toán 2026 | Chấp nhận toàn phần | Ngoại trừ |
Nhãn về TRONG vùng khi giá cum ≤ 27.119 (hoặc LN chuẩn hoá cao hơn ~32% so mô hình, hoặc lãi huy động thấp hơn ~2,3 điểm % — định giá ngược r3 `dd_SCL_20261029/r3/calc/reverse_r3_out.json` ở cùng giá 30.000).

## 10. Phụ lục — ĐỔI so với DD cũ và vì sao
| Mục | r3 03/11 | Redo 05/11 | Lý do |
|---|---|---|---|
| Khung mô hình | r3 | **giữ nguyên** (tái lập byte) | r3 đã đúng luật 03/11 |
| r | 13,5% @7,40% | 13,5% @7,40% (04/11) | lãi huy động không đổi |
| CK thanh khoản 5 tỷ | 4,55% (tới 03/11) | 4,50% (tới 04/11) | thêm 1 phiên dữ liệu |
| Vùng báo | P25–P75 sau quyền 18.600–23.900 | P10–P90 cum 17.615–27.119; sau quyền 16.855–25.087 | chuẩn hoá liên mã |
| Giá so | TERP vs sau quyền | cum vs cum (chính) + TERP vs sau quyền | giá 04/11 còn quyền |
- DD 29/10 bản đầu (tâm ~25.500, cách khác) đã bị thay ở r2/r3; lệch chính khi đó là dự án theo giá vốn và r neo lãi huy động.
