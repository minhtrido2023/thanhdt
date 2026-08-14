# Bảo vệ tin xấu — mở rộng từ rổ ngân hàng ra TOÀN BỘ portfolio

> Taylor (Quant/Algo), job `Taylor_20260814_034642`, 2026-08-14. **PAPER-ONLY — chưa wire cron/code.**
> Nối tiếp `bank_tailrisk_insurance_design_20260814.md` (Tầng 0/1/2, rổ 13 mã ngân hàng).
> Yêu cầu user (John): (1) watchlist tự đồng bộ theo vị thế thật, (2) phủ khoảng trống tin cuối
> tuần trước phiên thứ Hai, (3) tránh case DGC/PNJ tái diễn.

---

## 0. Kết luận một câu

**Phần lớn thứ user muốn ĐÃ TỒN TẠI và đang chạy hằng ngày** — `anomaly_scan.py` đã lấy watchlist
tự động từ vị thế sống của cả 2 account, đã chạy 08:20 T2-T6, và replay lịch sử cho thấy nó bắt
PNJ đúng phiên sàn ĐẦU TIÊN (03/07) và DGC đúng ngày khởi tố (17/03). Cái thật sự còn thiếu chỉ có
**ba lỗ hổng nhỏ, cụ thể, rẻ**: (a) không có cổng độ tươi cho nguồn watchlist (cron nguồn mới cài
hôm qua, chưa có ai kiểm nó còn sống); (b) kênh TIN chỉ quét **1 lần/tuần vào thứ Sáu** trong khi
kênh GIÁ quét hằng ngày — tin nổ thứ Hai-thứ Năm phải chờ tới 4 ngày; (c) khoảng trống cuối tuần
là **THẬT và đo được** (thứ Hai tập trung 1,409× tỉ lệ sập riêng lẻ, p=2,1e-37, và lệch này **bất
đối xứng** — chiều tăng chỉ 1,115×; số đã cập nhật theo bản chạy ổn định §C.2, và là số TOÀN
mẫu — hiệu ứng tập trung sau 2020, xem §F.9). Đề xuất: **không xây cơ chế mới nào**, chỉ vá 3 chỗ đó và gộp
Tầng 1 ngân hàng vào cùng một lượt quét portfolio-wide. Chi phí biên: **0 cron mới** cho (a)+(b),
**1 dòng cron mới** cho (c).

⚠️ **Một phát hiện đi NGƯỢC trực giác của chính đề xuất, phải nói trước** (§3.3): sau một cú sập
riêng lẻ vào **thứ Hai**, lợi suất phiên kế tiếp trung bình là **+0,02%** — không có đà giảm tiếp.
Trong khi sau cú sập **thứ Sáu** là **−3,09%**. Nghĩa là giá trị của lượt quét sáng thứ Hai
**KHÔNG nằm ở chỗ bán kịp** (bán sau cú sập thứ Hai không cứu được gì) mà nằm ở **phía MUA**:
không rót thêm tiền vào một mã mà luận điểm vừa gãy trong lúc mình ngủ. Tôi giữ đề xuất, nhưng lý
do của nó khác với lý do ban đầu, và số liệu bắt phải sửa lại lý do.

---

## A. Lịch sử THẬT của DGC và PNJ — cơ chế hiện có nhanh hay chậm?

### A.1 Câu trả lời thực chứng: cơ chế hiện có **nhanh tối đa có thể**, nhưng nó CHƯA TỒN TẠI lúc case xảy ra

Đây là điểm dễ đọc nhầm nhất, nên tách bạch hai câu hỏi khác nhau:

| Câu hỏi | Trả lời |
|---|---|
| Lúc PNJ/DGC xảy ra, hệ thống mất bao lâu để phát hiện? | **15 ngày** (PNJ) — vì lúc đó **không có cơ chế nào cả** |
| Nếu cơ chế HÔM NAY chạy lại lịch sử đó, nó bắt lúc nào? | **Phiên sàn đầu tiên** — sớm nhất mà một tín hiệu giá có thể có |

Bằng chứng cho vế 2 — chạy thật, không phải suy luận (`python3 anomaly_scan.py --selftest`):

```
PNJ: kỳ vọng alert 2026-07-03 → thực tế 2026-07-03  PASS
DGC: kỳ vọng alert 2026-03-17 → thực tế 2026-03-17  PASS
PNJ 2026-03-09 (thị trường sập chung): PASS (không trip)   ← không phải cỗ máy báo bừa
SELFTEST PASS
```

Bằng chứng cho vế 1 — ngày tạo file, đọc từ git:

| Cơ chế | Ngày ra đời | So với tin PNJ (02/07/2026) |
|---|---|---|
| `anomaly_scan.py` | 2026-07-17 | **+15 ngày** |
| `anomaly_escalate.py` | 2026-07-17 | +15 ngày |
| `due_diligence.py` | 2026-07-21 | +19 ngày |
| `anomaly_gate.py` (chặn CAPIT mua PNJ) | 2026-07-21 | +19 ngày |
| `fearbuy_weekly_scan.sh` | 2026-07-23 | +21 ngày |

Dấu vết trên bus khớp chính xác: mã "PNJ" **lần đầu tiên** xuất hiện ngày `2026-07-17T11:20:15Z`,
đúng topic *"anomaly-detection chủ động kiểu DGC/PNJ — khảo sát+thiết kế+implement"*. Tức là toàn bộ
hạ tầng phát hiện hiện có **được sinh ra như phản ứng với chính hai case này** — user chú ý thấy
trước, hệ thống không thấy.

