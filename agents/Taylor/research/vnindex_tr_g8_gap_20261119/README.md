# Vá điểm mù G8 + kiểm dòng sealed rộng hơn — `vnindex_total_return.py` (job Taylor_20261119_080122)

Commit hiện hành **`60a54a051`** (vòng 4 do Mike vá, lib + selfcheck; trước đó `f7cdf9a22` vòng 3; vòng 1 `48d4a8d07`, vòng 2 `905745fbb`; commit `ff130d986` của Mike
là `fund_bench_cron`), nhánh `session/vnindex-tr-g8-gap-20261119`, worktree `agents/Taylor/wt-vnindex-tr-g8-gap-20261119`.
**CHƯA merge.** Tôi không chạy `--update` và không ghi gì vào
`data/benchmark/`: md5 chuỗi canonical vẫn là `fe3fe42f…` trước và sau khi replay (`replay_result.json`).
Nguồn: README `vnindex_tr_g5_drift_20261119`, mục Khuyến nghị 2 và 3.

## Diff tóm tắt (`git diff --numstat`: +113/−10 lib, +152 selfcheck)
- **G8_NEW** (nhánh mới, G8 cũ giữ nguyên). Bắt mã nằm trong bảng sàn HOSE phiên t mà không vào rổ, theo hai nhánh:
  - `osh`: mã có giá ở t-1 và t, nhưng `OShares` rỗng trong K=11 phiên chỉ số cuối tới t-1 (cửa sổ cố định, xem vòng 3).
  - `row`: bảng `ticker` chưa từng có dòng nào của mã, tính tới t. Nhánh này dựa vào `first_seen`, một
    query mới trong `fetch_bq`: `MIN(time)` theo mã trên toàn bảng, dry-run **54.285.126 byte**/lần.
  - Ngưỡng chống nhiễu `G8_NEW_MIN_SESSIONS = 5`. Nhánh `osh` cần ≥5 phiên có giá; nhánh `row` cần mã đã niêm
    yết ≥5 phiên của chỉ số.
  - Thông báo lỗi nêu tên mã, nguyên nhân và đúng giá trị đã đọc (số phiên có giá, hoặc ngày niêm yết).
- **Lưu trữ:** token nằm sau dấu `|` trong cột `osh_missing_ticker`, dạng `"<mã G8 cũ>|DMX:osh:72;GEL:row:2026-02-06"`.
  Cách này không đổi danh sách cột (hợp đồng `COLUMNS`), và dòng sealed cũ giữ nguyên byte. Hệ quả: **chỉ dòng
  được dựng SAU khi merge mới có thông tin G8_NEW**; dòng đã sealed thì không.
- **Ack:** thêm mục `G8_NEW` trong `vnindex_tr_acks.json`, gồm `{date, ticker, cause: osh|row, confirmed_by, reason}`.
  - Khoá là `(date, "@G8_NEW:<mã>:<cause>")`, không trùng khoá G6.
  - Khi nguyên nhân đổi (`row` → `osh`), G8 nổ lại.
  - Tôi không thêm ack nào vào file thật.
- **VERIFY_SEALED:** khi dòng sealed dựng lại có `n_members` hoặc `mc_members_vnd` lệch > 0,3%, script in
  CẢNH BÁO ra stderr và thêm `sealed_drift_warnings` vào JSON `--update`. Nó không chặn, không đổi rc và
  không viết lại phần sealed.

## Đo tần suất báo trên toàn chuỗi 2026 (217 phiên; `measure.py`, `measure_window.py`, `cand_*.csv`)
| Quy tắc | Mã bị báo | Ghi chú |
|---|---|---|
| `osh` (≥5 phiên có giá) | BCG (01-05→06-18), TCD (01-05→07-14), VMD (01-05→10-23), DMX (08-12→11-18) | BCG, TCD, VMD từng có OShares (2449/1997/3786 dòng) nhưng rỗng suốt 2026 ⇒ lỗ hổng thật |
| `row` + `first_seen` (≥5 phiên niêm yết) | CRV, GEL, HPA (cả năm), DSH (từ 10-30), DVV (từ 11-06) | 0 dòng trong `ticker` toàn bảng |
| `row` theo cửa sổ 11 phiên (**BỊ LOẠI**) | 22 mã (thêm BTT, LGC, TTE, DRH, PNC…) | mã ngừng giao dịch ⇒ nhiễu, nên phải dùng `first_seen` |

