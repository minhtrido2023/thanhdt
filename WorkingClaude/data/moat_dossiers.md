# Moat Dossiers — sourced 5F / competitive-analysis evidence behind `moat_tags.csv`

> **Purpose:** `moat_tags.csv` carries only a one-line `risk1`. This file holds the full Porter
> 5-Forces reasoning + point-in-time sources behind each WIDE/NARROW tag, so a moat call can be
> *defended with evidence* later. NONE-tagged names are intentionally omitted — a missing moat is
> readable straight from the financials (durable ROIC fails); the heavy qualitative review is
> reserved for *claimed* moats, where being wrong is costly.
>
> **Discipline (mirrors `moat_5f.py`):** these verdicts run on LLM/web knowledge → **non-point-in-time,
> LIVE-ONLY. Never feed a historical backtest.** Re-review annually or on a category shock; bump `asof`.

---

## VCS — Vicostone (HNX) · engineered quartz / surface products
**Tag:** `NARROW` · type `BRAND/PROCESS` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**Prior tag:** `WIDE` (TECH/BRAND, 2026-06-03) — **downgraded** by this review.

**Why downgraded (WIDE → NARROW):** the two pillars of the original WIDE thesis were measured and
both are weaker/reversed than the tag implied:
1. *"US anti-dumping duty on quartz countertops"* — real and continued (US ADD/CVD on **Chinese**
   quartz; expedited sunset review Oct-2024, applicable 24-Jan-2025), BUT this is a **borrowed
   regulatory moat**, external to VCS, and it is now **turning against Vietnam**: QMAA (2024)
   petitioned to extend duties to VN/India/Turkey; US–VN tariff landed ~20% (46% worst-case / 40%
   transshipment). The tailwind that built VCS's US share is reversing.
2. *"Sintered-stone substitute"* — the engineered-stone **category itself faces an existential
   health/regulatory overhang (silicosis)**: Australia **banned** engineered stone outright from
   1-Jul-2024 (first country); California moving to an emergency standard prohibiting cutting/
   installing engineered stone (519 silicosis cases, 29 deaths to early-2026). Low-/zero-silica
   substitutes (sintered stone, porcelain) growing ~7.8%/yr partly *because* they dodge this. A moat
   around a shrinking, regulation-threatened category cannot be WIDE.

**5-Forces summary:**
- *Substitutes* — HIGH & rising (silicosis-driven category shift; sintered/porcelain). **Decisive.**
- *New entrants / "moat"* — REGULATORY arbitrage (US ADD wall on China), now reversing vs VN; Breton
  "Bretonstone" process is *licensed*, not exclusive.
- *Buyer power* — HIGH; export = 74.3% of net rev; **US already collapsed 80% → ~25%** of stone export rev.
- *Supplier power* — LOW-MOD; acquiring Phenikaa Chemical to self-supply >95% of inputs (real positive).
- *Rivalry* — HIGH; global oversupply, Chinese transshipment, Caesarstone (US 49% rev) struggling.

**Quant cross-check (BQ `ticker_financial`, to 2026Q1):** durable ROIC signature is **real but
compressing** — ROE5Y 38.6%→22.3%, ROIC5Y 30.9%→20.3%, ROIC_Min5Y 22.6%→14.0%; **revenue YoY
negative 12 straight quarters**; Debt/Eq 0.16 (clean). Not NONE (ROIC_Min5Y still 14%, genuine
process+scale), not WIDE (eroding franchise + category overhang) → **NARROW** is the honest middle.

**#1 risk to watch:** silicosis-ban contagion spreading from AU/CA into more developed markets +
US tariff on VN exports compounding the already-collapsed US channel.

**Sources (accessed 2026-06-05):**
- US ADD/CVD continuation — Federal Register 2025-01946 (30-Jan-2025)
- USITC five-year sunset determinations on China quartz (10-Jan-2025)
- Australia engineered-stone ban from 1-Jul-2024 — AIHA
- California ban move / silicosis cases — Times of San Diego (28-May-2026)
- VCS export 74.3%, US 80%→25%, 46% tariff → −50% US rev / −30-40% profit — TheInvestor.vn (d15263)
- VCS Q3-2025 results amid trade challenges — Vietnam News (1728642)

---

## DGC — Duc Giang Chemical Group (HOSE) · phosphorus / P4 / DAP / detergent chemicals
**Tag:** `NARROW` · type `COST/LOCATION` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**Prior:** NARROW/COST (2026-06-03) — **tier kept**, type + risk refined.

**Verdict:** keep NARROW. DGC has a genuine low-cost integrated position (captive apatite ore — Fields
19B/25; ~56% of Vietnam's national P4 capacity; ~1/3 of global P4 export flow; fortress balance sheet
Debt/Eq 0.14-0.29) → rules out NONE. BUT the high headline ROIC is **operating leverage on the
phosphorus price, not a through-cycle moat** → rules out WIDE.

**5-Forces:** Rivalry HIGH/commodity (China P4 surplus forecast 2026, DAP ~−8% 2026, DGC is a
price-taker). Cost/integration = the moat core (captive ore + Lao Cai hydropower siting = COST+LOCATION,
not brand/tech). Substitutes MED (semis high-purity P4 + LFP-battery demand = structural tailwind).
Regulatory: China phosphate export curbs since 2024 benefit DGC as non-China supplier — exogenous,
reversible tailwind, **not a self-owned barrier**. New capex: Nghi Son chlor-alkali (Q1-Q2 2026) +
Field-25 license = execution overhang.

