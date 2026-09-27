# Layer 1 — DETECT-ONLY: lệch hệ số điều chỉnh corp-action

**Job** `Taylor_20260927_041543` · 2026-09-27 · Taylor (Quant) · branch `feat/adjfactor-layer1-detect`
**CHƯA MERGE, CHƯA CÀI CRON** — chờ user sign-off. User đã duyệt option A (bus `answer/duyet-Layer1-detect-only`,
2026-09-27 11:14 ICT) để *xây*; đưa lên cron hằng ngày + alert Discord thật là bước sau.

Tiền đề: prototype R&D cùng thư mục (`README.md`, job `Taylor_20260927_034929`) đã chứng minh phương
pháp khả thi (46 mã control, sai số ≤0,08%, hệ số 1,01→4,16).

## 1. Ba file, mỗi file một việc

| File | Việc | Không làm |
|---|---|---|
| `bin/adjfactor_drift_detect.py` | So `r_obs = Price/Close` với `r_pred` tự suy từ `corporate_action`; in dòng MÁY ĐỌC | Không ghi bus, không gửi Discord, không sửa số nào (§5b: cổng giữ THUẦN) |
| `bin/adjfactor_drift_alert.sh` | Parse dòng máy đọc → Discord + bus + de-dup nguyên tử | Không tính lại gì; không grep văn xuôi (§28) |
| `bin/adjfactor_drift_daily.sh` | Runner cron: chạy detector, **giữ rc của nó**, rồi gọi alert. rc hợp lệ là **allow-list `0/10/11`** — mọi rc khác (124 timeout, 137 OOM, …) là lỗi hạ tầng | Không dùng pipe trực tiếp (pipe làm MẤT rc=1 ⇒ "BQ chết" bị đọc thành "không có lệch"); không dùng deny-list rc (§8b F2) |

Selfcheck: `bin/adjfactor_drift_detect_selfcheck.py` — **337/337 assertion PASS**, đo dưới `$DNA_PYEXE`
(`/home/trido/thanhdt/wc_venv/bin/python`). Phần shell chạy LẶP dưới 4 môi trường TZ (`unset TZ`,
`TZ=UTC`, `TZ=Pacific/Kiritimati` +14, `TZ=Pacific/Midway` −11) theo §16/§19 — hai TZ lệch CỰC ĐẠI
được thêm ở vòng 2 vì `TZ=America/New_York` cùng ngày lịch với ICT trong phần lớn giờ hành chính,
nên mutation "bỏ hẳn neo `TZ='Asia/Ho_Chi_Minh'`" vẫn PASS (§19: assertion neo-TZ phải phân biệt
được, và selfcheck có một assertion META tự kiểm điều đó thay vì giả định).
Không cần BigQuery — **cưỡng chế bằng `MIKE_ADJFACTOR_NO_BQ=1`**, không phải chỉ bằng lời hứa: mọi
lối ra BQ đi qua `_bq()`/`bq_guard_active()` và raise ngay khi cờ bật. Trước vòng 3 các assertion
"argparse NHẬN giá trị đúng" đi qua cổng rồi vào `run_scan` thật và phát truy vấn THẬT (9,6s, đọc cả
`data/execution_logs/`) — chỉ-đọc nên không vi phạm §5b, nhưng vẫn là một selfcheck phụ thuộc mạng.
Mọi assertion công thức/ngưỡng dùng chuỗi tổng hợp dựng theo CHỮ KÝ ca thật
(FPT/VPB/XHC/GEX/DGC/DXG + ffill toàn thị trường 2026-01-30); phần shell chạy trong ROOT sandbox với
`notify_thread.sh`/`append_event.sh` là stub ⇒ **selfcheck không bao giờ gửi Discord thật hay ghi bus thật**.

Cổng cơ học đã chạy sạch: `shellcheck` 0.11.0 (0 finding, cả 2 file `.sh`), `bin/shellcheck_gate.sh`,
`bin/diagnosis_evidence_gate.py` (rc=0), `bin/tz_anchor_gate.py --scan` (0 vi phạm / 0 file).

## 2. Ranh giới detect-only (yêu cầu #3 + #7 của dispatch)

- Không có consumer nào đọc output của Layer 1. Nó chỉ in ra stdout (→ log cron), ghi 1 event bus
  `finding/adjfactor-drift-scan-<asof>` với `published_any_number: false`, và gửi Discord.
