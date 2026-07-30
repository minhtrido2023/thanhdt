---
kind: incident
date: 2026-07-11
topic: dispatch-hard-timeout-4-jobs-fable
title: >-
  2026-07-11 — 4 lần dispatch bị hard-timeout giữa việc nặng (Fable-model, đa bước) dù fix "heartbeat-aware deadline" (2026-07-09) đã có hiệu lực — không mất dữ liệu lần nào, nhưng tần suất cho thấy trần thời gian vẫn chưa đủ cho khối lượng việc thật
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-11 — 4 lần dispatch bị hard-timeout giữa việc nặng (Fable-model, đa bước) dù fix "heartbeat-aware deadline" (2026-07-09) đã có hiệu lực — không mất dữ liệu lần nào, nhưng tần suất cho thấy trần thời gian vẫn chưa đủ cho khối lượng việc thật

**4 lần xảy ra trong đúng 1 ngày lịch ICT 2026-07-11** (job board `bus/jobs/*.json`, tất cả
`attempt=2/2, exit_code=124`):
1. `Winston_20260710_170615` (00:16–00:26 ICT — job_id mang giờ UTC dispatch nên tên có
   `_170615` nhưng thực chạy đã sang ngày lịch ICT 07-11) — audit DT5G pipeline (EW-leg
   path bug). Nối tiếp bởi `Winston_20260710_173031` (dispatch 00:30 ICT, done 00:38 ICT) —
   hoàn tất sạch, quant-skeptic CONFIRMED 02:24:53Z.
2. `Taylor_20260711_043508` (11:50–12:05 ICT) — fix HIGH/MEDIUM audit money-path freshness.
   Nối tiếp bởi `Taylor_20260711_051033` (done) — prompt tiếp tục ghi rõ "đã commit thật:
   F1 (`a7668f3`), F6 …" trước khi bị giết, không mất việc.
3. `Winston_20260711_043611` (11:51–12:06 ICT) — fix MEDIUM audit freshness 8L/production.
   Nối tiếp bởi `Winston_20260711_051109` (done, selfcheck 45/45, commit `4111009`).
4. `Taylor_20260711_114557` (18:55–19:16 ICT) — bắt đầu Phase 0 re-tune SIGNAL_V11 trên
   fa_ratings_8l. Nối tiếp bởi `Taylor_20260711_121933` (done) — prompt tiếp tục tự ghi
   "công việc QUÁ NẶNG cho khung giờ đó, không phải lỗi cơ chế".

**Cơ chế phục hồi hoạt động ĐÚNG cả 4/4 lần — 0 mất dữ liệu:** mỗi lần, Mike (trong phiên
sống) tự phát hiện job `timeout`, đọc lại working memory + commit thật của agent, rồi
dispatch job MỚI với prompt "TIẾP TỤC (trace `<job_id_cũ>`) — đừng làm lại từ đầu", đúng
quy trình `MIKE.md` §Quy chuẩn bắt buộc mục 2 (verify artifact, không tin status tự báo).
Cả 4 lần đều xác nhận công việc trước đó ĐÃ commit thật một phần trước khi bị giết.

**Đây KHÔNG PHẢI tái diễn của bug `2026-07-09 (tối)` (agent ĐÃ XONG bị giết ngay trước khi
kịp return)** — bug đó đã fix bằng heartbeat-aware deadline (`_hb_aware_timeout`, tối đa 3
lần gia hạn `DISPATCH_HB_MAX_EXTENSIONS=3`, trần tuyệt đối `TIMEOUT×(N+1)`) và verify e2e
4/4, không có bằng chứng nào cho thấy fix đó regressed. Đây là dạng KHÁC: agent **còn đang
làm việc thật** (chưa hoàn tất hết danh sách fix/phase) khi chạm TRẦN TUYỆT ĐỐI của chính
cơ chế gia hạn đó — với `TIMEOUT` mặc định 600s và 3 lần gia hạn, trần mỗi attempt là
~2400s (40'), nhân 2 attempt (`--retries` mặc định 1) là tối đa ~80' — vẫn không đủ cho các
task Fable-model nhiều bước (fix 7 phát hiện HIGH/MEDIUM, hay 1 phase audit+backtest đầy
đủ) chạy trong 1 lần dispatch.

**Còn hở — residual risk cụ thể:** cơ chế phục hồi hiện tại phụ thuộc HOÀN TOÀN vào Mike
đang ở phiên sống, chú ý thấy job `timeout` trên job board, và tự tay soạn prompt "TIẾP
TỤC" đúng ngữ cảnh. Không có cơ chế TỰ ĐỘNG làm việc này (khác với `resume_pending.py` —
cơ chế đó CHỈ xử lý usage-limit, không xử lý timeout-vì-việc-nặng). Nếu 1 trong 4 lần này
xảy ra khi KHÔNG có Mike tương tác sống theo dõi (vd trong 1 job headless dài không có
người canh) → job đó sẽ kẹt ở `timeout` vô thời hạn, không ai tự nối tiếp.

**Đối chiếu với tuyên bố "Pattern A coi như ĐÃ ĐÓNG, cần quan sát thêm ~1 tuần" (RETRO
2026-07-09):** 07-10 (ngày quan sát đầu tiên) không có lần timeout nào (0/0 trong bus job
board), nhưng 07-11 (ngày quan sát thứ 2) đã có NGAY 4 lần. Tuyên bố "đóng" cho lớp lỗi cụ
thể (giết-nhầm-agent-đã-xong) vẫn ĐÚNG — không có bằng chứng nào cho thấy lớp đó tái phát.
Nhưng cửa sổ quan sát "1 tuần sạch" mà 07-09 đặt ra **CHƯA ĐẠT** — vì đây là 1 biểu hiện
KHÁC của cùng họ pattern (job nền chết giữa lúc còn sống/còn việc, cần con người phát hiện
+ can thiệp tay) tái xuất hiện ngay trong tuần quan sát. Theo đúng bước 5 của quy trình
retro: đây là tín hiệu quan trọng cần prevention MẠNH HƠN, không chỉ ghi thêm 1 dòng nhận
xét — xem đề xuất cụ thể ở entry RETRO tổng hợp bên dưới.