- Mã nhỏ không khớp lệnh (40/408 mã ngày 11/11) **không vào nhánh nào**: có dòng trước đó ⇒ không phải `row`;
  không có giá t-1/t ⇒ không phải `osh`.
- Cả 9 mã bị báo đều là lỗ hổng dữ liệu thật. Không có ca báo oan nào.
- Nhưng **217/217 phiên năm 2026 có ≥1 mã bị báo** (CRV vắng cả năm). Nếu áp ngược cho cả chuỗi thì mọi kỳ
  báo cáo 2026 đều "chưa có số", trừ khi BQ lấp dữ liệu hoặc có ack.

## Chạy thật (replay trong bộ nhớ; `replay.py` → `replay_result.json`, `series_replay.csv`)
`--update` trên bản sao bị bộ phân loại quyền chặn, vì nhiệm vụ cấm `--update`. Tôi thay bằng cách dựng lại
trong bộ nhớ bằng `_rebuild` + `_merge_lines`, cùng logic với `--update`. Đầu vào là cache BQ
`bq_inputs_20251103.pkl` kéo 19/11, nên có thể không trùng byte với lần chạy cron.
- Cửa sổ dựng: mốc 2026-11-04, dựng lại 10 dòng; 0 dòng bị giữ seal.
- G8_NEW nổ ở **6 mã × 5 phiên** (11/12, 11/13, 11/16, 11/17, 11/18): **CRV, GEL, HPA, DSH, DVV** (row) +
  **DMX** (osh). LPS không bị báo (OShares đã đủ).
- **Kỳ 2026-11-06→11-18:** G5 có 1 lỗi, cũ và mới giống hệt (không hồi quy). G8 mới có 30 lỗi. Trạng thái đã
  `unavailable` từ trước (vì G5), ô giá −1,295% không đổi.
- **Kỳ 2026-11-12→11-18:** trước đây **ok** (giá −1,83%, TR net −1,82%), nay **chưa có số** do 24 lỗi G8
  (6 mã × 4 phiên). Ô giá vẫn −1,83%.
- **VERIFY_SEALED** có 2 cảnh báo thật: `2026-11-05 n_members 363 → 367 (+1,102%)` và
  `2026-11-06 353 → 355 (+0,567%)`. `mc` không lệch quá 0,3%, nên nhiều khả năng đây là dòng mã thanh khoản
  thấp vào BQ muộn chứ không phải dấu vết kiểu LPS. Xem quyết định (4).

## Hệ quả với báo cáo SpaceX/ZaloPay (đã sửa vòng 2, 19/11)
- **G5 + G8 KHÔNG còn được waiver Q9.** `period_table_32._q9_waiver` chỉ được gọi khi `_g5_only(reason)` và ô ghi
  `chưa có số (G5…` (`period_table_32.py:524-534`); `data/q9_waivers.json` chỉ có hai waiver theo TÊN FILE cho G5 đơn lẻ
  (`SpaceX/ZaloPay_weekly_report_2026-11-09_to_2026-11-13`, hết hạn 11/20). Lý do CLI có thêm `G8:` ⇒ không phải G5-only
  ⇒ `TableBlock` (weekly/monthly CHẶN gửi).
- **Sau merge, lần `--update` đầu dựng lại các dòng provisional ≥ 11/12 kèm token.** Kỳ báo cáo nào có phiên ∈ [11/12, nay]
  mà CHƯA có ack G8_NEW thì ô "VN-Index có cổ tức" = `chưa có số` và report bị chặn:
  | Kỳ | Chặn bởi |
  |---|---|
  | weekly 11/09→11/13 (đã gửi, waiver G5 hết hạn 11/20) | G5 (đã waiver) + **G8 11/12, 11/13** ⇒ gửi lại/kiểm lại sẽ BLOCK |
  | weekly 11/16→11/20 (anchor 11/13) | **G8** (6 mã × 4–5 phiên) — kỳ chuyển từ "có số" sang "chặn" |
  | mọi weekly/monthly sau đó cho tới khi BQ lấp hoặc hết hạn ack | G8 |
  | tháng 11 + "từ khi bắt đầu hoạt động" (SpaceX 07-01, ZaloPay 07-06) | G5 11/11 (sẵn có) + **G8** |
  Replay: kỳ 11/12→11/18 **không ack ⇒ `chưa có số`** (giá −1,83%); **nạp ack đề xuất vào file ack TẠM ⇒ CÓ SỐ**
  (TR net −1,82%, giá −1,83%) — `replay_result_r2.json`. Kỳ 11/06→11/18 vẫn `chưa có số` vì G5 (ack không chữa G5).
