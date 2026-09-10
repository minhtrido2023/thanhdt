# Thước đo mức độ hiệu quả của TTCK Việt Nam theo thời gian (AMH #2 / gap G4)

> Taylor · job `Taylor_20260910_131910` · 2026-09-10 · **PAPER-ONLY, KHÔNG WIRE**
> Đọc được độc lập — không cần mở file khác.
> Artifact: `mike/agents/Taylor/research/vn_market_efficiency_20260910/`

---

## 0. TL;DR — câu trả lời cho câu hỏi được giao

**"Edge momentum trên TTCK VN suy giảm CẤU TRÚC hay CHU KỲ?"**

> **CHU KỲ — với một cải thiện cấu trúc THẬT nhưng ở MỘT TẦNG KHÁC, không phải tầng mà BAL khai thác.**

Hai chân trời cho hai câu trả lời khác nhau, và đây là phát hiện chính:

| Tầng | Thước đo | Kết quả |
|---|---|---|
| **Vi mô (ngày)** | AC(1) lợi suất NGÀY của từng cổ phiếu, trung vị cross-sectional | **CẤU TRÚC**. Break 2010, R²gain 0,644 (toàn universe) / **0,743** (rổ cân bằng 45 mã), p_perm 0,0017 / **0,0007**. Trung vị trước 0,173→0,228, sau **0,018**. Sống sót khi kiểm soát vol + |lợi suất 1 năm| (t=−2,30). |
| **Chỉ số (VNINDEX)** | VR(2/5/10) Lo-MacKinlay, Hurst DFA, AC(1) chỉ số | **KHÔNG có break đo được** (p_perm 0,68–0,99). Dao động theo chu kỳ/biến động. |
| **Trung hạn cross-sectional** = **đúng thứ BAL/SIGNAL_V11 ăn** | IC Spearman của mom(6-1) với lợi suất fwd-3M | **KHÔNG có break** (p_perm **0,216**; mom(12-1) p=0,340). Chu kỳ rõ: 3 đáy 2008-10, 2014, 2020-23 — rồi hồi. |

Và một kết quả ngược trực giác nhưng đo được: **AC(1) ngày cao (thị trường KÉM hiệu quả vi mô) đi kèm
IC momentum trung hạn THẤP hơn**, không phải cao hơn — ρ Spearman **−0,696** (p=0,001, N=19 năm);
hệ số hồi quy −0,99 (t=−2,32) khi đã kiểm soát vol. Nghĩa là "thị trường trở nên hiệu quả hơn ở tầng
ngày" **không phải tin xấu cho BAL** — dấu đi ngược lại.

⚠️ **Giới hạn phải nói thẳng**: VN chỉ có ~3 chu kỳ độc lập trong mẫu. "CHU KỲ" ở đây có nghĩa là
**không phân biệt được với chu kỳ**, không phải "đã chứng minh là chu kỳ". Xem §5.

---

## 1. Đã làm gì (BƯỚC 1) — chuỗi đo hiệu quả, CAUSAL

Tất cả cửa sổ **chỉ nhìn về quá khứ**, chốt tại cuối mỗi tháng. Không có chỉ số nào phải bỏ vì
không tính được causal.

| Chỉ số | Cửa sổ | Ghi chú |
|---|---|---|
| Variance ratio Lo-MacKinlay q=2,5,10 + z* robust phương sai thay đổi | 250 phiên trượt | VNINDEX |
| Hurst (DFA bậc 1) | 500 phiên trượt | VNINDEX (cần nhiều điểm hơn VR) |
| AC(1) chỉ số | 250 phiên trượt | VNINDEX |
| AC(1) cross-sectional, trung vị | 12 tháng dương lịch trượt, ≥100 phiên/mã | thành viên `universe_pit` |

Output: `efficiency_monthly.csv` (315 tháng, 2000-07 → 2026-09).

