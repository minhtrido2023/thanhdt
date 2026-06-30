# Securities / Brokerage — valuation & screen framework (sector #13)

Job `Taylor_20260630_073104`. Script `securities_screen.py`. Outputs `data/securities_{screen,screen_dt5g,basket}_monthly.csv`, `data/securities_verdict.json`. AUDIT_END 2026-04-29.

## What a brokerage firm IS (why it needs its own method)
A VN brokerage = **leverage on market activity**. Capital is deployed as a margin-lending book + a
FVTPL proprietary book, so:
- **VALUE = P/B, not P/E.** Capital deployed ≈ book value; ROE × P/B is the valuation matrix. NP is
  violently cyclical (brokerage fee = market volume × rate; margin NIM; prop trading P&L; IB/underwriting
  fees — all collapse in a bear, some go negative), so a P/E gate is unusable.
- **ROE is the swing factor.** Bull (2021, 2024-25): ROE doubles as margin lending + fees explode.
  Bear (2020Q1, 2022-23): ROE craters or goes negative.
- **Debt_Eq is HIGH by design** (margin debt funds the lending book) — NOT a red flag. The leverage gate
  must be **IntCov**, not `Debt_Eq<2`.
- **Cyclicality ~1:1 with VNINDEX trading volume** → brokerage is the **highest-beta sector** in the
  13-sector sweep (measured β 1.27 screen / 1.60 always-invested basket).

## The screen (single, coherent — one sub-sector unlike F&B)
Universe (17 liquid VN brokers): SSI VCI HCM VND MBS SHS AGR BSI CTS VIX FTS VDS BVS APG TVS ORS EVS.
Point-in-time prune ADV≥1B gates monthly membership; ASOF financials ≤120d; EW top-8; cash when none.

| gate | rationale |
|---|---|
| `PB ∈ (0, 1.8)` | cheap on book — AND the euphoria-cap. At the 2021-22 top SSI/VND/HCM ran PB 3.0-4.1, so this gate KEEPS THE SCREEN OUT of the cycle peak by construction. |
| `ROE_Trailing > 0.08` | minimum capital efficiency (TTM ROE; NP too volatile for P/E). |
| `ROE_Trailing > ROE3Y` | **INFLECTION gate** — trailing ROE re-crossing ABOVE its own 3Y base = cycle turning up. **Fires LATE, not at the price trough** (see below). |
| `NP_P0 > 0` | profitable — parks in CASH through the earnings collapse. |
| `IntCov_P0 > 1.5` (NULL-tolerant) | can service margin-funding debt — the leverage gate that REPLACES Debt_Eq. NULL-tolerant: coverage is patchy (FTS 2/39) so exclude only KNOWN-bad ≤1.5, never on missing data. |

Rank: `z(−PB) + z(ROE_Trailing) + z(ROE_Trailing − ROE3Y)`.

## Backlook that shaped the design (ticker_financial cache)
- **ROE_Trailing>ROE3Y fires LATE.** After a crash, trailing ROE sits BELOW the still-elevated 3Y avg
  and only re-crosses once the recovery is CONFIRMED: VND caught **late-2020** (2020Q3 roet 0.172 > 3Y
  0.152), but SSI/SHS were **NOT** caught at the 2020Q1 price trough because their 3Y base was still
  ~0.13-0.21. It is a **confirmation signal, not a bottom-picker** — trades whipsaw-avoidance for a
  later, surer entry, and clips the early recovery leg.
- **PB<1.8 cap works at the top.** SSI 2021Q4 PB 3.20 / VND 2022Q1 PB 3.65 / HCM 2021Q3 PB 3.35 — all
  excluded → screen avoids the 2021-22 euphoria peak. Only 1 month of 2021-H2 top-entry slipped through.
- **NP_P0>0 + ROE>8% holds cash through 2022-23.** SHS 2022Q4 roet 0.033, VND 2023Q1 0.041, SHS 2023Q1
  −0.014 → all rejected; the screen sat in cash 12 months through the crash.
