# Định lượng correlation risk sleeve discretionary margin — 5% vs 10% vs 15%

> Job `Taylor_20260830_035805` · 2026-08-30 · **RESEARCH-ONLY, KHÔNG đổi policy/code.**
> Tiền đề: forensic combined-margin cấp account (`combined_margin_forensic_account_level_20260830.md`,
> job `Taylor_20260830_031004`) đã xác nhận margin ratio KHÔNG PHẢI ràng buộc thật ở f=1,3, kể cả ở
> sleeve 15%. risk-auditor 08-29 chỉ rõ: nếu giữ 5%, lý do phải là **correlation risk**, không phải
> margin-survival — nhưng risk đó mới chỉ là nhận định định tính (`margin_cap_recovery_forensic_
> 20260825.md` §A4). Job này định lượng nó bằng dữ liệu thật.

## Kết luận 1 dòng
Correlation giữa các mã "fear-buy" cùng profile (illiquid + PB<1 + bị bán tháo >30%) **tăng
thật, có ý nghĩa, trong đúng loại khủng hoảng kích hoạt sleeve** (ρ crisis ≈0,18-0,25 episode-avg
đã sửa qua risk-auditor review — xem §8, tới 0,37 ở khủng hoảng hệ thống kiểu GFC, vs ρ baseline
~0,05 — tăng 3,6-5 lần) — NHƯNG chưa đủ cao để biến "trần lý thuyết N×1,5% NAV" thành kịch bản kỳ
vọng: ở N=3 case đồng thời (sleeve 15%), tổn thất kỳ vọng có điều chỉnh correlation ≈**2,10-2,61%
NAV** (47-58% trần lý thuyết 4,5% NAV), so với 1,5% NAV nếu giả định độc lập hoàn toàn (33% trần).
Phát hiện phụ quan trọng hơn cả con số ρ: **correlation đo trên đúng nhóm thanh khoản mỏng như TV1
bị UNDERSTATE do stale-pricing, và CHƯA HỘI TỤ ngay cả ở cửa sổ 10 ngày** (§3 + §8) — dùng số đo
trực tiếp trên mã mỏng sẽ cho ảo giác "gần như độc lập" trong khi rủi ro hệ thống thật vẫn ở đó,
chỉ không hiện ra ngày-qua-ngày. **risk-auditor CONDITIONAL-APPROVE, nghiêng khuyến nghị giữ trần
5%** (§8) — chủ yếu vì điều kiện mở lại theo chính sách (≥3 case marginable đồng thời) chưa thoả,
không chỉ vì correlation math.

---

## 1. Phương pháp

**Cohort "fear-buy profile"** (không dùng lại đúng TV1/DGC vì 2 mã này không cùng tồn tại lịch sử
với các khủng hoảng cũ — dùng nhóm ĐẠI DIỆN cùng đặc tính, đúng như dispatch cho phép): tại một
thời điểm trong mỗi episode dd52≤−20%, mã phải (a) giảm ≥30% từ đỉnh cục bộ 400 ngày lịch (nặng
hơn mức dd52 thị trường −20%, đúng kiểu "bị bán tháo panic") VÀ (b) PB<1,0 tại đúng điểm đáy đó
(deep value xác nhận, không phải "rẻ danh nghĩa"). Định nghĩa dd52 giống hệt `capit_margin_lever`
gate (rolling 252-session high, verify lại từ `build_episodes.py` đã archive).

**7 episode dd52≤−20% dùng nguyên bộ đã có** (`extreme_bottom_recognition_20260823/episodes_dd52.csv`,
merge nếu gap<90 ngày lịch — cùng định nghĩa production):

| Episode | Arm | Trough | End | n_sessions |
|---|---|---|---|---|
| 2007-04 (GFC) | 2007-04-23 | 2009-02-24 | 2009-08-18 | 578 |
| 2009-11 | 2009-11-26 | 2010-08-25 | 2010-11-24 | 249 |
| 2011-05 | 2011-05-23 | 2012-01-06 | 2012-02-17 | 188 |
| 2012-08 | 2012-08-27 | 2012-11-02 | 2012-12-11 | 76 |
| 2018-05 | 2018-05-28 | 2019-01-03 | 2019-02-18 | 183 |
| 2020-03 (COVID) | 2020-03-11 | 2020-03-24 | 2020-08-03 | 101 |
| 2022-05 (SCB) | 2022-05-13 | 2022-11-15 | 2023-05-09 | 247 |

