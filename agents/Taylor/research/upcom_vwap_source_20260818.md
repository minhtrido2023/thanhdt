# UPCOM — nguồn giá bình quân gia quyền THẬT cho G5 (job Taylor_20260817_184109)

> **Kết luận một dòng:** nguồn **ĐÃ CÓ SẴN và đã ở trong client của mình** —
> `DNSEClient.latest_trade(symbol)` → `trades[boardId="G1"].avgPrice` chính là giá bình quân
> gia quyền sở công bố. Đo 509 mã cùng lần, cùng feed: tham chiếu UPCOM khớp
> `round(avgPrice, tick)` **108/114 = 94,7%** (so với 43/114 = 37,7% nếu đứng trên giá đóng
> cửa). Đối chứng nội bộ giữ nguyên: HOSE 289/289 và HNX 106/106 vẫn khớp CLOSE, và chỉ
> 19,0% / 42,5% khớp avgPrice ⇒ đây không phải hiệu ứng của làm tròn.
>
> **Nhưng chưa wire được ngay:** endpoint chỉ giữ phiên GẦN NHẤT, không có API lịch sử — xem §4.

Bổ sung cho `gdkhq_exchange_rounding_20260818.md` (job Taylor_20260817_175306), file đó chứng
minh tham chiếu UPCOM **không phải** giá đóng cửa. File này trả lời câu còn lại: *vậy nó là gì,
và ta lấy được số đó từ đâu.*

## 1. Trường dữ liệu — có sẵn trong `dnse_api.py`, không cần nguồn mới

`GET /price/{symbol}/trades/latest` (`DNSEClient.latest_trade`, `dnse_api.py:246`) trả về một
bản ghi **cho mỗi bảng giao dịch (`boardId`)**, không phải một bản ghi cho mỗi mã:

```
VGT 2026-08-17, boardId "G1" (khớp lệnh liên tục):
  matchPrice 12    matchQtty 130    avgPrice 11.944    totalVolumeTraded 51600
  grossTradeAmount 6.16315   highestPrice 12.4   lowestPrice 11.8   openPrice 12.3
  time "2026-08-17 14:59:15.194"
```

`avgPrice` là **giá bình quân gia quyền của phiên trên bảng đó**, đơn vị nghìn đồng như mọi
trường giá khác của DNSE. Kiểm chứng nội bộ trên chính bản ghi: `avgPrice × totalVolumeTraded`
= `grossTradeAmount` (VGT: 11,944 × 51.600 = 616.310 nghìn đ; grossTradeAmount 6,16315 ở đơn vị
100 triệu đ = 616.315 nghìn đ). ⇒ **KHÔNG phải cột dẫn xuất** — khác hẳn `tav2_bq.ticker.
Trading_Value` (= `Price × Volume` từng dòng một, tính VWAP từ nó là phép lặp vòng, §5 file kia).

**Phải lọc `boardId == "G1"`.** UPCOM trả 5 bảng (G1, G4, G7, T1, T4) — G4/G7/T-* là thoả thuận
/lô lẻ, `avgPrice` của chúng khác hẳn và không phải thứ sở dùng làm tham chiếu (VGT G4:
`avgPrice` 12,143 trên vỏn vẹn 451 cp). Lấy bừa phần tử `[0]` là sai — thứ tự bảng KHÔNG ổn định
giữa các mã (VGT trả G1 trước, SCL trả G4 trước).

## 2. Thí nghiệm — cùng thiết kế, cùng mẫu, cùng feed với job trước

Cùng 509 mã của `upcom_ref_basis_probe_20260818.csv` (đã loại 31 mã có sự kiện quyền trong cửa
sổ + mọi mã không đọc được sàn), chạy **01:5x ICT 2026-08-18**, ngoài giờ giao dịch: `secdef`
đã lật sang phiên 08-18 nên `basicPrice` = tham chiếu 08-18, còn `latest_trade` vẫn giữ nguyên
phiên 08-17. Hai vế cùng nói về đúng một cặp phiên (đúng logic cổng G6).

    H0 (đóng cửa)   : ref(T) == close(T−1)
    H2 (bình quân)  : ref(T) == round(avgPrice_G1(T−1), bước giá của sàn)

