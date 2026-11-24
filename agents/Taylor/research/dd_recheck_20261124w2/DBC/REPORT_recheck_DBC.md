# DBC — Rà lại DD theo luật B5 + E15/E16 (đợt 2, 24/11/2026, job Taylor_20261124_131354)

Bản rà lại **REPORT_rev4** (`agents/Taylor/research/dd_DBC_20261118/REPORT_rev4.md`, 23/11). **Không làm lại mô hình**: `rev4/calc_rev4.py` (md5 `ee3e09b5…`) + `assumptions_DBC_rev4.json` (khoá md5 `57b36d63e05ad2e2c209f2ce34fda8c9`) còn nguyên trong git (không bị TRIM). **CONTROL:** chạy lại `calc_rev4.py` ⇒ stdout trùng từng byte `calc_rev4_output.txt` (md5 `063dddd3…`).
Mù giá: không đọc giá mới. Giá 16.400 (DNSE 23/11/2026) kế thừa rev4, chỉ cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau chiết khấu thanh khoản 2%): 17.673 đ/cp — vùng 10.262–24.835. KHÔNG ĐỔI so với rev4.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 19.669 đ/cp (+11,29% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (rẻ…đắt)** — phân vị [fade 30, hold 68], 120 tháng, N hiệu dụng ≈ 14.0

- **Nhãn** (giá 16.400, DNSE 23/11/2026, kế thừa rev4): quanh giá trị hợp lý, dưới tâm ~7%; luật 4 (0,85 × 17.673 = 15.022) CHƯA đạt. Không đổi so với rev4.
- Kịch bản cơ sở sau chiết khấu (center_alt, kế thừa rev4): 17.798 đ/cp.
- **Tâm đổi 0%, nhãn không đổi** ⇒ phần luật mới là cơ học (MECH).
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding: không có tầng holding. (ii) r: neo 03/11 7,40%; `effective_deposit_rate('2026-11-24')` = 7,40% (`cctg_12m(2026-11-02)`) ⇒ Δ = 0, r = 13,5%. (iii) RONIC terminal = Ke đã áp ở rev4 (§6a). (iv) Độ nhạy r ±50/±100bp + β 0,5 tính từ mô hình (rev4 §6a), tái lập ở CONTROL.
- **Phản biện:** KHÔNG chạy vòng mới. skeptic r4 (23/11, `dd_DBC_20261118/skeptic/r4.json`, **DD_GENERAL**, REFUTED medium) đã phản biện ĐÚNG mô hình này (cùng assumptions_md5, cùng tâm); recheck chỉ thêm hai dòng hiển thị E15/E16. r4 là vòng thứ 4 không CONFIRMED ⇒ theo §E14 ("vòng cuối không CONFIRMED ⇒ DỪNG, KHÔNG chạy thêm vòng") giữ REFUTED_OPEN; hạng mục r4 xử lý bằng E17 (`ADJ_CENTER.md`).

## 1. Thay đổi so với rev4
| # | Luật | rev4 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Dải Ke có (19.669/17.818), chưa có dòng cố định | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 3 | E17 | Chưa có | `ADJ_CENTER.md` (tâm adj 16.439) | 0 (không thay tâm base) |
| 4 | Dữ kiện mới (A) cho hạng mục r4 "tài trợ XDCB" | Không trích | KT25 TM "Capitalised borrowing costs" (trang 34 bản EN, OCR `src_ocr/`): vốn hoá **9,5 tỷ (2025), 21,7 tỷ (2024)**, "relate to specific borrowings taken to finance the construction of fixed assets"; lãi vay LCTT 261,1 / 263,7 tỷ | vào E17, không vào base |

## 2. Soát luật B5 (D3/D4/V1–V8) — đều ĐÃ ĐỦ ở rev4
- **D4:** terminal RONIC = Ke (moat NARROW). **D3:** nghĩa vụ tái chế bao bì EPR (KT25 TM35) có thật nhưng chưa có số ⇒ độ nhạy −1,5…−4,5% (đúng luật: khoản trừ base phải có số + nguồn). **V1:** r 13,5%, Δ 0, β 0,5/1,0, dải Ke 12,3–13,4% (19.669 / 17.818). **V3:** CK 2% (trước 18.034). **V5:** NARROW, COST/INTEGRATION (rev1 §8, 18/11). **V6:** V_ngắn 8.991, FCFE âm (capex tăng trưởng) ⇒ V_dài không xác định, không cờ. **V8:** 2–4% NAV; tối đa 2%/tranche khi giá ≤ 15.022.
- Cổ tức tiền 15% năm 2025 (ĐHĐCĐ 25/04/2026): đã là nợ phải trả sau ĐHĐCĐ ⇒ vốn chủ Q3 đã trừ; không cần điều chỉnh cơ học.

## 3. Hạng mục skeptic r4 — trạng thái
| Hạng mục r4 | Dữ kiện mới | Xử lý |
|---|---|---|
| Tài trợ XDCB + BĐS 100% vốn chủ (quá cao) | Lãi vốn hoá cho vay ĐẶC THÙ tài trợ TSCĐ: 9,5 / 21,7 tỷ ⇒ ở lãi bình quân 4,51–4,56% (lãi LCTT / nợ BQ BQ-BCTC) nợ đặc thù ≈ 15% (2025) / 61% (2024) XDCB BQ; KHÔNG có lãi vốn hoá cho BĐS dở dang | E17 bậc B: f_XDCB 0,62 [0,39; 0,92], f_BĐS 1,0. Bản leverage-neutral 53% của skeptic bỏ qua việc lãi nợ chung đã bị trừ trong LNST: thêm cộng lại lãi ⇒ 15.470 (−12,5%) thay vì 14.023 (−20,7%) — chỉ độ nhạy |
| BĐS dở dang 1,0× sổ sách | Lãi gộp BĐS 24,7 (2024) / 4,6 (2025), DT 21,4 tỷ vs dở dang 1.114,5 | E17 bậc B (≥3 kỳ): haircut giá trị thời gian 33% [20; 40%] |
| Lỗ thuế 647 tỷ chỉ ở kịch bản tốt (quá thấp) | — | E17 bậc B |
| Quỹ đất trên giá gốc (quá thấp) | không có số | C — độ nhạy |
| EPR | không có số | C |

## 4. WARNING (giữ rev4 §7)
Phải thu người lao động 237,1 tỷ (−539 đ/cp nếu mất trắng); KT22 điều chỉnh giảm LNST Q4/22 144,9 tỷ; 2.447,7 tỷ hàng tồn kho thế chấp (KT25 TM9). Pháp lý chỉ WARNING.
