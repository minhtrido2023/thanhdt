---
kind: registry
status: CANONICAL
source: macro-strategist (Bobby). Đọc BLIND, Mike dispatch ngày 2026-11-09. KHÔNG biết mã cổ phiếu nào, giá cổ phiếu, BCTC, forward return hay giả thuyết của bất kỳ ai khác.
blind: YES
group: market-state
parent: vn_macro_regime_history.md
role: SECTOR READ hoá chất cơ bản VN, gồm xút–clo (chlor-alkali) và axit sunfuric. Có pipeline cầu (alumina Tây Nguyên, lọc dầu, giấy, dệt nhuộm, xử lý nước), pipeline cung nội địa, giá xút/PVC/lưu huỳnh TQ, chi phí điện–muối, rào cản cạnh tranh, phân loại STRUCTURAL/CYCLICAL/ADMIN_GATED, FORECAST khoá trước 20/60/120 ngày và checklist DD.
as_of: 2026-11-09 (giá BQ sunsirs/TE tới 2026-11-06; snapshot vĩ mô 09/11; tin web ≤ 2026-11-09)
---

# SECTOR READ: Hoá chất cơ bản VN (xút–clo, axit), as-of 09/11/2026 (Bobby, real-time BLIND)

Bản đọc này không phải episode VNINDEX và không vào N_effective. Nhãn dùng trong file: **[DK]** là dữ kiện có nguồn và ngày;
**[UĐ]** là ước đoán hoặc suy luận của Bobby; **[NỀN]** là hiểu biết nền chưa kiểm lại trong lượt này.
File chị em: `sector_read_phan_dam_ure_20261104.md` và `sector_read_fertilizer_dap_20261028.md` (cùng bối cảnh Hormuz, lưu huỳnh).
Tôi chỉ dùng chúng làm mẫu định dạng.

## 0. Đã đọc và chưa đọc (kiểm toán blind)
- **Repo đã đọc:** `macro_snapshot_20261109.md` (Mike đưa); `sector_read_phan_dam_ure_20261104.md` (mẫu);
  `feeds/bq_commodity_prices.md` (bẫy nguồn); `~/.claude/skills/due-diligence/SKILL.md` (chỉ grep "bước 3");
  `market-state/index.md` và `vn_macro_regime_history.md` (chỉ grep "sector_read").
- **BQ (tự truy vấn 09/11):** `tav2_bq.commodity_prices`, luôn chỉ rõ `source`, loại T7/CN:
  - `sunsirs` daily: `caustic_soda`, `polyester_staple_fiber`, `cotton_yarn`.
  - `trading_economics` daily: `polyvinyl` (PVC), `soda_ash`, `sulfur`, `aluminum`, `coal`, `kraft_pulp`, `brent`.
  - Không dùng view `commodity_latest`.
- **Web:** chỉ bài có ngày công bố ≤ 09/11/2026. Ngày ghi ở mục Nguồn.
- **Chưa đọc hoặc đã bỏ qua (ghi trung thực):**
  - Không mở `kb/projects/*`, `agents/Taylor/*` (ngoài file snapshot được giao), không tra giá cổ phiếu hay BCTC.
  - Không mở báo cáo CTCK nào (một file đính kèm của CTCK xuất hiện trong kết quả tìm kiếm, tôi không mở).
  - Không đọc bài CafeF 28/07/2026 có tiêu đề "Loại hoá chất chiến lược tăng giá gấp 2,7 lần… doanh nghiệp Việt lãi cao
    nhất 10 năm". Tôi chỉ thấy tiêu đề.
  - **Rò rỉ không chủ ý, ghi để người sau biết:**
    (a) `gitStatus` đầu phiên liệt kê tên các thư mục DD theo mã (`dd_redo_20261105/<mã>`) và thư mục `dd_lagcand_20261109/`.
    Tôi không mở thư mục nào ngoài file snapshot.
    (b) Skill `due-diligence` và file `feeds/bq_commodity_prices.md` có nhắc vài mã hoá chất/phân bón làm ví dụ.
    (c) Tóm tắt tìm kiếm có nêu tên các doanh nghiệp đứng sau dự án xút mới, một DN luyện kim màu, và một câu kiểu
    "DN X nắm lợi thế vượt trội so với xút nhập khẩu". Ngoài ra có hai con số "nhu cầu xút nội địa ~450 nghìn t, công suất
    ~230 nghìn t". Hai số này có vẻ lấy từ tài liệu tài chính, nên tôi chỉ dùng như một nguồn có độ tin cậy trung bình.
    Tôi **không dùng** KQKD, giá cổ phiếu hay nhận định doanh nghiệp nào. Trong thân file, dự án chỉ gọi theo **vùng**.
    Một số URL ở mục Nguồn vẫn có tên DN, nên người đọc blind sau nên bỏ qua mục Nguồn.

