# TWAP 17-block/15' vs gom-1-cửa-sổ — đo thật trên nến 15 phút

**Job**: `Taylor_20260804_124836` · **Owner**: Taylor · **Ngày**: 2026-08-04
**Hỏi bởi**: John (thread 1521735922066919515) qua Mike.
**Câu hỏi**: trải lệnh TWAP 17 block × 15 phút có tốt hơn cách gom-cửa-sổ (BUY 11:15 / SELL mở
cửa) về market impact / trượt giá / chất lượng khớp không?

---

## 0. Kết luận 1 đoạn

**Có dữ liệu thật để trả lời** — không phải lý luận suông. Trên **663 phiên độc lập**
(2023-09-11 → 2026-05-12, 33 mã ta thật sự giao dịch, nến 15'), kết quả là **tách đôi, không
phải một câu trả lời chung**:

- **Chân BÁN @mở cửa: TWAP THẮNG rõ.** "Edge" +9,3 bps của lệnh bán lúc mở cửa **không phải
  edge thực thi** — nó là một **đặt cược có đòn bẩy vào việc phiên hôm đó giảm**. Phân rã theo
  chiều phiên: ngày tăng >2% bán mở cửa **−168 bps**, ngày giảm >2% **+151 bps**. Độ phân tán
  gấp **3,27×** TWAP. Trung bình dương chỉ là phần dư mỏng của hai đuôi khổng lồ mà ta **không dự
  báo được lúc 09:15**.
- **Chân MUA @11:15: cửa sổ có edge THẬT, nhỏ nhưng bền.** Rẻ hơn day-VWAP **−7,4 bps**
  (t = −5,34), **cùng dấu ở cả 4/4 năm**, **30/33 mã**, và cùng dấu ở **mọi** nhóm điều kiện
  (ngày tăng −2,4 / ngày giảm −16,3 / ngày lặng −6,7 bps). Đây là hiệu ứng hình dạng phiên
  (chiều rẻ hơn sáng), không phải nhiễu.
- **Khuyến nghị: không phải chọn 1 trong 2 — trải TWAP *bên trong* cửa sổ thuận lợi.** Lịch
  HYBRID (MUA rải 5 block 11:00-13:30, BÁN rải 4 block 09:15-10:00) giữ **+15,8/16,7 = 95%**
  edge vòng khứ hồi mà cắt độ phân tán từ 62,0 → 53,5 bps, t tăng 6,91 → 7,62.
- **Về market impact — quy mô hiện tại của ta CHƯA đủ lớn để impact là vấn đề.** Lệnh trung vị
  24,5tr VND = **0,47%** khối lượng của 1 block. Chỉ ở lệnh lớn nhất (3,21 tỷ, gộp cả ngày)
  mới chạm 62% khối lượng 1 block — đó là ca duy nhất TWAP cần thiết vì lý do impact.
- ⚠️ Con số đo được là **hình dạng giá nội phiên lịch sử**, KHÔNG phải impact của chính lệnh ta
  (nến lịch sử không chứa lệnh của ta). Xem §5 giới hạn.

---

## 1. Dữ liệu — kiểm tra trước, không hứa trước

| Nguồn | Có nến trong ngày không? | Kết luận |
|---|---|---|
| BQ `ticker` / `ticker_1m` / `ticker_prune` | **KHÔNG** — OHLCV theo NGÀY (`time` DATE) | không dùng được cho câu hỏi này |
| `data/execution_logs/dnse_raw_*.jsonl` | Có `ts` giây, nhưng **561 `place_order` / 96 lệnh cha**, 32 phiên | quá mỏng để làm mẫu; dùng để lấy **quy mô lệnh thật** + **rổ mã thật** |
| **`data/intraday_full.pkl`** | **CÓ** — nến **15 phút**, **335 mã**, **2023-09-11 → 2026-05-12**, 2,84tr dòng | **nguồn chính của nghiên cứu này** |

`intraday_full.pkl` đã có trong registry: `mike/kb/data_registry/research-caches/static_panels.md`
(status **RESEARCH**, static, stale tự nhiên từ 05-17). Dùng cho nghiên cứu hình dạng nội phiên là
đúng vai — **không** phải nguồn tín hiệu sống, **không** wire vào bất cứ đâu.

Lưới giờ trong dữ liệu: `09:15 … 11:15` (sáng) + `13:00 … 14:45` (chiều) = 17 nhãn, khớp đúng
thiết kế 17 block/255 phút của John. Nghiên cứu dùng **16 block liên tục**, bỏ 14:45 (ATC — khớp
định kỳ, khác bản chất). Block 14:30 chỉ 0,8% khối lượng (khớp liên tục HOSE kết thúc ~14:30) —
giữ nhưng đọc riêng.

**Rổ**: 33/34 mã có lệnh thật trong `dnse_raw_*` (CTG/VPB/MBB/BID/VIB/HDB/TPB/DCM/VGC/SIP/NCT/…),
không phải toàn bộ 335 mã — để mẫu khớp cái ta thật sự mua bán.

**N khai theo kỷ luật §18**: 13.973 dòng ticker-day, nhưng **N = 663 PHIÊN** (gộp equal-weight
trong mỗi phiên trước rồi mới thống kê theo phiên) — 33 mã cùng phiên tương quan cực cao, khai
n=13.973 là sai.

Benchmark = **day-VWAP** (Σ giá điển hình × KL / ΣKL của chính ngày đó). Giá thực thi ước lượng
trong mỗi block = giá điển hình `(H+L+C)/3` (thực tế hơn giá đóng block).

---

## 2. Hình dạng giá nội phiên — gốc của mọi chuyện

Sai lệch so với day-VWAP (bps; **dương = mua đắt / bán được giá cao**), N = 663 phiên:

| Khung | mean (bps) | t | sd theo phiên | MAD |
|---|---|---|---|---|
| 09:15 | **+9,27** | 4,03 | 59,3 | 41,9 |
| 09:30 | +9,06 | 4,34 | 53,8 | 37,7 |
| 09:45 | +9,38 | 4,83 | 50,1 | 34,7 |
| 10:00 | +7,88 | 4,40 | 46,1 | 31,9 |
| 10:15 | +4,33 | 2,68 | 41,6 | 28,4 |
| 10:30 | +2,03 | 1,32 | 39,7 | 26,2 |
| 10:45 | −0,89 | −0,61 | 38,0 | 25,7 |
| 11:00 | −3,53 | −2,48 | 36,6 | 25,1 |
| **11:15** | **−7,37** | **−5,34** | 35,5 | 25,1 |
| **13:00** | **−12,21** | **−10,03** | 31,3 | 24,0 |
| 13:15 | −7,74 | −6,66 | 29,9 | 21,2 |
| 13:30 | −3,87 | −3,58 | 27,8 | 19,9 |
| 13:45 | −3,33 | −2,86 | 30,0 | 22,0 |
| 14:00 | −2,12 | −1,52 | 35,8 | 26,0 |
| 14:15 | −3,67 | −1,77 | 53,3 | 37,2 |
| 14:30 | −13,75 | −2,59 | 101,6 | 73,3 |
| **TWAP16** | **−0,27** | **−0,38** | **18,1** | **10,7** |

Hai điều đọc được:
1. **Dose-response đơn điệu** từ +9,4 (09:45) xuống −12,2 (13:00) rồi bò về 0 cuối phiên — sáng
   đắt, đầu chiều rẻ. Đây là *dấu hiệu hiệu ứng thật*, không phải kết quả bới 16 khung để tìm cái
   đẹp nhất (§18: dose-response là bằng chứng mạnh hơn t-stat của 1 điểm lẻ).
2. **TWAP hội tụ về benchmark theo cấu tạo** (−0,27 bps, t = −0,38) và có **độ phân tán thấp
   nhất tuyệt đối** (sd 18,1 vs 27,8-101,6 của mọi khung đơn lẻ). Đó chính là thứ TWAP bán:
   **loại rủi ro chọn giờ**, không phải tạo lợi nhuận.

**Khai báo multiple testing**: 16 khung được kiểm. Nhưng 11:15 và 09:15 là 2 khung được chọn
**trước** (charter `fill_timing`, không phải chọn sau khi nhìn bảng), và kết luận không dựa vào
việc chúng là cực trị — 13:00 mới là cực trị (−12,2 bps), rẻ hơn cả 11:15.

---

## 3. So khớp trực tiếp — gom-cửa-sổ vs TWAP

Cặp khớp theo phiên (mỗi phiên so 2 lịch trên cùng bộ dữ liệu), N = 663:

| Chân | so với TWAP | t | Đọc |
|---|---|---|---|
| BUY @11:15 | **rẻ hơn 7,11 bps** | −6,89 | có lợi |
| SELL @09:15 | **cao hơn 9,54 bps** | +5,00 | có lợi (nhưng xem §4) |
| **Vòng khứ hồi** | **+16,65 bps/vòng** | **+6,91** | sd 62,0 |

**Đối chiếu chéo quan trọng**: chương trình paper `fill_timing` ước +17,6 bps với t = 0,56
(n = 5 phiên BUY-window). Nghiên cứu này cho **+16,65 bps trên 663 phiên với t = 6,91** — **cùng
độ lớn, cùng dấu, mẫu gấp ~130 lần**. Tức là: giả thuyết edge-theo-giờ của charter **đúng về độ
lớn**, và **không cần chờ 65 tuần nữa** — nến lịch sử đã trả lời phần "hình dạng phiên có tồn tại
không". (Cái paper program vẫn phải chờ là phần khác: **fill thật của chính ta**.)

**Ổn định** (đây là phần quyết định, không phải t-stat):

| | 2023 (80 phiên) | 2024 (250) | 2025 (249) | 2026 (84) |
|---|---|---|---|---|
| BUY @11:15 vs VWAP | −7,01 | −6,42 | −9,30 | −4,85 |
| SELL @09:15 vs VWAP | +7,17 | +4,57 | +14,19 | +10,70 |
| TWAP16 | +3,00 | −0,53 | −0,51 | −1,87 |

**4/4 năm cùng dấu** cho cả hai chân. Theo mã: BUY@11:15 rẻ hơn TWAP ở **30/33 mã**;
SELL@09:15 cao hơn TWAP ở **33/33 mã**.

---

## 4. Nhưng chân BÁN không phải edge — nó là đặt cược hướng phiên

Phân rã +9,54 bps của SELL@09:15 theo chiều đi của chính phiên đó:

| Nhóm phiên | BUY @11:15 vs TWAP | **SELL @09:15 vs TWAP** | Vòng |
|---|---|---|---|
| Tất cả (663) | −7,12 | **+9,54** | +16,66 |
| Ngày TĂNG >2% (435) | −2,40 | **−168,06** | −165,65 |
| Ngày GIẢM >2% (336) | −16,28 | **+150,78** | +167,05 |
| Ngày lặng \|mv\|<1% (656) | −6,66 | **+9,58** | +16,24 |

*(Phân rã này dùng thông tin cuối phiên ⇒ là **chẩn đoán**, KHÔNG phải bộ lọc giao dịch được —
lúc 09:15 ta không biết phiên sẽ tăng hay giảm.)*

Đọc đúng:
- **Bán tại mở cửa = giữ trọn rủi ro cả phiên với dấu ngược.** Biên độ ±150-168 bps theo chiều
  phiên, so với "edge" trung bình +9,5 bps. Tỷ lệ tín hiệu/nhiễu ~1:17. Cái +9,5 bps chỉ nói
  rằng trong mẫu này số phiên giảm/độ lớn hơi nghiêng về phía có lợi — **đó là beta thị trường
  chui vào chi phí thực thi**, không phải kỹ năng khớp lệnh.
- **Chân MUA thì ngược lại**: giữ dấu âm (= rẻ) ở **cả 3 nhóm điều kiện**, kể cả nhóm ngày lặng
  (−6,66 bps) nơi hiệu ứng hướng phiên gần như bị khử. Đây là hiệu ứng hình dạng phiên thật.

⇒ **Đây là câu trả lời trực tiếp cho John**: cách trải-đều-TWAP của anh **đúng hơn hẳn ở chân
BÁN**; ở chân MUA thì cửa sổ hiện tại có nhặt được một ít edge thật mà TWAP thuần sẽ bỏ lỡ.

---

## 5. Market impact — đo được đến đâu, và tại sao quy mô ta chưa phải vấn đề

**KHÔNG đo được từ nến lịch sử**: impact của *chính lệnh ta* (nến quá khứ không chứa lệnh ta).
Bất kỳ con số "TWAP giảm impact X bps" nào rút ra từ dữ liệu này đều là bịa. Cái đo được là
**mức tham gia** — thứ quyết định impact có đáng lo hay không:

Rổ mã đang giao dịch có ADV trung vị **123,5 tỷ VND/ngày**. Lệnh cha thật (gộp theo ngày-mã-chiều,
96 lệnh, 2026-06-12 → 07-31): trung vị **24,5tr**, p90 **227tr**, lớn nhất **3,21 tỷ**.

| Quy mô lệnh | Gom hết vào 1 block | Trải TWAP (block mỏng nhất) |
|---|---|---|
| Trung vị 24,5tr | **0,47%** KL block | 0,15% |
| p90 227tr | **4,36%** | 1,43% |
| Lớn nhất 3,21 tỷ | **61,6%** | 20,3% |

Kinh nghiệm ngành: dưới ~1-2% khối lượng của khoảng thời gian thực thi, impact tạm thời gần như
không đo được so với spread. ⇒ **Ở lệnh trung vị, impact KHÔNG phải lý do để đổi lịch** — cái
đáng nói là spread (~22,5 bps đo được trong checkpoint `fill_timing`: BUY +14,0 / SELL −8,5 tại
cùng khung 09:15) và rủi ro chọn giờ (§2). Ở đuôi lớn (p90 trở lên, và tuyệt đối là ca 3,21 tỷ)
thì trải lệnh là **bắt buộc về mặt cơ học** — 61% khối lượng 1 block không khớp nổi ở giá hợp lý,
và đây đúng là lý do TWAP tồn tại.

**Một điểm phản trực giác về TWAP đều tay**: khối lượng theo giờ **không** phẳng —

| Khung | %KL ngày | lệch vs 6,25% đều tay |
|---|---|---|
| 09:15 | 8,37 | +2,12 |
| 11:00 | 4,40 | −1,85 |
| **11:15** | **4,22** | **−2,03** (mỏng nhất phiên sáng) |
| 14:00 | 8,78 | +2,53 |
| 14:15 | **12,34** | **+6,09** (dày nhất) |
| 14:30 | 0,80 | −5,45 |

TWAP **đều theo thời gian** bơm cùng một lượng tiền vào block 11:15 (4,2% KL) như vào block 14:15
(12,3% KL) ⇒ mức tham gia ở block mỏng cao gấp ~3× block dày. Với lệnh lớn, **VWAP-schedule**
(chia theo tỷ trọng khối lượng, không theo thời gian) tốt hơn TWAP đều — và đây là điểm cải tiến
duy nhất của bản thân lịch 17-block, độc lập với chuyện cửa sổ.

---

## 6. Lịch HYBRID — không phải chọn 1 trong 2

| Lịch | mean vs VWAP | t | sd | MAD | IR (mean/sd) |
|---|---|---|---|---|---|
| TWAP16 (trải đều cả ngày) | −0,27 | −0,38 | 18,1 | 10,7 | −0,015 |
| BUY gom @11:15 | −7,37 | −5,34 | 35,5 | 25,1 | −0,207 |
| **HYBRID BUY 11:00-13:30 (5 block)** | **−6,94** | **−6,80** | **26,3** | **18,6** | **−0,264** |
| HYBRID BUY chiều 13:00-13:45 (4 block) | −6,79 | −7,19 | 24,3 | 17,7 | −0,279 |
| SELL gom @09:15 | +9,27 | 4,03 | 59,3 | 41,9 | 0,156 |
| **HYBRID SELL 09:15-10:00 (4 block)** | **+8,89** | **4,64** | **49,4** | **34,2** | **0,180** |

Vòng khứ hồi: gom-cửa-sổ **+16,65 bps** (t 6,91, sd 62,0) vs HYBRID **+15,83 bps** (t 7,62,
sd 53,5). **Giữ 95% edge, cắt 14% độ phân tán, tỷ số tín hiệu/nhiễu tốt hơn ở mọi chân.**

---

## 7. Quy mô kinh tế — đừng phóng đại

+16,65 bps/vòng khứ hồi = **0,167% mỗi vòng quay đầy đủ NAV**. Nếu vòng quay 2 chiều của V2.4
cỡ ~3 lần NAV/năm (bậc độ lớn suy từ ghi chú TC-drag ~0,32%/năm @ TC 0,1% trong
`backtest_workflow.py` — **là giả định bậc độ lớn, chưa đo riêng cho V2.4**), phần này cỡ
**0,1-0,3%/năm**. So với CAGR 28,86%: **không phải đòn bẩy alpha, là vệ sinh chi phí**. Đáng làm
cho đúng, không đáng đánh đổi rủi ro/độ phức tạp lớn để lấy.

---

## 8. Giới hạn (đọc trước khi trích dẫn)

1. **Không đo được impact của chính lệnh ta** — chỉ đo hình dạng giá lịch sử và mức tham gia.
2. **Không có điều kiện tín hiệu**: mẫu là *mọi* ngày của 33 mã, không phải riêng ngày ta có tín
   hiệu LAG/BAL. Ngày sau tin BCTC có thể có hình dạng nội phiên khác. **Chưa kiểm được** (cần
   join lịch sử tín hiệu vào nến — việc riêng, làm được nếu muốn).
3. **Cache stale, hết 2026-05-12** — 2026 chỉ 84 phiên. Dấu vẫn nhất quán nhưng đoạn gần nhất
   mỏng nhất.
4. **Giá thực thi ước bằng `(H+L+C)/3` của block**, không phải fill thật; giả định ta là
   price-taker khớp ở giá trung bình block. Ở mức tham gia <1% đây là xấp xỉ hợp lý; ở lệnh lớn
   thì lạc quan.
5. **Bỏ ATC 14:45** — nếu thực thi có dùng ATC thì phải đo riêng (khớp định kỳ, cơ chế khác).
6. `intraday_full.pkl` là **research static**, chưa từng dùng cho quyết định sống. Không refresh,
   không wire.

---

## 9. Nếu muốn bằng chứng về fill THẬT (bổ sung, không thay thế)

Nghiên cứu này trả lời "hình dạng giá phiên có ưu ái giờ nào không" (**có**). Nó **không** trả lời
"lệnh của ta khớp thế nào" — cái đó chỉ tích lũy được từ thực thi thật:

- Mỗi lần khớp, ghi `ts` giây + giá + KL + mã + chiều (dnse_raw đã có đủ trường này; cái thiếu là
  **mẫu**, không phải cấu trúc log).
- Chỉ số cần theo dõi: **implementation shortfall vs giá quyết định (đóng cửa T-1)** và **vs
  day-VWAP của chính ngày đó** — chính là 2 thước đo dùng ở đây, để so được trực tiếp.
- Với 17 block/ngày, mỗi phiên thực thi sinh ~17 quan sát *có tương quan* — vẫn khai **N = số
  phiên**, không phải số fill.
- Blocker đã biết của paper program `fill_timing` (netting triệt tiêu 100% lệnh probe từ 07-28,
  xem `research/fill_timing_checkpoint_20260804.md`) vẫn cần gỡ trước khi kênh đó tích lũy tiếp.

---

## 10. Khuyến nghị (KHÔNG thay đổi code — đây là tư vấn nghiên cứu)

1. **Chân BÁN: bỏ gom-tại-mở-cửa.** Không có edge thực thi ở đó, chỉ có rủi ro hướng phiên
   (±150-168 bps). Trải ≥4 block, hoặc dùng thẳng TWAP như John đang làm.
2. **Chân MUA: giữ thiên lệch về 11:00-13:30, nhưng trải chứ đừng gom 1 block.** Edge −6,9 bps
   bền qua 4/4 năm, 30/33 mã, mọi nhóm điều kiện; trải 5 block giữ 95% edge và cắt sd 35,5→26,3.
3. **Nếu chỉ chọn 1 lịch duy nhất cho mọi thứ, TWAP-đều của John là lựa chọn phòng thủ đúng** —
   nó bỏ ~16 bps/vòng nhưng loại bỏ toàn bộ rủi ro chọn giờ (sd 18,1 vs 62,0) và không cần bảo
   trì giả thuyết nào.
4. **Cải tiến độc lập cho chính lịch 17-block**: chia theo **tỷ trọng khối lượng** thay vì đều
   theo thời gian (block 14:15 dày gấp 3× block 11:15). Chỉ đáng làm với lệnh ≥ p90 (227tr).
5. **KHÔNG cần chờ 65 tuần** như charter `fill_timing` ước — phần "hình dạng phiên" đã trả lời
   xong bằng 663 phiên lịch sử. Cái vẫn phải chờ là fill thật (§9).

---

## Tái lập

```bash
cd mike/agents/Taylor/exp_twap_20260804
/home/trido/thanhdt/wc_venv/bin/python twap_vs_window.py   # bang §2, §3, §5
/home/trido/thanhdt/wc_venv/bin/python robustness.py       # bang §3 (nam/ma), §6
```
Đầu ra trung gian: `per_day_exp.csv` (13.973 ticker-day). Production **không đụng đến**
(`git diff` sạch ngoài thư mục exp + research).

**quant-skeptic**: nghiên cứu này KHÔNG đề xuất thay đổi production và KHÔNG tạo claim CAGR/Sharpe
mới. Nếu ai đó muốn wire một lịch thực thi vào bot dựa trên kết quả này thì **lúc đó** mới cần
gate quant-skeptic + DSR/PBO.
