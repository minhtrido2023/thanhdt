"""Biểu phí giao dịch THẬT của DNSE — hằng số dùng chung cho đường KẾ TOÁN/BÁO CÁO.

Đo 2026-09-13 (aria-F1, job Taylor_20260913_064536) trên 400 dòng khớp của 25 email "Báo cáo giao
dịch khớp lệnh" DNSE 01/07→17/08/2026, cả 2 tiểu khoản (coverage 15/15 phiên SpaceX, 18/18 phiên
ZaloPay có fill trong dnse_raw), đối chiếu chéo sao kê tiền tháng 07/2026 (lệch ≤4đ/tháng/account):
  - phí DNSE 0,070% giá trị khớp, CẢ HAI chiều — 400/400 fill trong ±0,002pp
  - phí trả sở: HOSE 0,027% (334/334 fill), UPCOM 0,018% (66/66, mới chỉ chiều mua DRI/TV1/SCL);
    HNX chưa quan sát được ⇒ không có hằng số, đừng tự đoán
  - thuế TNCN bán 0,1% là THUẾ, không gộp vào phí
  - phí CKCK 0,3đ/cp chiều bán chỉ có trên sao kê (≈0,001% giá trị) — bỏ qua
Hằng số theo chiều = phí DNSE + phí sở HOSE (sàn chiếm 100% doanh số bán, 75,6% số fill mua).
Bằng chứng + script tái lập: agents/Taylor/research/aria_F_20260913/.

Đường THỰC THI (aria-H, user duyệt 2026-09-13 14:54 ICT): bin/merge_park_orders.py fee_est_vnd và
prompt DollarBill trong bin/bq_freshness_check.sh import trực tiếp từ đây. trading_bot/plan_funding_gate.py
FEE_RATE KHÔNG import được (ranh giới repo) ⇒ hardcode cùng giá trị, đồng bộ bằng selfcheck đối chiếu —
đổi hằng số ở đây là PHẢI đổi cả FEE_RATE bên đó.
"""

BROKER_FEE_PCT = 0.070
EXCHANGE_FEE_PCT = {"HOSE": 0.027, "UPCOM": 0.018}

FEE_RATE_BUY_PCT = BROKER_FEE_PCT + EXCHANGE_FEE_PCT["HOSE"]    # 0,097%
FEE_RATE_SELL_PCT = BROKER_FEE_PCT + EXCHANGE_FEE_PCT["HOSE"]   # 0,097%
SELL_TAX_RATE = 0.001   # thuế TNCN 0,1% giá trị bán — 130/130 fill bán (trừ bán CK quyền)
