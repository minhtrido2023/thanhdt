"""Pillar C probe: does market-wide liquidity contraction predict forward VNINDEX drawdown,
incrementally over what DT5G (price-based) already knows?  RESEARCH ONLY, no production write.
N-budget declared upfront: 2 liquidity definitions x 3 thresholds = 6 trials.
"""
import glob, duckdb, numpy as np, pandas as pd

files = sorted(glob.glob('data/bq_cache/ticker_prune/*.parquet'))
turn = duckdb.sql(f"""
  select time, sum(Volume*Price) as tv, count(*) as n
  from read_parquet({files!r}) where Volume is not null and Price is not null
  group by time order by time
""").df()
turn['time'] = pd.to_datetime(turn['time'])
vni = duckdb.sql(f"""
  select distinct time, VNINDEX from read_parquet({files!r}) where VNINDEX is not null
""").df()
vni['time'] = pd.to_datetime(vni['time'])
vni = vni.groupby('time', as_index=False)['VNINDEX'].median()

st = pd.read_parquet('data/bq_cache/vnindex_5state_dt5g_live.parquet')
st['time'] = pd.to_datetime(st['time'] if 'time' in st else st['date'])
st = st[['time', 'state']]

df = turn.merge(vni, on='time').merge(st, on='time', how='left').sort_values('time').reset_index(drop=True)
df = df[df.time >= '2013-06-01'].reset_index(drop=True)

# causal liquidity features (use only info up to t)
df['liq_ratio'] = df.tv.rolling(20).mean() / df.tv.rolling(250).mean()
lg = np.log(df.tv.rolling(5).mean())
df['liq_z'] = (lg - lg.rolling(250).mean()) / lg.rolling(250).std()

# forward 60-session max drawdown of VNINDEX (target, look-ahead by construction = OK for a predictor study)
H = 60
v = df.VNINDEX.values
fdd = np.full(len(v), np.nan)
for i in range(len(v) - H):
    w = v[i:i + H + 1]
    fdd[i] = (np.minimum.accumulate(w[::-1])[::-1].min() / w[0]) - 1  # min over window / today
    fdd[i] = w.min() / w[0] - 1
df['fwd_dd60'] = fdd
df['fwd_ret60'] = pd.Series(v).shift(-H) / pd.Series(v) - 1

d = df.dropna(subset=['liq_ratio', 'liq_z', 'fwd_dd60']).copy()
IS = d[d.time < '2020-01-01']; OOS = d[d.time >= '2020-01-01']

def rep(name, mask_fn, thr_list):
    for thr in thr_list:
        row = [f"{name}<{thr}"]
        for lbl, sub in (('ALL', d), ('IS', IS), ('OOS', OOS)):
            m = mask_fn(sub, thr)
            if m.sum() < 30:
                row.append(f"{lbl}: n={m.sum()} (thin)"); continue
            row.append(f"{lbl}: n={m.sum():4d} dd={sub.fwd_dd60[m].mean()*100:6.2f}% vs base {sub.fwd_dd60.mean()*100:6.2f}% | r60={sub.fwd_ret60[m].mean()*100:6.2f}% vs {sub.fwd_ret60.mean()*100:6.2f}%")
        print(" || ".join(row))

print("=== A. unconditional: low liquidity -> worse forward 60d DD? ===")
rep('liq_ratio', lambda s, t: s.liq_ratio < t, [0.70, 0.80, 0.90])
rep('liq_z', lambda s, t: s.liq_z < t, [-1.5, -1.0, -0.5])

print("\n=== B. INCREMENTAL over DT5G: restricted to non-defensive states (NEUTRAL/BULL/EXBULL, state>=3) ===")
dN = d[d.state >= 3]
ISN = dN[dN.time < '2020-01-01']; OOSN = dN[dN.time >= '2020-01-01']
def rep2(name, col, thr_list, lower=True):
    for thr in thr_list:
        row = [f"{name}{'<' if lower else '>'}{thr}"]
        for lbl, sub in (('ALL', dN), ('IS', ISN), ('OOS', OOSN)):
            m = (sub[col] < thr) if lower else (sub[col] > thr)
            if m.sum() < 30:
                row.append(f"{lbl}: n={m.sum()} thin"); continue
            row.append(f"{lbl}: n={m.sum():4d} dd={sub.fwd_dd60[m].mean()*100:6.2f}% vs {sub.fwd_dd60.mean()*100:6.2f}% | r60={sub.fwd_ret60[m].mean()*100:6.2f}% vs {sub.fwd_ret60.mean()*100:6.2f}%")
        print(" || ".join(row))
rep2('liq_ratio', 'liq_ratio', [0.70, 0.80, 0.90])
rep2('liq_z', 'liq_z', [-1.5, -1.0, -0.5])

print("\n=== C. today ===")
last = df.dropna(subset=['liq_ratio']).iloc[-1]
print(f"{last.time.date()}  tv_20d/250d={last.liq_ratio:.3f}  liq_z={last.liq_z:.2f}  state={last.state}  n_names={int(last.n)}")
print(df.dropna(subset=['liq_ratio']).tail(5)[['time','liq_ratio','liq_z','state']].to_string(index=False))
pct = (d.liq_ratio < last.liq_ratio).mean()
print(f"current liq_ratio percentile in 2013+ history: {pct*100:.1f}%")