**Nguồn dữ liệu**: BQ `tav2_bq.ticker` (Close/Volume/PB), pull qua Python BQ client + Storage API
(bq CLI paginate 1,5M dòng bị treo — đổi sang client trực tiếp, 2,26M dòng/7,8s). ⚠️ **Tự bắt được
bẫy CLAUDE.md #2 khi viết query đầu tiên**: `FROM tav2_bq.ticker` không alias làm cột `ticker`
resolve vào STRUCT cả dòng (60+ field) thay vì cột ticker thật — phải sửa thành
`FROM tav2_bq.ticker AS t ... t.ticker AS ticker`. Đã fix trước khi dùng số.

**Correlation**: return ngày (`pct_change`), Pearson pairwise trên các ngày dd52≤−20% thật (crisis)
so với dd52>−10% (normal), CÙNG bộ ticker cohort đã chọn — không so 2 universe khác nhau.

---

## 2. Kết quả chính — crisis correlation vs normal correlation

**Pooled (toàn bộ 7 episode gộp, mọi mã cohort, N=941 mã, 421.591 cặp, 1.120 ngày crisis):**

| | Mean ρ | Median ρ | p10 | p90 |
|---|---|---|---|---|
| **CRISIS** (dd52≤−20%) | **0,130** | 0,114 | −0,048 | 0,339 |
| **NORMAL** (dd52>−10%, cùng mã, 1.873 ngày) | **0,053** | 0,049 | −0,035 | 0,150 |
| **Tỷ lệ crisis/normal** | **2,45×** | 2,32× | — | — |

**Per-episode (N=7, đơn vị sự kiện ĐỘC LẬP thật, không phải N=pairs hay N=days — đúng nguyên tắc
quant-research "N là sự kiện, không phải hàng"):**

| Episode | Mean ρ (mọi mã cohort) | n mã | n ngày |
|---|---|---|---|
| 2007-04 (GFC) | **0,374** | 268 | 578 |
| 2009-11 | 0,301 | 468 | 249 |
| 2022-05 (SCB) | 0,135 | 915 | 247 |
| 2011-05 | 0,151 | 542 | 188 |
| 2012-08 | 0,113 | 478 | 76 |
| 2020-03 (COVID) | 0,099 | 711 | 101 |
| 2018-05 | 0,036 | 766 | 183 |

- **Trung bình 7 episode (unweighted): ρ≈0,173**, median 0,135, range **0,036–0,374**.
- **N=7 là mẫu nhỏ, và 2 episode cao nhất (2007-04, 2009-11) thực chất là MỘT khủng hoảng kéo dài**
  (GFC + dư chấn) — nếu gộp lại thành 1 sự kiện, N thực tế ≈6, và biến thiên giữa episode LỚN hơn
  cả biến thiên trong 1 episode → không có CI chặt, chỉ có RANGE.
- **Discriminator rõ**: khủng hoảng **hệ thống/tín dụng** (GFC 0,374, dư chấn 2009 0,301) đẩy
  correlation cao hơn hẳn khủng hoảng **cục bộ/chính sách** (2018 trade-war 0,036, COVID 0,099 —
  dù COVID là cú sốc lớn, nó phục hồi rất nhanh và không đồng bộ theo ngành). Đúng tinh thần macro-
  strategist: loại khủng hoảng quyết định mức độ đồng pha, không phải độ sâu dd52.

---

## 3. ⚠️ Phát hiện quan trọng hơn cả con số ρ — illiquid-tercile UNDERSTATE correlation

Tách cohort mỗi episode theo ADV (median Close×Volume trong cửa sổ episode) thành 3 nhóm, so
tercile thanh khoản THẤP NHẤT (đúng profile TV1 — UPCOM, ADV ~0,6-0,84 tỷ/ngày) với tercile CAO
NHẤT (cùng bộ lọc PB<1+dd≥30%, chỉ khác thanh khoản):

| Episode | ρ ILLIQUID tercile | ρ LIQUID tercile | Tỷ lệ liquid/illiquid |
|---|---|---|---|
| 2007-04 | 0,303 | 0,475 | 1,6× |
| 2009-11 | 0,199 | 0,488 | 2,5× |
| 2011-05 | 0,042 | 0,386 | 9,3× |
| 2012-08 | 0,008 | 0,345 | 43× |
| 2018-05 | 0,001 | 0,110 | 95× |
| 2020-03 | 0,011 | 0,344 | 33× |
| 2022-05 | 0,016 | 0,460 | 29× |

