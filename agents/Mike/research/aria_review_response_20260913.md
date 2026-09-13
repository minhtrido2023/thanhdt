# Đối chiếu bản review ARIA (09-11) với repo thật — Mike, 2026-09-13

## Kết quả đối chiếu từng claim
| Claim trong review | Đo lại 13/09 | Kết luận |
|---|---|---|
| mike_paseo git hỏng, tụt ~460 commit | `.git` trỏ `worktrees/wt-1521113190405247057` không tồn tại; HEAD 0e29acb8 KB v2611 vs production v2954 | ĐÚNG. Đã có 2 incident 09-12 + user gitignore 09-08. Paseo daemon (2 daemon: trido + hainguyen) vẫn mở agent "Research OpenCode" trong cây này, cập nhật 05:10 UTC 13/09 |
| ~16.000 .py, 1.002 ở root | 19.834 .py (trừ venv/.git), 1.004 ở root | ĐÚNG (số còn lớn hơn — đếm cả worktree) |
| dispatch.sh 1.740 dòng, ops_health_check 127KB | 1.759 dòng / 128,6KB, 1.791 dòng | ĐÚNG |
| bus/jobs 745 file, không dọn | 730 file, 8,5MB, từ 06-27 | ĐÚNG về sự kiện, SAI về rủi ro: 8,5MB/2,5 tháng không phải vấn đề |
| Incident 48 → 38 → 5 | 48 / 38 / 7 (+62 retro) | ĐÚNG xu hướng |
| 152 selfcheck | 86 file *selfcheck* trong bin/ (+ agents/) | Gần đúng |
| MTD T8 +5,03% / +7,15%, DD −1,67% | khớp monthly report 2026-08 | ĐÚNG |
| Residual reconcile +2,41% NAV SpaceX | reconcile_equity.py CHƯA có realized P&L (chỉ unrealized) — action #5 monthly report giao Taylor "trước báo cáo T9", chưa có bus/project theo dõi | ĐÚNG, và CHƯA ai làm |
| nav_history thiếu 4-5 ngày | SpaceX thiếu 6 phiên (07-21, 07-22, 08-06, 08-10, 08-25, 08-27), ZaloPay thiếu 5 (08-06, 08-07, 08-10, 08-25, 08-27) | ĐÚNG, không được theo dõi ở đâu |
| Đề xuất #4 "checker không hardcode chẩn đoán" | ĐÃ là luật §29 (08-28) + gate cơ học `bin/diagnosis_evidence_gate.py` (pre-commit, 08-29) | ĐÃ LÀM — reviewer không thấy vì đọc từ mike_paseo đông băng 08-28 |
| 3 HIGH finding money-path (get_nav, is_dead) | đang xử lý hôm nay: Taylor_20260913_050827 (batch 1), PHS + get_nav cờ OFF; patch loan_package apply chiều T2 | ĐANG LÀM |

## Nhận xét của Mike
1. Review chất lượng cao, đúng ~90% về sự kiện. Điểm mù duy nhất là chính reviewer thừa nhận: đọc từ mike_paseo nên hụt 2 tuần (§29, gate 08-29, retro 09-12).
2. Chẩn đoán "vận hành nhờ kỷ luật, chưa nhờ cấu trúc" là đúng và trùng với pattern retro 09-12 (worktree lệch canonical tái diễn lần 3).
3. Điểm review đánh giá đúng nhất: rủi ro đã dịch sang lớp giám sát/số liệu. Bằng chứng mới nhất là nav-xcheck ex-date vòng 2 NEEDS_CHANGES (09-12) — tự động hoá sai còn tệ hơn làm tay.
4. Điểm review đánh giá quá tay: bus/jobs (8,5MB) và SPOF host/broker — không phải việc cần làm bây giờ với 1 tỷ NAV.

## Đề xuất hành động (theo thứ tự)
A. (rẻ, làm ngay khi user duyệt) Số liệu NAV: (a) thêm realized P&L vào reconcile_equity.py để đóng residual 2,41% — Taylor + quant-skeptic; (b) backfill 6+5 phiên nav_history từ dnse_raw_*.jsonl cùng ngày nếu có, ghi nav_is_estimate nếu không; (c) risk-metrics tháng 8 qua risk-auditor. Đây là điều kiện để tin bất kỳ con số performance nào.
B. mike_paseo: KHÔNG xoá tự ý (paseo daemon còn dùng, 2 user). Đề xuất: đổi thành clone sạch theo dõi master (git clone --shared hoặc worktree hợp lệ) HOẶC đổi tên thành mike_paseo_frozen_20260828 và trỏ paseo sang mike/. Cần user chọn.
C. Tách production khỏi research: ĐỒNG Ý về hướng nhưng KHÔNG làm big-bang. Bước 1 rẻ: sinh danh sách file production từ crontab + import graph (`bin/selfcheck_scope_map.sh` đã có một nửa), ghi `kb/production_manifest.md`, dùng làm scope cho code-reviewer/selfcheck. Di chuyển vật lý chỉ khi manifest ổn định 1 tháng.
D. Chia nhỏ dispatch.sh/ops_health_check.sh: HOÃN. 3 tháng qua lỗi ở đó không đến từ kích thước file mà từ logic checker (§28/§29). Tách file không giảm lớp lỗi này, nhưng đổi 2 script đường găng có rủi ro hồi quy.
E. Bus/jobs, SPOF broker/host: ghi nhận, không hành động.
