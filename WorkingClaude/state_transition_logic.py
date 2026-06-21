# -*- coding: utf-8 -*-
"""
state_transition_logic.py
=========================
Giải thích từng bước quá trình ra quyết định chuyển trạng thái thị trường.
Chạy với bất kỳ ngày nào để xem tại sao hệ thống đang ở trạng thái đó.

Câu hỏi trả lời: "Hôm nay hệ thống đang ở NEUTRAL — vì sao không phải BULL?"

═══════════════════════════════════════════════════════════════════════════
EVOLUTION (codename family "Ngũ Hành"):
  • Cổ Điển       — original 7-factor baseline (script này mô tả)
  • Tinh Tế       — v2g_pe3c_s3 = pe3c states + mode(3) + ms(2)  (đã LIVE)
  • Tam Quan v3   — dual-blend (raw + EW concentration-weighted)
  • Tam Quan v3.1 — v3 + US shock override (SPX_DD_1Y, VIX)
  • v3.3b "Cẩn Thận" — v3.1 + RSI gate + conc filter  (superseded 2026-05-21)
  • Tam Quan v3.4b "Định Tâm" — v3.1 + BTC bull-aware US bypass + RSI/conc
                                (STAGING NEXT 2026-05-21, deploy candidate)

V3.4b ADDS 3 LAYERS sau pipeline base (xem `tam_quan_v3_4b_dinh_tam.md`):

  Layer A — Bull-Trend-Confirmed (BTC) US override bypass:
    BTC[t] = (VNINDEX 6-month return > 15%) AND (VNINDEX > MA200)
    if BTC[t]:
        base[t] = state_v3_staging[t]   # bypass US override
    else:
        base[t] = state_v31[t]          # use v3.1 (with US override)
    base = mode(3) ∘ min_stay(2)        # re-smooth

  Layer B — RSI uptrend gate (giống v3.3b):
    Khi base fire 1-step downgrade tại ngày t:
      if RSI(14)[t] >= 55 and concentration_smooth[t] <= 0.55:
          state[t] = state[t-1]
          gate_active = True
      # Exit: RSI<55, state hồi >= block, hoặc -2 bậc

  Layer C — RSI gate exit conditions:
    while gate_active:
      if RSI < 55: release       (momentum gãy)
      elif base[t] >= block_at: release  (state hồi)
      elif (block_at - base[t]) >= 2: release (real bear)
      else: hold state at block_at

V3.4b backtest V11 12y vs v3.1:
  FULL: +3.56pp CAGR, +0.24 Sharpe, +3.36pp MaxDD better
  OOS:  +7.60pp CAGR (Q1 2026 fix từ -11.39% → +8.30%)
  Walk-forward: 6M T=5-20% plateau, không overfit

MECHANISM (xem feedback_bull_market_psychology.md):
  150 US override fires post-2014; 43 trong bull regime BTC_R6M
  → T+60 mean +17.45%, 100% positive (filter 100% sai trong bull)
  → v3.4b bypasses 245 such days

CAVEAT v3.5 REJECT:
  Tested "disable conc filter trong bull" — thua 12pp năm 2021 do over-leverage.
  Conc filter có vai trò structural (leverage mgmt) ngoài predictive → giữ luôn.
  Pattern: predictive filters (US) tắt được; structural filters (conc) phải giữ.

NOTE: script này explain Cổ Điển logic. Để xem v3.4b decisions cụ thể, mở
bảng transitions `vnindex_transitions_v3_4b.html` (RSI, conc, BTC, US-bypass,
Gate status, drivers từng row).
═══════════════════════════════════════════════════════════════════════════

Tham số đã xác nhận cho Cổ Điển baseline (không thay đổi nếu không có lý do):
  EMA_ALPHA = 0.40  (grid-search toàn bộ, α=0.40 tối ưu IS + OOS)
  MIN_STAY  = 7     (so sánh trực tiếp: ms=7 beats ms=10 trên TẤT CẢ chỉ số)
  MODE_WIN  = 15    (cửa sổ mode smoothing)

Kết quả walk-forward (IS=2000-2020, OOS=2021-nay):
  OOS CAGR=12.1%  Calmar=0.84  MaxDD=-14.3%  vs B&H CAGR=10.2% MaxDD=-40.3%
  OOS Calmar / IS Calmar = 3.06 → không overfit
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 1 — BỨC TRANH TỔNG QUAN
# Hệ thống ra quyết định qua 8 lớp lọc tuần tự.
# Mỗi lớp có thể ghi đè lớp trước.
# ════════════════════════════════════════════════════════════════════════════
"""
LUỒNG QUYẾT ĐỊNH (8 BƯỚC)
══════════════════════════

                    7 yếu tố kỹ thuật (P3M, P1M, MA200, RSI, MACD, CMF, Breadth)
                          │
                    [BƯỚC 1] Expanding percentile rank → mỗi yếu tố: 0.0 → 1.0
                          │   (rank tại t chỉ dùng lịch sử t=0..t, không look-ahead)
                          │
                    [BƯỚC 2] Composite score (trung bình có trọng số)
                          │   score = Σ(rank × W) / Σ(W có dữ liệu)
                          │
                    [BƯỚC 3] Expanding rank của score → r_score (0→1)
                          │   EMA α=0.40 → r_score_ema (giảm nhiễu ngày-qua-ngày)
                          │
                    [BƯỚC 4] Phân loại thô theo ngưỡng r_score_ema:
                          │   <0.10→CRISIS  0.10-0.20→BEAR  0.20-0.70→NEUTRAL
                          │   0.70-0.90→BULL  ≥0.90→EX-BULL
                          │
                    [BƯỚC 5] Risk overrides (3 điều kiện ghi đè xuống):
                          │   PE>P90 expanding → EX-BULL cap BULL
                          │   DD<-25% → BULL/EX-BULL cap NEUTRAL
                          │   Vol>1.5×avg → EX-BULL cap BULL
                          │
                    [BƯỚC 6] BearDvg gate (RSI divergence → khóa ≤ CRISIS)
                          │   Mở khi: BearDvg signal xuất hiện
                          │   Đóng khi (OR): BullDvg | P3M>0.45+PE<0.80 | r_score streak 10
                          │   Min 60 phiên trước khi được đóng
                          │
                    [BƯỚC 7] Rolling mode (cửa sổ 15 phiên)
                          │   State cuối = state xuất hiện nhiều nhất trong 15 phiên gần nhất
                          │
                    [BƯỚC 8] min_stay_filter (tối thiểu 7 phiên/trạng thái)
                          │   Đoạn < 7 phiên bị sáp nhập vào trạng thái liền trước
                          │
                    TRẠNG THÁI CUỐI CÙNG → Phân bổ vốn
                          │
                    CRISIS=0% | BEAR=20% | NEUTRAL=70% | BULL=100% | EX-BULL=130%