**7/7 episode: illiquid tercile đo được correlation THẤP HƠN NHIỀU liquid tercile CÙNG PROFILE**
(cùng bị chọn vì PB<1 + bán tháo ≥30%, khác duy nhất thanh khoản). Đây gần chắc chắn là **artifact
giá trễ (stale pricing)**, không phải bằng chứng illiquid thật sự ít rủi ro hệ thống hơn — verify
bằng 2 test:
1. **% ngày return=0** (không đổi giá — dấu hiệu trực tiếp giá trễ): illiquid cao hơn liquid ở
   hầu hết episode (vd 2020-03: 24,3% vs 13,6%; 2022-05: 24,3% vs 11,7%) — có, nhưng KHÔNG đủ lớn
   để tự nó giải thích hết khoảng cách ρ 0,01 vs 0,34.
2. **Horizon-test** (nếu là artifact đồng bộ hoá giá, correlation phải PHỤC HỒI khi kéo dài cửa sổ
   đo return): đúng — ρ illiquid tăng từ **0,083 (1 ngày) → 0,123 (5 ngày) → 0,148 (10 ngày)**
   trong khi liquid chỉ tăng nhẹ (0,373→0,442→0,472). Illiquid PHỤC HỒI về gần đúng con số pooled
   toàn cohort (0,130) khi cho đủ thời gian phát giá — xác nhận cơ chế: giá mã mỏng không phản ứng
   CÙNG NGÀY với cú sốc hệ thống (biên độ giá + thiếu đối ứng mua/bán khiến discovery lệch pha
   từng mã), nhưng khi giá CUỐI CÙNG di chuyển, nó vẫn đi theo đúng hướng hệ thống — rủi ro thật
   không biến mất, chỉ **trễ pha và dồn cục** (gap nhiều phiên liên tiếp cùng chiều).

**Hệ quả cho sizing**: nếu dùng thẳng số đo 1-ngày trên đúng mã mỏng (ρ≈0,01-0,08), sẽ kết luận sai
"gần như độc lập, mở sleeff thoải mái". Số đúng hơn để LÊN KẾ HOẠCH RỦI RO là ở giữa — dùng **liquid-
tercile cùng profile làm cận trên "rủi ro hệ thống chưa bị che"** (0,30-0,49) và **illiquid 10-ngày
làm cận dưới đã hiệu chỉnh staleness một phần** (0,15) — khuyến nghị **ρ_planning ≈0,15-0,20** cho
kịch bản thường, và **0,30-0,37 cho kịch bản stress hệ thống** (không dùng số 1-ngày thô 0,01-0,08
làm cơ sở quyết định).

---

## 4. Model — tổn thất kỳ vọng khi arm N case đồng thời (5%/10%/15% NAV sleeve)

**Công thức** (one-factor xấp xỉ tuyến tính, đã kiểm tra hội tụ đúng 2 biên ρ=0 và ρ=1):
`E[loss_total] = L + (N−1)×ρ×L`, trong đó `L` = tổn thất thực nhận per-case tại exit −20%
(**1,5% NAV** — số đã chốt trong chính sách hiện hành, exposure_cap 5% NAV × 20% + haircut
slippage/lãi vay, xem `discretionary-margin-policy-20260823.md`). `N×L` = trần lý thuyết
(deterministic, KHÔNG đổi theo ρ — đây chính là điểm dispatch cần làm rõ: "trần" và "kỳ vọng" là
2 đại lượng khác nhau, ρ chỉ quyết định trần đó có PHẢI kịch bản kỳ vọng hay chỉ là đuôi hiếm).
So sánh với ngân sách rủi ro portfolio (**bootstrap 5th-pct V2.4 MaxDD −28,6% NAV**, pin trong KB):

| ρ giả định | N=1 (sleeve 5%) | N=2 (sleeve 10%) | N=3 (sleeve 15%) |
|---|---|---|---|
| **0,00** (độc lập — giả định ngầm bảng cũ) | 1,5% NAV (5,2% ngân sách) | **1,5%** NAV (5,2%) | **1,5%** NAV (5,2%) |
| **0,13** (pooled crisis, mọi thanh khoản) | 1,5% (5,2%) | 1,70% (5,9%) | 1,89% (6,6%) |
| **0,17** (trung bình 7 episode, khuyến nghị dùng làm base case) | 1,5% (5,2%) | 1,75% (6,1%) | **2,01%** (7,0%) |
| **0,37** (GFC-style, stress case) | 1,5% (5,2%) | 2,05% (7,2%) | **2,61%** (9,1%) |
| **1,00** (lockstep hoàn toàn) | 1,5% (5,2%) | 3,00% (10,5%) | **4,50%** (15,7%) |
| **Trần lý thuyết (deterministic, mọi ρ)** | 1,5% (5,2%) | 3,00% (10,5%) | 4,50% (15,7%) |

