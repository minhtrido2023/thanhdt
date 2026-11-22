# Review quy trình due diligence (DD) — 22/11/2026

Reviewer độc lập, chỉ đọc. Phạm vi: 2 skill, 3 định nghĩa agent, sổ `kb/dd_price_zones.json` (94 entry / 36 mã, 26/10–22/11), script sổ/ứng viên/cổng, 5 nghiên cứu hiệu chuẩn, retro 02–21/11, hồ sơ ca. **ĐK** = đã kiểm trên file/số đo; **SL** = suy luận.

## 1. Kết luận

| Trục | Điểm /10 | Một dòng |
|---|---|---|
| Độc lập / chống thiên lệch | 5 | Thiết kế đúng (đọc ngành mù, phản biện, mù giá) nhưng cưỡng chế bằng văn xuôi; mù thật hiếm khi đạt |
| Hiệu chuẩn & track record | 3 | Chưa có vòng chấm lại tâm DD; nền FCFE trượt tiêu chí hội tụ; độ nhiễu sửa tâm ≈ ngưỡng −15% |
| Dữ liệu đầu vào | 6 | BCTC gốc + số trang là điểm mạnh; đọc scan thủ công một người, lỗi "thiếu hạng mục" không ai bắt |
| Tái lập | 6 | md5 + chạy lại trùng byte tốt; khoá giả định không có schema chung |
| Cổng kiểm soát | 6 | Phản biện bắt lỗi thật; nhưng trượt vòng 1 là chuẩn mực, 16/36 mã chốt số chưa được xác nhận lại |
| Tích hợp quyết định | 4 | Sổ → ứng viên chạy ổn; thiếu vòng đời luận điểm, kill criteria, hậu kiểm; chân trời lệch |
| Quản trị quy trình | 4 | 61KB luật chồng theo ngày, có mâu thuẫn nội bộ, luật chết, cổng chết |
| Báo cáo NĐT | 7 | Bản gần đây đạt chuẩn ngắn/sạch; còn phụ thuộc kiểm tay, đã có 1 ca gửi sai rồi gửi lại |

**3 điểm yếu nặng nhất**
1. **Không đo được DD đúng hay sai, và tâm chưa ổn định.** Giữa bản đầu và bản mới nhất trong sổ, tâm đổi ở 19/30 mã so sánh được, trung vị |Δ| 10,2%, 6 mã >15% (DRI +45%, QTP −41%, HHS +40%) — cùng cỡ với ngưỡng mua −15%.
2. **Độc lập chỉ là tuyên bố.** 5/5 lượt thử mù 26/10 tự khai "blind: no"; PAT lượt 1–2 brief có giá + cột PE; đường dẫn snapshot đưa Bobby chứa mã; người phản biện đọc báo cáo có giá (ĐK ở PAT, SL ở ca khác).
3. **DD → tiền thiếu vòng đời luận điểm.** Định giá nội tại nhiều năm nhưng thoát ±10%/25 phiên; mốc kiểm chứng và điều kiện huỷ nằm trong văn bản tự do; chưa có hậu kiểm; cổng LAG (tiền thật) đọc tâm mà không đọc trạng thái phản biện.

**3 điểm mạnh nhất**: (1) cổng phản biện bắt lỗi trọng yếu trước khi phát hành (VLB hôm nay: 61.798 → 51.163, nhãn RẺ → TRUNG TÍNH); (2) sổ giá append-only có trích dẫn nguồn, khoá md5, hết hạn, chặn hệ giá sau sự kiện quyền, cron có báo stale; (3) kỷ luật nghiên cứu khoá trước, chấp nhận kết quả âm (blend bị bác, V_ngắn chỉ hiển thị).

## 2. Bảng phát hiện

### Điểm yếu

