# DRI — định giá lại có điều chỉnh theo cung cao su (job `Taylor_20261027_084046`, 27/10/2026)

> Chỉ nghiên cứu, không lệnh, không pin. Lưới khai trước trong `PREREG.md` (commit `abefa2578`, md5 `12a9d8c1…`), commit
> trước khi chạy số. Tính toán: `python3 model_supply_adj.py` → `out.txt` (md5 output `c44eada5…`, giống hệt dưới
> `env -u TZ` và `TZ=America/New_York`). Dữ liệu BQ chụp vào `data/` (truy vấn 27/10).
> Nhãn: [BCTC3] · [SXKD] · [BQ] · [FEED] `data/*.csv` · [UL] ước lượng · [NỀN] hiểu biết nền, chưa kiểm ·
> [DISPATCH] số Mike nêu trong prompt, chưa đo. **Đây là bản để skeptic phản biện, không phải kết luận chốt.**

## 0. Trả lời 4 câu
**Selfcheck:** hàm cũ tái lập đúng Base **10.878** / kỳ vọng **11.031** (PASS) trước khi đổi tham số.

**(1) FV theo bộ trọng số PEAK/MID** (đ/cp; C 34, lương cố định, Q4 Base, tồn kho vượt 1.717 t; ngoặc = giá 14.700 so FV) [UL, mục 2]:
| r · đời khai thác | 80/20 | 60/40 (Bobby) | 40/60 |
|---|---|---|---|
| 10% · L0 (28 năm) | 13.879 (+6%) | 15.692 (−6%) | 17.504 (−16%) |
| 12% · L0 | 12.710 (+16%) | 14.301 (+3%) | 15.892 (−8%) |
| 13% · L0 | 12.226 (+20%) | 13.726 (+7%) | 15.226 (−3%) |
| 12% · L1 (gia hạn 50%) | 12.858 (+14%) | 14.478 (+2%) | 16.097 (−9%) |
| 12% · L2 (gia hạn 100%) | 13.007 (+13%) | 14.654 (0%) | 16.302 (−10%) |
- Khoảng: **80/20 ⇒ 12,2–14,5k · 60/40 ⇒ 13,7–16,4k · 40/60 ⇒ 15,2–18,3k**. Lưới mở rộng (thêm giá vốn 32/36, lương (b);
  162 ô): **10.046 – 21.215**, trung vị 15.038; 53% số ô có FV ≥ 14.700.
- Chỉ kịch bản PEAK (trọng số 100/0): 10.726 – 12.546. Chỉ MID: 18.226 – 22.170.

**(2) 14.700 so FV:** từ **+20% đắt** (80/20, r 13%) tới **−18% rẻ** (40/60, r 10%, L1). Ở bộ Bobby 60/40, giá nằm trong
±8% quanh FV, tức **gần giá trị hợp lý**, không còn "−25%" như báo cáo Q3.

**(3) Nhạy nhất với gì** (đổi một trục, giữ tâm 60/40 · r 12% · L0 · C 34; biên độ FV đo được, mục 4):
| Trục | Biên độ FV |
|---|---|
| **RSS3 giữa chu kỳ (1,865 → 2,30)** | **9.949 đ** (9.615 → 19.564) |
| Giá vốn/t (32 → 36) | 4.664 |
| Trọng số (80/20 → 40/60) | 3.183 |
| r (10% → 13%) | 1.966 |
| Tồn kho vượt (0 → 3.370 t) | 1.911 |
| Q4/26 (Bear → Bull) | 919 |
| Đời khai thác (L0 → L2) | 353 |
| Quỹ lương (a → b) | 347 |
Kết luận nằm ở **mức RSS3 giữa chu kỳ**, rồi tới **giá vốn/t**. Đời khai thác và cách xử lý quỹ lương gần như không đổi kết luận.

**(4) Vùng mua Mike nêu 21/10** (nguồn: prompt dispatch; tôi không tìm thấy trong KB/bus):
- **≤ 11.500: đúng ở 27/27 ô bảng chính** và 91% lưới mở rộng. Chỉ sai khi tin gần như chắc PEAK *và* mid ≤ 1,97 (ví dụ
  PEAK-only r 13% = 10.726; mid 1,865 = 8.596).
