"""
SBV Macro Overlay — Plan A deployment.

Signal: composite of (1) Vietnam SBV refinancing rate 90-day change, lagged 90
        sessions, and (2) DXY 252d rank. Standardized via expanding z-score.

Action when signal triggers:
  TIGHT (composite z >= +1.0): macro stress regime — scale max_positions DOWN
  LOOSE (composite z <= -0.7): macro loose regime — expand max_positions UP
  NEUTRAL: no change

Validated 2026-05-19 via tier2b_sensitivity.py:
  - FULL 2014-2026:  CAGR +2.37pp, Sharpe +0.03, DD unchanged
  - IS  2014-2018:   +1.25pp
  - OOS1 2019-2021:  +4.69pp (Covid era — possibly inflated)
  - OOS2 2022-2026:  +2.40pp (more reliable estimate)
  - Date noise (±5d, 20 trials): 20/20 positive
  - Drop-one-event: all 11 post-2014 events tested, alpha positive
  - Lag sensitivity: stable in [75, 120]

Realistic expectation: +1.0 to +1.5pp CAGR with regime-dependence (alpha
larger during unexpected SBV decisions, smaller during anticipated cycles).

Files:
  - sbv_refi_events.json — single source of truth for SBV refi rate events
  - sbv_macro_state.json — persistent state (current window, cycle history)
  - sbv_macro_log.csv    — daily decisions for audit
"""
import json
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np

WORKDIR = Path(__file__).parent
EVENTS_PATH = WORKDIR / 'sbv_refi_events.json'
STATE_PATH = WORKDIR / 'sbv_macro_state.json'
LOG_PATH   = WORKDIR / 'data/sbv_macro_log.csv'

# ── Tuning (from sensitivity-validated optimum) ──
LAG_DAYS = 90
TH_TIGHT = 1.0
TH_LOOSE = -0.7
SC_TIGHT = 0.7   # equivalent to max_pos 12 -> 8 (rough proxy)
SC_LOOSE = 1.2   # equivalent to max_pos 12 -> 15
MIN_HOLD_DAYS = 20
MAX_POS_NORMAL = 12
MAX_POS_TIGHT  = 8   # 12 * 0.67 ~ 8
MAX_POS_LOOSE  = 15  # 12 * 1.25 ~ 15

BOOST_ENABLED = True

# ── SBV refi rate events (verified 2026-05-19 v2) ──
# v2 changes vs v1 (2026-05-19):
#   - 2006-2008 H1: filled context (6.5% stable pre-2008, 7.5% in Feb 2008)
#   - 2008-06-11: corrected 14.00% -> 15.00% (was confused with base rate)
# Pre-2014 entries are CONTEXTUAL — IC/backtest use 2011+ window only.
# Some pre-2011 dates have ±1-2 month uncertainty due to limited Vietnamese
# archive access; sequence and magnitudes verified via multiple sources.
SBV_REFI_EVENTS = [
    # Pre-2008: stable (limited date precision)
    ('2006-01-01', 6.50),  ('2008-02-01', 7.50),
    # 2008 hike cycle peak (CORRECTED: 15% not 14%)
    ('2008-06-11', 15.00),  ('2008-10-21', 13.00), ('2008-11-05', 12.00),
    ('2008-12-05', 11.00),  ('2008-12-22', 9.50),
    ('2009-02-01', 8.00),  ('2009-04-01', 7.00),  ('2009-12-01', 8.00),
    ('2010-11-05', 9.00),
    ('2011-02-17', 11.00), ('2011-04-01', 12.00), ('2011-05-01', 14.00),
    ('2011-10-10', 15.00),
    ('2012-03-12', 14.00), ('2012-04-10', 13.00), ('2012-05-25', 12.00),
    ('2012-06-11', 11.00), ('2012-07-01', 10.00), ('2012-12-24', 9.00),
    ('2013-03-26', 8.00),  ('2013-05-13', 7.00),
    ('2014-03-18', 6.50),  ('2017-07-10', 6.25),  ('2019-09-16', 6.00),
    ('2020-03-17', 5.00),  ('2020-05-13', 4.50),  ('2020-10-01', 4.00),
    ('2022-09-23', 5.00),  ('2022-10-25', 6.00),  ('2023-04-03', 5.50),
    ('2023-05-25', 5.00),  ('2023-06-19', 4.50),
    # Stable since 2023-06-19 at 4.50% (verified 2026-05-19 via SBV official sources)
]


