# DRI — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (07/11/2026, job Taylor_20261107_120601)

Bổ sung cho `REPORT_r2.md` (05/11). Mọi phần khác của REPORT_r2 giữ nguyên. **Mô hình KHÔNG đổi** (tâm 14.092 / P10 12.006 / P50 14.235 / P90 16.146 sau CK, nhãn TRONG vùng). Số độ nhạy: `calc_5f/moat_sens_5f_out.txt` (`$DNA_PYEXE -B moat_sens_5f.py`, chạy 2 lần trùng md5 `7a7522c6…`; chân đối chứng assert = pin r2 14.092; `calc/` không bị ghi).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng** tag `data/moat_tags.csv` dòng DRI: **NARROW · LOCATION/COST**, asof **2026-06-05**, src `5f_cyclical` (5 tháng < 12 tháng ⇒ không làm lại, theo luật tần suất 06/11). Dưới đây là kiểm nhanh bằng số đang có.

**Loại hình DN:** nhà sản xuất hàng hoá (mủ cao su, đồn điền tô nhượng tại Lào), **chấp nhận giá** (price-taker), lợi nhuận theo chu kỳ giá RSS3/SGX.

| Lực | Đánh giá (số + nguồn) |
|---|---|
| Cạnh tranh trong ngành | Hàng hoá đồng nhất, giá theo thị trường thế giới; DRI KH 2026 13.800 t (BCTN25 tr.46), quy mô nhỏ ⇒ không có quyền định giá. Mạnh. |
| Người mua | Bán mủ theo giá thị trường; **tập trung khách hàng: cần kiểm chứng** (thư mục không có số). |
| Đầu vào/nhà cung cấp | Tự chủ đất + vườn (tô nhượng Lào). Giá thành Cref **30,22 tr/t** (hiệu chỉnh từ LN 2025 của DRI) so giá TB chu kỳ **48,06 tr/t** (engine r4). **GPM TB 2017–25 DRI 36,9% vs trung vị peer DPR/PHR/GVR 25,2% (+11,7pp, DRI cao hơn trung vị cả 9/9 năm)** — BQ `ticker_financial` GPM_P0 các dòng Q4. Lưu ý so sánh: PHR/GVR có mảng KCN/gỗ, biên peer không thuần cao su. |
| Gia nhập mới | Rào cản = đất + 7 năm kiến thiết cơ bản (KTCB=7, engine) + vốn tái canh (PV capex tái canh tại điểm TB/L27 **2.764 đ/cp**). Rào cản chặn người mới về đất, nhưng không chặn cạnh tranh giá toàn cầu. |
| Sản phẩm thay thế | Cao su tổng hợp (theo giá dầu); **độ co giãn thay thế: cần kiểm chứng**. |
| **Lực thứ 6 (đồng hồ cắt hào)** | (a) Tô nhượng Lào — văn bản chưa công khai; mô hình đã cho giá trị về 0 sau **2054** (L0); (b) **NQ HĐQT 15**: thanh lý **1.975,23 ha (≈24% diện tích cạo)** 2027–30; (c) một phần đất trong quy hoạch rừng bảo tồn; (d) rò rỉ chuyển tiền/thuế Lào (KTPL 10,6%, w 10%, quỹ dự phòng 7,8% LNST). |

**Lợi nhuận siêu ngạch qua chu kỳ (Ke = r 13,5%):** ROE theo năm (ROE_Trailing, dòng Q4) 2018–2022 **6,0 / 4,6 / 3,4 / 10,0 / 9,7%** — dưới Ke 5 năm liền; 2023–25 13,8 / 19,6 / 23,3% (đỉnh giá). ROE_Min5Y **10,7%** < Ke; ROE5Y 15,8%. ROIC_Min5Y 16,8% nhưng ROIC_Min10Y **6,5%** < Ke. ROIC_Trailing ở dòng Q4 2021–25 ra **76–143%** ⇒ trường self-calc không tin cậy cho DRI, không dùng.

**Kết luận:** **moat_tier NARROW · moat_type LOCATION/COST (giữ nguyên tag 06/2026)**. Lợi thế giá thành có thật và lặp lại (+11,7pp GPM, 9/9 năm), nhưng không thành lợi nhuận vượt Ke qua đáy chu kỳ. **Rủi ro số 1:** giá cao su (price-taker) — tag 06/2026 ghi "đỉnh"; tới 11/2026 đã qua đỉnh (LNST mẹ Q3 −33% YoY, REPORT_Q3_UPDATE). Rủi ro số 2 là đồng hồ đất (NQ15 + tô nhượng). **Kiểm nhanh có gì đổi hào từ 06/2026:** NQ15 làm quỹ đất co ≈24% (hào hẹp đi, không rộng ra); vụ Dakruco/bên liên quan là rủi ro quản trị, không phải hào. Tier không đổi.

