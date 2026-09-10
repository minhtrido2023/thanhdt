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

## 7. Kết quả job B (#3 change-point + #4 fitness matrix) — XONG, job `Taylor_20260910_131908`

Đọc đầy đủ: `agents/Taylor/research/amh_changepoint_fitness_20260910/CONCLUSION.md`.

### #3 Change-point — **NO-GO**
CUSUM và BOCPD đều **tệ hơn** nhãn 12M đang có: chậm hơn 2 tháng (median lag 6,0 vs 4,0),
false-alarm 35%, chỉ 5% alarm trùng điểm gãy thật, và **không có dose-response** (h=4/5/6 →
56,5%/35,0%/46,7%, không đơn điệu ⇒ nhiễu). Lý do gốc: với null **block-permutation** trung thực
(block=3, đúng độ trùm fwd-3M), cả 10 signal × 12,5 năm chỉ còn **3 điểm gãy có ý nghĩa** — null
i.i.d. ngây thơ cho 17, tức 14/17 là ảo ảnh. **Chuỗi IC gần như không có điểm gãy để phát hiện.**
⇒ KHÔNG thêm dòng `P(regime-shift)` vào `edge_health_block.md`.

### Sản phẩm phụ đáng giá nhất — cổng `|t|≥2` đang PHÓNG ĐẠI 1,5-2,4×
`edge_health_monitor.py::edge_row()` tính t-stat bằng **n danh nghĩa** (150), trong khi chuỗi IC
fwd-3M **chồng lấn by construction** (lấy mẫu tháng trên cửa sổ forward 3 tháng ⇒ MA(2); ac1 đo
được 0,33-0,71). **Mike đã tự recompute độc lập từ `data/edge_health_ic.csv`, khớp tuyệt đối:**

| signal | ac1 | t danh nghĩa | n_eff | t hiệu dụng |
|---|---|---|---|---|
| mom_200 | +0,66 | +3,68 | 31 | **+1,67** |
| ROE_Min5Y | +0,71 | +4,03 | 26 | **+1,67** |
| PE | +0,55 | −6,20 | 44 | −3,34 |
| FSCORE | +0,49 | +4,90 | 52 | +2,88 |

⇒ **Nhãn `FLIPPED` của mom_200 lẽ ra đã không được phát ra.** Cộng với dữ liệu 05-06/2026 dương
mạnh, đây là bằng chứng thứ hai độc lập cho cùng kết luận ở §6. **CHƯA SỬA** — `classify()` là đầu
vào của allocator edge-gate LIVE ⇒ đã dispatch quant-skeptic (job `verify_20260910_135826`).

### #4 Fitness matrix — momentum chết ở MỌI Ô sau 2020, không trục nào cứu được
Tách IS(2014-19)/OOS(2020+), mốc pre-registered: `mom_200` **8/8 phạm vi dương ở IS** (6/8 có ý
nghĩa) và **8/8 phạm vi ≈ 0 ở OOS** (0/8 có ý nghĩa, mọi |t| < 1). NEUTRAL: IS +0,164 (t 5,09) →
OOS +0,005 (t 0,16). Leave-one-year-out 2020+ chạy trong [−0,027; +0,015] ⇒ **không phải hiệu ứng
một năm cá biệt**. `D_RSI` giống hệt.

> **Hệ quả cho review VPI/BAL 09-16: KHÔNG thể cứu BAL bằng cách thêm một cổng regime/breadth.**
> Vết gãy là **THỜI GIAN (~2020)**, không phải chế độ thị trường. Muốn giữ BAL thì lý do phải nằm
> ở chỗ khác (SIGNAL_V11 ≠ `mom_200` thô, yieldcombo, hoặc vai trò đa dạng hoá) — ủng hộ hướng
> **G1 edge-gate**, bác hướng regime-conditioning.