## 1. Chuỗi giá và đa proxy [DK, BQ trừ khi ghi khác]
| Chuỗi | Hiện tại | Mốc so sánh | Ghi chú |
|---|---|---|---|
| Xút TQ (sunsirs `caustic_soda`, CNY/t, **basis có vẻ là xút lỏng 32%, chưa xác minh**) | **568** (04-06/11). TB5 **574,0**. TB T10 624 | TB 2024: 845. T10/25: 844. T4/26: 710. Q3/26: 641 | **Đáy toàn chuỗi** (phân vị 0% trên 757 phiên, nhưng chuỗi chỉ có từ 15/09/2023). **−26% YoY** (T10), **−30%** (T11 so với T11/25: 823) |
| Quy đổi thô sang USD/t, NaOH 100% [UĐ] | 568 × 3,125 / 6,67 ≈ **266 USD/t** (có thể gồm VAT TQ) | T10/25: 844 × 3,125 / 7,13 ≈ 370 | Khớp về độ lớn với FOB TQ 230-240 USD/t đầu T6 và giá XK hải quan 248 (T3), 302 (T4) (SunSirs 26/06) |
| PVC TQ (TE `polyvinyl`, CNY/t) | **4.978** (06/11). TB5 **5.131,0** | T10/25: 4.653. TB 2024: 5.577. Trung vị từ 2016: 6.330 | Phân vị khoảng **18%** lịch sử từ 2016. Giảm 5 phiên liền từ 5.295 |
| Soda ash TQ (TE `soda_ash`, CNY/t, **không phải xút**, bẫy 5 file feeds) | 1.010 | T10/25: 1.185. TB 2024: 1.937 | Liên quan dự án soda 400 nghìn t (mục 3) |
| Lưu huỳnh TQ (TE `sulfur`, CNY/t) | **5.274** (06/11). TB5 **5.271,75** | Đỉnh 11.084 (06/2026). Trung vị tháng 6/2025 khoảng 2.346 (file feeds) | **−52% từ đỉnh** nhưng vẫn khoảng gấp đôi giữa 2025. Đầu vào của axit sunfuric đốt lưu huỳnh |
| Nhôm LME (TE `aluminum`, USD/t) | 3.066 | T10/25: 2.792. TB 2024: 2.459 | **+10% YoY.** Đỡ biên và sản lượng alumina |
| Than (TE `coal`, USD/t) | TB T10 150,3 | T10/25: 104,8 | **+43% YoY.** Đè chi phí phát điện của EVN |
| Bột giấy kraft TQ (TE, CNY/t) | 4.611 (TB T11) | T10/25: 4.834. TB 2024: 5.830 | −5% YoY. Cầu giấy không nóng |
| Xơ polyester TQ (sunsirs, CNY/t) | 8.908 | T10/25: 6.331 | +41% YoY, kéo theo dầu. Đây là chi phí, không phải cầu dệt |
| Giá xút nội địa VN | **không có số** | — | BQ không có, web không ra số T10/2026 |
| Xút CFR Đông Nam Á | **không có số T10-T11** | 383-420 USD/dmt (Argus, T2/2026); 380-400 (giữa 2026, bài tổng hợp) | Mốc cũ, chỉ dùng tham chiếu |
| Axit sunfuric VN | **không có số mức** | Q3/2026 **+259% YoY** (một DN luyện kim màu phía Bắc công bố, Báo Pháp luật) | SunSirs: axit nội địa TQ giảm đều trong T9/2026 |

**Phân kỳ lớn nhất [UĐ dựa trên DK]:** Hormuz làm năng lượng, cước biển và lưu huỳnh tăng vọt (Brent +68% YoY, than +43%,
lưu huỳnh từng gấp 4-5 lần). Thế nhưng **xút TQ lại ở đáy 3 năm**. Lý do (SunSirs 20/05, ECHEMI 28/10):
1. TQ đưa vào khoảng 1,5 tr t công suất xút mới năm 2026, trên kế hoạch khoảng 3,5 tr t.
2. Alumina, khách hàng lớn nhất, bị giới hạn mở rộng do thiếu bô-xít. Nhà máy alumina Sơn Đông liên tục hạ giá thu mua
   (580 CNY/t cuối T7, lại −10 CNY cuối T10).
3. Chỉ có kênh XK là ổn định.

Kết luận về **hướng**: xút là sản phẩm phụ cưỡng bức của dư cung TQ, **không** đi theo cú sốc năng lượng. Về **mức**: giá
đang sát giá vốn tiền mặt của nhà sản xuất TQ. Ước thô: điện khoảng 2.300-2.500 kWh/t cộng muối khoảng 1,5 t/t, chưa trừ
tín dụng clo [NỀN]. Vì vậy dư địa giảm thêm có hạn, như ECHEMI cũng nói.

**Bẫy dữ liệu:**
1. Basis của `caustic_soda` sunsirs chưa xác minh. Mức 600-1.000 CNY khớp xút lỏng 32% (SunSirs 20/05 nêu 827 đầu 2025,
   690 cuối 2025 cho loại 32%). BQ cho TB T1/2025 là 910 và T12/2025 là 749, tức **lệch 6-10%**, có thể do khác vùng. Chỉ
   tin **hướng** và **phân vị**.
2. Chuỗi xút chỉ có 3 năm, nên phân vị 0% chỉ nói "thấp nhất 3 năm", không nói "thấp nhất chu kỳ dài".
3. `soda_ash` là Na2CO3. Không được dùng thay xút.

## 2. Pipeline cầu VN
**Quy mô [DK, độ tin cậy trung bình]:**
- Nhu cầu xút nội địa 2025 khoảng **450 nghìn t**, công suất trong nước khoảng **230 nghìn t/năm**, tức tự cung khoảng
  50-55% (nguồn tài chính VN qua tóm tắt tìm kiếm). Tạp chí Công Thương cũng viết "nguồn cung nội địa chỉ đáp ứng khoảng 50%"
  và "thiếu hụt kéo dài".
- **⇒ VN là nước nhập ròng xút khoảng 200-220 nghìn t/năm [UĐ]**, chủ yếu từ TQ. Hàng sang VN mất 5-7 ngày, so với 12-18
  ngày đi Úc (SunSirs 26/06).

