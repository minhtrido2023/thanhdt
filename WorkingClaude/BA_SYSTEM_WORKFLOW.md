# BA-system v10 — Simulation Workflow

Documentation của luồng simulation production. Đọc file này để hiểu/reproduce hệ thống.

**Production scripts:**
- `simulate_holistic_nav.py` — sim engine (single-book NAV simulation)
- `recommend_holistic.py` — daily live engine
- `test_round*.py` — backtest variants (mỗi round test 1 hypothesis)

**Performance baseline (12 năm 2014-2026, 50B NAV):**
```
BA-system 50/50 (BAL_Fin4 + VN30_BAL):
  CAGR=17.15%  Sharpe=1.21  MaxDD=-14.5%  Calmar=1.18  Q-Win=85.4%
  Wealth multiplier 6.73× | 2022 crash: +2.6% (vs VNI -33%)
```

---

## 1. Data sources (BigQuery)

Project: `lithe-record-440915-m9` | Dataset: `tav2_bq` (asia-southeast1)

| Table | Mục đích | Key columns | Date range |
|---|---|---|---|
| `ticker` | Daily OHLCV + indicators | time, ticker, Close, MA50/200, D_RSI, D_MACDdiff, PE, NP_P0/P4, FSCORE, Volume_3M_P50, ICB_Code | 2014-01-02 → 2026-03-30 |
| `ticker_prune` | High-quality 449-mã subset | Same as ticker, partitioned + clustered | 2014+ → 2026-04-17 |
| `ticker_1m` | Rolling 1-month snapshot (live) | Same + extras | 2026-03-24 → 2026-05-08 |
| `vnindex_5state` | 5-state regime per session | time, state (1-5) | 2014+ → 2026-04-28 |
| `fa_ratings` | FA tier A-E + 7-axis scores | ticker, time, tier, total_score, score_quality… | through Q1 2026 |
| `ticker_financial` | Quarterly fundamentals | NP_P0..P7, Revenue_YoY_P0, ROIC_Trailing… | through 2026-05-08 |

**5-state mapping:**
- 1 = CRISIS (allocate 0%)
- 2 = BEAR (20%)
- 3 = NEUTRAL (70%)
- 4 = BULL (100%)
- 5 = EX-BULL (130%)

(BA-system entry **only** in states 3, 4, 5. CRISIS/BEAR → cash.)

---

## 2. Signal generation — v10 SQL

**Goal:** mỗi (ticker, date) → 1 score 0-194 → classify thành play_type tier.

### 2.1 TA score formula v10 (trên `tav2_bq.ticker`)

26 boolean conditions, cộng/trừ điểm:

| Component | Condition | Points |
|---|---|---|
| **Momentum (Technical)** | | |
| RSI strong | `D_RSI > 0.50` | +25 |
| Uptrend | `Close > MA50 AND MA50 > MA200` | +25 |
| Volume confirm | `Volume ≥ Vol_3M_P50 × 1.3 AND Close > Close_T1` | +20 |
| MACD positive | `D_MACDdiff > 0` | +15 |
| Above MA20 | `Close > MA20` | +15 |
| RSI extreme | `D_RSI > 0.75` | +5 |
| RSI Max1W | `D_RSI_Max1W > 0.65` | +5 |
| Fresh 3Y high | `ID_HI_3Y ≤ 5` | +8 |
| RSI weak penalty | `D_RSI < 0.30` | -10 |
| **Valuation (PE z-score)** | | |
| Cheap PE | `PE < PE_MA5Y - 0.5×PE_SD5Y` | +15 |
| Expensive PE | `PE > PE_MA5Y + 1.0×PE_SD5Y` | -15 |
| **VNINDEX context** | | |
| VNI 3M strong | `VNINDEX_RSI_Max3M > 0.65` | +10 |
| **FA quality** | | |
| FSCORE elite | `FSCORE >= 8` | +10 |
| NP YoY strong | `NP_P0 > 1.5 × NP_P4` | +8 |
| NP YoY decline | `NP_P0 < 0.7 × NP_P4` | -8 |
| NP QoQ accel | `NP_P0 > 1.2 × NP_P1` | +8 |
| **Sector tilt** | | |
| Fin/RE or Tech (sec 8,9) | `ICB_Code/1000 ∈ {8, 9}` | +5 |
| Health or Utilities (sec 4,7) | `ICB_Code/1000 ∈ {4, 7}` | -5 |
| **Trend confirmation (MA50 slope)** | | |
| MA50 rising | `MA50 > MA50_T1` | +5 |
| MA50 strong | `MA50 > MA50_T1 × 1.005` | +5 |
| MA50 falling | `MA50 < MA50_T1` | -5 |
| Drawdown deep | `Close/HI_3M_T1 < 0.85` | -10 |
| **v10 breakthrough (round 12)** | | |
| **Fin/RE × FA-D bonus** | `sector=8 AND fa_tier='D'` | **+10** |
| **Fin/RE × FA-A penalty** | `sector=8 AND fa_tier='A'` | **-10** |

