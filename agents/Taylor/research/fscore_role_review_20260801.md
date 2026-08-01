# Vai trò của FSCORE trong hệ thống rating — CAPIT entry-gate (A) & trục 8L (B)

Job `Taylor_20260801_082823` (dispatch từ Mike; câu hỏi mở của user sau finding CAPIT quality-exit
`Taylor_20260801_073610`).

**R&D THUẦN — KHÔNG sửa production.** `rating_8l.py` và `capit_basket()` trong
`pt_v23_audit_2014.py` KHÔNG bị đụng vào (xác nhận bằng `diff`, §6 dưới). Hai leg engine A/B chạy
trên **bản sao sinh tự động bằng `sed`, khác đúng 1 dòng**, để trong thư mục thí nghiệm.

---

## 0. Câu trả lời ngắn

**CÂU A — GIỮ NGUYÊN nhánh FSCORE trong `capit_basket()`. Không bỏ, không nới, không route qua 8L.**
Cả 4 phương án user/Mike nêu đều làm rổ CAPIT TỆ ĐI, theo một **dose-response sạch**: càng nới nhánh
FSCORE, sleeve càng kém. Engine A/B ở tầng danh mục xác nhận: bỏ hẳn FSCORE = **CAGR 27,60% → 26,85%,
Sharpe 1,84 → 1,79, MaxDD xấu đi −17,5% → −18,3%** — thua trên MỌI trục, không mua được gì.

**CÂU B — điểm yếu "FSCORE chỉ hợp công ty tài sản cố định lớn" ĐO ĐƯỢC nhưng NHỎ và KHÔNG có ý
nghĩa thống kê; nhóm tài sản NHẸ vẫn dương rõ.** Chênh IC heavy−light = **+0,016 (t=+1,52)** theo
`FAsset_Eq_P0` và **+0,005 (t=+0,39)** theo `FAssetTurn_P0`. Nhóm tài sản nhẹ tự nó vẫn IC **+0,034
(t=+4,70, hit 80%)**, vững cả IS lẫn OOS. **Không hạ trọng số, không bỏ trục cho sub-route tài sản
nhẹ** — sẽ là tinh chỉnh theo nhiễu.

**Ca DGC (capex lớn → tiền mặt giảm) — giả thuyết "cùng gốc lỗi" BỊ BÁC, ngược chiều dự đoán.**
FSCORE **không** bị hạ một cách cơ học ở quý capex nặng, và sức dự báo của nó **MẠNH NHẤT** chính ở
nhóm capex nặng.

> ⚠️ Một sửa nhỏ đối với brief của Mike (§1): **không có route `RETAIL`**, và **`POWER` KHÔNG dùng
> trục FSCORE**. Chỉ **COMPOUNDER + CYCLICAL** thực sự ăn 2/12 điểm FSCORE.

---

## 1. Xác nhận lại 2 phát hiện của Mike — tự đọc code, không tin lời

| Mike nói | Tôi đọc được | Kết luận |
|---|---|---|
| `core_score()`: FSCORE là 1/6 trục, tối đa 2/12, bậc thang fs≥8→2đ, fs≥6→1đ | `rating_8l.py:226` — `s += (2 if fs>=8 else 1 if fs>=6 else 0) if pd.notna(fs) else 0`, trong hàm 6 trục max 12 | ✅ **ĐÚNG NGUYÊN VĂN** |
| `rate_securities()`/`rate_insurance()` loại hẳn FSCORE; `rate_realestate()` chỉ 1/9 điểm | `rating_8l.py:297-311` (securities: chỉ ROE), `:312-326` (insurance: chỉ ROE), `:328-347` (RE: `s += (1 if fs>=6 else 0)` trên thang 9) | ✅ **ĐÚNG** |
| Route generic dùng đủ 2/12 = COMPOUNDER/CYCLICAL/**POWER**/**RETAIL** | `route_of()` (`:488-497`) chỉ sinh 7 route: BANK, INSURANCE, SECURITIES, POWER, CYCLICAL, REALESTATE, COMPOUNDER — **không có RETAIL**. `rate_row()` (`:356-364`) gọi `rate_power()` cho POWER, mà `rate_power()` (`:432-440`) đọc verdict từ `data/power_lens.csv` và **không đụng `core_score`/FSCORE** | ⚠️ **SỬA**: chỉ **COMPOUNDER + CYCLICAL** |
| Sàn CAPIT là 1 cổng AND nhị phân, KHÔNG qua routing sector-aware | `pt_v23_audit_2014.py:1171` — `WHERE p.time = DATE '…' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6` nằm thẳng trong SQL của `capit_basket()`, không có nhánh ngành nào | ✅ **ĐÚNG NGUYÊN VĂN** |

