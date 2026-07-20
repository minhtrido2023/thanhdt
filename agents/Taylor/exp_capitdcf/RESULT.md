# CAPIT × DCF filter/tiebreaker — NO-GO (job Taylor_20260720_153114)

**Câu hỏi (user 2026-07-20):** dùng DCF làm bộ lọc/tiebreaker PHỤ cho CAPIT basket selection
(bổ sung pb_z, không thay), để tránh case SAB (rẻ vs lịch sử bản thân nhưng đắt vs giá trị nội tại).

**N_trials pre-registered = 3**: (a) HARD filter loại DCF-RICH · (b) SOFT tiebreaker xếp RICH cuối ·
(c) BASELINE pb_z-only. N/A (FCFE âm) = PASS-THROUGH ở cả (a) và (b), theo chỉ đạo.

## Ràng buộc quyết định: mẫu quá mỏng
- Toàn bộ lịch sử 2014-2026 chỉ có **14 washout-fire episodes** (IS ≤2019: 5, OOS 2020+: 9).
- Bộ lọc **chỉ đổi rổ ở 4/14 event**. Mọi khác biệt CAGR/Sharpe đo được đều nằm trên n=4.
- → portfolio-level backtest KHÔNG đủ power. Vì vậy chạy **mechanism test name-level trước**
  (N=141 holdings / 66 pool-name-events) rồi mới tới pool-level.

## Stage 1 — mechanism (N=141 holdings thật, within-event demeaned rank IC)
| axis | IC | t | n_ev |
|---|---|---|---|
| DCF MoS | **+0.187** | 1.40 | 13 |
| pb_z (đảo dấu) | +0.069 | 0.51 | 13 |

Realized return theo bucket (demeaned): CHEAP +0.93pp (n=82) · **N/A +0.96pp (n=25)** · RICH −2.95pp (n=34).
Event-bootstrap gap RICH vs phần còn lại: −2.95pp, **CI95 [−10.6pp, +1.2pp], P(gap<0)=0.75** → đúng dấu, KHÔNG significant.

➡️ **Xác nhận thực nghiệm chỉ đạo về N/A**: nhóm N/A (FCFE âm — KCN/logistics capex nặng, 25/141 =
18% holdings) có return demeaned **ngang hệt nhóm CHEAP**. Treat N/A = reject sẽ loại nhầm nhóm
không hề kém. Pass-through là đúng, không chỉ là giả định an toàn.

## Stage 2 — pool-level, K=5, equal-weight (delta = variant − baseline)
| horizon | hard−base | soft−base | ghi chú |
|---|---|---|---|
| 60 phiên | **−0.73pp** (t=−1.61, CI95 [−1.74,−0.06]) | +0.24pp (ns) | CI loại trừ 0 nhưng ở phía **XẤU** |
| 120 phiên | +0.23pp (t=+0.45, ns) | +0.27pp (ns) | |
| 250 phiên | +3.01pp (t=+1.04, ns) | +2.76pp (ns) | |

**Dấu đảo theo horizon** (xấu ở 60d, tốt ở 250d) = đặc trưng nhiễu, không phải signal.

## Leave-one-out — toàn bộ edge 250d nằm ở 1 event
Bỏ **2020-03-12**: delta h250 sụp **+3.01pp → +0.15pp** (13/14 event còn lại đóng góp ~0).
Đúng 1 lệnh swap: `−SAB +CVT` tại đáy COVID, +40.2pp cho riêng event đó.
3/4 event bị đổi rổ mang delta **âm** ở h60. K-sensitivity (K=3..8): +4.8pp/+1.6pp/+3.0pp/+1.1pp/+1.2pp — nhảy loạn, không có plateau.

**Chi phí ẩn chưa mô hình hoá**: 2/4 event bộ lọc HARD làm rổ **co lại không có mã thay thế**
(2016-01-18 −LIX,VNM → còn 3 mã; 2026-03-09 −CTR,VGC) → tăng rủi ro tập trung.

## DSR
**Không báo DSR** — cố ý. DSR trên chuỗi mà edge nằm trọn ở 1 quan sát (n_ev hiệu dụng = 4, LOO
collapse về ~0) là con số trang trí, không phải bằng chứng. Báo DSR ở đây sẽ gây hiểu nhầm là đã
qua chuẩn multiple-testing. Điều kiện tiên quyết (edge sống sót LOO) đã trượt trước cả bước DSR.

## KẾT LUẬN: **NO-GO cả (a) và (b)** — không wire, không paper-first
- (a) HARD: NO-GO. Horizon ngắn CI loại trừ 0 ở phía xấu; edge dài hạn = 1 event; co rổ.
- (b) SOFT: NO-GO. Delta +0.2..+2.8pp mọi CI đều cắt 0, cùng nguồn 1-event.
- (c) BASELINE giữ nguyên.
- **KHÔNG đề xuất paper-first**: paper-trading không cứu được vấn đề này. CAPIT fire ~1,2 lần/năm →
  paper 6-12 tháng tích được 0-1 event. Không có độ dài paper nào tạo ra mẫu để kết luận.

## Điều đáng nói với user (case SAB có thật)
Trực giác SAB **không sai** — SAB bị loại đúng 2 lần (2020-03-12, 2022-09-29), và lần 2020 là
+40pp. Nhưng đó CHÍNH LÀ toàn bộ edge đo được: 1 giai thoại mạnh, không phải pattern lặp lại.
Wire 1 luật production dựa trên 1 event là đúng mẫu reshuffle-luck mà chuẩn 2026-07-05 (bài học
Wave1/H8a) yêu cầu bác.

## Hướng đáng theo tiếp (KHÔNG tự làm — cần user quyết)
Phát hiện phụ có giá trị hơn câu hỏi gốc: **DCF MoS rank tốt hơn pb_z** trong pool (IC +0.187 vs
+0.069). Đó là gợi ý đổi **rank chính**, không phải thêm lớp lọc phụ — thay đổi lớn hơn nhiều so
với đề bài, và vẫn chỉ t=1.40. Nếu user muốn, đo tiếp bằng name-level IC (N lớn, có power) thay vì
portfolio backtest (N=14, không có power).

## Provenance / audit
- Point-in-time đã xác minh: `ticker_financial.time == Release_Date` (SAB 2026Q1 → 2026-04-23), DCF
  chỉ đọc `fin.time <= asof` → không look-ahead.
- Nguồn: `data/bq_cache/ticker_prune/*.parquet` (chunked — tra `kb/data_registry.md` trước, tránh
  bẫy monolith đóng băng 06-26), `ticker_financial.parquet`, `dcf_valuation.fair_value()`.
- threads=1, tie-break stable-sort `(pbz,ticker)` theo chuẩn determinism 2026-07-13.
- **Không có self-check 0 VND**: đây là selection-study rank/forward-return, không phải NAV sim —
  không có ledger tiền để đối soát. Nói rõ thay vì claim một gate không chạy.
- Scripts: `dcf_mechanism.py`, `pool_variants.py`, `loo_check.py`; data: `holdings_dcf.csv`, `pool_dcf.csv`.
- Production `capit_basket()` KHÔNG bị sửa (R&D thuần tuý).