**Quant cross-check (BQ → 2026Q1):** classic cyclical. ROIC5Y ~0.29 / ROE5Y ~0.37 elite at peak, but
**ROIC_Min5Y ~0.14 / ROE_Min5Y ~0.17 show the trough far below peak — not held through cycle**. GPM
0.41→0.29, NPM 0.37→0.26 compressing; NP_YoY violent (−53/−46/−30% in 2023, brief 2024-25 recovery,
−50% 2026Q1 on RevYoY −24%). PB de-rated 3.1x→1.3x = market prices a cyclical, not a compounder.
Durable positive = solvency (clean B/S funds capex through troughs), not ROIC.

**#1 risk:** phosphorus/P4 + DAP price cycle drives earnings; apatite depletion + Nghi Son chlor-alkali
execution risk compound it.

**Sources (2026-06-05):** DucGiang IR (P4 share, Fields 19B/25) · MarketScreener (Field 25) ·
Mysteel (China yellow-P 2026 surplus) · ExpertMarketResearch / CRU (DAP 2026) · Vietnam.vn (Q2-2025
margin / ore shortage) · BQ `ticker_financial` DGC 2023Q2–2026Q1.

---

## QTP — Quang Ninh Thermal Power (UPCoM) · coal-fired generation, N. Vietnam
**Tag:** `NARROW` · type `REGULATORY/COST` · entry **`H`** (raised from M) · asof **2026-06-05** · src `5f_validated_compet`
**Prior:** NARROW/REGULATORY, entry M (2026-06-03) — **tier kept**, entry raised, framing sharpened.

**Verdict:** keep NARROW — regulated PPA + very high entry barrier are real, but **EVN monopsony caps
the return ceiling and PDP8 puts a hard end-of-life on the asset** → a regulated-yield moat, not WIDE.
Entry barrier raised to H: under PDP8 (Decision 768, 2025) **no new coal plant can be built** — incumbents
are structurally un-cloneable.

**5-Forces:** Buyer power DOMINANT NEGATIVE — EVN near-monopsony; ~70-75% revenue = fixed PPA capacity
(~339 VND/kWh) + fuel pass-through, EVN negotiates the fixed leg down → no pricing power. Entry/substitutes
double-edged: PDP8 bans new coal (near-term scarcity/dispatch value when hydro weak) but forces
conversion-to-biomass/ammonia or retire by ~40yr life/2050 → terminal, ESG-shunned "melting ice cube".
Supplier: TKV coal cost-pass-through muted; Quang Ninh coal-region siting = modest COST/LOCATION edge.
Rivalry/hydrology: merit-order vs cheap hydro → earnings swing La Niña (weak 2025, NPM ~5%) vs El Niño
(strong 2023-24); FSCORE 4↔8 = dispatch-dependent, not durable.

**Quant cross-check (BQ → 2026Q1):** NARROW-regulated signature. ROIC5Y 0.138→0.159, **ROIC_Min5Y
~0.125 = durable double-digit regulated floor**. Deleveraging clear: Debt/Eq 0.47→0.28 (China Eximbank
QN-2 loan matured 2023) → cash to dividends. DY ~7.3-7.7% annual, PE ~5.5, PB ~1.0 = **bond-proxy
re-rated to yield, never growth**; RevYoY negative (terminal/no-growth). Fully-funded cash cow paying
out, not a compounder.

**#1 risk:** EVN monopsony caps return + PDP8 terminal-asset clock (convert/retire ~2050) = depreciating
dispatch-dependent yield play, not a compounder.

**Sources (2026-06-05):** Vietstock QTP report (PPA 339 VND, El Niño dispatch) · EVN 2025 annual report ·
KPMG / White & Case (Revised PDP8, Decision 768) · IEEFA (PDP8 coal economics) · Global Energy Monitor
(commissioning, QN-2 loan) · EVNGENCO1 (QTP 2025 production) · BQ `ticker_financial` QTP.

---

## NNC — Nui Nho Stone (HOSE) · construction aggregates, S. Vietnam
**Tag:** `NARROW` · type `LOCATION` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**Prior:** NARROW/LOCATION (2026-06-03) — **tier kept, but the risk note was factually corrected.**

**Verdict:** keep NARROW — haul-radius location monopoly is a genuine barrier (rules out NONE), but
finite-life + single-asset concentration + demonstrated cyclicality cap it below WIDE.

**MATERIAL CORRECTION to prior tag:** the prior risk ("quarry reserve depletion") implied imminent
depletion. In fact the eponymous **Nui Nho pit (Binh Duong) EXPIRED 31-Dec-2019 and is in mine-closure**
(July-2025 "+5.1M m³" is just safety-pillar scraping, now only ~6% of revenue). The real cash engine is
the **Mui Tau / Tan Lap quarry (Binh Phuoc), 22.5M m³, ~1.0M m³/yr, licensed to 2043 → ~20yr runway**.
So this is a long-finite-life asset, NOT near-term-terminal — but a **single asset = ~94% of revenue**.

**5-Forces:** New entrants HIGH barrier locally (mining permits scarce, env/land-use gated; low-value/
high-weight stone = de-facto monopoly within ~25-30km haul radius) = real LOCATION moat. Rivalry low
within radius / high across Dong Nam Bo cluster. Buyer power moderate (regional stone shortage shifts
pricing to sellers). Substitutes/supplier low. Demand catalyst confirmed: Southern infra supercycle
(Long Thanh airport stone shortfall; ring roads/highways) + June-2025 govt +50%-capacity mechanism.

