# Foreign (khối ngoại) & prop-desk (tự doanh) flow — data probe

**Job**: Taylor_20260723_074919 · **Ngày**: 2026-07-23 · **Kết luận: NO-GO (data blocker, chưa tới bước tín hiệu)**

Nối tiếp chuỗi khám phá nguồn dữ liệu trong ngày (VN30F basis Taylor_20260723_073030 → data OK
nhưng IC~0). Câu hỏi user: có dữ liệu dòng tiền khối ngoại + tự doanh trên **cả cơ sở
(VNINDEX/cổ phiếu) lẫn phái sinh (VN30F)** đủ để nghiên cứu tín hiệu không?

## BƯỚC 1 — Khả năng dữ liệu (vnstock 2.4.9, sources hợp lệ: VCI, KBS)

| Method | VCI | KBS | Ghi chú |
|---|---|---|---|
| `Trading.foreign_trade(...)` | ❌ NotImplementedError | ❌ NotImplementedError | stub — KHÔNG provider nào cài đặt |
| `Trading.prop_trade(...)` (tự doanh) | ❌ NotImplementedError | ❌ NotImplementedError | stub — KHÔNG có dữ liệu |
| `Trading.order_stats/side_stats/trading_stats` | ❌ | ❌ | đều là stub `pass` → NotImplementedError |
| `Trading.price_board([...])` | ✅ | ✅ | **SNAPSHOT** thời gian thực, KHÔNG lịch sử |

**Cơ chế** (`vnstock/base.py::dynamic_method`): các method này chỉ là stub `pass`; decorator
delegate sang provider, provider VCI/KBS **chỉ implement `price_board`** → mọi call khác ném
`NotImplementedError` (bọc trong `tenacity.RetryError`). Xác minh trực tiếp: `t._provider` của
cả VCI và KBS có đúng 1 method callable = `price_board`.

**Con đường foreign DUY NHẤT = `price_board`** — trả về snapshot phiên HIỆN TẠI, mỗi cổ phiếu có:
`foreign_buy_volume`, `foreign_sell_volume`, `foreign_buy_value`, `foreign_sell_value`,
`current_room`, `total_room`. Giá trị THẬT, populated (VCB/FPT/HPG kiểm tra OK).
**Giới hạn chí mạng cho nghiên cứu tín hiệu:**
- Chỉ **1 điểm/phiên hiện tại** — KHÔNG có tham số date-range, KHÔNG backfill lịch sử. Reset mỗi phiên.
- Muốn có chuỗi thời gian phải **tự thu forward** (cron mỗi EOD) → 0 lịch sử để backtest, phải chờ
  tích lũy nhiều tháng/năm mới đủ mẫu.
- **Tự doanh (prop): KHÔNG có** ở bất kỳ đường nào.
- **Phái sinh (VN30F): KHÔNG có** endpoint foreign/prop riêng — snapshot price_board chỉ cho cổ phiếu.

## BƯỚC 2 — Kiểm tra tín hiệu: KHÔNG THỰC HIỆN ĐƯỢC

Không có độ sâu lịch sử → không tính được IC / walk-forward IS-OOS (đúng kỷ luật đã áp cho VN30F
basis). Câu hỏi thực tế nhất của user — "khối ngoại có bán ròng TRƯỚC khi VNI giảm (trước đỉnh
05-18 hay trước đợt cấp tính 07-17→07-22) không, sớm mấy phiên?" — **không trả lời được từ
vnstock** vì không có 1 điểm dữ liệu lịch sử nào. Đây là chặn dữ liệu, không phải NO-GO tín hiệu.

## BƯỚC 3 — Kết luận trung thực

**NO-GO (data blocker).** vnstock (bản cài 2.4.9) KHÔNG cung cấp chuỗi lịch sử dòng tiền khối
ngoại/tự doanh trên cả cơ sở lẫn phái sinh. Chỉ có snapshot foreign phiên hiện tại qua
`price_board` (cổ phiếu, real-time). Repo cũng không có sẵn nguồn nào (đã xác nhận grep).

**Không tự sửa DT5G/production.** Không wire gì.

**Hướng nếu team muốn theo đuổi (cần task riêng, KHÔNG làm trong job này):**
1. Nguồn lịch sử foreign VN có tồn tại ngoài vnstock (HOSE công bố; aggregator cafef/vietstock/
   fireant/fialda). Nhưng: chưa wire, lấy ổn định cần scrape/parse riêng, có thể rate-limit/đổi
   schema. → nếu muốn, dispatch **Winston (data-ops)** đánh giá khả thi + độ sâu lịch sử THẬT,
   ghi vào `mike/kb/data_registry.md` trước khi bất kỳ ai wire (§9 coding-guidelines).
2. Forward-collect `price_board` foreign snapshot mỗi EOD → xây chuỗi từ nay về sau. Rẻ, nhưng
   0 lịch sử ⇒ chỉ hữu ích sau nhiều tháng, và vẫn thiếu tự doanh + phái sinh.
3. Cảnh báo prior: đây là snapshot cổ phiếu cơ sở; dòng foreign trên phái sinh (thứ user nghi
   mang thông tin khác) hoàn toàn không có ở vnstock — muốn có phải nguồn khác (HNX/exchange).

## Artifacts
- `foreign_flow_probe.py` — script tái lập (chứng minh NotImplementedError + snapshot columns).
- (Không có CSV — không có dữ liệu lịch sử để lưu, khác với `vn30f_basis.csv`.)
