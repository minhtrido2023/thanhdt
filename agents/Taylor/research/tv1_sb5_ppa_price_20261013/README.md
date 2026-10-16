# TV1 / Sông Bung 5 — kiểm chứng tin giảm giá điện hợp đồng + SOTP dựng lại

Job `Taylor_20261013_061651` · 2026-10-13 · CHỈ ĐỌC (không đổi state/plan/config).
File: `sb5_price_series.csv` · `peer_hydro_prices.md` (subagent) · `sotp_sb5.py` → `sotp_sb5_scenarios.csv`.
PDF gốc đã tải: `/tmp/tv1sb5_dl/` (không bền — URL ghi dưới đây).

## 1. Tin giảm giá: ĐÚNG VỀ HƯỚNG, có văn bản gốc; KHÔNG phải tin mới; mốc + mức chưa có văn bản

| Ý | Nhãn | Nguồn |
|---|---|---|
| PPA SB5 có giá cố định HAI BẬC, bậc sau thấp hơn nhiều | **XÁC NHẬN bằng văn bản gốc** | PECC1, "Báo cáo phương án bán toàn bộ tài sản NMTĐ Sông Bung 5", 8/2018, tr.13 mục III — https://www.pecc1.com.vn/userfile/files/QHCD/2018/ (file "Báo cáo Phương án bán Nhà máy thủy điện Sông Bung 5.pdf") |
| Công ty thừa nhận giá điện SB5 sẽ sụt giảm | **XÁC NHẬN bằng văn bản gốc** (không số, không năm) | BCTN 2025 tr.38 mục 7: "...đầu tư dự án điện mặt trời lòng hồ Sông Bung 5 góp phần đảm bảo và duy trì doanh thu cho Công ty khi giá điện của nhà máy TĐ Sông Bung 5 sụt giảm" — owa.hnx.vn/ftp/cims/2026/4_W3/000000016132930_TV1Bao_cao_thuong_nien_nam_2025Tieng_Viet.pdf |
| Mốc hạ giá = 2027 | **CHỈ có lời lãnh đạo qua CTCK** | KBSV 17/04/2026 tr.4 |
| Mức sau hạ = 500-600 đ/kWh (chưa thuế TN, phí DVMTR), −40-50% | **CHỈ có lời lãnh đạo qua CTCK** | KBSV 17/04/2026 tr.4 |
| Phụ lục PPA hiện hành / thuyết minh BCTC về biểu giá | **KHÔNG TÌM THẤY** | BCTC kiểm toán, tài liệu ĐHĐCĐ 2026, bản cáo bạch: không tải được |

**Nội dung văn bản 2018 (nguyên văn, giá chưa gồm thuế tài nguyên, phí môi trường):** EVN phê duyệt tại NQ 286/NQ-HĐTV
06/08/2018, Cục ĐTĐL chấp thuận tại 1374/ĐTĐL-GP 24/8/2018, cho "Hợp đồng sửa đổi, bổ sung số 05":
giá cố định bình quân nhiều năm 569,36 đ/kWh; **01/01/2019–31/12/2021: 569,36**; **từ 01/01/2022 đến hết đời sống
kinh tế: 243,66**; giá O&M năm cơ sở 2018: 75,75 đ/kWh (30,3 nhân công trượt CPI ≤2,5% + 45,45 trượt 2,5%/năm).
PPA gốc: số 03/2013/HĐ-NMĐSB5 ngày 28/3/2013, phụ lục 01 (27/2/2015), 02 (18/1/2017), 03 (28/02/2018), 04 (3/2018).

**Suy diễn của tôi (không phải fact):**
- Đây là cơ chế CÓ SẴN (giá cố định từng năm: cao trong kỳ trả nợ, thấp sau đó — TT 56/2014, TT 57/2020 Đ.13 cho
  phép), lộ từ 2018, KHÔNG phải EVN đàm phán lại. KBSV cũng viết đấu giá thất bại vì "rủi ro điều chỉnh giá bán
  trong tương lai". Khoản vay VietinBank 13 năm đã tất toán 31/3/2025 (BC SXKD 2024 tr.3).
