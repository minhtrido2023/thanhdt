# Market Overheat Logic

Tài liệu này giải thích logic trong `report/build_report.py`, tập trung vào class `MarketEvaluation`, đặc biệt là phần xác định `overbuy` / `oversell` trong hàm `evaluate()`.

## Phạm Vi

Các đoạn chính cần hiểu:

- `MarketEvaluation._filter_and_group(...)`
- `MarketEvaluation.evaluate(...)`

File nguồn:

- `report/build_report.py`

## Mục Tiêu Của Logic

Phần này nhằm xác định xem thị trường hiện tại có đang ở trong một giai đoạn cực trị gần đây hay không:

- `overbuy`: thị trường tăng mạnh bất thường trong 3 tháng
- `oversell`: thị trường giảm mạnh bất thường trong 3 tháng

Kết quả cuối cùng được trả về trong key:

- `overheated`

Tên `overheated` hơi gây hiểu nhầm vì thực tế nó chứa cả trạng thái `overbuy` lẫn `oversell`, chứ không chỉ riêng trạng thái "quá nóng".

## Tổng Quan Luồng `MarketEvaluation.evaluate()`

Hàm `evaluate(df_latest)` thực hiện các bước chính sau:

1. Đọc dữ liệu lịch sử của chỉ số thị trường, mặc định là `VNINDEX`.
2. Tính các chỉ báo ngắn hạn và định giá:
   - `profit_3M`
   - `ratio_TD_MA1M`
   - `ratio_PE_PE_MA5Y`
   - `P3M`
3. Tính các percentile lịch sử cho:
   - `P3M`
   - `VNINDEX_PE`
   - các future-return window `P60` tới `P240`
4. Dùng `P3M` để tìm các giai đoạn extreme:
   - vùng tăng quá mạnh -> `overbuy`
   - vùng giảm quá mạnh -> `oversell`
5. Gọi `_filter_and_group()` để:
   - lọc các điểm extreme
   - gom thành các giai đoạn
   - ước lượng ngày kết thúc của giai đoạn
6. Nếu giai đoạn gần nhất còn hiệu lực tới sát hiện tại thì gắn `overheated`
7. Song song đó còn đánh giá thêm:
   - `is_pe`
   - `is_bfi`
   - `index_pattern`
   - `latest_hit_pattern`

## Dữ Liệu Cốt Lõi Dùng Để Xác Định Overbuy / Oversell

### `P3M`

Trong code:

```python
df_index['P3M'] = 100 * (df_index['O3M'] - 1)
```

Ý nghĩa:

- `O3M` biểu diễn tỷ lệ thay đổi trong 3 tháng
- `P3M` là mức sinh lời 3 tháng tính theo phần trăm

Ví dụ:

- `O3M = 1.15` -> `P3M = 15`
- `O3M = 0.85` -> `P3M = -15`

Diễn giải:

- `P3M` rất cao so với lịch sử -> thị trường tăng rất mạnh trong 3 tháng -> nghiêng về `overbuy`
- `P3M` rất thấp so với lịch sử -> thị trường giảm rất mạnh trong 3 tháng -> nghiêng về `oversell`

## Percentile Được Dùng

Code sử dụng các percentile:

```python
percentiles = [0.1, 0.2, 0.8, 0.9, 0.95]
```

Tức là dùng các ngưỡng:

- `10%`
- `20%`
- `80%`
- `90%`
- `95%`

Sau đó tính percentile của `P3M` trên toàn bộ lịch sử.

### Ý Nghĩa

- `95%`, `90%`, `80%`: vùng tăng cao
- `10%`, `20%`: vùng giảm sâu

## Các Rule Dùng Để Dò Extreme Regime

Trong `evaluate()` có:

```python
over_params = [
    {'col': 'P3M', 'threshold': df_percentiles.loc['95%', 'P3M'], 'comparison': "greater", 'id_percentile': '95%'},
    {'col': 'P3M', 'threshold': df_percentiles.loc['90%', 'P3M'], 'comparison': "greater", 'id_percentile': '90%'},
    {'col': 'P3M', 'threshold': df_percentiles.loc['10%', 'P3M'], 'comparison': "less", 'id_percentile': '10%'},
    {'col': 'P3M', 'threshold': df_percentiles.loc['80%', 'P3M'], 'comparison': "greater", 'id_percentile': '80%'},
    {'col': 'P3M', 'threshold': df_percentiles.loc['20%', 'P3M'], 'comparison': "less", 'id_percentile': '20%'},
]
```

