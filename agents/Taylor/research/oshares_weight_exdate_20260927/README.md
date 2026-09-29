# TICKET 1 — chân WEIGHT custom30V: `OShares` phải bước tại EX-DATE, không phải ngày công bố quý

Job `Taylor_20260927_043542` · 2026-09-27 · branch `fix/custom30v-weight-oshares-exdate`
(worktree `/home/trido/thanhdt/wt-c30v-wexdate`, **CHƯA merge**) · nhánh cơ sở = `main` @ `a808a613`
(đã có bản sửa chuỗi return JOB C).

Người nêu: quant-skeptic, khi verify `custom30v-fix-repin-R3`. Đường tiền LIVE:
`mcapw` → `custom30_history.py` → `custom30v_8l_publish.csv` → `tav2_bq.custom30v_8l` →
`compute_park_trim.py`.

---

## 0. ĐO TRƯỚC KHI SỬA

`custom_basket` lấy `OShares` bằng `LEFT JOIN ... ON t.time >= f.time`, và `f.time` của
`ticker_financial` **chính là ngày công bố** (đo thật: bằng đúng `Release_Date`, TCB 2024:
`time == Release_Date` ở cả 4 quý). Nên mỗi lần số cổ phiếu đổi, bước nhảy rơi vào ngày CÔNG BỐ
QUÝ, không phải ngày cổ phiếu thật sự xuất hiện.

**Phạm vi đo**: 203 mã đã từng vào rổ custom30V (`data/custom30v_8l_publish.csv`), 2014-01-01 →
2026-09-25, vintage `ticker_financial` = cache đã ghim `bq_cache_asof20260729_postrestate` (chính
cache mà bản pin R3 dùng) và đối chiếu lại trên cache live (kết quả gần như trùng: 1.521 bước vs
1.489, cùng phân phối).

| | |
|---|---:|
| Bước `OShares` 2014-2026 | **1.489** (192 mã) |
| Khớp được một sự kiện `corporate_action` | **757** (50,8%) |
| …trong đó rơi ĐÚNG ngày | **9** |
| …**TRỄ** (ngày quý sau ex-date) | **675**, median **47** ngày |
| …**SỚM** (dòng quý đã mang số của sự kiện đi ex SAU đó) = **LOOK-AHEAD** | **73**, min **−45** ngày |
| Không khớp sự kiện nào (412 không có sự kiện trong cửa sổ + 328 có sự kiện nhưng cỡ không khớp) | 732 |

Chạy lại bằng CHÍNH code sản xuất (`oshares_pit_grid`) trên 203 mã: **737/1.489 bước (49,5%) được
dời** — 663 dời SỚM hơn (median 46 ngày, sửa staleness) và 74 dời MUỘN hơn (median −28 ngày, **bỏ
look-ahead**). Độ lệch ngày: median 42, p90 77, max 99. Trong nhóm bước LỚN (`|ratio−1| ≥ 5%`):
663/964 = 68,8% được dời.

**Đối chiếu nguồn thứ 2** (`mike/data/fiinprox_oshares_pit_20260926.csv`, registry
`fundamentals/fiinprox_oshares_pit.md`, status **UNVERIFIED-PIT** — chỉ dùng để đối chiếu):
702 bước có cả hai nguồn, **85,9% cùng NGÀY** với `corporate_action`, |lệch| median **0** ngày.
Con số này khớp với nghiệm thu H3 (±3 phiên 85,7%) — hai nguồn độc lập nói cùng một chuyện, và
`corporate_action` vẫn là nguồn sự thật.

### Ghi chú về ca quant-skeptic nêu — ngày 2024-05-21 KHÔNG tái lập được
Bản dispatch ghi "TCB OShares ×2 tại **2024-05-21**". Đo lại trên **cả hai** nguồn
(`tav2_bq.ticker_financial` live và parquet cache đã ghim): TCB chỉ có 4 dòng quý trong 2024 —
01-22, 04-22, **07-22**, 10-22 — và bước ×2 nằm ở **2024-07-22**; `Release_Date` trùng `time` ở cả
4 dòng. Ex-date thật 2024-06-20 (`ISS`, `Cổ phiếu thưởng`, `exercise_ratio=1,0`, public_date
06-13). ⇒ **hướng lệch là TRỄ 32 ngày**, không phải sớm 30 ngày. Kết luận của quant-skeptic về
LỚP lỗi là đúng và đã xác nhận trên 737 bước; chỉ con số ngày cụ thể là không tái lập được, và
không đổi kết luận.