| ID | Phát hiện | Bằng chứng | Mức | Chắc |
|---|---|---|---|---|
| F1 | Tâm DD không ổn định qua các bản sửa | Sổ: 59/94 entry là bản thay thế; MVC 9 rev, TV1 6, SCL/NNC 5. Trước 09/11 TB 3,09 rev/(mã, ngày); từ 09/11 còn 1,35 | Cao | ĐK |
| F2 | Quyết định đã bị "quất hai chiều" do tâm đổi | DRI: tâm 10.500 (30/10) → user bán hết 02/11 → tâm 15.257 (08/11, +45%) → 20/11 DRI nằm trong danh sách ứng viên mua (−17,4%). Nguyên nhân chính là đổi luật phương pháp (`dd_audit_newproject_20261103`: riêng luật dự án mới +~30%), không phải dữ kiện doanh nghiệp mới | Cao | ĐK |
| F3 | Không có chấm điểm forward cho tâm/vùng DD và dự báo ngành | `paper_programs_registry.json` chỉ có chương trình cho bộ chọn mã (mốc 2027-04-06), không có cho sổ giá; 28 file sector read có FORECAST khoá trước, không script nào trong `bin/` đọc/chấm | Cao | ĐK |
| F4 | Nền định giá cơ học trượt kiểm định hội tụ | `dd_vn_calib_20261111/REPORT.md:1-3`: KHÔNG TƯƠNG THÍCH (K3a 1,009); khi FV<giá chỉ 32% chạm tâm trong 60 tháng; rule 0,85×tâm kích hoạt 49,6% số phiên, theo danh tính mã. Lớp phán đoán DD không kiểm PIT được | Cao | ĐK |
| F5 | Tâm DD bám giá | Cùng báo cáo :82-83: IQR log DD/giá 0,36 so với engine/giá 1,06. Sổ hiện tại: giá/tâm trung vị 1,08, 18/35 mã giá > tâm — khớp phản biện #5 của user ở PAT | Cao | ĐK (nguyên nhân: SL) |
| F6 | Mù giá/mù kết luận không được cưỡng chế | `dd_blind*/LOCK.txt`: 5/5 "blind: no" (memory, template lộ verdict, cột PE, WebSearch). `pat-dd-redo-objective-20261114.md:6-10`: lượt 1–2 không mù; phản biện không mù khuyến nghị 69–70k, sát giá 71.000 | Cao | ĐK |
| F7 | Skill tự gây rò mã cho người đọc ngành | `due-diligence/SKILL.md:18` ghi snapshot vào `dd_<MÃ>_<ngày>/` rồi đưa đường dẫn; sector read 22/11 dòng 289 trích `…/dd_VLB_20261122/macro_snapshot…` trong khi header khai "KHÔNG biết mã" | TB | ĐK |
| F8 | Bước mù giá không nằm trong thứ tự của skill chính | "Mù giá" chỉ được nhắc qua 2 lần trong `due-diligence/SKILL.md` (:19, :22); luật đầy đủ nằm ở skill đóng gói (luật 19). Khung nội dung lại yêu cầu PE/PB, phản ứng giá, ADV — không tách pha | TB | ĐK |
| F9 | Định nghĩa người phản biện lệch vai thực tế | `fundamental-skeptic.md`: công tố fear-buy, 7 đòn theo §2/§2.5, phải đọc "FIRST, in full" tài liệu 399.755 byte. Skill dùng nó cho MỌI DD (số liệu/nguồn/cân bằng/moat). Phản biện hai chiều + mù giá chỉ có ở prompt riêng của ca PAT | Cao | ĐK |
| F10 | Trượt phản biện vòng 1 là chuẩn mực | 14/16 mã DD mới từ 09/11 bị REFUTED/INCONCLUSIVE hoặc phải sửa số sau vòng đầu (chỉ MSB qua; PNJ qua một phần). Phân loại 54 lý do sửa trong sổ (theo từ khoá, xấp xỉ): 26 do phản biện bắt lỗi mô hình, 16 do luật/chỉ đạo user đổi, 7 nhãn sổ, 2 sự kiện vốn | Cao | ĐK |
| F11 | Lỗi lặp lại theo lớp, chưa thành checklist cơ học | Từ `correction_reason`: vốn dự án đã chi không cộng lại giá sổ (SZL, SCL, CSV, GAS, BSR, DDV); thiếu trừ quỹ KT-PL (DCM, SIP, SZL, BSR, PAT, VLB); trọng số/lưới một chiều (PVT, PVP, FPT, SIP, MBB, DRI, NNC, MSB); đếm đôi (NNC, MVC, SIP); bỏ sót ý kiến kiểm toán (LLM, TV1) | Cao | ĐK |
| F12 | Số chốt không được xác nhận lại sau khi sửa | 16/36 mã có trạng thái cuối "đã áp đính chính, không chạy vòng phản biện nữa" (BSR, CST, CSV, DBC, DCM, GAS, LLM, PAT, POW, SZL, TCH, TTA, VCB, VCP, VGS, VLB); 19 CONFIRMED. `skeptic_status` là văn bản tự do; `dd_price_zone_watch.py`, selfcheck và cổng LAG không đọc trường này | Cao | ĐK |
| F13 | Phản biện bắt sai số, không bắt thiếu hạng mục | QTP (`qtp-dd-20261117.md`): phản biện "khớp 14/14 số", email 17/11 ghi RẺ, tâm 13.140; user chỉ ra thiếu dự án khí thải ~3.485 tỷ → tâm 7.701 (−41%), ĐẮT, gửi email lần 2. Luật NPV=0 bị áp sai cho capex tuân thủ | Cao | ĐK |
| F14 | Kết quả phản biện không được lưu thống nhất | 17/36 thư mục ca không có file phản biện; retro 04/11 ghi "không có event verification của skeptic cho DCM trên bus" | TB | ĐK |
| F15 | Tốc độ lấn độ sâu | VLB: vòng 1 (đọc scan + mô hình + báo cáo) ~9 phút (09:45→09:54Z), ghi sổ ~30 phút sau khi bắt đầu. 36 mã / 4 tuần. Job DD (lọc từ khoá, xấp xỉ): ~280 job, ~925 USD, trung vị 7,5 phút và 2,8 USD/job; đuôi dài NNC 48, DRI 43, MVC 35 USD. Chưa gồm agent gọi trực tiếp | TB | ĐK (hệ quả chất lượng: SL) |
| F16 | Khoá giả định không có schema | 44/94 entry có `assumptions_md5`; file khoá: txt 19, json 14, md 6, py 5; mỗi JSON một bộ khoá riêng (so VCB với DBC). DCM (bản mới nhất) không có khoá | TB | ĐK |
| F17 | Đọc scan phụ thuộc một người đọc, công cụ ở `/tmp` | `SKILL.md:16` (pymupdf ở `/tmp/pdflib`, render PNG rồi đọc mắt); retro 17/11: VCB r2 "không có công cụ đọc PDF"; VCB còn số kiểm toán "chưa render lại từ scan"; VLB thiếu BCTC 2025 kiểm toán | TB | ĐK |
| F18 | Chân trời luận điểm lệch chân trời giao dịch | `discretionary_exit_rules.json`: FPT/NNC ±10%/25 phiên, VGS +15%/−10%/25 phiên, 5% NAV/mã. Hiệu chuẩn (nền engine): sau 36 tháng giá chỉ đi ~7% quãng log về FV. FPT vào ~51.160 (06/11), đóng 45.000 (20/11, −12%): lệnh bán huỷ, đang hỏi user miễn stop/mua thêm (`kb/memory/Mike.md:10`) — chưa có bước "kiểm lại luận điểm" | Cao | ĐK |
| F19 | Mốc kiểm chứng/điều kiện huỷ không máy đọc được | Schema sổ không có trường milestone/abandon; nằm trong `notes`. Không cron nào nhắc mốc. Chưa có mẫu hậu kiểm sau bán | Cao | ĐK |
| F20 | Luật −15% chọn ngược mã có cờ | Ứng viên 20/11: 7 mã, 4 mã mang cờ (HHS forensic exclude + RATING_FAIL, −30,6%; DBC RATING_FAIL; TCH FLOOR_FAIL; MVC ngoài universe, ADV 0,9 tỷ). 11/34 mã (32%) đang ở diện cảnh báo, trong đó 4 mã đang giữ đều dưới tâm >20% | TB | ĐK (chọn ngược: SL) |
| F21 | Ba mức chi phí vốn cùng tồn tại | Engine 12,25% (khung `domestic_v2`; là thành phần V nặng 0,50 của bộ chọn mã, `discretionary_dd_pick.py:43`); nghiên cứu 30/10 chốt DẢI 12,3–13,4% "không một điểm" (`SKILL.md:35`); báo cáo DD dùng ĐIỂM 13,5% (`SKILL.md:36`), nằm trên dải | TB | ĐK |
| F22 | Mâu thuẫn/luật chết trong skill | (a) `dd-investor-report/SKILL.md:25` + luật 12: "skeptic chỉ khi xét mua" còn nguyên, bị :199 thay; (b) `due-diligence/SKILL.md:22`: cùng một đoạn vừa "còn lại RONIC = Ke" vừa "KHÔNG ép … RONIC về … Ke" cho NARROW/NONE; (c) ghi sổ "ngay sau skeptic" (:25) trong khi doc sổ nói "bản SAU phản biện"; (d) sizing: skill 0,5–1,0% NAV, định nghĩa phản biện 2–4%, thực tế 5%; (e) template trỏ `dd_DDV_20261026` cũ hơn phần lớn luật; (f) cổng trần DD `--claim` (`discretionary_dd_pick.py:15`) chưa từng dùng: `data/discretionary_dd_ledger.jsonl` không tồn tại, skill bước 1 dùng cơ chế khác | TB | ĐK |
| F23 | Tích luỹ dòng hiển thị chưa qua kiểm định | V_ngắn, V_dài, D, C4, D2: 4 nền, không nền nào qua tiêu chí khoá trước (skill ghi "0/9 nền qua"); vẫn thêm vào mọi báo cáo | TB | ĐK |
| F24 | Thiếu bước so với thực hành DD cơ bản | Không mô-đun theo ngành (VCB thiếu CET1/LDR/CASA/nợ nhóm 2); không quét cam kết vốn/nghị quyết ĐHCĐ có hệ thống; không đối chiếu consensus sau khoá; hỏi doanh nghiệp chỉ 1 tiền lệ (email IR DDV); không có góc nhìn danh mục (NNC–MVC–VLB cùng ngành đá) | TB | ĐK |
| F25 | Kiểm bản NĐT hoàn toàn bằng tay | `send_dd_report_email.py` không chứa lint; grep luật 18/tên nội bộ/khớp số do Mike chạy tay. Sổ NNC rev3 tự ghi "lệch với báo cáo NĐT v2" | TB | ĐK |

