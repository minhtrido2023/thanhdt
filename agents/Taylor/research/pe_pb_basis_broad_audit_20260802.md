# Rà soát MỞ RỘNG "cơ sở giá" (raw `Price` PIT vs `Close` điều chỉnh hồi tố)

**Job**: `Taylor_20260802_083624` · **Ngày**: 2026-08-02 · **Loại**: RESEARCH / AUDIT — **KHÔNG sửa gì**
**Bối cảnh (saga cùng ngày)**: `kb/incidents/2026-08/2026-08-02-pe-price-close-adjustment-saga.md`
· Phần 1 = PE nhân sai `Price/Close` (gỡ, commit `beec96c`) · Phần 2 = lens `ps` dùng `Close` (sửa, commit `6ea466f`)
**Đăng ký dữ liệu**: `kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` "Bẫy (4)/(5)"
**Bằng chứng thô**: `WorkingClaude/exp_basis_audit/` (q1–q6 SQL + `basket_basis.csv` + `basket_basis_impact.csv`)

---

## 0. Kết luận 1 dòng

**Tầng DỮ LIỆU sạch** — mọi cột định giá lưu sẵn (`PE/PB/PCF/EVEB/DY/PS/PEG`, cả 2 bảng) đều nằm trên
**cơ sở `Price` thô PIT**, xác nhận liên tục **2007→2026** (đóng lỗ hổng "chưa kiểm pre-2014" mà
quant-skeptic nêu). **Tầng CODE thì KHÔNG**: cùng họ lỗi với `ps` còn sống ở **`custom_basket.py`
(PRODUCTION — custom30V)** và ~25 script khác, dưới 2 dạng `Volume_3M_P50*Close` (thanh khoản) và
`Close*OShares` (vốn hoá). Đây là **phát hiện MỚI, chưa sửa** — cần kế hoạch riêng + A/B backtest.

---

## 1. Việc 1 — Bản đồ mọi chỗ dùng cơ sở giá

### 1a. Cột định giá thực sự TỒN TẠI (schema đọc trực tiếp, KHÔNG theo CLAUDE.md)

| Bảng | Cột phụ thuộc giá |
|---|---|
| `tav2_bq.ticker` (174 cột) | `PE`, `PB`, `PCF`, `EVEB`, `DY`, `Dividend_Min3Y`, `PE_MA/SD*`, `PB_MA/SD*`, `EVEB_MA/SD*` |
| `tav2_bq.ticker_financial` (174 cột) | thêm `PS`, `PEG`, `EPS`, `DY_fin`, `Dividend_*_fin`, `PE_MA/SD 1Y/3M` |

⚠️ `ticker` **KHÔNG có** `PS` và **KHÔNG có** `PEG` (CLAUDE.md liệt kê cả hai — stale, đã ghi ở Bẫy (4)).

### 1b. Chỗ dùng trong code

| File | Dòng | Biểu thức | Cơ sở | Đánh giá |
|---|---|---|---|---|
| `rating_8l.py` | 517/529/561 | `1/PCF`, `1/PE`, `1/EVEB` | cột lưu sẵn (=Price) | ✅ đúng |
| `rating_8l.py` | 545-546 | `ps = Price*OShares/Rev_ttm` | `Price` | ✅ đã sửa hôm nay (`6ea466f`) |
| `rating_8l.py` | 556-557 | `div_yield = Dividend_Min3Y/Price` | `Price` | ✅ đúng (xem §2e) |
| `rating_8l.py` | 99 | `drop_pct = Close/HI_3M_T1` | Close/Close | ✅ nhất quán (2 vế cùng chuỗi đ/c) |
| `rating_8l.py` | 98 | `liq_bn = Trading_Value_1M_P50` | cột lưu sẵn (=Price) | ✅ đúng (§2f) |
| `custom_basket.py` | 163, 249 | `AVG(Volume_3M_P50*Close)` chọn top-30 | **`Close`** | ❌ **SAI — MỚI** |
| `custom_basket.py` | 183, 1077, 716 | `mcap = Close*OShares` (trọng số) | **`Close`** | ❌ **SAI (trọng số) — MỚI**; nhưng chuỗi *lợi suất* thì ĐÚNG, xem §3 |
| `custom_basket.py` | 175 | `tv = COALESCE(Price,Close)*Volume` | `Price` | ✅ đúng — **chính file này đã tự mâu thuẫn** |
| `lag_liquidity_filter.py` | 100 | `adv_vnd = Volume_3M_P50*Close` | **`Close`** | ⚠️ production (`golive_recommend_v23.py`) nhưng **live impact = 0** (§3c) |
| `score_live_signals.py` | 157, 411 | `cf_yield = CF_OA_5Y/OShares/Close` | **`Close`** | ⚠️ nhánh lịch sử lệch, live ≈0 |
| `value_radar.py` | 77-78 | `Price*OShares`, `BVPS*OShares` | `Price` | ✅ đúng |
| `dcf_valuation.py` | 529-546 | giá thị trường = `Price` (fallback `Close`) | `Price` | ✅ đúng |
| ~22 script nghiên cứu | — | `Volume_3M_P50*Close` và/hoặc `Close*OShares`, `smoothed_EY = NP_ttm/OShares/Close` | **`Close`** | ⚠️ kết luận IC lịch sử bị nhiễm (§4) |

