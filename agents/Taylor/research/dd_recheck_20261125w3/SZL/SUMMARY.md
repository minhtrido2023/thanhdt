# SZL — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_053004 resume Taylor_20261125_032446, job B)

Nguồn: `REPORT_recheck_SZL.md` (md5 `33e276f6…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `64967ddb…`; md5 LOCK rev5 khớp; CONTROL stdout `model_rev5.py` = `model_rev5_out.txt` `f9f1a8a2…`) · skeptic `skeptic/r1.json` · E17 `ADJ_CENTER.md` + `adj.json` (v2; kiểm kê khoá trước `ADJ_PREREG_SZL.md` commit `ba6ebbec8`, phụ lục `ADJ_PREREG_SZL_v2.md` commit `a2fac9b65`) · đề xuất sổ `LEDGER_PROPOSAL_SZL.json` (rev5; selfcheck sổ tạm lỗi 0). Nguồn rev5 còn trong git (không bị TRIM).

**Bước 0:** KHÔNG có tham số nền bị phủ (rev5 lập 23/11, sau V1 và D4: r 13,5% Δ = 0; RONIC = Ke; holdco base 0% trong dải v5; độ nhạy r tính từ mô hình) ⇒ tiếp tục.

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3% **27.233 (+4,01%)**; dải Ke 27.233 / 26.265; ±100bp 27.046 / 25.424 (khớp rev5 +3,3%/−2,9%).
- **E16:** nguyên văn **TRUNG TÍNH** (phân vị fade 52 / hold 43, N hiệu dụng ≈ 13.2) — chỉ hiển thị.
- **D3/D4:** không lệch. **V4:** ba tài sản t=0 cùng bản chất "sổ sách" chưa áp (tồn kho Tam An, ứng trước capex, cổ tức dự thu) ⇒ E17.
- **V6:** V_ngắn 31.011 / V_dài 1.335, D = 3,15 > ln2 — FCFE ≈ 0 do pha xây nhà xưởng + Long Phước, engine không thấy thu trước DTCTH; chỉ hiển thị.
- **V8:** trần 2% NAV NHƯNG chặn bởi thanh khoản — ADV250 0,461 tỷ/phiên, tham gia ≤20% ⇒ ≈ 92 triệu/phiên (đính chính theo skeptic r1; REPORT §0 ghi "≥2 phiên" là chưa đủ).

## (b) Tâm / vùng / nhãn
| | rev4 sổ (REPORT_rev5) | recheck | Δ |
|---|---|---|---|
| Tâm (5 tỷ) | 26.183 | 26.183 | 0% |
| Vùng | 22.740–29.700 | 22.740–29.700 | 0 |
| Nhãn @ 27.700 (06/11) | TRONG / TRONG | TRONG / TRONG | không đổi |
| skeptic_final | REFUTED_OPEN (r4 INCONCLUSIVE) | **REFUTED_OPEN** (r1 INCONCLUSIVE) | giữ |

## (c) Phản biện
E17 v1 lệch +8,87% > 5% ⇒ chạy `skeptic/r1.json`: **INCONCLUSIVE (medium)**, 1,30 USD, report_md5 khớp. Base tái lập, mọi số kiểm lại khớp ảnh trang. Đòn chính: E17 cộng tài sản chọn lọc mà không nêu luật vốn lưu động (skeptic tự tính hai phía vận hành gần triệt tiêu, ròng ≈ −0,4%); người mua trả trước 14,54 trên mặt BCĐKT bị ghi "chưa đọc" (sai của tôi); tồn kho Tam An chưa kiểm NRV; không khoảng nào lượng hoá được >5%. Còn thiếu: kiểm toán FY2025, pháp lý SNZ/thuế sau 23/11. Đính chính E17 v2 (nêu luật t=0 phi vận hành, S1 A→B, thêm S5); Δ v1→v2 −2,54% < 5%, nhãn không đổi ⇒ xác nhận cơ học, không chạy B2.

## (d) Tâm kỳ vọng điều chỉnh (E17, v2)
**27.782 đ/cp (dải 25.975–29.277; +6,10%)** — S1 tồn kho BĐS Tam An 116,58 (B, +4,43%), S2 ứng trước nhà thầu 58,39 [72,61] (B, +2,22%), S3 cổ tức dự thu 23,26 (A, +1,59%), S4 nc phân bổ DTCTH ≥17% N0 (C+ nhánh ngược, −1,58%), S5 người mua trả trước 14,54 (B, −0,55%). Bậc C chỉ độ nhạy: thu trước mới, capex duy trì ±24,8%, kiểm toán FY2025, Long Phước, liên kết theo giá gốc, SNZ. Điều kiện đổi số chính: NRV/bán Tam An (+3,34% / −2,09%), bản chất trả trước (+1,67% / −2,09%), TM19 phân bổ DTCTH thực (−2,34% … −5,63%), thuế truy thu 14 tỷ (−1,00%) — đủ bảng ở `ADJ_CENTER.md`.

## (e) Rủi ro / việc mở + khuyến nghị lớp
1. BCTC kiểm toán FY2025 + ý kiến. 2. Thuyết minh năm: bản chất trả trước nhà thầu, người mua trả trước gắn Tam An, NRV Tam An. 3. TM19: phân bổ DTCTH thực vs thu mới; LCTT tách capex duy trì (trục ±24,8% là lớn nhất). 4. Pháp lý SNZ / thuế ~14 tỷ — quét lại. 5. Ngày GDKHQ thưởng 70%, tổng mức Long Phước.
**Khuyến nghị: FULL (rev mới) khi có BCTC kiểm toán 2026 + LCTT** — vấn đề lớn nhất (capex duy trì, phân bổ DTCTH) cần dữ liệu năm; các tài sản t=0 của E17 nên vào base ở rev mới sau khi kiểm thuyết minh. Nhãn TRONG ở cả tâm base và tâm điều chỉnh.
