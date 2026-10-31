# TCH DD — Vòng bổ sung thông tin (GAPS) · 31/10/2026 · job `Taylor_20261031_145612`

> Bổ sung cho `REPORT.md` v1 (job `Taylor_20261031_141634`), **không sửa v1**. Nghiên cứu chỉ đọc. Pháp lý ⇒ vẫn phân tích, chỉ gắn WARNING.
> **Nguồn gốc:** 27 PDF tải từ hoanghuy.vn ngày 31/10/2026 → `src/gaps/pdf/`; ảnh trang đã đọc → `src/gaps/img/`. Chỉ BCTN 2025 có lớp text (`src/gaps/bctn25.txt`), còn lại là **scan** nên đọc bằng mắt từ ảnh pymupdf.
> Giá CRV/HHS/TCH lấy từ **DNSE API** read-only (`DNSEClient.ohlc` / `latest_trade`) → `calc/dnse_ohlc_{CRV,HHS,TCH}.json`. Phép tính: `calc/gaps_calc.py` → `calc/gaps_calc_out.txt`. Số gắn "ước lượng" là chưa đo.
> Viết tắt: **[NQ26]** = `20260724 - tch - nghi quyet dhdcd thuong nien 2026 va tai lieu kem theo.pdf` (trang PDF) · **[BCTN25]** = BCTN 2025 (trang PDF) · **[QT6T26]** = BC tình hình quản trị 6 tháng 2026 · **[RIENG]** = BCTC riêng 01/04–30/09/2026.

---

## TÓM TẮT — 5 điều đổi so với v1
1. **Phép thử SOTP qua giá CRV ở v1 (§8d, 10.700 đ/cp) KHÔNG DÙNG ĐƯỢC.**
   - CRV chỉ khớp lệnh **24/62 phiên** từ 03/08 đến 30/10/2026. Bình quân 1.454 cp/phiên; tổng giá trị khoảng **0,8 tỷ đ trong 3 tháng**. Giao dịch cuối là 21/10/2026 ở 23.000.
   - Ở giá đó CRV có P/B 2,06x và P/E FY25 205x. Đây không phải giá thị trường.
   - Thay bằng **SOTP hỗn hợp: ~11.200 đ/cp, −5,5% so với giá** (ước lượng, chi tiết ở mục 4).
2. **WARNING mới: QĐ 1020/QĐ-XPHC ngày 03/04/2026 của Thuế TP Hải Phòng.**
   - Nội dung: khai sai căn cứ tính thuế TNDN. Phạt 2,735 tỷ + truy thu 13,676 tỷ + chậm nộp 3,798 tỷ = **20,21 tỷ** (~20 đ/cp).
   - Chưa có trong v1. Tiền nhỏ, nhưng là **vi phạm tuân thủ thứ hai trong 16 tháng**, sau án UBCKNN 12/2024.
3. **WARNING "scandal di cư" GIẢM một bậc trong nội bộ mức trung bình.**
   - Giao dịch bên liên quan **đang được công bố**: BCTN 2025 tr.37 (13 dòng), BC quản trị 6T 2026 tr.9–15, 3 NQ HĐQT (16/04, 23/06, 21/07/2026).
   - Mọi giao dịch đều là **nội bộ tập đoàn** (công ty con). Vì vậy BCTC hợp nhất ghi "bên liên quan: –" là đúng: các giao dịch này đã bị loại trừ khi hợp nhất.
   - BC quản trị: "giao dịch giữa công ty với đối tượng khác: Không", "giao dịch cổ phiếu của người nội bộ: Không".
4. **HH Finance (5,81%) là người liên quan của ông Đỗ Hữu Hạ.** Ông là Chủ tịch HĐQT kiêm TGĐ HH Finance từ 06/2025 [BCTN25 tr.32].
   - Nhóm kiểm soát (2 cổ đông lớn) nắm **35,99%**, chiếm **71,2% số phiếu dự ĐHĐCĐ 2026** (đại hội chỉ có 50,51% cổ phần tham dự).
5. **Nhóm Dragon Capital (8 quỹ) bán ròng xuống 4,71%, không còn là cổ đông lớn từ 15/06/2026.** Đây là nguồn cung cổ phiếu có tổ chức, đã kéo dài từ 12/2025 (6 báo cáo thay đổi sở hữu).

**Tác động lên vùng giá v1 (9.600–14.400, tâm ~11.600–11.950):** giữ vùng, **nghiêng tâm về cận dưới ~11.600**. Lý do:
- Bỏ phép thử CRV (10.700, từng là "neo trên" cho phần ngoài CRV).
- SOTP hỗn hợp mới cho ~11.200 (ước lượng).
- WARNING thuế mới bù trừ với WARNING bên liên quan đã giảm.

Không đổi mốc M1–M6. Thêm M7 (sử dụng vốn chào bán).

---

## 1. Kế hoạch FY2026 gốc (NQ ĐHĐCĐ thường niên 2026)
**Câu hỏi:** chỉ tiêu DT/LNST là hợp nhất hay của công ty mẹ? Cổ tức, cổ phiếu thưởng, uỷ quyền, thù lao?

