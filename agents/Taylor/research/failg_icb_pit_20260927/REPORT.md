# FAIL-G — route (phân ngành) của 8L rating thành POINT-IN-TIME

Job `Taylor_20260927_071003` (resume của `Taylor_20260927_064748` sau usage-limit) ·
branch **`fix/rating8l-icb-pit`** @ `7cdc08cc` + `24c81498`, worktree
`/home/trido/thanhdt/wt-rating8l-icbpit`, rebase trên `main @f2cfb124` (đã gồm ticket 1).
Tách từ `proposal/fail-e-fail-g-pricebasis-gate @806d0eed` — **FAIL-E + cổng cơ học T5 để branch khác**.
**CHƯA MERGE.** Audit gốc: `measurement-integrity-audit-2026-09-27` PART2 §C.

## 0. Lỗi là gì

`rating_8l_history.py` gán route (BANK/INSURANCE/SECURITIES/POWER/CYCLICAL/REALESTATE/COMPOUNDER) từ
`ICB_Code` bằng `SELECT ANY_VALUE(ICB_Code) ... GROUP BY ticker` ⇒ **phân ngành CỦA HÔM NAY được dán
lên toàn bộ panel 2014→nay**, và `ANY_VALUE` **không tất định**. Route quyết định dùng thẻ điểm nào
(`rate_row()`), nên sai route ⇒ sai rating ⇒ sai cổng chất lượng ≤3.

Bản vá: lấy các **đoạn `ICB_Code` LIÊN TIẾP ≥ `ICB_MIN_RUN` (20) phiên** (lọc nhiễu), phát **một dòng
hiệu lực cho MỖI đoạn**, rồi `merge_asof` **backward** theo `eff_date`. Tất định theo định nghĩa.

## 1. Đo trên dữ liệu thật (2026-09-27)

Nguồn `tav2_bq.ticker`: **1.291 mã có `ICB_Code`, chỉ 6 mã từng có >1 giá trị.** Sau lọc đoạn ≥20
phiên, **đúng 3 mã** có >1 đoạn đã xác lập trải trên >1 ICB: **DIH, LIC, TV3**.

| Mã | Các đoạn đã xác lập (≥20 phiên) | Route ctl → new |
|---|---|---|
| DIH | `2357@2011-04-27 (3823)`, `8633@2026-08-21 (22)` | REALESTATE → **COMPOUNDER** |
| HDG | `8633@2010-02-02 (4136)` — đoạn `7535` chỉ **15 phiên** (từ 2026-09-07) ⇒ CHƯA xác lập | POWER → **REALESTATE** |
| LIC | 5 đoạn, `2357@2017-06-05` rồi `2353` — cùng route | không đổi |
| TV3 | 6 đoạn, `2357`→`2791` — cùng route | không đổi |
| SBM | chỉ `7535` xác lập (các đoạn `2357` đều 1-4 phiên = nhiễu) | không đổi |

**A/B trên output rating (cùng vintage live BQ hôm nay, một biến = đường code ICB):**

| Đại lượng | Số dòng | Mã |
|---|---|---|
| đổi `route` | **98** | DIH 49 + HDG 49 |
| đổi `rating` | **36** | HDG 28 + DIH 8 |
| **vượt ranh cổng ≤3 / ≥4** | **12** | HDG 7 + DIH 5 |
| đổi `tier` mà KHÔNG đổi route/rating | **40** (39 mã KHÁC) | spillover — xem §4 |
| byte-identical trên `route` | **1.289/1.291 mã** | |

**Hướng lệch ngược nhau, và đây là điều đáng chú ý nhất:**
* **HDG**: 28/28 dòng rating **TỐT LÊN** (4→3, 4→2, 3→2). Control (buggy) đang **phạt HDG oan** —
  dán route POWER (thẻ điểm proxy vòng đời điện) lên một doanh nghiệp bất động sản suốt 2014-2026.
  7 dòng vượt ranh theo hướng **từ LOẠI thành ĐỦ ĐIỀU KIỆN**.
* **DIH**: 5/8 dòng rating **XẤU ĐI** (3→4) ⇒ từ ĐỦ ĐIỀU KIỆN thành LOẠI.

