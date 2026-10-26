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

## Bổ sung 26/10 chiều (Winston, job Winston_20261026_070857 — Mike/user duyệt)
Tạo 3 file MỚI trong `data/` (không đụng canonical/cron): `bdi_daily_te_fill.csv`, `bdi_daily_te_fill_NOTES.md`, `rubber_tsr20_te_daily.csv`. Nguồn `tav2_bq.commodity_prices`, source=trading_economics, cadence=daily; mỗi dòng có `src` + `fetched_at`. **Chưa có consumer, không phải production.**
- **BDI fill:** 10 ngày TE có mà `bdi_daily_real.csv` thiếu (05-25, 06-10, 06-17, 06-22, 07-31, 08-21, 08-28, 09-11, 10-01 + **10-23** mới). Đối chiếu 114 ngày chung: 112 khớp, 2 lệch — 07-06 (csv 2717 / TE 2797), 08-31 (csv 3186 / TE 3157). Không chọn bên. Quan sát: csv 08-31 = 3186 = đúng TE 08-28 (ngày csv thiếu) → nghi csv gán nhầm ngày; chưa kết luận.
- **TSR20:** 2.512 dòng 2016-10-25→2026-10-23, 0 trùng ngày, unit gốc `USD Cents / Kg` ÷100. Khớp `rubber_weekly.csv` (63 ngày chung, 2026-06-19→10-16): TE/csv trung bình **+0,49%**, sd 1,96%, max |lệch| 6,70%, chỉ 2/63 ngày khớp tuyệt đối. Cùng cỡ số cũ (−0,45% ±1,9%, chiều ngược) → cùng hạng TSR20 nhưng không cùng điểm quan sát/giờ chốt.
- **Self-check:** query lại BQ → BDI 10/10 và TSR20 2.512/2.512 giá trị trùng 100% (sai khác ≤1e-8 do float BQ); 0 ngày BDI trùng csv gốc; `git status` 2 csv canonical không đổi.

