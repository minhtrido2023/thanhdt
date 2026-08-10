# LAG/BAL vs CAPIT — tham số thực thi có nên khác nhau theo book?

**Job** `Taylor_20260810_081824` · 2026-08-10 · Taylor
**Trạng thái**: NGHIÊN CỨU + ĐỀ XUẤT. **0 dòng code production bị sửa. Không có pending_ patch.**

---

## 0. Tóm tắt cho người quyết định

Câu hỏi chiến lược của user là **đúng và đáng làm** — và câu trả lời định lượng ủng hộ user.
Nhưng **chẩn đoán cơ học mà dispatch đưa xuống thì sai**, và nếu sửa theo chẩn đoán đó thì vừa
gỡ mất một luật user vừa duyệt hôm qua, vừa **không chạm** vào chỗ thật sự làm mất 173tr.

| | Dispatch nói | Đo thật |
|---|---|---|
| Nguyên nhân 0 fill hôm nay | `hard_no_chase_ceiling_vnd` (thêm 08-09) làm liệt lệnh | **Trần chạy ĐÚNG luật V2.4 user duyệt 08-09.** Hôm nay là **phiên 3** của cửa sổ entry — luật bắt buộc `≤ anchor` |
| Có bao nhiêu mã bị trần chặn | 3/4 (DRI, POW, SSI) | **SpaceX 3 mã** đúng. **ZaloPay 0 mã** — POW/SSI là `WAIT_CASH`, nguyên nhân khác hẳn |
| Tại sao vốn không giải ngân được | Trần quá chặt | **Phiên entry chuẩn 08-06 plan RỖNG (0 lệnh)** vì `park_trim` bị `BLOCKED_RECONCILE` (lệch sổ VHM) ⇒ chỉ còn 4,82tr tiền ⇒ cả 6 mã LAG `WINDOW_OPEN_DEFERRED` |

**Nhưng** — đo trên 4.618 sự kiện PEAD độc lập 2014-2026: luật `≤ anchor` ở phiên 2/3 **có
chọn lọc ngược thật**. Nhóm bị trần chặn lại là nhóm **tốt hơn +2,29pp** (t=2,82, p=0,005,
cụm theo ngày công bố). Nới trần lên `anchor × 1,03` cho **+0,84pp/sự kiện**, ổn định
**+0,61…+0,99pp** qua toàn bộ 13 leave-one-year-out.

**Đề xuất**: giữ nguyên cơ chế §24 trong `executor.py` (**không sửa 1 dòng nào**), chỉ đổi
**giá trị** mà plan generator ghi vào `hard_no_chase_ceiling_vnd` cho **riêng LAG phiên 2/3**.
CAPIT/discretionary **giữ nguyên**. Đây là sửa **luật**, cần **user duyệt** (§22).

---

## 1. Xác minh cơ học (Câu hỏi 1) — chẩn đoán của dispatch không đứng được

### 1.1 Không có một event `HARD_CEILING_BLOCK` nào

```
SpaceX  : WAIT_QUOTA 176 · REFRESH_SKIP 60 · PLACE 50 · FILL 24 · CANCEL_STALE 24 · HARD_CEILING_BLOCK 0
ZaloPay : PLACE_FAIL 944 · WAIT_CASH 315 · REFRESH_SKIP 46 · PLACE 30 · FILL 12 · HARD_CEILING_BLOCK 0
```

Trần **không chặn đặt lệnh**. Lệnh vẫn `PLACE` — chỉ bị **ghim tại đúng trần**. Bằng chứng
sạch nhất là tập giá `PLACE` phân biệt trong cả phiên:

| Mã | Giá đã đặt trong phiên | Kết quả |
|---|---|---|
| DRI | `13.000` (duy nhất) | 0 fill |
| POW | `13.400` (duy nhất) | 0 fill |
| SSI | `24.450` (duy nhất) | 0 fill |
| SCL | `24.200 → 23.700 → 23.600 → 23.400` | **fill 100%** @ 23.600 |

DRI/POW/SSI: **0 biến thiên giá** suốt phiên. SCL trượt **xuống** theo thị trường và khớp.
⇒ Cơ chế "bám giá" chỉ còn một chiều: **trượt xuống được, đi lên thì không**.