⇒ **Kết luận đúng cho câu hỏi của Mike**: không phải "cơ chế cũ chậm nên cần cơ chế mới". Mà là
"cơ chế đã được xây xong sau case, và chưa từng được kiểm tra sống trên một case tương đương".
Việc cần làm là **mở rộng phạm vi + bịt lỗ**, không phải thiết kế lại.

### A.2 Đường đi giá thật, và độ trễ CÒN LẠI sau khi đã có cơ chế

**PNJ** (tin công bố **02/07, thứ Năm**; giá phiên đó vẫn **+0,64%** — tin chưa vào giá):

| Phiên | Thứ | Close | Return |
|---|---|---:|---:|
| 02/07 | Năm | 63.100 | +0,64% ← **ngày tin ra** |
| 03/07 | **Sáu** | 58.700 | **−6,97%** ← anomaly_scan bắt ở đây |
| 06/07 | Hai | 54.600 | −6,98% |
| 07/07 | Ba | 50.800 | −6,96% |
| 10/07 | Sáu | 46.600 | −6,80% |
| 13/07 | Hai | 43.850 | −5,90% ← đáy, **−30,5%** so với 02/07 |

**DGC** (khởi tố **17/03, thứ Ba**):

| Phiên | Thứ | Close | Return |
|---|---|---:|---:|
| 13/03 | Sáu | 77.400 | −4,33% ← **giá yếu TRƯỚC tin chính thức** |
| 16/03 | Hai | 73.900 | −4,52% |
| 17/03 | **Ba** | 68.800 | **−6,90%** ← anomaly_scan bắt ở đây, đúng ngày khởi tố |
| 20/03 | Sáu | 55.500 | −6,88% |
| 23/03 | Hai | 51.700 | −6,85% ← **−36,1%** so với 12/03 |

Hai case cho **hai bài học ngược nhau**, và đó là lý do không được khái quát từ một case:

- **PNJ: kênh TIN đi trước kênh GIÁ đúng 1 phiên.** Tin công khai chiều 02/07, giá chỉ phản ứng từ
  03/07. Một lượt quét tin sáng 03/07 sẽ biết trước cả phiên sàn đầu tiên và trước toàn bộ −30,5%.
- **DGC: kênh TIN KHÔNG đi trước.** Giá đã yếu 13/03 và 16/03 (−4,33%, −4,52%) trước ngày khởi tố
  chính thức — rò rỉ/đồn. Ở case này kênh giá và kênh tin hoà nhau; không kênh nào có lead time.

⇒ Không kênh nào thắng tuyệt đối. Đó là lập luận để **giữ cả hai** (giá hằng ngày + tin định kỳ),
không phải để thay cái này bằng cái kia.

### A.3 Độ trễ CÒN LẠI của thiết kế hiện tại — nguyên nhân cấu trúc

`anomaly_scan.py` đọc **BQ cache T-1** (đồng bộ 23:45 T2-T6) và chạy trong `ops_health_check.sh`
lúc **08:20 T2-T6**. Vậy alert của phiên D đến tay người lúc **08:20 của phiên D+1** — trước giờ mở
cửa 09:00, **40 phút**. Đó là độ trễ tối thiểu về mặt cấu trúc và **không rút ngắn được** bằng cách
chạy sớm hơn: dữ liệu giá của phiên D chỉ tồn tại sau khi phiên D đóng cửa.

Với PNJ: bắt ở phiên 03/07 (thứ Sáu) → báo **08:20 thứ Hai 06/07**, tức đã bỏ qua **cả cuối tuần**.
Từ mốc đó giá còn rơi tiếp −25,3% tới đáy 13/07. Nhưng — theo đúng §3 vòng trước — **bán ở mốc đó
là quyết định thua tiền trên trung bình** (5/5 lần cổng giá bắn đều sai, lỗ suất +24,2%/12 tháng).
Nên con số −25,3% **không phải "khoản đáng lẽ tiết kiệm được"**; nó là "khoản mà một cổng giá tự
động sẽ dụ mình cắt, rồi thường là sai".

---

## B. Watchlist tự đồng bộ portfolio — **ĐÃ CÓ**, và đã dùng đúng field

### B.1 Chuỗi dữ liệu hiện tại, đã kiểm từng mắt

```
DNSE positions API
  └─ trading_bot/brokers.py :: DNSEBroker.get_positions()      ← đọc "openquantity" ĐẦU TIÊN
  └─ mike/bin/compute_active_nav.py :: live_balance_and_positions()
       └─ data/execution_logs/active_nav_{SpaceX,ZaloPay}.json  ← cron 20:15 T2-T6
            └─ anomaly_scan.py :: load_universe()  → tier H (mã đang giữ)
                 + fa_ratings_8l rating≤2          → tier W (watchlist chất lượng)
```

Ba điều đã verify chứ không giả định:

1. **Đúng field.** `brokers.py:474` đọc `openquantity` trước, rồi mới tới các tên khác; và nó
   **cộng gộp** nhiều dòng cùng mã (DNSE trả 1 dòng/deal). Đây chính là bài học vừa rút hôm nay
   (`Taylor_20260814_021603` — `accumulateQuantity` sai vì gồm CP chờ về). Không cần sửa gì.