- **Không đụng `report_return_gate.py` / `dividend_adjusted_return.py`.** Detector chỉ *import*
  `dividend_adjusted_return.ACCOUNTS` + `.broker_qty()` để gắn nhãn "mã này đang nắm LIVE" — đọc,
  không sửa, và fail-open (`held=unknown`, vẫn cảnh báo) nếu không tra được. Selfcheck có assertion
  chốt điều này (`dar.detect_adjustments` không được xuất hiện).
- Câu Discord nói thẳng "Layer 1 KHÔNG công bố và KHÔNG sửa số nào — cổng §21 vẫn là lớp chặn báo cáo".

## 3. Ngưỡng — và vì sao không được hạ

| Ngưỡng | Giá trị | Bằng chứng |
|---|---|---|
| `--dev-tol` | **0,3%** | Sàn chính xác của phương pháp ≈0,3%, KHÔNG phải 0,1%: DXG mang dư −0,17% trên đợt thưởng 14% suốt 95 phiên mà vendor vẫn đúng quy ước |
| `--min-run` | **3 phiên liên tiếp** | Bộ lọc này đã loại ffill `Price` **toàn thị trường 2026-01-30** (662/1.252 mã) + 40 đỉnh tỉ số 1 phiên; bỏ nó phóng đại điểm mù ~4× |

`--min-run < 3` bị **argparse TỪ CHỐI cứng** (rc=2) với thông điệp nêu lý do — không phải chỉ ghi
trong docstring rồi hy vọng không ai hạ.

## 4. UNCOMPUTABLE — fail-closed, không bao giờ suy đoán f=1,0 (yêu cầu #4)

**10** mã lý do MÁY ĐỌC, mỗi mã suy TỪ đúng thứ vừa đọc được (§29), kèm `note` văn xuôi có số thật:

`rights_issue_no_subscription_price` · `iss_ratio_unparsable` · `iss_ratio_nonpositive` ·
`div_dps_unparsable` · `div_dps_nonpositive` · `unsupported_event_code` ·
`no_cum_session_in_window` · `price_ffill_suspect` · `cash_exceeds_price` ·
`too_few_sessions_to_compare` *(thêm ở vòng 3 — xem §8b F8)*

Hai luật lan truyền, cả hai có assertion:
1. **Một ex-date không tính được làm `r_pred` SAI cho MỌI phiên trước nó** ⇒ chỉ chấm điểm các phiên
   `d >= max(ex-date uncomputable)`; phần còn lại báo UNCOMPUTABLE. Prototype bỏ CẢ mã khi có unknown;
   ở đây giữ phần còn hợp lệ — **và chính nhờ vậy bắt được XHC** (§5).
2. Mọi UNCOMPUTABLE **luôn** vào stdout (→log) và **luôn** vào payload bus. Chỉ mã đang NẮM LIVE mới
   được nêu tên trên Discord: uncomputable là trạng thái BÌNH THƯỜNG của quyền mua (26/83 mã cohort
   control) — bắn Discord mỗi ngày cho nó là dạy người ta bỏ qua đúng topic cần đọc.

## 5. Kết quả chạy thật (yêu cầu #5) — asof `2026-09-25`

### 5.1 Hai ca đã biết: BẮT ĐƯỢC cả hai, đúng con số prototype

| mã | ex-date | dev | run | nắm LIVE |
|---|---|---:|---:|---|
| **VPB** | 2026-09-24 | **−20,66%** | 78 phiên | **SpaceX + ZaloPay** |
| **FPT** | 2026-09-21 | **−9,09%** | 75 phiên | không |
| GAS | 2026-09-22 | −2,82% | 76 phiên | không |

### 5.2 Cohort tuần nghi vấn (ex-date 09-19..09-25) — 16 DRIFT

Prototype báo 15 BROKEN. Layer 1 báo **16**, thêm **XHC (−10,81%, 11 phiên)**: prototype gạt XHC sang
UNCOMPUTABLE vì có một ex-date 2026-07-22 không tính được, còn Layer 1 chấm từ ex-date đó trở đi.
Đã xác minh thủ công trên `tav2_bq.ticker` — XHC đúng là **cùng chữ ký `SETTLE_RUN=4`**:
`r = Price/Close` bằng 1,0 suốt 07-21..09-14, bằng **1,1236 đúng 4 phiên** 09-15..09-18, rồi 1,0 từ ex-date
09-21. Tức là **true positive mà prototype bỏ sót**, không phải false positive mới.

