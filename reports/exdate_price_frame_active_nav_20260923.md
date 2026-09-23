# Ex-date: KHỐI LƯỢNG và GIÁ phải cùng MỘT hệ quy chiếu — báo cáo job Taylor_20260923_160958

Nhánh `fix/exdate-price-frame-active-nav`, commit `6b331b37` (worktree `mike/wt-exdate-price-frame`).
CHƯA LAND. Không có lệnh thật nào phụ thuộc: plan 24/09 `approved_by=None`.

## 1. Lỗi (Mike chẩn đoán đúng, đã tái hiện trên dữ liệu thật)

Tối T-1 của GDKHQ, DNSE credit KL mới vào `positions` ngay và hạ `marketPrice` về giá tham
chiếu sau sự kiện, trong khi **giá đóng cửa G1 phiên T-1 vẫn là giá CÒN QUYỀN — và đó là
ĐÚNG** (hôm nay mã vẫn giao dịch có quyền). Hai con số đúng ở hai hệ; nhân chéo thì sai.

| | SpaceX | ZaloPay |
|---|---|---|
| (a) trước sự kiện, tự nhất quán | 1.100 × 27.800 = 30.580.000 | 1.200 × 27.800 = 33.360.000 |
| (b) sau sự kiện, tự nhất quán ← **chọn** | 1.386 × 22.050 = **30.561.300** | 1.512 × 22.050 = **33.339.600** |
| (c) TRỘN — lỗi đã chạy | 1.386 × 27.800 = 38.530.800 | 1.512 × 27.800 = 42.033.600 |
| active_nav phồng | **+7.969.500đ (+0,80%)** | **+8.694.000đ (+1,64%)** |

Chọn (b) chứ không (a): cả hai consumer định cỡ LỆNH CỦA PHIÊN MAI, mà từ mai vị thế thật là
1.386cp ở giá đã điều chỉnh.

## 2. Bản vá

`bin/exdate_frame.py` (mới):
- `verify_post_event_price(px_cum, market_price, multiplier)` — PURE. **KHÔNG tin thẳng
  `marketPrice`**; chỉ nhận khi nó tái tạo được giá cum qua hệ số sự kiện (dung sai
  `max(200đ, 0,5%)` = 2 tick lớn nhất mọi bảng). Lý do: `price_frame.py` §G4 đo được DNSE điều
  chỉnh **theo từng gói vay và KHÔNG nguyên tử** (BID 2026-08-14 mang đồng thời 35.800 đã điều
  chỉnh và 38.850 chưa), mà `get_positions()` gộp lô rồi giữ "marketPrice mới nhất khác None"
  ⇒ bản đọc hỏng trông hoàn toàn lành.
- `classify_positions()` — **tái dùng nguyên** `daily_nav_snapshot.classify_qty_residual` + bộ
  plumbing quanh nó (đã qua 5 vòng arch-review, đo trên 104 cặp phiên/2 account: 12 phần dư,
  12/12 corp-action thật, 0 nhiễu). Không viết lại phép phân loại.

Ba nhánh đúng như spec, không nhánh nào yếu đi:
1. `share_event_credit` + dựng được giá cùng hệ ⇒ đổi giá, `price_source="dnse_position_marketprice_corpaction"`.
2. `qty_unexplained`, **hoặc** credit sớm mà KHÔNG dựng nổi giá cùng hệ ⇒ **rc=6, không ghi file**.
3. còn lại ⇒ giữ nguyên hành vi.

Chỉ áp cho `asof == hôm nay`. `asof` quá khứ dùng `tav2_bq.ticker.Close` (đã điều chỉnh hồi tố,
vốn đã cùng hệ với KL đã credit) — sửa thêm ở đó là chia HAI LẦN.

## 3. Verify — số THẬT

- `bin/exdate_frame_selfcheck.py`: **32/32 PASS** × 4 môi trường (`TZ=Asia/Ho_Chi_Minh`,
  `env -u TZ`, `TZ=America/New_York`, `TZ=UTC`), dưới `$DNA_PYEXE`.
- Mutation, **4/4 chết bằng ASSERTION** (không phải crash), mỗi lần xoá `__pycache__` trước khi chạy:

  | mutation | assertion chết |
  |---|---|
  | `prices[tk] = px_new` → `pass` | E2, E3 |
  | bỏ kiểm dung sai trong `verify_post_event_price` | P3, P9, P10, P12, E7, E8, K3, K4 |
  | bỏ `sys.exit(6)` | E7, E8, U1, U2 |
  | `park_holdings` không sửa giá | K1 |

- Acceptance trên **dữ liệu thật tối 23/09, cả 2 account, `--out` vào tmpdir**:
  SpaceX active_nav 990.981.660 → **983.012.160**; ZaloPay 529.771.109 → **521.077.109** —
  khớp ĐÚNG mức phồng dự đoán (+7.969.500 / +8.694.000). §12: hai account cho kết quả KHÁC nhau.
  `md5sum -c` xác nhận `data/execution_logs/active_nav_{SpaceX,ZaloPay}.json` THẬT **không bị
  ghi đè** trước và sau toàn bộ phiên test.

