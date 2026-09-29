# JOB E — Quy ước trục-2 breadth-tercile PIT (08-22) có ĐỨNG VỮNG không?

> Job `Taylor_20260927_022338` · 2026-09-27 · Taylor · **PAPER-ONLY, không wire gì**
> Prereg: `PREREG.md` (viết TRƯỚC khi chạy) · Scripts: `step2_repro_0822.py`, `step3_ic_long.py`
> Artifacts: `step2.log`, `step2_panel_labelled.csv`, `step3.log`, `step3_daily_ic.csv`,
> `step3_verdict_long.csv`, `step3_verdict_intersect.csv`, `step3_loo.csv`

## KẾT LUẬN — **A. Quy ước 08-22 ĐỨNG VỮNG** (nhưng vì lý do khác cái H5 đã đo)

| Câu hỏi prereg | Trả lời |
|---|---|
| **(1)** Trên panel/cửa sổ GỐC, breadth-tercile có còn tách IC? | **Câu hỏi không áp được: 08-22 CHƯA BAO GIỜ đo IC.** Nó đo (a) cấu trúc mẫu và (b) excess CAGR theo ô — và tự kết luận **0/27 ô qua BH FDR 10%**. Tái lập số gốc: **khớp CHÍNH XÁC** (§2). |
| **(2)** Trượt ở H5 là do cửa sổ ngắn hay trục yếu? | **TRỤC YẾU, không phải cửa sổ.** Trên 12,6 năm (IS **72** tháng / OOS **80** tháng, gấp ~1,6× H5), breadth **vẫn** đảo dấu `ic_mom` IS +0,0569 → OOS −0,0382 và `ic_ey` vẫn sụp IS −0,0822 (p_BH **0,0030**) → OOS +0,0032 (p 0,886). H5 tái lập y nguyên (§3). |
| **(3)** Ô nào tách IC bền qua IS/OOS? | **KHÔNG ô nào. 0/12 so sánh** qua bộ 3+BH — breadth 0/4, retail 0/4, DT5G 0/4 (§4). |
| **(4)** Phán | **A — quy ước ĐỨNG**: cả 3 điều kiện prereg §5 đạt. Bằng chứng yếu nằm ở **cách quy ước được VIẾT**, không ở quyết định (§5). |

**Một câu:** H5 đo breadth bằng một tiêu chí (IC-separation) mà quyết định 08-22 chưa bao giờ tuyên
bố đạt — và **08-22 đã tự nói là không có tín hiệu**. Phát hiện phụ của H5 là **ĐÚNG và tái lập
được trên cửa sổ dài gấp 1,6×**, nhưng nó xác nhận lại kết luận 08-22 chứ không phủ định nó. Quy
ước đứng vì chỗ dựa của nó — **cấu trúc mẫu** — tái lập chính xác, và vì **không trục nào khác qua
được cùng chuẩn**.

---

## 1. Bước 1 — 08-22 dựa trên tiêu chí NÀO? (kiểm tài liệu TRƯỚC khi đo)

H1a và H1b của prereg **đều XÁC NHẬN**, bằng trích dẫn nguyên văn
`breadth_vs_radar_matrix_20260822.md`:

| Prereg | Trích nguyên văn báo cáo gốc |
|---|---|
| **H1a** — chọn breadth vì CẤU TRÚC MẪU | §7: *"CÓ đề xuất một thay đổi quy trình, chi phí bằng 0: mọi phân tích conditional […] từ nay dùng breadth-tercile PIT thay Value Radar zone làm trục 2 mặc định"* — lý do đưa ra là §6.1 *"n_effective có cao hơn radar không? — CÓ, gấp 2,0×"* |
| **H1b** — 08-22 tự kết luận KHÔNG có tín hiệu | Tiêu đề §6.2: *"Có ô nào qua BH FDR 10% không? — **KHÔNG. 0/27**, y như radar 0/24"* · §6.3: *"Tốt hơn để MÔ TẢ, không phải để wire"* · §7: *"**KHÔNG wire.**"* |

Thêm một điểm prereg không lường trước, đọc ra khi tái lập:

> **Quy ước đã codify là biến thể mà 08-22 TỰ TAY phá tính đơn điệu.** `context_pack.md` mục
> "Quy ước phân tích conditional" ghi *"Phân loại phiên t: dùng `breadth_{t-1}`"* — tức biến thể
> **trễ nhãn 1 phiên**, đúng cái §5a của báo cáo gốc dùng để *phá* kết quả §4: *"Tính đơn điệu biến
> mất (LOW +24,9 > HIGH +17,4 > MID +8,4)"*. Nói cách khác: **quy ước được duyệt trong khi đã biết
> tín hiệu bề mặt không còn.** Đây là bằng chứng mạnh nhất cho kết luận A — không có kỳ vọng
> "tách được" nào bị vỡ, vì chưa bao giờ có kỳ vọng đó.

⇒ Bộ 4 tiêu chí H5 áp lên breadth là **một tiêu chí mới**, không phải tiêu chí 08-22 trượt.

## 2. Bước 2 — Tái lập số GỐC 08-22: **KHỚP**

Nguồn gốc còn nguyên (`strategy_regime_matrix_20260822/{b2_breadth.csv, panel_daily.csv}`);
script gốc `b2.py` không còn ⇒ **tái lập độc lập theo mô tả trong báo cáo**, không chạy lại code cũ.
Panel: 3.106 phiên 2014-01-03→2026-06-19 (báo cáo gốc nói 3.107 — lệch 1 dòng).

| Khối | Số gốc | Tái lập | Tolerance prereg | Phán |
|---|---|---|---|---|
| Phân bố tercile | LOW **1.232** / MID **897** / HIGH 978 | LOW **1.232** / MID **897** / HIGH 977 | khớp chính xác | ✅ (HIGH lệch 1 = đúng 1 dòng panel) |
| n_effective breadth | 262 episode, 13 ô, năm/ô median 6 | **262**, **13**, **6** | chính xác | ✅ |
| n_effective radar | 131 episode, 14 ô | **131**, **14** | chính xác | ✅ |
| Confound kỷ nguyên | breadth **0%** / share trội 57%; radar **54%** / 84% | **0% / 57%**; **54% / 84%** | chính xác | ✅ |
| Marginal excess (§4) | LOW +27,1 / MID +10,8 / HIGH +5,4 pp | **+27,4 / +11,0 / +5,5** | ±0,5pp | ✅ |
| LOO theo năm, ô LOW | +23,4…+31,9pp, 13/13 không đảo dấu | **+23,4…+31,5pp**, 13/13 không đảo | — | ✅ |
| §5a trễ nhãn 1 phiên | LOW +24,9 / MID +8,4 / HIGH +17,4; đơn điệu MẤT | **+26,3 / +8,1 / +16,6**; đơn điệu MẤT | ±1,0pp | ✅ (LOW +1,4pp) |
| §5b khử beta | alpha LOW +16,3 < MID +20,2 < HIGH +28,1 (ĐẢO) | **+16,5 < +20,5 < +28,4** (ĐẢO) | ±1,0pp | ✅ |
| Self-check look-ahead | corr(pct252_t, r_vni_t) = **+0,1088** | **+0,1088** | — | ✅ khớp 4 chữ số |

**⇒ Tiêu chí mà quyết định 08-22 thật sự dựa vào — cấu trúc mẫu — tái lập CHÍNH XÁC.**

Hai chỗ lệch ngoài tolerance, báo trung thực: **tách IS/OOS** của ô MID (+10,7/+11,1 vs gốc
+7,9/+8,5) và ô HIGH OOS (+12,9 vs gốc +6,9). Số toàn-cửa-sổ khớp trong ±0,3pp nên đây là lệch ở
mốc chia kỳ hoặc ở 12 phiên cuối panel, **không** ảnh hưởng kết luận (kết luận 08-22 không treo
vào IS/OOS split của một ô).

### 2b. Hai bẫy tái lập phát hiện được — cả hai đáng ghi lại

1. **Quy ước TIE của phân vị không được ghi ở đâu.** Đo 5 quy ước hợp lý; chỉ
   **`(# trong 252 phiên trước < breadth_t) / 253`** trả đúng LOW 1.232 / MID 897:

   | quy ước | LOW | MID | HIGH |
   |---|---:|---:|---:|
   | `<` /252 | 1.226 | 890 | 990 |
   | `<=` /252 | 1.224 | 890 | 992 |
   | midrank /252 | 1.225 | 891 | 990 |
   | **`<` /253** | **1.232** | **897** | 977 |
   | rank gồm t /253 | 1.226 | 890 | 990 |

