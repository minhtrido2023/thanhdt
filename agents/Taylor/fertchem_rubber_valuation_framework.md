# Fertilizer / Chemicals / Rubber — valuation framework & screens

Job `Taylor_20260630_064517` (sector #7). Script `fertchem_rubber_screen.py`. AUDIT_END 2026-04-29.
Three sub-sectors, three distinct economics — one screen each. Same point-in-time monthly method as the
prior 6 sector screens (ASOF financials, staleness ≤120d, monthly EW, T+1, TC 0.1%, hold cash when empty).

## Part 1 — international framework per sub-sector

**Fertilizer (commodity cyclical).** Value on **EV/EBITDA** in upswing, **P/B trough-buy** when urea/DAP
prices crash. VN specifics: DPM/DCM are gas-fed urea — margin is hostage to the **policy gas price**, not
just the global commodity. Revenue lumps with the global fertilizer cycle; CF_OA huge in a supercycle,
negative when prices fall. High **DY** = the carry while you wait for the cycle.

**Chemicals — split in two.** Specialty (DGC: phosphorus/DAP) earns a real margin/ROIC → **EV/EBITDA +
ROIC**. Commodity chemicals are price-takers, thin margin → **trough-buy P/B**.

**Rubber — two value sources.** (1) Latex = pure commodity, thin margin, cyclical. (2) **Land-bank
conversion** (PHR/DPR/TRC: old rubber estates → industrial parks) = one-time massive gain, **invisible to
standard financial metrics**. P/B < 1.0 while the land sits un-revalued = the hidden-asset tell.

## Part 2 — BQ mapping
EVEB (primary fert/chem) · PB (trough + land-bank) · DY (carry) · GPM_P0 vs GPM_P4 (margin-expansion =
early cycle) · Revenue_YoY_P0 (commodity price-spike proxy) · CF_OA_P0 / CF_OA_3Y (supercycle cash) ·
Debt_Eq_P0 + IntCov_P0 (survivability) · ROIC5Y (chem moat; **DATA-CORRUPTED for rubber** — PHR 515%,
DPR 290% from a tiny/restated equity base → not used in Screen C).

**Universe (hand-curated — ICB does NOT separate the three): ** ICB **1357** lumps fertilizer+chemicals;
ICB **1353** lumps rubber+plastics. So:
- FERT = DPM, DCM, BFC, LAS, DDV, SFG, VFG, QBS, ABS, PMB (ADV-weighted big: DPM/DCM liquid)
- CHEM = DGC, CSV, PAT, HVT, PLC
- RUBBER = GVR, PHR, DPR, TRC, DRI (HRC not in liquid prune)

## Part 3 — backlook (was the cheapness / catalyst predictable?)

| name | quarter | EVEB | PB | DY | ROIC5Y | CF_OA / 3Y | read |
|---|---|---|---|---|---|---|---|
| DGC | 2019Q4 | 4.5 | 0.93 | 4.1% | 10.8% | +197B / ramping 887B→1368B | **pre-supercycle entry, catchable** |
| DGC | 2020Q1 | 4.3 | 0.86 | 0 | 10.8% | +247B | textbook bottom (before ~10×) |
| DPM | 2019Q4 | 3.2 | 0.60 | 3.4% | 8.2% | +307B | cheap trough; urea spike 2021 ahead |
| DCM | 2019Q4 | 2.5 | 0.49 | 0 | 4.8% | +1267B | cheap, gas-policy drag |
| PHR | 2016Q1 | 20.8 | **0.66** | 5.2% | (corrupt) | −25B | land-bank, **re-rated to PB 2.45 by 2019Q1** |
| DPR | 2017Q3 | 3.5 | **0.61** | 7.4% | (corrupt) | +109B | persistent land-bank deep value |

Honest reads: **DGC's supercycle WAS partly catchable** (EVEB<5, PB<1, ROIC~11%, CF_OA ramping in
2019-2020) — but ROIC5Y was **10.8–11.5%**, *below* a literal >12% gate. **PHR's land re-rate was FAST**
(PB 0.66→2.45 in ~3 yr) so the PB<0.8 window is short and was already passing pre-prune; **DPR stays cheap
for years** (slow/no conversion) and dominates a "wait-for-land" screen.

## Part 4 — screens
- **A Fertilizer cycle:** EVEB∈(0,6) & CF_OA_3Y>0 & GPM_P0>GPM_P4 & Debt_Eq<1.5; rank z(−EVEB)+z(DY)+z(GPM), top-10.
- **B Specialty chem:** EVEB∈(0,8) & ROIC5Y≥**0.10** (not 0.12 — would miss DGC golden window) & Revenue_YoY_P0>0.20 & CF_OA_P0>0; rank z(−EVEB)+z(ROIC)+z(RevYoY), take-all.
- **C Rubber land-bank:** PB∈(0,0.8) & Debt_Eq<0.5 & CF_OA_P0>0; rank z(−PB)+z(DY)+z(−Debt_Eq), take-all. **DY>4% used as SOFT score, not hard gate** (annual/lumpy dividends → a hard gate kills 22/54 valid rows).

