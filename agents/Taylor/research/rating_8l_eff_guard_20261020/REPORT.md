# Guard eff_date cho dòng rating 8L có Release_Date đáng ngờ — Việc 1 của Phần 3

Job `Taylor_20261020_045223` · 2026-10-20 · user duyệt luật 2026-10-20. **KHÔNG merge, KHÔNG ghi
`tav2_bq.fa_ratings_8l`, KHÔNG sửa `data/results_registry.md` / kho pin.**

- Nhánh `feat/rating-8l-eff-date-guard-20261020` @ **`db7fca931`**, worktree `/home/trido/thanhdt/wt-Taylor_20261020_045223`.
  ⚠️ Worktree tạo từ repo NGOÀI (`/home/trido/thanhdt`, nhánh `main`), KHÔNG phải repo `mike` (`master`):
  `rating_8l_history.py` nằm ở `WorkingClaude/`, thuộc repo ngoài.
- Diff (`git diff --numstat main..feat/rating-8l-eff-date-guard-20261020`): `rating_8l_history.py` +51/−12 ·
  `rating8l_icb_pit_selfcheck.py` +2/−2 · `rating8l_eff_guard_selfcheck.py` +201 (mới).

## 0. Kết luận ngắn

1. **Luật đã cài** đúng như duyệt: RD ≤ RD của quý LIỀN TRƯỚC (cùng mã) HOẶC RD < ngày cuối quý ⇒
   eff_date = `time`. Không đụng cụm 125 ca Q1 đầu tháng 4, không đổi gì khác.
2. **Tác động lên rating SỐ NGUYÊN = 0.** Trên vintage hiện tại (2026-10-20): guard bắt 27 dòng TF, 22 dòng
   đổi eff (tất cả 2026), 20 mã. Bảng sau dedupe: +20 dòng mới, 22 dòng đổi nội dung, nhưng **rating as-of
   không đổi ở bất kỳ ngày nào** (2025-10-01→2026-10-20), **0 lần lật cổng ≤3**, **0 mã khác as-of hôm nay**.
   Lý do: với cả 20 mã, rating quý trước = rating quý bị chép đè (rating 8L dính, dùng chỉ số nhiều năm). Đây là
   **trùng hợp, không phải tính chất cấu trúc** — ca chép RD sau này vẫn có thể lật cổng.
   Đổi được: `tier` (percentile) và `q_time` của dòng có hiệu lực — tier đổi trong một số ngày ở 5 mã
   (BOT, CT6, KSQ, SGP, TLP; ví dụ BOT 01-28→05-03 B→C).
3. **Đường live**: 0 mã đổi rating hôm nay ⇒ `filter_lag_rating_orders` (≤3), custom30V, golive **không đổi**.
   Không mã nào trong 20 mã có trong `custom30v_8l_publish.csv` năm 2026 hay trong `active_nav_{SpaceX,ZaloPay}.json`.
4. **R3 chạy lại (1 trục)**: cả 4 chân **byte-identical** với pin. CONTROL tái lập đúng pin
   (`537e349b` pin0%, `a6ba34d8` pin1M), EXP (cache có guard) ra **đúng hai md5 đó** ⇒ **Δ CAGR/Sharpe/DD = 0**
   ở cả pin0% và pin1M; self-check 0 VND (BAL+LAG) cả 4 chân. Kho pin sandbox từ chối EXP vì "md5 đã nằm trong kho" ⇒
   `compare` không cần chạy (hai ledger là cùng một file).
5. **⚠️ PHÁT HIỆN NGOÀI PHẠM VI, KHẨN**: `tav2_bq.ticker` đang **thiếu 243 mã** (EIN..PHN theo ABC, gồm HPG,
   KLB, HQC, GSM, PGI) so với `tav2_pin.ticker_pin_202610` (1.051 vs 1.294 mã; lastModified 2026-10-19 20:51 ICT).
   Refresh `fa_ratings_8l` 17:30 hôm nay (`fa_ratings_earnings_window_daily.sh`, code main, KHÔNG phải nhánh này)
   sẽ đẩy route 30 mã về COMPOUNDER ⇒ **719 rating / 1.378 tier lệch** so với bảng hiện tại (đo bằng chân CTL
   trên code main). Đã ghi bus `error` `tav2_bq-ticker-mat-243-ma-20261020` + dispatch Winston (nền).

