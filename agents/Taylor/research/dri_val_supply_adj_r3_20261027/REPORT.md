# DRI — định giá lại lần 3, sửa lỗi skeptic r2 (job `Taylor_20261027_100801`, 27/10/2026)

> Chỉ nghiên cứu: không lệnh, không pin. Lưới khai trước trong `PREREG.md` (commit `ee77a6821`, md5 `f22f23ef…`), commit
> trước khi chạy số. `python3 model.py` → `out.txt` (md5 `d60ff3ea…`, giống từng byte dưới `env -u TZ` và `TZ=America/New_York`).
> Nhãn: [BCTC3] BCTC HN Q3/26 · [SX] soát xét H1 · [BCTN] · [BQ] · [FEED] · [UL] giả định chưa có nguồn · [NỀN] hiểu biết nền.
> **Bản để skeptic phản biện tiếp, không phải kết luận chốt.** Số skeptic (13,0/14,3/15,5k; đường đáy 9.334…) chỉ đối chiếu ở §8, SAU khi có kết quả.

## 0. Trả lời thẳng
**Selfcheck** (out §0): tái lập 10.878 / 11.031 (model_q3), 14.301 (r1), hàng r2 11.061 / **12.481** / 13.901 / 15.321 trước khi đổi tham số.

**(1) FV theo từng mid** (đ/cp, 60/40; ngoặc = 14.700 / 14.400 so FV) — bốn cột ngang hàng, không cột nào là tâm:
| | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 |
|---|---|---|---|---|
| **Tâm r3** | **10.521** (+40% / +37%) | **11.863** (+24% / +21%) | **13.206** (+11% / +9%) | **14.548** (+1% / −1%) |
| TDND haircut 50% | 10.043 | 11.385 | 12.728 | 14.070 |
| TDND haircut 100% | 9.565 | 10.907 | 12.250 | 13.592 |
| Trôi chi phí THỰC 1%/năm | 7.705 | 8.981 | 10.256 | 11.531 |
| Đối chứng: khung trộn r2 (r 12% trên dòng tiền tiền-2025) | 9.628 | 10.674 | 11.720 | 12.766 |
| Lưới khai trước (69.984 ô) P10 – trung vị – P90 | 3.171 – 6.793 – 10.181 | 4.908 – 8.453 – 11.894 | 6.556 – 10.123 – 13.681 | 8.133 – 11.796 – 15.532 |
| Tỷ lệ ô lưới ≥ 14.700 / ≥ 14.400 | 0% / 0% | 1% / 1% | 5% / 6% | 16% / 19% |
- Tâm: khung thực (r danh nghĩa 12% ⇒ r thực 8,74%, π 3% [NỀN]), C_ref 30,22 (C_cal ở thuế 9T), k 0,3, f 0,5, sản lượng −2%/năm từ 2030, thuế 19,58%, KTPL 10,6%, w 10%, quỹ dự phòng Lào giữ tới 2054, haircut tiền Lào 15%, TDND 0, tồn kho X 1.717 t, Q4 Base.
- **Lưới lệch về phía bi quan theo cách khai** (C_ref có 2 mức trên tâm/1 dưới; d0 2028 sớm hơn tâm; trục g chỉ có chiều xấu; quỹ Lào có "mất"). Vì vậy trung vị lưới < tâm. Không trục nào được gán xác suất; P10/P90 là phân vị lưới.
- Đuôi dưới lưới có ô FV âm (44/7.776 ở mid 1,865) vì model không có quyền dừng khai thác khi lỗ. Sàn LN lõi ≥ 0 từng năm (POST-HOC, out §9) nâng P10 lưới lên 6.963 / 8.001 / 9.108 / 10.263. Tâm hầu như không đổi.

**(2) 14.700 (đóng 26/10) và 14.400 (đóng 27/10) so FV tâm:** cao hơn **+40 / +24 / +11 / +1%** (14.700) và **+37 / +21 / +9 / −1%** (14.400) ở mid 1,865 / 1,97 / 2,075 / 2,18. Giá chỉ ngang FV nếu mid ≈ 2,18 (≈ trung vị 10 năm THỰC 2,185) **và** không trôi chi phí thực, không haircut TDND.

