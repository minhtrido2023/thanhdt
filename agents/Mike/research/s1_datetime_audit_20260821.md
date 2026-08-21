# S1 Audit — `datetime.now()` naive classification cho TZ flip trên `ccdb-mike.service`

Job `Taylor_20260821_170812`, dispatch từ Mike. Bối cảnh: đang cân nhắc thêm
`Environment=TZ=Asia/Ho_Chi_Minh` vào unit `ccdb-mike.service`. Hiện `systemctl show
ccdb-mike.service -p Environment` **rỗng** và host `timedatectl` = **`Etc/UTC`** — mọi subprocess
(kể cả Bash tool trong phiên Claude) hiện mặc định UTC trừ khi script tự set TZ / source
`wc_env.sh`. Audit này KHÔNG sửa code, chỉ khảo sát và phân loại.

## Tổng số file tìm được

`grep -rl "datetime.now()"` trên 2 repo (`claude-code-discord-bridge`, `WorkingClaude`), loại
`__pycache__`, đếm được ~140 hit thô — nhưng phần lớn là NHIỄU:

| Loại nhiễu bị loại khỏi phân tích | Số lượng ước tính | Lý do loại |
|---|---:|---|
| Trùng lặp qua `mike/.claude/worktrees/*` và các thư mục `wt-*` (git worktree clone) | ~90 | Mirror 1:1 file gốc trong `mike/bin/`, `mike/agents/Taylor/` — cùng 1 file, đếm N lần |
| Vendor code (`stockquery/vnstock_stockquery/vnstock/*`, `.claude/skills/kronos/vendor/Kronos/*`) | 12 | Thư viện bên thứ ba, không phải code mình viết/deploy trực tiếp cho ccdb-mike |
| `.md`/`.patch` khớp chuỗi `datetime.now()` trong văn bản (kb archive, coding_guidelines, patch diff) | 6 | Không phải code thực thi |
| False positive — chuỗi `datetime.now()` chỉ xuất hiện trong COMMENT/docstring, không có lệnh gọi thật (`dt5g_writer_watch.py`, `staleness_watch.py`) | 2 | Verify bằng `grep -n "datetime.now()" <file>` riêng — không match dòng code |

**Sau lọc: ~55 file code thật có gọi `datetime.now()`**, phân loại dưới đây (đã đọc code thật, không suy đoán từ tên file).

| Category | Số file |
|---|---:|
| (a) NGUY CƠ — cần sửa/soát trước khi flip | **1** |
| (b) AN TOÀN / SẼ TỐT HƠN sau flip | ~40 |
| (c) KHÔNG QUAN TRỌNG (one-off/test/vendor/archive) | ~14 |

## Phát hiện quan trọng nhất — pattern NGƯỢC với giả thuyết ban đầu

Giả thuyết dispatch: "code đang ĐÚNG dưới UTC, flip sang ICT sẽ LÀM SAI nó." Thực tế đo được:
**codebase đã quy ước ICT rộng rãi** (crontab export `TZ=Asia/Ho_Chi_Minh` theo từng dòng, script
tự source `wc_env.sh`, nhiều helper tự anchor `ZoneInfo`/`datetime.now(timezone.utc)+7h` — xem
`bin/dt5g_writer_watch.py` dòng 83-87, `bin/snapshot_corp_action_daily.py::ict_today()`,
`agents/Taylor/anomaly_scan.py::_ict_now()`). Host UTC hiện tại mới là điểm KHÔNG khớp quy ước —
với các lệnh gọi `datetime.now()` trần chạy AD-HOC dưới `ccdb-mike.service` (agent gọi Bash tool
tương tác, không qua cron đã tự set TZ), flip sẽ làm chúng khớp ĐÚNG quy ước ICT sẵn có, **không
phải phá vỡ nó**. Điều này khớp với đúng lý do dự án đang cân nhắc flip (bridge repo vừa có 2
commit `feat(outbound): enforce ICT timestamp...` 2026-08-21).

## (a) NGUY CƠ — 1 file, mức độ THẤP nhưng cần soát

