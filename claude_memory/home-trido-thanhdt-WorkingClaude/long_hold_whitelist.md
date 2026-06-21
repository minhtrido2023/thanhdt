---
name: Long-Hold Quality Whitelist (Core compounders for BA-system)
description: 6-8 super compounders to HOLD without 45d cohort cutting. Identified from 12y A-tier consistency + multi-bagger price appreciation. Includes DGC special-case political-risk overlay.
type: project
originSessionId: 70c13426-2492-456b-9547-d14c8cf8fcb7
---
# Long-Hold Quality Whitelist

**Created**: 2026-05-15 | **Source**: `analyze_lh_super_stocks.py`, `find_true_compounders.py`
**Purpose**: Identify "core" positions that BA-system should HOLD indefinitely while fundamentals remain strong, overriding default 45d cohort exit.

## Core thesis

LH analysis showed many SUPER COMPOUNDERS were CUT by 45d cohort rotation, losing 600-1200% upside (MBB +1011%, FPT +829%, CEO +1202% post-exit gains). BA-system's 45d hold is appropriate for momentum picks but DESTROYS multi-year compounders.

**Solution**: Core-Satellite architecture:
- **Core (Whitelist)**: 40-50% NAV in 6-8 quality compounders, no time-based selling
- **Satellite (BA-rotation)**: 50-60% NAV in BA-system 45d cohort rotation
- This preserves BA's regime-aware momentum capture + lets winners compound

## Selection criteria (for inclusion)

A stock qualifies for whitelist if it meets **ALL**:
1. ≥60% A-tier consistency over ≥7 years history
2. ≥3× price multiple from first A-tier entry to peak
3. CAGR ≥15% over the hold period
4. Still A-tier in latest quarter (or special exception)
5. NOT in active commodity-peak cycle (per `lh_v3_sector_cycle.csv`)

## ✅ TIER 1 — HARD WHITELIST (5 names, high conviction)

These are PROVEN multi-year compounders with strong FA consistency.

### 1. MBB (Military Bank) — `BANK`
- **% A-tier**: 76.6% (36 of 47 quarters)
- **12y multiple**: 11.52× (2014→2026)
- **CAGR**: +22.5%
- **Thesis**: Top-tier private bank with consistent ROE 18-22%, MBs digital banking leadership, CASA ratio top, MB Group ecosystem (MBS, MBLand). Re-rated upward as private bank dominance grows.
- **Sizing**: 8-10% NAV (largest)
- **Exit triggers**: FA tier drops to C (banking quality regression), NPL ratio >2.5%, ROE drops <14% sustained 2Q

### 2. FPT (FPT Corp) — `IT_SERVICES`
- **% A-tier**: 78.0% (39 of 50 quarters)
- **12y multiple**: 11.17×
- **CAGR**: +21.7%
- **Thesis**: Vietnam's IT outsourcing champion. Foreign revenue growing 30%/yr. AI/cloud transition tailwind. Telecom + Edu segments adding stability.
- **Sizing**: 8-10% NAV (co-largest)
- **Exit triggers**: NP_TTM growth <10% for 2Q, FA drops to C, FPT Software pipeline contraction
- **Note**: 2025-Q1 corrected -47% from peak — currently at 2024-08 levels. FA still A. Mean revert candidate, but wait for clear catalyst (Q2 2026 earnings rebound).

### 3. CTR (Viettel Construction) — `TELECOM_TOWER`
- **% A-tier**: 82.1% (the MOST consistent quality)
- **6.8y multiple**: 4.68×
- **CAGR**: +25.6%
- **Thesis**: Telecom tower buildout, Viettel infrastructure, recurring revenue model. 5G rollout tailwind 2026-2028.
- **Sizing**: 6-8% NAV
- **Exit triggers**: FA drops to C, Viettel capex cut, government policy change

### 4. BMP (Binh Minh Plastics) — `CONSUMER`
- **% A-tier**: 76.7%
- **10.5y multiple**: 5.27×
- **CAGR**: +17.1%
- **Thesis**: Plastic pipe market leader, defensive consumer staple, Thai parent (SCG) backed, consistent dividend. Construction + infrastructure tailwind.
- **Sizing**: 5-7% NAV (defensive anchor)
- **Exit triggers**: FA drops to C, dividend cut, PVC raw material structural shift

### 5. MCH (Masan Consumer) — `CONSUMER`
- **% A-tier**: 72.2%
- **5.5y multiple**: 3.26×
- **CAGR**: +23.9%
- **Thesis**: Masan group consumer brands portfolio (Chinsu, Omachi, Tam Thai Tu...). Domestic consumption growth. Premium brand pricing power.
- **Sizing**: 5-7% NAV
- **Exit triggers**: FA drops to C, gross margin compression sustained, Masan Group governance issue

