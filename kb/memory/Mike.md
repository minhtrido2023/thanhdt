# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (cập nhật 2026-10-05 11:55 ICT)
- Broker corp-action PRIMARY: branch feat/broker-primary-20261003 HEAD 9e4d24c9, CHƯA merge, shadow trên master không đổi. Chờ log shadow T2 05/10 19:25 ICT + T3 06/10, rồi user quyết r5 hay merge có điều kiện. NB: dispatch vòng 4+ cùng chuỗi nay bị exit 7 → cần DISPATCH_ROUND_CAP_OVERRIDE=1 (phiên tương tác) khi user duyệt vòng 4.
- Feed vendor corp_action_daily: DEAD (asof 02/10). Chưa xác minh 03/10–04/10.

## Đã xong 05/10 (user duyệt)
- TPB ok (+--verify tính cash-leg). Trứng vàng = tương đương tiền.
- Round-cap polish vào dispatch.sh (exit 7) MERGED mike master; skill dispatch-routing đã cập nhật.
- 3 finding code-review (bot_execute/capit_episode) MERGED outer main.
- Deposit: Big-4 12M cùng NH online/quầy → lấy cao nhất (giữ 6,8). CCTG chuẩn = 12M cao nhất Big-4: anchor 2026-10-05 = 7,4% (REBASE từ 6M 7,5), trend-check đã ack cặp 7,5→7,4; prompt cron tuần đã đổi.

## Mốc
- 05/10 19:25 ICT: shadow broker lần đầu (log, data/corp_action_broker_ledger, bus corp-action-broker-shadow-*). 20:50 plan_position_drift_check lần đầu; 21:00 báo cáo plan khối vị thế.
- Thứ Hai 12/10 08:05 ICT: cron deposit/CCTG tuần chạy prompt MỚI lần đầu → kiểm Winston ghi đúng 12M cao nhất, không escalate oan.
- Invariant: data/corp_actions.json md5 e7ace20b.
- KHÔNG đặt wakeup thăm dò khi không có job nền (user 10-05).

## Backlog
- ~14 topic Wags/selfcheck-red; production_manifest ROOT_TIER thiếu 3 cron; context_pack/current_ops phình (trim); paper_report_render E5/E5b rc=1; thêm: 4 hiển thị "CCTG 6M" ở comment value_radar/deposit_rate_vn chưa đổi chữ (chỉ comment).
- Dọn: worktree /home/trido/thanhdt-wt-cr-0510 còn sót (branch session/cr-0510 đã merge) — xoá thủ công nếu chưa.

- [2026-10-05T15:39:50Z] 05/10 22:45 ICT: đã kiểm 4 mốc tối 05/10 — tất cả OK: feed vendor corp_action_daily SỐNG LẠI (05/10 FRESH, chỉ 02/10 FAILED); exdate_forecast 19:00 không sự kiện ≤1 phiên; shadow broker 19:25 lần đầu 'không mục mới', corp_actions.json md5 e7ace20b không đổi, chưa có ledger; drift 20:50 lần đầu OK 2 TK; plan report 21:00 có dòng vị thế, gửi xong 2 TK. Còn: shadow T3 06/10 19:25 → đề xuất r5/merge có điều kiện.