**Đọc bảng**: ở N=3 (sleeve 15%, kịch bản đã bị REJECT 08-29), tổn thất **kỳ vọng** dùng ρ đo được
thật (base case 0,17 → stress 0,37) rơi vào **2,01–2,61% NAV (7,0–9,1% ngân sách drawdown)** —
**thấp hơn ĐÁNG KỂ** trần lý thuyết 4,5% NAV (15,7% ngân sách) nếu coi "cả 3 case cùng chạm −20%
đồng thời" là kịch bản CHẮC CHẮN. Nhưng cũng **cao hơn có ý nghĩa** so với giả định độc lập hoàn
toàn (1,5% NAV không đổi theo N — tức bảng cũ N×1,5% chỉ đúng làm TRẦN, không phải kỳ vọng, và nếu
ai đọc N×1,5% như "tổn thất trung bình" thì đã NGẦM ĐỊNH ρ=1, không phải ρ=0 như dispatch nêu —
xem đính chính §5).

---

## 5. ⚠️ Đính chính khung dispatch — "bảng max-loss cũ ngầm định correlation=0" cần làm rõ 2 nghĩa

Dispatch đặt câu hỏi coi bảng N×1,5% NAV là ngầm định độc lập (ρ=0). Đọc kỹ lại: bảng đó là
**TRẦN xác định (deterministic ceiling)** — N case cùng cap 5% exposure, cùng cap thoát −20%, cộng
thẳng ra N×1,5% — phép cộng này **ĐÚNG ở MỌI ρ** vì nó không giả định gì về XÁC SUẤT đồng thời, chỉ
mô tả "nếu cả N case CÙNG chạm trần thì tổng là bao nhiêu". Cái THỰC SỰ phụ thuộc ρ là:
**(a) N case có thực sự cùng chạm trần không** (→ E[loss] ở §4, dùng ρ đo được) và
**(b) xác suất kịch bản "cả N cùng chạm" xảy ra** (→ chưa lượng hoá đầy đủ ở job này, xem giới hạn).
Kết luận thực dụng cho user: **trần N×1,5% NAV vẫn là con số ĐÚNG để công bố cho người duyệt** (nó
là trần, không phải kỳ vọng, và trần không đổi theo ρ) — cái MỚI job này thêm là **kỳ vọng thực tế
thấp hơn trần 40-70% tuỳ ρ**, tức trần đã BẢO THỦ sẵn, không cần thêm hệ số an toàn correlation nào
nữa lên trên trần đó.

---

## 6. Trả lời câu hỏi user — 5% đủ rộng hay đã đúng trần?

**Không tự quyết — đây là câu hỏi risk-appetite, đưa khung số đầy đủ:**

- **Correlation risk LÀ THẬT và có ý nghĩa** (2,4-3,4× baseline, xác nhận định tính A4 bằng số),
  nhưng **không đủ lớn để tự nó cấm mở rộng sleeve lên 10% hoặc 15%** trên trục thuần correlation —
  ở base case (ρ=0,17), tổn thất kỳ vọng N=3 (2,01% NAV = 7,0% ngân sách drawdown) vẫn là mức
  chấp nhận được so với các sleeve/lever khác đã duyệt trong hệ thống (vd single-episode
  `capit_margin_lever` documented borrow 25,9% NAV debt).
- **Trần lý thuyết (worst-case, không phải kỳ vọng) mới là con số đáng thận trọng**: N=3 chạm 4,5%
  NAV = 15,7% ngân sách drawdown CHO MỘT SLEEVE ĐƠN LẺ trong một portfolio đã có ngân sách DD toàn
  phần −28,6% — đây là câu hỏi risk-appetite thật (có chấp nhận 1 sleeve phụ trợ ăn tới ~16% ngân
  sách rủi ro CHÍNH trong kịch bản xấu nhất hay không), KHÔNG PHẢI câu hỏi correlation math nữa.
