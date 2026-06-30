# Aviation valuation framework — Sector #14 (airlines + airport/cargo services)

Job Taylor_20260630_074607. Screen: `aviation_screen.py`. Outputs: `data/aviation_infra_monthly.csv`,
`data/aviation_airline_monthly.csv`, `data/aviation_verdict.json`. Registry: `data/results_registry.md`.

## The sector is two unrelated economics sharing an airport

| Sub-sector | Names (prune) | Economics | Right metric | VN reality |
|---|---|---|---|---|
| **Airport / cargo infrastructure** | ACV, SCS, NCT, SGN | concession monopoly, capex/D&A-heavy | **EV/EBITDA (EVEB)** + ROIC moat | real high-ROIC monopolies, but value-uncapturable / microcap-thin |
| **Airlines** | HVN, VJC | capital-intensive deep cyclical, aircraft-financed | **EV/EBITDAR** (intl) → proxy P/B distress + IntCov | no trough-buy exists: HVN near-bankrupt, VJC never cheap |

## International standard → BQ mapping

**Airlines (intl = EV/EBITDAR, R = aircraft rent).** BQ has no EBITDAR → EVEB only (lease cost not
added back, so EVEB understates cross-carrier comparability — use cautiously). High Debt_Eq is BY
DESIGN (aircraft financing) → use **IntCov** not Debt_Eq. Distress entry = **P/B<1** (below
fleet/asset value), gated by CF_OA>0 + NP>0 (profitable survivor). Load factor / RASK not in BQ →
Revenue_YoY as throughput proxy.

**Airport infra (intl = EV/EBITDA + ROIC concession quality).** Same as ports (logistics_port
framework): EVEB primary, ROIC = monopoly-quality proxy, FCF maturity gate (CF_OA+CF_Invest>0),
net-cash names have IntCov=NaN → must PASS. Throughput proxy = Revenue_YoY.

**ICB trap:** SCS (Saigon Cargo) is tagged ICB **5751 'airline'** but is a net-cash cargo terminal;
NCT (also cargo) is 2777. **Screen by NAME, not ICB**, or you misclassify SCS as an airline.

## Backlook (ticker_financial cache — the economics that decide the verdict)

- **HVN** — chronic state-carrier. 2018-19 Debt_Eq 3-5x, IntCov thin 1.2-5x, ROIC5Y 2-4%, NP+thin.
  COVID 2020-24: **PB=0 (equity wiped — NEGATIVE EQUITY), Debt_Eq 57→123→neg, EVEB<0, ROIC deeply
  neg** = near-bankruptcy. 2024+ NP turns +, ROIC_TTM 14-18%, equity restored only 2025Q4.
  → **permanent exclude**; "buying below fleet value" in 2020-21 meant buying negative equity.
- **VJC** — LCC survivor. pre-COVID ROIC5Y 20-28% (genuine LCC economics), Debt_Eq 1.7-2.4 (< HVN),
  positive equity throughout COVID. BUT **P/B never <1** (3-10x always — no distress entry ever),
  DY=0 always, post-COVID ROIC5Y collapsed to negative, CF_OA lumpy/neg, heavy sale-leaseback. Better
  balance sheet than HVN, but not cheap and no longer the pre-COVID machine.
- **ACV** — the monopoly: ROIC5Y 5%→11% rising, IntCov 100-300x (~net cash), Debt_Eq falling 0.8→0.2,
  strong post-COVID throughput. BUT **EVEB rarely <12** (12-30 normal, 47-477 when COVID killed EBITDA),
  **DY=0** (retains for Long Thanh), **FCF<0** (Long Thanh construction capex). Best franchise, but a
  value/FCF screen never buys it → GARP/quality-growth name, not value.
- **SCS** — the gem: ROIC5Y 20%→**49%**, net cash (Debt_Eq 0.05-0.4, IntCov NaN), **real DY 2-5%**,
  FCF+ (asset-light), survived COVID flat (NP ~120-160B). EVEB down to 5.6-8.8 = cheap now.
- **NCT** — cargo cash-cow: ROIC_TTM ~3.0 (50-60%), net cash, EVEB cheap 5-8, lumpy DY 0-9%, stable
  thru COVID. SMALL (ADV ~1.7B), price-patchy in prune (gaps 2023).
- **SGN** — third cargo gem: ROIC5Y 17-46%, net cash, EVEB 4-13 cheap, DY~0. Price-patchy in prune
  (only 2020, 2024-25) → thin/intermittent.

## Screens & results (monthly EW, TC 0.1%, hold-cash-when-empty, self-check 0 VND PASS)

**A — Airport/cargo infra** (EVEB<12 + ROIC5Y≥10% + CF_OA_3Y>0 + (FCF>0 OR DY>4%) + IntCov NaN-or>2
+ Rev_YoY≥−10%): FULL **3.98%** vs B&H 10.23% (**−6.25pp**), IS −8.45pp, OOS −4.07pp — FAILS both.
Holds median 1 name (NCT 69mo + SCS 43mo + SGN 15mo; **ACV 0mo**). Killed by 1-name idiosyncratic
drag (2025 SCS −32% = −76.5pp) + early cash-drag. Ortho custom30V 0% / 8L 0%. Median ADV **1.6B microcap**.

**B — Airline trough** (PB<1 + CF_OA>0 + IntCov>1 + NP>0): **STRUCTURALLY EMPTY, 0 qualifiers ever.**
HVN PB=0 (neg equity) excluded; VJC PB never<1. **No VN airline trough-buy exists.**

**Buy-and-hold reality (2017-10→2026-06 vs VNINDEX 10.21%/DD−45%):** SCS 5.50%/−52%, ACV 1.15%/−63%,
**NCT 17.53%/−51% (only beater, illiquid)**, VJC 8.83%/−57%, HVN 6.02%/**−80.6%**. Even holding the
gems mostly LAGS the index (sharper negative than pharma).

## Durable exports (reusable across the fleet)
1. **Airline trough-buy does NOT exist in VN** — empty screen. **HVN = permanent-exclude** (negative
   equity 2021-24); VJC never cheap (premium LCC, PB never<1).
2. **Screen aviation by NAME not ICB** — SCS misclassified 5751.
3. **ACV = best monopoly franchise but value-uncapturable** (EVEB never<12 + DY0 + Long-Thanh FCF
   drag) → quality-growth/GARP, not a value pick.
4. **DY-uncapturable reconfirmed** (ACV DY=0, cargo DY lumpy/intermittent).
5. **Cargo terminals (SCS/NCT/SGN) = real net-cash high-ROIC monopolies** but microcap-thin (ADV 1.6B)
   + 1-name concentration + listed-expensive de-rate → buy-and-hold single-name lens, NOT a timed book.

## Verdict
**Weakest sector group alongside steel & energy/utilities.** Both sub-screens fail; even the
franchise-quality lens mostly fails to beat the index on a hold basis (only illiquid NCT wins). No
investable aviation book. (Data caveat: young sector, IS≈2017-19, OOS=COVID shock — economics carry
more weight than the curve.)
