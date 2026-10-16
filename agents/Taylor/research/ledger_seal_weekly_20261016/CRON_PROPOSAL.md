# Đề xuất cron — `ledger_seal_weekly` (CHỈ SOẠN, CHƯA CÀI)

Job Taylor_20261016_033549 · thiết kế user duyệt 16/10/2026 10:35 ICT (topic 1558645322085826593).
Mike cài SAU arch-review + merge nhánh `feat/ledger-seal-weekly-20261016`. Backup crontab trước khi cài
(`state/crontab_backups/crontab_pre_sealweekly_<ts>.txt`), cập nhật bảng chính + CHANGELOG CÙNG commit (§11).

## 1. Dòng crontab (host UTC; 00:30 UTC thứ Bảy = 07:30 ICT thứ Bảy)

```
30 0 * * 6 cd /home/trido/thanhdt/WorkingClaude && . ./wc_env.sh && TZ=Asia/Ho_Chi_Minh mike/bin/fund_bench_cron.sh ledger_seal_weekly timeout 1500 env -u WC_ROOT python3 mike/bin/ledger_seal_weekly.py >> /home/trido/thanhdt/WorkingClaude/mike/logs/ledger_seal_weekly.log 2>&1   # 07:30 ICT thu Bay - chot so don vi quy toi thu Sau tuan truoc (>=5 phien tre), SpaceX roi ZaloPay; fail-closed => Trading Daily; moc SEAL_MD5 -> kb/fund_ledger_anchors.txt + bus (user duyet 16/10/2026, job Taylor_20261016_033549)
```

⚠️ Comment KHÔNG được nhắc tên file của các writer nav_history. Wrapper đã so khớp theo tên file của
từng đối số (selfcheck A15 + mutant M13), nên comment có nhắc thì cũng không tự chặn. Dù vậy, cứ giữ
comment sạch.
`timeout 1500` > 2 × trần 600s mỗi lần gọi CLI (runtime thật ≈ 1–2s/TK trên sandbox).

## 2. Dòng bảng chính `kb/cron_registry.md` (chèn cạnh dòng 06:55 `ledger_anchor_check`)

| Sat 07:30 ICT — **CÀI MỚI <ngày cài>** (Mike, user duyệt 16/10/2026 10:35 ICT topic 1558645322085826593; host UTC `30 0 * * 6`; backup `state/crontab_backups/crontab_pre_sealweekly_*.txt`) | `mike/bin/fund_bench_cron.sh ledger_seal_weekly` → `ledger_seal_weekly.py` → `nav_unit_ledger.py --account <TK> --seal --real-data --asof <D>` (SpaceX rồi ZaloPay; D = phiên cuối ≤ thứ Sáu tuần trước có ≥5 phiên trễ) | `data/execution_logs/nav_history_{TK}.csv` (PRODUCER: `eod_trading_report.sh` 19:10 / `nav_snapshot_daily.sh` 19:50 / `nav_sync_retry.sh` ≤21:45, T2-T6; đính chính tay) + `data/account_cash_flows.json` + `data/account_inception.json` + sổ/manifest hiện có | `data/execution_logs/nav_unit_ledger_{TK}.csv` + `.manifest.jsonl` (kho bất biến, chỉ thêm) · `kb/fund_ledger_anchors.txt` (thêm dòng `SEAL_MD5`, nguyên tử, idempotent) · bus `Mike finding fund-unit-ledger-seal-<YYYYMMDD>` · rc≠0 ⇒ Trading Daily (8 dòng cuối đầu ra thật) | `ledger_anchor_check` 06:55 hằng ngày (đọc mốc mới nhất) · `consolidate.sh` :07 commit `kb/` · đính chính `fund_restatement.py` | Dòng chốt trễ ≥5 phiên ⇒ nav_history đã qua mọi lượt ghi/đính chính tự động; thứ Bảy không có writer nào chạy | FAIL-CLOSED: CLI rc≠0 (trừ NothingToSeal) ⇒ dừng, không chốt TK sau; KHÔNG BAO GIỜ thêm --accept-preclose/--restate/--force. Từ chối (rc=4) khi khoá `state/ledger_seal_weekly.lock` bận, trong khung 19:00–22:00 ICT, hoặc có tiến trình ghi nav_history. Code ngoài cây canonical chốt vào cây thật ⇒ rc=64. Selfcheck `bin/ledger_seal_weekly_selfcheck.py` (46 assert, env -u TZ + Kiritimati), mutation 14×2. |

