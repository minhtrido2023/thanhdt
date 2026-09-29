# Cổng fail-safe cơ sở giá luật A tại thời điểm ĐẶT LỆNH — chọn dung sai từ số đo

Job `Taylor_20260815_022340` (việc 1). Dispatch từ Mike sau khi user chốt:
> "Nếu giá ref_price khác giá live phiên giao dịch thực thì fail_safe từ chối thực hiện và
> raise warning lên"

Đây là **CHÍNH SÁCH đóng lỗ hổng THỰC THI**, không phải edge mới. Không có backtest nào ở đây,
không có DSR/PBO (không sinh chuỗi NAV) — nó chỉ bảo đảm luật A đã duyệt thực sự có hiệu lực
lúc đặt lệnh, hoặc lệnh không được đặt.

## 1. Lỗ hổng (quant-skeptic CONFIRMED, killer_objection)

`Executor._limit_price()` tính giá đặt:

```
cap  = ref_price × (1 + chase_pct)      # chase_pct = clamp(2×rvol_20d, 1,5%, 4%)
px   = min(q.ask, cap, hard_no_chase_ceiling_vnd, q.ceiling)
```

`load_plan()` chứng minh được trần **tự nhất quán** với provenance (`anchor × (1+τ)`), nhưng
không biết gì về phiên mà lệnh THỰC SỰ chạy trong đó. Nếu `ref_price`/anchor không còn mô tả
phiên đang chạy thì `cap` tụt xuống dưới cả trần lẫn thị trường: lệnh nằm ở mức không ai chào,
luật A còn nguyên trên giấy nhưng mất tác dụng — **và không có log nào nói điều đó**.

## 2. Chọn MỐC SỐNG: đã BÁC BỎ `q.ref`, dùng `ohlc` phiên đã đóng

Đo thật 2026-08-15, N=66 mã trên feed DNSE sống (`probe_ref_vs_close.py`, dữ liệu thô
`ref_vs_close_probe.json`): `|q.ref (secdef basicPrice) − giá đóng phiên trước| / giá đóng`.

| | |
|---|---|
| khớp TUYỆT ĐỐI (0,000%) | **59/66** |
| median / p95 | 0,000% / 0,488% |
| max | **3,376%** (SCL) |

Bảy ca lệch ≠ 0 **đều là mã biên ±15% (UPCOM)**: SCL −3,376%, TMG +0,949%, TV1 −0,497%,
SGP −0,488%, ACV +0,247%, QNS +0,215%, SSI +0,102%. Nguyên nhân là cấu trúc, không phải sự
kiện: **giá tham chiếu UPCOM là bình quân gia quyền phiên trước, không phải giá đóng** — SCL
08-14 `o=23,0 h=24,0 l=22,4 c=23,7` ⇒ bình quân ~22,9 hoàn toàn hợp lý, không có sự kiện quyền
nào. Mà TV1/DRI/SCL đều đang nằm trong sổ.

⇒ Dùng `q.ref` thì mọi dung sai đủ chặt để bắt plan cũ (≤1%) sẽ **chặn oan sạch UPCOM**, còn
dung sai đủ rộng cho UPCOM (>3,4%) thì **to hơn cả τ=3%** nên vô dụng. **Mốc đúng = giá ĐÓNG
phiên đã hoàn tất, lấy từ DNSE `ohlc` 1D — cùng feed, cùng cơ sở giá với anchor.**

## 3. Dung sai 1,00% — đến từ đâu

**Cận dưới (phải dung nạp):** nhiễu chéo-feed giữa cơ sở anchor (BQ `ticker.Price`) và
`ohlc` DNSE. Đo 29 mã cùng ngày 2026-08-14: **28/29 khớp tới từng đồng**. Ca còn lại là SSI
(BQ 24.500 vs DNSE 19.580, −20%) — không phải nhiễu mà là feed hỏng thật, đúng thứ cổng phải
bắt. Nhiễu cấu trúc còn lại chỉ là độ phân giải 10đ của payload `ohlc`: ≤0,10% ở mã 10.000đ,
≤1,00% ở mã 1.000đ.

**Cận trên (phải nhỏ hơn hẳn):** sai số x% ở cơ sở giá dịch gần 1:1 thành x% dư/thiếu dư địa
đuổi trên ngân sách τ=3% user duyệt. Đối chiếu ngưỡng đã có trong hệ: τ=3%,
`chase_cap_vol_ceil`=4%, `max_chase_pct_buy`=1,5%. **1% là số duy nhất nằm dưới cả ba mà vẫn
trên nhiễu đo được** (=1/3 ngân sách τ; một sai số lọt cổng không bao giờ ăn hết trần đuổi tĩnh).

