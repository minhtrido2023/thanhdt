# Brief A5 — job `Taylor_20261113_071030` (Mike dispatch, user chỉ đạo 13/11 14:09 ICT)

⚠️ PAPER. KHÔNG đổi production / `trading_rules.json` / neo sizing. KHÔNG merge.

- Việc 1: chạy lại pin1M (IDLE_CARRY_TIER=dep1m) + pin0% trên mã ĐÃ COMMIT, worktree sạch, ghi provenance (hash code, md5 ledger, md5 data);
  đối chiếu `e2de0ac4` / `80f509ec`.
- Việc 2: bằng chứng cho neo sizing −25,2% vs DD5 sàn mới −27,89%:
  (a) cấu hình chính xác của neo (fill ảo?), bảng DD5 2 chữ số neo cũ vs mới, mỗi bước 1 trục;
  (b) ADV live lúc đặt lệnh LAG vs ADV pit cùng (mã, ngày), N, lệnh bị cap;
  (c) DD thực tế BAL+LAG live vs phân phối (N=1 cửa sổ ~4 tháng);
  (d) kết luận: engine nào trung thực hơn với live ⇒ neo nào đúng.

Kế hoạch chạy (8 chân, `batch.txt`, 4 song song, threads=1, `$DNA_PYEXE`):
- V1_pin0 (main 7f25febc1 sạch, adj v2) · V1_pin1M (e9a9aed1a = 770393ce2 + 1 dòng A4 đã commit, adj v2)
- C30_off_q: tái lập neo 4707bcbe (worktree quicksort Luồng A dbfd9a4af, LIQ off, vint 10-29, park 0,3)
- Thang park 0,3 trên main: P3_L1 (off,bq,vint) → P3_L2 (lag,bq,vint) → P3_L3 (lag,bq,adj) → P3_L3P (lag,pit,adj) + P3_L3P_1m