## 1. Bước 1 — `time` ở các ca đáng ngờ có thật sự muộn hơn, không nhìn trộm?

Tập bị bắt trên toàn `ticker_financial` (time ≥ 2014-06-01, N=53.722 dòng, (ticker,quarter) duy nhất):
**27 dòng** (`raw/flagged_all.csv`, `raw/q_flagged.sql`):
- 5 dòng 2015-2017 (TA9, HU4, MTS, NSH, BGW): RD = RD quý trước = `time` (công bố 2 quý cùng ngày) ⇒ eff
  KHÔNG đổi.
- **22 dòng 2026** (12 ở Q1: `time` = 2026-05-04; 10 ở Q2: `time` 08-03…08-14). 7 trong universe = đúng 7 ca chắc chắn
  (BGE, BOT, DGT, HVA, VNE 2026Q1; SGP, VHE 2026Q2).

Đối chiếu (`raw/pins_flagged.csv`, `raw/news_flagged.csv`):
| Kiểm | Kết quả |
|---|---|
| Pin 07-29 / 09-05 / 10-01 / hiện tại | Dòng Q1 có `time` 05-04 ở mọi pin (ổn định). Dòng Q2 **không có** ở pin 07-29, **có** ở pin 09-05 ⇒ vào BQ trong (07-29, 09-05], khớp `time` 08-03…08-14 |
| `data/ticker_financial_breadth.csv` | 2026Q2: 684 mã ngày 07-31 → 926 mã ngày 08-03 ⇒ 08-03 là ngày batch thật |
| `stock_news` (tin FiinGroup) | Không có tin cho chính 22 dòng bị bắt. Tin cạnh đó: SD2 Q1 05-04 (= time), HTE Q1 05-05 (time 05-04), VHE Q1 05-07 (time 05-04, sớm 3 ngày) |

⇒ Với 21/22 dòng, `time` là ngày batch muộn hơn hạn nộp BCTC và nhất quán với pin; **không chứng minh được** từng dòng
`time` ≥ ngày công bố thật (không có tin cho chúng), nhưng không có bằng chứng ngược.

**⚠️ Ca vẫn nhìn trộm sau khi áp luật — HOT 2026Q2** (KHÔNG trong universe: `universe_pit` 07-01→10-19 `n_in=0`):
dòng **vắng ở pin 202608/202609 (cả hai chụp 09-05)**, xuất hiện ở pin 10-01 với `time` = **08-25**, nay `time` = **08-03** (vendor sửa
`time` LÙI). Có guard: eff = 08-03 (thay vì 05-04, bớt ~91 ngày) nhưng **vẫn sớm hơn lúc dữ liệu có trong BQ ≥33 ngày**
(cận dưới: lần đầu thấy giữa 09-05 và 10-01). Luật vẫn áp (nó chỉ làm ca này bớt sai), KHÔNG vá riêng (sẽ thành trục 2).
Cùng hiện tượng `time` sửa lùi ở **ATG 2026Q2** (RD NULL, 08-13 → 08-03; ngoài universe, ngoài phạm vi luật).
⇒ **`time` cũng không bất biến** — bẫy mới cho `fundamentals/ticker_financial.md` (đề xuất §6).

## 2. Code (`rating_8l_history.py`)

- `HIST_SQL` thêm `f.quarter`.
- `release_date_untrusted(df)` (mới): bool Series cùng index; `qend` từ `quarter` ('YYYYQn'); RD quý liền trước
  ghép theo (ticker, qidx−1) — **không** dùng "dòng trước" (quý cách 1 không tính); RD NULL ⇒ False;
  RD quý trước NULL/thiếu ⇒ chỉ xét luật cuối quý.
- `eff_date_of(release_date, q_time, rd_untrusted=None)`: cờ True ⇒ `q_time` ĐÚNG BẰNG (không cộng
  `NULL_RD_EFF_OFFSET_DAYS`, đúng chữ "eff_date = time" của luật). `None` ⇒ hành vi cũ.
- 3 chỗ gọi truyền cờ: `main` (`df["rd_untrusted"]` tính NGAY sau `bq(HIST_SQL)`, TRƯỚC `attach_icb_pit`),
  `attach_icb_pit` (`left.get("rd_untrusted")`), `bank_eff_date` (`r.get("rd_untrusted")`).
