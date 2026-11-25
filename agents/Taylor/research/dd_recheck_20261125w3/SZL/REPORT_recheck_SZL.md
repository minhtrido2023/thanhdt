# SZL — Rà lại DD theo luật B5 + E15/E16 + E17 (25/11/2026, job Taylor_20261125_053004 resume Taylor_20261125_032446, đợt 3 job B)

Bản rà lại **REPORT_rev5** (`agents/Taylor/research/dd_redo_20261105/SZL/REPORT_rev5.md`, md5 `3d5eecc3…`, sổ rev4 = REFUTED_OPEN, skeptic r4 vòng cuối INCONCLUSIVE medium, hạng mục r4 CHƯA áp). **Không sửa mô hình base**: tái dùng nguyên `rev5/calc/model_rev5.py` + `assumptions_rev5.json` (md5 `35165d4a…`); thêm E15/E16/dải Ke/V6/V8 và dựng tâm kỳ vọng điều chỉnh E17 từ hạng mục skeptic r4 (+ một khoản thiếu mới đọc từ thuyết minh).

- **Calc:** `calc/calc_recheck.py` (md5 mọi dòng `rev5/calc/LOCK_rev5_prerun.txt` khớp — assert; CONTROL: stdout `model_rev5.py` md5 = `model_rev5_out.txt` `f9f1a8a2…`; tâm/P10/P90 26.183 / 22.740 / 29.700 assert). Chạy 2 lần: `calc/run1.txt` = `run2.txt` md5 `64967ddb…`. Output `calc/calc_recheck_out.json`. E17: `calc/calc_adj.py` → `ADJ_CENTER.md` + `adj.json`.
- Mù giá: không đọc giá mới. Giá 27.700 (06/11/2026) kế thừa rev5, chỉ cho CK + nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, RONIC = Ke, sau CK 4,12% @5 tỷ): 26.183 đ/cp — vùng 22.740–29.700 (P10–P90 lưới 1.080 kết cục). KHÔNG ĐỔI so với rev5.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 27.233 đ/cp (+4,01% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **TRUNG TÍNH** — phân vị [fade 52, hold 43], 120 tháng, N hiệu dụng ≈ 13.2

- **Nhãn** (giá 27.700, BQ 06/11/2026, kế thừa rev5): **TRONG vùng** ở cả 2 cỡ (+5,8% so tâm 5 tỷ; 70,9% trọng số kết cục dưới giá). Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 26.183 = 22.256). Nhãn không đổi so với rev5.
- **Tâm kỳ vọng điều chỉnh (E17): 28.506 đ/cp (dải 26.772–29.639; +8,87%)** — chi tiết `ADJ_CENTER.md`. Chỉ hiển thị; KHÔNG thay tâm base trong sổ/luật 4. Lệch > 5% ⇒ chạy lại phản biện DD_GENERAL trên bản này.
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** rev5 lập 23/11 (sau luật V1 03/11 và D4 22/11): r = 13,5% + β×Δ (Δ lãi huy động 03/11→25/11 = 0, 7,40%); terminal RONIC = Ke (`core = cf/r`); holdco base 0% nằm trong dải CK holding v5 (0…+20%, hiển thị) — độ nhạy holdco 25% của rev5 vượt dải v5, chỉ là độ nhạy; độ nhạy r ±100bp TÍNH từ mô hình (tái lập +3,3%/−2,9%).
- **Sizing (V8):** nếu có ý định mua (nhãn TRONG ⇒ không có tín hiệu), trần đề xuất **2% NAV** (đầu dưới dải chuẩn: `audited_fy_missing = true`, trục capex ±24,8%, CK 4,12% ở cỡ 5 tỷ ⇒ chỉ cỡ nhỏ, chia ≥2 phiên).

## 1. Thay đổi so với rev5

| # | Luật | rev5 | Recheck | Ảnh hưởng tâm base |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20; `calc/dd_history_label_SZL_2026-11-20.*`) | 0 |
| 3 | D4 dải Ke 12,3–13,4% | Chỉ ±100bp | Bổ sung: 27.233 / 26.265 | 0 |
| 4 | V6 hai nền | "Không áp dụng" | Bổ sung §3 (chỉ hiển thị) | 0 |
| 5 | V8 sizing | "chỉ tham chiếu" | Trần 2% NAV | 0 |
| 6 | E17 / V9 | Chưa có | Tâm điều chỉnh 28.506 (+8,87%) | 0 (tâm base giữ) |

## 2. Độ nhạy r (V1 + D4 + E15) — mô hình rev5, chỉ đổi r tâm (trục r của lưới ±100bp dịch theo)

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%), β = 1 (giả định), Δ đến 25/11 = 0.

| r | Tâm 5 tỷ | P10 | P90 | Δ tâm (%) | Tâm 40 tr | Nhãn 5 tỷ / 40 tr |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 27.233 | 23.564 | 30.940 | +4,01% | 28.297 | TRONG / TRONG |
| 12,5% (−100bp) | 27.046 | 23.403 | 30.720 | +3,30% | 28.103 | TRONG / TRONG |
| 13,0% (−50bp) | 26.601 | 23.064 | 30.178 | +1,59% | 27.640 | TRONG / TRONG |
| 13,4% (đầu trên dải Ke) | 26.265 | 22.807 | 29.794 | +0,31% | 27.291 | TRONG / TRONG |
| **13,5% BASE** | **26.183** | **22.740** | **29.700** | 0 | **27.207** | TRONG / TRONG |
| 14,0% (+50bp) | 25.792 | 22.459 | 29.240 | −1,50% | 26.800 | TRONG / TRONG |
| 14,5% (+100bp) | 25.424 | 22.082 | 28.817 | −2,90% | 26.417 | TRONG / TRONG |

