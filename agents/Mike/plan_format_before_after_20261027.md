# Plan DollarBill — trước/sau bố cục mới (render thật từ plan 27/10 và 02/10, dry-run, chưa gửi)

## ZaloPay 2026-10-27 — TRƯỚC (3354 ký tự)
```
📋 **Kế hoạch giao dịch ngày mai 2026-10-27 — Account ZaloPay**
🧭 Thị trường: NEUTRAL (nguồn DT5G_gated (source=DT5G_macro)) · NAV cơ sở: 592,300,485đ
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate CRISIS 14/25 (56%, còn 11 phiên để commit, base giữ từ 2026-10-07, committed NEUTRAL) · P(CRISIS xác nhận|k=14)≈73% [50–93%, n=15] ⚠ mẫu mỏng, tham khảo  [dữ liệu tới 2026-10-26]
   ↳ Nền xấu 20 phiên liền từ 29/09 (6 BEAR + 14 CRISIS, đổi qua lại 1 lần → bộ đếm reset, vẫn NEUTRAL) · VNINDEX −1,0% từ đầu đợt · ngưỡng xem lại: ≥15 phiên và VNINDEX ≤−5,0% — chưa chạm
🥚 **Trứng vàng 535.6tr là tiền — CHUYỂN 11.7tr sang cash trước 9:05 ICT sáng mai** (bot nhắc mỗi 15' từ 8:30 tới khi xong) (Tổng mua 11.2tr theo giá ref → 11.7tr nếu mọi lệnh khớp ở trần đuổi +4% + phí − tiền mặt sẵn có 0.0tr = 11.7tr; riêng giá ref thì thiếu 11.2tr — phần chênh là đệm giá tăng).
🎯 Hành động: **2 lệnh** (0 bán, 2 mua):
  • MUA SCL 200cp @ ~32,600đ — RESIDUAL ngày 2/… (filter_lag_entry_window.py): phần chưa khớp của target ngày 1; LO ≤ ent…
      ↳ 💧 Tiền đâu ra: đủ tiền mặt sẵn có, KHÔNG cần bán PARK.
      ↳ DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 9.3% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
      ↳ DD SCL [LAG] (data 2026-10-26): thanh khoản OK (ADV3T 4.29 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
      ↳ FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.99 · PE 10.79
  • MUA VPB 200cp @ ~23,600đ — RESIDUAL ngày 2/… (filter_lag_entry_window.py): phần chưa khớp của target ngày 1; LO ≤ ent…
      ↳ 💧 Tiền đâu ra: đủ tiền mặt sẵn có, KHÔNG cần bán PARK.
      ↳ DCF: NOT_COMPUTED (financial_sector_excluded) → thay thế: 🟢 Gordon P/B (ngân hàng): P/B 1.18 vs hợp lý 1.22 (ROE5Y 14.8%, COE 13%/g 5%) — CHEAP [đã validate (bank_compounder_screen)]
      ↳ DD VPB [LAG] (data 2026-10-26): thanh khoản OK (ADV3T 361.93 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm) · ⚠ cờ bất thường H [IDIOCRASH] ngày 2026-09-18
      ↳ FA: ROE5Y 14.8% · ROE_Min3Y 8.4% · FSCORE 4 · D/E 7.05 · PE 7.57
⚠️ **2 mã auto-exit BỊ CẮT do trần sellable (Σ SELL mọi book):**
   • VPB (LAG): 282cp → 0cp
   • VPB (LAG): 982cp → 0cp
💧 L2 JIT unpark: NO_JIT_NEEDED — ⚠️ BUY-VPB-LAG-02 (VPB): tới 100cp trong lệnh này có thể cần Trứng vàng (≤2.4tr, cận trên — có thể ít hơn nếu bán PARK bù được một phần) — CẦN RÚT Trứng vàng trong giờ hành chính TRƯỚC khi đặt lệnh, hoặc để hệ thống tự bán PARK bù nếu đủ. Nếu chưa rút và PARK không đủ bù, gate P0 (check_plan_funding) sẽ giữ HOLD toàn bộ lệnh này (đúng thiết kế, không phải lỗi).
⏳ Trạng thái: **CHỜ DUYỆT** — chưa duyệt thì preflight 08:45 báo RED và bot KHÔNG đặt lệnh. Duyệt bằng cách nhắn Mike.
_(DollarBill lập, gửi 2026-10-27 01:01 ICT)_
```
## ZaloPay 2026-10-27 — SAU (2157 ký tự)
```
📋 **PLAN T+1 · Thứ Ba 27/10 · ZaloPay**
⏳ **CHỜ DUYỆT** — nhắn Mike để duyệt (chưa duyệt: bot KHÔNG đặt lệnh, preflight 08:45 báo RED). · ⚠️ **3 cảnh báo** (mục CẢNH BÁO cuối)
NAV 592.3tr · Regime NEUTRAL · DT5G candidate CRISIS 14/25 (còn 11 phiên để commit)

**🔔 CẦN LÀM / QUYẾT ĐỊNH**
🥚 **Chuyển 11.7tr từ Trứng vàng → cash trước 9:05 ICT** (bot nhắc mỗi 15' từ 8:30). Σ mua 11.2tr + đệm đuổi giá +4% & phí = 11.7tr − tiền mặt 0.0tr · Trứng vàng hiện 535.6tr.

**🎯 LỆNH — 2 mua Σ 11.2tr · 0 bán**
• **MUA SCL** 200cp @ 32,600 ≈ 6.5tr · LAG_LO
    ↳ 📌 RESIDUAL ngày 2/… (filter_lag_entry_window.py): phần chưa khớp của target ngày 1; LO ≤ entry_anchor_price, KHÔNG đuổi giá (chung cho 2 lệnh cùng loại)
    ↳ DCF n/a (fcfe_negative_buildout) → 8L (fallback rộng): 8L rating 2/5, earnings yield 9.3% (1/PE)
    ↳ DD: thanh khoản OK (ADV3T 4.29 tỷ/phiên) · FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.99 · PE 10.79
• **MUA VPB** 200cp @ 23,600 ≈ 4.7tr · LAG_LO ⚠️
    ↳ DCF n/a (financial_sector_excluded) → 🟢 Gordon P/B (ngân hàng): P/B 1.18 vs hợp lý 1.22 (ROE5Y 14.8%, COE 13%/g 5%) — CHEAP
    ↳ DD: thanh khoản OK (ADV3T 361.93 tỷ/phiên) · FA: ROE5Y 14.8% · ROE_Min3Y 8.4% · FSCORE 4 · D/E 7.05 · PE 7.57

**⚠️ CẢNH BÁO**
⚠ THIẾU GIÁ LIVE — cần kiểm tra tay: DNSE API trả HTTP 500 'authentication failed' cho mọi endpoint (balances/positions/secdef/latest_trade) lúc lập plan 10-26 ~19:10 ICT. Ref price lấy từ DNSE orderbook L2 14:44 (best offer) trong dnse_raw — KHÔNG phải giá đóng cửa chính thức, không dùng BQ. Số dư/egg cũng là bản log 14:02–14:30, không phải đọc sống. Cần user/Mafee kiểm lại trước 08:45.
⚠️ VPB: cờ bất thường H [IDIOCRASH] ngày 2026-09-18
⚠️ **2 mã auto-exit BỊ CẮT do trần sellable (Σ SELL mọi book):**
   • VPB (LAG): 282cp → 0cp
   • VPB (LAG): 982cp → 0cp

_(DollarBill lập, gửi 2026-10-27 01:02 ICT)_
```