**Phát hiện mới đáng chú ý: DRI (−8,71%, 76 phiên) ĐANG NẮM LIVE ở CẢ HAI tài khoản.**
Prototype đã liệt DRI trong 15 BROKEN nhưng README của nó chỉ nêu VPB là mã đang nắm ⇒ **có HAI mã
live bị ảnh hưởng, không phải một**.

5 mã đang nắm LIVE rơi vào UNCOMPUTABLE, phải nói rõ vì Layer 1 **không kết luận được gì** cho chúng:
`MBB` (ex 08-11, `rights_issue_no_subscription_price`) · `CTG`/`VCB` (ex 07-23), `VND` (ex 05-29),
`VNM` (ex 06-26) — tất cả `price_ffill_suspect`.

### 5.3 Tuần control (ex-date 09-01..09-18) — KHÔNG báo động giả

Đo lại sau các bản vá vòng 2 (lệnh: `--ex0 2026-09-01 --ex1 2026-09-18 --asof 2026-09-25 --no-holdings`):

| | Layer 1 | prototype `audit_week.py` |
|---|---:|---:|
| cohort | 95 | 95 |
| DRIFT / BROKEN | **11** | **11** |
| AGREE / OK | **46** | 46 |
| UNCOMPUTABLE | 26 | 26 |
| NODATA | **12** | 0 *(bị bỏ im lặng)* |

11 mã DRIFT của tuần control đều là tên mỏng (BAL, DVN, HES, NJC, OIL, PAT, PBP, PLE, PMT, SHC + TTD)
— đúng nền lỗi ~19% trên mã kém thanh khoản mà registry đã ghi, **không liên quan sự cố 09-19..09-25**.
DRIFT/AGREE/UNCOMPUTABLE giờ **khớp TỪNG Ô** với prototype (bản trước lệch 1 mã ở AGREE/UNCOMPUTABLE
do `ex_broken` chọn sai ex-date đại diện, xem §8); khác biệt còn lại DUY NHẤT là 12 mã `NODATA` mà
prototype bỏ im lặng.

⚠️ **`--no-holdings` là phần bắt buộc của phép so sánh này, không phải tuỳ chọn cho gọn.** Không có
cờ đó, universe hằng ngày CỘNG thêm mọi mã đang nắm LIVE có ex-date trong 120 phiên (§6 mục 2) ⇒
cohort 95→**122**, DRIFT 11→**13** vì **VPB (−20,66%) và DRI (−8,71%) của tuần 09-19..09-25 đi vào**.
Hai mã đó là **true positive của tuần nghi vấn**, không phải báo động giả của tuần control — nhưng
trích con số 13 mà không nói rõ nguồn gốc thì đọc ra thành "control bẩn hơn prototype". Đây chính là
lý do so control phải KHOÁ universe về đúng cohort ex-date.

**Hai đính chính với README prototype, đo được từ mã lý do mới:**
1. README §2 nói 26/83 mã cohort control "rơi vào lỗ quyền mua". Sai: **25/26 là `price_ffill_suspect`**,
   chỉ **1** (`RYG`) là quyền mua thật. Nguyên nhân chi phối của UNCOMPUTABLE trên mã mỏng là guard
   ffill `Price`, không phải thiếu giá phát hành.
2. Prototype cohort cũng là 95 mã nhưng lặng lẽ bỏ 12 mã không có dòng giá (`for tk in sorted(series)`
   bỏ qua mã vắng mặt). Layer 1 báo chúng là `NODATA` — không kết luận gì, nhưng không im lặng.

## 6. Universe quét hằng ngày

1. Mọi mã có ex-date **điều chỉnh giá** trong `--ex-days 30` ngày gần nhất (taxonomy do
   `corp_action_lib.is_price_adjusting` chốt; SQL chỉ khoanh vùng cho rẻ).
2. **Cộng** mọi mã đang NẮM LIVE có ex-date trong cửa sổ 120 phiên — một điều chỉnh CŨ có thể hỏng
   MUỘN khi vendor ghi lại lịch sử, và đó đúng là lớp mã duy nhất mà lỗi lại thành tiền thật.