### Điểm mạnh cần giữ

| ID | Cơ chế | Ví dụ đã chứng minh | Chắc |
|---|---|---|---|
| S1 | Phản biện bắt buộc trước phát hành | VLB 22/11 (tốc độ cấn trừ 47,6 → 19,4 tỷ/năm, thiếu trừ quỹ 14,8%: −17%, đổi nhãn); LLM (bỏ sót soát xét ngoại trừ, 1,05× → 1,35×); GAS/CSV sửa theo chiều TĂNG — không chỉ kéo xuống | ĐK |
| S2 | Sổ giá có kỹ thuật tốt | Append-only + trích nguyên văn + selfcheck số↔nguồn; md5 lệch ⇒ loại; hết hạn theo BCTC mới/120 ngày; chặn so giá sau sự kiện quyền (SCL, HHS); cron 19:45 báo lỗi thật khi stale | ĐK |
| S3 | Tái lập cơ học | Mike chạy lại `calc.py`/model trùng byte trước khi ghi sổ (VCB r4, PAT r5, VLB r2) | ĐK |
| S4 | Nghiên cứu khoá trước, nhận kết quả âm | Blend w=0,5 bị bác, V_ngắn chỉ hiển thị, khai N hiệu dụng (~349 mã chứ không phải 2.234 dòng), khai N trials | ĐK |
| S5 | Đọc ngành mù có dự báo bác bỏ được | 28 sector read, có ID dự báo + ngày, tự chỉ ra dự báo cũ định nghĩa lỏng (file 22/11 mục 5.1) | ĐK |
| S6 | BCTC gốc + số trang | `dd_VLB_20261122/notes_raw.md`: mỗi số gắn [trang]; biết bẫy cột BQ (TTM vs quý) | ĐK |
| S7 | Vòng retro tự phát hiện pattern | Retro 02→07/11 nêu "DD đa vòng do giả định chưa khoá" 5 ngày liền, escalate, user chọn B; số rev trên sổ giảm 3,09 → 1,35 | ĐK |
| S8 | Bản NĐT cải thiện đo được | 12 bản từ 10/11: thân ~590–1.230 từ, 7–12 trang ở các bản đo được, 0 từ cấm (đếm regex, xấp xỉ); bản ≤02/11: 3.000–6.300 từ | ĐK |

