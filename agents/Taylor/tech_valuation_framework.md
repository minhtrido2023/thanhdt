# Technology (IT Services) — Valuation Framework & Screen

**Job:** Taylor_20260630_071941 · **Script:** `tech_screen.py` · **AUDIT_END** 2026-06-26
**Sector #11 of the sector-compounder sweep.** Verdict: **REAL entry-timing LENS on FPT, NOT a sector book.**

## 1. What VN "tech" actually is
Not SaaS/product. It is **IT SERVICES** (offshore outsourcing for JP/US/KR) + system integration +
education — archetype **Infosys / TCS / Wipro**, capital-light, recurring revenue, ROIC-driven moat.
International valuation playbook: **P/E primary** (stable recurring, not lumpy like commodity), EV/Rev
secondary while margin expands, thesis = revenue growth + margin expansion, **ROIC>20% = moat**.

## 2. Structural reality — the liquid+quality universe is ONE name
Coverage in `ticker_prune` (liquid quality universe), 2014→:

| Name | Liquid since | Avg ADV | ROIC5Y | ROE5Y | Read |
|------|-------------|---------|--------|-------|------|
| **FPT** | 2013 (cont.) | 45→866B | 12→**17.7%** | 22→**27%** | the one genuine compounder; NPM 0.10→0.20 |
| CMG | **2024** only | <4B before | **7.8%** | 10–12% | infra/cloud capex sink; low quality, just got liquid |
| ELC | sporadic | 3–16B | 4–6% | 5–7% | project-lumpy, low quality |
| ITD | never (<5B) | 1–5B | 3–8% | 1–6% | micro-cap, negative-earnings periods |
| CTR | 2018 (~35B) | 35B | **21–24%** | **28–30%** | **only name at the global ROIC bar — but it's Viettel tower-co / telecom-INFRA** (NPM 0.04 construction margin), not software → excluded from IT book |

**There is no tech *sector* to buy in VN — there is FPT, plus a tail that is either too small, too
low-quality, or (CTR) not software.** This is the same single-name structure as telecom.

## 3. The dispatch gate problem (durable export #1)
The brief's `ROIC5Y > 18` is an **Infosys/TCS bar (25–30% ROIC)**. FPT runs a **blended 12–17%** because
**FPT Telecom (capital-heavy fiber capex) + education** dilute the pure-IT-services ROIC — FPT only
crosses 18 in **2025**. Applied literally with `RevYoY>0.12`, the gate holds **0 names across all of
2014–2026** (verified: `picks span: []`). **VN-calibrated bar = `ROIC5Y > 0.12`.**

## 4. The RevYoY artifact trap (durable export #2)
FPT's `Revenue_YoY_P0` printed **−20…−50% across 2015–2018** — purely the **FRT (FPT Retail) / Synnex-FPT
(FPT Trading) divestment deconsolidation**, not a real decline. A `RevYoY > 0.12` gate therefore wrongly
**ejects the excellent 2018 entry** (PE 8.3 / MA1Y 11.7 = 0.71, deeply cheap). **Do not gate FPT on
reported RevYoY** — it is corrupted by structural divestments.

## 5. The screen
**FPT timing lens (primary):** `PE < PE_MA1Y × 0.9` (cheap vs own 1Y) **AND** `ROIC5Y>0.12 AND
ROE5Y>0.15 AND NPM_P0 ≥ NPM_P4×0.85` (quality/margin-retention proxy for IT-services attrition). No
RevYoY gate. → forward-12M flagged vs unflagged.
**Tradeable basket (honesty check):** FPT,CMG,ELC,ITD EW, hold qualifiers / cash when none, monthly,
T+1, TC 0.1%. Two gate variants: **G_LIT** (dispatch-literal) vs **G_VN** (calibrated, no RevYoY).

## 6. Results
**FPT TIMING LENS — strong & real (131 monthly snapshots):**

| | n | avg fwd-12M | winrate |
|---|---|---|---|
| **FLAGGED** (cheap + quality) | 26 | **+50.6%** | **88%** |
| UNFLAGGED | 105 | +24.5% | 76% |
| **spread** | | **+26.0pp** | |

(FPT compounds so hard that even *unflagged* months return +24.5%; the cheap-PE lens adds **+26pp** of
entry timing on top. Adding the RevYoY gate drops 8/26 flagged months incl. the 2018 entry.)

**TRADEABLE BASKET (net vs B&H VNINDEX):**

| Variant | months held | Full CAGR | edge | IS edge | OOS edge | self-check |
|---------|-------------|-----------|------|---------|----------|------------|
| **G_LIT** (ROIC>18+RevYoY) | **0/148** | 0.0% | −10.2pp | — | — | PASS (0 VND) |
| **G_VN** (ROIC>12) | 37/148 | 2.82% | **−7.42pp** | −10.1pp | −4.78pp | PASS (1e-6) |

**The lens is strongly positive yet the book is negative** — because the +50.6% edge lives in the
**12-month HOLD**, while a monthly-rebalanced book sits in **cash 75% of months** (FPT isn't cheap) and
misses FPT's biggest compounding runs (2021 +44%, 2025 +44% market). Mono-name concentration makes it
lumpy (2022 +38.9pp, 2023 +35.6pp, but 2026 −31pp). **This is a buy-FPT-when-cheap-and-HOLD signal, not
a monthly rotation, and not a sector book.**

**Verify (all as predicted):** 2018 divestment entry CAUGHT by G_VN / MISSED by G_LIT (RevYoY<0);
2022–23 IT-slowdown entry CAUGHT; 2024 euphoria correctly ABSENT (PE rich); 2025 cheap re-entry caught.
**Orthogonality:** G_VN 32.4% vs custom30V (FPT already partly in the beta basket) | 0% vs 8L top-25.
**Liquidity:** median selected ADV 96.9B (FPT is deep — no capacity issue).

## 7. Verdict & durable exports
- **Lens, not book.** The cheap-vs-own-PE + quality entry signal on **FPT** is real and strong
  (+26pp fwd-12M, 88% win) → use as a **watchlist/entry-timing lens** for the one VN tech compounder.
  Do **not** deploy as a monthly book (mono-name, cash-drag kills the hold-edge, negative vs B&H).
- **ROIC5Y>18 is the wrong VN calibration** (FPT blended 12–17% via Telecom+education) → use **>12**.
- **Reported RevYoY is a divestment-artifact trap** for FPT → never gate on it.
- **CTR** is the only VN name at the global ROIC bar but is **telecom-infra**, not software.
- Entry windows the lens flags as cheap-and-quality: **2018 (post-divestment), 2022–23 (IT-spend
  slowdown), 2025/2026Q1 (PE 13–20 vs MA1Y 19–27)** — FPT is in such a window now.
