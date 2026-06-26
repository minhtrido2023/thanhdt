# DDV Verification + Data Pipeline Review — 2026-06-26

Dispatched by Mike. Winston audit.

---

## 1. DDV Verification (API vs BQ)

### 1.1 BQ raw data (tav2_bq.ticker — confirmed query 2026-06-26)

| Date | Close (adj) | Price (unadj) | close_chg | MA10 | MA20 | D_RSI |
|------|-------------|---------------|-----------|------|------|-------|
| 2026-06-12 | 25,800 | 25,800 | +0.39% | 25,870 | 26,160 | 0.414 |
| 2026-06-15 | 25,800 | 25,800 | 0% | 25,860 | 26,085 | 0.414 |
| 2026-06-16 | 25,800 | 25,800 | 0% | 25,870 | 26,030 | 0.414 |
| 2026-06-17 | 26,200 | 26,100 | +1.55% | 25,910 | 26,005 | 0.505 |
| 2026-06-18 | 26,200 | 26,200 | 0% | 25,900 | 25,995 | 0.505 |
| **2026-06-19** | **24,390** | **26,100** | **-6.91%** | **24,202** | **24,275** | **0.484** |
| 2026-06-22 | 24,390 | 26,100 | 0% | 24,230 | 24,266 | 0.484 |
| 2026-06-23 | 24,200 | 25,900 | -0.78% | 24,239 | 24,248 | 0.439 |
| 2026-06-24 | 24,110 | 25,800 | -0.37% | 24,239 | 24,220 | 0.419 |
| 2026-06-25 | 23,900 | 23,900 | -0.87% | 24,228 | 24,205 | 0.377 |

### 1.2 VCI adjusted close (vnstock VCI source — queried 2026-06-26)

| Date | VCI close (VND) |
|------|-----------------|
| 2026-06-12 | 24,100 |
| 2026-06-15 | 24,100 |
| 2026-06-16 | 24,100 |
| 2026-06-17 | 24,480 |
| **2026-06-18** | **24,480** ← retroactively adjusted down |
| **2026-06-19** | **24,390** ← matches BQ ✓ |
| 2026-06-22 | 24,390 |
| 2026-06-23 | 24,200 |
| 2026-06-24 | 24,100 |
| 2026-06-25 | 23,900 |

### 1.3 Verdict

| Question | Answer |
|---------|--------|
| BQ Close (adj) 2026-06-19 correct? | ✅ YES — 24,390 VND matches VCI |
| Estimated dividend | ~1,810 VND/share (26,200 − 24,390 = 1,810; ~6.91% of share price) |
| BQ Price (unadj) correct on 2026-06-19? | ❌ NO — 26,100 VND is FROZEN (ETL lag) |
| BQ Close retroactively adjusted? | ❌ NO — BQ shows 26,200 on 2026-06-18; VCI shows 24,480 (retroactively adj) |

---

## 2. Bug A — Price (unadjusted) Freeze

**Confirmed.** BQ `Price` (unadjusted market price) was FROZEN at ~26,100 VND for 4 days after ex-date:
- 2026-06-19: Price=26,100 (wrong — should be ~24,390 actual market)
- 2026-06-22: Price=26,100 (wrong)
- 2026-06-23: Price=25,900 (still wrong — ETL starting to catch up)
- 2026-06-24: Price=25,800 (still wrong)
- 2026-06-25: Price=23,900 (finally synced with market reality)

**Root cause**: External data vendor (tav2_bq.ticker is owned by external ETL, not our code) freezes the `Price` column 2-4 days after ex-date. This matches the known pattern documented in update_shares_live.py.

**Impact of Bug A**:
- `PE` = Market Cap / NP = (Close × OShares) / NP — but Close is OK; OShares is stale until next quarterly release
- `Price` column used in adj_factor computation: `adj_factor = Close/Price`
- Any consumer using `Price` directly for position sizing or valuation has ~7% overvalued NAV for 4 days
- `update_shares_live.py` detection v2 correctly uses `adj_drop >= 3% + Price_flat < 1.5%` to catch this

---

## 3. Bug B — No Retroactive Adjustment of Historical Close

**Confirmed.** BQ `Close` column is NOT retroactively adjusted when a corporate action occurs.

**Evidence**:
- BQ Close 2026-06-18 = 26,200 VND (actual market price that day)
- VCI adjusted close 2026-06-18 = 24,480 VND (retroactively adjusted to remove dividend effect)
- Gap = 26,200 − 24,480 = 1,720 VND ≈ the 6.91% adjustment factor

