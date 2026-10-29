# Cảnh báo TĂNG VỐN trong chu kỳ đầu tư — 29/10/2026

Job `Taylor_20261029_072529` (dispatch Mike). User chốt 29/10 14:2x ICT (`decided_by: user`): *"SCL đang có trong
lag book nên thoái và nên đưa warning khi có bất kỳ việc tăng vốn nào xuất hiện trong chu kỳ đầu tư của chúng ta"*.
Phạm vi: **chỉ cảnh báo**. Không chạm lệnh, plan hay `trading_rules.json`. Việc thoái SCL đi qua plan T+1 của DollarBill.
Nhánh `session/capraise-20261029`, worktree `wt-capraise-20261029`. **Chưa merge.**

## TL;DR

1. **Giả thuyết "BQ trễ ~7 tuần" là SAI (đã đo).** `ingested_at` là lần upsert CUỐI của vendor, không phải lần
   đầu bảng có dòng đó. Trên `tav2_mike.corporate_action_snapshots` (append-only), dòng quyền mua SCL
   `6a0516165b1fb4c98c3ab2a2` **đã có từ snapshot đầu tiên 2026-08-17** (lúc đó tỉ lệ 0,1851, public 2026-05-07).
   Đến 2026-09-11 nó đổi sang tỉ lệ 0,15384615, public 2026-09-08. Vậy **trước khi SCL vào LAG (26/10) hơn 2 tháng**,
   BQ đã có đủ dữ liệu.
2. **Vì sao hệ thống không báo trước khi vào lệnh:** (a) gói DD LAG (`lag_dd_pack.py`) **không có bước kiểm
   tăng vốn**; (b) `rights_issue_alert.py` chỉ quét mã ĐANG GIỮ, mà `active_nav_*.json` ngày 26/10 chưa có SCL và
   ngày 27/10 cũ (computed_at 10-25). Kết quả là tin đầu tiên tới **28/10 19:00** (log `logs/bq_freshness.log`, state
   ghi 2026-10-28 19:00:56).
3. **Độ trễ thật của nguồn:** BQ thấy record **median 1 ngày, p90 2 ngày** sau khi vendor tạo (n=30 record tạo sau 17/08).
   Vendor tạo record ngay từ giai đoạn kế hoạch: với quyền mua, **median 157 ngày trước GDKHQ**. ⇒ **Không cần nguồn dẫn
   trước** cho Rights/riêng lẻ/ESOP. Ngoại lệ là PUBL và TRANS (record tạo SAU GDKHQ), xem §1.
4. **Lớp A (trước vào lệnh):** thêm cờ `CAPITAL_RAISE_PENDING` / `CAPITAL_RAISE_12M` / `CAPITAL_RAISE_NA` vào gói DD
   LAG. Chạy phản thực tế SCL asof 2026-10-23 (ngày gói DD thật) ⇒ **`CAPITAL_RAISE_PENDING` BẬT**, bằng chứng
   "QUYỀN MUA pha loãng 15.38%… | số CP lưu hành 4 quý +73.4%".
5. **Lớp B (trong chu kỳ):** `rights_issue_alert.py` (vẫn chạy trong [pipeline-3c] 19:00, không thêm cron) nay báo
   **mọi phương thức phát hành**: WARN và INFO, kèm % pha loãng, giá phát hành so thị giá, khoảng cách tới ngày chốt.
   Đã sửa câu chữ "Bot TỰ giữ…" theo yêu cầu.
6. **Ngưỡng X = 10%** (pha loãng THU TIỀN đã thực hiện trong 12 tháng). Lý do: mọi mã chỉ có ESOP (n=34) đều có max
   **5,0%**; dải 5–10% chỉ có 2 mã.

## 0. Nguồn dữ liệu (§9 — đã tra `kb/data_registry/`)

