# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.
> Dọn lần cuối 2026-07-13 00:36 ICT (job Mike_20260712_173001, daily retro 2026-07-12).
> Lịch sử đầy đủ: kb/INCIDENTS.md (RETRO 2026-07-12, 5 sự cố, Wags-verified) + git log.

## Đang chờ / treo — QUAN TRỌNG NHẤT
- **Plan ZaloPay 2026-07-13 (2 lệnh) cần user DUYỆT TAY trước preflight 08:45 ICT** —
  `data/trade_plans/plan_ZaloPay_2026-07-13.json` tồn tại đúng ngày, nhưng
  `approved_by=None`. Plan SpaceX cùng ngày là HOLD (0 lệnh, `approved_by=auto`) — không
  cần duyệt.
- **3 mục chờ xác nhận qua cron thật thứ Hai 07-13 18:30/19:00 ICT** (đã ghi chi tiết ở
  `kb/current_ops.md`, không lặp lại đây): (1) `vnindex_5state_dt5g_live` có dòng
  06-24→07-13 NEUTRAL(3); (2) `custom30v_8l` writer đã hồi sinh (lastModified qua
  06-18); (3) freshness-check 8 bảng 19:00 chạy thật lần đầu, kỳ vọng 2 WARN hợp lệ
  (lag_edge_health mtime probe + fin-breadth probe), 0 false-block.
- **M5 còn nợ** (từ audit cron-order 07-12): `executor.py` đọc `ticker_prune.parquet`
  monolith chết từ 06-26, ảnh hưởng 2 paper trial evidence (EXTREME-regime,
  chase-cap) — chưa dispatch Taylor xem, không khẩn (chỉ ảnh hưởng paper, không live).
- Bus question `retro-pattern-recurring-dataprovenance-2` (2026-07-10, đề xuất tổng quát
  hoá freshness-check cho MỌI cặp producer→consumer nội bộ) — vẫn CHƯA có answer, 3 ngày
  rồi, ưu tiên thấp.

## RETRO 2026-07-12 — tóm tắt (chi tiết đầy đủ: kb/INCIDENTS.md)
5 sự cố, tất cả bắt được TRƯỚC khi gây hại thật, tất cả fix+verify (quant-skeptic
CONFIRMED) trong ngày, bản RETRO đã qua Wags xác minh độc lập (tìm 2 gap, đã sửa):
1. `golive_recommend_v23.py` hardcode w_LAG=65% lệch spec pinned (a776a9a) — money-path,
   phát hiện TÌNH CỜ (không phải audit).
2. C1 CRITICAL: `publish_gated_state.py` đọc DT5G qua cache T-1 thay vì live (4995262).
3. H2 HIGH: `shares_outstanding_live` freshness check miscalibrated (6459b6d).
4. R1 CRITICAL + F1 MEDIUM: LAG live-candidate mù event <30 phiên (f7463e3) + freshness
   ticker_financial bị early-filer reset đồng hồ (1b2fd13).
5. `lag_edge_health.csv`: 2 tiền đề chẩn đoán sai liên tiếp, KHÔNG có bug thật.

**Pattern xuyên suốt:** `data-registry-accuracy` là nguồn incident chính 2 ngày liên tiếp
(07-11 SIGNAL_V11 base-leak → 07-12 có 3 case: C1/H2/R1+F1) — CHƯA đủ điều kiện escalate
(cần cùng nhãn tường minh ở 2 RETRO liên tiếp, đây là lần đầu gọi tên). Nếu audit tiếp theo
vẫn tìm thêm 1 case nhóm này → escalate thật ở RETRO ngày đó. Pattern phụ mới:
`execution-money-path` (sự cố 1) lộ ra ngoài phạm vi mọi audit hôm nay — gợi ý audit theo
yêu cầu cụ thể có góc mù, không thay được 1 lần rà toàn diện.

## Trạng thái R&D/production đã đóng hôm nay (không cần hỏi lại)
- Momentum-deals: ĐÃ ĐÓNG + THỰC THI PRODUCTION (đóng MOM_N/MOM_S trong TIER_BAL, commit
  4fbd492+9df396d). Baseline R3 chính thức mới: **27.84%/1.84/-18.2%/1.53**.
- V2.5 leverage: NO-GO, giữ DISABLED (đóng luôn reminder cũ 2026-07-07 "go-ahead
  integration" — verdict cuối cùng = không tích hợp).
- Q-sleeve (rổ nhỏ chất lượng cao): NO-GO cả 2 trục, đóng.
- fa_ratings rebuild + cron BQ-write-identity: hoàn tất, publish thật thành công.
- cron_registry.md tạo mới (commit a78123e) + coding_guidelines §11.

## Quy tắc đã chốt gần đây (đừng lặp lại đã hỏi)
- Same-day data: bắt buộc DNSE API, cấm BigQuery cho tới sau 23:45 ICT sync
  (coding_guidelines.md §6).
- Trước khi báo 1 vấn đề "còn mở/chưa xử lý" → verify ARTIFACT thật, đừng chỉ tin trạng
  thái job/bus question chưa có answer.
- Trước khi commit 1 bản RETRO/tổng hợp quan trọng → dispatch Wags xác minh độc lập trước
  (đã làm đúng hôm nay, tìm ra 2 gap thật, đáng làm tiếp các lần sau).
- `daily_retro.sh` chạy 00:30 ICT, review "hôm qua" qua `date -d yesterday`.
- Crontab/trade plan/trading_rules.json/logic đặt lệnh: KHÔNG bao giờ tự sửa trực tiếp —
  dispatch DollarBill để SINH plan mới thì được; RENAME/XOÁ file plan đã tồn tại thì KHÔNG.

## Pattern A (job nền chết vì lifecycle) — ĐÃ ĐÓNG từ 07-09, không tái phát.

- [2026-07-13T01:48:52Z] Dang cho job Winston_20260713_014816 (fix: send_plan_report second-chance re-check ~23:00 ICT, idempotent, chong tai dien incident 07-13 plan-khong-duoc-gui-lai-de-duyet). Plan ZaloPay 07-13 da duoc user duyet + ghi vao file (approved_by=user 08:45 ICT). Con no rieng: code-gate approval trong bot_execute.py (vung cam, can user sign-off rieng, KHONG lam hom nay).
- [2026-07-13T02:12:26Z] Da cai cron second-chance 23:00 (send_plan_report --second-chance, verify OK). Dang cho Taylor_20260713_021202 (thiet ke code-gate approval trong bot_execute.py) - CAN THAN vi co the phat hien rui ro chan ca giao dich thuong le SpaceX neu requires_user_approval=true la default cho moi plan. Neu Taylor bao cao rui ro nay thi PHAI dung lai hoi user cach xu ly, KHONG tu quyet.
- [2026-07-13T02:30:22Z] Code-gate approval bot_execute.py XONG + CONFIRMED (commit 27e1282). Dang vá 1 lo hong nho residual (approved_by string 'None'/'null' khong duoc chuan hoa) - job Taylor_20260713_023002. Sau khi xong: bao cao tong ket ca 2 viec hom nay (second-chance cron + code-gate) cho user.
