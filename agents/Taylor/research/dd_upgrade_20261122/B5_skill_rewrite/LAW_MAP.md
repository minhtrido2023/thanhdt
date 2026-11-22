# B5 — LAW_MAP: mọi luật/ràng buộc/số trong 2 skill cũ → vị trí trong bản mới

Nguồn cũ (ngoài git, KHÔNG sửa): `~/.claude/skills/due-diligence/SKILL.md` (27.856 B, 58 dòng) và
`~/.claude/skills/dd-investor-report/SKILL.md` (37.242 B, 212 dòng). Bản mới: `new/<skill>/SKILL.md` (core) + `SKILL_ext.md`.

**Bảo toàn chữ (kiểm cơ học, 22/11):** MỌI dòng không rỗng của 2 file cũ (trừ frontmatter) có mặt NGUYÊN VĂN trong `SKILL_ext.md`
tương ứng sau khi bỏ các chú thích `⟨…⟩` do B5 chèn — script kiểm: so từng dòng `strip()` với nội dung ext đã xoá `' ⟨[^⟩]*⟩'`;
kết quả 0 dòng thiếu ở cả hai skill. Frontmatter (`name`, `description`) giữ nguyên từng byte trong core.

Ký hiệu vị trí: **C:** core `SKILL.md` (mục) · **E:** ext (§). DD = due-diligence, IR = dd-investor-report. "dòng" = số dòng file cũ.

