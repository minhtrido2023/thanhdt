# arch-review vòng 2 (APPROVED) + quyết định của user — đề bài vòng 3

> Chép NGUYÊN VĂN prompt dispatch của Mike (job `Taylor_20261012_161627`, 2026-10-12 23:16 ICT).
> Vòng 2 = commit `e650f7ce0`, giữ ở nhánh `backup/nav-loss-brake-r2-managed-20261012` (bộ máy
> "phần bot quản lý" còn nguyên ở đó). Kết quả vòng 3: bus finding `nav-loss-brake-monitor-20261012-r3`.

LƯỢT SỬA CUỐI — nhánh mike feat/nav-loss-brake-monitor-20261012 @e650f7ce0, worktree mike/agents/Taylor/wt-lossbrake-1012. Vòng 2 đã được arch-reviewer APPROVED (B1–B9 đóng, 0 mục chặn, 12 mục không chặn K1–K12). User duyệt lượt này lúc 2026-10-12 21:31 ICT (decided_by: user) và ĐỔI một quyết định nền — đọc kỹ mục 1.

Việc đầu tiên: tạo nhánh giữ chỗ `backup/nav-loss-brake-r2-managed-20261012` trỏ vào e650f7ce0 (để phần sắp gỡ còn khôi phục được), và chép file này vào agents/Taylor/research/nav_loss_brake_20261012/arch_review_r2_and_user_decisions.md.

1. ĐỔI CƠ SỞ ĐO (user, nguyên văn: "DGC đã thuộc về discretionary sleeve. Và hệ thống quản lý luôn không còn phân ra bot quản lý riêng không tính DGC").
   ⇒ Cả ba phanh đo trên NAV TOÀN TÀI KHOẢN (giá đơn vị quỹ qua nav_unit_ledger.build_ledger) cho MỌI account. Không còn "phần bot quản lý". Việc account có excluded_tickers KHÔNG còn ảnh hưởng cơ sở đo (monitor dòng 635 và 1512 đang chọn "managed" theo excluded_tickers — bỏ).
   ⇒ GỠ HẲN bộ máy phần quản lý, không để lại nhánh chết: chuỗi excluded_value_history, managed_sleeve_flows + bản khai market_only (27 bản khai máy sinh không còn cần), ba bẫy sleeve (KL đổi / giá ±biên / lịch corp-action), excluded_ticker_exchange.json, --correct-excluded, bin/nav_loss_brake_backfill_excluded.py, gen_sleeve_declarations.py, các ca selfcheck + mutant + seed + mục runbook/registry tương ứng. Mục tiêu là monitor NHỎ hơn rõ rệt; báo số dòng trước/sau.
   ⇒ GIỮ NGUYÊN mọi kiểm tra chất lượng dòng NAV tổng đã qua soát: balance_ts trong [14:45 phiên, 09:00 phiên kế) cho cả dòng phiên lẫn mốc so (B1), cờ nav_is_estimate, thiếu dòng / thiếu phiên liền trước, file nav_gate_block rc=5/rc=6, nạp/rút qua account_cash_flows (dòng tiền treo ⇒ không đo được), bọc main (B7), khoá, BREACH_PROVISIONAL (B6), phanh episode (B4/B5), --write-backdated.
   ⇒ Hệ quả phải tự kiểm và báo: ngày cổ tức tiền của DGC (GDKHQ 2026-09-14, trả 09-25) trên NAV tổng có tạo bước nhảy giả không — chuỗi NAV vốn mark giá CUM và trừ khoản phải thu (coding_guidelines §21); nêu số thật của các phiên 09-11 → 09-28 cho ZaloPay.

2. LUẬT GIẢM TIN (user duyệt, giá trị do Mike đề xuất): khi lý do DUY NHẤT khiến một phanh "không đo được" là cờ nav_is_estimate (ở dòng phiên hoặc dòng mốc so) VÀ số tạm tính còn cách ngưỡng của phanh đó HƠN 2,0 điểm % ⇒ KHÔNG đẩy tin tối; trạng thái vẫn là không đo được kèm số tạm tính, hiện ở status.json và dòng kiểm sáng (không đỏ). Mọi ca khác đẩy như cũ: không có số, có thêm bất kỳ lý do nào khác, hoặc tạm tính cách ngưỡng <= 2,0 điểm %. Hằng số có tên, ghi rõ "user duyệt 2026-10-12 21:31 ICT". Ca kiểm ở đúng biên 2,00.

3. KHOÁ SỐ NGƯỠNG EPISODE: đã có trên WC main (merge c6e43899): macro_kill_switches.C_episode_drawdown_breaker.episode_drawdown_limit_pct = -0.15 — đúng tên anh/chị đặt ở EPISODE_NUMERIC_KEY. Xác nhận monitor đọc khoá số từ file thật; khoá số và câu chữ lệch nhau ⇒ không đo được, không chọn hộ.

