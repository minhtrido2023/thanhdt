# DD việc tồn — HHS A/B + PAT nhãn thuê đất (25/11/2026, job Taylor_20261125_080257)
Nhánh `session/Taylor_20261125_080257`, worktree `wt-dd-hhs-pat-fu-20261125` (gốc ff4e5c744). KHÔNG ghi sổ master / merge / email / wire.

## (1) HHS — `HHS/REPORT_HHS_AB.md` (md5 8196fa4a…)
| | Tâm base CK0 | vs 10.805 | center_adj E17 (CK+20) | vs 10.805 |
|---|---|---|---|---|
| **A** biên s_obs 52,05% | 13.969 (12.422–15.564) | +29,3% | 11.593 (11.593–13.969) | +7,3% |
| **B1** TB 14 CĐT 37,7% | 12.357 (10.940–13.839) | +14,4% | 10.303 (10.303–12.357) | −4,6% |
| **B2** TCH 29,9% | 11.774 (10.390–13.240) | +9,0% | 9.837 (9.837–11.774) | −9,0% |
- Số đọc từ lưới khoá w3 `adj_run1.txt` (md5 82f1f004…), không tính lại. Peer GPM đo lại BQ 25/11 khớp 37,7 / 37,9 / 29,9 (IQR 30,3–47,2%).
- **Khuyến nghị A + ghi rev9** (base 13.969, adj 11.593): luật DD hiện hành (user 08/11 10:50) cấm ép biên về TB ngành ở pha dự báo khi moat NONE — B chỉ là độ nhạy; 52% đo trên chính NC-II (2 nguồn kế toán 52,2/51,9); 10.805 đang mang CK 26,63% nằm ngoài dải 0…+20% user chốt. Forensic EXCLUDE ⇒ A/B không đổi hành động.
- Proposal: A = `dd_recheck_20261125w3/HHS/LEDGER_PROPOSAL_HHS.json` + `adj.json`; B1 = `HHS/LEDGER_PROPOSAL_HHS_B.json` + `HHS/adj_B.json`.

## (2) PAT — `PAT/ERRATA_thue_dat.md`
- Tâm 55.527 / adj 57.872 GIỮ: base đã giả định gia hạn (assumptions_rev6.md:12), nhánh −28,7% là hạng mục C ngoài Σ.
- Chữ CHƯA nhất quán: sổ rev4/rev5 `verdict_label` + `notes`, SUMMARY/ADJ_CENTER w4 vẫn gọi là "rủi ro xuống lớn nhất". Đề xuất 5 diff; áp bằng rev6 chỉ-đổi-chữ `PAT/LEDGER_PROPOSAL_PAT_rev6_text.json` (không sửa tại chỗ — md5 khoá).

## Selfcheck sổ tạm (`selfcheck/run_selfcheck.sh`, `run_summary.txt`)
Kịch bản A và B (master 175 + HHS rev9 + PAT rev6 + HHS center_adj rev10 = 178 entry): lỗi 0 × 3 TZ (UTC / ICT / New York) mỗi kịch bản.
