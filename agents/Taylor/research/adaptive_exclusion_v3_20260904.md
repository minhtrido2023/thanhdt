# Adaptive exclusion — vòng 3: đóng 2 lỗ hổng quant-skeptic REFUTED

Job `Taylor_20260904_075525` (dispatch Mike), tiếp `Taylor_20260904_054209`. Bản trước:
[`adaptive_exclusion_architecture_20260904.md`](adaptive_exclusion_architecture_20260904.md) (v1),
[`adaptive_exclusion_v2_20260904.md`](adaptive_exclusion_v2_20260904.md) (v2). **Verdict quant-skeptic
lần 1: REFUTED** (`logs/verify_20260904_073326_2594281.log`) — lý do KHÔNG phải kiến trúc sai, mà
bằng chứng an toàn VÒNG TRÒN: ngưỡng (dilution 80% khớp đúng ca BAF 84%, Debt_Eq>3,5 percentile toàn
mẫu biết trước tên đã nổ) được chọn SAU khi biết mã nào nổ, rồi must-catch validate bằng CHÍNH các
mã đó. 3 điểm skeptic xác nhận ĐÚNG (giữ nguyên, không làm lại): forensic_flags date=2026-06-20
zero-effect (guard forward-only `custom_basket.py:307-315`); tái lập độc lập 67,7% false-positive +
821 dòng EBITDA rule; chuyển IntCov→EBITDA justified bất kể ngữ nghĩa. Artifact: `adaptive_exclusion_20260904/v3/`.

## 2 câu trả lời trực tiếp (đọc trước)

1. **Công thức thật của `IntCov_P0`: mẫu số là một khoản RÒNG có thể đảo dấu, nhưng KHÔNG tái lập
   được chính xác từ `ticker_financial`** (không có cột chi phí/doanh thu tài chính riêng). Bằng
   chứng mới, ở QUY MÔ UNIVERSE (không chỉ SBA): trong nhóm đòn bẩy cao + `IntCov_P0<0` là NET
   DEBTOR (91,9%, không phải net-cash-rich), **82,9% vẫn có EBIT ước tính dương** và **68,1% có cả
   EBIT lẫn NP cùng dương** — về toán học, điều này CHỈ khả thi nếu mẫu số âm, xác nhận lại kết luận
   v2 (mẫu số RÒNG). Nhưng proxy bảng cân đối đơn giản (`Cash_P0+LtInvest_P0` so `StDebt_P0+LtDebt_P0`)
   giải thích được RẤT YẾU (R²=0,25, khớp dấu chỉ 53% — gần tung đồng xu) — khoản "doanh thu tài
   chính" thật nhiều khả năng đến từ DÒNG CHẢY (lãi JV/liên kết, FX, lãi bán đầu tư một lần) chứ
   không phải tồn kho tiền cuối kỳ. **Luật tiền xử lý dấu đã ghi vào
   `kb/data_registry/fundamentals/ticker_financial.md`** (đọc trước khi dùng `IntCov_P0` ở bất kỳ
   rule mới nào): âm một mình KHÔNG đủ; phải đi kèm `EBITDA_P0<0` hoặc `NP_P0<0`.
2. **Gate với ngưỡng chọn IS-only (blind, ≤2019-12-31, KHÔNG nhìn 16 mã) — CHƯA đủ bằng chứng để
   CONFIRM.** Recall trên 35 sự kiện độc lập (BVPS chuyển âm lần đầu, 2020+, loại sạch 16 mã BANNED)
   = 100% nhưng phần lớn (34,3%) chỉ bắt được CÙNG QUÝ sự kiện xảy ra (tautological — rule1 chính
   là định nghĩa event), chỉ 65,7% có cảnh báo SỚM thật (rule2/rule3 bắn trước). **False-positive
   rate = 91,9%** (185 mã bị gắn cờ từ 2020, chỉ 15 mã/8,1% thật sự đi tới sự kiện nguy hiểm trong
   2 năm). **OOS 2020+ backtest: MaxDD của gate blind (E) = −40,5%, TỆ HƠN CẢ không lọc gì (A,
   −40,0%)** — và tệ hơn gate hindsight-tuned (D, −38,6%) 1,9pp, đúng như quant-skeptic tiên đoán
   nếu D bị overfit. **Ca cụ thể lộ rõ nhất: BAF.** Ngưỡng blind (dilution>175%, percentile-95 IS)
   KHÔNG bắt được đúng đợt pha loãng 84% (2022Q3) từng dùng để hiệu chỉnh ngưỡng cũ 80% — gate chỉ
   kích hoạt 21 THÁNG sau (2024-07-30, khi một đợt pha loãng khác đẩy tỷ lệ lên 206%), tức là ở
   NGÀY QUYẾT ĐỊNH THẬT (2023-11-06, ngày `custom30V` chọn BAF) gate blind sẽ hành xử Y HỆT không
   lọc gì. **DSR trên excess-return OOS (E so A) = 0,1426, RED FLAG rõ ràng (<0,95)** — giá trị
   tăng thêm từ gate blind KHÔNG phân biệt được với nhiễu, N_TRIALS=7 (v1=5+v2=1+v3=1). **Kết luận
   trung thực: KHÔNG CONFIRM được — gate động chưa đủ tốt để thay thế BANNED tĩnh mà không mất an
   toàn thật; giữ nguyên phần bảo vệ nào đó (BANNED tĩnh hoặc must-catch thủ công) cho tới khi có
   thiết kế khác vượt qua được test blind này.**

