# QUÉT SẠCH NHÃN as-of `entry` → `known_date` — 8 call-site còn lại (FAIL-C)

**Job** `Taylor_20260927_103332` · **User duyệt** 17:29 ICT 2026-09-27 · **Branch**
`fix/failc-sweep-8callsites-2709` @ `546d5c83` — **CHƯA MERGE**, chờ sign-off.
Worktree `mike/agents/Taylor/wt-failc-sweep-2709/` (repo ngoài `/home/trido/thanhdt`).

## 1. Bản chất lỗi, phát biểu bằng số

`data/lag_edge_health.csv` có CẢ HAI cột: `entry` (ngày vào lệnh) và `known_date`
(= entry + 25 phiên, **median 35 ngày lịch**). Cả 8 file index chuỗi `mean12` trên
`entry` rồi `reindex(common, method="ffill")` ⇒ **backtest đọc mỗi số đo ~25 phiên
TRƯỚC khi nó tồn tại được**. Đường LIVE vốn đã bảo thủ (một dòng chỉ xuất hiện khi sự
kiện đã hoàn tất) nên không đổi.

Mức phơi nhiễm đo trực tiếp trên chuỗi, độc lập với mọi engine:

| Cửa sổ | Số phiên cổng `mean12>=4%` LẬT | % | gate-ON (`entry`) | gate-ON (`known_date`) |
|---|---|---|---|---|
| 2014-01→2026-09 | 295 / 3.322 | **8,9%** | 46% | 47% |
| IS 2014-2019 | 146 / 1.565 | 9,3% | 35% | 37% |
| OOS 2020+ | 149 / 1.757 | 8,5% | 56% | 56% |
| **Cửa sổ paper pt_v22 (2026-06-11→09-24)** | **0 / 76** | **0,0%** | 0% | 0% |

Dòng cuối là lời giải thích CƠ HỌC cho delta 0,00 của `pt_v22_dt5g.py` — không phải may mắn.

## 2. Bảng DELTA — file | số | có chạm số PIN không

Config A/B: `BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg BASKET_WT=namecap
BASKET_SELECT=yieldcombo PARK_STATES="3:0.30" AUDIT_END=2026-06-19 $DNA_PYEXE <file>
v23a none postbull 0 edge`. BEFORE = `git show HEAD:` (nguyên bản), AFTER = bản đã vá.
`self-check 0 VND` (BAL+LAG) ở CẢ HAI chiều, mọi run.

| # | File | CAGR trước→sau | Δ | Sharpe | MaxDD | Calmar | Chạm số PIN? |
|---|---|---|---|---|---|---|---|
| 1 | `pt_v22_dt5g.py` (paper LIVE) | −4,79% → −4,79% | **0,00pp** | idem | −10,63% idem | — | **KHÔNG** — 3/3 CSV output **byte-identical** |
| 2 | `pt_v23_audit_ddpark.py` | 21,92 → 22,21 | **+0,29pp** | 1,73→1,75 | −14,7→−14,7 | 1,49→1,51 | KHÔNG — 0 ref trong `results_registry.md` |
| 2b | ↑ *config mặc định (không `edge`)* | 22,13 → 22,13 | 0,00pp | idem | idem | idem | — *(khối vá không chạy: `USE_EDGE_ALLOC` tắt)* |
| 3 | `pt_v23_lagcap_research.py` | 22,68 → 22,58 | **−0,10pp** | 1,82→1,81 | −14,8→−14,8 | 1,53→1,52 | KHÔNG — 0 ref |
| 4 | `pt_v23_lagqual_research.py` | 22,68 → 22,58 | **−0,10pp** | 1,82→1,81 | −14,8→−14,8 | 1,53→1,52 | KHÔNG — 0 ref |
| 5 | `lag_dnpr_harness.py` | 22,19 → 22,48 | **+0,29pp** | 1,75→1,77 | −13,6→−13,9 | 1,63→1,61 | KHÔNG — 0 ref |
| 6 | `converge_fullharness_test.py` (argv R3) | 22,19 → 22,48 | **+0,29pp** | 1,75→1,77 | −13,6→−13,9 | 1,63→1,61 | — |
| 6b | ↑ **config ĐÃ PIN** `CONVERGE_BOOK=1 CONV_WPN=0.11` | 13,78 → 13,78 | **0,00pp** | 0,94 idem | −36,9 idem | 0,37 idem | **KHÔNG** — pin **12,05%** (2026-07-06) an toàn |
| 7 | `data/research_edge_alloc_walkforward.py` | thr4 IS 20,86→20,80 · OOS 28,08→**28,27** | −0,06 / **+0,19pp** | OOS 1,88→1,89 | −20,3 idem | 1,39 idem | KHÔNG — 0 ref |
| 8 | `data/research_edge_conditional_allocator.py` | A2 (luật LIVE) 24,58→**24,64** · A3 24,82→**24,99** | **+0,06 / +0,17pp** | A2 1,81→1,82 | −20,3 idem | 1,21→1,22 | KHÔNG — 0 ref |

