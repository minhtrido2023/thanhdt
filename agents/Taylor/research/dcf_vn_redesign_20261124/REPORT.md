# DCF phù hợp thị trường Việt Nam — thiết kế lại & kiểm định (job Taylor_20261124_140534)

Taylor · 2026-11-24 · CHỈ NGHIÊN CỨU + ĐỀ XUẤT (không sửa `dcf_valuation.py`, không wire). **Chưa qua quant-skeptic — không
được coi là CONFIRMED.** Tiêu chí khoá trước ở `PRELOCK.md` (commit `b8fe8d1f8`, trước khi chạy mô hình).

## 0. Kết luận trước

1. **Theo đúng tiêu chí khoá trước: CHƯA có mô hình nào đạt đồng thời (1) và (2).**
   - Không mô hình **mù giá** nào đạt (1) "cắt giá trong 36 tháng" (ngưỡng ≥75% chung, ≥60% mỗi phía). Tốt nhất 68% (IS) /
     59% (OOS). Phía "đắt" (tâm < giá) chỉ cắt 44–50% ở OOS.
   - (2) đạt một phần: IC 36 tháng dương, CI không chứa 0 ở cả IS và OOS; nhưng phép thử sự kiện "tâm cắt lên giá" **sai
     chiều ở IS**, và 4 ca user không mô hình nào đạt 5/5 (tốt nhất 4/5).
2. **Nguyên nhân gốc của engine hiện tại là CƠ SỞ DÒNG TIỀN FCFE, không phải r / g_T / shrink.** Phần riêng của FCFE so với
   mô hình thu nhập thặng dư (RIM) có phương sai gấp 3 lần chính RIM và IC = +0,004 (IS) / −0,095 (OOS): nhiễu thuần.
   Engine còn bỏ trống 58% universe và xếp "luôn đắt" đúng nhóm doanh nghiệp đang đầu tư mở rộng.
3. **Mô hình đề xuất thay thế = RIM-VN (ký hiệu D0):** giá trị = vốn chủ sở hữu + giá trị hiện tại của lợi nhuận thặng dư,
   với ROE **xuyên chu kỳ** (trung vị 5 năm của chính mã) × vốn chủ **hiện tại**, fade 10 năm. So với engine FCFE: độ phủ
   42% → phủ thêm nhóm tài chính và nhóm FCFE âm, độ phân tán giảm một phần ba, IC 36T OOS 0,042 → 0,255, 4 ca user 1/5 → 3/5.
4. **Cái cản tiêu chí (1) là bản chất thị trường, không phải tham số:** ~51% phương sai log(tâm/giá) là lệch **bền theo
   từng mã**. Nhóm "luôn đắt" theo RIM (ROE xuyên chu kỳ 6%, không cổ tức) thật sự cho lợi suất 36T âm (−0,02 log) nhưng giá
   trôi xuống chậm chứ không về tâm. Muốn tâm cắt giá thì phải hiệu chỉnh theo premium lịch sử của chính mã (biến thể
   G1: cắt 85%/85%) — nhưng đó là **dùng giá quá khứ**, và nó **làm mất giá trị chọn mã** (danh mục vùng-mua CAGR IS
   9,3% → 2,3%).
5. **Tạo giá trị (4):** danh mục "vùng mua" theo RIM-VN (giá ≤ 0,8×tâm, rating 8L ≤ 3) đạt CAGR 15,4% so với universe
   EW 9,2% (2014-06→2026-10, pin0%, đã trừ phí 0,1%/chiều), thắng EW 10/13 năm, cả IS lẫn OOS. **Nhưng không hơn rổ
   E/P đối chứng ở OOS** (20,6% vs 21,2%) và DSR phần vượt trội = 0,79 < 0,95 ⇒ theo luật khoá trước: **đây là lens
   định giá tốt hơn engine cũ, CHƯA chứng minh được alpha vượt 1/PE.**

Hai câu trả lời trên (3) và (4) kéo ngược nhau, nên đề xuất kiến trúc **hai lớp** (§6) thay vì một con số tâm duy nhất.

## 1. Dữ liệu và khung PIT

- BCTC quý `ticker_financial` (cache local 23/11), known_date = cột `time` (ngày công bố). Lưới **tháng** 2008-01→2026-11:
  168.565 dòng (mã, tháng), 1.252 mã. Giá trước 2013 kéo từ `tav2_bq.ticker` (phiên cuối tháng).
