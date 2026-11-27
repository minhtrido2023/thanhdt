# Kế hoạch Nghiên cứu Phân tích Kỹ thuật v2 — DRI: Giải phẫu Hành vi NĐT & Thời điểm Ra/Vào Trung hạn

> **Ngày lập:** 2026-11-27 · **Trạng thái:** ĐÃ DUYỆT TRIỂN KHAI (user duyệt 2026-11-27) · **Phạm vi:** Nghiên cứu thuần (RESEARCH-ONLY), không tự động sửa code production/bot/registry.
> **Liên kết hồ sơ liên quan:** [`dri-dd-summary-20261030.md`](dri-dd-summary-20261030.md) · [`dri-triggers-20261027.md`](dri-triggers-20261027.md) · [`vn_sector_read_rubber_20261027.md`](../data_registry/market-state/vn_sector_read_rubber_20261027.md) · [`dd_price_zones.json`](../dd_price_zones.json)

---

## 0. Chốt mục tiêu & định hướng thiết kế (từ user 2026-11-27)

1. **Vai trò mục tiêu — Phương án (A):** Phân tích kỹ thuật đóng vai trò **lớp chọn thời điểm vào/ra & quản trị rủi ro bổ trợ** cho định giá DD + chu kỳ hàng hoá cao su (chỉ mua khi vùng giá hợp lý theo DD và kỹ thuật xác nhận cạn bán/ổn định; tỉa khi đầu cơ hưng phấn kéo giãn hoặc gãy cấu trúc). *(Hiệu quả giao dịch thuần kỹ thuật không dùng DD vẫn được đo làm mốc đối chứng ở P2.)*
2. **Tách ảnh hưởng & định danh nhóm NĐT — KHÔNG gom chung theo ngành để tìm pattern:**
   - **Tách ảnh hưởng (Factor Decomposition):** Dùng `VNINDEX` + `TSR20` + nhóm cao su HOSE (`DPR/PHR/TRC/GVR`, đối chứng ngược `DRC`) **chỉ để bóc tách phương sai**, lấy ra phần dư đặc thù `ε_DRI`.
   - **Định danh hành vi NĐT (Clientele Profiling):** DRI (UPCoM) có chữ ký nhà đầu tư ngắn hạn/đầu cơ khác hẳn cổ phiếu cùng ngành (xem §1). Thay vì ép tìm pattern chung với DPR/PHR/GVR, ta đo chữ ký hành vi riêng của DRI và kiểm định chéo trên **Behavioral Cohort** (nhóm cổ phiếu có cùng cấu trúc biến động + vòng quay trôi nổi đột biến, lọc PIT trên `universe_pit`, tách riêng nhánh có nền tảng cơ bản tốt/chu kỳ hàng hoá) để so trực tiếp hiệu quả chuyển giao với *Industry Peer*.
3. **Chân trời trọng tâm:** **Trung hạn (1–6 tháng / 20–120 phiên)** theo sóng hàng hoá và dòng tiền, có kiểm tra chéo chân trời 20 phiên.

---

## 1. Dữ liệu nền & Ràng buộc đã đo (tới `2026-11-26`)

| Chỉ tiêu (đo từ `bq_cache/ticker/*.parquet` & `mike/data`) | DRI (UPCoM) | DPR (HOSE) | PHR (HOSE) | TRC (HOSE) | GVR (HOSE) | VN-Index |
|---|---:|---:|---:|---:|---:|---:|
| Thời kỳ / Số phiên | `2017-05-23..2026-11-26` (2.379) | 3.467 | 3.467 | 3.467 | 2.164 | 3.467 |
| Biến động năm (toàn kỳ / `2024+`) | **48,5% / 43,8%** | 30,4% / 32,3% | 36,3% / 34,1% | 91,6% / 33,9% | 46,4% / 42,2% | 18,2% / 18,3% |
| Tỷ lệ phiên `\|r\| ≥ 5%` · Phiên `\|r\| ≥ 10%` | **8,7% · 36 phiên** | 3,4% · 0 | 6,1% · 0 | 4,7% · 3 | 10,7% · 8 | 0,4% · 0 |
| Max Drawdown lịch sử | **−78,8%** | −59,1% | −62,4% | −85,5% | −75,6% | −45,3% |
| Vốn hoá 2024–26 (ước lượng từ `OShares` = 73,2tr) | ~886 tỷ | ~2.772 tỷ | ~3.719 tỷ | ~507 tỷ | ~106.000 tỷ | — |
| ADV trung vị 2024–26 · Độ nổ (`P90/Med`) | 8,33 tỷ · **3,17×** | 19,34 tỷ · 2,72× | 17,91 tỷ · 3,37× | 3,64 tỷ · 4,66× | 92,93 tỷ · 2,39× | — |
| **Vòng quay ngày P90 (`Volume/OShares`)** | **2,59%/phiên** | 1,44%/phiên | 0,75%/phiên | 0,78%/phiên | 0,17%/phiên | — |
| Tương quan tháng với **TSR20** | **+0,47** | +0,33 | +0,23 | +0,26 | — | — |

