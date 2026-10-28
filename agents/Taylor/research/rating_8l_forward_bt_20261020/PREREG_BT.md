# PREREG_BT — Rating 8L G1: backtest có phí (sleeve mô tả, KHÔNG tối ưu)

Job `Taylor_20261020_055002` · 2026-10-20 (giờ thật = giờ commit). Viết + commit TRƯỚC khi chạy bất kỳ chân nào của
backtest (kể cả chân control). EXPLORATORY · PAPER-ONLY · KHÔNG ghi `data/results_registry.md`, KHÔNG pin, KHÔNG đề xuất wire.

## 1. Dữ liệu (vintage khai báo)
- Giá/khối lượng: **`tav2_pin.ticker_pin_202610`** (snapshotTime 2026-10-01T15:00:12Z, 1.294 mã, time 2000-07-28→2026-10-01)
  — KHÔNG đọc `tav2_bq.ticker` hiện tại (mất 243 mã). Kéo cột ticker, time, Close, Price, Volume từ 2013-09-01 cho mọi mã
  từng in_universe từ 2013-09-01 → `raw/px_pin.parquet` (md5 ghi REPORT).
- Sự kiện: `fa.parquet`, `tf.parquet`, `univ.parquet` của `rating_8l_lag_p2_20261020/raw/` (md5 trong PREREG vòng 2) —
  KHÔNG đổi, để chỉ một trục (nguồn giá) khác vòng 2.
- Lãi tiền nhàn rỗi: `idle_rate_proxy_dep1m_aaed41eec.py` (= `git show aaed41eec:WorkingClaude/idle_rate_proxy.py`, md5
  `7829aa27602379ca31229195b83bc61e`), tier `dep1m` PIT.
- R3 + book LAG: ledger pin `data/pinned_ledgers/2026-09-28__R3-anchor-pin0pct-sexies__4707bcbe.csv.gz` (pin0% = SÀN) và
  `2026-09-28__R3-pin1M-dau-TRAN-dai__bcd0469f.csv.gz` (pin1M = TRẦN); đọc DAILY `combined_nav` (R3) và `nav_lag_ref`
  (book LAG, ledger 25B độc lập). Kiểm md5 bằng `bin/pin_ledger.py` trước khi đọc.

## 2. Chân control (đọc TRƯỚC kết quả chiến lược)
- C0 tái lập: chạy `event_study_v2_frozen.py` trên ĐÚNG raw vòng 2 ⇒ md5 `out_v2_criteria.csv` phải = `90f6f340…` và G1 [2,40]
  δ = +1,55%. Không khớp ⇒ dừng, không đọc kết quả.
- C1 vintage: cùng code, chỉ thay px/vol bằng `px_pin.parquet` ⇒ báo δ G1 [2,20]/[2,40] + (b) IS/OOS. Đây là đo ảnh hưởng
  của 113 mã thiếu lên vòng 2 (1 trục). Chỉ MÔ TẢ, không đổi verdict vòng 2 trong job này (sẽ báo Mike).

## 3. Chiến lược (một cấu hình chính, khai trước)
- Tín hiệu: mọi sự kiện G1 (rating quý trước ≥4 → ≤3) eff ∈ [2014-07-01, 2026-07-31], qua luật loại ca (a)-(c) của vòng 2,
  in_universe tại phiên 0. KHÔNG dùng lọc dựa trên dữ liệu sau phiên 0 (loại "<80% phiên có giao dịch [−60,+40]",
  "|r|>40%" của event study là nhìn trước ⇒ không áp). KHÔNG khớp SUE/momentum (chiến lược mua toàn bộ G1).
- Vào lệnh: ramp 3 phiên — 1/3 mục tiêu ở close phiên +1, +2, +3 (thực thi T+1 so với phiên 0; quy ước "ramp 3 phiên" của
  CLAUDE.md). Mỗi tranche giữ đúng H = 40 phiên rồi bán ở close (phiên +41, +42, +43). Giá khớp = `Close` (đã điều chỉnh)
  ngày khớp. Mã ngừng giao dịch ngày khớp ⇒ dời sang phiên kế có giá (tối đa 5 phiên, quá ⇒ bỏ tranche vào / bán ở giá
  cuối có được cho tranche ra).
