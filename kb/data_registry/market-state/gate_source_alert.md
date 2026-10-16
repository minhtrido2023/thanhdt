---
kind: script-output
status: DERIVED
source: data/gate_source_alert.json
group: market-state
derived_from: deploy_golive_dt5g_v4/golive_state_today.json (trường source) + stdout lượt publish 19:00 + data/macro_health.json
writer: mike/bin/gate_source_check.py — gọi từ bq_freshness_check.sh ngay sau [pipeline-1] publish_gated_state (~19:01 ICT, ngày giao dịch)
role: BẰNG CHỨNG + khoá chống lặp cho cảnh báo "CỔNG DT5G SUY GIẢM" — KHÔNG phải nguồn trạng thái thị trường
---

# data/gate_source_alert.json

**Status: DERIVED — chỉ là bằng chứng của cảnh báo, không phải nguồn state.**

> ĐỀ XUẤT (§13) — mục mới, kèm 1 dòng cho `market-state/index.md`:
> `| [`gate_source_alert.md`](gate_source_alert.md) — data/gate_source_alert.json | DERIVED |`

## Là gì
File dấu do bước kiểm NGUỒN CỔNG ghi khi bản publish 19:00 ra nguồn khác `DT5G_macro`
(`DT4_only`, `DT4_STALE`, giá trị lạ, thiếu trường `source`, file state hỏng). Ngày thường
(nguồn `DT5G_macro`) bước kiểm KHÔNG ghi, KHÔNG sửa, KHÔNG xoá file này ⇒ file có thể tồn tại
với nội dung của một ngày cũ. Nằm trong `data/` của repo ngoài, gitignored.

Trường: `publish_date` (ngày ICT theo mtime file state), `source`, `published_at`, `as_of`,
`gate_line` (dòng `[get_gated_state] …` cổng tự in ở chính lượt đó), `gate_line_why` (lý do không
có dòng cổng), `health` (status/ts của `macro_health.json` lúc kiểm), `sent` =
`{"<ngày>|<nguồn>": {"discord": true, "bus": true}}` — khoá chống lặp theo từng cặp, chỉ giữ các
cặp của ngày publish hiện tại.

## Ai ghi / cadence
Producer duy nhất: `gate_source_check.py` trong chuỗi 19:00, và chỉ khi nguồn suy giảm.
Ghi atomic (`.tmp` + `os.replace`). Ghi hỏng ⇒ cảnh báo vẫn gửi, mất chống lặp + mất bằng chứng.

## Ai đọc
- `send_plan_report.sh` (21:00) qua `gate_source_check.plan_report_line()`: lấy phần BẰNG CHỨNG
  cho dòng ⚠️ "Cổng DT5G SUY GIẢM" trong báo cáo plan.
- Chính `gate_source_check.py` ở lượt chạy lại cùng ngày (đọc `sent`).

## Freshness (§14)
Consumer KHÔNG tin file này theo mtime: `plan_report_line()` chỉ trích bằng chứng khi
`source` và `published_at` của file KHỚP đúng `golive_state_today.json` đang hiển thị; không khớp
⇒ dòng ⚠️ nói thẳng "không có bằng chứng nguyên nhân của đúng lượt publish này". NGUỒN trong dòng
⚠️ luôn đọc từ `golive_state_today.json`, không đọc từ file này.

## Bẫy
- Đừng dùng file này để trả lời "cổng hôm nay ở nguồn nào" — nó không được dọn khi cổng hồi phục.
  Nguồn đúng: trường `source` của [golive_state_today.md](golive_state_today.md) hoặc
  `get_gated_state()`.
- Xoá file = lượt chạy lại cùng ngày sẽ báo lại (mất khoá chống lặp), không hại gì khác.
