# PREREG — ERP nội địa cho DCF fleet (job Taylor_20261030_034654)
Viết TRƯỚC khi chạy bất kỳ con số E/P, ERP, Ke hay FV nào. Commit trước khi chạy `erp_*.py`.
Chỉ nghiên cứu: không wire, không sửa `dcf_valuation.py` / skill due-diligence / r7, không đặt lệnh.

## 0. Đã biết trước PREREG (chỉ đọc schema, chưa tính số mới)
- Ke DGC r7 = 14,9% (rf 7,4 + 1,0×7,5). Nghiên cứu 29/10 (`dgc_discount_rate_20261029/`): rf chuẩn hoá trung tâm 6,75%
  (dải 6,0–7,5), ERP Damodaran 8,13 (= 4,23 + CRP 3,90), ERP ngầm định 5,7 (E/P VNINDEX 8,20 + π − 6,75).
- `dcf_valuation.py`: r = consumer_deposit_rate (7,4) + ERP 6,5; g_T = min(CPI5y + GDP thực 15y, rf=lãi huy động).
- Nguồn (đã tra `kb/data_registry/`): `tav2_mike.universe_pit` (CANONICAL, rổ PIT), `tav2_bq.ticker` (Price, PE, OShares,
  ROE5Y, ICB_Code, VNINDEX_PE — PE trên Price thô, PIT đúng), `data/benchmark/vnindex_tr_daily.csv` (TR có cổ tức từ
  2013-12-31, CANONICAL), `deposit_rate_vn.py` (Big-4 12M từ 2011-01, CANONICAL-PROXY, mốc neo có hindsight),
  `fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv` (NHNN TB huy động), TPCP 10Y theo năm = `../dgc_discount_rate_20261029/data/tpcp10y_annual.csv`
  (**9/16 điểm chưa kiểm chứng** — mọi số dùng nó mang nhãn đó). Lãi cho vay: KHÔNG có chuỗi trong registry ⇒ [UL]/[SRC] web.
- Mốc thời điểm: asof = **2026-10-29** (phiên cuối có cả `ticker` và `universe_pit`).

## 1. ERP ngầm định robust với vốn hoá lớn (việc 1)
Rổ: `universe_pit.in_universe` tại asof (KHÔNG ticker_prune). Với mỗi mã: mcap = Price×OShares; NP_ttm = mcap/PE
(PE âm ⇒ NP âm, giữ; PE NULL/OShares NULL ⇒ loại, báo số mã loại).
Bộ ước lượng E/P (khai trước, báo TẤT CẢ):
- E1 VNINDEX_PE chính thức → 1/PE.
- E2 aggregate = ΣNP_ttm / Σmcap (gồm mã lỗ).  E3 equal-weight mean E/P (winsor 1%/99%).  E4 median E/P.
- E5/E6 aggregate bỏ top-5 / top-10 vốn hoá.  E7 aggregate bỏ ngân hàng (ICB 8355).  E8 bỏ BĐS (ICB 8633, 8637).
- E9 bỏ cả ngân hàng + BĐS.  E10 median bỏ ngân hàng + BĐS.
Chuỗi lịch sử: E1, E2, E4, E6, E9 tại cuối mỗi quý 2014Q1→2026Q3 + asof (rổ PIT từng ngày) — chỉ mô tả độ chênh.
Đổi E/P → Ke ngầm định, HAI cách (báo cả hai):
- M-a: Ke = E/P + π (E/P xấp xỉ lợi suất THỰC khi RONIC ≈ Ke); π = 4,25 (dải 4,0–4,5) [UL].
- M-b: value-driver (McKinsey): P/E = (1 − g/ROE)(1+g)/(Ke − g) ⇒ Ke = g + (1 − g/ROE)(1+g)·E/P.
  g danh nghĩa trung tâm **5,5%** (π 4,25 + thực 1,25; tăng trưởng EPS niêm yết < GDP do pha loãng) — dải 4,25 / 6,75.
  ROE = ROE5Y (thập phân) kẹp [g+0,01; 0,40]; aggregate dùng ROE trọng số vốn chủ (mcap/PB không có ⇒ dùng trung vị ROE5Y
  của rổ tương ứng — khai: dùng TRUNG VỊ ROE5Y rổ). Mã lỗ/ROE NULL: loại khỏi M-b mã-lẻ.
ERP ngầm định = Ke − rf_c, rf_c = 6,75 (thừa kế 29/10, không bàn lại).

## 2. ERP thực nghiệm lịch sử (việc 2)
- TR: `tr_gross` 2013-12-31→asof (BQ/benchmark). Trước 2014: VNINDEX giá [BQ] + cổ tức = TB năm `y_gross` 2014–2016 đo
  trên chính chuỗi TR, dải ±1pp, nhãn [UL-ngoại suy]. Cửa sổ khởi: 2008-01-02, 2011-01-04, 2013-12-31.
- rf khớp kỳ hạn, HAI chân: (i) Big-4 12M (`deposit_rate_vn.current_deposit_rate`, cộng dồn ngày, act/365) — chỉ từ 2011;
  2008–2010 KHÔNG có chuỗi ⇒ cửa sổ 2008 chỉ báo với chân TPCP; (ii) TPCP 10Y: lợi suất TB năm (giữ-đến-hạn ≈ lợi suất
  lúc mua; KHÔNG phải TR trái phiếu) — chuỗi 2011+ có 9/16 điểm chưa kiểm chứng; 2008–2010 [UL] 9–12% nhãn rõ.
