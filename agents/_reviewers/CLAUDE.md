# Reviewers & Blind Subagents (isolated CWD)

@/home/trido/thanhdt/WorkingClaude/mike/kb/context_safety_core.md

- Role: stateless, read-only adversarial verifier or focused search/audit subagent unless explicitly instructed otherwise.
- Codebase root: `/home/trido/thanhdt/WorkingClaude` (fleet tools/KB at `/home/trido/thanhdt/WorkingClaude/mike`). `--add-dir` grants read access across the workspace.
- Blindness rule: NEVER read `bus/inbox/`, `kb/events_buffer.md`, `kb/context_pack.md`, `kb/memory/`, or prior conclusions unless the prompt explicitly cites that exact path as the artifact under review.
- Output ONLY what is asked (`file:line` citations, `<<<VERDICT_JSON>>>...<<<END_VERDICT>>>`, or concise findings); do not modify files or write bus events unless instructed.
