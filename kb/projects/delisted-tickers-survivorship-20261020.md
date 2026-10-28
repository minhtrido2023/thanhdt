# Mã hủy niêm yết / ngừng giao dịch 2009→2026 và survivorship của backtest (Winston, 2026-10-20)

Job `Winston_20261020_075929`. Chỉ đọc/đo, không sửa dữ liệu. Không dùng `profit_*`.
CSV chi tiết: `delisted-tickers-survivorship-20261020.csv` (581 mã, 1 dòng/mã) · số liệu phụ: `delisted-tickers-survivorship-20261020.d/`.

## Kết luận (6 dòng)
1. **Nguồn nội bộ có sẵn mà trước đây không ai dùng:** `tav2_bq.corporate_action` có `event_code='SUSP'` = 691 dòng / 581 mã (2009-04→2026-10) kèm **lý do + ngày giao dịch cuối + ngày hủy** trong `event_description_vi`. Đó là danh sách hủy niêm yết/hủy ĐKGD/tạm ngừng — không cần mua dữ liệu mới để có **danh sách + ngày**. Thiếu **giá cuối và BCTC**.
2. **Phân loại 581 mã:** 134 chỉ chuyển sàn (không biến mất) · 447 rời sàn thật: 216 bắt buộc (lỗ 3 năm, kiểm toán từ chối/ngoại trừ, vi phạm CBTT, chậm BCTC) · 164 mất tư cách công ty đại chúng (UPCOM) · 12 sáp nhập · 11 tự nguyện · 44 không rõ lý do.
3. **Dữ liệu ta cầm là survivor-only đúng như nghi ngờ:** 230/447 mã rời sàn **không có dòng nào** trong `ticker_financial`/`ticker_pin`. Mã có dòng cuối sớm nhất toàn hệ là **2025-05-15** (V11). Không có mã ma nào trong snapshot nào (xem §2a).
4. **Giả thuyết "8L tự loại" đúng một phần, không phải mặc định:** trong 127 mã bị hủy niêm yết bắt buộc trên HOSE/HNX (2014-09→2026) mà **vẫn còn data** (vì chuyển xuống UPCOM), rating 8L ngay trước thông báo: 100 mã = 4, 15 mã = 5, **12 mã (9,4%) ≤3**. 10/127 (7,9%) từng có ≥1 ngày **vừa ở `universe_pit` vừa rating ≤3** trong 12 tháng trước thông báo — tức vẫn vào được vùng mua.
5. **Mất tư cách công ty đại chúng (UPCOM) gần như vô hại với backtest:** 0/32 mã đã ngừng 2025-26 từng nằm `in_universe` trong 12 tháng cuối. Rủi ro nằm ở nhóm **HOSE/HNX bắt buộc, biến mất hẳn khỏi data**.
6. **Thiên lệch ước lượng thô: nhỏ, thiên về lạc quan, cỡ vài chục bps CAGR/năm, không phải 0** (§4). Phần không đo được: cú nổ của FLC/ROS/HAI/AMD/GAB/ART… vì thiếu cả giá.

## 1. Đếm theo năm (mã duy nhất, `corporate_action` SUSP, ngày hủy hoặc ngày công bố)
Cột "mất khỏi data" = không có dòng nào trong `ticker_financial`. `n_univ_pit` = số mã khác nhau `in_universe` trong năm (mẫu số).

| Năm | Bắt buộc | MC đại chúng | Sáp nhập | Tự nguyện | Không rõ | **Tổng rời sàn** | trong đó mất khỏi data | Chuyển sàn (không mất) | n_univ_pit |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 2009 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 13 | 278 |
| 2010 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 427 |
| 2011 | 5 | 0 | 1 | 0 | 0 | 6 | 1 | 4 | 407 |
| 2012 | 5 | 0 | 1 | 0 | 1 | 7 | 1 | 2 | 257 |
| 2013 | 6 | 0 | 2 | 3 | 4 | 15 | 7 | 0 | 212 |
| 2014 | 1 | 0 | 0 | 0 | 19 | 20 | 6 | 1 | 276 |
| 2015 | 15 | 0 | 4 | 4 | 3 | 26 | 10 | 4 | 312 |
| 2016 | 12 | 0 | 0 | 0 | 2 | 14 | 5 | 6 | 344 |
| 2017 | 10 | 1 | 0 | 0 | 3 | 14 | 3 | 7 | 361 |
| 2018 | 13 | 1 | 1 | 1 | 3 | 19 | 8 | 16 | 382 |
| 2019 | 31 | 1 | 1 | 1 | 2 | 36 | 18 | 7 | 328 |
| 2020 | 15 | 3 | 1 | 0 | 3 | 22 | 7 | 14 | 350 |
| 2021 | 16 | 13 | 0 | 2 | 0 | 31 | 20 | 19 | 588 |
| 2022 | 15 | 49 | 0 | 0 | 0 | 64 | 50 | 7 | 615 |
| 2023 | 26 | 21 | 0 | 0 | 0 | 47 | 29 | 7 | 487 |
| 2024 | 24 | 15 | 0 | 0 | 1 | 40 | 25 | 8 | 490 |
| 2025 | 14 | 26 | 0 | 0 | 1 | 41 | 21 | 11 | 471 |
| 2026* | 7 | 34 | 1 | 0 | 0 | 42 | 19 | 8 | 451 |

