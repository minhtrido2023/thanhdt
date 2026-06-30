# Real Estate Valuation Framework — VN property compounders (2 sub-sectors)

Job Taylor_20260630_053151 (sector-by-sector compounder book; RE after banking). Companion to
`retail_valuation_framework.md` / `banking_valuation_framework.md`. Backtest: `re_compounder_screen.py`
→ `data/re_compounder_{resid_monthly.csv, indust_monthly.csv, verdict.json}`.

RE is the hardest sector because **two structurally different businesses sit under one ICB code (8633)**:
- **A — Residential / urban developers** (VHM, VIC, KDH, NLG, NVL, TCH, DXG, PDR, DIG, HDG…): deep
  cyclical, handover-based revenue, credit-cycle = the dominant risk.
- **B — Industrial parks** (NTC, LHG, IDC, KBC, SZC, BCM, SIP, D2D, TIP…): REIT-like, stable lease
  income, high ROIC, low growth, **structurally illiquid** (NTC ADV 2.9B/day in 2017 — buying 10B = weeks).

BQ has **no sub-split** of 8633 → I maintain an explicit industrial-park ticker list; everything else in
8633 is residential.

## Part 1 — Why RE is valued differently (international practice)

### Residential developers
- Primary metric internationally = **discount to NAV** (NAV = land bank + inventory − net debt). Land bank
  is **NOT in BQ** → **P/B is the proxy**: book carries land/inventory at cost, so P/B < 1.0 ≈ buying land
  below carrying value; <1.5 = the distress zone. P/B is primary.
- **Revenue is handover-recognised, NOT pre-sale** → cripplingly lumpy (VHM NP swings 2.3T↔12T q/q). So
  **`Revenue_YoY` is USELESS here** (the generic-compounder Rev-persistence gate breaks). Use NP_P0>0 (level)
  and **GPM trajectory** (project profitability) instead of revenue growth.
- **Leverage + interest coverage = survival.** Cycle risk *is* credit risk. The single most important
  exclusion: a cheap-looking P/B sitting on un-payable debt (NVL). Gates: `Debt_Eq_P0`, `IntCov_P0`.
- **CF_OA turning positive** signals the cycle turn — but during the build phase CF_OA is structurally
  NEGATIVE and lumpy (cash into projects: VHM −5.4T at its 2023 trough). So CF_OA is **NOT a clean entry
  gate** (it would exclude the blue-chips mid-build); it's a confirmation lens, not a filter.
- **ROIC is distorted by the land bank** (huge invested capital carried at cost, revenue recognised years
  later) → use **ROE5Y / through-cycle ROE** for quality, not ROIC.
- **P/S is meaningless** (lumpy handover revenue, no recurring "sales").
- **Best entry = AFTER credit tightening (distress), BEFORE monetary easing** → P/B low + NP still positive
  + interest still covered. Confirmed by the backlook: the great entries cluster in **2020 (COVID)** and
  **2022Q4–2023Q1 (the bond/credit crunch)**; at cycle peaks (2019, 2021) almost nothing is cheap.

### Industrial parks (REIT-like)
- Valuation like a **REIT: P/B + DY (dividend yield) primary.** Stable lease income → ROIC5Y meaningful and
  high; growth low.
- **`Debt_Eq` / `IntCov` are MISLEADING for IPs**: long-term prepaid land-lease revenue is booked as a
  *liability* (deferred revenue), so reported Debt_Eq looks huge (NTC 6.0) and IntCov goes negative — a
  reporting artifact, **not** financial distress. → **Do NOT apply the residential leverage gates to IPs.**
- **Liquidity is the binding constraint** — NTC/LHG/D2D/TIP all trade <3B VND/day. ADV must be flagged, not
  silently ignored; position sizing is the real limiter, not signal.

## Part 2 — BQ column map
| Role | Residential | Industrial | Avoid (and why) |
|---|---|---|---|
| Valuation primary | `PB` | `PB`, `DY` | `PS` (lumpy handover rev), `PE` (cycle-noisy) |
| Survival | `Debt_Eq_P0`, `IntCov_P0` | *(N/A — deferred-lease artifact)* | — |
| Profitability/level | `NP_P0`, `NP_P4` | `NP_P0/P4` | `Revenue_YoY*` (handover-lumpy) |
| Margin trajectory | `GPM_P0 − GPM_P4` | `GPM_P0` | — |
| Through-cycle quality | `ROE5Y`, `ROE_Min3Y` | `ROIC5Y`, `ROE5Y` | `ROIC*` for residential (land-bank distortion) |
| Cycle-turn confirm | `CF_OA_P0` (lens, not gate) | — | — |
| Liquidity flag | `Trading_Value_1M_P50` | `Trading_Value_1M_P50` (**FLAG <10B**) | — |
| Universe id | `ICB_Code = 8633` ∖ IP-list | `ICB_Code = 8633` ∩ IP-list | — |

