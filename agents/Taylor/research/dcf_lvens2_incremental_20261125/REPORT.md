# lv_ENS2 incremental hằng tháng — cho sổ paper `behav_cell_ledger` (job Taylor_20261125_115701)

Nhánh `session/Taylor_20261125_lvens2inc`, worktree `wt-dcf-lvens2-inc-20261125`, tách từ mike master `4d1c19942`.
CHƯA merge, CHƯA cài cron, KHÔNG sửa `dcf_valuation.py`, `mike/kb/paper_programs_registry.json` hay bất kỳ file production nào. Chỉ dùng cho nghiên cứu, DISPLAY-ONLY.

## 0. Kết luận
1. **Code chép đúng.** Ở mode `v31` (không cắt dữ liệu), `lvens2_incremental.py` cho lại `vp2.parquet` của V3.1 **khớp tuyệt đối** trên 9/9 tháng
   (6 tháng gần nhất 2026-05→10 và 3 tháng ngẫu nhiên seed 20261125: 2016-02, 2021-04, 2021-10). Số mã khớp, max|Δ| = **0** trên cả lv_ENS2 lẫn 5 thành phần,
   route/in_universe lệch 0 (`out/cmp_v31.json`).
2. **Bản PIT KHÔNG khớp vp2 tới 1e-9, và nó không được phép khớp, vì vp2 tự nó không PIT.** Đo được hai nguồn look-ahead trong V3.1 (chi tiết ở §3):
   (a) `mc` dùng `N_next`, tức số cổ phiếu lấy từ kỳ BCTC **công bố SAU** as-of. Bị ảnh hưởng 6–53 mã in-universe mỗi tháng, |Δ| tới 1,39 (log; ví dụ VHM 2026-10 là log 2).
   (b) `route` lấy theo nhãn cuối cùng của toàn bảng `fa_ratings_8l` (đúng bẫy TRAP trong data_registry). Có 1–3 mã đổi route sau as-of (HDG, OGC, HKT), và nhãn của chúng
   đổi beta HEDf cùng trung vị MULT nên kéo trôi lv của cả universe: p95 0,005–0,017, max 0,18.
   Giữ route theo vp2 (chẩn đoán `--route-global`) thì phần trôi còn lại ≤ 1e-3 (max 9,6e-4), chỉ đến từ các dòng ngoài universe bị cắt đuôi.
3. **Kiểm PIT: PASS.** Phá toàn bộ dữ liệu sau ngày D (giá ×1,7, BCTC ×0,3, thêm dòng universe giả, route ngẫu nhiên, giá VND ×1,7), dựng lại thì đầu ra **cùng md5**
   (2026-10 step: `771d0c42…`; 2021-04 strict: `550613c5…`). Ba TZ (env -u TZ, America/New_York, Asia/Ho_Chi_Minh) cũng cùng md5 `771d0c42…`.
4. **Đã nối `paper_cell_monthly.py --lvens2-from`.** Dùng file `v31` thì ra 333/333 dòng khớp `out/paper_cell_TEST_2026-10.csv` tuyệt đối (lv, hi52, hạng, ô, route).
   Dùng file PIT thì vẫn 333 mã nhưng đổi ô: **2 mã** với `strict` (PHR, VCG), **6 mã** với `step` (GIL, LPB, NTC, TCB, TVN, VVS) — liệt kê ở §4. Fail-closed vẫn giữ.
5. **Chi phí mỗi tháng:** 1 lần dựng ≈ 41 s wall (đo 20,8–98,6 s tuỳ tải máy và độ dài lịch sử), RSS ≈ 2,0–2,1 GB; paper_cell thêm 2,3 s / 0,23 GB.
   Không cần BQ live (đọc cache) và không gọi engine production.
6. **Không tái lập được từ repo:** snapshot VNDirect (`delisted/`, 1.341 file, 62 MB, gồm giá + BCTC các mã vắng BQ) và `px_pre2013_d.csv` (22 MB). Cả hai nằm ở worktree
   V3.1 chưa merge. Script kiểm md5 và fail-closed nếu lệch. Bỏ VND đi thì lv_ENS2 2026-10 đổi ở 204/341 mã >1e-3 và 23 mã >0,05 ⇒ **không bỏ được**, phải chuyển
   snapshot này về chỗ ổn định trước khi merge (§5).

