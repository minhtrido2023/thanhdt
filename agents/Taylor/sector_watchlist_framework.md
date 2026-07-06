# Sector Watchlist Framework — composite of the 15-sector sweep

> **Author:** Taylor (Quant) · **Job:** Taylor_20260630_080124 (final deliverable of the 2026-06-30 sweep) · **For:** DollarBill, user (via Mike)
> **What this is:** a *usable* decision tool, not a re-summary. It tells you **when to buy what**, **which metric to use per sector**, and **what never to buy on a quant screen**. Current statuses are point-in-time on **2026-06-29** BQ data (`ticker` / `ticker_financial` latest rows; DT5G state to 2026-06-25).
> **Source frameworks (15):** banking, retail, RE, logistics/port/shipping, telecom, fertchem/rubber, steel/buildmat, energy/utilities, F&B, tech, pharma, securities, aviation, viettel-logistics (CTR/VTP/TOS). All in `mike/agents/Taylor/*_framework.md`; backtests in `data/results_registry.md`.

---

## Section 0 — Consolidated Classification (20 sectors/archetypes)

> **Added 2026-07-06** (job `Taylor_20260706_050653`). The sweep now spans **20 sector/archetype frameworks**. This section triages ALL of them into three buckets so a reader instantly knows *which knowledge produces a name to act on vs. which only prevents a mistake vs. which only re-reads a name already chosen*. Point-in-time statuses refreshed on **2026-07-03** BQ data (`ticker`/`ticker_financial` latest rows; `vnindex_5state_dt5g_live` = **BULL, state 3**).

### The three buckets

- **Group A — ACTIONABLE** *(a concrete name + a live entry rule, whether firing now or WATCH-with-armed-trigger)*: **8 sectors** → Banking, Tech(FPT), Securities, Logistics/Port/Shipping, Viettel-infra(CTR), Textile(MSH), Pharma(DHG buy-hold), Livestock(DBC).
- **Group B — DEFENSIVE / KNOWLEDGE-ONLY** *(no current buy candidate; the value is an exclude-list or a lens with an empty watchlist that stops you buying a trap)*: **10 sectors** → Retail, Real-estate, Telecom, Fertchem/rubber, Steel/buildmat, Energy/utilities, F&B, Aviation, Insurance, Construction.
- **Group C — GOVERNANCE / METHOD OVERLAY** *(cross-cutting lens applied ON TOP of a name already chosen by its own sector; never an independent name source)*: **2 archetypes** → SOE-governance, Holdco/Conglomerate-SOTP.

### Group A — actionable names, current status (2026-07-03)