## 3. Plan cải thiện

Nguyên tắc: không thêm luật văn xuôi; mỗi mục là một cổng/lint/selfcheck. Không mục nào tự đổi luật user đã chốt — chỗ chạm luật user đưa sang mục 4.

### P0 — tuần này (cơ học, rủi ro thấp)

| # | Vấn đề | Hành động | Cưỡng chế | Chủ | Công | Thước đo | Rủi ro / phụ thuộc |
|---|---|---|---|---|---|---|---|
| P0-1 | F12, F14 | Thêm trường enum `skeptic_final` (CONFIRMED / FIXED_UNVERIFIED / REFUTED / NONE) + đường dẫn file verdict vào sổ; watch in nhãn cạnh mỗi mã | `dd_price_zones_selfcheck.py` từ chối entry mới thiếu enum hoặc thiếu file | Taylor, arch-reviewer soát | 0,5 ngày | 100% entry mới có enum; tỷ lệ CONFIRMED lúc phát hành | Backfill 36 mã từ văn bản tự do. Cách cổng LAG dùng enum: Q1 |
| P0-2 | F6, F7, F8 | (a) snapshot vĩ mô ghi vào thư mục trung tính, không chứa mã; (b) `dd_blind_lint.py` quét brief/fact pack tìm giá, P/E, P/B, vốn hoá, mã; (c) giá chỉ lấy qua một script so giá, script từ chối chạy khi chưa có file khoá định giá (md5 + giờ) | Lint rc≠0 chặn dispatch; script so giá fail-closed | Mike | 0,5 ngày | Tỷ lệ hồ sơ khai mù đạt; 0 brief chứa token giá | Taylor có working memory: lượt định giá cần agent không trạng thái (đã làm ở PAT) |
| P0-3 | F9, F14 | Tách định nghĩa phản biện thành 2 chế độ: DD chung (hai chiều, mù giá, thêm đòn "thiếu hạng mục": capex cam kết, phát hành, hạn pháp lý; không đọc tài liệu 400KB) và fear-buy (giữ nguyên). Runner ghi verdict JSON ra `<dir>/skeptic/rN.json` | Runner script (kiểu `verify_finding.sh`), không để agent tự ghi | Mike soạn, user duyệt định nghĩa | 0,5 ngày | 100% DD có file verdict; token/lượt phản biện giảm | Đổi định nghĩa agent cần user duyệt |
| P0-4 | F13, F25 | Đưa vào `send_dd_report_email.py`: các grep (luật 18, tên nội bộ, nhãn fear-buy) + đối chiếu tâm/vùng/giá trong md với rev mới nhất của sổ + yêu cầu `skeptic_final=CONFIRMED` (hoặc cờ miễn do user) | rc≠0 chặn gửi, in dòng vi phạm | Taylor | 0,5 ngày | 0 lần gửi lại do sai; 0 lệch số md↔sổ | Regex "trước đây" có thể báo giả ⇒ thử trên 10 bản gần nhất trước khi bật |
| P0-5 | F22 | Dọn 2 skill, KHÔNG đổi luật: gom "luật hiện hành" một chỗ, lịch sử theo ngày sang file ext; xoá câu chết (F22a); đưa pha mù + khoá vào thứ tự bước; dùng hoặc gỡ cổng `--claim` | arch-reviewer soát "không mất fact, không còn câu trái nhau" | Mike | 3–4 giờ | Mỗi skill ≤ ~12KB; 0 cặp câu mâu thuẫn | F22b/d cần user trả lời Q4 trước |

