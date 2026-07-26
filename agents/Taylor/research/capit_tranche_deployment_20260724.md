# CAPIT — tranche-theo-xác-nhận vs lump+ramp: backtest event-study

> Taylor (Quant/Algo), job `Taylor_20260726_125456`, 2026-07-26. **RESEARCH-ONLY — KHÔNG wire production.**
> Câu hỏi (user, qua Mike): có nên thay cơ chế CAPIT hiện tại (chốt size 1 lần tại ngày fire rồi ramp cơ
> học 3 phiên) bằng **tranche giải ngân dần theo bằng chứng** (T1 fire ngay / T2 khi ổn định / T3 khi xác
> nhận) — lấy cảm hứng từ sleeve "mua khi sợ hãi" (`calculated_fear_state_backstop.md` §3, tranche cho từng mã).
>
> **Kết luận một câu: KHÔNG.** Tranche-theo-xác-nhận **KHÔNG cải thiện giá vốn** (thực tế còn **đắt hơn
> ~1%**), **mất ~1,1–1,7pp lợi nhuận** vì bỏ lỡ cú nảy sớm (đúng bẫy winner-cut), đổi lại chỉ **giảm
> drawdown nhẹ ~1,5pp** và lợi ích đó **tập trung vào 3 crash đa-nhịp** (COVID 2020, 2022, 2025-04), **vắng
> mặt hoàn toàn trong IS 2014-19**. Cơ chế `washout_gate` hiện tại đã fire **rất gần đáy cục bộ** rồi.

---

## 0. Bối cảnh cơ chế hiện tại (đã đọc code `pt_v23_audit_2014.py`)

- `capit_base(state, dd52w, vn_cooling)` trả 1 con số size mục tiêu DUY NHẤT lúc fire: CRISIS=1.0,
  NEUTRAL=0.75, BULL/EXBULL=0.5, BEAR=0.5 nếu dd52w>−25% hoặc vol cooling, else 0.
- Sự kiện fire = `breadth_oversold` (% `ticker_prune` có D_RSI<0.3) ≥ `WASHOUT_GATE=0.30`, gom cụm
  (gap ≥30 ngày → sự kiện mới), lấy **ngày đầu cụm** làm d0.
- Size cuối = `base × grind_half(0.5 nếu có washout 20-90 phiên trước) × maturity_mult × ew2d × postbull`
  × free-cash của book. **Toàn bộ nhập tại d0**, engine ramp cơ học 3 phiên (T+1 Open fills).
- **KHÔNG có tranche theo bằng chứng.** Các cổng maturity/ew2d/postbull đã **GIẢM SIZE** (không delay)
  cho washout nguy hiểm (fresh crisis nông, post-bull, trend chưa gãy) — đây là điểm mấu chốt ở §5.

---

## 1. BƯỚC 1 — Lịch sử các lần CAPIT fire (2014 → 2026-07-25)

19 sự kiện (replicate chính xác logic detection; `research/capit_tranche_probe/events.csv`). Cột
"further-fall" = đáy VNINDEX & rổ golden trong 40 phiên SAU fire so với giá tại d0 (đo "còn xấu thêm không").

