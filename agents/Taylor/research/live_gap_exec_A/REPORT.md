# Luồng A — engine: vá mergesort + LIQ_ZERO_BLOCK mặc định `lag` + pin ladder L0→L4

Job `Taylor_20261112_162004` (gốc `_151832`, resume ×3 do usage-limit). Brief: `brief.md`. User duyệt CHẠY 12/11 22:1x ICT.
⚠️ PAPER + REGISTRY. **KHÔNG merge, KHÔNG đổi production / cron / `trading_rules.json` / neo sizing −25,2%.**
Mọi số dưới đây đo trong job này (lệnh + log ở `logs/`, ledger ở `ledgers/`); chưa qua quant-skeptic.

## 1. Kết luận

1. **Nhánh sẵn sàng merge**: `feat/live-gap-exec-A-20261112` (worktree `/home/trido/thanhdt/wt-livegapA-1112`, base `a8eb74402`), 2 commit, 2 file, +16/−4:
   - `dbfd9a4af` A2 — `LIQ_ZERO_BLOCK` mặc định `""`→`lag`; knob lùi `LIQ_ZERO_BLOCK=off`; trục LIQ LUÔN vào tên file (`_liqzblag`/`_liqzboff`); không khai ⇒ in cảnh báo to 4 dòng `!!!`.
   - `efdb282bd` A1 — cherry-pick đúng `5512bfe3d`: `regime_size_overlay.py:43` `sort_values(["time","ticker"], kind="mergesort")`, `:93` `sort_values("time", kind="mergesort")`. KHÔNG kèm hook PARK_SCHEDULE/TIEBREAK_SEED.
2. **Knob lùi byte-identical**: code SAU A2 + `LIQ_ZERO_BLOCK=off` + data vintage 10-29 ⇒ `4707bcbe` (anchor sexies, park 0,3) và `537e349b` / `a6ba34d8` (pin park0 sàn/trần 10-08). Tức đổi mặc định không đụng số pin cũ khi khai `off`.
3. **Determinism (A1 selfcheck)**: ledger AUDIT_END 06-19 vs 07-29 trên 3.107 phiên chung —
   mergesort **0 phiên lệch** (max |ΔNAV| 0 VND, 0/149 tháng); quicksort (code cũ) **1.986 phiên lệch** từ 2018-07-06, max 26,55 tỷ, 88/149 tháng, 3 tháng đảo dấu. Tốt hơn ngưỡng brief (≤4 phiên).
4. **Dải mới (L3 = L4, đầu ladder)**: **pin0% 23,39% (sàn) … pin1M 26,77% (trần; trung bình 10 seed tie-break 26,30%, sd 0,26pp)**; MaxDD −17,1% / −14,8%; **bootstrap DD 5th −27,6% (sàn) / −25,0% (trần)**. Neo sizing −25,2% hiện hành KHÔNG đổi — số đo mới (sàn −27,6%) sâu hơn neo 2,4pp ⇒ để user quyết riêng.
5. **Trục gây biến động lớn nhất là LIQ_ZERO_BLOCK=lag**: CAGR +1,13pp (sàn) / +1,24pp (trần) nhưng **dịch IS→OOS mạnh** (IS 20,08→16,85%, OOS 24,33→29,80% ở sàn) và **DD 5th sâu thêm 4,1pp** (−23,6→−27,7%). Đây là fidelity-to-live, KHÔNG phải edge — không đọc +1,1pp là lợi nhuận.
6. **L4 (LAG data current 12/11) trùng BYTE L3 (adj v2)** — Δ = 0 chính xác, đã giải thích (§4). BQ cache current CHƯA ĐO (§6).

## 2. Ladder (FULL 2014-01-02→2026-06-19, 12,46 năm, NAV 50B, park 0, AUDIT_END 06-19, threads=1)

Số từ `logs/leg_metrics.log` (đầu ra engine/`extract`), bootstrap circular L=21 B=4000 seed 12345 (`logs/bootstrap.log`; L0 tái lập đúng số registry 10-08: 14,9/−23,9 và 18,0/−21,5).