Chi tiết cơ học đáng ghi: `rate_row()` **vẫn tính** `core_score()` cho mọi route (`:352`), nhưng với
BANK/POWER/SECURITIES/INSURANCE/REALESTATE giá trị đó bị **ghi đè** bởi lens riêng và chỉ còn tồn tại
như cột chẩn đoán `core_score` trong output. Nên "FSCORE có mặt trong core_score cho mọi mã" là đúng
về mặt tính toán nhưng **sai về mặt ảnh hưởng tới rating** ở 5/7 route.

---

## 2. Nguồn dữ liệu (tra `mike/kb/data_registry/` trước — §9)

| Thứ | Nguồn | Status | Ghi chú |
|---|---|---|---|
| FSCORE, ROE_Min5Y, ROIC5Y | `tav2_bq.ticker_prune` | CANONICAL (`fundamentals/roe_roic_fscore_quality.md`) | Registry ghi rõ **KHÔNG hồi tố** (0-diff pre/post change) ⇒ lịch sử FSCORE không bị viết lại, so sánh theo thời gian hợp lệ. Đúng bảng production `capit_basket()` đang đọc (CAPIT pool cố ý còn ghim `ticker_prune`). |
| Cường độ tài sản cố định | `tav2_bq.ticker_financial` (`FAsset_Eq_P0`, `FAssetTurn_P0`, `CF_Invest_P0`, `FSCORE_P1`) | CANONICAL (`fundamentals/ticker_financial.md`) | Join **PIT theo `Release_Date`**, không theo `time` (fiscal) — tránh nhìn trước. Phủ ~88%. |
| Panel value + forward return | `data/value_panel_2014.csv` | Panel PIT đông cứng, chính là input của `ic_panel_8l.py` đã pin trong registry | `profit_2M` = T+40 forward, dùng **nghiên cứu**, không phải filter live (§ no-look-ahead). |
| 8L rating as-of | `tav2_bq.fa_ratings_8l` | CANONICAL | Bảng đúng mà `custom_basket.rating_asof()` bisect. |
| Regime | qua engine → `vnindex_5state_dt5g_live` | CANONICAL | KHÔNG đọc `vnindex_5state` (bẫy base). |

**Snapshot pin CÂU A: `data/bq_cache_asof20260729_postrestate`** — đúng snapshot của lần re-pin R3
07-29, nên leg ctrl tái lập chính xác số pin. **CÂU B dùng panel vintage 2026-06-19** (panel đông
cứng). Hai câu **khác vintage** — không so số chéo giữa A và B, chỉ so trong nội bộ từng câu.

---

## 3. CÂU A — sàn FSCORE ở cổng VÀO của CAPIT

### 3a. Thiết kế

Tái tạo **nguyên văn** phần chọn rổ của `capit_basket()` (thang pb_z `g=pbz<-1` → `c=pbz<0` →
`nsmallest(15)`), chỉ thay tầng sàn chất lượng. Sàn ROE_Min5Y≥0,12 ∧ ROIC5Y≥0,10 ∧ thanh khoản ≥2
tỷ/ngày **giữ nguyên ở mọi biến thể** — chỉ nhánh FSCORE thay đổi. Đo lợi suất **đều-trọng-số** 60
phiên (đúng cơ chế engine: `tw2[pt] = wt/len(names)`, `pt_v23_audit_2014.py:1372`), vào lệnh Open
T+1 sau ngày sự kiện.

**N thật: 14 sự kiện CAPIT có vị thế (2014-05-09 → 2026-03-10), 61 lượt-mã của rổ production, 390
ô (sự kiện × mã) trong pool đủ điều kiện.** Mẫu nhỏ — không nguỵ trang.

### 3b. Kết quả — mọi cách nới đều thua, theo liều lượng