**Bằng chứng:**
- NQ số 01/2026/NQ-ĐHĐCĐ ngày **24/07/2026** [NQ26 tr.3–4], họp tại 116 Nguyễn Đức Cảnh, kết hợp trực tuyến.
  - **48 cổ đông dự, đại diện 460.731.803 cp = 50,5128%** số cp có quyền biểu quyết.
  - Mọi tờ trình đều thông qua ~99,98–100% số phiếu dự [NQ26 tr.7–10].
- **Kế hoạch FY26 (01/04/2026–31/03/2027), bảng "Các chỉ tiêu HỢP NHẤT"** [NQ26 tr.34, BC 01/2026/BC-TGĐ]: DTT bán hàng & CCDV **5.000 tỷ**; **LNST 2.000 tỷ (hợp nhất, gồm NCI)**; tỷ lệ cổ tức **10%**.
  - Cùng số trong BCTN25 tr.27 ("Kế hoạch kinh doanh năm 2026").
  - Thực hiện FY25: DTT 1.447 / KH 5.000 = **28,94%**; LNST 259 / KH 1.700 = **15,24%** [NQ26 tr.34].
- **Phân phối lợi nhuận FY25** (tờ trình 03/2026/TT-HĐQT) [NQ26 tr.44–45]:
  - Dựa trên LNST chưa phân phối của **công ty mẹ** 423,62 tỷ tại 31/03/2026 (nhỏ hơn số hợp nhất), cộng thặng dư 843,57 tỷ.
  - Dùng để **phát hành cp thưởng 10:1**. Không trả cổ tức tiền.
  - Cổ tức FY26 "dự kiến 10%". **Không ghi tiền hay cổ phiếu**; ĐHĐCĐ năm sau sẽ quyết hình thức.
- **Kiểm toán FY26** (tờ trình 02/2026/TT-BKS) [NQ26 tr.49]:
  - Uỷ quyền **TGĐ** chọn trong 9 công ty: Deloitte, AASC, E&Y, PwC, A&C, KPMG, Grant Thornton, IAV, VAE.
  - TCH đã ký với **AASC** HĐ 100826.001/HĐTC.KT7 ngày 10/08/2026, gồm cả **soát xét** bán niên và kiểm toán năm [CBTT 10/08/2026].
- **Thù lao** (tờ trình 05/2026) [NQ26 tr.50–51]: Chủ tịch HĐQT 120 tr/năm, thành viên HĐQT 60 tr/năm, Trưởng BKS 60 tr, thành viên BKS 36 tr. Bằng mức thực chi 2025 [BCTN25 tr.37].
- Không thấy nội dung niêm yết mới, phát hành riêng lẻ, ESOP, hay uỷ quyền HĐQT vay/bảo lãnh lớn trong 9 điều của NQ.

**Kết luận:**
- KH FY26 là **LNST HỢP NHẤT 2.000**, nên LN mẹ hàm ý chỉ khoảng 1.400–1.450 (giả định NCI ~28% như 6T, ước lượng).
- Tỷ lệ hoàn thành 6T theo v1 giữ nguyên: **LNST HN 914,29 = 45,7%**, **DT 2.414 = 48,3%**.
- Cổ tức thực tế là cp thưởng (pha loãng 10%), **không có tiền**.

**Tác động:** không đổi NAV. Xoá dòng "chưa rõ hợp nhất hay mẹ" ở v1 §2/§4. M4 giữ nguyên.

## 2. BCTN 2025 + BC quản trị: giao dịch bên liên quan, cổ đông, HĐQT
**Bằng chứng:**
- **Giao dịch với người nội bộ, FY25** [BCTN25 tr.37, bảng 13 dòng; tất cả "Công ty con"]:
  - Doanh thu cho thuê văn phòng: Đại Thịnh Vượng 108 tr; Đại Lộc 108 tr; Hoàng Giang 60 tr; Thịnh Hiệp 109,1 tr; Thịnh Phát 109,1 tr; Pruksa VN 216 tr; HHS 630 tr; CRV 700,66 tr.
  - Lãi cho CRV vay 5,49 tỷ. **CRV trả cổ tức cho TCH 153,66 tỷ**. CRV trả nợ vay cho TCH 316,5 tỷ.
  - **TCH mua cp HHS phát hành thêm 800 tỷ**; mua cp CRV phát hành thêm 166,47 tỷ.
  - Không có giao dịch cổ phiếu của cổ đông nội bộ trong năm.
