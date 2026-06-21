import os
import pickle
import sys
from datetime import timedelta
from typing import List, Dict, Optional, Any

import numpy as np
import pandas as pd
from hyperopt import fmin, tpe, STATUS_OK
from hyperopt.mongoexp import MongoTrials
from joblib import Memory
from pathos.multiprocessing import ProcessingPool as Pool
from pymongo import MongoClient

from core_utils.base_eval import PreProcess, Simulation, AllEval
from core_utils.constant import REDIS_HOST, MONGO_HOST, MONGO_PORT, JOBLIB_CACHE_DIR
from core_utils.redis_cache import EvalRedis
import warnings

warnings.simplefilter(action='ignore')

# Đường dẫn và biến toàn cục
current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = current_dir.replace("/tuning/buy_pattern", "")
os.chdir(current_dir)
sys.path.insert(0, current_dir)

memory = Memory(location=f'{JOBLIB_CACHE_DIR}_tuning', verbose=0)
memory.reduce_size(bytes_limit=3e9, age_limit=timedelta(days=1))
redis_cache = EvalRedis(host=REDIS_HOST, db=1)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

# FPATH = os.path.join(BASE_DIR, 'ticker_v1a_tuning')
FPATH = os.path.join(BASE_DIR, 'ticker_v1a')
PATH = os.path.join(BASE_DIR, 'tuning/hyperopt_results')

RANKING = 'trading_daily'
INIT_ASSETS = 10e9
INIT_SLOTS = 1
NUM_BLOCK = 30
NUM_DEAL_THRESHOLD = 5
SI_TYPE = 'adjust_cash'

NUM_PROCS = 20

TRACK_VERSION = "24/12/2025:0"
PATTERN_VERSION = "v1"


