# VÒNG 3 BAL — TIỀN ĐĂNG KÝ
## Trục A: nới cổng vào BAL trong NEUTRAL · Trục B: median lệnh BAL âm
job `Taylor_20260909_121342` · viết **TRƯỚC** khi chạy bất kỳ chân treatment nào · PAPER-ONLY

Mandate user 2026-09-09 19:12 ICT: (A) *"nghiên cứu tiếp việc nới cổng đi"* · (B) *"vào 2025 theo
BAL thì 50% khả năng đã lỗ — cải thiện hay tránh được không?"*

Bối cảnh bắt buộc mang theo: **vòng 1 NO-GO** (H-EY tilt; không indicator kỹ thuật nào sống OOS sau
BH) và **vòng 2 NO-GO cả 4 chân** (adaptive exit). Hai sự thật cơ học đã chốt ở vòng 2 và KHÔNG
được đo lại: (i) re-entry khi state về {4,5} vốn đã là hành vi mặc định; (ii) `PARK_STATES="3:0.7"`
⇒ vốn BAL rảnh trong NEUTRAL tự chảy 70% vào custom30V, nên "thoát"/"vào" trong NEUTRAL là **ĐỔI
RỔ**, không phải đổi mức rủi ro.

---

## 0. Vì sao trục A là ĐỔI THIẾT KẾ, và điều đó buộc thêm một đối chứng

Vòng 1 và 2 là **overlay** (nghiêng khoá sắp xếp, thêm luật thoát) — sai thì tắt env var là xong.
Trục A đụng **cổng sinh tín hiệu** (`signal_v11_sql.py:127-137`), thứ định nghĩa BAL là gì. Vì vậy
ngoài 7 tiêu chí GO, chân nào thắng còn phải qua **đối chứng phân rã exposure** ở §6 — nếu delta
chỉ đến từ việc nâng beta ròng thì đó không phải edge của BAL, và báo cáo phải nói thẳng.

**Sự thật nền (Phần 1 §3, §5):**
- 2026: BAL bị khoá 100/112 phiên ở state 3; nhịp +10,73% của VNI tháng 4 rơi trọn vào vùng khoá.
- Toàn kỳ, tỷ trọng CỔ PHIẾU trung bình của BAL: NEUTRAL **21,7%** vs BULL **92,2%**.
- Nhưng tổng tỷ trọng CỔ PHẦN (cổ phiếu + rổ parking custom30V) trong NEUTRAL **không** thấp —
  parking chiếm 70% book. ⇒ giả thuyết H0 cơ học của trục A: **nới cổng ≈ hoán đổi rổ custom30V
  lấy rổ momentum, không phải tăng rủi ro.** §6 kiểm định chính điều này.

## 1. Cổng hiện tại — đọc từ code, không suy đoán

| tier BAL (`TIER_BAL`, kể cả biến thể `_W`) | nhánh CASE | states mở được |
|---|---|---|
| `MEGA` | `signal_v11_sql.py:127` | {4,5} |
| `MOMENTUM` | `:129` | {4,5} |
| `DEEP_VALUE_RECOVERY` | `:134` | {4,5} |
| `RE_BACKLOG_BUY` | D1-override `pt_v23_audit_2014.py:793` | **{3,4,5}** — đã vào được NEUTRAL |

Các ràng buộc KHÁC giữ nguyên ở mọi chân (không chân nào đụng tới):
SV_TIGHT (state 3 ⇒ `days_since_release ≤ 60`), `AVOID_overheated`, `AVOID_exbull` (state 5),
`liq ≥ 1e9`, sector-8 cap 4, `MAX_POS_V11 = 12`, hold 45 phiên, stop −20%, DT5G, allocator,
CAPIT, custom30V, `filter.json`, `macro_state_live.py`.