- **6T 2026** [QT6T26 tr.9–15, NQ HĐQT]:
  - Thuê VP với các công ty con: căn cứ **NQ 06/2023/NQ-HĐQT ngày 24/07/2023**, chính là NQ "duyệt muộn" trong án phạt 2024, nay được viện dẫn công khai.
  - NQ 02/2026 (16/04/2026): TCH nhận chuyển nhượng HĐ tiền gửi 177,5 tỷ của CRV. QT6T26 ghi Đại Lộc chuyển HĐ tiền gửi **536,55 tỷ** cho TCH (tháng 5/2026).
  - NQ 05/2026 (23/06/2026): **TCH cho CRV vay tối đa 500 tỷ**, lãi thả nổi do TGĐ quyết, kỳ hạn 1 năm. Đã giải ngân 30 tỷ (6/2026), lãi 57,53 tr.
  - NQ 06/2026 (21/07/2026): TCH cho HHS vay tối đa 100 tỷ, cùng điều khoản.
  - 01/2026: tập đoàn mua cp CRV phát hành thêm: TCH 166,47; HHS 153,71; Hoàng Giang 36,77; HHS Capital 32,57 tỷ (**tổng 389,5 tỷ**).
  - QT6T26 tr.16: giao dịch với đối tượng khác: **Không**; giao dịch cp của người nội bộ: **Không**.
- **Cổ đông** tại 22/06/2026 (912.109.224 cp, trước thưởng) [BCTN25 tr.21]:
  - 2 cổ đông lớn **328.247.206 cp = 35,99%**: Đỗ Hữu Hạ 275.227.036 (30,17%) + phần còn lại 53.020.170 (5,81%), khớp HH Finance.
  - Nước ngoài **95.891.809 = 10,51%** (40 tổ chức 10,36%); room **51%** (CV 2759/UBCK-PTTT 10/06/2021).
  - Không có cp quỹ, không có cp hạn chế chuyển nhượng.
- **HH Finance:** ông Hạ là "Chủ tịch HĐQT kiêm Tổng giám đốc CTCP HH Finance, 06/2025 – nay" [BCTN25 tr.32] ⇒ **người có liên quan** theo Luật CK.
- **HĐQT** (5 người, bổ nhiệm 05/07/2022) [BCTN25 tr.32]:
  - Đỗ Hữu Hạ (Chủ tịch, 30,17%); Nguyễn Thị Hà (4,89% = 44,59 tr cp); Phạm Hồng Dung (0%); Đỗ Hữu Hưng (0,38%, kiêm PTGĐ); Phan Thị Phương Thủy (độc lập).
  - Bà Nguyễn Thị Hà: thủ quỹ Cty TNHH TM Hoàng Huy 1995–2004, thành viên HĐQT từ 2007. **BCTN không nêu quan hệ gia đình với ông Hạ.** Nếu có quan hệ, nhóm kiểm soát lên ~40,9%. **Chưa xác minh, không suy diễn.**
  - TGĐ là bà Hoàng Thị Huyên (thu nhập 2025: 420,8 tr). PTGĐ Đỗ Hữu Hậu 925 tr, Đỗ Hữu Hưng 992,9 tr [BCTN25 tr.37].
  - Trưởng BKS Vũ Thị Huyền đồng thời là Kế toán trưởng CTCP Đầu tư Tô Hiệu (công ty con) [BCTN25 tr.35] ⇒ **độc lập của BKS yếu**.

**Kết luận:**
- Các loại giao dịch từng bị phạt năm 2024 (thuê VP, cổ tức CRV, góp vốn) **nay đã được công bố đầy đủ**. "Di cư" sang dạng che giấu: **không thấy**.
- Rủi ro còn lại là **dòng tiền nội bộ giữa các tầng có cổ đông thiểu số khác nhau**. TCH (mẹ) cho CRV vay tới 500 tỷ và cho HHS vay tới 100 tỷ, lãi do TGĐ quyết. Lãi này chuyển giá trị giữa cổ đông TCH và cổ đông thiểu số CRV/HHS. Quy mô hiện nhỏ (đã giải ngân 30 tỷ).
- BKS kiêm nhiệm ở công ty con.

**Tác động:** WARNING quản trị **giữ "trung bình"**, nhưng gỡ ý "có thể đang di cư". Đề xuất M6 bỏ vế "BC quản trị bán niên 2026 liệt kê giao dịch bên liên quan" vì đã đạt. Theo khung §9 v1 (mỗi 5 điểm % chiết khấu quản trị ≈ ±750 đ), mức giảm này đáng khoảng +0 đến +750 đ. **Tôi chỉ cộng 0**, vì án thuế mới (mục 9) bù trừ.

## 3. Nhóm uỷ quyền 7,37% biểu quyết tại CRV; hồ sơ CRV
**Bằng chứng:**
- Báo chí (Viettimes 26/03/2025): tại Q1/2025, TCH nắm 256,1 tr cp CRV (38,1%), HHS 236,4 tr (35,17%), Hoàng Giang 56,6 tr (8,41%). **Nhóm Hoàng Huy: 549,1 tr cp = 81,7%.** https://viettimes.vn/hoang-huy-group-quyet-dinh-chon-me-cho-bat-dong-san-crv-post183958.html
- Mekong ASEAN: HHS nắm 51% CRV từ 18/06/2025, trở thành công ty mẹ.
- **CRV** [BCTN25 tr.19]: vốn điều lệ thực góp **6.784 tỷ**; TTS 11.987; nợ 4.408; **VCSH 7.579** (31/03/2026). LN hợp nhất FY24 462,32, FY25 76,23. NC-II tổng mức đầu tư **15.076 tỷ**.
- **Giá/KL CRV** [DNSE OHLC 03/08–30/10/2026]: 24 phiên có khớp / 62; bình quân 1.454 cp, trung vị 600 cp/phiên; giá 22.100–26.700; cuối 23.000 (21/10/2026, 800 cp).
  ⇒ **Free-float thực tế gần 0.** Nhóm tập đoàn nắm ≥81,7% (cộng thêm phần mua phát hành thêm 01/2026).
