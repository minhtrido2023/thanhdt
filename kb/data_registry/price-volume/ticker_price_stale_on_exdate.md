---
kind: bigquery-column
status: TRAP
source: tav2_bq.ticker.Price (và tav2_bq.ticker_prune.Price) — dòng ĐÚNG NGÀY GDKHQ
group: price-volume
scope: mọi code lấy giá lịch sử một phiên cụ thể từ ticker/ticker_prune (neo giá, trần đuổi giá, sizing, ADV cap)
writer: Ingest ETL nightly (append-only, KHÔNG back-correct)
---

# `tav2_bq.ticker.Price` có thể ĐỨNG YÊN ở hệ quy chiếu CŨ đúng ngày GDKHQ

**Status: TRAP.** Bổ sung cho [`ticker_close_vs_price_dividend_adj.md`](ticker_close_vs_price_dividend_adj.md)
— file đó nói `Price` là "giá THÔ, đúng giá thật khớp trên sàn phiên đó, không hồi tố". Câu đó
**đúng ~98% số ca nhưng SAI đúng vào ngày GDKHQ của ~2% sự kiện**, và ca sai nặng nhất đo được là
một blue-chip HOSE. Điều tra: job `Winston_20260815_064023`, phát hiện gốc từ
`Taylor_20260815_054822` (`agents/Taylor/research/exdate_order_pipeline_20260815/README.md` §1.1).

## Luật một dòng

> **Không bao giờ coi `ticker.Price` / `ticker_prune.Price` của DÒNG NGÀY GDKHQ là giá thật của
> phiên đó.** Nó có thể là giá phiên T−1 bị chép nguyên (hệ CUM), tức sai đúng bằng TOÀN BỘ hệ số
> quyền. Cần giá thô của đúng phiên GDKHQ ⇒ dùng `ticker_1m.Price` (nếu còn trong cửa sổ ~1 tháng),
> hoặc `Close` của chính dòng đó (từ ex-date trở đi hệ số điều chỉnh = 1 nếu chưa có sự kiện mới),
> hoặc DNSE API.

## Bằng chứng ca gốc — VHM 2026-08-06 (query BQ LIVE ngày 2026-08-15)

Sự kiện (`tav2_bq.corporate_action`): `event_code=ISS` "Phát hành cổ phiếu",
`exright_date=2026-08-06`, `exercise_ratio=1.0` (1:1 ⇒ hệ số **2,0**), source fiinpro,
`ingested_at=2026-08-12 15:24:01`.

`SELECT t.time,t.Open,t.High,t.Low,t.Close,t.Price,t.Volume FROM tav2_bq.ticker AS t WHERE t.ticker="VHM" ...`

| time | Open | High | Low | Close | **Price** | Volume | Price/Close |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-08-04 | 74.100 | 76.650 | 73.400 | 76.450 | 152.900 | 6.362.273 | 2,0000 |
| 2026-08-05 (cum cuối) | 77.100 | 79.400 | 76.500 | 76.500 | 153.000 | 10.722.235 | 2,0000 |
| **2026-08-06 (GDKHQ)** | 81.700 | 81.700 | 76.800 | **77.100** | **153.000** | **16.902.474** | **1,9844** |
| 2026-08-07 | 75.300 | 76.800 | 73.000 | 73.000 | 73.000 | 9.164.067 | 1,0000 |

Ba điểm chốt, không cần nguồn ngoài:
1. **153.000 = Price của 08-05 y hệt từng đồng** ⇒ giá trị bị **chép nguyên từ T−1**, không phải
   kết quả của một phép nhân hệ số nào (77.100 × 2 = 154.200 ≠ 153.000).
2. **153.000 nằm NGOÀI dải giá của chính phiên đó** `[Low 76.800 – High 81.700]` ⇒ về mặt số học
   nó **không thể** là giá khớp của phiên 08-06. Đây là bằng chứng tự chứa, không cần đối chiếu
   nguồn thứ hai.
3. **`ticker_1m` cùng ngày cùng mã lại ĐÚNG** (xem dưới) ⇒ giá đúng có tồn tại ở upstream; chỉ
   `ticker`/`ticker_prune` giữ bản cũ.

Sai số: **+98,4%** so với giá thật (153.000 vs 77.100).

## Ba bảng KHÔNG đồng ý với nhau (đây là chìa khoá nguyên nhân)

