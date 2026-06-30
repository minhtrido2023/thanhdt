# Steel + Building Materials — Valuation Framework (Sector #8)

> Author: Taylor (Quant) · job Taylor_20260630_065623 · 2026-06-30
> Companion screen: `steel_buildmat_screen.py` → `data/steel_*_monthly.csv` + `data/steel_buildmat_verdict.json`

This is a **broad, heterogeneous** sector that must be split into **three distinct economics**.
A single valuation lens is wrong for all of them. ICB does not separate these cleanly, so
sub-universes are hand-curated by name (parallel to logistics / fertchem splits).

---

## Part 1 — International framework (the economics)

### A. Steel (HPG, HSG, NKG, SMC, TLH, POM) — commodity cyclical, capital-intensive
- **EV/EBITDA primary** in upswing (global steel mills trade 4–7× mid-cycle).
- **P/B trough-buy**: in theory buy below replacement cost (rebuilding a mill costs more than
  buying the equity at P/B<1). **VN reality (see Part 3): this rule is a TRAP.** The names that
  trade P/B<1 are the *over-levered* ones (HSG, NKG), not the quality compounder (HPG).
- **Leverage is the survival metric.** Net-Debt/EBITDA in theory; in BQ proxy = `Debt_Eq_P0`
  + `IntCov_P0`. A steel name with `IntCov<1.5` through a downcycle can be wiped out.
- Revenue/margin extremely lumpy with the global hot-rolled-coil (HRC) price.
- **HPG is structurally different** — fully integrated (coke → pig iron → BOF steel → pipe →
  industrial-park RE). It earns a real ROIC through-cycle (ROE5Y 20–25% even in 2013–2019),
  so the market *never* lets it get truly cheap on P/B (floor ~1.0 only at the 2022 crash).

### B. Cement (HT1, BCC) — regional oligopoly, mature
- **EV/EBITDA primary** (capex-heavy, large D&A). Pricing power is *regional*, not global —
  domestic demand + clinker cost, not a world commodity like steel.
- Strong `CF_OA` when utilisation is high; mature → a **dividend-yield play** when not growing.
- **DATA CAVEAT (critical):** `DY` is essentially **uncapturable** for VN cement in BQ
  (HT1 1/75 quarters, BCC 6/79 have DY>0). The classic "cement = yield" screen **cannot be
  built** here → Screen B pivots to **EV/EBITDA value + CF_OA + leverage**, and we report the
  DY gap honestly rather than ship a broken yield gate.

### C. Specialty materials / pipes (NTP, BMP, VCS) — hidden quality compounders
- **NOT a commodity.** Local distribution moat (pipes) / niche export moat (VCS quartz).
- P/E or EV/EBIT appropriate — margins stable, not lumpy.
- **High-ROIC (>15–20%) + clean balance sheet + consistent dividend = compounding machine.**
- Grows with the construction cycle but is *not* cyclical like steel.

---

## Part 2 — Map to BQ columns
| Concept | BQ column | Used in |
|---|---|---|
| Cyclical valuation | `EVEB`, `PB`, `EVEB_MA1Y` | A, B |
| Margin turning up (early cycle) | `GPM_P0 > GPM_P4` | A |
| Leverage / survival | `Debt_Eq_P0`, `IntCov_P0` | A, B, C |
| Survived a full cycle | `CF_OA_3Y > 0`, `CF_OA_P0` | A, B, C |
| Moat / quality | `ROIC5Y`, `ROE5Y` | C |
| Not expensive vs own history | `PE < PE_MA1Y` | C |
| Volume/price spike | `Revenue_YoY_P0` | A |
| Yield (cement) | `DY` | B (broken — see caveat) |

---

## Part 3 — Backlook (ticker_financial cache; quarter = Release_Date asof)