Artifact: `route_changes.csv`, `rating_changes.csv`, `cross_34.csv`, `ab_summary.json`.

## 2. Ai đọc những dòng này (đường quyết định)

### 2.1 Rổ custom30V — `data/custom30v_8l_publish.csv`
HDG có **26 lượt** trong rổ đã công bố (2014-08-05 → 2025-02-05); **DIH chưa bao giờ vào rổ**.
As-of từng ngày rebal, trên cả 49 rebal lịch sử: **12 lần đổi quyết định cổng ≤3** và **23 lần đổi cờ
`rating ≤ 2`** — cờ này quan trọng riêng vì `custom30v_hybrid.py` có **luật swap rating≤2**.
(`publish_asof_ab.csv`, `gate_asof_ab.csv`)

### 2.2 Cổng LAG P1 — `lag_rating_filter.py` (rating ≤3, auto-exclude ≥4, user chốt 2026-07-27)
HDG xuất hiện **22 quý** trong pool PEAD (`data/lag_dnpr_pool.csv`); DIH **không lần nào** ⇒ 5 lần
vượt ranh của DIH **không tới được book LAG**. Trên 22 quý của HDG: **3 quý đổi quyết định**, cả 3 theo
hướng **từ LOẠI → NHẬN** (2019Q1/Q2/Q3), **cả 3 nằm trong cửa sổ IS**. `ret25` thực tế của 3 quý đó
mean **−3,95%** — n=3, **không suy luận được gì về edge**, ghi ra chỉ để công khai hướng. (`lag_gate_ab.csv`)

### 2.3 LIVE hôm nay (2026-09-27) — chạm đường tiền
| Mã | control | PIT (mới) | cổng ≤3 | cờ ≤2 |
|---|---|---|---|---|
| **HDG** | POWER, rating **3**, tier C | REALESTATE, rating **2**, tier B | True → True (không đổi) | **False → True (ĐỔI)** |
| DIH | REALESTATE, rating 4 | COMPOUNDER, rating 4 | False → False | False → False |

⚠️ **HDG đổi từ rating 3 sang 2 ở dòng LIVE** ⇒ vào tập `rating ≤ 2` mà `custom30v_hybrid.py` dùng cho
luật swap. **Rebal đang hiệu lực là `2026-08-05` (30 tên, `effective_to` để trống) và HDG KHÔNG có
trong đó** — xem §3.2 để biết bản vá có làm HDG vào rổ hay không.

## 3. A/B backtest

### 3.1 R3 (`pt_v23_audit_2014.py`, môi trường pin ticket 1)
Cách làm một-biến: **symlink farm** trên snapshot ghim `data/bq_cache_asof20260729_postrestate`
(2,0GB, không copy), **chỉ thay `fa_ratings_8l.parquet`**; hai chân dùng CÙNG vintage rating (hôm nay),
khác nhau duy nhất ở đường code ICB. `BASKET_CA_SNAPSHOT` ghim như pin.
Lệnh: `./run_leg.sh ctl_anyvalue|new_icbpit`.

| Chân | route | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ | self-check | CSV md5 | rows |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `ctl_anyvalue` control | `ANY_VALUE` (lỗi) | 24,46% | 1,70 | −18,8% | 1,30 | 763,83B | 19,39% | 29,28% | 0 VND BAL+LAG | `30e8c27c` | 16.784 |
| **`new_icbpit`** | **ICB-PIT (bản vá)** | **24,42%** | **1,69** | **−18,8%** | **1,30** | **761,11B** | **19,31%** | **29,29%** | 0 VND BAL+LAG | `67137fef` | 16.808 |
| **Δ (new − ctl)** | | **−0,04pp** | −0,01 | **0,0pp** | **0,00** | −2,72B | −0,08pp | +0,01pp | | | +24 |

IS/OOS **tính lại độc lập** từ chính CSV bằng `extract_peryear.py` (không đọc lại print của engine).

