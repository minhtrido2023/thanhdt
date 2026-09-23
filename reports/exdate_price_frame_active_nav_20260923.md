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
| 3 | `report_return_gate.py:126-166` | **CÙNG LỚP, CHƯA VÁ, ngoài phạm vi job này.** qty + `costPrice` từ broker (**cả hai** đã ở hệ SAU), giá từ `bq_close_prices(asof)` = 27.800 (hệ TRƯỚC, BQ đã có dòng 23/09). Đo thật: VPB ra **+26,24% (SpaceX) / +30,97% (ZaloPay)** thay vì +0,13% / +3,88%. **ĐÍNH CHÍNH vòng 2 — hệ quả KHÔNG phải "chặn oan" mà là LỖ HỔNG PHỦ IM LẶNG, tệ hơn:** nhánh BẢNG ghép theo `key = (mã, KL)` (`:510-511`); báo cáo lấy KL từ `verify_account_snapshot` (journal = 1.100) còn cổng dựng kỳ vọng từ broker (1.386) ⇒ key KHÔNG khớp ⇒ `unmatched += 1; continue` (`:512-513`) — **không fail**, chỉ in "ngoài phạm vi cổng này". `nocover` (`:568-570`) cũng không vớt được vì nó lọc `g > 0`, mà VPB là cổ tức CỔ PHIẾU nên `entitled_gross`=0. Chặn oan chỉ xảy ra ở nhánh VĂN XUÔI (`:543-551`, khớp theo mã). ⇒ Đúng mã có corp-action — mã KHÓ NHẤT — là mã cổng lặng lẽ thôi kiểm. |
| 4 | `discretionary_accumulation_inject.py:113-125` | **Cùng HỌ nhưng khác dạng** (không nhân giá): `filled_qty = broker_total − baseline` ⇒ KL credit sớm bị tính là "đã khớp". Chỉ ảnh hưởng mã đang có chương trình tích luỹ (DGC/TV1) — VPB không phải. Chưa vá. **Bổ sung vòng 2 (khai thiếu ở vòng 1):** (a) chiều lệch là **MUA THIẾU**, không bao giờ thừa — `filled_qty` phồng ⇒ chương trình tưởng đã mua đủ ⇒ dừng sớm; (b) `baseline` ghi vào state file hỏng **VĨNH VIỄN** theo hệ số sau sự kiện, **KHÔNG tự lành** như mọi call-site khác (các chỗ kia tự khỏi ngay phiên ex-date khi giá G1 điều chỉnh; chỗ này số hỏng được PERSIST). |
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

---

# VÒNG 2 — sau arch-review NEEDS_CHANGES (high), job Taylor_20260923_165842

## 9. R1–R5 đã sửa