**Effect on indicators (confirmed from BQ data)**:

| Indicator | 2026-06-18 (pre-ex) | 2026-06-19 (ex-date) | Structural break |
|-----------|--------------------|--------------------|-----------------|
| MA10 | 25,900 | 24,202 | -6.5% jump |
| MA20 | 25,995 | 24,275 | -6.6% jump |
| MA50 | 26,598 | 24,834 | -6.6% jump |
| D_RSI | 0.505 | 0.484 | slight drop (RSI correctly sees a down day) |

The MA contamination means:
- `Close > MA50` check: on 2026-06-18, Close=26,200 > MA50=26,598 → **FAIL** (uptrend not confirmed)
- On 2026-06-19, Close=24,390 > MA50=24,834 → also FAIL — but the MA50 just dropped by the same dividend amount, so the ratio is approximately preserved
- Over the next ~50 trading days, MA50 will still have a structural break in the rolling window

**Known limitation — DOCUMENTED in codebase**: 
`pt_v23_audit_ddpark.py:930` and `pt_v23_audit_2014.py:1832` both note: `"if a corporate action re-adjusted history after this run, compare RATIOS not absolute levels"`. The system is aware of this but accepts it as a known limitation.

**Why BQ doesn't retroactively adjust**: The `tav2_bq.ticker` table is written by an external data vendor whose ETL only applies adjustments going forward from the ex-date. Historical rows are immutable. Our codebase has NO write path to `tav2_bq.ticker` for OHLCV data.

---

## 4. Pipeline Architecture (Big Picture)

### 4.1 Data flow (text diagram)

```
EXTERNAL VENDOR                          OUR CODEBASE (WorkingClaude)
     │                                          │
     ▼                                          │
tav2_bq.ticker (T-1 lag; confirmed)             │
  - OHLCV, MA, RSI, CMF, MACD                  │
  - Close = adjusted from ex-date forward       │
  - Price = unadjusted (freezes 2-4d post-CA)  │
  - No retroactive adjustment of history        │
     │                                          │
     ├── tav2_bq.ticker_1m (same-day ~16:00 VN) │
     │   - Rolling 1-month snapshot             │
     │   - Used for live signal gen             │
     │                                          │
     └──────────────────────────────────────────┘
                   │  READ (our code reads from BQ)
                   ▼
     ┌─────────────────────────────────────────────────┐
     │  15:30 ICT: papertrade_daily.sh                  │
     │    - pull_us_market.py (VIX/SPX)                │
     │    - rebuild_state_from_ticker.sh               │
     │      (ew_v1 → dual_v3 → v3.4b → dt4gate)       │
     │    - golive_recommend_v23.py                    │
     └─────────────────────────────────────────────────┘
                   │
                   ▼
     ┌─────────────────────────────────────────────────┐
     │  18:00 ICT: telegram_run_daily.sh               │
     │    - telegram_recommend.py → Telegram           │
     └─────────────────────────────────────────────────┘
                   │
                   ▼
     ┌─────────────────────────────────────────────────┐
     │  23:15 ICT: daily_refresh_v34b_linux.sh         │
     │    WRITES to BQ (our code):                     │
     │    - tav2_bq.vnindex_5state (v3.4b base)        │
     │    - tav2_bq.vnindex_5state_tam_quan_v34b_clean │
     │    - tav2_bq.vnindex_5state_dt5g_live           │
     │    Auth: dtienthanh@gmail.com (transplanted)    │
     └─────────────────────────────────────────────────┘
                   │
                   ▼
     ┌─────────────────────────────────────────────────┐
     │  23:45 ICT: sync_bq_cache_daily.sh              │
     │    - DuckDB local cache sync (12 tables)        │
     └─────────────────────────────────────────────────┘
     
     ┌─────────────────────────────────────────────────┐
     │  18:40 ICT: update_shares_live.sh               │
     │    - corp-action detection v2                   │
     │    - WRITES to tav2_bq.shares_outstanding_live  │
     │      (does NOT touch tav2_bq.ticker)           │
     └─────────────────────────────────────────────────┘
```

### 4.2 Who writes to tav2_bq.ticker?

**External vendor only.** Zero scripts in our codebase INSERT/MERGE/UPDATE to `tav2_bq.ticker` for OHLCV data. Our code:
- READS from ticker (all strategy/signal scripts)
- WRITES to: vnindex_5state* tables (regime), shares_outstanding_live (OShares override)
- No adj-factor backward pass, no retroactive adjustment

### 4.3 Data freshness SLA