**Quant cross-check (BQ → 2026Q1):** ROIC5Y 0.165-0.346, ROE5Y 0.175-0.31 = strong location-moat margin
profile. **ROIC_Min5Y ~0.013 = the 2020-21 license-gap/cyclical trough fingerprint → caps at NARROW**.
GPM 0.26→0.50, NPM 0.18→0.39, NP_YoY +44% to +161% as the infra cycle bites; Debt/Eq 0.15-0.26, FSCORE
6-8, PE 6-10. (BQ DY shows 0.0 but NNC paid a 1,000đ/share 2024 cash dividend Aug-2025 → BQ DY field is
stale, data gap not a non-payer.)

**#1 risk:** single-asset concentration (~94% of revenue on the Mui Tau quarry to 2043); any permit/
geology/closure shock there is existential; trading liquidity genuinely thin (sizing-constrained).

**Sources (2026-06-05):** TinnhanhChungkhoan (+5.1M m³ Nui Nho) · PHS (Q3-2025, Tan Lap 94% rev) ·
PineTree (Mui Tau to 2043 / Nui Nho expired 2019) · Bao Dong Nai (Long Thanh stone shortage) ·
Vietnam.vn (+50% capacity mechanism) · Fili (1,000đ dividend) · BQ `ticker_financial` NNC.

---

## GMD — Gemadept (HOSE) · ports + logistics
**Tag:** `NARROW` · type `LOCATION/REGULATORY` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** (was untagged; 8L quant moat=STRONG/rating-2 — **overstated**, downgraded by review).

**Verdict:** NARROW. A genuine licensed deep-water concession/location edge (Gemalink = #1 VN throughput, 232k-DWT
capable) — rules out NONE — but contested by an overbuilt cluster and capped tariffs → not WIDE. The STRONG
quant tag is inflated by **non-recurring asset-sale gains**: ROE5Y 15.8% vs ROIC5Y only 8.9% / ROIC_Min5Y 6.5%;
NPM spikes to 65-74% in 2023Q2-2024Q1 = port-stake divestment gains; strip them → durable ROE ≈ the 8-9% ROIC.

**5-Forces:** Rivalry HIGH (Cai Mep-Thi Vai overbuilt: Gemalink vs SSIT/TCIT/CMIT/SP-PSA; Lach Huyen berths
3-6 pressure Nam Dinh Vu). New entrants M/rising (MSC-backed Can Gio mega-port + Lach Huyen expansion future
threats; barrier = scarce dredged deep-water concession). Buyer power HIGH (concentrated shipping alliances,
CMA CGM both partner & customer, can shift calls). Pricing capped (govt tariff bands, +~10% Feb-2026). Balance
sheet sound (real lev 0.15) = prudence, not moat. **#1 risk:** overbuilt cluster + new mega-ports cap per-TEU economics.

**Sources (2026-06-05):** Vietstock (cluster competition) · SGGP (tariff +10%) · TheInvestor (Gemalink Ph2/CMA CGM) · RealLogistics (232k-DWT licence) · BQ `ticker_financial` GMD.

---

## VGC — Viglacera (HOSE) · building materials + industrial parks
**Tag:** `NARROW` · type `LOCATION/REGULATORY` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** (was untagged; 8L quant moat=STRONG/rating-1 — **overstated**, downgraded).

**Verdict:** NARROW. Only the **industrial-park segment** (~70% of gross profit) carries a moat — scarce licensed
N-VN land bank (16 parks / 4,600+ ha, Samsung/Canon/Amkor anchored, Yen Phong >90% occupancy = pricing power on
remaining land). The larger **building-materials** business (glass glut, gas-cost, Chinese imports) is a cyclical
commodity drag that dilutes the blend. IP moat itself is finite (land depletes; the "annuity" is mostly one-off
land-use-right sales → must re-buy scarce land, capex/leverage-funded).

**5-Forces (IP leg):** Entry barrier = scarce licensed land + multi-year approvals + clearance (LOCATION+REGULATORY);
buyer power low (tenant switching cost high once built). **Quant:** ROIC_Min5Y 12.9% solid-not-fortress; GPM 29%
blended (high IP land margin masks thin materials); NP_YoY wild (+28x land-sale lumpiness → −55%), FSCORE 3→9→4 =
cyclical, not stable compounder. GELEX-controlled (~46-51%) + state ~38% divestment deferred 2026-30 = overhang.
**#1 risk:** IP land finite (re-buy at rising cost) + materials cyclical; FDI/tariff demand not contractual annuity.

**Sources (2026-06-05):** GELEX (Amkor/Yen Phong IP) · TheInvestor (segment split, state-divest delay) · Vietnam News (GELEX stake) · Cushman&Wakefield (Bac Ninh hub) · BQ `ticker_financial` VGC.

---

## VHM — Vinhomes (HOSE) · residential real-estate developer
**Tag:** `NARROW` · type `SCALE/LOCATION` · entry `H` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** (was untagged; 8L quant moat=STRONG/rating-2 — **overstated**, downgraded).

**Verdict:** NARROW (high-end of). The land bank is a real entry barrier (largest+cleanest in VN, ~10x #2, ~30yr
runway, Vingroup ecosystem land access + mega-township execution) → rules out NONE; entry barrier genuinely H.
But RE-developer moats are structurally **cyclical + depleting**, and durability is overstated: high ROE is
**episodic** (mega-handover years) and inflated by **related-party bulk sales recognized as financial income**
(Q1-25 bulk sales VND19.3tn +124%; receivables+inventory ~half of assets).