## SpaceX 2026-10-27 — TRƯỚC (2744 ký tự)
```
📋 **Kế hoạch giao dịch ngày mai 2026-10-27 — Account SpaceX**
🧭 Thị trường: NEUTRAL (nguồn DT5G_gated (source=DT5G_macro)) · NAV cơ sở: 969,118,586đ
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate CRISIS 14/25 (56%, còn 11 phiên để commit, base giữ từ 2026-10-07, committed NEUTRAL) · P(CRISIS xác nhận|k=14)≈73% [50–93%, n=15] ⚠ mẫu mỏng, tham khảo  [dữ liệu tới 2026-10-26]
   ↳ Nền xấu 20 phiên liền từ 29/09 (6 BEAR + 14 CRISIS, đổi qua lại 1 lần → bộ đếm reset, vẫn NEUTRAL) · VNINDEX −1,0% từ đầu đợt · ngưỡng xem lại: ≥15 phiên và VNINDEX ≤−5,0% — chưa chạm
🥚 **Trứng vàng 873.7tr là tiền — CHUYỂN 10.2tr sang cash trước 9:05 ICT sáng mai** (bot nhắc mỗi 15' từ 8:30 tới khi xong) (Tổng mua 9.8tr theo giá ref → 10.2tr nếu mọi lệnh khớp ở trần đuổi +4% + phí − tiền mặt sẵn có 0.0tr = 10.2tr; riêng giá ref thì thiếu 9.8tr — phần chênh là đệm giá tăng).
🎯 Hành động: **1 lệnh** (0 bán, 1 mua):
  • MUA SCL 300cp @ ~32,600đ — LAG_LO entry ngày 2/3 — chỉ phần dư. Điều kiện user (21/10): hủy nếu có tin VinCons chậm t…
      ↳ 💧 Tiền đâu ra: đủ tiền mặt sẵn có, KHÔNG cần bán PARK.
      ↳ DCF: NOT_COMPUTED (fcfe_negative_buildout) → thay thế: 8L (fallback rộng): 8L rating 2/5, earnings yield 9.3% (1/PE) [FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý]
      ↳ DD SCL [LAG] (data 2026-10-26): thanh khoản OK (ADV3T 4.29 tỷ/phiên) · nền YoY dương (surprise không phồng do nền âm)
      ↳ FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.99 · PE 10.79
ℹ️ Trim PARK (L1): chưa bán được phần PARK còn lại 9.1tr (1.15% pool) — MBB (65cp bán được), TPB (0cp bán được), VIB (0cp bán được), VPB (0cp bán được) (<1 lô / chưa giao dịch được). Không cần xử lý.
💧 L2 JIT unpark: NO_JIT_NEEDED — ⚠️ BUY-SCL-LAG-01 (SCL): tới 100cp trong lệnh này có thể cần Trứng vàng (≤3.3tr, cận trên — có thể ít hơn nếu bán PARK bù được một phần) — CẦN RÚT Trứng vàng trong giờ hành chính TRƯỚC khi đặt lệnh, hoặc để hệ thống tự bán PARK bù nếu đủ. Nếu chưa rút và PARK không đủ bù, gate P0 (check_plan_funding) sẽ giữ HOLD toàn bộ lệnh này (đúng thiết kế, không phải lỗi).
⏳ Trạng thái: **CHỜ DUYỆT** — chưa duyệt thì preflight 08:45 báo RED và bot KHÔNG đặt lệnh. Duyệt bằng cách nhắn Mike.
_(DollarBill lập, gửi 2026-10-27 01:00 ICT)_
```
## SpaceX 2026-10-27 — SAU (1299 ký tự)
```
📋 **PLAN T+1 · Thứ Ba 27/10 · SpaceX**
⏳ **CHỜ DUYỆT** — nhắn Mike để duyệt (chưa duyệt: bot KHÔNG đặt lệnh, preflight 08:45 báo RED).
NAV 969.1tr · Regime NEUTRAL · DT5G candidate CRISIS 14/25 (còn 11 phiên để commit)

**🔔 CẦN LÀM / QUYẾT ĐỊNH**
🥚 **Chuyển 10.2tr từ Trứng vàng → cash trước 9:05 ICT** (bot nhắc mỗi 15' từ 8:30). Σ mua 9.8tr + đệm đuổi giá +4% & phí = 10.2tr − tiền mặt 0.0tr · Trứng vàng hiện 873.7tr.

**🎯 LỆNH — 1 mua Σ 9.8tr · 0 bán**
• **MUA SCL** 300cp @ 32,600 ≈ 9.8tr · LAG_LO ngày 2/3
    ↳ 📌 chỉ phần dư. Điều kiện user (21/10): hủy nếu có tin VinCons chậm trả — chưa kiểm được tự động, kiểm tay trước 08:45
    ↳ DCF n/a (fcfe_negative_buildout) → 8L (fallback rộng): 8L rating 2/5, earnings yield 9.3% (1/PE)
    ↳ DD: thanh khoản OK (ADV3T 4.29 tỷ/phiên) · FA: ROE5Y 13.8% · ROE_Min3Y 10.1% · FSCORE 8 · D/E 0.99 · PE 10.79

**ℹ️ GHI CHÚ** (không cần quyết định)
ℹ️ PARK còn 9.1tr (1.15% pool) chưa bán được — MBB 65cp, TPB 0cp, VIB 0cp, VPB 0cp (bán được), <1 lô / chưa giao dịch được. Không cần xử lý.

_(DollarBill lập, gửi 2026-10-27 01:01 ICT)_
```