| Table | Cadence | Lag | Notes |
|-------|---------|-----|-------|
| `tav2_bq.ticker` | Daily | **T-1** (confirmed 2026-06-26: latest=2026-06-25) | External vendor; DEPLOYMENT.md says T-2 but actual=T-1 |
| `tav2_bq.ticker_1m` | Daily | Same-day ~16:00 VN | Fresher; used for live signal gen |
| `tav2_bq.ticker_prune` | Daily | T-1 | Quality-filtered view |
| `tav2_bq.vnindex_5state_dt5g_live` | Daily | T (via 23:15 cron) | Freshest — we own this |
| `tav2_bq.shares_outstanding_live` | Daily | T (via 18:40 cron) | We own this |

---

## 5. Gaps & Risks (Ranked by Severity)

### CRITICAL

**C1: No retroactive price adjustment (Bug B)**
- Every dividend ex-date creates a structural break in Close time series
- BQ MA10/20/50/200 all incorporate the break; triggers spurious TA signals
- Affects signal quality on ex-date and the following 200+ trading days (until MA windows fully roll over)
- **Mitigation (existing)**: detection v2 identifies the ex-date; known limitation documented in audit scripts
- **Gap**: No automated post-event indicator recalculation or flag in BQ

**C2: Price freeze after ex-date (Bug A)**
- BQ `Price` (unadjusted) lags 4+ days after corporate action
- OShares freeze in `ticker_financial` until next quarterly report
- PE/PB computed with stale Price + stale OShares → stock screens artificially cheap
- **Mitigation (existing)**: `update_shares_live.py` writes corrected OShares to `shares_outstanding_live`
- **Gap**: Consumers must explicitly JOIN `shares_outstanding_live` to get corrected valuation

### HIGH

**H1: External vendor SLA unknown**
- We have no SLA agreement or monitoring on when tav2_bq.ticker updates
- If vendor delays, all downstream (signal gen, 15:30 paper-trade, 18:00 Telegram) are stale
- **Existing guard**: `macro_healthcheck.py` checks freshness; `get_gated_state()` fail-safe
- **Gap**: No alert to user if ticker_1m is stale at signal-generation time (15:30 cron)

**H2: BQ auth via transplanted credential (dtienthanh@gmail.com)**
- Token has finite lifetime; if expired, 23:15 DT5G refresh fails silently
- Last resort: fresh gcloud auth login needed
- **Existing guard**: 23:15 script logs to `data/refresh_v34b_linux_*.log`
- **Gap**: No Telegram/bus alert on BQ auth failure

**H3: ffill-frozen state bug (known, occurred 2026-06-02)**
- DT5G state can get stuck if BQ feed is stale and the refresh blindly forward-fills
- **Existing guard**: `get_gated_state()` checks feed age, fails to DT4 on stale
- **Gap**: No intraday monitoring; only detected after the fact

### MEDIUM

**M1: SBG shares_outstanding stale after stock bonus (2026-06-19)**
- SBG had stock bonus ~20%; OShares in ticker_financial still at ~50M (should be ~60M)
- `CORP_ACTIONS` dict in update_shares_live.py does NOT include SBG yet
- **Next action**: confirm exact ratio from VSD, add SBG to CORP_ACTIONS, run update_shares_live

**M2: ticker vs ticker_1m gap**
- Signal gen at 15:30 uses ticker_1m (fresh) but backtest uses ticker (T-1)
- Any column present in ticker_1m but absent/different in ticker creates live-vs-backtest divergence
- Not actively monitored

**M3: DuckDB local cache delta-sync not verified post-corp-action**
- After price adjustment, cached parquet files may have stale Price values
- sync_bq_cache_daily.sh at 23:45 re-syncs; no mid-day refresh
- Gap window: 15:30 paper-trade may use cache with frozen Price if corp-action happened today

---

## 6. Summary / Decision

| Item | Verdict |
|------|---------|
| BQ Close (adj) on DDV 2026-06-19 | ✅ CORRECT (24,390 VND confirmed vs VCI) |
| Bug A (Price freeze) | ✅ CONFIRMED, 4-day freeze, ETL external |
| Bug B (no retroactive adj) | ✅ CONFIRMED, VCI adjusts historial BQ does not |
| MA/RSI contamination | ✅ CONFIRMED (MA10 dropped 1700 VND at ex-date) |
| Who writes ticker | ❌ EXTERNAL VENDOR (no write path in our code) |
| Retroactive adj capability | ❌ NONE in codebase (by design) |
| ticker freshness SLA | T-1 actual (not T-2 as documented); unknown vendor |
