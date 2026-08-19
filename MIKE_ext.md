# MIKE_ext — mục dùng THEO TÌNH HUỐNG, tách khỏi `MIKE.md` (OKF, 2026-08-19)

> Tách ra để `MIKE.md` (auto-load MỖI phiên) ở dưới ngưỡng cứng 40KB. File này **KHÔNG auto-load**
> — đọc bằng `Read` đúng mục khi rơi vào tình huống nêu ở bảng con trỏ đầu `MIKE.md`.
> Nội dung dưới đây là **nguyên văn** phần đã cắt, không nén, không sửa nghĩa.

## Luật khớp topic con của `rollup_of` (escalation TỔNG)

**Luật khớp topic con — ĐỌC TRƯỚC KHI VIẾT `rollup_of`** (siết ngày 2026-08-16, commit
`d65167a9` + arch-review; trước đó khớp lỏng hơn nên tài liệu cũ nói sai):
- Topic con phải viết **ĐÚNG NGUYÊN VĂN** topic câu hỏi con. Cắt cụt / thêm / bớt là KHÔNG
  khớp. (Khớp substring đã bị bỏ: nó cho MỘT decision thoả nhiều topic con cùng lúc, đóng oan
  cả escalation tổng trong khi con vẫn đang chờ user.)
- Viết `"topic-con"` hay `"Mike/topic-con"` đều được, và khớp được với cả 2 dạng ở phía đóng —
  **CHỈ khi câu hỏi con là của CHÍNH người đăng escalation tổng.** ⚠️ **Sub trần thuộc agent
  KHÁC người đăng tổng thì KHÔNG khớp** (chốt 2026-08-16, arch-review round 4 sau `8e9affc3`/
  `522e29d2`) — `_same_ref` gán sub trần cho agent đăng TỔNG, trong khi `close_bus_question.py`
  (công cụ đóng chuẩn tắc) LUÔN ghi `resolves:["Agent/topic"]` đầy đủ ⇒ không bao giờ khớp, tổng
  kẹt pending vĩnh viễn. Đây là hình thái PHỔ BIẾN NHẤT (Mike đăng tổng cho sub của Wags/Taylor/...)
  nên **luôn viết dạng đầy đủ `Agent/topic-con` khi con không phải của chính bạn** — đừng dựa
  vào "cả 2 dạng đều được" cho ca này. Ràng buộc agent chỉ áp khi phía đóng **khai tường minh**
  một agent: `resolves:["Taylor/x"]` KHÔNG đóng được câu hỏi con `Mike/x`. Còn một `answer`/
  `decision` chỉ đơn giản dùng lại topic `x` thì agent nào đăng cũng được — đó là quy ước đóng
  câu hỏi có sẵn của bus (người đóng thường khác người hỏi), không siết ở đây.
- Tiền tố chỉ được hiểu là agent khi nó là **agent-id CÓ THẬT** trên bus. Nên topic tự nó
  chứa `/` — ví dụ `selfcheck-red: mike/bin/job_cancel_guard_selfcheck.py` — là topic TRẦN,
  cứ chép nguyên văn, không phải escape gì.
- Phần tử **rỗng hoặc không phải chuỗi** trong `rollup_of` ⇒ fail-closed CẢ câu hỏi tổng (nó
  KHÔNG bị lọc bỏ im lặng rồi chốt trên số con ít hơn bạn khai). Gõ thừa dấu phẩy thì tổng ở
  lại pending — an toàn, và dòng gợi ý bên dưới sẽ nói ra.
- Tổng không tự đóng được thì `ops_health_check` in thêm một dòng `[WARN-ONLY]` liệt kê
  **đúng topic con nào chưa khớp** — đọc dòng đó trước khi đi tìm nguyên nhân.
- Con được tính là đã đóng khi có `answer`/`decision` **trùng khít topic**, hoặc một event
  khai `resolves` chứa topic đó (khuôn `bin/close_bus_question.py`) — đăng SAU câu hỏi tổng.
- ⚠️ Đóng con theo **quy ước hậu-tố trạng thái** (`<topic>-question-closed`, `-CONFIRMED`…)
  đóng được CHÍNH câu hỏi con, nhưng **KHÔNG tính cho rollup** — tổng sẽ vẫn pending. Muốn
  đóng tổng thì tự đăng `answer` giữ nguyên topic tổng. Đây là lựa chọn có chủ đích: hướng
  lỗi này chỉ tốn 1 job `wags_autofix` thừa, còn nới ra thì nuốt mất quyết định của user.