| Biến thể | Ý tưởng | rổ TB | ret TB/sự kiện | Δ vs prod | LOO 14 lần |
|---|---|---|---|---|---|
| **V0_prod** `FSCORE>=6` | hiện trạng | 4,4 | **+18,22%** | — | — |
| V1_nofscore | **bỏ hẳn** nhánh FSCORE | 9,1 | +11,27% | **−6,94pp** | **14/14 cùng dấu** |
| V4_r8l | thay bằng cổng 8L rating≤3 | 8,1 | +11,47% | −6,11pp | **14/14 cùng dấu** |
| V5_2q | **đề xuất của user**: chỉ loại khi yếu **2 quý liên tiếp** (`FSCORE>=6 OR FSCORE_P1>=6`) | 5,7 | +15,16% | **−3,06pp** | **14/14 cùng dấu** |
| V2_fs5 | hạ ngưỡng xuống 5 | 5,2 | +16,93% | −1,29pp | đổi dấu |
| V3_sectoraware | bỏ nhánh FSCORE cho đúng các route 8L bỏ nó (BANK/INS/SEC) | 4,5 | +18,95% | +0,73pp | đổi dấu |

Artifact: `data/fscore_review_20260801/basket_composition.csv`, `entry_gate_returns.csv`.

**Đọc bảng — điểm mạnh nhất của bằng chứng nằm ở TÍNH ĐƠN ĐIỆU, không ở 1 con số:** xếp các biến thể
theo "nới bao nhiêu" (V3 ≈ 0 mã → V2 → V5 → V4 → V1 nới nhiều nhất), thiệt hại tăng đơn điệu
+0,73 → −1,29 → −3,06 → −6,11 → −6,94pp. Một tham số bị nhiễu sẽ không tạo ra thang liều lượng như
vậy. Ba biến thể nới mạnh nhất đều **giữ nguyên dấu qua cả 14 lần leave-one-event-out**.

**Đề xuất riêng của user (V5, xác nhận 2 quý) — đã test đúng như phát biểu và VẪN THUA (−3,06pp,
14/14 LOO).** Nó nhận thêm 30 mã và bỏ 11 mã so với production; phần thêm vào kéo rổ xuống. Nghĩa là
"tụt 1 điểm FSCORE 1 quý" ở cổng VÀO **không phải nhiễu vô hại** như ở cổng RA.

**V3 (sector-aware) chỉ động vào đúng 2 mã trên 1/14 sự kiện** (E8, 2023-10-31) — về bản chất là
no-op, và +0,73pp là ngẫu nhiên của 1 sự kiện (LOO đổi dấu, dải [+0,00; +0,79]). Lý do cơ học: rổ
CAPIT đã bị lọc bởi `ROE_Min5Y>=0.12 ∧ ROIC5Y>=0.10` nên gần như không còn ngân hàng/chứng khoán/bảo
hiểm nào để routing tạo khác biệt. **Routing sector-aware ở đây giải một vấn đề không tồn tại.**

### 3c. Nó thật sự sàng lọc, hay chỉ làm rổ nhỏ đi?

Câu hỏi phản biện đúng: rổ V0 nhỏ hơn (4,4 vs 9,1 mã) nên trung bình có thể đẹp hơn chỉ vì ít pha
loãng. Test đúng là **ở tầng MÃ**, không phải trung bình-của-trung-bình:

| | n | ret TB 60 phiên | trung vị | win |
|---|---|---|---|---|
| Mã **GIỮ** bởi cả 2 (FSCORE≥6) | 29 | **+17,25%** | +11,06% | 82,8% |
| Mã **THÊM VÀO** khi bỏ FSCORE (= mã FSCORE loại) | 94 | **+11,14%** | +10,39% | 77,7% |

**Chênh +6,11pp, bootstrap CI90 [−1,07; +13,74]pp, P(chênh≤0)=0,081.** → cùng chiều nhưng **KHÔNG
đạt ý nghĩa thống kê ở tầng mã**. Tôi nói thẳng: bằng chứng quyết định nằm ở **engine A/B (§3d)** và
ở **tính đơn điệu**, không ở test này.

