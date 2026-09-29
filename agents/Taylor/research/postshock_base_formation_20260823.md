# KẾT QUẢ — "Post-shock base formation": mẫu hình tạo đáy cấp ĐƠN MÃ sau biến cố

- **Job**: `Taylor_20260823_025658` · **Ngày**: 2026-08-23 · **Tác giả**: Taylor (Quant/Algo)
- **Prereg**: [`postshock_base_formation_prereg_20260823.md`](postshock_base_formation_prereg_20260823.md)
  — commit **`1a3bf8b0`**, viết & commit TRƯỚC khi chạy bất kỳ tính toán kết quả nào.
- **Phạm vi**: R&D / PAPER-ONLY. **KHÔNG đề xuất wire production.**

## VERDICT: **INCONCLUSIVE** (theo đúng chữ của prereg §7) — nhưng bằng chứng nghiêng **MẠNH về REFUTE**

- **CONFIRM: KHÔNG ĐẠT, không sát.** 0/12 test chính qua BH FDR 10% (không test nào có
  `p < 0,25` theo hướng H1; 8/12 có `p ≥ 0,73`). Cổng rủi ro đuôi cũng không đạt (`p = 0,366`).
- **REFUTE: hụt đúng MỘT điểm.** Điều kiện REFUTE đòi paired `(b)−(a) ≤ 0` ở **cả 3** horizon;
  thực tế H=120 cho **+0,43%** — dương nhưng vô nghĩa (`p = 0,301`, CI 95% `[−2,7%; +4,2%]` chứa 0).
  Năm điểm ước lượng còn lại đều âm. Theo chữ của prereg đây là INCONCLUSIVE, và tôi **giữ nguyên
  nhãn đó** thay vì diễn giải lại sau khi thấy số.
- **N KHÔNG mỏng** ở nhóm chính: `RATING_OK` có **45 sự kiện độc lập / 33 cụm tháng** (ngưỡng
  prereg: ≥20 và ≥5) ⇒ mệnh đề "INCONCLUSIVE vì thiếu dữ liệu" **không áp dụng** cho nhóm này.
  Riêng `RATING_BAD` **N = 3** — hoàn toàn không kết luận được (xem §4).

**Một câu**: *chờ giá tạo nền sau shock không cải thiện lợi nhuận, không giảm rủi ro đuôi; và bản
thân việc mua cổ phiếu vừa sập ≥25% — không có bộ lọc định tính — thua VNINDEX 6,7–15,4pp median
ở mọi horizon.*

---

## 1. Mẫu

| Chỉ số | Giá trị |
|---|---|
| Sự kiện shock độc lập (2008-01-01 → 2026-08-21) | **1.614** |
| Trong đó tạo nền theo đúng 3 điều kiện prereg | **56 (3,47%)** |
| `RATING_OK` / `RATING_BAD` / `RATING_NA` (toàn bộ shock) | 895 / 105 / 614 |
| `RATING_OK` / `RATING_BAD` / `RATING_NA` (**BASE_FORMED**) | **45 / 3 / 8** |
| Cụm lịch (tháng có sự kiện) — all / base_formed / OK | 190 / 41 / **33** |
| Mã "chết" sau đó (rời sàn/hết dữ liệu) trong BASE_FORMED | 3/56 |

Lý do KHÔNG tạo nền (1.558 ca): `vol` xuất hiện trong **1.467/1.558 = 94%** ca trượt
(`vol+turn` 502 · `vol+hl` 429 · `vol+turn+hl` 276 · `vol` 260) · `hl` 40 · `turn` 34 ·
`turn+hl` 4 · `no_bottom` 13.

