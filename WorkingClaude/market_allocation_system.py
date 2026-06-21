"""
Market Allocation System
=========================
Dua ra ty trong tien mat / co phieu / don bay
dua tren 5-State Machine + market_overheat enhancement

Du lieu:
- PANIC + oversell_extreme : Fwd3M +5.9%, Win 67.3%
- BULL + PE < P50          : Fwd3M +3.2%, Win 66.6%
- BULL + overbuy_extreme   : Fwd3M +9.0%, Win 63.2%
- NEUTRAL                  : Fwd3M +1.8%, Win 59.6%
- CAUTION                  : Fwd3M +2.0%, Win 59% (mixed)
- CAUTION+P3M>P95          : Fwd3M -4.7%, Win 32.7%
- BEAR + oversell_extreme  : Fwd3M -1.4%, Win 42.6%
- NEUTRAL+P3M>P95          : Fwd3M -1.4%, Win 48%

Max leverage cho phep: 1:1 (co phieu 200%, tien mat -100%)
Thuc te de nghi: toi da 1:0.5 (co phieu 150%)
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pandas as pd
import numpy as np
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

CSV_PATH = r"/home/trido/thanhdt/WorkingClaude/VNINDEX.csv"

NEEDED = ['time','Close','MA200','D_RSI','D_CMF','D_MACDdiff',
          'VNINDEX_PE','Change_3M','Change_1M']
df = pd.read_csv(CSV_PATH, usecols=lambda c: c in NEEDED, low_memory=False)
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time').reset_index(drop=True)
for col in ['Close','MA200','D_RSI','D_CMF','D_MACDdiff','VNINDEX_PE','Change_3M']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['daily_ret'] = df['Close'].pct_change().fillna(0)
df['Change_3M']  = df['Change_3M'].fillna(df['Close'].pct_change(63))
df['P3M_pct']    = df['Change_3M'] * 100

# ── Percentiles ──
pe_series = df['VNINDEX_PE'].dropna()
p3m_vals  = df['P3M_pct'].dropna()

PE_PCT  = {p: np.percentile(pe_series, p) for p in [20,30,40,50,60,65,70,75,80,85,90,95]}
P3M_PCT = {p: np.percentile(p3m_vals,  p) for p in [5,10,15,20,80,85,90,95]}

print("PE Percentiles (2016-2026):")
for k,v in PE_PCT.items(): print(f"  P{k} = {v:.2f}x")
print("\nP3M Percentiles (2000-2026):")
for k,v in P3M_PCT.items(): print(f"  P{k} = {v:+.2f}%")

# ═══════════════════════════════════════════════════════════
# ALLOCATION SCORING ENGINE
# ═══════════════════════════════════════════════════════════

def compute_allocation(row):
    """
    Input: 1 row cua VNINDEX data
    Output: dict voi score, stock_pct, cash_pct, leverage, zone, reason
    """
    cl   = row['Close']
    ma   = row['MA200']  if pd.notna(row['MA200'])  else cl
    r    = row['D_RSI']  if pd.notna(row['D_RSI'])  else 0.5
    m    = row['D_MACDdiff'] if pd.notna(row['D_MACDdiff']) else 0
    c3   = row['P3M_pct']   if pd.notna(row['P3M_pct'])   else 0
    pe   = row['VNINDEX_PE']
    has_pe = pd.notna(pe)
    above  = cl > ma

    reasons = []

    # ── STEP 1: Xac dinh State co ban ──
    if r < 0.32 and not above and c3 < -15:
        base_state = 'PANIC'
    elif not above and r < 0.40 and m < 0:
        base_state = 'BEAR'
    elif has_pe and pe >= PE_PCT[80] and r > 0.70 and above:
        base_state = 'CAUTION'
    elif not has_pe and above and r > 0.72 and c3 > 18:
        base_state = 'CAUTION'
    elif above and m >= 0 and r < 0.70 and (not has_pe or pe < PE_PCT[80]):
        base_state = 'BULL'
    else:
        base_state = 'NEUTRAL'

    # ── STEP 2: Nang cap state theo P3M overheat ──
    if base_state == 'CAUTION' and c3 > P3M_PCT[95]:
        state = 'SUPER_CAUTION'
        reasons.append(f'P3M={c3:+.0f}% > P95={P3M_PCT[95]:+.0f}% → SUPER_CAUTION')
    elif base_state == 'NEUTRAL' and c3 > P3M_PCT[95]:
        state = 'NEUTRAL_WARNING'
        reasons.append(f'P3M={c3:+.0f}% > P95={P3M_PCT[95]:+.0f}% trong NEUTRAL → WARNING')
    elif base_state == 'BEAR' and c3 < P3M_PCT[10]:
        state = 'BEAR_DEEP'
        reasons.append(f'P3M={c3:+.0f}% < P10={P3M_PCT[10]:+.0f}% → BEAR sâu, chưa đáy')
    else:
        state = base_state

    # ── STEP 3: Dinh luong co phieu theo state ──
    # Base allocation
    alloc_map = {
        'PANIC':           1.50,   # 150% stock → dung don bay 1:0.5
        'BULL':            1.00,   # 100% stock
        'NEUTRAL':         0.75,   # 75% stock
        'NEUTRAL_WARNING': 0.50,   # 50% stock → canh bao P3M cao
        'CAUTION':         0.30,   # 30% stock
        'SUPER_CAUTION':   0.00,   # 0% stock → thoat hoan toan
        'BEAR':            0.10,   # 10% stock → giu chut de tinh hinh
        'BEAR_DEEP':       0.00,   # 0% stock → chưa mua
    }
    stock_pct = alloc_map[state]

    # ── STEP 4: Dieu chinh theo PE ──
    if has_pe:
        if pe < PE_PCT[30]:              # PE rất rẻ (<P30)
            if state in ('BULL', 'PANIC'):
                stock_pct = min(stock_pct + 0.30, 1.50)
                reasons.append(f'PE={pe:.1f}x < P30={PE_PCT[30]:.1f}x → tang them 30pp')
            elif state == 'NEUTRAL':
                stock_pct = min(stock_pct + 0.15, 1.00)
                reasons.append(f'PE={pe:.1f}x < P30 → tang them 15pp')
        elif pe < PE_PCT[50]:            # PE trung binh thap (<P50)
            if state in ('BULL', 'PANIC'):
                stock_pct = min(stock_pct + 0.20, 1.50)
                reasons.append(f'PE={pe:.1f}x < P50={PE_PCT[50]:.1f}x → tang them 20pp')
            elif state == 'NEUTRAL':
                stock_pct = min(stock_pct + 0.10, 1.00)
                reasons.append(f'PE={pe:.1f}x < P50 → tang them 10pp')
        elif pe < PE_PCT[65]:            # PE trung binh
            pass                         # giu nguyen
        elif pe >= PE_PCT[90]:           # PE rất cao
            if state in ('BULL', 'NEUTRAL'):
                stock_pct = max(stock_pct - 0.20, 0)
                reasons.append(f'PE={pe:.1f}x >= P90={PE_PCT[90]:.1f}x → giam 20pp')
        elif pe >= PE_PCT[80]:           # PE cao
            if state in ('BULL', 'NEUTRAL'):
                stock_pct = max(stock_pct - 0.10, 0)
                reasons.append(f'PE={pe:.1f}x >= P80={PE_PCT[80]:.1f}x → giam 10pp')

    # ── STEP 5: Dieu chinh theo P3M momentum ──
    if state == 'BULL' and c3 > P3M_PCT[80]:    # BULL + momentum manh
        stock_pct = min(stock_pct + 0.10, 1.50)
        reasons.append(f'P3M={c3:+.0f}% > P80 trong BULL → momentum manh +10pp')
    elif state == 'PANIC' and c3 < P3M_PCT[10]:  # PANIC + oversell extreme → xac nhan
        stock_pct = min(stock_pct + 0.00, 1.50)  # da toi da roi
        reasons.append(f'P3M={c3:+.0f}% < P10 → xac nhan oversell')
    elif state == 'NEUTRAL' and c3 < P3M_PCT[10]: # NEUTRAL + oversell
        stock_pct = min(stock_pct + 0.10, 1.00)
        reasons.append(f'P3M={c3:+.0f}% < P10 trong NEUTRAL → oversell xac nhan')

    # ── STEP 6: Dieu chinh theo RSI ──
    if r < 0.30 and state in ('BULL','NEUTRAL','BEAR'):
        stock_pct = min(stock_pct + 0.10, 1.50)
        reasons.append(f'RSI={r:.2f} < 0.30 → oversold them +10pp')
    elif r > 0.75 and state in ('BULL','NEUTRAL'):
        stock_pct = max(stock_pct - 0.10, 0)
        reasons.append(f'RSI={r:.2f} > 0.75 → overbought -10pp')

    # ── STEP 7: Round & finalize ──
    stock_pct = round(stock_pct * 20) / 20   # round toi 5%
    stock_pct = max(0, min(1.50, stock_pct))  # cap 0% - 150%
    cash_pct  = 1.0 - stock_pct
    leverage  = stock_pct > 1.0

    # Zone label
    if stock_pct >= 1.40:
        zone = 'AGGRESSIVELY IN (Margin 1:0.5)'
    elif stock_pct >= 1.10:
        zone = 'LEVERAGED IN (Margin 1:0.2)'
    elif stock_pct >= 0.90:
        zone = 'FULLY IN'
    elif stock_pct >= 0.70:
        zone = 'MOSTLY IN'
    elif stock_pct >= 0.50:
        zone = 'BALANCED'
    elif stock_pct >= 0.25:
        zone = 'DEFENSIVE'
    elif stock_pct > 0:
        zone = 'MOSTLY CASH'
    else:
        zone = 'FULL CASH'

    return {
        'state': state,
        'stock_pct': stock_pct,
        'cash_pct':  cash_pct,
        'leverage':  leverage,
        'zone':      zone,
        'pe':        pe if has_pe else None,
        'rsi':       r,
        'p3m':       c3,
        'reasons':   reasons,
    }

# ═══════════════════════════════════════════════════════════
# BACKTEST: TY TRONG THEO ALLOCATION SCORE
# ═══════════════════════════════════════════════════════════
print("\n\nComputing daily allocations...")

allocations = []
for i, row in df.iterrows():
    a = compute_allocation(row)
    allocations.append(a)

df['stock_pct']  = [a['stock_pct'] for a in allocations]
df['cash_pct']   = [a['cash_pct']  for a in allocations]
df['alloc_state']= [a['state']     for a in allocations]
df['zone']       = [a['zone']      for a in allocations]

# Backtest phan bo theo ty trong
CASH_RATE    = 0.06 / 252
MARGIN_COST  = 0.085 / 252   # lai vay 8.5%/nam khi co don bay

def backtest_weighted(df):
    n = len(df)
    portfolio = np.zeros(n)
    portfolio[0] = 100.0
    stock_w = df['stock_pct'].values
    ret     = df['daily_ret'].values

    for i in range(1, n):
        prev  = portfolio[i-1]
        sw    = stock_w[i-1]
        cw    = 1 - sw                # cash weight (co the am neu co don bay)
        # Return
        mkt_ret = ret[i]
        if sw <= 1.0:                 # khong vay
            r = sw * mkt_ret + cw * CASH_RATE
        else:                         # vay (sw > 1)
            borrowed = sw - 1.0       # ty le vay
            r = sw * mkt_ret - borrowed * MARGIN_COST + 0 * CASH_RATE
            # (100% von chu so huu: lai tu cp - chi phi vay)
        portfolio[i] = prev * (1 + r)
    return portfolio

port = backtest_weighted(df)
df['portfolio_alloc'] = port

# So sanh voi Buy & Hold
bh_port = np.zeros(len(df))
bh_port[0] = 100.0
for i in range(1, len(df)):
    bh_port[i] = bh_port[i-1] * (1 + df['daily_ret'].iloc[i])

years = (df['time'].iloc[-1] - df['time'].iloc[0]).days / 365.25

def metrics(portfolio):
    total = (portfolio[-1]/portfolio[0] - 1)*100
    cagr  = ((portfolio[-1]/portfolio[0])**(1/years) - 1)*100
    peak  = np.maximum.accumulate(portfolio)
    dd    = (portfolio - peak)/peak
    maxdd = dd.min()*100
    pr    = np.diff(portfolio)/portfolio[:-1]
    sharpe= np.mean(pr)/np.std(pr)*np.sqrt(252) if np.std(pr)>0 else 0
    calmar= cagr/abs(maxdd) if maxdd!=0 else 0
    return total, cagr, maxdd, sharpe, calmar

print("\n" + "="*65)
print("BACKTEST: ALLOCATION-BASED vs BUY&HOLD")
print("="*65)

t1,c1,dd1,s1,cal1 = metrics(port)
t2,c2,dd2,s2,cal2 = metrics(bh_port)
print(f"\n{'':30} {'Allocation':>12} {'Buy&Hold':>12}")
print(f"  Total Return:          {t1:>11.1f}% {t2:>11.1f}%")
print(f"  CAGR:                  {c1:>11.1f}% {c2:>11.1f}%")
print(f"  Max Drawdown:          {dd1:>11.1f}% {dd2:>11.1f}%")
print(f"  Sharpe:                {s1:>12.2f} {s2:>12.2f}")
print(f"  Calmar:                {cal1:>12.2f} {cal2:>12.2f}")
print(f"  Avg Stock Weight:      {df['stock_pct'].mean()*100:>10.1f}% {'100.0%':>12}")

# ═══════════════════════════════════════════════════════════
# BANG TONG HOP CAC ZONE
# ═══════════════════════════════════════════════════════════
print("\n" + "="*65)
print("BANG PHAN BO THEO ZONE")
print("="*65)

zone_stats = df.groupby('zone').agg(
    n=('zone','count'),
    avg_stock=('stock_pct','mean'),
    fwd_3m=('fwd_3m' if 'fwd_3m' in df.columns else 'daily_ret', lambda x: x.mean())
).reset_index()

df['fwd_3m'] = df['Close'].shift(-63) / df['Close'] - 1
df['fwd_1m'] = df['Close'].shift(-21) / df['Close'] - 1

print(f"\n{'Zone':<35} {'N':>5} {'%Time':>6} {'Avg Stock':>10} {'Fwd3M':>7} {'Win3M':>6}")
print("-"*70)

zone_order = [
    'AGGRESSIVELY IN (Margin 1:0.5)',
    'LEVERAGED IN (Margin 1:0.2)',
    'FULLY IN',
    'MOSTLY IN',
    'BALANCED',
    'DEFENSIVE',
    'MOSTLY CASH',
    'FULL CASH',
]
for z in zone_order:
    mask = df['zone'] == z
    n = mask.sum()
    if n == 0: continue
    avg_s = df.loc[mask,'stock_pct'].mean()*100
    f3 = df.loc[mask,'fwd_3m'].dropna()
    f3m = f3.median()*100 if len(f3)>0 else 0
    w3  = (f3>0).mean()*100 if len(f3)>0 else 0
    pct_time = n/len(df)*100
    print(f"{z:<35} {n:>5} {pct_time:>5.1f}% {avg_s:>9.0f}% {f3m:>+6.1f}% {w3:>5.1f}%")

# ═══════════════════════════════════════════════════════════
# LICH SU PHAN BO: CAC THOI DIEM QUAN TRONG
# ═══════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PHAN BO TAI CAC SU KIEN LICH SU QUAN TRONG")
print("="*65)

KEY_EVENTS = {
    '2007-03 Dinh VNI 1170':     '2007-03-12',
    '2008-03 Bear bat dau':      '2008-03-01',
    '2009-02 Day 235':           '2009-02-24',
    '2009-07 Phuc hoi manh':     '2009-07-20',
    '2012-01 Day 350':           '2012-01-09',
    '2015-09 Sau sell-off':      '2015-09-01',
    '2016-02 Low 500':           '2016-02-12',
    '2017-10 Bull PE cao':       '2017-10-01',
    '2018-04 Dinh 1204 PE22x':  '2018-04-09',
    '2020-03 COVID crash':       '2020-03-23',
    '2020-11 Hau COVID':         '2020-11-02',
    '2021-07 Bull PE17x':        '2021-07-30',
    '2021-11 Dinh 1500':         '2021-11-24',
    '2022-06 Mid crash':         '2022-06-20',
    '2022-11 Day 943 PE10x':     '2022-11-16',
    '2023-10 Panic RSI thap':    '2023-10-26',
    '2024-07 VNI 1250':          '2024-07-01',
    '2025-04 Tariff crash':      '2025-04-08',
    '2026-04 HIEN TAI':          '2026-04-17',
}

print(f"\n{'Su kien':<28} {'VNI':>5} {'PE':>6} {'RSI':>5} {'P3M':>7} {'State':>15} | {'Co phieu':>8} {'Tien mat':>8} {'Zone'}")
print("-"*105)

for event, date_str in KEY_EVENTS.items():
    dt = pd.to_datetime(date_str)
    idx = df['time'].searchsorted(dt)
    if idx >= len(df): idx = len(df)-1
    row  = df.iloc[idx]
    alloc= allocations[idx]
    pe_s = f"{row['VNINDEX_PE']:.1f}x" if pd.notna(row['VNINDEX_PE']) else "N/A"
    p3m_s= f"{row['P3M_pct']:+.0f}%" if pd.notna(row['P3M_pct']) else "N/A"
    sp   = alloc['stock_pct']*100
    cp   = alloc['cash_pct']*100
    lev  = " (MARGIN)" if alloc['leverage'] else ""
    print(f"{event:<28} {row['Close']:>5.0f} {pe_s:>6} {row['D_RSI']:>5.2f} {p3m_s:>7} {alloc['state']:>15} | {sp:>7.0f}% {cp:>7.0f}% {alloc['zone'][:25]}{lev}")

# ═══════════════════════════════════════════════════════════
# BANG TONG HOP CHIEN LUOC: DE XEM NHANH
# ═══════════════════════════════════════════════════════════
print("\n\n" + "="*65)
print("BANG CHIEN LUOC PHAN BO (DE XEM NHANH)")
print("="*65)

STRAT_TABLE = [
    # state, PE zone, P3M zone, stock%, cash%, action, ghi chu
    ('PANIC',        'bat ky',   'P3M<P10',   150, -50,  'AGGRESSIVELY IN + MARGIN', 'RSI<0.32+duoi MA200+C3M<-15%+oversell → mua manh nhat'),
    ('PANIC',        'bat ky',   'binh thuong',130, -30, 'LEVERAGED IN',             'RSI<0.32+duoi MA200+C3M<-15% → mua manh'),
    ('BULL',         'PE<P30',   'binh thuong',150, -50, 'AGGRESSIVELY IN + MARGIN', 'Tren MA200+MACD+>+PE rat re → leverage'),
    ('BULL',         'PE<P50',   'binh thuong',120, -20, 'LEVERAGED IN',             'Tren MA200+MACD>0+PE re → tang them don bay nhe'),
    ('BULL',         'PE<P80',   'P3M>P80',   110, -10, 'LEVERAGED IN',             'Momentum manh, PE ok'),
    ('BULL',         'PE<P80',   'binh thuong',100,   0, 'FULLY IN',                 'Tren MA200+MACD>0+PE trung binh → duy tri 100%'),
    ('BULL',         'PE>=P80',  'binh thuong', 80,  20, 'MOSTLY IN',               'BULL nhung PE bat dau cao'),
    ('NEUTRAL',      'PE<P50',   'binh thuong', 85,  15, 'MOSTLY IN',               'Xu huong trung lap, PE de chiu'),
    ('NEUTRAL',      'PE<P80',   'binh thuong', 75,  25, 'MOSTLY IN',               'Giu vi the, khong mo them'),
    ('NEUTRAL',      'PE>=P80',  'binh thuong', 60,  40, 'BALANCED',                'NEUTRAL nhung PE cao'),
    ('NEUTRAL',      'bat ky',   'P3M>P95',    50,  50, 'BALANCED → CANH BAO',      'P3M qua cao, giam ty trong'),
    ('CAUTION',      'PE>=P80',  'binh thuong', 30,  70, 'DEFENSIVE',               'PE cao+RSI>0.70+tren MA200 → giam manh'),
    ('SUPER_CAUTION','PE>=P80',  'P3M>P95',     0, 100, 'FULL CASH',                'PE cao+RSI cao+P3M cuc cao → thoat hoan toan'),
    ('BEAR',         'bat ky',   'binh thuong', 10,  90, 'MOSTLY CASH',             'Duoi MA200+RSI<0.40+MACD am → giu tien'),
    ('BEAR_DEEP',    'bat ky',   'P3M<P10',     0, 100, 'FULL CASH',               'Bear + thi truong van dang rot → KHONG mua'),
]

print(f"\n{'State':<16} {'PE':>12} {'P3M':>12} {'CP':>5} {'TM':>5} {'Zone':<30} Ghi chu")
print("-"*115)
for row in STRAT_TABLE:
    st, pe_z, p3m_z, sp, cp, zone, note = row
    cp_s = f"{cp:+.0f}%" if cp < 0 else f"+{cp}%"
    lev_s = " ← MARGIN" if sp > 100 else ""
    print(f"{st:<16} {pe_z:>12} {p3m_z:>12} {sp:>4}% {cp:>4}% {zone:<30} {note[:50]}{lev_s}")

# ═══════════════════════════════════════════════════════════
# TRANG THAI HIEN TAI
# ═══════════════════════════════════════════════════════════
print("\n" + "="*65)
print("TRANG THAI HIEN TAI & PHAN BO DE NGHI (2026-04-17)")
print("="*65)

latest_idx = df[df['time'] <= '2026-04-18'].index[-1]
latest_row = df.iloc[latest_idx]
latest_alloc = allocations[latest_idx]

print(f"""
  VNINDEX   : {latest_row['Close']:.0f}
  MA200     : {latest_row['MA200']:.0f}  ({'TREN' if latest_row['Close'] > latest_row['MA200'] else 'DUOI'} MA200, +{(latest_row['Close']/latest_row['MA200']-1)*100:.1f}%)
  RSI       : {latest_row['D_RSI']:.3f}  ({'binh thuong' if 0.40 < latest_row['D_RSI'] < 0.65 else 'cao' if latest_row['D_RSI'] >= 0.65 else 'thap'})
  MACDdiff  : {latest_row['D_MACDdiff']:+.2f}  ({'DUONG - bullish' if latest_row['D_MACDdiff'] >= 0 else 'AM - bearish'})
  PE        : {latest_row['VNINDEX_PE']:.2f}x  (P{sum(latest_row['VNINDEX_PE'] > v for v in PE_PCT.values())*100//len(PE_PCT):.0f} khu vuc)
  P3M       : {latest_row['P3M_pct']:+.1f}%  ({P3M_PCT[10]:.1f}% to {P3M_PCT[90]:.1f}% la binh thuong)

  ──────────────────────────────────────
  State     : {latest_alloc['state']}
  Zone      : {latest_alloc['zone']}
  ──────────────────────────────────────
  Co phieu  : {latest_alloc['stock_pct']*100:.0f}%
  Tien mat  : {latest_alloc['cash_pct']*100:.0f}%
  Don bay   : {'CO (Margin)' if latest_alloc['leverage'] else 'KHONG'}
  ──────────────────────────────────────""")

print(f"\n  Ly do dieu chinh:")
for rsn in latest_alloc['reasons']:
    print(f"    → {rsn}")
if not latest_alloc['reasons']:
    print(f"    → Gia tri mac dinh theo state {latest_alloc['state']}")

# Kich ban thay doi
print(f"""
  KICH BAN THAY DOI:
  → RSI len > 0.70 va PE len > 17.0x va P3M > +21%  → CAUTION (30%)
  → RSI xuong < 0.40 va xuong MA200                  → BEAR (10%)
  → RSI < 0.32 + xuong MA200 + P3M < -15%           → PANIC (150%)
  → PE xuong < 14.57x (P40)                          → BULL + them 20pp → 120%
""")

# Save lich su phan bo
df[['time','Close','VNINDEX_PE','D_RSI','P3M_pct','alloc_state','zone','stock_pct','cash_pct']].to_csv(
    r"/home/trido/thanhdt/WorkingClaude/allocation_history.csv",
    index=False
)
print("\nLich su phan bo da luu → allocation_history.csv")
