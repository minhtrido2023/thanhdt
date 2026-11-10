# Job Taylor_20261110_103537 — lagcache VÒNG 2 (arch-review NEEDS_CHANGES) — PAPER/NON-CANONICAL
Nhánh `session/lagcache-1110` (worktree `/home/trido/thanhdt/wt-lagcache-1110`): `fbeece879` → `b49fe7b76` → `49e70d6df`
(trên `b161f3242` vòng 1). **KHÔNG merge main. KHÔNG áp vào pkl canonical.** Thay `../backfill13/` (SUPERSEDED, xem `../backfill13/SUPERSEDED.md`).

## Sửa theo REQUIRED CHANGES
| # | Việc | Kết quả |
|---|---|---|
| 1 | `raw_basis` bỏ heuristic tự chế | Giá thô: `ticker_1m.Price` ưu tiên (Open×Price/Close của ticker_1m); ngoài phủ ⇒ `ticker.Price` trừ dòng GDKHQ kẹt hệ CUM theo detector registry: **bắt buộc exright_date trong corporate_action** + bước điều chỉnh thật (>2%) chiều pha loãng (r_prev>r_next≥0,98) + chưa sang hệ mới + còn kẹt hệ cũ (Price==T−1 hoặc r≈r_prev). Sửa = Close×r_next, Open×r_next. Không biết hệ mới ⇒ `unresolved`, không ghi. Chữ ký "Price đứng yên, Close đổi" KHÔNG dùng đơn lẻ (DRI 09-21: nhiễu hệ số vendor ở phiên liền trước GDKHQ cho cùng chữ ký). |
| 1 | ticker_1m có phủ không? | `tav2_bq.ticker_1m` + `data/bq_cache/ticker_1m.parquet`: đầy đủ (≥790 mã/phiên) chỉ từ **2026-10-12** ⇒ phủ cửa sổ daily K=10, KHÔNG phủ 13 phiên backfill (06–09) ⇒ backfill dùng detector. |
| 2 | `merge_window` fail-safe | Dòng cũ lệch >2% mà không giải thích được ⇒ GIỮ cũ + log + exit 1. Giải thích được = src t1m/exfix, hoặc dòng cũ trùng `ref_adj` (giá đã điều chỉnh — ca DIG 09-07) hoặc `ref_prev` (giá thô phiên trước — fetch khi BQ chưa chốt, ca VIC 07-16). Dòng thiếu vẫn điền. |
| 3 | selfcheck fixture BQ thật + mutation | `lagged_cache_patch_selfcheck.py`: **45/45 PASS**; `--mutate` (sandbox /tmp): **19/19 bị bắt** (11 mutation reviewer liệt kê + 8: window +1, Open stale hệ cũ, guard dilutive, bắt buộc corporate_action, guard kẹt hệ cũ, median, fail-safe, ref_*). Fixture: VHM 08-04..07 (hệ số 2), TRC 09-14..16, DRI 09-07..10 + 09-18..23, DIG 09-04..09, stale-CUM phiên đi ngang (FLT), r_next≠1 (NXT), HBC/STP/OFF/OTH. |
| 4 | test tích hợp | `refresh_lagged_caches_selfcheck.py` (stub bq + LAGCACHE_WORKDIR sandbox): **14/14 PASS** — phiên thưa ⇒ exit 1; ngoài cửa sổ md5 giữ; .prev tạo + = bản trước; không sót .tmp; nguồn đủ ⇒ lành exit 0; K=0/31/abc ⇒ exit 2 không ghi; lock bận ⇒ exit 3; phiên thưa sắp trôi ⇒ đúng 1 notify + 1 bus Winston; ca rỗng ⇒ exit 1; GDKHQ kẹt CUM trong pkl được sửa. |
| 5 | K | `1<=K<=30`, ngoài ⇒ exit 2 trước khi đọc/ghi gì; `window_start` cũng raise. |
| 6 | ghi file | `tempfile.mkstemp` cùng thư mục + fsync file + fsync thư mục + `os.replace`; `fcntl.flock` cả script (`data/.refresh_lagged_caches.lock`, LOCK_NB ⇒ exit 3); tmp xoá khi lỗi. |
| 7 | depth-check | so số mã/phiên pkl với nguồn vừa fetch (cùng universe pkl) ⇒ `source_thin` vs `cache_thin`; phiên thưa ở MÉP cửa sổ (sắp trôi) ⇒ MỘT cảnh báo riêng: `notify.sh` + `append_event.sh Winston error lagcache-thin-session-expiring` (override NOTIFY_BIN/APPEND_EVENT_BIN cho test). Câu "sẽ tự lành" đã sửa (chỉ lành nếu BQ đủ trước khi trôi; cache_thin = KHÔNG tự lành). |
| 8 | backfill13 dựng lại | dưới đây |
| 9 | docstring/line refs | docstring hết "incremental append"; `lag_liquidity_filter.py:134` 733→736 (đã sửa trên nhánh). `mike/bin/asof_label_selfcheck.py:46` 777→780 **nằm ở repo mike** ⇒ CHỈ sửa khi nhánh merge (main hiện vẫn 777 đúng). |

**Lỗi thật bắt được nhờ E2E BQ thật** (không có trong review): `corporate_action` KHÔNG có trong `BQ_LOCAL_CACHE`
(`wc_env.sh` bật cache cho mọi `bq()`) ⇒ bản đầu crash. Nay query riêng đi BQ thật (`_bq_live`), lỗi ⇒ rỗng ⇒ exit 1.
E2E trên bản sao pkl (`/tmp/lagcache_e2e_r2`, `env -u TZ`): rc=0; ngoài cửa sổ md5 giữ nguyên (px+ov); cửa sổ 7.812 dòng cũ
+163 dòng mới; 7 dòng Close đổi >0,1% (max 7,84% — VCP 10-27/28 theo ticker_1m, log "sửa"); canonical không đổi.