Bức tranh AMH gọn: mọi signal **dựa trên GIÁ** (momentum, RSI, CMF, C_L1M) sụp về ~0 quanh 2020;
**định giá cơ bản** mạnh lên (PE: IS −0,014 ns → OOS **−0,081\***, LOO [−0,091;−0,070], có ý nghĩa
ở CẢ 3 tercile breadth); **sàn chất lượng giữ nguyên** (ROE_Min5Y +0,052\* → +0,063). PB_z **đảo
dấu thật** (+0,056 IS → −0,064\* OOS). ⇒ Phần hệ thống đang đứng vững (8L: cổng nhị phân trên sàn
chất lượng + `1/PE` trục trội) **đúng là phần dữ liệu nói vẫn còn sống**.

Breadth-tercile **tách rất yếu** một khi đã điều kiện hoá theo state (momentum không đơn điệu:
+0,028/+0,083/+0,073). Trục có sức tách thật là DT5G. Chỉ **30/130 ô (23%)** đạt hạng kết luận;
BEAR và EXBULL không có ô nào đọc được.

### ⚠️ ĐÍNH CHÍNH việc Mike đã làm ở #7 — `fitness_matrix.py` cũ có LOOK-AHEAD
Job B phát hiện bản cũ gán state cho tháng bằng **modal state của CẢ tháng** (dòng ~73) ⇒ dùng
phiên SAU ngày hình thành vị thế, **lệch state-PIT ở 24/150 tháng (16%)**; và đọc
`data/dt5g_vnindex.csv` thay vì bảng canonical (lệch 52/3121 phiên, file đứng từ 07-09).
**Mike đã verify dòng 73 tồn tại thật.** Con số "momentum NEUTRAL IC +0,101 (t=4,75)" Mike trích
ở lượt trước là từ script này ⇒ **không dùng được**. Đã gắn header SUPERSEDED (commit `66e5ec7e`);
bản đúng là `fitness2.py`. Sửa path Windows (commit `30878a9b`) làm script CHẠY được, **không**
làm kết quả của nó ĐÚNG — hai việc khác nhau.

## 8. Kết quả job A (#1 BAL edge-gate) — **NO-GO**, job `Taylor_20260910_131906`

Đọc đầy đủ: `agents/Taylor/research/bal_edge_gate_20260910/CONCLUSION_bal_edge_gate_20260910.md`
(+ `PREREG.md` viết TRƯỚC mọi leg backtest). **Không wire gì; không có thay đổi production nào cần
user duyệt.**

### Hai đính chính tiền đề của chính bản rà soát này
**(a) `lag_edge_health()` KHÔNG đọc fill thật.** Nó dựng lại *cohort vào lệnh* LAG từ cache earnings,
vào T+5, giữ đúng 25 phiên của sổ, lấy price return thuần — không sizing, không slot, không parking.
Vì thế nó KHÔNG bao giờ đứng khi sổ đang park. Tiền đề "ledger sẽ đứng vì BAL đang parking" trong
brief của Mike **SAI**; trở ngại thật khác và nặng hơn.

**(b) BAL là sổ CHỈ-BULL by construction.** Mọi tier mua trong `signal_v11_sql.py` đều đòi
`state5 IN (4,5)` (Mike verify: dòng 127-134, 3 tier chính). DT5G có **0 phiên BULL/EXBULL** trong
2014, 2015, 2016, 2019, 2022, 2023 ⇒ **BAL im lặng 6/13 năm**, cohort chỉ đến trong **10 episode**.

⇒ **Cổng đối xứng là bất khả về CẤU TRÚC, không phải vấn đề tinh chỉnh.** Đọc causal tại thời điểm
mở từng cụm tín hiệu: gate MÙ (`n12=0`) ở 3/6 cụm, và ở phần còn lại nó **xếp hạng NGƯỢC** — sẽ
chặn cụm tốt nhất (03/2025, +12,49%) và cho qua cụm tệ nhất (08/2025, −6,22%).

### Backtest — 8 leg, harness chứng minh hợp lệ 2 lần độc lập
`ctrl` tái lập pin R3 tuyệt đối (28,86% / 1,90 / −17,79% / 1,62 / 1.178,01B, self-check **0 VND**),
**md5 `7d053e6201c9d107685ff4d1dd9d2d2a` — Mike verify khớp pin trong `results_registry.md`**; leg
`inert` (bản copy engine, chạy không mask) cho CSV byte-identical cùng md5 ⇒ mọi chênh lệch bên dưới
là do gate và chỉ do gate.