Bổ sung — IC của FSCORE **bên trong chính pool CAPIT** (390 ô, 14 sự kiện): **Spearman +0,179,
hit 71%, t=+2,77**. Trong bối cảnh mua-đáy-hoảng-loạn, FSCORE có sức dự báo thật.
Thang FSCORE→ret 60 phiên trong pool: `≤3` +7,24% · `4` +9,90% · `5` +15,20% · `6` +11,67% ·
`7` +13,90% · `8-9` +17,86% — **không đơn điệu hoàn hảo** (bậc 5 vượt bậc 6), đúng như V2_fs5 gợi ý
rằng con số 6 cụ thể không phải điểm tối ưu. Nhưng V2_fs5 vẫn âm và LOO đổi dấu ⇒ **không có cơ sở
để đổi ngưỡng**, chỉ có cơ sở để nói ngưỡng 6 không thiêng.

### 3d. Engine A/B tầng danh mục — bằng chứng quyết định

Config pin: `NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap BASKET_SELECT=yieldcombo
PARK_STATES=3:0.7 AUDIT_END=2026-06-19`, snapshot `bq_cache_asof20260729_postrestate`,
`BQ_CACHE_THREADS=1`, `$DNA_PYEXE`.

| Leg | CAGR | Sharpe | MaxDD | Calmar | self-check |
|---|---|---|---|---|---|
| **ctrl = production** (tái lập đúng pin R3) | **27,60%** | **1,84** | **−17,5%** | **1,58** | 0 VND ✅ |
| V1_nofscore (bỏ hẳn FSCORE) | 26,85% | 1,79 | **−18,3%** | 1,47 | 0 VND ✅ |
| V3_sectoraware | 27,19% | 1,82 | −17,5% | 1,56 | 0 VND ✅ |

**Bỏ FSCORE thua trên MỌI trục** — mất 0,75pp CAGR, mất 0,05 Sharpe, và **MaxDD XẤU ĐI** 0,8pp. Đây
là điểm then chốt: nếu FSCORE chỉ là nhiễu làm rổ nhỏ đi, bỏ nó phải **cải thiện** rủi ro (rổ rộng
hơn = phân tán hơn). Thực tế ngược lại ⇒ nó đang loại đúng nhóm mã dễ sập.

**V3_sectoraware: +0,73pp ở tầng rổ nhưng −0,41pp ở tầng danh mục.** Ghi lại như một cảnh báo phương
pháp — lợi suất rổ đều-trọng-số KHÔNG tự động chuyển thành kết quả danh mục (2 mã thêm vào ở E8 làm
đổi sizing/tiền mặt xuống các sổ). Cả hai con số đều trong vùng nhiễu; kết luận là **không đổi gì**.

---

## 4. CÂU B — trục FSCORE trong `core_score()` chung của 8L

### 4a. Thiết kế + kiểm chứng harness

Đúng phương pháp đã dùng cho "1/PE dominant IC +0,125, 94% hit" (`ic_panel_8l.py`, pin ở
`data/results_registry.md` §IC PANEL 8L): 1 obs/(mã,quý)=last → Spearman IC cắt ngang từng quý →
trung bình qua quý, `t = mean/(sd/√Nq)`, `hit` = % quý IC>0. Target `profit_2M` (T+40).

Đo **đúng trục như đã cài** (`fs_pts = 2 nếu FSCORE≥8, 1 nếu ≥6, 0 nếu <6`), không phải điểm thô —
và báo cả điểm thô để tham chiếu. Scope **COMPOUNDER + CYCLICAL** (2 route duy nhất thực sự dùng
trục này, §1). Chia nhóm bằng **trung vị cắt ngang TỪNG QUÝ** của biến cường độ tài sản, join PIT
theo `Release_Date`.

**Kiểm chứng harness:** trên đúng scope này, `ey` (1/PE) cho **IC +0,125, t=10,94, hit 94%** — trùng
khít số pin trong registry (**+0,125, t=11,0, hit 94%**). Harness tái lập được benchmark đã biết.

**N thật: 36.816 obs (mã × quý), 49 quý, 2014Q1–2026Q2.** Mẫu lớn.

### 4b. Kết quả