## 2. Moat trong mô hình
Ba điều kiện bền: (i) siêu ngạch nhiều chu kỳ — **TRƯỢT** (ROE < Ke 2018–22; ROE_Min5Y, ROIC_Min10Y < Ke); (ii) cơ chế gọi tên được — **CÓ một phần** (đất tô nhượng + giá thành thấp; chỉ phía chi phí, không có quyền định giá); (iii) không có đồng hồ — **TRƯỢT** (2054, NQ15, rừng bảo tồn) ⇒ **moat_durable = false ⇒ KHÔNG thưởng**.

**Đã ngầm trong mô hình và nhất quán, không đếm hai lần:**
| Tham số engine r4/r2 | Giá trị | Tương ứng moat |
|---|---|---|
| Giá thành Cref | 30,22 tr/t, hiệu chỉnh từ LN 2025 của chính DRI | lợi thế giá thành NARROW **đã nằm trong biên** — không cộng premium |
| Giá mủ mid | TB RSS3 thực 2014-01..2026-09 (P25/TB/P75) | biên về TB chu kỳ, không dùng năm đỉnh ✔ |
| Tái canh | NPV0 (luật 20) ⇒ RONIC = Ke; nhánh KINH TẾ (NPV<0) trọng số 0,20 | đúng luật NARROW ✔ |
| Giá trị cuối | L0: không có giá trị sau 2054 | đồng hồ tô nhượng đã phản ánh ✔ |
| Bội số | không dùng bội số | — |

## 3. Độ nhạy theo moat (cùng lưới 36 kết cục, sau CK, giá 13.500)
| Kịch bản | Thay đổi tham số | Tâm | Δ tâm | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **NARROW (hiện hành)** | — | **14.092** | 0 | 12.006 / 14.235 / 16.146 | 35,2% | TRONG vùng |
| NONE ½ | xoá ½ chênh GPM: Cref +½×11,7pp×48,06 | 12.489 | −1.603 (−11,4%) | 10.440 / 12.760 / 14.492 | 78,8% | TRONG vùng |
| NONE | xoá hết chênh GPM: Cref 30,22 → 35,84 tr/t | 10.885 | −3.207 (−22,8%) | 8.896 / 11.150 / 12.944 | 98,0% | TRÊN vùng |
| WIDE [UL minh hoạ] | tái canh RONIC>Ke: NPV = +0,25 × PV capex; bỏ nhánh KINH TẾ | 14.965 | +873 (+6,2%) | 12.817 / 15.055 / 16.957 | 17,5% | TRONG vùng |

Đọc: rủi ro bất đối xứng — nếu tag NARROW sai về phía NONE (lợi thế giá thành mất), giá trị giảm 11–23%; nếu sai về phía WIDE, tăng ~6% (con số 0,25 là giả định minh hoạ, không có dẫn chứng peer). WIDE không có cơ sở (đồng hồ 2054 + NQ15).

## 4. Thay đổi so với báo cáo hiện hành
Không đổi giá trị, không đổi nhãn. Mô hình r2 đã chứa lợi thế giá thành NARROW qua Cref hiệu chỉnh từ số thật, giá mủ TB chu kỳ, RONIC = Ke và không có giá trị sau 2054 — nhất quán với NARROW và moat không bền, nên không cộng/trừ tham số moat. Bổ sung duy nhất là bảng độ nhạy ở mục 3 và bằng chứng định lượng ở mục 1. Không sửa REPORT/SUMMARY cũ, không ghi `dd_price_zones`. 5F dựa trên kiến thức LLM + số BQ, không point-in-time ⇒ chỉ dùng cho DD sống, không đưa vào backtest. WARNING pháp lý (Dakruco, bên liên quan, NQ15) giữ nguyên như REPORT_r2 §5.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự sửa — Mike/user quyết)
Giữ tier/type, chỉ làm mới risk1 + asof:
```
DRI,NARROW,LOCATION/COST,M,"Commodity price-taker; cost edge real (GPM 2017-25 avg 36.9% vs peer median 25.2%, 9/9 yrs) but ROE<Ke 2018-22 (3.4-10%), ROE_Min5Y 10.7%<Ke 13.5% => not durable; post-peak (Q3-26 NP -33% YoY); land clock: NQ15 liquidates 1,975 ha (~24% tapped) 2027-30, Laos concession modelled to 2054, part in conservation-forest zoning; Dakruco related-party governance risk",2026-11-07,5f_quickcheck_reuse_20260605,Y
```
