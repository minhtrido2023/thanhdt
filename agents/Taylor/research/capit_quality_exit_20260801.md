# CAPIT quality-exit — giữ nguyên 60 phiên hay bán sớm khi 1 mã rớt sàn chất lượng?

Job `Taylor_20260801_073610` (dispatch từ Mike, câu hỏi mở của `kb/projects/capit-sizing-bug-0721.md`).

**R&D THUẦN — KHÔNG wire production.** Cơ chế đã cài vào engine là **env-gated, mặc định OFF**
(`CAPIT_QEXIT=off`), production byte-identical.

---

## 0. Câu trả lời ngắn

**GIỮ NGUYÊN 60 phiên (phương án a).** Không có biến thể nào của (b)/(c)/(d) tốt hơn baseline —
**tất cả 24 ô trong lưới chiến lược đều ≤ baseline**, ô tốt nhất chỉ là "hoà" vì luật gần như không
bao giờ bắn. Engine A/B đầy đủ ở tầng danh mục (§6) xác nhận: **5/5 leg ≤ control ở CAGR/Sharpe/
Calmar, và MaxDD y hệt −17,5% ở cả 5** — luật không mua được bảo hiểm rủi ro nào để bù phần CAGR
mất đi. (Cảnh báo trung thực: ở tầng danh mục, ĐỘ LỚN phần thua không bền — riêng 2025 gánh gần hết,
§6b. Kết luận "không đổi gì" không phụ thuộc vào điểm này, nhưng đừng trích con số −0,35pp CAGR như
một hằng số.)

Ba lý do, theo thứ tự quan trọng:

1. **"Rớt sàn chất lượng" trong 60 phiên = 100% do FSCORE, KHÔNG PHẢI do chất lượng dài hạn.**
   Trong 85 vị thế CAPIT lịch sử, **0/85** lần vi phạm `ROE_Min5Y>=0.12 ∧ ROIC5Y>=0.10`; **37/85
   (43,5%)** vi phạm `FSCORE>=6`. FSCORE là điểm Piotroski đo *biến động YoY* của 9 hạng mục kế
   toán — nó lật liên tục theo quý, đúng bản chất là nhiễu, không phải sự kiện "công ty hỏng".
2. **Tín hiệu đến SAU cú giảm và TRƯỚC cú hồi.** Nhóm bị cờ đúng là nhóm yếu hơn (giữ tới hết hạn
   +13,7% vs nhóm không cờ +22,8%) — nhưng bán tại ngày cờ chỉ thu được **+2,7%**, tức **bỏ lại
   11,0pp**. CAPIT là sleeve *mua đáy hoảng loạn*; cờ chất lượng bắn đúng lúc tin xấu ra, tức đúng
   lúc KHÔNG nên bán.
3. **"N kỳ liên tiếp" (phương án c theo quý) là bất khả thi về mặt cấu trúc.** Cửa sổ hold 60 phiên
   ≈ 87 ngày dương lịch ≈ **đúng 1 kỳ công bố**. Không bao giờ có 2 kỳ liên tiếp trong cửa sổ ⇒
   (c) với N≥2 quý **đồng nhất với (a)**. Chỉ có xác nhận theo **PHIÊN** (K) là cài được — và K
   càng dài thì thiệt hại càng nhỏ, hội tụ về baseline (đúng như dự đoán nếu tín hiệu là nhiễu).

---

## 1. Điều kiện chạy & nguồn dữ liệu (tra `mike/kb/data_registry/` trước, đúng quy tắc §9)

| Thứ | Nguồn | Status registry | Ghi chú |
|---|---|---|---|
| Sàn chất lượng CAPIT | `tav2_bq.ticker_prune` (`ROE_Min5Y`, `ROIC5Y`, `FSCORE`) | CANONICAL | **Đúng nguồn production đang wire cho rổ CAPIT** — `capit_basket()` trong `pt_v23_audit_2014.py` chọn rổ từ chính bảng này. CAPIT pool CỐ Ý còn ghim `ticker_prune` (chưa cutover `universe_pit`, xem `kb/projects/universe-pit-migration.md`) ⇒ dùng `ticker_prune` là **nhất quán với production**, không phải bỏ sót. |
| 8L rating | `tav2_bq.fa_ratings_8l` | CANONICAL | Lịch sử point-in-time (ticker, eff_date, rating). Phủ **2014-07-09 → 2026-07-29** ⇒ sự kiện E0 (2014-05) không có rating; đã tính vào phần "không cờ" (fail-safe, không bịa). |
| Regime | `tav2_bq.vnindex_5state_dt5g_live` (qua engine) | CANONICAL | KHÔNG đọc `vnindex_5state` (bẫy base). |
| Giá | `ticker_prune` Open/Close từ snapshot | CANONICAL | Thoát mô phỏng ở **Open T+1** sau phiên cờ (đúng quy ước engine, không nhìn trước). |

