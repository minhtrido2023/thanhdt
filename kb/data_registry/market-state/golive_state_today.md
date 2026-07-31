---
kind: script-output
status: DERIVED
source: deploy_golive_dt5g_v4/golive_state_today.json
group: market-state
derived_from: tav2_bq.vnindex_5state_dt5g_live
writer: publish_gated_state.py — daily_refresh_v34b_linux.sh step [12] ~18:35 + bq_freshness_check.sh [pipeline-1] ~19:01
role: BẰNG CHỨNG publisher — input của gate BLOCK trong bq_freshness_check.sh (từ 2026-07-31)
---

# deploy_golive_dt5g_v4/golive_state_today.json

**Status: DERIVED (từ `dt5g_live`)**

## Là gì
File publish nhanh cho DollarBill đọc.

## Ai ghi / cadence
`publish_gated_state.py`, ghi HAI lần mỗi phiên: `daily_refresh_v34b_linux.sh` step [12] (~18:35)
rồi `bq_freshness_check.sh` [pipeline-1] (~19:01).

## Vai trò MỚI (2026-07-31): bằng chứng publisher
`bq_freshness_check.sh` **BLOCK** pipeline/DollarBill nếu file này không chứng minh publisher CỦA TA
đã chạy: `as_of` == phiên giao dịch gần nhất **và** `bq_publish_ok == true` **và** mtime = hôm nay
(bỏ điều kiện mtime vào ngày KHÔNG giao dịch để không chặn oan ngày lễ giữa tuần).
Lý do phải gate bằng file LOCAL này thay vì `MAX(time)` của bảng BQ: bảng
`vnindex_5state_dt5g_live` có **writer thứ hai** (pipeline kaffa_v2 của team dữ liệu, ~17:12 ICT)
vẫn đẩy `MAX(time)=hôm nay` kể cả khi chuỗi của ta chết — xem
[vnindex_5state_dt5g_live.md](vnindex_5state_dt5g_live.md) §HAI WRITER ĐỘC LẬP. File này thì
writer ngoài không ghi được ⇒ không giả mạo được.

## Bẫy
Field `as_of` phải khớp NGÀY HÔM NAY — nếu lệch 1 ngày, xem sự cố cron-order 2026-07-10 (đã sửa).
Đừng "sửa nhanh" bằng cách `touch` file này: nó là bằng chứng của một gate chặn tiền thật.
