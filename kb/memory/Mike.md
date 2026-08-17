# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật 2026-08-17T18:20Z (UPCOM G5 finding, quant-skeptic dispatched)

## Plan 08-18 — ĐÃ DUYỆT, cả 2 HOLD ALL (không đổi)

## Đã đóng hôm nay 08-17
- verify_account_snapshot legacy-majority guard → DONE (commit 0946c83d)
- GDKHQ G5 root cause → FIXED + ACCEPTED (enabled, commits 1589fed1 + 49efb2ff)
- book_breakdown_current SCL mislabel → FIXED (context_planning_mini.md)
- Order-book Pha 0 telemetry audit → VERIFIED (selfcheck PASS)

## Việc còn hở
1. **UPCOM G5 finding: CHỜ quant-skeptic verdict** (log: verify_20260817_181551)
   Finding: UPCOM dùng giá bình quân phiên trước, không phải close → G5 sai 33% mã UPCOM
   Recommendation nếu CONFIRMED: G5 decline-to-speak trên UPCOM
   VIX 08-20 là HOSE → không bị ảnh hưởng
2. **Auto-accept GDKHQ**: classifier block wiring → giữ manual (ok cho VIX 08-20)
   Dead code đã tạo (gdkhq_config.json + 2 hàm helper), chưa active
3. **VIX ex-date 08-20**: shadow chạy TRONG PHIÊN (09:10-14:30 ICT), sau đó Mike gõ accept_shadow() thủ công
4. question-checker round-2 cần MERGE vào master (branch session/1522519012066721923-coord-20260817, commit 4435b3e0)
5. Pattern B wakeup-miss — escalation mở, chờ user chọn A/B/C
6. capit_lever_selfcheck K3 FAIL pre-existing — ưu tiên thấp
7. plan-dd-check-string fix (commit 9a9dbb1) — cần ngày có LAG/BAL entry
8. Order-book Pha 0 telemetry — chờ phiên có giao dịch ≥08-19

## Bối cảnh còn hiệu lực
- TV1 Rule A LIVE từ 08-15, an toàn.
- CASH_VENDOR gate: giữ ĐÓNG. CAPIT margin: enabled=false.
- dispatch-prompt-heredoc skill cho prompt có backtick/code snippet.
- BQ trap: bq query truncate 100 rows ngầm → luôn check COUNT(*) trước aggregate.
- BQ trap: Trading_Value = Price × Volume (derived), không tính được VWAP từ BQ.