- **Không dùng `OShares`, `PB`, `PE` vendor.** Registry ghi `OShares` là TRAP (bị restate); kiểm tra thô thấy `PB` vendor
  cũng lệch theo (VCS 2012-02: Price/BVPS = 0,67 nhưng `PB` = 0,39). Toàn bộ mô hình chạy trong **không gian tỉ số**:
  B/P = BVPS/Price tại ngày công bố, trượt theo Close điều chỉnh; ROE = `ROE_Trailing`. Không nhân thêm hệ số điều chỉnh
  nào (không double-count). 1.957/57.109 dòng BCTC (3,4%) bị "debounce" một quý vì BVPS nhảy >35% (lệch split một dòng).
- Universe: `universe_pit.in_universe` đúng phiên, 2014-01 trở đi. IS = as-of 2014-01→2019-12 (18.493 dòng có đủ 36
  tháng, 499 mã); OOS = 2020-01→ (18.606 dòng, 600 mã). **N độc lập:** theo mã ≈ 500–600 cụm; theo thời gian chỉ 2 khối
  36 tháng không chồng lấn mỗi era ⇒ sức mạnh theo thời gian yếu, mọi CI dưới đây là bootstrap **cụm theo mã** (B=300).
- Nhãn = lợi suất tương lai từ Close. Không dùng `profit_*`. Self-check PIT: `fin_time ≤ known ≤ time` trên 168.565 dòng.

## 2. Chẩn đoán nguyên nhân gốc engine FCFE hiện tại (`out/diag.json`)

| Câu hỏi | Đo được |
|---|---|
| Engine ra FV ở bao nhiêu dòng universe? (17.946 dòng mã-quý, 2014Q1–2026Q3) | **42,4%**. Bị loại: cổng CFO 3Y ≤ 0 25,9% · FCFE 3Y ≤ 0 16,3% · tài chính 13,3% · thiếu lịch sử 1,9% |
| log(FV_engine/P) = log(V_RIM/P) + phần riêng FCFE: phương sai từng phần (n=7.342) | engine 1,58 · RIM 0,60 · **phần riêng FCFE 1,82**; tương quan engine–RIM chỉ 0,18 |
| Phần riêng FCFE có dự báo lợi suất 36T không? | IC = **+0,004 (IS) / −0,095 (OOS)** ⇒ nhiễu, OOS còn ngược chiều. Cùng mẫu, RIM: 0,157 / 0,236 |
| Nhóm "luôn đắt" của engine (29,6% mã, FV/P trung vị < 0,75) là ai? | capex/CFO 5 năm trung vị **0,56** (nhóm luôn-rẻ 0,26) · P/B 1,63 · GTGD 2,7 tỷ/phiên · D/E 0,66 · lợi suất 36T trung vị **+0,13** |
| Nhóm "luôn rẻ" (45,1% mã, FV/P > 1,33)? | capex thấp · P/B 0,98 · ROE xuyên chu kỳ 10% · GTGD 1,1 tỷ · lợi suất 36T **+0,09** (thấp hơn nhóm "luôn đắt") |
| Nhóm engine KHÔNG ra FV (phi tài chính)? | lợi suất 36T trung vị 0,03 vs 0,15 nhóm có FV; trong nhóm này RIM vẫn xếp hạng được (IC36 0,18) |
| Tỉ trọng phương sai nằm GIỮA các mã | engine 48% · RIM D0 51% · neo P/B riêng 24% · G1 21% |

Đọc: (i) FCFE = CFO − capex phạt doanh nghiệp **đang đầu tư** và thưởng doanh nghiệp không tái đầu tư; ở VN nhóm đầu
lại là nhóm thanh khoản cao, tăng trưởng thật. (ii) Đổi r, g_T, shrink chỉ dời mức (đã đo 11/11, và lặp lại ở đây: r thích
nghi lãi suất đổi tỉ lệ cắt ≤ 1 điểm %, IC ≤ 0,005). (iii) Thiếu neo sổ sách + thiếu hồi quy ROE về chu kỳ là hai mảnh mà RIM
bổ sung. (iv) Nhưng **lệch bền theo mã không biến mất** khi đổi sang RIM (48% → 51%) — đây là giới hạn của mọi DCF dùng
tham số chung.

## 3. Họ mô hình và kết quả theo tiêu chí (1)–(2)

