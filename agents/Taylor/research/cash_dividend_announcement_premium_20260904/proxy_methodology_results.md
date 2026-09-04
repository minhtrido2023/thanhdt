# Cash Dividend Pre-Ex-Date Premium — Proxy Methodology (ex_date anchor)

**Job**: `Taylor_20260904_094347` · **Ngày**: 2026-09-04
**Verdict: NO-GO — hiệu ứng đo được KHÔNG phân biệt được với "cổ tức cổ phiếu" (negative control), tức KHÔNG đặc thù cho thông tin cổ tức TIỀN MẶT.**

Sprint trước (`Taylor_20260904_092935`) BLOCKED vì `announcement_date` PIT không tồn tại trên BQ.
Sprint này dùng đúng proxy user đề xuất — neo vào `exright_date` (ổn định, KHÔNG bị upsert-ghi-đè
như `public_date`, theo `corporate_action_bq.md`) — nên **chạy được** toàn bộ pipeline. Kết luận là
NO-GO trên bằng chứng thống kê thật, không phải BLOCKED lần nữa.

## Prereg (commit trước khi nhìn outcome)

- H1: median ABNORMAL_RETURN nhóm CASH > 0 (Wilcoxon vs 0)
- H2: Spearman(yield_ratio, ABNORMAL_RETURN) > 0, p<0.05
- H3: median AR(H) > median AR(L) (Mann-Whitney)
- H_neg: STOCK_DIV không có premium tương tự — nếu có = momentum chung, không phải cash effect
- **FAIL nếu**: H2 rớt OOS, HOẶC STOCK_DIV có premium tương tự CASH (không phân biệt được cash effect)

## Methodology