**(3) Trục nhạy nhất** (đổi một trục quanh tâm, out §4):
| Trục | Biên độ FV (đ/cp) | Đo / đoán |
|---|---|---|
| **Đường sản lượng** (bắt đầu giảm 2028/2030/2035 × 2/3%/năm) | **4.165 – 5.078** | ĐOÁN [UL]; không có bảng tuổi vườn |
| **Mid RSS3** 1,865 → 2,18 | **4.028** | ĐOÁN (các mốc tham chiếu là trung vị đo [FEED]) |
| Trôi chi phí thực 0 / 1%/năm | 2.815 – 3.017 | ĐOÁN; trục duy nhất dùng lập luận "chi phí trôi" |
| C_ref 30 / 30,22 / 31,5 / 32 | 2.032 | 30,22 và 30 ĐO; 31,5/32 không nguồn |
| r danh nghĩa 10/12/13% | 970 – 2.038 | ĐOÁN |
| Tồn kho vượt 0/1.717/3.370 t | ~1.850 | 1.717 ĐO [SXKD] |
| f (tỷ trọng giá vốn cố định) | ~1.500 | ĐOÁN |
| Quỹ dự phòng Lào tự do/2054/mất | 818 – 1.248 | tỷ lệ 7,8% ĐO; xử lý ĐOÁN |
| TDND 0/50/100% | 956 | số dư ĐO; khả năng thu hồi CHƯA BIẾT |
| h tiền Lào 0/15/30% | 806 | ĐOÁN |
| k chọn/0 | 289 – 1.617 | backcast N=4 |
| Q4 Bear↔Bull | 661 | ước lượng |
| Trọng số đường 80/20…40/60 | 348 – 539 | Bobby |

**(4) Vùng mua có biên ≥ 15% kể cả khi đáy 2 năm** (đường đáy RSS3 2027 = 2028 = 1,60, rồi mid; tâm các trục khác; out §6):
| Ngưỡng (PB) | mid 1,865 | mid 1,97 | mid 2,075 | mid 2,18 |
|---|---|---|---|---|
| FV đường đáy 1,60 | 8.415 | 9.592 | 10.770 | 11.947 |
| ≤ 9.000 (0,90x) | −7% | +7% | **+20% ✓** | **+33% ✓** |
| ≤ 10.000 (1,00x) | −16% | −4% | +8% | **+19% ✓** |
| ≤ 11.500 (1,15x) | −27% | −17% | −6% | +4% |
| ≤ 13.000 (1,30x) | −35% | −26% | −17% | −8% |
- **Không ngưỡng nào đạt ≥15% ở cả bốn mid.** 9.000 đạt ở mid ≥ 2,075; 10.000 chỉ đạt ở mid 2,18; 11.500 và 13.000 không đạt ở mid nào.
- Đáy 1,70 nhích nhẹ (9.000: −3 / +10 / +23 / +36%; 10.000: −13 / −1 / +11 / +23%) — không đổi kết luận.
- TDND haircut 100% trên đáy 1,60: chỉ còn 9.000 @ mid 2,18 (+22%) đạt.
- Ở P10 lưới trên đường đáy: không ngưỡng nào đạt ở mid nào (kể cả có sàn POST-HOC: P10 4.276 – 7.192).

**(5) §2.5 #3/#4 (calculated_fear_state_backstop.md):**
- **#3 chi phí thấp — proxy ủng hộ, chưa chứng minh:** GPM TB quý 2021–25 [BQ] DRI **39,2%** vs DPR 31,2%, TRC 25,1%, PHR 24,9%. Chỉ là proxy (peers có cơ cấu khác, vườn VN). Không có số giá thành/tấn của peers.
- **#4 sàn tài sản thực — KHÔNG đạt trên PB.** Sổ sách "cứng" (tiền + ĐT đáo hạn NH/DH + tồn kho + phải thu − tổng nợ) [BCTC3] = **294,5 tỷ = 4.023 đ/cp**; bỏ TDND 70 tỷ: **3.067 đ/cp**. Phần còn lại của BVPS 9.971 (**5.948 đ/cp**) là vườn cây 333,7 + XDCB 72,7 tỷ trên đất tô nhượng Lào. Không có bằng chứng giá trị thanh lý:
  - đất không sở hữu, hợp đồng tô nhượng (thoả thuận dự án 19/11/2004) [BCTN25];
  - gỗ thanh lý ở Lào "chưa hình thành thị trường" [dd_DRI REPORT, BCTN];
  - LAK làm VCSH −38,16 tỷ chỉ trong 9T/26 [BCTC3 hn_29].
  ⇒ **PB ≤ 1 (~9.971) không phải sàn tài sản thực theo #4.** Sàn chứng minh được chỉ ~3–4k đ/cp.

