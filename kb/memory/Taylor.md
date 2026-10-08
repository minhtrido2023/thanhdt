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

- [2026-10-08T04:48:53Z] ĐANG DỞ job Taylor_20261008_042322 adjfactor awaiting r3: sửa 5 mục arch-review (wt-await-1008 @c2854372) | NEXT: selfcheck+mut, review lại 1 lần, merge
- [2026-10-08T05:49:34Z] [adjfactor awaiting 10-08] DUNG sau arch-review vong 2 NEEDS_CHANGES (feat/adjfactor-awaiting-trade-20261008@25cf9a22, wt-await-1008): B1 _state_write msg duong xoa khoa, B2 alert.sh:560 dung -n DRIFTS, B3 test khe 1-2 phien, B4 dry-run lai sau r3. CHO Mike/user cho phep r4 roi merge.
- [2026-10-08T06:30:28Z] ĐANG DỞ job Taylor_20261008_055312 adjfactor awaiting r4: commit 9e4a6bd1 (wt-await-1008), 570/570 x4, mut 64/64 | NEXT: arch-review 1 lần → APPROVED squash merge mike master / NEEDS_CHANGES ghi finding dừng
- [2026-10-08T07:11:40Z] [adjfactor awaiting 10-08] MERGED 18f2317c (r4, APPROVED) — xoá dòng ĐANG DỞ/DUNG cũ của job này; worktree wt-await-1008 có thể dọn.
- [2026-10-08T08:01:00Z] ĐANG DỞ job Taylor_20261008_080048 adjfactor PRICE_FIELD_MISMATCH: bắt đầu | NEXT: đọc detect.py, thiết kế quy tắc bước giá
- [2026-10-08T08:10:29Z] ĐANG DỞ job Taylor_20261008_080048 PFM: worktree agents/Taylor/wt-pfm-1008 nhánh feat/adjfactor-price-field-mismatch-20261008; baseline /tmp/pfm_baseline.txt | NEXT: code detect.py + alert.sh + selfcheck
- [2026-10-08T08:25:52Z] ĐANG DỞ job Taylor_20261008_080048 PFM: commit c864ffda feat/adjfactor-price-field-mismatch-20261008 (wt-pfm-1008), 718/718 x2py | NEXT: đọc /tmp/pfm/mut_py31{0,2}.txt → arch-review 1 lần → merge
- [2026-10-08T09:25:41Z] ĐANG DỞ job Taylor_20261008_080048 PFM attempt2: arch-review r1 NEEDS_CHANGES đã sửa (chưa commit, wt-pfm-1008), sc 745/745 x2py, mut2 đang chạy /tmp/pfm/mut2_*.txt | NEXT: commit r2 → arch-review r2 (lần cuối) → merge/dừng
- [2026-10-08T09:56:10Z] [adjfactor PFM 10-08] DỪNG sau arch-review r2 NEEDS_CHANGES (feat/adjfactor-price-field-mismatch-20261008@4737f414, wt-pfm-1008): 1 lỗi R1 cửa sổ trượt qua cụm ⇒ DRIFT giả. CHỜ user chọn A (vòng 3) / B (ghi giới hạn, merge).
- [2026-10-08T10:00:32Z] ĐANG DỞ job Taylor_20261008_100015 PFM vòng 3 (user chọn A): sửa R1 detect.py:661 + 6 non-blocker (wt-pfm-1008 @4737f414) | NEXT: code→selfcheck→mut→dry-run→arch-review 1 lần
- [2026-10-08T10:24:30Z] ĐANG DỞ job Taylor_20261008_100015 PFM r3: commit 45179c7d (wt-pfm-1008), sc 763/763 x4, dry-run r3==r2, mut3 đang chạy /tmp/pfm/mut3_*.txt | NEXT: arch-review 1 lần → APPROVED merge / NEEDS_CHANGES dừng+finding
- [2026-10-08T10:43:31Z] [adjfactor PFM 10-08] DỪNG sau arch-review r3 NEEDS_CHANGES (45179c7d, wt-pfm-1008): B1 win0 giữa cụm ≥4 phiên ⇒ DRIFT giả (SHC ~10-29). CHỜ user chọn vòng 4 / chấp nhận giới hạn.
