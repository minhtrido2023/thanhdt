# PREREG — JOB E: quy ước trục-2 breadth-tercile PIT (08-22) có ĐỨNG VỮNG không?

> Job `Taylor_20260927_022338` · viết **TRƯỚC khi chạy bất kỳ script nào của job này**
> (thời điểm: 2026-09-27 ~09:3x ICT) · PAPER-ONLY, **không wire gì**
> Nguồn nghi vấn: `fiinprox_h4_h5_20260927/buoc2_h5.md` §2 "Phát hiện phụ"

## 0. Vì sao có job này (bối cảnh, không phải kết luận)

H5 (job `Taylor_20260926_164143`) báo phát hiện phụ: trục-2 mặc định **breadth-tercile PIT** trượt
4/4 tiêu chí prereg §2.3 của H5 trên panel H5, và tệ hơn trục `retail_net_share` ở mọi ô —
`ic_mom` đảo dấu IS +0,0367 → OOS −0,0385; `ic_ey` −0,0777 (IS, p_BH 0,006) → +0,0025 (OOS, p 0,917).

Mục tiêu job E: **trả lời quy ước 08-22 có đứng vững không và bằng chứng yếu ở đâu** — KHÔNG đề
xuất trục thay thế, KHÔNG đổi quy ước từ một cửa sổ.

## 1. Quan sát tài liệu phải kiểm TRƯỚC khi chạy số (Bước 1, không tốn compute)

Đọc `breadth_vs_radar_matrix_20260822.md` trước khi đo lại: **08-22 dựa trên tiêu chí NÀO?**
Giả thuyết cần xác/phủ bằng trích dẫn nguyên văn, không diễn giải:

- **H1a**: 08-22 chọn breadth vì **CẤU TRÚC MẪU** (hết confound kỷ nguyên, n_effective gấp đôi),
  không vì breadth tách được lợi suất/IC.
