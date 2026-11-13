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
- GĐ2 (xem mục dưới) đã qua 2 vòng skeptic; DỪNG polish (cầu chì), sửa diễn giải ngay trong file này.

## Việc chờ user (KHÔNG tự làm)
1. Re-pin R3 (23,60% với vá sort, hay giữ 23,37% làm một lần rút) + merge vá mergesort vào main.
2. Dòng "so với gửi tiết kiệm" trong bảng hiệu suất báo cáo (`PROPOSAL_savings_row.proposed.md` ở GĐ0) — chạm §21/§31.
3. Merge fix LAG cache adjusted (đã chạy `adj` = `ctrl` nhưng vintage LAG −1,34pp cửa sổ).

## GĐ2 — phân loại deal BAL/LAG (2 vòng, skeptic REFUTED cả hai vòng về diễn giải; null lõi đứng; Mike ghi bản đã sửa, 12/11 20:40 ICT)
Nguồn: `live_gap_phase2a_20261112` (panel cũ) → `live_gap_phase2b_20261112` (panel sạch fill ảo, ledger `151bd903…` với `LIQ_ZERO_BLOCK=lag`). Bus: `live-gap-phase2a/2b-20261112`.
- **Null lõi (CONFIRMED, 3 tập sạch):** 0 đặc trưng qua BH-FDR q<0,10 ở CẢ IS (2014–19) và OOS (2020+) cùng dấu; họ FDR 83/86 (liqz_all), 82/85 (old_adv100). Panel: 888 deal có nhãn (BAL 268 / LAG 620); sự kiện độc lập 28–43 cụm tháng/ô.
- **Hiện vật fill ảo (đã gỡ):** `log_adv20` "dương cả hai era" và H1 IS (+6,83pp → +2,09…+3,86pp). Nguyên nhân: engine mua trọn size trong 1 phiên khi thiếu khoá ADV (`liquidity_require_positive=False`); bật `LIQ_ZERO_BLOCK=lag` thì LAG >100% ADV20 rơi 45,6% → 7,4% (phần 7,4% còn lại = 4–5 lần mua ~27% ADV/phiên, không phải fill ảo).
- **ĐÍNH CHÍNH so với báo cáo Taylor (skeptic vòng 2):** value LAG IS ρ ey +0,145…+0,19 ổn định trên MỌI tập sạch, OOS ≈ 0 (comp_v3 liqz_adv100 IS q 0,042). Tức "IS mạnh → OOS yếu" là THẬT, không phải hiện vật fill ảo; chỉ q thay đổi theo lực/thành phần họ FDR. Quality: không được ủng hộ cũng không bị bác.
- **Lực (nói đúng):** luật quyết định = BH trên ~83 phép thử + qua cả hai era ⇒ KHÔNG bắt được ρ ≈ 0,3–0,45 (MDE hiệu dụng BAL IS 0,45–0,48, LAG IS 0,32–0,34, BAL OOS 0,34–0,37, LAG OOS 0,39–0,42). "Không phát hiện được" ≠ "không có edge". Placebo hoán vị-trong-năm không phải null hợp lệ cho bootstrap theo tháng (phá ICC 0,09–0,40) ⇒ bỏ câu "thật 1 vs placebo 6,75".
- **H5 (lãi tiết kiệm đang tăng ⇒ deal kém):** trên chuỗi PIT thật fiinprox dep1m (kỳ hạn 1T, 2019+): band>0 −1,18pp thô / −0,37pp khử năm (7 episode); band ≥0,2 −10,78pp thô nhưng chỉ do MỘT episode 2026 (bỏ 2026 → −1,32). Δ trong-năm ≈ −0,7pp, khử mức năm hấp thụ cơ học. **Không tách được khỏi mức năm; N độc lập 1–7: không kết luận, không bác.** Hurdle 12T trước 2019 không PIT (26 mốc hồi tố 19/06/2026).
- **Live OOS thật:** 12 deal đóng thuộc 4 mã (CSV, SCL, VPB, VPI) + 11 mở — quá ít để suy luận.
- **Khuyết điểm chưa sửa (ghi để GĐ sau):** `dt5g_cand_clock` dựng sai (không phải `get_dt_gate_clock()`); `cfoa_pos` nhị phân bị luật nunique<3 loại (LAG IS q 0,086); dt5g_state nhị phân BAL IS bị loại; độ nhạy phí native chưa chạy cho liqz_all; `psy` dùng OShares TRAP (≤2% sự kiện, không đổi kết luận).

