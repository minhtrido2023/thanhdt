# LAG cache về cơ sở giá ĐIỀU CHỈNH (Phương án A) — 2026-11-10

> ⚠️ **ĐÍNH CHÍNH 13/11/2026 01:3x ICT (arch-reviewer, Mike tự kiểm lại):** dòng "CHƯA apply, CHƯA merge" bên dưới ĐÃ LỖI THỜI. Nhánh đã squash lên `main` ở commit `97b2a7197` (reflog 10/11 15:30:03 +0000; message ghi "user duyệt 2026-11-10 22:10" — Mike chưa tìm thấy bản ghi duyệt khác ngoài message này) và `papertrade_daily.sh:43` chạy `refresh_lagged_caches.py` từ checkout main lúc 15:30 ICT T2-T6 ⇒ merge vào main = apply ở lần cron kế tiếp. Cache thật đã ở cơ sở điều chỉnh (`.pre_adj` sinh 11-10 08:30 UTC, còn nguyên); golive 11-11/11-12 đã dùng. Blast radius '4 rời/7 vào' bị phóng đại: 7/11 mã đã nằm trong `lag_liq_excluded`; delta live ≤ HTT, PHP rời / KLB, PHR vào. arch-review luồng C = NEEDS_CHANGES (code ổn, 65/65 + 27/27 + 13/13 + 4/4 tự chạy lại; thiếu validate Price/Volume_3M_P50, chưa có runbook rollback). Chờ user: PHÊ CHUẨN trạng thái live hay ROLLBACK.


> **VÒNG 2** (job `Taylor_20261110_132044`, sau quant-skeptic REFUTED + arch-reviewer NEEDS_CHANGES) — §4 viết lại.
> Job vòng 1 `Taylor_20261110_123246` · user chốt "làm A" 10/11. **ĐỀ XUẤT trên nhánh, CHƯA apply, CHƯA merge.**
> Nhánh `feat/lag-cache-adjusted-20261110` ở cả 2 repo: code `wt-lagadj-1110` (repo ngoài),
> research + doc `mike/agents/Taylor/wt-mike-lagadj-1110`. Artifact: `agents/Taylor/research/lag_cache_adjusted_20261110/`
> (md5 mọi file: `MD5SUMS`). Chờ: quant-skeptic → arch-reviewer → **user duyệt** (xem §6).

## 1. Lý do
- `refresh_lagged_caches.py` chỉ APPEND ⇒ (a) phiên fetch lúc BQ chưa đủ thì thưa vĩnh viễn (13 phiên 06-26..09-14,
  min 1 mã/phiên), (b) từ 19/06 dòng mới vào ở cơ sở "điều chỉnh tới ngày fetch" trong khi dòng cũ ở cơ sở khác
  ⇒ cú rơi GIẢ ngày GDKHQ (PHR 09-11 −45,7%, VHM 08-06 −49,6%, TRC 09-15 −73,7%) ⇒ `post_ret` LAG sai.
- `tav2_bq.ticker.Close/Open` điều chỉnh HỒI TỐ ⇒ cách duy nhất để cả chuỗi cùng cơ sở là **kéo lại toàn bộ** mỗi ngày.

## 2. Thiết kế (code: `lagged_cache_adjusted.py` + `refresh_lagged_caches.py`, selfcheck `lagged_cache_adjusted_selfcheck.py`)
- **Cửa sổ = TOÀN lịch sử cache (2011-01-04 → END), dựng lại mỗi ngày** — không có cửa sổ ngắn nào đủ: đoạn ≤06-18
  cũng lệch cơ sở với BQ hiện tại ở 576 mã (1.365.607 dòng |Δ|>0,1%, 2011→2026, `recon.txt`), hệ số lệch KHÔNG hằng
  ở 526 mã ⇒ không vá được bằng 1 hệ số/mã. ⇒ **đây là REBUILD TOÀN BỘ lịch sử cache** (cần user biết, §6).
- **Đọc BQ SỐNG, KHÔNG đọc BQ_LOCAL_CACHE** (lệch với dispatch): cache parquet chỉ tải lại năm cũ khi lệch SỐ DÒNG,
  hồi tố giá không đổi số dòng ⇒ đo 1.196 cặp (mã, năm) 2013–2025 có SUM(Close) cache ≠ BQ sống
  (`data/cache_vs_bq_close_mismatch.csv`); cache không có 2011–12. Chi phí: ~151,8MB quét / ~173MB tính phí mỗi lần (16 truy vấn theo năm, đo vòng 2; bản vòng 1 ghi 111,6MB là thiếu cột Price/Open).
