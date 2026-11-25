# NT2 — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_032446, job B)

Nguồn: `REPORT_recheck_NT2.md` (md5 `33c388dc…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `92aecb63…`; CONTROL: stdout `model_r3.py` md5 `f2c6788a…` = r3 `run1.md5`) · skeptic `skeptic/r1.json` · E17 `ADJ_CENTER.md` + `adj.json` (kiểm kê khoá trước `ADJ_PREREG_NT2.md` md5 `9cf0946d…`) · đề xuất sổ `LEDGER_PROPOSAL_NT2.json` (rev3).
⚠ `calc_r3/` gốc bị TRIM (`14ad1c925`). Khôi phục: `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105/{NT2,_common_020021,_common,_shared,TOP5B_CORRECTIONS_20261108.md,STANDARD_r2.md} | tar -x -C /tmp/ddrestore_NT2`; md5 22/22 dòng LOCK khớp.

**Bước 0:** KHÔNG có tham số nền bị phủ (không tầng holding; Δ lãi huy động 03/11→25/11 = 0, r 13,5%; dòng tiền hữu hạn TV=0 chặt hơn RONIC=Ke; độ nhạy r đã tính từ mô hình) ⇒ chạy skeptic.

## (a) Lệch theo luật mới
- **E15:** Tâm @ Ke 12,3%: **24.638 đ/cp (+2,64%)**. Dải Ke 24.638 / 24.054. ±100bp khớp r3 (24.528 / 23.513).
- **E16:** nguyên văn **KHÔNG CHẮC (rẻ…trung tính)** ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.89) — asof 2026-11-20.
- **D4:** dòng tiền hữu hạn 5–15 năm, TV = 0 — không lệch. **D3:** không nhận diện capex tuân thủ; nghĩa vụ môi trường/hoàn nguyên = cần kiểm chứng.
- **V6:** V_ngắn 20.350 / V_dài 57.794, **D = 1,044 > ln2** — nguồn chênh: nền máy vốn hoá VÔ HẠN dòng tiền của tài sản gần hết khấu hao (capex 1–11 tỷ/năm) + ROE < g. Vùng đọc [20.350; 57.794] chỉ hiển thị.
- **V3/V5:** đã đủ (CK 0,92% @5 tỷ; moat NONE 07–08/11). **V8:** trần 2% NAV (thay "sleeve 10–40 triệu").

## (b) Tâm / vùng / nhãn
| | rev2 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm | 24.003 | 24.003 | 0% |
| Vùng | 18.301–29.619 | 18.301–29.619 | 0 |
| Nhãn @ 22.200 (06/11) | TRONG | TRONG | không đổi |
| skeptic_final | CONFIRMED (backfill luật, path null) | **REFUTED_OPEN** | đổi trạng thái phản biện |

## (c) Phản biện
`skeptic/r1.json`: **REFUTED (medium)**, 1,01 USD. Cơ học đúng (net cash 11.398 đ/cp, hệ số niên kim 5,3195 khớp). Đòn chính (chiều LÊN): LNST chuẩn hoá 800 lấy biên 2015–25 còn gánh khấu hao ~550 tỷ/năm, nay khấu hao 115–153 ⇒ tâm có thể thấp 11–16% (ước lượng skeptic). Chiều xuống: quỹ KTPL, nợ ngắn hạn ngoài net cash, ưu đãi thuế. Tôi đọc BS 30/09/2026 (ảnh trang): thuế phải nộp 113,26 / NLĐ 26,37 / KTPL 37,90 / VAT khấu trừ 77,45 tỷ ⇒ ròng −91,88 tỷ. Ưu đãi thuế ĐÓNG (thuế Q3 20,1%). Không sửa mô hình base trong recheck (đổi LNST chuẩn hoá = rev mới + phản biện đầy đủ).

## (d) Tâm kỳ vọng điều chỉnh (E17)
**25.038 đ/cp (dải 21.938–29.039; +4,31%)** — N1 biên LNST thời kỳ hết khấu hao (B, +4,52%), N2 FCF−LNST (B ngược, +1,73%), N3 nợ ngắn hạn ngoài net cash (A, −1,19%), N4 trích KTPL ≥2,5% LNST (C+, −0,75%). Bậc C chỉ độ nhạy: giá công suất PPA giảm sau khấu hao (phản lực chính của N1), tồn kho 346 tỷ, hoàn nguyên, Q3 chưa soát xét, SHB. Điều kiện đổi số: BCTC Q4 + kiểm toán FY2026 (biên ≥/<11,2% ⇒ ±1,36%), NQ ĐHĐCĐ 2027 tỷ lệ KTPL (−0,60…−1,94%), hợp đồng giá công suất (tới ≈ −4,5%), Phụ lục 13 GSA (chạy lại trục thời hạn) — đủ bảng ở `ADJ_CENTER.md`.

## (e) Rủi ro / việc mở + khuyến nghị lớp
1. Đọc cơ chế giá công suất PPA sau khi hết khấu hao — quyết định N1 có thật hay bị giá điện ăn mất. 2. Phụ lục 13 GSA / thời hạn PPA. 3. Lịch sử chi phí trả trước đại tu. 4. Pháp lý chưa quét lại sau 05/11.
**Khuyến nghị: FULL (rev mới) khi có BCTC năm 2026** — đòn skeptic là lỗi cấu trúc dòng tiền (chuẩn hoá LNST theo thời kỳ khấu hao cũ), không sửa được bằng cơ học; E17 +4,31% < 5% nên không cần phản biện lại ngay. Nhãn TRONG ở cả tâm base và tâm điều chỉnh.
