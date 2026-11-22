# Nâng cấp quy trình DD — bản hành động FINAL (review vòng 2, 22/11/2026)

Đầu vào: `dd-process-review-20261122.md` (F1–F25), bản bên thứ ba, `dd-process-upgrade-plan-20261122.md` (Mike). **ĐK** = đã kiểm trên file/số đo hôm nay; **SL** = suy luận. Chưa sửa file nào khác; chưa có `decided_by: user` cho bất kỳ mục nào.

## 1. Phán quyết phản biện

1. **Đúng**: không coi Q1–Q6 của bên thứ ba là đã chốt; bác Ke phân tầng; hạ G4 xuống cảnh báo; bỏ `adv_60d` khỏi file khoá mù giá; Reverse-DCF chỉ hiển thị.
2. **Sai thứ tự (W0-1)**: đòi "đường dẫn verdict JSON" trước khi có runner ghi verdict (W0-4). ĐK: chỉ 19/58 thư mục `dd_*` có file tên skeptic/verdict ⇒ backfill đường dẫn là không làm được; enum phải suy từ `skeptic_status` văn bản tự do bằng luật cố định, đường dẫn để `null` cho entry cũ.
3. **Thừa (W0-2 "bóng 1 tuần")**: ĐK — 113 file plan tháng 10–11: lệnh MUA LAG chỉ có ở 26–29/10 và 09/11; **0 lệnh từ 10/11 tới 20/11**. Chờ 1 tuần sẽ đo ra 0. Thay bằng replay một lần trên plan lịch sử + đếm trên sổ. Hệ quả tiền thật của Q1 hiện ≈ 0, không phải "chặn 16/36".
4. **Thiếu file đích**: cổng LAG nằm ở repo NGOÀI `WorkingClaude/trading_bot/plan.py:1190` (gọi tại `bot_execute.py:611`, selfcheck `lag_dd_zone_gate_selfcheck.py`), và luật được lặp ở prompt DollarBill `bin/bq_freshness_check.sh:970`. Sửa một chỗ mà quên chỗ kia ⇒ ngân sách/egg của plan tính lệch.
5. **Trùng (W0-7 `dd_hard_gate.py`)**: G2 đã có `dd_flag_map` (`dd_price_zone_watch.py:331`); G3 đã có ADV20 trong watch và `adv_vnd()` + ngưỡng 10%/25% ADV (`trading_bot/due_diligence.py:59-62,232`); G4 đã có `earnings_quality` + `FLAG_CODES` trong `bin/lag_dd_pack.py:83-98`. G1/G5 không có trường máy đọc cho 36 mã ⇒ "chạy bóng" phải đọc tay. Script mới = accretion. Thay bằng phân bậc ngay trong watch.
6. **G3**: số học của Mike đứng được (5% × ~1,55 tỷ = 77,5 triệu = 8,6% ADV 0,9 tỷ, dưới ngưỡng cảnh báo 10%) nhưng NAV là số KB, tôi không mở được `nav_history` (SL); `discretionary_dd_pick.py` không có luật ADV nào; hai cơ sở ADV đang cùng tồn tại (watch: trung bình 20 phiên; `adv_vnd`: trung vị 3 tháng × giá thô). Dùng lại `adv_vnd` + công thức "số phiên thoát ở tỷ lệ tham gia 10–20%" của luật user 03/11 (`due-diligence/SKILL.md:36`), không đặt ngưỡng mới.
7. **Ke phân tầng — kết luận của Mike đúng, hai lý do yếu**: (a) hiệu chuẩn chỉ thử r ĐỒNG ĐỀU (`dd_vn_calib_20261111/REPORT.md:104`), không bác phân tầng; (d) phép thử SKILL:35 nói "Ke >15% cho MỌI doanh nghiệp", không cấm một tầng. Lý do mạnh Mike chưa nêu: T3 cộng 150–300 bps cho vốn hoá nhỏ **đếm đôi** với chiết khấu thanh khoản của luật 03/11. Kênh hợp lệ sẵn có: β peer (SKILL:35).
8. **Va luật user**: (i) "cấm tín hiệu 30 ngày" chặn đúng thứ luật 4 (02/11) cho phép (`dd-flag-rules-20261102.md:2`) ⇒ chỉ được là nhãn hiển thị; (ii) "đẩy mã có cờ khỏi rổ hành động" trái "discretionary = WARNING" (user 03/11) và luật 27/09 ⇒ xếp Bậc 2, không ẩn; (iii) "VLB gắn DRAFT" không cần: sổ append-only không có trường trạng thái, VLB rev2 chưa phản biện vòng 2 nên enum đã ghi `FIXED_UNVERIFIED`; thêm cờ `audited_fy_missing` là đủ.
9. **Bỏ nhầm từ bên thứ ba**: ngưỡng "sửa làm tâm dịch >5% hoặc đổi nhãn ⇒ phản biện lại" (định nghĩa cơ học duy nhất cho khi nào `FIXED_UNVERIFIED` được phép); trường `deal_type`.
10. **Thiếu**: số nền trước thay đổi; rollback cho file ngoài git (`~/.claude/skills`, `~/.claude/agents` — ĐK: không phải repo); sổ canonical đang có thay đổi chưa commit (94 entry/36 mã) trong khi worktree này 91/34; KPI "qua vòng 1 ≥50%" dễ đạt bằng cách phản biện nhẹ tay ⇒ phải đo kèm số lần sửa sau phát hành.

