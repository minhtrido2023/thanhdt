# ADDENDUM 5F (bước 3c) — TCH · job `Taylor_20261107_130208` · 07/11/2026

> Bổ sung cho `REPORT_r2.md` (05/11), KHÔNG thay. Mọi phần khác giữ nguyên. Số mới: `calc/model_5f.py` → `calc/model_5f_out.txt/json`
> (exec phần định nghĩa của `model_r2.py`, không ghi đè file r2; chân CONTROL tái hiện đúng r2: tâm 13.768, P10/P50/P90 12.559/13.726/14.983).
> ROIC/GPM: `calc/bq_5f_roic_gpm.csv` (`tav2_bq.ticker_financial`, dòng cuối mỗi năm 2016–2026Q3; GPM_P0 = TTM). Ke/r = 13,5% (r2).
> 5F dựa một phần kiến thức LLM ⇒ non-point-in-time, CHỈ cho DD sống, cấm backtest.

## 0. Tái dùng hay làm mới
**LÀM MỚI đầy đủ** — `data/moat_tags.csv` không có dòng TCH; `kb/projects/tch-dd-20261031.md`, REPORT/REPORT_r2 không có mục 5F/moat ⇒ chưa có audit 5F nào.

## 1. Vị thế & lợi thế cạnh tranh (5F)
**Loại hình DN**: chủ đầu tư BĐS nhà ở theo dự án (asset-heavy, chu kỳ, dòng tiền hữu hạn theo quỹ đất) tại Hải Phòng/Hà Nội + mảng phụ ô tô tải (HHS, biên gộp 13,2%) và cho thuê (40,5%). Góc **asset-play quỹ đất** (5F.md nguyên tắc 5) quan trọng hơn lợi nhuận hoạt động.

**Bằng chứng (i) — lợi nhuận siêu ngạch nhiều chu kỳ (cả hai phía):**

| Chỉ tiêu (2026Q3) | TCH | Peer trung vị (n=14 nội địa) | so Ke 13,5% |
|---|---|---|---|
| ROIC5Y | 5,6% (dải 2016–26: 5,6–14,7%; ≥11,9% chỉ đến 2019) | 7,1% (TB 8,2%) | **dưới** từ 2020 |
| ROIC10Y | 7,0% (dải 7,0–14,7%) | — | dưới |
| ROIC_Min5Y / Min10Y | 2,3% / 2,3% (đỉnh 4,5% năm 2022) | 0,7% | **dưới mọi năm** |
| ROE5Y / ROE_Min5Y (riêng, không thay ROIC) | 5,8% / 1,8% | 8,8% / — | dưới |
| Biên gộp BĐS (BCTC 6T FY26 / FY25, TM23–25) | **51,9% / 51,0%** | GPM TTM hợp nhất TB 2016–25: trung vị 37,9%, TB 39,4% | — |

Phía thuận: biên gộp BĐS ~51–52% cao hơn peer ~12–14pp (dự án NC-II/Green River trên đất giá vốn cũ). Phía nghịch: ROIC/ROE toàn DN <Ke liên tục từ 2020, kể cả cửa sổ 10 năm ⇒ biên dự án cao KHÔNG chuyển thành lợi nhuận siêu ngạch trên vốn (vốn đọng tiền + quỹ đất chưa sinh lãi; REPORT_r2 §3 ROE chuẩn hoá ~6%). ⇒ **(i) KHÔNG đạt.**
Lưu ý so sánh: GPM peer là TTM HỢP NHẤT (lẫn mảng), không phải biên mảng BĐS; GPM hợp nhất TCH 29,8% bị mảng ô tô kéo xuống ⇒ so biên mảng-với-mảng **cần kiểm chứng**.

