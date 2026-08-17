📊 **EOD Trading Report — SpaceX (2026-08-17)**
✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
💸 Phí/thuế THẬT theo statement: 8,844đ phí + 0đ thuế trên 10.1M giá trị khớp (= 0.0880% giá trị).

Tổng lệnh: **1** (1 mua / 0 bán) | Khớp đủ: 1 | Khớp một phần: 0 | Chưa khớp: 0

• MUA TV1: 500/500 (100%) @ 20,100đ → 10.1M
   ↳ DCF: NOT_COMPUTED (SOTP/asset-backed deep-value — không dùng LAG/BAL gate) → thay thế: 8L (fallback rộng): 8L rating 1/5, earnings yield 28.7% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
   ↳ DD TV1 (data 2026-08-14): ⚠ thanh khoản mỏng (ADV3T 757 tr/phiên < sàn 2 tỷ — sàn CỨNG của book LAG/BAL từ 2026-08-10; lệnh này tới được đây nghĩa là nó KHÔNG đi qua gate đó) · ⚠ universe_pit: n/a (không đọc được) · lệnh dự kiến 10 tr = 1% ADV
   ↳ FA: ROE5Y 23.2% · ROE_Min3Y 21.7% · FSCORE 5 · D/E 1.18 · PE 3.48

ℹ️ _DCF là lăng kính THAM KHẢO (không tham gia quyết định mua/bán): mô hình gộp doanh nghiệp thành 1 dòng tiền FCFE với 1 mức tăng trưởng + 1 lãi suất chiết khấu, rất nhạy với 2 tham số này. Với doanh nghiệp ĐA NGÀNH/HOLDING (mảng khác nhau, kinh tế + rủi ro khác nhau — cần định giá sum-of-the-parts) kết quả có thể KHÔNG CÓ Ý NGHĨA dù trông chính xác; các tên đã biết được đánh dấu '⚠ đa ngành', nhưng danh sách duy trì tay nên không đầy đủ. Nhóm tài chính (ngân hàng/bảo hiểm/chứng khoán) bị loại hẳn → NOT_COMPUTED. Khi NOT_COMPUTED, report nối thêm LĂNG KÍNH THAY THẾ theo ngành (Gordon P/B ngân hàng, P/B chứng khoán, EV/EBITDA cảng-viễn thông, P/B trough vận tải biển, 8L fallback) — độ tin cậy ghi rõ trong ngoặc vuông, cũng THUẦN THAM KHẢO._
ℹ️ _Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

**Tổng giá trị giao dịch: 10.1M / kế hoạch 10.3M (97%)**

💰 **NAV 2026-08-17: 958,129,863 VND** (-811,045 VND, -0.08% so với hôm trước)
   Cổ phiếu 848,146,000 · Tiền mặt 109,983,863 · Nợ margin 0
   Từ go-live: -41,870,137 VND (-4.19%)
   ℹ️ verify_account_snapshot (cross-check journal) rc=3 — NAV vẫn tính từ vị thế broker thật; cần xem cost-basis/đối soát riêng.