---

## Việc 1 — Truy công thức `IntCov_P0` bằng dữ liệu thật

### 1a. Không có cột chi phí/doanh thu tài chính trong `ticker_financial`

Quét TOÀN BỘ 100 cột của `tav2_bq.ticker_financial` qua `INFORMATION_SCHEMA.COLUMNS` (không chỉ
những cột có trong `bigquery_dictionary.json` — kiểm tra kỹ theo đúng yêu cầu dispatch): không có
cột nào tên `FinExpense`/`FinIncome`/`InterestExpense`/tương đương. Cột liên quan gần nhất chỉ có
`StDebt_P0`, `LtDebt_P0` (dư nợ có lãi, KHÔNG phải chi phí lãi), `EBITM_P0`/`EBITDA_P0`/`NP_P0`
(lợi nhuận, không phải chi phí tài chính), `Cash_P0`/`LtInvest_P0` (tồn kho tiền/đầu tư CUỐI KỲ,
không phải doanh thu tài chính trong kỳ). **Kết luận: không thể tái lập công thức chính xác từ
bảng này — mọi phân tích dưới đây là suy luận gián tiếp qua phương trình ngược, không phải xác
nhận trực tiếp.** (Đúng như dispatch mục (c) dự trù.)

⚠️ **Sửa 1 lỗi kỹ thuật của quant-skeptic khi tự tái lập** (phát hiện khi đối chiếu số):
`EBITM_P0` **đã là số THẬP PHÂN (fraction)**, không phải "số nguyên phần trăm cần chia 100" —
kiểm tra phân phối toàn universe (`v3/solve_intcov_formula.py`): median=0,0545 (5,45%), p75=0,133
(13,3%) — biên độ đúng của một tỷ suất EBIT margin thực tế. Verify log của quant-skeptic dùng
`EBIT_est = EBITM_P0/100 × Revenue_P0` (chia thêm 100 lần nữa) — với SBA 2013Q1 ra `EBIT_est=
7,83e7`, NHỎ HƠN CẢ `NP_P0=2,18e9` tới 28 lần (vô lý — EBIT luôn ≥ hoặc gần NP thông thường). Công
thức đúng `EBIT_est = EBITM_P0 × Revenue_P0` cho `7,83e9`, nằm ĐÚNG giữa `NP_P0` (2,18e9) và
`EBITDA_P0` (112,6e9) — hợp lý về bậc độ lớn. Sai số này KHÔNG đổi kết luận định tính của
quant-skeptic (EBIT vẫn dương, mẫu số vẫn phải âm) nhưng đổi TOÀN BỘ magnitude — cần sửa trước khi
dùng `EBIT_est` cho bất kỳ phân tích định lượng nào khác.

### 1b. Kiểm bằng phương trình ngược, quy mô UNIVERSE (không chỉ SBA/HVN)

`implied_denom = EBIT_est / IntCov_P0`, tính trên 37.246 dòng (2010→2026, `|IntCov_P0|>0,05` để
tránh vùng chia gần-0 bất ổn). Test giả thuyết: mẫu số ròng ≈ f(nợ vay − tiền/đầu tư tài chính).

