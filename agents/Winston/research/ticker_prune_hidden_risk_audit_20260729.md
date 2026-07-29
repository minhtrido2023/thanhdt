# `ticker_prune` — điểm rủi ro ẩn còn lại trong chuỗi tính toán? (audit sâu)

Job `Winston_20260729_132257` · Winston (data-ops) · read-only, không sửa production
Bổ trợ cho `dt5g_history_restate_rca_20260729.md` (cùng ngày, cùng người)

---

## TL;DR

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | `ticker_prune` có nằm trong pipeline UPSTREAM của bq_admin không? | **KHÔNG có bằng chứng.** Quan hệ chạy NGƯỢC LẠI: `ticker_prune` là bảng *derived* của bq_admin, không phải input. Mọi bảng regime/rating ta coi là "input tin cậy" đều do **CHÍNH TA** tính. (Không đọc được SQL của bq_admin — `INFORMATION_SCHEMA.JOBS` Access Denied — nên kết luận dựa trên test cấu trúc, ghi rõ giới hạn ở §1.) |
| 2 | Còn chỗ nào trong pipeline của ta đọc `ticker_prune` ngoài ý muốn? | **CÓ — 4 consumer LIVE-cron mà registry KHÔNG ghi**, nghiêm trọng nhất là `macro_state_live.py:158` (**chính đường DT5G production**). Registry ghi "còn 2 consumer live" → **SAI/thiếu**. Đã sửa registry. |
| 3 | `ticker_prune` có bị ghi đè âm thầm từ 07-15 tới nay không? | **CÓ, và ở quy mô toàn lịch sử.** Rebuild `--mode prune` (TRUNCATE) chạy **2026-07-29 07:27** → **58 mã bị xoá khỏi TOÀN BỘ lịch sử**, depth 07-13 rơi **265 → 220 mã**. Đúng cơ chế bq_admin đã tự mô tả. Hố 07-08→07-14 đã "lành" về độ sâu nhưng **không** về membership. |
| 4 | `ticker_prune` có phải NGUYÊN NHÂN THỨ BA của vụ DT5G 71 phiên? | **Là kênh thật, nhưng KHÔNG phải nguyên nhân.** Đo được: guard breadth lật **79/3135 phiên** — nhưng chỉ **2** phiên trùng lúc Pillar B bắn, cả 2 là singleton → `cap_commit=7` nuốt trọn → **0 phiên state đổi**. RCA giữ nguyên 2 nguyên nhân. |
| 5 | Kết quả PINNED nào còn dựa trên `ticker_prune` cũ? | **Mọi cổng quyết định sống đã migrate xong** (R3, custom30V, due-diligence đều `universe_pit`). **Còn ĐÚNG 1 số tiền thật chưa rà: `WASHOUT_GATE=0,30` của CAPIT** — hiệu chuẩn trên mẫu số `ticker_prune`, mà mẫu số đó vừa co 17%. |

**Một câu:** `ticker_prune` **vẫn là điểm rủi ro ẩn**, nhưng không phải chỗ ta tưởng — không phải
upstream bq_admin, mà là **4 chỗ trong chính pipeline của ta mà registry không biết**, cộng
**1 ngưỡng tiền-thật (CAPIT washout) hiệu chuẩn trên mẫu số vừa đổi**.

---

## 1. Upstream bq_admin — `ticker_prune` là ĐẦU RA, không phải đầu vào

**Giới hạn phải nói trước:** không đọc được SQL của bq_admin.

```
SELECT ... FROM `region-asia-southeast1`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
→ Access Denied: thiếu 'bigquery.jobs.listAll' ở cấp project
```

Nên câu này **không** trả lời được bằng cách đọc code họ. Trả lời bằng 2 đường gián tiếp:

### 1a. Ranh giới sở hữu: bảng nào ta tự tính, bảng nào bq_admin publish

| Bảng | Ai ghi | Ta coi là gì |
|---|---|---|
| `ticker`, `ticker_financial`, `ticker_1m`, `risk_rating` | **bq_admin** | lớp thô, input tin cậy |
| `ticker_prune` | **bq_admin** | universe *derived* từ 2 bảng trên |
| `vnindex_5state*` (base / dt5g_live), `fa_ratings_8l`, `custom30_8l`, `custom30v_8l`, `universe_pit*` | **CHÍNH TA** (`daily_refresh_v34b_linux.sh`, `papertrade_daily.sh`, `refresh_fa_ratings_8l.sh`) | tự tính |

