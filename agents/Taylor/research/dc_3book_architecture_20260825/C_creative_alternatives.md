# Phần C — Creative alternatives: không bị ràng buộc bởi frame BAL+LAG+DC 3-book

Job `Taylor_20260825_151108`. C1/C2 dùng phép tính số học trên `r_bal`/`r_lag`/`r_dc` đã có từ
Phần A (state-gated park, cùng cửa sổ 2014-08-05→2026-06-19) — không chạy backtest mới. C4 dùng
BQ cache local (`data/bq_cache/ticker/2026.parquet`, ADV 60 phiên gần nhất).

## Gross theo state — bảng nền cho toàn bộ Phần C (r_bal/r_lag/r_dc của tôi, state-gated park)

| State | N | gross_BAL | gross_LAG | gross_DC |
|---|---:|---:|---:|---:|
| CRISIS | 443 | 1.94% | 10.33% | **14.94%** |
| BEAR | 241 | 1.55% | **1.12%** | -7.58% |
| NEUTRAL | 1799 | **32.11%** | 30.24% | 19.40% |
| BULL | 422 | **46.34%** | 34.54% | 43.64% |
| EXBULL | 60 | 60.47% | **69.53%** | 47.85% |

(In đậm = book tốt nhất trong state đó. Lưu ý gross_DC ở đây dùng quy ước state-gated park riêng
của Phần A — thấp hơn số ConvergePort always-park ở Phần B/giai đoạn 1 (43,6% vs 64,1% BULL) vì
đổi quy ước idle-cash; không phải mâu thuẫn, hai số phục vụ 2 câu hỏi khác nhau và cả hai đều đồng
thuận DC vượt LAG trong BULL.)

## C1: Thay LAG bằng DC CHỈ trong BULL (state-conditional activation)

Giữ nguyên tỷ trọng vốn hiện tại (nav_bal_share≈0.44, nav_lag_share≈0.46, số đo từ job `_134238`),
nhưng trong BULL đổi hướng phần LAG sang DC:

```
current  = 0.44×gross_BAL + 0.46×gross_LAG  = 0.44×46.34% + 0.46×34.54% = 36.28%
swapped  = 0.44×gross_BAL + 0.46×gross_DC   = 0.44×46.34% + 0.46×43.64% = 40.46%
delta    = +4.19pp/năm (annualized gross, chỉ tính riêng phiên BULL, N=422)
```

**Kết luận C1: có cải thiện thật nhưng KHIÊM TỐN (+4,19pp), không phải bước nhảy lớn** như back-of-
envelope ban đầu ước tính bằng số ConvergePort always-park (64%/năm) gợi ý. Lý do: dưới quy ước
state-gated (idle cash park NEUTRAL only), gross_DC BULL "chỉ" 43,64% chứ không phải 64% — vẫn hơn
gross_LAG BULL (34,54%) nhưng cách biệt hẹp hơn nhiều so với ước tính ban đầu.

**Đây là hướng ĐÁNG backtest thật nhất** trong toàn bộ Phần C — cả 3 nguồn bằng chứng đều đồng
thuận theo cùng hướng (Phần A: DC thắng LAG ở BULL trong bảng gross-by-state; Phần B: outperform
không phải thuần beta; C1: cộng dồn vào combined gross cho +4,19pp dương). Cần: (a) backtest thật
(không phải suy luận cộng gộp linear) với allocator chuyển đổi w_LAG→w_DC CHỈ khi state=BULL, giữ
nguyên NEUTRAL/CRISIS/BEAR/EXBULL; (b) kiểm tra turnover cost của việc chuyển đổi qua lại mỗi lần
đổi state (BULL↔khác) — chi phí này CHƯA được tính trong phép cộng linear ở trên.

## C2: Thay LAG bằng DC HOÀN TOÀN (2-book BAL+DC, mọi state)

Từ bảng gross theo state ở trên — DC so với LAG:

| State | gross_LAG | gross_DC | Ai thắng |
|---|---:|---:|---|
| CRISIS | 10.33% | 14.94% | DC |
| BEAR | 1.12% | **-7.58%** | LAG (DC ÂM) |
| NEUTRAL | 30.24% | 19.40% | LAG (cách biệt lớn, -10.8pp) |
| BULL | 34.54% | 43.64% | DC |
| EXBULL | 69.53% | 47.85% | LAG (cách biệt lớn, -21.7pp) |

