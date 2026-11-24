# DGC — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, job Taylor_20261124_095517)

Bản rà lại **REPORT_r3b** (`agents/Taylor/research/dd_redo_20261105/DGC/REPORT_r3b.md`, 09/11/2026) theo HANDOFF `dd_recheck_20261124`. **Không làm lại mô hình**: tái dùng nguyên `calc_r3b/model_r3b.py` (import `calc/model_r3` → `model_r2` → `model`), giả định khoá ở `LOCK_r3b_md5.txt`, không sửa. Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp).

- **Nguồn calc:** output/CSV đã bị TRIM khỏi git (19/11). Khôi phục vào `/tmp/ddrestore_B/agents/Taylor/research/` bằng `git archive` từ `14ad1c925^` (dd_redo_20261105) và `60fe58b82^` (dgc_valuation_20261029_r12). md5 của 13 file đầu vào khớp `LOCK_r3b_md5.txt` (assert trong code).
- **Calc:** `calc/calc_recheck.py` (md5 `202e31ca…`). Base r3b có **trục r** = r_now ±50bp (trọng số 0,25/0,5/0,25). Đổi r = **dịch cả trục** một khoảng Δr (thay `C.r_now`), để nhất quán với cách tính tâm. CK 5 tỷ 0,7247% (ADV250, `summary_r3b_core.json`) giữ nguyên.
- **Chân CONTROL:** ở Δr = 0, tâm trước CK = `model_r3b_out.json` center_pre (sai số < 1e-6). Sau CK: 41.849 / P10 33.272 / P90 50.227 (assert). Bản một-điểm-r tái lập đúng 4 số `r_sens_pre` của r3b (assert).
- Chạy 2 lần: `run1.txt` = `run2.txt` = md5 `e2c7541c…`. Output `calc/calc_recheck_out.json`.
- Mù giá: calc không đọc giá mới. Giá 33.000 (BQ 06/11/2026) kế thừa r3b, chỉ dùng cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 5 tỷ): 41.849 đ/cp — vùng 33.272–50.227. KHÔNG ĐỔI so với r3b.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 43.657 đ/cp (+4,32% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (proxy lệch DD, k=0.27–0.59)** — phân vị [fade 1, hold 1], 120 tháng, N hiệu dụng ≈ 5.0 ⚠ LỢI NHUẬN SỤT? (ROE TTM/5Y=0.38)

- **Nhãn** (giá 33.000, BQ 06/11/2026, kế thừa r3b): **DƯỚI vùng, MỎNG** (thấp hơn P10 33.272 chỉ 0,8%). Luật 4 ĐẠT về số (ngưỡng 0,85 × 41.849 = 35.572), nhưng DGC KHÔNG đủ điều kiện sleeve (§2 trụ #2 trượt: DN tư nhân ⇒ NON) và đang **EXCLUDED ở ZaloPay**. Nhãn không đổi so với r3b.
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới chỉ cần soát cơ học (MECH).
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) Không có tầng holding. (ii) r: neo 03/11 7,40%, đọc lại 24/11 vẫn 7,40% ⇒ Δ = 0. (iii) RONIC terminal = Ke đã áp (`reinv = 1 − g/Ke`, `model_r3b.py` hàm `core`). (iv) Độ nhạy r ở r3b đã tính từ mô hình; recheck tái lập đúng.

## 1. Thay đổi so với r3b

| # | Luật | r3b | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20), kèm cờ LỢI NHUẬN SỤT? | 0 |
| 3 | D4 dải Ke 12,3–13,4% | Chưa có | Bổ sung: 43.657 / 41.987 | 0 |
| 4 | V1 ±50/±100bp | 42.547 / 43.315 / 41.176 / 40.562 — tính ở **một điểm r**, không có trục r như tâm | Giữ số cũ để đối chiếu; báo thêm bản **dịch cả trục** (nhất quán với tâm): 42.561 / 43.331 / 41.188 / 40.573. Lệch ≤ 16 đ/cp | 0 |
| 5 | V6 hai nền | Chưa có | Bổ sung §3 (chỉ hiển thị) | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r (dịch cả trục ±50bp)

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%). β = 1 (giả định). Δ đến 24/11 = 0.

| r | Tâm (sau CK) | Trước CK | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | Bản một điểm r |
|---|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 43.657 | 43.976 | 34.265 | 52.823 | +1.808 | +4,32% | 43.640 |
| 12,5% (−100bp) | 43.331 | 43.647 | 34.075 | 52.369 | +1.482 | +3,54% | 43.315 |
| 13,0% (−50bp) | 42.561 | 42.872 | 33.659 | 51.252 | +712 | +1,70% | 42.547 |
| 13,4% (đầu trên dải Ke) | 41.987 | 42.293 | 33.352 | 50.425 | +138 | +0,33% | 41.974 |
| **13,5% BASE** | **41.849** | **42.154** | **33.272** | **50.227** | 0 | 0 | 41.836 |
| 14,0% (+50bp) | 41.188 | 41.488 | 32.886 | 49.277 | −661 | −1,58% | 41.176 |
| 14,5% (+100bp) | 40.573 | 40.869 | 32.540 | 48.394 | −1.276 | −3,05% | 40.562 |

