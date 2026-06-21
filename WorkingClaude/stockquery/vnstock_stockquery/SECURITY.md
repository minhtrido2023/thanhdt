# Security and Risk Gates

`vnstock` is not a payments or auth-heavy system, but it still has meaningful risk areas because it touches external services, headers, proxies, package distribution, and financial-data expectations.

## Mandatory human review

Require explicit review for any change involving:

- auth, tokens, API-key handling, or secret storage
- proxy behavior, browser fingerprinting, or anti-bot workarounds
- request headers that change identity, authorization, or origin behavior
- dependency additions that expand network or system access
- GitHub Actions, release, or packaging changes
- destructive cleanup of public APIs or compatibility shims

## Default secure posture

- Treat external input and remote responses as untrusted.
- Keep secrets out of logs, docs, fixtures, and examples.
- Prefer explicit opt-in for risky network behavior.
- Fail clearly when authorization or provider support is missing.
- Do not present convenience data as investment advice or guaranteed truth.

## Repository-specific risk notes

- `vnstock/core/utils/auth.py` is currently placeholder/no-op behavior. Do not quietly reintroduce real auth semantics without approval.
- `vnstock/core/utils/user_agent.py` affects how the library identifies itself to remote systems; changes here can alter reliability and legal/operational posture.
- Providers under `vnstock/explorer/` may depend on scraping or browser-like requests and can break when upstream sites change.
- CI workflows may use secrets such as `VNSTOCK_API_KEY`; changes touching those paths deserve extra caution.

## What agents should do when unsure

If the task touches a risky area and repository docs do not make the intended behavior explicit, stop and ask for approval before implementing.

## Security review prompts

When reviewing a risky change, ask:

- Does this introduce or widen a trust boundary?
- Could malformed or hostile remote data break parsing or leak data?
- Does this change log, expose, or persist secrets?
- Does it change how the library identifies itself to external services?
- Is rollback safe if the provider or workflow breaks unexpectedly?