**Kết luận C2: BÁC BỎ — thay LAG bằng DC hoàn toàn ở MỌI state là ý tưởng TỆ.** DC chỉ thắng 2/5
state (CRISIS, BULL); thua rõ rệt ở NEUTRAL (nơi LAG hiện đang mạnh nhất, cách biệt −10,8pp) và
EXBULL (−21,7pp), và **ÂM hẳn ở BEAR (−7,58%/năm)** — một book "luôn-on" mà âm kỳ vọng trong 1
state có N=241 phiên đáng kể là rủi ro thật nếu wire production không có gate BEAR riêng. Đây là
bằng chứng số học trực tiếp xác nhận đúng giả thuyết dispatch đặt ra: "Nếu DC tệ hơn LAG trong
NEUTRAL → không hợp lý thay hoàn toàn, chỉ nên state-conditional (C1)".

## C3: Architecture rethink — hướng đột phá nhất

### C3.1 — State-adaptive factor LEADERSHIP (không phải book cố định, không phải chỉ swap 1 cặp)

Nhìn bảng gross theo state như 1 ma trận factor×regime thay vì 3 book cố định, không có book nào
thắng ở MỌI state:
- **CRISIS**: DC dẫn đầu (14,94%), LAG nhì (10,33%), BAL gần như phẳng (1,94%) — earnings-drift
  + quality-value làm việc, momentum (BAL) không có gì để bắt (giá đang rơi, chưa có xu hướng).
- **BEAR**: chỉ LAG dương nhẹ (1,12%); BAL phẳng (1,55%), DC ÂM (−7,58%) — không book nào đáng
  nặng vốn, đây là state cần PHÒNG THỦ (cash/parking), không phải chọn book nào "thắng".
- **NEUTRAL**: BAL dẫn đầu sát nút LAG (32,11% vs 30,24%) — 2 factor đồng thuận, đúng lý do V2.4
  chạy song song ở state này.
- **BULL**: BAL dẫn đầu, DC nhì sát (46,34% vs 43,64%), LAG rớt lại (34,54%) — đúng phát hiện C1.
- **EXBULL**: LAG dẫn đầu bất ngờ (69,53%, N=60 nhỏ), BAL nhì (60,47%), DC yếu nhất (47,85%).

**Đề xuất**: thay vì "V2.4 = BAL+LAG cố định, thêm/bớt book thứ 3" — nghĩ theo hướng **factor
rotation theo state** (weight 3 factor thay đổi CHỦ ĐỘNG theo DT5G, không chỉ w_lag_tgt 1 tham số
như hiện tại): BULL nghiêng BAL+DC (giảm LAG), NEUTRAL giữ BAL+LAG cân bằng (như hiện tại, đã đúng),
CRISIS nghiêng DC+LAG (giảm BAL — đang gần như vô dụng ở CRISIS), BEAR giảm cả 3 về phòng thủ/cash
thật (không phải chọn "book tốt nhất trong 3 cái tệ"), EXBULL giữ nguyên LAG+BAL (DC không cần ở
đây, N nhỏ nên không chắc chắn). Đây là kiến trúc **tổng quát hơn** ý tưởng "book thứ 3 cố định
1/3" — nó biến DC từ 1 book riêng thành 1 THÀNH PHẦN của ma trận phân bổ theo state, đúng tinh
thần "V2.4 tiến hoá" thay vì chỉ chồng thêm 1 sleeve.

⚠️ **Cảnh báo tự phê bình cần thiết**: bảng trên là ĐIỂM ƯỚC LƯỢNG (point estimate) từ 1 lần chạy,
KHÔNG qua DSR/PBO, N ở CRISIS/EXBULL (443/60) mỏng hơn NEUTRAL/BULL nhiều — đặc biệt LAG EXBULL
69,53% dựa trên chỉ 60 phiên, dễ bị 1-2 sự kiện outlier chi phối. Trước khi coi ma trận này là căn
cứ thiết kế thật, cần tối thiểu: (a) bootstrap CI cho từng ô, (b) walk-forward xem ma trận có ổn
định IS vs OOS không (chỉ mới validate BULL ở đây), (c) quant-skeptic pass.

### C3.2 — LAG overhaul trong BULL bằng signal khác (conceptual, chưa backtest)