- Không phụ thuộc `corporate_action`. Volume_3M_P50 kéo cùng lần (lagged_pos_ov).
- Fail-safe: flock (exit 3 nếu bận) · ghi nguyên tử mkstemp+fsync+os.replace+fsync thư mục, `.prev` lăn 1 bản,
  `.pre_adj` chụp 1 lần bản cơ sở-thô cuối · validate trước khi ghi: số mã/phiên <50% trung vị 60 phiên (từ 2014),
  mất >0,2% cặp (mã,phiên) cũ, phiên mất >5% mã, >20 mã bị BQ cắt lịch sử ⇒ **KHÔNG ghi, exit 1 cuối script**
  (bước 3/4 vẫn chạy). Mã bị BQ cắt lịch sử (đổi sàn/huỷ niêm yết): mang sang NGUYÊN TRẠNG dòng cũ — 5 mã
  (PMT, SSC, TLD, VFC, VTH; 16.597 dòng, `carried_tickers.csv`) ⇒ các mã này vẫn cơ sở cũ.
- Selfcheck: **65/65 PASS** + mutation **27/27 bị bắt** (vòng 2; vòng 1 45/45 + 17/17) dưới `env -u TZ`, `TZ=America/New_York`, `TZ=Pacific/Kiritimati` (đo 2026-11-10 trong
  phiên này); fixture thật PHR/VHM/DRI/TRC; `--mutate` có sẵn (mutation trên cả 2 file).

- **Vòng 2 vá thiết kế:** trần "≤20 mã bị cắt" chỉ đếm mã MỚI (state `data/lagged_carried.json`, ghi nguyên tử; trước đó đếm dồn
  ⇒ chặn vĩnh viễn) · 16 khúc năm + truy vấn END đọc CÙNG snapshot `FOR SYSTEM_TIME AS OF` một mốc UTC · `.pre_adj` chép qua tmp+`os.replace` ·
  kéo thêm cột `Price` (giá THÔ) vào `lagged_pos_ov` · `make_sandbox.sh` DỪNG nếu engine ≠ 33f005209.

## 3. Trước / sau — cache (`build_manifest.json`, `recon.txt`)
| | canonical (main) | adjusted (đề xuất) |
|---|---|---|
| earnings_px md5 | af4b8c1b72f4… | 184900987c28… |
| lagged_pos_ov md5 | afb2484e5fb7… | 87b49b483d80… |
| dòng | 3.769.344 | 3.791.117 (+21.773, mất 0) |
| min mã/phiên từ 2026-06-01 | 1 (13 phiên <665) | 766 (0/113 phiên <665) |
| top \|ret\| 1 phiên từ 06-01 | DNN +1324%, TRC −73,7%, VHM −49,6%, TRA −52,5% | DNN +98,6% (gap 6 tuần), còn lại là mã thanh khoản mỏng nhảy nhiều tuần; PHR/VHM/TRC/TRA hết |

## 4. Hệ quả (mỗi dòng đổi ĐÚNG 1 trục `LAG_CACHE_BASIS canonical→adjusted`)

### 4.1 R3 — KẾT LUẬN VÒNG 2: **KHÔNG re-pin, GIỮ pin hiện hành 22,12 (sàn) / 25,42 (trần)**. "Vintage pkl đổi, số pin không đổi."
Vòng 1 báo ΔCAGR +0,92/+0,78pp "vượt sàn nhiễu" — **bị quant-skeptic bác (REFUTED) và vòng 2 xác nhận là artifact fill ADV=0**:
- Pin R3 chạy `LIQ_ZERO_BLOCK=""` ⇒ `simulate_holistic_nav.py:1436-1444` mua đủ size trong 1 phiên ở mã ADV=0; **live `cap_lag_orders` chặn**.
  Toàn bộ Δ vòng 1 đến từ fill ở mã không fill được: **NAP 2023** (mua 25,8B, PnL +36,2B; BQ cả năm GTGD 0,74B, Volume_3M_P50=0) một mình > Δ2023;
  cũng BDW, HBH. Mã liq≤0 mang +49,7B/+56,9B trên Δ +38,5B/+34,3B ⇒ fillable net −11,2B/−22,7B; leave-2023-out +0,31/+0,26pp < sàn nhiễu 0,46pp (số của skeptic).
