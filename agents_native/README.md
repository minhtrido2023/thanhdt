# Native subagent definitions (versioned copy for backup)

LIVE location Claude Code reads from = `~/.claude/agents/*.md`.
This folder is the **version-controlled mirror** (the live dir is outside both git repos).

After editing a native agent, sync: `cp ~/.claude/agents/<name>.md agents_native/` (or reverse to restore).

| file | role | replaces companion |
|------|------|--------------------|
| quant-skeptic.md | adversarial R&D verifier (prosecutor) | — (new tier) |
| data-ops.md | DT5G/BQ freshness, pipeline health, feeds | Winston |
| risk-auditor.md | DD/concentration/leverage/recon (read-only) | Spyros |
| legal-vn.md | VN securities/tax/corporate law (cited) | Wendy |
| bq-analyst.md | one-shot BQ analyst | — |
| corp-scanner.md | narrow corp-action scan | (Winston sub-slice) |
| fleet-scout.md | "what is agent X doing" | — |