---

## 2. Việc 2 + 3 — Kiểm định từng cột, MỞ RỘNG ra trước 2014

### Độ phủ dữ liệu thực tế (kiểm trước, không suy đoán)

`PE` dùng được từ **2007** (2008: 37k/53k dòng) · `PB` từ **2007** · `EVEB` từ **2009-2010** ·
`PCF` chỉ đủ dày từ **2013** (2012 mới 38%) · `DY` từ **2006** · `PS`/`PEG` (`ticker_financial`) từ **2007**.
**Trước 2007 không kiểm định được** (PE/PB/PCF/EVEB toàn NULL) — đúng như CLAUDE.md cảnh báo thị trường
mỏng; **không ép kết luận cho 2000-2006**.

### Sức phân giải của phép thử (điều kiện cần, đo trước khi tin kết quả)

Hệ số điều chỉnh `Close/Price` **có đổi bên trong kỳ báo cáo** ở **94,2%** số kỳ (2007-2013) và **80,8%**
(2014-2026) ⇒ phép thử trong-kỳ-hằng-số **phân biệt được** 2 giả thuyết. Trung vị `Close/Price` đi từ
**0,219 (2007) → 1,000 (2026)** — pre-2014 là vùng phân giải MẠNH NHẤT, không phải vùng mù.

### 2a. Phép thử TÁI LẬP (mạnh nhất — không phụ thuộc biến động trong kỳ)

`% dòng` mà `basis/ratio` tái lập đúng mẫu số đã biết (sai số tương đối < 1%):

| Năm | PE→EPS_ttm (Price) | PE (Close) | PB→BVPS (Price) | PB (Close) | `Close/Price` trung vị |
|---|---|---|---|---|---|
| 2007 | **100,0%** | 2,0% | 98,3% | 1,0% | 0,219 |
| 2008 | **100,0%** | 1,1% | 99,7% | 1,4% | 0,234 |
| 2009 | **100,0%** | 1,3% | 99,2% | 2,1% | 0,238 |
| 2010 | **100,0%** | 2,5% | 97,8% | 3,3% | 0,292 |
| 2011 | **100,0%** | 4,3% | 97,8% | 5,9% | 0,346 |
| 2012 | **100,0%** | 5,4% | 99,1% | 9,0% | 0,375 |
| 2013 | **100,0%** | 4,5% | 86,5% | 9,1% | 0,415 |
| 2014-2026 | **100,0% MỌI NĂM** | 6,8→67,4% | 59,4-97,7% | 7,3-70,7% | 0,448→1,000 |

- **PE = `Price`/EPS_ttm đúng 100,0% MỖI NĂM từ 2007 đến 2026** (n ≈ 2,9 triệu dòng). Không có
  ngoại lệ, không có đứt gãy vintage. Cột "Close" chỉ tăng dần vì `Close→Price` khi tới hiện tại.
- **PB = `Price`/BVPS**: cơ sở giá vẫn là Price áp đảo, nhưng tỉ lệ tái lập tụt ở **2015-2017 (59-69%)**
  ở CẢ 2 bảng ⇒ **không phải vấn đề cơ sở giá** mà là **lệch vintage `BVPS`** (BVPS trong bảng thuộc kỳ
  khác kỳ dùng để tính PB). Phép thử trong-kỳ (2b) cho PB 95-97% ⇒ cơ sở giá của PB đã chốt.
  *Ghi nhận riêng, không thuộc phạm vi job này.*

### 2b. Phép thử TRONG-KỲ-HẰNG-SỐ (đúng phương pháp đã dùng cho PE/ps)

% kỳ báo cáo `(ticker × ID_Release, ≥5 phiên)` mà biểu thức hằng số (spread tương đối < 1e-4):