**Tác dụng phụ đã biết và chấp nhận trước:** khi mở nhánh 127/129 sang state 3, các dòng trước đây
mang nhãn `MOMENTUM_N` / `MOMENTUM_S_N` (state 3) sẽ bị nhánh trên **che** và đổi nhãn thành
`MEGA`/`MOMENTUM`. Cả hai nhãn cũ đã **đóng khỏi `TIER_BAL` từ 2026-07-12** nên trước nay không mở
được lệnh nào; việc đổi nhãn KHÔNG phải mở lại kênh MOM_N/MOM_S đã bị bác bỏ — nó chính LÀ nội
dung của treatment (cho phép mở lệnh trong NEUTRAL). Nói ra ở đây để không bị hiểu là lách luật
"MOM_N/MOM_S đã gỡ production".

## 2. Bốn chân trục A (N_trials trục A = 4). Không thêm chân sau khi thấy số.

Env `NGATE` (mặc định `off` = byte-identical). Mọi hằng số đều **đã tồn tại trong production** —
không grid-search, không ngưỡng tự chế.

| chân | luật | hằng số lấy từ đâu |
|---|---|---|
| **A1 — OPEN** | 3 nhánh CASE (`MEGA`,`MOMENTUM`,`DEEP_VALUE_RECOVERY`) đổi `state5 IN (4,5)` → `state5 IN (3,4,5)`. Không đổi gì khác. | **0 hằng số mới** — chỉ là tập state của `RE_BACKLOG_BUY` đang chạy. |
| **A2 — OPEN+VALUE** | Như A1 nhưng nhánh state-3 phải thêm `pe_z < -0.5`. Ở states {4,5} không đổi. | `-0.5` = **đúng ngưỡng `pe_z` của `COMPOUNDER_BUY`** (`:133`), đang chạy production. |
| **A3 — OPEN+HALFSIZE** | Như A1, nhưng lệnh khớp trong state 3 nhận **nửa tỷ trọng** (5% thay vì 10%) cho 3 tier được mở (+ biến thể `_W`). `RE_BACKLOG_BUY` và `CAPIT_*` giữ nguyên. | `0.05` = `WEAK_SIZE` của `regime_size_overlay.py`; cơ chế = `tier_weights_by_state`, đúng mẫu hàm production `_lag_disc_twbs` (`pt_v23_audit_2014.py:2002`). |
| **A4 — OPEN+BREADTH** | Như A1, nhưng chỉ mở trong state 3 khi **breadth-tercile PIT của phiên t−1 = HIGH**. Ngoài tercile HIGH, dòng state-3 bị gắn `AVOID_breadth_gate` (không mở được, không ảnh hưởng {4,5}). | Quy ước trục-2 chốt **2026-08-22**: breadth = %(Close>MA200) trên `universe_pit`, phân vị rolling **252** phiên trước, tercile 1/3–2/3, dùng breadth_{t−1}. |

**Vì sao 4 chân này, không phải 4 chân khác.** A1 là chân trần (cần để biết cổng có phải là nút
cổ chai không). A2/A3/A4 là ba cách BÙ RỦI RO khác nhau về bản chất — chất lượng định giá / kích
thước / điều kiện thị trường — nên không suy biến vào nhau. Không có chân "A1 + siết `ta`" vì mọi
ngưỡng `ta` cao hơn đều là **hằng số tự chế** (155/170 đã dùng hết trong CASE).

## 3. Trục B — hai phần, phần 1 KHÔNG được bỏ

### B0 — ĐẶC TÍNH hay KHIẾM KHUYẾT? (mô tả, không có treatment, không tiêu trial)

Momentum lệch phải theo bản chất. Trước khi "sửa median" phải biết median âm có phải chuẩn mực của
chính book này không.

