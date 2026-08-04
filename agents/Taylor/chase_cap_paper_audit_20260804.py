import csv, glob, json, os, sys
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
import pandas as pd, pyarrow.parquet as pq
from trading_bot.vn_market import round_price, tick_size

STATIC = 0.015; K = 2.0; CEIL = 0.04
cache_dir = os.environ.get("BQ_LOCAL_CACHE", "data/bq_cache")
chunks = sorted(glob.glob(os.path.join(cache_dir, "ticker_prune", "*.parquet")))
print("chunks:", len(chunks), "dir:", cache_dir)
tab = pq.read_table(chunks, columns=["time","ticker","Close"]).to_pandas(ignore_metadata=True)
tab["time"] = pd.to_datetime(tab["time"])
tab = tab[tab["ticker"].isin({"ACB","FPT","HDB","HPG","MBB","VNM"})].sort_values("time")

def rvol_for(tk, plan_date):
    d = tab[(tab.ticker==tk) & (tab.time < pd.Timestamp(plan_date))].tail(22)
    if len(d) < 2: return None
    rets = d["Close"].pct_change().dropna()
    if len(rets) < 5: return None
    r = float(rets.tail(20).std())
    return r if r > 0 else None

rows_out = []
for f in sorted(glob.glob('data/execution_logs/exec_main_*_journal.csv')):
    date = os.path.basename(f).split('_')[2]
    plan_p = f'data/trade_plans/plan_main_{date}.json'
    if not os.path.exists(plan_p): continue
    plan = json.load(open(plan_p))
    ref = {o['id']: o for o in plan['orders']}
    for r in csv.DictReader(open(f)):
        if r['event'] != 'PLACE' or r['side'] != 'buy': continue
        o = ref.get(r['parent_id'])
        if not o: 
            print("  !! no plan order for", date, r['parent_id']); continue
        rp = float(o['ref_price']); px = float(r['price'])
        rv = rvol_for(r['ticker'], date)
        volcap = min(max(K*rv, STATIC), CEIL) if rv else STATIC
        cap_static = rp*(1+STATIC); cap_vol = rp*(1+volcap)
        px_static = round_price(cap_static, r['ticker'], 'HOSE', 'down')
        px_vol = round_price(cap_vol, r['ticker'], 'HOSE', 'down')
        rows_out.append(dict(date=date, tk=r['ticker'], ref=rp, px=px, rvol=rv,
            volcap=volcap, widened=volcap>STATIC+1e-12,
            cap_static_px=px_static, cap_vol_px=px_vol,
            binds_static = px > px_static + 1e-9,
            chase_pct=(px/rp-1)))
print(f"{'date':11} {'tk':4} {'ref':>9} {'px':>9} {'chase%':>7} {'rvol%':>6} {'volcap%':>7} {'widened':>7} {'>staticcap':>10}")
for x in rows_out:
    print(f"{x['date']:11} {x['tk']:4} {x['ref']:9.0f} {x['px']:9.0f} {x['chase_pct']*100:7.2f} "
          f"{(x['rvol']*100 if x['rvol'] else float('nan')):6.2f} {x['volcap']*100:7.2f} "
          f"{str(x['widened']):>7} {str(x['binds_static']):>10}")
n=len(rows_out)
print("\nTOTAL buy placements:", n)
print("sessions:", len(set(x['date'] for x in rows_out)))
print("widened-armed (volcap>static):", sum(x['widened'] for x in rows_out))
print("rvol missing (fail-safe to static):", sum(1 for x in rows_out if x['rvol'] is None))
print("price ABOVE static cap (vol-cap actually bound/interfered):", sum(x['binds_static'] for x in rows_out))
print("price AT vol cap (cap binding at all):", sum(1 for x in rows_out if abs(x['px']-x['cap_vol_px'])<1e-9))
print("max chase% observed:", max(x['chase_pct'] for x in rows_out)*100)
