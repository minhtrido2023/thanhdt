---
kind: research-report
job: Taylor_20261015_173117
date: 2026-10-16
status: DONE — GĐ0 đo lường, PAPER-ONLY, không wire gì. Label MEASURED.
approved_by: user 16/10 00:30 ICT (topic 1559544863479824557)
---

# GĐ0 — "Dấu vân tay" hành vi công bố & mẫu hình giao dịch riêng từng công ty vs 8L

## Kết luận 1 dòng
**Không đặc trưng HÀNH VI CÔNG BỐ nào thêm được thông tin có ý nghĩa so với 8L** (NO-GO/INCONCLUSIVE).
Thứ duy nhất qua ngưỡng prereg là **biến động riêng (idio-vol 60 phiên) / tần suất chạm biên độ** —
yếu tố biến động thấp chung, không phải dấu vân tay hành vi — và về lợi nhuận nó không vững khi
kiểm soát thêm momentum. Nó dự báo **rủi ro sụt giá** mạnh hơn rating 8L nhiều (AUC 0,70 so với 0,57).

## Phải nói trước: mẫu nhỏ
- N độc lập = **đợt công bố** (quý tài chính): ~48 đợt (IS 22 / OOS 26), KHÔNG phải 17.739 dòng sự kiện.
- Pre-flight `rnd_preflight_power.py` (per-event, 4 đợt/năm, 16 phép thử): **NO-GO** ở effect giả định
  50–100bps/đợt. DSR 0,95 chỉ đạt nếu Sharpe năm ≥ 1,0 (≈ t_đợt ≥ 3,5). User đã duyệt GĐ0 như ĐO
  LƯỜNG, nên ngưỡng GO được khai trước ngang mức đó (`prereg.md`, viết trước khi tính bất kỳ IC nào).
- 38 phép thử (19 đặc trưng × 2 horizon) ⇒ Harvey-Liu-Zhu t ≥ 3.

## Dữ liệu (vintage: cache sync 2026-10-15 23:45 ICT; insider BQ MAX(public_date)=2026-10-14)
Tra `mike/kb/data_registry/` trước khi chọn: `ticker` (cache, Close để tính return, Price×Volume cho
Amihud), `ticker_financial.Release_Date`, **`universe_pit`** (as-of t0−1, không dùng `ticker_prune`),
`fa_ratings_8l` (as-of t0+1 theo eff_date, có assert), `insider_transaction` (Done, DDIND+DDRP,
`public_date` = ngày báo cáo kết quả = an toàn; bỏ 407 cụm ESOP ≥5 người mua cùng ngày; tự áp dấu).
`profit_*` KHÔNG dùng; forward return tự tính chỉ để ĐO, bắt đầu từ close t0+1 (sau khi mọi đặc trưng đã biết).

Khoảng trống dữ liệu (khai trước trong prereg):
- **Release_Date NULL ở 6.536/56.895 dòng (11,5%)** ⇒ loại.
- **Không có Release_Date nào rơi T7/CN**: vendor dồn sang thứ Hai (5.777 sự kiện thứ Hai vs ~3.100 ngày
  khác) ⇒ "công bố cuối tuần" chỉ đo qua proxy `monday`.
- Không có nguồn PIT "loại cổ đông" (chỉ dict tay 13 mã SOE trong `soe_governance_screen.py`) ⇒ EB chỉ
  kéo về trung bình **ngành ICB cấp 1**.
- Beneish: thiếu khấu hao/SG&A/AR kỳ trước ⇒ chỉ có Sloan accrual quý. Trần biên độ: không có cột
  sàn ⇒ proxy |ret| ≥ 6,5%.
- Sanity căn ngày: |AR| ngày t0 cao hơn nền +17%, volume +10–15% ở t0..t+1 ⇒ Release_Date khớp ngày tin.

## Việc (1) — bảng đặc trưng `events_features.csv.gz`
48.522 sự kiện release ≥ 2014; **17.739 trong universe_pit, 752 mã, 53 đợt**. Cột: `lag_dev` (trễ so
với trung vị 8 quý trước của CHÍNH mã), `monday`, `late30`, `near_deadline`, `car_m1p1`, `car_m5m1`,
`leak_ratio` = CAR[−5,−1]/CAR[−5,+1] (chỉ khi |mẫu| ≥ 2%, kẹp [−2,3]), `vol_ratio`, `amihud_log`,
`idio_vol60`, `limit_freq60`, `ins_netbuy_adv` (mua ròng 90 ngày / ADV), `ins_breadth`, `accr_q`.
`events_features_fp.csv.gz` thêm 5 dấu vân tay EB `fp_*`.

## Việc (2) — giá trị tăng thêm so với 8L (`ic_results.csv`, `robustness_vol.csv`)
IC Spearman trong từng đợt, sau khi trực giao hoá rank đặc trưng với dummy rating 8L PIT; t trên chuỗi
IC theo đợt; LOYO; block-bootstrap theo ticker B=1000. EB: `fp = M_g + w(m_k − M_g)`, `w = τ²/(τ²+σ²/n_k)`,
m_k là trung bình các sự kiện TRƯỚC của mã, M_g/σ²/τ² từ ngành với dữ liệu trước 01/01 năm sự kiện.