4. CÁC MỤC K CỦA REVIEWER VÒNG 2 (số dòng theo e650f7ce0):
   K1 (882-890): nhánh chặn mà `return` không kèm số tạm tính. Phần sleeve biến mất theo mục 1; còn lại rà MỌI nhánh "không đo được": hễ sổ có dòng NAV của phiên thì phải có số tạm tính, và tạm tính <= ngưỡng ⇒ BREACH_PROVISIONAL (tin đỏ, có dòng lệnh BOT_STOP).
   K2: lệnh của người có thể làm monitor xanh mà không ai thấy. --ack-approval (1393-1415) không kiểm bản duyệt có tồn tại hay ngày <= hôm nay (reviewer ack được 2027-01-01, rc=0; sau một lần ack sai, episode báo OK +5% trong khi thật -16%). --close-episode trước lượt 22:05 của chính ngày đóng (712: d < closed_date) ⇒ phiên đó NO_EPISODE toàn xanh dù luỹ kế -14%. SỬA: mỗi lệnh ghi state (--open-episode, --close-episode, --ack-approval) gửi MỘT dòng vào trading_daily (ai, lý do, trước/sau) và hiện trong notes của lượt đo kế; ack phải kiểm file duyệt tồn tại và ngày <= hôm nay; phiên của chính ngày đóng vẫn đo với episode.
   K3 (1594, 1612-1616): từ chối --now khi state là state sống.
   K4 (1647; open ở 281): lấy khoá nằm ngoài lớp bọc ⇒ state-dir không ghi được thì traceback rc=1 (trùng nghĩa "phanh chạm"), không status, không tin. Đưa vào trong try, OSError đi qua đường crashed().
   K5 (1120-1126, 1159-1163): tin vào file sink trên state sống vẫn tính đã gửi và ghi khoá chống trùng. Ghi `sink` vào status.alert; tin đi sink KHÔNG được tính là đã gửi Discord.
   K6 (1214-1215): --health-line trả rc=1 cho cả BREACH, tạm tính vượt và không đo được. Cho BREACH / BREACH_PROVISIONAL một rc riêng; khối LOSSBRAKE trong ops_health_check.sh in đỏ, tách khỏi nhãn [WARN-ONLY] chung, vẫn không route autofix.
   K7: kb/cron_registry.md.proposed ghi sai "20 17 TRỐNG" — crontab thật có `20 17 * * 1-5 … c1_shadow_paper.py` (kb/cron_registry.md:80). Hai job độc lập nên giữ giờ, sửa hàng registry cho đúng.
   K8: thứ tự cài thêm bước "áp runbook + data_registry TRƯỚC khi merge commit ops_health". Thông báo thiếu sổ không được gợi ý tạo file rỗng để qua.
   K9: runbook thiếu các loại tin: THIẾU NGƯỠNG/cấu hình, dòng tiền TREO, "gộp nhiều phiên", rc=4 (khoá bận), và câu "chạy tay trước 21:50 là đo phiên TRƯỚC".
   K11: (749) so loanPackageId theo kiểu — chuỗi "1840" ra NO_EPISODE im lặng ⇒ chuẩn hoá trước khi so (§28). (388) payload không có khoá positions bị coi là rỗng ⇒ phải là "không đọc được". Dòng điểm vào episode chưa được kiểm giờ chụp. Ghi chú "đỉnh chưa phải giá chốt" (926-927) không được in ra.
   B5 còn lệch (776-782, 944-947): ngày duyệt không đọc được positions thì không thử mở ở phiên kế, và câu lý do nói "không có bản duyệt margin hợp lệ" trong khi bản duyệt có thật (§29) — sửa cả hai.
   Mutant reviewer còn sống cần ca giết: R56 (active_episode bỏ lọc account — §12). R29/R31/R39 biến mất theo mục 1 thì ghi rõ.
   K10 (CSV) biến mất theo mục 1. K12/N13/N14: ghi thành việc sau, không làm ở đây.

5. SINH LẠI toàn bộ tư liệu từ code mới: replay lịch sử cả hai account (bảng: phiên nào kêu, vì sao; số phiên đẩy tin TRƯỚC và SAU luật giảm tin), chạy thật phiên mới nhất, mutation, seed (nay chỉ còn gì thì nêu), ba file .proposed (cron registry, runbook, data_registry). Đối chiếu số NAV tổng 09/10 đã báo user: SpaceX -1,33% từ đỉnh, sâu nhất -10,29% (07-27), ngày tệ nhất -2,27% (07-20); ZaloPay -5,76%, sâu nhất -16,35% (07-27), ngày tệ nhất -3,58% (07-22).

CẤM như các vòng trước: merge, push, sửa crontab, tạo BOT_STOP, sửa data/trading_rules.json, sửa MIKE.md, sửa risk_monitor.py, đụng trading_bot/, đổi ngưỡng, ghi vào data/ sống. Commit ops_health_check.sh vẫn tách riêng và là commit CUỐI.

BÁO CÁO: bus finding topic nav-loss-brake-monitor-20261012-r3: commit; số dòng monitor + selfcheck trước/sau; từng mục 1–5 và từng K = đã làm / không làm + lý do; selfcheck ở env -u TZ + một múi giờ lạ (số thật); mutant còn sống; bảng replay; phiên 09-11 → 09-28 của ZaloPay; cần gì trong data/loss_brake khi cài (danh sách file + lệnh seed); phần chưa kiểm được.