## A. due-diligence (60 luật)
| # | Luật/ràng buộc/số (dòng cũ) | Vị trí mới |
|---|---|---|
| DD-01 | Chỉ nghiên cứu, không lệnh/wire; mua = user duyệt từng tranche (8) | C: Nguyên tắc chung · E: §E0 |
| DD-02 | Pháp lý ⇒ phân tích bình thường, chỉ WARNING (user 27/09) (8) | C: Nguyên tắc chung · E: §E0 |
| DD-03 | Thứ tự không đảo (10) | C: Thứ tự bước · E: §E1 |
| DD-04 | Claim: lounge + `POST /api/claims resource=topic:dd-<MÃ>-<ngày>`; báo user ngay (11) | C: bước 1 · E: §E1 |
| DD-05 | BCTC gốc từ website; không BQ/báo chí nguồn chính; BQ thường chưa có quý mới (12) | C: bước 2 · E: §E1 |
| DD-06 | Mẹo AJAX `download.js`; pecc2 `cat_id=8/4`; fallback HOSE/HNX/cafef/vietstock (13) | E: §E1 |
| DD-07 | Bộ tài liệu phải lấy đủ (14) | C: bước 2 (rút gọn) · E: §E1 |
| DD-08 | Lưu `src/`; `curl -A "Mozilla/5.0"`; WebFetch không chạy JS (15) | C: bước 2 (đường dẫn) · E: §E1 |
| DD-09 | PDF scan: pymupdf `/tmp/pdflib`, zoom 1.6, chỉ trang cần, `-I` + `sys.path.insert` (16) | E: §E1 |
| DD-10 | Bobby đọc NGÀNH MÙ trước kết luận; cấm mã/giá/BCTC/giả thuyết; nội dung bắt buộc; `sector_read_<ngành>_<ngày>.md` blind: YES; song song bước 2 (17) | C: bước 4 · E: §E2 |
| DD-11 | Snapshot vĩ mô (user 05/11 09:19): lệnh, thư mục TRUNG TÍNH, không ghi `dd_<MÃ>_*`, copy sau, rc=2 nêu thẳng, chỉ đọc `macro_indicator` (18) | C: bước 3 · E: §E2 |
| DD-12 | Đưa Bobby đường dẫn snapshot; cấm thêm gì về mã, chọn chỉ báo theo NGÀNH; dòng nhắc chuẩn (18) | C: bước 4 · E: §E2 |
| DD-13 | Bobby ghi trước, Taylor nhận snapshot sau (18) | C: bước 4, 5 |
| DD-14 | Quy tắc dùng snapshot (a)–(d), bảng ngành→chỉ báo, `vn_bond_10y` chỉ Δ, spread thanh khoản = giả thuyết chưa kiểm (19) | C: V7 · E: §E2 |
| DD-15 | 5F tầng (b) (user 06/11 20:23): Taylor làm sau Bobby, `5F.md`, mục bắt buộc moat_tier/type/rủi ro số 1 + bằng chứng định lượng; `moat_tags.csv` không tự sửa; thiếu số ⇒ "cần kiểm chứng" (20) | C: V5 · E: §E3 |
| DD-16 | Tần suất 5F ≤1 lần/năm/mã (user 06/11 23:28); <12 tháng tái dùng + kiểm nhanh 1–2 dòng; phần khác Taylor quyết (21) | C: V5 + Nguyên tắc chung · E: §E3 |
| DD-17 | Moat bền = 3 điều kiện (22) | C: V5 (trỏ) · E: §E3 |
| DD-18 | Bền ⇒ tham số tường minh (fade N năm, biên bền, tăng trưởng, RONIC>Ke chỉ WIDE, premium có peer) (22) | C: V5 · E: §E3 |
| DD-19 | NARROW/NONE: không thưởng, không trừ; quote user 08/11 10:50 (22) | C: V5 (giải F22-b) · E: §E3 nguyên văn + chú thích |
| DD-20 | Mô hình ngầm thưởng ⇒ ghi rõ + độ nhạy, không đổi headline (22) | C: V5 · E: §E3 |
| DD-21 | Đối xứng cơ sở dữ liệu; không đếm hai lần; độ nhạy WIDE/NARROW/NONE; cấm suy moat từ giá; 5F non-PIT cấm backtest (22) | C: V5 · E: §E3 |
| DD-22 | Dispatch Taylor (`--bg --wakeup-ack --model opus --effort medium --timeout 5400 --thread`), nội dung brief, template DDV/FPT r3 (23) | C: bước 5 · E: §E4 |
| DD-23 | Skeptic BẮT BUỘC mọi DD (user 01/11 11:08 thay 29/10); phạm vi gồm moat; áp đính chính Phụ lục E; REFUTED văn bản ⇒ sửa trước đóng gói (24) | C: bước 7, 8 · E: §E4 |
| DD-24 | Hồ sơ §2.5 tách riêng, chỉ khi user xét mua (24, 42) | C: cuối Thứ tự bước · E: §E4, §E5 |
| DD-25 | Báo cáo NĐT làm liền; email chỉ khi user báo (03/11 15:23); dry-run; trình Discord; sửa vào nháp; gửi 1 lần; user nói gửi ⇒ grep L18 rồi gửi (25) | C: bước 10, 11 + IR "Gửi email" · E: §E4 |
| DD-26 | Đóng bus question; `kb/projects/<mã>-dd-<ngày>.md`; sổ giá "ngay sau skeptic" (25) | C: bước 9, 11 (giải F22-c) · E: §E4 |
| DD-27 | Kiểm chứng giả thuyết user (28) | C: Khung nội dung · E: §E5 |
| DD-28 | Chất lượng lợi nhuận (29) | C: Khung nội dung · E: §E5 |
| DD-29 | Net cash thật, đột biến, CFO thật (30) | C: Khung nội dung · E: §E5 |
| DD-30 | Ghi nhận DT POC/nghiệm thu, Q4, backlog vs MoU (31) | C: Khung nội dung · E: §E5 |
| DD-31 | KH/cổ đông lớn, room, ADV, sizing ≤0,5–1,0% NAV (32) | C: Khung nội dung + V8 (F22-d) · E: §E5 |
| DD-32 | Pháp lý WARNING + scandal di cư + ngoại trừ kiểm toán (33) | C: Khung nội dung · E: §E5 |
| DD-33 | Định giá: PE chuẩn hoá, PB, EV, comp, kịch bản trọng số, vùng, "(ước lượng)", phản ứng giá quanh sự kiện (34) | C: Khung nội dung + bước 6 (F8) · E: §E5 |
| DD-34 | rf chuẩn hoá ~6,75% (6,0–7,5); không huy động/TPCP thô làm rf; ERP ghi rf; β ~1,1 Blume (35) | C: V2 · E: §E6 |
| DD-35 | ERP nội địa (30/10), không CRP; Damodaran 8,13%/15,8% đầu trên; Ke 12,3–13,4% (ERP 5,0–6,1; dải 10,5–14,0); không 1 điểm; Ke>~15% = lệch (35) | C: V2 (8,13%/ERP 5,0–6,1 chỉ ở ext) · E: §E6 |
| DD-36 | Ke vùng + 3 mốc; độ nhạy g×Ke, tỉ trọng terminal; hạ Ke kèm g≤GDP + RONIC≥Ke; không nâng g đồng thời (35) | C: V2 · E: §E6 |
| DD-37 | Chỉ DCF vô hạn; dòng tiền có thời hạn ⇒ lãi khớp kỳ hạn; `consumer_deposit_rate()` giữ nguyên (35) | C: V2 (phần đầu) · E: §E6 |
| DD-38 | r=13,5% neo 03/11 (user 22:27), `deposit_rate_vn` effective=max(Big-4 12M, CCTG 12M) (36) | C: V1 · E: §E6 |
| DD-39 | β=1 (giả định, độ nhạy 0,5/1,0); báo r, neo, ±50/±100bp (36) | C: V1 · E: §E6 |
| DD-40 | Thanh khoản: trước/sau CK, ADV/free float/10–20%, cơ sở độc lập, nhãn theo sau CK, quy mô vị thế (36) | C: V3 · E: §E6 |
| DD-41 | Dự án mới NPV=0 base (user 03/11 17:06); đã chi = tài sản; cấm "đầu tư ⇒ giảm giá trị" (37) | C: V4(a) · E: §E7 |
| DD-42 | Lệch NPV=0 cần cơ sở độc lập (+/−); không "nguồn cung tự sập giá"; chi phí vốn cao không mặc định âm; mọi giảm trừ có dòng cơ sở; ca MVC (37) | C: V4 · E: §E7 |
| DD-43 | Hai nền V_ngắn/V_dài + D (11/11 11:37), cờ ln2/ln3, FCFE≤0, blend REFUTED, bẫy ROE≈g (38) | C: V6 · E: §E8 |
| DD-44 | Chặn g/ROE [0;0,8] (11/11 12:09); "tái đầu tư bị chặn ở 80%"; không ghi v_short/v_long/D vào sổ (38) | C: V6 · E: §E8 |
| DD-45 | Cờ phân kỳ ngữ cảnh capex + C4 (11/11 12:59), nhãn, chạy lại ~Q4/2027 (39) | C: V6 · E: §E8 |
| DD-46 | Dòng D2 (11/11 17:23), nhãn 0/9 nền, cách đọc, ≥434 phép thử (40) | C: V6 · E: §E8 |
| DD-47 | Mục 5F tầng (b) trong khung (41) | C: Khung nội dung → V5 · E: §E5 |
| DD-48 | Mốc khoá trước + đổi nhận định CẢ HAI chiều (42) | C: Khung nội dung · E: §E5 |
| DD-49 | Bẫy BQ: GPM/NPM/EBITM/EBITDA_P0 TTM; Revenue/NP_P0 quý; dictionary sai; Cash_P0 thiếu HTM (ca DDV) (45) | C: Bẫy · E: §E9 |
| DD-50 | BQ chưa có quý mới ⇒ ghi lệch nguồn (46) | C: Bẫy · E: §E9 |
| DD-51 | Không kết luận trước Bobby (47) | C: Bẫy + bước 4 · E: §E9 |
| DD-52 | Snapshot là bối cảnh hiển thị (48) | C: V7 · E: §E9 |
| DD-53 | "Giá không rẻ" không đủ (49) | C: Khung nội dung · E: §E9 |
| DD-54 | Moat ≠ thương hiệu; ROIC đỉnh chu kỳ DRC/DGC; đếm hai lần; lực 6 (50) | C: Bẫy + V5 · E: §E3 |
| DD-55 | Không làm lại từ đầu (51) | C: Nguyên tắc chung · E: §E3 |
| DD-56 | Khoá giả định + `assumptions_md5`; sửa nguồn sau ghi sổ = rev mới (54) | C: Chống làm lại + Sổ giá · E: §E10 |
| DD-57 | Trường sổ A2 từ 2026-11-23 + định nghĩa enum + ràng buộc CONFIRMED + rev mới/`correction_reason` + hàng đợi hạn 29/11 (55) | C: Sổ giá (enum định nghĩa ở ext) · E: §E10 |
| DD-58 | B2: tâm >5% hoặc đổi nhãn ⇒ phản biện lại; ≤5% cơ học giữ FIXED_UNVERIFIED; CONFIRMED qua `dd_ledger_append_confirmed.py` sau `dd_skeptic_run.py`; `dd_reconfirm_plan.py` (56) | C: bước 8 + Sổ giá · E: §E10 |
| DD-59 | Fan-out ≥5 ⇒ pilot 1 mã (57) | C: Chống làm lại · E: §E10 |
| DD-60 | Bài học kèm `evidence:` + đối chiếu dictionary (58) | C: Chống làm lại · E: §E10 |

