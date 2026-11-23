# Working memory — Taylor
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Taylor.

> Sổ tay việc ĐANG MỞ. File này bơm vào đầu MỌI phiên/dispatch của Taylor ⇒ mỗi dòng thừa là
> context phải trả tiền lại từ đầu, mỗi lần.

## Ghi gì vào đây (đọc 1 lần)
- Chỉ 2 loại: (a) việc CÒN TREO — đang chờ ai, chờ gì; (b) chốt làm ĐỔI CÁCH LÀM về sau.
- KHÔNG ghi "job X XONG, commit Y". git log + bus + `agents/Taylor/research/` đã giữ đủ; chép lại
  vào đây chỉ làm mọi phiên sau phải đọc lại một lần nữa.
- Mỗi entry ≤ 2 dòng: KẾT LUẬN trước, bỏ quá trình.
- Việc treo mà xong rồi thì XOÁ dòng đó, đừng ghi đè một dòng "đã xong" lên trên.
- Quy tắc dùng cho CẢ ĐỘI ⇒ đề xuất vào `kb/coding_guidelines.md` (§13: ghi ra `.proposed`),
  không nuôi riêng trong file này.
- Quá 12 entry thì phần cũ tự sang `kb/memory/archive/Taylor_history.md` — không mất, không auto-load.

