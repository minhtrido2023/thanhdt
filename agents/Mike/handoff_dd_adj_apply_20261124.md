# BÀN GIAO — áp dụng 4 việc đã duyệt (24/11/2026 19:10 ICT, từ topic 1574737600021930055)

User DUYỆT cả 4 việc ("Duyệt 4 việc đề nghị", 19:10). KHÔNG email, KHÔNG đặt lệnh. Đợt 2/3 recheck vẫn KHÔNG chạy. Topic cũ 1574737600021930055 DỪNG.

## Đã xong (đừng làm lại)
- Taylor dựng tâm điều chỉnh 8 mã, verify artifact (adj.json schema PREREG_adj_v2 mục 7, run1=run2): nhánh `session/adj-g1` (FPT 55.668, TCH 15.152, VGS 25.148), `session/adj-g2` (DRI 15.164, SIP 57.261, HHS 11.593 display-only), `session/adj-g3` (NNC 58.914, DGC 41.132); worktree wt-adj-g1/g2/g3 trong /home/trido/thanhdt/WorkingClaude/; g1-g3 đều sinh từ `session/adjpilot` (PREREG v2). Đường dẫn: agents/Taylor/research/dd_adjcenter_20261124/<MÃ>/{ADJ_CENTER.md,adj.json}.
- Cổng Bậc 1 E17: nhánh `session/1574737600021930055` (worktree wt-1574737600021930055), commit d48271fcc, arch-review NEEDS_CHANGES đã sửa hết, selfcheck 144/144 (env -u TZ + America/New_York), mutant 79/79, sổ lỗi 0. Diff: agents/Mike/watch_gate_E17.diff.
- Skill V9/E17: ~/.claude/skills/due-diligence/SKILL.md.proposed (diff agents/Mike/skill_dd_E17.diff), CHƯA áp.

## 4 việc làm (theo thứ tự)
1. **Áp skill**: `cp SKILL.md SKILL.md.bak_20261124_e17` rồi `mv SKILL.md.proposed SKILL.md` (kiểm diff còn đúng V9 trước khi mv). Cập nhật memory `feedback-dd-inconclusive-must-still-forecast.md` (+ dòng MEMORY.md nếu cần): tâm điều chỉnh E17/V9 đã LIVE trong skill.
2. **Phương án ngưỡng = A** (user duyệt): merge `session/1574737600021930055` vào master (dd_price_zone_watch.py, 2 selfcheck). Chạy lại selfcheck sau merge dưới `env -u TZ` + TZ=America/New_York (watch với `--mutants`), `dd_price_zones_selfcheck.py` lỗi 0.
3. **r 13,5% / chặn RONIC = tham số luật, KHÔNG vào Σ** (user duyệt): ghi vào skill V9 hoặc kb/projects (1 dòng nguồn `decided_by: user`, 24/11 19:10) — kiểm V9 `.proposed` đã nêu chưa, chưa thì thêm trước khi áp (đưa lại diff nhỏ nếu sửa nội dung).
4. **Merge nhánh adj + ghi sổ `center_adj`**: merge `session/adj-g1`, `adj-g2`, `adj-g3` (đã gồm adjpilot) vào master. Ghi sổ `kb/dd_price_zones.json` 7 mã (FPT, TCH, VGS, DRI, SIP, NNC, DGC; **HHS KHÔNG ghi sổ** — display-only theo dải CK, user chốt). Mỗi mã = rev mới (supersedes rev hiện tại, correction_reason "thêm tâm kỳ vọng điều chỉnh E17", giữ nguyên các trường cũ + skeptic_final cũ) với `center_adj`, `center_adj_low/high` (= range_low/high của adj.json), `center_adj_basis` (đường dẫn TƯƠNG ĐỐI từ mike root tới adj.json), `center_adj_md5` (md5 file đó). ⚠️ **Vướng schema cần xử lý**: validator `_center_adj_errs` (bin/dd_price_zones_selfcheck.py) đang đòi adj.json `rev` == entry `rev`; nhưng rev mới = rev cũ+1 nên LỆCH. Khuyến nghị: với entry có `supersedes` thì so adj.json `rev` với rev của entry được supersede (ticker@dd_date#N), và adj.json `dd_date` với dd_date entry — sửa validator + thêm test + mutant, selfcheck 2 TZ, và arch-review 1 vòng nhỏ (opus/medium, đã chạm cổng) trước khi merge. Dùng đúng tool ghi sổ hiện có nếu có (xem skill mục Sổ mức giá, `bin/dd_ledger_append_*.py`); không có thì ghi tay + selfcheck 0 lỗi. Sau ghi sổ: chạy `bin/dd_price_zone_watch.py` (chỉ in, KHÔNG đặt lệnh) và báo bảng Bậc 1/Bậc 2 của 7 mã (DGC/DRI/SIP kỳ vọng lên Bậc 1 nếu vượt đủ cổng khác: cờ DD, thoát ≤3 phiên, giá < đáy hiệu dụng).
Lưu ý SIP: tâm adj CAO hơn base ⇒ cổng A KHÔNG nới đáy (đúng thiết kế). Luật 4 KHÔNG đổi.

## Quy tắc
Chạm sổ + cổng ⇒ arch-review 1 vòng trước merge phần validator; mọi thay đổi chạy trong worktree riêng, commit đường dẫn của mình. Báo bảng kết quả vào topic MỚI; HỎI user chỉ khi gặp quyết định thật. `bin/remember.sh Mike`.
