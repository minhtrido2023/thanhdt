---
name: Layer 3 — Intraday Entry Timing
description: Fine-tune entry timing trong phiên cho watchlist từ Holistic engine
type: project
originSessionId: cc0496d6-7fd6-4cd3-8964-4af6fe223c99
---
# Layer 3 — Intraday Entry Timing

**Script:** `layer3_intraday_timing.py` | Output: `layer3_intraday_signals.csv`

## Mục đích

Sau khi Holistic engine chọn top picks (BUY priority list từ EOD), Layer 3 quét intraday data của phiên hôm nay (qua vnstock API 15m bars) để chấm điểm entry timing:
- Có nên mua **hôm nay** (close T+0) hay đợi T+1?
- Hay tránh nếu phiên đang yếu?

## Workflow

```
EOD T-1 → recommend_holistic.py output watchlist
           ↓
Trong phiên T → layer3_intraday_timing.py quét intraday
           ↓
GO_STRONG / GO / WAIT / AVOID per ticker
           ↓
Trader quyết định: enter trong phiên T hay đợi
```

## Scoring Algorithm (max ~120 points)

| Factor | Logic | Score |
|---|---|---|
| **VWAP regime** | ≥60% bars trong session đóng trên VWAP | +30 |
| | 40-60% bars trên VWAP | +10 |
| | <40% (bị bán) | 0 |
| **Last bar direction** | Bar cuối green & close > VWAP | +20 |
| | Bar cuối red & close < VWAP | -10 |
| **1-hour trend** | Last 4 bars > +0.5% | +15 |
| | Last 4 bars < -0.5% | -10 |
| **RSI(14) 15m** | 50-75 (healthy momentum) | +15 |
| | <40 (weak) | -5 |
| **MACD histogram** | > 0 (positive momentum) | +15 |
| **Position in day range** | Upper 60%+ of H-L | +10 |
| | Lower 30% (bottom of range) | -10 |
| **Late-day weakness** | Last 30min drops > -0.5% | -15 |
| **Volume burst up** | Last hour vol ≥ 1.5× avg AND trend up | +10 |

## Verdict thresholds:

- **GO_STRONG** (score ≥ 60): Buy at close today, full conviction
- **GO** (40-59): Buy reasonable, scaled-down position
- **WAIT** (20-39): Hold off, re-check tomorrow
- **AVOID** (< 20): Don't buy, regime weak

## Sample test output (2026-05-08):

```
ticker   verdict   score  close  vs_VWAP  RSI  pos_in_range  trend_1h
HPG    GO_STRONG    75   27.85   +0.27%   57.0    86%        +0.36%
PVS    GO_STRONG    60   38.70   +0.08%   43.4    45%        +0.78%
FPT      AVOID    -15   71.90   -0.58%   27.5     0%        -0.42%
VNM      AVOID    -10   60.90   -0.36%   41.7     0%        -0.16%
```

## Usage

```bash
# Auto-load from latest holistic_*.csv:
python layer3_intraday_timing.py

# Manual ticker list:
python layer3_intraday_timing.py "FPT,VNM,HPG,VVS"

# Specific date for backtest:
python layer3_intraday_timing.py "HPG" 2026-02-02
```

## Architecture

- Calls `stockquery.StockQuery.get_historical_symbol(ticker, "15m")` → ~7 days × 16 bars/day
- Computes session VWAP, RSI(14), MACD(12,26,9) histogram, volume MA(20)
- Aggregates 9 scoring factors → final verdict

## Integration với Holistic engine

Top picks workflow:
1. **EOD post-15:00**: run `recommend_holistic.py` → get top 10-20 watchlist
2. **Next morning ≥ 09:30**: run `layer3_intraday_timing.py` for those picks
3. **Mid/end-day**: re-run intraday script to re-check verdicts
4. **Place orders**: prioritize GO_STRONG → GO; skip AVOID

## Limitations

- Requires vnstock API (sometimes rate-limited)
- 15m bars chỉ available cho VN30 + most prune universe; small caps có thể thiếu
- Scoring is heuristic, chưa backtest trực tiếp do thiếu intraday lịch sử
- Cần thêm validation forward (track verdict vs T+5 outcomes)
