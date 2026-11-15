# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 14/11 → 15/11
- Retro 14/11 ghi (kb/incidents/retro/retro-2026-11-14.md). Weekly report 09–13/11: gate vẫn INCOMPLETE lúc 02:21Z, CHƯA xác nhận COMPLETE — kiểm report_delivery_gate lại.
## Đang chờ / mở
- Plan T+1 thứ Hai 16/11: vòng CN 19:00 dựng; user duyệt trước 08:45 T2 (mirror topic plan 1521183164364754974).
- PNJ Q3 chờ user A/B; classifier-denials-mike chờ user duyệt A (allowlist headless; build_universe_pit.py cũng bị chặn).
- DD PAT: rev3 tâm 64.700 (49.600–79.200), giá 13/11=71.000; CHƯA gửi email (chờ user nói); skeptic lần 2 cho r2 chưa chạy; mốc BCTC Q4/26. Topic: 1571194491489091644.
- 5 selfcheck-red thật (immutable_publish/universe_pit_p3,p4/basket_price_basis_audit/nav_scripts_2account) chưa triage; RCA ETL kaffa_v2 (bq_admin); đề xuất gate đếm raw ticker vs ticker_1m chưa làm.
- Opus 57%: selfcheck_red_owner_sweep.sh hardcode opus/high — đề xuất hạ, chưa sửa.
## Quyết định gần đây
- Livermore thu hẹp vai (merge 54aac7380); phân kỳ RSI NO-GO. Chấm TAY LVR-STK FPT/NNC 03/12, VGS/NNC 10/12; LVR-2026-10-21 scorer tự chấm 18/11.
- NEO sizing DD: NAV ≤2 tỷ ⇒ DD5 ≈ −33%; A8 live-gap SHELVED.
- 4 quy tắc DD-flag 02/11 giữ nguyên.

- [2026-11-15T09:39:06Z] [15/11 16:5x] PAT: skeptic lần 2 xong (REFUTED nhẹ 56.100 / CONFIRMED 68.000), tâm 64.700 giữ, sổ rev4; EMAIL ĐÃ GỬI tới dtienthanh@gmail.com. Mở: tờ trình GD bên liên quan DLC (ĐHĐCĐ 12/05&14/08) đóng nút T; BCTC Q4/26.
- [2026-11-15T10:40:13Z] [15/11 17:5x] Plan 16/11 THIẾU: nguyên nhân = Fri 13/11 18:30 daily_refresh abort (BQ VNINDEX chỉ tới 06/11 vs published 12/11, guard từ chối publish) ⇒ 19:00 bq_freshness FAIL DT5G publisher-evidence ⇒ không dispatch DollarBill. Vòng CN 19:00 no-op (ngày 15>10 ngoài cửa sổ BCTC). Chờ user chọn: A) mở cổng sunday_plan_round cho ca 'thiếu plan T+1' trước 19:00 CN; B) chạy tay chuỗi. Lệnh phục hồi trong alert KHÔNG đủ (thiếu NAV/inject/park).
- [2026-11-15T12:34:03Z] [15/11 19:5x] User chọn A + vá gốc. Đã merge cổng cứu hộ sunday_plan_round (commit 41a8bd58a lên master mike; selfcheck 247x3 TZ). Chạy tay vòng CN 19:30 cho plan 16/11 (log logs/sunday_plan_round.log). Winston_20261115_123354 làm guard ticker-vs-ticker_1m trong daily_refresh (không merge trước 21:30). RCA: ticker bị writer ngoài làm thủng 13/11 16:37-16:42, INSERT bù 14/11 09:03. Việc còn: xác nhận plan 16/11 đủ 2 account + gửi báo cáo duyệt; hỏi user có muốn thêm cứu hộ ngày thường (late_plan_catchup MISSING).
- [2026-11-15T12:40:37Z] [15/11 19:4x] Lượt 1 vòng CN fail vì dispatch.sh gate exit 8 (wrapper chạy từ phiên tương tác ⇒ CLAUDECODE=1). Lượt 2 chạy MIKE_WAKEUP_GATE=off. BÀI HỌC: chạy sunday_plan_round/bq_freshness tay từ phiên Mike phải đặt MIKE_WAKEUP_GATE=off hoặc env -u CLAUDECODE; cân nhắc cho wrapper tự đặt.
- [2026-11-15T12:49:51Z] [15/11 19:5x] Plan 16/11 XONG (b/b, requires_user_approval, report gửi 19:46); 2 bus q plan-t1-not-ready đóng. Còn mở: user duyệt plan trước 08:45 T2; Winston ticker-integrity-precheck READY_PENDING_MERGE (cần arch-review + merge sau 21:30; chưa merge); hỏi user cứu hộ ngày thường; cân nhắc cho sunday_plan_round tự đặt MIKE_WAKEUP_GATE=off khi chạy tay.
- [2026-11-15T13:30:42Z] [15/11 20:4x] Dọn rác: xoá bundle 3,8G + artifact untracked live_gap_*/intraday_cutloss v1,v2 (git clean -fdx, tracked giữ) → đĩa 92% (19G). Cron dọn worktree repo ngoài 03:10 ICT. Còn chờ user: worktree dirty, bq_cache_asof 2x2G, book_regime_fit 943M untracked (CHƯA xoá), journal cần sudo.
- [2026-11-15T14:43:16Z] [15/11 21:5x] Topic 1571535612136390818: user yêu cầu fable lên kế hoạch nghiên cứu AI-momentum 2-model (ảnh YouTube). Dispatch Taylor fable/high job Taylor_20261115_144310 → kb/projects/ai-momentum-research-plan-20261115.md; chờ rồi báo user trong topic này.
- [2026-11-15T14:51:12Z] [15/11 21:5x] Kế hoạch AI-momentum XONG (kb/projects/ai-momentum-research-plan-20261115.md), đã post topic 1571535612136390818. Chờ user: 'duyệt P0' + 4 câu F (mục tiêu, vũ trụ, M2, topic) rồi mới dispatch P0.
- [2026-11-15T15:06:37Z] [15/11 22:1x] User chốt: edge dự báo, rating≤4, M2=deepseek mù+fundamental-skeptic cổng, duyệt P0, mở topic mới. Topic Momentum Lab=1571541823615406201; job P0 Taylor_20261115_150627 (Opus/medium); phiên ở topic mới theo dõi (wake_thread). Topic cũ 1571535612136390818 DỪNG, không poll. Sau P0: quant-skeptic Opus/high đọc PREREG.
- [2026-11-15T15:22:52Z] [15/11 22:3x] P0 AI-momentum XONG (kb/projects/ai-momentum-p0-result-20261115.md); Taylor khuyến nghị P1 có điều kiện. quant-skeptic chạy bg (log logs/verify_20261115_152040_*.log) — chờ verdict post topic 1571541823615406201. Chờ user chọn: P1 / nới ngưỡng v2 / dừng.
