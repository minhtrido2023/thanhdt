# Construction Contractors (Civil / Industrial EPC) — Sector #18 Valuation Framework

> **Author:** Taylor (Quant) · **Job:** Taylor_20260706_033659 (dispatch from Mike) · **For:** DollarBill, user (via Mike)
> **Scope:** RESEARCH-ONLY, new files only (`construction_screen.py` + this doc + `data/construction_*`). Production (custom30V/BAL/LAG/DT5G) untouched.
> **Verdict up front: LENS, NOT A BOOK (Rule 3). No watchlist buy candidate. The deliverable is a RISK/EXCLUSION framework, not an entry signal.** The AR/cash quality gate is a valid *avoid* filter (dodged the −62% sector drawdown, rejected HBC through its entire blow-up); it is not tradeable as a long book (in cash 84% of months, OOS ≈ flat).
> Point-in-time values on **2026-Q1** BQ cache (`ticker_financial`, `ticker_prune` to 2026-06-26). Backtest self-check 0 VND PASS, threads=1, walk-forward IS(2014–19)/OOS(2020–26).

---

## 1. What this sector IS (and is NOT)

Vietnam listed construction is a **pure-contractor group** — general contractors (GC), EPC, foundation/ground-engineering, road/public-infra builders. They take on projects and get paid on completion; **they do not own long-lived infrastructure assets**.