⇒ **Điểm mù mà user lo — "bq_admin đã tính SẴN cho mình bằng dữ liệu cũ" — không tồn tại ở tầng
regime.** DT5G base `vnindex_5state_tam_quan_v34b_clean` và `vnindex_5state_dt5g_live` đều do
`daily_refresh_v34b_linux.sh` của ta tính và `bq load --replace` mỗi tối. bq_admin không đụng vào.

### 1b. Test cấu trúc: `ticker_prune` có phải mẫu số của bảng bq_admin nào không?

Nếu một bảng bq_admin được lọc qua `ticker_prune` thì nó không thể chứa mã ngoài prune.

```
ticker_1m    : 1.262 mã, trong đó 809 mã NGOÀI prune
risk_rating  : 1.279 mã, trong đó 826 mã NGOÀI prune
ticker_prune :   455 mã
```

⇒ **Cả hai đều rộng hơn prune rất nhiều → không bị prune-lọc.** `ticker` (~1.272 mã) và
`ticker_financial` (~1.255 mã) cũng vậy — chính là 2 nguồn mà prune được lọc RA TỪ ĐÓ
(bộ lọc thật, bq_admin xác nhận: `Volume_3M_P50 * Price / Inflation_7 > 1e9`).

**Ghi chú phụ (đi kèm, không phải mục tiêu):** cột `Pattern_Median_Profit_3Y` /
`Pattern_Winrate_3Y` / `Pattern_Deal_Count_3Y` trong `ticker_1m` **NULL 100%** cho cả
453 mã in-prune lẫn 809 mã ngoài prune → **cột chết**. Ai định dùng nhóm Pattern_* phải biết.
*(Tôi đã suýt đọc nhầm "0 mã ngoài prune có Pattern" thành "Pattern là prune-derived" — hoá ra
cả bảng đều NULL. Ghi lại để không ai lặp.)*

**Kết luận §1:** không có bằng chứng nào cho thấy một bảng bq_admin ta tiêu thụ được tính từ
`ticker_prune`. **Rủi ro nằm ở phía TA, không phải upstream.** *(Mức tin cậy: cao cho 4 bảng đã
test; không tuyệt đối vì không đọc được SQL họ.)*

---

## 2. `ticker_prune` trong pipeline của CHÍNH TA — registry đang thiếu 4 consumer LIVE

Registry (`data_registry/price-volume/ticker_prune.md`) ghi: *"2 consumer LIVE còn lại có chủ đích"*
= `golive_recommend_v23.py` (CAPIT) + `trading_bot/executor.py`. **Rà cron thật thì nhiều hơn.**

### Consumer LIVE (chạy trên cron) — trạng thái thật

| # | File | Dùng làm gì | Trong registry? | Đánh giá |
|---|---|---|---|---|
| **A** | **`macro_state_live.py:158`** | **breadth-decoupling guard của DT5G** (`daily_refresh` 18:30) | ❌ **KHÔNG** | 🔴 **NẶNG NHẤT** — đường regime production, lại đúng pattern look-ahead `IN (SELECT DISTINCT ticker …)` không điều kiện `time`. Xem §4. |
| **B** | `dna_report.py:91,129` | 2 trục breadth trong report Telegram + `eod_trading_report.sh` | ❌ KHÔNG | 🟠 tầng báo cáo, không chạm lệnh — nhưng user đọc số này |
| **C** | `update_shares_live.py:49` | `SCAN_UNIVERSE` quét ex-date corp-action (cron 18:40) | ❌ KHÔNG | 🟠 mã rớt prune → **ngưng phát hiện corp-action của mã đó** |
| **D** | `ta_score_daily.py:142` | universe chấm điểm TA | ❌ KHÔNG | 🟡 pattern look-ahead y hệt |
| E | `golive_recommend_v23.py:215,354` | CAPIT pool + ADV cap | ✅ có, cố ý | 🟠 xem §5 — ngưỡng cần rà |
| F | `trading_bot/executor.py:660` | cache prune cho 3 cờ R&D | ✅ có, cố ý | 🟢 3 cờ TẮT trên live |
| G | `daily_refresh_v34b_linux.sh:49`, `bq_freshness_check.sh`, `preflight_check.sh` | **giám sát freshness/depth** | ✅ có, cố ý | 🟢 đúng việc, giữ nguyên |
| H | `trading_bot/due_diligence.py:96` | nhánh **rollback** (`UNIVERSE_SOURCE`) | ✅ | 🟢 mặc định = `pit` |
| I | `custom_basket.py:65` | nhánh **rollback** | (ngụ ý) | 🟢 `UNIVERSE_SOURCE = "pit"` |
| J | sim paper (`pt_v4_dt5g`, `pt_v22_dt5g`, `pt_v23_audit_2014`, `dc_book_waterfall_paper`) | universe backtest | — | 🟡 paper, không tiền thật |