2. **Đã có cron.** `compute_active_nav_all.sh` 20:15 ICT T2-T6 — cài **2026-08-13** (hôm qua).
   Working-memory của tôi ghi "chưa có cron" là đã lạc hậu; tôi đã kiểm crontab thật.
3. **Vị thế EXCLUDED vẫn nằm trong watchlist.** `load_universe()` lấy mọi `positions[].ticker`,
   không lọc theo cờ `excluded` ⇒ **DGC vẫn được theo dõi** dù bị loại khỏi rebalancing. Đúng —
   loại khỏi giao dịch ≠ hết rủi ro; mình vẫn đang cầm.

**Danh sách hôm nay (`computed_at: 2026-08-13`) — hợp nhất 2 account: 29 mã.**

| Nhóm | N | Mã |
|---|---:|---|
| Ngân hàng (Tầng 1 vòng trước) | 13 | ACB BID CTG HDB LPB MBB MSB SHB TCB TPB VCB VIB VPB |
| Ngoài ngân hàng (**phần mở rộng**) | 16 | CSV **DGC** DRI EVF HPG NCT PVT SAB SCL SIP **TV1** VHM VIX VND VNM VRE |

Mở rộng từ 13 → 29 mã, tức **+16 tên**. Đây là lý do việc này rẻ: không phải nhân đôi hệ thống, chỉ
là cùng một lượt quét chạy trên một danh sách dài hơn 16 dòng.

### B.2 LỖ HỔNG THẬT #1 — không có cổng độ tươi cho watchlist

`load_universe()` chỉ `json.load()` file `active_nav_*.json`, **không kiểm `computed_at`**. Hệ quả
cụ thể: `compute_active_nav_all.sh` chết một tối (mất mạng DNSE, hết hạn token, API 5xx) → sáng hôm
sau `anomaly_scan` quét một **danh mục cũ**, và **không ai biết**. Mã vừa mua hôm qua **vô hình**
với lớp bảo vệ.

Đây đúng nghĩa là câu hỏi (1) của user — *"portfolio thay đổi thì watchlist có tự cập nhật không?"*
— ở dạng cơ học: **có tự cập nhật, nhưng không có ai gác việc cập nhật đó có thật sự xảy ra không.**

Đây cũng là vi phạm trực tiếp `coding_guidelines.md §14` (*mọi cặp producer→consumer chạy trên 2
cron độc lập phải có freshness precheck thật ở phía consumer*). Cặp này (20:15 sản xuất → 08:20 tiêu
thụ) mới ra đời **hôm qua**, nên chưa ai áp §14 vào.

**Vá đề xuất** — tái dùng nguyên mẫu đã có, không viết mới: `anomaly_gate.py::anomaly_flags_freshness()`
đã làm đúng việc này cho `anomaly_flags.json` (và `golive_recommend_v23.py:579` đã in WARNING khi
stale). Làm y hệt cho `active_nav_*.json`:

- `computed_at` < ngày giao dịch gần nhất ⇒ in cảnh báo LỚN trong report + gắn cờ
  `universe_stale=true` vào JSON output.
- **KHÔNG fail-closed** (không dừng quét): quét danh mục cũ vẫn hơn không quét gì. Nhưng phải nói
  ra, đúng nguyên tắc quiet-heartbeat — "đã quét, sạch" phải phân biệt được với "quét nhầm sổ cũ".

---

## C. Khoảng trống cuối tuần — đo thật, và kết quả buộc phải sửa lại lý do

### C.1 Lịch hiện tại, đọc từ `crontab -l` (không tin comment)

| Giờ ICT | Ngày | Việc | Kênh |
|---|---|---|---|
| 08:20 | **T2-T6** | `ops_health_check.sh` → `anomaly_scan.py` | **GIÁ/KL** (BQ cache T-1) |
| 08:10 | **chỉ T6** | `fearbuy_weekly_scan.sh` → dispatch Taylor + WebSearch | **TIN** |
| 08:25 / 08:30 / 08:45 | T2-T6 | cron_health / report_cadence / preflight | không liên quan tin xấu |

Hai khoảng trống, khác nhau về bản chất:

- **Trống KÊNH TIN trong tuần**: tin nổ thứ Hai → kênh tin không chạm tới nó cho tới **thứ Sáu**
  (tối đa **4 ngày**). Cái này *lớn hơn* khoảng trống cuối tuần mà user hỏi, và ít ai để ý.
- **Trống CUỐI TUẦN**: tin nổ T7/CN, không có phiên nào để giá phản ứng ⇒ kênh giá **về mặt cấu
  trúc mù** cho tới 08:20 **thứ Ba** (sau khi thứ Hai đã sập trọn một phiên). Kênh tin thì đã chạy
  thứ Sáu **trước khi tin tồn tại**.
- Ngược lại, **tin nổ tối thứ Sáu (sau phiên) hoặc sập trong phiên thứ Sáu thì ĐÃ ĐƯỢC PHỦ**:
  `anomaly_scan` chạy 08:20 thứ Hai đọc cache thứ Sáu ⇒ báo trước giờ mở cửa thứ Hai. Ca PNJ chính
  là ca này và nó đã được phủ.

### C.2 Khoảng trống này có THẬT không? — đo trên 10 năm dữ liệu