**Không số PIN nào bị chạm.** Số PIN duy nhất do nhóm 8 file này sinh ra là ConvergePort
12,05% (mục 6b) và nó **đứng yên tuyệt đối** — vì ở config đó sổ LAG bị làm trơ (1 VND)
nên tilt của allocator không có hiệu lực kinh tế. *(Run hôm nay in 13,78% thay vì 12,05%
là **data-drift** từ 2026-07-06, xuất hiện Y HỆT ở cả BEFORE lẫn AFTER ⇒ không quy được
cho bản vá. KHÔNG tự re-pin.)*

## 3. File 7 & 8 — nghiên cứu ĐẺ RA allocator edge-conditional đang LIVE

**Kết luận gốc SỐNG SÓT, và mạnh lên một chút.** Không có finding lớn.

- **File 7 (walk-forward IS→OOS).** Trước vá, đỉnh Calmar IS nằm ở thr 5/6 (2,17) trong
  khi thr **4** được deploy (2,11) — tức lựa chọn deploy hơi lệch khỏi đỉnh IS. Sau vá,
  IS Calmar thành **cao nguyên 2,11 tại thr 4/5/6**, và thr4 trở thành lựa chọn IS-tối ưu
  đồng hạng. OOS Calmar thr4 giữ 1,39 > state-tilt 1,36. Tức bản vá **củng cố** con số 4%,
  không làm lung lay nó.
- **File 8 (A0–A4).** A0 static 50/50 và A1 state-tilt **không đọc chuỗi edge** ⇒ đứng
  yên tuyệt đối (24,17 / 24,04) — đây là **chân đối chứng**, chứng minh mọi thay đổi chỉ
  đến từ đường edge chứ không phải nhiễu run-to-run. A2 = đúng luật đang LIVE
  (thr4, weak→0,50): 24,58→**24,64**, Sharpe 1,81→1,82, Calmar 1,21→1,22 — vẫn thắng cả
  A0 lẫn A1. A4 (thr2) TỆ đi 24,16→23,94, tức khoảng cách nghiêng về thr4 còn **rộng ra**.

Đọc chung với mục 2: **nhãn look-ahead không hề "làm đẹp" kết quả** — gỡ nó ra thì CAGR
phần lớn NHÍCH LÊN (+0,29pp / +0,19pp / +0,06pp), chỉ 2 harness LAG-cap nhích xuống
−0,10pp. Đúng dấu với lần re-pin R3 sạch nhãn sáng nay. Biên độ đều **dưới 0,3pp**, nằm
trong nhiễu data-drift — nên đây là việc **đúng đắn về nguyên tắc causal**, không phải
một cú đổi kết luận.

## 4. Consumer của `pt_v22_dt5g.py` (engine paper đang chạy)

- Chạy hằng ngày: `papertrade_daily.sh` bước **[12]** → ghi `data/pt_v22_dt5g_logs.csv`
  (+ `_transactions` / `_open_positions` / `_report.md`).
- `papertrade_compare.py` đọc `pt_v22_dt5g_logs.csv` thành dòng **`V23`** trong
  `data/papertrade_compare5.csv`.
- Chương trình paper trong `mike/kb/paper_programs_registry.json` đọc output đó:
  **`engine_room_oos`** — "Engine-room OOS panel (V11/V12/V4 vs V2.3-book vs VNINDEX)",
  `data_sources` liệt kê thẳng `data/pt_v22_dt5g_*.csv`, headline so `V23` với `VNI_BH`,
  mốc nghiệm thu **2026-12-01**. **Đây là chương trình DUY NHẤT** trong registry đọc
  output của file này.