**5-Forces:** New entrants HIGH barrier (land bank/ecosystem). Buyers MED-WEAK (retail price-sensitive, affordability
strained, demand cyclical — 2022-23 froze sales, no through-cycle pricing power). Suppliers/Policy HIGH RISK (2024
Land Law abolishes price framework → land-acquisition cost up, Art.79 limits commercial land fund → erodes the
land-cost edge). **Quant degrading:** ROIC_Min5Y 11.7%→8.1%, ROIC5Y 19.2%→14.0% (floors sliding); Debt/Eq 1.30→2.19,
real lev 0.24→0.59 (bond-dependent); NP/Rev whipsaw, FSCORE 2-4 trough → 8 handover. **#1 risk:** property cycle +
bond/leverage dependence + Land-Law-2024 replenishment cost can freeze pipeline & compress ROIC for years.

**Sources (2026-06-05):** TheInvestor (Vingroup 2025 results) · Vinhomes IR (Q1-25 bulk sales, corp presentation/land bank) · Vietnam-Briefing & Freshfields (Land Law 2024) · BQ `ticker_financial` VHM.

---

## IDC — IDICO (HNX) · industrial parks + infrastructure utilities
**Tag:** `NARROW` · type `LOCATION/REGULATORY` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** (was untagged; 8L quant moat=STRONG/rating-2 — **overstated**, downgraded).

**Verdict:** NARROW. Dual moat is real — scarce licensed prime-corridor **IP land** + a captive **regulated utilities
ring** (power distribution to its own IPs, water, BOT toll roads) — the recurring utilities ballast is what lifts it
above a pure cyclical (rules out NONE). But the IP leg is finite (~580ha mature core, ~3-4yr runway), contested
(BCM/KBC/SIP/SZC/VGC), and its headline economics are **lumpy/one-time** (post-2022 land-lease recognition flatters
ROE5Y/GPM). ROIC_Min5Y only 6.3% = mediocre durability floor for a STRONG tag.

**5-Forces:** Rivalry HIGH (6+ scaled IP developers chase same FDI tenants; IDC's edge = location/legacy parks, not
pricing). New entrants MED (licensing/clearance hard but state grants rival licences constantly — protects incumbents
collectively, not IDC uniquely). Buyers MED (FDI tenants footloose across provinces at lease-signing). Utilities ring =
the durable recurring leg. **Quant:** Debt/Eq 1.5-1.8 high (real lev ~0.5-0.7 falling); FSCORE 3→8, NP_YoY ±wild =
lumpy; PB 1.86, pb_z −0.34 fairly valued; DY 3-10%/40% payout = part yield-play. **#1 risk:** finite leasable land →
moat depletes unless replenished via slow, rising-cost clearance in a crowded field.

**Sources (2026-06-05):** IDICO (Phu My 2 land bank) · TheInvestor (targets/dividend, IP-developer earnings) · KBSV (IP 2026 outlook/rents) · BQ `ticker_financial` IDC.

---

## VNM — Vinamilk (HOSE) · dairy   ⭐ FIRST WIDE
**Tag:** `WIDE` · type `BRAND/DISTRIBUTION` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** — and the **first WIDE to survive scrutiny** across this whole review batch.

**Verdict:** WIDE, but a **mature/TRIMMED wide** (durable, not expanding). The barrier is real and through-cycle proven:
national 240-250k POS distribution, #1 brand, vertical herd integration, 22-26% durable ROIC/ROE at near-zero
leverage that survived a *self-inflicted* 2024-25 distribution restructuring (H1-25 rev −3.6%/NP −16.9%) and
bounced back (Q1-26 NP +55%). No challenger has overcome it in 20 years.

**5-Forces:** Rivalry HIGH but at the *edge* — TH True Milk owns ~30-45% of packaged *fresh* milk (premium/growth
segment), FrieslandCampina ~25%, Nutifood ~8%; VNM share hit a ~45-50% ceiling and trends down at the premium frontier.
Supplier MED (~60% milk demand imported → powder-cost cycle, mitigated by owned mega-farms). Substitutes MED, the
VCS-style quiet threat: EVFTA/CPTPP zero-tariff dairy imports + plant-based nibble the premium edge. **Share-erosion
verdict: ERODING-BUT-CONTAINED** — TH/Nutifood take *premium share*, not the *moat* (mass-market distribution+scale).
**Quant:** ROIC_Min5Y 22.5% / ROE_Min5Y 26% / GPM 41-42% (recovered off 2023 trough = pricing power intact) / real-lev
0.28 fortress; ROIC5Y slid 31.5%→24.4% = compounds slower than it used to; pb_z −0.88 prices the ceiling, not a breach.
**#1 risk:** permanent domestic share cap as premium fresh-milk leaks to TH + FTA imports — trimmed, not breached.

**Sources (2026-06-05):** Vietdata (share) · The-Shiv (dairy market) · DairyBusiness (Q1-26) · Shinhan (recovery) · TheInvestor (US-tariff) · USDA-FAS (FTA competition) · BQ `ticker_financial` VNM.

---

## FPT — FPT Corp (HOSE) · IT services / software + telecom
**Tag:** `NARROW` · type `SWITCHING/COST/SCALE` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** (8L quant STRONG/rating-1 = FAIR on realized durability, but the moat tier is a FORWARD call).

**Verdict:** NARROW. The moat is real and through-cycle proven on the numbers (ROIC_Min5Y flat 13.7% for 3yrs,
ROE_Min5Y 20-23%, low leverage), BUT it sits on a **cost/labor-arbitrage foundation under active substitution
disruption** — a textbook VCS-lesson erosion: generative-AI coding agents wiped $50B+ off TCS/Infosys/Wipro in 2026
with analysts flagging 20-30% of traditional outsourcing revenue at risk within ~18 months. FPT runs the same model.

