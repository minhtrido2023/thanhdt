# Chuỗi CCTG nhóm ngân hàng ngay sau Big-4 (VPB/MB/TCB/ACB) — job Taylor_20261013_082516

Nhánh `feat/cctg-tier2-banks-series-20261013` @ 7ec10026 (repo ngoài, worktree `wt-cctgt2-1013`), CHƯA merge.

| File ở đây | Nội dung |
|---|---|
| `selfcheck_*.txt` | 4 lượt `cctg_tier2_series_selfcheck.py` (`env -u TZ`, Kiritimati, Etc/GMT+12, ICT) — 48/48 |
| `mutants.py`, `mutants_out.txt` | 36 mutant, 35 bị bắt, 1 sống (M41) |
| `old_writer_run.txt` | selfcheck chạy với writer của `main` ⇒ đỏ |
| `regress_*.txt` | 5 selfcheck hồi quy |
| `prod_snapshot.py`, `prod_snapshot_{before,after}.txt` | đầu ra consumer trên code + dữ liệu production trước/sau khi ghi 3 dòng mốc |
| `write_baseline.py`, `write_baseline_out.txt` | lệnh đã ghi 3 dòng mốc vào `data/cctg_rate_vn_tier2_events.csv` |

Đề xuất registry: `mike/kb/data_registry/macro/cctg_rate_vn.md.proposed`.