Cấu trúc chung RIM: V/B = 1 + Σ₁..₁₀ (ROE_t − r)·B_{t−1}/(1+r)^t + terminal; B tăng theo g_t = min(ROE_t × tỉ lệ giữ lại,
15%) fade về g_T. Khác nhau ở đường ROE:

| Ký hiệu | Mô tả | Mù giá? |
|---|---|---|
| A | Engine production FCFE 3 năm, domestic_v2 (đối chứng) | có |
| B | RIM-naive: ROE = TTM, giữ nguyên, không fade | có |
| C | ROE = trung vị 5 năm của mã, không fade | có |
| **D0** | ROE trung vị 5 năm, fade 10 năm về r + 0,4×(ROE − r) | có |
| D | D0 + shrink Bayes về trung vị ngành + pha 1 đi từ ROE TTM | có |
| H *(sau prelock)* | D + độ bền κ theo mã = (ROE_min5Y − r)/(ROE − r) + trộn 50% TTM cho mã không chu kỳ | có |
| E | Trung vị P/B 5 năm của chính mã × B | **không** |
| F | Trung bình hình học D và E | **không** |
| G1 / G05 *(sau prelock)* | D0 × premium riêng: trừ λ × trung vị 60 tháng trước của log(V/P) của mã, λ = 1 / 0,5 | **không** |

Bảng chính (r cố định 12,25% trừ khi ghi khác; IS / OOS). "Cắt 36T" = tỉ lệ (mã, tháng) mà tâm trượt và giá đổi phía
trong 36 tháng sau. Nguồn: `out/metrics.csv`, `out/metrics_post.csv`, `out/cases*.csv`, `out/bt_summary.csv`.

| Mô hình | Cắt 36T | phía đắt | phía rẻ | mã không bao giờ cắt | IQR log(V/P) | IC 36T [CI95 cụm mã] | 4 ca (/5) | S1 CAGR |
|---|---|---|---|---|---|---|---|---|
| A engine FCFE | 53% / 50% | 54 / 49 | 52 / 50 | 7,1% | 1,48 / 1,50 | 0,112 [0,04–0,18] / 0,042 [−0,03–0,12] | 1 | 9,6% / 16,3% |
| B RIM-naive | 68% / 59% | 62 / 47 | 75 / 82 | 5,5% | 1,44 / 1,53 | 0,094 [0,04–0,15] / 0,220 [0,16–0,27] | 4 | 8,8% / 19,4% (r slow) |
| C | 49% / 43% | 46 / 32 | 53 / 63 | 17,9% | 1,48 / 1,47 | 0,125 [0,07–0,19] / 0,236 [0,18–0,30] | 4 | – |
| **D0 RIM-VN** | 63% / 55% | 60 / 44 | 68 / 75 | 10,0% | 0,99 / 1,02 | **0,155 [0,10–0,21] / 0,255 [0,19–0,32]** | 3 | **9,3% / 20,6%** |
| D | 66% / 56% | 61 / 45 | 74 / 82 | 10,5% | 0,87 / 0,90 | 0,133 [0,08–0,19] / 0,242 [0,19–0,30] | 3 | – |
| H *(sau prelock)* | 68% / 59% | 62 / 49 | 78 / 87 | 10,8% | 0,84 / 0,90 | 0,129 [0,07–0,18] / 0,254 [0,20–0,31] | 3 | 4,7% / 22,5% |
| E neo P/B riêng | 86% / 86% | 88 / 90 | 83 / 80 | 0,3% | 0,57 / 0,60 | 0,135 [0,06–0,19] / 0,209 [0,15–0,28] | 3 | 1,8% / 15,8% |
| F (D⊕E, r thích nghi) | 76% / 71% | 76 / 66 | 77 / 80 | 2,9% | 0,66 / 0,68 | 0,153 [0,07–0,22] / 0,235 [0,18–0,30] | 3 | 4,4% / 20,0% |
| G05 *(sau prelock)* | 77% / 71% | 74 / 62 | 82 / 87 | 2,0% | 0,77 / 0,76 | 0,165 [0,09–0,23] / 0,222 [0,16–0,29] | 3 | 5,9% / 17,6% |
| **G1** *(sau prelock)* | **85% / 86%** | 85 / 83 | 86 / 89 | 0,3% | 0,71 / 0,69 | 0,162 [0,09–0,21] / 0,166 [0,11–0,24] | 4 | 2,3% / 14,9% |
| Universe EW · VNINDEX giá | | | | | | | | 5,4% / 12,4% · 8,9% / 9,5% |