- **Danh tính nhóm uỷ quyền 7,37%: KHÔNG TÌM ĐƯỢC.** Đã tra:
  - BCTN 2025 (text, toàn văn): không nhắc.
  - NQ ĐHĐCĐ 2026, BC quản trị 6T 2026/năm 2025 (tr.1–16): không nhắc.
  - Web: vietnamfinance, baophapluat, nhadautu, mekongasean, viettimes.
  - Bản cáo bạch niêm yết CRV 2025: chỉ thấy tên trên simplize.vn, **không tải được nội dung**.
  - Chưa đọc BCTC HHS (nơi khoản uỷ quyền tạo kiểm soát), cũng chưa đọc trang CBTT của CRV.
- Lịch sử cổ tức CRV: chỉ thấy FY25 trả cho TCH **153,66 tỷ** [BCTN25 tr.37] và 2022 (320 + 66,5 tỷ, theo án phạt 2024). Kế hoạch 2026 của CRV: **không tìm được**.

**Kết luận:**
- Theo cấu trúc sở hữu báo chí đưa, phần sở hữu trực tiếp của tập đoàn (~81,7% vốn) đã **vượt 50%**. Vì vậy rủi ro "mất kiểm soát CRV nếu uỷ quyền bị thu hồi" là **thấp** ở cấp TCH: TCH vẫn hợp nhất CRV qua chuỗi sở hữu.
- 7,37% uỷ quyền có vẻ chủ yếu quyết định **tầng nào** hợp nhất CRV (HHS hay TCH trực tiếp), không quyết định TCH có hợp nhất hay không. Đây là **suy luận, chưa xác minh**.

**Tác động:** hạ cờ §6a v1 từ "cần kiểm" xuống "rủi ro thấp, danh tính vẫn chưa rõ". **Bỏ §8d (CRV look-through 10.700)**: giá CRV không có ý nghĩa định giá.

## 4. Mảng ô tô (HHS 58,31%) — SOTP qua HHS
**Bằng chứng:**
- HHS niêm yết **HOSE**, 431.985.968 cp [BQ `ticker_financial`]. Đóng cửa 30/10/2026 **9.450 đ** [BQ `ticker` + DNSE]. ADV 62 phiên khoảng 1,11 tr cp.
  ⇒ **Vốn hoá 4.082 tỷ**; phần TCH 58,31% = **2.380 tỷ = 2.373 đ/cp TCH**.
- HHS hợp nhất [BCTN25 tr.18]: vốn góp 4.320 tỷ; TTS 23.428; nợ 6.976; VCSH (gồm NCI của CRV) 16.452. LNST hợp nhất 2025 **3.530 tỷ**, phần lớn là lãi kế toán khi nắm quyền kiểm soát CRV (BQ: NP quý 07–09/2025 3.507 tỷ).
  - P/B BQ 0,24 tính trên VCSH gồm NCI, **không so được** với P/B của TCH.
- HHS là nhà phân phối độc quyền xe đầu kéo **International (Navistar, Hoa Kỳ)** [BCTN25 tr.8–9].
- Lý do DT ô tô 6T giảm (359,47 so với 427,83): **không tìm được giải trình chính thức**. CV giải trình 29/10/2026 chỉ giải thích LN hợp nhất. BCTN25 nêu rủi ro: biến động tỷ giá với xe nhập khẩu, thuế/phí, cạnh tranh [BCTN25 tr.15–16].
- **SOTP hỗn hợp** (ước lượng; `calc/gaps_calc_out.txt`):
  - Công ty mẹ trừ khoản đầu tư công ty con: [RIENG] VCSH 10.530,2 − đầu tư con thuần 4.571,6 = **5.958,7**. Gồm Green River, H2, 150 Tô Hiệu, tiền + HTM mẹ 2.244, trừ NMTT mẹ 2.457.
  - Cộng CRV trực tiếp 38,19% × VCSH CRV 31/03/2026 7.579 = **2.894,4** (theo sổ sách).
  - Cộng HHS 58,31% theo **giá thị trường** = **2.380,4**.
  - **= 11.233,5 tỷ = 11.196 đ/cp, −5,5% so với 11.850.**
  - Thiên lệch: (a) VCSH CRV lấy tại 31/03, **chưa gồm LN 6T FY26** (phần lớn LN hợp nhất 914 của 6T nằm ở CRV) ⇒ thấp hơn thực tế, có thể vài trăm đ/cp (ước lượng); (b) phần mẹ tính theo sổ, chưa có thặng dư quỹ đất; (c) dùng giá thị trường HHS ⇒ đã ngầm chứa chiết khấu holding của tầng HHS.

