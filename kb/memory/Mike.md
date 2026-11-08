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

- [2026-11-08T02:36:01Z] 08/11 09:45 DD-5F status: 20 mã đều có ADDENDUM_5F. Jobs _1316xx/_1316xx hit usage_limited đêm qua NHƯNG artifact đã ghi (HPG/MBB/HHS fix có *_r1 backup + số mới; cụm4 DDV/NT2/PVP/PVT/TV2 addendum 17:22-17:24Z). Việc kế: skeptic cụm4 (5 Agent song song, ≤350 từ), fix, rồi báo bảng cụm3+4 + tổng kết 20 mã. Chờ user: chặt-3c; Winston sửa dictionary.
- [2026-11-08T02:42:37Z] 08/11 09:45 cụm4 skeptic xong: NT2/PVT/TV2 CONFIRMED (sửa văn bản), DDV/PVP REFUTED (DDV peer cắt một chiều -> nhãn TRONG ~12,4–13,4k; PVP headline phải là CAP 20.356 TRONG). Fix jobs Taylor_20261108_024219 DDV, _024220 PVP, _024223 NT2, _024225 PVT, _024226 TV2 (brief /tmp/dd5f/fix5_*.txt). Sau: claim, Mike đọc, báo user bảng cụm 3+4 + tổng kết 20 mã.
- [2026-11-08T02:50:30Z] 08/11 09:55 DD-5F 20/20 XONG (12 NARROW, 8 NONE, 0 WIDE; mọi mã không bền). Đã báo user bảng + tổng kết. Chờ user: (1) chặt-3c cho model cũ (2) Winston sửa bigquery_dictionary.json. Chưa ghi dd_price_zones/moat_tags/REPORT cũ. Dòng moat_tags đề xuất trong ADDENDUM_5F.md từng mã.
- [2026-11-08T03:52:06Z] 08/11 10:55 USER CHỐT: (1) KHÔNG áp 3c chặt — moat chỉ thêm khi bền, không trừ; headline = mô hình cơ sở hiện hành; bản chặt chỉ là độ nhạy. Đã sửa skill 3c (backup /tmp/due-diligence-SKILL.md.bak-20261108), brief template, banner+field final_convention_20261108 trong 20 ADDENDUM/SUMMARY_5F. (2) bigquery_dictionary.json GPM/EBITM/NPM/EBITDA_P0=TTM đã sửa + merge main 3c61532aa. 20/20 DD-5F xong. Còn: SCL lõi calc GPM lan WIDE 22.769->21.813 (REPORT_r2, chờ quyết).
- [2026-11-08T04:59:48Z] 08/11 12:05 code review tuần: 5/11 finding đã sửa (de28d1893). 6 hard-boundary giao Taylor_20261108_045937 (opus, worktree, no-merge) → khi xong: arch-reviewer (opus high, plan.py lõi) → merge → close_bus_question code-reviewer/cq-2026-11-08-hard-boundary (decided_by user: user nói 'làm theo khuyến nghị' 08/11).
- [2026-11-08T05:50:22Z] 08/11 12:52 arch-review vòng 1 NEEDS_CHANGES (plan.py net guard: TypeError str/rác + max floor SELL chặn exit LAG + cash_only 'false'). Vòng 2 Taylor_20261108_055010 (cùng nhánh fix/cq-hardcore-20261108, commit thêm). Xong → arch-reviewer lần cuối → merge → sau merge chạy tz_anchor_gate --update-baseline trading_bot/plan.py → close_bus_question code-reviewer/cq-2026-11-08-hard-boundary. Không lặp vòng 3 (circuit-breaker). Ghi chú: preflight_check.sh:63 vẫn coi mọi approved_by non-empty là duyệt (lệch với bot) — báo user.
- [2026-11-08T05:56:27Z] 08/11 13:05 USER CHỐT option B (DD multi-round): assumptions_md5 trong dd_price_zones (merge master, selfcheck 0 lỗi; entry mới từ 08/11 bắt buộc khoá, entry cũ miễn) + skill due-diligence thêm 3 luật (khoá giả định, pilot 1 mã+skeptic trước fan-out ≥5, bài học phải verify dictionary). Bus question đã đóng decided_by user. Từ nay khi ghi entry sổ mới PHẢI tính assumptions_md5.
- [2026-11-08T06:09:31Z] 08/11 13:15 code review tuần XONG: merge d3e481e37, baseline 603a892cf, bus question đóng. Còn: preflight_check.sh:63 lệch cổng approved_by; xác minh luật lệnh đối ứng DNSE/HOSE (Mafee/legal-vn); test --auto-otp trong cq_hardcore selfcheck:158-169 không kiểm được gì (non-blocking).
