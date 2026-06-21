# MarketEvaluation Rules
## Mục đích
`MarketEvaluation` trong `webui/utils.py` là lớp filter ở cấp thị trường, dùng `VNINDEX_PE` để xác định trạng thái thị trường và tác động lên tín hiệu mua/bán của chiến lược cổ phiếu.
Nó không trực tiếp chọn cổ phiếu, mà làm nhiệm vụ:
- Xác định khi nào thị trường đang đắt/rủi ro.
- Chặn tín hiệu mua trong giai đoạn market xấu.
- Bổ sung tín hiệu bán do điều kiện thị trường.
- Chỉ cho phép mua lại khi thị trường hạ nhiệt hoặc đủ rẻ.
## Vị trí chính
- File: `webui/utils.py`
- Class chính: `MarketEvaluation(BaseEval)`
Các hàm liên quan:
- `__init__`
- `_quantile_pe`
- `_create_schedule_market`
- `update_long_hit_pattern`
- `update_short_hit_pattern`
- `update_buy_2_sell`
Các class sử dụng `MarketEvaluation`:
- `AllEvaluation`
- `ShortEvaluation`
---
## Tổng quan luồng xử lý
### 1. Khởi tạo
Trong `MarketEvaluation.__init__`:
- Gọi `BaseEval` với:
  - `stock='VNINDEX'`
  - `dict_filter=MARKET_DICT_FILTER`
  - `cutloss=0.2`