**Kết luận:** thị trường định giá tầng HHS rất thấp: 4.082 tỷ, trong khi chỉ riêng phần lợi ích CRV của HHS theo sổ sách đã khoảng 3.900 tỷ (51,2% × 7.579; tỷ lệ 51,2% suy từ TM1.5, ước lượng). Đây là bằng chứng thị trường cho **chiết khấu holding 2 tầng**, phù hợp mức chiết khấu cơ sở 20% của v1. SOTP hỗn hợp ~11.200 nằm trong vùng v1.

**Tác động:** phép thử chéo mới **ủng hộ tâm ~11.600 hơn ~11.950**.

## 5. Dự án & doanh số ký mới — điểm nhạy nhất của NAV
**Bằng chứng:**
- Không tìm được số căn đã bán/ký của HH1–HH4, Green River, NC-II sau 08/2026 trên website, BCTN hay báo chí.
  - SHS 08/2026: HH1–HH2 đang làm phần hầm, **dự kiến** mở bán Q3/2026.
  - Tin rao môi giới (batdongsan.com.vn, 07/2026) nói "mở booking HH2", giá rao thứ cấp khoảng **50–61 tr/m²**. **Không phải bảng giá chủ đầu tư.**
- Quy mô (website hoanghuy.vn):
  - Green River 32,5 ha: **780 căn liền kề/shophouse + 30 biệt thự + 441 căn NOXH**.
  - New City (giai đoạn I) 8,05 ha: 216 lô liền kề + 149 căn NOXH.
  - HH1–HH4 khoảng **2.494 căn** (Guland, nguồn thứ cấp).
  - H2 Commerce: 36 tầng, khoảng 976 căn (báo, thứ cấp).
  - NC-II tổng mức đầu tư 15.076 tỷ [BCTN25].
- **Tiến độ do công ty báo cáo** (BC sử dụng vốn 29/09/2026, tr.5):
  - Green River: đã xong một số khu liền kề và liền kề sân vườn; đang hoàn thiện phần còn lại; đang thi công khu NOXH. **Hạn dự án hết Q4/2028.**
  - **H2 Commerce: đang thi công phần thân tầng 1–35; hạn hết Q4/2027.** Khớp nhận định H2 ghi nhận từ FY27–28.
- NC-II còn bao nhiêu trong 543 căn thấp tầng đủ điều kiện kinh doanh: **không tìm được**.
- 150 Tô Hiệu, I.14 (mật độ, số căn, pháp lý): ngoài số SHS đã dùng ở v1, **không tìm được thêm**.
- Thị trường Hải Phòng Q3/2026: **không tìm được số Q3**.
  - Có số H1/2026: HPREA cho biết thanh khoản phân hoá, tập trung ở thấp tầng và đấu giá đất; giá chung cư 34 → 40 tr/m² (Q1/2025 → Q1/2026); nguồn cung sơ cấp >20.000 căn đầu 2026 (tổng hợp qua WebSearch; bài gốc: vietnamfinance d147330, nhadautu d102244).

**Kết luận:** chưa có dữ liệu doanh số ký mới, nên điểm nhạy nhất **vẫn mở**. Mốc M3 (NMTT 31/12/2026, công bố ≤15/02/2027) vẫn là nơi đầu tiên đo được.

**Tác động:** không đổi tham số NAV.

## 6. Khối ngoại & thanh khoản
**Bằng chứng:**
- Room 51%. NN nắm 10,51% (22/06/2026) [BCTN25 tr.21]; SHS 08/2026 ghi khoảng 9,5% (sau thưởng, chưa đối chiếu).
- **Dragon Capital** (đại diện bà Trương Ngọc Phượng, 1501 Mê Linh Point) [CBTT 17/06/2026, tr.1–2]:
  - Nhóm 8 quỹ: Amersham, Gates Foundation Trust, Hanoi Investments, **Norges Bank**, Saigon Investments, Samsung VN Securities Master Trust, Vietnam Enterprise Investments, Wareham.
  - Bán 3,23 tr cp ngày 15/06/2026: **5,066% → 4,712%** (42,98 tr cp). Không còn là cổ đông lớn, nên **sau ngày này không còn nghĩa vụ báo cáo**.
  - Trước đó đã có 5 báo cáo thay đổi qua ngưỡng (25/12/2025, 26/02, 26/03, 06/04, 22/05/2026).
- Dòng tiền khối ngoại quanh 21/10 và 29–30/10/2026: **không tìm được**. Đã tra WebSearch (vneconomy, tinnhanhchungkhoan, thesaigontimes: các bài trả về không phải 10/2026 hoặc không có TCH). BQ và DNSE OHLC không có trường khối ngoại.
- Thanh khoản [DNSE 03/08–30/10/2026, 62 phiên]: bình quân **5,42 tr cp/phiên**, trung vị 4,73 tr, khoảng **62 tỷ đ/phiên**. Phiên 30/10: 14,04 tr cp.
- Lý do KL 14 tr ngày 30/10 (tin quỹ/margin/ETF): **không tìm được**. Không có CBTT trên hoanghuy.vn từ 29/10 đến 31/10 ngoài BCTC.

