# GĐ3 — Khi nào dùng V2.4 thì an toàn hơn gửi tiết kiệm (job `Taylor_20261112_132954`, 12/11/2026)

Brief: `brief.md`. PREREG: `PREREG.md` (ghi 12/11 trước mọi phép thử; md5 `7c9bde3f7518ef5f9de857517e307703` trong `PREREG.md5`, đã phát lên bus ở heartbeat trước khi chạy).
Code: `analyze.py`; lệnh tái lập ở `REPRO_cmd.txt`; md5 các file ở `MD5SUMS`. Không wire, không merge, không đổi production, không đề xuất luật.

## 0. Kết luận

1. **Không tìm thấy điều kiện thời điểm nào bền.** 0/6 biến qua tiêu chí PREREG. Ở IS, mọi q-BH đều 0,945; ở OOS, mọi q-BH ≥ 0,977. N trials = 12. Ngưỡng hiệu ứng nhỏ nhất đo được (MDE) là chênh excess 12T 14–30pp ở IS và 57–110pp ở OOS. Mỗi era chỉ có khoảng 5–5,5 cửa sổ 12T không chồng nhau. Nghĩa là: với dữ liệu này, chỉ phát hiện được những chênh lệch rất lớn; câu đúng là "không phát hiện được", không phải "không tồn tại". Không vớt biến nào.
2. **Mặc định vô điều kiện (cửa sổ 12T):** engine P0 thắng tiết kiệm 12T ở **77,6%** ngày khởi đầu (CI90 theo tháng 65–88%); P30 thắng ở 79,8%. Khi thua, mức thua trung vị là −4,0pp (P0) và DD trung vị trong cửa sổ là −13,4%. Hai năm khởi đầu thua rõ: **2019** (P(thắng) 36%) và **2022** (20%). Đây là số backtest; theo CLAUDE.md, CAGR thật ≈ CAGR backtest − 1,5pp, và chưa trừ gap live−engine của GĐ1.
3. **Chính sách tham chiếu "về tiết kiệm khi DT5G ∈ {CRISIS, BEAR}"** (đã khai trước, không phải ứng viên):
   - CAGR 23,2% so với engine 23,4%, tức gần như không đổi.
   - MaxDD −12,6% so với −17,1%; Sharpe 2,07 so với 1,82.
   - Hơn 98% placebo tắt ngẫu nhiên cùng tần suất về CAGR, hơn 99% về DD.
   - Cách đọc: khớp với KB ("DT5G là bảo hiểm"). Hiệu quả là giảm DD, không tăng lợi nhuận.
   - Không được coi đây là phát hiện mới. Biến V1 (DT5G) **không qua** phép thử điều kiện: IS Δ +2,3pp, q 0,945. Lý do placebo thua là tắt ngẫu nhiên cắt cả tháng bull.
   - Chỉ có 28 lần đổi trạng thái trong 12,5 năm.
4. **Ngưỡng lãi (2019+, ngoài họ phép thử):** dep1m mức cao chỉ có 12 tháng / 2 episode. Tháng dep1m tăng 3T có P(thắng) 79% so với 80% khi không tăng (5 và 6 episode). ⇒ **Không có bằng chứng cho giả thuyết "mức hurdle tự nó là gate"** của plan §4. N quá nhỏ để bác.

## 1. Engine (self-check)

| Chân | Cấu hình | Ledger md5 | Self-check | CAGR / Sharpe / MaxDD |
|---|---|---|---|---|
| **P0** (chính cho điều kiện) | PARK_STATES=3:0 | `84f796bdedde8fefa02b37012e65bdde` | BAL 0 VND, LAG 0 VND, NAV identity 0 VND (`logs/exp_gap_p3_p0_liqz.log`) | 23,39% / 1,82 / −17,1% (tính lại từ DAILY: 23,389%, khớp số engine in ra) |
| **P30** (baseline + độ nhạy) | PARK_STATES=3:0.3 | `151bd903c7ef3f59ed7e9787e8aa4322` (ledger GĐ2B, chép sang `ledgers/`) | 0 VND (GĐ2B `engine_liqz.log`) | 24,77% / 1,79 / −17,6% |

