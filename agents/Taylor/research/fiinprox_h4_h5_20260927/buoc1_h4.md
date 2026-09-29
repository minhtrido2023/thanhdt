# BƯỚC 1 — H4: chỉ báo khối ngoại bán ròng KHỚP LỆNH vá điểm mù 2018

> Job `Taylor_20260926_164143` · PAPER-ONLY · prereg: `PREREG.md` §1 (viết TRƯỚC khi chạy)
> Artifact: `h4_indicator.py`, `h4_checks.py`, `build_gtgd.py`, `h4_series.csv`,
> `h4_summary.csv`, `h4_events.json`, `gtgd_daily.csv`

## KẾT LUẬN: **NO-GO** — cả 5/5 cấu hình đã prereg đều trượt tiêu chí quyết định (b)

Chỉ báo **bắt được 2018 rất tốt** (tiêu chí a: PASS MẠNH ở cả 5 cấu hình, có cấu hình fire
**trước đỉnh VNINDEX 09/04/2018**). Nhưng nó **cũng fire 11-15 lần nữa** trong 2014-2017 và
2019-2026, trong đó **6-10 lần là báo động giả** — so với trần prereg là **≤2**. Trượt xa,
không phải sát ngưỡng.

Con số đóng đinh: **tỷ lệ nền** P(VNINDEX giảm ≥10% trong 126 phiên tới) trên 3.069 phiên
2014-2026 = **33,5%**. Precision của chỉ báo = **33-54%**. Cấu hình tốt nhất (B@2,0: 7/13 đúng
= 54%) cho p một phía **0,106**, sau hiệu chỉnh 5 cấu hình (Šidák) = **0,429**. Tức là: chỉ báo
này **không phân biệt được với việc bấm chuông ngẫu nhiên** ở tần suất đó.

**Điểm mù 2018 vẫn còn.** Dữ liệu mới GIẢI QUYẾT được vấn đề *đo lường* mà
`production_mechanism_2009_2018_20260830.md` §B.1 nêu (nay đã có chuỗi khớp lệnh tách thoả thuận
từ 2014) — nhưng câu trả lời là chỉ báo đó **không tồn tại như một cổng dùng được**, chứ không
phải "chưa đo được". Đây là tiến bộ: một câu hỏi mở đã đóng bằng số, theo hướng phủ định.

---

## 0. Pre-flight (Step 0 quant-research) — NO-GO trước cả khi bắt đầu

```
rnd_preflight_power.py --sharpe-ann 0.30 --obs-per-year 252 --n-available 13
                       --n-trials 4 --n-rule per-episode --max-history-years 12.7
→ NO-GO. DSR(N=13 episode) = 0,1723. Cần 20.370 quan sát = 80,8 năm.
  Trần dữ liệu 12,7 năm ⇒ DSR tối đa 0,5068 — vẫn dưới 0,95.
  Sharpe tối thiểu phát hiện được = 13,4 (×44,7 effect giả định).
```

Nghĩa là: **H4 không bao giờ chứng minh được bằng thống kê trên dữ liệu VN.** Vẫn chạy vì
dispatch đặt tiêu chí quyết định là **số báo động giả** (chẩn đoán/nhân quả), không phải p-value.
Kết quả dưới đây phải đọc như **chẩn đoán**, và nó tình cờ đủ dứt khoát để không cần thống kê.

## 1. Thiết lập (đúng như prereg, không lệch)

| Thành phần | Chọn |
|---|---|
| Tử số | `foreign_matched_net_bn` (E) — **tách thoả thuận theo cấu tạo**, lô Vinhomes 2018-05-18 +28.571 tỷ nằm ở cột `foreign_deal_net_bn`, không vào tử số |
| Mẫu số | GTGD ngày = `Σ COALESCE(Price,Close)×Volume` trên bảng `ticker` **ĐẦY ĐỦ** (3.424 phiên 2013-2026), lấy **median 60 phiên** (bền với ngày thoả thuận) |
| **KHÔNG** dùng | `ticker_prune` làm mẫu số — §9b look-ahead universe |
| Nhãn episode | Bobby `vn_macro_regime_history_2009_2018_phases.md`, dùng NGUYÊN |
| Loại bỏ | `provisional` 2026-09-03→09-14; ô thiếu là THIẾU không phải 0 (min 15/20 ô mới tính) |
| Debounce | fire cách <60 ngày lịch = 1 sự kiện |
| Báo động giả | fire mà VNINDEX **không** giảm ≥10% trong 126 phiên kế tiếp |
| Thực thi | tín hiệu đóng cửa t, cap từ mở cửa t+1 (không nhìn trước) |

5 cấu hình, khai trước, không thêm: `A20@0,02` · `A20@0,03` · `A60@0,015` · `B@2,0` · `B@2,5`.