Nguồn: sổ lệnh `research/ccs_phase0_Taylor_20260905_135003/trade_ledger_bal_lag_exp.csv`
(2.056 dòng; **lọc `book=BAL`, `is_capit_arm=False`, bỏ `exit_reason=ABANDONED_REFUND`** — đúng
quy ước Phần 1 §6). Đo **theo từng năm 2014-2026**: n, mean, median, hit, skew, share của top-3
lệnh trong tổng lợi nhuận dương, và tỷ lệ đóng góp của đuôi phải.

Câu hỏi trả lời được bằng số: **2025 có bất thường so với chính lịch sử BAL không?** Test:
median-âm xuất hiện ở bao nhiêu năm; 2025 nằm ở phân vị nào của phân phối (skew, top3-share, hit)
so với 12 năm còn lại. Đây là **mô tả**, không gọi p-value quyết định.

**Ràng buộc diễn giải khai trước:** nếu median âm là chuẩn mực (xuất hiện ở đa số năm), thì mọi
luật "nâng median" phải được chấm CẢ ở tác động lên **đuôi phải** — báo cáo bắt buộc có Δ đóng góp
top-3, không chỉ Δmedian.

### B1 — ba luật (N_trials trục B = 3). Chỉ chạy SAU khi B0 xong.

Env `BRULE` (mặc định `off`). Baseline = cổng production hiện tại (KHÔNG nới), tức trục B độc lập
hoàn toàn với trục A.

| chân | luật | hằng số lấy từ đâu |
|---|---|---|
| **B1 — STOP10** | Stop lỗ BAL từ −20% → **−10%**. | Quy ước "halve" của production (`WEAK_SIZE = FULL_SIZE/2`) áp lên chính hằng số stop đang chạy. **0 giá trị tự chế.** |
| **B2 — PARTIAL20** | Giữ nguyên hold 45 phiên **và** stop −20%; **thêm** chốt lời một phần: khi lãi ≥ **+20%** thì bán **50%** vị thế, phần còn lại chạy tiếp theo luật cũ. | `+20%` = đúng độ lớn hằng số stop đang chạy; `50%` = quy ước "halve" của production (`WEAK_SIZE = FULL_SIZE/2`). Engine ĐÃ có `partial_take_at` (`simulate_holistic_nav.py:353`) — không phải cơ chế mới. |
| **B3 — VALENTRY** | Mọi lệnh BAL (kể cả BULL) phải có `pe_z < -0.5`. | Ngưỡng `COMPOUNDER_BUY` (`:133`). Nối thẳng với phát hiện ey lúc vào trôi 0,15 → 0,059. |

**KHÔNG test ở vòng này, khai để không ai tưởng đã thử:** gate `rating_8l ≤ 3` áp lên BAL (hiện chỉ
LIVE cho LAG). Bỏ ra vì trục B đã đủ 3 chân và `pe_z` là trục nối trực tiếp với bằng chứng ey-drift.

**B2 ≠ chân B vòng 2.** Vòng 2 chân B **gỡ** đồng hồ 45 phiên và thay bằng trailing −20% từ đỉnh
(`activate=0.0`) — một luật THAY THẾ cơ chế thoát. B2 ở đây **giữ nguyên** cả hold 45 phiên lẫn
stop −20%, chỉ THÊM một lần bán một phần. Hai luật khác nhau; NO-GO của vòng 2 không phủ lên B2.

**Duy nhất một thay đổi engine, default-None:** `partial_take_tiers` (giới hạn `partial_take_at`
theo tier) — cùng khuôn và cùng lý do với `trailing_tiers` của vòng 2: không có nó thì luật BAL sẽ
âm thầm định hình lại các arm `CAPIT_*` dùng chung sổ. Chân control chạy qua CHÍNH bản copy này ⇒
md5 phải trùng pin.

## 4. Chân control

