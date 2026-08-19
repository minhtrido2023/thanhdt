# MIKE_ext.md — mục dùng theo tình huống (KHÔNG auto-load)

Đọc khi cần — tra bảng pointer trong `MIKE.md` §Mục đã tách để biết mục nào nằm ở đây.
Nội dung giữ nguyên 100%, chỉ chuyển sang file này để không nạp mặc định mỗi phiên.

⚠️ `MIKE.md` KHÔNG dùng `@`-import file này (đệ quy ⇒ nạp lại, mất sạch tác dụng tách).

---

## §Escalation TỔNG — rollup_of matching rules đầy đủ

**Escalation TỔNG (gom nhiều câu hỏi con đang mở) — bắt buộc khai `rollup_of`.** Câu hỏi tổng
có topic RIÊNG, nên đóng hết các câu hỏi con KHÔNG đóng được nó (`ops_health_check` check #5
khớp theo topic-string) ⇒ nó ở lại pending và đốt 1 job `wags_autofix` mỗi ngày cho tới khi ai
đó nhớ ra (ca thật `retro-escalation-2026-08-13-patternB-and-backlog`). Khai tường minh danh
sách topic con trong payload thì check #5 tự đóng tổng khi MỌI con đã đóng:
```bash
bin/append_event.sh Mike question "retro-escalation-<ngày>-..." \
  '{"summary":"...", "rollup_of":["topic-con-1","Mike/topic-con-2"], "urgency":"medium"}'
```
Không khai thì hành vi y như cũ (fail-closed) — vẫn phải tự đăng `answer` giữ NGUYÊN topic tổng.

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

---

## §Tạo / thu agent con

- Tạo: `bin/spawn_child.sh <id> "<role>" "<mô tả>"` → dựng `agents/<id>/` (CLAUDE.md + hooks),
  seed registry idle. Sau khi OAuth claude.ai hợp lệ: `systemctl --user enable --now mike@<id>`.
- Thu: `systemctl --user disable --now mike@<id>` (tri thức đã ở KB, không mất). Giữ `agents/<id>/` để audit.

---

## §Giám sát sức khỏe fleet

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

---

## §Context role-scoped — quy tắc ghi chép & onboarding

**Tách OKF 2026-08-14** (user duyệt, sau 3 lần vượt ngưỡng 40KB): 11 mục dùng-theo-tình-huống
(§7/§8b/§10/§11/§13/§14/§15/§17/§18b/§22/§24) sang `kb/coding_guidelines_ext.md` — KHÔNG auto-load,
số hiệu § giữ nguyên, bảng con trỏ ở đầu `coding_guidelines.md`. ⚠️ Con trỏ đó **không được** đổi
thành `@`-import (đệ quy ⇒ nạp lại, mất sạch tác dụng tách); mục mới loại tình-huống thêm vào file
ext, đừng nhồi vào file chính.

**Quy tắc ghi chép — mở rộng nguyên tắc "ghi 1 lần đúng chỗ":** khi tạo tri thức bền mới
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

**Khi thêm agent mới hoặc đổi vai trò 1 agent:** chọn file role-scoped theo BẢNG trong `MIKE.md`
§Context-theo-vai-trò (không mặc định full `context_pack.md` trừ khi vai trò thực sự cần tổng hợp
xuyên domain như Taylor/Mike) — cập nhật cả bảng đó khi quyết định.
