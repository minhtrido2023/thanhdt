import hashlib, os, sys, datetime, zoneinfo
H = os.path.dirname(os.path.abspath(__file__)); tag = sys.argv[1]
fs = ['assumptions.json', 'model.py', 'notes_read.md', 'bq_msb_px.csv', 'bq_peers_20261106.csv', 'bq_msb_fin.csv'] + (['model_out.txt', 'model_out.json', 'bank_metrics.py', 'bank_metrics_out.txt', 'peers_xcheck.py', 'peers_xcheck_out.txt'] if tag == 'post' else [])
with open(os.path.join(H, f'LOCK_{tag}.txt'), 'w') as f:
    f.write(f"# {tag} {datetime.datetime.now(zoneinfo.ZoneInfo('Asia/Ho_Chi_Minh')).isoformat()}\n")
    for x in fs: f.write(f"{hashlib.md5(open(os.path.join(H, x),'rb').read()).hexdigest()}  {x}\n")
print(open(os.path.join(H, f'LOCK_{tag}.txt')).read())
