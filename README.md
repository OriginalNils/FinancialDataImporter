# 📈 Financial Data Importer

A simple yet robust Python package for downloading and caching historical stock prices from Yahoo Finance and Alpha Vantage. This module is designed to maximize code reusability and accelerate financial analysis projects.



## ✨ Key Features

- **Comprehensive Data Retrieval:** Fetch various types of financial data, including:
    - Historical Prices (OHLCV)
    - Fundamental Company Data (P/E, Sector, Market Cap, etc.)
    - Complete Option Chains (Calls and Puts)
- **Flexible, Modular Design:**  Built with a clean, object-oriented architecture that supports multiple data sources. The current implementation uses Yahoo Finance and Alpha Vantage. AV has not been tested with a premium API key.
- **Intelligent Caching:** Automatically caches all downloaded data (prices, fundamentals, options) as local files (`.pkl`). This minimizes API requests, avoids rate limits, and dramatically speeds up repeated data calls.
- **Configurable & Manageable Cache:** You can easily specify a custom directory for all cached files. A built-in `clear_cache()` method allows for simple cache management.
- **Robust Validation:** Prevents common errors by validating user inputs (like date ranges) before making an API request, providing clear and helpful error messages.


## 🚀 Installation

To use the package, clone the repository and install it using pip.

```bash
# 1. Clone the repository
git clone https://github.com/OriginalNils/FinancialDataImporter.git

# 2. Navigate into the directory
cd FinancialDataImporter

# 3. Install the package in editable mode
pip install -e .
```
    
## 💻 Usage Example

The new modular structure makes using the importer very flexible. The key is to first instantiate a specific data source (like `YahooFinanceSource`) and then pass it to the main FinancialDataImporter. Right now there is just YahooFinance as a secured data source, Alpha Vantage did not got tested with an Premium API Key.

Here's how to use it with the Yahoo Finance data source:

#### Example 1: Fetching Historical Price Data
This is the most common use case: getting the OHLCV (Open, High, Low, Close, Volume) data for a stock.

```python
from financialdataimporter import FinancialDataImporter, YahooFinanceSource

# 1. Choose and configure the data source
yf_source = YahooFinanceSource(cache_dir="stock_cache")

# 2. Initialize the main importer with the source
importer = FinancialDataImporter(source=yf_source)

# 3. Fetch the data
try:
    print("Fetching historical data for Apple (AAPL)...")
    price_data = importer.get_data('AAPL', '2025-01-01', '2025-08-08')
    print(price_data.tail()) # Show the last 5 days
except Exception as e:
    print(f"An error occurred: {e}")
```

#### Example 2: Fetching Fundamental Company Data
This example shows how to get a dictionary of key metrics for a company, such as its sector, P/E ratio, and dividend yield.

```python
from financialdataimporter import FinancialDataImporter, YahooFinanceSource

yf_source = YahooFinanceSource(cache_dir="stock_cache")
importer = FinancialDataImporter(source=yf_source)

try:
    print("Fetching fundamental data for Microsoft (MSFT)...")
    fundamentals = importer.get_fundamentals('MSFT')
    
    if fundamentals:
        print(f"Company: {fundamentals.get('longName')}")
        print(f"Sector: {fundamentals.get('sector')}")
        print(f"P/E Ratio: {fundamentals.get('trailingPE')}")
        print(f"Market Cap: {fundamentals.get('marketCap'):,}")

except Exception as e:
    print(f"An error occurred: {e}")
```

#### Example 3: Working with Option Chains
This example demonstrates the two-step process for fetching option data: first, you get the available expiration dates, and then you fetch the option chain for a specific date.

```python
from financialdataimporter import FinancialDataImporter, AlphaVantageSource

av_source = AlphaVantageSource(api_key=AV_API_KEY)
importer = FinancialDataImporter(source=av_source)

try:
    print("Fetching option data for NVIDIA (NVDA)...")
    
    # Step 1: Get all available expiration dates
    exp_dates = av_source.get_option_expiration_dates('NVDA') # Using the source directly
    
    if not exp_dates:
        print("No option expiration dates found.")
    else:
        print(f"Available expiration dates: {exp_dates[:5]}...")
        
        # Step 2: Fetch the full option chain for the next expiration date
        next_expiration = exp_dates[0]
        option_data = av_source.get_option_chain('NVDA', next_expiration) # Using the source directly
        
        if option_data:
            print(f"\n--- Call Options expiring on {next_expiration} ---")
            print(option_data['calls'].head())
            
            print(f"\n--- Put Options expiring on {next_expiration} ---")
            print(option_data['puts'].head())

except Exception as e:
    print(f"An error occurred: {e}")
```

#### Example 4: Clearing the Cache
If you need to force a fresh download of all data, you can use the `clear_cache` method on your data source object. This will delete all files within the specified cache directory.

```python
from financialdataimporter import FinancialDataImporter, AlphaVantageSource

# 1. Choose and configure the data source
# We use a specific cache folder for this example
av_source = AlphaVantageSource(api_key=AV_API_KEY)
importer = FinancialDataImporter(source=av_source)

# --- Run 1: Fetches data from the API and creates a cache file ---
print("--- FIRST RUN ---")
importer.get_data('MSFT', '2025-01-01', '2025-03-01')

# --- Run 2: Loads the same data from the cache ---
print("\n--- SECOND RUN ---")
importer.get_data('MSFT', '2025-01-01', '2025-03-01')

# --- Clear the cache ---
print("\n--- CLEARING CACHE ---")
# Note: The clear_cache method is called on the source object
av_source.clear_cache()

# --- Run 3: The cache is empty, so it fetches from the API again ---
print("\n--- THIRD RUN ---")
importer.get_data('MSFT', '2025-01-01', '2025-03-01')
```


## 🛡️ Error Handling

The module catches invalid inputs and provides clear error messages instead of crashing.

#### Example of an invalid input:
```python
importer.get_data('MSFT', '2025-08-01', '2025-01-01')
```

#### Resulting Output:

```bash
ValueError: The start date (2025-08-01) cannot be after the end date (2025-01-01).
```
## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.