> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành, đồng bộ `REPORT_r3.md` (vòng 3, giá 06/11 13.100, cỡ CK 5 tỷ): tâm 15.257; P10 12.908; P50 15.293; P90 17.549; nhãn TRONG vùng (sát cạnh dưới)** (14.092 là số r2 đã bị thay; mọi con số 14.092/12.006/16.146 và bảng §3 bên dưới là số r2, chỉ giữ làm đối chiếu lịch sử; độ nhạy moat trên base r3 ở §0); mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.

# DRI — ADDENDUM bước 3c: 5F tầng (b) + moat trong mô hình (5F-r3 07/11/2026; đồng bộ DD r3 08/11/2026 ở §0, job Taylor_20261107_124448; bản cũ: `ADDENDUM_5F_r1.md`, `ADDENDUM_5F_r2.md`)

## 0. Đồng bộ vòng 3 (08/11/2026, job Taylor_20261108_153743)
Base hiện hành = `REPORT_r3.md`. Độ nhạy moat chạy lại trên base r3: `calc_5f/moat_sens_5f_r3_out.txt` (`$DNA_PYEXE -B moat_sens_5f_r3.py`, 2 lần trùng md5 `9af83adf…`). Gap GPM giữ nguyên (trung vị 11,70pp; assert); 54 kết cục; giá 13.100; CK 5 tỷ.

| Bản (r3) | Cref | Tâm | Δ | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **Headline r3 (không thưởng, không trừ moat)** | 30,22 | **15.257** | 0 | 12.908 / 15.293 / 17.549 | 12,5% | TRONG |
| NONE½ — độ nhạy rủi ro | 33,03 | 13.640 | −1.618 (−10,6%) | 11.481 / 13.631 / 15.757 | 39,1% | TRONG |
| NONE (trung vị 3 peer 11,70pp) — độ nhạy rủi ro | 35,84 | 12.022 | −3.235 (−21,2%) | 9.742 / 12.099 / 14.050 | 74,2% | TRONG |
| NONE TB 3 peer / +TRC trung vị / +TRC TB / DPR một mình | 35,46 / 35,92 / 35,56 / 33,79 | 12.245 / 11.978 / 12.187 / 13.202 | | | 71,1 / 77,3 / 71,1 / 41,4% | TRONG cả 4 |

Theo quy ước cuối 08/11, các bản NONE là kịch bản "nếu biên về trung bình ngành", không phải kết luận. Bản WIDE không chạy lại vì không có moat bền. Ở giá 13.100, mọi bản NONE đều TRONG vùng (r2 @13.500: NONE là TRÊN vùng; đổi vì giá thấp hơn và base r3 cao hơn).

---
*(Phần dưới: bản r3-5F 07/11 trên base r2, giữ làm lịch sử.)*

Bổ sung cho `REPORT_r2.md` (05/11). Giá trị mô hình **lúc đó** (r2, nay đã thay bằng r3): tâm 14.092 / P10 12.006 / P50 14.235 / P90 16.146 sau CK, TRONG vùng, **nhưng r1 viết sai "nhất quán với 3c" — r2/r3 giữ đính chính: mô hình hiện hành LỆCH luật 3c (xem §2), kèm bản chặt-3c song song, chờ Mike/user duyệt.** r3 chỉ hoàn lại phép đo GPM: `GPM_P0` BQ là số TTM (dòng Q4 = GPM cả năm) nên dùng thẳng, bỏ "TTM trọng số tự tính" của r2. Số: `calc_5f/moat_sens_5f_out.txt` (`$DNA_PYEXE -B moat_sens_5f.py`, 2 lần trùng md5 `b8792326…`; chân đối chứng assert = pin r2 14.092; `calc/` không bị ghi).

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Tái dùng** tag `data/moat_tags.csv` dòng DRI: **NARROW · LOCATION/COST**, asof **2026-06-05**, src `5f_cyclical` (5 tháng < 12 tháng ⇒ không làm lại, theo luật tần suất 06/11). Dưới đây là kiểm nhanh bằng số đang có.

**Loại hình DN:** nhà sản xuất hàng hoá (mủ cao su, đồn điền tô nhượng tại Lào), **chấp nhận giá** (price-taker), lợi nhuận theo chu kỳ giá RSS3/SGX.