- **≤ 13.000: đúng ở 7/9 ô L0** (và 8/9 ở L2). **Sai ở 80/20 với r 12–13%** (FV 12.710 / 12.226). Tức là 13.000 chỉ là
  vùng mua nếu ta không đặt ≥ 80% vào kịch bản đỉnh rồi về giữa chu kỳ thấp.

## 1. Vì sao FV tâm lên từ 11.031 lên 14.301 (cầu nối, mục 10 `out.txt`)
| Bước (cộng dồn) | Δ đ/cp | FV |
|---|---|---|
| Base cũ (mid 1,97, C 32,5, r 13%, "đỉnh 1 năm") | | 10.878 |
| Đường giá theo lịch (2027 = nửa khoảng cách 2,753→mid) thay "đỉnh 1 năm" | +401 | 11.279 |
| + Tồn kho thành phẩm vượt mức 1.717 t bán H1/27 | **+1.082** | 12.361 |
| + Giá vốn 34 (thay 32,5) | **−1.635** | 10.726 |
| + r 12% | +392 | 11.118 |
| + PEAK trung bình 3 mid (1,865 / 1,97 / 2,075) | 0 | 11.118 |
| + 40% MID-tiếp diễn với mid {2,18; 2,30} | **+3.183** | 14.301 |
- Model cũ thực chất là **định giá PEAK thuần**: cả 3 kịch bản của nó dùng mid ≤ 2,075. Nó **thiếu** (i) phần tồn kho giữ
  hàng và (ii) mọi kịch bản mà mức giữa chu kỳ cao hơn TB 10 năm danh nghĩa. Phản biện của user đúng ở điểm này.
- Nhưng **+3.183 đến từ một lựa chọn đã khai trước, mang tính chủ quan**: ghép MID-tiếp diễn với mid 2,18–2,30. Ai không
  chấp nhận ghép đó thì đọc bảng phụ (mục 3): cùng mid, đường MID chỉ hơn PEAK 1.300–2.550 đ.

## 2. Mức RSS3 giữa chu kỳ — giả định quyết định
| mid (RSS3 $/kg) | Giá bán tr/t | LNST năm (C 34) | FV PEAK / MID (r 12%, L0) |
|---|---|---|---|
| 1,865 (trung vị 10 năm danh nghĩa) | 40,4 | 37,7 | 8.596 / 11.144 |
| 1,970 | 42,6 | 63,7 | 11.118 / 13.365 |
| 2,075 (trung vị 5 năm) | 44,9 | 89,7 | 13.640 / 15.586 |
| 2,180 (TB 2025) | 47,2 | 115,7 | 16.162 / 17.806 |
| 2,300 | 49,8 | 145,4 | 19.044 / 20.344 |
- Mỗi +0,1 $/kg RSS3 giữa chu kỳ ≈ **+2.400 đ/cp**. Đòn bẩy này đến từ giả định giá vốn/t cố định.
- **Kiểm tỷ giá/lạm phát (đã khai, không đổi bảng chính):**
  - USD/VND TB 2016 22.015 → 2026 26.189 (+19%) [FEED]. Model quy RSS3 ra VND theo giá 2025, nên tỷ giá nhất quán với chi phí 2025–26.
  - Trung vị RSS3 10 năm: danh nghĩa 1,865; tính bằng **USD thực 2026 = 2,24**. CPI Mỹ ở đây là số [NỀN/UL], chưa kiểm.
  - ⇒ Lấy trung vị danh nghĩa 10 năm làm "giữa chu kỳ" là **dùng đô-la cũ**: nó thấp hơn mức trung vị thực khoảng 17%.
    Đây là lập luận mạnh nhất ủng hộ mid ≥ 2,07. Đổi lại, chi phí của DRI cũng trôi theo lạm phát LAK/VND, mà model
    giữ cố định. Tôi không có chuỗi giá vốn/t dài để tách hai hiệu ứng này.

## 3. Rủi ro mô hình phát hiện khi đo (đọc trước khi tin bảng)
1. **Hàm LNST dốc gấp 2–2,8 lần lịch sử** (mục 11–12 `out.txt`). Phần này chạy *sau* khi thấy kết quả, **POST-HOC, ngoài PREREG**:
   - Backcast cùng công thức (C 34) cho 2023 ở RSS3 1,576 ra **−33,9 tỷ**, trong khi LNST thật là **74,1** [BQ]. Năm 2024:
     model 139,2, thật 108,8.
   - OLS LNST thật theo RSS3 năm: 2017–25 dốc 125 tỷ/($/kg), 2021–25 dốc 90; model dốc 248. Lịch sử có sản lượng, tỷ
     giá LAK và tồn kho thay đổi; N chỉ 5–9 năm nên hồi quy yếu.
   - Thay hàm lịch sử vào: FV tâm **14.712–15.286**; 80/20 r 13% **13.492–13.833**; 40/60 r 10% **16.981–17.869**.
     Kết luận hướng không đổi, khoảng hẹp lại. Đầu thấp của lưới chính (mid 1,865) có lẽ **quá bi quan**.
