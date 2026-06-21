# Feedback — Bull market psychology overrides caution signals (VALIDATED 2026-05-21)

## ✅ STATUS: Empirically confirmed & deployed in v3.4b "Định Tâm"

User's insight was validated with hard numbers via diagnostic
(`diagnose_bull_regime_v2.py`) and V11 12y backtest:

- 150 US override fires post-2014; 43 trong BTC_R6M bull regime
- **IN-bull T+60 mean = +17.45%, 100% positive** → filter 100% wrong khi bull
- OUT-bull T+60 = +2.29%, 71% positive → mixed (filter mostly right)
- v3.4b bypasses US override trong bull → **+3.56pp FULL CAGR / +7.60pp OOS** vs v3.1
- Walk-forward validated 14 variants — plateau 6M T=5-20%, không overfit

**Refinement to original insight**: chỉ US override (predictive filter) nên tắt;
conc filter có vai trò leverage management (structural), tắt thì 2021 mất 12pp
(test v3.5 reject). Lesson: phân biệt predictive vs structural filters.

## Insight (user-stated, original)

Khi thị trường vào BULL state trong thời gian không quá ngắn (vài tháng+), mọi người đều thắng, **tâm lý lạc quan thái quá** đè bẹp các yếu tố thận trọng:

- **Concentration không còn quá quan trọng**: dù narrow/VIC-led, retail vẫn FOMO vào cổ phiếu nóng → broad market tiếp tục lên
- **US crisis cũng không ảnh hưởng**: dù SPX_DD_1Y hay VIX báo nguy, người vẫn kiếm tiền VN → vẫn tham → không sell
- **Yếu tố thận trọng (caution gate, override) không còn predictive** trong giai đoạn này

## Implication cho state-system design

Các filter "conservative" như:
- `concentration_smooth ≤ 0.55` (v3.3b)
- `US shock override` (v3.1)
- `r_dual < 0.60` (v3.2 waypoint)

Đều giả định **fundamentals quan trọng**. Trong **sustained bull psychology**, fundamentals tạm thời bị disable bởi flow.

## Evidence từ historical fires (v3.3b context)

- **2021 super-bull** (post-COVID): 5 fires gồm 2021-03-30 conc=0.51, 2021-04-20 conc=0.47, 2021-05-20 conc=0.61, 2021-06-11 conc=0.65, 2021-04-20 EX-BULL→BULL conc=0.47. Hầu hết HELP (gate giữ BULL/EX-BULL) → portfolio +83-89% năm 2021.
- **2025-Q1 bull**: gate fire 2025-03-12 (conc 0.29, RSI 82, r_dual 0.85) — ALL signals nói "tốp lành mạnh", nhưng vẫn HURT T+20 -12.4%. Bull psychology peak → market roll over despite all positives.
- **Sustained bull (2020-09 → 2022-01, ~16 tháng BULL/EX-BULL)**: US crisis 2020-Q1 đã hết tác dụng (VN không quan tâm Mỹ sau khi đã thắng). US-override fires giảm hiệu lực rõ rệt trong giai đoạn này.

## Future v3.4+ research direction

Add **"bull-fatigue counter"**:
```
if state in {BULL, EX-BULL} continuously for > N_DAYS sessions:
    # disable conservative filters
    use raw state signal (no conc filter, no US-override)
    only re-enable filters when state drops to NEUTRAL or below
```

Candidate N_DAYS: 60-120 sessions (3-6 months sustained bull). Cần backtest từng giá trị.

**Mechanism**: trong sustained bull, momentum self-reinforcing > fundamentals. Filtering bằng fundamentals = chasing wrong signal. Khi bull break (→NEUTRAL), psychology shift → fundamentals lại quan trọng → re-enable.

## Caveat cho deployment v3.3b

v3.3b chưa implement bull-fatigue counter. Trong sustained bull (vd 2026 nếu thị trường hồi mạnh), conc filter có thể block các gates đáng giá. **Shadow track 2 tuần** sẽ chỉ catch short-term issues, không phát hiện sustained-bull psychology.

→ Monitor explicit: nếu sau 60 phiên BULL liên tục, conc filter bắt đầu hurt → cân nhắc disable hoặc add fatigue counter.

## Related insights

- Connect to **`feedback_us_vn_correlation_interpretation.md`** — tail dependence chỉ matter ở crisis tail, full-sample Pearson misleading. Bull psychology cũng decouple US-VN linkage tạm thời.
- Connect to **`ba_v11_production_proposal.md`** P3 overheat guard — VNI/MA200 > 1.30 + RSI > 0.75 → AVOID. P3 đã có sẵn cho buy-side; gate logic chưa có equivalent cho state-side.
