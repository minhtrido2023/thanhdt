# VLB — Rà lại DD theo luật B5 + E15/E16/E17 (đợt 3, 25/11/2026, job Taylor_20261125_032448)

Bản rà lại **REPORT_rev4** (`agents/Taylor/research/dd_VLB_20261122/REPORT_rev4.md`, md5 `3bb1f064…`, 23/11). **Không làm lại mô hình**: `model/dcf_vlb_r4.py` (md5 `05cc0943…`) + `assumptions_VLB_r4.json` (md5 `08740786baa1e16556cc848439ba9d3d`) còn nguyên trong git (không bị TRIM). **CONTROL:** chạy lại `dcf_vlb_r4.py` ⇒ stdout trùng từng byte `model/output_r4.txt` (md5 `02cb8486…`).
Mù giá: không đọc giá mới. Giá 48.100 (20/11/2026) kế thừa rev4, chỉ cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau chiết khấu thanh khoản 2,98% @5 tỷ, ex-div): 45.161 đ/cp — vùng 34.783–55.983. KHÔNG ĐỔI so với rev4.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 47.142 đ/cp (+4,39% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): VLB: so với lịch sử 10 năm của chính mã — **RẺ** — phân vị [fade 0, hold 0], 120 tháng, N hiệu dụng ≈ 9.7 (thước cơ học RI-ROE5Y của chính mã, KHÔNG dùng tâm DD; chỉ hiển thị) ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=2.31)
Tâm kỳ vọng điều chỉnh: 43.626 đ/cp (dải 40.056–45.906; −3,40% so với tâm base); căn cứ 4 hạng mục bậc B (`ADJ_CENTER.md`)

- **Nhãn** (giá 48.100, 20/11/2026, kế thừa rev4): trong vùng ±15%, nghiêng đắt nhẹ (1,07 × tâm); luật 4 (0,85 × 45.161 = 38.387) KHÔNG đạt. Không đổi so với rev4.
- Kịch bản cơ sở sau chiết khấu, ex-div (center_alt, kế thừa rev4): 44.940 đ/cp.
- **Tâm đổi 0%, nhãn không đổi** ⇒ phần luật mới là cơ học (MECH). Cờ E16 "ĐỈNH LỢI NHUẬN?" cùng hướng với hạng mục I1 của skeptic r3 (neo giữa chu kỳ) — chỉ hiển thị, không vào tâm.
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding: không có tầng holding. (ii) r: neo 03/11 7,40%; `effective_deposit_rate('2026-11-25')` = 7,40% (`cctg_12m(2026-11-02)`, Big-4 6,8%, last_update 16/11) ⇒ Δ = 0, r = 13,5%. (iii) RONIC terminal: mô hình hữu hạn theo hạn GP, không có terminal ⇒ không áp dụng. (iv) Độ nhạy r ±50/±100bp tính từ mô hình (rev4 §6), tái lập ở `calc/run1.txt`.
- **Phản biện:** KHÔNG chạy vòng mới. skeptic r3 (23/11, `dd_VLB_20261122/skeptic/r3.json`, **DD_GENERAL**, INCONCLUSIVE medium, report_md5 khớp rev4) đã chấm đúng mô hình/tâm này; recheck chỉ thêm dòng hiển thị E15/E16/E17. r3 là vòng CUỐI không CONFIRMED ⇒ theo §E14 DỪNG, giữ REFUTED_OPEN; hạng mục r3 xử lý bằng E17. HANDOFF đợt 3: chạy lại skeptic chỉ khi tâm lệch >5% hoặc đổi nhãn — không xảy ra.

## 1. Thay đổi so với rev4
| # | Luật | rev4 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Dải Ke có (trước CK 51.164 / 49.285), chưa có dòng cố định cùng cơ sở sổ | Dòng E15 ở §0 (sau CK, ex-div) | 0 |
| 2 | E16 | Chưa có | Dòng E16 nguyên văn `dd_history_label.py` (asof 2026-11-20; `calc/dd_history_label_VLB_2026-11-20.*`) | 0 |
| 3 | E17 | Chưa có | `ADJ_CENTER.md` (tâm adj 43.626) | 0 (không thay tâm base) |
| 4 | Dữ kiện A mới (đọc ảnh trang BCTC, cho hạng mục r3 "khấu hao không cộng lại" + "đền bù") | Không trích | LCTT KT25 [KT25 tr.14 PDF]: khấu hao 10,62 (2025) / 17,09 (2024); chi TSCĐ 12,04 / 3,62; tăng giảm chi phí trả trước −70,92 / +15,60. LCTT 9T/26 [Q3 tr.6]: khấu hao 8,00; chi TSCĐ 1,13; chi phí chờ phân bổ +2,89. BCTN 2025 tr.54-55: đền bù 2025 71,883 tỷ cho 47.417,8 m² | vào E17 |
| 5 | Dữ kiện A (cho hạng mục r3 "năm 1 thấp hơn tốc độ Q3") | Không trích | KQKD Q3/26 [Q3 tr.5]: LN thuần HĐKD 143,76, DTTC 17,81 ⇒ lõi quý ×4 ×0,8 = 403,0 (skeptic ước 440 vì gộp DTTC); 9T/26 lõi năm hoá 352,8 < TTM 357,4 | vào E17 |

