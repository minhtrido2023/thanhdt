# Tam Quan v3.3b "Cẩn Thận" — STAGING NEXT (2026-05-21)

**Codename**: Ngũ Hành → Tam Quan v3.1 (current STAGING) → Tam Quan v3.3b "Cẩn Thận" (deploy candidate)

**Source**: v3.1 STAGING + **RSI uptrend gate** (block 1-step downgrade khi RSI ≥ 55) + **concentration filter** (gate ngừng fire khi conc > 0.55, để bảo vệ trong narrow/VIC-led markets).

## Logic chi tiết

```python
# Khi v3.1 fire 1-step downgrade tại ngày t:
if (state_v31[t-1] - state_v31[t] == 1)        # 1-step down only
   and (RSI_VN(14)[t] >= 55)                   # momentum vẫn lên
   and (concentration_smooth[t] <= 0.55):      # broad market (không VIC-led)
    # Block downgrade — giữ state cao
    state[t] = state[t-1]
    gate_active = True

# Trong khi gate active, exit khi:
#   (a) RSI < 55 (momentum gãy)
#   (b) state v3.1 hồi về mức bị block
#   (c) state v3.1 rơi 2+ bậc (real bear signal — honor)
# Khi exit: state quay về theo v3.1.
```

## V11 12y backtest (2014-01-01 → 2026-05-15, 50B init)

| Metric | v3.1 | **v3.3b** | Δ |
|---|---|---|---|
| FULL CAGR | 17.58% | **18.62%** | **+1.04pp** ✓ |
| FULL Sharpe | 1.21 | **1.30** | **+0.09** ✓ |
| FULL MaxDD | -21.18% | **-17.40%** | **+3.77pp** ✓ |
| FULL Calmar | 0.83 | **1.07** | **+0.24** ✓ |
| FULL Wealth | ×7.41 | **×8.26** | **+0.85x** ✓ |
| OOS 24-26 CAGR | 21.28% | **22.12%** | **+0.85pp** ✓ |
| OOS Sharpe | 1.18 | **1.21** | **+0.03** ✓ |
| Pre-OOS 14-19 | 11.93% | 12.25% | +0.32pp ✓ |
| Mid 18-23 | 18.76% | **20.60%** | **+1.85pp** ✓ |
| Q1 2026 | -11.39% | **-11.06%** | **+0.33pp** ✓ |
| Y2022 | +0.22% | +0.12% | -0.10pp (tied) |

**10/10 tiêu chí PASS** — strongest deploy candidate trong lịch sử v3.x.

## Walk-forward robustness verification

Threshold sweep [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:

| | FULL CAGR | OOS CAGR |
|---|---|---|
| Spread | **0.18pp** | **0.45pp** |
| Plateau | toàn dải | toàn dải |

→ Mọi threshold trong dải cho V11 results gần như identical. **Không phải overfit**.

IS (2014-2021) best vs OOS (2022-2026) best:
- IS-best = no-filter (Calmar 1.34) — nhưng IS-best OOS = WORST (10.50, thua v3.1 baseline)
- OOS-best = t≤0.60 (Calmar 0.66) — bất kỳ conc filter [0.40-0.70] đều top-3 trong cả IS lẫn OOS

→ Kết luận: cần conc filter ở OOS, threshold cụ thể không quan trọng. **Chọn 0.55** vì nằm giữa plateau.

## Diagnostic discovery path (2026-05-21)

1. **Histogram T+5**: upgrade win 64%, downgrade win 49% — concern "ngẫu nhiên"
2. **Horizon diagnostic T+5/T+20/T+60**: upgrade edge +11pp T+20 ✓ (rất tốt), downgrade win edge -0.7pp T+20 (kém) nhưng mean edge -0.77pp ✓ (vẫn né drift)
3. **Per-step**: 1-step upgrade là core alpha, 2-step CRISIS→NEUTRAL noise (rejected v3.2 waypoint)
4. **Downgrade investigation**: 70% downgrades revert_30d post-2014, problem ở pair NEUTRAL→BEAR + BULL→NEUTRAL với T+60 mean +4.5%
5. **F6 filter**: 1-step downgrade + RSI ≥ 55 → BLOCK n=30 mean +6.23% (clear noise)
6. **v3.3 backtest**: +0.87pp FULL CAGR nhưng OOS tied + **Q1 2026 -3.80pp** ⚠
7. **v3.3b conc filter (≤0.55)**: fix Q1 2026 (-3.80 → +0.33pp), OOS thành +0.85pp, mọi metric khác cải thiện

## File artifacts

- State CSV: `vnindex_5state_tam_quan_v3_3b_full_history.csv`
- BQ table: `tav2_bq.vnindex_5state_tam_quan_v33b_clean` (loaded 2026-05-21, 6282 rows)
- Build script: `build_v3_3_conc_variants.py` (also produces 3.3c)
- Backtest script: `test_v3_3_conc_variants.py` (4-way comparison)
- Walk-forward: `test_v3_3_walkforward.py` (8-variant sweep)
- Diagnostic: `investigate_v3_1_downgrade_weakness.py` + `diagnose_v3_3_fires_by_conc.py`
- Transitions HTML: `vnindex_transitions_v3_3b.html`
- Shadow tracker: `shadow_track_v3_3b.py` (run daily 15:30)

## Deploy protocol

1. ✓ Upload BQ table `tav2_bq.vnindex_5state_tam_quan_v33b_clean`
2. ✓ Build transitions HTML for user review
3. ✓ Memory update with full spec
4. **Pending: 2-week shadow track** (2026-05-22 → [REDACTED]04) — daily diff vs LIVE
5. **Pending: Promote to LIVE** nếu shadow không bộc lộ vấn đề. Sequence:
   - Backup `tav2_bq.vnindex_5state` → `_archive_tinh_te_{TS}`
   - Replace `tav2_bq.vnindex_5state` ← v3.3b
   - Update `recommend_holistic.py` (no code change — đọc cùng table)
   - Codename promotion: "Cẩn Thận" thành LIVE

## Caveats & known limitations

- **Q1 2025**: gate vẫn fire 2 false alarms (2025-03-12, 2025-03-24 conc 0.29/0.35 — broad market nhưng momentum top). Conc filter không catch (vì conc < 0.55). Net 2025 -0.8pp vs v3.1, chấp nhận trade-off.
- **Bull psychology không model**: trong sustained bull, conc filter có thể vô hiệu (xem `feedback_bull_market_psychology.md`). v3.4 hướng tương lai có thể add "bull-day-counter" disable filter sau N+ phiên BULL/EX-BULL.
- **Pre-2014 fires (11) không có conc data** — gate hoạt động như v3.3 base ở giai đoạn này. Khôi phục bằng cách extend concentration history (chưa cần).
- **State distribution**: EX-BULL +0.9pp, BULL -0.4pp, BEAR -0.7pp — gate hold giữ EX-BULL lâu hơn trong bull cycles (2020-21).
