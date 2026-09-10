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

## Bước 0 KẾT QUẢ (2026-09-10 22:15 ICT, job Taylor_20260910_150633)

Tiền đề CÓ THẬT nhưng KHÔNG đồng đều:
- **Vingroup** (VIC/VHM/VRE): xác nhận MẠNH, ổn định 2 cửa sổ (full-sample corr 0,561 pctl 99,5;
  recent252d 0,656 pctl 99,2 vs cap-matched control).
- **Masan** (MSN/MCH/MML/MSR): KHÔNG xác nhận full-sample (pctl 55,8 ≈ ngẫu nhiên), chỉ yếu+gần
  đây (pctl 87,8, 252 phiên) → premise YẾU, loại khỏi test chính.
- Quét data-driven toàn universe (352 mã) tìm ra 2 cụm MỚI mạnh hơn cả ví dụ user nêu:
  **Viettel-family** (CTR/VGI/VTP, pctl 97-99,5) và **PVN-family** (9 mã: BSR/GAS/OIL/PLX/PVB/
  PVC/PVD/PVS/PVT, pctl 99,9 — mạnh nhất, bền suốt 8 năm).
- 2 cụm khác = **method artifact** (không phải phát hiện thật): "financial beta chain" = Banks+
  Financial Services đã biết, bị tách 2 mã ICB trong data; "KCN real estate" = lỗi phân loại ICB
  (VGC gắn nhãn sai), không phải sở hữu chéo mới.
- So với sector sweep #20 (holding SOTP, đã đóng): KHÔNG trùng phương pháp, nhưng #20 đã cảnh báo
  TRƯỚC đúng các tên gần giống bằng cách khác — "discount KHÔNG mean-revert, LÀ TRAP, LENS-NOT-
  BOOK". Rule 3 giữ vững 20/20 sweep trước — base rate mạnh phải neo trước bước 1.

File đầy đủ: `mike/agents/Taylor/research/kaffa_correlation_cluster_20260910/`.

## User duyệt bước 1 (2026-09-10 22:25 ICT)

User xác nhận đã biết nhóm Viettel/dầu khí tương quan mạnh (quên nêu ví dụ ban đầu), và cho biết
hệ thống Kaffa cũ có ý định đánh giá lại tương quan ĐỊNH KỲ HÀNG THÁNG để tìm tín hiệu mới —
**ý hay, ghi lại làm việc CÂN NHẮC SAU** (không build cron ngay — chỉ đáng làm nếu bước 1/2 chứng
minh cluster-RS có alpha thật; xây lịch định kỳ cho một lens chưa chứng minh là early-optimize).

Bước 1 dispatch: chỉ PVN-family + Viettel-family (loại Masan + 2 cụm artifact). Pre-register
hypothesis + methodology TRƯỚC khi tính return (khoá thiết kế signal trước, tránh overfitting/
multiple-testing). Rào chắn bắt buộc: phải sinh alpha OOS hậu-2020 thật (không chỉ IS) — khớp
đúng thanh chắn AMH vừa tìm ra cùng ngày (momentum cá lẻ chết cấu trúc sau 2020 mọi ô test).
N=2 cụm — quá nhỏ cho công cụ thống kê thường, phải nói rõ giới hạn, dựa vào walk-forward +
lý luận nhân quả (sở hữu chung/dòng vốn) hơn là p-value đơn thuần.

## Bước 1 KẾT QUẢ — NO-GO (2026-09-10 22:32 ICT, job Taylor_20260910_152624)

Pre-reg: `Cluster_RS_200` (200d relative-strength vs VNINDEX) có dự báo fwd_3M CHÍNH cụm đó
(giả thuyết A: continuation)? GO cần CẢ HAI cụm: OOS corr dương + sign-consistent ≥5/7 năm.

- **PVN-family**: OOS corr **−0,357**, t(NW)=−2,16 (có ý nghĩa), sign-consistency 5/7 năm —
  nhưng **SAI CHIỀU**: âm = mean-reversion, không phải continuation đã pre-register. Giả thuyết
  B (mean-reversion) đã loại khỏi scope trước — Taylor KHÔNG tự mở rộng test đuổi theo (đúng kỷ
  luật, tránh multiple-testing bias).
- **Viettel-family**: OOS corr +0,073, t=0,64 (không ý nghĩa), sign-consistency chỉ 2/7 năm.

**Verdict: NO-GO, dừng, không làm bước 2.** Cả 2 cụm không đạt điều kiện GO. Ý nghĩa: momentum
cấp-cụm cùng số phận với momentum cá lẻ đã chết cấu trúc hậu-2020 (khớp AMH cùng ngày) — không
có bằng chứng dòng vốn/sở hữu chung tạo continuation edge độc lập với price momentum thuần. Khớp
đúng tiền lệ Rule 3 (20/20 sector sweep: grouping chỉ là LENS, không phải BOOK).

**Đóng nghiên cứu correlation-cluster tại đây** (đề xuất của Taylor, Mike đồng ý). Hướng còn mở
(chưa duyệt, kỳ vọng thấp — cùng nhóm rủi ro LENS-not-BOOK): within-cluster mean-reversion (giả
thuyết B — PVN có t-stat đáng kể đúng chiều mean-reversion) — cần pre-reg riêng + user duyệt nếu
muốn theo đuổi.

File: `mike/agents/Taylor/research/kaffa_correlation_cluster_20260910/{PREREG_step1.md,
step1_backtest.py,STEP1_CONCLUSION.md,step1_corr_stats.csv}`.

## Bước 1 KẾT QUẢ (2026-09-10 23:0x ICT, job Taylor_20260910_152624) — **NO-GO**

Pre-registered TRƯỚC khi chạy (`PREREG_step1.md`): tín hiệu Cluster_RS_200 (200d relative-strength
cấp cụm vs VNINDEX, tái dùng nguyên lookback `mom_200` từ AMH cùng ngày — không grid-search), giả
thuyết A (continuation: RS cao → fwd_3M cụm cao), mẫu hàng tháng, NW lag=12, quyết định GO cần CẢ
HAI cụm OOS corr dương + sign-consistent ≥5/7 năm.

Kết quả OOS (2020-2026): **PVN-family corr −0,357 (n=76, t_nw=−2,16, CÓ Ý NGHĨA nhưng SAI CHIỀU —
mean-reversion chứ không phải continuation)**; **Viettel-family corr +0,073 (n=75, t_nw=0,64,
không đáng kể, sign chỉ 2/7 năm ổn định)**. → **NO-GO, dừng, không bước 2.** Cluster-level
momentum cùng số phận với momentum cá lẻ đã chết cấu trúc hậu-2020 (AMH cùng ngày) — không có bằng
chứng cơ chế dòng vốn/sở hữu chung tạo continuation edge độc lập với price momentum thuần.

File đầy đủ: `mike/agents/Taylor/research/kaffa_correlation_cluster_20260910/STEP1_CONCLUSION.md`.
Hướng còn mở (chưa làm, chưa duyệt): within-cluster mean-reversion (giả thuyết B, bị loại khỏi
scope bước 1 để tránh multiple-testing) — nếu user muốn tiếp tục cần pre-reg mới riêng.
