# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (cuối ngày 07/11 → 08/11)

## Đang chờ user
- OK UPDATE BQ `Price`=1710.72 VNINDEX 2026-11-02 (3 bảng, WHERE Close=1710.72; Close đã ĐÚNG, chỉ Price sai) → sau đó xoá key weekly_2026-11-02_2026-11-06 trong state/report_cadence_dispatched.json, chạy `env -u CLAUDECODE bin/check_report_cadence.sh --scheduled-weekly`, KIỂM file reports/SpaceX_weekly_report_2026-11-02_to_2026-11-06.md có thật (job Winston done ≠ xong). Báo cáo tuần CHƯA gửi. Kiểm 11-09 sau sync 23:45 xem Price có bị ghi đè lại.
- Escalation mở: retro-pattern-recurring-dd-multi-round-assumption-unlocked (A/B/C, khuyến nghị B). KHÔNG mở question trùng.
- DD-5F 20 mã (skill due-diligence bước 3c mới): cụm1+2 xong, báo user. Cụm3 HPG/MBB/TCH/SIP/HHS fix jobs Taylor_20261107_1316xx; cụm4 DDV/NT2/PVP/PVT/TV2 addendum xong. Việc kế: claim, skeptic cụm4 (báo cáo ≤350 từ), báo user bảng cụm3+4 + tổng kết. KHÔNG tự ghi dd_price_zones/moat_tags.
- Chờ user: quy ước "chặt-3c" cho model cũ; Winston sửa bigquery_dictionary.json mô tả GPM_P0 (thực tế TTM: GPM/NPM/EBITM/EBITDA_P0; quý: Revenue_P0/NP_P0).
- Chờ user OK cài 2 cron work-tree (build mỗi giờ + verify 07:30; backup crontab trước).
- Còn từ 05/11: chờ user quyết 'thẻ tần suất nền' Livermore; macro TE Làn 2; pnj-bctc-q3-review-trigger; approve_plan_simple.sh thiếu --dry-run; 2 câu bus Wags treo.

## Luật hiện hành
dd-flag-rules-20261102 (mã cờ loại khỏi candidate; DD base = sổ sách/NPV 0; r gắn lãi huy động; email DD chỉ khi user báo); moat/5F ≤1 lần/năm/mã.

## Mốc
Sáng 09/11: kiểm run 20:40 injector DISC, fill NNC/FPT/TV1; nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore H20 03/12; commodity 11-25; BĐS 11-26; LAG 12-15; audit đo lường ~12-27.
Bài học 07/11: không ghi "bài học" vào brief/skill khi chưa verify với bigquery_dictionary.json; pilot 1 mã trước fan-out ≥5.

