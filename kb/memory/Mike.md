# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cuối ngày 2026-08-22)

### Go-live V2.4 lever HOÀN TẤT — hiệu lực T2 24/08
- fill_timing (fill_timing_live_gate + hybrid_live_gate) → FALSE cho SpaceX + ZaloPay
- extreme_regime_enabled → TRUE cho SpaceX + ZaloPay
- capit_margin_lever.enabled → TRUE (user confirmed 08-22)
- CAPIT margin lever: mỗi ngày có leveraged CAPIT orders phải chạy
  `approve_margin_day.py --account <acct> --date <date> --approved-by "John"` trước khi bot chạy —
  lever chỉ fire khi capit_signal_today AND dd52<=-20% AND approval file tồn tại.

### R&D — TẤT CẢ đã đóng, không còn backlog mở từ tuần này
- A1/A2 (rate-regime × parking, forward-horizon matrix): KHÔNG đổi production, radar giữ DISPLAY-ONLY.
- B1 (BAL exit DT candidate), B2 (breadth vs radar), B3 (CAPIT radar-band guard): cả 3 NO-GO/ARCHIVE.
  capit_base() giữ nguyên. Breadth-tercile PIT (không phải radar) là trục 2 mặc định mới (đã ghi
  kb/canonical.md, user duyệt 08-22).
- Taylor_20260822_153901 (B2-ext, alpha vs breadth-tercile) đang chạy lúc cuối ngày — kiểm kết quả
  khi vào phiên tiếp theo (bus finding "b2-alpha-breadth-20260822" — REFUTE, đã có kết quả rồi,
  không cần chờ thêm).

### Retro 2026-08-22 — XONG, đã đóng đúng
- File: kb/incidents/retro/retro-2026-08-22.md. 4 sự cố: #1 weekly report có 2 nội dung lỗi thời
  (CÒN HỞ — cần user quyết có gửi đính chính không), #2 insider_flags cron-env (đã đóng),
  #3 wags-fix-not-confirmed coord-2026-08-21 (đã đóng thật bằng commit 13f7bd591 — draft ban đầu
  từng báo sai "còn hở", Wags GAPS FOUND sửa lại, escalation sai đã đóng bằng answer event),
  #4 ScheduleWakeup MISS 10% (dao động, chưa cần escalate).
- 3 pattern xuyên suốt CHƯA có gate cơ học: (1) report nội dung lỗi thời không tự xoá, (2) cron-env
  câm lặng đường lỗi (lần 3), (3) ScheduleWakeup MISS dao động 8-27% (lần 4). Đề xuất formalize
  Pattern 2 vào coding_guidelines nếu tái diễn lần 4.