## GĐ3 — thời điểm an toàn so với tiết kiệm (skeptic CONFIRMED medium, 12/11 20:50 ICT; bản đã sửa theo skeptic)
Nguồn: `live_gap_phase3_20261112` (PREREG ghi 20:32:59 ICT, md5 `7c9bde3f…`, có trước phép thử; engine sạch P0 ledger `84f796bd…`, P30 `151bd903…`). Bus `live-gap-phase3-20261112`.
- **Null lõi:** 0/6 biến thời điểm (DT5G, dd52 VNINDEX, breadth, SPX dd, LAG edge, vol60) qua tiêu chí khai trước; N trials 12; MDE excess 12T 14–30pp (IS) / 57–110pp (OOS), ~5 cửa sổ 12T độc lập/era ⇒ "không phát hiện được", thiết kế gần như chắc chắn ra null. Không vớt biến nào.
- **Baseline vô điều kiện (engine sạch, KHÔNG trừ gap live, lãi nhàn rỗi 0% = đầu SÀN):** V2.4 thắng tiết kiệm 12T ở 77,6% ngày khởi đầu; **dải theo quy ước: 67% (nhàn rỗi 0%, trừ 4,5pp/năm) … 74% (0%, trừ 1,5pp) … 85,5% (nhàn rỗi hưởng lãi 12T, trừ 1,5pp) … 90% (hưởng lãi, không trừ)** — CẤM trích một số trần trụi (CLAUDE.md pin-dải). CI90 65–88% của Taylor hẹp quá; theo N_eff≈11,5 khoảng 57–98% (≈9/12 năm: 73–83%). Năm khởi đầu thua rõ: 2019 (36%), 2022 (20%). Khung 3T thua tiết kiệm ~38% thời gian ⇒ cửa sổ live 4 tháng thua tiết kiệm nằm trong phân phối bình thường.
- **DT5G → tiết kiệm khi CRISIS/BEAR:** giảm DD (−17,1% → −12,6%; Sharpe 1,82 → 2,07; hơn ~98% placebo tắt ngẫu nhiên) nhưng **TỐN 0,8–1,4pp CAGR khi hai chân cùng quy ước lãi nhàn rỗi** (câu "CAGR gần như không đổi" của Taylor sai do P0 trả 0% cho 59–74% NAV nhàn rỗi). Kết luận khớp KB: DT5G là bảo hiểm, không phải máy tăng lợi nhuận. Không phải phát hiện mới.
- **Ngưỡng lãi (2019+, 2–6 episode/lớp):** hướng khớp trực giác (lãi cao/spread ey−dep1m thấp → kém hơn) nhưng không đủ cơ sở cho ngưỡng; chưa có bằng chứng cho "mức lãi tự nó là gate".
- **Sizing tham chiếu (không phải luật):** tỷ trọng V2.4 tối đa để DD bootstrap p5 ≥ −10%/−15%/−20% là 40%/60%/80% NAV; P(thắng 12T) gần như không đổi theo w (hệ quả toán học: excess pha ≈ w×excess engine) — đổi w chỉ co giãn độ lớn lần thua. Chân tiết kiệm 12T cân lại hằng ngày không thực hiện được.
- **Còn nợ (chưa sửa, ghi để vòng sau nếu user muốn):** chạy P0 với `IDLE_CARRY_TIER=dep1m` (pin1M); chính sách hai chân cùng quy ước lãi, lãi ≤3T, trễ T+1; CI Wilson; **bỏ placebo hoán vị-trong-năm khỏi brief** (không phải null hợp lệ cho dữ liệu cụm tháng — dùng hoán vị khối tháng); đăng ký `data/VNINDEX_pe_only.csv` vào data_registry.

