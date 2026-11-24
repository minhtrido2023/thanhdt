# HHS — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, job Taylor_20261124_094353)

Bản rà lại **REPORT_rev7** (`agents/Taylor/research/dd_dilution_update_20261110/HHS/REPORT_rev7.md`, md5 `afe93ea4…`) theo HANDOFF `dd_recheck_20261124`. **Không làm lại mô hình**: tái dùng nguyên lưới r3 + CK holding 26,63% của rev7 (assumptions khoá md5 `3afcd113013fad82acfa5ea35c5bce1d`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp).

- **Calc:** `calc/calc_recheck.py` (md5 `e307fdf0…`). Assert md5 lõi `hhs_r3.py` (`cf5420d8…`), `dilution_out.json` (`0450ba0a…`), assumptions rev7, `calc_rev7_out.json` (`b7d912f6…`). **Chân CONTROL:** ở r = 13,5%, h = 0,2663 tái lập đúng từng số rev7 (tâm 10.805, P10 9.634, P50 10.765, P90 12.012, trước CK 10.959) — assert trong code.
- Chạy 2 lần: `run1.txt` = `run2.txt` = md5 `bd675399…`. Output `calc/calc_recheck_out.json` (md5 `8d36413c…`).
- Mù giá: calc không đọc giá. Giá so sánh 9.700 (BQ 20/11/2026) chỉ dùng ở §0 để gắn nhãn, kế thừa rev5–rev7.

## 0. Kết luận

**TÂM CUM (base, r 13,5%, CK holding 26,63%): 10.805 đ/cp — vùng 9.634–12.012. KHÔNG ĐỔI so với rev7.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 11.014 đ/cp (+1,93% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (proxy lệch DD, k=0.23–0.26; N hiệu dụng thấp, 2.09)** — phân vị [fade 2, hold 4], 120 tháng, N hiệu dụng ≈ 2.1 ⚠ LỢI NHUẬN SỤT? (ROE TTM/5Y=0.05)

- **Nhãn** (giá 9.700, BQ 20/11/2026): **TRONG vùng**, sát đáy (P10 9.634). Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 10.805 = 9.184). Nhãn không đổi so với rev7.
- **EX** (phát hành đủ, k = 0,734 như rev7): tâm 8.846 (r 12,3%: 8.969). k = 1: 9.767 (r 12,3%: 9.889). Phản bác k của skeptic r5 vẫn **CHƯA ÁP** (§3).
- **Tâm đổi 0% (<5%), lớp nhãn không đổi** ⇒ phần luật mới (D3/D4/E15/E16/V) chỉ cần soát cơ học. **Nhưng** base của rev7 đang REFUTED_OPEN (skeptic r5) và tham số CK holding nền đã bị chính các phép đo sau (v2–v5, 24/11) phủ lên ⇒ xem §3, khuyến nghị lớp **FULL** sau khi user chốt CK.
- `forensic_flags` EXCLUDE ⇒ không vào candidate plan, bất kể nhãn. Sizing V8 không áp.

## 1. Thay đổi so với rev7

| # | Luật | rev7 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | V1 độ nhạy ±50/±100bp | Ghi "≈ 0 đ/cp (NAV quỹ đất)" | **SAI — sửa.** Mô hình có chiết khấu thời gian pv(y, Ke) trên giá gốc khối HTK cũ (6.009,8 tỷ), thặng dư HTK, backlog và I.14 (`hhs_r3.py` dòng 66–68). Số đo ở bảng §2 | 0 (chỉ là số báo kèm) |
| 2 | D4 dải Ke 12,3–13,4% | Không báo hai đầu dải | Bổ sung: 11.014 / 10.822 | 0 |
| 3 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 4 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 5 | V6 V_ngắn | 4.466 đ/cp ở r 13,5% | Giữ; ở r 12,3% = 4.903 đ/cp (chỉ hiển thị) | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng `deposit_rate_vn` = 7,40% cctg_12m 02/11). Đọc lại 24/11/2026: vẫn 7,40% (last_update 16/11) ⇒ Δ = 0 ⇒ r = 13,5%. β = 1 (giả định).