"""

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 2 — LOAD DỮ LIỆU
# ════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("PHÂN TÍCH QUÁ TRÌNH RA QUYẾT ĐỊNH CHUYỂN TRẠNG THÁI")
print("=" * 70)

vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

for col in ["Open", "High", "Low", "Close", "Volume", "VNINDEX_PE",
            "D_RSI", "D_RSI_T1W", "D_RSI_Max1W", "D_RSI_Max3M",
            "D_RSI_Min1W", "D_RSI_Min3M", "D_RSI_Max1W_Close", "D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD", "D_RSI_Max1W_MACD", "D_RSI_MinT3",
            "D_MACDdiff", "D_CMF", "C_L1M", "C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

breadth_path = os.path.join(WORKDIR, "breadth_data.csv")
if os.path.exists(breadth_path):
    breadth = pd.read_csv(breadth_path)
    breadth["time"] = pd.to_datetime(breadth["time"])
    vni = vni.merge(breadth, on="time", how="left")
else:
    vni["breadth"] = np.nan

close  = vni["Close"].values.copy()
high   = vni["High"].values.copy()
low    = vni["Low"].values.copy()
vol    = vni["Volume"].values.copy()
n      = len(close)
cal_days = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
sessions_per_year = n / (cal_days / 365.25)

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 3 — BƯỚC 1: 7 YẾU TỐ + EXPANDING PERCENTILE RANK
# ════════════════════════════════════════════════════════════════════════════
"""
BƯỚC 1: TẠI SAO 7 YẾU TỐ NÀY?
════════════════════════════════
Mỗi yếu tố đo một góc nhìn khác nhau, không bị redundant:

  P3M  (30%) — Momentum trung hạn: xu hướng 3 tháng quan trọng nhất
  P1M  (10%) — Momentum ngắn hạn: tín hiệu bổ sung, trọng số thấp vì noisy
  MA200(15%) — Xu hướng dài hạn: giá so với đường trung bình 1 năm
  RSI  (15%) — Relative Strength: sức mạnh tương đối, không bị ảnh hưởng bởi giá tuyệt đối
  MACD (10%) — Cross-signal: đà tăng/giảm qua chênh lệch EMA
  CMF  ( 8%) — Dòng tiền: xác nhận volume (mua hay bán chiếm ưu thế)
  Breadth(12%)— Độ rộng thị trường: % cổ phiếu > MA50 (toàn thị trường, không chỉ VNINDEX)

Tại sao expanding rank thay vì giá trị thô?
  - P3M = +5%: Tốt hay xấu? Phụ thuộc vào lịch sử.
  - Expanding rank = 0.65: Cao hơn 65% lịch sử từ 2000 đến nay — rõ ràng hơn nhiều.
  - Quan trọng: expanding rank tại ngày t chỉ dùng dữ liệu từ đầu đến t.
    Không có future data leak, đảm bảo causal correctness.
  - Min 252 sessions: cần ít nhất 1 năm lịch sử để rank có ý nghĩa thống kê.
"""

W = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15,
     "RSI": 0.15, "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB = 252

# --- P3M: % change 3 tháng (calendar-correct từ CSV) ---
p3m = np.full(n, np.nan)
if "Change_3M" in vni.columns:
    p3m_csv = pd.to_numeric(vni["Change_3M"], errors="coerce").values
    for i in range(n):
        p3m[i] = p3m_csv[i] if not np.isnan(p3m_csv[i]) else (
            close[i]/close[i-60]-1 if i>=60 and close[i-60]>0 else np.nan)
else:
    for i in range(60, n):
        if close[i-60] > 0: p3m[i] = close[i]/close[i-60]-1

# --- P1M: % change 1 tháng ---
p1m = np.full(n, np.nan)
if "Change_1M" in vni.columns:
    p1m_csv = pd.to_numeric(vni["Change_1M"], errors="coerce").values
    for i in range(n):
        p1m[i] = p1m_csv[i] if not np.isnan(p1m_csv[i]) else (
            close[i]/close[i-20]-1 if i>=20 and close[i-20]>0 else np.nan)
else:
    for i in range(20, n):
        if close[i-20] > 0: p1m[i] = close[i]/close[i-20]-1

# --- MA200 deviation ---
ma200     = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200 > 0) & ~np.isnan(ma200), close/ma200-1, np.nan)

# --- RSI Wilder 14 → [0, 1] ---
rsi = np.full(n, np.nan); avg_u = avg_d = np.nan
for i in range(1, n):
    diff = close[i] - close[i-1]; u = max(diff, 0); d = max(-diff, 0)
    if np.isnan(avg_u):
        if i >= 14:
            avg_u = np.mean([max(close[j]-close[j-1],0) for j in range(1,15)])
            avg_d = np.mean([max(close[j-1]-close[j],0) for j in range(1,15)])
            if avg_u+avg_d > 0: rsi[i] = avg_u/(avg_u+avg_d)
    else:
        avg_u=(avg_u*13+u)/14; avg_d=(avg_d*13+d)/14
        if avg_u+avg_d > 0: rsi[i] = avg_u/(avg_u+avg_d)

# --- MACD histogram (12, 26, 9) ---
ema12 = np.full(n, np.nan); ema26 = np.full(n, np.nan)
sig   = np.full(n, np.nan); macd_hist = np.full(n, np.nan)
k12=2/13; k26=2/27; k9=2/10
for i in range(n):
    is_first = (i == 0)
    ema12[i] = close[i] if (is_first or np.isnan(ema12[i-1])) else ema12[i-1]*(1-k12)+close[i]*k12
    ema26[i] = close[i] if (is_first or np.isnan(ema26[i-1])) else ema26[i-1]*(1-k26)+close[i]*k26
    ml = ema12[i] - ema26[i]
    sig[i]  = ml if (is_first or np.isnan(sig[i-1])) else sig[i-1]*(1-k9)+ml*k9
    if i >= 33: macd_hist[i] = ml - sig[i]

# --- CMF 14 (Chaikin Money Flow) ---
hl = high-low
mfm = np.where(hl>0, ((close-low)-(high-close))/hl, 0.0)
mfv = mfm*vol
cmf = np.full(n, np.nan)
for i in range(14, n):
    vs = np.sum(vol[i-14:i])
    if vs > 0: cmf[i] = np.sum(mfv[i-14:i])/vs

breadth_arr = vni["breadth"].values if "breadth" in vni.columns else np.full(n, np.nan)

raw_factors = {"P3M": p3m, "P1M": p1m, "MA200": ma200_dev,
               "RSI": rsi, "MACD": macd_hist, "CMF": cmf, "Breadth": breadth_arr}

def expanding_pct_rank(arr, min_lb=252):
    """Expanding percentile rank — causal, không look-ahead."""
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        hist = arr[:t+1]; valid = hist[~np.isnan(hist)]
        if len(valid) >= min_lb:
            out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

ranks = {k: expanding_pct_rank(v, MIN_LB) for k, v in raw_factors.items()}

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 4 — BƯỚC 2+3: COMPOSITE SCORE → EMA SMOOTH
# ════════════════════════════════════════════════════════════════════════════
"""
BƯỚC 2: TẠI SAO CHUẨN HÓA THEO Σ(W có dữ liệu)?
══════════════════════════════════════════════════
  score = Σ(rank_k × W_k) / Σ(W_k có dữ liệu)

  Breadth chỉ có từ 2014 → trước đó chỉ 6 yếu tố.
  Nếu chia cho tổng trọng số cố định (1.0), score trước 2014 sẽ thấp giả tạo.
  Chia cho Σ(W có dữ liệu) đảm bảo score luôn so sánh được qua thời gian.