def save_events():
    """Persist events to JSON for transparency / manual update."""
    EVENTS_PATH.write_text(json.dumps({
        'last_updated': str(date.today()),
        'note': 'Add new SBV refi rate events here when SBV announces',
        'events': SBV_REFI_EVENTS,
    }, indent=2))


def load_events():
    """Load events from JSON if exists, else use defaults."""
    if EVENTS_PATH.exists():
        try:
            d = json.loads(EVENTS_PATH.read_text())
            return [(e[0], e[1]) for e in d['events']]
        except Exception:
            pass
    return SBV_REFI_EVENTS


def _bq(sql):
    res = subprocess.run(['bq','query','--use_legacy_sql=false',
                          '--project_id=lithe-record-440915-m9',
                          '--format=csv','--max_rows=2000','-q', sql],
                         capture_output=True, text=True, shell=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr)
    return res.stdout


def get_dxy_rank252():
    """Fetch DXY 252d rank using yfinance."""
    import yfinance as yf
    h = yf.Ticker('DX-Y.NYB').history(period='400d', auto_adjust=False)
    if len(h) < 100: return None, None
    h = h.sort_index()
    cur = float(h['Close'].iloc[-1])
    # Rank: where is today's level in last 252d?
    last_252 = h['Close'].tail(252)
    rank = (last_252 <= cur).sum() / len(last_252)
    return cur, rank


def compute_signal_today(events=None):
    """Compute macro composite z-score for today using historical context."""
    events = events or load_events()
    # Build full daily series
    sbv = pd.DataFrame(events, columns=['time','refi_rate'])
    sbv['time'] = pd.to_datetime(sbv['time'])
    dr = pd.date_range(events[0][0], date.today(), freq='D')
    d = pd.DataFrame({'time': dr}).merge(sbv, on='time', how='left')
    d['refi_rate'] = d['refi_rate'].ffill()
    d = d.dropna()
    d['refi_chg_90d']  = d['refi_rate'].diff(90)
    d['refi_chg_90d_lag90']  = d['refi_chg_90d'].shift(90)

    # Get DXY data via BQ for full 252d history rank computation
    import yfinance as yf
    h = yf.Ticker('DX-Y.NYB').history(period='500d', auto_adjust=False)
    if len(h) < 252: return None
    h = h.sort_index()
    h['DXY_rank252'] = h['Close'].rolling(252).rank(pct=True)
    dxy_today_rank = float(h['DXY_rank252'].iloc[-1])
    dxy_today      = float(h['Close'].iloc[-1])

    # Need expanding mean/std for z-score of refi_chg_90d_lag90.
    # Build full history of refi changes from earliest date.
    refi_lag_series = d['refi_chg_90d_lag90'].dropna()
    if len(refi_lag_series) < 252:
        return None
    refi_mean = refi_lag_series.mean()
    refi_std  = refi_lag_series.std()
    refi_today_lag = float(d['refi_chg_90d_lag90'].iloc[-1])
    z_refi = (refi_today_lag - refi_mean) / refi_std if refi_std > 0 else 0.0

    # DXY: use expanding z from full history pulled
    dxy_full = h['DXY_rank252'].dropna()
    z_dxy = (dxy_today_rank - dxy_full.mean()) / dxy_full.std() if dxy_full.std()>0 else 0

    macro = (z_refi + z_dxy) / 2

    return {
        'date': str(d['time'].iloc[-1].date()),
        'refi_rate': float(d['refi_rate'].iloc[-1]),
        'refi_chg_90d_lag90': refi_today_lag,
        'dxy': dxy_today,
        'dxy_rank252': dxy_today_rank,
        'z_refi': z_refi,
        'z_dxy': z_dxy,
        'macro_score': macro,
    }


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {'regime_history': [], 'current_regime': None}


def save_state(st):
    STATE_PATH.write_text(json.dumps(st, indent=2, default=str))