| Lực | Đánh giá (số + nguồn) |
|---|---|
| Cạnh tranh trong ngành | Hàng hoá đồng nhất, giá theo thị trường thế giới; DRI KH 2026 13.800 t (BCTN25 tr.46), quy mô nhỏ ⇒ không có quyền định giá. Mạnh. |
| Người mua | Bán mủ theo giá thị trường; **tập trung khách hàng: cần kiểm chứng** (thư mục không có số). |
| Đầu vào/nhà cung cấp | Tự chủ đất + vườn (tô nhượng Lào). Giá thành Cref **30,22 tr/t** (hiệu chỉnh từ LN 2025 của DRI) so giá TB chu kỳ **48,06 tr/t** (engine r4). **GPM năm (BQ `GPM_P0` tại dòng Q4 = TTM 4 quý = cả năm, dùng thẳng) TB 2017–25: DRI 36,9% vs trung vị peer DPR/PHR/GVR 25,2% (+11,70pp; DRI > peer 9/9 năm)** — BQ `ticker_financial` GPM_P0, `calc_5f/ttm_bq.csv`. (Cách tính: mỗi năm lấy GPM_P0 dòng Q4 của DRI và trung vị GPM_P0 Q4 của các peer có mặt, hiệu số rồi TB 9 năm. r1 gọi "quý Q4" — sai nhãn, GPM_P0 là TTM; r2 thay bằng TTM tự tính trọng số — thừa và sai vì GPM_Pi đã là TTM chồng lấn; r3 hoàn về GPM_P0 Q4. Biên QUÝ thật cần BCTC, không lấy từ GPM_P0. 2026Q3 GPM_P0 ≈ 2026Q2 (0,39241 vs 0,39242) nghi chép đè ⇒ không dùng.) GVR thiếu dữ liệu 2017 (peer 2017 chỉ DPR/PHR). **Peer:** DPR/PHR/GVR là đối thủ cao su nội địa; TRC (cùng ngành) r1 loại không có lý do mạnh ⇒ đưa vào như bản nhạy: gap **trung vị 11,70 / TB 10,89 / +TRC trung vị 11,85 / +TRC TB 11,10 / DPR một mình 7,43pp (DRI>DPR 8/9 năm)**. Lưu ý so sánh: PHR/GVR có mảng KCN/gỗ, biên peer không thuần cao su. |
| Gia nhập mới | Rào cản = đất + 7 năm kiến thiết cơ bản (KTCB=7, engine) + vốn tái canh (PV capex tái canh tại điểm TB/L27 **2.764 đ/cp**). Rào cản chặn người mới về đất, nhưng không chặn cạnh tranh giá toàn cầu. |
| Sản phẩm thay thế | Cao su tổng hợp (theo giá dầu); **độ co giãn thay thế: cần kiểm chứng**. |
| **Lực thứ 6 (đồng hồ cắt hào)** | (a) Tô nhượng Lào — mốc **2054 = END của engine, văn bản chưa công khai ⇒ cần kiểm chứng** (không đánh ✔); mô hình cho giá trị về 0 sau 2054 (L0); (b) **NQ HĐQT 15**: thanh lý **1.975,23 ha (≈24% diện tích cạo)** 2027–30; (c) một phần đất trong quy hoạch rừng bảo tồn; (d) rò rỉ chuyển tiền/thuế Lào (KTPL 10,6%, w 10%, quỹ dự phòng 7,8% LNST). |

**Lợi nhuận siêu ngạch qua chu kỳ (Ke = r 13,5%):** ROE theo năm (ROE_Trailing, dòng Q4) 2018–2022 **6,0 / 4,6 / 3,4 / 10,0 / 9,7%** — dưới Ke 5 năm liền; 2023–25 13,8 / 19,6 / 23,3% (đỉnh giá). ROE_Min5Y **10,7%** < Ke; ROE5Y 15,8%. ROIC_Min5Y 16,8% (thuận) nhưng ROIC_Min10Y **6,5%** < Ke (ngược); ROIC5Y 19,5% (đỉnh gần đây). ROIC_Trailing ở dòng Q4 2021–25 ra **76–143%** ⇒ trường self-calc không tin cậy cho DRI, không dùng.

**Kết luận:** **moat_tier NARROW · moat_type LOCATION/COST (giữ nguyên tag 06/2026)**. Lợi thế giá thành có thật và lặp lại (+11,70pp GPM năm, 9/9 năm), nhưng không thành lợi nhuận vượt Ke qua đáy chu kỳ. **Rủi ro số 1:** giá cao su (price-taker) — tag 06/2026 ghi "đỉnh"; tới 11/2026 đã qua đỉnh (LNST mẹ Q3 −33% YoY, REPORT_Q3_UPDATE). Rủi ro số 2 là đồng hồ đất (NQ15 + tô nhượng). **Kiểm nhanh có gì đổi hào từ 06/2026:** NQ15 làm quỹ đất co ≈24% (hào hẹp đi, không rộng ra); vụ Dakruco/bên liên quan là rủi ro quản trị, không phải hào. Tier không đổi.