> **Cập nhật 2026-08-14 (vòng verify quant-skeptic)** — phép đo dưới đây nay có script + CSV
> kiểm lại được: **`weekday_idiocrash_stats_20260814.py`** cùng thư mục (`_weekday.csv`,
> `_forward.csv`, `_episodes.csv`). Số trong bảng là bản chạy lại 2026-08-14 trên cache tới
> phiên 08-13, nên lệch vài đơn vị so với bản viết tay ban đầu (5.497→5.496) — kết luận không đổi.
> **Bộ lọc thanh khoản phải nói rõ**: `liq=both` = `val1m_bn ≥ 3` **VÀ** `val_bn ≥ 3` (đúng
> nhánh tier-W của `anomaly_scan.compute_signals`, là biến thể dùng cho bảng này); `liq=adv` =
> chỉ `val1m_bn ≥ 3` ⇒ N=**5.738**. Không khai biến thể chính là nguồn của mọi chênh N (§F.7).
>
> ⚠️ **Bẫy thứ hai, phát hiện khi verify chính script này (2026-08-14) — số ĐÃ ĐỔI vì bẫy này.**
> Bản chạy đầu dùng `python3` hệ thống (pandas **2.3.3**), bản này dùng `$DNA_PYEXE`
> (`wc_venv`, pandas **3.0.2**). CÙNG script + CÙNG dữ liệu ra **số khác nhau**: N episode
> market/`none` 71.749 (pandas 2) vs 71.637 (pandas 3). Gốc: `pct_change()` mặc định
> `fill_method='pad'` ở pandas 2 nhưng `None` ở pandas 3 — cột mirror `VNINDEX` NULL đúng **5
> phiên** (2016-01-04, 2020-01-02, 2020-01-03, 2025-05-04, 2025-05-11), pandas 2 pad giá trị
> phiên trước ⇒ **bịa ra "phiên đó thị trường đi ngang 0%"** ⇒ `idio` có giá trị ở nơi lẽ ra
> phải khuyết ⇒ đếm dôi episode. Đã vá tận gốc: script khai `fill_method=None` tường minh (+ lọc
> `Close > 0`, vì 2.419 dòng giá ≤0 làm `fwd*` ra `inf`). **Sau khi vá, hai interpreter cho
> output khớp TUYỆT ĐỐI từng byte** — số dưới đây là bản đã ổn định, không còn phụ thuộc máy ai
> chạy. Đây đúng nhóm bẫy §8 coding_guidelines (dùng sai interpreter so với bản pin).

Đếm **episode sập riêng lẻ đầu tiên** (`ret ≤ −6%` **và** `idio ≤ −5%`, `liq=both`, hợp
nhất các phiên cách nhau ≤7 ngày thành 1 episode), 2016-01→2026-08-13, cache BQ local:

| Thứ | Số episode | Số phiên | Episode/phiên |
|---|---:|---:|---:|
| **Hai** | **1.401** | 518 | **2,705** |
| Ba | 1.174 | 533 | 2,203 |
| Tư | 1.066 | 534 | 1,996 |
| Năm | 837 | 534 | 1,567 |
| Sáu | 1.018 | 532 | 1,914 |

**Thứ Hai = 1,409× tỉ lệ trung bình T3-T6**, χ²=177,9, **p=2,1e-37**, N=5.496.
(`liq=adv`: 1,414×, χ²=189,4, p=7,3e-40, N=5.738 — cùng kết luận.)
⚠️ Đây là số của **TOÀN mẫu**, không phải hằng số đều suốt 10 năm: 2016-19 chỉ 1,202× và
**p=0,14 (không có ý nghĩa)**; 2020-22 1,369×; 2023-26 1,543×. Đọc **§F.9** trước khi trích.

**Kiểm chứng đối xứng (bắt buộc, nếu không thì đây chỉ là hiệu ứng phương sai cuối tuần):** làm lại
y hệt cho cú **TĂNG** riêng lẻ (`ret ≥ +6%`, `idio ≥ +5%`), N=10.921 → thứ Hai chỉ **1,115×**.

| | Tỉ trọng thứ Hai | |
|---|---:|---|
| Sập riêng lẻ | **25,5%** | |
| Tăng riêng lẻ (đối chứng) | 21,3% | |
| Chênh | +4,2pp | **z = 6,05, p = 1,4e-09** |

⇒ Thứ Hai dồn biến động **không đối xứng**, nghiêng hẳn về **tin XẤU**. Đây không phải hiện vật
"cuối tuần tích luỹ thông tin nên thứ Hai biến động mạnh hai chiều" — nếu vậy chiều tăng phải lệch
tương đương, mà nó chỉ lệch 1,115×. **Khoảng trống cuối tuần là thật, và đo được.**

### C.3 NHƯNG — giá trị của nó KHÔNG nằm ở phía bán

Đo tiếp lợi suất **sau** phiên sập, theo thứ trong tuần (cùng tập N=5.496, `liq=both`; cột CI là
bootstrap 2.000 lần trên trung bình fwd1):

| Thứ của cú sập | Sập ngày đó | +1 phiên | CI 95% của +1 phiên | +2 phiên | +3 phiên | P(phiên kế tiếp âm) |
|---|---:|---:|---:|---:|---:|---:|
| **Hai** | −7,97% | **~0%** | **[−0,23% ; +0,29%] — chứa 0** | +0,38% | +0,03% | **42,3%** |
| Ba | −7,51% | −0,62% | [−0,89% ; −0,35%] | −0,47% | −1,03% | 47,1% |
| Tư | −7,33% | −0,50% | [−0,82% ; −0,19%] | −0,39% | −1,64% | 49,3% |
| Năm | −7,80% | −0,65% | [−0,97% ; −0,30%] | −2,53% | −2,80% | 50,2% |
| **Sáu** | −7,57% | **−3,10%** | **[−3,40% ; −2,77%] — không chứa 0** | −3,28% | −2,43% | **65,6%** |

