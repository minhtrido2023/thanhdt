# Tách "edge thật" khỏi "hiện vật mô hình fill" — chẩn đoán 3 vòng INCONCLUSIVE + kế hoạch mới + kết quả bước 1

**Job:** `Taylor_20260803_021414` · **Ngày:** 2026-08-03 · **Tác giả:** Taylor
**Đầu vào:** finding `lag-fidelity: INCONCLUSIVE` (2026-08-02T18:10:09Z) · verdict
`mike/logs/verify_20260802_173456.log` · module `lag_liquidity_filter.py` (docstring "CHƯA PHÂN RÃ ĐƯỢC")
**Trạng thái:** RESEARCH — **KHÔNG đề xuất thay đổi production trong báo cáo này.**
`LIQ_ZERO_BLOCK` giữ opt-in (`""`), pin R3 giữ **27,24%**.

---

## 0. TL;DR

1. **Chẩn đoán vì sao 3 vòng đều INCONCLUSIVE: câu hỏi bị đặt sai dạng.** "Δ +4,08pp là edge thật
   HAY hiện vật fill" là câu hỏi **nhị phân** trong khi cơ chế thật là **hỗn hợp có tỷ lệ**, và —
   quan trọng hơn — **cả ba vòng đều so sánh mô phỏng-với-mô phỏng mà không có một dự đoán phân
   biệt nào được đăng ký trước**. Mọi bằng chứng đã thu thập đều **tương thích với CẢ HAI** giả
   thuyết. Thêm dữ liệu cùng loại sẽ cho INCONCLUSIVE lần thứ tư.
2. **Đã chạy ngay bước rẻ nhất (T3, phân rã sổ lệnh, KHÔNG cần backtest mới)** — chính phép đo mà
   docstring của module tự yêu cầu. Kết quả **bác bỏ cách diễn giải "capital velocity"** vốn là nền
   của cả hai lần đính chính trước:
   - Vòng quay vốn **CHẬM HƠN** ở chân sửa lỗi (5,62x/năm vs 6,28x/năm) — **không phải** "vốn chảy
     nhanh hơn".
   - Δ NAV +483,9B đến từ **lợi nhuận mỗi chu kỳ triển khai vốn tăng 3,549% → 4,582%**
     (+1,03pp/chu kỳ), trong đó **81% chỉ là do KHÔNG rót vốn vào nhóm mã bị chặn** — nhóm này ở
     L0 hút **1.690B vốn luỹ kế** để sinh **−1,77%/chu kỳ**.
   - Kiểm tra compounding khớp cơ học: `(1+r₁)^70 / (1+r₀)^78 = 1,51x` vs tỷ lệ NAV cuối thực đo
     **1,48x** ⇒ phân rã này giải thích được gần trọn Δ, không phải kể chuyện.
3. **Hệ quả về khung khái niệm (quan trọng nhất):** L1 là **siết chặt nghiêm ngặt** mô hình fill của
   L0 (chỉ có thể đặt `daily_max=0` ở chỗ trước đó **vô hạn**, không bao giờ nới). Một "hiện vật do
   mô hình fill quá dễ dãi" **không thể** sinh ra từ chân dễ dãi HƠN. Nên câu trả lời đúng không
   phải "edge" cũng không phải "artifact" mà là: **L0 mô phỏng một đường live KHÔNG đi được**
   (mua trọn size mã không đo được thanh khoản trong 1 phiên), L1 mô phỏng đường live **thật sự có**.
   Δ là **sửa sai số đo**, không phải alpha mới.
4. **Kế hoạch 5 phép thử có tiêu chí PASS/FAIL đăng ký TRƯỚC** (§4). Bước quyết định (T1) **đã chạy
   trong dispatch này**, kết quả ở §5.
5. **Phê phán chính đề xuất cũ của Taylor (NAV 5–10B): CHƯA đủ dứt điểm** — 4 lý do ở §3.2, và cách
   sửa (thang liều + manipulation check + đăng ký trước) ở §4.

---

## 1. Vì sao 3 vòng trước không giải quyết được câu hỏi — chẩn đoán phương pháp

Không phải thiếu dữ liệu. Cả 3 vòng đều **PASS** mọi kiểm tra vật lý (self-check 0 VND, IS/OOS,
LOO 13/13, DSR≈1,0, recompute độc lập khớp từng chữ số). Vẫn INCONCLUSIVE vì 4 khiếm khuyết
**thiết kế**:

