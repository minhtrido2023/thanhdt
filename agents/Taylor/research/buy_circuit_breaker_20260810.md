# Circuit-breaker dừng-mua khi giá rơi trong lúc thực thi multi-slice BUY — **NO-GO**

- **Job**: `Taylor_20260810_065757` · **Ngày**: 2026-08-10 · **Owner**: Taylor
- **Kết luận**: **KHÔNG wire.** Cơ chế thiếu là CÓ THẬT (§1), nhưng lấp nó bằng circuit-breaker
  dừng-mua **làm hại sổ LAG ở mọi ngưỡng, mọi mốc neo, mọi khung thời gian, cả IS lẫn OOS**.
- **Không sửa một dòng code production nào.** Không có `pending_*` patch — không có gì để bật.
- **quant-skeptic: CONFIRMED (high)**, có independent recompute toàn bộ (§9b).
- **Ca SCL 10/08 không phải ca circuit-breaker**: đó là biến động **z = −0,96** (dưới 1 sigma) của
  chính SCL. Xem §2.

---

## §0 — TL;DR cho người bận

| Câu hỏi của dispatch | Trả lời |
|---|---|
| Có lỗ hổng "chỉ có trần trên, không có trần dưới" không? | **CÓ** — xác nhận bằng dòng code cụ thể (§1) |
| SCL hôm nay có phải sự kiện bất thường? | **KHÔNG** — z = −0,96 vs rvol_20d 3,87% (§2) |
| Ngưỡng động nào là hợp lý? | Mốc neo đúng = `q.ref` (giá tham chiếu phiên). Nhưng **mọi** ngưỡng đều bị bác (§3, §4) |
| Circuit-breaker có cải thiện risk-adjusted return? | **KHÔNG** — tranche bị bỏ qua là tranche **TỐT NHẤT** của sổ: +9,5% vs +6,4% toàn sổ, CI 95% [+4,4; +14,2] hoàn toàn dương (§4) |
| Có lý do "bảo hiểm đuôi trái" không? | **KHÔNG** — đuôi trái của nhóm bị trip **MỎNG HƠN** nền: 0,0% số ca lỗ >20% vs 2,6% của nền (§5) |
| Thế thì SCL sai ở đâu? | Không phải ở tầng thực thi. Hai ứng viên thật: sàn ADV 2 tỷ chỉ **cảnh báo chứ không chặn**, và `due_diligence.py` không có trục "đã chạy xa sau rally" (§7) |

---

## §1 — Xác nhận lỗ hổng trong code (có thật, trích dẫn dòng)

`trading_bot/executor.py::_limit_price()` — nhánh MUA chỉ có **trần trên**, không có bất kỳ
kiểm tra nào theo chiều xuống:

```python
# trading_bot/executor.py:479-486
cap = o.ref_price * (1 + self._buy_chase_pct(o.ticker))
if q.ceiling:      cap = min(cap, q.ceiling)
hard = self._hard_buy_ceiling(o)
if hard:           cap = min(cap, hard)          # trần tuyệt đối (anchor entry-window)
desired = (q.ask if (cross and q.ask) else ...)  # bám giá chào SỐNG, đọc lại mỗi chu kỳ
px = min(desired, cap)                            # ← chỉ min(). Không có max() theo chiều xuống.
```

`q.ask` càng rơi thì `px` càng thấp và lệnh **vẫn được đặt**. Không có nhánh nào so `q.last`/
`q.ask` với `o.ref_price`/anchor theo chiều giảm rồi `return None`. Grep toàn file cho
`circuit|breaker|halt|stop_buy|intraday_drop|drop_pct` → **0 hit**.

`mike/bin/filter_lag_entry_window.py`: thuần **CHỈ ĐỌC**, offline, phân loại `due_today` từ cột
`status` của CSV + cổng anchor. Không biết gì về giá trong ngày (chính docstring của nó nói:
*"việc so anchor với giá live là của tầng đặt lệnh"*). **Đúng — không phải chỗ để đặt breaker.**

### Nhưng có 2 cơ chế đã tồn tại, và cần nói rõ vì sao chúng KHÔNG bắt được ca SCL

`trading_bot/executor.py:1145` `_extreme_regime_raw()` và `:1188` `_floor_guard_buy()` **đã** dừng
mua — nhưng chỉ với 2 trigger:

