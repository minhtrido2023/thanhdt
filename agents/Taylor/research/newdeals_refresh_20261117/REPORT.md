# REPORT — Refactor topic "New deals" (job Taylor_20261117_102211, user duyệt 17/11/2026)

**Nhánh** `feat/newdeals-season-20261117` (repo ngoài, đã push), worktree `/home/trido/thanhdt/wt-newdeals-season-20261117`,
commit `d97339d1a` trên main `3f1dbed08`. **CHƯA merge, CHƯA cài cron.**
Diff (`git diff --numstat main HEAD`): `newdeals_season.py` +470 (mới) · `newdeals_season_selfcheck.py` +257 (mới) ·
`newdeals_daily_report.py` +31/−16 · `converge_report.py` +4/−1.

## Đã đổi gì (4 phần)
1. **Gỡ AlphaLens** khỏi `newdeals_daily_report.py` (hết hạn `end_date` 2026-09-30 trong `data/alphalens_paper.json`).
   `alphalens_report.py` + file data GIỮ NGUYÊN để audit; lý do ghi ở docstring. **DC Book theo mùa**: `reset_dc_book()` đặt
   seed = tập double-confirm của mùa mới (giá THÔ `Price` phiên mới nhất, equal-weight cap 0,20, `benchmark_entry` = VNINDEX
   cùng phiên); seed cũ + mốc cũ vào `meta.season_history` (không xoá). Cùng mùa ⇒ idempotent.
2. **Trigger mùa** `newdeals_season.py`: quý lớn nhất trong cache `ticker_financial` (PIT `time<=asof`) phủ ≥80% watchlist
   Nhóm A (16 mã `sector_lens_monitor.NAMES`) ⇒ đến hạn. Idempotent theo mùa (`data/newdeals_season_state.json`), không chạy
   lùi. "Tính lại rating 8L" = đọc `data/rating_8l.csv` (pt_8l_daily 19:20, KHÔNG gọi `rating_8l.py`) và **hoãn** nếu file
   cũ hơn ngày BCTC mới nhất của watchlist. Mùa trước = snapshot `data/newdeals_season/<Q>.json`; mùa đầu tiên bootstrap
   từ `rating_prev` PIT trong `data/rating_8l_forward_events.csv` + seed DC hiện tại.
3. **Hàng đợi DD** `data/newdeals_dd_queue.json`: ứng viên = VÀO + ĐỔI HẠNG sang hạng ≤3 (tụt xuống 4–5 không tốn suất)
   + phần dư mùa trước; RA thì loại. Mã đã có DD đúng quý ⇒ `dd_fresh`. Trần 5; ưu tiên dư mùa trước → double-confirm →
   MoS DCF → rating. Quý DD = `bctc_quarter` bản mới nhất trong `mike/kb/dd_price_zones.json` (schema v1 tái dùng,
   ghi ra field `dd_asof_quarter` trong hàng đợi). `--notify-bus` ⇒ 1 event `question` "newdeals-season-<Q> dd-queue"
   cho Mike dispatch (cờ `bus_pending`: lỗi thì lượt sau post bù, không post lặp). **Không tự chạy DD.**
4. **Nhãn**: dòng đầu `🧭 Độ tươi: BCTC Q phủ x/16 (y%) · rating 8L <ngày> · DCF mùa <slot> · sổ DC mùa <Q> từ <ngày> (N ngày)`;
   mỗi dòng mã: `DD asof <Q>` / `DD: chưa có` / `⚠️ DD cũ (Qx) — tín hiệu chưa hợp lệ…` + gạch `~~ACCUMULATE~~`/`~~STRONG~~`.

## Kiểm chứng
- Selfcheck `newdeals_season_selfcheck.py`: ALL PASS, 43 assert, dưới `env -u TZ` VÀ `TZ=America/New_York`.
- Mutation `--mutate`: **9/9 killed** (đảo so sánh DD cũ, bỏ gạch, ngưỡng 0, bỏ idempotency mùa, trần 6, reset DC không
  idempotent, bỏ kiểm rating tươi, bỏ PIT, bỏ lịch sử seed).
