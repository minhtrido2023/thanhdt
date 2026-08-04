#!/usr/bin/env python
"""TWAP (trai deu 15' blocks) vs gom-1-cua-so — do tren intraday 15-min bars.

Nguon: data/intraday_full.pkl (RESEARCH static, 335 ma, 2023-09-11 -> 2026-05-12,
bar 15 phut). Registry: mike/kb/data_registry/research-caches/static_panels.md

Do CAI GI (thanh that):
  - Timing dispersion: |gia thuc thi - benchmark ngay| cua tung lich thuc thi.
  - Bias trung binh theo tung khung gio (16 khung -> khai multiple testing).
  - Ho so thanh khoan theo khung gio (equal-time TWAP co lech pha voi duong cong U?).
KHONG do duoc: market impact cua CHINH lenh minh (bars la lich su khong co lenh ta).

N = so PHIEN (su kien doc lap), khong phai so dong ticker-day (cross-section tuong quan cao).
"""
import sys, json, math, collections
import pandas as pd, numpy as np

PKL = '/home/trido/thanhdt/WorkingClaude/data/intraday_full.pkl'
# Ma da giao dich that (tu dnse_raw place_order, 2026-06-12 -> 2026-07-31)
TRADED = ['CTG','VPB','MBB','BID','VIB','HDB','TPB','DCM','VGC','SIP','NCT','LPB','SAB',
          'VHC','PVT','TV1','TCB','HPG','FPT','VCB','TCM','VHM','SHB','MSB','MBS','SHS',
          'VNM','ACB','VIX','VND','HAH','MSH','TLG','CSV']
GRID = ['09:15','09:30','09:45','10:00','10:15','10:30','10:45','11:00','11:15',
        '13:00','13:15','13:30','13:45','14:00','14:15','14:30','14:45']
CORE = GRID[:-1]           # bo ATC 14:45 (khop dinh ky, khac ban chat)
MIN_BARS = 15              # ngay du lieu day du

def load():
    d = pd.read_pickle(PKL)
    out = {}
    for t in TRADED:
        if t in d:
            v = d[t].copy()
            v['typ'] = (v.high + v.low + v.close) / 3.0
            v['hm'] = v.time.dt.strftime('%H:%M')
            v['day'] = v.time.dt.date
            out[t] = v
    return out


def per_day_rows(data):
    rows = []
    for t, v in data.items():
        for day, g in v.groupby('day'):
            g = g[g.hm.isin(CORE)]
            if len(g) < MIN_BARS:
                continue
            vol = g.volume.values.astype(float)
            typ = g.typ.values.astype(float)
            if vol.sum() <= 0 or not np.isfinite(typ).all():
                continue
            bench = float((typ * vol).sum() / vol.sum())      # day VWAP = benchmark
            if bench <= 0:
                continue
            r = {'ticker': t, 'day': day, 'vwap': bench,
                 'twap': float(typ.mean()), 'nbar': len(g),
                 'dayval_vnd': float((typ * vol).sum()) * 1000.0}  # gia don vi nghin VND
            m = dict(zip(g.hm.values, typ))
            for k in CORE:
                r['px_' + k] = m.get(k, np.nan)
            vm = dict(zip(g.hm.values, vol))
            tot = vol.sum()
            for k in CORE:
                r['vs_' + k] = vm.get(k, np.nan) / tot
            rows.append(r)
    return pd.DataFrame(rows)


def bps(x, b):
    return (x / b - 1.0) * 1e4


def tstat(x):
    x = np.asarray([v for v in x if np.isfinite(v)])
    if len(x) < 3:
        return float('nan'), float('nan'), 0
    return float(x.mean()), float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))), len(x)