**Các mảng cầu:**
| Mảng | Dữ kiện | Ước tính xút | Xu hướng |
|---|---|---|---|
| **Alumina Tây Nguyên** (2 tổ hợp, Lâm Đồng sau sáp nhập tỉnh) | Alumina 9T/2026 khoảng **1,0 tr t (+1,7%)**, Q3 khoảng 380 nghìn t **(+9,3%)** (AlCircle 08/10/2026) | **Khoảng 80-160 nghìn t/năm** [NỀN: 60-120 kg NaOH/t alumina tuỳ quặng], tức có thể là mảng lớn nhất (20-35% cầu) [UĐ] | Ngắn hạn đi ngang hoặc tăng nhẹ |
| Mở rộng alumina | TKV đề xuất nâng mỗi tổ hợp lên 800 nghìn t, tổng 1,6 tr t (bài không rõ ngày). Lâm Đồng duyệt khoảng 2,3 tỷ USD cho **dây chuyền alumina thứ 2, 1,2 tr t/năm** tại Bảo Lâm (tiêu đề SMM, khoảng T2/2026; trang gốc trả 404, **chưa kiểm chứng**). Mục tiêu TKV: 8,032 tr t alumina giai đoạn 2026-30, 4-6 tr t/năm giai đoạn 2031-45 | Nếu có dây chuyền 1,2 tr t thì thêm **khoảng 70-140 nghìn t xút/năm**, nhưng sớm nhất 2029-30 [UĐ] | Cầu dài hạn **STRUCTURAL tăng**, phụ thuộc giải ngân và quy hoạch (Lâm Đồng xin điều chỉnh hơn 65.000 ha quy hoạch bô-xít) |
| Nhôm điện phân | Nhà máy 450 nghìn t Al/năm, thỏi đầu tiên 26/07/2026, giai đoạn 3 xong Q1/2027 (AlCircle 08/10) | Không dùng xút trực tiếp. Hút alumina trong nước (khoảng 0,87 tr t) nên **tạo động lực** cho alumina chạy hết công suất [UĐ] | Tăng |
| Lọc hoá dầu | HĐ cung ứng **138.600 t xút lỏng 50%** cho NMLD giai đoạn 2026-28 (ký 24/02/2026) | Khoảng 23 nghìn t/năm (quy 100%) [UĐ] | Ổn định, đã ký |
| Giấy/bột giấy, dệt nhuộm, xử lý nước (PAC, javen, clo lỏng), chất tẩy rửa, chế biến thực phẩm/thuỷ sản | **không có số theo mảng** | — | SX công nghiệp **+15,0% YoY** (T10), PMI 52,3, XK +41% YoY (T9) theo snapshot. Cầu khối lượng tốt. Bột giấy TQ −5% YoY nên mảng giấy không nóng |

**Đọc [UĐ]:** cầu **khối lượng** VN đang tốt (công nghiệp +15%, alumina Q3 +9%). Vấn đề của ngành là **giá**, không phải
lượng. Giá xút nội địa bị neo bởi **import parity** = FOB TQ + cước 5-7 ngày + chi phí kho bồn. FOB TQ ở đáy 3 năm, và VND
**mạnh lên 2,77% YoY** so với USD (snapshot) nên import parity tính bằng VND giảm thêm. Ước thô: import parity VND **giảm
khoảng 25-30% YoY** [UĐ]. Mức tuyệt đối: không có số.

## 3. Pipeline cung nội địa và cấu trúc cạnh tranh
**Dự án xút mới (gọi theo vùng) [DK, toàn bộ là kế hoạch, chưa có số vận hành]:**
| Vùng | Quy mô | Mốc |
|---|---|---|
| **Thanh Hoá (KKT Nghi Sơn)**, tổ hợp 12.000 tỷ | GĐ1A: **50 nghìn t NaOH 100%** + HCl 15 nghìn t + javen 10 nghìn t + PAC 30 nghìn t. GĐ1: 80 nghìn t xút. Dự án 2: **100 nghìn t xút rắn + 150 nghìn t PVC**, khoảng 6.000 tỷ. GĐ3: soda 400 nghìn t | GĐ1A dự kiến Q2/2026 (VnEconomy 09/08/2025). Dự án 2: khởi công 2026, vận hành Q4/2027. **Tới 09/11/2026 tôi không tìm thấy tin xác nhận đã ra sản phẩm** (tìm chưa đầy đủ) |
| **Đồng Nai (KCN Nhơn Trạch 6)** | **Di dời bắt buộc** toàn bộ nhà máy khỏi KCN Biên Hoà 1, đồng thời mở rộng lên **100 nghìn t NaOH + 100 nghìn t H2SO4** | Khởi công T9/2025 (Đại biểu Nhân dân 26/09/2025). **Không có ngày vận hành** |
| **Lâm Đồng (Bảo Lâm)**, cạnh tổ hợp alumina | GĐ1 đang chạy **20 nghìn t**. GĐ2 lên **45 nghìn t** + clo lỏng 36 nghìn t | Q1/2026 đến Q4/2029 (Báo Pháp luật 13/07/2026) |
| KCN Phú Vinh | Dự án 2.800 tỷ có dây chuyền NaOH-clo | GĐ2 trong 48 tháng. Công suất: **không có số** |