| Bước (trục đổi) | đầu | CAGR | Sharpe | MaxDD | Calmar | IS / OOS CAGR | Boot CAGR5 | **Boot DD5** | P(DD<−30%) | md5 |
|---|---|---|---|---|---|---|---|---|---|---|
| L0 pin hiện hành (park0) | pin0% | 22,12% | 1,92 | −16,2% | 1,36 | 20,06 / 23,98 | 14,9% | −23,9% | 0,7% | `537e349b` |
| | pin1M | 25,42% | 2,16 | −13,9% | 1,84 | 23,21 / 27,43 | 18,0% | −21,5% | 0,1% | `a6ba34d8` |
| L1 +mergesort | pin0% | 22,31% | 1,94 | −16,2% | 1,37 | 20,08 / 24,33 | 15,1% | −23,6% | 0,5% | `2f7739b5` |
| | pin1M | 25,87% | 2,21 | −13,7% | 1,89 | 23,42 / 28,11 | 18,5% | −20,6% | 0,1% | `fe398133` |
| L2 +LIQ_ZERO_BLOCK=lag | pin0% | 23,44% | 1,82 | −16,3% | 1,44 | 16,85 / 29,80 | 15,2% | −27,7% | 2,5% | `5ae929c6` |
| | pin1M | 27,11% | 2,06 | −15,2% | 1,79 | 20,12 / 33,88 | 18,6% | −25,2% | 0,8% | `52b39597` |
| L3 +cache LAG adj v2 | pin0% | **23,39%** | 1,81 | −17,1% | 1,37 | 16,77 / 29,77 | 15,1% | **−27,6%** | 2,5% | `84f796bd` |
| | pin1M | **26,77%** | 2,04 | −14,8% | 1,81 | 20,15 / 33,16 | 18,2% | **−25,0%** | 0,8% | `35c8968f` |
| L4 +LAG data current 12/11 | pin0% | = L3 | | | | | | | | `84f796bd` (trùng byte) |
| | pin1M | = L3 | | | | | | | | `35c8968f` (trùng byte) |

Δ mỗi bước (pin0% / pin1M): L1 +0,19 / +0,45pp · L2 +1,13 / +1,24pp · L3 −0,05 / −0,34pp · L4 0 / 0.

`pin_ledger.py compare` 7 cặp, **tất cả rc=0 "khác ĐÚNG 1 trục"** (`logs/compare.log`): L0→L1 ENGINE_SORT, L1→L2 LIQ_ZERO_BLOCK, L2→L3 LAG_DATA (×2 đầu dải) + L1_off→L1_1m IDLE_CARRY_TIER. L3→L4 không compare được (md5 trùng ⇒ kho từ chối add lần 2 — đúng thiết kế §8c).

### Sàn nhiễu tie-break (≥10 seed, chỉ để ĐO — hook TIEBREAK_SEED ở code research, KHÔNG thuộc nhánh merge)

Cấu hình L4 + `TIEBREAK_SEED=1..10` (mergesort + hoán vị ngẫu nhiên thứ tự trong ngày), 20/20 chân selfcheck 0 VND. Nguồn: `logs/tb_stats.log` (`tb_stats.py`; Sharpe log-return, lệch ~0,04 so với Sharpe engine).

| đầu | TB mean CAGR | **sd CAGR** | min…max CAGR | sd MaxDD | min…max MaxDD | sd Sharpe | L4 (không seed) |
|---|---|---|---|---|---|---|---|
| pin0% | 23,39% | **0,17pp** | 23,02…23,63 | 0,004pp | −17,07…−17,06 | 0,014 | 23,39% (≈ mean) |
| pin1M | 26,30% | **0,26pp** | 26,03…26,89 | 0,59pp | −15,94…−14,79 | 0,018 | 26,77% (+1,8 sd, gần đỉnh phân phối) |

|Δ| mỗi bước so với sd (CAGR · Sharpe): L1 mergesort 1,1 / 1,7 sd (sàn) · 1,7 / 3,0 sd (trần) ⇒ **trong vùng nhiễu tie-break** về CAGR. L2 LIQ 6,7 / 9,8 sd · 4,7 / 8,7 sd ⇒ **vượt nhiễu rõ** (CAGR lên, Sharpe xuống). L3 adj v2 0,3 / 0,2 sd · 1,3 / 0,9 sd ⇒ trong nhiễu. L4 = 0.
MaxDD ở đầu sàn gần như không đổi theo seed (sd 0,004pp ⇒ tỷ lệ |Δ|/sd vô nghĩa); ở đầu trần sd 0,59pp ⇒ ΔMaxDD L2 −1,50pp = 2,5 sd.
⇒ **Đọc trần pin1M nên dùng trung bình 10 seed 26,30% thay vì 26,77% của một thứ tự tie-break cụ thể**; đầu sàn 23,39% nằm đúng trung tâm.

