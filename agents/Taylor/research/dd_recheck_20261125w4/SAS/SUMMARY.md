# SAS — DD rev3 đầy đủ (đợt 4, 25/11/2026, job Taylor_20261125_063648)

Nguồn: `REPORT_recheck_SAS.md` · khoá `PREREG_rev3.md` + `calc/assumptions_rev3.json` + `src_ocr/` ⇒ `LOCK_rev3_md5.txt`; phụ lục sau skeptic `PREREG_rev3_addendum_r1.md` ⇒ `LOCK_adj_md5.txt` · calc `calc/model_sas_rev3.py` (run1 = run2 md5 `71b97115…`; CONTROL tái lập r3 31.658), `calc/calc_adj_rev3.py` (md5 `7491a6a3…` ×2) · skeptic `skeptic/r1.json` · `LEDGER_PROPOSAL_SAS.json` (rev3) · `ADJ_CENTER.md` + `adj.json`.
Calc r3 bị TRIM: khôi phục `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105/{SAS,_common,_common_020021,_shared,TOP5B_CORRECTIONS_20261108.md}` → `/tmp/ddrestore_w4sas` (md5 model/assumptions r3 được assert).

## (a) Lệch luật
- **D4:** áp — TV = E₂₀₂₈/r (r3: E/(r−g) không tái đầu tư = RONIC ∞; moat NARROW). −4.232 đ.
- Lãi tiền gửi Q4/26 (r3 §10.1): cộng 7,24 tỷ, +51 đ.
- **E15:** Tâm @ Ke 12,3% = **29.113 (+5,95%)**. **E16:** nguyên văn **KHÔNG CHẮC (N hiệu dụng thấp, 1.99)** ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=2.36).
- **Cờ đỉnh lợi nhuận đã định lượng:** NPM 23,1% gồm cổ tức đầu tư 140,6 tỷ — N0 đã loại TC; biên VẬN HÀNH 15,42% (9T/26) vs 12,57% (9T/25) ⇒ E17 #1.
- D3: không có capex tuân thủ (cam kết TSCĐ 103,5 tỷ = V4a). V1: r 13,5%, Δ 0. V3/V5: kế thừa. V6: D = 0,261 < ln2, không cờ.
- Thuyết minh (OCR BCTC gốc): phải thu DH 242 = 227,8 tỷ ứng cho dự án đứng (Bắc Vũng Bàu 162,4…); bên trả cổ tức = Xăng dầu TSN (liên kết 38%, ngoài IPP); GTGT khấu trừ 199→241 tỷ; truy thu thuê đất đã hạch toán/nộp; soát xét H1 Deloitte chấp nhận.

## (b) Tâm / vùng / nhãn
| | rev2 (sổ) | rev3 | Δ |
|---|---|---|---|
| Tâm (sau CK 5 tỷ) | 31.658 | **27.477** | −13,21% |
| P10–P90 | 25.083–38.043 | 22.430–32.420 | |
| Nhãn @ 34.200 (06/11) | TRONG | **TRÊN** (>P90; sleeve 40 tr TRONG sát mép, P90 34.279) | đổi |
Luật 4 không đạt (ngưỡng 23.355).

## (c) Phản biện
`skeptic/r1.json` **INCONCLUSIVE (medium)**, 1,09 USD. Cơ học khớp (tâm điểm giữa 29.159/≈27.430). Đã áp: E17 #2 → C+ (bỏ 86%), #3 bù trừ VLĐ (130,3), thêm #4 mùa vụ Q4; đóng truy thu thuê đất + ý kiến soát xét. Tâm base không đổi sau đính chính ⇒ không phản biện lại; `skeptic_final` = REFUTED_OPEN.

## (d) Tâm kỳ vọng điều chỉnh (E17)
**26.803 đ/cp (dải 25.459–28.287; −2,45%)** — #1 N0 đỉnh biên −4,09 · #2 phải thu DH −0,35 · #3 GTGT/VLĐ +1,17 · #4 mùa vụ Q4 +0,87 (p×m, %). Bảng điều kiện đổi số: BCTC Q4/2026 (31/01/2027: biên Q4 ±2,34%; mùa vụ −0,87…+0,50%), BCTC năm 2026 (GTGT hoàn +1,83%; trích lập phải thu DH −5,24%), thầu Long Thành (±7,45%/10pp ⇒ rev mới), hợp đồng ACV (~27 năm −1,72%).

## (e) Rủi ro / việc mở
1. Killer objection skeptic: q trượt thầu Long Thành ngầm 0,5 (tham số lưới kế thừa) và TV trên mặt bằng giao không đấu thầu, chưa có thời hạn hợp đồng — có thể lớn hơn Σ E17.
2. Thời hạn hợp đồng khai thác mặt bằng TSN–ACV: chưa có văn bản. 20 lô đất: chưa kiểm bản gốc (WARNING).
3. Đối tác vận hành miễn thuế mới (Chủ tịch: tự vận hành "không thể kéo dài") — điều khoản quyết định #1.
4. Minh bạch mù giá: SUMMARY w3 đã in giá 06/11 trước khi khoá; không giả định nào chọn theo giá.

## (f) Khuyến nghị lớp: **FULL đã làm** — Mike ghi `LEDGER_PROPOSAL_SAS.json` (rev3, REFUTED_OPEN) rồi `dd_ledger_append_center_adj.py --adj SAS=…/adj.json` (rev4). Thử trên bản tạm: selfcheck 0 lỗi (172 → 173 entry, 3 TZ). Không có lý do mua (TRÊN vùng).
