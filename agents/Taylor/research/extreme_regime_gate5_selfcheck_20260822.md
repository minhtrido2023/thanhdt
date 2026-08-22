# Gate 5 — selfcheck sweep `extreme_regime` (job Taylor_20260822_023836)

**Verdict: PASS.** Không flip live gate, không sửa code production. Gate 6 (quant-skeptic) đã
được Mike dispatch riêng — không dispatch thêm ở đây.

## 1. Selfcheck chuyên trách
`extreme_regime_selfcheck.py` (repo root — KHÔNG nằm ở `agents/Taylor/` như prompt dispatch giả
định): **19/19 PASS**, exit 0. Bao gồm nhóm A (OFF ⇒ NORMAL byte-identical), B (2-poll confirm,
sell-to-floor, BUY pause, slice-mult), C (OFF end-to-end vẫn đặt lệnh), D (tương tác EXTREME ×
HYBRID cả hai chiều, kèm chứng minh ngược).

## 2. Sweep §23 — executor.py là module lõi (21 selfcheck phụ thuộc)
Gate nằm trong `trading_bot/executor.py` ⇒ theo §23 phải quét rộng, không chạy hẹp.
`bin/selfcheck_scope_map.sh trading_bot/executor.py` liệt kê 21 file. Chạy đủ **21/21, rc=0, 0 FAIL**:

book_tagging · capit_lever · capit_participation_cap · churn_guard · dcf_check ·
discretionary_participation_cap · dynamic_no_chase_ceiling · expected_volume_pacing ·
extreme_regime · ghost_order · hard_no_chase_ceiling · hybrid_fill_timing · order_book_shadow ·
paper_main_window · plan_check_field_schema · probe_linger · refresh_skip_participation ·
rule_a_ceiling · rule_a_ref_guard · t2_settlement · tick_retry

## 3. Ma trận TZ (§16 + §19)
`extreme_regime_selfcheck.py` chạy lại dưới `env -u TZ`, `TZ=America/New_York`, `TZ=UTC` — PASS
cả 3, 0 FAIL. `hybrid_fill_timing_selfcheck.py` (tầng có logic khung giờ, tương tác trực tiếp với
EXTREME ở nhóm D) chạy `env -u TZ` + `TZ=America/New_York` — PASS cả 2.

## 4. Marker EXTREME trên journal thật
Quét chuỗi `EXTREME` trên **toàn bộ 30 file** `exec_main_*_journal.csv` (2026-07-07 → 2026-08-21):
**0 hit**. Cửa sổ 08-17→08-21 mà dispatch chỉ định: 0/5 phiên có marker (171 dòng journal, event
chỉ gồm PLACE/FILL/DONE/HYBRID_DEFER/CANCEL_STALE/REFRESH_SKIP/PROBE_LINGER_*).

**Nói rõ mẫu, không làm tròn lên:** 34 ngày giao dịch trong khoảng đó nhưng chỉ **30 phiên có
journal** — thiếu 07-28, 07-29 (bug netting harness đã biết), **08-03 và 08-14 chưa giải thích
được** (08-14 có journal SpaceX ⇒ thị trường mở, harness paper main không chạy). Trong 30 phiên,
07-30 là phiên hỏng (431 dòng FAIL, bug `cash_only` đã vá) ⇒ **29 phiên sạch** dùng được cho điều
kiện 2. Vẫn vượt mốc 20 phiên, nhưng con số đúng là 29/30, không phải 34.

## 5. Replay qua HÀM PRODUCTION THẬT (bằng chứng mạnh hơn "không thấy marker")
`mike/agents/Taylor/replay_extreme_gate_20260822.py` (R&D, KHÔNG wire) nạp
`data/execution_logs/probe_ticks_main_2026-08-{20,21}.csv` — **1.140 tick, 6 mã** — rồi gọi thẳng
`Executor._extreme_regime()` + `Executor._floor_guard_buy()` với `extreme_regime_enabled=True`
(cfg còn lại = DEFAULTS, mode=paper):

| Ngày | Tick | `_extreme_regime` armed | `_floor_guard_buy` |
|---|---:|---:|---:|
| 2026-08-20 | 462 | 0 | 0 |
| 2026-08-21 | 678 | 0 | 0 |

**Chứng minh ngược (bắt buộc — nếu không thì PASS có thể là do harness chết):** cùng script, ghi
đè `last := floor`, cho ra **1.134/1.140 armed + 1.140/1.140 floor-guard**. Chênh 6 tick đúng bằng
6 mã ở poll đầu chưa đủ 2-poll confirm — khớp thiết kế. Vậy PASS ở trên là kết quả đo thật.

⚠️ `r15` được **inject theo giá trị đã ghi trong tick log**, không tái dựng từ buffer giá intraday
(buffer đó không persist). Đầu vào là số harness ghi lúc chạy live, nhưng đường tính r15 không nằm
trong phạm vi replay này.

## 6. Khoảng cách tới ngưỡng — đóng caveat "bằng chứng một chiều" của 08-19 cho nhánh (ii)
- Trigger (i) cận sàn: `headroom_floor` nhỏ nhất = **6,20%** (HDB 2026-08-21T10:00:25) vs band 3,00%.
- Trigger (ii) 3-sigma: **942/1.140 tick đã có r15** (08-19 chưa đo được nhánh này). Biên gần nhất
  = **+3,25pp** (ACB 2026-08-20T11:12:12: r15 −0,45% vs ngưỡng −3,70%).

⇒ Cả hai nhánh giờ đã **đo được**, không còn là "chưa từng quan sát". Nhưng bản chất bằng chứng
vẫn là: thị trường benign, chưa lần nào tới gần ngưỡng. Đây là bằng chứng KHÔNG-false-trigger,
KHÔNG phải bằng chứng gate bắt đúng khi thị trường thật sự sụp — đúng như chính sách đã chốt
(gate = bảo hiểm, không phải alpha; không đợi sự kiện sập thật).

## 7. Trạng thái 6 điều kiện
| # | Điều kiện | Trạng thái |
|---|---|---|
| 1 | Stress-injection 40/40 | PASS (từ 07-13) |
| 2 | ZERO false-trigger qua phiên benign | PASS — 0 marker / 29 phiên sạch (30 phiên ghi) |
| 3 | Không can thiệp NORMAL-path | PASS — 0 arm; replay production function xác nhận |
| 4 | Cả 2 nhánh trigger đo được | PASS — (i) headroom min 6,20%; (ii) 942 tick, biên gần nhất 3,25pp |
| 5 | **Selfcheck sweep** | **PASS — 21/21 + TZ matrix, báo cáo này** |
| 6 | quant-skeptic | dispatch riêng, ngoài phạm vi job này |