2. **Giá vốn/t chưa chốt được:** BCTN 2025 ghi 33,11; 9T/26 là 31,48 (chưa trích thưởng); riêng Q3 36,54 (ít tấn bán).
   Giá vốn ngầm định để công thức tái lập LNST 2025 thật (157,4 [BQ]) chỉ là **29,9**. Lưới 32–36 có thể đang thiên
   bi quan; nguyên nhân (FIN 2025 cao hơn vì khoản vay Dakruco 80 tỷ, SGA khác) chưa tách.
3. Sản lượng V = 14.000 t/năm cố định đến 2054. Không mô hình hoá vườn già hay tái canh sầu riêng.

## 4. Phần lợi nhuận đỉnh còn lại
- **Q4/26** (công thức `model_q3`): Bear 13,7 · Base 49,7 · Bull 90,0 tỷ. Đổi Bear ↔ Bull chỉ ±450 đ/cp.
- **Tồn kho giữ hàng** (giá trị = tấn × (giá bán − thuế × (giá bán − 36,54)), bán H1/27):

  | | X 1.717 t | X 3.370 t ("giữ tới 8.000 t") |
  |---|---|---|
  | PEAK, giá 2027 51,1 tr/t | 83,2 tỷ (1.136 đ/cp) | 163,2 (2.230) |
  | PEAK, giá −30% (35,8, **chạm NRV**) | 61,7 (842) | 121,0 (1.653) |
  | MID, giá 59,6 | 95,1 (1.299) | 186,6 (2.549) |

  - Căn cứ X 1.717 t: chế biến Q3 trừ bán Q3 [SXKD]. Đối chứng bằng giá trị: tồn kho 30/09 năm nay 183,9 so với 124,2 tỷ
    cùng kỳ 2025 [BQ], tức vượt ~59,7 tỷ, khớp cỡ ~1.630 t.
  - NRV chạm khi RSS3 ≈ 1,69 (−39% so Q3/26). Dưới mức đó vẫn còn lá chắn thuế, nên lỗ NRV nhỏ so với tổng FV.
  - Ca **8.000 t chưa xác minh nguồn** [DISPATCH]. Nếu xảy ra thì Q4 base chỉ còn 21,3 tỷ (thay vì 49,7) vì lợi nhuận
    dời sang 2027. Thị trường sẽ đọc Q4 xấu dù giá trị không mất.

## 5. Kiểm chéo độc lập
**(i) PB/PE lịch sử theo pha** (pha = phân vị RSS3 PIT; tháng 10/2026 = PEAK) [BQ `ticker`, `data/dri_peers_px.csv`]:
| Mã | PEAK PB / PE | MID PB / PE | TROUGH PB / PE |
|---|---|---|---|
| DRI | **1,49** / 8,6 | 1,25 / 12,5 | 0,65 / 9,2 |
| TRC | 1,00 / 10,3 | 0,73 / 11,9 | 0,54 / 7,5 |
| DPR | 1,04 / 13,2 | 0,99 / 10,8 | 0,63 / 7,0 |
| PHR | 1,94 / 17,0 | 2,28 / 11,7 | 1,40 / 7,8 |
- PB DRI hiện tại **1,47x** (BVPS 9.971). **Bằng đúng PB trung vị các tháng PEAK của chính DRI** ⇒ giá ngầm định 14.837.
  Ở PB pha MID ⇒ 12.493.
- TRC, mã gần thuần mủ nhất, rẻ hơn hẳn: PB pha PEAK ⇒ 9.938 đ. DRI luôn được định giá cao hơn TRC.
- Lưu ý: PHR/DPR có thu nhập đất KCN, không thuần mủ. Các tháng PEAK (n = 25) chỉ đến từ khoảng 3 đợt (2017, 2021,
  2024–26), nên số đợt độc lập rất ít. Nhóm do tên chỉ định, không lọc universe.
