# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-03 (sau khi user duyệt xử lý 5 việc treo từ báo cáo "vấn đề đang treo trong vận hành")

## 2026-08-03 — 6 việc user duyệt, đã xử lý xong trong phiên
1. Deposit rate 1.A: chốt 6.8% cho cả 4 Big-4, đóng câu hỏi Winston.
2. LAG fidelity (INCONCLUSIVE lần 3): dispatch Taylor (opus/high, job Taylor_20260803_021414, --bg)
   nghiên cứu sâu + lên plan tách edge thật khỏi hiện vật fill-model — CHƯA có kết quả lúc viết
   note này, cần kiểm tra job status khi quay lại.
3. Weekly KB editorial + Pattern-2 cron-confirm: ĐÃ XONG — root cause tìm ra (Friday 07-31 review
   KHÔNG BAO GIỜ chạy thật, bug quoting y hệt guidelines §15 trong kb_nightly.sh Phase 5, đã fix
   trước đó bởi 45f5c5d0 nhưng chưa xác nhận lại) → tự làm catch-up review đầy đủ 11 mục, sửa 4
   gap thật (model-ladder KNOWLEDGE.md lệch, 2 file thiếu SUPERSEDED-BY, context_execution_mini.md
   thiếu P1 domain-constraint, context_dataops_mini.md sai ticker_prune→universe_pit), đóng 2 bus
   question. Ghi opus-drift 74.2% vào KNOWLEDGE.md (chính đáng, theo dõi tuần sau). retro-pattern-
   recurring-silent-cron-spof-2 CÒN PENDING (mới 1 chu kỳ sạch, cần 3-5 ngày).
4. /api/notify UTF-8 bug: ROOT CAUSE THẬT tìm ra + FIX (không chỉ tìm sender) — surrogateescape
   round-trip trong notify_discord.sh/notify_thread.sh dưới minimal locale. Verified live (HTTP
   200 thay vì 500). Commit cacbfb9c. Riêng: bridge ccdb-mike.service đang chạy CODE CŨ (start
   07-31 15:17, trước fix ca0fde9 07-31→08-02 06:01 UTC) — restart cần user duyệt (ảnh hưởng mọi
   session), CHƯA làm.
5. wakeup_profile.py: verify an toàn (selfcheck PASS kể cả SIGKILL + TZ lạ), đã wired nightly từ
   lâu (kb_nightly.sh Phase 4.7) — gap thật là dispatch.sh's PRINTED hint vẫn ladder cũ, đã sửa để
   đọc bucket thật + fallback an toàn. Verified live (Taylor|opus|high→565s, Winston|default|
   medium→340s, corrupt-file fallback OK). Commit 84183462.
6. Wags coordination gap (concurrent wholesale git-add): fix TRỰC TIẾP — thêm bước "COMMIT AN
   TOÀN" (git status trước git add, chỉ add đúng file mình sửa) vào CẢ wags_autofix.sh VÀ
   ops_autofix.sh (cùng root cause class). Commit 3d16a976.

## Phát hiện phụ (không phải task được giao, tự thấy trong lúc làm)
- `Winston/ops-autofix-unresolved: run-bot-fail-ZaloPay-2026-08-03` — KHÔNG PHẢI bug (gate đúng
  thiết kế, chặn mua DHD vì plan chưa duyệt) — ĐANG được xử lý ở 1 thread/phiên KHÁC ngay lúc
  này (Taylor job điều tra thanh khoản DHD), không trùng lặp xử lý.

## Việc treo sang mai (ưu tiên)
- Kiểm tra kết quả job Taylor_20260803_021414 (LAG fidelity research plan) khi quay lại.
- Bridge ccdb-mike.service restart để nhận fix ca0fde9 — hỏi user trước khi làm (ảnh hưởng mọi session).
- retro-pattern-recurring-silent-cron-spof-2 — cần thêm 2-4 ngày xác nhận sạch liên tục.
- opus-drift 74.2% — xem lại tuần sau có giảm về baseline sau khi saga discord-routing đóng không.
- Kế thừa cũ (không mới): funding_required residual risk; PNJ TTL anomaly_flags (~08-23 review);
  coding_guidelines.md 39KB gần chạm ngưỡng 40KB (mới phát hiện hôm nay, theo dõi).

