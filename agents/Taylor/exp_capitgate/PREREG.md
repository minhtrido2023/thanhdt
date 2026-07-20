# PRE-REGISTRATION — nới quality gate của CAPIT basket (job Taylor_20260720_160852)
Viết TRƯỚC khi chạy bất kỳ test nào có dính forward-return. Chuẩn multiple-testing 2026-07-05.

## Câu hỏi
Ràng buộc thật của CAPIT không phải metric xếp hạng (đã NO-GO 2 lần với DCF) mà là **pool quá mỏng**:
median 7 tên/phiên; 9/14 washout event có pool ≤ K=5 → lấy trọn pool, không chọn được gì.
Nới quality gate có mở được pool mà KHÔNG rước value-trap không?

## Vì sao value-trap là câu hỏi cốt lõi (không phải return trung bình)
CAPIT hold **60 phiên, stop-exempt** — không có cơ chế thoát sớm. Một tên "rẻ theo pb_z" nhưng
suy yếu cấu trúc sẽ bị giữ trọn 60 phiên. Nên tiêu chí quyết định phải nặng về **đuôi trái**
(P(ret ≤ −20%), 5th-pct, mean worst-decile), không chỉ trung bình.

## Mức nới — neo theo PHÂN PHỐI THỰC TẾ (đo trước, không dính return)
Universe thanh khoản (ADV≥2B, 2014-2026, 551.673 name-day, 3.127 phiên):
| biến | p50 | p60 | p70 | p75 | p80 | ngưỡng baseline |
|---|---|---|---|---|---|---|
| ROE_Min5Y | 0,055 | 0,073 | 0,096 | 0,110 | 0,126 | **0,12 ≈ p79** |
| ROIC5Y | 0,073 | 0,089 | 0,115 | 0,131 | 0,151 | **0,10 ≈ p65** |
| FSCORE | 5 | 6 | 6 | 6 | 6 | **6 ≈ p70** |
| ADV (tỷ) trong nhóm quality-pass | 8,1 | | | 32,3 (p75) | | **2 ≈ p25 nhóm quality-pass** |

## N_TRIALS PRE-REGISTERED = 6 biến thể gate
| id | mô tả | ROE_Min5Y | ROIC5Y | FSCORE | ADV |
|---|---|---|---|---|---|
| **G0** | baseline production | ≥0,12 | ≥0,10 | ≥6 | ≥2B |
| G1 | nới ROE 1 nấc (p79→p70) | ≥0,09 | ≥0,10 | ≥6 | ≥2B |
| G2 | nới ROIC 1 nấc (p65→p55) | ≥0,12 | ≥0,08 | ≥6 | ≥2B |
| G3 | nới FSCORE 1 nấc (p70→p60) | ≥0,12 | ≥0,10 | ≥5 | ≥2B |
| G4 | nới thanh khoản | ≥0,12 | ≥0,10 | ≥6 | ≥1B |
| G5 | COMBO-mild (3 trục chất lượng, mỗi trục 1 nấc) | ≥0,09 | ≥0,08 | ≥5 | ≥2B |
| G6 | COMBO-p50 (neo trung vị — biên trên của việc nới) | ≥0,055 | ≥0,073 | ≥5 | ≥2B |

Horizon quyết định duy nhất = **h=60** (đúng holding period CAPIT). h=250 là robustness, không phải trial mới.

## Thiết kế test
### Panel A (test chính — có power): name-level MARGINAL vs CORE
- Ngày quan sát: đầu mỗi tháng 2014-2026; suy diễn chính trên **quarterly non-overlapping** (≥60 phiên).
- Với mỗi biến thể Gk: **MARGINAL** = tên qua Gk nhưng trượt G0; **CORE** = tên qua G0.
- Return **demeaned trong ngày** (bỏ market timing) → so MARGINAL vs CORE.
- Suy diễn: t-stat trên chuỗi hiệu-theo-ngày (N ngày độc lập); + cluster bootstrap theo khối NĂM.
- Vì CAPIT chỉ mua tên RẺ: bản chính giới hạn quan sát ở **pb_z < 0** (điều kiện production thật).
  Bản không lọc pb_z = robustness.

### Panel B: pool-size / event structure (mô tả, không thống kê)
Với mỗi Gk, đếm tại 14 washout event: pool size, bao nhiêu event có pool > K=5
(tức nới gate có TẠO RA lựa chọn thật không).

### Panel C: portfolio-level 14 event (tham khảo định hướng — N=14 KHÔNG đủ power)
Rank giữ **pb_z** (đã confirm không dùng DCF), K=5, equal-weight, h=60/250.

## TIÊU CHÍ GO / NO-GO (định trước)
Một biến thể Gk **GO-candidate (paper-first)** cần ĐỦ CẢ 4:
- (i) **Mở pool thật**: số event có pool > K tăng ≥ 3 so với G0 (5/14 → ≥8/14).
- (ii) **Không xấu đuôi trái**: P(ret60 ≤ −20%) của MARGINAL không cao hơn CORE quá **+5pp**,
  VÀ 5th-pct của MARGINAL không thấp hơn CORE quá **10pp**.
- (iii) **Trung bình không thua có ý nghĩa**: hiệu demeaned MARGINAL−CORE có **t > −2,0**
  (tức không có bằng chứng thống kê rằng tên mới tệ hơn). Không đòi hỏi tên mới TỐT HƠN —
  mục tiêu là mở pool an toàn, không phải tìm alpha.
- (iv) **Ổn định**: LOO theo năm không đảo kết luận (ii)/(iii); IS 2014-19 và OOS 2020+ cùng dấu ở (iii).

**NO-GO** nếu (i) trượt (nới cho có, không mở được lựa chọn) HOẶC (ii) trượt (rước value-trap).
**INCONCLUSIVE** nếu (i)+(ii) đạt nhưng (iii)/(iv) mập mờ.

## DSR
Chỉ báo **nếu** có biến thể đạt (i)+(ii)+(iii)+(iv) VÀ kết luận không do 1 năm chi phối.
Trượt → nói rõ không báo và tại sao (như 2 job trước), không báo số trang trí.

## Ràng buộc
- Point-in-time: đọc `ticker_prune` tại đúng ngày quan sát (cột tài chính đã join theo Release_Date).
- threads=1; stable-sort tie-break `(metric, ticker)`.
- R&D thuần: **KHÔNG sửa `capit_basket()`**, không chạm plan/executor.
