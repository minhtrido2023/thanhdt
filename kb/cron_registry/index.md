---
kind: registry-index
title: Cron Registry — phần tham chiếu (policy / step-detail / changelog)
owner: Winston (data-ops)
format: OKF (Open Knowledge Format) — markdown + YAML frontmatter
main_table: ../cron_registry.md
migrated_from: kb/cron_registry.md (single-file → tách phần tham chiếu 2026-07-28 job Winston_20260728_114643)
---

# Cron Registry — phần tham chiếu

> ⚠️ **LỊCH CRON HIỆN TẠI (bảng chính, mọi job theo giờ ICT) KHÔNG ở đây — nằm ở
> [`../cron_registry.md`](../cron_registry.md).** Bảng đó CỐ Ý giữ nguyên 1 khối liền mạch: giá trị
> cốt lõi của nó là thấy được buffer/phụ thuộc GIỮA các dòng liền kề (vd "sau publish DT5G ~19:01,
> 9' buffer") để tránh vintage-mismatch kiểu sự cố C1 2026-07-12 — TÁCH từng dòng sẽ phá mất giá trị
> này, nên KHÔNG tách.
>
> Thư mục này chỉ chứa các phần THAM CHIẾU ĐỘC LẬP tách khỏi bảng — thứ người ta muốn tra RIÊNG mà
> không cần load cả lịch trình.

## Nội dung

| File | Là gì |
|---|---|
| [`_adding-cron-policy.md`](_adding-cron-policy.md) | RULE khi THÊM/SỬA 1 dòng cron: 4 câu hỏi bắt buộc + chống xung đột tài nguyên + nguyên tắc buffer+verify + ghi lại ở đâu. Enforce bởi `coding_guidelines.md §11`. |
| [`papertrade_daily_steps.md`](papertrade_daily_steps.md) | Chi tiết 23 step nội bộ của cron `papertrade_daily.sh` (15:30) — không cần đọc khi tra lịch tổng. |
| [`CHANGELOG.md`](CHANGELOG.md) | Log thay đổi lịch cron (thêm/xoá/đổi giờ, ai, job, audit-trail §11). Provenance, KHÔNG phải narrative sự cố (đó là `kb/INCIDENTS.md`). |

**Grep vẫn hoạt động:** `grep -rn "<script/giờ>" mike/kb/cron_registry.md mike/kb/cron_registry/`.

↩ [Về cron_registry (bảng chính)](../cron_registry.md)