## TỔNG KẾT TOÀN CHUỖI (12/11 20:55 ICT) — trả lời câu hỏi gốc của user
1. **Vì sao backtest 23% mà live kém?** Phần lớn KHÔNG phải BAL/LAG hỏng: (a) cửa sổ live 4 tháng gặp thị trường −6% và V2.4 thua tiết kiệm ở ~38% cửa sổ 3 tháng (bình thường); (b) live chạy hệ KHÁC hệ pin: rổ park custom30V 70–80% NAV (141% gross 02/07) làm lỗ chính, BAL+LAG chỉ ~5% NAV, CAPIT/DISC/egg phần còn lại; park đã tắt 01/10; (c) fidelity thực thi tháng 7–đầu 8 (không JIT/bán rổ, hoãn LAG/CAPIT, lỡ entry do hết usage, ~3pp); (d) engine có hiện vật: ~46% nhãn LAG fill ảo (không có cờ chặn thanh khoản), số pin chỉ là MỘT lần rút tie-break (sd 0,35pp) và nhạy vintage dữ liệu earnings (+0,94pp).
2. **Phân loại deal tốt/xấu?** Chưa phát hiện đặc trưng đơn lẻ nào bền IS→OOS (0/83); value LAG mạnh IS rồi ≈0 sau 2020 (thật). Lực thấp: không bắt ρ 0,3–0,45.
3. **Khi nào an toàn?** Chưa phát hiện điều kiện thời điểm bền (0/6). Đòn bảy thực tế duy nhất kiểm được là TỶ TRỌNG (40/60/80% NAV ↔ DD p5 −10/−15/−20%) và DT5G (giảm DD, tốn CAGR). So với tiết kiệm: V2.4 thắng ~67–90% cửa sổ 12T tuỳ quy ước, thua nặng ở năm khởi đầu 2019 và 2022.
4. **Chờ user:** (i) re-pin R3 / merge vá mergesort; (ii) dòng "so với gửi tiết kiệm" trong báo cáo (`PROPOSAL_savings_row.proposed.md`); (iii) merge fix LAG cache adjusted; (iv) bật `LIQ_ZERO_BLOCK=lag` mặc định cho backtest mới (đang opt-in, sinh fill ảo). 

## Vòng 3 — A4: phân rã −0,48pp (13/11 11:40 ICT; skeptic CONFIRMED medium)
Nguồn: `agents/Taylor/research/live_gap_exec_A4/REPORT.md`, bus `live-gap-exec-A4-20261113`.
- Δ −0,48pp (pin0%, L3 bq 23,39 → L3P pit 22,91) là hiệu ứng THẬT, xác định: ghép cặp 10 seed sd 0,014, 10/10 âm. Toàn bộ nằm ở book LAG (BAL trùng 100%); rải 2021–2024 là chính.
- Cơ chế: `Volume_3M_P50` BQ gồm phiên t; engine tra ADV ở ngày fill ⇒ bản bq cộng khối lượng ngày fill (nhìn trước 1 phiên). pit (t-60..t-1) khớp cách live đọc ADV — SUY LUẬN từ code, chưa đối chiếu lệnh live.
- Tách 2 trục (1 lần/chân, chỉ gợi ý): vá NULL −0,20pp, đổi cửa sổ −0,28pp.
- Dải trên cơ sở production: pin0% 22,91% (DD5 −27,89%) … pin1M 26,61% (DD5 −24,96%). Neo sizing −25,2% GIỮ (user quyết riêng).
- ⚠️ Đính chính của skeptic: chân pin1M chạy trên code nghiên cứu (770393ce2 + 1 dòng chưa commit), KHÔNG phải main đã merge như REPORT §4 ghi — provenance cần ghi lại hoặc chạy lại pin1M sau khi merge IDLE_CARRY_TIER.
- Còn nợ: so ADV lúc đặt lệnh live với pit; 10 seed cho chân fill; ADV thấp giả sau corp-action (cửa sổ 60 phiên trộn khối lượng thô, cả bq lẫn pit).