| Trigger | Điều kiện | Vì sao trượt ca SCL |
|---|---|---|
| (i) cận sàn | `last <= floor*(1+extreme_band 3%)` | SCL (HNX, biên ±10%): sàn = 21.780 → ngưỡng 22.433 (−7,3%). Giá thấp nhất hôm nay ~23.300 |
| (ii) vận tốc | `r15 < −extreme_move_z(3,0) × rvol_20d` | Đây là **vận tốc 15 phút**, không phải mức tích luỹ. 3×3,87% = **−11,6% trong 15 phút**. SCL trượt −3,7% rải đều cả phiên |

⚠️ **Và cả hai đều `extreme_regime_enabled = False`** (`trading_bot/config.py:131`). Đã kiểm
`secrets/trading_bot_accounts.json`: chỉ account **paper `main`** bật (`overrides`); **SpaceX,
ZaloPay, RocketX (đều `mode="live"`) không có override → OFF**. Nên hôm nay trên live, chiều MUA
**hoàn toàn không có giới hạn dưới nào** — đúng như dispatch nghi ngờ.

Nói gọn: hệ có cổng bắt **vận tốc** và bắt **cận sàn**, không có cổng bắt **mức tích luỹ trong
ngày**. Đó là lỗ hổng thật. Phần còn lại của báo cáo trả lời: có nên lấp không.

---

## §2 — Ca SCL 10/08 nằm ở đâu trong phân phối? Dưới 1 sigma.

Số liệu thật (BQ `tav2_bq.ticker`, SDK Python + `secrets/sa-key.json`):

| | |
|---|---|
| `prev_close` (07/08) | 24.200đ |
| Giá thị trường 11:27 | 23.300đ → **−3,72%** |
| `rvol_20d` của SCL tính tới 07/08 (causal) | **3,87%** |
| **z** | **−0,96** |
| Trần đuổi động hiện hành `clamp(2×rvol, 1,5%, 4%)` | 4,00% (kịch trần) |

`rvol_20d` của SCL **cao** (3,87%) chính vì cú rally 15.300 → 25.200 (+64,7%) — biên độ ngày gần
đây ±4,6%. Một phiên −3,7% với mã đang dao động ±4,6%/ngày là **hoàn toàn bình thường**.

Muốn breaker bắt được ca này thì ngưỡng phải là **z ≈ 1,0** — mức đó **nổ trên 28,7% số phiên**
của rổ LAG (bảng §3). Tức không phải "chặn ca bất thường", mà là "hơn 1 trong 4 phiên mua đều bị
chặn". Đây là lý do đầu tiên khiến hướng này hỏng.

*(Con số "29% số phiên biên độ >4%" trong dispatch: xác nhận đúng tinh thần — đo lại trên
2024+ cho riêng SCL: p90 biên độ ngày = 6,68%.)*

---

## §3 — Khảo sát biến động: ngưỡng nào là "bất thường" với loại mã ta hay mua?

**Mẫu**: 110 mã từng là buy-candidate trong 43 file `golive_v23_recommendations_*.csv`
(2026-06-11 → 2026-08-07), bars ngày 2023-01 → 2026-08-07, **67 mã sổ LAG = 42.971 ticker-day**.
`rvol_20d` causal (chỉ dùng phiên TRƯỚC t). Cơ sở giá: `Open/High/Low/Close` đều đã kiểm là
**cùng basis điều chỉnh** (0,000% số dòng có `Close` nằm ngoài `[Low,High]`; cột `Price` thô nằm
ngoài 72,7% số dòng → **không dùng**).

| Rổ | rvol_20d trung vị | Biên độ H/L trung vị | p10 mức rơi vs prev-close | p5 | p1 |
|---|---|---|---|---|---|
| **LAG (67 mã)** | 2,25% | 2,41% | −4,71% | −6,86% | −10,01% |
| PARK/custom30V (38 mã) | 1,74% | 2,33% | −3,25% | −5,00% | −7,80% |
| SCL riêng | 1,88% | 2,36% | −3,73% | −5,96% | −11,77% |

**Tần suất một breaker sẽ nổ, theo ngưỡng z** (mốc neo = prev-close; % số phiên của rổ LAG):

| z | 1,0 | 1,5 | 2,0 | 2,5 | 3,0 |
|---|---|---|---|---|---|
| % phiên nổ (LAG) | **28,7%** | 16,1% | 9,3% | 5,6% | 3,5% |
| % phiên nổ (PARK) | 27,1% | 13,6% | 7,4% | 4,6% | 3,0% |

