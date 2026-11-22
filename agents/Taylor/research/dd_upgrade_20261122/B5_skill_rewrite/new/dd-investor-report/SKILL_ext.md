# dd-investor-report — SKILL_ext (nguyên văn luật, lý do, ca, lệnh đủ) — bản B5 22/11/2026

Đọc khi core `SKILL.md` trỏ tới §X…; KHÔNG nạp mặc định. Khối nguyên văn chép NGUYÊN VĂN từ
`~/.claude/skills/dd-investor-report/SKILL.md` (37.242 byte, mtime 22/11 19:48, trước B5; số đầu dòng = số dòng file cũ đã
bị lược). Chỗ đã bị luật sau thay đánh dấu ⟨ĐÃ THAY …⟩/⟨B5: …⟩. Ext khác core ⇒ CORE thắng.

## §X1 Chuẩn bắt buộc + mẫu SCL — nguyên văn
#### (tiêu đề cũ) Báo cáo DD chuẩn nhà đầu tư — mẫu SCL 29/10/2026
#### (tiêu đề cũ) CHUẨN BẮT BUỘC cho MỌI báo cáo mới (tóm tắt luật 9–12 + 15, user chốt 2026-10-29/31 — đọc trước, nếu mẫu SCL mâu thuẫn thì CHUẨN NÀY THẮNG)
1. Tiêu đề = câu tóm ý chính nổi bật (luật 9), subject email cùng tinh thần.
2. Ảnh hero trang 1 + nhiều hình thay chữ + mục Ngành/Doanh nghiệp viết kiểu báo cáo thường niên (luật 10) + BẢN ĐỒ vị trí mỏ/cơ sở/thị trường chính và ẢNH SẢN PHẨM chủ lực (luật 15, user chốt 2026-10-31 sau báo cáo NNC).
3. Phụ lục F CHỈ là tuyên bố miễn trừ trách nhiệm, không câu xung đột lợi ích, góc nhìn trung dung (luật 11).
4. KHÁCH QUAN TOÀN DIỆN: không nhãn QUALIFY/AMBIGUOUS/NON, không ngôn ngữ fear-buy/§2.5/"vùng giá chạy lại kiểm định"; kết luận =
   giá TRÊN/TRONG/DƯỚI vùng giá trị hợp lý + 3 kịch bản có xác suất; cân bằng tích cực/tiêu cực; "đổi ý" hai chiều (luật 1 + 12).
5. FONT + LOGO (luật 13): chữ tiêu đề/phụ đề/PDF/biểu đồ dùng **Be Vietnam Pro** (`fonts/`), KHÔNG Georgia/serif mặc định; banner
   tiêu đề có logo doanh nghiệp (`scripts/make_title_banner.py`), email gửi kèm `--banner`.
6. ÍT CHỮ, NHIỀU HÌNH/BẢNG (luật 16, user chốt 2026-10-31): thân ≤ ~10–12 trang, mỗi mục 1 câu kết luận + 1 hình/bảng + ≤3 gạch ≤25 từ; kịch bản/rủi ro dạng bảng.
⚠️ Mẫu SCL (`exemplar/`) viết TRƯỚC các luật 9–12: bắt chước giọng văn/độ dày/cấu trúc, KHÔNG bắt chước nhãn NON/AMBIGUOUS,
mục "vùng giá cần kiểm định", câu xung đột lợi ích, tiêu đề trung tính.

Mẫu: `exemplar/SCL_DD_investor_report_20261029.md` (+ `.pdf`, 14 trang). User chốt 2026-10-29: "Bản báo cáo viết rất
tốt… khi tôi nói gửi email đều dùng mẫu này". Đọc mẫu TRƯỚC khi viết — bắt chước giọng, độ dày, cách đặt tiêu đề.

## §X2 Tiền đề, cấu trúc, khung mục, 10 biểu đồ chuẩn — nguyên văn
#### (tiêu đề cũ) Tiền đề (đừng bỏ qua)
Báo cáo này là bước ĐÓNG GÓI sau quy trình DD của team (skill `due-diligence`): BCTC gốc → Bobby đọc ngành MÙ →
Taylor DD → kiểm số liệu/nguồn → mới viết báo cáo nhà đầu tư (fundamental-skeptic BẮT BUỘC mọi DD — mục "MỌI DD" bên dưới; chỉ HỒ SƠ discretionary §2.5 tách riêng theo luật 12). Số liệu/nguồn phải đã được kiểm TRƯỚC khi viết báo cáo. Báo cáo
nhà đầu tư KHÔNG tạo nghiên cứu mới; nó trình bày kết luận đã được phản biện. Nếu đã có đính chính của người phản biện, dùng bản
đã đính chính (ca SCL: REPORT.md §13 thắng §1/§6).

#### (tiêu đề cũ) Nguyên tắc cấu trúc (user hỏi top-down hay bottom-up — đã chốt)
**TRÌNH BÀY top-down, DỰNG GIÁ TRỊ bottom-up.**
- Người đọc bận: trang 1 đủ để quyết định. Câu trả lời ở đỉnh (Pyramid Principle/SCQA kiểu McKinsey), 3 luận điểm
  MECE bên dưới, mỗi luận điểm có dữ liệu. Trang 1 kiểu Goldman Sachs: nhãn xếp hạng + giá hợp lý + dải + khung dữ liệu
  chính + "điều gì làm chúng tôi đổi ý" + 1 football field.
- Giá trị dựng từ dưới lên: chất lượng lợi nhuận → dòng tiền → bảng cân đối → kịch bản LN năm tới → bội số; rồi đối
  chiếu top-down bằng cầu ngành (Bobby) và comp.
- Mỗi mục mở bằng **câu tiêu đề-kết luận** ("Biên gộp 41% là hoạt động lõi, không phải khoản một lần"), KHÔNG tiêu đề
  trung tính ("Phân tích biên gộp"). Mọi bảng/hình: đơn vị + nguồn + mốc thời gian; số không đo được gắn "(ước lượng)";
  tách SỰ KIỆN / ƯỚC LƯỢNG / NHẬN ĐỊNH.