**Three hard separations (Rule 1 — split by economics, not ICB code):**
- **≠ BOT-toll asset OWNERS** (CII / HHV / CTI / PC1) — those own concession assets, are D&A-heavy, and are routed to `rating_8l.py` **D&A_HEAVY** on EV/EBITDA. **Excluded here.**
- **≠ telecom-infra** (CTR — the documented ICB trap: tagged "construction," is actually a Viettel tower-co on EV/EBITDA).
- **≠ RE developers** (sector #3, P/B-vs-NAV). A contractor *builds for* a developer; it does not carry the land bank. The two are on opposite sides of the same receivable.

**Universe (hand-curated, liquid core ADV-2024+ > 5B):**

| Ticker | Name | Sub-type | Role in this study |
|---|---|---|---|
| **CTD** | Coteccons | flagship civil GC | the **survivor / quality anchor** (weathered 2022–23) |
| **VCG** | Vinaconex | civil + public-infra GC (+RE arm) | largest; healthiest balance sheet of the big-caps |
| **HBC** | Hòa Bình CG | civil GC | the **CRISIS CASE STUDY** (2022–23 receivables blow-up) |
| **FCN** | Fecon | foundations / ground-eng / infra | mid-cap, chronically high DSO |
| **LCG** | Licogi 16 | infra + renewable-EPC | structurally **very high DSO (400–600d)** yet survives |
| **C4G** | Cienco4 | roads / public infra | high-leverage road builder |
| **HTN** | Hưng Thịnh Incons | civil GC | **live HBC-repeat in progress (2026)** — see §5 |
| **DPG** | Đạt Phương | bridge/road EPC → hydro+materials | diversified away → cleaner metrics (borderline) |
| VC3 / DC4 / G36 | Vinaconex 3 / DIC No.4 / Tổng 36 | small-cap tail | thin, kept for breadth |

Excluded: CII/HHV/CTI/PC1 (BOT), CTR (telecom), ROS/PVX (fraud/delisted). Aquaculture/other protein is a different sector.

---

## 2. Why generic valuation fails here — the two structural facts

**(a) Percentage-of-completion (POC) accounting makes P/E NOISE.** Revenue and profit are booked as a project progresses — long before cash is collected. Reported earnings diverge violently from cash and swing the P/E through absurd/negative territory:
- CTD: PE **−65.6** (2022Q2) → **+140** (2022Q4) → **+322** (2023Q1). HBC: negative through all of 2023. **P/E is unusable as a valuation primary.** (Confirmed by data, not asserted.)

**(b) Receivables ARE the risk.** The contractor finances its developer client. AR balloons structurally (CTD carries ~11T VND of AR on ~3T quarterly revenue; **DSO of 230–300 days is normal**, LCG runs **400–600 days** and survives). With **razor-thin gross margins (GPM 0–8%)**, there is no cushion: when a client (NVL-era stressed developers, 2022–23) stops paying, a single bad-debt provision **wipes out years of profit and eats into equity itself**.

**International parallel (the playbook this borrows from):** global EPC contractors (Fluor, AECOM, Larsen & Toubro, Vinci, Bouygues) are valued on **backlog-to-revenue coverage + margin + cash conversion**, never trailing P/E. The canonical blow-up is **Carillion (UK, 2018)**: aggressive POC revenue recognition, ballooning receivables, operating cash flow persistently *below* reported profit → insolvency. **HBC 2022–23 is the Carillion script, line for line.**

> **Backlog is genuinely uncapturable in BQ** (no order-book field). `Revenue_YoY_P0` is a *coincident realization* of backlog, not a leading signal — treat it as a weak coincident proxy only, the same way DY is uncapturable (Rule 2). This is an accepted data limitation, not a solvable gap.

---

## 3. The signal test — what actually predicts forward return (`construction_screen.py` PART 1)

Spearman IC of each factor vs forward T+20/40/60 VNINDEX-relative return (`profit_1M/2M/3M`, **evaluation-only, never a live filter**), 25,341 name-days, 11 names, 2014→2026:

| Factor | IC(3M) | Read |
|---|---|---|
| **`pb_rel` = PB / PB_MA1Y** (trough proxy) | **−0.065** | **WRONG-SIGNED. Cheaper-vs-history predicts WORSE returns** — the P/B-trough TRAP. Sector IC (−0.065) is **20× more negative than whole-market** (−0.003) → sector-specific, not a market artifact. |
| `dso_chg` = DSO_P0 − DSO_P4 (deterioration) | −0.030 | Correct sign (rising receivables → worse fwd), but weak. |
| `ar_rev` = AR / (Revenue×4) | +0.002 | Noise (absolute AR level is structural, not a signal). |
| **`cfoa` = CF_OA_P0** (cash conversion) | **+0.052** | **The ONLY reliably correct-signed factor. Cash-generative names outperform** — but weak in magnitude. |

**Regime split (mean forward T+60):** clean 5.5% · mixed 6.3% · **stressed 3.8%** (n=2,754 / 7,112 / 15,475). The quality gate **avoids the worst tercile** but does not beat "mixed" — the edge is *risk reduction, not return*.

**Takeaway:** the sector's own "value" signal (cheap P/B) is actively *harmful*; the only useful signal is *cash quality*, and it is weak. This is the quantitative case for treating the sector as an **exclusion problem, not a selection problem.**

---

## 4. The three backtests — book or lens? (`construction_screen.py` PART 2)

Monthly rebalance, EW, TC 0.1%, hold cash when no name qualifies, self-check 0 VND PASS.

| Screen | Full CAGR | Full MaxDD | Full Calmar | OOS 2020–26 edge vs B&H | Months held | Verdict |
|---|---|---|---|---|---|---|
| **A — AR-quality contractor** (cheap **AND** cash-clean **AND** DSO not deteriorating **AND** solvent) | 3.1% | **−18.0%** | 0.17 | **+0.2% CAGR (≈flat), −11.2pp** | **25/148** (in cash 84%) | **RISK FILTER, not a book.** Dodges the disaster DD but structurally lags — too restrictive to be a long strategy. |
| **B — sector basket** (EW beta) | 15.0% | **−62.7%** | 0.24 | −3.1pp, Sharpe −0.20 | 147/148 | **Pure high-beta.** Big up-years (2016 +91%, 2021 +106%) paid for by −47% (2022). Calmar = B&H. Not investable. |
| **C — naive P/B-trough** (no quality gate) | **1.3%** | **−70.4%** | 0.02 | −9.8pp | 134/148 | **The documented TRAP.** Loses IS *and* OOS. |

**The counterfactual that proves the framework (crisis gate verify):**
- **Screen A REJECTED HBC through the entire 2022–24 crisis** (0 months held). ✅
- **Screen C (naive value) walked straight into HBC** — held it **Oct 2022 → Apr 2023** (i.e. *into* the −1.2T loss and equity wipeout) plus again mid-2024. ❌
- Screen A's distinct all-time picks: **{VCG, LCG, FCN, DPG}** — never HBC, never CTD (CTD was cash-negative when cheap, and not cheap-vs-history when clean). Median selected ADV 32B (liquid). Orthogonality vs custom30V 4%, vs 8L-top25 16% (genuinely uncovered names — but that does not make them tradeable).

**Conclusion:** no configuration produces an OOS-positive tradeable book. Screen A is a real *avoid* filter (the −18% vs −62% drawdown gap is the whole point); it is not a return generator. **LENS, NOT A BOOK.**

---

## 5. HBC case study + the live 2026 repeat (HTN) — the early-warning that WAS there

**HBC (Hòa Bình) — anatomy of the 2022–23 blow-up:**

| Quarter | DSO | Debt_Eq | CF_OA_P0 | NP_P0 | P/E | P/B | What the tape said |
|---|---|---|---|---|---|---|---|
| 2022Q1–Q3 | 139–175 | **3.1 → 4.0 (rising)** | **NEGATIVE** (−1.05T, −0.31T) | *positive* (+13B…+63B) | ~35–54 "ok" | 0.84–1.30 "cheap" | **THE WARNING:** book profit positive, but cash **burning** + leverage climbing |
| 2022Q4 | 157 | 5.40 | — | **−1,202B** | −2.3 | 1.03 | the loss lands |
| 2023Q1–Q4 | 182 → **386** | 6.2 → 27 → 38 → **162** | — | sustained losses | negative | 5.5 (**spiked**) | equity near-wiped; **P/B mechanically SPIKES as the denominator collapses** |

**The two lessons (both quantitatively confirmed):**
1. **The early warning fired ~3 quarters before the loss** — not in DSO's absolute level (LCG runs 400–600 and is fine), but in **CF_OA_P0 turning persistently negative *while the P&L still showed profit*, with Debt_Eq already >3 and climbing.** POC profit was fictional receivables; cash never came. This is exactly the Carillion tell.
2. **P/B-trough is a double trap here:** the pre-crash "cheap" P/B (0.84–1.03) *led into* the wipeout, and once equity collapses **P/B inverts to look expensive** (5.5) mid-crisis — so it fails as both an entry and a distress signal. Use **CF_OA + leverage**, never P/B, to read distress in this sector.

**⚠️ LIVE 2026 — HTN (Hưng Thịnh Incons) is HBC in progress.** 2026Q1: **DSO 2,425 days** (up from 1,485 a year ago), **AR/Revenue 49×**, P/E **−114**, GPM 6%, Debt_Eq 3.66 — a receivables collapse tied to a single stressed captive developer (Hưng Thịnh). **P/B is 0.46 — this is the trap, not a value entry. AVOID.** The framework flags it exactly as it would have flagged HBC in early 2022.

---

## 6. Point-in-time read (2026-Q1) — where the names stand

Whole sector runs **negative operating cash in Q1** (seasonal — contractors pay out early-year, collect later), so `CF_OA_P0` is noisy point-in-time; read `CF_OA_3Y` for solvency.

| Name | P/B | DSO (yoy) | Debt_Eq | CF_OA_3Y | Read |
|---|---|---|---|---|---|
| **VCG** | 1.15 | 64 (flat, low) | 1.37 | **+8.1T** | Healthiest large-cap balance sheet; IntCov 4.9. Current-quarter cash negative (seasonal). **WATCH** on a confirmed CF_OA turn — not a screen buy. |
| **CTD** | 1.01 | 168 (improving from 201) | 2.65 | −0.22T | The survivor; working-capital heavy, big Q1 cash draw (−1.7T). Not screen-clean; the sector's quality anchor to *watch*, not buy. |
| **DPG** | 1.47 | 53 (low) | 1.60 | −0.46T | Cleanest DSO (diversified into hydro/materials), but not cheap-vs-history and 3Y cash negative. |
| **DC4** | 0.66 | 99 (improving) | 0.95 | +0.39T | Small-cap (ADV ~7B); IntCov 37 — clean-ish but too thin to matter. |
| **LCG / FCN** | 0.74 / 0.62 | 203 / 157 (both **rising**) | 1.54 / 2.11 | +1.0T / +0.15T | Cheap P/B but DSO deteriorating → the trap zone. |
| **HBC** | 0.89 | **473 (rising)** | **7.14** | +2.5T (restructured) | Still stressed; P/B "cheap" = trap. Restructuring, not investable. |
| **HTN** | 0.46 | **2,425** | 3.66 | — | **Live HBC-repeat. AVOID.** (see §5) |

**No buy candidate.** No construction name is a catchable compounder (unlike DBC/MSH in sectors #16–17). The best a discretionary book can do here is **watch VCG/CTD for a genuine, cash-confirmed working-capital turn** — and even then it is a tactical beta trade, DT5G-gated, sized small, never a core sleeve.

---

## 7. Rules this sector adds / confirms (for `sector_watchlist_framework.md`)

1. **P/E is structurally unusable for POC contractors** (revenue-recognition noise) — never the valuation primary.
2. **P/B-trough is a TRAP in construction** (steel-parallel, but sharper): IC wrong-signed *and* worse than market; the cheap-P/B names are the AR-distressed ones, and equity collapse inverts P/B mid-crisis. **Never buy a contractor on cheap P/B.**
3. **The only correct-signed factor is cash conversion (CF_OA).** Read solvency off **CF_OA (vs reported NP) + Debt_Eq trend + DSO *trend*** — not DSO's absolute level (structurally high sector-wide) and not P/E.
4. **The AR/cash quality gate is an EXCLUSION filter, not an entry signal** — it dodges the drawdowns (−18% vs −62%) but is too restrictive (in cash 84% of months) to be a long book.
5. **Early-warning template (HBC/Carillion):** operating cash negative *while P&L shows profit* + leverage rising = distress ~3 quarters early. Applied live: **HTN 2026 = AVOID.**
6. **Verdict: LENS, NOT A BOOK.** Do not wire; do not add a construction sleeve. Add the *exclusion rules* to the sweep and flag HTN/HBC as receivables-blowup avoids.

---

### Auditability
Backtest: `construction_screen.py` → `data/construction_{arquality,basket,pbtrough}_monthly.csv` + `data/construction_verdict.json`. Self-check 0 VND PASS (arquality 0.0, basket 4e-6, pbtrough 3e-6). Prices/forward returns from `ticker_prune` cache; financials ASOF-joined from `ticker_financial` cache (STALE≤120d). Results pinned in `data/results_registry.md`. No production code touched.
