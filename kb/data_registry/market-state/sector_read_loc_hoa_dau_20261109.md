---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-09 (bước 3 skill due-diligence). KHÔNG biết mã cổ phiếu, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai về doanh nghiệp lọc hoá dầu cụ thể.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ ngành lọc hoá dầu nội địa VN (nhà máy lọc dầu khoảng 6,5-7 tr t/năm cấp xăng dầu cho thị trường nội địa; biên lọc theo crack spread; dầu thô nội địa/nhập khẩu; thuế BVMT/nhập khẩu xăng dầu; E10/E5; bảo dưỡng tổng thể; lãi/lỗ tồn kho theo giá dầu). Gồm pipeline cầu, cấu trúc cạnh tranh/rào cản, phân loại chế độ ngành + vị trí chu kỳ crack, FORECAST khoá trước có ngày chấm, checklist DD.
as_of: 2026-11-09 (giá BQ TE daily tới 2026-11-06; snapshot vĩ mô `agents/Taylor/research/dd_lagcand_20261109/macro_snapshot_20261109.md`; tin web ≤ 2026-11-03)
---

# SECTOR READ: Lọc hoá dầu nội địa VN, as-of 09/11/2026 (Bobby, real-time BLIND)

Đây không phải episode VNINDEX và không vào N_effective. Nhãn dùng trong file: **[DK]** là dữ kiện có nguồn và ngày;
**[UĐ]** là ước đoán hoặc suy luận của Bobby; **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này.
File chị em: `sector_read_oil_gas_shipping_20261029.md` (cùng bối cảnh Hormuz, có số Dung Quất/Nghi Sơn tới T10). Tôi dùng
file đó làm mẫu định dạng và để đối chiếu, không chép forecast của nó.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Repo đã đọc:** `sector_read_oil_gas_shipping_20261029.md` (mẫu + bối cảnh), `feeds/bq_commodity_prices.md` (mục BẪY),
  đầu file và các mục con trỏ của `vn_macro_regime_history.md`, `~/.claude/skills/due-diligence/SKILL.md` (bước 3), snapshot vĩ mô.
- **BQ (tự truy vấn 09/11):** `tav2_bq.commodity_prices` `source='trading_economics'`, `cadence='daily'`: `brent`, `crude_oil`,
  `urals_oil`, `te_crack_spread_index`, `gasoline` (RBOB), `heating_oil` (ULSD NYMEX), `naphtha`, `propane`, có loại T7/CN
  (bẫy b của registry feed). **BQ KHÔNG có crack Singapore/MOPS** (chuẩn định giá thực của nhà máy VN [NỀN]). Đây là khoảng trống
  dữ liệu, báo Mike/Winston, không tự sửa.
- **Ghi chú trung thực về độ mù:** mô tả ngành "nhà máy khoảng 6,5-7 tr t/năm" khớp đúng **một nhà máy** (Dung Quất, công
  suất thiết kế 6,5 tr t). Tôi đọc **số vận hành cấp nhà máy** (sản lượng, công suất, lịch bảo dưỡng, nguồn dầu thô) từ một bài
  Tạp chí Công Thương 16/10/2026 thuật lại buổi gặp nhà đầu tư của đơn vị vận hành. Khi fetch, tôi ra lệnh **bỏ hết số doanh
  thu/lợi nhuận/nộp ngân sách/giá cổ phiếu**, và không thấy số nào trong đó. Kết quả tìm kiếm có lộ: (a) tiêu đề "Operator of
  Vietnam's first oil refinery sees Q1 profit fall 31%" (không rõ năm, **không mở, không dùng**); (b) link PDF CTCK "báo cáo lần
  đầu" về đơn vị vận hành và 2 báo cáo ngành dầu khí T3 và T6/2026 (**không mở**). **Có dùng** số lợi nhuận 8T/2026 của **Nghi
  Sơn** (không niêm yết, là đối thủ) làm bằng chứng cấp ngành về biên lọc 2026. Rủi ro neo vẫn có, ghi ra đây.
- **Không đọc:** `kb/projects/*`, `agents/Taylor/*` (ngoài file snapshot được giao). Không tra giá cổ phiếu, BCTC hay khuyến
  nghị CTCK nào.
- **Chi phí vốn VN:** lượt này **không lấp bảng 5 tầng lãi suất**, nên **không kết luận** gì về chi phí vốn VND. Chỉ ghi số
  snapshot (tái cấp vốn 4,50%; LNH 3M 6,84%, +0,42pp/12T) để hiển thị. Điều này đáng lưu ý vì dự án mở rộng cần thu xếp vốn
  trong năm 2027 (mục 2).

## 1. Pipeline cầu [DK trừ khi ghi khác]

### 1.1 Cung nội địa: 2 nhà máy, cả hai ở trần kỹ thuật
| Hạng mục | Số liệu as-of | Đọc |
|---|---|---|
| **Dung Quất** (TK 6,5 tr t dầu thô/năm, khoảng 148k thùng/ngày) | 9T/2026 sản xuất **khoảng 6,15 tr t**, tiêu thụ khoảng 6,08 tr t (TCCT 16/10). Tết và Q1 chạy **khoảng 125%**; 7T bình quân khoảng 124%. Mục tiêu cả năm **8,3 tr t** (Tuổi Trẻ 30/03) | 6,15 tr t / 9 tháng tương đương **khoảng 126% công suất** quy đổi [UĐ]. Để đạt 8,3 tr t, Q4 cần khoảng 2,15 tr t, tức 0,72 tr t/tháng, **cao hơn** tốc độ 9T (0,68). Đạt 8,0 tr t chỉ cần giữ tốc độ 9T |
| **Dầu thô cho Dung Quất** | Mục tiêu tỷ trọng dầu **nội địa khoảng 88%** (kế hoạch cũ khoảng 70/30), đa dạng hoá sang Tây Phi, Địa Trung Hải, Mỹ, Nam Mỹ; nguyên liệu cơ bản đủ đến hết 2026 (TCCT 16/10) | Gần như không phụ thuộc Hormuz. Chi phí cước thấp hơn hẳn nhà máy châu Á nhập dầu Trung Đông [UĐ] |
| **Nghi Sơn** (TK 10 tr t, 200k thùng/ngày) | 9T/2026 chế biến **8,38 tr t dầu thô**, cấp 6,54 tr t sản phẩm; hiện **125%**; Kuwait nối lại từ T9 sau 5 tháng đứt; đủ dầu tới hết T11, T12 đang chốt; Q4 dự kiến cấp thêm 2,69 tr t; cấp **khoảng 35-40%** nhu cầu nội địa (VietNamNet 03/10) | Nhà máy lớn nhất đã hồi phục và đang chạy trần |
| **Bảo dưỡng tổng thể 2027** | Dung Quất **TA6 dự kiến năm 2027**, chưa công bố tháng; có kết hợp chuẩn bị đấu nối dự án mở rộng (TCCT 16/10). Đã duyệt nhà thầu gói 2 TA6 (Báo Đấu thầu). Nghi Sơn TA lần 2: **48 ngày từ 10/08/2027** (Vietnam News) | **Cả 2 nhà máy cùng dừng trong năm 2027.** Đây là biến số khối lượng lớn nhất của 2027. TA5 của Dung Quất kéo dài **48 ngày (15/03-01/05/2024)** |
| **Dung Quất mở rộng** (148k lên 171k thùng/ngày, khoảng +16%) | EPC ký 09/07/2026; san lấp khoảng **90%** đầu T10; mục tiêu giao toàn bộ mặt bằng trong 2026; thu xếp vốn vay (NH + tổ chức tín dụng xuất khẩu) và giải ngân trong **2027**; mục tiêu "hoàn thành 2028" (TCCT 16/10) | File vận tải 29/10 đã ghi EPC 37 tháng (khoảng T8/2029). Tôi vẫn tin **2029** hơn 2028 [UĐ]. Trước đó không có công suất mới |
| **Long Sơn** (hoá dầu, không lọc dầu) | Dừng từ giữa T5/2026 vì chi phí nguyên liệu; TA 5 tháng từ 01/11/2026; mục tiêu tái vận hành **Q2/2027** (Technode 13/10, theo SCG) | Không cạnh tranh nhiên liệu. Có ý nghĩa cho mảng polypropylene nội địa (bớt cung PP trong nước tới Q2/2027) [UĐ] |