- PE pha MID 12,5x × LNST chuẩn: mid 1,97 ⇒ 13.388; mid 2,18 ⇒ 22.272. Quá rộng để làm neo.

**(ii) Lợi suất cổ tức** [BQ `Dividend_1Y`; lợi suất ở 14.700 = 6,8%]:
- Tỷ lệ chi trả trung vị 2018–25 là **57%**, dao động 23–111% vì lệch thời điểm chi.
- Cổ tức 1.000 đ (73,2 tỷ) bằng **115% LNST chuẩn ở mid 1,97**, 82% ở mid 2,075, 63% ở mid 2,18. ⇒ Mức 1.000 đ **chỉ bền
  nếu mid ≥ ~2,1**.
- FV theo D/r (chỉ tính tiền thực chia, coi LN giữ lại vô giá trị): 2,4k–10,0k. Đây là cận dưới cho cổ đông thiểu số
  *nếu* tiền nằm lại ở Lào.
- LNST riêng công ty mẹ: Q2 55,70 tỷ, Q3 **0,15 tỷ** [GT/BCTC3]. Cổ tức phụ thuộc dòng chuyển LN từ Lào. Tôi không định
  lượng được xác suất bị chặn chuyển tiền.
- Khoảng cách lớn giữa DCF (14k) và D/r (4–8k ở mid 1,97–2,18) cho thấy: **giá trị cho cổ đông thiểu số phụ thuộc việc
  tiền ở Lào có về được không**. Đây là rủi ro tách khỏi giá cao su.

**r so lãi tiền gửi:** Big4 12 tháng online **6,8%** [FEED 26/10]. Mức ~7,4% Mike nêu [DISPATCH] tôi chưa đo. Phần bù
của r 10/12/13% trên tiền gửi là +3,2 / +5,2 / +6,2 điểm %. Với một mã nhỏ, tài sản ở Lào, thanh khoản UPCoM, mức bù
**+3,2 (r 10%) là mỏng**. Tôi coi 12–13% hợp lý hơn, nhưng đây là phán đoán, không phải số đo.

## 6. Chưa chắc / cần skeptic tấn công
1. **Ghép MID ↔ mid 2,18–2,30** tạo ra +3.183 đ. Lựa chọn này đã khai trước nhưng vẫn chủ quan. Trọng số 60/40 cũng là
   phán đoán của Bobby, không phải xác suất đo được.
2. Hàm LNST dốc hơn lịch sử (POST-HOC) và giá vốn/t 29,9–36,5 tuỳ cách đo: hai lỗi này **ngược chiều nhau** ở hai đầu lưới.
3. Ca 8.000 t, vùng mua 21/10, lãi 7,4%: đều chưa có nguồn xác minh. CPI Mỹ là số nền. Quyền đất tới 2054 chưa thấy văn bản.
4. Kiểm chéo PB dựa trên khoảng 3 đợt đỉnh. Kiểm chéo cổ tức phụ thuộc giả định "LN giữ lại ở Lào có giá trị không".
5. Không dùng giá hay lợi suất sau 27/10. Không chỉnh tham số sau khi thấy kết quả; mục 3.1 được dán nhãn POST-HOC.

**Hàm ý (không phải khuyến nghị lệnh):**
- FV −25% của báo cáo Q3 là **kết quả của một lưới chỉ có kịch bản đỉnh**. Khi đưa vào kịch bản giữa chu kỳ cao hơn và
  phần tồn kho, giá 14.700 nằm **quanh FV** ở bộ 60/40. Giá chỉ đắt rõ (+13–20%) nếu đặt ≥ 80% vào kịch bản về giữa chu kỳ thấp.
- Quyết định giảm 50% (user duyệt 12:14) không nằm trong phạm vi job này. Tôi không đề xuất đảo hay giữ; Mike/user
  cân nhắc sau phản biện.

## Nguồn
`../dd_DRI_20261027/` (REPORT_Q3_UPDATE.md, model_q3.py, extract_q3_bctc.md) · `kb/data_registry/market-state/vn_sector_read_rubber_20261027.md`
· BQ `tav2_bq.ticker_financial`, `tav2_bq.ticker` (27/10, snapshot `data/`) · `data/rubber_monthly.csv`, `data/macro_usdvnd.csv`,
`data/deposit_rate_vn_events.csv`. Không tìm thấy file skeptic 21/10 trong KB; dùng tóm tắt trong prompt.
