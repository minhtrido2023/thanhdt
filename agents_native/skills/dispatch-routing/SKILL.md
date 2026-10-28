---
name: dispatch-routing
description: Use EVERY time before calling bin/dispatch.sh, Agent(subagent_type=...), verify_finding.sh or arch-reviewer — and again when re-dispatching after an arch-review/verifier NEEDS_CHANGES verdict. Picks model and effort by task difficulty (read-only checkable lookups = Haiku; everyday work = Sonnet medium; hard work = Opus medium; adversarial review / money path / new design = Opus high, review the WHOLE thing then fix once) and applies the round-3 circuit-breaker that stops multi-round polish chains. Born from the 2026-10-02 token-cost audit (lag-exit 6 rounds, ATC UPCOM 4 rounds, ~2.6k Taylor turns in one day).
---

# Dispatch routing — chọn model/effort theo ĐỘ KHÓ, cắt vòng polish

Luật đầy đủ + lịch sử: `kb/mike_model_routing.md` (đọc khi cần chi tiết provider/drift/effort).
Skill này là checklist 1 phút TRƯỚC mỗi dispatch. `dispatch.sh` cũng tự in nhắc stderr
(`bin/dispatch_loop_hint.py`) khi thấy vòng ≥3 — thấy nhắc đó thì đọc lại mục 3.

## 1. Provider: mặc định `claude`. Mafee/DollarBill/Mike chỉ claude.
opencode chỉ còn cho `bin/second_opinion.sh` hoặc khi user chỉ định (từ 2026-10-11 không còn là đích của việc tra cứu). Chính sách codex 2026-08-16 không đổi (xem `kb/mike_model_routing.md`).

## 1b. Bốn tầng đời 5.5 (user duyệt 2026-10-11) — chỉnh effort trước, đổi model sau
| Tầng | Cờ | Việc |
|---|---|---|
| **0 Haiku** | native `Agent(...)` (fleet-scout đã ghim haiku); `dispatch.sh --model haiku` chỉ khi việc thật ngắn | CHỈ ĐỌC + ngắn (dưới ~30 lượt) + đầu ra kiểm được: trạng thái job/session, phân loại log/bus, smoke test, tra KB. KHÔNG: ghi code/KB, query BQ, phản biện, việc mà bỏ sót im lặng sẽ lọt. Qua `dispatch.sh` ngữ cảnh ≥ ~85K token/lượt nên Haiku chỉ rẻ hơn Sonnet ~4 lần, không phải 20 |
| **1 Sonnet** | omit (= sonnet 5.5, medium) | Việc thường ngày: báo cáo ngày/tuần/tháng, plan T+1, data-ops, query BQ, sửa đã biết đúng chỗ, áp `required_change`. Không hạ `low` |
| **2 Opus medium** | `--model opus` (trần lượt tự = 80) | Việc khó: R&D/backtest theo khuôn có sẵn, due diligence, tổng hợp nhiều nguồn, lỗi chưa rõ nguyên nhân |
| **2+ Opus high** | `--model opus --effort high` | Phản biện, chạm tiền/cổng an toàn, thiết kế backtest MỚI, lượt review toàn nhánh |
Không chắc → tầng 1.
**Siết 2026-10-18 (user duyệt, đo 86% chi phí tuần = Opus):** Opus CHỈ khi ≥1 dấu hiệu — phản biện/review toàn nhánh · chạm tiền/cổng an toàn · thiết kế MỚI chưa có đặc tả · lỗi chưa rõ nguyên nhân. Dựng tính năng THEO ĐẶC TẢ đã duyệt, vòng 2 áp `required_change`, sửa lỗi đã định vị, cron autofix/sweep, checkpoint paper, kiểm toán chỉ-đọc ⇒ **Sonnet/medium (omit)**. Opus/high CHỈ cho phản biện, chạm tiền/cổng an toàn, review toàn nhánh; Opus còn lại = medium. Thử tới 2026-10-25; luật + ngưỡng quay lại: `kb/mike_model_routing.md` mục "SIẾT LUẬT OPUS".
Từ 2026-10-11 11:50 ICT (user chốt) cả 8 agent ghi alias `sonnet` trong settings ⇒ omit ≡ `--model sonnet`, kể cả DollarBill / Mafee.
Native agent đã ghim model trong frontmatter (fleet-scout=haiku; bq-analyst/corp-scanner/data-ops/memo-optimizer=sonnet; còn lại=opus) — chỉ truyền `model` ở `Agent(...)` khi cần KHÁC tầng đã ghim.
🧪 "Opus mặc định medium" đang THỬ tới 2026-10-25 (số nền + ngưỡng quay về `high`: đầu file `kb/mike_model_routing.md`).
`ops_autofix.sh` và mọi cron ghim Opus: KHÔNG đổi.

