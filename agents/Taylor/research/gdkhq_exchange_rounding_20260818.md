# GDKHQ — luật làm tròn & CƠ SỞ GIÁ theo sàn (job Taylor_20260817_175306, Phần B)

> **Kết luận một dòng:** làm tròn theo sàn **đã đúng và đã wire sẵn** — thứ sai trên UPCOM
> không phải LÀM TRÒN mà là **CƠ SỞ GIÁ**. Tham chiếu phiên của UPCOM **không phải giá đóng
> cửa** phiên trước (đo 509 mã: HOSE 289/289 và HNX 106/106 khớp TUYỆT ĐỐI, UPCOM lệch
> 62,3%). Hệ quả: **G5 đứng trên `ticker.Price` là KHÔNG HỢP LỆ trên UPCOM** — dung sai ±1
> tick của nó bị vượt ở **1/3 số mã UPCOM** trong một phiên THƯỜNG.

## 0. Tiền đề trong dispatch cần đính chính (trước khi đọc tiếp)

Dispatch mô tả G5 là "P_cum / (1 + stock_ratio) → **ceiling** đến tick gần nhất". Hai điểm:

1. **Code không làm tròn gì cả.** `expected_reference_price()` cố ý trả số CHƯA làm tròn và
   `check_ref_vs_events()` biến quy ước làm tròn thành **dung sai ±1 tick**. Docstring nói rõ
   lý do: quy ước làm tròn của sở là thứ ta không kiểm chứng độc lập được, nên đừng biến nó
   thành một giả định im lặng nằm GIỮA hai con số đang đối soát. Đây là thiết kế đúng, không
   phải thiếu sót.
2. **Chính ví dụ trong dispatch bác bỏ chữ "ceiling".** BID: 38.250/1,068433 = 35.800,1;
   `ceiling` theo tick 50đ phải ra **35.850**, trong khi tham chiếu thật là **35.800**. Số
   liệu khớp với *nearest* hoặc *floor*, không khớp *ceiling*. Đừng wire chữ "ceiling" vào code.

## 1. Việc 3 của dispatch ("thêm exchange-aware rounding") — ĐÃ CÓ SẴN, không cần làm

Chuỗi truyền sàn đã thông suốt từ trước job này:

`resolve_reference()` đọc `exchange` từ quote sống → `check_ref_vs_events(exchange=…)` →
`expected_reference_price(exchange=…)` → `vn_market.tick_size(px, symbol, exchange)`.

`tick_size()` đã mã hoá đúng quy chế:

| Sàn | Bước giá | Xác nhận thực nghiệm trong job này |
|---|---|---|
| HOSE | <10.000đ → 10đ · 10.000–<50.000đ → 50đ · ≥50.000đ → 100đ | 289/289 mã ref khớp close tuyệt đối |
| HOSE ETF (`E1*`,`FUE*`) | 10đ mọi mức giá | không có mã ETF trong mẫu |
| HNX | **100đ mọi mức giá** | 106/106 khớp tuyệt đối |
| UPCOM | **100đ mọi mức giá** | 114/114 ref là bội số 100đ (mọi `dev_ticks` đo được đều là số nguyên) |

⇒ **Không có thay đổi rounding nào cần làm.** Việc 3 của dispatch dựa trên tiền đề rằng
rounding chưa exchange-aware; tiền đề đó sai.

## 2. Thí nghiệm quyết định — cơ sở giá tham chiếu UPCOM

### 2.1 Vì sao KHÔNG test trên ngày GDKHQ

Trên ngày GDKHQ, cỡ mẫu = số sự kiện (n=2: VGT lệch −100đ, QNS khớp) và bước giá 100đ của
UPCOM **nuốt mọi chênh lệch <50đ** — QNS khớp tuyệt đối là *không phân biệt được* hai giả
thuyết, không phải bằng chứng ủng hộ giả thuyết "đóng cửa".

Luật tham chiếu áp cho **MỌI phiên**, không riêng ngày có sự kiện. Nên test trên ngày THƯỜNG:
mỗi mã đang niêm yết là một quan sát, và **HOSE/HNX làm đối chứng trong cùng lần đo, cùng feed**.

    H0 (đóng cửa)  : ref(T) == close(T−1) trên MỌI sàn
    H1 (bình quân) : ref == close trên HOSE/HNX, LỆCH ở tỉ lệ đáng kể mã UPCOM

Đối chứng nội bộ là thứ khoá lại kết luận: nếu **cơ sở giá của ta** hay **feed** sai hệ quy
chiếu thì HOSE/HNX cũng phải lệch. HOSE/HNX khớp tuyệt đối mà UPCOM lệch ⇒ khác biệt nằm ở
**luật của sở**, không nằm ở đường dữ liệu.

### 2.2 Thiết lập

Script: `upcom_ref_basis_probe_20260818.py` (CHỈ ĐỌC — `secdef` + 2 truy vấn BQ, không đặt
lệnh, không ghi state production). CSV: `upcom_ref_basis_probe_20260818.csv`.