Lý do là số học, đọc thẳng từ plan: `ref_price == entry_anchor_price` **chính xác bằng nhau**
(13.000/13.400/24.200/24.450). Nên `cap = min(ref×(1+chase%), q.ceiling, hard) = hard` —
**băng chase sụp về 0**. Đây là *hệ quả* của luật phiên-3, không phải bug của §24.

### 1.2 Thị trường có thật sự nằm trên anchor không

Không lấy được quote DNSE trong phiên headless này (`get_quote_source` cần credential —
`secdef/latest_trade/latest_quote` đều trả `NoneType`). **Không dùng BQ thay thế** (§6: BQ chưa
sync tối nay). Suy luận từ chính sổ lệnh, đủ chắc cho POW:

> Lệnh mua giới hạn **13.400**, khối lượng 2.800cp, **nằm trên sổ suốt phiên**, mã có
> **ADV3T 113,49 tỷ/phiên**, và **0 fill**. Với thanh khoản đó, nếu thị trường có in giá
> ≤13.400 thì lệnh đã khớp. ⇒ **giá thấp nhất phiên của POW nằm trên 13.400.**

DRI (ADV 5,37 tỷ) và SSI cùng chữ ký. Đây là **suy luận từ artifact**, không phải quote trực
tiếp — ghi rõ để ai đọc sau không trích nhầm thành số đo.

### 1.3 ZaloPay: nguyên nhân HOÀN TOÀN khác, không liên quan trần

```
WAIT_CASH  BUY-POW-LAG-02  thiếu tiền — sức mua broker 142 cp < 1800
WAIT_CASH  BUY-SSI-LAG-04  thiếu tiền — sức mua broker  78 cp <  800
```

Và lý do thiếu tiền: **8 lệnh bán PARK (nguồn vốn JIT-unpark) fail 944 lần**:

```
PLACE_FAIL  SELL-VCB-PARK-06  VCB sell 700 @59.900  HTTP 400: deal not found
```
118 lần × 8 mã (BID, CTG, HDB, MBB, TCB, VCB, VHM, VPB).

⇒ **`HTTP 400: deal not found` là một sự cố vận hành riêng, chưa được ai xử lý.** Gộp nó vào
"lỗi trần giá" sẽ chôn luôn một bug thật. **Đề nghị escalate riêng cho Mafee/ops.**

---

## 2. Vì sao hôm nay đã là PHIÊN 3 — đây mới là chỗ mất 173tr

Luật V2.4 (`mike/bin/filter_lag_entry_window.py`, user duyệt 2026-08-09):
> 1. Cửa sổ entry = phiên chuẩn (Release_Date+5) và **hai phiên kế tiếp**.
> 2. Trong **phiên 2/3**, chỉ được vào nếu giá live **không vượt `entry_anchor_price`**. Không average-up.
> 3. Hết phiên 3 → `WINDOW_PASSED`, không catch-up. **Ngày thoát vẫn neo theo lịch entry chuẩn.**

Chạy lại script cho hôm nay:
```
entry_date 2026-08-06 · entry_window_day 3 · requires_anchor_price true
execution_mode RESIDUAL_OR_NEW_AT_OR_BELOW_ANCHOR
```
**Trần đã làm đúng việc của nó.** Vấn đề là *tại sao ta còn ở phiên 3 mà chưa có vị thế*:

| Phiên | Ngày | Điều gì xảy ra |
|---|---|---|
| **1 (chuẩn)** | **08-06** | `plan_SpaceX` + `plan_ZaloPay` đều có **0 lệnh**. `park_trim_proposal.decision = BLOCKED_RECONCILE` — sổ nội bộ VHM 500cp vs broker 1000cp ⇒ **không sinh lệnh trim nào** ⇒ `cash_available_vnd = 4.821.143` ⇒ cả 6 mã LAG `WINDOW_OPEN_DEFERRED`, `deferred_total = 674.145.232` |
| 2 | 08-07 | park_trim chạy lại được, nhưng plan **chỉ có DRI**. SSI (phiên chuẩn của *chính nó*) cũng không lên plan. DRI dính `GHOST_ORDER` 14:06 ⇒ dừng mã |
| 3 | 08-10 | Lần đầu đủ 4 mã lên plan — nhưng phiên 3 ⇒ trần anchor ⇒ 0 fill |

Trích thẳng plan 08-06 (`lag_analysis`):
> `"decision": "ĐỦ ĐIỀU KIỆN vào lệnh nhưng THIẾU TIỀN → deferred_orders[]. Không phải SKIP."`