| Bảng | VHM 2026-08-06 `Price` | Đúng? |
|---|---:|---|
| `tav2_bq.ticker` | 153.000 | ❌ hệ CUM (T−1) |
| `tav2_bq.ticker_prune` | 153.000 | ❌ (kế thừa `ticker`) |
| **`tav2_bq.ticker_1m`** | **77.100** | ✅ đúng giá phiên |

`Close` của cả ba bảng đều = 77.100 (khớp nhau) — **chỉ cột `Price` lệch**.

## Nguyên nhân (cơ chế suy ra từ artifact — CHƯA có xác nhận của bq_admin)

`ticker`/`ticker_prune` là bảng **append-only ghi một lần mỗi phiên và không bao giờ đọc lại để
sửa** cột `Price`. Đúng tối ngày GDKHQ, feed upstream vẫn còn phục vụ giá tham chiếu **CUM** (đúng
cửa sổ lật hệ quy chiếu ~19:10 ICT mà Taylor đo trên broker DNSE — `exdate_order_pipeline_20260815`
§3), nên dòng ghi ra mang giá T−1 và **đứng yên vĩnh viễn** ở đó. `ticker_1m` là **rolling snapshot
rebuild toàn bộ mỗi ngày** ⇒ lần rebuild sau nhặt được giá trị đã đúng của vendor.

Bằng chứng ủng hộ: đo tại 2026-08-15, tức **9 ngày sau** sự kiện — giá trị sai vẫn còn nguyên
trong `ticker`. **Nó KHÔNG tự lành.**

Đây là **lỗi ingest sporadic, KHÔNG phải quy ước cố ý**: 98,0% ex-date có bước điều chỉnh thật lại
hoàn toàn đúng (bảng dưới). Một quy ước thì phải nhất quán 100%.

❓ **Câu cần bq_admin xác nhận** (chưa hỏi được từ phiên headless này): (a) `ticker.Price` lấy từ
field nào của vendor và chốt lúc mấy giờ? (b) có job back-correct nào cho cột này không, hay
append-only vĩnh viễn? (c) có backfill được 42 dòng đã liệt kê không?

## Quy mô — quét toàn bộ 2024-01-01 → 2026-08-15

Detector: với mỗi `(ticker, exright_date)` DISTINCT trong `tav2_bq.corporate_action`, đặt
`r_t = Price_t / Close_t`; chỉ xét sự kiện có **bước điều chỉnh thật** (`|r_prev/r_next − 1| > 2%`);
dòng ex-date ĐÚNG nếu `r_ex ≈ r_next` (đã ở hệ mới).

| Phân loại | Số dòng | Tỉ lệ | Trong đó `Price[ex] == Price[ex−1]` tuyệt đối |
|---|---:|---:|---:|
| `OK_new_regime` — đúng | 2.033 | **98,0%** | 42 |
| `STALE_old_regime` — `r_ex ≈ r_prev`, kẹt hệ cũ | 11 | 0,5% | 10 |
| `OTHER` — lệch cả hai | 31 | 1,5% | 16 |
| **Tổng lệch** | **42** | **2,0%** | 26 |

**Gần như toàn bộ 42 ca là mã cực mỏng thanh khoản** (Volume phiên đó 0–100k cp, phần lớn UPCOM:
BTT, TTD, CMN, BSQ, ITD, F88, TV1, TNW, GCF, BTH, TLP, LPT, VAB, MVC, BSP, PRC, KCE, STC, SFI,
DHP, HC3, CMW, BSH, POS, VBB, PSN, HDW, BPC, VIH, BDW, QPH, MED, TLT, PTD, VGL, MCM, THS, SBM,
S4A, NAV, DM7 …). **VHM 2026-08-06 là ca thanh khoản cao DUY NHẤT** — và cũng là ca sai lớn nhất.

Kiểm chéo bằng đường thứ hai (diff `ticker` vs `ticker_1m` trên cửa sổ chồng lấn 2026-07-10 →
08-15, 18.817 dòng): **60 dòng lệch `Price` (0,32%)**; trong đó **đúng 1 dòng có Volume ≥ 100.000**
và **đúng 1 dòng lệch > 50%** — cả hai đều là VHM 2026-08-06. 59 dòng còn lại là mã mỏng, lệch nhỏ,
đa số **không phải** ngày GDKHQ (hiện tượng khác: phiên không có khớp ⇒ `Price` giữ giá khớp cuối).