| Nguồn | Trạng thái registry | Dùng cho |
|---|---|---|
| `tav2_bq.corporate_action` | TRAP (upsert in-place; `public_date`/`ingested_at` bị ghi đè) | trạng thái HIỆN TẠI của sự kiện (lớp A, B) |
| `tav2_mike.corporate_action_snapshots` | CANONICAL (append-only, 69 vintage 08-17→10-29) | đo độ trễ / "BQ thấy lúc nào" |
| `tav2_bq.ticker_financial.OShares` | CANONICAL | số CP 4 quý (bằng chứng phụ), % khi `exercise_ratio`=0 |
| `tav2_bq.stock_news` | PARTIAL (ingested_at ≠ lúc biết tin; backfill 09-13) | KHÔNG dùng (xem §1.4) |
| DNSE API (`dnse_api.py`) | — | **không có endpoint corp-action** (chỉ lệnh/vị thế/số dư/secdef/giá/ohlc). Nhánh broker trong `corp_action_auto_confirm.py` chỉ phát hiện điều chỉnh giá SAU GDKHQ ⇒ không thể làm nguồn công bố |

## 1. Độ trễ nguồn (đo, không đoán)

Script: `q_lag.sql`/`analyze_lag.py` → `analyze_lag_out.txt`; `q_lag2.sql`/`analyze_lag2.py` → `analyze_lag2_out.txt`.

**Cách đo sai (đừng dùng):** `ingested_at − public_date` trên bảng hiện tại cho median 42 ngày với WARN. Con số này
phồng vì `ingested_at` là lần upsert CUỐI. Ví dụ SCL: hash dòng không đổi từ 09-11 nhưng `ingested_at` = 10-28.

**Cách đo đúng:**
- `objid_d` = 8 hex đầu của `id`, đọc như ObjectId, tức thời điểm VENDOR tạo record. Đây là giả định định dạng,
  được kiểm bằng 3 điểm: (i) 30/30 record tạo sau 17/08 có `first_seen − objid` ∈ [1, 3] ngày, không có giá trị âm;
  (ii) 81 dòng dồn vào cùng ngày 2024-10-11, khớp một đợt migrate hàng loạt (loại khỏi đo); (iii) SCL ESOP/quyền mua/cổ tức
  2026 có chung tiền tố `6a051616…` = 2026-05-14, sát NQ ĐHCĐ 24/04 + public 05-07.
- `first_seen` = snapshot đầu tiên có id. Bị censor trái tại 08-17, nên chỉ dùng record tạo sau 17/08.

| Đại lượng (ISS public≥2025, bỏ `not_executed` + bulk) | n | p10 | median | p90 |
|---|---:|---:|---:|---:|
| **BQ thấy − vendor tạo** (record tạo >17/08) | 30 | 1 | **1** | **2** |
| vendor tạo − public_date (âm = record có TRƯỚC ngày ghi trên dòng) — WARN | 484 | −210 | −21 | 6 |
| vendor tạo − first_disclosure — WARN | 288 | −203 | −64 | 60 |
| GDKHQ − vendor tạo — Rights | 77 | 16 | **157** | 228 |
| GDKHQ − vendor tạo — PP (riêng lẻ) | 71 | −4 | 132 | 266 |
| GDKHQ − vendor tạo — EMPL (ESOP) | 88 | 40 | 110 | 213 |
| GDKHQ − vendor tạo — DIV / Bonus (INFO) | 276 / 139 | 28 / 25 | 64 / 50 | 160 / 157 |
| GDKHQ − vendor tạo — PUBL / TRANS | 6 / 12 | −34 / −9 | **−29 / −6** | −16 / 2 |

- Record vendor tạo đúng hoặc sau GDKHQ: **40/673 (6%)**, trong đó 34 là WARN (chủ yếu PUBL, TRANS, đuôi PP).
- Bốn mã nêu tên (bảng đầy đủ trong `analyze_lag_out.txt`): SCL quyền mua 2026 vendor tạo 05-14, BQ có ≤08-17. MBB
  quyền mua 10% + cổ tức CP 15% (GDKHQ 08-11) vendor tạo 04-21 (≈112 ngày trước GDKHQ). VIB thưởng 9,5% vendor tạo 04-10
  (GDKHQ 09-10). DSC quyền mua 17,25% vendor tạo 2025-04-10 (GDKHQ 2025-10-03).

**1.4 Kết luận nguồn dẫn trước:** với Rights/PP/ESOP/DIV/Bonus, BQ đã đi trước GDKHQ hàng tháng. Nguồn khác không thêm
được gì đáng kể, và `stock_news` không dùng được làm mốc PIT vì `ingested_at` của nó là backfill 09-13. Giới hạn:
**PUBL (6 sự kiện / 2 năm) và TRANS (13) đến muộn**. Với nhóm này cảnh báo có thể tới sau GDKHQ. Nguồn dẫn trước khả
thi duy nhất là CBTT HOSE/HNX (chưa có pipeline trong repo). **Không đề xuất xây** vì mẫu quá nhỏ; chấp nhận giới hạn
và ghi ở đây.

