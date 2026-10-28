# vnindex_tr vòng 2 — đính chính dòng sealed 12-13/10 (job Taylor_20261021_052419, 21/10/2026)
- Code: nhánh `fix/vnindex-tr-restate-sealed-20261021` @73c9e7746 (worktree /home/trido/thanhdt/wt_vnindex_tr_restate_20261021).
  A `--restate-sealed` + sổ `data/benchmark/vnindex_tr_restatements.jsonl`; C seal-guard G1/G4 trong `--update`.
- `mutants.py <worktree>`: 11 mutant (A1-A5, A7, A8, C1-C4), cả 11 chết.
- `dry1.json`: dry-run đính chính trên bản sao (md5 6c716f6f… → 329d76ce…). `copy_apply.json`: áp trên bản sao.
- `real_apply.json`: áp lên chuỗi thật 12:34 ICT. md5 6c716f6f21091503f2c838306e14eddf → 51cd88f43cfbd9ec951873b573a54d92;
  sao lưu `data/benchmark/vnindex_tr_daily.csv.bak_pre_restate_20261021` (md5 6c716f6f…).
Kết luận + số: event bus trace Taylor_20261021_052419.
