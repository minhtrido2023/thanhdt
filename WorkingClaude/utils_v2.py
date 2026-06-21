import json
import time
from datetime import datetime
from functools import lru_cache
from importlib import import_module
from multiprocessing import shared_memory, Pool as StandardPool
import os
import numpy as np
import pandas as pd
from joblib import Memory
from pathos.multiprocessing import ProcessingPool as PathosPool

from core_utils.constant import JOBLIB_CACHE_DIR, NUM_PROCESS, FPATH, MARKET_DICT_FILTER

memory = Memory(location=JOBLIB_CACHE_DIR, verbose=0)
VNINDEX_PATH = 'ticker_v1a/VNINDEX.csv'
SIMULATION_VERSION_OPTIONS = ('v1.5', 'v1.6', 'v2')
DEFAULT_SIMULATION_VERSION = 'v1.6'

_SIMULATION_BACKENDS = {
    'v1.5': {
        'simulation_module': 'core_utils.simulation_v1_5',
        'score_module': 'core_utils.wrap_score_1_5',
    },
    'v1.6': {
        'simulation_module': 'core_utils.simulation_v1_6',
        'score_module': 'core_utils.wrap_score_1_6',
    },
    'v2': {
        'simulation_module': 'core_utils.simulation_v2a',
        # Keep the score pipeline compatible with the existing hit-ranking flow.
        'score_module': 'core_utils.wrap_score_1_6',
    },
}


@lru_cache(maxsize=None)
def get_simulation_backend(simulation_version: str):
    version = simulation_version if simulation_version in _SIMULATION_BACKENDS else DEFAULT_SIMULATION_VERSION
    backend = _SIMULATION_BACKENDS[version]
    simulation_module = import_module(backend['simulation_module'])
    score_module = import_module(backend['score_module'])
    return {
        'version': version,
        'wrapper_class': getattr(simulation_module, 'WrapperSimulation'),
        'score_manager_class': getattr(score_module, 'ScoreManager'),
    }


def _to_iso_date(value):
    if pd.isna(value):
        return None
    return pd.Timestamp(value).strftime('%Y-%m-%d')


def _to_scalar(value):
    """Safely convert array-like values to scalar."""
    if value is None:
        return None
    if isinstance(value, (list, tuple, np.ndarray, pd.Series)):
        return value[0] if len(value) > 0 else None
    return value


def _build_simulation_log_jsonl(transactions_df, portfolio_logs_df, positions_df):
    if transactions_df.empty or portfolio_logs_df.empty:
        return ""

    tx = transactions_df.copy()
    for optional_col in ('buy_pattern', 'sell_pattern'):
        if optional_col not in tx.columns:
            tx[optional_col] = None
    tx['date'] = pd.to_datetime(tx['ymd'])
    tx['action'] = tx['action'].str.lower().str.strip()

    logs = portfolio_logs_df.copy()
    logs['date'] = pd.to_datetime(logs['ymd'])
    logs = logs.sort_values('date').drop_duplicates('date', keep='last')
    logs['utilization'] = np.where(logs['nav'] > 0, 1 - (logs['cash'] / logs['nav']), 0.0)
    state_by_date = logs.set_index('date')[['cash', 'nav', 'utilization']].to_dict('index')

    positions = positions_df.copy()
    if not positions.empty:
        positions['open_date'] = pd.to_datetime(positions['open_date'])
        positions['close_date'] = pd.to_datetime(positions['close_date'])
        positions_by_holding = positions.set_index('holding_id').to_dict('index')
    else:
        positions_by_holding = {}

    entries = []
    for tx_row in tx.itertuples(index=False):
        state = state_by_date.get(tx_row.date)
        if state is None:
            continue

        total_assets = float(state['nav'])
        if not positions.empty:
            active_positions = positions[
                (positions['open_date'] <= tx_row.date) &
                (positions['close_date'] > tx_row.date)
                ]
        else:
            active_positions = pd.DataFrame()

        active_deals = []
        for active in active_positions.itertuples(index=False):
            investment = float(getattr(active, 'buy_notional', 0.0) or 0.0)
            active_deals.append({
                'ticker': active.ticker,
                'investment': investment,
                'investment_ratio': ((investment / total_assets) * 100) if total_assets else 0.0,
                'buy_date': _to_iso_date(active.open_date),
            })

        amount = float(tx_row.buy_amount if tx_row.action == 'buy' else tx_row.sell_amount)
        num_shares = (amount / tx_row.adj_price) if tx_row.adj_price else None
        entry = {
            'action': tx_row.action.capitalize(),
            'date': _to_iso_date(tx_row.date),
            'ticker': tx_row.ticker,
            'num_of_shares_held': num_shares,
            'remaining_cash': round(float(state['cash']), 2),
            'utilization': float(state['utilization']),
            'total_assets': total_assets,
            'total_active_deals': len(active_deals),
            'total_active_tickers': len({deal['ticker'] for deal in active_deals}),
            'active_deals': active_deals,
        }

        filter_name = tx_row.buy_pattern if tx_row.action == 'buy' else tx_row.sell_pattern
        filter_name = _to_scalar(filter_name)
        if pd.notna(filter_name):
            entry['filter'] = filter_name

        if tx_row.action == 'buy':
            entry['investment'] = round(amount, 2)
            entry['price'] = float(tx_row.adj_price)
        else:
            position = positions_by_holding.get(tx_row.holding_id)
            if position:
                entry['buy_date'] = _to_iso_date(position.get('open_date'))
                holding_days = position.get('holding_days')
                entry['holding_days'] = int(holding_days) if pd.notna(holding_days) else None
                profit_ratio = position.get('ret_notional')
                entry['profit_percentage'] = round(float(profit_ratio) * 100, 2) if pd.notna(profit_ratio) else None

        entries.append(json.dumps(entry))

    return '\n'.join(entries)