- Render thật `build_message()` (WORKDIR=main, không gửi) + `_check_return_gate()` trên đúng message ⇒ **PASS** (cổng §21
  không đổi, vẫn fail-closed).
- `tz_anchor_gate` không chạy được trong worktree (file ngoài baseline-key) — kiểm tay: mọi `now/fromtimestamp` mới đều neo ICT.
  Gate sẽ chạy thật khi merge vào main.

## Dòng cron ĐỀ XUẤT (Mike cài sau arch-review; host TZ=UTC)
```
45 12 * * * cd /home/trido/thanhdt/WorkingClaude && . ./wc_env.sh && flock -n mike/state/newdeals_season.lock timeout 900 $DNA_PYEXE newdeals_season.py --notify-bus >> /home/trido/thanhdt/WorkingClaude/mike/logs/newdeals_season.log 2>&1   # 19:45 ICT hằng ngày — vòng làm mới New deals theo mùa BCTC (sau pt_8l_daily 19:20 để rating tươi); ngoài mùa = no-op
```
Lưu ý: lượt cron ĐẦU TIÊN sẽ thực sự đặt lại DC Book sang mùa 2026Q3 (dry-run đã đến hạn) và post hàng đợi.

## Mùa 2026Q3 hiện tại (dry-run `--asof` 2026-11-17, không ghi)
Phủ **16/16 (100%)** · rating 8L 2026-11-16 · baseline = bootstrap (rating_prev + seed 26/06).
- **VÀO**: VCB (vào double-confirm, R1). **RA**: SSI (R2→R3, rời golden + double-confirm).
- **ĐỔI HẠNG**: HCM 3→4, SSI 2→3, VCI 3→4 (HCM/VCI tụt khỏi vùng đầu tư ⇒ không tốn suất).
- **Hàng đợi DD**: `VCB` (queued, 1/5). Không có deferred.
- **Seed DC mùa Q3**: ACB, CTR, DHG, FPT, HAH, MBB, PVT, TCB, VCB (9 mã).

**Tuổi DD hiện có** (bản mới nhất `dd_price_zones.json`, tính tới 17/11): MBB 2026-10-31 rev3 Q3 (17 ngày) · FPT 2026-11-01
rev3 Q3 (16 ngày) · PVT 2026-10-29 rev2 Q3 (19 ngày). 13/16 mã watchlist **chưa có DD**: ACB, HDB, TCB, VCB, SSI, VCI, VND,
HCM, CTR, MSH, DHG, HAH, DBC. Hiện **không mã nào DD cũ** (mọi DD đều Q3 = quý mới nhất).

## Điểm mở cho Mike/user
- "Chưa có DD" chỉ gắn nhãn, KHÔNG gạch ACCUMULATE/STRONG (đọc sát brief: chỉ DD *cũ* bị vô hiệu). Nếu muốn chặt hơn thì
  đổi 1 nhánh trong `apply_dd_labels`.
- 6/9 mã seed DC Q3 chưa từng có DD nhưng không "đổi trạng thái" ⇒ không vào hàng đợi; còn 4 suất trống mùa này. Lấp bằng
  các mã đó hay không = quyết định của user (chưa làm).
- Golden/Strong tính trên watchlist 16 mã, không phải toàn universe (183 mã rating≤2 — quá nhiều cho trần 5).

## Vòng 2 (job Taylor_20261117_103907) — 6 mục arch-review, KHÔNG mở rộng phạm vi
Selfcheck `newdeals_season_selfcheck.py`: ALL PASS, **58 assert** (`env -u TZ` + `TZ=America/New_York`); mutation **15/15 killed**
(+6 mutant mới: bootstrap bỏ history, DD dùng max toàn universe, hàng đợi bỏ quý theo mã, bỏ guard rating_missing, CLI không phân biệt, bus lỗi không bọc).
1. **Cổng §21** — repo MIKE (nested), commit riêng `3a0f92f0f` (`bin/report_return_gate.py`, KHÔNG nằm trong commit nhánh outer; **phải merge cùng đợt**):
   `PAPER_MARKERS` chỉ còn "DC Book Paper Portfolio" (gỡ AlphaLens); thêm `PAPER_BOOKS_DISPLAYED=("converge",)` + `_displayed_books()` ⇒ cổng
   không chặn vì sổ AlphaLens ẩn (`load_books()` vẫn nạp AlphaLens từ file data để audit); stub `slm.NAMES` ở ca 27 + 29; sửa `quiet_msg` ca 28.
   `report_return_gate.py --selfcheck` với module nhánh (`WC_ROOT=<worktree>/WorkingClaude`): **270/270** (269 + 1 ca mới), 2 TZ; 4 mutant
   (marker AlphaLens quay lại / marker DC trôi / bỏ stub NAMES / hiển thị lại alphalens) đều bị bắt. Trước sửa: crash `AttributeError: slm.NAMES`.