## 2. Phân loại "tăng vốn" (đếm thật `tav2_bq.corporate_action`, event_code ISS)

| `issue_method_code` | Tên vendor | Tổng | public≥2025 | ex NULL | Hạng |
|---|---|---:|---:|---:|---|
| Rights | Quyền mua CP cho CĐ hiện hữu | 2.199 | 184 | 495 | **WARN** |
| PP | Phát hành riêng lẻ | 3.109 | 216 | 683 | **WARN** |
| EMPL | Phát hành cho CBCNV (ESOP) | 1.693 | 181 | 355 | **WARN** |
| PUBL | Phát hành rộng rãi qua đấu giá | 176 | 7 | 21 | **WARN** |
| TRANS | Chuyển từ trái phiếu chuyển đổi | 249 | 13 | 3 | **WARN** |
| MERGER | Phát hành để sáp nhập | 114 | 7 | 15 | **WARN** |
| ICRE | Phát hành cho trái chủ | 9 | 0 | 0 | **WARN** |
| BBOD | (vendor không đặt tên) | 15 | 0 | 3 | **WARN** |
| DIV | Trả cổ tức bằng CP | 2.659 | 340 | 239 | INFO |
| Bonus | Cổ phiếu thưởng | 1.538 | 164 | 96 | INFO |
| *(mã lạ tương lai)* | | | | | WARN (fail-closed) |

Ngoài ra AIS (niêm yết bổ sung, 5.001 dòng) là hệ quả của các đợt trên, không phải sự kiện tăng vốn riêng ⇒ không báo.
`value_per_share` = 0/NULL ở 100% dòng ISS. Giá phát hành chỉ suy được từ `total_value/issue_volumn` (Rights 90/184,
EMPL 87/181, PP 75/216 dòng 2025-26). **`event_description_vi` rỗng ở 100% dòng ISS 2025-26** ⇒ nguồn KHÔNG có mục đích
sử dụng vốn. Tin cảnh báo nói rõ điều này, không bịa.

## 3. Ngưỡng X (lớp A, `CAPITAL_RAISE_12M`) — `analyze_dil12.py` → `analyze_dil12_out.txt`

`exercise_ratio` dòng D 2025-26: EMPL median 1,6%, p90 5,0%, **max 5,0%** (n=102). Rights median 40,3%. PP median 35,0%.
Pha loãng THU TIỀN tích luỹ 12 tháng/mã (141 mã có ≥1 sự kiện WARN thực hiện): >5% 94 mã, >10% 92, >20% 74.
**Mã chỉ có ESOP: n=34, max 5,0%, p90 4,1%.**
⇒ **X = 10%, so sánh `>`**: tách sạch ESOP khỏi đợt huy động thật; kết quả ổn định trong cả dải 5–10% (chỉ đổi 2 mã).

Số CP lưu hành 4 quý (`ticker_financial.OShares`, 1.198 mã đang giao dịch, `q_shares.sql`): >10% 15,9%, >30% 8,8%,
p90 +25,2%. Chỉ số này gộp cả cổ tức CP/thưởng (ví dụ MBB +32% = cổ tức CP 32% GDKHQ 2025-08-13; VPB +26% chưa phân rã), nên **chỉ in làm bằng chứng phụ,
KHÔNG làm điều kiện cờ**. SCL: 22.392.839 → ≈38,84 triệu (khớp AIS 38.836.815), **+73,4%**.

**Ca SCL với điều kiện 12M:** quyền mua 35,7% GDKHQ 2025-10-17 nằm ngoài cửa sổ 365 ngày tính từ 2026-10-23 (cách 371
ngày). SCL bị bắt bởi `CAPITAL_RAISE_PENDING` (đợt 2026 đang chạy), không phải 12M. Selfcheck có cả hai ca.

