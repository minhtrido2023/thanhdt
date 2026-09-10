# AMH #3 + #4 — Change-point trên chuỗi IC & Fitness matrix trục-2 breadth-tercile PIT

> Taylor · job `Taylor_20260910_131908` · 2026-09-10 · **PAPER-ONLY, không wire gì vào production**
> Đây là công cụ **CHẨN ĐOÁN**, không phải return-enhancer. Kỳ vọng ΔCAGR ≈ 0.
> Bối cảnh: `mike/kb/projects/amh-adaptivity-review-20260910.md` khoảng trống **G3** (bước 1) và
> **G5+G6** (bước 2).
> Artifact: cùng thư mục — `changepoint.py`, `fitness2.py`, `tier3_isoos.py` + `*_out.txt` + `*.csv`.

---

## 0. Đọc 60 giây

| Câu hỏi được giao | Trả lời |
|---|---|
| Change-point (CUSUM/BOCPD) có tốt hơn nhãn 12M hiện tại không? | **KHÔNG.** Chậm hơn 2 tháng, false-alarm 35%, chỉ 5% alarm trùng điểm gãy thật. **NO-GO** cho dòng `P(regime-shift)`. |
| Điểm gãy tìm ra có trùng sự kiện thật không? | Gần như không có điểm gãy nào để trùng — chỉ **3 điểm gãy có ý nghĩa trên CẢ 10 signal × 12,5 năm**. Momentum flip 04/2026 **không** phải điểm gãy. |
| Momentum chết ở MỌI state hay chỉ NEUTRAL breadth-thấp? | **Chết ở MỌI ô, kể cả ô mạnh nhất của nó.** Không có trục điều kiện nào cứu được. Vết gãy là **THỜI GIAN (~2020)**, không phải regime. |
| Value/quality mạnh lên ở đâu? | **PE mạnh lên ở KHẮP NƠI** (IS −0,014 → OOS −0,081\*, LOO cực chặt). **ROE_Min5Y GIỮ NGUYÊN** qua vết gãy (+0,052\* → +0,063). FSCORE thì suy (+0,081\* → +0,018). |
| Sản phẩm phụ đáng giá nhất | **Cổng `|t|≥2` của `edge_health_monitor.py` đang phóng đại ~1,5–2,4×** vì chuỗi IC fwd-3M chồng lấn. Sửa đúng thì **nhãn `FLIPPED` của mom_200 sẽ KHÔNG được phát ra.** |

---

## 1. Nền: dữ liệu, môi trường, control leg

- Nguồn (đã tra `mike/kb/data_registry/index.md` trước khi chọn):
  - `data/edge_health_ic.csv` — chuỗi IC fwd-3M theo tháng, do chính `edge_health_monitor.py`
    production ghi (10 signal × 150 tháng, 2014-01 → 2026-06). Đây là chuỗi mà luật 12M đang chạy trên.
  - `data/edge_panel.csv` — panel gốc (29.687 obs, 438 mã, `ticker_prune`, liq ≥ 1e9).
  - `tav2_mike.universe_pit` — **CANONICAL** cho breadth (registry `price-volume/universe_pit.md`).
  - `tav2_bq.vnindex_5state_dt5g_live` — **CANONICAL** cho DT5G (registry + CLAUDE.md § bẫy nhãn bảng).
- Interpreter: `$DNA_PYEXE` = `/home/trido/thanhdt/wc_venv/bin/python`.
- **Control leg PASS**: dựng lại chuỗi IC fwd-3M từ panel khớp artifact pin
  **max |Δ| = 9,97e-17**. (Phải sao chép cả bước winsorize `fwd_3m` 0,5%/99,5% của
  `load_panel()`; thiếu bước đó lệch 5,8e-3 — đủ nhỏ để trông "đúng" nhưng không phải 0.)
- `git status` sạch trên mọi file `.py` production — không sửa gì.

### N khai báo trung thực
150 tháng **KHÔNG** phải 150 quan sát độc lập. IC fwd-3M lấy mẫu hàng tháng trên cửa sổ
forward 3 tháng ⇒ **MA(2) by construction**:

| signal | ac1 (3M) | n_eff (3M) | ac1 (1M) | n_eff (1M) |
|---|---|---|---|---|
| pb_z | 0,70 | 27 | 0,15 | 110 |
| PB | 0,68 | 29 | 0,05 | 135 |
| PE | 0,55 | 44 | 0,03 | 141 |
| ROIC5Y | 0,66 | 31 | −0,05 | 166 |
| FSCORE | 0,49 | 52 | 0,15 | 111 |
| ROE_Min5Y | 0,71 | 26 | −0,01 | 152 |
| mom_200 | 0,66 | 31 | 0,23 | 95 |
| D_RSI | 0,44 | 58 | 0,24 | 91 |
| D_CMF | 0,42 | 62 | −0,02 | 156 |
| C_L1M | 0,33 | 75 | 0,01 | 146 |

Mọi t-stat trong báo cáo này dùng **Newey-West HAC lag 2** (đúng độ trùm), không phải t thô.

---

## 2. BƯỚC 1 (AMH #3) — Change-point: **NO-GO**

### Thiết kế (mọi tham số PRE-REGISTERED, textbook, không quét lưới)
- **CUSUM** hai phía chuẩn hoá, `k=0,5` (bắt dịch chuyển 1σ), `h=5`, burn-in 24 tháng, refractory 6 tháng.
- **BOCPD** (Adams & MacKay 2007), Gaussian–NIG liên hợp, hazard `1/36` tháng; output
  `P(run_length ≤ 2)`, ngưỡng báo động 0,50.
- Cả hai đều **CAUSAL**: tại tháng *t* chỉ thấy `x[0..t]`.
- **Ground truth (hindsight, detector không được thấy)**: binary segmentation, đoạn tối thiểu 12
  tháng, ngưỡng lấy từ **block-permutation** 999 lần, **block = 3** (đúng độ trùm fwd-3M).
- **Baseline**: replay causal `edge_health_monitor.classify()` từng tháng.

### Kết quả

| | CUSUM | BOCPD | Nhãn 12M hiện tại |
|---|---|---|---|
| số alarm (fwd-3M, 10 signal) | 20 | 7 | — |
| false-alarm¹ | **35%** | 28,6% | — |
| % alarm trùng điểm gãy hindsight (±6 th) | **5%** | **0%** | — |
| bắt được / tổng điểm gãy | 2/3 | 0/3 | 2/3 |
| median lag (tháng) | **6,0** | — | **4,0** |

¹ *false-alarm = phát hiện mà trung bình 12 tháng sau đó không lệch ≥ 0,5σ so với 12 tháng trước.*

**Không có dose-response** — dấu hiệu nhiễu, đúng như `quant-research` mục 10:

```
CUSUM h=4 → false-alarm 56,5%  |  h=5 → 35,0%  |  h=6 → 46,7%   (KHÔNG đơn điệu)
```

### Vì sao thất bại — và đây mới là phần quan trọng
Với null **block-permutation** trung thực, cả 10 signal × 12,5 năm chỉ còn **3 điểm gãy có ý
nghĩa**: `pb_z` 2020-03, `D_RSI` 2015-01 và 2018-03. Với null i.i.d. ngây thơ, con số đó là **17**
— tức là 14/17 "điểm gãy" chỉ là ảo ảnh của một null quá hẹp. Nói cách khác: **chuỗi IC hầu như
không có điểm gãy để mà phát hiện**; SNR tại độ phân giải tháng quá thấp. Detector nào cũng chỉ
đang đuổi theo nhiễu.

### Đề xuất bước 1
1. **KHÔNG** thêm dòng `P(regime-shift)` vào `data/edge_health_block.md`. Nó sẽ báo muộn hơn và
   ồn hơn nhãn đang có.
