# PREREG-3 — Chu kỳ hàng hoá TE daily → giá cổ phiếu VN (job Taylor_20261026_075337)

Viết và commit **trước khi** chạy bất kỳ phép tính lợi suất nào của B3 (`b3_patterns.py` chưa tồn tại lúc commit).
B2 (nowcast KQKD) đã chạy trước; B2 chỉ đo tương quan hàng hoá↔BCTC và phản ứng quanh ngày công bố —
không đo các giả thuyết dưới đây. KHÔNG sửa `commodity_cycle_prereg2_20261025/PREREG-2.md`.

## Dữ liệu (đã tra `kb/data_registry/`)
- Hàng hoá: `tav2_bq.commodity_prices` `source='trading_economics' AND cadence='daily'` → `te_daily.parquet`
  (2016-10-25 → 2026-10-23). KHÔNG dùng `commodity_latest`/`unified`, KHÔNG nối với WB.
- PIT: giá ngày d công bố 23:00 ICT ngày d ⇒ tín hiệu tính tới hết ngày d chỉ dùng được ở **giá đóng cửa
  phiên giao dịch thứ 2 sau d** (trễ ≥1 phiên đầy đủ). Mọi TE series dùng `ffill` tối đa 10 ngày lịch.
- Cổ phiếu: `data/bq_cache/ticker/*.parquet` (`Close` điều chỉnh, `PE`), universe `data/bq_cache/universe_pit`.
  Không `ticker_prune`, không `profit_*`.
- Bản đồ: `commodity_map_te.csv` tier **A** (8 họ, 25 mã): rubber_tsr20, crude(brent), urea, dap(di_ammonium),
  sugar, steel_cn(steel SHFE), dry_bulk(baltic_dry), container(containerized_freight_index). Dấu +1 (producer).
- Rổ họ = bình quân đều các mã của họ có `in_universe` tại ngày vào. Lợi suất vượt trội = rổ − bình quân đều
  toàn universe_pit (thành viên tại t−1). MIXED-universe: không (cùng universe_pit cho cả hai chân).
- IS = ngày vào 2017-01-01 → 2022-12-31; OOS = 2023-01-01 → hết dữ liệu.

## Giả thuyết + phép thử (13 trial — Bonferroni ×13 và BH q=0,10 trên 13 p-value)
Ký hiệu P = giá TE daily, MA_L = trung bình trượt L phiên TE.

**H-a momentum/đổi pha (8 trial).** Sự kiện họ f ngày d ⇔ R_d = P_d/MA_L ≥ θ VÀ R_{d−1} < θ, thời gian chết 252 phiên
cùng họ. Vào lệnh = Close phiên thứ 2 sau d. Đo X = lợi suất vượt trội rổ ở chân trời h.
Lưới θ∈{1,05;1,10} × L∈{126;252} × h∈{63;126}. **Ô chính** = θ 1,05 / L 252 / h 63 (giả thuyết post-hoc ĐÃ BIẾT từ
WB monthly — đây là kiểm trên series daily khác). Lưu ý không độc lập: 5/8 họ (rubber, crude, urea, DAP, sugar) trùng
chu kỳ thật đã xem ở nghiên cứu WB ⇒ **phép thử sạch = 3 họ MỚI (steel_cn, dry_bulk, container) + OOS 2023+**, báo riêng.
Cụm: sự kiện có ngày vào cách nhau <126 phiên gộp 1 cụm. Thống kê = TB cụm; CI90 bootstrap theo cụm (10.000, seed 20261026);
p một phía = sign-flip permutation trên TB cụm (10.000).

**H-b lead-lag (3 trial).** Tháng m: c_m = log-return P trong tháng m (P cuối tháng ffill); s_{m+k} = vượt trội rổ
trong tháng lịch m+k, đo từ Close phiên thứ 2 của tháng m+1 nếu k=1 (trễ PIT), k=2,3 tương tự (cửa sổ 1 tháng bắt đầu từ
phiên thứ 2 của tháng m+k). Thống kê = rank-IC gộp (rank trong họ) giữa c_m và s_{m+k}. Trial: k=1,2,3. Mô tả (không
tính trial): k=0 (đồng thời, không giao dịch được) và k=−1 (cổ phiếu dẫn hàng hoá). p = circular-shift permutation trong họ
(2.000), CI bootstrap theo tháng.

**H-c bẫy value đỉnh chu kỳ (1 trial).** Mỗi tháng m (từ 2019-10, cần ≥3 năm lịch sử TE), pct_f = phân vị của TB 63 phiên
gần nhất của P trong chuỗi TB-63 kể từ 2016-10 tới m (expanding). Với mỗi mã tier A có in_universe và ey=1/PE>0 (PE từ
`ticker` tại ngày vào): "value" = ey thuộc nửa trên của universe_pit cùng ngày. Thống kê = TB(X_126 | value ∧ pct≥0,67)
− TB(X_126 | value ∧ pct≤0,33), X_126 = vượt trội từng mã 126 phiên. Giả thuyết bẫy ⇒ hiệu **âm**. Mẫu tháng: chỉ
lấy tháng 1 & 7 (không chồng 6M). Đơn vị độc lập = họ × nửa năm. p = permutation nhãn pct trong từng mã (5.000).

**H-d gap hàng hoá tăng – cổ phiếu chưa phản ứng (1 trial).** Mỗi tháng (lấy tháng 1,4,7,10 để không chồng 3M):
gap ⇔ log-return P 63 phiên ≥ phân vị 67% expanding của chính họ (từ 2016-10, cần ≥24 quan sát) VÀ vượt trội rổ 63 phiên
≤ 0. Thống kê = TB X_63 (rổ, kỳ sau) khi gap − TB X_63 khi không gap, cùng họ. p = permutation nhãn gap trong họ (5.000).

## Tiêu chí (cho từng giả thuyết)
"Có bằng chứng" ⇔ (1) p Bonferroni×13 < 0,05 HOẶC BH q≤0,10, (2) dấu đúng giả thuyết ở cả IS và OOS, (3) LOFO: bỏ 1 họ
bất kỳ vẫn cùng dấu, (4) hơn đường nền vô điều kiện (H-a: X ở mọi ngày vào hằng tháng cùng họ). Trượt bất kỳ ⇒
"không kết luận được / không có edge". Báo MDE ≈ 2,5·SD_cụm/√N_cụm cho H-a; SE cho H-b..d. Không có NAV ⇒ không DSR;
nếu bất kỳ ô nào được nêu là "tốt nhất" thì báo kèm Bonferroni trên đúng số trial.

## Không làm
Không tối ưu tham số ngoài lưới trên, không thêm họ sau khi thấy kết quả (họ tier B chỉ mô tả, ghi nhãn post-hoc).
Không wire, không sửa pin/registry production.
