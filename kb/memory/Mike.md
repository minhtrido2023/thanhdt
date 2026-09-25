# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Chuỗi audit lớp lỗi corp-action (exdate price-frame + 3 call-site + vendor-mismatch chain)
  ĐÃ ĐÓNG HOÀN TOÀN 2026-09-24 — tất cả LIVE trên master (bus finding
  corp-action-4sites-audit-COMPLETE-all-4-LIVE).
- Retro 2026-09-24 XONG (commit 8c5c4d68): 5 sự cố, Wags CONFIRMED. 1 escalation MỞ:
  `retro-pattern-recurring-fpt-vendor-backfill-2days` (BQ ticker.Close FPT backfill thiếu hệ số
  corp-action, chặn 2 consumer khác nhau 2 phiên liên tiếp 09-23/09-24) — chờ user/data-ops quyết
  ai theo dõi vendor + có cần lớp phát hiện dùng chung không.

## Việc đang mở / cần theo dõi
1. **FiinPro harvest**: 25/74 lô, rate-limit DAILY, tự resume 00:20 ICT mỗi ngày. Theo dõi thụ động.
2. **excluded_dividend_receivable[DGC]** (ZaloPay) — dọn config khi tiền DGC về thật, dự kiến
   ~2026-09-25. Chưa tới hạn.
3. Pattern "ack theo topic-counter" (`daily_retro.sh:195`) — gốc CHƯA vá, không urgent. Escalate
   nếu retro sau lại có instance MỚI (topic đổi số không được ack cũ phủ).
4. Sự cố #2 retro-09-24: dispatch 2 job liên quan cùng worktree không có khoá — cân nhắc thêm
   check "worktree đang có job khác sống" trước khi dispatch job R&D thứ 2 vào cùng chỗ.

## ĐÃ XÁC NHẬN KHÔNG CÒN TREO
- test_trading_bot.py:353 — ĐÃ SỬA 09-23 (commit 9fefd245+91564b1b+aa7a36ee).
- universe-pit-migration G7/G8/G9 — ĐÃ ĐÓNG 2026-09-19.
- NAV corp-action gate v2 rc=5 runbook — ĐÃ DUYỆT + promote 09-22 (commit c581c74e).
- data/discretionary_margin_arms.json — arm giả đã dọn, hiện = [].
- dnse-balances-stock-block-zero 09-24 — tự hồi phục, ĐÃ ĐÓNG.
- Treasury buyback branch — rút lên master 09-24 (commit 83f6a3ef), nhánh cũ xoá.
- compute_active_nav_selfcheck.py canonical-path bug — ĐÃ VÁ 09-24. ⚠️ còn 3 file nghi cùng lớp
  CHƯA vá: paper_corp_action_selfcheck.py, send_plan_report_park_jit_selfcheck.py,
  due_diligence_corp_flags_selfcheck.py, nav_cum_dividend_selfcheck.py (4 file, xem context_pack).

## Bài học tích luỹ quan trọng
- TRƯỚC KHI dispatch dựa trên tracker/memory: verify bằng git log + bus TRƯỚC — tracker có thể
  STALE dù mới đọc gần đây (7 lần sai trong chuỗi audit 09-24).
- acceptance/verify tự chạy: xem output có NỘI DUNG THẬT, đừng chỉ so 2 chuỗi bằng nhau.
- Lớp lỗi §29 (chẩn đoán không dựa bằng chứng) có thể có NHIỀU CỬA trong CÙNG 1 file — 1 vòng
  review chỉ đóng đúng cửa nó thấy.

