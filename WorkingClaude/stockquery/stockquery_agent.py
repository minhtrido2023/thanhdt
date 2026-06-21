import datetime
import time

import pandas as pd
import requests
from requests import exceptions as req_exc
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from vnstock.explorer.kbs.quote import Quote as KbsQuote
from vnstock.explorer.vci.listing import Listing as VciListing
from vnstock.explorer.vci.quote import Quote as VciQuote

from core_utils.log import get_logger


logger = get_logger(__name__)

TRANSIENT_EXC = (
    req_exc.ConnectionError,
    req_exc.Timeout,
    req_exc.ChunkedEncodingError,
)


class StockBase:
    def _handle_error(self, error):
        """General error handling function."""
        if isinstance(error, TRANSIENT_EXC):
            logger.error(f"Connection error to the API: {error}")
        else:
            logger.error(f"Unknown error: {str(error)}", exc_info=True)

    def execute_query(self, func, *args, max_retries=2, initial_delay=5, **kwargs):
        """
        Execute function with Exponential Backoff logic.

        Args:
            func: Function to execute.
            *args, **kwargs: Arguments for the function.
            max_retries (int): Number of retry attempts.
            retry_delay (int): Seconds to wait before retrying.
        """
        attempt = 0
        while True:
            try:
                response = func(*args, **kwargs)
                if hasattr(response, "raise_for_status"):
                    response.raise_for_status()
                return response

            except (KeyError, ValueError, TypeError) as e:
                # Error in data format -> NO RETRY
                logger.error(
                    f"Data format wrong inside {func.__name__}: {e}", exc_info=True
                )
                raise e
            # ---------------------

            except req_exc.HTTPError as e:
                status = getattr(e.response, "status_code", None)
                if status not in (429, 500, 502, 503, 504):
                    self._handle_error(e)
                    raise e

                if attempt >= max_retries:
                    logger.error(
                        f"[Give Up] Max retries ({max_retries}) reached for HTTPError: {str(e)}"
                    )
                    raise ConnectionError(
                        f"Max retries reached: {str(e)}"
                    )  # builtin Celery pickle

                # Calculate wait time (Exponential Backoff)
                wait_time = initial_delay * (3 ** attempt)
                logger.warning(
                    f"[Retry {attempt + 1}/{max_retries}] HTTP {status}. Waiting {wait_time}s..."
                )

                time.sleep(wait_time)
                attempt += 1

            except TRANSIENT_EXC as e:
                if attempt > max_retries:
                    logger.error(
                        f"[Give Up] Max retries ({max_retries}) reached for Connection Error: {str(e)}"
                    )
                    raise e  # builtin Celery pickle

                wait_time = initial_delay * (3 ** attempt)
                logger.warning(
                    f"[Retry {attempt + 1}/{max_retries}] Connection Error. Waiting {wait_time}s..."
                )

                time.sleep(wait_time)
                attempt += 1

            except Exception as e:
                self._handle_error(e)
                raise

    def _create_retry_session(
            self,
            retries: int = 3,
            backoff_factor: float = 5.0,
            status_forcelist=(429, 500, 502, 503, 504),
    ):
        # sleep = backoff_factor * (2 ** (retry_number - 1))
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            status=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=frozenset(["GET", "POST"]),
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _safe_call(self, func, params, text, warnings):
        try:
            return func(**params)
        except Exception as e:
            msg = f"[{text} FAILED]: {e}"
            logger.error(msg, exc_info=True)
            warnings.append(msg)
            return None


