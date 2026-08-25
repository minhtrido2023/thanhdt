# Phần A — Backtest 3-book thật (w_BAL=w_LAG=w_DC=1/3, band ±10pp)

Job `Taylor_20260825_151108` (dispatch Mike, giai đoạn 2). Script: `exp_dc3book_20260825.py`
(R&D wrapper trong thư mục này — KHÔNG sửa `pt_v23_audit_2014.py` /
`converge_portfolio_backtest.py`, KHÔNG ghi đè CSV canonical).

## Method

1. **r_BAL(t), r_LAG(t)**: lấy trực tiếp từ CSV production golive-audit (`record_type=DAILY`,
   cột `nav_bal_ref`/`nav_lag_ref`, pct-change) — đúng book-level NAV tracker đã dùng ở job
   `Taylor_20260825_134238` (gross-by-state). Đã bao gồm hành vi thật của từng book (BAL park vào
   custom30V khi NEUTRAL; LAG không park, ngồi cash khi hết signal).
2. **r_DC(t)**: dựng lại bằng chính loader/eval của `converge_portfolio_backtest.py` (import, không
   viết lại `eval_*`), **equal-weight** (tilt=False, đúng chỉ đạo dispatch), cap 0.20/tên. **Khác
   1 điểm có chủ đích so với ConvergePort gốc**: idle cash của DC KHÔNG park mọi state — chỉ park
   @0.80 vào custom30V khi state=NEUTRAL(3), state khác thì cash 0% (đúng quy ước V2.4/CLAUDE.md
   "lãi tiền gửi nhàn rỗi 0%/năm"), để DC là 1 book so sánh ngang hàng BAL/LAG dưới cùng quy ước.
3. **Combine**: 3 dollar-bucket (V_BAL, V_LAG, V_DC) khởi tạo NAV0/3 mỗi phần. Mỗi ngày áp return
   riêng của từng book vào bucket của nó. Nếu tỷ trọng bucket nào lệch khỏi 1/3 quá ±10pp →
   rebalance CẢ BA về 1/3, tính TC 0,1% (CLAUDE.md) trên phần vốn 2 chiều di chuyển.
4. **Self-check**: max weight-leak = 2.22e-16 (≈0, PASS). Calendar clip về ≥2014-08-05 (ngày
   custom30V/DC universe có dữ liệu) — baseline SO SÁNH cũng recompute lại trên ĐÚNG cửa sổ này
   (không dùng số đã đăng ký ở registry vốn tính từ 2014-01-02), để so sánh apples-to-apples.

## Kết quả

| Config | Window | CAGR% | Sharpe | Sortino | MaxDD% | Calmar | N |
|---|---|---:|---:|---:|---:|---:|---:|
| baseline 2-book (park=0.80, same window) | FULL | 29.33 | 1.81 | 2.40 | -18.3 | 1.60 | 2965 |
| baseline 2-book | IS 2014-19 | 26.63 | 1.63 | 2.35 | -18.3 | 1.46 | 1354 |
| baseline 2-book | OOS 2020+ | 31.65 | 1.98 | 2.42 | -17.5 | 1.80 | 1611 |
| **exp 3-book (dc33)** | **FULL** | **27.05** | **1.70** | **2.16** | **-19.9** | **1.36** | 2965 |
| exp 3-book (dc33) | IS 2014-19 | 20.51 | 1.44 | 1.97 | -16.6 | 1.23 | 1354 |
| exp 3-book (dc33) | OOS 2020+ | 32.82 | 1.90 | 2.30 | -19.9 | 1.65 | 1611 |

Self-check phụ: rebalance events = **4 lần trong ~11,9 năm** (0,34/năm) — band ±10pp gần như
KHÔNG BAO GIỜ kích hoạt, nghĩa là đây gần như là buy-and-hold tĩnh 1/3-1/3-1/3 từ ngày đầu, không
phải 1 allocator động thật sự. DC active (≥1 tên double-confirm) 82,6% số phiên (2449/2965).

Sanity check: baseline recompute của tôi (FULL CAGR 29,33%/MaxDD −18,3%/Calmar 1,60) khớp rất sát
số đã pin ở KB ("V2.4 baseline park=0.80: CAGR 29,85%/Sharpe 1,87/MaxDD −18,3%/Calmar 1,63") —
lệch nhỏ do khác điểm bắt đầu (2014-08 vs 2014-01), MaxDD khớp gần như tuyệt đối → phương pháp
extraction đáng tin.

## Kết luận Phần A

**3-book tĩnh (1/3-1/3-1/3, band rộng ±10pp) THUA baseline 2-book trên MỌI window**: CAGR thấp
hơn (FULL −2,28pp, IS −6,12pp), MaxDD xấu hơn (−19,9% vs −18,3%), Calmar thấp hơn rõ rệt
(1,36 vs 1,60 FULL). OOS CAGR nhích lên nhẹ (+1,17pp) nhưng đổi bằng MaxDD xấu hơn 2,4pp và Calmar
thấp hơn (1,65 vs 1,80) — không phải cải thiện ròng.

**Cơ chế thua**: pha loãng 1/3 vốn vào 1 book có MaxDD tự thân cao hơn nhiều (ConvergePort chuẩn
gốc MaxDD −40,6%/−46,1% full-sample, so với BAL+LAG combined −18,3%) và hiệu quả sử dụng vốn thấp
hơn (chỉ đầu tư khi có double-confirm, cap 0,20/tên nên chỉ 5 tên max được deploy full, phần còn
lại ngồi cash ngoài NEUTRAL) — pha loãng KHÔNG BÙ ĐƯỢC bằng phần CAGR tăng thêm, vì BAL+LAG kết
hợp vốn đã là 1 cặp bổ trợ hiệu quả (BAL thắng khi thị trường xác nhận, LAG thắng khi thị trường
chưa xác nhận).

→ **Cấu trúc "1/3 tĩnh mọi state" bị bác bỏ bởi data.** Câu trả lời thật nằm ở Phần C (C1/C2):
DC chỉ đáng thay thế MỘT PHẦN LAG, và CHỈ trong BULL — không phải 1/3 cố định mọi lúc.