## 🟡 TIER 2 — CONDITIONAL WHITELIST (3 names, monitor closely)

These qualify on data but have specific risks requiring quarterly review.

### 6. HDG (Ha Do Group) — `REAL_ESTATE_DEV`
- **% A-tier**: 62.9%
- **11.8y multiple**: 6.13×
- **CAGR**: +16.6%
- **Thesis**: Diversified — RE projects + renewable energy + retail (HEM). Solar/wind portfolio recurring revenue. Solid balance sheet.
- **Sizing**: 4-6% NAV
- **Exit triggers**: FA drops to C, renewable tariff cut, RE deferred recognition
- **Watch**: VN RE sector cyclical; reduce position if VN RE Index correlation increases

### 7. CSV (Casumina) — `CHEMICALS`
- **% A-tier**: 63.0%
- **9.8y multiple**: 4.59×
- **CAGR**: +16.9%
- **Thesis**: Specialty chemicals (caustic soda, chlorine), not commodity-grade. Domestic demand growth. Limited substitution.
- **Sizing**: 4-5% NAV
- **Exit triggers**: FA drops to C, gas price spike (input), commodity peak cycle
- **Watch**: Currently chemical group in downcycle (-0.50). CSV less affected than DGC but monitor

### 8. ⚠️ DGC (Duc Giang Chemicals) — `CHEMICALS_PHOSPHORUS` — SPECIAL CASE
- **% A-tier**: 73.1% (high quality)
- **7.3y multiple**: 5.11× (from first A) — currently DOWN -62% from June 2024 peak
- **CAGR**: +25.1% (from entry)
- **Current price** (~2026-05): 49,500 VND (from peak 128,310)
- **Thesis**: Vietnam's only producer of yellow phosphorus (P4) at scale. Proprietary technology, production capability moat. P4 prices trending up per user observation.
- **Recent drawdown driver**: Political/criminal investigation of economic cases involving leadership — **NON-FUNDAMENTAL drawdown**
- **Mean-reversion thesis**: When political noise clears + P4 prices rise → multiple expansion + earnings rebound

#### DGC special-case rules

**Initial position**: 3-5% NAV (smaller than Tier 1 due to risk)

**Hold conditions** (continue holding while ALL true):
- FA tier remains A or B
- Political investigation hasn't resulted in operational disruption (production continues)
- P4 spot prices trend up or stable (need external commodity data source)
- No major management exit

**Re-entry / averaging-down triggers** (consider adding if existing position):
- FA tier confirmed A in next quarterly report (2026-Q2 release ~ Aug 2026)
- Price stabilizes above MA50 for 4+ weeks
- DGC reports Q2 earnings showing P4 unit prices recovered
- Political news cycle ends (no further investigation news for 6+ weeks)

**Hard exit triggers** (sell despite thesis):
- FA tier drops to C or below (fundamentals confirming damage)
- Production capacity reduced (factory shutdown, license revoked)
- NP_TTM growth < -40% YoY in 2 consecutive quarters
- Price breaks 30,000 VND (-77% from peak, structural break)

**Monitoring frequency**: weekly during political-risk period, otherwise quarterly

**Position sizing rule**: max 5% NAV (down from typical 6-8% Tier 1) due to idiosyncratic risk

## 🚫 NOT included in whitelist (despite A-tier history)

These showed A-tier consistency but FAIL price test or have specific concerns:

| Ticker | %A | Multiple | CAGR | Why not whitelist |
|---|---|---|---|---|
| **VNM** | 100% | 1.80× | +4.9% | Past peak 2018, mature/slowing — FA score doesn't catch structural shift |
| **SAB** | 86.5% | 0.45× | **-9.0%** | LOSING money — perfect FA but price down 55% (warning case) |
| **GAS** | 78% | 2.37× | +7.3% | Oil cyclical mature, peak earnings 2022 |
| **NCT** | 96.2% | 2.48× | +8.6% | Steady but slow — small position size constraint |
| **SCS** | 96% | 1.04× | +0.5% | Stagnating airport cargo |
| HPG | 44.9% | 8.63× | +19.6% | Cyclical commodity — handle as BA satellite |
| HAH | 30.4% | 7.33× | +48.7% | Shipping commodity peak risk |

## Hold management framework

### Per-position monitoring (monthly review)

