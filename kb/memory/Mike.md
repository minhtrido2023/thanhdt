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

- [2026-09-06T02:45:17Z] 8L accruals chuoi DONG HAN 2026-09-06: Phase0 (T1 song 1/4) -> quant-skeptic CONFIRMED medium (chi ra sector confound lam suy giam 17-31%) -> Phase0b (qua 4 kiem tra) -> R3 NO-GO CA 2 NHANH (Taylor_20260906_022452). Ly do giet: IS/OOS nguoc dau (IS -0,41/-0,15pp, OOS +0,48pp), DSR P=0,0004 sau khai N_trials=9 that cua ca chuoi, LOO cho thay 2021(-0,55pp) va 2022(+0,50pp) triet tieu nhau = reshuffle-luck. Harness tai lap pin byte-identical nen ket qua tin duoc. DAY LA LAN NO-GO THU 3 cho cung y tuong accrual-gate trong CFO_POOL custom30V (2 lan truoc 2026-08-30) => KHONG thu them bien the nguong/cong thuc o vi tri do. Bai hoc phuong phap thu duoc: block bootstrap da thanh chuan Phase-0 (commit WC 22948494, skill quant-research buoc 4).
- [2026-09-06T12:04:21Z] 2026-09-06: quyết định lịch trình universe-pit migration — không chốt mốc lịch tổng, P5/P6+G8.1 giữ event-gated (chờ capit_fired=false), G7/G8/G9 đưa vào quét định kỳ kb_nightly.sh item 12 (commit 852d8d34), escalate nếu treo >8 tuần. Đã ghi vào kb/projects/universe-pit-migration.md (commit 8b9e7717).
