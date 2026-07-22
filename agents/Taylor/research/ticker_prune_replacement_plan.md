# PHƯƠNG ÁN THAY THẾ `ticker_prune` — kiến trúc, migration, timeline

Job `Taylor_20260722_033547` · 2026-07-22 · Taylor (Quant, lead)
Tiền thân: `ticker_prune_universe_governance.md` (job `Taylor_20260721_162005`) + phản hồi bq_admin.
**Trạng thái: ĐỀ XUẤT QUYẾT ĐỊNH. Chưa implement dòng code nào. Chờ Winston (khả thi vận hành) +
quant-skeptic review → user duyệt.**

---

## ⚠️ 0. Cảnh báo về nguồn — **ĐÃ GIẢI QUYẾT, giữ lại làm dấu vết**

> **CẬP NHẬT 2026-07-22:** file **CÓ tồn tại** —
> `agents/Taylor/research/ticker_prune_universe_QA_bq_admin_20260722.md` (21 KB, ghi lúc 03:45,
> đúng bằng thời điểm tôi ghi finding 03:45:34Z ⇒ **race giữa hai tiến trình, không phải file thiếu**).
> Cảnh báo bên dưới đã lỗi thời. Đọc lại văn bản gốc: bản tóm tắt của Mike **khớp** ở các điểm 1-3
> và 5 (không phải sửa gì trong §3-§6), **và §7 vẫn đứng vững** — Phần 4 mục 5 của văn bản gốc nêu
> `max_bad_records=10` mà **không giới hạn cho bảng nào**, nên câu hỏi Q8 là cần thiết. Q8 nay **đã
> có trả lời** (bq_admin, 04:12 ICT) — xem §7.

<details><summary>Cảnh báo gốc (đã lỗi thời, giữ để truy vết)</summary>

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

</details>

---

## 1. TL;DR — 5 câu

1. **Đồng ý hoàn toàn với bq_admin: đừng mirror, tự xây.** Nhưng lý do quyết định KHÔNG phải bias
   (bias là hệ quả) — mà là **`ticker_prune` không tái lập được (non-reproducible)**. Một baseline
   thay đổi sau lưng thì không phải baseline, bất kể nó đúng hay sai.