### 1.2 Cầu nội địa
| Hạng mục | Số liệu as-of | Đọc |
|---|---|---|
| **Tổng nguồn xăng dầu tối thiểu 2026** | **31,8 tr m³/tấn** (BCT) | Hai nhà máy cấp khoảng 17-18 tr t sản phẩm năm 2026 (Dung Quất khoảng 8,2 + Nghi Sơn hơn 9,2) [UĐ: so khác đơn vị m³/t, chỉ là bậc độ lớn khoảng 55-60%]. Phần còn lại nhập khẩu |
| **Nhập khẩu sản phẩm** | Q1/2026: **3,37 tr t, +44,5%** về lượng. 4T: diesel 2,19 tr t (+45,7%), xăng 1,04 tr t (+27,5%), nhiên liệu bay 719k t (+3%) (TBTC). **Chưa có số 10T** | Nhập khẩu bù hụt khi Nghi Sơn đứt dầu Kuwait. Nhập khẩu là **người định giá biên** của thị trường nội địa [NỀN] |
| **Hoạt động (snapshot 09/11)** | GDP Q3 **+9,95% YoY**; SXCN T10 **+15,0%**; bán lẻ T10 **+14,7%**; PMI 52,3 (−2,2 điểm/12T); khách quốc tế T10 +7,0% YoY | Cầu diesel (công nghiệp, vận tải, xây dựng) và nhiên liệu bay **mạnh**. Cầu không phải ràng buộc của ngành. Ràng buộc là **công suất** |
| **E10 / nhiên liệu sinh học** | TT 50/2025/TT-BCT: từ **01/06/2026** xăng không chì phải pha thành E10 toàn quốc; **E5 RON92 vẫn lưu hành tới hết 2030**; diesel sinh học **chưa bắt buộc** (B5/B10 chỉ khuyến khích). Dung Quất đã bán khoảng 400k m³ E10 RON95 luỹ kế tới T9; nhà máy ethanol Dung Quất chạy lại từ T1/2026; B5 từ T8/2026 (TCCT 16/10) | E10 thay khoảng 5pp xăng khoáng so với E5 [UĐ], tác động khối lượng nhỏ. Nhà máy có ethanol nội bộ thì giữ được một phần giá trị pha trộn |
| **Xói mòn cầu xăng dài hạn** | [NỀN, chưa kiểm lại trong lượt này] xe máy/ô tô điện, lộ trình hạn chế xe máy xăng ở trung tâm Hà Nội | Không phải lực chi phối tới 2027. Là rủi ro cấu trúc cho định giá dài hạn |

**Đọc tổng hợp [UĐ]:** cầu nội địa 2026-27 **dư** so với cung nội địa. Hai nhà máy chạy khoảng 125% và vẫn phải nhập khoảng
40-45% nhu cầu. Vì vậy lợi nhuận ngành **không** do khối lượng quyết định mà do **biên (crack) × khối lượng tối đa**. Khối lượng
2027 sẽ **thấp hơn** 2026 vì cả hai nhà máy đều có TA, khoảng 7 tuần mỗi nhà máy nếu theo lịch TA5 và Nghi Sơn.

## 2. Cấu trúc cạnh tranh và rào cản
- **Số người chơi trong lọc dầu:** **2 nhà máy** (Dung Quất, sở hữu nhà nước chi phối qua tập đoàn dầu khí quốc gia [NỀN];
  Nghi Sơn, liên doanh Idemitsu/Kuwait Petroleum/PVN/Mitsui [NỀN]). Đối thủ thật sự là **hàng nhập khẩu** từ Hàn Quốc,
  Singapore, Malaysia, Thái Lan, Trung Quốc qua khoảng 30 thương nhân đầu mối [NỀN]. Cấu trúc: **duopoly nội địa, chịu giá
  nhập khẩu** (import-parity).
- **Rào cản gia nhập: rất cao.** Vốn hàng tỷ USD; phê duyệt cấp Chính phủ/Quốc hội; cần nguồn dầu thô, cảng nước sâu, phao rót
  không bến. Không có nhà máy mới nào trước khi Dung Quất mở rộng xong (khoảng 2029 [UĐ]). Trung tâm lọc hoá dầu Quảng Ngãi mới
  ở mức kêu gọi (TCCT 16/10).
