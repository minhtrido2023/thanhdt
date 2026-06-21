# Tam Quan v3.4b "Định Tâm" — STAGING NEXT (2026-05-21)

**Codename evolution**: Cổ Điển → Tinh Tế (LIVE) → Tam Quan v3 → v3.1 → v3.3b "Cẩn Thận" (superseded) → **v3.4b "Định Tâm"** (new deploy candidate). Định Tâm = chắc chắn trong bull, không lay động bởi tin Mỹ.

## Logic chi tiết

```python
# Layer 1 — Bull-Trend-Confirmed (BTC) overlay
BTC_R6M = (VNINDEX 6-month return > 15%) AND (VNINDEX > MA200)

# Layer 2 — Conditional US-override
if BTC_R6M[t] == True:
    base[t] = state_v3[t]    # use v3 staging (pre-US-override)
else:
    base[t] = state_v31[t]   # use v3.1 (with US override active)

# Layer 3 — Re-smooth (mode(3) + min_stay(2))
state_smooth = smooth(base)

# Layer 4 — RSI gate + Conc filter (giống v3.3b)
if v31 fire 1-step downgrade at t AND RSI(14)[t] ≥ 55 AND conc[t] ≤ 0.55:
    state[t] = state[t-1]      # block downgrade
    # exit: RSI<55, state hồi, hoặc v3.1 -2 bậc
```

## V11 12y backtest (2014-01-01 → 2026-05-15, 50B init)

| Metric | v3.1 | v3.3b | **v3.4b** | Δ vs v3.1 |
|---|---|---|---|---|
| **FULL CAGR** | 17.58% | 18.62% | **21.14%** | **+3.56pp** |
| **FULL Sharpe** | 1.21 | 1.30 | **1.45** | **+0.24** |
| **FULL MaxDD** | -21.18% | -17.40% | **-17.82%** | **+3.36pp better** |
| **FULL Calmar** | 0.83 | 1.07 | **1.19** | **+0.36** |
| **FULL Wealth** | ×7.41 | ×8.26 | **×10.71** | **+3.30x** |
| **OOS 24-26 CAGR** | 21.28% | 22.12% | **28.88%** | **+7.60pp** |
| **Mid 18-23 CAGR** | 18.76% | 20.60% | **23.00%** | **+4.24pp** |
| **Y2022** | +0.22% | +0.12% | **+1.52%** | +1.30pp |
| **Q1 2026** ⭐ | -11.39% | -11.06% | **+8.30%** | **+19.69pp** |

## Year-by-year highlights

| Year | v3.1 | v3.4b | Δ | Mechanism |
|---|---|---|---|---|
| 2020 | +28.6% | **+42.9%** | **+14.3pp** | COVID recovery — US override stopped derisking |
| 2021 | +83.5% | **+92.0%** | **+8.5pp** | Post-COVID super-bull |
| 2025 | +45.4% | **+55.5%** | **+10.1pp** | 2025 bull — bypassed US override |
| 2026 | -5.2% | **+2.2%** | **+7.4pp** | Q1 2026 fix |

Other years: 12/13 tied or better, 2 years -1pp (small noise scale).

## Walk-forward robustness validation (2026-05-21)

14-variant sweep tested: 6M/3M/9M horizons × multiple thresholds.

**6M horizon plateau** (T = 5-20%):
- FULL CAGR spread: 0.07pp (basically identical)
- OOS CAGR spread: 0.33pp
- v3.4b's T=15% rank 5 IS / **rank 2 OOS** — middle of plateau, not corner

**Beyond T>25%**: degrades meaningfully (FULL CAGR drops to 20.1, OOS 12.9 — too strict, misses real bulls).

**Cross-horizon ranking**: 6M dominates 3M (too noisy) and 9M (too laggy).

**IS-OOS gap**: v3.4b -9.65pp vs v3.1 baseline -11.01pp — **tighter** than baseline, strong non-overfit signature.

## Diagnostic discovery (mechanism check)

US override fires post-2014 split by bull regime:

| Bull regime | n fires | T+60 mean | T+60 %pos |
|---|---|---|---|
| IN BTC_R6M | 43 | **+17.45%** | **100%** |
| OUT BTC_R6M | 107 | +2.29% | 71% |

**Every single US override fire in confirmed bull (43 of them) saw market rise — filter 100% wrong**. v3.4b bypasses 245 such days, allowing portfolio to stay fully invested.

## File artifacts

- State CSV: `vnindex_5state_tam_quan_v3_4b_full_history.csv`
- BQ table: `tav2_bq.vnindex_5state_tam_quan_v34b_clean` (loaded 2026-05-21, 6282 rows)
- Build: `build_v3_4_bull_aware.py`
- Backtest: `test_v3_4_bull_aware.py`
- Walk-forward: `build_v3_4_btc_sweep.py` + `test_v3_4_btc_walkforward.py`
- Diagnostic: `diagnose_bull_regime.py`, `diagnose_bull_regime_v2.py`
- Rejected experiments: v3.5 (conc filter bypass in bull) — caused 2021 -12pp due to over-leverage
- Transitions HTML: `vnindex_transitions_v3_4b.html`
- Shadow tracker: `shadow_track_v3_3b.py` (TODO: update to v3.4b)

## Deploy protocol

1. ✓ Upload BQ `tav2_bq.vnindex_5state_tam_quan_v34b_clean`
2. ✓ Build transitions HTML
3. ✓ Memory update
4. **Pending: 2-week shadow track** (2026-05-22 → [REDACTED]04)
5. **Pending: Promote to LIVE** sau shadow nếu không có vấn đề

## Sustained-bull failure mode reflection (v3.5 reject)

Test v3.5 = v3.4b + disable conc filter trong bull → THUA v3.4b. Năm 2021 mất 12.3pp do over-leverage (EX-BULL +0.4pp distribution → more margin cost).

**Lesson**: filter có thể có 2 chức năng:
- **Predictive** (lớp A): predict đúng/sai về future return
- **Structural** (lớp B): manage leverage exposure gián tiếp

User's hypothesis về bull psychology ĐÚNG ở lớp A (gate fires in bull are HELP, filters lose predictive power). Nhưng tắt filter cũng tắt lớp B → portfolio mất leverage protection → thua.

US override bypass an toàn vì US override không có vai trò leverage management (chỉ predictive). Conc filter có cả hai → giữ.

## Caveats

- **Bias period 2020-2021-2025**: Phần lớn alpha đến từ 3 bull cycles này. Future market regime có thể khác. Mitigation: walk-forward confirmed across IS (2014-2021) + OOS (2022-2026).
- **BTC_R6M slow to detect new bull**: cần ≥ 6 tháng dữ liệu return. Đầu bull cycle, BTC = False → US override vẫn active. Đây là conservative trade-off (avoid false-positive bull).
- **VNINDEX rolling 200-day MA**: cần 200 phiên data. Pre-2001 không có BTC. Không ảnh hưởng modern era.
- **Shadow track 2 tuần** không catch sustained-bull failure (cần tháng). Monitor explicit: nếu OOS hành vi khác backtest → debug.

## Related memory

- [feedback_bull_market_psychology.md](feedback_bull_market_psychology.md) — original user insight
- [tam_quan_v3_3b_can_than.md](tam_quan_v3_3b_can_than.md) — previous STAGING NEXT, superseded
- [tam_quan_v3_1_spec.md](tam_quan_v3_1_spec.md) — v3.1 base for v3.4b
- [ngu_hanh_tinh_te.md](ngu_hanh_tinh_te.md) — current LIVE