## Vòng 3 — dòng "so với gửi tiết kiệm" ĐÃ MERGE master (13/11 12:55 ICT)
- Merge `cb40031c6` (nhánh `feat/savings-row-b3-20261113`, 6 commit B2–B5). Skeptic B3/B4/B5 đều CONFIRMED (medium); user duyệt câu ALT cổ tức nguyên văn 13/11 11:20 ICT (provenance ghi ở `period_table_32.py`, comment `SAV_LABEL_ALT`).
- B5 sửa 3 mục của B4: cổng chỉ nhận ĐÚNG 1 dòng V0 (khi `cashDividendReceiving`=0) hoặc ALT (khi ≠0); không đọc được dữ kiện ⇒ BLOCK có bằng chứng (không rơi sang ALT); `report_date` ngày không giao dịch lùi về phiên giao dịch gần nhất.
- Kiểm sau merge: `e2e_gate.py` với `E2E_ROOT_BRANCH=0` trên master canonical ⇒ COMPLETE, DELIVER_RC 0 (`agents/Taylor/research/live_gap_exec_B5/e2e_postmerge/gate_run.log`; phải dùng `python3` hệ thống vì `wc_venv` thiếu pymupdf — artifact_lint cần nó). report_v2_selfcheck 3 TZ rc=0.
- Nhánh gốc repo mike là `master` (không phải `main`).
- Gợi ý skeptic chưa làm (tuỳ chọn): `norm()` từng dòng ứng viên trước khi so khớp chính xác trong `check_report`.

## Vòng 3 — A5: pin chính xác + bằng chứng neo sizing (13/11 14:50 ICT; skeptic CONFIRMED, confidence HIGH)
Nguồn: `agents/Taylor/research/live_gap_exec_A5/REPORT.md`, bus `live-gap-exec-A5-20261113`. User chỉ đạo 13/11 14:09: neo phải dựa bằng chứng thật; cho chạy lại pin1M.
- **Pin chính xác, trùng byte A3/A4, self-check 0 VND 8/8 chân:** pin0% CAGR 22,91%, DD5 −27,89%, md5 `80f509ec` (main `7f25febc1`, worktree sạch) … pin1M CAGR 26,61%, DD5 −24,96%, md5 `e2de0ac4`. ⚠️ pin1M chạy trên nhánh research `e9a9aed1a` (= `770393ce2` + 1 dòng `LAG_ADV_SRC` default pit) vì `IDLE_CARRY_TIER` CHƯA có trên master (knob ở `75fba8a9e`/`9327043d2`, tier `dep1m` ở `d3c376310`/`3c9e3d13d`) ⇒ hai đầu dải chạy trên 2 cây code; pin0% trên main = pin0% A3 nên phần khác nhau trơ.
- **Neo −25,2% = ledger `4707bcbe` (sexies 09-28) CÓ fill ảo:** park 0,3, `LIQ_ZERO_BLOCK` chưa tồn tại (≡ off), ADV bq, quicksort; chạy lại trùng byte. Thang 1 trục: bỏ fill ảo (`LIQ_ZERO_BLOCK=lag`) = **−3,96pp DD5 (park 0,3) / −4,17pp (park 0)**; mergesort, cache LAG adj v2, ADV pit mỗi trục ≤0,34pp. Skeptic: 256/278 fill ảo nằm ở mã có median khối lượng 60 phiên = 0 (không giao dịch được ở mọi cỡ NAV), giữ 41,8% tiền mua LAG của L1 — KHÔNG phải artefact trần capacity 50B.
- **Live:** ADV tại gate `cap_lag_orders` = pit ở 29/32 cặp (mã, ngày) trên 48 lệnh mua LAG thật (|log| ≤0,002); bq-ngày-fill lệch ±4–10% và nhìn trước 1 phiên; 0/48 lệnh vượt trần (ở NAV ~1 tỷ trần không ràng buộc). DD thực tế sleeve BAL+LAG live −23,2% (76 phiên, 2 TK, 1–4 mã) — nằm trong phân phối của cả hai engine (p10–13 engine sạch, p5–7 engine fill ảo): N=1, KHÔNG phân biệt được engine.
- **Kết luận có cơ sở:** engine `lag`+`pit` trung thực hơn live (code live fail-closed chặn ADV ≤0/NULL; ADV tái lập trên lệnh thật; thang 1 trục). Neo −25,2% không còn cơ sở. Áp luật neo user 10-08 (đầu sàn ở park XẤU HƠN trong {0; 0,3}) trên engine trung thực: **−29,09%** (park 0,3; skeptic: coi là khoảng −28,5…−29,1) hoặc **−27,89%** nếu chỉ tính park live (0). USER QUYẾT — chưa đổi neo.
- **Khoảng trống còn mở (không phủ nhận kết luận):** chưa có chân small-NAV (1–2 tỷ) trên engine mới; luật hủy `max_fill_days=5`/`min_fill_pct=0,30` và trần 20%×1/2 account không có ở engine; DD5 nên báo dải theo seed/độ dài khối (L=10/21/42); ADV thấp giả sau tách/thưởng chưa đo từng mã; nên cherry-pick `IDLE_CARRY_TIER` lên master để cả dải chạy một cây code.

