# Deposit-rate auto-crosscheck automation (2026-07-20)

**Status: DONE — quant-skeptic CONFIRMED after 10 rounds of adversarial review.**

## What changed

User asked to fully automate the monthly Big-4 12-month deposit-rate confirmation
(`refresh_deposit_rate_vn.sh`, feeds `rating_8l.py`'s NEUTRAL-only deposit tilt), removing the
human-confirmation step that had existed since 2026-07-17 — "để bạn tự động cập nhật thông tin mà
không phụ thuộc tôi".

`refresh_deposit_rate_vn.sh` now dispatches Winston monthly to WebSearch-crosscheck the Big-4 rate
and write via a new `append_deposit_rate.py --source web_crosscheck_auto` path, instead of only
reminding a human. If evidence is ambiguous/conflicting/insufficient, Winston escalates (bus
`question`, Discord notify) rather than guessing — verified working for real: one live run hit a
genuine Vietcombank rate conflict (5.9% vs 6.8% across sources) and correctly escalated without
writing anything.

## Why 10 rounds

Every round of `quant-skeptic` adversarial review found a **real, previously-unnoticed, distinct**
bug — never a repeat of a prior round — so each round was re-run rather than stopped early. The
core lesson, restated because it generalizes: **a prompt instruction is not a security/safety
boundary.** Every backstop that mattered ended up keyed on the caller's actual identity
(`JOB_ID` env var, which `dispatch.sh` exports into every headless agent's environment) or on a
mechanical check of the data itself — never on a self-declared CLI flag or string the agent
controls, because an agent (even a fully cooperative one, not malicious) can always be induced
to pass a different flag if the only thing stopping it is prose telling it not to.

| Round | Found | Fix |
|---|---|---|
| 1 | No deterministic backstop on the number itself; echo-chamber risk in the evidence bar | Added a delta guard (refuse ≥1.0pp move) + flagged the "1 article, 4 banks" evidence rule as N=1 |
| 2 | Guard keyed on `--source` string (agent-controlled) → wrote 12.00% using `--force` | Bound `--force` to `JOB_ID` presence, not `--source` |
| 3 | `--force` was bound to caller identity but `--source` itself wasn't → agent used `--source manual_verify` with zero evidence, wrote 12.00% again | Bound the **source choice itself** to `JOB_ID`: a dispatched agent may ONLY use `web_crosscheck_auto` |
| 4 | Owner-group domain check used `.netloc` (port/userinfo survive) + naive subdomain merge (all `.com.vn` collapsed into one group, wrongly both merging real sister sites AND blocking genuinely independent outlets) | Switched to `.hostname`, added a VN multi-label-suffix-aware registrable-domain helper |
| 5 | Percent-encoded / non-ASCII hosts still bypassed the domain check | Reject percent-escapes and non-ASCII hosts outright. **Also**: explicitly scoped the threat model in the docstring — this defends against *careless* citation by a cooperative agent, not a maliciously adversarial caller inventing fake domains (structurally unstoppable by string checks, disproportionate to fix here) |
| 6 | `date` field in `--sources` was required by schema/prompt but never validated (stale evergreen sources would pass); delta guard only checked the *most recent* value, not cumulative drift since the last human confirmation | Mechanically enforce source recency (≤35 days); delta guard now also checks against the last human-sourced anchor |
| 7 | Recency check anchored to `--collected` (agent-controlled), so a falsified `--collected` revived the stale-source exploit | Anchor recency to the real system clock (`date.today()`); bind `--collected` itself to `JOB_ID` (agent gets no say over it at all) |
| 8 | **`deposit_rate_vn.current_deposit_rate(asof=None)`** (the actual production consumer, called by `rating_8l.py`) returned the last row *by time*, not "as of today" — a typo'd/future `--effective` date would permanently pin or pre-empt the live series | Fixed the consumer function itself (protects against this regardless of how a bad row entered the CSV, not just this one writer); added a writer-side `--effective` window bound for defense-in-depth |
| 9 (confirmed, 1 disclosed item) | Writer-side `--effective` bound was symmetric (±35d), so a +35d future typo still slipped through | Made it asymmetric: 35d backward, 2d forward (an agent confirms *today's* rate, never a future-effective one) |
| 10 (confirmed) | — | — |

## Final design

- **Caller-identity gates** (keyed on `JOB_ID` presence, `is not None` not truthy — an empty-but-set
  `JOB_ID=""` still counts): a dispatched agent may only use `--source web_crosscheck_auto`, never
  gets `--force`, never gets to set its own `--collected`, and `--effective` is bounded to
  [-35, +2] days from the real clock.
- **Mechanical evidence check**: `--sources` (JSON array of `{publisher,url,date}`) must resolve to
  ≥2 distinct owner groups (`SAME_OWNER_GROUPS` — seeded with VCCorp's cluster:
  cafef.vn/cafebiz.vn/kenh14.vn/soha.vn/genk.vn/gamek.vn/afamily.vn/ttvn.vn/autopro.com.vn/sport5.vn,
  extend as new collisions are discovered) and each source's `date` must be within 35 days of today.
- **Delta guard**: any write ≥1.0pp from *either* `current_deposit_rate()` *or* the last
  human-sourced anchor is refused without `--force` (which an agent can never pass).
- **Post-condition check** (`refresh_deposit_rate_vn.sh`): after dispatch, greps
  `mike/bus/inbox/Winston.jsonl` for a `deposit-rate-refresh-done` (status) or
  `deposit-rate-refresh-question` (question) event timestamped after the run started. Neither found
  → falls back to the old plain-reminder notify, so a silent no-op agent run or an infra failure
  never means a skipped month. `rc=5` (usage-limit-queued, self-resuming) is explicitly carved out
  of this fallback.

## Explicit scope (read before extending this mechanism)

This defends against a **cooperative agent making an honest mistake** (citing sister sites without
realizing it, citing a stale page, a typo). It does **not** defend against a **maliciously
adversarial caller** fabricating evidence from scratch — round 5 established that's a different,
structurally-unstoppable-by-string-checks threat model, disproportionate to build for a monthly,
NEUTRAL-tilt-only input running inside the same trusted fleet. Don't chase further string-encoding
tricks in the name of that threat model; do fix anything that's a realistic *honest* failure mode.

## Known residual (disclosed by round 10, not fixed — low priority, fails safe)

`--collected` requires exact equality with `date.today()` when `JOB_ID` is set. The dispatch shell
script bakes in an ICT date while the Python check uses UTC `date.today()` (server TZ=Etc/UTC) — in
the ~17:00-24:00 UTC window (00:00-07:00 ICT) these can differ by a day, which would spuriously
refuse a legitimate auto-resumed run. This fails **closed to escalation** (worst case: an
unnecessary manual reminder gets sent), never to bad data, so it was left as-is rather than adding
another special case. Revisit only if it's observed to actually fire in production.

## Verification

10 real end-to-end dispatches run live during this session (not simulated) — including one that hit
a genuine data conflict (Vietcombank) and correctly escalated, and the rest correctly SKIPping
(idempotent, no rate change all month). Every guard was also unit-tested directly via the CLI
against a backed-up-then-restored copy of the real `data/deposit_rate_vn_events.csv` (left
byte-identical after every test run). quant-skeptic verdict: CONFIRMED (verify_20260720_060605.log).