| # | Khiếm khuyết | Hệ quả |
|---|---|---|
| **D1** | **Câu hỏi nhị phân cho một cơ chế hỗn hợp.** "Edge thật HAY hiện vật" giả định hai khả năng loại trừ nhau. Thực tế cả hai kênh cùng tồn tại; dữ liệu chỉ đo được **tỷ lệ**. | Mọi kết quả đều "chưa loại trừ được vế kia" ⇒ INCONCLUSIVE vĩnh viễn. |
| **D2** | **Không có dự đoán phân biệt đăng ký trước.** Không vòng nào tuyên bố trước "nếu H_artifact đúng thì con số X phải nằm ở khoảng Y". | Bằng chứng thu được **tương thích với cả hai** giả thuyết ⇒ không falsify được cái nào. |
| **D3** | **So sánh mô phỏng-với-mô phỏng.** Cả L0 và L1 dùng chung một mô hình fill (`%ADV/ngày`) chưa từng được neo vào fill THẬT. | Skeptic luôn có đường lùi hợp lệ: "cả hai chân đều là mô hình". |
| **D4** | **Không có manipulation check.** Khi đổi một tham số để "gỡ ràng buộc capacity", không ai kiểm tra xem ràng buộc **có thật sự được gỡ không**. | Một phép thử null có thể là do can thiệp không ăn, chứ không phải giả thuyết sai. |

**Kết luận chẩn đoán:** vòng 4 phải (i) hỏi **tỷ lệ**, không hỏi nhị phân; (ii) **đăng ký trước** dự
đoán phân biệt; (iii) có ít nhất **một neo ngoài mô phỏng**; (iv) có **manipulation check** cho mọi
can thiệp.

---

## 2. Đọc lại cơ chế từ code thật (skill quant-research §1)

`simulate_holistic_nav.py:1199-1216` — mô hình fill:

```python
remaining_value = entry["target_value"] - entry["filled_cost"]
daily_max = remaining_value                       # ← MẶC ĐỊNH: KHÔNG trần
if liquidity_volume_pct is not None and liquidity_lookup is not None:
    liq = liquidity_lookup.get((tk, today))
    if liq and liq > 0:
        daily_max = liq * liquidity_volume_pct    # trần %ADV bình thường
    elif liquidity_require_positive:
        daily_max = 0.0                           # ← L1 CHỈ thêm nhánh này
buy_value = min(remaining_value, daily_max, _bp)
```

`simulate_holistic_nav.py:1248-1306` — hoàn tất/bỏ dở: `done` khi `fill_pct ≥ 0.95` **hoặc**
`days_filling ≥ max_fill_days(5)`; nếu `fill_pct < min_fill_pct` ⇒ **ABANDONED_REFUND** (bán lại
phần đã mua theo giá hôm đó, hoàn tiền về sổ).

**Ba hệ quả then chốt, đọc thẳng từ code:**

- **(a) Vốn KHÔNG bị giữ chỗ.** `cash` chỉ giảm khi có fill thật. Một lệnh bị chặn (`daily_max=0`)
  **không chiếm vốn**, chỉ chiếm một chỗ trong `pending_entries`. ⇒ "chặn mã" **giải phóng vốn ngay**.
- **(b) L1 ⊂ L0 về độ dễ dãi của mô hình fill.** `liquidity_require_positive` **chỉ** biến một
  `daily_max` **vô hạn** thành **0**. Nó không nới bất kỳ ràng buộc nào. ⇒ **Một hiện vật kiểu "mô
  hình cho fill dễ hơn thực tế" không thể sinh ra từ chân bị siết chặt hơn.** Đây là lập luận
  logic, không cần số liệu.
- **(c) Chỗ DUY NHẤT mô hình fill "gian lận" nằm ở L0**, đúng nhánh `else` — mã không đo được ADV
  mua **trọn size trong 1 phiên**. Đường live chặn nhóm này ở **cả hai tầng**
  (`lag_filter_illiquid` từ 07-21, `cap_lag_orders` fail-closed từ 07-22).

⇒ **Khung đúng:** không phải "L0 = thực tế, L1 = L0 + edge". Mà là **"L0 = mô phỏng một đường live
không đi được; L1 = mô phỏng đường live đi được"**. Δ là **hiệu chỉnh sai số đo**.