| Cột | Kiểm | 2007-2013 Price | 2007-2013 Close | 2014-2026 Price | 2014-2026 Close | n kỳ |
|---|---|---|---|---|---|---|
| PE | `PE/basis` | **95,7%** | 4,2% | **93,6%** | 16,3% | 8.628 / 41.344 |
| PB | `PB/basis` | **96,7%** | 5,7% | **95,0%** | 19,2% | 10.957 / 47.810 |
| PCF | `PCF/basis` | **84,8%** | 18,2% | **88,8%** | 24,0% | 2.942 / 32.794 |
| DY | `DY*basis` | **51,6%** | 1,8% | **58,1%** | 6,3% | 7.617 / 27.525 |

DY chỉ 52-58% vì **tử số** (cổ tức 12T) đổi giữa kỳ theo ngày chốt quyền, không theo kỳ báo cáo —
**không phải** dấu hiệu sai cơ sở (Close chỉ 2-6%). Xác nhận riêng ở 2d.

### 2c. EVEB — phép thử ĐỘ DỐC (EVEB là hàm AFFINE của giá, tỉ số-hằng-số KHÔNG áp dụng)

`EVEB = (basis×OShares + NetDebt)/EBITDA_P0` ⇒ trong kỳ, `dEVEB/dbasis = OShares/EBITDA_P0` (hằng số đã biết).

| Kỷ nguyên | n kỳ | khớp với `Price` | khớp với `Close` | sai số tương đối trung vị (Price) | (Close) |
|---|---|---|---|---|---|
| 2007-2013 | 3.874 | **95,6%** | 4,8% | **0,00000** | 2,25243 |
| 2014-2026 | 37.841 | **95,4%** | 19,0% | **0,00000** | 0,29944 |

Đối chiếu tay VNM 2012-05: `ΔEVEB/ΔPrice = 3,3508e-4`; `OShares/EBITDA_P0 = 5,56115e8/1,65963e12 = 3,3508e-4`
— **khớp chính xác**. Cơ sở `Close` cho ra EBITDA hàm ý 127 tỷ thay vì 1.660 tỷ (vô lý).

### 2d. DY — nhận dạng công thức đầy đủ

`DY = Dividend_1Y / Price` (là **phân số**, không phải %) — tái lập **100,0% MỖI NĂM 2008→2026**
(`ticker_financial`, n≈38k). Cơ sở `Close`: 0,2-58,9% (chỉ khớp khi Close≈Price). Đối chiếu tay VNM
2012-05-02: `DY × Price = 0,0441989 × 90.500 = 4.000 VND` (số tròn) · `DY × Close = 578,6` (vô nghĩa).

### 2e. PS / PEG (`ticker_financial`) — mở rộng về 2007

| Năm | PS: `Price*OShares/Rev_ttm` | PS: `Close*...` | PEG = PE/(g×100) |
|---|---|---|---|
| 2007 | **100,0%** | 1,8% | **100,0%** |
| 2008-2013 | **100,0%** mọi năm | 1,2→10,0% | **100,0%** mọi năm |
| 2014-2026 | **99,8-100,0%** | 11,5→70,0% | **100,0%** mọi năm |

⇒ Bản sửa `ps` hôm nay (commit `6ea466f`) **đúng trên toàn lịch sử 2007-2026**, không chỉ 2014-2016 như
lần đo ban đầu (n=7.377). `PEG` **kế thừa** cơ sở của `PE` ⇒ tự động đúng, không cần đụng.

`Dividend_Min3Y` (rating_8l `div_yield`): VNM 2012 = 3.000 VND trên `Price` 90.500 (3,3%) — là **VND danh
nghĩa THÔ**, cùng quy ước với `DY`. Ghép với `Price` thô ⇒ **đúng**. *Lưu ý khái niệm (không phải lỗi):
cổ tức danh nghĩa của 3 năm trước ứng với số cổ phiếu CŨ, nên chia cho giá hôm nay là xấp xỉ theo định
nghĩa — giống hệt quy ước `DY` gốc, không phải lỗi cơ sở giá.*

### 2f. `Trading_Value` — chốt cơ sở đúng cho THANH KHOẢN (kết quả then chốt)

`Trading_Value = Volume × Price` khớp **100,0% MỖI NĂM 2010→2026** (`ticker_prune`, n≈850k);
`Volume × Close` chỉ 1,1-69,8%. ⇒ **`Volume` là số cổ phiếu THÔ**, giá trị giao dịch VND đúng phải
nhân `Price`. Đây là bằng chứng phủ định trực tiếp cho biểu thức `Volume_3M_P50*Close` ở §3.

---

## 3. PHÁT HIỆN MỚI (chưa sửa) — cơ sở giá sai ở tầng CODE của `custom_basket.py`