\*đến 2026-10-12. Theo sàn (tổng rời sàn, bảng đầy đủ `.d/by_year_exchange.csv`): HNX 155, HOSE 93, UPCOM 172 mã (sàn lấy từ tiêu đề/mô tả; mã 2009-2013 thiếu sàn được gán theo ngữ cảnh nếu có).
Số "bắt buộc" HOSE+HNX mỗi năm 2015-2025: 10-26 mã (2015:15, 2016:12, 2017:10, 2018:13, 2019:21, 2020:14, 2021:16, 2022:15, 2023:26, 2024:24, 2025:14).
**Sáp nhập/hợp nhất:** 17 dòng `MA` (16 mã, 2010-04→2026-03) + 12 mã phân loại sáp nhập từ lý do; con số này gần như chắc chắn **thiếu** — sáp nhập thường được nhập vào ISS/AIS, không phải SUSP/MA. **Chuyển sàn:** 432 sự kiện `MOVE` / 395 mã (không biến mất, đã tách riêng).
**Đình chỉ kéo dài:** nguồn chỉ có "tạm dừng niêm yết" 2009-2013 dạng tiêu đề chung; không có cờ "đình chỉ giao dịch" cho mã đang sống ngoài `SUSP`. Chưa đếm được riêng — xem mục thiếu.

### Độ phủ & tin cậy của từng nguồn
| Nguồn | Phủ | Tin cậy | Ghi chú |
|---|---|---|---|
| `tav2_bq.corporate_action` SUSP | 2009→2026-10, 581 mã | **Cao 2019+, trung bình 2014-18, thấp 2009-13** | 2009-13 chỉ 60 sự kiện / 55 mã, nhiều dòng tiêu đề chung "Tạm dừng Niêm yết", một số mã không rõ sàn. Bảng nạp 1 lần 2026-08-12 (TRAP trong registry); đây là snapshot, chưa kiểm refresh. Thông báo tạm ngừng có thể trùng thông báo hủy. |
| Phân loại tự động (regex trên lý do) | cả 581 | Trung bình | Dựng bằng từ khoá; 44 mã "không rõ"; "mất tư cách CTĐC" gộp cả bị cưỡng chế và chủ động. Không kiểm tay từng ca. |
| `ticker_financial` / `fa_ratings_8l` / `ticker_pin` | 1291-1294 mã | Chính xác cho việc đo "còn trong data" | Chỉ chứa mã còn sống sau 2025-05. |
| Không dùng: danh sách HOSE/HNX/VSDC/Vietstock/CafeF | — | — | **Chưa tra** (phiên headless, không xác minh được nguồn ngoài). Muốn đối chiếu độc lập phải làm thêm. |

## 2. Dữ liệu nội bộ còn sót
**(a) Snapshot cũ — không có mã ma.** `ticker_pin_202607` (1291 mã) ⊂ `ticker_pin_202610` (1294 mã; +3 mã niêm yết mới); `ticker_prune_ttbackup_fresh_20260713` 513 mã, 0 mã ngoài pin10; `ticker_financial_ttbackup_fresh_20260714` 1284 mã, 0 ngoài bảng hiện tại; `data/bq_cache_asof20260728` và `...0729_postrestate` đều 1291 mã, trùng hệt nhau; `_cache_universe_2005_now.pkl` (1281 mã), `fundamental_rating_*_backup_20260510.csv` (659 mã), `_ticker_prune_list.csv`, `bal_universe_2024_25.csv`: 0 mã ngoài bộ hiện tại. **Không có bản lưu nào chứa mã đã mất.**
Ghi chú ngoài phạm vi (đã báo bus trước đó): `tav2_bq.ticker` live hôm nay chỉ 1066 mã (mất 243 mã) — sự cố đang xử lý riêng, không liên quan danh sách này; số liệu ở đây dùng `ticker_financial`/`ticker_pin_202610`/cache.

