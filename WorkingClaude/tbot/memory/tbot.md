# tbot — working memory

> Own the mundane truth of "what am I doing / what's still open" here, so a fresh session (or a
> restart) can pick up without re-deriving it from chat history. Update whenever the thread of
> work changes, not just at the end of a session.

## Identity
- I am **tbot**, minhtrido's dedicated bot. Discord: `minhtrido`. OS user: `trido`.
- Distinct from Mike (`mike/` — trading-fleet coordinator). Different scope, different owner.
- Write-scope: everything stays inside `WorkingClaude/tbot/`. Writing elsewhere needs a real
  reason + minhtrido's confirmation first.

## 2026-08-04 — scaffold stood up
- Built `tbot/{kb,memory,code,projects,html}` per minhtrido's request (versioned OKF concept
  nodes, fact-status lifecycle verified/unverified/disputed/superseded/rejected, governance tools
  in `code/kb_tools/`).
- Moved `dnse_dashboard/` (built the previous session, was sitting at the `WorkingClaude/` root)
  into `tbot/projects/dnse_dashboard/` — dashboard output now writes to `tbot/html/dashboards/dnse_portfolio/`.
- Migrated the DNSE OpenAPI v2 calling guideline into `tbot/kb/concepts/dnse-openapi-v2-calling-guideline/`
  as a proper versioned concept node. The pre-existing copy in
  `mike/kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md` was left untouched
  (that's Mike's folder, not mine) — it now duplicates tbot's copy; flagged to minhtrido, not
  auto-resolved.

## 2026-08-04 — reviewed dnse-openapi-v2-calling-guideline (v1 -> v2)
- Cross-checked §2 (signing), §4 (endpoints), §8 (loanPackageId) against `dnse_api.py` AND
  DNSE's official SDK (`github.com/dnse-tech/openapi-sdk`, fetched live) — both agree.
- Found and fixed a real gap: the signing recipe was missing the URL-encoding step between
  base64-encoding the HMAC digest and putting it in the header. v2 has the corrected recipe +
  a note on why the `headers=` attribute never lists `nonce` even though nonce is signed.
- Deliberately did NOT flip the concept to `verified` — §3/§6/§7/§9/§11 are empirical
  production claims (OTP race, 3 cash fields, T+2 cutover, modify-500 quirk, multi-account
  shape) that neither the code nor the official SDK can confirm (both are thin passthrough
  wrappers, no typed response models), and DNSE's hosted docs render interactively (no
  field-level content via WebFetch). Closed the original ask-to-verify with these findings,
  opened a narrower one scoped to just those 5 sections — resolves once the dashboard runs
  against a real account, or minhtrido/another reviewer confirms by hand.

## Open / next
- Waiting on minhtrido for DNSE dashboard credentials (see `projects/dnse_dashboard/` — reuses
  `WorkingClaude/secrets/dnse_credentials.json` if that's the right account, otherwise needs a
  new key/secret) before the dashboard can run against real data instead of `--demo`.
- Once real data flows: use it to close the narrowed ask-to-verify on
  `dnse-openapi-v2-calling-guideline` (§3/§6/§7/§9/§11).
