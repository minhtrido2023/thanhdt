# HHS — DD rev9 (rà lại đợt 3, 25/11/2026, job Taylor_20261125_032448)

Việc tồn đợt 1 (HANDOFF `dd_recheck_20261125w3`): (1) sửa độ nhạy r của rev7 ("≈ 0" sai) bằng số TÍNH từ mô hình; (2) bỏ base CK holding 26,63% (N = 6) đã bị phép đo v5 phủ; dải CK 0…+20% (user chốt 24/11) chỉ HIỂN THỊ, KHÔNG vào base/sổ; (3) phản biện lại DD_GENERAL.
Bản trước: `dd_dilution_update_20261110/HHS/REPORT_rev7.md` (md5 `afe93ea4…`, sổ rev7) và bản rà lại `dd_recheck_20261124/HHS/REPORT_recheck_HHS.md` (sổ rev8, skeptic r1-recheck REFUTED: killer = CK 26,63% bị v5 phủ). rev9 KHÔNG ghi đè các bản đó.

- **Giả định khoá:** `calc/assumptions_rev9.json` (md5 `b5057d9d0497cb3fae3aba08798e03fe`, `calc/LOCK_md5.txt`) = assumptions rev7 (md5 `3afcd113…`) CHỈ đổi `holding_discount.base` 0,2663 → 0 (lý do + nguồn trong file); `k_base` = 1,0 giữ. `dd_assumptions_lint` 0 vi phạm.
- **Calc:** `calc/calc_rev9.py` — lưới r3 của rev7 (`hhs_r3.py` md5 `cf5420d8…`, `dilution_out.json` md5 `0450ba0a…`), không sửa lõi. **CONTROL:** h = 0,2663 tái lập rev7 (10.805) và h = 0 tái lập headline rev6 (13.969 / P10 12.422 / P90 15.564) — assert trong code. Chạy 2 lần `run1.txt` = `run2.txt` (md5 `6ea8be22…`).
- **Mù giá:** calc không đọc giá. Giá 9.700 (BQ 20/11/2026) kế thừa rev5–rev8, chỉ gắn nhãn ở §0 SAU khi khoá. Giới hạn khai thật: tâm ở CK 0% (13.969) và các mức CK khác đã xuất hiện trong rev6/rev7/recheck trước khi khoá — rev9 không chọn CK theo nhãn; lựa chọn đến từ phép đo v5 + quyết định dải của user 24/11.

## 0. Kết luận

**TÂM CUM (base, r 13,5%, CK holding 0%, sau CK thanh khoản 1,41%): 13.969 đ/cp — vùng P10–P90 12.422–15.564.** So rev8/rev7 (10.805): **+29,3%**.
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 14.255 đ/cp (+2,05% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): HHS: so với lịch sử 10 năm của chính mã — **KHÔNG CHẮC (proxy lệch DD, k=0.23–0.26; N hiệu dụng thấp, 2.09)** — phân vị [fade 2, hold 4], 120 tháng, N hiệu dụng ≈ 2.1 (thước cơ học RI-ROE5Y của chính mã, KHÔNG dùng tâm DD; chỉ hiển thị) ⚠ LỢI NHUẬN SỤT? (ROE TTM/5Y=0.05)
Dải CK holding tham chiếu 0…+20% (user chốt 24/11, CHỈ HIỂN THỊ): tâm CUM 13.969 … 11.593 (P10 @+20%: 10.322).

