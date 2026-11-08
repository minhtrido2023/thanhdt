# DGC — DD redo vòng 3 (08/11/2026, job Taylor_20261108_164329)

**Kết luận:** tâm **41.522 đ/cp** (sau CK 5 tỷ), P10/P50/P90 kết cục **32.931 / 41.087 / 49.929**; giá đóng cửa 06/11 **33.000** (BQ) ⇒ **TRONG vùng, rất mỏng** — giá chỉ trên P10 **+0,2%**, **10,2%** trọng số kết cục nằm dưới giá. So r2: tâm 44.767 → 41.522 (**−7,2%**), P90 57.101 → 49.929, P10 32.518 → 32.931.

**Nhãn phụ thuộc gần hoàn toàn vào trục mở lại khai trường 25** (đính chính #4): base r3 đặt w=0; chỉ cần w ≥ 0,10 là **DƯỚI vùng**. Các biến thể song song lật nhãn sang DƯỚI: lá chắn thuế dự phòng 20%, RONIC 20%. Biến thể kéo xuống (vẫn TRONG): nền biên r4, trục pháp lý.

Không đặt lệnh, không sửa `kb/dd_price_zones.json`, không email/PDF.

## 1. Kiểm từng đính chính (calc `calc/model_r3.py`; số đơn lẻ = áp riêng từng điểm lên r2, sau CK)

| # | Skeptic | r3 đo | Kết luận |
|---|---|---|---|
| 1 Đếm đôi dự phòng trên nền r4 | +1.612 | +2.022 | **ĐÚNG về bản chất.** Giá vốn nền r4 2027/28 cao hơn R2 **281/305 tỷ/năm** (`r9_calc.py` + `out_A_forecast.csv`). r3 bỏ chồng lấn ở MỌI quý dự phòng từ 2027 (cả nhánh hữu hạn 4 quý), không chỉ nhánh vĩnh viễn ⇒ số lớn hơn. Ở headline vấn đề tự biến mất vì base chuyển sang R2 (không chứa dự phòng). |
| 2 Trọng số 0,3/0,5/0,2 | +653 | +649 | **ĐÚNG.** r12 REPORT tự ghi "chủ quan"; biên độ quanh cơ sở gần đối xứng ⇒ 0,25/0,5/0,25. |
| 3 RONIC 20% > Ke | −1.760 | −2.046 | **ĐÚNG.** moat_durable=false (ADDENDUM_5F_r2 §2) ⇒ RONIC=Ke. Số lớn hơn vì reinv áp cả 2027–28 tường minh (cấu trúc model_r2). |
| 4 Trọng số mở lại khai trường 0,5 [UL] | dòng độ nhạy | w=0 ⇒ −6.813 | **ĐÚNG; r3 đi xa hơn: base w=0.** Lý do: Q3/26 chạy 100% quặng mua ngoài (hiện trạng quan sát được); không có văn bản/tin mở lại (WebSearch 08/11); mở lại = khôi phục chính cơ chế hào, hào không bền ⇒ không cộng. w=0,10/0,25/0,50 ở §3. |
| 5 Nền biên r4 thiếu cơ sở | R2 +3.041 (độ nhạy) | +4.791 | **ĐÚNG; R2 có dòng cơ sở ⇒ lên BASE.** Cơ sở: GPM Q3/26 thực tế khi dùng quặng mua ngoài **20,5%** (gồm dự phòng) / **24,6%** (bỏ dự phòng), 9T 20,7%/23,6% (BCTC HN Q3/2026); trung vị 4 peer **19,47%** (luật 3c: hào không bền ⇒ biên về TB ngành). R2 19,5/20,7% ≤ thực tế 2026 ⇒ không lạc quan. Số r3 lớn hơn skeptic vì gồm luôn việc hết chồng lấn (#1). |
| 6 Lá chắn thuế dự phòng = 0 | +378 | +570 (20%) | **ĐÚNG là độ nhạy**; base giữ 0 (khấu trừ khi chi thật chưa xác minh chứng từ). |
| 7 "LN 9T là đáy" | — | — | **ĐÚNG, sửa chữ:** EBIT 2027 cơ sở R2 **1.289** < EBIT 9T năm hoá **1.405** (gồm dự phòng) / **1.672** (bỏ dự phòng). Mô hình giả định biên về TB ngành, THẤP hơn 9T — 9T không phải đáy trong mô hình. |
| 8 HTM 9.531 | đối chiếu PDF | — | **Chưa kiểm PDF gốc.** Bản trích cộng khớp nội bộ: 2.991,4+3.241,0+2.017,5+401,3+786,6 = 9.437,8 + dự thu 93,2 = 9.531,0. |
| 9 Kỷ luật vị thế | WARNING | — | Ghi WARNING (§5). |

Tái lập r2 bằng code r3: **45.087,86 = model_r2_out.json** (assert khớp tuyệt đối).

## 2. Cầu nối r2 → r3 (trước CK, cộng dồn; CK 5 tỷ 0,725% ở cuối)

| Bước | Tâm trước CK | Δ |
|---|---|---|
| r2 tái lập | 45.088 | |
| c1 bỏ chồng lấn dự phòng (trên r4) | 47.124 | +2.037 |
| c2 trọng số 0,25/0,5/0,25 | 47.778 | +653 |
| c3 RONIC = Ke | 45.661 | −2.116 |
| c5 nền biên R2 (thay r4+fix) | 48.101 | +2.440 |
| c4 mở lại khai trường w 0,5 → 0 | **41.825** | **−6.276** |
| CK 0,725% (ADV250 đến 06/11) | **41.522** | |

Nguyên nhân chính: **c4 (bỏ trọng số mở lại khai trường)**; các đính chính còn lại gần bù trừ nhau (+2.970 ròng).

## 3. Headline vs biến thể (sau CK, giá 33.000)

| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **HEADLINE** (R2, RONIC=Ke, w mở lại 0) | **41.522** | **32.931** | **41.087** | **49.929** | **10,2%** | **TRONG** |
| mở lại w=0,10 | 42.768 | 33.267 | 42.100 | 53.030 | 9,2% | DƯỚI |
| mở lại w=0,25 | 44.637 | 33.983 | 44.163 | 56.573 | 7,7% | DƯỚI |
| mở lại w=0,50 (như r2) | 47.753 | 35.794 | 47.722 | 59.765 | 5,1% | DƯỚI |
| nền r4 + bỏ chồng lấn (#1 nguyên bản) | 39.100 | 32.655 | 38.971 | 46.167 | 11,9% | TRONG |
| nền r4 không sửa (đối chiếu) | 37.078 | 28.946 | 36.838 | 44.601 | 25,2% | TRONG |
| lá chắn thuế dự phòng 20% | 42.092 | 34.075 | 41.600 | 50.226 | 6,3% | DƯỚI |
| RONIC 20% (trái 3c) | 43.456 | 34.432 | 42.969 | 52.434 | 6,3% | DƯỚI |
| trọng số kịch bản r2 | 40.867 | 32.486 | 40.474 | 49.003 | 11,7% | TRONG |
| CÓ trục pháp lý (haircut tiền ròng) | 38.592 | 29.596 | 38.455 | 47.657 | 21,9% | TRONG |

r ±50/100bp: 42.221/42.990 (−) · 40.848/40.234 (+).

**Ba con số tách bạch:** tâm 41.522 (kỳ vọng lưới) · P50 41.087 · tham số trung tâm 43.410 (dự phòng hữu hạn 4 quý). Tâm < tham số trung tâm vì nhánh dự phòng vĩnh viễn (−7.696 đ/cp, w 1/3). P10 do nhánh xấu × dự phòng vĩnh viễn quyết định. n=405 kết cục, min 25.782, max 59.113.

**Giá ngụ ý 33.000:** để TÂM = giá cần EBIT lõi ≈ **0,61×** cơ sở mãi mãi (đã ở nền R2, khai trường dừng), hoặc kịch bản xấu chắc chắn + dự phòng vĩnh viễn chắc chắn (30.215). Riêng dự phòng vĩnh viễn chắc chắn: 36.718; riêng kịch bản xấu chắc chắn: 35.005.

## 4. Giả định khoá (đủ ở `SUMMARY.json.assumptions`)
Nền biên R2 19,5/20,7% (cơ sở BCTC Q3/26 + peer) · kịch bản 0,25/0,5/0,25 [UL] · RONIC=Ke · khai trường dừng ở base · dự phòng 100 tỷ/quý một lần/4 quý/vĩnh viễn 1/3 [UL], lá chắn 0 [UL] · Nghi Sơn sổ sách 1.408,8, trục ±500 (0,25/0,5/0,25 [UL]) · r = 13,5% + 1,0×(7,40% − 7,40%) = **13,5%** (CCTG 12T Big4 online 6,8% → hiệu dụng 7,40%, mốc 02/11, không đổi đến 06/11) ±50bp · g 3%, thuế dài hạn 15% [UL] · hệ số EBIT 0,8–1,2 · pháp lý ngoài base.
Tiền ròng/nghĩa vụ giữ như r2: tiền+HTM 9.761,2 − vay 1.391,0 − dự phòng 200 − quỹ KTPL 592,8 (BCTC HN Q3/2026).

## 5. Thanh khoản
ADV250 (05/11/25–06/11/26) 83,8 tỷ, σ 2,97%: CK 5 tỷ **0,725%** (Q/ADV 6,0%, trong vùng hiệu chỉnh) · ADV60 17,7 tỷ: CK 5 tỷ 1,13% (Q/ADV 28%, NGOÀI vùng). Sleeve thật 10/20/40 triệu: CK 0,03/0,05/0,07% (ADV250), 0,05/0,07/0,10% (ADV60). HOSE hạn chế giao dịch (chỉ phiên chiều) ⇒ ADV60 thấp hơn hẳn ADV250.

## 6. WARNING pháp lý/quản trị (mang đủ từ r2) + quét mới
- Vụ án môi trường/khai thác/kế toán: CT HĐQT cũ Đào Hữu Huyền (18,38%) tạm giam 17/03/2026; khởi tố thêm TGĐ, TV HĐQT, PTGĐ, GĐ mỏ KT25 (07/2026). Chưa thấy quyết định khởi tố pháp nhân.
- **Quét WebSearch 08/11/2026:** không thấy tin truy tố/xử phạt pháp nhân DGC mới sau 05/11; không có tin mở lại khai trường 25. Vụ Lilama (cáo trạng VKS Lào Cai) liên quan công ty con DGC Lào Cai mua quặng — đã biết.
- Ý kiến ngoại trừ BCTC kiểm toán 2025 (950,9 tỷ tồn kho); HOSE hạn chế giao dịch từ 26/05/2026; cắt margin.
- Dự phòng môi trường 200 tỷ: lặp hay không chưa phân định.
- **Vị thế ZaloPay 10.000 cp, giá vốn 39.775 ≈ 35% NAV** (số của skeptic; chưa đối soát broker trong phiên này) — **vượt xa trần sleeve 2–4% NAV**. §2.5: **NON** (P/B mẹ ≈0,96 đạt; trụ #2 nhà nước chi phối trượt — DN tư nhân).

## 7. Mốc đổi nhận định (hai chiều) + HARD ABANDON
- **Lên (DƯỚI vùng):** văn bản cơ quan có thẩm quyền cho khai trường 25 hoạt động lại / lộ trình cụ thể (w ≥ 0,10 đủ lật) · dự phòng môi trường Q4/26 = 0 · GPM quý ≥ 22% không dự phòng 2 quý liền.
- **Xuống (TRÊN/sát tâm thấp hơn):** dự phòng tiếp tục ≥ 100 tỷ Q4/26 (nghiêng nhánh vĩnh viễn) · GPM quý < 17% (về nền r4) · khởi tố pháp nhân hoặc phạt/truy thu định lượng được.
- **HARD ABANDON:** khởi tố pháp nhân DGC + đình chỉ hoạt động nhà máy chính, hoặc tiền gửi/HTM bị phong toả.

## 8. Tái lập
`$DNA_PYEXE -I calc/model_r3.py` → `calc/LOCK_r3_md5.txt` (19 file upstream: model/model_r2/model_r3 + out, compare_r3, BQ px 06/11 + SQL, common/common_r2, wpct, deposit_rate_vn + events, out_A_forecast, BCTC extract, r9_calc, ADDENDUM_5F_r2, TOP5C, STANDARD_r2) → `calc/compare_r3.py` → `calc/implied_r3.py` → `calc/make_summary_r3.py`. Chạy 2 lần trùng byte: model_r3_out.json `ba91265f…`, summary_r3_core.json `42fc85c5…`, implied_r3_out.json `0d3462f8…`, SUMMARY.json `a86b5916…`. Backup r2: `SUMMARY_r2.json`.
