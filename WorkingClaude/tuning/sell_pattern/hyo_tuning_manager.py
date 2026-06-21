import os
import pickle
import socket
import sys
import warnings
from datetime import timedelta
from functools import partial
from typing import Dict, Any

import numpy as np
import pandas as pd
from hyperopt import hp, fmin, tpe, STATUS_OK
from hyperopt.mongoexp import MongoTrials
from joblib import Memory
from pathos.multiprocessing import ProcessingPool as Pool
from pymongo import MongoClient

from core_utils.base_eval import PreProcess
from core_utils.common import extract_indicators
from core_utils.constant import REDIS_HOST, MONGO_HOST, MONGO_PORT, JOBLIB_CACHE_DIR
from core_utils.redis_cache import EvalRedis
from webui.utils import ShortEvaluation, MarketEvaluation

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = current_dir.replace("/tuning/sell_pattern", "")
os.chdir(current_dir)
sys.path.insert(0, current_dir)

warnings.simplefilter(action='ignore')

memory = Memory(location=f'{JOBLIB_CACHE_DIR}_tuning', verbose=0)
memory.reduce_size(bytes_limit=3e9, age_limit=timedelta(days=1))
redis_cache = EvalRedis(host=REDIS_HOST, db=1)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))  # lên đến thư mục /workspace/kaffa_v2

FPATH = os.path.join(BASE_DIR, 'ticker_v1a')
PATH = os.path.join(BASE_DIR, 'tuning/hyperopt_results')
TICKER_PATH = os.path.join(BASE_DIR, 'tuning/sell_pattern/tickers.csv')
NUM_PROCS = 20

# with SellResistance1Y/ S13/ SellResistance/ SellVolMax using NUM_DEAL_THRESHOLD =150
NUM_DEAL_THRESHOLD = 150

# NUM_DEAL_THRESHOLD = 200
LIMIT_PERIOD = 40

PATTERN_VERSION = 'v1'
TRACK_VERSION = "13-03-2026"
USERNAME = socket.gethostname()

df_vnindex = pd.read_csv(f'{FPATH}/VNINDEX.csv')
market_eval = MarketEvaluation(df_vnindex, cache_service=redis_cache)

RECORD = -np.inf

# ============================================================================
# PATTERN CONFIGURATIONS - SINGLE SOURCE OF TRUTH
# Export Init filter and pattern configs for use by other modules
# (run_tuning.py, parse_hyperopt_results.py)
# ============================================================================

# Base Init filter used by most patterns
Init = "((Volume_3M_P50*Price/Inflation_7)>700_000_000) & (Volume > 2e+4)"

# Pattern configurations will be populated by SellPatternTuner class
# This dict will be filled after the class definition
SELL_PATTERNS = {}


