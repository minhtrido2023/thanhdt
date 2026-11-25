# lvens2 pit2: sửa theo quant-skeptic REFUTED (job Taylor_20261125_160331)

Nhánh `session/Taylor_20261125_160331`, worktree `wt-dcf-lvens2-pit2-20261126`, tách từ mike master `4a5cba411`. Bản đã merge (`dcf_lvens2_incremental_20261125/`) KHÔNG sửa.
Chỉ nghiên cứu, DISPLAY-ONLY: KHÔNG cron, KHÔNG chèn registry, KHÔNG wire, KHÔNG email. Snapshot VND đọc từ `data/research_frozen/dcf_v31_inputs/out`, không fetch.

## 0. Kết luận
1. **Chọn mc = `stepcar`, theo luật đã khoá TRƯỚC khi đo** (`PRELOCK.md`, commit `ae1563d72`; khai N trials = 4: strict/step/stepca/stepcar).
   Thước đo là sai số số CP ngầm trong mc so với số CP PIT thật tại D (fiinprox, neo ex-right), trên 51.929 ô (mã, tháng) in_universe, 643 mã, 2014-01..2026-08.
   Mean |log err|: strict 0,0197 · step 0,0161 · stepca 0,0130 · **stepcar 0,0093**. stepcar tốt nhất ở **13/13 năm**. KHÔNG dùng "gần vp2" làm tiêu chí.
2. **E ngân hàng đã sửa (bản đầu của tôi sai, đã bỏ).** Luật cuối: E = BVPS×OShares chỉ được sửa khi E tụt >7% so với kỳ trước VÀ mức tụt được giải thích bởi sự kiện đổi số CP
   **đã công bố ≤ D** (tích tiền tố Π(1+r) khớp trong 0,06 log). Khi đó E = E_raw × Π(1+r), tức E và mc cùng một cơ sở cổ phiếu.
   Tụt không giải thích được thì giữ E_raw và gắn cờ `E_unexpl` (1–6 mã/tháng).
3. **Phần rò không sửa được bằng PIT (nói thẳng).** Ở as-of 2026-05, OCB, KLB, VBB, ACB (và ABB) có BVPS đã ở cơ sở CP sau sự kiện, trong khi sự kiện công bố SAU D=05-29
   (OCB pub 06-23, ACB 06-05, KLB 06-25, VBB 06-19). Cache vintage 2026-07-28 cho BVPS **giống hệt** hiện tại, nên không tách được vendor ghi BVPS lúc nào.
   Các mã này mang cờ `E_unexpl` trong sổ. Cũng vậy: 1.240/1.841 ô có sai số >5% dưới stepcar là do **OShares của kỳ BCTC đã mang số CP tương lai** (TRAP restate) — biến thể mc nào cũng không sửa được (§3.3).
4. **Selfcheck PIT: poison tách khỏi cut, có mutation test.** Lần chạy đầu đã **bắt được một lỗi thật** của tôi trong e_guard: tích tiền tố phụ thuộc thứ tự các dòng sự kiện
   cùng ngày ex (quicksort không ổn định), nên poison đổi lv_HEDf ~1e-5 trên 1.039 dòng. Lỗi này không phải rò dữ liệu nhưng làm mất tính tất định. Đã sửa (gộp sự kiện theo
   (mã, ngày ex)); chạy lại thì poison = base (md5 `dea31ba7`). Kết quả mutation và 3 TZ ở §4.
5. **Sổ paper (`paper_cell_monthly_pit2.py`):** ghi `mc_pit`, `lvens2_md5`, `script_md5`, md5 manifest frozen, md5 extract CA, cờ `E_unexpl`. Fail-closed khi đổi biến thể
   hoặc script giữa chừng, khi cache không tươi, sai tháng/ngày/mode. Append thật (mở 'a'), kèm md5 từng khối tháng ở sidecar, kiểm lại trước mỗi lần ghi. 9/9 ca kiểm đúng (§4).
6. **Đổi nhãn ô 2026-05..10** (stepcar so với bản đã merge và so với vp2) liệt kê ở §5. Ô đổi do mc là **thật** (sự kiện thưởng hoặc cổ tức CP lớn: TRC ×4, L40 ×2,2, PHR ×1,8, GEX ×1,5).
   Ô đổi do bank E là **thật** (KLB, MSB). Phần còn lại là mã sát trung vị (|v−0,5|<0,05), tức artefact ngưỡng.

