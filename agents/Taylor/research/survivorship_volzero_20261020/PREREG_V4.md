# PREREG V4 — Tỉ trọng lãi/lỗ LAG của PIN theo điều kiện thanh khoản lệnh mua, theo năm — job Taylor_20261020_162558, EXPLORATORY
Chỉ đọc 4 CSV pin (`raw/pin_*.csv`) + cache `data/bq_cache_asof20260729_postrestate/ticker`. Không chạy engine. md5+commit trước khi tính.

## 1. Phân loại từng lệnh MUA LAG (TX, book==LAG, action==buy, bỏ ETF_PARK)
`dv` = Volume × COALESCE(Price, Close) ngày khớp. Nhóm loại trừ lẫn nhau:
- **Z**: Volume==0; **X**: Volume>0 và buy_amount > 20% × dv; **OK**: còn lại; **NA**: không có dòng cache (báo riêng).
Đây là phân loại HẬU NGHIỆM (dùng KL cùng phiên) — mô tả, không phải luật khớp.
## 2. Lãi/lỗ theo lô
Lô = holding_id. PnL lô = Σ(sell_amount − fee) bán + giá trị MTM_UNREALIZED (nếu lô còn mở cuối kỳ: sell_amount, fee) − Σ(buy_amount + fee).
Chia PnL lô cho các lệnh mua của nó theo tỉ lệ buy_amount ⇒ PnL theo nhóm Z/X/OK/NA. Năm = năm của lệnh mua (ymd).
## 3. Báo
Mỗi chân × năm 2014–2026: giá trị mua (tỷ) và PnL (tỷ) theo Z/X/OK/NA; tỉ trọng giá trị mua; tỉ trọng PnL = PnL nhóm / PnL LAG tổng
(cả dấu: nhóm lỗ khi tổng lãi ⇒ âm). Tổng 2014–2026 + phân đoạn 2014–2021 vs 2022–2026. Kiểm tổng: ΣPnL lô = Σ(cash flow LAG) trong
TX (nếu lệch > 1 VND ⇒ báo, không giấu). Book ref LAG (25B riêng) ≠ phần LAG trong combined (allocator) — PnL ở đây là của book ref.
## 4. Giới hạn
Phân bổ PnL lô theo buy_amount giả định cùng lợi suất cho mọi lệnh mua trong lô (lệnh khớp nhiều ngày giá khác ⇒ xấp xỉ). PnL book ref
không phải đóng góp CAGR combined (không cộng ra ΔCAGR).
