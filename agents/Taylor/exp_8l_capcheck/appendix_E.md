
---

# PHỤ LỤC E — **KHÉP CHUỖI**: hai tầng bài toán (định-thời-điểm vs chọn-cổ-phiếu), và kiểm tra 8L rating có mắc lỗi kiểu-VIC không

**Ngày dữ liệu: 2026-08-01 (snapshot `ticker_1m` 2026-07-31)** · job `Taylor_20260802_014330` · Taylor (Quant)
**Loại: RESEARCH tổng hợp + 1 kiểm tra thực nghiệm N cao — KHÔNG wire, KHÔNG đổi tham số production nào.**

> **Vì sao có phụ lục này.** Bốn phụ lục trước (A→D) cùng hỏi một câu hỏi kinh tế theo bốn cách cắt
> khác nhau và cùng trượt. Phụ lục E **không thêm một cách cắt thứ năm** — nó làm hai việc khác hẳn:
> (1) nói rõ **lý do cấu trúc** khiến cả họ câu hỏi đó không thể trả lời được bằng dữ liệu VN hiện
> có, để đóng mạch lại thay vì thử tiếp; (2) chuyển đúng câu hỏi *"định giá có bị méo bởi một mã
> vốn hoá lớn không"* sang **tầng có đủ N để trả lời dứt khoát** — tầng chọn cổ phiếu (8L rating) —
> và trả lời nó.

---

## E.0 Trả lời ngắn

| Câu hỏi | Trả lời |
|---|---|
| Có nên thử thêm cách ghép DT5G × Value Radar thành tín hiệu định thời điểm không? | **KHÔNG** — không phải vì các thiết kế đã thử đều tồi, mà vì **cỡ mẫu cấu trúc** của bài toán này ở VN là ~22–26 quan sát độc lập. 0/110 phép thử sống sót là **kết quả đúng dự đoán** của một bài toán thiếu N, không phải chuỗi xui rủi. §E.2 |
| Value Radar nên ở đâu? | **Giữ nguyên hiển thị-thuần cạnh DT5G.** Không nâng thành gate/tilt. Điều kiện tối thiểu để xét lại đã được nâng ở §D.7 (N_trials ≥110 + DSR + PBO) — và cần **dữ liệu mới thật**, tức ~3–5 năm nữa. §E.5 |
| Phát hiện "khử méo do 1 mã vốn hoá lớn (VIC)" của Phụ lục B/C có phải áp vào 8L rating không? | **KHÔNG CẦN — 8L rating miễn nhiễm theo thiết kế, và đã kiểm chứng thực nghiệm.** Bỏ hẳn VIC khỏi universe rồi chạy lại **toàn bộ** pipeline `rating_8l.main()`: **0/857 mã đổi rating, 0/104 mã đổi zone, |Δpercentile| = 0,0000**. §E.4 |
| Có phát hiện gì cần xử lý không? | **1 phát hiện phụ, thuộc data-ops (không phải 8L):** `tav2_bq.ticker` tụt từ ~1.255 mã/phiên (đến hết T5/2026) xuống ~823 mã/phiên (T7/2026). **401 mã biến mất — nhưng cả 401 đều có thanh khoản ≤ 0,28 tỷ/phiên** (trần LIQ_MIN của screener là 3 tỷ) ⇒ **rổ đầu tư được KHÔNG bị ảnh hưởng**. Vẫn nên báo Winston. §E.4.5 |

---

## E.1 Tổng kết toàn chuỗi — 110 phép thử, 0 sống sót

Bảng dưới **không lặp lại** chi tiết đã có ở A/B/C/D; chỉ để nhìn một lần toàn cảnh.