### 2.2 Tier classification SQL (CASE WHEN priority order)

Score + state + FA tier → play_type:

```sql
CASE
  -- Block in BEAR/CRISIS
  WHEN state5 IN (1, 2) THEN 'AVOID_bear'
  WHEN fa_tier = 'E' THEN 'AVOID_faE'

  -- BA-CORE tiers (entered in production books)
  WHEN ta >= 170 AND state5 IN (4,5) AND fa_tier IN ('C','D')   THEN 'MEGA'
  WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('C','D')   THEN 'MOMENTUM'
  WHEN ta >= 155 AND state5 = 3   AND fa_tier IN ('C','D')   THEN 'MOMENTUM_N'
  WHEN ta >= 140 AND state5 IN (4,5)                          THEN 'MOMENTUM_S'
  WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5)
       AND ((np_yoy > 0.20) OR (rev_yoy > 0.20))               THEN 'DEEP_VALUE_RECOVERY'

  -- Informational (NOT entered in production)
  WHEN ta >= 170 AND state5 IN (4,5)                          THEN 'S_PRO'
  WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('A','B')  THEN 'MOMENTUM_QUALITY'
  WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95
       AND state5 IN (3,4,5) AND NOT warn_ext                  THEN 'COMPOUNDER_BUY'
  WHEN ta >= 125 AND state5 IN (4,5)                          THEN 'MOMENTUM_A'
  WHEN ta >= 140 AND state5 = 3                               THEN 'MOMENTUM_S_N'
  WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130          THEN 'COMPOUNDER_HOLD'
  WHEN fa_tier IN ('A','B')                                   THEN 'WAIT'
  ELSE 'PASS'
END
```

### 2.3 Liquidity filter (final WHERE)

`Volume_3M_P50 × Close >= 1B VND` (median daily turnover ≥ 1 tỷ VND). Rejects illiquid stocks.

### 2.4 Universe scope

`AND t.ticker IN (SELECT DISTINCT ticker FROM ticker_prune)` — restrict to 449 quality tickers.

---

## 3. Production books (the 50/50 split)

Strategy: **50% BAL + 50% VN30** (validated round-12 ULTIMATE).

### Book A — BAL+Fin/RE-max-4 (50% NAV)
- Universe: full `ticker_prune` (449 tickers)
- BA-core tiers: `[MEGA, MOMENTUM, MOMENTUM_N, MOMENTUM_S, DEEP_VALUE_RECOVERY]`
- Sector cap: **Fin/RE (sector 8) max 4 positions**
- Other sectors: unlimited

### Book B — VN30_BAL (50% NAV)
- Universe: top 30 tickers by avg liquidity 2020-2025
  - List: CTG, DGC, DIG, DXG, FPT, GEX, HAG, HPG, HSG, KBC, MBB, MSN, MWG, NKG, NVL, PDR, POW, PVD, PVS, SHB, SHS, SSI, STB, TCB, VHM, VIX, VND, VNM, VPB, VRE
- Same BA-core tiers
- No sector cap (VN30 inherently diversified)