| file | dòng | vấn đề |
|---|---|---|
| `mike/agents/Taylor/anomaly_scan.py` | 294 | `STATUS_SNAP` ghi `"asof": datetime.datetime.now().isoformat(...)` — **naive trần**, KHÔNG nhất quán với 2 chỗ khác trong CÙNG FILE: dòng 58 `_ict_now()` (`datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=7)` — ICT thật, không phụ thuộc TZ process) và dòng 325 `flags["_meta"]["generated_at"] = datetime.datetime.now(datetime.timezone.utc)...` (UTC tường minh). Tác giả file rõ ràng đã Ý THỨC được bẫy TZ (comment dòng 57 trích §16) nhưng bỏ sót đúng 1 chỗ ghi `asof` của `anomaly_status_snapshot.json`. Trước flip: `asof` = UTC-naive (khớp `generated_at` UTC, LỆCH `_ict_now()` 7h). Sau flip: `asof` = ICT-naive (khớp `_ict_now()`, LỆCH `generated_at` UTC 7h). **Đằng nào cũng có 1 cặp lệch nội bộ trong file** — flip không tạo ra bug mới, chỉ ĐỔI cặp nào lệch. Chưa xác nhận được có consumer nào thực sự đo tuổi `asof` (chỉ thấy field được ghi, chưa thấy code parse lại để tính age — có thể chỉ hiển thị). **Khuyến nghị**: đổi dòng 294 sang gọi `_ict_now()` sẵn có trong file, khớp 2 chỗ kia — sửa 1 dòng, loại bỏ ambiguity vĩnh viễn bất kể flip quyết định thế nào. |

Không tìm thấy file nào khác có pattern "so sánh `datetime.now()` trần với giá trị UTC-aware/mốc
bên ngoài UTC thật" — đã kiểm tra riêng: `trading_bot/brokers.py`, `trading_bot/config.py`,
`trading_bot/executor.py` (broker/gate lõi) **KHÔNG** gọi `datetime.now()` trần chỗ nào cả.
`trading_bot/plan.py:115` và `trading_bot/strategies.py:237` có gọi nhưng chỉ để ghi field
`created_at`/`logged_at` — thuần audit-log, không có code nào parse lại để so sánh cross-TZ.

### Ứng viên tưởng nguy hiểm nhưng đã VERIFY là AN TOÀN

- **Discord `Embed.timestamp=datetime.now()`** (`claude-code-discord-bridge/claude_discord/ext/api_server.py:2730`, `examples/ebibot/cogs/{reminder,watchdog}.py`): đọc source `discord/embeds.py:358-359`
  (`.venv` cài trong bridge repo) — setter gọi `value.astimezone()` (không tham số) trên datetime
  naive, tự gắn ĐÚNG offset theo TZ hệ thống tại thời điểm gọi. Vì `datetime.now()` và
  `.astimezone()` dùng CÙNG TZ hệ thống, round-trip luôn đúng bất kể host là UTC hay ICT. AN TOÀN.
- `macro_state_live.py:305` (`get_gated_state()`, gate fail-safe DT5G→DT4 mô tả trong CLAUDE.md):
  `age_min = (datetime.now() - datetime.fromisoformat(h["ts"])).total_seconds()/60` — `h["ts"]`
  do `macro_healthcheck.py` ghi (`NOW.isoformat()`, cron dòng riêng đã có `TZ=Asia/Ho_Chi_Minh`
  — xem crontab). Trước flip: gọi ad-hoc qua agent (UTC) so với ts ghi dưới ICT → lệch 7h theo
  hướng **AN TOÀN** (overcount tuổi → dễ rơi vào fail-closed DT4 hơn, không phải fail-open). Sau
  flip: khớp nhau, hết lệch. Không phải regressions, là fix.
- `bin/discretionary_accumulation_inject.py`, `bin/report_delivery_gate.py`,
  `bin/ops_health_check_selfcheck.py`: đều dùng `.astimezone()` ngay sau `datetime.now()` (tự gắn
  offset đúng TZ hệ thống) — cùng pattern an toàn như embed ở trên.
