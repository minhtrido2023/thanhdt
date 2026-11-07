# HPG — ADDENDUM 5F (bước 3c) · 07/11/2026 · job `Taylor_20261107_130203`

> Bổ sung cho `REPORT_r2.md` (05/11). Mọi phần khác của REPORT_r2 giữ nguyên. 5F dựa phần cấu trúc ngành trên kiến thức LLM, **không point-in-time ⇒ chỉ dùng cho DD sống, cấm đưa vào backtest**.
> Calc: `calc/5f/hpg_5f.py` (mô hình RI + lưới 675 kết cục **chép nguyên** `hpg_r2.py`, chỉ đổi quy tắc terminal). Chạy 2 lần trùng byte (`hpg_5f_out.txt` md5 `05a17d88…`). Nhánh CUR tái lập đúng r2: 16.286 / 8.942 / 16.343 / 23.520.
> Số BQ: `tav2_bq.ticker_financial`, dòng Q4 mỗi năm (GPM_P0/EBITM_P0 là TTM ⇒ dòng Q4 = cả năm), truy vấn 07/11.

## 1. Tái dùng hay làm mới
**Làm mới đầy đủ.** `data/moat_tags.csv` không có dòng HPG; REPORT DD 31/10 và `kb/projects/hpg-dd-20261031.md` không có mục 5F/moat. Lần 5F đầu tiên cho mã này.

## 2. Vị thế & lợi thế cạnh tranh (5F)
**Loại hình:** nhà sản xuất hàng hoá cơ bản, chịu chu kỳ, phải nhận giá thị trường (thép tích hợp lò cao BF-BOF, thép xây dựng + HRC). Ngành kém hấp dẫn về cấu trúc.

| Lực | Nhận định + số (nguồn) |
|---|---|
| 1. Cạnh tranh nội bộ | Doanh thu 2025 **158,3 nghìn tỷ**, so với 130,2 nghìn tỷ của 7 mã thép niêm yết khác cộng lại (HSG, NKG, TVN, GDA, VGS, SMC, TLH) [BQ]. GPM **cao nhất nhóm 10/11 năm 2015–2025** (ngoại lệ 2023: HSG 11,7% vs HPG 10,9%): trung bình 10 năm 2016–25 là **19,2%**, so với HSG 13,4% và trung vị/TB 6 peer 5,7%/6,4% (GDA chỉ có 2023–25, loại khỏi TB). EBITM 2025 13,1% so với HSG 1,8%, NKG 1,6% [BQ]. Thị phần thép xây dựng/HRC: **cần kiểm chứng** (VSA). |
| 2. Nhà cung cấp | Quặng sắt và than mỏ chủ yếu nhập khẩu, giá theo thị trường thế giới ⇒ HPG nhận giá đầu vào. Mức tự chủ cốc/quặng: **cần kiểm chứng**. |
| 3. Khách hàng | Phân tán (đại lý, nhà thầu, các nhà tôn mạ mua HRC). Hàng hoá đồng nhất nên chi phí chuyển đổi của khách thấp. Không có số tập trung khách hàng: **cần kiểm chứng**. |
| 4. Sản phẩm thay thế | Thấp với thép xây dựng/HRC. |
| 5. Gia nhập mới | Rào cản vốn rất cao: XDCB dở dang 16.113 tỷ, cam kết ~19.472 tỷ [HN-Q3]. Áp lực "gia nhập" thực tế là **thép nhập khẩu TQ**, hiện bị chặn bằng chính sách (lực 6). |
| 6. Chính sách (đồng hồ) | Bảo hộ: AD HRC (QĐ 1959) + chống lẩn tránh QĐ 1917/QĐ-BCT 27,83%, hiệu lực 28/07/2026 [REPORT_r2 §9]. Mốc hết hạn/rà soát cuối kỳ: **cần kiểm chứng**. Ưu đãi thuế DQ2: CV 377 chưa có kết luận (đã vào base qua thuế terminal 20%). CBAM EU. Đây là **đồng hồ chính sách**: phần biên vượt trội gần đây phụ thuộc bảo hộ có thời hạn. |

**Ba điều kiện moat bền:**

