# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (cuối ngày 05/11 → 06/11)

## Đang chờ user
- Escalation mở: retro-pattern-recurring-dd-multi-round-assumption-unlocked (A khoá giả định / B = A + dd_price_zones từ chối khi md5 lệch / C giữ; khuyến nghị B; thêm đề xuất pilot 1 mã + skeptic trước khi fan-out ≥5 mã). KHÔNG mở question trùng.
- DD: DCM r5 xong (tâm 24.326; giá 33.000 ĐẮT ~+35,7%), plan có BUY DCM LAG_LO — nợ: model_r5 md5 LOCK, luật 18, PDF, dd_price_zones rev=2, release claim topic:dd-dcm-20261104. DD redo 19 mã: vòng 2 đã chạy (dd_redo_20261105, STANDARD_r2.md); skeptic vòng 2 chưa đọc hết; DRI broker openQuantity 0 vs dossier 'GIỮ' cần đối chiếu. Email: chỉ khi user báo (DRI r5/SCL r3/DCM chưa gửi; NNC r6/MVC r9 đừng gửi lại).
- Macro TE: Làn 1 merge; chờ user: Làn 2? TE làm tầng CPI? Dọn worktree wt-macro-ind-1105, wt-te-crosscheck-20261105.
- Model TA ±5% NO-GO; chờ user quyết 'thẻ tần suất nền' cho Livermore hay đóng. Livermore 55/100 trượt PREREG; đọc sống FPT/NNC chấm H20 03/12, 25 phiên 10/12.
- Khác: pnj-bctc-q3-review-trigger; drift CANNOT_CHECK ZaloPay/SpaceX; SZL; DGC vòng 6; TV2.
- Near-miss chưa vá: approve_plan_simple.sh không có --dry-run (chỉ env DRY_RUN=1). 2 câu bus Wags treo (coord-2026-11-05: wags-fix-not-confirmed, wags-autofix-review-needed).

## Sáng 06/11
- Plan 06/11 rev2 ĐÃ DUYỆT cả 2 acct (BUY FPT+NNC sleeve 5% NAV/mã, + DCM...). Kiểm: Trứng vàng SpaceX ≥38,8tr, run_bot 09:05 (hot-path vừa đổi bởi clearing GĐ3, kỳ vọng no-op), fill FPT/NNC → dựng monitor ngày (+10% hỏi Livermore; −10% đề xuất SELL vào plan, không tự bán; 25 phiên hỏi Livermore). Kiểm fill TV1.
- Clearing GĐ3 đã merge master 0e4aaf50c, LAG-only, cờ apply_to_plan=false, chưa cron: cần shadow-apply ≥5 phiên & ≥2 cơ hội + 1 PAUSE drill rồi xin user bật. kb/projects/book-clearing-plan-20261029.md.
- CCDB_PERMISSION_MODE = auto (đã trả lại).

## Luật hiện hành (kb/projects/dd-flag-rules-20261102.md)
Mã có cờ loại khỏi candidate (không PARK, có CAPIT); DD base = sổ sách/NPV 0; r gắn lãi huy động; email DD chỉ khi user báo.

## Mốc
nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore ~19/11; commodity 11-25; BĐS 11-26; LAG 12-15; crontab báo cáo quý trước 31/12; measurement audit ~12-27. Wakeup MISS 05/11 = 0/8.

