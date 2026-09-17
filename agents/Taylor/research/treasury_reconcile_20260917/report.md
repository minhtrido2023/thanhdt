# Nhánh A — Treasury-share reconciliation: đo quy mô + thiết kế (job Taylor_20260917_150848)

R&D, READ-ONLY BQ. Không ghi bảng nào, không đụng `oshares_live.py`. Tái lập: chạy các script trong thư mục này bằng `$DNA_PYEXE` từ `WorkingClaude/`.

## A0 — 4 tiền đề trong dispatch SAI/LỆCH, đo lại
1. **"568 dòng buy_done/sell_done có shares_delta" — sai.** 568 = tổng dòng có `shares_delta` trên MỌI action_type
   (buy 196, sell 185, buy_done 80, other 56, sell_done 51). buy_done+sell_done có cỡ = **131 dòng**; gộp trùng
   `(ticker, public_date, action_type)` ⇒ **577 sự kiện / 233 mã, 128 có cỡ > 0 (22%), 449 KHÔNG cỡ**.
2. **Dòng treasury_news của VRE 2019-12-19 và SRF 2018-12-27 có `shares_delta = NULL`.** Hai dòng MANUAL_FILL không suy
   được từ treasury_news — cỡ lấy từ lệch OShares. ⇒ Nạp "có hệ thống" chỉ từ treasury_news sẽ KHÔNG tái tạo được chính 2 ca mẫu.
3. **Quy ước dấu ngược**: treasury_news `buy_done.shares_delta` DƯƠNG (số CP mua vào quỹ); dòng MANUAL_FILL ghi ÂM
   (Δ lưu hành). Nạp máy phải lật dấu tường minh.
