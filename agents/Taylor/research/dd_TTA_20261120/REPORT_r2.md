# DD — TTA r2 · 2026-11-20 · job `Taylor_20261120_044902` (áp đính chính fundamental-skeptic lên REPORT.md r1)

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua. Không đặt lệnh, không wire, **không ghi `dd_price_zones.json`, không email**.
> REPORT.md / model/dcf_tta.py (r1) giữ nguyên. Mô hình r2: `model/dcf_tta_r2.py`; độ nhạy trọng số: `model/sens_w_r2.py`. Nguồn như r1
> ([Q3] BCTC tổng hợp Q3/2026, [KT25], [GT], [BQ], [Bobby]…). Số tự đặt gắn **(ước lượng)**.

## 0. Kết luận r2

**Hướng giữ: KHÔNG RẺ ở 10.250 đ. Mức số r1 bị hạ mạnh:** tâm có trọng số **6.342 đ** (trước thanh khoản) → **5.708 đ sau chiết khấu thanh khoản 10%**
(r1: 8.040 / 7.240). Giá 10.250 = **1,80 × tâm** (sau thanh khoản).

| Kịch bản (mù giá) | Giá bán mặt trời | Hồi tố | Trả hồi tố/tỷ lệ tiền thu ngụ ý | V1 bù trừ ngay (đ/cp) | V2 trả góp 5n có lãi (đ/cp) | P (ước lượng) |
|---|---|---|---|---|---|---|
| A — giữ FIT cả hai | BN FIT1, NM1 FIT2 | 0 | 100% | **12.651** | 12.651 | 0,15 |
| B — chỉ Bầu Ngứ về FIT2 (NM1 giữ) | BN FIT2 | 385 tỷ | 85% | **8.821** | 8.945 | 0,25 |
| **B′** — BN FIT1→FIT2 + NM1 FIT2→trần 1.184,90 (đúng KL TTCP r1 :95) | BN FIT2, NM1 trần | 674 tỷ | 72% | **5.559** | 5.776 | **0,35** |
| C — cả hai về trần + hồi tố + thuỷ văn −15% 2027 + lãi +1pp | cả hai trần | 1.053 tỷ | 55% | **1.175** | 1.513 | 0,25 |
| **Tâm có trọng số** | | | | **6.342** | 6.534 | |
| **Sau thanh khoản 10%** (ước lượng) | | | | **5.708** | 5.881 | |

**Cơ sở B′ làm kịch bản trung tâm thay B:** KL TTCP nêu **cả hai** nhà máy (Bầu Ngứ FIT1 sai đối tượng; Núi Một 1 FIT2 trái TB 402/2019); r1 chỉ phạt một trong hai.
Cấu trúc r2 = A / B / **B′** / C (B giữ lại làm biên lạc quan có điều kiện, không xoá).
**Vùng đọc (sau thanh khoản, tâm 5.708):** ≤ **4.850** (= 0,85 × tâm) = vùng có biên an toàn **CHỈ KHI** đủ điều kiện HARD ABANDON §4 · 4.850–6.340 hợp lý ·
> 6.340 = trả cho xác suất giữ FIT cao hơn trọng số r2. Nếu thị trường chỉ cân A/B thì 10.250 ngầm định P(A) ≥ ~67% (tính: p·12.651+(1−p)·8.821 = 10.250/0,9 = 11.389).
**§2/§2.5 chạy tường minh (Phụ lục A): NON** — TTA KHÔNG vào sleeve fear-buy; mọi "vùng có biên an toàn" ở trên là tham chiếu định giá, **không** phải điều kiện mở vị thế sleeve.
**Pháp lý: WARNING.** Moat: NONE.

## 1. Danh sách đính chính (7 điểm của skeptic)

| # | Điểm | Xử lý r2 | Tác động |
|---|---|---|---|
| 1 | Thiếu B′ | Thêm B′; kiểm lại: skeptic 4.823 (PH=0, FX 25.755 cho hồi tố) vs r2 **PH=0: 5.051** — chênh do tỷ giá lịch sử (hồi tố B′ 674 vs 715 ⇒ +230 đ) | B′ = 5.559 (PH 90,7) |
| 2 | Trọng số mượn S1/S2 Bobby | Bỏ; neo hành vi trả EPTC §3 + bảng độ nhạy | tâm 8.040 → 6.342 |
| 3 | Hồi tố 5 năm không lãi + phải thu cộng t=0 | V1 bù trừ ngay (chính), V2 trả góp có lãi 8,4% (cận trên) — §2 | xem bảng |
| 3b | Tỷ giá | Hồi tố dùng TB năm lịch sử (`data/macro_usdvnd.csv`), không 25.755 | hồi tố ↓ (B 394→385; C 1.149→1.053) |
| 4 | Phước Hoà đặt 0 = xoá sổ | Đặt **sổ sách 95,7 − 5 (vốn bên ngoài) = 90,7** (NPV=0), độ nhạy =0 và =95,7 | +508 đ so với r1 (B, C) |
| 5 | Nhãn EPS, 183,6 vs 169,6, kiểm toán | §5 | nhãn/độ tin cậy |
| 6 | §2/§2.5 | Phụ lục A: NON; HARD ABANDON §4 | |
| 7 | HTKD, bên liên quan, Đức, nhóm Chiến | §6 | chưa kiểm được — nêu rõ |

