# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (cuối ngày 10/11 → 11/11)
## Đang chờ user
- Retro 10/11 ghi xong (kb/incidents/retro/retro-2026-11-10.md). Escalation đang mở, KHÔNG mở trùng: retro-pattern-recurring-bg-dispatch-wakeup-miss-gate-checks-declaration-only (khuyến nghị A: Stop hook kiểm ScheduleWakeup thật) và retro-pattern-recurring-anomaly-flags-stale-weekend-false-alarm (A: checker dùng lịch phiên; gộp luôn drift-check CANNOT_CHECK, bin/plan_position_drift_check.py:130 neo ngày plan).
- Câu hỏi mở: vgs-exit-max-sessions-can-chot (DollarBill, A/B/C: VGS không nêu hạn giữ vs auto_exit_inject cần max_sessions>0).
- Plan 11/11 (DollarBill rev2, có VGS+NNC) chờ user duyệt; drift-check 11/11 báo CANNOT_CHECK (lỗi ngày-lịch) ⇒ tự kiểm vị thế tay trước khi duyệt.
- LAG cache adjusted (A) ĐÃ merge+áp pkl 10/11; crontab dời orb_drift 15:50→15:55 BỊ classifier chặn ⇒ user tự chạy/cho phép, rồi cập nhật kb/cron_registry §11. Sáng 11/11 kiểm w_LAG live + papertrade 15:30 (lần đầu cache mới). GIỮ pin R3 22,12/25,42; re-pin mirror-live REFUTED.
- BAL edge gate tháng: nghiên cứu CONFIRMED gate hại CAGR ~2–2,8pp; code f103ae0fa CHƯA merge, chờ user quyết bật/không + cron 00:40.
- DD VGS đã email 1 lần (không gửi lại). HHS ex_basis_pending; SCL kiểm quyền sau 08/12. Winston: BQ Close SCL chưa điều chỉnh lùi 09/11.
- Fix chưa làm: close_bus_question --verified-by; wakeup gate kiểm hành động thật; dedupe APPROVAL_GATE_BLOCK; lệnh đối ứng cùng mã chưa guard; 2 cron work-tree/thẻ Livermore/macro TE Làn 2/pnj-bctc-q3 chờ user OK.
- LAG luật 5 (09/11): mua LAG cần DD + giá<=tâm; mốc 15/12; lag_gate_exit_check.py chưa cron.
## Mốc
nav-loss-brake 11-09 (đã qua); commodity 11-25; BĐS 11-26; Livermore H20 03/12; LAG 12-15; audit đo lường ~12-27; DT CRISIS sớm nhất ~11/10.

- [2026-11-11T01:23:38Z] 11/11: Taylor_20261111_011218 xong (rating lag LAG Q3: M1 đóng 0/88; phát hiện rating dòng Q3 trôi 4/88; đề xuất P1 log rating cổng (rẻ) + P2 cron re-rate có điều kiện sau 10/11) — chờ user duyệt P1/P2
- [2026-11-11T01:48:47Z] 11/11: P2 DONE + merged master — fa_ratings_earnings_window_daily.sh ngoài cửa sổ chạy có điều kiện (ticker_financial numRows đổi; state state/fa8l_tf_numrows.txt). Crontab không đổi. Lần 17:30 11/11 sẽ chạy 1 lần lập baseline. Kiểm log logs/fa_ratings_earnings_window.log tối nay. P1 (log rating cổng) chưa duyệt.
- [2026-11-11T02:09:58Z] 11/11: P1 DONE merged WC main b086580fb (lag_rating_gate_snapshot + data/lag_rating_gate_log.csv, arch-review fixes R1/R2 applied). Kiểm sáng 12/11 CSV có dòng lượt golive 19:00 11/11. Nợ nhỏ: CSV gitignored/no backup, chưa data_registry entry, không file lock. P2: kiểm log 17:30 11/11.
- [2026-11-11T03:26:17Z] 11/11 10:3x: user yêu cầu DD tương thích VN (giá 5 năm có chạm vùng DD không). Đo sơ bộ 25 mã: 100% chạm tâm; dispatch Taylor opus PIT calib (REPORT agents/Taylor/research/dd_vn_calib_20261111/); chờ kết quả rồi đề xuất tham số + skeptic, chưa sửa engine/skill.
- [2026-11-11T03:45:51Z] 11/11 10:5x: user bảo xử lý hết 5 câu bus (trừ PNJ→Q4). Đã dispatch: Taylor_20261111_034523 (VGS max_sessions=null + rule +15/-10, opus, arch-review), Wags_20261111_034525 (Stop hook wakeup A), Winston_20261111_034527 (anomaly-flags + drift-check lịch phiên A). Đã đóng: expvol_pacing, cq-hard-boundary. Khi các job xong: close vgs/wakeup/anomaly topics (--decided-by-user), báo user. PNJ: để đến BCTC Q4.
- [2026-11-11T03:47:47Z] 11/11 10:50: Taylor dd-vn-calib XONG: KHONG TUONG THICH (K3 khong hoi tu). Goc loi = co so FCFE 3y, khong phai r/g/shrink. De xuat P1 co so FCFE-chuan-hoa, P2 co nen-dong-tien-khong-dai-dien, P3 cham PIT dd_price_zones. quant-skeptic dang chay (verify_finding --topic dd-vn-calib); cho user duyet huong, CHUA sua engine.
