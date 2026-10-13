# CCTG tier2 — vòng 2 (job Taylor_20261013_090057)
Nhánh feat/cctg-tier2-banks-series-20261013 (wt-cctgt2-1013), commit r2 trên 7ec10026. KHÔNG merge/push.
- mutants_r2.py / mutants_r2_out_run1.txt (45/47 lần 1) / mutants_r2_out_rerun.txt + mutants_r2_out_M05.txt (các mutant sống đã vá test → bị bắt); `--old-control` chứng minh MC' SỐNG trên selfcheck HEAD(vòng 1).
- diff_writer.py / diff_writer_out.txt: vi sai writer main vs nhánh (12m/6m): 17/19 lệnh giống hệt, md5 data/ giống hệt; 2 khác là chủ ý (--bank trên 12m; câu "cctg_events_df()" ở 6m 'không mới hơn').
- selfcheck_r2_*.txt, regress_r2_*.txt: selfcheck mới 85/85 + 5 hồi quy dưới env -u TZ / GMT+12 / OVERLAY=0 / JOB_ID đặt sẵn.
