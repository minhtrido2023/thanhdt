# A2 — BACKFILL_REPORT (22/11/2026)

Sinh bởi bin/dd_ledger_backfill_skeptic_final.py; số trong báo cáo đo trên kb/dd_price_zones.json của worktree sau backfill.

## 1. Bảng đếm (rev cuối mỗi mã, 36 mã)

| nhãn | số mã |
|---|---|
| CONFIRMED | 15 |
| FIXED_UNVERIFIED | 21 |
| REFUTED_OPEN | 0 |
| NONE | 0 |

Baseline JSON (kb/projects/dd-baseline-20261122.json): CONFIRMED 19 / REFUTED 16 / OTHER 1. Review ghi 20/16.
Tái chạy `classify` của dd_baseline_snapshot trên cách chọn rev-cuối theo luật sổ (dd_date, rev) cho 19/15/2: chênh DUY NHẤT là PAT — baseline lấy PAT@2026-11-14#4 (REFUTED) còn luật sổ chọn PAT@2026-11-17#2 (r5, 'CHƯA chạy skeptic trên r5' ⇒ OTHER). OTHER còn lại = SZL. Không ép khớp.

## 2. Lệch so với baseline — từng mã (rev cuối)

| mã | rev | baseline | luật mới | basis |
|---|---|---|---|---|
| HHS | 4 | CONFIRMED | FIXED_UNVERIFIED | ambiguous_backfill |
| MSB | 1 | CONFIRMED | FIXED_UNVERIFIED | ambiguous_backfill |
| PAT | 2 | OTHER | FIXED_UNVERIFIED | ambiguous_backfill |
| PNJ | 1 | CONFIRMED | FIXED_UNVERIFIED | ambiguous_backfill |
| SCL | 5 | CONFIRMED | FIXED_UNVERIFIED | ambiguous_backfill |
| SZL | 2 | OTHER | FIXED_UNVERIFIED | ambiguous_backfill |

Lý do chung: baseline chỉ đếm chữ CONFIRMED/REFUTED; luật A2 yêu cầu CONFIRMED là vòng cuối VÀ không đính chính số/vùng sau đó ⇒ 4 mã (HHS r4, SCL r5, MSB, PNJ) có CONFIRMED kèm đính chính/phần không xác nhận bị hạ FIXED_UNVERIFIED (mơ hồ); PAT r5 + SZL r3c baseline 'OTHER' nay FIXED_UNVERIFIED (đã đính chính, chưa chạy lại skeptic). REFUTED-nhãn baseline đều thành FIXED_UNVERIFIED vì mọi bản đều ghi đã áp (REFUTED_OPEN = 0 sau khi sửa bắt 'áp r2'/'Taylor sửa').

## 3. Bốn mã bắt buộc nêu rõ

### PNJ (rev cuối 1, entry #78) → **FIXED_UNVERIFIED** [ambiguous_backfill]

> skeptic_status (nguyên văn): vòng 1 fundamental-skeptic CONFIRMED (medium) cho giữ loại; khối định giá KHÔNG xác nhận — 10 thay đổi đã áp ở r2 (bỏ nhãn mù giá, biên gộp trước dự phòng, vay NH, TM17, sàn giá phát hành BVPS, §7 park=0, điều kiện Q4, bỏ bear không cơ sở + g=0, WARNING quản trị, bảng §2); chưa chạy vòng 2

### PAT (rev cuối 2, entry #92) → **FIXED_UNVERIFIED** [ambiguous_backfill]

> skeptic_status (nguyên văn): r5 (22/11, user duyệt) áp 7 mục từ skeptic r4; CHƯA chạy skeptic trên r5 (Taylor khuyến nghị bác/xác nhận lựa chọn đọc H1/26 'sạch'). Mike 22/11: assumptions md5 872a9b82 khớp lock, chạy lại model_r5/bridge_sens_r5/selfcheck_r5 ⇒ cùng số (chênh chỉ nhiễu float), đường độc lập 66.475 (+0,0079%). Số lấy theo dispatch, Taylor chưa tự đo: 39,4 + 'UHY ngoại trừ', GTGD 1,01/0,60 tỷ, PAT +1% vs P4 TQ +19,5%, các số skeptic r4 −4.826/+6.409.

### QTP (rev cuối 3, entry #89) → **FIXED_UNVERIFIED** [ambiguous_backfill]