| # | Báo cáo | Câu hỏi cắt theo cách nào | N quan sát | Số phép thử | Kết luận |
|---|---|---|---|---|---|
| 1 | Phụ lục A | ROE gộp toàn thị trường (mức chu kỳ lợi nhuận) | ~17 năm chuỗi | 12 | NO-GO (0/12 qua Bonferroni/BH) |
| 2 | Phụ lục B | P/B đo 9 cách (có/không VIC, aggregate/median/cap10) | chuỗi ngày | 9 | **Lật kết luận định vị định giá**; không wire |
| 3 | `fundamental_valuation_framework_20260729.md` §2 | CAPE / EV-EBITDA / ERP / composite, điều kiện CAPIT | 26 sự kiện | 56 | 0/56 qua BH |
| 4 | Phụ lục C | Value Radar (expanding-2008), 17 lăng kính + biến thể | chuỗi + 23 nhãn | 23 | p tốt nhất **0,049 thô**; 0/17 qua BH |
| 5 | Phụ lục D | Radar rolling-10Y × đúng 26 đợt CAPIT-washout | 25 sự kiện (ĐẮT chỉ N=2) | 10 | Không đủ bằng chứng; p nhỏ nhất 0,133 |
| | **TỔNG** | | | **110** | **0 sống sót** |

Ngưỡng Bonferroni 5% trên họ 110 = **0,00045**; ngưỡng BH (FDR 10%) cho p nhỏ nhất = **0,00091**.
**p tốt nhất của cả mạch = 0,049**, lớn hơn ngưỡng cần **~54 lần**.

**Điểm cần nhớ khi trích dẫn về sau:** con số 0,049 (Phụ lục C.4.4) từng được mô tả là "vừa đủ loại
0". Khi cộng dồn đúng cách trên toàn họ, **nó không còn ý nghĩa nào**. Bất kỳ ai muốn dùng lại nó
làm căn cứ phải khai báo N_trials = 110, không phải 17 hay 23.

---

## E.2 Vì sao tầng định-thời-điểm ở VN **luôn** thiếu N — hạn chế cấu trúc, không phải tạm thời

Đây là phần quan trọng nhất của phụ lục này. Nếu chỉ nhớ "đã thử 110 lần đều trượt" thì kết luận sai
là *"thử thêm cách khác đi"*. Kết luận đúng là *"họ câu hỏi này không có đủ dữ liệu để trả lời, và
sẽ không có trong nhiều năm tới"*.

**Bốn ràng buộc, nhân với nhau:**

1. **Lịch sử tin cậy chỉ bắt đầu ~2008.** `ticker_prune` có 2006 ≈ 19 tên, 2007 ≈ 74, **2008 ≈ 105**
   (lần đầu vượt 100). Trước 2008 thị trường quá mỏng để một tín hiệu breadth/định giá toàn thị
   trường có nghĩa. ⇒ trần cứng ≈ **18 năm** dữ liệu dùng được, không phải 26 năm như `ticker` gợi ý.
2. **Đơn vị quan sát của bài toán định thời điểm là *đợt*, không phải *ngày*.** DT5G có **49 lần
   chuyển trạng thái** trong 2014→2026 (≈ 12,5 năm) ⇒ **~24–25 đợt regime trọn vẹn**. CAPIT-washout
   cho **26 sự kiện** kể từ 2009. Hai cách đếm độc lập cùng ra **~22–26**. Số dòng dữ liệu (~3.100
   phiên) **không phải** N — chúng tự tương quan gần như hoàn toàn trong cùng một đợt.
3. **Chính DT-gate làm N nhỏ đi — có chủ đích.** Cổng cam kết bất đối xứng (`enC=25`/`enX=25` phiên
   để vào CRISIS/EX-BULL) tồn tại để **cắt whipsaw**: nó ép base ~153 chuyển trạng thái xuống 49. Đó
   là điều ta muốn cho quản trị rủi ro, nhưng nó đồng thời **giảm 3 lần** số quan sát dành cho việc
   kiểm định thống kê. **Không thể vừa muốn ít whipsaw vừa muốn nhiều N** — đây là đánh đổi cấu
   trúc, không phải lỗi thiết kế.