| Điều kiện | Bằng chứng, trích cả hai phía | Kết quả |
|---|---|---|
| (i) Siêu ngạch nhiều chu kỳ, so với Ke 13,5% | **ROIC** (Q4/25 = Q3/26): Min5Y **5,7%** · 5Y **11,0%** · 10Y **13,0%** · Min10Y **5,7%**, đều ≤ Ke. **ROE** (tách riêng): năm 2022–25 là 8,4/6,8/10,9/12,4%, đều < Ke; 2016–21 từ 16,8% đến 44,2%, > Ke; ROE5Y 16,9% · ROE10Y 21,9% · ROE_Min5Y 6,9% · TTM Q3/26 19,5%. ⚠️ Trường ROIC5Y/ROIC_Trailing trong BQ có nhiều giá trị >1 phi lý ⇒ ROIC từ BQ chất lượng thấp, **cần kiểm chứng** bằng BCTC. | **KHÔNG ĐẠT.** Siêu ngạch tuyệt đối không liên tục: 4 năm gần nhất dưới Ke. Ưu thế **tương đối** so với peer thì liên tục. |
| (ii) Cơ chế gọi tên được | Quy mô + tích hợp BF-BOF (chi phí/tấn thấp nhất nội địa) + cảng nước sâu Dung Quất. Bằng chứng gián tiếp: GPM vượt mọi peer 10/11 năm. Chi phí/tấn: **cần kiểm chứng**. | ĐẠT (COST/SCALE) |
| (iii) Không có đồng hồ cắt hào | Bảo hộ AD có thời hạn; ưu đãi thuế DQ2 chưa rõ; dư cung thép TQ | **KHÔNG ĐẠT** |

**moat_tier = NARROW · moat_type = COST/SCALE · không bền** (trượt (i) và (iii)).
**Rủi ro số 1:** biên lợi nhuận tựa vào bảo hộ AD trước thép TQ dư cung (có thời hạn). Đảo chiều chính sách ⇒ HRC về giá nhập khẩu, đúng lúc vốn DQ2 đang dồn.
WARNING pháp lý/quản trị (TLSH, liên danh BT…) giữ nguyên REPORT_r2 §9. Không dùng các WARNING này để ép biên.

## 3. Moat trong mô hình — KHÔNG thưởng; mô hình hiện hành **KHÔNG nhất quán** luật 3c ở 2 kênh
1. **RONIC (kênh ngầm):** quy tắc terminal r2 là `g_RI = 0 nếu ROE_T < r, ngược lại g_RI = g`. Nhánh TỐT (ROE_T **14,25%** > 13,5%) được cho phần siêu ngạch tăng 5%/năm vĩnh viễn, tức là ngầm RONIC > Ke, một mức thưởng kiểu WIDE. Hai nhánh XẤU (7,85%) và TRUNG LẬP (11,84%) đã ở g_RI = 0.
2. **Biên/ROE terminal so với TB chu kỳ ngành:** ROE_T của nhánh TỐT 14,25% cao hơn ROE10Y của peer nội địa (trung vị **12,4%** / TB **11,6%**). XẤU 7,85% thấp hơn; TRUNG LẬP 11,84% xấp xỉ TB peer.
- **Peer:** đều là peer **nội địa nhưng không cùng mô hình** (tôn mạ/thương mại/EAF; không có mã BF-BOF niêm yết vì Formosa Hà Tĩnh không niêm yết). POM bị loại vì ROE âm sâu/phi lý (2025: 42,2). Peer ROE10Y: HSG 16,2 · NKG 15,1 · GDA 15,9 · VGS 12,4 · SMC 11,2 · TLH 5,9 · TVN 4,4%.
- **Bản CHẶT-3C (headline, quy ước chờ Mike/user duyệt):** RONIC = Ke đối xứng (g_RI = 0 mọi nhánh) + ROE_T **hồi về TB chu kỳ ngành ở cả hai phía** (REV). Năm 1 = 0,25 năm (Q4/26) và ROLL tới 04/11 giữ đúng quy ước r2. Thuế terminal 20% và trục TLSH giữ nguyên, nên không đếm hai lần.
- Đường LN 2027–29 (ROE TRUNG LẬP 2027 ≈ 17,5% > Ke) là dự báo 3 năm hữu hạn neo vào run-rate 9T26, không phải giả định moat ⇒ giữ nguyên.

