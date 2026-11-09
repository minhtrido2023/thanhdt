"""Ghi LOCK_r3_prerun.txt TRUOC khi chay model_r3.py (md5 file upstream + timestamp ICT). Khong chay model."""
import datetime, hashlib, os, sys
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); WC = '/home/trido/thanhdt/WorkingClaude'
out = os.path.join(HERE, 'LOCK_r3_prerun.txt')
if os.path.exists(out): sys.exit('LOCK da ton tai — khong ghi de')
F = [os.path.join(HERE, x) for x in ('assumptions_r3.json', 'model_r3.py', 'write_lock_prerun.py', 'px_fpt_r3.sql', 'px_fpt_r3_20261106.csv')] + \
    [os.path.join(ROOT, 'FPT', 'calc', x) for x in ('fpt_r2.py', 'fpt_redo.py', 'assoc_px_20261104.csv', 'fpt_r2_out.txt', 'LOCK_r2_outputs_md5.txt')] + \
    [os.path.join(ROOT, 'FPT', x) for x in ('SUMMARY.json', 'ADDENDUM_5F.md', 'SUMMARY_5F.json', 'REPORT_r2.md')] + \
    [os.path.join(ROOT, '_common_014125', x) for x in ('r2common.py', 'common.py', 'bq_px_liq_20261104.csv')] + \
    [os.path.join(ROOT, '_shared', 'wpct.py'), os.path.join(WC, 'deposit_rate_vn.py'), os.path.join(WC, 'cctg_rate_vn.py'),
     os.path.join(WC, 'data/deposit_rate_vn_events.csv'), os.path.join(WC, 'data/cctg_rate_vn_events.csv'),
     os.path.join(WC, 'mike/agents/Taylor/research/dd_FPT_20261101/calc/notes_q3_bctc.md'),
     os.path.join(ROOT, 'TOP5D_CORRECTIONS_20261108.md'), os.path.join(ROOT, 'STANDARD_r2.md')]
ts = datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(timespec='seconds')
rows = [f"# LOCK r3 pre-run FPT — ghi {ts} TRUOC lan chay dau model_r3.py (job Taylor_20261108_180128)",
        "# Minh bach: gia 50.800 (06/11) da biet tu TOP5D_CORRECTIONS + truy van BQ truoc LOCK; gia dinh chot trong assumptions_r3.json."]
rows += [f"{hashlib.md5(open(f, 'rb').read()).hexdigest()}  {os.path.relpath(f, ROOT) if f.startswith(ROOT) else f}" for f in F]
open(out, 'w').write('\n'.join(rows) + '\n'); print('\n'.join(rows))
