# RCA — DT5G lịch sử bị viết lại (2026-07-29)

Job `Winston_20260729_123049` · read-only · Winston

## TL;DR

Giả thuyết restate **ĐƯỢC XÁC NHẬN**, và **cả 2 loại trừ của Mike đều sai**:

- (a) VNINDEX_PE **KHÔNG** vô can — nó chính là **nguyên nhân chính** của đợt 2026-07-29.
  Test "AVG PE gần như không đổi" là **test sai**: AVG bỏ qua NULL, nên backfill hàng nghìn
  điểm NULL→value hầu như không đổi AVG nhưng đổi **toàn bộ expanding percentile rank**.
- (b) Universe composition **CÓ** đổi ở dòng lịch sử — `ticker_prune` năm 2024 mất
  1.269 dòng / 10 mã (346→336 mã). "Số lượng ticker không đổi" chỉ đúng ở ngày gần nhất.

Ngoài ra có **kênh restate thứ 2, liên tục và vĩnh viễn**: `Close`(adj)/`MA50`/`MA200`/`D_CMF`
bị điều chỉnh hồi tố mỗi khi có corporate action (~2,3–3,4% số dòng/tuần).

**Tác động production:** bảng **`vnindex_5state_dt5g_live` đổi 101/3134 phiên lịch sử (3,22%)**
trong lần refresh 2026-07-29, trong đó **35 phiên lệch ≥2 tier**, biên độ trọng số
**−70pp … +100pp**. Bao gồm cả việc xoá bỏ pha CRISIS 2018-03-19→2018-05-08 (đổi thành BULL).

## 1. Time-travel BẤT KHẢ THI — và đó tự nó là 1 phát hiện

```
FOR SYSTEM_TIME AS OF TIMESTAMP('2026-07-28 09:00:00+00')
→ Not found: Table ...tav2_bq.ticker@1785229200000 was not found
```

`tav2_bq.__TABLES__` (đọc 2026-07-29 ~12:30 UTC):

| table | creation_time (UTC) | last_modified |
|---|---|---|
| `ticker` | **2026-07-29 06:35:17** | 2026-07-29 10:23:41 |
| `ticker_prune` | **2026-07-29 07:27:05** | 2026-07-29 10:17:21 |
| `ticker_financial` | 2026-07-28 11:07:55 | 2026-07-29 10:21:32 |

`creation_time` = **hôm nay** ⇒ upstream **DROP + CREATE (CREATE OR REPLACE)** các bảng này
**mỗi ngày**, không phải append. Hệ quả: **BQ time-travel bị xoá sạch mỗi sáng** — không bao giờ
lùi được quá lần rebuild gần nhất. Mọi kế hoạch "pin lịch sử bằng time-travel" là bất khả thi.

**Anchor T-1 dùng thay thế:** local parquet cache `data/bq_cache/` (`sync_bq_cache_daily.sh`,
23:45 ICT, delta-append ⇒ giữ nguyên giá trị lịch sử như lúc lần đầu kéo về).
`ticker/{2013..2025}.parquet` mtime = 2026-07-22, `2026.parquet` = 2026-07-28 23:56.

## 2. Bằng chứng restate

### 2.1 VNINDEX_PE — backfill 2006+ (nguyên nhân chính, landed HÔM NAY)

Diff cache vs BQ live, hàng VNINDEX, 2013+:

| cột | số phiên đổi |
|---|---|
| Close, MA200, D_CMF, D_RSI, D_MACDdiff, C_L1M, C_L1W, Volume | **0** |
| **VNINDEX_PE** | **847** (843 NULL→value + 4 value→value vụn) |

843 dòng NULL→value nằm gọn ở **2013-01-02 → 2016-05-31**. Profile NULL hiện tại của BQ cho
thấy PE giờ đã có giá trị **từ 2006** (2006: 250 phiên / 56 NULL; 2007: 248 / 1 NULL) — đúng khớp
memory `vnindex-pe-bq-gotcha`: *bq_admin xác nhận BUG 2026-07-29, backfill về 2006*. **Backfill đã
đáp xuống, chính là hôm nay.**

