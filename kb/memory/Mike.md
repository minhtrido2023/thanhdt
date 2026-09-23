# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Retro 2026-09-23 XONG (6 sự cố, 3 pattern, Wags GAPS FOUND→đã sửa, commit `6d320fad`).
  Pattern 1 (approval-gate trễ) CHỐT sau 3 lần tái diễn — cron `plan_approval_reminder.sh`
  08:50 ICT go-live hôm nay, chưa qua chu kỳ nhiều ngày, theo dõi tuần tới.
- NAV corp-action gate v2 (L2-L4) LANDED master `4dcc3643`. Runbook rc=5 mới **CHỜ MIKE DUYỆT
  ĐƯA LIVE** — `kb/ops_runbook.md.proposed` §13.
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải
  chạy approve_margin_day.py TRƯỚC bot.

## Việc đang mở / cần theo dõi
1. **`test_trading_bot.py:353`** (raw `p["broker"]`/`p["mode"]`) — CHƯA sửa, quá hạn 2 ngày liên
   tiếp (deadline gốc "trước retro 09-22"). Cần dispatch cụ thể ai sửa.
2. **`question wags-fix-not-confirmed: coord-2026-09-23`** vẫn TREO cuối ngày 09-23 — arch-reviewer
   NEEDS_CHANGES cho finding `wags-fix: coord-2026-09-23`, chưa có finding/answer sửa theo sau.
   Root cause: root_cause sai + mô tả hành vi hệ thống sai vẫn đứng nguyên trên bus.
3. **Pattern 2 CHƯA sửa gốc** (retro-2026-09-23): `daily_retro.sh:195` sinh topic escalate nhúng
   bộ đếm ngày (`retro-pattern-recurring-<n>-days`) khiến ack theo topic khớp tuyệt đối không
   phủ được khi topic đổi số — ≥6 lần cùng gốc. Hướng sửa: tách `recurrence_count` ra payload
   riêng, topic ổn định theo tên pattern. Chưa đủ ngưỡng "2 retro liên tiếp" để bắt buộc — nếu
   lặp ở retro 09-24 phải escalate ngay.
4. **NAV corp-action gate v2 rc=5 runbook** — chờ Mike duyệt đưa live.
5. **universe-pit-migration G7/G8/G9** — ~9 tuần treo, chờ user chọn A (dispatch Taylor làm dứt
   điểm) hay B (đóng hẳn). G8.1 đã đóng 09-20.
6. **excluded_dividend_receivable[DGC]** (ZaloPay) cần dọn config sau khi tiền DGC về thật
   (~2026-09-25).
7. Treasury buyback/corp_action mở rộng (Taylor branch feat/treasury-share-events-table) — chờ
   user duyệt chính thức.
8. FiinPro/OShares harvest dừng 09-15 ở 4/59 lô — chưa có selfcheck/commit xác nhận.

