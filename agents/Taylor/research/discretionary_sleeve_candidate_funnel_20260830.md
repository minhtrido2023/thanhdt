# Discretionary sleeve candidate funnel — 2026-08-30

Job `discretionary-sleeve-candidate-funnel-20260830` (Taylor_20260830_054255), user duyệt 12:42 ICT:
gộp Việc 1 (wire marginability) + Việc 2 (lắp phễu candidate hệ thống) cho sleeve margin đơn mã
discretionary (TV1/DGC-style, per-name 5%/sleeve 10% NAV, LIVE commit 022c48e7).

## Việc 1 — `bin/marginability_check.py`

Probe thật `DNSEClient.loan_packages(account, symbol=X)` (GET /accounts/{acc}/loan-packages, đọc
thuần không cần OTP). Field đáng tin là `initialRate` (không phải `type` — `type` là thuộc tính
ACCOUNT, cả 2 gói tiền mặt+margin trên account margin đều trả `type="M"`).
`marginable(ticker) := any(pkg.initialRate < 1.0 for pkg in packages)`.

**Verify khớp 3 ground-truth case đã biết** (probe LIVE 2026-08-30, account SpaceX 0002023347):
- TV1 (UPCOM): 1 gói, không có `initialRate` → `marginable=False`. Khớp.
- DGC (HOSE hạn chế): gói "RocketX" id=1840 nhưng `initialRate=1.0` → `marginable=False`. Khớp.
- MBB (mainboard bình thường): gói 1840 `initialRate=0.5` → `marginable=True`. Khớp.

Cache atomic-write `data/marginability_cache.json`, refresh 7 ngày, per-account (đồng bộ
`ONLY_ACCOUNT` của `discretionary_margin_gate.py` — SpaceX, ZaloPay cash-only vô nghĩa với
endpoint này). Lỗi/timeout DNSE → `marginable=None` (không đoán, §29), không cache lỗi.

## Việc 2 — `bin/discretionary_candidate_funnel.py`

Lắp ráp 4 tầng đã có, không viết lại logic:
1. **Universe fear** = PB<1,0 & washout(400d, đỉnh cục bộ)<=-30% & dd52(252-phiên, per-ticker)<=-20%,
   từ `tav2_bq.ticker` JOIN `tav2_mike.universe_pit` (PIT) — đúng định nghĩa
   `discretionary_sleeve_correlation_risk_20260830.md` bước 1.
2. **Quality floor** = `data/rating_8l.csv`, golden floor `ROE_Min3Y>=0 & CF_OA_3Y>0`, rating<=3.
3. **Negative screens** = `data/insider_flags.json` (insider net-sell) + cột `redflag` có sẵn trong
   rating_8l.csv.
4. **Marginability + %ADV** = Việc 1 (chỉ probe shortlist đã qua bước 1-3) + `adv_3m()`/`ADV_CAP_PCT`
   tái dùng nguyên từ `discretionary_margin_gate.py`.

`FULLY_QUALIFIED` = qua đủ cả 4 tầng. Output là bảng xếp hạng RECON, KHÔNG auto-arm.

Wired vào `bin/fearbuy_weekly_scan.sh` (chỉ `--mode weekly`, timeout 240s, fail-soft cùng khuôn
`UNIVERSE_BLOCK` — lỗi thì nói thẳng trong prompt, không im lặng bỏ qua) + thêm việc 7 cho LLM: rà
`FULLY_QUALIFIED` chưa có trong backstop.md → WebSearch nguyên nhân washout → áp lại
QUALIFY/NON/AMBIGUOUS filter của việc 3.

## Selfcheck chạy thật (2026-08-30, 1 ngày dữ liệu thật, universe_pit 355 mã)

`python3 mike/bin/discretionary_candidate_funnel.py --json .../funnel_run_20260830.json --csv
.../funnel_run_20260830.csv` — không lỗi. Fear cohort 113/355 mã. 14 mã `FULLY_QUALIFIED`:
VSC, YEG, HDG, DTD, VGS, ITC, DRC, NTL, LCG, HT1, SHB, HPX, SKG, TPB (đủ dải liquidity, từ 0,45tỷ
đến 628tỷ ADV/3M — funnel không tự lọc theo ADV, chỉ annotate, đúng như thiết kế "RECON không phải
quyết định").

**TV1/DGC KHÔNG xuất hiện trong output — đã trace ra bằng chứng, không phải bug:**
- Cả 2 vẫn `in_universe=True` trong `universe_pit` hiện tại, dữ liệu panel đầy đủ (281 phiên,
  không có gap).
- Washout/dd52 của cả 2 vẫn sâu (DGC washout=-58,4%/dd52=-55,1%; TV1 washout=-48,0%/dd52=-48,0%)
  — vẫn "fear" theo nghĩa giá.
- Nhưng **PB hiện tại của cả 2 đã > 1,0** (DGC PB=1,005; TV1 PB=1,084) → fail điều kiện `PB<1,0`
  của cohort → không lọt vào `in_fear_cohort`.
- Đây **KHÔNG PHẢI lỗi funnel** — cohort definition được lệnh dispatch yêu cầu tái dùng nguyên văn
  từ `discretionary_sleeve_correlation_risk_20260830.md`, và tài liệu đó **tự ghi rõ ở dòng 28**:
  "cohort 'fear-buy profile' (không dùng lại đúng TV1/DGC vì 2 mã này không cùng tồn tại lịch sử
  ...)" — cohort PB<1 là proxy ĐẠI DIỆN cho correlation-risk study, **chưa từng được thiết kế để
  tái tạo đúng TV1/DGC**. Funnel hôm nay dùng đúng định nghĩa đó nên thừa hưởng luôn giới hạn đó.

**Hàm ý cần user/Mike biết:** nếu mục tiêu là "phễu bắt được ca như TV1/DGC trong tương lai", cohort
PB<1 hiện tại **sẽ bỏ sót** các case có giá washout sâu nhưng PB vẫn quanh/trên 1,0 (đúng như TV1/DGC
hôm nay). Đây là quyết định thiết kế cần user xác nhận, không tự nới ngưỡng — 2 lựa chọn:
(a) giữ nguyên PB<1 (đúng chỉ đạo dispatch, chấp nhận bỏ sót case như TV1/DGC hiện tại), hoặc
(b) nới/bỏ điều kiện PB cho riêng phễu này (tách khỏi cohort correlation-risk gốc, cần review lại
tương quan rủi ro nếu nới).

## Việc CHƯA làm / mở

- Đã KHÔNG tự nới ngưỡng PB — giữ nguyên theo chỉ đạo "dùng lại định nghĩa, không tự chế lại".
- Cadence: giữ nguyên lịch Friday 08:10 ICT hiện có của `fearbuy_weekly_scan.sh` (hợp lý — phễu chạy
  1 BQ query + N probe DNSE margin, không cần tần suất dày hơn tuần).
- Chưa review 14 case `FULLY_QUALIFIED` qua fundamental-skeptic/due-diligence — đây là RECON, việc
  đó thuộc bước tiếp theo nếu Mike/user chọn theo đuổi case cụ thể.