---

## 3. Phê phán các đề xuất đang có

### 3.1 Đề xuất "truy vết ENTRY_FILL/ABANDONED_REFUND" (quant-skeptic recommend #1)
**Đúng hướng, nhưng chưa đủ nếu chỉ đếm.** Đếm `ENTRY_FILL 5166→9496`, `ABANDONED 1001→1603` là
bằng chứng **tương thích với cả hai** giả thuyết (khiếm khuyết D2). Đã nâng cấp thành phép **phân
rã có ràng buộc cộng** (§5.1): buộc các cấu phần phải **cộng lại ra đúng Δ NAV** — khi đó không còn
chỗ cho diễn giải tuỳ ý.

### 3.2 Đề xuất "chạy L0/L1 ở NAV 5–10B" (bước 1 của chính Taylor) — **CHƯA dứt điểm**
Ý tưởng đúng (gỡ ràng buộc capacity), nhưng ở dạng **một điểm đơn** thì quant-skeptic vẫn bác được
hợp lệ, vì 4 lý do:

| | Vấn đề | Sửa |
|---|---|---|
| **C1** | **Không có dose-response.** Một điểm 5B không phân biệt được "capacity không phải nguyên nhân" với "5B tình cờ cho kết quả đó". Skill §10 nói rõ: thang liều đơn điệu mạnh hơn mọi p-value ở N nhỏ. | Chạy **thang**, không chạy một điểm. |
| **C2** | **Không có manipulation check.** Nếu ở 5B tỷ lệ abandoned **vẫn cao**, thì capacity **chưa hề** được gỡ — kết quả null vô nghĩa (D4). | Bắt buộc báo cáo `abandoned%` và `fill_rate` ở **mọi rung**; nếu không sụp ở đầu lỏng ⇒ **phép thử VÔ HIỆU**, không kết luận. |
| **C3** | **Đổi NAV làm nhiễu nhiều thứ cùng lúc** — số vị thế đồng thời, mức chạm trần 12, tương tác với sổ BAL/CAPIT/parking, mức độ tập trung. Không phải can thiệp một biến. | Dùng **`liquidity_volume_pct`** làm knob chính: nó tác động **đúng và chỉ** vào tốc độ fill. Giữ NAV-ladder làm knob **trực giao** để kiểm chứng chéo. |
| **C4** | **Vẫn trả lời câu hỏi nhị phân** (D1). Nếu Δ teo 60% thì kết luận là gì? | Đăng ký trước **ba vùng kết quả** với hành động tương ứng (§4.1) — không để khoảng trống diễn giải. |

**Kết luận:** giữ NAV-ladder nhưng **hạ ưu tiên xuống T2**; knob quyết định là `%ADV/ngày` (T1).

---

## 4. KẾ HOẠCH — 5 phép thử, tiêu chí PASS/FAIL đăng ký TRƯỚC

Giả thuyết cần tách (viết lại cho **đo được**, thay vì nhị phân):

- **H_A — "hiệu chỉnh sai số đo"**: Δ chủ yếu do L0 rót vốn vào nhóm mã live **không mua được**, ở
  mức size **không fill nổi**. ⇒ L1 là **ước lượng tốt hơn** cho P&L live.
- **H_B — "hiện vật capacity"**: Δ chủ yếu do chênh lệch **khả năng hấp thụ** của sổ 25B giữa hai
  chân (L1 bỏ dở nhiều hơn ⇒ profile vốn khác ⇒ số đẹp hơn một cách ngẫu nhiên). ⇒ Δ **không**
  chuyển sang live.
- **Đo bằng tỷ lệ** `s = phần Δ quy được cho H_A / Δ tổng`, không đo bằng "đúng/sai".

### T1 — THANG CAPACITY qua `%ADV/ngày` (**quyết định, đã chạy trong dispatch này**)
Quét `liquidity_volume_pct` của sổ LAG: **0,05 → 0,20 (gốc) → 1,00**, chạy **cả hai** chân ở mỗi rung.
Chỉ đổi **một** biến; mọi thứ khác giữ nguyên (snapshot `asof20260729_postrestate`, NAV 50B, threads=1, `$DNA_PYEXE`).

