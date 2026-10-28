# PREREG — Rating 8L Phần 2 vòng 2 (tách rating khỏi PEAD)

Job `Taylor_20261020_045201` · viết 2026-10-20 ~12:05 ICT, TRƯỚC khi tính bất kỳ CAR nào của vòng 2.
Thiết kế theo chỉ đạo Mike (user duyệt 2026-10-20) sau verdict REFUTED của quant-skeptic cho vòng 1
(`rating-8l-lag-p2-signal-20261020`). File này được commit + ghi md5 vào REPORT trước khi chạy `event_study_v2.py`.
Read-only: không đổi gate/luật production, không đề xuất wire.

## 1. Dữ liệu (vintage khai báo)
- Tái dùng raw vòng 1 `../rating_8l_lag_p2_20261020/raw/` (kéo BQ 2026-10-20 10:48 ICT), md5:
  fa `14b1921eecb63e664575b747ff438aed` (`tav2_bq.fa_ratings_8l`), tf `dced3011db939fb2e4636742a11cfd9e`
  (`ticker_financial` ticker/quarter/time/Release_Date), univ `ddaad50d3ee297624be7225bca1f3ffe`
  (`tav2_mike.universe_pit` in_universe), px `65c66c7fd2ab7e720d5d128e8dc65442` (`tav2_bq.ticker` Close/Price).
- Lịch phiên: `data/benchmark/vnindex_tr_daily.csv` md5 `eedb164b0df2398974ff6b68062710e3` (chỉ dùng làm lịch).
- Mới kéo: `raw/vol.parquet` = `tav2_bq.ticker` (ticker, time, Price, Volume) cùng tập mã/khoảng ngày như px — chỉ để tính ADV.
- SUE: `data/earnings_surprise_data.pkl` (CANONICAL, registry `lag-book/lag_caches.md`; đọc bằng `$DNA_PYEXE`),
  md5 `42ab446b604768d6f4dbd19bb27a7430`, mtime 2026-10-19 19:02 ICT. File KHÔNG chứa cột SUE PIT lưu sẵn
  (chỉ NP_P0..P7 theo vintage hiện tại) ⇒ dùng **SUE tự dựng** (§3). Giới hạn PIT: giá trị NP là vintage hôm nay
  (restatement không PIT) — cùng giới hạn với chính `fa_ratings_8l`; khai trong REPORT.

## 2. Sự kiện và loại ca (giữ nguyên vòng 1)
- Sự kiện = dòng `fa_ratings_8l` có dòng trước cùng mã, khớp (ticker, quý) trong `ticker_financial` theo eff = Release_Date
  (NULL→time); eff ∈ [2014-07-01, 2026-07-31]. G1: trước ≥4 → sau ≤3. G2: trước ≤3 → sau ≥4. G0: rating không đổi.
  (G3 không thuộc vòng này.)
- Loại: (a) nhìn trộm chắc chắn (RD < cuối quý HOẶC RD ≤ RD quý trước; gồm 7 ca `out_phase3_definite_peek_cases.csv`),
  (b) RD trong 0-7 ngày sau cuối quý (gồm 125 ca Q1 RD đầu tháng 4), (c) RD NULL.
- Phiên 0 = phiên đầu ≥ eff. Cửa sổ dữ liệu cần [−60,+40]. Mã phải `in_universe` (universe_pit) tại phiên 0; loại
  <80% phiên có giao dịch thật trong [−60,+40] hoặc |r| > 40%/phiên. Không dùng profit_*/O*/PC*; không ticker_prune.
- Giá: `Close` (đã điều chỉnh); kiểm lại 1 mã chia tách (VHM 2026-08-07) như vòng 1.

## 3. Biến khớp (đều tính từ thông tin ≤ phiên −1 / ≤ eff)
- **Momentum**: Close[−1]/Close[−61] − 1 của chính mã.
- **SUE tự dựng**: d_q = NP_P0 − NP_P4 của dòng (ticker, quý q). SUE = d_q / SD(d của 8 quý liền trước cùng mã),
  chỉ dùng các dòng quý trước có Release_Date ≤ eff sự kiện; cần ≥6/8 quý có d và SD>0, nếu không ⇒ SUE thiếu ⇒ sự kiện bị
  loại khỏi phép chính (đếm). Kiểm PIT: assert mọi dòng dùng có Release_Date ≤ eff.
