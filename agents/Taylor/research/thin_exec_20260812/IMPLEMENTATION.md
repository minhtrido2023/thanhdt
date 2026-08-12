# P1 + P2 + P5 — BẢN CÀI ĐẶT (code thật, paper-gated, MẶC ĐỊNH TẮT)

> Job `Taylor_20260812_095213` · 2026-08-12 · Taylor
> Nghiên cứu gốc: `README.md` cùng thư mục (job `Taylor_20260812_091343`). File này KHÔNG
> lặp lại nghiên cứu — chỉ ghi **đã sửa gì, cờ nào, mặc định gì, verify ra sao, còn rủi ro gì**.
>
> **TRẠNG THÁI: CHƯA COMMIT, CHƯA BẬT.** Cả 3 phần đều để uncommitted trong working tree.
> P1 và P2 mặc định **TẮT** ⇒ hành vi production hôm nay **không đổi một byte**. P5 chỉ THÊM
> log. Bật paper/production là quyết định của Mike/user **sau** khi có quant-skeptic verify —
> đúng thứ tự đã dùng cho HYBRID 08-10 (verify TRƯỚC, apply SAU).

---

## 0. TL;DR

| | Việc | File sửa | Cờ bật | Mặc định | Selfcheck |
|---|---|---|---|---|---|
| **P1** | Trần no-chase động `anchor×(1+τ)`, τ=3%, anchor = TB 5 phiên | `trading_bot/discretionary_accumulation.py`, `mike/bin/discretionary_accumulation_inject.py` | `state["dynamic_ceiling"]["enabled"]` **VÀ** `price_band.max_no_chase_ceiling` | **TẮT** (thiếu 1 trong 2 ⇒ trần cố định) | `dynamic_no_chase_ceiling_selfcheck.py` — **49/49** |
| **P2** | Mẫu số pacing `max(cum_vol, ADV20×f(t))` + clamp ≤50% tape | `trading_bot/executor.py`, `trading_bot/config.py` | `expected_volume_pacing_enabled` | **`False`** | `expected_volume_pacing_selfcheck.py` — **39/39** |
| **P5** | Ghi 10 mức giá chờ vào `dnse_raw_<date>.jsonl` | `trading_bot/brokers.py` | không có cờ (logging thuần) | bật, throttle 60s/mã | `quote_l2_logging_selfcheck.py` — **44/44** |

**Quét rộng §23 (executor.py = module lõi): 17 selfcheck, 13 xanh / 4 đỏ — cả 4 ca đỏ ĐÃ ĐỎ
SẴN trên code sạch, không phải do P1/P2/P5.** Nguyên nhân đã truy tận gốc và chứng minh bằng
thí nghiệm, không phải phỏng đoán — xem §4. Đó là một phát hiện phụ **cần xử lý riêng**.

---

## 1. P1 — trần no-chase động

### Sửa gì
`resolve_price_band(state, anchor_prices, latest_price) → (ceiling, resting, info)` mới trong
`discretionary_accumulation.py`; `compute_session_order()` gọi nó thay cho việc đọc thẳng
`band["no_chase_ceiling"]`. `mike/bin/discretionary_accumulation_inject.py` thêm
`anchor_prices_for()` lấy giá 5 phiên đã đóng từ **DNSE `/price/ohlc` 1D** (cùng feed với giá
đặt lệnh — không lẫn cơ sở giá `Close` đã điều chỉnh của BQ, đúng
`kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`).

Khi trần động ăn: `ceiling = min(mean(5 phiên)×(1+τ), max_no_chase_ceiling)`.

### Hai điều KHÔNG hiển nhiên, đã xử lý