- **Cơ chế giá bán (cốt lõi):** [NỀN, cần DD kiểm] nhà máy bán buôn cho đầu mối theo giá ngang hàng nhập khẩu, tức MOPS
  Singapore + premium + cước + **thuế nhập khẩu tương đương**. Khoảng chênh thuế nhập khẩu (MFN xăng 10%, diesel/FO/Jet 7%) so
  với thuế FTA thực áp dụng cho hàng nhập cạnh tranh là **phần "bảo hộ" hành chính** của nhà máy nội địa.
  · **Hiện tại phần bảo hộ đó đang bị gỡ:** NĐ 72/2026/NĐ-CP (09/03/2026) đưa thuế NK MFN về **0%** cho xăng (từ 10%) và
  diesel/FO/Jet/kerosene (từ 7%), cùng xylen/condensate/p-xylen (từ 3%). NQ 25/2026/NQ-CP và **NQ 43/2026/NQ-CP** kéo dài tới
  **hết 31/12/2026**, cho phép rút ngắn hoặc kéo dài (Báo Pháp luật/MOIT, 10/2026).
  · Mức ảnh hưởng thực **phụ thuộc** tỷ trọng hàng nhập từ nước có FTA 0% (ASEAN, Hàn Quốc) [NỀN]. Nếu phần lớn hàng nhập vốn đã 0%
  qua FTA thì việc gỡ MFN tác động nhỏ. **Đây là câu DD phải kiểm bằng số**, không suy được ở cấp ngành.
- **Thuế gián thu (chuyển qua giá, không phải biên lọc):** thuế BVMT xăng/diesel/nhiên liệu bay **0 đ/lít** từ 26/03/2026 (QĐ
  482/QĐ-TTg), NQ 19/2026/QH16 từ 16/04, NQ 43 kéo tới **31/12/2026**. Mức nền 2026 nếu hết giảm: xăng 2.000 đ/l, diesel 1.000 đ/l
  (UBTVQH). Một nguồn ghi **thuế TTĐB xăng về 0% từ 01/11/2026 đến 31/03/2027** nhưng hải quan nói NQ 43 **không** đổi TTĐB. **Mâu
  thuẫn chưa giải được**, cần đọc văn bản gốc. TTĐB xăng do nhà sản xuất/nhập khẩu kê khai [NỀN], nên nó chạm dòng tiền và vốn lưu
  động của nhà máy, dù về nguyên tắc vẫn chuyển qua giá.
- **Điều hành giá bán lẻ:** NĐ 80/2023 vẫn là khung hiện hành. Dự thảo nghị định mới (thay NĐ 83/95/80) cho **doanh nghiệp tự
  quyết giá bán lẻ theo thị trường** và chuyển Quỹ BOG về **một tài khoản tại Kho bạc**. Đã trình Chính phủ; PTT họp 24/06/2026;
  **chưa ban hành** tại as-of. Quy định này chủ yếu chạm khâu phân phối. Với nhà máy, rủi ro là **Nhà nước can thiệp giá bán buôn
  khi lạm phát tăng** [UĐ].
- **Sức mạnh của Nhà nước (lực thứ 6): cao.** Cả hai nhà máy được yêu cầu chạy tối đa để bảo đảm nguồn cung. Chính sách thuế
  đổi 4 lần trong năm 2026. CPI YoY **5,09%** (T10, +1,84pp/12T, snapshot) làm áp lực chính trị giữ giá xăng dầu tăng lên.
- **Khách hàng:** đầu mối bán lẻ (một đầu mối nhà nước chiếm khoảng một nửa thị trường bán lẻ [NỀN]). Sức mặc cả **trung bình**:
  khi thiếu hàng (2026) nhà máy có lợi thế; khi Hormuz mở và hàng nhập Singapore rẻ lại, đầu mối có lựa chọn.
- **Lợi thế tương đối giữa 2 nhà máy [UĐ]:** nhà máy chạy **dầu ngọt nội địa** (khoảng 88%) tránh được cước VLCC kỷ lục và rủi ro
  Hormuz. IEA (10/2026) nói biên lọc châu Á **bị ép** bởi giá dầu thô giao tới và cước. Nhà máy chạy dầu chua Kuwait (Nghi Sơn)
  chịu đủ cả hai. Chiều ngược lại: dầu nội địa định giá theo Dated Brent + premium [NỀN], nên không rẻ hơn về giá FOB. Cấu hình
  RFCC hướng xăng/LPG/PP của Dung Quất [NỀN] cho tỷ trọng diesel thấp hơn một nhà máy hydrocracker, tức hưởng **ít hơn** đợt
  crack diesel kỷ lục.

## 3. Phân loại chế độ ngành + vị trí chu kỳ

### 3.1 Biên lọc hiện tại (đa proxy) [DK BQ TE daily, tính lại 09/11; crack = sản phẩm quy USD/thùng − Brent cùng kỳ]
⚠ Đây là **proxy Đại Tây Dương** (NYMEX RBOB/ULSD), không phải MOPS Singapore. Hướng thường cùng chiều, **mức** có thể lệch lớn
(IEA: châu Á bị ép hơn Đại Tây Dương). Naphtha TE quy đổi bằng 8,9 thùng/tấn [UĐ].
| Tháng (BQ) | Brent | Chỉ số crack TE (≈ 3-2-1 Mỹ [UĐ]) | ULSD − Brent | RBOB − Brent | Naphtha − Brent |
|---|---|---|---|---|---|
| 2025-06 | 69,5 | 24,7 | 26,7 | 20,8 | −7,2 |
| 2025-10 | 63,8 | 24,4 | 32,0 | 14,8 | −4,3 |
| 2026-01 | 64,6 | 22,6 | 32,0 | 11,0 | −5,9 |
| 2026-03 | 98,1 | 45,4 | 64,4 | 25,0 | −8,5 |
| 2026-05 | 103,8 | 54,2 | 59,6 | 42,8 | −8,9 |
| 2026-07 | 83,6 | 64,4 | 77,7 | **50,4 (đỉnh)** | −2,6 |
| 2026-09 | 100,8 | **66,0 (đỉnh)** | **101,2 (đỉnh)** | 39,0 | −8,4 |
| 2026-10 | 107,3 | 61,0 | 93,0 | 28,3 | −7,5 |
| 2026-11 (1-6/11) | 101,0 | **48,1** | 83,8 | **18,7** | −8,4 |
| Ngày 06/11 | 98,32 | 47,9 | 83,5 | 18,4 | −6,4 |

Kiểm chứng chỉ số TE: (2×RBOB + ULSD)/3 − WTI ngày 06/11 xấp xỉ 45-46, trong khi chỉ số là 47,9. Tôi coi nó **xấp xỉ** crack 3-2-1
Mỹ [UĐ]. Urals T10 **113,3 > Brent 107,3**, 05/11 về 76,9: dầu chua ngoài Hormuz từng được trả giá cao rồi sụp nhanh.