- **Manipulation check (BẮT BUỘC, kiểm trước khi đọc Δ):** ở rung 1,00 tỷ lệ `abandoned` phải
  **sụp rõ rệt** ở **cả hai** chân (mục tiêu < ~20%, so với 48,5%/63,7% ở rung gốc).
  **Không sụp ⇒ phép thử VÔ HIỆU**, cấm kết luận từ Δ.
- **Đăng ký trước — 3 vùng kết quả:**

| Δ(CAGR) tại rung lỏng 1,00 | Kết luận | Hành động |
|---|---|---|
| **≥ +2,0pp** | H_A trội (Δ **không** do capacity) | Đủ điều kiện chuyển sang T4 (neo ngoài) rồi mới bàn pin |
| **+0,5 … +2,0pp** | hỗn hợp | Báo cáo **tỷ lệ** `s`, KHÔNG re-pin; chỉ giữ filter (đã đúng về logic) |
| **≤ +0,5pp** | H_B trội — Δ **là** hiện vật capacity | **Đóng hướng re-pin vĩnh viễn**, ghi vào registry là dead-end |

  (+0,5pp chọn làm mốc vì đó là bậc độ lớn của **riêng** phần tác động trực tiếp ước từ T3 khi
  capacity không còn ràng buộc; ≥+2,0pp = một nửa Δ gốc.)
- **Đơn điệu (skill §10):** Δ(0,05) ≤ Δ(0,20) ≤ Δ(1,00) hay ngược lại — hình dạng thang phải nhất
  quán với vùng kết luận; thang **không đơn điệu** = tín hiệu nhiễu, hạ độ tin cậy một bậc.
- **Effort:** ~5 chân × ~10–15 phút. **ĐÃ CHẠY** (§5.2).

### T2 — THANG NAV (knob trực giao, kiểm chứng chéo)
NAV ∈ {5, 10, 25, 50, 100}B, cả hai chân. Cùng bộ tiêu chí + manipulation check như T1.
**Giá trị:** hai knob độc lập cho **cùng** kết luận là bằng chứng mạnh hơn nhiều một knob; hai knob
**mâu thuẫn** ⇒ dừng, không kết luận (và đó cũng là một phát hiện thật).
**Effort:** ~10 chân, ~30 phút. **Ưu tiên 2** (chạy sau khi T1 có kết quả).

### T3 — PHÂN RÃ SỔ LỆNH CÓ RÀNG BUỘC CỘNG (**đã chạy**, §5.1)
Không cần backtest mới. Ràng buộc kiểm chứng: các cấu phần phải **tái tạo lại được** tỷ lệ NAV cuối
qua compounding (đạt: 1,51x tính vs 1,48x thực).
**PASS/FAIL:** nếu compounding **không** khớp trong ±15% ⇒ phân rã sai, bỏ.
**Effort:** ~30 phút. **ĐÃ XONG.**

### T4 — NEO NGOÀI MÔ PHỎNG: đối chiếu mô hình fill với fill THẬT (phá thế sim-vs-sim, **D3**)
Đây là phép thử **duy nhất** không tuần hoàn. Lấy toàn bộ lệnh mua sổ LAG thật của SpaceX+ZaloPay từ
2026-07-01 (`data/execution_logs/dnse_raw_*.jsonl`, **lọc `accountNo`** — coding_guidelines §12),
với mỗi lệnh tính `filled_value / (ADV_ngày_đó × 0,20)`.
- **PASS (mô hình fill bảo thủ hoặc đúng):** trung vị tỷ số ≥ 1,0 ⇒ thực tế fill **ít nhất** bằng
  giả định engine ⇒ mô hình fill không phải nguồn lạc quan.
- **FAIL:** trung vị < 0,5 ⇒ engine giả định fill **dễ gấp đôi** thực tế ⇒ **mọi** số CAGR của **cả
  hai** chân đều lạc quan, và câu hỏi Δ trở thành thứ yếu.
- **Giới hạn phải nói thẳng:** N nhỏ (~1 tháng, vài chục lệnh), lệnh live bị `cap_lag_orders` giới
  hạn sẵn nên **chệch về phía dễ fill** — đây là **kiểm tra bậc độ lớn**, không phải ước lượng.
  Ghi rõ N là **số lệnh độc lập**, không phải số dòng JSONL (skill §4).
**Effort:** ~1 giờ. **Ưu tiên 3.** Không chặn T1/T2.

