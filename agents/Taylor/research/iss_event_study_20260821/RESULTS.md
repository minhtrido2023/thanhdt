# KẾT QUẢ — Rights-offering (ISS/Rights) event study — **NO-GO trên H1 như đăng ký**

- **Job**: `Taylor_20260821_103727` (HƯỚNG C) · **PREREG**: `PREREG.md`, commit `c46d6671` (trước khi đọc outcome)
- **Script**: `analyze.py` · **Artifact**: `events.csv`, `control.csv`, `results_events_enriched.csv`,
  `results_stats.csv`, `results_h2_discount.csv`, `q_common.sql`/`q_events.sql`/`q_control.sql`
- **KHÔNG WIRE.** Chờ Mike review + quant-skeptic.

## 1. Verdict

| | |
|---|---|
| **PREREG §7** | **NO-GO** — H1 (BHAR_60 ≤ −2pp, t ≤ −2,0) **không đạt ở bất kỳ scope nào**; FULL thậm chí **DƯƠNG** (+1,22pp, t=+0,85), IS/OOS ngược dấu (−0,03 vs +3,91), hiệu ròng ghép cặp cũng dương (+1,57pp, t=+1,18) |
| **H2 (secondary)** | **BÁC BỎ** — discount sâu KHÔNG underperform nhiều hơn; nếu có thì NGƯỢC hướng giả thuyết và không sống qua OOS |
| **LEAD (phải PREREG riêng)** | Trung vị âm bền vững: **60,4% sự kiện có BHAR_60 < 0, median −3,51pp, Wilcoxon p=2,6e−4**. Mean bị kéo dương bởi đuôi phải béo. Xem §5 — **đây KHÔNG phải kết quả của job này.** |

## 2. Mẫu & hai deviation đã khai trước

- `event_code='RIGHTS'` **không tồn tại** ⇒ dùng `event_code='ISS' AND issue_method_code='Rights'`
  (PREREG §3.1-1). `value_per_share` **NULL 100% trên mọi dòng ISS** ⇒ H2 dùng proxy
  `issue_price = total_value / issue_volumn` (PREREG §3.1-2).
- 1.568 sự kiện `Rights`+`executed`+có `exright_date` → **910** có dòng giá trong `tav2_bq.ticker`
  tại/liền sau ex-right (**634 mã không nằm trong bảng giá** — `corporate_action` phủ 1.792 mã còn
  `ticker` chỉ 1.272; đây là giới hạn ĐỘ PHỦ, không phải survivorship) → **632 sự kiện `in_universe_pit`**.
- **0 sự kiện mất vì thiếu 60 phiên giá phía sau** ⇒ không có sai lệch sống sót do delist trong cửa sổ.
- 369 mã · 2005-02-24 → 2026-04-17 · **IS 431 / OOS 201** (cả hai ≫ 30 ⇒ không WEAK_N).
- Control ghép cặp có cho **624/632** sự kiện, trung vị **34 mã control**/sự kiện (cùng `icb_code_lv1`,
  cùng `t0`, `in_universe_pit`, không có `Rights` nào trong ±90 ngày).
- Nhãn DT5G chỉ có cho **359/632** (bảng phủ từ 2014) — hệ quả xem deviation log #1.

## 3. Kết quả chính — `BHAR_60` trên `Close` (PRIMARY)

| scope | n | mean | median | %âm | t | p | block-boot 95% |
|---|---:|---:|---:|---:|---:|---:|---|
| FULL | 632 | **+1,22pp** | −3,51pp | 60,4% | +0,85 | 0,39 | [−2,33 ; +5,10] |
| IS (≤2019) | 431 | −0,03pp | −3,32pp | 60,6% | −0,02 | 0,98 | [−4,02 ; +4,54] |
| OOS (≥2020) | 201 | +3,91pp | −3,59pp | 60,2% | +1,19 | 0,24 | [−2,82 ; +11,94] |
| EX_REGIME (như đăng ký) | 575 | −0,47pp | −3,72pp | 62,1% | −0,40 | 0,69 | [−3,72 ; +3,07] |
| EX_REGIME_STRICT (có nhãn DT5G) | 302 | −1,81pp | −4,55pp | 64,9% | −1,34 | 0,18 | [−4,57 ; +1,15] |

**Hiệu ròng ghép cặp (`event − control cùng ngành/cùng ngày`)**:
FULL **+1,57pp** t=+1,18 · IS +1,24 t=+0,95 · OOS +2,26 t=+0,74 · STRICT −0,95 t=−0,72.
Mọi CI bootstrap chứa 0.