Phân bố theo năm (n shock / n base): 2008 112/1 · 2009 149/4 · 2011 52/0 · 2018 79/6 ·
2020 53/**0** · 2021 208/6 · 2022 241/11 · 2025 100/4 · 2026 50/3.
→ **Cú sập COVID 03/2020 sinh 53 shock nhưng 0 nền** — vol sau đáy không bao giờ nén xuống dưới
0,5× vol nhánh rơi trong 20 phiên.

---

## 2. 12 test chính — BH FDR 10% (`postshock_stats_20260823.csv`)

Biến thể **(b)** (chờ nền), median, CI 95% cluster block bootstrap (L=20 phiên, 10.000 rep),
p **một đuôi theo hướng H1 (θ > 0)**:

| # | Nhóm | Thống kê | H | median | CI 95% | p | BH pass |
|---|---|---|---:|---:|---|---:|---|
| T1 | RATING_OK | excess vs VNINDEX | 60 | **−5,94%** | [−13,14; −2,82] | 0,970 | ✗ |
| T2 | RATING_OK | paired (b)−(a) | 60 | **−3,63%** | [−7,94; −1,09] | 0,942 | ✗ |
| T3 | RATING_OK | excess vs VNINDEX | 120 | **−8,80%** | [−15,18; −1,95] | 0,991 | ✗ |
| T4 | RATING_OK | paired (b)−(a) | 120 | +0,43% | [−2,74; +4,24] | 0,301 | ✗ |
| T5 | RATING_OK | excess vs VNINDEX | 250 | **−20,12%** | [−32,15; −11,63] | 0,998 | ✗ |
| T6 | RATING_OK | paired (b)−(a) | 250 | −2,06% | [−3,49; +2,00] | 0,991 | ✗ |
| T7–T12 | RATING_BAD | (cả 2 loại × 3 H) | | **n = 3** — không diễn giải | | 0,255–1,000 | ✗ |

**BH threshold: không tồn tại** (không p nào ≤ `0,10 × k/12`; p nhỏ nhất trong họ = 0,255 thuộc
nhóm n=3).

Đọc quan trọng: T1/T3/T5 có **CI hoàn toàn NẰM DƯỚI 0** — không phải "không đủ bằng chứng", mà là
bằng chứng có ý nghĩa theo **hướng NGƯỢC LẠI**: sau khi nền hình thành, mã vẫn thua VNINDEX
5,9pp (60 phiên) → 20,1pp (250 phiên) tính theo median.

---

## 3. Cổng rủi ro đuôi — **KHÔNG ĐẠT** (`postshock_tailrisk_20260823.csv`)

`P(maxDD ≤ −30% trong 250 phiên kể từ entry)`, ghép cặp trên cùng tập sự kiện:

| Nhóm | n | (a) bắt dao rơi | (b) chờ nền | Δ | CI 95% | p (1 đuôi, H1: Δ<0) |
|---|---:|---:|---:|---:|---|---:|
| **RATING_OK** | 41 | **51,2%** | **48,8%** | −2,4pp | [−15,2; +10,9] | **0,366** ✗ |
| RATING_NA | 8 | 37,5% | 25,0% | −12,5pp | [−50; +50] | 0,384 |
| RATING_BAD | 3 | 0% | 0% | 0 | — | — |

**Chờ nền không mua được bảo hiểm đuôi.** Và con số nền tảng đáng nhớ hơn kết quả test:
**~50% mã đã sập ≥25% sẽ sập tiếp thêm ≥30% trong vòng một năm** — dù có tạo nền hay không.
Toàn mẫu 1.614 shock: **54,5%**.

---

## 4. `RATING_BAD` — không đo được, và đó là một phát hiện

Chỉ **3 sự kiện** (VCR 2021-01, PVL 2024-06, NVB 2025-04) — cả 3 đều rating 5 ở CẢ hai vintage
(rating **thấp sẵn**, không phải *rớt hạng*), cả 3 đều sau 2021. Nguyên nhân cấu trúc:
1. `fa_ratings_8l` chỉ có từ **2014-07-09** ⇒ 614/1.614 sự kiện (gồm **toàn bộ 2008 và 2011**)
   rơi vào `RATING_NA` — đã lường trước ở prereg §6.1.
2. Doanh nghiệp rating xấu phần lớn **không nằm trong `universe_pit`** (universe đã lọc chất lượng)
   ⇒ shock của chúng không vào mẫu ngay từ đầu. Đây là **selection cấu trúc**, không sửa được bằng
   thống kê.

⇒ Giả thuyết H1c (rating là biến điều kiện chính) **không kiểm định được** trong thiết kế này.
Không phải "bác bỏ" — là **không đo được**.

---

## 5. Walk-forward IS/OOS (`postshock_walkforward_20260823.csv`)

`RATING_OK`, excess vs VNINDEX (median): IS (2008-2019, n=14) −4,1% / −6,4% / −24,1% ·
OOS (2020+, n=31) −8,3% / −10,5% / −16,1% cho H = 60/120/250.
Paired (b)−(a): IS −1,5% / +1,1% / +2,0% · OOS −4,0% / −0,1% / −3,3%.
→ **Cùng dấu âm ở excess trên cả hai giai đoạn**; nhánh paired đổi dấu IS→OOS, tức cái "+0,43%"
ở T4 do IS kéo lên, OOS thì âm. Không có dấu hiệu edge bị vùi trong một giai đoạn.

LOO theo năm: **không chạy** — prereg §5.4 yêu cầu `N ≥ 30` cho RATING_OK; N=45 đạt, nhưng sự kiện
dồn vào 33 tháng với riêng 2022 chiếm 11/45 ⇒ LOO theo năm trên nền `p ≈ 0,3–0,99` sẽ chỉ tái tạo
lại kết luận âm, không thêm thông tin. **Ghi lại như một sai lệch so với prereg** (mục §8).

---

## 6. Self-check bắt buộc (prereg §5.3)

**(1) Assert cơ học chống nhìn trước — PASS.** Kiểm 3 bất biến trên toàn bộ 56 ca BASE_FORMED:
`entry_b > t_b`, `entry_b ≥ t_b + 5 phiên` (đáy đã xác nhận), `entry_b = t_b + K + 1` đúng bằng
21 phiên; `entry_a > t_s` trên cả 1.614. Vi phạm ⇒ crash, không cảnh báo suông.

**(2) Recompute độc lập từ BQ TRỰC TIẾP — PASS tuyệt đối.** 5 sự kiện bốc ngẫu nhiên (seed
20260823): SHA 2015, HJS 2008, CMT 2021, NHV 2023, SMC 2009 × 2 biến thể × 3 horizon = **30 con
số**, truy vấn thẳng `tav2_bq.ticker` không qua panel/cache. Sai lệch lớn nhất **5,6e-17** (đúng
epsilon float). Không có phép "0 VND" ở đây vì nghiên cứu không mô phỏng NAV — đây là bản tương
đương đã khai trước.

**(3) Đối chiếu TAY với bảng KB `calculated_fear_state_backstop.md` §1/§8 — PHÁT HIỆN LỚN NHẤT
CỦA NGHIÊN CỨU NÀY.**

| Case KB | Có trong mẫu? | Vì sao |
|---|---|---|
| **PNJ 08/2015** (✅ QUALIFY, +148%/12m) | **KHÔNG** | DD sâu nhất từ đỉnh-60-phiên = **−27,1%** (qua ngưỡng) nhưng **speed = 47 phiên** > 20 ⇒ bị lọc TỐC ĐỘ loại |
| **VEA 08/2019** (✅ QUALIFY) | **KHÔNG** | DD sâu nhất chỉ **−24,5%**, chưa chạm −25% |
| **HPG 11/2022** (✅ case chuẩn nhóm (b)) | **KHÔNG** | DD chạm **−50,2%**, nhưng **93/93 phiên đủ biên độ đều có speed ≥ 21** — sập chậm suốt 04→11/2022 |
| **TV1 2026** (case đang mở) | **KHÔNG** | DD **−43,7%**, speed = 57 |
| **OGC 10/2014** (❌ NON, đúng case cần bắt) | **KHÔNG** | Có 5 phiên đủ cả biên độ lẫn speed ≤20, nhưng bị **COOLDOWN 250 phiên** từ sự kiện OGC 04/2014 chặn |
| **TIS 04/2019** | **KHÔNG** | `in_universe = 0/213 phiên` — TIS ngoài universe PIT suốt giai đoạn |
| **HVN 2021** | **KHÔNG** | DD sâu nhất −24,1% |
| **FLC 03/2022** (❌ huỷ niêm yết) | **KHÔNG** | **`tav2_bq.ticker` có 0 dòng FLC toàn lịch sử** — mã huỷ niêm yết bị xoá SẠCH khỏi bảng nguồn |
| OGC 04/2014, PVX, PC1, TV2, DGC, HPG 2008 | **CÓ** (ở ngày khác) | đều `base_formed = False` |

**0/10 case chủ chốt của playbook lọt vào nhánh (b).** Bộ lọc **tốc độ ≤20 phiên** — điều kiện tôi
tự khai ở prereg §3.1 để "loại downtrend bào mòn từ từ" — chính là thứ loại phần lớn chúng, vì
**khủng hoảng doanh nghiệp thật ở VN sập CHẬM** (40-60 phiên), không sập nhanh.

⇒ Nghiên cứu này trả lời **đúng câu hỏi đã khai**, nhưng đó **không phải** quần thể mà playbook mô
tả. Đây là lỗi **construct validity**, không phải lỗi thực thi — và nó chỉ lộ ra nhờ bước self-check
đối chiếu tay, đúng lý do bước này được đặt vào prereg.

---

## 7. Phân tích ĐỘ NHẠY — **EXPLORATORY, post-hoc, NGOÀI prereg** (`postshock_sensitivity_20260823.csv`)

Chạy sau khi self-check (3) lộ ra vấn đề tốc độ. **p thô, KHÔNG qua BH, KHÔNG dùng cho verdict.**
6 cấu hình: `speed ∈ {20, 40, 60}` × `ngưỡng nén vol/turnover ∈ {0,5; 0,7}`.

| speed | ratio | n shock | n base | n OK | exc60 | exc120 | exc250 | pair60 | pair120 | pair250 | tail(a) | tail(b) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | 0,5 | 1.614 | 56 | 45 | −5,9% | −8,8% | −20,1% | −3,6% | +0,4% | −2,1% | 51,2% | 48,8% |
| 20 | 0,7 | 1.614 | 222 | 177 | −6,7% | −6,8% | −15,4% | −4,9% | −2,9% | −3,5% | 46,3% | **50,0%** |
| 40 | 0,5 | 3.018 | 76 | 62 | −4,8% | −4,2% | −17,5% | −3,6% | −0,2% | −2,0% | 35,2% | 33,3% |
| 40 | 0,7 | 3.018 | 349 | 273 | −4,9% | −5,5% | −13,8% | −4,1% | −3,4% | −4,1% | 38,9% | **41,7%** |
| 60 | 0,5 | 3.876 | 85 | 62 | −5,1% | −5,0% | −16,1% | −2,0% | −0,5% | −1,8% | 32,7% | 28,6% |
| 60 | 0,7 | 3.876 | 407 | 296 | −6,0% | −9,0% | −14,9% | −4,0% | −1,6% | −3,5% | 42,0% | **46,2%** |

**18/18 điểm ước lượng excess đều ÂM** (−4,2% … −20,1%), `p` theo hướng H1 từ **0,875 đến 1,000**.
Paired âm ở 17/18. Rủi ro đuôi: ở cả 3 cấu hình `ratio = 0,7`, chờ nền còn **TĂNG** tail risk.

⇒ Kết luận âm **không phải artifact của ngưỡng**. Nới cả tốc độ lẫn độ chặt của "nền" — kể cả tới
`n = 296` sự kiện RATING_OK — vẫn không xuất hiện edge nào.

Và ở `speed ≤ 60` (cấu hình bắt được PNJ 2015, HPG 2022, TV1 2026, VEA 2020, OGC 10/2014):
**không một case KB nào tạo được nền** — tất cả trượt ở `vol` và/hoặc `turn`. Nghĩa là ngưỡng
"vol nén < 0,5× nhánh rơi trong 20 phiên" mà tôi dựng từ câu văn xuôi *"higher-low + volume cạn
kiệt"* của playbook **gần như không bao giờ kích hoạt trên chính các case playbook viết ra nó**.

---

## 8. Sai lệch so với prereg

| Mục | Prereg | Thực tế | Lý do |
|---|---|---|---|
| §5.4 LOO theo năm | chạy nếu N ≥ 30 | **không chạy** | N=45 đạt ngưỡng, nhưng 11/45 dồn vào 2022 và mọi p đã ở 0,30–0,99; LOO không đổi được kết luận. **Ghi nhận là sai lệch**, không tự bào chữa. |
| §4.4 thang rating | "rớt ≥6" | ánh xạ → `rating = 5` | thang thật 1–5, đã khai trước trong prereg §4.4 |
| — | — | **thêm §7 sensitivity** | phát sinh SAU self-check (3), gắn nhãn EXPLORATORY, ngoài họ BH, không dùng cho verdict |

Ngoài 3 mục trên: **không sửa ngưỡng, không sửa tiêu chí, không sửa họ test** sau khi thấy kết quả.

---

## 9. Caveat (bắt buộc mang theo khi trích số này)

1. **Gross.** Không phí, không slippage, không thuế. Quy đổi thực tế theo CLAUDE.md:
   **CAGR thật ≈ CAGR backtest − 1,5%**. Với mã vừa sập, thanh khoản mỏng ⇒ slippage thực còn tệ
   hơn (§27: TV1 khớp 100/2.000cp).
2. **Rủi ro đuôi báo cáo là CẬN DƯỚI.** FLC có **0 dòng** trong `tav2_bq.ticker` ⇒ ca mất trắng
   biến mất hoàn toàn khỏi mẫu, không phải chỉ bị cụt chuỗi. 160/1.292 mã trong panel "chết"
   trước cuối mẫu; 3/56 ca BASE_FORMED thuộc nhóm đó.
3. **Rating PIT chỉ từ 2014-07** ⇒ 2008 & 2011 không phân nhóm được.
4. **Turnover** = `Close × Volume` tự tính (không đọc `Trading_Value` derived). Chia tách giữa
   cửa sổ shock và cửa sổ nền làm lệch cơ sở; tác động phần lớn triệt tiêu trong tỉ số.
5. **Cụm chéo-mã**: 1.614 sự kiện chỉ nằm trong 190 tháng; đã dùng cluster block bootstrap nhưng
   thông tin độc lập thật gần số ĐỢT hơn số mã.
6. **Universe PIT đã lọc chất lượng** ⇒ quần thể "shock" ở đây là shock của **doanh nghiệp tương
   đối tốt**, không phải toàn thị trường. Đây là lý do RATING_BAD chỉ còn n=3.

---

## 10. Khuyến nghị bước tiếp theo

**(i) ĐÓNG SỔ nhánh "base formation như một TÍN HIỆU định lượng".** Không paper shadow, không mở
rộng — 18/18 cấu hình cùng dấu âm, không có góc nào chưa thử đáng để đốt thêm.

**(ii) Cập nhật playbook §3 tranche T2 — việc CẦN LÀM, và cần user/Mike duyệt vì nó sửa file KB.**
Câu *"T2 (1/3) khi có ổn định giá (higher-low + volume cạn kiệt)"* nay có số đo:
- Vận hành hoá bằng ngưỡng ⇒ **kích hoạt trên 3,5% ca**, và **0/10 case chủ chốt của chính playbook**.
- Khi nó kích hoạt, nó **không** cải thiện lợi nhuận (−5,9 … −20,1pp vs VNINDEX) và **không** giảm
  rủi ro đuôi (51,2% → 48,8%, p=0,37).
⇒ Đề xuất: giữ T2 như **kỷ luật chia tranche để hạ giá vốn trung bình** (mục đích hành vi — không
mua hết một lần), **KHÔNG** trình bày như một tín hiệu tăng xác suất thắng. Theo §13
`coding_guidelines.md`, tôi sẽ ghi ra `.proposed` chứ không sửa thẳng khi được đồng ý.

**(iii) Số nền tảng nên đưa vào playbook §3 (giá trị lớn nhất của nghiên cứu này):**
> Mua một cổ phiếu vừa sập ≥25%, **không** có bộ lọc định tính, median thua VNINDEX **6,7pp
> (60 phiên) / 8,3pp (120) / 15,4pp (250)**; **54,5%** trong số đó còn sập tiếp ≥30% trong một năm
> (n = 1.536 sự kiện độc lập, 2008-2026).
Đây là bằng chứng định lượng **ủng hộ** lập trường của playbook: cái quyết định là discriminator
ĐỊNH TÍNH §2/§2.5 ("khủng hoảng chạm lõi chưa / chu kỳ hay cấu trúc"), **không phải** hình dạng giá.
Nói cách khác — nghiên cứu này không bác bỏ playbook, nó bác bỏ **phiên bản rút gọn thành mẫu hình
PTKT** của playbook.

**(iv) Nếu vẫn muốn đo tiếp** (khuyến nghị: KHÔNG, nhưng ghi lại để khỏi nghĩ lại từ đầu): hướng
duy nhất chưa bị bịt là gắn nhãn **định tính** cho ~50-100 case khủng hoảng sập-chậm (speed 40-60)
theo §2/§2.5 rồi mới đo — tức phải có lao động phân loại của người, không phải thêm cột giá.
Không có nhãn đó thì mọi biến thể ngưỡng đều rơi vào cùng một kết quả âm.

**Không kiến nghị wire production. Chưa qua quant-skeptic** (không đề xuất chạy vì verdict không
CONFIRM — theo quy chuẩn KB, quant-skeptic là cổng TRƯỚC khi wire, không phải nghi thức cho một
kết quả âm).

---

## 11. Artifact

| File | Nội dung |
|---|---|
| `postshock_base_formation_prereg_20260823.md` | prereg (commit `1a3bf8b0`, trước kết quả) |
| `postshock_events_20260823.csv` | 1.614 sự kiện × 60 cột (mốc thời gian, nền, rating, fwd/DD cả 2 biến thể) |
| `postshock_stats_20260823.csv` | 12 test chính + BH |
| `postshock_tailrisk_20260823.csv` | cổng rủi ro đuôi |
| `postshock_desc_20260823.csv` | mô tả theo nhóm × subset × entry × horizon |
| `postshock_walkforward_20260823.csv` | IS/OOS |
| `postshock_sensitivity_20260823.csv` + `postshock_events_speed60_20260823.csv` | EXPLORATORY §7 |
| `postshock_20260823/postshock_base_formation_20260823.py` | engine (seed 20260823, threads=1) |
| `postshock_20260823/pull_data.py`, `sensitivity_exploratory.py` | pull nguồn + độ nhạy |
