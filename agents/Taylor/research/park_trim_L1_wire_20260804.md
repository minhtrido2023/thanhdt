# Wire F1 (target park 0,80) — L1 park-target compliance: ĐÃ VIẾT, CHƯA BẬT

Job `Taylor_20260804_024836` · 2026-08-04 · Taylor
Tiếp nối `park_unpark_live_wiring_20260803.md` (§B/§D/§F) và `park_wiring_two_options_20260804.md`
(user chốt hàng **F1**, target 0,80).

> **ĐÂY LÀ LẦN ĐẦU dự án này chạm code production thật.** Mọi vòng trước chỉ chạy trên bản sao
> `exp_park_jit_20260803/`. Danh sách file production đã sửa nằm ở §5 — **1 file production đang
> chạy (`trading_bot/executor.py`), 2 script MỚI chưa ai gọi, 1 file KB dạng `.proposed` chưa áp.**

## 0. Trạng thái từng bước

| Bước | Việc | Trạng thái |
|---|---|---|
| 1 | P0 — tag `book`/`play_type` vào journal executor | ✅ XONG, có selfcheck 30 ca |
| 2 | `park_holdings(account, asof)` — dựng lại vị thế theo book | ✅ XONG, đối soát broker KHỚP cả 2 account |
| 3 | `compute_park_trim.py` — L1 (trim), **CHỈ ĐỌC** | ✅ XONG |
| 3b | **L2 (JIT unpark)** | ⏸️ **CHƯA LÀM — treo sang vòng sau** (§6) |
| 4 | Dry-run số THẬT 2 account, DNSE sống | ✅ XONG, tái lập đúng số đã pin |
| 5 | Hướng dẫn DollarBill | ✅ viết ra `.proposed`, **chưa áp** (§13 coding_guidelines) |
| 6 | Tự verify + quant-skeptic | selfcheck + regression PASS; quant-skeptic: xem §7 |

**KHÔNG có gì được bật.** Không cron, không dispatch DollarBill, không sửa `trading_rules.json`,
không đưa lệnh nào vào plan thật.

## 1. Bước 1 — P0 book-tagging (thay đổi production DUY NHẤT đang chạy)

`trading_bot/executor.py::Executor._journal()` — thêm 2 cột `book`/`play_type`, **chèn TRƯỚC
`note`** (đúng §F1). Nguồn là `PlannedOrder.book`/`.play_type` vốn đã có sẵn ⇒ không đổi plan,
không đụng đường đặt lệnh, mọi event được tag đồng nhất (ghi tại `_journal`, không tại chỗ gọi).

**Hai điều đã kiểm chứ không phải suy đoán:**
- **Reader positional cũ không vỡ**: chỉ số cột 0-8 giữ nguyên. `churn_guard_selfcheck`,
  `tick_retry_selfcheck`, `extreme_regime_selfcheck` đều đọc `row[1]` = `event`. Đã grep TOÀN BỘ
  reader journal: `netting_recon.get_net_fill_from_journal` (production, `bot_execute.py:138`) và
  `paper_main_window_selfcheck` dùng `DictReader`; `execution_quality_review` dùng `pd.read_csv`
  theo tên cột. Không có reader nào đọc cột ≥ 9 theo vị trí.
- **Lỗi tôi tự bắt được khi review diff** (ghi lại vì nó suýt lọt): `_journal` chỉ ghi header khi
  file CHƯA tồn tại. Nếu executor khởi động lại GIỮA PHIÊN ngay sau khi deploy, nó sẽ ghi 12 giá
  trị vào một file có header 10 cột ⇒ `DictReader` đọc `note` thành `book` — hỏng cả file, đúng
  dạng lỗi im lặng. Đã vá: đọc header của file đang mở, thiếu cột `book` thì giữ nguyên layout CŨ
  cho đúng file đó (phiên ấy không có tag ⇒ `park_holdings` coi là chưa xác định ⇒ L1 tự chặn —
  fail-safe). Ca A7/A7b trong selfcheck. Hôm nay chưa có journal 08-04 nào nên cửa sổ này chưa
  từng mở, nhưng nó là lỗi cấu trúc, không phải giả định.

## 2. Bước 2 — `mike/bin/park_holdings.py`