| # | Ngày fire | State | dd52 | peak_oversold | grind | golden basket (n) | VNI further-fall | rổ further-fall | ngày tới đáy |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2014-05-08 | CRISIS | −13.2 | 0.62 | | PVS,PVD,HPG (3) | −2.5% | −0.9% | 5 |
| 2 | 2015-05-18 | NEUTRAL | −17.4 | 0.31 | | (2 — SKIP <3) | 0% | — | 0 |
| 3 | 2015-08-24 | NEUTRAL | −17.8 | 0.44 | ✓ | HPG,PVS,DPM (3) | 0% | 0% | 0 |
| 4 | 2016-01-18 | NEUTRAL | −17.6 | 0.45 | | NNC,LIX,DPM,DRC,VNM (5) | −0.9% | −1.2% | 3 |
| 5 | 2018-05-28 | CRISIS | −22.6 | 0.42 | | VSC,FMC,TCM (3) | −4.1% | −4.6% | 44 |
| 6 | 2018-07-05 | NEUTRAL | −25.3 | 0.32 | ✓ | GAS,FMC,TCM (3) | −0.7% | −0.9% | 6 |
| 7 | 2020-02-03 | NEUTRAL | −9.4 | 0.35 | | CVT,SAB,VSC,BMP,NT2 (5) | **−29.0%** | **−25.2%** | 50 |
| 8 | 2020-03-11 | BEAR | −20.8 | 0.61 | ✓ | +SCS (6) | **−18.8%** | **−17.4%** | 13 |
| 9 | 2020-07-27 | NEUTRAL | −23.4 | 0.39 | ✓ | KSB,DPG,SCS,VSC,GIL,MWG,BMP,NT2 (8) | 0% | −1.0% | 0 |
| 10 | 2022-04-19 | CRISIS | −8.0 | 0.61 | | C32,NHH,SAB,TLG,VCS (5) | **−16.7%** | **−20.4%** | 27 |
| 11 | 2022-06-15 | BEAR | −20.6 | 0.47 | ✓ | HPG,VCS,SAB,NHH (4) | −5.3% | −7.4% | 21 |
| 12 | 2022-09-28 | BEAR | −25.2 | 0.77 | ✓ | CSV,DPG,GAS,NTP,PTB,SAB,TLG (7) | **−20.3%** | **−27.5%** | 48 |
| 13 | 2023-10-30 | CRISIS | −16.3 | 0.45 | | SLS,VCS,QNS,MCH (4) | −1.4% | −4.8% | 1 |
| 14 | 2024-04-19 | BULL | −8.9 | 0.41 | | HDG,VCS,QNS,VNM,TLG,MSH (6) | 0% | −0.2% | 0 |
| 15 | 2024-08-05 | CRISIS | −8.7 | 0.36 | ✓ | RAL,SAB,TLG,VCS,VNM (5) | 0% | −1.6% | 0 |
| 16 | 2025-04-03 | BULL | −8.0 | 0.84 | | FMC,DGW,SCS,TNG,CTR (5) | **−11.0%** | **−21.6%** | 6 |
| 17 | 2025-10-20 | NEUTRAL | −7.4 | 0.33 | | DHC,DGW,GAS (3) | −3.4% | −0.6% | 21 |
| 18 | 2026-03-09 | NEUTRAL | −13.1 | 0.43 | | CTR,NCT,NTC,VCS,VGC,VNM (6) | −3.7% | −0.4% | 14 |
| 19 | **2026-07-20** | NEUTRAL | −9.6 | 0.51 | ✓ | SIP,PNJ,PVT,SAB,VNM,NCT (6) | −4.3%* | −5.7%* | 2* |

\* = sự kiện LIVE đang chạy tiền thật (chỉ ~4 phiên forward, quá sớm để kết luận; loại khỏi thống kê).

**Phát hiện Bước 1 — hầu hết fire đã sát đáy:** VNI further-fall trung vị chỉ **−3.4%**; chỉ **5/19 (26%)**
sụt sâu thêm >−10% sau fire. Đúng 5 case đó = **crash đa-nhịp**: COVID 2020-02 & 2020-03, 2022-04, 2022-09,
2025-04. **14/19 (74%) fire nằm trong vài % của đáy cục bộ** (thường 0% = ngày fire CHÍNH LÀ đáy). Đây là
lý do gốc khiến tranche thua: `washout_gate` vốn đã là bộ bắt-đáy tốt.

---

## 2. BƯỚC 2 — Thiết kế biến thể tranche-theo-xác-nhận (chỉ dùng tín hiệu ĐÃ CÓ)

Khai báo **N trials = 4** (2 tỷ lệ chia × 1 thiết kế trigger; + sensitivity 2 ngưỡng T3 & 2 MAXWAIT làm
robustness, KHÔNG phải để chọn cấu hình đẹp). Không sweep rộng rồi cherry-pick.

- **T1** = fire ngay tại d0 (như hiện tại nhưng chỉ 1 phần size). Fill T+1 Open.
- **T2 (ổn định)** = `breadth_oversold` đã tạo đỉnh rồi **hạ ≥15% khỏi đỉnh** kể từ d0 (không còn xấu thêm).
- **T3 (xác nhận)** = `breadth_oversold < 0.20` **HOẶC** DT5G state cải thiện trên state@d0.
- **Backstop**: tranche nào chưa trigger trong `MAXWAIT=40` phiên → giải ngân tại d0+40 (tránh under-invest
  vĩnh viễn làm nhiễu phép so sánh).