- Cơ chế "rơi giả từ 06-19" **không chạm R3** (`AUDIT_END=2026-06-19`). Δ vòng 1 đến từ **re-vintage lịch sử ≤06-18** (576 mã: cache cũ chứa rác, vd CCR đông cứng 4570, HHV 8190) **+ khe fill liq≤0** — không phải "dữ liệu sạch hơn ⇒ alpha".
- **Đo lại 4 chân với `LIQ_ZERO_BLOCK=lag`** (mirror live; đúng lệnh pin, `$DNA_PYEXE`, threads=1, tag `r3z_*`; self-check 0 VND cả 4; `r3z_results.json`):

| | ctrl (canonical) | adj | Δ adj−ctrl | CI p5..p95 (bootstrap ghép cặp, L=21 B=4000 seed 12345) |
|---|---|---|---|---|
| pin0% CAGR / Sharpe / DD / Calmar | 23,275 / 1,74 / −16,27 / 1,431 | 23,232 / 1,738 / −17,07 / 1,361 | **−0,043pp** / −0,002 / −0,80pp / −0,070 | [−0,50; +0,42], P(Δ>0)=0,43 |
| pin1M | 26,530 / 1,945 / −15,94 / 1,664 | 26,161 / 1,926 / −15,94 / 1,641 | **−0,369pp** / −0,019 / 0 / −0,023 | [−0,80; +0,05], P(Δ>0)=0,07 |

  Leave-one-year-out (`cagr_z.py`): pin0% bỏ 2023 −0,06 · bỏ 2025 +0,05 · bỏ 2019 −0,03 · bỏ 2023+2025 +0,05pp; pin1M bỏ 2023 −0,40 · 2025 −0,19 · 2019 −0,42 · 2023+2025 −0,21pp.
  Năm lệch lớn: 2020 −2,72/−2,48pp, 2025 −1,16/−2,50pp (cả hai chân âm). DSR(N=1) 0,44/0,07, PBO không áp dụng. |Δ| < sàn nhiễu 0,46pp ở cả hai chân ⇒ **không có bằng chứng R3 đổi**; **không đủ điều kiện đề xuất re-pin** (cần Δ fillable > 0,46pp VÀ qua leave-2023-out — trượt cả hai).
- **[ĐÍNH CHÍNH vòng 3]** Chân adj vòng 2 chạy trên cache vintage v1; lập luận cũ "R3 không đọc Price nên không cần dựng lại" là SAI: R3 đọc `earnings_events_classified.post_ret` và `lag_edge_health.mean12` dẫn xuất từ Close; events v1≠v2 lệch 182–186 `post_ret` (≤~1pp, chủ yếu TNG/PTC), mean12 lệch ≤0,004pp. Vòng 3 đã dựng lại sandbox `derived_v2/*_adjv2.csv` và chạy 2 chân adj v2 (`LIQ_ZERO_BLOCK=lag`): **23,232 / 26,161 — byte-identical chân adj v1** (md5 `1f8b373c…`/`2c3d87de…`) ⇒ kết luận "không re-pin vì trục cache" giữ nguyên trên đúng vintage sẽ deploy.
- ⚠️ Phát hiện phụ (KHÔNG thuộc nhánh này, cần user quyết riêng): control `LIQ_ZERO_BLOCK=lag` cho **23,28 / 26,53** vs pin hiện hành 22,12 / 25,42 (+1,16 / +1,11pp) — pin hiện hành chạy cấu hình KHÔNG khớp live (mua được mã ADV=0). Re-pin cấu hình mirror-live là quyết định riêng.
- ⇒ `PINS.jsonl`, 2 ledger f1bdcd02/54e98209 và mục `results_registry.md` của vòng 1 **đã gỡ khỏi commit code**; 4 ledger `r3z_*` (md5 trong `r3z_results.json`) chỉ là bằng chứng nghiên cứu, không pin.

### 4.2 Edge health / w_LAG
| Đại lượng | canonical | adjusted | nguồn |
|---|---|---|---|
| lag_edge_health mean12 (asof known 2026-09-23) | −0,62 NEGATIVE | +0,02 TROUGH (vòng 2 pkl: +0,02, `edge_results_v2.json`) | `edge_results.json` (ctrl tái hiện byte-identical canonical) |
| neg_streak | 1 | 0 | idem |
| **w_LAG live (2026-11-09)** | **0,50** (target 0,50; hiện 0,4761) | **0,50 — không đổi** | `derived/w_lag_history.csv`, `data/golive_v23_status.json` |