### Diễn giải

- `comparison == "greater"`:
  - `P3M >= threshold`
  - đây là vùng `overbuy`
- `comparison == "less"`:
  - `P3M <= threshold`
  - đây là vùng `oversell`

### Thứ Tự Ưu Tiên

Code duyệt theo đúng thứ tự sau:

1. `overbuy above 95% percentile`
2. `overbuy above 90% percentile`
3. `oversell below 10% percentile`
4. `overbuy above 80% percentile`
5. `oversell below 20% percentile`

Nghĩa là nếu nhiều tín hiệu cùng gần hiện tại thì tín hiệu xuất hiện trước trong danh sách sẽ thắng.

## Điểm Quan Trọng: Logic Không Chỉ Kiểm Tra Giá Trị Hiện Tại

Đây là phần dễ hiểu nhầm nhất.

Code không làm kiểu đơn giản:

- hôm nay `P3M > 95%` thì kết luận `overbuy`
- hôm nay `P3M < 10%` thì kết luận `oversell`

Thay vào đó, code:

1. tìm tất cả các ngày extreme trong lịch sử gần đây
2. gom chúng thành các giai đoạn
3. dùng future-return statistics để ước lượng giai đoạn đó kéo dài tới đâu
4. chỉ khi giai đoạn gần nhất còn sát hiện tại thì mới trả về `overheated`

Nói cách khác, hệ thống đang tìm một "extreme regime" chứ không chỉ check một điểm dữ liệu đơn lẻ ở ngày hôm nay.

## Vai Trò Của `_filter_and_group()`

Hàm `_filter_and_group(...)` là trung tâm của logic.

Đầu vào chính:

- `df_vnindex`
- `col`
- `threshold`
- `comparison`
- `df_percentiles`
- `id_percentile`

Đầu ra:

- một DataFrame chỉ chứa giai đoạn gần nhất:
  - `start_group`
  - `end_group`

## Bước 1: Lọc Các Điểm Extreme

```python
condition = f"{col} >= {threshold}" if comparison == "greater" else f"{col} <= {threshold}"
df_filtered = df_vnindex.query(condition).copy()
```

Diễn giải:

- `overbuy`: lấy các dòng mà `P3M` vượt ngưỡng cao
- `oversell`: lấy các dòng mà `P3M` thấp hơn ngưỡng thấp

Mỗi dòng này ban đầu được xem là một điểm khởi đầu tiềm năng của một giai đoạn extreme.

## Bước 2: Xác Định Độ Dài Hiệu Lực Của Mỗi Điểm Extreme

Trong `evaluate()`, code tạo các cột:

```python
for i in range(60, 245, 5):
    df_index[f'P{i}'] = 100 * ((df_index['Open_1D'].shift(-i) / df_index['Open_1D']) - 1)
```

Tức là có các cột:

- `P60`
- `P65`
- `P70`
- ...
- `P240`

### Ý Nghĩa

Mỗi `P{i}` là lợi nhuận tương lai sau `i` phiên, tính từ `Open_1D` của ngày bắt đầu.

Ví dụ:

- `P60`: lợi nhuận sau khoảng 60 phiên
- `P120`: lợi nhuận sau khoảng 120 phiên
- `P240`: lợi nhuận sau khoảng 240 phiên

Các cột này được dùng để so sánh một điểm extreme hiện tại với hành vi lịch sử sau extreme.

## Bước 3: So Sánh Future Return Với Percentile Cùng Mức

Trong `_filter_and_group()`:

```python
ret = (cur / base - 1) * 100
```

rồi so sánh với:

```python
df_percentiles.loc[id_percentile, per]
```

Tức là:

- nếu đang xét threshold `95%` của `P3M`
- thì future return tại các mốc `P60`, `P65`, `P70`... cũng được so với percentile `95%` của chính các cột đó

Điều này làm cho logic nhất quán theo từng mức extreme.

## Logic Riêng Cho `Overbuy`

Với `comparison == "greater"`:

```python
if comparison == "greater" and ret <= df_percentiles.loc[id_percentile, per]:
    break_count += 1
else:
    break_count = 0
```

### Cách Hiểu

Một điểm `overbuy` được coi là còn giữ được trạng thái "nóng" nếu các future return tương ứng vẫn đủ cao so với chuẩn lịch sử cùng percentile.

Ngược lại, nếu future return bắt đầu yếu đi, tức:

- `ret <= ngưỡng percentile tương ứng`

thì coi như regime bắt đầu gãy.

Nếu hiện tượng này xảy ra liên tiếp 4 mốc thì dừng:

```python
if break_count == 4:
    break
```

### Kết Luận Cho Overbuy

- bắt đầu từ một ngày có `P3M` cực cao
- nhìn về tương lai qua các mốc `P60` -> `P240`
- nếu chuỗi future performance không còn duy trì được độ mạnh tương ứng thì giai đoạn `overbuy` bị xem là kết thúc

## Logic Riêng Cho `Oversell`

Với `comparison == "less"`:

```python
elif comparison == "less" and ret >= df_percentiles.loc[id_percentile, per]:
    break_count += 1
```

### Cách Hiểu

Một điểm `oversell` được coi là còn nằm trong trạng thái cực xấu nếu future return vẫn còn yếu theo chuẩn percentile thấp.

Khi future return bắt đầu phục hồi, tức:

- `ret >= ngưỡng percentile thấp tương ứng`

thì đó là tín hiệu cho thấy regime `oversell` bắt đầu kết thúc.

Nếu điều này xảy ra liên tiếp 4 mốc thì dừng.

### Kết Luận Cho Oversell

- bắt đầu từ một ngày có `P3M` rất thấp
- nhìn xem hiệu suất sau đó có còn nằm trong trạng thái xấu kéo dài hay không
- nếu không còn xấu liên tục nữa thì xem như giai đoạn `oversell` đã chấm dứt

## Ý Nghĩa Của `break_count == 4`

Trong code, mỗi mốc thời gian tăng thêm 5 phiên:

- `60`
- `65`
- `70`
- `75`
- ...

Khi `break_count == 4`, điều đó tương đương với việc hệ thống quan sát thấy 4 mốc liên tiếp mà trạng thái extreme không còn được duy trì.

Đây là một heuristic thực nghiệm để tránh kết luận regime kết thúc chỉ vì một dao động ngắn hạn đơn lẻ.

## Cách Xác Định `end_group`

Sau khi break, code dùng:

```python
session_break = int(session) - break_count * 5
offset_dates = df_base.iloc[start_index + int(session_break)]['time']
```

Ý nghĩa:

- `session` là mốc hiện tại nơi chuỗi fail đang diễn ra
- `break_count * 5` lùi lại về trước khi chuỗi fail bắt đầu
- `offset_dates` trở thành ngày kết thúc hợp lệ cuối cùng của giai đoạn extreme

Nếu có lỗi hoặc thiếu dữ liệu, code fallback về ngày cuối cùng của chuỗi dữ liệu.

## Bước 4: Gom Các Điểm Extreme Thành Giai Đoạn

Sau khi mỗi điểm extreme có một `start_group` và `end_group`, code tiếp tục gom nhóm theo tháng:

```python
df_filtered['month_diff'] = round(df_filtered['month'].diff().dt.days / 31).fillna(0)
df_filtered['group'] = (df_filtered['month_diff'] > 1).cumsum()
```

Rồi merge các nhóm gần nhau thêm một lần nữa:

```python
df_filtered['group_diff'] = (df_filtered['start_group'] - df_filtered['end_group'].shift(1)).dt.days / 31
df_filtered['group'] = (df_filtered['group_diff'] > 1).cumsum()
```

### Mục Tiêu

