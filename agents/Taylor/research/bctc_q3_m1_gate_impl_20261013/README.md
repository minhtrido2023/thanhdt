# BCTC Q3 — triển khai 4 việc user duyệt 2026-10-13 19:51 ICT (job Taylor_20261013_125149)

Nguồn: audit `bctc-q3-readiness-signal-20261013` (`../bctc_q3_readiness_20261013/`). Nhãn: **đã code + selfcheck thật,
CHƯA merge, CHƯA chạy trong chuỗi 19:00 thật**. Không đổi crontab, không đụng `trading_rules.json`, không đổi điều
kiện lọc/chặn lệnh nào.

| Nhánh `fix/bctc-q3-m1-gate-20261013` | Commit | Worktree |
|---|---|---|
| repo `mike` | `7c1c00579` | `mike/agents/Taylor/wt-bctcq3-1013` |
| repo ngoài (`/home/trido/thanhdt`) | `866d549a` | `WorkingClaude/wt-bctcq3-1013` |

**Hai nhánh phải merge CÙNG LÚC**: `bq_freshness_check.sh` (mike) gọi `refresh_earnings_surprise_pkl.py` (repo ngoài).

## Việc và bằng chứng

| # | Việc | File chính | Selfcheck (chạy thật, 3 TZ) | Mutation |
|---|---|---|---|---|
| 1 | M1(a) gate re-rate 8L: (tháng 1/4/7/10 ∧ ngày ≥10) ∨ (tháng 2/5/8/11 ∧ ngày ≤10) | `mike/bin/fa_ratings_earnings_window_daily.sh` | `fa_ratings_earnings_window_gate_selfcheck.sh` 142/142 | 18/18 |
| 2 | M1(b) cờ cảnh-báo `lag_rating_stale` | `lag_rating_filter.py`, `golive_recommend_v23.py`, `telegram_recommend.py` | `lag_rating_stale_selfcheck.py` 66 offline + 3 live | 47/47 |
| 3 | L2 watcher PNJ Q3 | `mike/bin/pnj_q3_review_watch.py` | `pnj_q3_review_watch_selfcheck.py` 49 offline + 3 live; e2e với `append_event.sh` THẬT trên bus tạm PASS | 30/30 |
| 4 | L1 làm mới pkl LAG 19:00 từ BQ sống | `refresh_earnings_surprise_pkl.py`, `[pipeline-1d]` trong `bq_freshness_check.sh` | `refresh_earnings_surprise_pkl_selfcheck.py` 45 offline + 6 live; `bctc_q3_chain_wiring_selfcheck.py` 16/16 | 26/26 + 19/19 |
| L4 | registry `fa_ratings_8l.md` (+ `fa_ratings.md` cùng lỗi) | `mike/kb/data_registry/rating-8l/` | — | — |

Tổng 140 mutant có artifact, 0 sống (vòng 1 từng sống 7: F12, F13, G11, R08, R16, R22, R25 — đã thêm test giết).

## Số đo thật
- Bước (4): **13,7 – 14,9 s/lượt** (4 lượt, BQ sống, 58.234 dòng), RSS ~316 MB. Watcher PNJ: ~2,2 s. ⇒ chuỗi 19:00 dài thêm ~17 s.
- Lượt đầu trên bản sao pkl: 58.233 → 58.234 dòng, đúng 1 dòng mới = KBC 2026Q3 (release 10-12); lượt sau `unchanged`,
  mtime giữ nguyên. pkl production không bị chạm (md5 `077c38bf…` trước = sau).
- Cờ chạy trên BQ thật 10-13: KBC rating 4 chấm 07-31 < BCTC 10-12 ⇒ có cờ (`RATING_FAIL`).
- Quyết định lọc không đổi: AST `lag_filter_low_rating` giống hệt `3dc35467`; khối LAG của golive bản gốc vs bản mới trên
  300 thế giới ngẫu nhiên (hơn 200 dòng order LAG, có lượt nguồn hỏng) cho cùng `lag_up/lag_recent/dropped/recs`.

## ĐÍNH CHÍNH cơ chế L1 của audit trước
Audit ghi "pkl làm mới 15:30, TRƯỚC ingest 16:36". Độ trễ 1 phiên đúng, cơ chế sai: `papertrade_daily.sh` source
`wc_env.sh` ⇒ `BQ_LOCAL_CACHE` bật ⇒ bước [3] đọc cache DuckDB sync 23:45 đêm trước (đo: pkl 15:30 = 58.233 dòng /
max 08-21 = y hệt `data/bq_cache/ticker_financial.parquet`). Dời giờ 15:30 ra sau 16:36 sẽ KHÔNG giúp gì; phải đọc BQ sống.

## Quét rộng §23 (golive / lag_rating_filter chạm đường tiền) — 34/34 PASS, nhánh = baseline
34 selfcheck phụ thuộc, chạy trong sandbox có git (clone --shared + sed đường dẫn), nhánh vs baseline `3dc35467`/`58d3370be`.
Lượt 1: 29 PASS + 5 FAIL giống hệt ở cả hai do sandbox thiếu đầu vào. **Lượt 2 (20:40 ICT)** dựng lại sandbox đủ đầu vào
(`build_sandbox_full.sh`: thêm `agents/{Winston,Spyros,Taylor}/*.py`, `data/_quarantine`, file `data/` < 3MB, `deploy…/out`)
⇒ cả 5 PASS ở CẢ nhánh lẫn baseline, số ca PASS trùng nhau: `money_path_freshness` 29, `freshness_ops` 46,
`dt5g_chain_freshness` 51, `freshness_warn` 47, `filter_lag_entry_window` 53. Log: `broad_scan_{branch,baseline}_full/`.

