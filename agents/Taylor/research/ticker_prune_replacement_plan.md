# PHƯƠNG ÁN THAY THẾ `ticker_prune` — kiến trúc, migration, timeline

Job `Taylor_20260722_033547` · 2026-07-22 · Taylor (Quant, lead)
Tiền thân: `ticker_prune_universe_governance.md` (job `Taylor_20260721_162005`) + phản hồi bq_admin.
**Trạng thái: ĐỀ XUẤT QUYẾT ĐỊNH. Chưa implement dòng code nào. Chờ Winston (khả thi vận hành) +
quant-skeptic review → user duyệt.**

---

## ⚠️ 0. Cảnh báo về nguồn: file Q&A của bq_admin KHÔNG có trên đĩa

Dispatch chỉ tới `agents/Taylor/research/ticker_prune_universe_QA_bq_admin_20260722.md`. File này
**không tồn tại** — đã tìm toàn repo, `/tmp`, `$HOME`, bus events, và mọi file `.md` tạo sau
2026-07-21 20:00. Không có bản nào.

Vì vậy tài liệu này làm việc trên **bản tóm tắt 5 điểm của Mike trong prompt dispatch**, không phải
văn bản gốc. Hệ quả cụ thể:
- Các điểm 1-3 và 5 (3 đường ghi · `hit_ticker_list.csv` suy từ backtest · non-reproducible ·
  khuyến nghị tự xây snapshot) đủ chi tiết để làm căn cứ thiết kế — tôi coi là **dùng được**.
- **Phần 4 (5 vấn đề kỹ thuật ETL) thì KHÔNG.** Tóm tắt chỉ nêu tên 3 trong 5 vấn đề (GCS cleanup
  bị comment · `is_skip` không nhất quán · `max_bad_records=10` im lặng), không nói **các vấn đề đó
  nằm ở load job của bảng nào**. Đó chính là thông tin duy nhất cần để trả lời câu hỏi §7. Xem §7 —
  tôi KHÔNG xác nhận được giả định "không liên quan", và giải thích vì sao giả định đó có khả năng
  SAI.

**Việc cần làm trước khi user duyệt phương án này: lấy lại văn bản gốc của bq_admin và lưu đúng
đường dẫn trên.** Nếu văn bản gốc mâu thuẫn với tóm tắt ở bất kỳ điểm nào, §7 và §3.3 phải xem lại.

---

## 1. TL;DR — 5 câu

1. **Đồng ý hoàn toàn với bq_admin: đừng mirror, tự xây.** Nhưng lý do quyết định KHÔNG phải bias
   (bias là hệ quả) — mà là **`ticker_prune` không tái lập được (non-reproducible)**. Một baseline
   thay đổi sau lưng thì không phải baseline, bất kể nó đúng hay sai.