2. **`pd.cut([0,1/3,2/3,1])` ném mất `pct==0,0`** — đúng 63 phiên breadth thấp nhất lịch sử, tức
   những phiên VNI xấu nhất. Bỏ chúng làm excess ô LOW tụt từ **+27,4pp xuống +14,7pp** và LOO ô
   LOW từ +23,4…+31,5 xuống +7,5…+21,0. Đây là lỗi của chính tôi ở lần chạy đầu, bắt được vì
   KHỐI 1 không khớp số gốc — lý do để giữ số gốc làm mốc kiểm, không chỉ "trông hợp lý".

## 3. Bước 3 — Cửa sổ ngắn hay trục yếu? **TRỤC YẾU**

Cùng phương pháp `h5_ic.py` (công thức không đổi), chỉ nới cửa sổ: **2014-01-02 → 2026-08-26**,
3.155 phiên, **12,6 năm** (H5: 10,4 năm). Panel 1.156.084 dòng, 772 mã, chỉ thành viên
`universe_pit` PIT. IS **2014-01→2019-12 (72 tháng)** / OOS **2020-01→2026-08 (80 tháng)**.

**N thật mỗi ô (tháng độc lập)** — và đây là điểm phải sửa lại cách đặt vấn đề của dispatch:

| | LOW | MID | HIGH |
|---|---:|---:|---:|
| breadth IS (job E, 12,6 năm) | 41 | 38 | 36 |
| breadth OOS (job E) | 43 | 44 | 34 |
| breadth IS (H5, 10,4 năm) | 19 | 22 | 27 |
| breadth OOS (H5) | 42 | 44 | 34 |

> ⚠️ **Đính chính framing:** "N thật ~4-11 tháng/ô" trong dispatch là N của trục **retail**, không
> phải breadth. Warm-up 24 **tháng** thuộc phân vị rolling của retail; breadth dùng rolling **252
> phiên** ⇒ chỉ mất ~1 năm. Breadth ở H5 đã có 19-27 tháng IS / 34-44 tháng OOS. Job E nâng IS lên
> 36-41 tháng. **Cửa sổ ngắn chưa bao giờ là lời giải thích khả dĩ cho việc breadth trượt** — và
> cửa sổ dài xác nhận điều đó.

### Breadth trên cửa sổ dài — hỏng ĐÚNG CÙNG MỘT KIỂU

| | LOW | MID | HIGH | HIGH−LOW | CI95 | p_boot | p_BH | đơn điệu |
|---|---:|---:|---:|---:|---|---:|---:|---|
| **IS** `ic_mom` | 0,0412 | 0,0922 | 0,0981 | **+0,0569** | [−0,016, +0,130] | 0,132 | 0,197 | ✔ |
| **OOS** `ic_mom` | 0,0056 | 0,0268 | −0,0325 | **−0,0382** | [−0,117, +0,046] | 0,359 | 0,538 | ✘ |
| **IS** `ic_ey` | 0,0540 | 0,0044 | −0,0282 | **−0,0822** | [−0,130, **−0,035**] | 0,0005 | **0,0030** | ✔ |
| **OOS** `ic_ey` | 0,0634 | 0,0856 | 0,0665 | **+0,0032** | [−0,044, +0,050] | 0,886 | 0,886 | ✘ |

- `ic_mom`: **đảo dấu IS→OOS**, giống H5 (+0,037→−0,039). LOO theo năm: −0,0097…+0,0413, **có đảo dấu**.
- `ic_ey`: ô duy nhất trong CẢ 12 so sánh qua được BH (**p_BH 0,0030**, CI loại 0, đơn điệu) — và
  nó **chết sạch OOS** (p 0,886, dấu đảo). Đây là hình mẫu sách vở của **artifact IS**, giờ đo
  trên 72 tháng IS thay vì 45, nên không thể quy cho N.

## 4. Bước 4 — Ba trục cùng khuôn: **0/12**

12 so sánh (3 trục × 2 nhân tố × 2 kỳ), BH trong từng kỳ trên 6. **Không so sánh nào đạt cả 4
tiêu chí** (cùng dấu IS&OOS · CI OOS loại 0 · đơn điệu cả 2 kỳ · p_BH OOS < 0,10):

