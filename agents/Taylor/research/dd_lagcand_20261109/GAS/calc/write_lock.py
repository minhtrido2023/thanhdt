"""Ghi LOCK_prerun.txt (md5 dau vao + gia dinh) truoc lan chay chinh thuc model.py."""
import datetime, hashlib, os, sys
from zoneinfo import ZoneInfo
H = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(H, 'LOCK_prerun.txt')
if os.path.exists(out): sys.exit('LOCK da ton tai')
F = ['assumptions.json', 'model.py', 'write_lock.py', 'notes_bctc.md', 'bq_fin_gas.csv', 'np_hist_gas.csv', 'brent_y.csv', 'brent_q.csv', 'px_daily.sql', 'px_gas_daily_20261106.csv', '../src/GAS_Q3_2026_HN_VN.pdf', '../src/GAS_H1_2026_HN_soatxet.pdf']
ts = datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(timespec='seconds')
rows = [f'# LOCK pre-run GAS — {ts} (job Taylor_20261109_073604)',
        '# Minh bach: da chay thu 2 ban nhap truoc LOCK (v1 hoi quy quy — bi loai vi ngoai suy vo ly; v2 hoi quy nam chua co truc phan du). Gia 74.100 biet tu brief truoc moi tinh toan.']
rows += [f'{hashlib.md5(open(os.path.join(H, f), "rb").read()).hexdigest()}  {f}' for f in F]
open(out, 'w').write('\n'.join(rows) + '\n'); print('\n'.join(rows))
