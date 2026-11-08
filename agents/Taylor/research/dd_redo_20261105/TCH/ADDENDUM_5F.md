> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành (tâm 13.768 theo báo cáo gốc)**; mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.

# ADDENDUM 5F (bước 3c) — TCH · job `Taylor_20261107_130208`, sửa vòng 2 `Taylor_20261107_131628` · 07/11/2026 (bản trước: `ADDENDUM_5F_r1.md`)

> Bổ sung cho `REPORT_r2.md` (05/11), KHÔNG thay. Mọi phần khác giữ nguyên. Số mới: `calc/model_5f.py` → `calc/model_5f_out.txt/json`
> (exec phần định nghĩa của `model_r2.py`, không ghi đè file r2; chân CONTROL tái hiện đúng r2: tâm 13.768, P10/P50/P90 12.559/13.726/14.983).
> ROIC/GPM: `calc/bq_5f_roic_gpm.csv` (`tav2_bq.ticker_financial`, dòng **Q3** mỗi năm 2016–2026 = TTM tháng 10–tháng 9; GPM_P0 = TTM). ROIC/ROE_xY chỉ cập nhật ở dòng Q4 ⇒ **dòng Q3 năm Y mang số FY(Y−1)** (dòng 2026Q3 = FY2025). Ke/r = 13,5% (r2).
> Vòng 2: biến thể biên backlog về TB ngành → `calc/model_5f_fix.py` → `model_5f_fix_out.txt/json` (chạy 2 lần trùng byte; CONTROL tái hiện tâm 13.768).
> 5F dựa một phần kiến thức LLM ⇒ non-point-in-time, CHỈ cho DD sống, cấm backtest.

## 0. Tái dùng hay làm mới
**LÀM MỚI đầy đủ** — `data/moat_tags.csv` không có dòng TCH; `kb/projects/tch-dd-20261031.md`, REPORT/REPORT_r2 không có mục 5F/moat ⇒ chưa có audit 5F nào.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Loại hình DN**: chủ đầu tư BĐS nhà ở theo dự án (asset-heavy, chu kỳ, dòng tiền hữu hạn theo quỹ đất) tại Hải Phòng/Hà Nội + mảng phụ ô tô tải (HHS, biên gộp 13,2%) và cho thuê (40,5%). Góc **asset-play quỹ đất** (5F.md nguyên tắc 5) quan trọng hơn lợi nhuận hoạt động.

**Bằng chứng (i) — lợi nhuận siêu ngạch nhiều chu kỳ (cả hai phía):**

| Chỉ tiêu (dòng 2026Q3 = số FY2025) | TCH | Peer trung vị (n=14 nội địa) | so Ke 13,5% |
|---|---|---|---|
| ROIC5Y | 5,6% (dải FY2015–FY2025: 5,6–14,7%; ≥11,9% đến FY2018, 6,9% ở FY2019) | 7,1% (TB 8,2%) | **dưới** (chỉ FY2015 = 14,7% > Ke) |
| ROIC10Y | 7,0% (dải 7,0–14,7%) | — | dưới |
| ROIC_Min5Y / Min10Y | 2,3% / 2,3% (đỉnh 4,5% ở FY2021) | 0,7% | **dưới mọi năm** |
| ROE5Y / ROE_Min5Y (riêng, không thay ROIC) | 5,8% / 1,8% | 8,8% / — | dưới |
| Biên gộp BĐS (BCTC 6T FY26 / **6T cùng kỳ FY25**, TM23–25; DT BĐS 1.954,5 / 220,8 tỷ — `dd_TCH_20261031/calc/notes_read.md:44`, không phải cả năm) | **51,9% / 51,0%** | GPM TTM hợp nhất TB 2016–25: trung vị 37,9%, TB 39,4% | — |

