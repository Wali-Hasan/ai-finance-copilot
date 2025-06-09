"""
Data loading module for financial data from various sources.
"""
from typing import Dict, Optional, Union, List, Tuple
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug code to check environment setup
print("="*50)
print("Debug Information:")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")
print(f"FMP API key present: {bool(os.getenv('FMP_API_KEY'))}")
print(f"Dotenv file exists: {os.path.exists('.env')}")
print("="*50)

load_dotenv()

# Check again after load_dotenv
print("After load_dotenv:")
print(f"FMP API key present: {bool(os.getenv('FMP_API_KEY'))}")
print("="*50)

class DataLoader:
    def __init__(self):
        """Initialize the data loader with API configuration."""
        self.fmp_key = os.getenv('FMP_API_KEY')
        self.base_url = 'https://financialmodelingprep.com/api/v3'
        
        # Debug information
        logger.info("Current directory: " + str(os.getcwd()))
        logger.info("Files in current directory: " + str(os.listdir('.')))
        logger.info("FMP API key present: " + str(bool(self.fmp_key)))
        logger.info("Dotenv file exists: " + str(os.path.exists('.env')))

    def get_financial_data(self, ticker: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Get financial data for a given ticker symbol."""
        try:
            logger.info("Fetching data for ticker: " + str(ticker))
            
            # Fetch income statement data
            income_stmt_url = self.base_url + "/income-statement/" + str(ticker) + "?apikey=" + str(self.fmp_key)
            income_response = requests.get(income_stmt_url)
            income_data = income_response.json()
            
            if not income_data or not isinstance(income_data, list):
                raise ValueError("Invalid or empty income statement data for " + str(ticker))
            
            # Debug income statement data
            logger.info("First row keys: " + str(list(income_data[0].keys())))
            logger.info("Revenue value type: " + str(type(income_data[0].get('revenue', 'N/A'))))
            logger.info("Revenue value: " + str(income_data[0].get('revenue', 'N/A')))
            
            # Fetch balance sheet data
            balance_sheet_url = self.base_url + "/balance-sheet-statement/" + str(ticker) + "?apikey=" + str(self.fmp_key)
            balance_response = requests.get(balance_sheet_url)
            balance_data = balance_response.json()
            
            if not balance_data or not isinstance(balance_data, list):
                raise ValueError("Invalid or empty balance sheet data for " + str(ticker))
            
            # Debug balance sheet data
            logger.info("First row keys: " + str(list(balance_data[0].keys())))
            
            # Convert to DataFrames
            income_stmt = pd.DataFrame(income_data)
            balance_sheet = pd.DataFrame(balance_data)
            
            # Set date as index
            income_stmt['date'] = pd.to_datetime(income_stmt['date'])
            balance_sheet['date'] = pd.to_datetime(balance_sheet['date'])
            income_stmt.set_index('date', inplace=True)
            balance_sheet.set_index('date', inplace=True)
            
            # Debug DataFrame info
            logger.info("Income Statement columns: " + str(income_stmt.columns.tolist()))
            logger.info("Income Statement dtypes:\n" + str(income_stmt.dtypes))
            logger.info("Sample revenue data:\n" + str(income_stmt['revenue'] if 'revenue' in income_stmt.columns else 'No revenue column'))
            
            return income_stmt, balance_sheet
            
        except Exception as e:
            logger.error("Error fetching data: " + str(e))
            raise ValueError("Could not fetch data for " + str(ticker) + ". Error: " + str(e))

    def load_from_csv(self, file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """Load financial data from a CSV file."""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Basic validation
            required_columns = ['date', 'revenue', 'net_income', 'assets', 'liabilities']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Error processing CSV file: Missing required columns: {', '.join(missing_columns)}.\n\nPlease ensure your CSV contains these columns: {', '.join(required_columns)}")
            
            # Split into income statement and balance sheet
            income_cols = ['date', 'revenue', 'net_income', 'operating_income', 'gross_profit']
            balance_cols = ['date', 'assets', 'liabilities', 'equity', 'current_assets', 'current_liabilities']
            
            income_stmt = df[income_cols].copy()
            balance_sheet = df[balance_cols].copy()
            
            # Set date as index
            income_stmt['date'] = pd.to_datetime(income_stmt['date'])
            balance_sheet['date'] = pd.to_datetime(balance_sheet['date'])
            income_stmt.set_index('date', inplace=True)
            balance_sheet.set_index('date', inplace=True)
            
            # Rename columns to match API format
            income_stmt = income_stmt.rename(columns={
                'net_income': 'netIncome',
                'operating_income': 'operatingIncome',
                'gross_profit': 'grossProfit'
            })
            
            balance_sheet = balance_sheet.rename(columns={
                'assets': 'totalAssets',
                'liabilities': 'totalLiabilities',
                'equity': 'totalEquity',
                'current_assets': 'totalCurrentAssets',
                'current_liabilities': 'totalCurrentLiabilities'
            })
            
            return income_stmt, balance_sheet
            
        except Exception as e:
            logger.error("Error loading CSV data: " + str(e))
            return None, None

    def validate_data(self, data: Dict[str, pd.DataFrame]) -> bool:
        """
        Validate that the financial data contains required fields.
        
        Args:
            data: Dict containing financial statements
            
        Returns:
            bool indicating if data is valid
        """
        try:
            # Check if DataFrames exist
            if not isinstance(data.get('income_statement'), pd.DataFrame) or \
               not isinstance(data.get('balance_sheet'), pd.DataFrame):
                logger.warning("Invalid data format")
                return False
                
            # Check if DataFrames are empty
            if data['income_statement'].empty or data['balance_sheet'].empty:
                logger.warning("Empty DataFrames")
                return False
                
            # Check if we have numeric data
            income_numeric = data['income_statement'].select_dtypes(include=['float64', 'int64']).columns
            balance_numeric = data['balance_sheet'].select_dtypes(include=['float64', 'int64']).columns
            
            has_numeric = len(income_numeric) > 0 and len(balance_numeric) > 0
            if not has_numeric:
                logger.warning("No numeric data found")
            
            return has_numeric
            
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return False

    def get_trend_data(self) -> Dict[str, pd.Series]:
        """Get historical trend data for key metrics."""
        trend_data = {}
        
        # Try to get trend data for each metric
        metrics_to_fetch = {
            'Revenue': {'variations': ['totalRevenue', 'revenue', 'total revenue', 'sales', 'total sales'], 'is_balance_sheet': False},
            'Net Income': {'variations': ['netIncome', 'net income', 'netincome', 'net earnings', 'profit'], 'is_balance_sheet': False},
            'Total Assets': {'variations': ['totalAssets', 'total assets', 'assets'], 'is_balance_sheet': True},
            'Total Liabilities': {'variations': ['totalLiabilities', 'total liabilities', 'liabilities'], 'is_balance_sheet': True}
        }
        
        for metric, config in metrics_to_fetch.items():
            series = self._get_metric_series(metric, config['variations'], config['is_balance_sheet'])
            if not series.empty:
                # Ensure the series is numeric
                series = pd.to_numeric(series, errors='coerce')
                series = series.dropna()
                if not series.empty:
                    trend_data[metric] = series
                    logger.info(f"Added {metric} data: {series.dtype}")
        
        return trend_data

    def _get_metric_series(self, metric: str, variations: List[str], is_balance_sheet: bool = False) -> pd.Series:
        """Helper method to get historical data for a specific metric."""
        try:
            df = self.balance_sheet if is_balance_sheet else self.income_stmt
            logger.info(f"Getting {metric} series from {'balance sheet' if is_balance_sheet else 'income statement'}")
            
            # Find matching columns
            matching_cols = []
            for term in variations:
                # Try exact match first
                exact_matches = df.columns[df.columns.str.lower() == term.lower()]
                if not exact_matches.empty:
                    matching_cols.extend(exact_matches)
                    break  # Use first exact match
                else:
                    # Try contains match
                    matches = df.columns[df.columns.str.lower().str.contains(term.lower())]
                    matching_cols.extend(matches)
            
            if not matching_cols:
                logger.warning(f"No matching columns found for {metric}")
                return pd.Series([], dtype='float64')
            
            # Get the data
            col_name = matching_cols[0]
            logger.info(f"Using column {col_name} for {metric}")
            
            series = df[col_name].copy()
            
            # Convert to numeric, handling any string formatting
            if series.dtype == object:
                # Remove any non-numeric characters except decimal points and negative signs
                series = series.astype(str).str.replace(r'[^\d.-]', '', regex=True)
            
            # Convert to numeric
            series = pd.to_numeric(series, errors='coerce')
            series = series.dropna()
            
            # Sort by index
            series = series.sort_index()
            
            logger.info(f"Processed {metric} data type: {series.dtype}")
            return series
            
        except Exception as e:
            logger.error(f"Error getting metric series for {metric}: {str(e)}")
            return pd.Series([], dtype='float64') 