- **Sửa sai vòng 1:** w_LAG live là **0,50/0,50**, KHÔNG phải 0,65. Lý do: `golive_recommend_v23.py:127` `EDGE_THR = 4,0` (%): w_LAG chỉ lên 0,65 khi mean12 ≥ 4,0% — cả −0,62 lẫn +0,02 đều < 4,0 nên **TROUGH không đổi w_LAG**; cảnh báo "hạ w_LAG .65→.50" của NEGATIVE là vô nghĩa vì đã ở 0,50.
- w_LAG lịch sử khác ở 108/3.205 ngày (2025-06-13..08-27, 2025-12-15..2026-02-13, 02-23..03-09; đều 0,50→0,65 ở bản adj) — chỉ ảnh hưởng backtest lịch sử, không ảnh hưởng live hôm nay.

### 4.3 Tác động lên lệnh LAG thật — `live_lag_candidates` (pa_HL3 → qualify; vòng 2 đo trên pkl vòng 2, `live_cand_impact.json`)
- Cửa sổ 120 ngày tới 2026-11-10 (2.080 sự kiện): qualify **206 → 209**; chỉ có ở bản cũ: **HTT, PHP, PMP, TMG**; chỉ có ở bản adj: **BSP, DMN, KLB, LAW, NBC, PHR, TPC**; tier đổi ở mã qualify cả hai: 0; **229 sự kiện đổi pa_HL3 > 0,5pp**.
  Toàn lịch sử 59.255 sự kiện: qualify 5.606 → 5.629, 2.252 sự kiện đổi pa_HL3 > 0,5pp.
- w_cur (pt_v22 logs): 0,476 → 0,484. Danh sách mã đổi ⇒ **đổi lệnh LAG thật qua plan** ⇒ nằm trong danh sách USER QUYẾT (§6).
- Papertrade `pt_v22_dt5g` từ 07-01 (đã sửa ADV = Volume_3M_P50 × **Price thô** `COALESCE(Price, Close)`, `pt_v22_dt5g.py` trong nhánh; `pt_results_v2.json`): ctrl −7,15% / DD −12,17% (final 46,4259B; chạy 2 lần tất định, tx md5 trùng) → adj **−5,50% / DD −10,74%** (47,2513B). BAL tx y hệt; LAG tx 140→147 (12 chỉ ở ctrl, 18 chỉ ở adj). Vòng 1 ghi −5,59% khi ADV còn trộn cơ sở (Close điều chỉnh) — số cũ bỏ.
  Papertrade ctrl vs log canonical cũ: 46,4259 vs 46,4262, LAG events 97+36 vs 96+42 (không byte-identical; nguyên nhân chưa truy). Chỉ đọc theo hướng.
- Bootstrap DD p5 (R3, sàn/trần): ctrl −28,03/−26,03 · adj −27,99/−25,80 (chân `LIQ_ZERO_BLOCK=lag`); **neo sizing DD GIỮ −25,2% (đầu sàn)**.

