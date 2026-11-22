# Kế hoạch nâng cấp quy trình DD — bản điều chỉnh sau khi đối chiếu review bên thứ ba (22/11/2026)

Nguồn: `dd-process-review-20261122.md` (Fable/high, ID F1–F25, P0–P3) + `Khuyen_nghi_Nang_cap_Quy_trinh_Due_Diligence.md` (bên thứ ba, 22/11). Bản bên thứ ba dựng trên đúng số liệu của review gốc (94 entry/36 mã, 14/16 trượt vòng 1, IQR 0,36 vs 1,06, QTP −41%, DRI +45%) và đồng ý với khuyến nghị của review gốc ở Q1, Q2, Q4, Q5, Q6. **Nó trình bày Q1–Q6 là "quyết định chính thức", nhưng chưa có `decided_by: user` — chỉ bạn chốt được.** Chưa sửa file nào; chờ "bắt đầu".

Đã kiểm lại: sổ có 36 mã, bản mới nhất của 20 mã CONFIRMED, **16 mã không CONFIRMED** (khớp F12); sổ chưa có trường `skeptic_final`/`method_version`.

## 1. Đối chiếu từng đề xuất của bên thứ ba

| Đề xuất | Kết luận | Lý do / chỉnh |
|---|---|---|
| Q1 `skeptic_final` + cổng LAG chỉ đọc CONFIRMED | **Nhận, thêm điều kiện** | Bật thẳng sẽ chặn 16/36 mã ở cổng LAG (tiền thật). Làm: enum → chạy bóng 1 tuần đếm số lệnh bị chặn → một lượt "xác nhận cơ học" rẻ cho 16 mã → mới nối cổng. Backfill ghi `FIXED_UNVERIFIED`, không gán CONFIRMED hộ. |
| Q2 tách 2 sổ (trade / value), bỏ stop 25 phiên cho value | **Nhận hướng, tách 2 bước** | Bỏ stop = đổi luật thoát lệnh tiền thật → bạn duyệt. Trước đó phải có `thesis_card` + giao thức rà luận điểm 48h. FPT: áp ngay phương án C (kiểm luận điểm trước khi miễn stop/mua thêm). |
| Q3 Ke phân tầng (T1 12,3–12,5 / T2 13–13,5 / T3 14,5–16) | **KHÔNG nhận** | (a) Thêm bậc tự do chưa hiệu chuẩn (hiệu chuẩn 11/11: r chỉ dịch mức, không sửa độ phân tán); (b) tự mâu thuẫn guardrail "không chỉnh r cho khớp thị trường"; (c) hạ Ke cho ngân hàng đầu ngành đúng nhóm đang giá cao = nguy cơ neo giá; (d) T3 14,5–16% vượt phép thử "Ke >~15% ⇒ lệch" (SKILL:35); (e) đụng luật r=13,5% gắn lãi huy động của bạn (03/11). **Giữ phương án B**: 13,5% + giá trị ở hai đầu dải 12,3–13,4 + r ngầm của thị giá. |
| Q4 terminal RONIC = Ke cho NARROW/NONE | **Nhận** | Trùng khuyến nghị review gốc; ghi một câu duy nhất. Schema: `terminal_ronic` là enum (`EQ_KE` / `ABOVE_KE_WIDE_MECHANISM`), không phải boolean — boolean mâu thuẫn moat WIDE. |
| Q5 bậc 1 = dưới đáy vùng + CONFIRMED + qua Hard Gate; hiển thị P25–P75 | **Nhận** | Chỉ là hiển thị/xếp hạng, không đổi ngưỡng −15%. |
| Q6 Quick Screen vs Full DD, trần 2–3 Full/tuần | **Nhận hạng nhẹ/đầy đủ; trần là của bạn** | Hiện ~9 mã/tuần do bạn giao; con số trần để bạn đặt. |
| Capex tuân thủ = dòng tiền ra (NPV<0), capex mở rộng NPV=0 | **Nhận, cần bạn xác nhận** | Đúng ca QTP (thiếu khí thải 3.485 tỷ). Không mâu thuẫn tinh thần luật 03/11 (đó là dự án tạo giá trị; chi tuân thủ bắt buộc không tạo doanh thu) nhưng là diễn giải mới của luật bạn đã chốt. |
| Chặn ghi sổ khi thiếu BCTC kiểm toán năm gần nhất (G5) | **Nhận, áp từ nay** | VLB rev1–2 đã ghi sổ khi thiếu BCTC 2025 kiểm toán — ca này xử lý theo bạn (gắn nhãn DRAFT hay giữ). |
| Hard Gate G1 (kiểm toán) | **Nhận, chỉ cho rổ HÀNH ĐỘNG** | Không chặn phân tích (luật 27/09: pháp lý/kiểm toán ⇒ vẫn phân tích, WARNING). Ngoại trừ/nhấn mạnh ⇒ không vào rổ Bậc 1. |
| G2 forensic/rating | **Đã có phần lớn** | Luật 1 (02/11) đã loại mã có cờ khi lên plan; lỗ hổng thật là danh sách ứng viên vẫn hiện HHS/DBC/TCH/MVC (4/7 ngày 20/11) ⇒ đẩy ra khỏi rổ hành động theo Q5. |
| G3 ADV thoát ≤3 phiên | **Chỉnh** | Ngưỡng phải tính theo KHỐI LƯỢNG VỊ THẾ thực tế ÷ ADV, không theo "MVC 0,9 tỷ" tuyệt đối: với NAV ~1,55 tỷ và vị thế ≤5% NAV, 0,9 tỷ/phiên vẫn thoát được trong 1 phiên. Đo trước khi chặn. |
| G4 ΣCFO/ΣLNST < 0,6 + phải thu tăng nhanh ⇒ chặn | **Hạ xuống CẢNH BÁO** | Ngưỡng 0,6 chưa hiệu chuẩn, mẫu nhỏ; dựng thêm ngưỡng chưa kiểm là đúng kiểu rule-accretion (F23). Bắt buộc có đoạn giải trình chất lượng lợi nhuận; cân nhắc chặn sau khi scorecard có số. |
| Hard Gate chạy **bóng** trước | **Thêm** | `dd_hard_gate.py` chạy trên 36 mã hiện có, báo số mã sẽ bị chặn ở từng cổng, rồi mới bật cưỡng chế. |
| Schema `assumptions.json` v1 | **Nhận, 4 chỉnh** | (1) bỏ `adv_60d` khỏi file khoá mù giá (dữ liệu thị trường lẫn vào pha mù) — Hard Gate chạy ở bước riêng; (2) `ke_band_*` đọc từ config, không hardcode; (3) trọng số kịch bản cho phép lệch nhưng bắt buộc `asymmetry_reason` (không ép 25/50/25); (4) biến thể theo loại hình (bank/BĐS/điện/mỏ) có field riêng, không dùng chung một khuôn. |
| Mù giá 3 pha + Reverse-DCF | **Nhận, thí điểm** | Pha A–B trùng P0-2/P0-3 review gốc. Reverse-DCF/r ngầm/Variant Perception chỉ là diễn giải Pha C và hiển thị, **không** thêm dòng định giá vào sổ/báo cáo (tránh phạm guardrail "không thêm dòng thứ 5" — chính bản bên thứ ba cũng nêu). Thí điểm 3 mã, so chi phí/số vòng. |
| `method_version` + `delta_fundamental`/`delta_methodology` | **Nhận** | Đánh trúng nguyên nhân ca DRI. Phần tách delta cần chạy lại giả định của rev cũ theo luật mới ⇒ làm cho mã đang giữ/trong rổ ứng viên; mã khác ghi "chưa phân tách". Cấm tín hiệu 30 ngày khi >50% delta do phương pháp: cảnh báo trước, cưỡng chế sau khi bạn duyệt. |
| Ma trận phơi nhiễm ngành/vĩ mô + trần tập trung | **Nhận phần hiển thị trước** | Hiển thị ngay (NNC–MVC–VLB cùng ngành đá). Trần số do risk-auditor đề xuất, bạn duyệt. |
| Thẻ luận điểm (`thesis_card`) | **Nhận, 1 chỉnh** | `drawdown_review_protocol` ≥15% là rà 48h, không phải stop; ngày hết hạn mốc kiểm có cron nhắc. Ưu tiên FPT. |
| 6 điều KHÔNG làm | **Giữ nguyên** | Trùng review gốc. |
| KPI "qua vòng 1 ≥50%" tháng 2 | **Chỉnh** | Hiện 2/16 ⇒ mục tiêu 90 ngày ≥50%; mốc 60 ngày ≥30% (đo, không ép). |

