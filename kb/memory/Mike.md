# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.
- T2 14/09 = ex-date DGC cổ tức tiền 8.000đ (ZaloPay). xcheck NAV tối 14/09 SẼ chặn theo kỳ vọng
  (46.750−8.000=38.750). Xử TAY theo kb/ops_runbook.md § PRICE_XCHECK, KHÔNG hỏi lại user.
  Cổ tức TIỀN = kỳ vọng (mark giá CUM); cổ tức CỔ PHIẾU/thưởng/tách = VẪN CHẶN, cần người.

## ⏰ VIỆC CỦA MIKE CHIỀU T2 14/09 ≥15:00 ICT — KHÔNG CÓ SCHEDULER, PHẢI TỰ NHỚ (cập nhật 13/09 12:55)
Batch 1: #3+#2 ĐÃ COMMIT WC 24df0f76 (cờ nav_include_egg_offbook OFF, arch APPROVE, quant-skeptic
CONFIRMED). Working tree trading_bot SẠCH (Mike verify). Chiều T2 sau phiên:
  1) apply /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/cq20260913_batch1_item1.patch
     (`git -C /home/trido/thanhdt apply <patch>`; apply --check OK trên 24df0f76 lúc 12:52). Chạy lại
     selfcheck ghi CUỐI patch (loan_package_multi_account 24/24 + quét rộng 50 file, test_trading_bot.py
     FAIL 'quota AAA' là có sẵn). Commit theo lệnh cuối patch. Hạn 21:00 T2.
  2) dispatch Wags quét ~28 file bin/*.py dirname×3 → wc_paths.
  3) xem kết quả Taylor điều tra rò 1258 SpaceX (job dispatch 13/09 ~12:55, read-only) — nếu có
     script gọi broker thiếu loan_package_id ⇒ fix cùng lúc apply patch #1.
ĐÍNH CHÍNH ĐÃ BÁO USER: (a) #2 get_nav là ĐƯỜNG CHẾT (strategy v23, 0/148 plan 2026) — không ảnh hưởng
sizing thật, Mike từng nói sai '~10%'; (b) ZaloPay loan_package None = default creds 1258, lệnh TV1
thật MANG 1258 (thiếu = HTTP 400). Rò thật đã xảy ra 08-11: ZaloPay tra gói theo 1841 của SpaceX 13
lần (bot_execute nhiều account 1 tiến trình); SpaceX 08-11→14 tra theo 1258 (chưa rõ nguồn).
Chờ user: giữ cờ #2 OFF (Taylor+Mike khuyến nghị) hay gỡ hẳn đường v23/get_nav.

## Code-quality 09-13 — Batch 2+3 XONG, Mike verify 11:40 ICT
- Batch 3 (Taylor): WC b53d26b4 + mike 9a5a2723. fetch_new_listings loại false-positive thật DIH/VNH/HDG.
- Batch 2 (Wags): c9edd4c6 (NAV/report, arch-review 2 vòng) · 136a90d0 (dispatch.sh) · 767deb0e
  (selfchecks). Mike chạy lại: compute_active_nav ALL PASS, closure 19/19, park_trim 72/0, dispatch
  topic 42/42 + tiny 25/25 + hint 16/16, bash -n 3 script OK, $ROOT/.. đã hết trong dispatch.sh.
- HÀNH VI MỚI cần biết: compute_active_nav.py account 0 vị thế mà hôm trước có cổ phiếu ⇒ exit 5,
  KHÔNG ghi file (chống feed rỗng tạm thời ghi NAV thấp giả). Bán sạch THẬT ⇒ chạy tay --confirm-flat.
  Cron compute_active_nav_all.sh 20:15 ICT sẽ log rc=1 trong ca đó — không phải lỗi, là guard.
- Tồn nhỏ Wags ghi nhận: verify_account_snapshot.py:390 cùng lỗi ngày giá mã đầu alphabet;
  kb/events_buffer.md.tmp chưa .gitignore; ops_runbook chưa ghi --confirm-flat; c/e mới harness chưa
  selfcheck bền.

## Retro 09-12 đóng (50f7cb2a). Pattern worktree lệch canonical TÁI DIỄN LẦN 3 — gặp lại ⇒ escalate.
## Còn mở không khẩn: ~28 file bin/*.py dirname-x3; job_cancel_guard nhánh systemd luôn đỏ dưới cron.
## append_event.sh JSON isolation — pattern đã biết, không escalate.
## Sát ngưỡng OKF: kb/coding_guidelines.md 39,5KB/40KB — §-mới PHẢI tách _ext.md.

- [2026-09-13T05:28:26Z] 13/09 review ARIA (user gửi): đã đối chiếu, file agents/Mike/research/aria_review_response_20260913.md. 2 gap số liệu CHƯA ai theo dõi: reconcile_equity.py thiếu realized P&L (residual +2,41% SpaceX) + nav_history thiếu SpaceX 6 phiên/ZaloPay 5 phiên. Chờ user chọn A-E.
- [2026-09-13T05:33:51Z] 13/09 12:35 user duyệt review ARIA: A (Taylor realized P&L + backfill nav_history, job mới nhất Taylor_20260913_0533xx) + A3 (Spyros_20260913_053332 risk-metrics T8) + C (Wags production_manifest). B: mike_paseo = mirror cố ý, KHÔNG merge/xoá (đã ghi current_ops_ext). D/E không làm. Bước kế: đọc 3 finding → A1 qua quant-skeptic → cập nhật monthly report action #5.
- [2026-09-13T05:38:50Z] 13/09 12:40 A3 Spyros CONFIRM: risk metrics T8 khớp report (mọi delta <0,1pp), beta 0,56/0,59, margin SpaceX gần 0 (1 ngày, 7.763đ). Còn chờ Taylor_20260913_053329 (A1/A2) + Wags_20260913_053331 (C).
