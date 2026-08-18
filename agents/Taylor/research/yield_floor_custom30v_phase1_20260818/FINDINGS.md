# yield_dividend_floor Phase 1 — điều tra trước khi wire vào custom30V

**Job** `Taylor_20260818_131745` · **Ngày** 2026-08-18 · **Trạng thái: KHÔNG WIRE — cần user quyết**
**quant-skeptic: CONFIRMED (confidence high)** — tái lập độc lập khớp từng con số; bắt 1 lỗi *diễn giải*
ở §3b (đã đính chính tại chỗ), không lỗi số. Log: `mike/logs/verify_20260818_132819_2274736.log`.

## Kết luận một dòng

Pool ứng viên = **60 mã ở cả 35/35 kỳ rebalance** (điều kiện `pool > 30` của dispatch ĐẠT), nhưng
**tiebreaker thật sự KHÔNG BAO GIỜ fire** (0/34 kỳ có dữ liệu thật), còn **spec viết trong dispatch
nếu làm đúng chữ sẽ thay 16,3/30 mã mỗi kỳ** — tức xoá sổ selector custom30V chứ không phải phá hoà.
Hai đường đều không phải "soft tiebreaker". Đề xuất một đường thứ ba đã đo sẵn (§4).

## 1. Đường đi production của custom30V (xác minh, không suy đoán)

`papertrade_daily.sh` [6b] (15:30 ICT hằng ngày) → `BASKET_SELECT=yieldcombo CUSTOM30_TABLE=custom30v_8l
python3 custom30_history.py` → `custom_basket.build_pit(gate_rating=3, rebal="q2m5",
weight_scheme="namecap")` → BQ `tav2_bq.custom30v_8l` (money-path: 30% idle-pool parking).

Chuỗi chọn mã (`custom_basket.py:940-1080`):

```
liq_row  = liquidity quý TRƯỚC, giảm dần            (~420 mã)
gated    = liq_row lọc 8L rating ≤ 3                 (~220 mã)
pool     = gated[:CFO_POOL=60]                       ← lát cắt thanh khoản, chỉ là SÀN giao dịch
score    = rank_pct(1/PE) + rank_pct(1/PCF)          ← selector THẬT của custom30V
picks    = sorted(pool, key=score, desc)[:30]
```

**Điểm mấu chốt:** thanh khoản chỉ là *cổng*; thứ hạng cuối do `score` value-yield quyết định.

## 2. Pool size — dispatch Bước 0 (`probe_pool_size.py`)

| rebal | n_liq | n_gated (8L≤3) | pool | pool>30 |
|---|---:|---:|---:|---|
| 2024-02-05 → 2026-08-05 (11 kỳ) | 415–451 | 210–238 | **60 mọi kỳ** | YES |

Mở rộng 2018→2026 (`probe_tie_rate.py`): **pool = 60 ở cả 35/35 kỳ.** Pool luôn > 30 vì
`CFO_POOL` chặn cứng ở 60, không phải vì thị trường vừa đủ mã.

## 3. Hai đường trong dispatch, đo bằng số (`probe_yield_bonus.py`, 35 kỳ 2018→2026)

Nhãn `_yield_floor` tái lập ĐÚNG định nghĩa `trading_bot/due_diligence.py` (cửa sổ 365 ngày, dedup
`(ticker, exright_date, dividend_year, dividend_stage_vi)` lấy `public_date` mới nhất, giá tham
chiếu raw `COALESCE(Price,Close)`, banking ICB 8355 loại). Panel batched 2 query thay vì per-ticker.

**Phân bố nhãn trên 2.100 (mã × kỳ) trong pool:**

| nhãn | n | % |
|---|---:|---:|
| NO_DATA | 880 | 41,9% |
| ABOVE_FLOOR | 640 | 30,5% |
| BANKING_EXCLUDED | 420 | 20,0% |
| **BELOW_FLOOR** | **142** | **6,8%** |
| NEAR_FLOOR | 18 | 0,9% |

⇒ **61,9% pool nằm ở nhóm trung tính** (NO_DATA + BANKING), đúng theo constraint fail-open.

### 3a. V1 = tiebreaker THẬT (phá hoà điểm bằng nhau): `sorted(pool, key=(-score, yield_prio, ticker))`

Đây là nghĩa đen của "soft tiebreaker": chỉ được đảo thứ tự giữa các mã có `score` **bằng nhau tuyệt
đối**, không bao giờ hất một mã có score tốt hơn ra.