**5-Forces:** Rivalry HIGH (commoditized global delivery; margins held only via mix, not pricing). Switching cost
MED-HIGH = the real moat (deep Japan client embeds — Japan rev $500M+ +32% YoY, keiretsu/language lock-in that AI
displaces more slowly than US English-language code). New entrants MED but AI lowers the bar. Supplier=talent rising
(VN wage inflation erodes the arbitrage half of the moat). AI verdict TWO-SIDED: FPT rides demand (AI factories ~70%
util, $256M DX contract) but the same force commoditizes the billable-hour base → caps at NARROW. Moat-negative event:
the WIDE-moat **FPT Telecom (broadband oligopoly) leg is being deconsolidated to equity-method FY2026**, concentrating
the listed story into the contested AI-exposed IT business. **#1 risk:** GenAI collapses the labor-arbitrage model.

**Sources (2026-06-05):** FPT IR (Japan $500M, 12M2025 earnings) · Smartkarma (Q1-26) · BusinessToday/RestofWorld (AI threat to Indian IT) · TheInvestor (FPT-Telecom split) · BQ `ticker_financial` FPT.

---

## MCH — Masan Consumer (UPCoM) · branded FMCG
**Tag:** `NARROW` · type `BRAND/DISTRIBUTION` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** (8L quant STRONG/rating-1 — overstated portfolio-wide).

**Verdict:** NARROW. The durable barrier is real but **confined to the seasonings/sauce core** (fish sauce 68.8%,
chili 67%, soy 52.9% = genuine pricing power), while noodles (#2 ~27.9% vs Acecook 35.4%) and beverages compete on
shelf. The 2025 self-inflicted **Direct-Coverage rollout** stumble (NP_YoY −24.5/−19.1/−10.7% three straight quarters,
FSCORE 7→1→2) exposed execution fragility — not whipsaw-proof.

**5-Forces:** Rivalry HIGH (seasonings near-monopoly fortress, noodles a 3-way fight). Buyer power MED-rising (modern
trade), mitigated because Masan owns WinCommerce — **but that's the related-party flag** (captive channel also hosts a
competing private label; WinCommerce hiring an Own-Brand/Private-Label lead). Quant fortress on margins (ROIC5Y 24.3%,
ROIC_Min5Y 19.1%, GPM stable 45-47%) but PB 9.55/PE 26 = priced for unbroken compounding with no margin of safety while
the engine just stalled. **#1 risk:** moat is category-specific (sauces only), noodles contested, MSN-ecosystem channel
dependence cuts both ways.

**Sources (2026-06-05):** Vietnam.vn (market share) · PRNewswire (HoSE roadmap) · MasanGroup (Q3-25) · AsiaFoodBev (noodle share) · LinkedIn (WinCommerce private-label) · BQ `ticker_financial` MCH.

---

## SAB — Sabeco (HOSE) · beer
**Tag:** `NARROW` · type `BRAND/SCALE/DISTRIBUTION` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** — a textbook **VCS-style brand-under-regulatory-erosion** case.

**Verdict:** NARROW. A real brand/scale/distribution franchise (national reach, heritage Bia Saigon, ThaiBev capital)
that survives — but is being **eroded on two structural axes management cannot control**: (1) regulation — Decree
100 (2020) + Decree 168/2024 drink-driving crackdown structurally cut on-trade demand (Q1-25 vol −14.7%, rev −19%);
(2) tax — special consumption tax legislated 65%→80% (2026)→90-100% (2030), ~20% price hikes on an elastic product.

**5-Forces:** Rivalry HIGH/worsening — **lost #1 share to Heineken (42% 2018 → 34% 2023-25)**; premiumization (the
high-margin segment) flows to Heineken not Sabeco. Buyer MED (mass-market price-elastic). Entry barrier M genuine
(distribution+scale+brand). Quant: resilient core (ROIC_Min5Y 14.6%, ROE_Min5Y 17.4%, ~zero debt, GPM 29%→37% on cost
recovery) BUT RevYoY negative 7 of last 11 quarters, **weakest revenue in a decade**; Q1-26 +11% rev/+56% NP = LNY
timing + price-hike rebound off a depressed base, not a re-rating. **#1 risk:** excise tax to 80-100% + Decree-100
demand hit compounding. → durable enough to survive (not NONE), not to compound unimpaired (not WIDE).

**Sources (2026-06-05):** Investing.com / Vietnam-Briefing (excise tax to 100%) · Inside.beer (Heineken share) · KPMG (Decree 100) · AsiaBrewersNetwork (weakest decade) · Vietnam News (Q1-26) · BQ `ticker_financial` SAB.

---

## FOX — FPT Telecom (UPCoM) · fixed broadband + data center
**Tag:** `NARROW` · type `INFRASTRUCTURE/SCALE` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** (8L quant STRONG/rating-1 — backward-looking, slightly overstates forward durability).

**Verdict:** NARROW. The last-mile fiber + 3-player oligopoly (VNPT ~39% / Viettel ~38% / FPT #3, ~95% combined) is a
genuine capex barrier — validated by rock-stable ROIC_Min5Y 17.4% / ROE_Min5Y 29.1% / GPM 49% across 12 quarters. But
FPT is the **contested sub-scale #3** facing two state giants (mobile+fixed bundling, bigger capex, 5G spectrum FPT
lacks) in a **saturating market** (85% household fiber penetration, fixed-broadband rev CAGR only ~1.8%) with an
**emerging 5G FWA substitute** (59% pop covered one year in).