## 2. Kế hoạch triển khai (team Mike)

Quy ước: Taylor = dựng theo đặc tả (Sonnet/medium); phần chạm tiền hoặc cổng LAG qua arch-reviewer (Opus); thiết kế thang đo qua quant-skeptic; mỗi mục = lint/selfcheck, không thêm văn xuôi; mỗi merge đưa diff cho bạn trước.

### Đợt 0 — tuần 23–29/11 (cơ học, không đổi luật tiền thật)
| # | Việc | Cưỡng chế / thước đo | Chủ |
|---|---|---|---|
| W0-1 | Sổ giá: thêm `skeptic_final` (4 giá trị) + đường dẫn verdict JSON + `method_version`; backfill 36 mã (16 = FIXED_UNVERIFIED); watch in nhãn | `dd_price_zones_selfcheck` từ chối entry mới thiếu; 100% entry mới có | Taylor, arch-reviewer |
| W0-2 | Bóng cổng LAG: đếm lệnh LAG sẽ bị chặn nếu đòi CONFIRMED (CHƯA nối) | Báo cáo số liệu cho bạn | Taylor |
| W0-3 | `dd_blind_lint.py` (brief/fact pack không chứa giá, P/E, P/B, vốn hoá, mã); snapshot vĩ mô ra thư mục trung tính; script so giá chỉ chạy khi có file khoá md5 | rc≠0 chặn dispatch; 0 brief chứa token giá | Mike |
| W0-4 | Phản biện 2 chế độ (DD chung hai chiều mù giá + đòn "thiếu hạng mục": capex cam kết/tuân thủ, phát hành, quỹ KT-PL, ngoại trừ kiểm toán; fear-buy giữ nguyên) + runner ghi `skeptic/rN.json` | Bản nháp `.proposed` cho bạn duyệt định nghĩa agent | Mike |
| W0-5 | `send_dd_report_email.py`: grep luật 18/tên nội bộ + đối chiếu tâm/vùng md↔sổ + đòi CONFIRMED | Thử trên 10 bản gần nhất trước khi bật; 0 lần gửi lại | Taylor |
| W0-6 | Dọn 2 skill không đổi luật (xoá câu chết, gom luật hiện hành, đưa pha mù + khoá vào thứ tự bước, gỡ/dùng `--claim`) | arch-reviewer soát "không mất fact"; mỗi skill ≤~12KB | Mike |
| W0-7 | `dd_hard_gate.py` chạy BÓNG G1/G2/G3(theo khối lượng vị thế)/G4(cảnh báo)/G5 trên 36 mã | Bảng "mã nào trượt cổng nào" để hiệu chỉnh | Taylor |
| W0-8 | **FPT thesis audit** (ngay khi bạn đồng ý): rà luận điểm, mốc, điều kiện huỷ — trước khi quyết miễn stop/mua thêm | 1 trang, không đổi định giá | Taylor + skeptic |