| số kỳ đổi thành phần | 1/35 (2,9%) |
|---|---|
| kỳ duy nhất đó | 2018-02-05 — **cả 60 mã cùng score 1,0** vì quý nguồn thiếu sạch PE/PCF (`fillna(0.5)`), tức lỗ hổng dữ liệu chứ không phải hoà thật |
| **loại kỳ hỏng dữ liệu** | **0/34 kỳ — KHÔNG BAO GIỜ FIRE** |

Hoà tại đúng biên 30/31 (điều kiện cần để tiebreaker đổi được thành phần rổ): **1/35**, và chính là
kỳ hỏng đó. `score` là tổng hai rank-percentile liên tục ⇒ hoà tuyệt đối gần như không xảy ra.

**⇒ Gate criterion #1 của dispatch ("tiebreaker fires at 11-05 rebalance") gần như chắc chắn TRƯỢT.**

### 3b. V3 = spec viết nguyên văn trong dispatch: `pool.sort(key=(yield_priority, name)); pool[:30]`

| số mã bị thay so với rổ production | **16,29 / 30 mỗi kỳ (54%)**, min 12 max 21, **35/35 kỳ đều đổi** |
|---|---|

Vì sort key này là **PRIMARY**, `score` value-yield bị vứt bỏ hoàn toàn.

⚠️ **Đính chính cơ chế (quant-skeptic bắt được, 2026-08-18 — số 16,29 KHÔNG đổi, chỉ lời giải thích
sai):** bản đầu tiên viết "chỉ ~7 mã/kỳ có nhãn BELOW/NEAR, 23 suất còn lại lấp theo alphabet" — SAI.
Trong `_yield_floor`, nhãn `ABOVE_FLOOR` **chỉ được gán khi `stable=True`** (khối `if stable:` ở
`due_diligence.py:408-410`) ⇒ mọi ABOVE_FLOOR đều rơi vào **priority 3** ("stable nhưng ABOVE"), không
phải 4. Đo lại: **22,9 mã/kỳ có priority < 4** (≈4,1 BELOW + 0,5 NEAR + **18,3 stable-ABOVE**), chỉ
~7 mã/kỳ thật sự thuộc nhóm trung tính (NO_DATA/BANKING). Vậy 30 suất được lấp chủ yếu từ **khối
stable-ABOVE_FLOOR 18,3 mã** — tức V3 xếp rổ theo "có trả cổ tức đều hay không" rồi mới tới alphabet.
Kết luận không đổi: 16,29/30 mã bị thay ⇒ **thay selector, không phải phá hoà.**

**Hệ quả cho spec:** hai bậc ưu tiên 3 ("stable_payer nhưng ABOVE_FLOOR") và 4 ("ABOVE_FLOOR") mà
dispatch yêu cầu là **KHÔNG PHÂN BIỆT ĐƯỢC** với ngữ nghĩa hiện tại của `_yield_floor` — bậc 4 trong
spec là nhánh chết. Bất kỳ implement nào sau này phải hoặc bỏ bậc 4, hoặc đổi `due_diligence.py`
(mà constraint của dispatch lại cấm).

**⇒ Đây KHÔNG phải tiebreaker. Đây là thay toàn bộ selector. KHÔNG được implement như đã viết.**

## 4. V2 = đề xuất thay thế đã đo sẵn — cộng điểm mềm

Đúng khuôn mẫu ĐÃ CÓ trong chính file này (`BASKET_DCF_MODE="tiebreak"`: `score[t] += DCF_W * mos_r[t]`):

```python
BONUS = {1: 1.0, 2: 0.6, 3: 0.2, 4: 0.0}       # 1=BELOW 2=NEAR 3=stable-ABOVE 4=trung tính
score[t] += W * BONUS[yield_prio[t]]            # W nhỏ ⇒ chỉ lật được các cặp sát biên
```

| W | mã đổi / kỳ (TB) | số kỳ có đổi |
|---:|---:|---:|
| 0,05 | 0,83 | 15/35 |
| **0,10** | **1,03** | **20/35** |
| 0,20 | 1,57 | 28/35 |
| 0,50 | 2,60 | 32/35 |

Ở W=0,10 hiệu ứng là ~1 mã/kỳ — đúng tinh thần "soft", có thể quan sát được, và bị chặn cứng bởi độ
lớn của `score` (thang 0–2) nên không bao giờ lật được cặp cách nhau nhiều bậc.

