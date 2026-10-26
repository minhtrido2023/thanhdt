# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike (dọn cuối ngày 26/10, ghi 00:5x 27/10)
## Sáng T3 27/10 (việc đầu tiên)
- Plan T3 27/10 SpaceX+ZaloPay tồn tại; park_trim/jit_unpark chạy lại rc=0 (không lệnh bán PARK). KIỂM residual SCL/VPB (partial-fill 26/10: SCL 800/1100 SpaceX, 500/700 ZaloPay; VPB ZaloPay 700/900) xử lý ra sao trong plan.
- Egg: nhắc user nếu chưa FUNDED trước gate 09:05 (egg_transfer_alert Telegram 15'/lần 08:30-14:30).
- Sự cố 26/10: DNSE API auth 500 buổi tối (đã hết 22:58); nguyên nhân 500 CHƯA điều tra; báo cáo EOD 26/10 gửi bù CHƯA xác nhận — kiểm report_delivery_gate COMPLETE. Retro: kb/incidents/retro/retro-2026-10-26.md (Pattern A: chuỗi EOD đỏ, lỗi không mang nguyên nhân; prevention (1)(2)(3) chưa làm).
- Chạy tay send_plan_report.sh --second-chance sau nửa đêm ⇒ EXPECTED_DATE nhảy ngày (đã đóng báo động giả); lần sau neo ngày giao dịch.
## Chờ USER
- Bus Wags/wags-fix-not-confirmed: coord-2026-10-26 + retro-pattern-wakeup (đề xuất B: dispatch.sh --bg chặn exit≠0 trừ --wakeup-ack/--no-followup). KHÔNG đăng question mới cùng pattern.
- LAG capacity: chuỗi dừng, chờ fill thật 15/12. Skeptic yêu cầu theo dõi.
## Đang chạy
- Taylor_20261026_160657 (opus, P4+sulfur → agents/Taylor/research/commodity_p4_sulfur_20261026/): xong → quant-skeptic verify rồi báo user; không wire.
- DGC: dự báo Q3 khoá md5 (job _064029); sau khi DGC công bố → chấm vs BCTC gốc. Taylor dgc_valuation_20261027 untracked.
- DD chu kỳ: blind DRI+TV1 (FPT loại vì KQKD công bố 21/10); BCTC Q3 DRI/TV1 30/10 (cron one-shot session-only); cron FPT 29/10 đối chiếu không-mù.
## Mốc
- nav-loss-brake 11-09; DT CRISIS commit sớm ~11/10; Livermore chấm ~19/11; BĐS 11-26; commodity PREREG-2 cron 11-25; LAG checkpoint 12-15; measurement audit ~12-27; SUE tracker review 2027-09-01.
- Nợ prevention retro: (c) cổng NAV ngoài cửa sổ EOD; (d) cổng plan-vs-lag_dd/ack.json; (e) quét script in cảnh báo stdout. context_pack ~45KB cần trim.

