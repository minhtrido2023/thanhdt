# AMH (Adaptive Market Hypothesis, Andrew Lo) — rà soát độ thích nghi của hệ, 2026-09-10

> Người viết: Mike (trả lời user, topic 1547589883999158363). Nguồn: code + artifact thật tại
> `/home/trido/thanhdt/WorkingClaude` (mtime kiểm 2026-09-10), `data/results_registry.md`, KB.
> Trạng thái: ĐÁNH GIÁ + ĐỀ XUẤT, chưa dispatch nghiên cứu nào.

## 1. Kiểm kê "AMH arc" tháng 6/2026 (V6 "Tứ Trụ") — cái gì còn sống

| # | Proposal | Script | Trạng thái 2026-09-10 | Bằng chứng |
|---|---|---|---|---|
| 1 | Edge Health Monitor (rolling IC 12M, fwd-3M, theo lens 8L × super-sector; LAG realized ledger; CAPIT edge) | `edge_health_monitor.py` | **SỐNG**, chạy hàng ngày qua `papertrade_daily.sh` | `data/edge_health_{ic,matrix,status}.*`, `lag_edge_health.csv` mtime 09-10 08:37 |
| 2 | Vol-target overlay | `voltarget_overlay.py` | Chạy 1 lần 06-09, KHÔNG wire | `data/voltarget_results.csv` 06-09; registry H3 DD-cutter FAIL đóng nhánh này |
| 3 | Fitness matrix (signal × DT5G state) | `fitness_matrix.py` | **CHẾT KỸ THUẬT** — path Windows `\data\`, không chạy được trên Linux; chưa có verdict | output 06-09 |
| 4 | Ecology dashboard (opportunity/uniformity/mood) | `ecology_dashboard.py` | **REFUTED** walk-forward 07-13 (mood đảo dấu IS→OOS) | registry `## 2026-07-13 — ECOLOGY DASHBOARD (AMH#4)`; artifact đứng từ 07-13 |
| 5 | Biodiversity test (orthogonality gate cho chiến lược mới) | `biodiversity_test.py` | **CHẾT KỸ THUẬT** (path Windows); nguyên tắc sống dưới dạng khác (§2) | output 06-09 |
| — | AMH Cockpit (V6 core/value/capit/grind) | `amh_cockpit.py` | Chết từ 07-07; gỡ khỏi Telegram 06-26 khi V2.4 go-live. V6 không go-live. | `data/amh_cockpit.md` 07-07 |

**Edge Health đã đi vào production ở 2 chỗ (closed-loop thật, không chỉ chẩn đoán):**
- `pt_v22_dt5g.py:770-790` — allocator w_LAG **edge-conditional** (deploy 06-13): state 3/4/5 → 0,65 CHỈ khi
  `mean12` (trailing-12M mean realized LAG post-return) ≥ 4%, ngược lại 0,50. **Hiện mean12 = −0,16%
  (asof 07-29, n=609) ⇒ gate ĐANG kích hoạt, w_LAG = 0,50.**
- `pt_v22_dt5g.py:286-294` — EXBULL momentum suppression, LIVE 06-11 (user duyệt). ⚠️ Dòng
  "dormant fix… chưa live" trong `edge_health_block.md` là text STALE — cần sửa.
- CAPIT edge health (HEALTHY → carve 70%) chỉ đến cockpit/`pt_sleeve_allocator.py`, KHÔNG đến bot.

**Tín hiệu edge hôm nay (as_of 2026-06 — trễ 3 tháng cấu trúc do fwd-3M):**
`mom_200` và `D_RSI` **FLIPPED** (IC +0,06 → −0,02/−0,07, cả ALL và CYCLICAL) từ 04/2026;
value/quality (PE, ROIC5Y, ROE_Min5Y) **STRENGTH**. BAL = momentum SIGNAL_V11 ⇒ đây chính là bức
tranh AMH của "BAL 2025-26 âm" mà user đang cho Taylor nghiên cứu.

## 2. Độ thích nghi theo tầng — đối chiếu 3 luận điểm AMH của Lo

Lo: (a) edge waxes & wanes theo chu kỳ, không chết hẳn; (b) lợi nhuận phụ thuộc "ecology" (ai đang
chơi, bao nhiêu vốn đuổi cùng edge); (c) survival > optimization — đa dạng chiến lược quan trọng hơn
tối ưu một chiến lược.

### Đã adapt tốt (phần lớn by-construction, không phải tham số học từ lịch sử)
1. **8L rating** — `rating_8l.py` chấm bằng `rank(pct=True)` cross-sectional, sector-neutral trong route,
   MỖI LẦN CHẠY ⇒ tự hiệu chuẩn theo phân phối hiện tại, không hard-threshold (docstring dòng ~884 nói
   rõ lý do). Gate binary ≤3, không dùng làm return-tilt. Re-tune bucket 16/16 NO-GO (07-11) — đúng
   AMH: đừng tối ưu theo mẫu quá khứ.