### T5 — KHUNG QUYẾT ĐỊNH (chạy bất kể T1–T4 ra gì)
Câu hỏi kinh doanh **không** phải "Δ có thật không" mà là **hai** câu tách rời:
1. **Có giữ bộ lọc không?** → **CÓ, vô điều kiện.** Live đã chặn nhóm này ở 2 tầng từ 07-21/07-22
   vì lý do độc lập (không mua được thì đừng đặt mục tiêu). Kết quả T1–T4 **không** đổi câu này.
2. **Pin số nào?** → chỉ câu này phụ thuộc T1–T4. Nếu không tách được, **giữ 27,24%** và ghi rõ nó
   là **CẬN DƯỚI có thiên lệch đã biết** (nó mô phỏng việc mua nhóm mã live không mua được, và
   nhóm đó lỗ −1,77%/chu kỳ ⇒ 27,24% **thấp hơn** kỳ vọng của hệ thống live thật).
**Effort:** 0 (đã viết ở đây).

### Thứ tự ưu tiên
**T3 (xong) → T1 (xong) → T2 → T4 → T5.** T2/T4 độc lập nhau, chạy song song được.

---

## 5. KẾT QUẢ ĐÃ CHẠY TRONG DISPATCH NÀY

### 5.1 T3 — phân rã sổ lệnh (từ 2 CSV audit của A/B 2026-08-02, không chạy backtest mới)

Script: `ledger_attrib.py` (kèm thư mục này). Nguồn:
`..._wtnamecap_exp_L0_legacy_univpit.csv` (27,24%) và `..._liqzblag_exp_L1_liqzb_univpit.csv` (31,32%).

**Tổng quan sổ LAG**

| | L0 (control) | L1 (`LIQ_ZERO_BLOCK=lag`) |
|---|---|---|
| NAV cuối (toàn hệ) | 1.006,33B | 1.490,21B (**Δ +483,89B**) |
| Vị thế LAG: tổng / hoàn tất / bỏ dở | 2.066 / 1.065 / **1.001 (48,5%)** | 2.516 / 913 / **1.603 (63,7%)** |
| Vốn triển khai luỹ kế (vị thế hoàn tất) | 12.422B | 17.410B |
| P&L thực hiện | 440,9B | 797,7B |
| NAV sổ LAG trung bình | 158,8B | 248,5B |
| **Vòng quay vốn** | **6,28x/năm** | **5,62x/năm** |

**Phân rã theo tập mã**

| Nhóm | Số mã | L0 | L1 |
|---|---|---|---|
| **BỊ CHẶN** (có ở L0, hoàn toàn vắng ở L1) | 58 | 106 vị thế, vốn 1.690B, **P&L −29,88B** | — (không tồn tại) |
| Có ở **cả hai** | 493 | 1.960 vị thế, vốn 11.430B, P&L 474,95B | 2.367 vị thế, vốn 18.491B, P&L 793,77B |
| Chỉ có ở L1 | 88 | — | 149 vị thế, P&L +16,27B |

**Phân rã lợi nhuận mỗi chu kỳ triển khai vốn** (đây là cấu phần giải thích được Δ):

| | LN/chu kỳ |
|---|---|
| L0 — tất cả | **3,549%** |
| ↳ *riêng nhóm bị chặn* (vốn 1.690B) | **−1,768%** |
| L0 — sau khi bỏ nhóm bị chặn | **4,387%** |
| L1 — tất cả | **4,582%** |
| **(a) bỏ nhóm bị chặn** | +0,84pp = **81% tổng cải thiện** |
| **(b) phần còn lại (chất lượng thay thế)** | +0,20pp = **19%** |

**Kiểm tra compounding (ràng buộc cộng):** `(1+4,582%)^70 / (1+3,549%)^78 = 1,51x` so với tỷ lệ NAV
cuối thực đo **1,48x** ⇒ khớp trong 2% ⇒ phân rã hợp lệ (PASS tiêu chí ±15% của T3).

**Ba kết luận từ T3:**

1. **Cách diễn giải "capital velocity" BỊ BÁC.** Vòng quay vốn **giảm** (6,28 → 5,62x/năm). Δ đến
   từ **lợi nhuận mỗi chu kỳ cao hơn**, không phải từ quay vòng nhanh hơn. *(Đây là lần đính chính
   thứ BA cho cơ chế của module — hai bản trước, "không có trần slot" và "trần 12 BIND", đã bị
   REFUTED; bản thứ ba "vốn chảy nhanh sang event kế tiếp" nay cũng sai ở cách diễn đạt: đúng là
   "vốn không bị hút vào một cái bẫy lỗ", không phải "chảy nhanh hơn".)*