## 1. Đo trước — chuỗi tính lv_ENS2 trong V3.1 (chỉ đọc `wt-dcf-v3-20261125`, commit `1a279d12f`)
- **Công thức:** `lv_ENS2 = nanmedian(lv_D0B, lv_DDM, lv_EPV, lv_MULT, lv_HEDf)`, với lv = log(V_tổng / mc). Nguồn là `c_models2.py` (md5 `be7b28dd…`).
  ENS2 **không dùng** `engine_A2.parquet` (A_pit/A_RI, tức engine production `dcf_valuation`), nên bản incremental không đụng `dcf_valuation.py`.
- **Panel:** `b_panel.py` (md5 `0995ecde…`), gồm 3 phần:
  - Giá: `data/bq_cache/ticker/*.parquet` (CANONICAL, 1,4 GB, 14 file năm) cộng `px_pre2013_d.csv` (đóng băng; giá BQ 2006→2013-01 do V3.1 query một lần) cộng giá VND.
  - BCTC: `data/bq_cache/ticker_financial.parquet` (CANONICAL), dùng `totalAsset−nợ`, NP/Revenue P0–P7, CF, DY, BVPS, **OShares** (cột này là TRAP: restate, xem
    `kb/data_registry/fundamentals/ticker_financial_oshares.md`) cộng BCTC VND (`fs_*.csv`, ngày công bố giả định = cuối quý + 45/90 ngày).
  - Universe `data/bq_cache/universe_pit` (CANONICAL; không dùng ticker_prune). Route lấy từ `data/bq_cache/fa_ratings_8l.parquet` (TRAP: route không PIT trước 2026).
- **Bước tốn kém:** đọc 1,4 GB giá (duckdb) cộng hai vòng Python theo mã (`pick_n`, `roll_stats` trên ~64 nghìn kỳ BCTC) cộng `gate()` trên giá VND.
  V3.1 đo `b_panel.py` 42,6 s (`out_F/log_b.txt`), `c_models2.py` 50,9 s (`log_c.txt`, gồm cả 18 biến thể và nhãn tương lai).
  Bản incremental chỉ giữ những gì ENS2 cần: 44,7 s / 2,09 GB cho mode v31 (toàn lịch sử, xuất 9 tháng), 41 s / 2,0 GB cho mỗi as-of PIT 2026.
- **Vì sao chưa thể "chỉ tính tháng mới":** MULT cần trung vị bội số theo route của 60 tháng trước (chỉ mã in-universe), còn HEDf cần beta OLS gộp cố định 2015-01..2019-12.
  Cả hai đòi panel lịch sử. Dựng lại toàn bộ panel, cắt ở D, rẻ (≈ 40 s) nên tôi KHÔNG cache trạng thái giữa các tháng: đơn giản hơn, và không có trạng thái để trôi.

## 2. Script — `calc/lvens2_incremental.py`
- Chép từ b_panel mục 1–3 và c_models2 (chỉ D0B, DDM, EPV, MULT, HEDf, ENS2). Provenance ghi ở docstring, gồm đường dẫn và md5 nguồn; không import chéo.
  Cờ env của V3.1 được cố định ở mặc định (KD 45/90, PITMED=1, không PICK_OS/MC_OLD/VND_N_OLD), vì §8: trục làm đổi số thì phải đổi tên file.
- **Cắt PIT** (mode `pit`, mặc định): giá BQ/VND, `ticker_financial.time`, VND `known`, universe_pit và fa_ratings_8l đều chỉ giữ ≤ D, với D = phiên cuối tháng trong cache `ticker`.
  BCTC VND được cắt **trước** khi tính `N_nxt`; ở V3.1, `N_nxt` tính trên mọi kỳ.
