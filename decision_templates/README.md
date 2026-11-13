# decision_templates/ — prompt cố định cho `on_answer` → `dispatch_bg`

Một action `{"action":"dispatch_bg","target":"Taylor","template":"<tên>"}` trong payload câu hỏi bus
chỉ được phép trỏ tới file `<tên>.md` Ở ĐÂY (tên `[a-z0-9_]+`). Nội dung file = prompt dispatch; KHÔNG nhận
text tự do từ payload (để LLM viết câu hỏi không tự cấp được quyền chạy việc tuỳ ý).

- target hợp lệ: `Taylor`, `Winston`, `Wags`. **Cấm** `Mafee`, `DollarBill` (đặt lệnh/plan thật).
- Thêm template = một commit có người duyệt; template không tồn tại ⇒ `append_event.sh` từ chối ghi câu hỏi.
- Thiết kế + whitelist đầy đủ: `bin/decision_actions.py` (docstring) và
  `agents/Taylor/research/decision_inbox_design_20261113/DESIGN.md` §4.