### Việc còn hở
- Weekly report 08-17→08-21 đã gửi có 2 nội dung sai (breadth ticker_prune, limitation egg lỗi
  thời) — CHƯA đính chính, chờ user quyết (retro #1).
- expvol_pacing: 1/25 order-day (cần Taylor điều tra — chưa dispatch).
- order_book_execution_shadow: 0/40 outcome coverage.
- wake_debounce_selfcheck.sh vẫn ghi fixture vào logs/wake_thread_errors.log (nợ kỹ thuật nhẹ,
  không còn gây báo động giả vì daily_retro.sh đã ngừng đọc file đó).

### Signal holds — KHÔNG tự đổi
- VPI/BAL: HOLD đến 2026-09-16.
- SpaceX + ZaloPay: HOLD_ALL (theo VPI hold).

### probe_linger_live_gate: vẫn True (paper-only)

- [2026-08-23T02:46:10Z] 2026-08-23 09:50 ICT: user nêu ý tưởng bổ sung PTKT đơn mã 'post-shock base formation' (giảm mạnh→vol cạn→ổn định, rating không sập). Mike trả lời: playbook §3 T2 đã có dạng văn xuôi chưa đo; đề xuất 1 prereg Taylor (event DD≥25%/≤20 phiên, base K phiên, 3 cách entry, fwd 60/120/250, survivorship-safe). CHỜ user gật mới dispatch.
- [2026-08-23T02:57:10Z] 2026-08-23 09:57 ICT: user gật GO cho prereg post-shock base formation. Đã dispatch Taylor_20260823_025658 (opus/high, timeout 5400s). Chờ ScheduleWakeup poll.
- [2026-08-23T03:30:00Z] 2026-08-23 10:29 ICT: postshock-base-formation-20260823 XONG — INCONCLUSIVE/nghiêng REFUTE. Mẫu hình PTKT thuần hình dạng giá KHÔNG có edge (excess vs VNI âm cả 3 horizon, 0/12 BH). Lỗi construct validity lớn: filter speed<=20phien loại sạch 10/10 case chủ chốt playbook (khủng hoảng VN thật sập chậm 40-60 phiên). RATING_BAD n=3 quá mỏng, câu hỏi gốc (rating là discriminator chính) KHÔNG kiểm định được. Khuyến nghị Taylor: đóng sổ hướng PTKT-thuần-hình-dạng; SỬA playbook §3 T2 (từ 'tín hiệu' → 'kỷ luật chia tranche') CẦN USER DUYỆT trước khi apply — CHƯA làm. Đã post đầy đủ lên Discord.
- [2026-08-23T03:36:09Z] 2026-08-23 10:35 ICT: user duyệt khuyến nghị Taylor về postshock-base-formation. Đã sửa playbook §3 T2 (calculated_fear_state_backstop.md), commit 826d7473, ghi bus answer. Hướng PTKT-thuần-hình-dạng-giá ĐÓNG SỔ.
- [2026-08-23T03:46:45Z] 2026-08-23 10:47 ICT: user duyệt tạo agent fundamental-skeptic (KHÔNG tạo agent PTKT). Đã viết ~/.claude/agents/fundamental-skeptic.md + đăng ký MIKE.md commit a00c8a72. Sẵn sàng dùng cho case fear-buy/special-situation tiếp theo.
- [2026-08-23T03:53:36Z] 2026-08-23 10:56 ICT: user báo quant-skeptic/Wendy(legal-vn) không gọi được. Root cause tìm ra: 7 agent native (bq-analyst/corp-scanner/data-ops/fleet-scout/legal-vn/quant-skeptic/risk-auditor) + fundamental-skeptic đều THIẾU field 'name:' trong frontmatter ~/.claude/agents/*.md — chỉ arch-reviewer có nên chỉ nó gọi được. Đã sửa cả 8 file (thêm name:), KHÔNG phải git repo nên không cần commit. Test lại fleet-scout ngay sau sửa vẫn 'not found' → registry Agent tool nạp 1 lần lúc session start, CẦN PHIÊN MIKE MỚI mới có hiệu lực. VIỆC CẦN LÀM Ở PHIÊN TIẾP THEO: thử gọi lại 1 agent (vd fleet-scout hoặc quant-skeptic) để xác nhận fix work, báo user. Không ảnh hưởng Taylor/DollarBill/Mafee/Wags (dispatch.sh, cơ chế khác). Team status lúc kiểm tra: Taylor/Wags khoẻ, DollarBill/Mafee idle ĐÚNG kỳ vọng theo signal hold, 0/16 circuit breaker trip, 2 job maxturns_pending cũ (08-21) không chặn gì.
- [2026-08-23T04:00:51Z] 2026-08-23 11:01 ICT: Restart Mike XONG. Bug thiếu field name: đã fix có hiệu lực — 8 agent native (bq-analyst/corp-scanner/data-ops/fleet-scout/fundamental-skeptic/legal-vn/quant-skeptic/risk-auditor) đều xuất hiện trong Agent tool registry và gọi được (smoke-test quant-skeptic PASS). Đã báo Discord. Việc này ĐÓNG.
