# KB process records

- `ask_to_verify/<id>.md` — open/closed verification requests (`kb_ask_to_verify.py` /
  `kb_verify.py`).
- `conflict_review/<id>.md` — open/closed contradiction reviews (`kb_dispute.py` /
  `kb_resolve_conflict.py`).
- `contradiction_sweeps/<date>.md` — dated reports from `kb_contradiction_sweep.py`. A report,
  not a gate — it surfaces candidates for `conflict_review/`, never auto-resolves anything.
