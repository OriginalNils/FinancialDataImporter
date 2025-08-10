import os
import pandas as pd
import yfinance as yf
import pickle
from abc import ABC, abstractmethod # Für die abstrakte Basisklasse

class DataSource(ABC):
    @abstractmethod
    def get_historical_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_fundamentals(self, ticker: str) -> dict:
        pass

class YahooFinanceSource(DataSource):
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        print(f"YahooFinanceSource: Cache directory is used: {self.cache_dir}")

    def get_historical_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        cache_path = os.path.join(self.cache_dir, f"{ticker}_{start_date}_{end_date}.pkl")
        if os.path.exists(cache_path):
            print(f"Loading historical data for '{ticker}' from the cache...")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)

        print(f"Loading historical data for '{ticker}' from Yahoo Finance...")
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
        if data.empty:
            raise ValueError(f"No historical data found for '{ticker}'")
        
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        return data

    def get_fundamentals(self, ticker: str) -> dict:
        cache_path = os.path.join(self.cache_dir, f"{ticker}_fundamentals.pkl")
        if os.path.exists(cache_path):
            print(f"Loading historical data for '{ticker}' from the cache...")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)

        print(f"Loading historical data for '{ticker}' from Yahoo Finance...")
        stock = yf.Ticker(ticker)
        fundamentals = stock.info
        
        with open(cache_path, 'wb') as f:
            pickle.dump(fundamentals, f)
        return fundamentals
    
    def get_option_expiration_dates(self, ticker: str) -> tuple:
        print(f"Retrieval of expiry dates for {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            # .options returns a tuple containing all data
            return stock.options
        except Exception as e:
            print(f"Retrieval of expiry dates for {ticker}: {e}")
            return ()
        
    def get_option_chain(self, ticker: str, expiration_date: str):
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
    
    # Hinweis: get_option_chain etc. könnten hier auf dieselbe Weise hinzugefügt werden.

class AlphaVantageSource(DataSource):
    def __init__(self, api_key: str, cache_dir: str = "cache"):
        self.api_key = api_key
        # ...

    def get_historical_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        print(f"Loading data for {ticker} from Alpha Vantage...")

        raise NotImplementedError("Alpha Vantage logic has not yet been implemented.")
    
    def get_fundamentals(self, ticker: str) -> dict:
        raise NotImplementedError("Alpha Vantage logic has not yet been implemented.")
    
    def clear_cache(self):
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