## 2. Mô hình r2 (đo — `model/dcf_tta_r2.py`)

**Hồi tố (tỷ):** BN→FIT2 **385** · NM1→trần **290** · BN→trần **763** ⇒ B′ **674** · C **1.053**. Tỷ giá TB năm 2019–2026 = 23.179 / 23.228 / 22.905 / 23.400 /
23.824 / 25.041 / 25.987 / 26.189 (2026 chỉ tới 29/4 — dữ liệu local dừng ở đó; **ước lượng** cho tỷ giá EVN thực áp; tỷ giá hợp đồng thực chưa kiểm).
Thời gian hưởng giá sai tính tới 31/12/2026: BN từ 12/11/2019 (≈7,13 năm), NM1 từ 06/11/2020 (≈6,15 năm); sản lượng 98/85 GWh phẳng (ước lượng, không có số thực).
Dòng tiền tương lai vẫn đổi USD theo 25.755 như r1.
**Xử lý hồi tố (điểm 3):** V1 (chính) = cộng `phải thu vượt 330 (ước lượng) − hồi tố` ngay t=0 (hồi tố lớn hơn phải thu ⇒ số âm = nộp thêm ngay); V2 = phải thu 330 thu ngay,
hồi tố trả đều 5 năm **kèm lãi 8,4%** trên dư nợ còn lại (cận lạc quan vì phải thu thu ngay nhưng nợ trả dần). Skeptic dự đoán "B 8.263 / C 129 / B′ 4.823" (PH=0): r2 chạy PH=0 V1
ra **B 8.313 / B′ 5.051 / C 667** — chênh còn lại = tỷ giá lịch sử (hồi tố thấp hơn 9–96 tỷ). Khớp hướng, không chép số.
**Phước Hoà:** NPV=0 ⇒ giá trị = vốn đã bỏ (95,7), trừ 5 tỷ vốn bên ngoài (bà Nguyễn Thị Thanh, [Q3 tr.21]; BCTC không nói đó là nợ hay góp vốn ⇒ trừ để thận trọng, ước lượng).
Độ nhạy: PH=0 ⇒ B′ **5.051**; PH=95,7 ⇒ **5.587** (±~510 đ). Vốn còn phải bỏ thêm (19,9 tỷ trong 9T) không mô hình hoá — nếu tiếp tục, giá trị sổ sách có thể trượt.
**Độ nhạy khác (B′, V1):** thuỷ điện −20% **3.546** / +20% **7.549** · r −100bp **6.007** / +100bp **5.156** · lãi vay +1pp **5.338** · phải thu vượt =0: B′ **3.711**, C **−674** (VCSH âm).
**DSCR 2027 trước hồi tố** (EBITDA−capex 30)/(lãi+gốc 280): A **1,36** · B **1,22** · B′ **1,09** · C **0,79**; B′ với trả hồi tố 5 năm (≈135 tỷ/năm V2) < 1 ⇒ **cần giãn nợ/tái cấp vốn ở B′ nếu EVN đòi trả tiền mặt thay vì bù trừ**.
Kiểm độc lập: dựng lại B′ V1 bằng numpy tách riêng (hồi tố 674,4; 5.559 đ) = khớp mô hình.

## 3. Trọng số — neo hành vi thanh toán thực tế EPTC (điểm 2)

**Không dùng S1/S2 Bobby** (đó là nhóm 173 nhà máy thiếu CCA, rủi ro khác nhóm FIT sai đối tượng — r1 :102-104). Cơ sở dữ liệu riêng của TTA:

| Đo | Giá trị | Nguồn |
|---|---|---|
| Phải thu EPTC | 77,1 (cuối 2024) → 237,7 (cuối 2025) → **399,6** (30/9/2026) | [KT25], [Q3 tr.18]; số 77,1 lấy từ yêu cầu dispatch — **chưa kiểm lại trong PDF** |
| Tỷ lệ EPTC thực trả hoá đơn mặt trời | 2025 **~62%** (ngụ ý: tăng 160,6 / hoá đơn ~423 ⇒ trả 62% nếu hoá đơn ≈ 391×1,08); 9T/2026 **49,3%** (hoá đơn 295,5×1,08 = 319,1; phải thu +161,9 ⇒ trả 157,2) | đo từ [Q3] (tính được); 2025 là **ước lượng** (không có DT mặt trời 2025 riêng ở đây) |
| Tỷ lệ trả ngụ ý theo kịch bản (so với doanh thu FIT đầy đủ 391 tỷ/năm) | A 100% · B **85,4%** · B′ **71,5%** · C **55,4%** | tính từ giá kịch bản |

**Đọc:** hành vi thanh toán thực (62% → 49%) nằm ở/ dưới kịch bản C và đang **xấu đi**, không khớp trọng số nặng A/B. Nhưng đây **không phải xác suất kết quả**: (i) N = 2 quan sát,
1 bên mua, 2 nhà máy; (ii) không phân biệt được "EPTC trả tạm theo giá thấp chờ kết luận" với "chậm trả"; (iii) EPTC có thể trả bù khi có văn bản (r1 M1/M2 đã nêu). Vì vậy:
**trọng số 0,15/0,25/0,35/0,25 là PHÁN ĐOÁN (ước lượng)** — đặt A thấp (0,15) vì hành vi trả hiện nay trái hẳn A; dồn vào B′ vì KL TTCP nêu cả hai; giữ C ở 0,25 vì thanh toán thực đã ngang C.
Trọng số này gắn với tỷ lệ trả ngụ ý bình quân **75%** — vẫn **cao hơn** hành vi thanh toán thực (49–62%) ⇒ khá lạc quan chứ không bi quan.
Các mốc M1 (BCTC Q4/2026) và M2 (văn bản FIT) sẽ cập nhật trọng số — không cập nhật theo giá.

**Bảng độ nhạy trọng số (V1; đ/cp trước TK → sau TK):**
| Bộ trọng số A/B/B′/C | Tỷ lệ trả TB | Tâm | Sau TK | ×0,85 |
|---|---|---|---|---|
| **central 0,15/0,25/0,35/0,25** | 0,75 | **6.342** | **5.708** | 4.852 |
| lạc quan 0,25/0,30/0,30/0,15 | 0,80 | 7.653 | 6.888 | 5.855 |
| r1-style 0,25/0,50/0/0,25 (không B′) | 0,81 | 7.867 | 7.080 | 6.018 |
| A/B′/C 0,25/0/0,50/0,25 (skeptic) | 0,75 | 6.236 | 5.612 | 4.771 |
| đều 0,25×4 | 0,78 | 7.052 | 6.347 | 5.395 |
| bi quan 0,10/0,15/0,35/0,40 | 0,70 | 5.004 | 4.504 | 3.828 |
| khớp hành vi trả 0/0/0,5/0,5 | 0,64 | 3.367 | 3.030 | 2.576 |
Lưới sau TK (V1) theo P(A) × P(C), phần còn lại chia B:B′ = 1:1,4: P(A) 0,15 × P(C) 0,10…0,40 = 6.484 / 5.967 / 5.709 / 5.450 / 4.933 · P(A) 0,25 = 7.000 … 5.449 · P(A) 0 = 5.711 … 4.159.
**Mọi ô P(A) ≤ 0,35 đều cho sau-TK ≤ 7.516 < 10.250** ⇒ kết luận "KHÔNG RẺ" bền với trọng số; **mức số** nhạy ~±520 đ theo P(A) ±0,10 và ~±520 đ theo P(C) ±0,10 (đo từ lưới).
Skeptic ước tâm ~6.550 / sau TK ~5.900 / biên ~5.010 (nếu A/B→B′ giữ 0,25/0,50/0,25): kiểm với 0,25/0/0,50/0,25 ra **6.236 / 5.612 / 4.771** (Phước Hoà 90,7 thay 0 và tỷ giá lịch sử khác); với cấu trúc 4 nhánh trung tâm r2 **6.342 / 5.708 / 4.852** — cùng vùng biên an toàn ~4.770–5.020, không chép.

## 4. Vùng đọc + HARD ABANDON (bắt buộc nếu còn nêu "vùng có biên an toàn")

