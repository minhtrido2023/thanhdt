---
name: feedback-accounting-restructure-override
description: "When FA model flags a stock as WATCH/B-tier due to YoY revenue decline, check news for accounting restructure (subsidiary→associate, M&A divestiture, segment carve-out) before treating as fundamental damage. The FA model uses raw Revenue_YoY_P0 from BQ and cannot distinguish accounting from real decline."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6a525d72-2310-410b-91ab-1e5ab95cbfeb
---

# Always check restructuring news before trusting FA tier downgrade

**Rule**: When `fa_ratings` model drops a Tier 1 / whitelist stock from A → B/C due primarily to **Revenue_YoY_P0 turning negative**, verify the cause before applying exit triggers. If the YoY drop is from accounting restructure (deconsolidation, divestiture, equity-method switch, segment carve-out), treat as **qualitative override** — keep Tier 1 status, do not trigger sell.

**Why**: `tav2_bq.ticker_financial` reports consolidated revenue per the issuer's current accounting basis. When a subsidiary moves to equity method (e.g. FPT/FTel 2026-01-01) or is divested, consolidated revenue drops sharply YoY purely from accounting — NP attributable to parent shareholders and EPS are unaffected. The FA model penalizes valuation/growth axes blindly → false negative for 4 quarterly reports until the new basis becomes the YoY baseline. See [[fpt-ftel-deconsolidation-2026]] for the canonical case.

**How to apply**:
1. When a whitelist or Tier 1 name drops A → B (or B → C) in `fa_ratings`, run a quick news search for: ticker name + "thoái vốn / chuyển giao / hợp nhất / equity method / spin-off / divestiture / restructure" + year.
2. Cross-check: did the **NP attributable to parent shareholders** also drop sharply, or only revenue? If only revenue → likely accounting.
3. Compare segment-level revenue if disclosed (core business growth excluding the restructured unit).
4. If restructuring confirmed: keep whitelist status, document override in a project memory with the date the FA tier should auto-restore (typically ~12 months from accounting change).
5. If no restructuring news found → trust the model, apply normal exit rules.

**Don't blindly trust user claims either** — verify with WebSearch when user says "it's just accounting." User in this codebase was correct on FPT/FTel (2026-05-20 conversation), but verify each case independently.

**Related**:
- [[fpt-ftel-deconsolidation-2026]] — concrete instance, FPT 2026
- [[long_hold_whitelist]] — Tier 1 whitelist exit rules that this override modifies
- [[fa_v8c_final_spec]] — FA scoring spec that produces the false negative
