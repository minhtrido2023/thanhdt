# PREREG v3.2 — phụ lục giao thức chạy forward (viết TRƯỚC sự kiện forward đầu tiên)
Không đổi ngưỡng, schema, T1/T2/T3, nội dung prompt M1/M2. Chỉ đổi **cách tính lịch sử cooldown/cap** và **khoá giao thức**. Khoá = `PREREG_v3_2.md5` (md5 mọi file giao thức + hash hằng số); lệch ⇒ chương trình `SystemExit`, không chạy.

## 1. Lịch sử cooldown + cap tuần: tất định từ BQ (thay seed events_v3.csv + ledger)
- Với ngày T, lấy mọi (mã, ngày) đủ điều kiện sự kiện (cùng bộ lọc `sql_candidates`: universe_pit ruleset 1, mom20/idio20/volr/newhi/liq/rating≤4) trong **[T−200 ngày lịch, T−1]** — `sql_eligible_range`.
- Greedy **per-mã** (y hệt `build_events.greedy`): nhận ngày đủ điều kiện đầu tiên; ngày kế tiếp chỉ được nhận nếu cách sự kiện đã nhận trước >90 ngày lịch **và khác quý lịch**. Cap tuần bỏ qua khi tính cooldown (sự kiện bị `skipped_capacity` vẫn tính là đã phát — như trước).
- Cap 10/tuần ISO: số sự kiện đã XỬ LÝ trong tuần = replay tất định từ cùng dữ liệu BQ (mỗi ngày trong tuần trước T: các sự kiện nhận được, xếp liq giảm dần, lấy tối đa phần cap còn lại). **Không đọc ledger** để tính cooldown/cap ⇒ kết quả không phụ thuộc lượt chạy nào thành công/thất bại.
- Khoảng giữa 2026-11-13 và ngày cài cron được phủ tự động (cùng cơ chế: mọi ngày đủ điều kiện trong cửa sổ 200 ngày đều tính vào lịch sử, kể cả ngày chưa từng chạy M1). Ngày chưa chạy M1 KHÔNG bị bù ngược (live chỉ cho T = hôm nay ICT).
- Chỉ mốc idempotent theo `event_id` còn dùng ledger (không gọi lại M1 cho sự kiện đã ghi).
- Giới hạn đã biết: greedy bắt đầu tại T−200 có thể khác greedy từ gốc ở các chuỗi cooldown chéo biên cửa sổ; đã đo đối chiếu với events_v3.csv (xem `kb/projects/ai-momentum-p1-v3-20261115.md`).

## 2. Cổng dữ liệu (freshness) kiểm cả độ đầy
`MAX(time) ≥ T` **và** số dòng tại T ≥ 95% số dòng của phiên liền trước, cho cả `tav2_bq.ticker` (≠VNINDEX) và `universe_pit` (ruleset 1, in_universe). Thiếu/lệch ⇒ exit 4, không ghi gì. Thông điệp lỗi nội suy từ số đo được.

## 3. Phân biệt lỗi hạ tầng / nội dung (M1)
- Hạ tầng (không có binary `claude`, timeout, rc≠0, stdout không phải JSON, `is_error` khớp auth/usage/rate-limit/quota…) ⇒ dừng lượt chạy, **không ghi dòng** cho sự kiện đó, exit 5; chạy lại làm đúng sự kiện đó; không tính vào trần tuần.
- Nội dung (parse/schema/ngày evidence>T/hết max-turns hay budget) ⇒ ghi `m1_status=FAIL`.
- Lệnh M1: retro `--tools ""`; live `--tools WebSearch --allowedTools WebSearch`; cả hai `--max-turns` (live 8, retro 2) và `--max-budget-usd 0.60`; cwd tmp rỗng, `--setting-sources ""`, không MCP. Alias model `sonnet` có thể trôi ⇒ model thực tế ghi ở `usage[].models` từng dòng.

## 4. M2 (bổ sung v3.1)
`--model opencode/deepseek-v4.1-flash-free` truyền tường minh, `--retries 1`, `--timeout 240`; trần ngoài = (retries+1)·timeout + backoff + 60 = 545s. Mọi ngày M2 viết ra (`blind.evidence` chuỗi có ngày, `challenge.missed[].date`) phải ≤ T như M1, trái lại `m2_status=FAIL`. T3 chỉ gồm sự kiện `m2_status=OK`. Ghi `m2_model`, `m2_log` (đuôi stderr wrapper) vào mỗi dòng.

## 5. Khoá & chấm
Mỗi dòng ledger mang `prereg_version=v3.2`, `prereg_md5`, `protocol_md5` (md5 file khoá); scorer và G-proc chỉ lọc theo `protocol_md5` hiện hành. Không còn giá trị fallback khi thiếu file giao thức.