For each whitelist holding, track:
1. **FA tier history**: any drop from A/B → flag
2. **NP_TTM growth (4Q TTM)**: must remain positive year-over-year
3. **Price drawdown from peak**: if >30% → investigate cause
4. **Relative strength vs VNI 1Y**: if -30pp underperform → review thesis
5. **Sector cycle position**: if commodity-cyclical at peak → reduce
6. **News flow**: management changes, regulatory, political (for DGC)

### Portfolio-level rules

- **Max whitelist allocation**: 50% NAV (rest in BA rotation)
- **Max single position**: 10% NAV (excluding DGC special at 5%)
- **Rebalance**: quarterly — if whitelist grew to >55% NAV, trim 10% from largest winners
- **Add new names**: only if existing position EXITS first (one-in, one-out)

### Default exit conditions (applies to ALL whitelist names)

Force sell if ANY:
1. FA tier drops to D or E (fundamental break)
2. Price drops > 50% from purchase price (-50% absolute)
3. NP_TTM declines > 30% YoY for 2 consecutive quarters
4. Major management/governance event (CEO ouster, fraud disclosure)
5. Sector regulation change destroying business model
6. VNI in CRISIS state (state=1) for 60+ days — protect capital

## Suggested deployment plan

**Phase 1 (today, 2026-05-15)**: Identify positions
- BA-system already running with full 100B NAV
- Identify which BA picks overlap with whitelist (likely MBB, FPT, BMP — banks/blue chips)
- Tag those as "core" — extend hold beyond 45d when they appear in BA picks

**Phase 2 (next 1-2 quarters)**: Build core
- Each quarter, allocate 5-10% NAV to whitelist names not yet held
- Target reach: 40-50% NAV in whitelist by end Q2 2027
- Remaining 50-60% NAV stays in BA rotation

**Phase 3 (steady state)**: Maintain
- Whitelist positions: review monthly, hold absent exit trigger
- BA satellite: normal 45d cohort rotation

### DGC specific actions

If user currently HOLDS DGC:
- Maintain position, don't sell despite -62% drawdown
- Wait for catalyst: Q2-Q3 2026 earnings (need to confirm P4 trend)
- DO NOT average down YET (price could break lower)
- Re-evaluate when: FA Q2 2026 confirms A tier + price > MA50 4 weeks

If user does NOT hold DGC:
- WAIT for clearer signal (price above MA50 sustained + P4 trend confirmed)
- Initial buy size: 2-3% NAV (small, can scale up later if thesis confirms)

## Tracking — `whitelist_positions.csv` (template)

```csv
ticker,tier,position_pct_nav,first_buy_dt,first_buy_px,current_px,unrealized_pct,fa_tier_latest,status,notes
MBB,Tier1,8%,2024-XX-XX,XXXX,25800,+XX%,A,HOLD,
FPT,Tier1,8%,2024-XX-XX,XXXX,70700,+XX%,A,HOLD,
CTR,Tier1,7%,2024-XX-XX,XXXX,85900,+XX%,A,HOLD,
BMP,Tier1,6%,2024-XX-XX,XXXX,160900,+XX%,A,HOLD,
MCH,Tier1,6%,2024-XX-XX,XXXX,146490,+XX%,A,HOLD,
HDG,Tier2,5%,2024-XX-XX,XXXX,24900,+XX%,A,WATCH,RE cycle monitor
CSV,Tier2,4%,2024-XX-XX,XXXX,26350,+XX%,A,WATCH,Chemical group downcycle
DGC,Special,3%,2024-XX-XX,XXXX,49500,-XX%,A,HOLD-MONITOR,Political risk + P4 catalyst pending
```

Total Tier1+Tier2+Special: 47% NAV (within 50% cap)
Remaining 53% NAV: BA satellite rotation

## Files referenced

- `analyze_lh_super_stocks.py` — initial trade analysis from LH v1 12y
- `find_true_compounders.py` — true compounder analysis (FA consistency + price multiple)
- `lh_v1_quality_consistency.csv` — A-tier consistency table
- `elite_compounders.csv` — short-listed elite names
- `lh_v3_sector_cycle.csv` — sector cycle monitoring data
- `cohort_cut_victims.csv` — analysis showing 600-1200% missed gains from cohort cutting

## Next steps

1. **Today**: User reviews this whitelist, confirms or modifies names
2. **Build monitoring script** `whitelist_monitor.py` — daily check FA tier + price levels + flag deterioration
3. **Quarterly review** at Q-end: re-run `find_true_compounders.py` with latest data, validate whitelist still holds
4. **Future BA v12 patch** (optional, requires canonical sim): encode whitelist as `whitelist_skip_45d_exit` rule in `recommend_holistic.py`