**5-Forces:** Rivalry HIGH (ARPU price competition). New entrants LOW (fiber capex barrier = the moat). Substitutes
RISING (5G FWA for marginal/rural homes = the key erosion). Buyer power MED-HIGH (broadband commoditizing, low
switching cost, defended via TV/internet bundling). DC/cloud (AI+Cloud signed VND1,540bn +48%) = real growth optionality
but crowded (CMC/Viettel IDC/VNPT/NTT) and capital-heavy, not yet a moat. VNPT's Dec-2025 30% stake in FPT's enterprise
unit underscores state-giant gravity. **#1 risk:** saturation + FWA substitution + sub-scale-#3 disadvantage compress
ARPU/growth.

**Sources (2026-06-05):** Statista (market share) · Mordor (penetration/ARPU) · Vietnamnet (fiber speed) · 6Wresearch (FWA) · DatacenterDynamics (DC) · BQ `ticker_financial` FOX.

---

## BMP — Binh Minh Plastics (HOSE) · PVC pipes
**Tag:** `NARROW` · type `BRAND/DISTRIBUTION/COST` · entry `M` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** (8L quant STRONG/rating-1 — the record margin is a windfall, not the moat).

**Verdict:** NARROW. A real southern-VN brand/distribution + SCG resin-cost edge (rules out NONE), but the current
best-in-history **47% GPM is a transient cheap-PVC-resin windfall**, not durable pricing power — it marched 35.7%
(2023Q2)→47.2% (2026Q1) in lock-step with the 2023-24 resin crash, and brokers model it reverting to ~43% as HDPE
(+45%) / PVC (+31% YTD 2026) reflate. The moat is **visibly eroding**: BMP lost share 27%→23% (end-2024) and bought
it back only with **5-year-high discounting** (disc+sales/revenue 19.7%) — a defending franchise, not a pricing-power one.

**5-Forces:** Rivalry HIGH (commoditized pipes; BMP/NTP/HSG/Dekko compete on price). Buyer MED-HIGH (price-sensitive
contractors). Supplier MED (PVC resin swing input, mitigated by SCG/Nawaplastic 55% vertical supply = genuine cost edge
+ minority/transfer-pricing overhang). Entry MED / substitutes LOW (scale+distribution deter entry = the durable part).
**Quant:** avg ROIC5Y 40%/ROE5Y 31% dazzle, but ROIC_Min5Y 13.5%/ROE_Min5Y 9% floors = cyclical; ~100% payout (148.6%
cash div, real-lev 0.02, FSCORE 8) = saturated cash-cow, no reinvestment runway. **#1 risk:** resin reflation compresses
the windfall margin + price competition erodes home-turf share.

**Sources (2026-06-05):** TheInvestor (resin shortage) · DNSE/BSC (share loss/discounting) · Fili (BMP-NTP race) · Vietcap (OP) · Vietstock (record dividend) · BQ `ticker_financial` BMP.

---

## KSF — KSFinance / Sunshine Group (UPCoM) · luxury RE + finance holding   ⛔ NONE
**Tag:** `NONE` · type `NONE` · entry `L` · asof **2026-06-05** · src `5f_validated_compet`
**First tag** — a confirmed **quant-moat FALSE-POSITIVE** (same pattern as VVS/HAG).

**Verdict:** NONE. The 66% GPM that triggered quant moat=STRONG is the **artifact of related-party project transfers +
2024-25 M&A consolidation** (assets jumped 20.5tn→119.6tn, ~6x; 2025 "profit blowout" 11,294bn), not organic repeatable
returns — while **ROIC_Min5Y 1.0% / ROE_Min5Y 3.5%** expose zero durable through-cycle profitability and **no Porter
force shows a protected barrier**.

**Business ID:** CTCP Tập đoàn Sunshine (ex-Phú Thượng → KSFinance → Sunshine Group), Đỗ-Anh-Tuấn / Sunshine-ecosystem
luxury-RE + "finance" holding. **5-Forces:** all forces hostile — entry low (acquired not earned scale), buyers
discretionary/price-sensitive (RevYoY −89%→−66% before the 2025 handover spike), capital base distressed (bond
SHJCH2124001 late/short interest, app-withdrawal locks Nov-2022), every rival project substitutes. **Governance overlay
(decisive):** active fraud/embezzlement complaints (Art.174) referred to the Ministry of Public Security, retail-fund
withdrawal locks, bond defaults. D/E 5.01x, FSCORE oscillates 1↔7, PE ranged 7x→244x = lumpy manufactured earnings.
**#1 risk:** related-party/consolidation earnings + fraud complaints + bond defaults; zero through-cycle return floor.
**Do NOT tag WIDE/NARROW.**

**Sources (2026-06-05):** Vietstock (corporate profile) · BaoPhapLuat (2025 restructure results) · Hoanhap (fraud complaint) · Founder.com.vn (bond default) · BQ `ticker_financial` KSF.

---

# Cyclical-framework reviews (commodity-price-regime × stock-dislocation lens — NOT 5F brand)

> These three were assessed through the existing **cyclical commodity framework** (`cyclical_multi.py` / `sugar_cyclical.py`,
> see [[cyclical_commodity_framework_2026]] / [[sugar_cyclical_trend_2026]]) instead of the 5F brand lens, because their value
> driver is a commodity cycle, not a consumer moat. The tag is NARROW (real but cyclical/price-taker), and the actionable
> output is the **buy-timing read** (where the commodity sits in its cycle × whether the stock is dislocated). src `5f_cyclical`.