⚠️ **Ô "~0%" cố ý KHÔNG in số thập phân** (sửa 2026-08-14 theo verdict quant-skeptic). Bản đầu ghi
`+0,02%`; vòng tái lập độc lập ra `−0,04%`. **Sau khi vá bẫy interpreter (§C.2) thì rõ: cả hai
đều đúng, chỉ khác BIẾN THỂ LỌC** — `liq=both` (nhánh tier-W production) cho **+0,02%**, `liq=adv`
cho **−0,05%**; con số bản đầu tái lập lại được chính xác. Chính việc **dấu của nó đổi theo một
lựa chọn lọc vô thưởng vô phạt** là bằng chứng mạnh nhất rằng đại lượng này không khác 0; in 2
chữ số thập phân là gán độ chính xác giả cho một số mà ngay cả DẤU cũng không xác định.

Đọc thẳng:

- **Sập thứ Hai = tin đã vào giá xong ngay trong phiên đó.** Không có đà giảm tiếp (CI chứa 0), xác
  suất phiên sau âm chỉ 42,3% — thấp hơn tung đồng xu. Biết trước lúc 08:00 thứ Hai **không cứu
  được cú gap mở cửa** (không giao dịch được trước 09:00), và sau gap thì không còn gì để tránh.
- **Sập thứ Sáu mới là cú còn rơi tiếp** (−3,10%, CI không chứa 0, P(âm)=65,6%) — vì tin có nguyên cuối tuần để lan
  và để margin call chín. Và ca này **đã được phủ** bởi lượt 08:20 thứ Hai hiện có.

⇒ **Sửa lại lý do của lượt quét thứ Hai.** Nó không phải để "bán kịp trước khi sập" — số liệu nói
việc đó không có giá trị. Nó là để:

1. **Không MUA vào một luận điểm vừa gãy.** `run_bot.sh` chạy **09:05 thứ Hai** với plan đã duyệt
   từ tối thứ Sáu/Chủ nhật. Nếu tin xấu nổ Chủ nhật, plan đó vẫn nguyên si và bot vẫn đặt lệnh mua.
   Đây **không phải giả thuyết** — đó chính xác là ca đã ghi trên bus 2026-07-20:
   *"CAPIT due-diligence gate — PNJ sẽ bị mua full-size nếu không chặn"*.
2. **Người duyệt có bối cảnh trước phiên**, thay vì đọc tin xấu vào sáng thứ Ba khi đã lỡ một phiên.

Hai giá trị này đều thuộc phía **phòng thủ vốn chưa giải ngân**, không phải phía cắt lỗ vị thế đang
có — và vì thế **hoàn toàn nhất quán** với quyết định Tầng 2 vừa chốt (không tự động hoá hành động).

### C.4 Tần suất cảnh báo dự kiến — để biết có gây nhiễu không

Áp đúng luật tier-H lên 29 mã đang giữ:

| Luật | 2024→nay | 2025→nay |
|---|---:|---:|
| IDIOCRASH | 2,07 episode/tháng | 2,53 |
| FLOOR2 (ngày 1) | 2,23 episode/tháng | 2,84 |

≈ **1 cảnh báo mỗi 2 tuần**. Đủ hiếm để mỗi cái đều được đọc, đủ thường xuyên để biết pipeline còn
sống. Không cần nới ngưỡng, cũng không cần siết.

---

## D. Hợp nhất với Tầng 1 ngân hàng — MỘT lượt quét, hai bộ từ khoá

Không xây 2 cơ chế song song. `fearbuy_weekly_scan.sh` đã là một **dispatch wrapper** (LLM đọc tin +
phân loại QUALIFY/NON/AMBIGUOUS) chạy trên `anomaly_scan.py` + WebSearch. Nó **đã có sẵn hình dạng
đúng**; chỉ cần đổi phạm vi đầu vào và bộ từ khoá.

### D.1 Thay đổi phạm vi: từ "săn cơ hội" sang "săn cơ hội + gác hàng đang giữ"

Hiện `fearbuy_weekly_scan.sh` quét **toàn thị trường để TÌM cơ hội mua**. Mục 4 của prompt có nhắc
"case đã có trong watchlist (TV1, DGC, PNJ...)" nhưng đó là **danh sách tay chép cứng trong prompt**
— đúng cái mà user lo sẽ lạc hậu. Thay bằng: danh sách sinh từ `load_universe()` (mục B), tự đổi
theo vị thế thật.

### D.2 Bộ từ khoá — theo NHÓM, tái dùng khung sẵn có, không phát minh lại

| Nhóm | Mã (hôm nay) | Từ khoá |
|---|---|---|
| **Chung — mọi mã** | 29 | khởi tố · bắt tạm giam · thanh tra · điều tra · đình chỉ giao dịch · hạn chế giao dịch · từ chối kiểm toán · ý kiến ngoại trừ · chậm nộp BCTC · cắt margin · huỷ niêm yết |
| **Ngân hàng** (bổ sung, từ §4.2 vòng trước) | 13 | **kiểm soát đặc biệt · chuyển giao bắt buộc · rút tiền hàng loạt · khởi tố chủ tịch/TGĐ ngân hàng · cho vay sân sau · thao túng cổ phiếu ngân hàng** |
| **Phi tài chính** (bổ sung) | 16 | tai nạn/sự cố nhà máy · thu hồi sản phẩm · mất giấy phép/mỏ · kê biên tài sản · tranh chấp lãnh đạo |