**Estimator đã được self-check, không chỉ "chạy không lỗi"** (`selfcheck_efficiency.py`, 8/8 PASS,
`$DNA_PYEXE`):
- iid → VR(2) trung bình 1,0014; sd(z\*)=1,070; tỷ lệ bác bỏ 7,0% (≈ mức 5% danh nghĩa).
- AR(1) φ=+0,2 → VR(2)=1,1937 (lý thuyết 1,20), power 0,868 · AR(1) φ=−0,2 → VR(2)=0,7968 (lý thuyết 0,80).
- Hurst iid → 0,4955 · Hurst chuỗi tích luỹ → 1,46 (>0,5 rõ).
⇒ estimator CÓ khả năng bắt được cả 2 chiều; kết quả "không có break" không phải do công cụ mù.

### Tại sao test break chạy trên chuỗi NĂM, không chạy trên chuỗi tháng
Chuỗi tháng dùng cửa sổ trượt 250 ngày ⇒ **chồng lấn nặng**, t-stat tháng-qua-tháng là giả. Test
thống kê chạy trên **thống kê NĂM DƯƠNG LỊCH không chồng lấn**: mỗi năm góp **1** quan sát ⇒
N=19–21 năm thật, không phải 226 quan sát giả (`efficiency_annual.csv`). Break tìm bằng least-squares
1 điểm gãy, p-value bằng **permutation** (hoán vị năm, chạy lại đúng thuật toán tìm break) — chống
đúng cái bẫy "chuỗi 19 điểm nào cũng có một break đẹp nhất".

---

## 2. BƯỚC 2 — proxy hệ sinh thái VN: cái gì CÓ, cái gì KHÔNG

Đã tra `mike/kb/data_registry/index.md` + toàn bộ `tav2_bq`, `tav2_mike`, `WorkingClaude/data/`.

| Chiều được hỏi | Có dữ liệu thật? | Nguồn / trạng thái |
|---|---|---|
| **Dòng tiền khối ngoại ròng** | ✅ **CÓ, đã lấy thật** | VNDirect finfo `api-finfo.vndirect.com.vn/v4/foreigns`, registry `feeds/foreign_flow_vndirect.md` **CANDIDATE-FEASIBLE (chưa wire)**. Kéo được **1.998 phiên, 2018-08-30 → 2026-09-10** — khớp chính xác cảnh báo "chỉ từ 2018-08-30" trong registry. → `foreign_flow_vnindex_raw.csv` |
| **Tỷ lệ nhà đầu tư cá nhân** | ❌ **KHÔNG có dạng chuỗi** | Chỉ có **điểm rời rạc, nguồn thứ cấp**, đã ghi sẵn trong registry `market-state/vn_market_maturation_structural_20260830.md` (Bobby, 2026-08-30): tỷ trọng giao dịch khối ngoại 11%(2005)→22-25%(2007-08)→**~5-6% (2024-05)**. Nguồn báo chí, **CHƯA đối soát nguồn sơ cấp SSC/HOSE**. Không có chuỗi theo tháng/năm. |
| **Dư nợ margin toàn thị trường / vốn hoá** | ❌ **KHÔNG có, ở bất kỳ đâu** | Không có bảng BQ, không có file local, không có entry registry. ⚠️ **Bẫy tên**: `data/margin_cycle_detector.csv` **KHÔNG phải** margin debt — đó là chu kỳ **biên lợi nhuận gộp (GPM)** của doanh nghiệp chế biến hàng hoá, không liên quan. |
| **Số tài khoản mở mới** | ❌ **KHÔNG có dạng chuỗi** | Điểm rời rạc thứ cấp trong cùng file registry Bobby: 2,77tr (cuối 2020) → 6,83tr (cuối 2022) → 7,9tr (2024-05). **CHƯA đối soát VSD gốc.** Không có chuỗi. |

