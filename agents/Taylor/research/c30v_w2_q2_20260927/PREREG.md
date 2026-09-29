# PREREG — W2 / Q2 của `kb/projects/custom30v-revalidation-plan-20260927.md`

> Job `Taylor_20260927_141318`. **Ghi TRƯỚC log đầu tiên** (§3.3 kế hoạch). PAPER-ONLY:
> không re-pin, không đổi rail, không đổi `trading_rules.json`, không merge.
> Mọi tiêu chí dưới đây **KHÔNG được đổi sau khi thấy số**.

## 0. Câu hỏi

Trong 4 "phương tiện park" {A=custom30V, B=custom30, C=rổ tập trung theo quy tắc k∈{6,10}} và
D = **không park** (tiền nhàn rỗi ăn carry theo proxy), phương tiện nào thắng theo tiêu chí đã khai
báo trước — khi tiền nhàn rỗi KHÔNG còn giả định 0%/năm?

## 1. Tiêu chí chọn (đăng ký trước)

| | Tiêu chí |
|---|---|
| **Chính** | **E[Calmar]** từ paired block bootstrap — `L=21`, `B=4000`, `seed=12345`, đúng khuôn `research/park_fraction_grid_20260927/paired_v2.py` (một chuỗi block-index dùng cho MỌI chân ⇒ cùng một "thế giới resample" ở mọi cấu hình). |
| **Tie-break** | Ứng viên **ÍT TẬP TRUNG hơn** thắng (thứ tự tăng dần độ tập trung: D → A(30 tên, cap 0,10) → B(30 tên) → C10 → C6). "Ít tập trung hơn" = nhiều tên hơn / cap chặt hơn. |
| **Cổng DD (bắt buộc, prereg v2)** | `DD5th(X) ≥ DD5th(park=0) − 2,0pp`. Chân trượt cổng này **bị loại**, kể cả khi E[Calmar] cao nhất. `DD5th` = phân vị 5 của MaxDD trên B=4000 đường bootstrap. |
| **Cổng "C có edge"** | C chỉ được gọi là **có edge** nếu chuỗi return **standalone** của rổ C vượt **phân vị 90** của null-300 (300 draw ngẫu nhiên k tên từ CÙNG pool). Vượt trung vị là KHÔNG đủ. |
| **Cổng robustness** | IS 2014-19 / OOS 2020+ (báo cả hai); leave-one-year-out; DSR + PBO với `DSR_FAMILY_MANIFEST` GHIM (không glob động). Edge rớt OOS ⇒ nêu rõ là rớt, không trung bình hoá. |
| **Tầng proxy** | Kết luận phải đứng ở **tầng 1 (baseline)** VÀ **không đảo dấu ở tầng 2 (floor)**. Chỉ thắng ở tầng 3 (spot 8,543%) ⇒ ghi "phụ thuộc khuyến mãi DNSE", KHÔNG dùng để kết luận (tier `spot` không được chạy trong W2). |

**Không kết luận giữ/bỏ custom30V.** Đó là quyết định của user (Q3/W3). W2 chỉ trả lời: ai thắng
theo tiêu chí trên, ở tầng 1, và có đảo dấu ở tầng 2 hay không.

## 2. Ứng viên — định nghĩa VẬN HÀNH (env, không phải văn xuôi)

Tất cả dùng NGUYÊN VĂN lệnh pin anchor R3 (job `Taylor_20260927_131635`), chỉ đổi các biến ghi rõ:

```
WC=<worktree>/WorkingClaude ; $DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate  BQ_CACHE_THREADS=1
BASKET_CA_SNAPSHOT=$WC/data/snapshots/corp_action_share_20260927.parquet
NAV_TOTAL_B=50  ETF_LIQ=custompitg  AUDIT_END=2026-06-19
pt_v23_audit_2014.py v23a none postbull 0 edge
```

