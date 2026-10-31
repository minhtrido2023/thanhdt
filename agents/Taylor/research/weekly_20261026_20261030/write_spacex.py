import json
B=json.load(open("blocks.json")); D=B["D"]["SpaceX"]; TAB=B["TAB"]["SpaceX"]; LIV=B["LIV"]; VN=B["vn"]
L="weekly_2026-10-26_to_2026-10-30"
md=f"""# BÁO CÁO TUẦN — TÀI KHOẢN SPACEX
## Kỳ báo cáo: 26/10/2026 – 30/10/2026

**Tài khoản:** SpaceX · số hiệu 0002023347 tại công ty chứng khoán lưu ký · Chiến lược V2.4
**Ngày lập báo cáo:** 31/10/2026
**Đối tượng:** Báo cáo hiệu suất & quản lý danh mục — dành cho nhà đầu tư

> 📊 Xem biểu đồ minh hoạ đính kèm trong email (NAV, lợi nhuận lũy kế so VN-Index, phân bổ danh mục);
> bản trên kênh chat chỉ hiển thị văn bản.

---

## 1. TÓM TẮT ĐIỀU HÀNH

| Chỉ tiêu | SpaceX |
|---|---:|
| NAV cuối kỳ trước (23/10) | 968.934.792 |
| NAV cuối kỳ (30/10) | **945.141.046** |
| Thay đổi NAV theo sổ | −23.793.746 (−2,46%) |
| Trong đó: khoản chủ tài khoản rút vốn ngày 29/10 | −18.023.489 |
| **Thay đổi do hoạt động đầu tư (đã loại dòng tiền rút)** | **−5.770.257 (−0,60%)** |
| VN-Index cùng kỳ (23/10 → 30/10) | 1.774,15 → 1.741,62 (**−1,83%**) |
| Giá trị cổ phiếu cuối kỳ | 165.674.300 (17,5% NAV) |
| Tiền mặt | 30.122.995 (3,2% NAV) |
| Tiền gửi "Trứng vàng" | 749.343.751 (79,3% NAV) |
| Số mã nắm giữ cuối kỳ | 8 |

**Nhận định tuần:** VN-Index giảm **−1,83%** (từ 1.774,15 xuống 1.741,62) sau tuần tăng +4,00% trước đó: chỉ số đi ngang trong ba phiên đầu tuần rồi giảm hai phiên cuối, trong khi độ rộng thị trường suy yếu mạnh hơn nhiều so với chỉ số (tỷ lệ cổ phiếu trên đường trung bình 50 phiên từ 46,5% xuống 29,8%). Sau khi loại khoản rút vốn 18,02 triệu VND, danh mục SpaceX **−0,60%**, tốt hơn chỉ số **1,23 điểm phần trăm**; từ đầu tháng 10 danh mục **−1,89%** so với VN-Index **−1,53%** (kém 0,36 điểm phần trăm), từ khi bắt đầu hoạt động **−3,69%** so với **−6,37%** (vượt +2,67 điểm phần trăm so với chỉ số giá). Trong tuần danh mục chủ động tăng tỷ trọng cổ phiếu từ 9,5% lên 17,5% NAV: mua HT1, VPB, SCL (chiến lược khai thác hiệu ứng sau công bố lợi nhuận) và mã mới MCH, đồng thời giảm 50% vị thế DRI và thoái toàn bộ SCL sau khi đánh giá lại cơ bản (mua 1.100 cp, bán lại với giá thấp hơn 8,3%, ảnh hưởng −2,95 triệu VND). Đóng góp giá tổng cộng −6,29 triệu VND (lớn nhất: DRI −2,98 triệu, SCL −2,95 triệu, VPB −1,67 triệu, HT1 −1,54 triệu; TV1 đóng góp +3,22 triệu), được bù một phần bởi lãi tiền gửi +0,92 triệu VND. Phần còn lại 82,5% NAV nằm ở tiền gửi và tiền mặt.

![NAV theo ngày, SpaceX](assets/SpaceX_{L}_nav.png)
*NAV theo ngày, SpaceX (NAV theo sổ, gồm khoản rút vốn 18,02 triệu VND ngày 29/10). Đơn vị: VND. Kỳ dữ liệu: 23/10–30/10/2026 (6 phiên). Nguồn: dữ liệu tài khoản tại công ty chứng khoán lưu ký (NAV chốt cuối ngày), tính toán nội bộ.*

---

## 2. TOÀN CẢNH THỊ TRƯỜNG

{VN}

*VN-Index đóng cửa hằng ngày; nguồn HOSE, dữ liệu tới 30/10/2026.*

{LIV}

**Cơ bản / định giá (dữ liệu tới 30/10/2026):**
- *Định giá:* chỉ báo định giá tổng hợp (P/E, P/B và chênh lệch với lãi suất tiền gửi, phân vị 10 năm) ở **14,4/100 — vùng RẺ** (24,8 tuần trước); P/E thị trường 10,68 lần (phân vị 3), P/B 1,78 lần (phân vị 12), chênh lệch lợi suất lợi nhuận so với lãi suất tiền gửi 12 tháng +1,97 điểm % (phân vị 28). Chỉ báo mang tính tham khảo, chưa qua kiểm định đủ mạnh để dùng làm tín hiệu giao dịch (0/17 góc nhìn qua kiểm định đa giả thuyết).
- *Trạng thái thị trường theo mô hình của chiến lược:* vẫn ở mức **Trung tính**, ổn định; hiện không có tín hiệu chuyển trạng thái nào đang tích luỹ (tuần trước có tín hiệu thận trọng tích luỹ 13/25 phiên). Đây là thông tin mô hình, không phải khuyến nghị.
- *Tăng trưởng lợi nhuận, dòng tiền khối ngoại, diễn biến lãi suất mới trong tuần:* báo cáo này không có số liệu đã đối soát cho các mục này trong kỳ nên không đưa ra nhận định; chỉ sử dụng mặt bằng lãi suất đã phản ánh trong chỉ báo định giá ở trên.

![Lợi nhuận lũy kế so với VN-Index (cơ sở 100 tại 23/10/2026)](assets/SpaceX_{L}_adj_cumret.png)
*Lợi nhuận lũy kế so với VN-Index (cơ sở 100 tại 23/10/2026), NAV đã loại khoản rút vốn ngày 29/10. Đơn vị: chỉ số (cơ sở 100). Kỳ dữ liệu: 23/10–30/10/2026 (6 phiên). Nguồn: dữ liệu tài khoản tại công ty chứng khoán lưu ký (NAV chốt cuối ngày), HOSE (VN-Index), tính toán nội bộ.*

---

## 3. HIỆU QUẢ, ATTRIBUTION & RỦI RO

### 3.1 NAV theo ngày

{D['nav']}

*Thay đổi NAV hằng ngày đã loại khoản rút vốn 18.023.489 VND thực hiện trước giờ đóng cửa ngày 29/10 (thu hoạch Trứng vàng); NAV ngày 29/10 theo sổ là 945.841.724.*

Cả tuần **−0,60%** (đã loại dòng tiền rút) so với VN-Index **−1,83%** — chênh lệch **+1,23 điểm phần trăm**.

### 3.2 Hiệu suất lũy kế

{TAB}

Tài khoản bắt đầu hoạt động ngày 01/07/2026 nên quý IV/2026 (QTD) trùng với tháng 10 và chưa có số cả năm (YTD) độc lập.

**Rủi ro (từ khi bắt đầu hoạt động, theo NAV chốt cuối ngày đã loại dòng tiền ngoại sinh, 85 quan sát):** mức sụt giảm tối đa từ đỉnh −10,29% (đáy ngày 27/07, chưa bị vượt trong tuần); độ biến động hằng ngày 0,77% (quy năm khoảng 12,2%). Với 82,5% NAV ở tiền gửi và tiền mặt, độ biến động của tuần tới chủ yếu đến từ phần cổ phiếu (17,5% NAV).

### 3.3 Attribution tuần (đóng góp vào NAV, VND)

{D['attr']}

*Đóng góp giá = giá trị cuối kỳ − giá trị đầu kỳ − giá trị mua + giá trị bán, theo giá đóng cửa HOSE/UPCOM ngày 23/10 và 30/10 và giá khớp thực tế của từng lệnh (đã đối chiếu: tổng giá trị cổ phiếu cuối kỳ tính lại 165.674.300 khớp NAV chốt ngày). Cổ tức tiền mặt TV1 1.500 đ/cp × 2.300 cp = 3,45 triệu VND (trước thuế) đã nằm trong số dư tiền từ trước kỳ; khi chi trả ngày 29/10 chỉ phát sinh khấu trừ thuế 5% = 172.500 đ. Lãi Trứng vàng và lãi không kỳ hạn tính theo hiệu số từ đẳng thức tiền (khoảng 179 nghìn VND/ngày, tương ứng ≈8,5%/năm trên số dư Trứng vàng). Phí và thuế các phiên 26–28/10 theo xác nhận khớp lệnh của công ty chứng khoán; phiên 29–30/10 (phí 57.270 đ, thuế 37.340 đ) tính theo biểu phí hiện hành, chờ đối chiếu với sao kê. Số dư Trứng vàng giảm 123,90 triệu VND (873.245.042 → 749.343.751), gồm các khoản chuyển sang tiền mặt để thanh toán lệnh mua, khoản thu hoạch 18,02 triệu VND ngày 29/10 và lãi tích luỹ; các khoản chuyển này không làm đổi NAV. Tổng: −6.285.700 + 917.832 − 229.889 − 172.500 = −5.770.257 (khớp thay đổi NAV đã loại dòng tiền đến từng đồng).*

### 3.4 Hoạt động trong tuần

Tổng giá trị **mua** 135,09 triệu VND, **bán** 55,37 triệu VND:

{D['acts']}

- **Mua:** HT1, VPB và SCL (26/10, và thêm SCL ngày 28/10) thuộc chiến lược khai thác hiệu ứng sau công bố lợi nhuận; MCH (29/10) là mã mới đưa vào danh mục theo cùng chiến lược.
- **Bán:** DRI 1.250 cp (28/10) là quyết định chủ động của chủ tài khoản giảm 50% vị thế; VPB 200 cp (29/10) giảm tỷ trọng phần danh mục tạm giữ để lấy vốn cho lệnh mua MCH; SCL 800 cp (29/10, chủ tài khoản trực tiếp đặt) và 300 cp (30/10) là việc thoái toàn bộ vị thế sau khi đánh giá lại cơ bản: đợt phát hành quyền mua cho cổ đông hiện hữu làm pha loãng, và giá trị hợp lý ước tính thấp hơn giá thị trường. Vòng mua–bán SCL: mua 1.100 cp trị giá 35.600.000, bán 32.650.000, chênh lệch −2.950.000 (−8,3%).

Phí giao dịch 0,097% (HOSE) / 0,088% (UPCOM) và thuế chuyển nhượng 0,1% trên giá trị bán được khấu trừ khi giao dịch.

**Quyền lợi cổ đông:** cổ tức tiền mặt **TV1** 1.500 đ/cp × 2.300 cp = 3,45 triệu VND (trước thuế) đã được thanh toán ngày 29/10, khấu trừ thuế thu nhập cá nhân 5% (172.500 đ); khoản này đã được cộng (sau thuế) vào tỷ suất của TV1 ở bảng dưới. SCL thông báo phát hành quyền mua; vị thế SCL đã được thoái trước ngày chốt quyền nên không phát sinh nghĩa vụ nộp tiền mua.

### 3.5 Danh mục cuối kỳ (30/10/2026)

{D['port']}

*Giá vốn là giá vốn thô thực tế; "Lãi/lỗ (%)" tính theo giá đóng cửa 30/10/2026, đã cộng cổ tức tiền mặt đã đối soát được với sổ công ty chứng khoán (sau thuế thu nhập cá nhân 5%). Tổng lãi chưa thực hiện của các vị thế còn nắm giữ khoảng +1,47 triệu VND (+0,87% trên giá vốn thô 168,79 triệu VND). Với cổ phiếu thưởng và quyền mua, giá vốn được phân bổ lại trên số cổ phiếu sau thưởng/phát hành. Tiền mặt gồm tiền bán SCL ngày 30/10 (8,95 triệu VND) và các khoản tiền sở hữu khác. Đẳng thức: 165.674.300 + 30.122.995 + 749.343.751 = 945.141.046 (chênh 0 đồng).*

![Phân bổ danh mục cuối kỳ](assets/SpaceX_{L}_allocation.png)
*Phân bổ danh mục cuối kỳ 30/10/2026, % NAV ("Cổ phiếu khác" gồm MBB, VIB, TPB). Nguồn: dữ liệu tài khoản tại công ty chứng khoán lưu ký, giá đóng cửa HOSE 30/10/2026, tính toán nội bộ.*

**Ghi nhận:** danh mục gồm 8 mã, mã lớn nhất TV1 ở mức 4,82% NAV; 82,5% NAV nằm ở tiền gửi và tiền mặt. Tỷ trọng cổ phiếu (17,5%) thấp hơn nhiều so với trần phân bổ của trạng thái Trung tính (70%) vì tín hiệu mua chỉ xuất hiện theo từng nhóm nhỏ: không có tín hiệu động lượng mới, 5 mã vừa mua trong vài phiên gần đây, 4 mã đang chờ đến hạn xem xét mua, và phần danh mục tạm giữ chờ cơ hội đang để ở mức 0%; tiền chưa dùng được giữ ở tiền gửi cho tới khi có tín hiệu mới.

---

## 4. OUTLOOK KỲ TỚI (02/11 – 06/11/2026)

**Đối chiếu dự báo kỳ trước.** Kịch bản cơ sở của kỳ trước (VN-Index tích luỹ trong biên 1.740–1.800, kiểm tra lại 1.772 và 1.797) đúng về giá: cả 5 phiên đóng cửa nằm trong biên 1.741,62–1.766,65, chưa chạm 1.797. Tuy nhiên điều kiện làm sai về độ rộng (lùi dưới 40%) đã xảy ra từ phiên 29/10 (38,7%) và 29,8% ngày 30/10. Kịch bản tích cực (vượt 1.797, độ rộng vượt 50%) không diễn ra; kịch bản tiêu cực (đóng cửa dưới 1.738 hai phiên liên tiếp) chưa xảy ra (30/10 đóng cửa 1.741,62).

**Kỹ thuật.** Kịch bản cơ sở (khả năng cao nhất, ước lượng 50%): VN-Index giằng co trong vùng 1.727–1.781, trong đó đường trung bình 20 phiên (1.736,7) và đáy phiên 30/10 (1.727) là hỗ trợ, vùng 1.773–1.781 là kháng cự; độ rộng thấp (dưới 40%) khiến nhịp tăng khó bền. Kịch bản tiêu cực (ước lượng 30%): đóng cửa dưới 1.727 cùng khối lượng cao hơn trung bình 20 phiên (666 triệu cp) sẽ đưa chỉ số về kiểm tra vùng 1.677–1.690. Kịch bản tích cực (ước lượng 20%): đóng cửa vượt 1.781 với khối lượng cải thiện và độ rộng quay lại trên 40% mở đường lên 1.795 (đường trung bình 200 phiên). *Điều kiện làm sai kịch bản cơ sở:* đóng cửa ngoài vùng 1.727–1.781 với khối lượng cao hơn trung bình 20 phiên. Các xác suất là ước lượng chủ quan của người lập báo cáo, không phải dự báo thống kê đã kiểm định.

**Cơ bản.** Định giá thị trường ở vùng thấp trong lịch sử 10 năm (P/E 10,7 lần, chỉ báo tổng hợp 14,4/100) là nền hỗ trợ trung hạn nhưng không phải tín hiệu thời điểm; mô hình trạng thái của chiến lược giữ Trung tính và không có tín hiệu chuyển trạng thái đang tích luỹ. Về danh mục: 4 mã đang chờ đến hạn xem xét mua theo chiến lược khai thác hiệu ứng sau công bố lợi nhuận; nguồn tiền sẵn có lớn (tiền mặt và Trứng vàng 779,47 triệu VND, 82,5% NAV) nên việc thực hiện chủ yếu phụ thuộc vào việc tín hiệu có xuất hiện và vào quyết định của chủ tài khoản. *Điều kiện làm sai:* mô hình trạng thái chuyển sang mức thận trọng (Gấu/Khủng hoảng) sau khi tích luỹ đủ phiên xác nhận, khi đó tỷ trọng cổ phiếu mục tiêu giảm. Dòng tiền dự kiến: không có cổ tức tiền mặt nào chờ thanh toán đã biết tại ngày lập báo cáo.

Các nhận định trên là kịch bản có điều kiện, không phải khuyến nghị đầu tư chắc chắn.

---

## 5. PHỤ LỤC — PHƯƠNG PHÁP LUẬN

**Định giá:** NAV = giá trị cổ phiếu theo giá đóng cửa cuối ngày + tiền mặt + tiền gửi Trứng vàng − dư nợ (nếu có), đối chiếu trực tiếp với dữ liệu tài khoản tại công ty chứng khoán lưu ký. Đẳng thức cuối kỳ: 165.674.300 + 30.122.995 + 749.343.751 = 945.141.046 (chênh lệch 0 đồng).

**Dòng tiền ngoại sinh:** ngày 29/10 chủ tài khoản rút 18.023.489 VND (thu hoạch Trứng vàng). Mọi tỷ suất trong báo cáo (tuần, MTD, từ khi bắt đầu hoạt động, rủi ro) đã loại dòng tiền này; NAV theo sổ vẫn được trình bày ở các bảng NAV.

**Độ rộng thị trường:** tỷ lệ cổ phiếu đóng cửa trên đường trung bình 50 phiên, tính trên rổ cổ phiếu đủ điều kiện tại từng thời điểm (không dùng danh sách hiện tại để tránh sai lệch nhìn trước): 29,8% (339 mã) ngày 30/10; 46,5% (342 mã) ngày 23/10; các ngày trong tuần: 44,7% (340 mã) 26/10, 42,2% (339 mã) 27/10, 43,5% (338 mã) 28/10, 38,7% (336 mã) 29/10.

**Cổ tức & quyền lợi cổ đông:** cổ tức tiền mặt chỉ được cộng vào tỷ suất khi đã đối soát được với sổ công ty chứng khoán; thuế thu nhập cá nhân 5% trên cổ tức tiền mặt.

**Chi phí:** phí giao dịch 0,097% mỗi lượt đối với HOSE (0,088% đối với UPCOM); thuế chuyển nhượng chứng khoán 0,1% trên giá trị bán.

**Hiệu suất lũy kế:** vốn khởi điểm 1.000.000.000 VND tại 01/07/2026; VN-Index so sánh tại cùng mốc (đóng cửa 30/06/2026: 1.860,01).

**Track record:** lịch sử hoạt động còn ngắn (85 phiên kể từ 01/07/2026) — so sánh với VN-Index mang tính mô tả, chưa đủ dài để có ý nghĩa thống kê.

**Công bố tuân thủ:**
- Đây không phải là khuyến nghị đầu tư. Kết quả hoạt động trong quá khứ không đảm bảo cho kết quả trong tương lai.
- Số liệu trong báo cáo được đối chiếu với dữ liệu giao dịch tại công ty chứng khoán lưu ký tài khoản.

---

*Báo cáo tuần 26/10–30/10/2026 — Tổng hợp và đối soát bởi Đội ngũ Quản lý Danh mục & Nghiên cứu Định lượng.*
"""
open("/home/trido/thanhdt/WorkingClaude/mike/reports/SpaceX_weekly_report_2026-10-26_to_2026-10-30.md","w").write(md)