**(a) `resting_limit` phải được kéo theo cùng tỉ lệ — nếu không, P1 gần như vô hiệu.**
Executor tính giá đặt là `cap = ref_price×(1+chase%)` **rồi mới** `min` với trần cứng. Nâng
riêng trần cứng mà để `resting_limit` (= `ref_price`) đứng yên thì `ref×(1+chase%)` trở thành
ràng buộc buộc — và `chase` là **động** (`clamp(2×rvol_20d, 1,5%, 4%)`, đo thật TV1 ⇒ 3,06%),
nên phần lớn lợi ích bốc hơi. Band giữ nguyên **hình dạng** (`resting/ceiling`), chỉ đổi **mức**.

**(b) Trần động BẮT BUỘC có cận trên tuyệt đối do user duyệt.** `price_band.max_no_chase_ceiling`
là điều kiện bật thứ hai, không phải tuỳ chọn. Không có nó, anchor trôi lên trong vài tháng có
thể đưa giá mua vượt xa mức user từng đồng ý mà không ai phải bấm nút — biến một luật thực thi
thành một quyết định chính sách ngầm. Thiếu ⇒ fail-safe về band cố định.

### Fail-safe — mọi đường đều đóng
Cờ tắt · thiếu `max_no_chase_ceiling` · `τ` ngoài `(0; 0,10]` · `sessions` ngoài `[1;20]` ·
thiếu/không đủ giá anchor · anchor lệch >2× hoặc <0,5× giá mới nhất (nghi **sai đơn vị** —
nghìn đồng vs VND, lỗi đã cắn thật trong chính nghiên cứu này) · DNSE ohlc lỗi/thiếu phiên ·
band cố định ≤0 · trần/resting tính ra ≤0 · `resting > ceiling` ⇒ **tất cả trả về band cố định**.
**Không có nhánh nào fail-OPEN.**

### §24 — KHÔNG đụng lưới an toàn cuối
`_limit_price`/guard cuối trong `executor.py` **giữ nguyên tuyệt đối**. P1 chỉ đổi **giá trị**
plan generator ghi vào `hard_no_chase_ceiling_vnd`; cơ chế cưỡng chế vẫn đúng như §24 đã chốt.
Ca F3/F5 của selfcheck chứng minh: giá đặt không bao giờ vượt trần động, và khi thị trường vượt
**cả** trần động thì vẫn **không đặt lệnh** (thà lỡ phiên còn hơn mua trên trần).

### Ca chứng minh ngược (F1/F2)
Không chỉ khẳng định "bật thì tốt hơn": F1 tái lập đúng **chữ ký thất bại thật ngày 08-12** —
trần cố định 20.000đ, thị trường 20.200–20.500 ⇒ `_limit_price` trả `None`, **0 lệnh**, đúng
như đã xảy ra với TV1. F2 cùng dữ liệu đó, bật P1 ⇒ đặt được ở 20.300.

---

## 2. P2 — mẫu số pacing theo KL kỳ vọng + clamp tape

### Sửa gì
Trong `_child_qty`, nhánh `if q.day_volume:`:

```
basis     = max(q.day_volume, ADV20_cp × f(t))          # trước: q.day_volume
ceil_allow = 30% × basis − fleet_filled
clamp_allow = (0,5×q.day_volume − fleet_filled) / (1 − 0,5)      # trần đuôi tape THẬT
allowance  = min(floor_allow, ceil_allow, clamp_allow)
```

`f(t)` = tỷ trọng KL luỹ kế **trung vị** tới phút t, đo trên rổ 23 mã mỏng × 120 phiên
(`out/cum_volume_profile.csv`), đã ép đơn điệu không giảm, nội suy tuyến tính.

### Clamp — điểm quan trọng nhất, và công thức KHÔNG phải cái hiển nhiên
Bất biến cần giữ: fill luỹ kế của fleet ≤ 50% KL khớp **thật**. Đặt `F` = fleet đã khớp,
`V` = KL phiên (**V đã bao gồm F**). Fill thêm `X` vẫn phải giữ `F+X ≤ c(V+X)`:

> `X ≤ (cV − F)/(1 − c)` — với `c=0,5` ⇒ **`X ≤ V − 2F`**