## 3. Kho bất biến (`data/pinned_ledgers/`, `PINS.jsonl`)

6 ledger mới, `decided_by: agent`, mỗi cái khai `control` = md5 bước trước (byte_identical control đã chạy lại trên code mới): `ladderA-L1-mergesort-pin0pct/pin1M`, `ladderA-L2-liqzblag-pin0pct/pin1M`, `ladderA-L3-lagadjv2-pin0pct/pin1M`. L0 dùng pin sẵn có (`537e349b`, `a6ba34d8`, 10-08, user duyệt). Chưa commit vào git (chờ Mike/user).

## 4. Vì sao L4 trùng byte L3

Engine chỉ đọc 3 file LAG: `earnings_surprise_data.pkl` (chỉ cho `surprise_B_MA`, không dùng ở cấu hình này), `earnings_events_classified.csv` (`post_ret` → `pa_HL3`), `lag_edge_health.csv` (w_LAG theo `mean12 ≥ EDGE_THR=4,0`). `earnings_px.pkl`/`lagged_pos_ov.pkl` KHÔNG được pt_v23 đọc.
- classified adj v2 vs frozen 12/11: 386 dòng `post_ret` khác trước 06-19, 3 dòng `pattern` — không đổi lệnh nào.
- edge_health: 570 (entry, known_date) ≤06-19, max |Δmean12| 0,0014, **0 lần vượt ngưỡng 4,0 đảo chiều**.
⇒ Với AUDIT_END 06-19, "cache adj v2" và "data LAG hôm nay" tương đương trên đường quyết định. Hệ quả: toàn bộ Δ L2→L3 (−0,05/−0,34pp) đến từ classified/edge_health vintage 10-29 → adj v2, không phải từ pkl giá điều chỉnh.

## 5. Blast radius (đo bằng grep, không phải srcwalk)

- **Đường LIVE: 0 file.** `grep regime_size_overlay|apply_regime_size|load_rating8l` trong `trading_bot/`, `mike/bin/`, `golive_recommend*.py`, `bot_*.py` = rỗng. Live chặn ADV qua `cap_lag_orders` (không đổi). Crontab: 0 dòng gọi `pt_v23`/`regime_size_overlay`/`simulate_holistic`.
- **A2 (`LIQ_ZERO_BLOCK`)**: chỉ `pt_v23_audit_2014.py` đổi mặc định. Hai bản research `pt_v23_lagqual_research.py:269`, `pt_v23_lagcap_research.py:269` giữ mặc định cũ `""` (off) ⇒ sau merge chúng LỆCH mặc định với engine chính — phải khai biến khi so. `lag_liquidity_filter.py` chỉ nhắc trong comment (`:127`). `pt_v22_dt5g.py`, `pt_v4_dt5g.py`, `simulate_holistic_nav.py` không có knob ⇒ không đổi hành vi (vẫn kiểu "off").
  **⚠️ ĐÍNH CHÍNH 13/11 (job Taylor_20261112_181209, live_gap_exec_A2/REPORT.md §6):** SAI với `pt_v22_dt5g.py` — `:489` hardcode `liquidity_require_positive=True` cho LAG từ `32d65bbf6` (10/11) ⇒ papertrade pt_v22 (cron 15:30, `papertrade_daily.sh` [12]) ĐÃ chặn kiểu `lag`; A không đổi hành vi của nó.
  Mọi script gọi `pt_v23_audit_2014.py` qua subprocess mà KHÔNG khai biến sẽ đổi số + đổi tên file (`_liqzblag`) — 40+ file R&D (`run_park_ablation.sh`, `sweep_*.py`, `lag_dnpr_harness.py`, `failopen_failclosed_selfcheck.py`, `edge_wlag_gate_selfcheck.py`, `route_selector_selfcheck.py`…). Tên file luôn mang trục ⇒ không ghi đè được CSV pin cũ. Selfcheck có so số cứng với pin cũ cần thêm `LIQ_ZERO_BLOCK=off` (CHƯA rà từng file — việc sau merge).