## 2. Moat trong mô hình — SỬA r2
Ba điều kiện bền: (i) **TRƯỢT** (ROE<Ke 2018–22; ROE_Min5Y, ROIC_Min10Y<Ke); (ii) cơ chế gọi tên được — có một phần (đất + giá thành, chỉ phía chi phí); (iii) **TRƯỢT** (2054 chưa kiểm chứng, NQ15, rừng bảo tồn) ⇒ **moat_durable=false ⇒ luật 3c: RONIC=Ke VÀ biên về TB chu kỳ NGÀNH.**

**Kiểm mô hình hiện hành (r1 bỏ sót):** RONIC=Ke ✔ (nhánh NPV0), giá mủ mid=TB chu kỳ ✔, L0 sau 2054 ✔, **nhưng biên KHÔNG về TB ngành**: Cref giữ 30,22 tr/t tới 2054 (hiệu chỉnh từ LN 2025 đỉnh của chính DRI) ⇒ GPM mô hình tại giá TB ≈ **36,1%** (peer ~25,2%); LNST giữa chu kỳ (giá TB, 13.800 t) **≈151,9 tỷ** ⇒ **ROE giữa chu kỳ ≈ 18,9–20,7% > Ke 13,5%** (VCSH 2026Q2 805 / Q3 735 tỷ) — trái (i) mà tự chấm trượt, trái ADDENDUM r1 "lợi thế đã nằm trong biên". Tính này là mô hình hiện hành NGẦM thưởng moat bền. (Skeptic nêu LNST mid 163,6 tỷ — spec khác, không tái hiện; kết luận cùng chiều.) Đồng hồ cắt hào (2054/NQ15) chỉ cắt đuôi, không hạ biên.

**Hai cách xử lý (LỊCH SỬ r2 — ĐÃ CHỐT 08/11: user chọn KHÔNG áp 3c chặt; mục (b) chỉ còn là độ nhạy rủi ro, xem đầu file):**
(a) **Ngoại lệ 3c tường minh** — lợi thế đất/vườn Lào, đối thủ không vào được. Bằng chứng cơ cấu giá thành vs peer (năng suất t/ha, nhân công, thuê đất): **cần kiểm chứng** (thư mục chỉ có năng suất DRI 1,69 t/ha KH2026 BCTN25; không có số peer). **Lệch luật 3c** ⇒ chưa đủ cơ sở (đã giải quyết bằng quy ước cuối 08/11, không còn chờ).
(b) **Chặt-3c**: fade chênh biên về TB ngành (bảng §3). Bản này mô tả đúng luật nhưng là quy ước đề xuất ở r2, **nay chỉ còn là độ nhạy rủi ro** (không phải headline).

## 3. Độ nhạy — BASE r2, LỊCH SỬ (lưới 36 kết cục, sau CK 5 tỷ, giá 13.500; Cref chặt = 30,22 + gap×48,06; gap từ GPM_P0 Q4)
| Bản | Cref | Tâm | Δ | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| r2 lúc đó (ngầm moat) | 30,22 | 14.092 | 0 | 12.006 / 14.235 / 16.146 | 35,2% | TRONG |
| **NONE½** (fade nửa gap) | 33,03 | 12.488 | −1.604 (−11,4%) | 10.439 / 12.759 / 14.491 | 78,8% | TRONG |
| **NONE chặt** (gap trung vị 11,70pp) | 35,84 | **10.883** | −3.209 (−22,8%) | 8.894 / 11.148 / 12.942 | 98,0% | **TRÊN** vùng |
| NONE đối xứng (NONE + bỏ nhánh KINH TẾ, RONIC=Ke cả hai phía) | 35,84 | 11.188 | −2.905 (−20,6%) | 8.957 / 11.318 / 13.113 | 97,5% | TRÊN |
| WIDE [UL minh hoạ] n=18 | 30,22 | 14.965 | +873 (+6,2%) | 12.817 / 15.055 / 16.957 | 17,5% | TRONG |
| — trong đó chỉ bỏ nhánh KINH TẾ (S=0) | 30,22 | 14.288 | +196 | 12.140 / 14.378 / 16.280 | 30,0% | TRONG |

