# Retail Valuation Framework (VN: MWG / PNJ / FRT)
Author: Taylor · job Taylor_20260630_044001 · 2026-06-30
Companion to (and DISTINCT from) the industrial Compounder Screen (job Taylor_20260630_042949).

---

## Part 1 — Why retail needs its own lens (international practice)

International analysts (Amazon, Walmart, Costco, Best Buy, Inditex) do NOT anchor growth-retail
valuation on P/E. The reasons, each confirmed in VN data below:

1. **P/E is suppressed & misleading during expansion.** New stores carry full opex (rent, staff,
   pre-opening, ramp) from day 1 but only mature into full revenue over 12–24 months. Net profit is
   structurally depressed while the footprint compounds. → P/E looks *expensive* exactly when the
   business is cheapest on its earnings power. **VN proof:** MWG 2014Q3 P/E = **43** (scary) while
   P/S was only **1.2**; by 2015Q4 P/E collapsed to **9.8** as NP caught up — the stock *grew into*
   the multiple, it did not de-rate. Anyone using P/E in 2014 missed a 3x.

2. **P/S is the primary metric for a growth retailer.** Revenue is the cleanest, least-manipulable
   measure of footprint + share gain. For a fixed, stable net margin (the retail norm), P/S is just
   P/E × margin — but it strips out the expansion-cost distortion. Re-rating happens when the market
   re-prices the *sales base*, not next quarter's EPS. **VN proof:** MWG's winning entry was P/S
   **0.42–0.85** *de-rating* while revenue grew **55–68% YoY** — price lagging sales = the classic
   retail mispricing window.

3. **EV/EBITDA vs EV/EBIT — operating leverage.** Retailers carry heavy lease/D&A (esp. post-IFRS16).
   EV/EBITDA neutralizes lease-accounting noise and is preferred for *cross-retailer* comparison.
   EV/EBIT is the tougher test (charges the asset base) and better for *mature* retailers where you
   want to see the store fleet actually earns its capital. Growth phase → EV/EBITDA; maturity → EV/EBIT.
   (BQ proxy = `EVEB` = EV/EBITDA; no EV/EBIT column.)

4. **ROIC = the moat for capital-light retail.** The best retail models (Costco membership, MWG
   supplier credit, fast-fashion negative cash-conversion-cycle) fund inventory with *supplier money*
   and lease (not own) the stores → invested capital is tiny → ROIC is structurally high. High,
   durable ROIC at scale = pricing/scale moat. **Caveat (VN data):** when net working capital goes
   negative, the ROIC denominator collapses and point-in-time ROIC explodes — `ROIC_Trailing` reads
   1.1 (MWG) / 2.8 (FRT) / 1.3 (PNJ), which is NOT comparable across names. Use the multi-year
   averaged `ROIC5Y`/`ROE5Y` instead (MWG 10%/17%, PNJ 20%/22%, FRT 5%/13% — sane and discriminating).

5. **Inventory efficiency = health signal, but SECTOR-RELATIVE.** Rising DIO / falling InvTurn while
   revenue stalls = goods not selling (the classic retail death spiral — pre-bankruptcy signature).
   BUT the *level* is sector-specific: electronics 45–60 days (MWG ~50–60) is healthy; jewelry
   100–130 days (PNJ) is *normal* (gold/diamond inventory is expensive and slow) and must NOT be
   read as a red flag. Screen on the *trajectory* (deteriorating vs stable), benchmarked within sub-sector.

6. **Unit economics (revenue/store, NP/store).** International gold standard (same-store-sales growth,
   sales/sqft). **DATA GAP: BQ has NO store-count column** → revenue/store NOT computable here.
   Proxy with total `Revenue_YoY` decomposition is the best we can do; flag this for manual overlay.