**Bằng chứng ngoài BQ:**
- IEA OMR 14/10/2026: biên lọc Q3/2026 "exceptionally strong", nhờ crack diesel/jet **kỷ lục ở Đại Tây Dương**, bù cho crack
  FO/naphtha âm sâu. Biên châu Á và châu Âu **bị ép** vì giá dầu thô giao tới và cước. Crack diesel châu Âu từ khoảng 100 xuống
  khoảng 60 USD/thùng vào đầu T10. Gasoil toàn cầu **căng nửa đầu 2027, nới nửa sau 2027**. Cung dầu 2026 −5,8 tr thùng/ngày,
  2027 **+7,7 tr thùng/ngày** (giả định phục hồi). Tổn thất diesel Trung Đông + Nga T9 là 1,3 tr thùng/ngày (khoảng 4,5% cầu).
- Kpler 26/10: chênh giá giao ngay gasoil Singapore từ +3,75 xuống **+1,25 USD/thùng** từ đầu T10. Tồn kho trung cất Singapore
  +10% trong T10 (9,35 tr thùng). XK gasoil vùng Vịnh **khoảng 72k thùng/ngày** trong T10 (T9: 205k). Trung Quốc XK chậm, Hàn Quốc
  trần XK ở mức 2025. Kết luận của Kpler: "prompt fundamentals soft", nhưng có thể căng lại cuối năm.
- QCIntel 23/10: crack xăng Singapore bật lên từ **đáy 2 tháng**; gasoil châu Á hồi khi tồn kho Singapore giảm (bản tin không có số).
- **Nghi Sơn** báo lợi nhuận sau thuế **khoảng 530 tr USD trong 8T/2026**, **năm đầu tiên có lãi** kể từ khi vận hành cuối 2018
  (VietNamNet 03/10). Đây là bằng chứng cấp ngành mạnh nhất rằng **2026 là năm biên lọc ngoại lệ** tại VN.

### 3.2 Lãi/lỗ tồn kho: biến số thứ hai, đổi chiều mỗi quý năm 2026 [DK BQ, Brent ngày cuối quý]
| Mốc | Brent | Đổi so với quý trước | Hàm ý cho nhà máy giữ khoảng 3-5 tuần tồn kho [UĐ] |
|---|---|---|---|
| 31/12/2025 | 60,85 | — | — |
| 31/03/2026 | 103,97 | **+71%** | Lãi tồn kho rất lớn Q1 |
| 30/06/2026 | 72,95 | **−30%** | Lỗ tồn kho / dự phòng giảm giá Q2 |
| 30/09/2026 | 98,03 | **+34%** | Lãi tồn kho Q3 |
| 06/11/2026 | 98,32 | ~0% (đỉnh trong T10 116,7 ngày 28/10) | Q4 phụ thuộc Brent cuối T12. Hàng mua giá 105-116 cuối T10 bán ra ở khoảng 98 đầu T11 ⇒ **có áp lực lỗ tồn kho trong Q4** |

**Hệ quả [UĐ]:** lợi nhuận từng quý 2026 của một nhà máy VN là **crack + tồn kho**, và vế tồn kho có thể lớn ngang vế crack. Không
được ngoại suy quý nào thành "năng lực lợi nhuận".

### 3.3 Nguyên nhân gốc (trục 1) và có khoanh được không (trục 2)
- **Trục 1:** crack cao là **cú sốc cung ngoại sinh** (Hormuz bị đóng thực tế từ đầu T3/2026; XK sản phẩm vùng Vịnh sụp; tổn thất
  diesel Nga; Trung Quốc siết XK; cước tàu kỷ lục). Nó **không** phải dư cầu do mất cân đối vĩ mô VN. Cầu nội địa VN mạnh (GDP
  khoảng 10%) nhưng chỉ quyết định việc nhà máy chạy trần, không quyết định crack.
- **Trục 2: KHÔNG khoanh được bởi VN** ⇒ `EXTERNAL_CYCLE`. Đàm phán Mỹ–Iran qua Qatar: Iran nói có thể mở eo **trong 2 ngày**
  nếu Mỹ chấp nhận gói điều kiện (02/11); vòng Doha kết thúc **không đột phá** (03/11); Mỹ đe doạ tấn công sau bầu cử giữa kỳ.
  Brent rơi khoảng 8% ngày 02/11 vì kỳ vọng hoà bình (Gulf News). Goldman: Brent có thể lên 140 năm 2027 nếu sản lượng vùng Vịnh
  vẫn thấp hơn 2025 khoảng 3,5 tr thùng/ngày (theo OilPrice, **chưa kiểm**).
- **Phần VN kiểm soát được là hành chính:** thuế NK/BVMT/TTĐB, giá bán lẻ, lệnh chạy tối đa, lịch TA, E10. Phần này **khuếch
  đại hoặc giảm bớt** chu kỳ, không tạo ra chu kỳ.

### 3.4 Ba kịch bản tới giữa 2027 (đồng bộ với file vận tải 29/10, cập nhật sau tin 02-03/11) [UĐ]
- **K1, Hormuz còn tranh chấp/hạn chế tới hết Q1/2027 (p ≈ 0,50):** Brent 85-110; crack diesel giữ cao (IEA: căng nửa đầu 2027);
  crack xăng bình thường. Biên lọc VN cao hơn 2025 nhưng thấp hơn Q3/2026.
- **K2, thoả thuận thật trước giữa T1/2027 (p ≈ 0,35, tăng từ 0,30 ngày 29/10 vì tin 02/11):** Brent giảm nhanh về 70-85; crack về
  gần mức 2025 trong 2-3 quý (độ trễ do tồn kho sản phẩm toàn cầu thấp). Kèm **lỗ tồn kho** trong quý giá giảm.
- **K3, leo thang đánh vào hạ tầng vùng Vịnh (p ≈ 0,15):** Brent > 115; crack trồi lại, nhưng rủi ro nguồn dầu thô (phần nhập) và
  Nhà nước can thiệp giá bán tăng.