**Snapshot pin: `data/bq_cache_asof20260729_postrestate`** — đúng snapshot đã dùng cho lần re-pin R3
2026-07-29, nên mọi leg cùng vintage và so được với số pin hiện hành. `BQ_CACHE_THREADS=1`,
`NAV_TOTAL_B=50`, `ETF_LIQ=custompitg`, `BASKET_WT=namecap`, `BASKET_SELECT=yieldcombo`,
`PARK_STATES=3:0.7`, `AUDIT_END=2026-06-19`, `$DNA_PYEXE`.

Runner: `data/capit_qexit_20260801/run_leg.sh`. Panel: `panel.py` + `panel2.py` cùng thư mục.

---

## 2. Mẫu thật — N BAO NHIÊU, nói thẳng

- **14 sự kiện CAPIT** có vị thế thật (2014-05-09 → entry cuối 2026-03-10; thoát cuối 2026-06-08).
- **85 vị thế mã-cấp** (một mã × một sổ BAL/LAG = 1 vị thế; hai sổ mua song song nên các cặp
  BAL/LAG **không độc lập** — N hiệu dụng gần 45-50 hơn là 85).
- **11 sự kiện** là nơi luật thực sự hành động (có ≥1 mã bị cờ).

**Đây là mẫu nhỏ và tôi không nguỵ trang nó.** Kiểm định dấu trên 11 sự kiện quyết định: 7 xấu đi /
4 tốt lên, **p hai phía = 0,549 — KHÔNG có ý nghĩa thống kê về mặt TẦN SUẤT**. Bằng chứng chỉ mạnh ở
mặt **ĐỘ LỚN**: bootstrap resample theo SỰ KIỆN (10k) cho Δ trung bình **−4,05pp, CI90%
[−7,32; −1,33]pp, P(Δ>0)=0,001**; và leave-one-event-out **0/14 lần đổi dấu** (dải −7,82…−2,67pp).

> Đọc trung thực: **không có bằng chứng nào ủng hộ việc bán sớm**; bằng chứng rằng nó *có hại* là
> vừa-đến-mạnh về độ lớn nhưng yếu về tần suất. Với n như thế này, kết luận đúng là **giữ nguyên
> hiện trạng (a)** — đó cũng là lựa chọn không-hành-động, nên gánh nặng chứng minh thuộc về bên
> muốn đổi, và bên đó không có số.

**Walk-forward IS/OOS: BỎ QUA có chủ ý.** Chia 14 sự kiện thành IS 2014-19 (6 sự kiện, 5 có cờ) /
OOS 2020+ (8 sự kiện, 6 có cờ) cho ra hai nửa mà mỗi nửa đều không kết luận được gì hơn tổng thể;
LOO theo sự kiện ở trên là công cụ đúng cho n nhỏ và đã chạy đầy đủ. (Bài học 07-31: đừng ép chia
block khi kết quả nhạy với cách chia — ở đây LOO cho thấy nó KHÔNG nhạy, dấu giữ nguyên mọi cách bỏ.)

---

## 3. Lưới chiến lược — sleeve CAPIT, lợi suất trọng-số-theo-vốn trên toàn bộ 85 vị thế

Baseline (a) = **+19,34%** (trung bình mỗi vị thế, cost-weighted, gộp mọi sự kiện).

| Chiến lược | n bị cờ | ret | Δ vs (a) |
|---|---|---|---|
| **(a) hold 60td — BASELINE** | 0 | **+19,34%** | — |
| (b) exit ngay, `floor` K=1 | 37 | +12,70% | **−6,64pp** |
| (c) exit `floor` K=5 phiên | 29 | +13,69% | −5,65pp |
| (c) exit `floor` K=20 phiên | 24 | +16,47% | −2,87pp |
| (d) trim 50% `floor` K=1 | 37 | +16,02% | −3,32pp |
| (d) trim 50% `floor` K=5 | 29 | +16,52% | −2,83pp |
| (d) trim 50% `floor` K=20 | 24 | +17,91% | −1,43pp |
| (b) exit `floornf` (chỉ ROE/ROIC) K=1/5/20 | **0** | +19,34% | **+0,00pp** *(no-op)* |
| (b) exit `fscore` K=1 | 37 | +12,70% | −6,64pp *(≡ `floor`)* |
| (b) exit `r8l` (8L>3) K=1 | 4 | +19,06% | −0,28pp |
| (d) trim 50% `r8l` K=5 | 4 | +19,29% | −0,05pp |