4. **Cửa sổ forward chồng lấn.** Các sự kiện cách nhau <12 tháng chia sẻ phần lớn cửa sổ r12M
   (§D.8 mục 2) ⇒ số quan sát **thực sự độc lập** còn thấp hơn nữa, ước ~15.

**Hệ quả định lượng.** Với N ≈ 25 chia hai nhóm và độ lệch chuẩn lợi suất 6M của VNINDEX ở mức lịch
sử, một phép so sánh hai nhóm chỉ đủ sức phát hiện những hiệu ứng **rất lớn**; mọi hiệu ứng cỡ vừa
(vài điểm phần trăm) đều nằm gọn trong nhiễu. Đó chính xác là điều Phụ lục D đo được: CI90 của mọi
hiệu đều phủ 0 với biên rộng **gấp nhiều lần** chính hiệu đó.

**Vì sao "chờ thêm dữ liệu" không giải quyết được trong ngắn hạn.** N tăng theo **số đợt regime**,
không theo số phiên. Nhịp lịch sử ≈ **2 đợt/năm** ⇒ để N tăng 20% (25 → 30) cần **~2,5 năm**; để đủ
sức phân biệt một hiệu cỡ vừa cần **hàng chục năm**. Thu thập thêm vài tháng dữ liệu **không đổi gì**.

> **Kết luận §E.2:** không phải "chưa tìm ra cách ghép đúng". Là **bài toán định thời điểm ở tầng
> chỉ số, trên thị trường VN, không đủ dữ liệu để phân định**. Mọi thiết kế mới (ma trận 2 chiều
> DT5G-state × radar-band, ngưỡng động, v.v.) sẽ chạy vào **đúng ràng buộc N này** và chỉ cộng thêm
> vào mẫu số 110.

---

## E.3 Đối chiếu hai tầng — vì sao tầng chọn-cổ-phiếu mạnh hơn hẳn

|  | **Tầng ĐỊNH THỜI ĐIỂM** (DT5G, Value Radar) | **Tầng CHỌN CỔ PHIẾU** (8L Rating / composite v3) |
|---|---|---|
| Đơn vị quan sát | 1 đợt regime | 1 mã × 1 kỳ |
| N thực dụng | **~22–26** (thực độc lập có thể ~15) | **856 mã** ở snapshot hôm nay; qua nhiều kỳ là hàng chục nghìn cặp |
| N tăng thế nào | ~2 đợt/năm — **rất chậm** | mỗi kỳ báo cáo là một lát cắt mới **toàn bộ** universe |
| Bằng chứng mạnh nhất đang có | p tốt nhất **0,049 thô**, 0/110 qua BH | **1/PE: IC +0,125, hit-rate 94%** (`kb/KNOWLEDGE.md`); PS resid IC +0,057/+0,105; div lens +0,031 IS / +0,030 OOS |
| Trạng thái | Radar = hiển thị-thuần; DT5G = cổng phòng thủ (bảo hiểm, **không** tăng lợi suất) | **LIVE**, là gate cứng `rating ≤3` cho LAG + đầu vào custom30V |

Điểm mấu chốt **không phải** "8L tốt hơn radar". Là: **cùng một ý tưởng kinh tế (rẻ thì tốt hơn) khi
đặt ở tầng cross-sectional thì đo được, khi đặt ở tầng time-series thì không đo được** — vì tầng
cross-sectional có N lớn hơn ~35 lần chỉ trong một ngày, và tăng thêm mỗi kỳ.

Đây cũng là lý do 8L rating **đã** kết luận dứt khoát được điều mà 110 phép thử ở tầng chỉ số không
kết luận nổi: *"value dominates ALL regimes, kể cả BULL"* (`kb/KNOWLEDGE.md`). Cùng một câu hỏi, chỉ
khác tầng.

---

## E.4 Kiểm tra thực nghiệm: 8L rating **có** mắc lỗi méo-do-một-mã-vốn-hoá-lớn không?

### E.4.1 Vì sao đặt câu hỏi này