- `claude_discord/ext/teams_store.py:217,356`: `datetime.now().astimezone().isoformat()` — cùng
  pattern, an toàn.
- `bin/paper_programs_daily_report.py:690-691`: `os.environ.setdefault("TZ", "Asia/Ho_Chi_Minh")`
  rồi `datetime.now()` ngay dòng sau — LƯU Ý: `os.environ.setdefault` giữa tiến trình KHÔNG tự
  động áp dụng cho glibc TZ trừ khi gọi `time.tzset()` (Python gotcha có thật, không liên quan
  trực tiếp tới quyết định flip — nếu TZ đã kế thừa từ service (sau flip) thì dòng này thành
  no-op vô hại; nếu KHÔNG kế thừa và không có `time.tzset()`, dòng setdefault này có thể ĐÃ không
  có tác dụng từ trước — ngoài phạm vi S1, nêu ra để theo dõi riêng chứ không phải phát hiện của
  audit này).

## (b) AN TOÀN / SẼ TỐT HƠN sau flip — ~40 file, mẫu đại diện

Tuyệt đại đa số dùng `datetime.now()` cho **1 trong 3 việc**, cả 3 đều lành tính khi đổi TZ:

1. **Nhãn thời gian hiển thị cho người đọc** (report/log header, không có logic đọc lại):
   `layer3_v4_shadow.py`, `sim_v5_dt4_transparent.py`, `newdeals_daily_report.py`,
   `telegram_recommend.py`, `analyze_portfolio.py`, `dt4_decision_review.py`,
   `auto_update_commodity_wb.py`, `shadow_track_v3_3b.py`, `shadow_track_v3_4b.py`,
   `papertrade_compare.py`, `layer3_paper_trade.py`, `paper_trade_daily.py`,
   `test_kelly_q3_v2/v3/v4_hybrid.py`, `test_kelly_q2_v2.py`, `test_kelly_q2_heur_n100.py`,
   `test_kelly_q2q3_combined.py`, `test_kelly_q3_tier_weights.py` — flip chỉ đổi nhãn giờ hiển
   thị từ UTC sang ICT, **đúng ý nghĩa hơn** cho báo cáo thị trường VN.
2. **Tag filename (suffix backup/archive/zip)**: `deploy_v2g_pe3c_s3.py`,
   `deploy_v2g_pe3_canonical.py`, `deploy_v2g_canonical.py`, `deploy_ngu_hanh.py`,
   `package_for_deploy.py`, `state_publish_immutable.py`, `snapshot_state_vintage.py` — chỉ đổi
   chuỗi ngày trong tên file, không ảnh hưởng logic.
3. **Ngày lịch VN cho việc TÍNH TOÁN theo lịch** (ngày giao dịch, cửa sổ ngày, backlog check):
   `update_shares_live.py`, `pull_us_market.py`, `pt_dates.py`, `capit_episode.py`,
   `rubber_weekly.py`, `vcb_fx_feed.py`, `simulation_v1_6.py` — đây đúng là trường hợp (b) trong
   mô tả gốc: hiện SAI vì UTC (ranh giới ngày lệch múi giờ VN 7h quanh nửa đêm), flip sang ICT
   **sửa đúng** ý nghĩa lịch giao dịch.

## (c) KHÔNG QUAN TRỌNG

- Toàn bộ `test_kelly_*.py` ở root — đều là script backtest/nghiên cứu một lần (tên tự khai báo
  "test_"), không phải test suite thật, không phải production path (khớp coding_guidelines §23
  hệ luận 2: `test_*.py` ở root không phải test).
- `*_selfcheck.py` (`rubber_weekly_selfcheck.py`, `lag_live_schedule_selfcheck.py`,
  `universe_pit_p3/p4_selfcheck.py`, `freshness_ops_selfcheck.py`, `book_tagging_selfcheck.py`,
  `lag_liq_signal_filter_selfcheck.py`, `paper_main_window_selfcheck.py`) — tự test hành vi
  TZ, một số CHÍNH LÀ bài test xác nhận `TZ=Asia/Ho_Chi_Minh` hoạt động đúng
  (`paper_main_window_selfcheck.py` dòng 174-179) — không cần sửa, có lợi cho flip.
