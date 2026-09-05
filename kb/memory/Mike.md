# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## Retro 2026-09-05 — XONG (job Mike_20260905_173627)
File `kb/incidents/retro/retro-2026-09-05.md`, Wags CONFIRMED không sửa gì. 3 sự cố:
bq watchdog false-healthy (đã có entry riêng, lần tái diễn thứ 5 của §29 "đọc nhầm kênh lỗi
bq"), 1/6 turn thiếu ScheduleWakeup (nhẹ, không hậu quả), 3 vòng NEEDS_CHANGES trước review
tay tdays-gate (lặp lần 2, ghi chú "cân nhắc review tay sớm hơn cho gate AST đa-repo").
Escalation tdays-holiday từ 09-04 ĐÃ ĐÓNG hoàn toàn (0aab5fae).

**Đề xuất mở (chưa escalate, chưa đủ điều kiện 2-retro-liên-tiếp)**: Pattern §29 bq-channel
tái diễn 5 lần — cân nhắc xây RULE 2 kiểu `tz_anchor_gate.py` cho `bin/diagnosis_evidence_gate.py`
(quét call-site `bq` chỉ đọc 1 kênh stderr/stdout), nếu tái diễn lần 6 thì escalate thật.

## Bus question đang mở (2)
1. `Wags/wags-fix-not-confirmed: coord-2026-09-03` (2d) — Wags chưa có bằng chứng đã đính
   chính với user trên trading_daily về cơ chế ack deposit-rate. Cửa sổ: trước 2026-09-11.
2. `Mike/bq-monthly-pin-thieu-202608-202609-chay-bu-hay-khong` — chờ user quyết A/B/C.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm. §-mới tiếp theo gần như chắc chắn chạm
ngưỡng → tách sang _ext.md khi đó.

