# PRELOCK V2 — định giá đa proxy cho thị trường VN (job Taylor_20261124_160038)

Khoá 2026-11-24 ~23:35 ICT, TRƯỚC khi chạy bất kỳ mô hình mới nào. Tới lúc này đã làm: đọc REPORT vòng 1 + verdict
skeptic; kiểm kê registry; kéo giá + BCTC mã vắng BQ từ VNDirect (chưa tính gì trên đó); xem thô 7 dòng HPG 2018–2019 và
phân vị log(BVPS×OShares / (TS − nợ)) để hiểu lỗi cơ sở cổ phiếu. Chưa tính V/P của họ mô hình nào trên panel mới.
Mọi sai lệch so với file này ghi ở REPORT §"Lệch prelock". Biến thể thêm sau khi thấy số ⇒ gắn nhãn **giả thuyết**.

## 0. Dữ liệu và khung PIT (sửa lỗi skeptic 1–3)
- **Một vintage giá:** `Close` và `Price` chỉ lấy từ bảng `ticker` (cache 23/11; trước 2013 kéo BQ `tav2_bq.ticker` cùng ngày).
  KHÔNG dùng `Close`/`Price` của `ticker_financial`. Báo delta so với vòng 1.
- **Không gian tổng giá trị, không theo cổ phiếu:** vốn chủ E = `totalAsset − StLiab − LtLiab` (không phụ thuộc cơ sở cổ
  phiếu); thiếu thì BVPS×OShares. Vốn hoá tại ngày công bố MC(rel) = Price(rel) × N, N chọn giữa hai ứng viên
  {OShares, E/BVPS} theo ứng viên nào khớp hơn với N kỳ trước × bước nhảy hệ số điều chỉnh giá giữa hai kỳ
  (Δlog(Price/Close)); hai ứng viên trùng (lệch <5%) ⇒ dùng OShares. Giữa hai kỳ: MC(d) = MC(rel)×Close(d)/Close(rel).
  Báo số dòng bị đổi, delta, ca kiểm HPG quý 1/2019. Không nhân thêm hệ số điều chỉnh nào (không double-count).
- known_date BCTC = cột `time` của `ticker_financial` (BQ); mã ngoài BQ (VNDirect, không có ngày công bố): cuối quý + 45
  ngày (quý 1–3) / + 90 ngày (quý 4).
- **Sống sót:** panel = `universe_pit.in_universe` (mã có trong BQ) ∪ mã vắng BQ có ở VNDirect (669 mã, 409 đã huỷ) qua
  cổng thanh khoản tự dựng theo ruleset v1 (trung vị GTGD khớp lệnh 60 phiên ≥ 1 tỷ thực để vào; < 0,5 tỷ 20 phiên liên
  tiếp thì ra; giá ≥ 1.000; tuổi ≥ 60 phiên). Lợi suất của mã ngừng giao dịch: giá thật tới phiên cuối (kể cả sau khi
  xuống UPCOM), sau đó áp mức mất H trên giá cuối, **H chính = −50%**, báo cận H = 0% và H = −100%. Mọi chỉ số chính báo
  cả "chỉ BQ" lẫn "BQ + mã vắng" để thấy delta.
- IS = as-of 2014-01→2019-12; OOS = 2020-01→2023-10 (đủ 36 tháng tới 2026-10). N độc lập khai: theo mã ≈ 500–700 cụm;
  theo thời gian IS 2 khối 36T, OOS ≈ 1,3 khối ⇒ sức mạnh theo thời gian YẾU.
- Không dùng `profit_*`. Không tham chiếu mới tới `ticker_prune`. Tiền nhàn rỗi **pin0% (đầu sàn)**; phí 0,1%/chiều.