- **Nhãn nhạy với r (chỉ báo kèm; E15 không dùng cho nhãn/luật 4):** P10 nằm trên giá 33.000 khi r ≤ 13,5% ⇒ DƯỚI vùng; khi r ≥ 14,0% thì P10 32.886 < 33.000 ⇒ TRONG. Nhãn base nằm sát biên ở cả hai trục (r và w mở lại khai trường), đúng như errata r3b ghi nhận.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** đã đúng — RONIC = Ke ở base (`ronic='ke'`), RONIC 20% chỉ là biến thể đối chiếu (thưởng moat). Biên vĩnh viễn của nhánh mở lại đã bỏ (cách B). Không lệch.
- **D3 capex tuân thủ:** base đã có dòng tiền ra mang tính tuân thủ: **dự phòng môi trường 100 tỷ/quý** (trục một lần / 4 quý / vĩnh viễn, mỗi nhánh 1/3, lá chắn thuế 0) + trừ dự phòng hiện có và quỹ KTPL khỏi tài sản ròng (`model_r2.py` dòng 43). **Cần kiểm chứng**, chưa có số: capex xử lý môi trường bắt buộc mới (bãi thải, xử lý nước, hoàn nguyên khai trường 25) do cơ quan quản lý yêu cầu sau vụ án — nếu có, đó là chi ngoài dự phòng chi phí đã mô hình. Không có nguồn ⇒ không vào base. Nghi Sơn theo sổ (growth, NPV 0, trục ±500).
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0). Dải Ke nay đã báo. Ghi chú kỹ thuật: ±bp của r3b tính ở một điểm r, còn tâm có trục r — lệch ≤ 16 đ/cp, không đổi kết luận (§1 #4).
- **E15/E16:** đã thêm (§0). Cờ E16 "LỢI NHUẬN SỤT? (ROE TTM/5Y=0.38)" khớp bối cảnh r3b (khai trường 25 dừng, chạy quặng mua ngoài, dự phòng môi trường). Chỉ hiển thị.
- **V3 thanh khoản:** đã đủ (r3b §4) — trước CK 42.154, sau CK 5 tỷ (0,725%) 41.849; nhãn theo sau CK; cỡ sleeve 10–40 tr cũng DƯỚI.
- **V5 moat:** đã đủ — 5F `ADDENDUM_5F.md` (11/2026) < 12 tháng: **NARROW · COST/LOCATION**, rủi ro số 1 = nguồn quặng tự chủ (khai trường 25 dừng). Kiểm nhanh 24/11: không đọc tin mới trong recheck này.
- **V6 (bổ sung, chỉ hiển thị):** lấy nguyên từ `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11/2026, fin_time 29/10; file bị TRIM 19/11, khôi phục từ `3750ca176^`). V_ngắn **84.931** (LNST chuẩn hoá 2.958,9 tỷ, ROE 24,4%, g 1,75%) / V_dài **74.747** / D = **0,128** < ln2 ⇒ không cờ. Hai nền máy cao hơn tâm DD khoảng 1,8–2,0 lần. Lý do: DD có lớp phán đoán mà nền máy không có (biên về R2 19,5% khi dùng quặng mua ngoài, dự phòng môi trường, khai trường dừng). LNST chuẩn hoá của nền máy là trung vị TTM 3 năm, nên vẫn gồm giai đoạn khai trường 25 còn chạy — ngược với cờ E16 SỤT. Caveat: r theo engine dd_blend, không phải 13,5%. Không trộn vào tâm.
- **V7:** không dùng snapshot vĩ mô.
- **V8:** DGC EXCLUDED ở ZaloPay (vụ án lãnh đạo, HOSE hạn chế) ⇒ không đề xuất sizing mới. Nếu user gỡ EXCLUDE: chuẩn 2–4% NAV, đề xuất đầu dưới **2%** vì nhãn mỏng + WARNING pháp lý. Vị thế legacy ZaloPay vượt trần (r3b §5: 35,3% NAV tại 06/11, chưa đối soát lại trong recheck) là quyết định của user — recheck không đổi.

### Việc còn mở kế thừa (không chặn nhãn)
1. Errata r3b: HARD ABANDON đọc theo §3 (OR); thiếu nguồn cho "quét WebSearch 08/11"; LOCK r3b thiếu md5 `cctg_rate_vn.py`.
2. Dự phòng môi trường 200 tỷ chưa phân định có lặp lại; HTM 9.531 chưa đối chiếu PDF gốc; ý kiến ngoại trừ tồn kho 950,9 tỷ (BCTC 2025).
3. w mở lại khai trường = 0,5 là [UL] do user chốt; nhãn lật khi w ≤ 0,10.

## 4. WARNING (giữ r3b §6)
Vụ án môi trường/khai thác/kế toán (cựu Chủ tịch tạm giam 17/03/2026; 07/2026 khởi tố thêm TGĐ, thành viên HĐQT, PTGĐ, GĐ mỏ KT25); chưa thấy khởi tố pháp nhân; ngoại trừ kiểm toán 2025; HOSE hạn chế giao dịch từ 26/05/2026; cắt margin. Pháp lý chỉ WARNING.

## 5. Phạm vi đề nghị cho phản biện (§E4)
Moat (NARROW · COST/LOCATION khi quặng tự chủ đang dừng), cân bằng hai chiều (lên: Ke đầu dưới +4,3%, hai nền máy cao hơn nhiều; xuống: cờ LỢI NHUẬN SỤT, dự phòng vĩnh viễn, trục pháp lý ngoài base), thiếu hạng mục (D3 — capex môi trường bắt buộc mới sau vụ án), và kiểm bảng độ nhạy r §2 (dịch trục vs một điểm).