**Vốn bị đóng băng ở đúng phiên duy nhất được phép mua theo giá thị trường.** Trần giá là quân
domino cuối, không phải quân đầu. Nới trần mà không sửa đường cấp vốn thì lần sau lặp lại y hệt.

*(Ghi chú §25: plan 08-06 dùng `availableCash` 4.821.143 trong khi `totalCash` = 14.596.297
— thiếu 9,78tr `cashDividendReceiving`. Đúng loại bug §25, nhưng **không phải nguyên nhân**:
9,78tr không cứu nổi nhu cầu 674tr.)*

---

## 3. Chi phí cơ hội của vào lệnh trễ (Câu hỏi 2) — đo thật

**Thiết kế** (`exp_lag_entrylag_20260810/measure_entry_lag.py`). Tập sự kiện **sao y engine
production** `pt_v23_audit_2014.py`: `NP_R≥15 ∧ prior_n_good≥4 ∧ pa_HL3≥5`, forensic gate ON,
entry = Release_Date+5 phiên, **hold 25 phiên neo theo lịch chuẩn** (đúng luật 3 — vào trễ vừa
mất drift đầu, vừa bị rút ngắn thời gian nắm). Lợi nhuận trên `Close` (đã điều chỉnh cổ tức);
cổng chặn trên `Price` (giá thô) — **đúng cơ sở mà `lag_entry_anchor.py` sinh anchor live**.
Không dùng `profit_*` (§2 no-look-ahead).

**N = 4.618 sự kiện độc lập** (771 mã, 544 ngày công bố, 2014-2026).

| Phiên | Nhánh | fill% | ret \| fill | **ret × fill (trên vốn)** |
|---|---|---:|---:|---:|
| 1 (e+0) | vào ngay | 100,0% | 4,06% | **4,06%** |
| 2 (e+1) | CHASE | 100,0% | 3,72% | 3,72% |
| 2 (e+1) | ANCHOR *(luật nay)* | 62,9% | 2,95% | **1,86%** |
| 3 (e+2) | CHASE | 100,0% | 3,37% | 3,37% |
| 3 (e+2) | ANCHOR *(luật nay)* | 56,5% | 2,15% | **1,22%** |

**Hai chi phí tách bạch rõ:**
- **Suy giảm tín hiệu thuần** ≈ **−0,35pp/phiên** (4,06 → 3,72 → 3,37). Nhỏ.
- **Chi phí của luật `≤ anchor`** = 3,37% − 1,22% = **−2,15pp ở phiên 3**. **Lớn gấp ~3 lần**
  chi phí trễ. Vì nó không fill 43,5% số ca.

### 3.1 Phát hiện quan trọng nhất: trần anchor CHỌN LỌC NGƯỢC

| Phiên | Nhóm ĐƯỢC PHÉP (giá ≤ anchor) | Nhóm **BỊ CHẶN** (giá đã chạy) | Chênh |
|---|---|---|---|
| 2 | n=2.904 · **+2,95%** | n=1.714 · **+5,02%** | **+2,07pp** *(t=−3,16, p=0,0016)* |
| 3 | n=2.608 · **+2,15%** | n=2.010 · **+4,95%** | **+2,79pp** *(t=−4,06, p=5,0e−05)* |

Cụm theo ngày công bố (N đúng = 347 cụm, không phải 4.618 dòng): chênh **+2,29pp**,
**t=2,82, p=0,005**. Kết luận sống sót qua clustering.

> **Trần anchor lọc GIỮ những mã tụt về dưới giá phiên chuẩn (đà yếu) và lọc BỎ những mã tiếp
> tục chạy (đà xác nhận).** Với một sổ PEAD — vốn kiếm tiền từ *under-reaction rồi drift tiếp*
> — giá đi lên sau công bố **chính là tín hiệu đang đúng**, không phải lý do để tránh.

Ca SCL hôm nay là minh hoạ sống: mã **duy nhất khớp 100%** là mã **rơi −3,3% trong phiên**.

---

## 4. Giá phải trả để đổi lấy fill (Câu hỏi 3)

`exp_lag_entrylag_20260810/design_bounded_chase.py` — trần = `anchor × (1+cap)`:

**Phiên 3 (k=2), N=4.618:**