`asof` neo vào `MAX(time)` của `tav2_bq.ticker`, **không** vào đồng hồ host ⇒ chạy sớm chỉ làm cửa sổ
cũ đi một phiên, không bao giờ đọc ra một ngày không tồn tại.

## 7. Exit code — các trạng thái KHÁC nhau, không gộp

| rc | nghĩa | hệ quả |
|---:|---|---|
| 0 | feed **FRESH** + mọi mã tính được và khớp + 0 uncomputable + 0 nodata. Trạng thái DUY NHẤT nghĩa "không có gì" | im lặng |
| 10 | ≥1 DRIFT | Discord + bus |
| 11 | **ĐIỂM MÙ**, KHÔNG phải "sạch": ≥1 UNCOMPUTABLE, hoặc ≥1 NODATA, hoặc feed `corporate_action` không tươi, hoặc universe rỗng | bus (+ Discord nếu có mã đang nắm, hoặc nếu feed không tươi) |
| 1 | **lỗi hạ tầng (BQ)** — KHÔNG phải "sạch" | runner gửi Discord "LƯỢT QUÉT KHÔNG CHẠY ĐƯỢC" kèm LỖI THẬT, **không** gọi alert |
| 2 | sai đối số | như trên |

**De-dup Discord** — ba hạng khoá riêng, mỗi hạng theo đúng định danh của lỗi nó theo dõi:

| marker | khoá | vì sao |
|---|---|---|
| DRIFT | `<mã>\|<ex>` | `<ex>` = ex-date mà hệ số của nó đang THIẾU (ex-date sớm nhất SAU cụm lệch), không phải ex-date sớm nhất trong cửa sổ — xem §8 mục 3. Không tìm được ex-date nào sau cụm lệch ⇒ `unknown_gap@<d1>`, neo vào CỤM LỆCH chứ không vay tên sự kiện khác (§8b F3) |
| UNCOMPUTABLE | `<mã>\|<ex>\|<reason_code>` | đổi mã lý do là đổi việc phải làm ⇒ phải báo lại |
| NODATA | `<mã>\|nodata` | không gắn với ex-date nào |
| FEED không tươi **hoặc THIẾU** (`MISSING`) | **không de-dup** | không thuộc mã nào, và im lặng ở đây là đúng lớp lỗi §14/§29 ⇒ LUÔN lên Discord |
| universe RỖNG (`N_SCANNED=0`) | **không de-dup** | không sinh khoá nào ⇒ nếu de-dup thì im lặng vĩnh viễn |

De-dup **không** theo ngày (detector quét cohort 30 ngày nên de-dup theo ngày sẽ bắn FPT 30 lần);
nhắc lại sau **7 ngày** nếu vẫn còn lệch. Bus ghi **mọi** lượt, không qua de-dup — đó là dấu vết
audit. Discord gửi hỏng ⇒ **không** ghi de-dup (sổ sách không được nói "đã cảnh báo" khi chưa gửi
được gì) ⇒ lượt cron sau thử lại.

## 8. Lỗi arch-review tìm ra và đã vá (vòng 1 + 2 + 3)

Ghi lại vì mỗi lỗi là một ca "im lặng/khẳng định sai" mà bản đầu KHÔNG bắt được, và cả sáu đều có
assertion mới chốt lại (337 assertion hiện tại so với 142 của bản đầu).

1. **Feed nguồn chết = một tuần sạch.** `tav2_bq.corporate_action` là bảng **TRAP** có writer NGOÀI
   repo. Feed đứng im ⇒ 0 ex-date ⇒ mọi mã "khớp" ⇒ `ADJFACTOR_SCAN|…|0|0|0|0|0` và **rc=0, không
   một dòng cảnh báo nào**. Vá: `feed_gate()` bắt buộc, marker `ADJFACTOR_FEED`, status ≠ FRESH là
   hạng cảnh báo riêng luôn lên Discord. Không import `corp_action_daily.gate_freshness` (module đó
   có side effect TOP-LEVEL: `os.environ.pop` + một cổng có thể `raise SystemExit`); chỉ tái dùng
   hằng số `FEED_DEAD_DAYS=5`.
