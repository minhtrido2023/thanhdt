# DD — NNC (CTCP Đá Núi Nhỏ) · r3 · as-of 03/11/2026 · job `Taylor_20261103_130007`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. Bản trước (30–31/10, v1/v2 + bổ sung 03/11) lưu ở
> `archive_internal/REPORT_v2_20261031.md` — mọi số BCTC/nguồn trang ở đó vẫn là gốc tham chiếu cho bản này.
> **Nguyên tắc user 03/11 17:06** (skill due-diligence "ĐẦU TƯ DỰ ÁN MỚI", dd-investor-report luật 18–20): dự án mới base = sổ sách/NPV 0;
> lệch chỉ khi có cơ sở độc lập; áp ĐỐI XỨNG khoản cộng lẫn khoản trừ; mọi khoản giảm trừ trong base có dòng "cơ sở dữ liệu".
> **Mù giá — trung thực:** mô hình r3 không đọc giá/vốn hoá/P-E NNC hay MVC; khoá md5 `r3/calc/LOCK_md5_r3.txt` 20:04:30 ICT, so giá sau
> (`r3/calc/compare_r3.py`). NHƯNG v1/v2 (30–31/10) đã biết giá 47.100 và tài liệu MVC skeptic có số ~48k ⇒ khoá chỉ chứng minh THỨ TỰ CHẠY.
> Tham số kế thừa từ v2 (K 0,97, giá kịch bản 2027, W 25/50/20/5) được dựng khi đã biết giá.

## 0. Kết luận

**Tâm (kỳ vọng W 25/50/20/5 × đường giá g2031/thực 50:50, r13%) = 90.742 đ/cp; base cơ sở 96.433; trung vị lưới 729 = 78.070.**
Lưới (thang ĐĂNG KÝ TRƯỚC trong docstring `r3/calc/model_r3.py`): P10 **61.195** · P25 **68.069** · P50 78.070 · P75 **89.171** · P90 **99.160** (min 51.608, max 122.584).
Thang: RẺ ≤61.200 · RẺ CÓ ĐIỀU KIỆN 61.200–68.100 · HỢP LÝ 68.100–89.200 · NGHIÊNG ĐẮT 89.200–99.200 · ĐẮT ≥99.200.

**So giá (sau khoá): đóng cửa 03/11/2026 = 46.100** (DNSE `dnse_close_prices`, khớp BQ `ticker.Price` 03/11) ⇒ **RẺ (dưới P10); 0/729 bộ dưới giá.**
**Biên an toàn CÓ ĐIỀU KIỆN**: tâm = giá khi giá đá cụm từ 2028 ≤ ~217k/m³ (tiền 2026) ⇒ GPM đá mô hình ~28% (đỉnh 2026 ~59%; GPM NNC TB 2012–25 34%).
Kiểm chéo ngược chiều phải nêu: Gordon P/B (r13, g3, BVPS 29.915): ROE 12% → 26.923; ROE TB 2021–25 (giai đoạn một mỏ) 16,1% → 39.231; 20% → 50.856.
Giá 46.100 hàm ý ROE bền 18,4%; tâm hàm ý 33,3% (= TB 2012–25 33,8%, thời 2 mỏ). ⇒ "rẻ" đứng trên giả định biên KHÔNG quay về mặt bằng 2021–24.
Chu kỳ ở đỉnh: GPM NNC Q3/26 TTM 53% = cao nhất 15 năm; KSB 33% (dưới TB), DHA 37%, VLB 34% — đỉnh là của riêng NNC/cụm Đồng Phú.

| 3 kịch bản (NĐT, 25/50/25) | g2031 | thực |
|---|---|---|
| Tích cực (tot 25%) | 125.449 | 144.741 |
| Cơ sở (50%) | 88.891 | 103.975 |
| Tiêu cực (xau 20 + rat_xau 5) | 31.989 | 38.024 |

Stress (ngoài tâm): biên cụm về TB chu kỳ (giá 270k) 63.930 · GPM đá 36% trên chi phí mô hình (trần 242k, NGOÀI lưới) 55.175 · giá danh nghĩa phẳng 72.697.
Định giá ngược: ở 46.100 thị trường hàm ý P(tiêu cực) ≈85% (mô hình 25%).

## 1. Kiểm kê khoản cộng/trừ gắn dự án mới & giả định (hiệu ứng = đưa khoản đó vào/bỏ ra khỏi tâm r3, đ/cp NNC; số: `r3/calc/model_r3_out.txt` mục "Kiem ke")