| Trần dưới | fill% | ret\|fill | **trên vốn** | vs luật nay | số năm thắng |
|---|---:|---:|---:|---:|---:|
| **anchor +0% (luật nay)** | 56,5% | 2,15% | **1,22%** | — | — |
| anchor +1% | 64,7% | 2,47% | 1,60% | +0,38pp | 10/13 |
| anchor +2% | 73,0% | 2,56% | 1,87% | +0,65pp | 12/13 |
| **anchor +3%** | **79,4%** | **2,59%** | **2,06%** | **+0,84pp** | **11/13** |
| anchor +4% | 84,1% | 2,73% | 2,30% | +1,08pp | 12/13 |
| anchor +5% | 87,3% | 2,77% | 2,41% | +1,20pp | 11/13 |
| anchor +8% | 93,6% | 2,99% | 2,80% | +1,58pp | 11/13 |
| không giới hạn | 100,0% | 3,37% | 3,37% | +2,15pp | 11/13 |

**Leave-one-year-out cho `anchor +3%`** (kiểm tra reshuffle-luck theo §KNOWLEDGE §8):

| Bỏ năm | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Chênh còn lại | +0,84 | +0,87 | +0,83 | +0,83 | +0,87 | +0,89 | +0,81 | **+0,61** | +0,99 | +0,85 | +0,79 | +0,87 | +0,90 |

Toàn mẫu +0,84pp; **mọi LOO nằm trong +0,61…+0,99pp**. Bỏ 2021 (năm đóng góp lớn nhất) vẫn
+0,61pp. **Không có năm nào gánh edge** — khác hẳn chữ ký reshuffle-luck mà KB cảnh báo. Chỉ
2 năm âm, đều nhỏ và đều trong thị trường xuống: 2022 (−0,18pp), 2026 YTD (−0,22pp).

---

## 5. Đề xuất — tham số thực thi phân hoá theo book (Câu hỏi 4 & 5)

### 5.1 Thực ra hệ ĐÃ phân hoá — chỉ 1 chỗ sai

| Book | Trần cứng hiện tại | Đề xuất | Vì sao |
|---|---|---|---|
| **LAG phiên 1 (chuẩn)** | không có | **giữ nguyên** | Vào theo giá thị trường, đúng rồi |
| **LAG phiên 2/3** | `= anchor` | **`= anchor × 1,03`** | §3.1: trần hiện tại chọn lọc ngược, −0,84pp/sự kiện |
| **BAL** (momentum V11) | không có | **giữ nguyên** | Entry T+1, không có luật anchor. Không có gì hỏng |
| **CAPIT** (bear-washout) | `= anchor` | **giữ nguyên** | Mua-khi-rẻ *là* chiến lược. Kiên nhẫn ĐÚNG |
| **DISCRETIONARY** (fear-buy) | `= anchor` | **giữ nguyên** | Như trên. Doctrine "no-chase là bất biến" của chính nó |

⇒ Không cần cơ chế mới, không cần field mới, **không đụng `urgency`**.
`urgency="high"` là công tắc thô (bypass mọi passive logic ở 3 chỗ trong `executor.py`) — sai
công cụ cho một vấn đề chỉ là *sai giá trị của một tham số*.

### 5.2 Sửa ở đâu — KHÔNG phải `executor.py`

**Cơ chế §24 trong `executor.py` là đúng và nên giữ nguyên tuyệt đối.** 3 lỗ hổng nó vá
(`max(px, q.floor)` đẩy vượt anchor; mẹo `anchor/1,04` giả định chase cap 4%; `_atc_sweep`
không đặt được giá) đều **vẫn còn thật** và không liên quan gì tới việc trần nên bằng bao nhiêu.

Thay đổi duy nhất: **giá trị** mà tầng sinh plan ghi vào `hard_no_chase_ceiling_vnd` cho LAG
phiên 2/3 — `= entry_anchor_price × 1,03` thay vì `= entry_anchor_price`, và `ref_price` trả về
**giá tham chiếu sống thật** để `max_chase_pct_buy`/`chase_cap_vol_scale` cũng bó cùng lúc
(hai lớp bó độc lập, lấy min).

**Hệ quả về phạm vi kiểm thử (§23)**: 0 sửa `executor.py` ⇒ **không phải quét rộng 11 selfcheck**.
Đúng phạm vi cần chạy: `hard_no_chase_ceiling_selfcheck.py` (50 ca) +
`filter_lag_entry_window_selfcheck.py`. Xác nhận bằng `bin/selfcheck_scope_map.sh`, không đoán.