**Kết quả — giả thuyết "ròng = nợ − tiền mặt/đầu tư cuối kỳ" bị BÁC BỎ ở quy mô universe:**
- Tương quan `implied_denom` với `NetDebt` (=`StDebt+LtDebt-Cash-LtInvest`): r=0,204 — YẾU.
- Tỷ lệ khớp DẤU giữa `implied_denom` và `NetDebt`: **53,0%** (n=37.246) — gần bằng tung đồng xu
  (55,4% nếu so với `TotalDebt` gộp, cũng không tốt hơn đáng kể).
- OLS `implied_denom ~ b1·StDebt+b2·LtDebt+b3·Cash+b4·LtInvest` (không hệ số chặn): R²=0,2488 —
  giải thích được chưa tới 1/4 phương sai.

**Nhưng — kiểm trực tiếp trên đúng tập nghi vấn (không dựa vào NetDebt proxy) xác nhận mẫu số PHẢI
RÒNG:** lọc đúng tập mà luật gate CŨ sẽ gắn cờ (`Debt_Eq_P0>3,5 AND IntCov_P0<1,5`, n=3.437),
tách theo dấu `IntCov_P0`:

| nhóm | n | Đặc điểm |
|---|---:|---|
| `IntCov_P0<0` | 2.147 | 71,3% có `NP_P0>0`, 78,1% có `EBITDA_P0>0` |
| trong đó: net-debtor (`NetDebt>0`, đa số — **91,9%**) | 1.971 | **82,9% có `EBIT_est>0`**, **68,1% có CẢ `EBIT_est>0` và `NP_P0>0`** |
| trong đó: net-cash-rich (`NetDebt<0`) | 176 (8,1%) | — |
| `0<=IntCov_P0<1,5` | 1.290 | 61,4% có `NP_P0>0` |

