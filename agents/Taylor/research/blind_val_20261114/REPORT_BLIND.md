# PAT — định giá MÙ GIÁ (lượt riêng) · 14/11/2026 · tác nhân độc lập stateless (general-purpose/opus), Mike lưu giúp (agent bị chặn ghi .md)
Khoá giả định: assumptions_blind.md md5 `52883de26cd4b176ef181025fc259afd`, 2026-11-14T13:08:12Z (20:08 ICT) TRƯỚC khi chạy mô hình (13:09:21Z). Truy vấn BQ ghi ở query_log.md: chỉ ticker_financial (cột cơ bản), ticker (time, Volume), commodity_prices. Không thấy giá/PE/PB/vốn hoá (không BREACH). Đọc ngành có nhắc thư mục DD PAT khác; agent không mở.
## Kết quả (TRƯỚC chiết khấu thanh khoản)
- **Giá trị kỳ vọng có trọng số: 86.990 đ/cp (EV 2.174,7 tỷ; gồm tiền ròng 415,4 tỷ ≈ 16.600 đ/cp)**; vùng 0,85–1,15× = 73.900–100.000.
- Kịch bản (EBIT hoạt động 2027): xấu 160 tỷ → 64.500 (p=0,30) · cơ sở 245 tỷ → 89.500 (p=0,50) · tốt 330 tỷ → 114.500 (p=0,20). Cơ sở EBIT: run-rate quý (Q3/26 quy năm 215; 2024 = 249; TTM 274; 2025 = 339). Xác suất lấy từ dự báo khoá trước của người đọc ngành (P(P4<23k sau 12T)=0,32; P(3 nhà máy tuyển chạy ≥80%)=0,30).
- r = 13,5% (lãi huy động 12T hiệu dụng 7,40% = điểm neo ⇒ Δ=0); g = 2% (công suất cố định). Độ nhạy β=1: ±50bp → −2,9%/+3,2%; ±100bp → −5,7%/+6,7%.
- Hai nền: V_dài 86.990, V_ngắn 98.600 (LNST chuẩn hoá 291,1 tỷ, ROE 44,3%); D = 0,125.
- Moat NARROW (ROIC hoạt động ~85–100% vs Ke 13,5% nhiều năm, nhưng nguồn quặng thuộc mẹ, siêu lợi nhuận bị chia qua giá chuyển nhượng): không thưởng/không trừ; độ nhạy giá trị cuối ×0,8 → −5,3%.
- FCFE = EBIT × (1 − thuế ưu đãi 5% → 10% → 20%) × (1 − 6% trích quỹ KTPL) − g × VLĐ 53 tỷ; capex = KH; thuế XK P4 10% (2026) → 15% (01/01/2027) theo EY/NĐ 199 chỉ trên phần xuất khẩu trực tiếp (~250 tỷ/năm, ước lượng).
## Độ nhạy rủi ro (KHÔNG nằm trong tâm)
Pháp lý WARNING (thuế 20% ngay + truy thu 210 + môi trường 100, ước lượng) −20,9% (68.800) · trừ 42,6 tỷ cầm cố cho công ty thành viên −2,0% · trừ toàn bộ 441,6 tỷ cầm cố −20,6% · đất thuê hết ~2034 không gia hạn −29,6% (61.200) · g=0% −10,3%, g=3% +6,6%.
## Thanh khoản (để Mike áp sau)
Khớp trung vị 6.600 cp/phiên (6T; 17/129 phiên không khớp), 8.250 cp/phiên (3T; 0/63). Giá trị sau chiết khấu 5/10/20%: **82.600 / 78.300 / 69.600**.
## 5 điều cần kiểm nhất
1. Đơn giá bán P4 cho DLC so với giá xuất khẩu ròng thuế, và giá quặng/cốc mua từ DLC (quyết định xấu vs cơ sở). 2. Sản lượng Q4/26–2027 (quặng loại III thu hồi chỉ đủ cầm chừng đến hết T11/2026; quyết định dùng 3,53 triệu tấn quặng tồn). 3. Cổ tức sau 30/09: KH 90% chưa có nghị quyết; nếu ngày chốt quyền trước 14/11 phải trừ ~225 tỷ (9.000 đ/cp) khỏi tiền ròng; dư nợ công ty thành viên mà 42,6 tỷ bảo đảm. 4. Vụ án: thu hồi/truy thu ưu đãi thuế, hoàn nguyên đất thuê chưa trích lập, cơ sở các ngoại trừ của UHY. 5. Hạn thuê đất KCN và cam kết cung quặng.
## Tự kiểm của agent
12/12 kiểm tổng khớp BCTC; chạy lại mô hình 2 lần + 1 lần bỏ TZ cho csv giống hệt (md5 6dd7b761…); sau khoá chỉ sửa ngưỡng một dòng kiểm trong model_blind.py (273,72→273,7), không sửa giả định.
