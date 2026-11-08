> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành (đồng bộ r3 08/11: tâm 21.338, P10 13.316, P50 21.759, P90 28.993, nhãn TRONG vùng, theo `REPORT_r3.md`; 16.286 là tâm r2 cũ, chỉ còn là mốc so sánh)**; mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.
>
> **Ghi chú đồng bộ r3 (08/11):** mọi con số tâm/P10/P90 trong bảng bên dưới (CUR 16.286, REVF 18.376, NONE 17.656, WIDE 22.133, các bản chặt-3c…) được tính trên mô hình r2 (vốn giữ lại sinh lời 0%) và chỉ là độ nhạy tương đối ('nếu về trung bình ngành') quanh mô hình r2, KHÔNG phải tâm hiện hành. Tâm hiện hành là r3 = 21.338.

# HPG — ADDENDUM 5F (bước 3c) · 07/11/2026 · job `Taylor_20261107_130203` · **vòng sửa r2** job `Taylor_20261107_131620` (bản trước: `ADDENDUM_5F_r1.md`)

> Bổ sung cho `REPORT_r2.md` (05/11). Mọi phần khác của REPORT_r2 giữ nguyên. 5F dựa phần cấu trúc ngành trên kiến thức LLM, **không point-in-time ⇒ chỉ dùng cho DD sống, cấm đưa vào backtest**.
> Calc: `calc/5f/hpg_5f_r2.py` (mô hình RI + lưới 675 kết cục **chép nguyên** `hpg_r2.py`, chỉ đổi quy tắc terminal; neo peer đọc `peer_roe_q4_2016_2025.csv`). Chạy 2 lần trùng byte (`hpg_5f_r2_out.txt` md5 `a99b6a20…`, `.json` `47f9d293…`). Nhánh CUR tái lập đúng r2: 16.286 / 8.942 / 16.343 / 23.520. Bản r1 `hpg_5f.py` giữ nguyên để đối chiếu.
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
| 6. Chính sách (đồng hồ) | Bảo hộ: AD HRC (QĐ 1959) + chống lẩn tránh QĐ 1917/QĐ-BCT 27,83%, hiệu lực 28/07/2026 [REPORT_r2 §9]. ⚠️ QĐ 1917 **mới thấy trên báo, chưa mở bản gốc moit.gov.vn** (GAPS2, `kb/projects/hpg-dd-20261031.md`) và **chỉ phủ HRC bề rộng 1.880–2.300 mm**, không phải toàn bộ HRC ⇒ mức/phạm vi bảo hộ **cần kiểm chứng**. Mốc hết hạn/rà soát cuối kỳ: **cần kiểm chứng**. Ưu đãi thuế DQ2: CV 377 chưa có kết luận (đã vào base qua thuế terminal 20%). CBAM EU. Đây là **đồng hồ chính sách**: phần biên vượt trội gần đây phụ thuộc bảo hộ có thời hạn. |

**Ba điều kiện moat bền:**

| Điều kiện | Bằng chứng, trích cả hai phía | Kết quả |
|---|---|---|
| (i) Siêu ngạch nhiều chu kỳ, so với Ke 13,5% | **ROIC** (Q4/25 = Q3/26): Min5Y **5,7%** · 5Y **11,0%** · 10Y **13,0%** · Min10Y **5,7%**, đều ≤ Ke. **ROE** (tách riêng): năm 2022–25 là 8,4/6,8/10,9/12,4%, đều < Ke; 2016–21 từ 16,8% đến 44,2%, > Ke; ROE5Y 16,9% · ROE10Y 21,9% · ROE_Min5Y 6,9% · TTM Q3/26 19,5%. ⚠️ Trường ROIC5Y/ROIC_Trailing trong BQ có nhiều giá trị >1 phi lý ⇒ ROIC từ BQ chất lượng thấp, **cần kiểm chứng** bằng BCTC. ⚠️ ROE/ROIC 2022–25 **bị vốn DQ2 dở dang (XDCB) kéo thấp** vì vốn chưa sinh lời nằm trong mẫu số (Q3/26 XDCB 16.113 tỷ ≈ 10,8% VCSH; quy mô XDCB 2022–24: **cần kiểm chứng**). Bỏ phần này ra thì ROE 2025 lên khoảng 13,9% (`ước lượng`), vẫn ≈ Ke. | **KHÔNG ĐẠT** (kết luận không đổi sau khi tính tới DQ2). Siêu ngạch tuyệt đối không liên tục: 4 năm gần nhất dưới Ke; ROIC_Min5Y 5,7% không phụ thuộc vào điều chỉnh DQ2. Ưu thế **tương đối** so với peer thì liên tục. |
| (ii) Cơ chế gọi tên được | Quy mô + tích hợp BF-BOF (chi phí/tấn thấp nhất nội địa) + cảng nước sâu Dung Quất. Bằng chứng gián tiếp: GPM vượt mọi peer 10/11 năm. Chi phí/tấn: **cần kiểm chứng**. | ĐẠT (COST/SCALE) |
| (iii) Không có đồng hồ cắt hào | Bảo hộ AD có thời hạn; ưu đãi thuế DQ2 chưa rõ; dư cung thép TQ | **KHÔNG ĐẠT** |

