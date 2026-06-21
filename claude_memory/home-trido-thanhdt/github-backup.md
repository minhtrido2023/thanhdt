---
name: github-backup
description: "How the thanhdt repo is backed up to GitHub (backup.sh, structure, secret scrubbing)"
metadata: 
  node_type: memory
  type: project
  originSessionId: fef38ec9-be6a-47e0-ac13-1222be8cba59
---

`/home/trido/thanhdt` is backed up to private repo **github.com/minhtrido2023/thanhdt** (branch `main`). Auth = repo-scoped fine-grained PAT cached in `~/.git-credentials` (chmod 600); shared OS account `trido`, so token is intentionally scoped to only this repo.

**One-command backup:** `./backup.sh ["msg"]` — runs `tools/sync_claude_history.py`, a secret gate, then `git add/commit/push`. Aborts if a secret pattern is detected.

**Repo layout (what is / isn't tracked):**
- Tracked: code, docs, `CLAUDE.md`, `.claude/` skills, `data/*.md` reports + `data/*.py` helpers.
- Gitignored: `WorkingClaude/data/` bulk (csv/pkl/xlsx/logs — regenerable from BigQuery), `WorkingClaude/secrets/` (all credentials), `wc_venv/`, `gcloud_dtienthanh/`.
- `claude_memory/<project>/` and `claude_sessions/<project>/*.jsonl` = SCRUBBED Claude Code memory + transcripts (100 sessions). `*.jsonl` is globally ignored except these (negation `!claude_sessions/**/*.jsonl`).

**Secret scrubbing** (`tools/sync_claude_history.py`): redacts every string value from credential JSON under WorkingClaude + 8–16 char prefixes, PEM key blocks, telegram tokens, and strips base64 runs ≥64 (images/keys). Memory notes are scrubbed too (one had recorded the PHS CLIENT_ID). Caveat: a rotated/old credential no longer in `secrets/` is only caught by pattern, not by value.

See [[repo-structure-goal]] and [[poc-not-live]].
