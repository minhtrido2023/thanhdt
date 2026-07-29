# DT5G — cửa sổ EXPANDING vs ROLLING: phân tích & khuyến nghị

**Job:** `Taylor_20260729_155142` (Việc 3) · **Ngày:** 2026-07-29 · **Tác giả:** Taylor
**Trạng thái:** PHÂN TÍCH — KHÔNG implement. Không sửa `vnindex_5state_ew_v1.py` /
`vnindex_5state_dual_v3.py` (đúng ràng buộc dispatch).

## 0. Kết luận trước (TL;DR)

**KHÔNG NÊN đổi expanding → rolling.**

Lý do gọn: đổi cửa sổ là **thay đổi mô hình** (đổi ngữ nghĩa của gate: "cực đoan so với toàn
lịch sử" → "cực đoan so với 5-10 năm gần đây"), phải re-validate toàn bộ chuỗi
`ew_v1 → dual_v3 → v3.1 → v3.4b → DT-gate → macro` + re-pin mọi backtest — trong khi nó
**chỉ giảm chứ không khử** được vấn đề gốc, và **hoàn toàn không đụng** tới kênh corp-action
(`Close`/`MA`) vốn cũng viết lại lịch sử.

**Vấn đề gốc không nằm ở cửa sổ — nằm ở chỗ bảng công bố không có versioning.**
Cách sửa đúng và rẻ hơn nhiều: **làm `vnindex_5state_dt5g_live` bất biến (append-only /
bi-temporal)** — mỗi phiên đã công bố thì không bao giờ ghi đè, chỉ append phiên mới và
recompute phần đuôi chưa chốt. Việc này (a) khử 100% hiện tượng viết-lại-lịch-sử ở downstream,
(b) đúng cả với kênh corp-action mà rolling không chạm tới, (c) **rủi ro mô hình bằng 0**,
(d) đúng triết lý point-in-time đội đã áp cho `universe_pit`.

Nếu **buộc** phải rolling (tôi không khuyến nghị): **10 năm (2.520 phiên)**, không phải 5 năm —
lý do §3.2.

---

## 1. Hiện trạng: chính xác chỗ nào là expanding

Đọc code (không suy đoán). Có **5 cấu trúc expanding** trong chuỗi, không phải 2:

| # | Cấu trúc | File / dòng | Cửa sổ | Ảnh hưởng khi sửa dữ liệu quá khứ |
|---|---|---|---|---|
| 1 | `expanding_pct_rank` cho 7–8 factor | `ew_v1.py:330` (7 factor) · `dual_v3.py:111,127` (**8 factor, có `f_PE` w=0.03**) | từ đầu lịch sử, `MIN_LB=252` | **Kênh chính.** Sửa 1 điểm quá khứ → đổi mẫu số + đếm ⇒ đổi rank của **mọi** ngày sau đó |
| 2 | `expanding_pct_rank` cho composite (rank-of-rank) | `ew_v1.py:356` · `dual_v3.py:136` | như trên | Khuếch đại #1 một tầng nữa |
| 3 | `pe_p90` = `np.nanpercentile(hist[:t+1], 90)` | `ew_v1.py:388-392` · `dual_v3.py:190-191` | từ đầu, min 60 obs | Override `EX-BULL→BULL`. Kênh trực tiếp của backfill VNINDEX_PE |
| 4 | `running_max` (drawdown) `np.maximum.accumulate` | `ew_v1.py:395` · `dual_v3.py:192` | từ đầu | Override `dd<-25% ∧ s≥4 → 3`. Sửa 1 đỉnh cũ → đổi dd của mọi ngày sau |
| 5 | `avg_vol_exp` = mean của `vol20` toàn lịch sử | `ew_v1.py:409-412` · `dual_v3.py:204` | từ đầu, min 60 obs | Override vol `EX-BULL→BULL` |

Các cấu trúc **KHÔNG** expanding (không phải nguồn lây): `EMA_ALPHA=0.40` (IIR nhưng suy giảm
`0.6^k`, sau 30 phiên ≈ 2e-7 ⇒ trí nhớ hữu hiệu ~30 phiên), `vol20` (20 phiên), PE-slope
`SLOPE_WIN=120` (`dual_v3.py:293`), DT 4-gate (10/25 phiên), macro cap (`cap_commit=7`).

**Hệ quả quan sát được hôm nay** (tôi tự đo, không chép báo cáo — diff parquet cache 07-28
đóng cứng vs BQ live 07-29):

```
101 / 3.134 phiên đổi state (3,22%) · 35 phiên lệch ≥2 tier
2018: 48 · 2019: 1 · 2020: 16 · 2022: 2 · 2023: 34
  2018-02-27 → 2018-05-08  48 phiên  [CRISIS,BULL] → [NEUTRAL,BULL]   (pha CRISIS 2018 BIẾN MẤT)
  2020-03-16 → 2020-04-03  14 phiên  BEAR → CRISIS                    (COVID: PHÒNG THỦ HƠN)
  2023-02-07 → 2023-03-16  28 phiên  NEUTRAL → BEAR                   (PHÒNG THỦ HƠN)
  2023-04-04 → 2023-04-11   6 phiên  NEUTRAL → BEAR
```
(mapping 1=CRISIS 2=BEAR 3=NEUTRAL 4=BULL 5=EX-BULL)

Đáng chú ý: hướng đổi **không đồng nhất** — 2018 nới lỏng (bỏ CRISIS), 2020/2023 siết chặt hơn.
Đây là dấu hiệu điển hình của nhiễu rank-of-rank, không phải một thiên lệch có hướng.

---

## 2. Góc (a) — tài nguyên tính toán: **KHÔNG phải vấn đề, và rolling còn RẺ HƠN**

Đo thật (`n=6.331` phiên = độ dài chuỗi VNINDEX 2000→nay, cùng máy):

| Cách | Thời gian / 1 factor | Số phép so sánh |
|---|---|---|
| expanding (hiện tại) | **84 ms** | ~20,0 M |
| rolling 5 năm (1.260) | **63 ms** | ~8,0 M |
| rolling 10 năm (2.520) | **73 ms** | ~16,0 M |

Expanding là `O(n²/2)`, rolling là `O(n·W)`. Với `n=6.331`, `n/2 = 3.165 < W` chỉ khi cửa sổ
> ~12,5 năm — nên **mọi cửa sổ rolling ≤10 năm đều rẻ hơn expanding**. Tổng chi phí cả 9 lần
gọi rank (8 factor + composite) hiện chỉ **<1 giây**; đây là phần **không đáng kể** so với bước
kéo universe từ BQ (30–60s).

Điều lo trong dispatch — *"rolling có phải tính lại rank mỗi ngày trên cửa sổ trượt thay vì toàn
lịch sử"* — không thành vấn đề: **cả hai cách hiện đều đã tính lại TOÀN BỘ chuỗi mỗi ngày**
(script chạy lại từ đầu, không incremental). Rolling không thêm việc gì.

⇒ **Góc (a) không đóng góp gì vào quyết định.** Chi phí tính toán không phải lý do giữ, cũng
không phải lý do đổi.

---

## 3. Góc (b) — nhu cầu sử dụng thật & chất lượng gate

### 3.1 Production chỉ cần state HÔM NAY — đúng, nhưng đó là lý lẽ CHỐNG lại việc đổi mô hình

Đúng là `get_gated_state()` chỉ đọc state hiện hành. Nhưng chính vì thế: **nếu chỉ cần
today-stability thì không có lý do gì phải đụng vào mô hình** — today-stability đã có sẵn
(DT-gate 25 phiên + `cap_commit=7`). Cái đang hỏng là **tính tái lập của LỊCH SỬ**, và lịch sử
chỉ được dùng bởi **backtest/audit** — nơi cách sửa đúng là *đóng băng vintage* (§5), không phải
đổi công thức gate.

Ngược lại, đổi sang rolling **có** ảnh hưởng tới state hôm nay: rank/ngưỡng thay đổi ⇒ chuỗi
state thay đổi ⇒ toàn bộ số đã pin (R3, DT4-vs-DT5G ablation, audit 49 transitions) phải đo lại.
Đổi cửa sổ để "lịch sử ổn định hơn" mà lại làm **đổi ngay state hôm nay** là ngược mục tiêu.

### 3.2 Chất lượng gate: rolling đổi NGỮ NGHĨA, không chỉ đổi tham số

Expanding rank trả lời: *"hôm nay cực đoan cỡ nào so với **mọi thứ ta từng thấy**?"*
Rolling rank trả lời: *"…so với **W năm gần đây**?"*

Ba hệ quả cụ thể, đều bất lợi cho một gate phòng thủ:

1. **Trôi ngưỡng theo regime (drift).** Sau một bull dài, cửa sổ rolling "quên" mức đỉnh cũ ⇒
   phân vị 0,90 (EX-BULL) bị kéo lên theo giá ⇒ gate **chậm nhận ra hưng phấn**. Với một hệ mà
   kết luận đã chốt là *"fail-safe risk gate, không phải return-enhancer"*, mất trí nhớ dài hạn
   đúng chỗ đuôi phân phối là mất đúng thứ mình mua bảo hiểm.
2. **Mẫu đuôi mỏng.** Ngưỡng CRISIS là `r_score_ema < 0,10`. Trên cửa sổ 5 năm (1.260 phiên),
   decile dưới chỉ có ~126 quan sát và trong VN thường **cùng một sự kiện** (2018, 2020, 2022
   mỗi cái chiếm trọn phần đuôi của cửa sổ chứa nó) ⇒ phân vị đuôi nhiễu mạnh, dễ whipsaw.
   Expanding (≥3.400 obs tại 2014, ~6.300 obs hôm nay) không gặp vấn đề này.
3. **Chu kỳ VN dài hơn 5 năm.** VNINDEX đi ~4–6 năm/chu kỳ đầy đủ (2007-09, 2018, 2020-22,
   2024-25). Cửa sổ 5 năm có thể **không chứa trọn 1 chu kỳ bear** ⇒ có giai đoạn cửa sổ
   toàn-bull, khi đó phân vị hoàn toàn mất neo. **Nếu bắt buộc phải rolling thì tối thiểu 10
   năm** — đủ chứa ≥1 chu kỳ đầy đủ ở mọi thời điểm — và ngay cả vậy vẫn phải hiệu chuẩn lại
   4 ngưỡng `0,10/0,20/0,70/0,90` vì chúng được calibrate trên phân phối expanding.

### 3.3 Về giai đoạn ít dữ liệu 2014–2016 (câu hỏi trong dispatch)

Không phải rủi ro như lo ngại, nhưng vì lý do khác với dự đoán: chuỗi VNINDEX chạy từ
**2000-07-28**, nên tại 2014 expanding đã có ~3.400 phiên; rolling-5y có 1.260, rolling-10y có
2.520 — **tất cả đều vượt xa `MIN_LB=252`**. Vấn đề 2014–2016 không phải "thiếu dữ liệu"
mà là: cửa sổ 5 năm tại 2014 = 2009–2014, **chứa trọn đuôi khủng hoảng 2009** ⇒ phân vị bị neo
vào một regime cực đoan; tới 2016 cửa sổ trượt qua khỏi 2009 ⇒ **phân vị nhảy bậc không do thị
trường đổi mà do dữ liệu rơi khỏi cửa sổ**. Đây là một dạng "viết lại" khác — rolling không xoá
được tính không-ổn-định, chỉ **đổi nó từ dạng "sửa quá khứ" sang dạng "quá khứ rơi khỏi cửa
sổ"**. Với expanding thì không có hiệu ứng rơi-khỏi-cửa-sổ này.

---

## 4. Góc (c) — rolling có giải quyết vấn đề gốc không? **Chỉ một phần**

### 4.1 Rolling *giới hạn* chân trời lây, không khử

Backfill hôm nay phủ **2006 → 2016-07** (VNINDEX_PE NULL → có giá trị). Chiếu lên từng cửa sổ:

| Cửa sổ | Ngày nào còn bị ảnh hưởng bởi backfill 2006–2016/07 |
|---|---|
| **expanding** (hiện tại) | **mọi ngày từ 2006 → nay** ⇒ 101 phiên đổi, trải 2018–2023 ✅ khớp quan sát |
| rolling 10 năm | mọi ngày ≤ **2026-07** ⇒ **vẫn đổi gần như y hệt** (2018/2020/2022/2023 đều nằm trong) |
| rolling 5 năm | mọi ngày ≤ **2021-07** ⇒ 2018 + 2020 **vẫn đổi**; 2022/2023 (36 phiên, 36%) được miễn |

⇒ Ngay cả rolling-5y — cửa sổ ngắn tới mức tôi đánh giá là nguy hiểm cho chất lượng gate
(§3.2) — **cũng chỉ chặn được ~36% số phiên bị viết lại lần này**. Rolling-10y (mức tối thiểu
an toàn) chặn được ~0%. **Đây là lập luận quyết định.**

### 4.2 Kênh corp-action vẫn nguyên vẹn — rolling không chạm tới

`Close`/`MA200` bị re-adjust khi có cổ tức/chia tách (~2–3%/tuần theo đo trước đó). Kênh này
đi vào `f_P3M`, `f_P1M`, `f_MA200`, `close_ew_scaled`, `vol20` — **giá trị của chính điểm dữ
liệu đó bị đổi**, không phải "mẫu số lịch sử bị đổi". Cửa sổ nào cũng không giúp: nếu
`Close[2018-04-02]` bị adjust thì `f_P3M[2018-04-02]` đổi dù rank tính trên 5, 10 hay toàn bộ
lịch sử. Cộng thêm `running_max` (#4 §1) là expanding **theo bản chất khái niệm** (drawdown
đỉnh-mọi-thời-đại) — đổi nó thành rolling là đổi luôn định nghĩa override `dd<-25%`.

### 4.3 Chi phí đổi

Không phải sửa 2 dòng. Chuỗi sản xuất là `ew_v1 → dual_v3 → v3.1 → v3.4b(clean) → DT 4-gate →
macro cap → dt5g_live`. Đổi cửa sổ ⇒ đổi phân phối `r_score` ⇒ phải: hiệu chuẩn lại 4 ngưỡng
classify, đo lại số transitions (hiện 49 — con số này là *đặc trưng nhận dạng* của DT5G), chạy
lại ablation DT4-vs-DT5G, re-pin R3 + mọi backtest, qua quant-skeptic, user duyệt. Đổi lại
được: chặn ~36% (5y) hoặc ~0% (10y) của một lớp sự cố mà §5 chặn được 100% với rủi ro bằng 0.

---

## 5. Khuyến nghị thay thế: bảng công bố BẤT BIẾN (append-only / bi-temporal)

Đây là điều tôi khuyến nghị làm **thay cho** rolling — nhưng cũng chỉ là đề xuất, cần user
duyệt riêng, ngoài phạm vi 3 việc hôm nay.

**Nguyên tắc:** state của một phiên đã công bố là **sự kiện đã xảy ra** (ta đã hành động theo
nó), không phải một ước lượng được phép cập nhật. Publisher chỉ được:
- **append** phiên mới;
- **recompute** một đuôi ngắn chưa chốt (đề xuất: `N = 25` phiên = đúng độ dài cam kết
  `enC/enX` của DT-gate, dưới mức đó state chưa thể coi là chốt);
- **không bao giờ** ghi đè phiên đã chốt — nếu công thức mới cho kết quả khác, ghi thành
  **vintage mới** (thêm cột `asof_date`, hoặc bảng `..._vintage_YYYYMMDD`), không đè bản cũ.

Vì sao đây mới là fix đúng:
- Khử **100%** hiện tượng viết-lại lịch sử ở downstream — kể cả kênh corp-action (§4.2) mà
  rolling không chạm tới.
- **Rủi ro mô hình = 0**: state hôm nay tính y như cũ (vẫn expanding, vẫn dữ liệu tốt nhất hiện
  có), chỉ khác là quá khứ không bị đè.
- **Đúng hơn cho backtest**: label đóng băng = "cái ta biết tại thời điểm đó" ⇒ khử luôn một
  dạng look-ahead tinh vi hiện đang tồn tại (backtest 2018 hiện đang dùng state được tính bằng
  dữ liệu PE backfill năm 2026 — dữ liệu không hề tồn tại vào 2018).
- Cùng triết lý point-in-time đội đã bỏ công xây cho `universe_pit`; nhất quán kiến trúc.

**Việc cần làm nếu user duyệt hướng này** (ước lượng nhỏ): sửa bước publish của
`macro_state_live.py` thành upsert-chỉ-đuôi-25-phiên + thêm cột `asof_date`; ghim 1 snapshot
gốc làm mốc (chính là snapshot của Việc 2 hôm nay); thêm check cảnh báo nếu bản tính mới lệch
bản đã chốt >X phiên (biến sự cố im lặng hôm nay thành alert).

---

## 6. Kết luận & khuyến nghị

| Câu hỏi dispatch | Trả lời |
|---|---|
| (a) Rolling có tốn tài nguyên hơn không? | **Không** — rẻ hơn (63–73 ms vs 84 ms/factor). Cả hai đều <1s. Không phải yếu tố quyết định. |
| (b) Rolling đánh đổi gì về chất lượng gate? | **Có, bất lợi**: mất neo đuôi phân phối, mẫu đuôi mỏng (~126 obs ở decile CRISIS với 5y), chu kỳ VN 4–6 năm > cửa sổ 5 năm, và sinh ra hiệu ứng "quá khứ rơi khỏi cửa sổ" mới. |
| (c) Rolling có giải quyết vấn đề gốc không? | **Không** — chặn ~36% số phiên bị viết lại lần này với 5y, ~0% với 10y; **không chạm** kênh corp-action `Close`/`MA`. |
| **NÊN đổi hay KHÔNG?** | **KHÔNG NÊN ĐỔI.** |
| Nếu vẫn đổi thì bao nhiêu năm? | **10 năm (2.520 phiên)** — mức tối thiểu chứa ≥1 chu kỳ VN đầy đủ ở mọi thời điểm. **Không dùng 5 năm.** Và vẫn phải hiệu chuẩn lại 4 ngưỡng classify + đo lại 49 transitions + re-pin toàn bộ. |
| Thay vào đó nên làm gì? | **Bảng công bố bất biến (append-only + `asof_date` vintage, recompute chỉ 25 phiên đuôi)** — §5. Khử 100% vấn đề, rủi ro mô hình 0, đúng cả kênh corp-action. |

**Giới hạn của phân tích này (nói thẳng):** đây là phân tích cấu trúc + đo chi phí + chiếu chân
trời lây, **chưa có backtest A/B rolling-vs-expanding thật**. Tôi cố ý không chạy: (i) dispatch
giới hạn ở phân tích, không implement; (ii) muốn A/B đúng chuẩn phải hiệu chuẩn lại ngưỡng cho
nhánh rolling rồi mới so — nếu không sẽ so một hệ đã tune với một hệ chưa tune và kết luận vô
giá trị. Nếu user muốn con số thật trước khi quyết, đó là một job riêng (~1 ngày: fork chuỗi
ew_v1/dual_v3 sang thư mục `exp_`, sweep W ∈ {5y, 10y} × hiệu chuẩn ngưỡng, đo transitions +
CAGR/DD/Calmar của R3 dưới mỗi nhánh, LOO theo năm). Khuyến nghị của tôi là **không chi job đó**
— vì §4.1 đã cho thấy kể cả kết quả tốt nhất có thể của rolling cũng không giải quyết được vấn
đề đặt ra.
