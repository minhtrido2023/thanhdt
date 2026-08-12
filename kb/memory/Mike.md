# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-11 (cuối ngày, sau daily retro bước 3/3)

## Daily retro 08-11 — XONG
5 sự cố, 2 pattern. Wags verify GAPS FOUND → đã sửa (commit 19e788f không tồn tại — bug
funding-gate hũ-chung 08-10 chỉ được chẩn đoán+escalate, CHƯA vá code, đúng ra 770ff08e/97a80058;
mismatch "3 gap ở #3-#5" → đúng là #1/#4/#5; bỏ tên agent cụ thể khỏi cột blameless). File:
`kb/incidents/retro/retro-2026-08-11.md`, commit `f33c979c`.

**Pattern 1 (KHẨN, đã escalate 2 retro liên tiếp 08-09→08-10) — GÂY THIỆT HẠI THẬT trước khi vá**:
`plan_state_source_mismatch` (checker so CHUỖI MÔ TẢ thay vì giá trị `state` int) chặn oan
escalation `plan-t1-not-ready-SpaceX` tối 08-10 → **30 lệnh lỡ phiên sáng 08-11** (SpaceX 17 +
ZaloPay 13) vì plan không được gửi duyệt kịp. Wags tự root-cause + fix rạng sáng 08-11 (commit
`e6ae5551`, selfcheck 5/5 PASS) — NHƯNG SAU KHI thiệt hại đã xảy ra. Bài học: "ghi lesson vào file
incident" (như 07-15) không đủ ngăn tái diễn ở field khác cùng họ; đề xuất prevention mạnh hơn
(auto-dispatch khi retro đã formal hoá đề xuất rõ ràng, không chờ carryover) — CHƯA duyệt, chờ
Wags/Taylor/user.

**Pattern 2** — `load_plan()` chỉ validate field lạ/thiếu (§7/§24), CHƯA validate SAI KIỂU
(`dd_check` ghi chuỗi thay vì dict → `executor.py` AttributeError mỗi FILL, 22+27 POLL_FAIL). Đề
xuất: coi field sai kiểu như `None` + cảnh báo ồn ào — chờ Taylor/Wags/user duyệt (chạm vùng cấm
Winston).

## Việc treo sang 08-12 (ưu tiên)
1. Ghi file `kb/incidents/` cho 3 fix của Wags hôm nay (#1 state_source, #4 close-the-loop
   has-event-prefix, #5 triaged-needs-human suppress_days) — đủ bằng chứng, làm ngay.
2. Đưa user quyết dứt điểm 2 câu hỏi treo cùng lúc: (a) prevention mạnh hơn cho Pattern 1 ở trên,
   (b) `retro-pattern-recurring-2-days` cũ (backlog ~23 sự cố chưa có file — Wags đã khuyến nghị,
   chỉ thiếu quyết định).
3. `plan_funding_gate.py` (#2 hôm nay, ZaloPay chặn oan phiên chiều — KHÁC bug hũ-chung 08-10, VẪN
   CHƯA vá cả hai): đề xuất tính `need` trên qty còn lại — chờ Taylor/quant-skeptic.
4. `executor.py`/`load_plan()` type-validation (Pattern 2) — chờ Taylor/Wags/user.

## Kế thừa lâu hơn (theo dõi định kỳ, không cần hành động ngay)
- Sự cố `compute_active_nav.py` availableCash bug — verify lại trạng thái thật trước khi dùng.
- ZaloPay park-trim display-only + plan ZaloPay 08-07 0 fill — chưa ai điều tra.
- Job cancel guard round 9 (commit `9e20bbf0`) — fail-closed an toàn nhưng chưa CONFIRMED tuyệt đối.
- Verify độc lập fix VHM (NAV-report + LotBook corp-action) — vẫn chưa có ai verify ngoài Taylor.
- lag-sizing-basis-lech-2-account (SpaceX %active_nav sai mẫu số) — cần xác nhận.
- Mafee live-lever-order test vẫn CHUA_KET_LUAN, cần user cấp quyền Bash đặt lệnh thật.
- PNJ TTL anomaly_flags (~08-23 review).
- coord-2026-08-07 saga bị arch-reviewer bounce 2 vòng, im lặng từ đó.
- write-isolation (job_workspace.py) BOUNCE 2 vòng arch-reviewer 08-11 — DỪNG tự vá, chờ user chọn
  hướng (tiếp tục vá hay đơn giản hoá kiến trúc, tái dùng worktree theo agent/thread). Local only,
  chưa push GitHub.
- Máy fleet 98% đĩa (129G/138G, ~3.3GB free 08-11) — /workspace/kaffa_v2 (45G, không liên quan
  fleet) là consumer lớn nhất; ~2.6GB rác /tmp từ test cũ. Cần báo user/data-ops dọn.
- BACKLOG kiến trúc (Wags): pin-theo-inode không hoạt động thật trong production — quyết định
  thiết kế, chưa dispatch.

- [2026-08-11T21:37:53Z] 2026-08-11 23:xx: User chốt Option 1 cho broker-statement leg3 (đối soát khớp lệnh DNSE trong eod_trading_report.sh) — CHẤP NHẬN đã live (đã vô tình auto-commit qua fleet-backup, quant-skeptic CONFIRMED cao), KHÔNG thêm flag chặn. Điều kiện: 'cần kiểm tra lại mới dùng' — PHẢI tự verify output leg3 lần chạy live ĐẦU TIÊN (cron 19:10 ICT 2026-08-12) trước khi tin dùng cho các báo cáo sau. Việc cần làm 08-12 tối: đọc report EOD sau 19:10 ICT, xác nhận leg3 in đúng số khớp thật (so tay với dnse_raw positions), không có escalation giả.
- [2026-08-12T06:23:14Z] 2026-08-12: Chuoi commit-collision-gate (5 round, commit 79b4f258->0ffda43e->f5f20766->f1a41995->5b09c63d) DA DONG, arch-review CONFIRMED. Con 1 quyet dinh treo cho user: backup.sh || true o kb_nightly.sh:624 khong kiem tra loi backup runtime (khac hinh thai voi chuoi vua dong, hien KHONG firing) - can quyet co sua khong.
- [2026-08-12T06:57:37Z] 2026-08-12: kb_nightly backup.sh silent-fail (commit 984af90a) da vá xong, arch-review CONFIRMED. Toan bo chuoi commit-collision-gate + residual backup.sh DA DONG.
- [2026-08-12T09:46:12Z] 2026-08-12 09:39: Taylor xong nghiên cứu TV1 execution (job Taylor_20260812_091343, agents/Taylor/research/thin_exec_20260812/README.md). 2 nguyên nhân tách biệt: (A) trần giá 20.000đ dưới thị trường từ 08-11 — chính sách, cần user quyết tau; (B) executor tự bóp KL đầu phiên (ceil_allow=30%×KL-đã-khớp) — kỹ thuật, P2 cần paper trial+quant-skeptic. Đang chờ user quyết P1 (tau ceiling band) trước khi dispatch patch.
- [2026-08-12T09:52:23Z] 2026-08-12 09:52: User đồng ý P1+P2+P5 (TV1 execution). Dispatch Taylor implement paper-gated (job Taylor_20260812_095213, opus/high, write-scope executor.py+discretionary_accumulation.py+brokers.py). P1 tau=3% theo khuyến nghị report. Chờ quant-skeptic verify TRƯỚC khi apply/bật paper, giống quy trình HYBRID 08-10.
- [2026-08-12T10:44:44Z] 2026-08-12 10:44: Taylor xong implement P1+P2+P5 (job Taylor_20260812_095213), uncommitted, mặc định TẮT. Selfcheck 17 tổng: 13 xanh/4 đỏ — 4 đỏ đã chứng minh PRE-EXISTING (do HYBRID 08-10 gây ra, không liên quan patch này, không ai phát hiện từ 08-10 tới giờ — cần lưu ý riêng, có thể escalate). Report: agents/Taylor/research/thin_exec_20260812/IMPLEMENTATION.md. Đã dispatch quant-skeptic verify (log verify_20260812_104435_640589.log), chờ verdict trước khi apply/bật paper.
- [2026-08-12T11:01:33Z] 2026-08-12 11:00: quant-skeptic CONFIRMED (cao) P1+P2+P5. 2 defect thật: (1) clamp P2 deploy KHÁC clamp đã đo (cV-F vs (cV-F)/(1-c)) — gain thật +4.6pp không phải +7.7pp (fill 0.829 không phải 0.860), an toàn không đổi; (2) anchor_prices_for() P1 KHÔNG loại bar hôm nay — có thể lẫn giá live vào anchor 5 phiên, chưa test API thật. Khuyến nghị verifier: P5 bật ngay được; P2 paper trial với baseline 0.829 đã sửa; P1 CHƯA nên bật tới khi vá bug anchor + dry-run API thật. Đang hỏi user 3 quyết định: apply/commit code nền không, có tiến P2 paper không, và P1 cần vá thêm + chốt max_no_chase_ceiling VND (chính sách) trước khi bật. Riêng: 4 selfcheck đỏ từ 08-10 (HYBRID gây ra) verifier gọi là phát hiện đáng lo hơn cả — cần lượt riêng, khuyến nghị thêm vào weekly_ops_audit.sh.
- [2026-08-12T11:27:48Z] 2026-08-12 11:27: Việc 1 (commit) XONG: WorkingClaude@49c819e + mike@a91ad1ae, 3 selfcheck tự chạy lại PASS trước commit. Việc 2 (P2 paper) XONG: expected_volume_pacing_enabled=true CHỈ cho account main (paper) qua secrets/trading_bot_accounts.json overrides (xác nhận live SpaceX/ZaloPay/RocketX vẫn False) — không sửa DEFAULTS global vì P2 KHÔNG có live_gate như HYBRID. Dispatch Taylor vá lỗi anchor P1 same-day-bar (job Taylor_20260812_112700) + dispatch Wags dựng selfcheck-red sweep (job Wags_20260812_112724). Đang chờ user chốt max_no_chase_ceiling (số VND) cho P1 — đã giải thích đơn giản, đề xuất range.
- [2026-08-12T11:58:47Z] 2026-08-12 (giữa phiên): PHÁT HIỆN QUAN TRỌNG khi định set max_no_chase_ceiling — state_TV1_SpaceX.json có status='completed' (chương trình gốc target 400cp, xong 07-29). discretionary_accumulation_inject.py CHỈ đọc state status='active' (glob state_*_<account>.json rồi lọc). TV1 hôm nay (target MỚI 5% NAV, chỉ đạo user 08-10 tối) do DollarBill TỰ TAY hardcode hard_no_chase_ceiling_vnd=20000 thẳng vào plan JSON mỗi ngày — KHÔNG qua injector/resolve_price_band() nào cả. ⇒ Set max_no_chase_ceiling vào state file này SẼ KHÔNG có tác dụng gì lên lệnh thật cho tới khi ai đó reconcile 2 đường: (a) reactivate state file (status=active, update target_qty theo 5% NAV, thêm ZaloPay state file mới — hiện chỉ có SpaceX), (b) đổi DollarBill's plan-gen để đọc injector thay vì hardcode tay. Chưa làm gì thêm, đang hỏi user hướng đi trước khi động vào state file 'completed' hay quy trình DollarBill.