- **IntCov>1.5 catches over-levered margin books.** VND historically runs Debt_Eq 2.5-3.6; its IntCov
  dips ≤1.5 at over-extension points (2018Q4 IntCov 1.1) → correctly screened out.

## Results — the honest test (a high-beta sector demands it)
Three benchmarks: VNINDEX B&H, **EW broker-basket B&H** (own the whole sector, always invested), and the
**DT5G-gated** screen (cash when DT5G ∈ {CRISIS, BEAR}).

| view | window | net CAGR | Sharpe | MaxDD | Calmar | bench |
|---|---|---|---|---|---|---|
| screen vs **basket** (KEY) | FULL | 17.74% | 0.57 | −65.7% | 0.27 | basket 21.83% / −60.8% → **−4.10pp, worse Sharpe** |
| screen vs basket | IS 14-19 | 6.43% | 0.34 | −47.5% | 0.14 | basket 8.63% → −2.19pp |
| screen vs basket | OOS 20-26 | 29.55% | 0.72 | −65.7% | 0.45 | basket 35.82% → −6.27pp |
| **DT5G-gated** vs VNINDEX | FULL | **27.74%** | **0.79** | **−31.7%** | **0.88** | VNI 10.23% / −43.2% |
| DT5G-gated vs VNINDEX | OOS | 44.42% | 0.96 | −31.7% | 1.40 | VNI 11.45% |

**Per-year (screen | basket | VNINDEX | DT5G-gated):** 2018 −38/−20/−17/**+10**; 2021 +298/+212/+45/**+396**;
2022 −49/−49/−28/**−19**; 2023 −0/**+99**/+9/0; 2024 +42/−1/+7/+42.

## Verdict
1. **As a standalone cross-sectional screen → FAIL.** It loses to simply OWNING ALL BROKERS on CAGR AND
   Sharpe across FULL/IS/OOS. The late-confirmation inflection gate sits in cash through the basket's
   +99% 2023 and clips the 2017/2020 recovery legs; ungated DD −65.7% is even worse than the
   always-invested basket (−60.8%) — the valuation/cash-timing is mistimed.
2. **THE DURABLE EXPORT — brokerage is the ONE sector where DT5G is a RETURN-ENHANCER, not just insurance.**
   Gating to cash in CRISIS/BEAR lifts Full CAGR 17.7→27.7%, Calmar 0.27→0.88, and HALVES DD
   −65.7→−31.7% (beats VNINDEX). Multi-episode, not single-event (2018 + 2022 + the 2021 super-cycle kept).
   Mechanism: broker β~1.3 and its worst-drawdown quarters ARE the market's CRISIS/BEAR → the de-risk
   gate is maximally effective exactly where beta is highest. This is the strongest evidence in the
   13-sector sweep that DT5G adds return (not only protection).

## Reusable rules (durable exports)
1. **PB-primary, not PE** for brokers (NP too cyclical for an earnings multiple).
2. **IntCov replaces Debt_Eq** — margin debt is by-design; a HARD IntCov>1.5 gate would drop 241/405
   passing rows (116 known-bad + 125 NULL-coverage) → use NULL-tolerant.
3. **ROE_Trailing>ROE3Y = LATE confirmation, not a trough-pick** — re-crosses the elevated 3Y base only
   mid-recovery; do not market it as bottom-fishing.
4. **Brokerage = highest-beta sector** (β 1.27/1.60) → never own ungated; pair with DT5G.

## Caveats
- OOS CAGR leans on the 2021 margin-lending super-cycle (+298%/+396%), a once-a-generation event — but
  the DT5G edge itself is NOT single-event (also 2018 + 2022).
- Median selected ADV 21.2B → genuinely tradeable (unlike pharma/tech/telecom). Orthogonality:
  custom30V 33.5% | 8L top-25 6.9%.
