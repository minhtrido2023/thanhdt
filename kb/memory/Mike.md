# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (cuối ngày 04/11 → 05/11)

## Đang chờ user
- DD DCM r5 XONG (tâm 24.326; dải A/B 24.192–24.459; giá 33.000 cao hơn tâm ~35,7%, nhãn ĐẮT). Báo cáo NĐT mới: agents/Taylor/research/dd_DCM_20261104/investor_report/DCM_DD_investor_report_20261105.pdf. CHƯA email (user báo mới gửi, 1 lần). Plan 05/11 có BUY DCM 33.000 LAG_LO (SpaceX 1000cp, ZaloPay 700cp) — nhắc user.
- Mike còn nợ cho DCM: chạy lại model_r5 (md5 LOCK), grep luật 18, render PDF, dd_price_zones rev=2 supersedes DCM@2026-11-04#1 + selfcheck, cập nhật kb/projects/dcm-dd-20261104.md, release claim topic:dd-dcm-20261104.
- Escalation mở: retro-pattern-recurring-dd-multi-round-assumption-unlocked (A khoá giả định / B = A + dd_price_zones từ chối khi md5 lệch / C giữ; khuyến nghị B). KHÔNG mở question trùng.
- Macro TE: Làn 1 xong+merge (A1/A2 b66165196; C1 bb0f8f4ba). Chờ user: làm Làn 2 (D1/D2/E1)? duyệt TE làm tầng CPI trong cpi_vn.py? Writer macro=bq_admin; bỏ B1 view PIT. Thiếu freshness: vn_interbank_3m, us_bond_2y, jp_usdjpy. Dọn worktree wt-macro-ind-1105, wt-te-crosscheck-20261105.
- Khác chờ user: email DRI r5/SCL r3 (chưa gửi); NNC r6/MVC r9 email chưa đối chiếu hộp thư (đừng gửi lại); pnj-bctc-q3-review-trigger; drift CANNOT_CHECK ZaloPay/SpaceX (câu hỏi 29/10 A/B); SZL; DGC vòng 6; TV2.
- Sau 15:00 05/11: kiểm fill TV1 (plan 04/11) còn bao nhiêu.

## Luật hiện hành (kb/projects/dd-flag-rules-20261102.md)
Mã có cờ loại khỏi candidate (không PARK, có CAPIT); DD base = sổ sách/NPV 0; r gắn lãi huy động; email DD chỉ khi user báo.

## Mốc
nav-loss-brake 11-09; DT CRISIS ~11/10; Livermore ~19/11; commodity 11-25; BĐS 11-26; LAG 12-15; crontab báo cáo quý trước 31/12; measurement audit ~12-27. Wakeup MISS 04/11 = 0/6.

- [2026-11-04T17:34:43Z] 05/11 00:55: DD DCM vòng 3 XONG: tâm 24.326 (A 24.192/B 24.459), PDF NĐT 20261105 (md5 08356b32…), sổ mức giá rev=2, KB pointer cập nhật, claim release. r5 CHƯA qua skeptic; CHƯA email — user báo 'gửi email' thì gửi đúng 1 lần (kiểm lại grep luật 18). Nhắc plan 05/11 BUY DCM 33.000 LAG_LO.
- [2026-11-04T18:27:43Z] 05/11 01:30: user rút BUY DCM khỏi plan 05/11; đã dispatch DollarBill_20261104_182729 (opus/medium) làm lại plan 2 account (flag-exception: BAL không có cơ sở loại mã có cờ + còn vùng mua thì được mua, phải ghi notes). Chờ kết quả → user duyệt lại plan trước 09:00.
- [2026-11-05T01:41:48Z] 05/11 08:50 ICT: user yêu cầu REDO DD toàn bộ 20 mã mùa BCTC Q3 + bảng P10-P90/tâm. Đã dispatch 5 job Taylor (opus/med, timeout 4h): A=Taylor_20261105_014125 (MBB FPT HPG HHS), B=..014127 (DGC DDV PVP PVT), C=..014130 (SIP SCL TV1 TV2), D=..014133 (NT2 SAS SZL TCH), E=..014135 (NNC DRI MVC). DCM giữ r5 (đã đúng luật 03/11). Output: agents/Taylor/research/dd_redo_20261105/<MÃ>/SUMMARY.json. Bước kế: fundamental-skeptic từng mã khi xong, rồi ledger rev mới + bảng tổng hợp gửi user. Claim topic:dd-redo-20261105. Không PDF/email.