### 3.5 KẾT LUẬN PHÂN LOẠI
**Nhãn chi phối lợi nhuận biên của ngành tới hết 2027 (các nhãn không loại trừ nhau, xác suất là nhãn nào CHI PHỐI):**
| Nhãn | P | Lý lẽ |
|---|---|---|
| **CYCLICAL** (đỉnh crack cấp tính do cú sốc cung ngoại sinh; đã qua đỉnh: crack xăng đỉnh T7, diesel đỉnh T9, chỉ số TE từ 66 xuống 48) | **0,55** | Biên 2026 gấp khoảng 2-3 lần 2025 nhờ mất cung chứ không nhờ cầu. Nghi Sơn có lãi lần đầu sau 8 năm. IEA thấy gasoil nới nửa sau 2027 và cung dầu +7,7 tr thùng/ngày năm 2027. Cộng thêm TA của cả 2 nhà máy năm 2027 làm khối lượng giảm |
| **ADMIN_GATED** (thuế NK/BVMT/TTĐB, giá bán lẻ, lệnh chạy tối đa, lộ trình E10, dự thảo nghị định xăng dầu) | **0,30** | Phần bảo hộ thuế NK MFN đang ở 0% tới 31/12/2026; quyết định 2027 nằm trong tay Chính phủ. CPI 5,09% đang tăng làm tăng xác suất can thiệp. Khung 2027 sẽ quyết định nhà máy giữ được bao nhiêu phần biên quốc tế |
| **STRUCTURAL** (nền biên dài hạn cao hơn trước chiến tranh: "Hormuz new normal", Trung Quốc giữ trần XK và cầu đỉnh khoảng 2027, VN thiếu công suất tới khoảng 2029 nên luôn chạy trần) | **0,15** | Có lý lẽ, nhưng bị phản biện bởi phục hồi cung 2027 và việc thiếu hụt của VN chỉ đảm bảo **khối lượng**, không đảm bảo **biên** (biên do Singapore định) |

**Vị trí chu kỳ crack: "cuối đỉnh, đầu pha giảm" (late-peak → early-decline).** Crack xăng đã gần về bình thường (18,7 so với
11-21 năm 2025), crack diesel vẫn gấp khoảng 2,6 lần năm 2025 (83,8 so với khoảng 32). Độ tin cậy **ambiguous khoảng 60/40**: diesel
có thể căng lại cuối năm (Kpler, IEA H1/2027), và K3 vẫn mở.

**Hệ quả với DN VN [UĐ, không phải khuyến nghị]:** năm 2026 là **năm nền bất thường** trên cả 3 vế (crack, tồn kho, công suất
125%). Năm 2027 có 3 lực kéo xuống cùng lúc: crack về dần, TA khoảng 7 tuần, và có thể lỗ tồn kho nếu K2. Lực đỡ: dầu nội địa
(không chịu cước/Hormuz), cầu nội địa mạnh, và phần bảo hộ thuế NK nếu được khôi phục từ 01/01/2027.

## 4. FORECAST KHOÁ TRƯỚC (lập 2026-11-09; chấm theo quan sát cuối cùng ≤ ngày kiểm)
**Proxy chấm chính (tự động từ BQ):** `tav2_bq.commodity_prices`, `source='trading_economics'`, `cadence='daily'`, loại T7/CN.
Mốc gốc: Brent **98,03** (30/09/2026) và **98,32** (06/11); chỉ số crack TE **47,9** (06/11), BQ T11 (1-6/11) **48,1**, BQ Q3/2026
**64,7**; ULSD − Brent BQ tháng = `heating_oil×42 − brent`; RBOB − Brent = `gasoline×42 − brent`. Proxy Singapore: **không có**
trong BQ. Nếu sau này có chuỗi MOPS/Platts thì chấm thêm, không thay thế.

| ID | Mốc | Chuỗi (gốc) | Dự báo |
|---|---|---|---|
| F1 | **2026-12-31** | Brent đóng cửa phiên cuối 2026 (gốc 98,03 = cuối Q3) | **P(< 98,03) = 0,55**. Trung vị khoảng 96, 80% trong 74-115. Hàm ý: P(lỗ tồn kho Q4 so với cuối Q3) ≈ 0,55 |
| F2 | **2027-03-31** | Chỉ số crack TE, BQ tháng 3/2027 (gốc BQ 1-6/11: 48,1) | **P(< 48,1) = 0,55**; P(< 35) = 0,25; P(> 60) = 0,20 |
| F3 | **2027-06-30** | Chỉ số crack TE, BQ Q2/2027 (gốc BQ Q3/2026: 64,7) | **P(< 64,7) = 0,80**; P(< 40) = 0,40 |
| F4 | **2027-09-30** | ULSD − Brent, BQ tháng 9/2027 (gốc T9/2026: 101,2; T11/2026: 83,8) | **P(< 50) = 0,65**; P(< 83,8) = 0,85; trung vị khoảng 42 |
| F5 | **2027-09-30** | RBOB − Brent, BQ tháng 9/2027 (gốc T11/2026: 18,7) | **P(trong 8-28) = 0,65**, tức crack xăng ở vùng bình thường |
| F6 | **2027-06-30** | Brent BQ Q2/2027 (gốc BQ Q4/2026 tới 06/11: khoảng 101) | **P(< 90) = 0,55** |
| D1 | công bố khoảng T1/2027, chấm trước **2027-03-31** | Sản lượng sản xuất cả năm 2026 của Dung Quất (9T: 6,15 tr t) | **P(≥ 8,0 tr t) = 0,85; P(≥ 8,3 tr t, đạt kế hoạch) = 0,45** |
| D2 | **2027-12-31** | Dung Quất TA6 **bắt đầu** trong năm 2027 (tin chính thức) | **P = 0,80** (rủi ro chính: chu kỳ TA kéo dài 4 năm, hoặc lùi để ghép đấu nối mở rộng) |
| D3 | **2027-12-31** | Thời gian dừng TA6 Dung Quất (nếu diễn ra) | **P(≥ 40 ngày) = 0,65** (TA5: 48 ngày) |
| D4 | **2027-12-31** | Cửa sổ TA6 Dung Quất **trùng** cửa sổ TA Nghi Sơn (10/08-27/09/2027) ít nhất 1 ngày | **P = 0,12** (BCT sẽ điều phối tránh trùng để giữ nguồn cung [UĐ]) |
| D5 | **2027-09-30** | TA Nghi Sơn bắt đầu trong khoảng 10/07-10/09/2027 (lịch 10/08) | **P = 0,70** |
| D6 | **2027-01-15** | Thuế NK MFN xăng động cơ đang áp dụng (văn bản có hiệu lực tại ngày chấm) | **P(vẫn 0%) = 0,50**. Phụ: P(trở lại đúng 10%) = 0,35; mức trung gian khác = 0,15 |
| D7 | **2027-01-15** | Thuế BVMT xăng (trừ etanol) đang áp dụng | **P(vẫn 0 đ/l) = 0,40**; P(2.000 đ/l hoặc mức giảm từng phần khác 0) = 0,60 |
| D8 | **2027-06-30** | Nghị định kinh doanh xăng dầu mới (thay NĐ 80/2023) được **ban hành** | **P = 0,45** |
| D9 | **2027-06-30** | Long Sơn có tin tái vận hành thương mại | **P = 0,50** |
| D10 | **2027-12-31** | Dung Quất mở rộng: ký hợp đồng vay/thu xếp vốn chính (tin chính thức) | **P = 0,60** |
| D11 | **2028-12-31** | Dung Quất mở rộng vận hành thương mại | **P = 0,20** (EPC 37 tháng từ 07/2026 cho mốc khoảng T8/2029) |

