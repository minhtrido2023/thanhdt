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

Selfcheck: `bin/adjfactor_drift_detect_selfcheck.py` — **142 assertion PASS** (68 Python + 74 shell),
phần shell chạy LẶP dưới 3 môi trường TZ (`unset TZ`, `TZ=UTC`, `TZ=America/New_York`) theo §16/§19.
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

| | Layer 1 | prototype `audit_week.py` |
|---|---:|---:|
| cohort | 95 | 95 |
| DRIFT / BROKEN | **11** | **11** |
| AGREE / OK | **45** | 46 |
| UNCOMPUTABLE | 27 | 26 |
| NODATA | **12** | 0 *(bị bỏ im lặng)* |

11 mã DRIFT của tuần control đều là tên mỏng (BAL, DVN, HES, NJC, OIL, PAT, PBP, PLE, PMT, SHC + TTD)
— đúng nền lỗi ~19% trên mã kém thanh khoản mà registry đã ghi, **không liên quan sự cố 09-19..09-25**.
45 vs 46 và 27 vs 26: chênh đúng 1 mã (TTD/TIP) do cửa sổ đánh giá khác nhau (Layer 1 dùng
`--lookback-days 120` từ `asof`; prototype dùng `--since 2026-06-01` và chỉ chấm phiên TRƯỚC ex-date).

**Hai đính chính với README prototype, đo được từ mã lý do mới:**
1. README §2 nói 26/83 mã cohort control "rơi vào lỗ quyền mua". Sai: **25/27 là `price_ffill_suspect`**,
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

## 7. Exit code — ba trạng thái KHÁC nhau, không gộp

| rc | nghĩa | hệ quả |
|---:|---|---|
| 0 | mọi mã tính được và khớp, 0 uncomputable | im lặng |
| 10 | ≥1 DRIFT | Discord + bus |
| 11 | 0 DRIFT, ≥1 UNCOMPUTABLE | bus (+ Discord chỉ nếu có mã đang nắm) |
| 1 | **lỗi hạ tầng (BQ)** — KHÔNG phải "sạch" | runner gửi Discord "LƯỢT QUÉT KHÔNG CHẠY ĐƯỢC" kèm LỖI THẬT, **không** gọi alert |
| 2 | sai đối số | như trên |

De-dup Discord theo khoá `<mã>|<ex-date>` (không theo ngày — detector quét cohort 30 ngày nên de-dup
theo ngày sẽ bắn FPT 30 lần), nhắc lại sau **7 ngày** nếu vẫn còn lệch. Bus ghi **mọi** lượt có lệch,
không qua de-dup — đó là dấu vết audit. Discord gửi hỏng ⇒ **không** ghi de-dup (sổ sách không được nói
"đã cảnh báo" khi chưa gửi được gì) ⇒ lượt cron sau thử lại.

## 8. Còn phải làm trước khi lên production (KHÔNG tự làm)

1. **User sign-off** merge branch `feat/adjfactor-layer1-detect`.
2. **§11**: ghi `kb/cron_registry.md` TRƯỚC khi thêm dòng crontab. Dòng đề xuất (chưa cài):
   `10 0 * * 2-6  cd .../mike && bin/adjfactor_drift_daily.sh >> logs/adjfactor_drift_YYYYMM.log 2>&1`
   — 00:10 ICT T3-T7 = sau `sync_bq_cache_daily.sh` (23:45 ICT).
3. **Việc của Winston (data-ops), không phải Layer 1**: yêu cầu vendor backfill 16 mã tuần 09-19..09-25
   (ưu tiên **VPB + DRI** vì đang nắm LIVE), và kiểm `price_ffill_suspect` trên 4 mã lớn đang nắm
   (CTG, VCB, VND, VNM).
4. **Layer 2 (sửa/công bố số) vẫn chưa được phép** — §21 + quy chuẩn backtest mục 5 đòi
   **quant-skeptic CONFIRMED** trước khi bất kỳ consumer nào đọc một `Close` tự tính.