- **Tuỳ chọn mc** `--mc-pit strict|step` (mặc định `strict`):
  `strict` giữ đúng code V3.1, nên khi kỳ BCTC kế chưa công bố ở D thì dùng N cũ và bỏ sót đợt thưởng/chia tách.
  `step` là **biến thể mới, KHÔNG có trong V3.1**: nếu có sự kiện từ ngày công bố mà chưa có kỳ kế thì dùng `mc_old = Price×N×hệ số giá`. Cách này bắt được thưởng/chia tách,
  đổi lại sai đúng bằng tỉ suất cổ tức tiền nếu sự kiện chỉ là cổ tức.
- Fail-closed (rc=3): md5 snapshot đóng băng lệch; tháng chưa kết thúc; universe_pit chưa phủ D; không có phiên nào trong tháng.
  WARN nếu snapshot VND dừng trước D (snapshot hiện dừng ở `vnd_px_max_date` 2026-11-23).
- Ra: `out/lvens2_<ym>[_mcstep].parquet` (ticker, ym, time, known, src, route, in_universe, E, mc, n_next_used, event_no_next, 5 thành phần, lv_ENS2, n_ENS2, asof_date, mode)
  cộng `.json` (D, số dòng, md5 BCTC/rating, md5 script, beta HEDf).
- Chẩn đoán, **không dùng cho sổ**: `--mode v31`, `--route-global`, `--no-vnd`.

## 3. Self-check (số đo; lệnh tái lập ở §6)
| kiểm | kết quả | file |
|---|---|---|
| v31 vs vp2, 9 tháng | 9/9: số mã khớp, max\|Δ\|=0 ở mọi cột lv, route/iu lệch 0 | `out/cmp_v31.json` |
| PIT strict vs vp2, 9 tháng | không khớp; mã in-universe có \|Δ\|>0,05: 11 / 11 / 25 / 23 / 47 / 9 / 20 / 34 / 25 (2016-02, 2021-04, 2021-10, 2026-05…10) | `out/cmp_pit.json`, `out/attrib_pit.json` |
| phân rã (giữ route như vp2) | 2026-10: 27 mã khác mc/BCTC (max 0,693); phần còn lại 317 mã max 9,6e-4. 2021-04: 8 mã (max 0,699); còn lại max 8,6e-5 | `out/diag/attrib_routeglobal.json` |
| strict vs step (route như vp2), Σ\|Δ\| in-universe so với vp2 | 2021-10: 8,43 → 5,38 · 2026-06: 9,73 → 3,78 · 2026-10: số mã >0,05 là 26 → 8 | `out/diag/attrib_routeglobal_mcstep.json` |
| PIT đầu độc sau D | PASS, cùng md5 (2026-10 step; 2021-04 strict) | `out/selfcheck_pit.txt` |
| 3 TZ | cùng md5 parquet `771d0c42…` và json `407f1245…` | `out/selfcheck_tz.txt` |
| bỏ VND (2026-10 step) | 204/341 mã >1e-3, 23 mã >0,05, max 0,136 ⇒ VND là phụ thuộc thật | `out/diag/novnd_effect.txt` |

**Mã/dòng không tái lập được bằng PIT** (danh sách đầy đủ theo tháng nằm trong `out/attrib_pit.json` → `mc_diff_tickers`, `route_diff_tickers`):
- 2026-10, nhóm mc/N_next, 27 mã in-universe: AIG, BAF, BID, CLI, CTI, DHT, DIG, GMD, HDB, HHP, HTN, IPA, KDH, MBB, MSB, MZG, NAG, PHR, PLX, RYG, SSI, TCH, TPB, VC3, VDS,
  VHM, VPI. Tất cả có Δlog mc âm, tức PIT-strict thấy vốn hoá nhỏ hơn vì chưa biết số CP sau sự kiện.
- Nhóm route: HDG (POWER→REALESTATE khi cắt), OGC, và HKT ở các tháng cũ.
- Mã có ở vp2 nhưng vắng ở PIT (6–20 mã/tháng, **toàn bộ ngoài universe**, iu_diff=0) là do `last_trade`. V3.1 cắt đuôi giá treo bằng phiên khớp lệnh cuối của TOÀN lịch sử,
  nên biết trước mã sẽ giao dịch lại. PIT thì bỏ các tháng không khớp lệnh cho tới D.

