# PHƯƠNG ÁN THAY THẾ `ticker_prune` — kiến trúc, migration, timeline

Job `Taylor_20260722_033547` · 2026-07-22 · Taylor (Quant, lead)
Tiền thân: `ticker_prune_universe_governance.md` (job `Taylor_20260721_162005`) + phản hồi bq_admin.
~~**Trạng thái: ĐỀ XUẤT QUYẾT ĐỊNH. Chưa implement dòng code nào.**~~
✅ **TRẠNG THÁI CUỐI (2026-07-22): DỰ ÁN ĐÃ ĐÓNG.** Q1-Q9 duyệt · G1/G2/G2b xong · P1-P4 cutover
xong · G6 re-pin xong (pit 27,16% vs prune 27,95% cùng vintage, Δ −0,79pp). **Đọc §9 trước** để lấy
trạng thái cuối + danh sách hạng mục còn mở (quyết định pin production, G7/G8/G9, P5/P6); §5.4 cho
kết quả re-pin. Phần còn lại của tài liệu giữ nguyên làm dấu vết quá trình.

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

#### 3.2b-G2b — KẾT QUẢ ĐO (job `Taylor_20260722_054947`, 2026-07-22): **Q-A KHÔNG CHỐT ĐƯỢC — ESCALATE**

Đã chạy đúng việc G2b (§6): `golden floor rating_8l` (`ROE_Min3Y ≥ 0` ∧ `CF_OA_3Y > 0`, point-in-time)
+ `BANNED` + **rating 8L thật ≤3** (panel lịch sử `data/fa_ratings_8l_hist.csv`, as-of ≤ ngày đo) lên
nhóm rule-only. **Cổng cứng GIỮ NGUYÊN (đóng).**

⚠️ **Đính chính quan trọng trước khi đọc số: nhóm rule-only THẬT lớn gấp ~2-4 lần con số §2.4.**
§2.4 đo trên rule thanh khoản thuần (`Volume_3M_P50×Price ≥ 1e9×Inflation_7`). `universe_pit` đã build
(G1/G2) có thêm **hysteresis B4** (chỉ loại khi <0,5 tỷ suốt 20 phiên liên tiếp) nên giữ lại nhiều mã
thanh khoản mỏng hơn. Đo trực tiếp trên bảng thật `tav2_mike.universe_pit`:

| Ngày | universe_pit | BOTH (∩ prune) | **rule-only THẬT** | (§2.4 từng ghi) |
|---|---|---|---|---|
| 2014-06-30 | 227 | 138 | **89** | 30 |
| 2018-06-29 | 302 | 178 | **124** | 21 |
| 2022-06-30 | 551 | 318 | **233** | 84 |
| 2026-06-15 | 396 | 230 | **166** | 43 |

Cột BOTH khớp §2.4 chính xác (138/178/318/230) ⇒ chênh lệch nằm hoàn toàn ở B4, không phải lỗi đo.

**Kết quả 2 lớp chặn:**

| Ngày | rule-only | qua golden floor | BANNED | rating ≤3 | **LỌT CẢ HAI (leak)** |
|---|---|---|---|---|---|
| 2014-06-30 | 89 | 37 | 3 | *(n/a)* | **không đo được** |
| 2018-06-29 | 124 | 72 | 4 | 59 | **45** |
| 2022-06-30 | 233 | 121 | 3 | 104 | **77** |
| 2026-06-15 | 166 | 82 | 2 | 84 | **61** |

- **2014-06-30 KHÔNG đo được**: panel `fa_ratings_8l_hist.csv` bắt đầu **2014-07-09**, sau ngày đo ⇒
  100% mã thiếu rating. Không được đọc "0 leak" ở mốc này là kết quả tốt — đó là thiếu dữ liệu.
- **Leak ≠ ~0 ở cả 3 mốc đo được** ⇒ theo đúng cam kết §3.2b: **KHÔNG tự chọn Q-C/Q-B, trình user.**

**Nhưng số thô này gây hiểu lầm nếu đọc một mình — 2 điều chỉnh hướng NGƯỢC nhau, phải đọc cùng:**

1. **Chất lượng nhóm leak là TỐT, không xấu.** Trung bình nhóm lọt qua cả 2 lớp: `ROE_Min3Y`
   **+14,6% / +11,7% / +12,1%**, `ROE5Y` **+18,5% / +16,1% / +17,7%** (2018/2022/2026) — tức là **cao
   hơn cả nhóm BOTH** trong §2.4 (+9,2% / +6,8% / +4,9%). Rủi ro §2.4 nêu (nhóm rule-only có
   `ROE_Min3Y` **âm** trung bình) **đã bị 2 lớp chặn hấp thụ đúng như Q-A giả định**. Leak lớn về SỐ
   LƯỢNG nhưng không mang theo chất lượng xấu.
2. **Ở tầng chạm tiền thật (P2/P4) leak nhỏ hơn nhiều bậc.** Lọc thêm bằng sàn thanh khoản của chính
   consumer (custom30V min ADV ~13,1 tỷ; CAPIT sàn ~2 tỷ):

   | Ngày | leak ADV ≥ 13,1 tỷ (P2 custom30V) | leak ADV ≥ 2 tỷ (P4 CAPIT) |
   |---|---|---|
   | 2018-06-29 | **0** | **0** |
   | 2022-06-30 | **3**: ITA(r3, ROE_Min3Y +1,4%), BAF(r3, +13,4%), APH(r3, +1,8%) | **9** (+FIR, DVG, ODE, ADG, HAR, GMH) |
   | 2026-06-15 | **3**: VPL(r3, +3,2%), VGI(r3, +1,8%), FOX(r2, ROE5Y **31,0%**) | **4** (+VIW) |

   3 mã lọt ở mốc 2026 chính là **nhóm "curation SAI vì danh sách cũ"** §2.4 đã chỉ tên (FOX/VPL/VGI —
   mã lớn, chất lượng tốt, mới lên sàn). Ở tầng tiền thật, leak = **đúng phần curation cũ làm SAI**,
   không phải phần curation làm ĐÚNG. Mốc 2022 mờ hơn: BAF chất lượng thật, ITA/APH `ROE_Min3Y` dương
   nhưng mỏng (+1,4%/+1,8%) — đây là 2 tên cần user nhìn tận mắt.

**Vì sao vẫn KHÔNG tự chốt Q-A dù bức tranh có lợi:** tiêu chí §3.2b viết là "**≈0 hoặc rất nhỏ, giải
thích được từng trường hợp**". 45/77/61 không phải "rất nhỏ", và việc rào nó xuống 0-3 phải **mượn sàn
thanh khoản của consumer** — tức là đổi tiêu chí giữa chừng, đúng kiểu tự-hợp-lý-hóa mà §8.4 cảnh báo.
Việc quyết định "sàn thanh khoản consumer có được tính là lớp chặn hợp lệ hay không" là **quyết định
của user**, không phải của tôi.

**3 lựa chọn trình user (không tự chọn):**
- **A′ (Q-A có điều kiện)** — chấp nhận sàn thanh khoản consumer là lớp chặn thứ 3; chốt Q-A với ghi
  nhận rõ: leak thật ở tầng tiền = 0-3 mã/mốc, chất lượng dương, phần lớn là mã curation cũ bỏ sót.
  Rẻ nhất, không thêm tham số. Rủi ro còn lại: ITA/APH-2022 kiểu (rating 3 + ROE mỏng).
- **Q-C** — giữ universe thuần + xuất cờ `quality_flag` trong `universe_pit` (khuyến nghị gốc §3.2b),
  cho tầng due-diligence đọc. Không đổi hành vi, minh bạch, khớp mandate due-diligence 2026-07-21.
- **Q-B** — thêm ngưỡng chất lượng vào universe. **Tôi vẫn KHÔNG khuyến nghị** (§8.4: trộn tầng + thêm
  tham số tune được), và số đo hôm nay **không ủng hộ** Q-B: nhóm leak có chất lượng dương.

