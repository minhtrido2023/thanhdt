---
name: fpt-ftel-deconsolidation-2026
description: "FPT Q1 2026 revenue YoY -22% is FALSE NEGATIVE caused by FTel deconsolidation (accounting change), NOT business decline. FA tier B is artifact — qualitative override warranted for whitelist Tier 1 status."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6a525d72-2310-410b-91ab-1e5ab95cbfeb
---

# FPT — FTel deconsolidation context (do not treat as fundamental decline)

## The accounting event

- **Mid-2025**: Bộ Công an took 50.2% of FPT Telecom (FTel) from SCIC → became largest shareholder
- **2026-01-01 effective**: FPT changed FTel from **subsidiary (full consolidation)** → **associate (equity method)**
- **2026-03-18**: FPT officially announced the change
- FPT still holds ~45% of FTel — recognizes only proportional profit share, no longer consolidates FTel's revenue+expenses

## What this does to reported numbers

| Metric | Before (full consol.) | After (equity method) |
|---|---|---|
| Consolidated revenue | Includes 100% FTel revenue | EXCLUDES FTel revenue (~1 trillion VND/yr removed) |
| Reported NP | Includes 100% FTel NP, then minority interest deducted | Includes only FPT's ~45% share via equity-method line |
| **NP attributable to parent shareholders** | unchanged | **unchanged** |
| **EPS** | – | **unchanged** |

## What BQ data says vs reality (Q1 2026)

| Field | BQ value | Reality |
|---|---|---|
| `Revenue_YoY_P0` | **-22.3%** ❌ | Real organic = **+8.5% YoY** (12.48 trillion VND) |
| `NP_YoY` | +14.4% | Real (parent shareholders) similar — unchanged by restructure |
| Tech segment | – | **87% of revenue, 56% of profit** — still growing strong |
| Q4 release `Release_Date` | 2026-04-28 | – |

## Model blind spot

`fa_ratings` table uses raw `Revenue_YoY_P0` from `ticker_financial` — sees -22% → penalizes growth/valuation axes → drops FPT **A → B (2026-05-08)**.

This is a **false negative** caused by accounting restructure. Core IT outsourcing business (FPT Software, foreign revenue) still growing.

Downstream impacts in models:
- `recommend_holistic.py` → FPT classified `COMPOUNDER_HOLD` (not BUY) because requires FA=A
- `whitelist_monitor.py` → flags 🟡 WATCH (FA=B)
- `recommend_lh.py` → FPT not in top picks (B-tier score lower than A cohort)

## When the model will self-fix

- **2026-Q2 release (~22-28/07/2026)**: still YoY ảo (Q2 2025 had full FTel consolidation, Q2 2026 doesn't) → revenue YoY still appears bad
- **2027-Q1 release (~04/2027)**: first apples-to-apples comparison (both periods equity method) → FA tier should auto-restore to A
- **Bridge period (Apr 2026 → Apr 2027)**: every quarterly release will show artificially weak YoY — model will keep giving false negatives. **Apply qualitative override.**

## Action implication

FPT KEEPS Tier 1 whitelist status [[long_hold_whitelist]] despite FA=B because the degradation is accounting, not fundamental.

**Override rule for buying decisions on FPT during bridge period**:
- Treat as Tier 1 compounder (not Tier 2 / WATCH)
- Sizing: start 3-5% NAV when price reclaims MA50 with confirmation (4+ weeks above, or +3% over MA50)
- Add 2-3% when Q2 2026 earnings confirm core (ex-FTel) growth >10%
- Full target 8% NAV after Q1 2027 release lifts FA back to A

**DO NOT** apply exit triggers from whitelist that key on FA tier drop **unless**:
- FA drops further to C (would signal real damage beyond restructuring)
- Tech segment YoY growth falls <10% (real core deterioration)
- IT outsourcing pipeline contraction (qualitative)

## How to apply

Whenever Claude (or model) flags FPT as WATCH/HOLD due to revenue YoY decline in 2026:
1. Check if the period covers Q1 2026 → Q4 2026 releases → likely false signal
2. Look at NP YoY and tech segment growth, not consolidated revenue
3. Reference this memory in any FPT recommendation through ~April 2027
4. After 2027-Q1 release: re-evaluate — if FA auto-restores to A, this memory becomes historical

## Sources

- [FPT Telecom thành công ty liên kết của FPT (CafeF 2026-03-19)](https://cafef.vn/chinh-thuc-fpt-telecom-tro-thanh-cong-ty-lien-ket-cua-fpt-sau-khi-ve-bo-cong-an-188260319021831267.chn)
- [FPT Q1 2026: NR 12.48T VND +8.5% YoY, Tech 87% revenue 56% profit (Smartkarma)](https://www.smartkarma.com/home/newswire/earnings-alerts/fpt-corp-fpt-earnings-1q-net-income-aligns-with-estimates-technology-fuels-growth/)
- [FPT Corp & FTel strategic split (The Investor)](https://theinvestor.vn/fpt-corporation-and-fpt-telecom-a-strategic-split-to-unlock-higher-valuation-d18674.html)
