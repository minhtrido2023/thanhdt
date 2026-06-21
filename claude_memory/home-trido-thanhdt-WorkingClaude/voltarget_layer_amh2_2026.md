---
name: voltarget_layer_amh2_2026
description: Vol-target sizing layer (AMH
metadata: 
  node_type: memory
  type: project
  originSessionId: c20741c2-d11c-4052-813a-f3c503120558
---

**AMH proposal #2 — Vol-Target Sizing Layer.** Tested `w_final = w_state × clip(vol_target/realized_vol, 0, cap)` as an overlay on the DT5G VNINDEX 5-state allocation sim (Kelly money-metric, faithful T+1/3-session-ramp/TC=0.1%). Script `voltarget_overlay.py`; data `data/dt5g_vnindex.csv` (DT5G `vnindex_5state_dt5g_live` state JOIN VNINDEX close, 2014→2026, 3097 sessions). Outputs `data/voltarget_results.csv`, `voltarget_overlay.png`.

⚠️ **BQ DT5G state codes are 1–5 NOT 0–4**: 1=CRISIS(0%), 2=BEAR(20%), 3=NEUTRAL(70%), 4=BULL(100%), 5=EX-BULL(130%). (Verified: 2020-03 COVID & 2022-10 bear = state 1/2.) STATE_W = {1:0.0,2:0.2,3:0.7,4:1.0,5:1.3}.

**VERDICT: do NOT deploy vol-target as a cash-stack overlay — it is REDUNDANT with DT5G.** Quantified (full 2014-26):
- BASE DT5G: CAGR 12.15% / Sharpe **0.99** / Calmar **0.66** / MaxDD −18.3%.
- Best vol-target (EWMA vt=0.18 valve): Sharpe 0.94 / Calmar 0.58 — strictly DOMINATED. Every valve/2-side variant Sharpe 0.89–0.94 < 0.99, Calmar < 0.66.
- **Mechanism = the F-system "cùng cò súng" redundancy again**: realized vol and DT5G state are the SAME environmental signal. corr(state,rv)=−0.16; CRISIS/BEAR rv 0.18–0.24 vs NEUTRAL/BULL 0.12–0.14 → DT5G already down-weights high-vol periods. Vol-target shaves the same periods twice → cuts return without proportional risk cut.
- **Even levered (L=2x futures-like): still redundant on risk-adj** — BASE_L2 Calmar 0.69 vs +valve 0.58. On futures its justification is risk-of-RUIN (bounding notional when a vol spike outruns DT5G's slow enC=25 commit / margin survival) = an AMH SURVIVAL argument, NOT Sharpe/Calmar. Trades return for survival. Consistent with [[vn30f_data_fsystem_revalidation_2026]] "van vol-target BẮT BUỘC cho futures."
- **The V5 grind drawdown (9/2025–3/2026) — the case we hoped vol-target would catch — it CANNOT**: VNINDEX was FLAT (−0.4%) with only moderately elevated vol (19.9%); the bleed was STYLE divergence (8L picks vs flat VN30, per [[f_system_protect_v4v5_2026]]), not beta/index drawdown. Vol-target (index) is the wrong instrument; needs an independent **drawdown-stop on the book**, not a vol valve.

**AMH biodiversity lesson**: vol-target and DT5G-state are the same "species" (both fire on volatility/stress) → stacking gives zero diversification. The genuinely orthogonal book-protector is a drawdown-stop / fast independent trigger (NOT vol-target). Feeds #5 biodiversity test + the book-side protection question from f_system memo.

AMH roadmap: #1 Edge Health Monitor ✅ (per-sector+daily ✅) → **#2 Vol-target ✅ (negative/scoping result — not deployed)** → #3 Fitness Matrix (5-state × strategy) → #4 Ecology Dashboard → #5 Biodiversity test.