**A–D là "sót lại từ trước migration, không ai nhớ update"** — đúng thứ user hỏi. Không phải cố ý.

### Phần còn lại của repo
~150 file `.py`/`.sh` ngoài `archive/` còn tham chiếu `ticker_prune`, gần như toàn bộ là
research/backtest/screen viết **trước** dự án migrate (đa số commit ≤ 2026-07-13). Registry đã
nêu đúng: *không bắt buộc sửa hết*, nhưng **code MỚI phải dùng `universe_pit`**. Tôi không đề
xuất sweep hàng loạt — chi phí cao, lợi ích thấp, và §5 cho thấy không cái nào đang gác tiền thật.

---

## 3. `ticker_prune` có bị ghi đè âm thầm từ 07-15 tới nay? — **CÓ, toàn lịch sử**

So `tav2_bq.ticker_prune` (live, đọc 2026-07-29 ~13:4x) vs snapshot
`tav2_bq.ticker_prune_ttbackup_fresh_20260713` (clone time-travel 07-13 12:00 UTC, tạo 07-15).

*(Lưu ý: tên snapshot là `…_20260713`, không phải `…_20260714` như dispatch ghi — bản
`_20260714` là của `ticker_financial`.)*

```
                rows      distinct tickers   MAX(time)
LIVE          911.699           455          2026-07-29
BACKUP 07-13  912.209           513          2026-07-13
```

### 3a. 58 mã bị xoá khỏi TOÀN BỘ lịch sử (thêm mới: 0)

```
AAS AAV AIG ASP AST BAF BIG BTT C69 CCI CDC CDP CTF DIH DSE DST DTT DXS FIR FOX
FRT HNG KOS KSV L40 MKP MSR MZG NO1 NRC NVB OPC ORS PCH PIV PJT PPT PSI SBG SBS
SCG SGR STH TAL TCX TDP THD TIN TLD TMP TSA VCK VGI VIW VJC VNF VPL VTD
```
✅ **Không mã nào trong số này đang nằm trong sổ live hay plan** (đã đối chiếu positions + plan).

### 3b. Lịch sử bị viết lại ở **20/27 năm**, cả hai chiều

| năm | Δ dòng | | năm | Δ dòng |
|---|---|---|---|---|
| 2007 | −386 | | 2018 | −194 |
| 2009 | −590 | | 2019 | −260 |
| 2010 | −379 | | 2021 | −368 |
| **2015** | **+675** | | 2022 | −435 |
| **2016** | **+507** | | 2024 | −341 |

Có năm **thêm** dòng, có năm **bớt** — không phải cắt đuôi đơn giản, mà **tính lại membership**.

### 3c. Hố 07-08→07-14: lành về ĐỘ SÂU, **không** lành về MEMBERSHIP

```
ngày         backup   live   Δ
2026-07-06     222     221    −1     ← nền bình thường
2026-07-07     264     220   −44     ← đứt gãy bắt đầu
2026-07-08     267     221   −46
2026-07-10     265     219   −46
2026-07-13     265     220   −45
```
Trong sự cố 07-14/15 các ngày này chỉ còn **7–10 mã**. Nay đã về **219–221 mã** → hố đã được lấp.
**Nhưng**: tập mã 07-13 live là **tập con NGHIÊM NGẶT** của backup (`only_bk=45, only_live=0`).
Không phải phục hồi — mà là **thay bằng một universe hẹp hơn vĩnh viễn**.

### 3d. Nguyên nhân — **đã xác minh, đúng cơ chế bq_admin tự mô tả**