Phụ lục B/C đã chứng minh: ở **tầng chỉ số**, một mã (VIC) đủ sức bóp méo P/B và P/E gộp của cả thị
trường, đảo ngược cả kết luận "đắt hay rẻ". Câu hỏi công bằng tiếp theo: **hệ đang LIVE dùng để chọn
cổ phiếu có chung bệnh đó không?**

### E.4.2 Trả lời theo thiết kế (đọc code, `rating_8l.py`)

`rate_row()` — hàm sinh ra `rating` (đúng thứ mà gate `≤3` dùng) — nhận **duy nhất** một dòng dữ liệu
của **chính mã đó** (`core_score`, `stability`, `real_lev`, `redflag`, `eq_flag`) cộng với các registry
tra theo tên mã (`MOAT_TIER`, `FORENSIC`, `BANKD`, `POWERD`). **Không có một đại lượng cross-sectional
nào** trong đường tính rating. ⇒ Theo cấu trúc, rating của mã X **không thể** phụ thuộc vào sự tồn
tại hay giá của mã Y.

Bước cross-sectional **duy nhất** trong cả pipeline nằm ở **trục value** (`_route_pct_raw`,
`value_yield_pct` — xếp hạng phân vị `ey/cfy/ps/eveb`), và nó chỉ ảnh hưởng `value_score_v3` → `zone`
(BUY-NOW / ACCUMULATE / WATCH-RICH), tức **lớp trình bày/xếp hạng**, không phải cổng chất lượng.

**⚠️ Đính chính một con số hay bị nói sai** (nêu rõ vì dispatch dùng số cũ): bước phân vị này **không**
chạy trên 700–1090 mã. Nó chạy trên `scr = out[rating≤3 AND liq≥3 tỷ]` = **104 mã hôm nay**, rồi còn
chia nhỏ theo `val_route`: BANK 19 · COMPOUNDER 17 · RETAIL 14 · REALESTATE 13 · D&A_HEAVY 13 ·
SECURITIES 13 · CYCLICAL 11 · POWER 3 · INSURANCE 1. **Pool thật để tính phân vị là 1–19 mã.** Con số
856 chỉ đúng cho **rating** (per-stock, độc lập từng mã). Phải phân biệt hai cái này khi trích dẫn.

### E.4.3 Kiểm chứng thực nghiệm — leave-one-out trên **chính** pipeline production

Không mô phỏng lại logic; chạy lại **nguyên xi** `rating_8l.main()` ba lần, khác nhau **duy nhất** ở
tập mã bị bỏ khỏi universe **từ đầu** (trước mọi bước tính). Dữ liệu BQ lấy **một lần** rồi cache ⇒
ba lần chạy có đầu vào giống hệt nhau tới từng chữ số. Đầu ra ghi vào thư mục probe qua
`WORKDIR_8L` ⇒ **không chạm** bất kỳ file canonical nào (`data/rating_8l*.csv` của production nguyên vẹn).

| Lần chạy | Bỏ khỏi universe | Mã được rate | Mã vào screener |
|---|---|---|---|
| **A** | — (đầy đủ) | 859 | 104 |
| **B** | VIC | 858 | 104 |
| **C** | VIC, VHM, VCB, BID, VGI (top-5 vốn hoá) | 854 | 100 |

**Kết quả B (bỏ VIC) — trên 857 mã chung:**

| Đại lượng | Số mã thay đổi |
|---|---|
| `rating` (cổng gate ≤3) | **0** |
| Số mã qua gate ≤3 | 420 → **420** |
| `ey_pct` / `cfy_pct` / `ps_pct` / `value_score_v3` | **0** — max \|Δ\| = **0,0000** |
| `zone` (BUY-NOW / ACC / WATCH-RICH) | **0** |

Khác biệt **duy nhất** trên toàn bộ log 36 KB của hai lần chạy, khi `diff` trực tiếp:

```
< rated 859 tickers
> rated 858 tickers
< REALESTATE   0  16   19   38   10
> REALESTATE   0  16   19   37   10
```

Nghĩa là: **thứ duy nhất mất đi là chính dòng của VIC** trong ô "REALESTATE, rating 4". Không một mã
nào khác nhúc nhích.

**Kết quả C (bỏ top-5 vốn hoá) — trên 853 mã chung:**

| Đại lượng | Kết quả |
|---|---|
| `rating` | **0 mã đổi**; qua gate 416 → 416 |
| max \|Δ ey_pct\| | 0,0805 (41/100 mã lệch >0,01) |
| max \|Δ cfy_pct\| | 0,1333 (30/100) |
| max \|Δ value_score_v3\| | 0,0520 (37/100) |
| `zone` | **1 mã đổi**: MBB `1_BUY-NOW` → `2_ACCUMULATE` (score 0,714 → 0,679) |

**Diễn giải đúng của lần C** (đừng đọc thành "hệ vẫn bị méo"): bỏ 4–5 mã khỏi một pool chỉ 11–19 mã
thì phân vị của các mã còn lại **phải** dịch — biên dịch bị chặn cơ học ở ~k/N (5/100 = 0,05, khớp
với max Δ score 0,052 đo được). Đây là hiệu ứng **thành phần rổ** khi ta cố tình xoá những mã có
thật, **không phải** hiện tượng một mã lấn át các mã khác qua trọng số vốn hoá. Phân biệt hai thứ
này là điểm cốt lõi: ở tầng chỉ số, VIC bóp méo **vì nó nặng 1,66 triệu tỷ trong mẫu số cap-weighted**;
ở tầng chọn cổ phiếu, VIC **chỉ đáng 1 phiếu như mọi mã khác** — và lần B chứng minh phiếu đó bằng 0.

### E.4.4 Chính VIC hôm nay được 8L chấm bao nhiêu?

| ticker | route | rating | core_score | PE | PB | pb_z | liq (tỷ) |
|---|---|---|---|---|---|---|---|
| **VIC** | REALESTATE | **4** | 2 | **142,69** | **10,81** | **+2,99** | 718,6 |
| VHM | REALESTATE | 2 | 7 | 7,62 | 2,22 | +0,96 | 594,0 |
| VCB | BANK | 1 | 6 | 11,90 | 1,99 | −2,09 | 175,5 |
| CTG | BANK | 1 | 6 | 5,95 | 1,19 | −1,16 | 285,2 |
| FPT | COMPOUNDER | 2 | 8 | 11,50 | 2,81 | −1,66 | 476,0 |
| MSN | COMPOUNDER | 4 | 2 | 13,69 | 1,95 | −1,24 | 299,5 |

**VIC = rating 4 ⇒ trượt gate ≤3, và không có mặt trong screener 104 mã.** Đây là điểm đáng chú ý
nhất của cả phụ lục: ở tầng chỉ số, VIC làm cả thị trường **trông đắt** và ta phải bỏ công khử nó ra;
ở tầng chọn cổ phiếu, VIC **tự loại mình** bằng chính số của nó (PE 142,7 / PB 10,8 / pb_z +2,99).
Thiết kế per-stock không "chịu đựng" được vấn đề — nó **đảo ngược** vấn đề.

### E.4.5 Rổ qua gate ≤3 có lệch ngành / lệch vốn hoá bất thường không?

**Theo ngũ phân vị vốn hoá** (as-of PIT từ `tav2_bq.fa_ratings_8l`, ghép giá cùng ngày; Q1 = nhỏ nhất):

| Ngày | Q1 | Q2 | Q3 | Q4 | Q5 (lớn nhất) |
|---|---|---|---|---|---|
| 2022-07-29 | 0,412 | 0,523 | 0,542 | 0,606 | 0,667 |
| 2023-07-31 | 0,359 | 0,450 | 0,514 | 0,489 | 0,534 |
| 2024-07-31 | 0,283 | 0,468 | 0,577 | 0,523 | 0,662 |
| 2025-07-31 | 0,350 | 0,480 | 0,516 | 0,554 | 0,613 |
| 2026-01-30 | 0,392 | 0,448 | 0,579 | 0,557 | 0,665 |
| **2026-07-31** | **0,327** | **0,473** | **0,473** | **0,628** | **0,677** |

