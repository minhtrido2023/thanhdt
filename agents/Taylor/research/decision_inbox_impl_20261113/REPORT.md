# Decision Inbox — triển khai (job Taylor_20261113_080329, 13/11/2026)

Theo `research/decision_inbox_design_20261113/DESIGN.md` (user duyệt 13/11 15:03 ICT). **Chưa merge, chưa bật cog.**

- Nhánh: `feat/decision-inbox-20261113` (6 commit, base `fbe56ddef`), worktree sparse `/home/trido/thanhdt/WorkingClaude/wt-decision-inbox-20261113` (15 MB; `git worktree remove` sau khi merge).
- Diff `git diff --numstat master...HEAD`: **+2110 / −0**, 15 file. Sửa file có sẵn chỉ 4 (cộng dòng, không xoá): `close_bus_question.py` +19, `append_event.sh` +14, `daily_retro.sh` +25, `bus_question_closure_selfcheck.py` +19.

## Selfcheck thật (chạy cả `env -u TZ` và `TZ=America/New_York`, `MIKE_BOT_TEST_MODE=1`, mọi bus/state ở tmpdir)

| Selfcheck | Pass / Fail (mỗi TZ) |
|---|---|
| `bus_question_closure_selfcheck.py` (cũ + 5 ca provenance) | 30/30 · 0 fail |
| `decision_inbox_selfcheck.py` (bộ khớp; DESIGN §7 cần ≥25) | 84/84 · 0 fail |
| `decision_actions_selfcheck.py` (whitelist + ledger + chốt ở `append_event.sh` thật) | 65/65 · 0 fail |
| `classifier_denial_count_selfcheck.py` | 12/12 · 0 fail |
| `surface_question_selfcheck.py` (gồm vòng khép kín reply→đóng) | 10/10 · 0 fail |
| `decision_inbox_cog_selfcheck.py` (message giả + `load_custom_cogs` THẬT của bridge) | 20/20 · 0 fail |

Tổng 221 ca mới/mở rộng × 2 TZ, 0 fail. Selfcheck có sẵn chạm file đã sửa: `append_event_selfcheck.py` OK, `retro_escalate_selfcheck.py` OK, `daily_retro_failcause_selfcheck.sh` 8/8, `daily_retro_measured_by_selfcheck.sh` **48/48** (lần đầu 47/48 — chữ fallback của khối mới trùng chuỗi "helper không chạy được" mà selfcheck cũ cấm; đã đổi chữ, master cũng 48/48).
`shellcheck_gate.sh` sạch (chỉ 2 `info` có sẵn: SC1091 ở daily_retro.sh:36, SC2016 ở append_event.sh:53). Pre-commit chạy đủ ở cả 6 commit, không bỏ gate nào. Gate chặn 1 lần (commit bước 3): ID Discord trần trong fixture + import thừa (ruff) — đã sửa, không dùng `SKIP`.

## File đã chạm
`bin/close_bus_question.py` (+`--provenance-json`; cấm đè `resolves/decided_by/closed_by/resolution/evidence/source_topic`) · `bin/decision_inbox.py` (bộ khớp T1/T2/T3, risk money, hỏi lại 1 lần TTL 24h, shadow/live, flock, processed) · `bin/decision_actions.py` (whitelist 5 action + sổ `actions.jsonl` + `--validate`) · `bin/append_event.sh` (validate `on_answer` lúc ghi câu hỏi) · `bin/classifier_denial_count.py` · `bin/daily_retro.sh` (khối đếm + mục 2g + leo thang) · `bin/surface_question.py` · `ccdb_cogs/decision_inbox_cog.py` · `decision_templates/README.md` · 6 file selfcheck.
KHÔNG chạm: `/workspace/ccdb-mike/.env`, `.claude/settings*.json`, `hooks/`, service ccdb-mike, core bridge, BOT_STOP, trading_rules.json, secrets, broker.

