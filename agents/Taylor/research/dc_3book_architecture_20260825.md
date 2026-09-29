# Kiến trúc 3-book V2.4: BAL + LAG + DC (Alpha Lens), mỗi book 1/3 NAV

Job: `Taylor_20260825_145251` (dispatch Mike, 2026-08-25). Nghiên cứu — KHÔNG implement code mới,
KHÔNG ghi đè CSV canonical.

## Bối cảnh nhanh

Hướng B (route LAG idle cash → parking trong BULL) đã NO-GO (CAGR +0.1pp, DD -2-3pp xấu hơn,
Calmar 1.63→1.41 — beta tăng đúng đỉnh cycle). User muốn thử DC (Double-Confirm: sector-lens BUY
∩ 8L rating ≤2) làm book thứ 3 khai thác LAG idle cash trong BULL.

**Phát hiện nền tảng đầu tiên, quan trọng cho toàn bộ phần sau**: cơ chế DC hiện tại
(`dc_book_waterfall_paper.py`) là **NEUTRAL-ONLY theo thiết kế**, không phải một book độc lập:

```python
def compute_waterfall_targets(state, dc_set, basket, liq=None, ...):
    if state != NEUTRAL:
        return {}, False, "not-NEUTRAL → sleeve flat (waterfall is a NEUTRAL-only mechanism)", {}
```

Nó chỉ lấp tiền dư SAU BAL/LAG trong trạng thái NEUTRAL, KHÔNG BAO GIỜ deploy trong BULL. Vì vậy
câu hỏi "DC có signal trong BULL không" **không thể trả lời trực tiếp bằng data paper hiện có** —
paper trial chưa từng chạy 1 phiên BULL nào. Xử lý: Q1 trả lời bằng absence-of-data + lý do kiến
trúc; Q4 dùng backtest độc lập khác (`converge_portfolio_backtest.py`, full 2014-2026, ALWAYS-ON,
không gate NEUTRAL) làm proxy tốt nhất hiện có.

## Q1: DC sleeve có signal trong BULL không?

**Không đọc được trực tiếp — 2 nguồn kiểm tra đều xác nhận không có TX/paper day nào ở BULL:**

1. CSV production `v23_golive_audit_...park3-80...F1_t80_univpit.csv`: cột `book` trong
   `record_type=TX` chỉ có giá trị `{LAG, BAL}` (7.310 + 2.681 dòng) — **không có `book=DC`**.
   Đúng như dispatch dự đoán: DC hiện chỉ là waterfall paper, chưa phải book trong allocator.
2. `data/dc_book_waterfall_paper_nav.csv` (v2, live từ 2026-07-20): **27 phiên, TẤT CẢ đều
   `state_name=NEUTRAL`** (07-17 → 08-24 — đúng giai đoạn thị trường VN đang NEUTRAL). 0 phiên
   BULL/EXBULL. Cum P&L sleeve tích luỹ hiện tại: **+0,79%** trên 27 phiên (không đủ N để kết
   luận gì về BULL).

→ Câu hỏi gốc "DC có bổ sung alpha trong BULL" **chỉ trả lời được bằng backtest độc lập, không
phải bằng theo dõi paper hiện tại**. Chuyển sang Q4.

## Q2: Overlap DC với BAL và LAG

**Universe của DC bị giới hạn cứng vào 1 watchlist 16 mã** (`sector_lens_monitor.NAMES`), không
phải toàn bộ `ticker_prune` như BAL/LAG:

| Sector | Mã |
|---|---|
| Banking (5) | MBB, ACB, HDB, TCB, VCB |
| Securities (4) | SSI, VCI, VND, HCM |
| Tech (1) | FPT |
| Logistics (2) | PVT, HAH |
| Khác (4) | CTR (Viettel-infra), MSH (Textile), DHG (Pharma), DBC (Livestock) |

**56% (9/16) là Banking+Securities** — DC về bản chất là 1 lens tài chính-VN đậm đặc, không phải
1 screen rộng.