**Cộng dồn [UĐ]:** công suất nội địa có thể đi từ khoảng 230 lên khoảng **430-500 nghìn t vào 2028-2030**. Đây là tổng
gộp; phần tăng ròng ở Đồng Nai không rõ vì là di dời cộng mở rộng. Cầu đến 2029 khoảng 550-650 nghìn t nếu tăng 5-8%/năm và
có thêm alumina. ⇒ **Thiếu hụt thu hẹp từ khoảng 220 xuống khoảng 50-150 nghìn t. VN vẫn nhập ròng**, nên giá vẫn neo
import parity. Nhưng các nhà sản xuất nội địa sẽ **cạnh tranh nhau** giành khách lớn (alumina, lọc dầu) chứ không còn chỉ
"bán phần thiếu hụt".

**Rào cản và lợi thế tự nhiên [NỀN + UĐ]:**
1. **Logistics xút lỏng.** Xút lỏng 32-50% chứa 50-68% nước, nên nhập khẩu phải dùng tàu và bồn hoá chất. Nhà sản xuất gần
   khách hàng có lợi thế cước, ước **30-60 USD/t** (chưa kiểm). Đây là "hào" thật nhưng hẹp. Xút vảy/rắn nhập dễ hơn.
2. **Ràng buộc phía clo (quan trọng nhất).** Mỗi 1 t NaOH sinh ra **0,886 t Cl2**. VN gần như chưa có PVC đi từ clo trong
   nước: dự án Thanh Hoá tự mô tả là "lần đầu sản xuất PVC", còn dẫn xuất clo (HCl, javen, chloramine B) được gọi là "lần
   đầu tại VN". Clo phải đi vào HCl, PAC, javen, clo lỏng xử lý nước, mà các thị trường này nhỏ và địa phương. Khoảng 200
   nghìn t xút mới sẽ sinh **khoảng 180 nghìn t clo**. Nếu clo không tiêu thụ hết thì nhà máy phải giảm tải hoặc bán HCl/clo
   rẻ, thậm chí âm, nên **ECU (xút + giá trị clo) xấu đi dù giá xút đứng yên** [UĐ]. Dây chuyền PVC 150 nghìn t (Q4/2027)
   hút được khoảng 85 nghìn t clo, đúng là để giải bài toán này, nhưng PVC TQ đang ở phân vị 18%.
3. **Vốn và giấy phép môi trường** cho nhà máy clo-kiềm cao, cộng yêu cầu an toàn clo. Đây là rào cản gia nhập với người
   mới, không phải với các dự án đã có chủ trương ở trên.
4. **Quyền lực người mua:** tổ hợp alumina là khách mua lớn, tập trung, có thể nhập trực tiếp từ TQ. Giá hợp đồng nhiều khả
   năng gắn giá TQ hoặc import parity [UĐ].

**Chi phí:**
- **Điện** [DK]: EVN **giảm 2%** giá bán lẻ bình quân còn 2.159,9037 đ/kWh từ 01/11/2026 (QĐ 1305/QĐ-EVN ngày 30/10;
  QĐ 2892/QĐ-BCT ngày 31/10 về biểu giá theo nhóm). Biểu giá mới gộp theo cấp điện áp và có cơ cấu riêng cho khách SX mua
  ở cấp 220kV trở lên (theo tóm tắt, chưa đọc văn bản). Cơ chế: NĐ 72/2025, sửa bởi NĐ 278/2026 (hiệu lực 09/07/2026). Tăng
  2-5% phải có ý kiến Bộ; hai lần điều chỉnh cách nhau tối thiểu 3 tháng.
  **Điện chiếm khoảng 50-60% giá vốn tiền mặt của xút** [NỀN]. Mâu thuẫn [UĐ]: than +43% và Brent +68% YoY mà giá điện lại
  giảm. Đợt giảm này có thể do thuỷ điện dồi dào (VOV có bài "thuỷ điện dồi dào, vì sao chưa giảm") và **khó bền** nếu nhiên
  liệu giữ mức cao sang mùa khô 2027.
- **Muối** [DK]: SX muối VN 2025 khoảng 900 nghìn t (muối công nghiệp khoảng 270 nghìn t), cầu khoảng 2 tr t, nên phải nhập.
  Có hạn ngạch thuế quan muối 2026 theo TT 03/2026/TT-BCT (tổng 97.020 t theo một nguồn). Thời điểm phân giao hạn ngạch
  **muối làm nguyên liệu hoá chất** do Bộ Công Thương phối hợp Bộ NN&MT xác định. Đây là **đầu vào bị hành chính hoá**.
  Thuế ngoài hạn ngạch theo trang bên thứ ba là 60-90%, chưa kiểm biểu thuế chính thức. Giá muối nhập: không có số.
  Định mức khoảng 1,5-1,6 t muối/t NaOH [NỀN].
- **Phòng vệ thương mại:** không tìm thấy vụ điều tra chống bán phá giá xút nào của Bộ Công Thương. Khung pháp lý là
  NĐ 86/2025. Thuế NK xút (HS 2815) theo ACFTA/ATIGA: **không có số** (DD phải kiểm).

**Axit sunfuric (phân khúc phụ) [DK + UĐ]:** có 2 nhóm nhà sản xuất.
- **Đốt lưu huỳnh:** chịu cú sốc chi phí khi lưu huỳnh TQ lên đỉnh 11.084 CNY (T6). Lưu huỳnh nay −52%.
- **Thu hồi khí thải lò luyện kim màu:** axit là sản phẩm phụ nên **hưởng lợi bất thường**, giá Q3 +259% YoY.
- SunSirs ghi nhận axit nội địa TQ giảm đều trong T9. Cú sốc đang **đảo chiều**, giống chu kỳ lưu huỳnh/DAP ở file chị em.
- Dự án Đồng Nai có thêm 100 nghìn t H2SO4, mốc chưa rõ.

