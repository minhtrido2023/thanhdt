---
kind: external-api
status: CANONICAL
source: DNSEClient.latest_trade(symbol) → trades[boardId="G1"].avgPrice
group: price-volume
scope: UPCOM — cơ sở giá ex-rights (G5 gate), KHÔNG dùng cho HOSE/HNX (đã dùng close, đúng 100%)
owner: data-ops (Winston)
writer: mike/bin/capture_upcom_vwap_eod.sh, cron sau giờ đóng cửa (đề xuất 15:15 ICT — CHƯA CÀI)
---

# DNSE `latest_trade().avgPrice` (board G1) — VWAP UPCOM cho G5

**Status: CANONICAL** cho câu hỏi "tham chiếu GDKHQ của mã UPCOM dùng cơ sở giá nào" — NHƯNG
**lịch sử phải tự dựng** (xem §3), G5 chưa được wire vào nguồn này (Taylor giữ decline-to-speak
cho UPCOM, xem `agents/Taylor/research/upcom_vwap_source_20260818.md`).

## Là gì

`GET /price/{symbol}/trades/latest` (`DNSEClient.latest_trade`, `dnse_api.py:246`) trả về một
bản ghi **cho mỗi board** của mã đó, không phải 1 bản ghi/mã. UPCOM trả nhiều board (G1 = khớp
lệnh liên tục, G4/G7/T1/T4 = thoả thuận/lô lẻ). Field `avgPrice` của board **G1** là giá bình
quân gia quyền theo khối lượng của phiên đó trên board đó — kiểm chứng nội bộ:
`avgPrice × totalVolumeTraded == grossTradeAmount` (đúng cho từng bản ghi, không phải cột suy
diễn).

**Vì sao cần nó**: tham chiếu GDKHQ (ngày quyền) của UPCOM **không** dùng giá đóng cửa phiên
trước làm cơ sở (khác hẳn HOSE/HNX). Đo thật 509 mã, 1 phiên (2026-08-18): cơ sở
`round(avgPrice_G1, tick)` khớp tham chiếu thật **108/114 = 94,7%** mã UPCOM, so với **43/114 =
37,7%** nếu dùng giá đóng cửa. HOSE/HNX vẫn khớp giá đóng cửa 100% (289/289, 106/106) — đối
chứng nội bộ xác nhận đây là luật riêng của UPCOM, không phải lỗi feed. Chi tiết đầy đủ + 6 mã
chưa giải thích được (5,3%): `agents/Taylor/research/upcom_vwap_source_20260818.md`.

## Ai ghi / cadence

Không phải bảng do fleet ghi — đây là **API sống của DNSE**, đọc trực tiếp. Việc của Winston chỉ
là **chụp lại** `avgPrice` mỗi phiên và tích lũy thành lịch sử cục bộ (script §3).

## Bẫy

1. **Chỉ giữ phiên GẦN NHẤT — không có API lịch sử.** Đã kiểm: `GET /price/ohlc`
   (`resolution=1D`) trả `t/o/h/l/c/v`, KHÔNG có trường giá trị giao dịch → không dựng lại VWAP
   được từ đó. `tav2_bq.ticker.Trading_Value` cũng không dùng được (`Price × Volume` mỗi dòng,
   dùng nó để tính VWAP là vòng lặp). ⇒ **PHẢI chụp EOD mỗi phiên**, không có đường tắt đọc
   ngược ngày đã qua.
2. **Cửa sổ đọc hẹp, đọc sai giờ ra rác.** Đọc TRONG phiên (09:00–15:00 ICT) trả `avgPrice` là
   bình quân **dở dang** của chính phiên đang chạy, không phải phiên đã đóng — đối soát với nó
   sẽ ra kết luận sai (đúng loại lỗi mà cổng G6 sinh ra để bắt, chỉ khác chiều thời gian). Chỉ
   đọc trong khoảng **sau ~15:05 ICT tới trước 09:00 ICT hôm sau** (kể cả cuối tuần — DNSE giữ
   nguyên phiên T6 tới sáng T2).
3. **Không lấy phần tử `[0]` raw.** Thứ tự các board trong mảng `trades` KHÔNG ổn định giữa các
   mã (đo thật: VGT trả G1 trước, SCL trả G4 trước) — luôn `filter(t["boardId"] == "G1")` tường
   minh trước khi đọc `avgPrice`.
4. **Không phải mọi mã UPCOM khớp** (5,3%, n=6/114 phiên đo — VNE/MZG/VBB/SDA/AAV/DDG). Phần lớn
   là mã giá thấp (<3.000đ) hoặc thanh khoản cực mỏng (VBB: 1.290cp cả phiên). MZG/VBB còn là 2
   ca ref nằm NGOÀI dải [Low,High] phiên trước — chưa có giả thuyết đứng vững. Đừng coi
   `round(avgPrice, tick)` là đúng tuyệt đối cho MỌI mã UPCOM.
5. **Danh sách mã UPCOM không có sẵn 1 lệnh gọi.** Không có endpoint "liệt kê mã theo sàn" trong
   `dnse_api.py`; sàn của 1 mã chỉ biết được qua `marketId` trong response `secdef`
   (`trading_bot/brokers.py::MARKET_ID_TO_EXCHANGE`, `"UPX"` → UPCOM). Script capture dùng seed
   tĩnh `mike/data/upcom_tickers_seed.csv` (114 mã, trích từ probe Taylor 2026-08-18) — **danh
   sách này sẽ mòn** khi có mã mới niêm yết UPCOM hoặc mã cũ chuyển sàn/hủy niêm yết; cần refresh
   định kỳ bằng cách quét `secdef().marketId` trên ứng viên mới (chưa tự động hoá — ghi chú ở
   đây để không quên).

## Cách gọi đúng

```python
from dnse_api import DNSEClient
c = DNSEClient.from_credentials_file()
resp = c.latest_trade(symbol)          # KHÔNG truyền board_id — cần TOÀN BỘ mảng trades để filter
g1 = [t for t in resp.get("trades", []) if t.get("boardId") == "G1"]
avg_price = g1[0]["avgPrice"] if g1 else None   # None = mã không có board G1 phiên đó
```

## Output

`mike/bin/capture_upcom_vwap_eod.sh` → `mike/data/upcom_vwap_history.csv` (append-only,
cột `date,ticker,avg_price,total_volume_g1`; `avg_price`/`total_volume_g1` rỗng khi mã không có
board G1 phiên đó — KHÔNG bỏ dòng, giữ để phân biệt "không có dữ liệu" với "chưa từng chạy").

## Trạng thái wire vào G5

**CHƯA.** Theo `upcom_vwap_source_20260818.md` §5, thứ tự bắt buộc trước khi bật G5 cho UPCOM:
(a) tích lũy lịch sử vài tuần qua script này, (b) lặp lại probe đối soát ở ≥3 phiên khác nhau
(hiện mới 1 phiên), (c) giải thích hoặc khoanh vùng 6 mã lệch ở bẫy #4, (d) quant-skeptic + user
duyệt (cổng chặn lệnh chạm tiền thật). Việc của Winston dừng ở (a) — build nguồn, KHÔNG sửa G5.
