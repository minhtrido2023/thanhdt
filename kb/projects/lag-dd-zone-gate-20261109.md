# Cổng LAG: mua cần DD + giá ≤ tâm (user chốt 09/11/2026 19:2x ICT, `decided_by: user`)
Nguyên văn: "Plan muốn đưa vào lệnh mua cần phải làm due diligence cho candidate trước. Nếu giá không nằm trong, dưới vùng và dưới tâm thì không đưa vào danh sách mua. Hiện nay việc mua theo book lag đang cho thấy performance không ổn định. Mua 2 candidate, cả 2 đều performance kém. Nên cần xét thêm điều kiện này trước khi edge của lag book trở lại bình thường."

## Luật (Mike diễn giải — chờ user xác nhận nếu muốn khác)
- Phạm vi: MỌI lệnh MUA book `LAG` (khớp tuyệt đối). BAL/CAPIT/PARK/DISCRETIONARY không đổi. Lệnh BÁN không bao giờ bị chặn.
- Giữ lệnh chỉ khi: có DD trong `kb/dd_price_zones.json` (dd_date ≤ ngày plan, rev cao nhất) · khoá `assumptions_md5` còn khớp · DD chưa quá `expires_on` · không có sự kiện quyền điều chỉnh giá sau dd_date (không kiểm được corp-action ⇒ chặn) · **giá ≤ min(tâm, đỉnh vùng)**. ("Trong vùng/dưới vùng VÀ dưới tâm" ⇒ thực chất giá ≤ tâm.)
- Lệnh được giữ bị ÉP `hard_no_chase_ceiling_vnd` = min(trần sẵn có, tâm) ⇒ giá khớp không vượt tâm.
- Fail-CLOSED: sổ/corp-action không đọc được ⇒ chặn mọi LAG buy, báo Trading Daily.

## Cài đặt
`trading_bot/plan.py::filter_lag_dd_zone_orders` (+ hằng `LAG_DD_ZONE_GATE_ENABLED`), gọi trong `bot_execute.py` ngay sau cổng cờ DD, TRƯỚC netting. Merge main `6e991b41e`. Selfcheck `lag_dd_zone_gate_selfcheck.py` 28/0 (+`--live` 30/0). arch-review: vòng 1 NEEDS_CHANGES (6 điểm, đã vá) → vòng 2 APPROVED.
Tắt = đổi hằng số `LAG_DD_ZONE_GATE_ENABLED=False` trong code (không env/JSON).

## Hệ quả ngày 1 (09/11)
Plan 10/11 có 4 LAG buy (BSR 25.950 / CSV 22.600 / GAS 73.000 / MSB 16.300) — tất cả TRÊN tâm (17.496 / 20.717 / 50.146 / 13.018) ⇒ cổng loại cả 4 ở cả 2 TK.

## Điều kiện THOÁT — user chốt 09/11 23:3x ICT (`decided_by: user`)
- KHÔNG có dấu hiệu đáy đáng tin (mean12 là trung bình trượt 12 tháng, trễ 25 phiên + dữ liệu về theo mùa BCTC ⇒ không phải bộ dò đáy).
- Nếu chưa có dấu hiệu: **khi có 1 THÁNG DƯƠNG trở lại ⇒ XEM XÉT candidate của quý đó** (user quyết từng lần; cổng không tự tắt). **Mốc xem lại cứng 15/12/2026.**
- Mike diễn giải "tháng dương" = TB lợi suất 25 phiên của các sự kiện LAG theo `known_date` (nhân quả) > 0 VÀ ≥30 sự kiện (tháng ít sự kiện là nhiễu: 2026-08 n=4 +3,6%). Đo bằng `bin/lag_gate_exit_check.py` (chỉ đọc). Số 09/11: tháng đủ mẫu gần nhất 2026-09 −0,04% (n=96), 06 −3,18%, 05 −4,74%; dương gần nhất 2026-03 +1,67% — chưa có tháng dương mới.
- Dữ liệu `lag_edge_health.csv` về theo lô (known_date cuối 23/09): thường chỉ 3-4 tháng/năm có đủ mẫu ⇒ "tháng dương" thực tế xuất hiện theo mùa BCTC, không đều.