## 4. PHÂN LOẠI
**(a) Giá xút TQ ở đáy 3 năm là ĐÁY CHU KỲ trên nền DƯ CUNG CẤU TRÚC. Khó bật mạnh trước Q2/2027. Độ tin cậy khoảng 0,7.**
- Bằng chứng nghiêng cấu trúc: TQ vẫn thêm khoảng 1,5 tr t/năm, PVC không có công suất mới nên khó hấp thụ clo, alumina
  thiếu bô-xít, XK được dự báo đi ngang ở 3,0-3,5 tr t/năm, và SunSirs dự báo "biến động ở mức thấp… áp lực giảm kéo dài".
- Bằng chứng nghiêng chu kỳ: giá sát giá vốn tiền mặt, mùa bảo dưỡng T3-T5 (năm 2026 hệ số vận hành rơi từ trên 86% xuống
  75-78%), Hormuz làm Đông Bắc Á chạy 60-70% công suất (Argus 13/04).
- P(sunsirs `caustic_soda` > 700 ở bất kỳ phiên nào trước 31/03/2027) ≈ **0,10**.

**(b) Chế độ biên của nhà sản xuất xút–clo VN, 2-4 quý tới:**
| Nhãn | P | Lý do |
|---|---|---|
| **CYCLICAL** | **0,45** | Giá xút TQ là biến chu kỳ, đang ở đáy và sát giá vốn. Cầu khối lượng VN tốt (CN +15%, alumina +9%). Giá điện vừa giảm 2%. Đảo chiều được trong 2-4 quý nếu TQ bảo dưỡng hoặc cắt công suất, hoặc alumina khu vực tăng |
| **STRUCTURAL** | **0,35** | (1) Trần giá do dư cung TQ, hàng sang VN chỉ 5-7 ngày, nên premium import parity không bao giờ lớn. (2) Công suất nội địa có thể gần gấp đôi 2026-2029 trong khi thiếu hụt thu hẹp: chuyển từ "bán phần thiếu" sang cạnh tranh giành khách lớn. (3) Ràng buộc clo làm ECU của nhà máy mới xấu hơn nhà máy cũ. (4) Mặt ngược cũng là cấu trúc: cầu alumina dài hạn tăng (mục tiêu TKV 2031-45), nhưng chưa tới trong 2-4 quý |
| **ADMIN_GATED** | **0,20** | Giá điện (EVN/Bộ Công Thương, cơ chế NĐ 72/278), hạn ngạch muối nguyên liệu hoá chất, di dời nhà máy bắt buộc (Biên Hoà 1 sang Nhơn Trạch), phân bổ hợp đồng với tổ hợp alumina của DNNN, giấy phép môi trường/an toàn clo. Không có PVTM bảo hộ xút. Một quyết định giá điện ±3-5% có thể dịch giá vốn khoảng ±2-3% [UĐ] |

Mức tin: **ambiguous khoảng 55/45** (CYCLICAL so với STRUCTURAL). Diễn giải: đây **không phải cú sốc vĩ mô VN**. Vĩ mô VN đang
đỡ khối lượng. Giá do TQ quyết, VN chỉ chỉnh được tham số chi phí (điện, muối) và tiến độ dự án.

**(c) Axit sunfuric: cú sốc lưu huỳnh 2026 là TẠM THỜI và đang đảo chiều, độ tin cậy clean khoảng 0,85.** Lưu huỳnh −52% từ
đỉnh trong khi Hormuz chưa mở hẳn. Đây là cùng mẫu "đỉnh cấp tính tự vỡ" như urê/DAP. Lãi bất thường của nhóm axit thu hồi
(Q2-Q3/2026) **không** phải mức bền. P(TE `sulfur` > 8.000 ở bất kỳ phiên nào trước 31/03/2027) ≈ **0,10** (cần kịch bản leo
thang K3).

## 5. FORECAST KHOÁ TRƯỚC (lập 2026-11-09; chấm theo quan sát cuối cùng ≤ ngày kiểm)
**Proxy chấm:** BQ `tav2_bq.commodity_prices`, `cadence='daily'`, loại T7/CN:
- **X** = `caustic_soda`, `source='sunsirs'`, TB 5 quan sát cuối ≤ ngày chấm. Gốc = **574,0** (5 quan sát 02-06/11: 590, 576, 568, 568, 568).
- **P** = `polyvinyl`, `source='trading_economics'`, TB5. Gốc = **5.131,0** (02-06/11).
- **S** = `sulfur`, `source='trading_economics'`, TB5. Gốc = **5.271,75** (02-06/11).

**Kịch bản nền [UĐ]** (Hormuz giữ nguyên xác suất của file urê 04/11: K1 tranh chấp/đóng phần lớn 0,50, K2 thoả thuận 0,35, K3 leo thang 0,15):
- Xút ít nhạy với Hormuz, nhạy với tồn kho TQ và giá thu mua của alumina.
- Lưu huỳnh và PVC nhạy với Hormuz (năng lượng, naphtha, ethylene).