## Bật shadow (việc của user, SAU KHI merge) — đúng 2 dòng `.env` + restart
Trong `/workspace/ccdb-mike/.env`:
```
CUSTOM_COGS_DIR=/home/trido/thanhdt/WorkingClaude/mike/ccdb_cogs
DECISION_INBOX_USER_IDS=<Discord user id của bạn>
```
rồi `systemctl --user restart ccdb-mike` (~15 s gián đoạn). `DECISION_INBOX_MODE` không đặt ⇒ **shadow** (chỉ ghi `status decision-inbox-shadow`, không đóng, không trả lời Discord). Thiếu `DECISION_INBOX_USER_IDS` ⇒ cog vô hiệu (fail-closed, log 1 cảnh báo). Chuyển `live` = thêm `DECISION_INBOX_MODE=live` — sau 5 phiên shadow, user duyệt.

## Điểm cần reviewer/Mike nhìn kỹ (không giấu)
1. **Chưa kiểm trên gateway Discord thật.** Cog giả định bot nhận được tin CỦA CHÍNH NÓ qua `on_message` (discord.py có gửi) để ghi map thẻ→message_id. Selfcheck dùng message giả. Shadow phải xác nhận `state/decision_inbox/surfaced.jsonl` có dòng mới sau khi một tin bot mang `[#q…]` được đăng; nếu rỗng thì chỉ còn đường thẻ `A #q…` (T2) — vẫn dùng được.
2. **Bước 4 chỉ là công cụ**: `surface_question.py` (`--list/--tag/--dry-run/đăng`). CHƯA có chỉ dẫn nào buộc Mike dùng nó khi hỏi user (không sửa hooks/settings theo ràng buộc). Mike cần nhận quy ước: mọi tin hỏi user về 1 câu bus phải mang thẻ từ script này.
3. `dispatch_bg` chưa dùng được: `decision_templates/` chỉ có README, template chưa tồn tại ⇒ `append_event.sh` từ chối ghi câu hỏi tham chiếu template. Cố ý (mỗi template là 1 commit có người duyệt).
4. `paper_registry_set` ghi `kb/paper_programs_registry.json` (file KB, §13) — chỉ 4 field (`end/review_date/status/end_or_trigger`), chỉ qua `on_answer` đã validate, ghi nguyên tử. Nếu muốn siết thêm thì bỏ action này khỏi `ACTIONS`.
5. Câu risk=money kèm `on_answer` bị TỪ CHỐI lúc ghi (heuristic từ khoá: plan/lệnh/order/bot_stop/margin/park/live/bán/mua/NAV/…); ca bắt nhầm ⇒ đặt `"risk":"normal"` tường minh. Đo trên bus thật: `surface_question.py --list` xếp `nav-loss-brake-review-20261113` và `fleet-backup-gh001-history-rewrite` = money, `pnj-bctc-q3-review-trigger` = normal.
6. Sửa thiết kế so với DESIGN, có lý do: nhãn option tường minh chỉ khi MỌI option i bắt đầu bằng đúng chữ cái i (bus thật có option kiểu `A merge ngoài giờ` không dấu hai chấm); va chạm thẻ 6 hex ⇒ hỏi lại thay vì đoán; outcome không tác dụng phụ (ignored/no_binding/error) KHÔNG ghi `processed` để đổi cấu hình rồi gửi lại vẫn xử lý; money regex nhận `bot-stop`/`trading rules` (gạch nối) — bản đầu bắt hụt `bot-stop-policy`, selfcheck bắt được.
7. Bước 7 DESIGN §6 (lưới đối soát hằng ngày: số tin khớp ngữ pháp mà không ràng buộc được…) CHƯA làm — ngoài danh sách bước được giao; log thô đã có sẵn ở `state/decision_inbox/raw/<ngày ICT>.jsonl` để làm sau.
8. **Hệ quả khi merge**: `daily_retro.sh` 00:30 sẽ chạy `classifier_denial_count.py` cho ngày vừa qua. Đo hôm nay 13/11: Mike 8, Taylor 3, Wags 0, `close_bus_question` bị chặn 2 (`python3 bin/classifier_denial_count.py --day 2026-11-13`) ⇒ vượt ngưỡng (Mike>5) ⇒ retro đêm 13→14/11 sẽ gọi `retro_escalate.py --pattern classifier-denials-mike` (đúng thiết kế; có thể ra 1 câu hỏi relay cho user).