- Lịch 2019/2022 của dự thảo 2018 **không khớp thực tế**: giá bình quân thực hiện 2021-2025 (gồm thuế+phí) vẫn
  1.000-1.150 đ/kWh; trừ thuế TN + phí (~130-145) còn ~900-1.000, tức ngang giá hợp đồng 2014-2017 (939-941).
  VCBS 6/2024 cũng mô tả giá PPA chỉ nhích 0,3%/năm theo trượt O&M. ⇒ phụ lục 05 hoặc không ký như dự thảo, hoặc
  mốc hạ bậc đã lùi. Không có văn bản nào tôi đọc được nói rõ.
- **Hai nguồn mâu thuẫn về MỨC**: KBSV/lãnh đạo 500-600 vs dự thảo 2018 = 243,66 + O&M (75,75×1,025⁹ ≈ 95) ≈ 340.
  Chưa phân xử được; phải coi 340 là kịch bản xấu có cơ sở văn bản, không phải bịa.

## 2. Chuỗi giá SB5 — `sb5_price_series.csv`
Giá hợp đồng 2014-2017 phẳng 938,78 → 940,76 (văn bản gốc). 2022: 1.052 · 2023: 1.148 · 2025: 1.106 (tự chia, gồm
thuế+phí). **Chưa có bước giảm nào trong lịch sử 2014-2025.** Thiếu: 2019, 2020, sản lượng 2024, tách Qc/CGM sau 2017.
Sản lượng: thiết kế có 3 con số (187,06 / 208,85 / 230,34); bình quân thực 2013-2023 chỉ **175,3** (công ty, 7/2024);
KBSV dùng 210 (bình quân 2021-2025, giai đoạn mưa nhiều).

## 3. Peer — `peer_hydro_prices.md` (subagent; tôi chưa tự kiểm lại từng số)
Không mã nào có câu "giá hợp đồng giai đoạn 2 giảm" được công ty/CTCK nêu rõ. BSA 2024→2025 phẳng 1.229→1.215.
Tín hiệu cùng chiều duy nhất: **BSA KH 2026 = 172,86 tỷ / 230 tr kWh ≈ 752 đ/kWh, −39% so KH 2025**, BCTN không
giải thích. DPG (≤30MW) theo biểu giá chi phí tránh được — không so được với PPA đàm phán >30MW. Dữ liệu peer MỎNG.

## 4. SOTP dựng lại — `python3 sotp_sb5.py`
Giả định: định giá tại 01/2027, đời còn 30 năm, không terminal; O&M tiền mặt 25 tỷ (giá vốn điện 2025 96,5 − khấu
hao ~35 − thuế TN+phí ~37), capex 5 tỷ, cả hai +2,5%/năm; phần O&M của giá (95 đ) trượt 2,5%; khấu hao 33 tỷ × 15
năm; TNDN 20%; thuế tài nguyên + phí DVMTR coi là pass-through (giá đã tách); nợ ròng 117 tỷ; 26,69 tr cp; giá 19.200.
Chân control (a) ra EV 1.200-1.298 tỷ = tái lập dải cũ 1.000-1.300 ✓.

Q = 210 tr kWh, tư vấn = 0:

| Giá sau 2027 (đ/kWh, chưa thuế phí) | FCF 2027 | Hydro EV (r 10→12%) | Giá trị/cp | vs 19.200 |
|---|---|---|---|---|
| (a) giữ ~950 | 141 tỷ | 1.298 → 1.114 | 44.300 → 37.300 | +131% → +94% |
| (b) 600 | 82 tỷ | 744 → 640 | 23.500 → 19.600 | +22% → +2% |
| (c) 500 | 66 tỷ | 586 → 505 | 17.600 → 14.500 | −9% → −24% |
| (d) ~340 (dự thảo 2018) | 39 tỷ | 332 → 288 | 8.100 → 6.400 | −58% → −67% |

- Nhạy sản lượng (r 11%): ở 600 đ — Q 175 → 15.800 · 187 → 17.700 · 236 → 25.600; ở 500 đ — 11.200 · 12.800 · 19.500.
- **Giá hoà vốn** (equity = vốn hoá, tư vấn = 0, Q 210): **528-592 đ/kWh** — nằm đúng trong dải 500-600.
- Tư vấn +50/+100 tỷ = +1.900/+3.700 đ/cp. Đối chiếu độc lập: KBSV định giá mảng thủy điện 584 tỷ (DCF) — nằm giữa (b) và (c).
- Phép tính thô của Mike (EV 460-740, 12.700-23.200 đ/cp) **khớp**.

