# PREREG pre-flight #5 — đảo chiều sau ngày giảm cực đoan (daily, 2014+)  [job Taylor_20261119_052908]
GHI CHÚ TRUNG THỰC: file này được viết SAU khi đã chạy 3 script thăm dò đếm cụm (pf_probe/pf2/pf3) — không phải trước. Thăm dò chỉ lấy
SỐ CỤM và SD cụm (không đọc mean excess); định nghĩa dưới đây là đúng những gì đã chạy. Không có phép thử thật nào được chạy.
Dữ liệu: data/bq_cache/ticker (Price chưa điều chỉnh làm giá tham chiếu t-1) + universe_pit.in_universe; GTGD>2 tỷ VND/ngày; không dùng ticker_prune.
Định nghĩa (3 trial, ≤6): D1 = close ≤ −6,4% và băng suy ra là ~7% (max|r| 250 phiên trước ∈[6,5%;7,25%]); D2 = r ≤ −7% mọi băng; D3 = băng 7% và r ≤ −5%.
Cụm = các ngày có ≥k sự kiện, gộp khoảng cách ≤7 ngày lịch (~5 phiên); k ∈ {1,10,20}. IS 2014–19 / OOS 2020+. Exit: Open(t+1)→Close(t+11) trừ VNINDEX.
Chi phí 0,097%/chiều + 0,1% thuế. Mục tiêu excess +1,5%/cụm (150 bps). Tiêu chí GO: ≥30 cụm/era, ≤6 trial, DSR≥0,95.