Chạy TRƯỚC mọi treatment. Phải tái lập pin R3 **BYTE-IDENTICAL**:
CAGR **28,8627%** · Final NAV **1.178,0099B** · MaxDD **−17,785%** · Calmar **1,6229** ·
CSV md5 **`7d053e6201c9d107685ff4d1dd9d2d2a`**.
Lệnh = lệnh pin R3 nguyên văn (`NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap
BASKET_SELECT=yieldcombo PARK_STATES="3:0.7" AUDIT_END=2026-06-19`, `universe_pit`,
`LAG_ADV_BASIS=price`, `BQ_CACHE_THREADS=1`, `$DNA_PYEXE`, snapshot
`data/bq_cache_asof20260729_postrestate`).

⚠️ **Bẫy vòng 2 §6 — bắt buộc xử lý.** `pt_v23_audit_2014.py` tự `sys.path.insert(0, WORKDIR)`,
che mất bản copy nghiên cứu của `simulate_holistic_nav`. Bản copy engine của vòng này phải
**re-insert thư mục nghiên cứu lên đầu `sys.path` NGAY SAU dòng đó**, và chân control phải được
xác minh md5 trùng pin **trước khi tin bất kỳ chân treatment nào**. md5 lệch ⇒ dừng, sửa harness.

## 5. Tiêu chí GO — phải đạt TẤT CẢ. Thiếu 1 = NO-GO. (7 tiêu chí, giữ nguyên vòng 1-2)

| # | Tiêu chí | Ngưỡng |
|---|---|---|
| C1 | ΔCAGR full-period | **> +0,385pp** (sàn nhiễu của chính harness này — tái dùng từ CCS Phase 2, KHÔNG chọn lại) |
| C2 | Calmar không xấu đi | Calmar_treat **≥ 1,6229** |
| C3 | Walk-forward | ΔCAGR **IS(2014-19) và OOS(2020-06/2026) CÙNG DẤU DƯƠNG** |
| C4a | Leave-one-YEAR-out | không năm nào chiếm **> 50%** tổng delta |
| C4b | Leave-one-WINDOW-out trên **10 cửa sổ regime** (`p1_bull_windows.csv`; các cửa sổ phân hoạch toàn timeline) | không cửa sổ nào chiếm **> 50%** tổng delta |
| C5a | DSR, **null = Sharpe của chân control** (KHÔNG phải vs 0) | **> 0,95** |
| C5b | PBO (CSCV, S=16) | **< 0,5** |
| C6 | Block bootstrap (L=21, B=4000) CI95 của ΔCAGR | **loại trừ 0** |
| C7 | Self-check | **0 VND** cả sổ BAL lẫn LAG, **mọi chân**; control md5 trùng pin |

C4a và C4b đều phải đạt. `DSR vs SR0(N)` báo cáo thêm với **N = 7** (tổng số chân treatment của
job này: A1-A4 + B1-B3) — không phải tiêu chí, nhưng để người đọc thấy đúng độ rộng tìm kiếm.

## 6. Đối chứng BẮT BUỘC của trục A — phân rã EXPOSURE vs SELECTION

Vì nới cổng lấy vốn TỪ rổ parking custom30V, một chân có thể "thắng" chỉ vì đổi beta. Đo trên các
phiên **state = 3** từ chính file audit CSV (`bal_stocks_ref`, `bal_etf_ref`, `nav_bal_ref`):

1. `w_stock` = bal_stocks_ref/nav_bal_ref · `w_park` = bal_etf_ref/nav_bal_ref ·
   **`w_equity` = w_stock + w_park** (cả hai đều là cổ phần).
2. Báo cáo Δ`w_equity` (treat − ctrl) trung bình trên phiên NEUTRAL.
3. Quy tắc diễn giải **chốt trước**:
   - |Δ`w_equity`| ≤ **2pp** ⇒ đây là **hoán đổi rổ**; delta (nếu có) quy cho SELECTION.
   - Δ`w_equity` > +2pp và ΔCAGR > 0 ⇒ báo cáo **phải nói thẳng** phần delta đến từ tăng exposure
     ròng, và ước lượng nó bằng Δ`w_equity` × (lợi suất TB của rổ parking trên phiên NEUTRAL).
