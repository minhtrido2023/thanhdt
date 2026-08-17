---
kind: bigquery-column
status: TRAP
source: tav2_bq.ticker.Price (và tav2_bq.ticker_prune.Price) — dòng ĐÚNG NGÀY GDKHQ
group: price-volume
scope: mọi code lấy giá lịch sử một phiên cụ thể từ ticker/ticker_prune (neo giá, trần đuổi giá, sizing, ADV cap)
writer: Ingest ETL EOD ~15:30 ICT — RECONCILE 2 vendor (cafef GiaDongCua + VCI adjusted close); cửa sổ tự sửa 15 phiên KHÔNG BAO GIỜ chạm lớp lỗi này (bq_admin CONFIRMED bằng code 2026-08-15) ⇒ dữ liệu sai KHÔNG TỰ LÀNH
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
   ⚠️ **Trên GIẤY thôi.** Gate `need_cafef` (dòng 209) khiến khối này **không bao giờ chạy** cho
   lớp lỗi ở file này — xem §"Nguyên nhân — bq_admin CONFIRMED bằng code". Đừng đọc mục 2 này
   như một cơ chế bảo vệ đang hoạt động.
3. **Ngoài cửa sổ 15 phiên: chốt VĨNH VIỄN.** Daily job không bao giờ đụng lại (`overwrite=False`
   mặc định). ⇒ Sai quá 15 phiên = **chỉ backfill thủ công mới sửa được**.
4. **Giờ chốt**: pipeline EOD chạy **~15:30 ICT**, sau khi HOSE đóng cửa 14:45.

### Hệ quả trực tiếp cho người dùng dữ liệu
- `Price` của dòng **trước ex-date** = giá THÔ (cafef unadjusted) ⇒ `Price/Close` bằng đúng **hệ số
  quyền** chứ không phải 1. Đây là **đúng thiết kế**, không phải lỗi. VHM 07-20→08-05: `Price/Close`
  = **2,0000 chằn chặn mọi phiên**.
- ⇒ **Đừng viết detector "Price ≠ Close là sai"** — nó sẽ báo động giả trên toàn bộ lịch sử trước
  mọi sự kiện quyền. Detector đúng nằm ở cuối file này (so `r_ex` với `r_next`).

## Ca VHM 2026-08-06 — self-heal ĐÃ KHÔNG fire (nguyên nhân đã CONFIRMED, xem dưới)

Đo lại **2026-08-15** (job `Winston_20260815_072951`), tức **7 phiên giao dịch** sau ex-date
(08-06 → 08-14) ⇒ **VẪN NẰM TRONG cửa sổ 15 phiên**, và độ lệch **98,4%** vượt ngưỡng 1% gấp ~98
lần. Vậy mà `Price` vẫn nguyên **153.000**. Đây là **mâu thuẫn đo được**, không phải suy diễn.

Cấu trúc `Price/Close` của VHM (bằng chứng quyết định — chỉ MỘT dòng gãy):

| Khoảng | `Price/Close` | Diễn giải |
|---|---:|---|
| 2026-07-20 → 08-05 (13 phiên cum) | **2,0000** mọi phiên | đúng thiết kế: cafef unadjusted / Close back-adjusted |
| **2026-08-06 (GDKHQ)** | **1,9844** | **GÃY** — `Price` = 153.000 chép nguyên từ 08-05 |
| 2026-08-07 → 08-14 (6 phiên) | **1,0000** mọi phiên | đúng, hệ số đã về 1 |

### Nguyên nhân — bq_admin CONFIRMED bằng code, 2026-08-15

> Nguồn: bq_admin qua user relay, bus `finding:bq-admin-confirmed-H2-va-fill-forward-bang-code`
> (trace `Winston_20260815_082902`). **Đây là code của hệ thống ingest NGOÀI — ta không đọc,
> không sửa, không test được nó.** Ghi lại để biết dữ liệu có thể sai **kiểu này** và **không tự
> lành**; mọi trích dẫn dòng code dưới đây là nguyên văn bq_admin đưa, không phải ta verify được.

**✅ H2 — CONFIRMED. `anchor_event` chỉ so sánh MỘT ngày, và gate ở dòng 209 chặn toàn bộ khối sửa.**
Nguyên văn bq_admin:
- `anchor_event` chỉ so sánh **một ngày** (`d_last`) — ngày này **dịch mỗi lần chạy lại**.
- `holes` chỉ bắt giá trị **THIẾU (NaN)**, **không** bắt giá trị **CÓ MẶT nhưng SAI**.
- Toàn bộ khối sửa lỗi — **kể cả** nhánh `cafef_settled` ghi đè lại cả `recent_dates`
  (**dòng 261-270**) — **chỉ chạy khi `need_cafef=True`**.
- ⇒ Dòng lỗi nằm **GIỮA** cửa sổ, **không phải NaN**, và **không rơi đúng vị trí `d_last`** ngày
  nó xảy ra ⇒ `need_cafef` **không bao giờ bật lại** ⇒ cơ chế sửa (kể cả phần quét cả cửa sổ) bị
  **bỏ qua VĨNH VIỄN** cho ticker/ngày đó.
- **Điểm gãy là GATE ở dòng 209**, không phải bản thân vòng lặp sửa lỗi.

⇒ Cửa sổ tự sửa 15 phiên là **hư ảo đối với lớp lỗi này**. Số đo khớp: **0/42 dòng được self-heal**.