2. **NÊN sửa `edge_health_monitor.py`, hàm `edge_row()` (dòng 265–271)** — 1 dòng:
   ```python
   # hiện tại
   tstat = full / (sd / np.sqrt(n))
   # đề xuất — chuỗi IC fwd-3M chồng lấn, n danh nghĩa không phải n độc lập
   ac1  = ic.autocorr(1)
   neff = n * (1 - ac1) / (1 + ac1)
   tstat = full / (sd / np.sqrt(neff))
   ```
   Hiệu ứng đo thật (t danh nghĩa → t theo n_eff):

   | signal | t_nom | t_eff | hệ quả |
   |---|---|---|---|
   | ROIC5Y | +3,24 | **+1,46** | mất tư cách robust |
   | ROE_Min5Y | +4,03 | **+1,67** | mất tư cách robust |
   | **mom_200** | **+3,68** | **+1,67** | **mất tư cách robust ⇒ nhãn `FLIPPED` không được phát** |
   | PE | −6,20 | −3,34 | vẫn robust |
   | FSCORE | +4,90 | +2,88 | vẫn robust |
   | D_RSI | +4,78 | +2,98 | vẫn robust |

   Sửa này làm nhãn **CHẶT hơn**, không lỏng hơn — nên nó là hướng an toàn. **Chưa sửa**; cần
   user + `quant-skeptic` duyệt trước vì `classify()` là đầu vào của allocator edge-gate.
3. Muốn chỉ báo **NHANH** cho BAL (khoảng trống G2) thì đổi sang **fwd-1M**: `ac1` chỉ 0,01–0,24,
   `n_eff` 91–166 — gần như độc lập thật, và không phải đợi 3 tháng để realize.