**Câu phân loại:** CYCLICAL đúng nếu **chỉ số crack TE BQ Q3/2027 ≤ 35** (gần dải 2025 là 22-29) **hoặc** ULSD − Brent BQ Q3/2027
≤ 45: **P = 0,55**. STRUCTURAL đúng nếu chỉ số crack TE **≥ 45 bền suốt Q3/2027** sau khi Hormuz đã mở lại ≥ 2 quý: **P = 0,15**.
ADMIN_GATED được coi là chi phối nếu trong năm 2027 có **≥ 2 thay đổi** thuế NK/BVMT/TTĐB xăng dầu hoặc cơ chế giá bán buôn có hiệu
lực: **P = 0,55** (năm 2026 đã có 4 lần).

## 5. Chỉ báo dẫn dắt (theo dõi)
| # | Chỉ báo (tần suất) | Nguồn | Tín hiệu bình thường hoá ⇔ kéo dài/leo thang |
|---|---|---|---|
| 1 | Trạng thái Hormuz + đàm phán Mỹ–Iran (tuần) | Reuters/Al Jazeera, JMIC, LLI | Có thoả thuận + lượt tàu qua bền 4 tuần ⇔ tấn công tiếp diễn |
| 2 | Crack Singapore: gasoil 10ppm, xăng 92, naphtha so với Dubai; biên phức hợp Singapore (tuần/tháng) | Platts/Argus/QCIntel, OPEC MOMR (Refining margins), IEA OMR | Gasoil < 20 USD/thùng ⇔ > 35 |
| 3 | Proxy BQ: chỉ số crack TE, ULSD/RBOB/naphtha − Brent (ngày) | BQ `commodity_prices` | TE < 35 ⇔ > 55 |
| 4 | Brent so với mốc cuối quý (ngày); Urals − Brent | BQ | Brent giảm > 10% trong quý = lỗ tồn kho |
| 5 | XK sản phẩm vùng Vịnh; trần XK Trung Quốc 2027 (đợt 1 thường cuối T12); trần XK Hàn Quốc | Kpler, Reuters/OPIS | Đợt 1 năm 2027 ≥ 19 tr t ⇔ thấp hơn 2026 |
| 6 | Văn bản thuế xăng dầu 2027 (NK MFN, BVMT, TTĐB) + nghị định kinh doanh xăng dầu | Cổng Chính phủ, MOF, MOIT | Khôi phục thuế NK 10/7% (lợi cho nhà máy nội địa) ⇔ giữ 0% |
| 7 | Lịch TA6 Dung Quất + TA Nghi Sơn; mọi sự cố dừng ngoài kế hoạch | BCT, PVN, báo ngành | Công bố tháng TA6, không trùng Nghi Sơn ⇔ trùng hoặc lùi |
| 8 | NK xăng dầu theo tháng về lượng (Hải quan) | Cục Hải quan | NK giảm khi 2 nhà máy chạy trần ⇔ NK tăng vọt (TA/sự cố) |
| phụ | CPI YoY (áp lực chính trị lên giá xăng) | GSO / snapshot | CPI > 5,5% = tăng rủi ro can thiệp ⇔ < 4% |

## 6. DD cần kiểm gì (một DN lọc hoá dầu VN)
**A. Phân rã biên lọc (quan trọng nhất)**
1. **Biên lọc gộp (GRM, USD/thùng) theo từng quý 2024-2026**, tách 3 vế: (i) crack/biên lọc thuần, (ii) **lãi/lỗ tồn kho** và
   hoàn nhập/trích dự phòng giảm giá hàng tồn kho, (iii) chênh lệch tỷ giá. So vế (i) với biên phức hợp Singapore cùng quý.
2. **Cơ cấu sản phẩm (yield)**: xăng, diesel, Jet A1, LPG, polypropylene, FO, naphtha (%). Tính độ nhạy lợi nhuận với 1 USD/thùng
   crack **từng sản phẩm**. Đợt kỷ lục 2026 là diesel/jet. Nhà máy hướng xăng/PP hưởng ít hơn.
3. **Công thức giá bán buôn**: MOPS + premium bao nhiêu; có cộng thuế NK tương đương không; điều khoản hợp đồng với đầu mối (kỳ hạn,
   chiết khấu, ai chịu cước). **Đo bằng số** phần bảo hộ thuế NK mất đi trong giai đoạn MFN 0% (09/03-31/12/2026): so với hàng nhập
   từ ASEAN/Hàn Quốc (FTA 0%) và Trung Quốc.
4. **Lợi nhuận 2026 chuẩn hoá**: tính lại ở crack trung bình 2023-25 và tồn kho trung tính. Đó mới là nền định giá, không phải 2026.

**B. Nguyên liệu dầu thô**
5. Tỷ trọng dầu nội địa/nhập khẩu theo quý; **công thức giá** (Dated Brent ± premium từng loại dầu); hợp đồng khung với đơn vị
   cùng tập đoàn; điều khoản bao tiêu/thanh toán.
6. Chi phí cước + bảo hiểm (có phí war-risk không) cho phần nhập; danh mục dầu đã chế biến được; rủi ro mỏ nội địa suy giảm sau 2027.
7. **Số ngày tồn kho** dầu thô + sản phẩm; phương pháp tính giá xuất kho (bình quân/FIFO); chính sách dự phòng giá trị thuần có thể
   thực hiện. Dùng để ước lãi/lỗ tồn kho Q4/2026 (mục 3.2).

**C. Vận hành và bảo dưỡng**
8. Công suất thực theo tháng; số lần dừng ngoài kế hoạch; **độ bền thiết bị khi chạy khoảng 125% kéo dài** (có hạng mục nào bị dồn
   bảo dưỡng không).
9. **TA6**: tháng bắt đầu, số ngày dừng, chi phí, hạch toán (vốn hoá rồi phân bổ hay chi phí ngay), phần đấu nối dự án mở rộng
   ghép vào; kế hoạch nhập bù trong thời gian dừng; có trùng TA Nghi Sơn không.
10. Kế hoạch kéo dài chu kỳ TA lên 4 năm: căn cứ kỹ thuật, ảnh hưởng tới rủi ro dừng đột xuất.

