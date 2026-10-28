# Mã lớn đã biến mất — giá, BCTC, thống kê trực tiếp (Winston, 2026-10-20)

Job `Winston_20261020_091618`. Bước 2 của điều tra survivorship; đọc lại `delisted-tickers-survivorship-20261020.md`. Chỉ đọc/đo, không ghi bảng canonical, không dùng `profit_*`. KHÔNG kết luận lại số pin.

Tệp: `delisted-big-vanished-prices-20261020.csv` (15 mã, danh sách + lý do chọn + toàn bộ thống kê) · `delisted-big-vanished-fin-8q-20261020.csv` (BCTC 8 quý) · giá ngày `delisted-tickers-survivorship-20261020.d/prices/<MÃ>.csv` (15 mã) · giá thô 229 mã `in_data=False` (không gồm chuyển sàn) `…d/prices_all/` · đối chiếu nguồn thứ hai `…d/xsource_check_simplize.txt` · mã nguồn `agents/Winston/research/vanished_20261020/`.

## Kết luận (7 dòng)
1. **Có giá ngày dùng được cho cả 15 mã**, kể cả sau khi chuyển UPCOM, từ API công khai của VNDirect (`api-finfo.vndirect.com.vn/v4/stock_prices`, không cần khoá; phải gửi `User-Agent` kiểu curl, UA mặc định của `requests` bị 403). Phủ từ **2013-01-02** (mã niêm yết sau đó thì từ ngày niêm yết). Có `close` (chưa điều chỉnh) + `adClose` (đã điều chỉnh) + khối lượng + giá trị khớp lệnh/thỏa thuận (VND). Cả 229 mã `in_data=False` đã được tải; chỉ **FPC** rỗng.
2. **Độ tin cậy đo được:** trên VNM (2192 ngày, 2018→2026) `adClose×1000` lệch BQ `Close` ≤0,1% (p5–p95 = 0,999–1,000), khối lượng khớp 1,000, `close`/`Price` khớp 1,000 ⇒ **cùng quy ước điều chỉnh với BQ**. Với mã đã hủy: đối chiếu độc lập tháng-cuối với Simplize (mục 3): 9/14 mã khớp 100%.
3. **Trong 229 mã, chỉ 36 từng có GTGD trung vị 60 phiên ≥5 tỷ** trên sàn gốc (55 mã ≥1 tỷ). 15 mã đã chọn có đỉnh ≥16,7 tỷ và cả 15/15 từng vượt ADV≥5 tỷ; 5 mã đầu (ROS, FLC, GAB, KLF, ART) đều ≥82 tỷ.
4. **Tổn thất xảy ra TRƯỚC khi ngừng giao dịch, và phần lớn mã vẫn đủ thanh khoản gần sát đáy.** Sụt từ đỉnh đến ngày khớp cuối: −75% … −99% ở 14/15 mã (trung vị ≈ −94%; ngoại lệ GAB −0,3% vì đã halt từ 2022-03); FLC, ROS giữ ADV≥5 tỷ đến đúng ngày giao dịch cuối. Sau đó giá đứng yên ở UPCOM (thay đổi ≈0 đến −5%, trừ HVG −74%, NHP −57%).
5. **BCTC không cảnh báo sớm cho phần lớn:** ROS 4 quý cuối LNST +95 tỷ, CFO +416 tỷ, vốn chủ 12.000 tỷ, nợ vay 1.105 tỷ; GAB lãi, nợ thấp; FLC lỗ 4 quý −1.086 tỷ nhưng CFO +4.300 tỷ. Lỗ 4/4 quý + CFO âm chỉ ở PSH, DAG (TTB lỗ 3/4 quý + CFO âm; HVG, NHP lỗ 4/4 quý nhưng CFO dương). ⇒ Đừng mặc định "chỉ cần bộ lọc chất lượng là loại được" (nhưng chưa tính rating 8L thật — để Taylor).
6. **Rủi ro thực thi riêng:** từ ngày giao dịch cuối (khối lượng>0) đến ngày hủy niêm yết có **20–468 ngày lịch** không giao dịch được (halt): ROS 20, FLC 162, HAI 221, AMD 120, GAB 468, ART 265, TGG 91, TTB 183, KLF 326, SJF 356. Lỗ trong khoảng halt không thoát được ⇒ replay phải coi vị thế bị **kẹt** tại giá khớp cuối, không phải bán ở giá hủy. 2–7 phiên giảm sàn (≤−6,5%) trong 20 phiên cuối ở 12/15 mã (trừ GAB, HVG, NHP).
7. **Công sức còn lại cho replay: nhỏ ở phần giá, trung bình ở phần rating** — xem mục 6.

