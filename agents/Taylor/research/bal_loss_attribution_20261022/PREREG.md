# PREREG — Chẩn đoán lỗ sổ BAL (job Taylor_20261022_093122)

READ-ONLY. Không sửa production, không pin registry, không ghi tên file canonical. Output chỉ nằm
trong thư mục này.

## 0. Những gì ĐÃ THẤY trước khi viết PREREG (khai trung thực)
Lúc khảo sát nguồn dữ liệu tôi đã thấy:
- Journal live (`data/execution_logs/exec_{SpaceX,ZaloPay}_*_journal.csv`, cột `book`) chỉ có FILL
  `book=BAL` cho đúng MỘT mã: **VPI** (mua 17-18/09, bán `BAL_AUTO_EXIT` stop-loss 16/10), ở cả 2 tài
  khoản. Plans 07-31 → 09-16 có ứng viên BAL (AGG, VIC, VPI) nhưng không thành lệnh (thiếu tiền /
  signal_hold paper-track).
- Mức NAV thô ở `nav_history_*.csv` (SpaceX ~990tr → ~970tr; ZaloPay ~997tr → ~920tr); chưa thấy dòng
  21/10.
Mọi phép đo dưới đây khoá TRƯỚC khi tôi tính bất kỳ con số P&L/beta/phân phối nào.

## 1. Câu hỏi
Q1. Cửa sổ lỗ: đỉnh-đáy NAV mỗi tài khoản; phần đóng góp RIÊNG của sổ BAL, và (để đặt BAL vào bối cảnh)
    phần của từng sổ khác trong cùng cửa sổ.
Q2. Phân rã lỗ BAL: beta VNINDEX / phần dư momentum; top mã + ngành; thời điểm vào; cutloss; momentum crash.
Q3. So với backtest R3 pin0% (ledger `4707bcbeb7e801d49a4a851ffd91d5e7`), cùng thước đo.
Q4. Lịch sử: BAL trong các nhịp VNINDEX bật mạnh sau giảm sâu.
Q5. Kết luận + nhánh xử lý không bị bằng chứng bác.

## 2. Nguồn (tra `mike/kb/data_registry/` trước)
- NAV: `nav_history_<acct>.csv` (CANONICAL). Không có dòng ngày nào thì báo "chưa có", không suy.
- Fill: journal `FILL` (cột `book`), đối chiếu `dnse_raw_<date>.jsonl` (lọc `accountNo`, §12).
- Vị thế ngày: `verified_snapshot_<acct>_<date>.json` (qty × mtm_price).
- Giá lịch sử VPI/VNINDEX (ngày đã qua, sau sync): BQ `tav2_bq.ticker` (Close adj). Không có số trong ngày.
- Backtest: ledger pin `data/pinned_ledgers/2026-09-28__R3-anchor-pin0pct-sexies__4707bcbe.csv.gz`
  (md5 raw 4707bcbe…). KHÔNG chạy lại engine.
- Phí live: 0,097%/chiều (`bin/dnse_fee_rates.py`, coding_guidelines §6).

## 3. Cách đo (khoá)
Q1.
- Đỉnh-đáy: trên cột `nav` của nav_history, cửa sổ từ dòng đầu → dòng cuối có sẵn; đỉnh = max chạy, đáy =
  min sau đỉnh đó cho MaxDD; báo ngày + %. Kiểm dòng tiền ngoài (nạp/rút) trong cửa sổ bằng
  `sleeve_transfers.json`/`account_inception.json`/note offbook; có dòng tiền thì nêu, không tự hiệu chỉnh.
- P&L BAL: Σ(tiền bán) − Σ(tiền mua) − phí 0,097% mỗi chiều trên giá trị khớp, từ FILL journal; đối chiếu
  tổng KL/giá trị với dnse_raw. Báo VND và % NAV tài khoản ngày trước lệnh mua đầu.
- P&L theo sổ trong cửa sổ đỉnh→đáy của mỗi TK: theo mã, `MV_cuối − MV_đầu + bán − mua − phí` (MV từ
  verified_snapshot; FILL trong (đỉnh, đáy]). Mã → sổ: tag `book` của FILL gần nhất của mã ở TK đó; không có
  tag ⇒ `book`/`strategy` của order cùng mã trong plan; vẫn không có ⇒ `UNKNOWN` (báo riêng). Phần còn
  lại (NAV Δ − Σ mã) = tiền/lãi trứng/phí khác, báo là `residual`.
