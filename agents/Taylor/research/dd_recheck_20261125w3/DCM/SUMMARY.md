# DCM — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_032448)

Nguồn: `REPORT_recheck_DCM.md` · mô hình rev9 (CONTROL lưới 2.430 kết cục sau CK = 27.393) · skeptic `dd_DCM_20261104/skeptic/r4.json` (KHÔNG chạy vòng mới) · E17 `ADJ_CENTER.md` + `adj.json` · `LEDGER_PROPOSAL_DCM.json` (rev5). Calc không bị TRIM.

**Bước 0:** KHÔNG có tham số nền bị phủ (không holding; r Δ 0 ở 25/11; RONIC = Ke, g 0; độ nhạy r tính từ mô hình).

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3% (dịch trục r lưới): **28.941 (+5,65%)**; r cố định 12,3% 28.881 (+5,43%). **E16:** nguyên văn **RẺ** — phân vị [fade 30, hold 1], N hiệu dụng 4.4 (asof 2026-11-20).
- D3/D4/V1/V3/V5/V6/V8: rev9 đã đủ. D3: quỹ KH&CN không phải capex tuân thủ thuần (quy tắc v của rev9 đúng), phần chi KH&CN không thành TSCĐ đưa vào E17 D1.
- Đính chính văn bản (skeptic r4): giá đã biết từ r5 (33.000)/r6 (32.100), không phải "từ rev7" — không đổi số.

## (b) Tâm / vùng / nhãn
| | rev9 (sổ rev4) | recheck (proposal rev5) | Δ |
|---|---|---|---|
| Tâm | 27.393 | 27.393 | 0% |
| Vùng P25–P75 | 24.385–30.479 | 24.385–30.479 | 0 |
| Nhãn @ 30.400 (20/11) | TRONG P10–P90, +11% so tâm; luật 4 (23.284) không đạt | như cũ | không đổi |
| skeptic_final | REFUTED_OPEN | REFUTED_OPEN | giữ |

## (c) Phản biện
Không chạy vòng mới: r4 (DD_GENERAL, INCONCLUSIVE medium, 1,30 USD, report_md5 khớp) là vòng 3 cuối (user duyệt 23/11 17:03); §E14 dừng.

## (d) Tâm kỳ vọng điều chỉnh (E17)
**26.303 đ/cp (dải 24.470–27.236; −3,98%)**, tuyến tính (tổ hợp 26.309). D1 quỹ KH&CN chi bắt buộc không thành TSCĐ (f 38,7%, TM25) B p 0,5 × −3,25%; D2 hồi quy đoán cao 2024–25 (chạy mô hình, −6,72%; skeptic ước −4,5%) B nhánh ngược p 0,35.
Điều kiện đổi số chính: LNST KT 2026 vs hồi quy (+1,3% / −2,0%); TM quỹ KH&CN KT 2026 (+0,8 / −1,0%); văn bản hoàn nhập quỹ (tới −8,7%); hạn thuê đất (−3,6…−6,8%); giá khí sau 2034 (tới −17,6%).

## (e) Rủi ro / việc mở
1. Giá khí 2035+ (C, −17,6% biến thể có trọng số) — rủi ro đuôi lớn nhất, ngoài tâm. 2. Hoàn nhập quỹ KH&CN cho DN ngoài DNNN — cần legal-vn/Công báo. 3. Hạn thuê đất Cà Mau. 4. 332 tỷ MBV; ý kiến kiểm toán FY2025 chưa soát đoạn nhấn mạnh.
5. Giá 30.400 so tâm adj 26.303: 1,16× (chỉ đọc sau khoá; KHÔNG đổi nhãn sổ). Đáy hiệu dụng watch nếu Mike ghi center_adj = min(24.385, 24.385×26.303/27.393, 24.470) = 23.415.
6. `LEDGER_PROPOSAL_DCM.json` = rev5 REFUTED_OPEN, selfcheck `--ledger` bản tạm: lỗi 0.

## (f) Khuyến nghị lớp: **MECH** (tâm base 0%, không chạy vòng skeptic mới).