Industrial-park ticker list (explicit): `KBC, IDC, SZC, BCM, SIP, NTC, LHG, D2D, TIP, IDV, SZL, SNZ`.

## Part 3 — Backlook at the entry/danger points (ticker_financial cache)
**Residential — the 2022Q4–2023Q1 distress trough (the textbook entry) + the leverage trap:**
| name | qtr | PB | Debt_Eq | IntCov | NP_P0 | GPM | ROE5Y | read |
|---|---|---|---|---|---|---|---|---|
| **VHM** | 2023Q1 | **1.37** | 1.35 | **23.1** | +11.9T | 0.40 | 0.37 | blue-chip cheap-for-quality. Interest covered 23×. ✓ entry |
| **NLG** | 2022Q4 | **0.82** | 1.03 | **26.3** | +437B | 0.46 | 0.14 | clean deleverager, deep value. ✓ entry (trough 2022Q3 PB 0.73) |
| **TCH** | 2022Q4 | **0.44** | **0.25** | 4.8 | +75B | 0.19 | 0.09 | near debt-free, DY 16%, cheapest. ✓ entry |
| **KDH** | 2022Q4 | 1.68 | 0.83 | hi | +119B | 0.50 | 0.13 | safest B/S but **never cheap** (PB rarely <1.5) → quality-premium, mostly excluded |
| **NVL** | 2022Q4 | **0.62** | **4.73** | **0.50→−0.39** | +137B→**neg** | 0.39 | 0.13 | **LEVERAGE TRAP**: cheap P/B + un-payable debt, CF −5.2T, NP went negative 2023Q2. ✗ EXCLUDE |
| **PDR** | 2022Q4 | 1.03 | 1.47 | **−0.97** | **−267B** | 0.85 | 0.22 | IntCov negative + NP negative in the crunch → ✗ EXCLUDE (enters later once recovered+cheap) |