Dispatch gợi ý: PEAD/SUE-based LAG khan signal trong BULL không phải vì book kém mà vì tín hiệu
quá phụ thuộc BCTC (chỉ cập nhật theo quý, độ trễ tự nhiên). Ý tưởng thay bằng tín hiệu earnings-
momentum "forward-looking" hơn trong BULL cụ thể (ví dụ: analyst revision, guidance signal) —
**về mặt lý thuyết tài chính VN hợp lý** (thị trường VN thiếu coverage phân tích rộng, revision
signal có thể vẫn underexploited), nhưng **rủi ro thực thi lớn hơn nhiều so với C1**: (a) chưa có
nguồn dữ liệu revision/guidance nào được xác nhận trong `bigquery_dictionary.json` hiện tại — cần
tìm/mua nguồn mới, ngoài phạm vi BQ đang dùng; (b) C1 (route sang DC) dùng data ĐÃ CÓ SẴN và ĐÃ ĐO
được hiệu ứng dương — chi phí biên để thử C1 thấp hơn hẳn so với xây tín hiệu earnings-revision từ
đầu. **Xếp hạng: đáng ghi lại làm hướng dài hạn, không phải ưu tiên ngắn hạn.**

### C3.3 — Single unified book (complexity reduction)

Câu hỏi: có 1 signal nào đủ tốt ở MỌI state để thay 3 book? **Trả lời bằng chính bảng gross ở
trên: KHÔNG.** Không book nào (BAL/LAG/DC) đứng đầu ở ≥4/5 state — BAL đầu 2/5 (NEUTRAL, BULL),
LAG đầu 2/5 (BEAR, EXBULL), DC đầu 1/5 (CRISIS). Đây là bằng chứng trực tiếp phản đối hướng "gộp
về 1 signal" — sự đa dạng factor (momentum/PEAD/quality-value) đang thật sự bổ trợ nhau theo
regime, không phải dư thừa. **Kết luận: KHÔNG theo hướng này** — giữ đa-factor, chỉ tinh chỉnh
trọng số theo state (C3.1) mới là hướng đúng.

## C4: Capacity check — 4 mã Securities ở quy mô 1/3 NAV

ADV 60 phiên gần nhất (tính từ `data/bq_cache/ticker/2026.parquet`, Close×Volume thực, KHÔNG giả
định), so với vị thế tối đa 1 tên nếu w_DC=1/3 NAV @100B = 33 tỷ, cap 0,20/tên → **6,6 tỷ VND/tên**:

| Ticker | Sector | ADV 60d (tỷ VND) | Vị thế max (6,6 tỷ) / ADV |
|---|---|---:|---:|
| FPT | Tech | 548.9 | 1.2% |
| TCB | Banking | 404.9 | 1.6% |
| ACB | Banking | 398.2 | 1.7% |
| SSI | Securities | 374.1 | 1.8% |
| HDB | Banking | 271.6 | 2.4% |
| MBB | Banking | 256.4 | 2.6% |
| VCB | Banking | 254.1 | 2.6% |
| VND | Securities | 252.5 | 2.6% |
| VCI | Securities | 183.5 | 3.6% |
| HCM | Securities | 119.4 | 5.5% |
| PVT | Logistics | 63.8 | 10.4% |
| HAH | Logistics | 31.7 | 20.8% |
| DBC | Livestock | 27.1 | 24.3% |
| CTR | Viettel-infra | 22.4 | 29.5% |
| MSH | Textile | 3.2 | **204.9%** |
| DHG | Pharma | 0.7 | **890.4%** |

**Kết luận C4**: **4 mã Securities (câu hỏi dispatch hỏi cụ thể) đều AN TOÀN** — SSI/VND/VCI/HCM
chỉ chiếm 1,8-5,5% ADV cho 1 vị thế full-cap, không phải mối lo capacity ở quy mô 1/3 NAV @100B.
Cả nhóm Banking + FPT cũng an toàn (≤2,6%).

**NHƯNG phát hiện thêm ngoài phạm vi câu hỏi gốc**: **DHG (890% ADV) và MSH (205% ADV) là vấn đề
capacity NGHIÊM TRỌNG** nếu double-confirm gate active đúng lúc 2 tên này — 1 vị thế full-cap
(6,6 tỷ) sẽ không thể build/unwind trong nhiều phiên mà không đẩy giá mạnh. Đây khớp với chính
docstring cũ của `dc_book_waterfall_paper.py` ("standalone-sleeve capacity ~10-15B ex-DHG" — đã tự
loại trừ DHG). CTR/DBC/HAH ở mức biên (20-30% ADV) — chấp nhận được nếu ramp 3 phiên theo quy ước
T+1 (CLAUDE.md) nhưng không nên full-cap trong 1 phiên.

**Hành động cần nếu đi tiếp**: nếu wire DC làm book có vốn thật ở quy mô 1/3 NAV, cần thêm
capacity cap RIÊNG cho DHG/MSH (vd exclude khỏi active set ở quy mô này, hoặc trần vị thế thấp hơn
0,20 mặc định cho 2 tên này cụ thể) — không dùng cap 0,20 đồng nhất cho toàn bộ 16 tên.