### P1 — 2–4 tuần

| # | Vấn đề | Hành động | Cưỡng chế | Chủ | Công | Thước đo | Rủi ro / phụ thuộc |
|---|---|---|---|---|---|---|---|
| P1-1 | F10, F11, F16, F13 | Schema `assumptions.json` v1, khoá bắt buộc theo đúng các lớp lỗi lặp: cơ sở số cổ phiếu, xử lý XDCB/dự án (đã chi, còn phải chi, tăng trưởng hay tuân thủ), quỹ KT-PL, thuế + nguồn, vốn lưu động chuẩn hoá, trọng số kịch bản + cờ đối xứng, r + điểm neo, cơ sở chiết khấu thanh khoản, ý kiến kiểm toán, bên liên quan, khoản một lần, cam kết vốn từ nghị quyết/CBTT 12 tháng | `dd_assumptions_lint.py`: thiếu khoá ⇒ không gọi phản biện, không ghi sổ | Taylor | 1,5 ngày | Tỷ lệ qua vòng 1 từ 2/16 lên ≥50%; số vòng/ca ≤2 | Schema cứng quá sẽ không hợp ngân hàng ⇒ biến thể theo loại hình; sau P0-1 |
| P1-2 | F18, F19 | "Thẻ luận điểm" máy đọc trong sổ: `milestones[]` (ngày, chỉ số, ngưỡng, chiều), `abandon_triggers[]`; cron nhắc mốc đến hạn; vị thế chạm stop ⇒ bắt buộc "kiểm luận điểm" trước khi trình miễn stop/mua thêm | Selfcheck yêu cầu thẻ cho mọi mã đang giữ; cron báo mốc quá hạn chưa chấm | Taylor dựng, Mike vận hành | 1 ngày | 100% vị thế discretionary có thẻ; mốc chấm đúng hạn | Phụ thuộc Q2 (chân trời) |
| P1-3 | F3, F4, F5 | `dd_zone_scorecard.py` hằng tháng: với bản ĐẦU TIÊN phát hành của mỗi (mã, ngày DD), đo lợi suất gồm cổ tức 1/3/6/12 tháng, chạm tâm, nhóm rẻ so với đắt; thêm sổ chấm dự báo ngành. Đăng ký `paper_programs_registry.json`, khoá trước chỉ số và ngày đọc (~05/2027) | Cron tháng + mốc trong registry | Taylor; quant-skeptic soát thiết kế | 1 ngày | Scorecard chạy; N và CI công bố mỗi kỳ | N nhỏ, một giai đoạn thị trường: chỉ mô tả, không dùng để chỉnh tham số |
| P1-4 | F24 | Mô-đun theo loại hình (ngân hàng, BĐS/KCN, điện có PPA, mỏ có giấy phép): mục bắt buộc + nguồn số | Lint theo mã ngành ICB trong schema P1-1 | Taylor + người đọc ngành | 1 ngày | VCB/MBB lần sau có đủ CAR, nợ nhóm 2, bao phủ, LDR, CASA | Thiếu dữ liệu công khai ⇒ ghi "không công bố", không bịa |
| P1-5 | F17 | Nhập đôi: một agent không trạng thái đọc lại 10–15 số trọng yếu từ ảnh trang, so với bảng số của Taylor; chuyển công cụ PDF khỏi `/tmp` | Diff ≠ 0 chặn bước mô hình | Mike | 0,5 ngày | Tỷ lệ lệch nhập đôi (đo 10 ca đầu) | Nếu lệch ≈ 0 sau 10 ca thì hạ xuống lấy mẫu |