| Mốc (ngày chấm) | Chuỗi | Dự báo |
|---|---|---|
| **2026-11-29** (+20 ngày) | X | Trung vị **562**, khoảng 80% **535-595**. **P(<574,0) = 0,62**; P(≤540) = 0,13; P(≥600) = 0,08 |
| | P | Trung vị **5.000**, khoảng 80% **4.750-5.300**. **P(<5.131,0) = 0,65** |
| **2027-01-08** (+60 ngày) | X | Trung vị **570**, khoảng 80% **520-640**. **P(<574,0) = 0,53**; P(≤530) = 0,15; P(≥630) = 0,12 |
| | P | Trung vị **5.030**, khoảng 80% **4.600-5.450**. **P(<5.131,0) = 0,58** |
| | S | Trung vị **4.900**, khoảng 80% **4.000-6.000**. **P(<5.271,75) = 0,62** |
| **2027-03-09** (+120 ngày) | X | Trung vị **585**, khoảng 80% **515-690**. **P(<574,0) = 0,46**; P(≤530) = 0,17; P(≥680) = 0,10 |
| | P | Trung vị **5.100**, khoảng 80% **4.500-5.700**. **P(<5.131,0) = 0,52** |
| | S | Trung vị **4.600**, khoảng 80% **3.500-6.300**. **P(<5.271,75) = 0,65** |
| **Câu (a)** | X daily > 700 ở bất kỳ phiên nào trước 2027-03-31 | P = **0,10** |
| **Câu (c)** | `sulfur` TE daily > 8.000 ở bất kỳ phiên nào trước 2027-03-31 | P = **0,10** |
| **E1 (cung)** | Có nguồn chính thức hoặc báo chí uy tín xác nhận dây chuyền xút ở KKT Nghi Sơn (Thanh Hoá) **đã vận hành thương mại hoặc ra sản phẩm** trước 2027-03-31 (kể cả nếu thực tế đã chạy trước as-of) | P = **0,70** |
| **E2 (điện)** | EVN tăng giá bán lẻ điện bình quân (bất kỳ %) có hiệu lực trước 2027-03-31 | P = **0,20** [UĐ: vừa giảm 01/11, phải cách tối thiểu 3 tháng nên sớm nhất 01/02/2027; áp lực nhiên liệu cao] |
| **E3 (PVTM)** | Bộ Công Thương khởi xướng điều tra AD hoặc tự vệ với xút (HS 2815) trước 2027-06-30 | P = **0,05** |
| **E4 (cầu)** | Khởi công chính thức một dây chuyền alumina mới ≥1 tr t/năm ở Lâm Đồng trước 2027-06-30 | P = **0,25** |

Cách chấm: Mike/Bobby truy vấn BQ (`source` chỉ định rõ) tại 3 mốc rồi ghi Brier dưới bảng này. E1-E4 chấm bằng văn bản
hoặc báo chí có ngày. Chuỗi X đứng giá nhiều phiên liền (568 ba phiên), nên chấm kèm tin SunSirs/ECHEMI để tránh "đúng do
chuỗi không nhúc nhích".

## 6. Chỉ báo dẫn dắt
| # | Chỉ báo (tần suất) | Nguồn | Tín hiệu lên ⇔ xuống |
|---|---|---|---|
| 1 | Giá thu mua xút của nhà máy alumina Sơn Đông/Quảng Tây (sự kiện) | SMM, SunSirs | Tăng 2 lần liên tiếp ⇔ hạ tiếp dưới 560 CNY |
| 2 | Hệ số vận hành clo-kiềm TQ và mùa bảo dưỡng (tuần) | SunSirs, ECHEMI, Argus | < 78% trong T3-T5 ⇔ > 85% kèm công suất mới vào |
| 3 | PVC TQ và giá clo lỏng/HCl (ngày) | TE `polyvinyl`, SunSirs | PVC > 5.600 (ECU đỡ) ⇔ PVC < 4.700 kèm clo âm (TQ buộc giảm tải, xút có thể tăng ngược) |
| 4 | XK xút lỏng TQ (tháng) và FOB (tuần) | SunSirs (hải quan TQ) | XK giảm, FOB > 300 USD ⇔ XK > 350 nghìn t/tháng, FOB < 250 |
| 5 | Sản lượng alumina VN (quý) và tiến độ mở rộng (sự kiện) | TKV, AlCircle, UBND Lâm Đồng | Alumina > +10% YoY, khởi công dây chuyền mới ⇔ sự cố môi trường hoặc dừng máy |
| 6 | Văn bản giá điện, biểu giá cho cấp 220kV (sự kiện) | EVN, Bộ Công Thương | Giảm hoặc giữ ⇔ tăng ≥ 2% |
| 7 | Tiến độ vận hành 3 dự án xút trong nước (sự kiện) | Báo chí, CBTT | Trễ hẹn (cung chậm) ⇔ vận hành đúng hẹn (cạnh tranh sớm) |
| 8 | Lưu huỳnh TE và axit sunfuric (ngày/tuần) | BQ `sulfur`, SMM | Leo thang Hormuz ⇔ thoả thuận, cảng TQ hết khan |

## 7. DD cần kiểm gì (BCTC một nhà sản xuất xút–clo/axit VN phải chứng minh được)
1. **Giá bán bình quân (ASP) xút theo dạng** (lỏng 32/45/50%, vảy/rắn), quy về NaOH 100%, theo quý, sau chiết khấu.
   - So với import parity: FOB TQ + cước + bồn. ASP nội địa không thể vượt import parity lâu.
   - Tách premium logistics xút lỏng (ước 30-60 USD/t) khỏi phần do may mắn chu kỳ.
2. **Sản lượng, công suất hiệu dụng, hệ số vận hành.** Ràng buộc phía clo:
   - Clo tiêu thụ hết bao nhiêu và vào sản phẩm nào (HCl, PAC, javen, clo lỏng).
   - Giá HCl/clo có lúc âm không. Chi phí trung hoà hoặc huỷ clo.
   - ⇒ Tính **ECU = giá xút + 0,886 × giá trị clo ròng**.