## 1. Cách chọn 15 mã (tiêu chí khách quan, lưu trong CSV cột `selection`)
Tải giá 229 mã `in_data=False`, `cat≠chuyen_san`, từ `delisted-tickers-survivorship-20261020.csv`. Với mỗi mã tính **đỉnh của GTGD trung vị 60 phiên (nmValue+ptValue, VND) trên sàn gốc HOSE/HNX** (ngưỡng "lớn" theo thanh khoản vì không có vốn hóa trong nguồn). Lấy 15 mã đầu **cộng** 8 mã Mike nêu (FLC, ROS, HAI, AMD, GAB, ART, TGG, TTB): cả 8 đã nằm sẵn trong top 15 nên không có mã nào được thêm ngoài tiêu chí. Danh sách: ROS, FLC, GAB, KLF, ART, HVG, HAI, AMD, SJF, PSH, TTB, KSA, TGG, DAG, NHP. Mã tiếp theo (không chọn): TNA, CEE, DPS, VIS, CAV (đỉnh 9,7–16,5 tỷ). Mã 16–36 còn lại có ≥5 tỷ — nên thêm nếu Taylor cần độ phủ rộng hơn (giá đã tải sẵn trong `prices_all`, chỉ cần chạy `analyze.py`).
Lý do hủy (từ `corporate_action` SUSP): 13/15 "vi phạm nghiêm trọng nghĩa vụ CBTT"; NHP chậm nộp BCTC 3 năm; TTB ghi "chuyển sàn sang HOSE" nhưng thực tế **rời HOSE sang UPCOM 2024-01** (nhãn `khac_khong_ro` trong bảng CA là SAI cho mã này — dữ liệu giá cho thấy floor cuối = UPCOM).

## 2. Bảng thống kê trực tiếp (ngày cuối = ngày khớp cuối có khối lượng>0 trên sàn gốc; giá adClose)
| Mã | Sàn gốc | Ngày khớp cuối | Halt (ngày lịch) đến hủy | Giá 12T | Giá 24T | Max DD 24T | GTGD trung vị 60p cuối (tỷ) | Đỉnh GTGD 60p (tỷ) | ≥5 tỷ lần cuối | Đỉnh→ngày cuối |
|---|---|---|--:|--:|--:|--:|--:|--:|---|--:|
| ROS | HOSE | 2022-08-11 | 20 | −53% | +7% | −87% | 18,7 | 763 | 2022-08-11 | −98,6% |
| FLC | HOSE | 2022-09-08 | 162 | −67% | +15% | −85% | 27,6 | 387 | 2022-09-08 | −84,2% |
| GAB | HOSE | 2022-03-25 | 468 | +11% | +62% | −5% | 0,13 | 164 | 2022-03-17 | −0,3% |
| KLF | HNX | 2023-03-10 | 326 | −88% | −73% | −93% | 0 | 116 | 2022-11-01 | −95,8% |
| ART | HNX | 2022-11-18 | 265 | −91% | −48% | −93% | 2,3 | 82 | 2022-10-28 | −94,1% |
| HVG | HOSE | 2020-05-14 | 82 | +39% | +49% | −71% | 0,56 | 59 | 2020-02-11 | −75,4% |
| HAI | HOSE | 2022-09-08 | 221 | −64% | −42% | −85% | 2,7 | 58 | 2022-07-18 | −93,1% |
| AMD | HOSE | 2023-03-08 | 120 | −84% | −65% | −92% | 0,8 | 50 | 2022-09-28 | −95,3% |
| SJF | HOSE | 2023-11-10 | 356 | −39% | −85% | −93% | 1,4 | 40 | 2022-08-24 | −93,6% |
| PSH | HOSE | 2025-03-11 | 105 | −77% | −72% | −89% | 1,0 | 28 | 2024-08-21 | −94,2% |
| TTB | HOSE | 2023-07-06 | 183 | −48% | −69% | −86% | 1,4 | 25 | 2022-06-22 | −92,2% |
| KSA | HOSE | 2018-05-16 | 77 | −73% | −92% | −93% | 0,4 | 19 | 2016-08-17 | −96,5% |
| TGG | HOSE | 2023-09-15 | 91 | −66% | −96% | −97% | 0,6 | 19 | 2022-09-09 | −96,8% |
| DAG | HOSE | 2024-08-14 | 68 | −73% | −79% | −79% | 0,4 | 18 | 2023-09-07 | −92,1% |
| NHP | HNX | 2021-04-02 | 82 | +133% | −13% | −67% | 0 | 17 | 2016-12-23 | −96,7% |
Giá 12T/24T = adClose ngày khớp cuối / adClose cách đó 12/24 tháng. "Đỉnh→ngày cuối" = từ đỉnh toàn lịch sử trên sàn gốc. Cột đầy đủ hơn trong CSV (ngày liệt kê cuối, thay đổi giá sau halt, giảm sàn 20 phiên, v.v.). **Cảnh báo cách đọc:** mã có giá 12T/24T dương (ROS +7%, FLC +15%, GAB +62%, HVG) vẫn mất 85–99% từ đỉnh — chỉ số 12/24T một mình KHÔNG phản ánh cú nổ; dùng DD.

