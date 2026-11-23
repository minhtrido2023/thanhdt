# BÀN GIAO — topic "Chiết khấu holding niêm yết VN → áp HHS" (thread 1574394938161111083)
Từ Mike (topic DD vòng 3, thread 1574365262965121136, 23/11/2026 19:10 ICT).
## User yêu cầu 19:00 ICT
"Mở topic đo CK holding niêm yết tại Việt Nam, rồi áp cho HHS."
## Bối cảnh
HHS = holding ~51% lợi ích CRV (TCH 58,31% HHS). rev6 giữ 2 bản CK holding 0% (tâm 13.969, DƯỚI vùng ở 9.700) / 27% (tâm 10.761, TRONG); 27% là kỳ vọng trục tự đặt, 0% cũng giả định; skeptic r4 CONFIRMED (0%) nhưng gọi đây là biến số mở lớn nhất (~23% tâm). Ledger HHS hiện: rev6 FIXED_UNVERIFIED (master 58a74db91), chưa nâng CONFIRMED vì user chưa chốt quy ước. HHS forensic EXCLUDE ⇒ ngoài candidate plan dù nhãn nào.
## Job đang chạy
Taylor_20261123_120407 (opus/medium, timeout 7200s, 1 job gộp A→B): A = đo CK holding holding niêm yết VN (thư mục agents/Taylor/research/ck_holding_vn_20261123/, prompt PROMPT.txt) → bus finding ck-holding-vn-measure-20261123; B = áp HHS rev7 + skeptic ĐÚNG 1 vòng (skeptic/r5.json) → LEDGER_PROPOSAL_HHS.json (rev7) + bus finding dd-continue-HHS-ck-20261123. Chưa tới giờ có kết quả (ước 30–60 phút).
## Việc của phiên topic này
1. Poll job (claim-reply; status; usage_limited ≠ chết; verify ARTIFACT: REPORT_CK_HOLDING.md, REPORT_rev7.md md5 khớp skeptic/r5.json, LEDGER_PROPOSAL_HHS.json, selfcheck). Kỷ luật ScheduleWakeup ~10 phút/lượt, progress thật vào topic này.
2. Khi xong: chạy `quant-skeptic` (bin/verify_finding.sh --claim hoặc Agent) lên phần A (đo CK holding: N holding, PIT, bẫy mcap, survivorship) — đây là tham số định giá, nên CHỈ nhẹ nhưng nên có; rồi áp sổ trong worktree riêng (`git worktree add ../wt-1574394938161111083 -b session/1574394938161111083`; mẫu script áp sổ /tmp/apply_v3.py — chỉ 1 mã HHS; rsync artifact nhẹ loại src/pdf/png; selfcheck sạch; xoá untracked trùng bản commit; merge --no-ff vào master).
3. HHS nhãn: r5 CONFIRMED ⇒ entry rev7 FIXED_UNVERIFIED bước 1 rồi `bin/dd_ledger_append_confirmed.py --ticker HHS --verdict .../skeptic/r5.json --write` (CHỈ khi user chấp nhận quy ước CK holding mới; nếu job báo "không đủ mạnh để đặt base" thì GIỮ base 0% và hỏi user). Báo bảng: CK đo được (khoảng, N), tâm rev6→rev7, vùng, nhãn so giá 9.700.
## KHÔNG
Không email; không tự chọn quy ước thay user nếu dữ liệu không đủ; không wire vào production/sizing; không ghi sổ trong lúc job chạy.
## Việc song song ở topic 1574365262965121136 (đừng đụng)
9 job "dd-continue-<MÃ>" (BSR CST CSV LLM PNJ SCL TTA VCB VLB) do Mike poll ở đó.