Giá trị được thêm vào là vùng bong bóng 2006–2007:

```
yr    min    avg    max
2006  27.9   36.4   45.5
2007  26.4   39.9   59.9      <-- mới xuất hiện trong cửa sổ expanding
...
2018  15.4   18.9   22.6      <-- trước đây là ĐỈNH của cửa sổ
```

### 2.2 Cơ chế lan truyền — 2 kênh, đều là expanding window (xác nhận trong code)

1. `vnindex_5state_ew_v1.py:387-393` — **PE override** dùng `nanpercentile(hist_valid, 90)` với
   `hist = pe_arr[:t+1]` (expanding, mọi giá trị non-NaN trước đó).
   → Thêm PE 2006-07 (26–60) làm `pe_p90` bật vọt cho **mọi ngày về sau**.
   → PE 2018 (max 22,6) trước đây vượt p90 ⇒ **override CRISIS**; giờ không vượt ⇒ **không fire**.
   Khớp chính xác với việc pha CRISIS 2018-03-22→05-08 biến mất.
2. `vnindex_5state_dual_v3.py:111-125` — `expanding_pct_rank(min_lb=252)` trên 8 factor
   (`P3M,P1M,MA200,RSI,MACD,CMF,Breadth,PE`), rồi `r_score_raw = expanding_pct_rank(score_raw)`.
   → Thêm ~2.500 quan sát PE cũ đổi rank của PE tại **mọi** ngày sau đó → đổi composite score →
   đổi rank của score → đổi state. **Rank-of-rank ⇒ khuếch đại, không cục bộ.**

### 2.3 Close/MA50/D_CMF — restate liên tục do corporate action (kênh 2, vĩnh viễn)

Diff `tav2_bq.ticker` cache(07-22) vs live, cột mà `ew_v1` đọc:

| năm | Close | Price(unadj) | Volume | MA50 | D_CMF |
|---|---|---|---|---|---|
| 2019 | 6.709 (2,357%) | **0** | 28 | 6.822 | 4.252 |
| 2024 | 7.256 (2,296%) | 11 | 2.323 | 7.401 | 6.657 |

**`Price` (chưa điều chỉnh) gần như bất động, chỉ `Close` (đã điều chỉnh) đổi** ⇒ đúng chữ ký
của điều chỉnh hồi tố corporate action. Năm 2019: **29/1159 mã** bị đụng, mỗi mã bị viết lại
**trọn 250 phiên** với hệ số gần-đồng-nhất < 1 (BDW 0,946–0,982; BKC 0,775–0,779; CTG 0,984–0,986;
MWG 0,984–0,985) — không đồng nhất tuyệt đối chỉ vì làm tròn bước giá.
Đây là hành vi **ĐÚNG và CỐ Ý** của một chuỗi giá điều chỉnh — nhưng nó có nghĩa lịch sử
`Close/MA/D_CMF` **không bao giờ đứng yên**, ~2–3% dòng/tuần.

### 2.4 ticker_prune — membership lịch sử ĐỔI (bác bỏ loại trừ (b))

2024: cache 71.685 dòng / 346 mã → BQ live 70.420 dòng / **336 mã**.
**1.269 dòng bị XOÁ khỏi lịch sử**, chỉ 4 dòng thêm.

```
mã   số dòng mất   khoảng
FRT      250       2024-01-02 → 2024-12-31   (mất TRỌN năm)
NO1      217       2024-01-05 → 2024-12-31
PXL      213       2024-01-02 → 2024-11-12
AST      129 / VRG 127 / IVS 126 / TIS 90 / KSV 85 / TID 31 / VNA 1
```