## B. dd-investor-report (46 luật)
| # | Luật/ràng buộc/số (dòng cũ) | Vị trí mới |
|---|---|---|
| IR-01 | Chuẩn bắt buộc 1–6 (tóm tắt L9–16); chuẩn thắng mẫu SCL (8–16) | C: các L tương ứng + Tiền đề · E: §X1 |
| IR-02 | Mẫu SCL viết trước L9–12: không bắt chước NON/AMBIGUOUS, vùng kiểm định, xung đột lợi ích, tiêu đề trung tính (17–18) | C: Tiền đề · E: §X1 |
| IR-03 | Exemplar path, 14 trang, quote user 29/10, đọc mẫu trước (20–21) | C: Tiền đề · E: §X1 |
| IR-04 | Bước đóng gói; không tạo nghiên cứu mới; dùng bản đính chính (ca SCL §13) (24–27) | C: Tiền đề · E: §X2 |
| IR-05 | Top-down trình bày / bottom-up giá trị; trang 1 kiểu Goldman (30–33) | C: Cấu trúc · E: §X2 |
| IR-06 | Thứ tự bottom-up + đối chiếu Bobby/comp (34–35) | C: Cấu trúc · E: §X2 |
| IR-07 | Câu tiêu đề-kết luận; đơn vị/nguồn/mốc; "(ước lượng)"; tách sự kiện/ước lượng/nhận định (36–38) | C: Cấu trúc · E: §X2 |
| IR-08 | Khung mục (Summary, 1–10, Phụ lục A–F) (41–47) | C: Cấu trúc (trỏ) · E: §X2 |
| IR-09 | 10 biểu đồ chuẩn + CSV (48–49) | C: Cấu trúc (trỏ) · E: §X2 |
| IR-10 | L1 không fear-buy (user 29/10 19:20) (52–55) | C: L1/L11/L12 · E: §X3 |
| IR-11 | L2 không gán nhân quả giá (56–57) | C: L2 · E: §X3 |
| IR-12 | L3 luật nội bộ không đưa; tra ack.json/current_ops (58–59) | C: L3 · E: §X3 |
| IR-13 | L4 không lộ (user 29/10 18:01) (60–62) | C: L4 · E: §X3 |
| IR-14 | L5 giá DNSE, giờ, neo phiên trước, 2 mức (63–64) | C: L5 · E: §X3 |
| IR-15 | L6 cùng cơ sở, EPS hồi tố, BQ↔BCTC, sàn từ secdef (65–66) | C: L6 · E: §X3 |
| IR-16 | L7 kịch bản đúng phép tính (67) | C: L7 · E: §X3 |
| IR-17 | L8 giới hạn dữ liệu; pháp lý WARNING + phạm vi (68–69) | C: L8 · E: §X3 |
| IR-18 | L9 tiêu đề (mẫu SCL/DRI; subject) (71–76) | C: L9 · E: §X4 |
| IR-19 | L10 hero, hình mỗi mục, kiểu thường niên (78–88) | C: L10 · E: §X4 |
| IR-20 | L11 Phụ lục F chỉ miễn trừ; trung dung (90–93) | C: L1/L11/L12 · E: §X4 |
| IR-21 | L12 khách quan toàn diện (95–105) | C: L1/L11/L12 · E: §X4 |
| IR-21b | L12 gạch cuối "skeptic không còn là cổng… dành cho mua discretionary" (106–107) | ĐÃ THAY 01/11 — xoá khỏi core; E: §X4 có nhãn ⟨ĐÃ THAY⟩ (F22-a) |
| IR-22 | L13 font Be Vietnam Pro, NFC, stack HTML, logo, banner, nguyên nhân Georgia (109–122) | C: L13 · E: §X5 |
| IR-23 | L14 Ke trong báo cáo (124) | C: L14/L17/L21 · E: §X6 |
| IR-24 | L15 bản đồ khu vực + ảnh sản phẩm (126–141) | C: L15 · E: §X7 |
| IR-25 | L16 ít chữ: ≤10–12 trang, ≤1.800 từ, >60% chữ (143–149) | C: L16 · E: §X8 |
| IR-26 | L17 `dcf_rate_lines`, r\*, TPCP 10Y, display-only, r 13,5% thay "r giữ hằng", engine `dcf_valuation` khung riêng, cache r\* hết hạn 2026-12-14 (151–153) | C: L14/L17/L21 (2 mục cuối chỉ ở ext) · E: §X9 |
| IR-27 | L18 không nhắc lỗi; Phụ lục E trung tính; giả định có peer; grep (155–159) | C: L18 · E: §X10 |
| IR-28 | L19 mù giá, giá điện (Luật 61/2024 Đ.52; TT 12/2025 IRR ≤12%), pháp lý không base, tầm nhìn (161–165) | C: L19 · E: §X11 |
| IR-29 | QT1 xác nhận có REPORT (168) | C: QT bước 1 · E: §X12 |
| IR-30 | QT2 dispatch + brief + template + sản phẩm + pymupdf Story (169–173) | C: QT bước 2 (L1–15 → L1–21) · E: §X12 |
| IR-31 | QT3 poll ScheduleWakeup, ~15–20 phút (174) | C: QT bước 3 (chỉ khi có job nền) · E: §X12 |
| IR-32 | QT4 Mike kiểm (a)–(e) + 2 grep (175–178) | C: QT bước 4 · E: §X12 |
| IR-33 | QT5 lệnh gửi, `--dry-run`, `--html-out`, `to_email`, `.ccdb-attachments` (179–182) | C: QT bước 5 + Gửi email · E: §X12 |
| IR-34 | QT6 báo user + luật khuyến nghị bên thứ ba (183–185) | C: Gửi email · E: §X12 |
| IR-35 | Bẫy alt `"` (ca NNC 31/10) (188–189) | C: Bẫy · E: §X13 |
| IR-36 | matplotlib chỉ ở wc_venv (190) | C: Bẫy · E: §X13 |
| IR-37 | `send_report_email.py` chỉ DAILY; §21 nếu có tỷ suất per-position (191–192) | C: Bẫy · E: §X13 |
| IR-38 | Site chặn curl → WebFetch; Drive URL; không giả header (193–194) | C: Bẫy · E: §X13 |
| IR-39 | Matplotlib DejaVu đủ dấu; 200 dpi; 1 màu chủ đạo + 1 nhấn (195) | E: §X13 |
| IR-40 | Story lặp nền hàng khi bảng tách trang (196) | C: Bẫy · E: §X13 |
| IR-41 | Cập nhật 01/11: chuỗi bước; luật 12 vế skeptic đã thay (199) | C: Tiền đề · E: §X14 |
| IR-42 | Sổ mức giá (user 01/11 22:39): trường, rev cao nhất thắng, center_kind, trích nguyên văn, selfcheck 0 lỗi, watch ≥15%, hết hạn BCTC mới/120 ngày (202) | C (DD): Sổ mức giá (giải F22-c) · E: §X15, DD §E10 |
| IR-43 | Trường sổ A2 (203, trùng DD-57) | C (DD): Sổ mức giá · E: §X15 |
| IR-44 | Email chỉ khi user báo; báo địa chỉ + hash PDF; "DD X rồi gửi email" = lệnh gửi (206) | C: Gửi email · E: §X16 |
| IR-45 | Luật 20 dự án mới; tiêu đề không xây trên nghịch lý (209) | C: L20 · E: §X16 |
| IR-46 | Luật 21 r gắn lãi huy động + thanh khoản, bản NĐT lời thường (212) | C: L14/L17/L21 · E: §X16 |

