# PHẦN 2 — Kiểm kê indicator + bổ sung chuẩn quốc tế + IC test
job `Taylor_20260909_100425` · 2026-09-09 · **PAPER-ONLY**

## 1. Kiểm kê: indicator kỹ thuật CÓ SẴN trong `tav2_bq`

`bigquery_dictionary.json` có 236 cột; 84 cột thuộc nhóm kỹ thuật/khối lượng/giá.
Đọc `signal_v11_sql.py` (nguồn duy nhất của điểm `ta` cho BAL) để phân loại **đã dùng / chưa dùng**:

### SIGNAL_V11 ĐANG dùng (17 cột)
`D_RSI` · `D_RSI_Max1W` · `D_MACDdiff` · `MA20` · `MA50` · `MA50_T1` · `MA200` · `Close` ·
`Close_T1` · `Price` · `Volume` · `Volume_3M_P50` · `HI_3M_T1` · `ID_HI_3Y` · `PE`/`PE_MA5Y`/`PE_SD5Y` ·
`FSCORE` · `NP_P0/P1/P4` · `ICB_Code` · (cấp chỉ số) `VNINDEX.D_RSI` rolling-max 60 phiên.

### CÓ SẴN nhưng SIGNAL_V11 KHÔNG dùng (đáng chú ý)
`D_CMF` (Chaikin money flow) · `D_CMB`, `D_CMB_XFast`, `D_CMB_Peak_T1` · `C_L1W`, `C_L1M` ·
`VAP1W/1M/3M` + `ID_XVAP1M_Down_P2`, `ID_XVAP3M_Down_P0` · `Res_1Y`, `Sup_1Y` · `MA10`/`MA10_T1` ·
`D_RSI_T1W`, `D_RSI_Min1W/Min3M/MinT3`, `D_RSI_Max3M` · `D_MACD` (mức, khác `D_MACDdiff`) ·
`LO_3M_T1`, `ID_LO_3Y` · `PC_6M`, `Close_2Y_P90` · `Volume_1M`, `Volume_1M_P50`, `Volume_3M_P90`,
`Volume_Max1Y*`, `Volume_Max5Y_High`, `Volume_MaxTop5_2Y_*` · `Trading_Value*` ·
`D_MFI` (chỉ có ở `ticker_1m`) · `Risk_Rating`, `Beta`, `Dev`.

### ⚠️ BẪY MỚI PHÁT HIỆN — cột NHÌN TRỘM TƯƠNG LAI ngoài danh sách `profit_*` đã biết
`bigquery_dictionary.json` định nghĩa rõ, nhưng tên cột **không** gợi ý gì:
- **`PC1W`, `PC2W`, `PC3W`, `PC1M`, `PC2M`** = *"Peak price in the **NEXT** 1W/2W/3W/1M/2M"* —
  **forward-looking**. Dễ nhầm với `PC_6M` (*"Peak Close price in the **LAST** 6M"*, quá khứ, an toàn)
  và với `PC1W..PC2M` trong nhóm "Price change" của `ticker_1m` theo mô tả ở `bigquery_schema.md`.
- **`Open_1D`** = *"Open price in the **NEXT** 1D"* — forward-looking.
- `O1W..O2Y` (outcome stats) và `Pattern_*_3Y` cũng là hậu nghiệm.

⇒ Danh sách cấm-làm-filter-live phải mở rộng từ `profit_*`/`_center_*` sang **`PC1W/PC2W/PC3W/PC1M/PC2M`,
`Open_1D`, `O*`**. Đề xuất ghi vào `kb/data_registry/price-volume/ticker_ohlcv_tables.md` (chưa làm —
đó là file của Winston, §13).
Trong nghiên cứu này chúng chỉ được dùng ở vai trò **forward return để đo IC**, không bao giờ là feature.

## 2. Indicator chuẩn quốc tế đã TÍNH THÊM (từ OHLCV, point-in-time)

Panel: `p2_panel_exp.csv` — **51.650 dòng**, 758 mã, **150 tháng** (2014-01 → 2026-06), lấy mẫu
**phiên cuối mỗi tháng**, universe = `tav2_mike.universe_pit` (`in_universe = TRUE`, CANONICAL),
lọc `adv_vnd ≥ 1e9` để phản chiếu đúng cổng `liq >= 1e9` của SIGNAL_V11. SQL: `p2_panel.sql`.

