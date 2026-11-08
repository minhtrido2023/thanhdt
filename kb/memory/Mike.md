# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (cuối ngày 08/11 → 09/11)

## Đang chờ user
- **Plan thứ Hai 09/11 (SpaceX+ZaloPay) CHƯA DUYỆT** — là bản KHÔI PHỤC plan thứ Sáu (vòng CN không dựng được lớp park; 4 lệnh, approved_by=None). Hạn duyệt trước 09:05 ICT, không duyệt = HOLD. Xem plan có thiếu lệnh park T6 không (DollarBill/user).
- BQ `Price`=1710.72 VNINDEX 2026-11-02 (3 bảng, WHERE Close=1710.72) chờ user OK UPDATE → xoá key weekly_2026-11-02_2026-11-06 trong state/report_cadence_dispatched.json, chạy `env -u CLAUDECODE bin/check_report_cadence.sh --scheduled-weekly`, KIỂM file reports/SpaceX_weekly_report_2026-11-02_to_2026-11-06.md có thật. Báo cáo tuần CHƯA gửi. Sau sync 23:45 11-09 kiểm Price có bị ghi đè.
- DD r3: DGC (nhánh A xác suất 0 → 41.522 / B giữ 0,5 → DƯỚI) + SZL (RONIC=Ke; KTPL cổ phần → nhãn 5 tỷ TRÊN) REFUTED hẹp, CHƯA ghi sổ, chờ user quyết. DGC ZaloPay 35,3% NAV vs trần 2-4% đã báo. DCM r7 chưa duyệt. Chưa làm: FPT,HHS,SIP,TCH,MVC. Topic: cụm 3 = 1569011390365044787; DCM = 1568993376421023796. Sổ dd_price_zones 62 entry CHƯA commit (backup cron gom). Entry mới PHẢI tính assumptions_md5.
- Chờ user OK cài 2 cron work-tree; thẻ tần suất nền Livermore; macro TE Làn 2; pnj-bctc-q3-review-trigger; approve_plan_simple.sh thiếu --dry-run; SCL lõi GPM lan WIDE (REPORT_r2).
- Lệnh đối ứng cùng mã cùng phiên: nguyên tắc user (tránh; nếu có thì qty mua < qty bán), CHƯA guard code.

## Escalation đang mở (KHÔNG mở trùng)
retro-pattern-recurring-anomaly-flags-stale-weekend-false-alarm (khuyến nghị A: checker dùng lịch phiên). Option B DD đã chốt/đóng 08/11.

## Fix cần làm
anomaly-flags-stale (Winston) và chuỗi park vòng CN: đều lỗi lịch ngày-lịch vs ngày-phiên, chưa fix. Gợi ý: commit a8811154d có thể là fix cho Wags/selfcheck-red commodity_cycle_forward_tracker_selfcheck — đọc rồi đóng bằng close_bus_question.py nếu đúng.

## Luật hiện hành
dd-flag-rules-20261102; DD base = sổ sách/NPV 0; r gắn lãi huy động; email DD chỉ khi user báo; moat chỉ thêm khi bền, không áp 3c chặt (user 08/11); moat/5F ≤1 lần/năm/mã; khoá assumptions_md5, pilot 1 mã+skeptic trước fan-out ≥5.

## Mốc
Sáng 09/11: kiểm run 20:40 injector DISC, fill NNC/FPT/TV1; nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore H20 03/12; commodity 11-25; BĐS 11-26; LAG 12-15; audit đo lường ~12-27.