- Mọi ô chỉ số GIÁ không bị ảnh hưởng.

### Ack ĐỀ XUẤT cho user duyệt (KHÔNG ghi vào `data/benchmark/vnindex_tr_acks.json`)
Khoảng `date_from = 2026-11-12` (ngày đầu G8_NEW nổ), `date_to = 2026-12-27` (= +45 ngày; sau đó cổng tự nổ lại nếu BQ
vẫn chưa lấp). `decided_by:"user"`, `confirmed_by` = người duyệt.
| Mã | cause | date_from | date_to | Bằng chứng (đọc 19/11) |
|---|---|---|---|---|
| CRV | row | 2026-11-12 | 2026-12-27 | `ticker` 0 dòng toàn bảng (niêm yết 2025-10-10) |
| GEL | row | 2026-11-12 | 2026-12-27 | 0 dòng (niêm yết 2026-02-06) |
| HPA | row | 2026-11-12 | 2026-12-27 | 0 dòng (niêm yết 2026-02-06) |
| DSH | row | 2026-11-12 | 2026-12-27 | 0 dòng (niêm yết 2026-10-26) |
| DVV | row | 2026-11-12 | 2026-12-27 | 0 dòng (niêm yết 2026-11-02) |
| DMX | osh | 2026-11-12 | 2026-12-27 | có giá 72 phiên, OShares rỗng (G5-drift: Winston lập OShares) |
Lưu ý: ack chỉ nói "đã biết, chờ BQ lấp" — không chữa sai số (y thiếu vốn hoá 6 mã). Khi BQ lấp, `--update` tự xoá token;
nếu DMX được lấp OShares nhưng CRV vẫn trống thì chỉ ack row còn hiệu lực. Ack `osh` không che `row` và ngược lại.

## Selfcheck + mutation
- `vnindex_total_return_selfcheck.py`: **295 assertion PASS** (trước vá: 267), chạy đủ 3 môi trường
  `env -u TZ`, `TZ=Asia/Tokyo`, `TZ=America/Los_Angeles`. Selfcheck import từ `HERE` (bin của worktree).
  - Case mới: mã chỉ có giá ⇒ nổ; mã 0 dòng ⇒ nổ; mã niêm yết muộn chưa đủ 5 phiên ⇒ không nổ.
  - Mã nhỏ không giao dịch (QUIET, FFF) ⇒ không nổ; có `first_seen` trước cửa sổ ⇒ không nổ.
  - Ack đúng ⇒ hết nổ; ack sai nguyên nhân hoặc sai ngày ⇒ vẫn nổ; ack hỏng ⇒ ValueError.
  - Ô giá vẫn có số khi chỉ G8 nổ.
  - Lệch sealed > 0,3% ⇒ cảnh báo, không ném lỗi, không đổi byte sealed. CLI vẫn rc=0 và in cảnh báo ra
    stderr và stdout.
- `mutate.py` → `mutation_result.txt`: **7/7 mutant ĐỎ, 0 sống sót**. Các mutant: bỏ token osh, bỏ token row,
  cổng bỏ qua g8_new, bỏ ngưỡng N, bỏ first_seen, bỏ ack, bỏ cảnh báo drift.
- Pre-commit đã qua: tz-anchor-gate, ruff ratchet, commit-collision, discord-id, utc-text. ShellCheck skip vì
  không có file `.sh`.

## Vòng 2 (19/11, job Taylor_20261119_084930) — đã làm đủ 8 mục arch-review
1. Ack khoảng ngày `{ticker, cause, date_from, date_to|expires, confirmed_by, decided_by:"user", reason}` (≤90 ngày, fail-closed,
   không wildcard, đổi cause/hết hạn ⇒ nổ lại); dạng từng ngày cũ giữ nguyên. 2. G8_NEW vào `seal_blockers` (+ thông báo theo status).
3. Panel kéo lùi 30 ngày (`bq_panel_start`) + assert lúc import + selfcheck restate/update (chỉ đảm bảo panel PHỦ đủ; việc phân loại
   độc lập mốc dựng thực sự nằm ở vòng 3 dưới đây — vòng 2 chưa đạt, arch-reviewer bắt được).
