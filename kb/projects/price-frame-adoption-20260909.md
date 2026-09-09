# P1 — Giá: 4 consumer đọc `marketPrice` trần (2026-09-09)

**Trạng thái:** thiết kế v2 sau arch-review **NEEDS_CHANGES** (confidence high). Chưa code gì.
Bản v1 của tôi bị bác gần hết — giữ lại phần bị bác ở §"Sai ở đâu" để không ai đi lại đường đó.

## Kết luận sau phản biện

Vấn đề THẬT tồn tại, nhưng **không nằm ở chỗ tôi tưởng** và **không sửa bằng cách tôi đề xuất**.

- Lỗi thật, đáng sửa: **`report_return_gate.py:123-137`** — `agg.setdefault(sym, [0,0,mp])` khiến
  **giá của lô ĐẦU TIÊN trong mảng thắng im lặng**, rồi giá đó được áp cho **tổng** khối lượng
  (`:157-161`, `:462-463`). Đây là cổng gác số tỉ suất **gửi nhà đầu tư**. Comment ở `:123`
  ("marketPrice giống nhau mọi lô cùng mã") khẳng định điều đã bị bác bỏ, và selfcheck
  (`:663-677`) dựng fixture 2 lô **CÙNG** giá `12000.0` nên **không bao giờ chạm đường lệch** —
  test đang assert chính cái bug.
- Lời giải đúng cho 3 file còn lại: **BỎ HẲN `marketPrice`**, thay bằng hub giá đã có
  (`dnse_close_prices()` — cả 3 đều chạy `asof == today`). Xoá một nguồn giá, không thêm cổng
  canh nguồn giá thứ tư.

## Sai ở đâu trong bản v1 (ghi lại để không lặp)

| Tôi khẳng định | Thực tế (arch-review kiểm lại) |
|---|---|
| `resolve_reference` là hub luôn bật của đường đặt lệnh, gọi ở `bot_execute.py:120` | `:120` nằm trong `_run_gdkhq_shadow()` — nhánh **read-only**, không phải đường lệnh. Đường thật là `:736` → `exdate_gate.py:82`. Và **G4 chỉ chạy ngày ex-date**: `exdate_gate.py:105-109` return sớm `NO_EVENT` ⇒ phiên thường không hề gọi `check_same_frame` |
| 4 file đọc `marketPrice` trần | **5**, thiếu `daily_nav_snapshot.py` — mà file đó **đã có sẵn đúng cổng tôi định xây** (`:387-415`, rc=4 + `nav_sync_retry.sh`, chính tôi làm đêm qua). Tôi không đối chiếu với baseline của chính mình |
| `park_holdings` đọc `positions[].marketPrice` | Nó gọi `b.get_positions()` (`:228`) — tức giá **đã gộp**, không phải raw |
| 9 ca lệch thật | Chỉ **5 bản đọc** (1 record bị ghi log 2 lần), **toàn bộ ZaloPay**, toàn bộ lúc 19:07/19:10 |
| Nguyên nhân: DNSE điều chỉnh theo GÓI VAY, không nguyên tử | **Replica-lag đọc-sau-ghi**: BID 08-14 cả 2 gói đã được reprice 38850→35800 lúc `12:09:00Z`/`12:09:09Z`, nhưng bản đọc `12:10:23Z` (**sau cả hai**) vẫn trả dòng cũ của gói 1258, kèm `openQuantity` cũ 300 thay vì 320. Suốt 08-10→08-29 hai gói khớp nhau ở mọi quan sát khác |

⚠️ Phát biểu nguyên nhân sai đó đang **hardcode trong code**: `price_frame.py:355`,
`brokers.py:609-613`. Vi phạm §29 (khẳng định nguyên nhân mà code chưa đọc bằng chứng nào).

## Phản bác quyết định (killer objection)