3. **Điện:**
   - Mức tiêu hao kWh/t NaOH, giá điện thực trả, cấp điện áp, cơ cấu giờ cao/thấp điểm.
   - Tác động của QĐ 2892/QĐ-BCT (biểu giá từ 01/11/2026).
   - Tỷ trọng điện trong giá vốn. Độ nhạy theo ±5% giá điện.
4. **Muối:** nguồn (nội địa hay nhập, nước nào), giá CIF, hạn ngạch thuế quan được phân giao và thời điểm, chi phí tinh chế,
   tồn kho muối.
5. **Màng điện phân và capex duy trì:** chu kỳ thay màng (khoảng 3-5 năm [NỀN]), có vốn hoá hay chi phí ngay.
6. **Khách hàng lớn:**
   - Hợp đồng với tổ hợp alumina và lọc dầu: công thức giá (gắn giá TQ? cố định?), kỳ hạn, khối lượng tối thiểu.
   - Mức tập trung khách hàng, phải thu, bảo lãnh.
7. **Dự án mới / di dời** (áp luật base NPV=0 của skill DD):
   - Tiến độ thật so với kế hoạch, chi phí chạy thử, lãi vay vốn hoá, nguồn vốn.
   - Khấu hao tăng khi vận hành, đường ramp-up.
   - Phần **clo của dự án mới đi đâu**.
8. **Di dời bắt buộc khỏi KCN cũ:**
   - Bồi thường, giá trị quỹ đất cũ: là **khoản một lần, phải tách khỏi lợi nhuận cốt lõi**.
   - Suy giảm giá trị tài sản cũ, gián đoạn sản xuất trong giai đoạn chuyển, chi phí môi trường.
9. **Axit sunfuric:**
   - Đi từ đốt lưu huỳnh hay thu hồi khí thải lò luyện.
   - Giá lưu huỳnh đầu vào và độ trễ tồn kho.
   - **Tách lãi bất thường Q2-Q3/2026** khỏi mức bền.
10. **Tồn kho và NRV:** dự phòng giảm giá khi xút TQ ở đáy.
11. **An toàn và môi trường:** sự cố rò clo/axit, giấy phép, xử phạt, chi phí tuân thủ (khu bô-xít từng có sự cố môi trường;
    ngày của từng sự cố chưa kiểm).
12. **Thu nhập tài chính:** lãi tiền gửi chiếm bao nhiêu LNTT. Lãi bán tài sản/đất là một lần.
13. **Tỷ giá:** VND mạnh lên 2,77% YoY. Muối, màng và thiết bị mua bằng USD, trong khi giá bán VND neo import parity. Kiểm
    vị thế ngoại tệ ròng.
14. **Thuế:** thuế NK xút HS 2815 theo các FTA (để biết hàng TQ vào VN có hàng rào nào không), ưu đãi TNDN cho dự án mới,
    VAT đầu vào điện/muối.
15. **Mảng ngoài xút–clo** (nếu có): tách biên gộp từng mảng để không gán biên mảng khác cho xút.

## 8. Điều gì làm tôi sai
1. **TQ cắt công suất theo chính sách** (chống "nội quyển", siết năng lượng/khí thải [NỀN]) hoặc mùa bảo dưỡng 2027 sâu hơn
   2026. Khi đó xút bật lên 700-800 CNY trước Q2/2027, và forecast 120 ngày lệch xuống quá nhiều.
2. **Hormuz leo thang (K3).** Đông Bắc Á và Đông Nam Á giảm tải thêm, cước tăng, nên CFR Đông Nam Á tăng nhanh hơn FOB TQ.
   Import parity VN khi đó tăng dù xút TQ đứng yên. Tôi không có số CFR Đông Nam Á T10-T11 để kiểm.
3. **Basis chuỗi sunsirs sai** (không phải 32% lỏng, hoặc vùng khác). Quy đổi USD ở mục 1 khi đó lệch, nhưng phân vị và
   hướng vẫn dùng được.
4. **Nhu cầu 450 nghìn t / công suất 230 nghìn t sai.** Hai số này chỉ từ 1-2 nguồn tóm tắt. Nếu thiếu hụt nhỏ hơn thì cạnh
   tranh nội địa đến sớm hơn (nghiêng STRUCTURAL). Nếu lớn hơn thì ngược lại.
5. **Dự án nội địa trễ nhiều năm** (thường gặp ở VN [NỀN]). Thiếu hụt khi đó kéo dài, và phần STRUCTURAL (cạnh tranh nội
   địa) lùi sau 2029.
6. **Giá điện VN tăng mạnh 2027** vì nhiên liệu. Chi phí tăng trong lúc giá bán neo TQ, nên biên bị ép, nghiêng ADMIN_GATED.

**Đây không phải khuyến nghị mua/bán bất kỳ mã nào.**

## Nguồn (ngày công bố)
- BQ `tav2_bq.commodity_prices` (truy vấn 09/11/2026): sunsirs `caustic_soda` (prodetail-368), `polyester_staple_fiber`,
  `cotton_yarn`; TE `polyvinyl`, `soda_ash`, `sulfur`, `aluminum`, `coal`, `kraft_pulp`, `brent`. Phân vị tự tính.