## 4. Nối sổ paper — `dcf_vn_behavioral_20261125/calc/paper_cell_monthly.py`
- Thêm `--lvens2-from <parquet>`, nên không cần `vp2.parquet`. Fail-closed (rc=3) khi: thiếu file; ym/asof_date khác tháng hoặc ngày as-of mà script tự tính; mode ≠ `pit`
  (`--allow-v31` chỉ dành cho selfcheck). `panel_md5` của sổ = md5 file lvens2. Đường `--panel` cũ giữ nguyên; chạy lại đường cũ ra 333/333 khớp TEST, Δ=0.
- So từng dòng với `out/paper_cell_TEST_2026-10.csv` (`out/paper_cell_cmp_2026-10.txt`):
  - v31: 333/333 dòng, mọi cột số Δ=0, ô lệch 0.
  - PIT strict: 333 mã (đủ cùng tập), route lệch 1 (HDG). **Ô đổi 2**: PHR DAT_CON_NEO→RE_DUOC_THUA_NHAN, VCG RE_CHUA_THUA_NHAN→DAT_DANG_NGUOI.
  - PIT step: 333 mã, route lệch 1. **Ô đổi 6**: GIL, LPB, VVS DAT_DANG_NGUOI→RE_CHUA_THUA_NHAN; NTC, TCB, TVN RE_DUOC_THUA_NHAN→DAT_CON_NEO.
  - Diễn giải: tính theo mức, `step` gần vp2 hơn rõ trên 3/3 tháng đo. Tính theo ô (một tháng, N=2 so với 6, quanh trung vị), không kết luận được.
- Idempotent: chạy lại thì in `SKIP` với rc=0. Thiếu file lvens2 cho rc=3. as-of 2026-11 cho rc=3 (universe_pit cache mới tới 2026-11-20).

## 5. Đề xuất vận hành (KHÔNG cài; Mike/user duyệt; đã tra `kb/cron_registry.md` §11)
**Trước khi merge/cài, phải quyết 3 việc:**
1. **mc:** `strict` (code V3.1, đã biết bỏ sót thưởng/chia tách trong ≤ 1 quý) hay `step` (luật mới, gần vp2 hơn về mức). Tôi đề xuất `step`, nhưng nó là luật mới nên cần
   quant-skeptic 1 vòng. Hướng dài hạn là lấy số CP PIT thật (`kb/data_registry/fundamentals/fiinprox_oshares_pit.md`), nhưng làm vậy là đổi mô hình, không còn là "ENS2 V3.1".
2. **Snapshot đóng băng:** chuyển `delisted/` (62 MB) và `px_pre2013_d.csv` (22 MB) về vị trí ổn định ngoài worktree V3.1, ví dụ
   `data/research_frozen/dcf_v31_inputs/`, kèm `MD5SUMS_delisted.txt`, rồi đặt `LVENS2_FROZEN`. Lưu ý thêm: từ as-of 2026-11 (D 2026-11-30 > 2026-11-23), các mã chỉ có ở VND
   (in-universe 2026-10: DSH, GEL, HPA) sẽ thiếu giá tháng mới. Hoặc chấp nhận và ghi nhận qua WARN, hoặc chạy `a0_fetch_delisted.py` hằng tháng. Cách sau là phụ thuộc
   API ngoài (VNDirect); cần Winston/Mike quyết.
3. **Vintage:** `ticker_financial.OShares` bị restate về sau, nên dựng lại một tháng cũ vào ngày khác có thể ra số khác. Sổ ghi số tại thời điểm chạy, append-only;
   KHÔNG dựng lại tháng cũ để "sửa" sổ.