Phân loại kết quả: **giữ nguyên khung QUALIFY / NON / AMBIGUOUS** của
`calculated_fear_state_backstop.md`. Không thêm khung mới. Trục quyết định cũng giữ nguyên:
*cáo buộc chạm LÕI (sổ tín dụng với ngân hàng / tài sản sản xuất với phi tài chính) hay chỉ chạm
CÁ NHÂN?* — đúng trục đã tách đúng PNJ-2015 (QUALIFY) khỏi PNJ-2026 (AMBIGUOUS) và OGC (NON).

### D.3 Điều đã có sẵn, không cần làm lại

- **Cờ + TTL**: `anomaly_flags.json`, TTL 30 ngày, cửa sổ hai đầu chống look-ahead — dùng luôn.
- **Hiển thị cho người duyệt plan**: `due_diligence.py::_anomaly_note()` đã echo cờ vào báo cáo
  due-diligence tại **4 choke-point** (gồm `golive_recommend_v23.py` và `send_plan_report.sh`)
  ⇒ mọi lệnh mua BAL/LAG đều **hiện cờ** cho người duyệt. Không cần thêm đường hiển thị.
- **Chặn cứng phía mua**: hiện chỉ áp cho **rổ CAPIT** (`golive_recommend_v23.py:814`, trong nhánh
  `if capit_signal_today`). BAL/LAG **không bị chặn tự động** — chỉ hiện cảnh báo cho người duyệt.
  ⚠️ **Tôi KHÔNG đề xuất mở rộng hard-block sang BAL/LAG trong vòng này**: đó là thay đổi **chọn mã
  của production**, phải qua backtest + walk-forward + DSR/PBO + quant-skeptic, không phải một lớp
  phát hiện. Nếu user muốn, đó là **một job riêng**. Nêu ở đây để user biết ranh giới hiện tại nằm
  đâu, không phải để lặng lẽ mở rộng.

---

## E. Kế hoạch đề xuất

**Nguyên tắc bao trùm, không thay đổi: ESCALATE-ONLY. Không tự bán, không tự mua.** Chỉ tự động hoá
**PHÁT HIỆN**, nhất quán với quyết định Tầng 2 user vừa chốt (2026-08-14, `Mike/answer`).

### E.1 Ba việc, xếp theo tỉ lệ giá-trị/chi-phí

| # | Việc | Chạm gì | Cron mới | WebSearch/tuần thêm |
|---|---|---|---|---|
| **E1** | Cổng độ tươi `active_nav_*.json` trong `load_universe()` + cờ `universe_stale` ra output | `anomaly_scan.py` (~15 dòng) | **0** | **0** |
| **E2** | Watchlist tự động + từ khoá theo nhóm cho lượt quét tin (bỏ danh sách chép cứng) | `fearbuy_weekly_scan.sh` (prompt) | **0** | **0** (cùng 1 lượt, prompt dài hơn) |
| **E3** | Thêm lượt quét tin **sáng thứ Hai 08:00 ICT** phủ T6-tối→CN | 1 dòng crontab + 1 wrapper | **1** | **+~12–15 truy vấn** |

- **E1 + E2 = 0 chi phí biên.** Đề xuất làm ngay khi user duyệt.
- **E3** là phần duy nhất tốn thêm. Ước lượng: 1 lượt/tuần × ~12–15 WebSearch ⇒ **+12–15
  truy vấn/tuần**, gấp đôi kênh tin (từ 1 lượt/tuần lên 2). Rẻ tuyệt đối; nhưng lý do biện minh
  cho nó là **phía mua** (§C.3), không phải "bán kịp" — nếu user thấy lý do đó không đủ, **bỏ E3
  vẫn là lựa chọn hợp lý** và E1+E2 giữ nguyên giá trị.

### E.2 Chi tiết E3

- **08:00 ICT thứ Hai** — trước `ops_health_check` 08:20, trước `preflight` 08:45, trước phiên 09:00.
- Cùng script/wrapper với lượt thứ Sáu, chỉ khác **cửa sổ tin: 3 ngày (T6 sau phiên → CN)** thay vì
  7 ngày. Không dựng script thứ hai.
- **Không đụng `preflight_check.sh`**: preflight là cổng sẵn-sàng-thực-thi có ràng buộc thời gian
  chặt (08:45, ngay trước 09:05); nhét một dispatch LLM + WebSearch (thời gian không đoán trước
  được) vào đó là biến một checker tất định thành một checker có thể treo. Tách riêng.