def eval_filter_all_v2(dict_filter, cutloss=0.15, utilize_percent=1.0):
    """ Return dataframe of profit
        pdp: dataframe of profit
        pdx: dataframe of historical hit
        pdy: dataframe of latest hit
    """
    num_procs = NUM_PROCS

    def eval(ticker):
        try:
            pdxx = pd.read_csv(f'{FPATH}/{ticker}.csv')
            eval_ticker = AllEval(ticker, pdxx, dict_filter, cutloss=cutloss, cache_service=redis_cache)

            params = {
                'nums_block': NUM_BLOCK,
            }
            res = eval_ticker.get_deal(**params)
            return res
        except Exception as error:
            # print(f"Error: {ticker}: {error}")
            pass

    # list_processed_ticker = [f.replace('.csv', '') for f in os.listdir(FPATH) if f.endswith('.csv')]
    list_processed_ticker = ['VNINDEX']

    with Pool(num_procs) as p:
        lres = p.map(eval, list_processed_ticker)

    try:
        lres = [res for res in lres if res is not None and not res.empty]

        if not lres:
            raise ValueError("No valid results to concatenate")

        pd_deal = pd.concat(lres, axis=0).reset_index(drop=True)
        if pd_deal.shape[0] < NUM_DEAL_THRESHOLD:
            print(pd_deal.shape[0])
            raise ValueError(f"Insufficient data: {pd_deal.shape[0]}")

        df_process = PreProcess()
        pd_deal = df_process.deals(pd_deal)

        deal_result = {}

        pd_deal['month'] = pd_deal['time'].str[:7]
        # _pdd_d = df_process.group_by(pd_deal, ['filter'])
        _pdd_q = df_process.group_by(pd_deal, ['filter', "quarter"])
        _pdd_m = df_process.group_by(pd_deal, ['filter', "month"])

        # other
        deal_result['deal'] = pd_deal['profit'].count()
        deal_result['profit_expected'] = pd_deal['profit'].mean()
        deal_result['profit_win'] = pd_deal['p_win'].mean()
        deal_result['profit_loss'] = pd_deal['p_loss'].mean()
        deal_result['profit_hold'] = pd_deal['p_hold'].mean()
        deal_result['profit_cutloss'] = pd_deal['p_cutloss'].mean()
        deal_result['holding_period'] = pd_deal['holding_period'].mean()

        # win/loss/hold/cutloss deal
        deal_result['win_deal'] = pd_deal['count_win'].count() / pd_deal['deal'].count()
        deal_result['loss_deal'] = pd_deal['count_loss'].count() / pd_deal['deal'].count()
        deal_result['hold_deal'] = pd_deal['count_hold'].count() / pd_deal['deal'].count()
        deal_result['hold_win_deal'] = pd_deal['count_hold_win'].count() / pd_deal['deal'].count()
        deal_result['hold_loss_deal'] = pd_deal['count_hold_loss'].count() / pd_deal['deal'].count()
        deal_result['cutloss_deal'] = pd_deal['count_cutloss'].count() / pd_deal['deal'].count()

        # win_quarter
        win = _pdd_q[(_pdd_q['count_win'] + _pdd_q['count_hold_win']) >= (
                _pdd_q['count_loss'] + _pdd_q['count_cutloss'] + _pdd_q['count_hold_loss'])].shape[0]
        loss = _pdd_q[(_pdd_q['count_win'] + _pdd_q['count_hold_win']) <= (
                _pdd_q['count_loss'] + _pdd_q['count_cutloss'] + _pdd_q['count_hold_loss'])].shape[0]
        deal_result['win_quarter'] = win / sum([win, loss]) if (win + loss) > 0 else 0

        # winblock_20quarters
        df_tail = _pdd_q.tail(21).iloc[:-1]
        win_tail = df_tail[(df_tail['count_win'] + df_tail['count_hold_win']) >= (
                df_tail['count_loss'] + df_tail['count_cutloss'] + df_tail['count_hold_loss'])].shape[0]
        loss_tail = df_tail[(df_tail['count_win'] + df_tail['count_hold_win']) <= (
                df_tail['count_loss'] + df_tail['count_cutloss'] + df_tail['count_hold_loss'])].shape[0]

        deal_result['winblock_20quarters'] = win_tail / sum([win_tail, loss_tail]) if (win_tail + loss_tail) > 0 else 0

        # winblock_24months
        df_tail = _pdd_m.tail(24)
        win_tail = df_tail[(df_tail['count_win'] + df_tail['count_hold_win']) >= (
                df_tail['count_loss'] + df_tail['count_cutloss'] + df_tail['count_hold_loss'])].shape[0]
        loss_tail = df_tail[(df_tail['count_win'] + df_tail['count_hold_win']) <= (
                df_tail['count_loss'] + df_tail['count_cutloss'] + df_tail['count_hold_loss'])].shape[0]

        deal_result['winblock_24months'] = win_tail / sum([win_tail, loss_tail]) if (win_tail + loss_tail) > 0 else 0

        # SIMULATION
        simulation = Simulation(start_date='2000-01-01', end_date='2026-01-01',
                                initial_assets=INIT_ASSETS * utilize_percent,
                                max_deals=INIT_SLOTS, cache_service=memory, num_proc=num_procs, fpath=FPATH)
        si_result = simulation.run_fast(pd_deal, iterate=30, s_type=SI_TYPE)

        # windeal, win_quarter
        penalty = 1
        if (deal_result['win_quarter'] < 0.5) or (deal_result['winblock_20quarters'] < 0.5) or (
                deal_result['winblock_24months'] < 0.5) or (deal_result['win_deal'] < 0.5):
            penalty *= np.min(
                [deal_result['win_quarter'], deal_result['winblock_20quarters'], deal_result['winblock_24months'],
                 deal_result['win_deal']]) / 0.5

        # penalty = (np.min([win_quarter, winblock_20quarters, winblock_24months, win_deal]) > 0.5)

        ranking_point = 0.3 * si_result['BuyPattern']['return'] + \
                        0.3 * deal_result['win_deal'] * 100 + \
                        0.15 * deal_result['win_quarter'] * 100 + \
                        0.1 * deal_result['winblock_20quarters'] * 100 + \
                        0.05 * deal_result['winblock_24months'] * 100 + \
                        0.1 * deal_result['profit_expected'] * 100

        return {
            'si_return': si_result['BuyPattern']['return'],
            'si_std': si_result['BuyPattern']['return_std'],
            'si_deals': si_result['BuyPattern']['match_deals'],
            'si_profit': si_result['BuyPattern']['profit'],
            'si_cash_profit': si_result['BuyPattern']['cash_profit'],
            'si_utilization': si_result['BuyPattern']['utilization'] * 100,
            'si_win_deal': si_result['BuyPattern']['win_deal'],
            'si_win_quarter': si_result['BuyPattern']['win_quarter'],
            'si_peak': si_result['BuyPattern']['peak_number_deals'],
            "si_ticker_diversity": si_result['BuyPattern']['set_ticker'],
            'si_quarter_ticker_diversity': si_result['BuyPattern']['set_quarter_ticker'],

            'win_deal': deal_result['win_deal'] * 100,
            'loss_deal': deal_result['loss_deal'] * 100,
            'hold_deal': deal_result['hold_deal'] * 100,
            'hold_win_deal': deal_result['hold_win_deal'] * 100,
            'hold_loss_deal': deal_result['hold_loss_deal'] * 100,
            'cutloss_deal': deal_result['cutloss_deal'] * 100,

            'win_quarter': deal_result['win_quarter'] * 100,
            'winblock_20quarters': deal_result['winblock_20quarters'] * 100,
            'winblock_24months': deal_result['winblock_24months'] * 100,
            'deal': deal_result['deal'],
            'profit_expected': deal_result['profit_expected'],
            'profit_win': deal_result['profit_win'],
            'profit_loss': deal_result['profit_loss'],
            'profit_hold': deal_result['profit_hold'],
            'profit_cutloss': deal_result['profit_cutloss'],
            'holding_period': deal_result['holding_period'],

            'ranking_point': ranking_point,
            'penalty': penalty,
            'status': STATUS_OK
        }

    except Exception as e:
        print(f"Error in eval_filter_all_v2: {str(e)}")
        return {
            'si_return': np.inf,
            'win_deal': np.inf,
            'hold_win_deal': np.inf,
            'profit_expected': np.inf,
            'deal': np.inf,
            'penalty': -1,
            'status': STATUS_OK
        }
        # return {
        #     'si_return': -np.inf,
        #     'win_deal': -np.inf,
        #     'penalty': -1.0,
        #     'status': STATUS_OK
        # }