| Đặc trưng | Horizon | IC trực giao | t_đợt | IS t | OOS t | Phán |
|---|---|---|---|---|---|---|
| idio_vol60 | 3M | −0,102 | −4,74 | −3,35 | −3,44 | **GO theo prereg ⇒ hạ xuống INCONCLUSIVE** (xem dưới) |
| limit_freq60 | 3M | −0,085 | −3,92 | −3,28 | −2,56 | **GO theo prereg ⇒ hạ xuống INCONCLUSIVE** (tương quan 0,84 với idio_vol) |
| car_m1p1 (PEAD) | 3M | +0,036 | 3,06 | 5,83 | 0,75 | INCONCLUSIVE — chỉ sống IS, OOS tắt |
| car_m5m1 | 3M | +0,040 | 3,05 | 4,90 | 0,35 | INCONCLUSIVE — chỉ IS |
| vol_ratio_log | 3M | +0,021 | 2,23 | 1,33 | 1,78 | INCONCLUSIVE |
| fp_lag_dev | 1M | +0,030 | 2,38 | 1,40 | 1,97 | INCONCLUSIVE |
| fp_car | 1M | −0,032 | −2,55 | −0,27 | −3,13 | INCONCLUSIVE — chỉ OOS |
| fp_volr | 1M | +0,032 | 2,41 | 1,09 | 2,22 | INCONCLUSIVE |
| lag_dev, monday, late30, near_deadline, leak_ratio, amihud, ins_netbuy_adv, ins_breadth, accr_q, fp_leak, fp_ins | 1M & 3M | |t| < 2 hoặc OOS ngược dấu IS | | | | **NO-GO** |

Vì sao hạ idio_vol/limit_freq từ GO xuống INCONCLUSIVE:
1. Không phải hành vi công bố: đo trên cửa sổ 60 phiên TRƯỚC sự kiện, ngày nào đo cũng ra gần như vậy.
2. Kiểm soát thêm ngành + Amihud ⇒ vẫn vững (t −4,0); thêm **momentum 60 phiên ⇒ OOS t −1,52** (idio)
   / −1,86 (limit) — trượt ngưỡng OOS.
3. Hình dạng "xổ số": lợi nhuận vượt trung bình Q1–Q4 gần như phẳng, chỉ Q5 kém (IS −2,7%, OOS −1,9%/3M);
   spread Q5−Q1 trung bình t ≈ −1,4. IC mạnh vì TRUNG VỊ, không phải vì trung bình.
Composite (chọn trên IS, chấm OOS 1 lần): 3M OOS IC 0,075, t 2,79 < 3, do IVOL dẫn dắt; 1M OOS đảo dấu.
Không có cấu hình nào được khuyến nghị wire ⇒ DSR/PBO không áp dụng (Step 13).

**Đối chiếu nghiên cứu trước** (để không ai thấy "mâu thuẫn"): accrual Sloan NO-GO về lợi nhuận ở đây
vẫn khớp Phase 0b 2026-09-06 (`ccs_phase0_earnings_quality/`) — accrual sống ở EARNINGS PERSISTENCE,
không ở forward return; insider NO-GO khớp `insider_cluster_buy_scoping_20260830.md`; PEAD tắt OOS là
lý do LAG dùng SUE, không dùng phản ứng giá.

## Việc (3) — hiệu chỉnh rating 1–5 (`rating_calibration.csv`, `rating_auc.csv`, `rating_brier.csv`, `rating_transition.csv`, `rating_outlook*.csv`)
crash = MDD 3 tháng < −20%. N = 16.947 sự kiện / 48 đợt. Tỷ lệ crash theo năm từ 20% đến 75% (2022) ⇒ crash
tụ theo các cú sập thị trường; CI bootstrap theo ĐỢT.

| Rating | Crash ALL | Crash IS | Crash OOS | fwdx 3M trung bình |
|---|---|---|---|---|
| 1 | 17,9% | 17,9% | 17,9% | +0,8% |
| 2 | 30,4% | 23,2% | 33,6% | +1,0% |
| 3 | 36,0% | 26,5% | 41,8% | +0,9% |
| 4 | 42,0% | 33,4% | 47,3% | −0,9% |
| 5 | 42,1% | 31,0% | 48,2% | −0,9% |

- Đơn điệu 1→4; **4 và 5 KHÔNG tách** (IS 5 còn thấp hơn 4). Cổng ≤3 đúng hướng: rating 4–5 kém ~1,8pp/3M.
- Phân biệt crash: **AUC rating 0,573** (Gini 0,15, CI 0,557–0,591) vs **idio_vol rank 0,698** (Gini 0,40).
  Logit rating + IVOL (fit IS) ⇒ OOS AUC 0,694 ≈ IVOL một mình. 8L không phải bộ dự báo sụt (nó là cổng chất lượng).