## C. Luật MỚI viết vào core (đã duyệt, không có trong skill cũ)
| # | Luật | Nguồn | Vị trí |
|---|---|---|---|
| N-01 | Pha MÙ GIÁ → khoá → pha SAU KHOÁ trong thứ tự bước (F8) | review F8, P0-2; L19 | C (DD): bước 5–6 |
| N-02 | Snapshot ra thư mục trung tính không chứa mã (A8) | A8 22/11 | C (DD): bước 3 |
| N-03 | `dd_blind_lint.py` cho brief sector/valuation/skeptic (A5; chỉ cảnh báo, chưa nối dispatch) | A5 | C (DD): bước 4, 5, 7 |
| N-04 | `assumptions.json` v1 + `dd_assumptions_lint.py` CẢNH BÁO 2 tuần (B4, ĐÃ merge master `b242e616e`; schema `kb/schemas/dd_assumptions_v1.json`, ENFORCE_FROM 9999-12-31) | B4, D3–D5 | C (DD): bước 5 · E: §E6, §E7 |
| N-05 | Runner `dd_skeptic_run.py` → `skeptic/rN.json`; `DD_GENERAL` chỉ sau khi user duyệt `.proposed` (A4/B6) | A4, B6 | C (DD): bước 7 |
| N-06 | B2 phản biện lại >5%/đổi nhãn (đã có ở skill cũ :56) | B2/D1 | C (DD): bước 8 |
| N-07 | Ghi sổ sau áp đính chính, một câu (F22-c) | review F22 | C (DD): bước 9 |
| N-08 | D2: `deal_type`, thẻ luận điểm, FPT miễn exit cố định (user 22/11 19:27), NNC/VGS chờ | D2, B3 | C (DD): Loại deal |
| N-09 | D3: capex tuân thủ = dòng tiền ra, bổ sung luật 03/11 | D3 | C (DD): V4(b); C (IR): L20 · E: §E7 |
| N-10 | D4: báo hai đầu dải 12,3–13,4%; terminal RONIC=Ke NARROW/NONE = giả định cuối kỳ | D4 | C (DD): V1, V5; C (IR): L14 · E: §E6, §E12-b |
| N-11 | D5: `audited_fy_missing`, không Bậc 1, LAG coi như chưa DD | D5 | C (DD): Sổ giá + Cổng LAG · E: §E12-g |
| N-12 | B1: `LAG_DD_REQUIRE_CONFIRMED=False` mặc định, bật tay | B1 (outer `096541ed8`, trên main) | C (DD): Cổng LAG |
| N-13 | A6: lint email trong `send_dd_report_email.py`, `DD_LINT_BLOCK=False` | A6 | C (IR): QT bước 5 · E: §X18 |
| N-14 | Sizing: 3 mức, nhãn CHƯA THỐNG NHẤT — chờ user (Q4) | review F22-d | C (DD): V8 |
| N-15 | Cổng `--claim` chưa từng dùng — ghi hiện trạng | review F22-f | C (DD): bước 1 · E: §E12-f |