## Part 5 — results (self-check 0 VND: all three PASS)

| screen | window | net CAGR | Sharpe | MaxDD | B&H CAGR | edge | note |
|---|---|---|---|---|---|---|---|
| A fert | FULL 14-26 | 10.46% | 0.48 | −43.8% | 10.23% | **+0.22pp** | flat — all edge = 2021 |
| A fert | IS 14-19 | −0.53% | 0.07 | −26.2% | 8.96% | −9.49pp | IS-negative |
| A fert | OOS 20-26 | 21.98% | 0.74 | −43.8% | 11.45% | +10.53pp | **entirely the 2021 +204%/yr urea supercycle (+159pp)** |
| B chem | FULL 14-26 | −1.10% | 0.06 | −50.6% | 10.23% | **−11.34pp** | NEGATIVE |
| B chem | IS 14-19 | −7.79% | −0.65 | −38.5% | 8.96% | −16.75pp | bad |
| B chem | OOS 20-26 | 5.67% | 0.32 | −50.6% | 11.45% | −5.78pp | caught DGC 2020 (+62.9%) but MISSED 2021 supercycle |
| C rubber | FULL 14-26 | 5.63% | 0.47 | **−12.5%** | 10.23% | −4.60pp | **DD ¼ of market; Calmar 0.45 > 0.24** |
| C rubber | IS 14-19 | 6.87% | 0.50 | −12.5% | 8.96% | −2.09pp | defensive |
| C rubber | OOS 20-26 | 4.48% | 0.47 | **−0.1%** | 11.45% | −6.97pp | barely held 2020-23 (waited) |

**Verify:** DGC 2019-2020 **CAUGHT** (15 entry-months); DGC supercycle 2021-22 only late (2022Q3+ — the
Rev_YoY>0.20 base-effect drops it during the actual spike → the screen misses its own thesis). DPM/DCM
2019-2020 cheap troughs **CAUGHT**. PHR land-bank **NOT caught** (PB re-rated before the <0.8 window opened
in the prune era — land-as-alpha uncapturable, parallel to GMD/PNJ/VCB premium re-rates). DPR held **36
months** (the persistent cheap land-bank name dominates Screen C).

**Liquidity:** FERT 29.2B ADV (liquid — big names), CHEM 4.3B (thin ex-DGC), RUBB 1.4B (micro).
**Orthogonality (vs custom30V | vs 8L top-25):** FERT 47% | 8% (already largely in custom30V parking),
CHEM 5% | 0%, RUBB 13% | 0%.

## Verdict
Same family as the prior 6 sector screens — REAL but thin, **lens not standalone book**.
- **Fertilizer = a pure cyclical-timing lens.** Cheapness is predictable; the *entire* return is one
  un-forecastable global catalyst (the 2021 urea/gas supercycle). IS-negative, deep −44% DD, 47% already
  inside custom30V. Use EVEB<6 + high-DY as a *cheap-and-waiting* tell, size only when the global cycle
  turns — do not run as an alpha book.
- **Specialty chem = documented FAILURE to capture.** The screen caught DGC's 2019-2020 pre-supercycle
  entry, yet is net-NEGATIVE: the Rev_YoY>0.20 growth gate mistimes entries and the base-effect ejects DGC
  during the actual 2021 supercycle. **DGC's phosphorus alpha is NOT reliably capturable from financials**
  by a value+growth conjunction (honest answer to the dispatch's predictability question).
- **Rubber land-bank = the most valuable artifact, but as a DEFENSIVE value floor, not the land-alpha.**
  Returns lag B&H (−4.6pp) but **MaxDD is −12.5% vs market −43%, Calmar 0.45 > 0.24** — a genuine
  capital-preservation deep-value lens (DPR). The headline land-conversion alpha (PHR re-rate) is NOT
  captured — by the time PB prints <0.8 the land is already priced. Land-as-alpha = uncapturable;
  land-as-downside-floor = real.

None reaches a standalone book. Deploy: fertilizer EVEB+DY as a cyclical-entry lens (cycle-gated);
rubber PB<0.8 + clean-balance-sheet as a defensive deep-value lens inside V2.4; specialty chem = watchlist
only (DGC entry discipline = EVEB<5 + PB<1 + CF_OA ramping, by hand, accepting the supercycle is a bet).
