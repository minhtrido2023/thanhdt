# Bảng công bố BẤT BIẾN cho chuỗi 5-state (base v3.4b + DT5G production)

**Job**: `Taylor_20260730_013951` (code + self-check) → `Taylor_20260730_025109` (báo cáo + verify + commit)
**Ngày**: 2026-07-30
**Phạm vi**: đổi **CÁCH GHI** hai bảng công bố state. **Không đổi một dòng công thức nào** ⇒ rủi ro mô hình = 0.
**Trạng thái**: code + self-check XONG (PASS). Chờ quant-skeptic trước khi commit.

---

## 1. Vấn đề (RCA)

Nguồn: `mike/agents/Winston/research/dt5g_history_restate_rca_20260729.md`,
đề xuất §5 `mike/agents/Taylor/research/rolling_vs_expanding_dt5g_20260729.md`.

`daily_refresh_v34b_linux.sh` rebuild **toàn bộ** lịch sử state mỗi đêm rồi `bq load --replace`
đè cả bảng. Upstream (`ticker`, `ticker_prune`) bị DROP+CREATE mỗi ngày, nên mọi điều chỉnh hồi
tố (PE backfill 2006+, corp-action re-adjust `Close`, `ticker_prune` membership) lan qua các cửa
sổ **EXPANDING** của mô hình (`pe_p90`, `expanding_pct_rank`, rank-of-rank, `running_max`) và
**viết lại state của phiên đã đóng nhiều năm trước** — im lặng, không cảnh báo.

Đo thật ngày **2026-07-29**: **134 phiên** ở `vnindex_5state` (base) + **101 phiên** ở
`vnindex_5state_dt5g_live` (PRODUCTION) bị viết lại, trong đó 35 phiên lệch ≥2 tier.

Hệ quả nghiêm trọng nhất không phải vận hành mà là **nghiên cứu**: backtest 2018 đang đọc state
được tính bằng dữ liệu PE backfill năm 2026 — dữ liệu **không hề tồn tại** vào 2018. Đây là
look-ahead tinh vi, không bị bất kỳ gate nào hiện có bắt.

**Nguyên tắc user duyệt (2026-07-30)**:
> State của MỘT PHIÊN ĐÃ CÔNG BỐ là **SỰ KIỆN ĐÃ XẢY RA** (ta đã hành động theo nó), không phải
> một ước lượng được phép cập nhật.

---

## 2. Thiết kế — `state_publish_immutable.py` (384 dòng)

Publisher chỉ được làm 3 việc:

| | Việc | Cơ chế |
|---|---|---|
| (a) | **APPEND** phiên mới | nhánh `NOT MATCHED BY TARGET` của MERGE |
| (b) | **RECOMPUTE đuôi ngắn chưa chốt** (`SEAL_N = 25` phiên giao dịch) | nhánh `MATCHED` |
| (c) | **KHÔNG BAO GIỜ ghi đè phiên ĐÃ CHỐT** | xem "bảo đảm cấu trúc" dưới |

Công thức/dữ liệu mới cho kết quả khác ở vùng đã chốt → ghi thành **VINTAGE MỚI**
(`snapshot_vintage()` → `<table>_vintage_YYYYMMDD`), **không đè bảng công bố**.

### 2.1 Bảo đảm CẤU TRÚC (không phải bảo đảm bằng cẩn thận)

```
new series → staging table → MERGE chỉ trên `time > cutoff`
```
**Cả ba** nhánh MERGE đều bị chặn cứng bởi `time > cutoff`:
- `ON T.time = S.time AND T.time > DATE cutoff`
- `USING (SELECT * FROM stage WHERE time > DATE cutoff)`
- `WHEN NOT MATCHED BY SOURCE AND T.time > DATE cutoff THEN DELETE`

⇒ Vùng đã chốt **không nằm trong phạm vi câu lệnh ghi**. Không phụ thuộc việc code có nhớ
kiểm tra hay không.

**Xác minh kép**: checksum vùng đã chốt (`MD5(STRING_AGG(... ORDER BY time))`) được chụp **ngay
trước** và **ngay sau** mỗi MERGE, phải khớp **từng byte**; lệch → `PublishAbort` + alert.
(Cố ý **không** dùng `SUM(FARM_FINGERPRINT)`: tràn INT64 trên ~6.300 dòng — đo thật — và tổng
có thể trùng khi hai thay đổi triệt tiêu nhau.)

