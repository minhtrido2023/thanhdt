---
id: 20260803-163855-dnse-openapi-v2-calling-guideline
concept: dnse-openapi-v2-calling-guideline
requested_by: tbot
requested_at: '2026-08-03'
status: resolved
resolved_by: tbot
resolved_at: '2026-08-03'
---

Content was compiled and battle-tested in production by the Mike fleet (real incidents cited inline: 2026-07-08 OTP race, 2026-07-07 availableCash-vs-pp0Buy incident, T+2 settlement verified by hand). Marked unverified here only because tbot's own governance hasn't independently re-confirmed it — recommend minhtrido (or a review pass against DNSE's current docs) flips this to verified once spot-checked, rather than trusting the import blindly.


Resolution: Partial review done 2026-08-04 (see v2 CHANGELOG). Signing recipe (§2), endpoint list (§4), and loanPackageId requirement (§8) cross-checked against dnse_api.py + DNSE's official SDK (github.com/dnse-tech/openapi-sdk) — one real gap found & fixed (missing URL-encoding step). Concept kept status=unverified overall: §3/§6/§7/§9/§11 (OTP race, 3 cash fields, T+2 cutover, modify-500 quirk, multi-account contamination) are empirical production claims that can't be checked against code or the official SDK (both are thin wrappers, no typed response models) and DNSE's hosted docs render interactively (no field-level content via fetch). Opening a narrower ask-to-verify for just those.