| r | Tâm CUM | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | EX k=0,734 | EX k=1 |
|---|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 11.014 | 9.851 | 12.237 | +209 | +1,93% | 8.969 | 9.889 |
| 12,5% (−100bp) | 10.979 | 9.814 | 12.205 | +174 | +1,61% | 8.948 | 9.868 |
| 13,0% (−50bp) | 10.891 | 9.723 | 12.098 | +86 | +0,80% | 8.897 | 9.817 |
| 13,4% (đầu trên dải Ke) | 10.822 | 9.652 | 12.028 | +17 | +0,16% | 8.856 | 9.777 |
| **13,5% BASE** | **10.805** | **9.634** | **12.012** | 0 | 0 | 8.846 | 9.767 |
| 14,0% (+50bp) | 10.720 | 9.547 | 11.932 | −85 | −0,79% | 8.797 | 9.717 |
| 14,5% (+100bp) | 10.638 | 9.456 | 11.854 | −167 | −1,55% | 8.749 | 9.669 |

- Độ nhạy r thấp vì giá trị nằm ở tài sản theo sổ + thặng dư thực hiện trong 1–4 năm, không có terminal vô hạn. Đối chiếu CK 0% (headline rev6): r 12,3% cho 14.255 (+2,05% so với 13.969) — độ nhạy r gần như không phụ thuộc mức CK.
- **Nhãn nhạy với r (chỉ báo kèm, E15 không dùng cho nhãn):** P10 vượt giá 9.700 khi r ≤ 13,0% (P10 9.723 ở 13,0%; 9.851 ở 12,3%) ⇒ ở các mức r này nhãn sẽ là DƯỚI vùng; ở r ≥ 13,4% là TRONG. Nhãn base rev7 (TRONG) nằm sát biên — thêm một lý do để coi nhãn là mong manh.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** **không áp dụng** — mô hình NAV quỹ đất, thặng dư thực hiện hữu hạn (y 2,5/3,25/4 năm), `terminal_ronic = NOT_APPLICABLE_FINITE_LIFE`, moat NONE (lint L6 đạt). Thành phần duy nhất mang tính bội số vô hạn là mảng ô tô: LNST 25/35/50 tỷ × P/E 5/6/8 (`hhs_r3.py` SC). Ở Ke 13,5%, g = 0, RONIC = Ke ⇒ P/E hợp lý = 1/Ke = 7,4. P/E kịch bản cơ sở 6 **thấp hơn** 7,4 ⇒ không ngầm thưởng RONIC > Ke. Không lệch.
- **D3 capex tuân thủ:** assumptions rev7 chỉ có 2 hạng mục, đều `growth` / `generates_revenue=true` (I.14 NPV0_BOOK; phần vốn thiếu SCENARIO_ONLY có `independent_basis`). **Không nhận diện được** chi bắt buộc-không-tạo-doanh-thu trong BCTC Q3/2026 HN đã đọc. Hai chỗ **cần kiểm chứng**, không có số để đưa vào base hay độ nhạy: (i) nghĩa vụ quỹ đất/NƠXH theo quy định ở NC-II, I.14 (nếu có, thường đã nằm trong tổng mức đầu tư — chưa xác nhận); (ii) KL 08/KL-TTTP (NƠXH Pruksa) chưa có số liệu. Ghi lệch "chưa kiểm hết", không ước số.
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0). Dải Ke 12,3–13,4% nay đã báo (§2). Độ nhạy ±50/±100bp rev7 sai (ghi ≈0) — đã sửa (§1 #1).
- **E15/E16:** đã thêm (§0).
- **V3 thanh khoản:** đã đủ — tâm trước CK 10.959, sau CK 5 tỷ (1,41%) 10.805; nhãn theo giá trị sau CK. Caveat rev5 giữ nguyên: 5 tỷ = 48% ADV60 (10,35 tỷ, 20/11) ⇒ CK 1,41% có thể thấp; vị thế phải chia tranche.
- **V5 moat:** đã đủ — 5F đầy đủ 07–09/11/2026 (`dd_redo_20261105/HHS/ADDENDUM_5F.md`) < 12 tháng ⇒ tái dùng: NONE / LOCATION, rủi ro số 1 = thực hiện thặng dư quỹ đất + dòng tiền lên HHS qua 2 tầng holding. Kiểm nhanh 24/11: không dữ kiện quỹ đất mới.
- **V6:** đã đủ — FCFE ≤ 0 (CFO 9T/2026 −2.110,2 tỷ) ⇒ chỉ V_ngắn 4.466 đ/cp (r 12,3%: 4.903), chỉ hiển thị; chênh với tâm NAV giải thích ở rev5 §4 (asset-play, thặng dư chưa đi qua lợi nhuận).
- **V7:** không dùng snapshot vĩ mô.
- **V8:** không áp (EXCLUDE). Nếu user gỡ EXCLUDE: đề xuất **2% NAV** (đầu dưới chuẩn 2–4%), giữ như rev5/rev6 — vì nhãn sát biên và phụ thuộc tham số CK.

### Việc còn mở kế thừa — CHẶN việc nâng nhãn skeptic

1. **Skeptic r5 (rev7) REFUTED, bản sửa chưa áp:** (a) EX base k = 0,734 trái `k_base = 1,0` trong assumptions (−9,4% EX); (b) phạm vi áp CK không nhất quán giữa CUM (chừa OTHER/ô tô) và EX (áp lên tiền mới); (c) tham số CK mong manh (N = 6). Recheck **không sửa** các điểm này (ngoài phạm vi luật mới; sửa = rev8 + phản biện đầy đủ).
2. **Tham số CK holding nền đã bị phép đo sau phủ lên:** `ck_holding_vn_20261124_v5/REPORT_CK_HOLDING_v5.md` (24/11): trung vị N = 12 là **−3,24%**, mốc hiện tại 20/11 = **19,7%**, hull 36,5pp (không đạt dải trung tâm < 20pp); đề xuất phương án A của v5 là base 0%. Base 26,63% (N = 6, 23/11) của rev7 vì vậy **không còn là số đo mới nhất**. Chưa có user chốt. Đối chiếu, cùng mô hình (chỉ hiển thị, KHÔNG đổi base):

| CK holding | Tâm CUM (r 13,5%) | P10 | P90 | Tâm @ r 12,3% | Nhãn @ 9.700 |
|---|---|---|---|---|---|
| 26,63% (base rev7, N = 6) | 10.805 | 9.634 | 12.012 | 11.014 | TRONG |
| 19,7% (v5 mốc hiện tại) | 11.628 | 10.353 | 12.917 | 11.858 | DƯỚI |
| 0% (≈ trung vị v5; headline rev6) | 13.969 | 12.422 | 15.564 | 14.255 | DƯỚI |

   ⇒ Nếu user chốt CK theo v5 (0% hoặc 19,7%), tâm tăng **+7,6% đến +29,3%** và nhãn đổi TRONG → DƯỚI ⇒ cần **rev8 + phản biện đầy đủ**.
3. Nội dung lấy ý kiến cổ đông 14–25/12/2026 (NQ 10/NQ-HĐQT 20/11) — mốc làm lại bản pha loãng.
4. Cơ cấu HTK NC-II thấp tầng/cao tầng HH1–HH4 (kịch bản −2,3…−9,0%, không vào base).
5. BV NĐL chưa kiểm toán.

## 4. WARNING (giữ rev7 §4)
Tăng vốn 60% (quyền 5:3 @10.000) + cổ tức CP 7%; NQ 10/NQ-HĐQT nội dung chưa công bố; chuyển nhượng HĐ tiền gửi 852,0 tỷ TCH↔CRV/NĐL; TB 2124/TB-TTCP (7,87 tỷ); KL 08/KL-TTTP (NƠXH Pruksa). Pháp lý chỉ WARNING.

## 5. Phạm vi đề nghị cho phản biện (§E4)
Moat (NONE/LOCATION có bằng chứng đủ không), cân bằng hai chiều (chiều lên: CK đo mới hơn thấp hơn; chiều xuống: HH1–HH4, NƠXH), thiếu hạng mục (D3 capex tuân thủ — có nghĩa vụ bắt buộc nào chưa vào base?), và kiểm tính đúng của bảng độ nhạy r §2 (sửa lỗi "≈0" của rev7).
