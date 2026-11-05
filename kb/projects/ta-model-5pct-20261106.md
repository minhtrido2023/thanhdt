# Model kỹ thuật định lượng ±5% bổ trợ Livermore (user yêu cầu 06/11/2026 00:09 ICT)
- Deal: pattern → mua → bán được từ CHIỀU T+2 → chốt +5% / cắt lỗ −5%; chỉ mã thanh khoản cao (universe_pit + sàn ADV60).
- Job: Taylor_20261105_171103 (opus, timeout 4h), thư mục `agents/Taylor/research/ta_model_5pct_20261106/`. PAPER-ONLY.
- Bước kế khi xong: quant-skeptic phản biện → nếu CONFIRMED mới bàn ghép với Livermore (Livermore khoá dự báo TRƯỚC, rồi mới xem điểm model; model DISPLAY-ONLY). NO-GO là kết quả hợp lệ.
- Bối cảnh: bài thử Livermore 100 chuỗi 55/100, Brier 0,2507 (`livermore_stock_battery_20261105/REPORT.md`).

## KẾT QUẢ 06/11/2026 — NO-GO (Taylor_20261105_171103, 72 trial, DSR 0,00, PBO 0,086)
- 0/72 cấu hình có lợi suất ròng > 0 ở slippage 0,2%/chiều; hoà vốn win-rate 56,0% (s=0,2%), P(+5% trước −5%) tốt nhất 51,9%. Vào ngẫu nhiên cùng bộ lọc: 43–46% (nền DƯỚI 50%).
- BRK/PB20 hơn ngẫu nhiên +1–3pp P(TP) nhưng CI chứa 0; SQZ/OSB/FTD/PB50 thua ngẫu nhiên. Thanh khoản cao hơn không cải thiện. Phần "thắng" đi theo năm thị trường (beta).
- Calibration OOS: Brier 0,2501 vs climatology 0,2490 (BSS −0,5%) ⇒ không có điểm số nào đáng đưa cho Livermore. Mốc đúng để Livermore vượt = Brier climatology ~0,249, không phải 0,25.
- Không skeptic (không có gì để wire). Không pin registry. Báo cáo: `agents/Taylor/research/ta_model_5pct_20261106/REPORT.md`.
- Hàm ý Livermore: nếu cần tầng định lượng, chỉ "thẻ tham chiếu" tần suất nền hiện SAU khi Livermore khoá dự báo; Livermore chỉ coi là có kỹ năng khi BSS vs climatology >0, CI không chứa 0, ≥~100 dự báo độc lập theo ngày.