- **A1 (mergesort)**: mọi engine import `apply_regime_size`/`load_rating8l`: `pt_v4_dt5g`, `pt_v22_dt5g`, `pt_v11_*`, `pt_v12_*`, `pt_v121_*`, `pt_lagvn30_audit_2014`, `pt_v23_audit_ddpark`, `pt_v23_lagcap/lagqual_research`, `run_5systems_prodspec`, `lag_dnpr_harness`, `converge_fullharness_test`, `dvr8l_tilt`, `rating_8l_history`, `basket_price_basis_selfcheck` + nhiều bản sao dưới `data/*_exp/`, `mike/agents/Taylor/exp_*`. Hệ quả: số của các engine này có thể đổi ở mức tie-break (V2.4: +0,19/+0,45pp) và trở nên tất định theo AUDIT_END.

## 6. Chưa đo / giới hạn

- **BQ cache current**: L4 chỉ đổi data LAG; BQ cache giữ `bq_cache_asof20260729_postrestate`. Đóng băng `data/bq_cache` hôm nay = snapshot 2,0GB trong khi đĩa còn 5,6G (98%) và §8b yêu cầu duyệt retention ⇒ CHƯA ĐO, cần user/Mike duyệt dung lượng.
- DSR (`dsr_pbo_annex.py`, manifest `man_2026_07_recon.json`, 68 CSV): L0_off, L3_off, L3_1m đều DSR = 1,0000 ở N=68/120/200 (SR0 0,35–0,40 năm hoá); PBO họ = 0,2085 (thuộc họ, không đổi theo chân). **N trials của job này = 5 cấu hình × 2 đầu dải + 2 control + 2 determinism + 20 seed — KHÔNG có chọn lựa trên kết quả** (trục do brief định trước) ⇒ DSR chỉ để khai báo, không phải claim edge.
- Sharpe trong bảng TB tính lại bằng log-return (tb_stats.py) nên lệch ~0,04 so với Sharpe engine; chỉ dùng để đo sd, không trích.
- Không chạy lại W2b–W5 live-gap; không đổi neo; quant-skeptic CHƯA duyệt.

## 7. Tái lập

```bash
A=mike/agents/Taylor/research/live_gap_exec_A
$A/make_sandboxes.sh                              # sandbox sb/<fam><sort>_<lagdata>
B="BASKET_WT=namecap BASKET_SELECT=yieldcombo"
$A/run_leg2.sh L0_off $B PARK_STATES=3:0.0 IDLE_CARRY_TIER=off                       # → 537e349b
$A/run_leg2.sh L1_off $B PARK_STATES=3:0.0 IDLE_CARRY_TIER=off ENGINE_SORT=mergesort  # → 2f7739b5
$A/run_leg2.sh L2_off ... ENGINE_SORT=mergesort LIQ_ZERO_BLOCK=lag                    # → 5ae929c6
$A/run_leg2.sh L3_off ... LIQ_ZERO_BLOCK=lag LAG_DATA=adjv2_20261110                  # → 84f796bd
$A/run_leg2.sh L4_off ... LIQ_ZERO_BLOCK=lag LAG_DATA=frozen20261112                  # → 84f796bd
# đầu trần: thay IDLE_CARRY_TIER=dep1m (code research 33f005209 + 2 commit A2/A1, worktree -r*)
# control 4707bcbe: run_leg2.sh C30_off_q $B PARK_STATES=3:0.3 IDLE_CARRY_TIER=off
# determinism: run_leg2.sh D0729_{q,m} ... AUDIT_END=2026-07-29; ../live_gap_phase1_20261112/determinism_check.py A B
# seed: run_leg2.sh TB<i>_{off,1m} ... ENGINE_SORT=mergesort TIEBREAK_SEED=<i> LIQ_ZERO_BLOCK=lag LAG_DATA=frozen20261112
$DNA_PYEXE $A/tb_stats.py $A/ledgers
```
Env cố định (trong `run_leg2.sh`): `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19 BASKET_CA_SNAPSHOT=…corp_action_share_20260927.parquet TZ=Asia/Ho_Chi_Minh $DNA_PYEXE`. Dòng `EXIT=… MD5=… CODE=…@sha` cuối mỗi `logs/<TAG>.log`.

**Selfcheck**: mọi chân (L0–L4, C30, D0729, TB) in `[selfcheck LAG] cash-flow identity max err = 0 VND; final NAV identity err = 0 VND`; BAL identity ≈0 VND (PINS metrics, vd L1: 2,3e-5 VND). RAM max/chân 3,29–3,34G (≤5G), threads=1, swap 0.