- **H1b**: 08-22 **đã tự kết luận là KHÔNG có tín hiệu** ("0/27 ô qua BH FDR 10%", "trục tốt hơn để
  MÔ TẢ, không phải để wire").

Nếu H1a+H1b đúng ⇒ tiêu chí IC-separation của H5 là một tiêu chí **08-22 chưa bao giờ tuyên bố đạt**,
và "trượt 4/4" không tự động là bằng chứng phủ định quy ước. Điều này **không miễn trừ** Bước 2-4:
vẫn phải đo, vì nếu breadth cũng thua ở chính tiêu chí cấu trúc thì quy ước YẾU thật.

## 2. Bước 2 — Tái lập số GỐC 08-22 (câu hỏi 1)

Nguồn gốc còn nguyên: `research/strategy_regime_matrix_20260822/{b2_breadth.csv, panel_daily.csv}`
(2012-01-03→2026-08-21 và 2014-01-02→2026-08-21). Tái lập **4 khối số** của báo cáo gốc:

| Khối | Số gốc phải khớp | Tolerance |
|---|---|---|
| Phân bố tercile | LOW 1.232 / MID 897 / HIGH 978 phiên | **khớp CHÍNH XÁC** |
| n_effective | breadth 262 episode / radar 131; 0% vs 54% số năm bị 1 nhãn chiếm ≥90% | khớp chính xác (đếm) |
| Marginal excess theo tercile | LOW +27,1pp / MID +10,8pp / HIGH +5,4pp; IS/OOS gần trùng | ±0,5pp |
| Hai kiểm tra phá (§5a trễ nhãn, §5b khử beta) | đơn điệu biến mất khi trễ 1 phiên; alpha khử beta ĐẢO thứ tự (LOW +16,3 < MID +20,2 < HIGH +28,1) | ±1,0pp |

**Không khớp** ⇒ báo là lỗi tái lập trước khi kết luận gì về nội dung.

## 3. Bước 3 — IC trên cửa sổ DÀI NHẤT (câu hỏi 2): cửa sổ ngắn hay trục yếu?

Cùng phương pháp `h5_ic.py` (không đổi công thức), chỉ đổi cửa sổ:

- Panel: `bq_cache/ticker` JOIN `bq_cache/universe_pit_q` (`in_universe`), từ **2013-01-02** (mốc
  đầu của cache; universe_pit_q có 2013.parquet). `mom_200` hợp lệ từ ~2013-10; tercile breadth
  (rolling 252 phiên trên `breadth_{t-1}`) hợp lệ từ ~2014-01 ⇒ **cửa sổ IC 2014-01 → 2026-08**
  (~12,7 năm, so với 10,4 năm của H5).
- `mom_200` = Close/Close.shift(200)−1 · `ey` = 1/PE khi PE>0 · `fwd_1m` = Close.shift(−21)/Close−1
  (Close ĐÃ điều chỉnh, đúng vai trò RETURN §9).
- Tách **IS 2014-01→2019-12 / OOS 2020-01→2026-08**.
- IC = Spearman cross-sectional theo ngày (≥30 mã), trung bình trong ô.
- Bootstrap khối theo **THÁNG** B=4.000 cho HIGH−LOW, CI 95%.
- **LOO theo năm**: bỏ từng năm, tính lại HIGH−LOW, báo min/max + có đảo dấu hay không.

**Self-check bắt buộc (khai TRƯỚC):**
1. Chuỗi breadth tự dựng từ parquet phải khớp `b2_breadth.csv` trên đoạn chồng lấn (2013-01-02→
   2026-08-21): báo corr + max |Δ|. Lệch lớn ⇒ dừng, không đọc kết quả IC.
2. Phân bố tercile trên cửa sổ dài: báo n_phien / n_thang_distinct / n_episode mỗi ô.
3. `fwd_1m` không được dùng ngày sau mốc cuối cache.

## 4. Bước 4 — Ba trục cùng KHUÔN (câu hỏi 3)

Cùng panel, cùng IS/OOS, cùng bootstrap, khác nhau chỉ ở nhãn ô:

| Trục | Nhãn | Cửa sổ khả dụng |
|---|---|---|
| **breadth-tercile PIT** (mặc định 08-22) | LOW/MID/HIGH, pctile rolling 252 phiên trên `breadth_{t-1}` | 2014-01→2026-08 |
| **retail_net_share** (từ H5) | LOW/MID/HIGH, pctile rolling 24 **tháng** trên giá trị tháng TRƯỚC | **2016-04→2026-08** (trần nguồn, chết 28/09/2026) |
| **DT5G state** | 5 ô (CRISIS/BEAR/NEUTRAL/BULL/EXBULL) từ `data/vnindex_5state_dt5g_live.csv` cột `state`; **tương tự HIGH−LOW** = mean(BULL∪EXBULL) − mean(CRISIS∪BEAR) | 2014-01→2026-08 |

Cửa sổ retail ngắn hơn là **sự thật của nguồn**, không phải chọn có lợi — mọi so sánh 3 trục phải
báo kèm một bảng phụ **trên cửa sổ GIAO 2016-04→2026-08** để so công bằng, cạnh bảng cửa sổ riêng.

**Khai trial TRƯỚC:** 3 trục × 2 nhân tố × 2 kỳ = **12 so sánh**. BH áp **trong mỗi kỳ trên 6 so
sánh** (3 trục × 2 nhân tố). Bảng cửa sổ giao là **cùng 12 test đó đo lại**, không phải trial mới —
nó là robustness check, báo riêng, không gộp vào BH.

**N thật** = số **tháng độc lập mỗi ô**. Ghi rõ cảnh báo: một tháng lịch có thể góp ngày cho >1
tercile ⇒ các ô KHÔNG rời nhau theo tháng, bootstrap khối HIGH−LOW thừa hưởng sự chồng lấn đó.
Báo cả `n_month_distinct` và `n_episode` (đoạn nhãn liên tục).

## 5. Tiêu chí phán (khai TRƯỚC — 3 kết luận loại trừ nhau)

Dùng đúng bộ 3 + BH của H5 §2.3 để số so được với nhau: (i) HIGH−LOW cùng dấu IS&OOS, (ii) CI OOS
loại 0, (iii) đơn điệu theo tercile ở CẢ IS và OOS, (iv) p_BH OOS < 0,10.

| Kết luận | Điều kiện |
|---|---|
| **A. Quy ước 08-22 ĐỨNG** | Bước 2 tái lập được số gốc (tiêu chí cấu trúc mẫu vẫn đúng: 0% năm bị 1 nhãn chiếm ≥90%, n_eff ~2× radar) **VÀ** Bước 1 xác nhận 08-22 chưa bao giờ tuyên bố IC-separation **VÀ** không trục nào trong Bước 4 qua bộ 3+BH ⇒ H5 đo một tiêu chí khác; "trượt 4/4" không phủ định quy ước |
| **B. Quy ước 08-22 YẾU** | tiêu chí cấu trúc mẫu KHÔNG tái lập được, **HOẶC** một trục khác vượt breadth ở CẢ tiêu chí cấu trúc VÀ bộ 3+BH trên cửa sổ dài ⇒ ghi **câu hỏi mở**, KHÔNG đề xuất trục thay thế (chưa qua cùng chuẩn) |
| **C. KHÔNG KẾT LUẬN ĐƯỢC** | N mỗi ô dưới mức cho phép phân biệt A/B — nói rõ con số N, không phán |

**Cấm trước khi chạy:** (a) không đổi quy ước dựa trên job này dù kết quả thế nào — job này chỉ
phán ĐỨNG/YẾU/KHÔNG-BIẾT; (b) không test HƯỚNG của bất kỳ trục nào (ecology-as-direction REFUTED
2026-07-13); (c) nếu kết luận là **B (YẾU)** ⇒ bắt buộc `verify_finding.sh` (quant-skeptic);
(d) không dùng `profit_*` (look-ahead), không `IN (SELECT DISTINCT ticker FROM ticker_prune)` (§9b).

## 6. Đăng ký nguồn (§9 — tra data_registry TRƯỚC)

| Nguồn | Registry | Trạng thái |
|---|---|---|
| `tav2_mike.universe_pit` (cache `universe_pit_q/*.parquet`) | `price-volume/universe_pit.md` | CANONICAL |
| `tav2_bq.ticker` (cache `ticker/*.parquet`) | `price-volume/ticker_ohlcv_tables.md` | CANONICAL cho lịch sử/backtest |
| `data/vnindex_5state_dt5g_live.csv` | `market-state/` | DT5G production (KHÔNG dùng `vnindex_5state` = v3.4b BASE) |
| `h5_retail_monthly.csv` | DERIVED (H5, upstream FiinPro-X trial CHẾT 28/09/2026) | DESCRIPTIVE-ONLY |