## 3. Nguồn, độ phủ, độ tin cậy
| Nguồn | Dùng cho | Kết quả |
|---|---|---|
| VNDirect finfo `stock_prices` (chính) | giá ngày, KL, GTGD, sàn | 229/230 mã có dữ liệu; từ 2013-01-02; có cả đoạn UPCOM sau hủy; `adClose` khớp BQ ≤0,1% (VNM) |
| Simplize `api.simplize.vn/api/historical/prices/chart?period=all` | đối chiếu độc lập (chỉ **nến tháng**) | `ts` là 17:00Z ngày cuối tháng = **ngày 1 tháng sau theo ICT**; phải +7h mới khớp tháng |
| VNDirect `financial_statements` (modelType 1/2/3, theo quý) | BCTC | 14/15 mã (ART là CTCK, modelType 91, mã khoản khác — chưa lấy) |
| Vietstock / CafeF | thử | trang trả HTML, cần phân tích riêng; không dùng |
| SSI iboard `stock-price` | thử | trả `data:null` cho mã đã hủy ⇒ không dùng |
| Đối chiếu tháng-cuối adClose (VNDirect vs Simplize, sai số 0,5%) | | ROS, HAI, AMD, TGG, TTB, KLF, SJF, PSH, NHP, GAB (giá) = **100%** · ART 91% · FLC 76% · DAG 59% · **HVG 0,8%** |

**Phân hạng giá dùng để replay:**
- **A (tin được cả giá điều chỉnh):** ROS, HAI, AMD, TGG, TTB, KLF, SJF, PSH, NHP.
- **B (dùng được, kiểm điều chỉnh từng sự kiện):** FLC (76%), ART (91%), DAG (59%) — lệch nằm ở một số tháng có corporate action; giá `close` chưa điều chỉnh vẫn dùng được cho đoạn không có sự kiện. GAB: giá khớp 100% nhưng **khối lượng lệch** (Simplize gấp ~7,7×, khớp ≤1% chỉ 12% số tháng) ⇒ **không tin GTGD/ADV của GAB** (kết quả ADV≥5 tỷ của GAB là chưa kiểm chứng).
- **C (KHÔNG dùng `adClose`):** HVG — hệ số điều chỉnh hai nguồn bất đồng (0,8% khớp), VNDirect có `adClose/close` thấp tới 0,34. Chỉ nên dùng `close` thô với đoạn chưa có sự kiện, hoặc để nguyên chưa quyết.
- **Chưa đối chiếu:** KSA (Simplize không có mã).
- Cảnh báo chung: (a) đối chiếu hai nguồn chỉ ở **cuối tháng**, không phải từng ngày; (b) cả hai nguồn có thể cùng lấy nguồn gốc ở sở GDCK ⇒ "độc lập" mức vừa phải; (c) KL lệch ở ~30–40% tháng của nhiều mã (Simplize có thể gộp thỏa thuận) ⇒ GTGD tính ở đây = nmValue+ptValue của VNDirect, chưa kiểm chứng độc lập; (d) hệ số điều chỉnh là của nhà cung cấp, **tôi không tự suy hệ số**; (e) UPCOM sau hủy: giá đứng yên, GTGD ≈ 0 ⇒ không coi là thanh khoản thật.