7. **Operating leverage signal.** Revenue growth > total cost growth → margin expands *with a lag*.
   In practice: watch GPM stable-or-up while NPM begins to rise once new-store drag rolls off.
   Retail does NOT require margin *expansion* to win (volume is the engine) — flat margin + volume
   growth (MWG) and margin-expansion turnaround (PNJ) are *both* valid archetypes (see Part 4).

---

## Part 2 — Map to BQ columns (`ticker_financial` / `ticker_prune`)

| Concept | BQ column | Notes |
|---|---|---|
| **P/S (primary)** | `PS` (in `ticker_financial`) | Lives in `ticker_financial`, NOT `ticker`. Primary valuation axis. |
| P/CF (FCF-ish) | `PCF` | Secondary; CF more meaningful than NP for retail. |
| EV/EBITDA | `EVEB` | Cross-retailer comp; no EV/EBIT column exists. |
| Revenue growth | `Revenue_YoY_P0`, `Revenue_YoY_P4` | Persistence = both > threshold (2yr). |
| Gross margin trajectory | `GPM_P0` vs `GPM_P4` | Flat-or-up is fine; *down* while revenue stalls = avoid. |
| Net margin | `NPM_P0` vs `NPM_P4` | Thin & stable is normal; watch direction, not level. |
| **Inventory efficiency** | `InvTurn_P0`/`P4`, `DIO_P0`/`P4` | Use *trajectory*, benchmark within sub-sector. |
| Cash generation | `CF_OA_P0`, **`CF_OA_3Y`/`CF_OA_5Y`** | Per-quarter goes NEGATIVE in expansion (inventory build) → **gate on the 3Y/5Y sum, not P0.** |
| **Capital efficiency / moat** | **`ROIC5Y`, `ROE5Y`, `ROE_Min3Y`** | Use these, NOT `ROIC_Trailing` (unreliable magnitude). |
| Quality floor | `FSCORE`, `Debt_Eq_P0` | Retail should be low-debt (supplier-financed). |
| Sub-sector | `ICB_Code` | MWG/FRT = 5379 (retail); PNJ = 3767 (personal goods/jewelry). |
| Unit economics | — | **NOT AVAILABLE** (no store count). Manual overlay only. |

---

## Part 3 — Backlook at entry points (BQ-verified, auditable)

### MWG — 2014–2015 entry → +216% by 2018-01, ~4x by 2021 (adj Close 9,640 → 30,420 → 38,590)
The **textbook volume-compounder**:
- **P/S 0.42–0.85, DE-RATING** even as **Revenue YoY 55–68%** → price lagged sales (the entry window).
- **P/E misleading**: 43 (2014Q3) → 9.8 (2015Q4); earnings grew into the multiple.
- **GPM FLAT ~15–16%**, NPM flat ~4% (thin/stable — no margin expansion needed; volume is the engine).
- **InvTurn 5–7×, DIO ~50–60d** — healthy electronics inventory.
- **CF_OA lumpy / negative** in expansion quarters → confirms *why* NP/PE distorts; use TTM CF.
- ROIC5Y 10% / ROE5Y 17% (capital-light, supplier-financed).

### PNJ — 2014–2015 entry → +369% by 2018-01, ~6x by 2021 (5,980 → 28,040 → 36,480)
The **margin-expansion turnaround** (different archetype — would FAIL a pure revenue-growth screen):
- **P/S 0.23–0.40 (dead cheap)**, but **Revenue YoY NEGATIVE** in 2014–15 (gold-trading wind-down).
- The real signal = **GPM EXPANDING 8% → 17%** (mix shift to branded retail jewelry) + **ROIC rising**.
- **DIO HIGH & rising (100–130d)** — *normal for jewelry*, NOT a red flag (sector-relative rule).
- ROIC5Y 20% / ROE5Y 22% (strongest of the three). → caught only by the margin-expansion branch.