@memory.cache
def calc_annual_profit(fpath):
    df = pd.read_csv(fpath, usecols=['time', 'Close'])
    df['date'] = pd.to_datetime(df['time'])
    df['year'] = df['date'].dt.year

    if 'daily_return' not in df.columns:
        df['daily_return'] = df['Close'].pct_change()

    df = df.dropna(subset=['daily_return'])

    # group by year
    grouped = df.groupby('year')

    # Geometric mean (annualized)
    ann_profit = []
    for year, g in grouped:
        n_days = (g['date'].max() - g['date'].min()).days + 1
        geom_return = np.prod(1 + g['daily_return'].values) ** (365.25 / n_days) - 1
        ann_profit.append((year, geom_return))

    ann_df = pd.DataFrame(ann_profit, columns=['year', 'ann_profit'])

    # Calculate standard deviation
    valid_profits = ann_df['ann_profit'].dropna()
    ann_profit_std = valid_profits.std(ddof=1) if len(valid_profits) > 1 else np.nan

    return ann_df, ann_profit_std


def process_ticker(args):
    ticker, indicators_used, start_time = args
    try:

        cols_in_file = pd.read_csv(f'{FPATH}/{ticker}.csv', nrows=0).columns.tolist()
        valid_cols = [c for c in indicators_used if c in cols_in_file]

        df = pd.read_csv(f'{FPATH}/{ticker}.csv', usecols=valid_cols)
        df.rename(columns={'Close': 'close', 'Open': 'open', 'Price': 'price', 'Volume': 'volume',
                           'Volume_1M_P50': 'volume_1m_p50',
                           'Volume_3M_P50': 'volume_3m_p50'}, inplace=True)

        if start_time is not None:
            ticker_times = pd.to_datetime(df['time'], errors='coerce')
            date_mask = ticker_times.notna() & (ticker_times >= start_time)
            # if end_time is not None:
            #     date_mask &= ticker_times <= end_time
            df = df.loc[date_mask].copy()

        return df
    except Exception as error:
        # Log exception in child process but also return to parent
        print(f"Error processing ticker {ticker}: {error}")


@memory.cache
def prepare_core_data() -> pd.DataFrame:
    """
    Prepare core data for simulation.
    """
    df_core = None
    start_time = None
    if os.path.exists('webui/df_core_v1_5.csv'):
        df_core = pd.read_csv('webui/df_core_v1_5.csv')

    if df_core is not None and not df_core.empty:
        list_processed_ticker = df_core['ticker'].unique().tolist()
        latest_time = pd.to_datetime(df_core['time'], errors='coerce').max()
        if pd.notna(latest_time):
            start_time = latest_time - pd.Timedelta(days=5)

    else:
        list_processed_ticker = [f.replace('.csv', '') for f in os.listdir(FPATH) if f.endswith('.csv')]
        df_core = pd.DataFrame()
    num_procs = NUM_PROCESS
    # indicators_used = ['time', 'ticker', 'Close', 'Volume', 'Price', 'Volume_1M_P50', 'Volume_3M_P50', 'Open_1D',
    #                    'CF_OA_5Y', 'Oshares', 'FSCORE', 'NP_P0', 'PCF', 'PB', 'PE', 'ROE5Y', 'ROE_Min3Y']
    indicators_used = ['time', 'ticker', 'Close', 'Open', 'Volume', 'Price', 'Volume_1M_P50', 'Volume_3M_P50']

    lres = []
    # list_processed_ticker = ['HPG', 'FPT']
    with PathosPool(num_procs) as p:
        args = [(ticker, indicators_used, start_time) for ticker in list_processed_ticker]
        output = p.amap(process_ticker, args)

    lres.extend(output.get())
    lres = [res for res in lres if res is not None and not res.empty]
    if lres:
        pd_all = pd.concat(lres, axis=0)
        df_core = pd.concat([df_core, pd_all], axis=0).drop_duplicates(subset=['time', 'ticker'],
                                                                       keep='first').reset_index(drop=True)
    df_core.to_csv('webui/df_core_v1_5.csv', index=False)
    return df_core