| Lực | Mức | Cơ chế + số |
|---|---|---|
| Gia nhập mới | 🟡 TB | Quỹ đất mới qua ĐẤU GIÁ mở: I.14 trúng 1.322 tỷ (~70 tr/m² đất), 150 Tô Hiệu tiền đất ~103 tr/m² ≈ 30–43% giá bán (REPORT §10, ước lượng) ⇒ không có kênh đất độc quyền; vốn lớn là rào cản duy nhất (TCH không vay — điểm mạnh, không phải hào). |
| Nhà cung cấp | 🔴 Cao | Nhà nước = chủ đất + định giá tiền SDĐ (2.993 tỷ đã nộp cho 2 quỹ mới); NC-II một phần đất thuê trả hằng năm 26.664 m² đến 2073 (TM22b). Nhà thầu phân tán (cần kiểm chứng). |
| Người mua | 🟡–🔴 | Người mua lẻ phân tán (tập trung khách thấp — cần kiểm chứng), nhưng cầu thấp tầng HP phụ thuộc dòng tiền NĐT; vay mua nhà cố định 10,9%, thả nổi 13–15% (Bobby, DKRA T8/CBRE Q3). Switching cost = 0. |
| Thay thế | 🟡 TB | Thứ cấp, dự án lân cận, nguồn cung thấp tầng Thủy Nguyên tăng mạnh 3 năm tới (JLL qua Bobby). |
| Cạnh tranh nội bộ | 🔴 Cao | 1 chủ đầu tư quốc gia = 47% giao dịch thấp tầng sơ cấp Đông HP H1/2026, top-4 dự án ~89% (HPREA qua Bobby) ⇒ TCH không dẫn thị phần phân khúc (thị phần TCH: cần kiểm chứng). |
| **Lực 6** | 🔴 | **Đồng hồ cắt hào**: lợi thế giá vốn đất cũ HỮU HẠN — backlog NC-II 3.099 tiêu ~1.033/quý (~3 quý, REPORT §3b); quỹ mới giá đấu thị trường ⇒ biên mỏng hơn. Chính sách: 3 luật Đất đai/Nhà ở/KDBĐS sửa đổi đang trình QH (22/10/2026), bảng giá đất sát thị trường. |

**Kết luận**: ngành hấp dẫn **thấp** ở pha hiện tại; **moat_tier = NONE**, moat_type = **LOCATION (quỹ đất giá vốn cũ, hữu hạn — tài sản, không phải cơ chế tái tạo)**. (ii) cơ chế gọi tên được chỉ ở cấp dự án (đất mua rẻ trước đây), không lặp lại được; (iii) có đồng hồ. 0/3 điều kiện bền ⇒ `moat_durable=false`.
**Rủi ro số 1**: biên quỹ đất mới (150 Tô Hiệu, I.14 — ~25% HTK còn lại, giá đấu thị trường) mỏng hơn hẳn 51,9% lịch sử khi thị trường thấp tầng HP đang chậm ⇒ thặng dư NAV tái hiện không đạt.