2. **Nỗi lo lớn nhất trong doc gốc (§5: "rule thanh khoản thuần của ta có thể THUA curation của
   bq_admin") — ⚠️ ĐÃ ĐO LẠI ĐÚNG CÁCH, và câu trả lời NGƯỢC với bản trước: nỗi lo đó CÓ CƠ SỞ.**
   Bản trước dùng recall 97-99% để bác bỏ §5 — quant-skeptic REFUTED (cao): phép đo đó là
   **tautology** (`Inflation_7` là deflator neo 2026 ⇒ rule tôi viết trùng khớp đại số với chính
   row-filter production tạo ra prune ⇒ "prune ⊆ rule" đúng bất kể curation có nghĩa hay không; dùng
   đúng công thức gốc thì recall = **100,0%**). Phép test thay thế **có sức mạnh** (§2.4): 43 mã
   "rule-only" có `ROE_Min3Y` **âm trung bình** (−5,8% vs +4,9%), `ROE5Y` chỉ **1/3** nhóm được giữ,
   nhất quán ở **cả 4 mốc** và **không phải hiệu ứng quy mô**. ⇒ **Rule thanh khoản thuần KHÔNG đủ**;
   cần một lớp chất lượng ex-ante trước khi chạm tiền thật (§3.2b). Tin tốt: thông tin đó **không bí
   mật** — nằm trong cột ta đã có; và curation cũng **bỏ sót** mã tốt mới lên sàn (FOX ROE5Y 31%,
   VPL, VGI) nên nó không phải chuẩn vàng để bắt chước.
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

### 2.2 Recall của rule so với `ticker_prune` — ⚠️ ĐÃ SỬA sau review quant-skeptic (REFUTED, cao)

> **ĐÍNH CHÍNH (2026-07-22, job `Taylor_20260722_041743`).** Bản trước của mục này dùng con số
> recall 97-99% để tuyên bố "curation là TRỪ không phải CỘNG ⇒ nỗi lo §5 doc gốc KHÔNG được dữ liệu
> ủng hộ". **Tuyên bố đó VOID.** quant-skeptic (`mike/logs/verify_20260722_040031.log`) chỉ ra:
> `Inflation_7` là **hệ số khử lạm phát neo 2026** (đo được: 2026 = 1,0; 2014 = 0,4186-0,4501;
> `1/1,07¹² = 0,444`), nên B3 tôi viết (`Volume_3M_P50 × Price ≥ 1e9 × Inflation_7`) **đại số trùng
> khớp** với chính row-filter production tạo ra `ticker_prune`, nằm sẵn ở `filter.json:18`
> (`(Volume_3M_P50*Price/Inflation_7)>1000000000.0`). Đó KHÔNG phải một tái tạo độc lập — đó là hằng
> số của chính repo này.
>
> Vì `ticker_prune = hit_ticker_list ∩ liquidity_filter`, mệnh đề "prune ⊆ rule" là **đồng nhất thức
> cấu trúc**: nó đúng bất kể `hit_ticker_list` mang thông tin thật hay được bốc ngẫu nhiên. Chạy
> ĐÚNG công thức gốc cho recall **chính xác 100,0%** tại cả 3 mốc kiểm tra lại (140/140, 180/180,
> 233/233). Phần thiếu 1-3% trong bảng dưới **không phải tín hiệu về curation** — nó là **độ lệch
> công thức** giữa row-filter production và spec median-60-phiên tôi đề xuất (`COALESCE(Price,Close)`,
> `ICB_Code IS NOT NULL`).
>
> Hệ quả logic: phép test này có **sức mạnh thống kê bằng 0** đối với §5 doc gốc — vì §5 lo đúng về
> **phép TRỪ** (curation loại mã diện cảnh báo/kiểm soát/BCTC ngoại trừ), mà một phép đo chỉ có thể
> quan sát được phép trừ thì không thể bác bỏ giả thuyết phép trừ. Cả hai giả thuyết ("curation vô
> nghĩa" và "curation lọc đúng mã xấu thật") cho **cùng một kết quả**. Câu hỏi §5 vì vậy vẫn **MỞ**
> ở thời điểm đó — và được trả lời riêng ở **§2.4** bằng một phép test có sức mạnh thật.
>
> Giữ bảng dưới lại vì nó vẫn hữu ích cho đúng mục đích ban đầu: **đo độ lệch giữa spec đề xuất và
> row-filter production**. Không được trích dẫn nó như bằng chứng về chất lượng curation.

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

Ba kết luận rút ra:

**(a) Ngưỡng 1e9 là cao nguyên, không phải đỉnh nhọn — nay có n=3 mốc, không còn n=1.** Sweep gốc
tại 2026-06-15: 2e8→421 mã, 5e8→336, **1e9→273**, 2e9→220 (recall 82,8%), 5e9→171. quant-skeptic mở
rộng sang 2018-06-29 và 2022-06-30: recall tại **1e9 = 98,9% / 99,1%**, tại **2e9 = 80,6% / 87,2%**.
Cao nguyên giữ nguyên hình dạng ở cả 3 mốc ⇒ **rủi ro tự-flag #3 (§8.3) được giải quyết theo hướng
có lợi**.
⚠️ Nhưng phải nói lại cho đúng: khung "ngưỡng này tôi bốc ra TRƯỚC khi đo, không phải tuning" là
**diễn giải sai**. 1e9 không phải một phỏng đoán độc lập tình cờ trúng — nó là **hằng số đã hardcode
sẵn trong chính hệ đang được đo** (`filter.json:18`, `deeplearning/bigquery.py:261-265`). Điều này
không làm nó tệ đi (dùng lại hằng số production là đúng tinh thần "bảo toàn hành vi"), nhưng nó
KHÔNG phải bằng chứng chống overfit.

**(b) ⚠️ MỤC NÀY ĐÃ BỊ XÓA — tuyên bố cũ VOID.** Bản trước viết: *"Curation của bq_admin là TRỪ
không phải CỘNG ⇒ họ không biết thêm điều gì mà ta không biết ⇒ nỗi lo §5 doc gốc không được dữ liệu
ủng hộ."* Như hộp đính chính đầu §2.2 giải thích, phép đo dùng để chống lưng cho câu này là một
**tautology** — nó đúng 100% bất kể curation có thông tin hay không, nên **không kết luận được gì**
theo cả hai hướng. Câu hỏi §5 được trả lời riêng ở **§2.4**, bằng dữ liệu mà rule thanh khoản không
nhìn thấy. Kết quả ở §2.4 đi **ngược** với tuyên bố cũ: curation **CÓ** mang thông tin thật.

**(c) Look-ahead lớn hơn số cũ: 2,7× tại 2018 (không phải 2,3×).** Số cũ so `n_rule` PIT với `n_union`
lấy từ doc gốc (459 tại 2018). Sai mẫu số. Dạng gọi mà code **thực sự đang chạy** là
`IN (SELECT DISTINCT ticker FROM ticker_prune)` — `pt_v23_audit_2014.py:670/736/765/848` và ~20 file
khác — **không có bất kỳ điều kiện thời gian nào**. Mẫu số thật vì vậy là **543 mã từng có mặt bất kỳ
lúc nào trong lịch sử prune**, đo lại hôm nay:

```sql
SELECT COUNT(DISTINCT ticker) FROM tav2_bq.ticker_prune                          → 543   (mẫu số code thật dùng)
SELECT COUNT(DISTINCT ticker) FROM tav2_bq.ticker_prune WHERE time<=DATE"2018-06-29" → 381
```

⇒ **543 vs `n_rule` PIT 198 tại 2018 = 2,74×.** Backtest hiện tại cho phép mua gần **gấp ba** số mã
lẽ ra được phép tại thời điểm đó. Kết hợp với `hit_ticker_list.csv` suy từ chính kết quả backtest cũ
⇒ phần phồng thêm **thiên vị về phía mã từng sinh deal** = circular selection bias đúng định nghĩa.

📌 **Ghi chú riêng, tự nó là bằng chứng:** con số 459 (ever-đến-2018) trong doc gốc **không tái lập
được hôm nay — nay là 381**. Không ai sửa gì; bảng nguồn tự đổi dưới chân. Đây là minh chứng sống,
đo được, cho chính vấn đề non-reproducibility mà `universe_pit` sinh ra để giải quyết — và là lý do
mọi con số trích từ doc cũ phải đo lại chứ không chép.

### 2.4 ⚠️ Phép test CÓ sức mạnh: 43 mã "rule-only" có chất lượng KÉM RÕ RỆT — §5 doc gốc ĐƯỢC XÁC NHẬN

Đây là phép test thay thế cho §2.2 (theo `recommended_reruns` của quant-skeptic). Nguyên tắc: so 43
mã **rule-only** (qua rule thanh khoản nhưng KHÔNG có trong `ticker_prune`) với nhóm **BOTH** bằng
dữ liệu chất lượng mà **rule thanh khoản không nhìn thấy**.

**Kết quả A — chất lượng ex-ante (đo tại chính ngày đó, không look-ahead):**

| Ngày | Nhóm | n | ROE_Min3Y TB | % ROE_Min3Y<0 | ROE5Y TB | FSCORE TB |
|---|---|---|---|---|---|---|
| 2026-06-15 | BOTH | 230 | **+4,90%** | 6,5% | **11,85%** | 4,40 |
| 2026-06-15 | **RULE_ONLY** | **43** | **−5,83%** | **30,2%** | **3,56%** | 4,74 |
| 2014-06-30 | BOTH | 138 | +2,93% | 22,5% | 12,47% | 4,56 |
| 2014-06-30 | **RULE_ONLY** | **30** | **−14,12%** | **60,0%** | **1,92%** | 5,03 |
| 2018-06-29 | BOTH | 178 | +9,23% | 5,6% | 14,37% | 4,22 |
| 2018-06-29 | **RULE_ONLY** | **21** | **−6,78%** | **23,8%** | **6,94%** | 4,55 |
| 2022-06-30 | BOTH | 318 | +6,75% | 8,5% | 13,72% | 4,38 |
| 2022-06-30 | **RULE_ONLY** | **84** | **−5,51%** | **29,8%** | **5,26%** | 4,46 |

Dấu **nhất quán ở cả 4 mốc**, không phải một lần may. **FSCORE KHÔNG phân biệt được** (rule-only đôi
khi còn cao hơn) — nên đừng dùng FSCORE làm gate universe; ROE_Min3Y và ROE5Y mới là trục phân biệt.

**Không phải hiệu ứng quy mô.** Chia theo dải thanh khoản tại 2026-06-15, chênh lệch vẫn giữ nguyên
dấu trong từng dải (trừ dải C, n=7 quá nhỏ):

| Dải ADV | BOTH: ROE_Min3Y / %âm | RULE_ONLY: ROE_Min3Y / %âm |
|---|---|---|
| <2 tỷ | +4,4% / 14% (n=37) | −5,9% / **31%** (n=16) |
| 2-5 tỷ | −2,2% / 13% (n=39) | −13,6% / **50%** (n=10) |
| 5-15 tỷ | +0,4% / 7% (n=45) | +3,9% / 0% (n=7) |
| >15 tỷ | +9,5% / 2% (n=109) | −4,8% / **30%** (n=10) |

**Kết quả B — lợi suất 1 năm sau (ex-post):**

| Ngày | BOTH: TB / trung vị | RULE_ONLY: TB / trung vị |
|---|---|---|
| 2014-06-30 | +17,9% / +11,0% | **+3,4% / −16,2%** |
| 2018-06-29 | +6,3% / −1,4% | **−8,3% / −4,8%** |
| 2022-06-30 | −0,9% / −5,6% | **−19,9% / −19,2%** |

⚠️ **Kết quả B KHÔNG được dùng làm bằng chứng "curation khôn ngoan".** Nó bị nhiễm đúng thứ mà cả
tài liệu này đang tố cáo: `hit_ticker_list` suy từ deal backtest ⇒ mã trong prune **theo cấu trúc**
là mã đã tăng giá. Cả hai giả thuyết (curation-khôn-ngoan và circular-bias) đều dự đoán chênh lệch
này. Ghi lại để minh bạch, không để suy luận. **Kết quả A mới là phần có sức mạnh** — nó đo bằng dữ
liệu quá khứ tại chính ngày đó, và ta **có sẵn** các cột đó.

**Golden floor giải thích được phần lớn, nhưng KHÔNG hết.** Áp golden floor hiện hành của
`rating_8l` (`ROE_Min3Y ≥ 0 ∧ CF_OA > 0`) lên nhóm rule-only: loại **24/30 (2014), 16/21 (2018),
63/84 (2022), 32/43 (2026)** ≈ **70-76%**. Nhưng nhóm rule-only **qua được** golden floor vẫn thua
BOTH-qua-floor ở cả 3 mốc (−8,8% vs +21,7% · −11,3% vs +10,4% · −15,4% vs −1,7%) — n nhỏ (6/5/21) và
lại dính đúng confound circular ở trên, nên coi là **tín hiệu cảnh báo, không phải kết luận**.

**Đọc danh sách thật thì bức tranh có hai nửa** (43 mã tại 2026-06-15, xếp theo ADV — đây cũng là
danh sách §8.1 yêu cầu công bố trước P2/P4):

- **Nửa "curation ĐÚNG"** — mã lẽ ra không nên vào rổ: **HNG** (ROE_Min3Y −73,7%), **PIV** (−99,3%),
  **NVB** (−91,7%), **SBS** (−22,6%), **TTF** (−13,4%), **MSR** (−12,8%), **TIN** (−17,3%),
  **NRC** (−12,7%), và **VJC** — đã nằm trong danh sách **BANNED vĩnh viễn** của chính đội ta.
- **Nửa "curation SAI vì danh sách cũ"** — mã lớn, chất lượng tốt, **niêm yết/lên sàn gần đây** nên
  chưa kịp sinh deal trong backtest cũ: **FOX** (ADV 15 tỷ, ROE5Y **31,0%**), **VPL** (67 tỷ,
  FSCORE 8), **VGI** (52 tỷ, CF_OA dương lớn), **VIW**, **TDP**. Loại nhóm này là **MẤT**, không phải
  được — và đó chính là non-reproducibility/staleness của `hit_ticker_list`, không phải trí tuệ.

Còn lại là các mã nhỏ 1-8 tỷ ADV, chất lượng trung bình (`C69 DSE KOS CTF AAS AAV PPT L40 CDC STH
PSI PCH TLD TSA BIG SCG SGR THD AAH SBG FIR ASP MML RYG TAL DXS ORS BAF DSE VCK`).

**KẾT LUẬN §2.4 — trả lời dứt điểm §5 doc gốc:**
1. **Curation CÓ mang thông tin thật** (ngược tuyên bố cũ ở §2.2b). Rule thanh khoản thuần **KHÔNG
   đủ** để thay `ticker_prune` mà bảo toàn chất lượng universe.
2. **Nhưng thông tin đó KHÔNG bí mật** — nó nằm trong các cột ta đã có (`ROE_Min3Y`, `ROE5Y`,
   `CF_OA`). Không có bằng chứng bq_admin dùng nguồn ngoài (danh sách cảnh báo HOSE/HNX, BCTC ngoại
   trừ) mà ta không tra được. ⚠️ *Cũng không có bằng chứng ngược lại* — không tra được các nguồn đó
   trong BQ, nên đây là **chưa loại trừ**, không phải **đã loại trừ**.
3. **Curation cũng SAI theo hướng bỏ sót** (FOX/VPL/VGI) — nên nó không phải chuẩn vàng để bắt chước.
4. ⇒ **Hàm ý thiết kế bắt buộc**: trước khi `universe_pit` chạm P2/P4 (đường tiền thật), phải có
   **một lớp chất lượng ex-ante** — hoặc trong chính `universe_pit`, hoặc chứng minh được tầng chiến
   lược đã chặn đủ. Xem **§3.2b (mới)**.

📌 **Proxy hủy niêm yết: đo rồi, KHÔNG có sức mạnh — đừng dùng lại.** Đếm số mã không còn dòng nào
trong `ticker` ở cửa sổ T+12→T+15 tháng: **0/0 tại cả 3 mốc, cả hai nhóm.** `tav2_bq.ticker` giữ dòng
cho mọi mã bất kể tình trạng niêm yết ⇒ proxy này luôn cho 0, không phân biệt được gì. Muốn kiểm
delist/diện cảnh báo thật thì cần nguồn ngoài BQ (Winston) — chưa có, và §2.4 **không** dựa vào nó.

### 2.5 Chi phí backfill: không đáng kể

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
| B3 | VÀO: median trading value 60 phiên ≥ ngưỡng thực | 1,0 tỷ (*chưa hiệu chuẩn*) | **1,0 tỷ — giữ, có cơ sở** (§2.2a) | = hằng số production `filter.json:18`; cao nguyên n=3 mốc. **KHÔNG** còn viện dẫn "recall 97-99%" làm lý do (§2.2 đính chính) |
| B4 | RA: < 0,5 tỷ trong 20 phiên liên tiếp | ✔ | **giữ nguyên** | hysteresis bất đối xứng, cùng triết lý DT5G 4-gate |
| B5 | `Close ≥ 1.000 VND` | ✔ | **giữ nguyên** | |
| B6 | Loại cứng: vắng ≥10 phiên liên tiếp trong `ticker` | ✔ | **giữ nguyên** | delist/đình chỉ |
| B7 | Loại rồi phải đủ điều kiện lại từ đầu | ✔ | **giữ nguyên** | chống nhấp nháy |
| **B8** | — | *(không có)* | **MỚI: integrity gate** | xem §3.3 |

**Thay đổi thực chất:** thêm **B8** (§3.3), và thêm **hạng mục mở B-Q** (§3.2b) — hạng mục này SINH
RA từ kết quả §2.4 và **chưa có lời giải chốt**. Bộ tiêu chí còn lại đứng vững trước phản hồi
bq_admin — vì nó vốn đã được thiết kế để không phụ thuộc `ticker_prune`.

### 3.2b B-Q — lớp chất lượng ex-ante: HẠNG MỤC BẮT BUỘC, CHƯA CHỐT (mới, từ §2.4)

§2.4 đo được: rule thanh khoản thuần cho vào rổ ~43 mã (2026) / 84 mã (2022) có `ROE_Min3Y` **âm
trung bình** và `ROE5Y` chỉ bằng **1/3** nhóm được prune giữ. Vì vậy **B1-B8 thuần thanh khoản KHÔNG
đủ** cho P2/P4. Ba phương án, chưa chọn:

| PA | Nội dung | Ưu | Nhược |
|---|---|---|---|
| **Q-A** | **Không đụng `universe_pit`** — chứng minh tầng chiến lược đã chặn đủ (golden floor `rating_8l` loại 70-76% nhóm rule-only; VJC đã BANNED) | Giữ universe thuần "có giao dịch được không", đúng phân tầng trách nhiệm; **không thêm tham số mới nào** | Còn rò 24-30% qua floor; phải **đo thật** tỷ lệ rò tới tầng đặt lệnh, chưa đo |
| **Q-B** | Thêm B-Q vào `universe_pit`: loại khi `ROE_Min3Y < 0` ∧ `CF_OA ≤ 0` (2 điều kiện cùng lúc) | Chặn tận gốc, một chỗ | Trộn "chất lượng" vào tầng "thanh khoản" — sai phân tầng; **thêm 1 tham số có thể tune** ⇒ đúng cái bẫy §8.4 |
| **Q-C** | Giữ universe thuần, nhưng **xuất cờ** `quality_flag` trong `universe_pit` để tầng chiến lược/due-diligence đọc | Không đổi hành vi, minh bạch, khớp mandate due-diligence 2026-07-21 | Cần consumer chịu đọc cờ |

**Khuyến nghị Taylor: Q-A trước, Q-C kèm theo; KHÔNG làm Q-B.** Lý do: đúng nguyên tắc §8.4 (mọi
tham số universe phải chốt theo **bảo toàn hành vi**, không theo CAGR) — thêm ngưỡng ROE vào tầng
universe là mở đúng cánh cửa tự-tune mà tài liệu này cảnh báo. Nhưng Q-A **phải được đo, không được
giả định**: việc G2b (§6) = chạy `rating_8l` + `BANNED` + golden floor lên đúng 43/84 mã rule-only,
đếm còn bao nhiêu mã lọt tới tầng đặt lệnh. Nếu số rò đó **≠ ~0** ⇒ quay lại bàn Q-C/Q-B với user,
KHÔNG tự chọn.

**Cổng cứng:** cấm cutover P2/P4 khi hạng mục này chưa đóng. Đây là bổ sung thứ hai cho danh sách
cổng cứng, ngang hàng với cổng CAPIT §4.4.

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
| Curation của bq_admin có mang thông tin ta không có? | **CÓ thông tin thật, nhưng KHÔNG bí mật** — nhóm rule-only kém rõ rệt (ROE_Min3Y âm, ROE5Y ~1/3), song đo được bằng cột ta đã có (§2.4). ⚠️ *Đây là bản sửa: câu trả lời cũ "Không — recall 97-99%" là tautology, đã VOID (§2.2)* |
| Nguồn của membership là gì? | **`hit_ticker_list.csv` suy từ chính kết quả backtest cũ** (bq_admin xác nhận) |
| Độ lớn look-ahead? | **2,74× số mã tại 2018** (543-ever vs 198 PIT) — §2.2c |
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
| **G2b** | **(MỚI, từ §2.4/§3.2b)** Đo độ rò chất lượng: chạy `BANNED` + golden floor `rating_8l` lên đúng nhóm rule-only tại nhiều mốc, đếm số mã lọt tới tầng đặt lệnh. Ra ~0 ⇒ chốt Q-A; ra ≠0 ⇒ trình user chọn Q-C/Q-B | 0,5-1 phiên | Trung bình | G2 |
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

## 7. 5 VẤN ĐỀ ETL PHỤ CỦA bq_admin — **giả định "không liên quan" ĐÃ BỊ BÁC BỎ (bq_admin xác nhận)**

Dispatch nêu giả định: *"lớp mới đọc thẳng `ticker` không qua `ticker_prune`, nên các bug này có lẽ
KHÔNG còn liên quan — verify giả định này."*

**Kết quả verify: giả định SAI. Đã có xác nhận trực tiếp từ bq_admin.**

> **CẬP NHẬT 2026-07-22 04:12 ICT — trả lời Q8 của bq_admin** (Discord, kênh technical analysis),
> nguyên văn (**bản đầy đủ**, do Mike gửi lại 2026-07-22 — không đổi kết luận, chỉ rõ hơn bản tóm
> tắt trước): *"Nó chỉ là config của bigquery và được apply ở toàn bộ các bảng. Logic ở đây chỉ là
> một script update xóa và update lại toàn bộ dữ liệu và chỉ được chạy một lần với mục đích là
> INITIAL table và dữ liệu."*
>
> Bản đầy đủ làm rõ thêm một chi tiết **củng cố** kết luận 2 bên dưới: script không chỉ "update lại"
> mà **XÓA rồi update lại** toàn bộ dữ liệu. Đó đúng là ngữ nghĩa `WRITE_TRUNCATE` — mọi dòng lịch
> sử biến mất trước khi được ghi lại, nên một lần chạy lại ngoài ý muốn là mất dữ liệu toàn bảng,
> không phải sửa lệch vài dòng.
>
> Hai điều được chốt:
> 1. **`max_bad_records=10` áp cho MỌI bảng, gồm cả `tav2_bq.ticker`.** Không còn là "có thể có" —
>    **ĐÃ XÁC NHẬN CÓ**. `universe_pit` đọc `ticker` ⇒ thừa hưởng nguyên vẹn khả năng âm thầm mất tới
>    10 dòng mỗi lần nạp, **không có cảnh báo nào**.
> 2. Cơ chế `WRITE_TRUNCATE` (rebuild toàn bộ) là script **"chỉ chạy 1 lần để initial"**, không phải
>    job định kỳ. Nhưng nó **vẫn kích hoạt lại thủ công được** — và thực tế **đã xảy ra ngày 07-12**
>    (sự cố corruption `ticker_financial` + `ticker_prune`). "Chỉ chạy 1 lần theo thiết kế" ≠ "không
>    thể chạy lại"; kiểm soát nằm ở phía bq_admin, không ở phía ta.
>
> ⇒ **B8 (§3.3) không còn là bảo hiểm phòng hờ — nó là bắt buộc, chống một rủi ro ĐÃ XÁC NHẬN TỒN
> TẠI.** Tôi từ chối viết builder không có B8.

| Vấn đề | Liên quan tới `universe_pit`? | Lập luận |
|---|---|---|
| `max_bad_records=10` im lặng | **CÓ — ĐÃ XÁC NHẬN** | bq_admin: *"config của bigquery và được apply ở toàn bộ các bảng"*. `ticker` mất tới 10 dòng/lần nạp, im lặng. `universe_pit` đọc `ticker` ⇒ thừa hưởng. |
| GCS cleanup bị comment | **CÓ THỂ CÓ** | File cũ tồn đọng trong bucket ⇒ rủi ro nạp lại/nạp trùng. Ảnh hưởng **mọi** bảng nạp từ đường GCS đó, không riêng prune. Chưa hỏi riêng. |
| `is_skip` không nhất quán | **Chưa xác định** | Không biết cờ này lọc ở tầng nào (nguồn hay riêng bước prune). |
| (2 vấn đề còn lại) | **Không biết** | Chưa đối chiếu chi tiết với văn bản gốc. |

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

1. **43 mã "rule-only" — ĐÃ ĐÁNH GIÁ (§2.4), và kết quả XẤU hơn tôi tưởng.** Không còn là "chưa
   biết": nhóm này có `ROE_Min3Y` âm trung bình, `ROE5Y` bằng ~1/3 nhóm được prune giữ, nhất quán ở
   4 mốc và không phải hiệu ứng quy mô. Danh sách đầy đủ đã công bố ở §2.4 (đáp ứng yêu cầu "liệt kê
   trước cutover"). Rủi ro còn lại **chuyển dạng**: từ "chưa đo" → "**đã đo, cần lớp chất lượng
   ex-ante, chưa chốt dùng lớp nào**" (§3.2b, cổng cứng trước P2/P4). Vẫn tương tác với mandate
   due-diligence toàn-diện (user 2026-07-21) và trần vị thế LAG.
2. **§2.2 đo bằng `Volume_3M_P50` dựng sẵn, không phải median-60-phiên tự tính** (§3.2). Recall sẽ
   xê dịch khi chuyển sang spec tự tính. ⚠️ **Khi nó xê dịch, KHÔNG được tune B3 về lại cho recall
   đẹp** — recall so với prune giờ đã biết là **thước đo không có sức mạnh** (§2.2), nên "kéo recall
   lên" chính là tuning mù. Xem #4.
3. ~~**`n=1` mốc cho sweep ngưỡng**~~ — **ĐÃ ĐÓNG, có lợi.** quant-skeptic mở rộng sang 2018 và
   2022: recall tại 1e9 = 98,9% / 99,1%; tại 2e9 = 80,6% / 87,2%. Cao nguyên giữ ở **n=3 mốc**
   (§2.2a). Không cần kiểm thêm trong G2.
3b. **RỦI RO MỚI thay chỗ #3: sai lầm suy luận, không phải sai số đo.** Bản trước của tài liệu này
   đã đưa một tautology lên thành kết luận nền tảng ("curation vô nghĩa") và suýt để nó đông cứng
   thành đồng thuận của fleet. Bài học vận hành: **một phép đo khớp 97-99% với hệ thống đang đo là
   dấu hiệu nghi ngờ, không phải dấu hiệu thành công** — phải hỏi "phép đo này có thể ra kết quả
   khác được không?" trước khi ăn mừng. Nếu câu trả lời là không, nó không phải bằng chứng.
4. **Rủi ro con người, không phải kỹ thuật: đây là lúc rất dễ tune.** Ta đang tự viết lại universe
   cho một hệ đã biết kết quả lịch sử. Mọi tham số universe (ngưỡng B3, `WASHOUT_GATE'`) phải chốt
   theo tiêu chí **tái tạo/bảo toàn hành vi**, không theo CAGR. Nếu ai đó (kể cả tôi) đề xuất đổi B3
   vì "backtest đẹp hơn" — đó là dấu hiệu dừng, không phải tiến bộ. Đề nghị quant-skeptic soi riêng
   điểm này.
5. **Kỳ vọng cần đặt lại ngay từ bây giờ: R3 mới nhiều khả năng THẤP HƠN 27,84%** (universe co lại,
   bỏ bớt mã thiên vị-về-phía-sinh-deal). Nếu con số mới **cao hơn**, đó là **dấu hiệu nghi ngờ**,
   phải điều tra chứ không phải ăn mừng.
6. ~~Chưa có ý kiến Winston~~ — **ĐÃ CÓ** (bus 2026-07-22 03:48, `Winston_20260722_034...`): khả thi
   vận hành, chi phí ~0. Winston bổ sung một điểm quan trọng: **`ticker` CŨNG bị ghi đè lịch sử** —
   nghĩa là `universe_pit` phải **tự lưu snapshot bất biến** (append-only, đúng như §3.1 thiết kế),
   không được coi `ticker` là nguồn ổn định để tính lại bất cứ lúc nào. Củng cố thêm B8.

---

## 9. CẦN USER DUYỆT GÌ TRƯỚC KHI IMPLEMENT

| # | Quyết định | Khuyến nghị Taylor |
|---|---|---|
| Q1 | Chấp nhận hướng `universe_pit` tự xây (không mirror `ticker_prune`) | **CÓ** — căn cứ **không** phải §2.2 (đã void) mà là: circular bias (bq_admin xác nhận `hit_ticker_list` ← deal backtest), non-reproducibility (IVS 0→1.622 dòng; 459→381), look-ahead 2,74× (§2.2c) |
| Q2 | Chốt B3 = 1,0 tỷ VND/ngày (thực, neo 2026, khử lạm phát 7%) làm v1 — **giữ vì nó là hằng số production sẵn có** (`filter.json:18`), **KHÔNG** hiệu chuẩn theo recall (thước đo vô hiệu, §2.2), **KHÔNG** theo CAGR | **CÓ** |
| **Q9** | **(MỚI)** Chấp nhận **cổng cứng §3.2b**: cấm cutover P2/P4 tới khi đóng hạng mục lớp-chất-lượng-ex-ante; hướng khuyến nghị **Q-A (đo độ rò qua golden floor) + Q-C (xuất cờ)**, **không** thêm ngưỡng ROE vào tầng universe | **CÓ** — đây là hệ quả trực tiếp của §2.4, chạm tiền thật |
| Q3 | Đánh dấu R3 27,84% là `PROVISIONAL` trong `results_registry.md` **ngay**, trước khi implement | **CÓ** — rẻ, ngăn trích dẫn sai trong 2-3 tuần tới |
| Q4 | Chấp nhận re-pin R3 (2 lần chạy) + rà soát N-trial tuần qua | **CÓ**, ưu tiên cao-không-khẩn |
| Q5 | **CAPIT: cho phép giữ breadth ở `ticker_prune` CÓ CHỦ Ý cho tới khi re-hiệu-chuẩn xong**, và cấm cutover P4 khi `capit_fired=true` | **CÓ** — đây là khoản chạm tiền thật, xin duyệt riêng |
| Q6 | Nếu G4 không tìm được `WASHOUT_GATE'` bảo toàn tập ngày fire → dừng và hỏi user, không tự chọn ngưỡng | **CÓ** |
| Q7 | Cho phép sửa `data_registry.md` / `coding_guidelines.md` / `cron_registry.md` kèm theo | **CÓ** |
| ~~Q8~~ | ~~Gửi bq_admin 1 câu hỏi bổ sung~~ — **ĐÃ XONG, đã có trả lời 04:12 ICT** | **ĐÓNG** — xác nhận `max_bad_records=10` áp cho MỌI bảng gồm `ticker` ⇒ B8 bắt buộc (§7) |

**Không xin duyệt trong tài liệu này** (chưa đủ dữ liệu): sửa trần vị thế LAG (12 vs 16-17 thực),
đổi bất kỳ tham số chiến lược nào, đụng vào 43 mã rule-only ở tầng sizing.

---

## 10. VIỆC KẾ TIẾP (nếu duyệt)

**Đã đóng kể từ bản đầu:**

| # | Việc | Trạng thái |
|---|---|---|
| ~~1~~ | ~~Lấy lại văn bản gốc Q&A bq_admin~~ | **XONG** — file có sẵn, đã đọc, §7 cập nhật (§0) |
| ~~2~~ | ~~Winston đánh giá khả thi vận hành~~ | **XONG** — khả thi, chi phí ~0; cảnh báo `ticker` cũng bị ghi đè lịch sử (§8.6) |
| ~~3~~ | ~~quant-skeptic review, soi riêng §2.2~~ | **XONG — REFUTED (cao) đúng §2.2.** Đã sửa: §2.2 (tautology), §2.4 (test thay thế), §2.2c (2,74×), §7 (Q8 có trả lời), §8.3 (n=3) |
| ~~4~~ | ~~User duyệt Q1-Q9~~ | **XONG 2026-07-22** — duyệt toàn bộ; Q9 theo khuyến nghị **Q-A + Q-C, KHÔNG Q-B** |
| ~~5~~ | ~~**G1** — viết builder + selfcheck + backfill~~ | **XONG 2026-07-22** (job `Taylor_20260722_044614`) — xem dưới |
| ~~6~~ | ~~**G2** — kiểm định recall bằng median-60 TỰ TÍNH~~ | **XONG — KHÔNG tụt.** Không phải hiệu chuẩn lại B3 |

### 10.1 G1 — ĐÃ XONG (2026-07-22)

**Artifact:**
- Builder: `mike/bin/build_universe_pit.py` (ruleset_version = 1)
- Selfcheck: `mike/bin/build_universe_pit_selfcheck.py` — **15 PASS / 0 FAIL**
- Bảng: **`lithe-record-440915-m9.tav2_mike.universe_pit`** — dataset **`tav2_mike`** (RIÊNG của đội,
  KHÔNG phải `tav2_bq`). Lý do đặt ngoài `tav2_bq`: bản đầy đủ câu trả lời Q8 (§7) xác nhận script
  của bq_admin **XÓA rồi ghi lại toàn bảng**; bảng bất biến của ta không được nằm trong tầm với của
  một lệnh TRUNCATE ta không kiểm soát.

**Kết quả backfill (2000-07-28 → 2026-07-21):** 4.089.541 dòng · 6.339 phiên · 1.463.992 dòng
`in_universe=TRUE` · **0 cặp (time,ticker) trùng lặp** (đã verify bằng query độc lập).

**Đã kiểm chứng:**
| Kiểm tra | Kết quả |
|---|---|
| B8 trip đúng 3 case (lệch >±15%, dòng thô <90%, double-run) | PASS (A2/A2b/A3/A4/A5) + PASS biên (A2c 15,0% và A3b 90,0% KHÔNG chặn nhầm) |
| Idempotent LIVE (chạy lại ngày đã có) | **PASS** — `--date 2026-07-21` → `REFUSED / B8_DUPLICATE`, không ghi thêm dòng nào |
| Atomic write (kill trước `os.replace`) | PASS — file đích còn nguyên bản cũ, không có file dở dang |
| Đọc LIVE không qua cache | `BQ_LOCAL_CACHE` pop process-local ngay đầu file (guidelines §11) |

⚠️ **Một sự cố THẬT trong chính G1, đã sửa và đáng ghi lại:** lần backfill đầu bị kill lúc timeout,
nhưng job `INSERT` phía BigQuery **vẫn chạy tiếp và commit SAU** khi lần chạy lại đã đọc `MAX(time)`
⇒ dữ liệu 2022 bị ghi **hai lần**. Kiểm tra `MAX(time)` là kiểm tra nguồn-sự-thật-bên-ngoài, nhưng
nó **không thấy được job đang bay**. Đã sửa bằng **`job_id` tiền định** (`_run_dml`): BigQuery từ
chối tạo job trùng id, ta bắt `Conflict` rồi bám vào chính job cũ thay vì chạy lệnh thứ hai. Bảng
hiện tại đã dựng lại sạch (0 trùng). Đây đúng là ca mà `coding_guidelines.md` §5 mô tả — và cho thấy
"kiểm tra state bên ngoài" một mình **không đủ** khi side-effect là bất đồng bộ.

### 10.2 G2 — kiểm định median-60 TỰ TÍNH: recall KHÔNG tụt

Bước bắt buộc ở §3.2b (chạy lại bảng §2.2 nhưng dùng **median 60 phiên tự tính từ `Price × Volume`
thô**, thay vì cột dựng sẵn `Volume_3M_P50` của ETL ngoài). Đo trên chính `universe_pit` đã build:

| Ngày | `n_prune` PIT | Giao | **Recall (median-60 tự tính)** | Recall §2.2 (`Volume_3M_P50`) | Δ |
|---|---|---|---|---|---|
| 2014-06-30 | 140 | 138 | **98,6%** | 97,1% | +1,5pp |
| 2016-06-30 | 167 | 165 | **98,8%** | 97,6% | +1,2pp |
| 2018-06-29 | 180 | 178 | **98,9%** | 98,3% | +0,6pp |
| 2020-06-30 | 226 | 224 | **99,1%** | 98,7% | +0,4pp |
| 2022-06-30 | 321 | 318 | **99,1%** | 99,1% | 0,0pp |
| 2024-06-28 | 310 | 306 | **98,7%** | 99,0% | −0,3pp |
| 2026-06-15 | 233 | 230 | **98,7%** | 98,7% | 0,0pp |

⇒ **KHÔNG tụt** (thực tế nhỉnh hơn ở các mốc sớm). **Không hiệu chuẩn lại B3** — đúng §8.4, tránh
bẫy tự-tune. *(Nhắc lại đính chính §2.2: con số recall này chỉ đo **độ lệch công thức** giữa spec và
row-filter production; nó KHÔNG phải bằng chứng về chất lượng curation — câu đó thuộc §2.4/G2b.)*

**Kiểm tra chéo tách được 2 hiệu ứng — quan trọng cho việc đọc số:** tổng `in_universe` của
`universe_pit` **lớn hơn đáng kể** `n_rule` tĩnh ở §2.2 (vd 2026-06-15: 396 vs 273). Tách theo
`reason` cho thấy đây **không phải** lệch công thức mà là **B4 hysteresis đúng như thiết kế**:

| Ngày | `ENTER` (đủ điều kiện vào) | §2.2 `n_rule` tĩnh | `CARRY_IN` (giữ bởi hysteresis) |
|---|---|---|---|
| 2014-06-30 | 169 | 165 | 58 (26% rổ) |
| 2022-06-30 | 421 | 402 | 130 (24% rổ) |
| 2026-06-15 | 271 | 273 | 125 (32% rổ) |

Chân `ENTER` khớp §2.2 trong khoảng ~±5% ⇒ **công thức median-60 tự tính tái lập đúng row-filter
production**. Toàn bộ phần rộng thêm là `CARRY_IN`. Lưu ý đọc đúng B4: điều kiện ra là *"dưới 0,5 tỷ
trong 20 phiên **liên tiếp**"*, implement bằng `MAX(tv, 20 phiên) < 0,5e9` — đúng nghĩa đen của
"liên tiếp", nhưng **rất dính**: một phiên duy nhất vượt 0,5 tỷ là reset đồng hồ. Đó là lý do
`CARRY_IN` chiếm 24-32%. **Không sửa** (spec là spec, và bất đối xứng vào-chặt/ra-lỏng cùng triết lý
DT5G 4-gate), nhưng đây là số cần nhớ khi re-pin R3 và khi hiệu chuẩn lại mẫu số CAPIT breadth
(§4.4) — rổ `universe_pit` rộng hơn ~45% so với rule tĩnh, và **rộng hơn `ticker_prune` PIT ~1,7×**.

### 10.3 Còn lại

1. **G2b** (đo độ rò chất lượng qua golden floor — cổng cứng Q9/§3.2b) — chạy độc lập được, **chặn
   cutover P2/P4**. Chưa làm.
2. **G3** (cutover consumer) · **G4** (CAPIT breadth, §4.4) — chưa làm, phụ thuộc G2b.
3. Re-pin R3 (§5.1) — chưa làm.
4. **Không cần dispatch quant-skeptic vòng 2** cho các sửa đổi tài liệu (chúng chỉ **hạ** mức tự tin
   và **siết** thêm cổng, không nới lỏng gì). **Cần** skeptic khi: (a) G2b dẫn tới đề xuất thêm tham
   số chất lượng vào tầng universe (Q-B), hoặc (b) trước cutover bất kỳ consumer chạm tiền thật.
   G1 tự nó **không đổi hành vi production nào** — chỉ thêm một bảng mới chưa ai đọc.