## Lệnh tái lập
```
cd /home/trido/thanhdt/WorkingClaude/wt-decision-inbox-20261113 && export MIKE_BOT_TEST_MODE=1
for s in bus_question_closure decision_inbox decision_actions classifier_denial_count surface_question decision_inbox_cog; do
  env -u TZ python3 bin/${s}_selfcheck.py | tail -1; TZ=America/New_York python3 bin/${s}_selfcheck.py | tail -1; done
git diff --numstat master...HEAD
```

## Vòng 2 (13/11) — sửa 7 mục arch-review NEEDS_CHANGES
Nhánh `feat/decision-inbox-20261113`, commit `03187c254` (trên `2b17704de`). KHÔNG merge, KHÔNG đụng .env/settings/hooks/service, shadow vẫn mặc định, fail-closed giữ nguyên.

| # | Lỗi (reviewer tái hiện) | Cách sửa | Ca đối kháng (r2) |
|---|---|---|---|
| 1 | 'ạ','à','é','ê','đ' → A/A/E/E/D vì bỏ dấu cả chữ cái | `_letter_is_ascii`: token cuối của text GỐC phải `[A-Ha-h]` | 'Duyệt ạ','ok ạ','Chốt à','chốt ạ!','à','pa ạ','é','ê','đ','ok đ' = None |
| 2 | reply vào tin lạ rơi xuống T2/T3; T1 không xét thẻ | `_bind` trả 4-tuple; có reference ⇒ quyết ở T1: tin lạ ⇒ no_binding, trỏ câu đã đóng ⇒ hỏi lại (`reply_target_closed`), thẻ ≠ câu được reply ⇒ nhập nhằng | reply 'Duyệt A' vào tin 999; Q1 đóng + Q2 cùng thread, reply 'B' vào tin Q1 ⇒ Q2 không đóng, on_answer không chạy |
| 3 | T3 bám câu surface cũ bất kỳ | T3 chỉ khi tin bot GẦN NHẤT của channel là tin có thẻ của câu đó (cog ghi `state/decision_inbox/last_bot/<chan>.json` mọi tin bot, kể cả không thẻ; thiếu con trỏ ⇒ fail-closed) + `THREAD_TTL`=6h | surface 30 ngày trước; 'A' sau tin bot không thẻ; +7h không đóng / +5h đóng; thiếu con trỏ; bot channel khác |
| 4 | `\b` coi `_` là chữ ⇒ `capit_margin…` lọt; thiếu từ khoá; `risk:normal` hạ DollarBill | chuẩn hoá `_`/`-`→khoảng trắng trước regex; thêm tien/rut/nap/sell/buy/stop loss/capit/don bay/leverage/broker/dnse/approve; DollarBill/Mafee luôn money | capit_margin_lever_reenable, excluded_tickers_pnj, stop-loss-tv1, 'Sell HPG', 'Rút tiền thật … SpaceX 500tr', … = money |
| 5 | note `--clear` / `--set x` thành cờ của remember.sh | validate: note (remember) và message (notify_thread) không được bắt đầu bằng '-' (kể cả sau khoảng trắng). remember.sh KHÔNG hỗ trợ `--` ⇒ không thêm | `kb/memory/Mike.md` (tmp) nguyên byte với '--clear','--set x',' --clear','-x'; đối chứng note thường vẫn ghi |
| 6 | cog timeout 30s < tổng timeout script; kill không dọn con; lỗi chỉ log; mất on_answer im lặng | timeout nội bộ hạ (30/45/15/5×30) ⇒ `SCRIPT_BUDGET_S`=240s, cog mặc định budget+60=300s; `start_new_session`+`killpg`; `record_error` ⇒ `errors.jsonl` + bus `status decision-inbox-error`; `intents.jsonl` ghi TRƯỚC khi đóng, `done` sau; intent không `done` ⇒ báo `intent_orphan` 1 lần (KHÔNG tự chạy lại on_answer) | kill giả lập (KeyboardInterrupt) giữa đóng và on_answer; timeout/rc/JSON hỏng của cog; killpg diệt tiến trình con |
| 7 | payload leo thang classifier chỉ có số đếm | thêm summary, options A:/B: (DESIGN §8), recommendation, risk=normal | sandbox stub classifier_denial_count.py + retro_escalate.py: 3 nhánh (vượt ngưỡng Mike, close_bus_question bị chặn, dưới ngưỡng ⇒ không escalate) |
| thấp | khoá `on_answer` escape `\u005f` lách validate lúc ghi; dispatch_bg thiếu `--no-followup` | `append_event.sh` validate cả khi payload có `\u`; thêm `--no-followup` | E7 + R1 trong decision_actions_selfcheck |
| thấp (chưa làm) | retention cho state jsonl | — | `surfaced/processed/asked/actions/intents/errors.jsonl` + `raw/` chỉ tăng; cần cron dọn riêng nếu bật live lâu |

