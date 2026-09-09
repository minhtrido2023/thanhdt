# PHẦN 1 — Chẩn đoán hiệu suất book BAL (job `Taylor_20260909_100425`, 2026-09-09)

## 0. Tiền đề dispatch SAI — phải sửa trước khi đọc phần còn lại

Dispatch yêu cầu "chẩn đoán vì sao **BAL 2025 hiệu quả ÂM**". **BAL 2025 KHÔNG âm.**
Đo trên chân control tái lập pin R3 (xem §1): **BAL 2025 = +56,64%**, năm tốt nhất kể từ 2021,
**cao hơn cả LAG (+40,32%) lẫn VNINDEX (+40,87%)**.

Cửa sổ âm thật là **2026 YTD (đến 2026-06-19): BAL −2,36%** (LAG +0,57%, VNI +2,24%).
Toàn bộ chẩn đoán dưới đây nhắm vào 2026, không phải 2025.

## 1. Nguồn số + tái lập

| Hạng mục | Giá trị |
|---|---|
| Chuỗi NAV | `research/ccs_phase2_Taylor_20260906_153255/daily_ctrl_exp.csv` (chân **control** job CCS Phase 2) |
| Sổ lệnh | `research/ccs_phase0_Taylor_20260905_135003/trade_ledger_bal_lag_exp.csv` (2.056 dòng, 505 BAL / 1.551 LAG) |
| Config | pin R3: `NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19`, `universe_pit`, `LAG_ADV_BASIS=price`, threads=1, `$DNA_PYEXE` |
| Snapshot | `data/bq_cache_asof20260729_postrestate` |
| **Tái lập pin** | final NAV **1.178,0099B**, CAGR **28,8627%**, Sharpe 1,8999, MaxDD −17,785%, Calmar 1,6229 — **TRÙNG pin R3 2026-08-03** (28,86 / 1,90 / −17,8 / 1,62 / 1.178,01B) |
| Self-check | cash-flow identity max err 3,8e-05 VND (BAL) / 7,6e-05 (LAG); final-NAV identity err **0,0 VND** cả 2 sổ; `combination_replay_err = 0,0` |

`nav_bal_ref` / `nav_lag_ref` là **sổ tham chiếu 25B độc lập của từng book** (allocator chỉ tác động
qua `cap_bal`/`cap_lag`), nên `pct_change` của chúng là lợi suất THUẦN của book — không lẫn dòng vốn
điều chuyển.

## 2. Lợi suất theo năm — từng book

| Năm | BAL % | LAG % | Combined % | VNI % | đóng góp BAL (pp) | đóng góp LAG (pp) |
|---|---|---|---|---|---|---|
| 2014 | 9,49 | 73,22 | 49,14 | 8,15 | 4,03 | 45,14 |
| 2015 | 13,54 | 32,99 | 26,65 | 6,12 | 5,21 | 21,67 |
| 2016 | 24,83 | 4,05 | 14,45 | 14,82 | 12,42 | 2,08 |
| 2017 | 37,88 | 34,40 | 33,73 | 48,03 | 18,53 | 15,31 |
| 2018 | 27,86 | 24,08 | 28,85 | −9,32 | 15,37 | 13,62 |
| 2019 | 13,57 | 11,76 | 12,95 | 7,67 | 6,18 | 6,86 |
| 2020 | 63,55 | 3,20 | 28,15 | 14,87 | 20,79 | 7,63 |
| 2021 | 115,11 | 104,85 | 108,95 | 35,73 | 44,86 | 64,11 |
| 2022 | −12,49 | 1,30 | −7,43 | −32,78 | −3,98 | −3,17 |
| 2023 | 12,01 | 38,31 | 22,56 | 12,20 | 5,60 | 17,02 |
| 2024 | 26,80 | 26,55 | 25,60 | 12,11 | 10,54 | 15,09 |
| **2025** | **56,64** | 40,32 | 48,09 | 40,87 | **25,77** | 22,39 |
| **2026 (đến 06-19)** | **−2,36** | 0,57 | −0,91 | 2,24 | **−1,19** | 0,28 |