Each book runs **independently** at full capital → NAVs combined ex-post (50% × NAV_A + 50% × NAV_B).

---

## 4. Day-by-day simulation engine — `simulate()` function

**Input:** signals_df, prices, vni_dates, PM params, liquidity params

**Step-by-step daily loop** (for each `today` in `vni_dates`):

### Step 1: Mark-to-market
```
for each open position:
  pos.last_price = today's close
  pos.peak_price = max(peak_price, today's close)
  pos.days_held += 1
```

### Step 2: Check exits (only if `days_held >= MIN_HOLD=2`)

Order of exit checks per position:
1. **TIME exit:** `days_held >= 45` → close
2. **STOP exit:** `(last_price/entry_price - 1) <= -0.20` → close
3. (Optional) Trailing stop, partial sells — disabled in production

### Step 3a: Execute partial sells — N/A in production

### Step 3b: Execute full closes
For each `(ticker, reason)` to close:
- gross = shares × cur_price
- **Tiered exit slippage** (round 10): if position > 5/10/20% of ADV → +0.1%/0.3%/0.5% extra slip
- proceeds = gross × (1 - 0.001 TC_SELL) × (1 - 0.001 CG_TAX) × (1 - 0.001 SLIPPAGE) × (1 - extra_slip)
- cash += proceeds
- If reason ∈ {STOP, TRAIL} → add ticker to **blacklist for 20 days** (BL20)
- delete position

### Step 4: Cash earns deposit rate (3%/yr → daily compound)
```
cash *= (1 + 0.03/252)
```

### Step 5: Decrement blacklist counters

### Step 6: Execute pending entries (multi-day fill capable)

Pending entries created when signals fired previously (T+1 entry rule).

For each pending entry that's eligible today:
1. **Skip** if ticker already in positions or blacklist
2. **Get today's price** — if None, carry over (max 5 days fill window)
3. **First-fill checks** (only on initial day):
   - Sector limit: if `Fin/RE positions >= 4` → skip
   - Slot check: if `len(positions) >= 10` → skip (no eviction in production)
   - **Compute target_value**: `cur_NAV / max_positions` = NAV/10 (equal-weight 10%)
4. **Liquidity-aware sizing**:
   - `max_buy_value_today = today_volume × Close × 20% (liquidity_volume_pct)`
   - `today_buy_value = min(target_remaining, max_buy_value_today)`
   - Multi-day fill: spread purchase over up to 5 days if order is large vs ADV
5. **Execute buy:**
   - shares = today_buy_value / (price × buy_cost_factor)
   - buy_cost_factor = (1 + 0.001 TC_BUY) × (1 + 0.001 SLIPPAGE)
   - cash -= shares × price × buy_cost_factor
   - Update entry's `filled_shares` + `filled_cost`
6. **Finalize position** when fully filled OR fill window expires:
   - `entry_price = filled_cost / filled_shares` (weighted avg)
   - Initial peak_price = entry_price

### Step 7: Add new signals to pending_entries
Today's signals (already known from signal_df) → schedule T+1 fill:
```
pending_entries.append({
  ticker, play_type, ta_score,
  exec_start_date = next_trading_day,
  filled_shares=0, filled_cost=0,
  days_filling=0,
})
```
Sort by TIER_PRIORITY (MEGA=100 > MOMENTUM=85 > … DVR=55) when multiple signals fire same day.

### Step 8: Compute today's NAV
```
NAV = cash + sum(pos.shares × pos.last_price for pos in positions)
       + sum(entry.filled_cost for entry in pending_entries if filled_shares > 0)
```

### Step 9: Append to nav_history `[(today, NAV)]`

---

## 5. Realistic friction parameters (production)

