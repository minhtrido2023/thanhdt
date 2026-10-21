---
kind: local-file
status: CANONICAL — đã merge (mike master f17a1ec46), dựng chuỗi thật 2026-10-14 22:32 ICT (3.187 phiên từ 2013-12-31 tới 2026-10-13, md5 64dc8dee…), cron 00:35 ICT T3-T7 đã cài
source: data/benchmark/vnindex_tr_daily.csv
group: price-volume
role: VN-Index CÓ cổ tức (tự dựng) — mốc so sánh thứ hai của báo cáo hiệu suất
writer: mike/bin/vnindex_total_return.py --update (cron 00:35 ICT T3–T7, `fund_bench_cron.sh`) · bảng sàn: mike/bin/hose_membership_refresh.py (tuần)
---

# data/benchmark/vnindex_tr_daily.csv

## Là gì
Chuỗi ngày: chỉ số GIÁ chính thức + điểm % cổ tức tự ước (`y_gross`) ⇒ `tr_gross`, `tr_net` (thuế 5%).
`y_t = Σ OShares_{t-1} × DIV_t / Σ Price_{t-1} × OShares_{t-1}` trên rổ mã HOSE theo thời điểm.
HOSE KHÔNG công bố bản có cổ tức của VN-Index (chỉ có VN30/VN100/VNMidcap/VNSmallcap/VNAllshare TRI,
tính cuối ngày — factsheet HOSE-Index 03/2025).

## Nguồn vào
`tav2_bq.ticker` (Price, OShares) · `tav2_bq.corporate_action` (DIV executed) · bảng sàn
`data/benchmark/hose_membership_*.json` · chỉ số giá đối chiếu DNSE chart-api.

## Bẫy
- KHÔNG dùng `universe_pit`/`ticker_prune` làm rổ: đó là rổ lọc thanh khoản, không phải thành phần VN-Index.
- Dùng mọi mã 3 sàn thay HOSE làm `y` cao giả 0,07–0,37 điểm %/năm (đo 2018–2026).
- Danh sách HOSE "hôm nay" áp ngược quá khứ: 2024 lệch +0,40 điểm %.
- Trước 2018 rổ kém tin (chỉ số giá tổng hợp lệch chính thức 1,6–4,0 điểm %/năm 2014–2016).
- Hàng `ticker='VNINDEX'` của BQ SAI ngày 2025-04-09 (1.132,79 = lặp giá 08/04; DNSE 1.094,30) ⇒ luôn đối
  chiếu nguồn thứ hai.
- Dòng DIV có thể vào bảng sau ngày GDKHQ ⇒ 5 phiên gần nhất là `provisional`.
- Số đo tham chiếu (2026-10-13): 2023 y=1,68 · 2024 1,87 · 2025 1,62 · kỳ 2026-07-01→10-13 chênh gộp 0,64.

## File đi kèm (cùng thư mục `data/benchmark/`)
- `hose_membership_<vintage>.json` + `hose_membership_latest.json` — bảng sàn HOSE theo thời điểm; G7 chặn khi > 35 ngày.
- `vnindex_tr_acks.json` — xác nhận của NGƯỜI cho G6 (cổ tức > 30% giá): `{"G6": [{"date","ticker","confirmed_by"}]}`.
  Thêm (18/10/2026): mục `"G4": [{"date","n_prev","n","confirmed_by","reason"}]` — người xác nhận NGÀY rổ đổi >5% số mã (ca 14/10: n_prev=351, n=333 — ~100 mã kém thanh khoản KHÔNG giao dịch ngày đó nên `ticker` không có dòng; bq_admin xác nhận 19/10, KHÔNG phải lỗi nạp; G4-số-mã sẽ lặp lại mỗi khi nhiều mã không khớp lệnh — xem comment ngưỡng G4 trong `vnindex_total_return.py`). Ràng cả GIÁ TRỊ đã xem (dòng `provisional` bị dựng lại mỗi `--update`: số mã khác ⇒ G4 nổ lại). Chỉ che nhánh SỐ MÃ của đúng ngày đó; nhánh vốn hoá có mục RIÊNG `"G4_MC": [{"date","mc_prev","mc","confirmed_by","reason"}]` (vốn hoá rổ VND hai dòng liền nhau, lấy đúng số trong thông báo lỗi G4; số khác ⇒ ack vô hiệu; thêm 21/10/2026); gate khác không có ack; ngày bật lại >5% là G4 riêng cần ack riêng. `benchmark_period` trả `acked_g4_days` để báo cáo chú thích. **Tiền điều kiện trước khi ghi ack**: mã thiếu ngày D (và D+1, vì `t1_ok` làm mã rơi tiếp) không có GDKHQ cổ tức tiền trong `tav2_bq.corporate_action`. Nếu nguyên nhân là thiếu dữ liệu thật (không phải mã không giao dịch) thì ưu tiên lấp dữ liệu BQ hơn ack.
- `benchmark_config.json` — cờ Q2: `{"report_tr_kind": "tr_net"}` (mặc định khi thiếu file, user chốt 2026-10-14)
  hoặc `"tr_gross"`; giá trị lạ ⇒ ô `chưa có số`, KHÔNG đoán. Đổi cờ ⇒ chú thích bảng 3.2 đổi theo, cổng giao báo
  cáo chặn bảng cũ tới khi render lại.

## Consumer
`nav_period_returns.py` (khối `benchmark` mỗi kỳ; mốc = ngày dòng sổ đơn vị làm mốc kỳ — Q1) →
`period_table_32.py` (render bảng 3.2) → `report_delivery_gate._check_benchmark_table` (weekly/monthly).
Thiếu số ⇒ ô `chưa có số (lý do)`; cột có cổ tức thiếu số ở weekly/monthly ⇒ CHẶN gửi (Q9).

## Hồi quy trên dữ liệu thật (KHÔNG thuộc selfcheck khép kín; dung sai 0,02 — vendor có thể sửa lùi OShares)
```bash
python3 - <<'PY'
import sys; sys.path.insert(0, "mike/bin"); import vnindex_total_return as V, datetime as dt
s = V.read_series(V.SERIES_PATH)
for y in (2023, 2025): print(y, round(100*sum(r["y_gross"] for r in s if r["date"].year == y and r["y_gross"]), 2))
print(V.benchmark_period(dt.date(2026,7,1), dt.date(2026,10,13), series=s))
PY
```
Kỳ vọng: 2023 = 1,68 · 2025 = 1,62 · 07-01→10-13 giá −7,915 / gộp −7,276 (chênh 0,64). Đo 2026-10-14 trên bản sao
(sandbox `/tmp/step4_sbx`): khớp cả 3 số.


## Dựng lần đầu trên cây thật (2026-10-14)
BQ chạm trần 1.000.000 dòng khi `--update` kéo cả lịch sử ⇒ lần đầu phải tải panel theo từng năm vào parquet rồi `--update --from-cache <dir> --src2-csv <dnse.csv>` (DNSE cắt tới 13/10 vì BQ VNINDEX chưa có phiên 14/10 — đúng cổng G1). Từ phiên sau cron `--update` chỉ kéo từ mốc sealed nên không chạm trần. `hose_membership_refresh.py` phải gửi User-Agent (VNDirect 403 với `Python-urllib`).