| Name | Sector (#) | Primary lens | Current value | Status | Mode |
|---|---|---|---|---|---|
| **FPT** | Tech (10) | PE vs PE_MA1Y×0.9 | PE **12.7** < 16.8 (MA1Y 18.7) ; ROIC5Y 0.177, ROE5Y 0.266 | **IN ENTRY WINDOW** — strongest active signal | Single-name lens |
| **MBB** | Banking (1) | P/B vs Gordon justPB | PB **1.38** < justPB **2.21** (ROE5Y .227) | **CHEAP-BUY** | Compounder (archetype A) |
| **ACB** | Banking (1) | same | PB **1.33** < **2.25** (ROE5Y .23) | **CHEAP-BUY** (wide discount) | Compounder |
| **HDB** | Banking (1) | same | PB **1.62** < **2.35** (ROE5Y .238, ROE_Min3Y **.241** best floor) | **CHEAP-BUY** | Compounder |
| **TCB** | Banking (1) | same | PB **1.28** < **1.55** (ROE5Y .174) | **Modestly cheap** (thinner quality) | Compounder |
| **CTR** | Viettel-infra (14) | EV/EBITDA | EVEB **10.1** (<11 accum, <9 screaming) ; ROIC5Y .211, ROE_TTM .298 | **ACCUMULATE** (mid-bucket) | Single-name lens |
| **SSI** | Securities (12) | P/B<1.8 + ROE inflection + IntCov>1.5 | PB **1.72** ✓, ROE_TTM .139>ROE3Y .118 ✓, IntCov 3.3 ✓ | **QUALIFIES** (DT5G BULL → gate OPEN) | DT5G-gated sleeve |
| **VCI** | Securities (12) | same | PB **1.66** ✓, .092>.083 ✓, IntCov 2.5 ✓ | **QUALIFIES** (marginal, low ROE) | DT5G-gated sleeve |
| **PVT** | Logistics (4) | P/B trough | PB **0.86**<1, EVEB 3.8, CF_OA+ , ROE5Y .136 | **TROUGH-BUY** | Tactical high-beta (size small) |
| **HAH** | Logistics (4) | EV/EBITDA | EVEB **4.3**, ROE5Y .246, GPM .40>.35 improving | **CHEAP** cyclical | Tactical high-beta |
| **MSH** | Textile (16) | PE vs PE_MA1Y | PE **5.9** < MA1Y 7.6, ROE5Y **.249**, IntCov 7.7 ✓, GPM .216>.167 | **IN ENTRY WINDOW** (elite quality, even cheaper vs 06-29) | Buy-and-hold-on-weakness single-name (timing destroys it) |
| **DHG** | Pharma (11) | PE (buy-hold) | PE **13.6** < MA5Y 15.1, ROIC5Y .22, ROE5Y .217 | **ACCUMULATE** (no timing) | Buy-and-hold quality anchor |
| **DBC** | Livestock (17) | P/B trough **+ GPM-turn** | PB **0.94**<MA1Y 1.34 ✓ **but GPM_P0 .170 ≈ GPM_P4 .172 → turn NOT firing** ; hog↓yoy / feed↑ overlays both say hold | **WATCH** (value half present, margin-inflection half absent) | High-beta cyclical-timing; buy only on confirmed GPM turn-up |

**Group-A WATCH-adjacent (in the actionable sectors but not yet qualifying):**
- **VND** (Securities) — PB 1.31 ok but ROE_TTM .106 < ROE3Y .108 → **fails inflection**, watch for re-cross.
- **HCM** (Securities) — PB **2.14 > 1.8** euphoria cap → **excluded today**, re-qualifies on a pullback.
- **VCB** (Banking) — PB **2.21 > justPB 1.93** → archetype-B (premium justified by forward ROE only); a *value* screen can't catch it. Skip on value; not a trap.

**Key read:** every Group-A status is unchanged from the 2026-06-29 snapshot — a few names are marginally *cheaper* (FPT, MSH, banks), none crossed a state boundary in the week. This is the expected behaviour (Rule 3: these are slow lenses) and is exactly why the harvesting cadence below is **weekly, transition-alerted**, not daily.

### Group B — defensive / knowledge-only (no buy candidate now)

| Sector (#) | Why it's here (no actionable name) | The value it provides |
|---|---|---|
| **Retail (2)** | P/S lens; MWG/PNJ are megacaps that re-rate once (lens ≠ book, fails OOS) — no name in a clean entry today | Use P/S not P/E during store-expansion ramps |
| **Real-estate (3)** | Best entry is post-credit-crunch (not now); no developer at a clean distress-P/B with serviceable leverage | **NVL = canonical un-serviceable-debt trap**; P/B proxies discount-to-NAV |
| **Telecom (5)** | FOX EVEB **12.0** → rich (want <8); thin universe | Read FOX directly on EV/EBITDA, never via FPT |
| **Fertchem/rubber (6)** | DPM/DCM hostage to gas-policy; no trough firing; rubber P/B<1 land-lens not triggering | Renewables (GEG/PC1/SBA) un-screenable exclude |
| **Steel/buildmat (7)** | P/B<1 = **leverage TRAP** (the cheap names are the over-levered ones); only HPG compounds and never gets cheap | **HSG/NKG/POM/SMC exclude**; IntCov>1.5 is the survival gate |
| **Energy/utilities (8)** | Mature utilities structurally lag (defensive); oil-svc trough is tactical-only (PVD no quality, never core) | FCF>0 maturity gate separates cash-machine from build-phase |
| **F&B (9)** | FMCG lens ≠ book; VHC never cheap while quality; no name qualifying | **KDC/CMX exclude**; GPM-moat gate (avg8q≥22% ∧ CV<25%) |
| **Aviation (13)** | Weakest sector; value uncapturable / microcap-thin; no qualifiers exist | **HVN/VJC exclude** (no distress-entry ever exists) |
| **Insurance (15)** | No edge found; flagships trade a premium P/B (2.12× SOE); no candidate | Confirms *don't* buy insurers on a value screen |
| **Construction (18)** | Risk/exclusion framework only — screen is an EXCLUSION filter (in cash 84% of months), not entry; POC accounting makes P/E noise and P/B-trough a TRAP | **HTN = live HBC-repeat AVOID** (DSO 2425, AR/Rev 49×); CF_OA + DSO-trend gate dodges −62%→−18% DD |

### Group C — governance / method overlays (never a name source)

| Archetype (#) | What it is | How to use it |
|---|---|---|
| **SOE-governance (19)** | State-control lens (apply when State controls >50%/de-facto) | Mild return DRAG (state% IC −0.034, SOE −5pp/yr vs private peers); no governance discount to buy (flagships premium); DY = policy variable (income trap); thin float is the one measurable signature. **Adjust reading/sizing of a name chosen elsewhere; never a buy source.** |
| **Holdco/Conglomerate-SOTP (20)** | Valuation METHOD: `coverage = ParentMC / Σ(stake × listed-sub MC)` | Value the parts, not a blended multiple. **Discount does NOT mean-revert (trap); premium = optionality that deflates in CRISIS.** Use to understand what you're paying for + size optionality/leverage risk; **do NOT trade the discount.** |

**Both overlays: don't wire, don't gate.** They change how you *read/size* a name already surfaced by a Group-A sector, nothing more.

---

## Section 1 — Signal Map (6-state standardized; live via `sector_lens_monitor.py`)

DT5G regime today = **BULL (state 3, to 2026-06-25)** — risk-on; the euphoria caps are NOT engaged.
*(Note: this corrects the dispatch's "NEUTRAL" assumption — the live `vnindex_5state_dt5g_live` table reads BULL.)*

> **Standardized 2026-07-06** (job `Taylor_20260706_062405`). The old free-text status labels are replaced by the **6-state model** below; the numeric content is unchanged (point-in-time **2026-06-29** BQ rows). This table is now **regenerated live** by `sector_lens_monitor.py` (root `WorkingClaude/`, read-only, weekly), which reads the BQ DuckDB cache + the DBC hog/feed overlay, evaluates each framework's OWN entry condition, writes `data/sector_lens_status_<date>.csv`, and alerts only on a **state transition**. Run it for the current read; the values frozen here are the 2026-06-29 baseline.

**The 6 states** (a name is exactly one):
1. **EXCLUDED** — fails a hard gate (quality floor / leverage / forensic flag / euphoria cap).
2. **RICH_WAIT** — passes the gate but is currently EXPENSIVE vs its own history.
3. **WATCH** — passes the gate + cheap, but no confirmed turn/catalyst yet.
4. **ARMED** — *(only for a fast-proxy/slow-confirm sector; today ONLY DBC via the hog-feed spread)* early-warning has turned supportive, not yet confirmed.
5. **BUY** — confirmed entry; sub-mode **STRONG** (deep in window) vs **ACCUMULATE** (moderate), using each framework's OWN thresholds (only CTR defines a STRONG line: EVEB<9).
6. **STALE** — data feed not fresh → fail-safe holds the last known state, never fabricates.

| Name / group | Primary metric | Entry condition | Current value (2026-06-29) | State | Deploy mode |
|---|---|---|---|---|---|
| **CTR** | EV/EBITDA | <9 strong · <11 accumulate (+ROIC5Y>20, ROE_TTM>25) | EVEB **9.9** | **BUY · ACCUMULATE** (mid-bucket [9,11), not the <9 screaming buy) | Watchlist single-name; capturable book |
| **FPT** | PE vs PE_MA1Y | PE < PE_MA1Y×0.9 (+ROIC5Y>0.12, ROE5Y>0.15) | PE **12.4** vs MA1Y×0.9 = **16.8** | **BUY · ACCUMULATE** (in entry window, cheap vs own history) | Single-name lens; strongest active signal |
| **FOX** | EV/EBITDA | pullback to <8 (mature-telecom band 4–8x) | EVEB **12.0** | **RICH_WAIT** (rich) | Watchlist only *(not in monitor universe)* |
| **MBB** | P/B vs Gordon justPB | PB < justPB (ROE5Y, COE0.13, g0.05) | PB 1.40 vs **justPB 2.21** | **BUY · ACCUMULATE** (cheap) | Banking compounder (archetype A) |
| **ACB** | P/B vs justPB | same | PB 1.22 vs **2.25** | **BUY · ACCUMULATE** (widest discount) | Banking compounder |
| **HDB** | P/B vs justPB | same; ROE_Min3Y 0.241 (best) | PB 1.54 vs **2.34** | **BUY · ACCUMULATE** (best ROE floor) | Banking compounder |
| **TCB** | P/B vs justPB | same | PB 1.25 vs **1.55** | **BUY · ACCUMULATE** (modestly cheap, thinner margin) | Banking compounder |
| **VCB** | P/B vs justPB | same | PB 2.14 vs **1.93** | **RICH_WAIT** (archetype B — premium justified by forward-ROE only; value screen can't catch) | Skip on a value screen |
| **SSI** | P/B (+ROE inflection) | PB∈(0,1.8) · ROE_TTM>ROE3Y · IntCov>1.5 | PB 1.68 · 0.139>0.118 ✓ | **BUY · ACCUMULATE** (qualifies; DT5G gate open) | Securities screen (DT5G-gated) |
| **VCI** | same | same | PB 1.78 · 0.092>0.083 ✓ | **BUY · ACCUMULATE** (qualifies, marginal) | Securities screen |
| **VND** | same | same | PB 1.18 · 0.106 vs ROE3Y 0.108 | **WATCH** (fails inflection — TTM just below 3Y) | Watch for re-cross |
| **HCM** | same | same | **PB 2.10 > 1.8** | **EXCLUDED** (euphoria cap) | — |
| **PVT** | P/B trough | P/B<0.9 + CF_OA_3Y>0 + Debt_Eq<2.0 | PB **0.87**, EVEB 3.8 | **BUY · ACCUMULATE** (trough; tactical, size small) | Oil-svc/tanker, high-beta tactical |
| **HAH** | EV/EBITDA | EVEB<10 + ROE5Y>0.15 + CF_OA_3Y>0 | EVEB **4.3**, ROE5Y 0.246 | **BUY · ACCUMULATE** (cheap cyclical container shipper) | Tactical cyclical |
| **VSC** | P/B / EVEB | port; EVEB MA1Y was distorted | PB 1.04, EVEB 10.4, ROE5Y 0.093 | **WATCH** (weak ROIC) | Watch *(not in monitor universe)* |
| **PVD** | P/B trough | high-beta oil bet only | PB 1.04, ROE5Y 0.029 | **WATCH** (no quality; tactical only) | Risk-on tactical, never core *(not in monitor universe)* |
| **GMD** | EV/EBITDA | EVEB cheap vs build-phase | EVEB **15.0** (rich) | **RICH_WAIT** | Watch *(not in monitor universe)* |
| **DHG** | PE (buy & hold) | PE<PE_MA5Y + ROE5Y>0.15 + ROIC5Y>0.15 | PE 13.6<MA5Y 15.1, ROIC 0.22 | **BUY · ACCUMULATE** (quality anchor, no timing) | Buy-and-hold, **no timing** |
| **DBD** | PE (buy & hold) | quality floor | ROE5Y 0.181, ROIC 0.178; PE 17 not cheap | **RICH_WAIT** (hold-quality, not cheap) | Buy-and-hold *(not in monitor universe)* |
| **DMC / IMP** | — | ROE5Y<0.15 | DMC 0.126 / IMP 0.138 | **EXCLUDED** (quality-floor reject) | Exclude *(not in monitor universe)* |
| **MSH** *(textile, sector #16)* | PE vs PE_MA1Y | PE<PE_MA1Y (+ROE5Y>0.15, IntCov>1.5); GPM-CV = elite-ranking context | PE **6.5** < MA1Y 7.6, ROE5Y **0.249**, IntCov 7.7 | **BUY · ACCUMULATE** (in entry window, elite quality) | Buy-and-hold-on-weakness single-name (timing destroys it); NOT a book |
| **DBC** *(livestock/hog, sector #17)* | P/B trough **+ GPM-turn** | PB<PB_MA1Y **AND** GPM_P0>GPM_P4 (+CF_OA_3Y>0, IntCov>1); ARMED via hog-feed spread | PB **1.03**<MA1Y 1.34 (cheap ✓) but **GPM flat 0.17≈0.17 (turn ✗)**; hog↓/feed↑ spread not supportive | **WATCH** (value half present, margin-inflection half NOT yet, early-warning not supportive) | High-beta cyclical-timing single-name; ARMED→BUY on GPM turn-up, NOT the cheap multiple alone; NOT a book |

> **MSH GPM-CV note (2026-07-06):** the textile framework's `GPM_CV(P0..P7)<0.15` is used as a **ranking/elite-tier lens** (framework line 139: "correctly ranks MSH elite > TCM >> TNG"), NOT a hard binary gate for the single-name deploy. MSH's operative entry gates are `PE<PE_MA1Y ∧ ROE5Y>0.15 ∧ IntCov>1.5`. Its trailing GPM-CV has ticked to **~0.178 (above the nominal 0.15 line) purely because margin is RISING** (monotone 0.13→0.22 inflates trailing CV) — still far from the erratic ~0.38 crowd the gate rejects. `sector_lens_monitor.py` reports the CV transparently as quality context and does **not** hard-exclude MSH on it. Flagged for the user: if a strict CV<0.15 hard gate is ever wanted, MSH would need the threshold relaxed (~0.18) or a detrended CV — a calibration choice, not a code bug.

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

> **GOVERNANCE OVERLAY — State-Owned-Enterprise archetype** *(cross-cutting note, sector #19, added 2026-07-06; NOT a sector row — apply on TOP of the name's own sector metric whenever the State controls >50% / de-facto).* Source: `soe_governance_framework.md`. Confirmed on GAS/PLX/POW/NT2/VCB/CTG/BID/BVH/SAB/VNM vs matched private peers, 2014→2026, self-check 0 VND PASS.
> 1. **State ownership is a mild return DRAG, never a factor to harvest** — `state_pct` IC(3M) **−0.034**; SOE mean fwd T+60 **3.16% vs private 4.25%**; an EW SOE-controlled basket makes **9.45% vs 14.50% for the identical-sector private-peer basket (~−5pp/yr)**. **Don't overweight a name FOR being a state blue-chip.**
> 2. **No governance discount to buy — flagships trade a PREMIUM** (SOE/private avg PB: power 1.02×, banks 1.33×, insurance 2.12×). VCB/BVH/GAS/SAB/VNM earn a scarcity/blue-chip premium that outweighs the float/policy discount. A cheap-PB SOE (BSR/PLX) is cheap for a policy/cyclical reason, not a mispricing.
> 3. **DY on an SOE is a POLICY variable, not a free-cash-flow signal** — bifurcated: budget-payout cash-cows (GAS/VEA) vs regulator-forced *retention* (state banks pay stock-div + retain for CAR). The high-DY "yield play" is a documented **INCOME TRAP**: cash-cow basket price-CAGR 4.53% + ~4.5pp div ≈ 9.0% total-return **still lags B&H 10.23% with −58% DD**. (Behavioral reason reinforcing Rule 2's data-gap.)
> 4. **Thin float is the measurable signature** — annual share turnover ∝ −state% (**Spearman −0.51**); SOE median turnover 0.18 vs private 0.44. Size the **high-lock flagships (ACV/GAS/VCB/VEA/BID)** for the *locked* float, not the headline ADV. **Liquid exceptions:** POW/NT2/PLX/VNM (deep public float, retail favorites) — read the turnover, don't assume.
> 5. **Policy price-control caps upside asymmetrically** (PLX 2022 fuel-ceiling losses in a record-oil year; POW/NT2 sell to the EVN single-buyer at administered PPA) **+ state action is discrete event risk** (SAB 2017 divest-to-ThaiBev windfall; VNM SCIC divestment overhang = structural seller). Un-modellable in BQ — carry as a qualitative flag.
> **Verdict: a governance LENS, not a book and not a gate** (don't wire; state blue-chips are already handled by their own sector frameworks — banking archetype-B, energy). No buy-watchlist or exclude-list changes.

> **VALUATION-METHOD OVERLAY — Holding-Company / Conglomerate SOTP archetype** *(cross-cutting note, sector #20, added 2026-07-06; NOT a sector row — a valuation METHOD to apply whenever a listed group spans segments with different economics).* Source: `holdco_sotp_valuation_framework.md`. Universe VIC/MSN/GEX/GVR (listed parent → listed subs measurable in BQ), 2016→2026, self-check 0 VND PASS.
> 1. **A blended P/E or P/B on a conglomerate is meaningless — use listed-stake SOTP.** `coverage = ParentMarketCap / Σ(stake × listed-subsidiary MarketCap)`. VIC PB **11.3** with NPM that went **negative** in 2022 (VinFast) — you literally cannot value it on a consolidated multiple; VHM standalone PB 2.3, NPM ~0.33. **Split the parent into parts, value each on its own sector metric (Rule 1 applied to a single ticker).**
> 2. **coverage < 1 = market pays ≤0 for the unlisted ops (leverage/complexity discount); coverage > 1 = it pays UP for unlisted optionality.** Current snapshot: **MSN 0.70× / GEX 0.77× (DISCOUNT)** vs **VIC 4.07× / GVR 14.8× (PREMIUM)**. The discount names carry real holdco leverage (MSN Debt_Eq ~1.8-2.9, VIC ~6.7); the premium names carry unlisted optionality the tape re-rates (VinFast at VIC, the plantation→industrial-park landbank at GVR — its listed rubber subs are a tiny 7% of its cap).
> 3. **The discount does NOT mean-revert — deep discount is a TRAP, not an entry.** Pooled Spearman(coverage-z-vs-own-history, fwd return) = **+0.073/+0.054/+0.036** — *wrong-signed for the thesis*: it's premium-**momentum**, not discount-reversion. A "buy the deepest-own-discount" tilt basket **lost** (Full CAGR 4.5% vs 14.0% for naive EW-all, worse DD −57.6%). The series **trend** rather than oscillate (MSN/GEX coverage trend-vs-time −0.68/−0.62 = secular *de-rating*; GVR +0.55 = premium *re-rating*; AR(1) half-lives 50–260d). Classic emerging-market conglomerate discount that never closes.
> 4. **Any basket edge is reshuffle-luck, not signal.** EW-all-4 beats B&H +1.4pp Full but that is **100% OOS-concentrated (IS 2016-19 −19.1pp / OOS 2020-26 +16.2pp)** — the VIC+GVR run-up carries all of it; fails the per-year LOO / multiple-testing discipline.
> 5. **Premium = optionality that deflates violently in CRISIS** — GVR coverage collapses 14.7× (BULL) → 7.2× (CRISIS); the unlisted-story premium has higher downside beta than the listed-stake NAV. A risk flag on any premium holdco: you are long an unlisted call option, sized accordingly.
> **Verdict: a valuation-DIAGNOSTIC LENS, not a book and not a gate** (don't wire — tiny N=4, discount is a trap, edge is OOS-luck). Use SOTP to *understand what you're paying for* (unlisted burn/landbank vs listed NAV) and to size the optionality/leverage risk; do NOT trade the discount. No buy-watchlist or exclude-list changes. *Stakes held constant = documented limit; the level is sensitive to it but the trend / no-mean-reversion / momentum-sign conclusions are invariant to a constant stake error.*

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
| **Textile/garment export** | FOB/integrated (MSH/TCM) | **PE vs PE_MA1Y** (EVEB noisy) | **GPM-CV<0.15 + IntCov>1.5 + ROE5Y>0.15** | margin-stability gate is the lens; MSH=elite, TCM=faded. Screen FAILS as a book (−11pp) → lens only |
| | CMT scale (TNG, tail) | — | fails IntCov (neg) / NPM~0 / Debt_Eq 2-4 | thin-margin leverage trap; growth-bet not value. **FX: weak-VND is a NEGATIVE fwd signal (risk-off proxy), not a tailwind** |
| **Construction contractors** *(EPC/GC, sector #18, added 2026-07-06)* | civil/industrial GC (CTD/VCG/HBC/FCN/LCG/C4G/HTN…) | **CF_OA + Debt_Eq trend + DSO *trend*** (NEVER P/E or P/B) | CF_OA_P0>0 ∧ CF_OA_3Y>0 ∧ DSO not deteriorating ∧ IntCov>1.5 ∧ DE<2.5 = an **EXCLUSION filter, not entry** | POC accounting → **P/E unusable** (noise); **P/B-trough is a TRAP** (IC −0.065, worse than mkt; cheap-P/B = the AR-distressed names; equity collapse inverts P/B UP mid-crisis). Screen = LENS not book (in cash 84% of months, OOS≈flat) — but dodges −62%→−18% DD. Exclude BOT-toll (CII/HHV/CTI/PC1→D&A_HEAVY) + CTR (telecom ICB-trap). **No buy candidate.** |

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
| **HTN (Hưng Thịnh Incons)** *(construction, added 2026-07-06)* | **Live HBC-repeat in progress** — 2026Q1 DSO **2,425 days**, AR/Revenue **49×**, PE −114, receivables collapse tied to a stressed captive developer. **P/B 0.46 is the trap, not a value entry. AVOID.** |
| **HBC (Hòa Bình CG)** *(construction, added 2026-07-06)* | The 2022-23 receivables blow-up (Carillion-VN): CF_OA negative while booking POC profit, DSO 139→386, Debt_Eq 3→**162** (equity near-wiped). Cheap P/B *led into* the wipeout. Restructuring, not investable — the canonical contractor AR-trap case study. |

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
- **DBC** *(livestock/hog #17)* — cheap-vs-history (PB 1.03<MA1Y 1.34, PE 6.3) but the **margin-inflection
  trigger (GPM_P0>GPM_P4) is NOT firing** (0.17=0.17 flat) → **WATCH, not buy yet.** The hog-cycle pays on the
  GPM turn-up off a trough, not the cheap multiple alone (P/B-trough alone is a value trap, IC ≈ market). Buy on
  the next confirmed GPM turn-up; high-beta, size small, DT5G caps gross. NOT a secular compounder (ROE5Y swings
  0.11–0.19) — cyclical-timing only.

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
*(Section 0 statuses re-refreshed on 2026-07-03 BQ rows, job `Taylor_20260706_050653`.)*

---

## Section 7 — Harvesting Workflow Proposal (PROPOSAL — not built)

> **Added 2026-07-06** (job `Taylor_20260706_050653`). This is a **design/proposal only** — no script built, production untouched. If the user approves, a follow-up dispatch builds `sector_lens_monitor.py`. The problem it solves: with **8 Group-A sectors** (was fewer at sweep start), re-checking each name means manually dispatching Taylor per name — toil that scales badly and risks *missing the rare transition* on a lens that has sat still for months (DBC has been WATCH for months; that is normal, not a reason to stop watching).

### 1. Cadence — driven by how fast each trigger can actually move

| Lens family | Names | What updates | Trigger can change on | **Proposed check cadence** |
|---|---|---|---|---|
| Value-vs-own-history | FPT, MSH, DHG, CTR | price daily; PE/PB/EVEB history quarterly | a price move crossing the multiple threshold | **Weekly** (a multiple doesn't meaningfully cross intraday; daily = noise) |
| Banking justPB | MBB/ACB/HDB/TCB/VCB | price daily; ROE5Y quarterly | PB crossing justPB band | **Weekly** |
| Securities (DT5G-gated) | SSI/VCI/VND/HCM | price daily; ROE inflection quarterly; **DT5G state** daily | DT5G gate open/close OR PB<1.8 cap OR ROE re-cross | **Weekly + on any DT5G state change** (the gate flip is the real trigger here) |
| Trough tactical | PVT, HAH | price daily; CF_OA/EVEB quarterly | P/B<1 / EVEB-trough cross | **Weekly** |
| Livestock 2-part | DBC | hog+feed feeds ~daily/weekly (Winston cron); GPM quarterly | GPM_P0>GPM_P4 turn (quarterly) + hog/feed early-warning (weekly) | **Weekly** (feeds) + **event on new quarter** (GPM) |
| **Quarterly deep-refresh** | ALL | fundamentals land in earnings season | any fundamental gate (ROE inflection, GPM turn, justPB inputs) | **Event-driven, ~4×/yr** when a name posts a new quarter |

**Bottom line: one WEEKLY scan covers everything**, with a **quarterly deep-refresh** during earnings season and an **immediate re-run on any DT5G state change** (the only genuinely daily-relevant input, and only for the securities sleeve). **No daily cadence is warranted** — nothing in Group A changes state intraday.

### 2. What checks it — proposed `sector_lens_monitor.py` (ONE read-only script)

Replaces "remember to dispatch Taylor per name" with a single deterministic digest:
- **Reads** the BQ local DuckDB cache (`data/bq_cache/`, ~100ms, threads=1) — latest row per Group-A name — + latest `vnindex_5state_dt5g_live` state, + the commodity feeds already on disk (`hog_price_vn.csv`, `maize_monthly.csv`, `soybean_meal_monthly.csv`, `vcb_fx_rate.csv`) for the livestock/textile overlays.
- **Computes** each lens's entry condition (formulas already pinned in the per-sector frameworks) → a status per name: `BUY / ACCUMULATE / QUALIFIES / WATCH / WAIT / EXCLUDED`.
- **Prints** one status table (the Section-0 Group-A table, regenerated live) + a **diff vs. last run** (persisted `data/sector_lens_state.json`) to surface transitions.
- **Fail-safe:** a stale feed / missing row / small breadth universe → prints `WARN` and holds the prior status; it **never fabricates a signal** from missing data (same discipline as the DT5G `get_gated_state` fail-closed pattern and the report-provenance rule in `coding_guidelines.md §6`).
- **Read-only, auditable, no production touch** (recompute from cache, self-check against a BQ-live spot query on demand).

### 3. Alert thresholds — ping only on a state TRANSITION, never every run

Most names sit still for months → alerting every run is noise that trains people to ignore it. Alert (Discord *Trading report* topic / Telegram) **only when a name changes bucket.** Per-lens transition ladder:

| Lens type | Standing states | **Alert-worthy transition** |
|---|---|---|
| Value-vs-history (FPT/MSH/DHG/CTR) | WATCH(rich) ↔ **IN-WINDOW**(crossed cheap threshold) | either crossing |
| Banking justPB | below-justPB (cheap-buy) ↔ above (exit) | crossing the band, or discount widening past a set band |
| Securities (DT5G-gated) | QUALIFIES ↔ gated-off | **DT5G gate open/close**, PB crossing 1.8 cap, ROE re-cross |
| Trough (PVT/HAH) | trough-buy ↔ not-trough | P/B<1 or EVEB-trough crossing |
| **DBC 2-part** | **WATCH** (value ✓, GPM-turn ✗) → **ARMED** (hog/feed early-warning turns supportive + GPM approaching turn) → **BUY** (GPM_P0>GPM_P4 confirmed on a fresh quarter) | each step up/down |

Everything else = silent (logged to the status file for the weekly digest, no push).

### 4. Decision flow after a signal (confirms Section 6, one refinement)

The Section-6 flow is unchanged by having more lenses — more lenses change the *input feed*, not the pipeline. One refinement given the wider funnel:

```
sector_lens_monitor alert (transition)
  → Taylor validates  [quality gate + DT5G confirm + not-a-trap check]   ← NEW explicit gate
  → DollarBill builds discretionary plan  (within V2.4 weight + DT5G cap)
  → user approves
  → Mafee executes (plan-bound)
```

The **Taylor-validates** step is the safeguard: a raw multiple crossing a threshold is *necessary-not-sufficient* (Rule 3 — lens ≠ book; every Group-A lens failed OOS as a standalone monthly book). The gate re-checks the quality floor, the DT5G regime cap, and the trap-conditions specific to that sector (steel leverage, construction AR-quality, holdco discount) BEFORE it reaches a plan. This keeps the funnel honest without re-litigating each name from scratch.

### 5. Recommendation — build a light weekly monitor; keep the decision discretionary

**Recommend: build `sector_lens_monitor.py` as a lightweight WEEKLY read-only cron digest; do NOT automate the decision.**

- **Why build it:** cost is low (reuses the BQ cache + existing feed CSVs + lens formulas already written in the frameworks; ~150–250 lines, no new infra) and it removes real toil + closes the "hope someone remembers to check" gap on 8 sectors. Natural slot: **Friday after close**, alongside the existing `kb_nightly` Friday cadence.
- **Why keep the decision discretionary:** every framework's own verdict is *lens, not book* — these failed OOS as auto-allocated sleeves (Rule 3), so the monitor must only **surface status + transitions**, never auto-plan or auto-size. The one partial exception (securities as a small DT5G-gated sleeve) is still routed through the human approval chain.
- **Cost/benefit vs. status-quo:** the alternative (discretionary "dispatch Taylor when the user asks") works but is *reactive* — it only checks when someone thinks to, and the highest-value moment (a rare WATCH→BUY transition, e.g. DBC's GPM finally turning) is exactly the one a human is least likely to catch in time. A near-zero-marginal-cost weekly digest converts that from luck to a guarantee, with an audit trail of status history.
- **Known limits to state up-front:** (a) it's a MONITOR not an oracle — necessary-not-sufficient, hence the Taylor-validate gate; (b) it inherits every lens's OOS caveat, so it feeds *discretionary overlay sizing*, never a new auto-sleeve; (c) it depends on the BQ cache + Winston's feed crons being fresh — the fail-safe holds prior status on staleness rather than emitting a stale signal.

**Verdict:** worth building as a light weekly transition-alerter (proposal pending user approval); NOT worth building as an always-on daily system or an auto-trader. Awaiting user sign-off before any code.