**Khuyến nghị Taylor: A′ + Q-C** (chốt Q-A với điều kiện ghi rõ, đồng thời làm Q-C vì nó gần như miễn
phí và phục vụ mandate due-diligence).

> ### ✅ USER ĐÃ CHỐT (2026-07-22, job `Taylor_20260722_062405`): **A′ + Q-C. KHÔNG Q-B.**
>
> - **A′** — sàn thanh khoản riêng của từng consumer (**custom30V ≥13,1 tỷ/ngày**, **CAPIT ≥2
>   tỷ/ngày**) được tính là **lớp chặn chất lượng hợp lệ**, bổ sung cho golden floor + BANNED.
>   **KHÔNG sửa tiêu chí B1-B8** của `universe_pit`. Rủi ro còn lại (0-4 mã biên kiểu ITA/APH-2022)
>   được **CHẤP NHẬN có ghi nhận** — đây là quyết định của user, không phải kết luận đo đạc.
> - **Q-C** — làm (§3.2c). **Q-B — không làm** (không thêm ngưỡng ROE cứng vào tầng universe).
> - **Cổng cứng §3.2b/Q9 ⇒ MỞ.** G3 được phép chạy. Cổng CAPIT §4.4 **vẫn ĐÓNG độc lập** (P4 chưa
>   được cutover cho tới khi re-hiệu chuẩn breadth xong — hai cổng khác nhau, đừng nhầm).

#### 3.2c Q-C — CỜ CHẤT LƯỢNG: **ĐÃ IMPLEMENT** (job `Taylor_20260722_062405`, 2026-07-22)

**Bảng companion, KHÔNG thêm cột vào `universe_pit`.** `universe_pit` là bảng bất biến append-only —
thêm cột rồi `UPDATE` 6.339 partition đã ghi chính là thứ ta đang bỏ chạy (lịch sử bị viết lại). Vì
vậy: bảng riêng `tav2_mike.universe_pit_quality` + view `tav2_mike.universe_pit_q`
(`universe_pit LEFT JOIN quality`) để consumer đọc "như một cột". Lợi thêm: `quality_ruleset_version`
**riêng** — sau này đổi định nghĩa chất lượng không kéo theo re-version membership.

- **Phạm vi**: chỉ dòng `in_universe = TRUE` → **1.463.992 dòng** (khớp chính xác `COUNT(*) WHERE
  in_universe` của `universe_pit`). Cờ chất lượng của mã ngoài universe là vô nghĩa với mọi consumer.
- **Nguồn: ĐÚNG 3 nguồn đã dùng ở G2b, không thêm nguồn mới** — `ticker.ROE_Min3Y` (cùng ngày),
  `ticker_financial.CF_OA_3Y` (as-of quý, hiệu lực ≤400 ngày), `fa_ratings_8l` (panel as-of,
  CANONICAL) + hằng số BANNED.
- **`quality_flag`** (loại trừ nhau, theo thứ tự ưu tiên): `BANNED` → `UNKNOWN_FLOOR` (thiếu dữ liệu)
  → `FLOOR_FAIL` → `UNKNOWN_RATING` (chưa có panel 8L) → `RATING_FAIL` (rating >3) → `QUALITY_OK`.
  Kèm các cột thô `roe_min3y / cf_oa_3y / rating_8l / rating_asof` để người đọc tự kiểm.
- ⚠️ **Cờ này KHÔNG chặn gì.** Không đổi `in_universe`, không đổi rổ, không đổi lệnh. Thuần thông tin.
- **Selfcheck `universe_pit_quality_selfcheck.py` — PASS**, tái lập đúng số G2b trên nhóm rule-only:

  | Ngày | rule-only | `QUALITY_OK` (= "leak" G2b) | G2b ghi |
  |---|---|---|---|
  | 2014-06-30 | 89 | **0** (35 `UNKNOWN_RATING`) | không đo được ✔ |
  | 2018-06-29 | 124 | **45** | 45 ✔ |
  | 2022-06-30 | 233 | **77** | 77 ✔ |
  | 2026-06-15 | 166 | **60** | 61 — lệch 1, **giải thích được** |

  Lệch 1 mã ở 2026: G2b đọc snapshot local `data/fa_ratings_8l_hist.csv` (mtime 06-16), cờ này đọc
  bảng **CANONICAL** `tav2_bq.fa_ratings_8l` đã refresh — **TLD** bị re-rank 3→5 tại cùng eff-date
  2026-05-04 (refresh weekly re-rank 2 quý mở, `data_registry.md` dòng 117). Mọi mã khác trùng khít.
  Đây là **dữ liệu tươi hơn, không phải sai số tính toán**. Mốc 2014 ra `UNKNOWN_RATING` đúng như
  cảnh báo §3.2b-G2b — thiếu dữ liệu **không** được đọc thành "0 leak sạch".
- **Files**: `mike/bin/build_universe_pit_quality.py` (`--backfill` / `--date` / `--dry-run`,
  append-only, `SKIP_EXISTING` chống ghi đè), `mike/bin/universe_pit_quality_selfcheck.py`.

*Tái lập:* `/tmp/g2b_detail.sql` (SQL rule-only + floor) và bước join panel rating; artifact đầy đủ
`mike/agents/Taylor/research/g2b_leak_20260722.csv` (612 dòng, mọi mã rule-only 4 mốc kèm
`roe_min3y/cf_oa_3y/roe5y/FSCORE/adv_bn/pass_floor/banned/rating/leak`).

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
| P3 | `deploy_golive_dt5g_v4/golive_recommend_v23.py` 290/293 | D1 (**BẤT ĐỘNG SẢN** ICB-8633 — lens D1 RE_BACKLOG) | ✅ **DONE 2026-07-22** (commit `0bfbdfe`) — tác động LIVE hôm nay = **ZERO** (A/B trọn script byte-identical) | ⚠️ **ĐÍNH CHÍNH 2026-07-22**: bản trước ghi "banking sector-lens" — **SAI**. `ICB_Code=8633` là **Real Estate Holding & Development**, không phải ngân hàng. Nhãn sai này đã lan sang cả prompt dispatch. Diff §4.3b **không nhỏ** ⇒ hạ ước lượng "Thấp". |
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

### 4.3b KẾT QUẢ A/B TĨNH P1-P3 (job `Taylor_20260722_062405`, 2026-07-22)

Script: `mike/agents/Taylor/research/universe_pit_ab_p2p3.py` — **không sửa một dòng nào** của
`custom_basket.py` / `golive_recommend_v23.py`: `build_pit` nhận `bq` làm tham số, nên ta bọc `bq`
bằng wrapper viết lại đúng mệnh đề universe trong SQL. Chạy **đúng code production**, universe khác.
Artifact: `universe_pit_ab_p2p3_2026-07-22.csv`. Cấu hình P2 = production (`BASKET_SELECT=yieldcombo`,
`gate_rating=3`, `rebal=q2m5`, `namecap`).

**3 nhánh, cố ý tách 2 hiệu ứng** (gộp lại thì không đọc được diff đến từ đâu):
`A` = production hôm nay (`ticker_prune` DISTINCT-ever, **đang có look-ahead** §2.2) ·
`B0` = `universe_pit` DISTINCT-ever (**chỉ** hiệu ứng đổi universe) ·
`B` = `universe_pit` per-day `EXISTS` (**đúng đặc tả D1 §4.1**: đổi universe **+ bỏ look-ahead**).

#### P2 — rổ custom30V (30 mã) · **DIFF NHỎ, và = 0 ở kỷ nguyên hiện đại**

