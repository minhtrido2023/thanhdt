---
kind: local-file
status: CANONICAL
source: data/paper_report_state.json + mike/kb/paper_programs_charter/<id>.md
group: paper-harness
note: 2 artifact PHỤ TRỢ của tầng render báo cáo — KHÔNG phải nguồn số liệu giao dịch
writer: mike/bin/paper_programs_daily_report.py (cron 16:00 ICT T2-T6)
---

# data/paper_report_state.json + mike/kb/paper_programs_charter/&lt;id&gt;.md

**Status: CANONICAL (artifact của tầng render, sinh 2026-07-31)**

## Là gì
Hai artifact do redesign trình bày báo cáo paper (2026-07-31) sinh ra, để báo cáo hàng ngày
KHÔNG phải in lại nội dung tĩnh mỗi ngày:

- **`data/paper_report_state.json`** — ảnh chụp trạng thái gate GO/NO-GO của từng chương trình ở
  lần render trước + ngày thay đổi gần nhất. Dùng DUY NHẤT để quyết định "hôm nay có in lại
  checklist gate đầy đủ không" (chỉ in khi có status ĐỔI). Không chứa số liệu giao dịch/NAV nào.
- **`mike/kb/paper_programs_charter/<id>.md`** — charter TỰ SINH từ `mike/kb/paper_programs_registry.json`
  (mục đích, mốc nghiệm thu, tiêu chí GO/NO-GO đầy đủ, owner, nguồn dữ liệu). Báo cáo ngày chỉ
  LINK tới, không paste.

## Ai ghi / cadence
`mike/bin/paper_programs_daily_report.py` mỗi lần chạy LIVE (cron 16:00 ICT T2-T6, xem
`kb/cron_registry.md`). Ghi atomic (tmp + `os.replace`).
- State CHỈ được ghi khi chạy không có `--date` (hoặc có `--force-state`) và không có `--no-state`
  — chạy lại quá khứ để so sánh KHÔNG làm nhiễu mốc "gate đổi lần cuối" của bản production.
- Charter chỉ được ghi lại khi nội dung registry của chương trình đó THẬT SỰ đổi (so sánh nội dung,
  không so mtime) → git diff sạch, không churn hằng ngày.

## Bẫy
- **KHÔNG sửa tay charter** — mọi sửa tay sẽ bị ghi đè ở lần render kế tiếp. Sửa
  `mike/kb/paper_programs_registry.json` rồi chạy lại report.
- **Xoá `paper_report_state.json` = báo cáo hôm sau in lại TOÀN BỘ checklist gate** (coi như lần
  đầu). Vô hại về số liệu, chỉ dài hơn 1 ngày.
- State file này KHÔNG phải nguồn trạng thái chương trình — nguồn duy nhất vẫn là registry (tĩnh)
  + probe (động). Đừng đọc nó để biết "gate nào đã PASS" trong code khác.

## Kiểm chứng
`python3 mike/bin/paper_report_render_selfcheck.py` (26 check, chạy trên fixture tmpdir, không
đụng dữ liệu thật).

↩ [Về nhóm paper-harness](index.md)
