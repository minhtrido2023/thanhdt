# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI. Plan T+1 2026-09-14 (cả SpaceX+ZaloPay) đã HOLD_ALL đúng.

## CẦN THEO DÕI — DGC NAV ZaloPay stuck (2026-09-11, CÒN MỞ)
`Mafee/nav-price-xcheck-stuck-ZaloPay-2026-09-11` — gap 20,6% (close_price BQ 46.750 vs marketPrice
broker 38.750), quá cutoff 21:15 ICT. Trùng thời điểm DGC GDKHQ cổ tức 8.000đ/cp hiệu lực 14/09
(3 phiên sau, CHƯA qua ex-date) — KHÔNG kết luận nguyên nhân, cần Winston/Mafee verify DNSE trực
tiếp trước phiên 14/09. Nguyên nhân gốc thứ 5 (khác 4 nguyên nhân đã đóng bằng c30e0580 09-10).
Retro: `kb/incidents/retro/retro-2026-09-11.md`.

## Selfcheck đỏ MỚI — commit_collision_gate_selfcheck.py (2026-09-11, CÒN MỞ)
Wags tự phát hiện + triaged-needs-human (suppress 14d). Root cause đã xác định qua review
2026-09-12: test #12 "incident record present for replay" tham chiếu cứng 1 job file cụ thể
(`bus/jobs/Wags_20260812_035748.json`) đã bị dọn/rotate khỏi đĩa — fixture fragile phụ thuộc
state bên ngoài, KHÔNG phải production logic hỏng (43/44 test khác PASS). Cần Wags (chủ sở hữu)
tự sửa test dùng fixture tự chứa thay vì tham chiếu job thật có thể bị rotate.

## AMH (Adaptive Market Hypothesis) — ĐÓNG HẲN 2026-09-10
`kb/projects/amh-adaptivity-review-20260910.md` (mục 10 = INPUT cho review VPI/BAL 09-16).
KHÔNG WIRE GÌ. Đóng, đừng mở lại nếu không có dữ liệu ngoài mẫu mới.

## Bus question đang mở, CHỜ NGƯỜI (audit 2026-09-12, chỉ còn 2 — 3 mục cũ đã đóng 09-09)
1. `Mafee/nav-price-xcheck-stuck-ZaloPay-2026-09-11` — xem mục trên.
2. `Wags/selfcheck-red: mike/bin/commit_collision_gate_selfcheck.py` — xem mục trên.

## R&D đã ĐÓNG HẲN tuần 09-05→09-11 (đừng mở lại nếu không có dữ liệu ngoài mẫu mới)
- AMH 7 hướng (09-10) · CCS Phase 0-2 (09-05/06, 0/7 qua Phase 1) · BAL 5 vòng (09-09, NO-GO) ·
  custom30V 5 vòng (09-09, NO-GO — overweight bank = tác dụng phụ pool thanh khoản).
- CCS/8L accruals (09-06, NO-GO lần 3).

## append_event.sh JSON isolation — pattern lâu dài đã biết, KHÔNG escalate (18+ lần từ 07-11)
0 mất dữ liệu, agent luôn tự lành <60s, sidecar `bus/_rejected_resolved.jsonl` khử báo động giả.
Căn nguyên cấu trúc (Bash ad-hoc không lint được) vẫn hở nhưng chấp nhận được — theo dõi tần suất,
chỉ đáng xem lại nếu ≥2 ca CÙNG PHÁT SINH thật trong 1 ngày liên tục vài ngày.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm → §-mới tiếp theo phải tách sang _ext.md.

- [2026-09-11T21:10:50Z] weekly ops audit 2026-09-12 XONG (job Mike_20260911_204825): 3 bug that, 2 commit (9becc1b3 mike_paseo+ack fail-open, 97a60151 pattern ❌), 3 escalate. QUAN TRONG NHAT dang cho nguoi: 'Mike/report-return-gate-worktree-root-chan-bao-cao-nha-dau-tu' — report_return_gate.py:55 tinh ROOT sai trong worktree => cong ti suat §21 fail-closed => BAO CAO NHA DAU TU khong gui duoc (5 ca da xay ra). Bus question PENDING nay la 5.
- [2026-09-11T21:22:18Z] weekly ops audit 2026-09-12: bao cao da post day du vao Architecture o resume #1 (luot goc het max-turns truoc buoc post). 5 bus question PENDING, uu tien: report_return_gate worktree ROOT (client-facing) > DGC NAV gap ZaloPay (truoc 14/09) > hit_details_daily lech gio cron.