2. **Nỗi lo lớn nhất trong doc gốc (§5: "rule thanh khoản thuần của ta có thể THUA curation của
   bq_admin") — đã ĐO và bác bỏ được.** Bộ tiêu chí B1-B5 tôi đề xuất, dùng **0 thông tin từ
   backtest**, tái tạo universe PIT của `ticker_prune` với **recall 97-99% tại cả 7 mốc lịch sử
   2014→2026** (§2.2). Curation của họ gần như không mang thông tin gì mà rule không có.
3. **Migration khả thi hơn tôi tưởng: `tav2_bq.ticker` là superset THẬT của `ticker_prune` cả dòng
   lẫn cột** — 0/738.201 dòng prune (2014+) mồ côi, và 174 cột của `ticker` chứa đủ mọi cột mở rộng
   (`Trading_Value`, `O1W`, `Pattern_*`, `PC_*`) mà tôi từng lo là prune-only (§2.1). Thay thế =
   **đổi mệnh đề JOIN, không mất cột nào, không cần bảng trung gian.**
4. **CẦN re-pin R3 — câu trả lời đã đổi so với doc gốc.** Trước đây tôi đề xuất "A/B đo trước rồi
   mới quyết". Giờ đã biết chắc `hit_ticker_list.csv` được suy từ chính kết quả backtest cũ ⇒ đây
   là circular selection bias đã xác nhận, không còn là giả thuyết. A/B **hạ cấp** từ cổng-quyết-định
   xuống **chẩn đoán độ lớn**, và nó đến miễn phí như sản phẩm phụ của lần re-pin (§5).
5. **Rủi ro LIVE nguy hiểm nhất của migration KHÔNG phải backtest — là CAPIT.** Universe mới rộng
   hơn prune ~17% ⇒ **mẫu số breadth đổi ⇒ ngưỡng `WASHOUT_GATE=0.30` mất hiệu chuẩn**, đúng lúc
   breadth đang bò lên 0,2176 và CAPIT sắp fire. Đây là hạng mục phải xử lý riêng, không được cutover
   im lặng (§4.4).

---

## 2. BẰNG CHỨNG MỚI đo trong job này

Toàn bộ số dưới đây đo trực tiếp trên BQ hôm nay, có thể chạy lại.

### 2.1 `ticker` là superset thật của `ticker_prune` — migration không mất gì

```sql
SELECT COUNT(*) prune_rows, COUNTIF(t.ticker IS NULL) orphan_rows
FROM tav2_bq.ticker_prune p LEFT JOIN tav2_bq.ticker t ON p.ticker=t.ticker AND p.time=t.time
WHERE p.time>=DATE"2014-01-01"
→ prune_rows=738.201   orphan_rows=0
```

Về cột: `ticker` có **174 cột**, và các cột tôi tưởng là prune-only đều tồn tại **và có dữ liệu**
(mẫu 2024, n=316.591 dòng): `Trading_Value` 316.457 · `O1W` 316.591 · `Pattern_Winrate_3Y` 296.918 ·
`PC_6M` 314.379 · `Volume_3M_P50` 315.684.

→ **Mọi câu `FROM tav2_bq.ticker_prune p` đều thay được bằng `FROM tav2_bq.ticker t JOIN universe_pit
u USING(ticker, time)` mà không mất một cột nào.** Đây là điều làm cho phương án này rẻ.

### 2.2 Bộ tiêu chí B1-B5 tái tạo được curation của bq_admin — recall 97-99%

Rule đo: `ICB_Code IS NOT NULL` ∧ `Close ≥ 1.000đ` ∧ `Volume_3M_P50 × COALESCE(Price,Close) ≥ ngưỡng
thực`, ngưỡng thực = **1,0 tỷ VND neo 2026, khử lạm phát 7%/năm** (`1e9 / 1,07^(2026−năm)`).

| Ngày | `n_rule` (đề xuất) | `n_prune` PIT | Giao | **Recall** | `n_union` (dạng gọi hiện tại) |
|---|---|---|---|---|---|
| 2014-06-30 | 165 | 140 | 136 | **97,1%** | 316 |
| 2016-06-30 | 195 | 167 | 163 | **97,6%** | 367 |
| 2018-06-29 | 198 | 180 | 177 | **98,3%** | 459 |
| 2020-06-30 | 253 | 226 | 223 | **98,7%** | 494 |
| 2022-06-30 | 402 | 321 | 318 | **99,1%** | 523 |
| 2024-06-28 | 366 | 310 | 307 | **99,0%** | 535 |
| 2026-06-15 | 273 | 233 | 230 | **98,7%** | 540 |

(Cột `n_union` lấy từ doc gốc §2.2 = dạng `IN (SELECT DISTINCT ticker FROM ticker_prune)` không có
điều kiện thời gian — dạng đang chạy trong pin R3 và custom30V.)

Ba kết luận rút ra, đều quan trọng:

**(a) Mục tiêu hiệu chuẩn trong doc gốc đã đạt và vượt xa.** Doc gốc §3.2 đặt "overlap ≥85% thì rule
mới coi là đủ tốt". Thực đo 97-99% tại **mọi** mốc, không phải mốc gần đây. Và ngưỡng 1,0 tỷ là con
số tôi bốc ra hôm qua **trước khi** đo — không phải kết quả tuning. (Sweep kiểm chứng tại 2026-06-15:
2e8→421 mã, 5e8→336, **1e9→273**, 2e9→220 (recall tụt còn 83%), 5e9→171. Ngưỡng 1e9 nằm ở chỗ recall
còn ~99% mà universe chưa phồng — đây là **cao nguyên**, không phải đỉnh nhọn.)

**(b) Curation của bq_admin là TRỪ, không phải CỘNG.** Prune gần như là tập con của rule (chỉ 3 mã
prune-only tại 2026-06-15). Nghĩa là họ **không** biết thêm điều gì mà ta không biết — họ chỉ bỏ bớt.
Nỗi lo §5 doc gốc ("có thể họ lọc mã diện cảnh báo/kiểm soát, BCTC ngoại trừ — thay thế mù sẽ làm
xấu universe") **không được dữ liệu ủng hộ**: nếu curation mang tín hiệu chất lượng thật, ta sẽ thấy
prune chứa mã mà rule bỏ sót, chứ không phải ngược lại. ⚠️ *Giới hạn của lập luận này:* nó chứng minh
curation không thêm **phạm vi**, chưa chứng minh 43 mã "rule-only" là **tốt**. Đó là việc của gate
chất lượng ở tầng chiến lược (ROE/FSCORE/8L), không phải tầng universe — và §4.4 xử lý rủi ro sizing
của 43 mã này.

**(c) Look-ahead đo được rõ: 1,4×–2,3×.** So `n_rule` (PIT) với `n_union`: 2018 là **198 vs 459 =
2,3×**. Universe backtest hiện tại đang cho phép mua gấp đôi số mã lẽ ra được phép tại thời điểm đó.
Kết hợp với việc `hit_ticker_list.csv` được suy từ chính backtest cũ ⇒ **phần phồng thêm không phải
mã ngẫu nhiên, mà thiên vị về phía mã từng sinh deal** — đây đúng định nghĩa circular selection bias.

### 2.3 Chi phí backfill: không đáng kể

Dry-run quét toàn bộ lịch sử `ticker` cho các cột cần thiết: **215.458.030 bytes ≈ 215 MB** (~0,001
USD). Không phải rào cản. Rào cản là **kiểm định**, không phải compute.

---

## 3. KIẾN TRÚC — `universe_pit`

### 3.1 Nguyên tắc (giữ nguyên doc gốc §3.1, bq_admin xác nhận độc lập)

Bảng do đội Mike sở hữu, **append-only, bất biến**, tính **chỉ từ cột thô point-in-time của
`tav2_bq.ticker`**, **KHÔNG đọc `ticker_prune`** ở bất kỳ đâu.

```
universe_pit(time DATE, ticker STRING, in_universe BOOL, reason STRING,
             ruleset_version INT, backfilled BOOL, computed_at TIMESTAMP)
```
Partition `time`, cluster `ticker`. Ước lượng kích thước: ~26 năm × ~250-400 mã/ngày ≈ 1,5-2M dòng,
vài chục MB.

Nhắc lại phân biệt bắt buộc (đã có trong doc gốc, giờ càng đúng): **tính lại** universe quá khứ bằng
dữ liệu trailing ≤ ngày đó **không phải look-ahead** — hợp lệ. **Sửa** membership quá khứ theo danh
sách hôm nay **là** look-ahead — đó là cái `ticker_prune` đang làm.

### 3.2 Bộ tiêu chí v1 — sửa gì so với B1-B7 doc gốc

| # | Điều kiện | Doc gốc | **Bản này** | Ghi chú |
|---|---|---|---|---|
| B1 | `ICB_Code IS NOT NULL` | ✔ | **giữ nguyên** | loại pseudo-ticker chỉ số |
| B2 | Tuổi ≥ 60 phiên từ dòng đầu trong `ticker` | ✔ | **giữ nguyên** | khớp chế độ tự động ~85 ngày hiện có |
| B3 | VÀO: median trading value 60 phiên ≥ ngưỡng thực | 1,0 tỷ (*chưa hiệu chuẩn*) | **1,0 tỷ — ĐÃ HIỆU CHUẨN** (§2.2) | recall 97-99%, cao nguyên rộng |
| B4 | RA: < 0,5 tỷ trong 20 phiên liên tiếp | ✔ | **giữ nguyên** | hysteresis bất đối xứng, cùng triết lý DT5G 4-gate |
| B5 | `Close ≥ 1.000 VND` | ✔ | **giữ nguyên** | |
| B6 | Loại cứng: vắng ≥10 phiên liên tiếp trong `ticker` | ✔ | **giữ nguyên** | delist/đình chỉ |
| B7 | Loại rồi phải đủ điều kiện lại từ đầu | ✔ | **giữ nguyên** | chống nhấp nháy |
| **B8** | — | *(không có)* | **MỚI: integrity gate** | xem §3.3 |

**Chỉ 2 thay đổi thực chất:** B3 chuyển từ "đề xuất khởi điểm chưa hiệu chuẩn" → **đã hiệu chuẩn có
số**; và thêm **B8**. Bộ tiêu chí còn lại đứng vững trước phản hồi bq_admin — vì nó vốn đã được thiết
kế để không phụ thuộc `ticker_prune`.

**Điểm cần user biết rõ:** ⚠️ B3/B4 dùng `Volume_3M_P50 × Price` trong đo lường §2.2 (cột dựng sẵn,
cửa sổ 3 tháng), còn đặc tả ghi "median 60 phiên". Hai thứ **gần nhau chứ không bằng nhau**. Builder
phải tự tính median 60 phiên từ `Price × Volume` thô (tự chủ, không phụ thuộc cột dẫn xuất của ETL
ngoài) — và **bước đầu tiên khi implement là chạy lại bảng §2.2 với công thức tự tính** để xác nhận
recall vẫn 97-99%. Nếu tụt đáng kể thì hiệu chuẩn lại B3, không phải bỏ phương án.

### 3.3 B8 — Integrity gate (mới, bắt buộc)

Builder **từ chối append** ngày mới và báo động nếu bất kỳ điều kiện nào sau đây vi phạm:
- Số mã `in_universe` ngày d lệch > **±15%** so với trung vị 20 ngày trước đó.
- Số dòng thô của `ticker` tại ngày d < **90%** trung vị 20 ngày.
- Đã tồn tại dòng `universe_pit` cho ngày d (chống ghi đè / double-append — `coding_guidelines.md` §5).

Lý do B8 tồn tại: xem §7. Không có nó, `universe_pit` chỉ chuyển rủi ro toàn vẹn dữ liệu từ
`ticker_prune` sang `ticker` chứ không loại bỏ.

### 3.4 Cadence & versioning

Giữ nguyên doc gốc §3.3/§3.5, không sửa: đánh giá hằng ngày · kết nạp/loại-thanh-khoản có hiệu lực
**thứ Hai kế tiếp** · loại cứng delist **ngay trong ngày** · `ruleset_version` tăng khi đổi rule,
không sửa tại chỗ · changelog `mike/kb/universe_ruleset.md` · mọi backtest in `ruleset_version` +
**SHA hash của tập membership** vào log và pin vào `results_registry.md`.

Nhấn mạnh **hash membership**: đây là thứ lẽ ra đã bắt được sự cố drift ngay lập tức, và là biện
pháp duy nhất trong toàn bộ phương án này ngăn được vấn đề tương tự tái diễn với **bất kỳ** nguồn dữ
liệu nào trong tương lai, không riêng universe.

---

## 4. MIGRATION — PRODUCTION

### 4.1 Phân loại consumer theo cách dùng (quyết định độ khó, không phải tên file)

Khảo sát repo: `ticker_prune` xuất hiện ở **~50 file ngoài `archive/`**. Nhưng chỉ **3 dạng dùng**:

| Dạng | Ý nghĩa | Cách thay | Độ khó |
|---|---|---|---|
| **D1 — membership** `IN (SELECT DISTINCT ticker FROM ticker_prune)` | Look-ahead §2.2 | `EXISTS(... u.ticker=t.ticker AND u.time=t.time AND u.in_universe)` | Dễ, cơ học |
| **D2 — row source** `FROM ticker_prune p` | Dùng bảng làm nguồn dòng | `FROM ticker t JOIN universe_pit u USING(ticker,time) WHERE u.in_universe` | Dễ (§2.1: không mất cột) |
| **D3 — health gate** đếm mã/lag của chính bảng | Giám sát ETL upstream | Chuyển sang giám sát `ticker` + `universe_pit` | Cần suy nghĩ, xem §4.5 |

### 4.2 Consumer production — thứ tự cutover

Sắp theo **rủi ro tăng dần**, cố ý: làm cái an toàn trước để tích lũy niềm tin vào lớp mới.

| # | File | Dạng | Ảnh hưởng LIVE | Ghi chú |
|---|---|---|---|---|
| P1 | `trading_bot/due_diligence.py` (6 chỗ) | D1 (đọc `bq_cache/ticker_prune/*.parquet`) | **Không** — chỉ hiện cờ cho người đọc | Làm đầu tiên. Sai cũng chỉ sai 1 dòng nhãn. |
| P2 | `custom_basket.py` (114, 202, 656) | D1 × 3 | custom30V — parking NEUTRAL | Universe rộng hơn ~17% ⇒ rổ 30 mã có thể đổi thành phần. Cần A/B rổ trước-sau, **không cutover mù**. |
| P3 | `deploy_golive_dt5g_v4/golive_recommend_v23.py` 290/293 | D1 (banking sector-lens) | Thấp | |
| P4 | `golive_recommend_v23.py` 167/425/455 | D2 (ADV cap, breadth, pool pbz CAPIT) | **CAO — xem §4.4** | Không làm cùng lô với P1-P3. |
| P5 | `macro_state_live.py` (breadth Pillar B guard, %>MA200, cần ≥100 mã) | D2 | **CAO** — chạm DT5G | Đổi mẫu số breadth ⇒ có thể đổi state. Bắt buộc chạy song song đối chiếu chuỗi state 2014→nay, yêu cầu **0 phiên lệch** trước khi cutover. |
| P6 | `mike/bin/preflight_check.sh`, `bq_freshness_check.sh` | D3 | Gate vận hành | §4.5 |
| P7 | `book_c_signal.py`, `recommend_holistic.py`, `pt_v4_dt5g.py`, `pt_v22_dt5g.py`… | D1/D2 | Paper/research | Sau cùng, không chặn. |

**Không mass-edit ~50 file** (`coding_guidelines.md` §3). Chỉ P1-P6 + backtest canonical (§5). Phần
còn lại là script research phần lớn đã chết — xử lý theo `coding_guidelines.md` §10 (archive), không
phải sửa.

### 4.3 Có cần chạy song song (shadow) không? — CÓ, nhưng chỉ cho P4/P5

Chạy shadow toàn bộ là lãng phí; chạy shadow cho P4/P5 là bắt buộc.

- **P1-P3**: không shadow. Thay bằng **A/B tĩnh 1 lần**: xuất rổ/danh sách trước-sau tại ~10 ngày
  lịch sử + hôm nay, người đọc duyệt diff. Diff rỗng hoặc giải thích được ⇒ cutover.
- **P4/P5**: **shadow ≥10 phiên giao dịch**. Ghi song song 2 chuỗi (`_prune` và `_pit`) vào file
  quan sát, **không** để chuỗi mới điều khiển quyết định nào. Điều kiện cutover: (i) 0 phiên lệch
  state DT5G, (ii) breadth CAPIT đã hiệu chuẩn lại xong (§4.4), (iii) quant-skeptic CONFIRMED.
- **Rollback**: mỗi file cutover thêm 1 hằng số module-level `UNIVERSE_SOURCE = "pit" | "prune"`
  (không phải env var — env var thừa hưởng qua process là đúng cơ chế đã gây sự cố C1 07-12,
  `coding_guidelines.md` §11). Rollback = đổi 1 hằng số + rerun. **Fail-safe: nếu `universe_pit`
  thiếu ngày cần dùng → DỪNG CÓ LỖI, tuyệt đối không tự fallback về `ticker_prune`** — fallback im
  lặng sẽ tái nhập đúng cái drift ta đang bỏ chạy.

### 4.4 ⚠️ Hạng mục nguy hiểm nhất: CAPIT breadth + `WASHOUT_GATE=0.30`

`golive_recommend_v23.py:655` tính breadth = tỷ lệ mã có `D_RSI<0.3` **trên mẫu số `ticker_prune`**.
Universe mới rộng hơn ~17% ⇒ **cùng một ngày thị trường sẽ ra một con số breadth khác**. Ngưỡng 0,30
được hiệu chuẩn trên mẫu số cũ.

Bối cảnh làm việc này khẩn: breadth đang bò lên (0,166 ngày 07-13 → 0,2176 ngày 07-17), CAPIT là
nguồn vốn CHỐT đang chờ fire, và `capit_grind` còn ở thế knife-edge 91 phiên vs cửa sổ 20-90 (lệch 1
phiên ⇒ size 0,75 thay vì 0,375). **Đổi mẫu số breadth mà không đổi ngưỡng = âm thầm đổi cả xác suất
kích hoạt lẫn size của một lệnh mua thật.**

Quy tắc bắt buộc, đề xuất user duyệt riêng khoản này:
1. Tính lại chuỗi breadth 2014→nay trên **cả 2 mẫu số**, đặt cạnh nhau.
2. Xác định ngưỡng mới `WASHOUT_GATE'` sao cho **tập ngày fire lịch sử không đổi** (bảo toàn hành vi,
   không tối ưu lại — đây là re-hiệu-chuẩn, KHÔNG phải cơ hội tune. Tune ngưỡng ở đây = thêm N-trial
   vào một tham số đang trực tiếp điều khiển tiền thật).
3. Nếu **không** tồn tại ngưỡng nào bảo toàn được tập ngày fire ⇒ **DỪNG, escalate user** — nghĩa là
   đổi universe thật sự đổi hành vi CAPIT, và đó là quyết định của người, không phải của migration.
4. **Không cutover P4 trong lúc `capit_fired=true`.** Thêm điều kiện chặn này vào chính bước cutover.

Gợi ý an toàn nhất: **để CAPIT breadth ở lại `ticker_prune` một cách CÓ CHỦ Ý và ghi rõ trong code**
cho tới khi hoàn tất bước 1-2 ở trên. Một pin "cố tình dùng nguồn cũ, có lý do, có ngày hết hạn" an
toàn hơn nhiều so với một lần đổi mẫu số vô tình.

### 4.5 D3 — gate vận hành (P6) sau khi prod không còn đọc `ticker_prune`

Hiện `preflight_check.sh` + `bq_freshness_check.sh` gác **lag + depth của `ticker_prune`**
(`MIN_PRUNE_NAMES=200`, "bình thường ~225-265") — dựng sau sự cố ghi-đè 07-15.

Sau migration, các gate này gác **nhầm bảng**: production không còn phụ thuộc `ticker_prune` nữa,
nhưng lại phụ thuộc `ticker` (mà hiện **chưa ai gác depth**). Xử lý:
- **Thêm** gate lag + depth cho `ticker` (ngưỡng dựng lại từ lịch sử `ticker`, không copy 200/225-265
  vốn là ngưỡng của prune).
- **Thêm** gate `universe_pit` đã có dòng cho ngày giao dịch gần nhất.
- **Giữ** gate `ticker_prune` ở mức WARN (không BLOCK) trong ~1 tháng sau cutover — nó vẫn là chỉ báo
  sức khỏe ETL upstream hữu ích. Rồi gỡ.
- Cập nhật `mike/kb/cron_registry.md` **trong cùng commit** (`coding_guidelines.md` §11).

---

## 5. MIGRATION — BACKTEST / PIN

### 5.1 Có cần re-pin R3 không? — **CÓ.** Câu trả lời đã đổi so với doc gốc.

Doc gốc §4.1 đề xuất "A/B đo trước rồi mới quyết". Cơ sở của thái độ chờ đó là *"chưa biết curation
có mang thông tin thật không, và chưa biết độ lớn look-ahead"*. **Cả hai ẩn số đó nay đã đóng:**

| Ẩn số hôm qua | Hôm nay |
|---|---|
| Curation của bq_admin có mang thông tin ta không có? | **Không** — prune ⊂ rule, recall 97-99% (§2.2b) |
| Nguồn của membership là gì? | **`hit_ticker_list.csv` suy từ chính kết quả backtest cũ** (bq_admin xác nhận) |
| Độ lớn look-ahead? | **1,4×–2,3× số mã** (§2.2c) |
| Universe có tái lập được không? | **Không** — IVS 0 → 1.622 dòng trong 8 ngày |

Điểm quyết định không phải "27,84% cao hay thấp hơn thực tế bao nhiêu" — mà là: **một con số tính
trên universe (a) chứa thiên vị vòng tròn từ chính backtest và (b) không tái lập được giữa hai lần
chạy, thì không đủ tư cách làm baseline production, bất kể giá trị của nó.** Không có ngưỡng "lệch
≲1pp thì bỏ qua" nào cứu được tính chất (b).

**A/B vẫn chạy, nhưng đổi vai:** từ *cổng quyết định* → *chẩn đoán độ lớn để đặt lại kỳ vọng*. Và nó
miễn phí: lần re-pin sinh ra cả `R3_prune_union` (control) lẫn `R3_pit` (mới) trong cùng một đợt.

### 5.2 Ưu tiên: CAO nhưng KHÔNG khẩn cấp — và lý do phân biệt

- **Không khẩn** vì đường LIVE không sizing theo CAGR pin. Universe sai không đặt sai lệnh hôm nay;
  nó làm sai **kỳ vọng** và làm sai **cách ta so sánh các thay đổi tương lai**.
- **Cao** vì mọi quyết định R&D đang neo vào baseline này, và mỗi tuần trôi qua lại thêm kết luận
  chồng lên nó.

⚠️ **Trong thời gian chờ re-pin, phát biểu đúng về con số chính thức:** hiện `results_registry.md`
pin **R3 = 27,84%**, và context_pack đang ghi khoảng trung thực **[~27,2%; ~31,3%]** (từ vụ LAG %ADV
07-22). Phải thêm một cảnh báo thứ ba: **cả khoảng đó cũng tính trên universe có bias vòng tròn.**
Đề xuất: đánh dấu R3 trong registry là **`PROVISIONAL — universe under migration`** ngay khi user
duyệt phương án này, trước cả khi bắt đầu implement. Rẻ, và ngăn được việc trích dẫn con số như đã
kiểm chứng trong 2-3 tuần tới.

### 5.3 Các N-trial đã pin tuần qua — phần lớn KHÔNG cần chạy lại

Đây là điểm giảm nhẹ quan trọng, xin nói rõ để không hoảng quá mức:

- Các kết luận tuần qua (LAG %ADV gate +4,11pp · lọc thanh khoản LAG · CAPIT participation cap ·
  asymmetric beta · exit-signal) hầu hết là **A/B trên CÙNG một universe**. Bias universe xuất hiện
  ở **cả hai nhánh** ⇒ **delta phần lớn được bảo toàn**, chỉ **mức tuyệt đối** là sai.
- ⇒ Việc cần làm là **rà soát**, không phải chạy lại tất cả. Tiêu chí phải chạy lại: kết luận nào mà
  **bản thân universe là biến can thiệp**. Ứng viên rõ nhất: **lọc thanh khoản LAG** (`lag_filter_
  illiquid`, commit `4b7aaa1`) — nó lọc chính theo thanh khoản, mà B3/B4 của `universe_pit` cũng lọc
  theo thanh khoản ⇒ **hai lớp chồng nhau, khả năng cao thành thừa hoặc lệch**. Phải đo lại sau khi
  có `universe_pit`.
- Ứng viên thứ hai: mọi kết luận về mã **ngoài** `ticker_prune` (TMG `Volume_3M_P50=0`, IVS) — chính
  là các mã mà universe mới định nghĩa lại tư cách.

---

## 6. TIMELINE & EFFORT

Đơn vị "phiên" = 1 phiên làm việc tập trung của Taylor (~2-4h agent-time). Ước lượng có nêu độ tin cậy.

| Giai đoạn | Việc | Effort | Tin cậy | Chặn bởi |
|---|---|---|---|---|
| **G0** | Lấy lại văn bản gốc Q&A bq_admin (§0); đánh dấu R3 `PROVISIONAL` (§5.2) | <0,5 phiên | Cao | User |
| **G1** | `bin/build_universe_pit.py` + selfcheck (idempotent, atomic, B8) | 1-1,5 phiên | Cao | — |
| **G2** | Backfill 2000→nay (compute rẻ: 215MB) + **kiểm định**: chạy lại bảng §2.2 với median-60-phiên tự tính, ~30 mốc | **1 phiên** (compute ~phút, kiểm định chiếm hết) | Cao | G1 |
| **G3** | P1-P3 cutover + A/B tĩnh rổ custom30V | 1 phiên | Trung bình (phụ thuộc diff rổ lớn hay nhỏ) | G2 |
| **G4** | **Re-hiệu chuẩn breadth CAPIT (§4.4)** — chuỗi 2014→nay, tìm `WASHOUT_GATE'` bảo toàn tập ngày fire | 1 phiên | **Thấp** — có thể không tồn tại ngưỡng bảo toàn ⇒ escalate | G2 |
| **G5** | Shadow P4/P5 ≥10 phiên (chi phí *thời gian lịch*, gần như không tốn effort) | ~2 tuần lịch, 0,5 phiên | Cao | G4 |
| **G6** | Re-pin R3: 2 lần chạy (control + pit) theo **đúng lệnh pin + `$DNA_PYEXE`** (`coding_guidelines.md` §8) | 1-2 phiên + runtime | **Thấp** — chưa đo runtime thật của lệnh pin trong job này | G2 |
| **G7** | Rà soát N-trial (§5.3) — phân loại giữ/chạy-lại, chạy lại LAG-liquidity | 1-2 phiên | Thấp | G6 |
| **G8** | P6 gate + `data_registry.md`(prune→TRAP, pit→CANONICAL) + `cron_registry.md` + `coding_guidelines.md` (cấm dạng `DISTINCT` không điều kiện thời gian) + `universe_ruleset.md` v1 | 1 phiên | Cao | G3,G5 |
| **G9** | quant-skeptic full review | — | — | G6,G7 |

**Đường găng ≈ 2,5-3 tuần lịch**, trong đó ~8-11 phiên làm việc thật; phần còn lại là thời gian
shadow. **G1+G2+G3 (≈3 phiên) đã đủ khử được vấn đề nghiêm trọng nhất (non-reproducibility) cho mọi
việc mới** — nếu user muốn chia nhỏ phê duyệt, đây là điểm cắt tự nhiên.

⚠️ Hai ước lượng tôi **không** tự tin và không muốn bị trích như đã đo: **G4** (có thể bế tắc, phải
escalate) và **G6** (chưa đo runtime lệnh pin R3 trong job này — nên hỏi lại trước khi đưa vào lịch).

---

## 7. 5 VẤN ĐỀ ETL PHỤ CỦA bq_admin — **KHÔNG xác nhận được giả định "không liên quan"**

Dispatch nêu giả định: *"lớp mới đọc thẳng `ticker` không qua `ticker_prune`, nên các bug này có lẽ
KHÔNG còn liên quan — verify giả định này."*

**Kết quả verify: giả định này chỉ đúng nếu các bug nằm riêng ở load job của `ticker_prune`. Tôi
không xác minh được điều đó, và có lý do thực chất để nghi ngờ nó SAI.**

| Vấn đề | Liên quan tới `universe_pit`? | Lập luận |
|---|---|---|
| `max_bad_records=10` im lặng | **CÓ THỂ CÓ** | Đây là tham số của **load job**, không phải của bảng đích. Nếu `ticker` được nạp bằng load job có cùng cấu hình (rất hợp lý — cùng pipeline), thì `ticker` cũng âm thầm mất tới 10 dòng/lần nạp. `universe_pit` đọc `ticker` ⇒ **thừa hưởng nguyên vẹn**. |
| GCS cleanup bị comment | **CÓ THỂ CÓ** | File cũ tồn đọng trong bucket ⇒ rủi ro nạp lại/nạp trùng. Ảnh hưởng **mọi** bảng nạp từ đường GCS đó, không riêng prune. |
| `is_skip` không nhất quán | **Chưa xác định** | Không biết cờ này lọc ở tầng nào (nguồn hay riêng bước prune). |
| (2 vấn đề còn lại) | **Không biết** | Bản tóm tắt không nêu tên. |

**Bằng chứng ủng hộ phía "có liên quan"**: sự cố 07-14/15 làm hỏng **cả `ticker_financial` LẪN
`ticker_prune`** (rows 07-08→07-14 bị xoá/ghi đè) — nghĩa là chế độ hỏng của pipeline này **không**
bị giới hạn ở `ticker_prune`. Không có cơ sở nào để tin `ticker` miễn nhiễm.

**Kết luận:** `universe_pit` giải quyết dứt điểm hai vấn đề **membership** (bias vòng tròn +
non-reproducibility). Nó **không** giải quyết vấn đề **toàn vẹn dữ liệu thô**, và không nên được bán
cho user như thể có. Vì vậy **B8 (§3.3) không phải tính năng thêm cho vui — nó là thứ bù đắp đúng
khoảng trống này**, và là lý do tôi từ chối viết builder không có nó.

**Hai việc cần làm (không chặn G1-G3):**
1. Hỏi lại bq_admin **đúng một câu**: *"`max_bad_records=10` và đường GCS đó áp cho load job của
   những bảng nào — có gồm `tav2_bq.ticker` không?"*
2. Đưa depth/lag gate cho `ticker` vào P6 (§4.5) — bảo hiểm đúng chỗ, độc lập với câu trả lời.

---

## 8. RỦI RO CỦA CHÍNH PHƯƠNG ÁN NÀY (nói thẳng)

1. **43 mã "rule-only" chưa được đánh giá chất lượng.** §2.2b chứng minh curation không thêm phạm
   vi, **không** chứng minh phần rule thêm ra là tốt. Universe rộng hơn 17% ⇒ nhiều ứng viên mua hơn
   ⇒ tương tác với mandate due-diligence toàn-diện (user 2026-07-21) và với trần vị thế LAG đang treo
   (concurrency thực 16-17, không phải 12). **Cần liệt kê 43 mã đó cho người đọc trước khi cutover
   P2/P4** — rẻ, và là đúng tinh thần mandate due-diligence.
2. **§2.2 đo bằng `Volume_3M_P50` dựng sẵn, không phải median-60-phiên tự tính** (§3.2). Recall
   97-99% có thể xê dịch. Chưa phải kết quả cuối.
3. **`n=1` mốc cho sweep ngưỡng** (chỉ 2026-06-15). Cao nguyên 5e8-1e9 nên kiểm ở vài mốc lịch sử
   nữa trong G2 trước khi khoá B3.
4. **Rủi ro con người, không phải kỹ thuật: đây là lúc rất dễ tune.** Ta đang tự viết lại universe
   cho một hệ đã biết kết quả lịch sử. Mọi tham số universe (ngưỡng B3, `WASHOUT_GATE'`) phải chốt
   theo tiêu chí **tái tạo/bảo toàn hành vi**, không theo CAGR. Nếu ai đó (kể cả tôi) đề xuất đổi B3
   vì "backtest đẹp hơn" — đó là dấu hiệu dừng, không phải tiến bộ. Đề nghị quant-skeptic soi riêng
   điểm này.
5. **Kỳ vọng cần đặt lại ngay từ bây giờ: R3 mới nhiều khả năng THẤP HƠN 27,84%** (universe co lại,
   bỏ bớt mã thiên vị-về-phía-sinh-deal). Nếu con số mới **cao hơn**, đó là **dấu hiệu nghi ngờ**,
   phải điều tra chứ không phải ăn mừng.
6. Chưa có ý kiến Winston (khả thi vận hành, chạy song song) — phương án này chưa hoàn chỉnh nếu
   thiếu.

---

## 9. CẦN USER DUYỆT GÌ TRƯỚC KHI IMPLEMENT

| # | Quyết định | Khuyến nghị Taylor |
|---|---|---|
| Q1 | Chấp nhận hướng `universe_pit` tự xây (không mirror `ticker_prune`) | **CÓ** — bq_admin + số đo §2.2 đồng thuận |
| Q2 | Chốt B3 = 1,0 tỷ VND/ngày (thực, neo 2026, khử lạm phát 7%) làm v1, hiệu chuẩn theo **recall**, không theo CAGR | **CÓ** |
| Q3 | Đánh dấu R3 27,84% là `PROVISIONAL` trong `results_registry.md` **ngay**, trước khi implement | **CÓ** — rẻ, ngăn trích dẫn sai trong 2-3 tuần tới |
| Q4 | Chấp nhận re-pin R3 (2 lần chạy) + rà soát N-trial tuần qua | **CÓ**, ưu tiên cao-không-khẩn |
| Q5 | **CAPIT: cho phép giữ breadth ở `ticker_prune` CÓ CHỦ Ý cho tới khi re-hiệu-chuẩn xong**, và cấm cutover P4 khi `capit_fired=true` | **CÓ** — đây là khoản chạm tiền thật, xin duyệt riêng |
| Q6 | Nếu G4 không tìm được `WASHOUT_GATE'` bảo toàn tập ngày fire → dừng và hỏi user, không tự chọn ngưỡng | **CÓ** |
| Q7 | Cho phép sửa `data_registry.md` / `coding_guidelines.md` / `cron_registry.md` kèm theo | **CÓ** |
| Q8 | Gửi bq_admin 1 câu hỏi bổ sung (§7: `max_bad_records`/GCS có áp cho `ticker` không) | **CÓ** |

**Không xin duyệt trong tài liệu này** (chưa đủ dữ liệu): sửa trần vị thế LAG (12 vs 16-17 thực),
đổi bất kỳ tham số chiến lược nào, đụng vào 43 mã rule-only ở tầng sizing.

---

## 10. VIỆC KẾ TIẾP (nếu duyệt)

1. Lấy lại văn bản gốc Q&A bq_admin → lưu đúng đường dẫn → đọc lại §7 (G0).
2. Winston: đánh giá khả thi vận hành (cron slot cho builder, tương tác `sync_bq_cache_daily.sh`
   23:45, `bq_cache` có cần thêm `universe_pit` không).
3. quant-skeptic: review phương án này, soi riêng §2.2 (recall có bị tôi vô tình tune không) và §8.4.
4. Sau khi đủ 2 review → trình user quyết Q1-Q8 → bắt đầu G1.