## 1. Đổi gì so với bản đã merge (`lvens2_incremental.py` md5 `357f69c5…` → `calc/lvens2_pit2.py`)
- **Hồi quy:** `--mc-pit strict|step --no-eguard` cho lại bản merge **Δ=0** (2026-10, 1.086 dòng, mọi cột lv, mc, E).
- **mc `stepca`/`stepcar`:** mc = Price(D) × N_row × Π(1+exercise_ratio), lấy trên `tav2_bq.corporate_action` ISS, status ≠ not_executed, ratio > 0,
  method ∈ {Trả Cổ tức bằng Cổ phiếu, Cổ phiếu thưởng} (stepcar thêm Quyền mua CP cho Cổ đông hiện hữu), với ngày BCTC < ex ≤ D và public_date ≤ D. **Không bao giờ dùng DIV.**
  Nguồn là extract đóng băng `out/ca/ca_extract_20261125.csv` (34.159 dòng ISS/DIV/AIS, md5 `28418e9d…`, kiểm fail-closed). Đã dedup (ticker, ex, method, ratio).
  - Quyền mua (stepcar): tính đủ tỉ lệ, tức **cận trên**. Ca thấy được: RYG 2026-09 có 17% CP + 50% quyền ⇒ ×1,755, nhưng AIS thực tế cho thấy quyền chỉ thực hiện một phần.
    Fiinprox neo số CP ở ex-right nên phần nào thuận cho stepcar khi đo (ghi nhận, không đổi luật đã khoá).
  - 61/5.477 sự kiện đổi số CP có public_date > ex_date (upsert ghi đè public_date, Bẫy 2b registry). Những sự kiện này bị loại khi ex ≤ D < pub (bảo thủ).
- **e_guard (E ngân hàng):** chỉ áp cho dòng `E_src=BVPSxOS` (không có nợ ngắn/dài hạn). Hệ số cơ sở mang theo qua các dòng cùng OShares, reset khi OShares đổi.
  Sự kiện CÙNG ngày ex gộp thành 1 bước. N (pick_n) vẫn tính từ E gốc nên không kéo số CP tương lai vào N.
  - **Bản đầu (đã bỏ, có trong git `a96492ba2`):** E = E_trước + NP_P0 khi tụt >7%. Bản này **lan truyền**: dòng đầu TCB 2018-06 sai cơ sở (BVPS trước niêm yết) làm E TCB
    phình 2× vĩnh viễn (2026-05: 251 T thay vì 187 T). LPB tụt thật vì cổ tức tiền 2025 cũng bị "sửa". Luật giải-thích-bằng-CA bỏ được cả hai ca.
- **Poison tách cut:** `load()` = poison (mọi nguồn, lúc nạp) rồi mới cắt. `nocut={nguồn}` để làm mutation. `--route-global` giờ vẫn bị poison (chỉ bỏ cắt).
- **Freshness fail-closed:** manifest cache `ticker_financial`/`fa_ratings_8l` max_time phải ≥ D − 10 ngày. universe_pit phải phủ D (giữ như cũ).
- **`--cache-root`** cho selfcheck vintage (universe_pit luôn đọc cache hiện tại vì cache cũ không có bảng này).
- Cột mới: `E_raw, E_fix, E_unexpl, N, N_mc, ca_ratio, ca_n, mc_pit`. JSON ghi thêm md5 extract CA, manifest frozen, px_pre2013, cache_root/vintage, freshness.

## 2. Biến thể mc — chọn theo PRELOCK (`calc/mc_err.py`, `out/mc_err.json`)
| biến thể | mean\|log err\| | p95 | ô >5% | nhóm có sự kiện: mean / >5% | vs N kỳ BCTC kế (phụ) |
|---|---|---|---|---|---|
| strict | 0,0197 | 0,107 | 7,26% | 0,220 / 81,5% | 0,0297 |
| step | 0,0161 | 0,071 | 7,24% | 0,132 / 48,5% | 0,0258 |
| stepca | 0,0130 | 0,026 | 4,24% | 0,144 / 47,1% | 0,0230 |
| **stepcar** | **0,0093** | **0,016** | **3,55%** | **0,101 / 38,8%** | **0,0214** |

