---
kind: bigquery-column
status: TRAP
source: tav2_bq.ticker.Price (và tav2_bq.ticker_prune.Price) — dòng ĐÚNG NGÀY GDKHQ
group: price-volume
scope: mọi code lấy giá lịch sử một phiên cụ thể từ ticker/ticker_prune (neo giá, trần đuổi giá, sizing, ADV cap)
writer: Ingest ETL EOD ~15:30 ICT — RECONCILE 2 vendor (cafef GiaDongCua + VCI adjusted close), có cửa sổ tự sửa 15 phiên nhưng ĐO ĐƯỢC LÀ KHÔNG FIRE
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

## Cơ chế THẬT của cột `Price` — bq_admin xác nhận 2026-08-15

> Nguồn: bq_admin trả lời qua user relay, ghi lên bus `finding:bq-admin-explained-price-mechanism-self-heal-15session`
> (trace `Winston_20260815_064023`). Thay thế hoàn toàn phần "lỗi ingest ngẫu nhiên / append-only
> vĩnh viễn" mà bản đầu của file này suy ra từ artifact — suy luận đó SAI ở chi tiết "append-only".

1. `ticker.Price` **không phải một field vendor duy nhất**; nó là **kết quả RECONCILE hai vendor**:
   - **cafef `GiaDongCua`** — giá đóng cửa **UNADJUSTED**, ×1000. Đây là "xương sống" của cột.
   - **VCI adjusted close** — **luôn GHI ĐÈ** cho phiên **MỚI NHẤT**.
2. **Cửa sổ tự sửa `RECENT=15`** (15 phiên gần nhất): nếu phát hiện một `anchor_event` lệch **>1%**
   giữa cache cũ và VCI adjusted, **VÀ** cafef đã "settled" (`SETTLE_RUN=4` — 4 phiên gần nhất tỉ số
   VCI/cafef ≈ 1), job sẽ **ghi đè lại TOÀN BỘ `recent_dates`**.
3. **Ngoài cửa sổ 15 phiên: chốt VĨNH VIỄN.** Daily job không bao giờ đụng lại (`overwrite=False`
   mặc định). ⇒ Sai quá 15 phiên = **chỉ backfill thủ công mới sửa được**.
4. **Giờ chốt**: pipeline EOD chạy **~15:30 ICT**, sau khi HOSE đóng cửa 14:45.

### Hệ quả trực tiếp cho người dùng dữ liệu
- `Price` của dòng **trước ex-date** = giá THÔ (cafef unadjusted) ⇒ `Price/Close` bằng đúng **hệ số
  quyền** chứ không phải 1. Đây là **đúng thiết kế**, không phải lỗi. VHM 07-20→08-05: `Price/Close`
  = **2,0000 chằn chặn mọi phiên**.
- ⇒ **Đừng viết detector "Price ≠ Close là sai"** — nó sẽ báo động giả trên toàn bộ lịch sử trước
  mọi sự kiện quyền. Detector đúng nằm ở cuối file này (so `r_ex` với `r_next`).

## Ca VHM 2026-08-06 — self-heal ĐÃ KHÔNG fire, mâu thuẫn với mô tả cơ chế

Đo lại **2026-08-15** (job `Winston_20260815_072951`), tức **7 phiên giao dịch** sau ex-date
(08-06 → 08-14) ⇒ **VẪN NẰM TRONG cửa sổ 15 phiên**, và độ lệch **98,4%** vượt ngưỡng 1% gấp ~98
lần. Vậy mà `Price` vẫn nguyên **153.000**. Đây là **mâu thuẫn đo được**, không phải suy diễn.

Cấu trúc `Price/Close` của VHM (bằng chứng quyết định — chỉ MỘT dòng gãy):

| Khoảng | `Price/Close` | Diễn giải |
|---|---:|---|
| 2026-07-20 → 08-05 (13 phiên cum) | **2,0000** mọi phiên | đúng thiết kế: cafef unadjusted / Close back-adjusted |
| **2026-08-06 (GDKHQ)** | **1,9844** | **GÃY** — `Price` = 153.000 chép nguyên từ 08-05 |
| 2026-08-07 → 08-14 (6 phiên) | **1,0000** mọi phiên | đúng, hệ số đã về 1 |

### Ba giả thuyết (chỉ nêu — hệ thống của bq_admin, ta không code hoá)

