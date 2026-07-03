# Coding Guidelines — áp dụng cho toàn fleet

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Idempotent Side Effects

**Any script that can be killed mid-run and re-run must not repeat an external action.**

Root cause of the 2026-07-02 double-buy incident: a headless process crashed after
`broker.place_order()` succeeded but before it persisted that fact locally. The next run,
holding the lock correctly, had no way to know the order already existed and placed a
duplicate. A lock (flock/circuit-breaker) only stops two runs from overlapping — it does
nothing for one run dying mid-write. Fixed in `trading_bot/executor.py` (`_ghost_tickers` +
atomic `_save_state`, commit `e1d9b7c`); apply the same reasoning to every new script, not
just that one.

Before writing any script that calls an external system with a side effect (place an order,
send a message, write a shared file, call an API that isn't naturally idempotent):
- Ask: "if this process is killed right after the external call succeeds but before local
  state is saved, what does the next run do?" If the answer is "repeats the action," that's
  a bug, not an edge case.
- Prefer checking the external system's own source of truth (broker's live order book,
  the sent-messages log, etc.) over trusting only local state — local state can lag reality.
- When you can't tell whether an action already happened, **fail-safe pause and flag for a
  human** — do not guess-and-merge into local state, and do not silently proceed as if
  nothing happened. Guessing wrong is worse than stopping.
- Persist "the action happened" as close to the actual external call as possible (write
  immediately after, not batched at the end of a longer loop) — this shrinks the crash
  window rather than closing it, but every bit of shrinkage matters.
- Writes to shared state files must be atomic (`tmp` + `os.replace`/`os.rename`), never a
  direct overwrite — a kill mid-write must never leave a half-written file for the next run
  to trust.