**Overlap thực đo (buy-side, `book=BAL`/`book=LAG` từ CSV production, 2023-01-01→2026-06-19, loại
`CUSTOM_*` basket order), so với 7 tên DC đang live hôm nay (ACB, FPT, HAH, MBB, PVT, SSI, TCB):**

| Book | N buy | Unique tickers | Overlap với 7 tên DC |
|---|---:|---:|---|
| BAL | 684 | 141 | **MBB×1, SSI×1** |
| LAG | 1.649 | 294 | **SSI×2** |

Overlap gần như bằng 0 theo số lệnh — nhưng đây là so với set DC **hôm nay** (1 điểm thời gian),
không phải set DC lịch sử (không tái tạo membership lịch sử của DC ở đây — ngoài phạm vi "không
implement code mới"). Đọc kèm với top-10 tên BAL/LAG hay mua (D2D, KSF, RAL, PLC, MML — small-cap;
SCL, NT2, CTS, DDV, SZC — mid-cap): **overlap thấp có tính CẤU TRÚC**, không phải trùng hợp — BAL
(momentum SIGNAL_V11 + yieldcombo) và LAG (PEAD/SUE) chọn theo tín hiệu định lượng trên toàn
universe, tự nhiên nghiêng về small/mid-cap (nơi mispricing lớn hơn); DC chỉ BAO GIỜ chọn trong 16
blue-chip đã sector-lens curate sẵn, nên 2 tập hợp gần như rời nhau theo thiết kế.

**Ghi chú chéo-book (không phải BAL/LAG nhưng đáng lưu ý)**: PVT hiện vừa nằm trong DC book
(ACB/FPT/HAH/MBB/PVT/SSI/TCB) VỪA nằm trong CAPIT book của SpaceX hôm nay (PVT 3.500cp — plan
2026-08-26). Không phải vấn đề cho câu hỏi này (CAPIT là sleeve khác, không phải BAL/LAG) nhưng
nếu triển khai DC làm book riêng cần rà lại việc double-count PVT giữa 2 sleeve.

**Kết luận Q2**: overlap DC↔BAL và DC↔LAG THẤP, có tính cấu trúc (khác universe nguồn). DC **có
khả năng bổ sung**, không chỉ là BAL diluted.

## Q3: Backtest 3-book thật (w_BAL=w_LAG=w_DC=1/3, cash dư → park NEUTRAL @0.80)

**KHÔNG chạy được** — đúng như dispatch cảnh báo trước:
- Allocator V2.4 hiện tại (`book` trong CSV production) chỉ biết `{BAL, LAG}`; không có code path
  gán w_DC hay tích hợp DC vào combined_nav.
- `dc_book_waterfall_paper.py` là 1 sleeve NEUTRAL-only cộng thêm VÀO phần cash dư của
  BAL/LAG — kiến trúc khác hẳn "book độc lập 1/3 NAV chạy mọi state" mà dispatch mô tả.
- Ràng buộc "KHÔNG implement code mới nếu chưa có" của dispatch này loại trừ việc viết 1 allocator
  3-book mới ngay trong job này.

→ Chuyển sang Q4 (upper-bound bằng dữ liệu/backtest đã có sẵn).

## Q4: Upper-bound estimate — dùng `converge_portfolio_backtest.py`

Tìm được 1 backtest ĐỘC LẬP đã có sẵn, đúng khái niệm DC (double-confirm = sector-lens BUY ∩ 8L
≤2) nhưng chạy **ALWAYS-ON mọi state** (không gate NEUTRAL) suốt **2014-08 → 2026-06** — đây là
proxy tốt nhất hiện có cho "DC là 1 book độc lập, không chỉ chạy trong NEUTRAL". Cơ chế: layer 1 =
double-confirm active book (cap 0,20/tên, tilt 1,5x nếu STRONG), layer 2 = phần dư park vào
custom30V (baseline = 100% custom30V thuần — đúng đối chứng "không có DC"). T+1 execution, TC đã
trừ, walk-forward IS(2014-19)/OOS(2020+) đã ghi sẵn trong docstring gốc (Taylor_20260706_093329,
approved 2026-07-06).