- PRE_EX = [ex_date−14d, ex_date−1d]; BASELINE = [ex_date−28d, ex_date−15d]
- ABNORMAL_RETURN = (Close[ex−1]/Close[ex−14] − 1) − (Close[ex−15]/Close[ex−28] − 1) − (VNINDEX[ex−1]/VNINDEX[ex−14] − 1)
- Giá tại mỗi mốc = trading day gần nhất **≤** mốc, trong cửa sổ đệm 15 ngày lịch (đủ phủ nghỉ Tết)
- yield_ratio = (div_vnd / Close[ex−14]) / 0.068 (deposit rate Big4-12M, theo KB)
- Nhóm H (>1.0) / M (0.5–1.0) / L (<0.5); STOCK_DIV = negative control
- **Lệch có chủ đích so với dispatch**: `div_vnd` lấy TRỰC TIẾP từ `corporate_action.DIV.value_per_share`
  (đồng/cp GỘP, 100% populated, CANONICAL theo `corporate_action_bq.md` "Cách dùng hiệu quả" #2),
  KHÔNG suy từ tỉ lệ Close/Price như dispatch gợi ý — trực tiếp hơn và tránh nguyên bẫy Close/Price
  (§21) hoàn toàn. GROUP BY (ticker, ex_date) và SUM value_per_share khi có ≥2 dòng cùng ex-date
  (2,6% sự kiện DIV) — coi là tổng tiền mặt/cp thị trường nhận được cùng ngày, không tách rõ từng
  dòng theo `event_title_vi` (chấp nhận đơn giản hoá vì tỉ lệ trùng thấp).

## Data

- Nguồn: `tav2_bq.corporate_action` (DIV executed, `value_per_share>0`, `exright_date` 2010-01-01→2026-06-01)
  + `tav2_bq.ticker` (Close, VNINDEX mirror column)
- STOCK_DIV control: `event_code=ISS`, `issue_method_name_vi='Trả Cổ tức bằng Cổ phiếu'`, executed
- Loại 8 sự kiện CASH có giá 0 (lỗi dữ liệu mã thanh khoản cực mỏng: BMN/BTG/BTU/HAN/NBW/PIS/SWC/UDJ)
  và 544 sự kiện thiếu ≥1 mốc giá (không có trading day trong cửa sổ đệm)

## Kết quả — full sample (N_eff = số event ticker×ex_date, theo đúng note dispatch)

| Test | N | Kết quả | p |
|---|---:|---|---|
| H1 (CASH median AR vs 0) | 10.876 | median = **+0,232%**, dương | 1,08e-05 |
| H2 (Spearman yield_ratio↔AR) | 10.876 | rho = **0,097** (yếu nhưng dương) | 6,27e-24 |
| H3 (H vs L, MWU) | H=6.586 / L=1.648 | median H=+0,716% > L=−1,120% | 4,24e-19 |
| H_neg (STOCK_DIV vs 0) | 1.535 | median = +0,210% | **0,296 (không có ý nghĩa)** |
| **CASH vs STOCK_DIV trực tiếp (MWU)** | 10.876 vs 1.535 | CASH median 0,232% ≈ STOCK_DIV median 0,210% | **p=0,276 — KHÔNG phân biệt được** |

**H1/H2/H3 nhìn riêng lẻ đều "confirm"** (p rất nhỏ, N lớn) — nhưng đây chính xác là bẫy tiêu
chí FAIL đã prereg: khi so trực tiếp CASH với STOCK_DIV, **không phân biệt được về mặt thống kê**
(p=0,276), và độ lớn hiệu ứng gần như bằng nhau (0,232% vs 0,210%). Cổ tức cổ phiếu **không mang
thông tin cash-flow** nào cho cổ đông (chỉ chia nhỏ cổ phần), nên nếu nó cũng có "premium" tương tự
trong đúng cửa sổ đo, hiệu ứng nhiều khả năng là **drift chung quanh MỌI sự kiện corporate action
sắp treo** (kỳ vọng tích cực chung, hiệu ứng lịch/mùa vụ, hoặc thiên lệch lựa chọn công ty có tin
tốt sắp công bố) — không đặc thù cho **thông tin cổ tức tiền mặt**.

## Robustness — cluster theo ticker (chống 1 mã cổ tức đều đặn lấn át N)

Mỗi ticker chỉ đóng góp 1 quan sát (median AR/yield_ratio của chính nó qua các năm) — CASH
1.076 mã, STOCK_DIV 511 mã:

| Test | N (mã) | Kết quả | p |
|---|---:|---|---|
| H1 | 1.076 | median AR = +0,29% | 0,0082 (còn ý nghĩa, yếu hơn) |
| H2 | 1.076 | rho = 0,082 | 0,0074 (còn ý nghĩa, yếu hơn) |
| CASH vs STOCK_DIV | 1.076 vs 511 | **STOCK_DIV median (0,44%) CAO HƠN CASH (0,29%)** | 0,479 (không phân biệt được, càng rõ hơn) |

Ở mức cluster-theo-mã, negative control STOCK_DIV còn có median AR **cao hơn** CASH — củng cố
thêm kết luận NO-GO, không phải nhiễu do N lớn ở mức event.

## OOS check (2020+)

H1/H2/H3 đều còn ý nghĩa OOS (H N=1.994, L N=1.237, đủ sức thống kê) — **không phải lý do FAIL**,
nhưng FAIL criterion thứ hai (STOCK_DIV indistinguishable) đã đủ để kết luận NO-GO trên toàn mẫu,
nên không cần chẻ IS/OOS cho phép so sánh CASH-vs-STOCK_DIV riêng (N STOCK_DIV OOS sẽ mỏng hơn).

## Selfcheck

- Tái tạo thủ công SAB/REE/DGC/VNM: giá + div_vnd + yield_ratio đều trong khoảng hợp lý (vd SAB
  2018-01-15: div=3.500đ, Close[ex-14]=84.890đ → yield_ratio=0,61, khớp trực giác cổ tức SAB thấp
  hơn lãi suất tiết kiệm giai đoạn đó).
- N_eff tính đúng theo yêu cầu: (ticker, ex_date) là 1 quan sát — 1.076 mã × trung bình ~10 sự
  kiện/mã trải nhiều năm, không đếm gộp theo mã.
- 0 VND: không có model dự đoán nào được train, chỉ đo thống kê mô tả — không áp dụng.
- Đã phát hiện + sửa 1 bug thao tác trong lúc làm: `ROW_NUMBER() OVER()` không `ORDER BY` trong CTE
  `ev` là non-deterministic trên BigQuery khi CTE bị tham chiếu 2 lần trong cùng query → làm lệch
  khớp event↔giá hoàn toàn (vd sự kiện ex_date=2014 khớp nhầm giá năm 2022). Sửa bằng khóa string
  ổn định `CONCAT(ticker,'|',ex_date,'|',grp)`. Bài học: tránh `ROW_NUMBER() OVER()` không thứ tự
  làm khóa nối khi CTE có thể bị BigQuery re-evaluate.

## Kết luận

**NO-GO.** "Cash dividend announcement premium" đo qua proxy pre-ex-date window **không phân biệt
được** với hiệu ứng tương tự ở cổ tức cổ phiếu (negative control không mang cash-flow information).
Dose-response nội bộ trong nhóm CASH (yield_ratio càng cao, AR càng dương — H2/H3) vẫn sống sót
qua cluster-robust check, nhưng đây **không đủ để kết luận có "cash dividend announcement premium"
thật** — vì không có negative control tương đương để loại trừ khả năng đây là hiệu ứng value/mean-
reversion thông thường (mã yield cao thường là mã giá thấp/PE thấp, có thể tự có drift dương không
liên quan gì đến cổ tức). Không đề xuất wire vào production.

**Không cần quant-skeptic verify thêm** — verdict là NO-GO tự thân dựa trên đúng tiêu chí FAIL đã
prereg, không phải một claim GO cần kiểm chứng đối kháng.
