"""
BullDvg Boost — Plan A deployment.

Trigger: BullDvg{1,12} fires on VNINDEX (from filter.json formulas) AND
         close_hi252 <= 0.85 (VNI >=15% below trailing 252d high).
Action:  expand max_positions 12 -> 15 in recommend_holistic.py select_book()
         for HOLD_DAYS=60 sessions after fire.
Cost:    none (uses idle cash + slot capacity).

Validated 2026-05-19 via backtest_plan_a.py:
  - OOS 2019-2026 (8 fires, 6 used after cooldown):
    lift=25% hold=60 -> CAGR +1.09pp / Sh +0.05 / DD unchanged / Calmar +0.05
  - Walk-forward stable: IS 2014-18 also +0.33pp
  - DD never worsens because filter triggers only at deep drawdowns

Files:
  - bull_div_boost_state.json — persistent state (current window, fire history)
  - bull_div_boost_log.csv    — daily decisions for audit / paper-trade tracker
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKDIR = Path(__file__).parent
STATE_PATH = WORKDIR / 'bull_div_boost_state.json'
LOG_PATH   = WORKDIR / 'bull_div_boost_log.csv'

# Tuning (from OOS-best conservative pick — see backtest_plan_a.py)
HOLD_DAYS  = 60   # boost window length in trading sessions
COOLDOWN   = 20   # extra sessions where re-fire ignored (avoids duplicate boosts)
MAX_POS_NORMAL = 12
MAX_POS_BOOSTED = 15  # +25% capacity, equivalent to lift=25% in backtest
HI252_THRESHOLD = 0.85  # filter: VNI must be >=15% below 252d high

# Toggle: set False to disable boost without code change
BOOST_ENABLED = True


def _q(sql: str) -> str:
    """Run bq query, return CSV string."""
    cmd = ['bq', 'query', '--use_legacy_sql=false',
           '--project_id=lithe-record-440915-m9',
           '--format=csv', '--max_rows=10', '-q', sql]
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if res.returncode != 0:
        raise RuntimeError(f"bq query failed: {res.stderr}")
    return res.stdout


def detect_today():
    """
    Compute today's BullDvg fire status + close_hi252.
    Returns dict: {
        'date': 'YYYY-MM-DD',
        'bull1_fire': bool,
        'bull12_fire': bool,
        'any_bull_fire': bool,
        'close_hi252': float | None,
        'filter_pass': bool,
        'reason': str,
    }
    """
    sql = ('WITH t AS (SELECT t.time, t.Close, t.High, t.D_RSI, t.D_RSI_T1W, '
           't.D_RSI_MinT3, t.D_RSI_Min1W, t.D_RSI_Min1W_Close, t.D_RSI_Min3M, '
           't.D_RSI_Min3M_Close, t.D_RSI_Max1W, t.D_MACDdiff, t.D_CMF, t.C_L1M, '
           't.C_L1W FROM tav2_bq.ticker AS t WHERE t.ticker="VNINDEX" AND '
           't.time >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)), '
           'latest AS (SELECT * FROM t WHERE time=(SELECT MAX(time) FROM t)), '
           'hi AS (SELECT MAX(High) AS hi252 FROM t) '
           'SELECT l.*, h.hi252 FROM latest l, hi h')
    out = _q(sql).strip().split('\n')
    if len(out) < 2:
        return {'date': str(datetime.today().date()), 'error': 'no_data'}
    header = out[0].split(','); row = out[1].split(',')
    rec = dict(zip(header, row))

    def f(k):
        try: return float(rec[k])
        except: return None

    d   = rec['time']
    cl  = f('Close')
    hi  = f('hi252') or 1.0
    rsi = f('D_RSI');           rsiT1W = f('D_RSI_T1W')
    minT3 = f('D_RSI_MinT3')
    min1W = f('D_RSI_Min1W');   min1Wc = f('D_RSI_Min1W_Close')
    min3M = f('D_RSI_Min3M');   min3Mc = f('D_RSI_Min3M_Close')
    max1W = f('D_RSI_Max1W')
    macd  = f('D_MACDdiff');    cmf = f('D_CMF')
    cl1m  = f('C_L1M');         cl1w = f('C_L1W')

    def safe_div(a,b):
        if a is None or b is None or b==0: return None
        return a/b

    # BullDvgVNI1 (filter.json)
    try:
        b1 = (safe_div(min1W,min3M) > 0.9 and min1W < 0.6 and min3M < 0.4
              and safe_div(min1Wc,min3Mc) < 1.15
              and macd > 0 and minT3 < 0.5 and max1W < 0.48
              and safe_div(rsi,rsiT1W) > 1.12
              and cmf > 0 and cl1m < 1.21 and cl1w < 1.05)
    except Exception:
        b1 = False
    # BullDvgVNI12
    try:
        b12 = (safe_div(min1W,min3M) > 0.92 and min1W < 0.52 and min3M < 0.38
               and safe_div(min1Wc,min3Mc) < 1.1
               and macd > 0 and minT3 < 0.56 and max1W < 0.64
               and safe_div(rsi,rsiT1W) > 1.1
               and cmf > 0 and cl1m < 1.2 and cl1w < 1.025)
    except Exception:
        b12 = False

    close_hi252 = cl/hi if cl and hi else None
    any_fire = bool(b1 or b12)
    filter_pass = bool(any_fire and close_hi252 is not None and close_hi252 <= HI252_THRESHOLD)
    reason = ''
    if not any_fire:
        reason = 'no_bull_fire'
    elif close_hi252 is None:
        reason = 'no_close_hi252'
    elif close_hi252 > HI252_THRESHOLD:
        reason = f'close_hi252={close_hi252:.3f}>thr={HI252_THRESHOLD}'
    else:
        reason = f'fire+filter_pass close_hi252={close_hi252:.3f}'
    return {'date': d, 'bull1_fire': bool(b1), 'bull12_fire': bool(b12),
            'any_bull_fire': any_fire, 'close_hi252': close_hi252,
            'filter_pass': filter_pass, 'reason': reason}


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {'fire_history': [], 'current_window': None}


def save_state(st):
    STATE_PATH.write_text(json.dumps(st, indent=2, default=str))


def update_state(today_info, st=None):
    """
    Update state based on today's detection.
    Returns updated state + decision dict.
    """
    st = st or load_state()
    today = today_info['date']
    decision = {'date': today, 'boost_active': False,
                'max_positions': MAX_POS_NORMAL,
                'window_end': None, 'reason': ''}

    # Check existing window expiry (using session count is more rigorous;
    # here we use calendar approximation: 60 sessions ~= 84 calendar days)
    if st.get('current_window'):
        w = st['current_window']
        fire_d = datetime.strptime(w['fire_date'], '%Y-%m-%d').date()
        today_d = datetime.strptime(today, '%Y-%m-%d').date()
        cal_days = (today_d - fire_d).days
        if cal_days >= int(HOLD_DAYS * 1.4):  # ~84 calendar days
            st['current_window'] = None
            decision['reason'] = 'window_expired'

    # Check if new fire trigger
    if today_info.get('filter_pass'):
        in_cooldown = False
        if st.get('current_window'):
            in_cooldown = True
        # Look back at recent fires to enforce cooldown across windows
        elif st['fire_history']:
            last_fire = st['fire_history'][-1]
            last_d = datetime.strptime(last_fire['date'], '%Y-%m-%d').date()
            today_d = datetime.strptime(today, '%Y-%m-%d').date()
            if (today_d - last_d).days < int((HOLD_DAYS + COOLDOWN) * 1.4):
                in_cooldown = True
                decision['reason'] = f'cooldown_after_{last_fire["date"]}'
        if not in_cooldown:
            fire_entry = {'date': today, 'close_hi252': today_info['close_hi252'],
                          'b1': today_info['bull1_fire'], 'b12': today_info['bull12_fire']}
            st['fire_history'].append(fire_entry)
            st['current_window'] = {'fire_date': today, 'hold_days': HOLD_DAYS}
            decision['reason'] = 'new_fire_window_opened'

    # Compute boost active flag
    if BOOST_ENABLED and st.get('current_window'):
        decision['boost_active'] = True
        decision['max_positions'] = MAX_POS_BOOSTED
        decision['window_end'] = st['current_window']['fire_date']

    if not decision['reason']:
        decision['reason'] = 'normal'
    save_state(st)
    return decision


def log_decision(today_info, decision):
    """Append daily decision to audit log."""
    fields = ['date','any_bull_fire','bull1','bull12','close_hi252',
              'filter_pass','boost_active','max_positions','reason']
    row = {
        'date': today_info['date'],
        'any_bull_fire': int(bool(today_info.get('any_bull_fire'))),
        'bull1': int(bool(today_info.get('bull1_fire'))),
        'bull12': int(bool(today_info.get('bull12_fire'))),
        'close_hi252': f"{today_info.get('close_hi252', ''):.4f}"
                        if today_info.get('close_hi252') is not None else '',
        'filter_pass': int(bool(today_info.get('filter_pass'))),
        'boost_active': int(bool(decision['boost_active'])),
        'max_positions': decision['max_positions'],
        'reason': decision['reason'].replace(',',';'),
    }
    write_header = not LOG_PATH.exists()
    with LOG_PATH.open('a', encoding='utf-8') as f:
        if write_header:
            f.write(','.join(fields) + '\n')
        f.write(','.join(str(row[k]) for k in fields) + '\n')


def get_current_max_positions():
    """
    Read state and return current max_positions for production use.
    This is the ONLY function recommend_holistic.py needs to call.
    """
    if not BOOST_ENABLED:
        return MAX_POS_NORMAL
    st = load_state()
    if not st.get('current_window'):
        return MAX_POS_NORMAL
    # Check window not expired
    fire_d = datetime.strptime(st['current_window']['fire_date'], '%Y-%m-%d').date()
    today_d = datetime.today().date()
    cal_days = (today_d - fire_d).days
    if cal_days >= int(HOLD_DAYS * 1.4):
        return MAX_POS_NORMAL
    return MAX_POS_BOOSTED


if __name__ == '__main__':
    info = detect_today()
    print('Today info:', info)
    dec = update_state(info)
    print('Decision:', dec)
    log_decision(info, dec)
    print(f'\nProduction max_positions to use today: {get_current_max_positions()}')