Đây là cơ sở để hiệu chỉnh, **đồng dạng chase-cap** (`clamp(k×rvol_20d, sàn, trần)`, §24) như
dispatch yêu cầu — và nó nói ngay: vùng "hiếm" thật sự là z ≥ 2,5. Nhưng z=2,5 thì không bắt được
SCL (z=0,96), còn z=1,0 thì nổ 28,7% số phiên. **Không có ngưỡng nào vừa hiếm vừa bắt được ca
gốc.** §4 cho biết điều gì xảy ra ở từng ngưỡng.

---

## §4 — Backtest tác động (dose-response): breaker **phá giá trị** ở mọi ngưỡng

### Thiết kế (point-in-time, không look-ahead, thiên vị CÓ CHỦ ĐÍCH **về phía** breaker)

- **Tập sự kiện**: **mọi lệnh MUA của sổ LAG trong bản audit R3 đã pin**
  (`data/v23_golive_audit_2014_now_..._cap50b_ideal_univpit.csv`, record `TX`), **2014-01-27 →
  2026-04-09**. Đây là tập PIT thật của chiến lược, **không phải** rổ chọn từ CSV gần đây (rổ đó
  có selection-bias về TÊN — dùng được cho §3 vì độ phân tán ít nhạy, **không** dùng cho kết luận
  lợi nhuận).
- **Ngày thoát = lệnh BÁN thật của cùng `holding_id`** (khớp 100%, hold trung vị 38 ngày lịch) →
  chân trời là chân trời THẬT của chiến lược, không phải h tự chọn. Có kiểm chéo T+20/T+60.
- **Phản thực thiên vị về phía breaker**: tranche bị bỏ qua được giả định khớp **đúng tại
  `trip_price`** — mức giá **CAO NHẤT** còn với tới được sau khi breaker nổ (mọi fill sau đó đều
  rẻ hơn). Tức lợi nhuận đo được của "nền" là **cận dưới**. ⇒ Breaker chỉ +EV nếu con số này **ÂM**.
- Breaker = phần vốn đó nằm tiền mặt, lợi nhuận 0.
- **N cho suy diễn = 231 NGÀY VÀO LỆNH** (607 fill, 289 mã) — lệnh LAG về theo lô cùng ngày, mã
  cùng ngày chia chung nhân tố thị trường. Bootstrap **cụm theo NGÀY**, không theo dòng.

### Kết quả — lợi nhuận của chính tranche mà breaker sẽ bỏ qua

| z | % lệnh bị trip | n | **Mean (thoát THẬT)** | Median | Hit% | T+20 | T+60 |
|---|---|---|---|---|---|---|---|
| 1,5 | 19,8% | 120 | **+8,19%** | +5,92% | 70,0% | +3,92% | +7,63% |
| 2,0 | 12,0% | 73 | **+9,49%** | +8,15% | 67,1% | +3,29% | +10,13% |
| 2,5 | 9,1% | 55 | **+9,36%** | +8,12% | 70,9% | +3,32% | +9,40% |
| 3,0 | 4,8% | 29 | **+8,72%** | +7,94% | 75,9% | +2,01% | +7,42% |
| — | (toàn sổ, vào tại close) | 607 | **+6,38%** | +3,27% | — | +3,52% | +5,70% |

**Tranche bị breaker bỏ qua là tranche TỐT NHẤT của sổ** — tốt hơn nền ~3pp, hit-rate cao hơn.
Điều này hợp lý về mặt kinh tế: LAG là sổ PEAD/earnings-drift — mua nhịp trũng trong ngày của một
mã đang có drift nguyên vẹn là **mua rẻ hơn cùng một luận điểm**.

### Bootstrap cụm theo ngày (10.000 lần rút) — CI hoàn toàn dương

| z | n ngày | mean | **95% CI (cụm theo ngày)** | P(mean < 0) |
|---|---|---|---|---|
| 1,5 | 77 | +8,19% | **[+4,79; +11,73]** | 0,00% |
| 2,0 | 49 | +9,49% | **[+4,41; +14,15]** | 0,00% |
| 2,5 | 38 | +9,36% | **[+3,75; +14,31]** | 0,03% |
| 3,0 | 23 | +8,72% | **[+3,25; +12,90]** | 0,04% |

### IS / OOS — cùng dấu, OOS còn mạnh hơn

| z | IS 2014-19 (n, mean) | OOS 2020+ (n, mean) |
|---|---|---|
| 1,5 | 40 · +6,61% | 80 · **+8,98%** |
| 2,0 | 22 · +4,66% | 51 · **+11,58%** |
| 3,0 | 7 · +7,45% | 22 · **+9,12%** |

