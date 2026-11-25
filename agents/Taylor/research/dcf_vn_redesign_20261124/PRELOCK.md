# PRELOCK — DCF phù hợp thị trường VN (job Taylor_20261124_140534)
Khoá lúc 2026-11-24 ~21:35 ICT, TRƯỚC khi chạy bất kỳ mô hình nào. Tới lúc này mới chỉ xem schema, dải ngày,
vài dòng thô (HPG/VNM/VCS) để hiểu đơn vị cột; chưa tính V/P của họ mô hình nào. Không đổi tiêu chí sau khi thấy số;
mọi sai lệch so với file này ghi ở REPORT §"Lệch prelock".

## 0. Dữ liệu & khung PIT
- BCTC: `ticker_financial` (cache local), known_date = cột `time` (= ngày công bố/ngày vendor nạp). Chạy lại bản
  bảo thủ +1 quý trễ cho mô hình được chọn.
- KHÔNG dùng `OShares` (TRAP restate), KHÔNG dùng `PB`/`PE` vendor (phụ thuộc OShares). Làm việc trong KHÔNG GIAN TỈ SỐ:
  B/P = BVPS/Price tại ngày công bố; giữa hai kỳ công bố: B/P(d) = B/P(rel) × Close(rel)/Close(d) (Close đã điều chỉnh,
  không nhân thêm hệ số nào ⇒ không double-count). ROE = `ROE_Trailing` (không đơn vị). Payout = Dividend_1Y/(ROE×BVPS).
- Tâm theo đơn vị giá điều chỉnh: V_adj(d) = (V/P)(rel) × Close(rel). Giá = Close(d). Lưới tháng (phiên cuối tháng).
- Universe: `universe_pit.in_universe` đúng phiên (2013+). Trước 2013 chỉ dùng cho 4 ca kiểm (không có universe PIT).
- Nhãn: lợi suất tương lai từ Close (tổng lợi suất). KHÔNG dùng profit_*. Benchmark: universe_pit EW cùng kỳ + VNINDEX.
- Lãi suất: `deposit_rate_vn.DEPOSIT_EVENTS` (2011+; neo hồi tố — khai là hạn chế), trước 2011 = refi SBV + 1,0đ.
- Ngành: route 8L (không có vintage trước 2026 — hạn chế đã biết).

## 1. Họ mô hình (khai trước, N trials)
A  FCFE production (`dcf_valuation.fair_value`, domestic_v2) — đối chứng; chỉ phi tài chính.
B  RIM-naive: ROE = TTM giữ nguyên 10 năm (không chuẩn hoá, không fade).
C  RIM-tc: ROE xuyên chu kỳ = trung vị ROE TTM 5 năm của chính mã; không shrink ngành; không fade.
D0 RIM-tc + fade (κ=0,4) ; không shrink ngành.
D  RIM-VN đầy đủ: ROE_tc 5 năm → shrink Bayes về trung vị ROE_tc của ngành (w = n/(n+8)) → pha 1 (3 năm) ROE đi
   tuyến tính từ TTM về ROE chuẩn hoá → pha 2 (năm 4–10) fade về ROE_LR = r + κ(ROE_n − r), κ=0,4 → terminal RI
   tăng g_T. Tăng trưởng vốn chủ g_t = min(ROE_t × tỉ lệ giữ lại, 15%), fade tuyến tính về g_T tại năm 10.
E  Neo bội số lịch sử của chính mã: V = trung vị P/B 5 năm × B (CÓ dùng giá quá khứ — gắn nhãn "price-informed").
F  Blend D ⊕ E (trung bình hình học).
× r ∈ {R_fix 12,25% ; R_adp = huy động 12T tại as-of + 5,5đ ; R_slow = TB 5 năm huy động 12T + 5,5đ}; g_T = min(5,5%, r−4đ).
⇒ 6×3 + 1 = **19 biến thể chính**. Độ nhạy trên D (khai trước, 8 lần chạy): κ∈{0;0,7}, cửa sổ ROE {3;7 năm},
phụ phí thanh khoản +1đ cho mã dưới trung vị GTGD universe, r 13,5%, bỏ pha 1, lag +1 quý. **N trials tổng = 27.**
Tham số D là prior chuyên gia (không fit theo giá). Chọn mô hình: xem §4.

## 2. Tiêu chí (1) — CẮT GIÁ trong 36 tháng (tâm trượt)
Đơn vị: (mã, tháng as-of t0) trong universe_pit có đủ 36 tháng phía sau. "Cắt" = tồn tại tháng s∈(t0, t0+36] mà
sign(log V_s/P_s) ≠ sign(log V_t0/P_t0) (tâm cập nhật theo quý, giá theo tháng). Báo: tỉ lệ chung, riêng phía đắt (V<P),
riêng phía rẻ (V>P), và % mã (≥60 tháng trong universe) KHÔNG cắt lần nào trong toàn mẫu.
**ĐẠT (1)** khi cả IS và OOS: cắt36 chung ≥ 75% VÀ mỗi phía ≥ 60% VÀ mã không-bao-giờ-cắt ≤ 10%.
Chống lách: mô hình mù giá (B,C,D0,D) là ứng viên chính; E/F báo riêng. Báo thêm corr(Δlog V, Δlog P) theo quý và
SD(Δlog V)/SD(Δlog P) — tâm "bám giá" thì cắt nhiều nhưng không có nghĩa.