Tỷ lệ qua gate **tăng đơn điệu theo vốn hoá ở mọi năm** — công ty lớn hơn thì chất lượng cơ bản tốt
hơn, đúng như kỳ vọng kinh tế, và **có mặt từ 2022**, không phải hiện tượng mới. Hồ sơ hôm nay nằm
**trong khoảng lịch sử** ở cả 5 ngũ phân vị. **Không có bất thường.**

**Theo route:**

| route | 2024-07-31 | 2025-07-31 | 2026-07-31 | N pool |
|---|---|---|---|---|
| COMPOUNDER | 0,418 | 0,423 | **0,422** | 1016 |
| REALESTATE | 0,471 | 0,442 | 0,425 | 106 |
| CYCLICAL | 0,516 | 0,548 | 0,613 | 31 |
| BANK | 0,593 | 0,667 | **0,852** | 27 |
| SECURITIES | 0,357 | 0,167 | 0,340 | 47 |
| INSURANCE | 0,846 | 0,769 | 0,769 | 13 |
| POWER | 0,915 | 0,958 | **1,000** | 48 |

COMPOUNDER — pool lớn nhất, chiếm phần lớn universe — **ổn định đến mức đáng chú ý** (0,418 / 0,423 /
0,422 qua ba năm). Hai điểm nên **ghi nhận nhưng không kết luận** ở đây:

- **POWER = 1,000** (48/48 mã qua gate). `rate_power()` ánh xạ verdict của `power_lens.csv` vào rating
  2–3 cho mọi trạng thái trừ DEBT_STRESS ⇒ trong route này gate **không lọc gì**. Đây là **tính chất
  thiết kế của lens**, không phải méo do vốn hoá — nhưng nó có nghĩa là với POWER, tính chọn lọc phải
  đến từ tầng khác (value/liquidity). Đáng đưa vào danh sách rà lens, **không** phải việc của bài này.
- **BANK 0,59 → 0,85** trong 3 năm trên pool 27 mã: chất lượng ngành ngân hàng cải thiện thật (ROE/NPL
  trong `bank_lens_v3`) hay lens trôi ngưỡng — bài này **không phân định được** và không nên đoán.

### E.4.6 Có bị ảnh hưởng bởi restate dữ liệu gần đây không?

**(a) Nhịp thay đổi rating — không có bất thường.** Số dòng thay đổi/tháng trong `fa_ratings_8l`:

| Tháng | 2025-07 | 2025-10 | 2026-01 | 2026-04 | 2026-07 |
|---|---|---|---|---|---|
| Số mã đổi rating | 986 | 1012 | 664 | 766 | **684** |

Đỉnh rơi đúng bốn mùa báo cáo (T1/T4/T7/T10). T7/2026 = 684, **thấp hơn** các mùa tương đương trước
đó — phù hợp với universe đã nhỏ đi, và **không** có dấu hiệu một đợt re-rate hàng loạt do restate.

**(b) NHƯNG có một thay đổi dữ liệu thật, nằm ở tầng bảng nguồn — cần báo data-ops.** Số dòng/phiên
của `tav2_bq.ticker`:

| Tháng | 2025-09 → 2026-05 | 2026-06 | 2026-07 |
|---|---|---|---|
| Trung bình mã/phiên | **~1.252–1.272** | 1.159 (min 838) | **823** (min 770, max 902) |

So 2026-05-15 với 2026-07-31: **401 mã biến mất**. Vì `rating_8l.py` đọc `ticker_1m` tại `MAX(time)`,
universe 8L hôm nay là **858 mã** thay vì ~1.100 như đầu năm.

