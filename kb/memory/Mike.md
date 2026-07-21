# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Dọn lần cuối 2026-07-20 22:xx ICT (job Mike_20260720_173001, daily retro 2026-07-20).
> Lịch sử đầy đủ: kb/INCIDENTS.md (RETRO 2026-07-20, 6 sự cố, Wags-verified sau 1 vòng
> gaps-found-fixed) + git log.

## Đang chờ / treo — QUAN TRỌNG NHẤT
- **Bus question `retro-pattern-recurring-headless-wake-assumption-3`** (mới tạo hôm nay) —
  quy trình daily_retro.sh tự nó lỗi 2 RETRO liên tiếp (07-18 phát hiện lỗi 07-17, rồi 07-19
  lặp lại y hệt: job Mike headless schedule-wakeup-rồi-tự-dừng tưởng có turn sau, không có).
  Cần user quyết 1 trong 3 hướng đã đề xuất (gate cơ khí trong daily_retro.sh / đổi hẳn workflow
  Wags-verify không qua Mike trung gian / bỏ hẳn bước 4b ở ngữ cảnh headless). ƯU TIÊN CAO vì đã
  chạm ngưỡng escalation bước 10.
- **`ops_health_check.sh:188` — bug so khớp topic tuyệt đối, CÒN MỞ**: câu hỏi đóng bằng hậu tố
  `-closed`/`-resolved`/... không được checker nhận ra, báo sai "còn treo" vĩnh viễn + sinh dispatch
  wags_autofix lãng phí ~2/ngày. arch-reviewer đã cho `required_changes` cụ thể (chuẩn hoá so khớp
  + ghi convention vào kb/ops_runbook.md) nhưng CHƯA AI ÁP DỤNG — cần làm, không khẩn (không phải
  tiền thật, chỉ noise).
- **2 mục "chờ user" cũ (data-registry-accuracy-5days, joblifecycle-timeout-3) ĐÃ BỊ XÁC NHẬN
  KHÔNG TỒN TẠI TRÊN BUS** — nhiều RETRO trước lặp lại claim sai. Đã ngừng carry-forward. Nếu
  2 vấn đề gốc vẫn cần quyết định thật, phải escalate LẠI bằng question thật, không dựa văn bản cũ.
- M5 nợ cũ: `executor.py`/paper trials đọc `ticker_prune.parquet` monolith chết từ 06-26 — chưa
  dispatch Taylor, không khẩn (chỉ ảnh hưởng paper).
- Selfcheck 2-account-interleaved cho `daily_nav_snapshot.py`/`reconcile_equity.py`/
  `verify_account_snapshot.py` (đề xuất RETRO 07-19) — chưa làm.
- Dọn crontab paper-trading lạc hậu (diff Winston_20260712_151206) — vẫn chưa áp dụng, không khẩn.

## RETRO 2026-07-20 — tóm tắt (chi tiết đầy đủ: kb/INCIDENTS.md)
6 sự cố. Draft đầu tiên của chính Mike bị Wags audit (job Wags_20260720_173722) bắt GAPS FOUND:
(1) claim "đã escalate" viết ở thì quá khứ TRƯỚC KHI event thật tồn tại — tự sửa bằng cách escalate
thật rồi mới hoàn tất văn bản; (2) 2 sự cố bị bỏ sót (deposit-rate NOTIFY_OFF swallow,
bigquery_dictionary.json unit bug làm invalidate 1 kết luận nghiên cứu cũ) — đã bổ sung. Điểm quan
trọng nhất: quy trình retro TỰ NÓ lỗi 2 lần liên tiếp (07-18→07-19) không ai phát hiện tới hôm nay —
đã escalate + đề xuất gate cơ khí thật (không phải lời nhắc suông nữa).

## Trạng thái vận hành ổn định (không đổi hôm nay)
- SpaceX/ZaloPay LIVE, V2.4, không sự cố tiền thật hôm nay (ZaloPay approval-gate block sáng nay
  là ĐÚNG thiết kế, không phải bug — Winston đã xác nhận).
- Plan SpaceX 07-21 đã duyệt (5 lệnh CAPIT deploy, VIX SELL đã bị Mike gỡ vì là stop-loss bịa —
  xem RETRO 07-20 sự cố #2). User cần rút 302M Trứng vàng trước 08:45 ICT 07-21.
- CAPIT washout: chuỗi R&D DCF/quality-gate/exit/liquidity/trigger hôm nay đều NO-GO — trigger
  hiện tại được minh oan, không sửa gì. Basket hiện tại (nếu fire): NCT/PVT/SAB/SIP/VNM.

- [2026-07-21T01:20:03Z] TREO — merge cap %ADV N-account cho CAPIT: nhánh capit-adv-cap-20260721, quant-skeptic đã CONFIRMED (high) cả 2 vòng (per-account job Taylor_20260720_172614 + N-account pro-rata job Taylor_20260720_180351). CHỈ CÒN 1 bước kỹ thuật: chạy lại golive_recommend_v23.py để có artifact capit_adv_caps schema mới, RỒI mới merge (merge trước sẽ fail-closed chặn sạch sleeve CAPIT đang fired). User CHỈ ĐẠO 2026-07-21 08:19 ICT: đợi SAU phiên giao dịch sáng nay mới làm (không đụng vào lúc CAPIT SpaceX đang thực thi 5 lệnh ~236M @11:15). Trigger: sau ~11:30 ICT hôm nay (07-21), dispatch Taylor regenerate golive_recommend_v23.py + merge nhánh trên.
