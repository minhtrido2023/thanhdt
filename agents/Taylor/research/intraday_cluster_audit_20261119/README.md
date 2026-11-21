# Kiểm toán edge intraday HOSE theo cụm — #1, #4, #2 (khả thi) — 2026-11-19
Job Taylor_20261119_044412 · CHỈ ĐỌC (không đụng live/production/chuỗi sealed). PREREG: `PREREG.md` (md5 3a4a6f92e307c5a2833835f0483df33a, viết trước khi tính). Dữ liệu: `data/` (md5 trong `data_md5.txt`). Chạy lại: `$DNA_PYEXE audit_clusters.py` và `$DNA_PYEXE daily_vs_intraday.py` (log: `out/*.txt`, bảng: `out/*.csv`).

## Kết luận (trước)
- **#1 = NO-GO.** 0/5 setup PASS. Số cụm độc lập thật (gap ≤5 phiên) in-sample: FZ-001 **17**, FZ-002 **15**, C-CEIL 26, C-NFLOOR 19, C-NFLOOR3 23 — chỉ C-CEIL và C-NFLOOR3 ≥20. **Không setup nào có CI90 loại 0** và **không setup nào có DSR ≥0,95** (DSR(N=1000) tối đa 0,073 ở FZ-001; cả khi N=65 tối đa 0,22; xác suất PSR "Sharpe>0" chưa phạt trial chỉ 0,82–0,92, tức đã <0,95 trước khi phạt đa trial). Placebo khối tháng p<0,05 chỉ ở FZ-001 (0,041). Excess cấp cụm sau phí thật dương nhỏ (+0,59…+2,1%) nhưng biến mất khi bỏ 5 cụm tốt nhất (mean cụm còn lại âm ở cả 5 setup: −0,02% FZ-001, −0,53%, −0,24%, −0,74%, −1,05%).
- **Holdout: không đủ N** (2–4 cụm mỗi setup) — chỉ mô tả; không dùng làm xác nhận.
- **#4 = NO-GO (không có giá trị thêm của điều kiện intraday).** Bản daily proxy dựng công bằng (tái lập 99,4% deal, corr lợi suất 0,93). Chênh excess cấp cụm (intraday − daily-only) = +0,31pp, **CI90 [−0,52; +1,09]pp** ⇒ không loại 0 (13 cụm ghép). Trùng ngày CAPIT: **26–30% cụm/19–22% ngày signal** (<50% ⇒ PASS tiêu chí kế hoạch) — nhưng nền CAPIT chỉ fire 2,3% phiên, và 12/18 ngày CAPIT fire (2023-09→2026-11) có tín hiệu FZ-001 ⇒ phần lớn *lúc CAPIT fire thì FZ-001 cũng fire*; "mới" ở đây chỉ là các đợt bán tháo nhỏ hơn CAPIT.
- **#2 (từ deal-list) = lẫn lộn:** phí 0,097% và bỏ ex-date đều qua PASS cho FZ-001/C-NFLOOR*/C-CEIL in-sample; **FAIL ở holdout C-CEIL và FZ-002** (mean đã ~0, nên đổi >25%/đổi dấu là tất yếu). Phần cần engine nhóm kia: CHƯA làm (liệt kê cuối).
- **Verdict: NO-GO theo tiêu chí kế hoạch; KHÔNG khuyến nghị wire.** Không có gì ở đây thay đổi khuyến nghị "giữ paper, sổ cấp tín hiệu" (kế hoạch E).

## 1. Self-check (control tái lập summary.csv)
`out/audit_log.txt`: 14/14 (setup×giai đoạn) khớp `summary.csv` về n, mean net_ret_total, win rate, mean excess → `SELFCHECK_ALL PASS`. Daily proxy #4: coverage 175/176 deal in_stats nằm trong daily-set; D_RSI BQ khớp D_RSI deal đến 5e-7; giá raw close_raw_D khớp BQ `Price` (sai lệch ≤7e-12).