Dạng lỏng tay `cV − F` **sai**: nó quên rằng chính fill của ta cũng làm `V` tăng. Đây là loại
lỗi mà một bộ test "nạp sẵn trạng thái" sẽ không bao giờ hỏi tới — nên E1 kiểm bất biến bằng
cách **chạy nhiều bước liên tiếp** và đo `max(F/V)` thật, chứ không assert lên một con số.

**Vì sao clamp là điều kiện đi kèm, không phải guard rời:** bỏ hẳn trần 30% cho ta chiếm >50%
tape ở **6,9% số phiên** (>80% ở 3,5%) — vì `floor_allow` neo vào ADV20 chứ không vào KL thật
hôm nay, mà **12,7% số phiên có KL <30% ADV20**. Clamp bịt đúng nhóm đó mà không bóp đầu phiên.
Code cưỡng chế điều này: `_expected_vol_basis` kiểm luôn cấu hình clamp và trả `None` (⇒ tắt cả
hai vế) nếu clamp hỏng — **không có đường nào nới mẫu số mà không có trần đuôi**.

Ca **E4/E5** phân định vai trò bằng số thật: phiên bình thường ràng buộc buộc là trần 30%
(clamp chỉ là backstop); phiên **mỏng cuối phiên** thì clamp (1.000cp) thắng cả floor ADV20
(3.522cp) — clamp là ràng buộc **binding thật**, không phải trang trí.

### Tương tác với các tầng đã có trong executor — kiểm tường minh, không suy luận

| Cơ chế | Kết luận | Ca |
|---|---|---|
| **EXTREME-regime** | **KHÔNG bị P2 làm chậm.** Chiều MUA khi EXTREME_DOWN bị chặn **trước** khi tính KL (`EXTREME_PAUSE` + `continue`) — không bao giờ tới `_child_qty`. Lệnh **BÁN** (gồm cắt lỗ khẩn) **không đi vào nhánh ADV20/P2** dù cờ bật hay tắt. | H1, H2, H3 |
| **HYBRID fill-timing** | Trần HYBRID chặt hơn vẫn **cắt sau** P2 — P2 không vượt mặt tầng lịch trải (600→200cp). | I1 |
| **Gap-adaptive** | Không đụng: cùng đường bypass với EXTREME (`_hybrid_bypass`). | — |
| **BÁN / non-ADV20 (BAL) / CAPIT bán** | Cờ BẬT hay TẮT **ra cùng KL** — P2 chỉ chạm MUA-ADV20. | G1, G2 |
| **`day_volume=0`** (halt/chưa có tape) | P2 **không** áp clamp — áp ở đây sẽ là **regression** (0 tape ⇒ chặn sạch). | F1 |

Điểm cần nói thẳng về EXTREME: yêu cầu dispatch là "kiểm EXTREME có bypass đúng `ceil_allow`/
clamp mới không". Câu trả lời đúng là **EXTREME không cần bypass, vì nó không bao giờ chạm tới**
— MUA bị dừng ở tầng trên, BÁN không vào nhánh ADV20. Nếu sau này ai đó đưa lệnh BÁN vào nhánh
ADV20, ca G1/G2/H1 sẽ đỏ ngay — đó là lý do 3 ca này tồn tại dù hôm nay chúng "hiển nhiên đúng".

### Hai bẫy vận hành đã xử lý
- **Journal ngập**: `_child_qty` chạy từ **cả** `_place_slices` **lẫn** `_would_be_unchanged`
  mỗi chu kỳ 20s ⇒ `EXPVOL_PACING` chỉ ghi **1 lần/parent/phiên** (ca J1: chạy 25 lần → 1 dòng).
- **Huỷ+đặt lại vô ích**: đường **kiểm tra** (`exclude_reserved`) phải ra **cùng KL** với đường
  **đặt**, nếu lệch thì bot tự huỷ rồi đặt lại chính nó mỗi vòng poll (ca K1).

---

## 3. P5 — ghi 10 mức giá chờ