Breadth flag (Close>MA200) không phiên nào lật ⇒ macro breadth-guard tạm thời không bị ảnh hưởng
bởi phần *giá trị*, nhưng **mẫu số universe point-in-time đã đổi** ⇒ mọi backtest trên
`ticker_prune` có rủi ro survivorship di động.

## 3. Tác động: DT5G production đã bị viết lại

`data/bq_cache/vnindex_5state_dt5g_live.parquet` (07-28 23:45) vs `tav2_bq.vnindex_5state_dt5g_live` (live):

**101 / 3.134 phiên đổi state (3,22%) · 35 phiên lệch ≥2 tier · Δweight −70pp…+100pp**

| khoảng | phiên | cũ → mới | Δw |
|---|---|---|---|
| 2018-02-27 → 2018-03-16 | 14 | BULL (100%) → NEUTRAL (70%) | −30pp |
| 2018-03-19 → 2018-03-21 | 3 | **CRISIS (0%) → NEUTRAL (70%)** | +70pp |
| **2018-03-22 → 2018-05-08** | **31** | **CRISIS (0%) → BULL (100%)** | **+100pp** |
| 2019-12-10 | 1 | BEAR → NEUTRAL | +50pp |
| 2020-03-16 → 2020-04-03 | 14 | BEAR (20%) → **CRISIS (0%)** | −20pp |
| 2020-05-26 | 1 | NEUTRAL → CRISIS | −70pp |
| 2020-12-28 | 1 | BULL → EX-BULL | +30pp |
| 2022-11-01 / 2022-12-14 | 2 | CRISIS → BEAR | +20pp |
| 2023-02-07 → 2023-03-16 | 28 | NEUTRAL (70%) → BEAR (20%) | −50pp |
| 2023-04-04 → 2023-04-11 | 6 | NEUTRAL (70%) → BEAR (20%) | −50pp |

*(mã state: 1=CRISIS 0%, 2=BEAR 20%, 3=NEUTRAL 70%, 4=BULL 100%, 5=EX-BULL 130%)*

Phân bố 2014+ đổi: CRISIS 510→489, BEAR 220→241, NEUTRAL 1939→1923, BULL 406→422, EXBULL 59→60.

**Nghiêm trọng nhất:** pha CRISIS 2018-03-19 → 2018-05-08 **biến mất**. Bản cũ nói DT5G thoát
hàng ~3 tuần TRƯỚC đỉnh 2018-04-09; bản mới nói DT5G **giữ BULL 100% xuyên qua đỉnh** và chỉ ra
sau 2018-05-08. Đây là một trong những "cú cứu" trưng bày của mô hình — track record lịch sử vừa
bị đảo chiều. (Chiều ngược lại: 2020 COVID và 2023 Q1 trở nên **phòng thủ hơn**.)

Ở bảng base `vnindex_5state`: **134 state + 144 state_raw** đổi. Riêng **2014+ = đúng 71 phiên**
— khớp con số Mike báo (Mike đo trên cửa sổ 2014+; toàn lịch sử là 134). Cụm lớn nhất là 2007 (52).

## 4. Đây là churn LẶP LẠI hay sự cố 1 lần? → CẢ HAI

Diff các bảng archive `vnindex_5state_archive_predeploy_*` liên tiếp:

| refresh | state đổi | raw đổi |
|---|---|---|
| 07-23 → 07-24 | 0 | 1 |
| 07-24 → 07-27 | 0 | 0 |
| 07-27 → 07-28 | 1 (2026-07-24) | 0 |
| 07-28 → 07-29(archive) | 1 (2022-12-01) | 3 |
| **07-29(archive) → live (chạy hôm nay)** | **134** | **144** |

⇒ **Nền churn thường ngày ≈ 0–1 phiên/ngày** (kênh corp-action, không bao giờ tắt) +
**sự kiện đột biến khi upstream backfill/sửa dữ liệu** (hôm nay: 134).
Nghĩa là DT5G lịch sử là **target di động vĩnh viễn**, chỉ khác về biên độ.