**Kết quả đáng chú ý: chân bản vá rơi ĐÚNG lên bộ ba số pin** — 24,42% / IS 19,31% / OOS 29,29% /
761,11B / Sharpe 1,69 / DD −18,8% / Calmar 1,30, khớp từng chữ số với mục registry
"2026-09-27 — chân WEIGHT custom30V `OShares` bước tại EX-DATE". Chân **control** thì lệch pin +0,04pp.
Đọc đúng chiều nhân quả: **vintage rating của pin (07-29) vốn đã mang route đúng-PIT**, nên bản vá
**giữ pin đứng yên**, còn để nguyên lỗi thì pin sẽ **tự trôi +0,04pp** ở lần resync cache đầu tiên sau
2026-09-07. Đây là lập luận "bản vá bảo vệ số pin", KHÔNG phải "bản vá cải thiện lợi nhuận".

⚠️ **Không byte-identical với pin**: CSV md5 `67137fef` ≠ pin `2f9c3702` và số dòng khác (16.808 vs
16.784 ở control) — vì cả hai chân dùng vintage rating HÔM NAY (thêm 2 quý rating, bank-AQ, dòng
forensic), không phải vintage 07-29 của pin. Trùng ở **6 metric hiển thị**, không trùng ở đường giao
dịch. Đừng trích câu này thành "tái lập byte-identical bản pin".

⚠️ **Chân control ở đây KHÔNG phải số pin 24,42%** — và không thể là, vì pin dùng vintage rating
**07-29**, tức TRƯỚC khi HDG/DIH đổi `ICB_Code` (09-07 / 08-21). Trong snapshot pin, HDG đã là
REALESTATE và DIH đã là COMPOUNDER, **trùng với kết quả của bản vá**. Nói cách khác: **lỗi FAIL-G
chưa từng chảy vào con số pin**; nó chảy vào mọi lần refresh cache/bảng TỪ 2026-09-07 trở đi.
Chênh giữa chân control và pin là do **đổi vintage rating** (+2 quý rating mới, bank-AQ, dòng forensic),
không phải do route.

### 3.2 Publish custom30V (đường tiền)
`cb.build_pit(gate_rating=3, rebal="q2m5", BASKET_SELECT=yieldcombo)` — gọi trực tiếp, **không** đi qua
`custom30_history.py` để khỏi `bq load` vào bảng production. Cache = farm trên `data/bq_cache`
(vintage 09-25, cần thiết vì câu hỏi là về rebal 2026-08-05, nằm sau mốc snapshot 07-29).

| Đại lượng | Kết quả |
|---|---|
| số dòng / số rebal | 1.470 / 49 ở CẢ HAI chân (khớp `custom30v_8l_publish.csv` hiện hành: 1.470) |
| md5 | ctl `d8e5041c` · new `3ca8d3d3` |
| **rebal đổi THÀNH VIÊN** | **6/49**, toàn bộ là LỊCH SỬ 2019-2021 |
| rebal giữ thành viên nhưng đổi `rating` | 13 dòng, chỉ HDG |
| đổi `liq_rank` | 80 dòng (hệ quả số học của 6 rebal đổi thành viên — rank đánh lại) |

6 rebal đổi thành viên, tất cả cùng một hình dạng "**HDG vào, một tên ra**" (đúng 6 lần vượt ranh cổng
≤3 của HDG ở §2.1):

| rebal | vào | ra |
|---|---|---|
| 2019-05-06 | HDG | MBB |
| 2019-08-05 | HDG | DIG |
| 2019-11-05 | HDG | KSB |
| 2020-02-05 | HDG | BMP |
| 2020-05-05 | HDG | DPM |
| 2021-08-05 | HDG | KSB |

### ⇒ Trả lời trực tiếp câu hỏi đường tiền
**Rebal đang hiệu lực `2026-08-05`: thành viên GIỐNG HỆT ở cả hai chân (30/30), HDG KHÔNG vào rổ ở cả
hai, 0 dòng đổi rating.** ⇒ **merge bản vá KHÔNG sinh một lệnh park/trim nào hôm nay.**
HDG vắng rổ hiện tại là do **liquidity rank**, không do cổng rating — nên rating 3→2 của nó (§2.3)
không kéo nó vào rổ. Cờ `rating ≤ 2` vẫn đổi thật và `custom30v_hybrid.py` (luật swap ≤2) đọc cờ đó,
nên **vẫn phải hậu kiểm nhánh hybrid sau merge** — đường publish sạch không có nghĩa mọi consumer sạch.