- §23 quét RỘNG (`grep -rl compute_active_nav` → 29 file): `compute_active_nav_selfcheck` ALL
  PASS · `compute_park_trim_selfcheck` 82/0 · `corp_action_selfcheck` 85/0 ·
  `nav_exdate_forecast_selfcheck` 58/0 · `exrights_price_basis_selfcheck` 38/0 ·
  `nav_corpaction_gate_e2e_selfcheck` 38/0 · `daily_nav_snapshot_from_raw_selfcheck` 64/0 ·
  `money_path_freshness_selfcheck` ALL PASS.
  **KHÔNG chạy** `nav_scripts_2account_selfcheck.py` (gọi DNSE live + ghi đè `nav_history` THẬT).

## 4. Q1 — còn call-site nào khác cùng lớp?

Quét mọi chỗ đọc `openQuantity`/`get_positions()` rồi nhân với giá từ nguồn KHÁC.

| # | Script | Kết luận |
|---|---|---|
| 1 | `compute_active_nav.py` | **ĐÃ VÁ** — mẫu số sizing. |
| 2 | `park_holdings.py` | **ĐÃ VÁ** — `park_mv_vnd` là mẫu số cấp tài khoản của `compute_park_trim` (`:330` dùng `park_mv_vnd`, KHÔNG phải `park_mv_verified_vnd`) ⇒ chỉ gắn cờ UNVERIFIED là chưa đủ. |
| 3 | `report_return_gate.py:126-166` | **CÙNG LỚP, CHƯA VÁ, ngoài phạm vi job này.** qty + `costPrice` từ broker (**cả hai** đã ở hệ SAU), giá từ `bq_close_prices(asof)` = 27.800 (hệ TRƯỚC, BQ đã có dòng 23/09). Đo thật: VPB ra **+26,24% (SpaceX) / +30,97% (ZaloPay)** thay vì +0,13% / +3,88%. Hệ quả thật là **CHẶN OAN**, không phải số sai được công bố: báo cáo lấy % từ `verify_account_snapshot` (đúng, ~+0,1%), cổng tính +26% ⇒ lệch > 0,15pp ⇒ `CHẶN`. Tối nay chưa nổ vì NAV đã bị gate chặn trước nên báo cáo 23/09 không có dòng % của VPB. |
| 4 | `discretionary_accumulation_inject.py:113-125` | **Cùng HỌ nhưng khác dạng** (không nhân giá): `filled_qty = broker_total − baseline` ⇒ KL credit sớm bị tính là "đã khớp". Chỉ ảnh hưởng mã đang có chương trình tích luỹ (DGC/TV1) — VPB không phải. Chưa vá. |
| — | `reconcile_equity.py:288` | **AN TOÀN** — `bp["qty"] × bp["marketPrice"]`, cả hai từ CÙNG bản ghi positions ⇒ tự nhất quán. |
| — | `trading_bot/plan.py:1987` | **Cùng dạng nhưng cửa sổ KHÔNG xảy ra**: `p["total"] × (q.last or q.ref)`. Chỉ chạy ở live preflight 09:05 = ĐÚNG ngày ex-date, khi `ref` đã điều chỉnh ⇒ cùng hệ. (Chiều lệch nếu có: `nav_live` phồng ⇒ preflight YẾU đi, không phải cấp thêm vay.) |
| — | `verify_account_snapshot.py` | AN TOÀN — xem Q2. |
| — | `corp_action_auto_confirm.py`, `daily_nav_snapshot.py`, `nav_exdate_forecast.py`, `compute_park_trim.py` | Không trộn: đọc `openQuantity` để ĐỐI SOÁT (không định giá), hoặc lấy cả qty+giá từ artifact đã vá ở trên. `daily_nav_snapshot` đã có gate riêng (rc=5, đã chặn đúng tối nay). |

## 5. Q2 — vì sao `verify_account_snapshot.py` ĐÚNG mà `compute_active_nav` sai?

`verified_snapshot_SpaceX_2026-09-23.json` ghi VPB qty=1100 × 27.800 = 30.580.000 (tự nhất quán).
**Khác biệt cơ chế: nó KHÔNG lấy qty từ broker.** `:806-810` lấy `qty = raw_agg[tk][0]` —
KL dựng bằng **replay fill từ journal/dnse_raw**, nhân hệ số corp-action theo `corp_actions.json`
(`:118 mult *= a["qty_multiplier"]`, áp theo **ex_date của sổ lịch**, 24/09 ⇒ còn 1,0).
`openQuantity` của broker chỉ vào làm **cross-check** (`select_live_book(..., broker_qty)` + WARN
lệch), không vào phép nhân.

Nên hai script neo vào HAI CÁI ĐỒNG HỒ khác nhau:
- `verify_account_snapshot`: qty theo **đồng hồ sổ lịch** (ex_date) + giá theo **đồng hồ sở**
  (close) — hai đồng hồ này đổi CÙNG lúc ⇒ không bao giờ trộn.