- [2026-11-23T00:01:20Z] [dd-pnj rebuild 23/11] XONG job Taylor_20261122_234426: REPORT_rev4 tam 4.205 (vung 2.212-6.198), skeptic r3 REFUTED (O2 phat kep) — CHO Mike ap LEDGER_PROPOSAL (REFUTED_OPEN) / user quyet vong 3
- [2026-11-23T00:01:59Z] [VCB rebuild 23/11] XONG job Taylor_20261122_234428: REPORT_rev3 tâm 36.000 vùng 31.200–42.500, skeptic r3 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_VCB.json
- [2026-11-23T00:04:04Z] [dd-MSB rebuild 23/11] XONG job Taylor_20261122_234430: REPORT_r4 tam 13.042 (skeptic r3 CONFIRMED, md5 b3ec7a51) — CHO Mike ap LEDGER_PROPOSAL_MSB.json (can entry buoc1 truoc tool)
- [2026-11-23T00:08:16Z] [DD DCM rebuild 23/11] XONG job Taylor_20261122_234422: REPORT_rev8 tâm 26.780, skeptic r3 REFUTED — CHỜ Mike áp LEDGER_PROPOSAL_DCM.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T00:11:00Z] ĐANG DỞ: job Taylor_20261123_001048 DD LLM rebuild | NEXT: đọc skeptic r1 + REPORT.md dd_LLM_20261118
- [2026-11-23T00:11:01Z] ĐANG DỞ: job Taylor_20261123_001043 DD CST rebuild | NEXT: đọc skeptic r1 + REPORT.md dd_CST_20261111
- [2026-11-23T00:11:03Z] ĐANG DỞ: job Taylor_20261123_001050 DD HHS rebuild | NEXT: đọc skeptic r1 + HHS_r4.md
- [2026-11-23T00:11:03Z] ĐANG DỞ: job Taylor_20261123_001046 DD CSV rebuild | NEXT: đọc skeptic r1 + REPORT.md dd_lagcand_20261109/CSV
- [2026-11-23T00:11:06Z] ĐANG DỞ: job Taylor_20261123_001052 DD VLB rebuild (dd_VLB_20261122) | NEXT: đọc skeptic r1 + report hiện hành
- [2026-11-23T00:16:52Z] ĐANG DỞ: job Taylor_20261123_001043 CST rev2 model xong (tâm 4.563/4.422 sau CK, calc_rev2/) | NEXT: viết REPORT_rev2.md → skeptic r2 → LEDGER_PROPOSAL_CST.json → bus+notify
- [2026-11-23T00:17:41Z] ĐANG DỞ: job Taylor_20261123_001050 HHS rev5: calc+LOCK xong (HHS/rev5/calc) | NEXT: viết HHS/REPORT_rev5.md → skeptic r2 → LEDGER_PROPOSAL_HHS.json
- [2026-11-23T00:18:26Z] ĐANG DỞ: job Taylor_20261123_001052 VLB r3: model/dcf_vlb_r3.py xong (tâm exdiv 42.800) | NEXT: assumptions_r3.json + REPORT_rev3.md → skeptic r2 → LEDGER_PROPOSAL_VLB.json
- [2026-11-23T00:21:41Z] ĐANG DỞ: job Taylor_20261123_001048 LLM REPORT_rev3 (tâm 28.834) skeptic r2 chạy nền log /tmp/llm_sk_r2.log | NEXT: LEDGER_PROPOSAL_LLM.json → bus+notify
- [2026-11-23T00:24:57Z] ĐANG DỞ: job Taylor_20261123_001046 CSV r3: skeptic r2 INCONCLUSIVE | NEXT: thêm tax shield + kd chiết khấu capex vay → REPORT_r4.md → skeptic r3 (vòng cuối) → LEDGER_PROPOSAL_CSV.json → bus+notify
- [2026-11-23T00:26:04Z] [VLB rebuild 23/11] XONG job Taylor_20261123_001052: REPORT_rev3 tâm exdiv 42.800 (r2 48.735), skeptic r2 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_VLB.json (REFUTED_OPEN); thiếu BCTC KT 2025
- [2026-11-23T00:26:06Z] [dd-HHS rev5 23/11] XONG job Taylor_20261123_001050: tâm 13.969 giữ, skeptic r3 INCONCLUSIVE (biên cao tầng HH1–HH4 + CK holding chờ user) — CHỜ Mike áp LEDGER_PROPOSAL_HHS.json (REFUTED_OPEN)
- [2026-11-23T00:28:21Z] ĐANG DỞ: job Taylor_20261123_001048 LLM REPORT_rev4 (tâm 32.376) skeptic r3 (vòng cuối) nền log /tmp/llm_sk_r3.log | NEXT: LEDGER_PROPOSAL_LLM.json → bus+notify
- [2026-11-23T00:28:38Z] [dd-CST rebuild 23/11] XONG job Taylor_20261123_001043: REPORT_rev3 tâm 6.022/5.837 sau CK, skeptic r3 REFUTED — CHỜ Mike áp LEDGER_PROPOSAL_CST.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T00:31:59Z] [dd-CSV rebuild 23/11] XONG job Taylor_20261123_001046: REPORT_r4 tâm 11.224 TRÊN vùng, skeptic r3 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_CSV.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T00:32:52Z] [dd-LLM rebuild 23/11] XONG job Taylor_20261123_001048: REPORT_rev4 tâm 32.376, skeptic r3 REFUTED — CHỜ Mike áp LEDGER_PROPOSAL_LLM.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T00:32:57Z] [dd-CSV 23/11] job Taylor_20261123_001046 đã đóng đủ (bus+notify): REPORT_r4 tâm 11.224, r3 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_CSV.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T00:35:08Z] ĐANG DỞ: job Taylor_20261123_003452 DD BSR rebuild | NEXT: đọc skeptic r1 + REPORT.md dd_lagcand_20261109/BSR
- [2026-11-23T00:35:11Z] ĐANG DỞ: job Taylor_20261123_003454 DD GAS rebuild | NEXT: đọc skeptic r1 + REPORT.md dd_lagcand_20261109/GAS
- [2026-11-23T00:35:12Z] ĐANG DỞ: job Taylor_20261123_003456 DD DBC rebuild | NEXT: đọc skeptic r1 + REPORT.md dd_DBC_20261118
- [2026-11-23T00:35:14Z] ĐANG DỞ: job Taylor_20261123_003458 DD POW rebuild | NEXT: đọc skeptic r1 + REPORT.md dd_POW_20261118
- [2026-11-23T00:35:20Z] ĐANG DỞ: job Taylor_20261123_003503 DD SZL rebuild | NEXT: đọc skeptic r1 + REPORT_r3c.md dd_redo_20261105/SZL
- [2026-11-23T05:01:21Z] ĐANG DỞ: job Taylor_20261123_050007 POW rev3: đã đọc skeptic r1; QCVN19 thầu tư vấn 2,98 tỷ (CBTT 19/10) | NEXT: định lượng capex VA1 từ tiền lệ QTP → calc_rev3 → REPORT_rev3.md → skeptic r2
- [2026-11-23T05:07:19Z] ĐANG DỞ: job Taylor_20261123_050001 BSR REPORT_rev3 (tâm 16.112) skeptic r2 chạy | NEXT: LEDGER_PROPOSAL_BSR.json → bus+notify
- [2026-11-23T05:07:42Z] ĐANG DỞ: job Taylor_20261123_050009 SZL REPORT_rev4 (tâm 27.397) skeptic r2 chạy nền log /tmp/szl_sk_r2.log | NEXT: LEDGER_PROPOSAL_SZL.json → bus+notify
- [2026-11-23T05:09:02Z] ĐANG DỞ: job Taylor_20261123_050007 POW REPORT_rev3 (tâm 9.064, lock md5 858632b7) — skeptic r2 đang chạy | NEXT: đọc skeptic/r2.json → LEDGER_PROPOSAL_POW.json → bus+notify
- [2026-11-23T05:11:48Z] ĐANG DỞ: job Taylor_20261123_050005 DBC REPORT_rev2 (tâm 17.317, md5 khoá 25d2e305) skeptic r2 chạy nền log /tmp/dbc_sk_r2.log | NEXT: LEDGER_PROPOSAL_DBC.json → bus+notify
- [2026-11-23T05:12:59Z] ĐANG DỞ: job Taylor_20261123_050001 BSR REPORT_rev4 (tâm 16.886) skeptic r3 vòng cuối | NEXT: LEDGER_PROPOSAL_BSR.json → bus+notify
- [2026-11-23T05:14:23Z] ĐANG DỞ: job Taylor_20261123_050003 GAS REPORT_rev3 (tâm 50.651) skeptic r2 đang chạy, log /tmp/gas_sk_r2.log | NEXT: LEDGER_PROPOSAL_GAS.json → bus+notify
- [2026-11-23T05:15:06Z] ĐANG DỞ: job Taylor_20261123_050007 POW REPORT_rev4 (tâm 9.387, lock 820f22c0) skeptic r3 vòng cuối | NEXT: LEDGER_PROPOSAL_POW.json → bus+notify
- [2026-11-23T05:15:23Z] ĐANG DỞ: job Taylor_20261123_050009 SZL REPORT_rev4b (tâm 25.852) skeptic r3 vòng cuối log /tmp/szl_sk_r3.log | NEXT: LEDGER_PROPOSAL_SZL.json → bus+notify
- [2026-11-23T05:16:39Z] [dd-BSR rebuild 23/11] XONG job Taylor_20261123_050001: REPORT_rev4 tâm 16.886, skeptic r3 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_BSR.json (REFUTED_OPEN) / user quyết VAT + V4a hydrotreating
- [2026-11-23T05:18:51Z] [dd-POW rebuild 23/11] XONG job Taylor_20261123_050007: REPORT_rev4 tâm 9.387 (vùng 6.966–11.808), skeptic r3 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_POW.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T05:20:28Z] ĐANG DỞ: job Taylor_20261123_050003 GAS REPORT_rev4 (tâm 51.652) skeptic r3 vòng cuối, log /tmp/gas_sk_r3.log | NEXT: LEDGER_PROPOSAL_GAS.json → bus+notify
- [2026-11-23T05:20:33Z] [dd-SZL rebuild 23/11] XONG job Taylor_20261123_050009: REPORT_rev4b tâm 25.852, skeptic r3 REFUTED (KTPL 2026 20% chưa áp; skeptic ước 24.793) — CHỜ Mike áp LEDGER_PROPOSAL_SZL.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T05:20:46Z] ĐANG DỞ: job Taylor_20261123_050005 DBC REPORT_rev3 (tâm 14.696, khoá 66d9fbc6) skeptic r3 vòng cuối log /tmp/dbc_sk_r3.log | NEXT: LEDGER_PROPOSAL_DBC.json → bus+notify
- [2026-11-23T05:23:42Z] [dd-DBC rebuild 23/11] XONG job Taylor_20261123_050005: REPORT_rev3 tâm 14.696, skeptic r3 REFUTED (BĐS dở dang 1.186 tỷ chưa tách; thuế TNDN chưa kiểm) — CHỜ Mike áp LEDGER_PROPOSAL_DBC.json (REFUTED_OPEN) / user quyết vòng 4
- [2026-11-23T05:23:54Z] [dd-GAS rebuild 23/11] XONG job Taylor_20261123_050003: REPORT_rev4 tâm 51.652, skeptic r3 CONFIRMED — CHỜ Mike áp LEDGER_PROPOSAL_GAS.json (cần entry bước1 trước tool)
- [2026-11-23T06:37:02Z] ĐANG DỞ: job Taylor_20261123_063642 DD VCP rebuild | NEXT: đọc skeptic r1 + REPORT.md dd_VCP_20261112
- [2026-11-23T06:37:04Z] ĐANG DỞ: job Taylor_20261123_063644 DD QTP rebuild | NEXT: đọc skeptic r1 + REPORT_r3c.md qtp_r3_envcapex_20261120
- [2026-11-23T06:37:09Z] ĐANG DỞ: job Taylor_20261123_063646 DD SCL rebuild (dd_dilution_update_20261110/SCL) | NEXT: đọc skeptic r1 + SCL_r4.md
- [2026-11-23T06:40:24Z] ĐANG DỞ: job Taylor_20261123_063642 VCP rev3: src khôi phục từ git ff5fe27cd^; nguồn mới /tmp/vcp_dl (BCTN2023) | NEXT: chuẩn hoá thuỷ văn theo SL thiết kế, ROE fade, thuế, KTPL → calc_rev3 → REPORT_rev3.md → skeptic r2
- [2026-11-23T06:45:29Z] ĐANG DỞ: job Taylor_20261123_063642 VCP model rev3 xong (calc_rev3, lock fd9d6dd3, tâm 35.826→34.522 sau CK) | NEXT: REPORT_rev3.md → skeptic r2 → LEDGER_PROPOSAL_VCP.json → bus+notify
- [2026-11-23T06:47:05Z] ĐANG DỞ: job Taylor_20261123_063646 SCL REPORT_rev6 (tâm 16.883 sau quyền CK5ty, khoá 7f0ee875) skeptic r2 đang chạy log /tmp/scl_sk_r2.log | NEXT: LEDGER_PROPOSAL_SCL.json → bus+notify
- [2026-11-23T06:47:25Z] ĐANG DỞ: job Taylor_20261123_063642 VCP REPORT_rev3 (tâm 34.522, lock fd9d6dd3) skeptic r2 chạy nền log /tmp/vcp_sk_r2.log | NEXT: LEDGER_PROPOSAL_VCP.json → bus+notify
- [2026-11-23T06:47:37Z] ĐANG DỞ: job Taylor_20261123_063644 QTP REPORT_rev4 (tâm 6.273, khoá 190b8294) skeptic r2 chạy | NEXT: LEDGER_PROPOSAL_QTP.json → bus+notify
- [2026-11-23T06:53:05Z] ĐANG DỞ: job Taylor_20261123_063646 SCL REPORT_rev6 (tâm 16.883) skeptic r3 vòng cuối, log /tmp/scl_sk_r3.log | NEXT: LEDGER_PROPOSAL_SCL.json → bus+notify
- [2026-11-23T06:53:47Z] ĐANG DỞ: job Taylor_20261123_063644 QTP REPORT_rev4b (tâm 6.294, khoá 91add832) skeptic r3 vòng cuối | NEXT: LEDGER_PROPOSAL_QTP.json → bus+notify
- [2026-11-23T06:54:00Z] ĐANG DỞ: job Taylor_20261123_063642 VCP REPORT_rev3b (tâm 32.605, lock 8d93c85b) skeptic r3 vòng cuối log /tmp/vcp_sk_r3.log | NEXT: LEDGER_PROPOSAL_VCP.json → bus+notify
- [2026-11-23T06:57:19Z] [dd-SCL rebuild 23/11] XONG job Taylor_20261123_063646: REPORT_rev6 tâm 16.883 (r4 21.339), skeptic r3 REFUTED (k chia NLĐ vs lá chắn thuế) — CHỜ Mike áp LEDGER_PROPOSAL_SCL.json (REFUTED_OPEN) / user quyết vòng 4
- [2026-11-23T06:57:46Z] [dd-QTP rebuild 23/11] XONG job Taylor_20261123_063644: REPORT_rev4b tâm 6.294 (r3c 7.701), skeptic r3 INCONCLUSIVE (ETS/hoàn trả mặt bằng/PPA/pha loãng) — CHỜ Mike áp LEDGER_PROPOSAL_QTP.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T06:59:29Z] [dd-VCP rebuild 23/11] XONG job Taylor_20261123_063642: REPORT_rev3b tâm 32.605 (rev2 40.273), skeptic r3 INCONCLUSIVE — CHỜ Mike áp LEDGER_PROPOSAL_VCP.json (REFUTED_OPEN) / user quyết vòng 3
- [2026-11-23T10:17:24Z] [SZL DD v3 23/11] XONG job Taylor_20261123_100922: REPORT_rev5 tâm 26.183 (vùng 22.740–29.700), skeptic r4 INCONCLUSIVE (vòng cuối) — CHỜ Mike áp LEDGER_PROPOSAL_SZL.json (REFUTED_OPEN)
- [2026-11-23T10:18:57Z] [DD DBC vong 3 23/11] XONG job Taylor_20261123_100916: REPORT_rev4 tam 17.673, skeptic r4 REFUTED (qua cao: tai tro XDCB+BDS 100% von chu) — CHO Mike ap LEDGER_PROPOSAL_DBC.json (REFUTED_OPEN rev3) / user quyet
- [2026-11-23T10:19:20Z] [HHS rebuild v3 23/11] XONG job Taylor_20261123_100926: REPORT_rev6 tâm 13.969, skeptic r4 CONFIRMED — CHỜ Mike áp LEDGER_PROPOSAL_HHS (FIXED_UNVERIFIED bước 1) + dd_ledger_append_confirmed.py
- [2026-11-23T10:23:49Z] [VCP DD vòng3 23/11] XONG job Taylor_20261123_100924: REPORT_rev4 tâm 29.686 sau CK, skeptic r4 INCONCLUSIVE (hết vòng) — CHỜ Mike áp LEDGER_PROPOSAL_VCP.json (rev3 REFUTED_OPEN)
