import datetime
import uuid

import numpy as np
import pandas as pd
from core_utils.simulation_v2a import Simulation


# config = {
#     'initial_amount': 1e7,
#     'cutloss': 0.15,
#     'cutloss_duration': 30, # number of days not buying after cutloss
#     'ratio_nav': 0.9, # ratio between invest amount and nav (we will not buy more than ratio_nav * nav)
#     'ratio_deal': 0.1, # ratio between each deal amount and invest amount (we will not buy more than ratio_deal * ratio_nav * nav))
#     'ratio_deal_volume': 0.1, # ratio between each deal and daily volume (we will not buy more than ratio_deal_volume * daily_amount )
#     'review_frequency': 'monthly',
#     'fee_buy_rate': 0.001,
#     'fee_sell_rate': 0.002,
#     'score_sell': 0.5,
#     'score_buy': 1,
#     'gamma': 1,
#     'min_ratio_deal_nav': 0.01, # for buy or partial sell
# }

# portfolio:
# * data:
# - cash: float
# - fee_rate: float
# - holdings: ticker, holding_amount, adj_price, init_score, current_score, investment_amount
# - transaction: ymd, ticker, action, buy_amount, sell_amount, adj_price, fee
# * method
# - init(initial_amount)
# - update_ticker(data): update holdings at end of day based on new data(ymd, ticker, adj_price, score)
# - update_holding(data): update holding in the morning based on order plan (ymd, action, ticker, adj_price, amount)


# simulation:
# * data:
# - portfolio: current portfolio
# - config: config of the simulation
# - invest_ratio: float # usually 1. but can be lower based on market condition
# - daily_stats: ymd, nav, cash, list_holding, list_buy, list_sell
# * method
# - init(config): initialize the simulation
# - reset(config=None): reset the simulation
# - set_invest_ratio(invest_ratio): set the invest ratio
# - run(data): main function to run the simulation

def move_forward_date(ymd, days, date_format='%Y-%m-%d'):
    return (pd.to_datetime(ymd, format=date_format) + pd.Timedelta(days=days)).strftime(date_format)