### 2.2 Cơ sở `SEAL_N = 25` — đo thật, không đoán

- **Chân trên**: `enC`/`enX` của DT-4gate = **25 phiên**. Dưới ngưỡng này một state mới còn
  **chưa thể commit**, nên chưa thể coi là đã chốt.
- **Chân dưới** (hiệu ứng viết-lại **do chính mô hình**, không do dữ liệu): các bộ
  `min_stay_filter` là **không nhân quả** — một run ngắn ở cuối chuỗi bị ghi đè bằng state
  trước đó rồi tự phục hồi khi run dài ra. Đo trên chuỗi thật (200 điểm cắt, 2.000 phiên gần
  nhất): `ew_v1` (mode15+min_stay7) = tối đa **5 phiên**; leg v3.4b (mode3+min_stay2) = **0
  phiên**. `_dt_4gate` và `_commit` (cap) nhân quả thuần → **0**.

⇒ **25 phiên ≈ 5× biên độ viết-lại nội tại lớn nhất**, đồng thời phủ trọn cam kết DT-gate.

> `SEAL_N` là **ngữ nghĩa công bố**, KHÔNG phải tham số tinh chỉnh. Đổi nó cần user duyệt.

### 2.3 Các chi tiết an toàn khác

- **`asof_date`** (cột mới): ngày **giá trị** dòng đó được ghi/đổi lần cuối (không phải ngày
  chạm gần nhất) ⇒ đọc được ngay "dòng này ổn định từ bao giờ". Dòng đã chốt giữ vĩnh viễn.
  `ensure_asof_column()` idempotent; lần backfill migration = **đóng băng baseline** tại thời
  điểm triển khai (chấp nhận bản đã bị restate 07-29 là "sự thật đã công bố", dừng vòng lặp
  tại đây — đúng yêu cầu migration).
- **Telemetry quan trọng nhất — `n_sealed_diff`**: số phiên đã chốt mà bản tính hôm nay khác
  bản đã công bố. Đây **chính là** số phiên `bq load --replace` cũ sẽ âm thầm viết lại. Giờ nó
  **không được áp dụng, chỉ được ĐẾM** + alert → biến sự cố im lặng thành số liệu quan sát
  được (`data/immutable_publish_history.jsonl`).
- **GAP-FILL** (`n_sealed_only_new > 0`): phiên nằm trong vùng đã chốt nhưng **chưa từng được
  công bố** (chỉ xảy ra khi publisher chết >25 phiên liên tiếp) → `INSERT` + anti-join, câu
  lệnh này **không thể sửa dòng đã có**. Không vá thì chuỗi công bố **thủng lỗ vĩnh viễn**,
  hỏng hơn hẳn. Có alert riêng ("kiểm tra cron").
- **Fail-CLOSED** (`PublishAbort`, không ghi gì) khi: thiếu cột · ngày trùng · state NULL ·
  `len(new) <= seal_n` · bảng tồn tại nhưng **RỖNG** · chuỗi tính mới **tụt hậu** so với bản đã
  công bố (`new_max < pub_max` — nhánh `NOT MATCHED BY SOURCE` sẽ xoá phiên đã công bố; đó là
  mất dữ liệu, không phải "recompute đuôi").
- **Dọn staging ngay sau MERGE** — không để bảng `*__pubstage` tích trong dataset trông như
  nguồn dữ liệu thật (bẫy `coding_guidelines` §9/§10).
- **`export_published_csv()`** atomic (`tmp` + `os.replace`, §5).
- **Bootstrap**: bảng chưa tồn tại → nạp toàn bộ, coi là baseline đóng băng.

---

## 3. Self-check — `immutable_publish_selfcheck.py`

Chạy trong **sandbox** `tav2_bq._ipsc_*` (clone từ production), **không chạm bảng thật**.
`IMMUTABLE_NO_ALERT=1` để không spam Telegram đội.