### P2 — 1–2 tháng

| # | Vấn đề | Hành động | Chủ | Công | Thước đo | Rủi ro |
|---|---|---|---|---|---|---|
| P2-1 | F5, F6, F15 | Luồng 3 pha làm mặc định cho DD "đầy đủ": A định giá mù (agent không trạng thái, khoá) → B phản biện hai chiều mù giá → C so giá + "thị trường đang định giá gì, vì sao ta khác" + consensus SAU khoá. Thí điểm 3 mã, so với luồng hiện tại | Mike | 2–3 ngày | Số vòng, chi phí/ca, số lần đổi nhãn sau phát hành | Chậm hơn mỗi ca ⇒ gắn với Q6 |
| P2-2 | F1, F20 | Hiển thị độ bất định của tâm (P25–P75, lịch sử rev) cạnh cảnh báo −15%; phân bậc cảnh báo; xếp mã có cờ xuống dưới | Taylor | 0,5 ngày | User đọc được "−15% có vượt nhiễu không" | Không đổi ngưỡng user (Q5) |
| P2-3 | F19 | Mẫu hậu kiểm khi đóng vị thế discretionary: luận điểm vs kết cục, lớp lỗi, bài học ⇒ bổ sung khoá schema P1-1 | Mike | 0,5 ngày + mỗi ca 20 phút | 100% vị thế đóng có hậu kiểm | — |
| P2-4 | F24 | Trang danh mục sleeve: tập trung theo ngành/nhân tố chung, tổng trần sleeve, tương quan ứng viên với vị thế đang giữ | Taylor, risk-auditor soát | 1 ngày | Hiển thị trong khối ứng viên | — |

