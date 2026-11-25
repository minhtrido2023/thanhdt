# DDV — Rà lại DD theo luật B5 + E15/E16 (25/11/2026, job Taylor_20261125_032443)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/DDV/REPORT_r3.md`, dd_date 2026-10-28 rev2 sổ) theo HANDOFF `dd_recheck_20261125w3`. **Không làm lại mô hình**: tái dùng nguyên `calc_r3/model_r3.py` + `assumptions_r3.json` (md5 `0e62e59d6175ef01d6329a44737d7520`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp).

- **Nguồn calc:** `calc_r3/` (assumptions, out, px) đã bị TRIM khỏi git ngày 19/11 (commit `14ad1c925`). Khôi phục: `git -C <mike> archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 | tar -x -C /tmp/ddrestore_w3a/mike`. md5 của 10 file đầu vào khớp `calc_r3/LOCK_md5.txt` phần 1/1b (assert trong code).
- **Calc:** `calc/calc_recheck.py`. **Chân CONTROL:** chạy lại `model_r3.py` → stdout md5 `eeee072d…` = `run1.txt` r3 (LOCK phần 2), và `model_r3_out.json` md5 `d452a7de…` = LOCK phần 2 (assert). Tâm 15.911 / P10 13.315 / P90 18.573 cũng assert.
- Chạy 2 lần: `calc/run1.txt` = `calc/run2.txt` (md5 `1b0e4835…`). Output `calc/calc_recheck_out.json`.
- Ghi chú: `data/deposit_rate_vn_events.csv` (repo ngoài) đã thêm dòng sau LOCK (09/11, 16/11) nên md5 lệch LOCK; lãi hiệu dụng tại 03/11 và 06/11 vẫn 7,40% nên R0 = 13,5% không đổi — chân CONTROL trùng byte xác nhận.
- Mù giá: calc không đọc giá mới. Giá 15.200 (BQ 06/11/2026) kế thừa r3, chỉ dùng cho nhãn/%dưới giá.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 5 tỷ 1,47%): 15.911 đ/cp — vùng 13.315–18.573 (P10–P90 lưới 405 kết cục). KHÔNG ĐỔI so với r3.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 16.854 đ/cp (+5,93% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): DDV: so với lịch sử 10 năm của chính mã — **RẺ** — phân vị [fade 6, hold 0], 60 tháng, N hiệu dụng ≈ 2.9 (thước cơ học RI-ROE5Y của chính mã, KHÔNG dùng tâm DD; chỉ hiển thị)

- **Nhãn** (giá 15.200, BQ 06/11/2026, kế thừa r3): **TRONG vùng** (nửa dưới). Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 15.911 = 13.524). Nhãn không đổi so với r3.
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới chỉ là MECH. Bản cũ đã CONFIRMED (r3 08/11) nhưng chưa từng qua DD_GENERAL ⇒ chạy phản biện DD_GENERAL (HANDOFF).
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding v5: DDV không có tầng holding ⇒ không áp. (ii) r: neo 03/11 lãi huy động 12T hiệu dụng 7,40% (`cctg_12m(2026-11-02)`); đọc lại 25/11 vẫn 7,40% (last_update 16/11) ⇒ Δ = 0, r = 13,5%. HANDOFF ghi "báo cáo nguồn chỉ có r 14,58%" — kiểm lại: 14,58% là **r ngụ ý bởi giá** (REPORT_r3 §3), không phải r dùng cho tâm; tâm r3 đã ở r 13,5% neo (§4 r3) ⇒ không phải dựng lại tâm, chỉ bổ sung dải Ke + E15. (iii) RONIC = Ke mọi ô (f27 + terminal) đã áp ở r3 (#3). (iv) Độ nhạy r r3 §7 đã tính từ mô hình; tái lập khớp đến từng đồng (§2).
- **Sizing (V8):** đề xuất **0% mua mới ở giá tham chiếu** (TRONG vùng, luật 4 không đạt); nếu về dưới ngưỡng luật 4 thì ≤**2% NAV** (đầu dưới chuẩn 2–4%) vì moat NONE, UPCOM, free float 36%, cổ đông Nhà nước 64%.

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 3 | D4 dải Ke 12,3–13,4% | Chỉ ±50/±100bp | Bổ sung: 16.854 / 15.983 | 0 |
| 4 | V6 hai nền | Chưa có | Bổ sung §3 (chỉ hiển thị); **cờ D > ln2** | 0 |
| 5 | D3 capex tuân thủ | Chưa soát | Soát §3: bãi thạch cao = "cần kiểm chứng", không vào base | 0 |
| 6 | V8 sizing 2–4% | Chỉ CK theo cỡ 10/20/40 tr | §0 | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi tâm trục r (giữ trục ±50bp, trọng số 0,25/0,5/0,25)

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%). β = 1 (giả định). Δ đến 25/11 = 0.