**Cùng họ với lỗi `ps`**: ghép giá ĐÃ điều chỉnh hồi tố (`Close`) với đại lượng PIT thô
(`Volume`, `OShares`). Hệ số `Close/Price` phụ thuộc cổ tức/thưởng **XẢY RA SAU** ngày t và **khác nhau
giữa các mã** ⇒ bóp méo thứ hạng/trọng số cross-sectional lịch sử bằng thông tin tương lai.

### 3a. Chọn thành viên rổ (`select_members` dòng 163, `build_pit` dòng 249)

`AVG(Volume_3M_P50 * Close)` — sai theo §2f. Đo tác động (top-30 theo quý, universe ICB không NULL):

| Kỷ nguyên | số quý | số mã ĐỔI /30 (TB) | tối đa | % quý trùng khớp hoàn toàn |
|---|---|---|---|---|
| 2008-2013 | 24 | **8,46** | 14 | 0,0% |
| 2014-2026 | 51 | **5,04** | 13 | 2,0% |

Theo năm: 2010 đổi 11,3 mã · 2014 đổi 9,5 · 2020 đổi 5,5 · 2025 đổi 1,8 · 2026 đổi 1,0 (hội tụ về 0 khi
`Close→Price`). ⇒ **rổ custom30 lịch sử có tới ~1/3 thành viên khác** so với rổ chọn đúng cơ sở.

### 3b. Trọng số vốn hoá (`mcap = Close*OShares`, dòng 183/1077/716)

`mcap_tính = Price_t × OShares_t × adj_t = mcap_thật × adj_t` — sai số là hệ số nhân **theo từng mã**,
phụ thuộc sự kiện tương lai. Trên đúng 30 mã (chọn theo cơ sở đúng), áp `name_cap=0.10` như production:

| Kỷ nguyên | lệch trọng số TB | lệch tối đa 1 mã | Spearman(w_close, w_price) |
|---|---|---|---|
| 2008-2013 | **1,62 pp** | 8,59 pp | **0,762** |
| 2014-2026 | **0,63 pp** | 8,19 pp | 0,937 |

⚠️ **QUAN TRỌNG — KHÔNG được "sửa" bằng cách thay `Close`→`Price` toàn file.** Chuỗi *lợi suất*
`mcap_t/mcap_{t-1} = Close_t/Close_{t-1}` **BẮT BUỘC** dùng `Close` (nếu không, ngày chốt quyền sẽ bị
đếm thành khoản LỖ giả). Bản sửa đúng là **tách 2 vai**: trọng số/sàng lọc dùng `Price × OShares` và
`Volume × Price`; lợi suất giữ nguyên `Close`. Đây là lý do phải có **kế hoạch riêng + A/B backtest**,
không phải sửa 1 dòng.

### 3c. `lag_liquidity_filter.py:100` (WIRED PRODUCTION qua `golive_recommend_v23.py`)

`adv_vnd = Volume_3M_P50 * Close`, nhưng chỉ đọc **dòng MỚI NHẤT as-of hôm nay**, nơi `Price == Close`
(hệ số điều chỉnh = 1 ở ngày mới nhất) ⇒ **tác động LIVE = 0**, giống hệt ca PE/ps. Chỉ sai nếu replay
gate này as-of một ngày lịch sử. Nên đồng bộ về `Trading_Value_1M_P50` (đã là cơ sở Price) — sửa vệ sinh,
không khẩn cấp.

---

## 4. Ảnh hưởng lan sang kết luận nghiên cứu (ghi nhận, không hành động)

`smoothed_EY = NP_ttm/OShares/Close` và `MktCap = Close*OShares` xuất hiện ở ~12 script `test_fa_*` —
**cùng đúng hình dạng lỗi `ps`**. Trong đó **`test_fa_ic_2007_2013_crisis.py` và
`test_fa_ic_regime_2008_2026.py`** chính là 2 nghiên cứu IC **thời kỳ trước 2014** — nơi hệ số điều
chỉnh lớn nhất (`Close/Price` ~0,22-0,42) nên nhiễu cũng lớn nhất. Mọi kết luận IC dựa trên
`smoothed_EY`/`MktCap` ở các file này nên coi là **chưa tin cậy cho giai đoạn lịch sử** cho tới khi
đo lại. Các script `sim_*`, `test_round*`, `build_v21*`, `pt_lagvn30_audit_2014.py`,
`lag_dnpr_harness.py`, `converge_fullharness_test.py` dùng `Volume_3M_P50*Close` để chọn rổ 30 —
kế thừa đúng vấn đề §3a.

---

## 5. Bảng tổng hợp cuối (Việc 4)