### Leave-one-out theo năm (z=2,0) — không phải hiện vật 1-2 năm

Bỏ từng năm một, mean vẫn dương **cả 13/13 lần**, khoảng **[+6,65%; +10,48%]**. (Năm mạnh nhất
2025 +22,6%; bỏ nó đi vẫn còn +6,65%.)

### 3 phép thử độ bền — kết luận không đổi

**(a) Mốc neo nào?** Dispatch hỏi kỹ điểm này. Cả 3 lựa chọn đều cho cùng kết luận:

| Mốc neo | z=2,0 trip% | mean | Ghi chú |
|---|---|---|---|
| `q.ref` (prev-close) | 12,0% | +9,49% | **Đúng nhất về kỹ thuật**: có sẵn từ slice ĐẦU TIÊN, cùng thứ nguyên với `rvol_20d` (đều là sigma lợi nhuận NGÀY), độc lập với chính việc thực thi của ta ⇒ deterministic, audit được |
| Giá mở cửa (≈ lệnh khớp đầu) | 8,1% | +8,93% | Tự tham chiếu; **không bảo vệ được slice đầu** — đúng lỗ hổng mà `_floor_guard_buy` đã phải vá cho ca PNJ |
| Anchor trượt 3 phiên (khung SCL) | 33,3% | +5,52% | **Tệ nhất**: là giá CŨ tới 2 phiên; mã chỉ cần trôi xuống là nổ ngay ⇒ trip 25–43% số lệnh |

**(b) Chỉ tính ngày nhịp giảm GIỮ tới hết phiên** (`close <= trip level`, loại wick — đây là ca
thuận lợi nhất có thể dựng cho breaker): z=2,0 nổ 6,8%, mean vẫn **+9,50%**; z=3,0 mean **+10,43%**.

**(c) `low` của bar ngày bao gồm cả ATC** ⇒ phép đo này cho breaker nổ **NHIỀU hơn** thực tế, tức
lại càng thiên vị về phía breaker. Đã kiểm bằng (b).

---

## §5 — Lập luận "bảo hiểm đuôi trái" cũng không đứng được

Nếu mean dương nhưng đuôi trái dày thì vẫn có thể biện hộ bằng bảo hiểm (đúng khuôn DT5G:
*fail-safe risk gate, không phải return-enhancer*). Đo thật thì **ngược lại**:

| Nhóm | p5 | p10 | Median | Mean | **Tệ nhất** | **% ca lỗ >20%** |
|---|---|---|---|---|---|---|
| Bị trip z=1,5 | −12,25% | −10,60% | +5,92% | +8,19% | −17,86% | **0,0%** |
| Bị trip z=2,0 | −11,12% | −10,03% | +8,15% | +9,49% | −16,15% | **0,0%** |
| Bị trip z=3,0 | −9,20% | −4,45% | +7,94% | +8,72% | −12,51% | **0,0%** |
| **Nền (toàn sổ)** | −14,63% | −10,30% | +3,27% | +6,38% | **−52,14%** | **2,6%** |

Đuôi trái của nhóm "mua vào nhịp trũng" **mỏng hơn** nền ở mọi phân vị. **Không một thảm hoạ nào
của sổ LAG (lỗ >20%, tệ nhất −52%) rơi vào nhóm mà breaker sẽ chặn.** Thảm hoạ của LAG đến từ chỗ
khác, không từ "phiên vào lệnh có nhịp trũng". Bảo hiểm này thu phí mà không phủ đúng rủi ro.

---

## §6 — Hệ quả ngoài dự kiến: cổng EXTREME sẵn có cũng có chi phí đo được trên LAG

Cùng bộ máy, áp **đúng luật đang có trong code** (`_floor_guard_buy`: `last <= floor×1,03`, biên
sàn 7/10/15% suy từ chính tape của từng mã — 124 mã HOSE / 108 HNX / 150 UPCOM):

- Nổ trên **57/607 = 9,4%** số lệnh MUA của LAG.
- Tranche bị bỏ qua có mean **+10,58%**, median +6,40%.
- Với mã **HOSE** (biên ±7%) ngưỡng này tương đương **z ≈ 1,74** — tức rơi đúng vào vùng mà §4
  chứng minh là mua thì có lợi. (Trung vị toàn rổ z ≈ 2,90 vì UPCOM biên rộng.)

