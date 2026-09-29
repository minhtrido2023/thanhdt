⚠️ Trạng thái DT5G có thể là dữ liệu HÔM QUA (publisher chưa xác nhận xong lúc báo cáo này chạy) — xem lại trước khi dùng để quyết định. (chi tiết: as_of=2026-09-11 ≠ phiên gần nhất 2026-09-14)

📊 **EOD Trading Report — ZaloPay (2026-09-14)**
✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.

✅ Leg 3 (statement DNSE, độc lập với state/dnse_raw): số khớp trùng khớp state nội bộ, không có fill ngoài kế hoạch.
💸 Phí/thuế THẬT theo statement: 3,502đ phí + 0đ thuế trên 4.0M giá trị khớp (= 0.0880% giá trị).

Tổng lệnh: **1** (1 mua / 0 bán) | Khớp đủ: 1 | Khớp một phần: 0 | Chưa khớp: 0

• MUA TV1: 200/200 (100%) @ 19,900đ → 4.0M
   ↳ DCF: NOT_COMPUTED (SOTP/asset-backed deep-value — không dùng LAG/BAL gate) → thay thế: 8L (fallback rộng): 8L rating 1/5, earnings yield 29.0% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
   ↳ DD TV1 (data 2026-09-11): ⚠ thanh khoản mỏng (ADV3T 556 tr/phiên < sàn 2 tỷ — sàn CỨNG của book LAG/BAL từ 2026-08-10; lệnh này tới được đây nghĩa là nó KHÔNG đi qua gate đó) · lệnh dự kiến 4 tr = 1% ADV
   ↳ FA: ROE5Y 23.2% · ROE_Min3Y 21.7% · FSCORE 5 · D/E 1.18 · PE 3.45

ℹ️ _DCF là lăng kính THAM KHẢO (không tham gia quyết định mua/bán): mô hình gộp doanh nghiệp thành 1 dòng tiền FCFE với 1 mức tăng trưởng + 1 lãi suất chiết khấu, rất nhạy với 2 tham số này. Với doanh nghiệp ĐA NGÀNH/HOLDING (mảng khác nhau, kinh tế + rủi ro khác nhau — cần định giá sum-of-the-parts) kết quả có thể KHÔNG CÓ Ý NGHĨA dù trông chính xác; các tên đã biết được đánh dấu '⚠ đa ngành', nhưng danh sách duy trì tay nên không đầy đủ. Nhóm tài chính (ngân hàng/bảo hiểm/chứng khoán) bị loại hẳn → NOT_COMPUTED. Khi NOT_COMPUTED, report nối thêm LĂNG KÍNH THAY THẾ theo ngành (Gordon P/B ngân hàng, P/B chứng khoán, EV/EBITDA cảng-viễn thông, P/B trough vận tải biển, 8L fallback) — độ tin cậy ghi rõ trong ngoặc vuông, cũng THUẦN THAM KHẢO._
ℹ️ _Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

**Tổng giá trị giao dịch: 4.0M / kế hoạch 4.0M (100%)**

💰 **NAV 2026-09-14: 966,798,467 VND** (-14,214,304 VND, -1.45% so với hôm trước)
   Cổ phiếu 845,819,750 · Tiền mặt 81,974,059 · Nợ margin 0 · Trứng vàng 39,004,658
   Từ go-live: -33,201,533 VND (-3.32%)
🛰️ Gate DT5G: ✓ ổn định (NEUTRAL) · không có candidate đang track  [dữ liệu tới 2026-09-11]
🧭 Value Radar: 🟢 21.0 RẺ (phân vị 10 năm) · P/E 11.38 (p7) · P/B 1.91 (p28) · spread EY−tiết kiệm +1.99pp (p27)  [dữ liệu tới 2026-09-11]
  ↳ ⓘ thông tin bổ sung, CHƯA qua kiểm định đủ mạnh để dùng cho sizing (0/17 lăng kính qua đa kiểm định) — chỉ để đọc, không phải tín hiệu mua/bán.
💵 Spread định giá: 🔴 EY median 9.47% − lãi vay 12.5% = -3.03pp · chỉ hiển thị, không tác động sizing/gate  [dữ liệu tới 2026-09-11, 336/356 mã có PE>0]
🧲 CAP_SIGNAL advisory (2026-09-11): quiet | EM_dd60=-4.7% VNI_dd60=-4.4% DXY_mom60=-0.7% TNX=4.97 | N_clusters=0/10 — ADVISORY THAM KHẢO, KHÔNG phải tín hiệu mua/bán tự động.