## backfill13 v2 (`build_backfill13.py`, interpreter `$DNA_PYEXE`, threads=1)
Nguồn pull 2026-11-10: `data/bq_ticker_20260525_now.csv`, `bq_ticker_1m_…`, `bq_corporate_action_20260518_now.csv`, `bq_ticker_hilo_…` (md5 ở `MD5.txt`).

| artifact | md5 |
|---|---|
| `earnings_px_bf13v2.pkl` | `497494391360ff4ba49eea1c9ced61fa` |
| `lagged_pos_ov_bf13v2.pkl` | `34d91f4c5b92d6cf39b9828897ce5243` |
| canonical lúc dựng (px / ov) | `af4b8c1b72f4b133248516eff8b459b0` / `afb2484e5fb702cd4335949d1a69db1b` |

Đối soát (`recon.txt`):
- Dòng ngoài 13 phiên: giữ nguyên (px+ov `True`). Min mã/phiên từ 06-01: 665.
- **11.699 dòng gap mới vs BQ `Price`: 0 dòng lệch >0,1%.** Nguồn: 12.046 `price`, 6 `t1m`, 0 `exfix` (trên 13 phiên không có GDKHQ kẹt CUM).
- Fail-safe mặc định trên 13 phiên: 24 dòng cũ bị giữ + 5 được sửa (ref_prev). **24/24 dòng cũ nằm TRONG biên [Low,High]×r của phiên** = giá giữa phiên do fetch lúc BQ chưa chốt (chính lỗi đang vá) ⇒ bản dựng ghi đè 13 phiên với `tol=inf`, có chủ đích, có log. Đối chứng: trên 13 phiên, 30/129 dòng cũ lệch BQ Price >2%.
- So bf13 CŨ: 87 dòng khác >0,1% (147 dòng chỉ-cũ: bản cũ thay nguyên phiên, v2 giữ dòng cũ BQ không có).
- 01/08–27/10, `raw_basis` mới khác BQ `Price` >0,1%: 14 dòng/11 mã = 4 `exfix` (VHM 08-06 77.100, TRC 09-15 21.550, PHR 09-11, SZL 09-16) + 10 `t1m` (ticker_1m sửa lớp "phiên liền trước GDKHQ bị ghi giá đã điều chỉnh": TTT/QPH 10-22, VTH 10-15, BMV 10-12/13…).

## Trước/sau
| chân | pkl | mean12 LAG | verdict | w_LAG (state tốt) | papertrade danh mục | LAG book |
|---|---|---:|---|---:|---:|---:|
| ctrl | canonical, engine cũ | −0,62 | NEGATIVE | 0,50 | −7,15% (46,4262B) | 22,0813B |
| bf13 cũ (SUPERSEDED) | engine cũ | −0,47 | NEGATIVE | 0,50 | −6,55% | 22,3818B |
| bf13 cũ + liq_require_positive (`liq2`) | — | — | — | — | −5,87% | 22,7180B |
| **bf13v2 + liq_require_positive** | v2 | **−0,47** | NEGATIVE | **0,50** | **−5,87% (47,0636B)** | **22,7180B** |

- Edge-health (`edge_health/run_eh.py`, bảng `edge_health/edge_table.csv`, asof 2026-09-23): chuỗi `lag_edge_health` bf13 cũ ≡ v2 (5.505 dòng, 0 khác) ⇒ w_LAG giữ 0,50.
- Papertrade (`engine/pt_bf13v2.py`, log `engine/bf13v2.log`): `bf13v2_transactions.csv`/`_logs.csv` **trùng md5** với `liq2_*` (`ef7d83d5…`/`16a08c58…`) ⇒ 87 dòng sửa không chạm mã/ngày nào được giao dịch trong cửa sổ.
- **Nhãn:** LAG papertrade (pt_v22_dt5g, nhánh này) nay BẬT `liquidity_require_positive` (mirror gate live `cap_lag_orders`); **pin R3 thì KHÔNG** (env `LIQ_ZERO_BLOCK` mặc định tắt — registry mục "2026-07-21 — RE-PIN R3 (SỬA ENGINE: liq<=0 = KHÔNG MUA ĐƯỢC)", việc (a) chạy lại pin với `LIQ_ZERO_BLOCK=lag` còn TREO). Đừng so mắt-thường papertrade LAG với R3.

## Rủi ro tồn dư / phát hiện phụ (không sửa trong job này)
1. Phiên liền trước GDKHQ có `ticker.Price`=Close (r≈1) trong khi r_prev>1,02, NGOÀI phủ ticker_1m: 16 dòng toàn cửa sổ 06-01→, 3 trên 13 phiên thưa. KHÔNG tự sửa vì mơ hồ với exright_date lệch 1 phiên (ca TCB). Trong phủ ticker_1m thì đã đúng.
2. pkl canonical LẪN HỆ GIÁ có từ trước: phiên ≤2026-06-18 là Close ĐÃ điều chỉnh (930/1.240 dòng lệch Price >2% trùng adj Close; 1.170 dòng nằm tháng 6), từ 06-19 là giá thô. Lợi suất cắt ngang mốc này với mã có sự kiện quyền giữa chừng bị lệch. Cần quyết định riêng (owner pipeline).
3. Fail-safe daily giữ dòng ⇒ exit 1 ⇒ `papertrade_daily.sh` đếm FAIL + notify; người kiểm tay quyết định.

## `--apply`
`build_backfill13.py --apply` CHỈ sau arch-review vòng 2 + user duyệt: kiểm md5 canonical + md5 artifact, backup `.pre_bf13v2`, `os.replace`.
