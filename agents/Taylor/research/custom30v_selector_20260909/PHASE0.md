# PHẦN 0 — MÔ TẢ ĐỊNH LƯỢNG RỔ custom30V (trước khi sửa bất cứ thứ gì)
job `Taylor_20260909_153631` · 2026-09-09 · **PAPER-ONLY** · AUDIT_EXP_TAG `c30vsel20260909`

Tái lập rổ bằng chính `custom_basket.build_pit` với đúng config production
(`papertrade_daily.sh` [6b]), rồi **tái dựng vòng lặp trọng số hằng ngày** để lấy `W_i(d)` chính
xác. Chuỗi lợi suất tái dựng khớp `build_pit` tới **2,2e-16** (sai số máy) và tổng phân rã đóng góp
khớp `level_cuối − 1` tới **1e-6** ⇒ mọi số dưới đây là phân rã ĐÚNG của chính rổ đang chạy, không
phải mô hình xấp xỉ.

---

## 1. Selector thật sự là gì — đọc từ CODE

| thành phần | giá trị thật | nguồn |
|---|---|---|
| bảng production | `tav2_bq.custom30v_8l` | `papertrade_daily.sh:53-56` |
| selector | **`BASKET_SELECT=yieldcombo`** | `papertrade_daily.sh:53` |
| công thức | `score = rank_pct(1/PE) + rank_pct(1/PCF)`, **rank trong POOL**, thiếu dữ liệu → **0,5** | `custom_basket.py:998-1002` |
| PE/PCF | **trung bình theo QUÝ** của `tav2_bq.ticker.PE`/`.PCF`, lấy ở **quý TRƯỚC** ngày rebal (`src_q`) | `:395-402`, `:1096` |
| pool | 60 tên **thanh khoản nhất** đã qua cổng (`BASKET_CFO_POOL=60`) | `:370` |
| cổng | rating 8L **≤ 3** as-of, thiếu rating = LOẠI; + forensic-exclude 8 tên | `:238-256`, `:305-311` |
| thanh khoản | `AVG(Volume_3M_P50 × giá THÔ)` quý trước — **GATE thôi, không vào điểm số** | `:299-305` |
| số mã | 30 | `N_MEMBERS` |
| trọng số | vốn hoá (giá THÔ × OShares) rồi **water-fill cap 10%/tên** | `:1160-1171` |
| tái cân bằng | **`q2m5`** = phiên đầu tiên từ 05/02, 05/05, 05/08, 05/11 (để BCTC quý vừa xong đã công bố) | `:246-249` |
| thay mã | **KHÔNG có luật riêng** — mỗi rebal chọn lại top-30 từ đầu; không có phí chuyển, không có buffer giữ chỗ | `:1088` |
| mã rớt universe | **KHÔNG có luật riêng** — ngày nào giá NaN thì tên đó bị loại khỏi chuẩn hoá trọng số ngày đó (`valid` mask); rổ tự co lại rồi tự đầy lại | `:1150-1153` |

**Ba điều đáng lưu ý, không suy được từ tên gọi:**
1. **Thanh khoản KHÔNG nằm trong điểm số** của `yieldcombo` — nó chỉ định nghĩa pool. (Rổ `blend`
   cũ mới là `rank(liq) + λ·rank(yield)`.)
2. **Thiếu PE hoặc PCF không bị phạt** — `fillna(0.5)` cho điểm trung vị. Một tên không có PCF vẫn
   cạnh tranh bằng nửa điểm miễn phí ở chân đó.
3. **Trọng số dùng giá THÔ, lợi suất dùng giá ĐÃ ĐIỀU CHỈNH** (tách vai 2026-08-02) — đúng, và là
   lý do pin R3 phải re-pin hồi tháng 8.

⚠️ **ĐÍNH CHÍNH một tài liệu nội bộ:** `research/custom30v_cashflow_quality_selector_20260830.md`
§0 ghi *"`eyonly` (= current production, 'v4final')"* — **SAI**. Production là `yieldcombo`;
`eyonly` là arm A2 của job 07-14 và **kết luận là KHÔNG WIRE**. Đọc nhầm chỗ này sẽ dẫn tới thiết
kế đối chứng sai neo.

---

## 2. Hiệu suất rổ 2014-08 → 2026-06 (gross: không phí, không tiền mặt, 100% cổ phiếu)

**CAGR 34,02% · vol 24,4% · Sharpe(rf=0) 1,33 · MaxDD −40,01% (2022-11-15) · level 32,33×**

Đây là **xe**, không phải hệ. Trong V2.4 nó chỉ nhận 70% book và chỉ chạy ở NEUTRAL, nên MaxDD của
hệ là −17,8% chứ không phải −40%.

