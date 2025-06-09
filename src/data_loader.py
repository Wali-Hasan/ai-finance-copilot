"""
Data loading module for financial data from various sources.
"""
from typing import Dict, Optional, Union
import pandas as pd
import yfinance as yf
from alpha_vantage.fundamentaldata import FundamentalData
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
print(f"Alpha Vantage key present: {bool(os.getenv('ALPHA_VANTAGE_API_KEY'))}")
print(f"Dotenv file exists: {os.path.exists('.env')}")
print("="*50)

load_dotenv()

# Check again after load_dotenv
print("After load_dotenv:")
print(f"Alpha Vantage key present: {bool(os.getenv('ALPHA_VANTAGE_API_KEY'))}")
print("="*50)

class FinancialDataLoader:
    def __init__(self):
        """Initialize the data loader with API clients."""
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fd = FundamentalData(key=self.alpha_vantage_key) if self.alpha_vantage_key else None

    def load_from_csv(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        Load financial data from a CSV file.
        Supports multiple CSV formats:
        1. Single CSV with 'type' column indicating statement type
        2. Single CSV with predefined columns for each statement
        3. Single CSV with date-based financial data
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dict containing income_statement and balance_sheet DataFrames
        """
        try:
            df = pd.read_csv(file_path)
            
            # Case 1: CSV has a 'type' column
            if 'type' in df.columns:
                income_stmt = df[df['type'] == 'income_statement'].copy()
                balance_sheet = df[df['type'] == 'balance_sheet'].copy()
                return {
                    'income_statement': income_stmt,
                    'balance_sheet': balance_sheet
                }
            
            # Case 2: Try to identify statement type by common column names
            income_cols = ['revenue', 'sales', 'net_income', 'operating_income', 'gross_profit']
            balance_cols = ['assets', 'liabilities', 'equity', 'cash', 'inventory']
            
            # Convert column names to lowercase for matching
            df.columns = df.columns.str.lower()
            
            # Check which columns belong to which statement
            is_income = any(col in df.columns for col in income_cols)
            is_balance = any(col in df.columns for col in balance_cols)
            
            if is_income and is_balance:
                # Split into two dataframes based on column types
                income_cols_present = [col for col in df.columns if any(ic in col for ic in income_cols)]
                balance_cols_present = [col for col in df.columns if any(bc in col for bc in balance_cols)]
                
                income_stmt = df[income_cols_present].copy()
                balance_sheet = df[balance_cols_present].copy()
            else:
                # Case 3: Assume all numeric columns are financial data
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                income_stmt = df[numeric_cols].copy()
                balance_sheet = df[numeric_cols].copy()
            
            # Ensure DataFrames have an index
            if not isinstance(income_stmt.index, pd.DatetimeIndex):
                try:
                    # Try to find a date column
                    date_cols = df.columns[df.columns.str.contains('date|year|period', case=False)]
                    if len(date_cols) > 0:
                        date_col = date_cols[0]
                        income_stmt.index = pd.to_datetime(df[date_col])
                        balance_sheet.index = pd.to_datetime(df[date_col])
                    else:
                        # Create a default index
                        income_stmt.index = pd.date_range(end=pd.Timestamp.now(), periods=len(income_stmt), freq='Y')
                        balance_sheet.index = income_stmt.index
                except:
                    # If date conversion fails, use default index
                    income_stmt.index = pd.date_range(end=pd.Timestamp.now(), periods=len(income_stmt), freq='Y')
                    balance_sheet.index = income_stmt.index
            
            return {
                'income_statement': income_stmt,
                'balance_sheet': balance_sheet
            }
            
        except Exception as e:
            raise ValueError(f"Error processing CSV file: {str(e)}\n\nPlease ensure your CSV contains financial statement data with appropriate column names.")

    def load_from_ticker(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Load financial data for a given ticker using Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Dict containing income_statement and balance_sheet DataFrames
        """
        logger.info(f"Fetching data for ticker: {ticker}")
        try:
            # Try to download info first to validate ticker
            stock = yf.Ticker(ticker)
            try:
                info = stock.info
                if not info:
                    raise ValueError(f"No information found for ticker {ticker}")
                logger.info(f"Successfully validated ticker {ticker}")
            except Exception as e:
                logger.error(f"Error validating ticker: {str(e)}")
                raise ValueError(f"Invalid ticker symbol: {ticker}")

            # Try multiple methods to get financial statements
            logger.info("Fetching financial statements from Yahoo Finance")
            income_stmt = None
            balance_sheet = None

            # Method 1: Try income statement
            for _ in range(3):  # Try up to 3 times
                try:
                    income_stmt = stock.income_stmt
                    if income_stmt is not None and not income_stmt.empty:
                        break
                except:
                    try:
                        income_stmt = stock.financials
                        if income_stmt is not None and not income_stmt.empty:
                            break
                    except:
                        pass
                logger.info("Retrying income statement fetch...")

            # Method 2: Try balance sheet
            for _ in range(3):  # Try up to 3 times
                try:
                    balance_sheet = stock.balance_sheet
                    if balance_sheet is not None and not balance_sheet.empty:
                        break
                except:
                    try:
                        balance_sheet = stock.get_balance_sheet()
                        if balance_sheet is not None and not balance_sheet.empty:
                            break
                    except:
                        pass
                logger.info("Retrying balance sheet fetch...")

            logger.info(f"Income statement fetched: {not income_stmt is None}")
            if income_stmt is not None:
                logger.info(f"Income statement shape: {income_stmt.shape}")
            
            logger.info(f"Balance sheet fetched: {not balance_sheet is None}")
            if balance_sheet is not None:
                logger.info(f"Balance sheet shape: {balance_sheet.shape}")
            
            # Clean and process the data
            income_stmt = income_stmt.T if income_stmt is not None else pd.DataFrame()
            balance_sheet = balance_sheet.T if balance_sheet is not None else pd.DataFrame()
            
            logger.info(f"After processing - Income statement empty: {income_stmt.empty}, Balance sheet empty: {balance_sheet.empty}")
            
            # Only try Alpha Vantage if we got absolutely no data from Yahoo
            if income_stmt.empty and balance_sheet.empty:
                logger.warning("No data from Yahoo Finance, trying Alpha Vantage as fallback")
                if self.fd:
                    logger.info("Fetching from Alpha Vantage")
                    try:
                        income_stmt, _ = self.fd.get_income_statement_annual(ticker)
                        balance_sheet, _ = self.fd.get_balance_sheet_annual(ticker)
                        
                        income_stmt = pd.DataFrame(income_stmt)
                        balance_sheet = pd.DataFrame(balance_sheet)
                        logger.info("Successfully fetched data from Alpha Vantage")
                    except Exception as e:
                        logger.error(f"Alpha Vantage error details: {str(e)}")
                        raise ValueError(f"Could not fetch data. Yahoo Finance returned no data and Alpha Vantage rate limit reached. Try again tomorrow or use a different ticker.")
                else:
                    raise ValueError("No data available from Yahoo Finance and Alpha Vantage is not configured")
            
            # Convert any string numbers to float
            for df in [income_stmt, balance_sheet]:
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info("Successfully processed financial data")
            return {
                'income_statement': income_stmt,
                'balance_sheet': balance_sheet
            }
            
        except Exception as e:
            logger.error(f"Error loading ticker data: {str(e)}")
            raise ValueError(f"Failed to load data for ticker {ticker}: {str(e)}")

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