| r | Tâm | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | % trọng số dưới 15.200 | Nhãn |
|---|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 16.854 | 14.093 | 19.722 | +943 | +5,93% | 23,3% | TRONG |
| 12,5% (−100bp) | 16.684 | 13.959 | 19.495 | +773 | +4,86% | 26,5% | TRONG |
| 13,0% (−50bp) | 16.282 | 13.625 | 18.999 | +371 | +2,33% | 32,7% | TRONG |
| 13,4% (đầu trên dải Ke) | 15.983 | 13.375 | 18.653 | +72 | +0,45% | 36,8% | TRONG |
| **13,5% BASE** | **15.911** | **13.315** | **18.573** | 0 | 0 | 37,9% | TRONG |
| 14,0% (+50bp) | 15.567 | 13.065 | 18.154 | −344 | −2,16% | 43,0% | TRONG |
| 14,5% (+100bp) | 15.247 | 12.812 | 17.750 | −664 | −4,17% | 49,3% | TRONG |

- Bốn mốc ±50/±100bp khớp đúng r3 §7 (16.684 / 16.282 / 15.567 / 15.247).
- Độ nhạy r của DDV nhỏ (~+6% ở 12,3%) vì 1.108 tỷ tiền ròng (7.583 đ/cp = 47% tâm trước CK 16.149; 146.109.900 cp, `calc/model.py` SH) không chiết khấu.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** đúng — RONIC = Ke ở cả f27 và terminal (moat NONE). Không lệch.
- **D3 capex tuân thủ:** hạng mục ứng viên duy nhất = **xử lý/bãi thải thạch cao Đình Vũ** (nghĩa vụ môi trường, không tạo doanh thu; ADDENDUM_5F lực 6, DD 26/10 §7 [VND25]). Biên chu kỳ 4,05% (BQ 2015–25) đã chứa chi phí vận hành bãi lịch sử, nhưng **khoản bước tăng tương lai (mở bãi mới/xử lý tái chế bắt buộc) chưa có số** trong BCTC Q3/2026 đã đọc ⇒ **cần kiểm chứng** (thuyết minh cam kết vốn, giấy phép môi trường), không vào base, không ước. Capex 9T 186,4 tỷ (dự án MAP 60k t/năm) = tăng trưởng ⇒ V4(a) NPV = 0 (sổ sách) — đã đúng ở r3 (tiền ròng theo sổ, không trừ phần capex chưa chi vì dự án ở NPV 0).
- **V1/D4 r:** đúng neo + β×Δ (Δ = 0); dải Ke nay đã báo (§2).
- **E15/E16:** đã thêm (§0). E16 in nguyên văn "RẺ" của thước cơ học — KHÔNG phải nhãn DD, không vào luật 4/nhãn.
- **V3 thanh khoản:** đã đủ (r3 §5): trước CK 16.149, sau CK 5 tỷ (1,47%, ngoài vùng hiệu chỉnh) 15.911; sleeve 40 tr CK 0,13% ⇒ tâm 16.128. Nhãn theo sau CK.
- **V5 moat:** đã đủ — 5F 07–08/11/2026 (`ADDENDUM_5F.md`) < 12 tháng: **NONE**, rủi ro số 1 = spread DAP − (S + NH3 + apatit) do giá thế giới quyết định (price-taker hai đầu). Kiểm nhanh 25/11: không có BCTC/CBTT mới được đọc trong recheck.
- **V6 (bổ sung, chỉ hiển thị):** nền máy `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11/2026, fin_time 22/10; file TRIM 19/11, khôi phục từ `3750ca176^`): V_ngắn **29.229** (LNST chuẩn hoá 393,5 tỷ, ROE 15,0%, g 12,75%, g/ROE 0,85 ⇒ tái đầu tư bị chặn ở 80%) / V_dài **68.749** / D = **0,855 > ln2 (0,693), < ln3** ⇒ **cờ phân kỳ**. Nguồn chênh: (a) nền máy dùng LNST chuẩn hoá 393,5 tỷ (gồm FY2025 năm đỉnh + LTM) so với LN giữa chu kỳ DD 229 tỷ (biên 2015–25 × DT FY2025) — tức **chu kỳ lợi nhuận đỉnh**, không phải capex; (b) g 12,75% của engine > g 3% DD và ROE ≈ g làm V_dài phình. Vùng đọc mở rộng theo luật V6 = [min, max] hai nền & DD = **13.315 … 68.749** — chỉ hiển thị; tâm/vùng/nhãn vẫn từ mô hình DD. Caveat: r engine (ERP-based) ≠ 13,5%, chưa chạy lại ở 13,5%.
- **V7:** không dùng snapshot vĩ mô.
- **V8:** §0.

## 4. Rủi ro lớn kế thừa r3 (đưa phản biện xét hai chiều — KHÔNG đổi base trong recheck)
1. **DT chuẩn hoá = FY2025 5.652 là NĂM ĐỈNH** (trước đó tối đa 3.392); TB 2021–25 3.709,7 ⇒ tâm 12.452, nhãn TRÊN (r3 §2). LTM 6.406 ⇒ 17.254.
2. **Tiền ròng 1.108 tỷ có thể bị giữ lại** (Vinachem 64%): vốn hoá lãi gửi thay vì mệnh giá ⇒ 11.555, nhãn TRÊN (r3 §2/§6).
3. Khoản trừ lãi gửi: trung điểm 35,4 tỷ nằm nửa TRÊN khoảng lịch sử proxy −9…+26 tỷ/năm (thu nhập TC kiểm toán 2015–22 chưa kiểm) — chiều LÊN cho tâm (trừ ít hơn); cận trên 70,9 ⇒ 14.353.
4. Đường 2027 lệch (w 0,45/0,40/0,15); đối xứng 1/3 ⇒ 16.336.
5. Liven 217 tỷ theo sổ (mất 100% p 0,10 ⇒ −146).

## 5. WARNING (giữ r3 §8)
Vinachem 64% (giá chuyển giao apatit, thoái vốn chưa thực hiện) · Liven 217 tỷ một khách · phải trả Tường Nguyên 326,3 tỷ · bãi thạch cao Đình Vũ · 20/04/2026 hai lãnh đạo từ nhiệm · tồn kho NVL 617,3 tỷ chưa trích lập · UPCOM, free float 36%. Chưa tra trực tiếp UBCKNN/HNX. Pháp lý chỉ WARNING.

## 6. Phạm vi đề nghị cho phản biện (§E4, DD_GENERAL)
Moat (NONE có đúng không; có chi phí/hào nào bị bỏ qua), cân bằng hai chiều (xuống: DT đỉnh §4.1, tiền bị giữ §4.2, bãi thạch cao D3; lên: Ke đầu dưới +5,9%, trừ lãi gửi trung điểm nửa trên §4.3, trọng số 2027 lệch xấu §4.4), thiếu hạng mục (D3 — capex môi trường bắt buộc; cổ tức đã công bố chưa trừ?; quỹ KTPL/thưởng trích từ LN?), và kiểm bảng độ nhạy r §2 (tái chạy: lệnh ở đầu báo cáo, đường dẫn khôi phục `/tmp/ddrestore_w3a/mike/agents/Taylor/research/dd_redo_20261105`).
