# So sánh Kaffa (hệ thống cũ) vs ARIA — 2026-09-10

User yêu cầu đọc email "Stock report on September 10, 2026 by Kaffa" (Gmail, thread
`1a08abb3508c99c2`, gửi 09-10 09:51 ICT) và đối chiếu với ARIA để tìm điều đáng học/nghiên cứu.

## Phát hiện nền tảng
Kaffa KHÔNG phải hệ thống khác — `filter.json` của ARIA hôm nay vẫn dùng 16/17 tên filter y hệt
Kaffa (`_UnderBV`, `_BuySupport`, `_BullDvg`, `_Conservative`, `_DividendYield`, `_SurpriseEarning`,
`_CashCowStock`, `_SuperGrowth`, `_TradingValueMax`, `_RSILow30`, `_BKMA200`, `_TrendingGrowth`,
`_VolMax1Y`, `_TL3M`...). ARIA (V2.4 BAL/LAG/custom30V) là bản đã siết lại sau backtest/quant-skeptic/
DSR-PBO xuống còn 2 book cốt lõi — không phải build lại từ đầu.

## 4 thứ Kaffa có mà ARIA thiếu (đã đối chiếu `eod_trading_report.sh`, `dna_report.py`,
`score_live_signals.py`, `newdeals_daily_report.py`, `market_overheat.md`) — QUYẾT ĐỊNH ƯU TIÊN:

1. **"Hit Details" — formula + giá trị factor thật in kèm mỗi tín hiệu bắn ra.** ƯU TIÊN CAO —
   công cụ audit/quan sát thuần, KHÔNG phải signal mới, không cần quant-skeptic gate. Khớp thẳng
   coding_guidelines §29 (chẩn đoán phải trích bằng chứng cầm tay). Chưa dispatch — làm sau khi
   xong việc #2 dưới đây (session dài, ưu tiên 1 mạch việc/lượt).
3. **"Monitor" — null-indicator theo từng mã mỗi ngày.** ƯU TIÊN TRUNG — bundle cùng #1 khi làm
   (cùng loại: observability, chi phí thấp).
2. **Bảng RS sector rotation (ICB, Top ticker + Top-5-sector).** GỘP vào nghiên cứu correlation-
   cluster bên dưới (cùng họ ý tưởng "nhóm cổ phiếu di chuyển cùng nhau").
4. **Headline "Chain + Stable for N sessions".** ƯU TIÊN THẤP — dữ liệu đã có sẵn
   (`dna_report.build_dt_gate_line()`), chỉ là UX. Bỏ qua trừ khi rảnh.

**Không đáng học:** AI-score đơn (ARIA đã có `score_live_signals.py`, RandomForest, phức tạp hơn).
Buffett Indicator (đã có trong `market_overheat.md`, chỉ chưa lộ diện hàng ngày).

## Ý tưởng MỚI của user (2026-09-10 22:03 ICT) — correlation-cluster / "họ cổ phiếu"

User quan sát: có nhóm cổ phiếu tương quan cao dù KHÁC ICB sector chính thức (ví dụ nêu: nhóm
VIX, nhóm VIN/Vingroup, nhóm Masan) — nghi ngờ do cùng dòng vốn/chủ sở hữu, không phải cùng
ngành. Muốn biết có dùng được làm edge bổ sung không (rotation giữa nhóm mạnh/yếu theo giai đoạn
thị trường).

**Đánh giá của Mike:**
- **Genuinely mới** — KHÔNG trùng 20 sector sweep đã đóng (`kb/KNOWLEDGE.md` §7): tất cả 20 sweep
  dùng phân loại ICB CHÍNH THỨC (kể cả #20 "Holding company/conglomerate SOTP" — đó là lens ĐỊNH
  GIÁ theo SOTP, không phải cụm tương quan giá). Ý tưởng user là trục KHÁC: correlation-based,
  không cần ICB.
- **Nhưng 2 tiền lệ mạnh phải tôn trọng trước khi backtest:**
  1. Rule 3 của sector sweep giữ vững 20/20 lần: MỌI cách gộp nhóm trong hệ thống này (dù trục
     nào) cho tới nay chỉ có giá trị LÀM LENS/context, KHÔNG PHẢI BOOK độc lập sinh lời.
  2. **Quan trọng nhất, tìm ra CÙNG NGÀY (AMH, job Taylor_20260910_131906/B):** momentum giá cổ
     điển (SIGNAL_V11, lõi book BAL) đã CHẾT CẤU TRÚC sau 2020 ở MỌI ô điều kiện đã test (IS 8/8
     dương → OOS 8/8 ≈0, không ô nào cứu được). Rotation theo cụm tương quan về bản chất là MỘT
     dạng momentum/relative-strength (mua nhóm đang mạnh, né nhóm đang yếu) — CÙNG LỚP tín hiệu
     với cái vừa chết, TRỪ KHI cơ chế edge đến từ thứ khác giá (dòng vốn/cổ đông lớn/sở hữu chéo),
     không phải tự tương quan giá đơn thuần.
- **Kết luận:** đáng nghiên cứu, nhưng phải qua bước RẺ xác nhận tiền đề TRƯỚC khi backtest —
  tránh lặp lỗi "recompute đúng số nhưng sai phương pháp" (bài học AMH t_eff REFUTED cùng ngày).

**Kế hoạch 3 bước (chỉ bước 0 được duyệt tối nay, market đóng cửa):**
- **Bước 0 (đã dispatch, job xem bus)**: xác nhận tiền đề — tương quan trong 2 nhóm known-good
  (Vingroup: VIC/VHM/VRE; Masan: MSN/MCH/MML/MSR) có thật sự CAO HƠN tương quan trung bình cùng
  ICB sector hay pair ngẫu nhiên không, VÀ quét toàn universe tìm cụm tương quan cao KHÔNG giải
  thích được bằng ICB (data-driven, không đoán thành viên "họ VIX" — tránh tự bịa quan hệ sở hữu
  chưa xác minh, coding_guidelines §verify-real-facts). KHÔNG backtest ở bước này.
- **Bước 1 (chờ kết quả bước 0)**: nếu tiền đề đúng, pre-register hypothesis rõ ràng: cluster-RS
  phải sinh alpha NGAY CẢ trong giai đoạn hậu-2020 nơi momentum cá lẻ đã chết — đây là thanh chắn
  bắt buộc để không lặp lại đúng phát hiện âm tính vừa có.
- **Bước 2**: backtest đầy đủ walk-forward IS/OOS + DSR/PBO + quant-skeptic — CHỈ nếu bước 0-1 qua.

Job Taylor bước 0: xem bus topic `kaffa-correlation-cluster-premise-20260910`.