**Thứ tự và giờ** (host cron chạy UTC; giờ ghi theo ICT):
- 23:45 ICT ngày giao dịch cuối tháng (D): `sync_bq_cache_daily.sh` sync `ticker`, `ticker_financial`, `universe_pit`, `fa_ratings_8l` (mtime cache 24/11: 23:45–23:49).
- Ngày làm việc 1–3 của tháng sau, 08:05 ICT: chạy lvens2 (≈ 1–2 phút); 08:10 ICT chạy paper_cell. Cả hai tự fail-closed nếu cache chưa phủ D.
```
# ĐỀ XUẤT — chưa cài. Đường dẫn sau merge: mike/agents/Taylor/research/dcf_lvens2_incremental_20261125 (+ dcf_vn_behavioral_20261125)
5 1 1-3 * 1-5  cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research && YM=$(TZ=Asia/Ho_Chi_Minh date -d "$(TZ=Asia/Ho_Chi_Minh date +\%Y-\%m-01) -1 day" +\%Y-\%m) && LVENS2_FROZEN=/home/trido/thanhdt/WorkingClaude/data/research_frozen/dcf_v31_inputs PYTHONHASHSEED=0 timeout 900 /home/trido/thanhdt/wc_venv/bin/python dcf_lvens2_incremental_20261125/calc/lvens2_incremental.py --asof-ym $YM --mc-pit step --out-dir dcf_lvens2_incremental_20261125/out/monthly && timeout 300 /home/trido/thanhdt/wc_venv/bin/python dcf_vn_behavioral_20261125/calc/paper_cell_monthly.py --asof-ym $YM --lvens2-from dcf_lvens2_incremental_20261125/out/monthly/lvens2_${YM}_mcstep.parquet >> /home/trido/thanhdt/WorkingClaude/mike/logs/paper_cell_monthly.log 2>&1
```
(Dòng này thay dòng cron đề xuất ở `PAPER_REGISTRY_PROPOSED.md`. `5 1` UTC = 08:05 ICT. Nối bằng `&&` nên paper_cell không chạy nếu lvens2 fail.
Nếu lvens2 vẫn ghi đè file tháng khi đã có sổ, paper_cell sẽ SKIP. Muốn chặn hẳn việc dựng lại, thêm cờ skip-if-exists cho lvens2.)
- **Chi phí máy/tháng:** ≈ 1–2 phút CPU một luồng, RSS đỉnh ≈ 2,1 GB (§32: chạy một mình, không song song với backtest nặng), ghi ≈ 0,1 MB parquet/tháng. Không tốn BQ.
- **Rủi ro dữ liệu:**
  - BCTC quý chưa công bố đủ ở as-of: panel dùng kỳ BCTC mới nhất ≤ D trong vòng 200 ngày. Tháng 1/4/7/10 phần lớn mã còn dùng kỳ trước, đúng PIT nhưng cũ hơn.
    Mã có BCTC cũ hơn 200 ngày rơi khỏi panel (đếm qua `ENS2_ok`/`n`).
  - Route đổi sau as-of không sửa lại sổ.
  - Snapshot VND dừng ở 2026-11-23 (xem mục 2 ở trên).
  - BQ restate `OShares` (xem mục 3 ở trên).

## 6. Tái lập
```
cd agents/Taylor/research/dcf_lvens2_incremental_20261125; export PYTHONHASHSEED=0; PY=/home/trido/thanhdt/wc_venv/bin/python
$PY calc/lvens2_incremental.py --mode v31 --asof-ym 2016-02 2021-04 2021-10 2026-05 2026-06 2026-07 2026-08 2026-09 2026-10 --out-dir out/v31
$PY calc/cmp_vp2.py 'out/v31/lvens2_*_v31.parquet' --json out/cmp_v31.json
for ym in 2016-02 2021-04 2021-10 2026-05 2026-06 2026-07 2026-08 2026-09 2026-10; do $PY calc/lvens2_incremental.py --asof-ym $ym --out-dir out/pit; done
$PY calc/cmp_vp2.py 'out/pit/lvens2_*.parquet' --json out/cmp_pit.json; $PY calc/attrib_pit.py 'out/pit/lvens2_*.parquet' out/attrib_pit.json
$PY calc/selfcheck_pit.py 2026-10 step; $PY calc/selfcheck_pit.py 2021-04 strict
```
Tháng ngẫu nhiên: `np.random.RandomState(20261125).choice(period_range('2014-01','2026-04'), 3, replace=False)` cho ra 2016-02, 2021-04, 2021-10.
Parquet đầu ra (out/v31, out/pit, out/diag, out/tz_*, out/final) KHÔNG commit vì là sản phẩm tái lập được. Chỉ commit json/txt đo.
