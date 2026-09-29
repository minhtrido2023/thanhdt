---
kind: incident
date: 2026-09-19
status: fixed
severity: low
owner: Mike (weekly ops audit, job Mike_20260918_204303)
tags: [selfcheck, cron, drift, false-alarm]
---

# 4 selfcheck ĐỎ tồn đọng 1–7 ngày — KHÔNG ca nào là lỗi production

## Triệu chứng
`bin/selfcheck_weekly_baseline_check.sh` (cron 04:30 ICT) ghi 4 bus question `selfcheck-red: …`
tồn đọng 1–7 ngày. Bề ngoài giống 4 regression riêng lẻ.

## Chẩn đoán — 3 nguyên nhân khác nhau, 0 lỗi production

| Selfcheck | Đỏ từ | Nguyên nhân | Commit |
|---|---|---|---|
| `wait_for_artifact_selfcheck.py` | 09-16 | Assertion 5b neo cứng `("12","12")` = 19:12 ICT. User duyệt đổi `hit_details_daily.sh` 19:12→19:00 ngày 09-16 (`cron_registry.md:70`) ⇒ assertion lỗi thời | `a7dece49` |
| `production_manifest_selfcheck.sh` | 09-14 | 4 gốc cron mới 09-15..09-18 chưa vào `ROOT_TIER` ⇒ nhãn `T?` + drift giờ hit_details | `0643b543` |
| `check_report_cadence_selfcheck.py` | 09-12 | Ca #20 so `out_a == out_b` nhưng `run_detector()` dựng TemporaryDirectory MỚI mỗi lần gọi, detector trả đường dẫn TUYỆT ĐỐI ⇒ **không bao giờ bằng nhau được**, bất kể detector có state ẩn hay không | `73dfbe54` |
| `report_return_gate_selfcheck.py` | 09-12 | File tự khai docstring "~8-10 phút, chạm BQ"; runner cho trần 60s ⇒ `rc=124` CHẮC CHẮN mỗi lần. `is_live()` không bắt được vì gọi qua subprocess, không có literal `bq query` | `21734026` |

## Nguyên nhân GỐC chung
Cả 4 là **selfcheck lệch khỏi thực tế đã được duyệt**, không phải production lệch khỏi selfcheck:
1. Hai ca đầu — thay đổi production ĐÚNG và đã ghi registry, nhưng **không ai chạy selfcheck liên
   quan sau khi đổi** (§23 nói phạm vi, không nói "đổi crontab thì chạy selfcheck nào").
2. Hai ca sau — **assertion/ngân sách tự nó vô hiệu từ lúc viết**, chỉ lộ ra khi có bộ dò đỏ hằng
   ngày. Đây là giá trị THẬT của cơ chế `selfcheck_weekly_baseline_check.sh`, không phải nhiễu.

## Bài học
- **Ca #20 là dạng nguy hiểm nhất**: một assertion không thể ĐÚNG được (so đường dẫn tmp ngẫu
  nhiên) trông y hệt một assertion bắt được lỗi thật. Chỉ đọc thông điệp FAIL không phân biệt
  được — phải hỏi *"assertion này có bao giờ xanh được không?"*
- **Sửa assertion lỗi thời ≠ nới lỏng**: cả 4 bản vá đều kèm mutation chạy thật chứng minh
  assertion mới VẪN giết được ca lỗi gốc (xem commit message từng cái).
- Đổi giờ crontab của một consumer ⇒ phải chạy selfcheck của chính consumer đó. Chưa có cơ chế
  cơ học ép việc này (ứng viên: `selfcheck_scope_map.sh` mở rộng sang dòng crontab).

## Verify
4/4 chạy thật xanh sau vá; `bin/bus_question_audit.py` PENDING 9 → 5.