#### (tiêu đề cũ) Khung mục (≈10–12 trang A4 thân từ 2026-10-31, luật 16; mẫu SCL cũ 14–18 trang QUÁ DÀI)
Investment Summary (tear sheet) · 1 Tóm tắt điều hành SCQA · 2 Luận điểm + "thị trường đang định giá gì" (định giá
ngược) · 3 Ngành (top-down, từ file Bobby) · 4 Doanh nghiệp (sản phẩm, khách hàng, công suất) · 5 Tài chính bottom-up
(5a tăng trưởng/chất lượng LN, 5b phải thu, 5c dòng tiền, 5d đòn bẩy) · 6 Sự kiện vốn/corporate action nếu có (SCL: quyền
mua — TERP, giá trị quyền, pro-forma) · 7 Định giá (3 kịch bản có trọng số, comp, football field, P/E chuẩn hoá) · 8 Rủi ro
pre-mortem (bảng xác suất × tác động × dấu hiệu sớm × ngày kiểm) · 9 Pháp lý & quản trị (WARNING, không chặn) ·
10 Lịch xúc tác & ngưỡng quyết định · Phụ lục A số BCTC · B đối chiếu BQ↔BCTC · C nguồn · D phương pháp & GIỚI HẠN ·
E quy trình độc lập (nêu minh bạch cái skeptic đã sửa) · F tuyên bố miễn trừ trách nhiệm (CHỈ miễn trừ — không có câu xung đột lợi ích, luật 11).
Biểu đồ chuẩn (10): DT & biên gộp theo quý · LNST quý · phải thu & KH lớn · CFO vs LNST vs capex · nợ/tiền/nợ ròng ·
số cổ phiếu · TERP/waterfall (nếu có quyền mua) · giá 12T + sự kiện · football field · ma trận rủi ro. Mỗi hình kèm CSV.

## §X3 Luật nội dung 1–8 — nguyên văn
#### (tiêu đề cũ) Luật nội dung (bài học SCL — vi phạm là sai thật)
1. **KHÔNG nhãn/ngôn ngữ fear-buy trong báo cáo nhà đầu tư (user chốt 2026-10-29 19:20 — xem luật 12).** Không dùng
   QUALIFY/AMBIGUOUS/NON, không viết "§2.5", "không phải case fear-buy", "vùng giá cần chạy lại kiểm định", "NON chắc hơn".
   Kết luận định giá bằng ngôn ngữ trung tính: giá hiện tại nằm TRÊN / TRONG / DƯỚI vùng giá trị hợp lý (kèm khoảng tin),
   thị trường đang định giá điều gì, và ba kịch bản (tích cực/cơ sở/tiêu cực) có xác suất — KHÔNG "mua/bán/khuyến nghị" cá nhân hoá.
2. **Không gán nhân quả cho biến động giá** khi không chứng minh được (ca −6,6%: giá cum-quyền không mất giá trị cơ
   học vì công bố điều khoản). Ghi "quan sát", nêu cơ chế, nói rõ không đủ dữ liệu.
3. **Luật user/quyết định nội bộ** (vd luật quyền mua LAG) KHÔNG đưa vào báo cáo nhà đầu tư và đừng mô tả sai: tra
   `data/lag_dd/ack.json`, `kb/current_ops.md` trước khi nhắc bất kỳ "luật" nào.
4. **KHÔNG lộ**: số lượng vị thế, giá vốn, %NAV, tỷ suất per-position, tên tài khoản (SpaceX/ZaloPay), tên agent nội bộ
   (Taylor/Bobby/Mike…; gọi "nhóm nghiên cứu", "người đọc ngành độc lập", "người phản biện"). KHÔNG có câu xung đột
   lợi ích nào (user chốt 2026-10-29 18:01: "câu đó bỏ đi, chỉ viết phần miễn trừ trách nhiệm") — xem luật 11.
5. **Giá hiện tại**: lấy DNSE latest_trade (quy tắc same-day, KHÔNG BQ), ghi giờ; neo định giá vào đóng cửa phiên trước
   và nói kết luận có đổi hay không ở cả hai mức.
6. So sánh cùng cơ sở (DT thuần với DT thuần; EPS kỳ trước phải điều chỉnh hồi tố cổ tức cổ phiếu). Đối chiếu số BQ với
   BCTC (BQ thường là TTM/DT gộp — xem bẫy trong skill due-diligence). Sàn niêm yết: lấy từ DNSE secdef (`marketId`), đừng suy.
7. Mô tả kịch bản đúng như phép tính (ca SCL: base 135 tỷ = ước LNST 2026 giữ nguyên, không phải "Q3×4 chuẩn hoá").
8. Giới hạn dữ liệu viết thẳng (không có cơ cấu mảng/backlog/tuổi nợ/cáo bạch/giao dịch nội bộ…). Thiếu dữ liệu ⇒ bỏ ý
   đó và ghi Giới hạn, KHÔNG bịa. Pháp lý: chỉ WARNING có bằng chứng + nêu phạm vi tra cứu.

## §X4 Luật 9–12 (tiêu đề, hình, Phụ lục F, khách quan) — nguyên văn
9. **Tiêu đề báo cáo = một câu tóm ý chính, nổi bật (user chốt 2026-10-29, khen tiêu đề DRI).** Dạng
   `# <MÃ> — <Tên CTCP>: <vế 1 = điều đúng/đáng chú ý nhất>, nhưng <vế 2 = điều giá/rủi ro chưa trả đủ>`. Tiêu đề
   phải tự nói được luận điểm + nhãn hướng đi, người chỉ đọc dòng này vẫn hiểu. KHÔNG đặt tiêu đề trung tính
   ("Báo cáo Due Diligence DRI"). Mẫu: SCL "doanh nghiệp tốt lên thật, nhưng giá đã trả trước kịch bản cơ sở";
   DRI "lợi nhuận đỉnh chu kỳ, nhưng vườn cây đang già và giá đã trả cho một tương lai không tái canh". Tiêu đề email
   (`--subject`) cũng theo tinh thần đó: nêu ý chính, không chỉ "Báo cáo DD <MÃ>".

