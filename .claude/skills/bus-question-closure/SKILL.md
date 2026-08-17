---
name: bus-question-closure
description: Close and re-escalate fleet bus questions without duplicate or false pending alerts. Use whenever work, a user decision, or an artifact resolves a bus question; when the resolution happened under another Discord or bus topic; before raising an issue that may already have been fixed; or when editing a checker, cron, dispatch prompt, or audit that decides whether a question is still open.
---

# Bus Question Closure

Treat the question's canonical `Agent/topic` reference as its identity. Conversation topics,
finding titles, and commit messages are evidence locations, not identity.

## Required workflow

1. Run `python3 mike/bin/bus_question_audit.py --json` before calling an issue pending.
2. Check the artifact named by the question. Bus state alone cannot prove a live regression.
3. If resolved, immediately run:

   ```bash
   python3 mike/bin/close_bus_question.py 'Agent/original-topic' \
     --resolution '<what is now true>' --evidence '<commit/file/log/read-back>' \
     --source-topic '<different topic where it was resolved>'
   ```

4. Add `--decided-by-user` only for a real user decision. Never infer it.
5. Accept closure only when the helper prints `CLOSED` or `ALREADY_CLOSED_OR_UNKNOWN` after the
   canonical audit confirms the item is absent. Do not post a second hand-built resolver.
6. Re-escalate only with new artifact evidence dated after the prior closure. State explicitly
   that this is a regression/new instance, not the old unresolved question.

For an answer or decision that must keep its own topic, include
`"resolves":["Agent/original-topic"]` in the payload. The daily and weekly canonical matchers
understand this explicit link; free-text similarity never closes a question.

Do not use a `finding`, a renamed answer topic, a Discord reply, or a commit alone as closure.
Those can prove the fix, but the canonical resolver must still be written.