| Mốc rebal | B0 đổi | B đổi | VÀO (nhánh B) | RA (nhánh B) |
|---|---|---|---|---|
| 2014-08-05 | 6/30 | **6/30** | FDC,KMR,LAF,NTL,SMA,VHG | CTD,DPR,DQC,HLD,SVC,VSH |
| 2015-11-05 | 6/30 | **6/30** | APC,API,CSM,MCG,TIG,TMT | CMG,CMS,DHA,FMC,SD6,SVC |
| 2017-02-06 | 1/30 | **2/30** | TSC,WSB | CSV,TLH |
| 2018-08-06 | 0 | **0** | — | — |
| 2019-11-05 | 1/30 | **1/30** | SSI | NTL |
| 2021-02-05 | 2/30 | **2/30** | SZC,TAR | CRE,TTF |
| 2022-05-05 | 1/30 | **1/30** | VGC | PVT |
| 2023-11-06 | 0 | **0** | — | — |
| 2025-02-05 | 0 | **0** | — | — |
| **2026-05-05 (rổ ĐANG LIVE)** | **0** | **0** | — | — |

Đọc: universe rộng hơn ~1,7× **nhưng rổ 30 mã gần như không đổi** — vì `gate_rating≤3` + xếp hạng
theo value-yield đã tự lọc, mã mới vào universe chủ yếu là mã nhỏ/kém, không lọt top-30. **Rổ đang
LIVE (rebal 2026-05-05) GIỐNG HỆT** ⇒ cutover P2 hôm nay là **no-op với rổ hiện tại**. ⚠️ **Vẫn
KHÔNG tự cutover** — đây là parking NEUTRAL production, và diff lịch sử sẽ đổi chuỗi NAV backtest
(liên quan re-pin R3 §5), cần người duyệt.

##### ⚠️ ĐÍNH CHÍNH PHẠM VI DIFF (job `Taylor_20260722_070547`) — diff KHÔNG chỉ ở 2014-15

Bảng trên chỉ lấy mẫu 10 mốc rời rạc, dễ bị đọc thành "diff chỉ ở 2014-2015" (prompt dispatch của
job cutover đã tóm tắt sai đúng theo hướng đó). Quét **LIÊN TỤC MỌI mốc rebal 2021-06 → 2026-07**
(`UNIVERSE_SOURCE` prune vs pit, cấu hình production q2m5/gate3/namecap):

| Mốc rebal | Khác? | VÀO | RA |
|---|---|---|---|
| 2021-06-01 | 1/30 | ITA | PLX |
| 2021-08-05 | 1/30 | ITA | KDH |
| 2022-02-07 | 1/30 | ITA | FPT |
| 2022-05-05 | 2/30 | APH, ITA | MSB, VGT |
| **2022-08-05 → 2026-05-05 (16 mốc liên tiếp)** | **0** | — | — |

⇒ **Mốc diff CUỐI CÙNG là 2022-05-05.** Từ 2022-08-05 tới nay (16 mốc liên tiếp, gồm rổ ĐANG LIVE)
rổ giống hệt từng mã. Hàm ý: (a) cutover an toàn với tiền thật hôm nay — đúng cơ sở user đã duyệt;
(b) nhưng chuỗi NAV backtest 2021-2022 **sẽ đổi** ⇒ re-pin R3 (§5) vẫn là việc còn nợ, không được
coi là đã đóng.

*Quan sát cần người đọc:* mã VÀO ở 3/4 mốc là **ITA** — đúng loại "mã rule-only" mà `ticker_prune`
curation loại và quant-skeptic từng cảnh báo là curation CÓ mang thông tin thật. `universe_pit_q`
gắn ITA cờ **`QUALITY_OK`** ở cả 2021-06-01 lẫn 2022-05-05 ⇒ golden floor hiện có **không** bắt
được ca này. Không tự xử lý trong job cutover (đúng Q9: không thêm ngưỡng chất lượng vào tầng
universe); ghi lại để tầng chiến lược/§3.2b cân nhắc.

#### P3 — lens D1 RE_BACKLOG (ICB-8633, **bất động sản**, không phải ngân hàng) · **DIFF LỚN**

| Mốc | A (n) | B0 (n) | **B (n)** | B: VÀO / RA |
|---|---|---|---|---|
| 2014-08-05 | 36 | 52 | **34** | +8 / −10 (bỏ VHM, PDR, D2D, HDC…) |
| 2018-08-06 | 55 | 77 | **45** | +4 / −14 (bỏ BCM, VEF, HPX…) |
| 2022-05-05 | 66 | 91 | **78** | +17 / −5 |
| 2026-05-05 | 67 | 92 | **60** | +5 (API,HAR,LGL,LSG,PV2) / −12 (C21,EFI,IDV,PVR,SZB,SZL,TEG,TID,TIX,VPH,VRC,VRG) |

Hai điều đọc được, ngược chiều nhau:
1. **B0 chỉ CỘNG, không bao giờ TRỪ** ở mọi mốc ⇒ xác nhận lại `universe_pit ⊇ ticker_prune` ở mức
   tập-ever (khớp §2.1).
2. **Phần TRỪ của B toàn bộ đến từ việc bỏ look-ahead** — và nó **đúng**: VHM bị loại khỏi panel
   2014/2015 vì **VHM niêm yết 2018**. Đây chính là look-ahead §2.2 đang nằm trong production hôm
   nay. Nhưng độ lớn (±10-17 mã/mốc, ~20% panel) là **thay đổi hành vi thật**, không phải cosmetic.

⇒ ~~**P3 CHỜ NGƯỜI DUYỆT.**~~ *Giới hạn phép đo:* chỉ đối chiếu nhánh `tav2_bq.ticker` của UNION;
nhánh fallback `ticker_1m` (chỉ bổ sung phiên tươi nhất) không đo — không ảnh hưởng kết luận ở các
mốc lịch sử.

#### P3 — **DONE, ĐÃ CUTOVER 2026-07-22**, commit `0bfbdfe` (job `Taylor_20260722_084953`, user duyệt)

2 vị trí panel D1 (nhánh `ticker` + nhánh fallback `ticker_1m`) → `universe_pred()` đọc
`tav2_mike.universe_pit_q` **theo NGÀY**. Hằng số module-level `UNIVERSE_SOURCE = "pit"` (KHÔNG env
var, `coding_guidelines.md` §11) — rollback bằng 1 chữ. **3 chỗ đọc `ticker_prune` còn lại trong
cùng file (`:167` ADV cap, `:425`/`:455` CAPIT breadth + pool) là P4, GIỮ NGUYÊN có chủ đích** cho
tới khi hiệu chuẩn lại §4.4.

**Fail-safe §4.3** — `assert_universe_covers()` chạy TRƯỚC truy vấn panel; thiếu ngày → `RuntimeError`,
**tuyệt đối không** tự fallback `ticker_prune`. Phạm vi kiểm tra = các phiên **có dữ liệu panel
ICB-8633**, không phải mọi phiên trong `ticker`: upstream thường xuyên để lại **1 dòng stub** cho
ngày hiện tại (07-22 đúng 1 dòng, DRL) mà gate B8 của `build_universe_pit.py` **TỪ CHỐI** dựng
universe từ đó (`B8_RAW_DEPTH: 1 dòng = 0,1% trung vị 816`) — bắt lỗi ở đó sẽ hạ recommender vì một
ngày không đóng góp gì. Nếu stub có mã 8633 thì vẫn fail to.

**Selfcheck `universe_pit_p3_selfcheck.py` 14/14 PASS** (khác P2: **không** assert diff = 0, vì đây
là sửa bug — đổi hành vi là có chủ đích):
- **T4 = bằng chứng bug đã fix**: VHM **CÓ** trong panel 2014 nhánh `prune`, **KHÔNG còn** ở nhánh
  `pit`. Panel 2014: 38 → 39 mã (bỏ 9: C21, D2D, HDC, IDV, LHG, PVR, TIX, **VHM**, VRG; thêm 10).
- **T5 đo diff LIVE thật**: panel `[2026-03-24..07-22]` **67 → 60 mã** (RA 12 / VÀO 5); tập tín hiệu
  RE_BACKLOG (mask `d1m`) **778 → 649 cặp**; ngày tín hiệu gần nhất 07-21 mất **HLD, TEG**.
  T5.3 xác nhận **100% thay đổi giải thích được bằng membership theo ngày** (bỏ-sai 0 / thêm-sai 0).