**Tỉ lệ cờ dự kiến** (`flag_rate.py` → `flag_rate_out.txt`; cận dưới vì chỉ tính dòng public≥2025): asof 2026-10-29,
1.198 mã đang GD ⇒ PENDING 96 (8,0%), 12M 77 (6,4%), **có ít nhất một cờ 158 (13,2%)**. Asof 06-30: 12,6%. Các mốc quá
khứ đọc từ bảng đã upsert nên là ước lượng; mốc 10-29 là trạng thái thật hôm nay.

## 4. Thiết kế

**Thư viện chung `bin/capital_raise_lib.py`** (hàm thuần): phân hạng WARN/INFO; `is_zombie_p` / `is_stale_p` (chuyển từ
rights_issue_alert, `is_zombie_p` nay so cả **cùng phương thức**); `dilution` = `exercise_ratio`, hoặc
`issue_volumn/OShares` khi tỉ lệ = 0, không tính được ⇒ None ("CHƯA RÕ", không đoán 0); `live_events`;
`cash_dilution_12m`; `pre_entry_flags`.

**Lớp A — `lag_dd_pack.py`** (gói `data/lag_dd/<mã>_<release>.json`):

| Mã | Khi nào | Hệ quả |
|---|---|---|
| `CAPITAL_RAISE_PENDING` | có sự kiện WARN đã công bố ≤ asof, chưa GDKHQ, không phải xác sống / nghi bỏ dở | status FLAG ⇒ user thấy lúc ack (1/2/3). **Không tự loại** |
| `CAPITAL_RAISE_12M` | pha loãng THU TIỀN đã GDKHQ trong 365 ngày > 10% | như trên |
| `CAPITAL_RAISE_NA` | không đọc được nguồn phát hành | FLAG fail-closed, lỗi thật nằm trong `source_errors.capital_raise` (§29) |
| `CAPITAL_RAISE_INFO` / `CAPITAL_RAISE_NGHI_BO_DO` | cổ tức CP/thưởng sắp tới; dòng P > 183 ngày | chỉ ở `warnings`, KHÔNG đổi status/flags_hash |

Lưu ý: thêm mã cờ mới làm đổi `flags_hash` của gói có cờ đó. Ack cũ cho mã đó sẽ bị hỏi lại, đúng hành vi đã thiết kế.

**Lớp B — `rights_issue_alert.py`** ([pipeline-3c], 19:00, không cron mới):
- Quét mọi dòng ISS (`fetch_issuance`) của mã đang giữ trên mọi account live và mọi sleeve có trong `active_nav_*.json`
  (kể cả mã `excluded`).
- Một tin cho mỗi sự kiện, gộp mọi account đang giữ.
- Ba giai đoạn ANNOUNCE / DATED / (REMIND **chỉ Rights**), STALE gộp. **Khoá dedupe giữ nguyên định dạng cũ** nên
  `state/rights_issue_alert_state.json` hiện hành vẫn hợp lệ.
- Tin có: % pha loãng, giá phát hành = x% thị giá (giá `active_nav`, nguồn DNSE G1), ngày chốt (còn N phiên), mục đích
  vốn (nói rõ nguồn không có). WARN không phải Rights ⇒ "CHỈ CẢNH BÁO: bot KHÔNG tự bán/không sửa plan". INFO ⇒ "giá
  điều chỉnh qua luồng corp-action".
- **`fetch_rights` GIỮ hợp đồng chỉ-Rights**, vì `lag_rights_exit_hold.py`, `daily_nav_snapshot.py` và
  `rights_subscription.py` coi mọi dòng nó trả về là quyền mua. Mở rộng hàm này sẽ làm bot giữ lệnh thoát LAG vì ESOP.
  Có selfcheck và mutant khoá hợp đồng này.
- **Câu chữ (yêu cầu 3):** giữ nguyên "Bot TỰ giữ lệnh thoát T+25 của mã LAG tới GDKHQ…", thêm "Việc giữ này KHÔNG cấm
  thoái: user vẫn có thể thoái bằng plan (SCL là ngoại lệ — user chốt thoát 29/10/2026)". `lag_rights_exit_hold.py`
  không đổi.
- Fail-safe giữ như cũ: gửi lỗi ⇒ rc=1, state không ghi. State ghi ngay sau MỖI tin gửi thành công (§5). Vị thế cũ ⇒
  rc=3 kèm lý do. Lỗi đọc OShares ⇒ in lỗi thật, % chỉ lấy từ `exercise_ratio`.

