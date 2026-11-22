---
name: dd-investor-report
description: Viết và gửi email báo cáo due diligence / định giá một cổ phiếu theo chuẩn nhà đầu tư (kết luận trước, định giá dựng từ dưới lên, biểu đồ, PDF A4). Dùng MỖI KHI user yêu cầu "gửi email" báo cáo DD / định giá / phân tích sâu một mã (vd "DD SCL rồi gửi email cho tôi", "gửi báo cáo đầy đủ về email"). Mẫu chuẩn = báo cáo SCL 29/10/2026 mà user khen "viết rất tốt". KHÔNG dùng cho báo cáo giao dịch daily/weekly/monthly (đó là send_report_email.py + cổng §21).
---

# Báo cáo DD chuẩn nhà đầu tư — LUẬT HIỆN HÀNH (bản B5, 22/11/2026)

Core chỉ chứa luật đang áp. Nguyên văn luật user (L1–L21), lý do, ca minh hoạ, lệnh đủ tham số: `SKILL_ext.md` cùng thư mục
(§X1…§X18; đọc khi cần, không nạp mặc định). Luật quy trình DD + định giá: skill `due-diligence` (core). Đối chiếu cũ→mới:
`mike/agents/Taylor/research/dd_upgrade_20261122/B5_skill_rewrite/LAW_MAP.md`.

## Tiền đề
- Đây là bước ĐÓNG GÓI sau DD (skill `due-diligence` bước 1–9): BCTC gốc → Bobby đọc ngành mù → Taylor DD mù giá + khoá → phản biện (bắt buộc MỌI DD) → áp đính chính → ghi sổ. Báo cáo KHÔNG tạo nghiên cứu mới; số phải khớp REPORT đã phản biện; có đính chính thì dùng bản đã đính chính.
- Mẫu: `exemplar/SCL_DD_investor_report_20261029.md` (+ `.pdf`) — đọc trước, bắt chước giọng/cấu trúc. Mẫu viết TRƯỚC L9–L12: KHÔNG bắt chước nhãn NON/AMBIGUOUS, mục "vùng giá cần kiểm định", câu xung đột lợi ích, tiêu đề trung tính, độ dài 14 trang. Luật core thắng mẫu.

## Cấu trúc (user chốt 29/10)
- TRÌNH BÀY top-down, DỰNG GIÁ TRỊ bottom-up. Trang 1 = tear sheet: tiêu đề-kết luận + dải KPI + vùng giá trị hợp lý + football field/hero + "3 điều cần biết" + "điều gì làm chúng tôi đổi ý" (hai chiều).
- Bottom-up: chất lượng LN → dòng tiền → cân đối → kịch bản LN → bội số; đối chiếu cầu ngành (đọc ngành độc lập) + comp.
- Mỗi mục mở bằng câu tiêu đề-kết luận. Mọi bảng/hình: đơn vị + nguồn + mốc thời gian + CSV; số không đo được gắn "(ước lượng)"; tách SỰ KIỆN / ƯỚC LƯỢNG / NHẬN ĐỊNH.
- Khung mục + 10 biểu đồ chuẩn: §X2.

