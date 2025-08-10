import os
import pandas as pd
import yfinance as yf
from datetime import datetime
import pickle

class YahooFinanceImporter:
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize Importer.

        Args:
            cache_dir (str): Name of directory of cache files.
        """
        if cache_dir is None:
            self.cache_dir = os.path.join(os.getcwd(), "cache")
        else:
            self.cache_dir = cache_dir
        
        print(f"Cache directory is used: {self.cache_dir}")
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
    
    def get_fundamentals(self, ticker: str) -> dict:
        """
        Retrieves a dictionary containing fundamental key figures for a ticker.

        Args:
            ticker (str): The ticker symbol.

        Returns:
            dict: A dictionary containing fundamental data.
        """
        cache_path = os.path.join(self.cache_dir, f"{ticker}_fundamentals.pkl")

        if os.path.exists(cache_path):
            print(f"Loading fundamental data for “{ticker}” from cache...")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)

        print(f"Retrieval of fundamental data for {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            fundamentals = stock.info
            
            print(f"Save fundamental data for “{ticker}” in the cache...")
            with open(cache_path, 'wb') as f:
                pickle.dump(fundamentals, f)
            
            return fundamentals
        except Exception as e:
            print(f"Error retrieving fundamental data for {ticker}: {e}")
            return {}
        
    def get_option_expiration_dates(self, ticker: str) -> tuple:
        """
        Returns all available expiry dates for the options of a ticker.

        Args:
            ticker (str): The ticker symbol.

        Returns:
            tuple: A tuple of strings with the expiry dates.
        """
        print(f"Retrieval of expiry dates for {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            # .options returns a tuple containing all data
            return stock.options
        except Exception as e:
            print(f"Retrieval of expiry dates for {ticker}: {e}")
            return ()


    def get_option_chain(self, ticker: str, expiration_date: str):
        """
        Retrieves the entire option chain (calls and puts) for a specific expiration date.

        Args:
            ticker (str): The ticker symbol.
            expiration_date (str): A valid expiration date in the format “YYYY-MM-DD”.

        Returns:
            Options object: An object with .calls and .puts as attributes, which are DataFrames.
        """
        cache_path = os.path.join(self.cache_dir, f"{ticker}_option_{expiration_date}.pkl")

        if os.path.exists(cache_path):
            print(f"Loading option chain for “{ticker}” for {expiration_date} from cache...")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)

        print(f"Retrieving the option chain for {ticker} on {expiration_date}...")
        try:
            stock = yf.Ticker(ticker)
            option_chain_object = stock.option_chain(expiration_date)

            data_to_cache = {
                'calls': option_chain_object.calls,
                'puts': option_chain_object.puts
            }

            print(f"Caching option chain for '{ticker}'...")
            with open(cache_path, 'wb') as f:
                pickle.dump(data_to_cache, f)

            return data_to_cache
            
        except Exception as e:
            # The original error message was a bit hidden, let's make it clearer
            print(f"Error retrieving option chain for {ticker}: {e}")
            return None
    
    def clear_cache(self):
        """
        Deletes all files in the cache directory.
        """
        print(f"Clearing cache at: {self.cache_dir}")
        files_deleted = 0
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    files_deleted += 1
            print(f"Cache cleared. {files_deleted} files deleted.")
        except Exception as e:
            print(f"Error clearing cache: {e}")
