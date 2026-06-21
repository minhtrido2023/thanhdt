"""
Liệt kê cụ thể ngày ra/vào thị trường từ 2000-2026
theo từng hệ thống đề xuất
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

NEEDED = ['time','Close','MA200','D_RSI','D_CMF','D_MACDdiff','VNINDEX_PE','Change_3M','Change_1M']
df = pd.read_csv(CSV_PATH, usecols=lambda c: c in NEEDED, low_memory=False)
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time').reset_index(drop=True)

for col in ['Close','MA200','D_RSI','D_CMF','D_MACDdiff','VNINDEX_PE','Change_3M']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['daily_ret'] = df['Close'].pct_change().fillna(0)
if df['Change_3M'].isna().all():
    df['Change_3M'] = df['Close'].pct_change(63)

# PE percentiles
pe_series = df['VNINDEX_PE'].dropna()
pe_pct = {p: np.percentile(pe_series, p) for p in [10,20,30,40,50,60,65,70,75,80,85,90,95]}

# ─────────────────────────────────────────────────────────
# SYSTEM A: MA200 Cross (đơn giản, robust)
# ─────────────────────────────────────────────────────────
def get_trades_ma200(df):
    ma200 = df['MA200'].ffill()
    trades = []
    in_market = None
    for i in range(len(df)):
        cl = df['Close'].iloc[i]
        ma = ma200.iloc[i] if pd.notna(ma200.iloc[i]) else cl
        above = cl > ma
        if in_market is None:
            in_market = above
            continue
        if not in_market and above:
            trades.append({'date': df['time'].iloc[i], 'action': 'BUY',
                           'vnindex': cl, 'ma200': ma,
                           'rsi': df['D_RSI'].iloc[i],
                           'pe': df['VNINDEX_PE'].iloc[i],
                           'reason': f'Close {cl:.0f} vuot MA200 {ma:.0f}'})
            in_market = True
        elif in_market and not above:
            trades.append({'date': df['time'].iloc[i], 'action': 'SELL',
                           'vnindex': cl, 'ma200': ma,
                           'rsi': df['D_RSI'].iloc[i],
                           'pe': df['VNINDEX_PE'].iloc[i],
                           'reason': f'Close {cl:.0f} xuong duoi MA200 {ma:.0f}'})
            in_market = False
    return trades, in_market

# ─────────────────────────────────────────────────────────
# SYSTEM B: 5-State Machine (optimal params)
# PE P80=17.04x, RSI_sell=0.70, RSI_bear=0.40, RSI_panic=0.32
# ─────────────────────────────────────────────────────────
P80_VAL   = pe_pct[80]   # 17.04x
P75_VAL   = pe_pct[75]
P40_VAL   = pe_pct[40]
P70_VAL   = pe_pct[70]
RSI_SELL  = 0.70
RSI_BEAR  = 0.40
RSI_PANIC = 0.32

def get_trades_5state(df):
    ma200 = df['MA200'].ffill()
    trades = []
    prev_state = 'NEUTRAL'
    in_market = True
    prev_in = True

    for i in range(len(df)):
        cl  = df['Close'].iloc[i]
        ma  = ma200.iloc[i] if pd.notna(ma200.iloc[i]) else cl
        r   = df['D_RSI'].iloc[i] if pd.notna(df['D_RSI'].iloc[i]) else 0.5
        m   = df['D_MACDdiff'].iloc[i] if pd.notna(df['D_MACDdiff'].iloc[i]) else 0
        c3  = df['Change_3M'].iloc[i] if pd.notna(df['Change_3M'].iloc[i]) else 0
        pe  = df['VNINDEX_PE'].iloc[i]
        has_pe = pd.notna(pe)
        above = cl > ma
        t   = df['time'].iloc[i]

        # Determine state
        if r < RSI_PANIC and not above and c3 < -0.15:
            state = 'PANIC'
        elif not above and r < RSI_BEAR and m < 0:
            state = 'BEAR'
        elif has_pe and pe >= P80_VAL and r > RSI_SELL and above:
            state = 'CAUTION'
        elif not has_pe and above and r > 0.72 and c3 > 0.18:
            state = 'CAUTION'
        elif above and m >= 0 and r < 0.70 and (not has_pe or pe < P80_VAL):
            state = 'BULL'
        else:
            if prev_state in ('BEAR', 'CAUTION'):
                if above and r < 0.60 and m >= 0:
                    state = 'NEUTRAL'
                else:
                    state = prev_state
            else:
                state = 'NEUTRAL'

        in_market = state in ('PANIC', 'BULL', 'NEUTRAL')

        if prev_in and not in_market:
            pe_str = f"{pe:.1f}x" if has_pe else "N/A"
            trades.append({
                'date': t, 'action': 'SELL', 'state': state,
                'vnindex': cl, 'ma200': ma, 'rsi': r, 'pe': pe_str,
                'reason': f'State→{state} | RSI={r:.2f} | PE={pe_str} | {"tren" if above else "duoi"} MA200={ma:.0f}'
            })
        elif not prev_in and in_market:
            pe_str = f"{pe:.1f}x" if has_pe else "N/A"
            trades.append({
                'date': t, 'action': 'BUY', 'state': state,
                'vnindex': cl, 'ma200': ma, 'rsi': r, 'pe': pe_str,
                'reason': f'State→{state} | RSI={r:.2f} | PE={pe_str} | {"tren" if above else "duoi"} MA200={ma:.0f}'
            })

        prev_state = state
        prev_in = in_market

    return trades, in_market

# ─────────────────────────────────────────────────────────
# SYSTEM C: MACD Trend (tốt nhất về return)
# 2-day confirmation
# ─────────────────────────────────────────────────────────
def get_trades_macd(df):
    macd = df['D_MACDdiff'].fillna(0)
    trades = []
    in_market = True
    out_count = 0
    in_count  = 0
    prev_in   = True

    for i in range(len(df)):
        m  = macd.iloc[i]
        cl = df['Close'].iloc[i]
        r  = df['D_RSI'].iloc[i] if pd.notna(df['D_RSI'].iloc[i]) else 0.5
        pe = df['VNINDEX_PE'].iloc[i]
        t  = df['time'].iloc[i]

        if in_market:
            if m < 0:
                out_count += 1; in_count = 0
                if out_count >= 2:
                    in_market = False; out_count = 0
            else:
                out_count = 0
        else:
            if m > 0:
                in_count += 1; out_count = 0
                if in_count >= 2:
                    in_market = True; in_count = 0
            else:
                in_count = 0

        if prev_in and not in_market:
            pe_str = f"{pe:.1f}x" if pd.notna(pe) else "N/A"
            trades.append({'date': t, 'action': 'SELL',
                           'vnindex': cl, 'rsi': r, 'pe': pe_str,
                           'reason': f'MACD am 2 phien lien tiep | RSI={r:.2f} | PE={pe_str}'})
        elif not prev_in and in_market:
            pe_str = f"{pe:.1f}x" if pd.notna(pe) else "N/A"
            trades.append({'date': t, 'action': 'BUY',
                           'vnindex': cl, 'rsi': r, 'pe': pe_str,
                           'reason': f'MACD duong 2 phien lien tiep | RSI={r:.2f} | PE={pe_str}'})
        prev_in = in_market

    return trades, in_market

# ─────────────────────────────────────────────────────────
# RUN & DISPLAY
# ─────────────────────────────────────────────────────────

def compute_hold_days(trades, current_date):
    """Tính số ngày nắm giữ cho mỗi giao dịch."""
    result = []
    for i, t in enumerate(trades):
        if t['action'] == 'BUY':
            if i+1 < len(trades) and trades[i+1]['action'] == 'SELL':
                next_t = trades[i+1]
                hold = (next_t['date'] - t['date']).days
                ret = (next_t['vnindex'] - t['vnindex']) / t['vnindex'] * 100
                result.append({**t, 'hold_days': hold,
                                'exit_date': next_t['date'],
                                'exit_price': next_t['vnindex'],
                                'return_pct': ret})
            else:  # still in market
                hold = (current_date - t['date']).days
                ret = (df['Close'].iloc[-1] - t['vnindex']) / t['vnindex'] * 100
                result.append({**t, 'hold_days': hold,
                                'exit_date': pd.Timestamp('2026-04-17'),
                                'exit_price': df['Close'].iloc[-1],
                                'return_pct': ret,
                                'note': 'DANG HOLD'})
        elif t['action'] == 'SELL':
            if i+1 < len(trades) and trades[i+1]['action'] == 'BUY':
                next_t = trades[i+1]
                hold = (next_t['date'] - t['date']).days
                cash_ret = hold * 0.06 / 365 * 100  # 6% annual
                result.append({**t, 'hold_days': hold,
                                'reentry_date': next_t['date'],
                                'reentry_price': next_t['vnindex'],
                                'cash_gain_pct': cash_ret})
            else:  # still in cash
                hold = (current_date - t['date']).days
                cash_ret = hold * 0.06 / 365 * 100
                result.append({**t, 'hold_days': hold,
                                'reentry_date': None,
                                'cash_gain_pct': cash_ret,
                                'note': 'DANG CASH'})
    return result

current_date = pd.Timestamp('2026-04-17')

# ─── SYSTEM A: MA200 ───
print("=" * 80)
print("HE THONG A: MA200 CROSS")
print("=" * 80)
trades_a, still_in_a = get_trades_ma200(df)
print(f"\nTong so tin hieu: {len(trades_a)} | Hien tai: {'TRONG TT' if still_in_a else 'CASH'}")

pairs_a = []
i = 0
while i < len(trades_a):
    t = trades_a[i]
    if t['action'] == 'BUY':
        entry_date  = t['date']
        entry_price = t['vnindex']
        entry_ma200 = t['ma200']
        # Find next SELL
        if i+1 < len(trades_a) and trades_a[i+1]['action'] == 'SELL':
            s = trades_a[i+1]
            exit_date  = s['date']
            exit_price = s['vnindex']
            hold = (exit_date - entry_date).days
            ret  = (exit_price - entry_price) / entry_price * 100
            pairs_a.append((entry_date, entry_price, exit_date, exit_price, hold, ret, 'CLOSED'))
            i += 2
        else:
            hold = (current_date - entry_date).days
            ret  = (df['Close'].iloc[-1] - entry_price) / entry_price * 100
            pairs_a.append((entry_date, entry_price, current_date, df['Close'].iloc[-1], hold, ret, 'OPEN'))
            i += 1
    else:
        i += 1

print(f"\n{'No':>3} {'MUA vao':>11} {'VNI vao':>8} {'BAN ra':>11} {'VNI ra':>8} {'Ngay':>5} {'Return':>8} {'Status':>7}")
print("-" * 75)
for idx, (ed, ep, xd, xp, h, r, st) in enumerate(pairs_a, 1):
    marker = " ←DANG HOLD" if st == 'OPEN' else ""
    print(f"{idx:>3} {ed.strftime('%Y-%m-%d'):>11} {ep:>8.0f} {xd.strftime('%Y-%m-%d'):>11} {xp:>8.0f} {h:>5d} {r:>+7.1f}% {st:>7}{marker}")

wins_a = [r for (_,_,_,_,_,r,s) in pairs_a if r > 0]
loss_a = [r for (_,_,_,_,_,r,s) in pairs_a if r <= 0]
print(f"\nWin: {len(wins_a)} lan | Loss: {len(loss_a)} lan | Winrate: {len(wins_a)/(len(wins_a)+len(loss_a))*100:.1f}%")
if wins_a: print(f"Trung binh win: {np.mean(wins_a):+.1f}% | Max win: {max(wins_a):+.1f}%")
if loss_a: print(f"Trung binh loss: {np.mean(loss_a):+.1f}% | Max loss: {min(loss_a):+.1f}%")

# ─── SYSTEM B: 5-STATE MACHINE ───
print("\n\n" + "=" * 80)
print("HE THONG B: 5-STATE MACHINE (Optimal: PE P80=17.0x, RSI sell=0.70, bear=0.40, panic=0.32)")
print("=" * 80)
trades_b, still_in_b = get_trades_5state(df)
print(f"\nTong so tin hieu: {len(trades_b)} | Hien tai: {'TRONG TT' if still_in_b else 'CASH'}")

pairs_b = []
i = 0
while i < len(trades_b):
    t = trades_b[i]
    if t['action'] == 'BUY':
        entry_date  = t['date']
        entry_price = t['vnindex']
        entry_state = t['state']
        entry_rsi   = t['rsi']
        entry_pe    = t['pe']
        entry_rsn   = t['reason']
        if i+1 < len(trades_b) and trades_b[i+1]['action'] == 'SELL':
            s = trades_b[i+1]
            exit_date  = s['date']
            exit_price = s['vnindex']
            exit_state = s['state']
            exit_rsn   = s['reason']
            hold = (exit_date - entry_date).days
            ret  = (exit_price - entry_price) / entry_price * 100
            pairs_b.append((entry_date, entry_price, entry_state, entry_rsn,
                            exit_date, exit_price, exit_state, exit_rsn, hold, ret, 'CLOSED'))
            i += 2
        else:
            hold = (current_date - entry_date).days
            ret  = (df['Close'].iloc[-1] - entry_price) / entry_price * 100
            pairs_b.append((entry_date, entry_price, entry_state, entry_rsn,
                            current_date, df['Close'].iloc[-1], 'OPEN', 'Still in market',
                            hold, ret, 'OPEN'))
            i += 1
    else:
        i += 1

print(f"\n{'No':>3} {'MUA vao':>11} {'VNI':>6} {'State':>8} {'BAN ra':>11} {'VNI':>6} {'State':>9} {'Ngay':>5} {'Return':>8}")
print("-" * 85)
for idx, (ed, ep, es, er, xd, xp, xs, xr, h, r, st) in enumerate(pairs_b, 1):
    marker = " ←HOLD" if st == 'OPEN' else ""
    print(f"{idx:>3} {ed.strftime('%Y-%m-%d'):>11} {ep:>6.0f} {es:>8} {xd.strftime('%Y-%m-%d'):>11} {xp:>6.0f} {xs:>9} {h:>5d} {r:>+7.1f}%{marker}")

print("\n--- Chi tiet ly do vao/ra ---")
for idx, (ed, ep, es, er, xd, xp, xs, xr, h, r, st) in enumerate(pairs_b, 1):
    print(f"\n  [{idx}] MUA {ed.strftime('%Y-%m-%d')} @ {ep:.0f}: {er}")
    if st == 'CLOSED':
        print(f"       BAN {xd.strftime('%Y-%m-%d')} @ {xp:.0f}: {xr}")
        print(f"       Ket qua: {h} ngay, {r:+.1f}%")
    else:
        print(f"       Dang nắm giu tu {h} ngay, loi: {r:+.1f}% (tinh den 2026-04-17)")

wins_b = [r for (*_, r, s) in pairs_b if r > 0]
loss_b = [r for (*_, r, s) in pairs_b if r <= 0]
print(f"\nWin: {len(wins_b)} lan | Loss: {len(loss_b)} lan | Winrate: {len(wins_b)/(len(wins_b)+len(loss_b))*100:.1f}%")
if wins_b: print(f"Trung binh win: {np.mean(wins_b):+.1f}% | Max win: {max(wins_b):+.1f}%")
if loss_b: print(f"Trung binh loss: {np.mean(loss_b):+.1f}% | Max loss: {min(loss_b):+.1f}%")

# ─── SYSTEM C: MACD (tham khảo) ───
print("\n\n" + "=" * 80)
print("HE THONG C: MACD TREND (THAM KHAO - nhieu tin hieu nhat)")
print("=" * 80)
trades_c, still_in_c = get_trades_macd(df)
print(f"\nTong so tin hieu: {len(trades_c)} | Hien tai: {'TRONG TT' if still_in_c else 'CASH'}")

pairs_c = []
i = 0
while i < len(trades_c):
    t = trades_c[i]
    if t['action'] == 'BUY':
        entry_date  = t['date']
        entry_price = t['vnindex']
        if i+1 < len(trades_c) and trades_c[i+1]['action'] == 'SELL':
            s = trades_c[i+1]
            hold = (s['date'] - entry_date).days
            ret  = (s['vnindex'] - entry_price) / entry_price * 100
            pairs_c.append((entry_date, entry_price, s['date'], s['vnindex'], hold, ret, 'CLOSED'))
            i += 2
        else:
            hold = (current_date - entry_date).days
            ret  = (df['Close'].iloc[-1] - entry_price) / entry_price * 100
            pairs_c.append((entry_date, entry_price, current_date, df['Close'].iloc[-1], hold, ret, 'OPEN'))
            i += 1
    else:
        i += 1

print(f"\n{'No':>3} {'MUA vao':>11} {'VNI vao':>8} {'BAN ra':>11} {'VNI ra':>8} {'Ngay':>5} {'Return':>8}")
print("-" * 70)
for idx, (ed, ep, xd, xp, h, r, st) in enumerate(pairs_c, 1):
    marker = " ←HOLD" if st == 'OPEN' else ""
    print(f"{idx:>3} {ed.strftime('%Y-%m-%d'):>11} {ep:>8.0f} {xd.strftime('%Y-%m-%d'):>11} {xp:>8.0f} {h:>5d} {r:>+7.1f}%{marker}")

wins_c = [r for (*_, r, s) in pairs_c if r > 0]
loss_c = [r for (*_, r, s) in pairs_c if r <= 0]
print(f"\nWin: {len(wins_c)} lan | Loss: {len(loss_c)} lan | Winrate: {len(wins_c)/(len(wins_c)+len(loss_c))*100:.1f}%")
if wins_c: print(f"Trung binh win: {np.mean(wins_c):+.1f}% | Max win: {max(wins_c):+.1f}%")
if loss_c: print(f"Trung binh loss: {np.mean(loss_c):+.1f}% | Max loss: {min(loss_c):+.1f}%")

# ─── SO SANH TONG HOP ───
print("\n\n" + "=" * 80)
print("TONG HOP SO SANH 3 HE THONG")
print("=" * 80)
print(f"\n{'':30} {'MA200':>10} {'5-State':>10} {'MACD':>10}")
print(f"  So cap giao dich:{'':10} {len(pairs_a):>10} {len(pairs_b):>10} {len(pairs_c):>10}")

all_rets_a = [r for (*_, r, s) in pairs_a]
all_rets_b = [r for (*_, r, s) in pairs_b]
all_rets_c = [r for (*_, r, s) in pairs_c]

wr_a = len(wins_a)/(len(wins_a)+len(loss_a))*100 if (wins_a or loss_a) else 0
wr_b = len(wins_b)/(len(wins_b)+len(loss_b))*100 if (wins_b or loss_b) else 0
wr_c = len(wins_c)/(len(wins_c)+len(loss_c))*100 if (wins_c or loss_c) else 0

print(f"  Winrate:{'':22} {wr_a:>9.1f}% {wr_b:>9.1f}% {wr_c:>9.1f}%")
print(f"  Median return/gd:{'':13} {np.median(all_rets_a):>+9.1f}% {np.median(all_rets_b):>+9.1f}% {np.median(all_rets_c):>+9.1f}%")
print(f"  Max loss:{'':21} {min(all_rets_a):>+9.1f}% {min(all_rets_b):>+9.1f}% {min(all_rets_c):>+9.1f}%")

# Save
rows = []
for idx, (ed, ep, xd, xp, h, r, st) in enumerate(pairs_a, 1):
    rows.append({'system': 'MA200', 'trade_no': idx, 'entry_date': ed, 'entry_vnindex': ep,
                 'exit_date': xd, 'exit_vnindex': xp, 'hold_days': h, 'return_pct': r, 'status': st})
for idx, (ed, ep, es, er, xd, xp, xs, xr, h, r, st) in enumerate(pairs_b, 1):
    rows.append({'system': '5State', 'trade_no': idx, 'entry_date': ed, 'entry_vnindex': ep,
                 'entry_reason': er, 'exit_date': xd, 'exit_vnindex': xp, 'exit_reason': xr,
                 'hold_days': h, 'return_pct': r, 'status': st})
for idx, (ed, ep, xd, xp, h, r, st) in enumerate(pairs_c, 1):
    rows.append({'system': 'MACD', 'trade_no': idx, 'entry_date': ed, 'entry_vnindex': ep,
                 'exit_date': xd, 'exit_vnindex': xp, 'hold_days': h, 'return_pct': r, 'status': st})

pd.DataFrame(rows).to_csv(
    r"/home/trido/thanhdt/WorkingClaude/market_entry_exit_list.csv",
    index=False, encoding='utf-8-sig'
)
print("\nDa luu ra market_entry_exit_list.csv")