## 1. Kiểm lại từng lỗi skeptic (trước khi sửa; đều ĐÚNG)
| # | Kết quả kiểm | Sửa trong r3 | Tác động FV tâm (cầu nối §5) |
|---|---|---|---|
| 1 C_ref | C_cal 30,45 (thuế Q3) / **30,22** (thuế 9T); 9T/26 quy về P 47,24 = 30,09; FY26E 32,39 @53,71 ⇒ 30,45 (out §1) | tâm = C_cal 30,22; lưới {30; 30,22; 31,5; 32}, hai mức cuối không có nguồn | **+1.791** |
| 2 KTPL | trích 16,68 tỷ 9T/26 = **10,60%** LNST 2025; 11,55 tỷ 9T/25 = 10,62% LNST 2024 [BCTC3; BQ]. Cơ chế: trích từ LNST trong VCSH (không phải chi phí lương), quỹ đã **chi thật 10,94 tỷ** trong 9T ⇒ tiền rời công ty | κ 10,6% trừ khỏi FCF, Q4, lãi tồn kho | −1.235 … −1.732 |
| 2 Quỹ Lào | 12,30 tỷ = 7,8% LNST, nằm ở "quỹ khác" VCSH (không rời tập đoàn, bị giữ ở Lào) | trục τ {tự do; giữ tới 2054 không lãi; mất}, tâm 2054 | −779 … −1.098 |
| 3 w | khấu trừ tại nguồn 11,07 tỷ ghi giảm LNCPP thẳng (bảng VCSH), không qua thuế TNDN ⇒ w = 10% cố định. Quan sát: 11,07 = 7,0% LNST 2025; 9,03 = 8,3% LNST 2024 ⇒ áp 10% lên toàn FCF là hơi thận trọng | w 10%, bỏ w = 0 | 0 (r2 đã dùng 10%) |
| 8 thuế | 9T/26 (39,50+1,28)/208,21 = **19,58%** | thuế 19,58% | −131 … −199 |
| 6 TDND | 70 tỷ nằm trong 271,8 tỷ ĐT đáo hạn NH ⇒ đang tính 100% trong tiền ròng (956 đ/cp). Góp vốn 3 tỷ KHÔNG nằm trong tiền ròng | trục {0; 50; 100%}, báo cả ba | 0 / −478 / −956 |
| 7 sản lượng | thừa nhận: BCTN25 "đang dần bước vào chu kỳ thanh lý", thu mua tiểu điền "bù đắp sản lượng thiếu hụt" | tâm d0 2030 (r2: 2035), lưới 2028/2030/2035 × 2/3% | −1.549 … −1.890 |
| 4,5 | thừa nhận | §2 khung thực MỘT lần; 4 mid ngang hàng; vùng mua trên đường đáy | — |
- Mâu thuẫn chưa giải: thuyết minh EPS (hn_32) nói "số trích quỹ cả năm 2025 là 3,90 tỷ" ≠ 16,68 tỷ trong bảng VCSH. Dùng 16,68 vì khớp với dòng chi tiền của quỹ. Có thể 3,90 là phần riêng của công ty mẹ. Nếu đúng 3,90 (≈2,5% LNST) thì FV tăng khoảng +0,9–1,3k (`ước lượng` = ~3/4 bước KTPL ở §5, chưa chạy).

## 2. Khung thực/danh nghĩa — xử lý một lần
- Giá, C, SGA, FX đều ở "tiền 2025" ⇒ chiết khấu bằng **r thực** (1,12/1,03 − 1 = 8,74%). Cầu nối: **+1.362 … +2.356** so với khung trộn r2.
- Lập luận "chi phí trôi theo lạm phát" chỉ dùng ở **một trục** g (trôi chi phí THỰC, C nhanh hơn giá đầu ra). Không dùng để chọn C_ref, mid hay r. g = 1%/năm cộng dồn 28 năm ⇒ C 2054 cao hơn ~32% thực. Đây là trục nhạy thứ ba.
- Giả định PPP (VND/LAK mất giá bù chênh lạm phát) là [UL]. Nếu LAK mất giá nhanh hơn chênh lạm phát, chi phí VND hoá ra lại giảm, tức là có lợi cho DRI. Nhưng điều đó đi kèm rủi ro chuyển tiền (đã có trục h).

## 3. Phân rã PEAK (tỷ, tâm; out §2)
mid 1,97: Q4 31,5 · vận hành 2027–54 564,6 · quỹ Lào thu hồi 2054 9,5 · tồn kho 74,6 · tiền ròng 153,3 ⇒ 11.388. mid 2,075: vận hành 664,1 ⇒ 12.794.