## 4. BCTC 8 quý trước ngày khớp cuối (VNDirect, theo quý; `…fin-8q-20261020.csv`)
4 quý cuối (tỷ VND) — doanh thu / LNST / CFO · nợ vay · vốn chủ · quý gần nhất:
| Mã | Quý cuối | DT 4Q | LNST 4Q | CFO 4Q | Số quý lỗ/4 | Nợ vay | Vốn chủ | Nợ phải trả/VCSH |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| FLC | 2022Q2 | 4.273 | −1.086 | +4.300 | 2 | 5.127 | 36.300 | 0,8 |
| ROS | 2021Q4 | 2.496 | +95 | +416 | 0 | 1.105 | 12.002 | 0,5 |
| HAI | 2022Q2 | 537 | −621 | −9 | 1 | 243 | 2.514 | 0,3 |
| AMD | 2022Q4 | 486 | −150 | +71 | 3 | 232 | 2.207 | 0,2 |
| GAB | 2021Q4 | 422 | +2 | −27 | 0 | 73 | 290 | 0,4 |
| TGG | 2023Q2 | 71 | −14 | +45 | 2 | 42 | 242 | 0,6 |
| TTB | 2023Q2 | 630 | −14 | −67 | 3 | 181 | 1.987 | 0,6 |
| KLF | 2022Q4 | 458 | −90 | −57 | 2 | 475 | 2.302 | 0,3 |
| HVG | 2019Q4 | 3.629 | −1.402 | +404 | 4 | 3.022 | 7.793 | 0,9 |
| SJF | 2023Q3 | 142 | −321 | +64 | 2 | 157 | 1.060 | 0,2 |
| PSH | 2024Q4 | 678 | −790 | −814 | 4 | 6.884 | 10.713 | 0,9 |
| KSA | 2018Q1 | 315 | +12 | −10 | 0 | 103 | 1.293 | 0,2 |
| DAG | 2024Q2 | 367 | −266 | −465 | 4 | 1.111 | 1.198 | 1,1 |
| NHP | 2020Q1 | 11 | −27 | +43 | 4 | 65 | 279 | 0,4 |
| ART | — | không lấy được (CTCK, modelType 91, mã khoản khác) | | | | | | |
Cảnh báo: (1) "Nợ vay" = khoản `13110`+`13340` của VNDirect, tên mô tả mơ hồ ("Short term Loan and Liabilities") — **chưa xác nhận là vay có lãi** (cần đối chiếu với BQ `ticker_financial` cho một mã còn dữ liệu trước khi dùng); (2) không rõ hợp nhất hay riêng lẻ — VNDirect gom `modelType` 1/2/3 mà không ghi; (3) CFO quý dao động dấu nên có vẻ là CFO đơn quý nhưng chưa xác nhận chống lại BCTC gốc; (4) quý cuối có thể cách ngày khớp cuối >1 quý vì công ty không nộp (ROS: không có BCTC 2022Q1–Q2 trên VNDirect, FLC dừng ở 2022Q3 trong dữ liệu thô; thực tế chậm/không nộp BCTC chính là nguyên nhân hủy); (5) số liệu này là **sau điều chỉnh/số công bố**, chưa biết có bị làm đẹp hay không (xem cảnh báo pháp lý).