def update_state(today_info, st=None):
    """Classify regime + manage min-hold window."""
    st = st or load_state()
    today = today_info['date']
    ms = today_info['macro_score']

    decision = {'date': today, 'macro_score': ms, 'regime': 'NORMAL',
                'max_positions': MAX_POS_NORMAL, 'reason': ''}

    # Check existing window expiry (calendar days approximation)
    if st.get('current_regime'):
        cr = st['current_regime']
        ent_d = datetime.strptime(cr['entry_date'], '%Y-%m-%d').date()
        today_d = datetime.strptime(today, '%Y-%m-%d').date()
        cal_age = (today_d - ent_d).days
        # MIN_HOLD_DAYS in trading sessions ~ 1.4x calendar days
        if cal_age >= int(MIN_HOLD_DAYS * 1.4):
            st['regime_history'].append(cr)
            st['current_regime'] = None
            decision['reason'] = 'window_expired'

    # Detect new regime if no active window
    if not st.get('current_regime') and BOOST_ENABLED:
        if ms >= TH_TIGHT:
            regime = 'TIGHT'
            mp = MAX_POS_TIGHT
            decision['reason'] = 'new_TIGHT_regime'
        elif ms <= TH_LOOSE:
            regime = 'LOOSE'
            mp = MAX_POS_LOOSE
            decision['reason'] = 'new_LOOSE_regime'
        else:
            regime = None
            mp = MAX_POS_NORMAL

        if regime:
            st['current_regime'] = {
                'entry_date': today, 'regime': regime, 'macro_score': ms,
                'min_hold_days': MIN_HOLD_DAYS,
            }
            decision['regime'] = regime
            decision['max_positions'] = mp

    # Reflect active window
    if st.get('current_regime'):
        decision['regime'] = st['current_regime']['regime']
        decision['max_positions'] = (MAX_POS_TIGHT if decision['regime']=='TIGHT'
                                      else MAX_POS_LOOSE)
        if not decision['reason']:
            decision['reason'] = f"active_{decision['regime']}_window"

    if not decision['reason']:
        decision['reason'] = 'NORMAL'

    save_state(st)
    return decision


def log_decision(today_info, decision):
    fields = ['date','refi_rate','refi_chg_90d_lag90','dxy','dxy_rank252',
              'z_refi','z_dxy','macro_score','regime','max_positions','reason']
    row = {f: today_info.get(f, '') if f in today_info else decision.get(f, '')
           for f in fields}
    write_header = not LOG_PATH.exists()
    with LOG_PATH.open('a', encoding='utf-8') as f:
        if write_header:
            f.write(','.join(fields) + '\n')
        f.write(','.join(str(row[k])[:24] if not isinstance(row[k], float) else f"{row[k]:.4f}"
                          for k in fields) + '\n')


def get_current_max_positions():
    """Production hook. Read state and return current max_positions.
    Returns 12 (normal), 8 (tight), or 15 (loose)."""
    if not BOOST_ENABLED:
        return MAX_POS_NORMAL
    st = load_state()
    cr = st.get('current_regime')
    if not cr:
        return MAX_POS_NORMAL
    # Verify window not stale
    ent_d = datetime.strptime(cr['entry_date'], '%Y-%m-%d').date()
    today_d = date.today()
    cal_age = (today_d - ent_d).days
    if cal_age >= int(MIN_HOLD_DAYS * 1.4):
        return MAX_POS_NORMAL  # expired (next update will close it)
    if cr['regime'] == 'TIGHT':
        return MAX_POS_TIGHT
    elif cr['regime'] == 'LOOSE':
        return MAX_POS_LOOSE
    return MAX_POS_NORMAL


def add_event(date_str, rate):
    """User-facing CLI: add a new SBV rate event to the JSON."""
    date_str = pd.Timestamp(date_str).strftime('%Y-%m-%d')
    rate = float(rate)
    save_events()  # ensure file exists with defaults
    d = json.loads(EVENTS_PATH.read_text())
    existing = [(e[0], e[1]) for e in d['events']]
    # Prevent duplicates
    if any(e[0] == date_str for e in existing):
        print(f"  ! Date {date_str} already exists. Use a different date or edit JSON manually.")
        return False
    existing.append((date_str, rate))
    existing.sort()
    d['events'] = existing
    d['last_updated'] = str(date.today())
    EVENTS_PATH.write_text(json.dumps(d, indent=2))
    # Reset ack: new event means user wants warnings to resume tracking from here
    ack_path = WORKDIR / 'sbv_ack.json'
    if ack_path.exists():
        ack_path.unlink()
    print(f"  [OK] Added SBV event: {date_str}  refi_rate={rate}%")
    print(f"  Total events: {len(existing)} (latest: {existing[-1][0]} @ {existing[-1][1]}%)")
    return True