# ============================================================================
# Worker function for shared memory multiprocessing
# ============================================================================
def _shuffle_by_date(pd_deals: pd.DataFrame, seed: int, copy_data: bool = True) -> pd.DataFrame:
    """
    Shuffle DataFrame by date with random ordering within each date.

    Memory-optimized version that can optionally avoid copying the DataFrame.

    Args:
        pd_deals: DataFrame to shuffle
        seed: Random seed for reproducibility
        copy_data: If True, copy DataFrame before modification (safer but uses more memory)
                  If False, modify in-place (memory efficient but modifies original)

    Returns:
        Shuffled DataFrame
    """
    rng = np.random.RandomState(seed)

    if copy_data:
        # Create copy only when necessary (default behavior for safety)
        pd_deals = pd_deals.copy()

    # Use more memory-efficient random generation
    pd_deals["_rand_order"] = rng.rand(len(pd_deals)).astype(np.float32)

    # Sort in-place to avoid additional memory allocation
    pd_deals.sort_values(
        by=["ymd", "score", "_rand_order"],
        ascending=[True, False, True],
        inplace=True
    )

    # Drop temporary column and reset index in-place
    pd_deals.drop(columns=["_rand_order"], inplace=True)
    pd_deals.reset_index(drop=True, inplace=True)

    return pd_deals


def _worker_process_simulate(args):
    """
    Worker function for multiprocessing with shared memory support.

    This function is defined at module level (not inside class) to be picklable.
    It reconstructs the DataFrame from shared memory and runs the simulation.

    Args:
        args: Tuple of (seed, shm_name, df_metadata, simulate_config)
            - seed: Random seed for this simulation run
            - shm_name: Name of shared memory block containing DataFrame data
            - df_metadata: Dict with DataFrame structure info (columns, dtypes, shape)
            - simulate_config: Simulation configuration dict

    Returns:
        Dict with simulation results
    """
    seed, shm_name, df_metadata, simulate_config, simulation_version, start_date, period = args

    # Reconstruct DataFrame from shared memory (zero-copy)
    shm = shared_memory.SharedMemory(name=shm_name)
    try:
        # Reconstruct numpy array from shared memory buffer
        np_array = np.ndarray(
            df_metadata['shape'],
            dtype=df_metadata['dtype'],
            buffer=shm.buf
        )

        # Reconstruct DataFrame with proper columns and dtypes
        df_datas = pd.DataFrame(np_array, columns=df_metadata['columns'])

        # Restore categorical dtypes for memory efficiency
        for col, kind in df_metadata['column_dtypes'].items():
            if kind == 'category':
                cats = df_metadata['categories_map'][col]
                codes = df_datas[col].astype('int32')
                df_datas[col] = pd.Categorical.from_codes(codes, categories=cats)

        start_period = (pd.to_datetime(start_date) + pd.Timedelta(seed, "d"))
        end_period = (pd.to_datetime(start_period) + pd.Timedelta(period, "d"))
        mask = (df_datas["time"] >= start_period) & (df_datas["time"] <= end_period)

        df_datas = df_datas.loc[mask]

        # Set random seed for reproducibility
        np.random.seed(seed)

        # Shuffle data efficiently
        df_shuffled = _shuffle_by_date(df_datas, seed)

        # Run simulation
        simulator = get_simulation_backend(simulation_version)['wrapper_class'](simulate_config)
        simulator.run(df_shuffled)

        # Get results
        ann_index, _ = calc_annual_profit(VNINDEX_PATH)
        stats = simulator.stats(ann_index)

        # Extract results
        # pos_df = stats['stats_tx']['pos']
        # set_ticker = pos_df['ticker'].unique().tolist()
        # set_quarter_ticker = list(set(zip(pos_df['ticker'], pos_df['open_quarter'])))

        result = stats['stats_log']
        result.update(stats['stats_tx']['tmetrics'])
        # result['set_ticker'] = set_ticker
        # result['set_quarter_ticker'] = set_quarter_ticker

        return {'output': result}

    finally:
        # Close shared memory (but don't unlink - parent process will do that)
        shm.close()
        del np_array, df_datas