## Kiểm 2 ngày lệch (Winston, job Winston_20261026_071338)
**Kết luận: csv SAI ở 07-06; 08-31 cả hai bên đều không sạch (csv gán nhầm ngày, TE daily mang giá 3157 sang cả 08-31 lẫn 09-01). KHÔNG sửa code/cron/csv — chỉ đề xuất.**
- **Cơ chế writer** (`fetch_bdi_daily.py`): chỉ scrape handybulk, `src` luôn "handybulk" (investing/tradingeconomics là dòng nạp tay giai đoạn 05-05→06-05). `date` = chuỗi `d-Month-yyyy` ĐẦU TIÊN regex thấy trong HTML (dòng 30), KHÔNG phải ngày chạy, cũng không gắn với giá; `fetched` = `date` (dòng 58) nên không có dấu thời gian thật. Chạy cron 20:05 ICT T2-T6 (`paper_late_feeds.sh` step [21]); `drop_duplicates(date, keep=last)`.
- **07-06 (csv 2717 / TE 2797): TE ĐÚNG, csv SAI.** Hellenic Shipping News "Baltic Dry Index climbs to 2797 up 50 points", đăng 06/07/2026 (https://www.hellenicshippingnews.com/?p=1139891; bài ghi nhầm thứ "Friday"). Dòng csv 07-06 trùng nguyên 5 chỉ số (BDI/BCI/BPI/BSI/BHSI) với dòng 07-03 = trang handybulk chưa cập nhật nhưng đã mang ngày 07-06 → bản sao cũ. Dấu vết: 07-07 csv 2875 khớp Hellenic (?p=1140043, "2875 up 78" → 2797 là mốc trước).  Lưu ý: "up 50" của Hellenic không khớp 2717 (→2747); chưa giải thích được (có thể 07-03 thật là 2747, csv+TE cùng 2717), chưa kiểm.
- **08-31 (csv 3186 / TE 3157):** Hellenic "3186 up 79" đăng **28/08** (https://www.hellenicshippingnews.com/?s=Baltic+Dry+Index+climbs+to+3186) và "3157 down 29" đăng **01/09** (…?s=Baltic+Dry+Index+falls+to+3157; delta −29 tính từ 3186 → không có mốc riêng cho 08-31). 31/08/2026 là Thứ Hai cuối tháng 8 = UK Summer Bank Holiday (suy luận, chưa tìm nguồn xác nhận Baltic Exchange nghỉ). Hệ quả: 3186 = đóng cửa 08-28 (TE đúng ở 08-28); csv ghi 3186 vào 08-31 là bản mang-sang ngày nghỉ gán ngày chạy → **csv sai ngày**; csv 09-01 = 3157 **khớp Hellenic**. TE 08-31 = 3157 cũng sai (nên là 09-01); 3113 ở 09-01 là dòng monthly (xem đính chính).
- **Không tìm được** bài Hellenic cho 07-03, 07-07 (chỉ suy từ delta), 08-27, 08-31; không có HTML/JSON gốc handybulk lưu lại trong `data/` hay logs (`mike/logs/paper_late_feeds.log` không tồn tại) → không xác minh được trang gốc.
- **Hệ thống (bước 4):** csv có đúng 1 dòng trùng nguyên 5 chỉ số với dòng trước = 07-06. Dòng csv = giá TE ngày trước: 07-06, 08-31 (+ 06-01, 07-01, 09-01 nhưng đó là do TE có ngày trùng, không phải lỗi csv). Cả 2 ca thật đều là **Thứ Hai**; handybulk có 19 Thứ Hai, 20 T3, 18 T4, 20 T5, **15 T6** (Thứ Sáu thiếu nhiều: 08-28 không có trong csv). Mẫu quá nhỏ để khẳng định quy luật; gợi ý chạy 20:05 ICT gặp trang chưa cập nhật / ngày nghỉ.
- **[Mike đính chính 26/10 14:2x] 'Dòng ma' ở TE là hiểu nhầm:** 3007 dòng = 2505 daily + 502 monthly (cadence khác nhau). Dòng thứ hai vào ngày mùng 1 là dòng cadence=monthly (trung bình tháng, gắn ngày đầu tháng), vd 2026-07-01 daily 2562 / monthly 2732; 2026-09-01 daily 3157 / monthly 3113. Khoá (metric_key,source,cadence,observation_date) duy nhất 296.520/296.520. Mọi so sánh theo ngày phải lọc cadence='daily'. Việc thật: TE daily có 3157 ở CẢ 2026-08-31 và 2026-09-01 (mang giá sang ngày nghỉ).
- **Đề xuất (chưa làm):** (1) `fetch_bdi_daily.py`: bỏ qua/ghi cờ khi cả 5 chỉ số trùng dòng trước, hoặc khi `date` không bằng ngày hiệu lực của số liệu; lưu `fetched` = giờ chạy thật; lưu HTML thô mỗi lần. (2) Ghép đối chiếu cuối ngày với Hellenic/TE, và coi TE chỉ là tham chiếu tới khi dedupe xong. (3) Ghi chú NOTES: sửa 07-06 → 2797 (có nguồn); 08-31 → bỏ dòng (ngày nghỉ), thêm 08-28 = 3186.

## Đã sửa (Winston, job Winston_20261026_073848, 2026-10-26)
- `data/bdi_daily_real.csv` (backup `.bak_20261026`): 07-06 2717→2797 (Hellenic ?p=1139891; BCI/BPI/BSI/BHSI để trống vì không biết giá trị đúng, src ghi chú); xóa 08-31; thêm 08-28=3186 (hellenic/TE, các chỉ số phụ để trống). Diff đúng 3 thay đổi.
- `fetch_bdi_daily.py` (merge 51adab729, code e9e213859): (a) 5 chỉ số trùng dòng liền trước ⇒ không ghi, WARN stderr, exit 0; (b) `fetched` = giờ chạy ICT ISO có tz (consumer duy nhất `freight_map.current_bdi` chỉ đọc date/bdi — không vỡ); (c) HTML thô lưu `data/raw/bdi_handybulk_<date_HHMM>.html`, giữ 30 ngày (gitignore). Selfcheck `fetch_bdi_daily_selfcheck.py` PASS dưới `env -u TZ` và `TZ=America/New_York`.