## Luật nội dung (số L = số luật gốc; nguyên văn §X3–§X12)
- **L1/L11/L12 Khách quan toàn diện** (user 29/10 18:01, 19:20): không QUALIFY/AMBIGUOUS/NON, không "§2.5", "fear-buy", "vùng giá chạy lại kiểm định", "vùng giá nên mua", "đổi nhãn". Kết luận = giá TRÊN/TRONG/DƯỚI vùng giá trị hợp lý (kèm khoảng) + thị trường đang định giá gì + 3 kịch bản có xác suất; không "mua/bán/khuyến nghị" cá nhân hoá. Tích cực/tiêu cực ngang độ dày + chuẩn chứng cứ; giả định bất lợi và thuận lợi cùng hợp lý ⇒ cả hai vào dải, không lấy cận thận trọng làm tâm. Phụ lục F CHỈ là miễn trừ trách nhiệm; KHÔNG câu xung đột lợi ích/hàm ý vị thế. Hồ sơ mua discretionary là nội bộ, không đưa/dẫn chiếu vào báo cáo.
- **L2** Không gán nhân quả cho biến động giá khi không chứng minh được — ghi "quan sát", nêu cơ chế, nói rõ thiếu dữ liệu.
- **L3** Luật/quyết định nội bộ (vd luật quyền mua LAG) KHÔNG đưa vào; trước khi nhắc "luật" nào tra `data/lag_dd/ack.json`, `kb/current_ops.md`.
- **L4** KHÔNG lộ: số lượng vị thế, giá vốn, %NAV, tỷ suất per-position, tên tài khoản (SpaceX/ZaloPay), tên agent nội bộ (gọi "nhóm nghiên cứu", "người đọc ngành độc lập", "người phản biện").
- **L5** Giá hiện tại: DNSE latest_trade (không BQ), ghi giờ; neo định giá vào đóng cửa phiên trước, nói kết luận có đổi ở cả hai mức không.
- **L6** So cùng cơ sở (DT thuần với DT thuần; EPS kỳ trước điều chỉnh hồi tố cổ tức cổ phiếu); đối chiếu BQ↔BCTC; sàn niêm yết lấy từ DNSE secdef (`marketId`).
- **L7** Mô tả kịch bản đúng như phép tính.
- **L8** Giới hạn dữ liệu viết thẳng; thiếu ⇒ bỏ ý + ghi Giới hạn, không bịa. Pháp lý: chỉ WARNING có bằng chứng + phạm vi tra cứu.
- **L9 Tiêu đề = một câu tóm ý chính** (user 29/10): `# <MÃ> — <Tên CTCP>: <vế điều đúng/đáng chú ý nhất>, nhưng <vế giá/rủi ro chưa trả đủ>`; subject email cùng tinh thần. Mẫu: §X4.
- **L10 Hình + kiểu báo cáo thường niên** (user 29/10): ảnh hero trang 1 dựng từ số đã phản biện (matplotlib/SVG/PIL; không ảnh stock, không số mới); mỗi mục lớn ≥1 hình/sơ đồ/bảng; Mục 3–4 viết như BCTN, chỉ thông tin có nguồn.
- **L13 Font + logo** (user 29/10 20:12): Be Vietnam Pro (`fonts/`) cho tiêu đề/phụ đề/PDF/biểu đồ, KHÔNG Georgia/serif; văn bản NFC; HTML thân dùng stack `'Segoe UI','Helvetica Neue',Arial,Tahoma,sans-serif`, tiêu đề là ảnh banner. Logo từ website chính thức (`<dir>/src/logo.png`), không có ⇒ huy hiệu chữ mã; không bịa logo; nguồn logo vào Phụ lục C. Banner `scripts/make_title_banner.py` đặt đầu trang 1 + `--banner` khi gửi. Lệnh: §X5.
- **L14/L17/L21 Chi phí vốn trong báo cáo**: r = 13,5% tại điểm neo lãi huy động 12T (ghi số + ngày), điều chỉnh β=1 khi lãi huy động đổi, độ nhạy ±50/±100bp; báo thêm hai đầu dải Ke nội địa 12,3–13,4% (D4 22/11); THỨ TỰ: 13,5% (neo + β×Δ lãi huy động) là r DÙNG CHO TÂM, dải 12,3–13,4% + 3 mốc đọc là phần BÁO KÈM, "không chốt một điểm" = không CHỈ báo một điểm (user 29/10 20:50; D4); nêu rf chuẩn hoá ~6,75% (dải 6,0–7,5%), ERP đo so với rf nào, β Blume ~1,1; Ke > ~15% cho mọi mã = dấu hiệu lệch; KHÔNG lấy lãi huy động làm rf; Damodaran 15,8% chỉ ghi "góc nhìn nước ngoài, USD"; hình/bảng độ nhạy theo Ke + tỉ trọng terminal. Giá trị TRƯỚC/SAU chiết khấu thanh khoản + cơ sở; nhãn theo giá trị sau chiết khấu. Thêm 2 dòng r\* thị trường + TPCP 10Y từ `dcf_rate_display.dcf_rate_lines('<asof>')` (user 02/11 10:46; không tự tính; "không có dữ liệu" giữ nguyên chữ; TPCP ghi "nguồn chưa đối chiếu độc lập"; DISPLAY-ONLY, không đổi giá trị hợp lý). Lời thường, không nhãn nội bộ. Khung đủ: due-diligence V1–V3; lệnh + hạn cache r\*: §X9.
- **L15 Bản đồ + ảnh sản phẩm** (user 31/10): Mục 3–4 BẮT BUỘC ≥1 bản đồ định vị KHU VỰC (cơ sở + thị trường chính; `scripts/make_map.py` bằng `/home/trido/thanhdt/wc_venv/bin/python -I`; toạ độ có nguồn, ghi "vị trí gần đúng"; KHÔNG bản đồ/inset toàn quốc) và ≥1 khung 2–4 ảnh sản phẩm/hoạt động do CÔNG TY công bố (trích từ BCTN/website, ghi nguồn), không có ⇒ sơ đồ tự vẽ ghi "minh họa". Chi tiết: §X7.
- **L16 Ít chữ, nhiều hình/bảng** (user 31/10): thân ≤ ~10–12 trang A4, phụ lục ≤2–3 trang; mỗi mục = 1 câu kết luận + 1 hình/bảng + ≤3 gạch ≤25 từ; cấm đoạn >3 câu; kịch bản/rủi ro/xúc tác/so sánh ngành = BẢNG; bảng thân ≤10 hàng; mục tiêu ≤ ~1.800 từ thân; trang >60% chữ là chưa đạt. Không đánh đổi L1/L4/L11/L12 + nguồn/giới hạn lấy ngắn.
- **L18 Bản gửi ra ngoài không nhắc lỗi đã sửa** (user 02/11 18:20): cấm "BẢN ĐÍNH CHÍNH", "thay bản", "kết luận đổi từ…", "trước đây", "đã sửa", bảng số cũ→mới, "[ĐÍNH CHÍNH]", "bản rN", số vòng phản biện. Phân biệt bản chỉ bằng ngày dữ liệu. Phụ lục E chỉ mô tả quy trình trung tính. Mọi giả định định giá (P/E, tỷ suất cổ tức yêu cầu, chiết khấu thiểu số, xác suất kịch bản) dẫn peer/nguồn, chưa có ⇒ "giả định" + độ nhạy. Grep kiểm: §X10.
- **L19 Định giá mù giá + tầm nhìn** (user 02/11 21:35): người dựng DCF/SOTP/P-E không thấy giá/vốn hoá/P-E của mã trước khi khoá md5; cấm khung "hoà vốn so với giá hiện tại"; peer multiple chỉ đối chiếu. Giá điện/hợp đồng suy từ kinh tế + quy định (Luật Điện lực 61/2024 Đ.52; TT 12/2025: IRR ≤12% toàn đời; khung giá, tiền lệ, chi phí + lợi nhuận tối thiểu, văn bản gốc). Vụ án chưa thấy trong KQKD ⇒ chỉ WARNING + độ nhạy riêng, không vào base; thận trọng quá mức là sai lệch. Dựng mảng chủ lực từ gốc + mục "Điều thị trường có thể chưa tính" cân bằng hai chiều. Chi tiết: §X11.
- **L20 Dự án mới** (user 03/11 17:06): base NPV = 0 ở giá sổ sách; tiêu đề/kết luận không xây trên "đầu tư mới ⇒ giá trị giảm". Capex tuân thủ (bắt buộc, không tạo doanh thu) = dòng tiền ra (D3 22/11). Khung đủ: due-diligence V4.