- **Tách RONIC vs biên:** nhánh NPV0 sẵn RONIC=Ke; phần chênh −3.209 là hoàn toàn từ biên (Cref). Bỏ thêm nhánh KINH TẾ (đối xứng) cộng +305 ⇒ nhánh KINH TẾ là đuôi dưới, không phải kênh moat.
- **Độ nhạy cách chọn peer (NONE, tâm):** trung vị 3 peer 10.883 · TB 3 peer (10,89pp) 11.105 · +TRC trung vị (11,85pp) 10.840 · +TRC TB (11,10pp) 11.047 · **DPR một mình (7,43pp) 12.054 (−14,5%, TRONG vùng, 83,8% dưới giá)**. Khoảng NONE: **10.840–12.054**; nhãn TRÊN ở mọi bản nhiều peer, TRONG nếu chỉ lấy DPR ⇒ nhãn nhạy peer, ghi **ranh giới** giữa NONE½ và NONE.
- **Cỡ sleeve thật** (10–40 triệu; CK 0,09–0,18% thay 2,00%): P90 NONE tăng ≈ +1,9% ⇒ ≈13,19k (**ước lượng**, chưa chạy lại) vẫn < giá 13.500 ⇒ nhãn TRÊN không đổi.
- **WIDE:** +873 gồm ≈+196 do chỉ bỏ nhánh KINH TẾ (REPORT_r2 §37), phần moat thật ≈ **+677 (+4,8%)**; S=0,25 là giả định, không dẫn chứng peer; WIDE không có cơ sở (n=18, không còn "cùng lưới 36 kết cục").
- Quy ước hiện: không dùng năm đỉnh cho giá; vụ Dakruco là WARNING, không dùng ép biên (đã không dùng); giảm trừ pháp lý trong base giữ như REPORT_r2 — không đếm hai lần. Chiết khấu: engine r4 dùng T27=0,67 năm cho dòng 2027 (quy ước năm 1 giữ nguyên, không đổi ở addendum).

## 4. Thay đổi so với báo cáo hiện hành (viết 07/11 trên base r2)
Số r2 lúc đó **không đổi**; headline hiện hành = r3 (§0). Nhưng câu "nhất quán với 3c" của r1 **sai theo chữ**: mô hình giữ biên DRI cao hơn ngành tới 2054 (ROE mid ≈19–21%>Ke) ngầm hàm ý moat bền, trong khi tag NARROW/không bền. Theo luật 3c đúng chữ, giá trị là **NONE chặt 10.883 (TRÊN vùng, 98% dưới giá)** hoặc ít nhất **NONE½ 12.488 (TRONG, 78,8% dưới giá)**, so với 14.092 (35%). Nhãn có thể chuyển TRONG→TRÊN; khoảng theo peer 10.840–12.054. **Đã quyết 08/11 (user): không áp 3c chặt; headline = mô hình cơ sở (r3 15.257), các bản NONE chỉ là độ nhạy.** Không sửa REPORT/SUMMARY cũ, không ghi `dd_price_zones`. 5F non-PIT ⇒ chỉ DD sống. WARNING pháp lý giữ như REPORT_r2 §5.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự sửa)
Cột `entry` = độ hấp dẫn cấu trúc NGÀNH (moat_5f.py:33): cao su hàng hoá, price-taker ⇒ **L** (r1 để M). `moat_upgrade`: dòng 06/2026 đang Y; grep không thấy file .py nào ngoài research đọc cột này ⇒ không ảnh hưởng chạy; moat không bền ⇒ đề xuất **N** (có chủ ý, Mike xác nhận).
```
DRI,NARROW,LOCATION/COST,L,"Commodity price-taker; cost edge real (annual GPM [BQ GPM_P0 Q4=TTM] 2017-25 36.9% vs peer median 25.2%, 9/9 yrs) but ROE<Ke 2018-22, ROE_Min5Y 10.7%<Ke 13.5%, ROIC_Min10Y 6.5% => not durable => no moat credit added (convention 08/11: moat counts only when durable, never subtracted; NONE margin-to-industry = sensitivity only); post-peak (Q3-26 NP -33% YoY); land clock: NQ15 liquidates 1,975 ha (~24% tapped) 2027-30, Laos concession end 2054 unverified; Dakruco related-party governance risk",2026-11-07,5f_quickcheck_reuse_20260605,N
```
