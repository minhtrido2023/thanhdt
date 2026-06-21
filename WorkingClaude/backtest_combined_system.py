"""
Phân tích kết hợp 5-State Machine + market_overheat.md logic
=============================================================
Câu hỏi: Có nên kết hợp không? Và kết hợp như thế nào?

Logic market_overheat dùng:
  - P3M (3-month trailing return) percentile-based regime detection
  - Future-return statistics để xác định regime duration
  - Output: overbuy / oversell REGIME (không phải point-in-time)

5-State Machine dùng:
  - MA200 (trend)
  - RSI (momentum)
  - MACDdiff (momentum)
  - PE valuation (2016+)
  - Change_3M / C3M

Bài này kiểm tra:
  A. Overlap giữa hai hệ thống
  B. Các trường hợp 5SM và overheat MÂU THUẪN nhau
  C. Backtest 4 mode kết hợp
  D. Kết luận: nên dùng thế nào
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pandas as pd
import numpy as np
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

CSV_PATH = r"/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv"

NEEDED = ['time','Close','MA200','D_RSI','D_CMF','D_MACDdiff',
          'VNINDEX_PE','Change_3M','Change_1M']
df = pd.read_csv(CSV_PATH, usecols=lambda c: c in NEEDED, low_memory=False)
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time').reset_index(drop=True)
for col in ['Close','MA200','D_RSI','D_CMF','D_MACDdiff','VNINDEX_PE','Change_3M']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['daily_ret'] = df['Close'].pct_change().fillna(0)
df['Change_3M'] = df['Change_3M'].fillna(df['Close'].pct_change(63))

# ─────────────────────────────────────────────
# 1. TÍNH P3M PERCENTILE (như market_overheat.md)
# ─────────────────────────────────────────────
p3m = df['Change_3M'] * 100  # đổi về %

p3m_pct = {
    'P10': np.percentile(p3m.dropna(), 10),
    'P20': np.percentile(p3m.dropna(), 20),
    'P80': np.percentile(p3m.dropna(), 80),
    'P90': np.percentile(p3m.dropna(), 90),
    'P95': np.percentile(p3m.dropna(), 95),
}
print("P3M Percentiles (2000-2026):")
for k, v in p3m_pct.items():
    print(f"  {k} = {v:+.2f}%")

# PE percentiles
pe_series = df['VNINDEX_PE'].dropna()
pe_pct = {p: np.percentile(pe_series, p) for p in [20,40,60,70,75,80,90,95]}

# ─────────────────────────────────────────────
# 2. CLASSIFY OVERHEAT REGIME (simplified từ market_overheat.md)
# Thay vì future-return regime (cần look-ahead), dùng:
# - P3M > P95: overbuy_extreme
# - P3M > P80: overbuy_moderate
# - P3M < P10: oversell_extreme
# - P3M < P20: oversell_moderate
# Regime kéo dài: smoothed bằng 21-day rolling window
# ─────────────────────────────────────────────
df['P3M_pct'] = df['Change_3M'] * 100

# Rolling 21 ngày để xác định regime persistence (như market_overheat dùng regime grouping)
df['overbuy_extreme']   = (df['P3M_pct'] >= p3m_pct['P95']).rolling(21, min_periods=1).max().astype(bool)
df['overbuy_moderate']  = (df['P3M_pct'] >= p3m_pct['P80']).rolling(21, min_periods=1).max().astype(bool)
df['oversell_extreme']  = (df['P3M_pct'] <= p3m_pct['P10']).rolling(21, min_periods=1).max().astype(bool)
df['oversell_moderate'] = (df['P3M_pct'] <= p3m_pct['P20']).rolling(21, min_periods=1).max().astype(bool)

# ─────────────────────────────────────────────
# 3. CLASSIFY 5-STATE MACHINE
# ─────────────────────────────────────────────
P80_PE  = pe_pct[80]   # 17.04x
P75_PE  = pe_pct[75]
RSI_SELL  = 0.70
RSI_BEAR  = 0.40
RSI_PANIC = 0.32

def classify_5state(df):
    ma200 = df['MA200'].ffill()
    rsi   = df['D_RSI'].fillna(0.5)
    macd  = df['D_MACDdiff'].fillna(0)
    close = df['Close']
    c3m   = df['Change_3M'].fillna(0)
    pe    = df['VNINDEX_PE']

    states = []
    prev = 'NEUTRAL'
    for i in range(len(df)):
        cl = close.iloc[i]
        ma = ma200.iloc[i] if pd.notna(ma200.iloc[i]) else cl
        r  = rsi.iloc[i]
        m  = macd.iloc[i]
        c3 = c3m.iloc[i]
        pv = pe.iloc[i]
        has_pe = pd.notna(pv)
        above  = cl > ma

        if r < RSI_PANIC and not above and c3 < -0.15:
            st = 'PANIC'
        elif not above and r < RSI_BEAR and m < 0:
            st = 'BEAR'
        elif has_pe and pv >= P80_PE and r > RSI_SELL and above:
            st = 'CAUTION'
        elif not has_pe and above and r > 0.72 and c3 > 0.18:
            st = 'CAUTION'
        elif above and m >= 0 and r < 0.70 and (not has_pe or pv < P80_PE):
            st = 'BULL'
        else:
            if prev in ('BEAR', 'CAUTION'):
                st = 'NEUTRAL' if (above and r < 0.60 and m >= 0) else prev
            else:
                st = 'NEUTRAL'

        prev = st
        states.append(st)
    return states

df['state_5sm'] = classify_5state(df)

# ─────────────────────────────────────────────
# 4. PHÂN TÍCH OVERLAP & MÂU THUẪN
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("A. OVERLAP & MÂU THUẪN GIỮA 2 HỆ THỐNG")
print("="*65)

# Matrix: state × overheat regime
for state in ['PANIC','BEAR','CAUTION','BULL','NEUTRAL']:
    mask_st = df['state_5sm'] == state
    n = mask_st.sum()
    if n == 0: continue

    ob_ext = (mask_st & df['overbuy_extreme']).sum()
    ob_mod = (mask_st & df['overbuy_moderate'] & ~df['overbuy_extreme']).sum()
    os_ext = (mask_st & df['oversell_extreme']).sum()
    os_mod = (mask_st & df['oversell_moderate'] & ~df['oversell_extreme']).sum()
    normal = n - ob_ext - ob_mod - os_ext - os_mod

    print(f"\n  5SM={state} (n={n:,d}):")
    print(f"    overbuy_extreme (P3M>P95): {ob_ext:>4d} ({ob_ext/n*100:4.1f}%) ← {'MÂU THUẪN nếu PANIC/BEAR' if state in ('PANIC','BEAR') and ob_ext>0 else ''}")
    print(f"    overbuy_moderate(P3M>P80): {ob_mod:>4d} ({ob_mod/n*100:4.1f}%)")
    print(f"    oversell_extreme(P3M<P10): {os_ext:>4d} ({os_ext/n*100:4.1f}%) ← {'MÂU THUẪN nếu CAUTION/BULL' if state in ('CAUTION','BULL') and os_ext>0 else ''}")
    print(f"    oversell_moderate(P3M<P20):{os_mod:>4d} ({os_mod/n*100:4.1f}%)")
    print(f"    normal (không extreme):    {normal:>4d} ({normal/n*100:4.1f}%)")

# ─────────────────────────────────────────────
# 5. FORWARD RETURN ANALYSIS: COMBO STATE
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("B. FORWARD RETURN THEO COMBO (5SM state × Overheat regime)")
print("="*65)

df['fwd_3m'] = df['Close'].shift(-63) / df['Close'] - 1
df['fwd_1m'] = df['Close'].shift(-21) / df['Close'] - 1

combos = [
    # PANIC combinations
    ('PANIC', 'oversell_extreme',  'PANIC + Oversell Extreme (P3M<P10)'),
    ('PANIC', 'oversell_moderate', 'PANIC + Oversell Moderate (P3M<P20)'),
    ('PANIC', 'normal',            'PANIC + Normal P3M'),
    ('PANIC', 'overbuy_moderate',  'PANIC + Overbuy (mau thuan!)'),
    # BEAR combinations
    ('BEAR', 'oversell_extreme',   'BEAR + Oversell Extreme'),
    ('BEAR', 'oversell_moderate',  'BEAR + Oversell Moderate'),
    ('BEAR', 'normal',             'BEAR + Normal P3M'),
    # CAUTION combinations
    ('CAUTION', 'overbuy_extreme', 'CAUTION + Overbuy Extreme (P3M>P95)'),
    ('CAUTION', 'overbuy_moderate','CAUTION + Overbuy Moderate'),
    ('CAUTION', 'normal',         'CAUTION + Normal P3M'),
    ('CAUTION', 'oversell_moderate','CAUTION + Oversell (mau thuan!)'),
    # BULL combinations
    ('BULL', 'overbuy_extreme',    'BULL + Overbuy Extreme'),
    ('BULL', 'overbuy_moderate',   'BULL + Overbuy Moderate'),
    ('BULL', 'normal',             'BULL + Normal P3M'),
    ('BULL', 'oversell_extreme',   'BULL + Oversell (mau thuan!)'),
    # NEUTRAL
    ('NEUTRAL', 'overbuy_extreme', 'NEUTRAL + Overbuy Extreme'),
    ('NEUTRAL', 'normal',          'NEUTRAL + Normal P3M'),
    ('NEUTRAL', 'oversell_extreme','NEUTRAL + Oversell'),
]

def get_mask(state, overheat_type):
    mask_st = df['state_5sm'] == state
    if overheat_type == 'overbuy_extreme':
        return mask_st & df['overbuy_extreme']
    elif overheat_type == 'overbuy_moderate':
        return mask_st & df['overbuy_moderate'] & ~df['overbuy_extreme']
    elif overheat_type == 'oversell_extreme':
        return mask_st & df['oversell_extreme']
    elif overheat_type == 'oversell_moderate':
        return mask_st & df['oversell_moderate'] & ~df['oversell_extreme']
    elif overheat_type == 'normal':
        return mask_st & ~df['overbuy_moderate'] & ~df['oversell_moderate']
    else:
        return mask_st

print(f"\n{'Combo':<44} {'N':>5} {'Fwd1M':>7} {'Win1M':>6} {'Fwd3M':>7} {'Win3M':>6} {'Dieu chinh'}")
print("-"*90)

results_combo = {}
for state, ov_type, label in combos:
    mask = get_mask(state, ov_type)
    n = mask.sum()
    if n < 10:
        print(f"{label:<44} {n:>5} (qua it du lieu)")
        continue
    f1 = df.loc[mask, 'fwd_1m'].dropna()
    f3 = df.loc[mask, 'fwd_3m'].dropna()
    f1_med = f1.median() * 100
    f3_med = f3.median() * 100
    w1 = (f1 > 0).mean() * 100
    w3 = (f3 > 0).mean() * 100

    # Baseline: just the 5SM state
    mask_base = df['state_5sm'] == state
    f3_base = df.loc[mask_base, 'fwd_3m'].dropna().median() * 100

    diff = f3_med - f3_base
    diff_str = f"+{diff:+.1f}pp vs base" if diff != 0 else ""

    results_combo[(state, ov_type)] = {'n': n, 'f1': f1_med, 'f3': f3_med, 'w1': w1, 'w3': w3, 'diff': diff}
    print(f"{label:<44} {n:>5} {f1_med:>+6.1f}% {w1:>5.1f}% {f3_med:>+6.1f}% {w3:>5.1f}% {diff_str}")

# ─────────────────────────────────────────────
# 6. BACKTEST 4 CHIẾN LƯỢC KẾT HỢP
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("C. BACKTEST 4 CHẾ ĐỘ KẾT HỢP")
print("="*65)

CASH_RATE = 0.06 / 252

def backtest(df, signal, name=""):
    n = len(df)
    portfolio = np.zeros(n)
    portfolio[0] = 100.0
    sig = signal.values
    ret = df['daily_ret'].values
    for i in range(1, n):
        prev = portfolio[i-1]
        if sig[i-1] == 1:
            portfolio[i] = prev * (1 + ret[i])
        else:
            portfolio[i] = prev * (1 + CASH_RATE)
    port = pd.Series(portfolio, index=df.index)
    years = (df['time'].iloc[-1] - df['time'].iloc[0]).days / 365.25
    total_ret = (portfolio[-1]/portfolio[0] - 1) * 100
    cagr = ((portfolio[-1]/portfolio[0])**(1/years) - 1) * 100
    peak = np.maximum.accumulate(portfolio)
    dd = (portfolio - peak) / peak
    max_dd = dd.min() * 100
    pr = np.diff(portfolio) / portfolio[:-1]
    sharpe = np.mean(pr)/np.std(pr)*np.sqrt(252) if np.std(pr)>0 else 0
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0
    time_in = sig.mean() * 100
    trades = int(np.sum(np.abs(np.diff(sig))))
    return {'name': name, 'cagr': cagr, 'max_dd': max_dd, 'sharpe': sharpe,
            'calmar': calmar, 'time_in': time_in, 'trades': trades, 'total': total_ret}

# Compute signals
state = df['state_5sm']
ob_ext = df['overbuy_extreme']
ob_mod = df['overbuy_moderate']
os_ext = df['oversell_extreme']
os_mod = df['oversell_moderate']

# Signal 0: Baseline 5-State Machine
sig_base = pd.Series(
    np.where(state.isin(['PANIC','BULL','NEUTRAL']), 1, 0),
    index=df.index
)

# Signal 1: 5SM + Overheat Enhancement
# Thêm: CAUTION + overbuy_extreme -> 0 (thoát sớm hơn, tín hiệu MẠNH hơn)
# Thêm: PANIC + oversell_extreme -> 1 (giữ IN, tín hiệu xác nhận)
# Thêm: BEAR + oversell_extreme -> 0 (giữ OUT, chưa mua)
sig_combo1 = sig_base.copy()
# Không thay đổi IN/OUT logic nhưng điều chỉnh:
# Khi NEUTRAL + overbuy_extreme -> OUT (warning → reduce)
combo1_mask_out = (state == 'NEUTRAL') & ob_ext
sig_combo1[combo1_mask_out] = 0

# Signal 2: 5SM + Overheat (Mạnh hơn)
# CAUTION → OUT (baseline đã đúng)
# NEUTRAL + overbuy_moderate → OUT (reduce)
# BEAR + oversell_extreme → thêm vào IN (sắp turning point)
sig_combo2 = sig_base.copy()
# NEUTRAL + overbuy_moderate -> OUT
combo2_out = (state == 'NEUTRAL') & ob_mod
sig_combo2[combo2_out] = 0
# BEAR + oversell_extreme -> IN (market_overheat nói oversell = turning point)
combo2_in = (state == 'BEAR') & os_ext
sig_combo2[combo2_in] = 1

# Signal 3: Dual confirmation (chặt nhất)
# IN chỉ khi 5SM = IN VÀ không có overbuy_extreme
# IN bổ sung khi PANIC/BEAR + oversell_extreme
sig_combo3 = sig_base.copy()
# Thêm filter: khi đang IN nhưng có overbuy_extreme AND PE era → OUT
has_pe = df['VNINDEX_PE'].notna()
sig_combo3[(sig_combo3 == 1) & ob_ext & has_pe] = 0
# BEAR + oversell_extreme → IN (xác nhận đáy)
sig_combo3[(state == 'BEAR') & os_ext] = 1

# Signal 4: Market_overheat driven (gần với market_overheat.md gốc)
# SELL khi overbuy_extreme, BUY khi oversell_moderate hoặc không overbuy
sig_combo4 = pd.Series(1, index=df.index)
sig_combo4[ob_ext] = 0  # overbuy_extreme → OUT
sig_combo4[os_mod]  = 1  # oversell → force IN

SYSTEMS = [
    (sig_base,    "0. Baseline 5-State Machine"),
    (sig_combo1,  "1. 5SM + NEUTRAL×OverbuyExt→OUT"),
    (sig_combo2,  "2. 5SM + NEUTRAL×Overbuy→OUT + BEAR×Oversell→IN"),
    (sig_combo3,  "3. 5SM + OverbuyExt→OUT(PE era) + BEAR×Oversell→IN"),
    (sig_combo4,  "4. Overheat driven (OverbuyExt→OUT, Oversell→IN)"),
    (pd.Series(1, index=df.index), "5. Buy & Hold"),
]

print(f"\n{'System':<42} {'CAGR':>7} {'MaxDD':>8} {'Sharpe':>7} {'Calmar':>7} {'%InMkt':>7} {'Trades':>6}")
print("-"*90)
results = {}
for sig, name in SYSTEMS:
    r = backtest(df, sig, name)
    results[name] = r
    print(f"{name:<42} {r['cagr']:>6.1f}% {r['max_dd']:>7.1f}% {r['sharpe']:>7.2f} {r['calmar']:>7.2f} {r['time_in']:>6.1f}% {r['trades']:>6d}")

# PE era only (2016+)
print("\n--- PE Era (2016+) ---")
pe_start = df[df['VNINDEX_PE'].notna()]['time'].min()
mask_pe = df['time'] >= pe_start
sub_pe = df[mask_pe].copy().reset_index(drop=True)
sub_pe['daily_ret'] = sub_pe['Close'].pct_change().fillna(0)

print(f"{'System':<42} {'CAGR':>7} {'MaxDD':>8} {'Sharpe':>7} {'Calmar':>7}")
print("-"*78)
for sig, name in SYSTEMS:
    sub_sig = sig[mask_pe].reset_index(drop=True)
    r = backtest(sub_pe, sub_sig, name)
    print(f"{name:<42} {r['cagr']:>6.1f}% {r['max_dd']:>7.1f}% {r['sharpe']:>7.2f} {r['calmar']:>7.2f}")

# ─────────────────────────────────────────────
# 7. CASE STUDY: KHI 2 HỆ THỐNG MÂU THUẪN
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("D. CASE STUDY: CÁC THỜI ĐIỂM 2 HỆ THỐNG MÂU THUẪN")
print("="*65)

# Trường hợp 1: CAUTION (5SM=bán) nhưng oversell (overheat=mua)
mau_thuan_1 = (state == 'CAUTION') & os_mod
print(f"\n1. CAUTION + Oversell (mau thuan): {mau_thuan_1.sum()} ngay")
if mau_thuan_1.sum() > 0:
    sub = df[mau_thuan_1][['time','Close','VNINDEX_PE','D_RSI','P3M_pct','fwd_3m']].dropna(subset=['fwd_3m'])
    print(f"   Fwd3M median: {sub['fwd_3m'].median()*100:+.1f}% | Win: {(sub['fwd_3m']>0).mean()*100:.1f}%")
    for _, row in sub.head(5).iterrows():
        print(f"   {row['time'].date()} VNI={row['Close']:.0f} PE={row['VNINDEX_PE']:.1f}x RSI={row['D_RSI']:.2f} P3M={row['P3M_pct']:+.1f}%")

# Trường hợp 2: PANIC (5SM=mua) nhưng overbuy (overheat=bán)
mau_thuan_2 = (state == 'PANIC') & ob_mod
print(f"\n2. PANIC + Overbuy (mau thuan): {mau_thuan_2.sum()} ngay")
if mau_thuan_2.sum() > 0:
    sub = df[mau_thuan_2][['time','Close','VNINDEX_PE','D_RSI','P3M_pct','fwd_3m']].dropna(subset=['fwd_3m'])
    print(f"   Fwd3M median: {sub['fwd_3m'].median()*100:+.1f}% | Win: {(sub['fwd_3m']>0).mean()*100:.1f}%")

# Trường hợp 3: BULL nhưng overbuy_extreme
mau_thuan_3 = (state == 'BULL') & ob_ext
print(f"\n3. BULL + OverbuyExtreme (canh bao): {mau_thuan_3.sum()} ngay")
if mau_thuan_3.sum() > 0:
    sub = df[mau_thuan_3][['time','Close','VNINDEX_PE','D_RSI','P3M_pct','fwd_3m']].dropna(subset=['fwd_3m'])
    f3 = sub['fwd_3m']
    print(f"   Fwd3M median: {f3.median()*100:+.1f}% | Win: {(f3>0).mean()*100:.1f}%")
    print(f"   → Nen giu IN hay OUT khi nay?")

# Trường hợp 4: BEAR + oversell_extreme (market_overheat noi mua, 5SM noi cho)
mau_thuan_4 = (state == 'BEAR') & os_ext
print(f"\n4. BEAR + Oversell Extreme (BEAR noi cho, overheat noi mua): {mau_thuan_4.sum()} ngay")
if mau_thuan_4.sum() > 0:
    sub = df[mau_thuan_4][['time','Close','VNINDEX_PE','D_RSI','P3M_pct','fwd_3m']].dropna(subset=['fwd_3m'])
    f3 = sub['fwd_3m']
    print(f"   Fwd3M median: {f3.median()*100:+.1f}% | Win: {(f3>0).mean()*100:.1f}%")
    print(f"   Phan bo P3M trong BEAR+Oversell: {sub['P3M_pct'].describe().to_dict()}")

# ─────────────────────────────────────────────
# 8. KET LUAN
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("E. KET LUAN: NEN KET HOP KHONG?")
print("="*65)

# Tìm combo tốt nhất từ bước 5 (forward return analysis)
print("\nTop 5 combo có Fwd3M tốt nhất:")
sorted_combos = sorted([(k,v) for k,v in results_combo.items() if v['n']>=30],
                        key=lambda x: x[1]['f3'], reverse=True)
for (state_k, ov_k), v in sorted_combos[:5]:
    label = f"{state_k} + {ov_k}"
    print(f"  {label:<45} Fwd3M={v['f3']:+.1f}% Win={v['w3']:.1f}% (n={v['n']})")

print("\nTop 5 combo có Fwd3M tệ nhất:")
for (state_k, ov_k), v in sorted_combos[-5:]:
    label = f"{state_k} + {ov_k}"
    print(f"  {label:<45} Fwd3M={v['f3']:+.1f}% Win={v['w3']:.1f}% (n={v['n']})")

# Backtest winner
print("\nBacktest winner (by Calmar, toàn giai đoạn):")
sorted_bt = sorted(results.items(), key=lambda x: x[1]['calmar'], reverse=True)
for name, r in sorted_bt:
    marker = " ← WINNER" if r['calmar'] == max(v['calmar'] for v in results.values()) else ""
    print(f"  {name:<42} Calmar={r['calmar']:.2f} CAGR={r['cagr']:.1f}%{marker}")

print("\nBacktest winner (by Calmar, PE era):")
# Rerun for display
for sig, name in SYSTEMS:
    sub_sig = sig[mask_pe].reset_index(drop=True)
    r = backtest(sub_pe, sub_sig, name)
    results[name + '_pe'] = r
pe_sorted = sorted([(n,v) for n,v in results.items() if '_pe' in n],
                    key=lambda x: x[1]['calmar'], reverse=True)
for name, r in pe_sorted:
    print(f"  {name.replace('_pe',''):<42} Calmar={r['calmar']:.2f} CAGR={r['cagr']:.1f}%")
