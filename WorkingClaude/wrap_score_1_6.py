import os
import sys

import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = current_dir.replace("/core_utils", "")
os.chdir(current_dir)
sys.path.insert(0, current_dir)

score_config = {
    "score_col": "score",
    "score_sell": 0,
    "score_buy": 1,
    # "fa_option": "A",
    'score_rank_col': 'order_rank',
    "buy_sell_from_pattern": True,
}


class ScoreManager:
    def __init__(self, config, score_col='score', validation_probs=None, validation_labels=None):
        self.config = config
        # self.validation_probs = None
        # self.validation_labels = None

        # self.market_eval = None
        # self.score_engine = None
        self.score_col = score_col

    def _has_market_exit_signal(self, sell_pattern):
        if not self.config["market_sell_patterns"]:
            return False
        if sell_pattern is None:
            return False
        if np.isscalar(sell_pattern):
            if pd.isna(sell_pattern):
                return False
            return isinstance(sell_pattern, str) and sell_pattern in self.config["market_sell_patterns"]
        if isinstance(sell_pattern, (list, tuple, set, np.ndarray, pd.Series)):
            return any(isinstance(p, str) and p in self.config["market_sell_patterns"] for p in sell_pattern)
        return False

    def buy_sell_from_pattern_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply sell pattern scores to dataframe.
        Only apply sell pattern score if there is no buy pattern.
        """

        required_columns = ["sell_pattern", "buy_pattern"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
            return df

        def has_special_pattern(pattern) -> bool:
            """
            Check if a pattern is considered 'special' (ends with '_special').
            """
            if pattern is None or (isinstance(pattern, float) and np.isnan(pattern)):
                return False
            if isinstance(pattern, str):
                return pattern.endswith('_special')
            if isinstance(pattern, (list, tuple, set, np.ndarray, pd.Series)):
                return any(
                    isinstance(p, str) and p.endswith('_special')
                    for p in pattern
                )
            return False

        def extend_mask(mask: pd.Series, sessions: int) -> pd.Series:
            """
            Extend the mask for a given session window, using 'ticker' for grouped rolling windows if available.
            """
            window = sessions + 1
            mask_bool = mask.fillna(False).astype(bool)
            if mask_bool.empty:
                return mask_bool

            mask_int = mask_bool.astype(int)
            if 'ticker' in df.columns:
                grouped = pd.DataFrame({'ticker': df['ticker'], 'mask': mask_int})
                extended = grouped.groupby(
                    'ticker',
                    sort=False,
                    observed=True,
                    dropna=False,
                )['mask'].transform(lambda s: s.rolling(window=window, min_periods=1).max())
                return extended.fillna(0).astype(bool)
            return mask_int.rolling(window=window, min_periods=1).max().astype(bool)

        # Create masks for buy patterns
        buy_base_mask = df['buy_pattern'].notnull().astype(bool)
        buy_special_mask = df['buy_pattern'].apply(has_special_pattern)
        buy_regular_mask = buy_base_mask & ~buy_special_mask

        # Combine buy masks with extended windows
        # buy_mask = extend_mask(buy_special_mask, sessions=10) | extend_mask(buy_regular_mask, sessions=3)
        buy_mask_special = extend_mask(buy_special_mask, sessions=10)
        buy_mask_regular = extend_mask(buy_regular_mask, sessions=3)

        # Create sell mask (no extension needed)
        sell_mask = df['sell_pattern'].notnull().astype(bool)
        market_sell_mask = df['sell_pattern'].apply(self._has_market_exit_signal)
        market_sell_mask = extend_mask(market_sell_mask, sessions=11)

        # Apply buy and sell scores
        df.loc[buy_mask_regular, self.score_col] = self.config["score_buy"] + df.loc[
            buy_mask_regular, self.config['score_rank_col']] / 100.

        df.loc[buy_mask_special, self.score_col] = 2 * self.config["score_buy"] + df.loc[
            buy_mask_special, self.config['score_rank_col']] / 100.

        df.loc[sell_mask, self.score_col] = self.config["score_sell"] - 1
        df.loc[market_sell_mask, self.score_col] = -10

        # df.loc[~buy_mask & sell_mask, self.score_col] = self.config["score_sell"]

        return df

    def fundamental_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply a fundamental screening and adjust scores.

        Notes (keeping original semantics):
        - fa_flag: True by default; rows FAILING the screen become False.
        - fa_option "A": set score = score_sell for failing rows.
        - fa_option "B": score = min(score, score_buy) for failing rows.
        """

        required = [
            "CF_OA_5Y", "OShares", "FSCORE", "NP_P0", "NP_P1", "NP_P4",
            "PCF", "PB", "PE", "ROE5Y", "ROE_Min3Y"
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise KeyError(f"Missing columns: {missing}")

        # # Convert numeric columns once (invalid -> NaN so they naturally fail screening)
        # num_cols = ["CF_OA_5Y", "OShares", "FSCORE", "NP_P0", "NP_P1", "NP_P4",
        #             "PCF", "PB", "PE", "ROE5Y", "ROE_Min3Y"]
        # df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

        def safe_div(a, b):
            # Avoid division-by-zero; NaN -> fails numeric tests cleanly
            b = b.replace({0: np.nan}).astype(float)
            return a.astype(float) / b

        mask_pass = (
                (safe_div(df["CF_OA_5Y"], df["OShares"]) > 2500) &
                (df["FSCORE"] >= 3) &
                (df["NP_P0"] > 0) &
                (df["PCF"].between(0.4, 30.2)) &
                (df["PB"] < 4.6) &
                (df["PE"] > 0) &
                (df["ROE5Y"] > 0.05) &
                (df["ROE_Min3Y"] > 0.01)
        )

        # fa_flag: True by default; False for failing rows (same semantics as before)
        df["fa_flag"] = True

        opt = (self.config.get("fa_option") or "").upper()
        if opt == "A":
            df.loc[~mask_pass, self.score_col] = self.config["score_sell"]
        elif opt == "B":
            # Take elementwise min(score, score_buy) for failing rows
            df.loc[~mask_pass, self.score_col] = np.minimum(
                df.loc[~mask_pass, self.score_col].to_numpy(dtype="float64"),
                float(self.config["score_buy"])
            )
        elif opt == "C":
            df.loc[~mask_pass, "fa_flag"] = False

        return df

    def run(self, df):
        # Ensure time column is datetime (UTC-naive) for accurate comparison
        if not np.issubdtype(df["time"].dtype, np.datetime64):
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df[df["time"].notna()]

        df[self.score_col] = 0.5

        # Apply fundamental screening and adjust scores
        # Step: from_pattern_score -> fundamental_filter -> buy_from_pattern_score
        if self.config.get("buy_sell_from_pattern"):
            df = self.buy_sell_from_pattern_score(df)

        df["fa_flag"] = True
        # df = self.fundamental_filter(df)

        # Select and return final output columns (keep original order)
        out_cols = [
            "time", "ticker", "close", "open", "price", "volume", "volume_1m_p50",
            self.score_col, "buy_pattern", "sell_pattern"
        ]

        if "fa_flag" in df.columns:
            out_cols.append("fa_flag")

        return df.loc[:, out_cols]
