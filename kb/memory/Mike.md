# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Working memory — Mike
> Cập nhật 2026-08-17T18:46Z

## Đã đóng hôm nay 08-17
- GDKHQ D1-D3: enabled() = True
- book_breakdown_current SCL: fixed
- Order-book telemetry Pha 0: verified
- question-checker round-2 (4435b3e0): MERGED vào master
- Pattern B bus question: CLOSED — user chọn Option B (audit trước khi vá)

## Đang xử lý
- Taylor (job Taylor_20260817_184109): wire G5 decline-to-speak UPCOM + research VWAP source
- Wags (job Wags_20260817_184558): audit double-answer mechanism + hậu quả miss thật

## Chờ user (sau khi Wags xong)
- Kết quả audit double-answer → đề xuất fix dứt điểm → cần user duyệt trước khi wire

## Việc còn hở (tự xử lý)
- VIX ex-date 08-20: shadow chạy TRONG PHIÊN (09:10-14:30 ICT), sau đó accept_shadow() thủ công
- capit_lever_selfcheck K3 FAIL: pre-existing, ưu tiên thấp
- plan-dd-check-string fix: chờ ngày có LAG/BAL entry
- Order-book Pha 0 telemetry: chờ phiên ≥08-19

## Context
- BQ trap: bq query truncate 100 rows — luôn check COUNT(*).
- dispatch-prompt-heredoc skill cho prompt có backtick/code.