## ZaloPay 2026-10-02 — TRƯỚC (3306 ký tự)
```
📋 **Kế hoạch giao dịch ngày mai 2026-10-02 — Account ZaloPay**
🧭 Thị trường: NEUTRAL (nguồn DT5G_gated (source=DT5G_macro)) · NAV cơ sở: 597,182,854đ
🛰️ Gate DT5G: 🟢 BÌNH THƯỜNG · candidate CRISIS 14/25 (56%, còn 11 phiên để commit, base giữ từ 2026-10-07, committed NEUTRAL) · P(CRISIS xác nhận|k=14)≈73% [50–93%, n=15] ⚠ mẫu mỏng, tham khảo  [dữ liệu tới 2026-10-26]
   ↳ Nền xấu 20 phiên liền từ 29/09 (6 BEAR + 14 CRISIS, đổi qua lại 1 lần → bộ đếm reset, vẫn NEUTRAL) · VNINDEX −1,0% từ đầu đợt · ngưỡng xem lại: ≥15 phiên và VNINDEX ≤−5,0% — chưa chạm
🎯 Hành động: **16 lệnh** (16 bán, 0 mua):
  • BÁN ACB 200cp @ ~21,100đ — BÁN PARK gộp: L1 200cp + L2 0cp = 200cp × 21,100đ = 4,220,000đ.
  • BÁN BID 300cp @ ~35,450đ — BÁN PARK gộp: L1 300cp + L2 0cp = 300cp × 35,450đ = 10,635,000đ.
  • BÁN CTG 300cp @ ~30,050đ — BÁN PARK gộp: L1 300cp + L2 0cp = 300cp × 30,050đ = 9,015,000đ.
  • BÁN HDB 100cp @ ~28,000đ — BÁN PARK gộp: L1 100cp + L2 0cp = 100cp × 28,000đ = 2,800,000đ.
  • BÁN HPG 300cp @ ~20,050đ — BÁN PARK gộp: L1 300cp + L2 0cp = 300cp × 20,050đ = 6,015,000đ.
  • BÁN MBB 300cp @ ~19,550đ — BÁN PARK gộp: L1 300cp + L2 0cp = 300cp × 19,550đ = 5,865,000đ.
  • BÁN MSB 100cp @ ~14,200đ — BÁN PARK gộp: L1 100cp + L2 0cp = 100cp × 14,200đ = 1,420,000đ.
  • BÁN SHB 200cp @ ~11,350đ — BÁN PARK gộp: L1 200cp + L2 0cp = 200cp × 11,350đ = 2,270,000đ.
  • BÁN TCB 200cp @ ~33,000đ — BÁN PARK gộp: L1 200cp + L2 0cp = 200cp × 33,000đ = 6,600,000đ.
  • BÁN VCB 200cp @ ~57,600đ — BÁN PARK gộp: L1 200cp + L2 0cp = 200cp × 57,600đ = 11,520,000đ.
  • BÁN VHM 200cp @ ~68,400đ — BÁN PARK gộp: L1 200cp + L2 0cp = 200cp × 68,400đ = 13,680,000đ.
  • BÁN VIB 200cp @ ~13,400đ — BÁN PARK gộp: L1 200cp + L2 0cp = 200cp × 13,400đ = 2,680,000đ.
  • BÁN VPB 300cp @ ~23,300đ — BÁN PARK gộp: L1 300cp + L2 0cp = 300cp × 23,300đ = 6,990,000đ.
  • BÁN CSV 1000cp @ ~19,950đ — MANUAL-INJECT LAG (user duyệt 2026-10-01 19:54 ICT): CSV mua 2026-07-28 (BUY-CSV-00, LAG_H…
  • BÁN SCL 200cp @ ~28,900đ — AUTO-EXIT LAG: giữ 35 phiên ≥ mốc cố định 25 (pt_v23_audit_2014.py:2060) — đề xuất thoát t…
  • BÁN VPB 600cp @ ~23,300đ — MANUAL-INJECT LAG (user duyệt 2026-10-01 22:49 ICT): VPB LAG_LO mua 2026-07-27 (700cp → 88…
   ↳ ℹ️ Lý do (áp dụng CHUNG cho 13 lệnh BÁN PARK_TRIM ở trên): tuân thủ trần PARK 0% (park-trim), KHÔNG liên quan tới việc tài trợ lệnh mua trong plan này.
⚠️ **1 mã auto-exit BỊ CẮT do trần sellable (Σ SELL mọi book):**
   • VPB (LAG): 882cp → 600cp (duyệt tay)
🅿️ L1 trim PARK: TRIM — target_park=0 (park TẮT HẲN) ⇒ bỏ qua phân bổ theo rổ custom30V, mọi mã PARK đang giữ nhận target=0 ⇒ đề xuất bán sạch toàn bộ sổ PARK (vẫn qua trần ADV/ngày + lô + sellable T+2 như bình thường).
✅ Trạng thái: ĐÃ DUYỆT (user) — bot tự thực thi 09:05 sáng mai, không cần thao tác gì thêm.
_(DollarBill lập, gửi 2026-10-27 01:02 ICT)_
```
## ZaloPay 2026-10-02 — SAU (1665 ký tự)
```
📋 **PLAN T+1 · Thứ Sáu 02/10 · ZaloPay**
✅ **ĐÃ DUYỆT** (user) — bot tự đặt lệnh 09:05, không cần thao tác thêm. · ⚠️ **1 cảnh báo** (mục CẢNH BÁO cuối)
NAV 597.2tr · Regime NEUTRAL · DT5G candidate CRISIS 14/25 (còn 11 phiên để commit)

**🎯 LỆNH — 0 mua · 16 bán Σ 123.4tr**
• **BÁN PARK_TRIM** 13 mã Σ 83.7tr — ACB 200 · BID 300 · CTG 300 · HDB 100 · HPG 300 · MBB 300 · MSB 100 · SHB 200 · TCB 200 · VCB 200 · VHM 200 · VIB 200 · VPB 300
    ↳ ℹ️ cùng một lý do: park TẮT (0%) ⇒ bán sạch PARK (không liên quan tài trợ lệnh mua).
• **BÁN CSV** 1,000cp @ 19,950 ≈ 19.9tr · LAG_AUTO_EXIT
    ↳ 📌 MANUAL-INJECT LAG (user duyệt 2026-10-01 19:54 ICT): CSV mua 2026-07-28 (BUY-CSV-00, LAG_HI), giữ 44 phiên ≥ mốc cố định 25 — auto_exit_inject bỏ sót vì journal trước ~08-04 thiếu cột book; đề xuất thoát toàn bộ
• **BÁN SCL** 200cp @ 28,900 ≈ 5.8tr · LAG_AUTO_EXIT
    ↳ 📌 AUTO-EXIT LAG: giữ 35 phiên ≥ mốc cố định 25 — đề xuất thoát toàn bộ
• **BÁN VPB** 600cp @ 23,300 ≈ 14.0tr · LAG_AUTO_EXIT
    ↳ 📌 MANUAL-INJECT LAG (user duyệt 2026-10-01 22:49 ICT): VPB LAG_LO mua 2026-07-27 (700cp → 882cp sau thưởng 1,2604), giữ 45 phiên ≥ mốc cố định 25. [CAP sellable 882->600cp] broker tradeQuantity 900 (312cp thưởng chưa sellable) trừ PARKMERGE-S…

**⚠️ CẢNH BÁO**
⚠️ **1 mã auto-exit BỊ CẮT do trần sellable (Σ SELL mọi book):**
   • VPB (LAG): 882cp → 600cp (duyệt tay)

_(DollarBill lập, gửi 2026-10-27 01:03 ICT)_
```
