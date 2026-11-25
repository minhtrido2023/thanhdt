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

- [2026-11-25T00:41:01Z] [dcf-vn-redesign V3 25/11] XONG job Taylor_20261125_001435: nhánh session/Taylor_20261124_170355 commit 152e83c11 (wt-dcf-v3-20261125) — CHỜ Mike quant-skeptic V3 + user quyết (E/P hay mô hình cho cổng mềm; chọn ENS2 vs ENS1w)
- [2026-11-25T01:10:24Z] ĐANG DỞ: job Taylor_20261125_011012 dcf-earnings-forecast (phase1 kiểm kê+PRELOCK) | NEXT: worktree wt-dcf-earnfc-20261125d
- [2026-11-25T01:21:33Z] [dcf-earnings-forecast 25/11] XONG job Taylor_20261125_011012: nhánh session/Taylor_20261125_011012 cec37fa11 (wt-dcf-earnfc-20261125d) — D0imp tệ hơn naive, gap≈sai số earnings của D0, C2 không vượt E/P — CHỜ Mike quant-skeptic + chạy lại C sau V3.1
- [2026-11-25T01:30:05Z] [dcf-vn-redesign V3.1 25/11] XONG job Taylor_20261125_011009: commit 1a279d12f nhánh session/Taylor_20261124_170355 (wt-dcf-v3-20261125) — CHỜ Mike merge; luật §5 mong manh ENS2 vs ENS1 (KD 90/120 đổi chọn); nên GDKHQ đối chiếu mã vắng BQ còn mở
- [2026-11-25T01:47:52Z] ĐANG DỞ: job Taylor_20261125_014736 J3 earnings+chu kỳ (wt-dcf-earnfc-20261125d) | NEXT: vá J2 → PRELOCK addendum → chu kỳ
- [2026-11-25T02:01:39Z] [dcf-earnfc J3 25/11] XONG job Taylor_20261125_014736: nhánh session/Taylor_20261125_011012 1d74c6474 (wt-dcf-earnfc-20261125d) — B'/C' NO-GO, A' thiên lệch D0 đổi dấu theo pha; ứng viên PREREG 'neo theo độ chu kỳ' — CHỜ Mike quant-skeptic 1 vòng + user
- [2026-11-25T02:16:37Z] ĐANG DỞ: job Taylor_20261125_021625 J4 chu kỳ hướng C (wt-dcf-earnfc-20261125d, dir dcf_earnings_forecast_20261125e) | NEXT: đọc J3 → vá mc ảo → PRELOCK_J4 commit → chạy
- [2026-11-25T02:27:33Z] [dcf-earnfc J4 25/11] XONG job Taylor_20261125_021625: 8e467efab (wt-dcf-earnfc-20261125d, dir …20261125e) — NO-GO; M4 capex +0,0019 IC36 vs P1 3/4 năm (tiêu chí dừng không kích hoạt kỹ thuật, độ lớn ~0); panel V3.2 vá mc — CHỜ Mike skeptic + quyết A→B
- [2026-11-25T02:36:21Z] [dcf-earnfc J3.1 25/11] XONG job Taylor_20261125_022916: c82a9971b (wt-dcf-earnfc-20261125d, dir …20261125f) — REPORT kết luận cuối J1→J4; KL6 rút PREREG; C trên V3.2 không đổi kết luận — CHỜ Mike skeptic J3.1/J4 + ghi KB, rồi hướng B
- [2026-11-25T03:25:34Z] ĐANG DỞ: job Taylor_20261125_032443 dd-recheck w3 job A DDV→HPG→SAS (wt-dd-recheck-w3a-20261125) | NEXT: đọc mẫu FPT + SKILL V9
- [2026-11-25T03:25:35Z] ĐANG DỞ: job Taylor_20261125_032448 DD w3 job C (VLB→DCM→PAT→HHS) worktree /home/trido/thanhdt/WorkingClaude/wt-dd-w3c-20261125 | NEXT: đọc skill + mẫu FPT/HHS
- [2026-11-25T03:25:49Z] ĐANG DỞ: job Taylor_20261125_032446 dd-recheck w3 B (NT2→PVT→SZL), wt-dd-recheck-w3b-20261125 | NEXT: NT2 bước 0
- [2026-11-25T03:32:06Z] ĐANG DỞ: job Taylor_20261125_032448 DD w3 C — VLB XONG 4717a53cf; NEXT DCM→PAT→HHS (wt-dd-w3c-20261125)
- [2026-11-25T03:34:42Z] ĐANG DỞ: job Taylor_20261125_032443 w3 job A — DDV XONG d441f3d20 (wt-dd-recheck-w3a-20261125) | NEXT: HPG rồi SAS
- [2026-11-25T03:36:25Z] ĐANG DỞ: job Taylor_20261125_032446 w3 B — NT2 XONG f810b55c0 | NEXT: PVT bước 0 (wt-dd-recheck-w3b-20261125)
- [2026-11-25T03:36:38Z] ĐANG DỞ: job Taylor_20261125_032448 DD w3 C — VLB, DCM XONG; NEXT PAT→HHS (wt-dd-w3c-20261125)
- [2026-11-25T03:38:50Z] ĐANG DỞ: job Taylor_20261125_032448 DD w3 C — VLB/DCM MECH, PAT DỪNG Bước0 (D4); NEXT HHS (wt-dd-w3c-20261125)
- [2026-11-25T05:31:08Z] ĐANG DỞ: job Taylor_20261125_053002 (resume 032443) w3 A — DDV d441f3d20, HPG 858fb490c XONG | NEXT: SAS (wt-dd-recheck-w3a-20261125)
- [2026-11-25T05:32:58Z] ĐANG DỞ: job Taylor_20261125_053004 (resume 032446) w3 B — NT2 f810b55c0, PVT 851182687 XONG | NEXT: SZL (REFUTED_OPEN ⇒ E17 từ hạng mục skeptic cũ), wt-dd-recheck-w3b-20261125
- [2026-11-25T05:33:12Z] [dd-recheck w3 A 25/11] XONG job Taylor_20261125_053002 (wt-dd-recheck-w3a-20261125): DDV d441f3d20, HPG 858fb490c MECH+adj; SAS c4d23c4cc DỪNG Bước0 D4 −13,4% — CHỜ Mike ghi sổ/merge + user chọn SAS rev3 (a)/(b)
- [2026-11-25T05:38:24Z] [dd-recheck w3 C 25/11] XONG cả 4 mã (VLB/DCM MECH, PAT dừng B0, HHS dd4e59363 REFUTED_OPEN adj 11.593) — CHỜ Mike merge + user quyết HHS: center_adj 11.593 vs 13.969; biên 52% vs 3c
- [2026-11-25T05:42:32Z] [dd-recheck w3 B 25/11] XONG job Taylor_20261125_053004: NT2 f810b55c0 / PVT 851182687 / SZL 8bc49a2af (wt-dd-recheck-w3b-20261125) — CHỜ Mike ghi sổ (proposal trước, rồi center_adj) + merge sau user duyệt
- [2026-11-25T06:37:04Z] ĐANG DỞ: job Taylor_20261125_063648 DD w4 SAS rev mới (D4 đầy đủ), worktree wt-dd-w4-sas-20261125 | NEXT: đọc w3 SAS SUMMARY + mẫu FPT
- [2026-11-25T06:37:34Z] ĐANG DỞ: job Taylor_20261125_063651 DD w4 PAT rev6 (wt-dd-w4-pat-20261125) | NEXT: đọc w3 SUMMARY + skill + mẫu
- [2026-11-25T06:49:49Z] [dd-w4 PAT 25/11] XONG job Taylor_20261125_063651: a82bf4871 (wt-dd-w4-pat-20261125) — rev4 55.527 sau CK REFUTED_OPEN, E17 57.872 — CHỜ Mike ghi sổ+merge; mở: HĐ thuê đất 2034 (−28,7%), legal pháp nhân Đ.235
- [2026-11-25T06:57:44Z] [dd-recheck w4 SAS 25/11] XONG job Taylor_20261125_063648: d0fc3aea2 (wt-dd-w4-sas-20261125) rev3 27.477 (−13,2%, TRÊN), E17 26.803 — CHỜ Mike ghi sổ + merge sau user duyệt
- [2026-11-25T08:03:04Z] ĐANG DỞ: job Taylor_20261125_080254 DD PVP Aframax#3 ĐHĐCĐ 23/10 (wt-dd-pvp-afx-20261125) | NEXT: đọc pvp-dd-20261029.md + tìm văn kiện
- [2026-11-25T08:03:37Z] ĐANG DỞ: job Taylor_20261125_080251 MBB NQ ĐHĐCĐ 2026 (KTPL), wt-dd-mbb-agm-20261125 | NEXT: tải NQ/BB gốc
- [2026-11-25T08:04:49Z] ĐANG DỞ: job Taylor_20261125_080257 HHS A/B + PAT nhãn thuê đất (wt-dd-hhs-pat-fu-20261125) | NEXT: đọc HHS ref-range + rev9 w3, PAT rev4