## 1. Họ mô hình (18 biến thể mới; N trials cộng dồn = 33 vòng 1 + 18 = 51; +6 chiến lược ⇒ DSR dùng N = 57)
Mù giá tuyệt đối (ứng viên Lớp 1), r = 12,25%, g_T = 5,5% như vòng 1:
 1. **A_pit** engine FCFE production, số CP theo cơ sở mới (đối chứng).
 2. **A_RI** ablation: y hệt A (cùng r, g_explicit, g_T, 5 năm, cùng cổng, cùng mẫu) chỉ đổi dòng tiền gốc FCFE 3 năm →
    lợi nhuận thặng dư 3 năm (LN 3 năm TB − r × vốn chủ đầu kỳ TB) + vốn chủ hiện tại.
 3. **D0** RIM-VN vòng 1 trên dữ liệu đã sửa.
 4. **D0J** D0 + cờ "ROE đang nhảy": ROE_TTM − ROE_tc5 ≥ 10đ VÀ doanh thu TTM tăng ≥ 15% so cùng kỳ VÀ biên ròng TTM >
    trung vị biên 5 năm VÀ vốn chủ không giảm so 1 năm trước, đúng ≥ 2 kỳ công bố liên tiếp ⇒ ROE chuẩn hoá = ROE_tc5 +
    w×(ROE_TTM − ROE_tc5), w = 0,75×min(1, k/4), k = số kỳ liên tiếp có cờ.
 5. **D0B** D0J + ngân hàng (route BANK) dùng độ bền κ = 0,7 thay 0,4 (prior: ngành cấp phép, ROE hồi quy chậm).
 6. **DDM** hai giai đoạn cho mã trả cổ tức tiền đều (DY > 0 ở ≥ 16/20 kỳ công bố gần nhất): D₁ = payout trung vị 3 năm ×
    ROE chuẩn hoá × E; g₁ = min(ROE×(1−payout), 15%) fade tuyến tính về g_T trong 10 năm.
 7. **EPV** sức sinh lời: E_norm = doanh thu TTM × trung vị biên ròng 5 năm; V = E_norm×(1 − g/ROE_n)/(r − g),
    g = min(g_T, ROE_n × tỉ lệ giữ lại); không áp cho BANK/INSURANCE/SECURITIES.
Tương đối thị trường (dùng mặt bằng giá của CÁC MÃ KHÁC, không dùng lịch sử giá riêng của mã; nhãn "Lớp 1b"):
 8. **MULT** bội số ngành: trung vị 60 tháng trước (PIT, in-universe, theo route; route < 8 mã ⇒ toàn thị trường) của
    P/E chuẩn hoá, P/B, P/S, EV/EBITDA × cơ sở của mã; V = trung vị các ước lượng có được (≥ 2).
 9. **HEDf** hồi quy hedonic log(P/B) ~ ROE_tc5, ROE_TTM, cờ lỗ, tăng trưởng doanh thu, payout, D/E, SD ROE 5 năm,
    log vốn chủ, dummy route; gộp các lát cắt tháng 60 tháng trước (≥ 24), một hệ số chặn; **đóng băng tại 2019-12 cho
    toàn OOS**.  10. **HEDr** như 9 nhưng tiếp tục cuốn chiếu trong OOS.  11. **HEDL** = HEDr + log GTGD trung vị.
Có dùng giá quá khứ của chính mã (Lớp 2, hiển thị; KHÔNG dùng chọn mã):
 12. **REL** trung vị 60 tháng trước của chính mã (≥ 24, không gồm tháng hiện tại) cho P/E chuẩn hoá, P/B, P/S,
     EV/EBITDA, 1/DY × cơ sở hiện tại; V = trung vị.   13. **G1** = D0 × premium riêng (vòng 1).