## Vòng 4 — A6: một cây code, small-NAV, DD5 theo dải, ADV sau sự kiện CP (13/11 15:45 ICT; skeptic CONFIRMED, confidence MEDIUM)
Nguồn: `agents/Taylor/research/live_gap_exec_A6/REPORT.md` (job `Taylor_20261113_075112`), bus `live-gap-exec-A6-20261113`, raw log `logs/verify_20261113_083355_1303464.log`. PAPER, không đổi production/neo, KHÔNG merge.
- **Nhánh carry** `research/live-gap-A6-carry-20261113` @`262c117c3` = main `7f25febc1` + 7 commit `IDLE_CARRY_TIER`: pin0% `80f509ec` và pin1M `e2de0ac4` TRÙNG BYTE trên cùng 1 cây (skeptic đối chiếu md5 .gz đã pin); self-check 0 VND; selfcheck 21 file × 3 TZ cùng mã thoát với main (5 FAIL có sẵn ở cả hai). **CHƯA merge: cần arch-reviewer** (skeptic không thay).
- **DD5 theo dải** (15 cấu hình L∈{10,21,42}×5 seed, KHÔNG độc lập): neo cũ −24,77 [−25,20; −23,55]; L3P park0 −27,30 [−27,89; −26,63]; L3P park0,3 **−28,54 [−29,09; −27,99]**; pin1M −24,59. **−29,09% là cạnh dưới của dải, không phải tâm**; seed 12345/L21 sâu nhất 15/15. Chênh ghép cặp so với neo: park0,3 −3,89pp, park0 −2,87pp, bền; bất định neo ~±0,6pp.
- **Small-NAV (park0, pin0%):** chênh DD5 ghép cặp L3P−L1: 50B −4,11 / 2B −1,28 / 1B −1,58pp ⇒ ~4pp KHÔNG hằng số theo NAV. DD5 tuyệt đối 1B L3P −32,75 [−33,34; −30,21] (MaxDD −25,5), 2B −32,65, so 50B −27,30.
- **⚠️ Skeptic (killer objection):** engine bán HẾT tại Open, slippage ≤0,5%, KHÔNG có trần ADV phía bán (`simulate_holistic_nav.py:732,990`); mua mới bị trần 20% pitADV. Ở 1B sổ LAG giữ mã ADV median ~116 tr/ngày ⇒ **DD5 −32,75% là SÀN nông (lạc quan), CAGR 1B 27,04% bị thổi**; không dùng làm neo.
- **Fidelity engine 1B vs live chưa giải thích:** trần ADV ràng buộc 65,5% ngày mua LAG ở engine 1B, live 0/48 lệnh.
- **ADV sau thưởng/cổ tức CP:** (mã,ngày) ảnh hưởng 3,4–4,3%; lệnh cap sai 1,03% (1B) / 3,79% (50B); vốn mua bị cắt ≤0,69% (cận trên). Thật nhưng nhỏ; DD5 sau quy đổi CHƯA đo. Ghi chú: chênh 50B −4,11 trộn ledger khác commit/cache LAG (vint vs adj) — đã công bố.
- **Rerun skeptic đề nghị (chưa làm, chưa dispatch):** knob trần ADV phía bán (20%/ngày, carry phần dư) rồi chạy lại S1/S2 L1/L3P + DD5; 50B L1 trên cây A6 + cache adj; chẩn đoán vì sao engine 1B chọn mã LAG kém thanh khoản hơn live; knob adj-ADV đo DD5.
- **Hệ quả cho quyết định neo (USER QUYẾT, chưa đổi):** ngoài A/A'/B còn câu hỏi MỚI — neo áp cho CỠ NAV nào. Live ~1 tỷ; bằng chứng 1B không dùng làm neo được tới khi có trần bán. Khuyến nghị giữ A (−29,09%) làm sàn tạm cho engine 50B, nhận rõ đó có thể quá nông ở NAV nhỏ.

