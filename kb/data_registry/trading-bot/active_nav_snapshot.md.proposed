---
kind: local-file
status: CANONICAL
source: "data/execution_logs/active_nav_<label>.json (label = SpaceX | ZaloPay)"
group: trading-bot
role: ảnh chụp NAV + vị thế THẬT theo account, đã trừ mã excluded — cơ sở sizing và là nguồn watchlist cho lớp bảo vệ tin xấu
writer: mike/bin/compute_active_nav.py (qua compute_active_nav_all.sh, cron 20:15 ICT T2-T6)
readers: golive_recommend_v23.py (_account_nav_basis) · mike/bin/corp_action_daily.py · mike/agents/Taylor/anomaly_scan.py (load_universe) · mike/bin/compute_park_trim.py
---

# `active_nav_<label>.json` — NAV/vị thế theo account (đăng ký 2026-08-14, `.proposed` chờ Mike duyệt)

> Ghi ra `.proposed` theo §13 (file thuộc `kb/`, chưa được duyệt live). Lý do tạo: §9 bắt buộc tra
> data_registry trước khi phụ thuộc một nguồn — file này **chưa từng có entry** dù đã có ≥4 reader,
> trong đó 2 reader chạm tiền/chọn mã. Nay `anomaly_scan.load_universe()` phụ thuộc thêm vào ngữ
> nghĩa của field `computed_at` (cổng độ tươi E1) nên khoảng trống đó phải được đóng.

## Là gì
Ảnh chụp mỗi cuối phiên: NAV tổng, NAV "active" (đã loại vị thế `excluded_tickers` như DGC ở
ZaloPay), các chân tiền, và **danh sách vị thế thật** (`positions[].ticker`). Sinh từ DNSE live API.

## Ai ghi / cadence
`compute_active_nav_all.sh` — cron **20:15 ICT T2-T6** (cài 2026-08-13), trước
`inject_discretionary_orders.sh` 20:30. **KHÔNG chạy cuối tuần / ngày lễ** ⇒ bản đọc được sáng
thứ Hai luôn mang `computed_at` của **thứ Sáu**; đó là ĐÚNG, không phải stale.

## Field then chốt
| Field | Ngữ nghĩa | Bẫy |
|---|---|---|
| `computed_at` | **NGÀY (ICT), không phải timestamp** — `today_ict().isoformat()` | Không suy ra được giờ chạy; mọi cổng độ tươi phải tính theo PHIÊN, không theo giờ |
| `positions[].ticker` | vị thế thật, đã gộp nhiều dòng deal cùng mã | gồm CẢ mã `excluded` (loại khỏi rebalancing ≠ hết rủi ro — đó là lý do DGC vẫn được anomaly_scan gác) |
| `active_nav` | cơ sở sizing (NAV tổng − giá trị mã excluded) | KHÔNG dùng NAV tổng cho sizing account có vị thế legacy |
| `cash_basis` | chân tiền đang dùng | §25: cơ sở NAV = `totalCash − totalDebt`, KHÔNG phải `availableCash` |

## Bẫy (1) — không có cổng độ tươi thì hỏng ÂM THẦM
Producer (20:15) và các consumer (`anomaly_scan` 08:20, `corp_action_daily` 07:30) chạy trên các
cron **độc lập**. Producer chết một tối → consumer đọc sổ hôm trước và **không có gì báo**: file
vẫn tồn tại, JSON vẫn hợp lệ, chỉ là nội dung cũ. Với `anomaly_scan` hệ quả cụ thể là mã vừa mua
hôm qua **vô hình** với lớp bảo vệ tin xấu.

**Cách kiểm đúng** (đã wire trong `anomaly_scan.universe_freshness()`, 2026-08-14):
so `computed_at` với **phiên giao dịch gần nhất mà producer đã có thể chạy** — sáng T2 thì đó là
T6, không phải "hôm nay". Lấy `min()` qua CÁC file, không phải `max()`: một account trễ cũng đủ
làm mất toàn bộ vị thế của account đó. Ngưỡng "producer đáng lẽ xong" = **21:00 ICT** (20:15 + 45'
dự phòng). Fail-open có cảnh báo (quét sổ cũ hơn không quét gì), KHÔNG fail-closed.

## Bẫy (2) — `computed_at` là NGÀY, đừng so bằng giờ
Một cổng độ tươi kiểu "file cũ hơn 15h" sẽ báo động giả mỗi sáng thứ Hai (bản T6 luôn cũ hơn 48h)
và bỏ lọt ca producer chết đúng tối thứ Năm. Phải đếm theo **phiên giao dịch**, có trừ ngày lễ
(`trading_bot.vn_market.is_holiday`).

## Bẫy (3) — `manual_offbook_assets_vnd`
`total_nav` có thể bao gồm tài sản off-book khai thủ công. Cả 2 account hiện = 0 vĩnh viễn
(2026-07-23). Đọc `offbook_stale_warning` trước khi trích `total_nav` cho báo cáo.

## Selfcheck
`mike/agents/Taylor/universe_freshness_selfcheck.py` — 22 ca hermetic (tmpdir + `now_ict` bơm
tường minh, không đọc file production), pass dưới 4 TZ (`Asia/Ho_Chi_Minh`, `America/New_York`,
`UTC`, `env -u TZ`). 3 mutant đều bị giết: `min→max`, bỏ ngưỡng giờ 21:00, bỏ lịch nghỉ.