**Đo mức độ ảnh hưởng thật (đây mới là phần quyết định):** trong 401 mã biến mất, tại 2026-05-15 —

- số mã có thanh khoản ≥ 3 tỷ/phiên (ngưỡng `LIQ_MIN` của screener): **0**
- số mã có thanh khoản ≥ 1 tỷ/phiên: **0**
- **thanh khoản CAO NHẤT trong cả 401 mã: 0,28 tỷ/phiên** (~11 lần dưới ngưỡng)
- không mã nào có `Trading_Value_1M_P50` NULL (nên đây không phải hiệu ứng thiếu dữ liệu)
- 39 mã có vốn hoá sổ sách ≥1.000 tỷ nhưng **không có thanh khoản** — dạng UPCOM gần như không giao dịch

⇒ **Toàn bộ phần mất nằm ở đuôi không giao dịch được.** Rổ screener (`rating≤3 ∧ liq≥3 tỷ`) qua các
mốc: 131 (2023-07) · 154 (2024-07) · 154 (2025-07) · 134 (2026-01) · **108 (2026-07)**. Phần giảm
gần đây đến từ **số mã đủ thanh khoản** giảm (231 → 186 từ T1 đến T7/2026) — tức điều kiện thị
trường/thanh khoản, **không** phải do 401 mã kia biến mất (chúng chưa bao giờ nằm trong 186/231).

*(Chênh 108 vs 104 ở §E.4.3: 108 là đếm bằng **rating PIT** as-of trong `fa_ratings_8l`; 104 là
screener do `rating_8l.main()` **tính lại tại chỗ** ở lần chạy A. Lệch 4 mã là do độ trễ giữa rating
đã publish và rating tính lại từ dữ liệu tươi nhất — bình thường, không phải sai lệch cần xử lý.)*

**Khuyến nghị:** báo Winston (data-ops) xác minh nguyên nhân co universe `ticker` từ T6/2026 và ghi
vào `kb/data_registry/`. **Không** phải sự cố với 8L rating, **không** chặn gì đang chạy — nhưng một
bảng nguồn mất 32% số dòng mà không ai ghi nhận thì lần sau sẽ có người đọc nhầm.

### E.4.7 Kết luận Việc 2

> **8L rating KHÔNG mắc lỗi méo-do-một-mã-vốn-hoá-lớn. Không cần sửa gì. Câu hỏi đóng lại.**
>
> Bằng chứng: (1) đường tính `rating` **không có** đầu vào cross-sectional nào — chứng minh bằng đọc
> code; (2) leave-one-out VIC trên chính pipeline production: **0/857 rating đổi, 0/104 zone đổi,
> max |Δpercentile| = 0,0000**; (3) chính VIC bị 8L chấm rating 4 và loại khỏi screener bằng số của
> nó; (4) cấu trúc rổ qua gate theo vốn hoá/ngành nằm trong khoảng lịch sử 2022–2026.
>
> **Không đề xuất thay đổi production nào ⇒ không cần quant-skeptic** (theo đúng ranh giới dispatch).

---

## E.5 Khuyến nghị vận hành (không có gì phải làm ngay)

1. **Value Radar giữ nguyên hiển thị-thuần cạnh DT5G.** Ranh giới display-only trong docstring
   `value_radar.py` giữ **nguyên văn**. Không nâng thành gate/tilt/sizing. Phụ lục E chỉ **củng cố**
   §C.5.4 và §D.7, không nới.
2. **Đóng hướng nghiên cứu "ghép DT5G × Radar thành tín hiệu định thời điểm".** Không mở thêm biến
   thể (ma trận 2 chiều state × band, ngưỡng động, v.v.). Điều kiện mở lại: **≥5 đợt washout mới**
   (~3–5 năm), và khi đó vẫn phải khai báo N_trials tích luỹ **≥110** + DSR + PBO + LOO theo năm.