## 2. Danh sách hành động FINAL

### Nhóm A — làm ngay, không đổi luật tiền thật

| ID | Việc | Cưỡng chế | Owner · model | Công | Nghiệm thu | Rollback | Phụ thuộc |
|---|---|---|---|---|---|---|---|
| A0 | Commit sổ canonical; chụp số nền vào `kb/projects/dd-baseline-20261122.json`: rev/mã, tỷ lệ qua vòng 1, số lần gửi lại email, chi phí/ca, phân bố `skeptic_status` | Script chỉ đọc, chạy lại ra cùng số | Mike · haiku đếm, Mike kiểm | 1 giờ | File có 5 chỉ số + lệnh tái lập | Xoá file | — |
| A1 | **FPT thesis audit** 1 trang: luận điểm, mốc, điều kiện huỷ, dữ kiện mới từ 06/11; KHÔNG đổi định giá, KHÔNG đụng lệnh/stop | fundamental-skeptic đọc; trình user | Taylor · sonnet/medium; skeptic · opus/medium | 2–3 giờ | Mỗi điều kiện huỷ gắn nguồn; user nhận trước phiên kế | Không có side effect | User đang được hỏi miễn stop (`kb/memory/Mike.md`) — làm TRƯỚC mọi việc khác |
| A2 | Sổ giá: thêm `skeptic_final` (4 giá trị) + `skeptic_verdict_path` (cho phép null) + `audited_fy_missing`; backfill 36 mã bằng luật cố định: CONFIRMED chỉ khi câu vòng cuối ghi CONFIRMED và không có đính chính số sau đó, còn lại `FIXED_UNVERIFIED`; watch in nhãn | `dd_price_zones_selfcheck.py`: entry có `recorded_at` ≥ ngày bật phải có enum (mẫu `LOCK_REQUIRED_FROM`, dòng 30); test đột biến | Taylor · sonnet/medium; arch-reviewer · opus/medium | 0,5 ngày | Selfcheck 0 lỗi dưới `env -u TZ`; đếm backfill khớp 20/16 của review, lệch thì liệt kê từng mã | `git revert` (trường chỉ thêm; cổng LAG chưa đọc) | A0 |
| A3 | Replay bóng (thay W0-2): script chỉ đọc chạy lại mọi lệnh MUA LAG trong `data/trade_plans/` + 36 mã hiện tại qua luật "đòi CONFIRMED" | Không nối cổng | Taylor · sonnet/medium | 2 giờ | Bảng: lệnh/mã bị chặn thêm so với cổng hiện tại | Xoá script | A2 |
| A4 | Runner phản biện ghi `<dir>/skeptic/rN.json` (verdict, vòng, md5 báo cáo) — script ghi, không để agent tự ghi; brief phản biện không chứa giá | Sau A4 bật: selfcheck đòi path khác null cho entry mới | Mike · sonnet/medium | 0,5 ngày | 2 DD kế tiếp có file; path trỏ file tồn tại | `git revert`; path lại cho phép null | A2 |
| A5 | `dd_blind_lint.py` + snapshot vĩ mô ra thư mục không chứa mã (sửa F7) | rc≠0 chặn dispatch; thử trên 10 brief cũ | Mike · sonnet/medium | 0,5 ngày | Bắt được brief PAT lượt 1–2; 0 báo giả trên brief sạch | Tắt bằng hằng số | — |
| A6 | Lint trong `~/.claude/skills/dd-investor-report/scripts/send_dd_report_email.py`: grep luật 18/tên nội bộ + đối chiếu tâm/vùng md↔sổ; **chỉ cảnh báo** với `skeptic_final≠CONFIRMED` | `--dry-run` rc≠0; thử 10 bản gần nhất trước khi bật chặn | Taylor · sonnet/medium | 0,5 ngày | Bắt được ca NNC lệch sổ; ≤1 báo giả/10 bản | Sao lưu `.bak_20261122` (file ngoài git) | A2 |
| A7 | Phân bậc hiển thị trong `dd_price_zone_watch.py` (thay W0-7): Bậc 1 = dưới đáy vùng + CONFIRMED + không cờ + thoát ≤3 phiên ở 10% `adv_vnd` theo khối lượng vị thế; Bậc 2 = còn lại, vẫn hiện; thêm số rev + cột ngành (NNC–MVC–VLB) | `dd_price_zone_watch_selfcheck.py` thêm ca; ngưỡng −15% không đổi | Taylor · sonnet/medium | 0,5 ngày | Chạy lại ngày 20/11: HHS/DBC/TCH/MVC ở Bậc 2, không mất mã nào | `git revert` | A2 |
| A8 | Sửa nhỏ 2 skill: xoá câu chết F22a, sửa đường dẫn snapshot, trỏ template mới | arch-reviewer soát diff | Mike | 1 giờ | Diff ≤30 dòng, không đổi luật | Sao lưu `.bak` | — |

