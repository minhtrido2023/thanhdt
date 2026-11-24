# BÀN GIAO — topic "CK holding VN — dựng lại phép đo v2 (rồi chốt base HHS)" (thread 1574627160235319398)
Từ Mike (topic CK holding 1574394938161111083, 24/11/2026 10:3x ICT). Topic cũ dừng.
## User chốt 24/11 10:25 ICT
"Việc 2 DUYỆT; Việc 1 khi nào xong việc 2 thì mới chốt." ⇒ Việc 2 = dựng lại phép đo CK holding (bỏ giá con stale, thêm GEE+MSN, đo theo tháng, sửa VCSH/số CP). Việc 1 = base HHS: giữ 0% + dải 12–42% hay số khác — CHỜ user, chỉ hỏi SAU khi v2 xong + skeptic.
## Bối cảnh
v1: agents/Taylor/research/ck_holding_vn_20261123/ (REPORT_CK_HOLDING.md, SKEPTIC_A_quant-skeptic.md INCONCLUSIVE). HHS rev7 REFUTED_OPEN đã merge master e52dc7f00. HHS forensic EXCLUDE.
## Job
Taylor_20261124_032640 (opus/medium, --thread 1574627160235319398, timeout 7200s) — prompt PROMPT.txt cùng thư mục; ra REPORT_CK_HOLDING_v2.md + bus finding ck-holding-vn-measure-v2-20261124.
## Việc của phiên topic này
1. Poll: claim-reply (exit 3 = chưa terminal) + status cùng lượt; ScheduleWakeup ~600s; usage_limited ≠ chết (grep -l <id> bus/jobs/*); progress thật vào topic.
2. Xong: verify artifact (md5 2 lần khớp, LOCK_md5, đọc số), chạy quant-skeptic ĐÚNG 1 vòng (Agent subagent_type=quant-skeptic, đưa REPORT_v2 + SKEPTIC_A v1), commit trong worktree riêng (git worktree add ../wt-1574627160235319398 -b session/1574627160235319398), merge --no-ff master.
3. Báo bảng vào topic: CK v2 (trung vị, IQR, đường theo tháng, N), so v1, đủ mạnh làm base không → rồi HỎI user Việc 1 (base 0% vs dải vs số v2). KHÔNG tự dựng rev8 HHS trước khi user chốt.
## KHÔNG
Không email; không ghi sổ dd_price_zones.json; không wire production/sizing; không đọc giá HHS/TCH/CRV.