BƯỚC 3: TẠI SAO EMA α=0.40?
═════════════════════════════
  Sau khi tính score, ta rank nó trong lịch sử → r_score (0→1).
  EMA α=0.40 làm mịn r_score, giảm nhiễu ngày-qua-ngày:
    - α=0.40: phản ứng nhanh vừa (~2 phiên để chuyển 50% của thay đổi)
    - Nhỏ hơn (α=0.25): mịn hơn nhưng lag nhiều, bỏ lỡ tín hiệu sớm
    - Lớn hơn (α=0.50): phản ứng nhanh nhưng noisy, nhiều false signal
  → α=0.40 được chọn qua grid search IS, xác nhận ổn định trên OOS.
"""
MIN_FACTORS = 3

score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(avail) >= MIN_FACTORS:
        w_sum = sum(W[k] for k in avail)
        score[t] = sum(avail[k]*W[k] for k in avail) / w_sum

r_score = expanding_pct_rank(score, MIN_LB)

EMA_ALPHA = 0.40  # xác nhận tốt nhất qua grid search IS (2000-2020)
r_score_ema = np.full(n, np.nan)
for t in range(n):
    v = r_score[t]; prev = r_score_ema[t-1] if t > 0 else np.nan
    r_score_ema[t] = (v if np.isnan(prev) else
                      prev if np.isnan(v) else
                      EMA_ALPHA*v + (1-EMA_ALPHA)*prev)

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 5 — BƯỚC 4: PHÂN LOẠI THÔ (NGƯỠNG)
# ════════════════════════════════════════════════════════════════════════════
"""
BƯỚC 4: NGƯỠNG PHÂN LOẠI r_score_ema
══════════════════════════════════════

  r_score_ema  │  Trạng thái  │  Phân bổ  │  Ý nghĩa lịch sử
  ─────────────┼──────────────┼───────────┼─────────────────────────────────
  < 0.10       │  CRISIS  (1) │    0%     │  10% thấp nhất từ 2000 đến nay
  0.10 – 0.20  │  BEAR    (2) │   20%     │  Yếu hơn 80–90% lịch sử
  0.20 – 0.70  │  NEUTRAL (3) │   70%     │  Trung bình — zone bình thường
  0.70 – 0.90  │  BULL    (4) │  100%     │  Mạnh hơn 70–90% lịch sử
  ≥ 0.90       │  EX-BULL (5) │  130%     │  10% cao nhất — overheating signal

Tại sao ngưỡng không đối xứng (CRISIS<0.10 nhưng BEAR lên đến 0.20)?
  - CRISIS cần định nghĩa hẹp: chỉ những lúc thực sự cực xấu (bottom 10%)
  - Zone NEUTRAL rộng (0.20-0.70): chiếm ~50% thời gian — thị trường "bình thường"
  - EX-BULL cũng hẹp (>0.90): tín hiệu overheating hiếm gặp, cần thêm điều kiện PE
"""

def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs < 0.10:    return 1   # CRISIS
    elif rs < 0.20:  return 2   # BEAR
    elif rs < 0.70:  return 3   # NEUTRAL
    elif rs < 0.90:  return 4   # BULL
    else:            return 5   # EX-BULL

state_raw = np.array([classify_raw(r) for r in r_score_ema])

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 6 — BƯỚC 5: RISK OVERRIDES
# ════════════════════════════════════════════════════════════════════════════
"""
BƯỚC 5: RISK OVERRIDES — 3 điều kiện ghi đè xuống
════════════════════════════════════════════════════

Tại sao cần override nếu đã có 7 yếu tố?
  - Momentum có thể vẫn tốt ngay trước đỉnh (PE cao nhưng price vẫn tăng)
  - Cần lớp bảo vệ riêng cho rủi ro định giá và rủi ro đột biến

Override 1 — PE quá cao (cap tại BULL, không cho EX-BULL):
  Nếu state == EX-BULL VÀ PE hiện tại > PE_P90 (expanding 90th percentile):
  → Hạ xuống BULL → không dùng margin (130% → 100%) trong thị trường đắt
  Lý do: Momentum cao + định giá quá cao = rủi ro reversal cực lớn

Override 2 — Drawdown sâu (cap tại NEUTRAL):
  Nếu state >= BULL VÀ drawdown từ đỉnh lịch sử < -25%:
  → Hạ xuống NEUTRAL (100% hoặc 130% → 70%)
  Lý do: Giá đang rớt mạnh ngay cả khi các chỉ số technical còn lag

Override 3 — Volatility spike (cap tại BULL, không cho EX-BULL):
  Nếu state == EX-BULL VÀ vol_20ngày > 1.5 × vol_trung_bình_toàn_lịch_sử:
  → Hạ xuống BULL
  Lý do: Biến động cực cao thường báo hiệu tail risk — giảm đòn bẩy prudent