**moat_tier = NARROW · moat_type = COST/SCALE · không bền** (trượt (i) và (iii)).
**Rủi ro số 1:** biên lợi nhuận tựa vào bảo hộ AD trước thép TQ dư cung (có thời hạn). Đảo chiều chính sách ⇒ HRC về giá nhập khẩu, đúng lúc vốn DQ2 đang dồn.
WARNING pháp lý/quản trị (TLSH, liên danh BT…) giữ nguyên REPORT_r2 §9. Không dùng các WARNING này để ép biên.

## 3. Moat trong mô hình — KHÔNG thưởng; mô hình hiện hành **KHÔNG nhất quán** luật 3c ở 2 kênh
1. **RONIC (kênh ngầm):** quy tắc terminal r2 là `g_RI = 0 nếu ROE_T < r, ngược lại g_RI = g`. Nhánh TỐT (ROE_T **14,25%** > 13,5%) được cho phần siêu ngạch tăng 5%/năm vĩnh viễn, tức là ngầm RONIC > Ke, một mức thưởng kiểu WIDE. Hai nhánh XẤU (7,85%) và TRUNG LẬP (11,84%) đã ở g_RI = 0.
2. **ROE terminal so với TB chu kỳ ngành:** ROE_T nhánh TỐT 14,25% cao hơn mọi neo peer dựng lại ở dưới (7,1–9,8%).
- **Neo TB chu kỳ ngành — DỰNG LẠI (r2):** r1 dùng trường vendor `ROE10Y` (trung vị 12,4% / TB 11,6%), nhưng trường này **không khớp ROE năm quan sát được**: SMC ROE10Y 11,2% trong khi TB ROE năm 2016–25 chỉ 5,8%; GDA ROE10Y 15,9% trong khi chỉ có 3 năm quan sát 7,0–9,0%. r2 lấy **ROE năm** = `ROE_Trailing` dòng Q4 (2016–2025, 10 năm; khớp ROE năm HPG đã trích ở §2). TB 10 năm từng peer: HSG 15,7 · NKG 15,6 · VGS 12,1 · SMC 5,8 · TLH 5,1 · TVN 4,6%. **GDA bị loại** (chỉ 3 năm, TB 7,9%; tính vào thì neo 9,54%). ⇒ Neo = **trung vị-của-TB 8,91%** / **TB-của-TB 9,80%** (trung vị-của-trung vị 7,05%, nhạy với năm lỗ). Peer **nội địa nhưng không cùng mô hình** (tôn mạ/thương mại/EAF; Formosa Hà Tĩnh không niêm yết); POM loại vì ROE phi lý.
- **Bản CHẶT-3C (headline, quy ước chờ Mike/user duyệt):** RONIC = Ke đối xứng (g_RI = 0 mọi nhánh) + ROE_T **hồi về neo ngành ở cả hai phía** (REV). Ở chế độ REV, ROE_T được **thay thẳng bằng ROE sau thuế THỰC của peer** (`hpg_5f_r2.py` nhánh `REV`), **không** áp thuế terminal 20% (TAXF) như CUR/SYM. Câu "giữ thuế 20% terminal" ở r1 là sai, đã rút. Rủi ro ưu đãi thuế DQ2 vì thế đã nằm ngầm trong ROE peer (thuế suất thực của peer), không đếm thêm. Trục TLSH, năm 1 = 0,25 năm (Q4/26) và ROLL tới 04/11 giữ đúng r2.
- Đường LN 2027–29 (ROE TRUNG LẬP 2027 ≈ 17,5% > Ke) là dự báo 3 năm hữu hạn, neo vào run-rate 9T26, không phải giả định moat ⇒ giữ nguyên.