2. **DT5G** — adapt về TRẠNG THÁI (5 state, macro cap, breadth guard PIT), KHÔNG adapt về THAM SỐ (frozen,
   "insurance"). Đây là "survival valve" đúng nghĩa (c).
3. **Allocator w_LAG edge-gate** — vòng phản hồi thật, đang hoạt động (mục 1).
4. **EXBULL momentum suppression** — fitness-conditional theo state (momentum crash trong hưng phấn).
5. **custom30V parking** — rebalance định kỳ theo yieldcombo rank ⇒ universe tự cập nhật.
6. **Governance = biodiversity gate thực dụng**: quant-skeptic bắt buộc, IS/OOS, DSR/PBO, per-year LOO,
   `paper_programs_registry.json` có end-date, checkpoint cứng (LAG ADV 12-15/03-31), user-held review
   (VPI/BAL 09-16). Fear-buy sleeve + margin Loại-2 đi kèm điều kiện Bobby BLIND.

### Khoảng trống (theo đúng 3 luận điểm)
| # | Khoảng trống | Luận điểm | Mức |
|---|---|---|---|
| G1 | **BAL không có edge-gate đối xứng với LAG.** Momentum FLIPPED 5 tháng nhưng phản ứng duy nhất là EXBULL-suppress (state-conditional) + user hold VPI bằng tay. LAG có `mean12≥4%` gate, BAL không có ledger realized per-trade lẫn gate. | (a) | CAO |
| G2 | **Chỉ báo edge trễ 3 tháng** (fwd-3M IC). `lag_edge_health` là chỉ báo nhanh nhưng đứng khi không có trade (asof 07-29 vì parking). Không có chỉ báo edge nhanh cho BAL. | (a) | CAO |
| G3 | **Verdict alive/fading/dead theo cửa sổ 12M cố định + t≥2** — không có change-point detection (CUSUM/Bayesian) ⇒ không có xác suất "edge đã đổi chế độ", chỉ có nhãn. | (a) | TRUNG |
| G4 | **Không đo mức hiệu quả của thị trường theo thời gian** (Lo-MacKinlay variance ratio, rolling Hurst, autocorr) và không nối với proxy ecology VN (tỷ lệ retail, margin/vốn hoá, dòng ngoại, tài khoản mở mới). Đây là lõi AMH nhưng chưa có series. | (b) | TRUNG |
| G5 | **Ecology đã REFUTED làm tín hiệu HƯỚNG**, nhưng chưa test làm **biến ĐIỀU KIỆN** cho edge (fitness matrix chết trước khi validate). Breadth-tercile PIT đã là trục 2 mặc định — chưa áp lên IC momentum/value. | (b) | TRUNG |
| G6 | **2/5 proposal chưa có verdict** (fitness, biodiversity) — chết vì path Windows, không vì bị bác. | — | THẤP (kỹ thuật) |
| G7 | **Không có protocol structural-break.** Nâng hạng FTSE, KRX, rút ngắn T+, tổ chức hoá ⇒ ecology đổi mạnh nhất 10 năm; DT5G/8L frozen mà không có trigger "sự kiện X ⇒ bắt buộc re-validate". Frozen theo LỊCH SỬ đúng; frozen theo SỰ KIỆN là lỗ hổng. | (b)(c) | CAO (dài hạn) |
| G8 | Text stale trong `edge_health_block.md` ("EXBULL-suppression chưa live") ⇒ chẩn đoán sai cho người đọc. | — | THẤP |

## 3. Hướng explore (paper-only, prereg + quant-skeptic, KHÔNG wire trực tiếp)

Thứ tự theo giá trị/chi phí:
1. **BAL edge-gate đối xứng LAG (G1+G2)** — dựng `bal_edge_health.csv` (realized per-trade BAL post-return,
   cùng schema tinh thần `lag_edge_health.csv`) + IC mom nhanh hơn (fwd-1M bên cạnh fwd-3M). Luật ứng
   viên: mean12_BAL < thr ⇒ giảm slot/size BAL hoặc nới parking; prereg thr trước, không quét. Nối thẳng
   vào review VPI/BAL 09-16 và job Taylor "BAL 2025 âm".
2. **Market-efficiency gauge VN (G4)** — series tháng: variance ratio VNINDEX (q=2,5,10), rolling Hurst,
   autocorr 1-lag cross-sectional; ghép proxy ecology (retail share, margin/mktcap, net foreign, tài khoản
   mới). Deliverable: 1 biểu đồ + 1 bảng, trả lời "edge momentum suy giảm CẤU TRÚC hay CHU KỲ".