| Case | Nội dung |
|---|---|
| **A** | Vùng đã chốt BẤT BIẾN, **0 diff** sau publish hôm nay |
| **B** | Đuôi 25 phiên == chuỗi tính theo **công thức cũ**, byte-for-byte (chứng minh không đổi mô hình) |
| **C** | **Mô phỏng ĐÚNG sự cố 07-29**: backfill giả viết lại **101 phiên** đã chốt → **KHÔNG lan vào bảng** |
| **C2** | Telemetry đếm **đúng** số phiên upstream muốn viết lại |
| **D** | **Idempotent**: chạy lại lần 2 không đổi gì, kể cả `asof_date` |
| **E** | Append 30 phiên mới (25 đuôi + **5 gap-fill**) → đủ, phần đã công bố nguyên vẹn |
| **F** | `cutoff` **tiến lên** sau append, phần vừa chốt vẫn bất biến |
| **G** | Chuỗi tính **tụt hậu** → fail-CLOSED, không xoá phiên đã công bố |
| **H** (×3) | Input hỏng → fail-CLOSED: chuỗi ngắn hơn `seal_n` · ngày TRÙNG · state NULL |
| **I** | `publish_immutable` nhận **DataFrame** (đường mà `publish_gated_state.py` dùng); 60 phiên đã chốt bị sửa → KHÔNG lan vào bảng |
| **J1-J4** | CSV mirror: == bảng đã công bố byte-for-byte (KHÔNG phải chuỗi tính lại) · giữ đúng schema 3 cột · mang state ĐÃ CÔNG BỐ ở 60 phiên bị làm sai · atomic (không để lại `.tmp`) |

A/B/C/C2/D/E/F/G chạy cho **CẢ HAI** bảng (base v3.4b + DT5G live) ⇒ **8×2 + 3 + 1 + 4 = 24 assertion**.

**KẾT QUẢ: 24/24 PASS, 0 FAIL** — chạy lại **độc lập** trong job `Taylor_20260730_025109`
(job trước chạm max-turns nên stdout không được giữ; lần này log đầy đủ ở
`mike/logs/immutable_publish_selfcheck_20260730.log`, exit 0).

### 3.1 Kết quả đã ghi (`data/immutable_publish_history.jsonl`, **52 bản ghi**, 52/52 `sealed_immutable=true`)

Trích các dòng đại diện (mọi dòng đều `sealed_immutable=true`):

| ts (UTC) | label | cutoff | sealed_rows | tail | `n_sealed_diff` | `only_new` | `only_pub` | SEALED |
|---|---|---|---|---|---|---|---|---|
| 02:32:08 | selfcheck BASE v3.4b | 2026-06-24 | 6307 | 25 | **0** | 0 | 0 | ✅ |
| 02:32:38 | BASE rerun (idempotent D) | 2026-06-24 | 6307 | 25 | **0** | 0 | 0 | ✅ |
| 02:33:07 | **BASE FORGED** (case C) | 2026-06-24 | 6307 | 25 | **101** | 0 | 0 | ✅ |
| 02:33:39 | BASE APPEND (case E/F) | 2026-08-05 | 6337 | 25 | 101 | **5** | 0 | ✅ |
| 02:34:33 | selfcheck DT5G live | 2026-06-24 | 3110 | 25 | **0** | 0 | 0 | ✅ |
| 02:35:01 | DT5G rerun (idempotent D) | 2026-06-24 | 3110 | 25 | **0** | 0 | 0 | ✅ |
| 02:35:30 | **DT5G FORGED** (case C) | 2026-06-24 | 3110 | 25 | **101** | 0 | 0 | ✅ |
| 02:36:02 | DT5G APPEND (case E/F) | 2026-08-05 | 3140 | 25 | 101 | **5** | 0 | ✅ |
| 02:37:24 | selfcheck DF-input (case I/J) | 2026-06-24 | 3110 | 25 | **60** | 0 | 0 | ✅ |

**Cách đọc dòng FORGED** — đây là bằng chứng cốt lõi: input giả lập viết lại **101 phiên đã
chốt** (đúng quy mô sự cố 07-29, mẫu `2024-11-12 3->1 | 2024-11-13 3->1 | ... | 2024-11-21 1->5`);
telemetry **đếm đủ 101**, nhưng checksum vùng đã chốt **trước == sau MERGE** ⇒
`sealed_immutable=true` ⇒ **không một phiên nào trong 101 phiên đó lọt vào bảng**.