**Nhưng:** V2 là **blend selector**, không phải tiebreaker, và nó **đổi lợi suất rổ**. Research
`dividend_yield_floor_20260818` **REFUTED H1** (không có alpha lợi suất: BHAR60 t=0,67, median ÂM
−0,97pp) và chỉ CONFIRMED H2 (đệm đuôi trái, ΔMDD60 +3,46pp) ở mức tin cậy **TRUNG BÌNH**.
Wire một tín hiệu chỉ-có-downside vào selector quyết định lợi suất ⇒ **bắt buộc backtest NAV/DD
(IS 2014-19 / OOS 2020+, self-check 0 VND) trước**, theo §18 + luật "quant-skeptic CONFIRMED là điều
kiện cần trước khi wire production".

## 5. Hai phát hiện phụ, quan trọng cho bất kỳ đường nào

1. **Trùng lặp tín hiệu:** BELOW_FLOOR trung bình **4,06/60 mã trong pool**, trong đó **2,29 mã đã
   nằm sẵn trong rổ 30 của production** (56%). Selector yieldcombo (1/PE + 1/PCF) và sàn cổ tức đều là
   trục *value* nên tương quan — headroom thật nhỏ hơn nhiều so với cảm giác ban đầu.
2. **Chi phí vận hành của cách gọi trong spec:** `_yield_floor()` là per-ticker, 1 query BQ/mã, cache
   chỉ trong-process. `custom30_history.py` **dựng lại TOÀN BỘ ~50 kỳ rebal mỗi ngày** ⇒ spec "gọi
   `_yield_floor()` cho từng mã" = **~3.000 query BQ mỗi ngày** thêm vào pipeline 15:30. Phải batch
   (2 query cho cả panel — xem `probe_yield_bonus.py`) nếu wire.
3. **Panel batched ≡ `_yield_floor()` — đã kiểm chứng, không phải khẳng định suông:**
   `probe_panel_equiv.py` gọi THẲNG `trading_bot.due_diligence._yield_floor()` và so từng ô với panel
   trên 24 mã × 5 kỳ rebal (2025-08 → 2026-08) phủ cả 5 nhãn: **khớp 120/120 (100%)**, `prox_to_floor`
   khớp tới 4 chữ số thập phân ở mọi ô cả hai bên cùng tính được. quant-skeptic chạy độc lập một
   script tương đương trên 25 cặp phân tầng: **25/25 khớp**. Đây là mắt xích yếu nhất của phép đo và
   nó đã được đóng.
4. **Không có vi phạm price-basis:** `_ref_price_for` dùng `COALESCE(Price, Close)` — cùng hệ raw PIT
   với `pxw_sql()`. Nhánh cổ tức as-of đúng (`exright_date <= asof`). Đây là điểm SẠCH, không phải lo.

## 6. Khuyến nghị

**KHÔNG wire gì trong job này.** Ba lựa chọn để user chọn:

| | Việc | Đánh đổi |
|---|---|---|
| **A** | Bỏ Phase 1 ở custom30V, chuyển sang **LAG candidate tiebreaker** (chính dispatch nêu làm phương án dự phòng) | LAG có bước ranking rời rạc hơn ⇒ tiebreaker có cơ hội fire thật; cần điều tra riêng |
| **B** | Làm V2 (W=0,10) nhưng **backtest NAV/DD trước** rồi mới wire | Đúng quy chuẩn; tốn 1 job backtest; rủi ro là H1 đã REFUTED nên kỳ vọng lợi suất ≈ 0 |
| **C** | Giữ `_yield_floor` DISPLAY_ONLY như hiện tại, chỉ thêm cột nhãn vào bảng `custom30v_8l` để **quan sát 2 kỳ** rồi quyết | Rủi ro bằng 0, không đổi money-path, có dữ liệu thật cho quyết định 2027-02 |

Nghiêng về **C rồi B**: research tự khai MEDIUM và H1 REFUTED — chưa đủ để đổi cách chọn mã của rổ
parking đang chạy tiền thật.

## Tái lập

```bash
DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
$DNA_PYEXE probe_pool_size.py     # bảng §2
$DNA_PYEXE probe_tie_rate.py      # bảng §3a (tie rate 35 kỳ)
$DNA_PYEXE probe_yield_bonus.py   # bảng §3 phân bố nhãn + §3a/3b/4 + §5.1
$DNA_PYEXE probe_panel_equiv.py   # §5.3 — panel vs _yield_floor(), 120/120
```
Cả 4 script **chỉ đọc** — không ghi file, không `bq load`, không đụng `tav2_bq.custom30v_8l`.