2. **Idempotency mùa đầu** — `_bootstrap_prev`: khi `paper.meta.season == season` và có `season_history` ⇒ seed mùa trước = `season_history[-1]`.
   Ca kill giữa ghi sổ và ghi state: lượt 2 = lượt 1 (RA ['AAA'], VÀO [BBB,CCC], hàng đợi [BBB,CCC]; sổ không đặt lại lần 2).
3. **DD asof** — `ticker_quarters()` (quý mới nhất CỦA CHÍNH MÃ, PIT time<=asof); `dd_status/apply_dd_labels/build_dd_queue` nhận dict theo mã
   (str vẫn chạy). Báo cáo ngày dùng `ticker_quarters_from_cache`; lỗi đọc ⇒ rơi về quý chung (thận trọng hơn). Ca: universe có Q4 sớm, mã chưa
   công bố Q4 ⇒ KHÔNG "DD cũ". (Hàng đợi DD cũng dùng quý theo mã — cùng lỗi, 1 tham số.)
4. **Thông điệp CLI** — `BusPostError` (bus lỗi SAU khi state ghi) ⇒ "mùa X ĐÃ xong … bus_pending=X ⇒ lượt sau tự post bù"; lỗi khác ⇒ "mùa KHÔNG đánh dấu xong (lỗi trước khi ghi state)". rc vẫn 1.
5. **Guard đủ mã** — `rating_8l.csv` thiếu bất kỳ mã watchlist ⇒ `reason="rating_missing [...]"`, hoãn như `rating_not_fresh` (không diff, không đánh dấu mùa).
   Đo thật 17/11: 16/16 mã watchlist đều có rating ⇒ không chặn oan.
6. **Registry** — `mike/kb/data_registry/rating-8l/rating_8l_forward_events_csv.md` (+ dòng index): writer = `rating_8l_forward_tracker.py`, cron 11:15 UTC
   (crontab thật), ledger append-only, 1.395 dòng (283 Q2 + 1.112 Q3) đo 17/11. Commit ở repo mike (xem bus).
Dry-run thật `--asof 2026-11-17` sau vá: kết quả y hệt vòng 1 (VÀO VCB, RA SSI, seed 9 mã).

### Trước lượt cron ĐẦU TIÊN (Mike làm)
- **Chép backup `data/converge_portfolio_paper.json`** (file không theo git; lượt đầu GHI ĐÈ sổ DC sang mùa 2026Q3 — seed cũ chỉ còn trong `meta.season_history`),
  vd `cp data/converge_portfolio_paper.json state/converge_portfolio_paper.pre_season_20261117.json`.
- Question bus `newdeals-season-<Q> dd-queue` (post bởi `--notify-bus`) — **Mike đóng bằng cách**: dispatch DD (skill `due-diligence`, tối đa 5 mã `queued`)
  rồi post `answer`/`decision` ĐÚNG topic string `newdeals-season-<Q> dd-queue` kèm danh sách DD đã dispatch/mã deferred (skill `bus-question-closure`);
  trống hàng đợi ⇒ đóng ngay bằng `answer` "không có mã cần DD". Payload event ghi sẵn `action` + `measured_by`.
- Merge cùng đợt: nhánh outer `feat/newdeals-season-20261117` + commit mike `3a0f92f0f` + commit registry (cổng §21 sửa trong mike, không có thì daily report crash ở ca 27).