- **Đầu ra**: bus finding + Discord Taylor thread. **Luôn có output kể cả khi sạch** ("0 case mới,
  29 mã rà qua") — quy tắc quiet-heartbeat.
- **Không có hành động tự động nào** gắn vào output này.

### E.3 Việc CỐ Ý không làm

| Không làm | Vì |
|---|---|
| Cổng giá → tự bán | §3 vòng trước: 5/5 lần bắn đều sai, lỗ suất +24,2%/12 tháng |
| Chạy quét tin **hằng ngày** | Chưa đo được giá trị biên so với Mon+Fri; và §C.3 cho thấy lợi ích của "sớm hơn" nhỏ hơn trực giác. Nếu sau 2-3 tháng thấy có case rơi vào T3-T5 bị bỏ lọt → mở rộng khi đó, có bằng chứng |
| Hard-block anomaly cho BAL/LAG | Thay đổi chọn mã production ⇒ cần backtest + DSR/PBO + quant-skeptic (job riêng) |
| Cơ chế riêng cho phi-ngân-hàng | Gộp làm một (§D) |
| Fail-closed khi watchlist stale | Quét sổ cũ vẫn hơn không quét; nhưng phải in cảnh báo |

---

## F. Giới hạn của nghiên cứu này — đọc trước khi trích số

1. **N=2 cho câu hỏi "cơ chế bắt kịp không"** (DGC, PNJ) — và hai case cho hai kết luận ngược nhau
   về lead time của kênh tin (§A.2). Không đủ để nói kênh nào tốt hơn.
2. **Hiệu ứng thứ Hai (1,409×, p=2,1e-37) là thống kê TOÀN THỊ TRƯỜNG**, không phải của 29 mã đang
   giữ. Trên chính 29 mã (bản chạy lại 2026-08-14, `_weekday.csv` scope=`hold29`):

   | Luật | biến thể lọc | N episode | Tỉ trọng T2 | p |
   |---|---|---:|---:|---:|
   | IDIOCRASH | `none` (= đúng nhánh `is_hold` của production) | 391 | 22,5% | 0,058 |
   | IDIOCRASH | `adv` | 184 | 29,4% | 0,00096 |
   | FLOOR1 (ngày 1) | `none` | 432 | 29,4% | 8,5e-07 |
   | FLOOR2 (2 phiên liên tiếp) | `none` | 59 | 28,8% | 0,061 |

   Vẫn nghiêng thứ Hai nhưng N nhỏ, khoảng tin cậy rộng. Số 1,409× **không được trích như "rủi ro
   thứ Hai của danh mục mình"**.
   ⚠️ Bản đầu ghi `N=376` (IDIOCRASH) / `N=415` (nhãn "FLOOR2"). Tỉ trọng tái lập được gần đúng
   (22,3%→22,5%; 28,9%→29,4%) và **nhãn thì đã truy ra**: "FLOOR2" của bản đầu thực ra là luật
   **FLOOR ngày 1** (432), không phải luật 2-phiên-liên-tiếp (59) — nay script chạy CẢ HAI dưới
   tên `FLOOR1`/`FLOOR2` để không ai phải đoán lại. **Phần dư ~4% thì vẫn KHÔNG truy được**, và
   đây là điều đã **kiểm rồi mới nói**: giả thuyết "bản đầu chạy trên cửa sổ ngắn hơn" đã được
   **thử và BÁC BỎ** — quét mọi ngày kết thúc từ 2026-02-01→04-15, **không có ngày nào** cho
   đồng thời 376 và 415 (376 chỉ ứng với end=2026-03-09; 415 ứng với end=2026-03-02/03). Vì phép
   đo gốc chỉ tồn tại dưới dạng văn xuôi, nguyên nhân dừng ở "không tái lập được";
   **số dùng từ nay là bảng trên**.
3. **Không đo được thứ quan trọng nhất**: trong 1.401 cú sập thứ Hai, bao nhiêu cái **phát hiện
   được bằng tin cuối tuần**? Không có cách đo hồi tố (không có kho tin lịch sử có timestamp). Toàn
   bộ lập luận E3 đứng trên suy diễn *"lệch bất đối xứng về chiều xấu ⇒ tin xấu cuối tuần"*, hợp lý
   nhưng **chưa được chứng minh trực tiếp**.
4. **`~0%` sau cú sập thứ Hai là TRUNG BÌNH, và bản thân nó không khác 0.** Phân phối rất rộng; nó
   bác bỏ "trung bình còn rơi tiếp", **không** bác bỏ "case cá biệt còn rơi tiếp rất sâu" (PNJ
   chính là một case như vậy). Đừng trích lại nó dưới dạng số thập phân — xem ô cảnh báo §C.3.
5. ~~**Chưa kiểm E1/E2/E3 chạy thật**~~ — **hết hiệu lực 2026-08-14**: E1/E2/E3 đã wire thật
   (commit `mike@2ce53d7a`, job `Taylor_20260814_041116`), quant-skeptic CONFIRMED độ tin cậy cao.
   Con số duy nhất còn là ước lượng: tần suất cảnh báo §C.4 (≈1/2 tuần) — chờ vận hành thật.
6. **Chưa che**: rủi ro gánh nặng bên nhận chuyển giao 0 đồng (VCB/MBB/VPB/HDB) — nêu từ vòng
   trước, vẫn là job riêng.
7. **BỘ LỌC THANH KHOẢN PHẢI ĐƯỢC KHAI, KHÔNG ĐƯỢC NGẦM ĐỊNH** (bài học rút ra ở vòng verify
   2026-08-14, gốc của CẢ HAI lần chênh N). Luật `IDIOCRASH` production KHÔNG có một bộ lọc duy
   nhất — nó rẽ nhánh theo `is_hold`: mã **đang giữ** không qua cổng thanh khoản nào, mã **không
   giữ** phải qua `val1m_bn ≥ 3` **VÀ** `val_bn ≥ 3`. Vì vậy câu "N của phép đo này là bao nhiêu"
   **không có đáp án đơn trị** nếu không nói rõ biến thể:

   | Chênh đã xảy ra | Nguyên nhân thật |
   |---|---|
   | 5.741 (tái lập) vs 5.497 (bản đầu) | `liq=adv` vs `liq=both` — bản đầu dùng đúng nhánh tier-W production, chỉ quên khai. (Cả hai số nay dịch nhẹ còn 5.738 / 5.496 sau khi vá bẫy interpreter §C.2.) |
   | 184 (tái lập) vs 415 (bản đầu) | **hai** khác biệt chồng nhau: khác **LUẬT** (IDIOCRASH vs FLOOR ngày 1 = `FLOOR1`, 432) *và* khác **biến thể lọc** (`adv` vs `none`) — cộng thêm ~4% dư đã thử-và-bác-bỏ giả thuyết cửa sổ ngắn (mục 2) |

   ⇒ Từ nay mọi bảng số trong file này đều ghi kèm `liq=` và tên luật; script
   `weekday_idiocrash_stats_20260814.py` cố ý chạy **cả ba** biến thể × **bốn** luật để không ai
   phải đoán lại.

8. **Số của file này chỉ tái lập được bằng ĐÚNG interpreter đã pin** (`$DNA_PYEXE` =
   `/home/trido/thanhdt/wc_venv/bin/python`) — xem bẫy pandas 2 vs 3 ở §C.2. Script nay đã tự
   miễn nhiễm (khai `fill_method=None` tường minh, đã verify hai interpreter cho output khớp
   từng byte), nhưng **bài học chung thì rộng hơn script này**: mọi phép đo dùng `pct_change()`
   trên dữ liệu có ô khuyết đều dính, và nó **hỏng ÂM THẦM** — không exception, không cảnh báo,
   chỉ là vài trăm episode dôi ra từ những phiên lẽ ra không có `idio`.

9. **1,409× là số của TOÀN mẫu 2016→nay, KHÔNG phải một hằng số ổn định suốt 10 năm.** Cắt theo
   giai đoạn (thêm 2026-08-14 theo khuyến nghị #3 vòng verify quant-skeptic; nay có sẵn cột
   `period` trong `_weekday.csv` / `_forward.csv`, lát cắt `market · IDIOCRASH · liq=both`):

   | Giai đoạn | N episode | Tỉ trọng T2 | Tỉ lệ T2/T3-T6 | χ² | p | fwd1 sau sập T2 | fwd1 sau sập T6 |
   |---|---:|---:|---:|---:|---:|---:|---:|
   | **all (2016→08/2026)** | 5.496 | 25,49% | **1,409×** | 177,9 | 2,1e-37 | +0,02% | **−3,10%** |
   | 2016-19 | 834 | 22,30% | 1,202× | 6,9 | **0,141 (KHÔNG có ý nghĩa)** | **−1,20%** | −1,54% |
   | 2020-22 | 2.883 | 25,29% | 1,369× | 131,6 | 1,8e-27 | +0,18% | −4,16% |
   | 2023-26 | 1.779 | 27,32% | 1,543× | 122,1 | 1,9e-25 | +0,24% | −2,54% |

   Ba hệ quả, phải đọc đủ cả ba:
   - **Câu chữ**: hiệu ứng thứ Hai là **hiện tượng SAU 2020**, không phải sự thật đồng nhất
     "đo 10 năm". Đừng viết "10 năm ⇒ 1,409×" như một hằng số; viết "toàn mẫu 1,409×, tập trung
     ở nửa sau".
   - **Hướng lại có lợi cho việc deploy**: hiệu ứng **mạnh dần** về phía hiện tại
     (1,20 → 1,37 → 1,54), tức ngược hẳn chữ ký overfit thường gặp (mạnh IS, suy yếu OOS). Nếu
     nó là hiện vật khai thác dữ liệu thì đã phải yếu đi ở giai đoạn gần nhất.
   - **Bất đối xứng thứ Sáu ổn định DẤU ở cả 3 giai đoạn con** (−1,54 / −4,16 / −2,54), và
     `fwd1` sau sập thứ Hai không âm có ý nghĩa ở 2 giai đoạn gần nhất. Đây mới là chân đỡ của
     kết luận vận hành E3 (bảo vệ phía MUA sáng thứ Hai, không phải bán kịp) — nên **kết luận
     vận hành KHÔNG đổi**. Cái duy nhất phải chỉnh là mức tuyệt đối hoá của headline.
   - Lưu ý ngược chiều, không được giấu: ở **2016-19** `fwd1` sau sập thứ Hai là **−1,20%**
     (CI [−1,86; −0,56], không chứa 0) — tức mệnh đề "~0%" của §C.3 cũng là mệnh đề của giai
     đoạn SAU 2020, không phải của cả mẫu đều nhau.

---

## G. Cần user quyết

1. **E1 + E2** (0 chi phí biên): duyệt làm ngay? — khuyến nghị **CÓ**.
2. **E3** (thêm cron thứ Hai 08:00, +12–15 WebSearch/tuần): duyệt? — khuyến nghị **CÓ**, nhưng với
   lý do đã sửa lại: bảo vệ **phía mua** (không rót tiền vào luận điểm vừa gãy cuối tuần), **không
   phải** để bán kịp. Nếu user thấy lý do đó không đủ mạnh thì bỏ E3 là hợp lý.
3. **Hard-block anomaly cho BAL/LAG** — có muốn mở một job riêng để đo không? Đây là lỗ hổng thật
   duy nhất còn lại ở phía mua, nhưng nó là thay đổi production, không phải lớp phát hiện.