Cưỡng chế và thứ tự P2: P2-1 chạy trên cổng P0-2 (chưa khoá ⇒ không so giá) và P0-1 (chưa CONFIRMED ⇒ không ghi sổ), làm sau P0-3 + P1-1; P2-2 sau P0-1, kiểm bằng selfcheck khối ứng viên; P2-3 sau P1-2, vị thế đóng thiếu file hậu kiểm ⇒ báo trong kiểm tra vận hành hằng ngày.

### P3 — hằng quý
- Bảng chỉ số quy trình trong retro quý: vòng/ca, tỷ lệ qua vòng 1, chi phí/ca, sửa sau phát hành, tỷ lệ mù đạt (Mike, 2 giờ/quý).
- Bộ câu hỏi IR chuẩn theo ca (tiền lệ DDV) để user gửi; nạp tài liệu ĐHCĐ vào bước nguồn.
- Chạy lại nghiên cứu hiệu chuẩn khi đủ nhãn (~Q4/2027), không sớm hơn.

### 30 / 60 / 90 ngày
- **30 ngày**: xong P0-1…5; schema P1-1 chạy trên mọi DD mới; scorecard đăng ký.
- **60 ngày**: thẻ luận điểm cho mọi vị thế; mô-đun ngành; thí điểm 3 pha trên 3 mã; hậu kiểm FPT/NNC/VGS khi đóng.
- **90 ngày** (mùa BCTC Q4): đo lại — tỷ lệ qua vòng 1 ≥50%, 0 lần gửi lại, 100% số chốt có `skeptic_final`, kỳ scorecard đầu (chỉ mô tả).

### KHÔNG nên làm
- **Thêm dòng định giá hiển thị thứ năm.** Đã có 4 nền, 0 nền qua tiêu chí khoá trước; thêm nữa là thêm bậc tự do để chọn.
- **Chỉnh r/ERP/ngưỡng hoặc trộn tâm về phía giá cho "khớp thị trường".** Hiệu chuẩn: r chỉ dịch mức, không sửa độ phân tán; blend đã bị bác. Đó là neo giá bằng tham số.
- **Thêm vòng phản biện thứ 4–5.** Cầu chì 3 vòng đúng; sửa chất lượng vòng 1 (schema) mới giảm việc.
- **Tự động mua từ sổ giá** hoặc nới ứng viên khi chưa có scorecard.
- **Dựng hạ tầng OCR lớn** trước khi đo tỷ lệ lệch nhập đôi.
- **Backtest lớp phán đoán/5F** (không point-in-time).

