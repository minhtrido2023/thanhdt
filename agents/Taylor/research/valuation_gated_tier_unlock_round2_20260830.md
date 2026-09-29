# Valuation-gated tier-unlock cho SIGNAL_V11 — ROUND 2, sửa đúng 5 điểm quant-skeptic REFUTED

Job `Taylor_20260830_132917`. User đã duyệt "làm lại hướng 1" (2026-08-30 20:28 ICT, decided_by
user) sau khi round 1 (`Taylor_20260830_124256`) bị quant-skeptic REFUTED-as-presented (medium
confidence) — xem `valuation_gated_tier_unlock_20260830.md` (giữ nguyên, không sửa, là lịch sử).
**NGHIÊN CỨU — KHÔNG wire, KHÔNG sửa `signal_v11_sql.py`/`macro_state_live.py`.**

Không đổi design/threshold/panel query gốc (đã pre-registered round 1, không tune lại theo dữ
liệu) — chỉ sửa/verify đúng 5 điểm bị REFUTED, script mới `analyze_round2.py` (tái dùng
`panel_raw.csv`/`dt5g_prod_2014plus.csv`/`phaseA_dt5g_2007_2019.csv` đã pull sẵn, không refetch BQ).

## Tóm tắt kết quả round 2

Sau khi sửa cả 5 điểm (+ 1 bug tự phát hiện qua quant-skeptic verify lần 1, xem điểm 2): **edge vẫn
dương và có ý nghĩa thống kê ở mức khiêm tốn** (cluster-robust t=**3,10** — pairs-cluster bootstrap
ĐÚNG estimator, gần ước lượng nhanh ~2,17 của quant-skeptic hơn là con số 4,19 sai ban đầu; P(mean
≤0)=0,08%, CI 90% [+1,87%,+6,06%] chứa đúng điểm ước lượng), **nhưng capacity thật ở NAV production
(50 tỷ) siết mạnh quy mô khai thác được** (60-79% episode có ADV không đủ hấp thụ 1 phiên ở cỡ vị
thế 2-5% NAV), và **suy giảm OOS vẫn tồn tại nhưng ĐỠ NGHIÊM TRỌNG hơn round 1 mô tả** (không còn
âm liên tục, chỉ 2 năm riêng lẻ 2022/2026 âm). Đây là **NO-GO CHO WIRE Ở FORM HIỆN TẠI**, nhưng
khác NO-GO tuyệt đối — capacity là nút thắt chính, không phải bản thân tín hiệu vô nghĩa.
**quant-skeptic verify: REFUTED-as-presented lần 1** (bắt đúng bug t-stat mismatch numerator/
denominator), **đã tự sửa ngay + xác nhận số đúng khớp con số "pairs-cluster-bootstrap" họ tự tính
độc lập (t=3,10, CI[1,87%,6,06%]) — đây là bản đã sửa, cần verify lại lần 2 trước khi coi là CONFIRMED.**

---

## Điểm 1 — Baseline dùng ĐÚNG state production: VERIFY, không cần sửa code

**Phát hiện quan trọng nhất của round 2: design round 1 ĐÃ ĐÚNG, không cần sửa.**

