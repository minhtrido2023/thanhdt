# BÀN GIAO — topic "DD nhãn so-với-lịch-sử (E) + đo hồi tố giá/tâm + radar EPS chuẩn hoá" (thread 1574625384438308914)
Từ Mike (topic DD vs Radar 1574470111769796668, 24/11/2026 10:2x ICT). Topic cũ dừng.
## User chốt 24/11 10:1x ICT
Duyệt đề xuất E (nhãn 'so với lịch sử' cho DD) và 2 việc còn chờ: (M) script đo hồi tố giá/tâm → lợi suất 3/6/12 tháng (mốc đánh giá 2027-03-31); (R) bật dòng EPS chuẩn hoá của radar ở khối NỘI BỘ, ZaloPay trước, SpaceX CHỜ user quyết.
Bối cảnh: agents/Taylor/research/dd_vs_radar_20261124/MEMO_MIKE.md + rerun/REPORT_R2.md/REPORT_D2.md + rerun/QUANT_SKEPTIC_R2_D2.md. Luật 4 GIỮ NGUYÊN (không đổi). Mọi thứ display-only/chẩn đoán.
## Job đang chạy (--thread 1574625384438308914; dispatch 24/11 10:2x ICT)
- E (opus/medium) = Taylor_20261124_031942 → bin/dd_history_label.py + selfcheck + REPORT_E.md (nhãn trên lịch sử CỦA CHÍNH MÃ, tercile, dải [fade,hold]; worktree, KHÔNG merge)
- M (sonnet) = Taylor_20261124_031944 → bin/dd_forward_outcome.py + outcomes.csv/summary.md; cron THÁNG ở dạng đề xuất (chưa cài)
- R (sonnet) = Taylor_20261124_031947 → bật norm5 chỉ nội bộ theo call-site; SpaceX byte-giống; worktree, KHÔNG merge
Prompt: PROMPT_E.txt / PROMPT_M.txt / PROMPT_R.txt cùng thư mục (agents/Taylor/research/dd_label_20261124/).
## Việc của phiên topic này
1. Poll 1 lượt cho cả batch: claim-reply từng job (exit 3 = chưa terminal) + status cùng lượt; ScheduleWakeup ~600s; usage_limited ≠ chết (grep -l <id> bus/jobs/*). Post progress thật vào topic.
2. E xong: verify (md5 2 lần, selfcheck dưới env -u TZ + TZ=Asia/Ho_Chi_Minh, nhân quả/PIT), chạy quant-skeptic ĐÚNG 1 vòng (Agent subagent_type=quant-skeptic, đưa REPORT_E + QUANT_SKEPTIC_R2_D2.md). Sau đó duyệt diff, merge master (worktree riêng), post bảng nhãn cho user. Đề xuất vị trí hiển thị trong skill (một dòng) → CHỜ user.
3. M xong: verify look-ahead/PIT, n độc lập; post kết quả TRUNG THỰC (hầu hết 'chưa đủ kỳ'); merge sau duyệt; cron tháng: tra kb/cron_registry.md (§11), cài crontab CHỈ sau khi xem diff (user đã duyệt làm script, chưa nói rõ cron ⇒ hỏi user 1 dòng hoặc đặt ở dạng đề xuất).
4. R xong: duyệt diff, kiểm SpaceX/email byte-giống trước/sau, rebuild cache, merge repo ngoài (/home/trido/thanhdt) sau khi sạch; báo user dòng hiển thị hôm nay + nơi nào bật. KHÔNG bật ở báo cáo gửi nhà đầu tư.
5. Cập nhật bin/remember.sh Mike; KHÔNG email; KHÔNG tự đổi luật 4/DD/sổ.