- **Điều kiện thực tế còn thiếu, độc lập với correlation**: chính sách hiện hành ghi "≥3 case
  marginable đồng thời trong QUALIFY" là điều kiện mở lại 15% — hiện chỉ có TV1 (không marginable,
  UPCOM) và DGC (chưa xác nhận marginable SpaceX) → **N=3 đồng thời hiện tại là kịch bản GIẢ ĐỊNH,
  chưa từng xảy ra thật**. Correlation risk vừa đo là input CHO TƯƠNG LAI khi điều kiện đó thoả,
  không phải lý do để hành động ngay bây giờ.
- **Khuyến nghị trung lập cho user cân nhắc** (không phải quyết định của Taylor): nếu muốn nới,
  **10% (N=2) là bước đệm hợp lý hơn nhảy thẳng 15%** — ở N=2, kỳ vọng correlated-loss (1,75-2,05%
  NAV, 6,1-7,2% ngân sách) gần với trần lý thuyết N=1 hiện tại hơn N=3, và cho phép tích luỹ thêm
  dữ liệu thật (nếu có ≥2 case marginable đồng thời) trước khi cân nhắc N=3.

---

## 7. Giới hạn phải mang theo

1. **Cohort là ĐẠI DIỆN, không phải TV1/DGC thật** — do 2 case bản chất KHÔNG cùng tồn tại lịch sử
   với 7 episode cũ (đúng lý do chính sách "không backtest được", `discretionary-margin-policy-
   20260823.md`). ρ đo trên profile PB<1+washout≥30% là proxy hợp lý nhất có thể dựng, không phải
   con số "đúng" tuyệt đối cho chính 2 mã này.
2. **Rủi ro "enforcement-cluster" KHÔNG đo được bằng correlation giá** — các đợt bắt bớ/khởi tố ở
   VN thường đi theo CHIẾN DỊCH (nhiều DN cùng lúc trong 1 đợt thanh tra ngành/lĩnh vực), một nguồn
   correlation HOÀN TOÀN KHÁC (đồng nguyên nhân pháp lý, không phải đồng pha giá) mà phân tích return
   không bắt được. Đây là rủi ro CHƯA lượng hoá, cần theo dõi định tính riêng (tương tự cách §0.5
   khung `calculated_fear_state_backstop.md` phân loại trigger).
3. **One-factor linear approximation** (`E[loss_j|loss_i]=ρ×loss_i`) giả định phân phối gần chuẩn —
   return thật có đuôi dày hơn (fat tail), nên xác suất CẢ N case cùng chạm trần trong kịch bản đuôi
   cực đoan có thể cao hơn model tuyến tính này ước tính. Model dùng ở đây cho KỲ VỌNG (expected
   value), không phải phân phối đầy đủ xác suất đồng thời — chưa làm full copula/simulation.
4. **N=7 nhỏ, và 2 episode cao nhất không hoàn toàn độc lập**: 2007-04 và 2009-11 gộp lại gần như
   1 sự kiện vĩ mô kéo dài → N thực tế cho "loại khủng hoảng hệ thống" gần 1, không phải 2 — làm
   yếu thống kê ở đúng đầu ρ CAO NHẤT (đầu quan trọng nhất cho stress case).
5. **Không backtest, không DSR/PBO** — đây là forensic/correlation-measurement trực tiếp trên dữ
   liệu lịch sử thật, đúng bản chất "chính sách không backtest được" đã ghi trong tài liệu gốc.
6. Dữ liệu BQ dùng `Close` đã điều chỉnh (adjusted) — correlation không bị nhiễu bởi cổ tức/chia
   tách, đúng chuẩn.

## 8. risk-auditor review (CONDITIONAL-APPROVE) — 2 sửa số đã verify độc lập, kết luận hướng CÀNG
## thận trọng hơn, không đảo ngược

risk-auditor phản biện độc lập báo cáo này (đọc toàn văn, tự chạy lại số từ `full_with_peak.parquet`
+ `cohort_by_episode.csv`, không chỉ đọc bản tóm tắt). Verdict: **CONDITIONAL-APPROVE** — hướng kết
luận đứng vững nhưng 2 điểm số bị lệch nhẹ về phía "trông an toàn hơn thật", cả hai đã **verify lại
độc lập bằng cách tự chạy lại** (không chỉ nhận lời risk-auditor):

1. **Bug dilution cohort ở bảng §2**: correlation per-episode ở §2 tính trên `cohort_tickers` GỘP
   CHUNG cả 7 episode (948 mã pooled), không phải cohort ĐÚNG của riêng từng episode (179/243/472/…
   như trong `cohort_by_episode.csv`) — một mã "qualify" ở episode 2022-05 vẫn lọt vào tính
   correlation cho episode 2007-04 nếu nó có giao dịch thời điểm đó, dù nó KHÔNG hề bán tháo lúc
   2007. **Verify lại bằng cách tính đúng per-episode cohort riêng**: ρ trung bình 7 episode tăng từ
   **0,173 (bug) → 0,184-0,187 (đúng)** — chênh không lớn nhưng đúng hướng risk-auditor chỉ ra.