| # | Vấn đề | Sửa | Test giết mutation |
|---|---|---|---|
| R1 | `_corp_action_daily_snapshot` trả `None` IM LẶNG khi thiếu file ⇒ MỌI mã thành `qty_unexplained` với câu **"lịch corp-action KHÔNG có sự kiện nào cho mã này"** — suy diễn từ SỰ VẮNG MẶT của một kênh (§28). Replay vòng 1 in đúng câu đó cho VHM 08-05 / MBB 08-11, hai ngày file lịch KHÔNG TỒN TẠI ⇒ **4/4 ca BLOCK trong replay đều bị chẩn đoán sai hướng**. | `classify_positions` gọi `dns._corp_action_gate_status(snap, asof)` (hàm ĐÃ CÓ SẴN, `daily_nav_snapshot` in nó từ vòng 2 của việc trước). Tách thành 3 ca trong `_calendar_clause()`: có `ex_date` / lịch OK mà không có sự kiện / **`snap is None` ⇒ "KHÔNG ĐỌC ĐƯỢC LỊCH corp-action cho `<asof>` ⇒ KHÔNG kết luận được mã này CÓ hay KHÔNG CÓ sự kiện"**. `ca_note` đính vào MỌI thông điệp. | D1 D2 D3 D4 |
| R2 | Bỏ `missing_out=` ⇒ in "lệnh khớp thật +0" không caveat khi journal hỏng — tái lập ĐÚNG lỗi đã vá ở vòng 3 của `daily_nav_snapshot` (mục [N2]). | Truyền `missing_out=journal_gaps`; `_journal_caveat()` đính đúng chuỗi `[⚠️ journal KHÔNG đọc được cho N ngày GIAO DỊCH…]` như bản gốc (cắt 5 mục đầu, §29). | J1 J2 |
| R3 | rc=6 in "chờ `corp_action_auto_confirm.py` rồi chạy lại" — đường đó đi qua `confirmed_share_event_multiplier`, thứ `exdate_frame.py`/`compute_active_nav.py` **không gọi ở bất kỳ nhánh nào** (grep: 0 hit). Mã kẹt ở nhánh 1b chạy lại cho kết quả **Y HỆT** ⇒ người vận hành lặp vô ích. | Thay bằng việc thật: (1) NGƯỜI xác minh giá tham chiếu sau sự kiện rồi đối chiếu marketPrice; (2) kiểm journal + lịch theo đúng vế đã nêu trong từng dòng. Nói thẳng "chạy lại khi CHƯA có thêm bằng chứng cho kết quả Y HỆT" + chỉ `--out` để xem số mà không đụng file sizing. | E9 E10 |
| R4 | **Cổng fail-closed có LỐI VÒNG.** `:415` bỏ qua trọn khối khi `--asof` là quá khứ; `:238` `get_positions()` LUÔN trả vị thế LIVE; `:343` vẫn ghi FILE CANONICAL ⇒ sau rc=6, một lệnh `--asof <hôm qua>` ghi đúng con số phồng vào mẫu số sizing, rc=0, không cảnh báo. | Hai lớp: (a) `--asof` ≠ hôm nay **mà không có `--out` ⇒ rc=7, không chạm file canonical** (§8); (b) có `--out` thì vẫn chạy nhưng in cảnh báo cổng §exdate_frame BỊ TẮT cho bản chạy đó. | A1 A2 A3 A4 A5 |
| R5 | Báo cáo vòng 1 kết luận hệ quả của `report_return_gate` là "CHẶN OAN". | SAI — đã sửa mục 4 dòng 3: thực tế là **PHỦ IM LẶNG** (`key=(mã,KL)` không khớp ⇒ `unmatched; continue`, không fail; `nocover` lọc `g>0` nên cổ tức CỔ PHIẾU cũng không lọt). Tệ hơn chặn oan. | — (ngoài phạm vi nhánh) |

**R1–R5 có chỗ nào sai không: KHÔNG.** Tôi tự đọc lại code cho cả 5 và cả 5 đều đúng như reviewer
mô tả. Riêng R4 tôi chọn bản **chặn cứng** (rc=7) thay vì chỉ cảnh báo, vì cảnh báo không đóng
được lối vòng — và lý lẽ "BQ Close đã hồi tố ⇒ cùng hệ" đúng là bị chính §6.2 của tôi bác (8 sự
kiện vendor chưa hồi tố trong tháng 9). Không có caller tự động nào truyền `--asof`
(`compute_active_nav_all.sh:26` chạy trần), nên chốt này không chặn nhầm gì đang chạy.

## 10. Selfcheck — **45/45 PASS** (vòng 1: 32/32), qua **5** TZ

`TZ=Asia/Ho_Chi_Minh` · `env -u TZ` · `TZ=UTC` · `TZ=Pacific/Kiritimati` (+14) ·
`TZ=Pacific/Midway` (−11) — cả 5 đều 45/45.

**[V3] Câu "4/4 mutation chết bằng ASSERTION" ở vòng 1 là SAI — sửa lại:** đó là tính chất của 4
mutation TÔI chọn, không phải của harness. Reviewer chỉ đúng: mutation `multiplier→1.0` chết bằng
`FileNotFoundError`, `classify_positions→({},{})` (Mike) chết bằng `KeyError`. Vòng 2 đã thêm
**10 assertion CÓ TÊN** và đo lại bằng 4 mutation mới, mỗi mutation = revert đúng một mục R:

| Mutation (revert) | Kết quả | Chết bằng |
|---|---|---|
| R1 — bỏ `_corp_action_gate_status`, luôn nói "không có sự kiện nào" | 41/45, **4 FAIL** | D1 D2 D3 D4 — assertion có tên, KHÔNG crash |
| R2 — bỏ `missing_out=` | 44/45, **1 FAIL** | J1 |
| R3 — khuyên lại `corp_action_auto_confirm` | 43/45, **2 FAIL** | E9 E10 |
| R4 — bỏ rc=7 + bỏ cảnh báo cổng tắt | 42/45, **3 FAIL** | A1 A2 A4 — **A2 fail chứng minh cơ học rằng file canonical THẬT SỰ bị ghi đè** ở bản chưa vá |

Ghi nhận reviewer: mutation bỏ guard `market_price <= 0` SỐNG 32/32 — đúng là guard THỪA (dung
sai vẫn loại ca 0đ), không phải lỗ hổng, không sửa.

## 11. [V1] CALL-SITE THỨ BA — `dividend_adjusted_return.py`, CHẠM SỐ CÔNG BỐ CHO NHÀ ĐẦU TƯ

Reviewer tìm ra, vòng 1 tôi **khai thiếu**. Tôi tự đọc code xác nhận **cả hai vế**:

1. `broker_qty():459-470` key theo `ts[:10]` và giữ bản ghi **MỚI NHẤT** trong ngày ⇒ giá trị là
   KL **CUỐI NGÀY**. `_qty_at():473-478` lấy `qmap[(ticker, last_cum_date)]` — nhưng ngữ nghĩa
   cần là KL **HƯỞNG QUYỀN** (1.100), mà tối `last_cum_date` broker đã credit rồi (1.386).
2. Bộ chống chính ca này (`:523-527`, gắn `STOCK_SUSPECTED` khi `qty[last_cum] != qty[ex_date]`)
   **bị credit sớm VÔ HIỆU HOÁ**: hai ngày đã bằng nhau (1.386 = 1.386) ⇒ `changed` rỗng ⇒ không
   gắn cờ, sự kiện đi thẳng vào hệ phương trình.

`_qty_at` là **hệ số** của ma trận (`A[i, pos[c]] = _qty_at(...)`, `:565`) giải `A·x = b` với `b`
= delta tiền ⇒ hệ số phồng theo `1+r` làm `value_per_share` giải ra **THẤP** đúng hệ số đó.

**Hệ quả:** mã có **cổ tức TIỀN + cổ tức CỔ PHIẾU cùng ex-date** (rất phổ thông ở VN) ⇒ §21 cộng
**THIẾU** cổ tức vào tỉ suất **CÔNG BỐ CHO NHÀ ĐẦU TƯ**, và `entitled_gross` của
`report_return_gate` lệch theo. VPB đợt này không có chân tiền mặt nên chưa nổ.

**Hướng sửa (chưa làm — ngoài phạm vi nhánh này):** neo KL hưởng quyền theo bản ghi positions
**TRƯỚC `broker_effective_ts`**, không theo NGÀY. Đây là call-site NẶNG NHẤT trong cả 3 vì nó là
số công bố, không phải số nội bộ — đề nghị ưu tiên trên #3 và #4.

## 12. Việc còn mở sau vòng 2

- **Vẫn CHƯA LAND** — chờ user/Mike duyệt (chạm đường tiền). Sau land: `compute_active_nav_all.sh`
  rồi lập lại plan 24/09.
- 3 call-site chưa vá, xếp theo mức nặng: **V1 `dividend_adjusted_return.py`** (số công bố) >
  `report_return_gate.py` (phủ im lặng) > `discretionary_accumulation_inject.py` (baseline hỏng
  vĩnh viễn). Cần quyết phạm vi riêng cho từng cái.
- 24/09 là ex-date VPB THẬT ⇒ G1 close tự điều chỉnh sáng nay, lỗi của chính ca VPB tự lành. Bản
  vá vẫn cần cho lần sau.

---

# VÒNG 3 — F1..F5 (commit `3f66364c`, 2026-09-24 ~00:5x ICT)

## Đã sửa