±100bp tái lập trùng rev5 §3 (+3,3% / −2,9%). Độ nhạy r thấp (≈ ±3%/100bp) vì phần lớn giá trị là tài sản t=0 (cổ phần niêm yết, XDCB, BĐS ĐT) và dòng tiền hữu hạn 27 năm (3/4 trọng số).

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4:** RONIC = Ke đã có từ r3b; dòng tiền 27 năm (2053) 3/4 + vĩnh viễn 1/4. Không lệch.
- **D3 capex tuân thủ:** nhà máy xử lý nước thải GĐ4 116,34 tỷ đã đầu tư, đang khấu hao trong N0; capex tuân thủ mới chưa công bố ⇒ nằm trong trục capex duy trì/KH ±45 tỷ/năm (rev5). Không lệch.
- **V1:** r 13,5% đúng neo (Δ = 0); dải Ke và ±50/±100bp tính từ mô hình (§2).
- **V3:** đủ (rev5 §4): CK 4,12% @5 tỷ (ngoài vùng hiệu chỉnh, tham chiếu), 0,37% @40 tr.
- **V4:** dự án mới = sổ sách — rev5 áp cho BĐS ĐT mới, XDCB 407, Tân Đức. Recheck phát hiện ba tài sản t=0 cùng bản chất CHƯA áp (tồn kho Tam An 116,58; trả trước nhà thầu 58,39–72,61; cổ tức dự thu 23,264) ⇒ đưa vào E17 (không sửa base trong recheck).
- **V5 moat:** đủ — 5F 11/2026: NARROW / LOCATION; rủi ro số 1 quỹ đất KCN Long Thành gần cạn, đồng hồ 2053.
- **V6 (bổ sung, chỉ hiển thị):** `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11/2026, fin_time 20/10; khôi phục từ `3750ca176^`): V_ngắn **31.011** (LNST chuẩn hoá 116,6 tỷ, ROE 18,5%, g 12,75%) / V_dài **1.335**; D = ln(V_ngắn/V_dài) = 3,15 > ln2 ⇒ hai nền vênh mạnh. Nguồn chênh: FCFE chuẩn hoá 3 năm gần 0 vì CF đầu tư (202 tỷ 2025; 309 tỷ 9T/26) ≫ KH ~90 — pha xây nhà xưởng + CCN Long Phước (đầu tư tăng trưởng, base NPV 0), và động cơ dd_blend không thấy tiền thuê thu trước (DTCTH 762). Không phải cảnh báo đắt; vùng đọc [1.335; 31.011] chỉ hiển thị. Caveat: r engine dd_blend ≠ 13,5%; "chưa qua tiêu chí khoá trước, chỉ theo dõi".
- **V7:** không dùng snapshot vĩ mô. **V8:** trần 2% NAV (§0).

## 4. Phản biện cũ (r4) → xử lý ở E17

| Hạng mục skeptic r4 | Đọc thêm phiên này | Xử lý |
|---|---|---|
| Tồn kho 118,03 chưa định giá, "chưa rõ bản chất" | TM7 tr.18: dở dang 76,21 = san lấp, xây dựng KDC Tam An; thành phẩm BĐS 40,37; không đổi so đầu năm | E17 S1 (A, p 0,75 — quy đổi chậm) |
| Trả trước NCC 72,61 (+58,4) | TM4 tr.15: Phúc Hiếu 34,34, Kỹ thuật SEEN 16,80, Xây dựng Tu Sa 10,24 (nhà thầu), song song XDCB tăng | E17 S2 (B) |
| nc 10% dưới sàn phân bổ đều 17% | TM19 tr.24: DTCTH 762,16 (NH 42,90 + DH 719,25), tăng ròng +81,23 trong 9T | E17 S4 (C+, nhánh ngược) |
| CF_OA ≈ 1,8× LNST — thu trước định kỳ không được ghi có | — | C1 (chỉ độ nhạy) |
| Capex ≫ KH chưa đối chiếu | — | C2 (trục rev5 ±24,8%) |
| (mới) | TM5 c tr.16: cổ tức dự thu từ bên liên quan 23,264 | E17 S3 (A) |

## 5. Việc còn mở (không chặn nhãn)
1. Bản chất trả trước nhà thầu (thuyết minh BCTC năm) và người mua trả trước cho Tam An. 2. TM19 kỳ sau: phân bổ DTCTH thực vs thu mới. 3. LCTT năm: tách capex duy trì/mở rộng. 4. Ý kiến kiểm toán FY2025; ngày GDKHQ thưởng 70%; tổng mức Long Phước. 5. Pháp lý (SNZ, thuế ~14 tỷ) chưa quét lại sau 23/11 — WARNING.

## 6. Giả định khoá
Như rev5 (`rev5/calc/LOCK_rev5_prerun.txt`, md5 file `fd5265090e56beac6177dc5a8e6a4aaf` = `assumptions_md5` sổ rev4); recheck không đổi giả định nào. Kiểm kê E17 khoá trước ở `ADJ_PREREG_SZL.md` (commit `ba6ebbec8` trước lần chạy đầu).