### Còn "momentum flip 04/2026" thì sao?
- **Không có điểm gãy nào phát hiện được ở `mom_200`** (0 điểm với null block-perm).
- `P_shift_now = 0,292` — cao nhất trong 10 signal, nhưng dưới mọi ngưỡng dùng được.
- Hai tháng realized cuối: **2026-05 `+0,285`, 2026-06 `+0,382`** — dương mạnh, đang đảo lại.
- Roll-off (giả định IC tương lai = 0,00, tức null): `recent12` quay lại **dương sau +4 tháng`.
- ⇒ Nhãn `FLIPPED` là **artifact của cửa sổ 12M còn chứa 2025-09…2026-03**, không phải một lần
  đổi chế độ đo được. Kết hợp với t_eff = 1,67 ở trên: nhãn này lẽ ra đã không nên được phát.

---

## 3. BƯỚC 2 (AMH #4) — Fitness matrix hồi sinh, trục 2 = breadth tercile PIT

### 3 lỗi của `fitness_matrix.py` đã sửa trong bản dựng lại (`fitness2.py`)
| # | Lỗi bản cũ | Bằng chứng |
|---|---|---|
| 1 | **Look-ahead**: gán state cho tháng bằng **modal state của CẢ tháng** ⇒ dùng phiên SAU ngày hình thành vị thế | `fitness_matrix.py::load()` dòng `modal = st.groupby("ym")["state"].agg(...mode...)`. Đo thật: **modal ≠ state-PIT-tại-hình-thành ở 24/150 tháng (16%)** |
| 2 | Đọc `data/dt5g_vnindex.csv` thay vì bảng canonical | file đó **lệch 52/3121 phiên** so với `tav2_bq.vnindex_5state_dt5g_live`, và đứng từ 2026-07-09 (mtime 07-13) |
| 3 | t-stat thô trên chuỗi chồng lấn | như §1 |

`fitness2.py` dùng: state **PIT tại đúng phiên hình thành**, bảng **live canonical**, t **Newey-West lag 2**.

### Breadth — chép đúng quy ước, không tự chế
Sao chép nguyên văn `macro_state_live._breadth_sql` với `BREADTH_SOURCE="pit"`:
```
breadth_t = AVG(Close_t > MA200_t) trên {ticker : universe_pit.in_universe ngày t}
phiên t phân loại bằng breadth_{t-1}          (PIT, không nhìn cùng phiên)
tercile = phân vị 1/3, 2/3 của 252 phiên GẦN NHẤT KẾT THÚC tại t-1   (rolling, không toàn mẫu)
```
Breadth hôm nay (2026-09-10): **26,6%**.

### N thật của lưới — đọc cái này TRƯỚC

| state \ tercile | B-LOW | B-MID | B-HIGH | TỔNG |
|---|---|---|---|---|
| CRISIS | 11 | 9 | 4 | 24 |
| BEAR | 8 | 3 | 3 | 14 |
| **NEUTRAL** | **29** | **27** | **32** | **88** |
| BULL | 5 | 10 | 6 | 21 |
| EXBULL | 0 | 0 | 3 | 3 |
| **TỔNG** | 53 | 49 | 48 | **150** |

Sàn công bố: `n ≥ 10` mới in ô; `n ≥ 18` mới coi là kết luận được.
**Chỉ 30/130 ô (23%) đạt hạng kết luận.** Trong lưới 5×3, **BEAR và EXBULL không có ô nào đọc
được**, CRISIS chỉ có 1 (B-LOW, n=11, vẫn dưới hạng kết luận). Đây chính là cái bẫy dispatch cảnh
báo: **không vẽ bảng đẹp rồi đọc như thật** — file `.png` cố tình để trắng những ô N mỏng.

### Tier 1 — biên (N dày nhất)

**Theo DT5G state** (mean fwd-3M IC, `*` = |t_NW| ≥ 2):

| signal | FULL n150 | CRISIS n24 | BEAR n14 | NEUTRAL n88 | BULL n21 |
|---|---|---|---|---|---|
| Mom: Close/MA200 | +0,060\* | −0,006 | −0,015 | **+0,103\*** | +0,011 |
| Mom: D_RSI | +0,058\* | −0,011 | +0,013 | **+0,090\*** | +0,054 |
| Qual: ROE_Min5Y | +0,054\* | **+0,117\*** | +0,012 | +0,054\* | +0,020 |
| Qual: ROIC5Y | +0,035\* | **+0,087\*** | +0,033 | +0,029 | +0,008 |
| Qual: FSCORE | +0,048\* | +0,043 | +0,026 | +0,055\* | +0,032 |
| Val: PE | −0,048\* | **−0,072\*** | −0,029 | −0,027 | **−0,099\*** |
| Val: PB | −0,016 | +0,028 | −0,092 | +0,008 | **−0,099\*** |
| Val: PB_z | −0,007 | −0,061\* | −0,078 | +0,027 | −0,045 |
| Flow: CMF | +0,016 | −0,035 | −0,063 | +0,044\* | +0,016 |
| Pos: C_L1M | +0,011 | −0,048 | +0,031 | +0,029 | +0,011 |

**Theo breadth tercile:**

| signal | FULL | B-LOW n53 | B-MID n49 | B-HIGH n48 |
|---|---|---|---|---|
| Mom: Close/MA200 | +0,060\* | +0,028 | +0,083\* | +0,073 |
| Mom: D_RSI | +0,058\* | +0,040 | +0,056\* | +0,080\* |
| Qual: ROE_Min5Y | +0,054\* | +0,051 | +0,058\* | +0,053 |
| Val: PE | −0,048\* | **−0,075\*** | −0,046\* | −0,020 |
| Val: PB_z | −0,007 | −0,063\* | +0,015 | +0,033 |

Đọc: **breadth tách rất yếu** một khi đã điều kiện hoá theo state. Momentum không đơn điệu theo
breadth (+0,028 / +0,083 / +0,073). Trục có sức tách thật là DT5G, không phải breadth.

### Tier 2 — lưới 2 chiều: momentum

Chỉ **3 ô đạt hạng kết luận** cho `mom_200`, và **cả 3 đều là NEUTRAL**:

| ô | n | mean IC | t_NW | hit | L/S spread |
|---|---|---|---|---|---|
| NEUTRAL × B-LOW | 29 | **+0,087** | 2,04 | 55% | +3,47% |
| NEUTRAL × B-MID | 27 | **+0,118** | 2,70 | 74% | +6,69% |
| NEUTRAL × B-HIGH | 32 | **+0,104** | 2,21 | 69% | +5,40% |

Mọi ô có IC âm (CRISIS×B-LOW −0,046 n11; BULL×B-LOW −0,110 n5; BEAR×B-MID −0,055 n3) đều
**dưới hạng kết luận** — tức là chính những ô "momentum chết" lại là những ô ta **không được phép
kết luận**.

> **Trả lời trực tiếp câu hỏi được giao — nhưng chưa xong:** trên toàn mẫu, momentum **không**
> chết ở NEUTRAL breadth-thấp. Nó **chỉ sống** ở NEUTRAL, và sống ở cả 3 tercile breadth. Giả
> thuyết "chết ở NEUTRAL breadth-thấp" bị **BÁC BỎ**. Nhưng câu trả lời toàn mẫu này gây hiểu
> lầm — xem Tier 3.

### Tier 3 — vết gãy thật là THỜI GIAN, không phải regime

Tách IS(2014-19)/OOS(2020+) — mốc **pre-registered** theo chuẩn fleet, không phải chọn để ra kết quả:

**`mom_200`:**

| phạm vi | IS 2014-19 | | OOS 2020+ | |
|---|---|---|---|---|
| | IC (n) | t_NW | IC (n) | t_NW |
| ALL | **+0,135** (72) | 3,91 | −0,009 (78) | −0,32 |
| NEUTRAL | **+0,164** (54) | 5,09 | +0,005 (34) | 0,16 |
| NEUTRAL × B-LOW | **+0,119** (18) | 2,22 | +0,034 (11) | 0,54 |
| NEUTRAL × B-MID | **+0,192** (15) | 3,96 | +0,026 (12) | 0,52 |
| NEUTRAL × B-HIGH | **+0,182** (21) | 4,27 | −0,046 (11) | −0,93 |
| B-LOW | +0,071 (25) | 1,22 | −0,011 (28) | −0,27 |
| B-MID | **+0,161** (21) | 4,15 | +0,024 (28) | 0,56 |
| B-HIGH | **+0,176** (26) | 3,21 | −0,048 (22) | −0,90 |

**8/8 phạm vi dương ở IS (6/8 có ý nghĩa). 8/8 phạm vi ≈ 0 ở OOS (0/8 có ý nghĩa, |t| < 1 tất cả).**
`D_RSI` giống hệt: ALL +0,107\* → +0,013; NEUTRAL +0,135\* → +0,019; 0/8 có ý nghĩa OOS.

**Leave-one-year-out** (trung bình IC theo năm 2020+, bỏ từng năm):
`mom_200` full 2020+ = **−0,005**; LOO chạy trong **[−0,027; +0,015]** — không năm nào kéo được
về gần +0,135 của IS. Không phải hiệu ứng của một năm cá biệt (không phải COVID 2020, không phải
sập 2022).

> ### ⇒ Trả lời cuối cùng cho review VPI/BAL 09-16
> **Momentum chết ở MỌI ô sau 2020 — kể cả ô mạnh nhất của chính nó.** Không có trục điều kiện
> nào (DT5G state, breadth tercile, hay tương tác của hai) khôi phục được edge OOS. Kết quả Tier
> 1/2 "momentum sống ở NEUTRAL" là **sự thật CHỈ của giai đoạn IS**: NEUTRAL IS +0,164 (t 5,09)
> → OOS +0,005 (t 0,16).
>
> Hệ quả cho quyết định: **không thể cứu BAL bằng cách thêm một cổng regime/breadth.** Nếu muốn
> giữ BAL thì lý do phải nằm ở chỗ khác (SIGNAL_V11 khác `mom_200` thô, hoặc yieldcombo, hoặc
> vai trò đa dạng hoá), **không phải ở chỗ "chỉ cần chọn đúng chế độ"**. Đây là bằng chứng ủng hộ
> hướng **G1 — BAL edge-gate đối xứng với LAG**, chứ không phải hướng regime-conditioning.

### Value / quality mạnh lên ở đâu

| signal | IS 2014-19 | OOS 2020+ | LOO OOS (min…max) | đọc |
|---|---|---|---|---|
| **Val: PE** | −0,014 (ns) | **−0,081\*** | [−0,091; −0,070] | **MẠNH LÊN, và ổn định nhất trong toàn nghiên cứu.** Có ý nghĩa OOS ở **cả 3** tercile breadth (−0,085\*/−0,074\*/−0,078\*) và ở NEUTRAL (−0,067\*). Không phụ thuộc điều kiện nào — nó khoẻ ở khắp nơi. |
| **Qual: ROE_Min5Y** | +0,052\* | +0,063 | [+0,043; +0,089] | **GIỮ NGUYÊN** qua vết gãy — signal duy nhất không đổi độ lớn. Ô OOS mạnh nhất: B-MID +0,095\*. |
| Qual: ROIC5Y | +0,040\* | +0,030 | — | suy nhẹ, giữ dấu. Ô riêng mạnh: **CRISIS +0,087\*** (n24). |
| **Val: PB_z** | +0,056 | **−0,064\*** | — | **ĐẢO DẤU thật**: IS đắt-so-với-lịch-sử-mình thắng, OOS rẻ-so-với-lịch-sử-mình thắng. Có ý nghĩa OOS ở B-LOW (−0,098\*) và B-MID (−0,040\*). |
| Qual: FSCORE | +0,081\* | +0,018 (ns) | — | **SUY** — khớp với nhãn `FADING` mà monitor đang phát. |
| Flow: CMF, Pos: C_L1M | +0,052\*, +0,052\* | −0,017, −0,026 | — | sập cùng nhóm giá với momentum |

**Bức tranh AMH gọn:** mọi signal **dựa trên GIÁ** (momentum, RSI, CMF, C_L1M) sụp về ~0 quanh
2020; **định giá cơ bản** (PE, và PB_z theo hướng đảo dấu) **mạnh lên**; **sàn chất lượng**
(ROE_Min5Y, ROIC5Y) **giữ**. Điều này nhất quán với thiết kế 8L hiện tại (rating là **cổng nhị
phân trên sàn chất lượng**, và `1/PE` là trục trội) — nói cách khác, phần hệ thống đang đứng vững
đúng là phần dữ liệu nói vẫn còn sống.

---

## 4. Ranh giới & caveat bắt buộc mang theo

1. **Panel là `ticker_prune` liq ≥ 1e9, KHÔNG phải sổ BAL.** `mom_200` thô ≠ `SIGNAL_V11`. Kết
   luận ở đây là về **signal**, không phải trực tiếp về NAV của BAL. Muốn kết luận cấp sổ phải
   chạy full-engine (`quant-research` mục 6) — chưa làm trong job này, và không nên suy diễn thay.
2. **Không dùng `p-value` làm cổng duy nhất** — N chu kỳ VN chỉ ~2–3 (mandate 08-25). Sức nặng
   ở đây đến từ **dose-response + LOO + tính nhất quán 8/8 phạm vi**, không từ một con số t.
3. **Không recommend wire config nào** ⇒ theo `quant-research` mục 13, **DSR/PBO không áp dụng**
   và đã bỏ qua có chủ ý. `N_trials`: bước 1 so 2 detector × 3 tham số sensitivity (6, đều
   pre-registered, đều báo cáo); bước 2 không chọn config, chỉ mô tả.
4. Ba đề xuất sửa code ở §2 và §3 **CHƯA thực hiện**. Chạm `classify()` là chạm đầu vào của
   allocator edge-gate ⇒ cần `quant-skeptic` CONFIRMED + user duyệt trước
   (`quant-research` mục 15).
5. `fitness2.png` cố tình để **trắng** mọi ô `n < 10`. Đừng "điền cho đẹp".

## 5. Việc tiếp theo được ưu tiên (đề xuất, chưa làm)

1. Đưa **§2 đề xuất 2** (t theo `n_eff`) qua `quant-skeptic` → nếu CONFIRMED thì sửa 1 dòng ở
   `edge_health_monitor.py::edge_row()`. Rẻ, làm nhãn chặt hơn, và sẽ tự gỡ nhãn `FLIPPED` sai
   của `mom_200`.
2. Sửa text stale trong `data/edge_health_block.md` (khoảng trống **G8**) — độc lập, rẻ.
3. **G1 — BAL edge-gate đối xứng LAG**, dùng **fwd-1M** làm chỉ báo nhanh (n_eff 91–166, gần độc
   lập thật). Đây là hướng mà bằng chứng §3 Tier 3 ủng hộ, thay cho hướng regime-conditioning.
4. `fitness_matrix.py` cũ: **archive**, đừng sửa path rồi chạy lại — nó có look-ahead ở 16% số
   tháng và đọc nguồn DT5G sai. `fitness2.py` là bản thay thế.
