---
name: Validate FA/scoring changes on FULL canonical sim, not just tier-level
description: Tier-level forward-return test có thể đảo chiều với portfolio sim do interactions; phải chạy canonical config trước khi adopt
type: feedback
originSessionId: 762b6179-ddcb-41b7-ac2b-ee8d2f143ccc
---
# Validate FA refactors on canonical sim, not just tier-level

**Rule:** Trước khi adopt bất kỳ thay đổi nào trong FA-system (hoặc bất kỳ component nào trong BA-system pipeline), phải chạy `compare_ba_canonical_v4_vs_v5.py`-style test trên **full canonical config** (SIGNAL_V10, max_pos=10, hold=45d, stop=-20%, sec_lim 8:4, liq caps, 50B init, 50/50 BAL+VN30) — **không** chỉ tier-level forward returns.

## Why
**Reason:** Trong phiên 2026-05-12, FA-system v5 (H3+H4) thắng baseline +0.72pp A median trên tier-level test (forward profit_3M Q4), nhưng khi chạy canonical BA sim **mất 2.61pp CAGR full-period, mất 8.48pp CAGR OOS 2024-2026**. Sharpe và Calmar đều giảm.

**Mechanism:** BA scoring v10 có `+10 Fin/RE-D bonus / -10 Fin/RE-A penalty`. Logic này được tuned cho v4 distribution (SEC ít vào A, REIT A median âm). v5 fix sector bias → đẩy REIT/SEC/INS lên A tier → break tương tác đã tune → portfolio picks tệ hơn.

## How to apply
1. Khi thử nghiệm FA refactor (axis changes, NaN treatment, sector weighting, indicator additions), tier-level test (`test_fa_*.py`) là **filter pass 1**.
2. **PHẢI** chạy canonical sim (`compare_ba_canonical_v4_vs_v5.py` template) trên ít nhất 2 windows: FULL_PERIOD và OOS_2024_2026.
3. Adopt **chỉ khi** v5 ≥ v4 trên cả 2 windows ở CAGR, Sharpe, Calmar (MaxDD có thể trade off chút).
4. Default config sim (`compare_ba_v4_vs_v5.py`) không đủ — phải dùng SIGNAL_V10 + sec_lim + liq caps. Default thiếu interaction effects.
5. Áp dụng cùng rule cho thay đổi: TA scoring, state machine thresholds, sector limits, stop/hold params.

## Quick check
- Tier-level only → green: **không đủ**
- Default sim → green: **không đủ**  
- Canonical sim FULL+OOS → green: **đủ để adopt**

User explicitly confirmed (2026-05-12): "không nên trust tier-level test, phải qua full sim".