## DRI — Dầu Tiếng – Đắk Lắk Rubber (HOSE) · natural rubber
**Tag:** `NARROW` · type `LOCATION/COST` · entry `M` · asof **2026-06-05** · src `5f_cyclical` · **buy-timing: WAIT**

Rubber regime (cyclical_multi, 2026-03): **good=True, pctile5y=0.95** (95th = expensive end); current price **$2.30/kg
(Jun-2026), highest since Jan-2017, +43% YoY** on Thai-flood/Indonesia-dry supply deficit (2026 fwd avg forecast ~$1.85
→ downside). Framework bucket where DRI sits ("commodity GOOD + normal-dd") = **1Y med −0% / 46% win, 2Y −1%** = poor
forward; the money bucket is "WEAK + deep-dd" (+37%/79%) which is the OPPOSITE of now. DRI earnings are **peak-cycle**
(GPM 38.4%, NPM 23.8%, NP_YoY +40%) — the quant STRONG/high-margin signal is a rubber-price peak illusion. Moat = NARROW
(plantation land/cost edge but price-taker; ROE_Min5Y 10.7% = modest cyclical floor). **Read: WAIT for rubber correction
+ stock dislocation (pb_z +0.44 not cheap); do not chase the peak.**

**Sources (2026-06-05):** cyclical_multi.py (rubber pctile 0.95) · TradingEconomics (rubber $2.30/kg, 9-yr high) · BQ `ticker_financial` DRI.

## CSV — Hóa chất Cơ bản Miền Nam (HOSE) · caustic soda / chlor-alkali
**Tag:** `NARROW` · type `COST/SCALE` · entry `M` · asof **2026-06-05** · src `5f_cyclical` · **buy-timing: AVOID (expensive)**

CSV is the **dominant southern-VN caustic-soda (NaOH) / chlorine producer** — sticky industrial demand gives a decent
floor (ROIC_Min5Y 14.3%, ROE_Min5Y 13.7%) and a regional scale/cost edge, but it is a **commodity price-taker**.
**Product mix (verified 2026-06-05):** NaOH sold mostly as **liquid xút 25/32/40/50%** + some flakes; NaOH ≈27% of revenue,
chlorine ~15%, H₂SO₄ 7-8%, silicate 6-7% (caustic–chlorine segment >50% rev / >70% gross profit; ~40k t/yr, ~20% national
capacity). **Price-proxy basis = flakes-98% FOB benchmark** (`data/caustic_soda_monthly.csv`, consistent across all months).
CSV realizes domestic liquid-32% prices, but those are set off import-parity to the same regional chlor-alkali cycle the
flakes benchmark tracks, so it's the correct DIRECTIONAL proxy (the regime detector uses percentile/direction, not absolute
level — the cheap-looking liquid 30-50% quote, ~$270-340/MT, is water-diluted and on a 100%-NaOH basis is actually *higher*
than flakes, so it must NOT be substituted as the level). Caustic
soda 2026 outlook **bearish** ($690-740/MT range-bound, alumina/pulp demand softening + Chinese chlor-alkali capacity
glut). CSV earnings already rolling over (NP_YoY −18%, margin squeeze) yet the stock is **expensive** (PE 15, pb_z +0.57
above own avg) — not a contrarian trough buy. ✅ **Data bug fixed (2026-06-05):** `COMMODITY_MAP` now maps CSV→"caustic_soda"
(was wrongly "dap"); added `data/caustic_soda_monthly.csv` (NaOH FOB Asia, anchor-interpolated, AMPLE/glut structure) so the
framework reads CSV off its true chlor-alkali cycle (pctile ~0.70, elevated-but-soft) instead of the phosphate (DAP) chain.
**Read: AVOID at current valuation.**

**Sources (2026-06-05):** CAMAL/Procurement (caustic soda 2026 bearish, $690-740/MT) · cyclical_multi.py · BQ `ticker_financial` CSV.

## QNS — Đường Quảng Ngãi (UPCoM) · sugar + Vinasoy soymilk
**Tag:** `NARROW` · type `BRAND/COST` · entry `M` · asof **2026-06-05** · src `5f_cyclical` · **buy-timing: ACCUMULATE-on-quality, sugar headwind near-term**

QNS is a **hybrid**, not a pure cyclical: ~half **Vinasoy soymilk** (branded defensive consumer business = the durable
floor, drives ROE_Min5Y 17.7% / ROIC_Min5Y 14.5%) + ~half **sugar** (cyclical, tariff-protected). Per the **sugar
trend-rule (which INVERTS the contrarian logic — buy GOOD-regime dips, AVOID weak)**, the sugar leg is in a **WEAK regime
now**: world sugar price low + the **Thai anti-dumping duty 47.64% EXPIRES 15-Jun-2026** (next week) → cheap-import/dumping
risk returns. So the sugar leg is a near-term headwind. BUT the soymilk brand + **cheap valuation (pb_z −0.53, PE 8.8)**
cushion it — QNS is the best of these 3 cyclicals on quality/valuation, worst on near-term sugar catalyst. Moat = NARROW
(soymilk brand real-but-limited + protected-but-weak sugar). **Read: accumulate on the soymilk quality/cheapness; size
for the sugar/AD-expiry headwind.**

**Sources (2026-06-05):** [[sugar_cyclical_trend_2026]] (Thai AD duty expiry 15-Jun-2026, sugar WEAK) · sugar_cyclical.py · BQ `ticker_financial` QNS.

---