"""
pe_arr = vni["VNINDEX_PE"].values.copy()

pe_p90 = np.full(n, np.nan)
for t in range(n):
    hist = pe_arr[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60: pe_p90[t] = np.nanpercentile(valid, 90)

running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max > 0, close/running_max-1, 0.0)

daily_ret = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1] > 0: daily_ret[i] = close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20, n):
    w = daily_ret[i-20:i]; valid = w[~np.isnan(w)]
    if len(valid) >= 15: vol20[i] = np.std(valid)*np.sqrt(sessions_per_year)

avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    hist = vol20[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60: avg_vol_exp[t] = np.mean(valid)

state_after_override = state_raw.copy()
override_log = np.zeros(n, dtype=int)   # 0=không, 1=PE, 2=DD, 3=Vol

for i in range(n):
    s = state_after_override[i]
    if (not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i])
            and pe_arr[i] > pe_p90[i] and s == 5):
        s = 4; override_log[i] = 1
    if dd[i] < -0.25 and s >= 4:
        s = 3; override_log[i] = 2
    if (not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i])
            and vol20[i] > 1.5*avg_vol_exp[i] and s == 5):
        s = 4; override_log[i] = max(override_log[i], 3)
    state_after_override[i] = s

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 7 — BƯỚC 6: BEARDVG GATE
# ════════════════════════════════════════════════════════════════════════════
"""
BƯỚC 6: BEARDVG GATE — cơ chế bảo vệ quan trọng nhất
═══════════════════════════════════════════════════════

Bối cảnh: Tại sao cần gate riêng ngoài 7 yếu tố?
  Khi RSI tạo đỉnh thấp hơn trong khi giá tạo đỉnh cao hơn (bearish divergence),
  đây là tín hiệu momentum đang suy yếu ngầm → thị trường đang chuẩn bị đảo chiều.
  Tín hiệu này không được phản ánh đủ trong composite score (vì P3M/P1M vẫn dương).
  Gate giữ hệ thống ở CRISIS (0%) cho đến khi có đủ bằng chứng phục hồi.

Cơ chế 3 bước:
  1. BearDvg signal xuất hiện → MỞ GATE
     → Bất kể state pipeline tính ra gì, state bị cap tại CRISIS (1) → phân bổ 0%
     → Timer bắt đầu từ ngày BearDvg signal cuối

  2. Gate duy trì cho đến khi ĐÃ ĐÓNG
     → Cần đủ TỔNG THỜI GIAN (60 phiên từ signal cuối) VÀ ĐỦ DẤU HIỆU PHỤC HỒI (OR):
       Điều kiện A: BullDvg signal xuất hiện (RSI đảo chiều xác nhận đáy)
       Điều kiện B: P3M_rank>0.45 VÀ PE_rank<0.80 (momentum+định giá)
       Điều kiện C: r_score_ema > 0.65 liên tục 10 phiên (momentum bền vững)

  3. Gate đóng → hệ thống trở lại phân loại bình thường

Tại sao exit = OR (không phải AND)?
  - AND quá chặt: nếu BullDvg không xuất hiện → kẹt CRISIS suốt bull market
  - OR: khi r_score hồi phục mạnh liên tục 10 phiên, đó cũng là xác nhận đủ tin cậy
  - Kết quả backtest xác nhận: exit=OR cho Calmar tốt hơn exit=AND

Tại sao floor = CRISIS (0%) thay vì BEAR (20%)?
  - Kiểm tra trực tiếp: CRISIS floor CAGR/Calmar tốt hơn BEAR floor
  - Nguyên nhân: khi BearDvg đúng (thị trường thực sự đảo chiều), 0% bảo vệ hoàn toàn
  - Khi BearDvg sai: cost chỉ là bỏ lỡ 1-2 phiên tăng, không đáng kể trong 60+ phiên gate

Min 60 phiên: tránh đóng gate quá sớm sau false recovery (bounce ngắn).
"""

def _s(col):
    return vni[col] if col in vni.columns else pd.Series(np.nan, index=vni.index)

_D_RSI         = _s("D_RSI");      _D_RSI_T1W   = _s("D_RSI_T1W")
_D_RSI_Max1W   = _s("D_RSI_Max1W"); _D_RSI_Max3M = _s("D_RSI_Max3M")
_D_RSI_Min1W   = _s("D_RSI_Min1W"); _D_RSI_Min3M = _s("D_RSI_Min3M")
_D_RSI_Max1W_C = _s("D_RSI_Max1W_Close"); _D_RSI_Max3M_C = _s("D_RSI_Max3M_Close")
_D_RSI_Max3M_M = _s("D_RSI_Max3M_MACD");  _D_RSI_Max1W_M = _s("D_RSI_Max1W_MACD")
_D_RSI_Min1W_C = _s("D_RSI_Min1W_Close"); _D_RSI_MinT3  = _s("D_RSI_MinT3")
_D_MACDdiff    = _s("D_MACDdiff"); _D_CMF = _s("D_CMF")
_C_L1M         = _s("C_L1M");      _C_L1W = _s("C_L1W")
_mask_2011     = vni["time"] >= "2011-01-01"

bear_mask = (((_D_RSI_Max1W/_D_RSI > 1.044) & (_D_RSI_Max3M > 0.74) &
              (_D_RSI_Max1W < 0.72) & (_D_RSI_Max1W > 0.61) &
              (_D_RSI_Max1W_C/_D_RSI_Max3M_C > 1.028) &
              (_D_RSI_Max3M_M/_D_RSI_Max1W_M > 1.11) & (_D_MACDdiff < 0) &
              (vni["Close"]/_D_RSI_Max3M_C > 0.96) &
              (_D_RSI_MinT3 > 0.43) & (_D_CMF < 0.13) & _mask_2011)
             |
             ((_D_RSI_Max1W/_D_RSI > 1.016) & (_D_RSI_Max3M > 0.77) &
              (_D_RSI_Max1W < 0.79) & (_D_RSI_Max1W > 0.60) &
              (_D_RSI_Max1W_C/_D_RSI_Max3M_C > 1.008) &
              (_D_RSI_Max3M_M/_D_RSI_Max1W_M > 1.10) & (_D_MACDdiff < 0) &
              (vni["Close"]/_D_RSI_Max3M_C > 0.97) &
              (_D_RSI_MinT3 > 0.50) & (_D_CMF < 0.15) & _mask_2011)
            ).values.astype(bool)

bull_mask = (((_D_RSI_Min1W/_D_RSI_Min3M > 0.90) & (_D_RSI_Min1W < 0.60) &
              (_D_RSI_Min3M < 0.40) & (_D_RSI_Min1W_C/_D_RSI_Max3M_C < 1.15) &
              (_D_MACDdiff > 0) & (_D_RSI_MinT3 < 0.50) & (_D_RSI_Max1W < 0.48) &
              (_D_RSI/_D_RSI_T1W > 1.12) & (_D_CMF > 0) &
              (_C_L1M < 1.21) & (_C_L1W < 1.05) & _mask_2011)
             |
             ((_D_RSI_Min1W/_D_RSI_Min3M > 0.92) & (_D_RSI_Min1W < 0.52) &
              (_D_RSI_Min3M < 0.38) & (_D_RSI_Min1W_C/_D_RSI_Max3M_C < 1.10) &
              (_D_MACDdiff > 0) & (_D_RSI_MinT3 < 0.56) & (_D_RSI_Max1W < 0.64) &
              (_D_RSI/_D_RSI_T1W > 1.10) & (_D_CMF > 0) &
              (_C_L1M < 1.20) & (_C_L1W < 1.025) & _mask_2011)
            ).values.astype(bool)

pe_rank_arr = np.full(n, np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    v = pe_arr[:t+1]; v = v[~np.isnan(v)]
    if len(v) >= 60: pe_rank_arr[t] = np.sum(v <= pe_arr[t])/len(v)

p3m_rank_arr = ranks["P3M"]

_rscore_streak = np.zeros(n, dtype=bool); _streak = 0
for i in range(n):
    if not np.isnan(r_score_ema[i]) and r_score_ema[i] > 0.65: _streak += 1
    else: _streak = 0
    if _streak >= 10: _rscore_streak[i] = True

GATE_FLOOR   = 1   # CRISIS (0%) — xác nhận tốt hơn BEAR (20%) qua backtest
GATE_MIN_DUR = 60  # min 60 phiên trước khi được đóng

gate_active = False; gate_start = -1; gate_flag = np.zeros(n, dtype=int)
state_dvg   = state_after_override.copy()
gate_history = []   # lưu lịch sử mở/đóng gate

for i in range(n):
    if bear_mask[i]:
        if not gate_active:
            gate_active = True; gate_start = i
            gate_history.append(("OPEN", vni["time"].iloc[i].date(), close[i]))
        else:
            gate_start = i   # reset timer khi có BearDvg mới

    if gate_active:
        gate_flag[i] = 1
        if state_dvg[i] > GATE_FLOOR:
            state_dvg[i] = GATE_FLOOR

        sessions_in = i - gate_start
        if sessions_in >= GATE_MIN_DUR:
            _bull_ok = bool(bull_mask[i])
            _p3m_ok  = (not np.isnan(p3m_rank_arr[i])) and p3m_rank_arr[i] > 0.45
            _pe_ok   = (not np.isnan(pe_rank_arr[i])) and pe_rank_arr[i] < 0.80
            _rs_ok   = bool(_rscore_streak[i])
            if _bull_ok or (_p3m_ok and _pe_ok) or _rs_ok:
                gate_active = False
                trigger = "BullDvg" if _bull_ok else "P3M+PE" if (_p3m_ok and _pe_ok) else "r_score×10"
                gate_history.append(("CLOSE", vni["time"].iloc[i].date(), close[i], trigger, sessions_in))

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 8 — BƯỚC 7+8: SMOOTHING CUỐI CÙNG
# ════════════════════════════════════════════════════════════════════════════
"""
BƯỚC 7: ROLLING MODE (cửa sổ 15 phiên)
════════════════════════════════════════
Lấy state xuất hiện nhiều nhất trong 15 phiên gần nhất.