2. **Horizon-test dừng ở 10 ngày quá sớm**: illiquid-tercile ρ **CHƯA hội tụ** ở 10 ngày — verify
   lại kéo dài tới 20/30 ngày: **0,148 (10d) → 0,174 (20d) → 0,184 (30d)**, vẫn đang tăng, trong khi
   liquid-tercile đã phẳng (~0,47-0,49). Vị thế discretionary thật giữ nhiều tuần trước khi chạm
   −20%, không phải 10 phiên — dùng mốc 10 ngày làm cận dưới ρ_planning là **quá sớm, hiểu thấp**.

**Sửa khuyến nghị ρ_planning: 0,15-0,20 (bản gốc) → 0,20-0,25** (dùng mốc hội tụ 20-30 ngày, gần
khớp trực tiếp với con số episode-avg đã sửa 0,184-0,187 — hai đường verify độc lập hội tụ về CÙNG
một vùng số, củng cố lẫn nhau). Tính lại §4 ở ρ=0,20 và ρ=0,25 (N=3, sleeve 15%):

| ρ | E[loss] N=3 | % ngân sách DD (−28,6%) |
|---|---|---|
| 0,20 (sửa, cận dưới mới) | 2,10% NAV | 7,3% |
| 0,25 (sửa, giữa) | 2,25% NAV | 7,9% |
| 0,37 (stress GFC, không đổi) | 2,61% NAV | 9,1% |

Vẫn **thấp hơn đáng kể** trần lý thuyết 4,5% NAV (15,7% ngân sách) — 2 sửa số **không đảo ngược**
kết luận trung tâm (§4-6), chỉ thu hẹp khoảng cách giữa "kỳ vọng" và "trần" một chút (từ 42-58% lên
~47-58% của trần). Coi mọi con số ρ_planning và E[loss] trong §4/§6 ở trên là **cận dưới**, không
phải điểm ước lượng trung tâm, kể từ bản sửa này.

**Điểm risk-auditor không phản đối** (giữ nguyên, không sửa): logic §5 (trần N×1,5% là deterministic,
đúng ở mọi ρ) — xác nhận ĐÚNG, không phải chơi chữ. Cohort đại diện (không phải TV1/DGC thật) — chấp
nhận được với điều kiện disclose rõ đây là đo "co-movement hệ thống KHI panic xảy ra", không phải
correlation của 2 câu chuyện scandal độc lập — đã có ở §7.1, giữ nguyên.

**Khuyến nghị cuối của risk-auditor (không phải quyết định Taylor)**: **nghiêng về GIỮ trần 5%** —
không chủ yếu vì correlation math (ρ sửa 0,20-0,25 vẫn không đẩy E[loss] N=3 vượt trần 4,5%), mà vì
**điều kiện mở lại theo chính chính sách chưa thoả** (chưa từng có ≥3 case marginable đồng thời thật
— toàn bộ N=3 vẫn là kịch bản giả định). Nếu user muốn nới, **10% (N=2) vẫn là bước hợp lý hơn** so
với nhảy thẳng 15%, và nên dùng ρ đã sửa (0,20-0,25) khi tính lại size một khi có case thứ 2 thật.

---

## Liên quan
- `combined_margin_forensic_account_level_20260830.md` (job `Taylor_20260830_031004`) — tiền đề:
  margin ratio không phải ràng buộc, correlation risk là lý do hợp lệ duy nhất còn lại.
- `margin_cap_recovery_forensic_20260825.md` §A4 — nhận định định tính gốc (correlation sleeve vs
  BOOK hệ thống, khác trục với job này — job này đo correlation NỘI BỘ sleeve giữa các case).
- `discretionary_margin_sizing_20260829.md` — số per-case max-loss 1,5% NAV dùng làm `L` ở §4.
- `kb/projects/discretionary-margin-policy-20260823.md` — chính sách hiện hành (5% per-name,
  5% sleeve total, điều kiện mở lại 15%).
- Data/code: `agents/Taylor/research/discretionary_sleeve_correlation_20260830/` (pull_panel.py,
  cohort_corr.py, robustness_illiquid.py, corr_results.json, robustness_illiquid.json).