2. **Hợp đồng dòng máy đọc KHÔNG được test.** Mỗi dòng được f-string tại chỗ in, nên selfcheck chỉ
   grep được VĂN BẢN NGUỒN: hoán đổi `dir` với `held` trong dòng DRIFT vẫn **142/142 PASS** và sinh
   nhãn SAI "ĐANG NẮM LIVE: vendor_missing" trên Discord. Vá: dựng dòng ở MỘT chỗ (`marker_*`),
   selfcheck bơm dòng THẬT qua `alert.sh` và so TỪNG TRƯỜNG.
3. **Ex-date nêu tên sai ⇒ khoá de-dup không theo dõi đúng lỗi.** Bản đầu dùng `min(used)` = ex-date
   sớm nhất trong cả cửa sổ 120 phiên. Hai hệ quả đo được: (a) Discord nêu một ex-date KHÔNG phải cái
   bị hỏng; (b) một lỗi MỚI −16,67% ở ex 09-05 tái dùng khoá của ex 07-05 nên **bị chặn tới 7 ngày**,
   còn khi ex cũ trôi khỏi cửa sổ thì lỗi CŨ y nguyên lại báo lại. Vá: `ex_broken` = ex-date sớm nhất
   nằm SAU cụm lệch. (Đây cũng là lý do control giờ khớp từng ô với prototype — §5.3.)
4. **Nhánh UNCOMPUTABLE/NODATA không de-dup.** `N_UNCOMP_HELD > 0` luôn phá de-dup của nhánh DRIFT ⇒
   chạy 3 lượt cùng input thì gửi Discord **cả ba**. Không phải giả định: 5 mã đang nắm đã ở trạng
   thái này với cửa sổ 120 ngày ⇒ cùng một tin mỗi ngày. Vá: khoá riêng cho từng hạng (bảng §7).
5. **`held=unknown` bị gộp vào `none`.** Một mã ĐANG NẮM (VPB, −20,66%) in ra dưới tiêu đề "Mã không
   nắm (chỉ ảnh hưởng nghiên cứu/backtest)" khi `held_map()` fail-open — một KHẲNG ĐỊNH SAI về mức
   phơi nhiễm tiền thật (§29 dạng 2), và còn bị trần `MAX_OTHER_LINES` cắt mất. Vá: `unknown` có mục
   RIÊNG, không bị trần cắt, ghi thẳng "phải coi như CÓ THỂ đang nắm".
6. **Bản ĐÍNH CHÍNH cùng `event_code` bị cộng như tranche thật.** Registry Bẫy (3): `DIV 500` +
   `"Điều chỉnh … 800"` cộng thành `f=1,028603` trong khi đúng là `1,017410` (+1,1%, VƯỢT dung sai)
   ⇒ một cáo buộc `vendor_missing` **SAI** quy cho Winston. Phân biệt được chỉ bằng đọc hiểu tiêu đề
   tiếng Việt ⇒ chưa lint được; vá tối thiểu theo §29: ĐƯA TIÊU ĐỀ vào chứng từ để người xử lý thấy
   ngay, KHÔNG im lặng cộng rồi khẳng định vendor sai. **Đây là hạn chế còn lại đã biết của Layer 1.**

Ngoài ra `NODATA` được cho dòng máy đọc riêng (trước đó chỉ là một con số trong `SCAN` ⇒ một mã đang
NẮM không có dòng giá nào không sinh ra bất cứ thứ gì người đọc thấy; đo thật 12/95 mã trên control),
và universe rỗng trả **rc=11** chứ không phải 0 (cohort 30 ngày rỗng là bất khả về cấu trúc ở VN —
đo thật 95 mã cho cửa sổ 18 ngày).

### 8b. Vòng 3 — 9 finding nữa, 6 mutation SỐNG SÓT 233/233

Vòng 2 vá đúng 6 lỗi vòng 1, nhưng arch-review vòng 3 chạy **23 mutation** và **6 con sống sót** —
tất cả đều ở CÙNG MỘT khe: `marker_*` đã được unit-test và `alert.sh` đã được test bằng dòng viết
tay, nhưng **không có gì chốt `run_scan` THẬT SỰ phát ra marker nào và trả rc nào**. Tức là điểm yếu
cấu trúc của lỗi vòng 1 #2 chỉ dịch lên một tầng. Đó là lý do có hẳn mục `[13] t_emit` chạy `run_scan`
thật với mọi lối ra BQ được thay bằng dữ liệu tổng hợp.