## 2. Soát luật B5 (D3/D4/V1–V8)
- **D4:** không terminal (đời mỏ hữu hạn theo GP) ⇒ không có RONIC > Ke. **D3:** capex tuân thủ = hoàn nguyên môi trường: dự phòng 16,22 tỷ đã trích + ký quỹ (rev4 §6 V4); tiền đền bù đất trong ranh GP là chi bắt buộc để khai thác trữ lượng cơ sở — base rev4 coi chi đền bù ≈ chi phí phân bổ trong LNST (ngầm); lịch sử 2024–9T26 cho chênh −12,2 tỷ/năm ⇒ xử lý ở E17 (I3, bậc B), phần VƯỢT lịch sử (diện tích còn lại, BCTN "gặp khó", chưa có số) = độ nhạy. **V1:** r 13,5%, Δ 0, β 0,5/1,0, dải Ke 12,3–13,4% (rev4 §6). Độ nhạy cùng cơ sở sổ (sau CK, ex-div): −100bp 46.798 (+3,62%) · −50bp 45.963 (+1,77%) · +50bp 44.392 (−1,70%) · +100bp 43.654 (−3,34%). **V3:** CK 2,98% @5 tỷ (trước CK 49.123 cơ sở 30/9). **V5:** NARROW/LOCATION (tag 2026-06-05, <12 tháng). **V6:** D = 0,312 < ln2, không cờ. **V8:** 2–4% NAV; thanh khoản trói (5 tỷ ≈ 22 phiên @20% ADV); hiện không đề xuất vào. ⇒ **đã đủ** ở rev4, chỉ thiếu E15/E16/E17.
- Cổ tức tạm ứng 2026 2.500 đ/cp: GDKHQ 19/11/2026 ĐÃ QUA ⇒ tâm ghi sổ đã ex-div; không còn quyền chưa chốt (một dòng).

## 3. Hạng mục skeptic r3 — trạng thái
| Hạng mục r3 | Hướng | Xử lý |
|---|---|---|
| Neo giữa chu kỳ = lõi FY25 (năm cao nhất; 2017–2024 ≤218) + kịch bản xấu 250 | ↓ | E17 I1 bậc B (ngược: 9T/26, Q3/26 cao) |
| Phải trả NLĐ 54,2 tỷ mùa vụ trong VLĐ hoãn tới đóng mỏ | ↓ | E17 I2 bậc B |
| Khấu hao/phân bổ đền bù không cộng lại (+3–5%) vs đền bù phần diện tích còn lại (−4–6%) | ↑↓ | GỘP một hạng mục (cùng một dòng tiền đền bù/TSCĐ): E17 I3 bậc B theo LCTT 2024–9T26; phần vượt lịch sử = độ nhạy C |
| Năm 1 TTM thấp hơn tốc độ Q3/26 | ↑ | E17 I4 bậc B (ngược: 9T/26 năm hoá < TTM; KH 2026 LNTT 275) |
| Kịch bản tốt gia hạn không tính tiền cấp quyền/đền bù mới | ↓ | C — độ nhạy |
| Bù trừ chiết khấu 7,4% thay 13,5% (−1,5%) | ↓ | độ nhạy: rủi ro đảo chiều đã ở kịch bản xấu (bù trừ = 0, w 0,25) ⇒ đưa vào Σ là đếm hai lần |

## 4. WARNING (giữ rev4 §10)
Tiền cấp quyền đảo chiều 2022↔2026; rà soát GP Soklu; Kiểm toán NN (đất). Truy thu kiểu 2022 = STRESS −4.623 đ/cp + HARD ABANDON. Pháp lý chỉ WARNING.