Đối chiếu ngưỡng khoá trước:
- **(1):** chỉ E và G1 đạt ở cả IS và OOS — cả hai đều dùng giá quá khứ. F/G05 đạt IS, trượt OOS (71% < 75%). Mọi mô
  hình mù giá trượt. Tâm không "bám giá" theo quý ở bất kỳ mô hình nào (corr ΔlogV–ΔlogP ≤ 0,10), nên E/G1 cắt nhiều là do
  **mức** được neo theo premium riêng của mã, không phải do tâm chạy theo giá ngắn hạn.
- **(2a) IC:** mọi biến thể RIM có IC36 > 0 với CI không chứa 0 ở cả hai era; engine A thì CI OOS chứa 0. Trễ thêm 1
  quý: D 0,128 / 0,233 (gần như không đổi) ⇒ không sống nhờ dữ liệu sớm.
- **(2b) hội tụ:** β 36T của D0 = 0,17 / 0,19 (engine 0,06 / 0,01). Gap ratio với tâm **đứng yên** vẫn > 1 (1,41 / 1,12):
  giá không đi về tâm của 3 năm trước; giao cắt đến từ tâm trượt.
- **(2c) sự kiện — TRƯỢT ở IS.** D0, lợi suất vượt trội 36T (log, so trung bình EW): sau "cắt lên" −0,30 (n=215) vs sau
  "cắt xuống" −0,19 (n=156) ở IS — sai chiều; OOS −0,07 (n=229) vs −0,13 (n=228) — đúng chiều. Cả hai âm vì mốc so là trung
  bình số học (bị mã tăng mạnh kéo lên). Lý do sai chiều IS: tâm cắt lên giá phần lớn do **giá rơi** (động lượng âm còn
  tiếp diễn). ⇒ **Thời điểm cắt không phải tín hiệu mua**; thứ có thông tin là **mức** chiết khấu.
- **(2d) 4 ca:** §4.
- Luật chọn khoá trước (§4 PRELOCK): không biến thể mù giá nào đạt (1) ⇒ chọn theo phía-yếu-nhất cao nhất trên IS =
  **B với r slow/adp (64,5%)**, và nói thẳng là không đạt. Tôi **không** đề xuất B làm engine: IC IS thấp nhất họ RIM
  (0,085), phân tán bằng engine FCFE (IQR 1,4–1,5), IC phần dư sau khi loại E/P ≈ 0 ở IS (0,017). Đề xuất D0 là **phán đoán
  sau prelock**, cần skeptic soát.

## 4. Bốn ca kiểm của user (PIT; `out/cases_paths.csv`, đơn vị = Close điều chỉnh)

| Ca và điều kiện khoá trước | A | B | D0 | H | G1 |
|---|---|---|---|---|---|
| VCS: ≥50% cuối tháng 2015 có tâm > giá | 42% ✗ | **92% ✓** | 0% ✗ | 0% ✗ | 0% ✗ |
| DGC: ≥50% cuối tháng 2016 có tâm > giá | 0% ✗ (2 quan sát) | 100% ✓ | 100% ✓ | 75% ✓ | 80% ✓ (5 q.s.) |
| VNM-a: ≥50% cuối tháng 2011 có tâm > giá | không chạy (A chỉ dựng từ 2014) | 100% ✓ | 0% ✗ | 0% ✗ | **100% ✓** |
| VNM-b: ≥50% tháng 2015-07→2016-12 có tâm < giá | 100% ✓ | 100% ✓ | 100% ✓ | 100% ✓ | 94% ✓ |
| HPG: tâm 12/2019 > 12/2018, 06/2020 > 06/2019, có tháng 2019 tâm > giá | ✗ | ✗ (17.087 → 10.487) | **✓ (11.694 → 13.656)** | ✓ | ✓ |
| Điểm | 1/5 | 4/5 | 3/5 | 3/5 | 4/5 |

- **HPG 2019** là ca phân biệt rõ nhất: ROE TTM rơi 26% → 17% vì Dung Quất chưa chạy, FCFE âm (engine không ra FV), mô
  hình ngoại suy ROE hiện tại cho tâm giảm 39%. RIM xuyên chu kỳ nhân ROE 5 năm (27%) với vốn chủ đã phình ⇒ tâm tăng
  17% trong 2019, giá 7.230 so với tâm 13.656 cuối 2019; giá cuối 2021 là 23.710.