def eval_filter_all_v2(dictFilter, list_processed_ticker, CUTLOSS=1, validate=False):
    """ Return dataframe of profit
        pdp: dataframe of profit
        pdx: dataframe of historical hit
        pdy: dataframe of latest hit
    """
    num_procs = NUM_PROCS
    indicators_used = extract_indicators(dictFilter, eval_bool=True)
    params = {
        'limit_period': LIMIT_PERIOD
    }

    # Evaluate deals for all tickers
    def eval(ticker):
        try:
            t_path = f'{FPATH}/{ticker}.csv'
            cols_in_file = pd.read_csv(t_path, nrows=0).columns.tolist()
            valid_cols = [c for c in indicators_used if c in cols_in_file]

            pdxx = pd.read_csv(t_path, usecols=valid_cols)

            eval_ticker = ShortEvaluation(ticker, pdxx, dictFilter, cutloss=CUTLOSS, cache_service=redis_cache,
                                          market_eval=market_eval)
            res_s = eval_ticker.get_shortsell(**params)
            return res_s
        except Exception as error:
            print(f"Error: {ticker}: {error}")
            pass

    with Pool(num_procs) as p:
        lres = p.map(eval, list_processed_ticker)

    try:
        lres = [res for res in lres if res is not None and not res.empty]

        if not lres:
            raise ValueError("No valid results to concatenate")

        pd_short = pd.concat(lres, axis=0).reset_index(drop=True)
        if not validate and (pd_short.shape[0] < NUM_DEAL_THRESHOLD):
            print(f'deal: {pd_short.shape[0]}')
            raise ValueError(f"Insufficient data {pd_short.shape[0]}")

        # Process dataframe
        d_agg = {'trading_val': "sum", 'p_trading_val': "sum", 'trading_val_clip': "sum", 'p_trading_val_clip': "sum",
                 'P1W': "median", 'P2W': "median", 'P3W': "median", 'P1M': "median", 'P2M': "median", 'P3M': "median",
                 'P6M': "median", 'P1Y': "median", 'P2Y': "median", 'median_profit': "median"}
        df_process = PreProcess()
        pd_short = df_process.shortsell(pd_short)
        # weight profit

        # pd_short['trading_val_clip'] = (pd_short['Price'] * pd_short['Volume_1M_P50'] / pd_short['Trading_Session']).clip(
        #     upper=0.01)
        # pd_short['p_trading_val_clip'] = pd_short['profit'] * pd_short['trading_val_clip']

        # short deal dataframe
        _pds_d = df_process.group_by(pd_short, ['filter'], d_agg=d_agg)
        _pdd_q = df_process.group_by(pd_short, ['filter', "quarter"], d_agg=d_agg)
        pd_short['month'] = pd_short['time'].str[:7]
        _pdd_m = df_process.group_by(pd_short, ['filter', "month"], d_agg=d_agg)

        _pds_d['win_quarter'] = 0.0
        _pds_d['winblock_20quarters'] = 0.0
        pd_histogram_quarter = {}
        for f in _pdd_q['filter'].unique():
            data = _pdd_q[_pdd_q['filter'] == f]
            data.rename(columns={'count_win': 'Win', 'count_loss': 'Loss', 'count_hold': 'Hold',
                                 'count_hold_win': 'Win_Hold', 'count_hold_loss': 'Loss_Hold',
                                 'count_cutloss': 'Cutloss'}, inplace=True)

            pd_histogram_quarter[f] = data[['quarter', 'Win', 'Loss', 'Hold', 'Win_Hold', 'Loss_Hold', 'Cutloss']]

        for filter, df in pd_histogram_quarter.items():
            win = df[(df['Win'] + df['Win_Hold']) >= (df['Loss'] + df['Cutloss'] + df['Loss_Hold'])].shape[0]
            loss = df[(df['Win'] + df['Win_Hold']) <= (df['Loss'] + df['Cutloss'] + df['Loss_Hold'])].shape[0]

            _pds_d.loc[_pds_d['filter'] == filter, 'win_quarter'] = win / sum([win, loss]) \
                if (win + loss) > 0 else 0

            df_tail = df.tail(21).iloc[:-1]
            win_tail = df_tail[(df_tail['Win'] + df_tail['Win_Hold']) >= (
                    df_tail['Loss'] + df_tail['Cutloss'] + df_tail['Loss_Hold'])].shape[0]
            loss_tail = df_tail[(df_tail['Win'] + df_tail['Win_Hold']) <= (
                    df_tail['Loss'] + df_tail['Cutloss'] + df_tail['Loss_Hold'])].shape[0]
            _pds_d.loc[_pds_d['filter'] == filter, 'winblock_20quarters'] = win_tail / sum(
                [win_tail, loss_tail]) if (win_tail + loss_tail) > 0 else 0

        # winblock_24months
        _pds_d['winblock_24months'] = 0
        pd_histogram_month = {}
        for f in _pdd_m['filter'].unique():
            data = _pdd_m[_pdd_m['filter'] == f]
            data.rename(columns={'count_win': 'Win', 'count_loss': 'Loss', 'count_hold': 'Hold',
                                 'count_hold_win': 'Win_Hold', 'count_hold_loss': 'Loss_Hold',
                                 'count_cutloss': 'Cutloss'}, inplace=True)

            pd_histogram_month[f] = data[['month', 'Win', 'Loss', 'Win_Hold', 'Loss_Hold', 'Cutloss']]

        for filter, df in pd_histogram_month.items():
            df_tail = df.tail(24)
            win_tail = df_tail[(df_tail['Win'] + df_tail['Win_Hold']) >= (
                    df_tail['Loss'] + df_tail['Cutloss'] + df_tail['Loss_Hold'])].shape[0]
            loss_tail = df_tail[(df_tail['Win'] + df_tail['Win_Hold']) <= (
                    df_tail['Loss'] + df_tail['Cutloss'] + df_tail['Loss_Hold'])].shape[0]

            _pds_d.loc[_pds_d['filter'] == filter, 'winblock_24months'] = win_tail / sum([win_tail, loss_tail]) \
                if (win_tail + loss_tail) > 0 else 0

        win_deal = (_pds_d['count_win'].astype(int) / _pds_d['deal'].astype(int)) * 100

        win_quarter = _pds_d['win_quarter'].values * 100
        winblock_20quarters = _pds_d['winblock_20quarters'].values * 100
        winblock_24months = _pds_d['winblock_24months'].values * 100

        # windeal, win_quarter
        penalty = 1
        if (win_quarter[0] < 50) or (winblock_20quarters[0] < 50) or (win_deal[0] < 50) or (winblock_24months[0] < 50):
            penalty *= np.min([win_quarter[0], winblock_20quarters[0], win_deal[0], winblock_24months[0]]) / 50

        profit_expected = _pds_d['profit'].values
        median_profit = _pds_d['median_profit'].values
        weighted_profit = _pds_d['p_trading_val_clip'].values / _pds_d['trading_val_clip'].values * 100

        loss_deal = (_pds_d['count_loss'].astype(int) / _pds_d['deal'].astype(int)) * 100
        hold_deal = (_pds_d['count_hold'].astype(int) / _pds_d['deal'].astype(int)) * 100
        cutloss_deal = (_pds_d['count_cutloss'].astype(int) / _pds_d['deal'].astype(int)) * 100

        # P1W, P2W, P3W, P1M, P2M, P_weighted_profit
        px = [_pds_d['P1W'].values[0], _pds_d['P2W'].values[0], _pds_d['P3W'].values[0], _pds_d['P1M'].values[0],
              _pds_d['P2M'].values[0], weighted_profit[0], profit_expected[0]]
        px_count = [x for x in px if x > 0]

        # if (profit_expected[0] + median_profit[0] + weighted_profit[0]) > 0:
        if cutloss_deal[0] > 1.8:
            count_px = max(len(px_count) - 2, 1)
        else:
            count_px = max(len(px_count), 1)

        if median_profit[0] > 0:
            penalty *= count_px / len(px)
        else:
            penalty /= count_px / len(px)
        return {
            'deal': _pds_d['deal'].values[0],
            'profit_expected': profit_expected[0],
            'median_profit': median_profit[0],
            'weighted_profit': weighted_profit[0],
            'win_deal': win_deal[0],
            'loss_deal': loss_deal[0],
            'hold_deal': hold_deal[0],
            'cutloss_deal': cutloss_deal[0],

            'win_quarter': win_quarter[0],
            'winblock_20quarters': winblock_20quarters[0],
            'winblock_24months': winblock_24months[0],

            'trading_val': _pds_d['trading_val'].values[0],
            'p_trading_val': _pds_d['p_trading_val'].values[0],
            'weighted_profit_un_clip': _pds_d['p_trading_val'] / _pds_d['trading_val'],

            'PX': _pds_d[['P1W', 'P2W', 'P3W', 'P1M', 'P2M', 'P3M', 'P6M', 'P1Y', 'P2Y']].values[0],
            'profit_win': _pds_d['p_win'].values,
            'profit_loss': _pds_d['p_loss'].values,
            'profit_hold': _pds_d['p_hold'].values,
            'profit_cutloss': _pds_d['p_cutloss'].values,
            'holding_period': _pds_d['holding_period'].values,

            'penalty': penalty,
            'status': STATUS_OK
        }

    except Exception as e:
        print(e)
        return {
            'profit_expected': np.inf,
            'median_profit': np.inf,
            'weighted_profit': np.inf,
            'trading_val': 1.0,
            'p_trading_val': np.inf,
            'deal': 1.0,
            'penalty': -1.0,
            'status': STATUS_OK
        }