- 2 tỷ lệ: **T333** = 33/33/34, **T532** = 50/30/20 (lệch về T1).

Trigger fire hợp lý, không suy biến (bảng `results.csv`): T2 sau d0 trung bình 3-7 phiên, T3 muộn hơn;
COVID 2020-03 bắt được nhịp sâu (T2 03-18, T3 04-03, đáy ~03-24→03-31).

**Fills = T+1 Open (audit-faithful).** Rổ golden equal-weight, vốn cam kết = 1 đơn vị/sự kiện, phần chưa
giải ngân nằm tiền mặt (deposit ~0, thận trọng).

---

## 3. BƯỚC 3 — So sánh THẬT (17 sự kiện đủ dữ liệu forward ≥90 ngày, loại 2015-05 <3 tên & live 2026-07-20)

### Lợi nhuận (terminal, exit tại +60 phiên = CAPIT_HOLD; và +120)

| | ret+60 mean | ret+60 median | ret+120 mean | thắng lump |
|---|---|---|---|---|
| **LUMP (hiện tại)** | **+15.69%** | +15.70% | +19.88% | — |
| T333 (33/33/34) | +14.02% | +12.79% | +18.23% | 5/17 |
| T532 (50/30/20) | +14.54% | +13.51% | +18.75% | 5/17 |

**Δ tranche − lump (paired):** T333 **−1.66pp** (+60) / **−1.65pp** (+120); T532 **−1.15pp** / **−1.12pp**.
Thắng lump chỉ **5/17**. → tranche mất lợi nhuận, không phải hòa.

### Giá vốn (cost basis, so với entry lump; <1 = tranche rẻ hơn)

| | mean | median | rẻ hơn lump |
|---|---|---|---|
| T333 | **1.0145** | 1.0202 | 5/17 |
| T532 | **1.0099** | 1.0138 | 5/17 |

→ **Tranche trả giá vốn CAO HƠN ~1-1.5%**, không thấp hơn. Vì `washout_gate` đã fire gần đáy → chờ "xác
nhận ổn định" = mua lại sau khi giá đã nảy. **Đây là câu trả lời trực tiếp cho câu hỏi cốt lõi của user:
tranche KHÔNG giúp giá vốn tốt hơn — nó chỉ trì hoãn và mua đắt hơn ở đa số case.**

### Drawdown tối đa của vốn CAPIT trong lúc giải ngân (ít âm hơn = tốt)

| | mean | median |
|---|---|---|
| LUMP | −10.89% | −7.08% |
| T333 | **−9.36%** | −6.65% |
| T532 | −9.68% | −6.66% |

→ Tranche giảm DD **~1.5pp mean** (median gần như không đổi). **Đây là lợi ích DUY NHẤT**, và nó tập trung
vào 3 crash đa-nhịp: 2020-03 (LUMP −16.7%→T333 −8.1%, đồng thời ret CAO HƠN +30.3% vs +24.6%), 2025-04
(−20.7%→−9.4%, ret +22.7% vs +19.0%), 2022-04 (−20.7%→−16.8%). Ngoài 3 case này, DD gần như không cải thiện.

---

## 4. BƯỚC 4 — Walk-forward IS/OOS + LOO + sensitivity

| | IS 2014-19 (n=5) | OOS 2020+ (n=12) |
|---|---|---|
| T333−LUMP ret60 | **−5.80%** (thắng 0/5) | +0.06% (thắng 5/12) |
| T532−LUMP ret60 | −4.25% (thắng 0/5) | +0.15% (thắng 5/12) |
| T333−LUMP maxdd | +0.13% (tốt hơn 3/5) | **+2.11%** (tốt hơn 9/12) |

- **Lợi nhuận: IS âm nặng (−4→−6pp, thắng 0/5), OOS hòa (~0).** Tranche KHÔNG BAO GIỜ thắng lump về
  lợi nhuận in-sample. OOS chỉ hòa.