```
HPG 2013Q1  EVEB6.6 PB1.30 ROIC5Y0.7%(early-window noisy) GPM 17.6%>13.4%↑ IC-6.6  Rev-3.6%  -> early-cycle margin turn caught
HPG 2014Q1  EVEB7.0 PB2.26 GPM21.3% Rev+64.6%  -> already re-rated (the 2013→14 upcycle)
HPG 2019Q2  EVEB7.3 PB1.41 ROE5Y25% IC+12.5 GPM19.4%      -> quality, pre-2020 surge, NEVER cheap on PB
HPG 2022Q3  EVEB5.0 PB1.00 IC-0.6                          -> ONLY time HPG hit PB~1 (steel crash) — and IntCov went negative
HSG 2018Q4  EVEB8.3 PB0.49 Debt_Eq2.83 IC1.5 GPM10% NPM0.4%  -> "cheap" PB is a LEVERAGE TRAP
NKG 2014Q1  EVEB5.5 PB0.94 Debt_Eq6.32 IC-1.3 GPM4.9%        -> extreme leverage, IntCov negative -> reject
NKG 2018Q4  EVEB6.3 PB0.37 Debt_Eq1.73 IC-1.0                -> cheap but still cannot cover interest
BMP 2018Q4  EVEB4.6 PB1.61 ROIC5Y19.4% ROE5Y23% Debt_Eq0.15 DY3.2% GPM22%  -> TEXTBOOK compounder, cheap window
BMP 2015Q4  EVEB27→ compressed to 4.6 by 2018  ROIC5Y~20% persistent     -> valuation compression = the entry
NTP 2018Q4  EVEB9.8 PB1.62 ROIC5Y10.0% ROE5Y22% Debt_Eq1.16 DY3.6% GPM29% -> compounder-WITH-debt (fails clean-BS gate)
HT1 2018Q4  EVEB4.9 PB1.12 CF_OA+851B Debt_Eq1.05 DY≈uncaptured  -> cement value via EVEB+CF_OA, NOT yield
```

### The two patterns that define the sector
1. **HPG pattern (own-it):** quality integration → ROE5Y 20–25% through cycle, IntCov turns
   strongly positive post-2018, P/B floors ~1.0 only at crashes. You buy it on **EV/EBITDA +
   margin-turn**, *not* on a low-P/B screen (which it rarely triggers).
2. **HSG/NKG pattern (avoid-it):** low P/B (0.37–0.94) driven by **3–6× Debt/Equity** and
   **negative/thin IntCov** + razor-thin GPM (4–10%). The cheap-P/B signal is a leverage trap.
   → The **leverage gate (Debt_Eq<2.0 AND IntCov>1.5) is the entire alpha** of Screen A: it
   keeps HPG-survivors and ejects HSG/NKG-traps.

---

## Part 4 — Three sub-screens (point-in-time monthly, ASOF financials, ≤120d stale)

**Screen A — Steel cyclical (trough-buy, leverage-disciplined):**
- `EVEB ∈ (0,6)` · `PB < 1.5` (HPG never <1.2 except crashes → spec's <1.2 would *exclude the
  one name worth owning*; relaxed to 1.5) · `GPM_P0 > GPM_P4` (margin turning up) ·
  **`Debt_Eq_P0 < 2.0` AND `IntCov_P0 > 1.5`** (the leverage gate) · `CF_OA_3Y > 0`.

**Screen B — Cement (value + cash, NOT yield — DY uncapturable):**
- `EVEB ∈ (0,6)` · `CF_OA_P0 > 0` · `Debt_Eq_P0 < 1.5`. (DY reported as a soft score where
  present, never a hard gate.)

**Screen C — Specialty / pipe (ROIC compounder):**
- `ROIC5Y > 0.12` (catches BMP 19%, VCS 14%; **NTP 10% is a documented borderline miss**) ·
  `ROE5Y > 0.15` · `PE < PE_MA1Y` (not dearer than own history) · `CF_OA_3Y > 0` ·
  `Debt_Eq_P0 < 0.5` (clean BS — also drops NTP, which carries ~1.0× debt).

---

## Part 5 — Verdict (filled by the backtest)
See `data/steel_buildmat_verdict.json` + `data/results_registry.md` entry. Headline in the
bus finding. Expectation going in: a **lens/risk-discipline tool**, not a standalone book —
the steel leverage gate is the durable, transferable rule; the specialty compounders are too
few names to carry a sleeve.
