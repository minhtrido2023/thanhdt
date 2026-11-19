# PREREG — A5 (quy kết suy giảm theo ngành) + B2 bước 1 (đếm định tuyến 13 mã) + H-8L-3 (đếm bank-nodata)
Job `Taylor_20261119_090446` · viết 2026-11-19 TRƯỚC khi tính bất kỳ thống kê nào. Read-only; không NAV mới; không wire.

## A5
- Dữ liệu: `../lag_bal_discriminators_20261025/features.csv` (pin0%, md5 sổ 537e349b) và `features_pin1M.csv`. Lọc abandoned==0 & mtm==0.
  Nhóm: 7 nhóm cố định = `groups.py` (đã kiểm: tái lập 42/42 ô n và TB của `appendix_deals_by_sector_era.csv` pin0%).
  Nhóm 1 (hàng hoá tier A/B theo commodity_map_te.csv) ưu tiên trước; còn lại theo ICB tại signal_date.
- Thống kê: Δ = TB(ret, 2024+) − TB(ret, 2014-19) theo (sổ, nhóm). 14 phép (BAL,LAG × 7 nhóm), mỗi đầu dải.
- Bootstrap: cụm = tháng vào lệnh (`ym`); resample tháng có hoàn lại, ĐỘC LẬP trong từng era (2024+, 2014-19); B=20000, seed=20261119.
  CI90 = phân vị 5/95. p hai phía = 2·min(P(Δ*≤0), P(Δ*≥0)) (sàn 1/B). BH-FDR trên 14 p mỗi đầu dải (q=0,10); BH báo thêm, không đổi nhãn CI.
- Nhãn khai trước: "tụt có ý nghĩa" ⇔ CI90 trên < 0 ở CẢ pin0% và pin1M. Còn lại "không phân biệt được".
  (Chú thích thêm: nhãn đó có qua BH q<0,10 ở cả hai đầu hay không — chỉ ghi chú.) Ô thiếu lệnh ở một era ⇒ "không phân biệt được".
- Tự kiểm: tái lập ΣTB trong appendix; ΣPnL không đổi; bootstrap tái lập theo seed.

## B2 bước 1 (đếm)
- NOTE lệch brief: `build_rating_8l_history.py` là bản CŨ (BANK/POWER=3 cứng, ra `.pkl`, 06-05). Bản production là `rating_8l_history.py`
  (ra `data/rating_8l_history.csv`, cron `refresh_fa_ratings_8l.sh`). Dùng BẢN PRODUCTION.
- Làm trên BẢN SAO `b2/rating_8l_history_copy.py`, chỉ đổi `route_of`: thêm 13 mã {PVS,PVD,PVC,PVB,GAS,BSR,TLH,VOS,HAH,DRC,CSM,BMP,NTP} vào tập CYCLICAL
  (đặt SAU kiểm POWER icb==7535 như bản gốc ⇒ GAS ICB 7573 không bị POWER; ghi rõ nếu 13 mã có mã nào vốn đã ở tuyến khác). Env: R8L_HIST_OUT riêng, R8L_HIST_NO_BQ_REFRESH=1.
- Chạy 2 lần cùng vintage BQ: CONTROL (bản sao không đổi) và TREATMENT. Control vs `data/rating_8l_history.csv` hiện có: báo số dòng khác (vintage). 
  `data/rating_8l.csv` và `data/rating_8l_history.csv` md5 trước/sau phải BẰNG NHAU.
- Đếm: cặp (mã, quý) trong 13 mã mà (rating<=3) khác nhau giữa TREATMENT và CONTROL, 2014→nay; tách chiều (qua→trượt / trượt→qua);
  cặp nào gắn với lệnh LAG/BAL trong ledger pin0% hoặc pin1M (dòng rating hiệu lực tại signal_date = merge_asof theo eff_date ≤ signal_date).
- Khai trước: < 30 cặp đổi cổng ⇒ DỪNG (không bước 2). ≥ 30 ⇒ chỉ báo số, bước 2 cần user duyệt riêng.

## H-8L-3 (chỉ đếm)
- 10 mã VAB,KLB,NVB,PGB,SGB,PCB,ABB,BAB,BVB,VBB: (a) hiện rating/note trong `data/rating_8l.csv`; (b) có trong `tav2_mike.universe_pit` (in_universe) lúc nào;
  (c) từng được LAG/BAL mua (2 ledger); (d) nếu mặc định bank-nodata/bank-noROE 3→4: số cặp (mã, quý) đổi cổng ở lịch sử = số dòng history của 10 mã có rating 3 sinh ra từ nhánh ROE NaN
  (ROE_Trailing, ROE5Y, ROE3Y cùng NaN, từ ticker_financial) — lưu ý history đã fail-closed từ 2026-09-27 (override_current_bank_aq từ chối nodata) nên cổng LIVE là dòng `rating_8l.csv`;
  (e) ROE_Trailing mới nhất của STB/EIB/SSB từ ticker_financial và nhánh rating trong `rating_8l.csv`.
- Không đề xuất sửa rating.
