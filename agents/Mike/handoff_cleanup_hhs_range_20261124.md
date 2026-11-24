# BÀN GIAO — topic "Dọn worktree + chốt dải HHS gọn" (24/11/2026 15:4x ICT, từ topic 1574659987832307762)
(Thread mới: 1574705442590818419)

## User chốt 24/11 15:36 ICT
Việc 1: "Duyệt gỡ worktree đã merge và sạch. Dọn dẹp lại không gian làm việc của team luôn."
Việc 2: "Tôi đồng ý chốt dải đề xuất nhưng dải không nên quá dài làm mất giá trị đề xuất."

## Bối cảnh
- Đĩa gốc `/` 100% (233G, ~690MB trống lúc 15:3x ICT) — lỗi ghi `No space left on device` khi tạo worktree. Mỗi worktree ~4GB; ~8 cái hôm nay: wt-Taylor_20261124_031942/034215/034217, wt-radar-norm5-mike-20261124, wt-dd-fwd-20261124, wt-1574627160235319398 (CK v3, đã merge), wt-1574659987832307762 (CK v4/v5, đã merge c69a7935b), wt-mike-1574208662719828062 (2,7G), cùng các wt-* khác ở /home/trido/thanhdt/ và /home/trido/thanhdt/WorkingClaude/.
- CK v5 (Taylor_20261124_073243) xong, skeptic CONFIRMED/medium, merge master c69a7935b. Số: N=12, trung vị −3,24% (LOO −8,1…+1,6%), mốc hiện tại 19,7% (khoảng 15–23%), hull −16,8…+19,7 (36,5pp), q75 37,7% (33,5% PREREG gốc). Báo cáo: agents/Taylor/research/ck_holding_vn_20261124_v5/REPORT_CK_HOLDING_v5.md, SKEPTIC_v5.md.

## VIỆC 1 — gỡ worktree + dọn workspace (user ĐÃ duyệt phạm vi này)
Quy tắc an toàn (bắt buộc, theo thứ tự):
1. Liệt kê MỌI worktree của cả 2 repo: `git -C /home/trido/thanhdt/WorkingClaude/mike worktree list` và repo ngoài (`git -C /home/trido/thanhdt/WorkingClaude worktree list`, `git -C /home/trido/thanhdt worktree list`). Kèm `du -sh`.
2. CHỈ gỡ khi ĐỦ 3 điều kiện: (a) nhánh đã merge vào master/main của repo đó (`git branch --merged`/`merge-base --is-ancestor`); (b) `git status --porcelain` rỗng (không untracked quan trọng, không sửa dở); (c) không có phiên sống dùng nó (không process với cwd trong đó — `lsof +D`/`ls -l /proc/*/cwd`; không job `bin/jobs.sh` running trỏ vào; không ghi file trong 30 phút gần nhất). Gỡ bằng `git worktree remove <path>` (KHÔNG --force), rồi `git branch -d` (không -D) nhánh đã merge, `git worktree prune`.
3. Worktree chưa merge / bẩn / nghi đang dùng ⇒ KHÔNG gỡ; liệt kê trong báo cáo kèm lý do để user quyết.
4. Dọn thêm "không gian làm việc của team" CHỈ các loại rõ ràng an toàn: `/tmp` file của chính mình, `__pycache__`, log dispatch cũ > 30 ngày nếu đã có rotate sẵn — KIỂM tên trước, đo dung lượng trước/sau. CẤM xoá: `data/bq_cache_asof*` (coding_guidelines §8b, không tái tạo được), `data/pinned_ledgers/` (immutable), `secrets/`, `data/results_registry.md`, nested repo `mike/` trong outer, bất cứ thứ gì chưa chắc. Loại còn lại (cache lớn, snapshot cũ, thư mục research nặng) ⇒ ĐỀ XUẤT kèm size, chờ user duyệt.
5. Báo cáo: bảng worktree đã gỡ (path, nhánh, size), còn lại + lý do, dung lượng đĩa trước/sau (`df -h /`), đề xuất dọn thêm. Nếu đĩa vẫn >90% sau khi gỡ, tìm top thư mục nặng (`du -xh --max-depth=2` trong /home/trido/thanhdt) và trình user.
6. Đề xuất cơ chế phòng ngừa (không tự cài cron): vd kiểm dung lượng + nhắc gỡ worktree đã merge sau mỗi merge. Chỉ ĐỀ XUẤT.

## VIỆC 2 — chốt dải tham chiếu HHS gọn
User đồng ý dải đề xuất nhưng muốn GỌN. Đề xuất của Mike (trình user xác nhận ngắn): **dải tham chiếu = 0% … +20%** (2 mốc: base 0% nhãn "đầu lạc quan"; +20% = mốc hiện tại, khoảng đo 15–23%). Bỏ +6%. Stress +33…+38% (phân tán một holding) và đầu âm −17% KHÔNG nằm trong dải, chỉ ghi chú: stress dùng khi HHS có dấu hiệu cấu trúc premium; −17% chỉ khi HHS có cấu trúc R1/R2 (chưa ai kiểm; brief cấm đọc HHS). Nói rõ mỗi mốc là của cái gì (0% ≈ trung tâm −3,2% cộng đầu trên +1,6%; +20% = một holding PAN, ≈1 quan sát độc lập, xu hướng chưa đảo; KHÔNG phải trung tâm dài hạn). Độ tin THẤP (N=12, 1 chế độ, T_eff≈0,4).
Ghi quyết định: `kb/projects/ck-hhs-reference-range-20261124.md` (ngắn: dải, nguồn số, 3 lỗi nhỏ còn lại của v5 A/B/K1, điều kiện kiểm R1/R2 trước khi dùng đầu âm) + 1 dòng ở `kb/current_ops.md`. `decided_by: user` chỉ cho phần "đồng ý chốt dải đề xuất, gọn" (user 24/11 15:36 ICT); việc thu về 0…+20% là Mike đề xuất ⇒ nêu rõ để user chỉnh nếu muốn khác.
KHÔNG: dựng rev8 HHS, ghi dd_price_zones.json, đọc giá HHS/TCH/CRV, email, wire. Việc dựng HHS rev8 chỉ khi user giao riêng.

## Phiên topic mới
Làm Việc 1 + 2 ngay (không cần dispatch Taylor). Báo bảng vào topic này, HỎI user chỉ những gì cần quyết (đề xuất dọn thêm, xác nhận dải 0…+20%). Cập nhật bin/remember.sh Mike. Topic CK v4/v5 (1574659987832307762) DỪNG.