### ⚠️ Cái bẫy của chính detector — đừng dùng bản thô

Tỉ lệ "`r_t` lệch `r_{t+1}` > 2%" đo trên **dòng ex-date là 2,372%**, trên **dòng thường là 2,338%**
— **bằng nhau**. Nghĩa là nếu bỏ điều kiện "có bước điều chỉnh thật", detector chỉ đang đo nhiễu
nền của mã mỏng chứ không đo hiện tượng này. Phải giữ đủ hai lớp lọc.

## Việc phải làm khi viết code

1. **Cần giá THÔ của một phiên quá khứ cụ thể** (neo giá, trần đuổi giá, giá vốn) ⇒ phải xử lý
   khả năng dòng đó là ngày GDKHQ. Rẻ nhất: `LEAST(Price, High)` / kiểm `Low ≤ Price ≤ High` và
   fail-closed nếu vi phạm — bắt trọn ca VHM.
2. **Nếu chỉ cần "giá theo hệ quy chiếu HÔM NAY"** (đại đa số việc sizing) ⇒ **dùng `Close`**, đừng
   dùng `Price`. `Close` đúng ở cả ba bảng trong mọi ca đã quét.
3. **Trong cửa sổ ~1 tháng gần nhất** ⇒ `ticker_1m.Price` là bản đáng tin hơn `ticker.Price`.
4. **Cùng ngày / live** ⇒ DNSE API, không phải BQ (CLAUDE.md §Bright-line rule).
5. Consumer đã biết là chạm đúng chỗ này: `mike/bin/lag_entry_anchor.py:105` (`entry_anchor_price`,
   TRẦN ràng buộc, đọc thẳng `tav2_bq.ticker.Price`) — mục **D** trong bản đồ nguồn giá của
   `exdate_order_pipeline_20260815/README.md` §1. Chưa vá tính đến 2026-08-15.

## SQL detector (chép chạy được)

```sql
WITH px AS (
  SELECT t.ticker, t.time, t.Close, t.Price,
         SAFE_DIVIDE(t.Price,t.Close) AS r,
         LAG(SAFE_DIVIDE(t.Price,t.Close))  OVER (PARTITION BY t.ticker ORDER BY t.time) AS r_prev,
         LEAD(SAFE_DIVIDE(t.Price,t.Close)) OVER (PARTITION BY t.ticker ORDER BY t.time) AS r_next
  FROM tav2_bq.ticker AS t          -- CHÚ Ý: phải alias, cột `ticker` trùng tên bảng
  WHERE t.time >= '2024-01-01' AND t.Close > 0 AND t.Price > 0
),
ev AS (SELECT DISTINCT c.ticker, c.exright_date FROM tav2_bq.corporate_action AS c)
SELECT px.ticker, px.time, px.Close, px.Price, ROUND(px.Price/px.Close - 1, 4) AS err
FROM px JOIN ev ON px.ticker = ev.ticker AND px.time = ev.exright_date
WHERE px.r_prev IS NOT NULL AND px.r_next IS NOT NULL
  AND ABS(SAFE_DIVIDE(px.r_prev, px.r_next) - 1) > 0.02   -- có bước điều chỉnh thật
  AND ABS(SAFE_DIVIDE(px.r,      px.r_next) - 1) > 0.02   -- nhưng ex-date chưa sang hệ mới
ORDER BY px.time DESC
```

## Liên quan

- [`ticker_close_vs_price_dividend_adj.md`](ticker_close_vs_price_dividend_adj.md) — ngữ nghĩa gốc
  của cặp `Close`/`Price`; file này là **ngoại lệ** của nó.
- [`corporate_action_bq.md`](corporate_action_bq.md) — nguồn `exright_date` dùng trong detector.
- [`ticker_ohlcv_tables.md`](ticker_ohlcv_tables.md) — quan hệ `ticker` / `ticker_1m` / `ticker_prune`.
- `agents/Taylor/research/exdate_order_pipeline_20260815/README.md` — bản đồ 12 nguồn giá của
  đường đặt lệnh và cửa sổ lật hệ quy chiếu ~19:10 ICT của broker.

↩ [Về index nhóm](index.md)