2. **81% của cải thiện là do KHÔNG rót 1.690B vào một rổ sinh −1,77%/chu kỳ.** Đây là tác động
   **trực tiếp**, quy được về từng mã, không phụ thuộc giả định thay thế. 19% còn lại mới là
   "chất lượng vốn được giải phóng".
3. **Nghịch lý biểu kiến đã giải:** L1 bỏ dở nhiều hơn (63,7% vs 48,5%) **và vẫn lời hơn**. Vì
   ABANDONED không phải mất tiền (hoàn lại sổ, P&L nhóm bỏ dở nhỏ: 4,2B/12,3B) — nó chỉ là **chi
   phí ma sát** của việc thử nhiều ứng viên hơn. Tỷ lệ bỏ dở cao là **triệu chứng**, không phải
   **nguyên nhân** của Δ. Đây chính là chỗ trực giác "abandonment tăng ⇒ artifact" đi sai.

### 5.2 T1 — thang capacity

> Chân đang chạy trong dispatch này; kết quả + kiểm tra manipulation ghi ở
> `T1_RESULTS.md` cùng thư mục (và trên bus). Chân hợp lệ bắt buộc: rung 0,20 / L0 phải tái lập
> **27,24% / 1,81 / −18,4% / 1,48 / 1.006,33B**; không tái lập ⇒ toàn bộ T1 vô hiệu.

---

## 6. Kỷ luật đã tuân thủ / phải nói thẳng

- **Production KHÔNG bị đụng** (skill §14): `git status` sạch trên `pt_v23_audit_2014.py`,
  `simulate_holistic_nav.py`, `lag_liquidity_filter.py`. Bản sao nghiên cứu
  `pt_v23_lagcap_research.py` khác production **đúng 1 dòng đã ghi chú** (`liquidity_volume_pct`
  đọc từ env `LAG_LIQ_PCT`, mặc định 0.20 = y hệt).
- **§8 tên file:** mọi chân gắn `EXP_TAG=cap_pXXX_LY` ⇒ không chân nào ghi đè CSV canonical.
- **Vintage:** toàn bộ T1/T3 trên `bq_cache_asof20260729_postrestate` — **cùng** vintage số pin.
  Không so số nào của báo cáo này với số vintage khác.
- **N thật (skill §4):** T3 đo trên **58 mã bị chặn / 106 vị thế**, nhưng đây **không** phải mẫu
  thống kê để test — nó là **kế toán toàn bộ tổng thể** (mọi vị thế của cả hai chân), nên không
  cần p-value. T1 là thang cơ học, N=1 chuỗi/rung — bằng chứng nằm ở **hình dạng thang**, không ở
  ý nghĩa thống kê.
- **KHÔNG tự tuyên bố CONFIRMED.** Không đề xuất re-pin, không đề xuất bật `LIQ_ZERO_BLOCK` mặc
  định. Mọi khuyến nghị production (nếu có, sau T2/T4) phải qua `bin/verify_finding.sh`.
- **Đối chiếu finding kề (skill §12):** báo cáo này **mâu thuẫn có chủ đích** với cách diễn giải
  "capital velocity" trong docstring `lag_liquidity_filter.py:23-24` và trong finding 07-21. Cơ
  chế đúng là **tránh bẫy lỗ**, không phải **tăng tốc độ vòng quay** — số liệu §5.1 là căn cứ.
  Docstring cần cập nhật, nhưng đó là thay đổi file production ⇒ **không tự sửa trong job này**.
- **Quan sát ngoài phạm vi (báo để không ai đọc nhầm):** job song song `Taylor_20260803_015850`
  (thư mục `research/lag_quality_20260803/`) khai trong `run_leg.sh` rằng chân L0 "PHẢI tái lập
  27,24%", nhưng chân L0 của nó in **28,86%** — vì nó chạy với `LAG_ADV_BASIS=price` (mặc định mới),
  tức chân đối chứng của nó tương ứng **L2** của bảng 08-02, không phải L0. Số không sai; **điều
  kiện hợp lệ ghi trong header script mới là thứ cần sửa**. Không đụng vào file của job đó.
