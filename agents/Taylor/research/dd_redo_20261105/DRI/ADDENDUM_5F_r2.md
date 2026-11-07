# DRI — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (r2 07/11/2026, job Taylor_20261107_122446; bản cũ: `ADDENDUM_5F_r1.md`)

Bổ sung cho `REPORT_r2.md` (05/11). Mọi phần khác của REPORT_r2 giữ nguyên. **Giá trị mô hình hiện hành KHÔNG đổi** (tâm 14.092 / P10 12.006 / P50 14.235 / P90 16.146 sau CK, TRONG vùng), **nhưng r1 viết sai "nhất quán với 3c" — r2 sửa: mô hình hiện hành LỆCH luật 3c (xem §2), kèm bản chặt-3c song song, chờ Mike/user duyệt.** Số: `calc_5f/moat_sens_5f_out.txt` (`$DNA_PYEXE -B moat_sens_5f.py`, 2 lần trùng md5 `91f50f05…`; chân đối chứng assert = pin r2 14.092; `calc/` không bị ghi).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng** tag `data/moat_tags.csv` dòng DRI: **NARROW · LOCATION/COST**, asof **2026-06-05**, src `5f_cyclical` (5 tháng < 12 tháng ⇒ không làm lại, theo luật tần suất 06/11). Dưới đây là kiểm nhanh bằng số đang có.

**Loại hình DN:** nhà sản xuất hàng hoá (mủ cao su, đồn điền tô nhượng tại Lào), **chấp nhận giá** (price-taker), lợi nhuận theo chu kỳ giá RSS3/SGX.

| Lực | Đánh giá (số + nguồn) |
|---|---|
| Cạnh tranh trong ngành | Hàng hoá đồng nhất, giá theo thị trường thế giới; DRI KH 2026 13.800 t (BCTN25 tr.46), quy mô nhỏ ⇒ không có quyền định giá. Mạnh. |
| Người mua | Bán mủ theo giá thị trường; **tập trung khách hàng: cần kiểm chứng** (thư mục không có số). |
| Đầu vào/nhà cung cấp | Tự chủ đất + vườn (tô nhượng Lào). Giá thành Cref **30,22 tr/t** (hiệu chỉnh từ LN 2025 của DRI) so giá TB chu kỳ **48,06 tr/t** (engine r4). **GPM TTM (có trọng số doanh thu, 4 quý/năm, dòng Q4) TB 2017–25: DRI 37,5% vs trung vị peer DPR/PHR/GVR 25,4% (+12,06pp; DRI > peer 9/9 năm)** — BQ `ticker_financial` GPM_Pi×Revenue_Pi, `calc_5f/ttm_bq.csv`. (r1 dùng GPM_P0 quý Q4 gọi là "TB năm" — sai nhãn, đã bỏ; 2026Q3 GPM_P0 ≈ 2026Q2 (0,39241 vs 0,39242) nghi chép đè ⇒ không dùng.) GVR thiếu dữ liệu 2017–18 (peer chỉ còn DPR/PHR). **Peer:** DPR/PHR/GVR là đối thủ cao su nội địa; TRC (cùng ngành) r1 loại không có lý do mạnh ⇒ nay đưa vào như bản nhạy: gap **trung vị 12,06 / TB 11,48 / +TRC 12,18 (TB 12,06) / DPR một mình 6,97pp**. Lưu ý so sánh: PHR/GVR có mảng KCN/gỗ, biên peer không thuần cao su. |
| Gia nhập mới | Rào cản = đất + 7 năm kiến thiết cơ bản (KTCB=7, engine) + vốn tái canh (PV capex tái canh tại điểm TB/L27 **2.764 đ/cp**). Rào cản chặn người mới về đất, nhưng không chặn cạnh tranh giá toàn cầu. |
| Sản phẩm thay thế | Cao su tổng hợp (theo giá dầu); **độ co giãn thay thế: cần kiểm chứng**. |
| **Lực thứ 6 (đồng hồ cắt hào)** | (a) Tô nhượng Lào — mốc **2054 = END của engine, văn bản chưa công khai ⇒ cần kiểm chứng** (không đánh ✔); mô hình cho giá trị về 0 sau 2054 (L0); (b) **NQ HĐQT 15**: thanh lý **1.975,23 ha (≈24% diện tích cạo)** 2027–30; (c) một phần đất trong quy hoạch rừng bảo tồn; (d) rò rỉ chuyển tiền/thuế Lào (KTPL 10,6%, w 10%, quỹ dự phòng 7,8% LNST). |