## 2. #1 — bảng chính (in-sample, `out/cluster_audit.csv`)
Đơn vị = cụm E5 (signal_day cách nhau ≤5 phiên nối chuỗi); excess_adj = excess_ret − 0,134% (phí thật 0,097%/chiều + thuế 0,1% thay cho 0,03%/chiều).

| | FZ-001 | FZ-002 | C-CEIL | C-NFLOOR | C-NFLOOR3 |
|---|---|---|---|---|---|
| deal in_stats / ngày signal / tuần ISO | 176 / 39 / 27 | 174 / 37 / 26 | 304 / 174 / 95 | 48 / 30 / 27 | 69 / 39 / 32 |
| **cụm E5** | **17** | **15** | 26 | 19 | 23 |
| excess cụm, thô | +0,88% | +0,77% | +0,73% | +1,08% | +2,28% |
| excess cụm, sau phí thật | +0,75% | +0,64% | +0,59% | +0,95% | +2,14% |
| CI90 bootstrap theo cụm | [−0,15; +1,52]% | [−0,17; +1,53]% | [−0,37; +1,47]% | [−0,39; +2,30]% | [−0,76; +6,39]% |
| abs sau phí & hurdle tiền gửi 1M | +1,84% | +2,49% | +0,15% | +1,52% | +3,22% |
| Sharpe cấp cụm | 0,35 | 0,31 | 0,20 | 0,26 | 0,20 |
| DSR T=cụm, N=1000 (chính) | 0,073 | 0,007 | 0,023 | 0,014 | 0,0001 |
| DSR N=250 / 65 / 30000 | 0,13/0,22/0,016 | 0,024/0,076/0,0003 | 0,051/0,11/0,003 | 0,039/0,097/0,001 | 0,001/0,011/0 |
| placebo khối tháng p (số khối tháng) | **0,041** (13) | 0,132 (15) | 0,138 (19) | 0,183 (15) | 0,254 (18) |
| LOCO mean thấp nhất / cao nhất | +0,58 / +1,10% | +0,27 / +0,81% | +0,37 / +0,98% | +0,55 / +1,27% | **−0,02** / +2,47% |
| top-5 cụm / tổng cụm dương | 62% | 95% | 56% | 75% | 85% |
| mean cụm khi bỏ top-5 | −0,02% | −0,53% | −0,24% | −0,74% | −1,05% |
| PASS a (≥20 cụm) / b (>0) / c (CI90) / d (DSR) / e (placebo) | F/T/F/F/T | F/T/F/F/F | T/T/F/F/F | F/T/F/F/F | T/T/F/F/F |
| **Verdict** | FAIL | FAIL | FAIL | FAIL | FAIL |

Ghi chú: (i) hurdle tiền gửi 1M pro-rata chỉ ~0,04–0,07%/deal (giữ ~7 phiên, lãi 2–3%/năm) — nhỏ; cột `abs` dương vì mở thị trường 2023–26 tăng (market drift), đó là beta chứ không phải edge — không dùng làm PASS. (ii) `idle_rate_proxy.r_idle(d,'dep1m')` chạy được (dữ liệu thật ≥2019-02, nhóm này nằm hoàn toàn trong đoạn thật). (iii) Số trial N: 65 là tối thiểu liệt kê được từ kế hoạch A(iii)/BC (7 setup + 42 + 5 + 2 + 9) — **ước lượng từ báo cáo nhóm kia, không đo**; 1.000 là nền dự án. Kết luận không phụ thuộc N (fail ở mọi N). (iv) Placebo = lật dấu theo khối tháng (xem PREREG §3 T7), kiểm H0 đối xứng; FZ-001 p=0,041 là kết quả duy nhất <0,05 trong 5 và không sống sót hiệu chỉnh 5 setup (Bonferroni 0,05/5=0,01). (v) Cụm phụ (signal_day, tuần) có trong CSV; kết luận không đổi: số cụm theo ngày chỉ lớn hơn ở C-CEIL (174 ngày) nhưng đó là cụm trong cùng đợt, không độc lập.
**Holdout (`out/cluster_audit.csv`, period=holdout):** cụm E5 FZ-001 2, FZ-002 2, C-CEIL 4, C-NFLOOR 2, C-NFLOOR3 2 ⇒ "KHÔNG ĐỦ N (<15 cụm)" ở cả 5; chỉ ghi mean cụm sau phí: +1,50%, +1,20%, −0,13%, +4,5%, +2,6% (mô tả, không suy luận).