68,1% của nhóm net-debtor (đa số áp đảo, KHÔNG PHẢI thiểu số net-cash-rich như giả thuyết ban đầu
suy từ SBA) có ĐỒNG THỜI EBIT ước tính dương VÀ IntCov âm — về mặt toán học `sign(denom) =
sign(EBIT)×sign(IntCov)`, nên mẫu số của nhóm này PHẢI âm dù công ty là net-debtor trên bảng cân
đối. Điều này XÁC NHẬN lại kết luận định tính của v2 (mẫu số là khoản RÒNG có thể đảo dấu, không
phải "lãi vay gộp luôn dương") nhưng **BÁC BỎ giả thuyết cơ chế cụ thể** ("net-cash-rich → tiền
gửi sinh lãi → mẫu số âm") mà chỉ đúng cho 8,1% ca. Cơ chế thật (không xác nhận được từ bảng này)
nhiều khả năng là khoản "doanh thu tài chính" DẠNG DÒNG CHẢY trong kỳ (lãi từ công ty liên
doanh/liên kết, lãi chênh lệch tỷ giá, lãi bán khoản đầu tư một lần) — các khoản này KHÔNG để lại
dấu vết trên `Cash_P0`/`LtInvest_P0` cuối kỳ nếu công ty không giữ lại tiền mặt sau khi ghi nhận.

### 1c. Luật tiền xử lý dấu (ghi vào `kb/data_registry/fundamentals/ticker_financial.md`)

Đã ghi thành mục dùng lại được — tóm tắt:
- `IntCov_P0<0` một mình → KHÔNG suy ra distress; chỉ tin khi đi kèm `EBITDA_P0<0` hoặc `NP_P0<0`.
- `0<=IntCov_P0<1,5` → vẫn 61,4% false-positive (NP dương) trong tập kiểm — đối chiếu thêm, đừng
  dùng một mình.
- `|IntCov_P0|` gần 0 (~<0,05) → vùng chia bất ổn định, coi low-confidence, không lọc trực tiếp.
- Gate nghiên cứu hiện tại (v2, chưa wire) đã ĐÚNG theo nguyên tắc này (dùng `EBITDA_P0<0` thay
  `IntCov_P0<1,5`) — không cần sửa thêm code, chỉ cần tài liệu hoá lý do.

**Độ tin cậy: mẫu số là khoản RÒNG — CAO (2 bằng chứng độc lập, SBA + universe-scale 68,1%). Cơ chế
CỤ THỂ tạo ra khoản ròng đó (net-cash proxy) — KHÔNG xác nhận được (R²=0,25). Nếu cần chắc chắn
tuyệt đối, phải hỏi bq_admin/nguồn ETL, không tiếp tục suy diễn.**

---

## Việc 2 — Ngưỡng IS-only + kiểm chứng OOS trên tên ngoài 16 mã

### Bước 2.1 — Chọn ngưỡng CHỈ bằng dữ liệu ≤2019-12-31, không nhìn 16 mã

Tiêu chí khai TRƯỚC (`v3/thresholds_is_only.json`, timestamp `2026-09-04T08:01:02Z`, ghi trước khi
chạy bất kỳ backtest/recall nào): **"ngưỡng = percentile 95 của phân phối metric trên universe IS
(≤2019-12-31)"** — quy ước thống kê chuẩn "đuôi 5% cực đoan nhất", độc lập tên mã. N_TRIALS bước
này = 1 (percentile 90 tính SONG SONG làm robustness, không phải thử-rồi-chọn lại).

| Ngưỡng | IS-only (p95, dùng chính) | IS-only (p90, robustness) | Hindsight-tuned cũ (v1/v2) |
|---|---:|---:|---:|
| `Debt_Eq_P0` | **5,90** | 3,90 | 3,50 |
| dilution 12Q | **175%** | 110% | 80% (khớp đúng ca BAF 84%) |

Ngưỡng blind LỎNG HƠN đáng kể so với ngưỡng hindsight-tuned (Debt_Eq 5,9 vs 3,5; dilution 175% vs
80%) — bằng chứng gián tiếp đầu tiên rằng bộ ngưỡng cũ đã được "siết" chặt hơn mức một quy tắc
thống kê trung lập sẽ chọn, hướng về đúng vài ca đã biết.

### Bước 2.2 — Tập kiểm chứng độc lập: 35 sự kiện, KHÔNG chứa 16 mã BANNED

Tiêu chí khách quan: **`BVPS` chuyển ÂM LẦN ĐẦU**, 2020+, loại sạch 16 mã BANNED thật (verify lại
bằng grep code `lag_forensic_filter.py:90-91` — đúng 16 tên gồm cả BAF, không phải 15 như liệt kê
gộp trong `CLAUDE.md`). Kết quả: **35 sự kiện** (`v3/independent_event_set_bvps_turn_negative.csv`),
0 trùng tên với 16 mã BANNED — đây là tập kiểm chứng "sạch", gate chưa từng được tinh chỉnh theo.

**Recall — gate IS-only (rule2/rule3, KHÔNG tính rule1 vì rule1=`BVPS<=0` trùng chính định nghĩa
event, gắn cờ cùng lúc là tautological chứ không phải dự báo):**

| Loại bắt | n | % |
|---|---:|---:|
| SỚM thật (rule2/rule3 bắn TRƯỚC quý event) | 23 | 65,7% |
| CÙNG QUÝ (chỉ rule1 bắn đúng lúc BVPS đã âm — không phải dự báo) | 12 | 34,3% |
| BỎ LỌT hoàn toàn | 0 | 0% |
| **Recall tổng (bắt được trước khi hết quý event)** | 35 | **100%** |

Trong nhóm SỚM, lead time trung vị = 456 ngày, nhưng phân phối RẤT lệch (có ca 5.473 ngày = công
ty bị flag liên tục 15 năm — dấu hiệu "luôn xấu" hơn là "cảnh báo sớm có ý nghĩa"; xem
`v3/recall_leadtime_results.csv` để soi từng ca).

**False-positive rate — bằng chứng quan trọng nhất:** trong số **185 mã** bị gắn cờ bởi rule2/rule3
từ 2020 (loại 16 mã BANNED), chỉ **15 mã (8,1%)** thật sự đi tới một sự kiện BVPS-âm trong vòng 2
năm sau khi bị gắn cờ. **False-positive rate = 91,9%** (`v3/flagged_tickers_fp_check.csv`) — nếu
dùng gate này để loại khỏi rổ chọn cổ phiếu, ta sẽ loại nhầm ~12 mã lành mạnh cho mỗi 1 mã thật sự
nguy hiểm bắt được.

### Bước 2.3 — Backtest OOS 2020+, ngưỡng IS-only (Scenario E) so A/B/C/D

| Scenario | CAGR FULL | Sharpe | MaxDD | Calmar | CAGR IS | CAGR OOS |
|---|---:|---:|---:|---:|---:|---:|
| A — không lọc gì | 32,07% | 1,29 | −40,0% | 0,80 | 24,12% | 39,69% |
| B — BANNED-16 tĩnh | 31,41% | 1,29 | −40,2% | 0,78 | 22,77% | 39,83% |
| D — gate hindsight-tuned (v2, Debt_Eq>3,5/dilution>80%) | 30,20% | 1,30 | −38,6% | 0,78 | 18,56% | 41,91% |
| **E — gate IS-only blind (v3, Debt_Eq>5,9/dilution>175%)** | **30,74%** | **1,28** | **−40,5%** | **0,76** | **21,26%** | **40,09%** |

**E TỆ HƠN D ở MaxDD (−40,5% vs −38,6%, chênh 1,9pp) và TỆ HƠN CẢ A (−40,0%, không lọc gì!)** —
đây chính là bằng chứng đo được cho việc "nếu ngưỡng IS-only cho kết quả tệ hơn D, đó là bằng
chứng D đã overfit" mà dispatch yêu cầu nói thẳng. D đạt MaxDD tốt hơn CHÍNH VÌ nó được tinh chỉnh
bằng cách biết trước BAF/HVN sẽ nổ ở đâu; một ngưỡng blind — dù cùng kiến trúc gate — không tái
lập được lợi ích đó, và thậm chí drawdown còn kém hơn cả việc không lọc gì.

**Ca cụ thể lộ cơ chế thất bại — BAF:** must-catch case gốc là ngày **2023-11-06** (ngày
`custom30V` thật sự CHỌN BAF vào rổ, theo v1 §1b). Với ngưỡng blind (dilution>175%), đợt pha loãng
84% xảy ra 2022Q3 (`eff_date=2022-10-31`) — đúng ca dùng để hiệu chỉnh ngưỡng 80% cũ — **KHÔNG đủ
để vượt ngưỡng 175%**, dilution_pct giữ nguyên 84% suốt 2022Q3→2024Q1 (7 quý liên tiếp KHÔNG bị
gắn cờ). Gate blind chỉ kích hoạt ở **2024-07-30** (21 tháng SAU ngày quyết định 2023-11-06), khi
MỘT đợt pha loãng KHÁC đẩy tỷ lệ lên 206%. **Tại đúng thời điểm quyết định thật (2023-11-06), gate
blind sẽ hành xử Y HỆT scenario A (không lọc BAF)** — must-catch case gốc, nếu kiểm đúng ngày quyết
định thay vì "có bắt được cuối cùng không", là một **MISS**, không phải catch.

### Bước 2.4 — DSR trên excess-return OOS (E so A)

N_TRIALS tích luỹ cả 3 vòng = **7** (v1: 5 biến thể kiến trúc gate ban đầu + v2: 1 (rule2
IntCov→EBITDA) + v3: 1 (tiêu chí percentile-95-IS-only)). Dưới 8 biến thể nên KHÔNG cần chạy PBO
theo đúng ngưỡng dispatch đặt ra.

- Chuỗi excess-return hàng ngày OOS (E−A, n=1.606 phiên chung, `v3/step6_dsr.py`,
  hàm `dsr`/`expected_max_sr`/`moments` tái dùng nguyên từ `dsr_pbo_annex.py` đã có sẵn trong repo).
- Per-obs SR_hat = 0,00808 (annualized ~0,128) — RẤT nhỏ.
- SR0 (kỳ vọng SR tối đa dưới giả thuyết H0 không có skill, N=7 trials) = 0,0346.
- **DSR = P(true SR > SR0) = 0,1426 — RED FLAG (<0,95).**

Giá trị tăng thêm của gate blind so với không lọc gì (Sharpe OOS A=1,412 vs E=1,424, chênh không
đáng kể) **không phân biệt được với nhiễu thống kê** một khi đã tính đến số lần thử đã tích luỹ.

---

## Kết luận tổng hợp — CHƯA CONFIRM, không phải một CONFIRMED gượng ép

Đúng tinh thần dispatch cho phép: **kết quả ở đây là ÂM, và nó có giá trị.** Việc chọn ngưỡng theo
quy tắc thống kê trung lập (percentile-95 IS-only, không nhìn tên mã) giải quyết ĐƯỢC vấn đề vòng
tròn logic (ngưỡng không còn được chọn để khớp ca đã biết) — nhưng khi kiểm tra thật (trên 35 sự
kiện độc lập + OOS backtest + DSR), gate với ngưỡng đó:
- Có recall lý thuyết 100% nhưng phần lớn (34,3%) chỉ là bắt đồng thời với chính định nghĩa
  nguy hiểm (không phải cảnh báo sớm).
- False-positive rate 91,9% — chi phí cơ hội rất lớn nếu dùng để loại cổ phiếu.
- OOS MaxDD tệ hơn CẢ không lọc gì.
- Miss đúng must-catch case gốc (BAF) TẠI THỜI ĐIỂM QUYẾT ĐỊNH THẬT.
- DSR=0,1426, RED FLAG rõ ràng.

**Khuyến nghị: KHÔNG wire gate động (dù v1/v2/v3) thay thế BANNED tĩnh ở vòng này.** Giữ nguyên
hiện trạng (BANNED rỗng theo quyết định user đã chốt ở v2, dựa trên lý do khác — "xấu thì tự loại"
qua rating≤3 + gate rating tổng thể — KHÔNG dựa trên tuyên bố "gate động thay được BANNED an toàn",
tuyên bố đó vẫn REFUTED) hoặc — nếu muốn một lớp bảo vệ chủ động — cần thiết kế khác (không chỉ đổi
ngưỡng) đã vượt qua được đúng bộ test blind này (recall sớm >>65,7%, false-positive rate thấp hơn
nhiều <91,9%, DSR≥0,95) trước khi coi là an toàn. Việc 1 (IntCov formula) đã đóng — ghi vào
`kb/data_registry/` để không ai lặp lại nhầm lẫn sign-convention. Việc 2 CHƯA đóng.

## Giới hạn

- Tập kiểm chứng độc lập (35 sự kiện) chỉ dùng 1 tiêu chí (BVPS turn negative) — dispatch cho phép
  1-2 tiêu chí, KHÔNG kịp làm tiêu chí thứ 2 (drawdown≥70%/không hồi 50% trong 2 năm) trong ngân
  sách effort của job này; nếu tiêu chí thứ 2 cho kết quả khác đáng kể, cần chạy thêm.
- PC1 vẫn KHÔNG bị bắt bởi bất kỳ biến thể gate nào (đã biết từ v1/v2, không đổi) — gian lận sạch
  trên số, ngoài phạm vi giải quyết được bằng gate tài chính.
- `implied_denom` (Việc 1) dùng `EBIT_est` (từ `EBITM_P0×Revenue_P0`) làm proxy — bản thân
  `EBITM_P0` có outlier cực đoan (min=−5.749, khả năng lỗi dữ liệu ở vài dòng) nên R²=0,25 của
  Phần D có thể MỘT PHẦN do nhiễu ở tử số, không chỉ do proxy mẫu số sai — chưa tách được 2 nguồn
  nhiễu này trong ngân sách job.
- DSR dùng xấp xỉ `var_sr=1/T` (đơn giản hoá BLdP đã có sẵn trong `dsr_pbo_annex.py`, không tự
  phát minh công thức mới) — đúng quy ước đã dùng cho V2.4, nhất quán với registry.
- Chưa tính lại chi phí PC1 bằng trọng số thật (namecap mcap-weighted, không phải 1/30) như
  quant-skeptic đề xuất trong `recommended_reruns` — ngoài phạm vi 2 việc dispatch yêu cầu lần này,
  để ngỏ cho vòng sau nếu cần.
- Toàn bộ backtest tới `AUDIT_END=2026-06-15` (khớp cache); dữ liệu BQ trực tiếp cho Việc 1/2 tới
  `2026-08-21` (theo pull mới `v3/universe_financials_v3_intcov.csv`, KHÔNG qua cache).

## Phụ lục — file nguồn v3

`mike/agents/Taylor/research/adaptive_exclusion_20260904/v3/`: `universe_financials_v3_intcov.csv`
(BQ pull mới, thêm `EBITM_P0/Revenue_P0/StDebt_P0/LtDebt_P0/Cash_P0/LtInvest_P0` so với v2),
`solve_intcov_formula.py` (Việc 1, Phần A-D), `thresholds_is_only.json` (Bước 2.1, timestamp
frozen), `step2_independent_event_set.py` + `independent_event_set_bvps_turn_negative.csv` (Bước
2.2, 35 sự kiện), `step3_gate_recall_leadtime.py` + `recall_leadtime_results.csv` +
`flagged_tickers_fp_check.csv` (recall/lead-time/false-positive), `step4_build_episodes_is_only.py`
+ `dynamic_exclude_events_v3_is_only.csv` (episode PIT gate ngưỡng blind), `step5_scenario_e_backtest.py`
+ `scenarioE_metrics.csv` + `cache/nav_scenarioE.csv` (Scenario E), `step6_dsr.py` (Bước 2.4, DSR
tái dùng `dsr_pbo_annex.py`).
