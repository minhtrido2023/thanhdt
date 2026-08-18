# Top-5 sau mùa BCTC — full-universe PIT backtest → **NO-GO** (sleeve mới)

Job `Taylor_20260818_184457` (retry #4; 3 lần trước fail do outage Anthropic 529, không phải lỗi nghiên cứu).
Artifact: `agents/Taylor/research/top5_postearnings_sleeve_20260818/`. Engine `engine.py` + `run.py` + `variants.py`.
Interpreter pin: `/home/trido/thanhdt/wc_venv/bin/python` (§8). Threads=1.

## VERDICT: **NO-GO** cho việc tách thành sleeve đầu tư mới

Không phải vì quy tắc vô giá trị, mà vì **4 trong 5 tiêu chí GO đều trượt**, và cái trượt nặng nhất
là cái không sửa được bằng tinh chỉnh tham số: **toàn bộ edge nằm ở 8/48 mùa (2020-21)**.

| Tiêu chí | Kết quả | Đạt? |
|---|---|---|
| Edge sau chi phí vs VNINDEX (horizon chính) | mean +3,23%/mùa, **t=1,48**, bootstrap CI5 = **−0,23%** (chứa 0) | ❌ |
| Sống sót OOS | 2022+ (n=17): excVNI **−2,19%** t=−0,57; excSEC −0,13% t=−0,08 | ❌ |
| DSR ≥ 0,95 (§4) | **DSR_primary = 0,720**; best-of-24 = 0,938 | ❌ |
| PBO < 0,5 (§4) | **0,271** (CSCV S=8, 70 splits) | ✅ |
| Risk profile dùng được | **MaxDD −61,4%**, Calmar 0,30 (V2.4: DD −17,8%, Calmar 1,62) | ❌ |

## Vì sao NO-GO — 3 bằng chứng độc lập

**1. Edge tập trung vào một cửa sổ 2 năm.** Cắt theo 3 thời kỳ (horizon = giữ tới mùa kế tiếp):

| Thời kỳ | n mùa | sleeve | excVNI | excSEC |
|---|---:|---:|---:|---:|
| 2014-19 | 23 | +4,25% (t=1,93) | +2,53% (t=0,98) | +3,37% (t=1,86) |
| **2020-21** | **8** | **+22,92% (t=3,73)** | **+16,77% (t=3,50)** | **+7,88% (t=3,08)** |
| **2022+** | **17** | +0,22% (t=0,04) | **−2,19% (t=−0,57)** | −0,13% (t=−0,08) |

17 mùa gần nhất (hơn 4 năm) = **không còn gì**. NAV theo năm: 2023 +65,6% → 2024 −1,0% → 2025 −10,3% → 2026 −31,0%.

**2. Jackknife phá edge.** Bỏ 3/48 mùa tốt nhất: excVNI t **1,48 → 0,42** (mean 3,23% → 0,73%).
Kênh sector-relative bền hơn nhưng cũng rơi: t 2,45 → 1,68 (−top3) → 1,18 (−top5).

**3. Con số "5" không robust.** Trong lưới 24 biến thể khai báo trước, Top-5 xếp **hạng 11/24** theo Sharpe.
n_top=10/15 thắng rõ (Sharpe 1,01-1,07 vs 0,78). `ey` đơn lẻ ở top3 cho CAGR **−1,8%**.
"Top 5" là con số kể chuyện, không phải con số dữ liệu chọn.

## Cái DUY NHẤT sống sót (chưa đủ để wire, nhưng đáng ghi)

**Kênh so với NGÀNH, có điều kiện DT5G=BEAR.** Full-sample excSEC: mean +2,88%, median +2,80%,
win **70,8%**, t=2,45, CI5=+0,98% (loại 0) — sleeve **thắng peer cùng ICB** đều đặn hơn nhiều so với thắng VNINDEX.
Cắt theo state, BEAR là ô mạnh nhất và **sống sót cả khi bỏ 2020-21**: n=9, excSEC **+5,90% t=2,64**, excVNI +6,93% t=1,07.

Ngược lại **NEUTRAL 2022+ (n=7) LỖ có ý nghĩa**: excVNI −7,79% (t=−2,75), excSEC −4,94% (t=−2,16) —
mà NEUTRAL là state modal (28/48 mùa). Mua deep-value top-5 trong NEUTRAL gần đây là **phản tác dụng**.

⚠️ Ô BEAR là **1 trong 12 ô** của ma trận 4 state × 3 radar, chọn hậu nghiệm. Bonferroni 12 ô cần
t≳3,1 — t=2,64 với n=9 **chưa đạt**. Đây là LEAD, không phải kết luận. Ma trận đầy đủ: `out/matrix_primary.csv`.

## Điều kiện chất lượng — đã kiểm, đã đạt

- **PIT sạch, kiểm định phân biệt được**: trên 7.385 ticker-date mà giá trị khác nhau giữa quý đã công bố
  và quý kế chưa công bố, giá trị daily khớp **quý ĐÃ công bố 100,00%** và **quý CHƯA công bố 0,00%**.
  Không look-ahead. PE daily tái dựng từ `PE_rel × Price_d/Price_rel`: 99,18% trong sai số 0,5%.
- **Không cột forward-looking** (`profit_*`) ở bất kỳ đâu trong filter.
- **Self-check**: cash-flow identity err **7,3e-6 VND** trên sổ 7,62 tỷ (≈1e-15 tương đối), NAV identity **0,000000 VND**.
  Chạy lại lần 2: `matrix_primary.csv` **byte-identical**, metric lệch ở bit cuối (BLAS thread-order).
- **Verify tay CTG 2026Q2 khớp tuyệt đối**: BQ thô `PE=6,341506 PCF=1,635603 Price=32.800` (release 2026-07-30,
  `Price_rel=30.450`) → engine `PS = 1,4405742 × 32800/30450 = 1,551751` ✓. Percentile tính lại độc lập từ pool:
  sai lệch tối đa **1,11e-16**, **0 rank mismatch** trên 148 mã. CTG rank **27/148**, không lọt Top-5.
- **Không có survivorship do ffill**: 0/245 lượt nắm giữ có chuỗi giá kết thúc trước khi hết kỳ nắm giữ.
- **Chi phí đầy đủ**: TC 0,1%/chiều, phí luỹ kế 345,66tr VND trên turnover 345,66 tỷ (34,57% vốn gốc).
- **N = 48 mùa BCTC độc lập** (2014Q2→2026Q1), không phải 240 = 5×48. N≥30 ✓. Nhưng N các ô điều kiện (9-28) thì nhỏ.

## Sai khác so với đề bài (cố ý, nêu rõ)

**T0 = ngày rebalance cố định của mùa (q_end + 40 ngày lịch), KHÔNG phải Release_Date riêng từng mã.**
Lý do: một sleeve equal-weight Top-5 phải giao dịch tại MỘT thời điểm; xếp hạng cross-sectional đòi hỏi
mọi ứng viên được chấm cùng một ngày. Bù lại đã áp `require_reported=True` — chỉ mã **đã công bố BCTC mùa đó
tính tới D_s** mới đủ điều kiện (đúng tinh thần "sau BCTC"). Mốc +40 ngày phủ p90 Release_Date mọi mùa.
Tín hiệu chốt tại close D_s, **khớp lệnh tại close D_s+1** (không nhìn trước).

## Multiple-testing (§9)

**N_trials = 24, khai báo trước khi đọc kết quả biến thể**: lenses {ey, ey+cfy, ey+cfy+ps} × n_top {3,5,10,15}
× weighting {equal, score}. Pool gating độc lập với lens nên tái dùng `pool_primary.csv` cho cả 24.
PBO = 0,271 (CSCV, S=8, C(8,4)=70 splits) — **đạt**. DSR primary 0,720 / best 0,938 — **không đạt ngưỡng 0,95**.
Chi tiết: `out/multiple_testing.json`, `out/variants.csv`.

## Khuyến nghị

1. **Không tách sleeve mới.** Edge không sống sót 4 năm gần nhất, DD −61% không dùng được, "5" không robust.
2. **Không re-tune sang top10/top15 rồi coi là GO** — Sharpe cao hơn nhưng cùng chịu decay 2022+ và cùng DD ~−56 đến −62%.
   Đổi tham số sau khi thấy kết quả chính là thứ PBO/DSR đang phạt.
3. **Nếu muốn theo đuổi tiếp**: giả thuyết đáng prereg là **"value-vs-ngành trong DT5G BEAR"** (excSEC +5,90% t=2,64
   sau khi loại 2020-21), KHÔNG phải "Top 5 sau BCTC". Phải prereg riêng, neo benchmark ngành, và chờ N tăng —
   hiện n=9, dưới mọi ngưỡng kết luận.
4. Đây là GO/NO-GO cho R&D. **Chưa wire production**; quant-skeptic verify do Mike dispatch riêng (§4 mục 5).

## Pick 2026Q2 (chỉ để tham chiếu, KHÔNG khuyến nghị mua)

Rebalance 2026-08-10, pool 148: **PAN, NBC, HII, DC4, QTP**. Chưa có return đo được (exec 2026-08-11,
dữ liệu giá tới 2026-08-18 < 21 phiên). DT5G tại T0 = NEUTRAL — chính là state mà 2022+ cho excVNI **−7,79%**.