- [2026-11-06T07:21:04Z] 06/11 14:25: user ĐÓNG model TA; FPT/NNC thoát theo ngưỡng cứng (+10% bán, −10% đề xuất→user xác nhận, 25 phiên=12/11→11/12 thoái), BỎ Livermore khỏi quyết bán. Fill 06/11: FPT đủ cả 2 acct (~51.170), NNC khớp từng phần (100/900, 100/600). Dispatch Taylor_20261106_072056 (exit injector DISCRETIONARY trên auto_exit_inject, worktree, chưa merge) -> arch-reviewer -> merge -> cron. Cuối phiên 06/11 kiểm lại fill NNC.
- [2026-11-06T07:42:41Z] 06/11 14:45: injector DISC arch NEEDS_CHANGES -> vòng 2 Taylor (sonnet) trên nhánh session/disc-exit-20261106; xong thì re-review (1 arch-reviewer giới hạn diff r2) -> merge -> cron. Hỏi user: TIME bán 12/12 (phiên 26) hay 11/12? Finding ngoài phạm vi: plan đã duyệt ⇒ auto_exit_inject REFUSE hết, STOP không ai được báo.
- [2026-11-06T07:52:18Z] 06/11 14:55: injector DISC merged (cron 20:40 sẵn có chạy từ tối nay), sàn bán null. Việc kế: sáng 09/11 kiểm run 20:40 06/11 log (no-op kỳ vọng); hỏi user TIME 12/12 vs 11/12; kiểm fill NNC (còn lại 800/500 chưa khớp?); lưu ý FPT bị BAL/LAG mua thêm ⇒ BLOCK mixed-book.
- [2026-11-06T09:18:02Z] 06/11 16:30: custom30v_rebalance_watch đã vá WARN giả (chỉ đòi rebal khi TODAY > D=phiên đầu >= ngày 5), merge df3b2497a; bảng custom30v_8l đã rebal 2026-11-05 (30 mã). Smoke live trong worktree gửi nhầm 1 tin 🔴 'không đọc được MAX(rebal_date)' vào Trading Daily (worktree thiếu wc_env.sh) = nhiễu, bỏ qua.
- [2026-11-06T13:24:58Z] 06/11 20:30: user duyệt skill due-diligence thêm bước 3c (5F vị thế DN tầng b + tham số moat bền vào mô hình); backup /tmp/due-diligence-SKILL.md.bak-20261106. Lần DD kế tiếp là test thật.
- [2026-11-06T16:29:20Z] 06/11 23:30: user chốt moat/5F/vị thế ngành ≤1 lần/năm/mã (tái dùng nếu <12 tháng, chỉ kiểm nhanh có gì đổi); phần khác Taylor quyết tần suất, không làm lại từ đầu. Đã ghi vào skill due-diligence 3c.
- [2026-11-07T08:51:22Z] 07/11 15:55: báo cáo tuần 02-06/11 CHƯA gửi: (a) OAuth headless chết 09:00 (hết); (b) THẬT: G2 VNINDEX 02/11 BQ 1710.02 vs DNSE 1710.72 — Winston_20261107_085109 đối soát; xong thì xoá key weekly_2026-11-02_2026-11-06 trong state/report_cadence_dispatched.json rồi env -u CLAUDECODE bin/check_report_cadence.sh --scheduled-weekly. Cây việc: vá lọc nhiễu Wags + cờ tươi (commit 1b4817c1a); work_tree_verify_daily.sh đang test nền; CRON (build mỗi giờ 50 0-15 + verify 30 0) bị classifier chặn — cần user OK rồi cài (backup crontab trước).
- [2026-11-07T08:57:14Z] 07/11 16:00: chờ user OK UPDATE BQ Price=1710.72 VNINDEX 2026-11-02 (3 bảng, WHERE Close=1710.72; Price cũ 1710.02) -> sau đó xoá key weekly_2026-11-02_2026-11-06 + env -u CLAUDECODE bin/check_report_cadence.sh --scheduled-weekly. Kiểm 11-09 sau sync 23:45 xem Price bị ghi đè lại không. Chờ user OK cài 2 cron work-tree (build mỗi giờ + verify 07:30).
- [2026-11-07T12:06:14Z] 07/11 19:10 user yêu cầu cập nhật 20 DD theo skill mới (3c 5F+moat), 4 cụm×5, chỉ addendum. Cụm1 FPT/NNC/TV1/DRI/DCM dispatch Taylor opus (jobs _120553/_120556/_120558/_120601/_120603; out ADDENDUM_5F.md+SUMMARY_5F.json trong dd_redo_20261105/<T>/ hoặc dd_DCM_20261104/). Sau: fundamental-skeptic kiểm moat từng mã -> báo cụm1 -> cụm2 DGC/SZL/SAS/MVC/SCL, cụm3 HPG/MBB/TCH/SIP/HHS, cụm4 DDV/NT2/PVP/PVT/TV2. Brief: /tmp/dd5f/brief_template.txt. KHÔNG tự ghi dd_price_zones/moat_tags.
- [2026-11-07T12:25:04Z] 07/11 19:30 DD-5F cụm1: Taylor 5 addendum xong; skeptic: FPT/NNC/TV1/DRI REFUTED văn bản, DCM CONFIRMED (có đính chính). Dispatch vòng sửa sonnet: jobs Taylor_20261107_122439(FPT) _122441(NNC) _122443(TV1) _122446(DRI) _122448(DCM); r1 backup ADDENDUM_5F_r1.md. Brief template đã thêm BÀI HỌC A–H (GPM_P0 là quý, bản chặt-3c song song, v.v.). Khi sửa xong: re-check nhanh (Mike tự đọc, không skeptic vòng 2 nếu chỉ sửa văn bản) -> cụm2 DGC/SZL/SAS/MVC/SCL. Chờ user: quy ước 'bản chặt 3c' áp cho model cũ (NARROW ⇒ biên về TB ngành)? mặc định headline=bản mô tả đúng 3c, đánh dấu chờ duyệt.
- [2026-11-07T12:31:43Z] 07/11 19:40 cụm1 xong (5 addendum r2 đã sửa; chờ user quyết quy ước chặt-3c cho model cũ). Cụm2 DGC/SZL/SAS/MVC/SCL dispatch opus; poll ~750s; sau: Mike tự đọc + skeptic moat 5 mã -> vòng sửa nếu cần -> báo -> cụm3 HPG/MBB/TCH/SIP/HHS -> cụm4 DDV/NT2/PVP/PVT/TV2.
