# DDV — ADDENDUM 5F (bước 3c) · 07–08/11/2026 · job `Taylor_20261107_172007` (resume của `Taylor_20261107_131633`)

> NGHIÊN CỨU nội bộ, chưa qua fundamental-skeptic. KHÔNG sửa `REPORT_r2.md` / `SUMMARY.json` / `dd_price_zones`. 5F từ LLM-knowledge + BCTC/BQ = non-point-in-time ⇒ chỉ cho DD sống, không backtest.
> Số: `5F/ddv_moat_sens.py` → `5F/ddv_moat_sens_out.{json,txt}` (chạy lại 08/11 trùng byte, `cmp`); peer BQ `calc5f/peer.sql` → `calc5f/peer_out.csv` (`ticker_financial`, 2015–2025). Model gốc `calc/model.py`+`model_r2.py` import, không sửa.

## 1. Vị thế & lợi thế cạnh tranh (5F) — **LÀM MỚI**
Lý do: `data/moat_tags.csv` không có dòng DDV; `kb/projects/ddv-dd-20261028.md` (SUPERSEDED) và DD 26/10, 28/10 không có audit 5F ⇒ chưa có audit <12 tháng.
**Loại hình DN:** sản xuất hàng hoá chu kỳ (DAP/MAP, 1 nhà máy Đình Vũ 330k t/năm), kẻ ăn chênh lệch giá DAP − (S + NH3 + apatit), không tích hợp đầu vào.

