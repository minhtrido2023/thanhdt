# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.

## AMH (Adaptive Market Hypothesis) — TRỌN VẸN 7 HƯỚNG, XONG 2026-09-10
File tổng: `kb/projects/amh-adaptivity-review-20260910.md` (mục 10 = INPUT DÙNG THẲNG cho review VPI/BAL 09-16).
Kết quả: 4 job Taylor + 2 verdict quant-skeptic. **KHÔNG WIRE GÌ.**
- Job A (BAL edge-gate, Taylor_20260910_131906): **NO-GO**. Cổng đối xứng BẤT KHẢ về CẤU TRÚC (BAL chỉ-BULL,
  im 6/13 năm, gate mù 3/6 cụm + xếp hạng NGƯỢC ở phần còn lại). Backtest 8 leg: MaxDD bit-identical,
  PLACEBO THẮNG (+0,40 vs +0,30), LOO 1/4, không dose-response. Leg g0 bác tiền đề: tắt BAL khi FLIPPED
  mất −2,97pp. ⇒ **SỬA G1: BAL ĐÃ CÓ vòng phản hồi theo TRẠNG THÁI, không thiếu.**
- Job B (change-point + fitness matrix): change-point NO-GO. Momentum chết ở MỌI ô sau 2020 (IS 8/8 dương
  → OOS 8/8 ≈0, LOO không cứu) ⇒ không cứu BAL bằng cổng regime/breadth.
- Job C (market-efficiency gauge): CHU KỲ không phải cấu trúc, quant-skeptic CONFIRMED medium.
- Đề xuất t_eff (sửa edge_health_monitor.py): **REFUTED high** — công thức AR(1) áp lên chuỗi MA(2);
  dưới Newey-West |t| mom_200 ~2,5. KHÔNG SỬA. Bài học: recompute ĐÚNG SỐ ≠ phương pháp đúng.
- Mike tự làm xong: #7 fix path (30878a9b), #5 biodiversity gate vào skill quant-research (5432519b),
  #6 structural-break protocol + kb/structural_break_watch.json (5d9d4686, gộp review quý Bobby 11-26).
- Đính chính đã ghi: fitness_matrix.py cũ có look-ahead 16% số tháng → SUPERSEDED (66e5ec7e), dùng fitness2.py.
- Phụ phẩm: data_registry entry edge_panel.csv (a808687b) + fix ghi ATOMIC edge_panel (492b7637, test 3 đường).

## VIỆC MỞ phát sinh từ AMH — CHỜ USER QUYẾT (scope MỚI, chưa dispatch)
`data/lag_edge_health.csv` khoá stats theo ngày VÀO trong khi return chỉ biết sau 25 phiên.
LIVE KHÔNG ảnh hưởng. BACKTEST thì có: pt_v23_audit_2014.py:770-790 reindex chuỗi entry-keyed
⇒ ngày d đọc giá trị cần dữ liệu d+25 (~5 tuần). Nằm TRONG validate +0,60pp đã công bố của
allocator edge-conditional. Việc đúng = 1 A/B một-leg rebuild exit-keyed. KHÔNG phải lý do đổi gate live.

## Bus question đang mở, CHƯA fix (theo dõi tiếp)
1. `Mafee/nav-price-xcheck-stuck-{SpaceX,ZaloPay}-2026-09-09` — đã có fix (c30e0580); kiểm NAV 09-09 backfill xong chưa.
2. `Mike/bq-cache-manifest-not-updated-by-selfheal-2026-09-09` — self-heal quên rewrite manifest.json. Chưa sửa.
3. `Wags/wags-fix-not-confirmed: coord-2026-09-07` — doc drift cron vn_realestate_monthly_check.sh.
4. `macro-strategist/vn-realestate-monthly-check-2026-09` — chờ user chọn A/B/C.

## R&D đã ĐÓNG HẲN (đừng mở lại nếu không có dữ liệu ngoài mẫu mới)
- CCS/8L accruals (09-06, NO-GO lần 3) · BAL/custom30V 5 vòng (09-09, tất cả NO-GO).
- custom30V: user chốt overweight bank là TÁC DỤNG PHỤ của pool thanh khoản; cắt 16pp bank tốn ~0 CAGR
  nhưng LUÔN trả bằng ADV (−23,8% giữ pool 60 / −70,7% nới pool).

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm → §-mới tiếp theo phải tách sang _ext.md.

- [2026-09-10T14:24:32Z] 2026-09-10 21:23 USER DUYET A/B mot leg exit-keyed. Dispatch Taylor_20260910_142406 (opus/high, timeout 5400). Cau hoi duy nhat: trong +0,60pp da cong bo cua allocator edge-conditional, bao nhieu con song khi mean12 khoa theo ngay RA. Rang buoc: 1 leg duy nhat, khong quet grid, khong sua lag_edge_health.csv (hop dong production), control phai tai lap md5 7d053e6201c9d107685ff4d1dd9d2d2a + self-check 0 VND neu khong thi DUNG. Gate LIVE khong bi anh huong boi loi nay. Buoc ke tiep cua Mike: doc ket qua -> quyet co can dinh chinh cau chu +0,60pp trong data/results_registry.md khong (Mike sua registry, KHONG de Taylor tu sua). Wakeup turn PHAI bat dau bang jobs.sh claim-reply.
- [2026-09-10T14:59:40Z] 2026-09-10 AMH DONG HOAN TOAN. A/B exit-keyed (Taylor_20260910_142406) XONG: loi khoa-entry CO THAT nhung VO HUONG, ~107% phan chenh con song (+0,288 -> +0,309pp), delta +0,021pp nam ~19 lan trong dai nhieu placebo, 15 run 7+/8- p=0,93. LIVE chua bao gio bi anh huong, khong doi gate. PHAT SINH LON HON: cong edge-conditional dang +0,29pp tren pin R3 KHONG phai +0,60pp; +0,60pp KHONG CO RUN NGUON NAO DUOC PIN. MIKE DA TU SUA registry (commit a76b00d7) + amh review muc 12. BAI HOC: Mike chuyen tiep +0,60pp 2 luot ma khong grep nguon - cung lop loi voi recompute dung so hoc cua cong thuc sai. Tong ket AMH: 5 job Taylor + 2 verdict quant-skeptic, KHONG WIRE GI.
