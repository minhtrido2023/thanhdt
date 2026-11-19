# PREREG — A4 nowcast KQKD 12 họ (job Taylor_20261119_090443, 19/11/2026)

Viết và commit TRƯỚC khi tính bất kỳ IC nào của 12 họ mới. Đo **KQKD**, không đo giá cổ phiếu. Không wire gì.
Bản đồ đóng băng: `map_v2.csv` md5 `91bffcc87cf1bb307c646737c7390ef5` (commit `a968cc098`).
Dữ liệu chụp 1 lần 19/11: `commodity_snapshot_20261119.parquet`, `macro_snapshot_20261119.parquet` (`fetch_data.py`,
source tường minh), `data/hog_price_vn.csv`, `data/bq_cache/{ticker,universe_pit,ticker_financial.parquet}`.

## 0. Chân đối chứng (đã chạy TRƯỚC prereg này — tái lập, không phải kết quả mới)
`control_rerun.py` chạy lại nguyên văn `commodity_cycle_te_20261026/b2_nowcast.py` trên cache hiện tại:
IC gộp tier A (c_yoy→np_d, ALL) = **0,460** (pin 0,450; lệch 0,010 ≤ 0,02 ⇒ **PASS**), CI90 [0,342; 0,555],
n_famq 254 (pin 250; +4 họ×quý do ticker_financial cập nhật), IS 0,496 (= pin), OOS 0,371 (pin 0,353).

## 1. Đơn vị, biến
- Dòng panel = (mã, quý) khi: tín hiệu quý có đủ dữ liệu; `sig_day` = phiên đầu tiên ≥ cuối quý + max(2, `pit_lag_days`)
  ngày lịch; `Release_Date` (bản công bố ĐẦU TIÊN, `common.fin()`) > `sig_day`; mã ∈ `universe_pit` tại `sig_day`.
- Đích chính `np_d` = (NP_P0 − NP_P4)/Revenue_P4, cắt ±0,5. Mô tả: `rev_yoy` = log(Rev_P0/Rev_P4), `gpm_d` = GPM_P0 − GPM_P4.
- Họ × quý: `c` chung của họ, đích = trung vị qua các mã. **N = số họ×quý**, không phải số dòng.
- Gộp quý của series: daily TE/SunSirs/tỷ giá/lãi suất cần ≥ 40 quan sát/quý; giá heo ≥ 20; series tháng cần đủ 3 tháng.
- Tín hiệu `c` (đã nhân dấu kỳ vọng ⇒ kỳ vọng IC > 0):
  1. Thép: S = steel − 1,6·iron_ore_cny − 0,5·coke (CNY/T); c = (S̄_q − S̄_{q−4}) / steel̄_{q−4}.
  2. Heo: feed (VND/kg) = 0,65·corn + 0,25·SBM (corn USd/bu → USD/kg = v/100/25,4 × usdvnd; SBM CNY/T /1000 × usdvnd/usdcny);
     M = hog (TB 3 miền) − 2,8·feed; c = (M̄_q − M̄_{q−4}) / hoḡ_{q−4}.
  3. Phốt pho vàng: c = log(P̄_q/P̄_{q−4}).  4. Xút: như 3 (**chỉ mô tả**, xem §3).
  5. Polyester: S = PSF − 0,86·PTA − 0,34·MEG; c = (S̄_q − S̄_{q−4}) / PSF̄_{q−4}.
  6. PVC: c = −log(P̄_q/P̄_{q−4}).
  7. Bán lẻ: c = TB 3 tháng `vn_retail_sales_yoy`/100.
  8. Môi giới: c = log(GTGD TB phiên_q / GTGD TB phiên_{q−4}), GTGD = Σ `Trading_Value` mọi mã trong `data/bq_cache/ticker`.
  9. Hàng không/sân bay: c = log(Σ arrivals_q / Σ_{q−4}) (ACV, SCS, SAS; HVN/VJC chỉ mô tả, ngoài thống kê).
  10. Cảng: c = log(Σ(X+M)_q / Σ_{q−4}).  11. Ô tô: c = log(Σ xe_q / Σ_{q−4}).
  12. Ngân hàng: c = −[Δ4q TB_q(interbank_3m − policy_rate) + Δ4q TB_q(bond_10y)] (pp; policy_rate tháng ffill theo ngày).
- Độ trễ công bố series tháng (7, 9, 10, 11) là **GIẢ ĐỊNH** (+10/+10/+15/+20 ngày) vì `macro_indicator` chưa có vintage
  (A1 đang dựng song song); giá trị là bản hiện hành, có thể đã revise. Giới hạn BCTC: bản ingest, không phải bản công bố đầu.

## 2. Thống kê (từng họ)
- IC = Spearman(c, np_d) trên chuỗi họ×quý xếp theo thời gian. Cần n ≥ 12 họ×quý, nếu không ghi "không đủ N".
- CI90: moving-block bootstrap vòng, khối 4 quý, 5.000 lần, seed 20261119, phân vị 5/95.
- p: **dịch vòng** c so với np_d, liệt kê ĐỦ mọi độ dịch k = 1..n−1 (cùng thủ tục cho mọi họ);
  p = (1 + #{|IC_k| ≥ |IC_0|}) / n, hai phía. **Giới hạn biết trước:** p nhỏ nhất = 1/n (n ≈ 20–36 ⇒ 0,028–0,05);
  BH q<0,10 trên m = 12 vì thế chỉ đạt được khi nhiều họ cùng có p nhỏ. Không đổi phép thử sau khi thấy kết quả.
- Hai nửa: chia chuỗi quý tại floor(n/2); IC từng nửa.
- BH-FDR trên **12** p (họ 4 gán p = 1, không đủ điều kiện GO).

## 3. GO / NO-GO (từng họ, khai trước)
GO ⇔ IC ≥ 0,25 **và** CI90 cận dưới > 0 **và** IC hai nửa đều > 0 **và** BH q < 0,10 **và** n ≥ 12.
Trượt bất kỳ điều nào ⇒ ghi "không đạt", **không thử biến thể** (hệ số, độ trễ, dấu, mã, cửa sổ).
Họ 4 (xút, lịch sử từ 2023-09) và HVN/VJC: chỉ mô tả.
Số trial tích luỹ dòng hàng hoá/ngành: 17 + 12 = **29**.

## 4. Đầu ra
`a4_nowcast.py` → `a4_panel.csv`, `a4_famq.csv`, `a4_results.csv`, `a4_results.json`; `REPORT.md` kết luận đầu trang.
Khuyến nghị PREREG-5 (B1) chỉ khi có ≥ 1 họ GO.
