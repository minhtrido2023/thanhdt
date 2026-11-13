# Luồng C2 — vá 3 việc arch-reviewer cho cache LAG điều chỉnh đang LIVE (13/11/2026, job `Taylor_20261113_021438`)

User PHÊ CHUẨN trạng thái live của `97b2a7197` (13/11 09:1x ICT, qua Mike). Code nằm trên nhánh **`feat/lag-cache-c2-20261113`**
(repo ngoài, worktree `/home/trido/thanhdt/wt-lagc2-1113`, commit **`b1b91a5e6`** trên `main` `e614a10c6`). **CHƯA merge** — chờ arch-reviewer.
Diff: `lagged_cache_adjusted.py` +36/−2, `lagged_cache_adjusted_selfcheck.py` +58/−3, `refresh_lagged_caches.py` +19/−3 (`git diff --numstat main HEAD`).

## 1. Validate độ phủ Price / Volume_3M_P50 (fail-closed)
- `coverage_problems()` gọi trong `validate()`: 60 phiên T2–T6 gần nhất, **bỏ mã mang sang** (cơ sở cũ, không có Price — đã biết, có log).
  NaN trung bình cửa sổ > **2%** hoặc một phiên > **5%**, hoặc thiếu cột ⇒ problems ⇒ không ghi pkl, exit 1 (đường notify `[FAIL]` cuối chain như hiện nay).
- Ngưỡng đặt theo số đo trên `data/lagged_pos_ov.pkl` thật (max 2026-11-11):
  | | Price NaN | Volume_3M_P50 NaN |
  |---|---|---|
  | 60 phiên gần nhất, loại mã mang sang | 0 | 0 |
  | 60 phiên gần nhất, GỒM mã mang sang | 0,147% (max phiên 0,49%) | 0 |
  | max theo phiên 2025–2026 (loại mang sang) | 0,00% | 0,40% |
  | max theo phiên 2020+ / cửa sổ 60 phiên 2020+ | 1,49% / 1,16% | 1,88% / 1,66% |
  **Đính chính brief:** "0 dòng Price NULL từ 2025" chưa đúng — có **1.917** dòng Price NaN từ 2025 (0,36% của 535.150), và **toàn bộ**
  NaN trong 60 phiên gần nhất là của mã mang sang (TLD 37, SSC 19, VTH 17, PMT 1). Loại mã mang sang ⇒ 0.
- Cache thật qua cổng mới: `coverage_problems(ov, carried)` = `[]`.
- `lag_adv_basis.adv_px` không đổi: vẫn COALESCE về giá điều chỉnh cho mã mang sang (đúng như trước) — nay không thể xảy ra lặng lẽ cho mã thường.

## 2. Runbook rollback
- `kb/ops_runbook.md` § "Rollback LAG cache điều chỉnh" (lệnh đầy đủ) + `kb/projects/lag-cache-adjusted-20261110.md` §7 (tóm tắt).
- md5 kiểm lại 13/11: `earnings_px.pkl.pre_adj` = `af4b8c1b72f4b133248516eff8b459b0`, `lagged_pos_ov.pkl.pre_adj` = `afb2484e5fb702cd4335949d1a69db1b` — khớp brief; max 2026-11-09, không cột Price.
- `git revert 97b2a7197` thử trên nhánh tạm từ main: sạch (rc=0, không xung đột; nhánh tạm đã xoá). Không có commit nào sau `97b2a7197` trên main chạm 11 file đó.
- Code cũ là đường append (in `+N rows -> ... new max`), xác nhận bằng `git show 97b2a7197^:WorkingClaude/refresh_lagged_caches.py`. **Runbook CHƯA được chạy thử đầu-cuối** (sẽ ghi đè pkl live).
- **Không thêm knob env append-mode**: phải giữ song song code append cũ trong refresh ⇒ không tối thiểu; revert 1 commit đủ.

## 3. Sửa ghi chép
- `kb/cron_registry.md:89`: "ĐỀ XUẤT, CHƯA merge/cài" → ĐANG CHẠY từ 15:30 10/11, user phê chuẩn 13/11, trỏ runbook. (Bước đúng là [2] trong `papertrade_daily.sh:43`, không phải [0].)
- Doc dự án: banner dòng 3 → PHÊ CHUẨN 13/11; dòng "CHƯA apply" gạch; §4.3 thêm đính chính blast radius; §6.3 chú thích; §7 viết lại.
- **Quy nguyên theo mã** (`attrib_4.py` → `attrib_4.csv`; csv ctrl/adjv2 lấy ở worktree research `wt-mike-lagadj-1110`, vì bản trong research/ chính bị thiếu dù có trong MD5SUMS):
  - 7/11 (BSP, PMP, TMG, DMN, LAW, NBC, TPC) ∈ `lag_liq_excluded` của `golive_v23_status.json` signal 11-12 — **đo, đúng**.
  - HTT Q2 (entry 07-24) 6,11→4,62 rời · PHP Q3 (entry 11-05) 5,29→4,10 rời · KLB Q2 (entry 07-30) 4,37→5,40 vào, và KLB bị `lag_forensic_excluded` · PHR Q3 (entry 11-09) −0,32→5,06 vào (cơ sở cũ dính cú rơi giả GDKHQ 09-11).
  - Cửa sổ entry đang mở (signal 11-12: entry ≥ 11-07): trong 4 mã chỉ còn PHR. Entry của PHP (11-05) và PHR (11-09) đều trước lần apply đầu (15:30 10/11).
  - **0 lệnh** cho HTT/PHP/KLB/PHR trong `orders[]` của mọi plan SpaceX/ZaloPay/main ngày 05–13/11; PHP chỉ có ở `window_passed` SKIP (ZaloPay 11-11, 11-12).

## 4. (không chặn) nguyên tử + dọn tmp
- `.prev` qua `LCA.copy_atomic`; CSV bước [4] qua `_save_csv_atomic` (mkstemp + os.replace; giữ nhánh PermissionError → `.new.csv`).
- Dọn `*.tmp` mồ côi khi ĐÃ giữ flock, chỉ tmp có tiền tố 6 file của chính script.
- Lưu ý: tmp bằng mkstemp ⇒ CSV mới có quyền 0600 (pkl đã 0600 từ trước); mọi consumer cùng user `trido`.

## Đã chạy (log trong thư mục này)
- `$DNA_PYEXE lagged_cache_adjusted_selfcheck.py`: **80/80 PASS** dưới `env -u TZ` (`sc_noTZ.log`), `TZ=Pacific/Kiritimati` (`sc_kiri.log`), `TZ=America/Los_Angeles` (`sc_la.log`). Trước đây 65 (+15 kiểm mới: 9 unit độ phủ, 3 tích hợp nullprice, .prev kill, CSV kill, dọn tmp).
- `--mutate`: **39/39 bị bắt** (`mutate.log`; +9 mutation độ phủ, +4 refresh). 5'31".
- `lag_adv_basis_selfcheck.py`: 13/13 PASS (không đổi).
- `attrib_4.py` (quy nguyên).

## Rủi ro / ghi chú
- Đĩa `/` còn ~4,5G (99%) — một lần thử tạo worktree repo mike làm đầy đĩa (`No space left`), đã gỡ ngay. Docs vì vậy sửa thẳng trên checkout mike (master), không qua worktree.
- Ngưỡng 2%/5% chưa qua dữ liệu "sự cố thật" (chưa từng xảy ra) — đặt ~10× trên mức live, trên max 2020+.