Tổng tuần 1 ≈ 3 ngày công agent. Chỉ A2 và A6 chạm file dùng chung ⇒ không chạy song song với DD đang dở (VCB/PAT/VLB vừa ghi sổ hôm nay).

### Nhóm B — chờ user quyết

| ID | Việc | Quyết định mở khoá | Owner · model | Công | Nghiệm thu / rollback |
|---|---|---|---|---|---|
| B1 | Nối cổng LAG: hằng `LAG_DD_REQUIRE_CONFIRMED` (mặc định False) trong `plan.py:1190` + selfcheck + sửa prompt `bq_freshness_check.sh:970` cùng lượt | D1 | Taylor · opus/medium; arch-reviewer · opus/high (chạm tiền) | 0,5 ngày | Selfcheck hiện 28/0 + ca mới; rollback = đổi hằng |
| B2 | Luật "tâm dịch >5% hoặc đổi nhãn ⇒ phản biện lại; nhỏ hơn ⇒ xác nhận cơ học" + lượt xác nhận cho 16 mã (ưu tiên mã đang giữ/Bậc 1) | D1 | Taylor · sonnet; skeptic · opus/medium | ~16 lượt, đo chi phí 3 ca đầu | Tỷ lệ CONFIRMED trên sổ; dừng nếu >3 USD/ca |
| B3 | `thesis_card` + `deal_type` trong sổ cho vị thế discretionary; cron nhắc mốc; mẫu hậu kiểm. Bỏ stop 25 phiên cho deal giá trị = sửa `data/discretionary_exit_rules.json` từng vị thế, có `approval_ref` | D2 | Taylor · sonnet; arch-reviewer · opus/high cho phần exit | 1,5 ngày | 100% vị thế có thẻ; rollback = khôi phục JSON |
| B4 | `assumptions.json` v1 (4 chỉnh của Mike) + `dd_assumptions_lint.py`; gồm phân loại capex, `terminal_ronic` enum, `method_version` suy từ bảng ngày đổi luật, `audit_opinion`, G5 | D3, D4, D5 | Taylor · opus/medium thiết kế; sonnet dựng; quant-skeptic soát | 2 ngày | Lint chạy trên 5 ca cũ, ghi số ca trượt; 2 tuần đầu chỉ cảnh báo |
| B5 | Viết lại 2 skill (25,6KB + 36,1KB) thành "luật hiện hành" + file ext — làm MỘT lần sau D2–D5 | D2–D5 | Mike · opus/medium; arch-reviewer "không mất fact" | 0,5 ngày | Bảng đối chiếu từng luật user cũ→mới; rollback `.bak` |
| B6 | Tách chế độ phản biện DD chung trong `~/.claude/agents/fundamental-skeptic.md` (thêm đòn "thiếu hạng mục") | User duyệt bản `.proposed` | Mike · opus/medium | 3 giờ | Thử lại ca QTP: có bắt thiếu capex khí thải không |
| B7 | Mô-đun ngành, nhập đôi số scan, `dd_zone_scorecard.py`, thí điểm 3 pha, Quick/Full | D6; sau B4 | Taylor; quant-skeptic soát scorecard | tháng 2–3 | Theo review gốc P1-3…P2-1 |

### Nhóm C — không làm