**Không bịa số nào.** Không dùng WebSearch để bổ sung con số mới: registry đã có sẵn các điểm thứ cấp
kèm nguồn + ngày, và thêm một lớp thứ cấp nữa không làm dữ liệu tốt hơn — nó chỉ làm mất dấu vết
provenance đã có.

### Proxy tự dựng được từ dữ liệu SỞ HỮU (`ecology_monthly.csv`)
- **E2 tỷ trọng tham gia gộp của khối ngoại** = (mua+bán ngoại) / thanh khoản `universe_pit`.
  ⚠️ **MỨC bị thổi lên** (tử số HOSE-only, đếm 2 chiều; mẫu số chỉ ~400 mã thanh khoản, mọi sàn) —
  **chỉ đọc XU HƯỚNG, đừng trích con số tuyệt đối**: 0,44 (2019) → **0,156 (2021, đỉnh F0)** → 0,29 (2026).
  Xu hướng này **độc lập xác nhận** dòng "khối ngoại co lại" của Bobby bằng dữ liệu giao dịch thật.
- **E3 thanh khoản thực** (quy về VND không đổi, hằng số `Inflation_7` = 7%/năm của codebase):
  ~38–126 nghìn tỷ/tháng (2008-2017) → **690 nghìn tỷ (2021)** → 423–588 nghìn tỷ (2024-26).
- **E4 độ rộng universe**: 160 (2008) → 568 (2022) → ~400 (2026).

---

## 3. BƯỚC 3 — ghép và đọc kết quả

**Biểu đồ**: `vn_efficiency_gauge.png` (4 panel: AC(1) cross-sec · VR(2)/VR(10) · Hurst · IC momentum
12M). Dải vàng = vị trí break tìm được (2010); nhãn p_perm trên hình lấy từ test NĂM (§1), không phải
từ chuỗi tháng vẽ trên hình.
**Bảng**: `amh_gauge_annual.csv` — 1 dòng/năm, gộp cả 3 nhóm.

| year | vr2 | vr2_z | hurst | ac1_idx | **ac1_cs** | **mom6 IC** | mom12 IC | foreign_share | vol_ann |
|---|---|---|---|---|---|---|---|---|---|
| 2008 | 0,620 | −0,89 | 0,351 | −0,386 | **0,246** | −0,104 | −0,019 | — | 0,941 |
| 2009 | 1,292 | +4,01 | 0,592 | +0,283 | **0,206** | −0,052 | −0,063 | — | 0,344 |
| 2010 | 1,109 | +1,51 | 0,512 | +0,126 | **0,042** | −0,022 | −0,077 | — | 0,209 |
| 2011 | 1,290 | +3,08 | 0,696 | +0,280 | 0,007 | +0,246 | +0,152 | — | 0,210 |
| 2012 | 1,089 | +1,22 | 0,473 | +0,082 | 0,025 | +0,012 | +0,091 | — | 0,201 |
| 2013 | 1,091 | +1,29 | 0,548 | +0,086 | −0,006 | +0,133 | +0,124 | — | 0,171 |
| 2014 | 0,976 | −0,25 | 0,488 | −0,028 | −0,018 | +0,007 | −0,029 | — | 0,177 |
| 2015 | 1,166 | +2,23 | 0,542 | +0,157 | −0,018 | +0,212 | +0,143 | — | 0,166 |
| 2016 | 1,035 | +0,48 | 0,566 | +0,028 | −0,008 | +0,118 | +0,148 | — | 0,139 |
| 2017 | 0,989 | −0,16 | 0,469 | −0,013 | 0,016 | +0,046 | +0,110 | — | 0,098 |
| 2018 | 0,987 | −0,16 | 0,564 | −0,019 | −0,016 | +0,052 | +0,010 | 0,32 | 0,222 |
| 2019 | 1,068 | +1,03 | 0,461 | +0,060 | 0,005 | +0,105 | +0,074 | 0,44 | 0,108 |
| 2020 | 1,155 | +1,76 | 0,626 | +0,147 | 0,083 | −0,056 | −0,077 | 0,31 | 0,229 |
| 2021 | 1,009 | +0,09 | 0,473 | +0,004 | 0,065 | +0,000 | +0,012 | 0,16 | 0,212 |
| 2022 | 1,068 | +0,88 | 0,508 | +0,063 | 0,099 | +0,039 | −0,092 | 0,18 | 0,249 |
| 2023 | 0,996 | −0,07 | 0,489 | +0,010 | 0,012 | −0,093 | −0,049 | 0,18 | 0,170 |
| 2024 | 0,932 | −0,90 | 0,504 | −0,075 | −0,038 | **+0,127** | +0,077 | 0,21 | 0,135 |
| 2025 | 1,199 | +1,67 | 0,431 | +0,191 | 0,064 | **−0,026** | −0,068 | 0,23 | 0,212 |
| 2026\* | 1,108 | +1,12 | — | +0,095 | −0,007 | **+0,139** | +0,096 | 0,29 | 0,205 |

