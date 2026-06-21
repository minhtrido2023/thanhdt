---
name: FA-system extension test results (2026-05-12)
description: 6 góc nhìn FA mới đã backtest; T6 Industry modifier là cải tiến duy nhất có ý nghĩa (+1.52pp A-E spread)
type: project
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# FA extensions backtest — kết quả 2026-05-12

**Script:** `test_fa_extensions.py` | **Output:** `fa_ext_results.csv`
**Universe:** 3,313 (ticker, Q4) rows từ 2014, liquidity ≥ 1B VND/ngày | **Metric:** median forward `profit_3M` per tier

## Bảng tổng hợp (A−E median spread, pp)

| Variant | A% | E% | Spread | Δ vs base | Verdict |
|---------|----|----|--------|-----------|---------|
| baseline (v4)        | 6.67 | -3.76 | **10.43** | — | reference |
| T1 Margin slope      | 6.27 | -3.50 |  9.77 | **-0.66** | ❌ hurt (E mean +0.61, pha loãng growth) |
| T2 Beneish-lite      | 6.65 | -4.01 | 10.67 | +0.23 | ⚠️ marginal |
| T3 Working capital   | 5.98 | -2.96 |  8.94 | **-1.50** | ❌ hurt nặng |
| T4 Solvency depth    | 6.74 | -3.70 | 10.44 | +0.01 | ⚪ neutral |
| T5 ROIC trend        | 6.65 | -3.70 | 10.35 | -0.08 | ⚪ neutral |
| **T6 Industry mod**  | 6.66 | **-5.29** | **11.95** | **+1.52** | 🏆 **ADOPT** |

Tất cả variants giữ monotonic A>B>C>D>E (0 inversions).

## Kết luận

**ADOPT T6 vào FA v5** — sector-weighted axes (NH/CK/BH dùng weight khác CT):
```python
SECTOR_WEIGHTS = {
    "NH": {quality:0.25, stability:0.20, cash:0.05, shareholder:0.15,
           growth:0.10, health:0.15, valuation:0.10},
    "CK": {quality:0.22, stability:0.20, cash:0.05, shareholder:0.15,
           growth:0.13, health:0.10, valuation:0.15},
    "BH": {quality:0.22, stability:0.22, cash:0.05, shareholder:0.15,
           growth:0.13, health:0.10, valuation:0.13},
    "CT": baseline,  # default
}
```
T6 hiệu quả vì:
- E tier median -5.29% (vs -3.76%) — đào sâu hẳn nhóm tệ
- E WR chỉ 38.5% (vs 42%) — filter mạnh hơn rõ rệt
- A tier giữ nguyên 6.66% → không hy sinh upside

**REJECT T1, T3** — đều làm xấu spread. Lý do: margin slope/working capital không cùng phân phối với indicators hiện tại trong trục growth/quality, pha loãng signal mạnh (NP_R, ROIC5Y).

**SKIP T2, T4, T5** — marginal/neutral, không đáng độ phức tạp.

## Update 2026-05-12 (cùng phiên) — T6 refined

Phát hiện ICB_Code trong BQ là **numeric** (8355=BANK, 8633=REIT, 8536=INS, 8775/77=SEC), không phải 2-letter codes như giả định. T6 phiên đầu thật sự không test được industry-weighting — fallback toàn bộ về default. Cải thiện +1.52pp là **NaN treatment artifact** (fill 0 vs drop).

Script: `test_fa_t6_refined.py`, `test_fa_t6_sectorrank.py` | Output: `fa_t6_refined_results.csv`

### Findings tách bạch effects

| Effect | Δ spread vs base |
|--------|------------------|
| **NaN=0 penalty (universe)** | **+1.52pp** ✓ real |
| Industry weight reshuffle (B/C/D) | -0.2 to -1.0pp ✗ hurt |
| Sector-relative ranking | -0.70 (no NaN) / +0.98 (w/ NaN) |
| Hybrid (non-fin uni / fin sector) | -0.59 / +1.25 (w/ NaN) |

