# BÀN GIAO — topic "CK holding VN — v4 sửa OCH/GAS + chốt dải HHS" (thread 1574659987832307762)
Từ Mike (topic CK v2/v3 1574627160235319398, 24/11/2026 12:3x ICT). Topic cũ dừng.
## User chốt 24/11 12:36 ICT
"Mở topic mới và làm option 1" ⇒ Taylor v4: sửa OCH/OGC (+GIC/LBM), khử dòng trùng GAS, ghi rõ 5 chỗ khác PREREG, tính lại hull + độ nhạy; skeptic vòng cuối; rồi HỎI user chốt dải HHS (Việc 1, phương án A: base 0% + dải độ nhạy có nguồn).
## Bối cảnh
v2 agents/Taylor/research/ck_holding_vn_20261124_v2/ ; v3 ck_holding_vn_20261124_v3/ (REPORT, PREREG, SKEPTIC_v3 REFUTED/medium: đầu trên +23% sai do OCH/OGC, sửa ⇒ ~+14%). Gợi ý skeptic: base 0% (nhãn đầu lạc quan), độ nhạy +6/+14/+37%, bỏ −12%. HHS rev7 REFUTED_OPEN đã merge; HHS forensic EXCLUDE.
## Job
Taylor (opus/medium, --thread 1574659987832307762) — prompt PROMPT.txt cùng thư mục; ra REPORT_CK_HOLDING_v4.md + bus finding ck-holding-vn-measure-v4-20261124. Job id: **Taylor_20261124_053704** (dispatch 24/11 12:37 ICT).
## Việc của phiên topic này
1. Poll: bin/jobs.sh claim-reply <job_id> (exit 3 = chưa xong) + status cùng lượt; ScheduleWakeup ~600s; progress thật vào topic.
2. Xong: verify (md5 LOCK + PREREG_v4 mtime trước calc; run1=run2=run_dna; đọc số), quant-skeptic ĐÚNG 1 vòng (Agent subagent_type=quant-skeptic; đưa REPORT_v4 + PREREG_v4 + SKEPTIC_v3; hỏi riêng: OCH tổng quát hoá có tạo lỗi mới không, đầu trên ~14% có đứng không, 'Khác PREREG' đầy đủ chưa), lưu SKEPTIC_v4, commit worktree riêng (git worktree add ../wt-1574659987832307762 -b session/1574659987832307762), merge --no-ff master (thư mục v4 trong main là untracked: diff -rq rồi xoá bản main trước khi merge).
3. Báo bảng v4 vào topic, so v3, dải đề xuất cho HHS + 0% nằm đâu, rồi HỎI user chốt dải. Skeptic vòng cuối này là vòng CUỐI — nếu vẫn còn lỗi nhỏ thì ghi vào hạn chế, đừng mở vòng 3 trừ khi lỗi đổi dải >3pp.
## KHÔNG
Không email; không rev8 HHS; không ghi dd_price_zones.json; không wire production/sizing; không đọc giá HHS/TCH/CRV.
