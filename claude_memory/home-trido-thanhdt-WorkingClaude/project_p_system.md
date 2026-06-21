---
name: P-system definition
description: P-system là biến thể của H-system với allocation cao hơn, phù hợp danh mục dài hạn rủi ro cao hơn. Chờ MCP simulation hỗ trợ dynamic allocation để backtest đầy đủ trên cổ phiếu.
type: project
originSessionId: 637d3857-e32a-46ff-8dc2-9739c4574bd9
---
## P-system — High-Deployment Variant của H-system

**Mục đích:** Danh mục dài hạn (horizon ≥5 năm), chấp nhận MaxDD cao hơn (-30%) để đổi lấy deployment rate cao hơn (81% vs 66%), giảm tiền idle.

### Allocation table

| State   | H-system (original) | P-system (new) | Thay đổi |
|---------|---------------------|----------------|----------|
| CRISIS  | 0%                  | 0%             | Giữ nguyên — bảo vệ tối đa |
| BEAR    | 20%                 | **50%**        | +30pp — BEAR thường là điều chỉnh tạm thời |
| NEUTRAL | 70%                 | **85%**        | +15pp — chiếm 77% thời gian, lever chính |
| BULL    | 100%                | 100%           | Giữ nguyên |
| EX-BULL | 130%               | **120%**       | -10pp — giảm nhẹ margin |

### Backtest results (VNINDEX NAV simulation, since 2011)

| System    | CAGR | Sharpe | MaxDD  | Calmar | AvgDep |
|-----------|------|--------|--------|--------|--------|
| H-system  | 8.5% | 0.70   | -22.3% | 0.38   | 66.4%  |
| P-system  | 8.5% | 0.61   | -32.5% | 0.26   | 81.4%  |
| Buy & Hold| 9.2% | 0.56   | -45.3% | 0.20   | 100%   |

**Lưu ý backtest:** Chạy trên VNINDEX index (không phải cổ phiếu), không bao gồm BearDvg gate → CAGR thấp hơn documented H-system (12.1%). Comparison H vs P vẫn valid (cùng base).

### Profile phù hợp

- Nhà đầu tư chịu được drawdown tối đa -30 đến -35%
- Horizon đầu tư ≥ 5 năm
- Muốn giảm tiền idle (avg 81% deployed vs 66% của H-system)
- Chấp nhận Calmar thấp hơn (0.26 vs 0.38) để đổi lấy deployment cao hơn

### Trạng thái

**Chờ backtest đầy đủ** trên cổ phiếu khi MCP simulation hỗ trợ dynamic allocation ratio theo thời gian. Hiện MCP chỉ hỗ trợ fixed allocation.

**Why:** P-system ra đời từ phân tích: tăng BEAR/NEUTRAL allocation không cải thiện CAGR trên VNINDEX index (đã bão hòa), nhưng với danh mục cổ phiếu có alpha thì deployment cao hơn = alpha được khai thác nhiều hơn.
**How to apply:** Khi MCP simulation hỗ trợ dynamic allocation, backtest P-system với stock universe (ticker_prune hoặc ticker_1m) để đo alpha so với H-system.