**Industrial — NTC 2017 (the user's flagship "great entry") + cheap peers:**
| name | 2017 | PB | DY | ROE5Y | ROIC5Y | ADV | read |
|---|---|---|---|---|---|---|---|
| **NTC** | Q1–Q4 | **2.5–3.7** | 3.6–4.3% | **23–29%** | 9.4% | **2.9B** | NOT cheap on P/B — a **DY+ROE+land-revaluation** play; re-rated on the 2017–21 FDI/IP boom. Structurally like VCB/PNJ (forward re-rating) → a value-disciplined P/B<1.5 screen **MISSES it** |
| **TIP** | Q1–Q4 | 0.93–1.05 | **9–10%** | 12.5% | 11.0% | 2.4B | cheap + high yield ✓ (illiquid) |
| **D2D** | Q1–Q4 | 0.9–1.7 | 6.5% | 14.5% | −7.8% | 3.0B | cheap + yield ✓ (illiquid) |
| LHG | Q1–Q4 | 0.78–0.91 | 0→6% | 10.1% | 13.7% | 1.9B | cheap, DY only from Q4 |
| KBC | Q1–Q4 | 0.65–0.81 | 0% | 3.1% | 2.5% | 35B | cheap but weak ROE, no yield → fails quality |

**Two RE-compounder archetypes (parallel to retail volume/margin & banking cheap/premium):**
- **A — cheap-distress (VHM-2023, NLG-2022, TCH-2022)**: low P/B + covered interest + still-profitable +
  deleveraging-capable. **Value-identifiable at entry.** This is the headline screen.
- **B — premium-yield re-rating (NTC-2017)**: already-premium P/B justified only by *forward* land
  revaluation / FDI re-rating. **NOT identifiable without look-ahead** → structurally uncapturable by a
  value-disciplined screen (same shape as banking-VCB and retail-PNJ misses).

## Part 4 — Two screens (point-in-time ASOF, staleness ≤120d)

**Screen A — Residential Cyclical** (universe = 8633 ∖ IP-list, in `ticker_prune`, TV_1M_P50 ≥ 1e9):
1. `PB ∈ (0, 1.5)` — distress zone
2. `Debt_Eq_P0 < 2.0` — leverage ceiling (**excludes NVL-type at every distress point**)
3. `IntCov_P0 > 1.5` — survival (excludes can't-pay-interest: NVL, PDR-2022)
4. `NP_P0 > 0` — currently profitable (excludes NP-negative blowups). *(NP-turning `P0>0 & P4<0` also admitted as a recovery leg.)*
5. `GPM_P0 ≥ 0.15` — project margins intact

Rank `z(−PB) + z(ROE5Y) + z(GPM_P0−GPM_P4) + z(min(IntCov,30))`, top-K=10, monthly EW, T+1, TC 0.1%.

> **Deviation from the dispatch first-draft, justified by backlook:** dropped the "Debt_Eq_P0 < Debt_Eq_P4
> (YoY deleveraging)" hard gate and the "CF_OA_P0 > 0" hard gate. At the *trough* leverage is at its YoY
> PEAK (names borrow going INTO the crunch; VHM/NLG Debt_Eq rose YoY at entry) and CF_OA is structurally
> negative (cash into projects) — both gates would exclude the very best entries (VHM-2023, NLG-2022).
> Replaced by the absolute ceiling Debt_Eq<2.0 + IntCov>1.5 + NP_P0>0, which still cleanly excludes NVL/PDR.

**Screen B — Industrial Park** (universe = 8633 ∩ IP-list, in `ticker_prune`, **no liquidity gate**):
1. `PB ∈ (0, 1.5)`
2. `DY > 0.04`
3. `ROIC5Y > 0.08`
4. **FLAG `ADV < 10B` → liquidity-warning column, never exclude**

Rank `z(DY) + z(ROIC5Y) + z(−PB)`, take all qualifiers (thin), monthly EW, T+1, TC 0.1%.

## Part 5 — Backtest results (auditable, self-check PASS 0 VND both screens)

**Screen A — Residential Cyclical** (47-name universe, med 9 qualifiers/mo, 0 empty months):
| window | RE net CAGR | Sharpe | MaxDD | B&H CAGR | edge |
|---|---|---|---|---|---|
| FULL 2014-2026 | 10.41% | 0.43 | **−61.8%** | 14.57% | **−4.17pp (UNDERPERFORMS)** |
| IS 2014-2019 | 4.09% | 0.30 | −42.9% | 22.87% | −18.77pp |
| OOS 2020-2026 | 13.00% | 0.50 | **−61.8%** | 11.45% | +1.55pp **(but Sharpe −0.10, DD ≫ market)** |

**Verify (flawless):** VHM caught 2022Q4–2023 ✓ (cheap-quality), NLG caught 2022–23 ✓ (deleverager), TCH
caught 2022–23 ✓ (debt-free value). **NVL leverage trap EXCLUDED at every distress point ✓**, **PDR-2022
crunch (IntCov −0.97) EXCLUDED ✓**. The value/risk discipline does exactly what it should.

**But the sector does not compound — it oscillates.** Per-year the screen is pure high-beta cyclical:
+47.6pp (2020), +53.4pp (2021), +19.8pp (2023) in recoveries; **−20.0pp (2022), −16.4 (2019), −28.6 (2025)**
in late/down-cycle. A monthly value screen buys the distress and **holds it straight down** (long
VHM/NLG/TCH through 2022's −48%) → MaxDD −61.8%, far worse than market. The marginal OOS +1.55pp is entirely
2020–21 recovery-beta, not alpha. **RE needs TIMING (macro/regime exit), which a pure value screen lacks.**

**Screen B — Industrial Park** (11 names, **median 1 qualifier/month, max 2**):
| window | IP net CAGR | Sharpe | MaxDD | B&H CAGR | edge |
|---|---|---|---|---|---|
| FULL (29 mo) | 39.58% | 0.78 | −25.6% | 46.00% | −6.42pp |
| OOS 2020-2026 | 19.84% | 0.69 | −22.1% | 29.63% | **−9.79pp (WORSE)** |

**Structurally un-investable as a book:** 1-name micro-portfolio; **median selected-name ADV 1.7B VND/day**,
31 picked name-months sub-10B → capacity-dead (buying 10B of NTC = weeks, per the user's own NTC-2017 point).
NTC-2017 correctly ABSENT (PB 2.5–3.7 ≫ 1.5; premium DY+ROE+land-revaluation re-rating, uncapturable w/o
look-ahead — parallel to banking-VCB / retail-PNJ).

**Orthogonality (resid Screen A):** vs custom30V **15.2%**, vs 8L top-25 **7.9%** (orthogonal — RE is a
value/cyclical axis), vs industrial Screen B 0% (disjoint by construction).

## VERDICT — risk/valuation LENS, not a standalone book (cleanest negative of the 4 sector screens)
1. **Residential: the discipline is REAL and valuable as a GATE** — P/B<1.5 distress + Debt_Eq<2.0 +
   IntCov>1.5 + NP_P0>0 perfectly separates cheap-quality (VHM/NLG/TCH) from leverage traps (NVL/PDR). **Use
   it to pick WHICH RE names and to SIZE RE exposure (avoid the NVL-type), not as a buy-and-hold book** — the
   sector underperforms B&H (−4.2pp full) with −61.8% DD because it's cyclical, not a compounder. RE alpha
   requires regime TIMING (DT5G macro gate / exit), absent from a pure value screen.
2. **Industrial parks: a REIT yield-watchlist only** — 1-name, 1.7B ADV, capacity-dead, no OOS edge.
3. Lasting deliverable = the **valuation method** (P/B-as-NAV-proxy, two-archetype split, the leverage-trap
   exclusion gate, the IP deferred-lease caveat) for sizing RE inside V2.4 — consistent with the prior three
   sector screens all landing on "tilt/lens, not standalone book."
