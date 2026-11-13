# Decision Inbox — user trả lời "Duyệt A" ở Discord → script xác định tự đóng câu hỏi bus (13/11/2026)

Lý do: lớp "auto mode classifier" (CCDB_PERMISSION_MODE=auto, `/workspace/ccdb-mike/.env`) chặn 73 lần trong 25 ngày, gồm `close_bus_question.py` — quyết định của user kẹt dù đã duyệt (ca nav-loss-brake-review-20261113). User duyệt triển khai 13/11 15:03 ICT.

## Trạng thái
- ĐÃ MERGE master `3ea2e6d62` (shadow mặc định). Cog CHƯA bật. Thiết kế: `agents/Taylor/research/decision_inbox_design_20261113/DESIGN.md`; triển khai + vòng 2: `agents/Taylor/research/decision_inbox_impl_20261113/REPORT.md`.
- arch-review: vòng 1 NEEDS_CHANGES (7 mục, đã sửa) → vòng 2 CONFIRMED (duyệt merge ở shadow). Selfcheck 2 TZ: r2 77/77, inbox 85/85, actions 66/66, cog 30/30, các bộ cũ OK. Mike tự sửa lỗi C (append_event chỉ validate payload JSON) + F (daily_retro báo escalate thất bại) trong commit `00813e24e`.

## Việc của USER để bật shadow (2 dòng .env + restart ~15s)
`CUSTOM_COGS_DIR=/home/trido/thanhdt/WorkingClaude/mike/ccdb_cogs` và `DECISION_INBOX_USER_IDS=<Discord user id>` trong `/workspace/ccdb-mike/.env`, rồi `systemctl --user restart ccdb-mike`. `DECISION_INBOX_MODE=live` chỉ sau 5 phiên shadow 0 sai + user duyệt.

## CHẶN BẬT LIVE (phải sửa trước `DECISION_INBOX_MODE=live`)
- A. `bin/decision_inbox.py:437-441`: action on_answer failed mà user vẫn nhận ✅ — phải `record_error('on_answer_failed')` + cảnh báo trong reply.
- B. `bin/decision_inbox.py:328-329`: reply vào tin làm rõ của bot kèm thẻ `#q…` bị `no_binding` im lặng — thẻ tường minh phải chuyển xuống T2 (sửa ca 2a' trong `decision_inbox_r2_selfcheck.py`).
## KHÔNG chặn, nên sửa
- D. MONEY_RE (`decision_inbox.py:54-56`) còn sót: parking, cắt lỗ, chốt lời, giải ngân, tỷ trọng, vị thế, tài khoản, SpaceX, ZaloPay, cổ phiếu, kill switch, cash, withdraw, deposit, position, exposure; `risk:"normal"` vẫn hạ được câu money của Taylor/Wags/Mike; bỏ gợi ý "đặt risk normal" ở `decision_actions.py:262`.
- E. `_report_orphan_intents` (`decision_inbox.py:445-461`) post không giới hạn ⇒ SCRIPT_BUDGET_S không là trần thật.
- G. Retention state jsonl (`surfaced/processed/asked/actions/intents/errors.jsonl`, `raw/`) chưa có.
- Chưa làm: DESIGN §6 bước 7 (lưới đối soát hằng ngày), quy ước Mike dùng `surface_question.py` (thẻ `[#q…]`) khi hỏi user.

## Hệ quả đã LIVE từ merge
`daily_retro.sh` đêm 13→14/11 chạy `classifier_denial_count.py` (Mike 8, close_bus_question bị chặn 2 ngày 13/11 ⇒ vượt ngưỡng ⇒ gọi `retro_escalate.py --pattern classifier-denials-mike`, payload đã có summary/options/recommendation).