## 2. Phân loại ĐỘ KHÓ (user chỉ đạo 2026-10-02)
| Chế độ | Dấu hiệu | Dispatch |
|---|---|---|
| **A — NHẸ** | sửa text/docstring/message, fix code nhẹ đã biết đúng chỗ, bổ sung test cho mutation ĐÃ nêu tên, áp `required_change` reviewer đã liệt kê, revert phần thừa, đồng bộ config/registry, dọn worktree | `--model sonnet --effort medium` (hoặc omit) |
| **B — MỚI/KHÓ** | thiết kế chưa có template, bug chưa rõ nguyên nhân, chạm production/tiền/cổng an toàn, review lộ lỗi MỚI khác loại vòng trước | `--model opus`, làm MỘT LẦN: (1) review TOÀN BỘ diff/nhánh + liệt kê đủ lỗi & mutation sống (`--effort high`), (2) sửa hết trong 1 dispatch (medium; `high` nếu chạm tiền/cổng an toàn), (3) arch-review xác nhận 1 lần |
| Fable | chỉ LÊN KẾ HOẠCH việc cực khó, không implement; tối đa `high` | hiếm; không chắc → Opus |
Không chắc A hay B → tự hỏi: "lỗi lần này CÙNG loại với vòng trước và reviewer chỉ rõ file:dòng?" Có ⇒ A. Không/ngày càng nhiều ⇒ B.

## 3. Cầu chì vòng (áp khi dispatch lại sau NEEDS_CHANGES)
- **TRƯỚC VÒNG 2: review TOÀN BỘ nhánh MỘT lần** (user chốt 2026-10-07, retro Pattern A phương án a) — reviewer liệt kê trọn bộ lỗi + mutation còn sống; vòng 2 sửa hết trong 1 dispatch. Áp cho cả `dispatch.sh` LẪN `Agent()` (cầu chì code không đếm `Agent()` — luật này là chốt chặn duy nhất ở đường đó).
- Vòng 1-2 cùng nhánh: chế độ A nếu `required_change` đã cụ thể.
- **Vòng 3 mà arch-review VẪN trả phát hiện MỚI ⇒ DỪNG polish, chuyển chế độ B** (Opus high review toàn bộ, sửa một lượt). KHÔNG dispatch vòng 4 kiểu cũ.
- Vòng ≥4 cùng nhánh/agent trong 24h: `dispatch.sh` tự CHẶN (exit 7). User duyệt ⇒ `DISPATCH_ROUND_CAP_OVERRIDE=1 DISPATCH_ROUND_CAP_REASON="user duyệt <giờ>: <vì sao>" bin/dispatch.sh ...` (lý do BẮT BUỘC — thiếu ⇒ vẫn exit 7) (chỉ phiên tương tác; honour system). Bị chặn ngoài phiên tương tác ⇒ bus event `round-cap-blocked`.
- Vòng **test-only** quá 2 ⇒ HỎI USER trước khi tiếp, nêu rõ mutation còn sống.
- Dặn arch-reviewer ngay vòng đầu: "liệt kê TRỌN BỘ lỗi và mutation còn sống, không dừng ở lỗi đầu tiên".

## 4. Ghi nhớ khác
- Prompt dispatch qua heredoc (skill `dispatch-prompt-heredoc`).
- Redispatch sau timeout/hết turn: giữ model gốc, effort `medium` trừ khi việc THẬT SỰ khó.
- Đo lại hằng tuần: `python3 bin/spend_report.py --days 7`.