Tổ hợp:
 14. **ENS1** trung vị log V của {D0B, DDM, EPV} (không fit).  15. **ENS1w** trọng số ∝ max(IC36 IS, 0) trên {5,6,7,8,9}.
 16. **ENS2** trung vị {D0B, DDM, EPV, MULT, HEDf}; **vùng** = [q25, q75] giữa các phương pháp; **độ tin cậy** = SD log V
     giữa các phương pháp.   17. **META** mỗi route chọn 1 mô hình trong {5..9} theo IC36 IS (chỉ đổi khỏi ENS2 khi hơn
     ≥ 0,03 và route có ≥ 8 mã).   18. **L2** = (Lớp 1 được chọn ở §5) × premium riêng 60 tháng (λ = 1).
Null/đối chứng (không tính là mô hình): **N0** tâm = trung vị 60 tháng giá của chính mã; **EP** = E/P TTM; **BP**; size.

## 2. Mục tiêu 1 — phát hiện ĐỊNH GIÁ THẤP
Sự kiện rẻ: tháng t0 có V/P ≥ 1,25 sau ≥ 6 tháng liền V/P < 1,25 (hoặc lần đầu quan sát); mỗi mã re-arm sau 36 tháng.
- **U-hit** (định nghĩa user, tâm trượt): ∃ s ∈ (t0, t0+36]: P_s ≥ V_s VÀ P_s > P_t0.
- **U-static**: max P trong 36T ≥ V_t0 (giá chạm mức tâm lúc phát tín hiệu — không lách được bằng tâm trượt).
- Phụ: số tháng tới lúc chạm (trung vị), lợi suất vượt trội 36T sau sự kiện, tỉ lệ "chạm do tâm rơi" (P_s ≥ V_s, P_s ≤ P_t0).
- Đối chuẩn: cùng phép đo cho N0; nền vô điều kiện P(max 36T ≥ 1,25×P₀) trên mọi (mã, tháng).
- Báo thêm tỉ lệ cắt 36T mỗi phía như vòng 1 kèm **mức vượt null N0** (skeptic 7).
**ĐẠT (1)** khi ở CẢ IS và OOS: U-hit ≥ 60% VÀ U-hit hơn N0 ≥ 5 điểm VÀ U-static hơn nền vô điều kiện ≥ 5 điểm.

## 3. Mục tiêu 2 — CẢNH BÁO ĐẮT
Sự kiện đắt: V/P ≤ 0,67 đủ 6 tháng liên tiếp (ghi tại tháng thứ 6); re-arm 36 tháng. Trong 36T sau:
- **đúng-tương đối** = lợi suất vượt trội log so universe EW < 0; **đúng-tuyệt đối** = log(P36/P0) ≤ 0,10;
- **báo sai** = lợi suất vượt trội log > +0,30 (mã tăng bền);
- **độ trễ**: số tháng tới đỉnh giá trong 36T (trung vị); số tháng tới lúc giá lần đầu thấp hơn P0 ≥ 15% (trung vị, % không bao giờ).
- Đối chuẩn: nền vô điều kiện; N0 (P ≥ 1,5× trung vị 60 tháng).
**ĐẠT (2)** khi ở CẢ IS và OOS: đúng-tương đối ≥ 60% VÀ hơn nền ≥ 5 điểm VÀ báo sai ≤ nền báo-sai VÀ ≥ N0.

## 4. Tầm nhìn, ca kiểm, mẫu
- IC hạng log(V/P) với lợi suất vượt trội 12/24/36T, lát cắt quý; **CI theo khối năm as-of, B = 2000, seed 20261124**
  (mọi mô hình) + CI cụm theo mã B = 500 (mô hình được chọn và đối chứng). IC theo từng năm so với EP; IC phần dư sau khi
  loại hạng EP, BP, size.
- 5 ca (mù giá; **không chạy được = NA**, điểm = đạt/(5 − NA)): VCS 2015, DGC 2016, VNM 2011 (≥ 50% cuối tháng trong năm
  có V > P); HPG (V 12/2019 > V 12/2018 VÀ V 06/2020 > V 06/2019 VÀ có tháng 2019 V > P; nếu đạt chỉ nhờ vốn chủ tăng thì
  nói rõ); VNM 2015-07→2016-12 (≥ 50% tháng V < P) + báo độ trễ tới đỉnh và mức giá sau 36T.
