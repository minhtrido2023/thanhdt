---
name: tbot-scaffold
description: "tbot's dedicated folder (WorkingClaude/tbot/) — versioned OKF KB with fact-status lifecycle, shared code, dashboards"
metadata: 
  node_type: memory
  type: project
  originSessionId: a784d880-5a9e-4603-b19e-20d46f573eff
  modified: [REDACTED]03T16:39:37.192Z
---

Built [REDACTED] at minhtrido's request: multiple bots share `WorkingClaude/`, and there was no
dedicated, well-governed place for tbot's own KB/memory/code/HTML — everything was landing ad hoc
(a DNSE dashboard project sitting loose at the repo root, a KB entry written into Mike's fleet
folder instead of tbot's own).

**Why:** minhtrido wanted (1) a solid scaffold, (2) OKF (md+yaml) concept storage, (3) versioned
concept nodes with explicit change-edges + aliases/related for querying, (4) a real fact-status
lifecycle (verified/unverified/disputed/superseded/rejected) with governance processes
(ask-to-verify, conflict review, contradiction sweep) so verified facts never get silently
confused with unverified ones, (5) portable/reviewable code organization, (6) a dedicated HTML
publish folder separate from KB/code.

**How to apply:** the full design is documented in `WorkingClaude/tbot/README.md` — read that
before touching anything under `tbot/`, don't re-derive the layout from memory. Governance tools
live at `tbot/code/kb_tools/*.py` (kb_new_concept, kb_new_version, kb_verify, kb_ask_to_verify,
kb_dispute, kb_resolve_conflict, kb_reindex, kb_lint, kb_contradiction_sweep) with a passing
end-to-end selfcheck at `tbot/code/tests/selfcheck.py`. First real concept node migrated in:
`tbot/kb/concepts/dnse-openapi-v2-calling-guideline/` (status `unverified` — imported from a
proven [REDACTED] reference, not yet independently re-confirmed within tbot's own governance;
see the open ask-to-verify request under `tbot/kb/process/ask_to_verify/`).

See [[tbot-identity]] for the write-scope rule, [[dnse-portfolio-dashboard]] for the project that
now lives at `tbot/projects/dnse_dashboard/`.
