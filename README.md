# 📈 Financial Data Importer

A simple yet robust Python package for downloading and caching historical stock prices from Yahoo Finance. This module is designed to maximize code reusability and accelerate financial analysis projects.



## ✨ Key Features

- **Simple Data Fetching**: Load historical price data with a single function call.
- **Intelligent Caching**: Minimizes API requests with a local, file-based caching system.
- **Configurable Cache**: Specify a custom directory for cached files, or let it default to a cache folder in your current working directory.
- **Built-in Validation**: Automatically checks for correct date formats and logical consistency to prevent common errors.
- **Standardized Format**: Always returns data as a clean pandas.DataFrame.


## 🚀 Installation

To use the package, clone the repository and install it using pip.

```bash
# 1. Clone the repository
git clone https://github.com/your_username/FinancialDataImporter.git

# 2. Navigate into the directory
cd FinancialDataImporter

# 3. Install the package in editable mode
pip install -e .
```
    
## 💻 Usage Example

The importer can be used with its default settings or with a custom cache location.

#### Default Behavior
If you don't specify a `cache_dir`, a cache folder will be created in the same directory where you run your script.

```python
from financialdataimporter import YahooFinanceImporter

# This will create a './cache/' folder in your current directory
importer = YahooFinanceImporter()

stock_data = importer.get_data('AAPL', '2025-01-01', '2025-07-25')
print(stock_data.head())
```

#### Custom Cache Directory
Provide a path to the cache_dir argument to use a specific, centralized cache location

```python
from financialdataimporter import YahooFinanceImporter

# All cache files will be stored in this specific folder
custom_path = "/path/to/your/global_cache"
importer = YahooFinanceImporter(cache_dir=custom_path)

stock_data = importer.get_data('TSLA', '2025-01-01', '2025-07-25')
print(stock_data.head())
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