- **VCS 2015** thì ngược lại: ROE nhảy 12% → 44% trong một năm. Mọi mô hình chuẩn hoá theo lịch sử đều "không tin" (tâm D0
  2.587 vs giá 11.120). Chỉ B thấy. **Không có một cơ sở ROE nào bắt được cả HPG-2019 lẫn VCS-2015** — phân biệt "đỉnh
  chu kỳ" với "thay đổi cấu trúc" cần thông tin ngoài BCTC quý (đổi chủ, sản phẩm, công suất), tức là việc của DD.
- **VNM 2011**: P/B 4,0 với ROE 39–49%. Tâm > giá chỉ khi cho ROE 40% **không fade** (B, C) hoặc neo premium riêng
  (G1, E). D0 fade về 0,4 phần vượt trội nên cho tâm 8.642 < giá 11.710. Biến thể H (độ bền theo ROE thấp nhất 5 năm) được
  thiết kế cho đúng ca này nhưng vẫn trượt: ROE_min 5 năm của VNM còn dính 2008 (8% cuối 2010, 22% cuối 2011); tâm H 11.040 <
  giá 11.710 cuối 2011 và vẫn dưới giá suốt 2012–2014.
- Ca đối chiếu ngược (tâm < giá rồi giá nguội): VNM 2015–2017 đúng ở mọi mô hình RIM (D0: tâm 21.482 vs giá 43.770 cuối
  2015; giá cuối 2022 là 59.150 sau đỉnh 91.970). Trên toàn universe: nhóm "luôn đắt" của D0 (53% mã) có lợi suất 36T trung
  vị −0,02 so với +0,13 nhóm giữa.

Mẫu ngẫu nhiên 24 mã (seed 20261124, 3 mã × 6 route + 6 COMPOUNDER) và danh sách thất bại: `out/sample_table.csv`. Vài
dòng đáng nói: VCB tâm D0 < giá 153/155 tháng (trung vị V/P 0,48) trong khi giá ×7,3 — **mô hình sai rõ với ngân hàng
đầu ngành**; VPD (điện) không cắt lần nào trong 128 tháng; POM, HNG, OGC, PVX (giá còn 18–40% so với 2014) được D0 xếp
"đắt" phần lớn thời gian (V/P trung vị 0,14–0,46) — đúng; nhưng QBS (giá còn 4%) có V/P trung vị 1,13 và HAG 0,91 — không cảnh
báo. FLC, ROS, HVG, KSA **không có trong cache** (xem §7).

## 5. Tạo giá trị đầu tư (4) — luật khoá trước, không tune (`out/bt_summary.csv`, `bt_dsr.json`, `resid_ic.csv`)

Danh mục EW tái cân bằng cuối tháng, khớp tại Close phiên kế tiếp (T+1), phí 0,1%/chiều theo turnover, tiền nhàn rỗi 0%
(**pin0% = đầu sàn**; không đo pin1M). 2014-06→2026-10. S1 = giữ mã có giá ≤ 0,8×tâm và rating 8L ≤ 3, ra khi giá > tâm.

| Chiến lược (tâm D0) | CAGR toàn kỳ | IS | OOS | Sharpe | MaxDD | số mã TB | turnover/tháng |
|---|---|---|---|---|---|---|---|
| S1 vùng mua + rating ≤ 3 | **15,4%** | 9,3% | 20,6% | 0,81 | −39,5% | 68 | 23% |
| S2 không cổng rating | 14,5% | 6,8% | 21,2% | 0,74 | −40,7% | 127 | 17% |
| S3 đối chứng: cùng số mã, chọn theo E/P | 15,1% | 8,2% | 21,2% | 0,75 | −44,1% | 68 | 38% |
| S4 quintile V/P cao nhất | 11,4% | 2,9% | 19,0% | 0,56 | −41,7% | 67 | 29% |
| S1 với engine FCFE (A) | 13,2% | 9,6% | 16,3% | 0,71 | −38,4% | 53 | 26% |
| S1 với G1 (tâm cắt giá tốt nhất) | 9,0% | 2,3% | 14,9% | 0,52 | −40,0% | 61 | 28% |
| Universe EW | 9,2% | 5,4% | 12,4% | 0,50 | −47,7% | 339 | 12% |
| VNINDEX (giá, không cổ tức) | 9,2% | 8,9% | 9,5% | 0,54 | −43,2% | | |