- **Cố ý KHÔNG đổi** `rate_row` dòng đọc `Release_Date` cho `MOAT_GOV_CUTOFF` (2025-06-01): mọi dòng bị bắt
  có cả RD lẫn `time` cùng phía mốc (đều 2026, hoặc đều 2015-17) ⇒ không đổi kết quả; đổi sẽ là trục 2.
- Caller cũ không truyền cờ (selfcheck cũ, `custom_basket` không gọi) ⇒ hành vi cũ — **fail-open nếu ai thêm
  chỗ gọi mới mà quên truyền cờ**; G13 khoá 3 chỗ gọi hiện tại.

## 3. Selfcheck

`rating8l_eff_guard_selfcheck.py` (G1-G14, **51 assertion**): 7 ca chắc chắn (giá trị literal) · RD<cuối quý
(HVA/CT6 Q2) · RD NULL (kể cả cả cột NULL) · ngân hàng (`bank_eff_date` + VCB bình thường) · ca bình thường ·
bằng nhau 2015 · quý trước thiếu/NULL/cách 1 quý · không lẫn mã · cụm Q1 đầu tháng 4 KHÔNG bắt · RD == cuối quý
không bắt · index lộn xộn · scalar · `attach_icb_pit` · nối dây main/SQL · dữ liệu thật (27/22/7).
- Chạy: TZ mặc định, `env -u TZ`, `TZ=Pacific/Kiritimati`, `TZ=America/Los_Angeles` ⇒ **51/0/0 cả 4**.
- **9/9 mutant bị bắt** (`<=`→`<`, `<`→`<=` cuối quý, bỏ từng vế, quý trước = −2, eff = time+1, bỏ cờ ở
  attach_icb_pit / bank_eff_date / main).
- Không chạm Executor; vẫn `os.environ.setdefault("MIKE_BOT_TEST_MODE","1")`.
- Selfcheck cũ: `rating8l_icb_pit_selfcheck.py` 17 PASS / 0 FAIL / 2 SKIP (T7 skip vì md5 control vintage, BQ block
  cần `--bq` — skip có từ trước); T6g sửa đúng dòng main mới. `rating_8l_history_bank_aq_selfcheck.py` VERDICT PASS.
  `failopen_telegram_refresh_selfcheck.py` PASS 26.

## 4. Tác động trên bảng (vintage 2026-10-20) — `diff_ratings*.py`

Hai chân dựng cùng lúc, đích ghi non-canonical (`R8L_HIST_OUT`, refresh BQ tự SKIP):
- Lần 1 (ICB từ `tav2_bq.ticker` live): CTL lệch bảng production 719 rating — do `tav2_bq.ticker` thiếu mã (§0.5),
  KHÔNG do guard.
- **Lần 2 (`build_pinicb.py`, ICB từ `tav2_pin.ticker_pin_202610`, cùng patch cho cả 2 chân)**: CTL vs
  `fa_ratings_8l` hiện tại **0 rating / 0 tier lệch trên 53.705 dòng** ⇒ chân CTL tái lập đúng production.
  EXP vs CTL: `out_dedup_row_diff_pinicb.csv` (20 dòng thêm + 22 đổi), `out_asof_diff_segments_pinicb.csv`
  (20 đoạn, 91-197 ngày, `rating_ctl == rating_exp` mọi đoạn, `gate_flip_le3` False mọi đoạn).

## 5. Bước 4 — chạy lại R3 (lệnh + interpreter của mục "2026-10-08", 1 trục)

`run_leg.sh` = bản sao nguyên văn `repin_park0_dep1m_20261008/run_leg{,_main}.sh`, chỉ tham số hoá SRC/CACHE/OUT.
`$DNA_PYEXE`, `BQ_CACHE_THREADS=1`, `AUDIT_END=2026-06-19`, `PARK_STATES=3:0.0`. pin1M chạy trên worktree detached
`f66dab18` (`/home/trido/thanhdt/wt-Taylor_20261020_045223_repin`, worktree gốc của pin đã bị dọn).

Trục duy nhất: `fa_ratings_8l.parquet` trong bản sao cache `data/bq_cache_asof20260729_postrestate_exp_r8lguard`
(mọi file khác = symlink), dựng bằng `make_guard_cache.py`: trên vintage 07-29 có 12 dòng Q1/2026 bị bắt
(Q2 chưa có lúc đó) ⇒ dòng tại RD lấy rating quý trước, thêm dòng tại 05-04 mang rating Q1
(`out_guard_cache_patch_0729.csv`: rating cũ = mới ở cả 12).