## 5. Tình trạng pháp lý/quản trị (CẢNH BÁO, không phán xét — luật user 2026-09-27)
- **Nguồn đã kiểm trong job này:** chỉ lý do trong `tav2_bq.corporate_action` (13/15 vi phạm nghiêm trọng nghĩa vụ CBTT; NHP chậm BCTC 3 năm; TTB chuyển sàn nhưng thực tế bị loại khỏi HOSE).
- **Không tra cứu được trong job này** (không có nguồn tin cậy đã mở): vụ án hình sự, thao túng giá, vụ hủy niêm yết/thanh tra chi tiết của từng công ty — kiến thức nền cho thấy FLC, ROS, HAI, AMD, GAB, ART, TGG, TTB, KLF nằm trong nhóm vụ việc có liên quan lãnh đạo/thao túng 2022–2023, nhưng **đó là hiểu biết chung, chưa được tôi xác minh bằng văn bản công khai trong phiên này** ⇒ không dùng làm căn cứ. Việc cần làm: Wendy (legal-vn) tra từng mã nếu cần.
- Hệ quả đo được: 13/15 mã bị loại vì CBTT ⇒ số liệu BCTC công bố có thể không đáng tin ngay cả trước ngày bị loại.

## 6. Dùng để replay BAL/LAG — nên/không nên, công sức còn lại
**Nên dùng ngay:** chuỗi `adClose`, `close`, khối lượng, GTGD của hạng A cho 9 mã (ROS, HAI, AMD, TGG, TTB, KLF, SJF, PSH, NHP) để: (a) kiểm tra mã có nằm trong `universe_pit` tương ứng (ADV≥5 tỷ, giá, v.v.) tại từng ngày; (b) mô phỏng vị thế kẹt từ ngày khớp cuối đến ngày hủy (giữ nguyên giá khớp cuối, không thoát được); (c) đo thiệt hại tối đa nếu 1 mã lọt vào rổ ở mức tỷ trọng cap.
**Dùng có điều kiện:** FLC, ART, DAG (kiểm sự kiện điều chỉnh); GAB (chỉ giá; không dùng ADV).
**Không dùng `adClose`:** HVG (bất đồng hệ số). KSA chưa kiểm.
**Chưa làm / công sức còn lại (ước lượng của tôi, chưa đo):**
1. Dựng cột đầu vào rating 8L cho các mã này (cần map mã khoản VNDirect → trường `ticker_financial`; còn thiếu ART và các trường PE/PB/ROE… VNDirect có endpoint `ratios`/`financial_models` nhưng chưa thử) — **~1–2 ngày**. Không có rating thì không biết 8L có tự loại được hay không (đó mới là câu hỏi chính).
2. Đưa 15 mã vào `universe_pit` bản sao (không ghi bảng canonical) — **~0,5 ngày**; kiểm thanh khoản ADV bằng GTGD VNDirect.
3. Mở rộng 15 → 36 mã có đỉnh ADV≥5 tỷ (giá đã tải, chỉ cần chạy lại script + BCTC) — **~0,5 ngày**.
4. Lấp khoảng 2009–2012: VNDirect chỉ phủ từ 2013-01-02; Simplize có nến tháng từ 2006–2011 (không dùng cho ADV) ⇒ mã hủy 2009–2012 chưa có giá ngày.
**Rủi ro nguồn:** VNDirect finfo là API không chính thức/có thể đổi, chặn UA, hay bị giới hạn tốc độ; Simplize nến tháng chỉ để đối chiếu. Nên chốt bản sao tải về và **không phụ thuộc gọi lại** (đã lưu CSV thô 229 mã).

## Bẫy đã gặp / ghi chú vận hành
- `requests` mặc định UA bị VNDirect trả 403 (13 byte); curl UA OK. Giá VNDirect đơn vị **nghìn VND**, `nmValue` đơn vị **VND**.
- `last_trade` trong bảng CA là ngày **hành chính**, KHÁC ngày khớp cuối thật (FLC: CA 17/02/2023 vs khớp cuối 2022-09-08; GAB: CA 24/02/2023 vs 2022-03-25). Với replay phải dùng ngày khớp cuối từ giá.
- `after_last_trade_orig` trong CSV giá đánh dấu các hàng sau ngày khớp cuối trên sàn gốc (halt + UPCOM).