\* 2026 = 5 cross-section (dự báo T1→T5/2026, vì fwd-3M cần dữ liệu tới T8/2026). Hurst 2026 thiếu
(chưa đủ 500 phiên trong năm).

### 3.1 Cái GÌ gãy cấu trúc — và cái đó có phải "thị trường thông minh lên" không
`ac1_cs` rơi từ 0,17–0,25 (2006-2009) xuống ~0,02 và **chưa bao giờ quay lại vùng cũ** (đỉnh sau
break: 0,099 năm 2022, vẫn dưới một nửa mức trước 2010).

Ba kiểm tra để loại giả thuyết "chỉ là universe to ra":
- **Rổ CÂN BẰNG 45 mã** có mặt đủ 17 năm 2009-2025: break **mạnh hơn** (R²gain 0,743 vs 0,644,
  p_perm 0,0007 vs 0,0017), trước 0,228 → sau 0,019. ⇒ **không phải hiệu ứng thành phần**.
- **Dose-response**: tỷ lệ mã có AC(1) > 0,05 rơi 0,93–0,98 (2006-2009) → 0,23–0,45 (2010-2019).
  Không phải một trung vị lẻ nhảy.
- **Kiểm soát chu kỳ**: hồi quy `ac1_cs ~ 1 + dummy_post + log(vol) + |lợi suất 1 năm|` → dummy
  **t=−2,30** (sống), trong khi cùng mô hình cho vr2/ac1_idx/hurst cho t=−0,37/−0,49/−1,17 (chết).

**Nhưng phải nói thẳng cái không tách được**: 2008 có vol năm 94%, universe 160 mã. Một phần AC(1)
ngày cao thời kỳ đó đến từ **cơ học** — giá kẹt biên độ, giá cũ (stale), thanh khoản mỏng — chứ không
phải "arbitrageur ngày xưa dở hơn". Dữ liệu này **không phân biệt được** "thị trường học được cách
định giá" với "thị trường thôi bé tí". Cả hai đều là cấu trúc, nhưng hàm ý khác nhau, và tôi không
có bằng chứng để chọn.

### 3.2 Cái GÌ không gãy — chính là tầng BAL đứng
IC mom(6-1) → fwd-3M: **không có break** ở bất kỳ điểm nào trong lưới 2010-2022 (p_perm 0,216).
Hình dạng là chu kỳ, biên độ ổn định:

| Giai đoạn | mom6 IC TB | tỷ lệ tháng IC>0 | mom12 IC TB |
|---|---|---|---|
| 2007-2009 | −0,063 | 0,38 | −0,042 |
| 2010-2014 | +0,075 | 0,60 | +0,052 |
| 2015-2019 | **+0,107** | **0,73** | +0,097 |
| 2020-2023 | −0,027 | 0,46 | −0,052 |
| 2024-2026 | +0,066 | 0,66 | +0,021 |

