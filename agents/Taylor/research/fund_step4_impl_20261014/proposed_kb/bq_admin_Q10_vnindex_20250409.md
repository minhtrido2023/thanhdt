# Gửi bq_admin — hàng VNINDEX 2025-04-09 sai (Q10, user chốt mặc định 2026-10-14: báo + sửa registry, KHÔNG tự sửa BQ)

**Bảng:** `tav2_bq.ticker` (và các bảng mirror cột `VNINDEX` dẫn xuất từ nó), hàng `ticker='VNINDEX'`, `time=2025-04-09`.
**Hiện tại:** `Price` = `Close` = **1.132,79** — trùng đúng giá đóng cửa 2025-04-08 (lặp phiên trước).
**Đúng:** **1.094,30** (DNSE chart-api `services.entrade.com.vn/chart-api/v2/ohlcs/index?symbol=VNINDEX`, phiên 09/04/2025 — ngày
thị trường giảm mạnh sau thông báo thuế quan Mỹ). Lệch 3,5%.
**Ảnh hưởng:** mọi tỉ suất VN-Index có mốc hoặc điểm cuối đúng 2025-04-09; phiên 2025-04-10 tính từ hàng này cũng sai.
Không ảnh hưởng số 2026 của báo cáo quỹ. Chuỗi VN-Index có cổ tức mới (`vnindex_total_return.py`) đã có cổng G2 đối chiếu
DNSE nên KHÔNG dùng hàng này mà không báo lỗi.
**Phụ:** trên 3.151 phiên chung từ 2014 còn 58 phiên lệch DNSE > 0,05% (phần lớn phiên cuối tháng 2016–2017 DNSE làm
tròn số nguyên; vài phiên 0,3–0,5% năm 2014/2015/2018 chưa điều tra) — danh sách: 
`mike/agents/Taylor/research/fund_step4_20261014/out_tr_checks.txt`.
**Đề nghị:** sửa hàng 2025-04-09 (Price, Close, và các cột dẫn xuất phụ thuộc: MA/RSI/… của VNINDEX nếu tính từ Close) rồi
báo lại để Taylor đo lại và gỡ ghi chú trong `kb/data_registry/price-volume/vnindex_mirror_col.md`.
