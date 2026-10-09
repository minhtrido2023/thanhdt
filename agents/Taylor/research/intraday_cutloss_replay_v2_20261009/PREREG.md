# PREREG — replay v2 cổng giá trong phiên (job Taylor_20261009_110243)

Ghi **TRƯỚC** khi chạy/nhìn bất kỳ kết quả v2 nào (09/10/2026 ~19:00 ICT). Kết quả v1 (REPORT
`intraday_cutloss_replay_20261009`) + phản biện quant-skeptic (log `logs/verify_20261009_104604_2121601.log`,
REFUTED medium) đã biết — chính vì thế giả thuyết dưới đây là giả thuyết thanh khoản mà skeptic nêu, không
phải phân nhóm book/sàn của đề xuất A cũ. **Chỉ đề xuất, không wire.**

## H1 (duy nhất, quyết định)
> "Cổng thanh khoản ADV20 ≥ 10 tỷ cho phép tự bán thì cutloss ≥ giữ ở T+5."

- **Code**: watcher/engine SAU khi merge PHẦN 1 (luật (A) gộp cửa sổ 60', (B) chạm sàn, (C) ca hoãn
  mặc định GIỮ). Ngưỡng kích hoạt không đổi (ret ≤ −5% ∧ idio ≤ −4%).
- **Kịch bản**: BROKEN (agent kết luận GÃY ngay trước hạn ⇒ mặc định BÁN hết), user im lặng.
- **Cấu hình gốc**: sổ mua 3 bước giá dưới giá khớp, mỗi bước 0,5 × KL khớp TB/phút 15' gần nhất (như v1).
- **Tập ca**: ca riêng trên mã đang giữ mà code v2 THỰC SỰ bán (sold > 0), ADV20 ≥ 10 tỷ VND
  (ADV20 = trung vị Price×Volume 20 phiên **trước** ngày D, từ `cache/daily.parquet`, không dùng ngày D).
- **Loại trước khi chấm** (lọc dữ liệu, không phải lọc kết quả): (i) P1 == TC (|P1/TC − 1| < 1e−6, ngày
  không giao dịch); (ii) Volume(D) == 0 hoặc Volume(D+1) == 0 trong BQ daily; (iii) quote cũ: bar mới nhất
  nhìn thấy tại T0 cũ hơn 60' so với T0.
- **Thống kê**: E5 = giá bán ròng / giá nếu giữ tại D+5 − 1 (công thức `analyze.py` v1: phí 0,097%×2 +
  impact 0,5·σ20·√(KL/ADV20)). Trung bình, CI95 bootstrap theo CỤM NGÀY (2000 lần, seed 7). N độc lập =
  số ngày.
- **Luật quyết định**:
  - N ngày < 30 ⇒ **INCONCLUSIVE** (không kết luận).
  - CI95 trên < 0 ⇒ **REFUTED**.
  - mean < 0 ⇒ **NOT SUPPORTED**.
  - mean ≥ 0 ∧ CI95 dưới > 0 ⇒ **SUPPORTED-STRONG** (cutloss tốt hơn giữ).
  - mean ≥ 0 ∧ CI95 dưới > −1,0 điểm % ⇒ **SUPPORTED (không kém hơn, biên 1 điểm %)**.
  - mean ≥ 0 ∧ CI95 dưới ≤ −1,0 ⇒ **INCONCLUSIVE (quá rộng)**.
- **Điều kiện bền** để gọi SUPPORTED là "bền": dấu của mean E5 (ADV ≥ 10 tỷ) KHÔNG đổi qua 6 cấu hình
  sổ lệnh (0,25×/0,5×/1× KL mỗi phút × 1/3 bước giá) VÀ qua 2 nửa thời gian (2023-09→2024-12 /
  2025-01→2026-10). Đổi dấu ⇒ hạ một bậc (STRONG→SUPPORTED, SUPPORTED→INCONCLUSIVE).

## Universe (thay ledger R3 LAG micro)
- 2026-07-09→10-09: vị thế THẬT SpaceX/ZaloPay (như v1).
- 2023-09-11→2026-06-19: (a) dòng ledger R3 point-in-time (BAL/LAG/CUSTOM30V) **lọc ADV20 ≥ 1 tỷ**; ∪ (b)
  tập mã SpaceX/ZaloPay đang giữ gần nhất (giữ giả định suốt kỳ, mỗi mã 5% NAV; excluded ⇒ no_auto_sell như
  thật). NAV mô phỏng **50 tỷ** (cỡ R3 pin) thay 1 tỷ ⇒ KL bán thực tế hơn (v1 trung vị 300cp).
- Thiên lệch đã biết, khai trước: (b) là mã CÒN giữ hôm nay ⇒ survivorship nghiêng về "giá hồi" ⇒ nghiêng
  về GIỮ (bất lợi cho H1). Sàn giao dịch không point-in-time (như v1).

## Mô tả (không quyết định, không sửa lỗi bội)
Bảng theo ADV20 (<1 / 1–10 / ≥10 tỷ) và giá < 5.000đ (ở cả universe v1 để so); T+1/T+20; UNCLEAR;
bán-ngay-T0; độ nhạy sổ lệnh; so luật mới vs cũ (số ca riêng chuyển gộp/hoãn-GIỮ, Δ kết quả); control PNJ
06–09/10 chạy lại độc lập trên code mới, so với shadow log thật.

## ADDENDUM — user chốt cho phép thử OOS live (09/10/2026 19:44 ICT, thread 1557920546891763755)
Ghi TRƯỚC khi có bất kỳ dòng `EOD_OOS` live nào (shadow chạy code mới từ 12/10/2026).
1. **Mốc đánh giá**: bỏ mốc "5 phiên ~12/10". Thay bằng: kiểm lại H1 khi có **≥30 NGÀY có ca live**
   (N độc lập = số ngày có ca, không phải ngày lịch) trên mã ADV20 ≥ 10 tỷ, đúng luật quyết định ở trên,
   không đổi ngưỡng kích hoạt/ADV/horizon T+5. Nhịp lịch sử ≈ 85 ngày-ca / ~37 tháng (≈2,3/tháng ở NAV
   mô phỏng 50 tỷ) ⇒ mốc này có thể mất **1–2 năm**; không có ngày cố định.
2. **Biên không-kém-hơn 1,0 điểm %** (CI95 dưới > −1,0 ở T+5) — **user xác nhận chấp nhận được**
   (`decided_by: user`). Lý do user: tiền cắt lỗ được giải phóng, tránh chi phí cơ hội nếu mã đứng yên
   ~20 phiên; coi 1% là "chi phí sử dụng tiền". Đối chiếu: Trứng vàng 8,543%/năm ≈ 0,68% trên 20 phiên.
   Biên này áp cho phép thử OOS live; kết quả replay lịch sử v2 vẫn chỉ là mô tả (quant-skeptic
   INCONCLUSIVE, verify_20261009_123235) và KHÔNG đủ để bật tự bán.
3. Bật tự bán (wire live) vẫn cần: H1 OOS SUPPORTED theo 1–2 + quant-skeptic CONFIRMED + user duyệt.