⚠️ `load_plan()` chỉ giữ key có trong `dataclasses.fields(PlannedOrder)` và **im lặng bỏ phần
còn lại** (§24). Phải verify bằng `load_plan()` thật, **không đọc JSON**.

### 5.3 Vì sao +3% chứ không phải "bỏ hẳn trần" (mạnh hơn +2,15pp)

Cố ý **không** chọn argmax:
1. Bỏ trần = mở lại đúng lớp lỗ hổng §24 vừa vá hôm qua (`q.floor` đẩy giá vượt anchor).
2. +3% giữ nguyên **bất biến kiểm toán được**: "không bao giờ trả quá 3% trên giá phiên chuẩn".
3. +3% xấp xỉ trần chase động sẵn có `clamp(2×rvol_20d; 1,5%; 4%)` — **dùng lại máy móc đã có**,
   không đẻ thêm tham số tự do.
4. Chọn theo *lý do cơ chế*, không theo đỉnh backtest ⇒ giảm hẳn rủi ro overfit. Chấp nhận bỏ
   lại ~1,3pp trên bàn để đổi lấy một trần chặn được sự cố.

### 5.4 Điều kiện GO — chưa đủ để wire

| # | Cổng | Trạng thái |
|---|---|---|
| 1 | **User duyệt** — sửa luật V2.4 rule 2 user vừa chốt 08-09 (§22: quyết định CHÍNH SÁCH) | ⛔ **CHƯA** |
| 2 | Backtest NAV thật (`pt_v23_audit_2014.py`), self-check 0 VND, IS 2014-19 / OOS 2020+ | ⛔ chưa chạy |
| 3 | quant-skeptic CONFIRMED | ⛔ chưa |
| 4 | Paper rehearsal 1 phiên | ⛔ chưa |
| 5 | Sửa đường cấp vốn phiên 1 (§2) — **độc lập và ưu tiên cao hơn** | ⛔ chưa |

**Giới hạn lớn nhất của nghiên cứu này — phải đọc trước khi trích số:** đây là **event-study,
không phải NAV backtest**. Nó **chưa tính ràng buộc vốn**. Registry (audit H8) ghi sổ LAG
**oversubscribe ~6×, bind 92% số entry** — nếu tiền mới là ràng buộc thật, fill thêm mã **không
tạo thêm vốn**, chỉ đổi *mã nào được cấp vốn*. Chọn-lọc-ngược (§3.1) vẫn đúng trong trường hợp
đó (ta đang chọn nhóm tệ hơn), nhưng **biên độ trên NAV gần như chắc chắn nhỏ hơn +0,84pp**.
⇒ **Không trích +0,84pp như CAGR.** Cổng 2 tồn tại chính vì lý do này.

---

## 6. Việc cần làm ngay, không phụ thuộc quyết định trên

1. **`HTTP 400: deal not found`** — 944 PLACE_FAIL trên 8 lệnh bán PARK của ZaloPay hôm nay.
   Đây là lý do POW/SSI ZaloPay không có tiền. → **Mafee/ops**.
2. **Lệch sổ VHM** (ledger 500 vs broker 1000) làm `park_trim` BLOCKED_RECONCILE ngày 08-06 —
   đã escalate 08-05, **hệ quả thật là mất phiên entry chuẩn của 6 mã LAG**. Cần xác nhận đã đóng.
3. **Khe hở quy trình**: `park_trim` bị block ⇒ LAG mất phiên entry chuẩn, **không có cảnh báo
   nào nối hai việc đó**. Plan 08-06 ghi đúng "THIẾU TIỀN → deferred" rồi im. Nên có escalation
   khi `deferred_orders` chứa LAG **ở đúng phiên chuẩn** (mất phiên này là mất **không phục hồi
   được**: phiên 2/3 bị trần anchor, hết phiên 3 là `WINDOW_PASSED`).

---

## Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude
/home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/exp_lag_entrylag_20260810/measure_entry_lag.py
/home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/exp_lag_entrylag_20260810/design_bounded_chase.py
```
Artifact: `exp_lag_entrylag_20260810/exp_lag_entry_lag_events.csv` (4.618 sự kiện).
Tên `exp_*` theo §8/§23 — **không phải** canonical, không pin vào `results_registry.md`.
