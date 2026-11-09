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

- [2026-11-08T18:07:08Z] 09/11 01:20 DD cụm 3b (topic MỚI 1569046504570753125, user @mention đã gửi): DGC cách B xong+skeptic cuối CONFIRMED -> GHI SỔ (63 entry). SZL: r3b A đúng, B sai khung (KTPL trên cả vốn gốc) -> Taylor_20261108_180625 r3c (vòng cuối, Mike kiểm cơ học vs skeptic: tâm 5 tỷ 25.165-25.241, P90 27.710-27.786) -> sau đó ghi sổ. 5 mã FPT/HHS/SIP/TCH/MVC: skeptic r2 xong (TOP5D_CORRECTIONS_20261108.md), Taylor r3 jobs _180128 FPT/_180130 HHS/_180132 SIP/_180134 TCH/_180136 MVC. Sau: claim-reply -> skeptic cuối (opus) 5 mã -> sửa artifact stale/ERRATA -> ghi sổ rev+1 assumptions_md5 (/tmp/ledger_head.py + pattern /tmp/add_dgc.py) -> bảng ở topic mới. Quy ước chờ user: HHS/TCH chiết khấu holding [UL] ra độ nhạy (base 0%) có thể đảo nhãn sang DƯỚI. Sổ CHƯA commit.
- [2026-11-09T00:46:45Z] 09/11 07:55 DD cụm 3b XONG 7/7 mã ghi sổ (69 entry, chưa commit). Báo bảng ở topic 1569046504570753125. Chờ user: quy ước CK holding [UL] base 0% (HHS DƯỚI/TCH không chắc), DGC ZaloPay 35,3% NAV, DCM r7 (topic 1568993376421023796) chưa duyệt. Sổ dd_price_zones CHƯA commit.
- [2026-11-09T01:18:34Z] 09/11 08:2x user chốt (topic 1569046504570753125): DGC KHÔNG có lộ trình giảm (đang vùng P10 theo DD) — chỉ xem xét khi giá vượt tâm; DCM r7 KHÔNG làm (giá vượt tâm quá xa), chỉ khi có tín hiệu; CK holding: user hỏi giải thích 3 cách chọn (A base 0% hiện tại / B 27% / C giữ A + nhãn nhạy quy ước) — Mike đã giải thích, CHỜ user chọn; lưu ý HHS(forensic exclude)/TCH(FLOOR_FAIL) bị loại candidate bất kể nhãn.
- [2026-11-09T01:27:34Z] 09/11 08:3x user chốt C (giữ A base 0% + nhãn nhạy quy ước HHS/TCH). Đã gửi PDF r3 6 mã (trừ DGC) ở agents/Taylor/research/dd_redo_20261105/pdf_r3_20261109/ (đính kèm Discord). PDF investor-report cũ 01–03/11 là số trước redo, không gửi.
- [2026-11-09T07:36:15Z] 09/11 14:4x DD candidate LAG plan 09/11 (topic 1569250659272892526): Bobby xong 3 sector read (loc_hoa_dau, khi_dot_lpg, hoa_chat_xut_clo 20261109; MSB dùng ngan_hang 1031). Taylor opus jobs: BSR _073600, CSV _073602, GAS _073604, MSB _073606 (dir agents/Taylor/research/dd_lagcand_20261109/<MÃ>). Sau: claim-reply từng job -> fundamental-skeptic (opus) 4 mã -> sửa ERRATA -> ghi sổ dd_price_zones (assumptions_md5) + PDF -> báo topic này. GVR/HTN/MZG/YEG/PHP chưa DD (bị lọc khỏi plan).
