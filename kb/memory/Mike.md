# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## Weekly ops audit 2026-09-05 — XONG (job Mike_20260904_211002, resume sau max-turns)
Báo cáo đầy đủ ở topic Architecture + bus decision `weekly-ops-audit`.
4 bug tự sửa: be1d64a0 (watchdog custom30v báo KHOẺ giả khi bq fail auth — money-path
30% idle-pool parking mù mà im lặng; +2 lỗi kèm), d3924e24 (spend_history 12/53 dòng
thiếu 4 cột + nhãn ngày UTC), e5700fbd (freshness_warn selfcheck neo cứng tiêu đề báo
cáo, đỏ im lặng từ 09-03 sau tone-polish 14a90097 — KHÔNG phải bug production),
0b2eeb60 (market-state/index.md thiếu 2 nguồn).

**CHỜ NGƯỜI QUYẾT — bus question mới `bq-monthly-pin-thieu-202608-202609-chay-bu-hay-khong`**:
bq_monthly_pin chết 2 tháng ⇒ thiếu pin 202608+202609. Chạy bù bây giờ đóng dấu snapshot
theo 09-05 chứ không phải ngày đáng lẽ chụp (nhãn sai vintage). 3 options A/B/C trong payload.
Urgency thấp — rebalance thật vẫn đúng, chỉ mất 2 điểm lịch sử.

**CHƯA VERIFY ĐƯỢC trong production**: be1d64a0 + d3924e24 chưa có lần trigger thật kể từ
khi fix. Lần đầu = nightly 19:00 ICT 09-05 (spend_report) và cron bq kế tiếp. Kiểm lại ở
audit tuần sau nếu chưa ai đụng.

**Quan sát cần quyết ở review sau (KHÔNG tự đổi)**: `run_selfchecks.sh` cố ý gộp `mike_paseo/`
(clone đứng ở KB v2611, 2026-08-28, không cron nào dùng) vào phạm vi ⇒ 3/6 FAIL của lần chạy
là nhiễu từ bản clone cũ. Chưa rõ mục đích bản clone nên chưa đổi phạm vi.

**Sát ngưỡng OKF**: kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm (phẳng 6 ngày).
§-mới tiếp theo gần như chắc chắn chạm ngưỡng → tách sang _ext.md khi đó.

## Bus question đang mở (2)
1. `Wags/wags-fix-not-confirmed: coord-2026-09-03` (2d) — Wags chưa có bằng chứng đã đính
   chính với user trên trading_daily về cơ chế ack deposit-rate. Cửa sổ: trước 2026-09-11.
2. `Mike/bq-monthly-pin-thieu-202608-202609-chay-bu-hay-khong` (mới 09-05) — chờ user.

## Escalate cũ đã đóng
`retro-pattern-recurring-tdays-holiday-2days` — đã quyết B (xây gate kiểu tz_anchor_gate.py
quét AST tdays/busday_count/date-diff không kèm vn_market.is_holiday), decision 09-04.

- [2026-09-05T02:00:58Z] IntCov_P0 formula CONFIRMED bằng bq_admin (2026-09-05, Zalo): pass-through giá trị VCI opaque khi VCI trả non-null; fallback CHỈ khi null = PBT/abs(IntExp)+1. Chứng minh toán học: SBA (PBT dương/tăng, IntCov càng âm) KHÔNG thể đến từ fallback (fallback với PBT dương luôn ≥1) ⇒ số SBA chắc chắn từ nhánh VCI opaque, không suy ngược được. Kiểm schema ticker_financial: KHÔNG có cột interest_expense/profit_before_tax ⇒ không tự tính lại được kể cả công thức fallback đã biết, phải kéo BCTC thô ngoài BQ. Không đổi khuyến nghị (vẫn EBITDA_P0/NP_P0 đối chiếu). Cập nhật commit ee604173 (merged master), đính chính giả thuyết net-financial ở v3. Chuỗi adaptive-exclusion giờ đóng hoàn toàn kể cả câu hỏi mở cuối cùng.
- [2026-09-05T04:03:53Z] 2026-09-05 11:0x: cả 2 bus question weekly-ops-audit đã đóng — bq-monthly-pin backfill 202608/202609 XONG (BACKFILL metadata gắn), lãi suất VCCorp 6.8% giữ nguyên (khớp verify user 09-04). Bonus: Wags vá bug ack suppress_days (commit c437548b+4a35bd1d), arch-reviewer CONFIRMED, Mike tự re-verify selfcheck PASS. Không còn bus question tồn đọng.
- [2026-09-05T08:00:29Z] 05/09 15:00: tdays gate RULE 2 XONG — Wags_20260905_060209 cancel sau 3 vòng NEEDS_CHANGES (Pattern C, user chốt), Mike review tay thay vòng 4: 137/137 + 38/38 mutation + hành vi 8/8 + FP 0/300. Commit 0aab5fae (mike). Gate LIVE cả 2 rule. Bài học lặp lần 2: gate AST đa-repo luôn ăn 3-5 vòng arch-review — lần sau cân nhắc review tay sớm hơn thay vì auto-loop.