4. `fund_bench_cron.sh` báo `g8_new_open` / `sealed_drift_warnings`, dedupe 1 tin/ngày/tập mã. 5. MB, MD bị diệt (mutate.py 16 mutant: 0 sống sót,
   `mutation_result.txt`). 6. VERIFY_SEALED: mc > 0,3% HOẶC n ≥ 2% (replay 11/05 +1,10%, 11/06 +0,57% ⇒ KHÔNG nổ; `sealed_drift_warnings: []`).
   7. `kb/data_registry/price-volume/vnindex_total_return.md.proposed` (trong nhánh). 8. README này.
Selfcheck: 342 assertion × 3 TZ; nav_period_benchmark 69, period_table_32 159, fund_bench_cron 27 — PASS.

## Vòng 3 (19/11, job Taylor_20261119_091916) — điểm 3: nhánh `osh`/G8 cũ KHÔNG phụ thuộc cửa sổ dựng (nhánh `row` xem vòng 4)
Lỗi vòng 2: `S1_ff` ffill từ đầu panel ⇒ cùng phiên t, mốc dựng cách t 3–7 ngày ra token `XOSH:osh`, cách 14–21 ngày ra G8 cũ
(`osh_missing_ticker=XOSH`) ⇒ dòng bị seal dạng G8 cũ và `--restate-sealed` sau đó bị từ chối.
- Sửa (`div_yield_daily`): OShares ffill **tối đa `G8_NEW_K = 11` phiên chỉ số** (lưới phiên dày, `ffill(limit=K)`), số phiên có giá
  (`npx`, giá trị trong token `osh:<n>`) = đếm trong K phiên cuối tới t (≤ K). Cùng K cho cả hai phân loại: có OShares trong K
  phiên ⇒ G8 cũ (ngữ nghĩa cũ giữ); mất > K phiên ⇒ `osh` G8_NEW. Vị trí phiên lấy từ VNINDEX của TOÀN panel
  (`sess_full`), không phải `idx` đã cắt ở mốc dựng.
- Điều kiện: panel phủ K phiên trước mốc dựng — assert import `G8_NEW_LOOKBACK_DAYS ≥ ⌈K·7/5⌉ + G1_MAX_GAP_DAYS` (30 ≥ 16+14).
  Ngoài phạm vi đó (panel ngắn hơn) cửa sổ bị cắt như cũ.
- Hệ quả đã biết: mã mất OShares > 11 phiên giờ là `osh` (trước: G8 cũ theo ngưỡng vốn hoá 0,5% nếu có OShares xa hơn); mã mất ≤ 11 phiên
  vẫn G8 cũ. Đây là ranh giới cố ý, cố định.
- Selfcheck mới `t_g8_window_independent` (probe của reviewer: OShares mất ~42 ngày trước t; mốc dựng cách t 3/7/14/21 ngày ⇒ cùng
  `LOSTO:osh:11`; `RECENT` mất 4 phiên ⇒ G8 cũ ở mọi mốc). **353 assertion** PASS × 3 TZ (`env -u TZ`, Asia/Tokyo, America/Los_Angeles).
- `mutate.py`: 20 mutant (thêm M15 ffill không giới hạn K, M16 npx cộng dồn, M17 `sess_full` bỏ, M18 thông báo restate), **0 sống sót**.
- Thông báo lỗi G8_NEW khi ĐANG `--restate-sealed` (`seal_blockers(..., restating=True)`) không còn khuyên chạy chính lệnh đó: nói dữ liệu BQ
  hiện tại vẫn thiếu mã ⇒ cần ack G8_NEW (ưu tiên theo khoảng ngày) hoặc chờ BQ lấp rồi mới restate.
- Replay trên dữ liệu thật đã chạy lại ở vòng 4 (xem dưới) — kết quả thay cho "ước lượng" của vòng 3.

## Vòng 4 (19/11 16:54, Mike tự vá theo arch-review vòng 3, user duyệt phương án A)
arch-reviewer vòng 3: NEEDS_CHANGES nhẹ. Đã xử lý (commit `60a54a051`):
- **Nhánh `row` độc lập mốc dựng.** Trước: số phiên đã niêm yết đếm trên `idx` bị cắt ở mốc dựng ⇒ mã niêm yết trước mốc ⇒ `listed=None`
  ⇒ nổ oan (thật: DVV 2026-11-05, mới niêm yết 4 phiên, ra token `row` ở mốc 11-04, không ra ở mốc khác; hại ở `--restate-sealed`
  vì mốc = dòng liền trước). Nay đếm trên lưới phiên ĐẦY ĐỦ `sf` (`sess_full`): `listed = sf.searchsorted(t) − sf.searchsorted(st) + 1`.