- **Ngân hàng**: route = BANK ở dòng sự kiện.
- Phân vị: 5 nhóm momentum và 5 nhóm SUE, mỗi cái tính trong cùng QUÝ LỊCH của eff, trên toàn bộ sự kiện G0∪G1∪G2
  hợp lệ của quý đó.
- **Ô khớp** = (quý lịch, nhóm mom, nhóm SUE, bank). G0* của một sự kiện G = trung bình CAR của các G0 cùng ô.
  Sự kiện G có ô không có G0 nào ⇒ loại (đếm).

## 4. Benchmark và cửa sổ
- **B3** = trung bình EW lợi suất ngày các mã in_universe có giao dịch cùng phiên, LOẠI chính mã sự kiện. Không dùng B2.
- AR = r − B3. **Cửa sổ chính DUY NHẤT**: CAR[2,20], CAR[2,40] (vào close phiên +1).
- Đại lượng chính cho mỗi sự kiện G: δ = CAR_G − mean(CAR_G0 cùng ô). Ước lượng nhóm = trung bình δ.

## 5. Họ phép thử chính F1 = 4 phép
{G1, G2} × {[2,20], [2,40]}; H0: E[δ]=0, hai phía. p chính = block bootstrap theo QUÝ LỊCH (2.000 lần, seed 20261020),
p = 2·min(P(b≤0), P(b≥0)), sàn 1/2000. BH-FDR q=0,05 trên ĐÚNG 4 phép này.
Báo kèm (không đổi verdict): SE/p cluster theo MÃ (CR1); bản loại sự kiện thứ hai của cùng mã trong 40 phiên
(xét trên toàn tập sự kiện G0∪G1∪G2 hợp lệ); N sự kiện, N hiệu dụng = N·SE²_iid/SE²_cluster-quý, số quý, số phép.

## 6. Tiêu chí tái lập — một nhóm là "CÓ" nếu ∃ cửa sổ thoả CẢ (a)-(d)
(a) q_BH < 0,05 (F1).
(b) IS = eff 2014-2019 và OOS = 2020+: mỗi nửa cùng dấu với ước lượng toàn mẫu và p_boot < 0,10.
(c) Bỏ 3 quý lịch có tổng δ lớn nhất THEO CHIỀU dấu toàn mẫu ⇒ vẫn cùng dấu và |ước lượng| ≥ 50% bản đầy đủ.
(d) Sau phí 0,2% khứ hồi: |mean δ| − 0,2% > 0 và cùng dấu, ở cả toàn mẫu VÀ tập con ADV ≥ 5 tỷ VND/ngày
    (ADV = trung vị Price×Volume 20 phiên [−20,−1], VND danh nghĩa). Ghi chú: δ là chênh lệch so với đối chứng, không
    phải lợi nhuận một danh mục thực; (d) chỉ là ngưỡng kinh tế tối thiểu.

## 7. Verdict (theo thứ tự)
1. "không đủ N" nếu N sự kiện khớp < 100 hoặc N hiệu dụng < 30 ở cửa sổ đang xét.
2. "CÓ tín hiệu riêng của rating (tách khỏi PEAD)" nếu (a)-(d) đều đạt.
3. "không tách được khỏi PEAD" nếu bản đối chứng KHÔNG khớp SUE (ô = quý × mom × bank, cùng thống kê, BH riêng trên
   4 phép của nó) đạt (a) cho nhóm đó, nhưng bản khớp SUE không đạt (a).
4. "không có" trong mọi trường hợp còn lại (gồm: đạt (a) nhưng trượt (b)/(c)/(d) — ghi rõ trượt tiêu chí nào).
Mọi thứ khác (bản không khớp SUE, cluster theo mã, bản loại trùng, ngân hàng/phi NH, chi tiết ADV) = THĂM DÒ.
Mọi sai lệch khỏi file này phải khai ở mục riêng trong REPORT.
