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
- [2026-10-27T04:17:14Z] 27/10 11:2x: user duyệt gói kích hoạt DRI (kb/projects/dri-triggers-20261027.md): GIẢM 50% nếu LNST Q3<22tỷ | 2/3 chỉ báo Bobby xấu | giá>=15.100; THOÁT nếu Bobby TROUGH/sự kiện Lào/Dakruco. CHƯA wire auto-sell; báo user khi chạm. Cần: cảnh báo giá 15.100 (chưa có). Mốc 30/10 BCTC Q3.
- [2026-10-27T04:19:27Z] 27/10 11:3x: BCTC Q3 DRI (ký 22/10) user gửi: LNST mẹ 25,98 tỷ (−33% YoY) ≥22 nên trigger bán chưa kích; dự báo Taylor/blind trượt; cần kiểm ngày CBTT (mù 26/10?) + CĐKT/LCTT/thuyết minh (tồn kho tấn, thưởng, CFO, Dakruco). Chờ user quyết giảm hay giữ.
- [2026-10-27T04:38:44Z] 27/10 11:4x: Taylor DD DRI Q3 xong (REPORT_Q3_UPDATE.md): GIỮ theo kế hoạch; FV 11.031 (-25%); 2 cờ §6b bật; đề xuất riêng giảm 50% chủ động CHỜ USER quyết. F mù không chấm được (SXKD 9T 20/10). Chưa chạy Bobby indicators cập nhật. Còn nợ: kiểm lại 'fund history lock' = mốc CORR_STEP 23/10 (dashboard_watchlist).
- [2026-10-27T05:15:19Z] 27/10 12:1x: user DUYỆT giảm 50% DRI (SpaceX 1.250, ZaloPay 650) — đã ghi current_ops + dri-triggers; DollarBill đưa vào plan T+1 28/10 (19:00). Kiểm tối nay plan 28/10 có dòng SELL DRI đúng số; nếu user bán tay thì dùng KL broker.
- [2026-10-27T05:30:38Z] 27/10 12:4x: CORR_STEP (fund-history-lock mốc 23/10) HOÀN TẤT: đính chính A+B đã giao trong weekly 12–16/10 cả 2 TK (COMPLETE); đã gỡ mốc dashboard. Còn mở nhỏ: ledger có +1 dòng nav_is_estimate mỗi TK so với số dự kiến (chưa xác minh).
- [2026-10-27T08:40:57Z] 27/10 15:4x: user duyệt giao Taylor định giá lại DRI theo cung cao su (job Taylor_20261027_084046, opus, kết quả agents/Taylor/research/dri_val_supply_adj_20261027/). Xong → cho skeptic phản biện rồi báo user; không wire/không lệnh.
- [2026-10-27T08:59:14Z] 27/10 15:5x: Taylor dri_val_supply_adj xong (FV 60/40 tâm 14.301); fundamental-skeptic REFUTED (72% bước +3.183 là phép ghép MID↔mid 2,18-2,30; FV tin hơn ~12-14k tâm 13k; 14.700 hơi đắt 5-20%; không có cơ sở đảo giảm 50%; vùng mua ≤13.000 biên an toàn ~0). Chờ user: chạy lại không ghép + thêm trigger SXKD T10 (~10/11) vào gói dri-triggers.
- [2026-10-27T09:31:05Z] 27/10 16:3x: user duyệt 2 việc DRI: (1) Taylor_20261027_093047 chạy lại định giá không ghép (agents/Taylor/research/dri_val_supply_adj_r2_20261027/) → skeptic phản biện tiếp → báo user; (2) trigger SXKD T10 (~10/11: bán<1.000t hoặc LNTT 10T<9T 208,21 ⇒ giảm nốt) đã ghi dri-triggers (commit b4b35776f); vùng mua 21/10 đã rút.