# Example of inheriting this base class
class StockQuery(StockBase):
    def __init__(self, start_date="2000-01-01", end_date=None):
        self.proxy_mode = None
        self.proxy_list = None

        self.ticker = None

        self.vci_quote = None
        self.kbs_quote = None
        self.vci_finance = None
        self.kbs_finance = None

        self.start_date = start_date
        self.session = self._create_retry_session()

        if end_date:
            self.end_date = end_date
        else:
            self.end_date = (
                    datetime.datetime.today() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d")

    def update_ticker(self, ticker):
        """Fetch stock data using the vnstock3 library."""
        self.ticker = ticker
        try:
            self.vci_quote = self._create_vci_quote(ticker)
        except Exception as e:
            logger.warning(
                f"Failed to update VCI quote for {ticker}: {e}", exc_info=True
            )
            self.vci_quote = None

        try:
            self.kbs_quote = self._create_kbs_quote(ticker)
        except Exception as e:
            logger.warning(
                f"Failed to update KBS quote for {ticker}: {e}", exc_info=True
            )
            self.kbs_quote = None

    def _create_vci_quote(self, symbol, proxy_mode=None):
        return VciQuote(
            symbol,
            random_agent=False,
            show_log=False,
            proxy_mode=proxy_mode,
            proxy_list=self.proxy_list,
        )

    def _create_kbs_quote(self, symbol, proxy_mode=None):
        return KbsQuote(
            symbol,
            random_agent=False,
            show_log=False,
            proxy_mode=proxy_mode,
            proxy_list=self.proxy_list,
        )

    def symbols_by_exchange(self):
        try:
            return self.execute_query(
                VciListing(random_agent=True, show_log=False).symbols_by_exchange
            )
        except Exception as e:
            logger.error(f"Failed to get symbols by exchange: {e}", exc_info=True)
            return self.execute_query(
                VciListing(
                    random_agent=True, show_log=False, proxy_mode="auto"
                ).symbols_by_exchange
            )

    def symbols_by_industries(self):
        try:
            return self.execute_query(
                VciListing(random_agent=True, show_log=False).symbols_by_industries
            )

        except Exception as e:
            logger.error(f"Failed to get symbols by industries: {e}", exc_info=True)
            return self.execute_query(
                VciListing(
                    random_agent=True, show_log=False, proxy_mode="auto"
                ).symbols_by_industries
            )

    def symbols_by_group(self, group):
        try:
            return self.execute_query(
                VciListing(random_agent=True, show_log=False).symbols_by_group,
                group,
            )

        except Exception as e:
            logger.error(f"Failed to get symbols by industries: {e}", exc_info=True)
            return self.execute_query(
                VciListing(
                    random_agent=True, show_log=False, proxy_mode="auto"
                ).symbols_by_group,
                group,
            )

    def get_historical_ticker(self, ticker, interval, start_date=None) -> pd.DataFrame:
        """
        Fetch historical stock data using the vnstock3 library.
        :param ticker: ticker symbol
        :param start_date: start date in YYYY-MM-DD format
        :param interval: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M
        :return: pd.DataFrame
        """
        if start_date is None:
            start_date = self.start_date
        try:
            if ticker != self.ticker:
                self.update_ticker(ticker)

            df = self.execute_query(
                self.vci_quote.history,
                start=start_date,
                end=self.end_date,
                interval=interval,
                count_back=None,
            )
            if df is None or len(df) == 0:
                raise ValueError("Empty DataFrame returned from VCI")
        except Exception as e:
            logger.warning(
                f"Failed to get historical ticker with VCI for {ticker}:", exc_info=True
            )
            df = self.execute_query(
                self.kbs_quote.history,
                start=start_date,
                end=self.end_date,
                interval=interval,
                count_back=None,
            )
            if df is None or len(df) == 0:
                logger.error(
                    f"Failed to get historical ticker for {ticker}:",
                    exc_info=True,
                )
                raise ValueError(
                    f"Failed to get historical data for {ticker} from both VCI and KBS: {e}"
                )
            index_symbols = ["VNINDEX", "VN30", "HNXINDEX", "HNX30", "UPCOMINDEX"]
            if ticker.upper() in index_symbols:
                df["close"] = df["close"] * 1000
                df["open"] = df["open"] * 1000
                df["high"] = df["high"] * 1000
                df["low"] = df["low"] * 1000

        df = df.dropna(subset=["close", "open", "high", "low"])

        if interval[-1] in ["D", "W", "M"]:
            df["time"] = df["time"].dt.strftime("%Y-%m-%d")
            df = df.drop_duplicates(subset=["time"], keep="first")

        df = df.reset_index(drop=True)
        return df

    def get_historical_symbol(
            self, symbol, start_date=None, interval="1D"
    ) -> pd.DataFrame:
        df = self.get_historical_ticker(symbol, interval, start_date)

        return df

    def get_enrich_vnindex(self):
        url = "https://cafef.vn/du-lieu/Ajax/PageNew/FinanceData/GetDataChartPE.ashx"
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # RuntimeError will be caught by caller or crash app, can consider logging here too if needed
            logger.error(f"Failed to fetch PE data from cafef: {e}", exc_info=True)
            raise RuntimeError(f"Failed to fetch PE data: {e}")

        response = response.json()["Data"]["DataChart"]
        df_00 = pd.json_normalize(response)

        # df_00['time'] = df_00['TimeStamp'].agg(lambda x: datetime.datetime.fromtimestamp(x))
        df_00["time"] = df_00["Time"].str.extract(r"(\d+)").astype("int")
        df_00["time"] = df_00["time"].apply(
            lambda x: datetime.datetime.fromtimestamp(x / 1000)
        )
        df_00["time"] = df_00["time"].dt.strftime("%Y-%m-%d")
        df_00 = df_00.drop_duplicates(subset=["time"], keep="first").reset_index(
            drop=True
        )

        # get trading_session
        df_01 = self.get_unadjust_price("VNINDEX")
        df_01["trading_session"] = df_01["GiaTriKhopLenh"].copy()
        df_01["trading_session"] = df_01[
                                       "trading_session"] * 1e+9  # convert from billion VND to VND to match the unit of volume_session
        df_01["volume_session"] = df_01["KhoiLuongKhopLenh"].copy()

        df = df_01[["time", "trading_session", "volume_session"]].merge(
            df_00, on="time", how="left"
        )
        return df

    def get_unadjust_price(self, ticker, exchange_type="HOSE"):
        """Get price date isn't adjusted"""

        url = "https://cafef.vn/du-lieu/Ajax/PageNew/DataHistory/PriceHistory.ashx"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://s.cafef.vn/",
        }
        try:
            response = self.session.get(
                url,
                params={
                    "ExchangeType": exchange_type,
                    "Symbol": ticker,
                    "StartDate": self.start_date,
                    "PageSize": 10000,
                },
                headers=headers,
                timeout=200,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to fetch unadjusted price data for {ticker}: {e}",
                exc_info=True,
            )
            raise RuntimeError(
                f"Failed to fetch unadjusted price data for {ticker}: {e}"
            )

        response = response.json()["Data"]["Data"]
        df = pd.json_normalize(response)

        df["time"] = pd.to_datetime(df["Ngay"], format="%d/%m/%Y", errors="coerce")
        df = df.dropna(subset=["time"])
        df["time"] = df["time"].dt.strftime("%Y-%m-%d")
        df = df.sort_values("time", ascending=True)
        df = df.drop_duplicates(subset=["time"], keep="first").reset_index(drop=True)

        return df


if __name__ == "__main__":
    vnsto = StockQuery()
    #
    # df = vnsto.get_unadjust_price('HPG')
    # df = vnsto.get_enrich_vnindex()
    # 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M
    vnsto.get_historical_symbol(symbol='VNINDEX', interval='15m')
    #
    vnsto.symbols_by_exchange()
    vnsto.symbols_by_industries()
    vnsto.symbols_by_group('VN30')
    vnsto.symbols_by_group('CT')
    #
    # stock = Vnstock().stock(symbol='VNINDEX', source='VCI')
    pass