| Lực | Mức | Bằng chứng (nguồn) |
|---|---|---|
| Cạnh tranh nội ngành | CAO | Lớn nhất VN ~28% thị phần DAP [VND25, qua DD 26/10 §#3] nhưng giá theo DAP thế giới (WB 800,6 USD/t T9/26) + hàng nhập TQ. GPM năm 2015–25 (dòng Q4 GPM_P0 = cả năm, BQ): DDV TB **10,6%** / trung vị 13,2% / min **−21,4%** (2016) vs LAS 17,7%, NFC 16,6%, BFC 13,4%, SFG 7,3% ⇒ không có lợi thế chi phí. |
| Quyền lực nhà cung cấp | CAO | apatit+S+NH3 ≈ **80% giá vốn** [VND25]; S nhập 100%, NH3 nhập một phần; apatit mua Apatit VN (cùng Vinachem, giá chuyển giao bên liên quan); S ~3,6× YoY 2026 (DD 26/10 #1). |
| Quyền lực khách hàng | TRUNG BÌNH–CAO | Hàng đồng nhất, giá thế giới; tập trung: phải thu **Liven Nutrients 217 tỷ = 9,8% VCSH** (BCTC Q3/26). |
| Sản phẩm thay thế | TRUNG BÌNH | MAP/NPK/DAP nhập thay được trực tiếp — **cần kiểm chứng** tỷ lệ chuyển dịch. |
| Đối thủ mới | THẤP | Vốn lớn + giấy phép môi trường cho nhà máy DAP mới — **cần kiểm chứng**; "đối thủ mới" thực tế là hàng nhập (TQ nới XK). |
| Lực thứ 6 (chính sách/đồng hồ) | CÓ ĐỒNG HỒ | Bãi thạch cao Đình Vũ = nút thắt công suất nhiều năm [VND25]; Vinachem thoái vốn chưa định ngày; chính sách XK phosphate TQ (chu kỳ); VAT 5% từ 01/07/2025 (+, **cần kiểm chứng**). |

**Ba điều kiện moat bền** (Ke = r = 13,5%, `common_r2.C.r_now()`; ROIC/ROE dòng 2025Q4 BQ):
| | DDV | Đối chiếu | Kết |
|---|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ROIC_Min5Y **2,2%**, ROIC5Y **14,4%**, ROIC10Y **8,3%**, ROIC_Min10Y **−10,0%** · ROE5Y 16,2%, ROE_Min5Y 4,0% (ROE ghi riêng, không thay ROIC) | ROIC5Y > Ke chỉ +0,9pp và nhờ đỉnh 2021–22; ROIC10Y < Ke 5,2pp; Min5Y/Min10Y ≪ Ke | ✗ |
| (ii) cơ chế rào cản gọi tên được | Quy mô 28% thị phần không chuyển thành chi phí thấp (GPM < peer phosphate) | — | ✗ |
| (iii) không có đồng hồ cắt hào | Bãi thạch cao + giá chuyển giao apatit + thoái vốn | — | ✗ |

**moat_tier = NONE · moat_type = NONE · rủi ro số 1:** spread DAP − (S+NH3+apatit) do giá thế giới quyết định, DDV price-taker cả hai đầu (apatit qua bên liên quan); phụ: bãi thạch cao chặn công suất. Không có cờ vụ án (REPORT_r2 §5) ⇒ không có giảm trừ pháp lý để tránh đếm hai lần.

## 2. Moat trong mô hình — **KHÔNG nhất quán với NONE** ⇒ báo bản CHẶT-3C
Mô hình r2 đang chứa 2 kênh thưởng ngầm (kiểm theo bài học C):
- **RONIC 20% > Ke 13,5%** (`model.py` `RONIC`), áp cả f27 lẫn terminal ⇒ tái đầu tư tạo giá trị — trái luật NONE.
- **Biên LN ròng giữa chu kỳ = TB riêng DDV 2015–25 = 4,05%** (`NPM_CYCLE`) giữ tới terminal, không phải TB ngành.

Bản CHẶT-3C: RONIC = Ke **đối xứng mọi ô lưới** (cả f27 và terminal) + NPM giữa chu kỳ = TB chu kỳ NGÀNH (NP/DT gộp 2015–25, BQ). Peer = SX phân bón nội địa (không phải đối thủ DAP trực tiếp duy nhất; DAP Lào Cai không niêm yết): DPM, DCM, LAS, BFC, VAF, NFC, SFG; **loại DGC** (hoá chất P4, NPM 25,5%). NPM peer: DCM 13,3% · DPM 12,6% · VAF 5,6% · NFC 4,8% · LAS 3,5% · BFC 2,8% (10 năm) · SFG 2,5%. **Headline = peer bỏ urê khí (DPM/DCM)**: đầu vào khí/than, cấu trúc spread khác DAP; bộ còn lại (phosphate/NPK) gần DDV hơn. Lựa chọn peer quyết định chiều ⇒ báo khoảng. Quy ước số mũ chiết khấu (0,125/0,75/1,25 năm) giữ nguyên model r2 — bản CURRENT tái lập đúng REPORT_r2 (13.109 / 10.115 / 12.823 / 16.270).

## 3. Kết quả (sau CK 5 tỷ 1,45%; giá 15.200 ngày 04/11/2026)
| Bản | NPM giữa CK | RONIC | Tâm | P10 / P50 / P90 | % dưới giá | Nhãn 5 tỷ | Nhãn 40tr |
|---|---|---|---|---|---|---|---|
| **Hiện hành r2** | 4,05% (DDV) | 20% | 13.109 | 10.115 / 12.823 / 16.270 | 76,9% | TRONG | TRONG |
| Chỉ RONIC=Ke | 4,05% | Ke | 12.430 | 9.612 / 12.221 / 15.417 | 89,3% | TRONG (P90 +1,4% trên giá — ranh giới) | TRONG |
| **CHẶT-3C headline (bỏ urê, trung vị)** | 3,50% | Ke | **11.187** | 8.669 / 11.111 / 13.847 | 97,6% | **TRÊN** | TRÊN |
| **CHẶT-3C headline (bỏ urê, TB)** | 3,83% | Ke | **11.937** | 9.237 / 11.788 / 14.814 | 93,8% | **TRÊN** (giá +2,6% trên P90 — sát ranh giới) | TRÊN |
| CHẶT-3C đủ 7 peer, trung vị | 4,81% | Ke | 14.136 | 10.872 / 13.835 / 17.519 | 64,8% | TRONG | TRONG |
| CHẶT-3C đủ 7 peer, TB | 6,42% | Ke | 17.738 | 13.517 / 17.267 / 22.133 | 25,0% | TRONG | TRONG |

Tách phần chênh (headline trung vị): RONIC 20%→Ke **−679** đ/cp; biên DDV→ngành **−1.243** ⇒ tổng −1.922 (−14,7%). Bản TB: −679 / −493 ⇒ −1.172 (−8,9%).

## 4. Độ nhạy WIDE / NARROW / NONE (nếu moat sai)
| Giả định | Tâm | P90 | Nhãn | Δ tâm vs r2 |
|---|---|---|---|---|
| WIDE giả định (RONIC 25%, biên DDV) | 13.390 | 16.646 | TRONG | +281 (+2,1%) |
| NARROW ≈ hiện hành (RONIC 20%, biên DDV) | 13.109 | 16.270 | TRONG | 0 |
| NONE chặt-3C (bỏ urê) | 11.187–11.937 | 13.847–14.814 | TRÊN | −1.922…−1.172 |
Giá trị DDV kém nhạy với RONIC (+281/−679) vì g 3% nhỏ; nhạy nhất là **chọn biên ngành** (−1.243…+5.308 tuỳ bộ peer).

## 5. Thay đổi so với báo cáo hiện hành
Mô hình r2 **lệch luật 3c** (RONIC 20% + biên riêng DDV cho mã moat NONE). Bản chặt-3C headline: tâm **13.109 → 11.187–11.937** (−14,7…−8,9%), P10 10.115 → 8.669–9.237, P50 12.823 → 11.111–11.788, P90 16.270 → 13.847–14.814; **nhãn TRONG → TRÊN** ở cả 5 tỷ và 40tr (bản TB sát ranh giới, +2,6%). Nếu Mike giữ đủ 7 peer (gồm urê) ⇒ nhãn TRONG giữ, tâm 14.136–17.738. ⇒ **Nhãn nhạy theo bộ peer; quy ước chờ Mike/user duyệt.** Không ghi SUMMARY/zones mới. Sleeve fear-buy §2.5 vẫn KHÔNG đủ điều kiện (REPORT_r2 §8) — kết luận này càng chắc vì #3 "leader chi phí" nay ✗ có số.

## 6. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
DDV,NONE,NONE,L,"Price-taker spread DAP-(S+NH3+apatite): ~80% COGS inputs, S 100% imported, apatite from related-party Apatit VN (Vinachem transfer price); ROIC10Y 8.3%/ROIC_Min5Y 2.2% < Ke 13.5%; GPM 2015-25 avg 10.6% below phosphate peers (LAS 17.7/NFC 16.6); gypsum-stack (Dinh Vu) caps capacity; 28% DAP share not a cost moat",2026-11-07,5f,N
```
entry = L (ngành phân bón phosphate hàng hoá, quyền lực NCC cao, giá thế giới — kém hấp dẫn cấu trúc, theo `moat_5f.py` schema). moat_upgrade = N.