## 4. Kết quả (sau CK @5 tỷ; nhãn ở 5 tỷ = 10 tr = 40 tr, giống nhau ở mọi dòng)
| Bản | Tâm | P10 | P50 | P90 | Giá/P90 − 1 | Nhãn |
|---|---|---|---|---|---|---|
| Hiện hành r2 (CUR) | 16.286 | 8.942 | 16.343 | 23.520 | −7,7% | TRONG |
| Chỉ RONIC = Ke đối xứng (SYM) | 16.016 | 8.942 | 16.343 | 22.321 | −2,8% | TRONG |
| **CHẶT-3C, neo trung vị-của-TB 8,91%** | **12.580** | **10.576** | **12.655** | **14.512** | +49,5% | **TRÊN** |
| **CHẶT-3C, neo TB-của-TB 9,80%** | **13.705** | **11.601** | **13.791** | **15.737** | +37,9% | **TRÊN** |
| *(r1, neo vendor 12,4% / 11,6% — rút)* | *16.986 / 15.962* | | | *19.395 / 18.241* | | *TRÊN* |

Tái lập kiểm của skeptic: neo 9,5% → 13.320 (skeptic 13.371), 7,9% → 11.298 (skeptic 11.336), 13,5% → 18.376 (khớp). Chênh nhỏ ở 2 neo đầu nhiều khả năng do skeptic làm tròn neo (neo 9,54% có GDA → 13.367). Cả 3 điểm đều TRÊN vùng.
**Phần chênh CUR → neo 9,80%:** kênh RONIC −270 (CUR→SYM). Kênh ROE hồi về neo −2.311 (SYM→REV): nhánh TRUNG LẬP/TỐT bị kéo xuống, P90 −6.584. Nhánh XẤU kéo lên nhẹ, P10 +2.659.

## 5. Độ nhạy — nhãn PHỤ THUỘC HOÀN TOÀN vào neo terminal
Ở r1 tôi viết "không phải ca ranh giới". Câu đó **mâu thuẫn** với chính đoạn r1 nói neo ROE5Y HPG cho nhãn TRONG, nên đã **rút**. Lưới neo (REV, RONIC = Ke, 5 tỷ):

| Neo ROE terminal | Tâm | P10–P90 | Nhãn |
|---|---|---|---|
| 7,05% peer trung vị-của-trung vị | 10.228 | 8.516–11.871 | TRÊN |
| 7,9% | 11.298 | 9.416–13.097 | TRÊN |
| **8,91% peer trung vị-của-TB** | **12.580** | 10.576–14.512 | **TRÊN** |
| 9,5% / 9,54% (có GDA) | 13.320 / 13.367 | 11.257–15.318 / 11.301–15.369 | TRÊN |
| 9,64% HPG TB 2022–25 | 13.492 | 11.417–15.505 | TRÊN |
| **9,80% peer TB-của-TB** | **13.705** | 11.601–15.737 | **TRÊN** |
| 11,6% / 12,4% (vendor r1, rút) | 15.962 / 16.986 | 13.560–18.241 / 14.448–19.395 | TRÊN |
| 13,5% = Ke | 18.376 | 15.654–20.916 | TRÊN (giá > P90 3,7%) |
| **14,07% = điểm hoà vốn nhãn** (P90 = 21.700) | — | — | ranh giới |
| 15,36% HPG ROE5Y vendor × thuế | 20.732 | 17.703–23.492 | TRONG |
| 21,43% HPG TB ROE năm 2016–25 | 28.404 | 24.415–32.074 | DƯỚI |

⇒ Nhãn đổi TRÊN → TRONG khi neo vượt **14,07%** (> Ke). Mọi neo ngành quan sát được (7–10%) đều cho TRÊN với biên rộng (giá cao hơn P90 38–50%). Chỉ neo vào **chính lịch sử HPG** (ROE5Y hay TB 10 năm, gồm cả 2016–21 bảo hộ/siêu chu kỳ) mới cho TRONG/DƯỚI. Neo vào lịch sử HPG tức là coi ưu thế của HPG là bền, trái kết luận "không bền" ở §2. Chọn neo là quyết định quy ước của Mike/user.