Chi tiết: `p1_peryear_book_returns.csv`.

## 3. Cấu trúc BAL — điều phải hiểu trước khi quy trách nhiệm

Đọc code thật (`pt_v23_audit_2014.py:682`, `signal_v11_sql.py`), **book BAL là HAI thứ ghép lại**:

1. **Sleeve động lượng** — `TIER_BAL = [MEGA, MOMENTUM, DEEP_VALUE_RECOVERY, RE_BACKLOG_BUY]`
   (`MOMENTUM_N`/`MOMENTUM_S` đã đóng 2026-07-12). Cả 4 tier **chỉ mở lệnh được khi DT5G ∈ {4,5}**
   (RE_BACKLOG_BUY: {3,4,5}), và state 5 còn bị `AVOID_exbull` chặn MEGA/MOMENTUM. Max 12 vị thế,
   giữ **45 phiên cứng**, stop −20%.
2. **Rổ đỗ xe custom30V** — chạy trong NEUTRAL (`PARK_STATES="3:0.7"`), nằm ở `bal_etf_ref`.

Hệ quả đo được: BAL theo state (toàn kỳ 2014-2026, annualized)

| DT5G state | phiên | BAL ann.% | LAG ann.% | VNI ann.% | tỷ trọng CỔ PHIẾU TB của BAL |
|---|---|---|---|---|---|
| 1 CRISIS | 489 | −0,10 | 11,39 | −8,39 | 17,8% |
| 2 BEAR | 241 | 0,51 | 0,60 | −21,44 | 15,0% |
| 3 NEUTRAL | 1.895 | 32,54 | 34,39 | 16,77 | **21,7%** |
| 4 BULL | 422 | **60,10** | 39,92 | 27,21 | **92,2%** |
| 5 EX-BULL | 60 | 68,83 | 97,47 | 63,90 | 94,8% |

⇒ Lợi suất BAL trong NEUTRAL phần lớn **KHÔNG phải của tín hiệu momentum** (chỉ 21,7% vốn nằm ở cổ
phiếu) mà của **rổ parking custom30V**. Khi người đọc nói "BAL yếu", cần tách rõ đang nói về sleeve
momentum hay về cả book.

## 4. N THẬT của sleeve momentum BAL = **10 sự kiện**, không phải 505 dòng sổ

Vì lệnh chỉ mở được trong cửa sổ DT5G ∈ {4,5}, và cửa sổ đó ngắn + lệnh dồn vào vài phiên đầu,
mọi vị thế trong một cửa sổ **là cùng một cược regime**, không độc lập.

| Cửa sổ BULL/EX-BULL | phiên | n lệnh khớp | ret TB | hit | đóng góp (B) |
|---|---|---|---|---|---|
| 2017-12-26 → 2018-02-26 | 39 | 12 | +9,1% | 58% | +5,6 |
| 2018-03-22 → 2018-05-08 | 31 | 12 | **−11,7%** | 17% | −7,4 |
| 2020-10-06 → 2021-02-18 | 92 | 26 | +23,4% | 88% | +52,3 |
| 2021-03-05 → 2021-07-23 | 98 | 36 | +11,1% | 58% | +54,4 |
| 2021-08-23 → 2021-09-09 | 12 | 8 | +21,4% | 100% | +14,2 |
| 2021-10-26 → 2021-12-24 | 44 | 18 | +2,4% | 44% | +2,4 |
| 2024-01-24 → 2024-05-13 | 70 | 32 | +10,7% | 81% | +51,9 |
| 2025-03-07 → 2025-05-16 | 47 | 19 | +3,4% | 42% | +21,2 |
| 2025-08-12 → 2025-10-03 | 37 | 13 | −0,7% | 46% | +15,3 |
| **2026-01-28 → 2026-02-12** | **12** | **14** | **−4,8%** | **29%** | **−32,9** |