class Portfolio:
    def __init__(self, initial_amount, fee_buy_rate, fee_sell_rate):
        self.cash = initial_amount
        self.fee_buy_rate = fee_buy_rate
        self.fee_sell_rate = fee_sell_rate
        self.holdings = {}  # dict ['ticker'] of dict { 'holding_amount', 'adj_price', 'init_score', 'current_score', 'investment_amount'}
        self.transactions = []  # list of dict {'ymd', 'ticker', 'action', 'adj_price', 'transaction_amount', 'fee', 'investment_amount'}
        self.log = []  # list of dict {'ymd', 'cash', 'nav', 'num_holdings', 'num_transactions'}

    def update_score_close_price(self, data):
        ''' update holdings at end of day based on new data index by ticker, columns (close_price, score) '''
        time_stop_days = 20
        for ticker in self.holdings.keys():
            if ticker in data.index:
                try:
                    self.holdings[ticker] = self._update_one_holding(self.holdings[ticker],
                                                                     data.loc[ticker]['close_price'],
                                                                     data.loc[ticker]['score'])
                    holding = self.holdings[ticker]
                    days_held = holding.get('days_held', 0)
                    is_time_stop_candidate = holding.get('is_time_stop_candidate', True)
                    if days_held < time_stop_days and holding['holding_amount'] > holding['investment_amount']:
                        is_time_stop_candidate = False
                    holding['is_time_stop_candidate'] = is_time_stop_candidate
                    holding['days_held'] = days_held + 1

                    score_offset = self._calculate_score_offset(holding)
                    if data.loc[ticker]['score'] > 1:
                        holding['current_score'] = data.loc[ticker]['score'] + score_offset
                    else:
                        holding['current_score'] = holding['current_score']

                except:
                    print(
                        f"""Portfolio.update_score_close_price: Warning data not found for {ticker} on {data.index.name}""")
        # sort holdings by current score from low to high
        self.holdings = dict(sorted(self.holdings.items(), key=lambda x: x[1]['current_score'], reverse=False))

    def update_log(self, ymd):
        self.log.append({'ymd': ymd, 'cash': self.cash,
                         'nav': self.cash + sum(holding['holding_amount'] for holding in self.holdings.values()),
                         'num_holdings': len(self.holdings), 'num_transactions': len(self.transactions)})

    def _calculate_score_offset(self, holding):
        investment_amount = holding.get('investment_amount', 0)
        if investment_amount is None or investment_amount <= 0:
            return 0.0
        profit_ratio = (holding.get('holding_amount', 0.0) - investment_amount) / investment_amount
        return float(profit_ratio) / 10  # scale down the profit ratio to avoid too large score offset

    def _update_one_holding(self, holding, new_price, score=None, score_offset=0.0):
        if new_price != holding['adj_price']:
            holding['holding_amount'] = holding['holding_amount'] * new_price / holding['adj_price']
            holding['adj_price'] = new_price
            # holding['max_price'] = max(holding.get('max_price', new_price), new_price)
        if score is not None:
            holding['current_score'] = score + score_offset
        return holding

    def execute_plan(self, ymd, plans):
        ''' update holding in the morning based on order plan - list of dict (action, ticker, amount, score, adj_price, buy_pattern, sell_pattern)
        the holding might not be updated with latest price
        the plans should be updated with latest price
        '''
        if plans is None:
            return
        cnt = 0

        # step-by-step SELL:
        # - compute transaction amount and fee
        # - update holding list
        # - update cash
        # - append transaction
        for plan in plans:
            ticker = plan['ticker']
            if plan['action'] != 'sell':
                continue
            # if amount is larger than holding, sell all
            if ticker not in self.holdings:
                print(f"""execute_plan: Warning ticker not in holdings: {ticker}""")
                continue
            # update adj_price, amount of the holding
            self.holdings[ticker] = self._update_one_holding(self.holdings[ticker], plan['adj_price'])

            transaction_amount = min(plan['amount'], self.holdings[ticker]['holding_amount'])
            fee = transaction_amount * self.fee_sell_rate
            # investment amount corresponds to the amount of the transaction
            original_buy_amount = self.holdings[ticker]['investment_amount'] * transaction_amount / \
                                  self.holdings[ticker]['holding_amount']
            self.cash += (transaction_amount - fee)

            # use holding_id from holdings
            holding_id = self.holdings[ticker]['holding_id']

            # Get buy_pattern from holdings and sell_pattern from plan
            buy_pattern = self.holdings[ticker].get('buy_pattern', None)
            sell_pattern = plan.get('sell_pattern', None)

            # append transaction
            self.transactions += [{'ymd': ymd,
                                   'ticker': ticker,
                                   'holding_id': holding_id,
                                   'action': 'sell',
                                   'adj_price': plan['adj_price'],
                                   'buy_amount': original_buy_amount,
                                   'sell_amount': transaction_amount,
                                   'fee': fee,
                                   'buy_pattern': buy_pattern,
                                   'sell_pattern': sell_pattern}]
            cnt += 1

            self.holdings[ticker]['holding_amount'] -= transaction_amount
            self.holdings[ticker]['investment_amount'] -= original_buy_amount
            if self.holdings[ticker]['holding_amount'] <= 10000.0:
                del self.holdings[ticker]

        # step-by-step BUY:
        # - compute transaction amount and fee
        # - update holding
        # - update cash
        # - append transaction
        for plan in plans:
            if plan['action'] != 'buy':
                continue
            # print(f"""Plan amount: {plan['amount']}
            # Cash: {self.cash}
            # Fee buy rate: {self.fee_buy_rate}
            # """)
            transaction_amount = min(plan['amount'], self.cash * (1.0 - self.fee_buy_rate))
            fee = transaction_amount * self.fee_buy_rate

            # Get buy_pattern from plan
            buy_pattern = plan.get('buy_pattern', None)

            if plan['ticker'] in self.holdings:
                self.holdings[plan['ticker']]['holding_amount'] += transaction_amount
                self.holdings[plan['ticker']]['investment_amount'] += transaction_amount
                holding_id = self.holdings[plan['ticker']]['holding_id']
                # Update buy_pattern if provided (for additional buys)
                if buy_pattern is not None:
                    self.holdings[plan['ticker']]['buy_pattern'] = buy_pattern
            else:
                # new holding_id when first buy
                holding_id = str(uuid.uuid4())
                self.holdings[plan['ticker']] = {'holding_id': holding_id,
                                                 'holding_amount': transaction_amount,
                                                 'adj_price': plan['adj_price'],
                                                 'init_score': plan['score'],
                                                 'current_score': plan['score'],
                                                 'investment_amount': transaction_amount,
                                                 'buy_pattern': buy_pattern,
                                                 'days_held': 0,
                                                 'is_time_stop_candidate': True}
            self.cash -= (transaction_amount + fee)
            self.transactions += [{'ymd': ymd,
                                   'ticker': plan['ticker'],
                                   'holding_id': holding_id,
                                   'action': 'buy',
                                   'adj_price': plan['adj_price'],
                                   'buy_amount': transaction_amount,
                                   'sell_amount': 0,
                                   'fee': fee,
                                   'buy_pattern': buy_pattern,
                                   'sell_pattern': None}]
            cnt += 1
        if cnt != len(plans):
            print(f"""execute_plan: Warning cnt != len(plans) cnt: {cnt} len(plans): {len(plans)}""")