10. **Hình minh họa + phần giới thiệu kiểu báo cáo thường niên (user chốt 2026-10-29).** Giảm chữ, tăng hình:
   - **Ảnh hero trang 1** (ngay dưới tiêu đề): MỘT ảnh minh họa chuyên nghiệp, sáng tạo, thể hiện NGÀNH NGHỀ + TIỀM NĂNG
     TĂNG TRƯỞNG + MỨC ĐỊNH GIÁ của công ty (vd infographic/băng hình: bức tranh ngành, đường tăng trưởng, thanh
     định giá so với giá trị hợp lý). Dựng bằng matplotlib/SVG/PIL từ số đã phản biện — không ảnh stock bịa, không số mới.
   - **Mỗi mục lớn kèm ≥1 hình/sơ đồ/bảng trực quan** thay đoạn chữ dài: chuỗi giá trị/quy trình sản xuất, bản đồ địa
     bàn/cơ sở, cơ cấu doanh thu–sản phẩm, vòng đời ngành, icon-KPI. Ưu tiên "một hình + 2-3 dòng chú thích" hơn 1 đoạn
     phân tích. Mọi hình có nguồn + mốc thời gian + CSV.
   - **Mục 3-4 (Ngành, Doanh nghiệp) viết như báo cáo thường niên:** mở bằng câu chuyện/sứ mệnh doanh nghiệp, lịch sử
     hình thành ngắn (mốc năm), sản phẩm/dịch vụ chính, cơ sở/công suất/địa bàn, khách hàng–thị trường, vị thế trong ngành,
     định hướng chiến lược do công ty công bố — giọng văn rõ, tự nhiên, người ngoài ngành đọc hiểu; số liệu đặt trong
     khung KPI/biểu đồ chứ không dồn thành đoạn. Chỉ dùng thông tin có nguồn (BCTN, website, CBTT); thiếu ⇒ ghi Giới hạn.

11. **Phụ lục F chỉ là tuyên bố MIỄN TRỪ TRÁCH NHIỆM; góc nhìn phân tích TRUNG DUNG (user chốt 2026-10-29 18:01).** Bỏ hẳn
   câu "tác giả và/hoặc tài khoản liên quan có thể đang nắm giữ cổ phiếu X" và mọi hàm ý vị thế/lợi ích của tác giả. Văn phong
   của cả báo cáo là người quan sát độc lập: nêu cả luận điểm tích cực lẫn tiêu cực cân bằng, không nói "chúng tôi đang giữ/
   muốn mua/bán", không viết như người có lợi ích trong cổ phiếu; KHÔNG dùng nhãn QUALIFY/AMBIGUOUS/NON (luật 1, 12).

12. **Báo cáo nhà đầu tư = góc nhìn KHÁCH QUAN TOÀN DIỆN, không phục vụ chiến lược nào (user chốt 2026-10-29 19:20).**
   Chiến lược mua-khi-thị-trường-sợ-hãi (fear-buy / discretionary sleeve) là công cụ NỘI BỘ; không được dùng nó để bóp méo
   hoặc kéo nhận định về phía quá thận trọng. Cách viết:
   - Luận điểm tích cực và tiêu cực có độ dày và tiêu chuẩn chứng cứ NGANG NHAU; nói rõ điều tốt của doanh nghiệp (chất lượng
     lợi nhuận, bảng cân đối, vị thế, tăng trưởng) với cùng sự nghiêm túc như điều rủi ro. Không mặc định "giá cao ⇒ xấu".
   - Giả định định giá phải trung lập: khi một giả định bất lợi và một giả định thuận lợi cùng hợp lý thì cho CẢ HAI vào dải,
     không chọn cận thận trọng làm tâm; nêu rõ phần nào là ước lượng/post-hoc và chiều lệch có thể có.
   - Không có "vùng giá nên mua", "ngưỡng chạy lại kiểm định", điều kiện "đổi nhãn". Phần "điều làm chúng tôi đổi ý" phải
     cân bằng hai chiều (điều gì làm nhận định tích cực hơn / tiêu cực hơn).
   - Việc xét mua theo discretionary sleeve (khung §2.5, cổng mua, trigger, phản biện fundamental-skeptic) là HỒ SƠ RIÊNG, nội bộ:
     chỉ làm khi USER quyết định cân nhắc mua; không đưa vào, không dẫn chiếu trong báo cáo gửi nhà đầu tư.
   - Phản biện: dùng để kiểm số liệu/nguồn gốc (bắt buộc), nhưng fundamental-skeptic KHÔNG còn là cổng chặn báo cáo trung dung; ⟨ĐÃ THAY 01/11 11:08 (F22-a): skeptic BẮT BUỘC mọi DD và REFUTED văn bản phải sửa trước đóng gói; câu này và câu kế tiếp KHÔNG còn hiệu lực — §X17-a⟩
     nó dành cho quyết định mua discretionary. Skill `due-diligence` bước 5 cập nhật tương ứng.

## §X5 Luật 13 (font, logo, banner; nguyên nhân Georgia) — nguyên văn
13. **Font tiếng Việt chuẩn + logo doanh nghiệp (user chốt 2026-10-29 20:12, sau khi thấy tiêu đề email bị vỡ dấu).**
   Nguyên nhân gốc: `bin/render_report_html.py` đặt tiêu đề bằng Georgia + kicker "ARIA · Báo cáo hiệu suất & vận hành" — Georgia
   thiếu glyph tổ hợp tiếng Việt (ấ, ề, ố…) nên dấu chạy lung tung; header ARIA/disclaimer "nội bộ" lại là của báo cáo vận hành,
   không hợp báo cáo DD nhà đầu tư. Cách làm bắt buộc:
   - **Font:** Be Vietnam Pro (OFL, thiết kế cho tiếng Việt) ở `~/.claude/skills/dd-investor-report/fonts/` cho tiêu đề, phụ đề,
     thân PDF (pymupdf Story) và biểu đồ matplotlib. Văn bản luôn NFC-normalize. HTML email: không phụ thuộc font web — tiêu đề là
     ẢNH banner, thân dùng stack `'Segoe UI','Helvetica Neue',Arial,Tahoma,sans-serif` (đủ glyph Việt). KHÔNG dùng Georgia/serif cho tiêu đề.
   - **Logo:** lấy từ website chính thức của công ty (thẻ `<img … logo>` / `images/icons/…`; ví dụ DRI: `https://dri.com.vn/images/icons/dri_icon.png`),
     lưu `<dir>/src/logo.png`. Không tìm được ⇒ huy hiệu chữ bằng mã cổ phiếu (script tự làm) — KHÔNG vẽ/bịa logo, không dùng logo từ nguồn lạ.
     Ghi nguồn logo trong Phụ lục C. Logo chỉ để nhận diện doanh nghiệp, không ngụ ý công ty tài trợ/bảo chứng báo cáo.
   - **Banner:** `python3 ~/.claude/skills/dd-investor-report/scripts/make_title_banner.py --title "<tiêu đề md dòng 1 bỏ '# '>" --ticker <MÃ>
     --kicker "Báo cáo due diligence · <SÀN>: <MÃ>" --sub "Nhóm nghiên cứu · <ngày>" --logo <logo.png> --out <dir>/figs/title_banner.png`
     (dùng python3 thường, không `-I`, vì cần PIL). Đặt banner ở ĐẦU trang 1 PDF (full width, trên ảnh hero) và truyền `--banner` khi gửi email
     (script gửi tự bỏ header ARIA + disclaimer vận hành + h1 trùng).

