from .sources import DataSource

class FinancialDataImporter:
    def __init__(self, source: DataSource):
        """
        Initialises the importer with a specific data source.

        Args:
        source (DataSource): An object that inherits from the DataSource class
        (e.g. an instance of YahooFinanceSource).
        """
        if not isinstance(source, DataSource):
            raise TypeError("The source must be an instance of a DataSource class.")
        self.source = source

    def get_data(self, ticker: str, start_date: str, end_date: str):
        return self.source.get_historical_data(ticker, start_date, end_date)

    def get_fundamentals(self, ticker: str):
        return self.source.get_fundamentals(ticker)
    
    def clear_cache(self):
        return self.source.clear_cache()
    
    def get_opt_exp_dates(self, ticker: str):
        return self.source.get_option_expiration_dates(ticker)
    
    def get_opt_chain(self, ticker: str, expiration_date: str):
        return self.source.get_option_chain(ticker, expiration_date)