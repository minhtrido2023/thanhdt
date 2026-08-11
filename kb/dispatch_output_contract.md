---
kind: reference
title: Dispatch output contract — hợp đồng đầu ra cho mọi pipeline dispatch nền
owner: Mike
---

# Hợp đồng đầu ra cho dispatch nền (`--bg`)

**Vì sao tồn tại** (2026-08-01, khảo sát vận hành): `jobs.sh status`/exit-code chỉ nói lên
tiến trình `claude -p` có thoát sạch không — KHÔNG nói lên agent có làm ĐÚNG việc hay không
(MIKE.md §Quy chuẩn bắt buộc mục 2). 6 pipeline dispatch nền tự viết lại quy tắc này mỗi nơi
một kiểu (`ops_autofix.sh`, `kb_nightly.sh`, `weekly_ops_audit.sh`, `wags_autofix.sh`,
`check_report_cadence.sh`, `fearbuy_weekly_scan.sh`); 6/10 lần dispatch tự động KHÔNG có bước
kiểm hậu-điều-kiện nào — đúng lớp lỗi gây ≥4 sự cố "chết im/lạc đề" trong 14 ngày qua
(`kb/incidents/2026-08/` — kb_nightly Friday chết 2 tuần, daily_retro chết 2 đêm).

## 2 nửa bắt buộc khi viết 1 pipeline dispatch nền mới

**Nửa 1 — prompt dispatch phải ra lệnh kết bằng ĐÚNG 1 bus event, nguyên văn topic:**

```
BẮT BUỘC (hợp đồng đầu ra máy đọc được — dispatch này chạy nền, không ai chờ trực tiếp, đây
là tín hiệu DUY NHẤT phân biệt "đã xong thật" với "lạc đề/chết im"): kết thúc bằng ĐÚNG MỘT
trong các lệnh sau, dùng NGUYÊN VĂN topic, không viết biến thể khác dù có vẻ tương đương:
- Xong việc: append_event.sh <agent> finding "<topic-done>" "<JSON tóm tắt>"
- Không xong/gặp ranh giới cấm: append_event.sh <agent> question "<topic-unresolved>" "<JSON lý do>"
```

Nếu pipeline chạy im lặng khi "sạch" (không có gì cần báo, vd `fearbuy_weekly_scan.sh`) —
vẫn PHẢI ghi 1 event xác nhận "đã quét, 0 case" (nguyên tắc quiet-heartbeat, coding_guidelines
đã có sẵn ở nhiều nơi khác) — im lặng hoàn toàn KHÔNG phân biệt được với chết im.

**Nửa 2 — caller phải tự kiểm event đó có thật, KHÔNG tin exit-code:**

```bash
SINCE_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"   # ghi TRƯỚC khi dispatch, không phải sau
"$ROOT/bin/dispatch.sh" <agent> "..." --bg ...
# ... (ở LẦN GỌI SAU cho cùng label/pipeline, hoặc cuối chính lần này nếu dispatch đồng bộ):
if ! python3 "$ROOT/bin/mike_json.py" has-event "$ROOT/bus" <agent> "$SINCE_ISO" \
     "finding:<topic-done>" "question:<topic-unresolved>"; then
  "$ROOT/bin/notify.sh" "⚠️ [<pipeline>] dispatch trước KHÔNG có kết quả xác nhận được — có thể đã lạc đề/chết im." >/dev/null 2>&1 || true
fi
```

⚠️ **`has-event` khớp topic TUYỆT ĐỐI.** Nếu prompt của bạn bảo agent ghi topic *bắt đầu bằng*
X (và agent nối mô tả tự do phía sau — Wags luôn làm thế), dùng **`has-event-prefix`** cùng cú
pháp. Sai chỗ này thì post-condition check KHÔNG BAO GIỜ khớp và pipeline báo "agent chết im"
mỗi ngày dù event nằm ngay trên bus — bug thật 08-04→08-11 ở chính `wags_autofix.sh`, xem
kb/ops_runbook.md § "Checker TRA CỨU sai".

`has-event` tự quét cả `bus/inbox/*.jsonl` (hot) lẫn `bus/inbox/archive/*.jsonl.gz`
(§17 coding_guidelines) — không cần tự viết glob. **Luôn truyền `SINCE_ISO` = thời điểm THẬT
dispatch bắt đầu**, không phải "N giờ trước" — một cutoff tương đối sẽ khớp nhầm event CŨ từ
lần dispatch trước đó có cùng topic (xem `ops_autofix.sh`'s `STARTED_ISO_FILE` làm mẫu cho
pipeline `--bg` cần nhớ mốc này qua nhiều lần gọi, vì bản thân lần dispatch không tự chờ
được kết quả).

## Giới hạn đã biết (đừng coi cơ chế này là hoàn chỉnh)

Label gắn ngày dùng 1 lần (vd `run-bot-fail-SpaceX-2026-07-28`) không có "lần gọi sau" nào để
tự kiểm — cơ chế này chỉ thật sự hiệu quả cho pipeline có **lần gọi lặp lại theo tên cố định**
(cron chạy định kỳ). Muốn phủ cả nhóm label-1-lần cần 1 sweep định kỳ riêng quét
`state/autofix/*.started_iso` thiếu `.confirmed` quá N giờ — chưa làm, ghi nhận là nợ.

## Ví dụ đã wire (đọc code thật, không chỉ đọc doc này)

`ops_autofix.sh` (bản đầy đủ nhất, có cache `.confirmed` tránh hỏi bus lặp lại) ·
`kb_nightly.sh` Phase 0b (`kb-weekly-editorial`, cửa sổ ~30h) · `weekly_ops_audit.sh` ·
`wags_autofix.sh` · `eod_trading_report.sh` (Spyros) · `inject_discretionary_orders.sh`
(thêm 2026-08-01, dùng `has-event` trực tiếp thay vì tự viết matcher).