## 3. Tiêu chí (2) — TẦM NHÌN
(2a) IC hạng cắt ngang của log(V/P) với lợi suất vượt trội 12/24/36 tháng (so universe EW), trung bình theo as-of quý;
     CI bootstrap cụm theo mã và theo năm as-of (B=2000, seed 20261124). N độc lập khai = số mã (cụm) và số khối
     thời gian không chồng lấn (36T: IS 2 khối, OOS ≤2 khối ⇒ sức mạnh theo thời gian YẾU, nói thẳng).
(2b) Hội tụ: β của log(P36/P0) − thị trường theo log(V/P0); gap ratio median|log(P36/V0)| / median|log(P0/V0)|.
(2c) Sự kiện: "cắt lên" = tháng đầu V/P ≥ 1,0 sau ≥6 tháng liên tục < 1,0; "cắt xuống" = ngược lại. Mỗi mã re-arm sau
     36 tháng. Đo lợi suất vượt trội 12/24/36T sau sự kiện; N = số sự kiện. Kỳ vọng: sau cắt lên > 0 > sau cắt xuống.
(2d) 4 ca user (định nghĩa ĐẠT khoá trước, PIT, mô hình mù giá):
     VCS: ≥50% phiên cuối tháng năm 2015 có V>P.            DGC: ≥50% phiên cuối tháng năm 2016 có V>P.
     VNM-a: ≥50% cuối tháng 2011 có V>P.                    VNM-b: ≥50% cuối tháng 2015-07→2016-12 có V<P.
     HPG: V_adj(2019-12) > V_adj(2018-12) VÀ V_adj(2020-06) > V_adj(2019-06) VÀ có ≥1 cuối tháng 2019 với V>P.
     Điểm = số điều kiện đạt /5.
**ĐẠT (2)** khi mô hình mù giá được chọn có: IC36 > 0 với CI95 cụm-mã không chứa 0 ở CẢ IS và OOS; sự kiện cắt lên −
cắt xuống (36T) > 0 ở cả IS và OOS; 4 ca ≥ 4/5.
Chống panel-curation: toàn universe_pit; mẫu ngẫu nhiên 24 mã (3 mã/route × 8 route nếu đủ, seed 20261124, từ mọi mã
từng in_universe) + danh sách ca THẤT BẠI ép vào, khai trước: FLC, ROS, HVG, TTF, HNG, OGC, ITA, HBC, PVX, DLG, HAG, KSA
(mã nào có dữ liệu thì báo, kể cả khi mô hình sai).

## 4. Luật chọn mô hình
Trên IS (as-of 2014-01→2019-12): trong các biến thể MÙ GIÁ đạt ngưỡng (1), chọn IC36 cao nhất; hoà (chênh < 0,01) ⇒
chọn biến thể ít tham số hơn. Không biến thể nào đạt (1) ⇒ chọn theo cắt36 phía-yếu-nhất cao nhất và NÓI THẲNG là không
đạt. OOS (2020-01→) chỉ báo, không chọn lại. DSR tính cho backtest §5 với N=27.

## 5. Tiêu chí (4) — tạo giá trị (luật khoá trước, không tune)
Danh mục lịch-thời-gian, tái cân bằng cuối tháng, vào/ra tại Close phiên kế tiếp (T+1), EW, phí 0,1%/chiều theo turnover:
 S1 "vùng mua": giữ mã có V/P ≥ 1,25 (giá ≤ 0,8×tâm) VÀ rating 8L ≤ 3 (PIT); ra khi V/P < 1,0 hoặc rating > 3.
 S2 = S1 không cổng rating.   S3 đối chứng: cùng số mã như S1 nhưng chọn theo E/P TTM cao nhất (kiểm "chỉ là 1/PE?").
 S4: quintile cao nhất V/P.   Benchmark: universe EW, VNINDEX (giá).
Báo CAGR/Sharpe/MaxDD/vượt trội theo năm, IS vs OOS, theo DT5G lúc lập, leave-one-year-out, DSR (N=27), IC phần dư
⟂ {E/P, B/P}. Tiền nhàn rỗi 0% (pin0%) khi S1 rỗng. Self-check: tính lại NAV độc lập từ CSV danh mục, lệch 0.
Mã rời sàn: giữ giá cuối; độ nhạy −50%.
**Có giá trị** khi S1 vượt universe EW ở CẢ IS và OOS (CAGR) và S1 ≥ S3 ở OOS; nếu không ⇒ nói thẳng "lens, không alpha".
