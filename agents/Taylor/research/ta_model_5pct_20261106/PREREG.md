# PREREG — Model kỹ thuật định lượng "deal ±5%" bổ trợ Livermore (PAPER-ONLY)
Job `Taylor_20261105_171103` · viết 2026-11-06 00:2x ICT TRƯỚC khi chạy engine lần đầu. Không sửa sau khi
thấy kết quả; mọi lệch khỏi file này ghi ở REPORT §Lệch PREREG.

## 0. Tiền lệ phải vượt (đã đóng, không lặp)
`kb/projects/ta-schools-vn-20261025.md`: chỉ họ xu hướng/breakout hơn mua ngẫu nhiên (F1), không cái nào
hơn "giá > MA50 dốc lên" (F2); mọi tín hiệu đảo chiều/bắt đáy THUA ngẫu nhiên. Ở đây câu hỏi KHÁC: không
phải lợi suất trung bình h phiên mà **xác suất chạm +5% trước −5% với ràng buộc T+2 thực tế**, trên mã
thanh khoản CAO (≥20 tỷ), và đầu ra là xác suất đã hiệu chỉnh để Livermore xem SAU khi khoá dự báo.
Giả thuyết trước: kỳ vọng NO-GO cho họ đảo chiều; họ xu hướng có thể > ngẫu nhiên nhưng khó vượt hoà vốn.

## 1. Dữ liệu (point-in-time)
- `data/bq_cache/ticker/*.parquet` (mirror `tav2_bq.ticker`), OHLC **điều chỉnh** (Close/Open/High/Low cùng
  hệ), `Price` thô. Chỉ báo tự tính từ OHLCV điều chỉnh (công thức chuẩn, chỉ dùng dữ liệu ≤ T0); đối chiếu
  với cột BQ `MA20/MA50/MA200` để chứng minh tương đương. KHÔNG dùng `profit_*`, `*_center_*`, `PC1W..PC2M`,
  `Open_1D`, `O1W..O2Y` (forward-looking).
- Universe: `tav2_mike.universe_pit` (cache `data/bq_cache/universe_pit`), `in_universe=True` tại T0.
- Thanh khoản: **MDV60 thực** = trung vị 60 phiên (T0−59..T0) của `Price×Volume` chia `Inflation_7` (quy về
  VND 2026). Bậc: **L20 ≥ 20 tỷ, L50 ≥ 50 tỷ, L100 ≥ 100 tỷ** (lồng nhau).
- Giai đoạn: T0 ∈ [2014-01-01, cuối dữ liệu − đủ H]. IS = 2014–2019, OOS = 2020+. Phụ: post-FTSE T0 ≥ 2026-09-21.

## 2. Mô hình deal (cố định)
- Tín hiệu chốt ở close T0 → lệnh mua phiên B = T0+1 (phiên kế tiếp của mã).
- Giá vào: LO trần = Close_T0 × 1,03. Open_B ≤ trần → khớp Open_B; Open_B > trần mà Low_B ≤ trần → khớp
  tại trần; Low_B > trần → **KHÔNG KHỚP** (ghi nhận, loại khỏi deal, báo tỉ lệ). Phiên B "trần trắng"
  (High=Low và Open_B > Close_T0) → không khớp.
- Mức: TP = P_vào×1,05; SL = P_vào×0,95 (trên giá khớp thô, trước phí).
- Không thoát trước chiều B+2. **Bản C (bảo thủ)**: xét close từng phiên d = B+2..B+H; Close_d ≥ TP → bán
  tại Close_d; Close_d ≤ SL → bán tại Close_d. **Bản HL (lạc quan)**: B+2 chỉ xét close như bản C; từ B+3:
  Open_d ≥ TP → bán Open_d; Open_d ≤ SL → bán Open_d (gap xấu hơn mức); else Low_d ≤ SL → bán tại SL
  (ưu tiên SL nếu cùng phiên chạm cả 2); else High_d ≥ TP → bán tại TP.
- Sàn trắng (High=Low, Close_d < Close_{d−1}) phiên phải bán → không bán được, bán Open phiên kế tiếp.
- Hết hạn: H ∈ {10, 20} phiên tính từ B → bán close B+H. Thiếu dữ liệu tương lai → loại (ghi số).
- Chi phí: 0,097%/chiều + slippage s ∈ {0,1; 0,2; 0,3}%/chiều; **chính = 0,2%**.
  Lợi suất ròng = P_ra(1−f−s)/(P_vào(1+f+s)) − 1.