- tránh đếm nhiều ngày extreme gần nhau thành nhiều tín hiệu rời rạc
- gom thành một regime thống nhất
- lấy ra giai đoạn extreme gần nhất

Cuối cùng:

```python
return df_filtered.tail(1)[['start_group', 'end_group']]
```

Nghĩa là chỉ trả về giai đoạn gần nhất.

## Khi Nào `overheated` Được Gắn

Trong `evaluate()`:

```python
if abs(pd_period['end_group'].iloc[0] - now) < pd.Timedelta(days=15):
    found_flag = True
    break
```

Nghĩa là chỉ khi ngày kết thúc của giai đoạn gần nhất nằm rất gần hiện tại, nhỏ hơn khoảng 15 ngày, thì mới xem regime đó là còn "đang có ý nghĩa" ở hiện tại.

Sau đó build output:

```python
overheated = {
    'start_group': begin,
    'end_group': end,
    'profit': convert_to_sci_notation(100 * profit),
    'type': p_types
}
```

Trong đó:

- `start_group`: ngày bắt đầu regime
- `end_group`: ngày kết thúc regime
- `profit`: mức tăng/giảm của `Close` từ đầu tới cuối regime
- `type`: loại regime, ví dụ:
  - `overbuy above 95% percentile`
  - `oversell below 10% percentile`

## Ý Nghĩa Của `profit`

```python
profit = df_index.loc[df_index['time'] == end, 'Close'].values[0] / df_index.loc[df_index['time'] == begin, 'Close'].values[0] - 1
```

Đây là hiệu suất thực tế của chỉ số từ đầu tới cuối giai đoạn extreme.

Lưu ý:

- đây không phải future return dự báo
- đây là mức biến động đã thực sự xảy ra trong giai đoạn mà hệ thống xác định

## Phần Logic Tổng Hợp Để Người Dùng Và Agent Hiểu Nhanh

Có thể tóm gọn toàn bộ cơ chế như sau:

1. Hệ thống dùng `P3M` để đo độ nóng/lạnh của thị trường trong 3 tháng.
2. Nếu `P3M` nằm trong vùng cực cao của lịch sử, đó là ứng viên `overbuy`.
3. Nếu `P3M` nằm trong vùng cực thấp của lịch sử, đó là ứng viên `oversell`.
4. Nhưng hệ thống không kết luận ngay theo giá trị hiện tại.
5. Nó truy ngược các thời điểm extreme gần đây, rồi kiểm tra future-return regime để xem trạng thái extreme đó kéo dài tới đâu.
6. Sau đó gom các điểm gần nhau thành một giai đoạn thị trường.
7. Chỉ khi giai đoạn gần nhất còn sát hiện tại thì mới báo `overheated`.
8. Kết quả cuối cùng là một regime-level signal, không phải point-in-time signal đơn giản.

## Tóm Tắt Khái Niệm `Overbuy`

`Overbuy` trong logic này không có nghĩa là:

- chỉ số hôm nay tăng mạnh nên chắc chắn phải giảm ngay

Mà có nghĩa là:

- trong 3 tháng gần nhất, mức tăng của thị trường đang nằm trong vùng cực cao so với lịch sử
- và dữ liệu lịch sử cho thấy đây là một giai đoạn tăng mạnh bất thường
- hệ thống theo dõi tới khi cường độ tăng không còn duy trì được theo cấu trúc historical percentile nữa thì xem regime kết thúc

## Tóm Tắt Khái Niệm `Oversell`

`Oversell` trong logic này không có nghĩa là:

- chỉ số hôm nay giảm sâu nên chắc chắn phải bật tăng ngay

Mà có nghĩa là:

- trong 3 tháng gần nhất, mức giảm đang nằm trong vùng cực thấp so với lịch sử
- đây là một giai đoạn thị trường bị bán mạnh bất thường
- hệ thống chỉ coi regime còn tồn tại khi trạng thái xấu vẫn còn thể hiện liên tục trong cấu trúc future-return lịch sử

## Quan Hệ Giữa `overheated`, `is_pe`, `is_bfi`, `index_pattern`

Đây là các tín hiệu song song, không phải cùng một logic.

### `overheated`