Cấu hình chung cho cả hai chân:
- Code vá mergesort ở `live_gap_phase1b_20261112/sb_liq`, sandbox data đóng băng `bq_cache_asof20260729_postrestate`.
- LIQ_ZERO_BLOCK=lag, NAV 50B, namecap/yieldcombo, IDLE_CARRY_TIER=off, AUDIT_END 2026-06-19, BQ_CACHE_THREADS=1.
- Lệnh chạy: `run_leg.sh exp_gap_p3_p0_liqz <sb_liq> <sb_liq> LIQ_ZERO_BLOCK=lag BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0 IDLE_CARRY_TIER=off`.
- Ledger P0 có tên non-canonical, chứa `_exp_gap_p3_p0_liqz`.

Về park: cơ chế park live trước 06/08 khác engine, nên P0 là chân chính. Độ nhạy theo P30 nằm ở §3.

## 2. Bước 1 — baseline vô điều kiện (`step1_baseline.csv`, `step1_baseline_by_year.csv`)

Cách tính excess:
- excess = NAV(s+H)/NAV(s) − 1 − tiết kiệm 12T cộng dồn cùng kỳ.
- s là phiên kế tiếp sau ngày quan sát.
- Hurdle là `deposit_rate_vn`, 26 mốc neo hồi tố, chỉ dùng làm **nhãn ex-post**. CAGR tiết kiệm toàn kỳ đo được là 6,2%/năm (`step5_sizing.csv` w=0).

| P0 | H | era | P(thắng) | CI90 | excess trung vị | p10 | thua trung vị khi thua | DD trung vị khi thua | N cửa sổ độc lập* |
|---|---|---|---|---|---|---|---|---|---|
| | 3T | ALL | 61,9% | 52–72% | +2,3pp | −4,3 | −3,1pp | −4,6% | 49 |
| | 6T | ALL | 65,3% | 54–77% | +4,9pp | −5,9 | −4,0pp | −9,7% | 24 |
| | 12T | ALL | **77,6%** | 65–88% | +12,9pp | −4,6 | −4,0pp | −13,4% | 11,5 |
| | 12T | IS 2014–18 | 82,1% | 72–93% | +6,8pp | −1,8 | −2,0pp | −6,9% | 5 |
| | 12T | 2019 (đệm) | 36,0% | — | −3,9pp | −16,9 | −12,4pp | −14,9% | 1 |
| | 12T | OOS 2020+ | 81,2% | 58–97% | +21,9pp | −4,5 | −4,8pp | −15,5% | 5,5 |

\* số tháng/H. CI90 là block bootstrap theo tháng (khối 12). CI của ô 2019 suy biến vì chỉ có 1 khối.

- P30, 12T ALL: P(thắng) 79,8%, thua trung vị −5,8pp, DD khi thua −13,4%.
- P(thắng 12T) theo năm khởi đầu, chân P0: 2014 68% · 2015 97% · 2016 59% · 2017 98% · 2018 88% · **2019 36%** · 2020 100% · 2021 84% · **2022 20%** · 2023 100% · 2024 100% · 2025 (đến 06) 85%.
- Đọc: ở khung 3T, V2.4 thua tiết kiệm khoảng 38% thời gian. Một cửa sổ live 4 tháng thua tiết kiệm (GĐ0) **nằm trong phân phối bình thường**, không phải bất thường.

## 3. Bước 2 — điều kiện thời điểm (`step2_tests.csv`, `step2_class_table.csv`, `step2_monthly_panel.csv`)

Thiết kế:
- Mẫu lấy phiên đầu mỗi tháng: IS 60 tháng (2014–18), OOS 66 tháng (2020-01 → 2025-06).
- Δ = TB excess12 (lớp cao) − TB excess12 (lớp thấp).
- p tính bằng dịch vòng (2000 lần). Placebo hoán vị trong năm (500 lần). Bỏ từng năm.

Ngưỡng IS cố định: V3 breadth 0,525 / 0,620 · V5 LAG edge mean12 3,32 / 4,70 · V6 vol60 12,4% / 17,0%. V2 và V4 dùng mốc tự nhiên.

