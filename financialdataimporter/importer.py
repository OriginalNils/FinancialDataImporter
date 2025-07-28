import os
import pandas as pd
import yfinance as yf
from datetime import datetime

class YahooFinanceImporter:
    # Class to cash and download finance data from Yahoo Finance
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize Importer.

        Args:
            cache_dir (str): Name of directory of cache files.
        """
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _validate_dates(self, start_date: str, end_date: str):
        """
        Catch of date errors.
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError(
                f"Invalid date format. Please use 'YYYY-MM-DD' and ensure that the dates are valid."
            )

        if start_dt > end_dt:
            raise ValueError(
                f"The start date ({start_date}) must not be after the end date ({end_date})."
            )
        
        if start_dt > datetime.now():
            raise ValueError(
                f"The start date ({start_date}) is in the future. Future dates cannot be retrieved."
            )

    def get_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Retrieves historical price data for a specific ticker and time period.
        First checks the cache and downloads the data from the API if necessary.

        Args:
            ticker (str): ticker symbol.
            start_date (str): start date in format 'YYYY-MM-DD'.
            end_date (str): end date in format 'YYYY-MM-DD'.

        Returns:
            pd.DataFrame: A DataFrame containing historical price data
                          (Open, High, Low, Close, Adj Close, Volume).
        
        Raises:
            ValueError: If the ticker is invalid or no data was found.
        """
        
        filename = f"{ticker}_{start_date}_{end_date}.csv"
        cache_path = os.path.join(self.cache_dir, filename)

        if os.path.exists(cache_path):
            print(f"Load '{ticker}' from cache...")
            data = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            return data

        print(f"Load '{ticker}' from yfinance API...")
        try:
            data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
            
            if data.empty:
                raise ValueError(f"No data found for ticker '{ticker}'. Is the ticker symbol correct?")

        except Exception as e:
            print(f"Error downloading data: {e}")
            raise

        if isinstance(data.columns, pd.MultiIndex):
            print("...Clean up multi-level header...")
            data.columns = data.columns.get_level_values(0)

        print(f"Save '{ticker}' in cache...")
        data.to_csv(cache_path)

        return data