| Mục | Sửa | Bằng chứng |
|---|---|---|
| **F1** | `args.asof = (args.asof or "").strip() or None` ngay sau `parse_args` (tiền lệ `park_holdings.py:550`) + lớp hai: `bq_close_sql` **NÉM** `ValueError` khi `as_of_date` rỗng thay vì âm thầm thành `TRUE` | A6/A7/A8; mutation M-F1, M-F1b |
| **F2** | Chốt chặn đổi từ `not args.out` sang `os.path.realpath(out_path) == os.path.realpath(canonical_out)` | A9/A10 (cả đường thẳng lẫn qua `./`); mutation M-F2; **demo trên đường dẫn canonical THẬT: rc=7 × 2, md5 2 file không đổi** |
| **F3** | `park_holdings` phát cờ **cấp tài khoản** `frame_blocked_tickers` + `frame_blocked_detail`; `compute_park_trim.py` và `compute_jit_unpark.py` thêm cổng `BLOCKED_FRAME` ngay sau cổng reconcile (cùng hình dạng `BLOCKED_CASH_BASIS`) | K6..K12; mutation M-F3a/b/c |
| **F4** | 14 assertion CÓ TÊN (45 → **59**) | 59/59 PASS × 4 môi trường TZ |
| **F5** | `{args.asof!r}` ở cả dòng rc=7 lẫn dòng ⚠️ | — |

**Đo (sau commit, `git status --porcelain` RỖNG):** 59/59 PASS ở ICT / `env -u TZ` /
`Pacific/Kiritimati` / `UTC` dưới `$DNA_PYEXE` · **6/6 mutation bị giết** · selfcheck theo phạm vi
(§23, chạm `park_holdings` = lõi dùng chung của cả L1/L2): `compute_active_nav` ✅,
`compute_park_trim` 82/82, `compute_jit_unpark` 80/80 (ma trận TZ, digest đồng nhất),
`merge_park_orders` ✅, `approve_plan_with_jit` ✅, `corp_action` 85/85.

**KHÔNG chạy `--asof ""` trên production.** Sau F1 nó tương đương một lần chạy bình thường ⇒ gọi
DNSE live và ghi canonical thật. Bằng chứng là A6/A7 hermetic. Trước mọi lần chạy chạm đường dẫn
thật đã backup (`/tmp/anav_backup_1790184600`); md5 2 file canonical trước = sau; số hiện tại vẫn
là SpaceX 983.012.160 (VPB 30.561.300) / ZaloPay 521.077.109.

## Ba chỗ tôi thấy F1–F5 nói SAI hoặc tự mâu thuẫn

**(1) F4(c) mâu thuẫn với chính F3 — tôi theo F3.** F4(c) yêu cầu "nhánh verify-fail ⇒
`park_mv_vnd` KHÔNG còn 38.530.800". Không làm được, và không nên làm: nhánh verify-fail **theo
định nghĩa** là nhánh không dựng nổi giá cùng hệ, nên không tồn tại con số đúng để thay vào. Mọi
phương án thay (bỏ lô, dùng `park_mv_verified_vnd`, gán 0) đều là bịa một con số theo hướng
NGƯỢC LẠI. F3 nói đúng việc phải làm: *"trả BLOCKED_FRAME thay vì trim trên `park_mv_vnd` phồng"*.
Tôi giữ `park_mv_vnd` = 38.530.800 và **chặn consumer**; assertion **K8** pin thẳng rằng ở nhánh
fail mẫu số ĐÚNG LÀ số phồng — nên phải chặn, không phải tin.

**(2) F4(a) đòi sai mã lỗi.** F4(a) viết `--asof ""` ⇒ **rc=7**. rc=7 nghĩa là *"từ chối ghi đè vì
asof là ngày KHÁC hôm nay"* — sau F1 thì `""` ≡ `None` ≡ *không truyền* `--asof`, tức là một lần
chạy bình thường hợp lệ; bắt nó rc=7 là bắt script nói một câu SAI về chuyện vừa xảy ra, và sẽ chặn
cả ngày thường. Cái phải đạt là *`""` hết là lối vòng*: nó rơi vào **cùng nhánh** "hôm nay" nên
cổng §exdate_frame CHẠY. Trên fixture VPB ⇒ **rc=6** (`❌`, `cron_health_check.py` thấy); ngày sạch
⇒ rc=0 và ghi canonical, đúng. A6 assert rc=6, A7 assert canonical còn nguyên.