DNSE G1 thật sự trả `quotes[].bid/offer` = list 10 mức `{price, quantity}`, nhưng `Quote` chỉ
giữ mức 1 và dòng `raw.update(... not isinstance(v, (list, dict)))` vứt sạch phần còn lại.
`_log_l2()` ghi bản ghi `kind="quote_l2"` vào `dnse_raw_<date>.jsonl` **trước** khi chúng bị vứt.

**Logging thuần**: không đổi `Quote`, không đổi giá/KL đặt lệnh, **không thêm một lời gọi API
nào** (ghi lại chính payload đã lấy về), và `except Exception: pass` — lỗi ghi log tuyệt đối
không được làm hỏng đường lấy quote vì nó nằm trên đường đặt lệnh.

**Throttle 60s/mã** (`DNSE_L2_LOG_SEC`, 0 = ghi mọi lần). `dnse_raw_*.jsonl` là file **kế toán
dùng chung**; cache quote TTL 3s + poll 20s ⇒ ~3 fetch/phút/mã ⇒ ghi mọi lần sẽ thêm ~16k bản
ghi/ngày (~24MB, **gấp đôi** file hiện tại 17–31MB) để đổi lấy độ phân giải nghiên cứu **không
cần** (bucket phân tích 30 phút; TV1 chỉ ~40k cp khớp cả ngày). 60s cho ~30 mẫu/bucket.

### §12 — kiểm consumer trên DỮ LIỆU THẬT, không đọc code rồi đoán
Selfcheck chèn 1.996 bản ghi L2 vào **bản sao file thật** `dnse_raw_2026-08-11.jsonl` (16,9MB,
1.996→3.992 bản ghi) rồi chạy lại **6 consumer** kế toán, so kết quả trước/sau:

| Consumer | Kết quả |
|---|---|
| `daily_nav_snapshot.latest_balance` | giống hệt, 2 account |
| `park_holdings.read_broker_snapshot` | giống hệt (SpaceX 27 mã/136,8tr · ZaloPay 26 mã/63,3tr) |
| `verify_account_snapshot.dnse_fill_events` | giống hệt |
| `report_return_gate.broker_positions` | giống hệt |
| `capit_episode._raw_records` (orders/positions/balances) | giống hệt, không kind nào nhặt nhầm `quote_l2` |
| `execution_quality_review` | bỏ qua sạch — xem dưới |

Mỗi ca có **ca phụ chống rỗng** (`E2b`/`E3b`/…): nếu kết quả rỗng thì "giống hệt" chỉ là đang so
hai cái `None`. Và **ca chống lẫn account** (`E2c`/`E3c`): 2 account phải ra **kết quả khác
nhau** — theo đúng §12, giống hệt nhau giữa 2 account là dấu hiệu rẻ nhất của việc đọc chung
không lọc `account_no`.

`execution_quality_review.py` là consumer **duy nhất không lọc theo `kind`** — nó đọc
`payload["resp"]` (dict) và `payload["orders"]` (list) trên **mọi** bản ghi. Vì vậy tên field
của bản ghi L2 **cố ý tránh** hai key đó ⇒ nó bỏ qua, không vỡ (ca E7).

---

## 4. Quét rộng §23 — và 4 selfcheck ĐỎ SẴN trên production

`executor.py` là module lõi ⇒ **phải** quét rộng, không chỉ theo phạm vi. Chạy **hợp** các
selfcheck phụ thuộc `executor` (16) + `brokers` (9) + `discretionary_accumulation` (3), khử
trùng = **17 file** (`bin/selfcheck_scope_map.sh`, không chép bảng tay).

**Kết quả: 13 xanh, 4 đỏ.**

### Chứng minh 4 ca đỏ KHÔNG phải do P1/P2/P5 — bằng thí nghiệm, không bằng lập luận