## 5. Chi phí / thời gian / lịch
- **BQ:** ~151,8MB quét / ~173MB tính phí mỗi lần (16 truy vấn năm + 1 MAX(time), cùng snapshot). 
- **Thời gian bước [1+2] đầu-cuối ĐO 2026-11-10: 310,4s (≈5,2'; đọc pkl 0,8s + 16 BQ + validate 309,6s)**, validate sạch, END 2026-11-10.
- **Lịch:** `refresh_lagged_caches.py` là step [0] của `papertrade_daily.sh` 15:30 (runtime đo thật trước đây 8–12', worst DONE 15:42). Cộng ~5,2' ⇒ worst DONE ≈15:47. `orb_drift_monitor` 15:50 chỉ còn đệm ~3' (trước 8'), và `orb_pt` (step [17], ~15:37) trượt ~15:42; `paper_programs_daily_report` 07:30 hôm sau không ảnh hưởng. 
  **Đề xuất (không cài cron):** dời `orb_drift_monitor` 15:50→15:55 hoặc chấp nhận đệm 3' (check T0 tự WARN nếu `orb_pt` chưa ghi). Ghi vào `kb/cron_registry.md` dòng 15:30 (đã thêm ghi chú, nhánh).
- BQ lỗi ⇒ fail-closed giữ pkl cũ (exit 1) — cần owner cron nhìn exit code.
- Cơ sở điều chỉnh đổi hồi tố mỗi lần có sự kiện quyền ⇒ số tính từ pkl trôi nhẹ theo vintage; pin phải ghi md5 pkl. Tái lập: pull thô lưu bất biến `data/snapshots/lag_adjusted_pull_20261110_30d78da7.parquet` (vòng 1) và `..._v2_..._258d793b.parquet` (vòng 2).
- 5 mã bị BQ cắt lịch sử (PMT, SSC, TLD, VFC, VTH) giữ cơ sở cũ.

## 6. Cần user quyết
1. **Rebuild toàn bộ lịch sử cache mỗi ngày từ BQ sống** (không cửa sổ ngắn, không qua BQ_LOCAL_CACHE), ~5,2' + ~173MB/ngày.
2. **R3: KHÔNG re-pin** (kết luận §4.1) — chỉ cần xác nhận. Riêng: có muốn re-pin cấu hình mirror-live `LIQ_ZERO_BLOCK=lag` (23,28/26,53) hay không (ngoài nhánh này).
3. **Đổi lệnh LAG thật:** 4 mã rời (HTT, PHP, PMP, TMG), 7 mã vào (BSP, DMN, KLB, LAW, NBC, PHR, TPC), 229 sự kiện đổi pa_HL3 >0,5pp (§4.3).
4. Edge health NEGATIVE→TROUGH: **không đổi w_LAG live (0,50 cả hai)** — chỉ đổi nhãn/cảnh báo.
5. Dời/chấp nhận đệm 3' với `orb_drift_monitor` 15:50 (§5).

## 7. Việc sau khi duyệt
1. Merge nhánh code (repo ngoài) + mike; chạy `refresh_lagged_caches.py` 1 lần tay (tạo `.pre_adj`, `lagged_carried.json`), đối md5 với artifact research (cùng END) hoặc ghi md5 mới.
2. Cron refresh giữ nguyên lịch (§5); thêm theo dõi exit≠0.
3. Chạy lại `lag_edge_health` + papertrade LAG trên pkl mới; cập nhật `kb/projects/lag-edge-health-staleness.md`.

## 8. Vòng 3 (job Taylor_20261110_151145) — blast-radius ADV + re-pin mirror-live
- **Blast-radius ADV (arch mục 2+3):** sau apply `lagged_pos_ov` mang giá ĐIỀU CHỈNH; `pt_v4_dt5g.py` (papertrade_daily bước [11]) và `pt_v12_macro.py` (bước [8]) nhân `Volume_3M_P50` thô với `px_open` điều chỉnh ⇒ ADV lệch theo hệ số điều chỉnh (mã chia tách/cổ tức cổ phiếu). Đã vá: helper dùng chung `lag_adv_basis` (COALESCE(Price thô, Close/Open thô); thiếu cột Price ⇒ hành vi cũ), `pt_v22/pt_v4/pt_v12` đều dùng. Selfcheck 13 ca (3 ca × 3 engine + biên) + mutation 4/4; A/B ctrl vs sau-vá trên pkl canonical = byte-identical logs. Commit code `cf21463b9`.
- **Mã huỷ niêm yết mang sang không TTL:** carry chỉ đếm mã MỚI + state; mã đã huỷ niêm yết còn trong pkl được mang sang mãi (không hết hạn) — vô hại cho ADV/giá vì không còn dòng mới, nhưng nằm trong `lagged_pos_ov` và có thể hiện ở danh sách vị thế LAG; cần TTL hoặc loại theo `delist` nếu muốn sạch (đề xuất, chưa làm — chờ user).
- **Re-pin mirror-live (user mở):** nhánh `feat/repin-mirror-live-20261110` (commit `307593815`, tách khỏi code). Chuỗi 1 trục: pin cũ 22,121/25,420 → +`LIQ_ZERO_BLOCK=lag` 23,275/26,530 → +cache adj v2 **23,232/26,161**. Dải mới sàn 23,23 … trần 26,16. N_trials=3, DSR<0,95 (không claim edge). **Neo DD đo được −27,99% (sàn) ≠ neo cũ −25,2%** — đề xuất −28,0%, cần user quyết. Chưa wire; chờ quant-skeptic.