Chạy **01:04 ICT 2026-08-18**, TRƯỚC giờ mở cửa: bản ghi `secdef` đã lật sang phiên 08-18 từ
~19:23 ngày 08-17, nên `basicPrice` đọc lúc đó **là tham chiếu phiên 08-18**, và phiên liền
trước là 08-17 — đã có trong BQ. (Đúng logic cổng G6; chạy khung giờ khác thì cặp phiên đổi.)

Loại khỏi mẫu 31 mã có `exright_date` trong cửa sổ 08-17→08-21 (tham chiếu bị điều chỉnh hợp
lệ) và mọi mã không đọc được sàn (fail-closed, không đoán sàn).

### 2.3 Kết quả — n = 509 mã

| Sàn | n | khớp | lệch | % lệch | |lệch| TB | max |
|---|---:|---:|---:|---:|---:|---:|
| **HOSE** | 289 | **289** | **0** | **0,0%** | 0đ | **0,00 tick** |
| **HNX** | 106 | **106** | **0** | **0,0%** | 0đ | **0,00 tick** |
| **UPCOM** | 114 | 43 | **71** | **62,3%** | 269đ | **16,00 tick** |

**H0 bị BÁC BỎ trên UPCOM, được XÁC NHẬN trên HOSE/HNX.** Không một mã HOSE/HNX nào trong 395
mã lệch dù chỉ 1đ.

Ba kiểm chứng phụ, đều ủng hộ H1 (tham chiếu = giá bình quân gia quyền phiên trước):

1. **Điều kiện CẦN của một giá bình quân:** phải nằm trong `[Low, High]` của chính phiên đó.
   **69/71 mã lệch thoả** (nới 1 tick cho làm tròn). Hai ngoại lệ **MZG** (ref 12.900 ngoài
   [11.900; 12.350]) và **VBB** (ref 13.500 ngoài [12.800; 12.900]) — với hai mã này ref
   KHÔNG THỂ là bình quân của phiên T−1, cần cơ chế khác giải thích; **chưa điều tra**.
2. **Lệch hai chiều:** 24 dương / 47 âm. Bình quân gia quyền nằm hai phía giá đóng cửa —
   đúng chữ ký của H1. (Một cơ chế "sở tự hạ tham chiếu" sẽ cho lệch một chiều tuyệt đối.)
3. **Mọi ref UPCOM đều là bội số 100đ** ⇒ xác nhận độc lập bước giá UPCOM = 100đ phẳng.

### 2.4 Ca VGT được giải thích trọn vẹn

VGT 08-17: Open 12.300 / High 12.400 / Low 11.800 / **Close 12.000**; DIV 300đ, GDKHQ 08-18.
Công thức trên cơ sở đóng cửa: 12.000 − 300 = **11.700**. Tham chiếu sống: **11.600**.
Cơ sở hàm ý ≈ **11.900**, nằm gọn trong dải 08-17 — nhất quán với H1.

⇒ Lệch −100đ của VGT **không phải sai làm tròn** (11.700 vốn đã nằm trên bước giá) mà là
**sai cơ sở giá**. Giả thuyết ghi trong `gdkhq_g5_false_fail_20260818.md` §4.2 nay **được xác
nhận bằng mẫu độc lập, n=509, có đối chứng** — không còn là suy đoán n=2.

## 3. Hệ quả PHẢI xử lý: G5 hiện KHÔNG HỢP LỆ trên UPCOM

`P_cum` của G5 = `tav2_bq.ticker.Price` = **giá đóng cửa**. Trên UPCOM đó là sai cơ sở. Độ lớn
sai số đo trên chính mẫu 114 mã UPCOM, quy ra bội số dung sai ±1 tick của G5:

| Ngưỡng | Số mã | Tỉ lệ |
|---|---:|---:|
| lệch > 0 tick | 71/114 | 62,3% |
| **lệch > 1 tick (VƯỢT dung sai G5)** | **38/114** | **33,3%** |
| lệch > 2 tick | 22/114 | 19,3% |
| lệch > 5 tick | 9/114 | 7,9% |
| Phân vị | P50 = 1 · P75 = 2 · P90 = 5 · P95 = 6 · max = 16 tick |

**Đọc thẳng: nếu một mã UPCOM có sự kiện quyền, G5 sẽ CHẶN OAN với xác suất ~1/3** — không
phải vì công thức sai mà vì hai vế đứng trên hai cơ sở giá khác nhau.

**Lần shadow PASS 08-18 vì thế là bằng chứng YẾU HƠN vẻ ngoài của nó.** VGT lệch đúng 1 tick
= **ĐÚNG MÉP** dung sai; đó là may mắn ở rìa, không phải gate được kiểm chứng. QNS khớp tuyệt
đối cũng không nói được gì (§2.1). ⇒ **Đừng coi "2/4 mã UPCOM đã PASS" là G5 đã hợp lệ trên
UPCOM.**