Phía thuận: biên gộp BĐS 6T ~51–52% (dự án NC-II/Green River trên đất giá vốn cũ) — nhưng KHÔNG so được với peer: peer chỉ có GPM TTM hợp nhất (trung vị 37,9%) khác phạm vi, và nhiều peer đơn lẻ ngang/cao hơn ở dòng 2026Q3 (KDH 67,5%, PDR 73,2%, NVL 55,7%, VHM 50,3%; `calc/bq_5f_roic_gpm.csv`) ⇒ **không kết luận 'cao hơn peer'**. Phía nghịch: ROIC/ROE toàn DN <Ke liên tục từ FY2016, kể cả cửa sổ 10 năm ⇒ biên dự án cao KHÔNG chuyển thành lợi nhuận siêu ngạch trên vốn (vốn đọng tiền + quỹ đất chưa sinh lãi; REPORT_r2 §3 ROE chuẩn hoá ~6%). Đã cân nhắc và **loại** `ROIC_Trailing` (BQ: dòng 2016Q3–2026Q3 = 10,7–63,1%, phần lớn > Ke; dòng 2026Q3 14,2%) vì là artifact: LN TTM ≈ 796 tỷ (ước lượng, số từ brief skeptic 07/11, chưa tự tái tính) / VCSH 15.280 tỷ ≈ 5,2% — lệch vì tử số gồm lãi một lần/tiền gửi. ⇒ **(i) KHÔNG đạt.**
Lưu ý so sánh: GPM peer là TTM HỢP NHẤT (lẫn mảng), không phải biên mảng BĐS; GPM hợp nhất TCH 29,8% bị mảng ô tô kéo xuống ⇒ so biên mảng-với-mảng **cần kiểm chứng**.

| Lực | Mức | Cơ chế + số |
|---|---|---|
| Gia nhập mới | 🟡 TB | Quỹ đất mới qua ĐẤU GIÁ mở: I.14 trúng 1.322 tỷ (~70 tr/m² đất), 150 Tô Hiệu tiền đất ~103 tr/m² ≈ 30–43% giá bán (REPORT §10, ước lượng) ⇒ không có kênh đất độc quyền; vốn lớn là rào cản duy nhất (TCH không vay — điểm mạnh, không phải hào). |
| Nhà cung cấp | 🔴 Cao | Nhà nước = chủ đất + định giá tiền SDĐ (2.993 tỷ đã nộp cho 2 quỹ mới); NC-II một phần đất thuê trả hằng năm 26.664 m² đến 2073 (TM22b). Nhà thầu phân tán (cần kiểm chứng). |
| Người mua | 🟡–🔴 | Người mua lẻ phân tán (tập trung khách thấp — cần kiểm chứng), nhưng cầu thấp tầng HP phụ thuộc dòng tiền NĐT; vay mua nhà cố định 10,9%, thả nổi 13–15% (Bobby, DKRA T8/CBRE Q3). Switching cost = 0. |
| Thay thế | 🟡 TB | Thứ cấp, dự án lân cận, nguồn cung thấp tầng Thủy Nguyên tăng mạnh 3 năm tới (JLL qua Bobby). |
| Cạnh tranh nội bộ | 🔴 Cao | 1 chủ đầu tư quốc gia = 47% giao dịch thấp tầng sơ cấp Đông HP H1/2026, top-4 dự án ~89% (HPREA qua Bobby) ⇒ TCH không dẫn thị phần phân khúc (thị phần TCH: cần kiểm chứng). |
| **Lực 6** | 🔴 | **Đồng hồ cắt hào**: lợi thế giá vốn đất cũ HỮU HẠN — backlog NC-II 3.099 tiêu ~1.033/quý (~3 quý, REPORT §3b); quỹ mới giá đấu thị trường ⇒ biên mỏng hơn. Chính sách: luật Đất đai/Nhà ở/KDBĐS sửa đổi và bảng giá đất sát thị trường — mốc 'trình QH 22/10/2026' **cần kiểm chứng** (không có nguồn trong `dd_TCH_20261031`/REPORT_r2). |

**Kết luận**: ngành hấp dẫn **thấp** ở pha hiện tại; **moat_tier = NONE**, moat_type = **LOCATION (quỹ đất giá vốn cũ, hữu hạn — tài sản, không phải cơ chế tái tạo)**. (ii) cơ chế gọi tên được chỉ ở cấp dự án (đất mua rẻ trước đây), không lặp lại được; (iii) có đồng hồ. 0/3 điều kiện bền ⇒ `moat_durable=false`.
**Rủi ro số 1**: biên quỹ đất mới (150 Tô Hiệu, I.14 — ~25% HTK còn lại, giá đấu thị trường) mỏng hơn hẳn 51,9% lịch sử khi thị trường thấp tầng HP đang chậm ⇒ thặng dư NAV tái hiện không đạt.

