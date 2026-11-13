# Luồng B3 — dòng "so với gửi tiết kiệm" vào template báo cáo · 2026-11-13
Nhánh `feat/savings-row-b3-20261113` (từ `feat/savings-row-20261112` @418667a32), worktree `wt-savings-row-20261112`. KHÔNG merge, không gửi báo cáo thật, không đụng cron/sổ giao hàng thật (mtime `state/report_delivery.json` không đổi).

## 1. Template = `bin/period_table_32.py::render` (cả weekly/monthly qua `report_v2` đều gọi nó)
- CLI phát khối `savings` ⇒ thêm 2 cột `Gửi tiết kiệm (tham chiếu)` + `Chênh so tiết kiệm` (tên chứa "tiết kiệm" / "chênh" = quy ước cổng), số lấy NGUYÊN từ `nav_period_returns.py` (không tự trừ).
- Dưới bảng: nhãn 1 đã duyệt NGUYÊN VĂN + `anchor_warning` của CLI (nếu có) + cảnh báo "Kết quả trong quá khứ…" NGUYÊN VĂN. Câu cũ "chưa tính thuế" của footnote CLI KHÔNG hiện trong bảng (selfcheck khẳng định).
- CLI không phát savings ⇒ bảng như cũ (selfcheck). Dòng "Phần bot quản lý" (ZaloPay, nội bộ) hiện "—" ở 2 cột mới.
- Kiểm tra lại khẳng định thuế trong nhãn: phí + thuế bán 0,1% là tiền thật trừ trong số dư broker; NAV = số dư thật (`daily_nav_snapshot`) ⇒ TWR đã sau phí và thuế bán. Cổ tức: `dividend_adjusted_return.py` TẦNG 4 — DNSE ghi GỘP ở khoản phải thu, trừ 5% khi chi trả thật. ⚠️ Hệ quả: câu "đã trừ … 5% cổ tức" chỉ đúng tuyệt đối khi `cashDividendReceiving = 0`. Đo 2026-11-06 SpaceX = **0** (và 11-12 = 0) ⇒ nhãn đúng cho báo cáo 06/11. Khi có khoản phải thu chưa chi, NAV cao hơn thực đúng 5% phần đó (số nhỏ, nhưng nhãn sẽ hơi quá). Chưa có cổng cơ học cho điều kiện này — đề xuất: thêm 1 dòng chú thích có điều kiện hoặc cổng đọc `cashDividendReceiving` (chưa làm, cần duyệt).
- Câu "chứng chỉ tiền gửi chưa xác minh miễn thuế": nhãn đã duyệt không có câu này; nhãn nói rõ hurdle là THƯỢNG CẬN tham chiếu, không bảo đảm. Chưa thêm.

## 2. Cổng (`period_table_32.check_report`)
- Cột GIỐNG tiết kiệm (so sau bỏ dấu: tiet kiem / gui tien / tien gui / lai gui / gui ngan hang / hurdle / saving / deposit) mà không nhận ra theo tên ⇒ **BLOCK** (trước đó bị bỏ qua lặng lẽ, số không được đối chiếu). Selfcheck: 5 tên lạ ("Gửi tiet kiem", "Lãi gửi ngân hàng", "Hurdle (tiền gửi)", "Savings", "Lãi tiền gửi 12T") đều BLOCK.
- Bảng có cột tiết kiệm mà thiếu nhãn/cảnh báo NGUYÊN VĂN ⇒ BLOCK (kể cả sửa 1 chữ "miễn"→"chịu").
- `period_table_32_selfcheck`: **85 assertion PASS** (trước 68) dưới `env -u TZ`, `Pacific/Kiritimati`, `Asia/Ho_Chi_Minh`. Lõi cũng PASS cả 3 TZ: savings_hurdle 61, nav_period_benchmark 69, report_delivery_gate 7/7 + 5/5.

## 3. report_delivery_gate end-to-end trên báo cáo tuần THẬT 02→06/11 (SpaceX)
Script `e2e_gate.py` (tái lập): lấy `reports/SpaceX_weekly_report_2026-11-02_to_2026-11-06.md` thật, thay bảng "Hiệu suất lũy kế" bằng đầu ra `render()` của nhánh (có cột tiết kiệm — xem `e2e/…md`), kèm thư mục `v2/` thật, chạy `deliver()` với sổ tạm, notify/email giả. Kết quả log `e2e/gate_run.log` (python3 hệ thống vì artifact-lint cần pymupdf, wc_venv không có):
- return-gate §21 **PASS** (7 vị thế khớp sổ broker) · period-return **PASS** (−3,94% vs −3,944%) · benchmark-table **PASS** (wtd/mtd/inception khớp CLI, kể cả cột tiết kiệm) · livermore-block OK · artifact-lint **PASS** · nav-flow **PASS** · deliver rc=0 "COMPLETE" (notify/email là stub — KHÔNG phải gửi thật).
Số trong bảng: Từ khi bắt đầu −3,94% vs tiết kiệm +2,45% ⇒ **−6,39pp**; tuần/MTD −0,26% vs +0,14% ⇒ −0,41pp.
Giới hạn: PDF/email HTML trong `v2/` là bản CŨ (chưa re-render có cột mới) — artifact-lint chạy trên PDF cũ; cần build lại v2 từ nhánh khi duyệt.

## 4. Symlink `mike → /home/trido/thanhdt/WorkingClaude/mike`
Là file đã track trong git (từ backup 09-29), nên worktree nào cũng có: lệnh trong docstring `python3 mike/bin/X_selfcheck.py` chạy từ gốc worktree đi qua symlink và **test master**. Đã `git rm` symlink trên nhánh B3 + thêm vào `period_table_32_selfcheck` 3 assertion bắt buộc `pt/npr/rdg` nạp từ chính cây chứa selfcheck. Còn lại (không sửa, nêu rõ): `report_delivery_gate` CỐ Ý chạy CLI/return-gate của cây canonical (`ROOT`), nên gate chạy từ worktree mà không patch `ROOT` sẽ đối chiếu với CLI master (chưa có khối savings ⇒ BLOCK "thiếu khối savings"). e2e patch `rdg.ROOT = cây branch` — khi merge thì canonical = branch nên hết lệch. 22 worktree khác vẫn mang symlink này.

## report_v2_selfcheck
**CHƯA KẾT LUẬN**: chạy lại 2 TZ (env -u TZ, Pacific/Kiritimati) mỗi lần quá 280s timeout, log chỉ có 2 dòng cảnh báo; không ra PASS/FAIL (giống B). Sổ giao hàng thật mtime không đổi (07:32). Cần chạy không giới hạn thời gian ngoài dispatch.