| Nhãn | BASKET_SELECT | BASKET_WT | BASKET_TOPN | PARK_STATES |
|---|---|---|---|---|
| **A** custom30V (production) | `yieldcombo` | `namecap` (cap 0,10) | 30 | `3:0.3` |
| **B** custom30 | `blend` | `namecap` | 30 | `3:0.3` |
| **C6** tập trung k=6 | `v3route3` | `ew` | 6 | `3:0.3` |
| **C10** tập trung k=10 | `v3route3` | `ew` | 10 | `3:0.3` |
| **D** không park | `yieldcombo` (trơ) | `namecap` | 30 | `3:0.0` |

**Ánh xạ C → `v3route3`, khai báo trước:** kế hoạch §3.1 định nghĩa C = "composite v3 + tier A/B
của route". `BASKET_SELECT=v3route3` là **arm tham chiếu** của họ v3 đã có trong `custom_basket.py`
(composite ey/cfy/ps theo route-percentile, route TÀI CHÍNH chuyển sang `value_score_v2` của
`rating_8l` rồi quantile-match về phân phối điểm non-financial ⇒ arm DUY NHẤT trong 3 arm có thang
điểm so sánh được cross-route). Pool của nó ĐÚNG như kế hoạch yêu cầu: `in_universe` ∧ golden floor
(`pb_z≤−1` ∧ `ROE_Min3Y≥0` ∧ `CF_OA_3Y>0`) ∧ `gate_rating=3` ∧ `!banned` — cùng pool custom30V dùng.
⚠️ Ghi rõ **giới hạn diễn giải**: cụm "tier A/B" trong kế hoạch không khớp một field code nào;
diễn giải ở đây = phân tầng theo ROUTE (`v3route3`). Nếu user có ý khác thì đây là chân phải chạy lại.
**KHÔNG dùng 4 tên FPT/ACB/MBB/HDB** (hindsight, N hiệu dụng = 1).

### 2b. park = 0,0 là ĐIỂM SUY BIẾN — khai báo trước
Ở `PARK_STATES=3:0.0` KHÔNG có tiền nào vào rổ ⇒ phương tiện trở nên trơ, nên
`A@0,0 ≡ B@0,0 ≡ C6@0,0 ≡ C10@0,0 ≡ D`. Vì vậy cột "park 0,0" của bảng cuối là **MỘT chân duy nhất
(D)**, không phải 4 chân. Điều này được **CHỨNG MINH**, không giả định: chạy thêm `B@park0,0` và
`cmp` ledger với `D` (kỳ vọng byte-identical). Lệch ⇒ có rò rỉ phương tiện ngoài đường park ⇒ DỪNG.

## 3. Đưa lãi tiền nhàn rỗi vào khuôn đo — chọn phương án **(a)**, có knob env

**Chọn (a) — knob trong engine. KHÔNG chọn (b) overlay hậu kiểm.** Ba lý do, theo thứ tự quan trọng:

1. **`simulate()` ĐÃ có sẵn tham số `deposit_annual`** (`simulate_holistic_nav.py:373`, mặc định
   `0.0`), áp mỗi phiên tại bước 4 (`cash *= 1 + deposit_annual/252`, dòng 880-881), **chỉ trên
   `cash > 0`** — mà `cash` ở đây chính là tiền **CHƯA park** (phần đã park nằm ở `cash_etf`/lô rổ,
   do bước 6b "ETF POST-FILL SWEEP" chuyển ra). Interest được ghi vào cột `interest` và **đã nằm
   trong cash-flow self-check** (`pt_v23_audit_2014.py:2276`). Nghĩa là khuôn kế toán 0-VND đã hỗ
   trợ carry từ trước; việc còn lại chỉ là cho `deposit_annual` biến thiên theo ngày. Thay đổi mã
   nguồn vì thế là **nhỏ nhất có thể** — không dựng cơ chế mới.
