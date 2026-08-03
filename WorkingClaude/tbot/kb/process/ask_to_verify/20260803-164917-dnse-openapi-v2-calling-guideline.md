---
id: 20260803-164917-dnse-openapi-v2-calling-guideline
concept: dnse-openapi-v2-calling-guideline
requested_by: tbot
requested_at: '2026-08-03'
status: open
resolved_by: null
resolved_at: null
---

Narrowed scope after 2026-08-04 review (see CHANGELOG v2 and the closed request above). §1/§2/§4/§8 are now code+official-SDK confirmed — no longer in question. What's still open: §3 (OTP race incident), §6 (three cash fields' exact names/behavior), §7 (T+2 afternoon cutover timing), §9 (modify_order HTTP 500-on-success quirk), §11 (multi-account response shape). These are empirical/production claims inherited from the source doc, not independently confirmed by tbot. Resolves once either (a) the DNSE dashboard project (tbot/projects/dnse_dashboard/) runs against a real account and each claim is observed directly, or (b) minhtrido or another reviewer with production DNSE experience confirms them by hand.