## D. Đếm
- Cũ: **106 luật** (DD 60 + IR 46; IR-21b tính trong IR-21). Có vị trí trong bản mới: **106/106** (105 hiệu lực ở core hoặc ext; 1 câu chết IR-21b giữ ở ext có nhãn ĐÃ THAY).
- Dòng nguyên văn: mọi dòng THÂN không rỗng của 2 file cũ có trong ext (kiểm cơ học `B5_skill_rewrite/check_lines.py` — bản sao script của arch-reviewer: 0 dòng thân thiếu SAU KHI bỏ 17 chú thích ⟨…⟩ chèn trong 7 dòng (DD 8, IR 9); DD 48, IR 183 dòng). 17 dòng TIÊU ĐỀ (DD 4, IR 13) chỉ đổi định dạng (`## X` → `#### (tiêu đề cũ) X`), nội dung giữ.
- Kích thước sau vòng 2 (byte): DD core 16.853 (vượt 14KB mục tiêu vì vòng 2 khôi phục hệ quả cờ V6, ngưỡng 10–20% V3, phép thử Ke>15%, giờ ICT, hiện trạng skeptic; trong trần ~16KB reviewer cho phép ±), IR core 12.936.
- D6 (Quick/Full) đã duyệt, thí điểm tháng 2–3 (B7) — chưa nằm trong core.
- Luật mới thêm vào core: 15 (N-01…N-15).