- `stockquery/vnstock_stockquery/vnstock/*` (12 file) — vendor thư viện `vnstock` bên thứ ba,
  vẫn được import bởi vài script production (`update_shares_live.py`,
  `layer3_v4_shadow.py`...) nhưng `datetime.now()` bên trong vendor chỉ dùng cho proxy
  rate-limit/cache TTL nội bộ thư viện — không phải logic nghiệp vụ VN, không thuộc phạm vi audit
  này (không sửa code vendor).
- `.claude/skills/kronos/vendor/Kronos/*` — vendor mô hình forecast, không liên quan flip.
- `deploy_v3_4b_package/archive/`, `release_8l_full/`, `8l_package/` — đã archive/deprecated,
  không chạy production.
- `examples/ebibot/cogs/{reminder,watchdog}.py` — xác nhận **không có systemd unit nào chạy
  ebibot** (`systemctl list-units | grep ebibot` rỗng) — code ví dụ, không deploy.
- `mike/agents/Taylor/{exp_*,probe_*,pending_*,job_*}/**` — thư mục R&D một lần, không phải
  production path.
- `mike/bin/anomaly_escalate.py` — `escalated_at` chỉ để audit log ledger, không có so sánh TZ.

## Kết luận — danh sách cụ thể cần sửa trước khi flip

**Chỉ 1 dòng, 1 file:**

- `mike/agents/Taylor/anomaly_scan.py:294` — đổi
  `datetime.datetime.now().isoformat(timespec="seconds")` thành `_ict_now().isoformat(timespec="seconds")`
  (hàm đã có sẵn cùng file, dòng 57-58) để nhất quán với `generated_at`/`_ict_now()` khác trong
  file. Mức độ: THẤP — chưa xác nhận có consumer thực sự đo tuổi field `asof` này (grep 6 file
  đọc `anomaly_flags.json`/status_snap nhưng đa số đọc `flags["_meta"]`, không phải
  `STATUS_SNAP["asof"]`). Đây là dọn-dẹp phòng ngừa, không phải blocker cứng.

**Ước lượng khối lượng nếu muốn sửa triệt để mọi bare `datetime.now()` sang tường minh TZ (KHÔNG
bắt buộc để flip an toàn)**: ~40 file loại (b), mỗi file 1-3 dòng đổi từ `datetime.now()` sang
`datetime.now(timezone.utc)` hoặc ICT helper — nhưng theo phân tích trên, **phần lớn các dòng này
sẽ chỉ TỐT HƠN sau flip**, sửa trước là công lãng phí, trái tinh thần §2 (Simplicity First,
coding_guidelines) — không nên làm.

## Recommendation

**CÓ, nên flip TZ ngay sau khi sửa 1 dòng ở `anomaly_scan.py:294`** (hoặc thậm chí không sửa nó
trước — mức rủi ro của dòng đó rất thấp và bản thân flip cũng không LÀM XẤU đi tình trạng hiện
tại của nó, chỉ đổi hướng lệch). Không tìm thấy file production nào mà `datetime.now()` trần đang
ĐÚNG nhờ giả định UTC và sẽ SAI sau khi có ICT — pattern ngược lại (đang lệch vì host UTC không
khớp quy ước ICT đã thiết lập rộng khắp qua crontab/`wc_env.sh`/`ZoneInfo` helper) mới là cái audit
này đo được. Rủi ro lớn nhất không nằm ở logic Python mà ở khả năng có script CHƯA audit (ngoài
2 repo đã quét, ví dụ cron job gọi trực tiếp `python3 -c "..."` một lần) — nhưng đó là rủi ro
runtime cần theo dõi sau flip (`bin/staleness_watch.py`, `bin/ops_health_check_selfcheck.py`),
không phải thứ audit tĩnh này bắt được thêm.