Bootstrap ngày 0 (2 file user đã duyệt) → FIFO tiến bằng dòng FILL của journal. Ba cái bẫy được
xử lý tường minh: `qty` là **tích luỹ theo `child_oid`** (delta, không cộng thô); bán tiêu thụ
FIFO **trong cùng book**; bán không tag → FIFO oldest-first + cờ `UNVERIFIED`.

**Đối soát bắt buộc** Σ lô/mã vs `openQuantity` broker — lệch thì `reconcile.ok=False` và **giữ
nguyên sổ**, không tự nống cho khớp (§5). `park_mv_verified_vnd` loại hẳn phần UNVERIFIED.

**Kết quả trên số THẬT (DNSE sống 2026-08-04 09:55 ICT):**

| | PARK | CAPIT | LAG | EXCLUDED | DISC_SPECIAL | đối soát |
|---|---|---|---|---|---|---|
| SpaceX | **642,46tr** (15 mã) | 294,75tr | — | — | 7,80tr (TV1) | ✅ KHỚP 21/21 mã |
| ZaloPay | **279,78tr** (9 mã) | 176,39tr | 39,55tr | 394,00tr (DGC) | — | ✅ KHỚP 16/16 mã |

SpaceX PARK = **642,46tr** — trùng khít số §A6 đã pin, tức tái lập độc lập bằng một đường tính
khác (sổ lô theo tag, thay vì lọc theo tên mã).

⚠️ **ZaloPay thì KHÔNG trùng, và đó là điểm đáng giá nhất của bước này**: §A6 ước PARK ZaloPay
**297,63tr** bằng cách suy theo tên mã; sổ lô thật cho **279,78tr** (lệch **−17,85tr**) — vì CSV và
một phần VPB thực ra là **LAG**, không phải PARK. Đây chính xác là lỗi §A7 cảnh báo. Mọi số
`park_mv` suy-theo-tên từ nay không dùng nữa.

## 3. Bước 3 — `mike/bin/compute_park_trim.py` (L1, CHỈ ĐỌC)

Công thức §B2 + trần 2 tầng §D2, **không có tham số nào tự chế**: ngưỡng `0,005` và trần TỔNG
`_etf_day_cap` port từ `simulate_holistic_nav.py`; trần per-name = **đúng gate LAG live** (dùng
lại `LAG_ADV_PCT=0.20`, `LAG_ADV_MAX_STALE_DAYS=30`, `_adv_for_gate`, `share=1/N_live` import
thẳng từ `trading_bot/plan.py`, không copy số).

**Fail-closed ở 6 chỗ** (đều có ca selfcheck): sổ lệch broker · state ≠ NEUTRAL · không đo được
trần TỔNG · không dựng được danh sách account live · ADV lỗi/cũ >30 ngày/≤0 · không có
`marketPrice`. Thêm 2 ranh giới cứng: `excluded_tickers` và ticker `UNVERIFIED` không bao giờ vào
lệnh; CAPIT/LAG/BAL/DISCRETIONARY_SPECIAL nằm ngoài phạm vi theo cấu trúc (chỉ duyệt `park_lots`).

Ràng buộc hiện vật thêm vào ngoài thiết kế gốc: **không đề xuất bán quá `tradeQuantity`** (CP chưa
về T+2). Đây không phải tham số mô hình mà là điều kiện tồn tại của lệnh.

## 4. Bước 4 — Dry-run số thật (KHÔNG ghi vào plan nào)

`asof=2026-08-04`, DNSE sống, target F1 = 0,80:

| | pool | PARK | target 80% | **vượt** | trim đề xuất | còn thiếu → phiên sau |
|---|---|---|---|---|---|---|
| **SpaceX** | 647,28tr | 642,46tr | 517,82tr | **+124,63tr** | **85,31tr** (12 mã) | 39,32tr |
| **ZaloPay** | 285,59tr | 279,78tr | 228,48tr | **+51,30tr** | **28,58tr** (7 mã) | 22,72tr |

**Sanity check ngược về số đã biết** — chạy lại với target 0,70: SpaceX vượt **189,36tr**, khớp
**tuyệt đối** ô `SpaceX (dùng availableCash)` của bảng §A6. (Con số 182,52tr hay được trích là ô
dùng `totalCash` — thiết kế §B5 cấm dùng vì gồm 9,78tr cổ tức chưa về.) Hướng và độ lớn đúng.