**D. Dự án mở rộng và capex**
11. Tổng vốn đầu tư (gói EPC khoảng 1,0-1,2 tỷ USD theo 2 nguồn lệch nhau, cộng phần ngoài EPC); cơ cấu vốn vay/vốn chủ; đồng tiền
    vay; lãi suất (cố định hay thả nổi); lịch giải ngân 2027-29; covenant.
12. **Giả định crack trong IRR dự án**; độ nhạy khi crack về mức 2025; rủi ro trễ tiến độ (2028 hay 2029); chi phí đấu nối.
13. Cổ tức và việc dùng tiền mặt năm đỉnh 2026: trả nợ, giữ cho capex, hay chia.

**E. Thuế và chính sách**
14. TTĐB xăng: ai kê khai, mức áp dụng thực từ 01/11/2026 (giải mâu thuẫn ở mục 2), ảnh hưởng vốn lưu động.
15. Thuế NK/BVMT 2027: kịch bản khôi phục và tác động lên giá bán buôn. Ưu đãi thuế TNDN còn hay hết [NỀN, phải kiểm].
16. Nghĩa vụ "bảo đảm nguồn cung" (lệnh chạy tối đa, bán khi lỗ, giữ tồn kho dự trữ quốc gia): có làm DN hy sinh biên không.
17. E10/B5: chi phí ethanol, công suất nhà máy ethanol nội bộ, biên phối trộn; tiêu chuẩn chất lượng nhiên liệu mới (Euro 5 [NỀN]) và capex
    đi kèm.

**F. Tài chính, tỷ giá, quản trị**
18. Nợ USD và lãi/lỗ tỷ giá (VND **tăng khoảng 2,8%/12T** theo snapshot: lãi đánh giá lại nợ USD, nhưng doanh thu quy VND giảm).
19. Phải thu đầu mối (tập trung khách hàng top-3, tuổi nợ); giao dịch bên liên quan trong tập đoàn.
20. Sở hữu Nhà nước, kế hoạch thoái vốn/free float, cơ chế phê duyệt đầu tư (chậm hơn DN tư nhân).
21. Mảng hoá dầu (PP): biên PP so với naphtha/propylene; cạnh tranh khi Long Sơn chạy lại Q2/2027.

## 7. Điều gì làm tôi sai
1. **K3 leo thang** đánh vào hạ tầng lọc/XK vùng Vịnh: crack diesel lên lại > 100 và kéo dài qua 2027 (F2-F4 sai).
2. **Tồn kho sản phẩm toàn cầu quá thấp**: kể cả khi Hormuz mở, crack diesel giữ cao 3-4 quý vì bổ sung tồn kho (IEA đã nói căng
   nửa đầu 2027). Khi đó F4 có thể sai.
3. **Mất công suất cấu trúc** (nhà máy vùng Vịnh/Nga hư hại lâu dài, Trung Quốc giữ trần XK thấp, đóng cửa nhà máy châu Âu/Mỹ):
   nền biên 2027-28 cao hơn nhiều năm 2023-25. Khi đó STRUCTURAL đúng hơn mức 0,15 tôi cho.
4. **Nhà nước thu phần lợi nhuận bất thường** (khôi phục thuế nhanh, can thiệp giá bán buôn, yêu cầu đóng góp bình ổn): biên của
   DN thấp hơn biên quốc tế ở cả kịch bản K1. Khi đó ADMIN_GATED chi phối hơn mức 0,30.
5. **Proxy sai mức:** tôi không có crack Singapore. IEA nói châu Á bị ép hơn Đại Tây Dương, nên mọi suy luận từ RBOB/ULSD **có thể
   phóng đại** biên thực của nhà máy VN. Nhà máy chạy dầu nội địa có thể lại tốt hơn bình quân châu Á. Dấu của sai số này tôi không biết.
6. **Sự cố dừng ngoài kế hoạch** sau gần 1 năm chạy khoảng 125%: khối lượng 2026-27 thấp hơn dự báo D1.

Chấm điểm: F1-F6 chấm tự động từ BQ `commodity_prices` tại các mốc. D1-D11 chấm bằng tin chính thức (BCT, PVN, Cổng Chính phủ,
Hải quan). Ghi Brier dưới mục 4. **Đây không phải khuyến nghị mua/bán bất kỳ mã nào.**