**Tác động:** không đổi NAV. Dragon ra khỏi nhóm cổ đông lớn là bối cảnh cung cổ phiếu (bối cảnh, không phải tín hiệu). Giả thuyết "khối ngoại bán" ở §8e v1 **vẫn chưa đo**.

## 7. BCTC — các điểm treo
- **"Sài Gòn Tài Lộc" 678,32 tỷ** = **Sacombank (STB)**. Bản tiếng Anh TM4 ghi "Saigon Fortune Joint Stock Commercial [Bank]". Sacombank đổi tên thương mại thành "Ngân hàng TMCP Sài Gòn Tài Lộc" theo QĐ 36/QĐ-QLGS4 của NHNN ngày 01/06/2026 (theleader.vn d46210; baodautu d611228). **Đóng điểm treo, không phải rủi ro đối tác.**
- **BCTC bán niên 2025**: trên website ghi "**đã được kiểm toán**", không phải "soát xét" (công bố 28/11/2025, hợp nhất 87 tr + riêng 81 tr + giải trình). Có thể là kiểm toán phục vụ chào bán.
  ⇒ Mốc công bố bán niên năm ngoái là 28/11. **M1 = 30/11/2026 giữ nguyên.**
- **BCTC riêng 6T FY26** [RIENG tr.4–5]:
  - TTS mẹ 13.316; tiền 852,2 + HTM NH 1.392,0 = **2.244,2**; HTK 5.569,1 (đầu năm 3.538,0, +2.031); đầu tư công ty con 4.854,0, dự phòng −282,4.
  - NMTT 2.457,0; **không có vay**; VCSH 10.530,2; LNST chưa phân phối 497,1 (LNST 6T mẹ **141,95**).
  - **Không thấy khoản phải thu cho vay công ty con** đáng kể trên BS mẹ (phải thu khác NH 1,5 tỷ). Khoản cho CRV vay 30 tỷ (06/2026) có thể đã thu hồi hoặc nằm ở chỉ tiêu khác. **Chưa đọc thuyết minh riêng.**
  - Lưu ý: 865,5 tỷ tiền chào bán chưa dùng (mục M7) chiếm **39%** tiền + HTM của mẹ.
- **Cảng Kim Tân** (trả trước 73,7 tỷ): **không tìm được** danh tính. WebSearch không ra pháp nhân này; không có trong danh sách bên liên quan của BCTN/QT6T26. Coi là nhà thầu bên ngoài.
- **Pruksa International 59,43 tỷ**: không có thông tin mới ngoài TM19.
- **Tiền thuê đất hằng năm NC-II** (26.664,2 m² tới 2073): **không tìm được** số nghĩa vụ/năm. BCTC không tách. Chưa ước được vì thiếu bảng giá đất và hệ số K áp cho lô.
- **Sử dụng vốn chào bán 2025 (2.004,6 tỷ)** [BC 29/09/2026 tr.4–5]:
  - Đến 25/09/2026 đã dùng **1.139,1** (Green River 938,9/1.200; H2 200,3/804,6), còn **865,5**.
  - Không đổi mục đích. Tiền đất 150 Tô Hiệu / I.14 **không** lấy từ nguồn này.

## 8. Kiểm toán AASC
- AASC kiểm toán FY25 (ý kiến chấp nhận toàn phần; BTGĐ "không có ý kiến giải trình" [BCTN25 tr.28]) và **tiếp tục FY26** (HĐ 10/08/2026, gồm soát xét). Không có thay đổi kiểm toán.
- ĐHĐCĐ uỷ quyền **TGĐ** chọn kiểm toán, không phải BKS/HĐQT. Kết hợp với việc Trưởng BKS kiêm nhiệm ở công ty con ⇒ **cơ chế giám sát độc lập yếu**. Thuộc WARNING quản trị.
- Ý kiến kiểm toán FY24/FY23: **chưa đọc** (BCTC FY23/FY24 có trên website, chưa tải). Lịch sử AASC trước FY25: **chưa kiểm**.

## 9. Thanh tra / xử phạt 2025–2026
**Phạm vi tra:** trang CBTT hoanghuy.vn (21 mục); WebSearch tiếng Việt "Hoàng Huy TCH xử phạt UBCKNN 2025 2026 / thanh tra / khởi tố Đỗ Hữu Hạ CRV HHS"; mục "số lần bị xử phạt" trong BCTN25. **Chưa tra trực tiếp** trang xử phạt của UBCKNN (ssc.gov.vn) và CBTT của HHS/CRV.