def main():
    data = load()
    df = per_day_rows(data)
    print(f'# ma co intraday: {len(data)}/{len(TRADED)} da giao dich that')
    print(f'# ticker-day: {len(df)} | # PHIEN doc lap: {df.day.nunique()} '
          f'| {df.day.min()} -> {df.day.max()}')

    # --- 1. Bias + dispersion tung khung gio, so voi day-VWAP -------------
    print('\n## 1. Sai lech gia thuc thi vs day-VWAP (bps). Duong = MUA dat / BAN duoc gia.')
    print(f'{"khung":>7} {"mean_bps":>9} {"t":>7} {"sd_ngay":>8} {"MAD":>7}')
    daily = {}
    for k in CORE:
        e = bps(df['px_' + k], df.vwap)
        d = pd.DataFrame({'day': df.day, 'e': e}).dropna().groupby('day').e.mean()
        daily[k] = d
        m, t, n = tstat(d.values)
        print(f'{k:>7} {m:9.2f} {t:7.2f} {d.std(ddof=1):8.1f} {d.abs().mean():7.1f}')

    e_tw = bps(df.twap, df.vwap)
    d_tw = pd.DataFrame({'day': df.day, 'e': e_tw}).dropna().groupby('day').e.mean()
    daily['TWAP'] = d_tw
    m, t, n = tstat(d_tw.values)
    print(f'{"TWAP16":>7} {m:9.2f} {t:7.2f} {d_tw.std(ddof=1):8.1f} {d_tw.abs().mean():7.1f}   <-- trai deu')

    # --- 2. So khop cap: cua so hien tai vs TWAP -------------------------
    print('\n## 2. Cap khop theo PHIEN — cua so hien tai vs TWAP (bps, duong = cua so DAT hon TWAP)')
    for label, k, sign in [('BUY @11:15', '11:15', +1), ('SELL @09:15 (mo cua)', '09:15', -1)]:
        a = daily[k].reindex(d_tw.index)
        diff = (a - d_tw).dropna()
        m, t, n = tstat(diff.values)
        adv = m * sign   # sign=+1: mua dat hon = xau; sign=-1: ban thap hon = xau
        print(f'{label:>22}: diff={m:+.2f} bps  t={t:+.2f}  N_phien={n}  '
              f'=> {"BAT LOI" if adv>0 else "co loi"} {abs(adv):.2f} bps cho phia nay')

    # --- 3. Rui ro timing: phan tan (cai TWAP thuc su mua duoc) ----------
    print('\n## 3. Rui ro timing (do phan tan quanh benchmark) — chi so chinh')
    for k in ['09:15', '11:15', 'TWAP']:
        d = daily[k]
        print(f'{k:>7}: sd={d.std(ddof=1):6.1f} bps | MAD={d.abs().mean():5.1f} | '
              f'p05={d.quantile(.05):7.1f} | p95={d.quantile(.95):6.1f} | '
              f'worst={d.abs().max():6.1f}')
    r = daily['11:15'].std(ddof=1) / d_tw.std(ddof=1)
    print(f'  -> sd(BUY@11:15) / sd(TWAP) = {r:.2f}x')
    r2 = daily['09:15'].std(ddof=1) / d_tw.std(ddof=1)
    print(f'  -> sd(SELL@09:15) / sd(TWAP) = {r2:.2f}x')

    # --- 4. Ho so thanh khoan theo khung gio -----------------------------
    print('\n## 4. Ty trong KHOI LUONG theo khung gio (equal-time TWAP dat 1/16=6.25% moi block)')
    print(f'{"khung":>7} {"%vol":>7} {"lech vs 6.25%":>14}')
    eq = 100.0 / len(CORE)
    prof = {}
    for k in CORE:
        s = df['vs_' + k].mean() * 100
        prof[k] = s
        print(f'{k:>7} {s:7.2f} {s-eq:+14.2f}')
    print(f'  tong = {sum(prof.values()):.1f}%')

    # --- 5. Participation cho lenh that ----------------------------------
    print('\n## 5. %participation thuc te (gia tri lenh that / gia tri khop trong block)')
    med_dayval = df.groupby('ticker').dayval_vnd.median()
    for name, val in [('median 24.5tr', 24_545_000), ('p90 227tr', 226_875_000),
                      ('max 3.21ty', 3_210_570_000)]:
        # gom 1 cua so: toan bo lenh vao 1 block (~6.25% ADV ngay); TWAP: chia 16
        adv = med_dayval.median()
        p_win = val / (adv * (prof['11:15'] / 100)) * 100
        p_twap = (val / len(CORE)) / (adv * (min(prof.values()) / 100)) * 100
        print(f'  {name:>14}: gom-1-block = {p_win:6.2f}% khoi luong block | '
              f'TWAP (block mong nhat) = {p_twap:6.2f}%')
    print(f'  (ADV trung vi ro giao dich = {med_dayval.median()/1e9:.2f} ty VND/ngay)')

    df.to_csv('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_twap_20260804/'
              'per_day_exp.csv', index=False)
    print('\nOK -> per_day_exp.csv')


if __name__ == '__main__':
    main()