| Chân | md5 CSV | = pin? | self-check |
|---|---|---|---|
| CTL pin0% (main code, cache gốc) | `537e349b5589408c994f8aceafeb9a39` | = `R3-park0-pin0pct-SAN` | 0 VND |
| EXP pin0% (main code, cache guard) | `537e349b5589408c994f8aceafeb9a39` | byte-identical | 0 VND |
| CTL pin1M (`f66dab18`, cache gốc) | `a6ba34d83a4d374a73293d897c0b43d9` | = `R3-park0-pin1M-SO-CHINH` | 0 VND |
| EXP pin1M (`f66dab18`, cache guard) | `a6ba34d83a4d374a73293d897c0b43d9` | byte-identical | 0 VND |

⇒ **Δ CAGR / Sharpe / MaxDD = 0** (pin0% 22,12% … pin1M 25,42% giữ nguyên). Đúng kỳ vọng "Δ rất nhỏ" — ở đây bằng 0
vì rating số nguyên không đổi. `pin_ledger.py add` vào kho SANDBOX (`PIN_STORE_WC_ROOT`) bị từ chối rc=2 "md5 đã
nằm trong kho" ⇒ không có số mới để pin; kho thật không bị chạm. Chú ý: số đo trên vintage 07-29 (AUDIT_END 06-19);
các dòng Q2/2026 bị bắt nằm ngoài cửa sổ backtest.

## 6. Rủi ro khi merge

1. **Republish `fa_ratings_8l`** (lần refresh đầu sau merge): +20 dòng, 22 dòng đổi `tier`/dòng rating có hiệu lực;
   rating số nguyên as-of không đổi ⇒ consumer chỉ đọc `rating` (LAG gate, custom30V, golive, pt_v23) không đổi;
   consumer đọc **`tier`** (grep: `regime_size_overlay.py`, `run_fa8l_*`, `dvr8l_tilt.py`, `pt_v23_lag*_research.py`…)
   có thể lệch nhẹ ở 5 mã trong 2026. Backtest đọc bảng LIVE (không cache) sau merge sẽ khác vintage trước merge
   (§8: ghi rõ vintage khi so). Pin R3 dùng cache 07-29 ⇒ không bị ảnh hưởng.
2. **KHÔNG merge/refresh khi `tav2_bq.ticker` còn thiếu mã** (§0.5) — sẽ đẩy 719 rating lệch lên production
   (đúng hệt bản main hiện tại sẽ làm lúc 17:30 hôm nay).
3. Fail-open caller mới quên truyền `rd_untrusted` (§2). `time` cũng bị vendor sửa lùi (HOT/ATG) — guard không
   chống được loại này; cần cột `first_ingested_at` (đề xuất cũ REPORT P1 §4.2).
4. Đề xuất (cần Mike duyệt, §13): thêm bẫy "`time` bị sửa lùi" + "RD chép quý trước" vào
   `kb/data_registry/fundamentals/ticker_financial.md`.

## Tái lập

```bash
cd /home/trido/thanhdt/wt-Taylor_20261020_045223/WorkingClaude && env -u TZ $DNA_PYEXE rating8l_eff_guard_selfcheck.py
O=mike/agents/Taylor/research/rating_8l_eff_guard_20261020   # từ /home/trido/thanhdt/WorkingClaude
$DNA_PYEXE $O/build_pinicb.py <code_dir> <out.csv>             # CTL: WorkingClaude, EXP: worktree
$DNA_PYEXE $O/diff_ratings_pinicb.py $O
$DNA_PYEXE $O/make_guard_cache.py data/bq_cache_asof20260729_postrestate data/bq_cache_asof20260729_postrestate_exp_r8lguard \
  $O/rating_8l_history_EXP_guard_pinicb.csv $O/raw/flagged_all.csv $O/raw/tf_pin07_2026q12.csv
$O/run_leg.sh <SRC> <CACHE> <TAG> BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=off|dep1m
```
Dọn sau khi review: worktree `wt-Taylor_20261020_045223_repin`, cache `data/bq_cache_asof20260729_postrestate_exp_r8lguard`
(chỉ symlink + 1 parquet), 4 CSV `data/v23_golive_audit_*_r8lg_*`.