N = 51.929 ô, 4.625 ô có sự kiện. Đây là ô (mã×tháng), không phải sự kiện độc lập. Thắng 13/13 năm (`by_year_mean_abs`), nên kết luận không dựa vào vài năm.
Luật: lõi {strict, step, stepca} ⇒ stepca (cách hạng 2 là 19%). stepcar tốt hơn stepca 28,6% (≥ 10%) và tỉ lệ >5% không tăng ⇒ **stepcar**.
Step có lỗi 0,0047 ở nhóm KHÔNG có sự kiện (cổ tức tiền), còn stepca/stepcar chỉ 0,0002–0,0003. Đây chính là lỗi skeptic nêu ở mục 1.

### 2.1 Phần dư không sửa được bằng biến thể mc
Có 1.841 ô >5% dưới stepcar:
- **1.240 ô N_row THỪA** so với sự thật, tức OShares của kỳ BCTC đã mang số CP tương lai (TRAP `ticker_financial_oshares.md`).
- 601 ô thiếu. Trong đó 414 ô có sự kiện ex trong 365 ngày trước ngày BCTC (OShares chưa cập nhật), nhưng chỉ 131 ô sửa được nếu lùi cửa sổ về BCTC−365. Không làm vì lợi nhỏ và có rủi ro đếm đôi.
- Hướng đúng dài hạn là neo N bằng `oshares_live` (live=False) hoặc fiinprox cho lịch sử. Làm vậy là đổi mô hình, nên để quyết sau.

## 3. Ngân hàng — E và cơ sở cổ phiếu
(số cuối ở `out/cmp_cells_changes.csv`, `out/final/*_mcstepcar.json` → `E_unexpl_tickers`; bảng ở §5)
- 2026-10: TCB E 131,5 → **197,3 T** (bonus 50% ex 10-29, pub 10-23 ≤ D). mc stepcar ×1,5 cùng cơ sở. Ở bản merge, step cho lv −0,187 vì đếm đôi (E thiếu × mc đã bước).
  Bản mới không còn đếm đôi. MBB E 125,4 → 158,6 (cổ tức CP 15% + quyền 10%, ×1,265). MSB 37,7 → 45,2 (×1,2).
- 2026-05: OCB/ACB/KLB/VBB/ABB mang `E_unexpl` (xem §0.3). LPB 2025-07 tụt thật (cổ tức tiền) ⇒ giữ nguyên, không sửa.
- HDB/TPB: đã đi ex trước D và có hệ số stepcar (HDB ×1,312, TPB ×1,15). E của dòng BCTC 07-31 đã cùng cơ sở OShares nên không sửa.

## 4. Selfcheck (đều 0 lỗi)
**4.1 PIT poison/mutation** — `calc/selfcheck_pit2.py 2026-10 stepcar` (rc=0, bảng `out/selfcheck_pit2_2026-10_table.txt`; md5 lấy từ artefact `out/sc/`):

| ca | kết quả | md5 |
|---|---|---|
| poison (phá MỌI nguồn sau D lúc nạp) vs base | PASS | `dea31ba7` = `dea31ba7` |
| bỏ cắt px / vnd_px / fin / vnd_fs / rating | DETECTED ×5 | `356d3050` `6aae295f` `d960338d` `38b4853b` `02ca726a` |
| bỏ cắt universe | BLIND (khai trước: ghép theo (mã, phiên ≤ D)) | `dea31ba7` |
| bỏ cắt ca | BLIND (khai trước: `ca_factor` tự lọc ex ≤ D, pub ≤ D) | `dea31ba7` |
| bỏ cắt ca **và** phá lớp lọc trong (`leaky_ca_factor`, bỏ pub ≤ D) | DETECTED | `017b68d5` |

Lần chạy trước (attempt 1, 23:50) báo `ca` là BLIND(UNEXPECTED). Lý do: ca có hai lớp PIT, bỏ một lớp thì không lộ. Đã thêm ca+inner để chứng minh lớp trong thật sự chặn. EXPECT_BLIND được khai trong code, không sửa sau khi thấy kết quả.