## Quy trình thực thi
1. Xác nhận đã có REPORT DD + sector read + số đã kiểm + phản biện đã áp (chưa có ⇒ chạy skill `due-diligence`, báo user).
2. Dựng báo cáo (Taylor; dispatch `--bg --wakeup-ack --model opus --effort medium --timeout 5400 --thread $DISCORD_THREAD_ID`, prompt viết file rồi `"$(cat f)"`). Brief = khung trên + L1–L21 (nhấn L9, L10, L11, L12, L15; dặn không bắt chước nhãn mẫu SCL) + đường dẫn REPORT/đính chính/sector read/src. Khuôn `templates/build_report_SCL_example.py`. Sản phẩm `<dir>/investor_report/{<MÃ>_DD_investor_report_<yyyymmdd>.md,.pdf,.html,figs/,build_report.py,SELFCHECK.md}`; PDF bằng `pymupdf.Story` (`/tmp/pdflib`, python `-I` + `sys.path.insert`). Chi tiết: §X12.
3. Chờ Taylor (~15–20 phút; ScheduleWakeup CHỈ khi đang có job nền này).
4. **Mike kiểm trước khi trình**: đọc cả .md; 2 grep tên nội bộ + nhãn fear-buy phải rỗng (§X12); có ≥1 bản đồ + ≥1 khung ảnh sản phẩm có nguồn; HTML mọi `<img` có alt đóng đúng; render trang 1, trang định giá, 1 trang hình ra PNG xem bằng mắt; số khớp REPORT đã phản biện và rev mới nhất của sổ; đính chính không tái xuất hiện.
5. **Dry-run**: `python3 -I ~/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py <md> --pdf <pdf> --banner <title_banner.png> [--subject "..."] --dry-run --html-out f.html`. Lint email (A6) chạy trong script: dry-run chặn khi có vi phạm; gửi thật hiện chỉ IN cảnh báo (`DD_LINT_BLOCK = False`, Mike bật sau khi có số báo giả).
6. **DỪNG — trình user** theo due-diligence bước 11 (PDF lên Discord qua `.ccdb-attachments-<thread>`, nói "chưa gửi email", TRỪ khi rơi vào ngoại lệ "DD <mã> rồi gửi email" của due-diligence bước 10 ⇒ báo đã gửi + địa chỉ + hash PDF).