Đầy đủ 24 ô: `data/capit_qexit_20260801/strategy_grid.csv`.

**Đọc bảng:**
- **Mọi ô ≤ baseline.** Không có ngoại lệ, không có ô nào dương.
- **`floor` ≡ `fscore` từng con số** ⇒ xác nhận cơ học: sàn chất lượng CAPIT chỉ bị phá bởi FSCORE.
- **`floornf` = no-op tuyệt đối (0/85)** ⇒ nếu định nghĩa "rớt chất lượng" theo đúng nghĩa *chất
  lượng dài hạn* (ROE/ROIC nhiều năm — tinh thần "golden floor"), thì **sự kiện này chưa từng xảy
  ra** trong 12 năm CAPIT. Không có gì để thiết kế cơ chế thoát cho nó.
- **8L rating gần như không bắn (4/85)** và cũng âm nhẹ. 8L cập nhật theo quý (median 47 eff-date/mã
  trên 12 năm ≈ 4/năm) và rổ CAPIT vốn đã lọc chất lượng nên hiếm khi rơi xuống >3.
- **K dài hơn → thiệt hại nhỏ hơn, hội tụ về 0.** Đây là dấu vân tay của **nhiễu**: nếu tín hiệu
  thật, xác nhận lâu hơn sẽ *tăng* giá trị, không *giảm* thiệt hại.
- **Trim 50% ≈ đúng một nửa thiệt hại của exit toàn phần** ở mọi K ⇒ không có hiệu ứng lồi nào cứu
  được phương án (d); nó chỉ là "sai một nửa".

---

## 4. Vì sao bán sớm lại tệ — chẩn đoán

| | n | ret giữ tới hết 60td | ret nếu bán tại ngày cờ |
|---|---|---|---|
| Bị cờ (`floor` K=1) | 37 | **+13,72%** | **+2,72%** |
| Không bị cờ | 48 | **+22,81%** | — |

Cờ **có** chọn đúng nửa yếu (13,7% < 22,8%) — nó không phải tín hiệu rác. Vấn đề là **thời điểm**:
sau ngày cờ, giá đi tiếp **có lợi trong 23/37 ca** (trung bình +11,00pp, trung vị +4,00pp). Cờ FSCORE
bắn đúng ngày BCTC xấu ra — tức đúng điểm bi quan cực đại của một mã đang trong quá trình hồi từ
washout. Bán ở đó = hiện thực hoá đáy.

Thời điểm cờ so với ngày mua: trung vị **46 ngày** (p25 7 – p75 77), tức phân bố rộng khắp cửa sổ
hold, không tập trung đầu hay cuối.

**Ca lỗ nặng nhất của luật** (đều là mã hồi mạnh sau tin xấu):
MWG E8 (giữ +41,6% → bán +(−3,7)% = **−45,4pp**), GIL E8 (−42,6pp), TNG E15 (−37,2pp),
DGW E15 (−36,9pp), LIX E3 (−27,4pp), HDG E13 (−25,5pp), CTR E15 (−20,1pp).
Sự kiện tệ nhất: **E15 2025-04-04 (−25,00pp)**; tốt nhất chỉ **E2 +1,35pp**. Bất đối xứng đuôi rõ:
khi luật sai thì sai rất nặng, khi đúng thì đúng rất nhẹ.

Chi tiết từng vị thế: `data/capit_qexit_20260801/holdings_panel.csv`,
theo sự kiện: `event_rollup.csv`.

---

## 5. Đối chiếu ca thật NCT/SAB (đợt washout 2026-07-20)

Tiền đề dispatch **đúng, nhưng cần chính xác hoá về CƠ CHẾ** (kiểm chứng trên snapshot 07-29):