### Hidden sector bias (lý do T6e/g vẫn đáng giá dù spread thấp hơn)

Baseline (+ NaN=0) bị bias nặng: SECURITIES **0/237 reach A**; INSURANCE A=1 với -22.4%; REIT A=14 với **-1.6%** (inverse).

T6e_sectorrank fix triệt để: SECURITIES A=29 +7.4%, INSURANCE A=11 +1.3%, REIT A=58 +6.5%.

### Khuyến nghị adopt cuối cùng

**`T6g_hybrid_nan0`** = non-financials rank universe-wide + financials rank within sector + NaN=0 penalty:
- Spread A−E = 11.68pp (vs base 10.43, +1.25pp)
- A tier healthy across all sectors (+6.3% to +8.8%)
- Phù hợp BA-system `sec_lim Fin/RE max 4` (cần representative financial picks)

**KHÔNG adopt**: industry weight reshuffle (T6 original/T6b/c/d) — đều hurt.

## Update — H3+H4 combo (script: test_fa_t6_finetune.py + test_fa_t6_combo.py)

Sweep 5 tinh chỉnh tiếp theo. Findings:
- H1 (min_axis_coverage): no-op once NaN=0
- H2 (NaN fill intensity > 0.1): worse
- H3 (indicator-level NaN fill 0): A median **6.65→7.15** (+0.50)
- H4 (Beneish-lite on DEFAULT only): spread +0.16, A median +0.16
- H5 (top 5% tighter A tier): worse (A=6.30, less alpha)
- **H3+H4 combo:** A median **7.39%**, A mean **8.58%**, WR 65.3% — best in long-only metrics

### All-quarters robustness check (13,236 rows)
- T6g_hybrid_nan0: spread 5.46 nhưng có **A < B inversion (fragile)**
- H3+H4 combo: spread 5.72, mono ✓ — robust

### NEW FINAL recommendation: H3+H4 combo (supersedes T6g)
Spec for v5:
- Mode: hybrid (universe-rank DEFAULT, sector-rank BANK/REIT/INS/SEC)
- **Indicator-level NaN fill 0** (fill before axis mean)
- Health axis cho DEFAULT extends với 4 Beneish-lite: DSO_delta, FinLev_delta, GPM_delta_abs, AT_delta
- Financials giữ AXIS_BASE (Beneish không meaningful cho bank/REIT)
- Tier thresholds nguyên: top 10/30/60/85%

Expected improvement vs current v4 baseline:
- A median: 6.67% → **7.39%** (+0.72%)
- A mean: 7.31% → **8.58%** (+1.27%)
- A WR: 66.3% → 65.3% (-1.0pp, marginal)
- E median: -3.76% → -4.03% (slightly deeper)

## ✅ BA-system validation (2026-05-12)

Script: `fundamental_rating_v5.py` + `compare_ba_v4_vs_v5.py`
BQ table: uploaded as `tav2_bq.fa_ratings_v5`
Sim: 2014-01 → 2026-01 (12 years), default config (-15% stop, 60d hold, no slippage)

### BALANCED_8pos (canonical)
| Metric | v4 | v5 | Δ |
|---|---|---|---|
| CAGR | 26.79% | **30.83%** | **+4.03pp** |
| Sharpe | 1.26 | **1.39** | +0.13 |
| MaxDD | -32.0% | **-27.1%** | +4.9pp (DD shallower) |
| Calmar | 0.84 | **1.14** | +0.30 |
| WinRate | 57.5% | 58.1% | +0.6 |
| AvgRet | 12.13% | 12.86% | +0.73 |

### HIGH_CONV_5pos
| Metric | v4 | v5 | Δ |
|---|---|---|---|
| CAGR | 31.96% | 37.09% | +5.13pp |
| Sharpe | 1.17 | 1.31 | +0.14 |
| MaxDD | -37.0% | -29.4% | +7.6pp |
| Calmar | 0.86 | 1.26 | +0.40 |