- **Cấu trúc sở hữu & free-float DRI:** Cổ đông lớn Dakruco nắm 45% ⇒ free-float thực tế ~55% (~40,26 triệu cp). Những phiên đỉnh vòng quay (`2025-02-17`: 18,16% tổng cp; `2026-03-02`: 13,41%; `2026-01-09`: 6,64%) tương đương thay máu ~12–33% lượng trôi nổi trong 1 phiên.
- **Hiện trạng giá tới `2026-11-26`:** Giá `12.100 đ` (−28,4% từ đỉnh `16.900` ngày `2026-10-09`; `+1,4% YTD` 2026), dưới cận dưới P10 DD rev 5 (`12.908`, tâm `15.257`, `dd_price_zones.json`), nhưng vẫn cao hơn vùng định giá cơ sở có tái canh r4 (`9,1–11,1k`, ngưỡng biên ≥15% ≲7,9k).
- **Bài học NO-GO đã khoá của hệ thống (KHÔNG lặp lại):**
  - Phân kỳ RSI thuần: NO-GO (`0/48` trial, DSR `0,005`, PBO `0,74` — [`livermore-divergence-nogo-20261114.md`](livermore-divergence-nogo-20261114.md)).
  - Trường phái nến/VSA/Darvas/stopping volume làm tín hiệu mua: NO-GO ([`ta-schools-vn-20261025.md`](ta-schools-vn-20261025.md)).
  - Breakout momentum ngắn hạn (`MOM_N/MOM_S`): đã đóng khỏi production ([`momentum-deals.md`](momentum-deals.md)).
  - Limit −2% / chờ pullback 2 phiên ngắn hạn cho lệnh đã kích hoạt: NO-GO do adverse selection ([`entry_risk_tech_20261022/REPORT.md`](../../agents/Taylor/research/entry_risk_tech_20261022/REPORT.md)).
  - Hàng hoá dự báo tốt KQKD (cao su IC `0,48`), nhưng cổ phiếu phản ánh ngay trong quý và có xu hướng bị bán sau BCTC OOS (`b = −0,13, t = −2,3`) ([`commodity_cycle_te_20261026/REPORT.md`](../../agents/Taylor/research/commodity_cycle_te_20261026/REPORT.md)).

---

## 2. Lộ trình 5 pha (`P0 → P4`)

### Pha P0 — Kiểm toán dữ liệu, xử lý bẫy UPCoM, Free-Float & Khoá `PREREG`
1. **Giải mã và làm sạch chuỗi giá UPCoM (`Close` vs `Price`):** Đối chiếu `tav2_bq.ticker` với `corporate_action_snapshots` (dedupe theo `id` lấy `snapshot_date` mới nhất) và `upcom_vwap_history.csv` (`avg_price` đơn vị nghìn đồng, dùng cơ sở tham chiếu VWAP board G1 trên UPCoM). Làm rõ nguyên nhân `Close ≠ Price` ±100đ trên 4/47 phiên sau ex-date `2026-09-22` và dao động `Close/Price` `0,925–0,940` trước ex-date; dựng `Close_clean` sạch và ghi nhận `p0_audit_summary.json`.
2. **Đồng bộ hàng hoá & chế độ thị trường PIT:** Cập nhật `TSR20`, `Brent`, `synthetic_rubber` (TE daily) và `butadiene_rubber` (SunSirs daily) từ `tav2_bq.commodity_prices` tới `2026-11-26` (không nối `TSR20` USc/kg÷100 với WB `RSS3` `rubber_monthly.csv`); tích hợp `vnindex_5state_dt5g_live.parquet` (CANONICAL), `Release_Date` từ `ticker_financial.parquet` và `public_date` từ `tav2_bq.stock_news`. Cấm cứng mọi cột look-ahead (`profit_*`, `_center_*`, `PC1W..PC2M`, `Open_1D`, `O1W..O2Y`, `Pattern_*_3Y`).
3. **Dựng danh mục Behavioral Cohort (PIT từng năm `2015–2026`):** Dùng dữ liệu năm `Y-1` trong `universe_pit` (0 look-ahead) để gán nhãn tập cổ phiếu có tính chất dòng tiền tương đồng DRI (biến động năm `≥38%`, vòng quay P90 `≥0,8%`, độ nổ thanh khoản `P90/Med ≥ 2,5×`, vốn hoá vừa thanh khoản `300–15.000 tỷ`), kèm bản đối chiếu tỷ lệ tương đối theo năm và phân nhóm nền tảng chất lượng (`ROE_Min3Y ≥ 0 & CF_OA_5Y > 0` / `fa_ratings_8l ≤ 3`).
4. **Khoá `PREREG_P2.md` (MD5)** sau khi có kết quả P1, trước khi chạy backtest P2 (`N_TRIALS ≤ 12`).