| Nhóm | Trục | Nq | Nobs | IC | t | hit |
|---|---|---|---|---|---|---|
| TẤT CẢ (COMP+CYC) | `fs_pts` thô | 49 | 36.816 | +0,043 | +7,22 | 80% |
| TẤT CẢ | `fs_pts` **marginal** (đã trừ khối value ey/cfy/ps/pb_z) | 49 | 36.816 | **+0,037** | **+6,72** | 78% |
| TẤT CẢ | FSCORE thô | 49 | 36.816 | +0,050 | +7,50 | 84% |
| TẤT CẢ | *(tham chiếu)* `ey` = 1/PE | 49 | 31.249 | +0,125 | +10,94 | 94% |
| **HEAVY** theo `FAsset_Eq_P0` | `fs_pts` thô | 49 | 18.426 | **+0,050** | +5,97 | 80% |
| **LIGHT** theo `FAsset_Eq_P0` | `fs_pts` thô | 49 | 18.208 | **+0,034** | **+4,70** | 80% |
| HEAVY theo `FAssetTurn_P0` | `fs_pts` thô | 49 | 17.632 | +0,047 | +5,74 | 80% |
| LIGHT theo `FAssetTurn_P0` | `fs_pts` thô | 49 | 18.671 | +0,043 | +4,80 | 71% |

Bảng đầy đủ (kèm IS 2014-19 / OOS 2020+ cho từng dòng): `data/fscore_review_20260801/fscore_axis_ic.csv`.

**Test heavy−light, ghép cặp theo quý (cùng thị trường, cùng kỳ — so sánh sạch):**

| Biến phân nhóm | Trục | heavy | light | chênh | t | % quý heavy thắng |
|---|---|---|---|---|---|---|
| `FAsset_Eq_P0` | `fs_pts` thô | +0,050 | +0,034 | **+0,016** | **+1,52** | 59% |
| `FAsset_Eq_P0` | `fs_pts` marginal | +0,042 | +0,028 | +0,015 | +1,37 | 55% |
| `FAssetTurn_P0` | `fs_pts` thô | +0,047 | +0,043 | **+0,005** | **+0,39** | 49% |
| `FAssetTurn_P0` | `fs_pts` marginal | +0,038 | +0,033 | +0,005 | +0,44 | 55% |

**Kết luận CÂU B:**
1. **Trực giác của user ĐÚNG VỀ CHIỀU nhưng nhỏ và không có ý nghĩa thống kê.** FSCORE quả thật hơi
   mạnh hơn ở nhóm tài sản nặng, nhưng t=+1,52 (và chỉ thắng 59% số quý). Theo `FAssetTurn_P0` —
   thước đo cường độ tài sản trực tiếp hơn — chênh lệch **biến mất hoàn toàn** (+0,005, t=+0,39,
   49% số quý). Hai thước đo không đồng thuận về độ lớn ⇒ đây là **ấn tượng có thật nhưng mờ**, không
   phải hiệu ứng chắc.
2. **Nhóm tài sản NHẸ không hề mất sức dự báo.** IC +0,034 (t=+4,70, hit 80%), marginal +0,028
   (t=+4,18), **vững cả IS (+0,030) lẫn OOS (+0,038)**. Đây mới là điều quyết định: tiền đề "mất sức
   dự báo ở nhóm tài sản nhẹ" **không đúng**.
3. Cơ học trục còn cho thấy điều ngược với dự đoán: bậc cao nhất `fs_pts=2` ở nhóm **LIGHT** có
   forward return **cao hơn** nhóm HEAVY (+5,41% vs +3,93%), dù chỉ chiếm 5,3% số mã (vs 11,8%).

**Khuyến nghị: GIỮ NGUYÊN, không hạ trọng số và không bỏ trục FSCORE cho sub-route tài sản nhẹ.**
Ảnh hưởng không đáng kể, và tạo thêm 1 sub-route = thêm bậc tự do để overfit trên một hiệu ứng t=1,5.

---

## 5. Ca DGC — "capex hợp lý bị hiểu nhầm thành suy giảm chất lượng"

Lo ngại có cơ sở lý thuyết: 9 tín hiệu Piotroski là **thay đổi YoY**, nên một năm đầu tư lớn về
nguyên tắc làm xấu vài tín hiệu (CFO/tài sản, thanh toán hiện hành, vòng quay tài sản, đòn bẩy nếu
vay). Chia 3 nhóm theo phân vị cắt ngang từng quý của `CF_Invest_P0` (âm nhất = capex nặng nhất),
36.407 obs / 50 quý:

**Q1 — FSCORE có bị hạ cơ học ở quý capex nặng không? → KHÔNG.**