Đáy 2020-2023 (−0,027) **không sâu hơn** đáy 2007-2009 (−0,063), và đã hồi: 2024 +0,127, 2026(T1-T5)
+0,139. Năm yếu 2025 (−0,026) nằm trong biên độ dao động lịch sử, không nằm ngoài.

### 3.3 Đối chiếu với `edge_health` production (bắt buộc — §12 skill quant-research)
KB ghi "mom_200 và D_RSI FLIPPED từ 04/2026". Đọc thẳng artifact
`WorkingClaude/data/edge_health_ic.csv` (do `papertrade_daily.sh` ghi): mom_200 IC theo tháng
**2026-04 = −0,060 · 2026-05 = +0,285 · 2026-06 = +0,382**. Đo độc lập của tôi trên panel riêng:
mom6 IC **2026-04 = +0,252 · 2026-05 = +0,221**.

⇒ **Hai hệ đo độc lập cùng nói momentum đã quay đầu DƯƠNG trong Q2/2026.** Nhãn "FLIPPED" còn treo là
**độ trễ của verdict cửa sổ 12M**, không phải bất đồng dữ liệu — đúng gap **G2/G3** trong rà soát AMH
của Mike. Không nên đọc nhãn FLIPPED hôm nay như một tuyên bố về hiện tại.

### 3.4 Liên hệ với hệ sinh thái — và một chỗ AMH ngây thơ đoán SAI dấu
Trực giác AMH thô: nhiều retail hơn ⇒ kém hiệu quả hơn ⇒ momentum ăn tốt hơn. **Dữ liệu VN nói ngược.**
Giai đoạn retail thống trị nhất (2020-2023, `foreign_share` chạm đáy 0,156 năm 2021, thanh khoản thực
gấp ~4 lần) trùng đúng **giai đoạn IC momentum tệ nhất** (−0,027). Khi khối ngoại quay lại
(0,21→0,29, 2024-2026), IC momentum dương trở lại.

Định lượng (mô tả, KHÔNG phải kiểm định — N=9 và N=19 năm):
- `foreign_share` vs mom6 IC: ρ=+0,300 (p=0,433, N=9) — **không kết luận được gì**, nói thẳng.
- `ac1_cs` vs mom6 IC: ρ=**−0,696** (p=0,001, N=19); hồi quy b=−0,99, **t=−2,32** khi kiểm soát vol
  (vol tự nó rớt xuống t=+0,48) ⇒ AC(1) ngày **không** chỉ là đại diện cho biến động.
- `vol_ann` vs mom6 IC: ρ=−0,507 (p=0,027, N=19).

**Cơ chế hợp lý** (giả thuyết, chưa test): AC(1) ngày cao co cụm vào giai đoạn khủng hoảng/biến động
cao — kẹt biên độ, thanh khoản bốc hơi — mà đó chính là vùng **momentum crash**. Nên "kém hiệu quả vi
mô" và "momentum ăn được" là **hai thứ khác nhau**, thậm chí đối nghịch.

---

## 4. Hàm ý (chẩn đoán — KHÔNG có đề xuất wire nào)

1. **Không có bằng chứng cho luận điểm "momentum VN chết vì thị trường hiệu quả lên".** Tầng hiệu quả
   lên thật (AC ngày) không phải tầng BAL đứng, và tương quan giữa hai tầng **âm**, không dương.
2. **BAL yếu 2025 giống chu kỳ hơn giống mục nát.** Ba đáy tiền lệ có độ sâu tương đương, đều hồi.
   Đây là bằng chứng ủng hộ **G1** — cần *edge-gate* (giảm size khi đáy chu kỳ) chứ không phải quyết
   định *bỏ* BAL.