| Biến | IS Δ (pp) | p | q | MDE | OOS Δ (pp) | p | q | MDE | placebo IS/OOS | LOYO IS/OOS | QUA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 DT5G ({BULL,EX} − {CRISIS,BEAR}) | +2,3 | 0,83 | 0,945 | 30 | +28,8 | 0,28 | 0,982 | 58 | ✗/✓ | ✗/✓ | ✗ |
| V2 dd52 VNINDEX | +3,4 | 0,67 | 0,945 | 14 | +2,5 | 0,98 | 0,982 | 108 | ✗/✗ | ✗/✗ | ✗ |
| V3 breadth b200 (universe_pit) | +5,9 | 0,24 | 0,945 | 15 | +20,7 | 0,34 | 0,982 | 57 | ✗/✓ | ✗/✓ | ✗ |
| V4 SPX dd_1y | **không kiểm được** (IS: lớp ≤−15% có 0 tháng, SPX dd thấp nhất IS là −9,9%) | | | | +15,4 | 0,79 | 0,982 | 110 | —/✗ | —/✗ | ✗ |
| V5 LAG edge mean12 | +5,1 | 0,51 | 0,945 | 21 | **−30,2** | 0,51 | 0,982 | 91 | ✗/✗ | ✗/✗ | ✗ (đổi dấu) |
| V6 vol60 VNINDEX | +1,1 | 0,95 | 0,945 | 19 | +1,2 | 0,98 | 0,982 | 62 | ✗/✗ | ✗/✗ | ✗ |

N episode theo lớp (ví dụ, đầy đủ ở `step2_class_table.csv`):
- V1 OOS: CRISIS/BEAR 24 tháng / 7 episode, P(thắng) 58% (CI90 25–92%); NEUTRAL 25/11, 96%; BULL+ 17/6, 94%.
- V1 IS: CRISIS/BEAR 12/6, 92%.
- Dấu "CRISIS/BEAR xấu hơn" chỉ thấy ở OOS và không qua FDR. Ở IS, CRISIS/BEAR lại thắng 92%.

Độ nhạy (không đổi kết luận):
- P30 H12: 0 biến qua; V1 IS đảo dấu (−5,8pp).
- P0 H6: 0 biến qua. V1 OOS có p 0,044 nhưng q 0,264, và IS ngược dấu (−11,1pp).

Value Radar (chỉ mô tả, có bias neo hồi tố, `step2_radar_descriptive.csv`):
- Lớp ĐẮT thắng 96% ở IS (25 tháng / 2 episode) và 83% ở OOS (12/2).
- Lớp RẺ thắng 100% ở IS (6/3) và 85% ở OOS (33/5).
- Không đơn điệu và N nhỏ; không đọc như tín hiệu.

## 4. Bước 3 — chính sách (`step3_policy.csv`)

Không biến nào qua (1)–(3), nên **không có chính sách ứng viên**. Bảng dưới chỉ có tham chiếu đã khai trong PREREG:

| Chính sách | % ngày tắt | Số lần đổi | CAGR | Sharpe | MaxDD | Placebo CAGR p50 / p90 | Hạng CAGR so với placebo | Hạng DD |
|---|---|---|---|---|---|---|---|---|
| ENGINE P0 (DT5G bên trong) | 0 | 0 | 23,39% | 1,82 | −17,1% | — | — | — |
| Tiết kiệm khi DT5G ∈ {CRISIS,BEAR} | 23,5% | 28 | 23,2% | 2,07 | −12,6% | 18,7% / 21,6% | 98,2% | 99,4% |

- Chi phí: 0,1% NAV mỗi lần đổi. Phần thời gian ở tiết kiệm hưởng lãi 12T, mà chuỗi lãi này dùng mốc hồi tố.
- Phần tốt hơn nằm ở DD, không ở CAGR. Đây là một phiên bản thô hơn của chính DT5G (engine vốn đã giảm tỷ trọng ở BEAR).
- Không khuyến nghị; cần quant-skeptic trước khi coi là gì hơn "khớp KB".

## 5. Bước 4 — ngưỡng lãi 2019+ (`step4_rate.csv`)