## Gửi email (user chốt 03/11 15:23, thay luật "email tự động" 01/11)
- Chỉ gửi khi user báo "gửi email". User đã nói "DD X rồi gửi email" trong cùng yêu cầu = lệnh gửi (một lần, sau skeptic).
- Sửa theo phản hồi user chỉ vào bản nháp; KHÔNG gửi bản trung gian. Khi user báo: kiểm lại grep L18 + bước 4, gửi ĐÚNG MỘT LẦN bản chốt (lệnh bước 5 bỏ `--dry-run`), không hỏi lại.
- Chỉ tới `to_email` trong secrets (địa chỉ user). Báo user: đã gửi tới đâu, file ở đâu, mã hash PDF; việc chuyển tiếp cho bên thứ ba là quyết định của user (tài liệu thông tin, không phải tư vấn cá nhân hoá; có thể chạm luật khuyến nghị đầu tư chứng khoán, user tự đánh giá).
- Ghi sổ giá KHÔNG chờ bước này (due-diligence bước 9).

## Bẫy kỹ thuật (chi tiết §X13)
- Nháy kép thẳng trong tiêu đề làm vỡ alt `<img>` (đã vá html.escape; vẫn dùng “ ” hoặc nháy đơn) ⇒ luôn `--html-out` kiểm.
- matplotlib chỉ có ở `/home/trido/thanhdt/wc_venv/bin/python`; `make_title_banner.py` chạy python3 thường (không `-I`, cần PIL).
- `send_report_email.py` là của báo cáo DAILY + cổng §21 ⇒ DD dùng script của skill; báo cáo CÓ tỷ suất per-position thì phải qua cổng §21.
- Site chặn curl (403): lấy link bằng WebFetch; Drive: `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`; KHÔNG giả header lách chặn bot.
- Story vẽ lặp nền hàng khi bảng tách trang ⇒ giữ bảng gọn trong một trang.
