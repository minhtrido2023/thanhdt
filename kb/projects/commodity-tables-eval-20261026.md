# Đối chiếu `commodity_prices` vs file local — 2026-10-26 (Winston, read-only)
Job Winston_20261026_065210. Không đổi code/cron. Registry: `kb/data_registry/feeds/bq_commodity_prices.md`.

## (i) `data/rubber_weekly.csv` vs rubber TE daily → **KHÔNG thay RSS3; BỔ SUNG được TSR20**
- TE `rubber` (USc/kg, ÷100) **là hạng TSR20**: so cột `tsr20_usdkg` (63 ngày chung) lệch −0,45% TB, độ lệch chuẩn 1,9%, min −6,3% / max +2,2%.
- So với cột `rss3_usdkg` (63 ngày thật chung): csv cao hơn TE **+22,8% TB** (9,3–33,5%) — khác hạng hàng, không phải đơn vị.
- Phần `wb_seed` (4 dòng 2026-02-15→05-15; 29 dòng NaN): seed = chính WB RSS3 (2,26/2,39/2,51/2,69). TE tháng tương ứng thấp hơn 17–22% → **TE không thay được seed**; seed đúng nguồn, chỉ thưa (tháng). WB rubber hiện có trong BQ (RSS3, 2026-01→09) đã phủ seed đúng định nghĩa.
- RSS3 thật trong csv (`regionalert`) tháng 6–10: 2,76/2,81/2,70/2,75/2,86 ≈ WB 2,86/2,78/2,73/2,75 (khớp).
- Độ phủ: csv 68 điểm RSS3 thật (tuần) từ 2026-06-19; TE daily có 89 phiên cùng cửa sổ. `tsr20_usdkg` csv chỉ 64 điểm → TE daily cho TSR20 dày hơn và có từ 2016-10.
- `cn_rmb_ton` (91 điểm) vs TE `synthetic_rubber` CNY/T: lệch +22% TB (15–37%) → khác hợp đồng, không thay.
- **Kết luận:** RSS3: không thay (giữ regionalert + WB). TSR20: bổ sung được (backfill lịch sử + daily).

## (ii) `data/bdi_daily_real.csv` vs `baltic_dry` TE daily → **BỔ SUNG/dự phòng; thay được về giá trị, chưa về độ tươi**
- csv 114 ngày (2026-05-05→10-22; investing 21, handybulk 92, tradingeconomics 1). TE 2.505 ngày (2016-10-28→10-23).
- Toàn kỳ chung: **112/114 khớp tuyệt đối**; 2 ngày lệch: 2026-07-06 csv 2717 vs TE 2797 (−80); 2026-08-31 csv 3186 vs TE 3157 (+29).
- TE có 9 phiên mà csv thiếu trong cửa sổ (05-25, 06-10, 06-17, 06-22, 07-31, 08-21, 08-28, 09-11, 10-01) → csv có lỗ ~8%.
- Độ trễ: csv mtime 2026-10-23 20:05 ICT nhưng dòng cuối 10-22; TE đã có 10-23 (nạp 10-24/25). Csv luôn T-1 lúc chạy 20:05 (`fetched`=date, 114/114). `fetched_at` TE là nạp theo đợt → KHÔNG đo được độ trễ từng ngày của TE.
- Csv có BCI/BPI/BSI/BHSI (handybulk) mà TE không có.
- **Kết luận:** thay được giá trị BDI (độ khớp 98,2%); không thay cột phụ; dùng TE để lấp 9 ngày thiếu/lịch sử 2016+. Chưa thể thay nguồn live khi TE chưa có writer/cron.

## (iii) CSV tháng vs bảng
| file | kỳ | vs WB trong bảng | TE daily-avg vs WB (tháng chung) |
|---|---|---|---|
| brent_monthly.csv | 2006-04→2026-09 (246) | **246/246 khớp, lệch 0,00** | n=120, TB \|lệch\| 1,7%, max 15,9% |
| urea_monthly.csv | 246 | 246/246 khớp | n=87, TB 9,2%, median +4,2%, max 30,9% |
| iron_ore_monthly.csv | 246 | 246/246 khớp | n=120, TB 2,0%, max 6,8% |
| dap_monthly.csv | 246 | 246/246 khớp | TE không có dap |
| brent_monthly_full.csv | 2013-01→2026-05 (161) | chỉ 15/161 khớp, max lệch 4,92 | — (series khác, không phải WB) |
- Brent T9/2026: WB 116,8 vs TE daily-avg 100,8 (monthly TE 98,0). TE spot 10-23 = 116,72 → WB T9 đáng ngờ chưa giải thích.
- **Kết luận:** 4 csv WB đã **trùng hoàn toàn** bảng (bản sao WB) → bảng KHÔNG thêm thông tin cho tháng; **BỔ SUNG** duy nhất là TE daily nowcast trong tháng (khác định nghĩa, không thay). `brent_monthly_full.csv` không phải WB → xác định nguồn trước khi dùng.

## Giới hạn / việc mở
- Writer của bảng không tìm ra, không cron làm mới → chưa nên thay nguồn production bằng bảng đến khi có writer rõ.
- TE tea/salmon cập nhật thưa.