| Parameter | Value | Source |
|---|---|---|
| TC_BUY | 0.1% per trade | VN brokerage average |
| TC_SELL | 0.1% per trade | |
| CG_TAX | 0.1% on sells | VN capital gains tax |
| SLIPPAGE | 0.1% per side | Empirical (round 5) |
| Exit_slippage_tiered | True | round 10 — extra +0.1%/0.3%/0.5% if position > 5/10/20% ADV |
| MIN_HOLD | 2 sessions | T+3 settlement rule (cannot sell < 2 sessions after buy close) |
| HOLD_DAYS | 45 | Round 4-5 confirmed optimal |
| STOP_LOSS | -20% | Round 14/15 — kept conservative; -25% loses -2.97pp in 2021-2023 crash |
| BL20 (blacklist) | 20 sessions | Round 7 — +0.6pp CAGR for BAL |
| MAX_POSITIONS | 10 | Round 4 |
| LIQ_FLOOR | 1B VND/day | Memory: median ADV requirement |
| LIQUIDITY_VOLUME_PCT | 20% of ADV/day | Round 8 — capacity-aware sizing |
| MAX_FILL_DAYS | 5 | Round 8 |
| DEPOSIT_R | 3%/yr | Round-9 realistic VN non-term deposit |
| INIT_NAV (per book) | 50e9 (50B VND) | Production target scale |

---

## 6. Aggregation — combine BAL_Fin4 + VN30_BAL

After both books run independently:
```python
nav_combined = 0.5 × (nav_BAL / init_BAL) + 0.5 × (nav_VN30 / init_VN30)
```

Both NAVs normalized to start=1.0, then weighted average.

(Memory: round-13 confirmed 50/50 split is Pareto-optimal across all NAV scales 1B-200B; 200B+ shifts to 100% VN30.)

---

## 7. Metrics computation — `metrics()` function

| Metric | Formula |
|---|---|
| **CAGR** | `(NAV_end / NAV_start)^(1/years) - 1` (calendar years, not session count) |
| **Sharpe** | `mean(rets) / std(rets) × √(SPY)` where `SPY = n_sessions/years` |
| **Sortino** | Same numerator, denominator = std of negative rets only |
| **MaxDD** | `min((NAV_t - cummax(NAV))/cummax(NAV))` |
| **Calmar** | `CAGR / |MaxDD|` |
| **Q-Win** | `% quarters with positive return` |

---

## 8. Live engine workflow (`recommend_holistic.py`)

Daily routine (post-14:50 close):

```
[1/4] Run TA v10 SQL on tav2_bq.ticker for target_date → ta_df
[2/4] Load fundamental_rating_all.csv → fa_df (latest tier per ticker)
[3/4] Query VN30 universe (top 30 by avg liquidity 2020-2025)
[4/4] Cross-reference + classify into play_types

For state ∈ {1, 2}:  print BEAR/CRISIS message, BA-system → cash. F-overlay shows SHORT VN30F.
For state ∈ {3, 4, 5}:
  Build BAL book = top 10 BA-core picks with sector 8 cap = 4
  Build VN30 book = top 10 BA-core picks from VN30 set, no sector cap
  Print both books
  Print F-overlay status (target VN30F position based on F_HAdapted map)

Save: holistic_<date>.csv (full universe), ba_book_bal_<date>.csv, ba_book_vn30_<date>.csv
```

**Execution next session (T+1):**
- Buy each book pick at 5% NAV (=10% × 50% book)
- Stop loss -20% from entry, hold 45d, BL20 after stops

---

## 9. Reproducibility checklist

Để reproduce production performance từ scratch:

```bash
# 1. Verify data freshness
bq query --use_legacy_sql=false 'SELECT MAX(time) FROM tav2_bq.ticker'
# Should be ≥ 2026-03-30 for full backtest

# 2. Run a single config
python simulate_holistic_nav.py    # default: BAL strategy 1B
# (or use test_round12_v10_hybrid.py for the ULTIMATE 50/50 setup)

# 3. Run live engine (today)
python recommend_holistic.py

# 4. Backtest custom variant
python -c "
from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY
from test_round14_stability import SIGNAL_V10
sig = bq(SIGNAL_V10.format(start='2014-01-01', end='2026-03-30'))
... # see test_round12_v10_hybrid.py for full pattern
"
```