## 3. Dòng CHANGELOG `kb/cron_registry/CHANGELOG.md` (trên cùng)

- **<ngày cài> — THÊM `30 0 * * 6` ledger_seal_weekly (07:30 ICT thứ Bảy)** — Mike cài theo đề xuất job
  Taylor_20261016_033549 (user duyệt 16/10/2026 10:35 ICT). Bốn câu hỏi §11: (1) đọc nav_history /
  cash_flows / inception (file local, writer T2-T6 tối); (2) tươi: dòng của D đã ổn định sau 21:45 ngày D,
  và D trễ ≥5 phiên; (3) cần dữ liệu ≤ thứ Sáu tuần trước, không cần T, không BQ; (4) tiêu thụ: ledger_anchor_check
  06:55 sáng CN (đọc mốc mới), consolidate :07 (commit kb/), không có deadline giao dịch.

## 4. Bốn câu hỏi §11 (`kb/cron_registry/_adding-cron-policy.md`)

1. **Đọc gì, vintage nào?** Chỉ file local, không BQ, không DNSE: `nav_history_{TK}.csv` (ghi bởi EOD 19:10, nav_snapshot_daily
   19:50, nav_sync_retry */15 tới 21:45, T2-T6; đính chính tay qua `nav_history_corrections.jsonl`),
   `account_cash_flows.json` (người khai), `account_inception.json`, cùng sổ + manifest hiện có. Không có
   cache BQ ẩn: chuỗi import là `nav_unit_ledger` → `account_cash_flows` → `trading_bot.vn_market`, không ai source
   `wc_env.sh` để lấy BQ.
2. **Nguồn tươi lúc nào?** Dòng của phiên D chỉ ổn định sau lượt retry cuối 21:45 (D) và các đính chính
   sau đó. Mốc chốt D trễ ≥5 phiên ⇒ đã qua mọi lượt ghi tự động ≥ 4 ngày. Artifact cần cho D có từ
   ~19:10–21:45 ngày D, nên buffer thực ≥ 5 ngày.
3. **T hay T-1?** Không cần T. Chỉ cần dữ liệu ≤ thứ Sáu của tuần trước. Cổng của CLI còn tự chặn
   `asof ≥ hôm nay` (giờ ICT).
4. **Ai tiêu thụ, deadline?** `ledger_anchor_check` 06:55 sáng hôm sau (CN) đối chiếu mốc mới. `consolidate.sh`
   08:07 thứ Bảy commit `kb/fund_ledger_anchors.txt`. Báo cáo tuần thứ Bảy 09:00 KHÔNG đọc sổ trên đĩa,
   vì `nav_period_returns` dựng chuỗi trong bộ nhớ, nên không phụ thuộc giờ.

**Xung đột/buffer:** cùng phút 00:30 UTC thứ Bảy có `paper_programs_daily_report.sh` (`30 0 * * 2-6`).
Hai job không dùng chung file nào. Job này chạy ≈2–4s, chỉ dùng CPU local, không gọi mạng, nên trùng
phút vô hại. `hose_membership_refresh` chạy 07:40, `refresh_fa_ratings_8l` 08:30: đều khác file. Không
writer nav_history nào chạy thứ Bảy. Nếu vẫn có writer, wrapper kiểm tiến trình và từ chối (rc=4).