**Cách đọc cho đúng, không nói quá**: cổng này được đưa vào cho ca PNJ — lệnh 1-slice của NAV nhỏ
khớp trọn tại giá sàn trước khi gate 2-poll kịp arm — một **kiểu hỏng khác**, và backtest gốc của
EXTREME validate ở **chiều BÁN**. Số liệu ở đây **không bác bỏ** lý do bảo hiểm đó; nó chỉ đo được
**cái giá** của nó trên sổ LAG (n=57), điều trước nay chưa ai đo. Đáng để Mike/user biết trước
**nếu** có lúc bàn bật `extreme_regime_enabled` trên live — đó là quyết định riêng, không thuộc
job này, và **tôi không đề xuất đổi gì ở đây**.

---

## §7 — Nếu SCL vẫn khiến ta không yên tâm, thì phải sửa ở đâu?

Không phải ở tầng thực thi. Chính dispatch đã chỉ ra 2 chỗ, và dữ liệu ủng hộ cả hai:

1. **Sàn thanh khoản chỉ cảnh báo, không chặn.** `golive_v23_recommendations_2026-08-07.csv` đã
   gắn cờ ADV3T của SCL = 1,30 tỷ < sàn 2 tỷ, nhưng `status` vẫn `WINDOW_PASSED` và lệnh vẫn đi.
   Vấn đề thật của SCL không phải "giá rơi 3,7%" mà là **gom một lượng lớn vào một mã mỏng** — đó
   là câu hỏi SIZING, và nó đã có cổng (`cap_lag_orders`) nhưng sàn ADV thì không.
2. **`due_diligence.py` không có trục "đã chạy xa sau rally"** — 5 trục hiện có (thanh khoản/định
   giá/PEAD/anomaly/FA) đều mù với "mã vừa +64,7% từ đáy YTD, đang sát đỉnh 7 tháng".

Cả hai là **việc riêng**, cần dispatch riêng và backtest riêng. **Tôi không tự mở rộng phạm vi**;
ghi ra đây để Mike quyết có mở không.

---

## §8 — Nếu user vẫn muốn có cơ chế này (đặc tả sẵn, CHƯA viết code)

Tôi **không** viết code vào `trading_bot/executor.py` cho một cơ chế mà dữ liệu đã bác — đúng luật
đội (`quant-skeptic REFUTED/INCONCLUSIVE ⇒ KHÔNG wire`) và §2/§3 coding_guidelines (không viết code
đầu cơ, không đụng module lõi khi không cần). Nếu user override, đây là đặc tả đã chốt để khỏi
thiết kế lại:

- **Field riêng** (§24), KHÔNG bẻ cong field khác: `PlannedOrder.buy_halt_drop_z` (float, chỉ
  `side="buy"`; `None`/rác ⇒ tắt, **không bao giờ nới**). Phải thêm vào `dataclasses.fields` —
  `load_plan()` lọc im lặng mọi key lạ (bẫy đã ghi ở §24).
- **Mốc neo `q.ref`** (prev-close) — lý do ở §4(a). KHÔNG dùng anchor (trip 25–43%).
- **Cưỡng chế MỘT chỗ**: đầu `_place_slices` cho mỗi `o`, trước khi tính giá:
  `if o.side=="buy" and q.last <= q.ref*(1 - z*rvol_20d): journal("BUY_HALT_DROP"); continue`.
  Nguồn `rvol_20d` = `self._gap_ref[ticker]["rvol_20d"]` (đã nạp sẵn), thiếu ⇒ **fail-safe = KHÔNG
  chặn** (đồng khuôn `_buy_chase_pct`).
- **Guard cuối** trong `_limit_price` sau mọi phép biến đổi giá (bài học §24 mục 2: `q.floor` có
  thể đẩy giá ra ngoài ràng buộc tính ở trên).
- **Chỉ dừng slice tiếp theo**, KHÔNG huỷ phần đã khớp; 2-poll confirm + cooldown như
  `_extreme_regime` để chống nhiễu quote; bus event + journal riêng.
- **Cờ mặc định OFF**, live-gate riêng.
- **Selfcheck bắt buộc** theo khuôn `hard_no_chase_ceiling_selfcheck.py`: mỗi ca "chặn được" phải
  có **ca chứng minh ngược** (bỏ cờ ⇒ thật sự mua tiếp).
- **§23 quét rộng**: `executor.py` là module lõi — `mike/bin/selfcheck_scope_map.sh
  trading_bot/executor.py` liệt kê **14 selfcheck** phụ thuộc (`book_tagging`, `capit_lever`,
  `capit_participation_cap`, `churn_guard`, `dcf_check`, `discretionary_participation_cap`,
  `extreme_regime`, `ghost_order`, `hard_no_chase_ceiling`, `hybrid_fill_timing`,
  `paper_main_window`, `refresh_skip_participation`, `t2_settlement`, `tick_retry`) — tất cả phải
  chạy lại. **Lần này chưa cần chạy vì không đụng file nào.**