# P3 thin-liquidity worklist — compact reviews (light-touch 5F: quant + sector-archetype + 1-2 web checks)

> These are illiquid micro-caps (<5bn/day) where a tag has low *deployability* value but completes coverage. Reviewed by
> sector archetype (validated on the liquid names above) + durability quant + a targeted web check. The detailed `risk1`
> in `moat_tags.csv` is the primary record; this table is the evidence/source trail. asof 2026-06-05, src `5f_validated_compet`.

### Batch 1 (liq 5.0 → 1.0 bn/day)
| Ticker | Tier | Type | Archetype & verdict (1-line) | Key sources |
|---|---|---|---|---|
| **SCS** | NARROW | REG/LOCATION | Air-cargo terminal **duopoly** at TSN (ROIC 36%, GPM 78%) — elite but single-airport; Long Thanh re-bid caps WIDE | FPTS/ACBS reports, DDN |
| **TLG** ⭐ | **WIDE** | BRAND/DIST | #1 stationery ~60% pen share, 3800 POS — **Kokuyo JP buying >65%** validates; entry L (rich/thin) | Vietnamnet (Kokuyo), Vietcap VAD |
| **NTP** | NARROW | BRAND/DIST | North-VN #1 pipe (BMP=south); GPM flat 31% = pass-through not windfall; regional + resin price-taker | NTP AR2024, TraceData |
| **BWE** | NARROW | REG/LOCATION | Binh Duong water natural-monopoly, tariff-capped (ROIC 8.4% thin), debt-funded capex | Biwase, ADB |
| **DHA** | NARROW | LOCATION | Stone quarry (NNC archetype); **Thanh Phu 2 license expires Dec-2028** reserve cliff; fortress B/S | Pinetree, BMSC, Cafeland |
| **TV1** | NARROW | REG/AFFILIATION | PECC1 EVN 500kV-design incumbency (76% captive-EVN) + **chairman arrested** governance flag | Vietstock, EVN, Vietnam.vn |
| **DTD** | NARROW | LOCATION | Thanh Dat IP dev (Dong Van III Ha Nam); **below book PB 0.58**, low real-lev; lumpy land-sale rev | DauTuCoPhieu, Vietstock |
| **DBD** | NARROW | REG/NICHE | Bidiphar — VN's 1st GMP-EU **oncology** plant + dialysis niche, hospital lock-in; ETC-tender risk | Bidiphar, TheInvestor |
| **DVP** | NARROW | LOCATION | Dinh Vu Hai Phong port — eroding to upstream **Lach Huyen** deep-water; high-return but contested | Saodo, VietnamPlus |
| **NCT** | NARROW | LOCATION/REG | Noi Bai cargo terminal — elite (ROIC 54%) but **3 handlers** (not duopoly) + ACV favors ACSV | MarketScreener, ALS, Vietstock |

### Batch 2 (liq 0.90 → 0.30 bn/day)
| Ticker | Tier | Type | Archetype & verdict (1-line) | Key sources |
|---|---|---|---|---|
| **VLB** | NARROW | LOCATION | Bien Hoa stone quarry (NNC archetype); ROE_Min5Y −6.2% = pre-2018 special-div artifact not capital loss (ROIC 22.6%) | Vietstock, ASEAN Briefing |
| **DHG** ⭐ | **WIDE** | BRAND/DIST | #1 domestic pharma — **30k pharmacies** distribution moat + Taisho 51%; mature/low-growth, entry L | TheInvestor, DHG AR2025 |
| **HTI** | NARROW | REGULATORY | BOT toll road — **finite concession expires ~2032/33** then reverts free (melting annuity, value via run-off DCF) | Vietstock, VietnamPlus |
| **NTC** | NARROW | LOCATION | Nam Tan Uyen IP — NTU-3 catalyst (Q4-2026); ROE carried by Phuoc Hoa associate-div (ROIC core only 4%) | InvestVietnam, Vinahugo |
| **SGP** ⛔ | **NONE** | NONE | Saigon Port FALSE-POS — legacy ports relocating = concession extinguished; land+JV asset-play not franchise (ROIC 3%) | Shinhan, DTTC (broker SELL) |
| **FOC** | NARROW | BRAND | FPT Online/VnExpress #1 news audience moat but **ad-share leaking to Google/Meta/TikTok** (secular governor) | Statista, Similarweb |
| **SZL** | NARROW | LOCATION | Sonadezi Long Thanh IP (by airport) — moat real but **land bank ~26ha left** (growth stalls), PB rich | Sonadezi, Congluan |
| **SAS** | NARROW | LOCATION/REG | SASCO duty-free TSN concession; COVID-scarred (3Y floors healthy); **Long Thanh rights = key catalyst/risk** | SASCO AR2025, TravelMole |
| **TRA** | NARROW | BRAND/DIST | Traphaco #1 herbal-OTC (Boganic) + vertical GACP herb supply; high-end NARROW (niche, modern-pharma flank) | Traphaco, Euromonitor |
| **SLS** | NARROW | LOCATION/COST | Son La Sugar (`5f_cyclical`) — **AVOID**: sugar WEAK regime (world crash+smuggling); ⚠️**Thai AD duty EXTENDED 16-Jun-2026 not expired** | ChiniMandi, Czapp |

> ⚠️ **Correction (batch 2):** the Thai sugar anti-dumping duty (47.64%) was **EXTENDED effective 16-Jun-2026**, NOT expired — earlier QNS/SLS notes that said "expires 15-Jun" were wrong; import protection stays intact, the sugar headwind is world-price crash + smuggling. QNS risk1 corrected in moat_tags.csv.
