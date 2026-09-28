# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái cuối ngày 2026-09-28 (24:36 ICT)
- **Retro 2026-09-28 ĐÃ ĐÓNG** (`kb/incidents/retro/retro-2026-09-28.md`, commit `4305bbce`,
  Wags verify GAPS FOUND → đã sửa cả 2 gap). 3 sự cố: #1 ops_health_check check 5b agent↔reason
  mismatch (đã vá, §29 lần 3); #2 corp-action-daily VND (false-positive, đóng) / VNM exright_date
  lệch 1 phiên (bug thật, còn mở — cần dispatch Winston xác minh); #3 (TÁI DIỄN) classifier chặn
  Taylor headless merge production — **ESCALATE MỚI**
  `retro-pattern-recurring-classifier-blocks-headless-agent-production-write` (2 retro liên tiếp
  09-27→09-28, CHƯA có ai trả lời). Pattern A (bus-closure channel gap) lặp lần 2 ở
  `wags-fix-not-confirmed: coord-2026-09-28` — CHƯA escalate, lần 3 sẽ phải escalate.
- Dòng việc dep1m/pin-dải-2-số + close_repair Layer 2 + fail-open kiểm kê (đợt 1+2) +
  pinned_ledgers B0-B6 đều đã HOÀN TẤT + merge trong ngày 28/09 — không còn hạng mục treo từ
  các mạch đó.

## Còn mở (cần user quyết / chưa làm)
- Escalation classifier-block (xem trên) — chờ user chọn A/B/C (harness exception / đổi quy
  trình merge / chấp nhận chi phí runbook).
- VNM `exright_date` lệch 1 phiên trong `tav2_bq.corporate_action` — cần giao Winston xác minh
  metadata (Taylor đã đề xuất trong bus finding `vnd-vnm-uncomputable-not-fpt-class`, chưa dispatch).
- `Taylor/pnj-trong-ro-custom30v-live-can-user-duyet-chan` — chờ user chọn A/B/C cho PNJ trong
  rổ custom30V production (ack suppress 7 ngày, không cần nhắc gấp).
- Fail-open CÒN LẠI ngoài batch đã vá: `trading_bot/plan.py:1390/1787` + `executor.py` 5 handler
  CHƯA đọc hết (đợt-2 kiểm kê, ranh giới cứng — cần user ký từng site).
- `rating8l_icb_pit_selfcheck.py` MergeError dtype `<M8[s]` vs `<M8[us]` — tiền tồn, chưa ai sửa.

## Việc theo lịch
- T3 29/09 sáng: soát `logs/park_trim_daily.log`/`jit_unpark_daily.log` — lần đầu chuỗi cảnh báo
  rc≠0 chạy thật trên production sau batch vá fail-open 28/09.
- Xoá cron FiinPro sau 28/09 (đã qua hạn — làm sớm). Đóng AlphaLens 30/09 + ghi registry
  "PASS on N=1, không đủ bằng chứng sizing".
- Review quý: measurement-integrity audit ~2026-12-27; Bobby structural-risk ~2026-11-26.

## Bẫy đã ghi lại (đừng cắn lần nữa)
- Selfcheck neo bản cũ bằng `HEAD`/`main` ⇒ sau merge FAIL vĩnh viễn. Luôn neo `<commit-vá>^`.
- Selfcheck hardcode gốc canonical ⇒ chạy từ worktree test MASTER thay vì code đang sửa. Gốc
  mặc định phải suy từ `__file__`.
- Guard chống ghi-đè production OPT-IN thủ công không đủ an toàn — phải tự suy từ path/context.
- Đóng 1 `question` do AGENT KHÁC đăng lên bus vẫn cần 1 `answer`/`decision` ngắn TRÊN BUS, dù
  nội dung đầy đủ đã nằm ở KB/commit/finding riêng — pattern này đã lặp 2 lần (09-27, 09-28),
  lần 3 phải escalate.
- `git show <rev>:<path>` tính path từ GỐC REPO, `git diff … -- <pathspec>` tính từ CWD — nhầm
  1 cái làm cổng pre-commit im lặng cho qua. Dùng `:(top)` + `rev-parse --show-prefix`.
- Checker so sánh phải giữ quan hệ 1-1 với bằng chứng (không gộp 2 tập rời rồi in cạnh nhau) —
  §29 đã bắt lỗi này 3 lần (`55b3f34c`, `498466d9`, `e5825e11`, `f126e397`).
- `data/*.csv` ngoài version control ⇒ tên canonical ghi đè được, không tái lập số cũ — đã có
  `data/pinned_ledgers/` (B0-B6, 4 cổng pre-commit) chặn từ 28/09.