2. **Carry PHẢI cộng dồn vào vốn và ảnh hưởng sizing.** Ở chân D (không park), tiền nhàn rỗi là
   phần lớn NAV; carry của nó làm NAV lớn hơn ⇒ lệnh sau to hơn. Overlay hậu kiểm (nhân chuỗi
   return NAV với carry) **không** truyền hiệu ứng đó vào sizing, nên **hệ thống hạ thấp chân D** —
   tức là làm lệch ĐÚNG cái trục đang được đo (park vs không park). Đây là lý do quyết định.
3. Ledger CÓ tách được tiền chưa park (`bal_cash_ref`+`lag_cash_ref` vs `bal_etf_ref`+`lag_etf_ref`),
   nên (b) là **khả thi** — nhưng khả thi không phải là đúng, xem (2). (b) sẽ được dùng CHỈ như một
   phép đối chiếu bậc 1 trong REPORT, không phải nguồn số kết luận.

**Knob:** `IDLE_CARRY_TIER ∈ {off (mặc định), baseline, floor}`.
- `off` ⇒ truyền `deposit_annual=0.0` y như hiện tại ⇒ **PHẢI byte-identical anchor**.
- `baseline`/`floor` ⇒ truyền một `pd.Series` theo ngày, dựng từ
  `idle_rate_proxy.r_idle_series(dates, tier)` (W1 đã chốt, PIT: mốc tháng T chỉ dùng từ đầu tháng T+1).
- Filename tag `_idle<tier>` (§8: trục đổi số ⇒ đổi tên file). Mọi chân W2 còn thêm `EXP_TAG`.

**Quy ước tích lãi:** giữ NGUYÊN `/252` mỗi phiên của engine (không đổi sang day-count/365) để
thay-đổi-mã chỉ là scalar→Series. Hệ quả đã biết và chấp nhận: cửa sổ có ~249,4 phiên/năm nên carry
bị tích thiếu ~0,4% **tương đối** (vd 5,00%/năm thực nhận ≈ 4,98%) — bậc nhỏ hơn 2 bậc so với
khoảng cách tầng 1 ↔ tầng 2. Ghi vào REPORT §giới hạn.

**Cổng bắt buộc trước khi đọc BẤT KỲ số nào:**
1. **Control leg** = A@park0,3, `IDLE_CARRY_TIER=off` ⇒ ledger md5 **`4707bcbeb7e801d49a4a851ffd91d5e7`**,
   `cmp` sạch với ledger đang pin. **Không tái lập được ⇒ DỪNG, ghi bus, không đọc số.**
2. `self-check 0 VND` cả 4 chân (cash-flow identity BAL+LAG, final-NAV identity, borrow-audit) trên
   MỌI chân, kể cả chân có carry.
3. `basket_return_leg_oshares_selfcheck.py` PASS + tự kiểm đòn 8 quant-skeptic (double-count
   corp-action) cho MỖI chuỗi return rổ, **TRƯỚC** khi đọc số.

## 4. Null-300 cho C

300 draw ngẫu nhiên k tên từ **CÙNG pool** (`in_universe` ∧ `pass_golden_floor` ∧ `rating_8l≤3` ∧
`!banned`, theo quarter của `universe_pit_q`), EW, reshuffle mỗi quý — khuôn `conc_tail.py` (Job U),
`R=300`, `SEED=20260927`. Báo trung vị / p90 / phân vị 5 của CAGR và MaxDD. **C so với p90.**

## 5. Bảng cuối (cấu trúc cố định trước khi có số)

Mỗi ứng viên × {park 0,30; park 0,0 (= D)} × {tầng 1 baseline; tầng 2 floor}:
`CAGR / Sharpe / MaxDD / Calmar / E[Calmar] / P(X>D) / DD5th`.

## 6. Ghi nhận, KHÔNG làm trong W2

Chân **TRỌNG SỐ** `custom_basket.py:544` (`mcapw = pxw × OShares`) chưa được audit (replay job
`Taylor_20260927_101335` finding 4). Ghi vào REPORT §giới hạn; đề xuất A/B riêng
`BASKET_OSHARES_STEP` sau W2.