**4.2 Ba TZ:** base 2026-10 md5 `dea31ba7` dưới Asia/Ho_Chi_Minh, America/New_York, `env -u TZ` (`out/selfcheck_pit2_tz_*.txt`). File final `out/final/lvens2_2026-10_mcstepcar.parquet` dựng lại độc lập cũng ra `dea31ba7` (tất định).

**4.3 Sổ** — `calc/selfcheck_paper_cell_pit2.sh`, 9 ca + T8b, **PASS dưới 3 TZ** (`out/selfcheck_paper_cell_pit2.txt`):
T1/T2 ghi · T3 chạy lại ⇒ SKIP · T4 đổi biến thể giữa chừng ⇒ rc 3 · T5 sidecar sai biến thể ⇒ rc 3 · T6 file sai tháng ⇒ rc 3 · T7 sửa 1 dòng cũ ⇒ rc 3 ·
T8 khôi phục rồi ghi, và byte cũ giữ nguyên (T8b) · T9 manifest `ticker_financial` max_time 2026-10-01 < D−10 ⇒ rc 3.

**4.4 Vintage** (skeptic mục 3) — `calc/vintage_drift.py`: dựng as-of 2026-05 và 2026-06 (stepcar) từ `data/bq_cache_asof20260728`, so với cache hiện tại (`out/vintage_drift.json`).

| as-of | N chung (lv cả hai) | lv giống hệt | \|Δlv\|>0,01 / >0,05 | mean / p95 / max \|Δlv\| | Spearman | đổi nửa trên/dưới trung vị | E hoặc N đổi |
|---|---|---|---|---|---|---|---|
| 2026-05 | 1.087 (1.052) | 363 | 19 / 8 | 0,0014 / 0,0035 / 0,140 | 0,99988 | 2 | 0 / 0 |
| 2026-06 | 1.075 (1.041) | 360 | 16 / 5 | 0,0010 / 0,0035 / 0,081 | 0,99992 | 4 | 0 / 0 |

- Drift lớn nhất đến từ **mc**: giá bị restate sau ngày chụp cache (2026-05: 10 mã, ví dụ HPI +0,140, PTT −0,138). Phần còn lại đến từ MULT và HEDf: trung vị nhóm và hệ số hedonic dịch nhẹ (cả nhóm POWER cùng −0,032).
  Cache hiện tại có thêm mã mà vintage không có: BPC, DNN, VLW (2026-05), QST (2026-06).
- **E và N giống hệt giữa hai vintage.** Vì vậy đo vintage **không** phát hiện được rò BVPS của OCB/ACB/KLB/VBB (§0.3): cache 07-28 đã mang BVPS restate rồi. Giới hạn này nói thẳng, không coi là đã sạch.
- Hệ quả vận hành: dựng lại cùng một tháng vào ngày khác có thể lệch ô ở 2–4 mã sát trung vị. Vì vậy sổ là append-only, không dựng lại để "sửa".

## 5. Đổi nhãn ô 2026-05..10 (`out/cmp_cells.json`, `out/cmp_cells_changes.csv`)
Số ô đổi so với stepcar (N ô in-universe đủ dữ liệu: 391/374/360/350/344/333):

| as-of | vs merged | vs vp2 | merged vs vp2 | strict vs vp2 | step vs vp2 | stepca vs vp2 |
|---|---|---|---|---|---|---|
| 2026-05 | 6 | 2 | 8 | 10 | 2 | 2 |
| 2026-06 | 10 | 4 | 8 | 10 | 4 | 6 |
| 2026-07 | 0 | 2 | 2 | 2 | 2 | 2 |
| 2026-08 | 2 | 4 | 4 | 4 | 4 | 4 |
| 2026-09 | 6 | 4 | 6 | 6 | 4 | 2 |
| 2026-10 | 6 | 4 | 2 | 2 | 4 | 0 |
| **tổng** | **30** | **20** | 30 | 34 | 20 | 16 |

Giải thích từng ô. **Thật** nghĩa là sửa đúng cơ chế; **artefact** nghĩa là ngưỡng trung vị hoặc nguồn so sánh không PIT.
- **Thật, do mc bước theo sự kiện đổi số CP ≤ D (bản merge bỏ sót):** GEX 05/06 (×1,5) · L40 06 (×2,2) · TRC 09 (×4) · PHR 09/10 (×1,8) · TCM 05 (×1,05) · VFS 05 (×1,1).
  Δv_grp từ −0,27 đến −0,63. Ở các mã này mc cũ thiếu số CP mới ⇒ lv cao giả.