### Số selfcheck THẬT (`env -u TZ` và `TZ=America/New_York`, MIKE_BOT_TEST_MODE=1)
Trước = selfcheck vòng 2 chạy trên code HEAD `2b17704de` (git archive); sau = nhánh `03187c254`. Hai TZ cho cùng kết quả.

| selfcheck | trước | sau |
|---|---|---|
| decision_inbox_r2_selfcheck (MỚI, mục 1-6) | 17/77 (60 FAIL) | 77/77 |
| decision_inbox_selfcheck | 84/85 (1 FAIL: DollarBill+normal) | 85/85 |
| decision_actions_selfcheck | 64/66 (E7, --no-followup) | 66/66 |
| decision_inbox_cog_selfcheck | crash tại 5b (không có con trỏ) | 30/30 |
| daily_retro_measured_by_selfcheck (mục 7) | 57/67 (10 FAIL) | 67/67 |
| surface_question / classifier_denial_count / append_event / retro_escalate / daily_retro_failcause | — | 10/10 · 12/12 · OK · OK · 8/8 |

Sửa test cũ (ngữ nghĩa đổi có chủ đích): "risk explicit normal" nay dùng agent Taylor (DollarBill ⇒ money); test 2 (TTL hỏi-lại 24h) chuyển sang đường reply-to vì T3 nay có TTL 6h.

### File chạm
`bin/decision_inbox.py`, `bin/decision_actions.py`, `ccdb_cogs/decision_inbox_cog.py`, `bin/daily_retro.sh`, `bin/append_event.sh`; selfcheck: `decision_inbox_r2_selfcheck.py` (mới), `decision_inbox_selfcheck.py`, `decision_actions_selfcheck.py`, `decision_inbox_cog_selfcheck.py`, `daily_retro_measured_by_selfcheck.sh`.

### Lưu ý còn lại
- Cog mặc định giờ giữ `_lock` tối đa 300s khi script treo (trước 30s) — đổi lấy việc không giết giữa đóng↔on_answer.
- Intent mồ côi chỉ BÁO, không tự chạy lại: không biết câu đã đóng đúng lựa chọn đó chưa.
- Đo bằng: các lệnh selfcheck trên + `git diff --stat 2b17704de 03187c254`.
Vòng 2 thêm: `decision_inbox_r2_selfcheck` vào vòng lặp trên + `bash bin/daily_retro_measured_by_selfcheck.sh`; số dòng `git diff --numstat 2b17704de 03187c254` = +557/−58 (10 file).
