> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành (đồng bộ r3 08/11: tâm 15.911, P10 13.315, P50 15.919, P90 18.573, nhãn TRONG vùng, giá 15.200 ngày 06/11, CK 5 tỷ 1,47%; theo `REPORT_r3.md`; 13.109 là tâm r2 cũ, chỉ còn là mốc so sánh)**; mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.
>
> **Ghi chú đồng bộ r3 (08/11, job `Taylor_20261108_153738`):** mọi con số tâm/P10/P90 trong các bảng bên dưới (hiện hành r2 13.109, chặt-3C LAS/NFC 12.662–14.923, dải +DHB, WIDE 13.390…) được tính trên mô hình r2 (tiền ròng chuẩn hoá 869,1, hệ số giữa chu kỳ Bobby, RONIC 20%, DT 5.500, trừ lãi 55,6) và chỉ là độ nhạy tương đối quanh r2, KHÔNG phải tâm hiện hành. r3 đã đưa RONIC = Ke vào base (TOP5B #3) ⇒ kênh thưởng moat ngầm ở §2 không còn trong headline; biên vẫn là biên chu kỳ riêng DDV 4,05% (≈ peer phốt-phát LAS/NFC 4,16%). Tâm hiện hành = r3 15.911.

# DDV — ADDENDUM 5F (bước 3c) · r2 08/11/2026 · job `Taylor_20261108_024219` (sửa sau skeptic; r1 = `ADDENDUM_5F_r1.md`, job `Taylor_20261107_172007`)

> NGHIÊN CỨU nội bộ. r1 đã qua skeptic (Mike 08/11: moat NONE + RONIC=Ke ĐỨNG, nhãn TRONG→TRÊN KHÔNG đứng); r2 này CHƯA re-skeptic. KHÔNG sửa `REPORT_r2.md` / `SUMMARY.json` / `dd_price_zones`. 5F từ LLM-knowledge + BCTC/BQ = non-point-in-time ⇒ chỉ cho DD sống, không backtest.
> Số r2: `5F/ddv_moat_sens_r2.py` → `5F/ddv_moat_sens_r2_out.{json,txt}` (chạy 2 lần trùng byte, `cmp`; md5 json `914f2a72…`, txt `1d4bafb0…`); peer BQ `calc5f/peer_r2.sql` (= `peer.sql` + DHB) → `calc5f/peer_r2_out.csv` (`ticker_financial`, 2015–2025; bỏ DHB thì trùng `peer_out.csv` từng dòng, `diff`). Script r1 `5F/ddv_moat_sens.py` giữ nguyên. Model gốc `calc/model.py`+`model_r2.py` import, không sửa.
> Quy ước BQ: NP_P0/Revenue_P0 là số QUÝ (cộng 4 quý = năm, chỉ lấy năm đủ 4 quý); GPM_P0 là TTM ⇒ dòng Q4 = GPM năm; ROIC_xY lấy dòng 2025Q4 (= số FY2025). ROIC so với WACC/r 13,5% (`common_r2.C.r_now()`, mô hình dùng một suất chiết khấu cho cả Ke lẫn WACC vì DDV tiền ròng dương).

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

**Ba điều kiện moat bền** (WACC ≈ Ke = r = 13,5%, DDV tiền ròng dương, `common_r2.C.r_now()`; ROIC/ROE dòng 2025Q4 BQ):
| | DDV | Đối chiếu | Kết |
|---|---|---|---|
| (i) siêu ngạch nhiều chu kỳ | ROIC_Min5Y **2,2%**, ROIC5Y **14,4%**, ROIC10Y **8,3%**, ROIC_Min10Y **−10,0%** · ROE5Y 16,2%, ROE_Min5Y 4,0% (ROE ghi riêng, không thay ROIC) | ROIC5Y > WACC chỉ +0,9pp và nhờ đỉnh 2021–22; ROIC10Y < WACC 5,2pp; Min5Y/Min10Y ≪ WACC | ✗ |
| (ii) cơ chế rào cản gọi tên được | Quy mô 28% thị phần không chuyển thành chi phí thấp (GPM < peer phosphate) | — | ✗ |
| (iii) không có đồng hồ cắt hào | Bãi thạch cao + giá chuyển giao apatit + thoái vốn | — | ✗ |

**moat_tier = NONE · moat_type = NONE · rủi ro số 1:** spread DAP − (S+NH3+apatit) do giá thế giới quyết định, DDV price-taker cả hai đầu (apatit qua bên liên quan); phụ: bãi thạch cao chặn công suất. Không có cờ vụ án (REPORT_r2 §5) ⇒ không có giảm trừ pháp lý để tránh đếm hai lần.

## 2. Moat trong mô hình — **KHÔNG nhất quán với NONE** ⇒ báo bản CHẶT-3C
Mô hình r2 đang chứa 2 kênh thưởng ngầm (kiểm theo bài học C):
- **RONIC 20% > Ke 13,5%** (`model.py` `RONIC`), áp cả f27 lẫn terminal ⇒ tái đầu tư tạo giá trị — trái luật NONE.
- **Biên LN ròng giữa chu kỳ = TB riêng DDV 2015–25 = 4,05%** (`NPM_CYCLE`) giữ tới terminal, không phải TB ngành.

Bản CHẶT-3C: RONIC = Ke **đối xứng mọi ô lưới** (cả f27 và terminal) + NPM giữa chu kỳ = biên chu kỳ NGÀNH (NP/DT gộp các năm đủ 4 quý 2015–25, BQ).

**Sửa r2 — 2 lỗi skeptic chỉ ra (r1 đã sai):**
1. **Peer cắt một chiều.** r1 lấy headline "bỏ urê" (chỉ bỏ DPM/DCM) nhưng giữ BFC/SFG/VAF — NPK pha trộn, không phải SX DAP/phốt-phát — trong khi chính §1 dùng LAS/NFC làm "peer phốt-phát". r2: **headline = peer phốt-phát LAS + NFC** (NPM 3,50% / 4,81% ⇒ TB = trung vị 4,16%); dải phụ thêm **DHB** theo đề nghị skeptic (Đạm Hà Bắc — theo hiểu biết là urê từ than, không phải phốt-phát, **cần kiểm chứng** ⇒ chỉ vào dải, không vào headline; biên đo được 0,71% gộp 2018–25 — gồm quý 2023Q4 lãi bất thường 1.649 tỷ > DT quý; bỏ quý đó −4,44%). *Đính chính số skeptic:* NPM gộp DHB đo lại = +0,71% (không phải −0,16%); trung vị {LAS, NFC, DHB} = 3,50% (không phải 4,15%). Bộ "bỏ urê 5 mã" r1 hạ xuống độ nhạy.
2. **Trộn biên tổng/vận hành.** `mid = NPM × REV_NORM − INT_AT_NORM`: INT_AT_NORM (55,6 tỷ = 1,01% DT, lãi tiền gửi sau thuế của DDV) được trừ vì NPM *của DDV* đã gồm lãi đó và tiền ròng cộng riêng (NC_NORM). Cắm NPM *peer* (đã gồm thu nhập TC ròng của peer, không phải của DDV) rồi vẫn trừ INT_AT_NORM là trừ một khoản không có trong biên ⇒ đếm thiếu. Không có thu nhập TC từng peer trong `ticker_financial` để quy về biên vận hành chính xác ⇒ báo **2 cơ sở làm dải**: `int` (vẫn trừ — cận bảo thủ, đúng nếu peer có thu nhập TC ròng ≈ DDV) và `noint` (không trừ — đúng nếu thu nhập TC ròng peer ≈ 0).

Quy ước số mũ chiết khấu (0,125/0,75/1,25 năm) giữ nguyên model r2 — bản CURRENT tái lập đúng REPORT_r2 (13.109 / 10.115 / 12.823 / 16.270).

## 3. Kết quả (sau CK 5 tỷ 1,45%; giá 15.200 ngày 04/11/2026)
| Bản | NPM giữa CK | RONIC | Trừ INT | Tâm | P10 / P50 / P90 | P90 vs giá | Nhãn 5 tỷ | Nhãn 40tr |
|---|---|---|---|---|---|---|---|---|
| Hiện hành r2 | 4,05% (DDV) | 20% | có | 13.109 | 10.115 / 12.823 / 16.270 | +7,0% | TRONG | TRONG |
| Chỉ RONIC=Ke | 4,05% (DDV) | Ke | có | 12.430 | 9.612 / 12.221 / 15.417 | +1,4% | TRONG | TRONG |
| Độ nhạy chặt-3C (r2, không phải headline) · LAS/NFC · `int` | 4,16% | Ke | có | **12.662** | 9.785 / 12.422 / 15.731 | **+3,5%** | **TRONG (sát cạnh trên)** | TRONG |
| Độ nhạy chặt-3C (r2, không phải headline) · LAS/NFC · `noint` | 4,16% | Ke | không | **14.923** | 11.417 / 14.632 / 18.542 | +22,0% | TRONG | TRONG |
| Dải +DHB, trung vị · `int` | 3,50% | Ke | có | 11.187 | 8.669 / 11.111 / 13.847 | −8,9% | TRÊN | TRÊN |
| Dải +DHB, trung vị · `noint` | 3,50% | Ke | không | 13.448 | 10.369 / 13.118 / 16.618 | +9,3% | TRONG | TRONG |
| Dải +DHB, TB · `int` | 3,01% | Ke | có | 10.091 | 7.804 / 10.047 / 12.430 | −18,2% | TRÊN | TRÊN |
| Dải +DHB, TB · `noint` | 3,01% | Ke | không | 12.352 | 9.554 / 12.151 / 15.311 | +0,7% | TRONG (ranh giới) | TRONG |

Tách phần chênh headline `int` so với r2: RONIC 20%→Ke **−679** đ/cp; biên DDV 4,05%→LAS/NFC 4,16% **+232** ⇒ tổng **−447 (−3,4%)**. Biên DDV ≈ biên phốt-phát (chênh 0,10pp) ⇒ phần lệch luật 3c thực chất chỉ nằm ở kênh RONIC. Bỏ trừ INT (`noint`) cộng **+2.261** — đây là trục bất định lớn nhất của bản headline, lớn hơn cả kênh RONIC.

## 4. Độ nhạy (peer set · cơ sở biên · moat sai)
| Giả định | Tâm | P90 | Nhãn 5 tỷ | Δ tâm vs r2 |
|---|---|---|---|---|
| WIDE giả định (RONIC 25%, biên DDV) | 13.390 | 16.646 | TRONG | +281 (+2,1%) |
| NARROW ≈ hiện hành (RONIC 20%, biên DDV) | 13.109 | 16.270 | TRONG | 0 |
| **NONE headline LAS/NFC** (`int`…`noint`) | **12.662–14.923** | 15.731–18.542 | TRONG | −447…+1.814 |
| NONE dải +DHB (trung vị/TB, `int`…`noint`) | 10.091–13.448 | 12.430–16.618 | TRÊN ở `int`, TRONG ở `noint` | −3.018…+339 |
| *(độ nhạy, r1 headline cũ)* bỏ urê 5 mã trung vị / TB, `int` | 11.187 / 11.937 | 13.847 / 14.814 | TRÊN | −1.922 / −1.172 |
| *(độ nhạy)* bỏ urê 5 mã trung vị / TB, `noint` | 13.448 / 14.198 | 16.618 / 17.602 | TRONG | +339 / +1.089 |
| *(độ nhạy)* đủ 7 peer gồm urê, trung vị / TB, `int` | 14.136 / 17.738 | 17.519 / 22.133 | TRONG | +1.027 / +4.629 |
Giá trị DDV kém nhạy với RONIC (+281/−679) vì g 3% nhỏ; nhạy nhất là **cơ sở biên (trừ INT hay không, ±2.261)** rồi tới **có tính DHB không**. Nhãn TRÊN chỉ xuất hiện khi đồng thời (a) đưa DHB/NPK pha trộn vào peer VÀ (b) trừ INT trên NPM peer — tức chồng đúng hai lỗi r1.

## 5. Thay đổi so với báo cáo hiện hành
Mô hình r2 **lệch luật 3c** (RONIC 20% + biên riêng DDV cho mã moat NONE), nhưng lệch nhỏ: biên DDV ≈ biên peer phốt-phát. Bản chặt-3C (RONIC=Ke đối xứng, peer LAS/NFC; **độ nhạy r2, KHÔNG phải headline — headline = r3 15.911**): **tâm 13.109 → 12.662 (`int`, −3,4%)**, cận lạc quan 14.923 (`noint`); lõi tâm các bản RONIC=Ke có cơ sở hợp lý **~12,4–13,4k** (12.430 biên DDV · 12.662 LAS/NFC `int` · 13.448 +DHB trung vị `noint`). P90 của bản độ nhạy này 15.731 = giá +3,5% ⇒ (trong bản độ nhạy r2) nhãn TRONG giữ, sát cạnh trên (5 tỷ và 40tr). **r1 rút lại nhãn TRÊN** — nó dựa trên bộ peer cắt một chiều + trừ INT trên NPM peer. Dải gồm DHB ở cơ sở `int` cho TRÊN (tâm 10.091–11.187) ⇒ nhãn không vững ở cạnh trên: giá chỉ cần +3,5% là sang TRÊN. Quy ước (peer set, cơ sở biên) chờ Mike/user duyệt. Không ghi SUMMARY.json/zones. Sleeve fear-buy §2.5 vẫn KHÔNG đủ điều kiện (REPORT_r2 §8) — #3 "leader chi phí" ✗ có số (GPM DDV TB 10,6% < LAS 17,7%/NFC 16,6%; DHB 11,6%).

## 6. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
DDV,NONE,NONE,L,"Price-taker spread DAP-(S+NH3+apatite): ~80% COGS inputs, S 100% imported, apatite from related-party Apatit VN (Vinachem transfer price); ROIC10Y 8.3%/ROIC_Min5Y 2.2% < WACC 13.5%; GPM 2015-25 avg 10.6% below phosphate peers (LAS 17.7/NFC 16.6); gypsum-stack (Dinh Vu) caps capacity; 28% DAP share not a cost moat",2026-11-07,5f,N
```
entry = L (ngành phân bón phosphate hàng hoá, quyền lực NCC cao, giá thế giới — kém hấp dẫn cấu trúc, theo `moat_5f.py` schema). moat_upgrade = N.
