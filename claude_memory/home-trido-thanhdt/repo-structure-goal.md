---
name: repo-structure-goal
description: User wants a clean repo structure — data/ and secrets/ separated from code+docs
metadata: 
  node_type: memory
  type: project
  originSessionId: fef38ec9-be6a-47e0-ac13-1222be8cba59
---

User is backing up `/home/trido/thanhdt` to a **private** GitHub repo (`github.com/minhtrido2023/thanhdt`) so work can resume when the server is off. Goal structure:

- **code + docs + context** → committed to git
- **data** (csv/pkl/xlsx, regenerable from BigQuery) → `data/` folder, gitignored
- **secrets** (credentials/tokens/accounts, sa-key.json, gcp_credentials.json, telegram_config.json, phs_secret.json, dnse/phs creds) → `secrets/` folder, gitignored

**Why:** user explicitly wants the folder "cleaned completely", not just gitignored — physical reorg into data/ + secrets/.

**How to apply:** keep secrets and large data OUT of git; the repo is code/docs only. Server is shared (OS account `trido`) so credentials use a repo-scoped fine-grained PAT. The reorg is DONE (data→`data/`, secrets→`secrets/`, 1721 path refs rewritten). See [[poc-not-live]] and [[github-backup]] for the live backup workflow.
