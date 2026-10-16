---
name: moat_5f_8l_bridge_2026
description: 5F (Porter) qualitative moat → 8L L4 bridge as a GATE (not ranker) + interactive Telegram 2-block DNA/NOW report
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aee0eaa-e66c-43a2-9041-8e90dacf35eb
---

**5F ↔ 8L moat bridge + interactive bot report (built [REDACTED]03).** Connects the qualitative
**5F** persona (Porter 5-Forces, `5F.md`, a claude.ai project — assesses industry structure + firm
moat) into the quantitative **8L** ranker. See [[fa_layer_ic_audit_2026]] (FA-as-ranker FAILS full-NAV).

**Core decision — moat = GATE/durability multiplier, NOT additive points.** 8L's L4 was only an ROE
proxy, fooled by cyclical high-ROE (DGC ROE 37% looks "STRONG" but 5F reads NARROW cost-position; DRC
no-moat→transient). User insight: *moat is rare + stable over years* → so the tag file is a small,
hand-maintained, ~annual-review **registry**, and look-ahead risk is minimal (a stable structural fact,
not a trading signal). Overlay is intentionally ASYMMETRIC: NONE = big haircut (−16 on a high-ROE+deep-dd
block: L4→3 + buy-fear ×−0.5), WIDE = small bonus (+1.2: L4 floored 12, dislocation ×+0.15, capped at
ceiling 15), NARROW/untagged = no-op. Mainly removes false-positives, doesn't mint points.

**Files built:**
- `moat_5f.py` — schema + `load_moat_tags()` + `apply_moat_overlay()` (knobs at top: WIDE_FLOOR 12,
  NONE_CAP 3, factors +0.15/−0.50). Bounded, backward-compatible (no file → no-op).
- `data/moat_tags.csv` — the registry (cols: ticker,moat_tier WIDE/NARROW/NONE,moat_type,entry,risk1,asof,src).
  Hand-edit (NO intake script — over-engineering for a tiny stable table). Seeded VCS=WIDE, DGC/QTP/NNC=NARROW,
  DRC=NONE from validated 8L_README verdicts. `risk1` = kill-condition to watch (when the stable moat changes).
- `rank_8l.py` — imports overlay, applies in score_row, shows `5F` column. LIVE-ONLY: never wire into
  prodspec backtester (post-hoc/non-point-in-time → look-ahead).
- `dna_card.py` — added `5F-Moat:` line (tier + type + risk1) to bank & compounder branches + CSV cols.

**Interactive Telegram bot — ALREADY EXISTED, do NOT rebuild.** `telegram_8l_bot.py` long-polls
getUpdates, user texts a ticker → `reply_for()`. Upgraded only the renderer via new `dna_report.py`
`build_report(tk)`. **Two-clocks layout** (user's framing): 🧬 DNA (slow/structural — route·engine·
moat+5F+risk1·TAM·margin, from CACHED unified_screener/dna_cards/moat_tags) + ⚡ NOW (live BQ AT QUERY
TIME — price·%chg·pe_z/pb_z·dd·liq·**regime**·rank). Only NOW pays live-query cost; DNA cached (correct,
changes per quarter). Each block stamped with own freshness. Ngũ-Hành regime from `tav2_bq.vnindex_5state`
(state **1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EX-BULL**, weights 0/20/70/100/130%, cached 5min). Quick-read =
gate-style synthesis (regime+dislocation+moat tier), explicitly "not a buy signal".

**Re-validation via `/competitive-analysis` skill ([REDACTED]05).** Decided to run the deck-skill ONLY on
*claimed* moats (WIDE/NARROW) — NONE names are readable from financials, not worth the qualitative cost
(asymmetry: validate where being wrong is expensive). Full Porter 5F + BQ quant cross-check on all 4
non-NONE names. Outcome: **VCS WIDE→NARROW** (the only tier change) — its WIDE thesis rested on (a) US-ADD-
on-China = a *borrowed* regulatory tailwind now reversing vs Vietnam (20-46% US tariff; US share already
collapsed 80%→25%), and (b) a category facing the **silicosis** existential overhang (Australia banned
engineered stone 2024-07, California pending). DGC/QTP/NNC stayed NARROW (FA already flagged them right):
DGC = cyclical cost edge not through-cycle (ROIC_Min5Y 14% vs peak 29%); QTP entry M→H (PDP8 no-new-coal
barrier) but bond-proxy/terminal-asset; **NNC risk note corrected** — Nui Nho pit expired 2019, real asset
= Mui Tau quarry licensed to 2043 (~20yr, single-asset ~94% rev), NOT near-term depletion. All re-tagged
asof [REDACTED]05 src `5f_validated_compet`. **New artifact: `data/moat_dossiers.md`** = one sourced 5F memo
per claimed-moat name (Porter verdict + quant cross-check + point-in-time URLs) so a moat call can be
defended with evidence later; same LIVE-ONLY rule (never feed backtest). Open follow-up: registry is only
5 hand-picked names — *coverage* (which names deserve a tag) is the bigger gap than *accuracy*, deferred.