**Dry-run thật 29/10 với state thật:** lần chạy 19:00 đầu tiên sau merge sẽ gửi **2 tin**: SCL ESOP 2,1% `P` (ANNOUNCE)
và 1 tin gộp "nghi BỎ DỞ" (DGC TRANS 2017, MBB PP 04-20, TPB ESOP 04-28, VPB PP 04-24). Không flood. Tin SCL quyền mua
đã gửi 28/10 nên không gửi lại; câu chữ mới áp cho các tin sau. Thời gian chạy 4,3 s (trần chuỗi 120 s).

**Cron (yêu cầu 4):** không thêm cron. Dòng 109 `kb/cron_registry.md` nên đổi mô tả output thành "tin Discord Trading
Daily — quyền mua + tăng vốn mọi phương thức (WARN/INFO)". Đây là file `kb/` (§13) nên **chưa sửa**, chờ Mike/user.

## 5. Bằng chứng selfcheck (chạy trong worktree, 29/10)

| Selfcheck | Kết quả |
|---|---|
| `bin/rights_issue_alert_selfcheck.py` (env -u TZ + Pacific/Kiritimati + America/New_York) | 3×PASS · **mutants 37/37 killed** |
| `bin/lag_dd_gate_selfcheck.py` (3 TZ; gồm lag_dd_ack, lag_plan_consistency_check) | 198 pass / 0 fail ×3 · **mutants 52/52 killed** |
| `lag_rights_exit_hold_selfcheck.py` | PASS, 17/17 |
| `rights_subscription_qty_selfcheck.py` | PASS, 12/12 |
| `rights_terp_price_gate_selfcheck.py` | PASS, 10/10 |
| `rights_subscription_selfcheck.py` | 75/75 |
| `exrights_price_basis_selfcheck.py` | 38/0 |
| `bash -n bin/bq_freshness_check.sh` | OK (chỉ đổi comment và chuỗi cảnh báo) |

Các ca theo yêu cầu 6, đều có trong `rights_issue_alert_selfcheck.py`:

| Ca | Mong đợi |
|---|---|
| SCL D 2025 35,7% + P quyền mua 15,38% (public 09-08) + P ESOP 2,1% | 2 ANNOUNCE; D 2025 im; 2 account gộp 169 + 107 cp |
| MBB cổ tức CP 15% | INFO, ngày chốt còn 3 phiên, không REMIND |
| Riêng lẻ giả lập (ratio 0) | % = vol/OShares 20%; giá 15.000 = 75% thị giá |
| ESOP giả lập | không REMIND |
| Mã không giữ | im |
| P riêng lẻ > 183 ngày | chỉ STALE |
| Zombie | cùng phương thức thì bỏ, khác phương thức thì vẫn báo |
| Mã phương thức lạ | WARN |
| Lớp A | SCL 23/10 ⇒ PENDING kèm +73,4%; 35,7% sau GDKHQ ⇒ 12M; quá 365 ngày ⇒ hết; ESOP 5% ⇒ không; 11% ⇒ có; đúng 10% ⇒ không (float `1,10−1 = 0,1000…09` từng làm ca này đỏ, đã thêm tolerance); cổ tức CP đã thực hiện không tính 12M; công bố sau asof ⇒ không nhìn trước |
| Tích hợp `build_pack` | PENDING ⇒ FLAG; nguồn lỗi ⇒ `CAPITAL_RAISE_NA` + lỗi thật; INFO ⇒ vẫn CLEARED + warning |

Mutant trọng yếu (đều bị giết): REMIND cho mọi phương thức; ngưỡng `>`→`≥`; X 10%→5%; cửa sổ 12M bỏ giới hạn; tính cả INFO
vào 12M; PENDING gồm cả INFO; bỏ điều kiện cùng phương thức ở zombie; `fetch_rights` trả mọi phương thức; bỏ `held`; bỏ
khoảng cách ngày chốt; bỏ so thị giá; ghi state trước khi gửi.

**Phản thực tế thật** (BQ live, asof 2026-10-23, `lag_dd_pack.py --tickers SCL --release-date 2026-10-19 --dry-run`, thư
mục tạm): status FLAG, cờ `CAPITAL_RAISE_PENDING` + `EQ_PHAI_THU_TANG` (+ `ANOMALY_NA` do chạy lùi ngày, không liên quan).
Dòng P 0,15384615 đã có trên snapshot từ 09-11 ≤ 10-23 ⇒ **không nhìn trước**.