## QUYẾT ĐỊNH USER 13/11 16:39 ICT (`decided_by: user`) — neo sizing DD = phương án A
- **Neo sizing DD5 = −29,09%** (engine `lag`+`pit`, park 0,3 = đầu sàn của dải park XẤU HƠN, luật neo 10-08); thay neo cũ −25,2% (ledger `4707bcbe`, có fill ảo). KHÔNG còn trích −25,2% như neo hiện hành.
- Ràng buộc đi kèm (skeptic A6): −29,09% là **cạnh dưới dải bootstrap** của engine 50B và có thể NÔNG ở NAV live ~1 tỷ (engine không có trần ADV phía bán). Câu hỏi "neo cho cỡ NAV nào" + rerun trần bán: chưa dispatch, chờ user.
- Không code/config nào đọc neo (grep `mike/bin`, `trading_bot`, `trading_rules.json` = 0) ⇒ KHÔNG đổi production; chỉ đổi con số trích dẫn trong KB/báo cáo/số pin.
- Cùng lượt: xoá `live_gap_exec_E/{sb,sbv}` (đĩa 98%→94%); đóng bus `nav-loss-brake-review-20261113` = A (giữ cảnh báo); đóng `fleet-backup-gh001-history-rewrite` = A → dispatch Wags `Wags_20261113_094054` thực thi (bundle backup → filter-repo → push mike-fleet).

## GH001 history rewrite — XONG 13/11 18:35 ICT (user duyệt A 16:39 + 17:34; Wags `Wags_20261113_112633`)
- `master` rewrite gỡ 17 file `research/**/*.pkl|parquet` >100MB; push `mike-fleet` fast-forward `fc5bd02d → f1e5e9d31` OK. Mike verify độc lập: blob >100MB = 0, `git fsck` rc=0, tree trước/sau rewrite TRÙNG BYTE (`ffa8cde8`), remote = ancestor của master (+1 commit consolidate sau push), 47 thay đổi chưa commit của session khác còn nguyên, bundle cũ `git bundle verify` OK. Commit trước `fc5bd02d` giữ nguyên SHA; SHA đổi: master `a31c5ef3c→f1e5e9d31`, `feat/savings-row-20261112` `418667a32→d789849dd`, `feat/savings-row-b3-20261113` `4b34e8303→cc966974e`(Wags ghi cc966974e), `fix/book-clearing-lag-dd-zone-gate-20261113` `86508eed3→36ffb5449` (PARKED, chưa merge, patch `kb/projects/book-clearing-dd-zone-parked-86508eed3.patch`).
- File 17 pkl/parquet vẫn trên đĩa, đã .gitignore. Reflog repo chính còn commit cũ (chưa gc). Backup cron 00:00 ICT push từ master mới. Còn giữ: bundle 4,0GB `/home/trido/git_bundles/mike_all_pre_gh001_rewrite_20261113.bundle` + clone `rw_20261113b.git` — chờ user cho dọn. PAT hết hạn 15/11 07:17 ICT (việc riêng của user).