- **Bẫy đo lường tìm ra trong lúc làm**: chạy câu panel 2 lần cách nhau vài phút bị `fa_ratings`
  re-rank **đúng eff-date** làm nhiễu (QCG `fa_tier` D→E ⇒ 6 diff giả). Selfcheck đã sửa sang lấy
  **MỘT panel hợp `(pit OR prune)`** rồi tách 2 nhánh bằng membership đọc riêng — A/B nguyên tử.
  *(Cùng họ với ghi chú TLD dòng ~433. Mọi A/B tương lai chạm `fa_ratings` phải làm kiểu này.)*

**Tác động LIVE hôm nay = ZERO — đã đo, không phải suy luận.** Chạy trọn `golive_recommend_v23.py`
2 lần **cùng vintage** (`pit` rồi `prune`, 15:59-16:0x 07-22) → `out/golive_v23_recommendations_
2026-07-22.md`/`.csv` và `data/golive_v23_status.json` **byte-identical**. Lý do cơ chế: hôm nay
**BAL picks = 0**, mà `RE_BACKLOG_BUY` chỉ là một nhãn `play_type` trong `TIER_BAL` ⇒ thay đổi lens
không tới được đầu ra. Artifact production đã khôi phục về bản `pit`.
⚠️ Hệ quả: **zero-impact hôm nay là điều kiện thị trường, không phải tính chất của thay đổi.** Ngày
nào BAL có pick, HLD/TEG-loại-kiểu-này sẽ đổi đầu ra thật.

Selfcheck sẵn có đã chạy lại: `lag_live_schedule` · `edge_wlag_gate` · `money_path_freshness` ·
`anomaly_gate_prod_parity` · `lag_liq_signal_filter` — **PASS**. `anomaly_gate_selfcheck` 15 PASS /
**2 FAIL** (A4, B1 — cờ PNJ đã hết hạn 30 ngày): xác minh **CÓ SẴN TỪ TRƯỚC**, chạy lại với file đã
`git stash` cho kết quả y hệt.

#### P2 — `custom_basket.py` · **DONE — ĐÃ CUTOVER 2026-07-22**, commit `ce7d457` (job `Taylor_20260722_070547`, user duyệt)

**CHẠM PRODUCTION THẬT** — custom30V là parking book NEUTRAL đang sống của SpaceX/ZaloPay.
3 chỗ đọc `ticker_prune` (`select_members`, `build_pit`, nhánh sector-cap `mktcap`) → `universe_pred()`
đọc `tav2_mike.universe_pit_q` **theo NGÀY** (bỏ luôn look-ahead `DISTINCT ticker`-ever của nhánh cũ).
Hằng số module-level `UNIVERSE_SOURCE = "pit"` — rollback bằng 1 chữ, nhánh `prune` giữ nguyên.
**Fail-safe §4.3**: `assert_universe_covers()` chạy TRƯỚC truy vấn đầu tiên, thiếu ngày → `RuntimeError`,
**tuyệt đối không** tự fallback `ticker_prune` (thiếu ngày mà im lặng sẽ ra "rổ rỗng" thay vì lỗi to).
Kèm theo: `sync_bq_cache.py` cache `universe_pit_q` + `bq_local_cache.py` dịch tham chiếu `tav2_mike.*`
— nếu không, mọi lần build qua cache sẽ fail cứng (đúng thiết kế, nhưng làm hỏng đường chạy 23:45).

Selfcheck `universe_pit_p2_selfcheck.py` **13/13 PASS**: 7/7 mốc rebal trong 600 ngày byte-identical
(gồm mốc LIVE 2026-05-05) · thiếu ngày → dừng có lỗi · không có đường fallback · nhánh cache == BigQuery.
Selfcheck cũ: `route_selector` PASS; `dcf_selector` FAIL **1 test có sẵn từ trước** (đo lại với
`UNIVERSE_SOURCE="prune"` cho ra đúng FAIL đó ⇒ không do cutover); `eyrisk_selector`/`v4final_selector`
FAIL các test dạng "identical to **pre-edit** (`git show HEAD:custom_basket.py`)" — fail **do bản
cutover chưa commit**, sau khi commit HEAD đã chứa thay đổi thì cả hai trở lại PASS (đã verify:
`eyrisk_selector` **12/12 PASS**; `v4final_selector` **12/12 PASS / FAIL 0** — chạy lại sau commit
`ce7d457` trong job `Taylor_20260722_082001`, bao gồm cả các guard fincap/route/namecap trên 1114 ngày).

#### P1 — `trading_bot/due_diligence.py` · **ĐÃ CUTOVER** (rủi ro thấp nhất, §4.2)

Đọc `tav2_mike.universe_pit_q` (membership **+ `quality_flag`** — Q-C vào việc luôn) thay cho
`bq_cache/ticker_prune/*.parquet`. Hằng số module-level `UNIVERSE_SOURCE = "pit"`, nhánh cũ `_in_prune`
giữ nguyên để rollback bằng 1 chữ. **Fail-safe theo §4.3**: đọc lỗi/thiếu ngày → nhãn `n/a`, **không**
tự fallback về `ticker_prune`, và **không** được kết luận "NGOÀI universe". Selfcheck **20/20 PASS**
(thêm 3 test mới: `n/a` khi lỗi · hiện cờ chất lượng · TRC ở TRONG universe nhưng `RATING_FAIL`).
Kiểm chứng trên case thật 07-24: **TMG/IVS = NGOÀI `universe_pit`** (khớp kết luận thủ công),
**TRC = TRONG universe + cờ `RATING_FAIL`** (rating 8L = 4 — thông tin MỚI mà nhánh `ticker_prune`
cũ không có).

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

#### 4.4-KQ — **G4/P4 = ESCALATED, KHÔNG CUTOVER** (job `Taylor_20260722_093055`, 2026-07-22)

Đã chạy đúng bước 1-2. Kết quả: **CẢ HAI cổng ở trên đều CHẶN.** Không đổi một dòng code nào trong
`golive_recommend_v23.py` — 3 vị trí P4 (`:167` ADV cap, `:492`/`:522` CAPIT breadth+pool) **vẫn đọc
`ticker_prune` có chủ ý**. Bằng chứng: `agents/Taylor/exp_capit_breadth/breadth_both.csv`
(3.129 phiên 2014-01-02 → 2026-07-21, cả 2 mẫu số cạnh nhau, chạy lại được bằng SQL trong finding bus).

**Cổng 1 (mục 4) — `capit_fired` ĐANG `true`.** `data/golive_v23_status.json` (date 2026-07-22,
signal_date 2026-07-21): `capit_fired=true`, `breadth_oversold=0,4621` vs `washout_gate=0,30`.
⚠️ Điểm cần hiểu đúng, đừng chờ nhầm: `capit_fired` **KHÔNG phải cờ "còn vị thế mở"** — nó là hàm
thuần của breadth HÔM NAY (`golive_recommend_v23.py:497`). Vậy nên "user đã giải ngân xong" **không**
làm nó về `false`; nó chỉ tắt khi breadth thị trường tự hồi xuống <0,30. Cổng này sẽ tự mở khi thị
trường hồi, không cần ai làm gì — nhưng tới lúc đó vẫn còn cổng 2.

**Cổng 2 (mục 3) — KHÔNG TỒN TẠI ngưỡng nào bảo toàn tập ngày fire.** Hai tập không tách được
tuyến tính trên mẫu số mới:

| Đại lượng | Giá trị |
|---|---|
| min `br_new` trên 82 ngày fire cũ | **0,2425** (2018-07-05) |
| max `br_new` trên 3.047 ngày không-fire cũ | **0,3067** (2022-11-17) |

max(không-fire) **>** min(fire) ⇒ mọi ngưỡng đều sai ít nhất vài ngày. Hai ứng viên tốt nhất:

- `WASHOUT_GATE'=0,3070` (sai ít nhất): **7 ngày lệch**, đều là fire cũ bị MẤT (0 fire giả) —
  2015-05-18, 2018-07-05, 2020-02-04, 2020-03-11, 2020-04-01, 2022-10-05, 2023-10-30.
- Giữ nguyên `0,30` (cutover ngây thơ): **8 ngày lệch** (4 mất / 4 thêm). Đúng tổng số ngày fire
  (82) nhưng ở mức **episode** thì: MẤT hẳn 2 đợt 1 ngày (2015-05-18, 2018-07-05) và THÊM 1 đợt
  mới **2021-07-12** — tức mua rổ washout giữa năm bull 2021, một hành vi chưa từng có trong bản gốc.

**Tác động TIỀN thật không chỉ ở fire/không-fire mà ở SIZE.** `capit_grind` (lookback 20-90 phiên
tìm ngày washout trước đó) đọc chính chuỗi breadth này, và nó nhân đôi/chia đôi size (0,75 ↔ 0,375).
Đếm số sự kiện lịch sử đổi kết cục size: **10 sự kiện** ở gate 0,30 / **9 sự kiện** ở gate 0,3070.
Nặng nhất: **2015-08-24 và 2015-08-25 lật `grind` True→False ⇒ size GẤP ĐÔI** trên một lần fire thật.

**Hôm nay (2026-07-21) thì cả 3 cấu hình cho kết quả GIỐNG HỆT** — fired=True, grind=False,
size=0,75, và pool CAPIT **trùng khít 11 mã** (PNJ/NCT/SIP/PVT/VNM/SAB/DHC/HAH/VHM/BFC/MCH) trên cả
2 mẫu số, vì bộ lọc `ROE_Min5Y≥0,12 ∧ ROIC5Y≥0,10 ∧ FSCORE≥6 ∧ ADV≥2 tỷ` đã siết chặt hơn nhiều so
với ranh giới universe. ⇒ **Rủi ro không nằm ở hôm nay; nằm ở lần fire kế tiếp và ở việc baseline
lịch sử của CAPIT bị đổi ngầm.**

**Đề xuất (chờ user quyết, KHÔNG tự chọn — đúng Q6/§8.4):**
- **A (mặc định của tôi)**: **pin `ticker_prune` vĩnh viễn cho riêng breadth+pool CAPIT**, ghi rõ lý
  do trong code như hiện tại. CAPIT là 1 trigger duy nhất, đã hiệu chuẩn, chạm tiền thật; universe
  mới không mang lại lợi ích gì cho nó (pool trùng khít) mà chỉ mang rủi ro đổi hành vi. Đánh đổi:
  production vẫn còn 1 dây phụ thuộc `ticker_prune` ⇒ §4.5 phải GIỮ gate depth/lag `ticker_prune` ở
  mức BLOCK chứ không hạ xuống WARN rồi gỡ.
- **B**: chấp nhận `0,3070` + 7 ngày lệch (toàn bộ theo hướng THẬN TRỌNG hơn — mất fire, không thêm
  fire giả), đổi lại cắt hẳn phụ thuộc `ticker_prune`. Cần user duyệt tường minh vì đây là đổi hành
  vi một tham số điều khiển tiền thật.
- **C**: viết lại breadth cho bất biến với mẫu số (vd đếm trên rổ cố định top-N thanh khoản). Đây là
  thiết kế lại chỉ báo, không phải migration — cần R&D + backtest riêng, không làm trong lần này.

#### 4.4-C — KẾT QUẢ R&D HƯỚNG C (user chốt C; job `Taylor_20260722_094530`, 2026-07-22): **VẪN KHÔNG TÁCH SẠCH — ESCALATE LẦN 2, KHÔNG CUTOVER**

Thiết kế đã đo (N-trial khai báo TRƯỚC trên bus, không tune): breadth = tỷ lệ `D_RSI<0.3` trên rổ
top-N thanh khoản (`Volume_3M_P50 × COALESCE(Price,Close)`, rank mỗi ngày trong `universe_pit_q`),
N ∈ {100, 150, 200, 250, 300} — 5 trials. Gate quy ước = trung điểm khoảng tách, KHÔNG dò lưới.
Artifacts: `exp_capit_breadth/{breadth_topn.sql,breadth_topn.csv,sweep_topn.py,detail_topn.py,conservative_topn.py,grind_union.py,gate_placement.py}`.

**Kết quả 1 — không N nào tách được tập fire cũ** (gap = min_fire − max_nonfire, ÂM cả 5):

| N | min br trên 82 ngày fire | max br trên 3.047 ngày non-fire | gap |
|---|---|---|---|
| 100 | 0,1900 | 0,3300 | −0,1400 |
| 150 | 0,2467 | 0,3333 | −0,0867 |
| 200 | 0,2850 | 0,3250 | −0,0400 |
| 250 | 0,2680 | 0,3080 | −0,0400 |
| 300 | 0,2433 | 0,3133 | −0,0700 |

**Kết quả 2 — thất bại là CẤU TRÚC, không phải nhiễu ngưỡng.** Các ngày vi phạm KHÔNG phải
knife-edge của chuỗi cũ: 2018-07-05 br_old=0,3143 (fire thoải mái) nhưng MỌI mẫu số mới chỉ ra
0,24–0,29 — fire hôm đó do ĐUÔI ILLIQUID của `ticker_prune` oversold, phần lõi thanh khoản thì
không; ngược lại 2022-09-19 br_old=0,2876 (không fire) nhưng top-200/250/300 ra 0,308–0,315 (lõi
thanh khoản oversold HƠN trung bình prune). Corr(br_old, br250)=0,9908 nhưng đúng các ngày biên thì
lệch theo thành phần rổ ⇒ **không tồn tại chuỗi bất-biến-mẫu-số nào tái tạo đúng 100% tập fire cũ**
— tập fire cũ mã hoá thành phần cụ thể (kể cả đuôi illiquid) của `ticker_prune`.

**Kết quả 3 — menu tốt nhất trong họ C** (so với B = `br_new@0,3070` của §4.4-KQ):

| Config | lệch | MẤT/THÊM | episode Δ | grind flip thật | ghi chú |
|---|---|---|---|---|---|
| B (`br_new@0,3070`) | 7 | 7/0 | mất 2 ep 1-ngày (2015-05-18, 2018-07-05) | 2015-08-24/25 size GẤP ĐÔI | khoảng trống gate 0,0027 |
| C-mixed (`br250@0,288`) | 5 | 2/3 | mất 1 ep (2018-07-05), THÊM 1 ep mới giữa bear 2022 (2022-09-19) | 0 | ⚠️ 3 fire GIẢ (sai hướng tiêu chí); giữ được 2015-05-18 chỉ nhờ margin 0,0013 — knife-edge, không robust |
| **C-conserv (`br250@0,31`)** | 7 | 7/0 | mất đúng 2 ep 1-ngày NHƯ B | y hệt B (2015-08-24/25) | khoảng trống 0,0040 (rộng hơn B); 7 ngày mất hơi khác B trong-episode nhưng tương đương kinh tế |

**Kết luận trung thực (đúng tiêu chí đã khai báo, không ép số):** C KHÔNG giải quyết "dứt điểm"
việc tái tạo lịch sử — ứng viên duy nhất đạt chuẩn "sai số nhỏ + toàn thận trọng" (`br250@0,31`)
có profile đổi-hành-vi **y hệt B về số lượng và độ nặng** (7 ngày mất, cùng 2 episode mất, cùng 1
cặp grind-flip). Giá trị THẬT của C nằm ở tương lai, không phải quá khứ: mẫu số universe đã swing
128 → 589 → 365 mã trong 2014–2026; top-N cố định miễn nhiễm với swing đó, còn B sẽ lại lệch thang
đo khi universe phình/co lần tới. Đánh đổi: thêm 1 bước ranking (phức tạp hơn), và N=250 chỉ thực
sự là "top-N" từ 2014-10 (trước đó universe < 250 ⇒ br250 ≡ br_new). Lưu ý dữ liệu: 2015-09-28
universe co còn 128 mã (hậu crash 08/2015, thanh khoản 3M co lại) — hành vi đúng của rule, không
phải lỗi.