| Sự kiện | Nguồn | Mức |
|---|---|---|
| **QĐ 1020/QĐ-XPHC ngày 03/04/2026, Thuế TP Hải Phòng** — TCH "khai sai căn cứ tính thuế dẫn đến thiếu số thuế TNDN phải nộp" (điểm a k1 Đ142 Luật QLT; k1a Đ16 NĐ 125/2020). Phạt **2.735.112.269 đ** (20% số truy thu) + truy thu TNDN **13.675.561.345 đ** + chậm nộp **3.798.166.882 đ** = **20,21 tỷ**. Không có tình tiết tăng nặng/giảm nhẹ. Căn cứ: biên bản kiểm tra 02/04/2026, đoàn kiểm tra theo QĐ 1504/QĐ-HPH ngày 26/08/2025 | CBTT TCH 07/04/2026 (`20260407 ... xu phat ... thue.pdf` tr.3–4) | **WARNING mới.** Hành chính, không hình sự; tiền nhỏ (0,13% VCSH HN, ~20 đ/cp). Kỳ tính thuế bị kiểm tra: **chưa đọc trang 5**, chưa rõ năm nào |
| UBCKNN QĐ 1357/QĐ-XPHC 05/12/2024 (295 tr) | v1 | đã có |
| Ông Đỗ Hữu Hạ / CRV / HHS: QĐ xử phạt, khởi tố mới 2025–2026 | không tìm thấy trong phạm vi đã tra | — |
| BCTN25 tr.29: "số lần bị xử phạt do không tuân thủ luật về môi trường: không" | | |

**Tác động:** cộng vào WARNING quản trị/tuân thủ. **Hai vi phạm hành chính trong 16 tháng** (CBTT 12/2024, thuế 04/2026). Không đổi NAV (20 tỷ không trọng yếu). Đổi WARNING từ "lịch sử CBTT" thành "**lịch sử tuân thủ (CBTT + thuế)**". Mức vẫn **trung bình**: không gian lận, không khởi tố, kiểm toán sạch.

## 10. Hình ảnh / logo / toạ độ
Chi tiết ở `src/assets_notes.md`.
- (a) `src/logo.png`: cắt từ header hoanghuy.vn, chữ "HOANG HUY GROUP", nền chưa sạch.
- (b) 6 ảnh phối cảnh do công ty công bố (New City ×2, Commerce ×4) ở `src/photos/`. Không có ảnh Green River, HH1–HH4, 150 Tô Hiệu, I.14 trên website. Ảnh trong BCTN 2025 chưa trích.
- (c) Toạ độ OSM Nominatim cho 7 điểm (trụ sở, 150 Tô Hiệu, Commerce, New City, Green River (xấp xỉ), Bắc Sông Cấm, 183 Bà Triệu HN). **17B Bà Triệu, Pruksa Town, Grand Tower và nhà máy/đại lý ô tô: không định vị được.**

---

## Bảng "điều gì đổi so REPORT v1"

| Mục v1 | v1 nói | GAPS | Hệ quả |
|---|---|---|---|
| §2/§4 KH FY26 | "chưa rõ hợp nhất hay mẹ", nguồn báo | **HỢP NHẤT** (NQ26 tr.34; BCTN25 tr.27); cổ tức FY26 dự kiến 10% chưa rõ hình thức; FY25 không trả tiền (cp thưởng 10:1) | xoá cờ; M4 giữ |
| §6a uỷ quyền 7,37% CRV | "cần kiểm", rủi ro kiểm soát | tập đoàn nắm ~81,7% vốn CRV (Q1/2025, báo) ⇒ rủi ro mất hợp nhất **thấp**; danh tính nhóm vẫn chưa rõ | hạ cờ |
| §6b HH Finance | "chưa kiểm người liên quan" | **là người liên quan** (ông Hạ là CT kiêm TGĐ); nhóm 35,99% = 71,2% phiếu ĐHĐCĐ 2026 | quản trị tập trung, đã biết |
| §6b khối ngoại | ~9,5%, chưa đo dòng | 10,51% (22/06/2026); **Dragon <5% từ 15/06/2026**; dòng 10/2026 không tìm được | bối cảnh cung |
| §6d "di cư" bên liên quan | "có thể, chưa xác minh" | giao dịch bên liên quan **đã công bố đầy đủ** (BCTN25, QT6T26, 3 NQ HĐQT 2026), đều nội bộ tập đoàn; mới: TCH cho CRV vay ≤500 tỷ, HHS ≤100 tỷ | giảm vế "di cư"; thêm rủi ro chuyển giá trị giữa các tầng NCI (nhỏ) |
| §6d pháp lý | chỉ án UBCKNN 2024 | **+ QĐ thuế 1020 ngày 03/04/2026: 20,21 tỷ** (khai sai TNDN) | WARNING: lịch sử tuân thủ 2 lần/16 tháng, mức vẫn trung bình |
| §5a "Sài Gòn Tài Lộc" | chưa xác định | = **Sacombank** (đổi tên 06/2026) | đóng |
| §7 kiểm toán | AASC FY25 | AASC tiếp tục FY26 (soát xét + kiểm toán), do TGĐ chọn; Trưởng BKS kiêm KTT công ty con | ghi nhận giám sát yếu |
| §8d SOTP qua CRV | 10.700 đ/cp | **BỎ**: CRV khớp 24/62 phiên, ~0,8 tỷ/3 tháng, P/B 2,06x, P/E 205x | thay bằng SOTP hỗn hợp **~11.200 (−5,5%)**, ước lượng |
| §1 tâm vùng | ~11.600–11.950 | nghiêng **~11.600** (vùng 9.600–14.400 giữ nguyên) | — |
| §9 mốc | M1–M6 | M6 bỏ vế "BC quản trị liệt kê bên liên quan" (đã đạt), giữ vế "không QĐ mới"; **thêm M7** | xem dưới |