| Mã | Ngày rớt sàn | ROE_Min5Y | ROIC5Y | FSCORE | 8L rating |
|---|---|---|---|---|---|
| NCT | 2026-07-21 | 0,500 ✅ | 0,603 ✅ | **3,0 ❌** | 1 → **2** (vẫn ≤3, **KHÔNG rớt**) |
| SAB | 2026-07-23 | 0,174 ✅ | 0,176 ✅ | **5,0 ❌** | ≤3 (**KHÔNG rớt**) |
| PVT / SIP / VNM | — | ✅ | ✅ | 6/7/7 ✅ | ≤3 |

⇒ NCT và SAB **không hề "mất chất lượng"** theo nghĩa ROE/ROIC/8L. Cả hai rớt sàn **chỉ vì FSCORE**
— đúng leg mà nghiên cứu này cho thấy là nhiễu, và **8L rating — cổng chất lượng chuẩn tắc của hệ —
xác nhận cả hai vẫn đạt**. Đây chính là base-rate case: theo lịch sử 37 ca cùng dạng, bán ở đây kỳ
vọng **thiệt hại ~11pp** so với giữ.

*(Đợt 2026-07-20 nằm ngoài `AUDIT_END=2026-06-19` nên KHÔNG được đưa vào bất kỳ con số backtest nào
ở trên — đây là đối chiếu định tính, không phải mẫu thứ 15.)*

---

## 6. Kiểm chứng ở tầng danh mục (engine A/B đầy đủ)

Phần §3 đo **lợi suất vị thế của riêng các mã CAPIT**. Phần này chạy **engine đầy đủ V2.4/R3** (cùng
spec pin R3, `AUDIT_END=2026-06-19`, 50B, threads=1) để xem luật ảnh hưởng thế nào tới **NAV thật của
cả danh mục** — khác nhau vì tiền thoát sớm được **tái triển khai** sang BAL/LAG chứ không nằm im.

**5/5 leg `EXIT=0`, self-check cash-flow + NAV identity = 0 VND cho cả 2 sổ.**
**Control tái lập ĐÚNG số pin R3 hiện hành** (27,60% / 1,84 / −17,5% / 1,58 — `data/results_registry.md`
mục re-pin 2026-07-29) ⇒ harness hợp lệ, mọi Δ dưới đây là do treatment.

| Leg | CAPIT_QEXIT | Final NAV | CAGR | Sharpe | MaxDD | Calmar | ΔCAGR | ΔNAV |
|---|---|---|---|---|---|---|---|---|
| **ctrl (a)** | `off` | 1.041,95B | **27,60%** | **1,84** | −17,5% | **1,58** | — | — |
| (b) exit K=1 | `floor:1:1.0` | 1.006,54B | 27,25% | 1,82 | −17,5% | 1,55 | **−0,35pp** | −35,4B |
| (d) trim 50% | `floor:1:0.5` | 1.024,58B | 27,43% | 1,83 | −17,5% | 1,57 | −0,17pp | −17,4B |
| (c) exit K=20 phiên | `floor:20:1.0` | 1.025,35B | 27,44% | 1,83 | −17,5% | 1,57 | −0,16pp | −16,6B |
| (b) exit 8L>3 | `r8l:1:1.0` | 1.041,55B | 27,60% | 1,84 | −17,5% | 1,58 | −0,00pp | −0,4B |

**Hai điều đọc được ngay:**
1. **Không leg nào cải thiện gì** — CAGR/Sharpe/Calmar đều ≤ ctrl, thứ hạng khớp đúng §3
   (exit toàn phần tệ nhất → trim/K dài đỡ hơn → 8L ≈ no-op).
2. **MaxDD −17,5% GIỐNG HỆT ở cả 5 leg.** Đây là điểm quan trọng nhất của phần này: lý do duy nhất
   đáng để chấp nhận một luật thoát tốn CAGR sẽ là **nó mua được bảo hiểm rủi ro**. Nó không mua
   được gì cả. Không có đánh đổi return-vs-risk để cân nhắc — chỉ có mất mát một chiều.

### 6b. Per-year LOO ở tầng danh mục — ĐỘ LỚN KHÔNG BỀN, phải nói thẳng

Ở tầng vị thế (§3) hiệu ứng âm rất sạch (LOO 0/14 lần đổi dấu). Ở tầng **danh mục** thì **không**:

| Năm | ctrl | Δ (b) K=1 | Δ (d) trim | Δ (c) K=20 | Δ 8L |
|---|---|---|---|---|---|
| 2016 | +14,26% | −0,19 | −0,26 | −0,46 | +0,00 |
| 2018 | +26,82% | −0,35 | −0,15 | +0,05 | −0,05 |
| 2020 | +24,38% | −0,51 | −0,21 | −0,38 | +0,00 |
| **2021** | +102,29% | **+7,94** | −0,02 | **+7,81** | +0,02 |
| 2022 | −2,83% | −0,31 | −0,38 | +0,39 | −0,01 |
| 2023 | +23,37% | +0,47 | +0,48 | −0,02 | +0,00 |
| 2024 | +24,20% | −0,54 | +0,08 | −0,83 | +0,00 |
| **2025** | +54,12% | **−8,86** | −1,82 | **−6,62** | +0,00 |
| *(2014/15/17/19/26: \|Δ\|≤0,06pp)* | | | | | |
| **Tổng Δ theo năm** | | **−2,24pp** | −2,19pp | **+0,16pp** | −0,04pp |
| **Số năm xấu đi / tốt lên** | | 7 / 5 | 6 / 5 | 5 / 5 | 2 / 1 |

- Với (b) K=1: **bỏ riêng năm 2025 ra là luật hoà hoặc dương**. Với (c) K=20 phiên, tổng Δ theo năm
  thậm chí **+0,16pp** — dấu ngược với ΔCAGR compound (−0,16pp), tức nằm gọn trong nhiễu.
- **2021 luật LÃI +7,9pp** — nhất quán với cơ chế **tái triển khai**: thoát sớm giữa bull cực mạnh
  trả tiền về cho BAL/LAG đang chạy tốt. Đây là hiệu ứng *dùng vốn*, không phải bằng chứng cờ chất
  lượng chọn đúng mã (§4 đã cho thấy nó chọn sai thời điểm).
- Đây đúng khuôn mẫu **"1–2 năm gánh toàn bộ hiệu ứng = reshuffle-luck"** (`kb/KNOWLEDGE.md` §8, ca
  Wave1/H8a) — chỉ khác là lần này nó bác bỏ **độ tin cậy của con số âm**, không phải của một con số
  dương ai đó muốn wire.

**Kết luận trung thực gộp 2 tầng:**
- Tầng vị thế: bằng chứng *có hại* rõ và bền (LOO 0/14, bootstrap P(Δ>0)=0,001).
- Tầng danh mục: bằng chứng chỉ **"không cải thiện"** — không đủ mạnh để tuyên bố "gây hại
  −0,35pp CAGR" như một hằng số, vì 2025 gánh gần hết.
- **Cả hai tầng đều không có một ô nào dương ⇒ khuyến nghị KHÔNG ĐỔI GÌ không phụ thuộc vào việc
  giải quyết mâu thuẫn này.** Gánh nặng chứng minh thuộc bên muốn thêm luật; không có số nào ủng hộ.
  (Nếu ai đó muốn dùng chính bảng này để lập luận NGƯỢC — "K=20 tổng Δ dương, nên wire" — thì
  §3/§4 chặn: ở tầng vị thế nó thua 2,87pp và cơ chế lãi 2021 là tái-triển-khai-trong-bull, không
  phải chất lượng.)

Log: `data/capit_qexit_20260801/qx_{ctrl,floor1,floor1trim,floor20,r8l1}.log`.
CSV audit mỗi leg có suffix riêng (`_qx<metric><K>f<frac>`, §8) — **không leg nào ghi đè CSV pinned**.

---

## 7. Ý tưởng thay thế đã cân nhắc (và vì sao không theo đuổi)

1. **Đổi sàn thoát sang "chất lượng dài hạn" (`floornf`)** — đã đo: 0/85 lần bắn trong 12 năm. Cơ chế
   sẽ luôn ngủ ⇒ không có giá trị bảo hiểm đo được, chỉ thêm bề mặt lỗi. **Không theo đuổi.**
2. **Dùng 8L rating≤3 làm sàn thoát** — bắn 4/85, Δ từ −0,28pp đến −0,05pp. Về bản chất là một
   no-op đắt tiền (phải bơm thêm 1 phụ thuộc dữ liệu vào đường thoát của sleeve). **Không theo đuổi.**
   *(Khác hẳn LAG: ở LAG, gate 8L≤3 là gate ENTRY đã được user chốt cứng 07-27 — không mâu thuẫn,
   vì đây là cổng THOÁT giữa kỳ hold của một sleeve mean-reversion, không phải cổng vào.)*