| Sàn | n | ref == close | ref == round(avgPrice) | trong ±1 tick của avgPrice |
|---|---:|---:|---:|---:|
| **HOSE** | 289 | **289 (100,0%)** | 55 (19,0%) | 119 (41,2%) |
| **HNX** | 106 | **106 (100,0%)** | 45 (42,5%) | 81 (76,4%) |
| **UPCOM** | 114 | 43 (37,7%) | **108 (94,7%)** | **108 (94,7%)** |

**Đối chứng nội bộ là thứ khoá kết luận.** Nếu `avgPrice` chỉ là một con số "gần giá" mà quy
tắc làm tròn tự khớp được, HOSE/HNX cũng phải khớp nó ở tỉ lệ cao — thực tế 19,0%/42,5%. Và
nếu feed hay cơ sở giá của ta lệch hệ quy chiếu thì HOSE/HNX đã không khớp close 100%. Hai chiều
đều đóng ⇒ khác biệt nằm ở **luật của sở**, không ở đường dữ liệu.

Trên UPCOM, phân bố sai số của H2 là **P50 = P90 = 0 tick**: không có đuôi. Trong khi H0 có
P50 = 1, P90 = 5, max = 16 tick. Đây không phải "H2 nhỉnh hơn" — H0 sai có hệ thống, H2 đúng
hoặc trật hẳn.

### 2.1 Hai ca thật đã biết, nay giải thích trọn vẹn

| Mã | close 08-17 | avgPrice G1 | sự kiện | ref 08-18 thật | H0 (close) | H2 (avgPrice) |
|---|---:|---:|---|---:|---:|---:|
| **VGT** | 12.000 | 11.944 | DIV 300đ | **11.600** | 11.700 ✗ (−100) | (11.944−300)=11.644 → **11.600** ✓ |
| **SCL** | 24.500 | 24.112 | không | **24.100** | 24.500 ✗ (−400) | **24.100** ✓ |

VGT là ca quan trọng nhất: nó cho thấy công thức GDKHQ **không đổi** — chỉ **cơ sở giá** đổi.
Thay `P_cum` từ close sang avgPrice là khớp tới từng đồng, cùng một phép trừ cổ tức.

## 3. Sáu mã UPCOM H2 KHÔNG giải thích được (5,3%) — công bố nguyên trạng

| Mã | ref | close | avgPrice | lệch vs avg | KL G1 |
|---|---:|---:|---:|---:|---:|
| VNE | 2.200 | 2.200 | 2.959 | −8 tick | 90.300 |
| MZG | 12.900 | 12.000 | 12.095 | +8 tick | 34.040 |
| VBB | 13.500 | 12.900 | 12.882 | +6 tick | 1.290 |
| SDA | 1.800 | 1.800 | 1.402 | +4 tick | 77.130 |
| AAV | 6.400 | 6.200 | 6.750 | −4 tick | 57.920 |
| DDG | 1.000 | 1.100 | 799 | +2 tick | 246.650 |

Chưa có giả thuyết đứng vững cho nhóm này (4/6 là mã dưới 3.000đ hoặc thanh khoản rất mỏng —
VBB đúng 1.290cp cả phiên). **MZG và VBB chính là 2 ngoại lệ mà job trước đã ghi** (ref nằm
NGOÀI dải [Low, High] phiên trước) ⇒ ít nhất một cơ chế nữa còn chưa biết trên UPCOM, và H2
không xoá được nó. **Đây là lý do độc lập thứ hai để G5 giữ decline-to-speak** cho tới khi
nhóm này có lời giải: 5,3% không phải sai số đo, đủ để một cổng chặn lệnh vấp phải.