**Registry EXPANSION batch-1 contestable ([REDACTED]05).** Pool = quant-moat=STRONG & rating≤2 & route∈{COMPOUNDER,
CYCLICAL,REALESTATE,POWER} (`data/moat_5f_candidates.csv`, 75 left; bank/securities dropped = route-noise). Ran full
5F on the 4 liquid CONTESTABLE names → **all NARROW, all found the quant STRONG tag OVERSTATED**: GMD (port concession
real but Cai Mep cluster overbuilt + ROE inflated by one-off port-stake sale gains, true ROIC 6.5-9%); VGC (only IP
land-bank ~70% GP is moat, glass/materials cyclical drag); VHM (land bank real but RE-dev cyclical+depleting, Land-Law-
2024 cost, leverage→2.2x, ROE episodic + related-party bulk sales as financial income); IDC (IP finite ~3-4yr land +
captive utilities ballast, lumpy recognition). **Systematic finding: GPM-based quant moat OVER-rates asset-heavy/
cyclical/one-off-revenue names → 5F consistently downgrades STRONG→NARROW** (same lesson as VCS WIDE→NARROW). All 4
added to moat_tags.csv + dossiers. NOTE: NARROW = NEUTRAL in overlay (no floor/no haircut) → tagging them does NOT
change rank_8l scores, value is documentation/coverage + preventing future WIDE misreads. ⚠️ **HAG = quant-moat
FALSE-POSITIVE** (STRONG but ROE_Min5Y −7.5% capital-destroyer) — still in worklist, do NOT tag WIDE/STRONG. Remaining
deployable worklist = mostly obvious blue-chips (FPT/VNM/MCH/SAB/FOX/BMP, low 5F value) + cyclicals w/ frameworks
(DRI/QNS/CSV) + KSF. Registry now 9: VCS/DGC/QTP/NNC/GMD/VGC/VHM/IDC=NARROW, DRC=NONE. Pattern holds: **zero WIDE
survives scrutiny so far** — VN mid/large caps rarely have durable wide moats; most "moats" are cyclical/contested/
finite-land. Dossiers: `data/moat_dossiers.md`.

