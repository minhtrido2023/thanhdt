# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.
- T2 14/09 = ex-date DGC cổ tức tiền 8.000đ (ZaloPay). xcheck NAV tối 14/09 SẼ chặn theo kỳ vọng
  (46.750−8.000=38.750). Xử TAY theo kb/ops_runbook.md § PRICE_XCHECK, KHÔNG hỏi lại user.
  Cổ tức TIỀN = kỳ vọng (mark giá CUM); cổ tức CỔ PHIẾU/thưởng/tách = VẪN CHẶN, cần người.
- MỚI 13/09: cron 19:50 ICT nav_snapshot_daily.sh (đường ghi NAV thứ 2, idempotent, nhường
  nav_sync_retry khi rc=4). Tối T2 14/09 lần đầu chạy thật — xem logs/nav_snapshot_daily.log; ca DGC
  ex-date sẽ rc=4 → marker ⏳, KHÔNG phải lỗi.

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

## Review ARIA 13/09 — ĐÓNG TOÀN BỘ 14:40 ICT (file agents/Mike/research/aria_review_response_20260913.md)
A1 reconcile realized (706dec56) · A2 backfill 9/11 (a6e1abb8) · A3 risk T8 CONFIRM · C manifest 421→423
file (c9c883aa/070a6ece/beaa87e4) · F1 phí thật 0,097% HOSE/0,088% UPCOM (5f8c3ba2, dnse_fee_rates.py) ·
F2 ZaloPay seed vốn 987,9tr 07-06 (4a02f23a, data/account_seed_capital.json gitignored) · G cron 19:50
(4b51de53/f42cb7fe). quant-skeptic CONFIRMED A1/F1/F2. B: mike_paseo = mirror cố ý, KHÔNG merge/xoá.
CHỜ USER QUYẾT: (a) 3 chỗ đường THỰC THI còn 0,075% — trading_bot/plan_funding_gate.py:118 FEE_RATE,
bin/merge_park_orders.py:551 fee_est_vnd, bin/bq_freshness_check.sh:657 prompt DollarBill; (b) fill VHC
600cp ZaloPay 07-10 THIẾU trong dnse_raw+journal (có trong email+sao kê) — dispatch data-ops điều tra?;
(c) wire scope code_quality_weekly theo kb/production_manifest.json (đề xuất Wags, chưa làm).

## Code-quality 09-13 — Batch 2+3 XONG, Mike verify 11:40 ICT
- Batch 3 (Taylor): WC b53d26b4 + mike 9a5a2723. Batch 2 (Wags): c9edd4c6 · 136a90d0 · 767deb0e.
- HÀNH VI MỚI: compute_active_nav.py account 0 vị thế mà hôm trước có cổ phiếu ⇒ exit 5, KHÔNG ghi file.
  Bán sạch THẬT ⇒ chạy tay --confirm-flat. Cron 20:15 log rc=1 trong ca đó = guard, không phải lỗi.

## Retro 09-12 đóng (50f7cb2a). Pattern worktree lệch canonical TÁI DIỄN LẦN 3 — gặp lại ⇒ escalate.
## Còn mở không khẩn: ~28 file bin/*.py dirname-x3; job_cancel_guard nhánh systemd luôn đỏ dưới cron.
## append_event.sh JSON isolation — pattern đã biết, không escalate.
## Sát ngưỡng OKF: kb/coding_guidelines.md ~40KB — §-mới PHẢI tách _ext.md.

- [2026-09-13T07:56:00Z] 13/09 14:57 user duyệt 3 việc còn lại ARIA → H Taylor_20260913_075547 (phí thực thi: nhóm A merge_park+prompt commit hôm nay; nhóm B plan_funding_gate PATCH-ONLY, apply chiều T2 ≥15:00 cùng v2 — thêm vào checklist T2), I Winston_20260913_075549 (điều tra fill VHC 600cp thiếu 07-10, read-only, quét lớp lỗi 07-01→08-17), J Wags_20260913_075550 (cq weekly scope theo manifest). Sau H: verify B trước khi apply T2.
- [2026-09-13T08:01:40Z] 13/09 15:03 I XONG: fill VHC 600cp = child ATC oid 502431, bot tắt 14:45:05 trước khi ATC publish → LỚP LỖI latent (1 ca khớp, 4 ca may không khớp). Fix đề xuất executor.py run_session CLOSED: poll tới 14:50-14:55 cho child mở. CHỜ USER duyệt làm patch-only. Gotcha: journal FILL.qty luỹ kế theo child — reader cộng thô thừa 1.544cp/6 key, cần grep reader (giao Wags sau).
- [2026-09-13T08:35:58Z] 13/09 15:38 H+I+J XONG. Checklist T2 ≥15:00 THÊM mục 1c: SAU v2 + remove_v23 → apply /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/aria_H_20260913/plan_funding_gate_fee.patch (Mike verify --check OK trên 24df0f76; Taylor kiểm cả 3 thứ tự OK), chạy selfcheck theo header patch (plan_funding_gate 103/0, plan_cash_commitment 65/0), copy agents/Taylor/research/aria_H_20260913/plan_funding_gate_fee_sync_selfcheck.py vào mike/bin SAU khi land, commit theo header. 12/12 plan replay OK→OK kể cả ZaloPay 14/09 (need 3,98tr / pp0Buy 5,96tr). J xong: cq scope theo manifest (3c22c06b+5283f0f8+edb49264), selfcheck 20/20 Mike chạy lại PASS. CHỜ USER: duyệt patch executor ATC post-close poll (Winston I).
- [2026-09-13T09:10:16Z] 13/09 16:11 user duyệt patch ATC (I) → K Taylor_20260913_0911xx patch-only executor run_session CLOSED poll tới 14:55 + backfill script VHC 07-10. Checklist T2 ≥15:00 THÊM mục 1d: SAU v2 → remove_v23 → plan_funding_gate_fee → apply agents/Taylor/research/aria_K_20260913/executor_atc_postclose.patch (chỉ khi arch APPROVE), chạy selfcheck + quét rộng §23, commit; rồi chạy tay backfill_vhc_0710.py 1 lần. Wags reader FILL.qty luỹ kế: chưa giao.
- [2026-09-13T10:08:54Z] 13/09 17:10 K XONG (Taylor_20260913_091014, mike 430fa526, arch vòng 2 APPROVE, selfcheck 46/46 x4 TZ, mutation 11/11+14/15, quét §23 0 đổi). Checklist T2 ≥15:00 mục 1d SẴN SÀNG: SAU v2 → remove_v23 → gate fee →  (Mike verify --check OK HEAD 24df0f76 17:08), selfcheck theo header (atc_postclose_selfcheck.py + quét executor), commit riêng theo header. ⚠️ backfill_vhc_0710.py CHƯA --apply: verify_account_snapshot ZaloPay 07-10 sẽ rc 0→1 (raw 1200 vs journal 1800) — cần việc nhỏ trước: verify cộng missing_fills_broker_confirmed ở tầng so sánh (reconcile_equity đã làm). Ghi chú owner: K chỉ chạy khi bot vào CLOSED (heartbeat restart KHÔNG --once); run_bot --once không tới; session_announce 14:50 chưa nhắc chờ ATC. Wags reader FILL.qty luỹ kế: chưa giao.