**Lợi nhuận siêu ngạch qua chu kỳ (Ke = r 13,5%):** ROE theo năm (ROE_Trailing, dòng Q4) 2018–2022 **6,0 / 4,6 / 3,4 / 10,0 / 9,7%** — dưới Ke 5 năm liền; 2023–25 13,8 / 19,6 / 23,3% (đỉnh giá). ROE_Min5Y **10,7%** < Ke; ROE5Y 15,8%. ROIC_Min5Y 16,8% (thuận) nhưng ROIC_Min10Y **6,5%** < Ke (ngược); ROIC5Y 19,5% (đỉnh gần đây). ROIC_Trailing ở dòng Q4 2021–25 ra **76–143%** ⇒ trường self-calc không tin cậy cho DRI, không dùng.

**Kết luận:** **moat_tier NARROW · moat_type LOCATION/COST (giữ nguyên tag 06/2026)**. Lợi thế giá thành có thật và lặp lại (+12,06pp GPM TTM, 9/9 năm), nhưng không thành lợi nhuận vượt Ke qua đáy chu kỳ. **Rủi ro số 1:** giá cao su (price-taker) — tag 06/2026 ghi "đỉnh"; tới 11/2026 đã qua đỉnh (LNST mẹ Q3 −33% YoY, REPORT_Q3_UPDATE). Rủi ro số 2 là đồng hồ đất (NQ15 + tô nhượng). **Kiểm nhanh có gì đổi hào từ 06/2026:** NQ15 làm quỹ đất co ≈24% (hào hẹp đi, không rộng ra); vụ Dakruco/bên liên quan là rủi ro quản trị, không phải hào. Tier không đổi.

## 2. Moat trong mô hình — SỬA r2
Ba điều kiện bền: (i) **TRƯỢT** (ROE<Ke 2018–22; ROE_Min5Y, ROIC_Min10Y<Ke); (ii) cơ chế gọi tên được — có một phần (đất + giá thành, chỉ phía chi phí); (iii) **TRƯỢT** (2054 chưa kiểm chứng, NQ15, rừng bảo tồn) ⇒ **moat_durable=false ⇒ luật 3c: RONIC=Ke VÀ biên về TB chu kỳ NGÀNH.**

**Kiểm mô hình hiện hành (r1 bỏ sót):** RONIC=Ke ✔ (nhánh NPV0), giá mủ mid=TB chu kỳ ✔, L0 sau 2054 ✔, **nhưng biên KHÔNG về TB ngành**: Cref giữ 30,22 tr/t tới 2054 (hiệu chỉnh từ LN 2025 đỉnh của chính DRI) ⇒ GPM mô hình tại giá TB ≈ **36,1%** (peer TTM ~25,4%); LNST giữa chu kỳ (giá TB, 13.800 t) **≈151,9 tỷ** ⇒ **ROE giữa chu kỳ ≈ 18,9–20,7% > Ke 13,5%** (VCSH 2026Q2 805 / Q3 735 tỷ) — trái (i) mà tự chấm trượt, trái ADDENDUM r1 "lợi thế đã nằm trong biên". Tính này là mô hình hiện hành NGẦM thưởng moat bền. (Skeptic nêu LNST mid 163,6 tỷ — spec khác, không tái hiện; kết luận cùng chiều.) Đồng hồ cắt hào (2054/NQ15) chỉ cắt đuôi, không hạ biên.

**Hai cách xử lý (chờ Mike/user chọn):**
(a) **Ngoại lệ 3c tường minh** — lợi thế đất/vườn Lào, đối thủ không vào được. Bằng chứng cơ cấu giá thành vs peer (năng suất t/ha, nhân công, thuê đất): **cần kiểm chứng** (thư mục chỉ có năng suất DRI 1,69 t/ha KH2026 BCTN25; không có số peer). **Lệch luật 3c, chờ duyệt** ⇒ chưa đủ cơ sở.
(b) **Chặt-3c**: fade chênh biên về TB ngành (bảng §3). Bản này mô tả đúng luật nhưng là **quy ước chờ duyệt**.

## 3. Độ nhạy (lưới 36 kết cục, sau CK 5 tỷ, giá 13.500; Cref chặt = 30,22 + gap×48,06)
| Bản | Cref | Tâm | Δ | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **Hiện hành (ngầm moat)** | 30,22 | **14.092** | 0 | 12.006 / 14.235 / 16.146 | 35,2% | TRONG |
| **NONE½** (fade nửa gap) | 33,12 | 12.438 | −1.654 (−11,7%) | 10.391 / 12.705 / 14.430 | 78,8% | TRONG |
| **NONE chặt** (gap trung vị 12,06pp) | 36,02 | **10.784** | −3.308 (−23,5%) | 8.798 / 11.055 / 12.844 | 98,0% | **TRÊN** vùng |
| NONE đối xứng (NONE + bỏ nhánh KINH TẾ, RONIC=Ke cả hai phía) | 36,02 | 11.091 | −3.001 (−21,3%) | 8.854 / 11.215 / 13.014 | 97,5% | TRÊN |
| WIDE [UL minh hoạ] n=18 | 30,22 | 14.965 | +873 (+6,2%) | 12.817 / 15.055 / 16.957 | 17,5% | TRONG |
| — trong đó chỉ bỏ nhánh KINH TẾ (S=0) | 30,22 | 14.288 | +196 | 12.140 / 14.378 / 16.280 | 30,0% | TRONG |

