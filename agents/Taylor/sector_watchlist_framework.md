# Sector Watchlist Framework — composite of the 15-sector sweep

> **Author:** Taylor (Quant) · **Job:** Taylor_20260630_080124 (final deliverable of the 2026-06-30 sweep) · **For:** DollarBill, user (via Mike)
> **What this is:** a *usable* decision tool, not a re-summary. It tells you **when to buy what**, **which metric to use per sector**, and **what never to buy on a quant screen**. Current statuses are point-in-time on **2026-06-29** BQ data (`ticker` / `ticker_financial` latest rows; DT5G state to 2026-06-25).
> **Source frameworks (15):** banking, retail, RE, logistics/port/shipping, telecom, fertchem/rubber, steel/buildmat, energy/utilities, F&B, tech, pharma, securities, aviation, viettel-logistics (CTR/VTP/TOS). All in `mike/agents/Taylor/*_framework.md`; backtests in `data/results_registry.md`.

---

## Section 1 — Signal Map (current, 2026-06-29)

DT5G regime today = **BULL (state 3, to 2026-06-25)** — risk-on; the euphoria caps are NOT engaged.
*(Note: this corrects the dispatch's "NEUTRAL" assumption — the live `vnindex_5state_dt5g_live` table reads BULL.)*

| Name / group | Primary metric | Entry condition | Current value | Status | Deploy mode |
|---|---|---|---|---|---|
| **CTR** | EV/EBITDA | <9 strong · <11 accumulate (+ROIC5Y>20, ROE_TTM>25) | EVEB **9.9** | **ACCUMULATE** (mid-bucket, not screaming) | Watchlist single-name; capturable book |
| **FPT** | PE vs PE_MA1Y | PE < PE_MA1Y×0.9 (+ROIC5Y>0.12, ROE5Y>0.15) | PE **12.4** vs MA1Y×0.9 = **16.8** | **IN ENTRY WINDOW** (cheap vs own history) | Single-name lens; strongest active signal |
| **FOX** | EV/EBITDA | pullback to <8 (mature-telecom band 4–8x) | EVEB **12.0** | **WAIT** (rich) | Watchlist only |
| **MBB** | P/B vs Gordon justPB | PB < justPB (ROE5Y, COE0.13, g0.05) | PB 1.40 vs **justPB 2.21** | **CHEAP — BUY zone** | Banking compounder (archetype A) |
| **ACB** | P/B vs justPB | same | PB 1.22 vs **2.25** | **CHEAP — BUY zone** | Banking compounder |
| **HDB** | P/B vs justPB | same; ROE_Min3Y 0.241 (best) | PB 1.54 vs **2.34** | **CHEAP — BUY zone** | Banking compounder |
| **TCB** | P/B vs justPB | same | PB 1.25 vs **1.55** | **Modestly cheap** | Banking compounder (thinner margin) |
| **VCB** | P/B vs justPB | same | PB 2.14 vs **1.93** | **NOT cheap on value** (archetype B — forward-ROE only) | Skip on a value screen |
| **SSI** | P/B (+ROE inflection) | PB∈(0,1.8) · ROE_TTM>ROE3Y · IntCov>1.5 | PB 1.68 · 0.139>0.118 ✓ | **QUALIFIES** | Securities screen (DT5G-gated) |
| **VCI** | same | same | PB 1.78 · 0.092>0.083 ✓ | **QUALIFIES (marginal)** | Securities screen |
| **VND** | same | same | PB 1.18 · 0.106 vs ROE3Y 0.108 | **FAILS inflection** (TTM just below 3Y) | Watch for re-cross |
| **HCM** | same | same | **PB 2.10 > 1.8** | **EXCLUDED** (euphoria cap) | — |
| **PVT** | P/B trough | P/B<1 + CF_OA>0 + NP>0 | PB **0.87**, EVEB 3.8 | **TROUGH — buy candidate** | Oil-svc/tanker, high-beta tactical |
| **HAH** | EV/EBITDA | EVEB cheap + ROE strong | EVEB **4.3**, ROE5Y 0.246 | **CHEAP** (container shipper, cyclical) | Tactical cyclical |
| **VSC** | P/B / EVEB | port; EVEB MA1Y was distorted | PB 1.04, EVEB 10.4, ROE5Y 0.093 | **Marginal** (weak ROIC) | Watch |
| **PVD** | P/B trough | high-beta oil bet only | PB 1.04, ROE5Y 0.029 | **Tactical only** (no quality) | Risk-on tactical, never core |
| **GMD** | EV/EBITDA | EVEB cheap vs build-phase | EVEB **15.0** (rich) | **WAIT** | Watch |
| **DHG** | PE (buy & hold) | quality floor ROE5Y>0.15, ROIC5Y>0.15 | PE 13.6<MA5Y 15.1, ROIC 0.22 | **Quality — accumulate** | Buy-and-hold, **no timing** |
| **DBD** | PE (buy & hold) | quality floor | ROE5Y 0.181, ROIC 0.178; PE 17 not cheap | **Hold-quality, not cheap** | Buy-and-hold |
| **DMC / IMP** | — | ROE5Y<0.15 | DMC 0.126 / IMP 0.138 | **Quality-floor REJECT** | Exclude |

---

## Section 2 — Five universal rules (reused across every sector)

**Rule 1 — Split by economics, not by ICB code.** Almost every ICB code lumps unrelated businesses: steel∥cement∥pipes (one code), util∥oil-svc∥renewables, FMCG∥seafood, residential∥industrial-park RE, airport-concession∥airline. A single P/E or P/B across the code is wrong for all of them. **Hand-curate sub-universes by name.** ICB traps confirmed: SCS tagged "airline" is a net-cash cargo terminal; CTR tagged "construction" is telecom-infra.

**Rule 2 — DY is uncapturable in BQ → scoring bonus, never a gate.** `DY` is populated only in dividend-declaration quarters (~20–30% of rows; PVD literally 0/79, HT1 1/75, MSN 7/67). A hard `DY>X%` gate fires sporadically and *ejects a known payer* in the 70%+ of quarters DY isn't recorded. This kills the entire "yield screen" archetype (cement, mature utilities, FMCG staples, industrial-park REITs). Use DY only as a tie-break bonus.

**Rule 3 — A valuation LENS ≠ a tradeable BOOK.** A metric can cleanly *explain* forward returns yet produce **no OOS monthly-book edge** — because the names are megacaps that re-rate once then de-rate (FMCG, tech, telecom, retail), or the edge is a single event (seafood = 2022 ASP, energy oil-svc = 2020-21). **Quality compounders are buy-and-hold; timing destroys them** (pharma: same names +15.96% B&H but the timed screen loses both IS and OOS by holding cash 82% of months). Always ask: lens or book? Only wire a book if the edge survives **walk-forward OOS 2020+**.

**Rule 4 — The valuation primary is dictated by the economics:**
| Economics | Primary metric | Why generic P/E fails |
|---|---|---|
| Capex/D&A-heavy concession/infra (ports, telecom, towers, airport, cement, mature utility) | **EV/EBITDA** | heavy D&A distorts earnings |
| Financials (banks, brokers) | **P/B + Gordon justified-P/B** | NP violently cyclical; leverage is the product |
| Growth retailer | **P/S** | P/E suppressed during store-expansion ramp |
| Commodity cyclical (steel, seafood, oil-svc, fertilizer, latex) | **P/B trough-buy** | margin lumpy with the global commodity |
| Real-estate developer | **P/B** (proxy for discount-to-NAV; land bank not in BQ) | revenue handover-lumpy, P/E & P/S meaningless |
| Capital-light IT-services / asset-light infra compounder | **PE / EV-EBITDA + ROIC moat** | — |

**Rule 5 — Match the leverage gate to the business; treat NaN-IntCov as PASS.** `Debt_Eq` is meaningless for banks/brokers (leverage *is* the product) and for airlines (aircraft financing) → use **IntCov** instead. **Net-cash names print IntCov=NaN** (DVP, VSC, ACV, DHG, the big banks) — that is the *best* case, so NULL must PASS the gate, never fail it. Conversely for commodity cyclicals, leverage IS the survival metric: the steel "P/B<1 = buy below replacement cost" rule is a **TRAP** because the names trading P/B<1 are the *over-levered* ones (HSG/NKG), not the quality compounder (HPG).

> *Corollary (capture-failure law):* a backward quality floor (ROE5Y/ROIC5Y>15%) structurally **ejects forward growth-build stories** — IMP's ETC build-out, VTP's scale-up, VCB/PNJ's margin-turnaround. These are real businesses the screen *cannot* catch without look-ahead. Accept the miss; do not loosen the floor to chase them.

---

## Section 3 — Sector → primary-metric lookup

To evaluate any single stock, find its sector and use the primary metric (secondary in parens):

| Sector | Sub-type | Primary metric | Quality gate | Notes |
|---|---|---|---|---|
| **Banking** | — | **P/B vs Gordon justPB** = (ROE5Y−0.05)/0.08 | ROE5Y>COE(0.13); ROE_Min3Y (asset-quality proxy) | NEVER use Debt_Eq/CF_OA/ROIC. NIM/NPL/CAR not in BQ |
| **Securities** | — | **P/B ∈(0,1.8)** (cap = euphoria gate) | ROE_TTM>ROE3Y (inflection), IntCov>1.5 | Highest-beta sector (β1.27). DT5G adds RETURN here, not just insurance |
| **Retail** | growth | **P/S** (EV/EBITDA secondary) | ROIC5Y/ROE5Y (not point-in-time ROIC) | P/E lies during expansion |
| **Real estate** | residential | **P/B** (<1.5 distress) | Debt_Eq + IntCov (survival); NP_P0>0; GPM-trend | Rev_YoY useless (lumpy handover); best entry post-credit-crunch |
| | industrial park | **P/B + DY** (REIT-like) | ROIC5Y high | structurally illiquid (NTC ADV ~3B) |
| **Ports/infra** | port concession | **EV/EBITDA** (PCF, P/B 2nd) | ROIC5Y≥5% + ROIC_Trailing; FCF=CF_OA+CF_Invest | net-cash → IntCov NaN = PASS |
| **Shipping** | marine cyclical | **P/B trough** | CF_OA>0 | high-beta cycle |
| **Telecom** | infra/fixed | **EV/EBITDA** (mature 4–8x) | FCF; ROIC | thin universe; read FOX directly, not via FPT |
| **Tech** | IT-services | **PE vs PE_MA1Y** | ROIC5Y>0.12 (VN-calibrated, not Infosys 18+), ROE5Y>0.15 | ONE name = FPT. Don't gate FPT on RevYoY (divestment artifact) |
| **Fertilizer/chem** | commodity | **EV/EBITDA up-cycle, P/B trough** | CF_OA, Debt_Eq+IntCov | DPM/DCM hostage to gas-policy |
| | specialty (DGC) | EV/EBITDA + ROIC | — | supercycle name, not a durable value compounder |
| **Rubber** | land-bank conv. | **P/B<1.0** (hidden land asset) | — | ROIC5Y data-corrupted (PHR 515%) — don't use |
| **Steel** | commodity | EV/EBITDA up-cycle | **IntCov>1.5 (survival)** | P/B<1 is the leverage TRAP; only HPG compounds |
| **Cement** | regional oligopoly | EV/EBITDA + CF_OA | leverage | DY uncapturable → no yield screen |
| **Pipes/specialty** | NTP/BMP/VCS | PE / EV-EBIT | ROIC>15–20%, clean BS | real compounders but no OOS book |
| **Energy/utilities** | mature utility | **EV/EBITDA + FCF>0** (maturity gate) | FCF separates cash-machine from build-phase | structurally LAG index — defensive |
| | oil services | P/B<0.8 trough | CF_OA>0 (reject COVID neg-cash trap) | high-beta oil bet, −68% DD, tactical only |
| **F&B** | FMCG staples | PE<PE_MA1Y + ROE5Y>18% | **GPM-moat: avg8q≥22% AND CV<25%** (rejects KDC) | lens not book |
| | seafood | P/B<1.2 trough + GPM turning | CF_OA_3Y>0, Debt_Eq<1.5 (duty-cycle filter) | VHC un-capturable (quality never cheap) |
| **Pharma** | generics/distrib | **PE** (buy-and-hold) | ROE5Y>0.15 AND ROIC5Y>0.15 | TIMING destroys it — hold, don't trade |
| **Aviation** | airport concession | EV/EBITDA + ROIC | FCF | value-uncapturable / microcap-thin |
| | airline | P/B<1 distress + IntCov | NP>0, CF_OA>0 | no trough-buy exists (see exclude list) |

---

## Section 4 — Permanent exclude list (never buy on a quant screen)

| Name / group | Reason |
|---|---|
| **HVN** | Negative equity through COVID; "buying below fleet value" = buying a near-bankruptcy. Permanent. |
| **VJC** | P/B never <1 — no distress entry ever exists; DY=0; post-COVID ROIC collapsed. |
| **DGC (on value)** | Returns came from a one-off phosphorus supercycle, not durable compounding. Not value-screenable today (expensive); a momentum/cycle name, not a value book. |
| **VTP (on quality)** | Broken FedEx-early thesis; quality screen rejects it. Only a contrarian P/S-mean-reversion *lens*, never a quality book. |
| **HSG, NKG, POM, SMC** | Steel leverage traps — the P/B<1 names are over-levered with thin IntCov; can be wiped in a downcycle. (Only HPG compounds — and HPG never gets truly cheap on P/B.) |
| **KDC** | Serial restructurer; GPM swings 15%→58% (CV 0.38) → no moat. Rejected by the GPM-stability gate. |
| **CMX** | Seafood with median Debt_Eq 3.5 — fails the duty-cycle balance-sheet filter outright. |
| **NVL** | RE with un-payable debt — the canonical "cheap P/B on un-serviceable leverage" trap. |
| **GEG, PC1, SBA (renewables)** | Un-screenable — look expensive + 1.6–2.5x levered + FCF-negative *while building* FIT assets; the windfall is a policy event, not a financial signal. Documented failure. |
| **DMC, IMP, TRA (pharma)** | ROE5Y<0.15 quality-floor reject (IMP = the documented ETC-growth capture failure); also going illiquid. |
| **TOS** | Best fundamentals of the Viettel-logistics trio but ADV ~1.08B → un-tradeable. Watchlist/lens only. |

*Point-in-time (not permanent):* **VCB** and **HCM** are excluded *today* — VCB is archetype-B (premium P/B justified only by forward ROE; a value screen can't catch it), HCM is above the PB<1.8 euphoria cap. Both can re-qualify when price/regime change.

---

## Section 5 — Current watchlist (point-in-time, 2026-06-29)

**Only OOS-verified signals listed. Ranked by conviction.**

**TIER 1 — in entry zone, capturable, act now:**
- **FPT** — PE 12.4 vs PE_MA1Y×0.9 = 16.8 → **deep in the entry window**, quality intact (ROIC5Y 0.177, ROE5Y 0.266). Strongest active single-name signal in the sweep.
- **Banks MBB / ACB / HDB** — all trade **well below Gordon justified-P/B** (1.40<2.21, 1.22<2.25, 1.54<2.34) with strong never-destroyed-equity floors (ROE_Min3Y 0.18–0.24). Archetype-A cheap-re-rating setups. **HDB** has the highest ROE floor; **ACB** the widest discount.

**TIER 2 — accumulate / qualifies:**
- **CTR** — EVEB 9.9, mid-bucket (hist +44%/89% fwd-12M). Accumulate; a print <9 (last seen 2022) is the screaming buy. Quality elite (ROIC5Y 0.211, ROE_TTM ~30%).
- **TCB** — modestly below justPB (1.25<1.55); cheaper bank but thinner quality margin.
- **SSI / VCI** — both pass the securities screen (PB<1.8, ROE inflection up, IntCov ok). VCI marginal (PB 1.78). DT5G=BULL → the gate is open; **this is the one sector where DT5G gating ADDS return** (DD −66→−32%, CAGR 17.7→27.7%).

**TIER 3 — tactical / trough (high-beta, size small):**
- **PVT** — P/B 0.87 trough, EVEB 3.8, profitable (ROE5Y 0.136). Cleanest oil-svc/tanker trough.
- **HAH** — EVEB 4.3, ROE5Y 0.246 — cheap container cyclical (not a P/B trough but cheap on EV/EBITDA).

**BUY-AND-HOLD (no timing — accumulate on weakness, never trade the screen):**
- **DHG** — PE 13.6 < MA5Y 15.1, ROIC5Y 0.22, Taisho moat. The quality pharma anchor.

**WAIT / WATCH (rich or failing a gate today):**
- **FOX** (EVEB 12 → want <8) · **GMD** (EVEB 15) · **VND** (ROE inflection not yet crossed) · **VSC** (weak ROIC) · **HCM** (PB>1.8 cap) · **VCB** (above justPB).

---

## Section 6 — Integration with V2.4 (production)

**What V2.4 already covers:**
- **BAL book** (SIGNAL_V11 momentum) + **LAG book** (PEAD/earnings drift), static 50/50, state-allocated.
- The books are **already bank-heavy** (banking ~74% of some windows) and tilt to liquid quality/industrial names — so MBB/ACB/HDB/TCB exposure is **largely captured already**. Don't double-count banks.
- **custom30V** = the NEUTRAL-state "parked-cash" beta basket (most-trusted sleeve, +7.4pp Full) — it is a beta parker, **not** an alpha picker.

**What these sector screens add (the gaps V2.4 doesn't reach):**
1. **Growth-priced single names V2.4's value/momentum books miss** — **FPT** (PE-vs-history timing) and **CTR** (EVEB lens). These compound but rarely surface in a momentum or PEAD book at the right entry.
2. **A regime-gated high-beta sleeve** — **securities (SSI/VCI)**: the one sector where DT5G is a *return-enhancer*. A small DT5G-gated brokerage sleeve, on only in non-CRISIS, is additive and uncorrelated with the BAL/LAG cores.
3. **Trough-cyclical tactical entries** — PVT/HAH on the P/B/EVEB trough conditions, sized small, risk-on only.
4. **A buy-and-hold quality anchor** — DHG (pharma): explicitly *outside* the timed books (timing destroys pharma), held as a low-vol ballast.

**Recommended usage (not a wiring proposal — for DollarBill to plan):**
- Treat this watchlist as a **discretionary overlay candidate list**, NOT an automated book. Most sector screens are *lenses, not books* (Rule 3) — they failed OOS as standalone monthly strategies, so do **not** wire them as new auto-allocated sleeves.
- **Flow:** sector watchlist (this doc) → DollarBill builds a discretionary plan `data/plan_<acct>_<T+1>.json` for the Tier-1/2 names within current V2.4 weight and DT5G state → user approves → Mafee executes plan-bound.
- The **only** screen with a genuine standalone case for a *small* gated sleeve is **securities** (return-additive under DT5G). Everything else is overlay/discretionary or buy-and-hold.
- **Hard constraints unchanged:** DT5G state caps gross exposure; per-name caps and `data/trading_rules.json` limits apply; live changes need user approval.

---

### Auditability
All current values are BQ-live (`tav2_bq.ticker` / `ticker_financial`, latest rows 2026-06-29 / 2026Q1; DT5G `vnindex_5state_dt5g_live` to 2026-06-25). Backtest provenance for each sector is in `data/results_registry.md` and the 15 per-sector framework docs. No backtest re-run here — synthesis of already-pinned findings per the dispatch.
