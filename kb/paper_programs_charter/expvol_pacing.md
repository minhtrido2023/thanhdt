# Charter — P2 — mẫu số pacing theo KL KỲ VỌNG (expected-volume pacing) (`expvol_pacing`)

> File TỰ SINH từ `mike/kb/paper_programs_registry.json` bởi
> `mike/bin/paper_programs_daily_report.py`. **Đừng sửa tay** — sửa registry rồi chạy lại
> report. Đây là nơi giữ mục đích/phương pháp/tiêu chí nghiệm thu ĐẦY ĐỦ để báo cáo hàng
> ngày chỉ link tới, không paste lại mỗi ngày. (registry v3)

- **Người phụ trách (owner):** Taylor
- **Trạng thái:** active
- **Bắt đầu:** 2026-08-17 · **Kết thúc dự kiến:** 2026-09-15

## 🎯 Mục đích

Trần phụ `ceil_allow = 30% × KL ĐÃ khớp trong ngày` lấy mẫu số là đại lượng phản ánh thị trường KHÔNG CÓ TA ⇒ đầu phiên allowance ≈0 (ca thật TV1 2026-08-11: 12.400cp có sẵn dưới trần, bot khớp 100cp). P2 đổi mẫu số thành max(KL đã khớp, ADV20_cp × f(t)) + clamp fill fleet ≤50% tape THẬT. Câu hỏi của trial: trên lệnh THẬT của mọi book đi qua nhánh ADV20-paced, trần này có THẬT SỰ là ràng buộc BINDING không, P2 nới thêm bao nhiêu, và có ca nào phá trần an toàn 50% tape không? KHÔNG đo P&L (fill cao hơn chỉ tốt khi quyết định mua vốn đã đúng — câu hỏi khác).

## 📅 Nghiệm thu / mốc kết thúc

Review 2026-09-15 (thứ Hai). Điều kiện KÉP, lấy mốc ĐẾN SAU: (a) ≥20 phiên giao dịch kể từ 2026-08-17 (08-17 → 09-11), (b) ≥25 order-day ADV20-paced tích luỹ. Vì sao 20 phiên chứ không phải '≥4 tuần' chung chung như đề xuất gốc trong README: tần suất cơ hội đo THẬT trên plan 07-01→08-17 là 27 lệnh ADV20-paced / 10 ngày có lệnh, gần đây 1-2 lệnh/phiên (chương trình gom TV1) ⇒ 20 phiên kỳ vọng ~25-40 order-day. Thiếu order-day tại 09-15 = GIA HẠN, KHÔNG phải kết luận NO-GO (mẫu mỏng ≠ không có edge).

## ✅ Tiêu chí GO/NO-GO

- ⏳ (pending) AN TOÀN: 0 vi phạm trần 50% tape thật (recompute ĐỘC LẬP từ journal, không tin field đã ghi) và 0 dòng EXPVOL_SHADOW_ERR trong suốt trial — Đây là gate CHẶN: 1 vi phạm = dừng trial, không đàm phán. Cơ chế đo: bin/expvol_shadow_probe.py tính lại (F+X)/(V+X) ≤ 0,50 từ chính số đã log.
- ⏳ (pending) LIVE KHÔNG ĐỔI HÀNH VI trong suốt trial: 0 dòng EXPVOL_PACING trong journal của MỌI account live, và `_expvol_active()` = False trên SpaceX/ZaloPay/RocketX — Xác minh 2026-08-14 tại thời điểm wire: 3/3 account live cho _expvol_active()=False, 3/3 paper (main/ab_cross/ab_dip) cho True. Phải kiểm lại tại review — cấu hình có thể bị đổi giữa chừng.
- ⏳ (pending) CƠ HỘI CÓ THẬT: ≥10% số slice quan sát có bind=ceil, VÀ trung vị delta allowance trên nhóm đó > 0 (đo trên ≥25 order-day) — NO-GO nếu trượt: nếu ADV20-floor mới là thứ bind gần như luôn luôn, thì đổi mẫu số của ceil KHÔNG mua thêm được cổ phiếu nào — đóng P2, khỏi bàn tiếp về fill/giá.
- ⏳ (pending) CẬN TRÊN CƠ HỘI (ghép cặp, KHÔNG phải edge đã chứng minh): trên nhóm slice bind=ceil, KL khớp thật tới slice kế tiếp VƯỢT allowance nền ở ≥1/3 số order-day — Diễn giải bắt buộc mang theo: κ (phần tape mà lệnh nằm chờ giành được) KHÔNG neo được từ dữ liệu ta có (README §6.2) ⇒ đây là CẬN TRÊN của phần bị bỏ lỡ, không phải fill sẽ thu thêm. Nếu tape sẵn có luôn nhỏ hơn allowance nền thì trần không bóp gì thật và P2 vô nghĩa dù gate 3 đạt.
- ⏳ (pending) quant-skeptic CONFIRMED trên bằng chứng của trial → user sign-off RIÊNG mới flip `expected_volume_pacing_live_gate` sang False — Flip gate là cánh cửa DUY NHẤT đưa P2 lên tiền thật (selfcheck L4 khoá đúng bất biến này). Cờ `expected_volume_pacing_enabled` một mình KHÔNG đủ.