class WrapperSimulation(Simulation):
    def __init__(self, config):
        super().__init__(config)
        self.portfolio = Portfolio(initial_amount=config['initial_amount'], fee_buy_rate=config['fee_buy_rate'],
                                   fee_sell_rate=config['fee_sell_rate'])

    def calculate_delta_price(self, v_sell, v_prev, k=0.1, p_latest=1):
        if np.isnan(v_sell) or np.isnan(v_prev) or v_prev == 0 or v_sell == 0:
            return 0.1
        return min(0.1, p_latest * (1 - np.exp(-k * (v_sell / v_prev))))

    def _is_review_day(self, ymd, review_frequency):
        if review_frequency == 'daily':
            return True
        elif review_frequency == 'weekly':
            return pd.to_datetime(ymd).weekday == 4  # Friday
        elif review_frequency == 'monthly':
            ymd_dt = pd.to_datetime(ymd)
            next_day = ymd_dt + pd.Timedelta(days=1)
            return next_day.month != ymd_dt.month  # Last day of month
        elif review_frequency == 'quarterly':
            ymd_dt = pd.to_datetime(ymd)
            next_day = ymd_dt + pd.Timedelta(days=1)
            return (next_day.month - 1) // 3 != (ymd_dt.month - 1) // 3  # Last day of quarter
        return False

    def _is_valid_sell_pattern(self, buy_pattern, sell_pattern, pattern_mapping, use_pattern_validation):
        """
        Check if sell_pattern is valid for the given buy_pattern.

        Args:
            buy_pattern: Pattern used when buying (from holdings)
            sell_pattern: Current sell pattern (from data)
            pattern_mapping: Dict mapping buy_pattern -> list of valid sell_patterns
            use_pattern_validation: Whether to enforce pattern validation

        Returns:
            bool: True if sell is allowed, False otherwise
        """
        # If pattern validation is disabled, always allow sell
        if not use_pattern_validation:
            return True

        # If either pattern is None/missing, allow sell (backward compatible)
        if buy_pattern is None or sell_pattern is None:
            return True

        # If buy_pattern not in mapping, allow any sell_pattern (permissive default)
        if buy_pattern not in pattern_mapping:
            return True

        # Check if sell_pattern is in the list of valid patterns for this buy_pattern
        valid_sell_patterns = pattern_mapping[buy_pattern]

        if isinstance(sell_pattern, float) and pd.isna(sell_pattern):
            return False

        for p in sell_pattern:
            if p in valid_sell_patterns:
                return True

        return False

    @staticmethod
    def _use_fallback(x):
        if x is None:
            return True
        if x == 'blacklist':
            return True
        if np.isscalar(x):
            return pd.isna(x)
        if isinstance(x, (list, tuple, np.ndarray, pd.Series)):
            return len(x) == 0
        return False

    def prepare_order_plan(self, ymd, data_input):
        data = data_input.copy()
        cash = self.portfolio.cash
        nav = self.portfolio.cash + sum(holding['holding_amount'] for holding in self.portfolio.holdings.values())
        # min_buy_amount = self.config['min_ratio_deal_nav'] * nav
        min_buy_amount = self.config['min_amount_deal']
        slot_amount = nav * self.config['ratio_nav'] * self.config['ratio_deal']
        gamma = self.config['gamma']
        score_sell = self.config['score_sell']
        score_buy = self.config['score_buy']
        ratio_deal_volume = self.config['ratio_deal_volume']
        cutloss = self.config['cutloss']
        cutloss_duration = self.config['cutloss_duration']
        review_frequency = self.config['review_frequency']
        is_review_day = self._is_review_day(ymd, review_frequency)
        time_stop_days = self.config.get('time_stop_days')

        # Pattern validation config
        use_pattern_validation = self.config.get('use_pattern_validation', False)
        pattern_mapping = self.config.get('pattern_mapping', {})

        # update cutloss_dict
        for ticker in self.portfolio.holdings.keys():
            if self.portfolio.holdings[ticker]['holding_amount'] / self.portfolio.holdings[ticker][
                'investment_amount'] < (1 - cutloss):
                if self.config.get('verbose', False):
                    print(
                        f"""{ymd} add cutloss for {ticker} {self.portfolio.holdings[ticker]['holding_amount'] / self.portfolio.holdings[ticker]['investment_amount']}""")

            # elif self.portfolio.holdings[ticker].get('max_price', self.portfolio.holdings[ticker]['adj_price']) / \
            #         self.portfolio.holdings[ticker]['adj_price'] < (1 - cutloss):
            #     if self.config.get('verbose', False):
            #         print(
            #             f"""{ymd} add drawdown for {ticker} {self.portfolio.holdings[ticker]['max_price'] / self.portfolio.holdings[ticker]['adj_price']}""")
            else:
                continue

            self.cutloss_dict[ticker] = move_forward_date(ymd, cutloss_duration)

        self.cutloss_dict = {ticker: expiry_date
                             for ticker, expiry_date in self.cutloss_dict.items()
                             if ymd <= expiry_date}

        data.loc[data.index.isin(self.cutloss_dict.keys()), 'score'] = score_sell - 10.
        data.loc[data.index.isin(self.cutloss_dict.keys()), 'sell_pattern'] = 'blacklist'

        invest = {
            ticker: {'score': holding['current_score'] if ticker not in self.cutloss_dict else score_sell - 10.,
                     'amount': holding['holding_amount']} for ticker, holding in self.portfolio.holdings.items()}

        # sell full tickers with current_score < score_sell
        # sell partial tickers if holding amount > expected amount + 0.5 slot
        for ticker, e in invest.items():
            days_held = self.portfolio.holdings[ticker].get('days_held', 0)
            is_time_stop_candidate = self.portfolio.holdings[ticker].get('is_time_stop_candidate', False)
            is_time_stop_sell = (days_held == time_stop_days) and is_time_stop_candidate
            # Full sell: score-based OR cutloss OR time-stop
            if e['score'] <= score_sell or is_time_stop_sell:
                # Get current sell_pattern from data if available
                sell_pattern = None
                if ticker in data.index:
                    # Try multiple column names for sell_pattern
                    if 'sell_pattern' in data.columns:
                        sell_pattern = data.loc[ticker, 'sell_pattern']

                # Get buy_pattern from holdings
                buy_pattern = self.portfolio.holdings[ticker].get('buy_pattern', None)

                # Check if this is a valid sell based on pattern
                is_valid_pattern = self._is_valid_sell_pattern(
                    buy_pattern, sell_pattern, pattern_mapping, use_pattern_validation
                )

                # Only sell if pattern is valid
                if is_valid_pattern or (ticker in self.cutloss_dict) or is_time_stop_sell:
                    # print(f"""{ymd} is_valid_pattern: {is_valid_pattern} {ticker} {buy_pattern} {sell_pattern} {e['score']}""")
                    cash += e['amount']
                    invest[ticker]['amount'] = 0

                    if is_time_stop_sell:
                        invest[ticker]['sell_trigger'] = 'time_stop'
                        # add to blacklist
                        self.cutloss_dict[ticker] = move_forward_date(ymd, cutloss_duration)
                        if ticker in data.index:
                            data.loc[ticker, 'score'] = score_sell - 10.
                            data.loc[ticker, 'sell_pattern'] = 'blacklist'

                    elif ticker in self.cutloss_dict:
                        invest[ticker]['sell_trigger'] = 'cutloss'
                else:
                    # Log rejection due to pattern mismatch
                    if self.config.get('verbose', False):
                        pass
                        # print(f"""{ymd} REJECT SELL {ticker}: buy_pattern={buy_pattern}, sell_pattern={sell_pattern}, score={e['score']:.2f}""")
            else:
                # Partial sell on review day
                if is_review_day:
                    expected_amount = slot_amount * self.score_to_ratio_nav(e['score'], score_buy, gamma)
                    if e['amount'] > expected_amount + slot_amount * 0.5:
                        invest[ticker] = {'score': e['score'], 'amount': expected_amount}
                        cash += (e['amount'] - expected_amount)
                        # Only partial sell if pattern is valid
                        # if is_valid_pattern:
                        #     invest[ticker] = {'score': e['score'], 'amount': expected_amount}
                        #     cash += (e['amount'] - expected_amount)
                        # else:
                        #     if self.config.get('verbose', False):
                        #         print(f"""{ymd} REJECT PARTIAL SELL {ticker}: buy_pattern={buy_pattern}, sell_pattern={sell_pattern}""")

        # buy tickers with cash then swaps score > lowest score + gamma
        for ticker in data.index:
            if data.loc[ticker]['sell_pattern'] == 'blacklist':
                continue

            if data.loc[ticker]['score'] < score_buy or data.loc[ticker]['fa_flag'] is False:
                break  # the ticker is not good enough to buy

            expected_amount = min(
                slot_amount * self.score_to_ratio_nav(data.loc[ticker]['score'], score_buy, gamma),
                data.loc[ticker]['daily_amount'] * ratio_deal_volume)
            current_amount = 0 if ticker not in invest else invest[ticker]['amount']
            delta = expected_amount - current_amount

            if delta < min_buy_amount:
                continue  #

            if cash >= delta:
                invest[ticker] = {'score': data.loc[ticker]['score'], 'amount': expected_amount}
                cash -= delta
                continue

            should_force_swap = bool(self.score_to_ratio_nav(data.loc[ticker]['score'], score_buy, gamma) >= 2)
            if is_review_day or should_force_swap:
                # cash is not enough to buy the expected amount, then buy partial amount and find swaps
                swaps = self._find_potential_swaps(ticker, data.loc[ticker]['score'] - gamma, delta, cash,
                                                   min_buy_amount,
                                                   invest)

                # update invest
                for tt in swaps.keys():
                    if tt in invest:
                        invest[tt]['amount'] = float(int(invest[tt]['amount'] + swaps[tt]))
                        cash -= swaps[tt]
                    else:
                        invest[tt] = {'score': data.loc[tt]['score'], 'amount': swaps[tt]}
                        cash -= swaps[tt]

        plans = []
        for ticker in invest.keys():
            if ticker in self.portfolio.holdings:
                prev_amount = self.portfolio.holdings[ticker]['holding_amount']
            else:
                prev_amount = 0
            delta = invest[ticker]['amount'] - prev_amount
            if int(delta) != 0:
                if ticker in data.index:
                    close_price = data.loc[ticker]['close_price']
                    # Get buy_pattern and sell_pattern from data
                    buy_pattern = None
                    sell_pattern = None
                    if 'buy_pattern' in data.columns:
                        buy_pattern = data.loc[ticker, 'buy_pattern']

                    if 'sell_pattern' in data.columns:
                        sell_pattern = data.loc[ticker, 'sell_pattern']
                else:
                    close_price = self.portfolio.holdings[ticker][
                        'adj_price']  # this only happens when data is incomplete and we what to sell the ticker
                    buy_pattern = None
                    sell_pattern = None

                sell_trigger = invest[ticker].get('sell_trigger', None)
                sell_pattern = sell_trigger if self._use_fallback(sell_pattern) else sell_pattern

                if delta > 0:
                    plans.append(
                        {'action': 'buy', 'ticker': ticker, 'score': invest[ticker]['score'],
                         'adj_price': close_price,
                         'amount': delta,
                         'buy_pattern': buy_pattern,
                         'sell_pattern': sell_pattern})
                else:
                    plans.append(
                        {'action': 'sell', 'ticker': ticker, 'score': invest[ticker]['score'],
                         'adj_price': close_price,
                         'amount': -delta,
                         'buy_pattern': buy_pattern,
                         'sell_pattern': sell_pattern})
        return plans

    # ====== Stat =======
    def stat_logs(self, logs_df, ann_index=None):
        def drawdown_series(df: pd.DataFrame) -> pd.DataFrame:
            """
            Compute the drawdown time series from NAV.

            Intuition:
            - Peak NAV to date (running max) tracks the highest water mark.
            - Drawdown at time t = NAV(t) / PeakToDate(t) - 1  (≤ 0)
            - When NAV hits a new high, drawdown resets to 0.

            Parameters
            ----------
            df : pd.DataFrame
                Must contain column 'nav' and be indexed by date.

            Returns
            -------
            pd.DataFrame
                Columns:
                - 'nav'        : current NAV
                - 'peak_nav'   : running max of NAV
                - 'drawdown'   : relative drop from the running max (≤ 0)
            """
            s = df['nav'].astype(float)
            peak = s.cummax()  # running peak (highest so far)
            dd = (s / peak) - 1.0  # negative or zero
            return pd.DataFrame({'nav': s, 'peak_nav': peak, 'drawdown': dd}, index=df.index)

        def calc_annual_profit(df):
            df = df.copy()
            df['year'] = df['date'].dt.year

            # Giả sử df đã có daily_return, nếu chưa thì tính từ nav
            if 'daily_return' not in df.columns:
                df['daily_return'] = df['nav'].pct_change()

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

        def preprocess(df):
            out = df.copy()

            if 'ymd' in out.columns:
                out['date'] = pd.to_datetime(out['ymd'])
            elif 'date' in out.columns:
                out['date'] = pd.to_datetime(out['date'])

            out = out.sort_values('date').reset_index(drop=True)
            # out.set_index('date', inplace=True)

            # NAV & return
            if 'nav' in out.columns:
                out['daily_return'] = out['nav'].pct_change()

            # cash ratio
            if 'cash' in out.columns:
                out['cash_ratio'] = out['cash'] / out['nav']
                out['utilization'] = 1 - out['cash_ratio']

            return out

        def perf_stats(df: pd.DataFrame, rf: float = 0.03, periods_per_year: int = 240,
                       ann_vnindex: pd.DataFrame = None):
            """
           Compute core performance & risk statistics.

           Metrics:
           - total_return : (NAV_end / NAV_start - 1)
           - CAGR         : geometric annualized growth rate over the full period
           - ann_return   : mean daily return * periods_per_year (simple annualization)
           - ann_vol      : std(daily_return) * sqrt(periods_per_year)
           - Sharpe       : (ann_return - rf) / ann_vol
           - Sortino      : (ann_return - rf) / ann_downside,
                            where ann_downside uses std of negative daily returns only
           - max_drawdown : min(drawdown series)
           - Calmar       : ann_return / |max_drawdown|
           - period_days  : calendar length in days
           - obs          : number of rows

           Notes
           -----
           - `CAGR` uses geometric compounding across the actual time span,
             which is robust to irregular sample sizes.
           - `ann_return` is a linear annualization of mean daily returns;
             it’s convenient for ratios (Sharpe/Sortino), but not equal to CAGR.

           Parameters
           ----------
           df : pd.DataFrame
               Must include 'nav' and 'daily_return' and be date-indexed.
           rf : float, optional
               Annual risk-free rate (in decimal), default 0.0.
           periods_per_year : int, optional
               Trading periods per year, default 252 (daily bars for equities).

           Returns
           -------
           Key performance statistics as described above.

           Raises
           ------
           ValueError
           If there are no valid daily returns.
           """

            r = df['daily_return'].dropna()
            if len(r) == 0:
                raise ValueError("Not enough data to compute returns.")

            # Total return and time span
            total_return = df['nav'].iloc[-1] / df['nav'].iloc[0] - 1.0
            n_days = (df['date'].max() - df['date'].min()).days
            n_years = max(n_days, 1) / 365.25  # avoid division by zero

            # si_return
            # CAGR via geometric compounding across the full period
            cagr = (1 + total_return) ** (1 / n_years) - 1 if n_years > 0 else np.nan

            # Annualized return & volatility for ratio-based metrics
            ann_profits, ann_profit_std = calc_annual_profit(df)
            ann_return = ann_profits['ann_profit'].mean()
            sharpe = (ann_return - rf) / ann_profit_std if ann_profit_std != 0 else np.nan

            # Information Ratio
            information_ratio = np.nan
            if isinstance(ann_vnindex, pd.DataFrame):
                merged = pd.merge(ann_profits, ann_vnindex, on='year', suffixes=('_p', '_b'), how='left').dropna()
                merged['excess'] = merged['ann_profit_p'] - merged['ann_profit_b']
                information_ratio = merged['excess'].mean() / merged['excess'].std(ddof=1) if len(
                    merged) > 1 else np.nan

            # mean_daily = r.mean()
            # vol_daily = r.std(ddof=1)
            # ann_return = mean_daily * periods_per_year
            # ann_vol = vol_daily * np.sqrt(periods_per_year)
            # sharpe = (ann_return - rf/periods_per_year) / ann_vol if ann_vol != 0 else np.nan

            # Downside deviation: only consider negative daily returns
            downside = r[r < 0].std(ddof=1)
            ann_downside = downside * np.sqrt(periods_per_year) if pd.notna(downside) else np.nan
            sortino = (ann_return - rf) / ann_downside if (pd.notna(ann_downside) and ann_downside != 0) else np.nan

            # Drawdown-based risk
            dd = drawdown_series(df)['drawdown']
            max_dd = dd.min()
            calmar = ann_return / abs(max_dd) if max_dd != 0 else np.nan

            return {
                'total_return': total_return,
                'total_time': n_days,
                'utilization': np.nanmean(df['utilization']),
                'CAGR': cagr,
                'Sharpe': sharpe,
                'IR': information_ratio,
                'Sortino': sortino,
                'max_drawdown': max_dd,
                'Calmar': calmar,
                'period_days': n_days + 1,
                'obs': len(df),
                'flattened_ann_profits': ann_profits['ann_profit'].tolist(),
                'ann_return': ann_profits['ann_profit'].mean(),
                'ann_return_std': ann_profit_std
            }

        logs_df = preprocess(logs_df)
        return perf_stats(logs_df, ann_vnindex=ann_index)

    def stat_transactions(self, transactions_df):
        def preprocess(df):
            """
            Optimized preprocess with vectorized quantity estimation.

            Key optimization: Replace .apply() with vectorized operations.
            """
            out = df.copy()

            # 1) Date & action normalization
            if 'ymd' in out.columns:
                out['date'] = pd.to_datetime(out['ymd'])
            elif 'date' in out.columns:
                out['date'] = pd.to_datetime(out['date'])

            out['action'] = out['action'].str.lower().str.strip()

            # 2) Ensure money/price columns exist and are numeric
            for col in ['buy_amount', 'sell_amount', 'fee', 'adj_price']:
                if col not in out.columns:
                    out[col] = 0.0
                out[col] = pd.to_numeric(out[col], errors='coerce').fillna(0.0)

            # Clip to avoid negatives in these fields (simulation logs should be non-negative)
            for col in ['buy_amount', 'sell_amount', 'fee']:
                out[col] = out[col].clip(lower=0.0)

            # Determine which amount to use based on action
            # is_buy = out['action'] == 'buy'

            # For buy actions: prefer buy_amount, fallback to sell_amount
            # For sell actions: prefer sell_amount, fallback to buy_amount
            # amt = np.where(
            #     is_buy,
            #     np.where(out['buy_amount'] > 0, out['buy_amount'], out['sell_amount']),
            #     np.where(out['sell_amount'] > 0, out['sell_amount'], out['buy_amount'])
            # )
            #
            # # Calculate quantity: amt / price (handle division by zero)
            # out['est_qty'] = np.where(
            #     out['adj_price'] > 0,
            #     amt / out['adj_price'],
            #     np.nan
            # )

            out = out.sort_values(['date', 'holding_id']).reset_index(drop=True)
            out.set_index('date', inplace=True)

            return out

        def build_positions(df_tx: pd.DataFrame, qty_tol: float = 1e-8) -> pd.DataFrame:
            """
               Aggregate fills into position-level rows using `holding_id`.

               Lifecycle logic
               ---------------
               - Group rows by `holding_id` and sort by date.
               - Position open_date = first fill date; close_date = last fill date.
               - Buys add positive quantity; sells subtract quantity (best-effort via est_qty).

               PnL & pricing
               -------------
               - gross_pnl = sum(sell_amount) - sum(buy_amount)
               - net_pnl   = gross_pnl - sum(fee)
               - invested  = sum(buy_amount)  (capital deployed)
               - ret_net   = net_pnl / invested  (NaN if invested==0)
               - avg_buy_price  = sum(buy_amount)  / sum(buy_qty)  (if buy_qty>0)
               - avg_sell_price = sum(sell_amount) / sum(sell_qty) (if sell_qty>0)
               - ret_period = (close_price - open_price) / open_price

               Returns
               -------
               pd.DataFrame
                   One row per holding_id with:
                   - ticker, open_date, close_date, trades_count
                   - buy_notional, sell_notional, fee_total
                   - buy_qty, sell_qty, qty_net, status ('closed'|'open')
                   - gross_pnl, net_pnl, invested, ret_net, ret_period
                   - avg_buy_price, avg_sell_price
                   - holding_days (inclusive)
               """

            g = df_tx.groupby('holding_id', sort=False)

            rows = []
            for hid, grp in g:
                grp = grp.sort_index()
                ticker = grp['ticker'].iloc[0]
                open_date = grp.index.min()
                close_date = grp.index.max()
                open_quarter = grp.index.min().to_period('Q').strftime('%YQ%q')
                close_quarter = grp.index.max().to_period('Q').strftime('%YQ%q')

                open_price = grp['adj_price'].iloc[0]
                close_price = grp['adj_price'].iloc[-1]

                # trades_count = len(grp)
                sell_transaction_count = grp[grp['action'] == 'sell'].shape[0]
                buy_transaction_count = grp[grp['action'] == 'buy'].shape[0]
                win_transaction_count = \
                    grp[(grp['action'] == 'sell') & (grp['sell_amount'] > (grp['buy_amount'] + grp['fee']))].shape[0]

                # Quantities by action (best-effort)
                buy_mask = grp['action'].eq('buy')
                sell_mask = grp['action'].eq('sell')

                buy_notional = grp.loc[buy_mask, 'buy_amount'].sum()
                sell_notional = grp.loc[sell_mask, 'sell_amount'].sum()
                fee_total = grp['fee'].sum()

                # buy_qty = grp.loc[buy_mask, 'est_qty'].sum(min_count=1)
                # sell_qty = grp.loc[sell_mask, 'est_qty'].sum(min_count=1)

                # if pd.isna(buy_qty): buy_qty = 0.0
                # if pd.isna(sell_qty): sell_qty = 0.0

                # qty_net = buy_qty - sell_qty

                gross_pnl = sell_notional - buy_notional
                net_pnl = gross_pnl - fee_total

                invested = buy_notional if buy_notional > 0 else np.nan
                ret_net = (net_pnl / invested) if pd.notna(invested) and invested != 0 else np.nan

                # avg_buy_price = (buy_notional / buy_qty) if buy_qty > 0 else np.nan
                # avg_sell_price = (sell_notional / sell_qty) if sell_qty > 0 else np.nan

                holding_days = (close_date - open_date).days + 1

                ret_notional = (close_price - open_price) / open_price

                rows.append({
                    'holding_id': hid,
                    'ticker': ticker,
                    'open_date': open_date,
                    'close_date': close_date,
                    'open_quarter': open_quarter,
                    'close_quarter': close_quarter,
                    'open_price': open_price,
                    'close_price': close_price,
                    # 'trades_count': trades_count,
                    'buy_transaction_count': buy_transaction_count,
                    'sell_transaction_count': sell_transaction_count,
                    'win_transaction_count': win_transaction_count,
                    'buy_notional': buy_notional,
                    'sell_notional': sell_notional,
                    'fee_total': fee_total,
                    # 'buy_qty': buy_qty,
                    # 'sell_qty': sell_qty,
                    # 'qty_net': qty_net,
                    'gross_pnl': gross_pnl,
                    'net_pnl': net_pnl,
                    # 'invested': invested,
                    'ret_net': ret_net,
                    'ret_notional': ret_notional,
                    # 'avg_buy_price': avg_buy_price,
                    # 'avg_sell_price': avg_sell_price,
                    'holding_days': holding_days
                })

            pos = pd.DataFrame(rows).sort_values(['open_date', 'holding_id']).reset_index(drop=True)
            # Helpful time fields
            pos['open_month'] = pos['open_date'].dt.to_period('M').astype(str)
            pos['close_month'] = pos['close_date'].dt.to_period('M').astype(str)
            return pos

        def trade_metrics(pos: pd.DataFrame, closed_only: bool = True):
            """
            Compute headline trade-performance metrics from position table.

            Metrics (closed-only by default)
            --------------------------------
            - n_trades, win_rate
            - avg_win, avg_loss
            - profit_factor = sum(win_pnl) / abs(sum(loss_pnl))
            - expectancy    = p(win)*avg_win - p(loss)*avg_loss
            - median_pnl, p25, p75, p90
            - holding_days_mean/median

            Returns
            -------
            pd.Series
            """
            df = pos.copy()
            # if closed_only:
            #     df = df[df['status'] == 'closed'].copy()

            # pnl = df['net_pnl'].dropna()
            pnl = df['ret_net'].dropna()

            pnl_notional = df['ret_notional'].dropna()

            n = len(pnl)
            if n == 0:
                return pd.Series({
                    'n_deals': 0, 'n_buy_transactions': 0, 'n_sell_transactions': 0, 'win_rate_transactions': np.nan,
                    'win_rate_deals': np.nan, 'loss_rate_deals': np.nan, 'win_rate_quarter': np.nan,
                    'avg_win': np.nan, 'avg_loss': np.nan, 'profit_factor': np.nan, 'expectancy': np.nan,
                    'pnl_median': np.nan,
                    'ret_deals': np.nan, 'ret_notional': np.nan,
                    'holding_days_mean': np.nan, 'holding_days_median': np.nan,
                    'set_ticker': [],
                    'set_quarter_ticker': []
                })

            n_sell_transactions = df['sell_transaction_count'].sum()
            n_buy_transactions = df['buy_transaction_count'].sum()
            n_win_transactions = df['win_transaction_count'].sum()
            p_win_transaction = n_win_transactions / n_sell_transactions if n_sell_transactions > 0 else np.nan

            unique_ticker = df['ticker'].unique().tolist()
            unique_quarter_ticker = list(set(zip(df['ticker'], df['open_quarter'])))

            wins = pnl[pnl > 0]
            losses = pnl[pnl < 0]

            p_win = len(wins) / n
            p_loss = len(losses) / n

            p_win_quarter = (wins.groupby(df['open_quarter']).count() / pnl.groupby(
                df['open_quarter']).count() > 0.5).sum() / len(df['open_quarter'].unique())

            avg_win = wins.mean() if len(wins) > 0 else 0.0
            avg_loss = losses.mean() if len(losses) > 0 else 0.0  # negative

            profit_factor = (wins.sum() / abs(losses.sum())) if len(losses) > 0 else np.inf
            expectancy = p_win * avg_win + p_loss * avg_loss  # avg_loss is negative

            holding_days_mean = df['holding_days'].mean() if 'holding_days' in df.columns else np.nan
            holding_days_median = df['holding_days'].median() if 'holding_days' in df.columns else np.nan

            return {
                'n_deals': n,
                'n_buy_transactions': n_buy_transactions,
                'n_sell_transactions': n_sell_transactions,
                'win_rate_transactions': p_win_transaction,
                'win_rate_deals': p_win,
                'loss_rate_deals': p_loss,
                'win_rate_quarter': p_win_quarter,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'expectancy': expectancy,
                'ret_deals': pnl.mean(),
                'ret_notional': pnl_notional.mean(),
                'holding_days_mean': holding_days_mean,
                'holding_days_median': holding_days_median,
                'set_ticker': unique_ticker,
                'set_quarter_ticker': unique_quarter_ticker
            }

        tx = preprocess(transactions_df)
        pos = build_positions(tx)
        tmetrics = trade_metrics(pos, closed_only=True)

        return {
            # 'tx': tx,
            'pos': pos,
            'tmetrics': tmetrics,
        }

    def stats(self, ann_vnindex=None, detail=False):
        logs_df = pd.DataFrame(self.portfolio.log)
        transactions_df = pd.DataFrame(self.portfolio.transactions)
        # DEBUG
        # logs_df.to_csv('debug_logs_df.csv', index=False)
        # transactions_df.to_csv('debug_transactions_df.csv', index=False)

        # Complete all holdings
        hold_transactions = []
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        for ticker, row in self.portfolio.holdings.items():
            original_buy_amount = row['investment_amount'] * row['holding_amount'] / \
                                  row['holding_amount']
            fee = row['holding_amount'] * self.portfolio.fee_sell_rate
            hold_transactions.append({
                'ymd': now,
                'ticker': ticker,
                'holding_id': row['holding_id'],
                'action': 'sell',
                'adj_price': row['adj_price'],
                'buy_amount': original_buy_amount,
                'sell_amount': row['holding_amount'],
                'fee': fee,
                'buy_pattern': row.get('buy_pattern', 'unknown'),
                'sell_pattern': 'hold',
            })

        transactions_df = pd.concat([transactions_df, pd.DataFrame(hold_transactions)], ignore_index=True)

        stats_log = self.stat_logs(logs_df, ann_vnindex)
        stats_tx = self.stat_transactions(transactions_df)

        results = {
            'stats_log': stats_log,
            'stats_tx': stats_tx
        }

        if detail:
            results['daily'] = self.portfolio.log
            results['transactions'] = self.portfolio.transactions

        return results