| Nhóm | n | FSCORE TB | tỷ lệ FSCORE<6 | fwd `profit_2M` TB |
|---|---|---|---|---|
| HEAVY capex | 12.118 | **4,89** | **61,0%** | +2,44% |
| mid | 11.793 | 4,85 | 62,3% | +1,94% |
| LIGHT capex | 12.496 | 4,66 | **65,9%** | +3,13% |

Nhóm capex nặng bị gắn cờ FSCORE<6 **ÍT hơn** nhóm capex nhẹ (61,0% vs 65,9%). **Thiên lệch cơ học
được giả định là KHÔNG tồn tại trong dữ liệu này.**

**Q2 — bên trong nhóm capex nặng, FSCORE còn dự báo không? → CÒN, và MẠNH NHẤT.**

| Nhóm | IC(`fs_pts`) | t | hit | IC(FSCORE thô) | t |
|---|---|---|---|---|---|
| **HEAVY capex** | **+0,056** | +5,24 | 76% | **+0,074** | +6,86 |
| mid | +0,044 | +4,57 | 69% | +0,047 | +4,46 |
| LIGHT capex | +0,032 | +3,72 | 71% | +0,036 | +3,92 |

**Q3 — đúng hình dạng DGC (capex nặng + CFO mạnh, tam phân vị trên):** n=6.216. Nhóm này bị gắn cờ
FSCORE<6 chỉ **47,0%** (vs 76,7% của phần còn lại trong capex nặng) — tức **dòng tiền hoạt động mạnh
đã tự bảo vệ điểm số**, đúng như thiết kế của Piotroski. Và khi nó *vẫn* bị gắn cờ, cờ đó **có
thông tin**: trong chính nhóm DGC-shape, FSCORE<6 → +1,93% vs FSCORE≥6 → +3,57%, **chênh +1,63pp,
bootstrap CI90 [+0,81; +2,47]pp, P(chênh≤0)=0,000**.

> **Kết luận: KHÔNG tìm được bằng chứng cho giả thuyết "cùng gốc lỗi" giữa DGC và NCT/SAB.** Bằng
> chứng đi ngược lại ở cả 3 lát cắt. Điều này KHÔNG bác bỏ luận điểm đầu tư về DGC (đó là ca đơn lẻ,
> n=1, và đang được theo dõi riêng ngoài rổ) — nó chỉ bác bỏ việc **khái quát hoá** ca đó thành lỗi
> hệ thống của FSCORE.

**Điểm mấu chốt hoà giải cả hai câu:** trong sự cố quality-EXIT 07-31, FSCORE tụt 1 điểm trong 60
phiên nắm giữ đúng là nhiễu (`floornf` = 0/85, mọi luật thoát đều lỗ). Ở đây, cùng chỉ số đó ở **cổng
VÀO** lại có giá trị thật. Không mâu thuẫn: cổng VÀO là **so sánh cắt ngang** giữa các mã tại một
thời điểm (FSCORE mã A vs mã B — có tín hiệu); cổng RA là **so sánh chuỗi thời gian** trong một mã
(FSCORE mã A hôm nay vs 3 tháng trước — là nhiễu, và bắn đúng lúc tin xấu đã ra). **Một chỉ số có
thể là tín hiệu cắt ngang và là nhiễu chuỗi thời gian cùng lúc** — đó chính là điều dữ liệu nói.

---

## 6. Giới hạn — nói thẳng

1. **CÂU A mẫu nhỏ**: 14 sự kiện, 61 lượt-mã production. Test tầng mã KHÔNG đạt ý nghĩa
   (P=0,081). Sức nặng đến từ (a) dose-response đơn điệu qua 5 biến thể, (b) LOO 14/14 cùng dấu ở
   3 biến thể nới mạnh, (c) engine A/B thua mọi trục **kể cả MaxDD**. Đây là 3 mảnh bằng chứng độc
   lập cùng chiều, không phải 1 con số.
2. **Không chạy DSR/PBO/walk-forward IS-OOS cho CÂU A** — có chủ ý: khuyến nghị là **KHÔNG ĐỔI GÌ**,
   nên không có config nào được "chọn" để cần khử thiên lệch multiple-testing. Nếu sau này có ai muốn
   wire một biến thể, **phải chạy đủ** DSR/PBO/IS-OOS trước.