3. **Nhãn edge-health hôm nay đang trễ pha thật.** Bằng chứng số ở §3.3; củng cố **G2/G3**.
4. **Khoảng trống dữ liệu hệ sinh thái là THẬT và có thể lấp một phần rẻ**: foreign flow (2018+) đã
   chứng minh lấy được trong 1 lần gọi API. Margin debt / retail share / tài khoản mở mới thì **không
   có nguồn nào trong tay** — muốn có phải đi lấy từ VSD/SSC/HOSE, không suy ra được.

---

## 5. Giới hạn — đọc trước khi trích bất kỳ con số nào

- **N chu kỳ ≈ 3.** "Không phát hiện được break" ≠ "chắc chắn không có break". Với N=19-21 năm, một
  suy giảm cấu trúc CHẬM sẽ không bị lưới này bắt. Đây là lý do §0 nói "không phân biệt được với
  chu kỳ", không nói "đã chứng minh là chu kỳ".
- **2026 chưa đủ năm** — chỉ 5 cross-section cho IC, chưa đủ 500 phiên cho Hurst.
- **Break "2010" là năm, không phải ngày.** Thống kê năm không định vị được tháng.
- **`ac1_cs` trước 2010 lẫn cơ học vi cấu trúc** (biên độ, stale price, universe 160 mã) — xem §3.1.
- **`foreign_share` chỉ đọc được XU HƯỚNG**, mức tuyệt đối sai lệch (§2).
- **Retail share / margin debt / tài khoản mới: các con số duy nhất tồn tại là THỨ CẤP, CHƯA ĐỐI SOÁT**
  (báo chí, qua registry Bobby 2026-08-30). Không được trích như số liệu sơ cấp.
- **Đây là thước đo CHẨN ĐOÁN, không phải tín hiệu.** Tín hiệu AMH duy nhất từng test theo hướng
  (ecology mood) đã bị **REFUTED walk-forward 2026-07-13**. Không lặp lại lỗi đó: không có luật giao
  dịch nào được dẫn xuất từ file này.
- **Không chạm production**: `git status` sạch trên mọi file `.py`; toàn bộ output nằm trong thư mục
  research này.

---

## 6. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/vn_market_efficiency_20260910
PY=/home/trido/thanhdt/wc_venv/bin/python     # $DNA_PYEXE (pandas 3.0.2 / numpy 2.4.4)
$PY pull.py               # 2 query BQ  -> vnindex_daily.csv, panel_ac_stats.csv (billed 51MB + 145MB)
$PY selfcheck_efficiency.py   # 8/8 PASS — chạy TRƯỚC khi tin bất kỳ số nào
$PY efficiency.py         # -> efficiency_monthly.csv
$PY structural.py         # -> efficiency_annual.csv + test break + kiểm soát chu kỳ
$PY robustness.py         # rổ cân bằng + lưới break rộng + dose-response
$PY momentum_env.py       # -> momentum_ic_{monthly,annual}.csv  (query q3 đã pull sẵn)
$PY ecology.py            # -> ecology_monthly.csv  (cần foreign_flow_vnindex_raw.csv)
$PY combine.py            # -> amh_gauge_annual.csv + vn_efficiency_gauge.png
```

**Vintage**: BQ đọc LIVE 2026-09-10, `tav2_bq.ticker` và `tav2_mike.universe_pit` cùng có
`MAX(time)=2026-09-10`. Foreign flow kéo 2026-09-10 (tới phiên 2026-09-10).
**Nguồn đã tra registry trước khi dùng**: `ticker_ohlcv_tables.md` CANONICAL ·
`universe_pit.md` CANONICAL · `feeds/foreign_flow_vndirect.md` CANDIDATE-FEASIBLE (chưa wire — dùng
cho nghiên cứu, không wire vào gì) · `ticker_close_vs_price_dividend_adj.md` TRAP → dùng `Close`
(đã điều chỉnh) cho MỌI phép tính lợi suất, `COALESCE(Price, Close)` cho giá trị giao dịch.
