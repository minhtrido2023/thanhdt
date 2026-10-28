📈 **Báo cáo giao dịch ngày — SpaceX (2026-10-26)**

─────────────────────────────────────────────────
📋 **TÌNH TRẠNG DANH MỤC — SpaceX (2026-10-26)**
Chiến lược: **V2.4** | Regime: **NEUTRAL** (DT5G) | Park target: **0%** idle cash
⚠️ NAV hôm nay (2026-10-26) CHƯA có trong nav_history_SpaceX.csv lúc chạy mục này — hiện NAV gần nhất (2026-10-23): **968.9M**, đổi so với ngày trước đó **-0.04%** (KHÔNG PHẢI thay đổi của hôm nay). Số NAV chính thức hôm nay xem mục 💰 NAV cuối report (daily_nav_snapshot.py, chạy sau mục này).
Gate DT5G: 🟢 BÌNH THƯỜNG · candidate CRISIS 14/25 (56%, còn 11 phiên để commit, base giữ từ 2026-10-07, committed NEUTRAL) · P(CRISIS xác nhận|k=14)≈73% [50–93%, n=15] ⚠ mẫu mỏng, tham khảo  [dữ liệu tới 2026-10-26]
   ↳ Nền xấu 20 phiên liền từ 29/09 (6 BEAR + 14 CRISIS, đổi qua lại 1 lần → bộ đếm reset, vẫn NEUTRAL) · VNINDEX −1,0% từ đầu đợt · ngưỡng xem lại: ≥15 phiên và VNINDEX ≤−5,0% — chưa chạm
Value Radar: 🟢 23.2 RẺ (phân vị 10 năm) · P/E 11.19 (p7) · P/B 1.87 (p23) · spread EY−CCTG 12T +1.54pp (p40)  [dữ liệu tới 2026-10-26]
─────────────────────────────────────────────────

**Cơ cấu danh mục**

| Sleeve | Giá trị | % NAV | Lãi/Lỗ CK | Ghi chú |
|--------|--------:|------:|----------:|---------|
| Trứng vàng | 873.2M | 90.1% | — | DNSE bond-like (off-book) |
| Cash | 3.5M | 0.4% | 0% | Idle |

**Corp Action — 7 ngày tới** (mã đang giữ)
Không có corp action trong 7 ngày tới trên mã đang giữ.

**Cờ theo dõi**
- PARK: rổ hiện hành chốt 2026-08-05 (chu kỳ ~quý, kế tiếp ~2026-12-01 (ước tính)).
- LAG: 2 candidate đang trong cửa sổ upcoming (chưa vào lệnh).

✅ Đã đối chiếu số liệu khớp lệnh trong ngày với công ty chứng khoán, khớp đúng.

✅ Đã đối chiếu độc lập với sao kê giao dịch của công ty chứng khoán, số khớp lệnh trùng khớp, không phát sinh giao dịch ngoài kế hoạch.
📉 **Broker xác nhận KHỚP THIẾU so với kế hoạch** — chưa đạt mục tiêu, KHÔNG được đọc là "đã mua đủ" (§27):
  • SCL (mua): chỉ khớp 800/1,100 đặt (73%) — phần thiếu 300cp
💸 Phí/thuế THẬT theo statement: 92,785đ phí + 0đ thuế trên 98.0M giá trị khớp (= 0.0946% giá trị).

Tổng lệnh: **3** (3 mua / 0 bán) | Khớp đủ: 2 | Khớp một phần: 1 | Chưa khớp: 0

| Chiều | Lệnh | Khớp đủ | Khớp thiếu | Chưa khớp | Giá trị |
|-------|:----:|:-------:|:----------:|:---------:|--------:|
| Mua   | 3 | 2 | 1 | 0 | 98.0M |

**Chi tiết đáng chú ý:**
  • MUA HT1: 2,700/2,700 (100%) @ 13,469đ → 36.4M
     ↳ 🟢 DCF: CHEAP (giá trị hợp lý ~25,652đ vs giá 13,550đ, MoS +47.2%, robust)
     ↳ DD HT1 (data 2026-10-23): thanh khoản OK (ADV3T 3.04 tỷ/phiên) · lệnh dự kiến 37 tr = 1% ADV
     ↳ FA: ROE5Y 4.0% · ROE_Min3Y 0.3% · FSCORE 8 · D/E 0.46 · PE 12.91
  • MUA VPB: 1,500/1,500 (100%) @ 23,910đ → 35.9M
     ↳ DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 1.20 vs hợp lý 1.22 (ROE5Y 14.8%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)]
     ↳ DD VPB (data 2026-10-23): thanh khoản OK (ADV3T 369.60 tỷ/phiên) · lệnh dự kiến 36 tr = 0% ADV · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-09-18
     ↳ FA: ROE5Y 14.8% · ROE_Min3Y 8.4% · FSCORE 4 · D/E 7.05 · PE 7.73
  • MUA SCL: 800/1,100 (73%) @ 32,275đ → 25.8M
     ↳ DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 9.8% (1/PE) [FALLBACK — ngưỡng lọc chất lượng + trục value, không phải giá trị hợp lý]
     ↳ DD SCL (data 2026-10-23): thanh khoản OK (ADV3T 4.06 tỷ/phiên) · lệnh dự kiến 34 tr = 1% ADV
     ↳ FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.99 · PE 10.26

ℹ️ _DCF là lăng kính THAM KHẢO (không tham gia quyết định mua/bán): mô hình gộp doanh nghiệp thành 1 dòng tiền FCFE với 1 mức tăng trưởng + 1 lãi suất chiết khấu, rất nhạy với 2 tham số này. Với doanh nghiệp ĐA NGÀNH/HOLDING (mảng khác nhau, kinh tế + rủi ro khác nhau — cần định giá sum-of-the-parts) kết quả có thể KHÔNG CÓ Ý NGHĨA dù trông chính xác; các tên đã biết được đánh dấu '⚠ đa ngành', nhưng danh sách duy trì tay nên không đầy đủ. Nhóm tài chính (ngân hàng/bảo hiểm/chứng khoán) bị loại hẳn → NOT_COMPUTED. Khi NOT_COMPUTED, report nối thêm LĂNG KÍNH THAY THẾ theo ngành (Gordon P/B ngân hàng, P/B chứng khoán, EV/EBITDA cảng-viễn thông, P/B trough vận tải biển, 8L fallback) — độ tin cậy ghi rõ trong ngoặc vuông, cũng THUẦN THAM KHẢO._
ℹ️ _Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/cờ bất thường/FA thô/định giá). KHÔNG phải ngưỡng lọc chặn lệnh; số từ bq_cache local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, vẫn thực thi)._

**Tổng giá trị giao dịch: 98.0M / kế hoạch 106.9M (92%)**

⚠️ Không đọc được positions broker (SpaceX): HTTP 500: authentication failed
❌ [2026-10-26] Không lấy được vị thế broker — KHÔNG tính NAV (tránh đăng số thiếu vị thế).