- `rollup_of` tới nay **chưa có lần dùng thật nào trên bus**, nên lần escalation TỔNG đầu tiên
  phải tự kiểm tận nơi (`bin/bus_question_audit.py` xem tổng có tự đóng không), đừng tin
  cơ chế đã chạy đúng.

## Tạo / thu agent con

- Tạo: `bin/spawn_child.sh <id> "<role>" "<mô tả>"` → dựng `agents/<id>/` (CLAUDE.md + hooks),
  seed registry idle. Sau khi OAuth claude.ai hợp lệ: `systemctl --user enable --now mike@<id>`.
- Thu: `systemctl --user disable --now mike@<id>` (tri thức đã ở KB, không mất). Giữ `agents/<id>/` để audit.

## Giám sát sức khỏe fleet (auto-recovery cho nhân viên)
`bin/watchdog.sh` (cron 10') giám sát mọi unit `mike@<id>` bằng `bin/is_serving.py` (oracle agent
có THỰC SỰ phục vụ session — mạnh hơn `systemctl is-active`, bắt được ca ZOMBIE host sống nhưng
không serving). DOWN → restart (persistent DOWN sau 3 lần → nghi OAuth logout). ZOMBIE →
`clear_bridge` + restart (plain restart không đủ, xem `kb/incidents/`). Alert qua `bin/notify.sh`
→ Telegram (dedup 300s, kill-switch `state/NOTIFY_OFF`). Bảng sức khỏe đầy đủ
(STATE/SERVING/CTX/uptime/streak): chạy tay `bin/fleet_health.sh`.
`bin/context_watch.py` + `bin/usage_watch.py` (cùng cron 10') canh độ dài hội thoại từng phiên
(auto-compact của Claude Code tự lo, Mike chỉ cảnh báo) và trần 5h usage CHUNG của tài khoản (ước
lượng, không phải API chính thức — cảnh báo sớm để giãn việc nặng, không tự resume hộ phiên
khác). **2 việc CHỈ con người làm tay** (restart không cứu): logout → `claude login`; zombie dai
dẳng → mở agent trong app Claude để re-pair.

## Context theo vai trò (role-scoped) — quy tắc ghi chép & bảo trì (thêm 2026-07-17)

**Nguyên tắc: mỗi agent chỉ import ĐÚNG phần việc của mình** (trước 2026-07-17 mọi agent import
y hệt `context_pack.md` toàn bộ domain — tốn token vô ích; chi tiết sự cố gốc ở
`kb/incidents/index.md`):

| Agent | File(s) import (qua CLAUDE.md, KHÔNG qua hook nữa — xem cost-opt #1b) | Vì sao |
|---|---|---|
| Taylor | `kb/context_pack.md` (full) + `coding_guidelines.md` | R&D xuyên domain, cắt sẽ mất thông tin; viết backtest/script thường xuyên |
| DollarBill | `context_safety_core.md` + `context_planning_mini.md` + `coding_guidelines.md` | Lập plan T+1 (KHÔNG cần backtest); sở hữu `bot_prepare_plan.py`/`golive_recommend_v23.py` nên cần guideline khi sửa |
| Mafee | `context_safety_core.md` + `context_execution_mini.md` + `coding_guidelines.md` | Thực thi plan-bound (KHÔNG cần chiến lược/backtest); sở hữu `trading_bot/{executor,brokers,...}.py` — §5 Idempotent Side Effects trích dẫn TRỰC TIẾP `executor.py` làm ví dụ chuẩn |
| Winston | `context_safety_core.md` + `context_dataops_mini.md` + `coding_guidelines.md` | Data-ops: cần bảng BQ/registry/DT5G-trap; thêm guideline 2026-08-01 sau khi Winston viết đúng bug TZ-assumption mà §16 dạy (`dt5g_writer_watch.py`) |
| Spyros | `context_safety_core.md` + `context_mini.md` | Risk-audit tần suất thấp: cần kill-switch + BQ cơ bản, không cần bespoke file |
| Wendy | `context_mini.md` | Legal-vn: gần như tự chứa, không chạm execution |
| Wags | `context_ops_mini.md` (không đổi từ cost-opt #1) | Fleet-ops thuần, 0 domain trading |
| Mike | `context_pack.md` (full) + `coding_guidelines.md` | Coordinator — cần toàn cảnh để định tuyến đúng; sửa fleet tooling thường xuyên |

`kb/context_safety_core.md` là file NHỎ dùng chung cho mọi agent chạm surface tiền thật (kill-
switch, banned tickers, human-in-the-loop, danh tính 2 account LIVE) — tách riêng để 1 fact an
toàn chỉ cần sửa ĐÚNG 1 chỗ, không lệch giữa nhiều bản sao.

**`kb/coding_guidelines.md` — 5/8 agent import (Mike/Taylor/DollarBill/Mafee/Winston, thêm Winston
2026-08-01), CHỦ Ý**: cả 5 sở hữu/sửa code sản xuất thường xuyên (cột "Vì sao" bảng trên). Đừng
tự ý bớt file này khỏi Mafee/DollarBill/Winston để "tiết kiệm token" mà không kiểm tra lại bảng
"File sở hữu" trong CLAUDE.md của agent đó — cả 3 sở hữu code chạm tiền thật hoặc gate production.
Wags cân nhắc thêm nếu autofix của mình tái phạm đúng loại lỗi guideline này nhắm tới (chưa cần,
lý do đầy đủ: git log file này).

**Tách OKF 2026-08-14** (user duyệt, sau 3 lần vượt ngưỡng 40KB): 11 mục dùng-theo-tình-huống
(§7/§8b/§10/§11/§13/§14/§15/§17/§18b/§22/§24) sang `kb/coding_guidelines_ext.md` — KHÔNG auto-load,
số hiệu § giữ nguyên, bảng con trỏ ở đầu `coding_guidelines.md`. ⚠️ Con trỏ đó **không được** đổi
thành `@`-import (đệ quy ⇒ nạp lại, mất sạch tác dụng tách); mục mới loại tình-huống thêm vào file
ext, đừng nhồi vào file chính.

**Quy tắc ghi chép — mở rộng nguyên tắc "ghi 1 lần đúng chỗ" ở trên:** khi tạo tri thức bền mới
(quyết định/kết luận/quy tắc), trước khi ghi vào `context_pack.md`/`canonical.md`, tự hỏi **"role
nào thực sự cần fact này khi làm việc?"** rồi sửa đúng (các) file role-scoped tương ứng CÙNG LÚC:
- Fact chạm tiền thật/an toàn (kill-switch, banned ticker, account LIVE mới) → `context_safety_core.md`.
- Fact riêng thực thi lệnh (broker quirk, settlement, executor bug) → `context_execution_mini.md`.
- Fact riêng lập plan (allocator, regime-gate, pricing rule, plan-file convention) → `context_planning_mini.md`.
- Fact riêng data-ops (bảng BQ mới, cron, cache) → `context_dataops_mini.md`.
- Fact chỉ Taylor cần (backtest method, R&D history) → giữ nguyên ở `context_pack.md`/`KNOWLEDGE.md`, KHÔNG cần lan sang các file role-scoped khác.
Fact liên quan ≥2 role — ghi vào MỖI file liên quan (chấp nhận trùng nhỏ, ưu tiên đúng hơn DRY
tuyệt đối cho nội dung an toàn-quan trọng), HOẶC nếu đủ nhỏ/nền tảng thì đưa vào
`context_safety_core.md` thay vì lặp nhiều file.

**Audit định kỳ — gộp vào Friday KB editorial review có sẵn** (không tạo cron mới, theo pattern
`coding_guidelines.md` §9/§10/§11): mục 5 trong dispatch Friday của `bin/kb_nightly.sh` yêu cầu
Mike đọc lại các file role-scoped, đối chiếu `KNOWLEDGE.md`/`current_ops.md` mới nhất — fact đã đổi
ở nguồn canonical nhưng chưa lan sang file role-scoped liên quan (vd đổi target NEUTRAL parking,
thêm account LIVE mới, đổi tên bảng DT5G) thì sửa ngay.

**Khi thêm agent mới hoặc đổi vai trò 1 agent:** chọn file role-scoped theo BẢNG trên (không mặc
định full `context_pack.md` trừ khi vai trò thực sự cần tổng hợp xuyên domain như Taylor/Mike) —
cập nhật cả bảng này khi quyết định.
