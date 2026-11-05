# Model kỹ thuật định lượng ±5% bổ trợ Livermore (user yêu cầu 06/11/2026 00:09 ICT)
- Deal: pattern → mua → bán được từ CHIỀU T+2 → chốt +5% / cắt lỗ −5%; chỉ mã thanh khoản cao (universe_pit + sàn ADV60).
- Job: Taylor_20261105_171103 (opus, timeout 4h), thư mục `agents/Taylor/research/ta_model_5pct_20261106/`. PAPER-ONLY.
- Bước kế khi xong: quant-skeptic phản biện → nếu CONFIRMED mới bàn ghép với Livermore (Livermore khoá dự báo TRƯỚC, rồi mới xem điểm model; model DISPLAY-ONLY). NO-GO là kết quả hợp lệ.
- Bối cảnh: bài thử Livermore 100 chuỗi 55/100, Brier 0,2507 (`livermore_stock_battery_20261105/REPORT.md`).