## 2. Moat trong mô hình
Mô hình r2 là **NAV dự án hữu hạn** (không có terminal/fade): backlog đã bán (NMTT) + thặng dư HTK đất cũ PV 4 năm + quỹ mới NPV 0. Rà soát theo luật C (kể cả kênh ngầm):
| Kênh | r2 | Luật 3c cho NONE | Kết luận |
|---|---|---|---|
| RONIC/terminal | không có terminal; quỹ đất mới = giá sổ (NPV 0) | RONIC = Ke | **đã = Ke**, đối xứng (song song ±10% đã có) |
| Biên phần chưa bán (đất cũ) | s_old {25;40;55} tâm 40% ⇔ GPM ~40% (s(1−g)=0,8(g−0,1)) | biên về TB chu kỳ ngành | TB ngành 37,9–40,6% ⇔ s 35,9–41,2% ⇒ **gần trùng**; KHÔNG giữ biên riêng 51,9% của mã (⇔ s≈70%) |
| Backlog biên ròng {30;33,5;36}% | doanh thu đã ký/đã thu trước | — | hợp đồng đã chốt, không phải giả định moat ⇒ giữ |
| Năm/số mũ chiết khấu (H) | backlog 1–2 năm, thặng dư 4 năm, `1/(1+r)^y` | — | giữ nguyên quy ước r2 |
| Pháp lý (E) | CK quản trị chỉ song song (WARNING) | không dùng ép biên | không đếm hai lần |
⇒ **Không thưởng moat; mô hình hiện hành ĐÃ ngầm ở mức NONE (biên đất cũ ≈ TB ngành, RONIC=Ke) — nhất quán**, sau khi đã kiểm bản chặt-3c bên dưới (chênh ≤1,1%).

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
| NARROW | = NONE (NAV hữu hạn, không terminal ⇒ NARROW không thưởng) | 13.611–13.815 | | | TRONG | TRONG |
| **NONE cứng** (biên = GPM hợp nhất TB TCH 29,8% ⇒ s 19,1%; quỹ mới −10%) | 19,1% | 12.947 (−6,0%) | 11.827 / 12.904 / 14.086 | 48,4% | TRONG | TRONG |

Peer (nội địa, chủ đầu tư BĐS niêm yết): VHM, KDH, NLG, DXG, PDR, DIG, NTL, IJC, HDC, CEO, AGG, NVL, HDG, SJS; loại HHS (cùng tập đoàn, mảng ô tô) và CRV (công ty con). Nhóm "nhà ở thuần" bỏ thêm HDG (năng lượng), AGG, SJS, CEO (cơ cấu mảng lẫn). Cách chọn peer làm tâm dao động 13.611–13.815 (−1,1% … +0,3%). NVL nằm trong danh sách BANNED giao dịch nhưng chỉ dùng làm điểm dữ liệu ngành.
**Nếu moat sai**: đọc WIDE (+5,3%) đẩy nhãn sang DƯỚI; đọc NONE cứng (−6,0%) giữ TRONG nhưng 48% trọng số dưới giá. Biên độ do moat (≈ −6% … +5%) NHỎ hơn trục CK holding (0% ⇒ +8,4%) và CK quản trị 15% (−15%) đã có ở r2.

## 4. Thay đổi so với báo cáo hiện hành
**Mô hình KHÔNG đổi** (model_changed=false): tâm 13.768, P10/P50/P90 12.559/13.726/14.983, nhãn **TRONG vùng** giữ nguyên; bản chặt-3c theo mọi cách chọn peer cho 13.611–13.815 (±1,1%), nhãn TRONG ở cả 5 tỷ và sleeve. Bổ sung duy nhất: mục 5F + kết luận NONE/LOCATION hữu hạn, củng cố cảnh báo §3 REPORT_r2 (ROE/ROIC < Ke: NAV phụ thuộc thặng dư quỹ đất cũ, không phải hào tái tạo). Không ghi `dd_price_zones`, không sửa REPORT/SUMMARY — Mike quyết.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
```
TCH,NONE,LOCATION,L,"Hoang Huy (Hai Phong residential developer + HHS trucks). BDS project GPM 51.9% (6T FY26) on OLD low-cost land bank, but firm-level ROIC5Y 5.6%/ROIC_Min5Y 2.3%/ROE5Y 5.8% < Ke 13.5% every window since 2020 (peer ROIC5Y med 7.1%) — no multi-cycle excess return. Land advantage FINITE (NC-II backlog ~3 quarters; new land bought at open auction, thinner margin) = countdown clock. #1 risk: new-land (150 To Hieu, I.14) margin far below 51.9% while HP low-rise demand weak; governance WARNING (2 penalties 16m, related-party cash 678bn SG Tai Loc)",2026-11-07,5f,N
```
entry = L (ngành nhà ở thấp tầng HP pha hiện tại kém hấp dẫn cấu trúc, theo Bobby 31/10 — không suy từ tier); moat_upgrade = N.