| Indicator | Công thức | Cơ sở học thuật |
|---|---|---|
| `prox52` | `Close / MAX(High, 252 phiên)` | George & Hwang 2004 JF — 52-week-high |
| `mom12_1` | `Close_{t-21}/Close_{t-252} − 1` | Jegadeesh-Titman 1993, skip-month |
| `mom3m` | `Close/Close_{t-63} − 1` | momentum ngắn |
| `relmom12_1` | `mom12_1 − mom12_1(VNINDEX)` | market-adjusted momentum |
| `residmom_scaled` | `relmom12_1 / (vol60·√252)` | Blitz-Huij-Martens 2011 (**xấp xỉ**: chưa hồi quy beta cuốn chiếu) |
| `trend_atr` | `(Close − MA50) / ATR20` | trend chuẩn hoá biến động |
| `bb_pctb_centered` | `(Close − MA20) / (2·SD20)` | Bollinger %B |
| `eff_ratio60` | `\|Close − Close_{t-63}\| / Σ\|ΔClose\|` (60 phiên) | Kaufman Efficiency Ratio — **thay ADX** (ADX cần làm mượt Wilder, không viết được sạch bằng window function SQL; ER đo cùng thứ: trend "sạch" hay "răng cưa") |
| `fip` | `sign(mom12_1) × (%ngày giảm − %ngày tăng)` trong cửa sổ t-252..t-21 | Da-Gurun-Warachka 2014 — Frog-in-the-Pan / information discreteness |
| `idiovol_ann` | `SD(r1, 60) × √252` | Ang-Hodrick-Xing-Zhang 2006 — low-vol |
| `volratio` | `Volume_1M / Volume_3M_P50` | volume confirmation |
| `cmf` | `D_CMF` (có sẵn, V11 chưa dùng) | Chaikin money flow |

Nhóm đối chứng (V11 đã dùng): `rsi`, `macddiff`, `px_ma50`, `pe_z`, `ey`.

## 3. Kết quả IC (Spearman cắt ngang theo tháng, Fama-MacBeth)

**N khai báo = 150 THÁNG** (không phải 51.650 dòng). t-stat Newey-West (lag 1 cho fwd 1M, lag 3 cho 3M).
Forward return = `profit_1M`/`profit_3M` — **chỉ dùng để đo IC nghiên cứu, không bao giờ làm filter**.

### 3.1 fwd = `profit_1M`, IC trung bình

| Indicator | mới? | FULL | (t) | IS 14-19 | (t) | **OOS 20-26** | **(t)** | 2025 | 2026H1 |
|---|---|---|---|---|---|---|---|---|---|
| `prox52` | ✓ | **+0,0721** | 3,75 | +0,1126 | 4,77 | +0,0347 | 1,21 | +0,0443 | +0,1360 |
| `ey` | | +0,0413 | 3,56 | +0,0051 | 0,33 | **+0,0747** | **4,81** | +0,0492 | +0,0981 |
| `mom3m` | ✓ | +0,0346 | 2,24 | +0,0797 | 3,46 | −0,0071 | −0,39 | −0,0498 | −0,0089 |
| `rsi` | | +0,0306 | 2,30 | +0,0577 | 3,07 | +0,0056 | 0,31 | −0,0244 | +0,0093 |
| `bb_pctb_centered` | ✓ | +0,0302 | 2,44 | +0,0583 | 3,68 | +0,0042 | 0,24 | −0,0245 | +0,0094 |
| `trend_atr` | ✓ | +0,0247 | 1,71 | +0,0540 | 2,49 | −0,0024 | −0,13 | −0,0329 | +0,0251 |
| `mom12_1` | ✓ | +0,0200 | 1,31 | +0,0527 | 2,41 | −0,0102 | −0,51 | −0,0502 | +0,0455 |
| `eff_ratio60` | ✓ | +0,0186 | 1,92 | +0,0260 | 1,67 | +0,0118 | 1,00 | +0,0289 | +0,0144 |
| `residmom_scaled` | ✓ | +0,0146 | 0,96 | +0,0523 | 2,37 | −0,0201 | −1,04 | −0,0607 | −0,0166 |
| `fip` | ✓ | +0,0041 | 0,46 | +0,0139 | 1,00 | −0,0049 | −0,44 | −0,0091 | +0,0094 |
| `pe_z` | | −0,0133 | −1,35 | +0,0063 | 0,36 | **−0,0314** | **−3,47** | −0,0533 | −0,0482 |
| `cmf` | ✓ | −0,0114 | −1,03 | +0,0149 | 1,15 | −0,0357 | −2,13 | −0,0412 | +0,0711 |
| `idiovol_ann` | ✓ | **−0,0593** | −3,23 | −0,0614 | −2,68 | −0,0573 | −2,03 | −0,1039 | **−0,1514** |