4. **2 dòng MANUAL_FILL hiện KHÔNG có tác dụng nào lên oshares_live**: `_fetch` lọc `event_status = "executed"`, và
   `oshares_at` lọc AIS có `shares_total_after` ⇒ bị loại 2 lần. Cũng không vào `corp_action_lib.events()`
   (executed_only) hay `pricing_events()` (chỉ DIV/ISS). CÓ lọt vào `corp_action_daily._events_on_sql`
   (`!= "not_executed"`, mọi code, khớp `effective_date = asof`) ⇒ nếu backfill có ngày GẦN, daily sẽ hiện chúng như
   sự kiện "STILL_ANNOUNCED"/*(dự kiến)*; và canary `KNOWN_STATUSES` WARN (đã thấy 17/09).

## A1 — Quy mô ảnh hưởng thật
**Sự thật ngữ nghĩa quyết định mọi thứ:** mua CP quỹ KHÔNG đổi số NIÊM YẾT. `AIS.shares_total_after` = niêm yết (GỒM CP quỹ);
`ticker_financial.OShares` = lưu hành (đã trừ). VRE: 2.328.818.410 − 2.272.318.410 = 56.500.000 đúng lô 2019.

- Cỡ sự kiện (108 sự kiện có cỡ + có OShares nền): % OShares p25/p50/p75/p90 = 0,11 / 1,36 / 3,30 / 6,31, max 20,8;
  phân bố [<0,5%] 42 · [0,5-1) 7 · [1-2) 17 · [2-5) 24 · [5-15) 15 · [≥15] 3. Theo năm: dồn 2017-2021 (406/577).
- **Tác động HÔM NAY** (`oshares_at(live=True)`, 233 mã): chỉ 28 mã neo AIS (niêm yết) — nhóm duy nhất có thể thừa CP quỹ.
  Trong đó lệch dương giải thích được bằng tin buy_done: **GDT +316.310 (+1,17%)** (buy_done ESOP 2025-12-30/2026-05-14, cả hai NULL cỡ).
  PAN +2,95%, KLB +0,51%, PET +0,40% lệch nhưng KHÔNG có tin buy_done/sell_done ⇒ không phải CP quỹ theo nguồn này.
  → `ais_anchor_gap.csv`
- **Tồn latent** (niêm yết lăn tới dòng BCTC mới nhất − OShares BCTC, 163 mã đo được): 39 mã >0,1%, 17 trong ticker_prune
  (TVC 26,3 · VNE 10,2 · KDC 4,9 · SZL 4,3 · PAN 3,0 · **VRE 2,49** · CTD 2,0 ...). Đây là CẬN TRÊN — có thể lẫn lệch vendor khác.
  Rủi ro: ngày nào mã có AIS mới (≤90 ngày) thì oshares_live chuyển sang neo niêm yết ⇒ thừa đúng phần này. → `latent_balance.csv`
- **Mã đang nắm giữ** (dnse_raw 2026-09-17, lọc account_no; SpaceX 28 mã, ZaloPay 28 mã): 11 mã có sự kiện done
  (ACB HDB MSB SIP TPB VHM VIB VND VNM VPB VRE). **Hôm nay 0 mã sai vì CP quỹ**: 10 neo BCTC, VHM neo AIS lệch 0.
  **Latent duy nhất: VRE 2,49%** (đang FIN_FALLBACK vì AIS 2018 cũ; một AIS mới bất kỳ của VRE ⇒ thừa 56,5tr trong
  cửa sổ ≤90 ngày). Hàm ý composite: chỉ nhánh `ps` (sales_yield) lệch ~2,5% cho 1 mã.

## A2 — Thiết kế cơ chế tiêu thụ (prototype, KHÔNG wire)
**Hấp thụ kiểu ISS (dispatch đề xuất) là SAI chiều ngữ nghĩa:** ISS tăng niêm yết ⇒ AIS kế tiếp nuốt nó. CP quỹ không đổi niêm yết
⇒ AIS kế tiếp VẪN gồm CP quỹ ⇒ phần trừ phải kéo dài qua MỌI neo AIS tới khi bán/huỷ. Prototype `treasury_adjust.py` (hàm thuần, hậu-xử-lý
trên output `oshares_at`):
- Neo **BCTC** ⇒ chỉ áp sự kiện có public_date ∈ (ngày dòng quý, asof]; nếu Δ dòng quý so quý trước ≈ tổng Δ đó ⇒ `TREASURY_FIN_ABSORBED`
  (ca VRE restate sớm) — đây chính là chiều ngược của `_forward_absorption_test`.
- Neo **AIS** ⇒ trừ CP quỹ đang tồn **hiệu chuẩn tại dòng BCTC gần nhất** (niêm yết lăn tới ngày đó − OShares), rồi ± sự kiện sau dòng quý.
  Không cần tổng dồn toàn lịch sử tin (449/577 thiếu cỡ) — tự hiệu chuẩn mỗi quý. Chỉ trừ khi có ≥1 tin buy_done/sell_done trước dòng quý
  (`TREASURY_GAP_UNCORROBORATED` giữ nguyên — ca PAN/KLB).
- Fail-closed/flag: sự kiện sau dòng quý thiếu cỡ ⇒ `TREASURY_UNSIZED` (giữ số, cờ); niêm yết GIẢM sau dòng quý (huỷ CP quỹ) ⇒ `None`
  `TREASURY_CANCEL_AMBIGUOUS`; |điều chỉnh| >15% ⇒ `None` `TREASURY_CEILING`; lưu hành > niêm yết ⇒ `TREASURY_NEG_GAP` giữ nguyên.
- Selfcheck hermetic `treasury_adjust_selfcheck.py` **20/20 PASS** (env -u TZ, TZ=America/New_York, `$DNA_PYEXE`); `mutation_test.py` **18/18 killed**
  (vòng đầu 15/18 — thêm B1/B2/A2 khoá biên ngày + neo AIS có mua thêm).
- **Câu hỏi mở cho Mike**: `TREASURY_UNSIZED` nên giữ số+cờ (đề xuất; CP quỹ thường <5%) hay fail-closed `None` như `UNKNOWN_RATIO`?
  PIT: hiệu chuẩn dùng dòng BCTC ≤ asof ⇒ thừa hưởng bẫy RESTATE y như neo BCTC hiện có (không tệ hơn, không PIT hơn).

## A2b — Nơi lưu: bảng RIÊNG, KHÔNG trộn vào `corporate_action` (đề xuất; Mike/user quyết)
| | Trộn vào `tav2_bq.corporate_action` (như 2 dòng tay) | Bảng riêng `tav2_mike.treasury_share_events` (dry-run: `build_overlay_rows.py`) |
|---|---|---|
| Ngữ nghĩa | `event_code=AIS` nhưng không đổi niêm yết, `shares_total_after` NULL ⇒ phá hợp đồng "AIS = mức niêm yết" mà cổng chứng nhận dựa vào | cột riêng `outstanding_delta` (đã lật dấu), `size_status` SIZED/UNSIZED/CONFLICT |
| Tác động downstream | canary WARN mỗi giá trị mới; `corp_action_daily` hiện như sự kiện dự kiến; snapshot chép vào vintage; vendor UPSERT có thể ghi đè/xoá (bảng vendor, writer ngoài repo) | 0 consumer hiện có bị chạm; chỉ `oshares_live` opt-in đọc |
| Lineage | id tĩnh tay, `source_url` không trỏ tin | id = `TRSY-sha1(ticker|date|action)[:16]` (577 id duy nhất), `source_news_ids`, `first_public_datetime` |
| Nhược | 1 bảng để JOIN | thêm 1 nguồn + 1 freshness check (§14) + registry entry |
Khuyến nghị thêm: **gỡ hoặc để nguyên-nhưng-ghi-nhận 2 dòng MANUAL_FILL** — hiện chúng vô tác dụng với oshares_live, chỉ tạo nhiễu canary.

## A3 — One-time hay recurring? (không tự quyết)
- treasury_news: 2.371 dòng ingest lô 2026-09-13 + 6 dòng 2026-09-16 (public_date đến 09-15) ⇒ có dấu hiệu cập nhật tăng dần, **n=1, chưa xác nhận cadence**.
- Tác động live hôm nay ≈ 0 cho mã nắm giữ; giá trị chính là PIT/backtest (đã có overlay 09-07) + phòng VRE-type khi AIS mới về.
- Đề xuất: **KHÔNG làm gì production cho tới khi Mike/user chọn**. Nếu làm: (1) one-time dựng bảng riêng từ dry-run (577 dòng),
  (2) recurring chỉ khi `treasury_news` có cadence xác nhận ≥2 tuần + freshness gate; tiêu thụ trong oshares_live chỉ sau đo tác động
  ranking composite (điều kiện mở lại của quyết định 09-08 vẫn đứng: chưa có case đổi quyết định đầu tư).

## Artifact
measure_scope.py → events_scope.csv, tickers_today.csv, held.json · ais_anchor_gap.py → ais_anchor_gap.csv · latent_balance.py → latent_balance.csv ·
treasury_adjust.py + treasury_adjust_selfcheck.py + mutation_test.py · build_overlay_rows.py → overlay_rows_dryrun.csv