Không so `weight`: `build_pit` trả membership + `liq_rank` + `rating`; weight do `custom30_history.py`
tính sau từ chính member set theo `namecap` ⇒ member set giống nhau thì weight giống nhau, member set
khác thì weight khác theo. 6 rebal lịch sử ở trên vì thế cũng đổi weight.

## 4. Hiệu ứng lan (phát hiện thêm, không có trong ticket)

`tier` của route COMPOUNDER là **phân vị theo từng quý trong pool COMPOUNDER**. DIH chuyển vào pool đó
⇒ **40 dòng / 39 mã KHÁC đổi tier** (tất cả tốt lên 1 bậc: D→C, C→B, B→A), **không mã nào đổi `route`
hay `rating`**. Cổng của engine đọc `rating` (`custom_basket.py:631` chỉ `SELECT ticker, time, rating`)
nên **không ảnh hưởng quyết định**; nhưng bất kỳ consumer nào đọc `tier` phải biết điều này.
(`engine_visible_diff_in_window.csv`)

## 5. Nợ latent đã sửa luôn (mục 5 của ticket)

`GROUP BY ticker, icb` + `MIN(icb_from)` làm mã đi **X→Y→X** mất lần **quay lại** X (as-of sau
`icb_from` của Y sẽ mãi trả Y). **Đã sửa**: SQL phát một dòng cho MỖI đoạn. Hiện **0/1.291 mã** gặp ca
này ⇒ nếu không có test thì đây là code không ai kiểm ⇒ đã thêm **T2** trong selfcheck, và mutation
"gộp runs" phải bị GIẾT.

## 6. Giới hạn dữ liệu — ghi thẳng docstring + registry (mục 6)

`tav2_bq.ticker` **không phải nguồn phân ngành có vintage**: chỉ 6/1.291 mã từng có >1 `ICB_Code`, và
5/6 lần đổi đầu tiên từ 2017 trở về sau (2 mã chỉ trong 2 tháng gần nhất). ⇒ **tái phân ngành trước
2026 gần như KHÔNG được ghi lại và KHÔNG khôi phục được từ bảng này.** Bản vá bảo đảm (a) **tất định**
và (b) đúng PIT cho những lần đổi **ĐƯỢC GHI** — không hơn. Đúng PIT đầy đủ cần nguồn có vintage
(FiinPro-X / lịch sử ngành HOSE).

Đã ghi: docstring `rating_8l_history.py` (khối "ROUTE (sector) is POINT-IN-TIME since 2026-09-27") +
`mike/kb/data_registry/fundamentals/rating_8l_history.md.proposed` (**§13 — chờ Mike duyệt**, kèm
`index.md.proposed.note` cho dòng index).

## 7. Ngưỡng `ICB_MIN_RUN=20` là một knob có hiệu lực THẬT

HDG có đoạn POWER **15 phiên** ⇒ chưa xác lập ⇒ vẫn REALESTATE. Đoạn đó **sẽ vượt 20 phiên trong
khoảng 1 tuần** (≈2026-10-02) và HDG **sẽ tự đổi sang POWER** ở lần refresh weekly kế tiếp — đổi route
⇒ đổi thẻ điểm ⇒ có thể đổi rating, **không cần ai sửa code**. Đây là hành vi đúng (chờ xác lập rồi mới
đổi), nhưng phải biết trước để không coi cú nhảy rating HDG đầu tháng 10 là sự cố.
20 phiên ≈ 1 tháng giao dịch, chọn để lọc nhiễu 1-4 phiên (ca SBM) — **chưa tối ưu hoá tham số này và
không nên**: nó là ngưỡng vệ sinh dữ liệu, không phải tham số sinh lợi.

## 8. Selfcheck

`WorkingClaude/rating8l_icb_pit_selfcheck.py` — **24/24 PASS, giống từng dòng dưới 4 biến thể TZ**
(ICT / UTC / America-New_York / `env -u TZ`), gồm khối integration BQ và **4/4 mutation bị GIẾT**
(ANY_VALUE-last, first-value, `merge_asof` forward, gộp runs).
Chạy: `python3 rating8l_icb_pit_selfcheck.py --bq --mutations --all-tz`.