| trục | nhân tố | HI−LO IS | HI−LO OOS | cùng dấu | CI OOS loại 0 | đơn điệu IS/OOS | p_BH OOS | đạt |
|---|---|---:|---:|---|---|---|---:|---|
| breadth | mom | +0,0569 | −0,0382 | ✘ | ✘ | ✔/✘ | 0,538 | ✘ |
| breadth | ey | −0,0822 | +0,0032 | ✘ | ✘ | ✔/✘ | 0,886 | ✘ |
| retail | mom | +0,1155 | +0,0713 | **✔** | ✘ | ✘/✔ | 0,429 | ✘ |
| retail | ey | −0,0985 | −0,0243 | **✔** | ✘ | ✔/✔ | 0,538 | ✘ |
| dt5g | mom | −0,0084 | +0,0611 | ✘ | ✘ | ✘/✘ | 0,528 | ✘ |
| dt5g | ey | +0,0451 | −0,0169 | ✘ | ✘ | ✘/✘ | 0,584 | ✘ |

Bảng cửa sổ GIAO 2016-04→2026-08 (robustness, **không phải trial mới**): kết luận không đổi, 0/12
(`step3_verdict_intersect.csv`). Breadth IS `ic_ey` vẫn qua BH (0,0090) rồi vẫn chết OOS.

**Xếp hạng — chỉ để trả lời câu hỏi 3, KHÔNG phải để đề xuất thay trục:**
- **retail** là trục duy nhất giữ **cùng dấu IS&OOS ở cả 2 nhân tố**. Phát hiện phụ của H5 ("retail
  phân tách tốt hơn trục mặc định") **tái lập trên cửa sổ dài**. Nhưng: IS chỉ **9/7/5 tháng**
  (5 episode), OOS CI chứa 0 cả 2 nhân tố, và **nguồn chết 28/09/2026 không có nối tiếp** ⇒
  **không phải ứng viên**, đúng như prereg cấm đề xuất.
- **breadth** là trục duy nhất có một ô qua BH ở IS — và đó là điểm TRỪ, không phải điểm cộng
  (artifact IS chết OOS).
- **dt5g** yếu nhất: đảo dấu cả 2 nhân tố, không ô nào đơn điệu.

⚠️ **Caveat riêng cho DT5G, làm nhẹ kết luận "DT5G đảo dấu":** giỏ HI **không cùng một thứ** giữa
2 kỳ — IS **không có phiên EXBULL nào** (BULL 70 phiên/6 tháng), OOS có EXBULL 60 phiên. Đảo dấu
của DT5G một phần là đổi thành phần giỏ, không thuần là bất ổn. Không dùng số DT5G ở đây để kết
luận gì về DT5G như một cổng rủi ro — **DT5G là chốt rủi ro fail-safe, không phải bộ điều kiện IC**,
và job này không kiểm nó ở đúng vai trò của nó.

## 5. Bằng chứng YẾU ở đâu (câu hỏi dispatch) — 4 điểm, đều về CÁCH VIẾT chứ không về quyết định

1. **Câu quy ước rộng hơn bằng chứng đỡ nó.** `context_pack.md` viết *"trục 2 mặc định cho **mọi**
   phân tích conditional"* và liệt kê 2 lý do, cả 2 đều thuần cấu trúc mẫu. Nó **không** mang theo
   kết luận §6.2/§7 của chính báo cáo gốc (*0/27 ô, "không phải để wire"*). Người đọc "trục mặc
   định" rất dễ suy ra "trục này tách được cái gì đó" — H5 đã đọc đúng như vậy. **Đây chính là chỗ
   yếu thật, và nó sửa được bằng một dòng văn bản, không cần đổi trục.**
2. **Hai chuỗi nhãn khác nhau cùng tên "breadth-tercile PIT".** 08-22 §4 dùng breadth **cùng phiên**
   (look-ahead corr **+0,109**, chính báo cáo thừa nhận); quy ước codify dùng **trễ 1 phiên**.
   Chúng cho số khác nhau đáng kể — ô HIGH excess **+5,5pp vs +16,6pp**, và **thứ tự tercile đảo**.
   Ai "tái lập số 08-22" có thể rơi vào biến thể nào cũng được.
3. **Bẫy cache mới, chưa có trong registry:** `data/bq_cache/ticker` có **`MA200 = NULL` cho phần
   lớn mã giai đoạn 2015-2017** (median 137 mã/ngày năm 2016; 2016-07-13: **199/296**). Tính breadth
   từ cache mà không lọc `MA200 IS NOT NULL` cho breadth **0,243 thay vì 0,730** cùng ngày
   (max|Δ| **0,487**, corr 0,934). Lọc đúng → **corr 0,999954, mean|Δ| 0,000585**. Self-check #1 của
   prereg là thứ duy nhất bắt được; **nếu prereg không bắt buộc nó, toàn bộ Bước 3 đã sai mà vẫn
   trông hợp lý.**
4. **Quy ước tie `/253` không ghi ở đâu** (§2b) — 5 quy ước hợp lý cho LOW 1.224…1.232.

**Không điểm nào trong 4 điểm trên làm quyết định 08-22 sai.** Chúng làm nó **khó tái lập** và
**dễ bị đọc quá nghĩa**.

## 6. Khuyến nghị — không đổi trục, chỉ đóng khoảng cách văn bản

1. **KHÔNG đổi quy ước trục-2.** Không có trục thay thế qua cùng chuẩn (0/12); retail trội hơn ở
   một tiêu chí nhưng N nhỏ và nguồn chết 28/09/2026.
2. **Sửa 1 dòng trong `context_pack.md`** (§13: ghi ra `.proposed`, cần Mike duyệt): thêm ranh giới
   hiệu lực mà báo cáo gốc đã có nhưng quy ước bỏ mất — đại ý *"chọn vì CẤU TRÚC MẪU (hết confound
   kỷ nguyên, n_eff 2,0×). KHÔNG có bằng chứng trục này tách lợi suất hay IC: 08-22 = 0/27 ô qua BH;
   job E 2026-09-27 = 0/4 trên 12,6 năm. Dùng để MÔ TẢ/phân tầng, không suy ra tín hiệu từ nhãn ô."*
   Kèm định nghĩa chính xác (nhãn `breadth_{t-1}`, phân vị rolling 252, tie `/253`).