**4 lý do độc lập để NO-GO:**
1. **MaxDD BIT-IDENTICAL ở cả 8 leg** (−0,17785101, đáy 2018-07-05). Đáy đó nằm trong cửa sổ gate có
   **0 ngày hoạt động** ⇒ gate không chạm được đúng cái drawdown nó sinh ra để bảo hiểm. Tiêu chí
   prereg #1 trượt thẳng.
2. **PLACEBO THẮNG.** Mask theo lịch, không mang thông tin edge-health nào, cho **+0,40pp** so với
   gate thật **+0,30pp**, và thắng mọi biến thể ladder. ⇒ +0,30pp không phải "gate biết điều gì đó",
   nó là "giữ ít slot BAL hơn trong 2020-2024".
3. **Leave-one-episode-out: 1/4.** Ba episode momentum THẬT SỰ bị gắn FLIPPED đều **mất tiền** khi
   cắt slot (−0,09 / −0,01 / −0,10pp); chỉ episode 01/2026 giúp (+0,12pp). Sign test p=0,625. Bốn
   episode cộng lại **−0,08pp**; toàn bộ +0,23pp tổng đến từ **residual NGOÀI chúng**.
4. **Không có dose-response**: 12→10 +0,31 · 12→8 +0,16 · 12→6 +0,30 · 12→4 +0,36 · 12→0 −2,97.
   Nhiễu quanh +0,3 rồi vực. Ngược hẳn hình dạng của một ngưỡng thật.

### Leg quan trọng nhất là leg BÁC BỎ TIỀN ĐỀ
`g0` (tắt hẳn BAL mỗi khi `mom_200` đọc FLIPPED) **mất −2,97pp CAGR**, Calmar 1,62 → 1,46. Dashboard
nói momentum đã lật; **sổ BAL vẫn kiếm tiền qua đúng những cửa sổ đó.**

Cơ chế: **lệch quần thể**. `edge_health_monitor` đo IC cross-sectional trên **toàn universe thanh
khoản, mọi tháng**; BAL giao dịch một tập con **chỉ BULL/EXBULL, đã lọc tier, đã chặn momentum ở
EXBULL**. Sign flip ở quần thể thứ nhất KHÔNG kéo theo thua lỗ ở quần thể thứ hai.

> **⇒ SỬA LẠI G1.** BAL **không** thiếu vòng phản hồi thích nghi. Nó CÓ một vòng, và vòng đó chạy
> theo **TRẠNG THÁI** chứ không theo edge đã thực hiện: tier vào lệnh chỉ-BULL + EXBULL momentum
> suppression + regime-size. Việc job này xác lập là: thêm một vòng THỨ HAI khoá vào dashboard IC
> **không** phải cải tiến — đã đo, có placebo đối chứng, **NO-GO**.

## 9. quant-skeptic bác đề xuất t_eff — **REFUTED (confidence high)**, KHÔNG SỬA CODE

Đề xuất ở §7 (đổi t-stat của `edge_row()` sang n_eff) **BỊ BÁC**. Lý do quyết định: công thức
`n*(1-ac1)/(1+ac1)` là công thức **AR(1)**, áp lên chuỗi mà chính tác giả mô hình hoá là **MA(2)**
và đo bằng Newey-West lag 2 ở mọi chỗ khác. **Dưới NW/block-bootstrap, |t| của `mom_200` là ~2,5** —
tức hệ quả được quảng cáo ("nhãn FLIPPED sẽ bị chặn") là **hiện vật của công thức sai**, và nhãn
AR(1) tự lật trong chính sai số lấy mẫu của nó.