- Brier: bảng IS theo rating áp OOS ⇒ BSS +1,7% so climatology IS, −4,6% so base-rate OOS (base-rate thị trường át hết).
- Chuyển hạng quý-qua-quý: đường chéo 69–86%; 3→4 21%, 2→3 20%; trôi xuống bất đối xứng; 25% sự kiện đổi rating.
- **Outlook theo động lực rating: KHÔNG ủng hộ.** Trong cùng mức rating, mã "xấu đi" thường crash THẤP hơn
  mã "ổn định" (rating 2–3, cả IS lẫn OOS). Thứ nhất quán duy nhất: tercile IVOL tăng so với sự kiện trước
  ⇒ +4..6pp crash (demean theo đợt) ở mọi nhóm, IS và OOS. Lưu ý: IVOL dự báo ĐỘ LỚN drawdown một phần
  vì cơ học (vol cao ⇒ MDD sâu) — đây là rủi ro, không phải kỳ vọng lỗ.

## Chẩn đoán phụ — 6 mã Release_Date NULL / eff_date tương lai (CHỈ chẩn đoán, KHÔNG sửa)
- Cơ chế: `rating_8l_history.py:597-600` — `eff_date = Release_Date`, thiếu thì **`q_time + 45 ngày`**, mà
  `q_time` = `ticker_financial.time` (SQL `HIST_SQL` dòng 113), **KHÔNG phải cuối quý** như comment nói.
  Với dòng NULL, `time` ≈ cuối quý + 32 ngày (trung vị), nhưng PMT 2026Q2 có `time` = 2026-09-03 ⇒ eff
  **2026-10-18 (tương lai)**. Cả 6 mã NULL cả 2026Q1 lẫn Q2; Q1 rơi vào 06-18 (05-04 + 45).
- Có look-ahead trong backtest không: **Không.** Trên 47.930 dòng có Release_Date, 0% có release thật
  muộn hơn `time + 45` ⇒ fallback luôn MUỘN hơn thực tế (rating cũ ~45 ngày), không bao giờ sớm.
- Có lọt vào cổng live không (subagent rà code, tôi verify lại dòng 740):
  - Cổng 8L của LAG (`lag_rating_filter.py:62-64`, `trading_bot/plan.py:796`), custom30/30V `rating_asof`
    (`custom_basket.py:729-743`), `regime_size_overlay.py`, `build_universe_pit_quality.py`: đều lọc
    `time <= as_of` ⇒ **KHÔNG đọc sớm**.
  - **`deploy_golive_dt5g_v4/golive_recommend_v23.py:740-742`** (cờ weak BAL, nửa size trong BEAR/CRISIS) và
    `hit_details.py:62-66` (chỉ hiển thị): lấy dòng mới nhất mỗi mã, **KHÔNG lọc ngày** ⇒ đọc sớm dòng tương lai.
    PMT hôm nay: 06-18 và 10-18 đều rating 4 ⇒ **tác động 0**. Chỉ `rating` được dùng, không ai đọc `tier`.
- Đề xuất (KHÔNG làm, cần owner + duyệt): (a) thêm `WHERE f.time <= DATE '{LATEST}'` vào 2 query trên;
  (b) fallback dùng `MIN(q_time + 45, cuối quý + 90)` hoặc ngày ingest thật thay cho `q_time + 45` để rating
  bớt cũ; (c) cảnh báo khi `fa_ratings_8l` có `MAX(time) > hôm nay` trong `refresh_fa_ratings_8l.sh`.

## Tái lập (threads=1, `$DNA_PYEXE`)
```bash
cd mike/agents/Taylor/research/firm_behavior_fingerprint_20261016
# insider_raw.csv: bq query --format=csv --max_rows=1000000 < insider_extract.sql > insider_raw.csv
$DNA_PYEXE build_events.py && $DNA_PYEXE sanity_event_profile.py && $DNA_PYEXE analyze_ic.py \
  && $DNA_PYEXE robustness_vol.py && $DNA_PYEXE calibrate_rating.py && $DNA_PYEXE selfcheck_spot.py
```
Self-check: `selfcheck_spot.py` tính lại CAR[−1,+1], fwdx_3m, MDD3M và rating as-of cho 5 sự kiện ngẫu nhiên
bằng một đường code khác ⇒ **5/5 PASS**. Không có backtest NAV ⇒ self-check 0 VND không áp dụng.
Production không bị đụng: chỉ thêm file trong thư mục này.

## Nếu đi tiếp (đề xuất, chưa làm)
Nếu muốn đi tiếp: dùng IVOL/limit-freq như **chỉ báo RỦI RO** (sizing/cảnh báo) chứ không như alpha. Nó
cần một vòng riêng: kiểm soát beta/size đầy đủ, chạy full-engine NAV có self-check 0 VND, quant-skeptic.
Hiện **chưa có gì để wire**.