### Ảnh hưởng lên weight — `custom30v_8l_publish.csv`
Chạy `custom30_history.py` (đường publish thật, config production `BASKET_SELECT=yieldcombo`,
`gate_rating=3`, `namecap` 10%) hai chế độ trên CÙNG vintage, `bq load` bị chặn bằng stub:

* **THÀNH VIÊN rổ không đổi một dòng nào** (selection xếp hạng theo `Volume_3M_P50 × giá`, không
  dùng số cổ phiếu) — 1.470/1.470 dòng khớp `(rebal_date, ticker, liq_rank)`.
* **16/49 rebal đổi weight; 33 rebal BYTE-IDENTICAL.**
* Nặng nhất: `2021-11-05` sum|Δw| **2,748pp** (MSB −0,870pp, SHS −0,504pp) · `2020-02-05` **2,432pp**
  (SHB **+1,216pp**) · `2018-05-07` **1,047pp** (PDR +0,524pp). Bảng đầy đủ từng tên:
  `publish_weight_diff.csv`.
* **REBAL ĐANG HIỆU LỰC `2026-08-05`: 0/30 tên đổi weight, max |Δw| = 0,0000pp.**
  Lý do là lịch, không phải vì lỗi vô hại: bước gần nhất của thành viên hiện tại là ACB (ngày quý
  2026-07-22 → ex-date 2026-06-15), cửa sổ lệch `[06-15, 07-22)` **không chứa** 2026-08-05, nên tới
  ngày chốt weight cả hai chế độ đã cùng mang số mới. Một bước rơi vào đầu tháng 8 sẽ đổi weight
  live ngay.

---

## 1. THIẾT KẾ BẢN SỬA

Sửa **NGÀY**, không bao giờ sửa **MỨC**. Toàn bộ nằm trong `custom_basket.py` (khối
`WEIGHT LEG` ở đầu file là bản đặc tả đầy đủ) + knob `BASKET_OSHARES_STEP=exdate|quarter`.

* **Nguồn sự thật cho ex-date**: `tav2_bq.corporate_action`, đọc bằng semantics của
  `corp_action_lib` (`event_status != "not_executed"` = `pricing_events`), codes `ISS` + `AIS`.
  Taxonomy tái dùng `corp_action_lib.PRICE_ADJUSTING_ISS` (không định nghĩa lại):
  * `ISS` có quyền cho cổ đông hiện hữu (cổ tức CP / thưởng / quyền mua) → **`exright_date`**. Đó
    là ngày `Close` bị pha loãng hồi tố, nên số cổ phiếu PHẢI tăng đúng ngày đó, không thì vốn hoá
    bị hụt cả cửa sổ.
  * `AIS` (niêm yết bổ sung, chỗ DUY NHẤT có `shares_total_after`) → **`effective_date`**. Dùng cho
    nhóm không phát sinh quyền (ESOP / riêng lẻ / chuyển đổi TP) — không làm giá đổi, cổ phiếu chỉ
    vào lưu hành khi được niêm yết thêm.
* **Chỉ gắn khi CỠ KHỚP**, không phải "có sự kiện trong cửa sổ là gắn": `exercise_ratio` lệch
  ≤ 2% + 0,2pp so với `new/old − 1` (kể cả tổng nhiều tranche đi ex CÙNG ngày), hoặc
  `AIS.shares_total_after` lệch ≤ 0,1% so với mức mới.
* **Fallback = ngày công bố quý = ĐÚNG hành vi hiện tại.** 49% bước không khớp sự kiện nào (bảng
  vendor có lỗ thật); thiết kế nào bắt buộc phải có sự kiện sẽ làm rỗng rổ. Fallback là chi phí
  **staleness**, không bao giờ là số sai.