VNINDEX B&H: 11.54% / 0.69 / -45.3%

### Mechanism
v5 không tăng số trades đáng kể (+8 trades trên 219 in BAL). Cải thiện thuần từ chất lượng pick. Play-type distribution: SECURITIES từ 0% A tier (baseline) lên 32 A picks; PASS giảm 7,318; WAIT/COMPOUNDER_HOLD tăng 11,628.

### Caveat
Default sim config khác BA canonical (-20% stop, 45d hold, slip, liquidity caps, sec lim). CAGR tuyệt đối 26-31% > BA canonical 17.15% vì idealized. Nhưng **relative Δ v5 vs v4 robust** trên cùng config.

## Status: READY TO ADOPT
- [x] H3+H4 spec validated tier-level + BA-system level
- [x] Rerun với BA canonical config — **REVEALED CRITICAL FAILURE**
- [ ] ~~Replace `tav2_bq.fa_ratings` content with v5~~ **DO NOT DEPLOY**
- [ ] ~~Update `recommend_holistic.py` reference~~

## ⚠️ CRITICAL FINDING — v5 FAILS on BA canonical config (2026-05-12)

Script: `compare_ba_canonical_v4_vs_v5.py`. Canonical = SIGNAL_V10, max=10, hold=45d,
stop=-20%, slip=0.1%, sec_lim 8:4, liq caps 20% ADV, init_nav=50B, 50/50 BAL+VN30.

| Period | v4 CAGR | v5 CAGR | Δ |
|--------|---------|---------|---|
| FULL 2014-2026 | **16.59%** | 13.98% | **-2.61pp** ❌ |
| OOS 2024-2026  | **22.71%** | 14.23% | **-8.48pp** ❌ |
| OOS 2022-2026  | 9.99%  | 5.85% | -4.14pp ❌ |

Sharpe, Calmar đều giảm. MaxDD ngang. Trade count v4=437 → v5=412.

### Root cause analysis
BA scoring v10 có **`+10 bonus cho Fin/RE×D-tier` và `-10 penalty cho Fin/RE×A-tier`**.
Logic này được tuned khi v4 đặt Securities gần như không vào A tier (0/237) và REIT có A=14 với median -1.6%. v5 fix sector bias → đẩy REIT/SEC/INS lên A tier → giảm Fin/RE-D bonus, tăng Fin/RE-A penalty → ít MOMENTUM/MEGA picks trong Fin/RE → portfolio diversification giảm + miss winners.

### Lesson (lưu vào feedback memory)
**Tier-level forward-returns test KHÔNG đủ validate FA system change cho portfolio**.
Portfolio scoring (v10) có interactions phi-tuyến với tier distribution — đổi 1 component
sẽ phá tương tác đã tune. **Phải test full canonical sim trước khi adopt bất kỳ FA refactor nào.**

### Adoption decision
**❌ KHÔNG DEPLOY v5** vào production. 3 options:
1. **Keep v4** (safe, BA đang stable ~17% CAGR)
2. **Partial adopt**: v5 cho `recommend_holistic.py` (live single-quarter screening) nhưng giữ v4 cho BA sim/historical
3. **Re-tune BA v11**: refactor Fin/RE bonus/penalty + sector limits cho v5 distribution (1-2 phiên work, ROI uncertain)

## Còn lại (chưa hoàn thành)
- [ ] Viết `fundamental_rating_v5.py` adopt T6g_hybrid_nan0
- [ ] Validate v5 trên BA-system: rerun `simulate_holistic_nav.py` xem CAGR/Sharpe/DD thay đổi ra sao
- [ ] (Optional) Test thêm `min_axis_coverage=4/7` filter trước khi compute score (an toàn hơn fill-0)

User chờ quyết: viết v5 luôn, hay validate impact lên BA-system trước.