- **EX** (quyền 5:3 @10.000 + CP 7% phát hành đủ, k = k_base = 1): tâm **11.615** (P10 10.711, P90 12.546); @Ke 12,3%: 11.782. Dải CK 0…+20%: 11.615 … 10.227 (k = 1) / 9.536 (k = 1 − h, đối chiếu cách rev7).
- **Nhãn** (giá 9.700, BQ 20/11/2026, kế thừa): **DƯỚI vùng** (P10 12.422). Luật 4: 0,85 × 13.969 = 11.874 ≥ 9.700 ⇒ ĐẠT. Ở đầu +20% của dải: P10 10.322 > 9.700 ⇒ vẫn DƯỚI; luật 4 0,85 × 11.593 = 9.854 ⇒ ĐẠT sát. EX: TERP sau cổ tức 9.171 < P10 EX 10.711 ⇒ DƯỚI.
- **Đổi lớp nhãn TRONG → DƯỚI và tâm +29,3% > 5% ⇒ phản biện lại đầy đủ (B2)** — `skeptic/r1.json` (thư mục này).
- `forensic_flags` EXCLUDE ⇒ KHÔNG vào candidate plan bất kể nhãn. Sizing V8 không áp (nếu user gỡ EXCLUDE: 2% NAV, đầu dưới chuẩn).
- **Độ tin THẤP** — phụ thuộc một tham số CK có độ tin thấp (v5: N = 12, 1 chế độ thị trường, hull 36,5pp). CK 0% là đầu LẠC QUAN của dải user chốt (≈ trung vị v5 −3,24%, LOO −8,1…+1,6%); mốc hiện tại +20% (15–23%) là 1 holding ≈ 1 quan sát độc lập.

## 1. Đính chính so với rev7/rev8
| # | Hạng mục | rev7/rev8 | rev9 | Nguồn | Ảnh hưởng tâm CUM |
|---|---|---|---|---|---|
| 1 | CK holding base | 26,63% (trung vị N = 6, `ck_holding_vn_20261123`) | **0%**; dải 0…+20% chỉ hiển thị | `ck_holding_vn_20261124_v5/REPORT_CK_HOLDING_v5.md` (trung vị N = 12 −3,24%); `kb/projects/ck-hhs-reference-range-20261124.md` (decided_by user 24/11 15:36 + 15:48 ICT) | 10.805 → **13.969** (+29,3%) |
| 2 | Skeptic r5 (a): EX dùng k = 0,734 trái k_base = 1,0 | chưa sửa | k = 1 (= k_base; với h = 0 hai cách trùng nhau) | assumptions `k_base` | EX 8.846 → 11.615 |
| 3 | Skeptic r5 (b): phạm vi áp CK không nhất quán CUM/EX | chưa sửa | Hết đối tượng ở base (h = 0). Dải hiển thị: CK áp phần HHS × CRV như rev7; EX báo cả k = 1 và k = 1 − h | rev7 §2 | 0 |
| 4 | V1 độ nhạy ±50/±100bp | rev7 ghi "≈ 0" (SAI); rev8 sửa ở CK 26,63% | Tính lại ở base mới (bảng §2) | `calc/calc_rev9_out.json` | 0 |
| 5 | E15 / E16 | rev8 có ở CK 26,63% | Dòng E15 ở base mới; E16 nguyên văn (asof 2026-11-20) | `dd_history_label.py` | 0 |

## 2. Độ nhạy r (V1 + D4 dải Ke + E15) — cùng mô hình, chỉ đổi r, base CK 0%
r tại neo 03/11 = 13,5%; `effective_deposit_rate('2026-11-25')` = 7,40% (cctg_12m 02/11) ⇒ Δ = 0. β = 1 (β 0,5 ⇒ nửa các số dưới).

| r | Tâm CUM | P10 | P90 | Δ (đ/cp) | Δ (%) | EX k = 1 |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 14.255 | 12.723 | 15.818 | +286 | +2,05% | 11.782 |
| 12,5% (−100bp) | 14.206 | 12.669 | 15.774 | +237 | +1,70% | 11.753 |
| 13,0% (−50bp) | 14.087 | 12.534 | 15.667 | +118 | +0,84% | 11.684 |
| 13,4% (đầu trên dải Ke) | 13.993 | 12.443 | 15.583 | +24 | +0,17% | 11.629 |
| **13,5% BASE** | **13.969** | **12.422** | **15.564** | 0 | 0 | **11.615** |
| 14,0% (+50bp) | 13.854 | 12.312 | 15.441 | −115 | −0,82% | 11.548 |
| 14,5% (+100bp) | 13.741 | 12.211 | 15.333 | −228 | −1,63% | 11.482 |

