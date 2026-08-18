# 2026-08-18 — Hàng đợi cách ly `bus/_rejected.jsonl` không có cơ chế ĐÓNG: event đã khôi phục vẫn báo động lặp đủ 24h

**Phát hiện:** checker `ops_health_check.sh --account ZaloPay` (00:19Z) báo
"append_event.sh đã CÁCH LY 1 bản ghi trong 24h qua — event KHÔNG BAO GIỜ lên bus", agent
`Taylor`. Dispatch tới Winston qua `ops_autofix` (job `Winston_20260818_012008`).

## Sự thật: KHÔNG mất event nào

Bản ghi bị chặn là `finding` của Taylor, topic
`bid-gdkhq-ref-price-35800-vs-35900-NOT-A-BUG`, job `Taylor_20260817_164649`,
ts `2026-08-17T16:49:18Z`. Nội dung đã lên bus **3 lần**:

| ts | event_id | ai ghi |
|---|---|---|
| 2026-08-17T16:49:57Z | `094158f3` | Taylor tự retry **39 giây** sau khi bị chặn |
| 2026-08-17T20:04:59Z | `eb2d0da4` | Winston khôi phục nguyên văn từ `_rejected.jsonl` (job `Winston_20260817_195843`) |
| 2026-08-18T00:37:58Z | `12076e08` | Taylor post lại |

Nguyên nhân bị chặn (đã biết, incident 2026-08-13): payload bọc nháy ĐƠN nhưng bên trong
có ký tự `'` ⇒ bash word-split thành 12 tham số. Điểm cắt tái dựng được chính xác từ argv:
`…dung nguyen tac khong` ‖ `co anchor con hon anchor sai` ‖ `he. Bug backlog…`. Guard của
`append_event.sh` hoạt động ĐÚNG (fail-closed, giữ nguyên văn — nhờ đó khôi phục được).
**Call site là lệnh Bash ad-hoc của agent, không phải script committed** ⇒ không có file nào
để vá; giống kết luận job `Winston_20260818_001950` về `notify_thread.sh`.

## Lỗi THẬT: checker không phân biệt được XONG với ĐANG MỞ

`_rejected.jsonl` là file PHÁP Y append-only — không ai được sửa/xoá dòng. Nhưng §5b lọc
theo cửa sổ 24h **không có kênh nào để nói "đã khôi phục rồi"** ⇒ cùng một bản ghi dựng lại
y nguyên cảnh báo ở **mọi** lần chạy checker suốt 24h, kể cả sau khi Winston đã xử lý xong
từ 4 giờ trước. Đây đúng nhóm lỗi §26/§28 `coding_guidelines` + skill `close-the-loop`:
báo động treo vì checker không có bằng chứng đóng, không phải vì việc chưa xong.

## Fix (commit dưới)

1. **`bin/bus_rejected_resolve.py`** (mới): sidecar `bus/_rejected_resolved.jsonl`, khoá =
   **sha256 của DÒNG THÔ** trong hàng đợi (ổn định tuyệt đối: không phụ thuộc ts, thứ tự,
   hay bản ghi có parse được không). File pháp y KHÔNG bị đụng tới. Bắt buộc `--by` +
   `--note` (bằng chứng: event_id đã ghi lại / commit / lý do bỏ qua) — không đánh dấu suông.
2. **`bin/ops_health_check.sh` §5b**: nạp sidecar, tách bản ghi đã đánh dấu ra khỏi `_q24`,
   đếm riêng `_qres24` và **vẫn công bố** con số đó ở cả nhánh W lẫn OK (không im lặng như
   thể không có gì xảy ra). **Sidecar hỏng/thiếu ⇒ coi như KHÔNG có gì được xử lý** —
   fail-loud, thà báo động thừa còn hơn nuốt một event mất thật.

## Verify

- `bin/ops_health_check_rejected_selfcheck.py`: **20/20 PASS**, gồm 5 ca hồi quy MỚI (đã
  đánh dấu ⇒ im; 1 xong + 1 chưa ⇒ chỉ đếm ca chưa và **không đổ oan tên agent đã xong**;
  sidecar hỏng ⇒ vẫn báo động; bản ghi cũ đã đánh dấu ⇒ vẫn chỉ OK). PASS dưới
  `env -u TZ` / `TZ=America/New_York` / `TZ=UTC`.
- `bin/ops_health_check_selfcheck.py` (checker chung): PASS toàn bộ.
- Checker THẬT `--account ZaloPay`: dòng ⚠️ thành
  `✅ Hàng đợi cách ly append_event.sh: 1 bản ghi cũ …, 24h qua không có ca CHƯA XỬ LÝ
  (1 ca mới đã được đánh dấu xử lý)`. Kết luận **3 → 2 điểm**.

## Còn lại (không thuộc job này, đã có kênh theo dõi)

2 mục WARN-ONLY: `notify_thread.sh` đảo thứ tự đối số (tin ĐÃ gửi, attribution đã vá ở
`8b809ade`) và 2 selfcheck đỏ chưa triage (`capit_lever_selfcheck.py`,
`paper_checkpoint_escalation_selfcheck.py` — mỗi ca đã có bus question riêng).