- S1-D0 thắng universe EW **10/13 năm**; thua 2019 (−5,5đ), 2021 (−11,4đ), 2025 (−1,5đ). Bỏ lần lượt từng năm, CAGR vượt
  trội vẫn trong +5,3 → +7,4 điểm %/năm. Theo DT5G lúc lập danh mục, vượt trội TB/tháng: CRISIS +1,40% (21 tháng) · BEAR
  +0,47% (13) · NEUTRAL +0,22% (90) · BULL +0,16% (21) · EX-BULL +1,19% (3).
- **Cổng rating 8L có ích ở IS** (S1 9,3% vs S2 6,8%), trung tính ở OOS.
- **So với "chỉ là 1/PE":** S1 hơn S3 ở IS (+1,1đ), kém ở OOS (−0,6đ) ⇒ theo prelock, **không tuyên bố alpha vượt E/P**.
  Điểm cộng thật: turnover thấp hơn (23% vs 38%/tháng) và MaxDD nông hơn 4,6 điểm. IC phần dư của log(V/P) sau khi loại hạng
  E/P và B/P: 0,079 (IS) / 0,153 (OOS) — dương ở cả hai era, nhưng t-stat tính trên các quý chồng lấn nên bị thổi phồng,
  không dùng làm bằng chứng.
- **DSR (N = 33 biến thể đã chạy):** Sharpe tuyệt đối S1-D0 → DSR 0,983; Sharpe **vượt trội so EW** → DSR **0,788 < 0,95
  ⇒ RED FLAG** theo quy chuẩn. Kết luận về alpha chưa đủ mạnh để wire vào book.
- **Tâm cắt giá nhiều hơn không tạo thêm giá trị:** S1 với G1 chỉ 2,3% ở IS (thua EW). Trừ đi premium riêng của mã là
  trừ luôn phần "rẻ bền" — chính phần mang lợi suất.
- Self-check: NAV S1 tính lại bằng đường code độc lập từ `holdings_S1_*.csv`: lệch 0,000012 VND trên 5.824.634.626 VND
  (D0), tương tự G1 và B; PASS dưới `env -u TZ` và `TZ=America/New_York`. V/B D0 tính lại bằng vòng lặp thuần trên 200 dòng:
  lệch tối đa 4,4e-16.

## 6. Thiết kế đề xuất: DCF-VN hai lớp

**Lớp 1 — Giá trị nội tại RIM-VN (mù giá, D0).** Dùng để: xếp hạng, lens sizing, cổng "không mua đắt", neo tuyệt đối.
**Lớp 2 — Tâm giao dịch = Lớp 1 × premium riêng của mã (G1/G05).** Dùng để: vùng hiển thị trong DD, vì đây là lớp duy
nhất thoả tiêu chí "giá và tâm phải gặp nhau". Phải gắn nhãn "có dùng giá quá khứ", **không** dùng để chọn mã.
Chênh giữa hai lớp = premium/discount bền mà thị trường trả cho mã đó — đây là con số DD cần **giải thích** (moat, tài sản
ngoài sổ, sở hữu nhà nước, room ngoại, thanh khoản), thay vì để lớp phán đoán âm thầm sửa như hiện nay (báo cáo 11/11 §5).

Tham số và lý do (đã đo độ nhạy ở `metrics.csv`; không tham số nào fit theo giá):