- **Tách RONIC vs biên:** nhánh NPV0 sẵn RONIC=Ke; phần chênh −3.308 là hoàn toàn từ biên (Cref). Bỏ thêm nhánh KINH TẾ (đối xứng) cộng +307 ⇒ nhánh KINH TẾ là đuôi dưới, không phải kênh moat.
- **Độ nhạy cách chọn peer (NONE, tâm):** trung vị 3 peer 10.784 · TB 3 peer (11,48pp) 10.944 · +TRC trung vị (12,18pp) 10.751 · +TRC TB 10.785 · **DPR một mình (6,97pp) 12.180 (−13,6%, TRONG vùng, 79,8% dưới giá)**. Khoảng NONE: **10.751–12.180**; nhãn TRÊN ở mọi bản nhiều peer, TRONG nếu chỉ lấy DPR ⇒ nhãn nhạy peer, ghi **ranh giới** giữa NONE½ và NONE.
- **Cỡ sleeve thật** (10–40 triệu; CK 0,09–0,18% thay 2,00%): P90 NONE tăng ≈ +1,9% ⇒ ≈13,09k (**ước lượng**, chưa chạy lại) vẫn < giá 13.500 ⇒ nhãn TRÊN không đổi.
- **WIDE:** +873 gồm ≈+196 do chỉ bỏ nhánh KINH TẾ (REPORT_r2 §37), phần moat thật ≈ **+677 (+4,8%)**; S=0,25 là giả định, không dẫn chứng peer; WIDE không có cơ sở (n=18, không còn "cùng lưới 36 kết cục").
- Quy ước hiện: không dùng năm đỉnh cho giá; vụ Dakruco là WARNING, không dùng ép biên (đã không dùng); giảm trừ pháp lý trong base giữ như REPORT_r2 — không đếm hai lần. Chiết khấu: engine r4 dùng T27=0,67 năm cho dòng 2027 (quy ước năm 1 giữ nguyên, không đổi ở addendum).

## 4. Thay đổi so với báo cáo hiện hành
Số hiện hành **không đổi**. Nhưng câu "nhất quán với 3c" của r1 **sai theo chữ**: mô hình giữ biên DRI cao hơn ngành tới 2054 (ROE mid ≈19–21%>Ke) ngầm hàm ý moat bền, trong khi tag NARROW/không bền. Theo luật 3c đúng chữ, giá trị là **NONE chặt 10.784 (TRÊN vùng, 98% dưới giá)** hoặc ít nhất **NONE½ 12.438 (TRONG, 78,8% dưới giá)**, so với 14.092 (35%). Nhãn có thể chuyển TRONG→TRÊN; khoảng theo peer 10.751–12.180. **Chờ Mike/user quyết**: giữ ngoại lệ (a) khi có bằng chứng giá thành peer, hay áp (b). Không sửa REPORT/SUMMARY cũ, không ghi `dd_price_zones`. 5F non-PIT ⇒ chỉ DD sống. WARNING pháp lý giữ như REPORT_r2 §5.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự sửa)
Cột `entry` = độ hấp dẫn cấu trúc NGÀNH (moat_5f.py:33): cao su hàng hoá, price-taker ⇒ **L** (r1 để M). `moat_upgrade`: dòng 06/2026 đang Y; grep không thấy file .py nào ngoài research đọc cột này ⇒ không ảnh hưởng chạy; moat không bền ⇒ đề xuất **N** (có chủ ý, Mike xác nhận).
```
DRI,NARROW,LOCATION/COST,L,"Commodity price-taker; cost edge real (GPM TTM 2017-25 37.5% vs peer median 25.4%, 9/9 yrs) but ROE<Ke 2018-22, ROE_Min5Y 10.7%<Ke 13.5%, ROIC_Min10Y 6.5% => not durable (rule 3c: margin to industry mean); post-peak (Q3-26 NP -33% YoY); land clock: NQ15 liquidates 1,975 ha (~24% tapped) 2027-30, Laos concession end 2054 unverified; Dakruco related-party governance risk",2026-11-07,5f_quickcheck_reuse_20260605,N
```