## 2. Moat trong mô hình
Mô hình r2 là **NAV dự án hữu hạn** (không có terminal/fade): backlog đã bán (NMTT) + thặng dư HTK đất cũ PV 4 năm + quỹ mới NPV 0. Rà soát theo luật C (kể cả kênh ngầm):
| Kênh | r2 | Luật 3c cho NONE | Kết luận |
|---|---|---|---|
| RONIC/terminal | không có terminal; quỹ đất mới = giá sổ (NPV 0) | RONIC = Ke | **đã = Ke**, đối xứng (song song ±10% đã có) |
| Biên phần chưa bán (đất cũ) | s_old {25;40;55} tâm 40% ⇔ GPM ~40% (s(1−g)=0,8(g−0,1)) | biên về TB chu kỳ ngành | TB ngành 37,9–40,6% ⇔ s 35,9–41,2% ⇒ **gần trùng**; KHÔNG giữ biên riêng 51,9% của mã (⇔ s≈70%) |
| Backlog biên ròng {30;33,5;36}% | doanh thu đã ký/đã thu trước; biên = 0,8×(GPM riêng TCH 51,9% − 10%) ⇒ 33,5% | biên về TB ngành | **doanh thu đã chốt nhưng CHI PHÍ HOÀN THÀNH chưa công bố** ⇒ biên 33,5% dựa GPM riêng của mã, không phải số đã chốt ⇒ chạy biến thể (a)(b)(c) ở §3 |
| Năm/số mũ chiết khấu (H) | backlog 1–2 năm, thặng dư 4 năm, `1/(1+r)^y` | — | giữ nguyên quy ước r2 |
| Pháp lý (E) | CK quản trị chỉ song song (WARNING) | không dùng ép biên | không đếm hai lần |
⇒ **Không thưởng moat.** Kênh RONIC và biên thặng dư đất cũ nhất quán với NONE (chênh ≤1,1%), NHƯNG **biên backlog 33,5% đang giữ GPM riêng 51,9% của mã** (trên TB ngành 37,9–40,6%) ⇒ KHÔNG ghi 'nhất quán toàn phần': bản chặt-3c đầy đủ (c) ở §3 thấp hơn r2 −2,6% … −4,7%.

## 3. Bản CHẶT-3C (biên đất cũ về TB ngành, lưới ±15pp đối xứng) và độ nhạy moat — sau CK 5 tỷ
| Bản | s_old tâm | Tâm | P10 / P50 / P90 | % dưới giá | Nhãn 5 tỷ | Nhãn sleeve 10–40tr |
|---|---|---|---|---|---|---|
| r2 hiện hành (CONTROL) | 40% | **13.768** | 12.559 / 13.726 / 14.983 | 19,1% | TRONG | TRONG |
| Chặt-3c, GPM peer trung vị 37,9% (n=14) | 35,9% | 13.611 (−1,1%) | 12.417 / 13.569 / 14.811 | 23,8% | TRONG | TRONG |
| Chặt-3c, GPM peer TB 39,4% (n=14) | 38,8% | 13.722 (−0,3%) | 12.518 / 13.680 / 14.933 | 21,1% | TRONG | TRONG |
| Chặt-3c, nhà ở thuần trung vị 39,0% (n=10) | 38,0% | 13.692 (−0,6%) | 12.490 / 13.650 / 14.900 | 21,1% | TRONG | TRONG |
| Chặt-3c, nhà ở thuần TB 40,6% (n=10) | 41,2% | 13.815 (+0,3%) | 12.601 / 13.773 / 15.035 | 18,4% | TRONG | TRONG |
| **WIDE** (biên lịch sử bền: s {40;55;70} + quỹ mới +10%) | 55% | 14.495 (+5,3%) | 13.221 / 14.454 / 15.798 | 3,9% | **DƯỚI** | DƯỚI |
| WIDE nhẹ (chỉ quỹ mới +10%) | 40% | 13.914 (+1,1%) | 12.697 / 13.872 / 15.137 | 14,1% | TRONG | DƯỚI (**ranh giới**, P10 ≈ giá) |
| **(a)** chỉ biên backlog về ngành (GPM 37,9–40,6% ⇒ m tâm 22,3–24,5%) | 40% | 13.398–13.470 (−2,7% … −2,2%) | 12.218–12.284 / 13.356–13.428 / 14.585–14.662 | 25,4–27,0% | TRONG | TRONG |
| **(b)** (a) + chi phí hoàn thành backlog theo GPM ngành | 40% | 13.266–13.363 (−3,6% … −2,9%) | 12.096–12.185 / 13.227–13.323 / 14.443–14.547 | 29,3–31,6% | TRONG | TRONG |
| **(c) CHẶT-3C ĐẦY ĐỦ** = (b) + s_old về ngành (RONIC=Ke, lưới ±15pp đối xứng) | 35,9–41,2% | **13.122–13.407 (−4,7% … −2,6%)**; med14 13.122, mean14 13.277, med10 13.235, mean10 13.407 | 11.971–12.224 / 13.083–13.367 / 14.285–14.595 | 27,3–35,9% | TRONG | TRONG |
| NARROW | = NONE (NAV hữu hạn, không terminal ⇒ NARROW không thưởng) | 13.611–13.815 | | | TRONG | TRONG |
| **NONE cứng** (biên = GPM hợp nhất TB TCH 29,8% ⇒ s 19,1%; quỹ mới −10%) | 19,1% | 12.947 (−6,0%) | 11.827 / 12.904 / 14.086 | 48,4% | TRONG | TRONG |