- **Selfcheck ranh giới K** (`t_g8_window_independent` mở rộng; mốc dựng cách t 1/3/7/14/21 ngày): `B_K` (OShares cuối ở D[44−K]) ⇒ G8 cũ,
  `B_K1` (D[43−K]) ⇒ `osh`, `NEWT` (OShares chỉ TỪ t) ⇒ `osh` (S1_ff không nhìn t), `LATEL` (niêm yết 3 phiên) ⇒ KHÔNG nổ,
  `LATEOK` (8 phiên) ⇒ nổ. Mutant kiểm tay: `ffill(limit=K−1)`, `ffill(limit=K+5)`, bỏ `shift(1)`, `row` theo `idx` cắt, `listed >= N → > N`
  ⇒ 5/5 ĐỎ. **355 assertion** PASS × 3 TZ.
- **Thông báo osh (§29)** sửa thành "có giá {val}/{K} phiên chỉ số cuối tới t nhưng OShares rỗng trong {K} phiên tới t-1".
- **Replay dữ liệu thật** (cache `bq_inputs_20251103.pkl`, mốc dựng 2026-11-04, bản dựng trong `/tmp`, KHÔNG ghi `data/benchmark/`;
  md5 chuỗi canonical vẫn `fe3fe42f…`): 6 mã × 5 phiên (CRV, GEL, HPA, DSH, DVV = `row`; DMX = `osh`, số phiên 68–72 → **11** do K cố định),
  số lỗi G8 kỳ 11-12→11-18 = 24 và kỳ 11-06→11-18 = 31, **giống hệt vòng 2**; `seal_blocked` và `sealed_drift_warnings` đều rỗng.
- **Hệ quả ngưỡng 5/11 phiên đã biết:** mã vừa quay lại giao dịch chưa đủ 5 phiên có giá trong 11 phiên cuối thì im lặng (vd TCD
  2026-07-06→07-08, mã quay lại ngày 07-03); vòng 2 (cửa sổ dựng) có báo. Chấp nhận: đây là chống nhiễu mã nhỏ.

## Thứ tự triển khai (user duyệt 19/11 16:18)
1. Merge nhánh **CÙNG LÚC với ack 6 mã** CRV/GEL/HPA/DSH/DVV/DMX, `date_from 2026-11-12` → `date_to 2026-12-27` (ack theo khoảng ngày,
   `decided_by:"user"`) — không merge trước ack, nếu không mọi kỳ có phiên ≥ 11/12 thành `chưa có số` và report bị chặn.
2. Sau merge: `--update` thật (dựng lại provisional ≥ 11/12 kèm token; có ack ⇒ cổng không nổ). Không `--restate-sealed` nếu không cần.
3. Việc song song: nhờ bq_admin/Winston lấp dữ liệu 6 mã; khi BQ lấp thì `--update` tự xoá token, ack hết hạn 12/27 tự nổ lại nếu chưa lấp.

## Quyết định còn cần user
Các mục 1/2/4 cũ đã đóng ở vòng 2 (ack khoảng ngày ĐÃ làm; ngưỡng VERIFY_SEALED đã đổi thành mc > 0,3% HOẶC n ≥ 2%).
1. **User đã duyệt hướng 19/11 16:18 và duyệt phương án A (Mike vá) 16:54; đang chờ arch-review/audit xác nhận `60a54a051` rồi merge** (kèm `ff130d986`) theo thứ tự trên; ack 6 mã nạp vào `data/benchmark/vnindex_tr_acks.json`
   cùng lượt (tôi không sửa file thật).
2. **Ngưỡng trọng yếu (chưa quyết):** chưa suy được vốn hoá mã thiếu OShares ⇒ mã nào cũng bị báo. Phương án: nối vốn hoá ngoài (VNDirect)
   để chỉ báo mã ≥ 0,5% rổ như G8 cũ. Cần quyết có nối nguồn ngoài không.
3. **Hợp đồng dữ liệu:** token lưu sau `|` trong `osh_missing_ticker` thay vì thêm cột. Cần cập nhật
   `kb/data_registry/price-volume/vnindex_total_return.md` (§13: `.proposed` đã có trong nhánh; Winston hoặc Mike duyệt).