- `ticker_prune.creation_time = 2026-07-29 07:27:05` ⇒ **DROP+CREATE hôm nay** (rebuild `--mode prune`).
- `gs://tav2-gs/rawdata/stock_meta/latest/hit_ticker_list.csv` — **1.819 B, sửa lần cuối 2026-04-14**
  (≈453 mã, khớp QA doc). Không đổi.
- Live distinct = **455** ≈ hit list; `ticker_1m ∩ prune` = **đúng 453**.

QA doc `ticker_prune_universe_QA_bq_admin_20260722.md` (Câu 8) đã ghi trước:
> *"mọi mã đưa vào bằng đường daily append đều bị xóa sạch ở lần rebuild toàn bộ tiếp theo, vì
> rebuild chỉ nạp lại các mã thuộc hit list"* — 91/543 mã không thuộc hit list.

⇒ Backup 07-13 (513 mã) = 453 hit-list + ~60 mã đường daily-append tích được. Rebuild 07-29 xoá
sạch phần tích luỹ. **Đây là hành vi đã được cảnh báo trước, không phải bug mới.** Nhưng nó
**chưa từng được đo sau sự cố** — và nó **sẽ lặp lại** ở mọi rebuild sau.

### 3e. Hệ quả cho quyết định khôi phục đang treo

> **Khuyến nghị: ĐÓNG quyết định "khôi phục ticker_prune từ backup" theo hướng KHÔNG khôi phục.**

Lý do: khôi phục sẽ nhét lại 58 mã mà upstream **chủ động loại ở mọi rebuild** → bị xoá lại ở lần
TRUNCATE kế tiếp. Đây là quyết định của user, tôi chỉ nêu bằng chứng. Giữ
`ticker_prune_ttbackup_fresh_20260713` làm **mỏ neo nghiên cứu** (RCA §Ưu tiên 2 dùng chính nó).

---

## 4. Liên hệ với vụ DT5G 71 phiên — kênh THẬT, nhưng **không** phải nguyên nhân

### 4a. Kênh tồn tại — và nằm đúng trên đường production

`macro_state_live.py:153-163`:
```sql
SELECT t.time, AVG(IF(t.Close>t.MA200,1.0,0.0)) AS b200, COUNT(*) AS univ
FROM tav2_bq.ticker AS t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)   -- ← KHÔNG có điều kiện time
```
```python
decoup = ((univ >= 100) & (b200 >= 0.50)).shift(1)
...
if bull[t] or decoup[t]:   uc = ub = umild = False     # Pillar B (US panic) bị BỎ QUA
```
Danh sách mã là **DISTINCT toàn thời gian** ⇒ xoá 58 mã làm đổi breadth ở **MỌI ngày lịch sử**.

**Đối chứng — `vnindex_5state_ew_v1.py` KHÔNG dùng `ticker_prune`**: factor `Breadth` của nó
(`% above MA50`) chạy trên universe eligible tự tính từ `ticker` (≥252 phiên + ADV60 ≥ 0,5 tỷ).
⇒ **Kênh expanding-rank ở §2.2 của RCA sạch với prune.** Chỉ có 1 điểm chạm: guard macro.

### 4b. Đo tác động thật (live-list vs backup-list, 2014+)

```
n_days = 3.135
b200 lệch          : 3.130 / 3.135 phiên   (max lệch 4,66pp)
decoup LẬT         :    79 phiên
```

### 4c. …nhưng chỉ **2/79** phiên trùng lúc Pillar B thực sự bắn

Guard chỉ có tác dụng khi US panic. Đối chiếu `data/us_market_history.csv`
(`vix_crisis=35 / vix_bear=25+spx_dd<−15% / vix_mild=20+spx_dd<−10%`):

| ngày lật | VIX max | SPX DD | tier Pillar B | hướng |
|---|---|---|---|---|
| 2016-01-28 | 22,4 | −11,1% | MILD | bk=suppress → live=**không** suppress |
| 2020-06-17 | 35,1 | −8,5% | CRISIS (VIX) | bk=suppress → live=**không** suppress |

**77 phiên còn lại rơi vào giai đoạn US bình yên → guard vô nghĩa → 0 tác động.**

### 4d. Và cả 2 phiên đó cũng bị `cap_commit=7` nuốt