- Snapshot vĩ mô: `agents/Taylor/research/dd_lagcand_20261109/macro_snapshot_20261109.md` (as-of 09/11/2026).
- ECHEMI, bình luận xút ngày 28/10/2026: https://www.echemi.com/cms/3292083.html
- SunSirs, "Structural Reshaping of the Caustic Soda Industry Underway", 20/05/2026: https://www.sunsirs.com/uk/detail_news-33003.html
- SunSirs, "Current Status of Liquid Caustic Soda Exports and Shipping", 26/06/2026: https://www.sunsirs.com/uk/detail_news-33948.html
- SunSirs, XNK xút TQ Q1/2026: https://www.sunsirs.com/uk/detail_news-32870.html (ngày chưa kiểm, khoảng T4/2026)
- Argus, "Impact of Middle East conflict/Hormuz on Asia chlor-alkali and vinyls", 13/04/2026: https://www.argusmedia.com/en/news-and-insights/market-opinion-and-analysis-blog/impact-middle-east-conflict-hormuz-asia-chlor-alkali-vinyls
- Argus FER chlor-alkali 14/11/2025 (FOB Đông Bắc Á khoảng 373-375 USD/dmt): https://view.argusmedia.com/rs/584-BUW-606/images/FER-20251114chlor-alkali.pdf?version=0
- SMM, tiêu đề "nhà máy alumina Sơn Đông hạ giá thu mua xút lỏng xuống 580 CNY/t" (31/07/2026), chỉ tóm tắt tìm kiếm.
- AlCircle, "Lam Dong bauxite-aluminium chain expands as alumina output hits 1Mt, ingot production begins", 08/10/2026: https://www.alcircle.com/news/vietnams-lam-dong-bauxite-aluminium-chain-expands-as-alumina-output-hits-1mt-ingot-production-begins-121474
- SMM (tiêu đề), "Vietnam's Lam Dong approves $2.3bn expansion of alumina projects", khoảng T2/2026, trang gốc 404: https://news.metal.com/articolo.php/newscontent/103782300
- Mục tiêu alumina TKV 2026-2045 và đề xuất 800 nghìn t mỗi tổ hợp: tóm tắt tìm kiếm (baolamdong.vn, nongnghiepmoitruong.vn), ngày chưa kiểm.
- VnEconomy, "Tiến độ giải ngân dự án tổ hợp hoá chất 12.000 tỷ đồng tại Nghi Sơn", 09/08/2025: https://vneconomy.vn/tien-do-giai-ngan-du-an-to-hop-hoa-chat-12-000-ty-dong-tai-nghi-son.htm
- Đại biểu Nhân dân, khởi công nhà máy hoá chất Nhơn Trạch (di dời từ Biên Hoà 1), 26/09/2025: https://daibieunhandan.vn/khoi-cong-nha-may-hoa-chat-nhon-trach-buoc-ngoat-phat-trien-cua-hoa-chat-co-ban-mien-nam-10388014.html
- Báo Pháp luật (Doanh nhân), "Lâm Đồng điều chỉnh dự án nhà máy sản xuất xút Bảo Lâm nâng công suất lên 45.000 tấn/năm", 13/07/2026: https://doanhnhan.baophapluat.vn/lam-dong-dieu-chinh-du-an-nha-may-san-xuat-xut-bao-lam-nang-cong-suat-len-45-000-tan-nam.html
- Đại biểu Nhân dân, HĐ cung ứng 138.600 t xút lỏng cho NMLD Nghi Sơn 2026-28, ký 24/02/2026: https://daibieunhandan.vn/vitrichem-va-pvchem-ky-hop-dong-cung-ung-xut-long-cho-nha-may-loc-hoa-dau-nghi-son-10407656.html
- Tạp chí Công Thương, "Giá bán lẻ điện bình quân giảm 2% từ ngày 1/11/2026", 31/10/2026: https://tapchicongthuong.vn/gia-ban-le-dien-binh-quan-giam-2--tu-ngay-1-11-2026-562569.htm
- Tiền Phong, "EVN tăng giá điện từ 2% phải xin ý kiến" (NĐ 278/2026): https://tienphong.vn/evn-tang-gia-dien-tu-2-phai-xin-y-kien-post1858686.tpo
- TT 03/2026/TT-BCT, hạn ngạch thuế quan muối 2026: https://thuvienphapluat.vn/van-ban/EN/Xuat-nhap-khau/Circular-03-2026-TT-BCT-import-tariff-rate-quotas-for-salt-and-poultry-eggs-in-2026/694480/tieng-anh.aspx ; sản lượng/cầu muối: https://vneconomy.vn/nganh-muoi-can-mot-khung-phap-ly-moi-va-linh-hoat-de-phat-trien-ben-vung.htm (ngày chưa kiểm)
- Báo Pháp luật, axit sunfuric +259% (Q3/2026): https://doanhnhan.baophapluat.vn/gia-axit-sunfuric-tang-vot-259-kim-loai-mau-thai-nguyen-vimico-tmg-bao-lai-ky-luc-vuot-muc-tieu-ca-nam.md
- Tạp chí Công Thương, tự cung xút khoảng 50%: https://tapchicongthuong.vn/hashtag/cong-ty-cp-hoa-chat-co-ban-mien-nam-2516.htm (trang tag, ngày bài chưa kiểm)
- NĐ 86/2025/NĐ-CP về phòng vệ thương mại: https://thuvienphapluat.vn/van-ban/Thuong-mai/Nghi-dinh-86-2025-ND-CP-huong-dan-Luat-Quan-ly-ngoai-thuong-bien-phap-phong-ve-thuong-mai-651742.aspx
