---
name: sugar-cyclical-trend-2026
description: Sugar (SLS/SBT/LSS/KTS/QNS) is a TREND cyclical — inverts the contrarian rule that works for rubber/steel/urea/dap
metadata: 
  node_type: memory
  type: project
  originSessionId: 087259f2-b3a8-4404-b00d-c687c7268c14
---

Added SUGAR to the 8L cyclical family ([REDACTED]01, user request). Driver = world sugar price (USD/kg, Thai-export anchored), `data/sugar_monthly.csv` (240mo 2006→2026-03 via indexmundi). Group ICB 3577: **SLS, SBT, LSS, KTS, QNS** (QNS hybrid — Vinasoy ~half profit). Script `sugar_cyclical.py` → `data/sugar_cyclical.md`.

**KEY FINDING — sugar INVERTS the contrarian pattern.** For rubber/steel/urea/dap, "commodity WEAK + deep-dd" was the BEST bucket (buy trough). For sugar it's the WORST: WEAK+deep-dd 1Y **−4%/41%win**; GOOD+deep-dd 1Y **+29%/72%win**. Spread WEAK−GOOD is NEGATIVE for all 5/5 tickers (SLS −2, SBT −6, LSS −13, KTS −23, QNS −14 pp). → **Sugar = TREND/momentum cyclical: buy when sugar price GOOD (>36m median), ideally on a stock pullback (dip-in-uptrend); AVOID when WEAK.** Opposite of [[cyclical-commodity-framework-2026]].

**WHY structural:** VN sugar = structural deficit + PROTECTED (import quota + anti-dumping). Supply response is slow (cane 12-18mo; acreage destroyed in 2018-20 bust doesn't rebuild fast) → high prices PERSIST and troughs are long grinds (WEAK deep-dd = value trap, not a V-bottom). Unlike steel/rubber hog-cycle where high price kills itself.

**Protection overlay (the structural layer, like rubber deficit / DGC oil-anchor):** VN anti-dumping 47.64% on Thai sugar official Jun-2021 (5y) + 47.64% anti-circumvention on 5 ASEAN re-routers Aug-2022. Decoupled domestic price UP 2022-24 → drove SLS boom (NP peak Q2/23 224bn, Q2/24 235bn, ROE_tr 54%) alongside world deficit (India export ban, sugar 0.58 peak 9/2023).

**CURRENT STATE 2026-06 = triple bearish:** (1) world sugar WEAK 0.33, pctile5y **0.08** (near 5y low, off 0.58 peak); (2) SLS Q1/26 NP collapsed to 16bn / ROE_tr 16.7% (downcycle); (3) **AD duty EXPIRES 15-Jun-2026** — MOIT end-of-term review Decision 1686/QD-BCT (13-Jun-2025) pending: extend=floor holds, revoke=Thai sugar floods→domestic price pressure. Framework verdict = **WAIT** (not contrarian-buy); wait for sugar regime flip GOOD + AD review outcome.

**Integration caveat:** do NOT drop sugar into `unified_screener.py` COMMODITY_MAP — its `eval_cyclical()` uses contrarian logic (pctile<0.40+deep=TROUGH_BUY) which is INVERTED-WRONG for sugar. Needs a separate trend-cyclical branch. Data gap: domestic VN sugar price monthly (world price + protection premium − smuggling) — world price used as proxy.
