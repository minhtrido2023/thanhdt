# Rating 8L G1 — B1 tích luỹ forward + B2 backtest có phí (EXPLORATORY · PAPER-ONLY)

Job `Taylor_20261020_055002` · 2026-10-20. Kiểm chứng tiếp, KHÔNG phải wire: không đề xuất đổi gate/luật, KHÔNG ghi
`results_registry.md`, KHÔNG pin. Mọi số dưới đây là EXPLORATORY.

PREREG: `PREREG_FORWARD.md` md5 `4ad20803a74b046af74a9b128085019c`, `PREREG_BT.md` md5 `831ae90e77359e391e14137d4b87682f`,
cùng commit `2991ee58d` (2026-10-20 12:56:03 +0700), TRƯỚC lần chạy tracker đầu tiên và trước mọi chân backtest.

## Kết luận
| Phần | Kết quả |
|---|---|
| **B2 nhãn (PREREG_BT §6, V1)** | **"không phân biệt được (thiếu N)"** — R3 + 5% sleeve: ΔSharpe +0,022 (pin0%) / +0,023 (pin1M), CI95 [−0,024; +0,068] / [−0,025; +0,070] chứa 0. Dương ở cả IS và OOS, DSR ≥ 0,95, nhưng cận dưới CI < 0. |
| **B1** | Tracker + PREREG đã khoá; N_min = **3.398** sự kiện G1 (δ*=1%, power 80%, α=0,05 hai phía) ⇒ khoảng **35-40 năm** (ước lượng). Forward chỉ mô tả được, cùng một quy tắc futility. |
| **⚠️ Phát hiện phụ — dữ liệu vòng 2 hỏng** | raw giá của vòng 1/2 (kéo `tav2_bq.ticker` lúc 10:48) chỉ có 657/770 mã universe (thiếu HPG, HQC, HBC…). Chạy lại ĐÚNG code vòng 2 trên giá pin (770/770): G1 **đạt cả (a)-(d)** của PREREG vòng 2. Trượt (b) là do bảng giá hỏng. Ngưỡng (b) chỉ qua sát nút: IS p 0,098 / 0,089. Cần Mike/quant-skeptic xét lại verdict vòng 2 (§3). |

## 1. Chân control (PREREG_BT §2)
- **C0 tái lập**: `event_study_v2_frozen.py` (md5 `a857d81b…`) trên raw vòng 2 ⇒ md5 `out_v2_criteria/events/tests` **trùng
  khít** `90f6f340` / `079db2ae` / `e291fc36`. G1 [2,40] δ = +1,55%. ✅
- **C1 vintage** (trục duy nhất đổi = px/vol từ `tav2_pin.ticker_pin_202610`, snapshotTime 2026-10-01T15:00:12Z,
  `raw/px_pin.parquet` md5 `9e4e12ee321d4cb353bd08fbe713b07e`, 770 mã): `ctl1/c1/out_v2_stdout.txt`, criteria md5 `869cf601…`.

| G1 | N | δ | CI95 | q_BH | IS 2014-19 | OOS 2020+ | (a)(b)(c)(d) |
|---|---|---|---|---|---|---|---|
| [2,20] vòng 2 (657 mã) | 938 | +1,06% | [+0,35; +1,78] | 0,032 | +0,75% p 0,18 | +1,22% p 0,006 | ✅❌✅✅ |
| [2,20] **pin (770 mã)** | 1.083 | **+1,07%** | [+0,37; +1,77] | 0,008 | +0,96% p **0,098** (N 361) | +1,12% p 0,006 | ✅✅✅✅ |
| [2,40] vòng 2 | 938 | +1,55% | [+0,22; +2,80] | 0,044 | +1,67% p 0,19 | +1,49% p 0,050 | ✅❌✅✅ |
| [2,40] **pin** | 1.083 | **+1,62%** | [+0,38; +2,82] | 0,014 | +2,10% p **0,089** | +1,38% p 0,071 | ✅✅✅✅ |