⚠️ **Đính chính điều Mike đã báo user ở lượt trước:** Mike recompute độc lập và khớp tuyệt đối —
nhưng cái khớp đó chỉ xác nhận **SỐ HỌC của công thức AR(1)**, không xác nhận **công thức đó ĐÚNG
cho chuỗi này**. Recompute đúng ≠ phương pháp đúng. **Không sửa `edge_health_monitor.py`.**

Ghi nhận: cổng `|t|≥2` trên chuỗi chồng lấn vẫn là câu hỏi mở hợp lệ, nhưng lời giải phải là
Newey-West (đã dùng ở nơi khác trong fleet), không phải n_eff kiểu AR(1).

## 10. INPUT CHO REVIEW VPI/BAL 2026-09-16 — dùng thẳng mục này

1. **Kênh "edge-health dashboard" là kênh RỖNG cho quyết định BAL.** Đã đo, có placebo đối chứng,
   NO-GO. Nếu định giảm exposure BAL, lý lẽ **phải đến từ chỗ khác** — không phải từ IC momentum.
2. **Nhãn `FLIPPED` đang treo KHÔNG mô tả hiện tại.** `mom_200` IC: 04/2026 −0,060 → 05/2026
   **+0,285** → 06/2026 **+0,382** (Mike đọc thẳng `data/edge_health_ic.csv`). Hai hệ đo độc lập
   (job B, job C) cùng kết luận momentum đã quay đầu dương trong Q2/2026.
3. **BAL yếu 2025 giống ĐÁY CHU KỲ hơn giống mục nát** (job C, quant-skeptic CONFIRMED): đáy 2020-23
   không sâu hơn đáy 2007-09, và đã hồi. Caveat bắt buộc mang theo: N chu kỳ ≈ 3, "không phát hiện
   được break" ≠ "chắc chắn không có break".
4. **Nhưng KHÔNG thể cứu BAL bằng một cổng regime/breadth** (job B): momentum chết ở MỌI ô sau 2020,
   IS 8/8 dương → OOS 8/8 ≈ 0. Vết gãy là THỜI GIAN, không phải chế độ.
5. **Điều 3 và 4 KHÔNG mâu thuẫn** — chúng đo hai thứ khác nhau: (3) đo `mom(6-1)` thô trên toàn
   universe (chu kỳ, đang hồi); (4) đo khả năng CỨU bằng cách điều kiện hoá (không cứu được). Và
   (job A) BAL thật sự giao dịch một quần thể KHÁC CẢ HAI. Đừng gộp ba con số này lại.
6. **Việc duy nhất cần user quyết ngày 09-16 vẫn là quyết định cũ**: giữ hay gỡ signal_hold VPI/BAL.
   Bốn job hôm nay **không** cung cấp lý do định lượng để cắt BAL, và cũng **không** cung cấp cơ chế
   mới để giữ. Chúng thu hẹp không gian lý lẽ, không thay người quyết.

## 11. Việc mở phát sinh (chưa làm, cần user quyết vì là scope MỚI)

- **`data/lag_edge_health.csv` khoá stats theo ngày VÀO trong khi return chỉ biết được sau 25 phiên.**
  **Live KHÔNG bị ảnh hưởng** (file chỉ chứa event đã hoàn tất; allocator ffill giá trị cũ-nhưng-thật).
  **Backtest thì có**: `pt_v23_audit_2014.py:770-790` reindex chuỗi entry-keyed qua 2014-2026 ⇒ ngày
  `d` đọc giá trị cần dữ liệu `d+25`. Độ lớn ~5 tuần. Nó nằm TRONG phần validate +0,60pp đã công bố
  của allocator edge-conditional. **Không phải lý do đổi gate live.** Việc đúng: 1 A/B một-leg
  (rebuild exit-keyed) để biết bao nhiêu trong +0,60pp còn sống. Bounded, không phải redesign.
- **`data/edge_panel.csv` và `data/bal_edge_health.csv` chưa có entry trong `kb/data_registry/`**
  (§9 coding_guidelines). Đã giao data-ops bổ sung cho `edge_panel.csv`; `bal_edge_health.csv` cố ý
  KHÔNG publish ra `data/`, chỉ là bằng chứng nghiên cứu.