class SellPatternTuner:
    def __init__(self, ticker_path=None):
        # Init = "(time>='2014-01-01') & (time<='2025-10-01') & (Volume > 2e+4)"
        Init = "((Volume_3M_P50*Price/Inflation_7)>700_000_000) & (Volume > 2e+4)"
        self.patterns = {
            'MA21': {
                'search_space': {
                    'w1': hp.quniform('w1', 0.8, 1.3, 0.01),
                    'w2': hp.quniform('w2', 0.8, 1.3, 0.01),
                    'w3': hp.quniform('w3', 0.8, 1.3, 0.01),
                    'w4': hp.quniform('w4', 0.8, 1.3, 0.01),
                    'w5': hp.quniform('w5', -15, 10, 1),
                    'w6': hp.quniform('w6', 0.8, 1.3, 0.01),
                },
                'init_vals': {
                    'w1': 1.04,
                    'w2': 0.96,
                    'w3': 1.21,
                    'w4': 0.81,
                    'w5': 7.0,
                    'w6': 0.95
                },
                'filter_template': f"{Init}"
                                   "& (MA20/MA50<{w1}) "
                                   "& (MA20_T1/MA50_T1>{w2}) "
                                   "& (D_RSI/D_RSI_T1W < {w3}) "
                                   "& (Close < {w4}*VAP1M) "
                                   "& (D_MACDdiff< {w5}) "
                                   "& (Close/Close_T1W < {w6})",
            },
            'MA31': {
                'search_space': {
                    'w1': hp.quniform('w1', 0.85, 1.2, 0.01),
                    'w2': hp.quniform('w2', 0.85, 1.2, 0.01),
                    'w3': hp.quniform('w3', 0.85, 1.2, 0.01),
                    'w4': hp.quniform('w4', 0.8, 1.05, 0.01),
                    'w5': hp.quniform('w5', 0.8, 1.05, 0.01),
                    'w6': hp.quniform('w6', 0.2, 0.7, 0.01),
                    'w7': hp.quniform('w7', -15, 10, 1),
                    'w8': hp.quniform('w8', 0.85, 1.2, 0.01),
                    'w9': hp.quniform('w9', 0.85, 1.2, 0.01)
                },
                'init_vals': {
                    'w1': 1.0,
                    'w2': 1.0,
                    'w3': 0.98,
                    'w4': 0.95,
                    'w5': 0.95,
                    'w6': 0.5,
                    'w7': 0.8,
                    'w8': 0.88,
                    'w9': 0.9
                },
                'filter_template': f"{Init}"
                                   "& (MA10/MA200<{w1}) & (MA10_T1/MA200_T1>{w2}) "
                                   "& (Close < {w3}*VAP3M) & (Close/Close_T1W < {w4})"
                                   "& (D_RSI/D_RSI_T1W < {w5}) & (D_RSI < {w6}) "
                                   "& (D_MACDdiff< {w7})"
                                   "& (NP_P0/NP_P1 < {w8}) "
                                   "& (Volume>{w9}*Volume_3M_P50)",
            },
            'MA41': {
                'search_space': {
                    'w1': hp.quniform('w1', 1.2, 1.8, 0.01),
                    'w2': hp.quniform('w2', 0.85, 1.2, 0.01),
                    'w3': hp.quniform('w3', 0.85, 1.2, 0.01),
                    'w4': hp.quniform('w4', 0.8, 1.05, 0.01),
                    'w5': hp.quniform('w5', 0.8, 1.05, 0.01),
                },
                'init_vals': {
                    'w1': 1.5,
                    'w2': 1.0,
                    'w3': 1.0,
                    'w4': 0.95,
                    'w5': 0.98,
                },
                'filter_template': f"{Init}"
                                   "& (Close > {w1}*MA200) "
                                   "& (NP_P0/NP_P1 < {w2}) "
                                   "& (Volume>{w3}*Volume_3M_P50) "
                                   "& (Close/Close_T1W < {w4}) & (Close < {w5}*VAP1M)"
            },
            'S13': {
                'search_space': {
                    'w1': hp.quniform('w1', 1.15, 1.6, 0.01),
                    'w2': hp.quniform('w2', 0.8, 1.2, 0.01),
                    'w3': hp.quniform('w3', 1, 1.4, 0.01),
                    'w4': hp.quniform('w4', 0, 7, 1),
                },
                'init_vals': {
                    'w1': 1.2,
                    'w2': 1.0,
                    'w3': 1.3,
                    'w4': 2.0,
                },
                'filter_template': f"{Init}"
                                   "& (C_L1W>={w1}) "
                                   "& (D_CMB_Peak_T1>{w2}*D_CMB) "
                                   "& (Close>{w3}*MA10) "
                                   "& (D_CMB_XFast<{w4})"
            },
            'SellBV': {
                'search_space': {
                    'w1': hp.quniform('w1', 1.7, 2.8, 0.05),
                    'w2': hp.quniform('w2', 0.6, 1.2, 0.01),
                    'w3': hp.quniform('w3', 0.75, 1.2, 0.01),
                    'w4': hp.quniform('w4', 0.85, 1.25, 0.01),
                    'w5': hp.quniform('w5', 0.95, 1.4, 0.01),
                },
                'init_vals': {
                    'w1': 2.0,
                    'w2': 0.85,
                    'w3': 1.0,
                    'w4': 1.0,
                    'w5': 1.15,
                },
                'filter_template': f"{Init}"
                                   "& (Close > {w1}*BVPS) & (Close < {w3}*VAP1M) & (Close_T1W > {w4}*VAP1M)  "
                                   "& (NP_P0 /NP_P1 < {w2}) "
                                   "& (Volume > {w5}* Volume_3M_P50) "
                                   "& (ICB_Code != 8633)"
            },
            'SellBV2': {
                'search_space': {
                    'w1': hp.quniform('w1', 0.8, 1.3, 0.01),
                    'w2': hp.quniform('w2', 0.8, 1.3, 0.01),
                    'w3': hp.quniform('w3', 0.5, 1.1, 0.01),
                    'w4': hp.quniform('w4', 0.8, 1.3, 0.01),
                    'w5': hp.quniform('w5', 0.8, 1.3, 0.01),
                    'w6': hp.quniform('w6', 0.1, 0.65, 0.01),
                    'w7': hp.quniform('w7', 1, 1.4, 0.01),
                },
                'init_vals': {
                    'w1': 1.0,
                    'w2': 1.0,
                    'w3': 0.85,
                    'w4': 0.98,
                    'w5': 1.0,
                    'w6': 0.32,
                    'w7': 1.15
                },
                'filter_template': f"{Init}"
                                   "& (PB > {w1}*PB_MA5Y + {w2}*PB_SD5Y) "
                                   "& (NP_P0 /NP_P1 < {w3}) "
                                   "& (Close < {w4}*VAP1M) & (Close_T1W > {w5}*VAP1M) "
                                   "& (D_RSI > {w6}) "
                                   "& (Volume > {w7}*Volume_3M_P50)"
            },
            'SellPE': {
                'search_space': {
                    'w1': hp.quniform('w1', 0.8, 1.3, 0.01),
                    'w2': hp.quniform('w2', 0.8, 1.3, 0.01),
                    'w3': hp.quniform('w3', 0.5, 1.1, 0.01),
                    'w4': hp.quniform('w4', 0.8, 1.3, 0.01),
                    'w5': hp.quniform('w5', 0.8, 1.3, 0.01),
                    'w6': hp.quniform('w6', 0.7, 1.3, 0.01),
                    'w7': hp.quniform('w7', 0.8, 1.3, 0.01),
                },
                'init_vals': {
                    'w1': 1.0,
                    'w2': 1.0,
                    'w3': 0.85,
                    'w4': 1.0,
                    'w5': 1.0,
                    'w6': 0.95,
                    'w7': 1.0
                },
                'filter_template': f"{Init}"
                                   "& (PE >= {w1}*PE_MA5Y  + {w2}*PE_SD5Y) "
                                   "& (NP_P0 /NP_P1 < {w3}) "
                                   "& (Close < {w4}*VAP3M) & (Close_T1W > {w5}*VAP3M) & (Close/Close_T1W < {w6}) "
                                   "& (Volume > {w7}*Volume_3M_P50)"
            },
            'SellResistance': {
                'search_space': {
                    'w1': hp.quniform('w1', 0.9, 1.1, 0.01),
                    'w2': hp.quniform('w2', 0.8, 1.3, 0.01),
                    'w3': hp.quniform('w3', 1.1, 1.6, 0.01),
                    'w4': hp.quniform('w4', 1.7, 2.5, 0.01),
                },
                'init_vals': {
                    'w1': 0.97,
                    'w2': 0.96,
                    'w3': 1.3,
                    'w4': 2.0,
                },
                'filter_template': f"{Init}"
                                   "& (Open/Close< {w1}) & (Close  <  {w2}*Res_1Y) & (Close/LO_3M_T1 > {w3}) "
                                   "& (Volume > {w4}*Volume_3M_P50)"
            },
            'SellResistance1M': {
                'search_space': {
                    'w1': hp.quniform('w1', 15, 40, 1),
                    'w2': hp.quniform('w2', 0.85, 1.2, 0.01),
                    'w3': hp.quniform('w3', 0.85, 1.2, 0.01),
                    'w4': hp.quniform('w4', 0.85, 1.3, 0.01),
                    'w5': hp.quniform('w5', 0.2, 0.4, 0.01),
                },
                'init_vals': {
                    'w1': 30.0,
                    'w2': 0.98,
                    'w3': 1.0,
                    'w4': 1.1,
                    'w5': 0.32,
                },
                'filter_template': f"{Init}"
                                   "& (ID_XVAP3M_Down_P0 - ID_XVAP1M_Down_P2 <= {w1}) "
                                   "& (Close < {w2}*VAP1M) & (Close_T1 >  {w3}*VAP1M) "
                                   "& (Volume > {w4}* Volume_3M_P50) "
                                   "& (D_RSI > {w5})"
            },
            'SellResistance1Y': {
                'search_space': {
                    'w1': hp.quniform('w1', 0.85, 1.3, 0.01),
                    'w2': hp.quniform('w2', 0.85, 1.3, 0.01),
                    'w3': hp.quniform('w3', 0.65, 1, 0.01),
                    'w4': hp.quniform('w4', 0.85, 1.3, 0.01),
                    'w5': hp.quniform('w5', 1.2, 2.2, 0.01),
                    'w6': hp.quniform('w6', 0.85, 1.3, 0.01),
                    'w7': hp.quniform('w7', 0.1, 0.7, 0.01),
                },
                'init_vals': {
                    'w1': 1.0,  # Hệ số nhân của PB_MA5Y
                    'w2': 1.0,  # Hệ số nhân của PB_SD5Y
                    'w3': 0.85,  # Tỷ lệ NP_P0 / NP_P1
                    'w4': 0.96,  # Hệ số nhân của Res_1Y
                    'w5': 1.4,  # Hệ số nhân của Volume_3M_P50
                    'w6': 1.0,  # Hệ số nhân của VAP1M
                    'w7': 0.32,  # Giá trị ngưỡng của D_RSI
                },
                'filter_template': f"{Init}"
                                   "& (PB > {w1}*PB_MA5Y + {w2}*PB_SD5Y) "
                                   "& (NP_P0 /NP_P1 < {w3}) "
                                   "& (Close < {w4}*Res_1Y) "
                                   "& (Close_T1W > {w6}*VAP1M) "
                                   "& (Volume  > {w5}*Volume_3M_P50) "
                                   "& (D_RSI > {w7})"
            },
            'BearDvg2': {
                'search_space': {
                    'w1': hp.quniform('w1', 0.8, 1.3, 0.01),
                    'w2': hp.quniform('w2', 0.5, 1, 0.01),
                    'w3': hp.quniform('w3', 0.65, 0.8, 0.01),
                    'w4': hp.quniform('w4', 0.5, 0.65, 0.01),
                    'w5': hp.quniform('w5', 0.9, 1.4, 0.01),
                    'w6': hp.quniform('w6', 1, 1.5, 0.01),
                    'w7': hp.quniform('w7', 0.8, 1.3, 0.01),
                    'w8': hp.quniform('w8', 0.9, 1.4, 0.01),
                    'w9': hp.quniform('w9', 0.8, 1.4, 0.01),
                },
                'init_vals': {
                    'w1': 1.03,
                    'w2': 0.75,
                    'w3': 0.69,
                    'w4': 0.6,
                    'w5': 1.14,
                    'w6': 1.25,
                    'w7': 1.0,
                    'w8': 1.18,
                    'w9': 1.0,
                },
                'filter_template': f"{Init}"
                                   "& (D_RSI_Max1W/D_RSI > {w1}) & (D_RSI_T1/D_RSI > {w7}) "
                                   "& (D_RSI_Max3M > {w2}) "
                                   "& (D_RSI_Max1W < {w3}) & (D_RSI_Max1W >{w4}) "
                                   "& (D_RSI_Max1W_Close/D_RSI_Max3M_Close > {w5}) "
                                   "& (D_RSI_Max3M_MACD/D_RSI_Max1W_MACD > {w6}) "
                                   "& (Volume > {w8}*Volume_1M)"
                                   "& (D_RSI_Max3M/D_RSI_Max1W > {w9})"
            },
            'SellVolMax': {
                'search_space': {
                    'w1': hp.quniform('w1', 0.75, 1.3, 0.01),
                    'w2': hp.quniform('w2', 100, 150, 1),
                    'w3': hp.quniform('w3', 0.8, 1.3, 0.01),
                    'w4': hp.quniform('w4', 0.15, 0.5, 0.01),
                    'w5': hp.quniform('w5', 0.8, 1.3, 0.01),
                    'w6': hp.quniform('w6', 0.8, 1.3, 0.01),
                    'w7': hp.quniform('w7', 1.1, 1.7, 0.01),
                },
                'init_vals': {
                    'w1': 0.9,
                    'w2': 120,
                    'w3': 1.0,
                    'w4': 0.32,
                    'w5': 0.98,
                    'w6': 0.95,
                    'w7': 1.3,
                },
                'filter_template': f"{Init}"
                                   "& (Close/Volume_MaxTop5_2Y_Close < {w1}) "
                                   "& (ID_Current - Volume_MaxTop5_2Y_ID <={w2}) "
                                   "& (Close < {w3}*VAP1W) "
                                   "& (D_RSI > {w4}) "
                                   "& (Close/Close_T1 < {w5}) "
                                   "& (D_RSI/D_RSI_T1W < {w6}) "
                                   "& (Close_T1/LO_3M_T1 > {w7})"
            },
            'SellLowGrowth': {
                'search_space': {
                    'w1': hp.quniform('w1', 1.1, 1.3, 0.01),
                    'w2': hp.quniform('w1', 1.1, 1.3, 0.01),
                },
                'init_vals': {
                    'w1': 1.2,
                    'w2': 10.0,
                },
                'filter_template': f"{Init}"
                                   "& (NP_P0/NP_P4 < {w1}) & (ID_Current -  ID_Release <= {w2}) "
            },
            # 'BearDvgVNI': {
            #     'search_space': {
            #         'w1': hp.quniform('w1', 1.0, 1.05, 0.002),  # (D_RSI_Max1W/D_RSI > {w1})
            #         'w2': hp.quniform('w2', 0.7, 0.85, 0.01),  # (D_RSI_Max3M > {w2})
            #         'w3': hp.quniform('w3', 0.55, 0.8, 0.01),  # D_RSI_Max1W < {w3}
            #         'w4': hp.quniform('w4', 0.55, 0.7, 0.01),  # D_RSI_Max1W>{w4}
            #         'w5': hp.quniform('w5', 1.0, 1.05, 0.002),  # (D_RSI_Max1W_Close/D_RSI_Max3M_Close > {w5})
            #         'w6': hp.quniform('w6', 1.01, 1.2, 0.01),  # (D_RSI_Max3M_MACD/D_RSI_Max1W_MACD>{w6})
            #         'w7': hp.quniform('w7', 0.95, 1.2, 0.01),  # (Close/D_RSI_Max3M_Close > {w7})
            #         'w8': hp.quniform('w8', 0.3, 0.7, 0.01),  # (D_RSI_MinT3 > {w8})
            #         'w9': hp.quniform('w9', 0.0, 0.3, 0.01),  # (D_CMF < {w9}
            #     },
            #     'init_vals': {
            #         'w1': 1.015,
            #         'w2': 0.78,
            #         'w3': 0.7,
            #         'w4': 0.6,
            #         'w5': 1.018,
            #         'w6': 1.05,
            #         'w7': 1.0,
            #         'w8': 0.5,
            #         'w9': 0.15,
            #     },
            #     # 'filter_template': f"(Volume*Price/Inflation_7>10e+8) & (time>='2014-01-01') & (time<='2026-01-01') & (VNINDEX_RSI_Max1W/VNINDEX_RSI > {w1}) & (VNINDEX_RSI_Max3M > {w2}) & (VNINDEX_RSI_Max1W < {w3}) & (VNINDEX_RSI_Max1W_Close/VNINDEX_RSI_Max3M_Close > {w4}) & (VNINDEX_RSI_Max3M_MACD/VNINDEX_RSI_Max1W_MACD>{w5}) & (VNINDEX_RSI_Max3M_MFI/VNINDEX_RSI_Max1W_MFI>{w6})"
            #     'filter_template': f"(time>='2000-01-01') & (time<='2025-01-01') "
            #                        "& (ticker=='VNINDEX') "
            #                        "& (D_RSI_Max1W/D_RSI > {w1})  & (D_RSI_Max3M > {w2}) "
            #                        "& (D_RSI_Max1W < {w3}) & (D_RSI_Max1W>{w4}) "
            #                        "& (D_RSI_Max1W_Close/D_RSI_Max3M_Close > {w5}) "
            #                        "& (D_RSI_Max3M_MACD/D_RSI_Max1W_MACD>{w6}) "
            #                        "& (D_MACDdiff < 0)  "
            #                        "& (Close/D_RSI_Max3M_Close > {w7}) "
            #                        "& (D_RSI_MinT3 > {w8}) "
            #                        "& (D_CMF < {w9})"
            # }
        }
        self.tickers = self.get_ticker_name(TICKER_PATH)

    @staticmethod
    def get_ticker_name(path):
        pd_ticker = pd.read_csv(path)
        tickers = list(pd_ticker['ticker'].unique())

        list_exits_ticker = [f.replace('.csv', '') for f in os.listdir(FPATH) if f.endswith('.csv')]
        tickers = [ticker for ticker in tickers if ticker in list_exits_ticker]

        return tickers

    def objective(self, params: Dict[str, Any], pattern_name):
        global RECORD
        pattern = self.patterns[pattern_name]

        filter = {
            "_PS1": "Price < 0",
            "~SellPattern": "(time>='2014-01-01') & (time<='2025-01-01') &" + pattern['filter_template'].format(
                **params)
        }

        filter_validate = {
            "_PS1": "Price < 0",
            "~SellPattern": "(time>='2025-01-01') & (time<='2026-01-01') &" + pattern['filter_template'].format(
                **params)
        }
        result = eval_filter_all_v2(filter, list_processed_ticker=self.tickers, CUTLOSS=1)
        # result = eval_filter_all_v2(filter, list_processed_ticker=['VNINDEX'], CUTLOSS=1)

        deal = result['deal']

        penalty = result['penalty']
        profit_expected = result['profit_expected']
        median_profit = result['median_profit']
        weighted_profit = result['weighted_profit']
        win_deal = result.get("win_deal", -500)

        # profit_ratio = (0.3 * weighted_profit + 0.3 * profit_expected + 0.3 * median_profit) / 100
        # profit_ratio = (0.5 * profit_expected + 0.5 * median_profit) / 100
        profit_ratio = (median_profit) / 100

        # for VNINDEX
        # loss = deal * win_deal
        # loss_formula = "deal * win_deal"

        loss_formula = "deal * (median_profit) / 100 * penalty"

        oginal_loss = deal * profit_ratio * penalty
        loss = max(oginal_loss, 0.0)

        log_data = {
            "pattern": pattern_name,
            "loss_formula": loss_formula,
            "loss": loss if not np.isinf(-loss) else -loss,
            "original_loss": oginal_loss if not np.isinf(-oginal_loss) else -oginal_loss,
            "deal": result.get("deal", 0.0),
            "profit_expected": result.get("profit_expected", 0.0),
            "median_profit": result.get("median_profit", 0.0),
            "weighted_profit": result.get("weighted_profit", 0.0),

            "win_deal": result.get("win_deal", 0.0),
            "loss_deal": result.get("loss_deal", 0.0),
            "hold_deal": result.get("hold_deal", 0.0),
            "cutloss_deal": result.get("cutloss_deal", 0.0),

            "win_quarter": result.get("win_quarter", 0.0),
            "winblock_20quarters": result.get("winblock_20quarters", 0.0),
            "winblock_24months": result.get("winblock_24months", 0.0),
            "trading_val": result.get("trading_val", 0.0),
            "p_trading_val": result.get("p_trading_val", 0.0),

            "profit_win": result.get("profit_win", 0.0),
            "profit_loss": result.get("profit_loss", 0.0),
            "profit_hold": result.get("profit_hold", 0.0),
            "profit_cutloss": result.get("profit_cutloss", 0.0),
            "holding_period": result.get("holding_period", 0.0),

            "penalty": result.get("penalty", 0.0),
        }
        px_key = ['P1W', 'P2W', 'P3W', 'P1M', 'P2M', 'P3M', 'P6M', 'P1Y', 'P2Y']
        log_data.update({px_key[i]: v for i, v in enumerate(result.get("PX", []))})
        print("------------------------------------------------------------------------------------")
        print(f'TRACKING_VERSION: {TRACK_VERSION}')
        print(log_data)
        print("------------------------------------------------------------------------------------")

        # Validate pattern
        log_validate = {}
        if loss > RECORD:
            RECORD = loss
            result_validate = eval_filter_all_v2(filter_validate, list_processed_ticker=self.tickers, CUTLOSS=1,
                                                 validate=True)

            log_validate = {
                "deal_validate": result_validate.get("deal", 0.0),
                "profit_expected_validate": result_validate.get("profit_expected", 0.0),
                "median_profit_validate": result_validate.get("median_profit", 0.0),
                "weighted_profit_validate": result_validate.get("weighted_profit", 0.0),

                "win_deal_validate": result_validate.get("win_deal", 0.0),
                "loss_deal_validate": result_validate.get("loss_deal", 0.0),
                "hold_deal_validate": result_validate.get("hold_deal", 0.0),
                "cutloss_deal_validate": result_validate.get("cutloss_deal", 0.0),

                "profit_win_validate": result_validate.get("profit_win", 0.0),
                "profit_loss_validate": result_validate.get("profit_loss", 0.0),
                "profit_hold_validate": result_validate.get("profit_hold", 0.0),
                "profit_cutloss_validate": result_validate.get("profit_cutloss", 0.0),
            }

        params = {
            k: float(v) if isinstance(v, (int, np.integer, np.floating)) else v
            for k, v in params.items()
        }

        log_data.update(log_validate)
        log_data.update(params)
        log_data.update({'pattern_formula': pattern['filter_template'].format(**params)})

        # Append new log data to the CSV file
        LOG_FILE = f"{PATH}/trials_sell_{pattern_name}_{USERNAME}_{PATTERN_VERSION}_{TRACK_VERSION}.csv"
        if os.path.exists(LOG_FILE):
            df = pd.read_csv(LOG_FILE)
        else:
            df = pd.DataFrame(columns=list(log_data.keys()))

        new_df = pd.DataFrame([log_data])
        for col in df.columns:
            if col in new_df.columns:
                if df[col].dtype == 'int64':
                    new_df[col] = new_df[col].fillna(0).astype(df[col].dtype)
                elif df[col].dtype == 'float64':
                    new_df[col] = new_df[col].fillna(0.0).astype(df[col].dtype)
                else:
                    new_df[col] = new_df[col].fillna('').astype(df[col].dtype)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(LOG_FILE, index=False)

        if np.isinf(loss):
            return {'loss': np.inf, 'status': STATUS_OK}

        return {'loss': -loss, 'status': STATUS_OK}

    def cleanup_stuck_jobs(self):
        client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
        collection = client["hyperopt_db"]["jobs"]

        query_broken_jobs = {
            '$or': [
                {'result.status': 'new'},
                # {'spec': None},
                # {'spec': {}}
            ]
        }
        collection.delete_many(query_broken_jobs)

    def clear_all_cache(self):
        memory.clear()
        redis_cache.clear_cache()

    def tune_pattern(self, pattern_name, max_evals=1000):
        if pattern_name not in self.patterns:
            raise ValueError(f"Pattern {pattern_name} not found")

        pattern = self.patterns[pattern_name]
        trial_path = f"tuning/sell_pattern/trials_sell_{pattern_name}_{PATTERN_VERSION}_{TRACK_VERSION}.pkl"
        os.makedirs(os.path.dirname(trial_path), exist_ok=True)

        # if os.path.exists(trial_path):
        #     trials = pickle.load(open(trial_path, "rb"))
        # else:
        #     trials = generate_trials_to_calculate(pattern['init_vals'])

        # Parallelization
        self.cleanup_stuck_jobs()
        self.clear_all_cache()

        trials_name = f"trials_sell_{pattern_name}_{PATTERN_VERSION}_{TRACK_VERSION}"
        trials = MongoTrials(f'mongo://{MONGO_HOST}:{MONGO_PORT}/hyperopt_db/jobs', exp_key=trials_name)

        # For debugging
        print("Debugging objective function")
        self.objective(self.patterns[pattern_name]['init_vals'], pattern_name)

        objective_fn = partial(self.objective, pattern_name=pattern_name)
        best = fmin(
            fn=objective_fn,
            space=pattern['search_space'],
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=trials,
            rstate=np.random.default_rng(42),
            # early_stop_fn=no_progress_loss(700),
            # trials_save_file=makedirs
        )
        print(f"Best parameters for {pattern_name}:", best)

        # Parallelization
        trials = MongoTrials(f'mongo://{MONGO_HOST}:{MONGO_PORT}/hyperopt_db/jobs', exp_key=trials_name)
        filtered_trials = [t for t in trials.trials if t['result'].get('status') == 'ok']
        with open(trial_path, 'wb') as f:
            pickle.dump(filtered_trials, f)

        return best

    def tune_multiple_patterns(self, pattern_names, max_evals=1000):
        results = {}
        for pattern_name in pattern_names:
            print(f"\nTuning pattern: {pattern_name}")
            results[pattern_name] = self.tune_pattern(pattern_name, max_evals)
        return results