## Nguồn (ngày công bố)
- BQ `tav2_bq.commodity_prices` (TE daily: brent, crude_oil, urals_oil, te_crack_spread_index, gasoline, heating_oil, naphtha, propane), truy vấn 09/11/2026, dữ liệu tới 06/11/2026; snapshot vĩ mô `mike/agents/Taylor/research/dd_lagcand_20261109/macro_snapshot_20261109.md` (tav2_bq.macro_indicator, UNVERIFIED).
- Tạp chí Công Thương, "BSR tăng tốc nâng cấp Nhà máy Lọc dầu Dung Quất, hướng tới năng lượng xanh", 16/10/2026 (chỉ dùng số vận hành): https://tapchicongthuong.vn/bsr-tang-toc-nang-cap-nha-may-loc-dau-dung-quat--huong-toi-nang-luong-xanh-558441.htm
- TA5 Dung Quất 15/03-01/05/2024, 48 ngày: The Investor https://theinvestor.vn/vietnams-first-oil-refinery-prepares-for-fifth-most-comprehensive-maintenance-d8744.html ; Hydrocarbon Processing https://hydrocarbonprocessing.com/news/2025/10/asia-refinery-2024-2025-maintenanceoutages/ ; gói thầu TA6: https://baodauthau.vn/lien-danh-pqn-pvchem-trung-goi-thau-134-ty-dong-bao-duong-thiet-bi-nha-may-loc-dau-dung-quat-post208680.html
- VietNamNet, Nghi Sơn nối lại dầu Kuwait, lợi nhuận 8T/2026, 03/10/2026: https://vietnamnet.vn/en/vietnam-s-nghi-son-refinery-resumes-kuwait-crude-imports-posts-530m-profit-2561438.html ; Vietnam News, TA Nghi Sơn 48 ngày từ 10/08/2027: https://vietnamnews.vn/economy/1801913/nghi-son-refinery-to-undergo-48-day-turnaround-in-august-2027.html ; Hydrocarbon Processing 10/2026: https://hydrocarbonprocessing.com/news/2026/10/vietnams-nghi-son-refinery-secures-crude-supplies-through-november-mostly-from-kuwait/
- Tuổi Trẻ, Dung Quất nhắm 8,3 tr t, 30/03/2026: https://tuoitre.vn/van-hanh-vuot-cong-suat-loc-dau-dung-quat-nham-ky-luc-8-3-trieu-tan-giu-nguon-cung-xang-dau-20260330155910682.htm ; Đại biểu Nhân dân (sản lượng Q1 +10,5%): https://daibieunhandan.vn/loc-dau-dung-quat-tang-10-5-san-luong-du-nguyen-lieu-san-xuat-den-dau-thang-5-10411008.html
- Long Sơn: Technode 13/10/2026 https://technode.global/2026/10/13/thailands-scg-to-soon-restart-long-son-petrochemicals-complex-in-vietnam/ ; Vietstock 04/2026 https://en.vietstock.vn/2026/04/long-son-petrochemicals-to-suspend-operations-from-mid-may-974-631475.htm
- IEA Oil Market Report 10/2026 (qua tóm tắt, trang gốc trả 403): https://www.iea.org/reports/oil-market-report-october-2026 ; Hellenic Shipping News https://www.hellenicshippingnews.com/?p=1147760 ; BOE Report 14/10/2026 https://boereport.com/2026/10/14/diesel-shortages-could-persist-well-into-2027-iea-says/amp/ ; OGJ https://www.ogj.com/general-interest/economics-markets/news/55411809/iea-oil-supply-rebound-remains-fragile-diesel-tightness-persists
- Kpler, "Economics improve but arbs remain closed into Europe", 26/10/2026: https://www.kpler.com/blog/economics-improve-but-arbs-remain-closed-into-europe ; QCIntel 23/10/2026: https://www.qcintel.com/article/distillates-asian-cracks-rebound-as-sing-stocks-slump-europe-eases-75890.html , https://www.qcintel.com/article/east-of-suez-crude-extends-gains-gasoil-crack-nears-70-b-75867.html
- Trần XK Trung Quốc 2026 (đợt 1 19 tr t; đợt 2 khoảng 13 tr t): Baird Maritime https://www.bairdmaritime.com/shipping/tankers/china-maintains-stable-fuel-export-quotas-for-first-batch-of-2026 ; Kpler https://www.kpler.com/blog/second-tranche-of-chinese-export-quotas-to-offer-little-relief-to-asian-product-markets
- Hormuz/đàm phán: Gulf News 02/11/2026 https://gulfnews.com/business/energy/oil-plunges-8-as-us-iran-peace-hopes-ease-hormuz-fears-1.500733408 ; Boston Globe 02/11/2026 https://www.bostonglobe.com/2026/11/02/world/iran-says-it-would-reopen-strait-hormuz-2-days-part-us-deal/ ; Al Jazeera 01/11/2026 https://aljazeera.com/news/2026/11/1/mediators-continue-us-iran-negotiations-amid-war-rhetoric-what-we-know ; FinChannel 11/2026 https://finchannel.com/us-iran-talks-continue-as-doha-mediation-ends-without-breakthrough/140371/world-2/2026/11/ ; OilPrice (Goldman 140 USD, chưa kiểm) https://oilprice.com/Energy/Energy-General/The-Iran-War-Isnt-Over-but-Oil-Traders-Are-Already-Pricing-In-Peace.html
- Thuế NK xăng dầu: NĐ 72/2026/NĐ-CP (toàn văn, Hà Tĩnh) https://hatinh.gov.vn/vi/bai-viet/toan-van-nghi-dinh-so-722026nd-cp-giam-thue-mot-so-mat-hang-xang-dau-ve-0 ; NQ 43/2026/NQ-CP: Báo Pháp luật https://baophapluat.vn/keo-dai-uu-dai-thue-xang-dau-0-den-het-nam-2026.html , MOIT https://moit.gov.vn/tin-tuc/chinh-phu-ban-hanh-nghi-quyet-ve-viec-keo-dai-thoi-han-ap-dung-uu-dai-thue-xang-dau-den-het-nam-2026.html ; TTĐB xăng 0% từ 01/11 (mâu thuẫn, chưa kiểm): https://vietbao.vn/giam-thue-tieu-thu-dac-biet-voi-xang-ve-0-tu-ngay-mai-111-613989.html
- Thuế BVMT: QĐ 482/QĐ-TTg 26/03/2026 https://tapchicongthuong.vn/giam-thue-doi-voi-xang--dau-tu-24h-ngay-26-3-2026-501494.htm ; VCCI (NQ 43 kéo tới 31/12/2026) https://vcci.com.vn/tin-tuc/giam-thue-bao-ve-moi-truong-thue-gtgt-voi-xang-dau-nhien-lieu-bay-den-het-nam-2026 ; mức nền 2026 https://www.vcci.com.vn/tin-tuc/ban-hanh-nghi-quyet-ve-muc-thue-bao-ve-moi-truong-voi-xang-dau
- E10: VOH (TT 50/2025/TT-BCT, E5 tới 2030) https://voh.com.vn/kinh-te/tu-162026-ap-dung-xang-e10-toan-quoc-nhung-chua-khai-tu-e5-654915.html ; Hà Tĩnh (BCT chốt 01/06/2026) https://hatinh.gov.vn/vi/bai-viet/bo-cong-thuong-chot-lo-trinh-cung-ung-xang-e10-tren-toan-quoc-tu-0162026
- Dự thảo nghị định kinh doanh xăng dầu: VCCI https://vcci.com.vn/news/du-thao-nghi-dinh-xang-dau-moi-giam-trung-gian-tang-quyen-tu-chu-cho-doanh-nghiep ; LSVN (Quỹ BOG) https://lsvn.vn/de-xuat-moi-ve-quy-binh-on-gia-xang-dau-a179866.html ; CafeF 05/10/2026 https://cafef.vn/tai-co-cau-thi-truong-xang-dau-188261005082212441.chn
- NK xăng dầu Q1 và 4T/2026: https://thoibaotaichinhvietnam.vn/xuat-khau-xang-dau-giam-sau-nhap-khau-tang-manh-phuc-vu-san-xuat-195896.html ; https://thoibaotaichinhvietnam.vn/viet-nam-chi-hon-10-ty-usd-nhap-khau-nhien-lieu-trong-4-thang-dau-nam-198033.html
- Tổng nguồn xăng dầu 2026: https://vneconomy.vn/dam-bao-cung-ung-xang-dau-2026-khong-de-dut-gay-trong-moi-tinh-huong.htm
- Bối cảnh Hormuz/cước tàu (đã có nguồn): `sector_read_oil_gas_shipping_20261029.md` mục 3 và mục Nguồn.