Dòng `only_new=5` (case E) chứng minh **gap-fill** hoạt động đúng: 5 phiên chưa từng công bố
được APPEND, đồng thời `sealed_immutable` vẫn `true` (không ghi đè gì).

### 3.2 Lần ghi THẬT vào production

| ts (UTC) | table | cutoff | sealed_rows | `n_sealed_diff` | SEALED |
|---|---|---|---|---|---|
| 02:06:13 | `tav2_bq.vnindex_5state` (base v3.4b) | 2026-06-24 | 6307 | **0** | ✅ |
| 02:14:04 | `tav2_bq._ipsc_e2e` (E2E DT5G production path) | 2026-06-24 | 3110 | **0** | ✅ |

Lần ghi thật vào `vnindex_5state` qua publisher mới: `n_sealed_diff=0`, `sealed_immutable=true`
— an toàn, không làm hỏng gì.

---

## 4. Thay đổi wire vào chain

### 4.1 `daily_refresh_v34b_linux.sh`

**Step [10]** — `bq load --replace vnindex_5state` → `state_publish_immutable.py --csv ... --table tav2_bq.vnindex_5state`. Abort → `die` (bảng giữ bản hôm qua; gate freshness chặn hạ nguồn).

**Step [11]** (sửa **sau** review quant-skeptic, xem §7) — `... AS SELECT * FROM vnindex_5state`
→ `... AS SELECT time, state, state_raw FROM vnindex_5state`. Publisher bất biến thêm cột audit
`asof_date` vào `vnindex_5state`; `SELECT *` sẽ âm thầm nhân bản cột đó sang
`vnindex_5state_tam_quan_v34b_clean` — bảng có **~50 consumer** chưa ai audit về giả định số cột.
`asof_date` là metadata **của hành động công bố**, không thuộc đặc tả chuỗi state ⇒ ghim 3 cột
tường minh giữ đúng hợp đồng `_v34b_clean == vnindex_5state` (CLAUDE.md), và mọi cột audit thêm
sau này cũng tự động không lan xuống.
Verify: chạy đúng SQL đó vào sandbox `_ipsc_v34b_syncprobe` → schema ra
`['time','state','state_raw']`, **không có** `asof_date` (đã dọn probe). `bash -n` PASS.

**Step [11b] + [12b]** — `restate_guard.sh` giờ chạy với **hai env override, GIỐNG NHAU ở cả hai
lần gọi** (cả hai bảng đều publish bất biến):

- **`RESTATE_LOOKBACK_DAYS=45`** (mặc định 30). Cửa sổ chốt của publisher là **25 phiên GIAO
  DỊCH** (~35 ngày lịch, hơn nữa nếu rơi vào Tết), còn guard cắt theo **NGÀY LỊCH**. Để mặc
  định 30 ngày lịch (~21 phiên) thì guard soi cả dải 21-25 phiên **vốn chưa chốt và được phép
  tính lại hợp lệ mỗi đêm** ⇒ alert dương-tính-giả đều đặn. 45 ngày lịch (≥26 phiên kể cả tuần
  Tết) nằm **trọn trong vùng đã chốt**.
- **`RESTATE_ALERT_THRESHOLD=0`** (mặc định 5). Ngưỡng 5 được đặt cho **thời** `bq load
  --replace`, khi churn nền 0-4 phiên/đêm là chuyện thường ngày. Với publish bất biến, kỳ vọng
  ở vùng đã chốt là **đúng 0** — để nguyên 5 thì một bug tương lai ghi đè 1-5 phiên đã chốt sẽ
  bị guard **làm ngơ**, tức lưới an toàn có lỗ rộng 5 phiên đúng ở chỗ nó phải bắt. Guard so
  `n_total <= THRESH` nên 0 = alert khi có **bất kỳ** phiên đã chốt nào đổi/thêm/mất.

⇒ Guard trở lại đúng vai trò: **dây bẫy chỉ kêu khi có BUG** ghi đè phần đã chốt.
(`restate_guard.sh` **không sửa** — chỉ truyền env, đã có sẵn `${RESTATE_ALERT_THRESHOLD:-5}` /
`${RESTATE_LOOKBACK_DAYS:-30}` ở dòng 43-44.)