## 6. Giới hạn / việc mở

- Tỉ lệ vendor 0,15384615 (= 2/13) khác tỉ lệ thật 0,154453 khoảng 0,06pp. Tin dùng số vendor. Số CP được mua là cận
  dưới, user đối chiếu thông báo VSDC.
- Dedupe ANNOUNCE theo `id`: khi vendor đổi tỉ lệ trên CÙNG id (SCL 0,1851 → 0,1538 ngày 09-11), hệ **không báo lại**.
  Có thể thêm khoá theo tỉ lệ nếu user muốn (chưa làm, tránh thêm tin).
- SCL ESOP P 2,1% (public 05-07) có thể chính là đợt D 2,43% (GDKHQ 07-30) với tỉ lệ đã đổi. Zombie-check so tỉ lệ
  chính xác nên không bỏ được dòng này ⇒ có thể là 1 tin thừa. Nó sẽ tự rơi vào STALE sau 183 ngày (06/11).
- Lớp B vẫn phụ thuộc độ tươi `active_nav` (SCL trễ 2 phiên). Lớp A mới là chốt chặn trước vào lệnh. Lớp B chỉ đảm
  bảo việc nhắc trong chu kỳ.
- PUBL/TRANS đến muộn (§1). Sleeve ngoài account DNSE live (ví dụ RocketX, tiền riêng user) không được phủ, đúng chủ đích.
- Chưa chạy `freshness_ops_selfcheck.py` vì nó đọc `bq_freshness_check.sh` ở repo chính, không phải worktree. Thay đổi
  ở script đó chỉ là chuỗi.

## Files

`q_lag.sql`, `q_lag.csv`, `analyze_lag.py`, `analyze_lag_out.txt` (snapshot / 4 mã nêu tên) · `q_lag2.sql`, `q_lag2.csv`,
`analyze_lag2.py`, `analyze_lag2_out.txt` (độ trễ 2025-26) · `q_dil12.sql`, `analyze_dil12.py`, `analyze_dil12_out.txt`
(ngưỡng X) · `q_shares.sql`, `q_shares.csv` (OShares 4 quý) · `flag_rate.py`, `flag_rate_out.txt`.
Code: `bin/capital_raise_lib.py` (mới), `bin/rights_issue_alert.py`, `bin/lag_dd_pack.py`, 2 selfcheck,
`bin/bq_freshness_check.sh` (chuỗi).

## 7. Cập nhật sau arch-review + quyết định user (29/10/2026 15:4x)
arch-reviewer: NEEDS_CHANGES (lớp B đạt; lớp A đưa PENDING vào FLAG ⇒ gói DD FLAG chưa ack = đứng ngoài plan, vd VPB asof 23/10 bị FLAG vì dòng PP P 6,24%).
**User chọn (b)**: `CAPITAL_RAISE_PENDING` và `CAPITAL_RAISE_12M` chỉ là WARNING trong `pack['warnings']` (gói vẫn CLEARED, `flags_hash` không đổi, không chặn mua),
theo tiền lệ DCF_RICH_NHE. Chỉ `CAPITAL_RAISE_NA` (nguồn lỗi) còn là cờ fail-closed. Bỏ chuỗi cố định "SCL là ngoại lệ…" khỏi mẫu tin Rights.
Selfcheck sau sửa: `rights_issue_alert_selfcheck` 37/37 mutant (3 TZ), `lag_dd_gate_selfcheck` 52/52 (env -u TZ + Tokyo; mutant `flags += cr_flags` thay bằng mutant `[1]→[0]`), thêm ca `flags_hash` không đổi khi có cảnh báo; 6 selfcheck lân cận PASS. Commit `87afedea3`.
Nit còn lại (không blocker, chưa làm): tin INFO cổ tức/thưởng trùng `nav_exdate_forecast`; `fetch_oshares` không giới hạn asof (chỉ ảnh hưởng chạy hồi cứu); không báo lại khi vendor đổi tỉ lệ trên cùng id; `_f` trả 0 khi tỉ lệ hỏng.
