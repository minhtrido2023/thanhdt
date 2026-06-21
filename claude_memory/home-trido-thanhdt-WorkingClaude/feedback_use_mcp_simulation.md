---
name: Dùng MCP simulation để backtest, không dùng simulation_email.py
description: Khi cần backtest kết quả gợi ý, luôn dùng MCP simulation thay vì simulation_email.py
type: feedback
originSessionId: afd1283e-9ed8-4ec5-8a51-488c813fe806
---
Luôn dùng MCP simulation (mcp__simulation__simulation_v1_6_webui_submit) để backtest các kết quả gợi ý. Không dùng simulation_email.py cho mục đích này.

**Why:** simulation_email.py kém hiệu quả so với MCP thực tế — số deals ít hơn nhiều (93 vs 771), CAGR thấp hơn đáng kể (24% vs 34%) do thiếu cơ chế add-to-position và nhiều khác biệt logic khác.

**How to apply:** Khi user muốn test một thay đổi filter/weight/parameter, submit job qua MCP simulation v1.6 với profile email và chờ kết quả. simulation_email.py chỉ dùng cho mục đích tham khảo/debug nội bộ nếu có yêu cầu riêng.