**M7 (mới):** BC sử dụng vốn chào bán kỳ 03/2027 cho thấy 865,5 tỷ còn lại dùng đúng 2 mục đích đã duyệt (Green River, H2), không đổi mục đích.
- Ngày chấm: 31/03/2027. P = 0,80 (ước lượng).
- Nếu đổi mục đích sang quỹ đất mới hoặc cho công ty con vay ⇒ +5 điểm % chiết khấu quản trị (≈ −750 đ).

## Còn KHÔNG tìm được (và đã tra ở đâu)
1. Danh tính nhóm uỷ quyền 7,37% tại CRV, thời hạn, quan hệ với ông Hạ. Đã tra BCTN25, NQ26, QT6T26, báo (5 trang). Chưa đọc: bản cáo bạch niêm yết CRV 2025, BCTC HHS.
2. Doanh số ký mới / số căn đã bán HH1–HH4, NC-II, Green River; giá bán chủ đầu tư. Đã tra website, BCTN, WebSearch, rao bán. Chỉ có giá rao thứ cấp.
3. Số liệu thị trường Hải Phòng Q3/2026 (HPREA/Savills/CBRE/DKRA). Chỉ có số H1/2026.
4. Dòng khối ngoại quanh 21/10 và 29–30/10/2026; lý do KL 14 tr ngày 30/10.
5. Lý do chính thức DT ô tô giảm (359 vs 428).
6. Cảng Kim Tân là pháp nhân nào; tiền thuê đất hằng năm NC-II.
7. Quan hệ gia đình bà Nguyễn Thị Hà (4,89%) với ông Hạ.
8. Kỳ tính thuế bị truy thu trong QĐ 1020 (trang 5 chưa đọc); ý kiến kiểm toán FY23/FY24.
9. Kế hoạch 2026 và chính sách cổ tức riêng của CRV.
10. Tra trực tiếp ssc.gov.vn và CBTT HHS/CRV về xử phạt 2025–2026.

## Nguồn (truy cập 31/10/2026)
- hoanghuy.vn: `/dai-hoi-co-dong/`, `/cong-bo-thong-tin/`, `/bao-cao-thuong-nien/`, `/hoat-dong-cua-hoi-dong-quan-tri/`, `/bao-cao-tai-chinh/`, `/duanbatdongsan/` — danh mục 27 PDF ở `src/gaps/pdf/`.
- DNSE API (read-only `ohlc`, `latest_trade`) cho CRV/HHS/TCH; BQ `tav2_bq.ticker_financial` / `ticker` cho HHS.
- [Viettimes 26/03/2025 — cơ cấu cổ đông CRV](https://viettimes.vn/hoang-huy-group-quyet-dinh-chon-me-cho-bat-dong-san-crv-post183958.html) · [Mekong ASEAN — HHS 51% CRV](https://mekongasean.vn/hoa-ng-huy-hhs-so-huu-51-bat-dong-sa-n-crv-42792.html) · [Thoibaotaichinh — CRV niêm yết 672,4 tr cp](https://thoibaotaichinhvietnam.vn/hon-6724-trieu-co-phieu-crv-chinh-thuc-niem-yet-tren-hose-184816.html)
- [Sacombank đổi tên Sài Gòn Tài Lộc — The Leader](https://theleader.vn/sacombank-doi-ten-thanh-ngan-hang-sai-gon-tai-loc-d46210.html) · [Báo Đầu Tư](https://baodautu.vn/sacombank-chinh-thuc-doi-ten-thanh-ngan-hang-sai-gon-tai-loc-d611228.html)
- [SHS cập nhật TCH T5/2026](https://s3-storage.shs.com.vn/shs-website/Bao_cao_Cap_nhat_TCH_T5_2026_31fe03518e.pdf) (chưa đọc; T8/2026 đã dùng ở v1) · [batdongsan.com.vn — rao HH New City](https://batdongsan.com.vn/ban-can-ho-chung-cu-hoang-huy-new-city/p2)
- [VietnamFinance — BĐS Hải Phòng phân hoá](https://vietnamfinance.vn/bat-dong-san-hai-phong-phan-hoa-dau-gia-dat-tro-thanh-diem-sang-d147330.html) · [Nhà Đầu Tư — Hải Phòng điểm sáng](https://nhadautu.vn/hai-phong-noi-len-nhu-diem-sang-bat-dong-san-phia-bac-trong-chu-ky-phuc-hoi-moi-d102244.html)
- OpenStreetMap Nominatim (toạ độ).