## 5. Cố ý hay bug?

**Cả 2 kênh đều CỐ Ý, không phải bug upstream:**
- PE backfill 2006+ = bq_admin **sửa** một BUG đã xác nhận (PE NULL trước 2016-07-01).
  Dữ liệu MỚI đúng hơn dữ liệu cũ.
- Close re-adjust = hành vi chuẩn của chuỗi giá điều chỉnh corporate action.
- `ticker_prune` membership = tiêu chí lọc chất lượng được tính lại (FRT, KSV, TIS… bị loại).

**Bug thật sự nằm ở PHÍA TA:** pipeline DT5G dùng **expanding window** (p90 override +
expanding_pct_rank + rank-of-rank) trên dữ liệu **có thể bị restate**, và rebuild **toàn bộ lịch sử
từ đầu mỗi đêm** (`daily_refresh_v34b_linux.sh` step [1] `rm -f data/_cache_*.pkl`) rồi
`bq load --replace` đè bảng. Không có bất kỳ lớp pin/lock/cảnh báo nào giữa hai điều đó.

## 6. Khuyến nghị mitigate (đề xuất — cần user/Taylor duyệt, tôi KHÔNG tự sửa)

**Ưu tiên 1 — cảnh báo (rẻ, read-only, không đụng mô hình):**
thêm 1 step vào `daily_refresh_v34b_linux.sh` **sau** step [11]: diff `vnindex_5state` mới với
`vnindex_5state_archive_predeploy_<TS>` vừa tạo, trên các dòng `time < T-30`; nếu số phiên đổi
> ngưỡng (đề xuất 5) → alert bus + Telegram. Hôm nay sẽ bắn ở 134. **Hiện tại sự kiện này lọt
qua hoàn toàn im lặng** — chỉ tình cờ được phát hiện.

**Ưu tiên 2 — giữ được anchor lịch sử:** archive predeploy đang prune còn **5 bản** ⇒ chỉ lùi
được 5 ngày. Đề xuất giữ thêm 1 bản **mốc tháng** (`..._monthly_YYYYMM`) không bao giờ prune, cho
cả `vnindex_5state` và `vnindex_5state_dt5g_live` (dt5g_live hiện **không** được backup dated).
Vì time-travel BQ đã chết (mục 1) nên đây là cách duy nhất pin lịch sử.

**Ưu tiên 3 — dán nhãn mọi kết quả đã pin:** mọi CAGR/Sharpe/audit trích DT5G lịch sử (kể cả
**R3 đã pin**) phải ghi kèm snapshot dùng (tên bảng archive / mtime parquet) và coi là
**"as-of", không tái lập được** nếu không có snapshot. Kết quả pin trước 2026-07-29 chạy trên
lịch sử **đã lỗi thời** — 2018/2020/2023 là các năm nặng ký, cần chạy lại.

**Ưu tiên 4 — thuộc Taylor (mô hình, ngoài phạm vi Winston):** cân nhắc khoá điểm bắt đầu cửa sổ
expanding (vd luôn tính rank từ 2006 bất kể dữ liệu tới lúc nào) hoặc dùng cửa sổ rolling cố định,
để backfill upstream không viết lại được lịch sử. Đây là **thay đổi mô hình**, cần user duyệt.

## Lệnh tái lập

```bash
# 1. chứng minh time-travel đã chết
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 \
 "SELECT table_id, TIMESTAMP_MILLIS(creation_time) FROM tav2_bq.__TABLES__ WHERE table_id IN ('ticker','ticker_prune')"
# 2. diff base state qua các bản archive
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 \
 "SELECT COUNTIF(a.state!=b.state) FROM tav2_bq.vnindex_5state_archive_predeploy_20260729_183602 a JOIN tav2_bq.vnindex_5state b USING(time)"
# 3. diff dt5g production vs cache parquet 07-28 → script trong log job này
```
