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

- [2026-10-26T18:19:45Z] 27/10 01:15 user duyệt format plan (master 4b0ee23d5) và YÊU CẦU duyệt plan T3 27/10 SpaceX+ZaloPay, NHƯNG lệnh approve_plan_simple.sh bị classifier chặn ⇒ plan CHƯA ghi duyệt; chờ user cho phép/tự chạy. Egg: SpaceX ≥10,2tr, ZaloPay ≥11,7tr trước 09:05; kiểm tay giá SCL/VPB ZaloPay trước 08:45
- [2026-10-27T01:38:44Z] 27/10 08:5x: user duyệt B wakeup gate — DONE master f16a39cb1 (dispatch.sh --bg tương tác cần --wakeup-ack|--no-followup, exit 8). Từ giờ MỌI dispatch --bg của Mike phải kèm 1 trong 2 cờ. Plan T3 27/10 vẫn chờ user cho phép approve_plan_simple.
- [2026-10-27T03:45:06Z] 27/10 10:5x: user hỏi review 'fund history lock' — đã rà (chỉ đọc): anchor check OK 2 TK, 2 seal (tới 10-16), đuôi 10-19→10-26 chưa chốt (cron T7 31/10 chốt tới 10-23); đính chính 07-02/08-06 đã áp. Không thấy mốc review có ngày trong KB.