`_commit(arr, K=7)`: một mức cap mới phải **giữ liên tiếp 7 phiên** mới commit. Cả 2 phiên trên
là **singleton biệt lập** (không phải chuỗi) → cap đổi đúng 1 phiên → **không bao giờ commit**.

> **Kết luận §4: `ticker_prune` KHÔNG phải nguyên nhân thứ ba. Blast radius = 0 phiên state đổi.**
> RCA `dt5g_history_restate_rca_20260729.md` giữ nguyên 2 nguyên nhân (VNINDEX_PE backfill +
> corp-action restate). *(Đã xác minh bằng query + đọc code, không suy đoán.)*

### 4e. NHƯNG là tripwire sống — vì nó nằm ngay trên lưỡi dao

Nhìn danh sách 79 phiên: đại đa số b200 dao động **±0,5pp quanh đúng ngưỡng 0,50**
(vd 2025-06-05: `0,5049` → `0,4934`). Guard này về bản chất là **coin-flip quanh 0,50**, và
membership prune vừa dịch nó ~1pp. Trong đó **2 phiên thuộc 2026** (01-29, 03-02) — vùng live.

⇒ Rủi ro thật không phải quá khứ, mà là: **một rebuild `--mode prune` rơi đúng vào cửa sổ US
panic sẽ lật guard ngay trên chuỗi live** — im lặng, không cảnh báo nào.

### 4f. Ranh giới với điều tra song song của Taylor

Job `Taylor_20260729_132056` điều tra **giai đoạn 2006-2008 thị trường mỏng làm méo percentile PE**.
Đó là **kênh khác hẳn**: PE expanding-percentile trong `ew_v1`/`dual_v3`, dữ liệu `ticker` /
`VNINDEX_PE`, **không đụng `ticker_prune`** (đã xác minh ở §4a: `ew_v1` không đọc prune).
**Không trùng công sức.** Nếu Taylor cần: breadth-vào-`ew_v1` là universe tự tính, đừng nghi prune ở đó.

---

## 5. Kiểm kê kết quả PINNED — cổng quyết định sống đã sạch, còn 1 ngưỡng cần rà

`data/results_registry.md`: 197 mục, ~30 mục có nhắc `ticker_prune`.

### 5a. Đã re-pin / đã migrate ✅

| Kết quả pinned | Trạng thái | Bằng chứng |
|---|---|---|
| **R3** CAGR 27,16% / Sharpe 1,81 / MaxDD −18,1% / Calmar 1,50 | ✅ re-pin `universe_pit` 2026-07-22 | registry_dòng 36-39 |
| **custom30V** (rổ parking V2.4 production, `custom30v_8l`) | ✅ `custom_basket.py:54  UNIVERSE_SOURCE = "pit"` | đường sinh: `papertrade_daily.sh [6b]` → `custom30_history.py` → `custom_basket.build_pit` |
| **due-diligence** (gác lệnh) | ✅ `due_diligence.py` mặc định `pit`, **cấm** fallback ngầm (§4.3) | |
| **R3 predicate** trong `golive_recommend_v23.py` | ✅ P3 cutover `pit`, không có nhánh fallback im lặng | |
| **DT5G perf** (CAGR/Sharpe/ablation DT4-vs-DT5G) | ✅ không liên quan — chạy trên VNINDEX | ⚠️ *vẫn phải re-pin vì lý do KHÁC: restate PE/corp-action, xem RCA §Ưu tiên 3* |

### 5b. ⚠️ CHƯA rà — số duy nhất gác tiền thật còn dính prune

> **`WASHOUT_GATE = 0,30` + ADV cap của CAPIT** (`golive_recommend_v23.py:215, 354`)

- Hai chỗ này **cố ý** còn đọc `ticker_prune` (registry ghi rõ, ghim chờ `capit_fired=false`).
- Registry cũng đã cảnh báo sẵn: *"`WASHOUT_GATE=0,30` được hiệu chuẩn trên mẫu số `ticker_prune`.
  Đổi mẫu số mà giữ ngưỡng = đổi ngữ nghĩa gate."*
- **Cái mới của audit này: mẫu số ĐÃ tự đổi mà không ai đổi gì cả** — 265 → 220 mã/ngày (**−17%**),
  và 58 mã rời khỏi toàn bộ lịch sử. Ngưỡng 0,30 nay đọc trên một mẫu số khác lúc hiệu chuẩn.