**H1 — `SETTLE_RUN=4` không bao giờ thoả ĐÚNG LÚC cần.** Điều kiện settle là "4 phiên gần nhất tỉ
số VCI/cafef ≈ 1". Nhưng cafef là **unadjusted vĩnh viễn**, nên **mọi phiên cum** có tỉ số = **0,5**
(chính là `Price/Close`=2,0 ở bảng trên). Trong các phiên 08-06 → 08-11, cửa sổ 15 phiên vẫn còn đầy
dòng cum ⇒ chuỗi 4 phiên tỉ số ≈1 **chưa đủ dài** ⇒ gate settle FAIL ⇒ self-heal bị bỏ qua. Chuỗi 4
phiên post-ex đầu tiên (08-07, 08-10, 08-11, 08-12) chỉ hoàn tất **ngày 08-12** — và nếu
`anchor_event` là trạng thái tính-một-lần-rồi-bỏ (không xếp hàng chờ), cửa sổ vá đã trôi qua khi
gate mở. Đây là bản làm sắc của giả thuyết Mike nêu, có số neo.

**H2 — `anchor_event` chỉ được đánh giá trên phiên MỚI NHẤT, không quét hết `recent_dates`.** Phiên
mới nhất (08-14) có cache 68.200 == VCI adjusted 68.200 ⇒ lệch **0%** ⇒ không sinh event ⇒ không bao
giờ ghi đè `recent_dates`. Một hỏng nằm GIỮA cửa sổ thì vĩnh viễn không được nhìn tới. **H2 giải
thích được cả 42 dòng bằng một cơ chế duy nhất**, nên là giả thuyết mạnh nhất.

**H3 — "cache 153.000 chính là VCI-adjusted-của-T-1 nên so sánh bị lẫn hệ quy chiếu": BÁC BỎ bằng
số.** VCI adjusted close của 08-05 trong hệ quy chiếu hôm nay là **76.500** (= `Close` 08-05), không
phải 153.000. Giá trị kẹt 153.000 là **cafef unadjusted của 08-05** — tức hỏng nằm ở **nhánh cafef**,
không phải nhánh VCI.

**H4 — cơ chế ghi ra giá trị sai ban đầu = FILL-FORWARD khi vendor thiếu.** 26/42 dòng lệch có
`Price[ex] == Price[ex−1]` **tuyệt đối từng đồng**. Chép nguyên T−1 là chữ ký kinh điển của
fill-forward khi vendor trả null/chưa cập nhật. Ngày GDKHQ đúng là ngày cafef lật hệ quy chiếu ⇒
đúng ngày dễ trả null nhất lúc 15:30 ICT. **Fail-safe đúng phải là bỏ trống/fail, không phải chép
T−1** — chép T−1 tạo ra một giá trị *trông hợp lệ* mà không consumer nào phát hiện được.
⇒ Có **HAI lỗi độc lập**: (a) ingest chép T−1 khi thiếu dữ liệu; (b) self-heal không sửa lại.

## Kiểm chứng "self-heal có hoạt động nói chung không" — KHÔNG kết luận được từ 41 dòng còn lại

Đo tuổi (số phiên VNINDEX) của 42 dòng lệch tại 2026-08-15:

| Tuổi (phiên) | Số dòng | Trong cửa sổ 15 phiên? |
|---|---:|---|
| 7 (VHM 08-06) | 1 | ✅ CÒN trong cửa sổ — đáng lẽ phải tự sửa |
| 27 → 649 (41 mã UPCOM/mỏng) | 41 | ❌ đã ngoài cửa sổ, chốt vĩnh viễn |

⇒ **41 dòng kia KHÔNG dùng để test self-heal được** — chúng đã ngoài cửa sổ nên "vẫn sai" là **đúng
thiết kế**, không nói lên điều gì. Test mà Mike đề xuất (dòng nào đã tự sửa?) **không quyết định
được** vì mẫu rỗng.

**Nhưng có một suy luận mạnh hơn theo hướng ngược**: mỗi dòng trong 41 dòng ấy ĐÃ từng nằm trong cửa
sổ 15 phiên suốt 15 phiên sau ex-date của nó, và **thoát ra mà không được sửa**. Cộng cả VHM:
**42/42 dòng ex-date lệch đã biết đều KHÔNG được self-heal**. Không có một ca dương tính nào.
(Không chứng minh được self-heal *chưa từng* fire — 2.033 dòng ex-date ĐÚNG không phân biệt được
"ghi đúng ngay từ đầu" với "đã được sửa" — nhưng riêng trên tập lỗi thì tỉ lệ sửa là **0/42**.)

❓ **Còn treo — Q3 chưa được trả lời**: có backfill được 42 dòng đã liệt kê không? (39/42 đã ngoài
cửa sổ 15 phiên ⇒ theo chính mô tả cơ chế, **chỉ backfill thủ công mới sửa được**.)

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
