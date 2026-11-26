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

- [2026-11-25T08:13:28Z] [dd-MBB KTPL 25/11] XONG job Taylor_20261125_080251: 7c1fad8a2 (wt-dd-mbb-agm-20261125) — k=9,03% ⇒ rev6 18.595 (−11,7%) vùng 13.151–24.140 TRONG, E17 18.731 — CHỜ Mike ghi sổ+merge; NQ gốc chưa đọc (MB 403)
- [2026-11-25T08:28:03Z] ĐANG DỞ: job Taylor_20261125_082754 MBB rev6' (quỹ khác-sử dụng, E17 đối xứng k, CAR) wt-dd-mbb-agm-20261125 | NEXT: đọc skeptic/r2.json
- [2026-11-25T08:34:30Z] [dd-MBB rev6' 25/11] XONG job Taylor_20261125_082754: 8881d7289 (wt-dd-mbb-agm-20261125) tâm 17.925 (k 11,59% gồm quỹ khác), E17 18.059 — CHỜ Mike ghi sổ+merge; CAR 30/09 gốc còn mở
- [2026-11-25T10:43:16Z] ĐANG DỞ: job Taylor_20261125_104308 dcf-vn-behavioral (plan + pilot tâm hành vi) | NEXT: kiểm kê dữ liệu, đọc REPORT 20261125c
- [2026-11-25T10:55:06Z] [dcf-vn-behavioral 25/11] XONG job Taylor_20261125_104308: 7294cf0d1 nhánh session/Taylor_20261125_104308 (wt-dcf-behav-20261125) — pilot YẾU, tâm hành vi không hơn giá hôm nay về mức; đề xuất bốn ô nội tại × hi52 — CHỜ Mike quant-skeptic 1 vòng + user duyệt G1 hẹp/dừng
- [2026-11-25T11:50:51Z] [dcf-behav 25/11] XONG job Taylor_20261125_114526: 83d5f99c3 (wt-dcf-behav-20261125) PLAN/PRELOCK sửa theo skeptic + paper_cell_monthly — CHỜ Mike skeptic vòng 2 + duyệt entry registry/cron; blocker: lv_ENS2 cần panel dựng lại hằng tháng; user quyết G1 (dự kiến NO-GO 1)
- [2026-11-25T11:57:36Z] ĐANG DỞ: job Taylor_20261125_115701 lv_ENS2 incremental (wt-dcf-lvens2-inc-20261125) | NEXT: đo b_panel.py
- [2026-11-25T12:33:54Z] [lvens2-inc 25/11] XONG job Taylor_20261125_115701: 6eb45da21 (wt-dcf-lvens2-inc-20261125) — v31 khớp vp2 Δ=0, PIT lệch do N_next/route look-ahead của V3.1 — CHỜ Mike/user: mc strict vs step (skeptic), chỗ đặt snapshot VND, duyệt cron
- [2026-11-25T16:04:27Z] ĐANG DỞ: job Taylor_20261125_160331 lvens2 pit2 (skeptic REFUTED fixes 1-6), worktree wt-dcf-lvens2-pit2-20261126 dir dcf_lvens2_pit2_20261126 | NEXT: đọc lvens2_incremental.py, data_registry CA/oshares
- [2026-11-25T17:17:56Z] [lvens2-pit2 26/11] XONG job Taylor_20261125_160331: 58e35d1dd (wt-dcf-lvens2-pit2-20261126) stepcar+e_guard, selfcheck PASS 3TZ — CHỜ Mike quant-skeptic vòng 2 + merge; blocker cron B1 CA_MD5 hardcode
- [2026-11-25T18:12:08Z] [lvens2-pit2 B1 26/11] XONG job Taylor_20261125_173540: script_md5 3f5041d6 (wt-dcf-lvens2-pit2-20261126) — CHỜ Mike quant-skeptic vòng 2 (B2) + B3 VND + merge/cron sau user duyệt
- [2026-11-26T04:04:11Z] [lvens2-pit2 v3 26/11] XONG job Taylor_20261126_021759: 7649df7c4 (wt-dcf-lvens2-pit2-20261126) — CHỜ Mike quant-skeptic vòng 3 + user duyệt merge/cron; mở: B3 VND dừng 11-23, cảnh báo wrapper