class Simulation_v2:
    """
    Simulate trading strategy
    """

    def __init__(self, simulate_config=None, score_config=None, start_date='2022-06-01',
                 end_date='2027-01-01', num_proc=20, buffer_ratio=0.15, fpath='ticker_v1a',
                 simulation_version: str = DEFAULT_SIMULATION_VERSION):

        backend = get_simulation_backend(simulation_version)

        self.simulate_config = simulate_config
        self.score_config = score_config
        self.simulation_version = backend['version']
        self.wrapper_class = backend['wrapper_class']
        self.score_manager = backend['score_manager_class'](score_config, score_col='score')

        self.df_datas = None
        self.start_date = start_date
        self.end_date = self.preprocess_end_time(end_date)
        self.period, self.buffer = self.find_simulate_period(start_date, self.end_date, buffer_ratio)

        self.num_proc = num_proc
        self.fpath = fpath

    def load_score(self, df_datas, start_date, end_date, format='%m/%d/%Y'):
        """
        Optimized load_score with vectorized operations and efficient data types.
        """
        # Avoid unnecessary copy - work with view where possible
        df = df_datas.reset_index(drop=True)

        # Convert time once
        df['time'] = pd.to_datetime(df['time'], format=format)

        # Calculate score
        df = self.score_manager.run(df)

        # Vectorized boolean indexing - all at once
        ii = (
                (df['close'] > 0) &
                (df['price'] > 0) &
                (df['volume_1m_p50'] > 0) &
                df['score'].notna() &
                (df['time'] >= pd.to_datetime(start_date)) &
                (df['time'] <= pd.to_datetime(end_date))
        )

        # Select columns and rename in one operation
        if 'open' not in df.columns:
            df['open'] = df['close']
        if 'fa_flag' not in df.columns:
            df['fa_flag'] = True

        cols = ['time', 'ticker', 'close', 'open', 'price', 'score', 'volume_1m_p50', 'fa_flag']

        if 'buy_pattern' in df.columns and 'sell_pattern' in df.columns:
            cols.append('buy_pattern')
            cols.append('sell_pattern')

        data = df.loc[ii, cols].copy()
        data.rename(columns={'close': 'close_price', 'open': 'open_price'}, inplace=True)

        # Vectorized calculations
        data['daily_amount'] = data['volume_1m_p50'] * data['price']
        data.drop(columns=['volume_1m_p50', 'price'], inplace=True)

        # # Optimize data types for memory and speed
        data['ymd'] = data['time'].dt.strftime('%Y-%m-%d')

        data['ticker'] = data['ticker'].astype('category')
        data['ymd'] = data['ymd'].astype('category')

        # Sort once at the end
        data.sort_values('ymd', ascending=True, inplace=True)
        data.reset_index(drop=True, inplace=True)
        # data.drop(columns=['time'], inplace=True)

        return data

    @staticmethod
    def preprocess_end_time(end_date):
        end_date = min(datetime.today(), datetime.strptime(end_date, "%Y-%m-%d")).strftime('%Y-%m-%d')
        return end_date

    @staticmethod
    def find_simulate_period(start_date, end_date, ratio):
        """
            Finds the simulation period based on the given start and end dates, and a buffer.

            The function takes the start and end dates, and a buffer value. It calculates the number of days between the end date and the start date, and subtracts the buffer value to get the simulation period.

            Parameters:
                start_date (str): The start date in the format "YYYY-MM-DD".
                end_date (str): The end date in the format "YYYY-MM-DD".
                buffer (int): The buffer value to subtract from the number of days.

            Returns:
                int: The simulation period in days.
            """
        delta_day = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
        buffer = int(delta_day * ratio)
        simulate_period = int(delta_day - buffer)
        return simulate_period, buffer

    @staticmethod
    def convert_to_dict(serial_data):
        result = {}

        for item in serial_data.items():
            key, value = item
            main_key, sub_key = key.split('.', 1)

            if main_key not in result:
                result[main_key] = {}

            result[main_key][sub_key] = value

        return result

    def _run_with_shared_memory(self, random_list):
        """
        Run simulations using shared memory for efficient multiprocessing.

        This method creates a shared memory block containing the DataFrame data,
        allowing worker processes to access it without serialization overhead.

        Args:
            random_list: List of random seeds for each iteration

        Returns:
            List of simulation results from all workers
        """
        # Convert DataFrame to numpy array for shared memory
        # Save categorical columns info before conversion
        column_dtypes = {}
        categories_map = {}

        df_for_shm = self.df_datas.copy()
        for col in df_for_shm.columns:
            if isinstance(df_for_shm[col], pd.CategoricalDtype):
                categories_map[col] = df_for_shm[col].cat.categories.tolist()
                df_for_shm[col] = df_for_shm[col].cat.codes.astype(np.int32)
                column_dtypes[col] = 'category'
            elif pd.api.types.is_string_dtype(df_for_shm[col]):
                df_for_shm[col] = df_for_shm[col].astype('category')
                categories_map[col] = df_for_shm[col].cat.categories.tolist()
                df_for_shm[col] = df_for_shm[col].cat.codes.astype(np.int32)
                column_dtypes[col] = 'category'
            else:
                column_dtypes[col] = str(df_for_shm[col].dtype)

        # Convert to contiguous numpy array in one step
        np_array = np.ascontiguousarray(df_for_shm.to_numpy())
        del df_for_shm  # Free intermediate DataFrame immediately

        # Initialize resources for proper cleanup
        shm = None
        pool = None
        try:
            # Create shared memory block
            shm = shared_memory.SharedMemory(create=True, size=np_array.nbytes)

            # Copy data to shared memory
            shm_array = np.ndarray(np_array.shape, dtype=np_array.dtype, buffer=shm.buf)
            shm_array[:] = np_array[:]

            # Prepare metadata for workers to reconstruct DataFrame
            df_metadata = {
                'shape': np_array.shape,
                'dtype': np_array.dtype,
                'columns': list(self.df_datas.columns),
                'column_dtypes': column_dtypes,
                'categories_map': categories_map,
            }

            # Prepare arguments for each worker
            args_list = [
                (seed, shm.name, df_metadata, self.simulate_config, self.simulation_version, self.start_date,
                 self.period)
                for seed in random_list
            ]

            # Create pool with comprehensive error handling
            try:
                pool = StandardPool(processes=self.num_proc)

                # Use imap_unordered for dynamic load balancing
                result_iterator = pool.imap_unordered(
                    _worker_process_simulate,
                    args_list,
                    chunksize=1  # Dynamic assignment - workers get tasks one at a time
                )

                # Collect results with proper error handling
                all_results = []
                for result in result_iterator:
                    all_results.append(result)

            except Exception as e:
                raise

            return all_results

        except Exception as e:
            print(f"Critical error in _run_with_shared_memory: {e}")
            raise

        finally:
            # Comprehensive cleanup sequence - order matters!
            shm.close()
            shm.unlink()
            # Clean up multiprocessing pool
            if pool is not None:
                try:
                    # Close pool to prevent new tasks
                    pool.close()
                except Exception as e:
                    print(f"Warning: Error closing pool: {e}")
                    # Force terminate if join fails
                    try:
                        pool.terminate()
                        # Simple join without timeout after terminate
                        pool.join()
                    except Exception as e2:
                        print(f"Warning: Error terminating pool: {e2}")

                # Clear pool reference
                pool = None

    def process_simulate(self, seed):
        """
        This method is used when use_shared_memory=False in run_fast().
        """
        np.random.seed(seed)

        # Shuffle data efficiently with memory optimization
        start_period = (pd.to_datetime(self.start_date) + pd.Timedelta(seed, "d"))
        end_period = (pd.to_datetime(start_period) + pd.Timedelta(self.period, "d"))
        mask = (self.df_datas["time"] >= start_period) & (self.df_datas["time"] <= end_period)

        df_datas = self.df_datas.loc[mask].copy()  # Explicit copy for clarity
        df_datas = _shuffle_by_date(df_datas, seed, copy_data=False)  # No additional copy needed

        # Run simulation
        simulator = self.wrapper_class(self.simulate_config)
        simulator.run(df_datas)
        ann_index, _ = calc_annual_profit(VNINDEX_PATH)
        stats = simulator.stats(ann_index)

        result = stats['stats_log']
        result.update(stats['stats_tx']['tmetrics'])

        return {'output': result}

    def run_fast(self, df_proba, iterate=10, use_shared_memory=True):
        """
        Run multiple simulation iterations in parallel.

        Args:
            df_proba: DataFrame with probability/score data
            iterate: Number of simulation iterations to run
            use_shared_memory: If True, use shared memory optimization
                             If False, use original method (for backward compatibility)

        Returns:
            Dict with aggregated simulation results
        """
        # Load and prepare data
        self.df_datas = self.load_score(df_proba, start_date=self.start_date, end_date=self.end_date, format='%Y-%m-%d')

        np.random.seed(iterate)
        iterate_range = np.linspace(0, self.buffer, iterate + 1, dtype=int)
        random_list = [np.random.randint(int(r[0]), int(r[1])) for r in zip(iterate_range[:-1], iterate_range[1:])]

        if use_shared_memory:
            all_results = self._run_with_shared_memory(random_list)
        else:
            # Use method for small datasets
            with PathosPool(processes=self.num_proc) as pool:
                all_results = pool.map(self.process_simulate, random_list)

        # Normalize results
        df = pd.json_normalize(all_results)

        # Pre-allocate result series for better performance
        df_result = pd.Series(dtype=object)

        # Vectorized aggregation operations
        for col in df.columns:
            if 'CAGR' in col:
                # Compute all CAGR-related metrics at once
                col_data = df[col]
                df_result[col] = col_data.mean()
                df_result[col.replace('CAGR', 'return_std')] = col_data.std()
                df_result[col.replace('CAGR', 'return_max')] = col_data.max()
                df_result[col.replace('CAGR', 'return_min')] = col_data.min()

            elif ('set_ticker' in col) or ('set_quarter_ticker' in col):
                # Optimized ticker diversity calculation
                col_values = df[col].values
                lengths = [len(v) for v in df[col].values]
                tickers = [ticker for v in df[col].values for ticker in v]
                df_result[col] = len(set(tickers)) / np.mean(lengths)
                df_result[f"{col}_diversity"] = len(set(tickers)) / np.mean(lengths)
                df_result[col.replace('set', 'unique')] = len(set(tickers))

            elif isinstance(df[col].iloc[0], (list, np.ndarray)):
                df_result[col] = np.mean(np.concatenate(df[col].values))
                df_result[f"{col}_std"] = np.std(np.concatenate(df[col].values))

            else:
                # Simple mean for other columns
                df_result[col] = df[col].mean()

        return self.convert_to_dict(df_result)['output']

    def get_detail(self):
        """
        Optimized get_detail with vectorized shuffle operation.
        """

        df_datas = _shuffle_by_date(self.df_datas, 42)

        simulator = self.wrapper_class(self.simulate_config)
        simulator.run(df_datas)
        result = simulator.stats(detail=True)
        result['log'] = _build_simulation_log_jsonl(
            pd.DataFrame(result.get('transactions', {})),
            pd.DataFrame(result.get('daily', {})),
            result.get('stats_tx', {}).get('pos', pd.DataFrame()),
        )
        return result