**(b) Mã có dòng cuối sớm (đã ngừng giao dịch trong data):** 32 mã theo `ticker_pin_202610` (dòng giá cuối < 2026-06-01), 110 mã theo `fa_ratings_8l` (kể cả mã chỉ ngừng cập nhật quý). Toàn bộ danh sách + rating 4 quý cuối: `.d/ceased_in_data_with_8l.csv`. 31/32 khớp một sự kiện SUSP (30 "mất tư cách công ty đại chúng", V11 "thu hồi giấy chứng nhận ĐKDN"); **BCB** không khớp sự kiện nào (chưa rõ nguyên nhân). Tất cả là UPCOM/HNX nhỏ. Dòng giá cuối sớm nhất: V11 2025-05-15, EPH 2025-05-26, ATB/L44/NQT 2025-06-13.

**(c) Mẫu "đang bị hạn chế/cảnh báo" còn trong data — DGC:** `fa_ratings_8l` DGC = **2 (tier B)** liên tục từ 2025-07 đến 2026-07-22, `universe_pit` DGC `in_universe` đến 2026-10-19. ⇒ **8L không bắt rủi ro quản trị/pháp lý** (BCTC vẫn tốt); DGC chỉ bị loại nhờ `excluded_tickers` thủ công. Đây là bằng chứng trực tiếp rằng "BCTC xấu" ≠ "hủy niêm yết". Các mã bị đưa ra khỏi HOSE/HNX 2026 mà còn data: VAF (rating 1→1), HVX, AAV (5), SDA, VNE, BCG (5), TCD — xem `.d/mandatory_delist_inData_8l_test.csv`.

## 3. Kiểm chứng "8L tự loại"
Mẫu: 127 mã **bắt buộc hủy niêm yết HOSE/HNX, thông báo đầu tiên từ 2014-09-01** (8L bắt đầu 2014-08), vẫn còn data (đa số xuống UPCOM). Rating = 4 dòng 8L gần nhất ≤ ngày thông báo. Dữ liệu: `.d/mandatory_delist_inData_8l_test.csv`.

| Chỉ tiêu | Kết quả |
|---|---|
| Rating cuối trước thông báo | 1:1 · 2:2 · 3:9 · **4:100 · 5:15** |
| ≤3 (vùng mua) | **12/127 = 9,4%** |
| Từng ≤3 trong 4 quý cuối | 23/127 = 18% |
| Có ≥1 ngày `in_universe` trong 12 tháng trước | 48/127 = 38% |
| **Có ≥1 ngày vừa `in_universe` vừa rating ≤3** | **10/127 = 7,9%** (≥20 ngày: 8 mã) |
| Giá: median thay đổi 12 tháng trước thông báo (nhóm 10 mã) | −38% (mean −46%); tất cả 10 mã đều giảm ≥ −9% trừ IDC (+5%) |

10 mã: PHH 2015, ATA 2017, PIV 2018, ALV 2019, IDC 2019 (rating 2, 203 ngày!), LMH 2020, PXS 2022, PHP 2022 (rating 2-3, 250 ngày), BII 2023, DNM 2023. **IDC** (HNX, vi phạm CBTT, rating 2 cả 4 quý) và **PHP** (ngoại trừ kiểm toán, rating 2-3) cho thấy 8L **không** chặn mọi ca — rating dựa trên số BCTC đã công bố, trong khi lý do hủy là vi phạm CBTT hoặc ý kiến kiểm toán.
**Giới hạn của kết luận:** (i) mẫu này là các mã **còn data** — thiên về mã nhẹ hơn mã nổ; (ii) 64 mã bắt buộc HOSE/HNX (2013+) **không có data** (FLC, ROS, HAI, AMD, GAB, ART, TGG, TTB, IBC, SJF, KLF, DAG…) — lý do trong `corporate_action` đa số "vi phạm nghiêm trọng nghĩa vụ CBTT"/kiểm toán từ chối: BCTC trễ hoặc không có thì 8L không có số mới → nhiều khả năng rating cũ/NaN, **nhưng không đo được** vì không có BCTC trong data; (iii) tôi chưa tra BCTC công khai của các ca nổi tiếng (không xác minh được nguồn trong phiên này) — đừng trích tên ca nổi tiếng như bằng chứng; (iv) rating tại mốc thông báo, chưa mô phỏng danh mục thật.