Ngưỡng cố định lấy trung vị 2019-03→2020-12: dep1m 4,30%; spread ey_mkt−dep1m 2,37pp. Spread dùng PE từ `data/VNINDEX_pe_only.csv` (xem §7).

| Điều kiện | Lớp | Tháng | Episode | P(thắng 12T, hurdle 12T) | excess trung vị | P(thắng, nhãn dep1m) |
|---|---|---|---|---|---|---|
| dep1m mức | thấp / cao | 61 / 12 | 2 / 2 | 80% / 75% | +23,7 / +7,5pp | 87% / 75% |
| dep1m xu hướng 3T | không tăng / tăng | 59 / 14 | 6 / 5 | 80% / 79% | +21,9 / +18,9pp | 86% / 79% |
| spread ey−dep1m | thấp / cao | 10 / 63 | 3 / 3 | 70% / 81% | +9,9 / +20,6pp | 70% / 87% |

- Hướng của ba điều kiện khớp trực giác: lãi cao hoặc spread thấp thì kém hơn.
- Nhưng chỉ có 2–6 episode mỗi lớp, nên không đủ cơ sở cho một ngưỡng.

## 6. Bước 5 — sizing tham chiếu (`step5_sizing.csv`; không đề xuất luật)

Danh mục: w·V2.4 + (1−w)·tiết kiệm 12T, cân lại hằng ngày. Bootstrap theo khối 12 tháng, 1000 lần.

| w (P0) | CAGR | MaxDD | Bootstrap CAGR p5 | Bootstrap MaxDD p5 | P(thắng tiết kiệm 12T) | Thua trung vị khi thua |
|---|---|---|---|---|---|---|
| 0,3 | 11,2% | −4,2% | 8,3% | −5,3% | 78,5% | −1,1pp |
| 0,4 | 12,9% | −5,8% | 8,9% | −7,7% | 78,5% | −1,5pp |
| 0,5 | 14,7% | −7,5% | 9,6% | −10,3% | 78,3% | −2,0pp |
| 0,6 | 16,4% | −9,1% | 10,3% | −12,9% | 78,2% | −2,3pp |
| 0,8 | 19,9% | −12,9% | 11,6% | −18,4% | 77,9% | −3,1pp |
| 1,0 | 23,4% | −17,1% | 12,8% | −23,9% | 77,6% | −4,0pp |

- w lớn nhất có MaxDD-p5 bootstrap ≥ −10% / −15% / −20% là **0,4 / 0,6 / 0,8** (P30 cho cùng kết quả: 0,4 / 0,6 / 0,8).
- P(thắng 12T) gần như không phụ thuộc w. Thay đổi w chỉ co giãn **độ lớn** của lần thua, không đổi **xác suất** thua. Muốn giảm xác suất thua cần một điều kiện thời điểm, và §3 không tìm thấy.
- Dòng w=0 có p_win 0,597 là nhiễu so sánh bằng (excess ≈ 0), bỏ qua.

## 7. Lệch PREREG / giới hạn
- V4 ở IS không kiểm được, vì lớp cực có 0 tháng. Theo PREREG, như vậy là không qua.
- Bước 4: PREREG ghi lấy PE từ "`data/VNINDEX.csv` cột PE", nhưng file này chỉ có `VNINDEX_PE` (NULL trước 2016, theo memory gotcha). Đã dùng `data/VNINDEX_pe_only.csv` cột `Pe` (2014→2026-03-30). Các tháng 2019+ đều có PE.
- Breadth tải từ BQ bằng đúng SQL `macro_state_live._breadth_sql` (pit), ra file `breadth_pit_b200.csv`. Lấy giá trị phiên < t.
- Nhãn excess dùng hurdle 12T không-PIT. Chuỗi này chỉ làm nhãn; không có biến điều kiện nào dùng hurdle.
- Overlap cửa sổ 12T rất lớn, nên N độc lập thật chỉ khoảng 5 mỗi era. Mọi p và q đều mang giới hạn này.
- Engine chưa trừ gap thực thi live (GĐ1: −2..−4pp ở cửa sổ live) và chưa trừ "−1,5pp thực tế".
- Chưa qua quant-skeptic.