Trần TỔNG/phiên đo được **1.337 tỷ** — không binding ở quy mô hiện tại (thừa ~10.700×). Trần
per-name cũng không cắt mã nào hôm nay.

⚠️ **Hạn chế thật, phải nói ra: lô chẵn ăn mất ~32% lượng trim mỗi phiên.** Pro-rata chia nhỏ cho
15 mã rồi làm tròn XUỐNG lô 100 ⇒ SpaceX đề xuất 85,31tr / 124,63tr cần. Ba mã (VHM 148k/cp, SHS,
VND) có phần chia < 1 lô nên **không trim được gì** phiên này. Hệ quả: (a) cần ~2 phiên để về
trong band, phần dư carry-over đúng như thiết kế; (b) mã giá cao bị trim chậm hơn mã giá thấp ⇒
trọng số rổ trôi nhẹ theo thời gian. Chưa đo mức trôi này; **không đề xuất "gộp cho đủ lô"** vì
đó sẽ là tham số mới chưa backtest.

## 5. Bước 6 — Danh sách ĐẦY ĐỦ file production đã thay đổi thật

| File | Loại | Đã sửa gì | Đang chạy chưa |
|---|---|---|---|
| `trading_bot/executor.py` | **PRODUCTION ĐANG CHẠY** | `_journal()`: +2 cột `book`/`play_type` trước `note`; giữ layout cũ cho file 10 cột đang mở dở | **CÓ** — mọi lệnh từ giờ ghi 2 cột này |
| `mike/bin/park_holdings.py` | script MỚI | (mới) sổ vị thế theo book | **KHÔNG** — chưa ai gọi |
| `mike/bin/compute_park_trim.py` | script MỚI | (mới) L1 trim, chỉ đọc | **KHÔNG** — chưa ai gọi |
| `book_tagging_selfcheck.py` | selfcheck MỚI | 30 ca | chạy tay |
| `mike/kb/context_planning_mini.md.proposed` | **`.proposed`, KHÔNG áp** | mục hướng dẫn DollarBill | **KHÔNG** — file gốc chưa đụng |
| `mike/agents/Taylor/research/park_trim_L1_wire_20260804.md` | báo cáo | (file này) | — |

**KHÔNG đụng tới**: `data/trading_rules.json`, `simulate_holistic_nav.py`, `pt_v23_audit_2014.py`,
`golive_recommend_v23.py`, `trading_bot/plan.py`, crontab, mọi file `plan_*.json` thật.

`context_planning_mini.md` được ghi ra `.proposed` **có chủ đích** (§13 coding_guidelines): nó là
file `@`-import thẳng vào phiên DollarBill — sửa tại chỗ = DollarBill bắt đầu chạy script ngay lần
dispatch kế, đúng thứ Bước 6 cấm. Mike duyệt xong thì `mv`.

**Cổng còn phải mở trước khi dùng thật**: target 0,80 ≠ `etf_park_frac`=0,70 đang publish trong
`golive_v23_status.json` ⇒ cần `risk_dial_override` được ghi nhận (`trading_rules.json` v2.1
`neutral_parking`). Script **tự in cảnh báo này** mỗi lần chạy; nó không tự mở cổng cho mình.

## 6. L2 (JIT unpark) — CHƯA LÀM, treo sang vòng sau

Đúng khuyến nghị của chính báo cáo gốc (§B1: L1 trước L2) và cho phép của dispatch. Lý do dừng
đúng ở đây chứ không cố nhồi: L2 cần một điểm tích hợp KHÁC hẳn — nó phải đọc danh sách lệnh mua
đang thiếu tiền của plan đang lập, tức là phải gắn vào luồng sinh plan chứ không phải một script
đọc-broker độc lập; làm vội sẽ ra một cơ chế bán PARK không ai review kịp.

Đo được từ Bước 4: L1 một mình giải phóng **85,31tr phiên đầu** cho SpaceX (và 124,63tr sau ~2
phiên) so với **171,1tr** nhu cầu của 2 lệnh đang bị defer — tức L1 lấy lại phần lớn nhưng
**chưa đủ hết** cho case hiện tại. L2 vẫn có giá trị, chỉ là không cấp bách bằng.