3. **Change-point trên IC series (G3)** — CUSUM/BOCPD thay nhãn 12M; output P(regime-shift) đưa vào
   `edge_health_block.md`. Rẻ, không đụng production.
4. **Hồi sinh fitness matrix trên harness hiện tại (G5+G6)** — IC signal × (DT5G state × breadth tercile
   PIT). Câu hỏi cụ thể: momentum chết ở mọi state hay chỉ NEUTRAL breadth-thấp.
5. **Chính thức hoá biodiversity gate (G6)** — vào skill `quant-research`: candidate mới nộp correlation
   với BAL/LAG/parking theo state + điểm "sống nơi incumbent chết". Áp ngay cho mania indicator và fear-buy.
6. **Structural-break protocol (G7)** — danh mục sự kiện (nâng hạng, KRX, T+, luật margin) + checklist
   re-validation bắt buộc cho DT5G/8L SAU sự kiện. Không đổi tham số trước; chỉ thêm trigger.
7. **Fix nhỏ (G8+G6)** — sửa text stale, đổi path Windows 2 script (11 file di sản đã ghi ở CLAUDE.md).

## 4. Caveat phải giữ
- Tín hiệu AMH-inspired duy nhất đã test hướng (ecology mood) **REFUTED** — mọi hướng trên là CHẨN ĐOÁN/
  GATE, không phải return-enhancer; kỳ vọng ΔCAGR≈0, mục tiêu là sống qua đổi chế độ.
- N chu kỳ VN ~2-3 ⇒ dùng causal + judgment (như mandate 08-25), không dùng p-value làm cổng duy nhất.
- DT5G/8L: đừng để "adapt" thành cớ re-tune theo lịch sử — CLAUDE.md đã cấm, và AMH cũng không đòi điều đó.

## 5. THỰC THI — user duyệt cả 7 hướng, 2026-09-10 20:15 ICT

Thứ tự Mike chốt = (giá trị × ràng buộc thời gian) ÷ chi phí. #7 lên đầu vì nó là điều kiện cần
của #4 (script chết thì không nghiên cứu được), rẻ, và làm xong ngay trong lượt.

| Thứ tự | Hướng | Trạng thái | Bằng chứng |
|---|---|---|---|
| 1 | #7 Fix kỹ thuật | **XONG** | commit `30878a9b` — 3 script đổi `\data\`→`/data/`; `fitness_matrix.py` + `biodiversity_test.py` chạy lại được sau ~3 tháng chết; gỡ dòng "EXBULL-suppression chưa live" (SAI) |
| 2 | #1 BAL edge-gate | dispatch Taylor `Taylor_20260910_131906` (opus/high) | deadline review VPI/BAL **09-16** |
| 3 | #3+#4 Change-point + fitness matrix | dispatch Taylor `Taylor_20260910_131908` | gộp 1 job vì cùng `edge_panel.csv`; truc 2 = breadth-tercile PIT theo quy ước 08-22 |
| 4 | #2 Market-efficiency gauge | dispatch Taylor `Taylor_20260910_131910` | variance ratio / Hurst / autocorr + proxy ecology VN |
| 5 | #5 Biodiversity gate | **XONG** | `.claude/skills/quant-research/SKILL.md` bước **18** + 1 dòng checklist |
| 6 | #6 Structural-break protocol | **XONG** | `kb/projects/amh-structural-break-protocol-20260910.md` + `kb/structural_break_watch.json` (6 sự kiện) + con trỏ ở `current_ops.md` § Macro watch |

**Kết quả #4 chạy lần đầu sau khi fix (full-sample, CHƯA phải kết luận):** `fitness_matrix.py` cho
momentum trong NEUTRAL có IC +0,101 (t=4,75) trên TOÀN mẫu 2014-2026 — trong khi edge-health nói
`mom_200` FLIPPED từ 04/2026. Hai con số này **không mâu thuẫn**: một cái là trung bình 12 năm, một
cái là 12 tháng gần nhất. Đó chính xác là lý do #3+#4 tồn tại — phải tách "momentum chết ở mọi
state" khỏi "momentum chết ở đúng chế độ hiện tại".

**Kết quả #5 chạy thật (incumbent = MOMENTUM, 2026-09-10):** VALUE_PE PASS (corr −0,23; sống sót
0,79 trong quý xấu nhất của incumbent; ΔSharpe +0,24), QUALITY_ROIC PASS, DT5G_TIMING PASS; RSI
FAIL (corr 0,60), FLOW_CMF FAIL (ΔSharpe −0,03), PBZ FAIL (corr 0,62). Ba cái FAIL đều là tín hiệu
tử tế nếu đo một mình — đó là lý do cổng này đáng tồn tại.