> skeptic_status (nguyên văn): fundamental-skeptic vòng 1 (r3): INCONCLUSIVE; vòng 2 (r3b): CONFIRMED, độ tin cậy trung bình; đã áp đính chính (r3c: lỗi bù FOM+VC 2030–31, điều kiện huỷ có ngày, EVN bên mua bị ép biên). Chưa vào sleeve discretionary.

### SZL (rev cuối 2, entry #67) → **FIXED_UNVERIFIED** [ambiguous_backfill]

> skeptic_status (nguyên văn): r3c (09/11, cụm 3b): A (RONIC=Ke) skeptic cuối r3b xác nhận cài đúng; B cài sai khung ở r3b đã sửa ở r3c (khung BÁN, KTPL trên lãi vốn sau thuế) — r3c Mike kiểm cơ học (không skeptic vòng nữa, circuit-breaker): tâm/P90 hai cỡ nằm đúng khoảng skeptic độc lập dựng lại; lỗi văn bản ghi ở SZL/ERRATA_final_skeptic_20261109.md


## 4. TOÀN BỘ ca mơ hồ (basis=ambiguous_backfill → gán FIXED_UNVERIFIED; Mike xác nhận tay)

- #4 HPG@2026-10-31#1: CONFIRMED (medium; B1/B2 đã sửa; v3)

- #5 MBB@2026-10-31#1: CONFIRMED (medium; 1 BLOCKING MBV đã xử)

- #11 PVT@2026-10-29#1: CONFIRMED phân loại NON; định giá đã đính chính (REPORT §14)

- #22 HPG@2026-10-31#2: CONFIRMED (medium; B1/B2 đã sửa; v3)

- #23 MBB@2026-10-31#2: CONFIRMED (medium; 1 BLOCKING MBV đã xử)

- #25 HPG@2026-10-31#3: CONFIRMED (medium; B1/B2 đã sửa; v3)

- #30 TV1@2026-11-02#5: định giá nội tại dựng mù giá (khoá md5 trước khi so giá) + phản biện độc lập mù giá + phản biện báo cáo cuối (tái lập byte-for-byte; sửa cân bằng cờ kế toán) 

- #31 MVC@2026-11-03#1: định giá SOTP dựng mù giá (khoá md5 calc/LOCK_md5*.txt trước khi so giá) + fundamental-skeptic CONFIRMED (12 đính chính đã áp; tâm/vùng không đổi)

- #67 SZL@2026-10-26#2: r3c (09/11, cụm 3b): A (RONIC=Ke) skeptic cuối r3b xác nhận cài đúng; B cài sai khung ở r3b đã sửa ở r3c (khung BÁN, KTPL trên lãi vốn sau thuế) — r3c Mike kiểm cơ học (không skeptic vòng nữa, circuit-breaker): tâm/P90 hai cỡ nằm đúng khoảng skeptic độc lập dựng lại; lỗi văn bản ghi ở SZL/ERRATA_final_skeptic_20261109.md

- #72 MSB@2026-11-09#1: r2 (09/11): skeptic r1 CONFIRMED (medium) với 7 đính chính câu chữ/độ nhạy (room tín dụng đã quan sát, phải thu RRTD 4.101, NPL, kịch bản XẤU bất đối xứng 11%→12% ⇒ tâm +2,2%…); Taylor áp, Mike kiểm cơ học tâm 13.018 (lệch +18 đ so với cận trên 13.000); không đảo nhãn; KHÔNG skeptic vòng 3. ERRATA: MSB/ERRATA_r1_skeptic.md

- #73 HHS@2026-11-01#4: r4 (10/11): fundamental-skeptic CONFIRMED (medium; tái tính độc lập khớp tới đồng, không đổi nhãn); required_change vòng 2 đã áp (Taylor_20261110_040253)

- #74 SCL@2026-10-29#5: r4 (10/11): fundamental-skeptic CONFIRMED (medium; tái tính độc lập khớp tới đồng, không đổi nhãn); required_change vòng 2 đã áp (Taylor_20261110_040253)

- #78 PNJ@2026-11-14#1: vòng 1 fundamental-skeptic CONFIRMED (medium) cho giữ loại; khối định giá KHÔNG xác nhận — 10 thay đổi đã áp ở r2 (bỏ nhãn mù giá, biên gộp trước dự phòng, vay NH, TM17, sàn giá phát hành BVPS, §7 park=0, điều kiện Q4, bỏ bear không cơ sở + g=0, WARNING quản trị, bảng §2); chưa chạy vòng 2