G2 trên pin: δ −0,14% / −0,09%, q 0,82 ⇒ vẫn "không có". Bản không khớp SUE: G1 +1,29% / +1,84% (q 0,001). Đọc: dữ liệu
đầy đủ thì δ G1 gần như không đổi (+1,06→+1,07, +1,55→+1,62), nhưng N tăng 15% (938→1.083), đủ đẩy nửa IS qua p<0,10.
Biên quá mỏng (~0,01 p): seed bootstrap khác có thể lật kết quả (quant-skeptic dùng seed 7 ở vòng 2 thì p lệch 0,02-0,03).

## 2. B1 — tracker forward
- Thiết kế đã khoá (`PREREG_FORWARD.md`): sự kiện eff > 2026-07-31; G1 − G0* khớp quý × mom5 × SUE5 × bank; B3 loại chính
  mã; cửa sổ quyết định DUY NHẤT [2,40]; code `event_study_v2_frozen.py`; luật loại ca của vòng 2.
- **N_min** = DEFF · ((z₀,₉₇₅ + z₀,₈₀) · σ / δ*)² = 1,355 · ((1,960 + 0,842) · 0,1787 / 0,010)² = **3.398**. σ_iid = 0,1787
  và DEFF = 938/692 đều đo trên `out_v2_events.csv` (raw đã hỏng; con số này đã khoá, không tính lại). Tốc độ tích luỹ
  khoảng 90 G1 có ô khớp mỗi năm, nên cần khoảng 35-40 năm (ước lượng).
  Verdict "có" chỉ được phép khi N ≥ N_min. Futility: N ≥ 300 và cận trên CI95 < 0 ⇒ dừng. Còn lại = "thiếu N".
