---
name: dnse-portfolio-dashboard
description: "New initiative — DNSE portfolio management dashboard (balances/positions/orders/NAV/quotes), separate from the live trading bot"
metadata: 
  node_type: memory
  type: project
  originSessionId: a784d880-5a9e-4603-b19e-20d46f573eff
  modified: [REDACTED]03T16:39:56.129Z
---

This is **tbot's** project (see [[tbot-identity]], [[tbot-scaffold]]) — read-only DNSE dashboard
(balances, positions, orders, NAV, quotes), distinct from Mike fleet's live `trading_bot`
execution system (see [[mike-fleet]], [[poc-not-live]]).

**Why:** dashboard-only use case doesn't need order placement, so it can skip the trading-token/
OTP flow entirely and avoid that whole class of incident (OTP races between sub-accounts sharing
one DNSE login).

**How to apply:** code lives at `WorkingClaude/tbot/projects/dnse_dashboard/build_dashboard.py`
(moved [REDACTED] from a loose `WorkingClaude/dnse_dashboard/` — everything tbot owns now lives
under `tbot/`, per the write-scope rule). Output HTML goes to
`WorkingClaude/tbot/html/dashboards/dnse_portfolio/` (gitignored — holds real financial data).
`--demo` mode works today with synthetic data; real use needs DNSE credentials (see the script's
`--creds`/`--account` args) — still [REDACTED] on minhtrido for which account(s) to point it at.

The calling guideline for DNSE OpenAPI v2 (signing, endpoints, gotchas) is now a proper versioned
KB concept at `WorkingClaude/tbot/kb/concepts/dnse-openapi-v2-calling-guideline/` (status
`unverified` — imported from Mike fleet's [REDACTED]-tested copy, not yet independently
reconfirmed within tbot's own governance). Key gotchas to reuse: three different "cash" fields
(`availableCash` vs `totalCash` vs `ppse`'s `pp0Buy`) answer three different questions and must be
labeled separately; positions need `total` vs `sellable` shown distinctly; T+2 settlement flips
mid-afternoon, not at market open; pick the `G1` board explicitly when reading quotes.