| # | Finding | Hạng | Bản vá |
|---|---|---|---|
| F1 | `held_map()` trả `{}` (dict RỖNG, `is not None`) khi `broker_qty()` không đọc được file — nó **không raise** — ⇒ mọi mã gán `none` ⇒ **VPB −20,66% ĐANG NẮM in dưới tiêu đề "Mã không nắm"**, y nguyên lỗi vòng 1 #5 qua đường khác. Kèm theo `if held:` falsy ⇒ mất luôn phần universe cộng thêm mã đang nắm | **HIGH** | `snap_dates` rỗng ⇒ `None`; thêm freshness `HELD_MAX_STALE_DAYS=4` so với `asof` (§14) |
| F2 | Runner chỉ coi `rc=1/2` là thất bại ⇒ **rc=124 (timeout), rc=137 (OOM/SIGKILL) trả exit 0, không gửi gì**: detector bị giết không phân biệt được với tuần sạch. Và `rc=11` universe rỗng thoát TRƯỚC bước ghi bus ⇒ §7 ghi "rc=11 → bus" là SAI cho ca đó | **HIGH** | `case` **allow-list** `0\|10\|11`, mọi rc khác = hạ tầng; `EMPTY_UNIVERSE` lên cả bus và Discord |
| F3 | `ex_broken` fallback `min(used)` = đúng biểu thức bug vòng 1. Với `our_table_missing`, ex-date còn thiếu **theo định nghĩa** không nằm trong `used` ⇒ `ex > d1` luôn rỗng ⇒ nêu tên ex-date vendor làm ĐÚNG, rồi khoá đổi khi ex-date đó trôi khỏi cửa sổ | MED-HIGH | khoá neo vào CỤM LỆCH: `unknown_gap@<d1>`, không vay tên sự kiện khác |
| F4 | Mitigation của lỗi vòng 1 #6 chỉ vào `notes` → **stdout/log**, còn CÁO BUỘC đi lên **Discord** ⇒ ca `DIV 500 + "Điều chỉnh 800"` vẫn gửi "vendor THIẾU hệ số" + dòng việc cho Winston, bằng chứng phản bác ở kênh khác | MED | bit cơ học `corr` vào **dòng máy đọc**; `alert.sh` gắn cờ "NGHI BẢN ĐÍNH CHÍNH" và **loại khỏi TODO của Winston** |
| F5 | **THIẾU** dòng `ADJFACTOR_FEED` ⇒ `FEED_STATUS=""` ⇒ coi như FRESH ⇒ im lặng hoàn toàn. §28 dạng 3 (suy "không có vấn đề" từ sự VẮNG MẶT của kênh) — trên đúng kênh duy nhất tồn tại để chống feed chết | MED | `FEED_STATUS="MISSING"` fail-closed, luôn lên Discord |
| F6 | Ngưỡng chỉ được canh chiều LÀM Ồ. Chiều LÀM IM mở: `--lookback-days 2` và `--min-run 9999` biến **16 lệch thật (gồm VPB) thành "50 khớp"**, rc=11 | MED | `MIN_RUN_MAX=120`, `LOOKBACK_MIN=20`, `--ex-days >= 1` |
| F7 | `--no-holdings` bị gộp vào `unknown` ⇒ trên đúng lệnh control tài liệu hoá, Discord khẳng định "`broker_qty()` lỗi ⇒ kiểm `dnse_raw_*.jsonl`" cho cả 49 mã **trong khi `broker_qty()` chưa hề được gọi** (§29 dạng 2) | LOW-MED | nhãn thứ ba `skipped`, tách khỏi `unknown` ở cả 3 vòng lặp của `alert.sh` |
| F8 | `evaluated == []` trả **AGREE** với `n_eval=0` ⇒ "khớp" nghĩa là "không có đủ dữ liệu để bất đồng", vẫn được cộng vào con số "N khớp". Kèm: lý do `UNREADABLE` đa dòng bị cắt ở newline đầu ⇒ Discord in ra "bq failed:" mất nguyên nhân | LOW | `MIN_EVAL_SESSIONS=3` ⇒ UNCOMPUTABLE `too_few_sessions_to_compare`; `marker_feed` làm phẳng `reason` |
| F9 | de-dup đọc-sửa-ghi không có lock: 2 lượt chồng nhau đều gửi Discord, khoá của lượt trước bị ghi đè | LOW | `flock -w 60` trên FD 9 quanh toàn bộ read-modify-write |

