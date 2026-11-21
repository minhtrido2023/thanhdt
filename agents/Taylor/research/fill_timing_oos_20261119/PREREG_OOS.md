# PREREG ADDENDUM — fill_timing HYBRID OOS THẬT (job Taylor_20261119_051519) — viết TRƯỚC khi tính
Kế thừa NGUYÊN VẸN `../fill_timing_recheck_20261119/PREREG.md` (md5 93638a29cfc701d0d04b7986492edd3e) và `engine.py` (import nguyên, không sửa). Chưa qua quant-skeptic. Chỉ đọc production.

## Dữ liệu (đã đo trước khi viết)
- Kéo mới: vnstock VCI `Quote(tk).history(interval="1m")`, 16 mã TICKERS của workspace/fetch_intraday_1m.py, 2026-06-12→2026-11-18, ghi `data/intraday_1m_ext_20261119/` (md5 trong MD5SUMS_data.txt). Mỗi mã 111 phiên (gồm 06-12) ⇒ **số phiên OOS mong đợi = 110** (06-15→11-18); 0 lỗi/retry (fetch_failures.json rỗng).
- Kiểm khớp ngày chồng 06-12: timestamp + volume KHỚP 100% mọi bar ở 16 mã. open/close: 5 mã (DXG,GEX,HPG,MSN,STB) khớp tuyệt đối; 11 mã lệch bởi **hệ số nhân hằng** trong ngày (VCI trả giá điều chỉnh ngược theo corp action sau 06-12: vd PHR ×0,5427, PVD ×0,5993, D2D ×0,831; dải trong-ngày chỉ do làm tròn tick). Diễn giải: không phải lệch dữ liệu; metric là TỶ SỐ trong cùng ngày nên bất biến theo hệ số nhân (đúng như PREREG gốc). Ghi rõ: chỗ này là diễn giải của tôi về lệnh "lệch thì dừng" — tiêu chí khớp áp dụng = tỷ số new/old hằng trong ngày (±0,2%) + timestamp/volume khớp; kiểm thêm metric buy/sell ngày 06-12 giữa bản cũ và mới (self-check).
- Rủi ro: làm tròn tick trên giá đã điều chỉnh thấp (PVD ~18, PHR ~35) thêm nhiễu ≤ ~3 bps/bar, không thiên lệch có hệ thống; báo trong caveat.
## Thiết kế (KHÔNG đổi)
- Lịch, giá fill=open bar 1m ≥ nhãn, benchmark = open bar đầu, N=phiên (trung bình cắt ngang mã), CI95 bootstrap khối tuần ISO 10000 lần seed 0, nhóm ngày giảm = median cắt ngang close-to-close <0 (ex-post), lọc ticker-ngày <50 bar — GIỮ NGUYÊN engine.py (import `load_1m`,`boot`,`summarize`). prev_close của phiên 06-15 lấy từ bar 06-12 trong file mới (cùng hệ điều chỉnh).
- Cửa sổ OOS = phiên > 2026-06-12 (kỳ thị trường giảm). Báo: BUY/SELL all / ngày giảm / ngày tăng; từng block BUY 11:00,11:15,13:00,13:15,13:30 và SELL 09:30,09:45,10:00 (09:15 = chính open). Panel thanh khoản thấp: dùng ĐÚNG 5 mã của recheck (từ ticker_day_1m.csv cũ).
- Panel 15m 335 mã KHÔNG mở rộng (task chỉ kéo 16 mã 1m).
## Tiêu chí (như cũ)
- PASS BUY: mean ≤ −5 bps, CI95 trên <0, ngày giảm mean <0. PASS SELL: mean ≥ +5 bps, CI95 dưới >0, ngày giảm >0.
- **ROLLBACK ĐỀ XUẤT khi mean BUY-vs-open > +22 bps** (CHỈ khi vậy). Còn lại: GIỮ nếu PASS BUY; INCONCLUSIVE/CHƯA ĐỦ N nếu n_days<~60 hoặc CI cắt 0.
- Trong 110 phiên ≈ 22 tuần ⇒ CI tuần thô; nêu rõ.
## Self-check
- Control: so buy/sell/p-block ngày 06-12 per ticker giữa data cũ và mới (|Δ| kỳ vọng ≲3 bps, 5 mã khớp 0 nếu giá nguyên); engine chạy trên cửa sổ A cũ tái lập số RECHECK (BUY −18,3 phiên A) không cần thiết vì engine bất biến — thay bằng chạy `engine.load_1m` trên data cũ ngày 06-12.
- Journal fill thật (phụ): lọc account_no từng account; chỉ mô tả, không suy edge nếu N nhỏ.
