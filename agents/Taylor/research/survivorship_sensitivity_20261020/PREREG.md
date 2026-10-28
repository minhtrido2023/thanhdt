# PREREG — Stress test độ nhạy survivorship của R3 (job Taylor_20261020_082308)

EXPLORATORY. Không sửa số pin R3/V2.4, không ghi `data/results_registry.md`, không `pin_ledger.py add`.
Viết + md5 + commit TRƯỚC khi chạy overlay Monte Carlo. Control leg (chạy lại engine) đã khởi động trước
— nó không phụ thuộc lựa chọn nào dưới đây.

## 0. Dữ liệu
- Danh sách rời sàn: `mike/kb/projects/delisted-tickers-survivorship-20261020.csv` (Winston), cột `in_data`.
  Spot-check 5 mã ngẫu nhiên (`random_state=20261020`, bỏ `chuyen_san`): TGG/PX1/CVH (`in_data=False`) có
  0 dòng ở `tav2_pin.ticker_pin_202610`, `ticker_financial`, `universe_pit`; DCS/IHK (`True`) có đủ ⇒ 5/5 khớp.
- Ledger control: 4 chân, đọc qua `bin/pin_ledger.py extract` và đối chiếu md5 với chân chạy lại:
  `4707bcbe` (park 0.3, pin0%) · `bcd0469f` (park 0.3, pin1M) — như dispatch ghi; và `537e349b` (park 0, pin0%)
  · `a6ba34d8` (park 0, pin1M) — R3 ở knob LIVE theo registry mục "2026-10-08". Báo cả hai cặp; cặp dispatch
  nêu là cặp chính.
- Giá control lấy từ cache `data/bq_cache_asof20260729_postrestate`, đúng lệnh pin (không đọc `tav2_bq.ticker` live).

## 1. Mô hình phantom (overlay lên NAV ngày của control, không chạy lại engine)
Mỗi sự kiện phantom j: ngày biến mất `t1_j`, ngày vào `t0_j = t1_j − 365 ngày lịch` (cắt ở 2014-01-02).
Tỉ trọng `w_j = w(t0_j)` = tỉ trọng TRUNG BÌNH một mã trong danh mục ngày t0
= (cổ phiếu BAL+LAG + ETF/rổ) / combined_nav / (số vị thế mở BAL+LAG + 30 nếu ETF>0), số vị thế dựng lại từ TX.
Giữ nguyên số lượng suốt [t0, t1]; giá phantom đi tuyến tính 1 → 1−L (dạng chính) hoặc giữ 1 rồi rơi một lần
ở t1 (dạng "vách", chỉ báo phụ cho DD). Phần vốn đó lẽ ra hưởng lợi suất danh mục R(t0,t).
- t0 ≤ t < t1: `NAV'_t = NAV_t · (1 − w_j · (1 − p_t / G_{t0,t}))`, G = NAV_t/NAV_t0 (control).
- t ≥ t1: hệ số đóng băng ở giá trị tại t1 (phần mất không hồi phục, phần còn lại quay về danh mục).
Nhiều sự kiện: nhân các hệ số. Chân pin0% và pin1M dùng NAV của chính chân đó.

## 2. Kịch bản
Số sự kiện ~ Poisson(λ · số năm cửa sổ), `t1` đều trên [2014-01-02, 2026-06-19].
- **L** ∈ {−30%, −50%, −80%, −100%}.
- **λ (phantom THỰC SỰ NẮM/năm)** = D × p_zone × p_hold:
  - D = số mã rời sàn MẤT khỏi data/năm, HOSE/HNX/không rõ sàn, cat ∈ {bat_buoc, khac_khong_ro, tu_nguyen},
    năm 2014–2025 (đếm từ CSV). Biến thể rộng D+ thêm `mat_tu_cach_DC` HOSE/HNX và `bat_buoc` UPCOM.
  - p_zone (GIẢ ĐỊNH) ∈ {5%, 10%, 20%}; tham chiếu quan sát 7,9% (10/127 nhóm còn data).
  - p_hold: **trần** = 1 (mọi mã vùng mua bị biến mất đều được nắm trọn 12 tháng);
    **trung vị** = (số mã trong 10 mã "vùng mua" của Winston mà ledger control có nắm ≥1 ngày trong 12 tháng
    trước `ann`) / 10 — đo từ ledger, không chọn tay.
  - **λ_emp** (neo thực nghiệm, độc lập p_zone): D × (số mã trong 127 mã bắt buộc-còn-data mà ledger có nắm
    ≥1 ngày trong 12 tháng trước `ann`) / 127.
- Lưới hòa vốn: λ ∈ {0,1; 0,25; 0,5; 1; 2; 3}/năm × L.
- Kịch bản "xấu nhất hợp lý" = D+ × 20% × p_hold=1, L=−100%. "Trung vị" = D × 10% × p_hold(trung vị), L=−50%
  (gần mean −46% / median −38% của 10 mã); λ_emp × L=−50% báo cạnh.

## 3. Monte Carlo
- 2000 lần mỗi ô, `numpy.random.default_rng(20261020)`, cùng chuỗi số ngẫu nhiên cho mọi ô (common random numbers).
- Metric tính lại từ NAV ngày đã overlay đúng công thức engine (CAGR theo năm lịch, Sharpe √252, MaxDD).
  Trước hết phải tái tạo đúng METRIC của ledger control (sai lệch < 1e-9) — không đạt thì dừng.
- Báo ΔCAGR / ΔSharpe / ΔMaxDD so control: trung vị và khoảng 5–95%, ở cả pin0% và pin1M.

## 4. Tiêu chí kết luận (nhãn duy nhất)
Sàn nhiễu W2b = 0,46 pp CAGR.
- "nhỏ hơn sàn nhiễu 0,46pp ở mọi kịch bản hợp lý": |trung vị ΔCAGR| < 0,46pp ở kịch bản trung vị VÀ xấu nhất hợp lý.
- "vượt sàn nhiễu ở kịch bản X": trung vị |ΔCAGR| ≥ 0,46pp ở ít nhất một kịch bản hợp lý (nêu X).
- "không đủ căn cứ": không tái tạo được control, hoặc p_hold không đo được.
- Ngưỡng hòa vốn: λ* (nội suy tuyến tính trên lưới) để trung vị ΔCAGR = −0,5pp, theo từng L.
Không tự kết luận lại số pin.