**Đo lại sau vá, không đổi một số nào:** suspect week 16 DRIFT / 13 UNCOMP / 23 AGREE / 2 NODATA,
feed FRESH, rc=10, VPB+DRI đúng nhãn `SpaceX,ZaloPay`, 0 dòng `corr=1`. Control `--no-holdings`
95 / 11 / 26 / 46 / 12, mọi nhãn là `skipped`, và **`MIN_EVAL_SESSIONS` không làm mất một AGREE thật
nào** (`too_few_sessions_to_compare` = 0 ca) — khớp đúng phép đo của arch-review (0/69 mã AGREE có
`n_eval < 3`, nhỏ nhất 43), tức cổng F8 là lưới cho ca cấu trúc, không phải thứ đang cắt dữ liệu thật.

**Hạn chế còn lại đã biết (KHÔNG giải được bằng code):** phân biệt tranche thật với bản ĐÍNH CHÍNH
cùng `event_code` cần đọc hiểu `event_title_vi` tiếng Việt. `corr=1` chỉ NÊU NGHI VẤN và chặn việc
quy cho vendor — nó không nói được bên nào đúng.

### 8c. Vòng 4 — 2 must-fix + 5 should-fix (5/6 mutation vòng 3 đã thành KILL)

Vòng 3 xác nhận 5 trong 6 mutation sống sót đã bị giết (M4/M7/M18/M19 bởi mục `[13] t_emit`, M8 bởi
assertion rc); M10 gốc thành vestigial nên arch-review mutate CƠ CHẾ MỚI thay vì mục tiêu cũ —
**M10a** (tắt `corr_ex.add`) và **M10b** (tắt định tuyến corr trong `alert.sh`) đều KILLED.

| # | Finding | Hạng | Bản vá |
|---|---|---|---|
| R3-1 | **F1 chưa hết: hỏng MỘT tài khoản vẫn không fail-closed.** `if not qmap: continue` bỏ qua tài khoản hỏng lặng lẽ, `snap_dates` còn của tài khoản sống ⇒ cả hai cổng vòng 3 PASS. Đo trên `dar` **THẬT** với dữ liệu broker hôm nay: ZaloPay hỏng + SpaceX khoẻ ⇒ dict(28) không cảnh báo, `CSV`/`DGC` (chỉ nắm ở ZaloPay) gán `none` ⇒ đúng lại failure mode F1 trên vị thế LIVE thật | **MED-HIGH** | thiếu dù MỘT tài khoản ⇒ `None`, thông điệp nêu rõ "một tài khoản còn sống KHÔNG đủ" |
| R3-4 | **Lock F9 đảo chiều fail-open và tự bịa nguyên nhân.** `state/` không ghi được ⇒ thông điệp khẳng định "một lượt khác đang chạy" + "sau 60s" khi nó chờ 0s và không có lượt nào khác; bằng chứng thật (`Permission denied`) bash in ra rồi bị vứt — §29 dạng 2 trong chính code vá §29. Và lock lấy TRƯỚC cả bus lẫn Discord ⇒ lỗi môi trường thành im lặng HOÀN TOÀN, trái header của chính file | **MED** | tách "không MỞ được lock" (chạy TIẾP không lock) khỏi "lock đang bị giữ" (ghi bus rồi bỏ qua Discord, rc=11) |
| R3-2 | `unknown_gap@<d1>` **re-key mỗi ngày** khi cụm lệch chạm rìa phải — ảnh gương của F3 (khoá quá ổn định → quá bất ổn). Đo: cùng lệch, hai asof liên tiếp cho `@2026-09-09` rồi `@2026-09-10` ⇒ báo lại hằng ngày | LOW-MED | neo vào `dev` làm tròn 4 chữ số (bất biến theo cửa sổ): `unknown_gap@dev-0.1667` |
| R3-3 | cùng lớp: `too_few_sessions_to_compare` dùng `d_min_of(series)` làm ex de-dup ⇒ trôi theo rìa cửa sổ nạp | LOW | hằng `no_ex_in_window`; `d_min_of()` bị xoá |
| R3-7 | `read ... held corr` để biến CUỐI hút phần còn lại ⇒ một trường **thứ 13** thêm về sau làm `corr` thành `"1\|extra"` ⇒ **mất nhánh cờ đính chính**, dòng quay về "vendor THIẾU hệ số" + TODO Winston = tái lập F4 im lặng | LOW | biến hứng `_rest` ở cả 3 vòng lặp; assertion cho cả dòng 13 trường và dòng 11 trường (bản cũ) |
| R3-6 | **F6 còn hở chiều `--dev-tol`**: trần 0,5 cao hơn sàn bằng chứng 0,3% hai bậc độ lớn; `--dev-tol 0.4` được nhận và biến lệch lớp VPB −20,66% thành AGREE (đo: 0,003/0,05 → DRIFT; 0,4/0,499 → AGREE) | LOW | `DEV_TOL_MAX = 0.05` |
| R3-5 | selfcheck **thật sự chạm BigQuery** ở assertion cuối của F6 (9,6s, `feed_freshness` + `price_rows` + `events` thật, đọc cả `data/execution_logs/` → `# vi the LIVE: 30 ma`). Chỉ-đọc nên KHÔNG vi phạm §5b, nhưng §1 hứa "không cần BigQuery" | LOW | `MIKE_ADJFACTOR_NO_BQ=1` + `_bq()`/`bq_guard_active()` chặn MỌI lối ra BQ; có assertion cho chính cổng đó |