- [2026-09-25T05:21:00Z] 25/09 12:2x — User hỏi VN30F1M có dùng không (có, orb_intraday) + hạ tầng đặt lệnh phái sinh sẵn sàng chưa. Mike tự kiểm code: CHƯA sẵn sàng — PHSFlashBroker chỉ ĐỌC balance/position phái sinh (fno_account_id SANDBOX), 0 method đặt lệnh phái sinh ở cả 5 broker class, docstring tự ghi 'Phase 1 chỉ ĐỌC, đặt lệnh chưa xác nhận spec'. Đã báo user: cần dự án hạ tầng riêng nếu muốn live, khuyên tách quyết định quant trước/hạ tầng sau. Dispatch Taylor_20260925_052050 (bg, opus/high, 1.5h) đánh giá lại orb_intraday theo đúng tiêu chí registry (≥60 phiên GỒM chop/bear qua DT5G thật, không phải đếm ngày) + re-eval quant-skeptic nếu đủ điều kiện + hỏi rõ config 'validated' có phải chọn từ sweep cần DSR/PBO không. Kết luận A(đủ+đứng vững)/B(chưa đủ regime)/C(NO-GO). ĐANG CHỜ — poll qua ScheduleWakeup.
- [2026-09-25T09:59:20Z] [2026-09-25T16:59:20+0700] 25/09 16:58 ICT — User duyệt cả 6 đề xuất Taylor từ orb_intraday re-eval (verdict B CONTINUE PAPER). Dispatch Taylor_20260925_095910 (bg, opus/high) triển khai: (1) sửa docstring orb_pt.py bỏ chữ 'validated' sai, (2) chạy config gốc validated song song forward trên 74 phiên, (3) log append-only, (4) xác nhận quy ước sizing notional/margin + fix rounding 5.16->5, (5) ghi chú DT5G backfill vào registry, (6) cập nhật điều kiện re-eval lần sau (regime rời NEUTRAL + ~290-430 phiên). ĐANG CHỜ — poll qua ScheduleWakeup.
- [2026-09-25T10:21:52Z] [2026-09-25T17:21:52+0700] 25/09 17:21 ICT — Taylor_20260925_095910 XONG 6/6. Phát hiện quan trọng việc #2: config GỐC đã validate chạy forward thật trên 35 phiên mới => gate#2 (năm lỗ 2024) FAILED thật (mean -11.20bps, Sharpe -3.05, cum -3.90%, p=0.26) — lặp lại đúng chiều lỗ 2024. Thêm: bộ lọc |OR|>=0.2% (trục quyết định giữa config gốc vs config đang deploy) ĐẢO DẤU giữa IS và 74 phiên live (Welch p=0.028) — dấu hiệu overfit tham số. Badge orb_intraday daily report tự chuyển RED. 5 việc còn lại (docstring, log append-only, sizing notional xác nhận, DT5G backfill note, điều kiện re-eval mới) đã commit, không đổi tham số chiến lược. orb_intraday: cả kết luận quant lẫn dữ liệu forward mới đều nói CHƯA sẵn sàng cho live — không có lý do đầu tư hạ tầng derivatives lúc này. ĐÃ BÁO USER, ĐÓNG mạch việc này.
- [2026-09-25T10:32:31Z] [2026-09-25T17:32:31+0700] 25/09 17:32 ICT — User yêu cầu nghiên cứu củng cố CHÍNH config đang chạy paper (không phải config gốc 'validated' cũ). Dispatch Taylor_20260925_103217 (bg, opus/high, 1.5h): (A) validate đúng từ đầu config đang deploy (walk-forward, per-year, DSR N=1, robustness lân cận), (B) hiệu quả hiện tại 74-75 phiên so kỳ vọng từ A + xu hướng theo thời gian, (C) thiết kế cơ chế cảnh báo sớm (CUSUM/SPRT/rolling Sharpe, ngưỡng cụ thể, dry-run chống false-positive) — chỉ thiết kế, chưa triển khai cron, Mike xem xét sau. Paper-only, không đổi tham số đang chạy. ĐANG CHỜ — poll qua ScheduleWakeup.
- [2026-09-25T11:12:17Z] [2026-09-25T18:12:17+0700] 25/09 18:12 ICT — User duyệt 3 việc + 1 việc mới ưu tiên cao (FiinPro trial hết hạn 2026-09-27 23:59 ICT, ~2.5 ngày). Dispatch Taylor_20260925_111203 (bg, opus/high): (0) kiểm tra FiinX MCP có VN30F1M lịch sử trước 2023-09-11 không (thiếu 2018/2020/2022 bear), ưu tiên chèn hàng đợi harvest nếu khả thi, đối soát chéo vnstock; (1) cài cron monitor orb (chuyển sang mike/bin+data, đăng ký cron_registry.md); (2) sửa API vnstock deprecated trong orb_pt.py; (3) viết lại gate#2 registry cho đúng đối tượng (config đang chạy, không năm lỗ, DSR N=20=0.9234). ĐANG CHỜ — poll qua ScheduleWakeup.
- [2026-09-25T12:09:37Z] [2026-09-25T19:09:37+0700] 25/09 19:09 ICT — User duyệt tính lại ngưỡng graduate orb_intraday. Dispatch Taylor_20260925_120926 (bg, opus/high, 1h): tính N cần theo effect size hợp nhất mới (+6.16bps, DSR N=20=0.49, MaxDD thật -31.78%) thay vì +9.06bps cũ; nếu N cần quá lớn để tự đạt DSR>=0.95 thì trình bày rõ 2 phương án (tiếp tục chờ / tạm dừng tìm cơ chế kinh tế thật) — KHÔNG tự quyết NO-GO. Cập nhật registry end_or_trigger theo số mới. ĐANG CHỜ — poll qua ScheduleWakeup.
- [2026-09-25T12:25:35Z] [2026-09-25T19:25:35+0700] 25/09 19:24 ICT — User CHỐT PHƯƠNG ÁN B cho orb_intraday (decided_by user): tạm dừng hướng 'tích luỹ thêm N' vì DSR 0.95 cần 4075 phiên (~16.2 năm) > cả đời hợp đồng VN30F1M (9.13 năm); ngay cả với TOÀN BỘ lịch sử hợp đồng DSR cũng chỉ 0.779. Cron paper + orb_drift_monitor 15:50 VẪN CHẠY. Nhưng B không phải dừng im — user yêu cầu đổi ngân sách R&D sang: (a) giải thích CHO HẾT tại sao ORB suy giảm (cơ chế, không phải sweep config mới), (b) tìm hướng nghiên cứu mới khả thi hơn. Dispatch Taylor_20260925_122513 (bg, opus/high, 1.5h): việc 1 ghi quyết định B vào registry; việc 2 nghiên cứu chẩn đoán 4 câu hỏi (đoạn lỗ 2023, đảo dấu bộ lọc OR, có cơ chế kinh tế thật không, sự kiện cấu trúc) → danh sách giả thuyết kiểm chứng được; việc 3 bài học quy trình = pre-flight check khả thi DSR TRƯỚC khi đầu tư R&D mới + liệt kê 3-5 hướng ứng viên kèm đánh giá khả thi. ĐANG CHỜ — poll qua ScheduleWakeup.