- Ke phân tầng T1/T2/T3 (đếm đôi thanh khoản, va luật 03/11). Giữ 13,5% + hai đầu dải; r ngầm chỉ ở phần diễn giải.
- `dd_hard_gate.py` riêng và G4 dạng chặn (trùng cơ chế có sẵn, ngưỡng 0,6 chưa hiệu chuẩn).
- Chờ bóng 1 tuần cho cổng LAG.
- Cấm tín hiệu 30 ngày dạng cưỡng chế; chỉ in nhãn "tâm đổi chủ yếu do phương pháp" khi có `method_version`.
- Trạng thái DRAFT riêng cho VLB; ẩn mã có cờ khỏi danh sách ứng viên.
- Tách `delta_fundamental`/`delta_methodology` hồi tố cho mọi mã (cần chạy lại mô hình cũ; chỉ làm khi mã đang giữ đổi tâm >15%).
- Sáu điều "không làm" của review gốc.

## 3. Lịch

- **Tuần 1 (23–29/11)**: A0 → A1 (ngày đầu) → A2 → A3/A4/A5 song song → A6, A7, A8. Trình user D1–D6 kèm số của A3.
- **Tuần 2–4**: B1, B2, B3, B4 (chế độ cảnh báo), B6. Mốc 15/12: user xem lại cổng LAG — trình cùng lúc kết quả B1.
- **Tháng 2–3**: B5, B7; bật chặn lint B4 nếu báo giả ≤10% trên DD thật.
- **Đo lại**: 22/12 và 22/02/2027 so với A0 — vòng/ca, tỷ lệ qua vòng 1 **cùng với** số lần sửa sau phát hành, số lần gửi lại, tỷ lệ CONFIRMED. Scorecard chỉ mô tả; hiệu chuẩn lại ~Q4/2027.

## 4. Quyết định user cần chốt

- **D1 — LAG đòi CONFIRMED**: duyệt, bật sau A3. Từ chối ⇒ cổng tiền thật tiếp tục nhận tâm chưa được xác nhận lại; nhãn vẫn hiện.
- **D2 — Hai loại deal**: duyệt `thesis_card` cho mọi vị thế; việc bỏ stop 25 phiên quyết từng vị thế sau khi có thẻ (FPT: đọc A1 rồi quyết). Từ chối ⇒ giữ ±10%/25 phiên, vẫn lệch chân trời định giá.
- **D3 — Capex tuân thủ là dòng tiền ra** (bổ sung luật 03/11, chỉ cho chi bắt buộc không tạo doanh thu). Từ chối ⇒ ca kiểu QTP (tâm −41%) có thể lặp.
- **D4 — Chi phí vốn + RONIC**: giữ 13,5% gắn lãi huy động, báo thêm hai đầu dải 12,3–13,4%; NARROW/NONE terminal RONIC = Ke. Từ chối ⇒ hai câu trái nhau trong SKILL còn nguyên, B5 không viết được.
- **D5 — Thiếu BCTC kiểm toán năm gần nhất**: vẫn ghi sổ kèm cờ `audited_fy_missing`, không vào Bậc 1, cổng LAG coi như chưa có DD. Từ chối ⇒ giữ như hiện nay (VLB không đổi).
- **D6 — Quick/Full**: duyệt hai hạng; user đặt trần Full/tuần (hiện ~9 mã/tuần). Từ chối ⇒ dời thí điểm 3 pha vì không đủ thời gian mỗi ca.

## 5. Rủi ro còn lại & giới hạn review

- Backfill enum đọc văn bản tự do: sẽ có ca mơ hồ (PNJ, PAT, QTP, SZL) — liệt kê để Mike xác nhận tay, không tự gán CONFIRMED.
- Số "19/58 có file verdict" đếm theo tên file, xấp xỉ. Số "0 lệnh LAG từ 10/11" đếm trên file plan; chưa đối chiếu nhật ký executor.
- NAV ~1,55 tỷ lấy từ KB, chưa kiểm trên sổ NAV; G3 phải tính riêng từng tài khoản.
- A6, A8, B5, B6 sửa file ngoài git: rollback chỉ bằng bản sao lưu.
- Lint/schema mới có thể tự thành accretion: mỗi cổng mới chạy chế độ cảnh báo 2 tuần và phải có số báo giả trước khi chặn.
- Không kiểm tính đúng của định giá nào; không đọc transcript phản biện; không truy vấn BigQuery; không kiểm crontab.
- D1–D6 ĐÃ có `decided_by: user` (22/11/2026 19:07 ICT, "theo khuyến nghị"); Nhóm B chạy tuần tự.