**✅ H4a — CONFIRMED. Chép T−1 khi vendor null là forward-fill CHỦ ĐÍCH, và im lặng tuyệt đối.**
Nguyên văn bq_admin:
- Chép nguyên T−1 khi vendor trả null = **forward-fill `Price`/`Close` cho giá trị thiếu**, là
  **CHỦ ĐÍCH thiết kế** (invariant: `Price` không bao giờ ≤ 0).
- Có **test riêng khẳng định hành vi**: `tests/test_worker_tasks_behavior.py:2443-2453`,
  `test_zero_price_midseries_is_ffilled` — verify với input `Price=0` giữa chuỗi → output ffill,
  **đúng y hệt 26/42 dòng** đã tìm thấy.
- **KHÔNG LOG GÌ CẢ** — khác `clean_ohlc_df` (có log khi drop spike); `merge_adjust_unadjust`
  ffill **ÂM THẦM**, tạo giá trị *nhìn hợp lệ* mà không ai biết nó bị lặp.

⇒ Xác nhận có **HAI lỗi độc lập**, và cả hai đều là **hành vi đã được chủ đích hoá / test hoá** ở
phía họ: (a) ingest chép T−1 khi thiếu dữ liệu, im lặng; (b) self-heal không bao giờ sửa lại.
**Không có lý do gì để chờ nó tự hết.**

### Hai giả thuyết cũ nay đã hết vai trò

**H1 (`SETTLE_RUN=4` không thoả đúng lúc)** — **KHÔNG CÒN CẦN**. H2 đã giải thích trọn hiện tượng
ở tầng trên (`need_cafef` không bao giờ bật ⇒ gate settle không bao giờ được đánh giá tới). Giữ lại
làm ghi chú: cafef unadjusted vĩnh viễn nên mọi phiên cum có tỉ số VCI/cafef = 0,5, chuỗi 4 phiên
post-ex đầu tiên của VHM (08-07, 08-10, 08-11, 08-12) chỉ hoàn tất 08-12 — vẫn đúng, nhưng không
phải điểm gãy.

**H3 ("cache 153.000 là VCI-adjusted-của-T−1")** — **ĐÃ BÁC BỎ bằng số** (job
`Winston_20260815_072951`). VCI adjusted close của 08-05 trong hệ quy chiếu hôm nay là **76.500**
(= `Close` 08-05), không phải 153.000. Giá trị kẹt 153.000 là **cafef unadjusted của 08-05** ⇒ hỏng
ở **nhánh cafef**, không phải nhánh VCI. Khớp với H4a đã CONFIRMED.

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

📌 **Q3 (backfill 42 dòng lịch sử) — bq_admin chưa trả lời, và ta ĐÃ THÔI HỎI.** Đây giờ là ghi
chú "nice to have", **không phải việc đang chờ**: 42 dòng đều là dữ liệu lịch sử, không dòng nào
đang được dùng cho một quyết định live nào. Bus question đã đóng 2026-08-15
(`Winston/bq-admin-ticker-price-exdate-backfill` + `.../bq-admin-followup-self-heal-khong-fire-va-Q3-backfill`)
vì phần lõi kỹ thuật đã được trả lời xác đáng. **Lý do quan trọng hơn: kể cả có backfill, nó cũng
không bảo vệ được ta** — cơ chế sinh lỗi vẫn nguyên (H4a là hành vi chủ đích, có test khẳng định)
và self-heal vẫn không bao giờ chạm tới (H2), nên **dòng lỗi MỚI sẽ tiếp tục xuất hiện**. Bảo vệ
duy nhất có tác dụng là **guard phía consumer** (mục "Việc phải làm khi viết code" §1). Ai cần
backfill cho một nghiên cứu cụ thể thì hỏi lại bq_admin theo ca đó, đừng mở lại câu hỏi tổng.

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

> ⚠️ **Tiền đề đã đổi (2026-08-15, bq_admin CONFIRMED):** đây **KHÔNG phải lỗi ingest ngẫu nhiên
> rồi sẽ được sửa**. Ghi sai là hành vi **chủ đích, im lặng, có test khẳng định** (H4a); và cơ chế
> tự sửa **theo cấu trúc không bao giờ chạm tới lớp lỗi này** (H2, gate dòng 209). ⇒ **Đừng chờ
> dữ liệu tự lành, đừng giả định "chắc đã được backfill rồi".** Nghi một dòng GDKHQ cụ thể sai thì
> **luôn verify tay qua nguồn thứ 2** (`ticker_1m`, `Close` cùng dòng, hoặc DNSE API) — kể cả dòng
> mới tinh trong cửa sổ 15 phiên, vì chính ca VHM 7-phiên-tuổi vẫn sai. Guard phía consumer là
> **lớp bảo vệ DUY NHẤT** có tác dụng.

1. **Cần giá THÔ của một phiên quá khứ cụ thể** (neo giá, trần đuổi giá, giá vốn) ⇒ phải xử lý
   khả năng dòng đó là ngày GDKHQ. Rẻ nhất: `LEAST(Price, High)` / kiểm `Low ≤ Price ≤ High` và
   fail-closed nếu vi phạm — bắt trọn ca VHM. **Đây là guard BẮT BUỘC, không phải tuỳ chọn**:
   không có cơ chế nào ở phía upstream sẽ bắt hộ (ffill im lặng + self-heal không fire).
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