3. **A và B khác vintage dữ liệu** (A: snapshot 07-29 post-restate; B: panel đông cứng 06-19).
   Không so số chéo giữa hai câu.
4. **`FAsset_Eq_P0` có mẫu số vốn chủ, dễ méo khi vốn chủ ≈ 0** (registry đã ghi outlier ROE/ROIC
   cực đoan cùng gốc). Đã giảm thiểu bằng chia nhóm theo **thứ hạng cắt ngang**, và đã kiểm chứng
   chéo bằng `FAssetTurn_P0` — hai thước đo cho cùng kết luận định tính (không suy giảm ở nhóm nhẹ)
   dù khác nhau về độ lớn của chênh lệch.
5. **Trong 1 sự kiện, các mã tương quan mạnh** (cùng cú sốc thị trường) ⇒ N hiệu dụng của CÂU A thấp
   hơn 390 nhiều. Vì vậy mọi kiểm định của CÂU A đều lấy **sự kiện** làm đơn vị (LOO theo sự kiện),
   không lấy mã.
6. **Không đụng production, đã verify bằng `diff`:** `rating_8l.py` và `pt_v23_audit_2014.py` sạch;
   2 bản sao engine khác đúng 1 dòng (`:1171`) và nằm trong `data/fscore_review_20260801/`.

---

## 7. Khuyến nghị

| # | Khuyến nghị | Trạng thái |
|---|---|---|
| 1 | **CÂU A: giữ nguyên `FSCORE>=6` trong `capit_basket()`.** Không bỏ, không hạ ngưỡng, không xác nhận-2-quý, không route qua 8L. | KHÔNG ĐỔI GÌ |
| 2 | **CÂU B: giữ nguyên trục FSCORE 2/12 trong `core_score()`.** Không tạo sub-route tài sản nhẹ. | KHÔNG ĐỔI GÌ |
| 3 | **Không khái quát ca DGC thành lỗi hệ thống của FSCORE** — bằng chứng đi ngược ở cả 3 lát cắt. Luận điểm riêng về DGC vẫn theo dõi độc lập. | Ghi nhận |
| 4 | Sửa brief nội bộ: **không có route RETAIL**; **POWER không dùng trục FSCORE**. Chỉ COMPOUNDER+CYCLICAL. | Sửa tài liệu |
| 5 | **Lead còn mở (KHÔNG phải khuyến nghị)**: registry §IC PANEL 8L mục 6 ghi "FSCORE thêm marginal trong gate +0,031 — ứng viên enhancer selection, **chưa test trong custom30V**". Đo của tôi ủng hộ (+0,037 marginal trên COMP+CYC). Vẫn **chưa test**. | Chưa làm |

**quant-skeptic:** kết luận là **không đổi gì**, nên không có thay đổi production nào cần cổng duyệt.
Đề nghị verify **nếu** sau này có ai muốn hành động theo lead #5, hoặc muốn đảo ngược #1/#2 — khi đó
phần cần soi kỹ nhất là **engine A/B §3d** (tái lập được ctrl = pin R3 hay không) và **tính PIT của
join `Release_Date`** ở §4/§5.

---

## 8. Artifact

Thư mục: `data/fscore_review_20260801/`

| File | Nội dung |
|---|---|
| `entry_gate.py` | CÂU A — 6 biến thể sàn vào, tái tạo nguyên văn selection của `capit_basket()` |
| `decompose.py` | CÂU A — test tầng mã KEPT-vs-ADDED + IC FSCORE trong pool CAPIT |
| `fscore_axis_ic.py` | CÂU B — IC trục FSCORE chia theo cường độ tài sản (+ kiểm chứng harness bằng `ey`) |
| `capex_falsealarm.py` | Ca DGC — 3 lát cắt capex |
| `basket_composition.csv`, `entry_gate_returns.csv`, `eligible_pool.csv`, `fscore_axis_ic.csv`, `capex_falsealarm.csv` | Số liệu thô |
| `engine_V1_nofscore.py`, `engine_V3_sectoraware.py` | Bản sao engine sinh bằng `sed`, khác production đúng 1 dòng (`:1171`) |
| `run_leg.sh`, `entrygate_v1nofscore.log`, `entrygate_v3sector.log` | Runner + log engine A/B (self-check 0 VND) |