Độ nhạy r thấp vì giá trị là tài sản theo sổ + thặng dư thực hiện trong 1–4 năm (pv(y, Ke) trong `hhs_r3.py`), không terminal vô hạn. Nhãn DƯỚI không đổi trong toàn dải r.

## 3. CK holding — CHỈ HIỂN THỊ (không vào base/sổ)
| CK holding | Tâm CUM | P10 | P90 | Δ so base | EX k = 1 | EX k = 1 − h |
|---|---|---|---|---|---|---|
| **0% (base)** | **13.969** | 12.422 | 15.564 | 0 | 11.615 | 11.615 |
| +19,7% (mốc v5 20/11) | 11.628 | 10.353 | 12.917 | −16,76% | 10.247 | 9.567 |
| **+20% (đầu trên dải user)** | **11.593** | 10.322 | 12.876 | −17,01% | 10.227 | 9.536 |
| 26,63% (base rev7 cũ, N = 6 — đã bị phủ) | 10.805 | 9.634 | 12.012 | −22,65% | 9.767 | 8.846 |
| +37,7% (stress v5, chỉ ghi chú) | 9.490 | 8.485 | 10.556 | −32,06% | 8.998 | 7.696 |

## 4. Soát luật B5 (D3/D4/V1–V8) — kế thừa rev8 §3, cập nhật số
- **D4:** không áp — NAV quỹ đất hữu hạn (`terminal_ronic = NOT_APPLICABLE_FINITE_LIFE`), moat NONE; mảng ô tô P/E 6 < 1/Ke 7,4 ⇒ không ngầm thưởng.
- **D3:** không nhận diện capex tuân thủ trong assumptions/BCTC đã đọc; nghĩa vụ quỹ đất/NƠXH (NC-II, I.14) và KL 08/KL-TTTP = **cần kiểm chứng**, chưa có số.
- **V3:** CK thanh khoản 1,41% (trước CK 14.169). Caveat: 5 tỷ = 48% ADV60 ⇒ chia tranche.
- **V5:** NONE / LOCATION (5F 07–09/11, < 12 tháng). **V6:** FCFE ≤ 0 ⇒ chỉ V_ngắn 4.467 (r 12,3%: 4.903), chỉ hiển thị (asset-play). **V8:** không áp (EXCLUDE).
- Còn mở (không do rev9): cơ cấu HTK NC-II HH1–HH4 (kịch bản w 10–30% ⇒ −2,3…−9,0%, không vào base); BV NĐL chưa kiểm toán; nội dung lấy ý kiến cổ đông 14–25/12/2026 (NQ 10/NQ-HĐQT) ⇒ làm lại bản pha loãng.

## 5. WARNING (giữ rev7 §4)
Tăng vốn 60% (quyền 5:3 @10.000) + cổ tức CP 7%; NQ 10/NQ-HĐQT nội dung chưa công bố; chuyển nhượng HĐ tiền gửi 852,0 tỷ TCH↔CRV/NĐL; TB 2124/TB-TTCP (7,87 tỷ); KL 08/KL-TTTP (NƠXH Pruksa). Pháp lý chỉ WARNING.

## 6. Phạm vi đề nghị cho phản biện (§E4)
(1) Việc chọn CK 0% làm base (đầu lạc quan của dải user chốt) có đúng chỉ đạo "dải hiển thị, không vào base" và có cơ sở đo không, hay nên là mức khác; (2) tính đúng của bảng độ nhạy r §2 và CONTROL; (3) EX k = 1; (4) moat NONE, cân bằng hai chiều (HH1–HH4, NƠXH chiều xuống; v5 trung vị âm chiều lên); (5) thiếu hạng mục (D3 nghĩa vụ bắt buộc).