- dựa chủ yếu vào `P3M`
- đại diện cho regime giá tăng/giảm cực trị

### `is_pe`

- dựa vào percentile của `VNINDEX_PE`
- phản ánh định giá PE hiện tại đang cao/thấp thế nào

### `is_bfi`

- dựa vào Buffett Indicator
- phản ánh vốn hóa thị trường so với GDP

### `index_pattern`

- dựa vào các mẫu kỹ thuật trong `self.index_pattern`
- phản ánh cấu trúc kỹ thuật kiểu Bear divergence / Bull divergence

Nói cách khác:

- `overheated` = regime giá
- `is_pe` = regime định giá PE
- `is_bfi` = regime định giá theo vốn hóa/GDP
- `index_pattern` = regime kỹ thuật

## Các Điểm Cần Lưu Ý Cho Agent Và Người Bảo Trì

### 1. Tên `overheated` không hoàn toàn chính xác

Vì kết quả này có thể là:

- `overbuy`
- hoặc `oversell`

Nên nếu refactor sau này, tên rõ nghĩa hơn có thể là:

- `market_extreme`
- `market_regime_extreme`
- `overbuy_oversell_signal`

### 2. Logic là heuristic, không phải mô hình tài chính cứng

Các tham số hard-code:

- 500 phiên gần nhất
- bước 5 phiên
- window từ 60 đến 240 phiên
- break sau 4 lần liên tiếp
- threshold 15 ngày gần hiện tại

Tất cả đều là rule thực nghiệm.

### 3. `overheated` không kết hợp trực tiếp `PE` hoặc `BFI`

Dù cùng nằm trong output cuối, nhưng `overheated` hiện chỉ dùng `P3M` để xác định overbuy/oversell.

### 4. Chỉ lấy `df_index[-500:]` để dò giai đoạn gần đây

Điều này giúp tập trung vào regime hiện tại nhưng cũng làm tín hiệu phụ thuộc vào cửa sổ dữ liệu gần đây.

### 5. Việc so sánh future-return percentile là điểm cốt lõi nhất

Nếu cần refactor, test, hoặc giải thích cho người khác, đây là đoạn quan trọng nhất phải giữ nguyên ý tưởng:

- không check điểm hiện tại đơn lẻ
- mà check sự tồn tại và độ bền của một regime extreme

## Pseudocode Tóm Tắt

```text
load VNINDEX history

compute:
- P3M
- VNINDEX_PE percentile
- future returns P60..P240

build percentile table for:
- P3M
- VNINDEX_PE
- P60..P240

for each rule in over_params:
  find all rows where P3M is extreme enough
  for each row:
    evaluate how long extreme regime survives
    determine start_group / end_group
  merge nearby rows into one regime
  keep latest regime only

  if latest regime ends within 15 days of now:
    mark found_flag = True
    classify as overbuy / oversell
    stop

if found_flag:
  output overheated = {
    start_group,
    end_group,
    profit,
    type
  }
else:
  overheated = None
```

## Kết Luận Cuối

Logic `overbuy` / `oversell` trong `MarketEvaluation.evaluate()` là một cơ chế phát hiện regime extreme của thị trường dựa trên `P3M`.

Nó không chỉ kiểm tra xem hiện tại thị trường đang cao hay thấp so với lịch sử, mà còn cố gắng xác định:

- extreme regime bắt đầu từ khi nào
- kéo dài đến đâu
- và liệu regime gần nhất có còn đủ sát hiện tại để đáng báo động hay không

Đây là một cách tiếp cận theo regime/historical behavior, không phải một rule một-dòng kiểu threshold check tại ngày hiện tại.

## Tham Chiếu Nhanh

- `report/build_report.py`
  - `MarketEvaluation._filter_and_group(...)`
  - `MarketEvaluation.evaluate(...)`

- chỉ báo chính:
  - `P3M = 100 * (O3M - 1)`

- phân loại:
  - `overbuy`: `P3M` cao hơn các percentile cao
  - `oversell`: `P3M` thấp hơn các percentile thấp

- output:
  - `overheated`
  - `is_pe`
  - `is_bfi`
  - `index_pattern`