- Code: nhánh `feat/rating-8l-forward-tracker-20261020` @`68b34b377`, wt `/home/trido/thanhdt/wt-Taylor_20261020_055002`:
  `bin/rating_8l_forward_tracker.py`, `bin/rating_8l_forward_tracker_selfcheck.py`, thêm mục `rating_8l_g1_forward_oos` vào
  `kb/paper_programs_registry.json` (end/review 2027-10-20, `reporting:false`; daily report render đúng ở khối "Đã chuyển khỏi
  báo cáo ngày"). **KHÔNG merge.**
- Selfcheck: 28 assertion PASS dưới `env -u TZ`, `TZ=America/New_York`, `TZ=Pacific/Kiritimati`; mutation 11/11 bị bắt
  (nhóm G1, mốc eff, 2 ngưỡng cổng, B3 loại chính mã, biên 42 phiên, fail-closed BLOCKED, append-only, x_definite, neo ICT,
  RD NULL).
- Lần chạy đầu (thật, ghi file): 295 sự kiện eff 2026-08-03→10-14 (G0 258 · G1 11 · G2 11 · G3 15; loại ca 111) →
  `data/rating_8l_forward_events.csv` md5 `c136fb2a271605b3ea7a1824fe43d659`. CAR: 0/295 (chưa sự kiện nào đủ 42 phiên trên
  pin 10-01). Cổng giá: live `tav2_bq.ticker` **FAIL** (1.051 mã < 1.200; phủ universe 0,904) → pin `ticker_pin_202610` OK
  (1.294; phủ 1,000).
- **Đề xuất cron (CHƯA cài; Mike quyết sau review):**
  `15 11 * * * cd /home/trido/thanhdt/WorkingClaude && . ./wc_env.sh && flock -n mike/state/rating_8l_forward_tracker.cron.lock timeout 900 $DNA_PYEXE mike/bin/rating_8l_forward_tracker.py >> /home/trido/thanhdt/WorkingClaude/mike/logs/rating_8l_forward_tracker.log 2>&1` (UTC 11:15 = 18:15 ICT; `.` thay `source` vì cron dùng dash; log đường dẫn tuyệt đối)
  (18:15 ICT, sau `fa_ratings_8l` 17:30; tracker chỉ đọc BQ; trùng lần chạy thì idempotent theo khoá ticker+quarter).
- Sai lệch so với PREREG_FORWARD:
  1. §2 ghi "số mã có giá tại phiên mới nhất ≥ 1.200". Đo thật thì số mã mỗi phiên dao động 774-1.259 ngay trên pin lành
     (86 phiên 06-10/2026), nên ngưỡng này luôn trượt. Đã đổi thành: số mã TOÀN bảng ≥ 1.200, và tỉ lệ mã in_universe có ≥1
     giá trong 30 ngày cuối ≥ 0,98. Đổi TRƯỚC khi có bất kỳ CAR nào. Không đụng thiết kế thống kê.
  2. `first_seen` của 295 sự kiện lô đầu = 2026-10-20, nên lô này không PIT tuyệt đối (rating có thể đã restate giữa eff và
     10-20). Từ mùa Q3/2026, nếu cron chạy hằng ngày thì first_seen ≈ eff.

## 3. B2 — backtest có phí (sleeve V1 = mua mọi G1, giữ 40 phiên)
Đầu vào: sự kiện từ raw vòng 2 (fa/tf/univ), giá pin; 1.193 sự kiện G1 hợp lệ (3.455 trong cửa sổ eff; trừ luật loại ca,
không giá, không in_universe phiên 0). Không áp lọc nhìn sau phiên 0. Quy ước: ramp 3 phiên ở close +1..+3, 10%/mã, ADV =
trung vị Price×Volume (giá thô) 60 phiên, ≤20% ADV/tranche, TC 0,1%/chiều, không slippage/thuế (CAGR thật ≈ −1,5%), tiền
bán dùng ngay trong phiên (bỏ qua T+2). **Self-check 0 VND**: 7/7 chân, |cash dựng lại từ TX + lãi − cash| ≤ 0,0006 VND,
|NAV dựng lại từ vị thế − NAV| ≤ 0,0002 VND (`out_bt_stdout.txt`).

**Sleeve một mình, vốn 2,5 tỷ** (`out_eval_metrics.csv`; CI = CI95 bootstrap khối quý của lợi suất năm hoá trung bình ngày):

| Biến thể | pin0% CAGR / Sharpe / MaxDD | pin1M CAGR / Sharpe / MaxDD | IS CAGR (pin0/pin1M) | OOS CAGR (pin0/pin1M) |
|---|---|---|---|---|
| **V1 H40 (chính)** | 23,66% / 1,27 / −51,3% | 25,46% / 1,35 / −50,2% | 17,31% / 19,79% | 29,11% / 30,31% |
| V2 H20 (mô tả) | 17,70% / 1,38 / −35,1% | 20,84% / 1,60 / −34,2% | 12,50% / 15,78% | 22,12% / 25,15% |
| V3 H40 ADV≥5B (mô tả) | 16,12% / 0,95 / −52,7% | 18,35% / 1,06 / −52,3% | 5,46% / 8,19% | 25,62% / 27,35% |

- DSR V1 (N_trials=3): 0,9999 ở cả hai đầu. Nhưng DSR ở đây đo Sharpe TUYỆT ĐỐI của một sleeve long-only, gồm cả beta
  small-cap, nên gần như không có thông tin.
- Mô tả (không thuộc verdict, `describe_bench.py`): rổ EW mọi mã in_universe cùng kỳ có CAGR 8,73%, Sharpe 0,55, DD −59,6%.
  Sleeve V1 pin0% có beta 0,66 so với rổ này, corr 0,67. MaxDD −51% của sleeve rơi vào OOS (2022).
- **Tương quan** sleeve V1 (2014-07-02→2026-06-19, N = 2.989 ngày):

  | | pin0% | pin1M |
  |---|---|---|
  | với book LAG, theo ngày | 0,43 | 0,43 |
  | với book LAG, theo tháng | 0,53 | 0,52 |
  | với R3, theo ngày | 0,53 | 0,53 |
  | với R3, theo tháng | 0,65 | 0,65 |

- **Đóng góp biên — R3 + 5% sleeve** (tỉ trọng khai trước, cân lại hằng ngày, không tính phí cân lại):

| Đầu dải | Kỳ | R3 CAGR / Sharpe / DD | R3+5% CAGR / Sharpe / DD | ΔSharpe [CI95] p |
|---|---|---|---|---|
| pin0% (SÀN) | FULL | 23,07% / 1,837 / −14,64% | 23,22% / 1,859 / −15,24% | +0,022 [−0,024; +0,068] 0,33 |
| | IS | 19,07% / 1,716 | 19,02% / 1,754 | +0,037 [−0,011; +0,094] 0,14 |
| | OOS | 26,60% / 1,935 | 26,93% / 1,950 | +0,014 [−0,053; +0,084] 0,63 |
| pin1M (TRẦN) | FULL | 25,32% / 2,008 / −14,03% | 25,46% / 2,030 / −13,96% | +0,023 [−0,025; +0,070] 0,34 |
| | IS | 21,36% / 1,904 | 21,33% / 1,946 | +0,042 [−0,006; +0,101] 0,09 |
| | OOS | 28,81% / 2,096 | 29,12% / 2,107 | +0,012 [−0,057; +0,085] 0,70 |

(R3 trên chuỗi ngày chồng lấn 2014-07-02→2026-06-19 nên CAGR khác số pin 23,37% / 25,71%, vốn tính từ 2014-01-02.)

- **Công suất** (`out_bt_capacity.csv`):

  | | 2,5 tỷ | 50 tỷ |
  |---|---|---|
  | Số mã giữ / ngày (TB · p90 · max) | 10,3 · 21 · 29 | 7,7 · 17 · 22 |
  | Vốn dùng trung bình | 60% | 45% |
  | Sự kiện bị trần ADV cắt nhỏ | 40% | 80% |
  | Tranche bỏ (tiền < 0,5% NAV hoặc không giá) | 51% | 55% |

  Ở 2,5 tỷ mà vẫn bỏ 51% tranche là vì các sự kiện G1 dồn cục theo mùa BCTC. 8 sự kiện có ADV = 0 bị bỏ. 700/1.193 sự kiện
  (59%) có ADV < 5 tỷ.

## 4. Đọc kết quả (không phải đề xuất)
- Sleeve standalone có lãi lớn sau phí, nhưng phần lớn có thể là beta/size. Thêm vào R3 ở 5%, nó cải thiện Sharpe một chút
  ở cả hai nửa. Không phân biệt được với 0 (CI chứa 0), và MaxDD xấu thêm 0,6pp ở đầu sàn.
- Tương quan với LAG 0,43-0,53: phần drift trùng với PEAD (vòng 2 đã thấy SUE giải thích khoảng 17% δ). Đây không phải
  nguồn edge độc lập.
- Không có kết quả nào ở đây cho phép đổi gate/luật. Việc mở: xét lại verdict vòng 2 trên dữ liệu đầy đủ (§1).

## Tái lập
```bash
cd mike/agents/Taylor/research/rating_8l_forward_bt_20261020
$DNA_PYEXE pull_pin.py                                  # → raw/px_pin.parquet (md5 9e4e12ee…)
(cd ctl/c0 && OMP_NUM_THREADS=1 $DNA_PYEXE ../../event_study_v2_frozen.py)      # C0 (symlink raw vòng 2)
(cd ctl1/c1 && OMP_NUM_THREADS=1 $DNA_PYEXE ../../event_study_v2_frozen.py)     # C1 (px/vol pin)
OMP_NUM_THREADS=1 $DNA_PYEXE bt_sleeve.py > out_bt_stdout.txt
OMP_NUM_THREADS=1 $DNA_PYEXE evaluate_bt.py > out_eval_stdout.txt
$DNA_PYEXE describe_bench.py > out_bench_stdout.txt
```
Ledger R3: `python3 mike/bin/pin_ledger.py extract 4707bcbe --out raw/r3_pin0.csv` (md5 khớp manifest), tương tự
`bcd0469f` → `raw/r3_pin1m.csv`. md5 (8 ký tự): bt_sleeve.py `b9ed16f5`, evaluate_bt.py `8f8c964f`, describe_bench.py
`5b5e08be`, pull_pin.py `045ce3fe`, out_eval_metrics.csv `d81eefd4`, out_bt_capacity.csv `17b33e2d`.
