# arch-reviewer vòng 1 — nhánh `feat/nav-loss-brake-monitor-20261012` @074899796

> Chép nguyên văn từ dispatch của Mike (job `Taylor_20261012_120049`, 2026-10-12 19:00 ICT).
> Verdict: **NEEDS_CHANGES**, 9 mục chặn. Vòng 2 là vòng sửa DUY NHẤT.

VÒNG 2 (và là vòng sửa DUY NHẤT) — nhánh mike feat/nav-loss-brake-monitor-20261012 @074899796, worktree mike/agents/Taylor/wt-lossbrake-1012. arch-reviewer đã soát TRỌN nhánh một lần: NEEDS_CHANGES, 9 mục chặn. Sửa HẾT trong lượt này. Năm quyết định của user 2026-10-12 18:11 ICT giữ nguyên (chỉ cảnh báo, không BOT_STOP, giá chốt, ZaloPay theo phần bot quản lý, có phanh episode -15%). Số dòng dưới đây thuộc bin/nav_loss_brake_monitor.py @074899796 trừ khi ghi khác. Việc đầu tiên: chép file này vào agents/Taylor/research/nav_loss_brake_20261012/arch_review_r1.md và commit cùng nhánh.

Phần reviewer đã xác nhận đạt, GIỮ NGUYÊN: ranh giới quyền (chỉ ghi state-dir + sink, subprocess duy nhất notify_thread.sh, BOT_STOP chỉ là chuỗi in ra), selfcheck 110/110 ở 4 TZ, replay khớp từng byte.

## MỤC CHẶN

**B1.** evaluate() 578-614 chọn row/prev theo ngày, không đọc balance_ts ⇒ NAV chụp TRƯỚC giờ đóng cửa bị coi là giá chốt. Dữ liệu thật: nav_history_SpaceX 2026-07-02 chụp 09:46:35, 2026-08-24 chụp 04:49:59; ZaloPay 2026-08-24 04:50:08; ZaloPay 07-27 chụp 07-28T09:15:15. Fixture: D2 chụp 04:49, phiên D2 thật -6%, D3 +2% ⇒ D2 0,00% OK, D3 -4,10% OK, không tin nào. SỬA: dòng của ngày có phiên (cả row lẫn prev) phải có balance_ts trong [14:45 ngày đó, 09:00 phiên kế); ngoài khoảng ⇒ KHÔNG ĐO ĐƯỢC kèm giờ chụp đọc được. Dùng lại SESSION_CLOSE_ICT của account_cash_flows.py.

**B2.** Bẫy lịch corp-action fail-open hai chỗ. (a) _corp_events_today 359-373 trả ([], note) khi snapshot thiếu hoặc usable != True; sleeve_tripwires dòng 399 vứt note (thật: 1/39 phiên từ 08-13 không dùng được — 2026-10-02 FAILED; trước 08-13 không có file). (b) 373 và 399 chỉ kiểm sự kiện đúng ngày cur; chuỗi bắc cầu qua ngày thiếu thì sự kiện rơi vào ngày thiếu không ai kiểm, bẫy giá nới thành ±7,5%^n (384-397) ⇒ lãi giả + ĐỈNH GIẢ vĩnh viễn (ca DGC 80tr = 15,6% phần quản lý 513tr). SỬA: khi đang giữ mã loại trừ, snapshot thiếu/không usable của BẤT KỲ phiên nào trong (prev, cur] là một bẫy (KHÔNG ĐO ĐƯỢC tới khi khai market_only); quét sự kiện cho mọi phiên trong (prev, cur].

**B3.** build_chain 447-461: chuỗi phần quản lý bắt đầu muộn hơn mốc khởi điểm chỉ thêm warnings (chỉ vào status.json 713 và thân tin 765; health_line 837-842 không in) ⇒ âm thầm đặt lại đỉnh. Chạy thật không seed, --date 2026-10-09: SpaceX OK -0,07% đỉnh 10-08 (đúng là -1,33% đỉnh 07-01). SỬA: base_date not in excl ⇒ drawdown + episode KHÔNG ĐO ĐƯỢC. backfill_excluded_value.py:83-85 đang xoá CSV rồi mới ghi ⇒ phải ghi nguyên tử, chỉ THÊM ngày thiếu; và chuyển công cụ này ra bin/ (nó là công cụ vận hành bắt buộc, không phải research).

