# NT2 — Rà lại DD theo luật B5 + E15/E16 (25/11/2026, job Taylor_20261125_032446, đợt 3 job B)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/NT2/REPORT_r3.md`, md5 `510e112e…`) theo `dd_recheck_20261125w3/HANDOFF.md`. **Không làm lại mô hình**: tái dùng nguyên `calc_r3/model_r3.py` + `assumptions_r3.json` (md5 `675413d6a93559f6c55b0dd2cfd009ea`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp).

- **Nguồn calc:** `calc_r3/` bị TRIM khỏi git ngày 19/11 (commit `14ad1c925`). Khôi phục bằng `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105/{NT2,_common_020021,_common,_shared,TOP5B_CORRECTIONS_20261108.md,STANDARD_r2.md}` ra `/tmp/ddrestore_NT2/agents/Taylor/research/dd_redo_20261105/` (đọc được tại đó). md5 của 17 file đầu vào trong `LOCK_md5.txt` khớp (assert trong code; 22/22 dòng repo-relative khớp khi kiểm bằng `md5sum -c`).
- **Calc:** `calc/calc_recheck.py`. **Chân CONTROL:** chạy lại `model_r3.py` cho stdout md5 `f2c6788a0c53c0cdf7b7acddb941b4ae` = `run1.md5` của r3 (assert). Tâm 24.003 / P10 18.301 / P90 29.619 cũng assert.
- Chạy 2 lần: `calc/run1.txt` = `calc/run2.txt` = md5 `92aecb63…`. Output `calc/calc_recheck_out.json`.
- Mù giá: calc không đọc giá mới. Giá 22.200 (BQ 06/11/2026, đã ex-div 1.000 đ GDKHQ 29/10) kế thừa r3, chỉ dùng cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 0,92% @5 tỷ): 24.003 đ/cp — vùng 18.301–29.619 (P10–P90 lưới 225 kết cục). KHÔNG ĐỔI so với r3.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 24.638 đ/cp (+2,64% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (rẻ…trung tính)** — phân vị [fade 27, hold 67], 120 tháng, N hiệu dụng ≈ 6.0 ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.89)

- **Nhãn** (giá 22.200, BQ 06/11/2026, kế thừa r3): **TRONG vùng** (−7,5% so tâm; 35,7% trọng số kết cục dưới giá). Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 24.003 = 20.403). Nhãn không đổi so với r3.
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới chỉ là MECH.
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding v5: NT2 không có tầng holding ⇒ không áp. (ii) r: neo 03/11 lãi huy động 12T hiệu dụng 7,40%; đọc lại 25/11 = 7,40% (`deposit_rate_vn.effective_deposit_rate('2026-11-25')` → `cctg_12m(2026-11-02)`) ⇒ Δ = 0, r = 13,5%. (iii) RONIC terminal: NT2 định giá theo thời hạn hữu hạn 5–15 năm, giá trị sau thời hạn = 0 (moat NONE) — chặt hơn RONIC = Ke, không bị phủ. (iv) Độ nhạy r ở r3 §7 đã tính từ mô hình; khớp lại từng đồng (§2).
- **Sizing (V8):** nếu có ý định mua (hiện nhãn TRONG ⇒ không có tín hiệu), trần đề xuất **2% NAV** (đầu dưới dải chuẩn 2–4%: moat NONE, thời hạn PPA chưa xác minh, số Q3 chưa soát xét). Tương đương ~19 triệu ở NAV SpaceX ≈ 0,94 tỷ (r3 §0) — nằm trong cỡ sleeve 10–40 triệu r3 đã tính CK (0,04–0,08%).

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20; `calc/dd_history_label_NT2_2026-11-20.*`) | 0 |
| 3 | D4 dải Ke 12,3–13,4% | Chỉ ±50/±100bp | Bổ sung: 24.638 / 24.054 | 0 |
| 4 | V6 hai nền | Chưa có | Bổ sung §3 (chỉ hiển thị) — **cờ D > ln2** | 0 |
| 5 | D3 capex tuân thủ | Chưa soát | Soát: không nhận diện hạng mục (§3) | 0 |
| 6 | V8 sizing | "sleeve 10–40 triệu" | Trần 2% NAV theo chuẩn 2–4% | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%), β = 1 (giả định), Δ đến 25/11 = 0. Trục r của lưới (±1pp, ¼–½–¼) dịch theo r tâm.

| r | Tâm | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | % trọng số dưới 22.200 |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 24.638 | 18.629 | 30.663 | +634 | +2,64% | 32,3% |
| 12,5% (−100bp) | 24.528 | 18.585 | 30.483 | +525 | +2,19% | 32,8% |
| 13,0% (−50bp) | 24.261 | 18.449 | 30.043 | +258 | +1,07% | 34,2% |
| 13,4% (đầu trên dải Ke) | 24.054 | 18.319 | 29.704 | +51 | +0,21% | 35,7% |
| **13,5% BASE** | **24.003** | **18.301** | **29.619** | 0 | 0 | 35,7% |
| 14,0% (+50bp) | 23.754 | 18.165 | 29.294 | −249 | −1,04% | 37,0% |
| 14,5% (+100bp) | 23.513 | 18.023 | 28.894 | −490 | −2,04% | 37,5% |