### Pha P1 — Giải phẫu Biến động & Hồ sơ Hành vi NĐT riêng của DRI (`2017–2026`)
- **Trục 1 — Phân rã phương sai đa nhân tố (tách, không gộp):** Hồi quy ngày/tuần/tháng (toàn kỳ & trượt 120 phiên) theo `VNINDEX`, `TSR20` (đồng thời & trễ), nhóm cao su HOSE (`DPR/PHR/TRC/GVR`, đối chứng `DRC`), và phần dư đặc thù `ε_DRI`. Phân rã các nhịp sóng lớn 2025–2026 (gồm T9–T11/2026).
- **Trục 2 — Bản đồ cấu trúc sóng (ZigZag mô tả `±15% / ±20%`):** Thời lượng, tốc độ tăng vs rơi, độ giãn khỏi `MA20/50/200`, `VAP1M/3M`, `ATR20`, và vòng quay free-float tích lũy từng con sóng.
- **Trục 3 — Hồ sơ hành vi NĐT ngắn hạn (DRI vs Industry Peers vs Behavioral Cohort):**
  - *(3a)* **Climax vòng quay free-float** (`turn_total_pct ≥ 250d P95`, tích lũy 20 phiên) phân tầng theo vị trí **Đang kéo giãn** vs **Tại nền**.
  - *(3b)* **Phản xạ FOMO (`Chase-vs-Fade`)**: Hiệu suất 5/10/20/60 phiên sau phiên nổ tăng `≥+5%` (hoặc `≥+3% & vol ≥ 2×`).
  - *(3c)* **Rũ kẹp hàng & Cạn cung (`Washout & Dry-Up`)**: Trong pha giảm `≥15%/≥20%` từ đỉnh 120 phiên, so sánh *dao rơi còn vol xả* vs *cạn cung đầu cơ* (`Volume < 0,75 × P50`, biên độ co hẹp, giá ngừng phá đáy) + vùng kẹp hàng `VAP3M`.
  - *(3d)* **Vi cấu trúc UPCoM**: Volatility clustering sau phiên `|r| ≥ 5%/10%`, phân tích độ lệch `Price` cuối phiên vs `avg_price` G1 (`upcom_vwap_history.csv`).
- **Trục 4 — Event Study quanh `Release_Date` BCTC & Tin sự kiện (`stock_news`):** Kiểm định cơ chế "ra tin tốt bị bán" theo run-up trước kỳ công bố và xu hướng `TSR20`.
- **Trục 5 — Độ trễ Hàng hoá–Cổ phiếu, Phân kỳ tương đối, Mùa vụ & Độ ổn định thời gian:** Cross-correlation tuần `[-4..+4]`, spread `DRI − β·TSR20`, mùa vụ T1–T12, và đối chiếu độ bền các đặc trưng hành vi giữa **`2017–2021` vs `2022–2026` vs `2024–2026`**.
- **Đầu ra cuối P1:** Báo cáo P0–P1 + Chẩn đoán trạng thái DRI tại `2026-11-26` (mô tả thuần túy) + Dự thảo `PREREG_P2.md` để user/planner duyệt trước khi chạy P2.

### Pha P2 — Kiểm định Quy tắc Vào/Ra Trung hạn (`1–6 tháng`, `N_TRIALS ≤ 12`, sau khi duyệt `PREREG_P2`)
- Chạy song song 2 tầng đối chứng: **Behavioral Cohort** vs **Industry Peers** theo chuẩn walk-forward `IS (2014–2020) / OOS (2021–2026)`, `threads=1`, `Open(t+1)`, đủ phí + thuế + trượt giá, tính **DSR, PBO (CSCV), BH-FDR, placebo hoán vị khối tháng**.
- Chuyển giao không tinh chỉnh lại sang **DRI (`2017–2026`)**, kiểm Leave-One-Year-Out, đo giá trị gia tăng so với `B0` (Buy & Hold DRI), `B1` (Hurdle tiền mặt ~7,4–8,5%/năm), `B2` (chỉ vùng DD không lớp kỹ thuật).

### Pha P3 — Playbook Thực chiến (`DD × Hành vi NĐT DRI`) & Phản biện `quant-skeptic`
- Đóng gói quy tắc vào/tỉa/dừng lỗ thích nghi ATR & sizing `∝ 1/ATR20`, xác minh độc lập qua `bin/verify_finding.sh` (`CONFIRMED` bắt buộc trước khi coi là khung chính thức), và đánh giá thực tế vùng `12.100` hiện tại.

### Pha P4 — Mở rộng Cảnh báo Chỉ-đọc & Theo dõi Tiến-tới (tuỳ chọn sau `CONFIRMED`)
- Bổ sung lớp cảnh báo hành vi/kỹ thuật chỉ-đọc vào `bin/dri_buy_gate_watch.py` (không tự đặt lệnh) và log tiến-tới append-only.
