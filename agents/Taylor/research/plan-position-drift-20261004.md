# Cờ "vị thế đổi sau khi lập plan" — HƯỚNG NHẸ cho rủi ro Q5 (2026-10-04)

Job `Taylor_20261004_024243`, user duyệt 2026-10-04 09:40. Branch `feat/plan-position-drift-flag-20261004`.
CHỈ CỜ / BÁO — không đụng `bot_execute.py` / `executor.py` / `exdate_gate.py` / sinh plan / `PlannedOrder`.

## Đã làm
- `bin/plan_position_drift_check.py` (mới) — mỗi account (lọc `account_no` ở mọi lần đọc, §12): đọc DNSE
  SỐNG (§6), so với 2 mốc trong `dnse_raw_<ngày>.jsonl`:
  - **mốc plan** = bản ghi `positions` SỚM NHẤT trong [18:50, 19:30] (mọi lần đọc broker — kể cả của
    DollarBill — tự log vào file này). Plan JSON không chứa snapshot vị thế, và bị viết lại 20:20-20:40 ⇒
    mtime vô dụng. Không có bản trong cửa sổ ⇒ FALLBACK bản cuối trước 19:30, ghi rõ trong báo cáo.
  - **mốc phiên** = bản cuối trước 18:50 — bắt credit SAU phiên nhưng TRƯỚC/TRONG lúc lập plan (VPB 09-23,
    TPB 10-01): plan thấy KL mới nhưng giá ref vẫn là giá đóng cửa cũ.
  - KL lệch trừ phần khớp lệnh thật (diff `fillQuantity` sổ lệnh); không loại trừ được ⇒ vẫn cờ + ghi chú.
- `bin/send_plan_report.sh` — nhúng khối kết quả (kiểm lại NGAY lúc 21:00; lỗi mà lần 20:50 kiểm được ⇒ in
  cả hai). Fail-soft nhưng không im lặng: script lỗi/treo/in rỗng ⇒ dòng "KHÔNG KIỂM ĐƯỢC" + stderr thật.
- `bin/plan_position_drift_check_selfcheck.py` — 76 assertion có tên + 34 đột biến (29 trên script, 5 trên
  khối shell), 34/34 bị giết.

## Phát hiện đo được (đổi thiết kế)
`marketPrice` của positions KHÔNG đổi trong phiên — chỉ đổi khi DNSE chạy **batch cuối ngày**, batch đó cập
nhật `modifiedDate` của MỌI lô và cũng là lúc credit corp-action xuất hiện. Giờ batch đo 60 phiên 08-01→10-02:
18:52 → 20:15 tuỳ ngày (08-14: 19:09; 09-08/09-14: chỉ thấy lúc 20:15). Hệ quả:
- So giá chặt (1%) với mốc TRƯỚC batch báo nhầm cả danh mục (replay 08-14 bản đầu: 14/14 mã) ⇒ ngưỡng giá
  theo độ tươi của lô: cả 2 bản đã qua batch ⇒ 1%; mốc trước batch ⇒ 15% (biên độ rộng nhất).
- Lúc kiểm mà batch CHƯA chạy cho mã nào ⇒ không được kết luận "không đổi" ⇒ CANNOT_CHECK (hoặc ghi chú nếu đã có cờ).

## Replay dnse_raw thật (bản ghi 20:50 không có ⇒ mô phỏng từ bản cuối ≤ 20:50, nói rõ "MÔ PHỎNG")
| Ngày | SpaceX | ZaloPay |
|---|---|---|
| 08-14 BID (credit 19:09 + lô 2 20:15) | BID 1.100→1.175, mốc plan 19:03 | BID 400→427, mốc plan 19:03 |
| 09-23 VPB (credit ~18:58) | VPB 1.100→1.386 (sau phiên) | VPB 1.200→1.512 (sau phiên) |
| 10-01 TPB (credit trước 19:03) | TPB 200→230 (sau phiên) — plan có lệnh BÁN 200cp @12.100 ⇒ đúng ca rủi ro | không đổi (đã bán hết) |

Quét toàn bộ phiên 08-01→10-02 (cả 2 account): bắt thêm mọi corp-action thật đã biết (VIX 08-19, MSB 08-27,
MBB 08-28, VIB 09-09, DGC 09-11 giá −17,5%). 1 cờ do thiếu dữ liệu replay: SCL 09-30 SpaceX 1.500→0 — user bán
tay qua app, ngày đó không có bản ghi sổ lệnh nào của SpaceX trong dnse_raw ⇒ cờ kèm "KL GIẢM: nhiều khả năng do
BÁN". Chạy sống, sổ lệnh đọc trực tiếp từ DNSE ⇒ được loại trừ. Ngày batch chưa chạy trước bản ghi cuối (08-04/06/10,
bản cuối 19:10) ⇒ CANNOT_CHECK, đúng thiết kế.

## Chưa đo được — cần xem lượt chạy sống đầu tiên
- DNSE `GET /orders` lúc 20:50 trả gì (sổ trong ngày hay rỗng)? Chưa có bản ghi `orders` nào sau 15:00 trong
  dnse_raw. Code phòng thủ: rỗng ⇒ lùi về bản `orders` cuối trong dnse_raw, không có ⇒ cờ kèm ghi chú.