Q2. (chỉ trên VPI, N=1 lệnh × 2 TK)
- Return lệnh = giá bán bình quân / giá mua bình quân − 1 (trước và sau phí).
- VNINDEX cùng kỳ: Close ngày trước ngày khớp mua đầu → Close ngày bán.
- β VPI: OLS log-return ngày VPI trên VNINDEX, 250 phiên kết thúc ngày trước ngày mua đầu (không nhìn trước).
  Phần beta = β × R_VNI; phần dư = R_VPI − β × R_VNI. Thêm phiên bản β=1 làm độ nhạy.
- Ngành: `ICB_Code` BQ. Vào lệnh: giá mua so với max Close 20 phiên và 250 phiên trước ngày mua; tăng
  60 phiên trước mua. Cutloss: lý do exit từ parent_id/play_type + dòng code stop của BAL live.
- (e) Momentum crash: chỉ kết luận được nếu BAL có vị thế trong nhịp bật; đo số vị thế BAL ngày 21/10.
Q3.
- (i) Per-trade: phân phối return theo holding của BAL lệnh cổ phiếu (play_type ∉ {ETF_PARK, CAPITB_*}),
  holding đã đóng (có sell, bỏ ABANDONED_REFUND), return = Σsell/(Σbuy+Σfee) − 1. Báo phân vị của lệnh VPI,
  và riêng nhóm exit `STOP`.
- (ii) NAV toàn TK: MaxDD live (Q1) vs R3 MaxDD −14,6% và bootstrap 5th −25,2% (pin0%, combined NAV).
- (iii) Cùng thước đo "lỗ sổ BAL / NAV toàn hệ": trong ledger, P&L sổ BAL theo cửa sổ 21 phiên không chồng
  lấn (Δnav_bal_ref / combined_nav đầu cửa sổ); báo phân vị của số live.
Q4.
- Episode: ngày t có VNINDEX ret(t) ≥ +2,0% VÀ Close(t−1) ≤ 0,92 × max Close 60 phiên trước (t−60..t−1).
  Episode mới chỉ khi cách ngày bắt đầu episode trước ≥ 20 phiên. Nguồn VNINDEX = `vni_close` trong ledger,
  2014-01-02 → 2026-06-19 (cửa sổ backtest; dùng 60 phiên đầu làm warm-up).
- Đại lượng: return sổ BAL (`nav_bal_ref`) và excess = BAL − VNINDEX trên [t, t] và [t, t+4] (5 phiên,
  từ Close t−1). Đối chứng: cùng đại lượng trên MỌI ngày (không điều kiện).
- Thống kê cho N nhỏ: liệt kê từng episode; đếm dấu (excess < trung vị không điều kiện) + binomial chính xác
  p=0,5 một phía; phân vị của trung vị episode trong 10.000 lần rút N ngày ngẫu nhiên (seed 20261022).
  Không t-test. Không gọi đây là kiểm định edge (đây là mô tả; preflight DSR không áp dụng vì không đề xuất
  rule).
- Độ nhạy (chỉ báo, không đổi kết luận): ngưỡng (−10%, +2,5%).
- Tiêu chí "BAL tụt hậu trong nhịp bật": ≥ 2/3 episode có excess 5 phiên < trung vị không điều kiện VÀ
  phân vị resample ≤ 10%. Không đạt ⇒ "không có bằng chứng".

## 4. Tiêu chí kết luận Q3
- Lỗ sổ BAL "ngoài dải" nếu phân vị per-trade của VPI < 5% HOẶC phân vị (iii) < 5%.
- NAV toàn TK "ngoài dải" nếu MaxDD live tệ hơn −25,2%; trong (−14,6%; −25,2%] = trong dải bootstrap nhưng
  sâu hơn pin; nông hơn −14,6% = trong pin.

## 5. Ràng buộc
threads=1; không dùng profit_*; không backtest mới ⇒ self-check 0 VND không áp dụng; kiểm tính nhất quán
ledger: combined_nav ≈ nav_bal_ref + nav_lag_ref (báo sai lệch lớn nhất).