* **Hai cổng PIT** (không dùng số tương lai):
  1. Bước **không được** dời về trước/đúng ngày dòng quý LIỀN TRƯỚC — cưỡng chế bằng **biên dưới
     của cửa sổ khớp**, nên sự kiện ngoài phạm vi không bao giờ là ứng viên. Căn cứ: restatement
     chỉ kéo giá trị một dòng quý ĐI VỀ SAU (registry `ticker_financial_oshares.md`), nên một dòng
     vẫn đang hiện số CŨ là bằng chứng tích cực rằng sự kiện chưa xảy ra lúc đó.
  2. Biên **trên** dừng ở dòng quý KẾ TIẾP (và tối đa +45 ngày), cộng cổng đơn điệu: ứng viên rơi
     vào/trước bước đã dời trước đó thì giữ ngày quý. Đây là thứ giữ chuỗi ngày tăng ngặt.
* **Phạm vi**: dời chính cột `OShares` dùng chung, nên `mcap` (cột audit/level + mặt nạ `valid`) và
  `mcapw` (weight) đi cùng nhau và đẳng thức `mcap/mcapw == Close/Price` vẫn đúng. Selection không
  đụng tới; chuỗi RETURN sau JOB C không còn `OShares` ⇒ **thứ duy nhất đổi là weight**.
* **Vì sao KHÔNG dùng `oshares_live.py`/`oshares_pit.py`** (module PIT đã wire): nó trả lời câu hỏi
  KHÁC — **MỨC** tại một ngày — và theo thiết kế **từ chối 33,3%** của universe 108 mã tại
  2014-07-01 (docstring của chính nó cảnh báo). Thay thẳng vào đây là đổi lỗi ngày này lấy một
  availability bias lớn hơn nhiều. Dời ngày của một mức ĐÃ CÓ thì không cần nguồn mức mới.
* **Tái lập được**: bảng `corporate_action` bị UPSERT IN-PLACE, nên `BASKET_CA_SNAPSHOT=<parquet>`
  ghim vintage. Snapshot của phiên này:
  `data/snapshots/corp_action_share_20260927.parquet` — 14.912 dòng / 1.434 mã (TOÀN bảng, không
  lọc mã: union thành viên phụ thuộc lần chạy, thiếu một mã sẽ âm thầm tụt về ngày quý),
  `max_ingested=2026-09-26 15:43:40 UTC`, digest `7409599216578255470`. Dumper:
  `corp_action_share_snapshot.py`.

### Phát hiện phụ — lỗi TIỀM ẨN CŨ trong chính dòng bị thay (ngoài phạm vi ticket)
Dòng gốc `bx.groupby("ticker")["OShares"].ffill().bfill()`: `.ffill()` có group, **`.bfill()` thì
KHÔNG** (nó chạy trên Series kết quả). Với frame sắp theo `(ticker,time)`, NaN ở ĐẦU một mã vẫn
được lấp đúng bằng số của chính mã đó, nên lỗi này lặng. Nó chỉ cắn khi một mã **không có dòng
`OShares` nào**: cả group là NaN và `.bfill()` ngoài group lấp bằng số của **mã kế tiếp theo thứ
tự** — trái đúng câu header "a name with no OShares row at all is excluded exactly as before".
Chân `exdate` dùng `groupby(...).bfill()` (có group) nên không có đường rò này. **Đo thật: 203/203
mã trong rổ đều có dòng `OShares` ⇒ lỗi này hiện KHÔNG cắn**, khác biệt giữa hai chế độ vì thế
thuần là việc dời ngày (A/B một biến). Đã ghim bằng T6 của selfcheck để không mất; chưa sửa dòng
legacy (giữ chân đối chứng byte-identical).

---

## 2. SELFCHECK — `basket_oshares_step_exdate_selfcheck.py`

**37/37 PASS**, và **giống nhau từng dòng dưới 4 biến thể TZ** (`Asia/Ho_Chi_Minh`, `UTC`,
`America/New_York`, `env -u TZ` — md5 của các dòng PASS/FAIL trùng khít):
`selfcheck_TZ_{ICT,UTC,NewYork,unset}.log`.

