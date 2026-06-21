"""
SBV Macro Overlay paper-trade tracker.

Modes:
  update  — append daily decision + cumulative ghost-alpha
  report  — generate 12-month verdict
  backfill — bootstrap from historical data (one-time)
"""
import argparse
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd

WORKDIR = Path(__file__).parent
TRACKER_PATH = WORKDIR / 'sbv_macro_tracker.csv'
REPORT_PATH  = WORKDIR / 'sbv_macro_report.txt'
DEPLOY_DATE  = date(2026, 5, 19)
REPORT_DATE  = date(2027, 5, 19)

# Realistic alpha estimates (from sensitivity test)
# Lift effect ~ 0.25 × VNI return when LOOSE active
# Cut effect ~ -0.30 × VNI return when TIGHT active
LIFT_LOOSE = 0.25
CUT_TIGHT  = -0.30


def cmd_update():
    from sbv_macro_overlay import compute_signal_today, update_state, log_decision, stale_check
    import yfinance as yf

    # C-option: stale-event warning
    warn = stale_check(threshold_days=180)
    if warn:
        print(f"\n[WARNING] {warn['message']}\n")

    info = compute_signal_today()
    if info is None:
        print('No data available'); return
    decision = update_state(info)
    log_decision(info, decision)

    # Compute today's VNI return
    h = yf.Ticker('DX-Y.NYB').history(period='5d')  # just for date
    # Actually we need VNI — use BQ
    res = subprocess.run(['bq','query','--use_legacy_sql=false',
                          '--project_id=lithe-record-440915-m9','--format=csv','--max_rows=10','-q',
                          'SELECT t.time, t.Close FROM tav2_bq.ticker AS t '
                          'WHERE t.ticker="VNINDEX" ORDER BY t.time DESC LIMIT 2'],
                         capture_output=True, text=True, shell=True)
    vni_rows = res.stdout.strip().split('\n')[1:]
    if len(vni_rows) >= 2:
        cl_today = float(vni_rows[0].split(',')[1])
        cl_prev  = float(vni_rows[1].split(',')[1])
        vni_ret  = cl_today/cl_prev - 1
    else:
        cl_today = None; vni_ret = None

    # Accumulate ghost alpha
    cum_alpha = 0.0
    if TRACKER_PATH.exists():
        prev = pd.read_csv(TRACKER_PATH)
        if not prev.empty:
            cum_alpha = float(prev.iloc[-1].get('cum_alpha_pct', 0))

    daily_alpha = 0.0
    if vni_ret is not None and decision['regime'] != 'NORMAL':
        if decision['regime'] == 'LOOSE':
            daily_alpha = LIFT_LOOSE * vni_ret * 100
        elif decision['regime'] == 'TIGHT':
            daily_alpha = CUT_TIGHT * vni_ret * 100
    cum_alpha += daily_alpha

    row = {
        'date': info['date'], 'refi_rate': info['refi_rate'],
        'macro_score': round(info['macro_score'], 4),
        'z_refi': round(info['z_refi'], 4), 'z_dxy': round(info['z_dxy'], 4),
        'dxy_rank252': round(info['dxy_rank252'], 4),
        'regime': decision['regime'], 'max_positions': decision['max_positions'],
        'vni_close': cl_today, 'vni_ret_d': vni_ret if vni_ret else '',
        'daily_alpha_pct': round(daily_alpha, 4),
        'cum_alpha_pct': round(cum_alpha, 4),
        'reason': decision['reason'].replace(',',';'),
    }
    write_header = not TRACKER_PATH.exists()
    with TRACKER_PATH.open('a', encoding='utf-8') as f:
        if write_header:
            f.write(','.join(row.keys()) + '\n')
        f.write(','.join(str(v) for v in row.values()) + '\n')

    print(f"[{info['date']}] macro_score={info['macro_score']:+.3f}  "
          f"regime={decision['regime']}  max_pos={decision['max_positions']}  "
          f"daily_alpha={daily_alpha:+.3f}%  cum={cum_alpha:+.3f}%")


def cmd_report():
    if not TRACKER_PATH.exists():
        print('No data yet'); return
    df = pd.read_csv(TRACKER_PATH, parse_dates=['date']).sort_values('date').reset_index(drop=True)

    n = len(df)
    n_tight = (df['regime']=='TIGHT').sum()
    n_loose = (df['regime']=='LOOSE').sum()
    n_normal = (df['regime']=='NORMAL').sum()
    cum_a = df['cum_alpha_pct'].iloc[-1] if not df.empty else 0
    today = date.today()
    months = (today.year - DEPLOY_DATE.year)*12 + (today.month - DEPLOY_DATE.month)

    txt = []
    txt.append("="*72)
    txt.append("SBV Macro Overlay — Paper-Trade Report")
    txt.append("="*72)
    txt.append(f"Deploy date: {DEPLOY_DATE}")
    txt.append(f"Report date: {today}  ({months} months elapsed)")
    txt.append(f"Tracking window: {df['date'].iloc[0].date()} -> {df['date'].iloc[-1].date()}")
    txt.append(f"Sessions tracked: {n}")
    txt.append(f"  NORMAL: {n_normal} ({100*n_normal/n:.1f}%)")
    txt.append(f"  TIGHT:  {n_tight}  ({100*n_tight/n:.1f}%)")
    txt.append(f"  LOOSE:  {n_loose}  ({100*n_loose/n:.1f}%)")
    txt.append("")
    txt.append(f"Cumulative ghost-alpha: {cum_a:+.3f}% (12mo proxy)")
    txt.append("")
    # List regime changes
    df['regime_prev'] = df['regime'].shift(1)
    changes = df[df['regime']!=df['regime_prev']].dropna(subset=['regime_prev'])
    txt.append("Regime transitions:")
    for _, r in changes.iterrows():
        txt.append(f"  {r['date'].date()}  {r['regime_prev']:>6s} -> {r['regime']:<6s}  "
                   f"macro_score={r['macro_score']:+.2f}  refi={r['refi_rate']}%")

    txt.append("")
    if months >= 11:
        txt.append("Validation vs backtest expectation:")
        txt.append(f"  Expected 12mo alpha range: +1.0pp to +1.5pp (realistic, lower bound of backtest)")
        txt.append(f"  Backtest OOS2 2022-26 estimate: +2.40pp (upper)")
        txt.append(f"  Realized 12mo alpha: {cum_a:+.3f}pp")
        if cum_a >= 1.0:
            verdict = "🟢 GREEN — confirmed live alpha within expected range; keep deploy"
        elif cum_a >= 0:
            verdict = "🟡 YELLOW — below backtest range, marginal; extend tracking 6mo"
        else:
            verdict = "🔴 RED — negative alpha; revert in sbv_macro_overlay.py (set BOOST_ENABLED=False)"
        txt.append(f"  Verdict: {verdict}")
    else:
        txt.append(f"Report incomplete: only {months} months elapsed.")
        txt.append(f"  Wait until {REPORT_DATE} for final verdict.")

    txt.append("")
    txt.append("Decision rules:")
    txt.append("  GREEN  -> keep deploy, optionally raise sc_l to 1.25")
    txt.append("  YELLOW -> extend tracking 6 more months before action")
    txt.append("  RED    -> revert via BOOST_ENABLED=False in sbv_macro_overlay.py")

    out = '\n'.join(txt)
    print(out)
    REPORT_PATH.write_text(out, encoding='utf-8')
    print(f"\nReport saved: {REPORT_PATH}")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', nargs='?', default='update', choices=['update','report'])
    a = p.parse_args()
    {'update': cmd_update, 'report': cmd_report}[a.mode]()