⇒ **Không có bằng chứng underperformance theo trung bình.** Giả thuyết prior ("rights issue = tín
hiệu cần vốn ⇒ giá tệ") **không được số liệu VN 2005-2026 ủng hộ ở tầng trung bình**.

**Đối chứng cơ học trên `Price` (giá thô)**: FULL mean −0,54pp / median −3,99pp — **gần như trùng
kết quả `Close`**. Bẫy hệ quy chiếu §6 KHÔNG cắn ở thiết kế này, và đó là hệ quả của một lựa chọn
đăng ký trước: cửa sổ bắt đầu **TẠI/SAU** `exright_date` nên phần pha loãng đã nằm ngoài cửa sổ.
(Ở HƯỚNG A cửa sổ bắc QUA ex-date nên bẫy cắn rất mạnh: −6,83pp thuần kế toán.)

## 4. H2 — độ sâu discount (secondary, không quyết GO)

`discount = 1 − issue_price/Price(t0)`; sâu = `≥30%`. Tính được cho 551/632 sự kiện.

| scope | n_deep | n_shallow | mean deep | mean shallow | Δ (deep−shallow) | t | p |
|---|---:|---:|---:|---:|---:|---:|---:|
| FULL | 327 | 224 | +2,02pp | −0,96pp | **+2,98pp** | +1,03 | 0,30 |
| IS | 201 | 149 | +1,35pp | −4,11pp | **+5,46pp** | +2,00 | 0,046 |
| OOS | 126 | 75 | +3,09pp | +5,30pp | −2,21pp | −0,35 | 0,73 |

**BÁC BỎ H2.** Hướng thực tế NGƯỢC với giả thuyết (deep discount làm TỐT hơn, không tệ hơn), và
riêng cái nominal-significant ở IS (p=0,046) **lật dấu hoàn toàn ở OOS** ⇒ nhiễu, không phải hiệu
ứng. Không có gì để mang sang production.

## 5. LEAD — trung vị âm bền vững (PHẢI PREREG RIÊNG, chưa phải kết luận)

Phân phối lệch phải rất mạnh: mean và median **ngược dấu** ở mọi scope. Thống kê phi tham số (thêm
sau khi nhìn dữ liệu — xem deviation log #2, KHÔNG được dùng lật verdict):

| scope | %âm | median | Wilcoxon p |
|---|---:|---:|---:|
| `bhar60_close` FULL | 60,4% | −3,51pp | 2,6e−4 |
| `bhar60_close` IS | 60,6% | −3,32pp | 1,8e−3 |
| `bhar60_close` OOS | 60,2% | −3,59pp | 5,3e−2 |
| `net_close` (ròng ghép cặp) FULL | 57,9% | −2,34pp | 1,1e−3 |
| `net_close` IS | 56,5% | −2,03pp | 3,6e−2 |
| `net_close` OOS | 60,7% | −3,19pp | 6,6e−3 |
| `bhar60_close` EX_REGIME_STRICT | 64,9% | −4,55pp | 1,6e−4 |

Đọc cho đúng: **cổ phiếu ĐIỂN HÌNH sau rights offering thua benchmark ~2–5pp trong 60 phiên, nhưng
một đuôi phải béo kéo trung bình về 0/dương.** Nhất quán IS/OOS, sống qua ghép cặp ngành, mạnh hơn
khi loại CRISIS/EX-BULL.

**Vì sao đây KHÔNG được tính là GO**: §7 khoá theo **trung bình + t-test**. Đổi sang thống kê trung
vị SAU khi đã nhìn kết quả chính là thứ pre-registration sinh ra để chặn — đúng nhóm lỗi
`coding_guidelines §18`/skill `quant-research`. Muốn theo thì:
- PREREG mới, khoá trước: thống kê = Wilcoxon/sign test trên `net_close`, ngưỡng median ≤ −2pp,
  `p < 0,01` cả IS lẫn OOS, + block bootstrap trên MEDIAN (bootstrap ở file này chạy trên MEAN).
- Và phải trả lời được câu hỏi nghiệp vụ **trước** khi đo: một tín hiệu mà median âm nhưng mean ≈ 0
  thì **né nó không tạo ra alpha** cho một book position-sizing đều — nó chỉ đúng nếu book đang
  đánh trọng số bằng nhau và ta chấp nhận bỏ luôn đuôi phải. Với V2.4 (12 slot, sizing theo NAV)
  điều này **không hiển nhiên có lợi** và phải chứng minh ở tầng NAV harness, không phải tầng event.

## 6. Tái lập

```bash
cd /home/trido/thanhdt/WorkingClaude && source ./wc_env.sh
# 3 query BQ: q_events.sql (events.csv), q_control.sql (control.csv) — cả hai gộp q_common.sql ở đầu
$DNA_PYEXE mike/agents/Taylor/research/iss_event_study_20260821/analyze.py
```
Seed bootstrap `20260821`, 5.000 vòng, block = tháng lịch của `exright_date`.