- Tính percentile của `VNINDEX_PE` qua `_quantile_pe()`
- Sinh lịch market regime qua `_create_schedule_market()`
### 2. Ý tưởng chiến lược
Chiến lược dùng định giá thị trường (`VNINDEX_PE`) để điều khiển giao dịch:
- Thị trường đắt -> hạn chế hoặc khóa long.
- Thị trường đủ rẻ / hết cooldown -> cho phép mở lại long.
- Nếu thị trường quá đắt -> yêu cầu điều kiện quay lại chặt hơn.
---
## Hàm `_quantile_pe`
### Mục đích
Tính các percentile cho cột `VNINDEX_PE` trong toàn bộ dữ liệu thị trường.
### Cách làm
Tạo dictionary:
- `P0, P5, P10, ..., P95`
Dựa trên:
- `np.percentile(self.df_all['VNINDEX_PE'].dropna().values, i)`
### Vai trò
Các percentile này là ngưỡng động để áp rule, thay vì dùng giá trị P/E cố định.
Ví dụ:
- `P20`: vùng rẻ
- `P60`: vùng cao tương đối
- `P90`, `P95`: vùng rất đắt
---
## Hàm `_create_schedule_market`
Đây là lõi logic của `MarketEvaluation`.
### Bước 1. Lấy tín hiệu buy/sell của market
Dùng `self.df_buy` và `self.df_sell` do `BaseEval` tạo ra cho `VNINDEX`, rồi merge thêm cột `VNINDEX_PE`.
Ngoài ra:
- Loại bỏ các dòng sell có `Sell_filter` là `Hold` hoặc `hold`
### Bước 2. Chuẩn hóa theo tháng
Thêm cột:
- `month = YYYY-MM`
Sau đó mỗi tháng chỉ giữ tín hiệu đầu tiên cho buy và sell.
### Rule đang dùng
#### Rule 1. Market sell threshold
Chỉ giữ sell khi:
- `VNINDEX_PE >= P60`
#### Rule 2. Market buy threshold
Chỉ giữ buy khi:
- `VNINDEX_PE <= P60`
Ý nghĩa:
- Từ `P60` trở lên: thị trường bắt đầu bị xem là đủ đắt để phòng thủ.
- Từ `P60` trở xuống: thị trường được xem là đủ an toàn để xem xét quay lại.
#### Rule 3. Mỗi tháng chỉ lấy tín hiệu đầu tiên
Sau khi lọc, dữ liệu được:
- sort theo `time`
- `drop_duplicates(subset=['month'], keep='first')`
Ý nghĩa:
- Giảm nhiễu tín hiệu lặp trong cùng tháng.
---
## Rule tạo block window từ sell đến buy
Với mỗi market sell, code tạo một khoảng thời gian chặn mua:
- `block_start = sell_time`
- `block_end = buy_time`
### Rule 4. Thời gian chặn phụ thuộc mức PE tại thời điểm sell
Nếu `sell_pe`:
- `>= P95` -> chặn `1.5 năm`
- `>= P90` -> chặn `1 năm`
- `>= P80` -> chặn `90 ngày`
- `>= P65` -> chặn `60 ngày`
- còn lại (`P60` đến dưới `P65`) -> chặn `30 ngày`
Ý nghĩa:
- PE càng cao thì thị trường càng bị coi là rủi ro, thời gian chặn càng dài.
### Bước chọn `buy_time`
Ban đầu:
- `buy_time = sell_time + window`
Sau đó tìm buy signal đầu tiên trong khoảng:
- `time > sell_time`
- `time <= buy_time`
Nếu có buy hợp lệ:
- dùng buy đầu tiên đó làm `buy_time`
Nếu không có:
- giữ `buy_time` là cuối cửa sổ chặn
### Rule 5. Trường hợp market cực đắt phải đợi cực rẻ
Nếu:
- `sell_pe >= P90`
Thì buy trong cửa sổ còn phải thỏa:
- `VNINDEX_PE <= P20`
Ý nghĩa:
- Nếu market đã từng quá nóng, chỉ quay lại khi market thật sự rẻ.
### Kết quả
Sinh ra `schedule_market`, mỗi phần tử gồm:
- `sell_time`
- `buy_time`
- `sell_pe`
- `buy_pe`
Đây là danh sách các khoảng market bị block.
---
## Hàm `update_long_hit_pattern`
### Mục đích
Áp market regime lên tín hiệu long của cổ phiếu.
### Logic
Với mỗi khoảng trong `schedule_market`:
- xóa mọi `df_buy_hit` có `time` nằm trong đoạn từ `sell_time` đến `buy_time`
Rule:
- Không cho mở vị thế long trong giai đoạn market đang bị block.
### Logic bổ sung
Hàm còn lấy các market sell đã lọc từ `self.df_sell` và append vào `df_sell_hit`.
Ý nghĩa:
- Không chỉ chặn buy mới
- Mà còn bổ sung sell signal do market
### Kết luận cho long
`MarketEvaluation` tác động lên long strategy theo 2 cách:
- Chặn mua trong vùng market rủi ro
- Thêm tín hiệu bán do market regime
---
## Hàm `update_short_hit_pattern`
### Mục đích
Áp market regime lên tín hiệu short.
### Logic hiện tại
Với mỗi khoảng trong `schedule_market`:
- xóa các `df_sell_hit` nằm trong đoạn block
### Nhận xét
So với long strategy, logic cho short đơn giản hơn và có dấu hiệu chưa hoàn thiện:
- Có một khối code comment-out liên quan đến bearish market
- Hiện tại chưa thấy bổ sung đầy đủ market signal cho short như với long
### Kết luận cho short
`MarketEvaluation` có tích hợp với short, nhưng mức độ hoàn thiện thấp hơn long.
---
## Hàm `update_buy_2_sell`
### Mục đích
Cập nhật mapping `buy_2_sell`.
### Logic
Duyệt `self.market_dictFilter`.
Nếu filter bắt đầu bằng `~`:
- bỏ ký tự `~`
- append tên filter đó vào danh sách sell của từng key trong `buy_2_sell`
Ngoại trừ:
- key `pre_pattern`
- hoặc key nằm trong `buy_2_sell['pre_pattern']`
### Ý nghĩa
Các market filter dạng phủ định được thêm như sell condition bổ sung cho nhiều buy pattern.
---
## Các class liên quan
### `AllEvaluation`
Sau khi gọi `AllEval`, nếu có `market_eval` thì:
- update lại `df_sell`, `df_buy` bằng `update_long_hit_pattern`
- update `buy_2_sell` bằng `update_buy_2_sell`
Đây là nơi market filter được tích hợp vào chiến lược long.
### `ShortEvaluation`
Sau khi gọi `ShortSellEval`, nếu có `market_eval` thì:
- update lại `df_sell`, `df_buy` bằng `update_short_hit_pattern`
Đây là nơi market filter được tích hợp vào short strategy.
### `Simulation_all`, `Simulation_weight`, `ShortSellSimulation_all`
Các class simulation này không tạo thêm market rule mới.
Vai trò của chúng là:
- nhận các deal đã được filter bởi `MarketEvaluation`
- rồi chạy mô phỏng backtest
---
## Danh sách rule đầy đủ
### Rule nền theo percentile
- Dùng percentile của `VNINDEX_PE` thay cho ngưỡng P/E tuyệt đối.
### Rule market sell
- Chỉ coi là market sell khi `PE >= P60`.
### Rule market buy
- Chỉ coi là market buy khi `PE <= P60`.
### Rule chống nhiễu
- Mỗi tháng chỉ lấy tín hiệu đầu tiên cho buy và sell.
### Rule loại bỏ hold
- Không dùng sell có `Sell_filter` là `Hold` hoặc `hold`.
### Rule cooldown theo độ nóng của PE
- `P60-P65`: 30 ngày
- `P65-P80`: 60 ngày
- `P80-P90`: 90 ngày
- `P90-P95`: 1 năm
- `>=P95`: 1.5 năm
### Rule quay lại sau extreme valuation
- Nếu `sell_pe >= P90` thì chỉ chấp nhận buy với `PE <= P20`.
### Rule chọn buy đầu tiên
- Nếu có nhiều buy trong cửa sổ thì chỉ lấy buy đầu tiên.
### Rule áp lên long
- Xóa buy signal của cổ phiếu trong toàn bộ block window.
- Append thêm market sell vào stock sell.
### Rule áp lên short
- Xóa một phần sell signal nằm trong block window.
- Chưa thấy phần mở rộng bearish regime được dùng đầy đủ.
---
## Ý đồ chiến lược
`MarketEvaluation` là một market overlay theo hướng phòng thủ:
- Market đắt -> giảm tham gia
- Market quá đắt -> chờ rất lâu hoặc chờ rất rẻ mới quay lại
- Dùng valuation regime để giảm drawdown cho chiến lược long
Đây là logic market timing dựa trên định giá, không phải chỉ dựa trên price action hay momentum.
---
## Điểm mạnh
- Ngưỡng động theo phân vị lịch sử
- Có cơ chế cooldown theo mức độ overvaluation
- Tách market filter khỏi stock filter
- Có thể tái dùng cho nhiều lớp đánh giá
## Điểm cần lưu ý
- Mốc `P60` là ngưỡng khá mềm
- Rule `P90 -> P20` rất chặt, có thể bỏ lỡ nhịp hồi
- Chỉ lấy 1 tín hiệu/tháng có thể bỏ sót regime shift nhanh
- Logic short hiện chưa hoàn chỉnh bằng long
- Việc fallback `buy_pe` theo `searchsorted(...)-1` phụ thuộc dữ liệu time khá nhiều
---
## Kết luận ngắn
`MarketEvaluation` là lớp filter thị trường dùng `VNINDEX_PE` để:
- nhận diện vùng market đắt
- block tín hiệu mua trong vùng rủi ro
- thêm tín hiệu bán do market
- chỉ cho phép mua lại khi đủ thời gian hoặc đủ rẻ
Rule quan trọng nhất:
1. `Sell` khi `PE >= P60`
2. `Buy` khi `PE <= P60`
3. Block window tăng dần theo độ cao của PE
4. Nếu `PE >= P90` thì buy lại phải đạt `PE <= P20`