**Không consumer nào trong 4 file từng ăn phải bản đọc lệch.** Cửa sổ lệch là batch reprice EOD
của DNSE, `modifiedDate` dồn 11h-12h UTC (18h-19h ICT), đuôi batch kết thúc ~19:0x:

| Cửa sổ | số bản đọc | lệch |
|---|---|---|
| 19:07 + 19:10 (eod_trading_report, plan DollarBill) | 96 | **5** |
| 19:30 `park_trim_daily.sh` | 26 | **0** |
| 19:40 `jit_unpark_daily.sh` | 27 | **0** |
| bản ghi CUỐI ngày (thứ `report_return_gate` thật sự đọc) | — | **0** |

Cả 2 ngày có lệch, input thật của `report_return_gate` đều sạch (08-14 `21:52:31` BID
`[35800,35800]`; 08-28 `23:30:09` MBB `[21050,21050]`). Tôi đã trình 9 ca như bằng chứng phơi
nhiễm của 4 file — **chúng không phải**. Và cửa sổ 19:0x nơi lệch thật sự xảy ra thì
`daily_nav_snapshot.py:387-415` đã canh sẵn.

## Việc còn lại (phạm vi đã co lại)

1. `report_return_gate.py:123-137` — sửa như **bug đúng-sai**, không phải thêm gate: thay
   `setdefault`-lô-đầu-thắng bằng `bq_close_prices(tickers, as_of_date)`
   (`verify_account_snapshot.py:377` — chạy được trên `asof` LỊCH SỬ, `dnse_close_prices()` thì
   không). Xoá comment sai `:123`.
2. Thêm **fixture LỆCH** vào selfcheck `:663-677` bằng đúng 2 dòng ZaloPay 08-14 (BID
   107cp@35800 gói 1826 / 300cp@38850 gói 1258), assert hành vi mới. Bắt buộc trước khi
   CONFIRMED.
3. `compute_park_trim` / `compute_jit_unpark` / `park_holdings` — thay `marketPrice` bằng
   `dnse_close_prices()`. Lưu ý `compute_park_trim` đã sẵn **2** đường giá (`live_price_fn`
   `:240-252`, fallback `:440-443`); mục tiêu là **giảm** còn 1, không phải thêm.
4. Sửa phát biểu nguyên nhân ở `price_frame.py:355` + `brokers.py:609-613` (§29).

**Câu hỏi đã ĐÓNG — không mở lại:**
- **KHÔNG sửa `DNSEBroker.get_positions()`.** Việc cộng gộp là bản vá có chủ đích (commit
  `36846b86`): sửa NAV ZaloPay thiếu **24,01tr**, và `park_holdings.py:225-227` cố ý tái dùng
  để không tái lập `BLOCKED_RECONCILE` giả cho L1.
- **Chặn per-ticker KHÔNG cô lập được bán kính nổ**: `park_mv` nuôi `pool`/`target_value`/`delta`
  (`compute_park_trim.py:354-356`) và renormalize `w_sum` (`:462`) ⇒ bỏ giá 1 mã làm cả account
  trông under-parked, ém trim **mọi mã khác**. Nếu còn giữ G4 ở đâu đó thì phải tách "giá ĐỊNH
  GIÁ" khỏi "giá ĐỊNH CỠ LỆNH" và nói rõ một lần từ chối ảnh hưởng cái nào.
- **Dung sai G4**: hiện so **bằng nhau tuyệt đối** (`price_frame.py:350`). MBB 08-28
  `[21000,21050]` đúng **1 tick HOSE** ⇒ cho dung sai 1 tick sẽ nuốt 4/9 ca; giữ tuyệt đối thì
  kêu vì nhiễu 1 tick. Không có lời giải sạch — ghi lại đánh đổi, không tự chọn.

**Nỗi lo đã bị BÁC BỎ (không cần xử):** false-positive "lô mới mua chưa kịp có giá" — đo trên
2.604 bản đọc: **0 ca**.