**Việc này chạm sổ thật, không phải học thuật:** book đang giao dịch mã UPCOM. Đo trong chính
mẫu này — **SCL lệch −400đ (4 tick)**, MSR −600đ (6 tick), OIL −200đ (2 tick); DRI tình cờ
khớp 0đ. TV1 (UPCOM, sleeve discretionary) không có trong mẫu phiên này.

## 4. Đề xuất — và vì sao job này DỪNG ở đề xuất

**KHÔNG wire gì trong job này.** Sửa cơ sở giá của một cổng chặn lệnh, cho cả một sàn, là thay
đổi production chạm tiền ⇒ theo chuẩn fleet phải qua **quant-skeptic + user duyệt**. Job này
giao BẰNG CHỨNG, không giao thay đổi.

Ba phương án, kèm nhược điểm thật:

- **(A) G5 KHÔNG phát biểu trên UPCOM** (tiền lệ có sẵn: G4 khi thiếu `marketPrice`, G6 khi
  thiếu dấu thời gian). Ghi rõ `gate="G5_NA_UPCOM"` + lý do, để G1/G2/G3/G4/G6 gánh, và
  **công bố mức bảo đảm thấp hơn** cho mã UPCOM. Trung thực, không chặn oan; đổi lại mất
  đúng lớp đối soát chéo mạnh nhất trên sàn có thanh khoản mỏng nhất.
- **(B) Nới dung sai riêng cho UPCOM.** Muốn phủ P95 phải nới tới **6 tick (600đ)** — với mã
  UPCOM giá thấp đó là vài phần trăm, cổng gần như mất hết khả năng bắt lỗi thật. **Không
  khuyến nghị**; nới đến mức vô dụng còn tệ hơn tắt hẳn vì tạo cảm giác an toàn giả.
- **(C) Lấy đúng cơ sở giá bình quân cho UPCOM.** Đúng bản chất nhất, nhưng **hiện KHÔNG có
  nguồn**: xem §5 — `Trading_Value` của BQ là số DẪN XUẤT, không tính ra VWAP được.

**Khuyến nghị: (A)**, kèm điều tra tiếp nguồn VWAP thật cho (C). (A) giữ nguyên tinh thần
fail-safe của D1-D3: thà nói "cổng này không phát biểu được trên sàn này" còn hơn để một cổng
sai cơ sở vừa chặn oan 1/3 vừa PASS nhầm ở phần còn lại.

## 5. Phát hiện phụ về dữ liệu (đáng vào data_registry)

1. **`tav2_bq.ticker*.Trading_Value` là cột DẪN XUẤT, không phải giá trị giao dịch thật.**
   Đo trên toàn bộ mẫu: `Trading_Value / Volume == Price` **từng dòng một**, không sai số.
   ⇒ **Không thể dùng nó để tính VWAP** (sẽ ra đúng `Price`, một phép lặp vòng trông như đã
   xác minh). Đây chính là lý do phương án (C) chưa chạy được.
2. **`bq query` mặc định chỉ in 100 dòng và KHÔNG báo là đã cắt.** Lần chạy đầu của probe ăn
   đúng bẫy này: `LIMIT 700` trả 100 dòng, universe tụt còn 95 mã với vỏn vẹn 4 UPCOM, và vì
   **trùng khít con số lần chạy trước** nên trông y như "đã lấy hết". Bắt được là nhờ đối
   chiếu `COUNT(*)` (773 dòng cho 08-17). **Luôn truyền `--max_rows`.** Nếu không bắt, kết
   luận UPCOM đã đứng trên n=4 thay vì n=114.
3. `ticker_1m` là ảnh chụp ĐÃ LỌC (772 dòng 08-17, nhưng chỉ 4 mã UPCOM sau lọc thanh khoản);
   `ticker` mới đủ phủ để nói chuyện theo sàn.

## 6. Hạn chế phải công bố cùng số

1. **Một phiên duy nhất** (tham chiếu 08-18 vs phiên 08-17). Kết luận về *luật* nên ổn định
   theo thời gian, nhưng chưa lặp lại ở phiên khác. Rẻ để lặp: chạy lại probe bất kỳ ngày nào.
2. **Chưa chứng minh trực tiếp "bình quân GIA QUYỀN"** — mới chứng minh (a) *không phải* giá
   đóng cửa, (b) *nhất quán* với một giá bình quân (nằm trong dải, hai chiều). Phân biệt
   bình quân gia quyền theo KL với các dạng bình quân khác cần dữ liệu khớp lệnh trong phiên
   mà ta chưa có (§5.1).
3. **MZG và VBB chưa giải thích được** — ref nằm NGOÀI dải phiên trước. 2/71, không lật kết
   luận chung, nhưng là dấu hiệu còn ít nhất một cơ chế nữa chưa biết trên UPCOM.
4. **Không có mã ETF trong mẫu** ⇒ nhánh tick 10đ của `tick_size` cho `E1*`/`FUE*` không được
   kiểm trong job này.
5. VIX (GDKHQ 08-20) là **HOSE** ⇒ **không dính** vấn đề này. Phần B không chặn việc chạy
   shadow VIX 08-20 trong phiên.