| Tham số | Giá trị | Lý do góc nhìn VN | Độ nhạy đo được |
|---|---|---|---|
| Cơ sở lợi nhuận | ROE trung vị 5 năm × vốn chủ hiện tại | Chu kỳ ngành VN 3–5 năm; capex đi trước lợi nhuận (HPG, DGC); LNST quý nhiễu vì thu nhập tài chính/thanh lý | đo trên D: cửa sổ 3 năm cắt +2–3đ, IC không đổi; 7 năm cắt −2–4đ |
| r | 12,25% cố định (= domestic_v2) | Huy động 12T ~6,75% + ERP nội địa 5,5đ | r theo lãi suất tại chỗ / TB 5 năm: IC ±0,005, cắt ±1đ ⇒ **chỉ dời mức, không cần r động** |
| g_T | min(5,5%, r − 4đ) | Lạm phát mục tiêu ~4% + tăng trưởng thực dài hạn, trần dưới r | – |
| Kỳ dự báo | 10 năm, fade tuyến tính | 3 năm quá ngắn cho doanh nghiệp tái đầu tư 15%/năm | – |
| Fade ROE vượt trội | giữ 0,4 phần chênh so với r | Cạnh tranh bào mòn nhưng VN còn rào cản (giấy phép, đất, thương hiệu) | đo trên D: κ=0 ⇒ IC OOS 0,242 → 0,148; κ=0,7 ⇒ phía đắt OOS 45% → 35% |
| Tái đầu tư | g = ROE × (1 − cổ tức tiền/LN), trần 15%, không giả định phát hành thêm | Cổ tức cổ phiếu = giữ lại; trần tránh ngoại suy giai đoạn tăng nóng | – |
| Shrink về ngành | **không** (D0 hơn D ở IC cả hai era) | Phân ngành 8L quá thô (1.026/1.306 mã nằm ở COMPOUNDER) | D: IC 0,133 / 0,242 |
| Phụ phí thanh khoản | **không đưa vào r** | +1đ cho nửa kém thanh khoản không cải thiện gì (IC 0,130 / 0,242) | xử lý ở sizing, không ở tâm |
| Ngân hàng | cùng RIM (P/B–ROE) | Cho phép phủ nhóm engine đang bỏ | **VCB/BID/CTG vẫn lệch một phía** — cần tham số riêng, chưa làm |

Cách dùng để tạo giá trị (theo bằng chứng ở §3–§5):
1. **Mức chiết khấu, không phải thời điểm cắt.** Mua khi giá ≤ 0,8× tâm Lớp 1 **và** rating 8L ≤ 3; không coi "tâm vừa
   cắt lên giá" là tín hiệu (sai chiều ở IS).
2. **Cảnh báo đắt là phần đáng tin nhất:** tâm Lớp 1 < 0,75× giá kéo dài + ROE xuyên chu kỳ thấp ⇒ không mở mới. Đây là
   chỗ thị trường cá nhân trả giá quá tay lâu nhất.
3. **Sizing theo độ đồng thuận hai lớp:** rẻ ở cả Lớp 1 và Lớp 2 ⇒ đủ cỡ; chỉ rẻ ở Lớp 1 (rẻ bền) ⇒ cần chất xúc tác từ
   DD; chỉ rẻ ở Lớp 2 ⇒ rẻ so với chính nó nhưng không rẻ tuyệt đối, cỡ nhỏ. *Luật 3 mức này chưa backtest.*
4. **Ca thay đổi cấu trúc (kiểu VCS 2015) là việc của DD:** khi ROE TTM vượt ROE 5 năm > 15 điểm, mô hình phải gắn cờ
   "ROE đang nhảy — tâm xuyên chu kỳ có thể lạc hậu" và DD quyết định dùng ROE nào, có lý do bằng văn bản.
5. **Quan hệ với hệ đang chạy:** không đổi V2.4/DT5G. Ứng viên dùng đầu tiên là lens trong DD và cảnh báo đắt cho
   custom30V — đều là hiển thị, không chặn lệnh.

## 7. Rủi ro và giới hạn

- **Thiên lệch sống sót:** FLC, ROS, HVG, KSA không có dòng nào trong cache `ticker` lẫn `ticker_financial` (chưa kiểm BQ
  gốc). Nếu mã huỷ niêm yết bị xoá khỏi nguồn thì mọi con số ở đây lạc quan, nhất là phía "rẻ". Trong panel hiện có, 559 /
  37.261 dòng in-universe (1,5%) thiếu giá sau 36 tháng và bị loại khỏi mẫu. Độ nhạy −50% cho mã biến mất: S1-D0 CAGR 15,3% vs EW 8,9% (`out/bt_summary_hair.csv`).
- **Mã vốn chủ âm bị loại** (BVPS ≤ 0; TTF chỉ có 5 tháng) — RIM không định giá được đúng nhóm rủi ro nhất.
- **33 biến thể, 6 trong đó thêm sau khi thấy số** (H, Hd, G1, G05 trên D0 và H). G1 và H phải coi là giả thuyết.
- **Sức mạnh theo thời gian yếu:** 2 khối 36 tháng độc lập mỗi era; OOS trùng giai đoạn 2020–2021 tăng mạnh. CI theo cụm
  năm **chưa làm**; bootstrap B=300 thay vì 2.000 đã khai.
