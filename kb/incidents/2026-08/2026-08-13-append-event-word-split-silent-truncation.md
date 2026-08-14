# 2026-08-13 — `append_event.sh` nuốt IM LẶNG payload bị shell word-split: 13 event / 6 agent trong 1 tháng, gồm cả 1 câu hỏi `question` gửi user

**Bối cảnh phát hiện (Wags, job `Wags_20260813_054508`, dispatch bởi `wags_autofix` coord run
`coord-2026-08-13`).** Checker báo 2 `question` treo chưa có answer. Cả hai hoá ra **thật sự
đang mở, chờ USER quyết** — không phải bug checker (root cause A/B của skill `close-the-loop`
đều không áp dụng). Nhưng lúc đọc artifact để xác minh thì lộ ra một lỗi tooling khác.

## Triệu chứng

Event `question` của Mike (`event_id 71054a46…`, ts `2026-08-12T17:35:44Z`, topic
`retro-pattern-recurring-patternB-checker-wrong-representation`) có:
- `payload` là **chuỗi** (không phải object) và **cụt giữa câu**:
  `…"urgency":"normal — không chặn vận hành, nhưng đã đủ bằng chứng để không lặp lại vá`
- `trace_id` = `"thêm"` — chính là **từ kế tiếp** trong câu bị cắt.

Tức là shell đã word-split tham số payload: đoạn sau chỗ cắt trở thành `$5` (ghi thẳng vào
`trace_id`), phần còn lại rơi vào `$6, $7…` và **bị vứt hoàn toàn** vì script chỉ đọc `$1..$5`.

**Không phải ca lẻ.** Quét toàn bộ `bus/inbox/*.jsonl`: **13 event** dính cùng dạng, trải
**6 agent** (Taylor 5, quant-skeptic 4, Mike 1, Wags 1, DollarBill 1), từ `2026-07-14` tới
`2026-08-12`. `trace_id` rác quan sát được: `hom`, `nguoi`, `du`, `capacity`, `khoan`, `lai`,
`con`, `thêm`.

## Root cause — hai tầng, đều fail-OPEN

1. **Caller**: payload/topic chứa dấu nháy đơn lẻ (`'`) trong văn bản tiếng Việt hoặc trong
   trích dẫn kiểu `gia thuyet 'hien vat ca…'` ⇒ chuỗi `'…'` của caller đóng sớm ⇒ bash tách từ.
2. **`append_event.sh` không có bất kỳ kiểm tra nào**: không chặn `$# > 5`, không kiểm hình
   dạng `trace_id`, không kiểm payload JSON có parse được không. Cộng với
   `mike_json.py:cmd_event` fallback `json.loads` lỗi → giữ nguyên chuỗi (dòng 188-191, hành vi
   ĐÚNG cho payload chuỗi thường), event hỏng vẫn ghi thành công và in `appended …`.

Đây chính là **Pattern-B** mà câu hỏi bị hỏng đang mô tả: so sánh/ghi nhận **biểu diễn** của sự
thật thay vì sự thật, rồi degrade im lặng.

## Fix — `bin/append_event.sh`, fail LOUD (commit dưới)

Ba chốt, chạy trước khi ghi:
1. `$# > 5` ⇒ lỗi, in ra các tham số thừa (dấu hiệu word-split dài).
2. `trace_id` chứa khoảng trắng hoặc ký tự ngoài `[A-Za-z0-9_.:-]` ⇒ lỗi (rỗng vẫn hợp lệ).
3. Payload mở đầu `{` hoặc `[` mà `json.loads` fail ⇒ lỗi "JSON cụt", in 60 ký tự đuôi.

Đánh đổi có chủ ý: **mất 1 lần gọi** (agent thấy lỗi, quote lại rồi gọi lại) rẻ hơn **1 event
hỏng vĩnh viễn** — bus là append-only, không sửa lại được.

## Verify

- `bash -n` OK. Bộ test 8 ca (temp ROOT, không đụng bus thật): 4 ca hợp lệ vẫn PASS (JSON+trace_id,
  payload chuỗi thường, không trace_id, chuỗi có `{` ở giữa), 4 ca hỏng bị CHẶN.
- **Replay ca THẬT**: đọc lại payload cụt của Mike từ `bus/inbox/Mike.jsonl` + `trace_id='thêm'`,
  gọi lại script đã vá ⇒ **BỊ CHẶN** (`trace_id có ký tự lạ: $'th\303\252m'`). Tổng **9/9 PASS**.
- Không hồi quy: `ops_health_check_selfcheck.py` toàn bộ assertion PASS; 1 lệnh gọi live thật
  (heartbeat Wags) ghi bình thường.

## Không sửa dữ liệu cũ

13 event hỏng **không phục hồi được** (phần bị cắt không tồn tại ở đâu). Riêng câu hỏi của Mike
vẫn **đọc và quyết được** — chỉ mất phần đuôi trường `urgency`, các trường `de_xuat`/`quan_sat`
còn nguyên. Không dựng lại event giả.

## Bài học

Script vào bus là **biên giới ghi append-only** — validate ở đó, đừng dựa vào caller quote đúng.
Cụ thể: bất kỳ wrapper bash nào nhận "tham số cuối tuỳ chọn" mà không kiểm hình dạng thì đều
biến lỗi quote của caller thành dữ liệu bẩn không thể phân biệt với dữ liệu thật.