if __name__ == "__main__":
    import os
    import sys

    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = current_dir.replace("/webui", "")
    os.chdir(current_dir)
    sys.path.insert(0, current_dir)
    #
    FPATH = 'ticker_v1a'

    simulate_config = {
        'initial_amount': 50e9,
        'cutloss': 0.15,
        'cutloss_duration': 30,  # number of days not buying after cutloss
        'ratio_nav': 1.0,  # ratio between invest amount and nav (we will not buy more than ratio_nav * nav)
        'ratio_deal': 0.1,
        # ratio between each deal amount and invest amount (we will not buy more than ratio_deal * ratio_nav * nav))
        'ratio_deal_volume': 0.1,
        # ratio between each deal and daily volume (we will not buy more than ratio_deal_volume * daily_volume * price_target)
        'review_frequency': None,
        'fee_buy_rate': 0.001,
        'fee_sell_rate': 0.002,
        'score_sell': 0,
        'score_buy': 1,
        'gamma': 1,
        'min_ratio_deal_nav': 0.01,
        'min_amount_deal': 10_000_000,  # for buy or partial sell
        'verbose': True,
        'use_pattern_validation': True,
        'time_stop_days': 20,
        'pattern_mapping': {
            "BKMA200": ["MA41", "SellBV", "SellBV2", "SellResistance1Y", "BearDvgVNI1", "BearDvgVNI2"],
            "BullDvg": ["BearDvg2", "SellBV", "SellBV2", "SellPE", "SellResistance", "SellVolMax", "BearDvgVNI1",
                        "BearDvgVNI2"],
            "BuySupport": ["BearDvg2", "MA31", "SellBV", "SellPE", "SellResistance", "SellResistance1M", "SellVolMax",
                           "BearDvgVNI1", "BearDvgVNI2"],
            "CashCowStock": ["BearDvg2", "MA41", "S13", "SellBV", "SellBV2", "SellPE", "SellResistance1M",
                             "SellResistance1Y", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "Conservative": ["MA31", "MA41", "S13", "SellResistance", "SellResistance1M", "SellVolMax", "BearDvgVNI1",
                             "BearDvgVNI2"],
            "DividendYield": ["BearDvg2", "MA31", "MA41", "S13", "SellBV", "SellBV2", "SellResistance",
                              "SellResistance1M", "SellResistance1Y", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "RSILow30": ["BearDvg2", "MA41", "S13", "SellBV", "SellBV2", "SellResistance", "SellResistance1M",
                         "SellResistance1Y", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "SuperGrowth": ["BearDvg2", "S13", "SellBV", "SellLowGrowth", "SellPE", "SellResistance",
                            "SellResistance1M", "SellResistance1Y", "BearDvgVNI1", "BearDvgVNI2"],
            "SurpriseEarning": ["BearDvg2", "MA41", "S13", "SellBV", "SellBV2", "SellResistance", "SellResistance1M",
                                "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "T3P4": ["MA31", "MA41", "S13", "SellBV", "SellBV2", "SellResistance", "SellResistance1Y", "SellVolMax",
                     "BearDvgVNI1", "BearDvgVNI2"],
            "TL3M": ["BearDvg2", "MA31", "S13", "SellBV2", "SellResistance1M", "SellResistance1Y", "BearDvgVNI1",
                     "BearDvgVNI2"],
            "TradingValueMax": ["BearDvg2", "MA41", "S13", "SellResistance", "SellVolMax", "BearDvgVNI1",
                                "BearDvgVNI2"],
            "TrendingGrowth": ["BearDvg2", "MA41", "SellBV", "SellBV2", "SellPE", "SellResistance1M", "BearDvgVNI1",
                               "BearDvgVNI2"],
            "UnderBV": ["BearDvg2", "SellBV", "SellPE", "SellResistance", "SellResistance1M", "SellVolMax",
                        "BearDvgVNI1", "BearDvgVNI2"],
            "VolMax1Y": ["MA41", "SellBV2", "SellPE", "SellResistance1M", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "AccSup": ["MA21", "SellResistance", "SellBV2", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],

            "BKMA200_special": ["MA41", "SellBV", "SellBV2", "SellResistance1Y", "BearDvgVNI1", "BearDvgVNI2"],
            "BullDvg_special": ["BearDvg2", "SellBV", "SellBV2", "SellPE", "SellResistance", "SellVolMax",
                                "BearDvgVNI1", "BearDvgVNI2"],
            "BuySupport_special": ["BearDvg2", "MA31", "SellBV", "SellPE", "SellResistance", "SellResistance1M",
                                   "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "CashCowStock_special": ["BearDvg2", "MA41", "S13", "SellBV", "SellBV2", "SellPE", "SellResistance1M",
                                     "SellResistance1Y", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "Conservative_special": ["MA31", "MA41", "S13", "SellResistance", "SellResistance1M", "SellVolMax",
                                     "BearDvgVNI1", "BearDvgVNI2"],
            "DividendYield_special": ["BearDvg2", "MA31", "MA41", "S13", "SellBV", "SellBV2", "SellResistance",
                                      "SellResistance1M", "SellResistance1Y", "SellVolMax", "BearDvgVNI1",
                                      "BearDvgVNI2"],
            "RSILow30_special": ["BearDvg2", "MA41", "S13", "SellBV", "SellBV2", "SellResistance", "SellResistance1M",
                                 "SellResistance1Y", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "SuperGrowth_special": ["BearDvg2", "S13", "SellBV", "SellLowGrowth", "SellPE", "SellResistance",
                                    "SellResistance1M", "SellResistance1Y", "BearDvgVNI1", "BearDvgVNI2"],
            "SurpriseEarning_special": ["BearDvg2", "MA41", "S13", "SellBV", "SellBV2", "SellResistance",
                                        "SellResistance1M", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "T3P4_special": ["MA31", "MA41", "S13", "SellBV", "SellBV2", "SellResistance", "SellResistance1Y",
                             "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
            "TL3M_special": ["BearDvg2", "MA31", "S13", "SellBV2", "SellResistance1M", "SellResistance1Y",
                             "BearDvgVNI1", "BearDvgVNI2"],
            "TradingValueMax_special": ["BearDvg2", "MA41", "S13", "SellResistance", "SellVolMax", "BearDvgVNI1",
                                        "BearDvgVNI2"],
            "TrendingGrowth_special": ["BearDvg2", "MA41", "SellBV", "SellBV2", "SellPE", "SellResistance1M",
                                       "BearDvgVNI1", "BearDvgVNI2"],
            "UnderBV_special": ["BearDvg2", "SellBV", "SellPE", "SellResistance", "SellResistance1M", "SellVolMax",
                                "BearDvgVNI1", "BearDvgVNI2"],
            "VolMax1Y_special": ["MA41", "SellBV2", "SellPE", "SellResistance1M", "SellVolMax", "BearDvgVNI1",
                                 "BearDvgVNI2"],
            "AccSup_special": ["MA21", "SellResistance", "SellBV2", "SellVolMax", "BearDvgVNI1", "BearDvgVNI2"],
        },
    }
    #
    # score_config = {
    #     "score_col": "score",
    #     "proba_col": "proba",
    #     "step_round": 0.5,
    #     "score_sell": 0,
    #     "score_buy": 1,
    #     "fa_option": "A",
    #     'calibrate_kind': None,
    #     'use_temperature': False,
    #     'temp_mode': 'brier',
    #     'percentiles': (0, 80, 82, 100),
    #     'score_knots': [-1.0, 1.2, 2, 3.0],
    #     'lift_target_rates': None,
    #     'base_rate': None,
    #     'clip_range': (-1.0, 3.0)
    # }
    #
    # score_config = {
    #     "score_col": "score",
    #     "step_round": 0.5,
    #     "score_sell": 0,
    #     "score_buy": 1,
    #     "fa_option": "A",
    #     "ai_engine": False,
    #     "sell_from_pattern": True,
    #     "buy_from_pattern": True,
    #     "buy_engine": {
    #         'calibrate_kind': None,
    #         'use_temperature': False,
    #         'temp_mode': 'brier',
    #         'percentiles': (0, 80, 82, 100),
    #         'score_knots': [-1.0, 1.2, 2, 3.0],
    #         'lift_target_rates': None,
    #         'base_rate': None,
    #         'clip_range': (-1.0, 3.0),
    #         'proba_col': "proba",
    #     },
    #     "sell_engine": {
    #         'threshold': 0.6,
    #         'proba_col': "sell_proba",
    #     }
    # }
    market_sell_patterns = [p_name[1:] for p_name in MARKET_DICT_FILTER.keys() if
                            p_name.startswith("~")] if True else []
    # v1.5
    score_config = {
        "score_col": "score",
        "score_sell": 0,
        "score_buy": 1,
        # "fa_option": "A",
        'score_rank_col': 'order_rank',
        "buy_sell_from_pattern": True,
        'market_sell_patterns': market_sell_patterns,
    }

    order_dict = {
        'BKMA200': 7,
        'TrendingGrowth': 5,
        'TL3M': 1,
        'BuySupport': 10,
        'RSILow30': 15,
        'UnderBV': 12,
        'SuperGrowth': 4,
        'SurpriseEarning': 5,
        'Conservative': 2,
        'BullDvg': 15,
        'VolMax1Y': 6,
        # 'T3P4': 1,
        'T3P4': 0,
        'DividendYield': 0,
        'CashCowStock': 0,
        # 'TradingValueMax': 0.15,
        'TradingValueMax': 0,
        'AccSup': 7,

        'BKMA200_special': 20 + 7,
        'TrendingGrowth_special': 20 + 5,
        'TL3M_special': 20 + 1,
        'BuySupport_special': 20 + 10,
        'RSILow30_special': 20 + 15,
        'UnderBV_special': 20 + 12,
        'SuperGrowth_special': 20 + 4,
        'SurpriseEarning_special': 20 + 5,
        'Conservative_special': 20 + 2,
        'BullDvg_special': 20 + 15,
        'VolMax1Y_special': 20 + 6,
        'T3P4_special': 20 + 0,
        'DividendYield_special': 20 + 0,
        'CashCowStock_special': 20 + 0,
        'TradingValueMax_special': 20 + 0,
        'AccSup_special': 20 + 7,
    }
    # df_proba = pd.read_csv('deeplearning/outputs/predictions/predictions_20251121.csv',
    #                        usecols=['time', 'ticker', 'close', 'price', 'volume', 'volume_1m_p50', 'proba', "CF_OA_5Y",
    #                                 "OShares", "FSCORE", "NP_P0", "NP_P1", "NP_P4", "PCF", "PB", "PE", "ROE5Y",
    #                                 "ROE_Min3Y", "v1_buy", "v1_sell"])

    df_profile_hit = pd.read_csv('webui/profile_hit.csv',
                                 # df_profile_hit = pd.read_csv('webui/artifacts/profile_hit.csv',
                                 usecols=['ticker', 'time', 'Sell_time', 'filter', 'Sell_filter'])

    valid_filter = [k for k, v in order_dict.items() if v > 0]
    df_profile_hit = df_profile_hit[df_profile_hit['filter'].isin(valid_filter)]
    df_profile_hit['order_rank'] = df_profile_hit['filter'].map(order_dict).fillna(0).astype('int8')
    df_profile_hit = df_profile_hit.sort_values('order_rank', ascending=False).drop_duplicates(['ticker', 'time'],
                                                                                               keep='first')

    buy = (
        df_profile_hit
        .set_index(['ticker', 'time'])[['filter', 'order_rank']]
        .rename(columns={'filter': 'buy_pattern'})
    )

    sell = (
        df_profile_hit[['ticker', 'Sell_time', 'Sell_filter']]
        .drop_duplicates(['ticker', 'Sell_time', 'Sell_filter'])
        .rename(columns={'Sell_time': 'time', 'Sell_filter': 'sell_pattern'}).reset_index(drop=True)
    )
    # 8143 -> 3648
    sell = sell[sell['sell_pattern'] != 'cutloss']
    sell = sell.groupby(by=['ticker', 'time'])[['sell_pattern']].agg(list)

    # df_proba = prepare_core_data()
    df_proba = pd.read_csv('webui/df_core_v1_5.csv')
    if 'open' not in df_proba.columns:
        df_proba['open'] = df_proba['close']

    valid_ticker = df_profile_hit['ticker'].unique()
    df_proba['ticker'] = df_proba['ticker'].astype('category')
    df_proba = df_proba[df_proba['ticker'].isin(valid_ticker)]

    df_proba = (
        df_proba
        .set_index(['ticker', 'time'])
        .join(buy)
        .join(sell, how='left')
        .reset_index()
    )

    # df_proba = df_proba.drop_duplicates(subset=['ticker', 'time'], keep='first')
    df_proba = df_proba.sort_values('time', ascending=True)
    print(df_proba.shape)
    now = time.time()
    simulation = Simulation_v2(simulate_config, score_config, start_date='2025-01-01', end_date='2027-01-01',
                               buffer_ratio=0.15)
    result = simulation.run_fast(df_proba, iterate=1, use_shared_memory=False)
    detail = simulation.get_detail()
    detail_transactions = pd.DataFrame(detail.get('transactions', {}))

    print(f"Time: {time.time() - now}")
    # # with open('result.json', 'w') as f:
    # #     json.dump(result, f, indent=4)
    print("📊 Performance Metrics")
    print("-" * 35)
    for k, v in result.items():
        if isinstance(v, float):
            print(f"{k:<30}: {v:>10.4f}")
        else:
            print(f"{k:<30}: {v}")
