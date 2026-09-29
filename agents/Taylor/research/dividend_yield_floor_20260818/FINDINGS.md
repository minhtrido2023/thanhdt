# FINDINGS — Dividend Yield Floor (sàn giá từ cổ tức tiền mặt)

- **Job**: `Taylor_20260818_024006` (tiếp `_021828`) · **Ngày**: 2026-08-18
- **PREREG**: `PREREG.md`, commit `beabb4f8` — khoá TRƯỚC mọi query outcome. Tiêu chí §9 **không sửa**.
- **Sai lệch**: `DEVIATIONS.md` (D1–D5) · **Selfcheck**: 20/20 PASS, byte-identical dưới `env -u TZ` và `TZ=UTC`
- **Phạm vi**: R&D thuần. **KHÔNG wire production**, không sửa `filter.json`, không đề xuất banned ticker.

---

## 1. VERDICT

> ### **CONFIRMED — nhưng CHỈ ở chân H2 (đuôi trái / drawdown), KHÔNG ở chân H1 (lợi suất trung bình).**

| Chân | Nội dung | Kết quả | Đạt §9? |
|---|---|---|---|
| **H2** (quyết định bản chất cơ chế) | Chạm sàn ⇒ sụt **ít hơn** nhóm chứng cùng ngành/cùng vol | ΔMDD₆₀ = **+3,46 pp**, t=**5,14**, n=412 | ✅ **4/4 tiêu chí** |
| **H1** (phụ) | Vượt ngưỡng ⇒ lợi suất vượt trội | BHAR₆₀ = +0,64 pp, t=0,67, **median −0,97** | ❌ Không đạt |

**Đây đúng là claim user đặt ra** — "cổ phiếu cổ tức ổn định **không giảm mạnh** khi yield chạm
lãi suất tiết kiệm". PREREG §0 đã khoá trước rằng *"không giảm mạnh" ≠ "tăng nhiều"*, và dữ liệu
tách đúng theo đường đó: có đệm downside, **không** có alpha lợi suất.

**Mức tin cậy: TRUNG BÌNH, không phải CAO.** Xem §4 — placebo ghép cặp không bằng 0, và phần
hiệu ứng còn lại sau khi trừ placebo **không đạt** ngưỡng t≥2,0. Chi tiết ở §4.1, đây là hạn chế
lớn nhất và là lý do **chưa đủ để đổi cách làm**.

---

## 2. Đối chiếu từng tiêu chí §9 (đã khoá trước)

| # | Tiêu chí CONFIRMED | Ngưỡng | Thực tế | Kết |
|---|---|---|---|---|
| 1 | ΔMDD₆₀ dương ≥ 1,5 pp, \|t_c\| ≥ 2,0 | ≥1,5pp / ≥2,0 | **+3,456 pp**, t=**5,14**, CI[+2,15;+4,79] | ✅ |
| 2 | Đúng dấu + \|t_c\| ≥ 2,0 ở CẢ IS lẫn OOS | cả hai | IS **+4,53** (t=4,11) · OOS **+2,93** (t=3,48) | ✅ |
| 3 | Nhất quán dấu ở ≥3/4 ngưỡng cố định | ≥3/4 | **4/4** dương, t ∈ [3,98 ; 6,33] | ✅ |
| 4 | Sống sót §7.2 (bỏ CRISIS+EX-BULL), không mất quá nửa độ lớn | >50% | **+2,97 pp** (t=4,92) = **86%** độ lớn giữ lại | ✅ |
| §7.3 | Không năm nào gánh >60% hiệu ứng | <60% | năm gánh nhiều nhất **2022 = 20,9%**, 0 lần đổi dấu | ✅ |
| §8.1 | N ≥ 300 episode, ≥ 60 mã | — | **412** episode ghép cặp, **188** mã, 127 tháng | ✅ |