**Biên an toàn của SOTP gốc (≥40% ở kịch bản bảo thủ) KHÔNG CÒN.** Ở dải lãnh đạo nêu, cổ phiếu ≈ đúng giá
(−24%…+22%); nếu sản lượng về bình quân lịch sử 175-187 thì âm cả ở 600; nếu mức thật là ~340 thì −60%.
- **Comp Nậm Nơn 32 tỷ/MW**: hết dùng được — giá/MW chỉ có nghĩa khi giá bán/kWh tương đương; Nậm Nơn 20MW thuộc
  nhóm biểu giá chi phí tránh được. Áp cho nhà máy bán 500-600 là thổi giá.
- **Đấu giá 2018-2021 hỏng 5-6 lần**: SOTP cũ đọc là "do bảo lãnh tín dụng, không phải giá trị nội tại" — đọc SAI.
  Chứng thư AASC ra 1.686 tỷ với chi phí vốn chủ **7%**, 40% sản lượng bán CGM ở 890 đ +2,5%/năm (tr.14); không ai
  nộp hồ sơ ở 1.352-1.688 tỷ là người mua đã chiết khấu bậc giá. Đó là bằng chứng thị trường CHỐNG lại dải cũ.

## 5. Tỷ trọng thật (dnse_raw_2026-10-13.jsonl, snapshot 04:57 ICT, lọc account_no; giá 19.200)
| Account | TV1 | Giá vốn | Giá trị | % active_nav | % tổng NAV | Target | SOTP gốc đề xuất |
|---|---|---|---|---|---|---|---|
| SpaceX 0002023347 | 2.300 cp | 18.648 | 44,16 tr | **4,48%** (986,2 tr) | 4,48% | 5% | ≤0,5-1,0% |
| ZaloPay 0001743768 | 1.400 cp | 18.829 | 26,88 tr | **4,47%** (601,4 tr) | 2,89% (931,4 tr) | 5% | ≤0,5-1,0% |

active_nav lấy từ `active_nav_{acct}.json` computed_at 2026-10-12. Cả hai state file `status=active`, trần 25.000đ.
Thiếu ~0,5pp so target ⇒ chương trình vẫn có thể chèn lệnh mua bù. Vị thế đang lãi nhẹ (+2-3% trên giá vốn).

## 6. Khuyến nghị (user quyết — tôi không đổi gì)
1. **TẠM DỪNG mua thêm TV1 ở cả 2 account** trong khi chờ. Luận điểm gốc (tài sản che downside) đã mất nền; mua tiếp
   ở 19-20k là mua đúng giá, không còn mua rẻ. Trần 25.000đ hiện CAO HƠN giá trị kịch bản 600 đ (19.600-23.500).
2. **GIỮ vị thế hiện có, chưa bán vội**: ở dải 500-600 không bị định giá cao rõ rệt; KH 2026 bán điện 187 tỷ nên 2026
   chưa chịu ảnh hưởng. Nhưng 4,5% active_nav là gấp 4,5-9 lần mức SOTP gốc đề xuất — nên bàn hạ về ≤1-2% sau khi
   fundamental-skeptic phản biện.
3. **Việc quyết định được ván này**: lấy phụ lục PPA hiện hành (mốc + mức bậc 2) — hỏi IR PECC1/EPTC hoặc đọc thuyết
   minh BCTC kiểm toán 2025. 500-600 hay ~340 là chênh giữa "đúng giá" và "−60%".
4. Nếu sau này mở lại: trần không quá ~16.000-17.000đ (giá trị kịch bản 500 đ) thay cho 25.000đ.

## Tự nhận sai
SOTP 2026-07-23 giả định FCF thủy điện 110-140 tỷ PHẲNG 30 năm. Bậc giá nằm sẵn trong tài liệu công ty 2018 và trong
báo cáo KBSV 4/2026 — tôi không đọc cả hai trước khi kết luận "biên an toàn ~40%".