## 3. #4 — FZ-001 intraday vs daily (`out/daily_vs_intraday.csv`, `out/capit_overlap.csv`)
Universe xấp xỉ = 55 mã xuất hiện trong các deals_*.csv (danh sách top-50 mcap PIT thật không có trong export). Daily = D_RSI<0,32 ∧ ≥3 mã universe cùng điều kiện; engine proxy: vào Open D+1, TP +6%, SL 2×ATR14%, sellable T+2, thoát time đóng cửa phiên thứ 10 (đúng luật deal). Proxy vs engine (175 deal khớp): mean 2,65% vs 2,55%, corr 0,93, đồng ý loại thoát 94%.

| | deal | ngày signal | mean excess (proxy) |
|---|---|---|---|
| daily-all | 425 | 123 | +0,74% |
| tập intraday (FZ-001 ⊂ daily) | 187 | 39 | +1,26% |
| daily-only (phần bù) | 377 | 122 | +0,55% |

Chênh cấp cụm E5 (13 cụm ghép): intraday − daily-only = **+0,31pp, CI90 [−0,52; +1,09]** (FAIL); intraday − daily-all = +0,07pp [−0,65; +0,73]; engine-thật vs daily-only = −0,05pp [−1,15; +0,98]. Hạn chế: universe xấp xỉ; TP/SL kiểm daily (không biết thứ tự trong bar; SL ưu tiên); mẫu 13 cụm rất nhỏ nên **không đủ lực để nói "intraday không thêm gì"** — chỉ "không chứng minh được có thêm".
CAPIT (breadth top-250 universe_pit_q, D_RSI<0,3 ≥0,31; truy vấn `data/bq/capit_breadth.sql`): FZ-001 tất cả candidate: 12/54 ngày signal trùng ngày CAPIT fire (22%), 6/20 cụm (30%); in_stats: 10/52 ngày (19%), 5/19 cụm (26%); cửa sổ 5 phiên trước: 24%/30%. **PASS tiêu chí <50%.** Ngữ cảnh: CAPIT fire 18/788 phiên (2,3%); 12/18 ngày fire có FZ-001 cùng ngày.

## 4. #2 — độ nhạy lạc quan từ deal-list (`out/sensitivity.csv`, mean net_ret_total, in_stats)
Quy tắc PASS: |Δmean|/|mean|<25% và không đổi dấu.

| Giai đoạn / setup | mean gốc | bỏ entry sát trần | bỏ gap≥5% | bỏ ex-date | net_ret_cash | phí 0,097% | gộp S1b+S2+S3 |
|---|---|---|---|---|---|---|---|
| IS FZ-001 | 2,57% | = | = | = | = | 2,44% (−5%) | 2,44% (−5%) PASS |
| IS FZ-002 | 3,66% | = | 3,70% | = | = | 3,53% (−4%) | 3,57% (−3%) PASS |
| IS C-CEIL | 1,47% | 1,38% (−6%) PASS | 1,52% (+4%) | 1,38% (−6%) | 1,25% (−15%) | 1,34% (−9%) | 1,28% (−13%) PASS |
| IS C-NFLOOR | 2,43% | = | 2,08% (−15%) | 2,76% (+13%) | 2,15% (−11%) | 2,30% (−6%) | 2,27% (−7%) PASS |
| IS C-NFLOOR3 | 2,38% | = | 2,14% (−10%) | 2,61% (+9%) | 2,19% (−8%) | 2,25% (−6%) | 2,23% (−6%) PASS |
| HO FZ-001 | 1,19% | = | = | 1,10% (−8%) | 1,16% | 1,05% (−11%) | 0,96% (−19%) PASS |
| HO FZ-002 | 0,24% | = | = | 0,05% (−80%) FAIL | 0,13% (−43%) | 0,10% (−57%) FAIL | −0,09% (−136%, đổi dấu) FAIL |
| HO C-CEIL | −0,30% | +0,02% (đổi dấu) FAIL | +0,02% FAIL | = | = | −0,43% (+45%) FAIL | −0,11% FAIL |
| HO C-NFLOOR / NFLOOR3 | +6,8% / +5,8% | = | = | = | = | PASS | PASS (n=3/5) |