Join với `vnindex_5state_dt5g_live.parquet` (cache local, fresh tới 2026-08-24) để tách gross theo
state — cùng phương pháp `gross_by_state` vừa dùng cho LAG (job _134238, 2026-08-25).

### Gross theo state (annualized mean daily return, ×252)

**Full sample 2014-2026:**

| State | N phiên | baseline (100% park) | ConvergePort equal-weight | ConvergePort tilt-STRONG |
|---|---:|---:|---:|---:|
| CRISIS | 443 | +4,77% | **+7,48%** | +7,90% |
| BEAR | 241 | −20,48% | **−16,82%** | −16,68% |
| NEUTRAL | 1.804 | +21,00% | +22,83% | +22,70% |
| BULL | 422 | +45,34% | **+64,12%** | +63,56% |
| (EXBULL loại theo yêu cầu dispatch) | 60 | +83,55% | +57,92% | +57,92% |

**OOS 2020+ (loại survivorship của giai đoạn calibrate IS):**

| State | N phiên | baseline | ConvergePort equal-weight |
|---|---:|---:|---:|
| CRISIS | 297 | +15,60% | **+17,63%** |
| BEAR | 194 | −22,55% | **−19,50%** |
| NEUTRAL | 713 | +26,25% | +30,13% |
| BULL | 352 | +46,50% | **+68,94%** |