- ±100bp khớp đúng r3 §7 (24.528 / 23.513). Độ nhạy r nhỏ vì net cash 11.398 đ/cp (~47% tâm) và dòng tiền hữu hạn ~10 năm.
- Nhãn TRONG ở mọi mức r trong bảng. Luật 4 ở r 12,3% (chỉ báo kèm): ngưỡng 20.942 < giá 22.200 ⇒ vẫn không đạt.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** không áp dạng Gordon — mô hình là dòng tiền hữu hạn (thời hạn 5/8/10/12/15 năm), giá trị sau thời hạn = 0 (moat NONE, `ADDENDUM_5F.md`). Bảo thủ hơn RONIC = Ke. Độ nhạy WIDE (vận hành vô hạn RONIC = Ke sau 2036) ở ADDENDUM_5F: +19,7% trên khung r2 — chỉ là độ nhạy, không vào base. Không lệch.
- **D3 capex tuân thủ:** không nhận diện hạng mục chi bắt buộc-không-tạo-doanh-thu trong `assumptions_r3.json`/REPORT_r3. Chi đại tu định kỳ (bảo trì, không phải tuân thủ) đã nằm trong trục FCF − LNST ±150 tỷ/năm (nút −150 có cơ sở CF_OA 2022–24). **Cần kiểm chứng:** nghĩa vụ môi trường (quan trắc khí thải/xử lý nước làm mát) và nghĩa vụ tháo dỡ/hoàn nguyên cuối đời nhà máy chưa đọc trong thuyết minh; không có số ⇒ không vào base, không ước.
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0); dải Ke 12,3–13,4% nay đã báo (§2); ±50/±100bp tính từ mô hình.
- **E15/E16:** đã thêm (§0). E16 có cờ "ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.89)" — khớp WARNING r3 §8 mục 8 (9T/26 có thể bị soát xét giảm) và ROE vận hành 34,3% do khấu hao hết (r3 §5); base LNST 800 đã neo biên lịch sử 728–829, không dùng LNST đỉnh 9T/26.
- **V3 thanh khoản:** đã đủ (r3 §6): trước CK 24.226, sau CK 5 tỷ (0,92%) 24.003; sleeve 10–40 triệu 24.206–24.216. Nhãn theo sau CK.
- **V5 moat:** đã đủ — 5F 07–08/11/2026 (`ADDENDUM_5F.md`, < 12 tháng): **NONE**, CONTRACT/LOCATION, `moat_durable=false`, ROIC_Min5Y −0,6% (QTP NARROW 12,5%, HTI 9,9%). Rủi ro số 1 = thời hạn PPA/GSA + cạn khí mỏ hiện hữu ~2030. Kiểm nhanh 25/11: không đọc BCTC/CBTT mới trong recheck này.
- **V6 (bổ sung, chỉ hiển thị):** lấy nguyên từ `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11/2026, fin_time 20/10; file bị TRIM, khôi phục từ `3750ca176^`). V_ngắn **20.350** (LNST chuẩn hoá 652 tỷ, ROE 12,6%, g 12,75% > ROE ⇒ tái đầu tư bị chặn ở 80%) / V_dài **57.794** / D = **1,044** > ln2 (0,693), < ln3 (1,099) ⇒ **cờ D > ln2**.
  - Nguồn chênh: (a) V_dài là FCFE 3 năm chuẩn hoá VÔ HẠN — FCFE NT2 2022–24 gồm khấu hao ~550 tỷ/năm trong khi capex chỉ 1–11 tỷ/năm (BQ `CF_Invest_P0`), tức dòng tiền của tài sản đã gần khấu hao hết, đem vốn hoá vô hạn; DD giới hạn dòng tiền ở thời hạn PPA/khí 5–15 năm, giá trị sau thời hạn 0. (b) V_ngắn dùng ROE trên vốn chủ có ~47% là tiền ròng ⇒ ROE thấp, g > ROE làm V_ngắn sụp (nhánh "ROE<g"). (c) Vốn lưu động: phải thu EVN 4.252 tỷ dao động mạnh theo kỳ ⇒ FCFE 3 năm không ổn định.
  - Vùng đọc mở rộng (chỉ hiển thị, theo luật cờ): **[min, max] hai nền = [20.350; 57.794]**. Tâm/vùng/nhãn vẫn từ mô hình DD; không trộn. V_dài > giá nhưng capex/CFO của NT2 RẤT THẤP ⇒ không thuộc ca "FCFE thấp vì đầu tư tăng trưởng"; chênh là do giả định vô hạn của nền máy.
  - Caveat: r của engine dd_blend (ERP-based), không phải 13,5%; chưa chạy lại ở 13,5%. "chưa qua tiêu chí khoá trước, chỉ theo dõi".
- **V7:** không dùng snapshot vĩ mô.
- **V8:** trần 2% NAV (§0).

### Việc còn mở kế thừa (không chặn nhãn)
1. Thời hạn PPA/GSA (Phụ lục 13 HĐ mua bán khí — NQ HĐQT 08/07/2026 chưa đọc); hai nguồn mâu thuẫn ~2036 vs PPA gốc 2011–2020.
2. Lịch sử chi phí trả trước đại tu 2015–25 (quyết định nhánh FCF −150 vs bản D +110).
3. Số Q3/2026 tự lập, chưa soát xét (tiền lệ bán niên −94 tỷ LNST).
4. Thuyết minh tiền gửi theo ngân hàng (SHB), phải thu EPTC quá hạn, Qc 2027.
5. Pháp lý: chưa quét lại sau 05/11/2026 (WARNING r3 §8).

## 4. Giả định khoá (không đổi)
Như r3 §10. md5 `assumptions_r3.json` = `675413d6a93559f6c55b0dd2cfd009ea`; file khoá `calc_r3/LOCK_md5.txt` md5 `524b45989db9737e96c762edd6b2f4ef` (= `assumptions_md5` sổ rev2).