- `compute_active_nav`: qty theo **đồng hồ broker** (credit sớm) + giá theo đồng hồ sở ⇒ lệch
  đúng một đêm.

**KHÔNG bê nguyên sang được, và không nên.** `compute_active_nav` cố ý broker-native (§6: NAV
sống phải phản ánh vị thế THẬT ở broker); thay bằng replay là đổi bất biến của nó và nhập luôn
rủi ro "thiếu fill ⇒ thiếu KL". Bản vá đi chiều ngược lại — kéo GIÁ về đồng hồ broker, không
kéo QTY về đồng hồ sổ — và đó là chiều đúng vì active_nav dùng để sizing lệnh NGÀY MAI.

## 6. Q3 — cửa sổ lỗi

**Đúng: chỉ ĐÊM T-1.** Sang phiên ex-date, `dnse_close_prices`/BQ `Close` đã ở hệ sau sự kiện,
cùng hệ với KL đã credit ⇒ tự lành. Đo được: bản ghi positions 04:51 hôm nay còn 1.100 @
`marketPrice` 28.000 (cum); bản 23:19 đã 1.386 @ 22.050 (post). Cửa sổ mở trong ngày, sau EOD.

**Hai ngoại lệ phải nói rõ:**
1. Nếu DNSE credit sớm **≥2 phiên** trước ex-date, `held_event_next_session` chỉ neo vào phiên
   KẾ TIẾP ⇒ phần dư thành `qty_unexplained` ⇒ **rc=6 fail-closed**, không ra số sai nhưng
   **chặn NAV và cần người**. Chưa quan sát được ca nào; nêu ra để không bị bất ngờ.
2. Call-site #3 (`report_return_gate`) đọc `asof` LỊCH SỬ nên cửa sổ của nó **không tự lành theo
   giờ** — nó lành khi BQ hồi tố hệ số cho phiên 23/09. Với độ trễ vendor đã đo (tháng 9: 8 sự
   kiện chưa hồi tố, xem `alphalens-fpt-vendor-factor-stale`), cửa sổ đó có thể dài NHIỀU NGÀY.

## 7. Chỗ hướng sửa của Mike còn sai / thiếu

1. **"dùng LUÔN `marketPrice` của broker" — KHÔNG được dùng thẳng.** `marketPrice` sai thật ở cả
   hai chiều: SCL 2026-08-28 đứng im 27.600 trong khi phiên đóng 27.800; BID 2026-08-14 một bản
   đọc mang đồng thời giá đã và chưa điều chỉnh (§G4, không nguyên tử theo gói vay). Đã thêm
   **đối soát cơ khí** `marketPrice ≈ px_cum / multiplier` — bằng chứng, không niềm tin (§29).
2. **Spec chỉ nêu `compute_active_nav`; `park_holdings` cũng đã cắn cùng số** và gắn cờ
   UNVERIFIED là chưa đủ vì `compute_park_trim:330` đọc `park_mv_vnd` (không phải bản `_verified`).
   Đã vá luôn.
3. **Bất biến "chỉ nhánh 1 đổi cách lấy giá" cần một nhánh 1b**: credit sớm ĐÃ CHỨNG MINH nhưng
   KHÔNG dựng nổi giá cùng hệ. Spec để nó ngầm rơi vào nhánh 1 ⇒ sẽ giữ giá cum = tái lập đúng
   bug. Đã cho fail-closed như nhánh 2.
4. **Thiếu trong spec: sự kiện QUYỀN MUA.** `ref = (P_cum + r×giá_phát_hành)/(1+r)` nên không
   khớp công thức thuần ⇒ hàm từ chối (test P12). Đúng ý (chưa nộp tiền thì broker chưa credit),
   nhưng phải là hành vi CÓ TEST chứ không phải may mắn.
5. **`production_manifest.py` trong danh sách nghi của Mike không đọc positions** (0 hit
   `openQuantity`/`get_positions`) — không phải call-site. Ngược lại `report_return_gate.py` và
   `discretionary_accumulation_inject.py`, KHÔNG có trong danh sách nghi, mới là hai chỗ thật.

## 8. Việc còn mở

- **Cần user/Mike duyệt LAND** nhánh này (chạm đường tiền). Sau khi land: chạy lại
  `compute_active_nav_all.sh` rồi **lập lại plan 24/09** — plan hiện tại có `BÁN VPB 200cp
  (SpaceX) / 100cp (ZaloPay)` `play_type=PARK_TRIM` tính trên rổ phồng.
- `nav_history` **thiếu dòng 09-21 VÀ 09-23** cả 2 account (mtime 09-22 20:30) — chờ quyết backfill.
- Call-site #3 (`report_return_gate`) và #4 (`inject`): chưa vá, cần quyết phạm vi riêng.
- `nav_cum_dividend_selfcheck.py:34` đếm cấp `dirname×2` ⇒ chết `FileNotFoundError` từ MỌI
  worktree (38/38 PASS từ checkout canonical). **Tiền-tồn-tại**, đã báo trước (N4); bản vá này
  chỉ sửa đúng instance chặn việc verify chính nó (`corp_action_selfcheck.py`).
