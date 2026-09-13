# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.
- T2 14/09 = ex-date DGC cổ tức tiền 8.000đ (ZaloPay). xcheck NAV tối 14/09 SẼ chặn theo kỳ vọng
  (46.750−8.000=38.750). Xử TAY theo kb/ops_runbook.md § PRICE_XCHECK, KHÔNG hỏi lại user.
  Cổ tức TIỀN = kỳ vọng (mark giá CUM); cổ tức CỔ PHIẾU/thưởng/tách = VẪN CHẶN, cần người.

## ⏰ VIỆC CỦA MIKE CHIỀU T2 14/09 ≥15:00 ICT — KHÔNG CÓ SCHEDULER, PHẢI TỰ NHỚ (cập nhật 13/09 13:30)
Batch 1: #3+#2 ĐÃ COMMIT WC 24df0f76 (cờ nav_include_egg_offbook OFF). Working tree trading_bot SẠCH
(Mike verify 13:28). Chiều T2 sau phiên, hạn 21:00:
  1) APPLY V2 (thay cho v1, KHÔNG chồng lên v1):
     git -C /home/trido/thanhdt apply /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/cq20260913_batch1_item1_v2.patch
     (apply --check OK trên 24df0f76 lúc 13:28; mike commit 063dd83f). Chạy selfcheck theo khối CUỐI file
     v2: loan_package_multi_account_selfcheck 44/44 + quét rộng §23 50 file (test_trading_bot.py FAIL có sẵn
     ở HEAD, 'sell window 1.875'). Commit theo lệnh cuối patch. COMMIT MESSAGE PHẢI GHI: dnse_order_test.py
     (tool đặt lệnh tay) nay gửi 1841 cho SpaceX thay vì 1258 — đúng nhưng là đổi hành vi đường tiền.
     v2 = v1 (bỏ ghi gói lên client dùng chung) + fix gốc _profile_default_lp (broker không truyền gói ⇒ tra
     profile theo account_id; SpaceX 1841, ZaloPay giữ 1258 từng byte). arch-review 2 vòng APPROVE.
     Rollback: v1 = cq20260913_batch1_item1.patch (vẫn apply --check OK).
  1b) SAU v2 — PATCH GỠ v23 SẴN SÀNG (Taylor_20260913_064725, mike 2a067741, arch-review 2 vòng APPROVE,
      Mike verify 14:22: apply v2 → remove_v23 --check OK trên worktree tạm; working tree thật SẠCH):
      a) `git -C /home/trido/thanhdt apply --index <.../cq20260913_remove_v23.patch>` — BẮT BUỘC --index (2 rename
         archive/: bot_prepare_plan.py, capit_exit_floor_selfcheck.py). Selfcheck + commit theo khối cuối patch.
      b) apply agents/Taylor/research/cq20260913_remove_v23_mike_docs.patch vào mike repo (DollarBill/CLAUDE.md
         82+86, MIKE_ext.md:90, kb/coding_guidelines_ext.md:27 — chỉ text).
      c) chạy mike/bin/production_manifest.py cho mất entry capit_exit_floor_selfcheck (hiện chỉ WARN).
      Mike đã soi: bot_execute.py chỉ đổi 1 thông điệp + 1 comment (không logic); capit_exit_floor guard CHỈ
      nằm trong V23Strategy.build_plan diff step (strategies.py:485/495) ⇒ gỡ cùng đường chết, không mất
      coverage live. test_trading_bot.py FAIL giống hệt trước/sau (có sẵn). Gỡ xong ⇒ đóng retro 08-19 bug2.
      Câu hỏi mở KHÔNG chặn: plan V2.4 DollarBill có tránh bán nhầm phần custom30V khi đóng CAPIT cùng mã
      không (guard cũ chưa bao giờ bảo vệ plan live) — cân nhắc kiểm sau.
  2) dispatch Wags quét ~28 file bin/*.py dirname×3 → wc_paths.
Rò 1258 SpaceX (Taylor_20260913_055125, Mike đếm lại): KHÔNG ảnh hưởng tiền — 160 lệnh SpaceX 07→09 =
{1841:78, 1122:82}, 0 lệnh/ppse 1258; nguồn discretionary_accumulation_inject.py:116. v2 đóng ca này.

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
- [2026-09-13T06:15:54Z] 13/09 13:17 ARIA: A1 CONFIRMED high (706dec56), A2 backfill 9/11 (a6e1abb8), A3 CONFIRM, monthly action #5 đóng (1eb115b9). Còn Wags_20260913_053331 (C manifest 422 file, arch-review vòng 2). 3 việc phát sinh cần user: phí thật 0,092/0,097% vs 0,075%; ZaloPay seed vốn đầu kỳ + sao kê 34,3tr 07-10; EOD wrapper thoát sớm ⇒ nav_snapshot không chạy 3/11 phiên.
- [2026-09-13T06:29:02Z] 13/09 13:30 ARIA batch ĐÓNG: A1 CONFIRMED, A2 9/11, A3 CONFIRM, C manifest 421 file (105/101/65/150) commit c9c883aa+070a6ece+beaa87e4, selfcheck drift trong run_selfchecks. Đã báo user kết quả cuối + 3 việc phát sinh chờ quyết (phí thật 0,092/0,097%; ZaloPay seed vốn + sao kê 34,3tr; tách nav_snapshot khỏi EOD wrapper). Đề xuất wire scope code_quality_weekly theo manifest CHƯA làm.
- [2026-09-13T06:45:48Z] 13/09 13:47 user quyết 3 việc phát sinh ARIA: (1)+(2) dùng email khớp lệnh DNSE làm chứng cứ, đủ dữ liệu thì đổi phí thật → Taylor_20260913_064536 (F1 phí + F2 ZaloPay seed vốn); (3) duyệt tách nav_snapshot thành cron riêng → Wags_20260913_064538 (G, được đụng crontab). Sau F1 nếu đổi phí: sửa memory project-spacex-account-fee-margin-rates.md + F1 qua quant-skeptic. Còn chờ user: wire scope code_quality_weekly theo manifest.