## 2. (a) Có bắt được 2018 không — **PASS MẠNH, 5/5**

| Cấu hình | Fire đầu tiên 2018 | vs đỉnh 09/04/2018 | Sụt 126 phiên sau |
|---|---|---|---|
| B@2,0 | **2018-03-02** | **trước đỉnh 38 ngày** | −20,3% |
| A20@0,02 | **2018-03-16** | **trước đỉnh 24 ngày** | −22,3% |
| B@2,5 | **2018-03-16** | **trước đỉnh 24 ngày** | −22,3% |
| A60@0,015 | 2018-05-02 | sau đỉnh 23 ngày | −13,2% |
| A20@0,03 | 2018-05-04 | sau đỉnh 25 ngày | −13,5% |

Đây là kết quả THẬT và đáng ghi nhận: chuỗi khớp lệnh tách thoả thuận **có** nhìn thấy cú rút
vốn 2018, và nhìn thấy **trước** đỉnh — đúng như Bobby mô tả pha 2B (siết USD toàn cầu, DXY
rally từ giữa 04, UST 10Y vượt 3% ngày 24/04). Nếu chỉ hỏi câu (a) thì đây là "thành công".
Nhưng (a) chưa bao giờ là câu hỏi quyết định.

## 3. (b) QUYẾT ĐỊNH — báo động giả ngoài 2018: **trượt 5/5**

| Cấu hình | Sự kiện (tổng) | Ngoài 2018 | **Báo động GIẢ** | Trần prereg | Precision | vs nền 33,5% |
|---|---|---|---|---|---|---|
| A20@0,02 | 15 | 14 | **10** | ≤2 | 33% | p=0,601 |
| A20@0,03 | 16 | 15 | **9** | ≤2 | 40% | p=0,387 |
| A60@0,015 | 12 | 11 | **7** | ≤2 | 42% | p=0,373 |
| B@2,0 | 13 | 12 | **6** | ≤2 | **54%** | p=0,106 · **Šidák 0,429** |
| B@2,5 | 13 | 12 | **7** | ≤2 | 46% | p=0,245 |

Trần thứ hai của prereg ("tổng sự kiện ngoài 2018 ≤6") cũng trượt: thực tế **11-15**.

**Vì sao con số 33,5% là con số quan trọng nhất trong báo cáo này.** Thị trường VN giảm ≥10%
trong 6 tháng bất kỳ ở **1/3 số phiên**. Một chỉ báo "đúng" 33-54% trên 12-16 sự kiện đang làm
gần đúng những gì một cái đồng hồ hỏng làm. A20@0,02 precision **33% = đúng bằng tỷ lệ nền**,
tức **không có kỹ năng nào cả**.

### Duty cycle — cái làm hỏng nó như một CAP phòng thủ

Áp hysteresis đúng prereg (bật ở −θ, tắt khi hồi trên −θ/2):

| Cấu hình | % thời gian CAP BẬT | VNINDEX ann. khi BẬT | khi TẮT |
|---|---|---|---|
| A20@0,02 | 34,8% | +6,99% | +15,27% |
| A20@0,03 | 21,8% | +11,04% | +12,83% |
| A60@0,015 | **43,7%** | **+16,79%** | **+9,29%** ← **ĐẢO DẤU** |
| B@2,0 | 39,9% | +11,27% | +13,23% |
| B@2,5 | 34,2% | **+15,11%** | **+11,12%** ← **ĐẢO DẤU** |

Một cổng phòng thủ bật **22-44% thời gian** đã là quá đắt ngay cả khi đúng hướng. Nhưng **2/5
cấu hình ĐẢO DẤU** — thị trường tăng NHANH HƠN trong lúc chỉ báo đang kêu bán. Không có dạng
dose-response (§10 quant-research): siết chặt ngưỡng không cải thiện đơn điệu thứ gì.

### (1.8) Có dư thừa so với cap hiện có không? — Không, và điều đó KHÔNG cứu được nó

Cap DT5G hiện tại (DT5G state < v3.4b base) active 624/3.165 phiên.

| Cấu hình | H4 bật | Trùng cap cũ | **H4 MỚI** | % H4-on đã được cap cũ phủ |
|---|---|---|---|---|
| A20@0,02 | 1.101 | 153 | 948 | 13,9% |
| A60@0,015 | 1.382 | 250 | 1.132 | 18,1% |
| B@2,0 | 1.264 | 235 | 1.029 | 18,6% |

82-86% ngày H4 bật là **mới** so với cap SBV-refi + VIX/SPX. Nhưng "mới" ở đây không phải giá
trị gia tăng — đó là **~1.000 phiên hạ trần thêm mà phần lớn không có sụt giảm nào theo sau**.
Prereg §1.8 hỏi "nếu trùng nhiều thì dư thừa ⇒ NO-GO"; thực tế là ngược lại và vẫn NO-GO, vì
lý do khác: nó không dư thừa, nó chỉ sai.