- "Thành công" = thoát lý do TP (chạm +5% trước −5% trong H). Hoà vốn win-rate cho deal ±5% thuần (bỏ qua
  overshoot/timeout): p* = (1 − a·0,95)/(a·1,05 − a·0,95) với a = (1−f−s)/(1+f+s).

## 3. Họ pattern (tham số sách giáo khoa, KHÔNG tune) — 6 pattern
- **P1 BRK** breakout có volume: Close_T0 > max(High T0−60..T0−1) VÀ Vol_T0 ≥ 1,5×TB Vol 20 phiên trước VÀ Close>MA50.
- **P2 PB20** pullback MA20 trong uptrend: MA50>MA200, MA50 > MA50 20 phiên trước, Close>MA50,
  Low_T0 ≤ MA20×1,01 VÀ Close_T0 ≥ MA20, đỉnh 20 phiên trước T0 ≥ MA20×1,05 (đã có nhịp lên).
- **P3 PB50** pullback MA50 trong uptrend: MA50>MA200, MA200 > MA200 20 phiên trước, Low_T0 ≤ MA50×1,01 VÀ Close_T0 ≥ MA50.
- **P4 SQZ** co hẹp rồi bung: bề rộng Bollinger(20,2)/MA20 tại T0−1 ≤ phân vị 20% của 120 phiên trước, VÀ
  Close_T0 > dải trên VÀ Vol_T0 > TB Vol 20.
- **P5 OSB** oversold bounce: RSI14(Wilder) T0−1 < 30 VÀ Close_T0 > High_{T0−1}.
- **P6 FTD** follow-through cấp mã: Close giảm ≥15% từ đỉnh 60 phiên tới đáy L (đáy = min Close 20 phiên),
  ngày FTD = phiên thứ 4..10 kể từ đáy, tăng ≥ +3% close-to-close với Vol > Vol phiên trước và > TB Vol 20,
  và chưa thủng đáy L.
- Mỗi (mã, pattern) hồi chiêu 10 phiên (không đếm lại tín hiệu chồng).
- **Số trial khai báo**: 6 pattern × 3 bậc × 2 H × 2 bản chạm = **72** (slippage 0,1/0,3 là độ nhạy, không vào họ).

## 4. Baseline + suy diễn
- Đối chứng = **mọi** mã đủ điều kiện (universe + bậc thanh khoản) cùng T0, cùng mô hình deal (= vào ngẫu nhiên
  cùng ngày). exP = P(TP)_sig − P(TP)_ctrl cùng ngày; exR = R_ròng_sig − R_ròng_ctrl cùng ngày.
- **N độc lập = số NGÀY tín hiệu** (gộp các mã cùng T0 thành 1 quan sát trung bình); bootstrap khối theo
  THÁNG (5000 lần) cho CI/p. Báo N_dòng, N_ngày, N_tháng.
- Tiêu chí "có edge dùng được" (tất cả phải đạt, ở s=0,2%, bản C): (a) mean R_ròng > 0 cả IS lẫn OOS;
  (b) exR > 0 với p_boot < 0,05 OOS; (c) P(TP)_OOS > p*; (d) DSR ≥ 0,95 trong họ 72; (e) leave-one-year-out
  không đổi dấu exR quá 1 năm; (f) PBO < 0,5 của họ.
- PBO: CSCV, S=16 khối thời gian, metric = trung bình exR theo khối.
- Calibration: logistic IS (đặc trưng: dummy pattern, bậc, VNINDEX>MA50, khoảng cách Close/MA50) dự báo P(TP)
  bản C H=20 s=0,2%; OOS: Brier, Brier của đối chứng (tần suất nền IS), reliability 10 bin, BSS.

## 5. Self-check
- Chân control (mọi mã đủ điều kiện) tính lại độc lập bằng vòng lặp thuần Python trên mẫu ngẫu nhiên 300 deal
  → chênh 0 (|Δ| < 1e-12) về giá vào/ra/lý do.
- MA tự tính vs cột BQ MA20/MA50/MA200: tỉ lệ khớp (|Δ|/Close < 1e-3).