**(3) K9 yếu hơn vẻ ngoài — nói rõ ở comment trong code.** Fixture `t_park` có mọi field tiền = 0,
nên gỡ cổng `BLOCKED_FRAME` khỏi L1 thì nó rơi vào `BLOCKED_CASH_BASIS` chứ không ra lệnh trim (đo
thật bằng mutation M-F3b). Vậy K9 chứng minh **cờ thắng trước mọi cổng khác**, KHÔNG thực thi được
phản chứng "thiếu cổng thì over-trim thật". Vế đó vẫn là suy luận trên đường code
`:331 park_mv` → `:406 pool` → `:408 delta` — cùng bằng chứng reviewer đã dùng, không mạnh hơn.

F2, F3, F5: không có ý kiến ngược, đúng như mô tả.

## Việc RIÊNG — ghi nhận, KHÔNG sửa ở nhánh này

- **V1 · `discretionary_margin_gate.py:335` — call-site thứ TƯ, TIỀN THẬT.**
  `drawdown = px / a["arm_price"] - 1.0`, `:341 if drawdown <= EXIT_DD_PCT` (−0,20).
  `current_price()` (`:180-188`) trả giá SAU sự kiện; `arm_price` ghi lúc arm (`:269`) là giá CUM
  và không bao giờ được điều chỉnh ⇒ mọi sự kiện hệ số ≥1,25 tự chế ra một lần "chạm −20% ⇒
  de-lever bắt buộc" GIẢ (VPB 1,2604104: `1/1,2604104 − 1 = −20,66%`, vượt ngưỡng). Hiện **LATENT**
  (không state file, 0 case đang arm) — nhưng đây là sleeve margin discretionary, lệnh thoát thật.
- **V2 · Runbook rc=6, hai câu còn thiếu.** (a) Cửa sổ block **tự đóng sau GDKHQ** ⇒ tối đa 1 đêm;
  người nhận rc=6 lúc 20:15 hiện KHÔNG có cách nào biết. (b) Vòng phụ thuộc `corp_action_daily`
  ⇄ `active_nav` (`corp_action_daily.py:100,171` đọc danh sách mã đang giữ TỪ chính
  `active_nav_*.json`) ⇒ rc=6 kéo dài nhiều đêm phải gỡ **TAY**, không chờ tự khỏi.
- **V3 · `send_plan_report.sh:621`** đọc `active_nav_{acct}.json` KHÔNG có cổng độ tươi, bọc
  `except: pass` ⇒ đêm rc=6 thì dòng 🥚 "CẦN RÚT X tr trước 9:05" tính trên tiền HÔM QUA. Có sẵn
  từ trước bản vá này.
- **V4 · Khoảng trống cảnh báo:** `❌` chỉ tới người lúc **08:25** hôm sau, trong khi user duyệt
  plan ~21:00 đêm trước. Không có cảnh báo cùng-tối. Đúng với MỌI mã lỗi cũ, không riêng rc=6.
- **V5 · 3 call-site đã biết:** `dividend_adjusted_return.py:473-478`, `report_return_gate.py`,
  `discretionary_accumulation_inject.py:124`.
- **Đã tra thêm, SẠCH:** `verify_account_snapshot.py:382` có BẢN CHÉP riêng của `bq_close_sql`
  nhưng **không** có nhánh `else "TRUE"` (luôn `t.time <= '{as_of_date}'`) ⇒ `""` cho 0 dòng và
  in `WARN no BQ price` cho từng mã (ồn, không im lặng); tên file output nhúng `asof` nên không
  ghi đè được file sizing canonical. Khác lớp lỗi F1, không đụng.

⚠️ **KHÔNG tuyên bố đã quét hết.** Lớp lỗi này là *"hai số từ hai nguồn, ranh giới corp-action nằm
ở giữa"*; `grep` chỉ bắt được chỗ có `get_positions`/`close_prices`/`arm_price` lộ ra tên. Câu này
là của reviewer và tôi giữ nguyên: chưa đóng được toàn bộ.

**CHƯA LAND.** Nhánh `fix/exdate-price-frame-active-nav` @ `3f66364c`, worktree
`mike/wt-exdate-price-frame`. Chờ arch-review vòng 3 + Mike/user.