Không tiêu chí nào hỏng ⇒ theo đúng chữ của §9 (WEAK = "đúng (1) nhưng hỏng đúng một trong
(2)/(3)/(4)") verdict là **CONFIRMED**. Hạ verdict xuống ở đây sẽ chính là dời cột gôn sau khi
nhìn số — điều PREREG cấm theo cả hai chiều.

---

## 3. Số chính

### 3.1 Test B — episode chạm sàn (H2, PRIMARY, h=60 phiên)
`prox(t) ∈ [0,97;1,03]` tiếp cận **từ TRÊN** xuống · chứng = NON-PAYER cùng ngày, cùng ICB
industry, `rvol₆₀` trong dải [0,8;1,25]×, tối đa 3 mã gần nhất.

| Đại lượng | n | mean | median | CI 95% (block-bootstrap tháng) | t (two-way cluster) |
|---|---:|---:|---:|---|---:|
| MDD₆₀ **sự kiện** | 412 | −10,84% | −7,47% | [−12,99 ; −8,91] | −10,49 |
| MDD₆₀ **chứng** | 412 | −14,29% | −11,75% | [−16,39 ; −12,25] | −13,46 |
| **ΔMDD₆₀** | **412** | **+3,46 pp** | +2,69 | **[+2,15 ; +4,79]** | **+5,14** |
| ΔMDD₆₀ · IS (≤2019) | 136 | +4,53 | +4,73 | [+2,49 ; +6,79] | +4,11 |
| ΔMDD₆₀ · OOS (≥2020) | 276 | +2,93 | +1,60 | [+1,38 ; +4,56] | +3,48 |
| Δ**BHAR**₆₀ (cùng cặp) | 412 | +2,56 pp | +2,72 | [−0,55 ; +5,51] | +1,61 ❌ |

**Xác suất đuôi** — cùng một hiện tượng, đọc theo cách khác:

| | sự kiện | chứng |
|---|---:|---:|
| P(MDD₆₀ < −10%) | **42,7%** | 57,0% |
| P(MDD₆₀ < −20%) | **18,2%** | 26,5% |
| p10 của MDD₆₀ | −27,2% | −30,8% |
| % episode có MDD₆₀ ≥ 0 (không hề sụt) | **12,6%** | 4,9% |

Hiệu ứng **nằm ở giữa phân phối, không ở đuôi cực**: khoảng cách p50 là 4,3 pp còn ở p10 chỉ
3,6 pp. Đây **không** phải bảo hiểm thảm hoạ — chạm sàn cổ tức vẫn sụt trung bình −10,8%, và
1/5 số ca vẫn sụt quá −20%.

### 3.2 Bảng 4 ngưỡng CỐ ĐỊNH — TRỌNG TÀI của mọi kết luận (§7.1)
Miễn nhiễm hoàn toàn với hindsight của `deposit_rate_vn.py` (§1.1).

| thr | n ep | n matched | ΔMDD₆₀ | CI 95% | t | IS | OOS |
|---|---:|---:|---:|---|---:|---:|---:|
| deposit (primary) | 524 | 412 | **+3,46** | [+2,15;+4,79] | 5,14 | +4,53 (4,11) | +2,93 (3,48) |
| **5%** | 503 | 401 | **+2,65** | [+1,37;+3,95] | 3,98 | +3,50 (3,43) | +2,19 (2,49) |
| **6%** | 502 | 377 | **+2,52** | [+1,36;+3,66] | 4,20 | +3,39 (3,63) | +2,09 (2,73) |
| **7%** | 468 | 369 | **+3,69** | [+2,52;+4,84] | 6,01 | +3,80 (3,53) | +3,63 (5,02) |
| **8%** | 458 | 368 | **+3,82** | [+2,65;+4,98] | 6,33 | +5,51 (6,20) | +2,86 (3,77) |

**4/4 ngưỡng dương, mọi t ≥ 3,98, mọi nhánh IS và OOS đều dương và có ý nghĩa.** Đây là bằng
chứng mạnh nhất trong toàn nghiên cứu: kết quả **không** phụ thuộc vào series lãi suất proxy.
Độ lớn tăng đều theo ngưỡng (5% → 8%: +2,52 → +3,82 pp) — nhất quán với "ngưỡng càng cao thì
mã lọt vào càng rẻ/càng nhiều cổ tức".

### 3.3 Robustness Test B

| Chân | n | ΔMDD₆₀ | t | Đọc |
|---|---:|---:|---:|---|
| Bỏ CRISIS + EX-BULL (§7.2) | 306 | +2,97 | 4,92 | ✅ không phải hiệu ứng của khủng hoảng |
| STABLE-5 (§7.5) | 325 | +3,46 | 5,36 | ✅ trùng khít primary |
| Ghép thêm theo pretrend₆₀ (D5) | 198 | +3,00 | 3,50 | ✅ không phải do "mã đang rơi chậm hơn" |
| Bỏ dòng `stale_px` (D2) | 412 | +3,46 | 5,14 | ✅ bẫy `Price` không đụng tới kết quả |
| DT5G state 1 CRISIS | 89 | +5,44 | 2,43 | dương |
| state 2 BEAR | 39 | +2,85 | 2,31 | dương |
| state 3 NEUTRAL | 185 | +2,67 | 3,55 | dương |
| state 4 BULL | 82 | +3,72 | 3,07 | dương |
| state 5 EX-BULL | 17 | +1,81 | 1,65 | n quá nhỏ |
| Ngân hàng (ICB 8355) | **3** | −0,11 | −0,10 | ⚠️ **không đánh giá được** |
| Phi ngân hàng | 409 | +3,48 | 5,15 | toàn bộ hiệu ứng nằm ở đây |

**Dương ở cả 5 trạng thái DT5G**, mạnh nhất ở CRISIS. §7.4 (ngân hàng) **không chạy được**:
chỉ 3 episode / 2 mã — kết luận này **chỉ nói về phi ngân hàng**.

### 3.4 Test A — crossing ngưỡng (H1, KHÔNG đạt)

| Horizon | n | mean | median | CI | t | IS | OOS |
|---|---:|---:|---:|---|---:|---:|---:|
| BHAR₂₀ | 518 | +0,25 | −0,21 | [−0,73;+1,23] | 0,48 | +0,75 | −0,08 |
| **BHAR₆₀** (primary) | 516 | **+0,64** | **−0,97** | [−1,26;+2,61] | **0,67** | +1,48 (1,48) | +0,07 (0,05) |
| BHAR₁₂₀ | 503 | +1,76 | −1,66 | [−1,01;+4,56] | 1,27 | +3,76 (1,98) | +0,37 (0,19) |

Không đạt ở mọi horizon; **median âm ở cả ba** (mean dương do đuôi phải kéo). Bỏ CRISIS+EX-BULL
thì mean lật **âm** (−0,14, t=−0,13). LOO-year: **2022 gánh 68,4% > ngưỡng 60% của §7.3** ⇒ dù
t có đạt cũng phải hạ WEAK. Phân rã nguyên nhân (§5.1): `PRICE_DRIVEN` +2,08 (t=1,67),
`DIV_DRIVEN` +1,64 (t=0,62), `OTHER` −0,79 (t=−0,65) — không nhóm nào đạt.

Test A ở 4 ngưỡng cố định **tăng đơn điệu theo ngưỡng** (5%: −0,36 → 8%: +4,65, t=3,82). Đó là
chữ ký của **deep value / phần bù rủi ro**, không phải của "sàn": ngưỡng 8% chọn ra mã rẻ nhất
thị trường, và mã rẻ thì lợi suất kỳ vọng cao — một sự thật đã biết, không cần cơ chế cổ tức.
**Không tuyên bố gì từ chân này.**

---

## 4. Hạn chế — đọc TRƯỚC khi trích số

### 4.1 ⚠️ Placebo ghép cặp KHÔNG bằng 0 — hạn chế lớn nhất
PREREG §8 (bài học Sprint 2) buộc chạy toàn bộ pipeline trên **ngày giả** `t − 250` phiên và
báo cả dạng thô lẫn dạng đã trừ placebo. Kết quả (deviation D4):

| Đại lượng | n | mean | CI 95% | t |
|---|---:|---:|---|---:|
| ΔMDD₆₀ placebo (ngày giả, re-match đầy đủ) | 225 | **+1,29 pp** | [−0,18 ; +2,71] | 1,77 |
| **ΔMDD₆₀ ròng = sự kiện − placebo (cùng cặp episode)** | 225 | **+2,08 pp** | **[−0,34 ; +4,82]** | **1,63** ❌ |
| — IS | 54 | +5,10 | [−0,51;+13,00] | 1,41 |
| — OOS | 171 | +1,12 | [−1,27;+3,58] | 0,90 |

**Đọc thẳng: khoảng +1,3 pp trong con số +3,46 pp là "null của chính pipeline"** — tức khoảng
cách thường trực giữa mã trả cổ tức ổn định và mã không trả cùng ngành/cùng vol, vào một ngày
ngẫu nhiên bất kỳ, **không liên quan gì tới việc đang đứng ở sàn**. Placebo này tự nó không đạt
t≥2,0 (1,77), nên không thể khẳng định null ≠ 0; nhưng cũng không thể coi null = 0.

Phần ròng **+2,08 pp có t = 1,63, CI chứa 0** ⇒ **không phân biệt được với 0**. (n giảm còn 225
vì ngày giả phải tồn tại và ghép cặp lại được — mất power là có thật, nhưng không thể dùng nó
để bào chữa.)

**Hệ quả:** phần hiệu ứng **quy được cho cơ chế yield floor** nằm đâu đó trong khoảng
**+2 pp**, không phải +3,5 pp; và ở tiêu chuẩn chặt nhất (ròng placebo) nó **chưa đạt** ngưỡng
suy diễn của chính nghiên cứu này. §9 không đặt placebo-net vào tiêu chí GO/NO-GO, nên nó không
lật verdict — nhưng một quant-skeptic **có lý do chính đáng** để lập luận WEAK thay vì CONFIRMED.
Ghi ra đây như một câu hỏi mở, không giấu.

### 4.2 Hiệu ứng KHÔNG chỉ có ở sàn — nhưng ở sàn mạnh hơn ~5 lần
Chân falsification `far_from_floor` (D5): lấy episode có `prox > 1,3` — giá ở **xa phía trên**
sàn, nơi cơ chế lẽ ra không áp dụng:

| | n | ΔMDD₆₀ | CI | t |
|---|---:|---:|---|---:|
| Ở sàn (`prox` ∈ [0,97;1,03]) | 412 | **+3,46** | [+2,15;+4,79] | 5,14 |
| Xa sàn (`prox` > 1,3) | 1.391 | **+0,70** | [−0,04;+1,44] | 1,84 |

Xa sàn hiệu ứng **gần như biến mất** (+0,70, không có ý nghĩa) — đây là bằng chứng **ủng hộ
tính đặc thù** của vị trí "ở sàn", và là chân robustness thuyết phục nhất bên cạnh bảng 4 ngưỡng.
Nhưng nó không hoàn toàn bằng 0, nhất quán với §4.1.

### 4.3 `ticker.DY` KHÔNG phải nguồn kiểm chứng độc lập
Selfcheck T5 (§10.3) cho Spearman ρ = **1,0000**, max|Δ| = 2,8e-14 pp trên n=360.143. Trùng
khớp **tuyệt đối** ⇒ `ticker.DY` chính là cùng một đại lượng (cổ tức tiền mặt trailing / `Price`
thô) và gần như chắc chắn **chung nguồn upstream** với nghiên cứu này. Nó xác nhận **công thức
và đơn vị** — nó **không** xác nhận dữ liệu bằng một đường đi thứ hai. Đừng trích T5 như bằng
chứng độc lập.

### 4.4 Các hạn chế còn lại
- **Không có alpha lợi suất**: ΔBHAR₆₀ = +2,56 pp, t=1,61. Cơ chế này **chỉ** nói về đuôi trái.
- **Ngân hàng: n=3.** Mọi phát biểu ở đây là về **phi ngân hàng**. §7.4 không chạy được.
- **Không phải bảo hiểm**: chạm sàn vẫn sụt trung bình −10,8%; 18,2% số ca sụt quá −20%.
- `deposit_rate_vn.py` là PROXY có hindsight nhẹ (§1.1) — đã trung hoà bằng bảng 4 ngưỡng cố
  định, nhưng con số "primary" tự nó vẫn mang khuyết điểm đó.
- Ghép cặp đóng được ICB industry + vol + (chân D5) pretrend. **Không** đóng được: quy mô, thanh
  khoản, sở hữu nhà nước, chất lượng lợi nhuận.

---

## 5. Hàm ý — và ranh giới của nó

**Được phép nói:** với mã phi ngân hàng trả cổ tức tiền mặt ổn định ≥3 năm, thời điểm giá rơi
xuống vùng yield ≈ lãi suất huy động đi kèm **drawdown 60 phiên nông hơn ~2–3,5 pp** so với mã
cùng ngành cùng biến động không trả cổ tức, và **xác suất sụt quá −10% thấp hơn ~14 pp**
(42,7% vs 57,0%). Hiệu ứng nhất quán qua 4 ngưỡng cố định, cả IS lẫn OOS, cả 5 regime DT5G.
Đây là câu trả lời **ủng hộ quan sát ban đầu của user** ở đúng chân mà user nêu.

**KHÔNG được nói:**
- ✗ "Có sàn giá" theo nghĩa giá không thủng — 18,2% số ca vẫn sụt quá −20%.
- ✗ "Nên mua khi yield chạm lãi suất huy động" — chân lợi suất (H1) **không đạt**, t=0,67.
- ✗ Bất cứ điều gì về ngân hàng (n=3).
- ✗ Coi +3,46 pp là độ lớn có thể mang đi dùng — sau khi trừ placebo còn ~+2 pp và **không đạt**
  ý nghĩa thống kê (§4.1).

**Đề xuất KHÔNG wire.** Đây là tri thức **định cỡ rủi ro / due-diligence**, cùng loại với kết
luận Sprint 2 corp-action, không phải tín hiệu vào lệnh. Nếu muốn dùng thật, đường đi đúng là:
`prox` như một **trường thông tin** trong bảng due-diligence ứng viên mua (giống
`upcoming_exdate`/`insider_net_sell` đang chờ quant-skeptic), **không** phải một gate.

---

## 6. Câu hỏi mở (không tự trả lời trong job này)

1. **Placebo-net không đạt t≥2,0** (§4.1) — cần quant-skeptic phán: CONFIRMED theo chữ §9, hay
   hạ WEAK vì chân ròng? Đây là câu hỏi phương pháp luận, không phải câu hỏi dữ liệu.
2. Vì sao hiệu ứng ở **giữa** phân phối (p50: 4,3 pp) mà không ở **đuôi** (p10: 3,6 pp)? Một
   "sàn" thật lẽ ra phải mạnh nhất ở đuôi. Đây là bằng chứng ngược với cơ chế vật lý "dòng tiền
   tiết kiệm đỡ giá", và nghiêng về giải thích "mã cổ tức ổn định = doanh nghiệp ổn định hơn".
3. Ngân hàng — cần định nghĩa mẫu riêng (ICB 8355 gần như không lọt STABLE-3 vì trả bằng cổ phiếu).
4. Chân H1 tăng đơn điệu theo ngưỡng (5% → 8%) là deep-value hay là cổ tức? Tách được bằng cách
   ghép cặp theo PE/PB — **cần PREREG riêng**, không phải robustness của job này.

---

## 7. Tái lập

```bash
cd mike/agents/Taylor/research/dividend_yield_floor_20260818
python3 build.py       # panel.csv.gz + bench_ew.csv + dt5g.csv (BQ; ~10')
python3 analyze.py     # out/results.json
python3 selfcheck.py   # 20/20 PASS
env -u TZ python3 selfcheck.py && TZ=UTC python3 selfcheck.py   # phải trùng từng byte
```
Seed `20260818`, 10.000 block-bootstrap (block = tháng dương lịch), t-stat two-way cluster
(ticker × năm-tháng, Cameron–Gelbach–Miller). Artifact: `out/results.json`,
`out/episodes_testA_deposit.csv`, `out/episodes_testB_deposit.csv`.