**Giới hạn đã công bố (không giấu):** plan trễ đúng một phiên mà mã đi <1% qua đêm sẽ LỌT —
nhưng khi ấy sai số trần cũng <1%, tức bị kẹp bởi chính cận trên ở trên. Cổng chặn sai số LỚN,
không hứa phát hiện mọi plan cũ. Khoá bằng test B7.

## 4. Hai phép kiểm

- **C1 — anchor còn đúng phiên**: `|ceiling_anchor_price / live_prev_close − 1| ≤ 1%`.
  So với giá đóng phiên trước chứ **không** so với `q.last`: giá khớp chạy suốt phiên và luật A
  **cho phép** thị trường chạy tới +τ trên anchor — lấy `q.last` làm mốc sẽ chặn oan đúng vùng
  vận hành mà luật A sinh ra để phục vụ.
- **C2 — trần % theo `ref_price` không được âm thầm thay trần A**:
  `ref_price × (1+chase_pct) ≥ min(trần_A, live_prev_close)`. MỘT CHIỀU có chủ đích —
  `ref_price` cao hơn anchor là thiết kế hợp lệ (book DISCRETIONARY_SPECIAL cố ý kéo
  `resting_limit` lên cùng tỉ lệ với trần đúng để tránh cái bẫy này) và vô hại vì trần cứng vẫn
  kẹp phía trên.

Vi phạm ⇒ **không đặt lệnh đó chu kỳ này** (journal `RULE_A_REF_BLOCK`, thử lại chu kỳ sau —
cùng khuôn `HARD_CEILING_BLOCK`/`WAIT_CASH`, KHÔNG raise, KHÔNG giết bot) + **một** event bus
`RULE_A_REF_PRICE_MISMATCH` mỗi (mã, loại lỗi) mỗi lần chạy.

Fail-closed mọi hướng: thiếu `live_prev_close`, `ohlc` lỗi, anchor rác ⇒ CHẶN. Ngoại lệ duy
nhất là broker **không có** client `ohlc` (Sim/PHS/paper) ⇒ bỏ qua cổng — chân paper không đụng
tiền thật và chặn ở đó chỉ làm hỏng đối chứng.

## 5. ĐỀ XUẤT RIÊNG — chưa làm, ngoài phạm vi job này

Đo được trong lúc làm, **không tự wire** (Mike chỉ đạo: thấy mở rộng hợp lý thì đề xuất, đừng
tự làm):

**(a) Trần đuổi % và trần luật A là hai ràng buộc CHỒNG NHAU, và cái nào bind phụ thuộc
`rvol_20d`.** Với `ref_price == anchor` (đúng hình dạng LAG hôm nay: DRI/POW/SCL/SSI plan
08-10 đều có `ref_price == entry_anchor_price` tuyệt đối):

```
cap_chase = anchor × (1 + clamp(2×rvol_20d, 1,5%, 4%))
trần_A    = anchor × 1,03
```

⇒ luật A chỉ THẬT SỰ bind khi `chase_pct ≥ 3%`, tức `rvol_20d ≥ 1,5%/phiên`. Dưới mức đó,
**trần đuổi 1,5% mới là ràng buộc quyết định và τ=3% user duyệt không bao giờ với tới được** —
kể cả khi anchor hoàn toàn đúng. (Đo trên máy này: DRI `chase = 3,33%` ⇒ luật A bind; nhưng đó
là thuộc tính của rvol từng mã từng thời kỳ, không phải bảo đảm.) Đây là câu hỏi CHÍNH SÁCH cần
user quyết, không phải bug: *lệnh mang trần tuyệt đối luật A có nên được miễn trần đuổi % không?*
Cổng C2 ở trên chỉ bắt ca `ref_price` LỆCH; nó **không** và **không nên** tự ý gỡ ràng buộc kia.

**(b) Mở rộng cổng ra mọi lệnh mua** (không chỉ luật A): blast-radius lớn hơn nhiều, ngoài yêu
cầu, cần job riêng.

**(c) `q.last` của SSI đo được 24.500 trong khi `ohlc` 19.580 và `q.ceiling` 20.950** — tức
giá khớp NẰM TRÊN giá trần phiên, bất khả thi trong một phiên. Đây là bất nhất nội tại của quote
DNSE cho SSI, không thuộc phạm vi luật A nhưng đáng cho Winston (data-ops) soi: mọi consumer
đọc `q.last` đều đang tin một con số như vậy.