## 4. Thiên lệch survivorship — thô, định tính
- **UPCOM mất tư cách CTĐC (164 mã, 158 mã từ 2021, 151 là UPCOM):** thanh khoản thấp, 0/32 mẫu 2025-26 từng ở `universe_pit` ⇒ **bỏ qua**.
- **Nhóm quan trọng: 64 mã bắt buộc HOSE/HNX mất khỏi data (2013-2025).** Nếu hành xử như mẫu 127 mã (38% từng ở universe, 7,9% vừa ở universe vừa ≤3) ⇒ ~24 mã từng ở universe, **~5 mã** từng nằm vùng mua trong 2015-2025 (≈0,45 mã/năm trên n_univ_pit 300-600 ⇒ **~0,1-0,2% số mã/năm**). Nếu rỗng BCTC làm rating xấu hơn mẫu ⇒ thấp hơn; nếu mã lớn như FLC/ROS từng thanh khoản cao 2021 ⇒ cao hơn.
- **Độ lớn:** mỗi mã nổ ~−60% trong danh mục 30 mã đồng trọng ≈ −2% NAV một lần. 5 mã/11 năm ⇒ ~−0,1-0,2 pp CAGR/năm; kể cả gấp 3 (mã lớn, mất 100%, trọng số cao) vẫn ≲ −0,5 pp. **Chiều: số backtest hiện tại CAO hơn thực tế (lạc quan).** Sharpe lệch cùng chiều nhẹ (đuôi trái thiếu).
- Không đặt con số này vào số pin R3/V2.4 — nó nhỏ hơn dải 23,37-25,71% và hệ số "CAGR thật ≈ backtest −1,5%" đã bao trùm bậc độ lớn đó, nhưng **chưa được tách riêng** trong hệ số đó.
- Hiệu ứng khác không đo: hai lớp lệch cùng chiều — (1) mã có data đến UPCOM vẫn "được cứu" bằng giá UPCOM sau khi hủy (px_ann_to_p60 median −9% trong nhóm universe, nhưng thanh khoản UPCOM khó thoát thật); (2) backtest thoát vị thế ở giá đóng cửa, thực tế không bán được khi bị ngừng giao dịch.

## 5. Đề xuất vá (chưa thực hiện)
| Phương án | Công sức | Rủi ro / giới hạn |
|---|---|---|
| **A. Dựng bảng `delisted_events` từ `corporate_action` SUSP (đã có 581 mã, ngày, lý do)** + mô phỏng "sự kiện loại" ở backtest: giả định −X% trong N phiên trước ngày hủy cho mã từng ở universe | ~0,5-1 ngày, đa số dùng lại CSV này | Cần giá cuối; nếu không có phải giả định (−40% median là từ mẫu 10 mã, rất nhỏ) |
| **B. Lấy giá lịch sử đến ngày giao dịch cuối cho ~64 mã mất data** (nguồn công khai: HOSE/HNX hoặc nhà cung cấp dữ liệu có hồ sơ delisted) rồi nạp vào bảng riêng `tav2_mike.*` (không ghi canonical) | 2-4 ngày + chi phí/giấy phép | Giá điều chỉnh sự kiện công ty; BCTC vẫn thiếu ⇒ rating 8L không dựng được ⇒ chỉ dùng cho test độ nhạy |
| **C. Stress test độ nhạy:** chèn 0,45 mã/năm × (−60..−100%) vào backtest R3/V2.4 để thấy ΔCAGR | ~0,5 ngày (Taylor) | Là giả định, không phải dữ liệu thật |
| **D. Để sau:** thêm cột `delist_flag` vào universe PIT để chặn mã có thông báo hủy trong T-90 (đã live-usable; thông báo CBTT/kiểm toán xuất hiện trước ngày hủy 30-60 ngày) | 0,5 ngày + Taylor duyệt | Đây là thay đổi luật LIVE ⇒ cần user duyệt; không liên quan survivorship của quá khứ |
Khuyến nghị: **C trước** (rẻ nhất, cho biên độ thật), A nếu muốn lưu danh mục sự kiện lâu dài; B chỉ khi C cho ra ΔCAGR >0,3 pp.

## Cách tái lập
1. `bq query` trên `tav2_bq.corporate_action WHERE event_code IN ('SUSP','MA','MOVE')` → `.d/ca_susp_ma_move.csv`; regex phân loại → `.d/susp_classified.csv`.
2. Mã còn trong data: `GROUP BY ticker` trên `ticker_financial`, `ticker_pin_202610`, `universe_pit`, `fa_ratings_8l` (`.d/cov_*.csv`).
3. Phép thử 8L: `.d/fa8l_mandatory_inData.csv` + `universe_pit` + `Close` từ `bq_cache_asof20260728`.
Interpreter: `/home/trido/thanhdt/wc_venv/bin/python` (pandas 3). Không đụng `profit_*`, không ghi bảng canonical.