---

## §9 — Giới hạn của kết luận này (nói trước, không để ai phải tự tìm ra)

1. **n=73 sự kiện / 49 ngày ở z=2,0.** CI đã tính theo cụm ngày và vẫn dương rõ, nhưng đây không
   phải mẫu lớn. Kết luận chắc ở **dấu**, không phải ở **mức** (+9,5% ± vài pp).
2. **Bar NGÀY, không phải tape trong ngày.** `low` là proxy cho "giá có chạm ngưỡng không" và bao
   gồm ATC; đường giá thật trong phiên không quan sát được. Đã kiểm bằng biến thể (b) §4.
3. **Không mô hình hoá được "mua ít hơn thì mua được gì khác"** — vốn không mua được giả định nằm
   tiền mặt (0%). Nếu vốn đó chảy sang tên khác trong sổ, chi phí của breaker **nhỏ hơn** con số
   trên, nhưng dấu không đổi (nền cũng chỉ +6,38%).
4. **Không phủ ca tin xấu thảm hoạ trong phiên** (khởi tố, gian lận, huỷ niêm yết). Mẫu 2014-2026
   của LAG không có ca nào như vậy rơi vào nhóm bị trip. Đây là **rủi ro tồn dư đã công bố**, và
   nó cũng chính là loại ca mà cổng cận-sàn (§6) — chứ không phải breaker vùng giữa — mới phủ được.
5. Rổ §3 (110 mã từ CSV gần đây) **có selection-bias về tên**; đã cố ý chỉ dùng nó cho thống kê
   **độ phân tán**, mọi kết luận **lợi nhuận** đều chạy trên tập PIT §4.
6. **Cột `capital%` trong §4 là CẬN TRÊN, không phải lượng vốn thật bị giữ lại.** Nó tính trọn
   `buy_amount` của cả lệnh trong ngày bị trip, trong khi breaker theo đặc tả §8 chỉ dừng **các
   slice CÒN LẠI** — phần đã khớp trước đó vẫn giữ. (quant-skeptic nêu đúng, vòng 1.) Điều này
   **không đổi dấu** kết luận: con số quyết định là lợi nhuận **trên mỗi tranche** tính từ
   `trip_px`, không phụ thuộc vào việc bao nhiêu phần trăm lệnh bị chặn. Nó chỉ có nghĩa: **mức
   thiệt hại** thực tế của việc wire breaker sẽ nhỏ hơn cột capital% gợi ý.

---

## §9b — Phản biện quant-skeptic

**CONFIRMED (high)** — `mike/logs/verify_20260810_071247_2783279.log`. Reviewer **tự chạy lại**
cả 4 script chính và **tự kéo lại bars SCL từ BigQuery**; mọi con số dẫn trong báo cáo tái lập
đúng tới độ chính xác đã trích (n=607/289/231, dose-response theo z, CI bootstrap, LOO 13/13,
bảng mốc neo, floor-guard 9,4%/+10,58%; SCL rvol 3,86% vs 3,87% do làm tròn, z=−0,96 khớp tuyệt
đối). 6/7 mục check `pass`, 1 mục `na` (capacity — finding này không đề xuất triển khai vốn mới).
`killer_objection` duy nhất = mục 6 ở trên, đã ghi nhận vào §9.

---

## §10 — Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_buy_circuit_breaker_20260810
export GOOGLE_APPLICATION_CREDENTIALS=/home/trido/thanhdt/WorkingClaude/secrets/sa-key.json
PY=/home/trido/thanhdt/wc_venv/bin/python
$PY pull_bars.py && $PY pull_lag_bars.py     # BQ → bars_universe.csv, bars_lag_audit.csv
$PY survey.py           # §3 khảo sát biến động
$PY dose_response.py    # §4 dose-response + IS/OOS
$PY stats_robust.py     # §4 bootstrap cụm ngày + LOO theo năm (seed 20260810)
$PY ref_choice.py       # §4(a) độ bền theo mốc neo
$PY tail_and_extreme.py # §5 đuôi trái + §6 cổng EXTREME sẵn có
```
Tất cả CHỈ ĐỌC; output nằm trong thư mục experiment (không đụng tên canonical, §8 guidelines).
