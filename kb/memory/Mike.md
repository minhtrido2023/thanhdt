# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật lần cuối: 2026-08-18T12:11Z (plan 08-19 xong, cả 2 HOLD ALL, chờ duyệt)

## Plan 08-19 — ĐÃ SINH XONG, cả 2 HOLD ALL, CHỜ DUYỆT
- SpaceX (job DollarBill_20260818_120604): HOLD ALL, 0 lệnh. ZaloPay (job
  DollarBill_20260818_120602): HOLD ALL, 0 lệnh. Cả 2 approved_by=None, cần duyệt trước
  08:45 ICT sáng mai (08-19).
- Cả 2 đã báo cáo đầy đủ vào thread.

## Đã xong 08-18 (từ trước, giữ nguyên)
- F1+F3 anti-double-reply, gdkhq Option B, UPCOM VWAP cron, Wags coord fix — arch-review CLEAN.
- G5 UPCOM: cron cài xong (15:15 ICT T2-T6), đang tích luỹ history, cần ≥3 phiên trước khi wire.
- VIX ex-date 08-20: shadow trong phiên 09:10-14:30, G2 tolerance fix xong.
- dividend-yield-floor: CONFIRMED downside-protection signal, CHƯA wire production.
- book_breakdown_current SCL mislabel: FIXED 08-17, verify độc lập OK.

## Việc còn hở (ưu tiên giảm dần)
1. GDKHQ dry-run D1-D3 chưa setup — theo dõi trước VIX 08-20 (còn 2 phiên).
2. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify.
3. Order-book Pha 0 telemetry (commit d6346efd) — chờ phiên thật có giao dịch.

## Bối cảnh còn hiệu lực
- TV1 Rule A LIVE từ 08-15, an toàn, đã đạt target. CASH_VENDOR gate: giữ ĐÓNG.
- CAPIT margin: enabled=false. dispatch-prompt-heredoc skill cho prompt có backtick.
- park_holdings.py stdout lẫn dòng "[dnse] kết nối OK" trước JSON — cần tail -n +2 khi parse.