## 4. Câu hỏi cần user quyết

1. **Số "đã sửa nhưng chưa được phản biện xác nhận lại" (16/36 mã) dùng tới đâu?** A: như hiện nay. B: chỉ hiển thị nhãn; cổng LAG đòi CONFIRMED (chặn nhiều lệnh LAG hơn). C: thêm một lượt "xác nhận cơ học" rẻ trước khi ghi sổ, cổng đọc enum. *Khuyến nghị C.*
2. **Chân trời của deal mua theo DD.** A: giữ ±10%/25 phiên cho mọi deal. B: tách hai loại — "trade" theo ngưỡng cứng và "giá trị" theo mốc luận điểm + điều kiện huỷ cơ bản. C: giữ ngưỡng, nhưng chạm stop thì bắt buộc kiểm luận điểm trước khi miễn/mua thêm. *Khuyến nghị B; tối thiểu C (áp ngay cho FPT).*
3. **Chi phí vốn: điểm 13,5% nằm trên dải nghiên cứu 12,3–13,4%, engine dùng 12,25%.** A: giữ 13,5%. B: giữ 13,5% làm tâm, báo thêm giá trị ở hai đầu dải + r ngầm của thị trường. C: thống nhất một khung cho DD và engine. *Khuyến nghị B — không chỉnh để khớp giá.*
4. **RONIC cho moat NARROW/NONE** (hai câu trái nhau trong cùng đoạn skill; thực hành 08–09/11 đã áp RONIC = Ke). A: terminal RONIC = Ke, "không trừ" chỉ áp cho biên giai đoạn dự báo. B: giữ RONIC của mô hình cơ sở. *Khuyến nghị A, ghi lại một câu duy nhất.*
5. **Ngưỡng −15% so với độ nhiễu của tâm (trung vị 10%).** A: giữ, không thêm gì. B: giữ ngưỡng, thêm bậc hiển thị (dưới đáy vùng + CONFIRMED = bậc 1). C: ngưỡng theo độ rộng vùng từng mã. *Khuyến nghị B.*
6. **Nhịp độ hay độ sâu.** A: giữ ~9 mã/tuần, một lượt. B: hai hạng — "nhẹ" (sàng lọc, không ghi sổ, không PDF) và "đầy đủ" (3 pha, CONFIRMED mới ghi sổ), trần số ca đầy đủ mỗi tuần (khớp tầng light/full đã khoá trước của bộ chọn mã). C: giảm số mã. *Khuyến nghị B.*

## 5. Giới hạn của review này
- Không kiểm tính đúng của bất kỳ định giá nào; không đọc trọn 36 REPORT (đọc sâu PAT, VCB, VLB, QTP; còn lại qua sổ, `correction_reason`, retro).
- Forward: N=33 mã, chân trời 1–16 ngày, một giai đoạn thị trường. Nhóm giá ≤0,92×tâm (13 mã) trung vị −3,8%, 4/13 tăng; nhóm ≥1,15×tâm (13 mã) trung vị 0,0%, 6/13 tăng. **Không kết luận được gì** về giá trị dự báo của vùng giá; cần ≥6 tháng.
- Chi phí, phân loại lý do sửa và đếm từ cấm đều lọc bằng từ khoá/regex — xấp xỉ; chi phí chưa gồm agent gọi trực tiếp.
- Không đọc transcript phản biện; nhận định "phản biện thấy giá" có bằng chứng ở PAT, là suy luận cho các ca khác. Trạng thái mù của các ca gần đây không kiểm được.
- Không mở PDF kiểm bằng mắt; không truy vấn BigQuery; không kiểm crontab thật (chỉ `cron_registry.md`).
- Quyết định user (ngưỡng, sizing, NPV=0, moat không trừ, r 13,5%) coi là cho trước; chỉ nêu chỗ chúng va với bằng chứng hoặc với nhau.
