# Product Sense

This repository is a library first. Product decisions should optimize for a reliable developer experience, not for flashy one-off implementations.

## Core principles

- Keep the library approachable for beginners without hiding important behavior from advanced users.
- Preserve a stable, predictable public API whenever possible.
- Prefer explicit names and discoverable methods over clever abstraction.
- Keep Vietnamese users first-class while maintaining usable English-facing code and docs where practical.
- Treat data access as a convenience and research aid, not as a promise of trading-grade correctness.

## User experience rules

- Public entrypoints should stay easy to import and easy to reason about.
- Default behavior should be conservative and unsurprising.
- Error messages should help users identify source, symbol, or parameter problems quickly.
- If a provider has source-specific limitations, surface them clearly instead of silently guessing.
- Do not introduce workflow bureaucracy for contributors unless it clearly reduces risk or repeated confusion.

## Compatibility bias

- Backward compatibility matters because this is a library used in notebooks, scripts, and automation.
- Renames, signature changes, and changed defaults require explicit justification and documentation.
- When possible, add compatibility shims before removing older behavior.

## Documentation bias

- Keep end-user docs focused on usage.
- Keep agent and contributor docs focused on architecture, validation, and risk boundaries.
- Link existing docs instead of duplicating long explanations in multiple places.

## Non-goals

- This repo does not need a heavyweight enterprise process.
- It should not optimize for autonomous shipping without human review of risky changes.
- It should not imply investment advice, guaranteed data quality, or execution safety for live trading.
