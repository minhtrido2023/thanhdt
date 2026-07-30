---
kind: open-items
date: 2026-07-10
topic: open-not-yet-hardened
title: >-
  Open / not-yet-hardened
status: open
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031) — vị trí gốc: giữa entry 2026-07-10 (đêm) và 2026-07-10 (sáng sớm)
---

# Open / not-yet-hardened

- **quant-skeptic's second recommendation on the ghost-order guard** (2026-07-02,
  `is_dead` heuristic in `brokers.py:126` matches single characters `f`/`x` inside a
  status string, which is broad) — not yet tightened to an explicit DNSE status
  allowlist. Low urgency: a false-negative there only means a genuinely-dead order is
  treated as a live ghost (extra caution, fails safe), not the reverse.

- **No official "unpause" for a ghosted ticker** (raised by an independent third-party
  review, 2026-07-02, after verifying the guard mechanism against real DNSE data —
  6,338 orders in `dnse_raw_2026-07-02.jsonl`, confirmed `poll_orders()` returns the
  full daily book, `symbol` field maps correctly, oid types are consistently `str`). A
  ticker that trips the ghost guard stays paused for the rest of the session until a
  human manually reconciles the untracked oid into `state["parents"][id]["children"]`
  (cross-check against `dnse_raw_<date>.jsonl` or a direct `poll_orders()` call). This
  is accepted-by-design (human-in-the-loop, no auto-reconcile — see the field-mapping
  risk noted in the double-buy entry above) but now has an explicit runbook note in
  `_ghost_tickers()`'s docstring so an operator isn't left guessing. **Fixed same
  review round:** (a) `_save_state()` was a direct overwrite, not atomic — now
  tmp-file + `os.replace()`, since it runs far more often post-idempotency-fix (after
  every `place_order`, not once per cycle) so a kill-mid-write is more likely to be
  hit; (b) `PaperBroker.poll_orders()` built `OrderUpdate` with `raw=None`, so the
  guard could never resolve a symbol in paper mode and paper trading could never
  rehearse it — now passes `raw={"symbol": ...}` matching the real broker's shape.