Peer (nội địa, chủ đầu tư BĐS niêm yết): VHM, KDH, NLG, DXG, PDR, DIG, NTL, IJC, HDC, CEO, AGG, NVL, HDG, SJS; loại HHS (cùng tập đoàn, mảng ô tô) và CRV (công ty con). Nhóm "nhà ở thuần" bỏ thêm HDG (năng lượng), AGG, SJS, CEO (cơ cấu mảng lẫn). Cách chọn peer làm tâm dao động 13.611–13.815 (−1,1% … +0,3%). NVL nằm trong danh sách BANNED giao dịch nhưng chỉ dùng làm điểm dữ liệu ngành.
Biến thể (a)(b)(c): m backlog = 0,8×(GPM ngành − 10%) (cùng quan hệ ⇒ 33,5% khi GPM 51,9%), lưới giữ lệch {−3,5; 0; +2,5}pp như r2; (b) tính lại chi phí hoàn thành/phần đất cũ còn lại theo GPM ngành. Mức giảm ≈ −2,6% … −4,7% (≈ −350 … −650 đ/cp), tương đương ước −2,4% của skeptic nhưng sâu hơn khi gộp (b)(c). Nhãn vẫn TRONG ở mọi cỡ (10 triệu … 10 tỷ).
**Nếu moat sai**: đọc WIDE (+5,3%) đẩy nhãn sang DƯỚI; đọc NONE cứng (−6,0%) giữ TRONG nhưng 48% trọng số dưới giá. Biên độ do moat (≈ −6% … +5%) NHỎ hơn trục CK holding (0% ⇒ +8,4%) và CK quản trị 15% (−15%) đã có ở r2.

## 4. Thay đổi so với báo cáo hiện hành
**Mô hình r2 giữ nguyên (model_changed=false, quy ước chờ Mike duyệt)**: tâm 13.768, P10/P50/P90 12.559/13.726/14.983, nhãn **TRONG vùng**. Bản chặt-3c chỉ phần thặng dư đất cũ cho 13.611–13.815 (±1,1%); **bản chặt-3c ĐẦY ĐỦ có kéo biên backlog về ngành cho 13.122–13.407 (−2,6% … −4,7%, % dưới giá 27–36%), nhãn TRONG ở mọi cỡ** — đây là bản mô tả đúng luật 3c (headline, **quy ước chờ Mike/user duyệt**); nhãn không đổi nên không ảnh hưởng vùng giá. Bổ sung duy nhất: mục 5F + kết luận NONE/LOCATION hữu hạn, củng cố cảnh báo §3 REPORT_r2 (ROE/ROIC < Ke: NAV phụ thuộc thặng dư quỹ đất cũ, không phải hào tái tạo). Không ghi `dd_price_zones`, không sửa REPORT/SUMMARY — Mike quyết.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
TCH,NONE,LOCATION,L,"Hoang Huy (Hai Phong residential developer + HHS trucks). BDS project GPM 51.9% (6T FY26) on OLD low-cost land bank, but firm-level ROIC5Y 5.6%/ROIC_Min5Y 2.3%/ROE5Y 5.8% < Ke 13.5% every FY window since FY2016 (peer ROIC5Y med 7.1%) — no multi-cycle excess return. Land advantage FINITE (NC-II backlog ~3 quarters; new land bought at open auction, thinner margin) = countdown clock. #1 risk: new-land (150 To Hieu, I.14) margin far below 51.9% while HP low-rise demand weak; governance WARNING (2 penalties 16m, related-party cash 678bn SG Tai Loc)",2026-11-07,5f_cyclical,N
```
entry = L; src = 5f_cyclical (ngành nhà ở thấp tầng HP pha hiện tại kém hấp dẫn cấu trúc, theo Bobby 31/10 — không suy từ tier); moat_upgrade = N.