Vùng (sau TK, V1): **biên an toàn ≤ 4.850** · hợp lý **4.850–6.340** · **trên 6.340 = trả thêm cho xác suất giữ FIT**. Thanh khoản: ADV trung vị **1,07 tỷ/phiên** (BQ 68 phiên 13/08–19/11/2026: trung vị 102.100 cp, TB 152.012 cp) ⇒
vị thế 1–2 tỷ ở 10–20% tham gia = **5–19 phiên** thoát; sizing ≤0,5% NAV, chỉ khi đã qua cổng dưới.
**HARD ABANDON — viết thành ĐIỀU KIỆN BẮT BUỘC (một điều kiện kích hoạt = bỏ phân tích mua, không "chờ thêm"):**
1. Phải thu EPTC **> 450 tỷ** (BCTC Q4/2026 hoặc bất kỳ kỳ nào) hoặc DT mặt trời bị giảm/ trích dự phòng.
2. Có **văn bản hồi tố đối với Núi Một 1** (hoặc Bầu Ngứ) — chuyển P(B′/C) lên ≥ 0,70 ⇒ xem lại, không mua trước khi định giá lại.
3. **Vi phạm covenant, giãn/hoãn nợ, hoặc cần tái cấp vốn** (DSCR 2027 B′ ≈ 1,09 trước hồi tố).
4. Nhóm Đinh Quang Chiến chào mua công khai / kiểm soát tranh chấp làm tê liệt HĐQT (r1 M5) — định giá không áp được.
5. Kiểm toán 2026 ngoại trừ/nhấn mạnh về phải thu EPTC hoặc FIT.
Điều kiện **tốt hơn** (hai chiều như r1): phải thu EPTC < 300 tỷ (EVN trả phần giữ) hoặc văn bản giữ FIT cho dự án đã COD ⇒ tâm +~1.000 (r1 M1) — tính lại bằng r2.

## 5. Nhãn nguồn, kiểm toán, brief (điểm 5)

- **EPS 949,68 đ/cp 9T/2026:** **không phải số in trong BCTC** — [Q3 tr.28] ô "Lãi cơ bản" năm nay in **"-"** (năm trước in 849,10). 949,68 = **tự tính (183,61 − 14,04) ÷ 178,559** = 169,57 tỷ ÷ 178,559 tr cp (đo).
  Kiểm cùng cách 9T/2025: (165,43 − 13,82)/178,559 = **849,1** = đúng số in ⇒ cách tính đúng.
- **183,6 vs 169,6:** 183,6 = LNST phân bổ cho cổ đông phổ thông **trước** trích quỹ khen thưởng phúc lợi; **169,6 = sau** quỹ KTPL 14,04 (cơ sở EPS). TTM EPS 1.145 (r1) dùng sau-quỹ ⇒ P/E **8,9** nhất quán; mọi chỗ khác dùng 183,6 phải ghi "trước quỹ".
- **Kiểm toán 2025 "chấp nhận toàn phần" — BỎ khỏi điểm trấn an.** Bằng chứng yếu: doanh thu ghi đủ FIT trong khi EPTC giữ ~50% tiền và không trích dự phòng; kiểm toán viên (NTV) là công ty nhỏ; ý kiến toàn phần không bác được rủi ro hồi tố vì chưa có văn bản.
- **Brief sửa:** Bầu Ngứ là điện mặt trời **mặt đất trong lòng hồ thuỷ lợi (~73,7–75 ha)**, không phải điện mặt trời nổi.
- **ADV:** 1,07 tỷ/phiên (68 phiên), thay 0,94 (62 phiên) của r1.

## 6. Kiểm chứng/đề xuất (điểm 7)

| Câu hỏi | Kết quả kiểm | Đề xuất |
|---|---|---|
| 6 cá nhân HTKD có phải bên liên quan? | Danh sách bên liên quan Q3 [tr.28-29] gồm: Cty TNHH XD Trường Thành, TNHH ĐT Xây lắp Trường Thành, Phong điện Phương Mai + HĐQT/BĐH (Nguyễn Thị Ngọc, Trần Huyền Trang, Nguyễn Văn Trường, Nguyễn Duy Hưng; năm trước thêm Nguyễn Thanh Hà). **6 người HTKD (Cao Đăng Kiểu, Trâu Kiến Hoa, Daniel Triệu, Tô Thanh Hà, Nguyễn Duy Viễn, Phạm Mạnh Thắng) KHÔNG có tên.** Họ trùng (Nguyễn Duy Viễn/Hưng; Thanh Hà) **không đủ để kết luận** quan hệ — chưa xác lập | Đối chiếu BCTN 2025/ danh sách cổ đông; hỏi IR; hỏi kiểm toán về phạm vi "bên liên quan" |
| Thời hạn HTKD | BCTC **không nêu** thời hạn/điều khoản thoái | Cần hợp đồng HTKD (CBTT bất thường nếu có); M3 r1 |
| Chuyển giao tài sản/nợ của cựu CT Trần Huy Đức (23,26% theo báo chí, chưa đối chiếu) | Chỉ có câu trong [KT25 tr.3] (đã hoàn tất chuyển giao nghĩa vụ nợ; đang chuyển giao tài sản) — người nhận, giá, lý do **không nêu** | Tìm CBTT thay đổi sở hữu của ông Đức và các bên nhận; kiểm có thế chấp cổ phiếu/margin |
| Nhóm Đinh Quang Chiến 20,04% | [TX 25/08/2026]: mục đích không công bố; cùng kỳ ông Đức chuyển giao | Theo dõi báo cáo sở hữu tiếp theo; kiểm có quan hệ với phía nhận chuyển giao — **chưa kiểm được** |
| Quỹ KTPL/BĐH & HTKD tương lai | Phải trả HTKD tồn 29,4 tỷ [Q3 tr.21] | Theo dõi tăng nhanh bất thường |