**Trả lời trực tiếp câu hỏi dispatch — DC hoạt động TỐT HƠN trong BULL, không phải NEUTRAL, cả
IS lẫn OOS, N đủ lớn (BULL: 422 phiên full / 352 phiên OOS).** Chênh lệch BULL full-sample là
+18,8pp/năm so với baseline — lớn hơn hẳn chênh lệch ở NEUTRAL (+1,8pp) hay ở BEAR/CRISIS
(vài pp). Đây LÀ hiện tượng "thị trường đã re-rate = nhóm quality có sẵn nhiều hơn" mà dispatch
giả thuyết — nhưng có 1 cách đọc khác an toàn hơn (xem caveat #2 dưới).

### Metrics tổng hợp (portfolio-level, không phải chỉ leg DC)

| | CAGR | Sharpe | MaxDD | Calmar |
|---|---:|---:|---:|---:|
| baseline (100% custom30V) FULL | 18,75% | 0,88 | −45,9% | 0,41 |
| ConvergePort eq-weight FULL | **23,86%** | **1,12** | −46,1% | 0,52 |
| baseline OOS 2020+ | 24,03% | 0,99 | −45,7% | 0,53 |
| ConvergePort eq-weight OOS | **32,54%** | **1,31** | **−40,6%** | **0,80** |

MaxDD không xấu đi (thậm chí nhẹ hơn ở OOS) trong khi CAGR/Sharpe/Calmar đều cải thiện rõ — khác
hẳn hướng B (LAG→park trong BULL, DD xấu đi 2-3pp). Cơ chế khác nhau: hướng B THÊM beta (đổ thêm
tiền vào equity đúng đỉnh cycle); DC ở đây là THAY THẾ (swap 1 phần custom30V bằng double-confirm
book cùng mức exposure, không tăng tổng beta).

### 4 caveat bắt buộc đọc trước khi coi đây là bằng chứng đủ để wire production

1. **Đây là so sánh DC-độc-lập-thay-thế-parking, KHÔNG PHẢI backtest 3-book thật (Q3 chưa chạy
   được).** Chưa biết tương tác với allocator w_BAL/w_LAG band ±10pp, ADV cap, CAPIT lever khi có
   cả 3 book cùng lúc tranh phần NAV.
2. **Outperformance BULL có thể là BETA ngành, không phải alpha chọn mã.** Universe DC 56%
   Banking+Securities — 2 ngành có beta cao với cycle tín dụng VN, tự nhiên re-rate mạnh hơn
   VNINDEX broad trong BULL. Cần tách bằng 1 kiểm định factor-neutral (vd so DC với 1 rổ
   Banking+Securities cap-weight thuần, không double-confirm) trước khi gọi đây là "alpha" — job
   này CHƯA làm được (đúng ràng buộc không implement code mới).
3. **Correlation DC-like với V2.4 (BAL+LAG combined) = 0,626 — GẦN BẰNG correlation V2.4 với
   chính parking basket (0,643).** Nghĩa là DC KHÔNG bổ sung diversification nhiều hơn những gì
   custom30V parking đã cho sẵn — giá trị chính của nó là NÂNG RETURN trong BULL, không phải giảm
   rủi ro danh mục tổng.
4. **Capacity chưa verify ở quy mô 1/3 NAV.** Docstring `dc_book_waterfall_paper.py` tự ghi
   "standalone-sleeve capacity ~10-15B ex-DHG" cho vai trò waterfall (phần dư nhỏ). Universe 16
   mã có 4 mã Securities (SSI/VCI/VND/HCM) — ADV các mã này biến động mạnh theo phiên thanh khoản
   thị trường chứng khoán, cần check ADV riêng nếu scale lên 1/3 NAV thật của SpaceX/ZaloPay.

## Ghi chú thêm — DSR/PBO chưa chạy

Đây là ước lượng upper-bound theo đúng khung Q4 dispatch yêu cầu (redirect vì Q3 không chạy
được), KHÔNG PHẢI 1 backtest sẵn sàng lên `data/results_registry.md`. Backtest `ConvergePort`
gốc đã tự khai walk-forward IS/OOS + self-check 0 leak + T+1 (docstring, approved 2026-07-06) —
nhưng KHÔNG có DSR/PBO/quant-skeptic pass cho khung "book độc lập" này (khác với khung "waterfall
NEUTRAL-only" đã approve). Nếu đi tiếp theo hướng GO, bước kế tiếp phải qua đủ pipeline
`quant-research` skill (§18 coding_guidelines) trước khi đề xuất wire.

## Recommendation: **GO** (có điều kiện — đề xuất backtest 3-book đầy đủ, chưa wire production)

Bằng chứng đủ mạnh để đi tiếp:
- DC (dạng always-on, proxy `ConvergePort`) outperform parking basket rõ rệt trong BULL cả
  IS(2014-19 nằm trong full-sample) lẫn OOS(2020+), N lớn (352-422 phiên), không đánh đổi DD.
- Overlap với BAL/LAG thấp có tính cấu trúc (universe khác nhau hẳn) → không phải BAL diluted.
- Kiến trúc hiện tại (NEUTRAL-only waterfall) đang bỏ phí đúng phần alpha lớn nhất (BULL).

Nhưng CHƯA đủ để coi là quyết định cuối — cần đúng 3 việc trước khi wire:
1. Backtest 3-book THẬT (Q3): tích hợp `converge_portfolio_backtest.py`'s double-confirm logic
   vào allocator V2.4 (golive audit machinery), w_DC=1/3 chạy song song w_BAL/w_LAG, so với
   baseline park=0.80 hiện tại trên `combined_nav` — không phải so DC đơn lẻ với parking.
2. Factor-neutral check (caveat #2): tách xem BULL outperformance là alpha double-confirm hay
   beta Banking+Securities thuần.
3. Capacity check 4 mã Securities ở quy mô 1/3 NAV thật + quant-skeptic pass trước khi đề xuất
   flip flag `dc_book_waterfall_enabled` sang scope rộng hơn NEUTRAL-only.

**KHÔNG phải NO-GO** (khác hẳn hướng B) — cơ chế THAY THẾ (không thêm beta) khác căn bản với cơ
chế THÊM (hướng B), và dữ liệu ủng hộ rõ ràng hơn nhiều.
