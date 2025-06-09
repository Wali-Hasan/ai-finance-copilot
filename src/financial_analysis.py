"""
Financial analysis module for calculating key metrics and ratios.
"""
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import logging

# Configure logging
logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    def __init__(self, income_statement: pd.DataFrame, balance_sheet: pd.DataFrame):
        """
        Initialize the analyzer with financial statements.
        
        Args:
            income_statement: Income statement DataFrame
            balance_sheet: Balance sheet DataFrame
        """
        self.income_stmt = income_statement
        self.balance_sheet = balance_sheet

    def calculate_growth_rates(self) -> Dict[str, float]:
        """Calculate year-over-year growth rates for key metrics."""
        metrics = {
            'revenue_growth': self._get_growth_rate('Revenue'),
            'net_income_growth': self._get_growth_rate('Net Income'),
            'asset_growth': self._get_growth_rate('Total Assets', is_balance_sheet=True)
        }
        return metrics

    def _get_growth_rate(self, metric: str, is_balance_sheet: bool = False) -> float:
        """Helper method to calculate growth rate for a specific metric."""
        try:
            df = self.balance_sheet if is_balance_sheet else self.income_stmt
            
            # Map common variations of metric names (same as _get_latest_value)
            metric_variations = {
                'Revenue': ['revenue', 'total revenue', 'sales', 'total sales'],
                'Net Income': ['net income', 'netincome', 'net earnings', 'profit'],
                'Total Assets': ['total assets', 'assets', 'totalassets']
            }
            
            # Get variations for the requested metric
            search_terms = metric_variations.get(metric, [metric.lower()])
            
            # Find matching columns
            matching_cols = []
            for term in search_terms:
                matches = df.columns[df.columns.str.contains(term, case=False)]
                matching_cols.extend(matches)
            
            if not matching_cols:
                logger.warning(f"No matching columns found for metric: {metric}")
                return 0.0
            
            # Get values for the last two periods
            values = df[matching_cols[0]].iloc[0:2]
            if len(values) >= 2:
                current = float(values.iloc[0])
                previous = float(values.iloc[1])
                
                if pd.notnull(current) and pd.notnull(previous) and previous != 0:
                    growth_rate = ((current - previous) / abs(previous)) * 100
                    return growth_rate
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating growth rate for {metric}: {str(e)}")
            return 0.0

    def calculate_profitability_ratios(self) -> Dict[str, float]:
        """Calculate profitability ratios."""
        revenue = self._get_latest_value('Revenue')
        net_income = self._get_latest_value('Net Income')
        total_assets = self._get_latest_value('Total Assets', is_balance_sheet=True)
        total_equity = self._get_latest_value('Total Stockholder Equity', is_balance_sheet=True)

        return {
            'profit_margin': (net_income / revenue * 100) if revenue else 0,
            'return_on_assets': (net_income / total_assets * 100) if total_assets else 0,
            'return_on_equity': (net_income / total_equity * 100) if total_equity else 0
        }

    def calculate_liquidity_ratios(self) -> Dict[str, float]:
        """Calculate liquidity ratios."""
        current_assets = self._get_latest_value('Current Assets', is_balance_sheet=True)
        current_liabilities = self._get_latest_value('Current Liabilities', is_balance_sheet=True)
        total_liabilities = self._get_latest_value('Total Liabilities', is_balance_sheet=True)
        total_equity = self._get_latest_value('Total Stockholder Equity', is_balance_sheet=True)

        return {
            'current_ratio': current_assets / current_liabilities if current_liabilities else 0,
            'debt_to_equity': total_liabilities / total_equity if total_equity else 0
        }

    def _get_latest_value(self, metric: str, is_balance_sheet: bool = False) -> float:
        """Helper method to get the most recent value for a metric."""
        try:
            df = self.balance_sheet if is_balance_sheet else self.income_stmt
            
            # Map common variations of metric names
            metric_variations = {
                'Revenue': ['revenue', 'total revenue', 'sales', 'total sales'],
                'Net Income': ['net income', 'netincome', 'net earnings', 'profit'],
                'Total Assets': ['total assets', 'assets', 'totalassets'],
                'Total Stockholder Equity': ['total stockholder equity', 'stockholder equity', 'total equity', 'equity'],
                'Current Assets': ['current assets', 'currentassets'],
                'Current Liabilities': ['current liabilities', 'currentliabilities'],
                'Total Liabilities': ['total liabilities', 'liabilities', 'totalliabilities']
            }
            
            # Get variations for the requested metric
            search_terms = metric_variations.get(metric, [metric.lower()])
            
            # Find matching columns
            matching_cols = []
            for term in search_terms:
                matches = df.columns[df.columns.str.contains(term, case=False)]
                matching_cols.extend(matches)
            
            if not matching_cols:
                logger.warning(f"No matching columns found for metric: {metric}")
                return 0.0
                
            # Get the first matching column's most recent value
            value = df[matching_cols[0]].iloc[0]
            if isinstance(value, pd.Series):
                value = value.iloc[0]
                
            return float(value) if pd.notnull(value) else 0.0
            
        except Exception as e:
            logger.error(f"Error getting latest value for {metric}: {str(e)}")
            return 0.0

    def get_trend_data(self) -> Dict[str, pd.Series]:
        """Get historical trend data for key metrics."""
        return {
            'Revenue': self._get_metric_series('Revenue'),
            'Net Income': self._get_metric_series('Net Income'),
            'Total Assets': self._get_metric_series('Total Assets', is_balance_sheet=True),
            'Total Liabilities': self._get_metric_series('Total Liabilities', is_balance_sheet=True)
        }

    def _get_metric_series(self, metric: str, is_balance_sheet: bool = False) -> pd.Series:
        """Helper method to get historical data for a specific metric."""
        try:
            df = self.balance_sheet if is_balance_sheet else self.income_stmt
            matching_cols = df.columns[df.columns.str.contains(metric, case=False)]
            if matching_cols.empty:
                return pd.Series([])
            # Get the data and sort by index (dates) in ascending order
            series = df[matching_cols].iloc[:, 0]
            series = series.sort_index()
            # Convert values to float and handle any non-numeric values
            series = pd.to_numeric(series, errors='coerce')
            return series
        except:
            return pd.Series([]) 