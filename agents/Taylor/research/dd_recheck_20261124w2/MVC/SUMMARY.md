# MVC — rà lại DD đợt 2 (24/11/2026, job Taylor_20261124_131351)

**Tệp:** `REPORT_recheck_MVC.md` (md5 `c04d150a…`) · calc `calc/calc_recheck.py` (run1 = run2 md5 `21099185…`; CONTROL: stdout mô hình trùng byte r3 `3b13f061…`) · `calc/calc_items.py` (run1 = run2 `2fc6efa4…`) · skeptic `skeptic/r1.json` · E17 `ADJ_CENTER.md` + `adj.json` (`INVENTORY_adj_MVC.md` khoá trước) · đề xuất sổ `LEDGER_PROPOSAL_MVC.json` (rev10).

⚠ calc_r3 gốc bị TRIM (`14ad1c925`). Khôi phục `git archive 14ad1c925^ dd_redo_20261105/{MVC,NNC,common.py,_shared}` + `ef7472f56^ dd_NNC_20261030` + `bffae9c42^ dd_MVC_20261103` vào `/tmp/ddrestore_MVCw2`. 25/26 md5 LOCK khớp (lệch: `deposit_rate_vn_events.csv` thêm dòng sau 06/11; lãi hiệu dụng vẫn 7,40%).

**Bước 0:** KHÔNG có tham số nền bị phủ (CK holding base 0% = mốc dải user chốt; r Δ 0; RONIC không áp; độ nhạy r tính từ mô hình) ⇒ đã chạy skeptic.

## (a) Lệch theo luật mới
- **E15:** 16.761 (+3,20%). **E16:** KHÔNG CHẮC (proxy lệch DD, k 1,33–2,33; fade 70 / hold 79; N hiệu dụng 6,3) ⚠ đỉnh lợi nhuận (ROE TTM/5Y 2,86).
- **D4/V1:** ±100bp trên lưới −2,43…+2,65%; luật 4 @5 tỷ TRƯỢT ở r 14,5%.
- **CK holding:** mốc 20% −7,26% trước CK (thay mốc 6% cũ) — độ nhạy [LUẬT].
- **D3:** PHMT/ký quỹ đóng mỏ chưa đọc (tham chiếu NNC 4,5 tỷ, nhỏ).
- **V6:** D 0,481, không cờ. **V3/V5:** đủ (moat NONE trực tiếp). **V8:** 2% NAV.
- **Hạng mục thiếu (mới phát hiện):** trích quỹ 11% LNST theo NQ ĐHĐCĐ 2026 chưa trừ.

## (b) Tâm / vùng / nhãn
| | r3 (sổ rev9) | recheck (rev10) | Δ |
|---|---|---|---|
| Tâm | 16.241 | 16.241 | 0% |
| Vùng | 9.940–23.471 | 9.940–23.471 | 0 |
| Nhãn @ 13.500 (06/11) | TRONG, luật 4 ĐẠT (mỏng 2,2%) | TRONG, luật 4 ĐẠT ở base | không đổi |
| skeptic_final | CONFIRMED (backfill rule) | **REFUTED_OPEN** | hạ nhãn |

## (c) Phản biện
`skeptic/r1.json`: **REFUTED (medium)**, 0,76 USD. Cơ học đúng (tự tính lại 1,04755/−4,59/−1,51/−4,03/−10,13%).
- Đòn chính: trích quỹ 11% chưa vào tâm (≈ −5…−7% sau khi dùng đúng cơ sở LNST riêng) > 5% trọng yếu.
- Đòn 2: cụm công nghiệp ≤500 tỷ NPV 0. Taylor GIỮ NPV 0 theo luật house 03/11 (dự án mới base = sổ sách/NPV 0); chỉ độ nhạy −2,96%/10% hao hụt.
- Chiều rẻ skeptic (cơ sở −4,59/−10,13% bị thổi) — đã áp vào E17 (cận bảo thủ trên LNST riêng).
- Không chạy B2: sửa base = đổi mô hình = rev mới (ngoài phạm vi recheck) ⇒ khuyến nghị FULL.

## (d) Tâm kỳ vọng điều chỉnh (E17)
**15.684 đ/cp (−3,43%), dải 14.727–16.093.** #1 trích quỹ 11% C+ (m −4,02% [−6,10; −4,02], p 0,5) + #2 truyền dẫn adj NNC (−1,42% [−4,75; +0,09]). Cụm công nghiệp, PHMT, biên Tân Lập 38% = bậc C (độ nhạy); CK holding, r vs Ke = [LUẬT].
- Sau khi dựng (không dùng khi dựng): ở 15.684 ngưỡng luật 4 @5 tỷ = 13.331 < giá tham chiếu 13.500 ⇒ **TRƯỢT**; ở base vẫn ĐẠT. Nhãn luật 4 phụ thuộc trực tiếp vào hạng mục trích quỹ.
- **Điều kiện đổi số quan trọng nhất:** BCTC riêng 2026 + NQ ĐHĐCĐ 2027 phân phối LNST 2026 (03–04/2027): #1 lên A ⇒ −1,61…−3,48% thêm.

## (e) Rủi ro / việc mở
1. Rev mới: đưa trích quỹ 11% vào base trên LNST riêng (sau khấu hao/lãi vay), chạy lại lưới.
2. Kế hoạch vốn cụm công nghiệp ≤500 tỷ (cơ sở độc lập mới được đổi NPV 0).
3. Thuyết minh ký quỹ PHMT; hạn GP Tân Lập; GP 2 mỏ mới.
4. Pháp lý: legal-vn Điều 195 LDN (lên 51% NNC); quét pháp lý sau 05/11. Chỉ WARNING.
5. Soát mắt số BCTC từ pdftotext.
6. Selfcheck sổ tạm có LEDGER_PROPOSAL: lỗi 0; thêm center_adj trên sổ tạm (`dd_ledger_append_center_adj.py --ledger /tmp/…`): rev 11, lỗi 0. Sổ thật không đụng.

## (f) Khuyến nghị lớp: **FULL**
Skeptic REFUTED vì hạng mục đo được > 5% chưa vào base; sửa cần rev mới của mô hình (trích quỹ trên LNST riêng), không phải soát cơ học. Trong lúc chờ: dùng tâm điều chỉnh 15.684 (đã gồm cận bảo thủ), nhãn luật 4 @5 tỷ coi như TRƯỢT.