## Mutation gate + chain-wiring (chạy lại lượt 2 vì lượt 1 không lưu artifact)
`mutants_gate_chain.py` → `out_mutants_gate_chain.txt`: gate **18/18 KILLED**, chain-wiring **19/19 KILLED**, 0 sống, 0 not-applied.
(Commit message ghi 17/17 và 15/15 = bộ mutant lượt 1, không còn file; số có bằng chứng là 18 và 19.)
Tổng có artifact: 47 + 30 + 26 + 18 + 19 = **140 mutant, 0 sống**.

## Rủi ro còn lại (trọn bộ)
1. **Thứ tự cron chưa đổi: golive 19:00 chạy TRƯỚC re-rate 20:00.** L1 đưa BCTC ingest hôm nay tới golive ngay 19:00
   ⇒ ngày đầu của MỌI sự kiện mới, cổng 8L≤3 chấm bằng rating quý trước (trước L1, sự kiện tới trễ 1 phiên nên
   re-rate 20:00 đã kịp). Entry LAG = release+5 phiên và cổng chạy lại mỗi tối ⇒ plan của ngày entry thường đã có
   rating mới; ca còn hở = BCTC ingest muộn sát ngày entry, hoặc ngày nằm ngoài cửa sổ gate. Cờ M1(b) chính là thứ
   làm lộ ca này, và sẽ kêu ở ngày đầu của mỗi sự kiện mới (nhiễu có chủ đích, dòng cảnh báo nhắc kiểm lại sau 20:00).
2. **Cờ chỉ có nghĩa ở lượt LIVE** — replay lịch sử không tái hiện được (`fa_ratings_8l.time` = Release_Date dù ghi muộn).
   Chưa có số đo tỉ lệ cờ đúng/sai qua một mùa thật; đo trong mùa Q3 rồi mới bàn siết.
3. **Lễ biến động (Tết) chưa encode** trong `is_holiday` (có sẵn từ trước) — cửa sổ nới thêm tháng 2 ⇒ gate có thể RUN
   trong kỳ nghỉ Tết. Hệ quả: re-rate thừa, không sai số liệu.
4. **Chi phí nới gate**: ~32 ngày/quý chạy re-rate thay vì ~17 (cả năm 127 vs 67 lượt, đếm lịch, chưa trừ lễ). Chưa đo phí BQ mỗi lượt.
5. **Watcher PNJ chỉ canh 2026Q3** (hằng số) và bắn đúng 1 lần; mất state mà bus còn event ⇒ bus không lặp (e2e với
   `append_event.sh` thật); Discord ở ca mất state chưa đo riêng. Discord lỗi ⇒ thử lại Discord lượt sau, bus không lặp.
6. **pkl bị ghi 2 lần/ngày** (15:30 qua cache đêm trước, 19:00 qua BQ sống). Bản 15:30 hôm sau có thể ÍT dòng hơn bản
   19:00 hôm trước nếu sync 23:45 hỏng ⇒ pkl lùi tạm tới 19:00; probe lag-pkl hiện có vẫn canh đường 15:30.
7. **Hai nhánh phải merge cùng lúc.** Chỉ merge `mike` ⇒ `[pipeline-1d]` gọi file không tồn tại ⇒ WARN Discord mỗi tối
   (không chặn plan). Chỉ merge repo ngoài ⇒ không ai gọi script, cờ vẫn chạy.
8. **Chưa chạy trong chuỗi 19:00 thật**; `telegram_recommend` mới kiểm bằng selfcheck dựng message, chưa gửi thật.
9. **CHƯA có quant-skeptic / arch-review** — đổi này là vận hành + cảnh báo, không đổi số backtest; arch-review là của Mike.

## Cần Mike quyết
- **A.** Merge 2 nhánh cùng lúc (ngoài 18:30–19:10 và 21:00). Nhánh `mike` không trùng file nào với `58d3370be..master`;
  repo ngoài: master vẫn ở `3dc35467` ⇒ fast-forward.
- **B.** Có dời re-rate 20:00 lên TRƯỚC chuỗi 19:00 trong mùa BCTC không (đổi crontab ⇒ cần user)? Không dời thì
  chấp nhận cờ kêu ngày đầu mỗi sự kiện (rủi ro 1).
- **C.** Sau mùa Q3: đọc lại `lag_rating_stale` trong status để quyết siết thành fail-closed hay giữ cảnh báo (user).
- **D.** Khi PNJ Q3 về: question `pnj-bctc-q3-review-trigger` chỉ GỌI review, không tự khôi phục — Mike dispatch
  fundamental-skeptic.

## File trong thư mục này
`mutants_*.py` + `out_mutants_*.txt` · `out_selfcheck_3tz.txt` · `out_selfcheck_live.txt` ·
`out_pnj_e2e_real_append_event.txt` · `broad_scan.sh`, `build_sandbox.sh`, `broad_scan_{branch,baseline}{,_rerun}/` (lượt 1) · `build_sandbox_full.sh`,
`broad_scan_5.sh`, `broad_scan_{branch,baseline}_full/`, `mutants_gate_chain.py`, `out_mutants_gate_chain.txt` (lượt 2).
