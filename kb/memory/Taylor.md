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