1. **Control**: `git checkout` 4 file production về bản sạch (0 dòng P1/P2/P5) → chạy lại 4 ca
   đỏ ⇒ **tái lập Y HỆT**, cùng danh sách assertion, từng chữ. ⇒ pre-existing.
2. **Root cause**: tắt `fill_timing_hybrid_enabled` → **cả 4 xanh (rc=0)**.

```
extreme_regime_selfcheck.py          HYBRID OFF → rc=0
hard_no_chase_ceiling_selfcheck.py   HYBRID OFF → rc=0
paper_main_window_selfcheck.py       HYBRID OFF → rc=0
t2_settlement_selfcheck.py           HYBRID OFF → rc=0
```

**Nguyên nhân**: HYBRID fill-timing bật mặc định từ 2026-08-10 (`fill_timing_hybrid_enabled:
True`) hoãn lệnh **MUA** ra ngoài `hybrid_buy_blocks = 11:00/11:15/13:00/13:15/13:30`. Bốn
selfcheck này khẳng định "lệnh MUA được đặt" tại **09:30** (extreme), **09:16 / 10:46**
(paper_main_window) — những giờ giờ đây **không còn là block MUA**. Lệnh bị hoãn ⇒ không đặt ⇒
cũng không có `HARD_CEILING_BLOCK` để ghi journal (ca E4). Đây là **assertion cũ mốc theo hành
vi mới**, KHÔNG phải bug production: hoãn MUA ngoài block chính là thiết kế của HYBRID.

### Việc này cần xử lý riêng — tôi CỐ Ý không tự sửa
Sửa 4 file test đó nằm ngoài phạm vi dispatch này, và quan trọng hơn: **sửa test cho xanh là
đúng cách rẻ nhất để chôn một lỗi thật**. Cần một lượt riêng xác định cho từng ca "giờ này lẽ
ra phải đặt được lệnh không" trước khi đổi assertion.

Điều đáng lo hơn bản thân 4 ca đỏ: **chúng đã đỏ từ 08-10 mà không ai thấy** — đúng dạng mục
rữa mà §23 hệ luận 1 cảnh báo. Đề xuất: cho `weekly_ops_audit.sh` chạy bộ selfcheck lõi và báo
đỏ, để lần sau không phải một dispatch tình cờ mới phát hiện.

---

## 5. Tự phản biện — học từ HYBRID (93/93 xanh vẫn lọt 3 lỗi nghiêm trọng)

Bài học HYBRID: test "nạp sẵn trạng thái" rồi assert, **không hỏi trạng thái đó xảy ra được
bằng cách nào**. Ba việc đã làm khác đi:

1. **Ca chứng minh ngược cho mọi khẳng định "chặn được"** — P1 F1 (bỏ P1 ⇒ thật sự 0 lệnh, tái
   lập chữ ký thất bại 08-12), P2 E3 (cờ tắt ⇒ gom 1.200cp vs bật 2.000cp), P2 E5 (clamp thật
   sự binding). Cùng khuôn `hard_no_chase_ceiling_selfcheck.py` (§24).
2. **Bất biến đo qua nhiều bước, không assert lên số nạp sẵn** — E1 chạy vòng lặp fill và đo
   `max(F/V)` thật (0,4000), thay vì kiểm một phép tính đơn lẻ.
3. **§12 kiểm trên file thật + ca chống rỗng + ca chống lẫn account** — không đọc code consumer
   rồi kết luận "chắc không sao".

### Rủi ro tồn dư — công bố thẳng

- **`f(t)` là trung vị lịch sử của rổ 23 mã mỏng, không phải của TV1/DGC.** Một phiên có tin
  làm KL dồn khác thường ⇒ `f(t)` sai lệch. Hệ quả bị chặn hai lớp: mẫu số chỉ **max** với KL
  thật (không bao giờ nhỏ hơn hành vi cũ), và clamp neo vào tape **thật** chứ không vào `f(t)`.
