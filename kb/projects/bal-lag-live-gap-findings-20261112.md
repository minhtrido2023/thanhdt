# BAL/LAG backtest-vs-live gap — kết luận tạm GĐ0–GĐ1 (2026-11-12 ~20:20 ICT)

> Kế hoạch: `bal-lag-live-gap-research-plan-20261112.md` (user duyệt 12/11 17:40). Artifact: `agents/Taylor/research/live_gap_phase{0,1,1b,1c,2a}_20261112/`.
> Mỗi giai đoạn qua quant-skeptic; verdict trên bus topic `live-gap-phase*-20261112`. TRẠNG THÁI: GĐ1 DỪNG sau 3 vòng (cầu chì vòng-3), GĐ2 vòng 2 và GĐ3 đang/sắp chạy.

## Đã chốt (số tái lập độc lập bởi skeptic)
- Hurdle tiết kiệm PIT 01/07→11/11 = 2,548% (SpaceX), 2,455% (ZaloPay 06/07→). Live SpaceX −3,862% (−6,41pp vs hurdle), ZaloPay bot −2,609% (−5,06pp), cả TK −7,511%. Nguồn: GĐ0 `vs_savings_table.csv`.
  ⚠️ Chuỗi hurdle 2011→2026-06 là 26 mốc neo HỒI TỐ ngày 19/06/2026 (registry deposit_rate_vn caveat b) — dùng làm kết quả ex-post OK, KHÔNG dùng làm đặc trưng/điều kiện thời điểm trước 2019 (và coi 2019+ là mốc tay).
- Pin R3 tái lập byte-by-byte (23,37% / 684,52B / `4707bcbe`) CHỈ khi hoán đủ 3 file data pin-era (earnings_events_classified, lag_edge_health, earnings_surprise); lệch +0,94pp trên data hiện tại là cơ sở giá thô→điều chỉnh (không look-ahead).
- Engine pt_v23_audit_2014: bất tất định theo AUDIT_END do `sort_values` quicksort trong `regime_size_overlay` (tie cùng ngày); vá mergesort thu 1986→4 phiên lệch; 4 phiên dư = rổ park re-dating OShares (ACB), 0,006% NAV. Phân phối tie-break 10 seed: CAGR 23,94–25,05% (sd 0,35pp) ⇒ pin 23,37% là MỘT lần rút. **Chưa re-pin, chưa merge vá sort — cần user + quant-skeptic.**
- Cửa sổ live KHÔNG phải phép thử BAL/LAG: từ 04/08 BAL+LAG ≈ 5% NAV (SpaceX 5,2%, ZaloPay 5,9%); phần còn lại CAPIT, PARK, DISC, egg (TB 24%/15% NAV, 8,5%/năm đo thật). Lỗ live chủ yếu = rổ park custom30V trong thị trường −6% (park đã tắt từ 01/10) + CAPIT.
- Live thắng VN-Index (−6,08%) nhưng thua tiết kiệm.

## Chưa chốt / KHÔNG kết luận được (nói thẳng)
- Dấu của gap "live − engine": engine park=0 → live thua 2,1–3,9pp; engine + lịch park live → live thắng +4,4..4,7pp. Skeptic: cái sau KHÔNG so cùng cơ chế — trước ~06/08 live chỉ có đường MUA park (JIT/bán rổ thêm 08-06), defer 4 LAG+3 CAPIT (plan 07-28/29), lỡ entry LAG 07-24 do DollarBill hết usage; ~3,0pp của 4,35pp nằm ở 20–31/07 ⇒ đó là **fidelity/thực thi live**, không phải alpha. Live alpha ex-egg ≈ +0,07pp (SpaceX), +0,94pp (ZaloPay).
- W2b (sàn ADV 2 tỷ/mã cờ/DD-zone/excluded), W3 lệnh tay, W4 fill thật: chưa đo. Cần fidelity counterfactual (tắt JIT/bán rổ tới 08-04/06) nếu muốn đóng. Bỏ ở vòng 4 vì N=1 cửa sổ: lợi ích thấp.
- GĐ2A (0/90 đặc trưng cùng dấu IS&OOS; value LAG chết sau 2020; H5 không phải OOS; ~46% nhãn LAG engine là fill ảo) đang làm lại ở `live_gap_phase2b`.

## Việc chờ user (KHÔNG tự làm)
1. Re-pin R3 (23,60% với vá sort, hay giữ 23,37% làm một lần rút) + merge vá mergesort vào main.
2. Dòng "so với gửi tiết kiệm" trong bảng hiệu suất báo cáo (`PROPOSAL_savings_row.proposed.md` ở GĐ0) — chạm §21/§31.
3. Merge fix LAG cache adjusted (đã chạy `adj` = `ctrl` nhưng vintage LAG −1,34pp cửa sổ).
