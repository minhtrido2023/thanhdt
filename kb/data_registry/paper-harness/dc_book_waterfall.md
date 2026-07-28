---
kind: local-file
status: CANONICAL
source: data/dc_book_waterfall_paper_state.json
group: paper-harness
writer: dc_book_waterfall_paper.py --update, cron 15:05 ICT
---

# data/dc_book_waterfall_paper_state.json

**Status: CANONICAL (paper sleeve)**

## Là gì
State DC-book NEUTRAL idle-cash waterfall (paper, review event-anchored).

## Ai ghi / cadence
`dc_book_waterfall_paper.py --update`, cron 15:05 ICT.

## Bẫy
Atomic write có sẵn; đọc `history[-1]` cho EOD report — đừng tự tính lại từ đầu.
