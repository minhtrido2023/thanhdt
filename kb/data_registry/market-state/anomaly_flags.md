---
kind: local-file
status: CANONICAL
source: data/anomaly_flags.json
group: market-state
role: money-path gián tiếp (CAPIT candidate gate)
writer: mike/agents/Taylor/anomaly_scan.py, chạy trong ops_health_check.sh 08:20 + 12:45 ICT (T2-T6, chỉ lượt account đầu)
selfcheck: agents/Taylor/capit_dd_gate_selfcheck.py
---

# data/anomaly_flags.json

**Status: CANONICAL**

## Là gì
Cờ due-diligence per-ticker (`last_alert`, `tier` H/W, `reasons`) — bất thường giá/khối lượng
(VOLSPIKE/IDIOCRASH/FLOOR2).

## Ai ghi / cadence
`mike/agents/Taylor/anomaly_scan.py`, chạy trong `ops_health_check.sh` 08:20 + 12:45 ICT (T2-T6,
chỉ lượt account đầu).

## Bẫy
**Money-path gián tiếp**: `golive_recommend_v23.py:anomaly_excluded()` đọc file này để loại ticker
khỏi rổ ứng viên CAPIT (cờ hiệu lực `ANOMALY_TTL_DAYS=30` kể từ `last_alert`). Cửa sổ HAI ĐẦU
`cutoff <= last_alert <= asof` — chặn trên chống look-ahead khi rerun ngày quá khứ. Fail-safe: file
thiếu/JSON hỏng/rỗng → gate TẮT (set rỗng) + WARNING, KHÔNG chặn pipeline → **file này chết âm thầm
= CAPIT mất gate**, kiểm mtime nếu nghi ngờ. Selfcheck: `agents/Taylor/capit_dd_gate_selfcheck.py`.