| năm | rổ % | VNINDEX % | vượt (pp) |
|---|---|---|---|
| 2014 (từ 08-05) | 10,43 | −10,22 | +20,65 |
| 2015 | 18,98 | 6,12 | +12,86 |
| 2016 | 24,20 | 14,82 | +9,38 |
| 2017 | 74,92 | 48,03 | +26,89 |
| 2018 | 11,42 | −9,32 | +20,74 |
| 2019 | 15,48 | 7,67 | +7,81 |
| 2020 | 76,83 | 14,87 | +61,96 |
| 2021 | 136,51 | 35,73 | +100,78 |
| 2022 | −23,90 | −32,78 | +8,88 |
| 2023 | 35,00 | 12,20 | +22,80 |
| 2024 | 36,05 | 12,11 | +23,94 |
| 2025 | 54,43 | 40,87 | +13,56 |
| 2026 (tới 06-19) | −2,51 | 2,24 | **−4,75** |

**Vượt VNINDEX 12/13 năm.** Năm duy nhất thua là 2026 YTD — cùng cửa sổ mà vòng 1 BAL đã xác định
là vấn đề REGIME, không phải vấn đề chọn mã.

## 3. Theo state DT5G

| state | phiên | % thời gian | rổ (ann.) | VNI (ann.) | vượt | % tổng lãi |
|---|---|---|---|---|---|---|
| 1 CRISIS | 443 | 14,9 | +10,46% | −6,01% | +16,5pp | 5,8 |
| 2 BEAR | 241 | 8,1 | **−6,56%** | −21,44% | +14,9pp | 1,2 |
| **3 NEUTRAL** | **1.799** | **60,7** | **+36,40%** | +13,73% | **+22,7pp** | **57,8** |
| 4 BULL | 422 | 14,2 | +75,35% | +27,21% | +48,1pp | 27,1 |
| 5 EXBULL | 60 | 2,0 | +140,65% | +63,90% | +76,8pp | 8,1 |

Rổ vượt chỉ số ở **cả 5 state**. Trong NEUTRAL — nơi V2.4 thực sự dùng nó — nó ăn +36,4%/năm vs
VNI +13,7%. **Con số này giải thích kết quả vòng 3**: rổ momentum mở trong NEUTRAL phải thắng
36,4%/năm mới hoà, và nó không thắng nổi.

## 4. Đóng góp theo TÊN — 204 tên từng vào rổ

| | |
|---|---|
| tên đóng góp DƯƠNG | **141/204 (69,1%)** |
| top-1 tên (MBB) | 8,4% tổng lãi |
| top-3 | 24,5% |
| top-5 | 39,7% |
| top-10 | 65,9% |
| **top-decile (20 tên)** | **84,3%** |

Top-15: MBB 8,4% · HDB 8,2% · CTG 7,9% · BID 7,6% · TCB 7,6% · ACB 7,3% · LPB 6,7% · SHB 4,5% ·
VIB 4,2% · VCB 3,4% · STB 2,8% · VPB 2,5% · MSB 2,1% · DGC 1,9% · HPG 1,8%.
**13/15 tên đóng góp lớn nhất là NGÂN HÀNG.**
Đáy: VHM −1,5% · VRE −0,7% · GAS −0,35% · PVD −0,34% · VEA −0,23%.

## 5. Tập trung ngành — số đo mới, LỚN HƠN con số 07-14 đang lưu hành

Đo trên **vector trọng số THẬT theo ngày** (không phải đếm tên), route PIT từ `value_panel_2014.csv`:

| | toàn kỳ | IS 2014-19 | OOS 2020+ | đỉnh |
|---|---|---|---|---|
| BANK+INSURANCE+SECURITIES | **52,8%** | 30,7% | **71,4%** | **93,3%** (2026-04-29) |
| riêng BANK | **49,1%** | — | **67,5%** | — |

| route | % trọng số | % tổng lãi | số tên |
|---|---|---|---|
| **BANK** | **49,1** | **76,7** | 18 |
| COMPOUNDER | 22,5 | 8,5 | 112 |
| CYCLICAL | 11,3 | 6,0 | 15 |
| REALESTATE | 8,9 | 2,0 | 38 |
| POWER | 4,5 | 1,2 | 7 |
| SECURITIES | 3,1 | 5,4 | 12 |
| INSURANCE | 0,6 | 0,2 | 2 |

Job 07-14 (`reconcile_finweight.py`) ghi BANK+INS+SEC = 47,4% full / 64,4% OOS. Cửa sổ nay dài hơn
tới 2026-06 ⇒ **52,8% / 71,4%**. Xu hướng đang TĂNG, không phải đứng yên.

**Đây là hiệu ứng SELECTOR, không chỉ là universe trôi.** Trong pool 60 tên, ngân hàng chỉ chiếm
15,5% số tên toàn kỳ (22,0% OOS) — nhưng chiếm 25,3% số tên trong rổ (38,1% OOS), tức **value-rank
khuếch đại tỷ lệ ngân hàng ×1,64 (×1,73 OOS)**. Kỳ 2026-05-05: **13/13** ngân hàng trong pool đều
lọt rổ (43% số tên, 60% nếu tính cả INS+SEC).

