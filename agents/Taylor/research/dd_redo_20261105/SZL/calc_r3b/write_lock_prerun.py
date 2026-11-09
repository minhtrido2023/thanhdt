"""Ghi LOCK_r3b_prerun.txt TRUOC khi chay model_r3b.py (md5 moi file upstream + timestamp ICT). Khong chay model."""
import datetime, hashlib, os, sys
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
out = os.path.join(HERE, 'LOCK_r3b_prerun.txt')
if os.path.exists(out):
    sys.exit('LOCK da ton tai — khong ghi de')
F = [os.path.join(HERE, x) for x in ('assumptions_r3b.json', 'model_r3b.py', 'write_lock_prerun.py')] + \
    [os.path.join(ROOT, 'SZL', 'calc_r3', x) for x in ('assumptions_r3.json', 'model_r3.py', 'px_szl_r3_20261106.csv', 'snz_holdco_20261106.csv', 'szl_cf_hist.csv', 'LOCK_md5.txt', 'model_r3_out.txt')] + \
    [os.path.join(ROOT, 'SZL', 'calc', 'bq_oshares_szc_szb.csv'), os.path.join(ROOT, 'SZL', 'src', 'Q3_2026_hopnhat.pdf'), os.path.join(ROOT, 'SZL', 'SUMMARY.json'),
     os.path.join(ROOT, '_shared', 'wpct.py'), '/home/trido/thanhdt/WorkingClaude/deposit_rate_vn.py', '/home/trido/thanhdt/WorkingClaude/data/deposit_rate_vn_events.csv',
     os.path.join(ROOT, 'TOP5C_CORRECTIONS_20261108.md'), os.path.join(ROOT, 'STANDARD_r2.md')]
ts = datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(timespec='seconds')
rows = [f"# LOCK r3b pre-run — ghi {ts} TRUOC lan chay dau model_r3b.py (job Taylor_20261108_175123)",
        "# Luu y minh bach: gia 27.700 (06/11) da biet tu r3; file gia giu nguyen r3, KHONG truy van lai."]
rows += [f"{hashlib.md5(open(f, 'rb').read()).hexdigest()}  {os.path.relpath(f, ROOT) if f.startswith(ROOT) else f}" for f in F]
open(out, 'w').write('\n'.join(rows) + '\n'); print('\n'.join(rows))