**Hai lỗi phát sinh trong lúc vá vòng 4, cả hai tự bắt được:**
1. `_LOCK_ERR="$(exec 9>"$STATE.lock" 2>&1)"` **không bắt được lỗi**: redirect xử lý trái→phải nên
   `9>file` thất bại khi stderr VẪN là stderr ngoài ⇒ biến rỗng và thông điệp phải in "khong ro" —
   tức lại đúng §29 dạng 1 trong bản vá cho §29 dạng 2. Đo thật: dạng `9>file 2>&1` cho
   `captured=[]`, dạng `2>&1` TRƯỚC cho đúng dòng `Permission denied`. Đã đổi sang dạng sau.
2. Assertion R3-4 ban đầu **vô nghĩa**: `.lock` đã tồn tại từ các lượt trước, mà mở file ĐÃ CÓ để ghi
   chỉ cần quyền trên FILE (0600, ta sở hữu) chứ không cần quyền trên thư mục ⇒ ca không tái hiện.
   Phải XOÁ `.lock` trước khi `chmod 500`.

Kèm theo: ghi state thất bại từng bung **traceback trần** (`PermissionError` từ `mkstemp`) — giờ nói
rõ hệ quả thật ("Discord ĐÃ gửi, lượt sau sẽ GỬI LẠI các khoá này") kèm lỗi thật, §29.

**Đo lại real-data lần thứ ba, vẫn KHÔNG đổi một số nào:** suspect 16/13/23/2 rc=10, VPB+DRI đúng
nhãn, 0 `corr=1`, **0 `unknown_gap`**; control `--no-holdings` 95/11/26/46/12, 0 `too_few`.

## 9. Còn phải làm trước khi lên production (KHÔNG tự làm)

1. **User sign-off** merge branch `feat/adjfactor-layer1-detect`.
2. **§11**: ghi `kb/cron_registry.md` TRƯỚC khi thêm dòng crontab. Dòng đề xuất (chưa cài):
   `10 0 * * 2-6  cd .../mike && bin/adjfactor_drift_daily.sh >> logs/adjfactor_drift_YYYYMM.log 2>&1`
   — 00:10 ICT T3-T7 = sau `sync_bq_cache_daily.sh` (23:45 ICT).
3. **Việc của Winston (data-ops), không phải Layer 1**: yêu cầu vendor backfill 16 mã tuần 09-19..09-25
   (ưu tiên **VPB + DRI** vì đang nắm LIVE), và kiểm `price_ffill_suspect` trên 4 mã lớn đang nắm
   (CTG, VCB, VND, VNM).
4. **Layer 2 (sửa/công bố số) vẫn chưa được phép** — §21 + quy chuẩn backtest mục 5 đòi
   **quant-skeptic CONFIRMED** trước khi bất kỳ consumer nào đọc một `Close` tự tính.