**12,5 năm = 10 cửa sổ.** Bất kỳ tuyên bố "momentum đã suy thoái" nào dựa vào 2025-2026 đều đang
đứng trên **2 sự kiện**. (`p1_bull_windows.csv`)

## 5. Chuyện gì xảy ra năm 2026 — cơ chế, không phải phỏng đoán

Toàn bộ 14 lệnh BAL năm 2026 vào trong **11 phiên** (2026-01-29 → 2026-02-09), cửa sổ BULL chỉ dài
**12 phiên** — ngắn nhất trong 10 cửa sổ trừ 2021-08. Hold cứng 45-46 phiên ⇒ **toàn bộ exit dồn vào
2026-04-10 → 04-21**.

| Tháng 2026 | BAL % | VNI % | % vốn BAL ở cổ phiếu | DT5G |
|---|---|---|---|---|
| 01 | +4,96 | +2,50 | 6,2% | 3→4 |
| 02 | +3,97 | +2,80 | **94,1%** | 4→3 |
| 03 | **−9,05** | −10,95 | 88,9% | 3 |
| 04 | **−0,76** | **+10,73** | 35,7% | 3 |
| 05 | +1,02 | +0,51 | 10,2% | 3 |
| 06 | −1,87 | −2,09 | 9,1% | 3 |

Chuỗi nhân quả: DT5G bật BULL 28/01 → BAL nạp gần đầy trong 11 phiên → DT5G tắt BULL 12/02 →
crash tháng 3 (BAL −9,05%, **không tệ hơn VNI −10,95%** — chọn mã KHÔNG phải thủ phạm) → hold cứng
buộc bán ra 10-21/04 **đúng lúc thị trường bật** → state đã về 3 nên **không có tier nào mở lệnh
lại được**, BAL đứng ngoài toàn bộ nhịp +10,73% tháng 4.

**Chi phí đo được của riêng nhịp bỏ lỡ tháng 4: ~11,5pp so với VNI trong MỘT tháng.**

Chỉ 2 lệnh dính STOP −20% (VCB −17,8%, KBC −23,1%) = −22,9B; phần còn lại thua vì mua ở đỉnh cửa sổ
và bị buộc bán ở đáy.

## 6. Phân định 3 giả thuyết

**(a) Alpha decay của momentum — KHÔNG chứng minh được, dữ liệu không đủ để kết luận.**
Ở mức *episode* (gộp các lệnh cùng ngày vào, xem `p1_bal_episodes.csv`):
- MWU 2025-26 (n=27 episode) vs 2017-24 (n=118): **p = 0,105** — không đạt.
- 2026 riêng: n=8 episode, mean −4,1%, sign test **p = 0,363**.
- Spearman(năm, ret TB episode) 2017→2026: rho=0,018, **p = 0,960** — **không có xu hướng nào**.

Có hai chỉ báo *gợi ý* (không phải bằng chứng): (i) tỷ lệ thắng theo năm 2020 74% → 2021 58% →
2024 66% → 2025 47% → 2026 29%; (ii) **ey (1/PE) trung vị lúc vào lệnh trôi từ 0,15 (2019) →
0,076 (2021) → 0,069 (2024) → 0,076 (2025) → 0,059 (2026)** — tức PE lúc mua từ ~6,6 lên ~17,0.
BAL đang mua ngày càng đắt. Cần theo dõi, chưa đủ tư cách kết luận.

**(b) Regime mismatch — ĐÚNG, và là nguyên nhân chính của 2026.** §5 là bằng chứng cơ học:
BAL bị KHOÁ ngoài thị trường 89% số phiên 2026 (100/112 phiên ở state 3), và nhịp tăng lớn nhất
của năm rơi trọn vào vùng bị khoá. Đây là **thuộc tính thiết kế** (gate `state5 IN (4,5)`), không
phải hỏng hóc.