- `BVPS` và `ROE_Trailing` lấy như vendor nạp; chưa kiểm chúng có bị restate không (đã biết `OShares` bị).
- Lãi huy động lịch sử là chuỗi neo hồi tố (registry: CANONICAL-PROXY); trước 2011 dùng refi + 1đ. Ảnh hưởng nhỏ vì r
  động gần như không đổi kết quả.
- Route 8L không có vintage trước 2026.
- Backtest là EW toàn universe, **không mô hình hoá thanh khoản/sức chứa, slippage, thuế**; MaxDD ~−40% không phù hợp làm
  book độc lập. Quy đổi thực tế theo quy ước chung: trừ thêm ~1,5 điểm %/năm.
- Luật sizing 3 mức và cờ "ROE đang nhảy" ở §6 là đề xuất, chưa đo.

## 8. Lệch so với PRELOCK

1. Thêm 6 biến thể sau khi thấy kết quả (H, Hd, G1D0, G05D0, G1H, G05H) ⇒ N trials 27 → 33; DSR tính với 33.
2. Bootstrap B=300 (khai 2.000); chưa có CI cụm theo năm as-of.
3. Mẫu ngẫu nhiên: chỉ có 7 route ⇒ 3 × 6 route + 6 COMPOUNDER = 24 mã.
4. 4/12 mã thất bại khai trước không có dữ liệu (FLC, ROS, HVG, KSA).
5. Độ nhạy mã rời sàn −50%: chỉ chạy cho D0 (số ở §7).
6. Đề xuất D0 thay vì biến thể mà luật chọn khoá trước chỉ ra (B) — lý do ở cuối §3.

## 9. Lộ trình `dcf_valuation` v3 và việc cần user duyệt

| Bước | Nội dung | Cần duyệt |
|---|---|---|
| 0 | quant-skeptic soát báo cáo này (trọng tâm: sống sót, 6 biến thể sau prelock, S1 vs E/P) | Mike |
| 1 | Winston kiểm BQ gốc có mã huỷ niêm yết không; kiểm `BVPS`/`ROE_Trailing` có bị restate | Mike |
| 2 | Chạy lại với mã huỷ niêm yết + CI cụm năm + B=2.000; prelock mới cho G1/H và luật sizing 3 mức | Mike |
| 3 | Viết `dcf_rim_vn.py` **song song** engine cũ (không thay), xuất 2 lớp tâm + cờ "ROE đang nhảy"; DD hiển thị cả engine cũ lẫn mới trong 1 quý | **user** |
| 4 | Tham số ngân hàng riêng (P/B–ROE với chi phí vốn và fade khác) | user, sau bước 3 |
| 5 | Chỉ sau khi bước 2 qua skeptic: quyết định có thay cơ sở FCFE trong `dcf_valuation.py` hay không | **user** |

Câu hỏi cần user trả lời trước bước 3: **chấp nhận tâm hiển thị (Lớp 2) có dùng giá quá khứ của chính mã hay không?** Nếu
không, tiêu chí (1) không đạt được với dữ liệu hiện có, và nên đổi tiêu chí (1) thành "cảnh báo đắt/rẻ có giá trị dự báo"
(điều mà Lớp 1 đã cho thấy).

## 10. Tái lập

```
cd agents/Taylor/research/dcf_vn_redesign_20261124/calc ; PY=/home/trido/thanhdt/wc_venv/bin/python
# out/px_pre2013_m.csv: bq query phiên cuối tháng 2006–2012 (lệnh trong git log / PRELOCK §0)
$PY a_engine_baseline.py            # đối chứng A -> out/engine_A.parquet
$PY b_build_panel.py ; LAGQ=1 $PY b_build_panel.py
$PY c_models.py                     # 33 biến thể -> out/vp.parquet
$PY d_metrics.py                    # tiêu chí 1–2 -> out/metrics.csv, cases.csv  (seed 20261124)
ONLY=H_fix,Hd_fix,G1D0_fix,G05D0_fix,G1H_fix,G05H_fix SFX=_post $PY d_metrics.py
$PY e_backtest.py ; $PY f_diag.py ; $PY g_selfcheck.py
```
Parquet không commit (lớn); CSV/JSON kết quả và `calc/MD5SUMS.txt` có trong nhánh `session/Taylor_20261124_140534`.