**Step [12]** — `publish_gated_state.py` giờ `exit != 0` khi hỏng → caller **alert (Telegram +
Trading Daily) nhưng KHÔNG `die`**. Lý do có chủ đích: step [14] `macro_healthcheck` phải chạy —
health report đứng im sẽ khiến `get_gated_state()` fail-closed về **DT4**, tức **BỎ macro cap**,
tức **kém phòng thủ hơn**. Bảng giữ bản hôm qua ⇒ `bq_freshness_check` chặn hạ nguồn đúng thiết kế.

### 4.2 `deploy_golive_dt5g_v4/publish_gated_state.py`

1. **`bq load --replace` → `publish_immutable(out, ...)`** (nhận DataFrame trực tiếp, không qua
   file — case I của self-check đi đúng đường này).
2. **Đảo thứ tự ghi CSV**: trước đây ghi `LOCAL_CSV` từ chuỗi **vừa tính lại** rồi mới publish
   (CSV và BQ luôn khớp vì cả hai đều là bản mới). Với publish bất biến thì **không còn vậy**:
   BQ giữ lịch sử **đã chốt**, `out` chứa lịch sử **đã bị restate**. Ghi `out` ra CSV sẽ tạo hai
   nguồn lệch nhau cho cùng một chuỗi — và lệch đúng ở phía sai: **~7 script nghiên cứu/backtest**
   đọc **trực tiếp** CSV này làm chuỗi DT5G (`f_sleeve_pt.py`, `crisis_release.py`,
   `f_protect_v4v5_test.py`, `f_system_improve_test.py`, `f_fast_hedge_test.py`,
   `test_crisis_release_nav.py`, `analyze_vix_peak_bottom.py`) — chính là nhóm consumer **cần
   point-in-time nhất**.
   ⇒ **Giờ: publish trước, rồi `export_published_csv()` TỪ BQ** ⇒ CSV == bảng công bố, các script
   kia **tự động** nhận chuỗi đã chốt, **không phải sửa file nào**.
   > **Đính chính (quant-skeptic bắt, tôi đã tự xác minh)**: chỉ **6/7** script thực sự đang đọc
   > được file này. `analyze_vix_peak_bottom.py:20` dùng path kiểu Windows
   > `f"{WORKDIR}\\vnindex_5state_dt5g_live.csv"` — dấu `\` là ký tự thường trên Linux, file đó
   > **không tồn tại** (`ls` xác nhận; bản thật ở `data/`). Đây là **bug có sẵn**, không do diff
   > này gây ra và cũng không được diff này sửa — ghi lại thành việc nhỏ riêng (§7), không sửa
   > kèm ở đây vì ngoài phạm vi và cần verify riêng.
   Publish hỏng ⇒ **không ghi CSV** (giữ bản cũ, vẫn khớp BQ). Không bao giờ để CSV chạy trước BQ.
   Schema CSV giữ **nguyên 3 cột** `[time,state,state_raw]` — `asof_date` là cột audit, chỉ sống
   ở BQ (đổi schema CSV sẽ đụng 7 consumer trên).
3. **`exit 1` khi publish hỏng** (trước: chỉ in `WARNING` rồi `exit 0` ⇒ **thất bại lặng lẽ**).
   `data/golive_dt5g_state.json` thêm field `bq_publish_ok`.

---

## 5. Lưu ý vận hành

- **`RESTATE_LOOKBACK_DAYS=45`** là **hệ quả bắt buộc** của `SEAL_N=25`, không phải tuning. Nếu
  sau này đổi `SEAL_N`, phải đổi lookback tương ứng (quy tắc: lookback ngày lịch > `SEAL_N` phiên
  giao dịch quy đổi, có đệm cho Tết).
- **`SEAL_N` là ngữ nghĩa công bố** — đổi cần **user duyệt**, không phải tham số tinh chỉnh.
- Từ nay `n_sealed_diff > 0` trong `data/immutable_publish_history.jsonl` = **bằng chứng upstream
  đã restate dữ liệu quá khứ** (không còn là sự cố im lặng). Cần bản mới cho nghiên cứu →
  `snapshot_vintage()`, **đừng đè bảng công bố**.
- `restate_guard.sh` vẫn giữ nguyên vai trò **lưới an toàn dự phòng** — module này chặn từ gốc,
  guard bắt trường hợp có bug tương lai vượt qua được chặn đó.
- **Rủi ro mô hình = 0**: không đổi một dòng công thức tính state nào; case B của self-check
  khẳng định đuôi == chuỗi tính theo công thức cũ byte-for-byte.

---

## 6. File thay đổi

| File | Trạng thái |
|---|---|
| `state_publish_immutable.py` | **MỚI** (384 dòng) |
| `immutable_publish_selfcheck.py` | **MỚI** (24 assertion, sandbox `_ipsc_*`) |
| `daily_refresh_v34b_linux.sh` | sửa step [10], [11b], [12], [12b] |
| `deploy_golive_dt5g_v4/publish_gated_state.py` | publisher mới + đảo thứ tự ghi CSV + `exit 1` khi hỏng |
| `data/immutable_publish_history.jsonl` | telemetry (mới, append-only) |

---

## 7. Review quant-skeptic — **CONFIRMED (medium)**

Log đầy đủ: `mike/logs/verify_20260730_030147.log`.

Reviewer **tự tái lập độc lập** 3 việc (không tin payload): (1) python recompute trên
`immutable_publish_history.jsonl` → 52/52 `sealed_immutable=true`, lần ghi production duy nhất
`n_sealed_diff=0`; (2) grep log self-check → 24 PASS / 0 FAIL; (3) `bq show --schema` xác nhận
`asof_date` **thật sự** đã có ở `vnindex_5state` production. Cũng xác nhận `SEAL_N=25` khớp chính
xác `_dt_4gate(..., enC=25, ..., enX=25, ...)` ở `macro_state_live.py:104`, và **không có** cột
forward-looking nào bị chạm. Ghi nhận finding **không overclaim**: `dt5g_live` chỉ chạy sandbox,
đã khai báo rõ.

**Killer objection (thật, đã xử lý ngay)**: publisher thêm cột `asof_date` vào `vnindex_5state`,
mà step [11] `CREATE OR REPLACE ... AS SELECT *` (diff gốc **không** đụng tới) sẽ lan cột đó sang
`_v34b_clean` — bảng ~50 consumer chưa ai audit giả định số cột — ngay **lần đầu chain thật chạy**,
tức **sau** commit. Tôi đã tự xác minh đúng (4 cột vs 3 cột) và **áp dụng luôn** cách sửa reviewer
đề xuất là đơn giản nhất: ghim 3 cột tường minh ở step [11] (§4.1), verify bằng probe sandbox.
Đây là dọn hệ quả do chính thay đổi này sinh ra, nên nằm trong phạm vi.

**Ba khuyến nghị còn lại** (không chặn commit):
1. ~~grep ~50 consumer `_v34b_clean`~~ → **không cần nữa**: đã chặn tại nguồn ở step [11], cột
   audit không bao giờ tới bảng đó.
2. **Theo dõi sát lần chạy cron THẬT đầu tiên** của chain mới (step [10]→[11]→[11b]→[12]→[12b]) —
   self-check chỉ kiểm từng mảnh + 1 lần ghi thật vào bảng base, **chưa** chạy trọn chain E2E.
   Đây là việc còn treo, phải theo dõi chủ động (không chờ user báo).
3. `analyze_vix_peak_bottom.py:20` path Windows hỏng — **bug có sẵn**, việc nhỏ riêng, không sửa
   trong diff này.

Hai điểm reviewer nêu về **độ chính xác của báo cáo** (số telemetry 43→52; claim "7 script") đã
sửa trong chính file này (§3.1, §4.2).

Điểm reviewer **không tự tái lập** (khai báo minh bạch): chân dưới của `SEAL_N` (độ sâu viết-lại
`min_stay_filter` ≤5 phiên) — cần chạy lại script đo offline. **Không binding**, vì 25 đã trội
gấp 5× con số đó.

**Không có câu hỏi thiết kế nào bị escalate** (reviewer xác nhận cơ sở `SEAL_N=25` bằng grep trực
tiếp) ⇒ đủ điều kiện commit theo hướng dẫn dispatch.
