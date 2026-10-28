# Luật lô cổ phiếu quyền mua — LAG (user chốt 22/10/2026 09:40 ICT, phương án A)

- Câu hỏi N1 (audit `agents/Taylor/research/lag_rights_audit_20261022/B2b_B3_park_exit.md`): entry_date của lô cổ phiếu từ quyền mua. User chọn **A — kế thừa entry_date gốc** (không tính 25 phiên mới từ ngày về tài khoản).
- Hệ quả: lô quyền thoát cùng hạn T+25 của vị thế gốc; vì chưa niêm yết/chưa bán được nên ở trạng thái khoá và bán ở **phiên đầu tiên được phép bán**. Kèm quy tắc: user khai riêng từng account số quyền THỰC SỰ mua (mua tay, có thể không đủ).
- N4 (legal-vn 22/10): cổ phiếu quyền mua chờ ghi nhận KHÔNG vào cơ sở hưởng quyền của đợt cổ tức khác tới khi VSDC ghi có.
- Triển khai N1: sau khi job `Taylor_20261022_022942` (X1,X2,X3,N2,N3) merge, tránh xung đột file (daily_nav_snapshot / portfolio_status / auto_exit_inject).
