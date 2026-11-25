# PVT — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_032446 → resume Taylor_20261125_053004, job B)

Nguồn: `REPORT_recheck_PVT.md` (md5 `43b7dd2e…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `e6639533…`; CONTROL `pvt_r3_out.txt` md5 `23f5090f…` + `grid_pvt_r3.csv` `58d04616…` = LOCK r3) · skeptic `skeptic/r1.json` · E17 `ADJ_CENTER.md` + `adj.json` (kiểm kê khoá trước `ADJ_PREREG_PVT.md` md5 `9d8b4c53…`) · đề xuất sổ `LEDGER_PROPOSAL_PVT.json` (rev3; selfcheck sổ tạm 157 entry lỗi 0).
⚠ `calc_r3/` gốc bị TRIM (`14ad1c925`); khôi phục `git archive 14ad1c925^ … | tar -x -C /tmp/ddrestore_PVT`; md5 LOCK khớp trừ `data/deposit_rate_vn_events.csv` (append-only, giá trị as-of không đổi — control khớp byte).

**Bước 0:** CÓ một tham số nền bị phủ — terminal RONIC = ROE kịch bản (r3) bị D4 (22/11) phủ. Thay thế CƠ HỌC bằng chính script (r3 đã ghi sẵn độ nhạy) ⇒ áp trong recheck rồi chạy skeptic trên bản đã áp. Không tầng holding; Δ lãi huy động 03/11→25/11 = 0, r 13,5%.

## (a) Lệch theo luật mới
- **D4:** RONIC = Ke ⇒ tâm +0,61%, vùng hẹp lại. **E15:** Tâm @ Ke 12,3% **20.798 (+9,72%)**; dải Ke 20.798 / 19.097; ±100bp 20.466 / 17.656.
- **E16:** nguyên văn **RẺ** (phân vị fade 16 / hold 18, N hiệu dụng ≈ 4.5) — chỉ hiển thị.
- **D3:** dry-dock/BWM/EEXI bắt buộc; TT99 ngừng trích trước sửa chữa lớn ⇒ LN 2026 thiên lệch tăng (E17 P2).
- **V6:** V_ngắn 22.045 / V_dài không có (FCFE 3 năm ≤ 0 do pha mua tàu — đầu tư tăng trưởng, không phải cảnh báo đắt). **V3/V5:** đủ (CK 0,67%; moat NONE). **V8:** trần 2% NAV.

## (b) Tâm / vùng / nhãn
| | rev2 (sổ) | recheck | Δ |
|---|---|---|---|
| Tâm | 18.841 | 18.956 | +0,61% |
| Vùng | 13.903–24.207 | 15.021–23.164 | hẹp lại |
| Nhãn @ 20.550 (06/11) | TRONG | TRONG | không đổi |
| skeptic_final | CONFIRMED (backfill luật, path null) | **REFUTED_OPEN** | đổi trạng thái phản biện |

## (c) Phản biện
`skeptic/r1.json`: **REFUTED (medium)**, 0,91 USD, report_md5 khớp. Cơ học đúng, tái lập được. Đòn chính (chiều XUỐNG): ~7,5% LN mẹ FY2025 đi vào quỹ KTPL (nợ phải trả) nhưng mô hình coi 100% LNST mẹ thuộc cổ đông ⇒ tâm ~17.500–18.000 (ước lượng skeptic). Chiều lên: không có khoản nào có bằng chứng độc lập. Không sửa mô hình base trong recheck (đổi cơ sở LN = rev mới + phản biện đầy đủ).

## (d) Tâm kỳ vọng điều chỉnh (E17)
**18.184 đ/cp (dải 16.806–18.586; −4,07%)** — P1 trích KTPL từ LN mẹ k = 7,47% [7,47%; 14,5%] (B, −3,74%), P2 hoàn nhập dự phòng sửa chữa lớn TT99 −73,2 tỷ/năm phần mẹ (B, −0,35%). Bậc C chỉ độ nhạy: chi dry-dock tiền mặt, ý kiến kiểm toán 2025, NPV tàu mới/quyền PDV, đáo hạn TC, mùa vụ Q4. |Σ| < 5% ⇒ không phản biện lại. Điều kiện đổi số chính: tỷ lệ trích KTPL trong NQ ĐHĐCĐ/BCTC kiểm toán 2026 (7,5% ⇒ −3,10%; 14,5% ⇒ −9,68%; không trích ⇒ +3,88%) — đủ bảng ở `ADJ_CENTER.md`.

## (e) Rủi ro / việc mở + khuyến nghị lớp
1. Tỷ lệ trích KTPL (NQ ĐHĐCĐ 2026/2027) + tách "điều chỉnh khác" 9T/26. 2. Ý kiến kiểm toán 2025 / soát xét H1. 3. Chi dry-dock tiền mặt vs hoàn nhập TT99. 4. Quyền mua PDV; TC/spot. 5. Pháp lý chưa quét lại sau 08/11.
**Khuyến nghị: FULL (rev mới) khi có BCTC kiểm toán 2026** — đòn skeptic là khoản thiếu cấu trúc (phân phối LN cho người lao động), cần sửa cơ sở LN của mô hình; E17 −4,07% < 5% nên không phản biện lại ngay. Nhãn TRONG ở cả tâm base và tâm điều chỉnh (giá ref 20.550 > cả hai).