**B4.** detect_episode_opens 517-521 bỏ qua mọi bản duyệt nằm trong episode đang mở; run_account 695-703 chỉ kiểm chiều 'có vị thế mà không có episode'. Fixture: episode 1 vào 100, bán hết ở 125 không ai đóng; bản duyệt mới + vị thế 1840 mới vào 125, NAV về 105 (thật -16%) ⇒ báo OK +5,00%. SỬA: episode đang mở mà phiên d không còn vị thế gói vay ⇒ KHÔNG ĐO ĐƯỢC ('đóng episode?'); bản duyệt mới trong lúc episode còn mở phải được nêu ra.

**B5.** 696-698 (held, _ts, _why) + raw_positions 231-252 không kiểm ts ⇒ không đọc được positions, hoặc positions chụp trước phiên, bị coi là 'không có vị thế vay'. Fixture 1: D2 có vị thế 1840 không episode kêu đúng; D3 thiếu dnse_raw ⇒ NO_EPISODE, chuông tắt. Fixture 2: ngày duyệt chỉ có positions 04:58 ⇒ không mở; hôm sau KHÔNG ĐO ĐƯỢC vĩnh viễn vì không có --open-episode. SỬA: held is None hoặc ts trước 14:45 ⇒ phanh episode KHÔNG ĐO ĐƯỢC kèm why; khớp bản duyệt ngày d với vị thế xuất hiện ở d hoặc phiên kế; thêm --open-episode bắt buộc --opened-by + --reason.

**B6.** 610-612, 619-621, 645-647 + alert_text 757-772: số TẠM TÍNH đã vượt ngưỡng vẫn mang đầu tin KHÔNG ĐO ĐƯỢC (vàng, không có dòng lệnh BOT_STOP) — giống hệt 17/69 tin thường lệ; và nếu 22:05 đã gửi KHÔNG ĐO ĐƯỢC vì thiếu dòng, chạy lại khi dòng ước tính -8% đã có thì khoá dedupe (798) trùng ⇒ không gửi gì. SỬA: tạm tính <= ngưỡng là trạng thái RIÊNG (vd BREACH_PROVISIONAL): đầu tin đỏ, có dòng lệnh BOT_STOP, khoá dedupe riêng.

**B7.** Ba đường chết trước khi gửi và trước khi ghi status: dispatch_alerts 800 (_read_json(ctx.sent_path) ngoài try ở 1018), load_episodes 995, load_profiles 980; status.json chỉ ghi ở 1029. Fixture hai account đều -30%: alerts_sent.json cụt ⇒ JSONDecodeError, không status, 0 tin. SỬA: bọc main — mọi ngoại lệ vẫn ghi status KHÔNG ĐO ĐƯỢC và cố gửi một tin 'monitor lỗi' kèm lỗi thật (§29); sổ đã-gửi hỏng thì VẪN gửi (thà trùng).

**B8.** Selfcheck chưa khoá các bất biến trên nhánh managed (nhánh cả hai account đang chạy). Mutant của reviewer còn SỐNG, phải có ca giết: X05 (bẫy chỉ chặn một ngày thay vì tới khi khai) · X28/X28b (bỏ nạp/rút ngoài, hoặc bỏ kiểm dòng tiền treo, khỏi chuỗi quản lý) · X29 (thiếu managed_sleeve_flows.json coi như rỗng) · X33 (nuốt lỗi khi ghi chuỗi mã loại trừ) · X46 (account crash thì overall = OK) · X50 (active_nav thiếu giá mã loại trừ coi là 0) · X09/X54 (health bỏ qua send_error) · X07 (bỏ lọc ngày sự kiện) · X08 (dùng snapshot usable=False) · X18 (không lọc openQuantity>0) · X19 (lấy positions đầu thay vì cuối) · X20 (bỏ kiểm account của active_nav) · X21a (bỏ cận trên biên giá) · X45 (tắt cảnh báo gap/mốc muộn) · X02 (bỏ kiểm cờ ước tính ở episode) · X14 (ngày đóng dùng <=) · X15 (bỏ kiểm account trong bản duyệt) · X16 (bản duyệt tương lai vẫn mở) · X17 (bản duyệt cũ hơn episode đã đóng vẫn mở) · X43/X44 (bỏ EPS ở drawdown/episode) · X51 (nhận ngưỡng dương). Thêm ca phủ B1-B7. Báo lại danh sách mutant còn sống sau sửa, kèm lý do từng cái (tương đương / chưa giết).