- **Ưu tiên: CAO** (tiền thật, đang chạy). **Chủ sở hữu: Taylor** (hiệu chuẩn ngưỡng = việc mô hình,
  ngoài phạm vi tôi). Tôi **không** tự sửa.

### 5c. Còn lại — ~30 mục research/lens, ưu tiên THẤP

Sector screens (bank/pharma/retail/tech/telecom…), `gap_fairvalue_*`, `gq_score_gate`,
`lag_dnpr_*`, compounder screens. Đều là **lens, không phải book**; không cái nào gác quyết định
sống. registry đã tự ghi caveat "bias sống sót" (dòng 204) và "data-drift" (dòng 221 — *"Số tuyệt
đối trong registry sẽ trôi theo data; DELTA enhancement mới ổn định"*). **Không đề xuất tính lại
hàng loạt** — chi phí cao, không đổi quyết định nào.

---

## 6. Việc cần làm (đề xuất — KHÔNG tự thực hiện, đúng ranh giới data-ops)

| # | Việc | Chủ | Ưu tiên |
|---|---|---|---|
| 1 | **Rà `WASHOUT_GATE=0,30` + ADV cap CAPIT** trên mẫu số prune mới (265→220) | **Taylor** | 🔴 CAO — tiền thật |
| 2 | **Migrate `macro_state_live.py:158` breadth guard sang `universe_pit`** (hoặc ít nhất thêm điều kiện `time` để bỏ look-ahead). Đây là **đổi input mô hình regime** → cần user + Taylor duyệt, tôi không tự sửa | Taylor + user | 🔴 CAO |
| 3 | **ĐÓNG quyết định treo "restore ticker_prune từ backup"** theo hướng KHÔNG restore (§3e) | user | 🟠 |
| 4 | Migrate `dna_report.py`, `update_shares_live.py`, `ta_score_daily.py` sang `universe_pit` | Winston (sau khi #2 chốt pattern) | 🟠 |
| 5 | Cảnh báo membership-drift: alert khi `COUNT(DISTINCT ticker)` của `ticker_prune` đổi > ngưỡng giữa 2 ngày (hôm nay sẽ bắn ở −58). Bổ sung cho depth-check đã có (bắt "moi ruột", **không** bắt "thay universe") | Winston | 🟠 |
| 6 | Re-pin kết quả DT5G lịch sử — **vì restate PE/corp-action**, không phải vì prune (RCA §Ưu tiên 3) | Taylor | 🟠 |

---

## Lệnh tái lập

```bash
P=lithe-record-440915-m9; Q="bq query --use_legacy_sql=false --project_id=$P"

# §3a — 58 mã bị xoá khỏi toàn lịch sử
$Q 'SELECT COUNT(*) FROM (SELECT DISTINCT ticker FROM `'$P'.tav2_bq.ticker_prune_ttbackup_fresh_20260713`
    EXCEPT DISTINCT SELECT DISTINCT ticker FROM `'$P'.tav2_bq.ticker_prune`)'

# §3c — membership 07-13 là tập con nghiêm ngặt
$Q 'SELECT COUNT(*) FROM (SELECT ticker FROM `'$P'.tav2_bq.ticker_prune` WHERE time="2026-07-13"
    EXCEPT DISTINCT SELECT ticker FROM `'$P'.tav2_bq.ticker_prune_ttbackup_fresh_20260713` WHERE time="2026-07-13")'  # = 0

# §3d — rebuild TRUNCATE hôm nay + hit list không đổi
$Q 'SELECT TIMESTAMP_MILLIS(creation_time) FROM `'$P'.tav2_bq.__TABLES__` WHERE table_id="ticker_prune"'
gsutil ls -l gs://tav2-gs/rawdata/stock_meta/latest/hit_ticker_list.csv

# §4b — 79 phiên lật guard breadth
# (query đầy đủ: xem bus event Winston_20260729_132257)

# §1b — bảng bq_admin KHÔNG bị prune-lọc
$Q 'SELECT COUNT(DISTINCT ticker) FROM `'$P'.tav2_bq.ticker_1m`
    WHERE ticker NOT IN (SELECT DISTINCT ticker FROM `'$P'.tav2_bq.ticker_prune`)'   # 809
```