- Cỡ vị thế: mục tiêu mỗi sự kiện = min(**10% NAV sleeve** tại phiên 0 [trần 0,10/mã như rổ custom30], 3 × 20% × ADV)
  với ADV = trung vị Price×Volume (giá THÔ, quy ước `LAG_ADV_BASIS="price"`) 60 phiên [−60,−1] (≈ Volume_3M_P50 × Price);
  mỗi tranche ≤ 20% ADV (quy ước "capped at 20% of ticker ADV/day" của engine V2.4). Không margin: tổng vị thế ≤ 100%
  NAV sleeve; thiếu tiền ⇒ tranche co lại bằng tiền có; tiền < 0,5% NAV ⇒ bỏ tranche (đếm "loại do vốn").
  Cùng mã đang giữ có sự kiện mới ⇒ bỏ sự kiện mới (đếm).
- Phí: TC **0,1% mỗi chiều** trên giá trị khớp. Không mô hình slippage, không thuế (CAGR thật ≈ backtest − 1,5%).
- Vốn sleeve: **2,5 tỷ** (= 5% × 50 tỷ, tỉ trọng dùng ở §5). Chạy thêm vốn 50 tỷ CHỈ để báo công suất.
- Tiền nhàn rỗi: hai đầu dải — **pin0%** (0%/năm, SÀN) và **pin1M** (dep1m PIT, %/năm × ngày lịch/365, TRẦN).
- Self-check 0 VND mỗi ngày: cash_t − cash_{t−1} = Σbán − Σmua − phí + lãi; NAV = cash + Σ shares × Close (ffill).
  Dư khác 0 (>1 VND) ⇒ dừng.

## 4. Biến thể (N_trials = 3, khai trước — DSR dùng N = 3; KHÔNG chạy PBO vì < 8)
- **V1 (CHÍNH)**: như §3, H = 40.
- V2 (mô tả): H = 20.
- V3 (mô tả): như V1 + chỉ nhận sự kiện có ADV ≥ 5 tỷ VND/ngày.
Verdict chỉ đọc V1. Không thêm biến thể sau khi xem kết quả.

## 5. Đánh giá
- Sleeve một mình (V1, mỗi đầu dải): CAGR (thời gian lịch), Sharpe_252, MaxDD; IS = 2014-07-01→2019-12-31, OOS = 2020-01-01→
  cuối; CI95 bootstrap khối QUÝ (2.000 lần, seed 20261020) của lợi suất năm hoá trung bình ngày; DSR (Bailey-López de Prado)
  với N_trials = 3, phương sai SR giữa 3 biến thể.
- Tương quan lợi suất ngày và tháng của sleeve V1 với (i) book LAG (`nav_lag_ref`), (ii) R3 (`combined_nav`), mỗi đầu dải
  dùng ledger tương ứng; giai đoạn chồng lấn 2014-07-01→2026-06-19 (audit_end R3).
- **Đóng góp biên** (khai trước tỉ trọng **w = 5% NAV cố định**, cân lại mỗi ngày, không tính phí cân lại giữa 2 phần —
  giản lược khai báo): r_mix = 0,95·r_R3 + 0,05·r_sleeve, so với R3 một mình: ΔCAGR, ΔSharpe, ΔMaxDD, mỗi đầu dải;
  CI95 bootstrap khối quý của ΔSharpe (cặp ngày giữ nguyên); ΔSharpe theo IS/OOS.
- Công suất: số mã giữ/ngày (trung bình, p90, max), tỉ lệ vốn dùng (trung bình), % sự kiện bị cắt/loại do trần ADV, do vốn,
  do trùng mã — ở vốn 2,5 tỷ và 50 tỷ.

## 6. Nhãn kết luận (V1, chỉ ba nhãn)
- **"có đóng góp tăng thêm sau phí"**: ở CẢ pin0% và pin1M: ΔSharpe toàn kỳ > 0 với cận dưới CI95 > 0, VÀ ΔSharpe > 0 ở cả
  IS và OOS, VÀ DSR sleeve ≥ 0,95.
- **"không có"**: ΔSharpe toàn kỳ ≤ 0 ở ít nhất một đầu dải.
- **"không phân biệt được (thiếu N)"**: mọi trường hợp còn lại.
Mọi số báo cáo gắn nhãn EXPLORATORY.
