---
name: vn30f_intraday_orb_2026
description: VN30F intraday data (1m bars 2.7y từ vnstock) + Opening-Range momentum strategy (ORB) có edge thật Sharpe ~2 net cost
metadata: 
  node_type: memory
  type: project
  originSessionId: da955fb4-3cf3-4f12-a372-44b0e169e1a4
---

**[REDACTED]09.** User hỏi lấy intraday VN30F từ vnstock xây strategy in-day.

**DỮ LIỆU (vnstock VCI quote.history):** bar 1m/5m/15m/1H đều có. 1m sâu ~2023-09-11→nay (~164k bar, 679 phiên, ~243 bar/phiên) — đủ backtest. Tick khớp lệnh (quote.intraday): endpoint có nhưng trả 0 dòng (chỉ live-session, KHÔNG lịch sử sâu) → strategy phải dựa BAR, không scalping sub-phút. Lưu data/vn30f1m_1min.csv. Giờ GD ~09:00-14:45, vol hình chữ U (sôi mở 08:45-09:00 + đóng 14:00-14:45 vol 24bps, im giữa phiên 11:00-13:30).

**CẤU TRÚC (2 khung khác nhau):**
- Bar-to-bar 15-30p: MEAN-REVERSION (autocorr lag1 30m=−0.122, 15m=−0.060, 5m=−0.035=phần lớn bid-ask bounce). Move ngắn đảo lại.
- Opening-range→cả ngày: MOMENTUM (corr OR30 vs rest +0.142; OR30>0→rest +12.3bps, <0→−9.0bps). Hướng sáng BÁM hết phiên. Overnight gap momentum yếu (+0.033).

**ORB BACKTEST (sign(OR 09:00-09:30) giữ đến đóng phiên, net TC 1.5bps, 669 phiên):**
- Tất cả ngày: WR 53.8%, +9.05bps/ngày, Sharpe 1.45, cum +77% (2.7y).
- **|OR30|≥0.2% = sweet spot: WR 55.5%, +14.8bps, Sharpe 2.04.** ≥0.4%: WR 62%/Sharpe 2.08 (n=100 mỏng). **≥0.6% HỎNG (Sharpe 0.33)** = mở quá mạnh→kiệt sức/đảo (khớp MR khung lớn).
- Cả LONG (Sh1.83) & SHORT (Sh1.11) đều ăn, KHÔNG long-bias artifact. Baseline long open→close chỉ +1.6bps.

**EDGE THẬT nhưng CHƯA validate đủ.** Caveat: (1) TC 1.5bps optimistic — all-in thật 2-4bps (mean +9bps nên còn dương ở 3bps nhưng cần sensitivity); (2) in-sample 1 regime 2023-26, CHƯA walk-forward, lọc ≥0.4% n=100 risk overfit ngưỡng; (3) thực thi bar-based, breakout thật có slippage; (4) giữ đến đóng = phơi vùng ATC biến động → cần stop/thoát sớm.

**REFINE + VALIDATE (vn30f_orb_strategy.py):**
- (2) Stop-loss + thoát sớm = THẤT BẠI, làm TỆ HƠN. Best=exit 14:30(đóng phiên) KHÔNG stop Sharpe 2.29; +stop0.7%→1.73; exit14:00→1.70; exit13:30→2.08. Stop bị chặt bởi whipsaw MR intraday (autocorr−0.122); thoát sớm vứt momentum chiều. → **chiến lược tốt nhất = ĐƠN GIẢN NHẤT: giữ đến đóng, không stop.**
- (1) PASS. Cost-sens (exit14:30 no-stop |OR|≥0.2%): TC 1.5/2.5/3.5bps → Sharpe 2.29/2.14/1.98 (bền tới 3.5bps). Walk-forward TC2.5bps DƯƠNG MỌI NĂM: 2023 Sh1.78, 2024 Sh0.29(yếu nhưng dương), 2025 Sh2.84, 2026 Sh2.59. Bản KHÔNG lọc |OR| (677 phiên) còn chắc hơn: mọi năm dương (2024 Sh0.99), tổng Sh1.50, không ngưỡng overfit.
- ⚠️ "2024 Sharpe −1.84" ở lần đầu = ARTIFACT của config kém (14:00+stop), KHÔNG phải strategy — chạy lại grid-best mới lộ. Bài học: validate trên config grid-best, đừng đoán trước.

**CHỐT deployable: ORB = lúc 09:30 lấy dấu cú 09:00→09:30, long/short giữ đến 14:30 đóng phiên, KHÔNG stop; tùy chọn lọc |OR30|≥0.2% (Sh~2.1 vs 1.5 toàn bộ). Net 2.5bps dương mọi năm, bền 3.5bps, phẳng qua đêm, đối xứng.** Quản trị rủi ro bằng POSITION SIZING (vol-target số HĐ) KHÔNG bằng stop. Ràng buộc: bar-based fill, 2.7y 1 regime, 2024 edge nén.

**KHÉP VÒNG: vol-target sizing + slippage (vn30f_orb_final.py):**
- SLIPPAGE (tick=0.1đ~0.5bps@1940, fill lệch hướng xấu): fixed-1 lọc Sharpe 2.42(0tick)/2.22(1)/2.01(2tick~thực tế)/1.80(3). Mỗi tick ≈ −0.2 Sharpe. Edge SỐNG net thực tế (Sh2.01 @2tick).
- VOL-TARGET sizing = THẤT BẠI (giống stop): giảm Sharpe (1.84 vs 2.01 fixed @2tick) + làm 2024 TỆ HƠN (−1.35). Lý do: edge ORB TỶ LỆ THUẬN vol (cú OR=phần biên độ ngày) → inverse-vol cắt vị thế đúng ngày vol cao nhiều thông tin nhất = SAI TRỤC. → risk mgmt KHÔNG bằng vol-target.
- 2024 isolate (fixed-1, no vol-target): lọc≥0.2%+slip2tick → 2024 −0.03(hòa)/tổng Sh2.01; TẤT CẢ NGÀY+slip2tick → 2024 +0.74/tổng Sh1.35; all-days+slip1tick → 2024 +1.06/Sh1.58. **Bản KHÔNG lọc ROBUST hơn (dương mọi năm); lọc≥0.2% tăng Sharpe nhưng 2024 mỏng = đánh đổi magnitude↔robustness.**

**CHỐT CUỐI deployable: ORB all-days (mặc định, robust nhất), 09:30 dấu OR→giữ 14:30, KHÔNG stop, size CỐ ĐỊNH theo vốn. Net slip 1-2tick: Sharpe 1.35-1.58, dương mọi năm 2023-26, MaxDD ~−6%, phẳng qua đêm. Optional lọc |OR|≥0.2%→Sh~2.0 (2024 mỏng). BÀI HỌC: cả 3 refinement trực giác (stop, thoát sớm, vol-target) ĐỀU HẠI — edge nằm ở sự ĐƠN GIẢN, slippage là thứ duy nhất ăn edge (đã định lượng).**

NEXT (optional, chưa làm): sizing theo SIGNAL strength (thuận vol, ngược vol-target) thử xem; overlay MR fade; lọc DT5G/vol regime; paper-trade live. Files: data/vn30f1m_1min.csv, vn30f_orb_strategy.py, vn30f_orb_final.py. ⚠️ Edge intraday HOÀN TOÀN khác edge daily (DT5G/FA/8L không chuyển sang) — microstructure/session-pattern. Liên quan [[vn30f_data_fsystem_revalidation_2026]] (overlay daily).
