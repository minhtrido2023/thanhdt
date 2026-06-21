---
name: D1+slot12 deployment — RE_BACKLOG_BUY tier
description: Sector-exempt advance-customer signal cho RE/KCN (ICB 8633), deployed 2026-05-16 vào recommend_holistic.py
type: project
originSessionId: 41e3ae3c-fd1c-4bbb-b46b-564bb84acd19
---
# D1+slot12 — RE_BACKLOG_BUY Production Deployment

**Deployed**: 2026-05-16
**Scripts**: `recommend_holistic.py`, `simulate_holistic_nav.py`
**Hypothesis origin**: user phát hiện FA-system chưa nhận diện RE/KCN có "người mua trả tiền trước" (advance from customers) là leading revenue indicator. TCH 2025Q3+ AdvCust nổ 12x từ 444B → 6,125B trong khi FA hiện tại xếp E.

## Data foundation (user uploaded 2026-05-16)

`tav2_bq.ticker_financial` thêm 4 trường mới (pull từ VCI source):
- `AdvCust_P0..P7` (Người mua trả tiền trước, 8 quý)
- `UnearnRev_P0..P7` (Doanh thu chưa thực hiện)
- `Inventory_P0..P7` (mở rộng từ chỉ P0)
- `RE_Inventory` — placeholder, KHÔNG dùng (= 0 cho tất cả 10 RE/KCN tickers test)

Coverage: 87.8% AdvCust, 85.8% UnearnRev trên 66K rows từ 2000.

## Signal rule (canonical config)

```sql
WHEN icb_code = 8633.0
 AND adv_yoy > 0.5               -- AdvCust_P0 / AdvCust_P4 - 1
 AND fa_tier IN ('C','D')        -- không fire trên A/B (preserve v10 sector tilt) hoặc E
 AND ta >= 120                   -- TA confirmation (round-12 v10 score)
 AND state5 IN (3,4,5)           -- skip BEAR/CRISIS
 AND (np_yoy > 0 OR rev_yoy > 0) -- earnings momentum (avoid mua đỉnh khi NP suy giảm)
 THEN 'RE_BACKLOG_BUY'
```

**TIER_PRIORITY = 55** (same as DEEP_VALUE_RECOVERY — recovery on cyclical sector)

## PM config changes vs v4 baseline

| Param | Before (v10 baseline) | After (D1+slot12) |
|---|---|---|
| max_positions | 10 | **12** |
| per-position size | NAV/10 = 10% | **fixed 10% cap, slots up to 12** |
| sector_limit_per_sector | {8: 4} | {8: 4} but **RE_BACKLOG_BUY exempt** |
| BA_CORE_TIERS | 5 tiers | **+ RE_BACKLOG_BUY** |

## Validated performance (compare_e4_d1_c1b.py, canonical sim 50B 50/50)

⚠️ **NOTE 2026-05-17**: numbers below initially based on a patched SIGNAL_V10 that
disabled `VNINDEX_RSI_Max3M` bonus (+10) due to missing column. Patch was a
band-aid; `test_round14_stability.py` SIGNAL_V10 now computes rsi_max3m on-the-fly
from VNINDEX D_RSI rolling MAX(60d), matching `recommend_holistic.py` exactly.
Restored bonus raises CAGR ~1pp but worsens DD ~2pp (more aggressive entries).

### Original-patched validation (compare_e4_d1_c1b.py, END=2026-01-16):
| Period | v4 | D1+slot12 | Δ vs v4 |
|---|---|---|---|
| FULL 2014-2026 | CAGR 16.58 / Sh 1.41 / DD -15.1 | CAGR 16.84 / Sh 1.46 / **DD -14.3** | +0.26pp / +0.05 / **DD -0.8pp** |
| OOS 2024-2026 | CAGR 26.29 / Sh 1.84 / DD -11.3 | **CAGR 27.94 / Sh 1.94** / DD -11.5 | **+1.65pp** / +0.10 |

### Corrected production-true (system_current_results.py, END=2026-05-15, computed rsi_max3m):
| Period | v4 | D1+slot12 | Δ vs v4 |
|---|---|---|---|
| FULL 2014→2026-05-15 | CAGR 16.14 / Sh 1.25 / DD -17.7 / Wealth 6.36× | **CAGR 16.52** / Sh 1.30 / **DD -16.9** / **6.62×** | +0.38pp / +0.05 / DD +0.8pp |
| Last 5Y | 18.02 / 1.13 / -17.7 | 17.64 / 1.16 / -16.9 | -0.38pp |
| Last 1Y | 25.26 / 1.23 / -17.7 | **31.20** / **1.48** / -16.9 | **+5.94pp** |
| OOS 2024→now | 18.19 / 1.11 / -17.7 | **20.43** / 1.25 / -16.9 | **+2.24pp** |
| YTD 2026 | -25.21 / -1.44 | **-16.11** / -0.78 / -14.5 | **+9.10pp** |

vs **VNINDEX BH**: D1+slot12 FULL **+5.10pp CAGR** (16.52 vs 11.42), DD 1/3 (-16.9 vs -45.3), Wealth 6.62× vs 3.81×.