3. **Cắt lỗ theo giá thay vì theo chất lượng (`CAPIT_STOP`)** — engine đã có sẵn knob này, và nó nằm
   ngoài phạm vi câu hỏi được giao. Ghi lại như hướng riêng nếu sau này muốn hỏi "CAPIT có nên có
   stop không" (câu hỏi khác, cần pre-reg riêng, đừng gộp vào N_trials của họ này).
4. **Dùng cờ chất lượng làm bộ lọc TÁI-MUA ở sự kiện SAU (không phải thoát)** — hấp dẫn về lý thuyết
   và "miễn phí" (không bán gì), nhưng mẫu quá mỏng để đo: chỉ 4 mã xuất hiện lại ở sự kiện sau
   (HPG, VCS, DGW, CTR). **Ghi nhận là câu hỏi mở, KHÔNG kết luận.**

---

## 8. Khuyến nghị

1. **GIỮ NGUYÊN production: hold cố định 60 phiên, không cơ chế quality-exit.** Không cần thay đổi
   gì — đây là kết luận "không hành động".
2. **Không wire `CAPIT_QEXIT`.** Knob đã cài ở dạng env-gated OFF để nghiên cứu này tái lập được;
   nó nên ở nguyên trạng thái đó. Mọi leg mặc định = production byte-identical.
3. **Điều nên nhớ cho lần sau (giá trị bền nhất của job này):** khi ai đó nói *"mã X đã rớt sàn chất
   lượng của rổ CAPIT"*, câu hỏi đầu tiên phải là **"rớt leg nào?"** — nếu là FSCORE thì đó là nhiễu
   kế toán quý, không phải suy giảm chất lượng, và lịch sử 12 năm nói **đừng bán**. Chỉ ROE/ROIC
   nhiều năm mới là chất lượng — và leg đó chưa từng bị phá trong một cửa sổ hold CAPIT.
4. **Đề xuất quant-skeptic verify.** Mẫu nhỏ (14 sự kiện / 11 quyết định), và kết luận dựa vào độ lớn
   chứ không phải tần suất (sign test p=0,549) ⇒ đúng tiêu chí phải qua cổng hoài nghi trước khi coi
   là tri thức chốt của fleet. Kết luận đề nghị verify: *"không có biến thể quality-exit nào cải
   thiện CAPIT; tín hiệu rớt-sàn trong cửa sổ hold là 100% FSCORE"*.

---

## 9. Multiple-testing / kỷ luật (§Quy chuẩn 5)

- **N_trials khai báo = 24 ô panel + 4 leg engine treatment = 28 cấu hình.** Không có ô nào dương ⇒
  **không có gì để chọn**, nên DSR/PBO không áp dụng (DSR/PBO là cổng cho *cấu hình sắp deploy*;
  ở đây khuyến nghị là KHÔNG deploy gì).
- Kiểm định đã chạy: sign test theo sự kiện, bootstrap resample **theo sự kiện** (không theo vị thế —
  các cặp BAL/LAG tương quan gần 1), leave-one-event-out.
- **Chưa pre-register trước khi nhìn số.** Đây là một khiếm khuyết quy trình thật so với job
  07-31 (có `capit_sizing_PREREG`): họ chiến lược ở đây được định nghĩa từ chính prompt dispatch
  (a/b/c/d), nhưng lưới metric × K là do tôi mở rộng SAU khi thấy `floornf` không bắn. Vì mọi ô đều
  âm và khuyến nghị là không-hành-động, rủi ro data-snooping ở đây nghiêng về phía an toàn — nhưng
  ghi nhận thẳng để không tự cho điểm cao hơn thực tế.

## 10. Thay đổi mã nguồn (R&D, default OFF)

- `simulate_holistic_nav.py`: thêm kwarg `quality_exit_dates` — `{(play_type, ticker): (date, frac)}`,
  thoát/trim theo TỪNG MÃ giữa kỳ hold. `None` (mặc định) ⇒ byte-identical.
  Hạn chế đã biết: trim một phần khớp ở giá mark trong ngày (quy ước sẵn có của engine, dùng chung
  với soft-stop), trong khi thoát toàn phần xếp hàng bán Open T+1 — trim vì thế hơi *lạc quan*, mà
  vẫn thua baseline.
- `pt_v23_audit_2014.py`: env `CAPIT_QEXIT="<metric>:<K>:<frac>"` (mặc định `off`), 4 metric
  (`floor`/`floornf`/`fscore`/`r8l`). Có suffix tên file output theo đúng `coding_guidelines.md` §8
  (`_qx<metric><K>f<frac>`) nên không leg nào ghi đè được CSV pinned.
