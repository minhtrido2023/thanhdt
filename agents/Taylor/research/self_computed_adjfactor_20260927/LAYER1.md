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
| `bin/adjfactor_drift_daily.sh` | Runner cron: chạy detector, **giữ rc của nó**, rồi gọi alert | Không dùng pipe trực tiếp (pipe làm MẤT rc=1 ⇒ "BQ chết" bị đọc thành "không có lệch") |

Selfcheck: `bin/adjfactor_drift_detect_selfcheck.py` — **233/233 assertion PASS**, đo dưới `$DNA_PYEXE`
(`/home/trido/thanhdt/wc_venv/bin/python`). Phần shell chạy LẶP dưới 4 môi trường TZ (`unset TZ`,
`TZ=UTC`, `TZ=Pacific/Kiritimati` +14, `TZ=Pacific/Midway` −11) theo §16/§19 — hai TZ lệch CỰC ĐẠI
được thêm ở vòng 2 vì `TZ=America/New_York` cùng ngày lịch với ICT trong phần lớn giờ hành chính,
nên mutation "bỏ hẳn neo `TZ='Asia/Ho_Chi_Minh'`" vẫn PASS (§19: assertion neo-TZ phải phân biệt
được, và selfcheck có một assertion META tự kiểm điều đó thay vì giả định).
Không cần BigQuery: mọi assertion công thức/ngưỡng dùng chuỗi tổng hợp dựng theo CHỮ KÝ ca thật
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

9 mã lý do MÁY ĐỌC, mỗi mã suy TỪ đúng thứ vừa đọc được (§29), kèm `note` văn xuôi có số thật:

`rights_issue_no_subscription_price` · `iss_ratio_unparsable` · `iss_ratio_nonpositive` ·
`div_dps_unparsable` · `div_dps_nonpositive` · `unsupported_event_code` ·
`no_cum_session_in_window` · `price_ffill_suspect` · `cash_exceeds_price`

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
| DRIFT | `<mã>\|<ex>` | `<ex>` = ex-date mà hệ số của nó đang THIẾU (ex-date sớm nhất SAU cụm lệch), không phải ex-date sớm nhất trong cửa sổ — xem §8 mục 3 |
| UNCOMPUTABLE | `<mã>\|<ex>\|<reason_code>` | đổi mã lý do là đổi việc phải làm ⇒ phải báo lại |
| NODATA | `<mã>\|nodata` | không gắn với ex-date nào |
| FEED không tươi | **không de-dup** | không thuộc mã nào, và im lặng ở đây là đúng lớp lỗi §14/§29 ⇒ LUÔN lên Discord |

De-dup **không** theo ngày (detector quét cohort 30 ngày nên de-dup theo ngày sẽ bắn FPT 30 lần);
nhắc lại sau **7 ngày** nếu vẫn còn lệch. Bus ghi **mọi** lượt, không qua de-dup — đó là dấu vết
audit. Discord gửi hỏng ⇒ **không** ghi de-dup (sổ sách không được nói "đã cảnh báo" khi chưa gửi
được gì) ⇒ lượt cron sau thử lại.

## 8. Sáu lỗi arch-review tìm ra và đã vá (vòng 1 + 2)

Ghi lại vì mỗi lỗi là một ca "im lặng/khẳng định sai" mà bản đầu KHÔNG bắt được, và cả sáu đều có
assertion mới chốt lại (233 assertion hiện tại so với 142 của bản đầu).

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