## 4. (c) Kiểm tra phụ 2009-2013 (gross, file F) — **không kết luận được, vì lý do cơ học**

Chuỗi F bắt đầu **2009-06-01**, mà z-score cần warm-up SD 250 phiên (min 180). ⇒ z20 là **NaN
suốt 2009**. Cả pha 1B (rally 03-08/2009) lẫn pha 1C (điểm gãy 09-12/2009, mốc SBV 25/11) đều
**nằm trọn trong vùng warm-up** — không đánh giá được, không phải "không fire".

Đây là một hạn chế cứng: **bộ F không lấp được 2009** cho bất kỳ chỉ báo chuẩn-hoá-theo-lịch-sử
nào. Kỳ vọng ở đề xuất §H4 ("lấp luôn 2009 rally bị bỏ lỡ") **không thành hiện thực**.

Phần đo được (2010-2013, gross gồm thoả thuận ⇒ chỉ mô tả): z20 ≤ −2,0 cho 3 sự kiện
(2011-10, 2011-12→2012-02, 2013-06/07); z20 ≤ −2,5 cho 2 (2012-01/02, 2013-06/07). Không so
sánh trực tiếp được với phần 2014+ vì khác định nghĩa (gross vs khớp lệnh).

## 5. Overlay NAV R3 — **KHÔNG chạy, đúng prereg §1.7**

Prereg quy định overlay chỉ chạy nếu (a) VÀ (b) đều PASS. (b) trượt 5/5 ⇒ không chạy. Không tiêu
compute vào một cấu hình đã bị loại; và chạy overlay sau khi biết nó trượt chính là cách một kết
quả bị "cứu" bằng chọn lọc hậu nghiệm.

**Ước lượng bằng lý lẽ** (không phải kết quả đo): cap hạ trần xuống ≤NEUTRAL trong 22-44% thời
gian, mà VNINDEX trong các khoảng đó tăng trung bình 7-17%/năm ⇒ ΔCAGR gần chắc chắn **âm**, khả
năng âm đáng kể chứ không phải "âm nhẹ". Nhãn rõ ràng: đây là suy luận, chưa đo.

## 6. N thật là bao nhiêu

- **N = 12-16 sự kiện độc lập** tuỳ cấu hình (không phải 462-1.047 phiên fire, không phải 3.165
  phiên dữ liệu). Debounce 60 ngày lịch.
- Trong đó **đúng 1 sự kiện là 2018** — chính là sự kiện mà giả thuyết được xây để bắt.
- Episode regime độc lập trong toàn cửa sổ: ~13 (DT5G 2014+). Đây là lý do pre-flight phán NO-GO.
- Với N=13 và tỷ lệ nền 33,5%, để đạt p<0,05 một phía cần **≥9/13 đúng**. Cấu hình tốt nhất đạt
  7/13. Ngay cả khi đạt 9/13 thì sau hiệu chỉnh 5 cấu hình vẫn không qua.

## 7. Cái KHÔNG được kết luận từ báo cáo này

- ❌ "Dòng tiền ngoại khớp lệnh không chứa thông tin." Nó **có** — nó nhìn thấy 2018 trước đỉnh.
  Cái bị bác bỏ là **một luật ngưỡng cố định trên chuỗi đó dùng làm cap**, ở 5 dạng đã prereg.
- ❌ "Đã chứng minh được điều gì bằng thống kê." Pre-flight nói không thể. Đây là chẩn đoán.
- ❌ "Thử thêm ngưỡng/cửa sổ khác sẽ ra." Đó chính là đường dẫn tới overfit; 5 cấu hình đã khai
  trước và đã dùng hết. Muốn thử tiếp phải khai trial mới và chịu deflate tiếp.

## 8. Đề xuất

1. **NO-GO** cho H4 như một cap tầng 3. Không dispatch quant-skeptic (quy chuẩn §15: chỉ bắt buộc
   khi đang ĐỀ XUẤT thay đổi production — đây là "không đổi gì").
2. **Đóng câu hỏi mở §B.1** của `production_mechanism_2009_2018_20260830.md`: điểm mù 2018 nay đã
   đo được, câu trả lời là phủ định. Cập nhật file đó trỏ tới báo cáo này.
3. Giữ lại **một** thứ có giá trị: chuỗi `foreign_matched_net_bn` là biến **mô tả/chẩn đoán** tốt
   cho báo cáo regime (nó thực sự nhìn thấy 2018, 2020, 2022) — dùng trong khối "Market regime
   context" weekly/monthly theo tinh thần Value Radar **DISPLAY-ONLY**, không làm cổng.
4. Không đóng góp gì cho quyết định mua gói FiinPro — H4 không phải lý do mua.