- #82 PAT@2026-11-14#4: skeptic lần 2 (15/11) mù giá hai chiều: lạc quan REFUTED nhẹ (tâm hiệu chỉnh 56.100, −13,4%: nút T bất đối xứng, vận chuyển 4,69%, O1), bi quan CONFIRMED (68.000, +5%: P×T, chi phí theo chế độ); 20 số khớp ảnh BCTC, tái lập 64.736; tâm 64.700 giữ (hiệu chỉnh trái chiều, nhỏ hơn bất định nút T); chưa có tờ trình GD bên liên quan DLC để đóng nút T; báo cáo NĐT đã gửi email 15/11

- #85 PAT@2026-11-17#1: phản biện user 17/11: 4 agent kiểm dữ kiện + quant-skeptic cohort cổ tức (CONFIRMED, tin cậy TB, có đính chính); 2 skeptic mù giá trên r3 66.864 (lạc quan CONFIRMED 67.000–71.500; bi quan REFUTED quá cao ~57.500) → 1 vòng đính chính valuer mới → r4; CHƯA chạy skeptic trên r4

- #89 QTP@2026-11-17#3: fundamental-skeptic vòng 1 (r3): INCONCLUSIVE; vòng 2 (r3b): CONFIRMED, độ tin cậy trung bình; đã áp đính chính (r3c: lỗi bù FOM+VC 2030–31, điều kiện huỷ có ngày, EVN bên mua bị ép biên). Chưa vào sleeve discretionary.

- #92 PAT@2026-11-17#2: r5 (22/11, user duyệt) áp 7 mục từ skeptic r4; CHƯA chạy skeptic trên r5 (Taylor khuyến nghị bác/xác nhận lựa chọn đọc H1/26 'sạch'). Mike 22/11: assumptions md5 872a9b82 khớp lock, chạy lại model_r5/bridge_sens_r5/selfcheck_r5 ⇒ cùng số (chênh chỉ nhiễu float), đường độc lập 66.475 (+0,0079%). Số lấy theo dispatch, Taylor chưa tự đo: 39,4 + 'UHY ngoại trừ', GTGD 1,01/0,60 tỷ, PAT +1% vs P4 TQ +19,5%, các số skeptic r4 −4.826/+6.409.


Tổng mơ hồ: 17/95

## 5. audited_fy_missing

true: #93 VLB@2026-11-22#1, #94 VLB@2026-11-22#2

Không gán true nhưng có nhắc (Mike xem): #54 PVT notes 'ý kiến kiểm toán 2025 treo' (BCTC đã có, ý kiến treo ≠ thiếu); #91 VCB 'Số BCTC KT 2025 … CHƯA render lại từ PDF' (đã có số, chưa đối chiếu PDF).

## 6. skeptic_verdict_path (best-effort, tên tự nhiên lớn nhất trong thư mục nguồn có chứa mã)

Số entry có path: 54/95; null: 41 (NONE luôn null). Mike nên soát tay các mã dưới (nhiều ứng viên):