## E. Mâu thuẫn
**Đã giải:** F22-a (câu skeptic chết) · F22-b (RONIC: dự báo vs cuối kỳ, theo D4) · F22-c (thứ tự ghi sổ) · F22-e (template → DDV/FPT r3, file tồn tại) · F22-f (ghi đúng hiện trạng `--claim`) · F8 (pha mù vào thứ tự) · IR bước gửi đứng trước luật "chỉ gửi khi user báo" · brief "L1–15" → "L1–21" · poll ScheduleWakeup chỉ khi có job nền.
**Còn lại (không tự giải):**
1. **F22-d sizing** 0,5–1,0% vs 2–4% vs 5% — chờ user (Q4).
2. **D5 vs code — ĐÃ VÁ 22/11 23:14 ICT (A7 `468b75384`)**: `bin/dd_price_zone_watch.py:115` nay loại mã `audited_fy_missing=true` khỏi Bậc 1 (selfcheck 124/0); cổng LAG chỉ chặn khi bật `LAG_DD_REQUIRE_CONFIRMED` (mặc định False).
3. **`--claim`**: dùng hay gỡ — Mike/user.
4. **Phụ thuộc**: B2, B3, B4 ĐÃ merge master (B4 `b242e616e`; B3 `kb/thesis_cards.json`, cron chờ user duyệt). Còn chờ user: `DD_GENERAL` cần duyệt `fundamental-skeptic.md.proposed` (B6); thẻ FPT/NNC/VGS + cron B3. Core ghi đúng điều kiện, không tuyên bố đang chạy.
5. Frontmatter IR vẫn "Viết và gửi email…" (giữ trigger theo SPEC mục 6); luật thân là "chỉ gửi khi user báo" — không trái nhau về hành vi nhưng mô tả có thể đọc nhầm; đổi mô tả cần Mike quyết.
6. **Skeptic brief (R1 #2)**: `bin/dd_skeptic_run.py` brief = template cố định fear-buy; `fundamental-skeptic.md` thuần fear-buy, không có "moat" ⇒ phạm vi moat/cân bằng/thiếu hạng mục KHÔNG truyền tới khi duyệt `.proposed`. Cách tạm: CHƯA THỐNG NHẤT — chờ user (đề xuất Mike tự thêm câu kiểm moat vào brief chạy tay).
7. **IR bước 4**: grep fear-buy chỉ có ở ext (§X12); lint A6 chưa phủ "xung đột lợi ích", "đang nắm giữ", "kiểm định", "sợ hãi", "NAV" (`send_dd_report_email.py:30-37`) — việc riêng, không sửa lint ở B5.