Đọc lại `pull_candidates.py`/`analyze.py` round 1: cả nhóm A (mở mới) và nhóm B (baseline "đã
fire") đều dùng state5 từ `phaseA_dt5g_2007_2019.csv` (<2014-01-02) + `dt5g_prod_2014plus.csv`
(≥2014-01-02) — **DT5G/DT4-base CANONICAL, không phải `tav2_bq.vnindex_5state` (v3.4b BASE)**.

Verify lại bằng BQ trực tiếp hôm nay (2026-08-30 20:xx ICT):
```
base_v34b_45=515, dt5g_live_45=482   (2014-01-02→2026-06-15, tav2_bq.vnindex_5state_dt5g_live)
```
Khớp CHÍNH XÁC con số quant-skeptic trích (515 vs 482). Và `dt5g_prod_2014plus.csv` (file round 1
đã dùng) tự đếm ra đúng **482** ngày state4/5 trong cùng khung — nghĩa là **design round 1 đã dùng
DT5G-live, không phải v3.4b BASE**, ngay từ đầu.

**Vậy tại sao quant-skeptic vẫn REFUTED ở điểm này?** Vì complaint thật của họ không phải "backtest
dùng sai bảng" mà là: **`signal_v11_sql.py` — file PRODUCTION thật đang chạy live V2.4 — tự nó
join `tav2_bq.vnindex_5state` (v3.4b BASE) làm `state5`, một bug riêng chưa sửa** (Phát hiện phụ #2
round 1). Nên nhóm B ("baseline hiện tại đã fire") trong backtest là counterfactual "nếu
`signal_v11_sql.py` join đúng bảng", không phải hành vi live 100% hôm nay.

**Dispatch round 2 (user 20:28 ICT) giải quyết đúng ambiguity này**: "đổi ... sang state THẬT đang
chạy sản xuất — đọc qua `get_gated_state()` hoặc join trực tiếp `vnindex_5state_dt5g_live` (DT5G
production thật)". Theo CLAUDE.md § VNINDEX 5-State, DT5G-live (qua `get_gated_state()`) **CHÍNH LÀ**
"state THẬT đang chạy sản xuất" ở tầng macro — đây là cái design round 1 đã dùng. **Kết luận: không
cần recompute, chỉ cần verify + nói rõ trong báo cáo (đã làm ở trên).** Bug riêng của
`signal_v11_sql.py` (join sai bảng) vẫn tồn tại và nên được Winston/Taylor sửa độc lập (ngoài phạm
vi job này) — nhưng nó KHÔNG làm sai kết luận của nghiên cứu này, vì nghiên cứu neo vào state đúng
theo định nghĩa production của CLAUDE.md, không neo vào bug hiện tại.

## Điểm 2 — Cluster-robust SE theo tháng-lịch

1.348 episode (sau loại banned, xem điểm 3) trải trên **172 tháng-lịch riêng biệt** — đúng như
quant-skeptic chỉ ra. Cluster bootstrap theo tháng (resample CLUSTER có hoàn lại, 5.000 lần,
không phải resample episode).

**⚠️ Tự sửa 1 bug sau khi quant-skeptic verify lần 1 phát hiện (2026-08-30, cùng ngày)**: bản đầu
`cluster_robust_tstat()` tính SAI — tử số (`grand_mean`, episode-weighted 3,95%) và mẫu số
(`se_cluster`) không cùng 1 estimator: mẫu số bootstrap trên **trung bình-của-trung-bình-cụm**
(equal-weight-by-month), trong khi tử số là episode-weighted — sinh `t=4,19` với CI 90%
`[+0,48%,+3,56%]` **không chứa nổi điểm ước lượng của chính nó (3,95%)** — bằng chứng cơ học của
bug, không phải tranh cãi phương pháp. Đã sửa: resample cluster-tháng có hoàn lại, **giữ NGUYÊN
toàn bộ episode** thuộc cụm được chọn (không rút gọn về trung bình trước), tính lại episode-
weighted mean trên tập đã pool mỗi lần resample — numerator/denominator giờ cùng 1 estimator.

| Đo | Round 1 (REFUTED) | Round 2 lần 1 (BUG, đã sửa) | **Round 2 lần 2 (đúng)** |
|---|---|---|---|
| N episode | 1.399 | 1.348 | 1.348 |
| Naive t (episode-level, KHÔNG cluster) | 7,47 | 7,21 | 7,21 |
| **Cluster t (pairs-cluster bootstrap, theo tháng)** | ~2,17 (quant-skeptic ước lượng nhanh) | 4,19 ❌ (numerator/denominator lệch estimator) | **3,10** ✅ |
| P(cluster bootstrap mean ≤ 0) | không rõ | 1,56% (sai) | **0,08%** |
| % cluster-tháng có mean âm (equal-weight) | 47% | 47,1% | 47,1% (không đổi) |
| CI 5-95% (bootstrap mean, đúng estimator) | không có | [+0,48%,+3,56%] (không chứa 3,95% — bug) | **[+1,87%,+6,06%]** (chứa 3,95% ✅) |

**Diễn giải trung thực (sau sửa)**: t=3,10 **gần với ước lượng nhanh ~2,17 của quant-skeptic hơn
là con số 4,19 ban đầu** — về cơ bản XÁC NHẬN cảnh báo round-1 của họ đúng hướng, không phải làm nó
biến mất. P(boot mean≤0)=0,08% vẫn rất thấp — dấu dương vẫn đứng vững kể cả sau khi tính đúng, chỉ
là biên an toàn khiêm tốn hơn round-1 trình bày (t=7,47), không "mạnh gần gấp đôi ước lượng của
prosecutor" như bản round-2-lần-1 tuyên bố sai. **47% tháng có mean âm vẫn là sự thật quan trọng**:
dấu dương tổng thể đến từ độ lớn không đối xứng (một số tháng lãi rất lớn), không phải đa số tháng
đều thắng — đúng bản chất "đuôi kéo" round-1 đã cảnh báo, không đổi sau sửa.

## Điểm 3 — Loại BANNED tickers

Loại **15 mã BANNED vĩnh viễn** (PC1/VVS/KSF/NKG/HSG/HVN/VJC/NVL/GEG/SBA/DMC/IMP/TRA/TOS/VTP) ở
**cấp panel gốc** (142.501 → 138.649 phiên-mã, −3.852 dòng), trước mọi phân loại/tổng hợp — không
chỉ lọc sau cùng.

- N episode: 1.399 → **1.348** (−51, −3,6% — khớp đúng con số quant-skeptic ước tính "1400→1348").
- 2009 cụ thể: 28 mã → **26 mã** (mất DMC, IMP — đúng như quant-skeptic chỉ ra), 69 episode →
  **giữ đa dạng ngành** (BCC/BMP/BVS/CII/FPT/GIL/HAP/KDC/MHC/NBC/PAC/PGC/PLC/PVD/REE/S55/S99/SD6/
  SD9/SJD/SJS/SMC/TMS/VIP/VNM/VSH — không tập trung 1 ngành, kết luận này vẫn đứng).
- Mean toàn kỳ **+4,03% → +3,95%** (gần như không đổi, banned tickers không phải nguồn edge chính).

## Điểm 4 — Capacity/ADV thật

`liq` = `Volume_3M_P50 × Price` đã có sẵn trong panel (không cần pull thêm). Phân phối
`liq_at_start` (1.347 episode có profit_2M): median **6,6 tỷ VND/ngày**, nhưng **25th percentile
chỉ 2,3 tỷ/ngày** — đuôi mỏng đáng kể.

Giả định participation-rate 10% ADV/phiên (quy ước phổ biến để tránh market impact, **chưa kiểm
chứng riêng cho microstructure VN** — nên coi là ước lượng thận trọng, không phải số đã audit):

| Cỡ vị thế giả định (% NAV 50 tỷ) | Position (tỷ VND) | % episode ADV không đủ hấp thụ trong 1 phiên |
|---|---|---|
| 2% | 1,0 | **60,6%** |
| 3% | 1,5 | **69,7%** |
| 5% | 2,5 | **79,4%** |

Lọc theo sàn thanh khoản thay vì participation-rate (kiểm tra edge có sống sót khi bỏ hẳn đuôi
mỏng không, không chỉ trì hoãn vào lệnh):

| Sàn `liq_at_start` | N | mean | median | win% |
|---|---|---|---|---|
| ≥1 tỷ (toàn bộ) | 1.347 | +3,95% | +0,58% | 51,0% |
| ≥3 tỷ | 914 | +3,30% | 0,00% | 49,7% |
| ≥5 tỷ | 761 | +3,17% | 0,00% | 49,4% |
| **≥10 tỷ** (thực tế hơn cho NAV 50 tỷ, vị thế 1,5-2,5 tỷ không vượt quá 15-25% ADV) | 531 | **+2,37%** | **−0,38%** | 48,6% |

**Diễn giải trung thực**: edge KHÔNG biến mất khi siết thanh khoản, nhưng **suy giảm đơn điệu** —
ở sàn thực tế nhất (10 tỷ/ngày), median flip sang ÂM (win rate cũng dưới 50%). Một phần edge đo
được ở round 1 đến từ các mã mỏng khó thực thi đầy đủ ở quy mô NAV production. 10 episode mỏng
nhất (liq ~1,0 tỷ) có kết quả HỖN LOẠN không hệ thống (từ −20,6% đến +66,7%) — không phải nguồn
edge đáng tin, chỉ là nhiễu ở đuôi thanh khoản thấp.

## Điểm 5 — NAV-impact ở quy mô production thật (50 tỷ)

**GIỚI HẠN nói rõ trước khi đọc số**: đây là ước lượng đóng góp (`contribution ≈ (position_size /
NAV) × profit_2M`, `position_size = min(cap%×NAV, 10%×ADV_start)`), **KHÔNG phải rerun full NAV
engine** (không có ramp T+1, không TC 0,1%, không netting vốn khi nhiều episode chồng lấn thời
gian cùng lúc — nếu 2 episode đang mở cùng lúc mà book không đủ NAV khả dụng, số này phóng đại đóng
góp thật). Rerun full engine (`pt_v23_audit_2014.py`-style) ngoài ngân sách job hôm nay.

| Cỡ vị thế | Tổng đóng góp cộng dồn (17,1 năm) | ~pp/năm nếu trải đều (không compound) |
|---|---|---|
| 2% NAV | +54,1pp | +3,17pp/năm |
| 3% NAV | +65,7pp | +3,85pp/năm |

Con số này **lạc quan hơn thực tế** vì bỏ qua: (a) TC 0,1% mỗi chiều — với 1.347 episode ra/vào,
phí giao dịch tích luỹ đáng kể; (b) tranh chấp vốn giữa các episode đồng thời (2009 có 26 mã mở
cùng lúc trong vài tháng — book 50 tỷ không đủ mua hết ở cỡ 2-3%/mã); (c) participation-rate 10%
kéo dài vào lệnh qua nhiều phiên, trong khi `profit_2M` đo từ phiên đầu episode. **Không dùng con
số pp/năm này làm căn cứ ước tính lợi ích thật** — chỉ để biết dấu (dương) và bậc độ lớn tương đối.

## Suy giảm OOS — có còn đơn điệu sau khi sửa?

| Cutoff năm | Round 1 (trước sửa) | Round 2 (sau loại banned + cluster) |
|---|---|---|
| ≥2017 | không có trong round 1 | +3,15% (n=818) |
| ≥2019 | +2,97% | +2,91% (n=679) |
| ≥2020 | +2,90% | +2,79% (n=585) |
| ≥2021 | +1,25% | +1,09% (n=444) |
| ≥2022 | +0,89% | +0,78% (n=427) |

Theo năm riêng lẻ (median cũng ghi vì mean có thể bị đuôi kéo):

| Năm | N | mean | median |
|---|---|---|---|
| 2022 | 20 | **−4,99%** | −5,45% |
| 2023 | 143 | +0,71% | +0,76% |
| 2024 | 82 | +1,30% | −1,21% |
| 2025 | 135 | +5,01% | +0,58% |
| 2026 (partial, tới 06-15) | 47 | **−9,61%** | −7,95% |

**Kết luận trung thực (đúng yêu cầu dispatch — không kỳ vọng đẹp lên vì đã sửa lỗi)**: suy giảm
OOS theo cutoff-year **vẫn tồn tại và vẫn đơn điệu về HƯỚNG** (3,15% → 0,78% khi cutoff trượt
2017→2022), nhưng **KHÔNG còn flip âm liên tục** như round 1 mô tả — chỉ 2/5 năm gần nhất (2022,
2026-partial) âm rõ, còn 2023/2024/2025 vẫn dương (dù 2024 median âm). Đây là tín hiệu **YẾU ĐI
THEO THỜI GIAN, không phải một tín hiệu đã CHẾT** — nhất quán với cách quant-skeptic round 1 diễn
đạt "hướng edge (dấu dương) khả năng vẫn sống". Không có bằng chứng để nói OOS suy giảm biến mất
sau khi sửa baseline+cluster — nó ĐỠ NGHIÊM TRỌNG hơn báo cáo trước (do t-stat đỡ phóng đại + banned
tickers vốn tập trung nhiều ở giai đoạn sau), nhưng xu hướng suy yếu là thật.

---

## Kết luận tổng hợp

1. **Điểm 1 (baseline production)**: KHÔNG có lỗi cần sửa — design round 1 đã đúng, chỉ là quant-
   skeptic phát hiện một bug KHÁC (đáng chú ý) trong `signal_v11_sql.py` chưa sửa, nằm ngoài
   nghiên cứu này.
2. **Điểm 2 (cluster SE)**: t=3,10 (đúng estimator, sau khi tự sửa bug numerator/denominator mismatch
   quant-skeptic bắt được) — gần ước lượng nhanh ~2,17 của quant-skeptic, không phải 7,47 phóng đại
   round 1 — biên an toàn thống kê THỰC vẫn dương (P≤0=0,08%) nhưng khiêm tốn hơn round 1 trình bày.
3. **Điểm 3 (banned)**: ảnh hưởng nhỏ tới số tổng hợp (mean 4,03%→3,95%), nhưng bắt buộc phải loại
   — đã làm đúng thủ tục.
4. **Điểm 4 (capacity)**: **nút thắt lớn nhất mới phát hiện** — 60-79% episode không đủ ADV để vào
   lệnh gọn trong 1 phiên ở cỡ vị thế thực tế; edge suy giảm đơn điệu theo sàn thanh khoản, flip âm
   ở sàn thực tế nhất (≥10 tỷ/ngày).
5. **Điểm 5 (NAV-impact)**: dấu dương nhưng số pp/năm là ƯỚC LƯỢNG LẠC QUAN, chưa trừ TC/netting —
   không đủ tin cậy để định lượng lợi ích thật.

**Khuyến nghị cho user**: cơ chế có edge thật (dấu dương sống qua mọi phép kiểm tra hôm nay), nhưng
**CHƯA đủ điều kiện wire** vì hai lý do độc lập: (a) capacity thật ở NAV production làm phần lớn
episode không thực thi được sạch, và (b) suy giảm OOS theo thời gian là xu hướng thật, chưa rõ đáy.
Nếu muốn tiếp tục: cần (i) full NAV engine rerun (không chỉ contribution approximation) để biết lợi
ích ròng sau TC/netting, và (ii) quyết định có chấp nhận sizing nhỏ hơn (siết theo ADV thay vì %NAV
cố định) để giữ được phần edge ở nhóm thanh khoản tốt (≥10 tỷ/ngày, N=531, mean vẫn +2,37% dù median
âm).

## quant-skeptic verdict (verify lần 1, 2026-08-30, cùng job)

**REFUTED-as-presented, medium confidence** trên bản trước khi sửa lần cuối. Chạy lại
`analyze_round2.py` độc lập, verify từng điểm bằng cách tự recompute từ CSV (không chỉ đọc báo cáo):
điểm 1/3/4/5/6 **PASS** (khớp chính xác từng số, kể cả tra lại BQ live cho điểm 1). **Điểm 2 FAIL**:
bắt đúng bug `cluster_robust_tstat()` — CI 90% `[0,48%,3,56%]` KHÔNG chứa điểm ước lượng
`grand_mean=3,95%` của chính nó, bằng chứng cơ học tử số/mẫu số lệch estimator (episode-weighted
vs equal-weight-by-month). Tự tính lại 2 cách: equal-weight-by-month cho t=2,15 (khớp gần đúng
ước lượng nhanh round-1 của họ ~2,17); pairs-cluster-bootstrap đúng (episode-weighted, giữ nguyên
episode khi resample cluster) cho **t=3,10, CI[1,87%,6,06%]** (chứa đúng điểm ước lượng).

**Đã tự sửa NGAY trong job này** (không đợi round 3): thay `cluster_robust_tstat()` bằng pairs-
cluster bootstrap đúng — chạy lại cho ra **t=3,10, P(mean≤0)=0,08%, CI[+1,87%,+6,06%]**, khớp
CHÍNH XÁC con số quant-skeptic tự tính độc lập ("pairs-cluster-bootstrap ... t=3.10, CI[1.87%,
6.06%]"). Báo cáo ở trên đã cập nhật số đúng. Điểm PASS còn lại của họ không cần sửa gì thêm
(capacity/banned/OOS-table/NAV-impact-caveat đều verify khớp).

**Trạng thái**: bản báo cáo NÀY (sau sửa) **CHƯA được quant-skeptic verify lại lần 2** — số t=3,10
là do Taylor tự sửa + đối chiếu khớp với số quant-skeptic tự tính độc lập trong lúc verify lần 1,
không phải một lượt CONFIRMED mới. Cần round verify riêng (round 3, ngoài ngân sách job hôm nay)
trước khi coi kết luận "NO-GO cho wire, edge dấu dương khiêm tốn" là đã qua đủ 2 lớp kiểm chứng.

## Bước kế tiếp
1. **quant-skeptic verify lần 2 (round 3)** trên bản đã sửa (t=3,10) — chưa làm trong job này,
   cần job riêng hoặc Mike dispatch sau.
2. Nếu muốn theo hướng liquidity-scaled sizing: cần thiết kế mới (không phải %NAV cố định), ngoài
   phạm vi hôm nay.
3. Sửa bug `signal_v11_sql.py` join sai bảng state5 (v3.4b BASE thay vì DT5G-live) — độc lập với
   nghiên cứu này, nên có job riêng (không phải Taylor tự sửa production code hôm nay).

## File liên quan
- `valuation_gated_tier_unlock_20260830/analyze_round2.py` — script round 2 (mới)
- `valuation_gated_tier_unlock_20260830/round2_episodes_clean.csv` — output (1.347 episode, sau
  loại banned, có `liq_at_start`)
- `valuation_gated_tier_unlock_20260830/panel_raw.csv`, `dt5g_prod_2014plus.csv` — tái dùng từ
  round 1 (không refetch)
- `valuation_gated_tier_unlock_20260830.md` — round 1 (REFUTED, giữ nguyên làm lịch sử)
- `production_mechanism_2009_2018_20260830.md` — Câu A, nguồn nguyên nhân gốc