## §X6 Luật 14 (chi phí vốn trong báo cáo) — nguyên văn
14. **Chi phí vốn / tỷ lệ chiết khấu trong báo cáo (user duyệt 2026-10-29 20:50).** Với DCF vô hạn: nêu rf chuẩn hoá (lạm phát mục tiêu + lãi thực dài hạn, ~6,75%), ERP kèm cơ sở đo (so với rf nào), β, và báo Ke theo VÙNG + 3 mốc đọc, không một điểm; KHÔNG lấy lãi huy động 12M làm rf. ERP theo nhà đầu tư NỘI ĐỊA (không cộng rủi ro quốc gia Damodaran — user 2026-10-30); Ke nội địa β1,1 báo khoảng 12,3–13,4% (dải 10,5–14,0%, không một điểm), Damodaran 15,8% chỉ là đầu trên ghi nhãn "góc nhìn nước ngoài, USD"; Ke > ~15% cho mọi mã là dấu hiệu lệch. Hiển thị độ nhạy giá trị theo Ke (và tỉ trọng terminal) bằng hình/bảng gọn. Chi tiết khung: skill `due-diligence` mục Định giá.
⟨B5: bổ sung bởi L17 [ĐỔI 03/11 22:27], L21 và D4 22/11 (báo thêm hai đầu dải 12,3–13,4%)⟩