- Mẫu ngẫu nhiên 24 mã (seed 20261124, từ mọi mã từng in-universe gồm mã vắng BQ) + ca thất bại ép vào: FLC, ROS, HVG,
  KSA, AMD, HAI, ART, GTN, TGG, TTF, HNG, OGC, ITA, HBC, PVX, DLG, HAG, QBS, POM.
- Độ tin cậy ENS2: IC36 và U-hit ở tercile SD thấp phải > tercile SD cao ở cả hai era thì mới gọi "độ tin cậy có ích".

## 5. Luật chọn (chỉ dùng IS)
Lớp 1 = biến thể trong {3..11, 14..17} có IC36 IS với CI khối-năm không chứa 0 và điểm IS cao nhất, điểm =
(U-hit − U-hit N0) + (đúng-tương đối − nền); hoà (< 1 điểm) ⇒ chọn bản không fit/ít tham số hơn (ENS1 > ENS2 > D0B > khác).
Không biến thể nào có CI IC36 IS loại 0 ⇒ nói thẳng không chọn được. OOS chỉ báo. Lớp 2 = L2 trên Lớp 1 đã chọn.

## 6. Mục tiêu 4 — tạo giá trị (luật khoá trước, không tune)
Sổ 50 tỷ, tái cân bằng cuối tháng, khớp Close phiên kế (T+1), phí 0,1%/chiều, pin0%.
- **S1** vùng mua: V/P ≥ 1,25 VÀ rating 8L ≤ 3; ra khi V/P < 1,0 hoặc rating > 3; EW.
- Sức chứa: chạy S1 với sàn GTGD trung vị 1 tháng ≥ 1 tỷ và ≥ 5 tỷ/phiên; vị thế mỗi mã ≤ 20% × GTGD × 5 phiên, phần
  không mua được nằm tiền (pin0%). Benchmark universe EW cùng sàn.
- **S3f** đối chứng E/P công bằng: cùng cổng rating, cùng số mã mỗi tháng, giữ mã cũ khi còn trong top 2N theo E/P.
- **S5** sizing theo đồng thuận: trọng số 1 nếu rẻ ở cả Lớp 1 (≥ 1,25) và Lớp 2 (≥ 1,0), 0,5 nếu chỉ rẻ ở Lớp 1.
- **S7** tránh đắt: universe EW bỏ các mã đang có cảnh báo đắt, so universe EW.
- Self-check: tính lại NAV bằng đường code độc lập từ CSV danh mục, lệch 0 VND; chạy dưới `env -u TZ` và TZ lạ.
**Có giá trị** khi S1 (sàn ≥ 1 tỷ, có trần vị thế) > universe EW cùng sàn ở CẢ IS và OOS VÀ ≥ S3f ở OOS; DSR ≥ 0,95.
Nếu không ⇒ "lens, chưa phải alpha".

## 7. Kiểm kê proxy (mục tiêu 3)
IC36 đơn biến (IS/OOS, CI khối năm) cho từng proxy có lịch sử PIT theo mã: E/P, B/P, S/P, CFO/P, EBITDA/EV, DY, payout,
ROE, ROIC, ROA, biên gộp/ròng, độ ổn định ROE, tăng trưởng doanh thu/LN/vốn chủ, capex/CFO, vòng quay tiền, nợ/EBITDA,
IntCov, tiền ròng/vốn hoá, vốn hoá, GTGD, risk_rating, FSCORE, rating 8L, z-score bội số so lịch sử mã. Chuỗi thị trường
(lãi huy động, refi, VNINDEX P/E, tín dụng, tỷ giá, hàng hoá, breadth) chỉ mô tả vì N theo thời gian quá nhỏ.
Nguồn không có lịch sử PIT theo mã (moat_tags, room ngoại, route trước 2026) ⇒ không đưa vào mô hình, ghi lý do.