**Trạng thái (lúc escalate): 3 vị trí P4 trong `golive_recommend_v23.py` (`:229` ADV cap, `:492`/`:522`
breadth+pool) VẪN đọc `ticker_prune` có chủ ý — không đổi dòng code nào.** Cổng "không cutover khi
`capit_fired=true`" cũng đang CHẶN độc lập (fired từ 07-20). Chờ user chọn: A (pin vĩnh viễn) /
B (0,3070, mất 7 ngày) / C-conserv (`br250@0,31`, mất 7 ngày tương đương B + bất biến mẫu số về
sau) — C-mixed KHÔNG khuyến nghị (fire giả + knife-edge).

#### 4.4-P4 — **IMPLEMENT C-conserv (user chốt 2026-07-22)**: breadth CUTOVER, pool + ADV **CÒN GHIM**
*(job `Taylor_20260722_100814`)*

**User chốt C-conserv** ⇒ đã wire vào `deploy_golive_dt5g_v4/golive_recommend_v23.py`. Điểm quan
trọng nhất của lô này: **P4 tách làm HAI switch độc lập, không phải một**, vì đo thật cho thấy hai
nửa có hồ sơ rủi ro khác hẳn nhau:

| Switch | Giá trị hôm nay | Phạm vi | Tác động ngày LIVE 07-22 |
|---|---|---|---|
| `CAPIT_BREADTH_SOURCE` | **`"pit"`** (CUTOVER) + `CAPIT_TOPN=250`, `WASHOUT_GATE=0,31` | trigger `capit_fired` + `capit_grind` (⇒ size) | **0 đồng** — A/B trên cùng dữ liệu: fired/size/grind/rổ/ADV cap **giống hệt** |
| `CAPIT_POOL_SOURCE` | **`"prune"`** (CÒN GHIM) | pool chọn rổ (pbz) + nguồn ADV cap | — (chưa cutover) |

`WASHOUT_GATE` được **buộc vào mẫu số** (`0,31 if pit else 0,30`) để không tồn tại trạng thái
"mẫu số mới + ngưỡng cũ" — đó là dạng hỏng nguy hiểm nhất của lô này. Rollback = sửa đúng 1 dòng.