- Chia giai đoạn: 2008–2013 (khủng hoảng/kìm lạm phát), 2014–2019, 2020–2026; cửa sổ dài 2011→, 2014→.
- Báo: CAGR TR, rf TB, ERP hình học = (1+TR)/(1+rf) − 1 và số học (TB tháng ×12); ERP **bỏ tái định giá** = ERP − Δln(PE)/năm
  (PE = VNINDEX_PE đầu/cuối cửa sổ; VNINDEX_PE NULL trước 2016-07 ⇒ cửa sổ đó không bỏ tái định giá được, báo "không đo").
- Bất định: bootstrap khối dừng (stationary, khối TB 12 tháng) trên lợi suất vượt TRỘI THÁNG, 10.000 lần, seed 20261030 ⇒ CI 90% của ERP số học năm.
  N độc lập ≈ số năm (12–18), tự tương quan + chế độ ⇒ CI chỉ mô tả, không kiểm định.

## 3. Khung proxy vĩ mô (việc 3)
rf ứng viên tại asof: building-block 6,0/6,75/7,5; Big-4 12M; CCTG 12M; NHNN TB huy động mới nhất; TPCP 10Y 4,47 [SRC 29/10];
lãi cho vay (TB, [SRC] nếu tìm được, không thì [UL]). rf_c = 6,75 giữ nguyên. Kiểm: rf_c phải nằm giữa TPCP 10Y và lãi cho vay —
nằm ngoài ⇒ báo, không sửa. Ke = rf + β×ERP cho β 1,0/1,1/1,2.

## 4. Luật chọn ERP nội địa (khai trước — KHÔNG phụ thuộc FV DGC)
Ứng viên NỘI ĐỊA (đều đo so với rf_c 6,75 hoặc quy về rf_c bằng cộng/trừ chênh rf của chân đo):
- D1 = ERP ngầm định M-b, trung vị của {E2, E4, E6, E9, E10} (bỏ E1 vì là đối tượng bị nghi méo; bỏ E3 vì mean nhạy đuôi).
- D2 = ERP ngầm định M-a, trung vị cùng tập.
- D3 = ERP lịch sử hình học bỏ tái định giá, cửa sổ dài nhất đo được (2016-07→), quy về rf_c: D3 = ERP_vs_deposit + (dep_TB_cửa_sổ − 6,75).
- D4 = ERP lịch sử hình học KHÔNG bỏ tái định giá, 2014→, quy về rf_c như D3.
**ERP trung tâm = trung vị {D1, D2, D3, D4}; dải = [min, max] của bốn số.** Sàn: nếu trung tâm < 4,23 (ERP thị trường trưởng thành
Damodaran) ⇒ đặt = 4,23 và báo (ERP EM nội địa thấp hơn Mỹ không đáng tin vì σ VN cao hơn). Trần tham chiếu 8,13 (góc nhìn nước ngoài):
trung tâm > 8,13 ⇒ báo, không cắt. Damodaran KHÔNG vào trung vị.
CRP: phần rủi ro VN thật sự còn lại với NĐT nội (biến động cao hơn, quản trị, thanh khoản) đã có trong ERP đo ở VN; rủi ro
chuyển đổi/ lạm phát vĩ mô đã nằm trong rf VND. Không cộng CRP vào Ke nội địa; rủi ro đặc thù (pháp lý, chính sách) đưa vào
**dòng tiền/kịch bản/g**, không vào Ke.

## 5. Phép thử "justify" (việc 4)
Mỗi mã rổ asof có PE>0 và ROE5Y hợp lệ: PE hàm ý(Ke) = (1 − g/ROE)(1+g)/(Ke − g), g = 5,5% (độ nhạy 4,25/6,75); "đắt" nếu PE thực > PE hàm ý.
Báo trên lưới Ke 9%→17% bước 0,5: % mã đắt (đếm), % vốn hoá đắt, % mã đắt > 1,5× hàm ý ("đắt vô lý"). Ke* = mức làm 50% số mã đắt
(= trung vị ICC). Mã lỗ báo riêng (không xếp). Ngân hàng tách bảng phụ (ROE ngân hàng không cùng loại vốn).
Ghi rõ tính vòng tròn: ICC giả định giá thị trường đúng ⇒ chỉ HIỆU CHỈNH vùng Ke, không kết luận thị trường rẻ/đắt.

## 6. DGC + consumer (việc 5)
Tái lập TRƯỚC: r7 tầng A DCF 21.407 / 32.925 / 41.779 ở Ke 14,9% (lệch 0 đồng; dùng lại cơ chế `model_ke.py` của 29/10, không sửa r7).
Sau đó Ke = 6,75 + β×ERP cho (ERP thấp/trung tâm/cao) × β (1,0; 1,1; 1,2) + β DGC 1,11. g giữ 3% của r7.
Liệt kê consumer của `dcf_valuation.ERP`/`discount_rate`/`terminal_growth_mode` bằng grep (không sửa).

## 7. Kỷ luật
Nhãn mọi số [SRC]/[BQ]/[UL]. Dữ liệu BQ kéo một lần vào `data/*.csv` (cache bất biến) rồi tính offline; chạy dưới TZ=UTC và
TZ=Pacific/Kiritimati ⇒ md5 out_*.csv trùng byte (SELFCHECK.md). Không kiểm định p-value; N độc lập nhỏ.