- **Tác động lên `engine_room_oos`: bằng 0.** A/B trên đúng cửa sổ paper cho 3/3 CSV
  byte-identical (mục 2 dòng 1), lý do cơ học ở mục 1 (0/76 phiên cổng lật).
  ⇒ Merge bản vá **không** làm gãy chuỗi NAV paper, **không** cần backfill, **không**
  cần re-baseline panel.

## 5. Selfcheck — `failc_sweep8_selfcheck.py` (MỚI, commit cùng branch)

Không phải grep: nó **nâng đúng khối đã vá ra khỏi source thật** rồi `exec` trên một
`lag_edge_health.csv` tổng hợp mà `entry` (2020-02-03) và `known_date` (2020-04-01) bắc
qua ngày dò 2020-03-10. Assertion là **một con số**: giá trị tại ngày dò phải là 1.0
(số quan sát được), **không phải** 99.0 (số của tương lai).

| | Kết quả |
|---|---|
| Assertion | **40 PASS / 0 FAIL** (5 assertion × 8 file) |
| Múi giờ | **4/4 PASS** — `Asia/Ho_Chi_Minh`, `UTC`, `America/Los_Angeles`, **TZ unset** |
| Mutation | **16/16 BỊ GIẾT, 0 sống sót** |

Hai mutation mỗi file: (M1) revert `_eh_key` về `"entry"` → A1/A2 chết; (M2) xoá khối
cảnh báo thiếu cột → A4 chết. Chạy: `python3 failc_sweep8_selfcheck.py --all-tz --mutations`.

## 6. §8 — không có file pin nào bị ghi đè

Mọi output A/B đi ra `data/_exp_failc8_20260927/{BEFORE,AFTER}/` (sandbox copy ở
`research/failc_sweep8_20260927/sandbox/`, chỉ khác bản commit ở **đường dẫn ghi**).
Kiểm chứng sau khi chạy: `data/lag_edge_health.csv` mtime **16:39:56** (trước phiên này),
`data/pt_v22_dt5g_logs.csv` mtime **2026-09-25 15:37**, `data/v23c_golive_audit_*.csv`
mtime **2026-06-13** — cả ba **không đổi**. Bản vá thêm biến `EDGE_HEALTH_CSV` (rỗng =
file production) để A/B tương lai chạy được trên input non-canonical.

## 7. Tồn dư — 11 call-site CÙNG LỚP LỖI, NGOÀI phạm vi 8 file được giao

`grep -rn 'drop_duplicates("entry")'` còn **11** vị trí, tất cả đều là **bản chụp thí
nghiệm đã đóng băng** (`data/*_exp/`, `data/*_logs/`, tên có ngày `_20260711`/`_20260712`):
`data/fscore_review_20260801/engine_V{1,3}*.py` · `data/fscore_c30v_20260801/engine_fsx.py` ·
`data/fa8l_exp/pt_v23_{fatier8l_probe,fa8l_phase2,fa8l_diag}_20260711.py` ·
`data/f3_exp/pt_v23_basetable_probe_20260711.py` · `data/momdeal_exp/pt_v23_scopeC_tmp_20260712.py` ·
`data/v25chk_logs/pt_v25_loo_tmp_20260712.py` · `data/qsleeve_logs/pt_v23_qsleeve_tmp_20260712.py` ·
**`agents/Taylor/research/backtest_2008_v24_20260825/engine_2008.py`**.

**Không vá** (ngoài scope + vá snapshot đã đóng băng sẽ làm nó hết tái lập được kết quả
cũ). Đáng chú ý duy nhất: `engine_2008.py` — nếu backtest 2008 từng sinh số được trích
dẫn ở đâu đó thì số đó mang cùng nhãn look-ahead ~25 phiên. **Đề xuất**: một job riêng
chỉ để rà `engine_2008.py`, không gộp vào đây.

## 8. Đề xuất

1. **Merge** `fix/failc-sweep-8callsites-2709` (`546d5c83`). Rủi ro sản xuất ≈ 0: consumer
   duy nhất đang chạy là `engine_room_oos`, delta đo được = 0,00.
2. **Không re-pin gì cả** — không số PIN nào đổi.
3. Mở job rà `engine_2008.py` (mục 7).