- **Thật nhưng là CẬN TRÊN, do có quyền mua trong hệ số:** RYG 09/10 (×1,755, gồm 50% quyền mà AIS cho thấy chỉ thực hiện một phần; §1), SMC 10 (×1,5, cả vs vp2), VVS 06 (×2,0).
  Cả ba ô KHÁC giữa stepcar và stepca (đã kiểm). Tổng số ô stepcar≠stepca trong 6 tháng là 8 (06 JVC, VVS · 09 RYG, SZC · 10 SMC, RYG, VVS, GIL). Đây là các ô nhạy với lựa chọn stepcar.
- **Thật, do E ngân hàng (e_guard):** KLB 06 (E_fix, +0,39). KLB 08 (vs merged): E/mc tháng 08 không đổi, nhưng lv_D0B −0,046 → 0,735 vì chuỗi E lịch sử (các kỳ 05/06) không còn cú tụt giả.
  MSB 08/09 (vs vp2; E ×1,2, cùng cơ sở với mc ×1,2).
- **Đối xứng ở ngân hàng, sát trung vị:** TCB 08/09, CTG 06. E và mc không đổi; đổi hạng vì KLB/MBB/MSB/VAB/VIB trong nhóm BANK (n≈26) đổi lv. Đây là hệ quả hợp lệ của xếp hạng trong nhóm, không phải lỗi của chính mã.
- **Artefact so với vp2 (vp2 không PIT, có N_next/route look-ahead):** TRC 07 (v_grp vp2 0,05 → 0,56) và TOS 06. Bản merge cho ô giống stepcar, tức chênh này đã có từ bản PIT trước, không do pit2.
- **Artefact ngưỡng** (|v−0,5| < 0,05, lv gần như không đổi): vs merged gồm TTN, DPG, DBC 05 · JVC, VSC, DL1, TLG 06 · TLD, SZC, EVG 09 · VVS, GIL, VCG 10 (**13 ô**).
  vs vp2 gồm BGE, HBC 05 · NTL 07 · CIG, QNS 08 · SZC 09 · VVS, GIL 10 (**8 ô**). Lệch hạng ±0,01 làm đổi ô, nên đọc sổ theo hạng liên tục, không theo nhãn cứng.
- Cờ `E_unexpl` (E tụt >7% không giải thích được bằng CA ≤ D): 05 ABB/ACB/KLB/OCB/VBB · 06 ABB/VBB · 07 LPB/MBB/MSB/VAB/VIB/VPB · 08 LPB/VPB · 09 LPB · 10 TIN.
  Cờ này được ghi vào sổ để người đọc biết, KHÔNG được dùng để loại mã.

## 6. Vận hành (ĐỀ XUẤT — KHÔNG cài; tra `kb/cron_registry.md` §11 trước khi cài)
**Còn chặn trước khi cài (blocker):**
- **B1 — Extract CA hằng tháng.** `CA_MD5` hiện viết cứng trong `lvens2_pit2.py`, nên mỗi lần làm mới extract `corporate_action` sẽ đổi `script_md5`, và sổ sẽ fail-closed (T4) mỗi tháng.
  Sửa đề xuất: đọc `LVENS2_CA` + `LVENS2_CA_MD5` từ env, đặt file theo tháng `out/ca/ca_extract_<YYYYMM>.csv`. `ca_md5` đã nằm trong từng dòng sổ.
  Script cố định, dữ liệu đổi thì ghi lại. Chưa làm ở job này để không đổi md5 các số đã đo.
- **B2 — quant-skeptic vòng 2** trên stepcar + e_guard + vintage (gate trong entry đề xuất).
- **B3 — Snapshot VND dừng ở 2026-11-23** (giữ nguyên từ bản merge §5.2): DSH/GEL/HPA sẽ thiếu giá từ as-of 2026-11.