- **DD cushion CHỈ có ở OOS 2020+ (+2.1pp)**, IS gần như bằng 0. → lợi ích DD **tập trung vào regime
  crash-nhịp-mạnh 2020-2022** — đúng cờ đỏ robustness đã gặp ở MOM_N/MOM_S (edge dồn regime 2020-21).
- **LOO** (bỏ từng sự kiện, tính lại mean T333−LUMP ret60): dao động **−1.13% → −2.12%**, **KHÔNG BAO GIỜ
  lật dương**. Penalty lợi nhuận không do 1 sự kiện lẻ — nó phổ biến.
- **Sensitivity**: đổi T3_THR ∈ {0.15, 0.20, 0.25} và MAXWAIT ∈ {30, 40, 60} → Δ ret60 ổn định ở
  −1.6% (T333)/−1.1% (T532), **không đảo chiều**. Kết luận không phải hiện vật của 1 lựa chọn ngưỡng.

**N nhỏ (17 sự kiện phân tích được, IS chỉ 5)** — nêu rõ theo kỷ luật. Nhưng kết luận vững CHÍNH VÌ tranche
thất bại trên **chính lý do tồn tại của nó** (giá vốn): đây không phải một quyết định thống kê sát biên.

---

## 5. Kết luận & khuyến nghị

**KHÔNG áp dụng tranche-theo-xác-nhận cho CAPIT.** Ba lý do:
1. **Không cải thiện giá vốn** (còn đắt hơn ~1%) — `washout_gate` đã bắt đáy tốt (74% fire sát đáy cục bộ).
2. **Mất ~1.1-1.7pp lợi nhuận** (bẫy winner-cut/miss-recovery), robust qua LOO + sensitivity, âm nặng IS.
3. Lợi ích duy nhất (DD −1.5pp) **regime-concentrated** (chỉ crash đa-nhịp 2020-2022), vắng mặt IS →
   không đáng tin để tune vào.

**Quan trọng — công cụ đúng cho rủi ro "washout còn xấu thêm" ĐÃ CÓ SẴN và TỐT HƠN tranche:** hệ thống
hiện dùng **giảm size** (maturity_mult trong CRISIS, grind-half, ew2d-shrink, postbull) cho đúng các
washout nguy hiểm (fresh crisis nông, hậu-bull, trend chưa gãy). Giảm size **de-risk mà KHÔNG delay** →
không hy sinh cú nảy sớm, khác hẳn tranche (delay + mua đắt). Nếu user muốn thêm đệm downside cho crash
sâu, đòn bẩy đúng là **siết `CAPIT_EVENT_CAP` / mở rộng maturity-shrink**, KHÔNG phải tranche trì hoãn.

**Vì sao sleeve "mua khi sợ hãi" (§3) tranche được mà CAPIT không:** sleeve đó là **1 mã đơn lẻ, đặc tình
huống, tail-risk đình chỉ giao dịch thật** (TV1/DGC) — tranche ở đó để quản trị rủi ro *idiosyncratic
nhị phân* (audit từ chối, huỷ niêm yết), không phải để bắt giá vốn tốt hơn. CAPIT là **rổ ≥3-15 mã chất
lượng, market-level, đã diversify** — bài toán khác, và bằng chứng cho thấy timing lump thắng.

**Không wire** (dispatch chốt: không wire dù kết quả gì). Kết quả TIÊU CỰC → không kích hoạt quant-skeptic
(chỉ bắt buộc trước khi bàn wire nếu kết quả tích cực). Nếu sau này muốn theo đuổi biến thể "chỉ tranche
khi dd52 nông + CRISIS mới" (first-leg), cần re-design + skeptic — nhưng maturity-shrink hiện tại đã phủ
khoảng đó.

## 6. Tái lập
- `research/capit_tranche_probe/pull_data.py` — pull breadth/VNI/state/baskets/prices từ BQ → CSV cache.
- `research/capit_tranche_probe/analyze.py` — event-study (env: `MAXWAIT`, `T3_THR`).
- Interpreter: `/home/trido/thanhdt/wc_venv/bin/python`. Dữ liệu: `tav2_bq.ticker_prune/ticker` +
  `vnindex_5state_dt5g_live`. Fills T+1 Open. Không ghi vào file canonical nào (§8).