**Registry EXPANSION batch-2 blue-chips + KSF ([REDACTED]05).** User: "có thể mọi thứ thay đổi như VCS rồi" → ran full
5F on the deployable blue-chip pool (don't rubber-stamp; allow WIDE if truly durable). Results — **the user was right,
moats DID change**: **VNM = WIDE** (FIRST WIDE to survive — national 240k-POS distribution + brand + fortress B/S +
22-26% durable ROIC survived a self-inflicted 2024-25 restructuring; but a *trimmed* wide, premium fresh-milk share
leaking to TH True Milk + FTA imports). **FPT = NARROW** (elite realized durability BUT GenAI commoditizing the IT
labor-arbitrage model — TCS/Infosys crashed 2026; Japan switching-cost lock-in is the edge; WIDE telecom leg being
deconsolidated out of core). **SAB = NARROW** (textbook VCS-style: excise tax 65%→80%/2026→100%/2030 + Decree-100
drink-driving demand hit; lost #1 to Heineken 42%→34%). **MCH = NARROW** (moat only in seasonings core, noodles #2 vs
Acecook, MSN/WinCommerce related-party channel). **FOX = NARROW** (sub-scale #3 vs Viettel/VNPT, broadband saturation +
5G FWA substitution). **BMP = NARROW** (47% GPM = transient cheap-PVC-resin windfall reverting; lost share, record
discounting). **KSF = NONE** (confirmed quant FALSE-POSITIVE like VVS/HAG — 66% GPM = related-party transfers + M&A
consolidation, ROIC_Min5Y 1%, D/E 5x, ACTIVE FRAUD COMPLAINTS + bond defaults). All 7 tagged + dossiers.
**VNM WIDE overlay VERIFIED firing** in rank_8l (_L4_moat floored 12, _moat5f_dur +0.8); KSF NONE haircut. rank_8l/
dna/screener refreshed. **Registry now 16: 1 WIDE (VNM), 13 NARROW, 2 NONE (DRC,KSF).** Worklist `moat_5f_candidates.csv`
68 left, deployable cleared except HAG (false-pos, don't tag), DRI/QNS/CSV (cyclical, frameworks exist). **Meta-pattern:
1/12 names earns WIDE; quant GPM-moat systematically over-rates → 5F downgrades; durability-floor red-flags (ROE_Min5Y<0
or ~0) reliably catch quant false-positives (VVS/HAG/KSF).**

**Registry batch-3 cyclicals via commodity-framework ([REDACTED]05, src `5f_cyclical`).** DRI/QNS/CSV assessed through the
commodity-regime×dislocation lens ([[cyclical_commodity_framework_2026]]/[[sugar_cyclical_trend_2026]]) not 5F brand. All
**NARROW** + a buy-timing read: **DRI=WAIT** (rubber 95th-pctile, $2.30/kg Jun-2026 9-yr high +43%YoY on Thai-flood deficit
→ framework 'GOOD regime'=poor fwd 1Y −0%; DRI earnings peak-cycle, contrarian says buy the trough not now). **CSV=AVOID**
(caustic-soda/chlor-alkali bearish 2026 $690-740/MT on alumina-soft+China glut, NP_YoY −18%, expensive PE15/pb_z+0.57;
⚠️ **DATA BUG: COMMODITY_MAP mis-tags CSV as 'dap' — it's chlor-alkali NaOH, wrong price proxy**, fix needs a caustic-soda
series). **QNS=ACCUMULATE-on-quality** (hybrid: ~half Vinasoy soymilk branded-defensive = durable floor ROE_Min5Y 17.7%
+ ~half sugar; sugar WEAK regime + Thai AD duty 47.64% EXPIRES 15-Jun-2026 = near-term headwind, but cheap pb_z −0.53/PE
8.8 cushions). **Registry now 19: 1 WIDE (VNM), 16 NARROW, 2 NONE (DRC,KSF).** Deployable 5F worklist now fully cleared
(only HAG=false-pos left, don't tag). Tags+dossiers in `data/moat_dossiers.md`.

**Registry batch-4/5 P3 thin worklist ([REDACTED]05, light-touch: quant+archetype+1-2 web).** Processed top-20 by liquidity
of the 64 P3 (<5bn/day) names; user chose to STOP after these (rest = 45 untradeable dregs <0.30bn/day, not worth deep
review). **2 more WIDE found** (both dominant consumer/distribution franchises, the recurring WIDE archetype): **TLG**
(Thien Long #1 stationery ~60% pen share, Kokuyo JP buying >65% validates) + **DHG** (DHG Pharma #1, ~30k-pharmacy
distribution moat, Taisho 51%). **1 more NONE** (**SGP** Saigon Port FALSE-POSITIVE — legacy ports relocating =
concession extinguished, land/JV asset-play not franchise, ROIC 3%; VVS/HAG/KSF pattern). Rest NARROW by archetype:
air-cargo terminals (SCS duopoly/NCT 3-handler), stone quarries (DHA/VLB = NNC family), ports (DVP/eroding-to-Lach-Huyen),
IP-RE (NTC/SZL/DTD = IDC family), water (BWE reg-monopoly), pharma (DBD oncology-niche, TRA herbal-brand), BOT toll
(HTI finite-concession=melting annuity exp 2032/33), online media (FOC=VnExpress, ad-share leaking to Big Tech),
power-consulting (TV1 EVN-incumbency + chairman-arrest flag), airport-retail (SAS COVID-scarred use 3Y floor). SLS sugar
= `5f_cyclical` AVOID. **⚠️ CORRECTION: Thai sugar anti-dumping duty 47.64% was EXTENDED eff 16-Jun-2026, NOT expired**
(earlier QNS/SLS "expires 15-Jun" notes were WRONG — fixed; sugar headwind = world-price crash + smuggling, not tariff
lapse). **FINAL registry = 39 tags: 3 WIDE (VNM/TLG/DHG), 33 NARROW, 3 NONE (DRC/KSF/SGP).** TLG/DHG WIDE overlays
verified firing in rank_8l (_L4_moat=12). Dossiers compact-table format in `data/moat_dossiers.md` (batch 1+2). Worklist
`moat_5f_candidates.csv` = 45 untradeable left (parked). **Meta confirmed: ~3/27 reviewed earn WIDE, all dominant
brand+distribution; quant GPM-moat over-rates (5F downgrades STRONG→NARROW); near-zero durability floors = reliable
false-positive flag (VVS/HAG/KSF/SGP).**

**Bug fixed:** live_now join needed `lt.ticker=t.ticker` (was joining all tickers same date → wrong row);
nan-guard via `_s()` for bank cards (no moat_type/tam/margin).
**Coverage gap (CLOSED):** `dna_card.py` no-arg now profiles the FULL universe from unified_screener.csv
(`_universe()`, fallback to curated list) → `dna_cards.csv` = 129 rows. Added as step [4/6] in
`pt_8l_daily.bat` (after rank_8l, before alerts) so DNA cards refresh nightly. Bot needs restart to load
new code (dna_report import).