# ============================================================================
# POPULATE SELL_PATTERNS - Export pattern configs for other modules
# ============================================================================
# Create a temporary instance to get the pattern definitions
_temp_tuner = SellPatternTuner()
SELL_PATTERNS = _temp_tuner.patterns.copy()
del _temp_tuner  # Clean up

# Export individual pattern configs for backward compatibility
ma21_config = SELL_PATTERNS.get('MA21', {})
ma31_config = SELL_PATTERNS.get('MA31', {})
ma41_config = SELL_PATTERNS.get('MA41', {})
s13_config = SELL_PATTERNS.get('S13', {})
sellbv_config = SELL_PATTERNS.get('SellBV', {})
sellbv2_config = SELL_PATTERNS.get('SellBV2', {})
sellpe_config = SELL_PATTERNS.get('SellPE', {})
sellresistance_config = SELL_PATTERNS.get('SellResistance', {})
sellresistance1m_config = SELL_PATTERNS.get('SellResistance1M', {})
sellresistance1y_config = SELL_PATTERNS.get('SellResistance1Y', {})
beardvg2_config = SELL_PATTERNS.get('BearDvg2', {})
sellvolmax_config = SELL_PATTERNS.get('SellVolMax', {})
# Note: BearDvgVNI is commented out in the class, so it won't be in SELL_PATTERNS
# If you need it, uncomment it in the SellPatternTuner.__init__() method
beardvgvni_config = {
    'filter_template': "(time>='2000-01-01') & (time<='2025-01-01') "
                       "& (ticker=='VNINDEX') "
                       "& (D_RSI_Max1W/D_RSI > {w1})  & (D_RSI_Max3M > {w2}) "
                       "& (D_RSI_Max1W < {w3}) & (D_RSI_Max1W>{w4}) "
                       "& (D_RSI_Max1W_Close/D_RSI_Max3M_Close > {w5}) "
                       "& (D_RSI_Max3M_MACD/D_RSI_Max1W_MACD>{w6}) "
                       "& (D_MACDdiff < 0)  "
                       "& (Close/D_RSI_Max3M_Close > {w7}) "
                       "& (D_RSI_MinT3 > {w8}) "
                       "& (D_CMF < {w9})"
}
