# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Dọn lần cuối 2026-07-11 00:30 ICT (job Mike_20260710_173001, đóng nốt retro 2026-07-10
> mà job tiền nhiệm 150001 hết turn giữa chừng). Lịch sử đầy đủ: kb/INCIDENTS.md (RETRO
> 2026-07-10 + addendum) + git log. Chỉ giữ trạng thái THẬT cần biết ngay để tiếp mạch việc.

## Đang chờ / treo — QUAN TRỌNG NHẤT
- **Plan ZaloPay thứ Hai 2026-07-13 (2 lệnh, SELL VIB + 1 lệnh khác) cần user DUYỆT TAY
  trước preflight 08:45 ICT** — `data/trade_plans/plan_ZaloPay_2026-07-13.json` tồn tại,
  `plan_date` đúng, nhưng `approved_by=None`. Plan SpaceX cùng ngày là HOLD (0 lệnh,
  `approved_by=auto`) — không cần duyệt.
- Bus question `retro-pattern-recurring-dataprovenance-2` (đề xuất tổng quát hoá quy tắc
  freshness-check cho MỌI cặp pipeline producer→consumer nội bộ, không chỉ BQ-vs-DNSE) —
  VẪN CHƯA có answer, chờ user/Mike xác nhận hướng.
- Taylor's câu hỏi `cần-quyết-trước-18h30` (fix path-bug ew_full BULL-commit giả) — đã
  fix + verify counterfactual xong (job `Taylor_20260710_170527`, commit trên repo
  WorkingClaude), nhưng **publish BQ production bị harness chặn** — câu hỏi mới
  "publish base v3.4b: chạy manual hay để cron thứ Hai 18:30 tự publish?" còn mở, cần
  user quyết.
- Dispatch `Winston_20260710_170615` timeout 2 lần (~00:06-00:16 ICT 11/07, liên quan việc
  publish ở trên) — chưa điều tra, để retro 2026-07-11 xử lý (đúng ranh giới ngày lịch).
- V2.5 live-recommend integration: user go-ahead vẫn treo từ 2026-07-07.

## Sự cố 2026-07-10 — đã đóng đầy đủ, xem RETRO + addendum trong INCIDENTS.md
Cả 3 sự cố hôm đó (ops_health_check cross-agent answer-match, DollarBill đọc DT5G hôm qua
do lệch thứ tự cron, DollarBill tính sai ngày T+1 thứ Bảy thay vì thứ Hai) đã fix root
cause + verify artifact xong (plan 07-13 cả 2 account tồn tại đúng ngày; file ngày sai đã
được rename). Không còn việc treo từ ngày đó ngoài 2 mục approval/escalation ở trên.

## Quy tắc đã chốt gần đây (đừng lặp lại đã hỏi)
- Same-day data: bắt buộc DNSE API, cấm BigQuery cho tới sau 23:45 ICT sync (bright-line
  rule, coding_guidelines.md §6) — biết là CHƯA bao phủ hết pattern data-provenance rộng
  hơn (xem escalation-2 ở trên, còn mở).
- Bất cứ giá trị tính tất định được (ngày, %, số lượng) → tính bằng code, truyền literal
  vào dispatch prompt, KHÔNG giao LLM tự suy luận.
- Trước khi báo 1 vấn đề "còn mở/chưa xử lý" → verify ARTIFACT thật (crontab -l, đọc file,
  giá trị API), đừng chỉ tin trạng thái job/bus question chưa có answer — job có thể tự
  báo "failed" (vd max-turns) dù nội dung đã đúng và đã commit.
- `daily_retro.sh` giờ chạy 00:30 ICT (đổi từ 22:00, 2026-07-10) — chỉ 1 dòng cron, review
  "hôm qua" qua `date -d yesterday`.
- Crontab/trade plan/trading_rules.json/logic đặt lệnh: KHÔNG bao giờ tự sửa trực tiếp —
  dispatch DollarBill để SINH plan mới thì được (routine); RENAME/XOÁ file plan đã tồn tại
  thì KHÔNG (bị permission classifier chặn theo thiết kế).

## Pattern A (job nền chết vì lifecycle) — ĐÃ ĐÓNG từ 07-09, không tái phát kể từ đó.

- [2026-07-12T15:12:31Z] Đang chờ 2 job song song: Taylor_20260712_151135 (fix C1 CRITICAL - publish DT5G qua cache, deadline truoc 18:30 T2 07-13) + Winston_20260712_151206 (audit + de xuat don crontab paper-trading lac hau). Con no: verify C1 fix, quyet H2 (BLOCK->WARN), formalize kb/cron_registry.md tu Phan 5 audit report, apply diff don crontab sau khi Winston xong + toi review, dispatch Taylor xem M5 (2 paper trial bi anh huong boi ticker_prune.parquet chet tu 06-26).
- [2026-07-12T15:45:43Z] C1 CRITICAL: FIX+COMMIT+VERIFY XONG (commit 4995262, quant-skeptic CONFIRMED). Dang cho: (1) user duyet diff crontab 1 dong (xoa dangling comment go-live flip) - da hoi 2 luot truoc chua tra loi; (2) quyet H2 (ha BLOCK->WARN cho shares_outstanding_live, false-block ~07-15); (3) formalize kb/cron_registry.md tu Phan 5 audit report; (4) fix logic that cho lag_edge_health.csv refresh (bug o script khong phai thieu cron). Dang dispatch Taylor viec nho: ghi finding bus cho commit 4995262 (job Taylor_20260712_154530).
- [2026-07-12T15:53:09Z] Da xong: crontab diff (xoa dangling comment, ap dung), kb/cron_registry.md tao xong + commit (a78123e), coding_guidelines Sec 11. Dang cho 2 job song song: Winston_20260712_155038 (H2 fix BLOCK->WARN shares_outstanding_live) + Taylor_20260712_155038 (fix logic lag_edge_health.csv refresh khong catch-up). Sau khi ca 2 xong: verify + dispatch quant-skeptic cho H2 (production gate change), doc lai finding cho lag_edge_health fix.