## Đề xuất cron (Mike cài SAU khi tự kiểm — host UTC)
```
50 13 * * 1-5 /home/trido/thanhdt/WorkingClaude/mike/bin/for_each_live_account.sh /home/trido/thanhdt/WorkingClaude/mike/bin/plan_position_drift_check.py >> /home/trido/thanhdt/WorkingClaude/mike/logs/plan_position_drift.log 2>&1   # 20:50 ICT T2-T6 - co "vi the doi sau khi lap plan" (Q5 huong nhe, CHI CO/BAO): DNSE song vs ban doc dau cua plan (~19:03) + moc phien; bus finding khi co, error khi khong kiem duoc. SAU auto_exit_inject 20:40, TRUOC send_plan_report 21:00 (send_plan_report tu kiem lai luc 21:00). Ghi 1 ban positions vao dnse_raw cho luot corp_action_auto_confirm 21:05. User duyet 2026-10-04 (Taylor_20261004_024243).
5 14 * * 1-5 timeout 900 /home/trido/thanhdt/WorkingClaude/mike/bin/corp_action_auto_confirm.py >> /home/trido/thanhdt/WorkingClaude/mike/logs/corp_action_auto_confirm.log 2>&1   # 21:05 ICT T2-T6 - LUOT 2 cung ngay (luot 1 19:25): bat credit corp-action muon sau plan (BID 08-14 lo 2 20:15). Idempotent: so broker key (mode,ticker,credit_day,verdict) + vendor already_confirmed_set; khoa fcntl chung. Mode theo MIKE_CA_BROKER_SOURCE (mac dinh shadow). Lech 5' khoi send_plan_report 21:00 theo _adding-cron-policy. (Taylor_20261004_024243)
```
**Lệch so với dispatch (21:00 → 21:05):** `_adding-cron-policy.md` cấm 2 job gọi mạng trùng phút; 21:00 đã có
`send_plan_report` (nay cũng gọi DNSE). Nếu Mike muốn đúng 21:00: `0 14 * * 1-5 ...` — chức năng không đổi.

## Lượt `corp_action_auto_confirm.py` thứ hai — KHÔNG cần sửa code
- Vendor: `already_confirmed_set()` bỏ qua mã đã CONFIRMED lúc 19:25; "broker chưa credit hôm nay" lúc 19:25 ⇒
  21:05 thấy credit ⇒ CONFIRMED lần đầu (đúng mục đích). Câu hỏi qua `_ask_once` (sổ) ⇒ không hỏi lại.
- Broker (shadow mặc định): `ledger_key = [mode, ticker, credit_day, verdict]` ⇒ cùng verdict = im lặng; verdict đổi
  (vd INSUFFICIENT/AMBIGUOUS lúc 19:25 vì credit dở → CONFIRMABLE lúc 21:05) = mục MỚI ⇒ đúng 1 finding mới.
  Marker ngày `.lockfail/.vendorcrash/.brokercrash-<D>`: lượt 2 cùng ngày KHÔNG hỏi lại sự cố đã hỏi lúc 19:25 (chấp nhận).
- Khoá fcntl chờ tối đa 120s, 2 lượt cách nhau 1h40 ⇒ không tranh. Phụ thuộc ngầm "phải có bản ghi `positions` SAU
  credit": 20:15 `compute_active_nav_all` + 20:50 script này đều ghi ⇒ có.
- Bằng chứng: `corp_action_broker_detect_selfcheck.py` 248/248 (B4/B8/B11 chạy lại idempotent, G1 2 lượt),
  `corp_action_auto_confirm_selfcheck.py` 29/29 — trên master hiện tại.
- **Xung đột cần biết:** `feat/broker-primary-20261003` (chưa merge, arch-review NEEDS_CHANGES) sửa 211 dòng
  `corp_action_auto_confirm.py` + đảo vendor→broker. Branch này KHÔNG đụng file đó ⇒ không xung đột git, nhưng khi
  broker-primary merge thì phân tích idempotency trên phải kiểm lại (đặc biệt MAJOR-3 "không re-verify sau ex").

## Dòng `kb/cron_registry.md` (dán cùng commit cài crontab + 1 dòng CHANGELOG)
| **20:50 (T2-T6)** — ĐỀ XUẤT 2026-10-04 (`Taylor_20261004_024243`, user duyệt hướng nhẹ Q5) | `for_each_live_account.sh` → `mike/bin/plan_position_drift_check.py --account <acct>` | (1) DNSE **LIVE** positions + orders (§6, không BQ); (2) `data/execution_logs/dnse_raw_<D>.jsonl` bản ghi `positions`/`orders` — producer: mọi lần đọc broker (DollarBill/EOD ~19:03-19:15, `compute_active_nav_all` 20:15); (3) `data/trade_plans/plan_<acct>_<T+1>.json` (chỉ để gợi ý hành động) | `mike/state/plan_position_drift/<acct>_<D>.json` (atomic) + 1 bản `positions` vào dnse_raw + bus `finding plan-position-drift-<acct>-<D>` / `error plan-position-drift-cannot-check-<acct>-<D>` (1 lần/nội dung) | `send_plan_report.sh` 21:00 (kiểm lại + nhúng) · `corp_action_auto_confirm` 21:05 (bản positions) · user | cần T; sau batch cuối ngày DNSE (đo 18:52-20:15) ⇒ 20:50; trước 21:00. Runtime: 2 lệnh gọi DNSE/account | rc 2 = KHÔNG KIỂM ĐƯỢC (log + bus error); không có đường all-clear im lặng; selfcheck `plan_position_drift_check_selfcheck.py` |
| **21:05 (T2-T6)** — ĐỀ XUẤT 2026-10-04 (cùng job) — LƯỢT 2 của dòng 19:25 | `mike/bin/corp_action_auto_confirm.py` (bọc `timeout 900`) | như dòng 19:25 + bản `positions` 20:15/20:50 sau credit muộn | như dòng 19:25 (sổ 2 pha, khoá chung) | như dòng 19:25 | sau 20:50 (bản positions mới), lệch 5' khỏi `send_plan_report` 21:00 | idempotent theo `ledger_key` (gồm verdict) + `already_confirmed_set`; xem dòng 19:25 |
