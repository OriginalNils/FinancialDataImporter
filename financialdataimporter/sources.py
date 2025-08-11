import os
import pandas as pd
import yfinance as yf
import pickle
from abc import ABC, abstractmethod
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

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
        # Use .csv for price data as it's more standard
        cache_path = os.path.join(self.cache_dir, f"{ticker}_{start_date}_{end_date}.csv")
        
        if os.path.exists(cache_path):
            print(f"Loading historical data for '{ticker}' from cache...")
            # Load from CSV, ensuring the first column is the index
            return pd.read_csv(cache_path, index_col=0, parse_dates=True)

        print(f"Downloading historical data for '{ticker}' from Yahoo Finance...")
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
        
        if data.empty:
            raise ValueError(f"No historical data found for '{ticker}'.")
        
        standard_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
        data.columns = standard_columns

        print(f"Caching historical data for '{ticker}'...")
        data.to_csv(cache_path)
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


class AlphaVantageSource(DataSource):
    def __init__(self, api_key: str, cache_dir: str = "alpha_vantage_cache"):
        if not api_key:
            raise ValueError("An Alpha Vantage API key is required.")
        self.api_key = api_key
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        print(f"AlphaVantageSource: Cache directory is used: {self.cache_dir}")
        
        self._ts = TimeSeries(key=self.api_key, output_format='pandas')
        self._fd = FundamentalData(key=self.api_key, output_format='pandas')

    def get_historical_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        cache_path = os.path.join(self.cache_dir, f"AV_{ticker}_history.pkl")
        if os.path.exists(cache_path):
            print(f"Loading historical data for “{ticker}” from the Alpha Vantage cache...")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)

        print(f"Loading historical data for “{ticker}” from Alpha Vantage...")
        data, _ = self._ts.get_daily_adjusted(symbol=ticker, outputsize='full')

        data.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. adjusted close': 'Adj Close',
            '6. volume': 'Volume'
        }, inplace=True)
        
        data.index = pd.to_datetime(data.index)
        
        data = data.loc[start_date:end_date]
        
        data.sort_index(inplace=True)

        if data.empty:
            raise ValueError(f"No historical data found for “{ticker}” from Alpha Vantage.")
        
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        return data
    
    def get_fundamentals(self, ticker: str) -> dict:
        cache_path = os.path.join(self.cache_dir, f"AV_{ticker}_fundamentals.pkl")
        if os.path.exists(cache_path):
            print(f"Loading fundamental data for “{ticker}” from the Alpha Vantage cache...")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)

        print(f"Loading fundamental data for “{ticker}” from Alpha Vantage...")
        try:
            data, _ = self._fd.get_company_overview(symbol=ticker)
            fundamentals = data.T.to_dict()[0]
            
            with open(cache_path, 'wb') as f:
                pickle.dump(fundamentals, f)
            return fundamentals
        except Exception as e:
            print(f"Error retrieving fundamental data from Alpha Vantage: {e}")
            return {}
    
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