**Dòng cron đề xuất** (thay dòng của bản merge; host cron chạy UTC, `5 1` = 08:05 ICT; thứ tự: sync 23:45 ICT ngày D, sau đó ngày làm việc 1–3 tháng sau):
```
# ĐỀ XUẤT — chưa cài, chờ B1+B2 + user duyệt. Đường dẫn sau merge: mike/agents/Taylor/research/dcf_lvens2_pit2_20261126
5 1 1-3 * 1-5  cd /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dcf_lvens2_pit2_20261126 && YM=$(TZ=Asia/Ho_Chi_Minh date -d "$(TZ=Asia/Ho_Chi_Minh date +\%Y-\%m-01) -1 day" +\%Y-\%m) && LVENS2_FROZEN=/home/trido/thanhdt/WorkingClaude/data/research_frozen/dcf_v31_inputs/out PYTHONHASHSEED=0 timeout 900 /home/trido/thanhdt/wc_venv/bin/python calc/lvens2_pit2.py --asof-ym $YM --mc-pit stepcar --out-dir out/monthly && timeout 300 /home/trido/thanhdt/wc_venv/bin/python calc/paper_cell_monthly_pit2.py --asof-ym $YM --lvens2-from out/monthly/lvens2_${YM}_mcstepcar.parquet >> /home/trido/thanhdt/WorkingClaude/mike/logs/paper_cell_monthly_pit2.log 2>&1
```
- Sổ mới: `out/paper_cell_ledger_pit2.csv` + `.blocks.jsonl`. Không trộn với sổ của bản merge (`mc_pit` khác thì sổ sẽ fail-closed).
- Chi phí: khoảng 53 giây/tháng một luồng, dựng cả 4 biến thể (đo bằng mtime `out/final`: 6 tháng tuần tự 00:06:54→00:11:19). RSS khoảng 2,1 GB (ước lượng, lấy từ bản merge, chưa đo lại). Không tốn BQ.
  Chạy một mình theo §32.
- Rủi ro: ngày 1–3 chưa có BCTC quý mới thì panel dùng kỳ cũ hơn. Cách này đúng PIT. Drift vintage nêu ở §4.4.

## 7. Tái lập
```bash
cd mike/agents/Taylor/research/dcf_lvens2_pit2_20261126
export LVENS2_FROZEN=/home/trido/thanhdt/WorkingClaude/data/research_frozen/dcf_v31_inputs/out PY=/home/trido/thanhdt/wc_venv/bin/python
$PY calc/mc_err.py                                                     # §2 → out/mc_err.json
for ym in 2026-05 2026-06 2026-07 2026-08 2026-09 2026-10; do $PY calc/lvens2_pit2.py --asof-ym $ym --mc-pit all --out-dir out/final; done   # 1 as-of mỗi lần
$PY calc/cmp_cells.py out/cmp_cells.json out/cmp_cells_changes.csv     # §5
$PY calc/selfcheck_pit2.py 2026-10 stepcar out/sc                      # §4.1 (rc 0)
TZ=America/New_York $PY calc/selfcheck_pit2.py 2026-10 stepcar out/sc_tz_ny base; env -u TZ $PY calc/selfcheck_pit2.py 2026-10 stepcar out/sc_tz_unset base   # §4.2
bash calc/selfcheck_paper_cell_pit2.sh                                 # §4.3
for ym in 2026-05 2026-06; do $PY calc/lvens2_pit2.py --asof-ym $ym --mc-pit stepcar --out-dir out/vintage --cache-root /home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260728; done
$PY calc/vintage_drift.py out/vintage_drift.json out/vintage_drift_top.csv   # §4.4
$PY calc/lvens2_pit2.py --asof-ym 2026-10 --mc-pit strict --no-eguard --out-dir out/regress   # hồi quy Δ=0 vs bản merge (§1)
```
md5 (8 ký tự đầu): `lvens2_pit2.py` ad565e0d · `paper_cell_monthly_pit2.py` 65eaf7e4 · `selfcheck_pit2.py` 20e4b7b8 · `mc_err.py` e4ebca73 · `cmp_cells.py` f9a3e94c · `vintage_drift.py` e59ecfe8 ·
extract CA 28418e9d · manifest frozen 59a5ee62 · cache `ticker_financial` ab5d424d (max_time 2026-11-20) · `fa_ratings_8l` 2ab15311 · final 2026-10 stepcar dea31ba7.
Không dùng `profit_*`. Không dùng `ticker_prune`. Universe lấy từ `universe_pit`.