| Đối tượng | Cơ sở ĐANG dùng | Cơ sở ĐÚNG | Sai? | Tác động lịch sử đã đo |
|---|---|---|---|---|
| `PE` (cột) | `Price` | `Price` | **KHÔNG** | — (100,0%/năm 2007-2026) |
| `PB` (cột) | `Price` | `Price` | **KHÔNG** | — (95-97% trong-kỳ); riêng vintage BVPS 2015-17 cần soi |
| `PCF` (cột) | `Price` | `Price` | **KHÔNG** | — (85-89% trong-kỳ; phủ dày chỉ từ 2013) |
| `EVEB` (cột) | `Price` | `Price` | **KHÔNG** | — (95,5% slope-test, sai số 0,00000) |
| `DY` (cột) | `Price` | `Price` | **KHÔNG** | — (`Dividend_1Y/Price` 100,0%/năm) |
| `PS` (`ticker_financial`) | `Price` | `Price` | **KHÔNG** | — (100,0%/năm 2007-2026) |
| `PEG` (`ticker_financial`) | kế thừa `PE` | kế thừa `PE` | **KHÔNG** | — (100,0%/năm) |
| `rating_8l` lens `ey/cfy/eveb/div` | `Price` | `Price` | **KHÔNG** | — |
| `rating_8l` lens `ps` | `Price` (đã sửa) | `Price` | đã đóng | trung vị lệch 47,5-56,7%; 10-15/30 tên đổi |
| `rating_8l` `_pe_adj_factor` | đã gỡ | không nhân | đã đóng | −1,70pp CAGR nếu áp dụng |
| **`custom_basket` chọn rổ** | **`Close`** | **`Price`** | **CÓ — MỚI** | **8,5/30 tên đổi (pre-2014), 5,0/30 (2014+)** |
| **`custom_basket` trọng số mcap** | **`Close`** | **`Price`** (lợi suất giữ `Close`) | **CÓ — MỚI** | **lệch TB 1,62pp / max 8,6pp; Spearman 0,76** |
| `custom_basket` chuỗi lợi suất | `Close` | `Close` | KHÔNG | — (đúng theo thiết kế) |
| `lag_liquidity_filter` adv | `Close` | `Price` | CÓ (vệ sinh) | **live = 0** (as-of hôm nay) |
| `score_live_signals` cf_yield | `Close` | `Price` | CÓ (vệ sinh) | live ≈0, nhánh lịch sử lệch |
| ~22 script nghiên cứu | `Close` | `Price` | CÓ | kết luận IC lịch sử nhiễm (§4) |

---

## 6. Đề xuất (KHÔNG tự làm — chờ Mike/user quyết)

1. **Không sửa gấp.** `custom30V` là cấu phần tin cậy nhất của V2.4 (+7,4pp Full); đổi cơ sở chọn rổ +
   trọng số sẽ **đổi số R3 đã pin**. Phải có kế hoạch riêng: A/B `Close` vs `Price` trên đúng engine
   production, self-check 0 VND, walk-forward IS/OOS, DSR/PBO, quant-skeptic — **rồi mới** quyết wire.
2. Câu hỏi cần trả lời trước khi sửa: đây là **look-ahead thật** (hệ số phụ thuộc tương lai) hay đã
   **vô tình được hưởng lợi**? Nếu A/B cho thấy cơ sở đúng làm R3 XẤU đi, đó là dấu hiệu số pin cũ đang
   ăn look-ahead ⇒ vẫn phải sửa và **hạ kỳ vọng**, không phải giữ vì đẹp số.
3. Việc rẻ, làm được ngay khi có lệnh (live impact 0, không đụng số pin): `lag_liquidity_filter.py` +
   `score_live_signals.py` chuyển sang cơ sở `Price`/`Trading_Value_1M_P50`.
4. Ngoài phạm vi job này nhưng nên mở ticket: **vintage `BVPS` 2015-2017** (PB tái lập chỉ 59-69%).

## 7. Giới hạn đã biết

- **Trước 2007 không kiểm định được** (PE/PB/PCF/EVEB toàn NULL) — không suy rộng kết luận về 2000-2006.
- `PCF` chỉ phủ dày từ 2013; kết luận pre-2014 cho PCF dựa trên n=2.942 kỳ (2013 là chủ yếu).
- §3 mới đo **tác động ở tầng thành phần** (đổi tên rổ, lệch trọng số). **Chưa** chạy backtest đầy đủ ⇒
  **chưa biết** R3 CAGR/Sharpe đổi bao nhiêu. Không suy đoán con số.
- Đây là audit tĩnh + kiểm định dữ liệu, **chưa qua quant-skeptic** (đúng mandate: research thuần,
  không wire, không sửa production).
