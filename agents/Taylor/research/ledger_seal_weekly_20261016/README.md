# ledger_seal_weekly — cron chốt sổ đơn vị quỹ hằng tuần (job Taylor_20261016_033549)

Nhánh `feat/ledger-seal-weekly-20261016`, CHƯA merge, CHƯA cài cron. Không sửa `nav_unit_ledger.py`
(§23: không đụng lõi ⇒ không cần chạy selfcheck phụ thuộc của nó).

## File
- `bin/ledger_seal_weekly.py` — wrapper (docstring = đặc tả đầy đủ, mã thoát 0/1/4/64).
- `bin/ledger_seal_weekly_selfcheck.py` — 46 assert: phần A dùng CLI giả (stub), phần B tích hợp
  `nav_unit_ledger.py` THẬT trên bản sao /tmp, cuối cùng kiểm md5 dữ liệu thật không đổi.
- `CRON_PROPOSAL.md` — dòng crontab + dòng bảng chính + CHANGELOG + 4 câu hỏi §11 (CHỈ SOẠN).
- `mutants.py` + `mutants_run.txt` — 14 đột biến × 2 TZ = 28/28 bị bắt.
- `selfcheck_TZunset.txt`, `selfcheck_TZkiritimati.txt` — đầu ra thật, 46/46 mỗi TZ.
- `demo_fund_bench_cron_tk2_fail.txt` — đầu ra thật khi bọc bằng `fund_bench_cron.sh` (stub notify), ca TK2 lỗi.

## Hành vi (đo, không giả định)
| Ca | rc | Mốc `kb/fund_ledger_anchors.txt` | Bus |
|---|---|---|---|
| Cả 2 TK chốt được | 0 | +1 dòng/TK (kèm comment ngày) | 1 finding/TK, topic `fund-unit-ledger-seal-<YYYYMMDD>` |
| Chạy lại, SEAL_MD5 trùng mốc mới nhất | 0 | không đổi | không post lại |
| NothingToSeal (rc=2 + dấu `[NothingToSeal]` của ĐÚNG TK) | 0 | không đổi | không |
| rc=2 khác (SealGateError, LedgerDrift, Integrity…), rc=1 | 1 | TK lỗi: không; TK trước đó: ĐÃ ghi | TK trước: đã post |
| rc=0 mà không có ĐÚNG MỘT dòng `SEAL_MD5 <TK>` | 1 | không | không |
| Ghi mốc lỗi / post bus lỗi | 1 | (bus lỗi: mốc đã ghi) | — |
| CLI quá trần 600s | 1 (CLI 124) | không | không |
| Khoá bận / 19:00–22:00 ICT / có tiến trình ghi nav_history | 4 | không gọi CLI | không |
| Code worktree/bản sao sắp chốt vào cây dữ liệu thật | 64 | không gọi CLI | không |

**asof** = phiên d cuối cùng ≤ thứ Sáu tuần trước mà trong (d, hôm nay) có ≥ 5 phiên. Lịch phiên dùng
`account_cash_flows._is_session_day`, CÙNG lịch với cổng "thiếu dòng phiên" của nav_unit_ledger. Kết quả
đo: T7 17/10 → 09/10, T7 24/10 → 16/10. Sau lễ 31/8–2/9/2026 (T7 05/09) → 25/08, vì 28/08 mới có 3
phiên trễ. Lễ 30/4–1/5 (T7 02/05) → 22/04. Tết 2027 tiêm giả định (8–12/02): T7 13/02 → 29/01,
T7 20/02 → 05/02.

## Phát hiện cần Mike/user biết
1. **Lần chạy ĐẦU TIÊN (T7 17/10) sẽ là NothingToSeal cả 2 TK, rc=0, im lặng.** Sổ thật đã chốt tay tới
   15/10, còn asof của ngày đó là 09/10. Lần chốt thật đầu tiên rơi vào T7 24/10, chỉ thêm đúng dòng 16/10.
2. **`trading_bot/vn_market.py` CHƯA khai Tết Âm lịch** (comment trong file ghi "xử lý sau"). Nếu tới
   02/2027 vẫn chưa khai, asof tuần sau Tết sẽ trễ ít hơn 5 phiên THẬT. Cổng của nav_unit_ledger sẽ coi các
   ngày Tết là phiên thiếu dòng ⇒ từ chối, tức là vẫn fail-closed và Trading Daily nhận báo, không chốt sai.
   Việc này cần khai `_VARIABLE_HOLIDAYS` 2027 trước tháng 2, không thuộc job này.
3. **Thông báo lỗi của `fund_bench_cron.sh` có tiêu đề cứng** "Quỹ bước 4 … bảng 3.2 sẽ in chưa có số".
   Câu này sai ngữ cảnh cho `ledger_seal_weekly`, và cả cho `ledger_anchor_check` đang chạy. Thêm nữa
   Discord chỉ thấy 8 dòng cuối, tức là đúng 8 dòng CLI, nên mất dòng "đã chốt+ghi mốc: SpaceX" của
   wrapper (dòng đó vẫn còn trong log). Không sửa `fund_bench_cron.sh` vì đó là file dùng chung, ngoài
   phạm vi job. Đề xuất: biến `FUND_BENCH_HEADER` tuỳ chọn.
4. **Kẽ hở đã biết:** nếu bị giết đúng giữa lúc "CLI chốt xong" và "ghi mốc" (cửa sổ cỡ mili-giây), sổ có
   bản ghi mới mà file mốc không có. `ledger_anchor_check` 06:55 sáng hôm sau sẽ báo LỆCH (mốc mới nhất
   ≠ md5 sổ) ⇒ phát hiện được, nhưng không tự vá. Lượt kế tiếp sẽ là NothingToSeal và cũng không vá.
   Cách vá: chép tay dòng SEAL_MD5 lấy từ log, hoặc từ `--verify-anchor` sau khi kiểm manifest. Wrapper cố ý
   KHÔNG tự suy mốc từ trạng thái đĩa, vì làm vậy là hợp thức hoá đúng thứ mốc ngoài kho có nhiệm vụ bắt.
5. **Commit file mốc:** `consolidate.sh` (cron `7 * * * *`) chạy `git add kb/` rồi commit `-- kb/` mỗi khi
   có event mới, và finding bus của wrapper chính là event mới đó. Vì vậy file mốc được commit trong ≤ 1
   giờ (≈ 08:07 thứ Bảy). Nếu commit kẹt, consolidate tự báo `⛔ … KHÔNG commit được` qua notify.sh.

## Việc Mike làm sau
1. Arch-review nhánh, merge vào master của repo mike.
2. Chạy lại selfcheck từ cây canonical, dưới cả hai TZ:
   `env -u TZ python3 mike/bin/ledger_seal_weekly_selfcheck.py` và
   `TZ=Pacific/Kiritimati python3 mike/bin/ledger_seal_weekly_selfcheck.py`. Kỳ vọng 46/46 mỗi lần.
   Khi chạy từ canonical, A17 (guard) dùng thư mục tạm trong `mike/state/` và vẫn đúng.
3. Kiểm thử chỉ-đọc: `python3 mike/bin/ledger_seal_weekly.py --print-asof`.
4. Cài crontab theo `CRON_PROPOSAL.md` §1. Backup trước, cập nhật bảng chính + CHANGELOG CÙNG commit.
5. Sau T7 24/10: xác nhận log có `SpaceX: ĐÃ CHỐT tới 2026-10-16`, file mốc có thêm 2 dòng, và CN 25/10 06:55
   `ledger_anchor_check` báo OK.