## Kết luận điều tra: producer vốn ĐÃ ĐÚNG, báo cáo bỏ qua nó (2026-09-09)

Câu hỏi "sửa hoàn toàn cho kỳ tới" dẫn tới mắt còn thiếu của chuỗi: **không phải producer sai.**

    verified_snapshot_ZaloPay_2026-08-28.json → SCL mtm_price 27.800, pnl_pct 17,8465%

Hub canonical (`verify_account_snapshot`, §6) ghi ĐÚNG con số ngay từ đầu. Báo cáo công bố
**+17,00%** ⇒ nó **không dựng số từ snapshot canonical** mà lấy `marketPrice` (27.600) từ chỗ
khác. Và cổng cũ **xác nhận** con số sai đó vì cổng dùng **chung đúng nguồn sai ấy** — nên về
cấu trúc nó không bao giờ bắt được lớp lỗi này. Lỗi xuất hiện ở **cả** weekly 08-24→28 **và**
monthly 08 (văn xuôi dòng 109), đúng như kỳ vọng nếu cả hai cùng lấy từ một số sai.

`marketPrice` đứng im 27.600 từ 23:01 đến 23:30 trong khi phiên đóng 27.800 (O 26.800 / H 27.900
/ L 26.700) — KHÔNG phải trễ đồng bộ, chỉ là field khác. SCL không thuộc UPCOM nên ngoại lệ giá
bình quân không áp dụng.

### Độ bao phủ cho kỳ tới (đã kiểm, không suy đoán)
- Cổng chạy cho MỌI cadence công bố tỉ suất; `--skip-validation` chỉ dành cho report HOLD/alert
  không công bố tỉ suất (`eod_trading_report.sh:63`) — đúng thiết kế, không phải lỗ hổng.
- Chạy thật monthly 08: **chỉ SCL bị chặn, 9/10 vị thế PASS** ⇒ hiệu chuẩn đúng, không chặn oan.
- Dung sai 0,15pp bắt được lệch 0,85pp.
- Câu gợi ý sửa giờ rẽ theo cổ tức THẬT của mã lệch (commit `9645d2bd`): mã cổ tức 0đ được chỉ
  thẳng vào `mtm_price` của snapshot, không bị dẫn sai sang "thiếu cổ tức".

**User chốt 2026-09-09: KHÔNG hồi tố báo cáo đã gửi; chỉ cần kỳ tới đúng.**

### Bài học test
Bản vá đầu của câu gợi ý khởi tạo biến SAI SCOPE ⇒ `NameError` ở nhánh văn xuôi. **Selfcheck
53/53 vẫn PASS** (fixture không chạm nhánh đó); chỉ chạy trên báo cáo THẬT mới lộ. Đúng §19 —
selfcheck xanh không thay được một lần chạy trên artifact thật.

### Việc 3 vẫn MỞ (không chặn kỳ báo cáo tới)
`park_holdings.py` → `compute_park_trim/jit_unpark` vẫn định cỡ lệnh bằng `marketPrice`. Chưa
làm, có lý do: (a) đổi SIZING LỆNH THẬT; (b) `park_holdings.py:562` ghi `§6: KHÔNG BQ` ⇒ nguồn
đúng là `dnse_close_prices` (DNSE) chứ KHÔNG phải `bq_close_prices`; (c) nhánh jsonl LỊCH SỬ
không dùng được nguồn live ⇒ cần thiết kế 2 nhánh; (d) phơi nhiễm đo được **0/26 park_trim +
0/27 jit_unpark**. Nên làm thành đợt riêng có selfcheck, KHÔNG ghép vào đợt này.

## Nguồn
- arch-review 2026-09-09 (verdict NEEDS_CHANGES, confidence high) — 7 required_changes
- `exdate_price_frame_selfcheck.py` chạy thật 4 biến thể TZ: exit 0, output identical
- Quét lại `data/execution_logs/dnse_raw_2026-0[89]-*`: 2.604 bản đọc `positions`