- #7 NNC#1: chọn `agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R4_20261103.md` trong 3 ứng viên: SKEPTIC_20261031.md; SKEPTIC_R3_20261103.md; SKEPTIC_R4_20261103.md
- #9 DGC#1: chọn `agents/Taylor/research/dd_DGC_20261029/inputs/ERRATA_r11_skeptic_round5.md` trong 2 ứng viên: ERRATA_r10_skeptic_round4.md; ERRATA_r11_skeptic_round5.md
- #24 NNC#2: chọn `agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R4_20261103.md` trong 3 ứng viên: SKEPTIC_20261031.md; SKEPTIC_R3_20261103.md; SKEPTIC_R4_20261103.md
- #26 TV1#1: chọn `agents/Taylor/research/dd_TV1_20261102/SKEPTIC_20261102.md` trong 5 ứng viên: SKEPTIC2_20261102.md; SKEPTIC3_20261102.md; SKEPTIC4_20261102.md; SKEPTIC5_20261102.md; SKEPTIC_20261102.md
- #27 TV1#2: chọn `agents/Taylor/research/dd_TV1_20261102/SKEPTIC_20261102.md` trong 5 ứng viên: SKEPTIC2_20261102.md; SKEPTIC3_20261102.md; SKEPTIC4_20261102.md; SKEPTIC5_20261102.md; SKEPTIC_20261102.md
- #28 TV1#3: chọn `agents/Taylor/research/dd_TV1_20261102/SKEPTIC_20261102.md` trong 5 ứng viên: SKEPTIC2_20261102.md; SKEPTIC3_20261102.md; SKEPTIC4_20261102.md; SKEPTIC5_20261102.md; SKEPTIC_20261102.md
- #29 TV1#4: chọn `agents/Taylor/research/dd_TV1_20261102/SKEPTIC_20261102.md` trong 5 ứng viên: SKEPTIC2_20261102.md; SKEPTIC3_20261102.md; SKEPTIC4_20261102.md; SKEPTIC5_20261102.md; SKEPTIC_20261102.md
- #31 MVC#1: chọn `agents/Taylor/research/dd_MVC_20261103/SKEPTIC_R7_20261103.md` trong 4 ứng viên: SKEPTIC2_20261103.md; SKEPTIC4_20261103.md; SKEPTIC_20261103.md; SKEPTIC_R7_20261103.md
- #32 MVC#2: chọn `agents/Taylor/research/dd_MVC_20261103/SKEPTIC_R7_20261103.md` trong 4 ứng viên: SKEPTIC2_20261103.md; SKEPTIC4_20261103.md; SKEPTIC_20261103.md; SKEPTIC_R7_20261103.md
- #33 MVC#3: chọn `agents/Taylor/research/dd_MVC_20261103/SKEPTIC_R7_20261103.md` trong 4 ứng viên: SKEPTIC2_20261103.md; SKEPTIC4_20261103.md; SKEPTIC_20261103.md; SKEPTIC_R7_20261103.md
- #34 NNC#3: chọn `agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R4_20261103.md` trong 3 ứng viên: SKEPTIC_20261031.md; SKEPTIC_R3_20261103.md; SKEPTIC_R4_20261103.md
- #36 MVC#5: chọn `agents/Taylor/research/dd_MVC_20261103/SKEPTIC_R7_20261103.md` trong 4 ứng viên: SKEPTIC2_20261103.md; SKEPTIC4_20261103.md; SKEPTIC_20261103.md; SKEPTIC_R7_20261103.md
- #38 NNC#2: chọn `agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R4_20261103.md` trong 3 ứng viên: SKEPTIC_20261031.md; SKEPTIC_R3_20261103.md; SKEPTIC_R4_20261103.md
- #40 NNC#3: chọn `agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R4_20261103.md` trong 3 ứng viên: SKEPTIC_20261031.md; SKEPTIC_R3_20261103.md; SKEPTIC_R4_20261103.md
- #41 MVC#7: chọn `agents/Taylor/research/dd_MVC_20261103/SKEPTIC_R7_20261103.md` trong 4 ứng viên: SKEPTIC2_20261103.md; SKEPTIC4_20261103.md; SKEPTIC_20261103.md; SKEPTIC_R7_20261103.md
- #81 PAT#3: chọn `agents/Taylor/research/dd_PAT_objective_20261114/skeptic/skeptic_pessimistic.md` trong 4 ứng viên: skeptic2_optimistic_r2.md; skeptic2_pessimistic_r2.md; skeptic_optimistic.md; skeptic_pessimistic.md
- #82 PAT#4: chọn `agents/Taylor/research/dd_PAT_objective_20261114/skeptic/skeptic_pessimistic.md` trong 4 ứng viên: skeptic2_optimistic_r2.md; skeptic2_pessimistic_r2.md; skeptic_optimistic.md; skeptic_pessimistic.md
- #85 PAT#1: chọn `agents/Taylor/research/dd_PAT_rebuttal_20261117/C/skeptic/skeptic_pessimistic_r3.md` trong 2 ứng viên: skeptic_optimistic_r3.md; skeptic_pessimistic_r3.md
- #86 DBC#1: chọn `agents/Taylor/research/dd_DBC_20261118/skeptic_r2.md` trong 2 ứng viên: skeptic_r1.md; skeptic_r2.md
- #91 VCB#1: chọn `agents/Taylor/research/dd_VCB_20261117/skeptic_r1_corrections.md` trong 2 ứng viên: skeptic_r1_applied.md; skeptic_r1_corrections.md
- #92 PAT#2: chọn `agents/Taylor/research/dd_PAT_rebuttal_20261117/C/skeptic/skeptic_pessimistic_r3.md` trong 2 ứng viên: skeptic_optimistic_r3.md; skeptic_pessimistic_r3.md