## 7. Tự kiểm

- `book_tagging_selfcheck.py` — **30/30 PASS**, chạy lại dưới `env -u TZ`,
  `TZ=America/New_York`, và `env -i` (môi trường trắng, cwd khác) — **giống nhau cả 4 lần**
  (§19 verify-before-done; §16: `_journal` gọi `now_ict()`, `park_holdings` gọi
  `datetime.now(ZoneInfo)`).
- Regression suite executor/plan: `tick_retry`, `churn_guard`, `extreme_regime`,
  `paper_main_window`, `discretionary_participation_cap`, `capit_participation_cap`,
  `test_trading_bot`, `capit_lever`, `ghost_order`, `excluded_tickers`, `lag_adv_cap` — **11/11
  exit 0**.
- Đối soát sổ-vs-broker: KHỚP 100% cả 2 account trên dữ liệu sống.
- Tái lập số đã pin: SpaceX PARK 642,46tr (§A6) và mức vượt 189,36tr @0,70 (§A6) — **khớp tuyệt đối**.

**Chưa làm**: quant-skeptic vòng cuối (đang chạy) · Mike đọc lại code · chưa đo mức trôi trọng số
do lô chẵn · L2.

## 8. quant-skeptic vòng cuối — **CONFIRMED, confidence CAO** (2026-08-04, log `mike/logs/verify_20260804_031110.log`)

Reviewer **tự tái lập độc lập**, không chỉ đọc: chạy lại selfcheck 30/30 trên 4 môi trường, chạy
lại 11/11 regression, và **tự gọi DNSE sống** chạy `compute_park_trim --account SpaceX` ngay trong
phiên review — tái lập **đúng tới từng đồng VND** mọi số headline (park_mv 642.455.000, pool
647.276.143, target 517.820.914, vượt 124.634.086, trim 85.310.000, thiếu 39.324.086, day_cap
1.336.981.660.406) và đúng 3 mã bị chặn bởi lô chẵn. Grep xác nhận mọi hằng số trong code mới là
**port nguyên văn** từ file production đã duyệt, không phải tham số mới; và **không reader journal
nào trong repo** — kể cả ngoài danh sách báo cáo tự nêu — đọc CSV theo vị trí ở vùng cột bị ảnh
hưởng.

**Killer objection (giữ nguyên, không phản bác được bằng code):** sổ lô chỉ đúng bằng độ chính xác
của bootstrap snapshot + trường `book`/`play_type` của MỌI plan tại thời điểm khớp. Selfcheck chứng
minh cơ chế replay đúng **khi đầu vào đúng**; nó không chứng minh được snapshot (JSON người duyệt)
hay plan generator quá khứ chưa từng gắn sai book. Một bug tương lai gắn lệnh mua CAPIT thành PARK
sẽ làm `park_mv` phồng lên và kích hoạt trim THẬT. Đây là rủi ro garbage-in của mọi ledger
bootstrap — và đúng là lý do thiết kế giữ L1 gated hoàn toàn.

**3 việc reviewer yêu cầu trước khi mở cổng:**
1. ✅ **XONG NGAY** — chạy lại ZaloPay live độc lập: TRIM, park_mv 279.775.200, pool 285.594.054,
   target 228.475.243, vượt 51.299.957, đề xuất 28.580.000 (BID/CTG/HDB/MBB/TCB/VCB/VPB), thiếu
   22.719.957, chặn LPB+VHM (dưới 1 lô). **Khớp tuyệt đối bảng §4.**
2. ⏸️ **CHƯA LÀM** — audit từng tag `book`/`play_type` của bootstrap snapshot 2 account đối chiếu
   lịch sử giao dịch broker THẬT. `park_holdings` tin snapshot này là ground truth ngày 0.
3. ⏸️ **CHƯA LÀM** — quant-skeptic cho chính báo cáo chọn F1 (`park_wiring_two_options_20260804.md`,
   Calmar 1,63 / PBO 0,08). Finding này coi 0,80 là **đầu vào**, không tự chứng minh lại.