* **T1** knob đọc tại call-time, mặc định `exdate`, hoa/thường, giá trị lạ → không bật legacy.
* **T2** luật khớp (đơn vị): ratio đơn, tổng tranche cùng ngày, `AIS` khớp mức, `AIS` lệch >0,1%
  **không** khớp, cửa sổ rỗng, và **hai phía của biên dung sai** (0,153 vs 0,150 khớp; 0,158 không).
* **T3** ca thật trên snapshot ghim, **cả hai hướng lệch**: TCB ×2 dời về 2024-06-20 (+32 ngày,
  ratio đúng 2,0); TCB ESOP dòng quý 2024-10-22 dời MUỘN tới 2024-11-30 (−39 ngày, **bỏ
  look-ahead**); FPT 2025-07-22 không khớp cỡ → **giữ ngày quý**; tập MỨC `OShares` y nguyên cho cả
  4 mã; hai cổng PIT.
* **T4** trên frame NGÀY — bất biến quan trọng nhất: tập ngày LỆCH **đúng bằng** hợp các cửa sổ đã
  dời (1.372 = 1.372, không rò một ngày), ngoài đó **byte-identical**; trong cửa sổ tỷ số
  `OShares_exdate/OShares_quarter` **đúng** ratio của bước; mặt nạ `valid` y nguyên; chế độ
  `quarter` byte-identical với dòng code trước khi sửa; **đột biến**: hai chế độ phải thực sự khác
  nhau (bản vá no-op sẽ FAIL).
* **T5** diff publish CSV từng tên (bảng ở mục 0), tổng weight = 1, không tên nào vượt trần 10%.
* **T6** ghim lỗi tiềm ẩn `bfill()` không group + chứng minh hướng sửa.

> Hai lần FAIL đầu tiên là **lỗi của test**, không phải của code, và đáng ghi lại: (a) so tập MỨC
> với `ticker_financial` KHÔNG lọc ngày (thừa 13 năm dòng pre-2013); (b) đưa `bx` sắp theo THỜI
> GIAN vào `apply_oshares` trong khi `build`/`build_pit` luôn đưa frame sắp theo `(ticker,time)` —
> mà kết quả của `bfill()` không group **phụ thuộc thứ tự dòng**. Chính lần FAIL (b) đã lộ ra lỗi
> tiềm ẩn ở mục 1.

## 3. A/B trên R3 — chi tiết ở `AB_R3.md`

| Leg | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ | CSV md5 |
|---|---|---|---|---|---|---|---|---|
| control `quarter` | 24,38% | 1,69 | −18,8% | 1,30 | 757,61B | 19,26% | 29,24% | `3f836927…` = **md5 bản pin R3** |
| `exdate` (mặc định mới) | **24,42%** | 1,69 | −18,8% | 1,30 | **761,11B** | 19,31% | 29,29% | `80fc59f9…` |
| Δ | **+0,04pp** | 0,00 | 0,0pp | 0,00 | +3,50B | +0,05pp | +0,05pp | |

`self-check 0 VND` BAL+LAG ở CẢ HAI chân. Chân control **trùng md5 bản pin R3 hiện hành** ⇒ A/B một
biến, đo được. **+0,04pp là NHIỄU** — đây là bản sửa đúng-sai (bỏ 73 bước look-ahead + 663 bước lệch
ngày), KHÔNG phải cải thiện lợi nhuận. Nghiệm thu H3 FiinProX đo độc lập cũng ra +0,04pp.

## File trong thư mục này
`steps_{pinned_postrestate,live_bqcache}.csv` (đo bước 0, script độc lập
`oshares_step_vs_exdate_measure.py`) · `redating_report_pinned.csv` (báo cáo dời ngày từ CODE SẢN
XUẤT, 203 mã) · `publish_weight_diff.csv` (từng tên đổi weight) · `publish_{quarter,exdate}.log` ·
`selfcheck_TZ_*.log` · `wexd_{ctl_quarter,new_exdate}.log` · `run_leg.sh`, `run_wt_leg.py`.
