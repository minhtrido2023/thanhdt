# Quỹ bước 4 — vòng 2 (arch-review NEEDS_CHANGES) — job Taylor_20261014_091148

Nhánh `feat/fund-step4-benchmark-20261014` (wt `agents/Taylor/wt-step4-1014`), từ 6a60a0bbc. KHÔNG merge, KHÔNG
cron, `data/` thật không sửa (xem "Sự cố" — có 1 dòng sót do selfcheck chạy song song).

| Mục | Commit | Bằng chứng |
|---|---|---|
| B2 `--sleeve bot` SleeveError ⇒ rc=3 "chưa có số (lý do)" | 94804b24a | selfcheck 6 ca; bản sao thật: rc=3, render 15 ô `chưa có số (SleeveError (thiếu …sleeve_scope.json…))`, cổng PASS |
| B1 mốc VN-Index "từ khi bắt đầu" theo TK (`index_anchor_date`) | 131ea7abf | `byte_proof_r2/`: SpaceX→09-30 giá **−4,913%** (mốc 30/06); ZaloPay mốc 06/07 không đổi; thiếu trường ⇒ rc=1 + lý do. Kiểm kê: `published_inventory.md` (9 ô cần đính chính) |
| B3 G1 lấy tập phiên từ chuỗi VNINDEX (BQ ∪ DNSE) | 773a9e432 | Tết 2026-01-30→03-02 hết G1 oan; 12/12 năm 2014-2025 bản cũ oan → mới 0 |
| B4 giết N1/N6/N9/N11 | cafcac529 | `mutants_reviewer_harness_final.txt` (HEAD 8d39846be): 9/9 đích CHẾT, N10 đối chứng sống |
| N-b S4 hằng đúng | 10e84dd2c | S4 chuyển sang consumer (file b sửa tay ⇒ chưa có số) |
| N-a cổng 3.2 NFC/"luỹ", thiếu bảng ⇒ CHẶN, cột TK + WTD/MTD | 81856c2cd | selfcheck 40→55; ca NFD bắt lỗi thật (chú thích so trên text chưa chuẩn hoá) |
| N-e `SpaceX_ZaloPay_*` | 81856c2cd | mỗi TK một bảng; thiếu bảng 1 TK ⇒ chặn |
| N-d hose refresh ±5% + dọn .tmp | 82dfff5cb | selfcheck mới 8 assertion, 3 mutant tay chết |
| N-c cron lỗi ⇒ Trading Daily | 8d39846be | `fund_bench_cron.sh` + selfcheck 9 assertion; chỉ SOẠN trong `cron_proposed.txt` |

## Byte master vs nhánh (`byte_proof_r2.sh`)
17/17 cặp (SpaceX+ZaloPay × 9 ngày, trừ ZaloPay 07-03 rc=1 cả hai — trước go-live) BẰNG từng byte sau khi bỏ khối
`benchmark` ⇒ tỉ suất danh mục/pnl/mwr không đổi.

## §23 / §16
32 selfcheck phụ thuộc (grep import các module đã sửa) × {`env -u TZ`, `TZ=Pacific/Kiritimati`}:
- sandbox /tmp: nhánh 25/32 PASS; 7 lỗi GIỐNG HỆT master cùng sandbox (thiếu git/module/cấu hình trong /tmp).
- 7 cái đó chạy tại chỗ: eod_trading_report_account_filter, exdate_frame, failopen_batch1, report_return_gate,
  nav_scripts_2account PASS cả 2 TZ ở worktree; paper_report_render + report_delivery_ledger lỗi ở worktree NHƯNG
  lỗi y hệt ở worktree đối chứng master cùng độ sâu (đường `../../paper_entry_adjust.py`, sổ canonical) ⇒ bố cục
  worktree, không phải hồi quy; PASS ở canonical.

## ⚠️ Merge phải đi kèm `data/account_inception.json`
Code đọc `index_anchor_date` BẮT BUỘC: thiếu ⇒ `nav_period_returns.py` rc=1 cho MỌI kỳ (kể cả tỉ suất danh mục) ⇒
cổng period-return chặn mọi weekly/monthly. Áp `account_inception.json.proposed` CÙNG lúc merge.

## Sự cố (đã báo bus `error selfcheck-parallel-leak-nav_history_ZaloPay-20261014`)
Chạy song song 2 bản `nav_scripts_2account_selfcheck.py` (canonical + worktree) ⇒ khôi phục đè nhau ⇒ sót 1 dòng
`2026-10-14 …16:38:50` trong `data/execution_logs/nav_history_ZaloPay.csv` thật. Cron 19:10 (`daily_nav_snapshot.py:1579`
xoá-rồi-ghi dòng cùng ngày) sẽ thay bằng số EOD. Taylor bị chặn ghi `data/` nên không tự xoá.

## KHÔNG làm / chưa kiểm
- Không sửa báo cáo cũ (B1 chỉ kiểm kê). Ảnh `*_cumret.png` chưa kiểm mốc.
- Lý do "chưa có số" của dòng b in nguyên đường dẫn file (nội bộ, chỉ ZaloPay) — chưa rút gọn.
- `.lock` của `vnindex_total_return` cố ý giữ (flock file bền).