### Đợt 1 — 2–4 tuần (sau khi bạn chốt mục 3)
- `assumptions.json` v1 (đã chỉnh) + `dd_assumptions_lint.py` (thiếu khoá ⇒ không gọi phản biện, không ghi sổ) — kỳ vọng tỷ lệ qua vòng 1 từ 2/16 lên ≥30% sau 60 ngày.
- `thesis_card` trong sổ cho 100% vị thế discretionary; cron nhắc mốc quá hạn; mẫu hậu kiểm khi đóng vị thế.
- Nối cổng LAG đọc `skeptic_final` (sau bóng + lượt xác nhận cơ học 16 mã).
- Mô-đun ngành (ngân hàng, BĐS/KCN, điện PPA, mỏ/đá) + nhập đôi 10–15 số từ ảnh scan (đo 10 ca đầu, công cụ PDF ra khỏi `/tmp`).
- Bảng phơi nhiễm ngành/nhân tố trong khối ứng viên; `dd_zone_scorecard.py` (bản phát hành ĐẦU TIÊN, mốc 1/3/6/12 tháng; đăng ký `paper_programs_registry.json`, chỉ mô tả).
- Hiển thị P25–P75 + số rev cạnh mức −15%; Bậc 1/Bậc 2 trong `dd_price_zone_watch.py`.

### Đợt 2 — tháng 2–3
- Thí điểm 3 pha + Reverse-DCF trên 3 mã Full DD; Quick Screen/Full DD.
- Bật cưỡng chế Hard Gate theo số liệu bóng; trần tập trung ngành do risk-auditor đề xuất.
- 90 ngày (mùa BCTC Q4): qua vòng 1 ≥50%, 0 lần gửi lại, 100% số chốt có `skeptic_final`, scorecard kỳ đầu (không chỉnh tham số theo nó). Hiệu chuẩn lại ~Q4/2027.

## 3. Cần bạn chốt (khuyến nghị sẵn — trả lời "duyệt theo khuyến nghị" là đủ)
1. **LAG đọc CONFIRMED** (Q1): bóng 1 tuần + xác nhận cơ học 16 mã rồi mới nối. *Khuyến nghị: duyệt.*
2. **Hai loại deal, value không còn stop 25 phiên** (Q2): trước hết thẻ luận điểm; FPT áp C ngay. *Khuyến nghị: duyệt B sau khi có thẻ; FPT = C.*
3. **Capex tuân thủ trừ thẳng khỏi giá trị** (sửa diễn giải luật 03/11). *Khuyến nghị: duyệt.*
4. **Chi phí vốn**: giữ 13,5% + hai đầu dải + r ngầm; KHÔNG Ke phân tầng. *Khuyến nghị: duyệt.* (RONIC NARROW/NONE = Ke: duyệt.)
5. **Hard Gate**: G1/G5 cho rổ hành động + ghi sổ, G4 cảnh báo, G3 theo khối lượng vị thế, chạy bóng trước. *Khuyến nghị: duyệt.* VLB (thiếu BCTC 2025 kiểm toán): gắn DRAFT hay giữ?
6. **Hạng nhẹ/đầy đủ** và con số trần Full DD/tuần (bạn đặt); quy tắc 30 ngày sau thay đổi phương pháp (cảnh báo trước).

Mọi thay đổi chạm cổng LAG/luật thoát lệnh sẽ qua arch-reviewer + diff cho bạn trước khi merge.