**Vì sao pool KHÔNG cutover cùng breadth (phát hiện MỚI, chưa có trong §4.4-C):** đo ngày 07-22
(`universe_pit_p4_selfcheck.py` T6c2) — pool `pit` **thêm HVT** (pbz −1,362) ⇒ rổ đổi từ 4 mã
`[PVT, SAB, SIP, VNM]` thành 5 mã `[HVT, PVT, SAB, SIP, VNM]`: vừa **thêm một lệnh mua thật**, vừa
pha loãng equal-weight 25% → 20% cho 4 mã **đang khớp dở**. HVT không phải nhiễu: chất lượng thật
(ROE_Min5Y 16,1% · ROIC5Y 24,0% · FSCORE 7) nhưng **ADV thật chỉ 0,196 tỷ/phiên** — nó lọt sàn
"2 tỷ" của pool vì sàn đó đo **turnover MỘT NGÀY** (07-22: 2,063 tỷ, sát mép) chứ không đo ADV.
`ticker_prune` vô tình che lỗ hổng sàn-thanh-khoản này bấy lâu; bỏ prune ra là lộ. **Sửa sàn đó là
ĐỔI CHIẾN LƯỢC** (cần R&D + backtest riêng), không được làm lẫn vào migration. ⇒ Ghim `pool` tới khi
(a) `capit_fired` về `false`, VÀ (b) user duyệt riêng khoản sàn thanh khoản pool. Cổng Q5 ("không
cutover P4 khi `capit_fired=true`") đang chặn **đúng chỗ nó sinh ra để chặn**. ADV cap đi THEO
`CAPIT_POOL_SOURCE` (không theo breadth): ADV đo trên chính những cái tên pool đã chọn.

**Bảo hiểm mới đi kèm — fail-CLOSED độ tươi (`capit_breadth_is_stale`)**: `universe_pit` do một job
RIÊNG build; nếu job đó chưa chạy cho phiên mới nhất thì câu breadth vẫn trả kết quả, chỉ thiếu ngày
cuối ⇒ `breadth` lặng lẽ thành của HÔM QUA (đúng mẫu sự cố C1 07-12, nhưng lần này điều khiển một
lệnh mua thật). Xử lý: **không raise** (sẽ hạ cả recommender, BAL/LAG vô can) mà chặn riêng CAPIT
không fire lệnh mới trên dữ liệu cũ + nói to trong status JSON (`capit_breadth_stale`,
`capit_breadth_src_max`) và MD.

**Bằng chứng (đều chạy thật, không suy luận):**
- `universe_pit_p4_selfcheck.py`: **26/26 PASS**. Trong đó T4b MẤT **đúng 7 ngày đã công bố**
  (2015-05-18, 2018-07-05, 2020-02-04, 2020-03-11, 2020-03-25, 2020-04-01, 2022-06-15), T4a **THÊM
  0** ngày (0 fire giả), T5 grind lật **đúng 1 cặp** 2015-08-24/25, T7 fail-closed đủ 4 nhánh.
- A/B **end-to-end trên cùng dữ liệu 07-22** (chạy production 2 lần, lật đúng 1 dòng): khác nhau
  **chỉ** ở `breadth_oversold` 0,5096 → 0,4960 + 3 field metadata + `washout_gate`;
  `capit_fired=True`, `capit_size=0,75`, `capit_grind=False`, `n_capit_basket=4`, **`capit_adv_caps`
  bằng nhau từng đồng**. ⇒ đợt giải ngân CAPIT đang dở KHÔNG bị đụng.
- Số tổng 82→75 của §4.4-C là **đo tới 07-21**; hôm nay 07-22 fire ở CẢ HAI nhánh nên thành 83→76.
  Bất biến thật là **hiệu = 7** và tập fire mới là **tập con** — selfcheck assert theo bất biến đó,
  cố ý KHÔNG pin số tuyệt đối (pin tổng sẽ tự hỏng sau mỗi lần CAPIT fire).

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

### 5.4 ✅ KẾT QUẢ RE-PIN CUỐI CÙNG (G6 — XONG 2026-07-22)

Jobs: `Taylor_20260722_151919` (chạy) + `Taylor_20260722_154334` (ghi nhận). Điều kiện đo: **cache
`data/bq_cache` ĐÓNG CỨNG**, manifest `verified: true`, **14/14 bảng**, `verified_at
2026-07-22T14:22:24Z`. 3 chân khác nhau đúng 2 biến `UNIVERSE_SRC`/`EXP_TAG`; driver
`data/g6_repin/chain_after_resync_v2.sh`; logs `data/g6_repin/cache_v2_{control,control2,pit}.log`.

| Chân | Universe | Vintage | Final NAV | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|---|---|
| **control_v2c** | `ticker_prune` | cache 07-22 | 1.077,68B | **27,95%** | 1,85 | −18,4% | 1,52 |
| **control_v2c2** (chạy lại) | `ticker_prune` | cache 07-22 | 1.077,68B | **27,95%** | 1,85 | −18,4% | 1,52 |
| **pit_v2c** | **`universe_pit`** | cache 07-22 | 998,09B | **27,16%** | 1,81 | −18,1% | 1,50 |
| *(tham chiếu)* pin 2026-07-12 | `ticker_prune` | cache 07-12 (**khác vintage**) | — | 27,84% | 1,84 | −18,2% | 1,53 |

Self-check **0 VND** (BAL+LAG, cash-flow identity + final-NAV identity) ở cả 3 chân.

**H1 vs H2 — đã tách xong.** Hai chân control khớp **tuyệt đối** ⇒ **H1 LOẠI** ("engine không tất
định" — sai); **H2 XÁC NHẬN**: chênh 0,37pp giữa 2 lần chạy control trên **live BQ** sáng cùng ngày
(job `Taylor_20260722_112850`) là do **dữ liệu BQ trôi giữa các lần chạy khác giờ**. Engine ĐÃ được
xác nhận tất định trên cache đóng cứng. Hệ quả: delta pit đo lần này là tín hiệu thật, không còn bị
nhiễu-vintage che (lần đo live-BQ trước: delta 0,49pp < nhiễu 0,37pp ⇒ không kết luận được).

**⚠️ SO SÁNH CÔNG BẰNG = `pit_v2c` vs `control_v2c` (CÙNG VINTAGE), KHÔNG phải vs pin cũ 27,84%**
(khác vintage ⇒ trộn hiệu ứng universe với hiệu ứng dữ liệu trôi).
**Δ (pit − prune, cùng vintage): CAGR −0,79pp · Sharpe −0,04 · MaxDD tốt hơn nhẹ (−18,1 vs −18,4) ·
Calmar −0,02.**

**Kết luận pit-vs-prune:** R3 trên `universe_pit` **THẤP HƠN** `ticker_prune` cùng vintage 0,79pp —
**đúng hướng đã pre-register ở §8.5** (*"nhiều khả năng THẤP HƠN; nếu CAO HƠN mới là dấu hiệu nghi
ngờ"*). **KHÔNG điều tra thêm.** Phần chênh đọc là *bias vòng tròn/look-ahead của `ticker_prune` bị
khử*, không phải `universe_pit` chọn kém hơn (MaxDD còn tốt hơn nhẹ).

**❗Quyết định production CHƯA có:** có cutover **baseline R3 chính thức** sang `universe_pit`
(27,84% → 27,16%) hay không **KHÔNG thuộc phạm vi G6** — cần **escalate user riêng**. Cho tới lúc đó
**số chính thức vẫn là 27,84%**, trích dẫn kèm ghi chú đo-lại-cùng-vintage 27,16% và khoảng
[~27,2%; ~31,3%] (vụ LAG %ADV). Đã ghi đầy đủ vào `data/results_registry.md`.

*(Về nhãn `PROVISIONAL` đề xuất ở §5.2/§6-G0/§9-Q3: **chưa từng được ghi vào `results_registry.md`**
— grep xác nhận 0 hit. Không có nhãn nào sót lại cần gỡ; §5.4 này thay thế toàn bộ cảnh báo tạm đó
bằng số đo thật.)*

---

## 6. TIMELINE & EFFORT

Đơn vị "phiên" = 1 phiên làm việc tập trung của Taylor (~2-4h agent-time). Ước lượng có nêu độ tin cậy.

| Giai đoạn | Việc | Effort | Tin cậy | Chặn bởi |
|---|---|---|---|---|
| **G0** | Lấy lại văn bản gốc Q&A bq_admin (§0); đánh dấu R3 `PROVISIONAL` (§5.2) | <0,5 phiên | Cao | User |
| **G1** | `bin/build_universe_pit.py` + selfcheck (idempotent, atomic, B8) | 1-1,5 phiên | Cao | — |
| **G2** | Backfill 2000→nay (compute rẻ: 215MB) + **kiểm định**: chạy lại bảng §2.2 với median-60-phiên tự tính, ~30 mốc | **1 phiên** (compute ~phút, kiểm định chiếm hết) | Cao | G1 |
| **G2b** | ✅ **XONG + ĐÃ ĐÓNG 2026-07-22.** Đo xong (§3.2b-G2b) → escalate → **user chốt A′ + Q-C, không Q-B** → **Q-C đã implement (§3.2c), selfcheck PASS**. **Cổng cứng §3.2b/Q9 MỞ** (cổng CAPIT §4.4 vẫn đóng riêng) | 0,5-1 phiên | Trung bình | G2 |
| **G3** | 🔶 **ĐANG DỞ 2026-07-22**: **P1 XONG** (`due_diligence.py`, selfcheck 20/20) · **P2 XONG** (`custom_basket.py` → `universe_pit_q`, user duyệt, commit `ce7d457`, selfcheck 13/13, rổ LIVE byte-identical, v4final/eyrisk selector 12/12 PASS sau commit) · **P3 XONG** (`golive_recommend_v23.py` panel D1 ICB-8633, user duyệt, commit `0bfbdfe`, selfcheck 14/14, VHM-look-ahead fix có bằng chứng, A/B trọn script byte-identical) ⇒ **P1-P3 ĐỦ, G3 XONG** (P4/P5/P6 là hạng mục riêng) | 1 phiên | Trung bình | G2 |
| **G4** | ✅ **ĐO XONG 2 VÒNG, ESCALATED 2026-07-22.** Vòng 1 (§4.4-KQ): không tồn tại gate bảo toàn trên mẫu số mới. Vòng 2 hướng C (§4.4-C): top-N thanh khoản N∈{100..300} vẫn không tách sạch — thất bại CẤU TRÚC (đuôi illiquid của prune); ứng viên tốt nhất C-conserv `br250@0,31` = ngang B. **User chốt C-conserv ⇒ ĐÃ IMPLEMENT nửa breadth (§4.4-P4, selfcheck 26/26, A/B live 0 đồng); pool + ADV còn ghim `ticker_prune` (pool `pit` thêm HVT vào rổ đang giải ngân)** | 1 phiên | **Thấp** — có thể không tồn tại ngưỡng bảo toàn ⇒ escalate (đã xảy ra đúng vậy, cả 2 vòng) | G2 |
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

## 9. ✅ DỰ ÁN ĐÃ ĐÓNG (2026-07-22) — trạng thái cuối + phần duyệt (lưu trữ)

> **DỰ ÁN `ticker_prune` → `universe_pit` ĐÓNG HOÀN TOÀN ngày 2026-07-22** (job cuối
> `Taylor_20260722_154334`). Bảng dưới là trạng thái cuối cùng; phần "cần user duyệt" ban đầu giữ
> nguyên bên dưới làm dấu vết lịch sử (đã duyệt xong toàn bộ Q1-Q9 ngày 2026-07-22).

| Hạng mục | Trạng thái cuối | Bằng chứng |
|---|---|---|
| **Q1-Q9** — phê duyệt phương án | ✅ **USER DUYỆT TOÀN BỘ 2026-07-22** (Q9 theo khuyến nghị **Q-A + Q-C, KHÔNG Q-B**) | §9 bảng dưới |
| **G1** — builder + backfill | ✅ XONG — `mike/bin/build_universe_pit.py`, selfcheck **15/15**, bảng `tav2_mike.universe_pit` 4.089.541 dòng / 6.339 phiên, 0 trùng | §10.1 |
| **G2 / G2b** — kiểm định recall + lớp chất lượng | ✅ XONG — recall median-60 tự tính **KHÔNG tụt** (98,6-99,1%), không hiệu chuẩn lại B3; G2b → user chốt **A′ + Q-C**, Q-C đã implement (`universe_pit_quality`) ⇒ **cổng cứng Q9 MỞ** | §10.2, §3.2c |
| **P1** — `due_diligence.py` | ✅ **CUTOVER XONG** — commit `b2d0502`, selfcheck 20/20 | §4.2 |
| **P2** — `custom_basket.py` (custom30V, CHẠM TIỀN THẬT) | ✅ **CUTOVER XONG** — commit `ce7d457`, user duyệt, selfcheck 13/13, rổ LIVE **byte-identical**, rollback 1 chữ `UNIVERSE_SOURCE` | §4.3b |
| **P3** — `golive_recommend_v23.py` panel D1 | ✅ **CUTOVER XONG** — commit `0bfbdfe`, user duyệt, selfcheck 14/14, VHM-look-ahead đã fix, A/B trọn script byte-identical ⇒ **0 tác động LIVE** | §10.3 |
| **P4** — CAPIT breadth (C-conserv) | ✅ **CUTOVER XONG** — commit `dcee252`, **quant-skeptic CONFIRMED**, `CAPIT_BREADTH_SOURCE="pit"` top-250 gate 0,31, selfcheck 26/26, A/B live 07-22 **không đổi 1 đồng**. ⚠️ **`CAPIT_POOL_SOURCE` + ADV cap CỐ Ý còn ghim `ticker_prune`** (pool `pit` sẽ thêm HVT vào rổ đang giải ngân — là ĐỔI CHIẾN LƯỢC, không gộp vào migration) | §4.4-P4 |
| **G6** — re-pin R3 | ✅ **XONG** — control 27,95% vs **pit 27,16%** cùng vintage (Δ **−0,79pp**), 2 chân control khớp tuyệt đối ⇒ H1 loại / H2 xác nhận; đúng hướng pre-register §8.5 | **§5.4** |
| Nhãn `PROVISIONAL` (Q3/G0) | ✅ **KHÔNG CÒN SÓT** — grep `results_registry.md` = 0 hit (nhãn này thực tế chưa từng được ghi vào registry); §5.4 thay thế bằng số đo thật | §5.4 |

**Còn mở SAU khi dự án migration đóng (hạng mục RIÊNG, không chặn việc đóng dự án — CHƯA làm trong job này):**

| # | Việc | Trạng thái |
|---|---|---|
| **Quyết định production** | Cutover **baseline R3 chính thức** sang `universe_pit` (27,84% → 27,16%) | ✅ **ĐÃ QUYẾT (user, 2026-07-22) + ĐÃ THỰC HIỆN** — job `Taylor_20260722_155549`. `pt_v23_audit_2014.py` default `UNIVERSE_SRC` = `"pit"`; chạy lại KHÔNG set env ra **đúng 27,16%/1,81/−18,1%/1,50**, self-check 0 VND (BAL+LAG), CSV **identical** với `pit_v2c`. **Số CHÍNH THỨC nay là 27,16%/1,81/−18,1%/1,50**; số `ticker_prune` giữ làm lịch sử. Đã đồng bộ `data/results_registry.md` + `mike/kb/canonical.md`. Phạm vi KHÔNG gồm P4 (`CAPIT_POOL_SOURCE`/ADV vẫn ghim prune) |
| **G7** | Rà soát N-trial tuần qua (§5.3) — phân loại giữ/chạy-lại; ứng viên rõ nhất: **lọc thanh khoản LAG** (`lag_filter_illiquid`, commit `4b7aaa1`) chồng lớp với B3/B4 | 🔶 **CÒN TREO** — chưa làm |
| **G8** | P6 gate + `data_registry.md` (prune→TRAP, pit→CANONICAL) + `cron_registry.md` + `coding_guidelines.md` + `universe_ruleset.md` v1 | ✅ **`data_registry.md` ĐÃ SỬA** (2026-07-22, audit toàn repo dispatch bởi Mike): entry `ticker_prune` đổi từ "ĐANG XEM XÉT" sang **TRAP** cho code mới, ghi rõ khung "silent drift" (bảng vẫn được ghi liên tục nên KHÔNG có tín hiệu tự động báo lệch — khác hẳn rủi ro file đông cứng đã gặp ở vụ monolith 06-26); §"Quy tắc chọn universe" đổi khuyến nghị mặc định sang `universe_pit`. `cron_registry.md`/`coding_guidelines.md`/`universe_ruleset.md` v1 **CHƯA làm** — vẫn treo. |
| **G8.1 — MỚI** | `trading_bot/executor.py:588-603` đọc cache `ticker_prune` (rvol_20d cho `gap_adaptive_enabled`/`extreme_regime_enabled`/`chase_cap_vol_scale_enabled`) — **KHÔNG nằm trong 4 phase P1-P4 gốc**, phát hiện qua audit toàn repo 2026-07-22 (dispatch Mike, không phải job Taylor) | 🔶 **MỚI PHÁT HIỆN, CHƯA LÀM** — hiện TẮT trên cả SpaceX/ZaloPay (chỉ bật ở account paper), nên KHÔNG phải gap tiền thật hôm nay. Nhưng cả 3 cờ đang trên lộ trình lên live (KB "Đang R&D"). **Cổng cứng: PHẢI migrate executor.py sang `universe_pit` TRƯỚC KHI duyệt bật bất kỳ cờ nào trong 3 cờ cho SpaceX/ZaloPay** — đừng để lặp lại kiểu sự cố "P4 CAPIT breadth" (universe đổi mà không ai để ý gate cũ vẫn chạy). |
| **G9** | quant-skeptic full review toàn bộ dự án | 🔶 **CÒN TREO** — từng phần chạm tiền thật (P2/P3/P4) đã qua skeptic riêng; review tổng chưa chạy |
| **P5/P6** | `CAPIT_POOL_SOURCE` cutover + gate vận hành cấm đọc `ticker_prune` | 🔶 **CÒN TREO** — chặn bởi (a) `capit_fired=false` và (b) user duyệt riêng sàn thanh khoản pool |

---

### 9.1 (lưu trữ) Bảng phê duyệt ban đầu — ĐÃ DUYỆT TOÀN BỘ 2026-07-22

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

1. ✅ **G2b XONG + ĐÓNG** (2026-07-22): đo → escalate → user chốt **A′ + Q-C** → Q-C implement
   (§3.2c). **Cổng cứng §3.2b/Q9 đã MỞ.**
2. 🔶 **G3 đang dở**: **P1 đã cutover** (`due_diligence.py`, §4.2) · **P2 đã cutover 2026-07-22**
   (`custom_basket.py`, user duyệt — CHẠM TIỀN THẬT, rổ LIVE byte-identical, rollback 1 chữ
   `UNIVERSE_SOURCE`) · **P3 đã cutover 2026-07-22** (`golive_recommend_v23.py` panel D1, user duyệt,
   commit `0bfbdfe`, selfcheck 14/14, VHM-look-ahead xác nhận đã fix, A/B trọn script byte-identical
   ⇒ 0 tác động LIVE hôm nay). **G3 coi như XONG** cho phần P1-P3; P4/P5/P6 vẫn mở.
3. ✅🔶 **G4/P4 — user chốt C-conserv, ĐÃ IMPLEMENT MỘT NỬA** (2026-07-22, §4.4-P4):
   **breadth CUTOVER** (`CAPIT_BREADTH_SOURCE="pit"`, top-250, gate 0,31 — selfcheck 26/26, A/B
   live 07-22 không đổi 1 đồng), **pool + ADV cap CÒN GHIM `ticker_prune`** vì đo được pool `pit`
   sẽ thêm **HVT** vào rổ CAPIT **đang giải ngân dở** (lộ lỗ hổng sàn thanh khoản pool đo turnover
   1 ngày thay vì ADV — là ĐỔI CHIẾN LƯỢC, không làm lẫn vào migration). **Còn mở**: cutover
   `CAPIT_POOL_SOURCE` sau khi (a) `capit_fired=false` và (b) user duyệt riêng sàn thanh khoản pool.
4. Re-pin R3 (§5.1) — **chưa làm, và P2 vừa làm nó cần thiết hơn**: rổ custom30V đổi ở 4 mốc rebal
   2021-06 → 2022-05 (§4.3b đính chính) ⇒ chuỗi NAV backtest 2021-2022 sẽ khác bản đang pin 27,84%.
4. **Không cần dispatch quant-skeptic vòng 2** cho các sửa đổi tài liệu (chúng chỉ **hạ** mức tự tin
   và **siết** thêm cổng, không nới lỏng gì). **Cần** skeptic khi: (a) G2b dẫn tới đề xuất thêm tham
   số chất lượng vào tầng universe (Q-B), hoặc (b) trước cutover bất kỳ consumer chạm tiền thật.
   G1 tự nó **không đổi hành vi production nào** — chỉ thêm một bảng mới chưa ai đọc.