**(c) Vài mã cá biệt kéo cả book — KHÔNG.** 2026 lỗ trải đều: 14/20 lệnh âm, mã tệ nhất (KBC)
chỉ chiếm −12,9B/−38,1B = 34%. Ngược lại **2025 mới là năm phụ thuộc đuôi**: median ret của lệnh
2025 là **−0,4%** (âm!), hit 52%, nhưng top-3 mã (SJS +74,9%, GEX, VIC) đóng **54%** tổng lợi
nhuận. **Lệnh BAL điển hình năm 2025 đã là lệnh thua — cả năm dương nhờ đuôi phải.** Năm 2026
đuôi phải không xuất hiện (mã tốt nhất GAS +78,6% nhưng là lệnh 2025 chốt sang 2026).

⚠️ Ghi chú tự phản biện: `ABANDONED_REFUND` (191/505 dòng BAL) là lệnh đặt rồi huỷ, đóng góp
+0,404B tổng ⇒ đã **loại khỏi mọi thống kê hit/mean/median** ở trên. Tính cả vào sẽ thổi phồng N
lên gấp đôi một cách giả tạo.

## 7. Đối chiếu LIVE — âm do chiến lược hay do thực thi?

| Account | Cửa sổ | NAV | VNINDEX cùng kỳ | Chênh |
|---|---|---|---|---|
| SpaceX | 2026-07-02 → 09-08 (41 phiên) | **−1,29%** | 1.866,35 → 1.830,44 = **−1,92%** | **+0,63pp** |
| ZaloPay | 2026-07-07 → 09-08 (39 phiên) | **−0,89%** | 1.848,25 → 1.830,44 = **−0,96%** | **+0,07pp** |

Nguồn: `data/execution_logs/nav_history_{SpaceX,ZaloPay}.csv` (pipeline §6), VNINDEX từ
`tav2_bq.ticker` (lịch sử, không phải same-day).

**Không có bằng chứng lỗi thực thi.** Cả 2 account nhỉnh hơn index trong một thị trường đi ngang/giảm.
Nhưng **N = 2 tháng, và cả 2 tháng đều ở NEUTRAL** ⇒ sleeve momentum BAL gần như KHÔNG chạy trong
cửa sổ live; cái đang được đo là parking + LAG, **không phải BAL momentum**. Không thể tách đóng góp
BAL từ 41 dòng NAV. Kết luận đúng: *live chưa hề kiểm định được sleeve BAL.*

## 8. Kết luận Phần 1

1. Tiền đề "BAL 2025 âm" **sai**; 2025 là +56,64%. Cửa sổ âm là 2026 YTD −2,36%.
2. Nguyên nhân 2026 = **(b) regime**: một cửa sổ BULL 12 phiên + hold cứng 45 phiên ⇒ mua đỉnh,
   bán đáy, rồi bị gate `state ∈ {4,5}` khoá ngoài nhịp hồi +10,73% tháng 4.
3. **(a) alpha decay: chưa chứng minh được** (p=0,105 / 0,363 / 0,960). Hai dấu hiệu cần theo dõi:
   hit-rate trôi xuống và **ey lúc vào lệnh trôi từ 0,15 → 0,059**.
4. **(c) mã cá biệt: bác bỏ cho 2026**, nhưng phát hiện ngược: **2025 dương nhờ đuôi phải, median
   lệnh đã âm**.
5. Chọn mã KHÔNG phải thủ phạm tháng 3/2026 (BAL −9,05% vs VNI −10,95%). Thủ phạm là **timing vào,
   cơ chế thoát cứng, và việc không có đường tái nhập trong NEUTRAL**.
6. **N thật của sleeve BAL = 10 cửa sổ regime trong 12,5 năm.** Mọi đề xuất sửa BAL phải được đánh
   giá ở mức N này, không phải ở mức 505 dòng sổ.