## 4. Kết quả (sau CK @5 tỷ; nhãn ở 5 tỷ = 10 tr = 40 tr, giống nhau ở mọi bản)
| Bản | Tâm | P10 | P50 | P90 | % dưới giá 21.700 | Nhãn |
|---|---|---|---|---|---|---|
| Hiện hành r2 (CUR) | 16.286 | 8.942 | 16.343 | 23.520 | 83,6% | TRONG |
| Chỉ RONIC = Ke đối xứng (SYM) | 16.016 | 8.942 | 16.343 | 22.321 | 86,7% | TRONG |
| **CHẶT-3C, neo trung vị peer (REVm)** | **16.986** | **14.448** | **17.090** | **19.395** | 100% | **TRÊN** |
| **CHẶT-3C, neo TB peer (REVa)** | **15.956** | **13.556** | **16.051** | **18.235** | 100% | **TRÊN** |
| Cắt một chiều, chỉ tham khảo (CAPm / CAPa) | 15.112 / 14.614 | 8.942 / 8.942 | 16.343 / 15.945 | 19.395 / 18.235 | 100% | TRÊN |

**Phần chênh từ CUR sang REVm:** kênh RONIC −270 (CUR→SYM; P90 −1.199). Kênh biên/ROE hồi về TB +970 (SYM→REVm): nhánh XẤU được kéo lên từ 7,85% thì P10 +5.506, nhánh TỐT bị kéo xuống thì P90 −2.926. Tâm thay đổi ít (−330 đến +700) nhưng **phân phối co lại mạnh**, P90 rơi xuống dưới giá ⇒ **nhãn đổi TRONG → TRÊN**. Không phải ca ranh giới: giá cao hơn P90 11,9% (REVm) đến 19,0% (REVa). Nhãn không nhạy theo việc chọn trung vị hay TB peer, nhưng **nhạy theo peer set**: peer không cùng mô hình, xem §5.

## 5. Độ nhạy theo moat (tâm / P10–P90 / nhãn)
| Giả định moat | Quy tắc | Tâm | P10–P90 | Nhãn | Δ tâm vs CUR |
|---|---|---|---|---|---|
| WIDE | ROE_T ≥ ROE5Y HPG × thuế 20% (15,36%), g_RI = g (RONIC > Ke) | 22.133 | 18.331–25.154 | TRONG (41% dưới giá) | +5.847 (+35,9%) |
| NARROW, CHẶT-3C | như REVm / REVa | 15.956–16.986 | 13.556–19.395 | TRÊN | −330 … +700 |
| NONE | SYM + spread (ROE_T − r) fade tuyến tính về 0 trong 5 năm, hai chiều | 17.656 | 13.625–21.204 | TRÊN (sát: P90 thấp hơn giá 2,3% ⇒ **ranh giới**) | +1.370 |

Nếu neo TB ngành bằng **chính chu kỳ HPG** thay vì peer nội địa (lập luận: HPG chính là phân khúc BF-BOF nội địa), kết quả đổi theo cửa sổ. ROE5Y HPG × thuế = 15,36% gần với nhánh WIDE (nhãn TRONG). TB 2022–25 = 9,6% thì thấp hơn REVa. ⇒ Nhãn nhạy theo cách chọn neo; đây là quyết định quy ước của Mike/user.

## 6. Thay đổi so với báo cáo hiện hành
Moat NARROW không bền ⇒ **không thưởng**. Mô hình r2 **có** chứa thưởng ngầm (RONIC > Ke ở nhánh TỐT, ROE terminal của nhánh TỐT cao hơn TB peer) nên không ghi "nhất quán". Theo đúng luật 3c (CHẶT-3C), tâm **15.956–16.986** (so với 16.286, đổi −2,0% … +4,3%), P90 **18.235–19.395** (so với 23.520), nhãn **TRONG → TRÊN vùng** ở mọi cỡ lệnh. Đây là quy ước chờ Mike/user duyệt. KHÔNG sửa REPORT_r2/SUMMARY.json/dd_price_zones.

## 7. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
HPG,NARROW,COST/SCALE,L,"Integrated BF-BOF scale/cost leader (GPM top of listed VN steel 10/11 yrs 2015-25, 10y avg 19.2% vs peer median 5.7%) BUT absolute excess return not multi-cycle (ROIC_Min5Y 5.7%, ROIC10Y 13.0% <= Ke 13.5%; ROE 2022-25 6.8-12.4%); #1 risk: margin leans on time-limited AD protection vs Chinese HRC oversupply (QD 1917 27.83% eff 2026-07-28) while DQ2 capex concentrated; DQ2 tax incentive unresolved (CV 377)",2026-11-07,5f,N
```
entry = L vì ngành thép commodity kém hấp dẫn cấu trúc (`moat_5f.py`: entry = độ hấp dẫn ngành); moat_upgrade = N.