`profit_3M` cho cùng thứ tự và cùng dấu (`p2_ic_results.csv`) — không có mâu thuẫn giữa 2 chân trời.

### 3.2 Sau hiệu chỉnh đa kiểm định BH (17 feature/cửa sổ) — **đây mới là bảng để quyết định**

| | FULL p_BH | OOS p_BH |
|---|---|---|
| `prox52` | **0,0030** ✅ | 0,638 ❌ |
| `ey` | **0,0031** ✅ | **<0,0001** ✅ |
| `idiovol_ann` | **0,0069** ✅ | 0,181 ❌ |
| `pe_z` | 0,266 ❌ | **0,0043** ✅ |
| mọi indicator còn lại | ❌ | ❌ |

### 3.3 Ngũ phân vị (kiểm tra đơn điệu — mạnh hơn p-value ở N nhỏ)

`prox52`, fwd 1M, spread Q5−Q1 mỗi tháng: **FULL +1,63pp (t 2,49), ĐƠN ĐIỆU** ·
**IS +3,07pp (t 4,17), ĐƠN ĐIỆU** · **OOS +0,32pp (t 0,32), KHÔNG đơn điệu**.
`idiovol_ann`: không đơn điệu ở FULL/IS/OOS; chỉ đơn điệu ở 2026H1 (n = **6 tháng** — vô nghĩa thống kê).
`ey`: OOS spread +1,09pp (t 1,57), 2026H1 +1,84pp (t 2,26).

## 4. Kết luận Phần 2 — thẳng và không thuận tiện

1. **Không indicator kỹ thuật nào — cũ hay mới — sống sót OOS sau hiệu chỉnh đa kiểm định.**
   Toàn bộ họ momentum/trend (`mom12_1`, `mom3m`, `trend_atr`, `rsi`, `bb_pctb`, `residmom`) mạnh
   ở IS (t 2,4-3,7) và **chết sạch ở OOS** (t −1,0…+0,3). Đây chính là chữ ký "IS-overfit mirage"
   mà `quant-research` §5 cảnh báo.
2. **`prox52` là ứng viên hấp dẫn nhất nhưng KHÔNG qua cổng OOS** (p_BH 0,638, spread OOS +0,32pp
   t=0,32). Đẹp ở FULL/IS + đơn điệu hoàn hảo IS ⇒ **đúng dạng bẫy**. **Không đề xuất wire.**
3. **Chỉ họ ĐỊNH GIÁ sống OOS**: `ey` (IC OOS +0,0747, t 4,81, p_BH<0,0001) và `pe_z` (t −3,47,
   p_BH 0,0043 — rẻ so với dải 5 năm của CHÍNH nó thì tốt hơn). Cả hai **mạnh lên** trong 2025-2026,
   ngược chiều hoàn toàn với họ momentum. `ey` cũng là indicator duy nhất dương ở CẢ hai regime
   (BULL t 2,31 / NEUTRAL t 2,20).
4. **`idiovol_ann`** qua FULL (p_BH 0,0069) nhưng **trượt OOS** (0,181) và không đơn điệu — mức
   "đáng theo dõi", không phải mức "wire". Ghi nhận riêng: 2026H1 IC −0,151 (t −8,52) là số mạnh
   nhất bảng, nhưng n = 6 tháng ⇒ không được trích rời khỏi cảnh báo này.
5. Trả lời trực tiếp câu hỏi *"indicator nào LẼ RA đã cứu 2026?"*: **theo IC thì là `ey` (+0,098)
   và tránh `idiovol` cao (−0,151)**. Nhưng §4.2/4.4 nói rõ hai thứ này **không** đủ tư cách thống kê
   để thành gate — nói cách khác, câu trả lời trung thực là *"không có indicator nào ĐÃ ĐƯỢC CHỨNG MINH
   là cứu được 2026; hai ứng viên tốt nhất đều thuộc trục ĐỊNH GIÁ, không phải trục kỹ thuật."*

**Hệ quả cho Phần 3:** hướng sửa BAL có cơ sở nhất **không phải** thêm indicator kỹ thuật, mà là
(i) nghiêng bộ chọn BAL về **earnings yield**, (ii) sửa **cơ chế regime/exit** đã xác định ở Phần 1.
