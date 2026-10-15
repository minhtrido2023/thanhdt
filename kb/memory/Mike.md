# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Cuối ngày 15/10 (dọn 00:40 ICT 16/10)
## Việc ngày 16/10
- 08:00 kiểm bản tin dashboard E–I (topic daily_decision) đủ, không khối ⚠️. 08:45 preflight; plan 16/10 (7 SELL mỗi acct) ĐÃ user duyệt, bot 09:05 → theo dõi fill, đối soát §27.
- 09:00–18:30: chốt sổ `nav_unit_ledger --seal --real-data --accept-preclose 2026-08-24=<lý do ở C_seal/log.txt>` SpaceX rồi ZaloPay; post SEAL_MD5 lên bus, --verify-anchor, cron verify-anchor (cron_registry), áp 4 .proposed registry bước 3. Tránh 19:05-19:15, 20:15, 23:30.
- 19:00 xem bước 1a universe_gap_fill lần đầu thật (logs/bq_freshness.log); morning-mode (MIKE_MORNING_RUN=1) review lần dùng thật đầu.
- Taylor đang chạy nghiên cứu 'dấu vân tay hành vi công bố' GĐ0 (paper-only, thread 1559544863479824557, out agents/Taylor/research/firm_behavior_fingerprint_20261016/) → xong thì quant-skeptic verify.
- Weekly T7 17/10: kiểm khối đính chính CORR_STEP + bảng 3.2 mới (mốc CORR_STEP 23/10).
## Chờ user quyết
- Escalation retro-pattern-recurring-done-on-branch-not-merged-backlog (A merge ngoài giờ / B mốc cứng+cron / C bỏ nhánh).
- Đính chính số đã công bố (Taylor): benchmark ZaloPay neo 03/07 vs 06/07; vol tháng 8 ZaloPay; EOD SpaceX 08-07 % ngày.
## Nhánh chưa merge
- feat/finding-measured-by-20261013 (3 retro liên tiếp), gate-source-check-publish, dcf-rf-slow, cctg-tier2, fund-cashflow-detect-20261012 (chép 2 xác nhận user 07-03, 08-28 vào data/cash_identity_acks.json), nav-loss-brake-monitor (mốc 2026-11-09).
## Chưa điều tra
- ZaloPay DNSE 401 lúc 14:00Z (4 lần: 10-07,09,12,15) — đề xuất giao Winston: vòng đời token + refresh/retry trước CANNOT_CHECK; adjfactor-drift-scan drift=4; gap N2 (stub-only không WARN), N4 (quality gap) của universe_gap_fill; dashboard: VN-Index cổ tức n/a, ZaloPay thiếu nav_sleeve 15/10.
## Quyết định hiệu lực
- CAPIT margin lever TẮT; park NEUTRAL 0%; PNJ EXCLUDED (review khi BCTC Q3/2026). CronCreate trong phiên mất khi restart.

- [2026-10-15T17:49:27Z] 16/10 00:55: Taylor xong GĐ0 dấu vân tay hành vi công bố: NO-GO/INCONCLUSIVE (không đặc trưng nào thêm thông tin vững so với 8L; idio-vol là chỉ báo RỦI RO AUC 0,70 vs rating 0,57, không phải alpha). Không có gì wire ⇒ không cần quant-skeptic. CHỜ user: (a) vá golive_recommend_v23.py:740 + hit_details.py:62 đọc dòng fa_ratings_8l mới nhất không lọc ngày (tác động hôm nay 0); (b) fallback eff_date q_time+45; (c) cảnh báo MAX(time)>hôm nay; (d) có đi vòng riêng idio-vol làm chỉ báo rủi ro không. Report: agents/Taylor/research/firm_behavior_fingerprint_20261016/README.md
- [2026-10-15T18:19:14Z] 16/10 01:25: MERGED việc 1 (user duyệt): golive_recommend_v23.py:~742 + hit_details.py:64 lọc fa_ratings_8l f.time<=as-of (outer 15836bc9), cảnh báo dòng eff_date tương lai trong refresh_fa_ratings_8l.sh (mike 21ed48298, dedupe state, báo Trading Daily khi tập đổi; PMT@2026-10-18 sẽ báo 1 lần lúc re-rate 17:30). arch-review NEEDS_CHANGES→đã vá hết. Còn mở: (b) fallback eff_date q_time+45 (rating_8l_history.py:597), anomaly_scan.py:154 đọc dòng mới nhất không lọc ngày (paper), (d) idio-vol chỉ báo rủi ro.
