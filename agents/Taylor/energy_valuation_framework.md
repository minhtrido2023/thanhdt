# Energy / Utilities valuation framework (Taylor, job Taylor_20260630_070640)

**Sector #9 of the sector-by-sector valuation sweep.** ICB lumps Utilities + Oil&Gas together, but
three sub-sectors have entirely distinct economics, so the screen is THREE hand-curated sub-universes.
Script: `energy_screen.py`. Outputs: `data/energy_{util,oilsvc,renew}_monthly.csv`, `data/energy_verdict.json`.

## Verdict (one line)
**Weakest sector group of the sweep alongside steel.** No standalone book. Mature utilities structurally
*lag* (defensive, don't compound — FAIL IS, ~flat OOS); oil services are a pure high-beta oil-cycle bet
(−68% DD, FAIL IS / star OOS — tradable only tactically in risk-on); renewables are a documented capture
FAILURE. Two durable exports: the **DY-uncapturable** data gap and the **FCF>0 maturity gate**.

## Part 1 — International framework → VN reality
| Sub-sector | Textbook method | VN reality (what actually works in BQ) |
|---|---|---|
| **Mature utility** (hydro/thermal/conglomerate) | EV/EBITDA + P/FCF; DY yield play when mature | EVEB primary OK, but **DY is a TRAP** (see below). Real signal = **FCF>0** (cash machine after maintenance capex). Cash-machine identification is REAL but the names structurally **lag the index** — defensive, not compounders. |
| **Oil services** (PVD/PVS/PVT) | P/B trough-buy when oil crashes (rig/vessel < book) | P/B<0.8 + **CF_OA>0 discipline** (reject the cheap-on-negative-cash COVID trap). Mechanically correct, but **high-beta oil-cycle bet**: −68% DD, fails 2017-19, stars 2020-26. |
| **Renewables** (GEG/PC1/SBA) | EV/EBITDA + P/B asset play; FIT windfall | **Un-screenable.** Look expensive + 1.6-2.5x levered + FCF-negative *precisely while building* FIT assets. Windfall is a policy event, not a financial signal. Documented FAILURE. |

## Part 2 — The two durable findings

### (a) DY is uncapturable across VN energy → no "utility yield screen" in BQ
DY is only populated in **dividend-declaration quarters** (~20-30% of rows), not continuously:
UTIL 242/699 ASOF rows, OILSVC 42/444, RENEW 37/228. Pure hydros are worst-hit at year-ends
(VSH 21/85, SJD 14/79); PVD literally **0/79**. A hard `DY>4%` gate fires sporadically and *ejects a
known payer* in the 70% of quarters DY isn't recorded. → **DY used as a SCORING bonus, never a gate.**
This is the same data gap found in cement (steel_buildmat sector) — it generalizes to all VN dividend-yield screens.

### (b) FCF>0 is the maturity gate (the real alpha for utilities)
`FCF = CF_OA_P0 + CF_Invest_P0` (capex is negative). It cleanly separates a paid-off cash machine
from an expansion-phase plant. Verified perfectly on VSH: the Thượng-Kon-Tum **expansion (2017-19,
FCF deeply negative) is REJECTED**; the **post-capex value entry (2022-24, FCF strongly positive) is
CAUGHT**. Of 267 EVEB/leverage/IC-passing utility rows, the FCF gate rejects 82 expansion-phase rows.

## Part 3 — Backlook anchors (ticker_financial cache)
- **SJD 2018Q4** EVEB5.07 FCF+145B ROE5Y17.6% Debt0.50 IC2.9 → textbook mature hydro cash-machine
- **NT2 2019Q4** EVEB4.24 FCF+692B DY5.3% ROIC5Y10.1% IC12.5 → PPA gas, cheap + (rarely) yielding
- **POW 2020Q4** EVEB5.36 FCF+3.96T PB0.90 → mature gas-thermal cash machine
- **VSH 2018Q4** EVEB19.9 FCF−630B Debt1.66 → expansion, FCF gate rejects (correct)
- **VSH 2022Q4** EVEB4.84 FCF+363B Debt0.93 → value entry *after* capex done (caught)
- **PVD 2014Q4** EVEB5.10 **PB1.51 (pre-crash)** → not a trough yet, correctly missed
- **PVD 2016Q2** PB0.69 CF_OA+95B → trough caught (below asset value, still cash-positive)
- **PVD 2020Q4** PB0.49 CF_OA−70B → "cheapest" PB is the COVID value-trap; CF_OA gate rejects the Q2+ rows
- **PVT 2020Q4** EVEB2.97 PB0.78 CF_OA+509B IC176 → oil-transport, mature cash-gen at trough PB
- **GEG 2021Q4** EVEB14.4 CF_OA−1.84T Debt2.55 DY0 → renewables build-phase, un-screenable

## Part 4 — The three screens (point-in-time monthly, ADV≥1B prune universe)
- **A — Mature utility** (VSH,SJD,NT2,PPC,REE,POW): `EVEB∈(0,8) & FCF>0 & CF_OA_3Y>0 & Debt_Eq<2.0 & IntCov>2.0`; score `−EVEB, +FCF, +DY(bonus)`.
- **B — Oil services trough** (PVD,PVS,PVT): `PB∈(0,0.8) & CF_OA_P0>0 & Debt_Eq<2.0`; score `−PB, +CF_OA`. **HIGH BETA — design intent: hold only in DT5G NEUTRAL/BULL** (backtest is unconditional EW; caveat reported not gated).
- **C — Renewables** (GEG,PC1,SBA): `EVEB∈(0,10) & IntCov>1.5 & Revenue_YoY>0 & CF_OA_3Y>0`; score `−EVEB, +DY(bonus), +IntCov`. Expected weak.

## Part 5 — Backtest results (2014-01 → 2026-04, net of 0.1% TC, self-check 0 VND PASS all three)
| Screen | Full CAGR | edge vs B&H | IS edge | OOS edge | MaxDD | ortho c30v / 8L | med ADV |
|---|---|---|---|---|---|---|---|
| **A Mature utility** | 4.16% | **−6.07pp** | −12.19pp | +0.22pp | −43.5% | 12.5% / 0.0% | 9.3B |
| **B Oil services** | 11.06% | +0.82pp | **−14.95pp** | **+18.60pp** | **−68.1%** | 33.8% / 31.5% | 44.2B |
| **C Renewables** | 2.30% | **−7.94pp** | −12.69pp | −3.10pp | −44.9% | 2.5% / 0.0% | 14.2B |

**Reading:**
- **A FAILS** — the cash-machine thesis is real (SJD 44mo / NT2 63mo / POW 45mo caught; VSH expansion rejected, post-capex caught) but mature VN utilities are **defensive laggards**: 2019 −30% (thermal crush), they trail every bull year. Confirms utilities belong in a *park-cash / income tilt*, NOT an alpha book. (Ortho to custom30V only 12.5% → they're not even much in the parking basket today — but adding them wouldn't add alpha.)
- **B** is the textbook two-faced cyclical: a disaster in the oil malaise (IS −14.95pp, 2017-19) and a star in the oil recovery (OOS +18.60pp; 2020 +21, 2022 +47, 2025 +18). **−68% DD makes it un-ownable standalone.** It is a **tactical oil-cycle overlay for risk-on regimes only**, exactly the design caveat. The trough discipline is mechanically sound (miss-2014 pre-crash ✓, reject COVID-Q2+ negative-CF ✓, of 182 cheap-PB rows the CF_OA gate rejects 59).
- **C** is a **documented capture FAILURE** as predicted — renewables can't be valued on financials during their FIT build-out.

## Orthogonality / deployment
- A & C are orthogonal to custom30V/8L (≈0-12%) but have **no edge** → nothing to add.
- B overlaps ~33% with both (PVD/PVS leak into momentum/quality baskets in oil rallies) and has edge **only** as a regime-timed tactical sleeve, never a standalone book.
- **Net: Energy contributes a valuation/risk LENS, not a book.** Durable team takeaways = the DY-uncapturable rule and the FCF>0 maturity gate (both reusable across other capex-heavy/dividend sectors).