class PatternTuningManager:
    def __init__(self, pattern_name: str, utilize_percent: float, cutloss: float, search_space: Dict[str, Any],
                 init_vals: Dict[str, Any], filter_template: str,
                 sell_filters: Optional[Dict[str, str]], sell_search_space: Dict[str, Any],
                 sell_init_vals: Dict[str, Any], sell_mapping: Dict[str, str]):

        search_space.update(sell_search_space)
        init_vals.update(sell_init_vals)
        self.pattern_name = pattern_name
        self.utilize_percent = utilize_percent
        self.cutloss = cutloss

        self.search_space = search_space
        self.init_vals = init_vals
        self.filter_template = filter_template
        self.sell_filters = sell_filters
        self.sell_mapping = sell_mapping

    def create_filter(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Tạo filter từ params"""
        filter_dict = {
            "_BuyPattern": self.filter_template.format(**params)
        }
        # Thêm các filter bán nếu có
        if self.sell_filters:
            filter_dict.update(self.sell_filters)

        b2s = ""
        for key, value in self.sell_mapping.items():
            if params[key] > 0:
                b2s += f"{value}, "

        filter_dict['$BuyPattern'] = b2s[:-2]

        return filter_dict

    def objective(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hàm objective cho hyperopt"""
        filter_dict = self.create_filter(params)
        # print(filter_dict)
        result = eval_filter_all_v2(dict_filter=filter_dict, utilize_percent=self.utilize_percent, cutloss=self.cutloss)

        si_return = result['si_return']
        profit_expected = result['profit_expected']
        win_deal = result['win_deal']
        hold_win_deal = result['hold_win_deal']
        penalty = result['penalty']
        deal = result['deal']

        # loss = (si_return * 1.5 + win_deal * 0.5) * penalty
        # loss_formula = "(si_return * 1.5 + (win_deal) * 0.5) * penalty"

        loss = (si_return * 1.5 + win_deal * 0.1 + 0.2 * deal) * penalty
        loss_formula = "(si_return * 1.5 + win_deal * 0.1 + 0.2 * deal) * penalty"

        # loss = (si_return * 1.5 + windeal * 0.5) * penalty
        # loss_formula = "(si_return * 1.5 + windeal * 0.5) * penalty"
        log_data = {
            "pattern": self.pattern_name,
            "loss_formula": loss_formula,
            "simulate_type": SI_TYPE,
            "initial_assets": INIT_ASSETS * self.utilize_percent,
            "initial_slots": INIT_SLOTS,
            "initial_cutloss": self.cutloss,
            "loss": loss if not np.isinf(-loss) else -loss,

            "deal": result.get("deal", 0.0),
            "si_return": result.get("si_return", 0.0),
            "profit_expected": result.get("profit_expected", 0.0),

            "win_deal": result.get("win_deal", 0.0),
            "loss_deal": result.get("loss_deal", 0.0),
            "hold_deal": result.get("hold_deal", 0.0),
            "hold_win_deal": result.get("hold_win_deal", 0.0),
            "hold_loss_deal": result.get("hold_loss_deal", 0.0),
            "cutloss_deal": result.get("cutloss_deal", 0.0),

            "win_quarter": result.get("win_quarter", 0.0),
            "winblock_20quarters": result.get("winblock_20quarters", 0.0),
            "winblock_24months": result.get("winblock_24months", 0.0),
            "ranking_point": result.get("ranking_point", 0.0),

            "profit_win": result.get("profit_win", 0.0),
            "profit_loss": result.get("profit_loss", 0.0),
            "profit_hold": result.get("profit_hold", 0.0),
            "profit_cutloss": result.get("profit_cutloss", 0.0),
            "holding_period": result.get("holding_period", 0.0),

            "si_deals": result.get("si_deals", 0.0),
            "si_profit": result.get("si_profit", 0.0),
            "si_cash_profit": result.get("si_cash_profit", 0.0),
            "si_utilization": result.get("si_utilization", 0.0),
            "si_win_deal": result.get("si_win_deal", 0.0),
            "si_win_quarter": result.get("si_win_quarter", 0.0),

            "si_peak_number_deal": result.get("si_peak", 0.0),
            "si_ticker_diversity": result.get("si_ticker_diversity", 0.0),
            "si_quarter_ticker_diversity": result.get("si_quarter_ticker_diversity", 0.0),

        }
        print("------------------------------------------------------------------------------------")
        print(f'TRACKING_VERSION: {TRACK_VERSION}')
        print(log_data)
        print("------------------------------------------------------------------------------------")

        log_data.update(params)
        log_data.update({'pattern_formula': filter_dict['_BuyPattern']})
        log_data.update({'map_pattern_formula': filter_dict['$BuyPattern']})

        LOG_FILE = f"{PATH}/trials_buy_{self.pattern_name}_{PATTERN_VERSION}.csv"
        if os.path.exists(LOG_FILE):
            df = pd.read_csv(LOG_FILE)
        else:
            df = pd.DataFrame(columns=list(log_data.keys()))

        new_df = pd.DataFrame([log_data])
        for col in df.columns:
            if col in new_df.columns:
                if df[col].dtype == 'int64':
                    new_df[col] = new_df[col].replace([np.inf, -np.inf], 0).fillna(0).astype(df[col].dtype)
                elif df[col].dtype == 'float64':
                    new_df[col] = new_df[col].fillna(0.0).astype(df[col].dtype)
                else:
                    new_df[col] = new_df[col].fillna('').astype(df[col].dtype)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(LOG_FILE, index=False)

        return {'loss': -loss, 'status': result['status']}

    def cleanup_stuck_jobs(self):
        client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
        collection = client["hyperopt_db"]["jobs"]

        query_broken_jobs = {
            '$or': [
                {'result.status': 'new'},
            ]
        }
        collection.delete_many(query_broken_jobs)

    @staticmethod
    def clear_all_cache():
        memory.clear()
        redis_cache.clear_cache()

    def run_tuning(self, max_evals: int = 1000, trials_file: Optional[str] = None) -> Dict[str, Any]:
        """Chạy tuning cho pattern"""
        if trials_file is None:
            trials_file = f"{PATH}/trials_buy_{self.pattern_name}_{PATTERN_VERSION}.pkl"
        os.makedirs(os.path.dirname(trials_file), exist_ok=True)

        # Parallelization
        self.cleanup_stuck_jobs()
        self.clear_all_cache()

        trials_name = f"trials_buy_{self.pattern_name}_{PATTERN_VERSION}"
        trials = MongoTrials(f'mongo://{MONGO_HOST}:{MONGO_PORT}/hyperopt_db/jobs', exp_key=trials_name)

        # For debugging
        print("Debugging objective function")
        self.objective(self.init_vals)

        best = fmin(
            fn=self.objective,
            space=self.search_space,
            algo=tpe.suggest,
            max_evals=max_evals,
            trials=trials,
            rstate=np.random.default_rng(42),
        )

        # Parallelization
        # trials = MongoTrials(f'mongo://{MONGO_HOST}:{MONGO_PORT}/hyperopt_db/jobs', exp_key=trials_name)
        # filtered_trials = [t for t in trials.trials if t['result'].get('status') == 'ok']
        # with open(trials_file, 'wb') as f:
        #     pickle.dump(filtered_trials, f)
        return best


def run_multiple_patterns(pattern_configs: List[Dict[str, Any]], sell_config: Dict[str, Any], max_evals: int) -> \
        Dict[str, Dict[str, Any]]:
    """
    Chạy tuning cho nhiều pattern cùng lúc
    
    Args:
        pattern_configs: Danh sách cấu hình cho các pattern
        max_evals: Số lần đánh giá tối đa cho mỗi pattern
        
    Returns:
        Dict chứa kết quả tốt nhất cho mỗi pattern
    """
    results = {}

    for config in pattern_configs:
        print(f"\nTuning pattern: {config['pattern_name']}")
        manager = PatternTuningManager(**config, **sell_config)
        best_params = manager.run_tuning(max_evals=max_evals)
        results[config['pattern_name']] = best_params

    return results