Số deal bị loại: C-CEIL entry sát trần 13 (IS)/4 (HO); gap≥5% 36 (IS, 12%)/4; deal cắt ex-date 4 (IS). Tác động của "sát trần" lên mean IS chỉ −6% vì xấp xỉ **chỉ thấy entry đã ở trần** (deal ATO khớp đủ), không thấy phần ATO-trần-vỡ-bị-không-khớp hay lạc quan của khớp tại open khi low<trần — đây là xấp xỉ **thấp** của lạc quan thật (kế hoạch ước tính C-CEIL 75% NO-GO). Hạn chế FAIL ở holdout: mean đã ~0 nên PASS tương đối vô nghĩa — đọc là "không có edge để mất". `net_ret_cash` vs `total`: C-TAMIX/C-ONID mất 41–43% nhưng không thuộc 5 setup này.

**Lý do skipped book3 (`out/skipped_reasons.csv`; holdout, câu B5):** FZ-001: slots_full 29, symbol_held 29, no_cash 12 (70 candidate bị bỏ, 9 vị thế được lấy). FZ-002: slots_full 39, symbol_held 24, no_cash 20 (83 bỏ, 14 lấy). C-CEIL: symbol_held 13, slots_full 2, no_cash 1, reentry_same_session 1. C-NFLOOR: no_cash 2, symbol_held 1. Khớp README export; không có `not_filled` ở holdout (in-sample có 19–27 ở FZ). Đọc: ở holdout phần lớn tín hiệu FZ bị loại vì **book đầy/đang giữ chính mã đó** (cụm bán tháo ⇒ nhiều mã cùng ngày tranh 10 slot) chứ không vì thanh khoản 5% — tức "95→9" chủ yếu là cạnh tranh slot + lệnh chọn ngẫu nhiên (seed 7), không phải bằng chứng riêng về edge. Muốn tách edge vs thiết kế cần chạy lại engine (chưa làm).

## 5. CHƯA làm (cần engine nhóm kia)
Fill ATO thực tế khi trần/ATO-trần-vỡ (chọn lọc ngược); rescale TP/SL ngày GDKHQ & hành vi lệnh điều kiện DNSE; cổ phiếu thưởng bán ngay; đuôi khoá sàn nhiều phiên; PBO cấp book; nhạy cảm slot/seed; danh sách top-50 mcap PIT thật cho #4; alpha đã trừ beta cấp book.

## 6. Caveat
Phân tích cấp cụm trên 5 setup × 10 phép thử, N trial lấy từ báo cáo nhóm kia (ước lượng). Cụm E5 là lựa chọn khai trước; ngưỡng gap=5 phiên không tune. Cả 3 phần dùng cùng dữ liệu in-sample mà nhóm kia đã tìm setup trên đó (hai nửa không độc lập) — kết quả dương ở đây là cận trên. Holdout chỉ mô tả. Nguồn số: `out/cluster_audit.csv`, `out/sensitivity.csv`, `out/skipped_reasons.csv`, `out/daily_vs_intraday.csv`, `out/capit_overlap.csv`, logs trong `out/`.
