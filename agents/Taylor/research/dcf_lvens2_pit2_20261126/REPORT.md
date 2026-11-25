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

## 4. Selfcheck
(điền ở cuối job — xem §4 bảng dưới)

## 5. Đổi nhãn ô 2026-05..10
(điền ở cuối job)

## 6. Vận hành (ĐỀ XUẤT — KHÔNG cài)
(điền ở cuối job)

## 7. Tái lập
(điền ở cuối job)