## ℹ️ Ghi chú vận hành

PHẠM VI THẬT — hẹp hơn mô tả trong dispatch, đọc từ code chứ không từ mô tả: nhánh ADV20-paced chỉ nhận CAPIT buy ∪ DISCRETIONARY_SPECIAL buy (`executor.py::_adv20_basis_for`). Lệnh BAL/LAG đi nhánh `max_participation × day_volume` KHÁC, P2 KHÔNG chạm. Trong phạm vi đó thì đúng là MỌI mã, không riêng TV1. || NGUỒN SỐ CỦA TRIAL LÀ JOURNAL LIVE, KHÔNG PHẢI PAPER — và đây là điều kiện thiết kế, không phải sự tiện tay: account paper `main` từ trước tới nay chỉ phát sinh lệnh `book="PROBE"` (342/342 lệnh), mà PROBE không vào nhánh ADV20-paced ⇒ bật cờ trên paper một mình sẽ đo được ĐÚNG SỐ 0. Cơ chế đo thật là `EXPVOL_SHADOW`: log-only trên account LIVE, ghi allowance mà P2 SẼ cho ở cùng lệnh/cùng tape/cùng phút, hành vi đặt lệnh KHÔNG đổi (mẫu ghép cặp hoàn hảo — cùng order, cùng tape, cùng giây). Cờ paper vẫn bật để đường thật được chạy end-to-end nếu sau này có plan paper phát sinh CAPIT/DISC. || CAVEAT MANG THEO TỪ VÒNG VERIFY 08-12 (commit 49c819e): công thức clamp đã deploy KHÁC bản đo trong nghiên cứu ⇒ lợi ích kỳ vọng thật là +4,6pp fill, KHÔNG phải +7,7pp như bảng §4 của README. An toàn không đổi. || ĐỘC LẬP HOÀN TOÀN với chương trình `order_book_execution_shadow` (P5, log L2 depth, bắt đầu 18/08): hai track song song, không chặn nhau, không dùng chung nguồn số. ⚠️ Tại 2026-08-14 entry của order_book MỚI CHỈ NẰM TRÊN NHÁNH `session/1521113190405247057` (commit f4e96f28), CHƯA merge vào master — người merge sẽ phải giải quyết xung đột JSON ở mảng `programs` (2 entry cùng thêm vào cuối). || P1 (trần no-chase động) đã LIVE từ 08-13 và KHÔNG thuộc phạm vi trial này.

## 🔍 Nguồn dữ liệu kiểm chứng

- `data/execution_logs/exec_{SpaceX,ZaloPay,RocketX}_*_journal.csv — event EXPVOL_SHADOW / EXPVOL_SHADOW_ERR`
- `mike/bin/expvol_shadow_probe.py (+ expvol_shadow_probe_selfcheck.py, 13 ca)`
- `expected_volume_pacing_selfcheck.py (59 ca, gồm mục L cổng LIVE + M đối chứng shadow)`
- `mike/agents/Taylor/research/thin_exec_20260812/README.md §P2 (nghiên cứu gốc, N=1.840 phiên-mã)`