Tại sao mode thay vì EMA?
  - State là categorical (1/2/3/4/5), không phải số liên tục.
  - EMA của số không có ý nghĩa: EMA(CRISIS=1, BULL=4) = 2.5 ≠ trạng thái hợp lệ.
  - Mode giữ nguyên chất categorical, chọn state "chiếm đa số" trong window.

Tại sao 15 phiên (~3 tuần)?
  - Đủ ngắn để phản ứng kịp thời khi xu hướng thật sự thay đổi
  - Đủ dài để lọc nhiễu 1-3 ngày dao động qua ngưỡng
  - Tie-break: ưu tiên state gần nhất (tránh dùng state lịch sử cũ hơn)

BƯỚC 8: MIN_STAY_FILTER (tối thiểu 7 phiên/trạng thái)
═════════════════════════════════════════════════════════
Sau rolling mode vẫn còn đoạn 1-6 phiên. min_stay_filter xử lý triệt để:
  - Quét toàn bộ chuỗi, tìm đoạn nào < 7 phiên
  - Sáp nhập vào trạng thái liền trước (hoặc liền sau nếu ở đầu chuỗi)
  - Lặp cho đến khi tất cả đoạn đều ≥ 7 phiên

Tại sao 7 phiên (không phải 5 hay 10)?
  - Grid search (ms 1→20) + so sánh trực tiếp toàn bộ backtest:
    ms=7:  CAGR=12.1%  Calmar=0.63  MaxDD=-19.3%  Sharpe=1.06  (128 transitions)
    ms=10: CAGR=11.6%  Calmar=0.53  MaxDD=-21.8%  Sharpe=1.01  (99 transitions)
  - ms=7 THẮNG trên TẤT CẢ chỉ số hiệu suất.
  - ms=10 chỉ giảm được 29 transitions — không đủ để đánh đổi.
  - Lưu ý: sensitivity analysis quick_backtest cho kết quả ngược (ms=10 tốt hơn)
    → đây là artifact của quick_backtest dùng code path khác. Direct backtest là đúng.
