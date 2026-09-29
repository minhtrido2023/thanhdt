# 2026-08-17 — Gate corp-action từ chối GIẢ suốt 10 ngày vì đọc `ticker.Price` đông cứng (VHM 1:1)

**Triệu chứng.** ops_health_check (SpaceX, 19:21 ICT) cảnh báo mục 6: `1 sự kiện corp-action đã
alert >7 ngày trước, CHƯA resolve vào shares_outstanding_live: ['VHM|2026-08-07']`. Backlog ghi
`days_since_ex_date: 10`. Cảnh báo này đúng — nhưng cách diễn giải mặc định của nó ("Winston chưa
phân loại cash/stock") thì SAI: sự kiện đã được scanner phát hiện đúng ngày 2026-08-07, và có một
gate đã âm thầm TỪ CHỐI ghi mỗi lần chạy.

**Sự kiện thật.** VHM trả cổ tức 2025 bằng cổ phiếu **tỷ lệ 100% (1:1)**, ex-date 2026-08-07, phát
hành thêm **4,1 tỷ cp** (41.074 tỷ đồng mệnh giá) — nguồn mekongasean/DNSE/Vietstock. Dữ liệu BQ
xác nhận độc lập: hệ số điều chỉnh `Close/Price` bước đúng ×2,0000 tại 08-07 (0,5 → 1,0) và
`vnstock` VCI adj(ex) khớp BQ adj(ex) 0,00%. Cấu phần TIỀN MẶT của cùng đợt chia có ex-date riêng
cuối 06/2026 (factor 0,4815 → 0,5), KHÔNG thuộc ex-date này.

**Root cause.** `update_shares_live.py::process()` lấy `cum_raw` bằng `cum_rows.iloc[-1]["raw"]` —
phiên cum cuối cùng trước ex-date. Phiên đó là **2026-08-06**, đúng dòng nằm trong bẫy đã được ghi
nhận `kb/data_registry/price-volume/ticker_price_stale_on_exdate.md`: `ticker.Price` đông cứng ở
153.000 (giá thật 154.200) trong khi `Close` đã chạy 76.500 → 77.100. Gate tính
`theo_ex = 153.000/2 = 76.500` so với `cum_adj = 77.100` ⇒ lệch **0,78% > tol 0,5%** ⇒
`✗ GATE FAILED — REFUSING to write` cho một ca 1:1 sách giáo khoa.

Hai tầng làm nó tồn tại 10 ngày:
1. Gate từ chối **im lặng** (in ra stdout của cron 18:40, không post bus, không WARN riêng) — nhìn
   từ ops_health_check nó không phân biệt được với "chưa ai đụng tới".
2. `CORP_ACTIONS` chưa có mục VHM nên nhánh chạy dừng sớm ở "no declared action"; gate chỉ lộ ra
   sau khi khai báo. Tức là nếu chỉ nhìn log scan sẽ không thấy gate là thủ phạm.

**Hệ quả.** `OShares` của VHM đứng ở 4.107.412.004 thay vì 8.214.824.008 trong 10 ngày ⇒ mọi
consumer LEFT JOIN `shares_outstanding_live` để sửa OShares quý-cũ vẫn thấy **PE/PB thấp một nửa**
⇒ VHM screen ra "rẻ gấp đôi". Không chạm money-path (không có gate đặt lệnh nào đọc bảng này), và
consumer KHÔNG join thì vốn dĩ đã dùng số quý cũ — bảng override sinh ra chính là để rút ngắn cửa
sổ sai này, nên nó hỏng = cửa sổ sai kéo dài như khi chưa có bảng.

**Fix** (commit `ced702ac`, repo gốc). Trong `process()`, đi lùi tới phiên cum gần nhất KHÔNG mang
chữ ký đông cứng (`raw` trùng đúng phiên trước trong khi `adj` đã đổi) → dùng 2026-08-05
(raw 153.000 / adj 76.500) ⇒ gate **0,00%**. Kèm khai báo `CORP_ACTIONS["VHM"]`
(`stock_div_ratio=1.0`, `cash_div_per_share=0.0`) với nguồn công bố.

**Verify (artifact, không tự báo).**
- `--detect-only`: gate 0,00%; vnstock adj(ex) 73.000 vs BQ adj(ex) 73.000 = 0,00% diff.
- Ghi thật: `shares_outstanding_live` VHM|2026-08-07 = `oshares 8.214.824.008`,
  `prev_oshares 4.107.412.004`, `stock_div_ratio 1.0`, `price_adj_factor 0.5`. Số cổ phiếu tăng
  thêm **khớp từng cổ phiếu** với công bố 4.107.412.004.
- Regression ACB/HDC/EVG: guard `[stale-raw]` KHÔNG fire, gate giữ nguyên 0,01% / 0,04% / 0,03%.
- `--scan` chạy lại: 0 candidate tồn đọng, `data/corp_action_backlog.json` `pending: []`.
- `ops_health_check.sh --account SpaceX`: `✅ Corp-action backlog: không có sự kiện nào tồn đọng
  >7 ngày`, không còn cảnh báo nào.

**Bài học.** Đây là **nạn nhân thứ 2** của cùng một bẫy `ticker.Price` (nạn nhân đã biết:
`lag_entry_anchor.py:105`, chưa vá — vùng Taylor/DollarBill). Điểm mới đáng ghi: một gate an toàn
đọc `ticker.Price` không gây ghi SAI — nó gây **từ chối GIẢ**, và từ chối im lặng thì nhìn giống
hệt "chưa ai xử lý", nên nó sống được cả tuần dưới mắt một checker đang chạy đúng. Gate từ chối
nên nói ra lý do ở nơi có người đọc (bus/WARN), không chỉ stdout của cron.