| Khoản | Hiệu ứng | Cơ sở dữ liệu độc lập (nguồn) | Xử lý r3 |
|---|---|---|---|
| CIP Tam Lập 1 khu II 83,5 tỷ chỉ ở tốt/cơ sở (v2: xấu/rất xấu = 0) | −998 nếu giữ | KHÔNG (không có tín hiệu huỷ dự án) | **Sổ sách mọi kịch bản** |
| Chi phí trễ GP Tam Lập 1 khu II (P trễ 0/1/2 năm = 0,30/0,40/0,30) | −443 (giữ) | CÓ: Bobby F6 P(GP mỏ đấu giá trước 06/2027)=0,30; đối xứng với mỏ mới MVC r6 | Trong base (chi phí kỳ vọng 9,3 tỷ) |
| Upside Tam Lập 1 khu II (sản lượng thêm) | không định lượng | KHÔNG: chưa có GP/trữ lượng/công suất/capex công bố (AWM thứ cấp) | 0 ở base, chỉ định tính |
| Dự phòng truy thu CQ 15,58 + thuê đất 2019 Núi Nhỏ 5,95 + CQ Mũi Tàu 0,84 | −1.021 (giữ) | CÓ: BCTC Q3 V19a | Trừ ở tiền ròng |
| Đối xứng BCĐKT: ký quỹ PHMT 4,57 + thuế hoãn lại 4,31 (v2 trừ dự phòng nhưng không cộng tài sản đối ứng) | +424 | CÓ: BCTC Q3 V9 / tr.2 | **Cộng vào base** |
| Trả trước dài hạn CN Bình Phước 59,2 (phân bổ 3,2/quý, phi tiền mặt trong chi phí hiệu chỉnh) | +2.146 nếu cộng | CHƯA XÁC MINH bản chất (có thể là tiền thuê đất đã trả trước) | Độ nhạy |
| Máy nghiền 350 t/h (CIP 24,5; mua từ NHC) | +1.171 nếu cộng | Thay thế/duy trì năng lực ⇒ nằm trong dòng tiền DCF | Độ nhạy; giao dịch NHC = WARNING |
| Vách giá cơ sở 380→300 (2028–30), nhãn FPTS "cung mới" | −2.740 nếu giữ | Chiều: CÓ (cung mới cụm định lượng được: mỏ MVC ~2,1 tr m³ TP/năm + Tam Lập 1 khu II); độ lớn: KHÔNG | Trượt 360/340/320; vách = độ nhạy |
| Mốc giá 320 từ 2031 + trục stress biên | — | CÓ: GPM NNC 2012–25 TB 34,1% vs 53,3% (BQ `ticker_financial`, `r3/calc/sector_gpm_roe.csv`) | Base 320; lưới stress 0/0,5/1 |
| Cắt sản lượng co_so 1,10 (2028–30)/1,20 (2031+) | −6.874 nếu giữ | KHÔNG về độ lớn (FPTS base 0,8 không nêu lý do) | **Base 1,40** (= 2026; GP 1,42 tr m³ TP [BCTN25 tr.6]; 2025 100% công suất [tr.20]) |
| Trọng số kịch bản 25/50/20/5 | (v2 20/45/25/10: −8.710) | CÓ: Bobby F2 P(giá Q2/27 >+7%)=0,30, <−7%=0,15 | Giữ; lưới 3 bộ |
| Đường giá phẳng danh nghĩa trong tâm (10/50/40) | −2.498 nếu giữ | KHÔNG: 2012–25 không mã đá ĐNB nào đi theo (SKEPTIC2 C) | Chỉ stress (72.697) |
| Cổ phần MVC theo thị giá × (1−15% thanh khoản) − vòng chéo bằng giá NNC (v2) | v2 ~3.814 đ/cp vs r3 ~11.400 | D1: không dùng thị giá trong định giá NNC | **Giải hệ nhất quán** V_N = N_ex + 0,103·V_M; V_M = D_M + 0,4407·V_N |
| Holding MVC→NNC 15% | −643 | KHÔNG về độ lớn | 0 ở base; độ nhạy |
| NHC thị giá 13,2 → sổ sách 14,1 | +41 | Không dùng thị giá (kém thanh khoản) | Sổ sách |
| Mở rộng công suất (dây chuyền 1.000 t/h, đá 1x1, cát nghiền) | 0 | KHÔNG có IRR | NPV 0 (không capex, không lãi) |
| LN gộp cho thuê Núi Nhỏ 11,13 tỷ/năm tới 2043 | +3.500 (giữ) | CÓ: KT25 7.1–7.2 | Base |
| Chi phí K 0,97 (GV kiểm toán 2024–25) | ±6,6–6,7k (±10%) | CÓ: KT25 7.2 | Base; lưới |
| r 13% | −7,0k/+8,4k (15/11%) | Khung user (Ke nội địa) | Base; lưới |

## 2. Mô hình (`r3/calc/model_r3.py`, tái dùng MVC r6 KHÔNG SỬA — md5 khớp LOCK_md5_r6)
- Cầu nối cơ sở (tỷ; g2031 / thực): DCF Mũi Tàu 2027–43 gồm cho thuê 1.336,4 / 1.629,6 · Q4/26 60 · tiền ròng sau nghĩa vụ 223,6 · ký quỹ 4,6 + thuế hoãn lại 4,3
  · NHC sổ sách 14,1 · CIP Tam Lập 83,5 − trễ 9,3 · **10,3% MVC (nội tại, giải đồng thời) 231,2 / 268,7** ⇒ 88.891 / 103.975 đ/cp.