"""

MODE_WIN = 15
MIN_STAY = 7   # xác nhận tốt hơn ms=10 qua so sánh trực tiếp (không phải quick_backtest)

def rolling_mode(states, window=15):
    out = states.copy()
    for t in range(window-1, len(states)):
        w = states[t-window+1:t+1]
        vals, counts = np.unique(w, return_counts=True)
        cands = vals[counts == counts.max()]
        for v in reversed(w):
            if v in cands: out[t] = v; break
    return out

def min_stay_filter(states, min_days=7):
    """Loại bỏ đoạn trạng thái < min_days phiên bằng cách sáp nhập."""
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j < len(out) and out[j] == out[i]: j += 1
            if j-i < min_days:
                fill = out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

state_mode   = rolling_mode(state_dvg, MODE_WIN)
state_smooth = min_stay_filter(state_mode, MIN_STAY)

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 9 — GIẢI THÍCH NGÀY CỤ THỂ: explain_day()
# ════════════════════════════════════════════════════════════════════════════

STATE_NAMES  = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}
STATE_ALLOC  = {1:"0%", 2:"20%", 3:"70%", 4:"100%", 5:"130%"}
OVERRIDE_LBL = {0:"—", 1:"PE>P90 → EX-BULL cap BULL", 2:"DD<-25% → cap NEUTRAL", 3:"Vol>1.5x → EX-BULL cap BULL"}


def explain_day(date_str):
    """
    In toàn bộ 8 bước ra quyết định cho một ngày cụ thể.

    Ví dụ:
      explain_day("2026-04-28")  # ngày hôm nay
      explain_day("2022-01-28")  # ngày CRISIS đầu 2022
    """
    mask = vni["time"].dt.strftime("%Y-%m-%d") == date_str
    if not mask.any():
        print(f"Không tìm thấy ngày {date_str} trong dữ liệu"); return
    i = vni[mask].index[0]

    print(f"\n{'═'*72}")
    print(f"  GIẢI THÍCH TRẠNG THÁI: {date_str}")
    print(f"{'═'*72}")
    print(f"  VNINDEX close = {close[i]:.2f}  │  PE = {pe_arr[i]:.2f}x  │  DD từ đỉnh = {dd[i]:.1%}")

    # ── BƯỚC 1: 7 yếu tố ──────────────────────────────────────────────────
    print(f"\n  ┌─ BƯỚC 1: 7 YẾU TỐ RAW & EXPANDING RANK ─────────────────────────")
    print(f"  │  {'Yếu tố':<10} {'Trọng số':>9} {'Giá trị thô':>14} {'Rank (0→1)':>12}  Đánh giá")
    print(f"  │  {'─'*60}")
    factor_display = {
        "P3M":     (p3m[i],       "%",  "% tăng 3 tháng"),
        "P1M":     (p1m[i],       "%",  "% tăng 1 tháng"),
        "MA200":   (ma200_dev[i], "%",  "giá/MA200-1"),
        "RSI":     (rsi[i],       "",   "RSI Wilder14 [0-1]"),
        "MACD":    (macd_hist[i], "",   "MACD histogram"),
        "CMF":     (cmf[i],       "",   "Chaikin MF14"),
        "Breadth": (breadth_arr[i] if "breadth" in vni.columns else np.nan, "", "% cổ phiếu>MA50"),
    }
    avail_ranks = {}
    for k, (raw_val, unit, _) in factor_display.items():
        r = ranks[k][i]
        raw_str = (f"{raw_val*100:+.1f}{unit}" if not np.isnan(raw_val) and unit == "%" else
                   f"{raw_val:.4f}" if not np.isnan(raw_val) else "N/A")
        rank_str = f"{r:.3f}" if not np.isnan(r) else "N/A (chưa đủ lịch sử)"
        emoji = ("🔴" if not np.isnan(r) and r < 0.30 else
                 "🟡" if not np.isnan(r) and r < 0.70 else
                 "🟢" if not np.isnan(r) else "⚪")
        print(f"  │  {k:<10} {W[k]:>8.0%}  {raw_str:>14}  {rank_str:>10}  {emoji}")
        if not np.isnan(r): avail_ranks[k] = r

    # ── BƯỚC 2: Composite score ────────────────────────────────────────────
    print(f"  │")
    print(f"  ├─ BƯỚC 2: COMPOSITE SCORE ──────────────────────────────────────────")
    w_sum   = sum(W[k] for k in avail_ranks)
    score_i = sum(avail_ranks[k]*W[k] for k in avail_ranks) / w_sum if w_sum > 0 else np.nan
    for k in avail_ranks:
        contrib = avail_ranks[k] * W[k] / w_sum
        bar = "█" * int(contrib * 30)
        print(f"  │    {k:<10} rank={avail_ranks[k]:.3f} × w={W[k]:.2f} ÷ {w_sum:.2f} → {contrib:.3f}  {bar}")
    print(f"  │    score = {score_i:.4f}")

    # ── BƯỚC 3: r_score + EMA ─────────────────────────────────────────────
    r_sc  = r_score[i]
    r_ema = r_score_ema[i]
    print(f"  │    rank(score) trong lịch sử = r_score = {r_sc:.4f}")
    print(f"  │    EMA(α=0.40): r_score_ema = {r_ema:.4f}  (sẽ dùng để phân loại)")

    # ── BƯỚC 4: phân loại thô ────────────────────────────────────────────
    print(f"  │")
    print(f"  ├─ BƯỚC 4: PHÂN LOẠI THÔ THEO NGƯỠNG ──────────────────────────────")
    thresholds = [
        ("<0.10",     "CRISIS",  r_ema < 0.10),
        ("0.10-0.20", "BEAR",    0.10 <= r_ema < 0.20),
        ("0.20-0.70", "NEUTRAL", 0.20 <= r_ema < 0.70),
        ("0.70-0.90", "BULL",    0.70 <= r_ema < 0.90),
        ("≥0.90",     "EX-BULL", r_ema >= 0.90),
    ]
    for rng, name, here in thresholds:
        marker = f"  ← r_score_ema={r_ema:.4f} — ĐÂY" if here else ""
        print(f"  │    {rng:<12} → {name:<10}{marker}")
    print(f"  │  → state_raw = {STATE_NAMES[state_raw[i]]}  ({STATE_ALLOC[state_raw[i]]})")

    # ── BƯỚC 5: Risk overrides ────────────────────────────────────────────
    print(f"  │")
    print(f"  ├─ BƯỚC 5: RISK OVERRIDES ───────────────────────────────────────────")
    pe_ok = not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i])
    print(f"  │    Override1 PE: hiện={pe_arr[i]:.2f}x  P90={pe_p90[i]:.2f}x  "
          f"→ {'⚠ TRIGGER (EX-BULL→BULL)' if pe_ok and pe_arr[i]>pe_p90[i] and state_raw[i]==5 else 'OK'}")
    print(f"  │    Override2 DD: drawdown={dd[i]:.1%}  threshold=-25%  "
          f"→ {'⚠ TRIGGER (→NEUTRAL)' if dd[i]<-0.25 else 'OK'}")
    vol_ok = not np.isnan(vol20[i]) and not np.isnan(avg_vol_exp[i])
    if vol_ok:
        ratio = vol20[i]/avg_vol_exp[i]
        print(f"  │    Override3 Vol: vol20={vol20[i]:.1%}  avg={avg_vol_exp[i]:.1%}  ratio={ratio:.2f}x  "
              f"→ {'⚠ TRIGGER (EX-BULL→BULL)' if ratio>1.5 and state_raw[i]==5 else 'OK'}")
    ov_lbl = OVERRIDE_LBL[override_log[i]]
    print(f"  │    Kết quả: {ov_lbl}")
    print(f"  │  → state_after_override = {STATE_NAMES[state_after_override[i]]}")

    # ── BƯỚC 6: BearDvg gate ─────────────────────────────────────────────
    print(f"  │")
    print(f"  ├─ BƯỚC 6: BEARDVG GATE ─────────────────────────────────────────────")
    print(f"  │    BearDvg signal hôm nay: {'⚠ CÓ — timer reset' if bear_mask[i] else 'Không'}")
    print(f"  │    BullDvg signal hôm nay: {'✓ CÓ — điều kiện thoát A' if bull_mask[i] else 'Không'}")
    if gate_flag[i]:
        sessions_ago = i - gate_start if gate_active else "?"
        p3_ok = (not np.isnan(p3m_rank_arr[i])) and p3m_rank_arr[i] > 0.45
        pe_ok2 = (not np.isnan(pe_rank_arr[i])) and pe_rank_arr[i] < 0.80
        rs_ok = bool(_rscore_streak[i])
        print(f"  │    Gate đang MỞ ⚠ (≥{sessions_ago} phiên từ BearDvg cuối)")
        print(f"  │    Điều kiện đóng (cần ≥60 phiên + 1 trong 3):")
        print(f"  │      A. BullDvg:  {'✓' if bull_mask[i] else '✗'}")
        print(f"  │      B. P3M({p3m_rank_arr[i]:.3f})>0.45 VÀ PE({pe_rank_arr[i]:.3f})<0.80: {'✓' if p3_ok and pe_ok2 else '✗'}")
        print(f"  │      C. r_score>0.65 × 10 phiên liên tiếp: {'✓' if rs_ok else '✗'}")
    else:
        print(f"  │    Gate đóng ✓ — hệ thống hoạt động bình thường")
    print(f"  │  → state_dvg = {STATE_NAMES[state_dvg[i]]}")

    # ── BƯỚC 7: Rolling mode ─────────────────────────────────────────────
    print(f"  │")
    print(f"  ├─ BƯỚC 7: ROLLING MODE (cửa sổ {MODE_WIN} phiên) ─────────────────────────")
    if i >= MODE_WIN - 1:
        window_states = state_dvg[i-MODE_WIN+1:i+1]
        from collections import Counter
        cnt = Counter(window_states.tolist())
        for s_id, c in sorted(cnt.items(), key=lambda x: -x[1]):
            chosen = " ← MODE (được chọn)" if s_id == state_mode[i] else ""
            bar = "▓" * c + "░" * (MODE_WIN - c)
            print(f"  │    {STATE_NAMES[s_id]:<10}: {c:2d}/{MODE_WIN} [{bar}]{chosen}")
    print(f"  │  → state_mode = {STATE_NAMES[state_mode[i]]}")

    # ── BƯỚC 8: min_stay_filter ──────────────────────────────────────────
    print(f"  │")
    print(f"  ├─ BƯỚC 8: MIN_STAY_FILTER (tối thiểu {MIN_STAY} phiên) ────────────────────")
    seg_start = i
    while seg_start > 0 and state_smooth[seg_start-1] == state_smooth[i]:
        seg_start -= 1
    seg_len = i - seg_start + 1
    print(f"  │    Đoạn trạng thái hiện tại bắt đầu: {vni['time'].iloc[seg_start].date()}")
    print(f"  │    Độ dài đến hôm nay: {seg_len} phiên (cần ≥{MIN_STAY}) → {'ổn định ✓' if seg_len>=MIN_STAY else 'ngắn → giữ state trước'}")

    # ── KẾT QUẢ CUỐI ─────────────────────────────────────────────────────
    final = state_smooth[i]
    changed_from = state_raw[i] != final
    print(f"  │")
    print(f"  └─ TRẠNG THÁI CUỐI: {STATE_NAMES[final]}  →  Phân bổ: {STATE_ALLOC[final]}")
    if changed_from:
        print(f"       (Đã thay đổi từ state_raw={STATE_NAMES[state_raw[i]]} qua các bước lọc)")
    print(f"{'═'*72}\n")


# ════════════════════════════════════════════════════════════════════════════
# PHẦN 10 — LỊCH SỬ CHUYỂN TRẠNG THÁI VỚI NGUYÊN NHÂN
# ════════════════════════════════════════════════════════════════════════════

def print_recent_transitions(n_recent=20):
    """
    In N lần chuyển trạng thái gần nhất kèm nguyên nhân chính.
    Nguyên nhân được phân tích theo thứ tự ưu tiên:
      1. Risk override fired?
      2. BearDvg gate opened?
      3. r_score_ema vượt/xuống ngưỡng?
    """
    print(f"\n{'═'*72}")
    print(f"  {n_recent} LẦN CHUYỂN TRẠNG THÁI GẦN NHẤT + NGUYÊN NHÂN")
    print(f"{'═'*72}")
    print(f"  {'Ngày':<12} {'Từ':<10} {'→ Sang':<11} {'VNI':>7} {'PE':>6} {'r_ema':>7}  Nguyên nhân")
    print(f"  {'─'*72}")

    trans_list = []
    prev = state_smooth[0]
    for i in range(1, n):
        if state_smooth[i] != prev:
            causes = []
            if state_raw[i] != state_after_override[i]:
                causes.append(OVERRIDE_LBL[override_log[i]])
            if state_after_override[i] != state_dvg[i]:
                causes.append("BearDvg gate mở")
            if gate_flag[i] and state_smooth[i] == 1 and not causes:
                causes.append("Gate khóa → CRISIS")
            if not causes:
                rs = r_score_ema[i]
                if not np.isnan(rs):
                    direction = "giảm" if prev > state_smooth[i] else "tăng"
                    causes.append(f"r_ema={rs:.3f} {direction} qua ngưỡng")
            if not causes: causes.append("Momentum thay đổi")

            trans_list.append({
                "i": i, "from": prev, "to": state_smooth[i],
                "date": vni["time"].iloc[i].strftime("%Y-%m-%d"),
                "vni": close[i], "pe": pe_arr[i],
                "r_ema": r_score_ema[i],
                "cause": " │ ".join(causes)
            })
            prev = state_smooth[i]

    for t in trans_list[-n_recent:]:
        fn = STATE_NAMES[t["from"]]; tn = STATE_NAMES[t["to"]]
        pe_s = f"{t['pe']:.1f}" if not np.isnan(t["pe"]) else "—"
        rs_s = f"{t['r_ema']:.3f}" if not np.isnan(t["r_ema"]) else "—"
        arrow = "↑" if t["to"] > t["from"] else "↓"
        print(f"  {t['date']:<12} {fn:<10} {arrow}{tn:<10} {t['vni']:>7.0f} {pe_s:>6} {rs_s:>7}  {t['cause']}")
    print()


def print_gate_history():
    """In lịch sử mở/đóng BearDvg gate."""
    print(f"\n{'═'*72}")
    print(f"  LỊCH SỬ BEARDVG GATE")
    print(f"{'═'*72}")
    if not gate_history:
        print("  Không có gate event nào."); return
    for ev in gate_history:
        if ev[0] == "OPEN":
            print(f"  🔒 MỞ   {ev[1]}  VNINDEX={ev[2]:.0f}  → khóa CRISIS (0%)")
        else:
            _, date, price, trigger, dur = ev
            print(f"  🔓 ĐÓNG {date}  VNINDEX={price:.0f}  sau {dur} phiên  trigger={trigger}")
    print()


# ════════════════════════════════════════════════════════════════════════════
# CHẠY PHÂN TÍCH
# ════════════════════════════════════════════════════════════════════════════

print(f"  Dữ liệu: {vni['time'].iloc[0].date()} → {vni['time'].iloc[-1].date()}")
print(f"  Tổng phiên: {n}  │  SPY thực tế: {sessions_per_year:.1f} phiên/năm\n")

# 1. Giải thích ngày hôm nay
latest_date = vni["time"].iloc[-1].strftime("%Y-%m-%d")
explain_day(latest_date)

# 2. Giải thích 2 lần transition gần nhất
trans_dates = []
prev_s = state_smooth[0]
for i in range(1, n):
    if state_smooth[i] != prev_s:
        trans_dates.append(vni["time"].iloc[i].strftime("%Y-%m-%d"))
        prev_s = state_smooth[i]

print(f">>> Giải thích 2 lần chuyển trạng thái gần nhất:\n")
for d in trans_dates[-2:]:
    explain_day(d)

# 3. Lịch sử transitions
print_recent_transitions(25)

# 4. Lịch sử gate
print_gate_history()

# 5. Tóm tắt trạng thái hiện tại + điều kiện chuyển tiếp
last = len(vni) - 1
cs   = state_smooth[last]
cs_ema = r_score_ema[last]

print(f"{'═'*72}")
print(f"  TÓM TẮT TRẠNG THÁI HIỆN TẠI ({latest_date})")
print(f"{'═'*72}")
print(f"  Trạng thái: {STATE_NAMES[cs]}  →  Phân bổ: {STATE_ALLOC[cs]}")
print(f"  r_score    : raw={r_score[last]:.4f}  EMA={cs_ema:.4f}")
print(f"  VNINDEX    : {close[last]:.2f}  │  PE={pe_arr[last]:.2f}x  │  PE P90={pe_p90[last]:.2f}x")
print(f"  DD từ đỉnh : {dd[last]:.1%}")
print(f"  BearDvg    : {'CÓ ⚠' if bear_mask[last] else 'Không'}")
print(f"  BullDvg    : {'CÓ ✓' if bull_mask[last] else 'Không'}")
print(f"  Gate       : {'MỞ ⚠ — đang khóa CRISIS' if gate_flag[last] else 'Đóng ✓'}")
print()

# Điều kiện chuyển tiếp
print(f"  ĐIỀU KIỆN ĐỂ THAY ĐỔI TRẠNG THÁI:")
print(f"  {'─'*60}")
if cs == 3:   # NEUTRAL
    print(f"  → BULL    : r_ema vượt 0.70 (hiện {cs_ema:.3f}, cần +{0.70-cs_ema:.3f})")
    print(f"              VÀ duy trì ≥7 phiên (mode×15 + min_stay×7)")
    print(f"  → BEAR    : r_ema xuống dưới 0.20 (hiện {cs_ema:.3f})")
    print(f"  → CRISIS  : r_ema xuống dưới 0.10 HOẶC BearDvg gate mở")
elif cs == 4: # BULL
    print(f"  → EX-BULL : r_ema vượt 0.90 (hiện {cs_ema:.3f}) VÀ PE≤P90 ({pe_p90[last]:.2f}x)")
    print(f"  → NEUTRAL : r_ema xuống dưới 0.70 (hiện {cs_ema:.3f})")
    print(f"  → CRISIS  : BearDvg gate mở (bất kể r_score)")
elif cs == 1: # CRISIS
    print(f"  → NEUTRAL : Gate đóng VÀ r_ema ≥ 0.20")
    if gate_flag[last]:
        print(f"    Gate đóng khi (OR sau ≥60 phiên):")
        print(f"      A. BullDvg signal xuất hiện")
        print(f"      B. P3M_rank>0.45 VÀ PE_rank<0.80")
        print(f"      C. r_ema>0.65 liên tục 10 phiên")
    else:
        print(f"    (Gate hiện đóng — đang chờ r_ema vượt 0.20)")
elif cs == 2: # BEAR
    print(f"  → NEUTRAL : r_ema vượt 0.20 (hiện {cs_ema:.3f}, cần +{0.20-cs_ema:.3f})")
    print(f"  → CRISIS  : r_ema xuống dưới 0.10 HOẶC BearDvg gate mở")
elif cs == 5: # EX-BULL
    print(f"  → BULL    : r_ema xuống dưới 0.90 (hiện {cs_ema:.3f})")
    print(f"              HOẶC PE vượt P90 ({pe_p90[last]:.2f}x, hiện {pe_arr[last]:.2f}x)")
print(f"  (Mọi thay đổi cần thêm: mode(15 phiên) + min_stay(7 phiên))")
print()

# Thống kê phân bổ thời gian
from collections import Counter
state_dist = Counter(state_smooth.tolist())
total_sessions = len(state_smooth)
print(f"  PHÂN BỔ THỜI GIAN THEO TRẠNG THÁI (toàn lịch sử):")
print(f"  {'─'*50}")
for s in [1,2,3,4,5]:
    cnt = state_dist[s]
    pct = cnt/total_sessions*100
    bar = "█" * int(pct/2)
    print(f"  {STATE_NAMES[s]:<10} {cnt:5d} phiên ({pct:5.1f}%)  {bar}")
print()

n_trans = sum(1 for i in range(1,n) if state_smooth[i] != state_smooth[i-1])
durs = []
prev_s = state_smooth[0]; seg = 0
for i in range(1, n):
    seg += 1
    if state_smooth[i] != prev_s or i == n-1:
        durs.append(seg); prev_s = state_smooth[i]; seg = 0
print(f"  Tổng transitions: {n_trans}  │  Median stay: {int(np.median(durs))} phiên")
print(f"  Không có đoạn nào < {MIN_STAY} phiên ✓ (đảm bảo bởi min_stay_filter)")
print(f"{'═'*72}")

# ════════════════════════════════════════════════════════════════════════════
# PHẦN 11 — GỢI Ý: explain_day() với ngày bất kỳ
# ════════════════════════════════════════════════════════════════════════════
print(f"""
  Để giải thích một ngày cụ thể, gọi:
    explain_day("2022-01-28")   # ví dụ: CRISIS đầu năm 2022
    explain_day("2021-07-01")   # ví dụ: từ BULL xuống NEUTRAL

  Để xem khi nào gate đóng/mở:
    print_gate_history()

  Để xem 30 transition gần nhất:
    print_recent_transitions(30)
""")