Một lỗi của chính test đã bị bắt và sửa trong lúc làm: T5b ban đầu grep chuỗi thô để kiểm "SQL không
còn `ANY_VALUE`/`MIN(icb_from)`" — **fail giả**, vì chính SQL viết hai cái tên đó trong `--` comment để
giải thích vì sao chúng sai (đúng bẫy §22 "kiểm source không còn chứa X bằng chuỗi luôn sai"). Đã sửa
thành strip comment trước khi so.

## 9. Sự cố kèm theo — bảng production `tav2_bq.fa_ratings_8l` ĐANG SAI

Job trước (`Taylor_20260927_052433`) chạy thí nghiệm ICB-PIT có `R8L_HIST_OUT` nhưng **thiếu**
`R8L_HIST_NO_BQ_REFRESH=1` ⇒ `refresh_bq_table()` vẫn `CREATE OR REPLACE` **bảng production** lúc
**13:00:29 ICT 2026-09-27**. Kiểm chứng lại lúc 14:1x: `lastModifiedTime` vẫn 13:00:29, **HDG
route=REALESTATE** (canonical CSV: POWER), **DIH=COMPOUNDER** (canonical: REALESTATE), `COUNT(*)=53660`
⇒ **vẫn chưa được khôi phục**. Bảng trung gian `tmp_r8l_restore` mà phiên trước dựng **đã không còn**.

Lệnh khôi phục (đi đúng đường production, nguồn là canonical CSV mtime 10:36):
```bash
cd /home/trido/thanhdt/WorkingClaude && python3 -c \
 "import rating_8l_history as R; R.refresh_bq_table('/home/trido/thanhdt/WorkingClaude/data/rating_8l_history.csv')"
# rồi PHẢI kiểm chứng bằng truy vấn: HDG=POWER 49 dòng, DIH=REALESTATE 49, COUNT(*)=53660.
# refresh_bq_table() bắt MỌI Exception và chỉ in "[!] skipped" -> stdout không phải bằng chứng.
```
Tôi **bị auto-mode classifier chặn** ở bước ghi BQ (cả phiên trước và phiên này) và **không lách**.
Bus question: `restore-fa-ratings-8l-BQ-can-quyen-ghi-VAN-TREO`.
Snapshot bản bị ghi đè: `../measurement_integrity_audit_20260927/part2/fa_ratings_8l_CONTAMINATED_snapshot_20260927.csv`.

⚠️ Hệ quả nghiệp vụ: trong lúc bảng sai, `regime_size_overlay` / `custom30v_hybrid` (swap ≤2) /
golive sizing / `build_universe_pit_quality` / `lag_rating_filter` đọc số chưa được duyệt. Nghịch lý
cần nói rõ: **bảng đang chứa đúng dữ liệu của bản vá CHƯA được duyệt** — nếu user duyệt merge thì nội
dung bảng thành hợp lệ, chỉ cần re-pin CSV; nếu không duyệt thì phải khôi phục.

## 10. Một artifact của phiên trước đã bị loại bỏ

`r8l_hist_EXP_icbpit.csv` mà phiên trước để lại **md5 trùng khít canonical** (`68ae047b…`) ⇒ A/B đó so
control với CHÍNH NÓ và cho "0 thay đổi" — **vô nghĩa**. Đã xoá và dựng lại
`r8l_hist_EXP_icbpit_v2.csv` (md5 `ea66aa95…`, có xác nhận dòng
`[bq] refresh SKIPPED (R8L_HIST_NO_BQ_REFRESH=1)` trong `out_EXP_v2.txt`).

## 11. Việc cần NGƯỜI

1. **User duyệt merge** branch `fix/rating8l-icb-pit` (sau `verify_finding.sh`/quant-skeptic). Nếu merge:
   sinh lại `data/rating_8l_history.csv` + refresh `tav2_bq.fa_ratings_8l`, rồi hậu kiểm cổng LAG và rổ
   custom30V; **không tự re-pin R3** (xem §3.1 — pin không chứa lỗi này).
2. **Một phiên có quyền ghi BQ** chạy lệnh khôi phục §9 (hoặc user duyệt merge ⇒ bảng thành hợp lệ).
3. **Mike duyệt §13**: `kb/data_registry/fundamentals/rating_8l_history.md.proposed` (+ dòng index).