Expected metrics from full reproduction:
- BAL_Fin4 alone (50B): CAGR ~17.97% / Sharpe ~1.12 / DD ~-20%
- VN30_BAL (50B): CAGR ~16% / Sharpe ~1.05 / DD ~-16%
- 50/50 combined: **CAGR ~17.15% / Sharpe ~1.21 / DD ~-14.5%**

---

## 10. Common pitfalls when reproducing

1. **`ticker_1m` ≠ `ticker`** — `ticker_1m` is a rolling 1-month live snapshot; `ticker` is canonical history. Use `ticker_1m` only for live signals after `ticker.MAX(time)`.

2. **`risk_rating` table has duplicates** — always `GROUP BY` or `SELECT DISTINCT` when joining.

3. **Table/column name collision** — `risk_rating`, `ticker` cũng là column names. Always alias tables: `t.Risk_Rating` not just `Risk_Rating` (BQ resolves to row struct otherwise).

4. **Forward-looking columns** — `profit_2W`, `profit_1M`, `profit_2M`, `profit_3M` are training labels. **Never** use as live filters (they leak future).

5. **FA join window** — `fa_ratings` updates quarterly; live SQL uses 30-day or 90-day join window. Production scripts use 90d to capture latest Q reports.

6. **5-state has 7-day MIN_STAY smoothing** — state changes confirmed only after 7 sessions. Don't expect immediate signal on regime shift.

7. **End-of-period biases** — backtest END_DATE in old rounds was 2026-01-16 (missed recent BEAR Mar-Apr 2026). Use 2026-03-30 for fresh tests.

8. **NAV path is single-path simulation, not Monte Carlo** — confidence intervals require bootstrap (round-15 stress test only does single-event shocks).

---

## 11. File reference map

```
simulate_holistic_nav.py        Sim engine (single-book NAV)
recommend_holistic.py           Live engine (daily)

test_round12_v10_hybrid.py      v10 + 50/50 split breakthrough
test_round13_ultimate.py        Multi-NAV + rolling + DD analysis
test_round14_stability.py       Sector + day/month + PM variants
test_round15_tactical.py        Calendar tactics (rejected)
test_round16.py                 Tier sizing + EX-BULL threshold (rejected)
test_round17.py                 State-exit + profit-target (rejected)

test_stop_validation.py         Multi-period stop loss grid
test_f_ba_mix.py                F-system + BA mix grid
quarterly_walkforward.py        Forward QWF tracking
layer3_paper_trade.py           Paper-trade tracker

VNINDEX.csv                     Local VNINDEX history (2000+)
fundamental_rating_all.csv      FA snapshot cache
holistic_<date>.csv             Daily watchlist output
ba_book_{bal,vn30}_<date>.csv   Daily book picks
qwf_tracking_log.csv            Quarterly tracking log
round{12-17}_*.csv              Per-round result CSVs
```

---

## 12. Key design lessons (from 17 rounds)

1. **Equal-weight beats tier-weighted** — DVR (62% trades, +7.5% avg) carries compounding; concentrating into MEGA wastes slots
2. **TIME exit dominates (88.7%)** — system signals have ~45-day half-life
3. **Stop -20% optimal** — looser stops only win in pure-bull (2021-2023 loses -2.97pp)
4. **5-state regime > price-based filters** — manually filtering by month/day fails (correlation, not causation)
5. **Capacity issue is positive** — mediocre signals fill slots and contribute meaningfully; "drop weak tiers" rejected
6. **Liquidity-aware sizing scales gracefully** — 50B realistic, 200B+ shift to VN30 only
7. **Compounding > risk overlays** — every defensive overlay (trail, partial, eviction, state-exit, profit-target) cuts returns more than DD savings
8. **Sector tilt has structural pull** — Fin/RE = 54% of trades; cap at 4 (round 10 breakthrough)
9. **FA × Sector inversion** — Fin/RE × FA-D rallies harder than Fin/RE × FA-A (priced-in vs recovery setup)
10. **Walk-forward shows alpha is real** — OOS 2020-2026 Sharpe 1.35, IS 2014-2019 Sharpe 0.85; system improves over time, not overfit