## Phụ lục A — Chạy §2 / §2.5 tường minh (hồ sơ nội bộ; `calculated_fear_state_backstop.md`)

**§2 (nhóm a — scandal cá nhân): KHÔNG ĐỦ ĐIỀU KIỆN (1/5 đạt).**
| # | Tiêu chí | TTA | Kết |
|---|---|---|---|
| 1 | Scandal là CÁ NHÂN | **Không** — rủi ro là doanh thu 2 nhà máy lõi bị tính lại (pháp nhân/tài sản), không phải hành vi cá nhân lãnh đạo | ❌ |
| 2 | NN/chiến lược >50% có backstop | **Không** — tư nhân, cổ đông lớn 23,63%/23,26%/20,04%; EVN là người mua đang giữ tiền, không phải backstop | ❌ |
| 3 | Tài sản lõi tách biệt + CF_OA ≥ NP | CFO 9T/2026 **159,0 < LNST 206,7** (77%); 2025 236,3 ≈ 231,6; phải thu +167,3 | ❌ (9T/26) |
| 4 | Solvent | Nợ ròng/EBITDA **2,3x**; DSCR 2027 **1,36 (A) → 1,09 (B′) → 0,79 (C)** | ⚠️ (C: không tự trả) |
| 5 | Sàn định giá PB ≲1,2 / PE<5 | PB **0,72**; P/E **8,9** (không <5); sổ sách chứa DT FIT chưa thu | ⚠️ |
Mục "KHÔNG ĐỦ": scandal lan vào tài sản lõi (FIT 51% DT) **✔ vi phạm**; DN tư nhân không backstop **✔ vi phạm**.

**§2.5 (nhóm b/c/d):**
| # | Tiêu chí | TTA | Kết |
|---|---|---|---|
| 1 | Chu kỳ, không cấu trúc | Giá FIT bị tính lại là **quyết định hành chính cấu trúc** (không có chu kỳ để chờ quay lại) | ❌ |
| 2 | Bảng cân đối sống qua đáy | C: DSCR 0,79 ⇒ tái cấp vốn/pha loãng; TSCĐ ~100% thế chấp | ❌ (C) |
| 3 | DN dẫn đầu chi phí | Price-taker IPP; ROIC_Min5Y 4,6–8,4% < Ke 13,5% (moat NONE) | ❌ |
| 4 | Sàn bằng tài sản thực | TSCĐ 3.461 tỷ hữu hình nhưng giá trị phụ thuộc giá FIT ⇒ không phải sàn thanh lý | ⚠️ |
Mục "KHÔNG ĐỦ": khủng hoảng cấu trúc ✔; bảng cân đối không sống nổi ở C ✔; "rẻ" chỉ vì sổ sách chứa doanh thu chưa thu ✔.
**Phán quyết: NON** (khớp dự đoán skeptic) — không đưa vào sleeve fear-buy; chỉ là DD định giá.

## Phụ lục B — Giới hạn
- Chưa qua fundamental-skeptic r2. Chưa ghi `dd_price_zones.json`. Không email.
- Tỷ giá local dừng 29/4/2026; tỷ giá EVN thực, sản lượng thực, giá EPTC trả tạm, ĐK HTKD: **chưa đo/chưa có**. Phải thu EPTC 77,1 (2024) từ dispatch chưa đối chiếu PDF.
- Cặp V1/V2 là hai giả định xử lý hồi tố, không phải dự báo; thực tế (bù trừ thật, có lãi hay không) phụ thuộc văn bản.