**B9.** Chưa có artifact cho 'cron + bằng chứng chạy hằng ngày': thêm vào nhánh (KHÔNG cài) dòng cron đề xuất `5 15 * * 1-5` (crontab UTC = 22:05 ICT) có flock + log, cộng lượt thứ hai ~00:15 ICT để bắt dòng NAV backfill về muộn (idempotent); bản .proposed cho kb/cron_registry.md (§11) và kb/ops_runbook.md: mỗi loại tin thì người làm gì (khai sleeve flow, mở/đóng episode, vá chuỗi), ops_autofix ĐƯỢC và KHÔNG ĐƯỢC làm gì (không được tự chạy monitor khi chưa seed).

## MỤC KHÔNG CHẶN — sửa luôn nếu gọn, cái nào không sửa thì ghi rõ lý do

- **N1** (994-1029) --date khác phiên mặc định trên state sống ⇒ không ghi status, không gửi, trừ khi có cờ tường minh.
- **N2** (800-811, 690-692) thêm khoá flock cho cả lượt chạy và --close-episode.
- **N3** (786-792, 1022-1025) gửi lỗi thì lượt chạy sau cùng phiên phải thử lại (lượt 00:15 ở B9 dùng được cho việc này).
- **N4** (248, 277-289) positions cuối ngày rỗng ⇒ ghi 0 vĩnh viễn; cần đường đính chính có bằng chứng thay vì mổ CSV tay.
- **N5** (525) rec.get('revoked') coi chuỗi 'false' là đã thu hồi, lệch trading_bot/plan.py:1201-1202 — chuẩn hoá giống plan.py (§28).
- **N6** (206-211) regex ngưỡng episode nhận -0.5, -0.015, 1-0.15 ⇒ thêm kiểm khoảng; nếu trading_rules.json có khoá số thì ưu tiên khoá số (Mike đang xin user thêm khoá, CHƯA có — vẫn không được sửa file đó).
- **N7** (304-323, 88) active_nav chỉ có computed_at theo ngày; nêu giới hạn, đừng coi dung sai 0,1% là đã kiểm.
- **N8** (82) biên ±7,5% chỉ đúng HOSE — lấy biên theo sàn của mã.
- **N9** (395-397) .replace('7.5','7,5') làm hỏng giá in ra (47.500 thành 47,500).
- **N10** (570-572) lý do sai khi chuỗi chỉ có 1 dòng (§29).
- **N11** (ops_health_check.sh khối LOSSBRAKE) rc=1 gộp 'monitor lỗi khi đo' vào WARN-ONLY ⇒ tách: lỗi vận hành phải tới được autofix.
- **N12** real_run_and_dgc_case.txt + sink_real_run.jsonl sinh từ bản code cũ ⇒ sinh lại.
- **N13/N14**: ghi thành việc sau (strategy_fit_dashboard.py@aaaf60a3b:879-908 vẫn grep 'risk_monitor'; data/loss_brake phải có trong backup) — KHÔNG sửa dashboard ở đây.

## VIỆC ĐO THÊM (để user quyết, KHÔNG tự đổi luật)

17/69 phiên SpaceX và 12/66 ZaloPay ra tin KHÔNG ĐO ĐƯỢC vì cờ nav_is_estimate. Đo trên lịch sử: với mỗi dòng ước tính, số tạm tính lệch bao nhiêu so với số sau khi có NAV thật (nếu dữ liệu còn cho phép so; không so được thì nói rõ vì sao). User sẽ dùng số này để quyết có chỉ đẩy tin khi 'không có số' hoặc 'tạm tính cách ngưỡng dưới X điểm %' hay không. Giữ hành vi hiện tại (báo hết) cho tới khi user quyết.

## CẤM như vòng 1

merge, push, sửa crontab, tạo BOT_STOP, sửa data/trading_rules.json, sửa MIKE.md, sửa risk_monitor.py, đụng trading_bot/, đổi ngưỡng, ghi vào data/ sống. Giữ commit ops_health_check.sh tách riêng và là commit cuối (thứ tự cài reviewer yêu cầu: merge monitor → seed data/loss_brake + --replay khớp → chạy tay một tối với sink → cài cron → sau một đêm cron thành công mới merge khối ops_health).

## BÁO CÁO

bus finding topic nav-loss-brake-monitor-20261012-r2: commit; từng mục B1-B9 và N1-N14 = đã sửa / không sửa + lý do; selfcheck ở env -u TZ + một TZ lạ (số PASS/FAIL thật); mutant còn sống; replay lịch sử chạy lại (số phiên kêu thay đổi thế nào sau B1/B2/B3 — nêu từng ngày mới kêu và vì sao); kết quả việc đo thêm; phần chưa kiểm được (đường mở episode chưa từng có dữ liệu thật: 0 bản ghi loanPackageId 1840 trong dnse_raw, data/margin_approvals chưa tồn tại).