## 6. Pool bị RÀNG BUỘC 100% số kỳ — phát hiện cấu trúc mới

Trung bình mỗi kỳ có **192 tên qua cổng rating≤3** (min 104, max 328) trên ~360 tên có thanh khoản,
nhưng chỉ **60 tên thanh khoản nhất** được vào pool. ⇒ **`BASKET_CFO_POOL=60` ràng buộc ở 48/48 kỳ**;
trung bình **132 tên đủ chất lượng không bao giờ được chấm điểm định giá**.

Registry chỉ từng đo pool THU HẸP (60→30, mục liq-tilt, REFUTED). Chiều NỚI RỘNG chưa ai đo.

## 7. Turnover

- **9,7/30 tên mới mỗi quý** (trung vị 9, min 5, max 15) = turnover **32,3%/quý ≈ 129%/năm một chiều**.
- Tuổi thọ một tên trong rổ: trung bình 7,1 kỳ, **trung vị 4 kỳ (1 năm)**, max 39 kỳ.
- Ở TC 0,1%/chiều, 129%/năm ≈ **0,26%/năm** chi phí — không phải nút thắt.

## 8. CÂU HỎI TRUNG TÂM CỦA DISPATCH: rổ có phụ thuộc đuôi phải như BAL không?

**Trả lời: ở cấp vị thế thì PHỤ THUỘC NHIỀU HƠN BAL; ở cấp phụ thuộc thì ÍT HƠN HẲN. Hai câu này
không mâu thuẫn.**

Khung B0 y hệt vòng 3 (1 vị thế = 1 tên × 1 kỳ rebal, vào giá đóng cửa ngày rebal):

| | BAL (268 lệnh) | **custom30V (1.440 vị thế)** |
|---|---|---|
| median | 4,15% | **3,73%** |
| hit | 58,2% | **58,9%** |
| skew | 1,31 | **3,02** |
| top-decile share of gain | 57,2% | **73,5%** |

Median/hit **gần như trùng khít** — chất lượng lệnh trung vị của hai sổ là như nhau. Nhưng rổ
parking **lệch phải mạnh hơn** (skew 3,02 vs 1,31).

**Điều đổi mọi thứ: 1.440 vị thế / 204 tên, không tên nào gánh hệ.**

| bỏ đi | CAGR còn lại | mất |
|---|---|---|
| — | 34,02% | — |
| 1 tên đóng góp lớn nhất | 33,20% | −0,82pp |
| 3 tên lớn nhất | 32,82% | −1,19pp |
| 5 tên lớn nhất | 31,21% | −2,81pp |

So với BAL, nơi **một năm đơn lẻ (2021) hoặc một rổ đơn lẻ lớn hơn cả tổng delta** (C4a/C4b > 1 ở
vòng 3): rổ này bỏ 5 tên đóng góp lớn nhất vẫn còn **31,2% CAGR**. **Lợi nhuận KHÔNG trải đều —
nhưng nó cũng KHÔNG treo trên vài cái tên.** Đó là chất lượng khác thật, và nó đến từ N: 1.440 vị
thế qua 48 kỳ tái cân bằng độc lập vs 268 lệnh qua 10 cửa sổ regime.

**Median vị thế âm ở 5/13 năm** (2015 −0,88 · 2018 −0,58 · 2019 −1,03 · 2022 −4,48 · 2026 −2,78) —
cùng ĐẶC TÍNH lệch phải mà vòng 3 đã kết luận cho BAL, không phải khiếm khuyết riêng của rổ nào.

---

## 9. Ba việc Phần 0 để lại cho Phần 1

1. **Pool ràng buộc 100% kỳ, 132 tên qua cổng bị chặn ngoài** — trục cấu trúc, chưa ai đo chiều nới.
2. **Ngân hàng 49% trọng số / 77% lợi nhuận, và đang tăng** — đã biết từ 07-14 nhưng số thật cao
   hơn; mọi cách CẮT đã đo đều tốn tiền (fincap 0,30/0,45/0,50/0,55 = −0,64/−0,84/−0,74/−0,32pp).
3. **Chân `1/PCF` là chân chết trong điểm số** — bỏ hẳn (`eyonly`) chỉ −0,05pp = no-op đã đo 07-14.
   Một chân không làm gì là chỗ rẻ nhất để thử thay bằng thước đo dòng tiền BỀN.

**Artifacts:** `phase0_describe.py` · `phase0_analyze.py` · `phase0_pool.py` ·
`members.csv` · `daily_contrib.parquet` · `positions.csv` · `contrib_by_name.csv` ·
`daily_fin_weight.csv` · `turnover.csv` · `pool_diag.csv` · `phase0_report_raw.txt`.
