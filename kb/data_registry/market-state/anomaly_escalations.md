---
kind: local-file
status: DERIVED
source: data/anomaly_escalations.json
group: market-state
role: idempotency ledger
writer: mike/bin/anomaly_escalate.py
---

# data/anomaly_escalations.json

**Status: DERIVED (ledger)**

## Là gì
Sổ chống escalate trùng tier-H (08:20 vs 12:45 cùng 1 trip).

## Ai ghi / cadence
`mike/bin/anomaly_escalate.py`.

## Bẫy
Idempotency ledger — xoá file = escalate lại từ đầu (dispatch trùng Wendy/Spyros).