## §X7 Luật 15 (bản đồ + ảnh sản phẩm) — nguyên văn
15. **Bản đồ + hình sản phẩm — làm báo cáo "hình dung được" (user chốt 2026-10-31, sau khi đọc báo cáo NNC: "viết ổn rồi; thêm hình minh họa như vị trí mỏ,
   thị trường kinh doanh chính dưới dạng bản đồ, các sản phẩm chủ lực có hình minh họa thì hấp dẫn hơn nữa").** Mục 3–4 (Ngành, Doanh nghiệp) BẮT BUỘC có:
   - **(a) Bản đồ định vị** (ít nhất 1): vị trí mỏ / nhà máy / trụ sở / cơ sở chính + **thị trường tiêu thụ chính** (tỉnh/thành, cụm đô thị) + dự án hạ tầng
     là cầu chính (nếu có). Công cụ: `scripts/make_map.py` (matplotlib thuần, ranh giới tỉnh geoBoundaries VNM-ADM1 cache ở `data/`, font Be Vietnam Pro) —
     chạy bằng `/home/trido/thanhdt/wc_venv/bin/python -I` (python3 hệ thống KHÔNG có matplotlib khi `-I`). Đầu vào: CSV `name,lat,lon,kind[,dx,dy]`, `--bbox`, `--highlight`.
     · **Toạ độ phải có NGUỒN**: lấy tên xã/huyện/khu vực từ BCTN/BCTC/website công ty rồi tra toạ độ trung tâm (Wikipedia/OSM); ghi "vị trí gần đúng theo xã/huyện,
       không phải ranh giấy phép" trong `--source`, nguồn toạ độ vào Phụ lục C. Không rõ vị trí ⇒ không vẽ điểm đó, ghi Giới hạn.
     · **CHỈ bản đồ KHU VỰC** (bbox vài tỉnh). KHÔNG vẽ bản đồ/inset toàn quốc từ dữ liệu này — thiếu quần đảo Hoàng Sa/Trường Sa, nhạy cảm với độc giả Việt Nam.
     · Dữ liệu ranh giới là bản 2008 (tỉnh cũ). Doanh nghiệp/BCTC có thể gọi theo địa danh sau sáp nhập ⇒ nêu cả hai tên trong chú thích ("Bình Phước cũ, nay thuộc Đồng Nai").
     · Doanh nghiệp bán đi nhiều vùng/xuất khẩu: thêm bản đồ cụm thị trường (hoặc sơ đồ dòng chảy) — thiếu dữ liệu tỷ trọng thì chấm điểm KHÔNG theo cỡ, ghi "tỷ trọng: không công bố".
   - **(b) Hình sản phẩm/hoạt động chủ lực** (≥1 khung 2–4 sản phẩm hoặc quy trình): ưu tiên **ảnh CÔNG TY TỰ CÔNG BỐ** (BCTN, website, CBTT) — trích ảnh từ PDF bằng pymupdf
     (`page.get_images(full=True)` → `doc.extract_image(xref)`; lọc ≥300×200 px; ví dụ BCTN NNC 2025 có ảnh mỏ/sản phẩm ở tr.1,4–9,11), cắt gọn, ghi nguồn "Ảnh: BCTN <năm>/website công ty" dưới hình + Phụ lục C;
     chú thích mỗi sản phẩm 1 dòng (công dụng + vị trí trong chuỗi giá trị). KHÔNG dùng ảnh stock/ảnh từ nguồn lạ, KHÔNG bịa ảnh; công ty không có ảnh dùng được ⇒ sơ đồ/icon vector
     tự vẽ (matplotlib) và ghi "minh họa".
   - Ghép hình đẹp: panel 2–4 ảnh cùng chiều cao (PIL), viền mảnh, nhãn Be Vietnam Pro, 1440 px rộng, kèm CSV/ghi chú nguồn như mọi hình khác. Kiểm bằng mắt: nhãn không chồng nhau, địa danh đúng chính tả.
   - Bản đồ + sản phẩm bổ sung (không thay) cho hero và chuỗi giá trị đã có ở luật 10.

## §X8 Luật 16 (ít chữ) — nguyên văn
16. **Ít chữ, nhiều hình/bảng — cùng chuẩn báo cáo tuần v2 (user chốt 2026-10-31).** Báo cáo DD hiện đủ tốt nhưng CÒN DÀI; viết lại theo chuẩn `kb/projects/report-style-v2-20261031.md` (báo cáo ngày/tuần/tháng/quý):
   - **Trần độ dài:** thân ≤ ~10–12 trang A4 (mẫu cũ 14–18 trang là QUÁ DÀI); phụ lục (A–F) gom ≤ 2–3 trang chữ nhỏ/bảng. Mục nào ≥ 1 trang chữ liền ⇒ cắt hoặc đổi sang hình/bảng.
   - **Mỗi mục = 1 câu tiêu đề-kết luận + 1 hình HOẶC bảng + tối đa 3 gạch, mỗi gạch ≤ 25 từ.** CẤM đoạn văn > 3 câu, CẤM giải thích lê thê (lý do, bối cảnh, "như đã nêu ở trên"). Lý giải phương pháp/đối soát/chú thích dài → Phụ lục; trong thân chỉ còn footnote 1 dòng.
   - **Trang 1 = tear sheet:** tiêu đề kết luận (luật 9) + dải KPI (giá, vùng giá trị hợp lý, P/E, ROE, nợ ròng/EBITDA…) + football field/hero + "3 điều cần biết". Kịch bản, rủi ro, xúc tác, so sánh ngành → **BẢNG** (kịch bản: xác suất × điều kiện × giá trị; rủi ro: xác suất × tác động × dấu hiệu sớm × ngày kiểm), không văn xuôi.
   - **Ưu tiên hình/bảng thay chữ:** tăng trưởng/biên/dòng tiền/nợ = biểu đồ có nhãn trực tiếp; so sánh = bảng căn phải, +/− có màu và dấu; bảng thân ≤ 10 hàng (dư → Phụ lục). Mỗi hình có tiêu đề-kết luận, đơn vị, nguồn, CSV.
   - **Mục Ngành/Doanh nghiệp (luật 10/15):** viết kiểu báo cáo thường niên NHƯNG ngắn — 1 sơ đồ chuỗi giá trị + bản đồ + khung ảnh sản phẩm + bảng KPI; câu chữ chỉ làm chú thích. Tự kiểm trước khi gửi: đếm số từ thân (không tính bảng/hình/phụ lục) — mục tiêu ≤ ~1.800 từ; xem PDF bằng mắt, trang nào > 60% chữ là chưa đạt.
   - Không đánh đổi trung thực lấy ngắn: các luật 1, 4, 11, 12 (khách quan, không lộ nội bộ, disclaimer, đổi ý hai chiều) và nguồn/giới hạn dữ liệu vẫn giữ — chỉ nén CÁCH TRÌNH BÀY (bảng/hình/footnote), không bỏ nội dung bắt buộc.

## §X9 Luật 17 (r\*, TPCP 10Y, r gắn lãi huy động) — nguyên văn
17. **Bối cảnh lãi suất trong mục định giá (user duyệt 2026-11-02 10:46).** Mọi báo cáo DD có DCF thêm 2 dòng gọn, lấy bằng
    `cd /home/trido/thanhdt/WorkingClaude && python3 -c "import dcf_rate_display as d; print(*d.dcf_rate_lines('<asof ISO>'), sep=chr(10))"`
    (không tự tính lại): (i) **r\* thị trường** (lãi suất chiết khấu mà giá thị trường đang ngầm định, so với r hằng của mô hình; kèm percentile lịch sử + đỉnh 2022/đáy 2022–23); (ii) **TPCP 10Y** + thay đổi 12 tháng. Chỉ để người đọc thấy thị trường đang chiết khấu nặng hay nhẹ hơn mô hình: DISPLAY-ONLY, KHÔNG nêu như tín hiệu mua/bán, KHÔNG đổi giá trị hợp lý. Dòng nào ra "không có dữ liệu" thì giữ nguyên chữ đó (đừng điền số cũ); TPCP ghi "nguồn chưa đối chiếu độc lập". Bỏ các nhãn nội bộ (DISPLAY-ONLY, UNVERIFIED…) khỏi bản gửi nhà đầu tư, diễn đạt bằng lời thường. [ĐỔI 03/11 22:27 ICT theo user] r báo cáo DD = 13,5% tại điểm neo (lãi huy động 12T hiệu dụng ghi số+ngày) và ĐƯỢC ĐIỀU CHỈNH khi lãi huy động đổi (β=1, kèm độ nhạy ±50/100bp) — thay cho câu 'r giữ hằng' cũ; engine `dcf_valuation` của fleet vẫn dùng khung riêng. Cache r\* hết hạn 2026-12-14 (xem `kb/cron_registry_dcf_rstar.proposed`).

## §X10 Luật 18 (không nhắc lỗi đã sửa; grep) — nguyên văn
18. **BẢN GỬI RA NGOÀI KHÔNG BAO GIỜ NHẮC LỖI ĐÃ XẢY RA/ĐÃ SỬA (user chốt 2026-11-02 18:20, sau ca TV1 có 4 bản).** Việc nhắc lỗi cũ thể hiện thiếu chuyên nghiệp trong nghiên cứu. Báo cáo nhà đầu tư (md/pdf/html/email, subject, banner) phải đọc như MỘT bản độc lập, tự đứng được:
   - CẤM: nhãn "BẢN ĐÍNH CHÍNH", "thay bản gửi…", "kết luận đổi từ … sang …", "lỗi phương pháp", "trước đây", "đã sửa", bảng "số cũ → số mới", Phụ lục "đính chính từ phản biện", subject có "[ĐÍNH CHÍNH]", "bản r4/r5/r6", số vòng phản biện + nội dung từng vòng. Nếu cần phân biệt bản: chỉ ghi ngày dữ liệu/as-of ("dữ liệu đến 30/10/2026"), không ghi lý do đổi.
   - Lịch sử sửa, vòng phản biện, lỗi đã bắt: CHỈ ở hồ sơ NỘI BỘ (REPORT.md, SKEPTIC*_.md, kb/projects). Phụ lục E của báo cáo NĐT chỉ mô tả quy trình trung tính ("số liệu đối chiếu BCTC gốc; có người phản biện độc lập; giới hạn dữ liệu"), không liệt kê cái đã sửa.
   - Mọi giả định định giá phải có CƠ SỞ DỮ LIỆU nêu được (so sánh ngành/peer, lịch sử thị trường), không tự chọn con số tuỳ ý: bội số P/E, tỷ suất cổ tức yêu cầu, chiết khấu thiểu số, xác suất kịch bản đều phải dẫn bảng peer/nguồn; chưa có cơ sở ⇒ nói "giả định" + độ nhạy, không trình bày như sự thật.
   - Trước khi gửi: grep "đính chính|thay bản|trước đây|đã sửa|vòng [0-9]|r[0-9]\b|sai sót" trong md/html/subject phải rỗng.

## §X11 Luật 19 (mù giá, giá điện, pháp lý, tầm nhìn) — nguyên văn
19. **ĐỊNH GIÁ DCF PHẢI CHẠY MÙ VỚI GIÁ THỊ TRƯỜNG; GIÁ ĐIỆN/HỢP ĐỒNG SUY TỪ KINH TẾ + QUY ĐỊNH; KHÔNG THẬN TRỌNG TRƯỚC BẰNG CHỨNG; PHẢI CÓ TẦM NHÌN (user chốt 2026-11-02 21:35, sau ca TV1 8 vòng).** Bốn điều:
   - **Mù giá:** người dựng DCF/SOTP/P-E KHÔNG được thấy giá thị trường/vốn hoá/P-E hiện tại của chính mã đó trong brief và không truy vấn chúng trước khi khoá. Quy trình: dựng giá trị nội tại từ nền tảng (BCTC, ngành, quy định) → ghi file giá trị + khoá md5 → MỚI so với giá. Cấm khung "hoà vốn so với giá hiện tại", "giá −x% so tâm" dẫn lái giả định (đã gây neo giá ở ca TV1: các vòng sau đều kéo kết quả về ≈ giá). Peer multiple chỉ làm đối chiếu chéo, không phải mỏ neo.
   - **Giá bán điện/hợp đồng suy từ kinh tế và quy định, không từ tin đồn/lời lãnh đạo qua CTCK:** giá thoả thuận phải bảo đảm vận hành an toàn bền vững và lợi nhuận hợp lý (không ai vận hành ở giá chỉ bằng chi phí/hoà vốn). Dựng khoảng giá khả dĩ từ: khung giá/cơ chế quy định (Luật Điện lực 61/2024 Đ.52; TT 12/2025: IRR ≤12% toàn đời), tiền lệ nhà máy cùng loại, chi phí vận hành + sửa chữa + lợi nhuận tối thiểu trên giá trị còn lại/giá trị M&A, lịch sử giá thực hiện, điều kiện hợp đồng thật (đọc văn bản gốc). "Hoà vốn" nghĩa là chi phí hoà vốn của nhà máy, không phải giá làm giá cổ phiếu khớp.
   - **Rủi ro pháp lý/vụ án chưa thấy trong kết quả kinh doanh ⇒ KHÔNG đưa vào kịch bản cơ sở; chỉ WARNING + kịch bản độ nhạy riêng.** Không cắt lợi nhuận/bội số theo suy đoán khi chưa có bằng chứng rõ ràng (luật user 27/09). Thận trọng quá mức là sai lệch ngang với lạc quan quá mức.
   - **Tầm nhìn:** không chỉ làm phần dễ (nhân bội số). Phải dựng mảng chủ lực từ gốc (vd tư vấn thiết kế: đường ống đầu tư của khách hàng chính × tỷ lệ phí tư vấn theo định mức × thị phần × năng lực/biên), nêu rõ vai trò/vị thế đặc thù của doanh nghiệp trong chuỗi giá trị, và một mục "Điều thị trường có thể chưa tính" (có bằng chứng, nêu điều kiện kiểm chứng, cân bằng với điều thị trường có thể đã tính quá tay). Không chỉ trả lời câu hỏi người hỏi; phải tìm điều họ chưa hỏi.

## §X12 Quy trình thực thi cũ — nguyên văn
#### (tiêu đề cũ) Quy trình thực thi
1. Xác nhận đã có REPORT DD + sector read + số liệu/nguồn đã kiểm (nếu chưa → chạy skill `due-diligence` trước, báo user).
2. Dispatch Taylor (`--bg --wakeup-ack --model opus --effort medium --timeout 5400 --thread $DISCORD_THREAD_ID`, prompt viết
   file rồi `"$(cat f)"`) với brief = khung ở trên + CÁC LUẬT 1–15 ⟨B5: nay là L1–L21⟩ (nêu rõ luật 9 tiêu đề, 10 hero/hình/kiểu thường niên, 11 chỉ miễn trừ, 12 khách quan không fear-buy, 15 bản đồ + hình sản phẩm: dặn trích ảnh từ BCTN/website, tra toạ độ có nguồn, chạy make_map.py; dặn Taylor không bắt chước nhãn NON/AMBIGUOUS của mẫu SCL) + đường dẫn REPORT/§đính chính/sector read/src. Dùng
   `templates/build_report_SCL_example.py` làm khuôn dựng biểu đồ + PDF (copy vào thư mục DD mới, sửa `figs()` và header;
   `md_to_html`/`CSS`/`pdf()` dùng lại được). Sản phẩm: `<dir>/investor_report/{<MÃ>_DD_investor_report_<yyyymmdd>.md,.pdf,.html,figs/,build_report.py,SELFCHECK.md}`.
   PDF dựng bằng `pymupdf.Story` (pymupdf ở `/tmp/pdflib`, python `-I` + `sys.path.insert`); không có chrome/weasyprint/reportlab.
3. Poll bằng ScheduleWakeup (claim-reply dòng đầu). ⟨B5: chỉ khi có job nền đang chạy (feedback 05/10 không poll rỗng)⟩ Taylor mất ~15–20 phút.
4. **Mike đọc kiểm trước khi gửi**: (a) đọc cả .md; (b) `grep -n -i -E "SpaceX|ZaloPay|giá vốn|NAV|Taylor|Bobby|Mike|skeptic|Wendy|Spyros"`
   → phải rỗng (trừ "giá vốn" nghĩa COGS); VÀ `grep -n -i -E "QUALIFY|AMBIGUOUS|\bNON\b|§2\.5|fear|sợ hãi|kiểm định|xung đột lợi ích|đang nắm giữ cổ phiếu"`
   → phải rỗng (chuẩn khách quan luật 1/11/12); đọc lại xem kết luận có cân bằng hai chiều, tiêu đề + hero + hình theo luật 9–10; (b2) luật 15: có ≥1 bản đồ định vị (mỏ/cơ sở + thị trường chính, địa danh đúng, nguồn toạ độ) và ≥1 khung ảnh sản phẩm chủ lực có nguồn; (b3) HTML email: mọi `<img` có alt đóng đúng (`--html-out`); (c) render 2–3 trang PDF ra PNG (trang 1, trang định giá, 1 trang hình) rồi `Read`
   xem bằng mắt (dấu tiếng Việt, bảng không tràn); (d) số khớp REPORT đã phản biện; (e) các đính chính đã có (nếu có) không tái xuất hiện.
5. Gửi: `python3 -I ⟨B5: chỉ chạy thật SAU khi user báo 'gửi email' (luật 03/11 15:23); trước đó chỉ `--dry-run`⟩ /home/trido/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py <md> --pdf <pdf> --banner <title_banner.png> [--subject "..."]`
   (thêm `--dry-run` để xem trước người nhận/số ảnh/dung lượng; `--html-out f.html` để kiểm HTML). Thân email = HTML có ảnh nhúng; kèm PDF + .md. Chỉ gửi tới
   `to_email` trong secrets (địa chỉ user) — báo cho user địa chỉ đó. Thêm đường dẫn PDF vào
   `.ccdb-attachments-<thread>` để Discord nhận bản PDF.
6. Báo user: đã gửi tới đâu, file ở đâu, các điểm cần user quyết (việc chuyển tiếp cho bên thứ ba là
   quyết định của user; tài liệu thông tin, không phải tư vấn cá nhân hoá — bên thứ ba nhận tài liệu có thể chạm luật
   khuyến nghị đầu tư chứng khoán, user tự đánh giá).

## §X13 Bẫy kỹ thuật — nguyên văn
#### (tiêu đề cũ) Bẫy kỹ thuật
- **Alt ảnh banner chứa dấu `"`** (tiêu đề kiểu `…"vách" cung–cầu…`) làm vỡ thẻ `<img>` ở email ⇒ banner/ảnh hiển thị lỗi (ca NNC 2026-10-31). Đã vá `send_dd_report_email.py`
  (html.escape alt). Vẫn nên tránh nháy kép thẳng trong tiêu đề; dùng “ ” hoặc nháy đơn. Sau khi dựng HTML: `--dry-run --html-out f.html` rồi kiểm mọi `<img` có alt đóng đúng.
- `make_map.py`/`make_title_banner.py`: matplotlib chỉ có ở `/home/trido/thanhdt/wc_venv/bin/python`; `python3 -I` (hệ thống) không import được matplotlib.
- `send_report_email.py` chỉ đính kèm file phụ cho báo cáo DAILY và chạy cổng tỉ suất §21 ⇒ DD dùng script riêng của skill.
  Nếu báo cáo CÓ tỉ suất per-position thì phải qua cổng §21 (`dividend_adjusted_return.py`) — đừng dùng script của skill.
- `songdacaocuong.vn`-kiểu site chặn curl (403): lấy link bằng WebFetch; tải file Drive qua
  `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`. KHÔNG giả header để lách chặn bot (classifier từ chối).
- Matplotlib: font DejaVu hiển thị tiếng Việt đủ; 200 dpi, nền trắng, 1 màu chủ đạo + 1 màu nhấn.
- Story vẽ lặp nền hàng bảng khi bảng tách qua trang → giữ bảng gọn trong một trang.

## §X14 Cập nhật 2026-11-01 — nguyên văn
#### (tiêu đề cũ) Cập nhật 2026-11-01 (user chốt)
MỌI DD: sau Taylor DD → fundamental-skeptic (bắt buộc) → áp đính chính → báo cáo nhà đầu tư (skill này) → **DỪNG, chờ user nói "gửi email"** (đổi 2026-11-03: không tự gửi; xem mục dưới). Luật 12 vế "skeptic chỉ khi xét mua" đã THAY bằng: skeptic luôn chạy, nhưng chỉ kiểm số liệu/nguồn/cân bằng; hồ sơ mua discretionary vẫn tách riêng.

## §X15 Sổ mức giá DD — nguyên văn (luật hiện hành nay ở core `due-diligence` mục "Sổ mức giá")
#### (tiêu đề cũ) Sổ mức giá DD (user chốt 2026-11-01 22:39 ICT) — BẮT BUỘC cuối mỗi DD
Sau khi báo cáo đã qua skeptic + áp đính chính (trước/cùng lúc gửi email): ⟨B5 §X17-c: thống nhất = ghi sổ ngay sau khi áp đính chính vòng skeptic cuối, không đợi báo cáo NĐT/email; luật sổ nay ở core due-diligence⟩ ghi vùng giá hợp lý vào `mike/kb/dd_price_zones.json` (append-only; bản rev cao nhất của (mã, dd_date) thắng): ticker, dd_date, bctc_quarter, zone_low/center/zone_high (đ/cp), price_ref + price_date, center_kind (ưu tiên GIÁ TRỊ KỲ VỌNG TRỌNG SỐ KỊCH BẢN khi báo cáo có; ghi kịch bản cơ sở ở center_alt), verdict_label, skeptic_status, source_file + trích nguyên văn dòng chứa vùng giá. Số phải khớp nguyên văn nguồn. Sau đó chạy `python3 mike/bin/dd_price_zones_selfcheck.py` (phải 0 lỗi). Mục đích: mỗi tối `bin/dd_price_zone_watch.py` ghi chú mã DD có giá đóng cửa dưới tâm ≥15% vào báo cáo plan (chỉ để user cân nhắc, không phải tín hiệu mua). DD hết hạn khi có BCTC quý mới hơn (hoặc 120 ngày) — khi đó DD lại, đừng dùng vùng giá cũ.
- **Trường sổ BẮT BUỘC từ 2026-11-23 (A2, user duyệt kế hoạch 22/11; `bin/dd_price_zones_selfcheck.py` chặn pre-commit nếu thiếu):** mỗi entry mới phải có `skeptic_final` ∈ {`CONFIRMED` = vòng skeptic CUỐI ghi CONFIRMED và sau đó KHÔNG đính chính số/vùng nào; `FIXED_UNVERIFIED` = đã REFUTED/INCONCLUSIVE (hoặc đính chính sau CONFIRMED), bản sửa đã áp nhưng chưa có vòng nào chạy lại; `REFUTED_OPEN` = REFUTED/INCONCLUSIVE, bản sửa CHƯA áp; `NONE` = chưa qua skeptic}, `audited_fy_missing` (bool: thiếu BCTC năm gần nhất đã kiểm toán), `skeptic_verdict_path` (file verdict thật của vòng cuối hoặc `null` — KHÔNG đoán), `skeptic_final_basis` (`skeptic_run`|`user_confirmed`). `CONFIRMED` mà `skeptic_status` có REFUTED/INCONCLUSIVE/CHƯA thì phải có `skeptic_verdict_path` tới file chứa CONFIRMED, nếu không bị chặn. Có vòng skeptic MỚI trên DD đã ghi sổ ⇒ thêm **rev mới** (+`correction_reason`), KHÔNG sửa tại chỗ nhãn của entry cũ. 17–20 ca backfill mơ hồ: `kb/projects/dd-ledger-ambiguous-queue-20261122.md` (hạn xác nhận 29/11).

## §X16 Email chỉ khi user báo; Luật 20; Luật 21 — nguyên văn
#### (tiêu đề cũ) EMAIL CHỈ GỬI KHI USER BÁO (user chốt 2026-11-03 15:23 ICT — thay luật "email tự động" của 11-01)
Lý do: tránh gửi đi gửi lại nhiều lần (ca TV1 4 bản). Quy trình: dựng PDF/HTML, chạy `send_dd_report_email.py --dry-run --html-out`, kiểm grep luật 18 + bước 4, rồi **KHÔNG gửi thật**. Đăng PDF lên Discord + nói "chưa gửi email". Chỉnh sửa theo phản hồi user ⇒ chỉ sửa bản nháp, không gửi bản trung gian. Khi user báo "gửi email" ⇒ kiểm lại grep, gửi ĐÚNG MỘT LẦN bản chốt, báo địa chỉ + mã hash PDF. Nếu user đã nói "DD X rồi gửi email" trong cùng yêu cầu thì đó là lệnh gửi (một lần, sau skeptic). 

#### (tiêu đề cũ) Luật 20 — Dự án đầu tư mới: base = giá trị sổ sách/NPV 0 (user chốt 2026-11-03 17:06 ICT)
Cấm tuyệt đối báo cáo DD nào để base case giảm giá trị doanh nghiệp chỉ vì doanh nghiệp đầu tư dự án mới. Đứng vai doanh nghiệp: đã đầu tư thì kỳ vọng có lời; không tự nhiên "vứt tiền qua cửa sổ". Base = dự án ở giá vốn/sổ sách (NPV = 0, phần đã chi là tài sản, KHÔNG đồng thời trừ trong nợ ròng và coi là mất); lệch khỏi 0 chỉ khi có cơ sở độc lập cụ thể nêu nguồn (upside: IRR kiểm được; downside: rủi ro quan sát cụ thể, đặt thành kịch bản có xác suất, không đặt vào base). Chi tiết: skill `due-diligence` mục "ĐẦU TƯ DỰ ÁN MỚI". Mọi khoản giảm trừ trong base phải có dòng cơ sở dữ liệu + nguồn. Tiêu đề/kết luận không được xây trên nghịch lý "đầu tư mới ⇒ giá trị công ty giảm".

#### (tiêu đề cũ) Luật 21 — r gắn lãi huy động + rủi ro thanh khoản (user 2026-11-03 22:27 ICT)
Xem skill `due-diligence` mục "CHI PHÍ VỐN GẮN LÃI SUẤT HUY ĐỘNG + RỦI RO THANH KHOẢN". Bản NĐT phải có: r + điểm neo + độ nhạy lãi huy động; giá trị trước/sau chiết khấu thanh khoản kèm cơ sở; nhãn dựa trên giá trị sau chiết khấu thanh khoản; bằng lời thường (không nhãn nội bộ).

## §X17 Mâu thuẫn đã giải trong B5 (đồng bộ với due-diligence §E12)
- **a** Luật 12 gạch cuối "fundamental-skeptic KHÔNG còn là cổng chặn … dành cho quyết định mua discretionary" (29/10) mâu thuẫn :25 + :199 (skeptic bắt buộc MỌI DD, 01/11 11:08) ⇒ xoá khỏi core; giữ ở §X4 có nhãn ⟨ĐÃ THAY⟩.
- **c** Sổ giá "trước/cùng lúc gửi email" vs due-diligence "ngay sau skeptic, không đợi email" ⇒ một câu (core due-diligence bước 9).
- Quy trình cũ bước 5–6 (gửi + báo đã gửi) đứng ngay sau bước kiểm, trong khi luật 03/11 15:23 chỉ gửi khi user báo ⇒ core tách mục "Gửi email" riêng, bước 6 = DỪNG.
- Brief "CÁC LUẬT 1–15" thiếu L16–L21 ⇒ core: L1–L21.
- "Poll bằng ScheduleWakeup" ⇒ core: chỉ khi có job nền (feedback user 05/10 không poll rỗng).
- Không còn mâu thuẫn mở riêng của skill này; các mục mở chung (sizing Q4, `--claim`, watch không đọc `audited_fy_missing`) ở due-diligence §E12-d/f/g.

## §X18 A6 — lint email (hiện trạng 22/11)
`scripts/send_dd_report_email.py`: hằng `DD_LINT_BLOCK = False` — gửi thật chỉ IN cảnh báo; `--dry-run` chặn khi có vi phạm. Commit A6 `ffeae621e` (mike, đã vào master); bản sao lưu file skill `.bak_20261122`. Bật `True` sau khi có số báo giả (Mike).