**Ràng buộc giữ nguyên cho cả 3 job đang chạy:** PAPER-ONLY, prereg trước khi backtest, ngưỡng chốt
trước không quét grid, N = số sự kiện độc lập, khai trước kỳ vọng ΔCAGR≈0, và KHÔNG wire gì —
mọi thay đổi production vẫn phải qua quant-skeptic + user duyệt.

## 6. Kết quả job C (#2 market-efficiency gauge) — XONG 2026-09-10, job `Taylor_20260910_131910`

**Câu trả lời: CHU KỲ, không phải cấu trúc** — nhưng có một cải thiện cấu trúc THẬT ở một TẦNG KHÁC.
Đọc đầy đủ: `agents/Taylor/research/vn_market_efficiency_20260910/KETLUAN_vn_market_efficiency_20260910.md`.

| Tầng | Thước đo | Kết quả |
|---|---|---|
| Vi mô (ngày) | AC(1) lợi suất ngày từng mã, trung vị cross-sectional | **CẤU TRÚC** — break 2010, p_perm 0,0017 (rổ cân bằng 45 mã: 0,0007); 0,17-0,25 → ~0,02, chưa từng về lại |
| Chỉ số | VR(2/5/10) Lo-MacKinlay, Hurst DFA | **Không có break đo được** (p_perm 0,68-0,99) |
| Trung hạn cross-sectional (**đúng tầng BAL đứng**) | IC mom(6-1) vs fwd-3M | **Không có break** (p_perm 0,216) — chu kỳ rõ, 3 đáy đều hồi |

**Ba điều quan trọng nhất cho quyết định:**
1. **Không có bằng chứng cho "momentum VN chết vì thị trường hiệu quả lên".** Tầng hiệu quả lên thật
   (AC ngày) KHÔNG phải tầng BAL khai thác, và tương quan giữa hai tầng là **ÂM** (ρ = −0,696, p=0,001,
   N=19 năm; t=−2,32 khi kiểm soát vol) — ngược hẳn trực giác AMH thô.
2. **BAL yếu 2025 giống ĐÁY CHU KỲ hơn giống mục nát.** Đáy 2020-23 (IC −0,027) KHÔNG sâu hơn đáy
   2007-09 (−0,063); 2024 +0,127, 2026 (T1-T5) +0,139. ⇒ ủng hộ G1 (cần *edge-gate* giảm size ở đáy
   chu kỳ), KHÔNG ủng hộ việc BỎ BAL.
3. **Nhãn "FLIPPED" hôm nay đang TRỄ PHA thật — Mike đã kiểm chứng độc lập.** Đọc thẳng
   `data/edge_health_ic.csv`: mom_200 IC 2026-04 = **−0,060** · 2026-05 = **+0,285** · 2026-06 =
   **+0,382**. Hai hệ đo độc lập cùng nói momentum đã quay đầu DƯƠNG trong Q2/2026. Nhãn FLIPPED còn
   treo là độ trễ cửa sổ 12M ⇒ **đừng đọc nhãn FLIPPED như tuyên bố về hiện tại**. Đây chính là G2/G3.

**Dữ liệu hệ sinh thái — trung thực về cái KHÔNG có:** dòng tiền khối ngoại ròng CÓ thật (VNDirect
finfo, 1.998 phiên từ 2018-08-30). Tỷ lệ retail, dư nợ margin toàn thị trường, tài khoản mở mới —
**KHÔNG có nguồn chuỗi nào trong tay**, chỉ có điểm rời rạc thứ cấp chưa đối soát. ⚠️ Bẫy tên:
`data/margin_cycle_detector.csv` KHÔNG phải margin debt (đó là chu kỳ biên lợi nhuận gộp doanh nghiệp).

**Giới hạn phải mang theo khi trích:** N chu kỳ VN ≈ 3 ⇒ "không phát hiện được break" ≠ "chắc chắn
không có break". `ac1_cs` trước 2010 lẫn cơ học vi cấu trúc (biên độ, giá cũ, universe 160 mã) — không
tách được "thị trường học được cách định giá" khỏi "thị trường thôi bé tí". Đây là thước đo CHẨN ĐOÁN,
không phải tín hiệu; không luật giao dịch nào được dẫn xuất từ nó.

**Kiểm chứng của Mike (artifact, không tin self-report):** selfcheck estimator 8/8 PASS đọc từ
`run_selfcheck.txt`; ba con số mom_200 IC recompute độc lập khớp tuyệt đối; `git status` sạch trên mọi
`.py` production. **Đã dispatch quant-skeptic** (đang chạy) vì kết luận này sẽ được viện dẫn tại review
VPI/BAL 09-16 — tức là nó decision-adjacent, dù bản thân nó không đề xuất wire gì.