3. **Thêm entry `kb/data_registry/`** cho bẫy `MA200 NULL 2015-2017` trong `bq_cache/ticker`
   (§9 + §3 điểm trên) — bẫy này đụng bất kỳ ai tính breadth/%>MA200 từ cache.
4. **Đóng phát hiện phụ của H5**: ĐÚNG, tái lập được, và **không** là lý do đổi quy ước. Nó là
   bằng chứng bổ sung cho chính kết luận 08-22 ("không có tín hiệu để wire"), đo bằng một thước
   khác (IC thay vì excess CAGR) trên cửa sổ dài hơn.
5. **Câu hỏi mở đáng theo** (nguyên văn từ §7 báo cáo gốc, vẫn chưa ai làm): *"alpha sau khử beta có
   phụ thuộc breadth không"* — §5b gợi ý HIGH > MID > LOW, ngược trực giác, **chưa hề được kiểm
   định**. Job E tái lập được gợi ý đó (+16,5 < +20,5 < +28,4) nhưng **không** kiểm định nó. Đó là
   một prereg RIÊNG.

## 7. N thật & khai trial

- **N quyết định = số tháng độc lập mỗi ô**: breadth IS 41/38/36, OOS 43/44/34 · retail IS 9/7/5,
  OOS 33/26 · DT5G IS 14/7/62/6 (không có EXBULL), OOS 18/15/47/25/5.
  **KHÔNG** phải 3.155 phiên, **KHÔNG** phải 1,16 triệu dòng panel.
- **Cảnh báo chồng lấn (khai trong prereg §4):** một tháng lịch có thể góp ngày cho >1 tercile ⇒
  các ô **không rời nhau theo tháng**; bootstrap khối HIGH−LOW thừa hưởng sự chồng lấn đó. Vì vậy
  cũng báo `n_episode` (đoạn nhãn liên tục): breadth IS 30/59/30, OOS 26/52/27.
- **Trial khai TRƯỚC: 12** (3 trục × 2 nhân tố × 2 kỳ). BH trong mỗi kỳ trên 6. Bảng cửa sổ giao là
  **cùng 12 test đo lại**, báo riêng, không gộp BH.
- Bootstrap khối theo **THÁNG**, B=4.000, `p_boot` hai phía, sàn 1/4.000.
- **Không test HƯỚNG** của bất kỳ trục nào (ecology-as-direction REFUTED 2026-07-13).
- Không dùng `profit_*`; không `IN (SELECT DISTINCT ticker FROM ticker_prune)` (§9b) — panel join
  `universe_pit` PIT theo `(time, ticker)`.