def stale_check(threshold_days=180):
    """C-option: warn if latest SBV event is older than threshold_days
    AND newer than last acknowledged event.

    Suppression: a user-acknowledged 'no-change' baseline is stored. As long as
    the latest event in JSON matches the acknowledged event, no warning fires.
    Only when JSON has events newer than acknowledged AND the newest is stale
    do we raise. This means: by default, user is assumed up-to-date with all
    events currently in JSON; warning only fires if a new SBV decision is
    added but somehow becomes stale (edge case)."""
    events = load_events()
    latest_date_str = events[-1][0]
    latest_date = pd.Timestamp(latest_date_str).date()
    age = (date.today() - latest_date).days

    # Load ack baseline
    ack_path = WORKDIR / 'sbv_ack.json'
    ack_event = None
    if ack_path.exists():
        try:
            ack_event = json.loads(ack_path.read_text()).get('acknowledged_latest')
        except Exception:
            pass

    # If user has ack'd this exact event, suppress warning
    if ack_event == latest_date_str:
        return None

    # If no ack file or ack mismatches → fire warning
    if age > threshold_days:
        return {'stale': True, 'latest_date': latest_date_str,
                'age_days': age, 'threshold': threshold_days,
                'message': (f"WARN: latest SBV event {latest_date} is {age} days old. "
                            f"If SBV announced new rate, add: "
                            f"python sbv_macro_overlay.py --add-event YYYY-MM-DD RATE  "
                            f"OR ack no-change: python sbv_macro_overlay.py --ack-no-change")}
    return None


def ack_no_change():
    """User confirms latest event is current — silence stale warning."""
    events = load_events()
    latest = events[-1][0]
    ack_path = WORKDIR / 'sbv_ack.json'
    ack_path.write_text(json.dumps({
        'acknowledged_latest': latest,
        'acknowledged_on': str(date.today()),
        'note': ('User confirmed no SBV rate change since this date. Warning '
                 'will resume if a newer event is added but becomes stale.')
    }, indent=2))
    print(f"  [OK] Acknowledged: latest event {latest} confirmed current.")
    print(f"  Warning suppressed until a new event is added.")


if __name__ == '__main__':
    import sys
    if '--add-event' in sys.argv:
        idx = sys.argv.index('--add-event')
        if len(sys.argv) < idx + 3:
            print("Usage: python sbv_macro_overlay.py --add-event YYYY-MM-DD RATE")
            sys.exit(1)
        ok = add_event(sys.argv[idx+1], sys.argv[idx+2])
        sys.exit(0 if ok else 1)
    if '--stale-check' in sys.argv:
        s = stale_check()
        if s: print(s['message'])
        else: print(f"  OK: latest event acknowledged or fresh")
        sys.exit(0)
    if '--ack-no-change' in sys.argv:
        ack_no_change()
        sys.exit(0)
    save_events()  # ensure events JSON exists
    info = compute_signal_today()
    if info is None:
        print('No data available'); exit(1)
    print(f"Today: {info['date']}")
    print(f"  refi_rate     = {info['refi_rate']:.2f}%")
    print(f"  refi_chg_90d_lag90 = {info['refi_chg_90d_lag90']:+.3f}")
    print(f"  z_refi        = {info['z_refi']:+.3f}")
    print(f"  DXY rank252   = {info['dxy_rank252']:.3f}")
    print(f"  z_dxy         = {info['z_dxy']:+.3f}")
    print(f"  macro_score   = {info['macro_score']:+.3f}")
    print(f"  thresholds    = TIGHT(>=+{TH_TIGHT})  LOOSE(<={TH_LOOSE})")
    dec = update_state(info)
    print(f"\nDecision: regime={dec['regime']}  max_positions={dec['max_positions']}  ({dec['reason']})")
    log_decision(info, dec)
    print(f"\nProduction max_positions: {get_current_max_positions()}")