## 4. Chưa tính (không có số có nguồn)
- Gỗ thanh lý: BCTN ghi chờ liên doanh nhà máy gỗ/viên nén; thị trường "chưa hình thành".
- Sầu riêng 238 ha tới 2030.
- Tái canh: 37,77 ha/2026 trên 8.592 ha; khó cho mủ trước 2054.
- Thu mua tiểu điền ~2.000 t/2026: biên gia công chưa biết.
- Dịch vụ mới: xăng dầu, cửa hàng.
- Giá trị cuối sau 2054 (L0). Model chỉ giữ "khác 10 tỷ/năm".
- Ba khoản đầu là phần có thể làm FV **tăng**. Bên giảm chưa tính: chi phí trả đất/khoanh nuôi khi hết chu kỳ 1, và rủi ro gia hạn tô nhượng.

## 5. Cầu nối r2 → r3 (cộng dồn, 60/40; out §5)
| | mid 1,865 | 1,97 | 2,075 | 2,18 |
|---|---|---|---|---|
| r2 tâm | 11.061 | 12.481 | 13.901 | 15.321 |
| thuế 19,58% | −131 | −154 | −177 | −199 |
| C_ref 32 → 30,22 | +1.791 | +1.791 | +1.791 | +1.791 |
| KTPL + rò rỉ trên Q4/tồn kho | −1.235 | −1.401 | −1.566 | −1.732 |
| quỹ Lào giữ tới 2054 | −779 | −885 | −991 | −1.098 |
| khung thực | +1.362 | +1.694 | +2.025 | +2.356 |
| sản lượng 2035 → 2030 | −1.549 | −1.663 | −1.777 | −1.890 |
| **r3 tâm** | **10.521** | **11.863** | **13.206** | **14.548** |
Sửa C_ref (+1,8k) bù được phần lớn, không hết, KTPL + quỹ Lào (−2,0…−2,8k). Hai bước lớn còn lại ngược chiều nhau: khung thực (+) và sản lượng sớm hơn (−).

## 6. Đo vs đoán
- **ĐO:** selfcheck; thuế 9T 19,58%; KTPL 10,6% (2 năm); quỹ Lào 7,8%; khấu trừ tại nguồn 7,0/8,3%; C_cal 30,22/30,45; GVHB/t 9T; TDND 70 tỷ; sổ cứng 294,5 tỷ; BVPS 9.971; GPM peers; trung vị RSS3 danh nghĩa; TB 2023 1,576.
- **ĐOÁN:** mid (trục lớn), đường sản lượng (trục lớn nhất), g, r, π 3%, f, cách xử lý quỹ Lào, h, khả năng thu hồi TDND, trọng số 60/40, FCF 90%, quyền đất tới 2054, PPP.

## 7. Hàm ý (không phải khuyến nghị lệnh)
- Ở ba trên bốn mid, 14.400–14.700 **cao hơn FV tâm 9–40%**. Chỉ ở mid 2,18 (trung vị thực 10 năm) giá mới ngang FV, và ở đó lưới vẫn chỉ có 16–19% số ô ≥ giá.
- Không có cơ sở đảo quyết định giảm 50%.
- Vùng mua sau đáy: **chỉ ≤ 9.000** có biên ≥15%, và chỉ khi mid ≥ 2,075 (TDND 100% ⇒ chỉ mid 2,18). ≤10.000 chỉ đạt ở mid 2,18. ≤11.500 / ≤13.000 không đạt ở mid nào.
- PB ≤ 1 không phải sàn tài sản thực (#4 không đạt). Đây là input cho quy ước mua lại (a)/(c) Mike đang chờ. Ngưỡng nào áp dụng tuỳ việc user/Mike tin mid nào; r3 không chọn mid.

## 8. Đối chiếu SAU với skeptic (không chỉnh tham số)
- Đường đáy skeptic 9.334 / 10.424 / 11.514 / 12.604. Tái dựng thô bằng khung r2 + C_cal thuế Q3 + KTPL 10,5% + sản lượng 2035 cho **9.258 / 10.334 / 11.410 / 12.485**, lệch ≤1%. Bản r3 trên đường đáy thấp hơn (8.415 … 11.947), chủ yếu do quỹ Lào, sản lượng 2030 và thuế, bù một phần bằng khung thực.
- "Khoảng tin hơn" 13,0 / 14,3 / 15,5k của skeptic ở mid 1,97 / 2,075 / 2,18. r3 tâm: 11,9 / 13,2 / 14,5k, thấp hơn ~1,1k mỗi cột. Phần chênh nằm ở các khoản skeptic chưa tính: quỹ Lào, sản lượng 2030, thuế 9T.

Nguồn: `PREREG.md`, `model.py`, `out.txt` · `../dri_val_supply_adj_r2_20261027/` · `../dd_DRI_20261027/extract_q3_bctc.md` · `../dri_val_supply_adj_20261027/data/` (snapshot BQ) · `data/rubber_monthly.csv`, `data/macro_usdvnd.csv`.