## 4. Vì sao BIẾT nguồn rồi vẫn CHƯA wire được — ràng buộc thời điểm

`latest_trade` là endpoint **SỐNG**, chỉ giữ **phiên gần nhất**. Hệ quả cứng:

- Chạy **trước giờ mở cửa** ngày GDKHQ ⇒ trả đúng phiên cum → dùng được.
- Chạy **trong phiên** ngày GDKHQ ⇒ trả **phiên HÔM NAY đang chạy**, `avgPrice` là bình quân
  dở dang của chính phiên GDKHQ. Đem đối soát sẽ ra kết luận rác — đúng họ lỗi mà cổng **G6**
  sinh ra để bắt, chỉ khác chiều thời gian.
- **Không có endpoint VWAP lịch sử.** Đã kiểm: `GET /price/ohlc` (`resolution=1D`) trả đúng
  `t/o/h/l/c/v` — **không có trường giá trị giao dịch** nên không dựng lại VWAP được.
  `tav2_bq.ticker.Trading_Value` đã bị loại (§1). `close_price` chỉ trả `closePrice`.

⇒ Muốn G5 đứng trên VWAP cho UPCOM thì phải **tự dựng lịch sử**: một job chụp
`latest_trade().avgPrice` (board G1) sau giờ đóng cửa mỗi phiên và ghi lại — không có đường tắt
đọc ngược. Đó là một nguồn dữ liệu MỚI phải qua `data_registry` + owner (Winston, data-ops), nên
nằm ngoài phạm vi job này.

## 5. Khuyến nghị

1. **Giữ decline-to-speak** (đã wire trong job này). Hai lý do độc lập: (a) chưa có lịch sử
   VWAP để G5 chạy đúng ở mọi khung giờ; (b) 5,3% mã UPCOM (§3) vẫn chưa giải thích được kể cả
   khi có VWAP.
2. **Nếu muốn bật G5 cho UPCOM sau này** — thứ tự bắt buộc:
   a. Winston thêm nguồn `dnse latest_trade.avgPrice (board G1)` vào `data_registry` +
      dựng job chụp EOD, tích ít nhất vài tuần lịch sử.
   b. Lặp lại probe này ở **≥3 phiên khác nhau** (hiện mới 1 phiên) — rẻ, chỉ là chạy lại.
   c. Giải thích được nhóm 6 mã §3, hoặc khoanh chúng bằng một điều kiện tường minh
      (không phải nới dung sai — xem phương án (B) đã bị bác ở job trước).
   d. quant-skeptic + user duyệt, vì đây là cổng chặn lệnh chạm tiền thật.
3. **Không nới dung sai G5 cho UPCOM** trong mọi trường hợp — kết luận này không đổi.

## 6. Hạn chế phải công bố cùng số

1. **Một phiên duy nhất** (ref 08-18 vs phiên 08-17), y như job trước. Kết luận về *luật* nên
   ổn định, nhưng chưa lặp.
2. **Chưa chứng minh `avgPrice` là bình quân gia quyền theo KHỐI LƯỢNG** một cách trực tiếp —
   mới chứng minh nó nhất quán nội bộ (`avgPrice × vol == grossTradeAmount`) và nó *dự đoán
   đúng* tham chiếu ở 94,7%. Phân biệt với các dạng bình quân khác cần dữ liệu khớp lệnh trong
   phiên.
3. **Không có mã ETF trong mẫu** (nhánh tick 10đ của `tick_size` chưa được kiểm).
4. Quy tắc làm tròn đo được là **nearest-tick**; chưa phân biệt được nearest với floor/ceiling
   ở những mã mà avgPrice tình cờ rơi gần mép — đúng giới hạn mà job trước đã nêu.

---
**Artifact:** `upcom_vwap_source_probe_20260818.csv` (509 dòng, sinh bởi probe chỉ-đọc trong
job này) · nguồn mẫu: `upcom_ref_basis_probe_20260818.csv` (job Taylor_20260817_175306).