**Độ nhạy theo moat, và tính đơn điệu (theo skeptic):**
| Giả định | Quy tắc | Tâm | P10–P90 | Nhãn |
|---|---|---|---|---|
| WIDE | ROE_T ≥ 15,36%, g_RI = g (RONIC > Ke) | 22.133 | 18.331–25.154 | TRONG |
| NARROW, CHẶT-3C | REV neo 8,91–9,80% | 12.580–13.705 | 10.576–15.737 | TRÊN |
| NARROW, **không phạt DQ2 (a)** sàn | REVF: chênh (neo − Ke) sàn 0, mọi vốn terminal sinh lời đúng Ke | 18.376 | 15.654–20.916 | TRÊN (giá > P90 3,7%) |
| NARROW, **không phạt DQ2 (b)** chỉ XDCB | REVD: XDCB 16.113 tỷ sinh lời = Ke, phần vốn còn lại theo neo | 13.014–14.055 | 11.010–16.087 | TRÊN |
| NONE | spread (ROE_T − r) fade tuyến tính về 0 trong 5 năm, hai chiều | 17.656 | 13.625–21.204 | TRÊN (giá > P90 2,3%) |

**Không đơn điệu, nêu thẳng:** NONE (17.656) > NARROW chặt (12.580–13.705). Lý do là bản NARROW chặt **ghim ROE dưới Ke vĩnh viễn trên toàn bộ vốn chủ**, kể cả vốn DQ2 đã vào sổ. Điều này phạt ngầm vốn DQ2, trái tinh thần luật 20 (base dự án mới = sổ sách/NPV 0). NONE thì cho spread âm tắt dần về 0 sau 5 năm. Biến thể (a) bỏ hoàn toàn phần phạt, tâm 18.376 ≥ NONE nên thứ tự đơn điệu được khôi phục (WIDE > NARROW-sàn ≥ NONE). Biến thể (b) chỉ miễn phạt phần XDCB đang dở dang, tâm +434…+350. **Ở mọi biến thể nhãn vẫn TRÊN**; (a) và NONE là các ca sát ranh giới nhất (giá > P90 2,3–3,7%).

## 6. Thay đổi so với báo cáo hiện hành
Moat NARROW không bền ⇒ **không thưởng**. Mô hình r2 **có** thưởng ngầm (RONIC > Ke ở nhánh TỐT; ROE_T nhánh TỐT 14,25% cao hơn mọi neo ngành) nên không ghi "nhất quán". Theo luật 3c (CHẶT-3C, neo ROE năm quan sát), tâm **12.580–13.705** (so với 16.286, đổi −22,8% … −15,8%), P10 **10.576–11.601** (8.942), P50 **12.655–13.791** (16.343), P90 **14.512–15.737** (23.520), nhãn **TRONG → TRÊN vùng** ở mọi cỡ lệnh. Nếu bỏ phạt DQ2 (biến thể a) thì tâm 18.376, nhãn vẫn TRÊN. Nhãn chỉ quay về TRONG khi neo ≥ 14,07%. So với r1 (tâm 15.956–16.986), con số giảm thêm vì neo vendor ROE10Y đã được thay bằng ROE năm quan sát. Đây là quy ước chờ Mike/user duyệt. KHÔNG sửa REPORT_r2/SUMMARY.json/dd_price_zones.

## 7. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
HPG,NARROW,COST/SCALE,L,"Integrated BF-BOF scale/cost leader (GPM top of listed VN steel 10/11 yrs 2015-25, 10y avg 19.2% vs peer median 5.7%) BUT absolute excess return not multi-cycle (ROIC_Min5Y 5.7%, ROIC10Y 13.0% <= Ke 13.5%; ROE 2022-25 6.8-12.4%, partly depressed by DQ2 CWIP); #1 risk: margin leans on time-limited AD protection vs Chinese HRC oversupply (anti-circumvention QD 1917 27.83% eff 2026-07-28 - press-reported only, moit.gov.vn original not yet opened, covers HRC width 1880-2300mm only) while DQ2 capex concentrated; DQ2 tax incentive unresolved (CV 377)",2026-11-07,5f,N
```
entry = L vì ngành thép commodity kém hấp dẫn cấu trúc (`moat_5f.py`: entry = độ hấp dẫn ngành); moat_upgrade = N.
