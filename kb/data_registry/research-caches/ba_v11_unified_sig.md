---
kind: local-file
status: RESEARCH
source: data/ba_v11_unified_12y_sig.pkl
group: research-caches
note: rebuilt 2026-07-11 trên DT5G, max 2026-07-10
builder: build_pkl_v11_current.py (rebuild DT5G: mike/agents/Taylor/momdeal/rebuild_pkl_dt5g.py)
---

# data/ba_v11_unified_12y_sig.pkl

**Status: Research cache — rebuilt 2026-07-11 trên DT5G, max 2026-07-10**

## Là gì
Signal cache BAL/V11 cho ~90 script sim/tune.

## Ai ghi / cadence
Rebuild tay khi cần. **Builder thật = `build_pkl_v11_current.py`** (dòng cũ ghi nhầm
`build_state_free_signals.py` — script đó build bản state-FREE `ba_v11_state_free_sig.pkl` khác, chỉ
ĐỌC pkl unified làm đối chứng; sửa 2026-07-11, job Taylor_20260711_165407). Bản rebuild DT5G:
`mike/agents/Taylor/momdeal/rebuild_pkl_dt5g.py`.

## Bẫy
Production KHÔNG đọc file này (pt_v22/golive query BQ trực tiếp). ⚠️ Bản TRƯỚC 07-11 built trên bảng
BASE (pre-F3) — state5/play_type bên trong là base, không phải DT5G; bản hiện tại đã verify 1.085/1.085
ngày divergent khớp `dt5g_live`. Backup bản base: `.bak_predt5g_20260711`. Sim đối chiếu kết quả cũ
(trước 07-11) phải nhớ pkl đã ĐỔI cả state-source lẫn end-date.