4. Đồng thời báo Δ lợi suất năm hoá của **riêng sổ BAL** tính trên phiên NEUTRAL, để tách khỏi
   nhiễu allocator/LAG.

## 7. Nguồn dữ liệu — cùng vintage pin, không thêm nguồn ngoài

- Snapshot đóng băng `data/bq_cache_asof20260729_postrestate` (DuckDB chạy chính SQL đã sửa trên
  parquet ⇒ đổi SQL KHÔNG gây lệch vintage).
- State giao dịch: `tav2_bq.vnindex_5state_dt5g_live` (`STATE_TABLE` production).
- Breadth (A4): `research/ccs_phase0_Taylor_20260905_135003/breadth_pit_frozen_exp.csv` — dựng từ
  chính snapshot trên, đã đăng ký ở CCS Phase 0. Không tạo nguồn mới.
- Sổ lệnh (B0): `research/ccs_phase0_.../trade_ledger_bal_lag_exp.csv`.
- **Cấm tuyệt đối làm feature**: `profit_*`, `*_center_*`, `PC1W/PC2W/PC3W/PC1M/PC2M`, `Open_1D`,
  `O1W..O2Y`, `Pattern_*`. Không chân nào đọc bất kỳ cột nào trong danh sách này.
  (`PC_6M` quá khứ thì được, nhưng vòng này không dùng.)
- `LAG_ADV_BASIS=price`, `universe_pit` cho mọi cổng quyết định, `BQ_CACHE_THREADS=1`.

## 8. Điều đã biết trước là sẽ làm kết quả yếu — nói trước, không bào chữa sau

- **N thật của sleeve BAL = 10 cửa sổ regime** trong 12,5 năm (Phần 1 §4). Trục A tăng N (mở thêm
  1.895 phiên NEUTRAL) — đó là lợi thế thống kê THẬT của trục này so với vòng 1-2, và cũng là lý
  do C4b vẫn phải chạy: delta mới có thể vẫn dồn vào 1-2 vùng.
- 2025 = **2 cửa sổ trong 10**. Mọi phát biểu ở trục B về "2025" đều không phải mẫu độc lập; báo
  cáo phải nói rõ giới hạn N này ở đúng chỗ kết luận.
- Delta của mọi luật đổi cổng/thoát đều **rẽ nhánh quỹ đạo danh mục** (mua khác ⇒ vốn khác ⇒ lệnh
  sau khác). Vòng 1 đã thấy chữ ký này (λ=0,5 → 2021 −13,2pp; λ=1,0 → 2021 +12,9pp). C4a/C4b/C6
  tồn tại chính để bắt dạng nhiễu đó.
- Trục A mở thêm cơ hội trong NEUTRAL ⇒ theo cấu trúc sẽ **tăng turnover và phí**. TC 0,1%/chiều
  đã nằm trong engine; không được viện lý do "phí ăn hết edge" sau khi thấy số.
- **NO-GO là NO-GO.** Đã 2 vòng NO-GO liên tiếp. Không nắn số, không đổi ngưỡng sau khi thấy kết
  quả, không thêm chân thứ 5.

## 9. Vật chứng sẽ nộp

`PREREG.md` (file này) · `gate_engine.py` (copy `pt_v23_audit_2014.py` + overlay env-gated) ·
`simulate_holistic_nav.py` (copy + `trailing_tiers`) · `run_leg.sh` · `run_{ctrl,a1..a4,b1..b3}.log` ·
`analyze.py` · `ab_metrics.csv` · `peryear.csv` · `perwindow.csv` · `exposure_decomp.csv` ·
`b0_peryear_dist.py` + `b0_peryear_dist.csv` · `report.md`.
Mọi output NAV mang `AUDIT_EXP_TAG=balgate<leg>` ⇒ không đè đường dẫn canonical (§8
coding_guidelines).