### FRT — 2018 IPO entry → −55% trough by 2021, only +154% by 2024 with a brutal DD (31,540 → 14,100 → 80,230)
The **cautionary tale / value-trap that sprang** — the screen should AVOID it in 2018:
- **P/S 0.47 → DE-RATED to 0.19** (cheap got cheaper — the trap).
- **Revenue YoY DECELERATING 24% → 2% → 7%** (phone retail saturating) — fails persistence.
- **GPM thin ~13% and flat-to-down**, NPM razor-thin 2.3% and falling.
- ROIC5Y only **5%** / ROE5Y 13% (weakest) — borderline on the capital-efficiency gate.
- The eventual win came from **Long Châu pharmacy**, a NEW business INVISIBLE in 2018 financials.
  → No fundamental screen could (or should) have bought FRT in 2018 on the numbers. Correctly excluded.

**Verdict on leading indicators:** ✅ confirmed. P/S (cheap + lagging sales), inventory-efficiency
trajectory, and revenue-growth-persistence-OR-margin-expansion are the right leading signals.
The 3 names cleanly separate into WIN (MWG volume, PNJ margin) vs AVOID (FRT deceleration).

---

## Part 4 — Proposed Retail Compounder Screen (separate from industrial screen)

**Universe gate:** `ICB_Code` in retail/consumer sub-sectors (5379 retail; 3767 personal goods; plus
other consumer-discretionary retail codes — to be enumerated). Liquid universe = `ticker_prune`.

**Primary valuation (replaces P/E):**
- `PS` < **1.5** soft cap; **prefer < 1.0** (MWG/PNJ/FRT all entered < 1.0). Penalize, don't hard-cut, 1.0–1.5.
- Secondary sanity: `PCF` positive, `EVEB` not extreme.

**Growth — TWO archetypes (pass EITHER):**
- **(A) Volume compounder:** `Revenue_YoY_P0` ≥ **15%** AND `Revenue_YoY_P4` ≥ **10%** (2yr persistence),
  with `GPM_P0` ≥ `GPM_P4` − 1pp (flat-or-up). [MWG path]
- **(B) Margin-expansion turnaround:** `Revenue_YoY` may be flat/negative BUT `GPM_P0` − `GPM_P4` ≥ **+2pp**
  AND `ROIC5Y` rising vs prior / ≥ 15%. [PNJ path]

**Quality / health (all required):**
- **Inventory trajectory:** `InvTurn_P0` ≥ 0.85 × `InvTurn_P4` (not sharply deteriorating); evaluate
  DIO *within sub-sector* (no absolute DIO cap — jewelry vs electronics differ 2×).
- **Cash:** `CF_OA_5Y` > 0 (multi-year, NOT per-quarter — expansion quarters legitimately go negative).
- **Capital efficiency / moat (use multi-year, NOT `ROIC_Trailing`):** `ROIC5Y` ≥ **12%** OR
  `ROE5Y` ≥ **15%** (capital-light retail clears easily; FRT at 5%/13% is correctly borderline = risk flag).
- **Balance sheet:** low `Debt_Eq_P0` (retail should be supplier-financed, not levered).

**Why retail ROIC threshold ≠ industrial:** capital-light retail *should* show HIGHER ROIC than
asset-heavy industrials (no plants to fund). So a 12% ROIC5Y floor is *easy* for a genuine moat
retailer and a 5% reading (FRT) is a genuine warning, not noise. Do NOT lower the bar for "retail".

**Known limits / honesty:**
- No store-count → no true unit economics (rev/store, SSSG). Manual overlay required for conviction.
- `ROIC_Trailing` magnitude is unreliable for capital-light names — gate on `ROIC5Y`/`ROE5Y`.
- This is a *retrospective signature match* on 3 names, NOT a backtested edge. Next step (if approved):
  point-in-time monthly rebalance backtest, walk-forward IS(2014–19)/OOS(2020+), orthogonality vs 8L
  rating + vs the industrial compounder screen — same bar as every other Taylor edge.
- Expect THIN, like the industrial screen: VN retail compounder set is small (≈MWG/PNJ/FRT/DGW/PET) →
  likely watchlist/tilt, not a standalone book.