- [2026-09-23T17:52:24Z] 24/09 00:5x — exdate price-frame ĐÃ LAND: mike master 508bb607, arch-review APPROVED sau 3 VÒNG. current_ops đã ghi (1656990a). Selfcheck từ master 59/59 qua 5 TZ + corp_action 85/0.
SỐ ĐÃ ĐÚNG cả 2 account (Mike chạy lại lúc 00:5x): SpaceX VPB 1.386 × 22.050 = 30.561.300, active_nav 982.294.013; ZaloPay VPB 1.512 × 22.050 = 33.339.600, active_nav 520.678.926; computed_at 2026-09-24.
Dispatch DollarBill_20260923_175136 LẬP LẠI plan 24/09 cả 2 account trên số mới (plan cũ BÁN VPB 200cp/100cp ref_price 27.800, CHƯA duyệt nên không có lệnh nào chạy).
ĐÃ ĐẾM 5 CALL-SITE CÙNG LỚP CHƯA VÁ — thứ tự ưu tiên: (1) dividend_adjusted_return.py:473-478 chạm SỐ CÔNG BỐ nhà đầu tư §21; (2) discretionary_margin_gate.py:335 sleeve margin tiền thật, latent; (3) report_return_gate.py lỗ hổng phủ im lặng; (4) discretionary_accumulation_inject.py:124 baseline hỏng vĩnh viễn; (5) due_diligence.py adv_vnd() chiều an toàn không gấp.
NỢ VỆ SINH: compute_active_nav.py:616 chưa atomic (§5, đóng luôn lỗ hardlink); bản CŨ mike/.claude/worktrees/wags-fix-coord-08-19/bin/compute_active_nav.py ghi thẳng canonical với bug gốc (grep exdate_frame = 0); runbook rc=6/rc=7.
⚠️ arch-reviewer KHÔNG khẳng định đã quét hết lớp lỗi này — không tuyên bố đã đóng.
- [2026-09-23T18:51:05Z] 24/09 01:5x — CALL-SITE THỨ 3 ĐÃ LAND: mike master 1608a267 (+ current_ops 733e08a7), arch-review APPROVED high. Selfcheck 120/0 từ master qua 3 TZ.
Q1 — CÂU QUAN TRỌNG NHẤT, ĐÃ TRẢ LỜI: KHÔNG số công bố nào bị ảnh hưởng. Mike tự xác nhận độc lập bằng BQ + quét toàn bộ dnse_raw: 24 sự kiện DIV+ISS cùng ex-date sau go-live 01/07, 39 mã đã từng nắm giữ, GIAO = RỖNG. Reviewer mở rộng: cả 2025 còn 5 ca nữa (SHS 04-24, ACB 05-23, HAH 08-07, MBB 08-13, TLG 12-11) => nhịp ~5-7 ca/năm, KHÔNG phải ca hiếm, chỉ chưa cắn.
SPEC MIKE SAI LẦN 6 — Taylor bác bằng dữ liệu thật, reviewer đo lại xác nhận: hướng 'neo theo broker_effective_ts' SAI. (1) MBB 10/08 mốc khai 19:32:49 nhưng bản ghi positions CUỐI của ngày là 19:12:13 vẫn ở 1.100 chưa credit; credit thật chỉ ở file 11/08 => mốc ĐÚNG SỐ nhưng SAI LÝ DO. (2) VPB 23/09 bản ghi duy nhất trước mốc 11:58 là 04:51 SÁNG => neo ở đó bỏ mất lệnh khớp trong chính phiên cum; ca thật SpaceX bán MBB 1.500->1.100 lúc 09:15 ngày 10/08 => neo mốc trả 1.500 thay vì 1.100, sai 36%.
MIKE ĐỌC SAI TRƯỜNG: tôi báo mutation cho 'per_share 6.537 = số THỪA'. Reviewer bác: 6.537 là giá trị KHỞI TẠO tầng 1 để chẩn đoán (_EST = 27.800 × (1 − 1/1,30756)), KHÔNG bao giờ đi ra ngoài vì cash_per_share (:191-207) trả 0 với mọi kind != CASH_CONFIRMED. Taylor đúng, tôi sai.
MÔ TẢ RỦI RO ĐÚNG (reviewer chốt, 4 chiều): MẤT số (fail-closed về 0) => §21 công bố THIẾU cổ tức, tỉ suất thấp hơn thực tế — CÓ tới số công bố; số THIẾU — bị lưới SANITY_REL 1% bác; số THỪA — KHÔNG TỒN TẠI; LÂY sang mã KHÁC cùng ngày delta — CÓ tới số công bố (selfcheck 18 ghim: YYY công bố 502đ/cp thay vì 500, lệch 0,4%, lọt CẢ dư số LẪN sanity). Đây mới là đường im lặng thật.
LỖ MỚI reviewer tìm, ƯU TIÊN CAO NHẤT việc sau: dividend_adjusted_return.py:469-472 broker_qty() lấy LÔ CUỐI thay vì TỔNG LÔ (cùng ts thì ghi đè chứ không cộng) => thiếu 25% KL thật ở 135 cặp (mã,ngày) của ZaloPay (BID 11/08: 300 vs 400; BID 14/08: 320 vs 427). credit_frame đi qua raw_positions thì GỘP LÔ ĐÚNG => sau bản vá có HAI QUY ƯỚC KL cùng tồn tại trong một lần giải. Pre-existing + fail-closed (hệ 2x2 bất tương thích => dư số bác; hệ 1x1 nghiệm cao hơn ~33% => sanity bác) nhưng BID/VCB/MBB trả cổ tức tiền HẰNG NĂM nên sẽ cắn. Kèm vi phạm §29: thông điệp :876-877 khẳng định cứng 'nghi phương trình bị nhiễm bởi sự kiện chưa phát hiện' — sai hẳn hướng.
VIỆC SAU KHÁC: (2) §29 :876-877; (3) thêm bin/dividend_adjusted_return_selfcheck.py 3 dòng — hiện 120 assertion TÀNG HÌNH với CẢ 2 runner (run_selfchecks.sh tìm -iname '*selfcheck*.py', selfcheck_weekly_baseline_check.sh tìm '*_selfcheck.py'), pre-existing; (4) bỏ default frame=None của _qty_at để caller mới không âm thầm nhận semantics cũ (report_return_gate.py:185 là caller 2-tham-số DUY NHẤT, chỉ dùng DẤU nên vô hại); (5) 3 khoảng trống test (mutation A2/A3/C2 sống); (6) CHÍNH SÁCH cần user quyết: resolve_dividends:963 vs :977 — vendor_check='mismatch' hiện chỉ là ghi chú, unverified rỗng, KHÔNG consumer nào đọc; gói chung với bus question can-user-quyet-mo-cong-CASH_VENDOR; (7) entitled_gross() report_return_gate.py:176 chưa có selfcheck nào — là cổng cuối trước số gửi nhà đầu tư.
CÒN 4 CALL-SITE: discretionary_margin_gate.py:335 (sleeve margin tiền thật, latent, ƯU TIÊN TIẾP), report_return_gate.py, discretionary_accumulation_inject.py:124, due_diligence.py adv_vnd().
⚠️ reviewer KHÔNG khẳng định đã quét hết.