- **P1 đổi trần theo anchor trôi ⇒ chi phí trung bình tăng +0,77pp** (đo được, đã báo cáo).
  Đây là đánh đổi user đã duyệt (~20:1 nghiêng về nới), không phải phát hiện mới.
- **P2 chưa từng chạy trên tape thật.** Mọi con số đến từ mô phỏng fill với trần 20% ADV/phiên —
  tham số **chưa neo** bằng fill thật (mới xác nhận tới ~3,86% ADV/phiên), đúng cảnh báo đang mở
  ở `kb/projects/lag-adv-filter-tracking.md`. ⇒ paper trial ≥4 tuần trước khi nghĩ tới production.
- **P5 chưa trả lời được câu hỏi nào cả** — nó chỉ **bắt đầu tích luỹ** dữ liệu. Mọi con số
  depth-aware sizing trước 4–6 tuần nữa vẫn là bịa, y như README đã kết luận.
- **`anchor_prices_for()` gọi DNSE ohlc — chưa chạy trên API thật** (cờ tắt nên chưa có đường
  gọi live). Ba lớp fail-safe che (exception → `None`; thiếu phiên → `None`; sai đơn vị → guard
  sanity), nhưng lần bật paper đầu tiên **phải xem log** `[FAILSAFE]` để xác nhận đường này sống.

---

## 6. File đã sửa (uncommitted)

| File | Repo | Nội dung |
|---|---|---|
| `trading_bot/discretionary_accumulation.py` | WorkingClaude | P1 — `resolve_price_band()` + hằng số + fail-safe |
| `mike/bin/discretionary_accumulation_inject.py` | mike | P1 — `anchor_prices_for()` lấy 5 phiên từ DNSE ohlc |
| `trading_bot/executor.py` | WorkingClaude | P2 — `_expected_vol_frac()`, `_expected_vol_basis()`, sửa `_child_qty` |
| `trading_bot/config.py` | WorkingClaude | P2 — 3 khoá cấu hình (cờ + clamp + đường cong `f(t)`) |
| `trading_bot/brokers.py` | WorkingClaude | P5 — `_l2_levels()`, `_log_l2()`, 1 dòng gọi trong `get_quote` |
| `dynamic_no_chase_ceiling_selfcheck.py` | WorkingClaude | mới — 49 ca |
| `expected_volume_pacing_selfcheck.py` | WorkingClaude | mới — 39 ca |
| `quote_l2_logging_selfcheck.py` | WorkingClaude | mới — 44 ca |

### Cách bật (KHÔNG bật trong lượt này)

```jsonc
// P1 — state file TV1/DGC, cần CẢ HAI:
"dynamic_ceiling": { "enabled": true, "tau": 0.03, "sessions": 5 },
"price_band": { ..., "max_no_chase_ceiling": <VND user duyệt MỘT LẦN> }

// P2 — trading_bot/config.py hoặc override account:
"expected_volume_pacing_enabled": true
```

Rollback: `enabled: false` / `expected_volume_pacing_enabled: false` — một chữ, không cần revert
code. P5 muốn tắt: `DNSE_L2_LOG_SEC` không tắt được logging (chỉ đổi throttle) — muốn tắt hẳn
phải gỡ 1 dòng gọi `_log_l2` trong `get_quote`; cố ý để vậy vì nó không đổi hành vi đặt lệnh.

---

## 7. Bước kế tiếp (đề xuất, không tự làm)

1. **quant-skeptic verify** cả 3 phần — trước khi bật bất cứ gì (thứ tự HYBRID: verify TRƯỚC).
2. **P5 bật ngay được sau verify** — nó chỉ là log, và mỗi ngày chờ là một ngày mất dữ liệu.
3. **P1 cần user chốt `max_no_chase_ceiling`** (số VND) — đây là quyết định **chính sách**, §22.
4. **P2 paper trial ≥4 tuần** theo đúng mẫu HYBRID, rồi mới bàn production.
5. **Riêng: 4 selfcheck đỏ từ 08-10** — một lượt riêng, đừng gộp vào việc này.