- Lưới 729: r 11/13/15 × K 0,87/0,97/1,07 × W 3 bộ × PW g2031:thực 70:30/50:50/30:70 × stress 0/0,5/1 × hạn GP Tân Lập (MVC) 2035/W/2045.
  Theo stress: 0 → P50 92.322; 0,5 → 78.594; 1 → 65.405.
- Ghi chú stress: P_CYC r6 (270k) quy tỷ lệ GPM toàn công ty; trên chi phí đá của mô hình (155k/m³) mức tương đương GPM đá 36% là 242k ⇒ stress 1,0 của lưới là NHẸ hơn
  "về TB chu kỳ" theo nghĩa chặt; số 55.175 báo riêng, KHÔNG đưa vào lưới (ngưỡng đã đăng ký trước).

## 3. V_NNC cho MVC (KHÔNG dựng lại MVC — Mike làm)

| Nguồn V_NNC cũ | V_NNC cũ | V_NNC r3 | Δ NNC | Hệ quả MVC (độ dốc 966 đ/cp MVC / 10k NNC, MVC r6) |
|---|---|---|---|---|
| NNC-DD công bố (r3 MVC, 77.656) | 77.656 | **90.742** | +13.086 | **+1.264 đ/cp MVC** |
| V_NNC nhất quán trong MVC r6 | 83.887 | **90.742** | +6.855 | **+662 đ/cp MVC** (so tâm MVC r6 23.093) |

Đối chiếu: giải đồng thời trong hệ r3 cho MVC 23.755 (≈ 23.093 + 662) — CHỈ là kiểm nhất quán, không phải số MVC mới.
Nguồn Δ: chủ yếu sản lượng co_so 1,40 (+6.874) và đối xứng BCĐKT (+424); trễ GP Tam Lập (−443).

## 4. Điều kiện đổi nhận định (hai chiều; mốc khoá 03/11/2026)
- **Tiêu cực hơn:** biên gộp quý < 45% khi DT đi ngang (≤28% ⇒ giá trị ≈ giá); giá công bố Sở XD Q2/27 thấp hơn Q3/26 >7%; GP mỏ đấu giá trong cụm cấp sớm (trước 06/2027);
  truy thu/xử phạt mới >20 tỷ; MVC ≥51% kèm thoái MVC dưới giá trị; ĐHĐCĐ 2027 dồn tiền vào BĐS; thêm dòng tiền lớn với NHC.
- **Tích cực hơn:** biên ≥55% ở Q4/26 + Q1/27; giá công bố Q2/27 cao hơn >7%; VĐ4 ≥20% khối lượng tới 30/06/2027; GP Tam Lập 1 khu II kèm trữ lượng/công suất công bố
  (khi đó mới định lượng upside); công bố sản lượng m³; cổ tức tiền cao hơn.
- Mốc: BCTC Q4/26 ~20/01/2027 · Q1/27 ~20/04/2027 · VĐ4 & GP mỏ cụm 30/06/2027 · giá Sở XD Q2/27 (kiểm 31/08/2027).

## 5. Sản phẩm & kiểm
- Báo cáo NĐT: `investor_report_v3/NNC_DD_investor_report_20261103.{md,pdf,html}` — 10 trang; thân ~1.090 từ (bỏ bảng/tiêu đề/phụ lục); grep luật 18 + luật 4/12 rỗng
  trên md + subject; dry-run email (`--html-out`): 16 ảnh, 9,4 MB, 16/16 `<img>` alt đóng; **KHÔNG gửi**. Hình 01–10, 18–22 chép từ bộ 31/10 (số BCTC không đổi);
  hình định giá 00/11/12/13/14/23 dựng mới từ `r3/calc/model_r3_out.json`. Chi tiết `investor_report_v3/SELFCHECK.md`.
- ADV trung vị (BQ Price×Volume): 20/60/120 phiên 1,43 / 1,38 / 1,39 tỷ. r* thị trường 15,1% (panel 30/10); TPCP 10Y 4,58% (`dcf_rate_display`).
- fundamental-skeptic: **CHƯA CHẠY** trên r3.

## 6. Giới hạn
Không có sản lượng m³ công bố; đường giá 2028+ và xác suất là nhận định; trữ lượng còn lại và dữ liệu mỏ cạnh tranh thứ cấp; tham số kế thừa dựng khi đã biết giá;
Gordon chỉ đối chiếu thô (mỏ hữu hạn 2043, ~1/3 vốn chủ là tiền/đầu tư); giá trị 10,3% MVC phụ thuộc mô hình MVC r6 chưa qua skeptic
(theo thị giá MVC 03/11 thì phần này thấp hơn ~5.200 đ/cp NNC).