3. **Hướng nghiên cứu định giá tiếp theo nên ở tầng cross-sectional**, nơi N đủ để kết luận dứt
   khoát. Bài này đã dùng đúng tầng đó và trả lời được câu hỏi VIC trong một buổi — trong khi cùng
   câu hỏi ở tầng chỉ số đã ngốn 110 phép thử mà không phân định nổi.
4. **Hai việc nhỏ tách ra khỏi phạm vi bài này** (ghi để không rơi, không tự làm):
   (a) báo Winston vụ `ticker` co từ ~1.255 → ~823 mã/phiên (§E.4.6b);
   (b) rà `power_lens` — route POWER hiện cho 48/48 mã qua gate ≤3, tức gate không lọc gì trong route
   đó (§E.4.5).

---

## E.6 Giới hạn của Phụ lục E

1. **Việc 2 là kiểm tra *một ngày*** (snapshot `ticker_1m` 2026-07-31). Kết luận cấu trúc (§E.4.2 —
   rating không có đầu vào cross-sectional) đúng ở mọi ngày vì đó là tính chất của code; nhưng con số
   "0/857 đổi" là đo trên **một** snapshot. Chưa chạy leave-one-out cho nhiều ngày lịch sử — hợp lý
   vì kết luận cấu trúc đã đủ mạnh, nhưng cần nói rõ.
2. **Không backtest.** Bài này không đo P&L của bất cứ điều gì. Mọi phát biểu về 8L (IC +0,125 v.v.)
   là **trích dẫn** kết quả đã pin trước đó (`kb/KNOWLEDGE.md`, `data/results_registry.md`), không
   phải đo lại ở đây.
3. **§E.4.5 chỉ mô tả, không kiểm định.** Các con số tỷ lệ qua gate theo ngũ phân vị/route là thống kê
   mô tả để tìm bất thường; **không** chạy phép thử nào trên chúng ⇒ **không cộng vào N_trials = 110**.
   Nếu sau này có ai muốn dùng chúng làm căn cứ cho một thay đổi, phải thiết kế phép thử riêng và khai
   báo trials của phép thử đó.
4. **Hai quan sát bỏ ngỏ có chủ đích** (POWER 100% qua gate; BANK 0,59→0,85): bài này **không** phân
   định được nguyên nhân và **không đoán**. Chúng là việc riêng, cần lens-audit, không phải kết luận
   của bài này.
5. **§E.2 lập luận về N là lập luận cấu trúc**, dựa trên đếm đợt regime (49 chuyển trạng thái DT5G,
   26 sự kiện CAPIT) — không phải một phép tính power chính thức. Nó đủ để biện minh cho quyết định
   *dừng*, không nên trích như một giới hạn định lượng chính xác.
6. **Kế thừa mọi giới hạn của A/B/C/D** khi trích dẫn lại số của chúng.

---

## E.7 Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source wc_env.sh
$DNA_PYEXE mike/agents/Taylor/exp_8l_capcheck/loo_megacap.py
```

Script tự cache đầu vào BQ (`exp_8l_capcheck/bq_cache.pkl`) để ba lần chạy dùng **đúng cùng** dữ
liệu; đặt `WORKDIR_8L` vào thư mục probe nên **không** ghi đè `data/rating_8l*.csv` của production.
Xoá `bq_cache.pkl` nếu muốn lấy lại dữ liệu tươi (kết quả sẽ theo snapshot mới, không tái lập
byte-identical bảng trên).

Đầu ra: `exp_8l_capcheck/run_{A_full,B_noVIC,C_noTop5}_{rating,screener}.csv` +
`log_{A_full,B_noVIC,C_noTop5}.txt` (diff A vs B = 2 dòng, §E.4.3).
Các truy vấn BQ của §E.4.5–E.4.6 chạy trực tiếp bằng `bq query` (as-of `fa_ratings_8l` +
`tav2_bq.ticker`), không sinh file trung gian.
Interpreter: `$DNA_PYEXE` (= `/home/trido/thanhdt/wc_venv/bin/python`).