---
# VÒNG 2 (arch-review R1) — cập nhật 22/11 (commit 47bc1c02d, wt-1574033826936660078)
Lệnh: `python3 bin/dd_ledger_backfill_skeptic_final.py --redo --write` (gỡ 4 trường v1 rồi tính lại). Output thô:

```
TOÀN SỔ (mọi entry): {'CONFIRMED': 20, 'FIXED_UNVERIFIED': 63, 'REFUTED_OPEN': 1, 'NONE': 11} tổng 95
NHIỀU ỨNG VIÊN ⇒ null: TV1@2026-11-02#2 ['agents/Taylor/research/dd_TV1_20261102/SKEPTIC2_20261102.md', 'agents/Taylor/research/dd_TV1_20261102/SKEPTIC_20261102.md']
NHIỀU ỨNG VIÊN ⇒ null: TV1@2026-11-02#3 ['agents/Taylor/research/dd_TV1_20261102/SKEPTIC2_20261102.md', 'agents/Taylor/research/dd_TV1_20261102/SKEPTIC3_20261102.md', 'agents/Taylor/research/dd_TV1_20261102/SKEPTIC4_20261102.md', 'agents/Taylor/research/dd_TV1_20261102/SKEPTIC_20261102.md']
NHIỀU ỨNG VIÊN ⇒ null: TV1@2026-11-02#4 ['agents/Taylor/research/dd_TV1_20261102/SKEPTIC2_20261102.md', 'agents/Taylor/research/dd_TV1_20261102/SKEPTIC3_20261102.md', 'agents/Taylor/research/dd_TV1_20261102/SKEPTIC4_20261102.md', 'agents/Taylor/research/dd_TV1_20261102/SKEPTIC5_20261102.md', 'agents/Taylor/research/dd_TV1_20261102/SKEPTIC_20261102.md']
NHIỀU ỨNG VIÊN ⇒ null: MVC@2026-11-03#2 ['agents/Taylor/research/dd_MVC_20261103/SKEPTIC2_20261103.md', 'agents/Taylor/research/dd_MVC_20261103/SKEPTIC_20261103.md']
NHIỀU ỨNG VIÊN ⇒ null: MVC@2026-11-03#3 ['agents/Taylor/research/dd_MVC_20261103/SKEPTIC2_20261103.md', 'agents/Taylor/research/dd_MVC_20261103/SKEPTIC_20261103.md']
NHIỀU ỨNG VIÊN ⇒ null: MVC@2026-11-03#5 ['agents/Taylor/research/dd_MVC_20261103/SKEPTIC2_20261103.md', 'agents/Taylor/research/dd_MVC_20261103/SKEPTIC4_20261103.md', 'agents/Taylor/research/dd_MVC_20261103/SKEPTIC_20261103.md']
NHIỀU ỨNG VIÊN ⇒ null: NNC@2026-11-03#2 ['agents/Taylor/research/dd_NNC_20261030/SKEPTIC_20261031.md', 'agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R3_20261103.md', 'agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R4_20261103.md']
NHIỀU ỨNG VIÊN ⇒ null: NNC@2026-11-03#3 ['agents/Taylor/research/dd_NNC_20261030/SKEPTIC_20261031.md', 'agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R3_20261103.md', 'agents/Taylor/research/dd_NNC_20261030/SKEPTIC_R4_20261103.md']
NHIỀU ỨNG VIÊN ⇒ null: MVC@2026-11-03#7 ['agents/Taylor/research/dd_MVC_20261103/SKEPTIC2_20261103.md', 'agents/Taylor/research/dd_MVC_20261103/SKEPTIC4_20261103.md', 'agents/Taylor/research/dd_MVC_20261103/SKEPTIC_20261103.md', 'agents/Taylor/research/dd_MVC_20261103/SKEPTIC_R7_20261103.md']
NHIỀU ỨNG VIÊN ⇒ null: PAT@2026-11-14#4 ['agents/Taylor/research/dd_PAT_objective_20261114/skeptic/skeptic2_optimistic_r2.md', 'agents/Taylor/research/dd_PAT_objective_20261114/skeptic/skeptic2_pessimistic_r2.md', 'agents/Taylor/research/dd_PAT_objective_20261114/skeptic/skeptic_optimistic.md', 'agents/Taylor/research/dd_PAT_objective_20261114/skeptic/skeptic_pessimistic.md']
NHIỀU ỨNG VIÊN ⇒ null: PAT@2026-11-17#1 ['agents/Taylor/research/dd_PAT_rebuttal_20261117/C/skeptic/skeptic_optimistic_r3.md', 'agents/Taylor/research/dd_PAT_rebuttal_20261117/C/skeptic/skeptic_pessimistic_r3.md']
NHIỀU ỨNG VIÊN ⇒ null: VCB@2026-11-17#1 ['agents/Taylor/research/dd_VCB_20261117/skeptic_r1_applied.md', 'agents/Taylor/research/dd_VCB_20261117/skeptic_r1_corrections.md']
NHIỀU ỨNG VIÊN ⇒ null: PAT@2026-11-17#2 ['agents/Taylor/research/dd_PAT_rebuttal_20261117/C/skeptic/skeptic_optimistic_r3.md', 'agents/Taylor/research/dd_PAT_rebuttal_20261117/C/skeptic/skeptic_pessimistic_r3.md']
entry đã thêm trường: 95 / 95
rev-cuối-mỗi-mã: {'CONFIRMED': 15, 'FIXED_UNVERIFIED': 21, 'REFUTED_OPEN': 0, 'NONE': 0} tổng 36
AMBIG #4 HPG@2026-10-31#1 → FIXED_UNVERIFIED: CONFIRMED (medium; B1/B2 đã sửa; v3)
AMBIG #5 MBB@2026-10-31#1 → FIXED_UNVERIFIED: CONFIRMED (medium; 1 BLOCKING MBV đã xử)
AMBIG #8 DRI@2026-10-30#1 → FIXED_UNVERIFIED: CONFIRMED (medium; định giá r4)
AMBIG #11 PVT@2026-10-29#1 → FIXED_UNVERIFIED: CONFIRMED phân loại NON; định giá đã đính chính (REPORT §14)
AMBIG #22 HPG@2026-10-31#2 → FIXED_UNVERIFIED: CONFIRMED (medium; B1/B2 đã sửa; v3)
AMBIG #23 MBB@2026-10-31#2 → FIXED_UNVERIFIED: CONFIRMED (medium; 1 BLOCKING MBV đã xử)
AMBIG #25 HPG@2026-10-31#3 → FIXED_UNVERIFIED: CONFIRMED (medium; B1/B2 đã sửa; v3)
AMBIG #30 TV1@2026-11-02#5 → FIXED_UNVERIFIED: định giá nội tại dựng mù giá (khoá md5 trước khi so giá) + phản biện độc lập mù giá + phản biện báo cáo cuối (tái lập byte-for-byte; sửa cân bằng cờ kế toán) 
AMBIG #31 MVC@2026-11-03#1 → FIXED_UNVERIFIED: định giá SOTP dựng mù giá (khoá md5 calc/LOCK_md5*.txt trước khi so giá) + fundamental-skeptic CONFIRMED (12 đính chính đã áp; tâm/vùng không đổi)
AMBIG #33 MVC@2026-11-03#3 → FIXED_UNVERIFIED: định giá SOTP r3 mù giá (khoá md5 r3/calc/LOCK_md5_r3.txt); fundamental-skeptic vòng 3 CONFIRMED (medium) tâm 20.181 và vùng 17.500–22.900; r4 chỉ đổi thang nhãn (có điều kiện), số mô hình không đổi
AMBIG #34 NNC@2026-10-31#3 → FIXED_UNVERIFIED: mô hình nhất quán MVC r3 qua skeptic vòng 3 (CONFIRMED medium, phía MVC); NNC rev 3 chưa có vòng phản biện riêng
AMBIG #67 SZL@2026-10-26#2 → FIXED_UNVERIFIED: r3c (09/11, cụm 3b): A (RONIC=Ke) skeptic cuối r3b xác nhận cài đúng; B cài sai khung ở r3b đã sửa ở r3c (khung BÁN, KTPL trên lãi vốn sau thuế) — r3c Mike kiểm cơ học (không skeptic vòng nữa, circuit-breaker): tâm/P90 hai cỡ nằm đúng khoảng skeptic độc lập dựng lại; lỗi văn bản ghi ở SZL/ERRATA_final_skeptic_20261109.md
AMBIG #72 MSB@2026-11-09#1 → FIXED_UNVERIFIED: r2 (09/11): skeptic r1 CONFIRMED (medium) với 7 đính chính câu chữ/độ nhạy (room tín dụng đã quan sát, phải thu RRTD 4.101, NPL, kịch bản XẤU bất đối xứng 11%→12% ⇒ tâm +2,2%…); Taylor áp, Mike kiểm cơ học tâm 13.018 (lệch +18 đ so với cận trên 13.000); không đảo nhãn; KHÔNG skeptic vòng 3. ERRATA: MSB/ERRATA_r1_skeptic.md
AMBIG #73 HHS@2026-11-01#4 → FIXED_UNVERIFIED: r4 (10/11): fundamental-skeptic CONFIRMED (medium; tái tính độc lập khớp tới đồng, không đổi nhãn); required_change vòng 2 đã áp (Taylor_20261110_040253)
AMBIG #74 SCL@2026-10-29#5 → FIXED_UNVERIFIED: r4 (10/11): fundamental-skeptic CONFIRMED (medium; tái tính độc lập khớp tới đồng, không đổi nhãn); required_change vòng 2 đã áp (Taylor_20261110_040253)
AMBIG #78 PNJ@2026-11-14#1 → FIXED_UNVERIFIED: vòng 1 fundamental-skeptic CONFIRMED (medium) cho giữ loại; khối định giá KHÔNG xác nhận — 10 thay đổi đã áp ở r2 (bỏ nhãn mù giá, biên gộp trước dự phòng, vay NH, TM17, sàn giá phát hành BVPS, §7 park=0, điều kiện Q4, bỏ bear không cơ sở + g=0, WARNING quản trị, bảng §2); chưa chạy vòng 2
AMBIG #82 PAT@2026-11-14#4 → FIXED_UNVERIFIED: skeptic lần 2 (15/11) mù giá hai chiều: lạc quan REFUTED nhẹ (tâm hiệu chỉnh 56.100, −13,4%: nút T bất đối xứng, vận chuyển 4,69%, O1), bi quan CONFIRMED (68.000, +5%: P×T, chi phí theo chế độ); 20 số khớp ảnh BCTC, tái lập 64.736; tâm 64.700 giữ (hiệu chỉnh trái chiều, nhỏ hơn bất định nút T); chưa có tờ trình GD bên liên quan DLC để đóng nút T; báo cáo NĐT đã gửi email 15/11
AMBIG #85 PAT@2026-11-17#1 → FIXED_UNVERIFIED: phản biện user 17/11: 4 agent kiểm dữ kiện + quant-skeptic cohort cổ tức (CONFIRMED, tin cậy TB, có đính chính); 2 skeptic mù giá trên r3 66.864 (lạc quan CONFIRMED 67.000–71.500; bi quan REFUTED quá cao ~57.500) → 1 vòng đính chính valuer mới → r4; CHƯA chạy skeptic trên r4
AMBIG #89 QTP@2026-11-17#3 → FIXED_UNVERIFIED: fundamental-skeptic vòng 1 (r3): INCONCLUSIVE; vòng 2 (r3b): CONFIRMED, độ tin cậy trung bình; đã áp đính chính (r3c: lỗi bù FOM+VC 2030–31, điều kiện huỷ có ngày, EVN bên mua bị ép biên). Chưa vào sleeve discretionary.
AMBIG #92 PAT@2026-11-17#2 → FIXED_UNVERIFIED: r5 (22/11, user duyệt) áp 7 mục từ skeptic r4; CHƯA chạy skeptic trên r5 (Taylor khuyến nghị bác/xác nhận lựa chọn đọc H1/26 'sạch'). Mike 22/11: assumptions md5 872a9b82 khớp lock, chạy lại model_r5/bridge_sens_r5/selfcheck_r5 ⇒ cùng số (chênh chỉ nhiễu float), đường độc lập 66.475 (+0,0079%). Số lấy theo dispatch, Taylor chưa tự đo: 39,4 + 'UHY ngoại trừ', GTGD 1,01/0,60 tỷ, PAT +1% vs P4 TQ +19,5%, các số skeptic r4 −4.826/+6.409.
```

Ghi chú: master ĐÃ merge bản v1 (860f70026) nên so với master có 41 dòng bị THAY (nhãn/path) — thay bản ghi v1, đúng yêu cầu; so với gốc trước A2 (9958a58d0~1): +380/−0 (chỉ thêm).