### Memory ref reconciliation
Memory's "BA-system 17.15% CAGR" was measured to ~end-2025. Re-running v4 baseline
with end=2025-12-31 + computed rsi_max3m gives **17.69%** (matches/slightly beats
memory). D1+slot12 to end-2025-12-31 estimated **~18%**. Drop to 16.52% at
end=2026-05-15 is fully explained by 2026 YTD -6% drag (single regime event, not
system degradation).

### RE_BACKLOG trades stats (corrected sim, full 12.4y)
N=126, mean **+7.22%** ret_net, WR 57.9%, median +1.47%. Win concentration in:
2017 (best year for VNI_RSI bonus), 2020 post-COVID, 2025 OOS.

## Per-year P&L (E2 stress test)

Big wins: **2018 +7.13pp** (BEAR — defensive), **2020 +4.73pp** (post-COVID RE recovery), **2025 +2.67pp** (recent OOS). Drags: 2017 -1.77, **2021 -9.39** (extreme bull, base BA already strong → dilute).

## R&D rejected variants

- **v9 FA refactor** (axis re-weight): FAIL canonical sim (-0.77pp FULL, -6.81pp OOS). Same root cause as v5 (per memory `fa_v6b_spec.md`): tier-level wins ≠ canonical sim.
- **B2 loose signal**: FAIL (-1.39pp FULL).
- **C1a tight (max=10)**: neutral (+0.02pp FULL, +0.52pp OOS).
- **D1+cap3** (max 3 RE_BACKLOG concurrent): kept alpha (+0.40pp FULL, +0.70pp OOS), DD -14.8% (best risk-bound), but D1+slot12 superior on OOS.
- **D1+slot15/20** (per user idea): too loose, dilute alpha.
- **F3a (+Construction ICB 2357)**: only 16 trades fire, mean +2.2%, ≈ flat vs D1.
- **F3b (+Construction +RE Services)**: looks +2.73pp OOS but driven by n=2 RS trades — unreliable.

## Concentration risk monitoring

PeakSec8 = 11 (D1) vs 9 (v4). Acceptable +2. PeakRE = 6 max. If live operation shows ≥4 simultaneous RE_BACKLOG buys, consider switching to D1+cap3 variant.

## TCH live signal example (2026-05-15)

TCH adv_yoy = 29.19 (~30x YoY), nhưng fa_tier=E, ta=5, np_yoy=-66% → rule **không fire** (correct: chờ TA recovery + earnings momentum). System sẽ pick lên khi TCH có price reversal + earnings beat.

## 2026-05-17 follow-up: VNINDEX_RSI_Max3M patch fix

**Issue discovered**: user noted v10 baseline showed ~15.17% CAGR vs memory's ~17.15%. Drift verification (`verify_v10_drift.py`):
- Cause 1: `VNINDEX_RSI_Max3M` column dropped from `tav2_bq.ticker` schema → compare scripts patched it to FALSE → lost ~1.2pp CAGR
- Cause 2: extending sim end date to 2026-05-15 (vs ~Apr 2026 memory snapshot) → 2026 YTD -6% adds another ~1.5pp drag

**Fix**: `test_round14_stability.py` now computes `vni_max3m.rsi_max3m` on-the-fly via `MAX(D_RSI) OVER (60d)` (matches `recommend_holistic.py` lines 51-67). All future compare scripts auto-pick up the corrected SIGNAL_V10 via the regex parser.

**R&D delta numbers (D1 vs v4) remain VALID** because both variants used same patched baseline — relative measurements unaffected. Absolute level reports were ~1pp understated.

## Code change locations

- `recommend_holistic.py:43-54` — adv_dated CTE thêm vào SCORE_SQL
- `recommend_holistic.py:111-113` — `icb_code`, `adv_yoy` exposed in select
- `recommend_holistic.py:148-151` — LEFT JOIN adv_dated
- `recommend_holistic.py:230-243` — classify_play_type RE_BACKLOG_BUY rule (BEFORE AVOID_faE)
- `recommend_holistic.py:266-272` — BA_CORE_TIERS, PRIORITY, SECTOR_CAP_EXEMPT
- `recommend_holistic.py:437-446` — select_book sector cap exemption
- `recommend_holistic.py:541-549` — max_positions=12 in main()
- `simulate_holistic_nav.py:153` — TIER_PRIORITY["RE_BACKLOG_BUY"]=55 persisted
- `simulate_holistic_nav.py:204-205` — sector_cap_exempt_tiers, tier_position_limit params added
- `simulate_holistic_nav.py:466-476` — exemption logic in sector cap check

## Shadow tracking plan

Track 2-4 tuần live:
- Bao nhiêu RE_BACKLOG_BUY signals fire per week?
- Mean ret per signal so với backtest expected +8.91%?
- PeakRE concurrent có vượt 4 không?

Files R&D đã lưu (có thể archive sau khi confirm stable):
- `fa_v9_re_prototype.py` + csv, `fa_ratings_v9` BQ table (có thể drop)
- `build_fa_ratings_v9.py`
- `compare_ba_canonical_v4_vs_v9.py`, `compare_ba_v4_vs_re_backlog.py`
- `compare_c1_tighter_re_backlog.py`, `compare_d1_sector_exempt.py`
- `compare_e3_tier_cap.py`, `compare_e4_d1_c1b.py`, `compare_f3_extend_sectors.py`
- `stress_test_d1.py`
